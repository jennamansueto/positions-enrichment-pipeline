# Risk Analytics Domain

## Source Configuration
- **Source System**: risk_engine
- **Source Table**: risk.calculations
- **Primary Key**: risk_calc_id
- **Load Strategy**: INCREMENTAL

## Field Mappings

### Key Fields
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| risk_calc_id | CALC_ID | STRING | ACTIVE | Unique risk calculation identifier |
| security_id | SEC_ID | STRING | ACTIVE | Foreign key to security |
| position_id | POS_ID | STRING | ACTIVE | Foreign key to position |
| as_of_date | CALC_DATE | DATE | ACTIVE | Calculation date |
| calc_timestamp | CALC_TS | TIMESTAMP | ACTIVE | When calculation was performed |

### Pricing
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| price_clean | CLEAN_PX | DECIMAL(12,6) | ACTIVE | Clean price |
| price_dirty | DIRTY_PX | DECIMAL(12,6) | ACTIVE | Dirty price (clean + accrued) |
| price_mid | MID_PX | DECIMAL(12,6) | ACTIVE | Mid price |
| price_bid | BID_PX | DECIMAL(12,6) | ACTIVE | Bid price |
| price_ask | ASK_PX | DECIMAL(12,6) | ACTIVE | Ask price |
| price_source | PX_SOURCE | STRING | ACTIVE | Price source (BLOOMBERG, ICE, INTERNAL) |

### Yields
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| yield_to_maturity | YTM | DECIMAL(8,5) | ACTIVE | Yield to maturity (%) |
| yield_to_worst | YTW | DECIMAL(8,5) | ACTIVE | Yield to worst (%) |
| yield_to_call | YTC | DECIMAL(8,5) | ACTIVE | Yield to call (%) |
| current_yield | CUR_YIELD | DECIMAL(8,5) | ACTIVE | Current yield (%) |
| yield_spread_to_govt | SPREAD_GOVT | DECIMAL(8,4) | ACTIVE | Spread to government (bps) |

### Duration
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| duration_macaulay | DUR_MAC | DECIMAL(10,6) | ACTIVE | Macaulay duration |
| duration_modified | DUR_MOD | DECIMAL(10,6) | ACTIVE | Modified duration |
| duration_effective | DUR_EFF | DECIMAL(10,6) | ACTIVE | Effective/option-adjusted duration |
| duration_spread | DUR_SPREAD | DECIMAL(10,6) | ACTIVE | Spread duration |
| duration_key_rate_2y | KRD_2Y | DECIMAL(10,6) | ACTIVE | Key rate duration (2Y) |
| duration_key_rate_5y | KRD_5Y | DECIMAL(10,6) | ACTIVE | Key rate duration (5Y) |
| duration_key_rate_10y | KRD_10Y | DECIMAL(10,6) | ACTIVE | Key rate duration (10Y) |
| duration_key_rate_30y | KRD_30Y | DECIMAL(10,6) | ACTIVE | Key rate duration (30Y) |

### Convexity & Sensitivities
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| convexity | CONVEXITY | DECIMAL(10,6) | ACTIVE | Convexity |
| effective_convexity | EFF_CONVEXITY | DECIMAL(10,6) | ACTIVE | Effective/option-adjusted convexity |
| dv01 | DV01 | DECIMAL(18,2) | ACTIVE | Dollar value of a basis point |
| cr01 | CR01 | DECIMAL(18,2) | ACTIVE | Credit spread sensitivity (1bp) |
| cs01 | CS01 | DECIMAL(18,2) | ACTIVE | Credit spread 01 |

### Spreads
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| oas | OAS | DECIMAL(8,4) | ACTIVE | Option-adjusted spread (bps) |
| z_spread | Z_SPREAD | DECIMAL(8,4) | ACTIVE | Zero-volatility spread (bps) |
| i_spread | I_SPREAD | DECIMAL(8,4) | ACTIVE | Interpolated spread (bps) |
| g_spread | G_SPREAD | DECIMAL(8,4) | ACTIVE | Government spread (bps) |
| asset_swap_spread | ASW_SPREAD | DECIMAL(8,4) | ACTIVE | Asset swap spread (bps) |

### Value at Risk
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| var_95_1d | VAR_95_1D | DECIMAL(18,2) | ACTIVE | Value at Risk (95%, 1-day) |
| var_99_1d | VAR_99_1D | DECIMAL(18,2) | ACTIVE | Value at Risk (99%, 1-day) |
| var_95_10d | VAR_95_10D | DECIMAL(18,2) | ACTIVE | Value at Risk (95%, 10-day) |
| cvar_95_1d | CVAR_95_1D | DECIMAL(18,2) | ACTIVE | Conditional VaR (95%, 1-day) |
| cvar_99_1d | CVAR_99_1D | DECIMAL(18,2) | ACTIVE | Conditional VaR (99%, 1-day) |

### Portfolio Risk
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| beta_to_benchmark | BETA | DECIMAL(8,4) | ACTIVE | Beta to benchmark index |
| tracking_error | TRACK_ERR | DECIMAL(8,4) | ACTIVE | Tracking error (%) |

### Greeks
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| delta | DELTA | DECIMAL(10,6) | ACTIVE | Option delta |
| gamma | GAMMA | DECIMAL(10,6) | ACTIVE | Option gamma |
| theta | THETA | DECIMAL(10,6) | ACTIVE | Option theta |
| vega | VEGA | DECIMAL(10,6) | ACTIVE | Option vega |
| rho | RHO | DECIMAL(10,6) | ACTIVE | Option rho |

### Scenario Analysis
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| scenario_up_50bps | SCEN_UP_50 | DECIMAL(18,2) | ACTIVE | P&L impact: rates +50bps |
| scenario_down_50bps | SCEN_DN_50 | DECIMAL(18,2) | ACTIVE | P&L impact: rates -50bps |
| scenario_up_100bps | SCEN_UP_100 | DECIMAL(18,2) | ACTIVE | P&L impact: rates +100bps |
| scenario_down_100bps | SCEN_DN_100 | DECIMAL(18,2) | ACTIVE | P&L impact: rates -100bps |
| scenario_up_200bps | SCEN_UP_200 | DECIMAL(18,2) | ACTIVE | P&L impact: rates +200bps |
| scenario_credit_widen_100bps | SCEN_CRD_100 | DECIMAL(18,2) | ACTIVE | P&L impact: credit spreads +100bps |

### Volatility & Liquidity
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| implied_volatility | IMPL_VOL | DECIMAL(8,4) | ACTIVE | Implied volatility (%) |
| historical_volatility_30d | HIST_VOL_30D | DECIMAL(8,4) | ACTIVE | 30-day historical volatility (%) |
| liquidity_score | LIQ_SCORE | DECIMAL(5,2) | ACTIVE | Internal liquidity score (0-100) |
| bid_ask_spread | BID_ASK_SPREAD | DECIMAL(8,4) | ACTIVE | Bid-ask spread |
| avg_daily_volume | AVG_DAILY_VOL | BIGINT | ACTIVE | Average daily trading volume |
| days_to_liquidate | DAYS_TO_LIQUIDATE | DECIMAL(8,2) | ACTIVE | Estimated days to liquidate position |
| turnover_ratio | TURNOVER_RATIO | DECIMAL(8,4) | ACTIVE | Turnover ratio |
