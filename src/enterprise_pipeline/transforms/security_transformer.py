"""Security domain transformer — explicit type casting and cleaning."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enterprise_pipeline.transforms.base import DomainTransformer

# Explicit type-cast map: canonical field name -> target Spark type.
# Every security field is declared here; adding a new field requires a new entry.
SECURITY_FIELD_TYPES: dict[str, str] = {
    # Identifiers
    "security_id": "string",
    "isin": "string",
    "cusip": "string",
    "sedol": "string",
    "ticker": "string",
    "bbg_global_id": "string",
    "ric": "string",
    "figi": "string",
    # Names
    "security_name": "string",
    "security_short_name": "string",
    "security_description": "string",
    # Classification
    "security_type": "string",
    "asset_class": "string",
    "sub_asset_class": "string",
    "product_type": "string",
    # Issuer
    "issuer_id": "string",
    "issuer_name": "string",
    "issuer_short_name": "string",
    "issuer_lei": "string",
    "issuer_country": "string",
    "issuer_domicile": "string",
    "issuer_sector": "string",
    # Coupon / payment
    "coupon_rate": "decimal(8,5)",
    "coupon_frequency": "string",
    "coupon_type": "string",
    "coupon_currency": "string",
    "day_count_convention": "string",
    # Dates
    "accrual_start_date": "date",
    "first_coupon_date": "date",
    "last_coupon_date": "date",
    "next_coupon_date": "date",
    "maturity_date": "date",
    "issue_date": "date",
    "dated_date": "date",
    "first_settle_date": "date",
    # Call / put
    "worst_call_date": "date",
    "worst_put_date": "date",
    "next_call_date": "date",
    "next_put_date": "date",
    "first_call_date": "date",
    "first_put_date": "date",
    "call_price": "decimal(12,6)",
    "put_price": "decimal(12,6)",
    "call_type": "string",
    "is_callable": "boolean",
    "is_puttable": "boolean",
    "is_convertible": "boolean",
    "is_perpetual": "boolean",
    "is_144a": "boolean",
    "is_reg_s": "boolean",
    # Sizing
    "par_value": "decimal(18,2)",
    "minimum_denomination": "decimal(18,2)",
    "minimum_increment": "decimal(18,2)",
    "issue_size": "decimal(18,2)",
    "amount_outstanding": "decimal(18,2)",
    "currency": "string",
    # Geography
    "country_of_risk": "string",
    "country_of_domicile": "string",
    "country_of_incorporation": "string",
    "region": "string",
    # Sector / industry
    "sector": "string",
    "industry_group": "string",
    "industry": "string",
    "sub_industry": "string",
    # Credit ratings
    "credit_rating_sp": "string",
    "credit_rating_moody": "string",
    "credit_rating_fitch": "string",
    "composite_rating": "string",
    "rating_outlook_sp": "string",
    "rating_outlook_moody": "string",
    # Structure
    "seniority": "string",
    "collateral_type": "string",
    "guarantee_type": "string",
    "payment_rank": "string",
    # Floating rate
    "benchmark_index": "string",
    "spread_to_benchmark": "decimal(8,4)",
    "float_index": "string",
    "float_spread": "decimal(8,4)",
    "float_reset_frequency": "string",
    # Trading
    "exchange": "string",
    "listing_status": "string",
    "trading_status": "string",
    "settlement_type": "string",
    "tax_status": "string",
    # Timestamps
    "created_timestamp": "timestamp",
    # ESG
    "esg_score": "decimal(5,2)",
    "environmental_score": "decimal(5,2)",
    "social_score": "decimal(5,2)",
    "governance_score": "decimal(5,2)",
    "carbon_intensity": "decimal(10,2)",
    "esg_controversy_flag": "boolean",
    "green_bond_flag": "boolean",
}

# Explicit output column list — the silver table for security contains exactly these.
SECURITY_OUTPUT_COLUMNS: list[str] = list(SECURITY_FIELD_TYPES.keys())


class SecurityTransformer(DomainTransformer):
    """Cleans and conforms security reference data for the silver layer."""

    def transform(self, df: DataFrame) -> DataFrame:
        df = self._cast_types(df)
        df = self._normalize_enums(df)
        df = self._validate_coupon_rate(df)
        df = self._validate_ratings(df)
        df = self._validate_esg_scores(df)
        df = self._validate_carbon_intensity(df)
        df = self._select_output_columns(df)
        return df

    @property
    def domain(self) -> str:
        return "security"

    @staticmethod
    def _cast_types(df: DataFrame) -> DataFrame:
        """Apply explicit type casts for every declared field."""
        for field, target_type in SECURITY_FIELD_TYPES.items():
            if field in df.columns:
                df = df.withColumn(field, F.col(field).cast(target_type))
        return df

    @staticmethod
    def _normalize_enums(df: DataFrame) -> DataFrame:
        enum_fields = [
            "security_type",
            "asset_class",
            "sub_asset_class",
            "product_type",
            "coupon_frequency",
            "coupon_type",
            "call_type",
            "seniority",
            "trading_status",
            "tax_status",
        ]
        for field in enum_fields:
            if field in df.columns:
                df = df.withColumn(field, F.upper(F.trim(F.col(field))))
        return df

    @staticmethod
    def _validate_coupon_rate(df: DataFrame) -> DataFrame:
        """Ensure coupon_rate is within reasonable bounds (0-100)."""
        if "coupon_rate" in df.columns:
            df = df.withColumn(
                "coupon_rate",
                F.when(
                    (F.col("coupon_rate") >= 0) & (F.col("coupon_rate") <= 100),
                    F.col("coupon_rate"),
                ).otherwise(None),
            )
        return df

    @staticmethod
    def _validate_ratings(df: DataFrame) -> DataFrame:
        """Uppercase credit rating fields."""
        rating_fields = [
            "credit_rating_sp",
            "credit_rating_moody",
            "credit_rating_fitch",
            "composite_rating",
        ]
        for field in rating_fields:
            if field in df.columns:
                df = df.withColumn(field, F.upper(F.trim(F.col(field))))
        return df

    @staticmethod
    def _validate_esg_scores(df: DataFrame) -> DataFrame:
        """Ensure ESG scores are between 0 and 100."""
        for field in ["esg_score", "environmental_score", "social_score", "governance_score"]:
            if field in df.columns:
                df = df.withColumn(
                    field,
                    F.when(
                        (F.col(field) >= 0) & (F.col(field) <= 100),
                        F.col(field),
                    ).otherwise(None),
                )
        return df

    @staticmethod
    def _validate_carbon_intensity(df: DataFrame) -> DataFrame:
        """Ensure carbon_intensity is non-negative."""
        if "carbon_intensity" in df.columns:
            df = df.withColumn(
                "carbon_intensity",
                F.when(
                    F.col("carbon_intensity") >= 0,
                    F.col("carbon_intensity"),
                ).otherwise(None),
            )
        return df

    @staticmethod
    def _select_output_columns(df: DataFrame) -> DataFrame:
        """Select only the explicitly declared output columns."""
        selected = [c for c in SECURITY_OUTPUT_COLUMNS if c in df.columns]
        return df.select(*selected)
