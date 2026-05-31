"""Loads and validates canonical JSON schema files."""

from __future__ import annotations

import json
from pathlib import Path

from enterprise_pipeline.config.models import CanonicalField, CanonicalSchema


class SchemaRegistry:
    """Registry for canonical domain schemas loaded from JSON files."""

    def __init__(self, mappings_dir: str | Path = "config/mappings") -> None:
        self.mappings_dir = Path(mappings_dir)
        self._schemas: dict[str, CanonicalSchema] = {}

    def load(self, domain: str) -> CanonicalSchema:
        """Load a canonical schema for a domain from its JSON file."""
        filepath = self.mappings_dir / f"{domain}_canonical.json"
        if not filepath.exists():
            raise FileNotFoundError(f"Canonical schema not found: {filepath}")

        raw = json.loads(filepath.read_text())
        schema = CanonicalSchema(
            domain=raw["domain"],
            version=raw["version"],
            primary_key=raw["primary_key"],
            fields=[CanonicalField(**f) for f in raw["fields"]],
        )
        self._schemas[domain] = schema
        return schema

    def load_all(self) -> dict[str, CanonicalSchema]:
        """Load all canonical schemas from the mappings directory."""
        for json_file in sorted(self.mappings_dir.glob("*_canonical.json")):
            domain = json_file.stem.replace("_canonical", "")
            self.load(domain)
        return self._schemas

    def get(self, domain: str) -> CanonicalSchema:
        """Get a loaded schema by domain name."""
        if domain not in self._schemas:
            self.load(domain)
        return self._schemas[domain]

    def get_field_names(self, domain: str) -> list[str]:
        """Get list of field names for a domain."""
        schema = self.get(domain)
        return [f.name for f in schema.fields]

    def get_primary_key(self, domain: str) -> list[str]:
        """Get the primary key fields for a domain."""
        schema = self.get(domain)
        return schema.primary_key

    def diff_schemas(self, domain: str, existing_columns: list[str]) -> list[CanonicalField]:
        """Find fields in the canonical schema that are not in the existing table.

        Returns only new fields (add-only — never drops or renames).
        """
        schema = self.get(domain)
        existing_set = {c.lower() for c in existing_columns}
        return [f for f in schema.fields if f.name.lower() not in existing_set]
