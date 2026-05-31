"""Reader for accounting system alpha (Geneva-like)."""

from __future__ import annotations

import logging
from datetime import date

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType

from enterprise_pipeline.connectors.parquet_reader import ParquetSourceReader
from enterprise_pipeline.ingestion.base import SourceReader

logger = logging.getLogger("enterprise_pipeline")

# Column mapping: Alpha source field -> canonical target field
ALPHA_COLUMN_MAP = {
    "POS_ID": "position_id",
    "BOOK_CODE": "book_id",
    "BUS_DATE": "as_of_date",
    "ACCT_ID": "account_id",
    "ACCT_NAME": "account_name",
    "ACCT_TYPE": "account_type",
    "LE_ID": "legal_entity_id",
    "LE_NAME": "legal_entity_name",
    "CUST_ID": "custodian_id",
    "CUST_NAME": "custodian_name",
    "PB_ID": "prime_broker_id",
    "PB_NAME": "prime_broker_name",
    "SEC_ID": "security_id",
    "QTY": "quantity",
    "NOTIONAL": "notional_amount",
    "MV_LOCAL": "market_value_local",
    "MV_BASE": "market_value_base",
    "COST_BASIS": "cost_basis",
    "ACCR_INT": "accrued_interest",
    "UNREAL_PNL": "unrealized_pnl",
    "REAL_PNL": "realized_pnl",
    "TOTAL_PNL": "total_pnl",
    "DAILY_PNL": "daily_pnl",
    "MTD_PNL": "mtd_pnl",
    "YTD_PNL": "ytd_pnl",
    "TRD_DATE": "trade_date",
    "SETTLE_DATE": "settle_date",
    "EFF_DATE": "effective_date",
    "LS_IND": "long_short_indicator",
    "POS_TYPE": "position_type",
    "POS_STATUS": "position_status",
    "CCY": "currency",
    "BASE_CCY": "base_currency",
    "FX_RATE": "fx_rate_to_base",
    "DESK_NAME": "desk",
    "DESK_ID": "desk_id",
    "STRAT_NAME": "strategy",
    "STRAT_ID": "strategy_id",
    "PORT_ID": "portfolio_id",
    "PORT_NAME": "portfolio_name",
    "FUND_ID": "fund_id",
    "FUND_NAME": "fund_name",
    "TRADER_ID": "trader_id",
    "TRADER_NAME": "trader_name",
    "CP_ID": "counterparty_id",
    "CP_NAME": "counterparty_name",
    "CP_LEI": "counterparty_lei",
    "LOT_ID": "lot_id",
    "LOT_DATE": "lot_date",
    "LOT_COST": "lot_cost",
    "PORT_WEIGHT": "weight_in_portfolio",
    "FUND_WEIGHT": "weight_in_fund",
    "MARGIN_REQ": "margin_requirement",
    "COLLATERAL_VAL": "collateral_value",
    "HAIRCUT": "haircut_pct",
    "FIN_RATE": "financing_rate",
    "FIN_COST": "financing_cost",
    "RECORD_ID": "source_record_id",
    "LOAD_TS": "source_load_timestamp",
    "IS_ACTIVE": "is_active",
    "REG_BOOK": "regulatory_book",
    "ACCT_TREATMENT": "accounting_treatment",
}


class PositionsAlphaReader(SourceReader):
    """Reads positions from accounting system alpha (Geneva-like)."""

    def __init__(self, spark: SparkSession, source_path: str) -> None:
        self.spark = spark
        self._reader = ParquetSourceReader(spark, source_path)

    def extract(self, as_of_date: date) -> DataFrame:
        date_str = as_of_date.strftime("%Y%m%d")
        df = self._reader.read(date_str)

        # Rename columns to canonical names
        for src_col, tgt_col in ALPHA_COLUMN_MAP.items():
            if src_col in df.columns:
                df = df.withColumnRenamed(src_col, tgt_col)

        # Tag with source system
        df = df.withColumn("source_system", F.lit("accounting_system_alpha"))

        logger.info("Extracted %d rows from accounting_system_alpha for %s", df.count(), as_of_date)
        return df

    def get_schema(self) -> StructType:
        return StructType()

    @property
    def source_system_name(self) -> str:
        return "accounting_system_alpha"

    @property
    def domain(self) -> str:
        return "positions"
