# Source: Council 136 Option-7 Audit-A sub-agent + feedback_monitor_design_vs_operational_gap per CHECKLIST #77.

# B1042 Audit-A: CAT-1 Monitor + CAT-2 Validator / Preflight / Checker - DESIGN-vs-ARMED Audit

# Source: Council 136 Option-7 sub-agent Audit-A invocation 2026-06-28
# Source: scripts/launch_phase_1_aws.sh + scripts/launch_r5_master_4y_v2.sh (production launchers)
# Source: scripts/pre_launch_validation.py (used by GH workflow .github/workflows/cold_start.yml)
# Source: VERIFICATION_MATRIX.md DEC-179 PARTIAL-ORPHAN finding (cross-reference)
# Source: feedback_monitor_design_vs_operational_gap (B1019 banner mismatch lineage)

## Scope

CAT-1 (monitor / watchdog / wrapper) + CAT-2 (validator / preflight / checker). Read-only audit per L86/L95. No code changes.

## Per-file table

| File | Purpose | Invocations found | Verdict |
|---|---|---|---|
| `scripts/b1019_phase_1_runtime_monitor.py` | Engine subprocess wrapper + cadence/baseline monitor | `scripts/launch_phase_1_aws.sh:88` only | **ORPHAN-RECURSIVE** (Pattern C - caller is also orphan) |
| `scripts/b1019_phase_1_post_run_analyzer.py` | Post-run cube analyzer (failure classification) | Self-only (docstring example) + `PHASE_1_AWS_HANDOFF.md:97` (doc-only) | **ORPHAN** (Pattern A) |
| `scripts/b1019_a5_phase_1_preflight_coverage_check.py` | Phase-1 preflight coverage check | `scripts/launch_phase_1_aws.sh:82` only | **ORPHAN-RECURSIVE** (Pattern C) |
| `scripts/monitor_phase_1a_beta_health.py` | 14-check W1-W14 monitor (Batch 394 expansion) | Only `pre_launch_validation.py:512` reads it as text (existence verifier); `test_batch394_monitor_checks.py` imports for tests | **ORPHAN** (Pattern B - imported by tests + path-existence check, never executed in launch path) - DEC-179 PARTIAL-ORPHAN ratified |
| `scripts/monitor_phase_1a_beta_health.sh` | Shell backup monitor (legacy Batch 377) | `pre_launch_validation.py:538` path-existence check only | **ORPHAN** (Pattern A) |
| `scripts/aws_batch395_monitor.py` | Multi-instance S3 heartbeat poller across 5 instances | `test_batch395_aws_scripts.py:30` (test registry only) | **ORPHAN** (Pattern A - Batch 395 5-instance shard run is one-off, not recurring) |
| `scripts/preflight.py` | Staged-diff CHECKLIST gate (C1-C4) | `.git/hooks/pre-commit` (installed via `scripts/git_hooks/pre-commit`) - calls `python scripts/preflight.py --staged` | **WIRED** (git hook; CI-equivalent for local commits when hooks installed) |
| `scripts/preflight_cross_sweep.py` | Per-row addressal `conflicts` populator | `test_batch568_preflight_cross_sweep.py:69,167` (smoke-only) | **ORPHAN** (Pattern A - tests verify existence + behavior but no production / dashboard regen path invokes it) |
| `scripts/walk_preflight.py` | Stage 4 walk fire-count one-line emitter | `test_batch625_walk_commit_fire_count_pin.py` imports functions; CHECKLIST #105 references | **DOCUMENT-AS-MANUAL** (Pattern A - intentional manual Stage-4 helper) |
| `scripts/validate_phase1b_data.py` | Pre-Phase-1B activation data validator | `test_integration.py:948,966-970,2766` (existence + content-grep tests only) | **ORPHAN-PHASE-DEFERRED** (Pattern A - gates Phase 1B not yet activated; intentional) |
| `scripts/validate_sec_edgar_decoded_completeness.py` | SEC EDGAR cache completeness | `test_batch526_sec_edgar_decoded_validator.py` + `test_batch465_orphan_scripts_registry.py` | **ORPHAN** (Pattern A) |
| `scripts/validate_smc_panel_cache_semantic.py` | SMC panel cache semantic gate | `test_batch465_orphan_scripts_registry.py` only | **ORPHAN** (Pattern A - already registered orphan) |
| `scripts/validate_trigger_followthrough.py` | Trigger follow-through validator | `test_batch465_orphan_scripts_registry.py` only | **ORPHAN** (Pattern A) |
| `scripts/validate_pattern_producer_audit.py` | Pattern producer audit harness | `STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md` (doc-only ref) | **ORPHAN** (Pattern A - one-off Stage 4 helper) |
| `scripts/validate_earnings_feed_pit_audit.py` | Earnings-feed PIT audit | Only `STAGE_4_EVENT_DRIVEN_*.md` docs + `EXECUTION_QUEUE.md` | **ORPHAN** (Pattern A - doc-only) |
| `scripts/validate_pattern_w_candidates.py` | Pattern W council candidate validator | `test_batch759_pattern_w_validation.py` import + `test_batch465_orphan_scripts_registry.py` | **DOCUMENT-AS-MANUAL** (Pattern A - Stage 4 council helper) |
| `scripts/run_pbo_check.py` | Probability of Backtest Overfitting check | `test_unit.py` + `scripts/run_t0_close_out.py:119,123` | **WIRED** (called by T0 close-out automation) |
| `scripts/check_platform_determinism.py` | DET-1 cross-platform determinism gate | `.github/workflows/det1-platform-determinism.yml:62` + `scripts/verify_environment.py` | **WIRED** (GH workflow) |
| `scripts/check_merge_train_conflicts.py` | Path-C merge-train conflict detector | `test_batch529_merge_train_conflict_detector.py` (smoke-only) | **ORPHAN** (Pattern A - pin tests verify but no CI workflow invokes) |
| `scripts/checklist_106_cluster_a_producer_audit.py` | One-off CHECKLIST #106 audit (B757) | `test_batch757_checklist_106_audit.py` + `test_unit.py:12153` (one helper-fn import) | **DOCUMENT-AS-MANUAL** (Pattern A - non-recurring per `b938_measure_fire_count_caller_audit.md:22`) |
| `backtest/util/holdout_guard.py` | Post-OOS data-access guard | `test_batch477_holdout_guard_m4.py` only | **ORPHAN** (Pattern B - imported by tests; no engine call-path consumes) |
| `backtest/util/silent_failure_logger.py` | Producer silent-failure logger | `backtest/signals/smc_ict.py:33` + `backtest/engine/exit_strategies.py:1607` + `backtest/util/holdout_guard.py:72` | **WIRED** (production import; engine + signals path) |

## Summary

- Total candidates: **22**
- WIRED: **4** (`preflight.py`, `run_pbo_check.py`, `check_platform_determinism.py`, `silent_failure_logger.py`)
- ORPHAN: **15** (DESIGN-vs-ARMED gaps)
- DOCUMENT-AS-MANUAL: **3** (`walk_preflight.py`, `validate_pattern_w_candidates.py`, `checklist_106_cluster_a_producer_audit.py`)
- DEPRECATED: **0** explicitly tagged (most orphans are non-recurring one-off audit helpers, not deprecated paths)

## Taxonomy distribution

- **Pattern A** (script exists + has `__main__` / CLI but never called): 12
  - `b1019_phase_1_post_run_analyzer`, `monitor_phase_1a_beta_health.sh`, `aws_batch395_monitor.py`, `preflight_cross_sweep`, `validate_phase1b_data`, `validate_sec_edgar_decoded_completeness`, `validate_smc_panel_cache_semantic`, `validate_trigger_followthrough`, `validate_pattern_producer_audit`, `validate_earnings_feed_pit_audit`, `check_merge_train_conflicts`, manual-helpers (3)
- **Pattern B** (script imported but methods never called from production): 2
  - `monitor_phase_1a_beta_health.py` (only tests + path-existence verifier), `holdout_guard.py` (tests only)
- **Pattern C** (script's invocation is INSIDE another orphan - recursive orphan chain): **2 CRITICAL**
  - `b1019_phase_1_runtime_monitor.py` -> called by `launch_phase_1_aws.sh` -> which is NEVER called by `launch_r5_master_4y_v2.sh` (the actual current launcher). This is the **exact B1019 banner-vs-armed pattern** that surfaced honest-finding-pivot #24.
  - `b1019_a5_phase_1_preflight_coverage_check.py` -> same recursive orphan chain via `launch_phase_1_aws.sh`.
- **Pattern D** (claimed RESOLVED-IMPLEMENTED in queue but unwired): At least 1
  - `monitor_phase_1a_beta_health.py` - VERIFICATION_MATRIX.md DEC-179 already tagged PARTIAL-ORPHAN; no production wiring delivered.

## CRITICAL FINDING - Pattern C recursive orphan chain (B1019)

`scripts/launch_r5_master_4y_v2.sh` line 13 docstring claims: *"B-3: B1019 runtime_monitor.py wraps engine subprocess"*. The CHECKLIST #121 grep at line 247 checks for `sync_loop|phase_watchdog|engine.log` - NOT for `b1019_phase_1_runtime_monitor`. The actual user-data uses inline `sync_loop()` + `phase_watchdog()` bash functions + `engine.log` tee. **`b1019_phase_1_runtime_monitor.py` is never invoked from the current production launcher.** The only invocation site is `launch_phase_1_aws.sh` which itself has zero production callers (only `PHASE_1_AWS_HANDOFF.md` documentation refers to it). This is the **exact design-vs-armed pattern** memory-rule `feedback_monitor_design_vs_operational_gap` was authored to prevent.

## Disposition recommendations (per ORPHAN - surface only per L86/L95)

| Script | Recommendation |
|---|---|
| `b1019_phase_1_runtime_monitor.py` | **WIRE** into `launch_r5_master_4y_v2.sh` user-data per its original B1019 design intent, OR **DELETE** + update CLAUDE.md banner to reflect that the inline bash `sync_loop`+`phase_watchdog` is the real production monitor |
| `b1019_phase_1_post_run_analyzer.py` | **WIRE** as post-run step in launcher OR **ARCHIVE** if superseded |
| `b1019_a5_phase_1_preflight_coverage_check.py` | **WIRE** into launcher pre-flight OR **DELETE** (replaced by inline launcher checks) |
| `launch_phase_1_aws.sh` (chain root) | **DELETE** or **ARCHIVE** - superseded by `launch_r5_master_4y_v2.sh` |
| `monitor_phase_1a_beta_health.py` / `.sh` | **ARCHIVE** - Phase 1A-β complete; superseded by R5 Master launcher monitor armament |
| `aws_batch395_monitor.py` | **ARCHIVE** - Batch 395 5-instance run was one-off |
| `preflight_cross_sweep.py` | **WIRE** into dashboard regen pipeline OR **DOCUMENT-AS-MANUAL** |
| `validate_phase1b_data.py` | **KEEP** + queue for explicit Phase 1B activation wiring (intentionally phase-deferred; not a true orphan) |
| `validate_sec_edgar_decoded_completeness.py` | **WIRE** into prefetch validation flow OR **DOCUMENT-AS-MANUAL** |
| `validate_smc_panel_cache_semantic.py` | **WIRE** into SMC cache build pipeline (semantic gate) - high-value catch |
| `validate_trigger_followthrough.py` | **DOCUMENT-AS-MANUAL** - Stage 4 helper |
| `validate_pattern_producer_audit.py` | **DOCUMENT-AS-MANUAL** - Stage 4 helper |
| `validate_earnings_feed_pit_audit.py` | **DOCUMENT-AS-MANUAL** - Stage 4 helper |
| `check_merge_train_conflicts.py` | **WIRE** into pre-merge GH workflow OR **DOCUMENT-AS-MANUAL** |
| `holdout_guard.py` | **WIRE** into data-access call sites per its original M4 design intent - true ARMED gap |

## Cross-reference to memory rules

- `feedback_monitor_design_vs_operational_gap` (B1019 banner FALSE) - pattern recurs in 4 scripts in this audit
- `feedback_audit_recommendations_against_existing_directives` - recommendations surfaced only, NOT auto-applied
- VERIFICATION_MATRIX.md DEC-179 PARTIAL-ORPHAN already documented for `monitor_phase_1a_beta_health.py` - ratified
- L86/L95 - read-only audit; zero code mutations

# End of B1042 Audit-A
