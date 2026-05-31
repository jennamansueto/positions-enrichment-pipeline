"""Gold layer: denormalized enterprise dataset."""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from enterprise_pipeline.config.models import JoinConfig
from enterprise_pipeline.connectors.base import WarehouseConnector
from enterprise_pipeline.patterns.repository import DomainRepository

logger = logging.getLogger("enterprise_pipeline")


class GoldLayer:
    """Produces the denormalized enterprise positions dataset."""

    def __init__(self, spark: SparkSession, connector: WarehouseConnector, gold_path: str) -> None:
        self.spark = spark
        self.connector = connector
        self.gold_path = gold_path

    def build_enterprise_dataset(
        self,
        positions_repo: DomainRepository,
        domain_repos: dict[str, DomainRepository],
        join_configs: list[JoinConfig],
    ) -> DataFrame:
        """Join all silver domains into a single denormalized dataset.

        Positions is the base table; security and risk join via configured keys.
        Only current records (_is_current=True) are used.
        """
        logger.info("Building gold enterprise dataset")

        base = positions_repo.read_current()

        for join_cfg in join_configs:
            domain = join_cfg.domain
            repo = domain_repos.get(domain)
            if repo is None:
                logger.warning("No repository found for join domain: %s — skipping", domain)
                continue

            domain_df = repo.read_current()

            # Determine join keys
            if isinstance(join_cfg.join_key, list):
                join_keys = join_cfg.join_key
            else:
                join_keys = [join_cfg.join_key]

            # Prefix domain columns to avoid ambiguity (except join keys and SCD2 meta)
            scd2_cols = {"_record_hash", "_effective_from", "_effective_to", "_is_current", "_batch_id"}
            skip_cols = set(join_keys) | scd2_cols

            rename_map: dict[str, str] = {}
            for col_name in domain_df.columns:
                if col_name in skip_cols:
                    continue
                if col_name in base.columns:
                    new_name = f"{domain}_{col_name}"
                    rename_map[col_name] = new_name

            for old_name, new_name in rename_map.items():
                domain_df = domain_df.withColumnRenamed(old_name, new_name)

            # Drop SCD2 metadata columns from the joined domain
            for scd_col in scd2_cols:
                if scd_col in domain_df.columns:
                    domain_df = domain_df.drop(scd_col)

            base = base.join(domain_df, on=join_keys, how=join_cfg.join_type)
            logger.info("Joined domain=%s on keys=%s (%s)", domain, join_keys, join_cfg.join_type)

        # Drop SCD2 metadata from final output
        for scd_col in ["_record_hash", "_effective_from", "_effective_to", "_is_current", "_batch_id"]:
            if scd_col in base.columns:
                base = base.drop(scd_col)

        # Add pipeline metadata
        base = base.withColumn("_pipeline_timestamp", F.current_timestamp())

        output_path = f"{self.gold_path}/enterprise_positions"
        self.connector.write_table(output_path, base, mode="overwrite")

        logger.info("Gold enterprise dataset written: %d records, %d columns", base.count(), len(base.columns))
        return base
