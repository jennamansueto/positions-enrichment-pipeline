"""Multi-source position consolidation (deduplication across accounting systems)."""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

logger = logging.getLogger("enterprise_pipeline")


def consolidate_positions(alpha_df: DataFrame, beta_df: DataFrame) -> DataFrame:
    """Consolidate positions from two accounting systems.

    When the same position exists in both systems (matched by composite key),
    the alpha system record takes precedence.
    """
    # Ensure both DataFrames have the same columns
    all_cols = sorted(set(alpha_df.columns) | set(beta_df.columns))

    for col_name in all_cols:
        if col_name not in alpha_df.columns:
            alpha_df = alpha_df.withColumn(col_name, F.lit(None))
        if col_name not in beta_df.columns:
            beta_df = beta_df.withColumn(col_name, F.lit(None))

    alpha_df = alpha_df.select(*all_cols)
    beta_df = beta_df.select(*all_cols)

    combined = alpha_df.unionByName(beta_df)

    # Deduplicate: alpha takes priority over beta
    source_priority = F.when(F.col("source_system") == "accounting_system_alpha", 1).otherwise(2)

    window = Window.partitionBy("position_id", "book_id", "as_of_date").orderBy(source_priority)

    deduped = combined.withColumn("_rank", F.row_number().over(window)).filter(F.col("_rank") == 1).drop("_rank")

    input_count = combined.count()
    output_count = deduped.count()
    logger.info(
        "Consolidated positions: %d input -> %d output (%d duplicates removed)",
        input_count,
        output_count,
        input_count - output_count,
    )

    return deduped
