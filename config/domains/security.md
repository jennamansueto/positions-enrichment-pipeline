# Security Reference Data Domain

## Source Configuration
- **Source System**: security_master
- **Source Table**: sec_master.securities
- **Primary Key**: security_id
- **Load Strategy**: FULL_REFRESH

## Field Mappings

### Identifiers
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| security_id | SEC_ID | STRING | ACTIVE | Unique security identifier |
| isin | ISIN_CODE | STRING | ACTIVE | ISIN |
| cusip | CUSIP_NUM | STRING | ACTIVE | CUSIP |
| sedol | SEDOL_NUM | STRING | ACTIVE | SEDOL |
| ticker | TICKER | STRING | ACTIVE | Bloomberg ticker |
| bbg_global_id | BBG_GLOBAL_ID | STRING | ACTIVE | Bloomberg Global ID |
| ric | RIC_CODE | STRING | ACTIVE | Reuters Instrument Code |
| figi | FIGI_CODE | STRING | ACTIVE | Financial Instrument Global Identifier |

### Names & Description
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| security_name | SEC_NAME | STRING | ACTIVE | Full security name |
| security_short_name | SEC_SHORT_NAME | STRING | ACTIVE | Abbreviated name |
| security_description | SEC_DESC | STRING | ACTIVE | Detailed description |

### Classification
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| security_type | SEC_TYPE | STRING | ACTIVE | BOND, NOTE, BILL, MBS, ABS, etc. |
| asset_class | ASSET_CLASS | STRING | ACTIVE | FIXED_INCOME, EQUITY, DERIVATIVES |
| sub_asset_class | SUB_ASSET_CLASS | STRING | ACTIVE | Sub-classification |
| product_type | PRODUCT_TYPE | STRING | ACTIVE | CORPORATE, SOVEREIGN, MUNI, etc. |

### Issuer
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| issuer_id | ISSUER_ID | STRING | ACTIVE | Issuer identifier |
| issuer_name | ISSUER_NAME | STRING | ACTIVE | Issuer legal name |
| issuer_short_name | ISSUER_SHORT | STRING | ACTIVE | Issuer abbreviated name |
| issuer_lei | ISSUER_LEI | STRING | ACTIVE | Issuer LEI code |
| issuer_country | ISSUER_COUNTRY | STRING | ACTIVE | Issuer country (ISO 3166) |
| issuer_domicile | ISSUER_DOMICILE | STRING | ACTIVE | Issuer domicile |
| issuer_sector | ISSUER_SECTOR | STRING | ACTIVE | Issuer sector |

### Coupon & Payment
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| coupon_rate | CPN_RATE | DECIMAL(8,5) | ACTIVE | Coupon rate (%) |
| coupon_frequency | CPN_FREQ | STRING | ACTIVE | ANNUAL, SEMI, QUARTERLY, MONTHLY |
| coupon_type | CPN_TYPE | STRING | ACTIVE | FIXED, FLOATING, ZERO, STEP_UP |
| coupon_currency | CPN_CCY | STRING | ACTIVE | Coupon payment currency |
| day_count_convention | DAY_COUNT | STRING | ACTIVE | 30/360, ACT/360, ACT/ACT, etc. |

### Dates
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| accrual_start_date | ACCR_START_DT | DATE | ACTIVE | Accrual start date |
| first_coupon_date | FIRST_CPN_DT | DATE | ACTIVE | First coupon payment date |
| last_coupon_date | LAST_CPN_DT | DATE | ACTIVE | Last coupon payment date |
| next_coupon_date | NEXT_CPN_DT | DATE | ACTIVE | Next coupon payment date |
| maturity_date | MATURITY_DT | DATE | ACTIVE | Maturity date |
| issue_date | ISSUE_DT | DATE | ACTIVE | Original issue date |
| dated_date | DATED_DT | DATE | ACTIVE | Dated date (interest accrual begins) |
| first_settle_date | FIRST_SETTLE_DT | DATE | ACTIVE | First settlement date |

### Call & Put Schedule
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| worst_call_date | WORST_CALL_DT | DATE | ACTIVE | Worst-case call date |
| worst_put_date | WORST_PUT_DT | DATE | ACTIVE | Worst-case put date |
| next_call_date | NEXT_CALL_DT | DATE | ACTIVE | Next callable date |
| next_put_date | NEXT_PUT_DT | DATE | ACTIVE | Next puttable date |
| first_call_date | FIRST_CALL_DT | DATE | ACTIVE | First call date |
| first_put_date | FIRST_PUT_DT | DATE | ACTIVE | First put date |
| call_price | CALL_PRICE | DECIMAL(12,6) | ACTIVE | Call price |
| put_price | PUT_PRICE | DECIMAL(12,6) | ACTIVE | Put price |
| call_type | CALL_TYPE | STRING | ACTIVE | AMERICAN, EUROPEAN, BERMUDA |
| is_callable | IS_CALLABLE | BOOLEAN | ACTIVE | Whether security is callable |
| is_puttable | IS_PUTTABLE | BOOLEAN | ACTIVE | Whether security is puttable |
| is_convertible | IS_CONVERTIBLE | BOOLEAN | ACTIVE | Whether security is convertible |
| is_perpetual | IS_PERPETUAL | BOOLEAN | ACTIVE | Whether security is perpetual |
| is_144a | IS_144A | BOOLEAN | ACTIVE | Rule 144A private placement |
| is_reg_s | IS_REG_S | BOOLEAN | ACTIVE | Reg S eligible |

### Sizing
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| par_value | PAR_VALUE | DECIMAL(18,2) | ACTIVE | Par/face value |
| minimum_denomination | MIN_DENOM | DECIMAL(18,2) | ACTIVE | Minimum trade denomination |
| minimum_increment | MIN_INCR | DECIMAL(18,2) | ACTIVE | Minimum increment |
| issue_size | ISSUE_SIZE | DECIMAL(18,2) | ACTIVE | Total issue size |
| amount_outstanding | AMT_OUTSTANDING | DECIMAL(18,2) | ACTIVE | Amount outstanding |
| currency | CCY | STRING | ACTIVE | Denomination currency |

### Geography
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| country_of_risk | CTRY_RISK | STRING | ACTIVE | Country of risk (ISO 3166) |
| country_of_domicile | CTRY_DOMICILE | STRING | ACTIVE | Country of domicile |
| country_of_incorporation | CTRY_INCORP | STRING | ACTIVE | Country of incorporation |
| region | REGION | STRING | ACTIVE | Geographic region |

### Sector & Industry
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| sector | SECTOR | STRING | ACTIVE | GICS/ICB sector |
| industry_group | IND_GROUP | STRING | ACTIVE | Industry group |
| industry | INDUSTRY | STRING | ACTIVE | Industry |
| sub_industry | SUB_INDUSTRY | STRING | ACTIVE | Sub-industry |

### Credit Ratings
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| credit_rating_sp | RATING_SP | STRING | ACTIVE | S&P credit rating |
| credit_rating_moody | RATING_MOODY | STRING | ACTIVE | Moody's credit rating |
| credit_rating_fitch | RATING_FITCH | STRING | ACTIVE | Fitch credit rating |
| composite_rating | RATING_COMPOSITE | STRING | ACTIVE | Composite/internal rating |
| rating_outlook_sp | OUTLOOK_SP | STRING | ACTIVE | S&P rating outlook |
| rating_outlook_moody | OUTLOOK_MOODY | STRING | ACTIVE | Moody's rating outlook |

### Structure
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| seniority | SENIORITY | STRING | ACTIVE | SENIOR_SECURED, SENIOR_UNSECURED, SUBORDINATED |
| collateral_type | COLLATERAL_TYPE | STRING | ACTIVE | Collateral type |
| guarantee_type | GUARANTEE_TYPE | STRING | ACTIVE | Guarantee type |
| payment_rank | PAYMENT_RANK | STRING | ACTIVE | Payment priority rank |

### Floating Rate
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| benchmark_index | BENCHMARK_IDX | STRING | ACTIVE | Benchmark index |
| spread_to_benchmark | SPREAD_BM | DECIMAL(8,4) | ACTIVE | Spread to benchmark (bps) |
| float_index | FLOAT_IDX | STRING | ACTIVE | Floating rate index (SOFR, EURIBOR, etc.) |
| float_spread | FLOAT_SPREAD | DECIMAL(8,4) | ACTIVE | Floating rate spread (bps) |
| float_reset_frequency | FLOAT_RESET_FREQ | STRING | ACTIVE | Float reset frequency |

### Trading
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| exchange | EXCHANGE | STRING | ACTIVE | Primary exchange |
| listing_status | LISTING_STATUS | STRING | ACTIVE | Listing status |
| trading_status | TRADING_STATUS | STRING | ACTIVE | ACTIVE, SUSPENDED, DELISTED |
| settlement_type | SETTLE_TYPE | STRING | ACTIVE | Settlement type (T+1, T+2, etc.) |
| tax_status | TAX_STATUS | STRING | ACTIVE | TAXABLE, TAX_EXEMPT |

### Dividend
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| ex_dividend_date | EX_DVD_DT | DATE | ACTIVE | Ex-dividend date |
| dividend_record_date | DVD_RECORD_DT | DATE | ACTIVE | Dividend record date |
| dividend_pay_date | DVD_PAY_DT | DATE | ACTIVE | Dividend payment date |
| dividend_amount | DVD_AMT | DECIMAL(18,6) | ACTIVE | Dividend amount per share |

### Metadata
| Target Field | Source Field | Type | Status | Description |
|---|---|---|---|---|
| created_timestamp | CREATED_TS | TIMESTAMP | ACTIVE | Record creation time |
