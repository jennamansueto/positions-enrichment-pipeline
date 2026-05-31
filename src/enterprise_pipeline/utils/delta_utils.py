"""Delta Lake utility functions."""

from __future__ import annotations

from pathlib import Path

from pyspark.sql import SparkSession


def table_exists(spark: SparkSession, path: str) -> bool:
    """Check if a Delta table exists at the given path."""
    try:
        target = Path(path)
        if not target.exists():
            return False
        spark.read.format("delta").load(path)
        return True
    except Exception:
        return False


def get_table_columns(spark: SparkSession, path: str) -> list[str]:
    """Get column names from an existing Delta table."""
    if not table_exists(spark, path):
        return []
    df = spark.read.format("delta").load(path)
    return df.columns
