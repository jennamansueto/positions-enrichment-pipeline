# Operational Runbook

## Daily Pipeline Execution

### Normal Operation

The pipeline runs daily via Kubernetes CronJob at 06:00 UTC (weekdays):

```bash
# Manual run for a specific date
python -m enterprise_pipeline run --date 2026-05-28

# Via make
make run
```

### Monitoring

1. **Quality Reports**: Check `quality_reports/quality_report_*.json` after each run
2. **Schema Evolution Logs**: Check `quality_reports/schema_evolution_*.json` for field additions
3. **Spark UI**: Available on port 4040 during execution

### Common Issues

#### Pipeline fails with "No data ingested"

**Cause**: Source files not available for the requested date.

**Resolution**:
1. Verify source files exist in `data/raw/<source>/`
2. Check filename pattern matches expected date format (`*YYYYMMDD*.parquet`)
3. Regenerate sample data: `make generate-data`

#### SCD2 merge performance degradation

**Cause**: Large accumulation of historical records.

**Resolution**:
1. Review Delta table history: `DESCRIBE HISTORY delta.'path'`
2. Run VACUUM to remove old files: `VACUUM delta.'path' RETAIN 168 HOURS`
3. Consider partitioning by `as_of_date`

#### Schema validation failures

**Cause**: Mismatch between domain MD files and canonical JSON schemas.

**Resolution**:
1. Run `make validate-schema` to identify mismatches
2. Update the canonical JSON to include missing fields
3. Re-run pipeline (add-only evolution will handle the rest)

#### Docker build fails

**Cause**: Base Spark image or dependency issues.

**Resolution**:
1. Verify base image is available: `docker pull apache/spark-py:v3.5.1`
2. Clear Docker cache: `docker system prune`
3. Rebuild: `docker compose build --no-cache`

## Regenerating Sample Data

```bash
make generate-data
# Creates ~500 positions, ~200 securities, ~500 risk calculations
# across 3 business date snapshots
```

## Configuration Changes

1. **Adding a new field**: Add to domain MD + canonical JSON, pipeline handles evolution
2. **Adding a new source**: Implement `SourceReader`, register in `ReaderFactory`
3. **Switching to Snowflake**: Set `warehouse.backend: snowflake` in `pipeline.yaml`

## Backup & Recovery

- Delta Lake tables support time travel: `spark.read.format("delta").option("versionAsOf", 0).load(path)`
- Quality reports are append-only JSON files
- Configuration is version-controlled
