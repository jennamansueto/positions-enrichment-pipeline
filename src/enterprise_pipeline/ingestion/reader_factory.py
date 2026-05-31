"""Factory for creating source readers based on configuration."""

from __future__ import annotations

from pyspark.sql import SparkSession

from enterprise_pipeline.config.models import PipelineSettings
from enterprise_pipeline.ingestion.base import SourceReader
from enterprise_pipeline.ingestion.positions_alpha_reader import PositionsAlphaReader
from enterprise_pipeline.ingestion.positions_beta_reader import PositionsBetaReader
from enterprise_pipeline.ingestion.risk_reader import RiskReader
from enterprise_pipeline.ingestion.security_reader import SecurityReader


class ReaderFactory:
    """Creates source readers based on pipeline configuration."""

    @staticmethod
    def create_all(spark: SparkSession, settings: PipelineSettings) -> dict[str, SourceReader]:
        """Create all source readers defined in the pipeline config."""
        readers: dict[str, SourceReader] = {}

        for source_name, source_config in settings.sources.items():
            reader: SourceReader
            if source_name == "accounting_system_alpha":
                reader = PositionsAlphaReader(spark, source_config.path)
            elif source_name == "accounting_system_beta":
                reader = PositionsBetaReader(spark, source_config.path)
            elif source_name == "security_master":
                reader = SecurityReader(spark, source_config.path)
            elif source_name == "risk_engine":
                reader = RiskReader(spark, source_config.path)
            else:
                raise ValueError(f"No reader registered for source: {source_name}")
            readers[source_name] = reader

        return readers
