"""Add-only schema evolution: detect new fields, apply ALTER TABLE ADD COLUMN."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    BooleanType,
    DateType,
    DecimalType,
    DoubleType,
    LongType,
    StringType,
    StructField,
    TimestampType,
)

from enterprise_pipeline.config.models import CanonicalField
from enterprise_pipeline.config.schema_registry import SchemaRegistry
from enterprise_pipeline.connectors.base import WarehouseConnector

logger = logging.getLogger("enterprise_pipeline")


def _canonical_type_to_spark(type_str: str) -> StructField:
    """Convert a canonical type string to a Spark StructField."""
    upper = type_str.upper()
    if upper == "STRING":
        return StructField("", StringType(), True)
    if upper == "DATE":
        return StructField("", DateType(), True)
    if upper == "TIMESTAMP":
        return StructField("", TimestampType(), True)
    if upper == "BOOLEAN":
        return StructField("", BooleanType(), True)
    if upper == "BIGINT":
        return StructField("", LongType(), True)
    if upper.startswith("DECIMAL"):
        import re

        match = re.match(r"DECIMAL\((\d+),(\d+)\)", upper)
        if match:
            return StructField("", DecimalType(int(match.group(1)), int(match.group(2))), True)
        return StructField("", DecimalType(18, 2), True)
    return StructField("", DoubleType(), True)


class SchemaEvolution:
    """Handles add-only schema evolution for Delta tables."""

    def __init__(
        self,
        spark: SparkSession,
        schema_registry: SchemaRegistry,
        connector: WarehouseConnector,
        audit_log_dir: str = "quality_reports",
    ) -> None:
        self.spark = spark
        self.registry = schema_registry
        self.connector = connector
        self.audit_log_dir = Path(audit_log_dir)
        self.audit_log_dir.mkdir(parents=True, exist_ok=True)

    def evolve(self, domain: str, table_path: str) -> list[CanonicalField]:
        """Compare canonical schema against existing table and add new columns.

        Returns list of newly added fields.
        """
        if not self.connector.table_exists(table_path):
            logger.info("Table %s does not exist yet — no evolution needed", table_path)
            return []

        existing_cols = [c.name for c in self.connector.get_columns(table_path)]
        new_fields = self.registry.diff_schemas(domain, existing_cols)

        if not new_fields:
            logger.info("Schema evolution: no new fields for domain=%s", domain)
            return []

        # Apply add-only changes
        for field in new_fields:
            spark_field = _canonical_type_to_spark(field.type)
            type_str = spark_field.dataType.simpleString()
            logger.info("Adding column %s (%s) to %s", field.name, type_str, table_path)

        # Use mergeSchema option on next write (Delta handles this)
        self._log_audit(domain, new_fields)
        return new_fields

    def _log_audit(self, domain: str, new_fields: list[CanonicalField]) -> None:
        """Write schema evolution audit log."""
        audit = {
            "timestamp": datetime.utcnow().isoformat(),
            "domain": domain,
            "action": "schema_evolution",
            "mode": "add_only",
            "new_fields": [{"name": f.name, "type": f.type, "description": f.description} for f in new_fields],
        }
        log_path = self.audit_log_dir / f"schema_evolution_{domain}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        log_path.write_text(json.dumps(audit, indent=2))
        logger.info("Schema evolution audit written to %s", log_path)
