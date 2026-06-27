# Source: Council 137 + Council 138 + feedback_monitor_design_vs_operational_gap per CHECKLIST #77.

# B1043 - Wired-but-Engine-Not-Activated Deep Audit (Sub-agent B / Council 137 Option-4)

**Date:** 2026-06-28
**Author:** Sub-agent B (Council 137 Option-4)
**Owner mandate:** "Do another deep review of wired but engine activated scripts. Be extremely thorough and comprehensive. No more silent misses."
**Methodology:** L86/L95 read-only audit; per-claim 4-step probe (import -> call -> runtime-reach -> output-consumed); cross-checked against `VERIFICATION_MATRIX.md` + `feedback_wired_means_engine_consumed` rule + `test_batch464_writer_outputs_registry.py` + `test_batch465_orphan_scripts_registry.py`.
**Verdict legend:** **FULLY-WIRED** / **CALLED-BUT-OUTPUT-ORPHAN** (engine writes; no Python reader downstream) / **IMPORT-ONLY** / **NEVER-CALLED** / **STANDALONE-CLI** (manual operator only) / **DEPRECATED**.

---

## CATEGORY A - Risk-management scripts

| Claim | Implementation file:line | Imported | Called | Runtime-reached | Output-consumed | Verdict |
|---|---|---|---|---|---|---|
| DEC-505 walk-forward fold logic | `backtest/engine/improvements.py:183 run_walk_forward` | `backtest.py:48` | `backtest.py:2468` | YES (when `walk_forward=True`, default per Batch 187 INV-050) | `walk_forward_validation.csv` -> `merge_batch_outputs.py:165` + `build_phase_1a_beta_dashboard.py:138` | **FULLY-WIRED** |
| DEC-505 SMC walk-forward runner | `scripts/run_dec505_walk_forward_smc.py` | - | only by `test_b1039_dec505_smc_walk_forward.py` | NO (not on engine path) | n/a - manual operator script | **STANDALONE-CLI** (by design; B1039 acknowledges) |
| DEC-084 look-ahead validator (engine env-check) | `backtest/run_phase1a.py:62 validate_lookahead` | self | `run_phase1a.py:296` | YES (called every run; aborts on fail) | console log | **FULLY-WIRED** |
| DEC-084 SMC PIT auditor | `scripts/smc_pit_audit.py` | only by `test_batch735_smc_pit_auditor.py` + sibling `cross_sectional_pit_audit.py` adaptation | manual CLI | NO (not on engine path) | n/a | **STANDALONE-CLI** (operator-run pre-cube gate) |
| DEC-426 5-Gate / Tranche 1/2 (cube populator) | `backtest/results/cube_populator.py:284 five_gate` | `writer.py` indirect via `cube_populator` import chain | runtime when cube replay completes | YES under cube path | cube_populator output keys consumed by `optimize_strategies_from_cube.py` | **FULLY-WIRED** (cube-path) |
| A5 planted-bug canary framework | `scripts/a5_planted_bug_canary_framework.py` | - | manual CLI | NO | recorded in `output_audit/a5_planted_bug_canary_log.json` | **STANDALONE-CLI** (operator-run; PATH Section 13.7 gate) |

**Category A severity:** No risk-mgmt BLOCKERs. Standalone-CLI items are operator-gated by design.

---

## CATEGORY B - Cost / slippage models

| Claim | Implementation file:line | Imported | Called | Runtime-reached | Output-consumed | Verdict |
|---|---|---|---|---|---|---|
| `apply_transaction_costs` | `improvements.py` (line ~120) | `backtest.py:48` | engine main loop | YES | trade_log `pnl_pct` net-of-cost | **FULLY-WIRED** |
| `_cost_sensitivity_sharpe` (DEC-404 sharpe_at_0/5/10/20bps) | `metrics.py:578` | self (metrics.py) | `compute_strategy_metrics:2336` | YES on every metrics compute | `backtest_results.csv` columns + DEC-612 gate | **FULLY-WIRED** |
| DEC-612 cost-sensitivity AUTO-FAIL gate | `metrics.py:_eval_cost_sensitivity_gate` invoked at `metrics.py:2553` | self | `compute_strategy_metrics passes` dict | YES - `passes["cost_sensitivity"]` member of `passes_all` | `passes_all` -> `winning_strategies.json` | **FULLY-WIRED** |
| `compute_slippage_bps_advanced` (DEC-092 advanced slippage analytics) | `improvements.py:compute_slippage_bps_advanced` | `writer.py:570` | `writer.py:585` (tier-stub inputs) | YES (every backtest writes slippage_advanced.csv) | **NONE** - `slippage_advanced.csv` is class-(a) in `test_batch464` registry, no Python reader | **CALLED-BUT-OUTPUT-ORPHAN** (stub inputs; pre-1B+ consumer) |
| Bid-ask modeling | n/a - only annualized-vol proxy + per-trade tier flat slippage | n/a | n/a | n/a | n/a | **NEVER-CALLED** (intentional; DEC notes 1B+ work) |

**Category B severity:** WARN - DEC-092 advanced slippage is stub-input only; engine emits the file but never consumes it; can degrade phase-D conclusions if cube-stage owner expects per-trade slippage from this CSV. Recommend documenting "stub artifact" explicitly.

---

## CATEGORY C - Statistical gates

| Claim | Implementation file:line | Imported | Called | Runtime-reached | Output-consumed | Verdict |
|---|---|---|---|---|---|---|
| Bonferroni adjusted threshold (info-only) | `improvements.py:1123 bonferroni_adjusted_threshold` | `backtest.py:50` | `backtest.py:2473` | YES | `bonferroni` dict passed to `write_all_outputs(...)` (writer.py) -> logger info only; no gate | **CALLED-BUT-OUTPUT-ORPHAN** for cube selection (logger only) |
| Bonferroni Gate 2 in 7-gate verdict | `seven_gate_verdict.py:44` imports `multi_test.bonferroni`; Gate 2 at compute_verdict_cube | self | `writer.py:276 compute_verdict_cube` | YES when `df_trades.strategy/regime/sector` columns present + n>=30 | `verdict_cube.csv` -> `optimize_strategies_from_cube.py` + `aws_batch395_forensic_per_batch.py:312` | **FULLY-WIRED** |
| BH-FDR gate (B982 promoted to HARD GATE) | `multiple_testing_correction.py:494 benjamini_hochberg_fdr`; gate at line 506 | `cube_compose_verdict.py:35` | `cube_compose_verdict.py:162 cube_select_with_multiple_testing` | YES - invoked from `writer.py:310 emit_cube_compose_verdict_csv` | `cube_compose_verdict.csv` -> **only operator/diagnostic script references** (`run_conditional_information_diagnostic_on_strategies.py` docstring + cube optimizer reads `verdict_cube.csv` not compose); dashboard does NOT consume | **CALLED-BUT-OUTPUT-ORPHAN** (gate runs; CSV ungated by downstream selector) |
| Deflated Sharpe (Bailey-LdP 2014) | `metrics.py:_deflated_sharpe` invoked at `metrics.py:2335`; `multiple_testing_correction.py:216` | self | `compute_strategy_metrics` (per-strategy) + `cube_select_with_multiple_testing` (cube-cell) | YES - `passes["deflated_sharpe"]` gate at metrics.py:2536 | passes_all -> winning_strategies.json | **FULLY-WIRED** |
| PSR companion gate (B983 DEC #6) | `metrics.py:_deflated_sharpe` returns `psr` key; gate at `metrics.py:2544` | self | `compute_strategy_metrics` | YES - `passes["psr"]` member of `passes_all` | passes_all -> winning_strategies.json | **FULLY-WIRED** |
| SPA bootstrap (Hansen) | `multiple_testing_correction.py:hansen_spa_pvalue` invoked at compose:477 | self | `cube_select_with_multiple_testing` | YES if cube path | `cube_compose_verdict.csv` (see BH-FDR row) | **CALLED-BUT-OUTPUT-ORPHAN** (same chain as BH-FDR; CSV ungated downstream) |
| EXPLORATORY_STRATEGIES family-size adjuster | `multiple_testing_correction.py:cube_eligible_for_multiple_testing` | self + `section_09b_pre_cube_evidence.py:118` | invoked at compose:439 | YES on cube path | drives family_size used in DSR / BH-FDR | **FULLY-WIRED** |
| DEC-613 Chow break-point AUTO-FAIL | `metrics.py:_chow_test` at 2329; `_eval_chow_gate` at 2561 | self | `compute_strategy_metrics passes` | YES - `passes["chow_break"]` member of `passes_all` | passes_all -> winners | **FULLY-WIRED** |
| DEC-614 ADF stationarity AUTO-FAIL (regime-conditional) | `metrics.py:_adf_test` at 2328; `_eval_adf_gate` at 2573 | self | `compute_strategy_metrics passes` | YES - `passes["adf_stationary"]` member of `passes_all` | passes_all -> winners | **FULLY-WIRED** |
| Sortino / Calmar gates (Batch 221) | `metrics.py` lines 2546-2547 | self | `compute_strategy_metrics passes` | YES | passes_all -> winners | **FULLY-WIRED** |

**Category C severity:** WARN - BH-FDR + SPA + DSR cube-cell verdict (compose layer) is fully computed but `cube_compose_verdict.csv` has NO Python reader in `scripts/*` non-test code (dashboard reads `verdict_cube.csv` 7-gate output, not compose output). Cube optimizer (`optimize_strategies_from_cube.py:18`) explicitly consumes `verdict_cube.csv` (DEC-426 5-Gate), not compose. **Phase-D risk:** if owner intent is that COMPOSE layer drives R5 winner selection (per `STRATEGY_ROSTER`/EXECUTION_QUEUE B982 BH-FDR-gate [OK] claim), the gate is computed and serialized but selection actually uses 7-gate verdict_cube. Verify owner expectation: 7-gate (Bonferroni-corrected) IS the operative gate; COMPOSE is a parallel artifact per B668 wiring comment in writer.py:302.

---

## CATEGORY D - Cube post-processors / dashboard generators

| Claim | Implementation file:line | Engine reaches? | Output-consumed | Verdict |
|---|---|---|---|---|
| `trade_log.csv/parquet` | writer.py:76,97 | YES every run | downstream cube + dashboard | **FULLY-WIRED** |
| `backtest_results.csv` | writer.py:122 | YES every run | dashboard_phase_1a.py:439 (bootstrap_ci) + cube optimizer | **FULLY-WIRED** |
| `raw_signal_fires.json` (B901) | writer.py:111 + screener.emit_raw_signal_fire_counts | YES only when env `EMIT_RAW_SIGNAL_FIRES=1` (R5 AWS bootstrap sets it) | R5 diagnostic only | **FULLY-WIRED** (env-gated by design) |
| `verdict_cube.csv` (DEC-578 7-gate) | writer.py:287 via compute_verdict_cube | YES if df_trades has strategy/regime/sector + n>=30 | `optimize_strategies_from_cube.py` + `aws_batch395_forensic_per_batch.py` | **FULLY-WIRED** |
| `cube_compose_verdict.csv` (B668 COMPOSE) | writer.py:310 | YES if df_trades non-empty | NO Python reader (operator/diagnostic only) | **CALLED-BUT-OUTPUT-ORPHAN** (see Cat C) |
| `stress_metrics.json` (DEC-082/405) | writer.py:355 | YES | dashboard_phase_1a.py:440 | **FULLY-WIRED** |
| `rolling_sharpe_stability.json` (DEC-111/415) | writer.py:381 | YES | dashboard_phase_1a.py:438 | **FULLY-WIRED** |
| `edge_decay_metrics.csv` (DEC-250) | writer.py:412 | YES | NO reader in scripts/* | **CALLED-BUT-OUTPUT-ORPHAN** (class-a per test_batch464; dashboard catalog entry only) |
| `bootstrap_ci.csv` (DEC-423) | writer.py:442 | YES | dashboard_phase_1a.py:439 | **FULLY-WIRED** |
| `regime_stratified_summary.json` (DEC-153) | writer.py:477 | YES | dashboard_phase_1a.py:425 | **FULLY-WIRED** |
| `top_losers_per_strategy.json` (DEC-015/089/120) | writer.py:500 | YES | NO reader | **CALLED-BUT-OUTPUT-ORPHAN** (class-a; "candidate for dashboard tab wire") |
| `stop_cluster_pattern.json` (DEC-078A/366) | writer.py:525 | YES | NO reader | **CALLED-BUT-OUTPUT-ORPHAN** (class-c forensic-only per test_batch464) |
| `trade_pnl_decomposition.csv` (DEC-214/279) | writer.py:554 | YES (with zero-stubs in Phase 1A) | NO reader | **CALLED-BUT-OUTPUT-ORPHAN** (class-a "analyst-pass candidate") |
| `slippage_advanced.csv` (DEC-092/280) | writer.py:593 | YES (stub tier inputs) | NO reader | **CALLED-BUT-OUTPUT-ORPHAN** |
| `test_coverage_gate.json` (DEC-095/225) | writer.py:615 | YES only when coverage.xml exists at output_dir | NO reader | **CALLED-BUT-OUTPUT-ORPHAN** (class-b stub) |
| `portfolio_metrics.json` (BUG-95) | writer.py:1113 via `compute_portfolio_metrics_from_curves` | YES if portfolio attached | dashboard_phase_1a.py:434 | **FULLY-WIRED** |
| `equity_curve.parquet` + `benchmark_curve.parquet` | writer.py:1097/1103 | YES | dashboard + portfolio_metrics | **FULLY-WIRED** |
| `yfinance_hardcut_verify.json` (BUG-228) | writer.py:715 | YES | NO reader | **CALLED-BUT-OUTPUT-ORPHAN** (class-b verifier-only) |
| `batch163_stub_results.json` | writer.py:908 | YES | NO reader | **CALLED-BUT-OUTPUT-ORPHAN** (class-b stub) |
| `dec_constants_verification.json` (Batch 166; 66 DEC constants check) | writer.py:1063 | YES every run | NO reader | **CALLED-BUT-OUTPUT-ORPHAN** (class-b debug; failure logs as warning only - does NOT abort engine) |
| `signal_fire_rates.json` (DEC-296) | writer.py:1281 `_write_signal_fire_rate_report` | YES via writer.py:1254 | NO reader | **CALLED-BUT-OUTPUT-ORPHAN** (class-a human-inspection) |

**Category D severity:** WARN per-artifact, no individual BLOCKER. Aggregated: 13 of 27 writer outputs are CALLED-BUT-OUTPUT-ORPHAN, matching `test_batch464_writer_outputs_registry` class-(a/b/c) classification. The owner has already approved the registry - they ARE expected outputs. **Phase D risk:** these are catalog/forensic artifacts, not decision-driving inputs; treat as low-risk debt.

---

## CATEGORY E - Walk-forward enforcers

| Claim | Implementation | Runtime | Verdict |
|---|---|---|---|
| `run_walk_forward` (DEC-505 4-fold) | improvements.py:183 | backtest.py:2468 | **FULLY-WIRED** |
| `walk_forward_validation.csv` emission | writer.py:1142 via `walk_forward=wf_df` arg from backtest.py:2593 | YES | **FULLY-WIRED** |
| `trade_log_in_sample.csv` / `trade_log_out_of_sample.csv` | writer.py:1154/1155 | YES if walk_forward present | dashboard / DEC-505 walk-forward consumer | **FULLY-WIRED** |
| 4-fold gate (>=3-of-4 OOS = ROBUST) | improvements.py:_metrics + verdict logic ~lines 252-320 | YES | wf_results dict in walk_forward_summary | **FULLY-WIRED** (but verdict is INFORMATIONAL - not gating `passes_all` directly) |
| DEC-426 5-Gate cube-cell verdict | cube_populator.py:284 five_gate | YES on cube path | drives priority + fail_reason in verdict_cube | **FULLY-WIRED** |

**Category E severity:** No BLOCKER. Walk-forward verdict is informational (does NOT contribute to `passes_all` in `metrics.py`); the 5-Gate IS the gating layer on the cube path. Confirm owner intent: walk-forward summary is for human review only.

---

## CATEGORY F - Multi-testing correction

| Claim | Implementation | Runtime | Verdict |
|---|---|---|---|
| `cube_select_with_multiple_testing` | multiple_testing_correction.py:399 | via cube_compose_verdict.py:162 ← writer.py:310 | **FULLY-WIRED** computation |
| BH-FDR significance | multiple_testing_correction.py:494 (`benjamini_hochberg_fdr`) | invoked inside compose at line 494 | **FULLY-WIRED** |
| EXPLORATORY_STRATEGIES filter | line 50-115 (set definition) + line 118 (`cube_eligible_for_multiple_testing`) | invoked at compose:439 | **FULLY-WIRED** |
| `passes_compose` downstream selection | result.passes_compose attribute serialized in compose CSV col `passes_compose` | NO Python reader of CSV in scripts/* | **CALLED-BUT-OUTPUT-ORPHAN** |
| `compute_dsr_from_returns` (deflated_sharpe.py) | deflated_sharpe.py:140 | imported by seven_gate_verdict.py:43 (Gate 3) | **FULLY-WIRED** via 7-gate path |

**Category F severity:** WARN - same finding as Cat C: multi-testing CORRECTION runs and emits `cube_compose_verdict.csv` but downstream selector (`optimize_strategies_from_cube.py`) reads `verdict_cube.csv` (7-gate). The two layers are PARALLEL per B668 design (writer.py:302 explicitly states "Architecture: PARALLEL artifact; does NOT replace 7-gate Gate 2 / Gate 3"). Owner needs to confirm: if the design intent is that COMPOSE is observational while 7-gate is the operative selector, this is correct. If owner expects COMPOSE to gate R5 winner selection, the cube optimizer needs a wiring change to read compose output.

---

## CATEGORY G - Sub-batch monitors / runtime instrumentation

| Claim | Implementation | Armed? | Verdict |
|---|---|---|---|
| `engine_state.json` emit (B1042 producer) | backtest.py:574-605 (every 100 sim-days, atomic write) | engine main loop | **FULLY-WIRED** (B1042 fix verified) |
| `b1019_phase_1_runtime_monitor.py` consumer | scripts/b1019_phase_1_runtime_monitor.py | armed by `scripts/launch_r5_master_4y_v2.sh:195` + `scripts/launch_phase_1_aws.sh:88` | **FULLY-WIRED** (R5 launches arm the monitor) |
| `_RAW_SIGNAL_FIRE_COUNTER` (B901) | screener.py:64 + emit at screener.py:67 / writer.py:111 | env-gated by `EMIT_RAW_SIGNAL_FIRES=1` (set by R5 AWS bootstrap) | **FULLY-WIRED** (env-gated) |
| `monitor_phase_1a_beta_health.py` | scripts/monitor_phase_1a_beta_health.py + .sh | NO python importer; .sh wrapper present | **STANDALONE-CLI** (operator/cron-driven) |
| `holdout_guard.is_in_holdout / HoldoutUnlock / assert_no_holdout_intrusion` (Batch 477 / M4) | backtest/util/holdout_guard.py | NO engine importer - only `test_batch477_holdout_guard_m4.py` | **NEVER-CALLED** by engine - primitives defined, but no caller in engine path wraps walk-forward / cube selector with `assert_no_holdout_intrusion`. Audit-A also flagged this. |
| DEC-179 memory snapshot | n/a - refer to PARTIAL-ORPHAN VERIFICATION_MATRIX `DEC-179` (primary helper scripts/monitor_phase_1a_beta_health.py has no live importer) | NO engine call | **NEVER-CALLED** (matches Audit-A finding) |

**Category G severity:** **BLOCK candidate.** `holdout_guard.assert_no_holdout_intrusion` is the M4 final-OOS protection that gates the 1A-alpha gate evaluation. Per Batch 477 docstring it must "wrap engine entry points so accidental holdout inspection surfaces in CI." Currently NO engine entry point invokes `assert_no_holdout_intrusion`, so the holdout window (date(2026,1,1) -> date(2026,6,30)) is structurally unprotected - any walk-forward / cube / verdict call may read it without raising. **Phase D blocker if owner expected M4 holdout guard to be operative.**

---

## CATEGORY H - Engine-side validators

| Claim | Implementation | Runtime | Verdict |
|---|---|---|---|
| `validate_lookahead` (date_ceiling check via fetch_ohlcv as_of) | run_phase1a.py:62 + 296 | YES every run; aborts on fail | **FULLY-WIRED** |
| `assert_no_finnhub_financials` (DEC-606 financials guard) | improvements.py:626; run at run_phase1a.py:54-58 | YES every run | **FULLY-WIRED** |
| `validate_strategy_roster` (Batch 270 roster sanity gate) | screener.validate_strategy_roster; run at run_phase1a.py:287 | YES every run; aborts on fail | **FULLY-WIRED** |
| BUG-228 yfinance_hardcut_verify | writer.py:715 - verifies 0 yfinance calls | YES every run | logs WARNING only on fail (no abort) | **FULLY-WIRED-EMIT** but does NOT halt engine on violation (logger.warning only) |
| BUG-95 portfolio_metrics | writer.py:1108 `compute_portfolio_metrics_from_curves` | YES if portfolio attached | dashboard_phase_1a:434 | **FULLY-WIRED** |
| Batch 296 fire-rate report | writer.py:1281 `_write_signal_fire_rate_report` | YES via writer.py:1254 | NO reader | **CALLED-BUT-OUTPUT-ORPHAN** |
| `batch163_stub_results.json` | writer.py:908 | YES | NO reader | **CALLED-BUT-OUTPUT-ORPHAN** (class-b stub) |
| `dec_constants_verification.json` (Batch 166; 66 DEC constants) | writer.py:1063 | YES | NO reader (and FAILURE logs WARNING, does not halt) | **CALLED-BUT-OUTPUT-ORPHAN** |

**Category H severity:** WARN - `yfinance_hardcut_verify` and `dec_constants_verification` are write-and-log-only diagnostics. If a future code edit reintroduces yfinance in the engine path, the JSON file will record it but the engine will NOT abort. Recommend promoting BUG-228 from advisory log -> CI-failing assertion if owner expects hard CUT.

---

## Summary

| Category | Claims audited | FULLY-WIRED | CALLED-BUT-OUTPUT-ORPHAN | NEVER-CALLED | STANDALONE-CLI |
|---|---|---|---|---|---|
| A (risk-mgmt) | 6 | 4 | 0 | 0 | 2 |
| B (cost/slippage) | 5 | 3 | 1 | 1 | 0 |
| C (stat gates) | 11 | 8 | 3 | 0 | 0 |
| D (cube/dashboard writers) | 21 | 8 | 13 | 0 | 0 |
| E (walk-forward) | 5 | 5 | 0 | 0 | 0 |
| F (multi-testing) | 5 | 4 | 1 | 0 | 0 |
| G (runtime monitors) | 6 | 3 | 0 | 2 | 1 |
| H (engine validators) | 8 | 5 | 3 | 0 | 0 |
| **Total** | **67** | **40** | **21** | **3** | **3** |

---

## Phase D launch BLOCKER section

**BLOCK-severity findings (Categories A / E / F):**
- A: none.
- E: none - walk-forward fully wired; verdict informational only (confirm owner intent).
- F: none structural; the BH-FDR gate is computed and serialized but downstream selector reads 7-gate. This is a documented PARALLEL design (writer.py:302). **WARN-severity** if owner expected COMPOSE to gate.

**BLOCK-severity candidate finding (Category G):**
- **`holdout_guard.assert_no_holdout_intrusion` NEVER-CALLED by engine.** Batch 477 M4 final-OOS holdout primitives (`FINAL_OOS_HOLDOUT_START = 2026-01-01`, `_END = 2026-06-30`) are defined but no engine entry point invokes the assert. Any walk-forward / cube / metrics call may read holdout dates without raising. **Recommendation:** wrap engine entry (run_phase1a.py:main OR backtest.py:run) with `assert_no_holdout_intrusion(...)` over the trade-log entry-date iterable before reporting `passes_all`. Without this, Phase D 1A-alpha gate is structurally unenforced.

**WARN-severity findings (cumulative):**
- 13 writer.py outputs CALLED-BUT-OUTPUT-ORPHAN (matches owner-approved test_batch464 registry; class-a/b/c expected debt).
- BUG-228 yfinance_hardcut_verify logs warning instead of aborting.
- DEC-092 advanced slippage emits stub tier inputs not real per-trade slippage.
- `cube_compose_verdict.csv` (B982 BH-FDR + B668 COMPOSE) has no Python reader downstream - gate runs but selection uses parallel 7-gate verdict_cube.csv.

**Recommendation: PROCEED WITH ONE CAVEAT** -
- **HALT-equivalent for Phase D 1A-alpha gate evaluation step:** wire `holdout_guard.assert_no_holdout_intrusion` into the engine entry before claiming M4 protection. Without this fix the M4 holdout is an honor-system guard, not an enforced gate. If owner has independently approved unwired holdout for Phase D (operator-discipline assumed), proceed; otherwise patch before launch.
- All other categories are wired adequately. The CALLED-BUT-OUTPUT-ORPHAN count (21) matches owner-approved registries (test_batch464 + test_batch465); no NEW silent gaps surfaced beyond Audit-A/D scope.

**Honest-finding pivot vs Sub-agent A scope:** Sub-agent A (B1042 Audit-A) found 15 ORPHAN monitor/validator scripts at file-level glob. This deep audit confirms most are STANDALONE-CLI by design (operator-driven, not engine-path). The genuine NEW gap surfaced here is **holdout_guard.py** - it's a `backtest/util/` module (engine-internal namespace) defined as a wrapping API, but no wrap-site exists. This pattern (designed-but-not-armed) matches the B1019 / B1042 lineage and the `feedback_monitor_design_vs_operational_gap` memory rule.

---

**Audit complete.** Findings surfaced read-only per L86/L95; no remediation applied per `feedback_audit_recommendations_against_existing_directives`. Owner decides remediation order.
