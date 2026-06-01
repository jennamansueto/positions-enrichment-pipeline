"""Reader for accounting system beta (Eagle-like)."""

from __future__ import annotations

import logging
from datetime import date

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType

from enterprise_pipeline.connectors.parquet_reader import ParquetSourceReader
from enterprise_pipeline.ingestion.base import SourceReader

logger = logging.getLogger("enterprise_pipeline")

BETA_COLUMN_MAP = {
    "POSITION_KEY": "position_id",
    "BOOK_ID": "book_id",
    "AS_OF_DT": "as_of_date",
    "ACCOUNT_NUM": "account_id",
    "ACCOUNT_DESC": "account_name",
    "ACCT_CLASSIFICATION": "account_type",
    "LEGAL_ENTITY": "legal_entity_id",
    "LE_DESC": "legal_entity_name",
    "CUSTODIAN_CODE": "custodian_id",
    "CUSTODIAN_DESC": "custodian_name",
    "PRIME_BROKER": "prime_broker_id",
    "PB_DESC": "prime_broker_name",
    "SECURITY_KEY": "security_id",
    "UNITS_HELD": "quantity",
    "FACE_VALUE": "notional_amount",
    "MKT_VAL_LC": "market_value_local",
    "MKT_VAL_USD": "market_value_base",
    "ORIG_COST": "cost_basis",
    "ACCRUED": "accrued_interest",
    "UNREALIZED_GL": "unrealized_pnl",
    "REALIZED_GL": "realized_pnl",
    "TOTAL_GL": "total_pnl",
    "DAY_PNL": "daily_pnl",
    "MTD_GL": "mtd_pnl",
    "YTD_GL": "ytd_pnl",
    "TRADE_DT": "trade_date",
    "SETTLEMENT_DT": "settle_date",
    "EFFECTIVE_DT": "effective_date",
    "LONG_SHORT": "long_short_indicator",
    "POSITION_CLASS": "position_type",
    "STATUS": "position_status",
    "LOCAL_CCY": "currency",
    "RPT_CCY": "base_currency",
    "FX_RATE_USD": "fx_rate_to_base",
    "TRADING_DESK": "desk",
    "DESK_CODE": "desk_id",
    "STRATEGY_DESC": "strategy",
    "STRATEGY_CODE": "strategy_id",
    "PORTFOLIO_KEY": "portfolio_id",
    "PORTFOLIO_DESC": "portfolio_name",
    "FUND_KEY": "fund_id",
    "FUND_DESC": "fund_name",
    "TRADER_CODE": "trader_id",
    "TRADER_DESC": "trader_name",
    "CPTY_KEY": "counterparty_id",
    "CPTY_DESC": "counterparty_name",
    "CPTY_LEI": "counterparty_lei",
    "TAX_LOT_KEY": "lot_id",
    "TAX_LOT_DT": "lot_date",
    "TAX_LOT_COST": "lot_cost",
    "PORTFOLIO_PCT": "weight_in_portfolio",
    "FUND_PCT": "weight_in_fund",
    "MARGIN_AMT": "margin_requirement",
    "COLL_VALUE": "collateral_value",
    "HAIRCUT_PCT": "haircut_pct",
    "FINANCING_RT": "financing_rate",
    "FINANCING_AMT": "financing_cost",
    "SRC_REC_ID": "source_record_id",
    "LOAD_TIMESTAMP": "source_load_timestamp",
    "ACTIVE_FLAG": "is_active",
    "REG_CLASSIFICATION": "regulatory_book",
    "ACCT_METHOD": "accounting_treatment",
    # Performance attribution
    "RET_CONTRIB_1D": "return_contrib_1d",
    "RET_CONTRIB_MTD": "return_contrib_mtd",
    "RET_CONTRIB_YTD": "return_contrib_ytd",
    "DUR_CONTRIB": "duration_contribution",
    "SPREAD_CONTRIB": "spread_contribution",
    "SECTOR_ALLOC": "sector_allocation_pct",
    "COUNTRY_ALLOC": "country_allocation_pct",
}


class PositionsBetaReader(SourceReader):
    """Reads positions from accounting system beta (Eagle-like)."""

    def __init__(self, spark: SparkSession, source_path: str) -> None:
        self.spark = spark
        self._reader = ParquetSourceReader(spark, source_path)

    # Explicit list of canonical columns this reader produces (plus source_system tag)
    EXTRACT_COLUMNS: list[str] = [*list(BETA_COLUMN_MAP.values()), "source_system"]

    def extract(self, as_of_date: date) -> DataFrame:
        date_str = as_of_date.strftime("%Y%m%d")
        df = self._reader.read(date_str)

        # Rename source columns to canonical target names
        for src_col, tgt_col in BETA_COLUMN_MAP.items():
            if src_col in df.columns:
                df = df.withColumnRenamed(src_col, tgt_col)

        df = df.withColumn("source_system", F.lit("accounting_system_beta"))

        # Explicitly select only the declared canonical columns
        selected = [c for c in self.EXTRACT_COLUMNS if c in df.columns]
        df = df.select(*selected)

        logger.info("Extracted %d rows from accounting_system_beta for %s", df.count(), as_of_date)
        return df

    def get_schema(self) -> StructType:
        return StructType()

    @property
    def source_system_name(self) -> str:
        return "accounting_system_beta"

    @property
    def domain(self) -> str:
        return "positions"
