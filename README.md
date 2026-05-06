# Stock Picks & Automated Trading System

**Stage 2 — Strategy Validation** | Phase 0A — Sprint 0A active (DEC-497 multi-API prefetch + universe build complete + Stage 2 NO-LIVE-API refactor pending) | Pass 53 in progress

A multi-stage swing trading system: rule-based + smart money + multi-agent architecture validating strategies on historical data before any real money risked.

## Architecture (current)

- **5-bucket universe** (DEC-118 + DEC-483 Pass 53):
  - Tier 1 sub-tiers — T1a S&P 500 (~503) + T1b Russell 1000-non-S&P (~497) + T1c NDX-non-S&P (~15) = ~1015 unique tickers
  - Tier 1 ETFs — 27 sector + macro ETFs ([Backtesting universe/Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv](Backtesting%20universe/Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv))
  - Tier 2 — spinoffs >$5B + recent IPOs >$10B
  - Tier 3 — Top 100 non-T1 momentum names per Jegadeesh-Titman 12-1 (DEC-496)
- **All universe CSVs in [`Backtesting universe/`](Backtesting%20universe/) folder** with B++ schema (`Symbol, Company, Sector, added_date, removed_date`); PIT loader filters by date with NULL-pre-window handling.
- **Signal universe (~265-275 fields)** across 6 categories (Technical / Smart Money / Options / Macro / Sentiment / Company) — see [TRADING_RULES_AND_INFORMATION.md §2A](TRADING_RULES_AND_INFORMATION.md).
- **Smart money composite** with weights matrix + composite labels by score — see [TRADING_RULES_AND_INFORMATION.md §10.8](TRADING_RULES_AND_INFORMATION.md).
- **11-active-agent TradingAgents pipeline** per DEC-057 + [DETAILED_PROJECT_PLAN.md §2.6](DETAILED_PROJECT_PLAN.md) (3 Analysts: Market / Fundamentals / News + Bull / Bear Researchers + Research Manager + Trader + 3 Risk Debaters: Aggressive / Conservative / Neutral + Portfolio Manager; +1 Reflection node post-decision). Pattern 2 integration; Phase 1B+ — see [TRADINGAGENTS_DATA_AUDIT.md](TRADINGAGENTS_DATA_AUDIT.md).

## Five-stage roadmap

| Stage | Description | Status |
|---|---|---|
| 1 | Proof of concept — webpage | ✅ COMPLETE (retired) |
| **2** | **Strategy validation — backtest all signals across regimes** | **IN PROGRESS** (Pass 53; Sprint 1 pending) |
| 3 | Paper trading — validate live with fake money | NOT STARTED |
| 4 | Live trading small — $500-1000 CAD, human approval | NOT STARTED |
| 5 | Full automation — autonomous trading | NOT STARTED |

## Canonical documents

| Doc | Purpose |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Project overview + HARD RULES + repo structure |
| [PROJECT_PLAN.md](PROJECT_PLAN.md) | Stage transition criteria + sprint roadmap + critical path |
| [DETAILED_PROJECT_PLAN.md](DETAILED_PROJECT_PLAN.md) | Per-phase detail (Parts 0-12; Part 2.5 dashboard map) |
| [TRADING_RULES_AND_INFORMATION.md](TRADING_RULES_AND_INFORMATION.md) | Per-rule canonical reference (gates, tiers, exits, regime, PIT, cache, costs, A/B, signal universe §2A, smart money §10.8/§10.9, API endpoints §13.12) |
| [STRATEGY_REGISTER.md](STRATEGY_REGISTER.md) | Strategy roster (~119 classes; ~117 active Phase 1A) |
| [ENGINEERING_REGISTER.md](ENGINEERING_REGISTER.md) | Sprint-level decisions + test signals + effort |
| [AUDIT.md](AUDIT.md) + [AUDIT_INDEX.md](AUDIT_INDEX.md) | Decision history + index (~490 decisions cumulative) |
| [CHECKLIST.md](CHECKLIST.md) | Pre-action checklist (66 items) |
| [LEARNINGS.md](LEARNINGS.md) | Lessons learned (L1-L144+) |
| [EXPLANATION.md](EXPLANATION.md) | Plain-English guide for non-technical readers |
| [Backtesting universe/](Backtesting%20universe/) | All universe CSVs (Pass 53 owner directive — top-level folder for visibility) |

## Critical rules

- **All decisions need explicit owner approval before implementation** — no exceptions.
- **Mandatory pre-flight checklist** (CHECKLIST.md 66 items) before every recommendation.
- **CSV-first data architecture** (Pass 53 HARD RULE) — all input/output data lives in CSV; no exclusively-codebase data.
- **Point-in-time data enforcement** is non-negotiable (DEC-305 RAISE not WARNING).
- **Universe membership PIT** via B++ schema with NULL pre-window handling (DEC-303 / DEC-477).

## Tech stack

- Python 3.11+ / pandas / pyarrow (Parquet)
- Polygon Stocks Starter $29/mo (primary OHLCV + corporate actions + news + fundamentals)
- Quiver Quantitative paid tier (smart money: congressional + insider + 13F + analyst revisions + gov contracts + lobbying)
- FRED + ALFRED (macro: yield curve + FEDFUNDS + cross-asset)
- AAII (sentiment survey) + CNN F&G + CFTC COT
- TradingAgents v0.2.4 (LangGraph, Pattern 2 integration)
- Streamlit (DEC-430 — Phase 1A-α + 1B-α dashboards)
- IBKR / ib_async (Stage 4+ broker integration)

## Stage 2 progress (Pass 53)

Pass 53 universe-build effort completed:
- ✅ Tier 1 ETFs CSV migration from hardcoded list (27 ETFs)
- ✅ T1c NDX populated (157 rows including multi-period entries)
- ✅ T2/T3 schema migrated to B++ format
- ✅ Smart money composite documented (TRADING_RULES §10.8)
- ✅ Comprehensive signal universe documented (TRADING_RULES §2A — 6 categories, ~265-275 fields)
- ✅ API endpoint inventory (TRADING_RULES §13.12 — 16 sources)
- ✅ Universe folder migration to top-level `Backtesting universe/`
- ✅ T1a `Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` (Pass 53 RESOLVED-IMPLEMENTED — 614 rows from Wikipedia rebuild + 4/4 S&P DJI spot-check; renamed Pass 53 from `historical_membership.csv`)
- ⏸ T1b russell_1000_membership.csv (DEFERRED TO STAGE 3 per Pass 53 — LSEG paywall; T1a 503 + T1c 101 + ETFs sufficient for Stage 2)
- ✅ T2 + T3 historical populate (Pass 53 Phase 3+4 done; T2 baseline 10 tickers, full SCREENER pending; T3 1999 period rows / 1220 unique — T2 10 seeds + T3 1220 unique non-T1 tickers via SCREENER-FIRST)
- ✅ Sprint 0A Polygon Stocks Starter ($29/mo) active; OHLCV + reference + corp-actions cache populated
