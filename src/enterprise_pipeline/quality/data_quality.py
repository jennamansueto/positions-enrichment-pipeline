"""Data quality checks: nulls, referential integrity, range validation."""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

logger = logging.getLogger("enterprise_pipeline")


def check_null_rates(
    df: DataFrame,
    key_columns: list[str],
    max_null_rate: float = 0.5,
    label: str = "",
) -> dict[str, object]:
    """Check null rates for key and non-key columns."""
    total = df.count()
    if total == 0:
        return {"check": "null_rates", "label": label, "passed": True, "message": "Empty DataFrame"}

    results: dict[str, float] = {}
    failures: list[str] = []

    for col_name in df.columns:
        null_count = df.filter(F.col(col_name).isNull()).count()
        null_rate = null_count / total
        results[col_name] = round(null_rate, 4)

        if col_name in key_columns and null_rate > 0:
            failures.append(f"{col_name} (key, null_rate={null_rate:.2%})")
        elif null_rate > max_null_rate:
            failures.append(f"{col_name} (null_rate={null_rate:.2%} > {max_null_rate:.0%})")

    passed = len(failures) == 0
    message = f"Null check failures: {failures if failures else 'none'} [{'PASS' if passed else 'FAIL'}]"
    logger.info("Null rate check [%s]: %d columns checked, %d failures", label, len(results), len(failures))

    return {
        "check": "null_rates",
        "label": label,
        "column_null_rates": results,
        "failures": failures,
        "passed": passed,
        "message": message,
    }


def check_referential_integrity(
    child_df: DataFrame,
    parent_df: DataFrame,
    join_key: str,
    label: str = "",
) -> dict[str, object]:
    """Check that all join key values in child exist in parent."""
    child_keys = child_df.select(join_key).distinct()
    parent_keys = parent_df.select(join_key).distinct()
    orphans = child_keys.join(parent_keys, on=join_key, how="left_anti")
    orphan_count = orphans.count()

    passed = orphan_count == 0
    message = f"Orphan {join_key} values: {orphan_count} [{'PASS' if passed else 'FAIL'}]"
    logger.info("Referential integrity [%s]: %s", label, message)

    return {
        "check": "referential_integrity",
        "label": label,
        "join_key": join_key,
        "orphan_count": orphan_count,
        "passed": passed,
        "message": message,
    }


def check_range(
    df: DataFrame,
    column: str,
    min_val: float | None = None,
    max_val: float | None = None,
    label: str = "",
) -> dict[str, object]:
    """Check that numeric values are within expected bounds."""
    if column not in df.columns:
        return {"check": "range", "label": label, "column": column, "passed": True, "message": "Column not present"}

    violations = df.filter(F.col(column).isNotNull())
    if min_val is not None:
        violations = violations.filter(F.col(column) < min_val)
    if max_val is not None:
        remaining = df.filter(F.col(column).isNotNull()).filter(F.col(column) > max_val)
        violations = violations.unionByName(remaining) if min_val is not None else remaining

    violation_count = violations.count()
    passed = violation_count == 0
    message = f"{column}: {violation_count} out-of-range values [{'PASS' if passed else 'FAIL'}]"
    logger.info("Range check [%s]: %s", label, message)

    return {
        "check": "range",
        "label": label,
        "column": column,
        "min": min_val,
        "max": max_val,
        "violations": violation_count,
        "passed": passed,
        "message": message,
    }
