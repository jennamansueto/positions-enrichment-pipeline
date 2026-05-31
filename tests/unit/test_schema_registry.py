"""Tests for canonical JSON schema loading and validation."""

import pytest

from enterprise_pipeline.config.schema_registry import SchemaRegistry


@pytest.fixture
def registry() -> SchemaRegistry:
    return SchemaRegistry("config/mappings")


class TestSchemaRegistry:
    def test_load_positions(self, registry: SchemaRegistry) -> None:
        schema = registry.load("positions")
        assert schema.domain == "positions"
        assert schema.primary_key == ["position_id", "book_id", "as_of_date"]
        assert len(schema.fields) >= 60

    def test_load_security(self, registry: SchemaRegistry) -> None:
        schema = registry.load("security")
        assert schema.domain == "security"
        assert schema.primary_key == ["security_id"]
        assert len(schema.fields) >= 80

    def test_load_risk_analytics(self, registry: SchemaRegistry) -> None:
        schema = registry.load("risk_analytics")
        assert schema.domain == "risk_analytics"
        assert len(schema.fields) >= 50

    def test_load_all(self, registry: SchemaRegistry) -> None:
        schemas = registry.load_all()
        assert "positions" in schemas
        assert "security" in schemas
        assert "risk_analytics" in schemas

    def test_get_field_names(self, registry: SchemaRegistry) -> None:
        names = registry.get_field_names("positions")
        assert "position_id" in names
        assert "security_id" in names
        assert "market_value_base" in names

    def test_diff_schemas_detects_new_fields(self, registry: SchemaRegistry) -> None:
        existing = ["security_id", "isin", "cusip"]
        new_fields = registry.diff_schemas("security", existing)
        assert len(new_fields) > 0
        new_names = {f.name for f in new_fields}
        assert "security_id" not in new_names
        assert "isin" not in new_names
        assert "coupon_rate" in new_names

    def test_diff_schemas_empty_when_complete(self, registry: SchemaRegistry) -> None:
        all_names = registry.get_field_names("positions")
        new_fields = registry.diff_schemas("positions", all_names)
        assert len(new_fields) == 0

    def test_load_nonexistent(self, registry: SchemaRegistry) -> None:
        with pytest.raises(FileNotFoundError):
            registry.load("nonexistent")

    def test_field_lineage_present(self, registry: SchemaRegistry) -> None:
        schema = registry.load("security")
        for field in schema.fields:
            assert field.lineage, f"Field {field.name} has no lineage"
