#!/usr/bin/env python3
"""Standalone schema validation script."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from enterprise_pipeline.config.domain_parser import DomainParser
from enterprise_pipeline.config.schema_registry import SchemaRegistry


def main() -> None:
    parser = DomainParser()
    registry = SchemaRegistry()

    print("=== Domain MD Files ===")
    domains = parser.parse_all()
    for name, config in domains.items():
        print(f"  {name}: {len(config.active_fields)} active fields, PK={config.primary_key}")

    print("\n=== Canonical JSON Schemas ===")
    schemas = registry.load_all()
    for name, schema in schemas.items():
        print(f"  {name}: {len(schema.fields)} fields, version={schema.version}")

    print("\n=== Cross-Check ===")
    errors = 0
    for domain_name in domains:
        if domain_name not in schemas:
            print(f"  ERROR: {domain_name} has MD but no canonical JSON")
            errors += 1
            continue

        md_fields = {f.target_field for f in domains[domain_name].active_fields}
        json_fields = {f.name for f in schemas[domain_name].fields}
        missing = md_fields - json_fields
        if missing:
            print(f"  WARNING: {domain_name} — {len(missing)} fields in MD but not JSON: {missing}")
        else:
            print(f"  {domain_name}: OK ({len(md_fields)} fields)")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
