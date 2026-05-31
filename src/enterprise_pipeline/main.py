"""Pipeline entrypoint — orchestrates the full bronze → silver → gold flow."""

from __future__ import annotations

import logging
from datetime import date

from enterprise_pipeline.builders.pipeline_builder import PipelineBuilder
from enterprise_pipeline.catalog.lineage import LineageTracker
from enterprise_pipeline.catalog.metadata import MetadataCatalog
from enterprise_pipeline.config.pipeline_config import PipelineConfig
from enterprise_pipeline.config.schema_registry import SchemaRegistry
from enterprise_pipeline.connectors.factory import ConnectorFactory
from enterprise_pipeline.ingestion.reader_factory import ReaderFactory
from enterprise_pipeline.patterns.schema_evolution import SchemaEvolution
from enterprise_pipeline.quality.cardinality import check_cardinality, check_uniqueness
from enterprise_pipeline.quality.data_quality import check_referential_integrity
from enterprise_pipeline.quality.reporter import QualityReporter
from enterprise_pipeline.quality.schema_validator import check_schema_conformance
from enterprise_pipeline.transforms.positions_transformer import PositionsTransformer
from enterprise_pipeline.transforms.risk_transformer import RiskTransformer
from enterprise_pipeline.transforms.security_transformer import SecurityTransformer
from enterprise_pipeline.utils.logging import setup_logging
from enterprise_pipeline.utils.spark_session import get_spark_session

logger = logging.getLogger("enterprise_pipeline")

DOMAIN_PRIMARY_KEYS = {
    "positions": ["position_id", "book_id", "as_of_date"],
    "security": ["security_id"],
    "risk_analytics": ["risk_calc_id"],
}

DOMAIN_TRANSFORMERS: dict[str, type[PositionsTransformer] | type[SecurityTransformer] | type[RiskTransformer]] = {
    "positions": PositionsTransformer,
    "security": SecurityTransformer,
    "risk_analytics": RiskTransformer,
}


def run_pipeline(
    as_of_date: date,
    config_path: str = "config/pipeline.yaml",
    domains_dir: str = "config/domains",
    mappings_dir: str = "config/mappings",
    log_level: str = "INFO",
) -> None:
    """Execute the full pipeline for a given business date."""
    setup_logging(log_level)
    logger.info("=== Enterprise Pipeline Starting === date=%s", as_of_date)

    # Load configuration
    pipeline_config = PipelineConfig(config_path)
    settings = pipeline_config.load()
    schema_registry = SchemaRegistry(mappings_dir)
    schema_registry.load_all()

    # Initialize Spark and connector
    spark = get_spark_session(settings.name, settings.warehouse.path)
    connector = ConnectorFactory.create(spark, settings)

    # Schema evolution
    schema_evo = SchemaEvolution(spark, schema_registry, connector)
    for domain in DOMAIN_PRIMARY_KEYS:
        if settings.medallion:
            table_path = f"{settings.medallion.silver_path}/{domain}"
            schema_evo.evolve(domain, table_path)

    # Create readers
    all_readers = ReaderFactory.create_all(spark, settings)

    # Group readers by domain
    domain_readers: dict[str, list] = {  # type: ignore[type-arg]
        "positions": [],
        "security": [],
        "risk_analytics": [],
    }
    reader_to_domain = {
        "accounting_system_alpha": "positions",
        "accounting_system_beta": "positions",
        "security_master": "security",
        "risk_engine": "risk_analytics",
    }
    for name, reader in all_readers.items():
        domain = reader_to_domain.get(name, reader.domain)
        domain_readers[domain].append(reader)

    # Build pipeline
    assert settings.medallion is not None
    builder = PipelineBuilder(spark, connector)
    for domain, readers in domain_readers.items():
        for reader in readers:
            builder.with_source(domain, reader)
        if domain in DOMAIN_TRANSFORMERS:
            builder.with_transformer(domain, DOMAIN_TRANSFORMERS[domain]())
        builder.with_primary_key(domain, DOMAIN_PRIMARY_KEYS[domain])

    builder.with_medallion_config(settings.medallion)
    builder.with_joins(settings.joins)
    pipeline = builder.build()

    batch_id = as_of_date.strftime("%Y%m%d")

    # === Bronze ===
    logger.info("--- Bronze Layer ---")
    for domain, readers in pipeline.readers.items():
        pipeline.bronze.ingest_domain(domain, readers, pipeline.repositories[domain], as_of_date)

    # === Silver ===
    logger.info("--- Silver Layer ---")
    for domain in pipeline.repositories:
        transformer = pipeline.transformers.get(domain)
        if transformer:
            primary_key = pipeline.primary_keys.get(domain, [])
            pipeline.silver.process_domain(domain, pipeline.repositories[domain], transformer, primary_key, batch_id)

    # === Gold ===
    logger.info("--- Gold Layer ---")
    positions_repo = pipeline.repositories["positions"]
    other_repos = {k: v for k, v in pipeline.repositories.items() if k != "positions"}
    gold_df = pipeline.gold.build_enterprise_dataset(positions_repo, other_repos, pipeline.join_configs)

    # === Quality Checks ===
    logger.info("--- Quality Checks ---")
    reporter = QualityReporter()

    reporter.add_result(check_cardinality(gold_df, label="gold_enterprise_positions"))
    reporter.add_result(
        check_uniqueness(gold_df, ["position_id", "book_id", "as_of_date"], label="gold_pk_uniqueness")
    )

    gold_schema = schema_registry.get("positions")
    reporter.add_result(check_schema_conformance(gold_df, gold_schema, label="gold_positions_schema"))

    if positions_repo.silver_exists():
        positions_silver = positions_repo.read_current()
        security_repo = pipeline.repositories.get("security")
        if security_repo and security_repo.silver_exists():
            security_silver = security_repo.read_current()
            reporter.add_result(
                check_referential_integrity(positions_silver, security_silver, "security_id", label="pos_sec_ref")
            )

    report_path = reporter.write_report(settings.name)

    # === Lineage & Catalog ===
    logger.info("--- Lineage & Cataloging ---")
    lineage_tracker = LineageTracker()
    catalog = MetadataCatalog()
    for domain in DOMAIN_PRIMARY_KEYS:
        schema = schema_registry.get(domain)
        lineage_tracker.track_from_schema(schema)
        catalog.catalog_schema(schema)

    lineage_tracker.write_lineage()
    catalog.write_catalog()

    logger.info("=== Pipeline Complete === quality=%s, report=%s", reporter.summary(), report_path)
    spark.stop()
