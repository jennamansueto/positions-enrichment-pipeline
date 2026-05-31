# Architecture

## Overview

The Enterprise Positions Enrichment Pipeline implements a medallion architecture (Bronze → Silver → Gold) using PySpark and Delta Lake. It ingests fixed-income position data from two accounting systems, enriches it with security reference data and risk analytics, and produces a denormalized enterprise dataset.

## System Context

```
┌──────────────────────────────────────────────────┐
│              Enterprise Pipeline                  │
│                                                  │
│  ┌────────┐   ┌────────┐   ┌────────┐          │
│  │ Bronze │──▶│ Silver │──▶│  Gold  │          │
│  │  Layer │   │ Layer  │   │ Layer  │          │
│  └────┬───┘   └────┬───┘   └────┬───┘          │
│       │            │            │               │
│  Raw ingest   SCD2 merge   Denormalized join    │
│                                                  │
│  ┌──────────────────────────────────┐           │
│  │        Quality Framework         │           │
│  │  Cardinality · Schema · Lineage  │           │
│  └──────────────────────────────────┘           │
└──────────────────────────────────────────────────┘
     ▲           ▲          ▲            ▲
     │           │          │            │
  Acct α     Acct β    Sec Master   Risk Engine
```

## Data Flow

1. **Ingestion**: Source readers extract data from Parquet files (local) or external systems. Column names are mapped from source-specific names to canonical target names.

2. **Bronze**: Raw data is written as-is with metadata columns (`_source_system`, `_ingestion_timestamp`). For positions, data from both accounting systems is consolidated with alpha taking priority.

3. **Silver**: Domain transformers clean and conform the data (uppercase enums, validate bounds, derive computed fields). SCD2 merge logic tracks changes: unchanged rows keep their current record, changed rows get their old version closed and a new version inserted.

4. **Gold**: Current records from all silver tables are joined at position grain: positions LEFT JOIN security ON `security_id`, LEFT JOIN risk_analytics ON `position_id`.

## Warehouse Backends

The connector abstraction supports:
- **Delta Lake (local)**: Default for development. Reads/writes Delta tables on local filesystem.
- **Snowflake**: Production target. Uses Spark Snowflake connector (placeholder implementation).

## Schema Evolution

The pipeline supports add-only schema evolution:
- New fields in the canonical schema are detected by comparing against existing table columns
- Columns can only be added, never dropped or renamed
- All changes are audit-logged to `quality_reports/`

## Configuration

Three layers of configuration:
1. `pipeline.yaml`: Runtime settings (sources, warehouse, joins)
2. `domains/*.md`: Field mappings from source → target
3. `mappings/*_canonical.json`: Target schema contract
