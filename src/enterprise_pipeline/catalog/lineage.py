"""Field-level lineage tracking."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from enterprise_pipeline.config.models import CanonicalSchema

logger = logging.getLogger("enterprise_pipeline")


class LineageEntry:
    """Tracks lineage for a single field."""

    def __init__(
        self,
        target_field: str,
        source_system: str,
        source_table: str,
        source_column: str,
        domain: str,
        transformation: str = "direct_map",
    ) -> None:
        self.target_field = target_field
        self.source_system = source_system
        self.source_table = source_table
        self.source_column = source_column
        self.domain = domain
        self.transformation = transformation

    def to_dict(self) -> dict[str, str]:
        return {
            "target_field": self.target_field,
            "source_system": self.source_system,
            "source_table": self.source_table,
            "source_column": self.source_column,
            "domain": self.domain,
            "transformation": self.transformation,
        }


class LineageTracker:
    """Tracks and persists field-level lineage across the pipeline."""

    def __init__(self, output_dir: str = "quality_reports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.entries: list[LineageEntry] = []

    def track_from_schema(self, schema: CanonicalSchema) -> None:
        """Extract lineage entries from a canonical schema's lineage strings."""
        for field in schema.fields:
            if not field.lineage or field.lineage == "derived":
                self.entries.append(
                    LineageEntry(
                        target_field=field.name,
                        source_system="derived",
                        source_table="",
                        source_column="",
                        domain=schema.domain,
                        transformation="derived",
                    )
                )
                continue

            for lineage_path in field.lineage.split(" | "):
                parts = lineage_path.strip().split(".")
                if len(parts) >= 4:
                    self.entries.append(
                        LineageEntry(
                            target_field=field.name,
                            source_system=parts[0],
                            source_table=f"{parts[1]}.{parts[2]}",
                            source_column=parts[3],
                            domain=schema.domain,
                        )
                    )

    def write_lineage(self) -> Path:
        """Write lineage report as JSON."""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_fields": len(self.entries),
            "lineage": [e.to_dict() for e in self.entries],
        }
        path = self.output_dir / f"lineage_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        path.write_text(json.dumps(report, indent=2))
        logger.info("Lineage report written to %s (%d entries)", path, len(self.entries))
        return path
