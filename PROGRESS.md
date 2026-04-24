# Project Progress & Status Log
**Project:** Stock Picks & Automated Trading System
**Repo:** jeetmehta1991/stock-picks-app
**Updated:** April 24, 2026 — End of day

---

## Current Status
**Stage:** 2 — Strategy Validation
**Phase:** 1B — Pre-fetch running on laptop, Phase 1B ready to run after
**Blocker:** Quiver pre-fetch running (insider + 13F + gov_contracts + lobbying + wikipedia + wsb)

---

## Environment Status
| Component | Status |
|---|---|
| GitHub repo | ✅ Clean |
| Codespaces | ✅ Active |
| VS Code laptop | ✅ Python 3.14, all packages installed |
| OHLCV cache (494 tickers) | ✅ Committed to main |
| Quiver congressional (509 tickers) | ✅ Committed to main |
| Quiver insider (509 tickers) | 🔄 Running on laptop |
| Quiver 13F + other data types | ⏳ Queued after insider |
| FRED macro cache | ✅ Committed to main |
| AAII sentiment (260 weekly) | ✅ Committed to main |
| CNN Fear & Greed (1305 daily) | ✅ Committed to main |
| Agent output cache | ✅ Built — JSON per ticker/date/strategy |
| Phase 1A v3 results | ✅ Committed (output_v2/) |

---

## Phase 1A v3 Results Summary

| Metric | Value |
|---|---|
| Trades | 6,942 |
| Strategies fired | 50/60 |
| Gross ROI | 19,685% |
| Net ROI | 18,349% |
| Strategies passing all criteria | 0 (sample size — expected) |
| Best exit method | atr_trail_1x (wins 20/29 strategies) |
| 4 WEAK strategies (OOS 2024 only) | golden_cross_9_21, golden_cross_20_50, bollinger_lower, volume_spike_breakout |

---

## Pre-Phase 1B Data Downloads

| Data | Status | Records |
|---|---|---|
| OHLCV 494 tickers | ✅ Complete | 3 years daily bars |
| Congressional trades 509 tickers | ✅ Complete | Rich — MSFT 1303, AAPL 1087 |
| Insider trades 509 tickers | 🔄 Running | Rich — GOOG 5853, ANET 3768 |
| 13F institutional 509 tickers | ⏳ Queued | — |
| Gov contracts 509 tickers | ⏳ Queued | — |
| Lobbying 509 tickers | ⏳ Queued | — |
| Wikipedia page views 509 tickers | ⏳ Queued | — |
| WallStreetBets 509 tickers | ⏳ Queued | — |
| FRED macro 7 series | ✅ Complete | 1305 daily rows |
| AAII sentiment | ✅ Complete | 260 weekly readings |
| CNN Fear & Greed | ✅ Complete | 1305 daily readings |
| Finnhub news | ⏳ After Quiver | Annual batches per ticker |

---

## Key Decisions Made This Session

| Decision | Outcome |
|---|---|
| Multiple strategies same ticker | Separate independent positions |
| AVOID signal → short trade | Approved in principle — logic design pending |
| Primary exit | Switched to atr_trail_1x |
| Phase 1B universe | Fixed — 509 instruments via --phase 1b |
| Agent output cache | Built — protects against losing API spend |
| Pre-fetch architecture | Built — agents read from disk, not live API |
| Granular before aggregate | Added to CHECKLIST.md and CLAUDE.md |
| Quiver API tier | Upgraded to Trader ($75/mo) for insider + 13F |
| Per-trade exit detail | Added to engine — trade_exit_detail.csv output |
| IS/OOS trade log splits | Added to writer — trade_log_in_sample/out_of_sample.csv |
| Raw smart money signals per trade | Added to ClosedTrade dataclass |
| Sentiment signals per trade | Added to ClosedTrade dataclass |

---

## Issues This Session

| Issue | Resolution |
|---|---|
| Insider endpoint returning 0 records | Hobbyist tier doesn't include insider — upgraded to Trader |
| Wrong Quiver endpoint URLs | Found correct URLs from official Python package source |
| Codespace network blocks Quiver/Finnhub | Pre-fetch scripts run from laptop instead |
| Agent pipeline calling live APIs per candidate | Pre-fetch architecture built — agents read from cache |
| AAII only 15 hardcoded points | Replaced with full CSV (260 weekly readings 2020-2024) |
| CNN only 16 hardcoded points | Replaced with full CSV (1305 daily readings 2020-2024) |
| push rejections during laptop pre-fetch | Expected — manual push after pre-fetch completes |

---

## Upcoming Steps

1. Wait for Quiver pre-fetch to complete on laptop (insider + 6 more data types)
2. Run Finnhub news pre-fetch on laptop
3. Sync Codespace: `git fetch origin ; git reset --hard origin/main`
4. Restart Phase 1B: `nohup python -m backtest.run_phase1a --phase 1b --output-dir output_v2_1b > backtest_1b.log 2>&1 &`
5. Analyse Phase 1B results in analysis_dashboard_1b.html
6. Phase 1C — top 20% strategies, Sonnet agents
7. Phase 1D — top 5 strategies, 5-year test

---

## Strategy Results Tracker

### Passed All 10 Criteria — Phase 1B (pending)
*Not yet*

### Most Promising (Phase 1A — strong profit factors)
| Strategy | Trades | Win Rate | Profit Factor |
|---|---|---|---|
| roc_burst | 125 | 51.2% | 2.98 |
| camarilla_r3_breakout | 162 | 49.4% | 2.62 |
| adx_initiation | 14 | 35.7% | 2.85 |
| pivot_s1_bounce | 44 | 43.2% | 2.37 |

### Best Exit Method (Phase 1A)
- atr_trail_1x wins 20/29 strategies — switched as primary exit

---

## Cost Tracker

| Item | Estimated | Spent | Status |
|---|---|---|---|
| Phase 1A (no agents) | $0 | $0 | ✅ Complete |
| Phase 1B partial run (stopped) | — | ~$3 CAD | ❌ Wasted — incomplete data |
| Phase 1B full run (Haiku) | ~$116 CAD | $0 | Pending pre-fetch |
| Phase 1C (Sonnet) | ~$102 CAD | $0 | Not started |
| Phase 1D (Sonnet) | ~$38 CAD | $0 | Not started |
| Quiver Hobbyist | $30 USD/mo | $30 | Active |
| Quiver Trader upgrade | $75 USD/mo | $75 | Active — cancel after Phase 1B |
| **Total spent** | | **~$108 USD** | |

---
*Updated: April 24, 2026 — End of day*
