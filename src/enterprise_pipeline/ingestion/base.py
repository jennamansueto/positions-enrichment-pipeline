"""Abstract base class for source readers (Strategy pattern)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from pyspark.sql import DataFrame
from pyspark.sql.types import StructType


class SourceReader(ABC):
    """Interface for reading data from a specific source system."""

    @abstractmethod
    def extract(self, as_of_date: date) -> DataFrame:
        """Extract data for a specific business date."""
        ...

    @abstractmethod
    def get_schema(self) -> StructType:
        """Return the expected Spark schema for this source."""
        ...

    @property
    @abstractmethod
    def source_system_name(self) -> str:
        """Name of the source system."""
        ...

    @property
    @abstractmethod
    def domain(self) -> str:
        """Domain this reader serves (positions, security, risk_analytics)."""
        ...
