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

# R5 Cube Validation Manifest

**Purpose**: single canonical list of items that have been DEFERRED-STAGE-5 across recent batches and require empirical validation when the R5 cube next runs. Each item references the source batch, the deferred decision, and the validation success criterion.

**R5 status**: 🚀 **LAUNCHED 2026-06-27 B1028** on AWS i-0940a53c75d049381 (c6a.16xlarge spot us-east-1f). Config: Master 1929 ops-intersection (PROJECT_PLAN line 193 spec = Master 1937; intersect S3 OHLCV); 4y window 2022-05-05 → 2026-05-05; 217 active strategies × 26 exits = 5,642 cells/ticker. Pre-launch: A4 OOS seal + A5 planted-bug canary owner-completed; 15/15 PATH §13.7 gates READY. Sunk cost B1024-B1027 = $1.41 (HALT-chain); B1028 expected $1.20-2.70. Pre-launch readiness governed by `feedback_readiness_audit_must_verify_universe_scope` (memory rule per owner correction). This manifest is the staging ground — every item below gets validated against B1028 R5 cube output. Prior status: PAUSED per `feedback_r5_paused_pending_stage4_completion` (owner directive 2026-06-04; gate LIFTED 2026-06-16 per Stage 4 walks complete).

**Living document**: append-only across batches that produce R5-deferred work. Each new deferral adds a row; resolved items move to a "RESOLVED" section with the R5 batch that closed them.

**Audited tests**: `EXECUTION_QUEUE.md` `S5-*` entries reference this manifest; tests that pin deferred state should cite their item ID below.

---

## Active R5 Validation Items

### M1 — 21 deferred STRATEGY_REGIME_AFFINITY dual entries

**Source**: B617 family audit (Batch 271 mass-edit signature on 40 dual `_strat3` strategies); B623 direction-disaggregated audit on existing 29,360-trade cube data.

**Status**: 4 REMOVE_OK + 14 KEEP + 1 INSUFFICIENT_DATA + 2 NO_TRADES (per B623 verdicts).

**Validation needed**: R5 cube must emit direction-aware per-(strategy, direction, regime) Sharpe + n. The B623 verdicts assumed the existing cube data was representative; R5 with proper direction-aware logging must confirm. For each entry:
- **REMOVE_OK candidates** (4): R5 must confirm B291 direction-aware default produces equal or better PnL than the explicit dual entry. If confirmed, remove the entry.
- **KEEP entries** (14): R5 must confirm the explicit dual entry dominates B291 default by ≥ 5pp. If R5 contradicts, re-decide per-entry.
- **INSUFFICIENT_DATA** (1, `pivot_s2_bounce`): R5 must produce ≥ 30 trades for the strategy; if still insufficient, mark exploratory.
- **NO_TRADES** (2, `smc_bos_retest_entry`, `smc_inverse_fvg`): R5 must produce ≥ 1 trade; if still zero, investigate producer / signal availability.

**Per-entry detail**:

| Entry | Current regimes | B623 verdict | KEEP-PnL | REMOVE-PnL | Delta |
|---|---|---|---|---|---|
| adx_initiation | bear | KEEP | +362.4 | -897.6 | -1260.0 |
| avwap_252_breakout | bear,neutral | KEEP | +205.1 | +115.4 | -89.7 |
| awesome_oscillator | bear | KEEP | +74.4 | -483.6 | -557.9 |
| bollinger_tight | bull | KEEP | +448.1 | -100.8 | -548.9 |
| **camarilla_s3_bounce** | bear,crisis,neutral | **REMOVE_OK** | -10.7 | +93.4 | **+104.2** |
| cmf_flip | bear,neutral | KEEP | +1067.2 | +219.9 | -847.3 |
| **force_index_breakout** | all-4 | **REMOVE_OK** | -1341.5 | -721.0 | **+620.5** |
| macd_fast_crossover | bull | KEEP | +372.5 | +319.1 | -53.5 |
| morning_star | bear | KEEP | +96.0 | +2.9 | -93.0 |
| parabolic_sar_flip | bear | KEEP | +75.0 | -86.4 | -161.4 |
| pivot_s1_bounce | bear,neutral | KEEP | -33.2 | -40.2 | -7.0 |
| pivot_s2_bounce | bear,neutral | INSUFFICIENT | +21.1 | +5.2 | -15.9 |
| ppo_crossover | bear | KEEP | +416.4 | +115.4 | -301.0 |
| prev_day_high_break | bear | KEEP | +155.8 | -237.9 | -393.7 |
| **prev_day_low_bounce** | bear,neutral | **REMOVE_OK** | -105.2 | -101.1 | **+4.1** |
| smc_bos_retest_entry | all-4 | NO_TRADES | 0.0 | 0.0 | 0.0 |
| smc_inverse_fvg | bull,bear,neutral | NO_TRADES | 0.0 | 0.0 | 0.0 |
| supertrend_macd | bull | KEEP | +346.6 | +212.1 | -134.5 |
| tema_dema | bear | KEEP | +436.4 | -259.9 | -696.3 |
| **ultimate_oscillator** | bull | **REMOVE_OK** | +89.3 | +120.4 | **+31.1** |
| williams_stoch_dual | bear | KEEP | +119.8 | -128.1 | -247.9 |

**EXECUTION_QUEUE ID**: `S5-REGIME-AFFINITY-21-DEFERRED`.

**R5 success criteria**: post-R5 trade_log produces direction-aware verdicts that either (a) confirm B623 verdicts → action the 4 REMOVE_OK now / KEEP the rest, or (b) materially diverge → re-decide per-entry with fresh data.

---

### M2 — 1.5×ATR(14) tolerance sensitivity scan

**Source**: B619 codification of CHECKLIST (p); external-AI critique standing concern across 4 walks.

**Status**: codified as Stage 5 task; walks STOP attempting hand-tuning of the 1.5× default.

**Validation needed**: R5 must replay each of the 10 retest-family strategies at multi-ATR tolerance settings (0.5× / 1.0× / 1.5× / 2.0× / 2.5×) + select per-strategy tolerance that maximizes a joint (Sharpe + fires ≥ 30/yr) criterion.

**Affected producers**: `compute_break_retest_signals`, `compute_flag_break_retest_signals`, pivot/level proximity producers.

**Affected strategies** (10): strat_break_retest_volume, strat_break_retest_confluence, strat_flag_bull_retest_long, strat_flag_bear_retest_short, strat_52wh_break_retest, strat_52wl_break_retest_short, strat_r1_break_retest, strat_donchian_breakout_retest_long, strat_donchian_breakdown_retest_short, strat_volume_spike_breakout_retest.

**EXECUTION_QUEUE ID**: `S5-ATR-SENSITIVITY`.

---

### M3 — squeeze_setup_long EVENT-only L1c offline A/B

**Source**: B620 deletion of strat_squeeze_setup_event_only_long (B-twin was FAIL_FIRE_STARVED per B619 estimator); the A/B question "is EVENT-only L1c better than OR composite?" can be answered offline from cube trade log.

**Status**: B-twin deleted; original strat_squeeze_setup_long retained.

**Validation needed**: post-R5, filter `strat_squeeze_setup_long`'s trade log to the subset where `insider_cluster_active=True` at fire bar + compare hit-rate / Sharpe of the EVENT subset vs the full population. If EVENT subset materially outperforms, consider re-introducing as a smaller A/B test OR loosening L1c to EVENT-only with a less aggressive L3.

**EXECUTION_QUEUE ID**: `S5-SQUEEZE-EVENT-ONLY-AB` (added B632 per owner directive).

---

### M4 — 5 REAL FAIL + 4 WARN fire-count audit candidates

**Source**: B621 fire-count audit across all 221 strategies.

**Status**: surfaced for owner review; no auto-action per `feedback_no_apriori_strategy_pruning` + `feedback_no_rushing_per_strategy_tweak`.

**REAL FAIL (5, < 5 fires/yr UB)** — pure-AND gate stacks; expected to produce INSUFFICIENT_DATA in R5 cube:
- volume_spike_breakout_retest (0.01/yr, 9 gates) — B600 walked
- volume_spike_breakout (0.07/yr, 9 gates)
- break_retest_confluence (0.09/yr, 11 gates) — B609 walked
- 52wl_break_retest_short (0.13/yr, 9 gates) — B605 walked
- break_retest_volume (1.54/yr, 7 gates) — B608/B617 walked

**WARN (4, 5-30 fires/yr UB)** — borderline:
- news_momentum_short (8.73/yr) — B603
- flag_bear_retest_short (15.77/yr) — B607
- news_momentum_long (20.79/yr) — B603
- donchian_breakdown_short (24.95/yr) — B595

**Validation needed**: R5 must produce actual fires/year per strategy. For each REAL FAIL candidate:
- If cube produces ≥ 30 trades/regime → estimator's independence-product upper bound was too pessimistic (correlated gates fire more often than independent product implies); re-tune PRIOR_RATES.
- If cube produces < 30 trades/regime → estimator was correct; owner decides per `feedback_minimum_fire_count_gate_before_cube` resolutions (loosen / mark exploratory / delete).

**EXECUTION_QUEUE ID**: `S5-FIRE-COUNT-CANDIDATES` (added B632 per owner directive).

---

### M5 — 1 FAIL_BUT_HAS_OR (squeeze_setup_long false-FAIL)

**Source**: B621 fire-count audit; strategy uses OR clauses (L1c smart-money OR; L2 catalyst OR) that the AND-product estimator over-restricts → false FAIL verdict (0.12/yr UB).

**Status**: flagged for manual review; no auto-action.

**Validation needed**: R5 actual fire-count. If < 30/regime, the false-FAIL flag was conservative cover; if ≥ 30, OR-aware estimator extension is warranted. Either way the estimator should be enhanced to compute OR-aware joint rates (B619 follow-up).

**EXECUTION_QUEUE ID**: `S5-OR-AWARE-ESTIMATOR` (added B632 per owner directive).

---

### M6 — PRIOR_RATES expansion for 189 INCOMPLETE_PRIORS strategies

**Source**: B621 fire-count audit; 189 strategies fell into INCOMPLETE_PRIORS because their gate signals aren't in PRIOR_RATES.

**Status**: open follow-up; no batch yet.

**Validation needed**: post-R5, measure actual per-signal fire rates from `signal_fire_rates.json` (engine output) + back-fill `scripts/estimate_fire_count.py:PRIOR_RATES` with measured priors. After back-fill, re-run `scripts/audit_fire_counts.py` to surface additional FAIL/WARN candidates that were previously hidden.

**Examples of missing signals**: institutional_persistence_*, classification_change_*, mmbm_long, judas_swing_*, week_opening_gap_*, vix_*, sector_*, calendar_* (totm_long, halloween_seasonal_long, etc.).

**EXECUTION_QUEUE ID**: `S5-PRIOR-RATES-EXPANSION` (added B632 per owner directive).

---

### M7 — 14 environmental pyramid failures (B622 deferred)

**Source**: B622 pyramid drift cleanup; 14 remaining failures need per-item investigation.

**Status**: deferred to focused tooling/registry batch.

**Validation needed**: many of these depend on cube run completion or environmental fixtures:
- Engine parity (test_engine_optimization_parity, test_integration x2) — needs golden fixture investigation post-R5
- Data/PIT freshness (B473, B496, B533 AWS keys, B537 EMA panel, test_data_integrity OHLCV) — needs cache regeneration aligned with R5 inputs
- Registry drift (B465 orphans, B466 bug-engine-status) — careful per-item update batch
- Dashboard/preflight (B568, B569) — artifact regen post-R5

**EXECUTION_QUEUE ID**: `PYRAMID-CLEANUP-ENV`.

---

### M8 — STRATEGY_REGIME_AFFINITY: 4 LONG-only B417-cube-derived entries (not in B617 dual-audit scope)

**Source**: B617 family audit explicitly scoped to dual `_strat3` strategies; B417 cube also produced single-direction entries for LONG-only strategies that were not audited:
- `institutional_buy_momentum_long`: {bull}
- `institutional_cluster_long`: {bear}

These were NOT in the B617 audit because LONG-only strategies don't have the dual-direction-blocking signature. They may still benefit from direction-disaggregated review (e.g., is `institutional_cluster_long` really better in bear than bull?), but the family-bug risk doesn't apply.

**Validation needed** (LOW priority): R5 confirms cube Sharpe sign per regime for these 2 entries; if any single-bucket entry shows the OTHER regime is also profitable, expand the entry.

**EXECUTION_QUEUE ID**: `S5-B417-LONG-ONLY-CUBE` (added B632 per owner directive).

---

## RESOLVED (R5 closed)

*(none yet — R5 has not run)*

---

## Cross-references

- **CHECKLIST.md** sub-rules (h)/(k)/(o)/(p) — each cite this manifest as the staging doc for cube-deferred work.
- **EXECUTION_QUEUE.md** — `S5-*` tickets reference manifest items by M-ID.
- **scripts/direction_disaggregated_regime_audit.py** + `output_audit/direction_disagg_audit.json` — M1 source data + harness.
- **scripts/audit_fire_counts.py** + `output_audit/fire_count_audit.json` — M4/M5 source data.
- **scripts/estimate_fire_count.py:PRIOR_RATES** — M6 expansion target.
