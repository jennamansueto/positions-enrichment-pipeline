"""Abstract base classes for connectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from pyspark.sql import DataFrame


@dataclass
class ColumnInfo:
    """Metadata for a table column."""

    name: str
    data_type: str
    nullable: bool = True


class WarehouseConnector(ABC):
    """Abstract interface for warehouse read/write operations."""

    @abstractmethod
    def read_table(self, path: str) -> DataFrame:
        ...

    @abstractmethod
    def write_table(self, path: str, df: DataFrame, mode: str = "overwrite") -> None:
        ...

    @abstractmethod
    def execute_ddl(self, sql: str) -> None:
        ...

    @abstractmethod
    def table_exists(self, path: str) -> bool:
        ...

    @abstractmethod
    def get_columns(self, path: str) -> list[ColumnInfo]:
        ...
