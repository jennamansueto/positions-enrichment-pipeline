"""Tests for pipeline configuration loading."""

import pytest

from enterprise_pipeline.config.pipeline_config import PipelineConfig


class TestPipelineConfig:
    def test_load_config(self) -> None:
        config = PipelineConfig("config/pipeline.yaml")
        settings = config.load()
        assert settings.name == "enterprise-positions"
        assert settings.warehouse.backend == "delta_local"
        assert len(settings.sources) == 4
        assert "accounting_system_alpha" in settings.sources
        assert len(settings.joins) == 2

    def test_medallion_config(self) -> None:
        config = PipelineConfig("config/pipeline.yaml")
        settings = config.load()
        assert settings.medallion is not None
        assert settings.medallion.scd2_enabled is True
        assert settings.medallion.gold_table_name == "enterprise_positions"

    def test_schema_evolution_settings(self) -> None:
        config = PipelineConfig("config/pipeline.yaml")
        settings = config.load()
        assert settings.schema_evolution_mode == "add_only"
        assert settings.schema_evolution_audit is True

    def test_nonexistent_config(self) -> None:
        config = PipelineConfig("nonexistent.yaml")
        with pytest.raises(FileNotFoundError):
            config.load()
