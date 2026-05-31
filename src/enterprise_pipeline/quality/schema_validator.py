"""Schema conformance validation."""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame

from enterprise_pipeline.config.models import CanonicalSchema

logger = logging.getLogger("enterprise_pipeline")


def check_schema_conformance(df: DataFrame, canonical: CanonicalSchema, label: str = "") -> dict[str, object]:
    """Validate that all canonical fields exist in the DataFrame."""
    df_cols = {c.lower() for c in df.columns}
    canonical_cols = {f.name.lower() for f in canonical.fields}
    missing = canonical_cols - df_cols
    internal_cols = {
        "_record_hash", "_effective_from", "_effective_to", "_is_current",
        "_batch_id", "_pipeline_timestamp", "_source_system", "_ingestion_timestamp",
    }
    extra = df_cols - canonical_cols - internal_cols

    passed = len(missing) == 0
    status = "PASS" if passed else "FAIL"
    missing_str = sorted(missing) if missing else "none"
    message = f"Missing columns: {missing_str}, extra: {len(extra)} [{status}]"

    logger.info("Schema conformance [%s]: %s", label, message)
    return {
        "check": "schema_conformance",
        "label": label,
        "missing_columns": sorted(missing),
        "extra_columns": sorted(extra),
        "passed": passed,
        "message": message,
    }
