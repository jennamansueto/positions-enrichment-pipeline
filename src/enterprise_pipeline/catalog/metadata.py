"""Cataloging, tagging, and metadata management."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from enterprise_pipeline.config.models import CanonicalSchema

logger = logging.getLogger("enterprise_pipeline")


class MetadataCatalog:
    """Manages field-level metadata: tags, classifications, audit trail."""

    def __init__(self, output_dir: str = "quality_reports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.entries: list[dict[str, object]] = []

    def catalog_schema(self, schema: CanonicalSchema) -> None:
        """Build catalog entries from a canonical schema."""
        for field in schema.fields:
            self.entries.append(
                {
                    "domain": schema.domain,
                    "field_name": field.name,
                    "data_type": field.type,
                    "nullable": field.nullable,
                    "description": field.description,
                    "classification": field.classification,
                    "group": field.group,
                    "tags": self._derive_tags(field.group, field.name),
                    "version": schema.version,
                    "cataloged_at": datetime.utcnow().isoformat(),
                }
            )

    def write_catalog(self) -> Path:
        """Write the metadata catalog as JSON."""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_fields": len(self.entries),
            "catalog": self.entries,
        }
        path = self.output_dir / f"catalog_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        path.write_text(json.dumps(report, indent=2, default=str))
        logger.info("Metadata catalog written to %s (%d entries)", path, len(self.entries))
        return path

    @staticmethod
    def _derive_tags(group: str, field_name: str) -> list[str]:
        """Derive tags from field group and name."""
        tags: list[str] = []
        if group:
            tags.append(group)

        tag_keywords = {
            "identifier": ["_id", "isin", "cusip", "sedol", "ticker", "figi", "lei"],
            "fixed_income": ["coupon", "maturity", "call", "put", "yield", "duration", "convexity"],
            "pricing": ["price", "px", "market_value", "nav"],
            "risk": ["var_", "cvar_", "dv01", "cr01", "delta", "gamma", "vega", "scenario_"],
            "pnl": ["pnl", "realized", "unrealized"],
        }

        for tag, keywords in tag_keywords.items():
            if any(kw in field_name.lower() for kw in keywords):
                tags.append(tag)

        return list(set(tags))
