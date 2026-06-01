#!/usr/bin/env python3
"""Generate realistic sample data for the enterprise pipeline.

Creates Parquet files simulating daily extracts from:
- accounting_system_alpha (~300 positions)
- accounting_system_beta (~200 positions, ~50 overlapping securities)
- security_master (~200 securities)
- risk_engine (~500 risk calculations)

Multiple business date snapshots with field value changes between snapshots.
"""

from __future__ import annotations

import random
import string
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Use pandas for data generation (simpler than PySpark for mock data)
try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    raise SystemExit("Install pandas and pyarrow: pip install pandas pyarrow")


random.seed(42)

OUTPUT_DIR = Path("data/raw")
BUSINESS_DATES = [date(2026, 5, 26), date(2026, 5, 27), date(2026, 5, 28)]
NUM_SECURITIES = 200
NUM_POSITIONS_ALPHA = 300
NUM_POSITIONS_BETA = 200
OVERLAP_SECURITIES = 50

# Realistic reference data
ISSUERS = [
    ("ISS001", "Apple Inc", "US"),
    ("ISS002", "Microsoft Corporation", "US"),
    ("ISS003", "JPMorgan Chase & Co", "US"),
    ("ISS004", "Goldman Sachs Group", "US"),
    ("ISS005", "United States Treasury", "US"),
    ("ISS006", "Federal National Mortgage Assn", "US"),
    ("ISS007", "European Investment Bank", "LU"),
    ("ISS008", "Deutsche Bank AG", "DE"),
    ("ISS009", "Barclays PLC", "GB"),
    ("ISS010", "Toyota Motor Corp", "JP"),
    ("ISS011", "BP PLC", "GB"),
    ("ISS012", "Nestle SA", "CH"),
    ("ISS013", "Samsung Electronics", "KR"),
    ("ISS014", "BHP Group Ltd", "AU"),
    ("ISS015", "Petrobras SA", "BR"),
]

SECURITY_TYPES = ["BOND", "NOTE", "BILL", "MBS", "ABS"]
ASSET_CLASSES = ["FIXED_INCOME"]
PRODUCT_TYPES = ["CORPORATE", "SOVEREIGN", "MUNI", "AGENCY", "MBS"]
COUPON_TYPES = ["FIXED", "FLOATING", "ZERO", "STEP_UP"]
COUPON_FREQS = ["ANNUAL", "SEMI", "QUARTERLY", "MONTHLY"]
RATINGS_SP = ["AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-", "BB+", "BB"]
RATINGS_MOODY = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3", "Ba1", "Ba2"]
SENIORITY = ["SENIOR_SECURED", "SENIOR_UNSECURED", "SUBORDINATED"]
REGIONS = ["NORTH_AMERICA", "EUROPE", "ASIA_PACIFIC", "LATIN_AMERICA"]
SECTORS = ["Financials", "Technology", "Energy", "Healthcare", "Industrials", "Consumer"]
DESKS = ["IG_CREDIT", "HY_CREDIT", "RATES", "EM_DEBT", "STRUCTURED"]
STRATEGIES = ["CARRY", "RELATIVE_VALUE", "DIRECTIONAL", "HEDGING"]
CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CHF"]


def _rand_id(prefix: str, n: int = 6) -> str:
    return f"{prefix}{''.join(random.choices(string.digits, k=n))}"


def _rand_cusip() -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=9))


def _rand_isin(country: str = "US") -> str:
    chars = string.ascii_uppercase + string.digits
    return f"{country}{''.join(random.choices(chars, k=10))}"


def generate_securities() -> pd.DataFrame:
    """Generate ~200 securities with realistic fixed-income attributes."""
    records = []
    for i in range(NUM_SECURITIES):
        issuer = random.choice(ISSUERS)
        sec_type = random.choice(SECURITY_TYPES)
        product = random.choice(PRODUCT_TYPES)
        cpn_type = random.choice(COUPON_TYPES)
        coupon = round(random.uniform(0.5, 12.0), 5) if cpn_type != "ZERO" else 0.0
        issue_dt = date(2020, 1, 1) + timedelta(days=random.randint(0, 1800))
        maturity_dt = issue_dt + timedelta(days=random.randint(365, 10950))
        is_callable = random.random() > 0.6
        is_puttable = random.random() > 0.8
        has_sinking_fund = random.random() > 0.85
        has_esg = issue_dt > date(2022, 1, 1)
        clean_px_base = round(random.uniform(85, 115), 6)

        records.append({
            "SEC_ID": f"SEC{i:06d}",
            "ISIN_CODE": _rand_isin(issuer[2]),
            "CUSIP_NUM": _rand_cusip(),
            "SEDOL_NUM": "".join(random.choices(string.ascii_uppercase + string.digits, k=7)),
            "TICKER": f"{''.join(random.choices(string.ascii_uppercase, k=4))} {coupon:.2f} {maturity_dt.strftime('%m/%y')}",
            "BBG_GLOBAL_ID": f"BBG{''.join(random.choices(string.ascii_uppercase + string.digits, k=9))}",
            "RIC_CODE": f"{''.join(random.choices(string.ascii_uppercase, k=4))}.{issuer[2][:2]}",
            "FIGI_CODE": f"BBG{''.join(random.choices(string.ascii_uppercase + string.digits, k=9))}",
            "SEC_NAME": f"{issuer[1]} {coupon:.3f}% {maturity_dt.year}",
            "SEC_SHORT_NAME": f"{issuer[1][:10]} {coupon:.1f} {maturity_dt.strftime('%y')}",
            "SEC_DESC": f"{product} {sec_type} issued by {issuer[1]}",
            "SEC_TYPE": sec_type,
            "ASSET_CLASS": random.choice(ASSET_CLASSES),
            "SUB_ASSET_CLASS": f"{'IG' if coupon < 6 else 'HY'}_{product}",
            "PRODUCT_TYPE": product,
            "ISSUER_ID": issuer[0],
            "ISSUER_NAME": issuer[1],
            "ISSUER_SHORT": issuer[1][:15],
            "ISSUER_LEI": f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=20))}",
            "ISSUER_COUNTRY": issuer[2],
            "ISSUER_DOMICILE": issuer[2],
            "ISSUER_SECTOR": random.choice(SECTORS),
            "CPN_RATE": coupon,
            "CPN_FREQ": random.choice(COUPON_FREQS),
            "CPN_TYPE": cpn_type,
            "CPN_CCY": random.choice(CURRENCIES),
            "DAY_COUNT": random.choice(["30/360", "ACT/360", "ACT/ACT"]),
            "ACCR_START_DT": issue_dt,
            "FIRST_CPN_DT": issue_dt + timedelta(days=180),
            "LAST_CPN_DT": maturity_dt - timedelta(days=180),
            "NEXT_CPN_DT": BUSINESS_DATES[0] + timedelta(days=random.randint(30, 180)),
            "MATURITY_DT": maturity_dt,
            "ISSUE_DT": issue_dt,
            "DATED_DT": issue_dt,
            "FIRST_SETTLE_DT": issue_dt + timedelta(days=2),
            "WORST_CALL_DT": (issue_dt + timedelta(days=random.randint(365, 3650))) if is_callable else None,
            "WORST_PUT_DT": (issue_dt + timedelta(days=random.randint(365, 3650))) if is_puttable else None,
            "NEXT_CALL_DT": (BUSINESS_DATES[0] + timedelta(days=random.randint(90, 730))) if is_callable else None,
            "NEXT_PUT_DT": (BUSINESS_DATES[0] + timedelta(days=random.randint(90, 730))) if is_puttable else None,
            "FIRST_CALL_DT": (issue_dt + timedelta(days=random.randint(365, 1825))) if is_callable else None,
            "FIRST_PUT_DT": (issue_dt + timedelta(days=random.randint(365, 1825))) if is_puttable else None,
            "CALL_PRICE": round(random.uniform(100, 105), 6) if is_callable else None,
            "PUT_PRICE": round(random.uniform(95, 100), 6) if is_puttable else None,
            "CALL_TYPE": random.choice(["AMERICAN", "EUROPEAN", "BERMUDA"]) if is_callable else None,
            "IS_CALLABLE": is_callable,
            "IS_PUTTABLE": is_puttable,
            "IS_CONVERTIBLE": random.random() > 0.9,
            "IS_PERPETUAL": random.random() > 0.95,
            "IS_144A": random.random() > 0.7,
            "IS_REG_S": random.random() > 0.7,
            "PAR_VALUE": 1000.0,
            "MIN_DENOM": random.choice([1000.0, 2000.0, 100000.0, 200000.0]),
            "MIN_INCR": random.choice([1000.0, 1.0]),
            "ISSUE_SIZE": round(random.uniform(100e6, 5e9), 2),
            "AMT_OUTSTANDING": round(random.uniform(50e6, 5e9), 2),
            "CCY": random.choice(CURRENCIES),
            "CTRY_RISK": issuer[2],
            "CTRY_DOMICILE": issuer[2],
            "CTRY_INCORP": issuer[2],
            "REGION": random.choice(REGIONS),
            "SECTOR": random.choice(SECTORS),
            "IND_GROUP": f"{random.choice(SECTORS)}_GROUP",
            "INDUSTRY": f"{random.choice(SECTORS)}_IND",
            "SUB_INDUSTRY": f"{random.choice(SECTORS)}_SUB",
            "RATING_SP": random.choice(RATINGS_SP),
            "RATING_MOODY": random.choice(RATINGS_MOODY),
            "RATING_FITCH": random.choice(RATINGS_SP),
            "RATING_COMPOSITE": random.choice(RATINGS_SP),
            "OUTLOOK_SP": random.choice(["STABLE", "POSITIVE", "NEGATIVE"]),
            "OUTLOOK_MOODY": random.choice(["STABLE", "POSITIVE", "NEGATIVE"]),
            "SENIORITY": random.choice(SENIORITY),
            "COLLATERAL_TYPE": random.choice(["UNSECURED", "FIRST_LIEN", "SECOND_LIEN", None]),
            "GUARANTEE_TYPE": random.choice(["NONE", "PARENT", "GOVERNMENT", None]),
            "PAYMENT_RANK": random.choice(["SENIOR", "SUBORDINATED", "JUNIOR"]),
            "BENCHMARK_IDX": random.choice(["UST", "SOFR", "EURIBOR"]),
            "SPREAD_BM": round(random.uniform(10, 500), 4),
            "FLOAT_IDX": "SOFR" if cpn_type == "FLOATING" else None,
            "FLOAT_SPREAD": round(random.uniform(50, 300), 4) if cpn_type == "FLOATING" else None,
            "FLOAT_RESET_FREQ": "QUARTERLY" if cpn_type == "FLOATING" else None,
            "EXCHANGE": random.choice(["NYSE", "LSE", "TSE", "OTC"]),
            "LISTING_STATUS": "LISTED",
            "TRADING_STATUS": "ACTIVE",
            "SETTLE_TYPE": random.choice(["T+1", "T+2"]),
            "TAX_STATUS": random.choice(["TAXABLE", "TAX_EXEMPT"]),
            "MAKE_WHOLE_CALL_PX": round(random.uniform(100, 110), 6) if is_callable else None,
            "PAR_CALL_DT": (maturity_dt - timedelta(days=random.randint(30, 365))) if is_callable else None,
            "FIRST_PAR_CALL_DT": (issue_dt + timedelta(days=random.randint(730, 3650))) if is_callable else None,
            "CALL_SCHEDULE": random.choice(["MAKE_WHOLE", "DISCRETE", "CONTINUOUS"]) if is_callable else None,
            "SINK_FUND_FLAG": has_sinking_fund,
            "SINK_FUND_AMT": round(random.uniform(1e6, 50e6), 2) if has_sinking_fund else None,
            "PIK_FLAG": random.random() > 0.92,
            "ESG_SCORE": round(random.uniform(20, 95), 2) if has_esg else None,
            "ENVIRONMENTAL_SCORE": round(random.uniform(15, 90), 2) if has_esg else None,
            "SOCIAL_SCORE": round(random.uniform(20, 90), 2) if has_esg else None,
            "GOVERNANCE_SCORE": round(random.uniform(25, 95), 2) if has_esg else None,
            "CARBON_INTENSITY": round(random.uniform(10, 800), 2) if has_esg else None,
            "ESG_CONTROVERSY_FLAG": random.random() > 0.85 if has_esg else None,
            "PX_OPEN": round(clean_px_base * random.uniform(0.995, 1.005), 6),
            "PX_HIGH": round(clean_px_base * random.uniform(1.001, 1.015), 6),
            "PX_LOW": round(clean_px_base * random.uniform(0.985, 0.999), 6),
            "VWAP": round(clean_px_base * random.uniform(0.998, 1.002), 6),
            "HIGH_52W": round(clean_px_base * random.uniform(1.02, 1.15), 6),
            "LOW_52W": round(clean_px_base * random.uniform(0.85, 0.98), 6),
            "AVG_VOL_30D": random.randint(50000, 50000000),
            "EX_DVD_DT": None,
            "DVD_RECORD_DT": None,
            "DVD_PAY_DT": None,
            "DVD_AMT": None,
            "SPLIT_FACTOR": None,
            "LAST_SPLIT_DT": None,
            "LEI": "".join(random.choices(string.ascii_uppercase + string.digits, k=20)),
            "CINS": "".join(random.choices(string.ascii_uppercase + string.digits, k=9)) if issuer[2] != "US" else None,
            "VALOR": "".join(random.choices(string.digits, k=7)) if issuer[2] == "CH" else None,
            "WKN": "".join(random.choices(string.ascii_uppercase + string.digits, k=6)) if issuer[2] == "DE" else None,
            "COMMON_CODE": "".join(random.choices(string.digits, k=9)) if random.random() > 0.5 else None,
            "PE_RATIO": None,
            "EPS": None,
            "BOOK_VAL_PER_SH": None,
            "REV_PER_SH": None,
            "DEBT_TO_EQUITY": None,
            "ROE": None,
            "EBITDA_MARGIN": None,
            "COVENANT_TYPE": random.choice(["LITE", "STANDARD", "TIGHT"]) if product == "CORPORATE" else None,
            "RECOVERY_RATE": round(random.uniform(0.25, 0.80), 4) if product == "CORPORATE" else None,
            "LOSS_GIVEN_DEFAULT": round(1.0 - random.uniform(0.25, 0.80), 4) if product == "CORPORATE" else None,
            "WORKOUT_DT": (maturity_dt - timedelta(days=random.randint(60, 730))) if random.random() > 0.9 else None,
            "PRIVATE_PLACEMENT": random.random() > 0.8,
            "GREEN_BOND_FLAG": random.random() > 0.85,
            "SUKUK_FLAG": random.random() > 0.95,
            "CREATED_TS": datetime.now(),
        })
    return pd.DataFrame(records)


def generate_positions_alpha(security_ids: list[str], biz_date: date, date_idx: int) -> pd.DataFrame:
    """Generate positions for accounting system alpha."""
    records = []
    for i in range(NUM_POSITIONS_ALPHA):
        sec_id = random.choice(security_ids)
        desk = random.choice(DESKS)
        mv_base = round(random.uniform(-5e6, 50e6), 2)
        # Add small variations across dates
        jitter = 1 + random.uniform(-0.02, 0.02) * date_idx

        records.append({
            "POS_ID": f"POS_A{i:06d}",
            "BOOK_CODE": f"BOOK_{desk}_{random.randint(1, 5)}",
            "BUS_DATE": biz_date,
            "ACCT_ID": f"ACCT_A{random.randint(1, 20):03d}",
            "ACCT_NAME": f"Alpha Account {random.randint(1, 20)}",
            "ACCT_TYPE": random.choice(["TRADING", "BANKING", "CUSTODY"]),
            "LE_ID": f"LE_{random.randint(1, 5):03d}",
            "LE_NAME": f"Entity {random.randint(1, 5)}",
            "CUST_ID": f"CUST_{random.randint(1, 3):03d}",
            "CUST_NAME": f"Custodian {random.randint(1, 3)}",
            "PB_ID": f"PB_{random.randint(1, 2):03d}",
            "PB_NAME": f"Prime Broker {random.randint(1, 2)}",
            "SEC_ID": sec_id,
            "QTY": round(random.uniform(100, 1e6) * jitter, 4),
            "NOTIONAL": round(random.uniform(1e5, 1e8) * jitter, 2),
            "MV_LOCAL": round(mv_base * jitter, 2),
            "MV_BASE": round(mv_base * jitter, 2),
            "COST_BASIS": round(mv_base * 0.95, 2),
            "ACCR_INT": round(random.uniform(0, 50000), 2),
            "UNREAL_PNL": round(mv_base * 0.05 * jitter, 2),
            "REAL_PNL": round(random.uniform(-100000, 200000) * jitter, 2),
            "TOTAL_PNL": round(mv_base * 0.05 * jitter + random.uniform(-100000, 200000), 2),
            "DAILY_PNL": round(random.uniform(-50000, 50000) * jitter, 2),
            "MTD_PNL": round(random.uniform(-200000, 200000) * jitter, 2),
            "YTD_PNL": round(random.uniform(-500000, 500000) * jitter, 2),
            "TRD_DATE": biz_date - timedelta(days=random.randint(1, 365)),
            "SETTLE_DATE": biz_date - timedelta(days=random.randint(0, 3)),
            "EFF_DATE": biz_date,
            "LS_IND": random.choice(["LONG", "SHORT"]),
            "POS_TYPE": random.choice(["OUTRIGHT", "HEDGE", "COLLATERAL"]),
            "POS_STATUS": "OPEN",
            "CCY": random.choice(CURRENCIES),
            "BASE_CCY": "USD",
            "FX_RATE": round(random.uniform(0.7, 1.5), 6),
            "DESK_NAME": desk,
            "DESK_ID": f"DSK_{desk}",
            "STRAT_NAME": random.choice(STRATEGIES),
            "STRAT_ID": f"STR_{random.randint(1, 10):03d}",
            "PORT_ID": f"PORT_{random.randint(1, 10):03d}",
            "PORT_NAME": f"Portfolio {random.randint(1, 10)}",
            "FUND_ID": f"FUND_{random.randint(1, 5):03d}",
            "FUND_NAME": f"Fund {random.randint(1, 5)}",
            "TRADER_ID": f"TRD_{random.randint(1, 15):03d}",
            "TRADER_NAME": f"Trader {random.randint(1, 15)}",
            "CP_ID": f"CP_{random.randint(1, 20):03d}",
            "CP_NAME": f"Counterparty {random.randint(1, 20)}",
            "CP_LEI": f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=20))}",
            "LOT_ID": f"LOT_A{i:06d}",
            "LOT_DATE": biz_date - timedelta(days=random.randint(30, 365)),
            "LOT_COST": round(mv_base * 0.93, 2),
            "PORT_WEIGHT": round(random.uniform(0.01, 5.0), 4),
            "FUND_WEIGHT": round(random.uniform(0.01, 3.0), 4),
            "MARGIN_REQ": round(random.uniform(0, 1e6), 2),
            "COLLATERAL_VAL": round(random.uniform(0, 5e6), 2),
            "HAIRCUT": round(random.uniform(0, 0.15), 4),
            "FIN_RATE": round(random.uniform(0.01, 0.08), 6),
            "FIN_COST": round(random.uniform(0, 50000), 2),
            "RECORD_ID": f"REC_A{i:06d}_{biz_date.strftime('%Y%m%d')}",
            "LOAD_TS": datetime.now(),
            "IS_ACTIVE": True,
            "REG_BOOK": random.choice(["TRADING", "BANKING"]),
            "ACCT_TREATMENT": random.choice(["HFT", "AFS", "HTM"]),
            "MIFID_CLASS": random.choice(["COMPLEX", "NON_COMPLEX", None]),
            "CFTC_REPORTABLE": random.random() > 0.8,
            "REPORTING_JURIS": random.choice(["US", "EU", "UK", "APAC"]),
            "LARGE_POS_FLAG": random.random() > 0.9,
            "CONCENTRATION_FLAG": random.random() > 0.92,
            "RESTRICTED_FLAG": random.random() > 0.95,
            "COMPLIANCE_STATUS": random.choice(["COMPLIANT", "PENDING_REVIEW", "EXCEPTION"]),
            "SETTLE_CCY": random.choice(CURRENCIES),
            "SETTLE_FX_RATE": round(random.uniform(0.7, 1.5), 6),
            "FAILED_SETTLE_FLAG": random.random() > 0.97,
            "SETTLE_INSTRUCTION": random.choice(["DVP", "FOP", "DWP"]),
            "SETTLE_LOCATION": random.choice(["DTC", "EUROCLEAR", "CLEARSTREAM", "FEDWIRE"]),
            "SECTOR_ALLOC_PCT": round(random.uniform(0.01, 15.0), 4),
            "COUNTRY_ALLOC_PCT": round(random.uniform(0.01, 20.0), 4),
            "DUR_CONTRIBUTION": round(random.uniform(0.001, 0.5), 6),
            "SPREAD_CONTRIBUTION": round(random.uniform(0.001, 0.3), 6),
            "RETURN_CONTRIB_1D": round(random.uniform(-0.05, 0.05), 6),
            "RETURN_CONTRIB_MTD": round(random.uniform(-0.5, 0.5), 6),
            "RETURN_CONTRIB_YTD": round(random.uniform(-2.0, 2.0), 6),
            "CONFIRM_STATUS": random.choice(["CONFIRMED", "UNCONFIRMED", "PENDING"]),
            "MATCHING_STATUS": random.choice(["MATCHED", "UNMATCHED", "ALLEGED"]),
            "BREAK_FLAG": random.random() > 0.95,
            "RECON_STATUS": random.choice(["RECONCILED", "PENDING", "BREAK"]),
            "LAST_RECON_DT": biz_date - timedelta(days=random.randint(0, 5)),
            "AGING_DAYS": random.randint(0, 365),
        })
    return pd.DataFrame(records)


def generate_positions_beta(security_ids: list[str], biz_date: date, date_idx: int) -> pd.DataFrame:
    """Generate positions for accounting system beta (different column names)."""
    records = []
    for i in range(NUM_POSITIONS_BETA):
        sec_id = random.choice(security_ids)
        desk = random.choice(DESKS)
        mv_base = round(random.uniform(-3e6, 30e6), 2)
        jitter = 1 + random.uniform(-0.02, 0.02) * date_idx

        records.append({
            "POSITION_KEY": f"POS_B{i:06d}",
            "BOOK_ID": f"BOOK_{desk}_{random.randint(1, 5)}",
            "AS_OF_DT": biz_date,
            "ACCOUNT_NUM": f"ACCT_B{random.randint(1, 15):03d}",
            "ACCOUNT_DESC": f"Beta Account {random.randint(1, 15)}",
            "ACCT_CLASSIFICATION": random.choice(["TRADING", "BANKING", "CUSTODY"]),
            "LEGAL_ENTITY": f"LE_{random.randint(1, 5):03d}",
            "LE_DESC": f"Entity {random.randint(1, 5)}",
            "CUSTODIAN_CODE": f"CUST_{random.randint(1, 3):03d}",
            "CUSTODIAN_DESC": f"Custodian {random.randint(1, 3)}",
            "PRIME_BROKER": f"PB_{random.randint(1, 2):03d}",
            "PB_DESC": f"Prime Broker {random.randint(1, 2)}",
            "SECURITY_KEY": sec_id,
            "UNITS_HELD": round(random.uniform(100, 5e5) * jitter, 4),
            "FACE_VALUE": round(random.uniform(1e5, 5e7) * jitter, 2),
            "MKT_VAL_LC": round(mv_base * jitter, 2),
            "MKT_VAL_USD": round(mv_base * jitter, 2),
            "ORIG_COST": round(mv_base * 0.96, 2),
            "ACCRUED": round(random.uniform(0, 30000), 2),
            "UNREALIZED_GL": round(mv_base * 0.04 * jitter, 2),
            "REALIZED_GL": round(random.uniform(-80000, 150000) * jitter, 2),
            "TOTAL_GL": round(mv_base * 0.04 * jitter + random.uniform(-80000, 150000), 2),
            "DAY_PNL": round(random.uniform(-30000, 30000) * jitter, 2),
            "MTD_GL": round(random.uniform(-150000, 150000) * jitter, 2),
            "YTD_GL": round(random.uniform(-400000, 400000) * jitter, 2),
            "TRADE_DT": biz_date - timedelta(days=random.randint(1, 365)),
            "SETTLEMENT_DT": biz_date - timedelta(days=random.randint(0, 3)),
            "EFFECTIVE_DT": biz_date,
            "LONG_SHORT": random.choice(["LONG", "SHORT"]),
            "POSITION_CLASS": random.choice(["OUTRIGHT", "HEDGE", "COLLATERAL"]),
            "STATUS": "OPEN",
            "LOCAL_CCY": random.choice(CURRENCIES),
            "RPT_CCY": "USD",
            "FX_RATE_USD": round(random.uniform(0.7, 1.5), 6),
            "TRADING_DESK": desk,
            "DESK_CODE": f"DSK_{desk}",
            "STRATEGY_DESC": random.choice(STRATEGIES),
            "STRATEGY_CODE": f"STR_{random.randint(1, 10):03d}",
            "PORTFOLIO_KEY": f"PORT_{random.randint(1, 10):03d}",
            "PORTFOLIO_DESC": f"Portfolio {random.randint(1, 10)}",
            "FUND_KEY": f"FUND_{random.randint(1, 5):03d}",
            "FUND_DESC": f"Fund {random.randint(1, 5)}",
            "TRADER_CODE": f"TRD_{random.randint(1, 15):03d}",
            "TRADER_DESC": f"Trader {random.randint(1, 15)}",
            "CPTY_KEY": f"CP_{random.randint(1, 20):03d}",
            "CPTY_DESC": f"Counterparty {random.randint(1, 20)}",
            "CPTY_LEI": f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=20))}",
            "TAX_LOT_KEY": f"LOT_B{i:06d}",
            "TAX_LOT_DT": biz_date - timedelta(days=random.randint(30, 365)),
            "TAX_LOT_COST": round(mv_base * 0.94, 2),
            "PORTFOLIO_PCT": round(random.uniform(0.01, 4.0), 4),
            "FUND_PCT": round(random.uniform(0.01, 2.5), 4),
            "MARGIN_AMT": round(random.uniform(0, 8e5), 2),
            "COLL_VALUE": round(random.uniform(0, 3e6), 2),
            "HAIRCUT_PCT": round(random.uniform(0, 0.12), 4),
            "FINANCING_RT": round(random.uniform(0.01, 0.07), 6),
            "FINANCING_AMT": round(random.uniform(0, 40000), 2),
            "SRC_REC_ID": f"REC_B{i:06d}_{biz_date.strftime('%Y%m%d')}",
            "LOAD_TIMESTAMP": datetime.now(),
            "ACTIVE_FLAG": True,
            "REG_CLASSIFICATION": random.choice(["TRADING", "BANKING"]),
            "ACCT_METHOD": random.choice(["HFT", "AFS", "HTM"]),
            "MIFID_CLASSIFICATION": random.choice(["COMPLEX", "NON_COMPLEX", None]),
            "CFTC_REPORT_FLAG": random.random() > 0.8,
            "RPT_JURISDICTION": random.choice(["US", "EU", "UK", "APAC"]),
            "LG_POSITION_FLAG": random.random() > 0.9,
            "CONC_LIMIT_FLAG": random.random() > 0.92,
            "RESTRICTED_SEC_FLAG": random.random() > 0.95,
            "COMPL_STATUS": random.choice(["COMPLIANT", "PENDING_REVIEW", "EXCEPTION"]),
            "SETTLEMENT_CCY": random.choice(CURRENCIES),
            "SETTLEMENT_FX": round(random.uniform(0.7, 1.5), 6),
            "FAILED_SETTLE": random.random() > 0.97,
            "SETTLE_INSTR_TYPE": random.choice(["DVP", "FOP", "DWP"]),
            "SETTLE_DEPOT": random.choice(["DTC", "EUROCLEAR", "CLEARSTREAM", "FEDWIRE"]),
            "SECTOR_ALLOC": round(random.uniform(0.01, 15.0), 4),
            "COUNTRY_ALLOC": round(random.uniform(0.01, 20.0), 4),
            "DUR_CONTRIB": round(random.uniform(0.001, 0.5), 6),
            "SPREAD_CONTRIB": round(random.uniform(0.001, 0.3), 6),
            "RET_CONTRIB_1D": round(random.uniform(-0.05, 0.05), 6),
            "RET_CONTRIB_MTD": round(random.uniform(-0.5, 0.5), 6),
            "RET_CONTRIB_YTD": round(random.uniform(-2.0, 2.0), 6),
            "CONFIRMATION_STATUS": random.choice(["CONFIRMED", "UNCONFIRMED", "PENDING"]),
            "MATCH_STATUS": random.choice(["MATCHED", "UNMATCHED", "ALLEGED"]),
            "POSITION_BREAK": random.random() > 0.95,
            "RECONCILIATION_STATUS": random.choice(["RECONCILED", "PENDING", "BREAK"]),
            "LAST_RECON_DATE": biz_date - timedelta(days=random.randint(0, 5)),
            "DAYS_SINCE_TRADE": random.randint(0, 365),
        })
    return pd.DataFrame(records)


def generate_risk_analytics(security_ids: list[str], position_ids: list[str], biz_date: date, date_idx: int) -> pd.DataFrame:
    """Generate risk analytics data."""
    records = []
    num_calcs = min(len(position_ids), 500)
    for i in range(num_calcs):
        sec_id = random.choice(security_ids)
        pos_id = position_ids[i % len(position_ids)]
        jitter = 1 + random.uniform(-0.01, 0.01) * date_idx
        clean_px = round(random.uniform(85, 115), 6)
        is_option = random.random() > 0.8

        records.append({
            "CALC_ID": f"CALC{i:06d}_{biz_date.strftime('%Y%m%d')}",
            "SEC_ID": sec_id,
            "POS_ID": pos_id,
            "CALC_DATE": biz_date,
            "CALC_TS": datetime.now(),
            "CLEAN_PX": clean_px * jitter,
            "DIRTY_PX": (clean_px + random.uniform(0, 3)) * jitter,
            "MID_PX": clean_px * jitter,
            "BID_PX": (clean_px - random.uniform(0.1, 0.5)) * jitter,
            "ASK_PX": (clean_px + random.uniform(0.1, 0.5)) * jitter,
            "PX_SOURCE": random.choice(["BLOOMBERG", "ICE", "INTERNAL"]),
            "YTM": round(random.uniform(1, 12) * jitter, 5),
            "YTW": round(random.uniform(0.5, 11) * jitter, 5),
            "YTC": round(random.uniform(0.5, 10) * jitter, 5),
            "CUR_YIELD": round(random.uniform(1, 10) * jitter, 5),
            "SPREAD_GOVT": round(random.uniform(10, 500) * jitter, 4),
            "DUR_MAC": round(random.uniform(0.5, 15) * jitter, 6),
            "DUR_MOD": round(random.uniform(0.5, 14) * jitter, 6),
            "DUR_EFF": round(random.uniform(0.5, 14) * jitter, 6),
            "DUR_SPREAD": round(random.uniform(0.5, 14) * jitter, 6),
            "KRD_2Y": round(random.uniform(0, 3) * jitter, 6),
            "KRD_5Y": round(random.uniform(0, 5) * jitter, 6),
            "KRD_10Y": round(random.uniform(0, 7) * jitter, 6),
            "KRD_30Y": round(random.uniform(0, 4) * jitter, 6),
            "CONVEXITY": round(random.uniform(0, 200) * jitter, 6),
            "EFF_CONVEXITY": round(random.uniform(0, 200) * jitter, 6),
            "DV01": round(random.uniform(100, 50000) * jitter, 2),
            "CR01": round(random.uniform(50, 30000) * jitter, 2),
            "CS01": round(random.uniform(50, 30000) * jitter, 2),
            "OAS": round(random.uniform(10, 500) * jitter, 4),
            "Z_SPREAD": round(random.uniform(10, 500) * jitter, 4),
            "I_SPREAD": round(random.uniform(10, 400) * jitter, 4),
            "G_SPREAD": round(random.uniform(10, 500) * jitter, 4),
            "ASW_SPREAD": round(random.uniform(10, 400) * jitter, 4),
            "VAR_95_1D": round(random.uniform(1000, 500000) * jitter, 2),
            "VAR_99_1D": round(random.uniform(2000, 700000) * jitter, 2),
            "VAR_95_10D": round(random.uniform(3000, 1500000) * jitter, 2),
            "CVAR_95_1D": round(random.uniform(1500, 600000) * jitter, 2),
            "CVAR_99_1D": round(random.uniform(3000, 900000) * jitter, 2),
            "BETA": round(random.uniform(0.5, 1.5) * jitter, 4),
            "TRACK_ERR": round(random.uniform(0.5, 5) * jitter, 4),
            "DELTA": round(random.uniform(-1, 1), 6),
            "GAMMA": round(random.uniform(0, 0.1), 6),
            "THETA": round(random.uniform(-1000, 0), 6),
            "VEGA": round(random.uniform(0, 5000), 6),
            "RHO": round(random.uniform(-500, 500), 6),
            "SCEN_UP_50": round(random.uniform(-500000, -10000) * jitter, 2),
            "SCEN_DN_50": round(random.uniform(10000, 500000) * jitter, 2),
            "SCEN_UP_100": round(random.uniform(-1000000, -20000) * jitter, 2),
            "SCEN_DN_100": round(random.uniform(20000, 1000000) * jitter, 2),
            "SCEN_UP_200": round(random.uniform(-2000000, -40000) * jitter, 2),
            "SCEN_CRD_100": round(random.uniform(-800000, -5000) * jitter, 2),
            "IMPL_VOL": round(random.uniform(5, 50) * jitter, 4),
            "HIST_VOL_30D": round(random.uniform(3, 40) * jitter, 4),
            "LIQ_SCORE": round(random.uniform(20, 95), 2),
            "SCEN_DN_200": round(random.uniform(40000, 2000000) * jitter, 2),
            "SCEN_UP_300": round(random.uniform(-3000000, -60000) * jitter, 2),
            "SCEN_EQ_DN_10": round(random.uniform(-200000, 200000) * jitter, 2),
            "SCEN_EQ_DN_20": round(random.uniform(-400000, 400000) * jitter, 2),
            "SCEN_FX_SHOCK_10": round(random.uniform(-300000, 300000) * jitter, 2),
            "SCEN_CREDIT_TIGHT_50": round(random.uniform(-500000, -5000) * jitter, 2),
            "SCEN_VOL_UP_25": round(random.uniform(-200000, 200000) * jitter, 2),
            "SYSTEMATIC_RISK": round(random.uniform(1000, 300000) * jitter, 2),
            "IDIOSYNCRATIC_RISK": round(random.uniform(500, 150000) * jitter, 2),
            "CREDIT_RISK_CONTRIB": round(random.uniform(200, 100000) * jitter, 2),
            "RATE_RISK_CONTRIB": round(random.uniform(200, 100000) * jitter, 2),
            "FX_RISK_CONTRIB": round(random.uniform(100, 50000) * jitter, 2),
            "EQUITY_RISK_CONTRIB": round(random.uniform(0, 30000) * jitter, 2),
            "BID_ASK_SPREAD": round(random.uniform(0.5, 50), 4),
            "AVG_DAILY_VOL": random.randint(10000, 10000000),
            "DAYS_TO_LIQUIDATE": round(random.uniform(0.5, 30), 2),
            "TURNOVER_RATIO": round(random.uniform(0.01, 2.0), 4),
            "CHARM": round(random.uniform(-0.01, 0.01), 6) if is_option else None,
            "VANNA": round(random.uniform(-0.05, 0.05), 6) if is_option else None,
            "VOLGA": round(random.uniform(-0.1, 0.1), 6) if is_option else None,
            "SPEED": round(random.uniform(-0.001, 0.001), 6) if is_option else None,
            "COLOR": round(random.uniform(-0.001, 0.001), 6) if is_option else None,
            "STRESS_VAR_95": round(random.uniform(3000, 1000000) * jitter, 2),
            "INCR_VAR_95": round(random.uniform(500, 200000) * jitter, 2),
            "MARGINAL_VAR_95": round(random.uniform(100, 100000) * jitter, 2),
        })
    return pd.DataFrame(records)


def main() -> None:
    print("Generating sample data...")

    # Create output directories
    for subdir in ["accounting_system_alpha", "accounting_system_beta", "security_master", "risk_engine"]:
        (OUTPUT_DIR / subdir).mkdir(parents=True, exist_ok=True)

    # Generate securities (same for all dates)
    sec_df = generate_securities()
    security_ids = sec_df["SEC_ID"].tolist()

    # Shared securities between alpha and beta
    shared_sec_ids = security_ids[:OVERLAP_SECURITIES]
    alpha_sec_ids = security_ids[:150]
    beta_sec_ids = shared_sec_ids + security_ids[150:]

    for idx, biz_date in enumerate(BUSINESS_DATES):
        date_str = biz_date.strftime("%Y%m%d")
        print(f"  Generating data for {biz_date}...")

        # Securities
        pq.write_table(
            pa.Table.from_pandas(sec_df),
            OUTPUT_DIR / "security_master" / f"securities_{date_str}.parquet",
        )

        # Positions alpha
        alpha_df = generate_positions_alpha(alpha_sec_ids, biz_date, idx)
        pq.write_table(
            pa.Table.from_pandas(alpha_df),
            OUTPUT_DIR / "accounting_system_alpha" / f"positions_{date_str}.parquet",
        )

        # Positions beta
        beta_df = generate_positions_beta(beta_sec_ids, biz_date, idx)
        pq.write_table(
            pa.Table.from_pandas(beta_df),
            OUTPUT_DIR / "accounting_system_beta" / f"positions_{date_str}.parquet",
        )

        # Risk analytics
        all_pos_ids = alpha_df["POS_ID"].tolist() + beta_df["POSITION_KEY"].tolist()
        risk_df = generate_risk_analytics(security_ids, all_pos_ids, biz_date, idx)
        pq.write_table(
            pa.Table.from_pandas(risk_df),
            OUTPUT_DIR / "risk_engine" / f"risk_analytics_{date_str}.parquet",
        )

    print(f"Sample data generated in {OUTPUT_DIR}/")
    print(f"  Securities: {NUM_SECURITIES}")
    print(f"  Positions (alpha): {NUM_POSITIONS_ALPHA} per date")
    print(f"  Positions (beta): {NUM_POSITIONS_BETA} per date")
    print(f"  Overlapping securities: {OVERLAP_SECURITIES}")
    print(f"  Risk calculations: ~500 per date")
    print(f"  Business dates: {[d.isoformat() for d in BUSINESS_DATES]}")


if __name__ == "__main__":
    main()
