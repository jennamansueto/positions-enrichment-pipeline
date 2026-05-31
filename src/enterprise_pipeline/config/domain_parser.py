"""Parses domain .md files to extract field mappings and source configuration."""

from __future__ import annotations

import re
from pathlib import Path

from enterprise_pipeline.config.models import DomainConfig, FieldMapping


class DomainParser:
    """Parses a domain markdown file into a DomainConfig."""

    def __init__(self, config_dir: str | Path = "config/domains") -> None:
        self.config_dir = Path(config_dir)

    def parse(self, domain_name: str) -> DomainConfig:
        """Parse a domain markdown file and return a DomainConfig."""
        filepath = self.config_dir / f"{domain_name}.md"
        if not filepath.exists():
            raise FileNotFoundError(f"Domain config not found: {filepath}")

        content = filepath.read_text()
        source_systems = self._parse_source_systems(content)
        source_table = self._parse_source_table(content)
        primary_key = self._parse_primary_key(content)
        load_strategy = self._parse_load_strategy(content)
        fields = self._parse_fields(content, domain_name)

        return DomainConfig(
            domain_name=domain_name,
            source_systems=source_systems,
            source_table=source_table,
            primary_key=primary_key,
            load_strategy=load_strategy,
            fields=fields,
        )

    def parse_all(self) -> dict[str, DomainConfig]:
        """Parse all domain markdown files in the config directory."""
        domains: dict[str, DomainConfig] = {}
        for md_file in sorted(self.config_dir.glob("*.md")):
            domain_name = md_file.stem
            domains[domain_name] = self.parse(domain_name)
        return domains

    def _parse_source_systems(self, content: str) -> list[str]:
        match = re.search(r"\*\*Source Systems?\*\*:\s*(.+)", content)
        if match:
            raw = match.group(1).strip()
            return [s.strip() for s in raw.split(",")]
        return []

    def _parse_source_table(self, content: str) -> str:
        match = re.search(r"\*\*Source Tables?\*\*:\s*(.+)", content)
        if match:
            return match.group(1).strip()
        return ""

    def _parse_primary_key(self, content: str) -> list[str]:
        match = re.search(r"\*\*Primary Key\*\*:\s*(.+)", content)
        if match:
            raw = match.group(1).strip()
            return [k.strip() for k in raw.split(",")]
        return []

    def _parse_load_strategy(self, content: str) -> str:
        match = re.search(r"\*\*Load Strategy\*\*:\s*(.+)", content)
        if match:
            return match.group(1).strip()
        return "INCREMENTAL"

    def _parse_fields(self, content: str, domain_name: str) -> list[FieldMapping]:
        """Parse field mapping tables from the markdown content."""
        fields: list[FieldMapping] = []
        current_group = ""

        for line in content.split("\n"):
            # Track section headers for grouping
            group_match = re.match(r"^###\s+(.+)", line)
            if group_match:
                current_group = group_match.group(1).strip()
                continue

            # Parse table rows (skip header and separator lines)
            if not line.startswith("|") or line.startswith("|---") or line.startswith("| Target"):
                continue

            parts = [p.strip() for p in line.split("|")]
            parts = [p for p in parts if p]

            if len(parts) < 4:
                continue

            if domain_name == "positions" and len(parts) >= 6:
                field = FieldMapping(
                    target_field=parts[0],
                    source_field=parts[1],
                    source_field_beta=parts[2] if parts[2] != "—" else None,
                    field_type=parts[3],
                    status=parts[4],
                    description=parts[5] if len(parts) > 5 else "",
                    group=current_group,
                )
            elif len(parts) >= 5:
                field = FieldMapping(
                    target_field=parts[0],
                    source_field=parts[1],
                    field_type=parts[2],
                    status=parts[3],
                    description=parts[4] if len(parts) > 4 else "",
                    group=current_group,
                )
            else:
                continue

            fields.append(field)

        return fields
