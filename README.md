# Enterprise Positions Enrichment Pipeline

A production-grade data pipeline that consolidates fixed-income positions from multiple accounting systems, enriches them with security reference data and risk analytics, and produces a denormalized enterprise dataset using medallion architecture.

## Architecture

```
Sources                   Bronze (raw)        Silver (SCD2)       Gold (joined)
┌─────────────────┐      ┌────────────┐      ┌────────────┐      ┌──────────────────┐
│ Accounting α    │─────▶│ positions  │─────▶│ positions  │──┐   │                  │
│ Accounting β    │─────▶│            │      │            │  ├──▶│ enterprise_      │
│ Security Master │─────▶│ security   │─────▶│ security   │──┤   │   positions      │
│ Risk Engine     │─────▶│ risk_analy │─────▶│ risk_analy │──┘   │ (~205 fields)    │
└─────────────────┘      └────────────┘      └────────────┘      └──────────────────┘
```

**Key features:**
- **Medallion architecture**: Bronze → Silver (with SCD2 historization) → Gold
- **~205 fields** across 3 domains: Positions (~65), Security (~85), Risk Analytics (~55)
- **SCD2 (Type 2 Slowly Changing Dimensions)**: Full history tracking with `_effective_from`, `_effective_to`, `_is_current`, `_record_hash`
- **Add-only schema evolution**: New fields can be added without breaking existing data
- **Multi-source consolidation**: Deduplicates positions from two accounting systems (alpha takes priority)
- **Data quality framework**: Cardinality, schema conformance, null rates, referential integrity, range checks
- **Field-level lineage**: Source → domain → output tracking for all fields

## Tech Stack

- **Python 3.11+** with PySpark + Delta Lake
- **uv** for dependency management
- **Docker** + **Kubernetes** (Kustomize overlays) for deployment
- **Flux** for GitOps

## Quick Start

```bash
# Install dependencies
make install

# Generate sample data (~500 positions, ~200 securities, ~500 risk calcs)
make generate-data

# Run the pipeline for today
make run

# Run tests
make test

# Lint + type check
make lint
make typecheck
```

## Project Structure

```
├── config/
│   ├── pipeline.yaml                 # Pipeline configuration
│   ├── domains/                      # Field mapping definitions (markdown)
│   │   ├── positions.md
│   │   ├── security.md
│   │   └── risk_analytics.md
│   └── mappings/                     # Canonical JSON schemas
│       ├── positions_canonical.json
│       ├── security_canonical.json
│       └── risk_analytics_canonical.json
├── src/enterprise_pipeline/
│   ├── config/                       # Config parsing, models, schema registry
│   ├── connectors/                   # Warehouse connectors (Delta, Snowflake)
│   ├── ingestion/                    # Source readers (strategy pattern)
│   ├── medallion/                    # Bronze, Silver (SCD2), Gold layers
│   ├── patterns/                     # SCD2, schema evolution, repository
│   ├── transforms/                   # Domain-specific data transformations
│   ├── builders/                     # Pipeline DAG builder
│   ├── quality/                      # Data quality checks & reporting
│   ├── catalog/                      # Lineage & metadata tracking
│   └── utils/                        # Spark session, Delta helpers, logging
├── tests/
│   ├── unit/                         # Unit tests (no Spark required)
│   └── integration/                  # Integration tests (requires Spark)
├── scripts/
│   ├── generate_sample_data.py       # Sample data generator
│   ├── run_pipeline.py               # Pipeline runner
│   └── validate_schema.py            # Schema validation
├── deploy/                           # Kubernetes manifests (Kustomize)
├── flux/                             # Flux GitOps configuration
└── docs/                             # Architecture & operational docs
```

## Configuration

### `config/pipeline.yaml`

Top-level pipeline configuration defining sources, warehouse backend, medallion layer paths, join configuration, and schema evolution settings.

### Domain Markdown Files

Field mappings are defined in `config/domains/*.md` using markdown tables. Each file specifies source-to-target field mappings, types, and status.

### Canonical JSON Schemas

Target schemas in `config/mappings/*_canonical.json` define the contract for each domain: field names, types, nullability, classifications, and lineage.

## Design Patterns

- **Repository**: Single interface for domain data at any medallion layer
- **Strategy**: Pluggable source readers and transformers
- **Builder**: Fluent pipeline construction

## Data Quality

Quality reports are written to `quality_reports/` as JSON:
- Row count validation (cardinality)
- Composite key uniqueness
- Schema conformance against canonical definitions
- Null rate checks for key and non-key fields
- Referential integrity (e.g., security_id in positions → security)
- Numeric range validation

## Deployment

```bash
# Local Docker
docker compose up

# Kubernetes (dev)
kubectl apply -k deploy/overlays/dev/

# Kubernetes (prod)
kubectl apply -k deploy/overlays/prod/
```

## License

Proprietary.
