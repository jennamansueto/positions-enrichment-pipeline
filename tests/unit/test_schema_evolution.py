"""Tests for schema evolution (add-only)."""


from enterprise_pipeline.config.schema_registry import SchemaRegistry


class TestSchemaEvolution:
    def test_add_only_detects_new_fields(self) -> None:
        registry = SchemaRegistry("config/mappings")
        existing = ["security_id", "isin"]
        new_fields = registry.diff_schemas("security", existing)
        assert len(new_fields) > 0
        new_names = {f.name for f in new_fields}
        assert "security_id" not in new_names
        assert "cusip" in new_names

    def test_add_only_no_drops(self) -> None:
        """Verify diff only returns additions, never removals."""
        registry = SchemaRegistry("config/mappings")
        # Extra column in existing that's not in canonical — should not appear in diff
        existing = ["security_id", "isin", "extra_col_not_in_schema"]
        new_fields = registry.diff_schemas("security", existing)
        new_names = {f.name for f in new_fields}
        assert "extra_col_not_in_schema" not in new_names

    def test_case_insensitive_matching(self) -> None:
        registry = SchemaRegistry("config/mappings")
        existing = ["SECURITY_ID", "ISIN", "CUSIP"]
        new_fields = registry.diff_schemas("security", existing)
        new_names = {f.name for f in new_fields}
        assert "security_id" not in new_names
        assert "isin" not in new_names
