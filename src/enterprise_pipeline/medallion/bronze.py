"""Bronze layer: raw data ingestion from source systems."""

from __future__ import annotations

import logging
from datetime import date

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from enterprise_pipeline.ingestion.base import SourceReader
from enterprise_pipeline.patterns.repository import DomainRepository
from enterprise_pipeline.transforms.consolidation import consolidate_positions

logger = logging.getLogger("enterprise_pipeline")


class BronzeLayer:
    """Ingests raw data from source systems into the bronze layer."""

    def __init__(self, spark: SparkSession) -> None:
        self.spark = spark

    def ingest_domain(
        self,
        domain: str,
        readers: list[SourceReader],
        repository: DomainRepository,
        as_of_date: date,
    ) -> DataFrame:
        """Ingest data from one or more readers for a domain into bronze."""
        logger.info("Bronze ingestion starting for domain=%s, date=%s", domain, as_of_date)

        dataframes: list[DataFrame] = []
        for reader in readers:
            try:
                df = reader.extract(as_of_date)
                df = df.withColumn("_source_system", F.lit(reader.source_system_name))
                df = df.withColumn("_ingestion_timestamp", F.current_timestamp())
                dataframes.append(df)
            except FileNotFoundError:
                logger.warning("No data found for %s on %s — skipping", reader.source_system_name, as_of_date)

        if not dataframes:
            raise ValueError(f"No data ingested for domain={domain} on {as_of_date}")

        if domain == "positions" and len(dataframes) == 2:
            result = consolidate_positions(dataframes[0], dataframes[1])
        elif len(dataframes) == 1:
            result = dataframes[0]
        else:
            result = dataframes[0]
            for df in dataframes[1:]:
                result = result.unionByName(df, allowMissingColumns=True)

        repository.write_bronze(result)
        logger.info("Bronze layer complete for %s: %d records", domain, result.count())
        return result
