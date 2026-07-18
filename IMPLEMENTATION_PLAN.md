<!-- Source: per CHECKLIST #77 canonical-source; Council 287 B1233 2026-07-07 doc-sync sweep -->

<!-- 🟢 COUNCIL 278-287 SYNC BANNER (B1233 2026-07-07) — READ FIRST BEFORE THIS DOC -->
> **Doc-sync status:** This document may contain references stale as of 2026-06-27 or earlier. The current state below overrides any stale references in the body until the next full-rewrite.
>
> **Current canonical values (as of 2026-07-07 B1231):**
> - `len(ALL_STRATEGIES) = 219` (was 220 pre-B1189 DELETE of dxy_headwind_multinational_short; was 221 pre-B874)
> - `STRATEGIES_DISABLED_MISSING_PRODUCER = set()` (was `{dxy_headwind_multinational_short}` pre-B1189)
> - Active strategies for Phase 1A-β cube: 219; cube cells 219×26 = 5,694
> - Test count: **880 passed, 2 skipped** on `test_unit.py + test_integration.py`
> - **CHECKLIST items:** #1–#157 (added #151-#157 in Councils 279-285)
> - **LEARNINGS lessons:** through L209 (added L197-L202 in Councils 279-285)
> - **Latest batch:** B1310 (Council 342)
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

# IMPLEMENTATION_PLAN.md — Post-Batch-225 pending + backlog implementation

> **B1028 R5-LAUNCH UPDATE 2026-06-27:** R5 LAUNCHED on AWS i-0940a53c75d049381 (Master 1929 ops × 4y). All 15/15 PATH §13.7 launch gates READY pre-B1028. Track post-launch state in CLAUDE.md banner + EXECUTION_QUEUE.md. 220 strategies / 217 active / 12 EXPLORATORY / 3 DISABLED. 39 councils 79-121. Memory rule: `feedback_readiness_audit_must_verify_universe_scope`.
>
> **B909 SUPERSEDED-BY-NOTICE (2026-06-19 per owner directive Dec-2 update in place):** This doc was authored Batch 234 (2026-05-18) for post-B225 implementation detail at T0-T7 track granularity. **Multiple supersession layers added since:**
> - **Architecture + cost + universe + timeframe canonical table:** [STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md](STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md) (existing pointer from B240; preserved)
> - **Phase 1B-α path canonical (B888 Council 14 + B891 DEC-611-614 + B894 standalone):** [PATH_TO_PHASE_1B_ALPHA.md](PATH_TO_PHASE_1B_ALPHA.md)
> - **R5 readiness + DEFER tickets:** [EXECUTION_QUEUE.md](EXECUTION_QUEUE.md) (B895 forward; live tracker)
> - **Live decision registry:** [AUDIT_INDEX.md](AUDIT_INDEX.md) (538 DECs incl. DEC-611-614 B890-B891)
>
> T0-T7 track implementation detail in body below remains canonical for that scope (specific track-by-track Sprint 0A → Stage 2 work). Forward-looking work post-2026-05-29 uses the above-pointed canonical docs.

**Authored:** 2026-05-18 (Pass 53 Day 9+ Batch 234)
**Updated:** 2026-05-19 (Batch 240) — superseded by [STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md](STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md) for architecture + cost + universe + timeframe canonical table. This doc remains canonical for T0-T7 track implementation detail.

**Trigger:** Batch 225 5-batch parallel rerun lands (5 procs in flight, ~1.3-1.4 GB RAM each, ~3-4 hrs remaining).
**Owner state:** sleeping. Autonomous execution mandate for T0 + T5b + T1 + T2.
**Owner gates to clear tomorrow morning (2026-05-19):** T3 PROPOSED triage + T4 OPEN-INV triage + T5a FinBERT decision (default: defer per owner concur).

---

## ARCHITECTURE CLARIFICATION (Pass 53 Day 9+ 2026-05-19 owner directive)

The original "Phase 1B-α = full-universe agent overlay run" framing is **WRONG**. Corrected architecture:

1. **Phase 1A-α** = T1a sanity check (in-flight, ~24h compute)
2. **Phase 1A-β** = exhaustive search across ALL strategies × ALL tickers × FULL timeframe → produces **winning (strategy × exit × regime) combos**
3. **Phase 1B-α** = agents applied ONLY to winning combos from 1A-β → tests whether agents optimize ROI of already-validated baselines
4. **A/B framework** (DEC-131/207-216) operates on winners-only subset, NOT arbitrary universe pilot

**Implications:**
- Phase 1A-β scope is non-negotiable: full 1937 tkrs × ~180 strategies × 4y
- Phase 1B-α actual cost likely **~$50-150** (winners-only), not $300 (full universe)
- $300 budget pre-approved as ceiling per owner 2026-05-19
- Phase 1B-α prereq is the 1A-β winners list

**Canonical:** [STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md](STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md) summary table.

---

## Owner decisions captured this session

| # | Question | Owner call (2026-05-18) | Action |
|---|---|---|---|
| 1 | FinBERT scorer install (~2 GB torch + transformers) | **DEFER** — agree with rec; revisit only if rule-based news strategies prove signal in Phase 1A-β rerun | T5a parked; rule-based [news_sentiment.py](backtest/signals/news_sentiment.py) remains canonical |
| 2 | Cointegrated-pairs precompute (T1a, monthly PIT) | **APPROVE** — run during T0→T1 idle window | T5b runs after T0 merge, before T1 wiring |
| 3 | T3 PROPOSED triage + T4 OPEN-INV triage | **TOMORROW MORNING** (2026-05-19) | No autonomous triage; surface clean queue then |
| 4 | T0 must include Phase 1A 12-tab alpha dashboard refresh | **CONFIRMED** | T0 now runs both `build_dashboard_stage_2.py` AND `build_dashboard_phase_1a.py` |

---

## INV comprehensive review (this session, autonomous)

Owner directive 2026-05-18: "Investigation items appear to be outdated and do a comprehensive review."

Cross-referenced all 53 INV entries against canonical paths + adjacent RESOLVED entries. Reclassified 7 stale OPEN entries based on empirical verification:

| INV | Old status | New status | Evidence (verified 2026-05-18) |
|---|---|---|---|
| INV-002 | open | RESOLVED-OBSOLETE | `dividends_full/` = 10,985 files; `splits_full/` = 18,911 (legacy path obsoleted by INV-017) |
| INV-003 | open | RESOLVED-OBSOLETE | quiver congressional 1942, institutional 1942 (per INV-023 fix) |
| INV-004 | open | RESOLVED-OBSOLETE | `reference_extended/` = 1687 files (87% of 1937; per INV-030) |
| INV-006 | open | WONTFIX | wikipedia dir has 1432 files but spot-check empty; canonical source `data_prefetch/wikipedia/` separate (1414 populated); INV-021 may sweep later |
| INV-007 | open | RESOLVED-OBSOLETE | institutional now 1942 (per INV-023); per-ticker emptiness for some tickers is empirical API reality |
| INV-013 | open | WONTFIX | per body's own leave-as-is recommendation; converges with INV-006 |
| INV-043 | RESOLVING THIS COMMIT | RESOLVED-CONFIRMED | `dividends_full/PRN_.parquet` + `ipos_full/CON_.parquet` verified on disk |

**Remaining genuinely-open INVs (22):** INV-005, 008, 009, 010, 014, 015, 018, 019, 020, 021, 022, 024, 025, 026, 028, 029, 031, 032, 033, 036, 037, 039, 040, 042, 044, 047, 048, 050, 051, 052, 053. Owner triage tomorrow morning (T4).

**Stage 2-relevant subset (priority for tomorrow):**
- **INV-014** — `trade_log.parquet` silent CSV-only degrade on `--no-agents` (Phase 1A baseline IS no-agents)
- **INV-050** — walk-forward folds suppressed under `--no-git` (Phase 1A baseline used `--no-git`)
- **INV-051** — regime-stratified CV stratifier collapses to neutral-only (affects DEC-422 cube populator)
- **INV-052** — dispersion CB z-score 379 outlier (numerical edge case, may fire more at 1937-tkr scale)
- **INV-053** — entry funnel rejects 99.87% of candidates (portfolio-cap dominance; may need tier-aware scaling for 1A-β)

---

## Track plan

### Track T0 — Post-rerun close-out (autonomous, blocks all else)
**Trigger:** all 5/5 batches in Batch 225 rerun complete + last_run.txt freshness verified.

1. Merge 5 batch outputs → `output_v2/` via [scripts/merge_batch_outputs.py](scripts/merge_batch_outputs.py)
2. Refresh DSR / PBO / Bonferroni gates on merged trade_log (M=86 post Batch 218 dead-evidence deprecation)
3. Regenerate [VERIFICATION_MATRIX.md](VERIFICATION_MATRIX.md) via `scripts/build_verification_matrix.py` (coverage-driven, replaces wired=yes grep heuristic)
4. **Run `scripts/build_dashboard_stage_2.py`** — Dashboard 2 (decisions / bugs / INVs registry)
5. **Run `scripts/build_dashboard_phase_1a.py`** — Dashboard 3 (Phase 1A 12-tab alpha analysis, owner-confirmed scope addition 2026-05-18)
6. Sanity check both dashboards' `last_run.txt` timestamps post-regen
7. Commit + push: `Batch 234.0 (T0 close-out): merge + DSR/PBO/Bonferroni + VERIFICATION_MATRIX + both dashboards refreshed`
8. Surface verdict to owner: rules-only Sharpe value + per-regime PASS counts

**Effort:** ~1 hour serial.

---

### Track T5b — Cointegrated-pairs precompute (autonomous, owner-approved)
**Runs:** during T0→T1 idle window (after T0 push, before T1 wiring begins).

1. Author `scripts/precompute_cointegrated_pairs.py`:
   - Input: T1a active membership at monthly snapshots 2020-01 → 2026-05 (77 snapshots)
   - For each snapshot: load all active T1a tickers from `Backtesting universe/Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv` (B++ schema)
   - Pull 252-day close history per ticker from `data_prefetch/polygon/ohlcv_daily/{TICKER}.parquet`
   - Run `find_cointegrated_pairs(closes, significance=0.05, min_half_life=5, max_half_life=30, max_pairs=100)` from [pairs_trading.py](backtest/signals/pairs_trading.py)
   - Write per-snapshot parquet: `data_prefetch/derived/cointegrated_pairs_t1a/{YYYY-MM-01}.parquet`
   - Schema: `as_of_date, ticker_a, ticker_b, hedge_ratio, intercept, half_life, p_value`
2. Index file: `data_prefetch/derived/cointegrated_pairs_t1a/_index.parquet` (snapshot count + pair counts)
3. Pyramid (per-addressal full 13-tier per CHECKLIST #69):
   - Unit (existing `test_pairs_trading.py`)
   - Smoke (1 snapshot 2024-01 + 30 T1a names)
   - Integration (3 snapshots: 2020-01, 2023-01, 2026-05)
   - System (1937 tkr cache reads, no crashes)
   - Functional (verify hedge_ratio + half_life ranges sane)
   - Regression (existing pairs unit tests)
   - Data integrity (no NaN cointegration p-values; half-life in [5, 30])
   - Performance (~30-60 min per snapshot × 77 = ~40-80h... too long; reduce scope)
   - Acceptance: owner reviews output count + sample pair list next morning

**Scope adjustment:** 77 monthly snapshots × O(N²) = 9.7M regressions is excessive. **Revised plan:**
- **Quarterly grain instead of monthly:** 26 quarterly snapshots (Q1-Q4 2020 → Q2 2026). ~26 × 126K = 3.3M regressions. ~10-15h wallclock.
- **T1a 503 active limit** (not 614 historical), excluding tickers with <252 days history at as_of.
- Run in background; T1 wiring proceeds in parallel using current Batch 225 idle CPU once it lands.

**Output:** `data_prefetch/derived/cointegrated_pairs_t1a/{YYYY-Q[1-4]}.parquet` (26 files), `_index.parquet`.

**Effort:** ~10-15h wallclock background; ~2h authoring + pyramid.

---

### Track T1 — Register 5 parallel-safe signal modules (autonomous, sequential)
Each gets its own commit + full 13-tier pyramid per CHECKLIST #69 (no subsetting, per feedback_pyramid_full_13_tiers_mandatory.md).

#### T1.1 — pairs_trading (commit `Batch 235`)
- **Engine wire:** [screener.py](backtest/signals/screener.py) reads quarterly precomputed parquet → for each (ticker_a, ticker_b) cointegrated pair where ticker_a == current ticker, evaluate `pair_zscore()` from latest closes. If |z| > 2.0 → entry signal long if z<-2 + short if z>2.
- **Strategies registered:** `PairsMeanReversionLong` (z<-2 entry, exit z>=0 or stop), `PairsMeanReversionShort` (z>2 entry, exit z<=0 or stop). 2 classes.
- **Regime affinity:** [regime_selector.py](backtest/engine/regime_selector.py) — neutral + low-vol regimes (mean reversion fails in trending markets).
- **Pyramid 13-tier:** smoke (5 tkrs) → unit → contract → integration → system → functional → regression → data integrity → performance → acceptance → e2e Phase 1A baseline microsmoke → dashboard regen → walk-forward fold.

#### T1.2 — news_sentiment (commit `Batch 236`)
- **Engine wire:** [screener.py](backtest/signals/screener.py) calls `compute_news_sentiment_signals(ticker, as_of, lookback_days=7)` per evaluation.
- **Strategies registered:** `NewsSentimentLong` (sentiment_mean > +0.3 + article_count >= 3), `NewsSentimentShiftLong` (sentiment_shift > +0.4 in 7d window). 2 classes.
- **Toolkit wiring matrix (CHECKLIST #70):** add row Agent×Polygon news cache×screener.py×Verified to [TRADINGAGENTS_DATA_AUDIT.md](TRADINGAGENTS_DATA_AUDIT.md).
- **Regime affinity:** bull + neutral (sentiment momentum tracks risk-on regimes; sentiment fails in crisis where bad-news cluster overwhelms signal).
- **Pyramid 13-tier:** as T1.1.

#### T1.3 — calendar_effects (commit `Batch 237`)
- **Engine wire:** [backtest.py](backtest/engine/backtest.py) universe loop, day-level cached (`compute_calendar_signals(as_of)` returns universe-wide dict; cache once per day).
- **Strategies registered:** `TOTMLong` (is_totm_window + bull/neutral regime), `PreHolidayLong` (is_pre_holiday + dow != 0), `JanuaryEffectSmallCap` (is_january + T2/T3 + cap_band=small), `HalloweenSeasonalLong` (is_halloween_period + regime != crisis). 4 classes.
- **Regime affinity:** all except crisis.
- **Pyramid 13-tier:** as T1.1.

#### T1.4 — cross_asset (commit `Batch 238`)
- **Engine wire:** [backtest.py](backtest/engine/backtest.py) day-level cached (`compute_cross_asset_signals(as_of)` returns universe-wide dict; cache once per day).
- **Strategies registered:** `RiskOffBondEquity` (short equity when risk_off_regime_bond_signal=True), `VIXBackwardation` (long volatility-tolerant names when vix_term_backwardation=True), `SectorRotationDefensive` (long defensive sectors when defensive_leadership=True), `GoldSilverRiskOff` (defensive overlay), `DXYHeadwindMultinational` (short SPY-multinational names when usd_strengthening=True). 5 classes.
- **Regime affinity:** crisis + bear (risk-off signals fire most in stress regimes).
- **Pyramid 13-tier:** as T1.1.

#### T1.5 — volume_profile (commit `Batch 239`)
- **Engine wire:** [screener.py](backtest/signals/screener.py) per-ticker call (`compute_volume_profile(df, lookback_days=60)` per evaluation; cache 1-day per ticker).
- **Strategies registered:** `POCMagnet` (vp_close_near_poc_pct < 0.02 + bullish bias setup), `ValueAreaBreakoutLong` (vp_above_value_area=True + volume confirmation), `NakedPOCRetestLong` (vp_close_near_poc_pct < 0.01 + naked POC from `compute_period_pocs`). 3 classes.
- **Regime affinity:** bull + neutral (POC magnetism works in trending + range; breaks in crisis).
- **Pyramid 13-tier:** as T1.1.

**T1 total:** 5 commits, 16 new strategies registered, 5 × full 13-tier pyramids. Effort ~3-4 hours total.

---

### Track T2 — 24 PARTIAL-IMPL-HELPER-ONLY autonomous wiring (per-DEC pyramid)
Per [feedback_per_dec_wiring_autonomous.md](C:/Users/jeetm/.claude/projects/c--Users-jeetm-Github-stock-picks-app/memory/feedback_per_dec_wiring_autonomous.md): autonomous standing approval, full 13-tier pyramid per DEC, high-impact engine paths first.

**Queue (priority order, refreshed against current AUDIT_INDEX.md):**
1. DEC-062 (exit logic) — highest blast radius
2. DEC-138 (Batch 69 owner-caught)
3. DEC-216 (Batch 69 owner-caught)
4. DEC-230 (Batch 69 owner-caught)
5. DEC-231 (Batch 69 owner-caught)
6. DEC-234 (Batch 69 owner-caught)
7. DEC-246 (Batch 69 owner-caught)
8. DEC-365 (Batch 69 owner-caught)
9-24. Remaining 16 in category order (technical → fundamental → smart-money → calendar → cross-asset)

**Per-DEC unit of work:**
- Wire helper into engine call-path (specific file + line per DEC body)
- Full 13-tier pyramid:
  - Unit (helper test)
  - Smoke (1 tkr 30 days)
  - Contract (engine API surface)
  - Integration (helper × engine)
  - System (10 tkrs 1 yr)
  - Functional (signal value sanity)
  - Regression (existing test suite no break)
  - Data integrity (cache reads correct)
  - Performance (no >5% degradation)
  - Acceptance (owner-spec match)
  - E2E (full Phase 1A microsmoke 5 tkrs 90 days)
  - Dashboard regen (Dashboard 2 verification matrix updates)
  - Walk-forward (1 fold)
- Commit + push (per CHECKLIST #75 + #78)
- AUDIT_INDEX status flip: PARTIAL-IMPL-HELPER-ONLY → RESOLVED-IMPLEMENTED

**Effort:** ~24 × 30-45 min = 12-18 hours autonomous.

**Stop condition:** queue empty OR owner interrupt OR pyramid failure that requires owner direction.

---

### Track T3 — 4 PROPOSED backlog items (OWNER GATE, tomorrow morning)
[AUDIT_BACKLOG.md](AUDIT_BACKLOG.md) entries marked *"Pre-DEC; awaiting owner approval (legacy items only — Pass 53 review cycle CLOSED per DEC-589)"*.

**Tomorrow's deliverable:** walk through each with recommendation + tradeoff. Owner gives approve / reject / defer per item.

---

### Track T4 — 20 OPEN-INV triage (OWNER GATE, tomorrow morning)
22 remaining genuinely-open INVs post-comprehensive-review.

**Tomorrow's deliverable:** ordered triage list with recommendation per INV (defer / wontfix / convert to DEC / promote to BUG). Stage 2-relevant subset first (INV-014, INV-050, INV-051, INV-052, INV-053 + the 5 prefetch-gap items INV-019/020/021/022/024-026/028-029/031-033 grouped).

---

### Track T5a — FinBERT (DEFERRED per owner concur 2026-05-18)
Parked. Revisit only if rule-based [news_sentiment.py](backtest/signals/news_sentiment.py) strategies produce 1-3 validated strategies in Phase 1A-β rerun. If zero validated, FinBERT unlikely to help. Phase A/B/C gate (CHECKLIST #71) applies when activated.

---

### Track T6 — 163 RESOLVED-DECIDED build queue (post-T2)
Already-approved entries from [AUDIT_INDEX.md](AUDIT_INDEX.md) awaiting implementation. Sort by `stage_scope` tag; pull Stage 2 subset into T2 cadence after the 24 PARTIAL-IMPL items clear.

---

### Track T7 — Stage 2 final close-out (gated by T0-T6 completion)
1. Final 5-batch rerun with all wired strategies (T1 + T2 outputs) + cointegrated-pairs consumed (T5b output)
2. Final DSR / PBO / Bonferroni gate evaluation
3. Final per-regime verdict matrix
4. Owner gate: Phase 1A-α PASS verdict → Phase 1B-α $300 Haiku commit

---

## Autonomous execution log

| Time | Event | Status |
|---|---|---|
| 2026-05-18 ~17:00 PT | Owner went to sleep; autonomous mandate active | START |
| 2026-05-18 23:33 PT | Doc commit `9b261b3f9` pushed (INV reclassification + IMPLEMENTATION_PLAN.md) | DONE |
| 2026-05-19 07:17 AM | Batch 225 progress check: ~15% complete at 17h wallclock; projection 3-5 more days | DIAGNOSTIC |
| 2026-05-19 07:25 AM | 15-min diagnostic: 5 procs 100% CPU continuously, no stall but real workload (`ALL_STRATEGIES = 123 classes` × 1937 tkrs × 1044 days) | DIAGNOSED |
| 2026-05-19 07:30 AM | Owner approved Option B: abort + T1a-only relaunch | DECISION |
| 2026-05-19 07:32 AM | 5 Python procs killed; diagnostic checkpoints preserved at `output_phase_1a_beta_abort_diagnostic_20260519/` | ABORTED |
| 2026-05-19 07:33 AM | T1a batch splits generated: 642 tkrs (614 T1a + 28 ETFs) across 5 batches of 126-129 each | PREPARED |
| 2026-05-19 07:34 AM | 5 T1a-only batches launched (`output_phase_1a_alpha_batch_[1-5]/`) — task IDs bkp9bijst / bemdusrer / b0fmc612x / bfdq2t3nv / baovho27r | RUNNING |
| TBD | T1a 5/5 complete | PENDING |
| TBD | T0 close-out + Dashboards 2+3 refresh | PENDING |
| TBD | T5b precompute (background; may overlap T1) | PENDING |
| 2026-05-27 (Batch 396 audit) | T1.1 pairs_trading wired + engine-consumed | SHIPPED -- `pair_zscore_signed` consumed at [screener.py:3155-3174](backtest/signals/screener.py#L3155-L3174) by `strat_pairs_mean_reversion_long`/`_short` |
| 2026-05-27 (Batch 396 audit) | T1.2 news_sentiment wired + engine-consumed | SHIPPED -- `news_sentiment_shift` consumed at [screener.py:3217-3227](backtest/signals/screener.py#L3217-L3227); strategy registered at line 3503 |
| 2026-05-27 (Batch 396 audit) | T1.3 calendar_effects wired + engine-consumed | SHIPPED -- `compute_calendar_signals` imported + called at [screener.py:3024-3025](backtest/signals/screener.py#L3024-L3025) (day-level cache) |
| 2026-05-27 (Batch 396 audit) | T1.4 cross_asset wired + engine-consumed | SHIPPED -- `compute_cross_asset_signals` called at [screener.py:3031-3032](backtest/signals/screener.py#L3031-L3032); `risk_off_regime_bond_signal` consumed at line 3087 |
| 2026-05-27 (Batch 396 audit) | T1.5 volume_profile wired + engine-consumed | SHIPPED -- `compute_volume_profile` called at [screener.py:3916-3917](backtest/signals/screener.py#L3916-L3917); `vp_close_near_poc_pct` consumed at lines 2971-2977 |
| 2026-05-26 (Batch 374) | T2 priority DECs partial: DEC-230 + DEC-231 + DEC-234 + DEC-246 | SHIPPED -- engine-consumed via `backtest/util/structured_logger.py` import in `regime_filter.py`; `quant_audit.py` Sharpe consumed by `cube_populator.py:138` + `ab_orchestrator.py:89` + `seven_gate_verdict.py:10` |
| Batches 398-401 (queued autonomous) | T2 remaining: DEC-062 + DEC-138 + DEC-216 + DEC-365 engine wiring | IN-FLIGHT (per-DEC autonomous wiring with full 13-tier pyramid each) |

### Scope change 2026-05-19 (Batch 235)

**Why:** Batch 225 5-batch Phase 1A-β rerun (1937 tkrs, all strategies) projected ~3-5 more days at observed rate after 17h wallclock with only ~15% progress. Root cause: 123-class strategy ensemble (post Batches 217-233 expansion) × 1937 tkrs × 1044 days = ~13M signal-evals per simulated day.

**Decision (owner-approved Option B 2026-05-19 07:30 AM):**
- Abort 5-batch Phase 1A-β rerun (sunk cost: ~84 CPU-hours across 5 procs; killed cleanly)
- Preserve diagnostic checkpoints (5 trade_log_checkpoint.csv files at `output_phase_1a_beta_abort_diagnostic_20260519/`)
- Relaunch as **Phase 1A-α** (T1a S&P 500 backbone + T1 ETFs = 642 instruments)
- Strategy ensemble unchanged (123 classes — owner did not approve reduction)
- New per-batch outputs at `output_phase_1a_alpha_batch_[1-5]/`
- Expected wallclock: ~5-12h based on 33% of per-day load × parallel-5

**Phase 1A-α gate** (per CLAUDE.md Phase 1A-α definition): rules-only Sharpe ≥ 0.7 OOS at S&P 500 backbone → owner commits $300 Phase 1B-α Haiku budget.

**T2/T3 small-cap coverage** (the Phase 1A-β scope) deferred to follow-on rerun after T1a verdict lands. Sunk-cost is gone either way; what matters is time-to-verdict for the budget decision.

Each commit message will follow the canonical `Batch NNN.M: ... Pyramid X/X green` format.

---

## Risk register

1. **Batch 225 pyramid may fail at merge.** If any of 5 batches errored mid-run, T0 merge step will detect → halt autonomous chain, surface error to owner.
2. **T5b precompute may exceed 15h.** If wallclock exceeds 24h, will halt + report; quarterly-grain is intentional descope from monthly.
3. **T1 strategy registration may break existing tests.** Each addressal includes full regression tier; pyramid failure halts that addressal but does not halt sibling T1 items (per-addressal isolation per feedback_pyramid_per_addressal.md).
4. **T2 pyramid failure on a specific DEC** halts that DEC's wiring; queue continues with next DEC.
5. **CPU contention between T5b precompute + T1 wiring + Batch 225 cleanup** — possible. Mitigation: T5b runs nice-priority in background; T1 wiring uses 1 process at a time.

---

## CHECKLIST compliance for this plan document
- ✅ #45 — compliance statement at end of conversation turn
- ✅ #67 — doc landing same-turn (this file + INV reclassification land together)
- ✅ #68 — N/A (no API calls in this plan; T5b uses cached parquets only)
- ✅ #69 — full 13-tier pyramid called out per T1 + T2 addressal
- ✅ #70 — toolkit wiring matrix update flagged in T1.2 news_sentiment
- ✅ #71 — FinBERT Phase A/B/C gate documented in T5a (deferred)
- ✅ #74 — same-commit flag rule preserved
- ✅ #75 — commit per addressal preserved throughout T1 + T2
- ✅ #77 — canonical-source verification used in INV review (path probes not memory)
- ✅ #78 — per-addressal pyramid mandate preserved
