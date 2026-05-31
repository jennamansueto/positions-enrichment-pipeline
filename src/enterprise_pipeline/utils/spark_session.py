"""SparkSession builder with Delta Lake support."""

from __future__ import annotations

from pyspark.sql import SparkSession


def get_spark_session(app_name: str = "enterprise-pipeline", warehouse_path: str = "./data/warehouse") -> SparkSession:
    """Build a SparkSession configured for Delta Lake in local mode."""
    builder = (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.warehouse.dir", warehouse_path)
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.enabled", "false")
    )
    return builder.getOrCreate()
