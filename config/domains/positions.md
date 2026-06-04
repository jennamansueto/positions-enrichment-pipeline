# Positions Domain

## Source Configuration
- **Source Systems**: accounting_system_alpha, accounting_system_beta
- **Source Tables**: alpha.positions, beta.pos_holdings
- **Primary Key**: position_id, book_id, as_of_date
- **Load Strategy**: INCREMENTAL

## Field Mappings

### Key Fields
| Target Field | Source Field (Alpha) | Source Field (Beta) | Type | Status | Description |
|---|---|---|---|---|---|
| position_id | POS_ID | POSITION_KEY | STRING | ACTIVE | Unique position identifier |
| book_id | BOOK_CODE | BOOK_ID | STRING | ACTIVE | Trading book identifier |
| as_of_date | BUS_DATE | AS_OF_DT | DATE | ACTIVE | Business date of the position snapshot |
| account_id | ACCT_ID | ACCOUNT_NUM | STRING | ACTIVE | Account identifier |
| account_name | ACCT_NAME | ACCOUNT_DESC | STRING | ACTIVE | Account display name |
| account_type | ACCT_TYPE | ACCT_CLASSIFICATION | STRING | ACTIVE | Account classification (TRADING, BANKING, CUSTODY) |
| legal_entity_id | LE_ID | LEGAL_ENTITY | STRING | ACTIVE | Legal entity owning the account |
| legal_entity_name | LE_NAME | LE_DESC | STRING | ACTIVE | Legal entity display name |
| custodian_id | CUST_ID | CUSTODIAN_CODE | STRING | ACTIVE | Custodian institution identifier |
| custodian_name | CUST_NAME | CUSTODIAN_DESC | STRING | ACTIVE | Custodian institution name |
| prime_broker_id | PB_ID | PRIME_BROKER | STRING | ACTIVE | Prime broker identifier |
| prime_broker_name | PB_NAME | PB_DESC | STRING | ACTIVE | Prime broker name |
| security_id | SEC_ID | SECURITY_KEY | STRING | ACTIVE | Foreign key to security domain |

### Position Values
| Target Field | Source Field (Alpha) | Source Field (Beta) | Type | Status | Description |
|---|---|---|---|---|---|
| quantity | QTY | UNITS_HELD | DECIMAL(18,4) | ACTIVE | Number of units/shares held |
| notional_amount | NOTIONAL | FACE_VALUE | DECIMAL(18,2) | ACTIVE | Face/notional value |
| market_value_local | MV_LOCAL | MKT_VAL_LC | DECIMAL(18,2) | ACTIVE | Market value in local currency |
| market_value_base | MV_BASE | MKT_VAL_USD | DECIMAL(18,2) | ACTIVE | Market value in base currency (USD) |
| cost_basis | COST_BASIS | ORIG_COST | DECIMAL(18,2) | ACTIVE | Original cost basis |
| accrued_interest | ACCR_INT | ACCRUED | DECIMAL(18,2) | ACTIVE | Accrued interest (fixed income) |
| unrealized_pnl | UNREAL_PNL | UNREALIZED_GL | DECIMAL(18,2) | ACTIVE | Unrealized profit/loss |
| realized_pnl | REAL_PNL | REALIZED_GL | DECIMAL(18,2) | ACTIVE | Realized profit/loss |
| total_pnl | TOTAL_PNL | TOTAL_GL | DECIMAL(18,2) | ACTIVE | Total P&L (realized + unrealized) |
| daily_pnl | DAILY_PNL | DAY_PNL | DECIMAL(18,2) | ACTIVE | Daily P&L change |
| mtd_pnl | MTD_PNL | MTD_GL | DECIMAL(18,2) | ACTIVE | Month-to-date P&L |
| ytd_pnl | YTD_PNL | YTD_GL | DECIMAL(18,2) | ACTIVE | Year-to-date P&L |

### Dates
| Target Field | Source Field (Alpha) | Source Field (Beta) | Type | Status | Description |
|---|---|---|---|---|---|
| trade_date | TRD_DATE | TRADE_DT | DATE | ACTIVE | Original trade date |
| settle_date | SETTLE_DATE | SETTLEMENT_DT | DATE | ACTIVE | Settlement date |
| effective_date | EFF_DATE | EFFECTIVE_DT | DATE | ACTIVE | Position effective date |

### Classification
| Target Field | Source Field (Alpha) | Source Field (Beta) | Type | Status | Description |
|---|---|---|---|---|---|
| long_short_indicator | LS_IND | LONG_SHORT | STRING | ACTIVE | LONG or SHORT |
| position_type | POS_TYPE | POSITION_CLASS | STRING | ACTIVE | OUTRIGHT, HEDGE, COLLATERAL |
| position_status | POS_STATUS | STATUS | STRING | ACTIVE | OPEN, CLOSED, PENDING |

### Currency & FX
| Target Field | Source Field (Alpha) | Source Field (Beta) | Type | Status | Description |
|---|---|---|---|---|---|
| currency | CCY | LOCAL_CCY | STRING | ACTIVE | Local currency (ISO 4217) |
| base_currency | BASE_CCY | RPT_CCY | STRING | ACTIVE | Base reporting currency |
| fx_rate_to_base | FX_RATE | FX_RATE_USD | DECIMAL(12,6) | ACTIVE | FX rate to base currency |

### Organizational
| Target Field | Source Field (Alpha) | Source Field (Beta) | Type | Status | Description |
|---|---|---|---|---|---|
| desk | DESK_NAME | TRADING_DESK | STRING | ACTIVE | Trading desk name |
| desk_id | DESK_ID | DESK_CODE | STRING | ACTIVE | Trading desk identifier |
| strategy | STRAT_NAME | STRATEGY_DESC | STRING | ACTIVE | Investment strategy |
| strategy_id | STRAT_ID | STRATEGY_CODE | STRING | ACTIVE | Strategy identifier |
| portfolio_id | PORT_ID | PORTFOLIO_KEY | STRING | ACTIVE | Portfolio identifier |
| portfolio_name | PORT_NAME | PORTFOLIO_DESC | STRING | ACTIVE | Portfolio display name |
| fund_id | FUND_ID | FUND_KEY | STRING | ACTIVE | Fund identifier |
| fund_name | FUND_NAME | FUND_DESC | STRING | ACTIVE | Fund name |
| trader_id | TRADER_ID | TRADER_CODE | STRING | ACTIVE | Trader identifier |
| trader_name | TRADER_NAME | TRADER_DESC | STRING | ACTIVE | Trader name |
| counterparty_id | CP_ID | CPTY_KEY | STRING | ACTIVE | Counterparty identifier |
| counterparty_name | CP_NAME | CPTY_DESC | STRING | ACTIVE | Counterparty name |
| counterparty_lei | CP_LEI | CPTY_LEI | STRING | ACTIVE | Counterparty LEI code |

### Tax Lots
| Target Field | Source Field (Alpha) | Source Field (Beta) | Type | Status | Description |
|---|---|---|---|---|---|
| lot_id | LOT_ID | TAX_LOT_KEY | STRING | ACTIVE | Tax lot identifier |
| lot_date | LOT_DATE | TAX_LOT_DT | DATE | ACTIVE | Tax lot date |
| lot_cost | LOT_COST | TAX_LOT_COST | DECIMAL(18,2) | ACTIVE | Tax lot cost basis |

### Portfolio Weights
| Target Field | Source Field (Alpha) | Source Field (Beta) | Type | Status | Description |
|---|---|---|---|---|---|
| weight_in_portfolio | PORT_WEIGHT | PORTFOLIO_PCT | DECIMAL(8,4) | ACTIVE | Position weight in portfolio (%) |
| weight_in_fund | FUND_WEIGHT | FUND_PCT | DECIMAL(8,4) | ACTIVE | Position weight in fund (%) |

### Margin & Collateral
| Target Field | Source Field (Alpha) | Source Field (Beta) | Type | Status | Description |
|---|---|---|---|---|---|
| margin_requirement | MARGIN_REQ | MARGIN_AMT | DECIMAL(18,2) | ACTIVE | Margin requirement |
| collateral_value | COLLATERAL_VAL | COLL_VALUE | DECIMAL(18,2) | ACTIVE | Collateral value |
| haircut_pct | HAIRCUT | HAIRCUT_PCT | DECIMAL(8,4) | ACTIVE | Collateral haircut percentage |
| financing_rate | FIN_RATE | FINANCING_RT | DECIMAL(8,6) | ACTIVE | Financing/repo rate |
| financing_cost | FIN_COST | FINANCING_AMT | DECIMAL(18,2) | ACTIVE | Financing cost |

### Return Contributions
| Target Field | Source Field (Alpha) | Source Field (Beta) | Type | Status | Description |
|---|---|---|---|---|---|
| return_contribution_1d | RETURN_CONTRIB_1D | RET_CONTRIB_1D | DECIMAL(12,6) | ACTIVE | 1-day return contribution |
| return_contribution_mtd | RETURN_CONTRIB_MTD | RET_CONTRIB_MTD | DECIMAL(12,6) | ACTIVE | Month-to-date return contribution |
| return_contribution_ytd | RETURN_CONTRIB_YTD | RET_CONTRIB_YTD | DECIMAL(12,6) | ACTIVE | Year-to-date return contribution |

### Source Tracking
| Target Field | Source Field (Alpha) | Source Field (Beta) | Type | Status | Description |
|---|---|---|---|---|---|
| source_system | — | — | STRING | ACTIVE | Originating accounting system |
| source_record_id | RECORD_ID | SRC_REC_ID | STRING | ACTIVE | Record ID in source system |
| source_load_timestamp | LOAD_TS | LOAD_TIMESTAMP | TIMESTAMP | ACTIVE | When loaded from source |
| created_timestamp | — | — | TIMESTAMP | ACTIVE | Record creation time |
| updated_timestamp | — | — | TIMESTAMP | ACTIVE | Last update time |
| is_active | IS_ACTIVE | ACTIVE_FLAG | BOOLEAN | ACTIVE | Whether position is active |

### Regulatory
| Target Field | Source Field (Alpha) | Source Field (Beta) | Type | Status | Description |
|---|---|---|---|---|---|
| regulatory_book | REG_BOOK | REG_CLASSIFICATION | STRING | ACTIVE | Regulatory classification (TRADING/BANKING) |
| accounting_treatment | ACCT_TREATMENT | ACCT_METHOD | STRING | ACTIVE | Accounting method (HFT, AFS, HTM) |
