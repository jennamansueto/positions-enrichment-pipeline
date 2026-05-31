"""Security domain transformer — cleaning and conforming."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enterprise_pipeline.transforms.base import DomainTransformer


class SecurityTransformer(DomainTransformer):
    """Cleans and conforms security reference data for the silver layer."""

    def transform(self, df: DataFrame) -> DataFrame:
        df = self._normalize_enums(df)
        df = self._validate_coupon_rate(df)
        df = self._validate_ratings(df)
        return df

    @property
    def domain(self) -> str:
        return "security"

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
