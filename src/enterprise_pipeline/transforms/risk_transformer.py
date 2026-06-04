"""Risk analytics domain transformer — explicit type casting and cleaning."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enterprise_pipeline.transforms.base import DomainTransformer

# Explicit type-cast map: canonical field name -> target Spark type.
# Every risk analytics field is declared here; adding a new field requires a new entry.
RISK_FIELD_TYPES: dict[str, str] = {
    # Key fields
    "risk_calc_id": "string",
    "security_id": "string",
    "position_id": "string",
    "as_of_date": "date",
    "calc_timestamp": "timestamp",
    # Pricing
    "price_clean": "decimal(12,6)",
    "price_dirty": "decimal(12,6)",
    "price_mid": "decimal(12,6)",
    "price_bid": "decimal(12,6)",
    "price_ask": "decimal(12,6)",
    "price_source": "string",
    # Yields
    "yield_to_maturity": "decimal(8,5)",
    "yield_to_worst": "decimal(8,5)",
    "yield_to_call": "decimal(8,5)",
    "current_yield": "decimal(8,5)",
    "yield_spread_to_govt": "decimal(8,4)",
    # Duration
    "duration_macaulay": "decimal(10,6)",
    "duration_modified": "decimal(10,6)",
    "duration_effective": "decimal(10,6)",
    "duration_spread": "decimal(10,6)",
    "duration_key_rate_2y": "decimal(10,6)",
    "duration_key_rate_5y": "decimal(10,6)",
    "duration_key_rate_10y": "decimal(10,6)",
    "duration_key_rate_30y": "decimal(10,6)",
    # Sensitivities
    "convexity": "decimal(10,6)",
    "effective_convexity": "decimal(10,6)",
    "dv01": "decimal(18,2)",
    "cr01": "decimal(18,2)",
    "cs01": "decimal(18,2)",
    # Spreads
    "oas": "decimal(8,4)",
    "z_spread": "decimal(8,4)",
    "i_spread": "decimal(8,4)",
    "g_spread": "decimal(8,4)",
    "asset_swap_spread": "decimal(8,4)",
    # VaR
    "var_95_1d": "decimal(18,2)",
    "var_99_1d": "decimal(18,2)",
    "var_95_10d": "decimal(18,2)",
    "cvar_95_1d": "decimal(18,2)",
    "cvar_99_1d": "decimal(18,2)",
    # Portfolio risk
    "beta_to_benchmark": "decimal(8,4)",
    "tracking_error": "decimal(8,4)",
    # Greeks
    "delta": "decimal(10,6)",
    "gamma": "decimal(10,6)",
    "theta": "decimal(10,6)",
    "vega": "decimal(10,6)",
    "rho": "decimal(10,6)",
    # Scenarios
    "scenario_up_50bps": "decimal(18,2)",
    "scenario_down_50bps": "decimal(18,2)",
    "scenario_up_100bps": "decimal(18,2)",
    "scenario_down_100bps": "decimal(18,2)",
    "scenario_up_200bps": "decimal(18,2)",
    "scenario_credit_widen_100bps": "decimal(18,2)",
    "scenario_down_200bps": "decimal(18,2)",
    "scenario_up_300bps": "decimal(18,2)",
    "scenario_equity_down_10pct": "decimal(18,2)",
    "scenario_equity_down_20pct": "decimal(18,2)",
    "scenario_credit_tight_50bps": "decimal(18,2)",
    "scenario_vol_up_25pct": "decimal(18,2)",
    "scenario_fx_shock_10pct": "decimal(18,2)",
    # Volatility
    "implied_volatility": "decimal(8,4)",
    "historical_volatility_30d": "decimal(8,4)",
    "liquidity_score": "decimal(5,2)",
}

# Explicit output column list — the silver table for risk analytics contains exactly these.
RISK_OUTPUT_COLUMNS: list[str] = list(RISK_FIELD_TYPES.keys())


class RiskTransformer(DomainTransformer):
    """Cleans and conforms risk analytics data for the silver layer."""

    def transform(self, df: DataFrame) -> DataFrame:
        df = self._cast_types(df)
        df = self._normalize_price_source(df)
        df = self._validate_yields(df)
        df = self._validate_liquidity_score(df)
        df = self._select_output_columns(df)
        return df

    @property
    def domain(self) -> str:
        return "risk_analytics"

    @staticmethod
    def _cast_types(df: DataFrame) -> DataFrame:
        """Apply explicit type casts for every declared field."""
        for field, target_type in RISK_FIELD_TYPES.items():
            if field in df.columns:
                df = df.withColumn(field, F.col(field).cast(target_type))
        return df

    @staticmethod
    def _normalize_price_source(df: DataFrame) -> DataFrame:
        if "price_source" in df.columns:
            df = df.withColumn("price_source", F.upper(F.trim(F.col("price_source"))))
        return df

    @staticmethod
    def _validate_yields(df: DataFrame) -> DataFrame:
        """Clamp extreme yield values."""
        yield_fields = ["yield_to_maturity", "yield_to_worst", "yield_to_call", "current_yield"]
        for field in yield_fields:
            if field in df.columns:
                df = df.withColumn(
                    field,
                    F.when(
                        (F.col(field) >= -50) & (F.col(field) <= 200),
                        F.col(field),
                    ).otherwise(None),
                )
        return df

    @staticmethod
    def _validate_liquidity_score(df: DataFrame) -> DataFrame:
        """Ensure liquidity_score is between 0 and 100."""
        if "liquidity_score" in df.columns:
            df = df.withColumn(
                "liquidity_score",
                F.when(
                    (F.col("liquidity_score") >= 0) & (F.col("liquidity_score") <= 100),
                    F.col("liquidity_score"),
                ).otherwise(None),
            )
        return df

    @staticmethod
    def _select_output_columns(df: DataFrame) -> DataFrame:
        """Select only the explicitly declared output columns."""
        selected = [c for c in RISK_OUTPUT_COLUMNS if c in df.columns]
        return df.select(*selected)
