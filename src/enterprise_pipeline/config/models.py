"""Pydantic models for pipeline configuration."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FieldMapping(BaseModel):
    """A single field mapping from source to target."""

    target_field: str
    source_field: str
    source_field_beta: str | None = None
    field_type: str
    status: str = "ACTIVE"
    description: str = ""
    group: str = ""


class DomainConfig(BaseModel):
    """Configuration for a single data domain parsed from markdown."""

    domain_name: str
    source_systems: list[str]
    source_table: str
    primary_key: list[str]
    load_strategy: str = "INCREMENTAL"
    fields: list[FieldMapping] = Field(default_factory=list)

    @property
    def active_fields(self) -> list[FieldMapping]:
        return [f for f in self.fields if f.status == "ACTIVE"]


class CanonicalField(BaseModel):
    """A field definition in the canonical JSON schema."""

    name: str
    type: str
    nullable: bool = True
    description: str = ""
    classification: str = "PII_NONE"
    group: str = ""
    lineage: str = ""


class CanonicalSchema(BaseModel):
    """Canonical schema for a domain, loaded from JSON."""

    domain: str
    version: str
    primary_key: list[str]
    fields: list[CanonicalField] = Field(default_factory=list)


class SourceConfig(BaseModel):
    """Source system connection configuration."""

    type: str
    path: str


class JoinConfig(BaseModel):
    """Join configuration for gold layer."""

    domain: str
    join_key: str | list[str]
    join_type: str = "left"


class WarehouseConfig(BaseModel):
    """Warehouse backend configuration."""

    backend: str = "delta_local"
    path: str = "./data/warehouse"


class MedallionConfig(BaseModel):
    """Medallion layer paths configuration."""

    bronze_path: str
    silver_path: str
    gold_path: str
    gold_table_name: str = "enterprise_positions"
    scd2_enabled: bool = True


class PipelineSettings(BaseModel):
    """Top-level pipeline settings."""

    name: str = "enterprise-positions"
    sources: dict[str, SourceConfig] = Field(default_factory=dict)
    warehouse: WarehouseConfig = Field(default_factory=WarehouseConfig)
    medallion: MedallionConfig | None = None
    joins: list[JoinConfig] = Field(default_factory=list)
    schema_evolution_mode: str = "add_only"
    schema_evolution_audit: bool = True
