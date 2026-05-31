"""Loads and resolves the top-level pipeline.yaml configuration."""

from __future__ import annotations

import os
import re
from pathlib import Path

import yaml

from enterprise_pipeline.config.models import (
    JoinConfig,
    MedallionConfig,
    PipelineSettings,
    SourceConfig,
    WarehouseConfig,
)


class PipelineConfig:
    """Loads and resolves the pipeline configuration from YAML."""

    def __init__(self, config_path: str | Path = "config/pipeline.yaml") -> None:
        self.config_path = Path(config_path)
        self._raw: dict = {}  # type: ignore[type-arg]
        self._settings: PipelineSettings | None = None

    def load(self) -> PipelineSettings:
        """Load and parse the pipeline configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Pipeline config not found: {self.config_path}")

        raw_text = self.config_path.read_text()
        self._raw = yaml.safe_load(raw_text)

        warehouse_raw = self._raw.get("warehouse", {})
        backend = warehouse_raw.get("backend", "delta_local")
        backend_config = warehouse_raw.get(backend, {})
        warehouse_path = self._resolve_env_vars(backend_config.get("path", "./data/warehouse"))

        warehouse = WarehouseConfig(backend=backend, path=warehouse_path)

        sources: dict[str, SourceConfig] = {}
        for name, src_raw in self._raw.get("sources", {}).items():
            sources[name] = SourceConfig(
                type=src_raw.get("type", "parquet"),
                path=src_raw.get("path", ""),
            )

        medallion_raw = self._raw.get("medallion", {})
        bronze_path = self._resolve_path_refs(medallion_raw.get("bronze", {}).get("path", ""), warehouse_path)
        silver_path = self._resolve_path_refs(medallion_raw.get("silver", {}).get("path", ""), warehouse_path)
        gold_path = self._resolve_path_refs(medallion_raw.get("gold", {}).get("path", ""), warehouse_path)

        medallion = MedallionConfig(
            bronze_path=bronze_path,
            silver_path=silver_path,
            gold_path=gold_path,
            gold_table_name=medallion_raw.get("gold", {}).get("table_name", "enterprise_positions"),
            scd2_enabled=medallion_raw.get("silver", {}).get("scd2_enabled", True),
        )

        joins: list[JoinConfig] = []
        for j in self._raw.get("joins", []):
            joins.append(
                JoinConfig(
                    domain=j["domain"],
                    join_key=j["join_key"],
                    join_type=j.get("join_type", "left"),
                )
            )

        se = self._raw.get("schema_evolution", {})

        self._settings = PipelineSettings(
            name=self._raw.get("pipeline", {}).get("name", "enterprise-positions"),
            sources=sources,
            warehouse=warehouse,
            medallion=medallion,
            joins=joins,
            schema_evolution_mode=se.get("mode", "add_only"),
            schema_evolution_audit=se.get("audit_log", True),
        )
        return self._settings

    @property
    def settings(self) -> PipelineSettings:
        if self._settings is None:
            return self.load()
        return self._settings

    @staticmethod
    def _resolve_env_vars(value: str) -> str:
        """Replace ${ENV_VAR} with environment variable values."""

        def _replacer(match: re.Match[str]) -> str:
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))

        return re.sub(r"\$\{(\w+)\}", _replacer, value)

    @staticmethod
    def _resolve_path_refs(path: str, warehouse_path: str) -> str:
        """Resolve ${warehouse.path} references."""
        return path.replace("${warehouse.path}", warehouse_path)
