"""Pipeline builder — composes the full pipeline DAG."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from pyspark.sql import SparkSession

from enterprise_pipeline.config.models import JoinConfig, MedallionConfig
from enterprise_pipeline.connectors.base import WarehouseConnector
from enterprise_pipeline.ingestion.base import SourceReader
from enterprise_pipeline.medallion.bronze import BronzeLayer
from enterprise_pipeline.medallion.gold import GoldLayer
from enterprise_pipeline.medallion.silver import SilverLayer
from enterprise_pipeline.patterns.repository import DomainRepository
from enterprise_pipeline.transforms.base import DomainTransformer

logger = logging.getLogger("enterprise_pipeline")


@dataclass
class PipelineComponents:
    """Holds all constructed pipeline components."""

    bronze: BronzeLayer
    silver: SilverLayer
    gold: GoldLayer
    readers: dict[str, list[SourceReader]] = field(default_factory=dict)
    transformers: dict[str, DomainTransformer] = field(default_factory=dict)
    repositories: dict[str, DomainRepository] = field(default_factory=dict)
    primary_keys: dict[str, list[str]] = field(default_factory=dict)
    join_configs: list[JoinConfig] = field(default_factory=list)


class PipelineBuilder:
    """Fluent builder for constructing the pipeline."""

    def __init__(self, spark: SparkSession, connector: WarehouseConnector) -> None:
        self.spark = spark
        self.connector = connector
        self._readers: dict[str, list[SourceReader]] = {}
        self._transformers: dict[str, DomainTransformer] = {}
        self._primary_keys: dict[str, list[str]] = {}
        self._medallion_config: MedallionConfig | None = None
        self._join_configs: list[JoinConfig] = []

    def with_source(self, domain: str, reader: SourceReader) -> PipelineBuilder:
        if domain not in self._readers:
            self._readers[domain] = []
        self._readers[domain].append(reader)
        return self

    def with_transformer(self, domain: str, transformer: DomainTransformer) -> PipelineBuilder:
        self._transformers[domain] = transformer
        return self

    def with_primary_key(self, domain: str, keys: list[str]) -> PipelineBuilder:
        self._primary_keys[domain] = keys
        return self

    def with_medallion_config(self, config: MedallionConfig) -> PipelineBuilder:
        self._medallion_config = config
        return self

    def with_joins(self, joins: list[JoinConfig]) -> PipelineBuilder:
        self._join_configs = joins
        return self

    def build(self) -> PipelineComponents:
        if self._medallion_config is None:
            raise ValueError("Medallion config is required")

        bronze = BronzeLayer(self.spark)
        silver = SilverLayer(self.spark, self.connector, self._medallion_config.scd2_enabled)
        gold = GoldLayer(self.spark, self.connector, self._medallion_config.gold_path)

        repositories: dict[str, DomainRepository] = {}
        for domain in self._readers:
            repositories[domain] = DomainRepository(
                domain=domain,
                connector=self.connector,
                bronze_path=self._medallion_config.bronze_path,
                silver_path=self._medallion_config.silver_path,
            )

        logger.info(
            "Pipeline built: domains=%s, joins=%s",
            list(self._readers.keys()),
            [j.domain for j in self._join_configs],
        )

        return PipelineComponents(
            bronze=bronze,
            silver=silver,
            gold=gold,
            readers=self._readers,
            transformers=self._transformers,
            repositories=repositories,
            primary_keys=self._primary_keys,
            join_configs=self._join_configs,
        )
