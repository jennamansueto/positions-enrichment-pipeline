"""Positions domain transformer — cleaning and conforming."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enterprise_pipeline.transforms.base import DomainTransformer


class PositionsTransformer(DomainTransformer):
    """Cleans and conforms positions data for the silver layer."""

    def transform(self, df: DataFrame) -> DataFrame:
        df = self._normalize_strings(df)
        df = self._add_derived_timestamps(df)
        df = self._validate_position_status(df)
        df = self._compute_total_pnl(df)
        return df

    @property
    def domain(self) -> str:
        return "positions"

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
