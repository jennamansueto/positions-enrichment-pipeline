"""Abstract base transformer for domain-specific data cleaning."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pyspark.sql import DataFrame


class DomainTransformer(ABC):
    """Interface for domain-specific data transformations (bronze -> silver)."""

    @abstractmethod
    def transform(self, df: DataFrame) -> DataFrame:
        """Apply domain-specific transformations to clean and conform data."""
        ...

    @property
    @abstractmethod
    def domain(self) -> str:
        """The domain this transformer serves."""
        ...
