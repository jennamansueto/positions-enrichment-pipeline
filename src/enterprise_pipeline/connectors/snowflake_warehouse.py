"""Snowflake warehouse connector for production use.

This is a placeholder implementation showing the connector abstraction.
In production, this would use the Snowflake Spark connector.
"""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame, SparkSession

from enterprise_pipeline.connectors.base import ColumnInfo, WarehouseConnector

logger = logging.getLogger("enterprise_pipeline")


class SnowflakeWarehouseConnector(WarehouseConnector):
    """Reads and writes to Snowflake via Spark connector.

    Requires snowflake-spark connector JAR and credentials configured
    via environment variables.
    """

    def __init__(
        self,
        spark: SparkSession,
        account: str,
        warehouse: str,
        database: str,
        schema: str,
        user: str,
        password: str,
    ) -> None:
        self.spark = spark
        self._sf_options = {
            "sfURL": f"{account}.snowflakecomputing.com",
            "sfWarehouse": warehouse,
            "sfDatabase": database,
            "sfSchema": schema,
            "sfUser": user,
            "sfPassword": password,
        }

    def read_table(self, path: str) -> DataFrame:
        return (
            self.spark.read.format("snowflake")
            .options(**self._sf_options)
            .option("dbtable", path)
            .load()
        )

    def write_table(self, path: str, df: DataFrame, mode: str = "overwrite") -> None:
        (
            df.write.format("snowflake")
            .options(**self._sf_options)
            .option("dbtable", path)
            .mode(mode)
            .save()
        )
        logger.info("Wrote Snowflake table %s (mode=%s)", path, mode)

    def execute_ddl(self, sql: str) -> None:
        raise NotImplementedError("DDL execution via Snowflake connector is not yet implemented")

    def table_exists(self, path: str) -> bool:
        try:
            self.read_table(path).limit(0)
            return True
        except Exception:
            return False

    def get_columns(self, path: str) -> list[ColumnInfo]:
        if not self.table_exists(path):
            return []
        df = self.read_table(path)
        return [
            ColumnInfo(name=field.name, data_type=field.dataType.simpleString(), nullable=field.nullable)
            for field in df.schema.fields
        ]
