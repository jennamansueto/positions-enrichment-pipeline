# Data Model

## Enterprise Positions Dataset

The gold-layer output is a denormalized dataset at position grain with ~205 fields across three domains.

### Domains

| Domain | Fields | Primary Key | Source Systems |
|--------|--------|-------------|----------------|
| Positions | ~65 | position_id, book_id, as_of_date | accounting_system_alpha, accounting_system_beta |
| Security | ~85 | security_id | security_master |
| Risk Analytics | ~55 | risk_calc_id | risk_engine |

### Gold Join Logic

```sql
SELECT *
FROM silver.positions p
LEFT JOIN silver.security s ON p.security_id = s.security_id
LEFT JOIN silver.risk_analytics r ON p.position_id = r.position_id
WHERE p._is_current = TRUE
  AND s._is_current = TRUE
  AND r._is_current = TRUE
```

### SCD2 Metadata Columns

| Column | Type | Description |
|--------|------|-------------|
| `_record_hash` | STRING | MD5 hash of all business columns |
| `_effective_from` | TIMESTAMP | When this version became current |
| `_effective_to` | TIMESTAMP | When this version was superseded (NULL if current) |
| `_is_current` | BOOLEAN | Whether this is the current version |
| `_batch_id` | STRING | Pipeline batch identifier |

### Field Groups

**Positions**: Key Fields, Position Values, Dates, Classification, Currency & FX, Organizational, Tax Lots, Portfolio Weights, Margin & Collateral, Source Tracking, Regulatory

**Security**: Identifiers, Names & Description, Classification, Issuer, Coupon & Payment, Dates, Call & Put Schedule, Sizing, Geography, Sector & Industry, Credit Ratings, Structure, Floating Rate, Trading, Metadata

**Risk Analytics**: Key Fields, Pricing, Yields, Duration, Convexity & Sensitivities, Spreads, Value at Risk, Portfolio Risk, Greeks, Scenario Analysis, Volatility & Liquidity
