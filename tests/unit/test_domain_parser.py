"""Tests for domain markdown file parsing."""


import pytest

from enterprise_pipeline.config.domain_parser import DomainParser


@pytest.fixture
def parser() -> DomainParser:
    return DomainParser("config/domains")


class TestDomainParser:
    def test_parse_positions(self, parser: DomainParser) -> None:
        config = parser.parse("positions")
        assert config.domain_name == "positions"
        assert "accounting_system_alpha" in config.source_systems
        assert "accounting_system_beta" in config.source_systems
        assert config.primary_key == ["position_id", "book_id", "as_of_date"]
        assert config.load_strategy == "INCREMENTAL"
        assert len(config.active_fields) >= 60

    def test_parse_security(self, parser: DomainParser) -> None:
        config = parser.parse("security")
        assert config.domain_name == "security"
        assert "security_master" in config.source_systems
        assert config.primary_key == ["security_id"]
        assert config.load_strategy == "FULL_REFRESH"
        assert len(config.active_fields) >= 80

    def test_parse_risk_analytics(self, parser: DomainParser) -> None:
        config = parser.parse("risk_analytics")
        assert config.domain_name == "risk_analytics"
        assert "risk_engine" in config.source_systems
        assert config.primary_key == ["risk_calc_id"]
        assert len(config.active_fields) >= 50

    def test_parse_all(self, parser: DomainParser) -> None:
        domains = parser.parse_all()
        assert "positions" in domains
        assert "security" in domains
        assert "risk_analytics" in domains

    def test_parse_nonexistent_domain(self, parser: DomainParser) -> None:
        with pytest.raises(FileNotFoundError):
            parser.parse("nonexistent")

    def test_active_fields_filter(self, parser: DomainParser) -> None:
        config = parser.parse("positions")
        for field in config.active_fields:
            assert field.status == "ACTIVE"

    def test_field_mapping_has_source(self, parser: DomainParser) -> None:
        config = parser.parse("security")
        for field in config.active_fields:
            assert field.source_field, f"Field {field.target_field} has no source mapping"

    def test_field_types_present(self, parser: DomainParser) -> None:
        config = parser.parse("positions")
        for field in config.active_fields:
            assert field.field_type, f"Field {field.target_field} has no type"
