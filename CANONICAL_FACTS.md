# CANONICAL_FACTS.md — Single Source of Truth for Project Quantitative Facts

**Created:** Pass 53 — 2026-05-06 (owner directive Q1=A "approve canonical-facts registry")
**Purpose:** Eliminate cross-document drift on quantitative claims (agent count, strategy count, signal count, test count, etc.) by maintaining one canonical value per fact with explicit dependencies and the docs that must agree.
**Authority:** This file is the single source of truth. If any other document conflicts with a fact stated here, this file wins and the conflicting doc is updated.
**Update protocol:** When the underlying number changes (e.g., new strategies decided, new tests added), update this file FIRST. Then run `backtest/tests/test_canonical_facts_alignment.py` to identify drifted docs. Update those docs. Commit atomically.
**Owner directive 2026-05-06:** "It doesnt matter at this stage whats in the code but rather whats planned." → values below are **PLANNED** state. Code-current state recorded as secondary annotation only.

---

## Why this file exists

Pass 53 owner question: *"Why are things like this getting missed?"*

Five compounding factors drove the 11-vs-6 agent drift (and several other latent drifts):
1. No single source of truth per quantitative fact — every doc independently states "6 agents", "60 strategies", etc.
2. CHECKLIST #43 (cross-doc consistency) is reactive — it triggers when someone notices drift, not at write time
3. No executable doc assertion — `test_unit.py` validates code, nothing validates that docs match each other
4. Pass-by-pass layering — each Pass adds new sections without retro-updating prior ones; numbers calcify
5. Reactive grep-and-fix behavior — when a single drift is reported, only that drift gets fixed; adjacent same-pattern drifts stay invisible

This file is the structural fix for #1; the alignment test is the structural fix for #2 and #3; the update protocol above (per-fact-first) is the structural fix for #4 and #5.

---

## Counting conventions (read first)

- **"Class" vs "variant":** A *strategy class* is unique entry/exit logic. A *variant* is the same class with parametric difference (long vs short, daily vs weekly TF). Counts in this file are **classes** unless specifically noted as variants.
- **"Active" vs "planned":** *Active* = currently executing in the latest run. *Planned* = decided + scoped but possibly not yet implemented. *Aspirational* = under consideration but not decided. Default scope below is **planned** per owner directive.
- **"Stage" vs "Phase":** Stage = top-level program milestone (1-5). Phase = sub-milestone within Stage 2-3 (1A, 1A-α, 1A-β, 1B, 1B-α, 1C, 1D). Sprint = engineering execution unit within phases.
- **"PIT" = point-in-time:** Data must reflect what was knowable as-of the trade date; no lookahead (DEC-261, DEC-305).

---

## Canonical Facts

Each fact has: **F-NNN identifier** • value (planned) • scope/definition • source-of-truth (SSOT) doc • dependencies (depends-on / depended-on-by) • docs that must align • code-current state (annotation only).

---

### F-001 — Agent count (TradingAgents pipeline)

**Value (planned):** **11 active LLM nodes per `propagate()` + 1 Reflection node post-decision = 12 total LLM nodes per candidate-day.**

**Definition:** "Agent" in this project means a discrete LangGraph node in TradingAgents v0.2.4 that issues one or more LLM calls and produces structured output consumed by the next node. Pre-Pattern-2 phrasing ("6 agents") referred to *conceptual roles* (Technical / Fundamental / Sentiment / Risk / Bull-Bear / Decision); this is no longer accurate as a node count.

**The 11 active agents (canonical enumeration):**
1. Market Analyst
2. Fundamentals Analyst
3. News Analyst
4. Bull Researcher
5. Bear Researcher
6. Research Manager
7. Trader
8. Aggressive Risk Debater
9. Conservative Risk Debater
10. Neutral Risk Debater
11. Portfolio Manager
12. (+1) Reflection (post-decision; runs once per closed trade for continuous learning)

**SSOT:** `DETAILED_PROJECT_PLAN.md` §2.6 + DEC-057 (TradingAgents Pattern 2 integration)
**LLM call count caveat:** Each Analyst can make 2-4 LLM calls due to LangChain tool-use loops (initial → tool → interpret → maybe retry). True call count per propagate() ≈ 2-3× node count (`LEARNINGS.md` L94).

**Dependencies (depends-on):**
- DEC-057 (Pattern 2 architecture decision) — without this, count would be 6 conceptual roles
- TradingAgents v0.2.4 source (`tradingagents_integration/`) — pinned version determines node graph
- 5 Custom toolkits F-011 (each agent consumes one or more)

**Dependencies (depended-on-by):**
- F-002 strategy count (agents overlay strategies; agent gating per `AgentGateConfig` DEC-481)
- Phase 1B+ cost estimate (`backtest/run_phase1a.py` lines 178-182): cost = days × candidates × 11 × $/Haiku-call × USD→CAD
- F-010 confidence-tier mapping (Portfolio Manager rating → position size modifier)
- DEC-507 wiring matrix (`TRADINGAGENTS_DATA_AUDIT.md` §1071+) — 13 rows = 5 toolkits + 8 LangGraph nodes; canonical 11 enumerated in matrix-structure note

**Docs that must align:** `CLAUDE.md` (repo structure docstring + agent pipeline section) • `README.md` line 17 • `EXPLANATION.md` §What are agents • `DETAILED_PROJECT_PLAN.md` §2.6 + §3.16.7 + §2.5 • `AUDIT_INDEX.md` DEC-500 entry • `API_AUDIT.md` ticker events feed • `TRADING_RULES_AND_INFORMATION.md` DEC-500 entry • `THEME_X53_SEQUENCING.md` Sprint 0A.9 • `TRADINGAGENTS_DATA_AUDIT.md` DEC-500 + matrix header • `backtest/run_phase1a.py` cost estimator strings.

**Acceptable phrasing variants:** "11 active agents", "11 active LLM nodes", "12 total LLM nodes per propagate() (11 active + 1 Reflection)", "12-agent debate pipeline (per DETAILED_PROJECT_PLAN §2.6)" — all valid; pick whichever fits context. *Not acceptable:* bare "6 agents", "6-agent pipeline".

**Code-current state:** `tradingagents_integration/` graph instantiates 11 active + 1 Reflection per `propagate()`.

---

### F-002 — Strategy roster (planned + LIVE)

**Live value (`len(ALL_STRATEGIES)` 2026-05-29 Batch 467):** **188 IMPLEMENTED strategy classes registered** in `backtest/signals/screener.py::ALL_STRATEGIES` (was 186 through Batch 372; Batch 467 P10 added `news_momentum_long` + `news_reversal_short`). `DEPRECATED_STRATEGIES` set is empty (Batch 316a un-deprecation 2026-05-25 reversed Batch 218). `STRATEGIES_DISABLED_MISSING_PRODUCER` set holds **1 strategy** (`dxy_headwind_multinational_short`; Batch 372 2026-05-26 owner-directed disable — foreign_rev_pct producer absent across Polygon Stocks Starter, SEC EDGAR companyfacts, SEC XBRL prefetch, Finnhub financials_reported; semantically distinct from literature-null deprecation). **187 active for Phase 1A-β cube mode** (187 × 25 = 4,675 cells; was 185 × 25 = 4,625 pre-Batch-467). Re-enable is a single-line removal once a 10-K XBRL segment-axis parser ships or paid Polygon Plus tier is approved.

**Value (planned target):** **199 RESOLVED-DECIDED strategy classes across 6 layers post owner "Approve all" + Layer 1.I symmetry + Q1+Q2+Q3 (Layer 5 flag schema + Layer 6 27 new) 2026-05-06 (was 134 pre-symmetry; 108-118 pre-Pass-53-Option-2). Goes to 203 when Layer 4 PENDING-DEC promoted; ~213 with Layer 2D form-derived ICT estimate. ~200-400+ multi-TF variants projected. Total unique testable strategies projected: 200+ confirmed (could exceed 400 with full multi-TF expansion).** Gap: 199 (target) - 186 (live) = 13 classes pending implementation across Layers 2D + 4 + 6 remainder.

**Project philosophy (owner directive 2026-05-06):** *"Buy the dip and sell the rip."* The roster evaluates long AND short strategies wherever the entry logic is logically symmetric. Direction asymmetry in Layer 1.A-H was a documentation artifact (PROJECT_PLAN section 6 baseline was long-biased; Layer 1.H added 12 shorts incrementally without coherent symmetry). Layer 1.I (38 new shorts approved 2026-05-06) closes the symmetry gap, bringing Layer 1 long/short ratio to ~1.2:1. Empirical results from Phase 1A-α / Phase 1B-α validation determine which strategies have edge in which direction; the roster's job is to make BOTH directions evaluable. Strategies that are NOT logically symmetric (breadth-thrust, dividend-initiation drift, defensive-tilt overlays) remain single-direction by design.

**Definition:** A "strategy" is a unique combination of {entry signal, entry zone, regime filter, exit method}. Layered roster:

| Layer | Source | Status | Class count | Notes |
|---|---|---|---|---|
| **Layer 1 — Baseline + symmetry** | PROJECT_PLAN section 6 + Pass 53 Layer 1.I owner-approved 2026-05-06 | DOCUMENTED + IMPLEMENTED (60L+12S) + RESOLVED-DECIDED (38 new S Sprint 7+) | **110** (60L + 50S; ratio ~1.2:1) | Layer 1.A-G 60 long baseline (Pivot 10, Momentum 9, Trend 9, Mean Rev 11, Breakout 6, Candle 6, Confluence 9) + Layer 1.H 12 dedicated shorts + Layer 1.I 38 symmetry shorts (philosophy: "buy the dip + sell the rip"). See [STRATEGY_ROSTER_FULL.md](STRATEGY_ROSTER_FULL.md) for per-strategy enumeration. |
| **Layer 2 — Phase 0.D additions** | DEC-045 / DEC-259 / DEC-261 + Pass 53 owner "Approve all" 2026-05-06 | RESOLVED-DECIDED post Pass 53 | **21** (12 + 4 + 5) | 2A ICT/SMC (6 patterns × 2 directional = 12 classes), 2B Earnings Momentum (4 named), 2C Calendar (5 named; DEC-368 absorbed). See [STRATEGY_ROSTER_FULL.md](STRATEGY_ROSTER_FULL.md). |
| **Layer 2D — ICT form-derived (NEW Pass 53 owner directive)** | smartmoneyconcepts library + form-derived patterns | PENDING-FORM — additional ICT strategies derived from owner's form once operational | **+TBD (likely 5-15)** | Owner Pass 53 Q2 directive: "doesnt yet include additional ICT strategies that will be derived from the form" — requires owner-driven enumeration once form is operational |
| **Layer 3A — Chart patterns** | DEC-355-362 (Pass 52) | RESOLVED-DECIDED | **20** | 10 base classes × 2 directional (with DEC-358 split into Wedge/Triangle/Pennant) per [STRATEGY_ROSTER_FULL.md](STRATEGY_ROSTER_FULL.md) |
| **Layer 3B — Strategy categories** | DEC-367/369/370/371 + Pass 53 owner "Approve all" 2026-05-06 | RESOLVED-DECIDED post Pass 53 | **21** | 4 Pairs/Stat Arb (DEC-367), 4 Cross-Asset (DEC-369), 2 Index Rebalance (DEC-370), 11 within-category gaps (DEC-371). DEC-368 Calendar absorbed into Layer 2C. |
| **Layer 4 — PENDING strategy-additive** | DEC-141/142/143/145/176 | 🔴 PENDING-DEC (per-DEC promotion required) | **~5-6** | Sector-neutral hedge overlay, market-neutral SPY, IPO/lockup framework, IV pre-earnings, meta-strategies (DEC-176 multiplier not counted) |
| **Layer 5 — Regime-eligibility flag schema** (✅ RESOLVED-DECIDED, owner-approved 2026-05-06 Q1) | overlay (no new strategies) | RESOLVED-DECIDED | **0 strategies; 172 tagged** | F-006 4-regime classifier reuse + per-strategy `regime_eligible` flag. Default flags by category (Pivot all, Momentum trending, Trend trending, Mean Rev neutral, Breakout trending, Candle all, Confluence inherit). See [STRATEGY_ROSTER_FULL.md Layer 5](STRATEGY_ROSTER_FULL.md). |
| **Layer 6 — External-AI-review additions** (✅ RESOLVED-DECIDED, owner-approved 2026-05-06 Q1) | external AI strategy review filtered + dedup | RESOLVED-DECIDED post Pass 53 | **27 (172-198)** | 6A Cross-sectional (8) + 6B Vol regime (3) + 6C Overnight/gap (5) + 6D Insider (1) + 6E Breadth (4) + 6F Drift (2) + 6G Microstructure (4). 17 external proposals rejected (11 dups + ORB out-of-scope + subscription/data-deferred). |
| **Total RESOLVED-DECIDED + IMPLEMENTED classes** | | | **199** (post Pass 53 "Approve all" + Layer 1.I symmetry + Q1+Q2+Q3 2026-05-06) | Was 134 pre-symmetry. Goes to **203** with Layer 4 promotion; **~213** with Layer 2D form-derived estimate. Owner expects "100+ strategies tested" — confirmed (200+ projected). |
| **+ long/short variants** | DEC counting convention | | **~150-200+** | Many classes have separate long + short entry logic |
| **+ multi-TF (DEC-350: daily + weekly)** | DEC-350 | | **~200-300+** | If non-ICT roster doubled with weekly TF |

**Phase-specific active counts:**
- **Phase 1A active:** ~117 of ~119 baseline classes (2 skipped per DEC-490: `buyback_announcements` needs SEC EDGAR Sprint 4; `guidance_driven_momentum` needs transcripts dropped DEC-485)
- **Phase 1B active:** Same roster as 1A (agent overlay added on top; roster does not change)
- **Phase 1C+:** Layer 2 + Layer 3 strategies operational (Sprint 8 — strategy categories implementation)

**SSOT:** `STRATEGY_REGISTER.md` (canonical layered roster doc) + **[`STRATEGY_ROSTER_FULL.md`](STRATEGY_ROSTER_FULL.md)** (per-strategy enumeration with every named strategy across all layers, Pass 53 Option 2 owner-directive)
**Origin docs:** `PROJECT_PLAN.md` §6 (Layer 1) • `PROJECT_PLAN_ARCHIVE.md` §5/§6 (Layer 1 detailed enumeration) • `AUDIT_INDEX.md` (DECs for Layers 2-4) • `backtest/signals/screener.py:812` `ALL_STRATEGIES` registry (Layer 1 code SSOT)

**Dependencies (depends-on):**
- F-005 universe size (more tickers = more candidate-days = strategies have more opportunities to fire)
- F-002.signals (each strategy reads one or more signal categories)
- DEC-045 (fork-first) — gates Layer 2A ICT/SMC via smartmoneyconcepts library; per DEC-508 + CHECKLIST #71 must complete Phase A/B/C before strategies fire
- DEC-261 (PIT N+1 enforcement) — strategy logic must compute on as-of data only
- DEC-484 (SEC EDGAR Sprint 4) — gates Layer 1 `buyback_announcements`
- DEC-485 (transcripts dropped) — kills Layer 1 `guidance_driven_momentum` for Stage 2

**Dependencies (depended-on-by):**
- F-009 passing criteria — each strategy gets per-regime verdict (PASS/FAIL/INSUFFICIENT_DATA) for each of 7 historical regimes
- Phase 1B-α dimensional cube — cube cells = strategies × regimes × sectors × …
- F-001 agent overlay — agents adjust confidence tier on top of strategy-fired candidates
- Cost estimates — runtime + LLM cost scales linearly with strategy count × universe size

**Docs that must align:**
- `STRATEGY_REGISTER.md` (canonical; Update FIRST)
- `EXPLANATION.md` §The 4 layers — must reference the layered roster, not a single integer
- `PROJECT_PLAN.md` §7.4 (Layer 1 baseline enumeration) — narrowly says "60 baseline" which is correct *for Layer 1 only*
- `DETAILED_PROJECT_PLAN.md` §3 + §7
- `IMPLEMENTATION_READINESS_DASHBOARD.md` — current Phase 1B-α scoping
- `CLAUDE.md` HARD RULES — currently does not state a strategy count; that's correct

**Acceptable phrasing variants:** "60 baseline + 12 Layer 2 + 8-30 Layer 3 + Layer 2D ICT form-derived + 5-6 PENDING ≈ 108-133+ classes (100+ unique testable strategies projected)" — or scope-narrow: "Layer 1 baseline (60 classes per PROJECT_PLAN §6)". *Not acceptable:* a bare "60 strategies" or "72 strategies" without scope qualifier.

**Code-current state:** `len(ALL_STRATEGIES) == 60` in `backtest/signals/screener.py`; CI asserts via `.github/workflows/validate_backtest.yml:58`. Layer 2/2D/3/4 strategies pending implementation. **Per owner directive, code-current is secondary; planned roster is canonical.**

---

### F-003 — Signal universe (planned)

**Value (planned):** **~270-280 active signal fields in Stage 2 backtest (current state) → ~315-325 post Sprint pre-Phase-1A (DEC-511 Category 7 universe-level signals + DEC-513 P1 signal additions, owner-approved 2026-05-06). 7 canonical categories (was 6 pre-Pass-53; Category 7 universe-level signals added DEC-511). Stage 3+ adds Category 3 options + completes Category 6 fundamentals → ~340+ signal fields. Owner expects "over 200" — confirmed; total exceeds 300 with Category 7 + DEC-513.**

**Definition:** A "signal" is a single computed numeric or categorical field per ticker per as-of date, consumed by strategies, agents, or the screener. Signals are computed deterministically from cached data; no live API calls per Stage 2 NO-LIVE-API HARD CUT (DEC-497 D4).

**The 6 canonical categories:**

Status is split into **two independent layers** (per owner directive 2026-05-06 — Option B refactor):
- **Prefetch state** = is the raw data cached in `data_prefetch/<api>/<endpoint>/...`? (or in `backtest/data/cache/` for OHLCV)
- **Consumer state** = is the cached data parsed + exposed as signals + read by the consuming agent toolkit?

A category can have prefetch ✅ but consumer 🔴 (data sitting on disk, no code reads it for agent input). This is the L146 pattern — the SEC EDGAR case is the canonical example.

| # | Category | Field count | Prefetch state | Consumer state | SSOT code path |
|---|---|---|---|---|---|
| 1 | Technical Indicators (pivots, momentum, trend, vol, volume, candles) | **~220** | ✅ ACTIVE — Polygon OHLCV cached for ~1,937 tickers | ✅ ACTIVE — `compute_all_signals()` exposes all ~220 fields; Market Analyst toolkit reads Cat 1 | `backtest/signals/technical.py` (26 functions aggregated by `compute_all_signals()`) |
| 2 | Smart Money composite + adjacents (congressional, insider, 13F, news, gov contracts, lobbying, analyst) | **~10** composite/raw labels | ✅ ACTIVE — Quiver Trader bulk endpoints cached (insiders 1M rows, 13Fchanges 500k rows, etc.) Pass 53 Batch 9 v2 | ✅ ACTIVE — `smart_money.insider_signal` / `institutional_signal` / composite wired Pass 53 Batch 13 sub-task 1 | `backtest/data/smart_money.py` |
| 3 | Options Intelligence (IV rank, IV percentile, term structure, P/C ratio, skew, max-pain, dealer gamma) | **~5+ planned** | 🔴 NOT PREFETCHED — Polygon Options + Ortex subscriptions deferred per DEC-506 (point-of-need) | 🔴 NOT WIRED — depends on prefetch | TBD post-subscription |
| 4 | Macro Filters (yield curve, VIX, DXY, FRED 50-series, ALFRED revisions, CFTC COT, event calendar) | **~15** | ✅ ACTIVE — FRED 50-series + ALFRED + CFTC COT cached Pass 53 Batches 6-8 | ✅ ACTIVE — `macro.macro_snapshot()` exposes 12 FRED-derived signals (yield curve / HY OAS / STLFSI4 / RECPROUSM156N / ICSA / WALCL); CFTC dealer positions Pass 53 Batch 13 sub-task 3+5 | `backtest/data/macro.py` |
| 5 | Sentiment Signals (AAII, CNN F&G composite + 7 components, Apewisdom, Wikipedia pageviews, pytrends) | **~5** | ✅ ACTIVE — AAII + CNN F&G composite + 7 sub-components + Apewisdom + Wikipedia pageviews cached (pytrends partial — 200/1937 per Batch 12-b rate-limit) | ✅ ACTIVE — `sentiment.sentiment_snapshot()` exposes all sources Pass 53 Batch 13 sub-task 4+5 | `backtest/data/sentiment.py` |
| 6 | Company / Fundamental Signals (EPS estimates, margin, FCF, insider ownership, share count delta, analyst rating) | **~15 (full set Sprint 4)** | ✅ PARTIAL — Polygon financials cached (1,746 files / 91k filings Batch 4); SEC EDGAR cached (6,056 files Form 4 + 8-K + SC 13D + SC 13G Batch 11 commit `0713f5a0`); Quiver analyst ratings cached | ⏸ PARTIAL — Quiver analyst ratings exposed via `smart_money.get_analyst_data` ✅; Polygon financials parser + SEC EDGAR Form 4/8-K/13D/13G parsers + Fundamentals Analyst toolkit wiring **Sprint 4 PENDING** (gates Layer 1 `buyback_announcements` strategy per DEC-490). **DEC-512 PIT-filing-date audit blocker:** consumer code must use `filing_date` not `period_of_report_date` for as-of cutoff. | `backtest/data/smart_money.py:88-253` (analyst); SEC EDGAR + Polygon financials Sprint 4 build |
| **7 (NEW DEC-511)** | Universe-level signals (cross-sectional ranks, breadth indicators, correlation matrix, factor exposures, sector RS) | **~25-30 fields across 5 modules** | 🔴 NOT STARTED — Sprint pre-Phase-1A blocker per DEC-511 (Pass 53 owner-approved 2026-05-06) | 🔴 NOT WIRED — `OurTechnicalToolkit` (DEC-462) Sprint 7+ consumer; gates 16 strategies + DEC-509 cluster | `backtest/signals/{universe_ranks,breadth,factor_exposures,sector_rs}.py` + `engine/correlation_matrix.py` (all NEW) |
| **DEC-513 P1 additions** | Realized vol (3 horizons) + rolling beta (3 windows) + overnight/intraday split + gap classification + 52w-distance continuous + VIX3M/VVIX + FINRA short interest + universal `signal_age_days` field | **+10 signal categories / ~25 new fields** | 🔴 NOT STARTED — Sprint pre-Phase-1A per DEC-513 (Pass 53 owner-approved 2026-05-06) | 🔴 NOT WIRED — extends Categories 1+4+6 + Category 7 | Distributed across `technical.py` (signals 1,2,5,6,8) + `macro.py` (signal 7) + `data/finra/short_interest.py` NEW (signal 9) + universal schema (signal 10) |
| **Stage 2 total active (current state, prefetch ✅ AND consumer ✅)** | | **~270** | | | |
| **Stage 2 cached but not consumed (prefetch ✅, consumer 🔴/⏸)** | | **+~10-15** (SEC EDGAR + Polygon financials parsing pending) | | | |
| **Sprint pre-Phase-1A target (after DEC-511 + DEC-513 implemented)** | (Category 7 ~25-30 + DEC-513 ~25) | **~315-325** | | | |
| **Stage 3+ planned (prefetch + consumer)** | (incl. Category 3 options + Category 6 full set) | **~340+** | | | |

**Disambiguation (per owner Q3 directive):**
- **"~220 signals"** = Technical category only (Category 1) — used in `EXPLANATION.md` §The signals + `backtest/signals/technical.py` docstring. **Correct in scope.**
- **"~270-280 signals"** = full active Stage 2 backtest across all 6 categories — used in `TRADING_RULES_AND_INFORMATION.md` §2A + `STRATEGY_REGISTER.md`. **Correct in scope.** (Prior "~265-275" wording adjusted upward to "~270-280" to align with Pass 53 Batch 13 wiring of new FRED + CNN + Apewisdom + Wikipedia signals.)
- **"274 signals"** = stale point-in-time count from a specific count run; no current authority. **Retire this number** in favor of the disambiguated values above.

**SSOT:** `TRADING_RULES_AND_INFORMATION.md` §2A Signal Universe Catalogue + §2A.7 totals table

**Dependencies (depends-on):**
- Polygon Stocks Starter cache (Category 1 OHLCV foundation; ~1,937 tickers)
- Quiver Trader cache (Category 2 + Category 6 partial; per DEC-450)
- FRED + ALFRED + CFTC cache (Category 4)
- AAII + CNN F&G + Apewisdom + Wikipedia + pytrends cache (Category 5)
- Polygon news (Category 5 partial; shared with Category 6 fundamentals)
- SEC EDGAR (Category 6 full set; Sprint 4)
- Polygon Options (Category 3; post-subscription per DEC-506)
- Ortex (Category 3 + 6; post-subscription per DEC-506)
- DEC-261 PIT N+1 enforcement — every signal must be PIT-correct
- DEC-298 raw OHLCV cache — gates Category 1
- DEC-440 Polygon news replaces AV+Finnhub — Category 5 + 6 sourcing
- DEC-484 SEC EDGAR replaces FMP — Category 6 sourcing

**Dependencies (depended-on-by):**
- F-002 strategy roster — every strategy reads one or more signal categories
- F-001 agent toolkits — `OurTechnicalToolkit` reads Cat 1, `OurFundamentalsToolkit` reads Cat 2+6, `OurNewsToolkit` reads Cat 5 + Polygon news, `OurRiskToolkit` reads Cat 3+4 (post-subscription) + Cat 4 (now)
- DEC-507 wiring matrix — every category must wire ✅ to its consuming agent

**Docs that must align:**
- `TRADING_RULES_AND_INFORMATION.md` §2A (canonical; Update FIRST)
- `STRATEGY_REGISTER.md` Pass 53 addendum (currently "~265-275" — update to "~270-280")
- `CLAUDE.md` repo structure docstring (currently "274 signal fields" — update to "~220 technical / ~270-280 total" with disambiguation)
- `EXPLANATION.md` §The signals (currently "~220" — keep but add disambiguation note: "~220 technical signals; ~270-280 total signals across 6 categories — see CANONICAL_FACTS.md F-003")
- `backtest/signals/technical.py` docstring (currently "~220" — keep, narrowly scoped to technical)
- `TRADINGAGENTS_DATA_AUDIT.md` (per-agent signal consumption tables)

**Acceptable phrasing variants:** "~220 technical signals (Category 1 only)" • "~270-280 total signals across 6 categories" • "Stage 2 active signal universe ~270-280 (Cat 1 ~220 + Cat 2+4+5+6 ~50)" • "Stage 3+ planned signal universe ~290+ (adds Cat 3 options)". *Not acceptable:* bare "274 signals", "~220 signals" without "(technical only)" qualifier.

**Code-current state:** Category 1 ~220 fields in `compute_all_signals()`; Category 2/4/5 fully wired post-Pass-53-Batch-13; Category 6 partial (analyst from Quiver only; SEC EDGAR Sprint 4 pending); Category 3 deferred to Stage 3+.

---

### F-004 — Exit methods

**Live value (`len(EXIT_STRATEGIES)` 2026-05-25 Batch 357):** **25 exit methods** registered in `backtest/engine/exit_strategies.py::EXIT_STRATEGIES`. All 25 are testable; Phase 1A-β cube mode simulates every method per entry (186 × 25 = 4,650 cells). Single-config-per-strategy via `STRATEGY_EXIT_OVERRIDE` is the future deployment mode for live trading, not the backtest mode.

**Value (planned target):** **20 exit methods + 8 cross-cutting exit DECs (Pass 53 owner-approved 2026-05-06)** = 9 baseline (pre-Pass-52) + 8 new (DEC-067 phases A+B = DEC-432/433) + 3 R-multiple/break-even (DEC-517) = 20 method classes; PLUS 8 cross-cutting decisions (DEC-516 regime-flip exit + DEC-518 earnings-blackout + DEC-519 strategy-to-exit-mapping + DEC-520 signal-reversal precise definition + DEC-521 per-class time stops + DEC-514 backtest fill methodology + DEC-515 Level-6 DD-from-peak breaker + DEC-522-527 P2 backlog).

**Definition:** An "exit method" is a deterministic rule for closing a trade. Strategies are tested against multiple exit methods to find the optimal pairing.

**The 25 live exit methods (live 2026-05-25):**

`atr_trail_1x`, `atr_trail_2x`, `atr_trail_mae_conditional`, `atr_trail_vix_conditional`, `break_even_at_1r`, `breakeven_plus_trail`, `chandelier_3x`, `class_time_stop`, `earnings_blackout`, `fixed_4r_2r`, `hybrid_50pct_target`, `ma_exit_ema9`, `mfe_lockin_trail`, `multi_tier_partial`, `next_pivot_target`, `r_multiple_2r`, `r_multiple_3r`, `regime_flip`, `reverse_signal`, `smc_mitigation_zone`, `time_stop_10d`, `time_stop_20d`, `trailing_10pct`, `trailing_15pct`, `trailing_5pct`.

**The legacy 17-method roster (pre-Batches 282-285; retained for historical context):**

| # | Method | Source DEC | Notes |
|---|---|---|---|
| 1 | Fixed % stop-loss | Baseline | |
| 2 | Fixed % take-profit | Baseline | |
| 3 | Trailing stop (% based) | Baseline | |
| 4 | Time-based exit (max days held) | Baseline | |
| 5 | ATR-based stop-loss | Baseline | |
| 6 | ATR-based trailing stop (atr_trail_1x) | Baseline | **Default per CLAUDE.md** — won 20/29 in Phase 1A v3 archive |
| 7 | Hybrid (50% at target, trail rest) | Baseline | |
| 8 | Volatility breakout exit | Baseline | |
| 9 | Signal-reversal exit | Baseline | |
| 10 | Chandelier exit (3 × ATR off rolling high) | DEC-432 (Phase A) | |
| 11 | Parabolic SAR (PSAR) | DEC-432 (Phase A) | |
| 12 | SuperTrend (ATR-based regime indicator) | DEC-432 (Phase A) | |
| 13 | Volatility-spike-aware ATR exit | DEC-433 (Phase B) | |
| 14 | Multi-timeframe momentum exit | DEC-433 (Phase B) | |
| 15 | Volume-spike exit | DEC-433 (Phase B) | |
| 16 | Volatility regime change exit | DEC-433 (Phase B) | |
| 17 | Time-decay accelerated exit | DEC-433 (Phase B) | |

**SSOT:** `TRADING_RULES_AND_INFORMATION.md` §8.1 + DEC-067 + DEC-432 + DEC-433

**Dependencies (depends-on):**
- F-003 signal universe — exits 13-17 read Cat 1 (vol, volume, momentum) and Cat 4 (regime) signals
- DEC-353 R:R 2:1 minimum — every exit method must produce average R:R ≥ 2.0 across calibration runs

**Dependencies (depended-on-by):**
- F-002 strategy roster — strategies × exit methods = test grid
- F-009 passing criteria — exit method choice affects Sharpe / drawdown / R:R
- Cube dimensions — exit method is one of the cube axes per Phase 1B-α dimensional cube

**Docs that must align:**
- `TRADING_RULES_AND_INFORMATION.md` §8.1 (canonical)
- `CLAUDE.md` Approved Rules table (mentions atr_trail_1x as default)
- `STRATEGY_REGISTER.md` (no specific exit-count claim; OK)

**Acceptable phrasing variants:** **"25 exit methods" (LIVE, code-derived 2026-05-25)** • "17 exit methods" (legacy planned target). *Not acceptable:* "12 exit methods" or "9 exit methods" (both stale; refer to pre-Batch-282-285 counts).

**Code-current state (2026-05-25 Batch 357):** **All 25 methods implemented and registered in `backtest/engine/exit_strategies.py::EXIT_STRATEGIES`.** Test coverage via `backtest/tests/test_exit_strategies.py`. Phase 1A-β cube mode (per `project_phase_1a_beta_is_exit_cube` memory) tests every method against every entry.

---

### F-005 — Universe (5-bucket architecture)

**Value (planned):** **5 buckets: T1a / T1c / T1 ETFs / T2 / T3. Master Dedup ~1,937 unique tickers (Pass 53 implemented). T1b R1000-non-S&P DEFERRED to Stage 3.**

**Definition:** "Universe" = the set of tickers eligible for trading at a given as-of date. PIT-filtered via `(added_date IS NULL OR added_date ≤ as_of) AND (removed_date IS NULL OR removed_date > as_of)`.

**The 5 buckets (Pass 53 baseline):**

| Bucket | Source | Status | Row count | Active count |
|---|---|---|---|---|
| **T1a** S&P 500 (with PIT history) | Wiki Table 1 (one-time exception per L88 with manual verification) | ✅ IMPLEMENTED | 614 | 503 active (+ 111 historical removed during Jan 2020 - May 2026) |
| **T1b** Russell 1000 non-S&P | LSEG / FTSE Russell | ⏸ DEFERRED to Stage 3 (LSEG free tier inadequate; T1a 503 + T1c 101 + ETFs 27 = ~632 instruments already 9× Phase 1A v3 archive baseline; T1b expansion premature for Stage 2 backtest validity) | — | — |
| **T1c** NASDAQ-100 non-S&P | Slickcharts + Wikipedia + Nasdaq IR (3-way cross-check Pass 53) | ✅ IMPLEMENTED | 161 | 101 active (+ 60 historical) |
| **T1 ETFs** Sector + Broad-Market ETFs | DEC-118 / DEC-494 | ✅ IMPLEMENTED | 27 | 27 (always-active reference instruments) |
| **T2** Spinoffs + Recent IPOs | Polygon corp-actions screener (DEC-103) | ✅ IMPLEMENTED Pass 53 | 347 | 297 SCREENER + 50 PIT graduated-name backfill (per BUG-274) |
| **T3** Momentum Top-100 | Polygon grouped-aggs broad-market screener + Jegadeesh-Titman 12-1 (DEC-496) | ✅ IMPLEMENTED Pass 53 | 1,923 period rows / 1,220 unique | 100 per monthly snapshot (72 snapshots × 100 = 7,200 row-snapshots; deduped to 1,220 unique tickers) |
| **Master Dedup** | All buckets union + DEC-504 T3-over-T1 precedence | ✅ IMPLEMENTED Pass 53 | **1,937 unique** | resolved_tier breakdown: T3=993, T1a=501, T2=282, T1c=134, T1ETF=27 |

**T3-over-T1 multi-tier precedence rule (DEC-504 Pass 53 owner directive):**
When a ticker is PIT-active in multiple tiers, **T3 > T2 > T1c > T1a > T1ETF** — the most-specific tier wins for runtime rules application (liquidity floor, history minimum, position sizing, strategy roster, refresh cadence).

**SSOT:** `Backtesting universe/` folder + `backtest/data/universe.py` + DEC-477 / DEC-483 / DEC-494 / DEC-495 / DEC-103 / DEC-104 / DEC-504

**Dependencies (depends-on):**
- B++ schema standardization (Pass 53) — all universe CSVs use `Symbol, Company, Sector, added_date, removed_date` + tier-specific extension columns
- DEC-499 18-classifier sector taxonomy (GICS-11 + Fixed Income, Commodities, Volatility, Broad Market, International, Emerging Markets, Small Cap)
- L88 (no Wikipedia runtime; one-time historical scrape exception with manual verification)
- L89 (universe staleness; quarterly refresh required)
- Polygon prefetch (T2/T3 SCREENER source; gated on Polygon Stocks Starter)

**Dependencies (depended-on-by):**
- F-002 strategy roster — universe size × strategy count = candidate-day grid
- F-009 passing criteria — min trades threshold (≥100 overall, ≥30 per regime) requires sufficient universe
- DEC-505 walk-forward — 4 OOS folds × 1y require universe coverage across the 5-year Polygon Stocks Starter cap window

**Docs that must align:**
- `CLAUDE.md` §Universe Management (5-bucket; T1b deferred)
- `DETAILED_PROJECT_PLAN.md` §3.16 (Sprint 0A universe build)
- `Backtesting universe/` folder filenames (B++ schema; date-range in filename per Pass 53 convention)
- `PROJECT_PLAN.md` (Tier 1 sub-tier definitions per DEC-483)
- `AUDIT_INDEX.md` DEC-477 / DEC-483 / DEC-494 / DEC-495 / DEC-503 / DEC-504

**Acceptable phrasing variants:** "5-bucket universe (T1a/T1c/T1ETF/T2/T3)" • "5-tier universe per DEC-477/483/494/495/103/104" • "Master Dedup 1,937 tickers". *Not acceptable:* "4-tier universe" (stale; pre-DEC-483) • "509 instruments" without scope qualifier (was Phase 1A v3 archive figure).

**Code-current state:** `backtest.data.universe` reads from `Backtesting universe/` folder via `UNIVERSE_DIR`. All tier loaders implemented; `resolve_tier_precedence()` + `get_tier_params()` per DEC-504.

---

### F-006 — Regimes

**Value (planned):** **4 regime types (bull / neutral / bear / crisis) classified per-day. 7 historical regime windows for per-regime verdict in Phase 1B-α. POST Pass 53 owner-approved 2026-05-06 Q1: 6→4 class collapse confirmed (DEC-542 — Bull-Pause/Bear-Pause sub-classes dropped; statistically indistinguishable with our data); training/labeling protocol defined (DEC-539 hand-labeled + cross-validation); validation methodology defined (DEC-541 baseline = SPY-200SMA-sign; 8-input must beat on ≥2 of 3 metrics with p<0.05); probability-vector consumption pattern reconciled with Layer 5 hard tags via Schmitt-trigger binarization (DEC-540 + DEC-546); Stage 2 vs Stage 3+ input parity locked (DEC-543 — freeze inputs at Stage 2 set).**

**Definition:** A "regime" is a market state classification computed from 8-input macro classifier (VIX + SPY-vs-200EMA + 20-day realized vol + yield curve + breadth + HY spread + ICSA + sector dispersion per DEC-106) → EMA-smoothed (DEC-108 + DEC-544 asymmetric: fast-in 5d half-life for Bear/Crisis, slow-out 20d for recovery, 10d default) → posterior-updated by transition matrix (DEC-545 Bayesian integration) → binarized via Schmitt threshold (DEC-546: enter > 0.6, exit < 0.4, min-duration ≥ 5 trading days, crisis-override on VIX > 50). Regimes are computed real-time at each as-of date.

**The 4 regime types:**

| Regime | Classifier | Notes |
|---|---|---|
| **Bull** | SPY > 200 EMA + low realized vol | Long-friendly |
| **Neutral** | Mixed signals | |
| **Bear** | SPY < 200 EMA + moderate realized vol | Short-friendly |
| **Crisis** | High realized vol (top decile) + VIX surge | **Buy-the-dip allowed at 50% size**; flagged `regime=crisis_CRISIS_FLAG` per CLAUDE.md Approved Rules |

**The 7 historical regime windows (used for per-regime verdict in Phase 1B-α):**
Pre-Pass-53 enumeration TBD; the "7 historical regimes" phrase appears in CLAUDE.md §Passing Criteria criterion 10. Specific window dates documented in `improvements.py` regime classifier or related test file. (Action item: enumerate the 7 windows in this fact's SSOT section.)

**Per-regime verdict rule:** A strategy gets PASS / FAIL / INSUFFICIENT_DATA verdict for each of the 7 historical regimes. A strategy that PASSes in crisis but FAILs in bull is deployed only during crisis — this is intentional.

**SSOT:** `backtest/engine/regime_filter.py` (`classify_regime()` function) + DEC-317 (5-day SMA ≥40 enter / <35 exit hysteresis)

**Dependencies (depends-on):**
- F-003 Category 4 macro signals (VIX, SPY 200 EMA, realized vol)
- DEC-298 raw OHLCV cache (foundation for VIX 20-day vol + SPY EMA)

**Dependencies (depended-on-by):**
- F-002 strategy roster — every strategy fires per-regime; regime hard blocks REMOVED per CLAUDE.md (crisis flagged but longs allowed)
- F-009 passing criteria — per-regime verdict matrix; min trades ≥30 per regime
- F-005 universe (Crisis regime longs at 50% size — universe and tier matter for sizing)

**Docs that must align:**
- `CLAUDE.md` §Key Design Decisions (regime classification real-time) + §Approved Rules (crisis regime longs at 50%) + §Passing Criteria (per-regime verdict)
- `TRADING_RULES_AND_INFORMATION.md` §10 Regime Classification
- `EXPLANATION.md` §What is a regime

**Acceptable phrasing variants:** "4 regime types (bull/neutral/bear/crisis)" • "7 historical regime windows for per-regime verdict". *Not acceptable:* "5 regimes" (stale).

**Code-current state:** `classify_regime()` returns one of 4 regime types per as-of date.

---

### F-007 — Test count

**Value (planned):** **All tests must pass (100% pass rate). Current count: ~102 (Pass 53 baseline). Count grows over time as new functionality is added.**

**Definition:** The "test gate" for phase entry requires every test in `backtest/tests/test_unit.py` + `backtest/tests/test_integration.py` (and any newly-added test files like `test_smartmoneyconcepts_unit.py`, `test_smartmoneyconcepts_pit.py` per DEC-508) to pass before code commits / phase advances.

**The 9-layer test pyramid (DEC-503 HARD RULE per CHECKLIST #69):**
Unit + Smoke + Integration + System + Functional + Regression + Data integrity + Performance + Acceptance — every code push must execute all applicable layers; partial coverage is non-compliant.

**SSOT:** Live `pytest` run output (the test count is the ground truth at any moment; no fixed integer)

**Dependencies (depends-on):**
- DEC-503 test pyramid HARD RULE
- CHECKLIST #69 (test pyramid before every code push)

**Dependencies (depended-on-by):**
- Every code commit (git pre-commit hook should run test_unit + test_integration)
- Phase entry gates (per CHECKLIST #69)
- DEC-508 + CHECKLIST #71 (library fork integration mandate Phase A: ≥90% coverage)

**Docs that must align:**
- `CLAUDE.md` (currently "36/36 must pass" — update to "all tests must pass; current count grows over time, run `pytest -q` to verify")
- `CHECKLIST.md` #69 (currently "36/36 must pass" — update similarly)
- `DETAILED_PROJECT_PLAN.md` (currently "36/36 must pass" — update similarly)

**Acceptable phrasing variants:** "all tests must pass" • "100% pass rate required" • "current ~102 tests; count grows; run `pytest -q backtest/tests/` to verify". *Not acceptable:* fixed integer like "36/36" (drifts immediately when tests added).

**Code-current state:** 102 tests passing as of 2026-05-06 (Pass 53 commit `05c7ec01` baseline).

---

### F-008 — Position sizing tiers

**Value (planned):** **5-tier confidence system + LOW (skip) = 6 effective levels.**

**The tiers (per CLAUDE.md Approved Rules):**

| Tier | % of portfolio | Trigger |
|---|---|---|
| EXCEPTIONAL | 5% | ≥5 strategies fire + agent score ≥75 |
| VERY HIGH | 4% | 4 strategies fire + smart money confluence |
| HIGH | 3% | 3 strategies fire |
| MEDIUM-HIGH | 1.5% | 2 strategies fire |
| MEDIUM | 0.75% | 1 strategy fires |
| LOW | (skip) | Below threshold |

**Crisis regime override:** Allowed at 50% of normal size — flagged `regime=crisis_CRISIS_FLAG`.

**Agent tier-shift rule:**
- Agent score ≥75 upgrades one tier
- Agent score ≤40 downgrades one tier

**5-tier rating from TradingAgents PM (DEC-459 supersedes DEC-042):**
Buy / Overweight / Hold / Underweight / Sell → maps to position_size_modifier 1.5x / 1.25x / 1.0x / 0.75x / 0.5x per DEC-062.

**SSOT:** `CLAUDE.md` Approved Rules + DEC-021 3-tier portfolio simplification + DEC-459 agent rating mapping

**Dependencies (depends-on):**
- F-001 agent count — Portfolio Manager rating drives tier-shift
- F-002 strategy roster — number of strategies firing drives initial tier
- F-006 regime — crisis regime applies 50% size scaler

**Dependencies (depended-on-by):**
- Portfolio class implementation (Phase 0.B Sprint 3)
- Phase 1B-α A/B arms (one arm tests rule-based tier; other tests agent-overlay tier)

**Docs that must align:**
- `CLAUDE.md` Approved Rules
- `TRADING_RULES_AND_INFORMATION.md` §5 Strategy Tiers + §7 AgentGateConfig
- `DETAILED_PROJECT_PLAN.md` §2.6 (TradingAgents 5-tier output)

**Acceptable phrasing variants:** "5-tier confidence system" (preliminary tier from strategies) • "5-tier rating" (TradingAgents PM output) • "3-tier portfolio simplification" (DEC-021 — HIGH/MED/LOW for portfolio-level decisions). *Disambiguate "5-tier"* — see also F-013 below.

**Code-current state:** Tier assignment logic in `backtest/engine/improvements.py` (rule-based); agent tier-shift PENDING Phase 1B integration per DEC-459.

---

### F-009 — Passing criteria

**Value (planned):** **9 overall criteria + per-regime verdict (criterion 10) = 10-row gate. Phase 1B-α verdict gate uses 6 strategy validity gates per DEC-426 + DEC-510 (Pass 53 owner Q3 2026-05-06: Deflated Sharpe added as 6th gate).**

**The 9 overall criteria (per CLAUDE.md):**

| # | Criterion | Threshold (standard / high-vol) |
|---|---|---|
| 1 | Win rate | ≥55% / ≥50% |
| 2 | Profit factor | >1.3 / >1.2 |
| 3 | Expected value | >0 |
| 4 | Win/loss ratio | >1.0 |
| 5 | Max drawdown | <20pp / <25pp |
| 6 | Total ROI | >0% |
| 7 | Smart money lift | ≥3pp win rate improvement |
| 8 | Macro correlation | ≥5pp win rate diff |
| 9 | Min trades | ≥100 overall, ≥30 per regime |
| 10 | Per-regime verdict | PASS in ≥1 regime (not universal pass required) |

**The 6 strategy validity gates (Phase 1B-α verdict per DEC-426 + DEC-510):**

| Gate | Threshold | Source |
|---|---|---|
| 1. Sample size | n ≥ 30 trades per cell | TRADING_RULES §3.1 |
| 2. Statistical significance | p < 0.05 Bonferroni-corrected | TRADING_RULES §3.2 / DEC-269 / DEC-080 |
| 3. PSR (Probabilistic Sharpe Ratio) | ≥ 0.95 | TRADING_RULES §3.3 |
| 4. t-statistic | ≥ 3.4 | TRADING_RULES §3.4 |
| 5. R:R ratio | ≥ 2.0 (HARD REJECT below) | DEC-353 / TRADING_RULES §3.5 |
| 6. Deflated Sharpe Ratio (Pass 53 Q3) | ≥ 0.95 confidence | DEC-510 (Bailey-Lopez de Prado 2014) — accounts for skew/kurtosis + multiple-testing trial count |
| 7. Absolute mean-return-per-trade-net-of-cost (NEW Pass 53 adversarial Q2) | ≥ 5 bps per trade after DEC-095 slippage + DEC-573 spread + DEC-574 borrow | DEC-578 — closes "5R:R 12% win-rate gameable" loophole; pairs R:R ratio with absolute effect-size floor |

**SSOT:** `CLAUDE.md` §Passing Criteria + `TRADING_RULES_AND_INFORMATION.md` §3 Strategy Validity Gates + DEC-269 + DEC-426

**Dependencies (depends-on):**
- F-005 universe — min trades requires sufficient ticker coverage
- F-002 strategy roster — each strategy gets evaluated against all 9+5 gates
- F-006 regimes — per-regime verdict requires regime classification

**Dependencies (depended-on-by):**
- Stage 2 → Stage 3 transition (Phase 1B-α verdict gate per DEC-269)
- Strategy retirement criteria (DEC-249/250 decay detection)

**Docs that must align:**
- `CLAUDE.md` §Passing Criteria (canonical 9+per-regime)
- `TRADING_RULES_AND_INFORMATION.md` §3 (5 validity gates) + §1 (Stage transition criteria)
- `DETAILED_PROJECT_PLAN.md` Phase 1B-α verdict gate

**Acceptable phrasing variants:** "9 overall criteria + per-regime verdict" • "9-criterion passing gate" • "5-gate Phase 1B-α validity filter (DEC-426)". *Not acceptable:* mixing the two gate sets without scope qualifier.

**Code-current state:** Implemented in `backtest/results/metrics.py` (9 criteria) + Phase 1B-α 5-gate filter PENDING Sprint 7.

---

### F-010 — Confidence rating tiers (TradingAgents PM output)

**Value (planned):** **5-tier rating from Portfolio Manager (per DEC-481 Option C2): Buy / Overweight / Hold / Underweight / Sell.**

**Definition:** The TradingAgents v0.2.4 Portfolio Manager produces a 5-tier rating in rendered markdown (no extractable numeric `confidence: 0.0-1.0` field — discovered Pass 52 turn 133 via direct verification of TradingAgents source). The `agent_gate.py` markdown parser extracts the rating via deterministic heuristic.

**The mapping to position_size_modifier (per DEC-062):**

| PM Rating | Position size modifier |
|---|---|
| Buy | 1.5x |
| Overweight | 1.25x |
| Hold | 1.0x |
| Underweight | 0.75x |
| Sell | 0.5x |

**SSOT:** DEC-481 Option C2 + DEC-062 + `tradingagents_integration/agent_gate.py` (PROPOSED file per DEC-481)

**Dependencies (depends-on):**
- F-001 agent count — Portfolio Manager is one of the 11 active agents
- TradingAgents v0.2.4 source (markdown rendering format determines parser logic)

**Dependencies (depended-on-by):**
- F-008 position sizing tiers — confidence rating modifies portfolio tier
- DEC-475 RM + Trader cross-check via 5-tier
- DEC-481 AgentGateConfig markdown parser

**Docs that must align:**
- `DETAILED_PROJECT_PLAN.md` §2.6 + Phase 4 description
- `AUDIT_INDEX.md` DEC-481 / DEC-062 / DEC-475

**Acceptable phrasing variants:** "TradingAgents 5-tier rating" • "5-tier rating (Buy/Overweight/Hold/Underweight/Sell)" • "PM 5-tier output". *Always disambiguate from F-005 5-bucket universe and F-008 5-tier confidence system* — see F-013 below.

**Code-current state:** `agent_gate.py` PROPOSED per DEC-481 — parser implementation pending Sprint 7.

---

### F-011 — Custom toolkits (TradingAgents)

**Value (planned):** **5 custom toolkits per DEC-462-466 (Pattern 2 integration).**

**The 5 toolkits:**

| Toolkit | DEC | Consumed by | Reads |
|---|---|---|---|
| OurTechnicalToolkit | DEC-462 | Market Analyst | F-003 Category 1 (~220 technical signals) + Polygon OHLCV |
| OurFundamentalsToolkit | DEC-463 | Fundamentals Analyst | F-003 Category 2 (smart money) + Category 6 (fundamentals) + SEC EDGAR |
| OurNewsToolkit | DEC-464 | News Analyst | F-003 Category 5 (sentiment) + Polygon news |
| OurTraderToolkit | DEC-465 | Trader | All categories (synthesized) |
| OurRiskToolkit | DEC-466 | Risk Debaters (3) | F-003 Category 3 (options; post-subscription) + Category 4 (macro) |

Plus `OurAgentState` schema extension with 7 new fields (DEC-467) and Ortex wiring (DEC-468; post-subscription).

**SSOT:** `TRADINGAGENTS_DATA_AUDIT.md` Wiring matrix §1071 + DEC-462 / DEC-463 / DEC-464 / DEC-465 / DEC-466 / DEC-467 / DEC-468

**Dependencies (depends-on):**
- F-003 signal universe (each toolkit reads one or more categories)
- F-001 agent count (toolkits feed agents; mapping must be ✅ in wiring matrix)
- DEC-507 wiring matrix HARD RULE — each toolkit-to-agent path must be ✅ before Phase 1B entry

**Dependencies (depended-on-by):**
- F-001 agent execution (each agent calls one or more toolkit functions during propagate())
- DEC-481 AgentGateConfig (gate logic reads toolkit outputs)

**Docs that must align:**
- `TRADINGAGENTS_DATA_AUDIT.md` (canonical wiring matrix)
- `DETAILED_PROJECT_PLAN.md` §3.6+ (custom toolkit descriptions)

**Code-current state:** Toolkit class skeletons PROPOSED per DEC-462-466; wiring per Pass 53 Batch 13 (rows 1, 2, 3.a, 3.b, 4, 5 ✅; rows 3, 6-13 PENDING).

---

### F-012 — APIs (Sprint 0A scope)

**Value (planned):** **8-API Stage 2 active set + 2-API post-subscription (Stage 3+) = 10 APIs canonical. Total catalog: 17 APIs across 4 tiers per `API_AUDIT.md`.**

**The 8 Stage 2 active APIs:**

Status is split into **two independent layers** (per owner directive 2026-05-06 — Option B refactor) to disambiguate prefetch readiness from consumer integration:
- **Prefetch state** = is the raw data cached on disk?
- **Consumer state** = is the cached data parsed + exposed via the consuming module + read by the toolkit/agent?

A row can have prefetch ✅ but consumer 🔴 (e.g., SEC EDGAR — 6,056 files cached but parsers + Fundamentals Analyst wiring is Sprint 4 work). This is the L146 pattern. The wiring matrix in [TRADINGAGENTS_DATA_AUDIT.md §1071](TRADINGAGENTS_DATA_AUDIT.md) cross-tracks consumer state per agent.

| API | Subscription | Prefetch state | Consumer state | Cache path |
|---|---|---|---|---|
| Polygon Stocks Starter | Paid | ✅ ACTIVE — 1,937 tickers OHLCV + 1.05M news articles + 1,746 financials + ticker events + dividends + reference cached Pass 53 Batches 2-5 | ✅ ACTIVE — `fetcher.fetch_ohlcv` + `smart_money.get_news_sentiment` + (financials parser pending Sprint 4) wired Pass 53 Batch 13 sub-tasks 2+6 | `data_prefetch/polygon/{aggs,news,financials,events,reference,dividends}/` |
| Quiver Trader | Paid | ✅ ACTIVE — 8 endpoint groups cached: insiders 1M rows, sec13fchanges 500k rows, quivernews, offexchange, etc. Pass 53 Batches 9 v2 + 10 | ✅ ACTIVE — `smart_money.insider_signal` / `institutional_signal` / composite reads bulk feeds Pass 53 Batch 13 sub-task 1 | `data_prefetch/quiver/{insiders,sec13fchanges,quivernews,offexchange,...}/` |
| FRED | Free | ✅ ACTIVE — 50 series cached Pass 53 Batch 6 | ✅ ACTIVE — `macro.macro_snapshot()` exposes 12 FRED-derived signals (yield curve / VIX / DXY / HY OAS / STLFSI4 / RECPROUSM156N / ICSA / WALCL) Pass 53 Batch 13 sub-task 3 | `data_prefetch/fred/observations/` (50 series) |
| ALFRED (revisions) | Free | ✅ ACTIVE — 50/50 series cached 2026-05-06 (~15MB; ~750k vintage observations) | ⚠ PARTIAL — vintage-aware reader pending Sprint 4; signals currently use first-print FRED only | `data_prefetch/alfred/` |
| AAII | Free | ✅ ACTIVE | ✅ ACTIVE — `sentiment.sentiment_snapshot()` exposes AAII bull/bear/neutral | `data_prefetch/aaii/` |
| CNN F&G (composite + 7 components) | Free | ✅ ACTIVE — composite + 7 sub-components cached Pass 53 Batch 7 | ✅ ACTIVE — `sentiment.get_cnn_components()` exposes all 7 components Pass 53 Batch 13 sub-task 4 | `data_prefetch/cnn_fg/` |
| CFTC COT | Free | ✅ ACTIVE — 1,293 weekly TFF reports cached Pass 53 Batch 8 | ✅ ACTIVE — `sentiment.get_cot_report()` exposes dealer_positions_long/short Pass 53 Batch 13 sub-task 5 | `data_prefetch/cftc/cot_emini_sp500.parquet` |
| SEC EDGAR | Free | ✅ ACTIVE — 6,056 files cached Pass 53 Batch 11 (commit `0713f5a0`); Form 4 + 8-K + SC 13D + SC 13G across 4 subfolders | 🔴 NOT WIRED — parsers pending **Sprint 4** (per DEC-484); blocks Layer 1 `buyback_announcements` per DEC-490; no agent currently reads SEC EDGAR cache | `data_prefetch/sec_edgar/{4,8_K,SC_13D,SC_13G}/` (6,056 files) |

**The 2 post-subscription Stage 3+ APIs (per DEC-506 owner directive 2026-05-05):**

| API | Subscription gate | Adds |
|---|---|---|
| Polygon Options Starter | Paid (deferred to point-of-need) | F-003 Category 3 (IV, P/C, skew, max-pain, dealer gamma) |
| Ortex | Paid (deferred to point-of-need) | F-003 Category 3 + Category 6 (short interest, days to cover, utilization) |

**Supplementary free sources (Pass 53 owner-approved):**
- Apewisdom (WSB+r/stocks ticker mentions)
- Wikipedia pageviews
- pytrends (Google Trends search-volume index; partial cache per Batch 12-b)

**HARD CUT NO LIVE API IN STAGE 2 (DEC-497 D4 owner directive 2026-05-05):**
yfinance permitted for one-time SETUP only; not in runtime hot path. All `backtest/data/{fetcher,macro,sentiment,smart_money}.py` migrated to read from `data_prefetch/<api_name>/<endpoint>/...` only (Pass 53 Batch 13 sub-task 6 RESOLVED-IMPLEMENTED 2026-05-06).

**SSOT:** `API_AUDIT.md` (full 17-API catalog) + DEC-440 / DEC-450 / DEC-484 / DEC-497 / DEC-499 / DEC-500 / DEC-506

**Dependencies (depends-on):**
- DEC-497 NO-LIVE-API HARD CUT
- Owner subscription budget (2 paid APIs already; 2 more deferred to point-of-need)

**Dependencies (depended-on-by):**
- F-003 signal universe (every signal reads from one or more APIs)
- F-005 universe (T2/T3 SCREENERs read from Polygon)
- F-001 agent toolkits (each toolkit consumes specific APIs)
- DEC-507 wiring matrix (data path from API to consumer must be ✅)

**Docs that must align:**
- `API_AUDIT.md` (canonical 17-API inventory)
- `TRADING_RULES_AND_INFORMATION.md` §13.12 API endpoint inventory
- `TRADINGAGENTS_DATA_AUDIT.md` Wiring matrix
- `DETAILED_PROJECT_PLAN.md` §3.16 Sprint 0A scope

**Acceptable phrasing variants:** "8-API Stage 2 active set" • "10-API canonical (8 active + 2 post-subscription)" • "17 APIs audited across 4 tiers" (full catalog).

**Code-current state:** All 8 Stage 2 active APIs prefetch ✅ Pass 53. Polygon Options + Ortex DEFERRED.

---

### F-013 — Stages + phases + sprints (program structure)

**Value (planned):** **5 stages program-level + 11 phases within Stages 2-3 (1A through 1D with sub-phases α/β) + sprints as engineering execution units.**

**The 5 stages (program-level):**

| Stage | Description | Status |
|---|---|---|
| 1 | Setup + Infrastructure | DONE |
| 2 | Strategy Validation (current) | ACTIVE — Pass 53 Sprint 0A |
| 3 | Paper Trading Proof | PENDING |
| 4 | Email-approved live trading | PENDING |
| 5 | Full Automation | PENDING |

**The 11 phases within Stages 2-3:**

| Phase | Sprint | Description |
|---|---|---|
| 0.A | Sprint 0A | Multi-API prefetch + 5-bucket universe build + Stage 2 NO-LIVE-API refactor (Pass 53 active) |
| 0.B | Sprint 3 | Portfolio Class |
| 0.C | Sprint 2 | Engine Bug Fixes Tier A |
| 0.D | Sprint 7 | ICT/SMC Fork Integration (smartmoneyconcepts library Phase A/B/C per DEC-508) |
| 0.E | Sprint 6 | Catch-Mechanism Defense + Architecture Hygiene |
| 1A | Sprint 6.5 | Rules-Based + Smart Money Baseline |
| 1A-α | Sprint 6.5-7 | Rules-Only Dimensional Cube + Dashboards |
| 1A-β | Sprint 7 D1 | Production-Scale Validation Run |
| 1B | Sprint 7 | Statistical Methodology + A/B (agent overlay added) |
| 1B-α | Sprint 7-8 | Combined Dimensional Cube + Dashboards |
| 1C+ | Sprint 8 | Strategy Categories Expansion (Layers 2+3 strategies) |

**SSOT:** `DETAILED_PROJECT_PLAN.md` §3 + `TRADING_RULES_AND_INFORMATION.md` §1 + §2

**Disambiguating "tier" / "5-tier" usage across the project:**
The phrase "5-tier" is used in **3 distinct contexts** — always qualify in writing:
1. **F-005 5-bucket universe** (T1a/T1c/T1ETF/T2/T3) — preferred phrasing **"5-bucket"** to avoid overload
2. **F-008 5-tier confidence system** (EXCEPTIONAL/VERY HIGH/HIGH/MEDIUM-HIGH/MEDIUM + LOW skip) — preferred phrasing **"5-tier confidence"** or **"5-tier position sizing"**
3. **F-010 5-tier rating from TradingAgents PM** (Buy/Overweight/Hold/Underweight/Sell) — preferred phrasing **"5-tier rating"** or **"PM 5-tier output"**

**Dependencies (depends-on):** All preceding facts (F-001 to F-012) anchor specific phases.

**Dependencies (depended-on-by):** Cost estimates, sprint planning, progress tracking.

**Docs that must align:**
- `DETAILED_PROJECT_PLAN.md` §3 (canonical phase structure)
- `CLAUDE.md` §Sprint Structure
- `TRADING_RULES_AND_INFORMATION.md` §2 Phase-by-Phase Acceptance Criteria
- `IMPLEMENTATION_READINESS_DASHBOARD.md`

---

## Dependency graph (high-level)

```
                  ┌──────────────────────────────────────────────┐
                  │  F-005 Universe (5 buckets, ~1937 tickers)   │
                  └───────┬──────────────────────────────────────┘
                          │
                          ▼
                  ┌──────────────────────────────────────────────┐
                  │  F-012 APIs (8 active + 2 post-sub)          │
                  └───────┬──────────────────────────────────────┘
                          │
                          ▼
                  ┌──────────────────────────────────────────────┐
                  │  F-003 Signal universe (~270-280 fields)     │
                  └───────┬──────────────────────────────────────┘
                          │
            ┌─────────────┼──────────────┐
            ▼             ▼              ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │ F-002 Strats │ │ F-006    │ │ F-011 5      │
    │ ~108-118+ cl │ │ Regimes  │ │ Custom       │
    │ (100+ tested)│ │ (4 + 7   │ │ Toolkits     │
    └──────┬───────┘ │ historic)│ └──────┬───────┘
           │         └────┬─────┘        │
           │              │              ▼
           │              │      ┌──────────────────┐
           │              │      │ F-001 11 Agents  │
           │              │      │ + 1 Reflection   │
           │              │      └──────┬───────────┘
           │              │             │
           ▼              ▼             ▼
    ┌────────────────────────────────────────────┐
    │ F-009 Passing criteria (9 + per-regime)    │
    │ + F-010 PM 5-tier rating                   │
    │ + F-008 5-tier confidence                  │
    │ + F-004 25 exit methods (LIVE 2026-05-25)  │
    └────────────────┬───────────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────────────┐
    │ F-007 All tests pass (2,536 live 2026-05-25)│
    │ + F-013 11 phases across 5 stages          │
    └────────────────────────────────────────────┘
```

**Read this as:** Universe (F-005) defines what's tradable. APIs (F-012) populate the data layer. Signals (F-003) compute from data. Strategies (F-002) consume signals. Regimes (F-006) classify time. Toolkits (F-011) wrap signals for agents. Agents (F-001) overlay strategies. Passing criteria (F-009) gate everything. Tests (F-007) validate everything. Phases (F-013) sequence the work.

---

## Alignment test (executable enforcement)

**File:** `backtest/tests/test_canonical_facts_alignment.py` (created alongside this doc)
**What it does:** For each fact F-NNN above, the test reads the doc(s) listed under "Docs that must align" and asserts the stated value matches the canonical value in this file. If a doc references the fact but uses a non-acceptable phrasing variant, the test fails. CI runs this on every commit.

**Drift fails the test.** This is the structural mechanism that makes alignment automatic, not aspirational.

**False-positive escape hatch:** If a doc *correctly* uses a scope-narrow value (e.g., `EXPLANATION.md` saying "~220 technical signals" — correct for Category 1 only), it must be annotated with a `<!-- canonical-fact-scope: F-003 Category 1 -->` HTML comment to tell the test "this scope is intentional". Bare counts without annotation always fail.

---

## Update protocol (write order)

When a fact changes:

1. **Update CANONICAL_FACTS.md FIRST.** Change the value in this file. Update SSOT citation. Update dependencies.
2. **Run alignment test.** `pytest backtest/tests/test_canonical_facts_alignment.py -v`. The test will identify every drifted doc.
3. **Update drifted docs.** Edit each flagged doc to match the new canonical value (or add scope annotation if the value is correct-in-scope).
4. **Re-run alignment test.** Must pass before commit.
5. **Commit atomically.** All updates in one commit. Per CHECKLIST #67/#67.b doc-sync-within-turn rule.

**Anti-pattern (forbidden):** Updating one doc without updating CANONICAL_FACTS.md. This silently restarts the drift cycle.

---

### F-014 — Live dashboards (GitHub Pages, Pass 53 Day 9+ 2026-05-15)

**Three live dashboards** hosted at `https://jeetmehta1991.github.io/stock-picks-app/` via GitHub Pages workflow `.github/workflows/deploy_pages.yml`.

| Dashboard | URL slug | Source builder | Trigger |
|---|---|---|---|
| Landing page | `/` | `index.html` (static, manual edit) | — |
| Sprint 0A API endpoint coverage | `/dashboard_sprint0a/` | `scripts/build_dashboard_sprint0a.py` | scans `data_prefetch/` + parses `API_ENDPOINT_INVENTORY.md` |
| Stage 2 Decisions + Bugs registry | `/dashboard_stage_2/` | `scripts/build_dashboard_stage_2.py` | parses `AUDIT_INDEX.md` + `BUG_REGISTER.md` + git + `verification_matrix.json` |
| Phase 1A Trade Summary | `/dashboard_phase_1a/` | `scripts/build_dashboard_phase_1a.py` | reads `output_v2/*` after backtest |

**Phase 1A dashboard 12-tab structure (per DETAILED_PROJECT_PLAN.md §7.6 Sprint 6.5 spec, delivered early Batch 177):**
1. Overview — portfolio KPIs (return, Sharpe, DD, win-rate, PF, heat)
2. Strategies — per-strategy ranking with 9-criteria PASS/FAIL pills
3. Regime — per-(strategy × regime) verdict heatmap
4. MAE/MFE — distribution buckets
5. Equity — equity curve chart (Chart.js line plot)
6. Walk-fwd — improvements + rolling Sharpe + bootstrap CI + stress
7. Smart-money — exit performance with/without smart-money signal
8. Sector — outcomes by sector + concentration
9. Skipped — rejected candidates with reason
10. CircuitBreakers — activation log + per-trade outcomes when active
11. Exits — 17 methods × N strategies + per-dimension breakdowns
12. Trades — trade-log preview (first 10K rows)

Plus Raw JSON debug tab.

**Dependencies:**
- F-002 strategy roster + F-004 exit methods + F-006 regimes + F-009 passing criteria all surface in Phase 1A dashboard tabs
- F-007 test count includes dashboard-builder smoke + integration tests
- F-012 APIs all surface in Sprint 0A dashboard catalog

**Consequences if value drifts:**
- URL slug change → owner-facing dashboards 404
- Deploy workflow `paths` filter must list `dashboard_*/**` for trigger fire
- Builder scripts must be re-run after backtest refresh to update payload

**Status (2026-05-15 Batches 175 + 177-178):**
- All 3 dashboards verified live (HTTP 200) at production URL
- `dashboard_phase_1a` data.js = 1.9 MB; index.html = 11.7 KB
- Builders idempotent — re-running after artifact refresh updates payload deterministically
- Matrix scope (`bugs_all`/`decisions_all`) emitted by stage_2 builder so verification matrix scope is stable (no oscillation per Batch 171 / L151)

---

## Cross-references

- `CLAUDE.md` HARD RULE #67/#67.b — per-turn doc sync (this file is the doc-sync target)
- `CHECKLIST.md` #43 — cross-doc consistency (this file makes #43 enforceable)
- `CHECKLIST.md` #69 — test pyramid (alignment test joins the pyramid as Layer 7 data integrity)
- `LEARNINGS.md` L143 — historical preservation (this file describes PLANNED state; historical narratives in AUDIT.md untouched)
- `AUDIT.md` Pass 53 11-agent correction narrative — root-cause analysis that motivated this file
- DEC list affecting facts: DEC-021 / DEC-042 / DEC-045 / DEC-057 / DEC-062 / DEC-067 / DEC-103 / DEC-104 / DEC-118 / DEC-211 / DEC-259 / DEC-261 / DEC-269 / DEC-298 / DEC-303 / DEC-317 / DEC-321 / DEC-332 / DEC-353 / DEC-355-362 / DEC-364 / DEC-366 / DEC-367-371 / DEC-380 / DEC-407 / DEC-426 / DEC-432-433 / DEC-440 / DEC-443 / DEC-450 / DEC-453-455 / DEC-459 / DEC-462-468 / DEC-475 / DEC-477 / DEC-481 / DEC-483 / DEC-484-485 / DEC-490-508

---

*Per CHECKLIST #1 (owner Q1+Q2+Q3 approved); #25 (6 drifts surfaced before this fix); #43 (this file IS the framework #43 was missing); #45 (this statement); #51 (scope strict — alignment + structural fix only); #58 (atomic codification — 13 facts in one doc); #66.b (INPUT/OUTPUT/FLOW: this file is INPUT for alignment test → OUTPUT is doc consistency); #67/#67.b (will commit this turn).*
