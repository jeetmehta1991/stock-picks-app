# Stock Picks & Automated Trading System

**Stage 2 — Strategy Validation** | Phase 1A pending Sprint 1 Polygon prefetch | Pass 53 in progress

A multi-stage swing trading system: rule-based + smart money + multi-agent architecture validating strategies on historical data before any real money risked.

## Architecture (current)

- **5-bucket universe** (DEC-118 + DEC-483 Pass 53):
  - Tier 1 sub-tiers — T1a S&P 500 (~503) + T1b Russell 1000-non-S&P (~497) + T1c NDX-non-S&P (~15) = ~1015 unique tickers
  - Tier 1 ETFs — 27 sector + macro ETFs ([Backtesting universe/tier1_etfs.csv](Backtesting%20universe/tier1_etfs.csv))
  - Tier 2 — spinoffs >$5B + recent IPOs >$10B
  - Tier 3 — Top 100 non-T1 momentum names per Jegadeesh-Titman 12-1 (DEC-496)
- **All universe CSVs in [`Backtesting universe/`](Backtesting%20universe/) folder** with B++ schema (`Symbol, Company, Sector, added_date, removed_date`); PIT loader filters by date with NULL-pre-window handling.
- **Signal universe (~265-275 fields)** across 6 categories (Technical / Smart Money / Options / Macro / Sentiment / Company) — see [TRADING_RULES_AND_INFORMATION.md §2A](TRADING_RULES_AND_INFORMATION.md).
- **Smart money composite** with weights matrix + composite labels by score — see [TRADING_RULES_AND_INFORMATION.md §10.8](TRADING_RULES_AND_INFORMATION.md).
- **6-agent TradingAgents pipeline** (Pattern 2 integration; Phase 1B+) — see [TRADINGAGENTS_DATA_AUDIT.md](TRADINGAGENTS_DATA_AUDIT.md).

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
- ⏸ T1a historical_membership.csv (Sprint 1 — S&P DJI press release scrape)
- ⏸ T1b russell_1000_membership.csv (Sprint 1 procurement — LSEG paywall)
- ⏸ T2 + T3 historical populate (Sprint 1 — post-Polygon-prefetch)
- ⏸ Sprint 1 Polygon prefetch (~$29/mo subscription owner action)
