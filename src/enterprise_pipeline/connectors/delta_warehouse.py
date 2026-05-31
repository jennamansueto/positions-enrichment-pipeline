"""Delta Lake warehouse connector for local development."""

from __future__ import annotations

import logging
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession

from enterprise_pipeline.connectors.base import ColumnInfo, WarehouseConnector

logger = logging.getLogger("enterprise_pipeline")


class DeltaWarehouseConnector(WarehouseConnector):
    """Reads and writes Delta tables on local filesystem."""

    def __init__(self, spark: SparkSession) -> None:
        self.spark = spark

    def read_table(self, path: str) -> DataFrame:
        return self.spark.read.format("delta").load(path)

    def write_table(self, path: str, df: DataFrame, mode: str = "overwrite") -> None:
        df.write.format("delta").mode(mode).save(path)
        logger.info("Wrote Delta table to %s (mode=%s, rows=%d)", path, mode, df.count())

    def execute_ddl(self, sql: str) -> None:
        self.spark.sql(sql)

    def table_exists(self, path: str) -> bool:
        try:
            target = Path(path)
            if not target.exists():
                return False
            self.spark.read.format("delta").load(path)
            return True
        except Exception:
            return False

    def get_columns(self, path: str) -> list[ColumnInfo]:
        if not self.table_exists(path):
            return []
        df = self.spark.read.format("delta").load(path)
        return [
            ColumnInfo(name=field.name, data_type=field.dataType.simpleString(), nullable=field.nullable)
            for field in df.schema.fields
        ]
