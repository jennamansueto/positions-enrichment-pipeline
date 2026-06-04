"""Reader for the security master source system."""

from __future__ import annotations

import logging
from datetime import date

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from enterprise_pipeline.connectors.parquet_reader import ParquetSourceReader
from enterprise_pipeline.ingestion.base import SourceReader

logger = logging.getLogger("enterprise_pipeline")

SECURITY_COLUMN_MAP = {
    "SEC_ID": "security_id",
    "ISIN_CODE": "isin",
    "CUSIP_NUM": "cusip",
    "SEDOL_NUM": "sedol",
    "TICKER": "ticker",
    "BBG_GLOBAL_ID": "bbg_global_id",
    "RIC_CODE": "ric",
    "FIGI_CODE": "figi",
    "SEC_NAME": "security_name",
    "SEC_SHORT_NAME": "security_short_name",
    "SEC_DESC": "security_description",
    "SEC_TYPE": "security_type",
    "ASSET_CLASS": "asset_class",
    "SUB_ASSET_CLASS": "sub_asset_class",
    "PRODUCT_TYPE": "product_type",
    "ISSUER_ID": "issuer_id",
    "ISSUER_NAME": "issuer_name",
    "ISSUER_SHORT": "issuer_short_name",
    "ISSUER_LEI": "issuer_lei",
    "ISSUER_COUNTRY": "issuer_country",
    "ISSUER_DOMICILE": "issuer_domicile",
    "ISSUER_SECTOR": "issuer_sector",
    "CPN_RATE": "coupon_rate",
    "CPN_FREQ": "coupon_frequency",
    "CPN_TYPE": "coupon_type",
    "CPN_CCY": "coupon_currency",
    "DAY_COUNT": "day_count_convention",
    "ACCR_START_DT": "accrual_start_date",
    "FIRST_CPN_DT": "first_coupon_date",
    "LAST_CPN_DT": "last_coupon_date",
    "NEXT_CPN_DT": "next_coupon_date",
    "MATURITY_DT": "maturity_date",
    "ISSUE_DT": "issue_date",
    "DATED_DT": "dated_date",
    "FIRST_SETTLE_DT": "first_settle_date",
    "WORST_CALL_DT": "worst_call_date",
    "WORST_PUT_DT": "worst_put_date",
    "NEXT_CALL_DT": "next_call_date",
    "NEXT_PUT_DT": "next_put_date",
    "FIRST_CALL_DT": "first_call_date",
    "FIRST_PUT_DT": "first_put_date",
    "CALL_PRICE": "call_price",
    "PUT_PRICE": "put_price",
    "CALL_TYPE": "call_type",
    "IS_CALLABLE": "is_callable",
    "IS_PUTTABLE": "is_puttable",
    "IS_CONVERTIBLE": "is_convertible",
    "IS_PERPETUAL": "is_perpetual",
    "IS_144A": "is_144a",
    "IS_REG_S": "is_reg_s",
    "PAR_VALUE": "par_value",
    "MIN_DENOM": "minimum_denomination",
    "MIN_INCR": "minimum_increment",
    "ISSUE_SIZE": "issue_size",
    "AMT_OUTSTANDING": "amount_outstanding",
    "CCY": "currency",
    "CTRY_RISK": "country_of_risk",
    "CTRY_DOMICILE": "country_of_domicile",
    "CTRY_INCORP": "country_of_incorporation",
    "REGION": "region",
    "SECTOR": "sector",
    "IND_GROUP": "industry_group",
    "INDUSTRY": "industry",
    "SUB_INDUSTRY": "sub_industry",
    "RATING_SP": "credit_rating_sp",
    "RATING_MOODY": "credit_rating_moody",
    "RATING_FITCH": "credit_rating_fitch",
    "RATING_COMPOSITE": "composite_rating",
    "OUTLOOK_SP": "rating_outlook_sp",
    "OUTLOOK_MOODY": "rating_outlook_moody",
    "SENIORITY": "seniority",
    "COLLATERAL_TYPE": "collateral_type",
    "GUARANTEE_TYPE": "guarantee_type",
    "PAYMENT_RANK": "payment_rank",
    "BENCHMARK_IDX": "benchmark_index",
    "SPREAD_BM": "spread_to_benchmark",
    "FLOAT_IDX": "float_index",
    "FLOAT_SPREAD": "float_spread",
    "FLOAT_RESET_FREQ": "float_reset_frequency",
    "EXCHANGE": "exchange",
    "LISTING_STATUS": "listing_status",
    "TRADING_STATUS": "trading_status",
    "SETTLE_TYPE": "settlement_type",
    "TAX_STATUS": "tax_status",
    # ESG
    "ESG_SCORE": "esg_score",
    "ENVIRONMENTAL_SCORE": "environmental_score",
    "SOCIAL_SCORE": "social_score",
    "GOVERNANCE_SCORE": "governance_score",
    "CARBON_INTENSITY": "carbon_intensity",
    "CREATED_TS": "created_timestamp",
}


class SecurityReader(SourceReader):
    """Reads security reference data from the security master."""

    def __init__(self, spark: SparkSession, source_path: str) -> None:
        self.spark = spark
        self._reader = ParquetSourceReader(spark, source_path)

    # Explicit list of canonical columns this reader produces
    EXTRACT_COLUMNS: list[str] = list(SECURITY_COLUMN_MAP.values())

    def extract(self, as_of_date: date) -> DataFrame:
        date_str = as_of_date.strftime("%Y%m%d")
        df = self._reader.read(date_str)

        # Rename source columns to canonical target names
        for src_col, tgt_col in SECURITY_COLUMN_MAP.items():
            if src_col in df.columns:
                df = df.withColumnRenamed(src_col, tgt_col)

        # Explicitly select only the declared canonical columns
        selected = [c for c in self.EXTRACT_COLUMNS if c in df.columns]
        df = df.select(*selected)

        logger.info("Extracted %d securities for %s", df.count(), as_of_date)
        return df

    def get_schema(self) -> StructType:
        return StructType()

    @property
    def source_system_name(self) -> str:
        return "security_master"

    @property
    def domain(self) -> str:
        return "security"
