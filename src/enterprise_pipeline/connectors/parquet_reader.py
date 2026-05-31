"""Reads source data from Parquet files."""

from __future__ import annotations

import logging
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession

logger = logging.getLogger("enterprise_pipeline")


class ParquetSourceReader:
    """Reads Parquet files for a specific source system and date."""

    def __init__(self, spark: SparkSession, base_path: str) -> None:
        self.spark = spark
        self.base_path = Path(base_path)

    def read(self, date_str: str | None = None) -> DataFrame:
        """Read parquet files, optionally filtering by date pattern in filename."""
        if not self.base_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {self.base_path}")

        parquet_files = list(self.base_path.glob("*.parquet"))
        if not parquet_files:
            raise FileNotFoundError(f"No parquet files found in {self.base_path}")

        if date_str:
            date_compact = date_str.replace("-", "")
            matched = [f for f in parquet_files if date_compact in f.name]
            if matched:
                path = str(matched[0])
            else:
                path = str(self.base_path / "*.parquet")
        else:
            path = str(self.base_path / "*.parquet")

        logger.info("Reading parquet from: %s", path)
        return self.spark.read.parquet(path)

    def list_available_dates(self) -> list[str]:
        """List available date snapshots based on filenames."""
        import re

        dates: list[str] = []
        for f in sorted(self.base_path.glob("*.parquet")):
            match = re.search(r"(\d{8})", f.name)
            if match:
                raw = match.group(1)
                dates.append(f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}")
        return dates
