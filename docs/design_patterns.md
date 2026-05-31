# Design Patterns

## Repository Pattern

Each data domain has a `DomainRepository` that provides a unified interface for reading and writing data at any medallion layer:

```python
repo = DomainRepository(
    domain="positions",
    connector=delta_connector,
    bronze_path="./data/warehouse/bronze",
    silver_path="./data/warehouse/silver",
)

# Read/write at any layer
repo.write_bronze(df)
bronze_df = repo.read_bronze()

repo.write_silver(df)
silver_df = repo.read_silver(as_of=date(2026, 5, 28))
current_df = repo.read_current()  # _is_current=True only
```

The connector is injected, so the same repository works with Delta Lake (local) or Snowflake (production).

## Strategy Pattern

### Source Readers

Each source system implements the `SourceReader` interface:

```python
class SourceReader(ABC):
    def extract(self, as_of_date: date) -> DataFrame: ...
    def get_schema(self) -> StructType: ...
    @property
    def source_system_name(self) -> str: ...
    @property
    def domain(self) -> str: ...
```

Implementations: `PositionsAlphaReader`, `PositionsBetaReader`, `SecurityReader`, `RiskReader`.

### Domain Transformers

Each domain implements the `DomainTransformer` interface:

```python
class DomainTransformer(ABC):
    def transform(self, df: DataFrame) -> DataFrame: ...
    @property
    def domain(self) -> str: ...
```

Implementations: `PositionsTransformer`, `SecurityTransformer`, `RiskTransformer`.

## Builder Pattern

The `PipelineBuilder` constructs the full pipeline DAG using a fluent API:

```python
pipeline = (
    PipelineBuilder(spark, connector)
    .with_source("positions", alpha_reader)
    .with_source("positions", beta_reader)
    .with_source("security", security_reader)
    .with_source("risk_analytics", risk_reader)
    .with_transformer("positions", PositionsTransformer())
    .with_transformer("security", SecurityTransformer())
    .with_transformer("risk_analytics", RiskTransformer())
    .with_primary_key("positions", ["position_id", "book_id", "as_of_date"])
    .with_medallion_config(medallion_config)
    .with_joins(join_configs)
    .build()
)
```

The builder validates that all required components are present and returns a `PipelineComponents` dataclass with all layers, repositories, and transformers ready to execute.
