"""Silver layer: cleaned data with SCD2 historization."""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame, SparkSession

from enterprise_pipeline.connectors.base import WarehouseConnector
from enterprise_pipeline.patterns.repository import DomainRepository
from enterprise_pipeline.patterns.scd2 import apply_scd2
from enterprise_pipeline.transforms.base import DomainTransformer

logger = logging.getLogger("enterprise_pipeline")


class SilverLayer:
    """Cleans bronze data and applies SCD2 historization."""

    def __init__(self, spark: SparkSession, connector: WarehouseConnector, scd2_enabled: bool = True) -> None:
        self.spark = spark
        self.connector = connector
        self.scd2_enabled = scd2_enabled

    def process_domain(
        self,
        domain: str,
        repository: DomainRepository,
        transformer: DomainTransformer,
        primary_key: list[str],
        batch_id: str | None = None,
    ) -> DataFrame:
        """Transform bronze data and apply SCD2 to produce the silver layer."""
        logger.info("Silver processing starting for domain=%s", domain)

        bronze_df = repository.read_bronze()

        # Drop internal bronze columns before transformation
        internal_cols = ["_source_system", "_ingestion_timestamp"]
        clean_df = bronze_df
        for col in internal_cols:
            if col in clean_df.columns:
                clean_df = clean_df.drop(col)

        transformed = transformer.transform(clean_df)

        if self.scd2_enabled:
            result = apply_scd2(
                spark=self.spark,
                incoming=transformed,
                target_path=repository.silver_path,
                primary_key=primary_key,
                connector=self.connector,
                batch_id=batch_id,
            )
        else:
            repository.write_silver(transformed)
            result = transformed

        logger.info("Silver layer complete for %s", domain)
        return result
