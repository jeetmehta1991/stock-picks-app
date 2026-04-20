# Project Progress & Status Log
**Project:** Stock Picks & Automated Trading System
**Repo:** jeetmehta1991/stock-picks-app
**Updated:** April 19, 2026

---

## Current Status
**Stage:** 2 — Strategy Validation
**Phase:** 1A — Pipeline validation on 67 instruments (v3 pending run)
**Blocker:** Two owner decisions required before Phase 1A v3 can run

---

## Environment Status
| Component | Status |
|---|---|
| GitHub repo | ✅ Clean — no .pyc files, no .archive bloat |
| Codespaces | ✅ Active — pyarrow installed via devcontainer |
| VS Code laptop | ✅ Python 3.14 installed, repo cloned |
| Claude Code laptop | ✅ Installed |
| 67-instrument cache | ✅ Committed to main |
| S&P 500 + ETF cache (~509) | 🔜 Download running overnight |
| sync_from_claude workflow | ✅ Fixed — no longer creates .archive on every sync |
| Branch discipline | ⚠️ Needs fixing — claude-updates → sync → main only |

---

## What Has Been Built

### Engine
- 60 strategies across 7 categories (pivot, momentum, trend, mean reversion, breakout, candle, confluence)
- 12 exit methods compared via composite score (40% ROI + 30% PF + 30% DD)
- Trailing stop primary exit: 10% below highest close, never reverses
- 5 circuit breakers in priority order
- Walk-forward validation: in-sample 2022-23, out-of-sample 2024
- Transaction costs: 0.08% ETF / 0.10% large-cap / 0.15% mid-cap
- Survivorship bias haircut: 2% annual
- Slippage model applied at entry
- Parquet cache layer — data persists across Codespace restarts

### Data
- 67-instrument cache committed (SP50 + 17 ETFs)
- S&P 500 ticker list committed as static CSV (482 tickers) — no Wikipedia dependency
- Full S&P 500 + ETF cache (~509 instruments) download running overnight

### Infrastructure
- devcontainer.json — auto-installs all packages on Codespace start
- requirements.txt — all dependencies including lxml, pyarrow, anthropic
- .gitignore — excludes .pyc, __pycache__, .env
- CLAUDE.md — 113-line context file for Claude Code
- PROJECT_PLAN.md — full project reference including all 60 strategies and all rules in plain English
- analysis_dashboard.html — 9-tab interactive dashboard
- launcher.html — navigation page

---

## Approved Rule Changes (Phase 1A v3)

| Rule | Value | Approved |
|---|---|---|
| Open position cap | Removed from backtest | ✅ |
| Daily loss limit | Removed from backtest | ✅ |
| Correlation filter | Removed from backtest | ✅ |
| Regime position sizing | Removed from backtest | ✅ |
| Regime direction hard block | Removed — crisis flagged not blocked | ✅ |
| One trade per ticker per day | Removed — all strategies fire independently | ✅ |
| Max candidates per day | 10 | ✅ |
| Mean reversion ATR multiplier | 1.0× (was 0.5×) | ✅ |
| Liquidity filter | Once at load time only | ✅ |
| Position sizing | EXCEPTIONAL 5% / VERY HIGH 4% / HIGH 3% / MEDIUM-HIGH 1.5% | ✅ |
| Short RSI threshold (rsi_overbought_short) | 68 | ✅ |
| Short candle conditions | Original strict — wait for Phase 1B volume | ✅ |
| Pyramiding | Out of scope — flagged for Stage 4 | ✅ |

---

## Pending Decisions (blocks Phase 1A v3 run)

| # | Decision | Options |
|---|---|---|
| 1 | Multiple strategies on same ticker | A) Separate positions per strategy B) One combined larger position |
| 2 | Review strategies + rules in PROJECT_PLAN.md sections 18 & 19 | Confirm or change anything before run |

---

## Upcoming Steps

1. **Tonight** — S&P 500 + ETF data download completes, auto-commits to main
2. **Tomorrow morning** — Owner reviews PROJECT_PLAN.md sections 18 & 19 (strategies + rules)
3. **Tomorrow** — Decision on multiple strategies per ticker
4. **After decisions confirmed** — Run Phase 1A v3 (67 instruments, all approved rules)
5. **After Phase 1A v3** — Analyse results, confirm before Phase 1B spend (~$116 CAD)
6. **Phase 1B** — Full S&P 500 + ETFs (~509 instruments), Haiku agents
7. **Phase 1C** — Top 20% strategies, Sonnet agents
8. **Phase 1D** — Top 5 strategies, 5-year extended test including COVID 2020
9. **Stage 3** — Paper trading (3-6 months minimum)

---

## Phase 1A Results Log

### v1 Run (April 18, 2026) — SUPERSEDED
- 782 trading days, 66/67 instruments (DIS data issue)
- 198 closed trades, 0 short trades, 17/60 strategies fired
- 9,974 trades skipped
- Gross ROI 780% → Net 742% → Adjusted 736%
- 0 strategies passed all 10 criteria (expected — 100 trade minimum not met)
- Root cause: 5-candidate cap + old restrictions prevented most signals firing
- Pipeline confirmed clean

### v2 Run — ABORTED
- Aborted before completion — rules were still being finalised

### v3 Run — PENDING
- All 13 approved rule changes in place
- Waiting for two owner decisions above

---

## Strategy Results Tracker
*Populated after Phase 1A v3 run completes*

### Passed All 10 Criteria
*None yet*

### Failed — With Reasons
*None yet*

### Flagged for Look-Ahead Bias Audit
*None yet*

### Selected for Phase 1B
*None yet*

### Selected for Phase 1C (Sonnet validation)
*None yet*

### Final Validated Strategies (Phase 1D)
*None yet*

---

## Issues Log

| Date | Issue | Resolution |
|---|---|---|
| Apr 18 | pyarrow not installed — cache not saving | Added to requirements.txt + devcontainer |
| Apr 18 | Wikipedia blocked by Codespaces network | Replaced with committed CSV file |
| Apr 18 | .archive folder bloating repo on every sync | Removed archive step from sync workflow |
| Apr 18 | .pyc files committed to repo | Added root .gitignore, removed all pyc files |
| Apr 18 | Direct pushes to main causing laptop conflicts | Rule re-established: claude-updates → sync → main only |
| Apr 19 | Merge conflicts on laptop from direct main pushes | Resolved manually — branch discipline restored |

---

## Cost Tracker

| Phase | Estimated | Spent | Status |
|---|---|---|---|
| Phase 1A (no agents) | $0 | $0 | Pending v3 run |
| Phase 1B (Haiku) | ~$116 CAD | $0 | Not started |
| Phase 1C (Sonnet) | ~$102 CAD | $0 | Not started |
| Phase 1D (Sonnet) | ~$38 CAD | $0 | Not started |
| Buffer | ~$44 CAD | $0 | Reserved |
| **Stage 2 Total** | **~$300 CAD** | **$0** | |

---
*Updated: April 19, 2026 — End of day*
