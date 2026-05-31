"""Connectors — Repository pattern for data access (read/write)."""

from enterprise_pipeline.connectors.base import WarehouseConnector
from enterprise_pipeline.connectors.delta_warehouse import DeltaWarehouseConnector
from enterprise_pipeline.connectors.factory import ConnectorFactory
from enterprise_pipeline.connectors.parquet_reader import ParquetSourceReader

__all__ = [
    "ConnectorFactory",
    "DeltaWarehouseConnector",
    "ParquetSourceReader",
    "WarehouseConnector",
]
