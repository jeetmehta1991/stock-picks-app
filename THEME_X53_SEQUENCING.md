# Theme X53 — Implementation Sequencing & Dependency Map (15 Stage 2 sub-decisions)

**Background:** Theme X53 (High-Impact Engine Bugs) catalogs CRITICAL/HIGH severity bugs in the backtest engine that produce plausible-looking but invalid results. Parent decisions DEC-307-327 are owner-approved per Pass 52; their implementation sub-decisions DEC-381-399 are the engineering work. This document sequences the 15 truly-pending Stage 2 sub-decisions after CHECKLIST #56 deferred 4 Stage 3+ items (DEC-385/386/387/395) to Stage 3 prep theme.

**Scope filter applied:** CHECKLIST #56 (Phase 0 + Stage 2 only) — DEC-385/386/387 (live circuit breaker mechanics) and DEC-395 (paid sector PIT subscription) deferred per L135.

---

## Dependency tiers

### Tier A — Independent (can start immediately, no blockers)

| Sub-decision | Parent | Description (one-line) | Effort | Resolves |
|---|---|---|---|---|
| **DEC-381** | DEC-307 | Cache get_ohlcv symmetric front-extension (fail-fast, no silent truncation) | ~1d | Cache-correctness gap |
| **DEC-382** | DEC-308 | Replace 20-day floor with min(20, available) + LIMITED_HISTORY flag | ~0.5d | Tier 2 ticker exclusion |
| **DEC-383** | DEC-310 | Remove `df[volume>0]` from cache write; add is_halted column | ~0.5d | Halted-stock invisibility |
| **DEC-384** | DEC-313+337 | update_trailing_stop signature change to use intraday HIGH/LOW | ~1d | BUG-232 lookahead in stops |
| **DEC-388** | DEC-317 | VIX 5-day SMA + hysteresis (crisis ≥40, exit <35) regime input | ~0.5d | Regime classifier flapping |
| **DEC-389** | DEC-318 | AAII pub-lag fix (shift as_of by 1 trading day; add pub_date column) | ~0.5d | BUG-235 PIT violation |
| **DEC-390** | DEC-319 | scripts/refresh_aaii_sentiment.py + GitHub Actions workflow | ~0.5d | BUG-236 stale CSV |
| **DEC-391** | DEC-320 | CNN F&G replace interpolation with last-published; expose age_days | ~0.5d | Interpolation lookahead |
| **DEC-392** | DEC-321 | apply_liquidity_filter fail-closed on missing/zero market_cap | ~0.5d | Silent universe leak |
| **DEC-394** | DEC-323 | Static sector_history.csv with major reclassifications (Phase 1) | ~1d | Sector PIT partial fix |
| **DEC-397** | DEC-326 | Replace hardcoded calendar with rolling train/oos windows | ~1d | Methodology inflexibility |
| **DEC-398** | DEC-327 Phase A | Investigate borrow cost path (improvements vs exit_manager) | ~0.5d | Code path duplication |
| **DEC-399** | DEC-327 Phase B | Consolidate borrow cost to backtest.engine.costs module | ~1d | Cost computation drift |

**Tier A subtotal: 13 sub-decisions, ~9 days effort, no dependencies.**

### Tier B — Blocked on prior decisions (cannot start until prerequisite lands)

| Sub-decision | Parent | Description | Blocker | Effort post-blocker |
|---|---|---|---|---|
| **DEC-393** | DEC-322 | market_cap_pit(ticker, as_of) = close × shares_outstanding(as_of) | DEC-257 (Polygon fundamentals — provides PIT shares outstanding) | ~1d |
| **DEC-396** | DEC-325 | Quiver 13F filing_date capture in prefetch | DEC-450 (Quiver prefetch extension already covers 13F filing_date scope per DEC-410 audit) | ~1-2d |

**Tier B subtotal: 2 sub-decisions, ~2-3 days post-blockers.**

---

## Total Stage 2 X53 implementation effort

**~11-12 days** for 15 sub-decisions (9d Tier A + 2-3d Tier B post-blockers).

Dependency graph:
- Tier A (13 sub-decisions) can start in any order today
- DEC-393 blocked → starts after DEC-257 (Polygon fundamentals prefetch)
- DEC-396 blocked → starts after DEC-450 (Quiver endpoint extension)

---

## Recommended implementation order

Optimized for compound impact:

1. **DEC-383** (zero-volume preservation) — foundational; affects all downstream cache reads
2. **DEC-381** (front-extension fail-fast) — fixes silent truncation that could hide cache holes
3. **DEC-382** (20-day floor relaxation) — unblocks Tier 2 newly-listed tickers in universe
4. **DEC-389** (AAII pub-lag) — PIT correctness; resolves BUG-235 HIGH OPEN
5. **DEC-390** (AAII auto-refresh) — operational; resolves BUG-236 HIGH OPEN
6. **DEC-391** (CNN F&G interpolation fix) — PIT correctness pattern match with DEC-389
7. **DEC-388** (VIX SMA hysteresis) — regime classifier stability; affects DEC-422 cube
8. **DEC-392** (liquidity filter fail-closed) — universe correctness
9. **DEC-394** (sector_history.csv Phase 1) — partial sector PIT fix
10. **DEC-384** (intraday HIGH stop tracking) — execution realism; resolves BUG-232
11. **DEC-397** (rolling train/oos) — enables walk-forward methodology per DEC-082
12. **DEC-398** (borrow cost path investigation) — diagnostic before consolidation
13. **DEC-399** (borrow cost consolidation) — depends on DEC-398 finding
14. **DEC-393** (market_cap_pit) — starts when DEC-257 lands
15. **DEC-396** (Quiver 13F filing_date) — starts when DEC-450 lands

---

## Status: 15 X53 sub-decisions remain PENDING (correctly — they are pending implementation, not approval)

These don't need re-approval — parents already approved Pass 52. They need to land as code changes in chronological/dependency order above. Owner can reference this document during implementation phase to track progress.

*Per CHECKLIST #43/#46/#47/#56/#57. Pass 52 turn 26 execution per owner directive "Approve your recs."*

---

## Pass 53 Update — Phase 1A Restoration Sequencing Impact

**Trigger:** Phase 1A restoration (DEC-486/487/488 PROPOSED Pass 53).

**Impact on Theme X53 sub-decisions:** TIMING UNCHANGED. All X53 engine bug fixes happen in Sprint 2 (Phase 0.C) per original sequencing. Phase 1A baseline (Sprint 6.5) operates on engine that has already had Sprint 2 fixes applied. No X53 sub-decision shifts due to Phase 1A insertion.

**Phase 1A runs against POST-X53 engine state:** This is intentional — Phase 1A is the empirical re-validation that engine fixes (Sprint 2) + Portfolio class (Sprint 3) + cache (Sprint 0A) + universe (Sprint 5) + catch-mechanism (Sprint 6) all integrate correctly. If X53 fixes have residual bugs, Phase 1A surfaces them at scale before Phase 1B agent layer adds complexity.

**No new X53 work introduced by Phase 1A restoration.**

---

## Pass 53 Sprint 0A.0-0A.10 sub-phase detail (DEC-497 + DEC-500/501/502/503 scope)

**Sprint 0A.0** — Quiver Trader-tier endpoint enumeration confirmed via owner dashboard (Pass 53 2026-05-05); 28 unique endpoints across Public + Tier 1 + Tier 2; 8 endpoint groups scoped-in per DEC-502 (App Ratings + Patent Drift dropped per Q1).

**Sprint 0A.1** — Polygon EXTENSION prefetch (news / financials / events / NBBO daily-close); owner-gated per CHECKLIST #68 smoke→demo→full protocol. Excludes options data per DEC-501 (defer Stage 3).

**Sprint 0A.2** — FRED + ALFRED 52-series prefetch curating to ~15-20 high-signal subset (Pass 53 turn analysis recommendation). High-value adds: BAMLH0A0HYM2 (HY OAS), STLFSI4 (financial stress), RECPROUSM156N (recession prob), T10Y3M (alt yield curve). ALFRED vintage realtime_end PIT correction per DEC-301.

**Sprint 0A.3** — AAII + CNN F&G prefetch with composite (current) + 7 sub-components (Pass 53 owner-approved expansion): junk-bond demand spread, put/call ratio, market momentum, stock breadth, safe-haven demand, market vol, stock-price strength.

**Sprint 0A.4** — CFTC COT prefetch (commercial vs speculative positioning, CME E-mini S&P 500); wires existing stub `sentiment.get_cot_report` (which currently returns `not_available`).

**Sprint 0A.5** — Quiver Trader-tier prefetch with **silent-gap fix** (BUG-271/272/273) as prerequisite. 8 endpoint groups + bulk migration:
- Live Quiver News (paginated)
- Off-Exchange Historical (per-ticker; 3,937 rows AAPL confirmed)
- Live Top Shareholders (per-ticker)
- Live ETF Holdings (query-param form)
- Live SEC13F + Live SEC13F Changes (10,000-row paginated bulk)
- Patents Historical + Recent + Patent Momentum (URL paths TBD smoke kickoff)
- Historical Executive Compensation (paginated bulk)
- Corporate Donors Bulk + Historical-by-ticker
- Migration: per-ticker → bulk where dashboard provides Bulk variant (Q3 owner-approved 2026-05-05)
- Smart_money silent-gap fix: REMOVE Quiver branch from `get_analyst_data` (BUG-271); migrate `insider_signal` to `live/insidertrading` (BUG-272); migrate `institutional_signal` to `live/sec13f` (BUG-273); per CHECKLIST #69 full test pyramid.

**Sprint 0A.6** — SEC EDGAR structured prefetch via edgartools library: Form 4 (insider direct, vs Quiver reformat), 8-K (material events for Risk Agent), 10-Q/K (financials, complementary to Polygon `/vX/reference/financials`).

**Sprint 0A.7** — Free social sentiment supplementary sources (Pass 53 Q2 owner-approved 2026-05-05; DEC-502 supplement):
- **Apewisdom** (apewisdom.io) — Free, daily WSB+r/stocks ticker mentions, 2021-present
- **pytrends** (Google Trends Python wrapper) — Free, search-volume index per ticker, 2004-present
- Combined coverage 2020-2026 (Apewisdom 2020 gap filled by pytrends)
- Sentiment Agent integration with bullish/bearish/neutral classification

**Sprint 0A.8** — Stage 2 NO-LIVE-API HARD CUT refactor (DEC-497 owner directive Q8). All `backtest/data/{fetcher,macro,sentiment,smart_money}.py` migrated to read from `data_prefetch/<api_name>/<endpoint>/...` only. yfinance permitted for one-time SETUP only (e.g., universe-build T3 sector backfill); not in runtime hot path.

**Sprint 0A.9** — **Polygon ticker events integration (DEC-500 Pass 53 owner directive 2026-05-05)** — `https://api.polygon.io/vX/reference/tickers/{ticker}/events` (Reference Data, included in Stocks Starter). Event types: ticker_change, ticker_split, name_change, listing_change, exchange_change, delisting, new_listing. Cache: `data_prefetch/polygon/events/{ticker}.parquet`. Feeds all 6 TradingAgents (Risk, Fundamental, Sentiment, Technical, Bull/Bear Debate, Decision) + T2 SCREENER per DEC-380.

**Sprint 0A.10** — Smoke + demo + full tests per API (16 test files: 8 smoke + 8 demo + per CHECKLIST #68); full test pyramid per CHECKLIST #69 (DEC-503): unit + smoke + integration + system + functional + regression + data integrity + performance + acceptance.

**Sprint 0A scope-out (per Pass 53 owner directives 2026-05-05):**
- Polygon Options Starter — DEFERRED to Stage 3 / Phase 1C per DEC-501 (owner Q1=C declined Stocks Starter upgrade)
- Polygon SMA/EMA/RSI/MACD indicator endpoints — DROPPED (duplicates local pandas-ta)
- Polygon NBBO intraday quotes / snapshots / market-status / tick trades — DEFERRED to Stage 3+ live trading
- Quiver App Ratings + Patent Drift — DROPPED per Q1 (low-novelty for regime taxonomy)
- WSB / Twitter / Reddit Quiver endpoints — NOT IN TRADER TIER (filled by Apewisdom + pytrends free alternatives)

**Cross-references:** DETAILED_PROJECT_PLAN.md Part 2.6 (Sprint-Sequenced Index) + Part 3 §3.16-§3.17 (Sprint 0A expanded scope detail); AUDIT_INDEX.md DEC-497-503; AUDIT.md Pass 53 narrative; BUG_REGISTER.md BUG-271/272/273.

