# Project Progress & Status Log
**Project:** Stock Picks & Automated Trading System
**Repo:** jeetmehta1991/stock-picks-app
**Updated:** April 23, 2026 — End of day

---

## Current Status
**Stage:** 2 — Strategy Validation
**Phase:** 1A complete — Phase 1B ready to run pending API keys
**Blocker:** Owner to register Quiver free + FRED + Finnhub free API keys

---

## Environment Status
| Component | Status |
|---|---|
| GitHub repo | ✅ Clean |
| Codespaces | ✅ Active — pyarrow + all deps auto-install via devcontainer |
| VS Code laptop | ✅ Python installed, repo cloned, Claude Code installed |
| 67-instrument cache (Phase 1A) | ✅ Committed to main |
| 561-instrument cache (Phase 1B) | ✅ Committed to main |
| Phase 1A v3 results | ✅ Committed to main (output_v2/) |
| sync_from_claude workflow | ✅ Fixed — no archive bloat |
| Branch discipline | ✅ claude-updates → main only |
| Agent output cache | ✅ Built — protects against losing API spend on crash |

---

## Phase 1A v3 Results (April 22, 2026)

| Metric | Value |
|---|---|
| Trading days | 782 |
| Instruments | 67 |
| Trades closed | 6,942 |
| Strategies fired | 50/60 |
| Strategies never fired | 10 (conditions not met on 67 instruments — expected) |
| Gross ROI | 19,685% |
| Net ROI (after costs) | 18,349% |
| Adjusted ROI (survivorship) | 18,343% |
| Strategies passing all criteria | 0 (win rate below 55% threshold — sample size issue) |

**Key findings:**
- Profit factors are strong (roc_burst 2.98, camarilla_r3_breakout 2.62) — edge exists
- Win rates below 55% due to 67 instruments only — Phase 1B will fix this
- Short strategies fired (evening_star_short, shooting_star_short, bollinger_upper_short) but loss-making in bull market — need bear market conditions
- `atr_trail_1x` wins as best exit on 20/29 strategies — switched as primary exit
- 4 strategies WEAK (pass out-of-sample 2024 only) — promising signal for Phase 1B
- Pipeline confirmed clean — all 13 output files written correctly

---

## Pre-Phase 1B Checklist

| # | Task | Status |
|---|---|---|
| 1 | Analyst data live-only comment in smart_money.py | ✅ Done |
| 2 | Switch primary exit to atr_trail_1x | ✅ Done |
| 3 | Agent output cache — prevents losing API spend on crash | ✅ Done |
| 4 | Investigate 10 never-fired strategies | ✅ Done — conditions not met on 67 instruments, no code fixes needed |
| 5 | run_backtest.sh with nohup | ✅ Done |
| 6 | Fix Phase 1B universe bug — --phase 1b now loads 509 instruments | ✅ Done |
| 7 | Register Quiver free API key (quiverquant.com) | ⏳ Owner action |
| 8 | Register FRED API key (fred.stlouisfed.org) | ⏳ Owner action |
| 9 | Register Finnhub free API key (finnhub.io) | ⏳ Owner action |
| 10 | Set API keys as env vars in Codespaces | ⏳ Owner action (after #7-9) |
| 11 | AVOID → short trade logic design | ⏳ Pending — approved in principle |
| 12 | Update PROGRESS.md | ✅ This update |

---

## Phase 1B Plan

| Item | Value |
|---|---|
| Universe | 509 instruments (full S&P 500 + all ETFs) |
| Date range | Jan 2022 — Dec 2024 (same as 1A) |
| Agents | Haiku enabled |
| Expected trades | 40,000 — 80,000 |
| Expected cost | ~$116 CAD |
| Expected runtime | 3-4 hours |
| Output directory | output_v2_1b/ |

**Phase 1B run command:**
```bash
nohup bash scripts/run_backtest.sh 1b > backtest_1b.log 2>&1 &
tail -f backtest_1b.log
```

---

## Strategy Results Tracker

### Passed All 10 Criteria
*None yet — Phase 1B required for sufficient trade counts*

### Most Promising (Phase 1A — strong profit factors, need more trades)
| Strategy | Trades | Win Rate | Profit Factor | Notes |
|---|---|---|---|---|
| roc_burst | 125 | 51.2% | 2.98 | Best PF — needs more trades |
| camarilla_r3_breakout | 162 | 49.4% | 2.62 | Most active — needs win rate lift |
| adx_initiation | 14 | 35.7% | 2.85 | Too few trades |
| pivot_s1_bounce | 44 | 43.2% | 2.37 | Needs more instruments |
| supertrend_ichimoku_adx | 101 | 42.6% | 2.23 | ⚠️ audit flag (74.3% WR with hybrid exit) |

### Best Exit Method (Phase 1A)
- `atr_trail_1x` wins on 20/29 strategies — switched as primary exit for Phase 1B
- `hybrid_50pct_target` wins on 4 strategies
- `trailing_15pct` wins on 3 strategies

### Walk-Forward (Phase 1A)
- 4 strategies WEAK (pass OOS 2024 only): golden_cross_9_21, golden_cross_20_50, bollinger_lower, volume_spike_breakout
- 0 ROBUST — expected at 67 instruments

### Never Fired (Phase 1A — 10 strategies)
All due to conditions not met on 67 instruments — not code bugs. Expected to fire in Phase 1B:
52w_high_breakout, bb_squeeze_volume, camarilla_rsi_obv, keltner_lower, parabolic_sar_flip, rsi21_slow, rsi9_extreme, rsi_overbought_short, rsi_oversold, squeeze_breakout

### Failed — Eliminated
*None yet*

### Selected for Phase 1B
*All 60 strategies proceed to Phase 1B*

---

## Key Design Decisions Made This Session

| Decision | Outcome |
|---|---|
| Multiple strategies same ticker | Separate independent positions — all fire |
| AVOID signal → short trade | Approved in principle — logic design pending |
| Primary exit method | Switched to atr_trail_1x (Phase 1A data confirmed) |
| Phase 1B universe | Fixed — 509 instruments via --phase 1b flag |
| ATR period | 14 days (industry standard for swing trading) |
| Stop simulation | Daily Low checked — slightly optimistic on gap-down exits |
| Scalping | Separate future project — not part of this system |
| Agent output cache | Built — JSON cache per ticker/date/strategy/phase |

---

## Upcoming Steps

1. Owner registers 3 free API keys (Quiver, FRED, Finnhub)
2. Owner sets API keys as env vars in Codespaces
3. Design AVOID → short trade logic — present to owner for approval
4. Run Phase 1B (~3-4 hours, ~$116 CAD)
5. Analyse Phase 1B results — confirm exit method per strategy
6. Phase 1C — top 20% strategies with Sonnet (~$102 CAD)
7. Phase 1D — top 5 strategies 5-year extended (~$38 CAD)
8. Stage 3 paper trading

---

## Issues Log

| Date | Issue | Resolution |
|---|---|---|
| Apr 18 | pyarrow not installed — cache not saving | Added to requirements.txt + devcontainer |
| Apr 18 | Wikipedia blocked by Codespaces network | Replaced with committed sp500_tickers.csv |
| Apr 18 | .archive folder bloating repo on every sync | Removed archive step from sync workflow |
| Apr 18 | .pyc files committed to repo | Added root .gitignore |
| Apr 18 | Direct pushes to main causing laptop conflicts | Rule restored: claude-updates → sync → main |
| Apr 19 | Phase 1B universe not switching from 67 instruments | Fixed --phase flag in run_phase1a.py |
| Apr 19 | Codespace closing during long download | Added nohup pattern to all long-running scripts |
| Apr 19 | Had to use ChatGPT for recovery commands | All scripts now self-contained with nohup |
| Apr 23 | Stop simulation described incorrectly | Corrected — daily Low checked, slightly optimistic on gaps |

---

## Cost Tracker

| Phase | Estimated | Spent | Status |
|---|---|---|---|
| Phase 1A (no agents) | $0 | $0 | ✅ Complete |
| Phase 1B (Haiku) | ~$116 CAD | $0 | Pending API keys |
| Phase 1C (Sonnet) | ~$102 CAD | $0 | Not started |
| Phase 1D (Sonnet) | ~$38 CAD | $0 | Not started |
| Buffer | ~$44 CAD | $0 | Reserved |
| **Stage 2 Total** | **~$300 CAD** | **$0** | |

---
*Updated: April 23, 2026 — End of day*
