# Project Progress & Status Log
**Project:** Stock Picks & Automated Trading System
**Repo:** jeetmehta1991/stock-picks-app
**Updated:** April 24, 2026 — End of day

---

## Current Status
**Stage:** 2 — Strategy Validation
**Phase:** 1B — Pre-fetch running on laptop, restart pending
**Blocker:** Quiver + Finnhub pre-fetch must complete before Phase 1B restart

---

## Environment Status
| Component | Status |
|---|---|
| GitHub repo | ✅ Clean |
| Codespaces | ✅ Active |
| VS Code laptop | ✅ Python + pip working, Git Bash configured |
| OHLCV cache (494 tickers) | ✅ Committed to main |
| FRED macro cache | ✅ Downloaded and committed |
| AAII sentiment CSV | ✅ 260 weekly readings 2020-2024 committed |
| CNN Fear & Greed CSV | ✅ 1,305 daily readings 2020-2024 committed |
| Quiver pre-fetch | 🔄 Running on laptop (~509 tickers × 7 data types) |
| Finnhub news pre-fetch | ⏳ Pending — run after Quiver completes |
| Agent output cache | ✅ 108 analyses cached from aborted run |
| Phase 1B results | ⏳ Pending — restart after pre-fetch completes |

---

## Phase 1A v3 Results (April 22, 2026)

| Metric | Value |
|---|---|
| Trades | 6,942 |
| Strategies fired | 50/60 |
| Gross ROI | 19,685% |
| Net ROI | 18,349% |
| Strategies passing all criteria | 0 (sample size — 67 instruments) |
| Best exit method | atr_trail_1x (wins 20/29 strategies) |

---

## Pre-Phase 1B Data Gaps Fixed This Session

| Gap | Before | After |
|---|---|---|
| AAII sentiment | 15 hardcoded points | 260 full weekly readings 2020-2024 |
| CNN Fear & Greed | 16 hardcoded points | 1,305 daily readings 2020-2024 |
| FRED macro | Live API calls per day | Pre-fetched 7 series, 1,305 daily rows |
| Quiver smart money | Live API calls per ticker per day | Pre-fetched Parquet cache (in progress) |
| Finnhub news | Not integrated | Pipeline built, pre-fetch pending |
| WallStreetBets | Not integrated | Added to Fundamental agent via Quiver |
| Wikipedia views | Not integrated | Added to Fundamental agent via Quiver |
| Agent runtime | 35 seconds per candidate (live API) | Will be ~2 seconds (reads from cache) |
| Estimated Phase 1B runtime | 40-60 hours | 3-4 hours after pre-fetch |

---

## Dashboard — Phase 1B (9 tabs)

| Tab | Content |
|---|---|
| 1. Strategy Performance | Win rate, PF, ROI, SM lift, regimes, **best exit per strategy** |
| 2. Exit Analysis | All 12 exits per strategy ranked by composite score |
| 3. Confidence Tiers | EXCEPTIONAL vs HIGH performance + **best exit per tier** |
| 4. Smart Money Lift | With vs without SM signals — win rate lift measurement |
| 5. Agent Analysis | Tier performance assigned by agents, tier lift |
| 6. Regime Analysis | Performance by regime + **best exit per regime** |
| 7. Walk-Forward | ROBUST/OVERFIT/WEAK per strategy |
| 8. Trade Log | Filterable + **"12 exits" button per trade for trade-level exit detail** |
| 9. Data Quality | Coverage of all data sources, agent cache status |

**New output file:** `trade_exit_detail.csv` — one row per trade × exit method (50k trades × 12 exits = 600k rows). Powers the trade-level exit comparison modal in Tab 8.

---

## Phase 1B Plan

| Item | Value |
|---|---|
| Universe | 509 instruments |
| Date range | Jan 2022 — Dec 2024 |
| Agents | Haiku + full pre-fetched data context |
| Expected trades | 40,000-80,000 |
| Expected cost | ~$116 CAD |
| Expected runtime | 3-4 hours (was 40-60 hours) |
| Output directory | output_v2_1b/ |

**Phase 1B restart command (Codespaces — after pre-fetch complete):**
```bash
git fetch origin ; git reset --hard origin/main
nohup python -m backtest.run_phase1a --phase 1b --output-dir output_v2_1b > backtest_1b.log 2>&1 &
tail -f backtest_1b.log
```

**After run completes:**
```bash
git add output_v2_1b/ backtest/agents/cache/ ; git commit -m "Phase 1B results and agent cache" ; git push origin main
```

---

## Pre-Fetch Scripts (run from laptop)

| Script | Command | Status |
|---|---|---|
| FRED macro | `python scripts/prefetch_macro.py` | ✅ Complete |
| Quiver smart money | `python scripts/prefetch_quiver.py` | 🔄 Running |
| Finnhub news | `python scripts/prefetch_finnhub_news.py` | ⏳ After Quiver |

---

## Upcoming Steps

1. Quiver pre-fetch completes on laptop → auto-commits to main
2. Run Finnhub news pre-fetch on laptop
3. Sync Codespaces: `git fetch origin ; git reset --hard origin/main`
4. Restart Phase 1B with nohup command above
5. Analyse Phase 1B results across all 9 dashboard tabs
6. Lock optimal exit per strategy before Phase 1C
7. Phase 1C — top 20% strategies, Sonnet (~$102 CAD)
8. Phase 1D — top 5 strategies, 5-year test (~$38 CAD)
9. Stage 3 paper trading

---

## Issues Log

| Date | Issue | Resolution |
|---|---|---|
| Apr 18 | pyarrow not installed | Added to requirements.txt + devcontainer |
| Apr 18 | Wikipedia blocked by Codespaces | Replaced with committed CSV |
| Apr 18 | .archive folder bloating repo | Removed from sync workflow |
| Apr 18 | .pyc files committed | Added root .gitignore |
| Apr 19 | Phase 1B universe not switching | Fixed --phase flag in run_phase1a.py |
| Apr 19 | Codespace closing during download | nohup added to all scripts |
| Apr 23 | Stop simulation described incorrectly | Corrected — gap-down exits slightly optimistic |
| Apr 24 | Agents making live API calls (35s each) | Pre-fetch architecture built — reads from disk |
| Apr 24 | AAII only 15 hardcoded points | Replaced with full 260-point CSV |
| Apr 24 | CNN only 16 hardcoded points | Replaced with full 1,305-point CSV |
| Apr 24 | Finnhub news not integrated | Built into Sentiment agent pipeline |
| Apr 24 | WSB + Wikipedia not in agents | Added to Fundamental agent |
| Apr 24 | No trade-level exit comparison | Added trade_exit_detail.csv output |
| Apr 24 | interactive prompt broke nohup | Removed input() call |

---

## Cost Tracker

| Phase | Estimated | Spent | Status |
|---|---|---|---|
| Phase 1A | $0 | $0 | ✅ Complete |
| Phase 1B agents (aborted run) | — | ~$3 CAD | Wasted — incomplete data |
| Phase 1B restart | ~$116 CAD | $0 | Pending pre-fetch |
| Phase 1C (Sonnet) | ~$102 CAD | $0 | Not started |
| Phase 1D (Sonnet) | ~$38 CAD | $0 | Not started |
| Quiver API | $30 USD/month | $30 USD | Active |
| **Stage 2 Total** | **~$300 CAD** | **~$3 CAD** | |

---
*Updated: April 24, 2026 — End of day*
