"""Positions domain transformer — explicit type casting and cleaning."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enterprise_pipeline.transforms.base import DomainTransformer

# Explicit type-cast map: canonical field name -> target Spark type.
# Every positions field is declared here; adding a new field requires a new entry.
POSITIONS_FIELD_TYPES: dict[str, str] = {
    # Key fields
    "position_id": "string",
    "book_id": "string",
    "as_of_date": "date",
    "account_id": "string",
    "account_name": "string",
    "account_type": "string",
    "legal_entity_id": "string",
    "legal_entity_name": "string",
    "custodian_id": "string",
    "custodian_name": "string",
    "prime_broker_id": "string",
    "prime_broker_name": "string",
    "security_id": "string",
    # Position values
    "quantity": "decimal(18,4)",
    "notional_amount": "decimal(18,2)",
    "market_value_local": "decimal(18,2)",
    "market_value_base": "decimal(18,2)",
    "cost_basis": "decimal(18,2)",
    "accrued_interest": "decimal(18,2)",
    "unrealized_pnl": "decimal(18,2)",
    "realized_pnl": "decimal(18,2)",
    "total_pnl": "decimal(18,2)",
    "daily_pnl": "decimal(18,2)",
    "mtd_pnl": "decimal(18,2)",
    "ytd_pnl": "decimal(18,2)",
    # Dates
    "trade_date": "date",
    "settle_date": "date",
    "effective_date": "date",
    # Classification
    "long_short_indicator": "string",
    "position_type": "string",
    "position_status": "string",
    # Currency / FX
    "currency": "string",
    "base_currency": "string",
    "fx_rate_to_base": "decimal(12,6)",
    # Organizational
    "desk": "string",
    "desk_id": "string",
    "strategy": "string",
    "strategy_id": "string",
    "portfolio_id": "string",
    "portfolio_name": "string",
    "fund_id": "string",
    "fund_name": "string",
    "trader_id": "string",
    "trader_name": "string",
    "counterparty_id": "string",
    "counterparty_name": "string",
    "counterparty_lei": "string",
    # Tax lots
    "lot_id": "string",
    "lot_date": "date",
    "lot_cost": "decimal(18,2)",
    # Portfolio weights
    "weight_in_portfolio": "decimal(8,4)",
    "weight_in_fund": "decimal(8,4)",
    # Margin / collateral
    "margin_requirement": "decimal(18,2)",
    "collateral_value": "decimal(18,2)",
    "haircut_pct": "decimal(8,4)",
    "financing_rate": "decimal(8,6)",
    "financing_cost": "decimal(18,2)",
    # Source tracking
    "source_system": "string",
    "source_record_id": "string",
    "source_load_timestamp": "timestamp",
    "created_timestamp": "timestamp",
    "updated_timestamp": "timestamp",
    "is_active": "boolean",
    # Regulatory
    "regulatory_book": "string",
    "accounting_treatment": "string",
    # Settlement
    "settlement_currency": "string",
    "failed_settlement_indicator": "boolean",
    "settlement_instruction_type": "string",
    "settlement_location": "string",
}

# Explicit output column list — the silver table for positions contains exactly these.
POSITIONS_OUTPUT_COLUMNS: list[str] = list(POSITIONS_FIELD_TYPES.keys())


class PositionsTransformer(DomainTransformer):
    """Cleans and conforms positions data for the silver layer."""

    def transform(self, df: DataFrame) -> DataFrame:
        df = self._cast_types(df)
        df = self._normalize_strings(df)
        df = self._add_derived_timestamps(df)
        df = self._validate_position_status(df)
        df = self._compute_total_pnl(df)
        df = self._select_output_columns(df)
        return df

    @property
    def domain(self) -> str:
        return "positions"

    @staticmethod
    def _cast_types(df: DataFrame) -> DataFrame:
        """Apply explicit type casts for every declared field."""
        for field, target_type in POSITIONS_FIELD_TYPES.items():
            if field in df.columns:
                df = df.withColumn(field, F.col(field).cast(target_type))
        return df

    @staticmethod
    def _normalize_strings(df: DataFrame) -> DataFrame:
        """Uppercase standardized enum-like fields."""
        enum_fields = [
            "long_short_indicator",
            "position_type",
            "position_status",
            "account_type",
            "base_currency",
            "currency",
            "regulatory_book",
            "accounting_treatment",
            "settlement_currency",
            "settlement_instruction_type",
            "settlement_location",
        ]
        for field in enum_fields:
            if field in df.columns:
                df = df.withColumn(field, F.upper(F.trim(F.col(field))))
        return df

    @staticmethod
    def _add_derived_timestamps(df: DataFrame) -> DataFrame:
        """Add created/updated timestamps if not present."""
        now = F.current_timestamp()
        if "created_timestamp" not in df.columns:
            df = df.withColumn("created_timestamp", now)
        if "updated_timestamp" not in df.columns:
            df = df.withColumn("updated_timestamp", now)
        return df

    @staticmethod
    def _validate_position_status(df: DataFrame) -> DataFrame:
        """Ensure position_status is one of the valid values."""
        valid_statuses = ["OPEN", "CLOSED", "PENDING"]
        if "position_status" in df.columns:
            df = df.withColumn(
                "position_status",
                F.when(F.col("position_status").isin(valid_statuses), F.col("position_status")).otherwise("OPEN"),
            )
        return df

    @staticmethod
    def _compute_total_pnl(df: DataFrame) -> DataFrame:
        """Re-derive total_pnl when missing."""
        if "total_pnl" in df.columns and "unrealized_pnl" in df.columns and "realized_pnl" in df.columns:
            df = df.withColumn(
                "total_pnl",
                F.coalesce(F.col("total_pnl"), F.col("unrealized_pnl") + F.col("realized_pnl")),
            )
        return df

    @staticmethod
    def _select_output_columns(df: DataFrame) -> DataFrame:
        """Select only the explicitly declared output columns."""
        selected = [c for c in POSITIONS_OUTPUT_COLUMNS if c in df.columns]
        return df.select(*selected)
