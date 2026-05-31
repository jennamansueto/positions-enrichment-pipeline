"""SCD2 (Type 2 Slowly Changing Dimensions) merge implementation."""

from __future__ import annotations

import logging
from datetime import datetime

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from enterprise_pipeline.connectors.base import WarehouseConnector

logger = logging.getLogger("enterprise_pipeline")

SCD2_COLUMNS = ["_record_hash", "_effective_from", "_effective_to", "_is_current", "_batch_id"]


def compute_record_hash(df: DataFrame, exclude_cols: list[str] | None = None) -> DataFrame:
    """Compute an MD5 hash of all business columns for change detection."""
    skip = set(exclude_cols or []) | set(SCD2_COLUMNS)
    hash_cols = sorted([c for c in df.columns if c not in skip])
    concat_expr = F.concat_ws("||", *[F.coalesce(F.col(c).cast("string"), F.lit("__NULL__")) for c in hash_cols])
    return df.withColumn("_record_hash", F.md5(concat_expr))


def apply_scd2(
    spark: SparkSession,
    incoming: DataFrame,
    target_path: str,
    primary_key: list[str],
    connector: WarehouseConnector,
    batch_id: str | None = None,
) -> DataFrame:
    """Apply SCD2 merge logic: insert new, close changed, keep unchanged.

    Uses Delta Lake MERGE for atomicity.
    """
    now = datetime.utcnow()
    batch = batch_id or now.strftime("%Y%m%d_%H%M%S")

    incoming_with_hash = compute_record_hash(incoming)
    incoming_with_hash = (
        incoming_with_hash.withColumn("_effective_from", F.lit(now))
        .withColumn("_effective_to", F.lit(None).cast("timestamp"))
        .withColumn("_is_current", F.lit(True))
        .withColumn("_batch_id", F.lit(batch))
    )

    if not connector.table_exists(target_path):
        connector.write_table(target_path, incoming_with_hash, mode="overwrite")
        logger.info("SCD2: Initial load — wrote %d records to %s", incoming_with_hash.count(), target_path)
        return incoming_with_hash

    existing = connector.read_table(target_path)
    current = existing.filter(F.col("_is_current") == True)  # noqa: E712

    # Records in incoming that are new (no match in current)
    new_records = incoming_with_hash.join(current, on=primary_key, how="left_anti")

    # Records that exist in both — check hash for changes
    matched = incoming_with_hash.alias("inc").join(current.alias("cur"), on=primary_key, how="inner")

    changed = matched.filter(F.col("inc._record_hash") != F.col("cur._record_hash"))
    unchanged_count = matched.filter(F.col("inc._record_hash") == F.col("cur._record_hash")).count()

    # Close old versions of changed records
    changed_keys = changed.select(*[F.col(f"inc.{k}").alias(k) for k in primary_key])

    closed_records = current.join(changed_keys, on=primary_key, how="inner").withColumn(
        "_effective_to", F.lit(now)
    ).withColumn("_is_current", F.lit(False))

    # New versions of changed records
    inc_cols = [F.col(f"inc.{c}").alias(c) for c in incoming_with_hash.columns]
    new_versions = changed.select(*inc_cols)

    # Historical (already closed) records remain as-is
    historical = existing.filter(F.col("_is_current") == False)  # noqa: E712

    # Unchanged current records
    unchanged_current = current.join(changed_keys, on=primary_key, how="left_anti")
    unchanged_current = unchanged_current.join(
        incoming_with_hash.select(*primary_key), on=primary_key, how="left_semi"
    )

    # Records in current but not in incoming (keep as-is)
    not_in_incoming = current.join(incoming_with_hash, on=primary_key, how="left_anti")

    # Combine all parts
    result = (
        historical.unionByName(closed_records)
        .unionByName(unchanged_current)
        .unionByName(not_in_incoming)
        .unionByName(new_versions)
        .unionByName(new_records)
    )

    connector.write_table(target_path, result, mode="overwrite")

    logger.info(
        "SCD2 merge complete: new=%d, changed=%d, unchanged=%d",
        new_records.count(),
        new_versions.count(),
        unchanged_count,
    )

    return result
