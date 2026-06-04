"""Reader for the risk engine source system."""

from __future__ import annotations

import logging
from datetime import date

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from enterprise_pipeline.connectors.parquet_reader import ParquetSourceReader
from enterprise_pipeline.ingestion.base import SourceReader

logger = logging.getLogger("enterprise_pipeline")

RISK_COLUMN_MAP = {
    "CALC_ID": "risk_calc_id",
    "SEC_ID": "security_id",
    "POS_ID": "position_id",
    "CALC_DATE": "as_of_date",
    "CALC_TS": "calc_timestamp",
    "CLEAN_PX": "price_clean",
    "DIRTY_PX": "price_dirty",
    "MID_PX": "price_mid",
    "BID_PX": "price_bid",
    "ASK_PX": "price_ask",
    "PX_SOURCE": "price_source",
    "YTM": "yield_to_maturity",
    "YTW": "yield_to_worst",
    "YTC": "yield_to_call",
    "CUR_YIELD": "current_yield",
    "SPREAD_GOVT": "yield_spread_to_govt",
    "DUR_MAC": "duration_macaulay",
    "DUR_MOD": "duration_modified",
    "DUR_EFF": "duration_effective",
    "DUR_SPREAD": "duration_spread",
    "KRD_2Y": "duration_key_rate_2y",
    "KRD_5Y": "duration_key_rate_5y",
    "KRD_10Y": "duration_key_rate_10y",
    "KRD_30Y": "duration_key_rate_30y",
    "CONVEXITY": "convexity",
    "EFF_CONVEXITY": "effective_convexity",
    "DV01": "dv01",
    "CR01": "cr01",
    "CS01": "cs01",
    "OAS": "oas",
    "Z_SPREAD": "z_spread",
    "I_SPREAD": "i_spread",
    "G_SPREAD": "g_spread",
    "ASW_SPREAD": "asset_swap_spread",
    "VAR_95_1D": "var_95_1d",
    "VAR_99_1D": "var_99_1d",
    "VAR_95_10D": "var_95_10d",
    "CVAR_95_1D": "cvar_95_1d",
    "CVAR_99_1D": "cvar_99_1d",
    "BETA": "beta_to_benchmark",
    "TRACK_ERR": "tracking_error",
    "DELTA": "delta",
    "GAMMA": "gamma",
    "THETA": "theta",
    "VEGA": "vega",
    "RHO": "rho",
    "CHARM": "charm",
    "VANNA": "vanna",
    "VOLGA": "volga",
    "SPEED": "speed",
    "COLOR": "color",
    "SCEN_UP_50": "scenario_up_50bps",
    "SCEN_DN_50": "scenario_down_50bps",
    "SCEN_UP_100": "scenario_up_100bps",
    "SCEN_DN_100": "scenario_down_100bps",
    "SCEN_UP_200": "scenario_up_200bps",
    "SCEN_CRD_100": "scenario_credit_widen_100bps",
    "IMPL_VOL": "implied_volatility",
    "HIST_VOL_30D": "historical_volatility_30d",
    "LIQ_SCORE": "liquidity_score",
}


class RiskReader(SourceReader):
    """Reads risk analytics from the risk engine."""

    def __init__(self, spark: SparkSession, source_path: str) -> None:
        self.spark = spark
        self._reader = ParquetSourceReader(spark, source_path)

    # Explicit list of canonical columns this reader produces
    EXTRACT_COLUMNS: list[str] = list(RISK_COLUMN_MAP.values())

    def extract(self, as_of_date: date) -> DataFrame:
        date_str = as_of_date.strftime("%Y%m%d")
        df = self._reader.read(date_str)

        # Rename source columns to canonical target names
        for src_col, tgt_col in RISK_COLUMN_MAP.items():
            if src_col in df.columns:
                df = df.withColumnRenamed(src_col, tgt_col)

        # Explicitly select only the declared canonical columns
        selected = [c for c in self.EXTRACT_COLUMNS if c in df.columns]
        df = df.select(*selected)

        logger.info("Extracted %d risk calculations for %s", df.count(), as_of_date)
        return df

    def get_schema(self) -> StructType:
        return StructType()

    @property
    def source_system_name(self) -> str:
        return "risk_engine"

    @property
    def domain(self) -> str:
        return "risk_analytics"
