# Project Progress & Status Log
**Project:** Stock Picks & Automated Trading System
**Repo:** jeetmehta1991/stock-picks-app
**Updated:** April 25, 2026 — End of day

---

## Current Status
**Stage:** 2 — Strategy Validation
**Phase:** 1B — Data pre-fetch in progress
**Blocker:** Quiver API full outage (500 errors) — retry tomorrow

---

## Cache Status on main
| Data | Status | Notes |
|---|---|---|
| OHLCV 509 tickers | ✅ Complete | Extended to March 2026 |
| Quiver congressional | ✅ 509/509 | Complete |
| Quiver insider | ✅ 509/509 | Complete |
| Quiver institutional 13F | ⚠️ 51/509 | API outage — 500 errors for all tickers |
| Quiver gov_contracts | ❌ 0/509 | API outage — not started |
| Quiver lobbying | ❌ 0/509 | API outage — not started |
| Quiver wikipedia | ❌ 0/509 | API outage — not started |
| Quiver wallstreetbets | ❌ 0/509 | API outage — not started |
| Alpha Vantage news | ❌ 0/509 | GitHub Actions batches pending (add secret first) |
| FRED macro | ✅ Extended to March 2026 | Needs push from Codespaces |
| AAII sentiment | ✅ 325 readings | Covers 2020-March 2026 |
| CNN Fear & Greed | ✅ 1630 readings | Covers 2020-March 2026 |

---

## Major Changes This Session

### Code Changes
- Trailing stop: switched from close-based to low/high-based — more realistic, ~2-4pp lower win rate
- Agent temperature = 0 — deterministic backtest results
- PROMPT_VERSION = "v2.0" — auto-invalidates stale agent cache
- Decision Agent: removed tier rules from prompt — now scores independently
- Calmar ratio, 95% CI on all win rates added to metrics
- Smart money lift threshold: ≥ 3pp required (was undefined)
- Macro correlation threshold: ≥ 5pp required (was undefined)
- SPY benchmark comparison added to all strategy metrics
- Sector-adjusted passing criteria in metrics
- Borrow cost for short strategies added
- LIVE_TRADING_RULES config: IBKR Canada, 1 position per ticker
- Alpha Vantage NEWS_SENTIMENT replaces Finnhub (better scores, free, full history)
- VWAP approximation documented in technical.py

### Data Decisions
- Finnhub replaced by Alpha Vantage news (AI sentiment, full 2022-2026, free)
- Quiver Trader tier ($75/mo) — institutional endpoint returning 500s (API outage)
- Broker changed from Alpaca to IBKR Canada

### Documentation
- PROJECT_PLAN.md v6.0 — 982 lines, 45 flags fixed, all design gaps addressed
- LEARNINGS.md — 43 mistakes documented
- CHECKLIST.md — 13 items

---

## Pending Before Phase 1B

| # | Item | Status |
|---|---|---|
| 1 | Quiver institutional 13F | ⏳ API outage — retry tomorrow |
| 2 | Quiver gov_contracts | ⏳ API outage — retry tomorrow |
| 3 | Quiver lobbying | ⏳ API outage — retry tomorrow |
| 4 | Quiver wikipedia | ⏳ API outage — retry tomorrow |
| 5 | Quiver wallstreetbets | ⏳ API outage — retry tomorrow |
| 6 | Alpha Vantage news | ⏳ Add ALPHAVANTAGE_API_KEY secret, trigger 4 batches |
| 7 | FRED macro push | ⏳ Run python scripts/prefetch_macro.py from Codespaces |
| 8 | 25-ticker batch test | ⏳ After all data complete |

---

## Tomorrow Morning Actions

**Laptop Git Bash:**
```bash
export QUIVER_API_KEY="your-key" ; python scripts/prefetch_quiver.py
```

**Codespaces:**
```bash
git fetch origin ; git reset --hard origin/main ; python scripts/prefetch_macro.py
```

**GitHub Actions:**
- Add secret: ALPHAVANTAGE_API_KEY = H1TXLB810KEATNBG
- Trigger: Prefetch Alpha Vantage News → batches 1, 2, 3, 4

---
*Updated: April 25, 2026*
