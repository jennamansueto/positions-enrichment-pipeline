"""CLI interface for the enterprise pipeline."""

from __future__ import annotations

from datetime import datetime

import click

from enterprise_pipeline.main import run_pipeline


@click.group()
def cli() -> None:
    """Enterprise Data Pipeline — Positions Enrichment."""


@cli.command()
@click.option("--date", "run_date", required=True, help="Business date (YYYY-MM-DD)")
@click.option("--config", default="config/pipeline.yaml", help="Pipeline config path")
@click.option("--log-level", default="INFO", help="Log level")
def run(run_date: str, config: str, log_level: str) -> None:
    """Run the full pipeline for a given business date."""
    as_of = datetime.strptime(run_date, "%Y-%m-%d").date()
    run_pipeline(as_of_date=as_of, config_path=config, log_level=log_level)


@cli.command()
def validate() -> None:
    """Validate configuration files (domain MD + canonical JSON)."""
    from enterprise_pipeline.config.domain_parser import DomainParser
    from enterprise_pipeline.config.schema_registry import SchemaRegistry

    parser = DomainParser()
    registry = SchemaRegistry()

    click.echo("Validating domain markdown files...")
    domains = parser.parse_all()
    for name, config in domains.items():
        click.echo(f"  {name}: {len(config.active_fields)} active fields")

    click.echo("\nValidating canonical JSON schemas...")
    schemas = registry.load_all()
    for name, schema in schemas.items():
        click.echo(f"  {name}: {len(schema.fields)} fields (v{schema.version})")

    click.echo("\nCross-checking MD ↔ JSON consistency...")
    for domain_name in domains:
        if domain_name not in schemas:
            click.echo(f"  WARNING: {domain_name} has MD but no canonical JSON")
            continue
        md_fields = {f.target_field for f in domains[domain_name].active_fields}
        json_fields = {f.name for f in schemas[domain_name].fields}
        missing_in_json = md_fields - json_fields
        if missing_in_json:
            click.echo(f"  WARNING: {domain_name} — fields in MD but not in JSON: {missing_in_json}")
        else:
            click.echo(f"  {domain_name}: OK")

    click.echo("\nValidation complete.")


@cli.command()
def info() -> None:
    """Show pipeline configuration summary."""
    from enterprise_pipeline.config.pipeline_config import PipelineConfig

    config = PipelineConfig()
    settings = config.load()
    click.echo(f"Pipeline: {settings.name}")
    click.echo(f"Backend: {settings.warehouse.backend}")
    click.echo(f"Sources: {list(settings.sources.keys())}")
    click.echo(f"Joins: {[(j.domain, j.join_key) for j in settings.joins]}")
    click.echo(f"Schema evolution: {settings.schema_evolution_mode}")


if __name__ == "__main__":
    cli()
