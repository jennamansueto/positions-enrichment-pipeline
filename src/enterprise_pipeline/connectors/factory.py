"""Factory for creating warehouse connectors based on configuration."""

from __future__ import annotations

from pyspark.sql import SparkSession

from enterprise_pipeline.config.models import PipelineSettings
from enterprise_pipeline.connectors.base import WarehouseConnector
from enterprise_pipeline.connectors.delta_warehouse import DeltaWarehouseConnector


class ConnectorFactory:
    """Creates the appropriate warehouse connector based on pipeline config."""

    @staticmethod
    def create(spark: SparkSession, settings: PipelineSettings) -> WarehouseConnector:
        backend = settings.warehouse.backend

        if backend == "delta_local":
            return DeltaWarehouseConnector(spark)

        if backend == "snowflake":
            from enterprise_pipeline.connectors.snowflake_warehouse import SnowflakeWarehouseConnector

            return SnowflakeWarehouseConnector(
                spark=spark,
                account=settings.warehouse.path,
                warehouse="",
                database="",
                schema="",
                user="",
                password="",
            )

        raise ValueError(f"Unsupported warehouse backend: {backend}")
