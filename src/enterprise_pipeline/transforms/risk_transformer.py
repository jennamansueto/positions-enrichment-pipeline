"""Risk analytics domain transformer — cleaning and conforming."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enterprise_pipeline.transforms.base import DomainTransformer


class RiskTransformer(DomainTransformer):
    """Cleans and conforms risk analytics data for the silver layer."""

    def transform(self, df: DataFrame) -> DataFrame:
        df = self._normalize_price_source(df)
        df = self._validate_yields(df)
        df = self._validate_liquidity_score(df)
        return df

    @property
    def domain(self) -> str:
        return "risk_analytics"

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
