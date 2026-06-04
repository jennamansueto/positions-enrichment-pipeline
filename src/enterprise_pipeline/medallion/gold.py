"""Gold layer: denormalized enterprise dataset with explicit column lists."""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from enterprise_pipeline.config.models import JoinConfig
from enterprise_pipeline.connectors.base import WarehouseConnector
from enterprise_pipeline.patterns.repository import DomainRepository

logger = logging.getLogger("enterprise_pipeline")

# ---------------------------------------------------------------------------
# Explicit output column lists per domain.
# Adding a new field to the gold layer requires adding it here.
# ---------------------------------------------------------------------------

# Columns from the positions silver table included in the gold output.
POSITIONS_GOLD_COLUMNS: list[str] = [
    # Key fields
    "position_id",
    "book_id",
    "as_of_date",
    "account_id",
    "account_name",
    "account_type",
    "legal_entity_id",
    "legal_entity_name",
    "custodian_id",
    "custodian_name",
    "prime_broker_id",
    "prime_broker_name",
    "security_id",
    # Position values
    "quantity",
    "notional_amount",
    "market_value_local",
    "market_value_base",
    "cost_basis",
    "accrued_interest",
    "unrealized_pnl",
    "realized_pnl",
    "total_pnl",
    "daily_pnl",
    "mtd_pnl",
    "ytd_pnl",
    # Dates
    "trade_date",
    "settle_date",
    "effective_date",
    # Classification
    "long_short_indicator",
    "position_type",
    "position_status",
    # Currency / FX
    "currency",
    "base_currency",
    "fx_rate_to_base",
    # Organizational
    "desk",
    "desk_id",
    "strategy",
    "strategy_id",
    "portfolio_id",
    "portfolio_name",
    "fund_id",
    "fund_name",
    "trader_id",
    "trader_name",
    "counterparty_id",
    "counterparty_name",
    "counterparty_lei",
    # Tax lots
    "lot_id",
    "lot_date",
    "lot_cost",
    # Portfolio weights
    "weight_in_portfolio",
    "weight_in_fund",
    # Margin / collateral
    "margin_requirement",
    "collateral_value",
    "haircut_pct",
    "financing_rate",
    "financing_cost",
    # Return contributions
    "return_contribution_1d",
    "return_contribution_mtd",
    "return_contribution_ytd",
    # Source tracking
    "source_system",
    "source_record_id",
    "source_load_timestamp",
    "created_timestamp",
    "updated_timestamp",
    "is_active",
    # Regulatory
    "regulatory_book",
    "accounting_treatment",
]

# Columns from the security silver table included in the gold output.
# Excludes join key (security_id) and SCD2 metadata (already on positions).
SECURITY_GOLD_COLUMNS: list[str] = [
    # Identifiers
    "isin",
    "cusip",
    "sedol",
    "ticker",
    "bbg_global_id",
    "ric",
    "figi",
    # Names
    "security_name",
    "security_short_name",
    "security_description",
    # Classification
    "security_type",
    "asset_class",
    "sub_asset_class",
    "product_type",
    # Issuer
    "issuer_id",
    "issuer_name",
    "issuer_short_name",
    "issuer_lei",
    "issuer_country",
    "issuer_domicile",
    "issuer_sector",
    # Coupon / payment
    "coupon_rate",
    "coupon_frequency",
    "coupon_type",
    "coupon_currency",
    "day_count_convention",
    # Dates
    "accrual_start_date",
    "first_coupon_date",
    "last_coupon_date",
    "next_coupon_date",
    "maturity_date",
    "issue_date",
    "dated_date",
    "first_settle_date",
    # Call / put
    "worst_call_date",
    "worst_put_date",
    "next_call_date",
    "next_put_date",
    "first_call_date",
    "first_put_date",
    "call_price",
    "put_price",
    "call_type",
    "is_callable",
    "is_puttable",
    "is_convertible",
    "is_perpetual",
    "is_144a",
    "is_reg_s",
    # Sizing
    "par_value",
    "minimum_denomination",
    "minimum_increment",
    "issue_size",
    "amount_outstanding",
    "currency",
    # Geography
    "country_of_risk",
    "country_of_domicile",
    "country_of_incorporation",
    "region",
    # Sector / industry
    "sector",
    "industry_group",
    "industry",
    "sub_industry",
    # Credit ratings
    "credit_rating_sp",
    "credit_rating_moody",
    "credit_rating_fitch",
    "composite_rating",
    "rating_outlook_sp",
    "rating_outlook_moody",
    # Structure
    "seniority",
    "collateral_type",
    "guarantee_type",
    "payment_rank",
    # Floating rate
    "benchmark_index",
    "spread_to_benchmark",
    "float_index",
    "float_spread",
    "float_reset_frequency",
    # Trading
    "exchange",
    "listing_status",
    "trading_status",
    "settlement_type",
    "tax_status",
    # Timestamps
    "created_timestamp",
]

# Columns from the risk analytics silver table included in the gold output.
# Excludes join keys (security_id, position_id) and SCD2 metadata.
RISK_GOLD_COLUMNS: list[str] = [
    "risk_calc_id",
    "calc_timestamp",
    # Pricing
    "price_clean",
    "price_dirty",
    "price_mid",
    "price_bid",
    "price_ask",
    "price_source",
    # Yields
    "yield_to_maturity",
    "yield_to_worst",
    "yield_to_call",
    "current_yield",
    "yield_spread_to_govt",
    # Duration
    "duration_macaulay",
    "duration_modified",
    "duration_effective",
    "duration_spread",
    "duration_key_rate_2y",
    "duration_key_rate_5y",
    "duration_key_rate_10y",
    "duration_key_rate_30y",
    # Sensitivities
    "convexity",
    "effective_convexity",
    "dv01",
    "cr01",
    "cs01",
    # Spreads
    "oas",
    "z_spread",
    "i_spread",
    "g_spread",
    "asset_swap_spread",
    # VaR
    "var_95_1d",
    "var_99_1d",
    "var_95_10d",
    "cvar_95_1d",
    "cvar_99_1d",
    # Portfolio risk
    "beta_to_benchmark",
    "tracking_error",
    # Greeks
    "delta",
    "gamma",
    "theta",
    "vega",
    "rho",
    # Scenarios
    "scenario_up_50bps",
    "scenario_down_50bps",
    "scenario_up_100bps",
    "scenario_down_100bps",
    "scenario_up_200bps",
    "scenario_credit_widen_100bps",
    # Volatility
    "implied_volatility",
    "historical_volatility_30d",
    "liquidity_score",
]

# Maps each join domain to its explicit gold column list.
DOMAIN_GOLD_COLUMNS: dict[str, list[str]] = {
    "security": SECURITY_GOLD_COLUMNS,
    "risk_analytics": RISK_GOLD_COLUMNS,
}


class GoldLayer:
    """Produces the denormalized enterprise positions dataset."""

    def __init__(self, spark: SparkSession, connector: WarehouseConnector, gold_path: str) -> None:
        self.spark = spark
        self.connector = connector
        self.gold_path = gold_path

    def build_enterprise_dataset(
        self,
        positions_repo: DomainRepository,
        domain_repos: dict[str, DomainRepository],
        join_configs: list[JoinConfig],
    ) -> DataFrame:
        """Join all silver domains into a single denormalized dataset.

        Positions is the base table; security and risk join via configured keys.
        Only current records (_is_current=True) are used.
        Each domain contributes only its explicitly declared columns.
        """
        logger.info("Building gold enterprise dataset")

        base = positions_repo.read_current()

        # Select only the explicitly declared positions columns (plus SCD2 meta for join)
        scd2_cols = ["_record_hash", "_effective_from", "_effective_to", "_is_current", "_batch_id"]
        pos_available = [c for c in POSITIONS_GOLD_COLUMNS if c in base.columns]
        pos_available += [c for c in scd2_cols if c in base.columns]
        base = base.select(*pos_available)

        for join_cfg in join_configs:
            domain = join_cfg.domain
            repo = domain_repos.get(domain)
            if repo is None:
                logger.warning("No repository found for join domain: %s — skipping", domain)
                continue

            domain_df = repo.read_current()

            # Determine join keys
            if isinstance(join_cfg.join_key, list):
                join_keys = join_cfg.join_key
            else:
                join_keys = [join_cfg.join_key]

            # Select only the explicitly declared columns for this domain (plus join keys)
            gold_cols = DOMAIN_GOLD_COLUMNS.get(domain, [])
            domain_select = list(join_keys)
            for col_name in gold_cols:
                if col_name not in domain_select and col_name in domain_df.columns:
                    domain_select.append(col_name)
            domain_df = domain_df.select(*[c for c in domain_select if c in domain_df.columns])

            # Prefix domain columns to avoid ambiguity (except join keys)
            skip_cols = set(join_keys)
            rename_map: dict[str, str] = {}
            for col_name in domain_df.columns:
                if col_name in skip_cols:
                    continue
                if col_name in base.columns:
                    new_name = f"{domain}_{col_name}"
                    rename_map[col_name] = new_name

            for old_name, new_name in rename_map.items():
                domain_df = domain_df.withColumnRenamed(old_name, new_name)

            base = base.join(domain_df, on=join_keys, how=join_cfg.join_type)
            logger.info("Joined domain=%s on keys=%s (%s)", domain, join_keys, join_cfg.join_type)

        # Drop SCD2 metadata from final output
        for scd_col in scd2_cols:
            if scd_col in base.columns:
                base = base.drop(scd_col)

        # Add pipeline metadata
        base = base.withColumn("_pipeline_timestamp", F.current_timestamp())

        output_path = f"{self.gold_path}/enterprise_positions"
        self.connector.write_table(output_path, base, mode="overwrite")

        logger.info("Gold enterprise dataset written: %d records, %d columns", base.count(), len(base.columns))
        return base
