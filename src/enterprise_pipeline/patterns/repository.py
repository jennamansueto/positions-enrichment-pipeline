"""Data repository pattern — single interface for reading/writing domain data at any medallion layer."""

from __future__ import annotations

import logging
from datetime import date

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enterprise_pipeline.connectors.base import WarehouseConnector

logger = logging.getLogger("enterprise_pipeline")


class DomainRepository:
    """Repository for a single data domain, abstracting medallion layer access."""

    def __init__(
        self,
        domain: str,
        connector: WarehouseConnector,
        bronze_path: str,
        silver_path: str,
    ) -> None:
        self.domain = domain
        self.connector = connector
        self.bronze_path = f"{bronze_path}/{domain}"
        self.silver_path = f"{silver_path}/{domain}"

    def read_bronze(self) -> DataFrame:
        return self.connector.read_table(self.bronze_path)

    def write_bronze(self, df: DataFrame) -> None:
        self.connector.write_table(self.bronze_path, df, mode="overwrite")
        logger.info("Wrote bronze layer for %s", self.domain)

    def read_silver(self, as_of: date | None = None) -> DataFrame:
        df = self.connector.read_table(self.silver_path)
        if as_of and "as_of_date" in df.columns:
            df = df.filter(F.col("as_of_date") == as_of)
        return df

    def write_silver(self, df: DataFrame) -> None:
        self.connector.write_table(self.silver_path, df, mode="overwrite")
        logger.info("Wrote silver layer for %s", self.domain)

    def read_current(self) -> DataFrame:
        """Read only current records (is_current=True) from the silver layer."""
        df = self.read_silver()
        if "_is_current" in df.columns:
            return df.filter(F.col("_is_current") == True)  # noqa: E712
        return df

    def bronze_exists(self) -> bool:
        return self.connector.table_exists(self.bronze_path)

    def silver_exists(self) -> bool:
        return self.connector.table_exists(self.silver_path)
