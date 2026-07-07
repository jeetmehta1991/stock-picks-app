<!-- Source: per CHECKLIST #77 canonical-source; Council 287 B1233 2026-07-07 doc-sync sweep -->

<!-- 🟢 COUNCIL 278-287 SYNC BANNER (B1233 2026-07-07) — READ FIRST BEFORE THIS DOC -->
> **Doc-sync status:** This document may contain references stale as of 2026-06-27 or earlier. The current state below overrides any stale references in the body until the next full-rewrite.
>
> **Current canonical values (as of 2026-07-07 B1231):**
> - `len(ALL_STRATEGIES) = 219` (was 220 pre-B1189 DELETE of dxy_headwind_multinational_short; was 221 pre-B874)
> - `STRATEGIES_DISABLED_MISSING_PRODUCER = set()` (was `{dxy_headwind_multinational_short}` pre-B1189)
> - Active strategies for Phase 1A-β cube: 219; cube cells 219×26 = 5,694
> - Test count: **858 passed, 2 skipped** on `test_unit.py + test_integration.py`
> - **CHECKLIST items:** #1–#157 (added #151-#157 in Councils 279-285)
> - **LEARNINGS lessons:** through L202 (added L197-L202 in Councils 279-285)
> - **Latest batch:** B1231 (Council 285)
>
> **Recent Council 278-287 milestones (chronological):**
> - Council 278 (B1188-B1204): 40 SKIP strategies loosened per CSV recommendations
> - Council 279 (B1205-B1210): 11 silent misses remediated + L197 + CHECKLIST #151-#153
> - Council 280 (B1211-B1213): News coverage refined (84.2%) + CHECKLIST #154 codified
> - Council 281 (B1214-B1216): short_interest_pct producer bug + institutional 30% gap surfaced
> - Council 282 (B1217-B1219): Cross-audit 192 strategies + CHECKLIST #155
> - Council 283 (B1220-B1223): 5 more producer audits + comprehensive report
> - Council 284 (B1224-B1228): All 25+ producers audited + historical 2020-2023 spot-check + L201 + CHECKLIST #156
> - Council 285 (B1229-B1231): 2 critical bugs FIXED with graceful degradation + L202 + CHECKLIST #157
> - Council 287 (B1232-B1236 in progress): Stage 4 walks archived + doc-sync sweep
>
> **Stage 4 walks: ARCHIVED 2026-07-07 to `archive/2026-07-07-stage-4-walks-complete/`** (Council 121+ 2026-06-27 owner-approved completion). Any `STAGE_4_*.md` reference in this doc now points to archived location.
>
> **Producer coverage (all 25+ producers audited Councils 280-284):**
> - news_sentiment 84.2% / short_interest_dtc 97.7% / **short_interest_pct 0%** (bug; graceful-degradation fix in B1229) / pead 85% / insider 18.8% (event-rarity) / **institutional_signal 85%** (B1230 corrected from B1216's 30% misattribution) / congressional 67.7% / sec_edgar 97.7% / search_volume 99.2% / index_rebalance 10.5% (event) / earnings_yoy 78.9% / cot_positioning 100% / cross_asset 100% (5 fns) / calendar_effects 100% / macro_events 100% / OHLCV-derived (chart_patterns/technical/dec513/multi_timeframe/cross_sectional/ict_producers/volume_profile/smc_ict/pairs_trading) all 100% (bounded by ~84% OHLCV cache)
> - **Critical historical finding (B1227):** news_sentiment 0% in 2020; short_interest_dtc 0% in 2020; institutional 0% in 2020-2021. Backtest interpretation must annotate producer coverage TIMELINE.
>
> **Sprint 5 tickets queued (post-Council 285 priorities):**
> - S5-B1214-SHARES-OUTSTANDING (HIGH; 1 strategy; 1d) - remove B1229 fallback when data ships
> - S5-B1216-INSTITUTIONAL-13F (MED after B1230 correction; 1 strategy; 1-2d) - expand T1a persistence file
> - S5-B1212-SECONDARY-NEWS (MED; 6 strategies; 2d) - Finnhub/AlphaVantage fallback
>
> **Comprehensive coverage report:** `output_audit/PRODUCER_COVERAGE_COMPREHENSIVE_REPORT.md`

---

# Stock Picks & Automated Trading System

**Stage 2 — Strategy Validation** | Phase 0A complete → Phase 1A launch day **2026-05-15** | Pass 53 Day 9+ Batch 178 | 0 strict blockers

A multi-stage swing trading system: rule-based + smart money + multi-agent architecture validating strategies on historical data before any real money risked.

## Live dashboards (GitHub Pages)

- **Landing:** https://jeetmehta1991.github.io/stock-picks-app/
- **Phase 1A Trade Summary (NEW Batch 177):** https://jeetmehta1991.github.io/stock-picks-app/dashboard_phase_1a/ — 12-tab analytical view: strategies, regime heatmap, MAE/MFE, equity curve, walk-forward, smart-money lift, sector breakdown, skipped trades, circuit breaker log, exits, trades, raw.
- **API endpoint coverage:** https://jeetmehta1991.github.io/stock-picks-app/dashboard_sprint0a/ — 109 CACHED endpoints across 20 APIs.
- **Decisions + Bugs registry:** https://jeetmehta1991.github.io/stock-picks-app/dashboard_stage_2/ — 481 DECs / 250 BUGs / matrix-verified engine consumption.

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
