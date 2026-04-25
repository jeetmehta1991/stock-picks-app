# Project Progress
**Updated:** April 25, 2026 — End of Day

---

## Current Blocker
Quiver API returning 500 errors on all endpoints since ~3pm EST. Retry tomorrow morning.

---

## Data Status

| Data | Status |
|---|---|
| OHLCV 509 tickers to March 2026 | ✅ |
| Quiver congressional | ✅ 509/509 |
| Quiver insider | ✅ 509/509 |
| Quiver institutional 13F | ⚠️ 51/509 — API outage |
| Quiver gov_contracts | ❌ 0/509 — API outage |
| Quiver lobbying | ❌ 0/509 — API outage |
| Quiver wikipedia | ❌ 0/509 — API outage |
| Quiver wallstreetbets | ❌ 0/509 — API outage |
| Alpha Vantage news | 🔄 4 batches running on GitHub Actions |
| FRED macro to March 2026 | ✅ |
| AAII sentiment | ✅ 325 readings |
| CNN Fear & Greed | ✅ 1,630 readings |

---

## What Was Done Today (April 25)

### Major Code Fixes (5 comprehensive audits)
- Fixed CRITICAL bug: smart_money_score returned wrong keys — all agent SM context was empty
- Fixed trailing stop to use intraday low/high (not close) — more realistic
- Fixed walk-forward: now two windows, sector-adjusted, INSUFFICIENT_OOS_DATA verdict
- Fixed survivorship bias: now hold-adjusted per trade
- Fixed crisis regime: now allows longs at 50% size (was blocking all — contradicted buy-the-dip)
- Fixed exit strategies (12 methods): all now use intraday low/high
- Fixed VIX/DXY: now reads from OHLCV cache, not live yfinance during backtest
- Fixed economic calendar: extended to March 2026
- Fixed Quiver live API fallback: disabled during backtest (prevents rate limit exhaustion)
- Added congressional age weighting: <30d full, 30-60d 50%, >60d excluded
- Added portfolio context to Decision Agent: sees open positions, sector concentration
- Added Kelly criterion to all strategy metrics
- Fixed Sharpe ratio: per-trade annualisation (not sqrt(252) which is for daily returns)
- Added sector concentration logging output
- Added portfolio compounding return with tier-based position sizing
- Added strategy-specific signals to Technical Agent (not just generic 10)
- Removed 40-day max hold period (illogical forced exit)
- Added AVOID tier correctly returned by confidence tier function
- Added preliminary_tier and agent_reasoning stored on every trade
- MAE/MFE now accumulated across full trade duration (was single day)
- Two-stage tiering fully implemented and tested
- Replaced Finnhub with Alpha Vantage news (better AI scores, full history, free)

### Tests
- 7/7 integration tests passing
- 29/29 unit tests passing
- End-to-end smoke test framework created

### Documentation
- PROJECT_PLAN.md: complete rewrite as flowing narrative for non-technical reader
- LEARNINGS.md: restructured as universal principles for all future projects

---

## Tomorrow Morning Actions

**Laptop (Git Bash) — check Quiver first:**
```bash
python -c "
import os, requests
token = os.environ.get('QUIVER_API_KEY','')
r = requests.get('https://api.quiverquant.com/beta/historical/congresstrading/AAPL',
    headers={'Authorization': f'Token {token}'}, timeout=10)
print(r.status_code, r.text[:60])
"
```

If 200 → run:
```bash
export QUIVER_API_KEY="your-key" ; python scripts/prefetch_quiver.py
```

**Check Alpha Vantage news batches on GitHub Actions** — all 4 should be green.

**After all data complete → run pre-run validation:**
```bash
python scripts/validate_phase1b_data.py
```

**Then 25-ticker batch test:**
```bash
nohup python backtest/run_phase1a.py --phase 1b --output-dir output_1b_test --start 2022-01-01 --end 2022-01-31 > batch_test.log 2>&1 &
tail -f batch_test.log
```
