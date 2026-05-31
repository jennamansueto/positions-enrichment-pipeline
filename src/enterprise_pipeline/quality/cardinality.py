"""Cardinality validation — row count checks."""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame

logger = logging.getLogger("enterprise_pipeline")


def check_cardinality(
    df: DataFrame,
    expected_count: int | None = None,
    tolerance_pct: float = 0.0,
    label: str = "",
) -> dict[str, object]:
    """Validate row count against an expected count.

    Returns a quality check result dict.
    """
    actual_count = df.count()
    passed = True
    message = f"Row count: {actual_count}"

    if expected_count is not None:
        lower = int(expected_count * (1 - tolerance_pct))
        upper = int(expected_count * (1 + tolerance_pct))
        passed = lower <= actual_count <= upper
        message = (
            f"Expected ~{expected_count} rows (±{tolerance_pct*100:.0f}%), "
            f"got {actual_count} [{'PASS' if passed else 'FAIL'}]"
        )

    logger.info("Cardinality check [%s]: %s", label, message)
    return {
        "check": "cardinality",
        "label": label,
        "expected": expected_count,
        "actual": actual_count,
        "passed": passed,
        "message": message,
    }


def check_uniqueness(df: DataFrame, key_columns: list[str], label: str = "") -> dict[str, object]:
    """Verify composite key uniqueness — no duplicate rows."""
    total = df.count()
    distinct = df.select(*key_columns).distinct().count()
    duplicates = total - distinct
    passed = duplicates == 0

    message = f"Unique keys: {distinct}/{total}, duplicates: {duplicates} [{'PASS' if passed else 'FAIL'}]"
    logger.info("Uniqueness check [%s]: %s", label, message)

    return {
        "check": "uniqueness",
        "label": label,
        "total_rows": total,
        "distinct_keys": distinct,
        "duplicates": duplicates,
        "passed": passed,
        "message": message,
    }
