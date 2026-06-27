# Source: Council 136 Option-7 + feedback_monitor_design_vs_operational_gap per CHECKLIST #77.

# B1042 Audit-C: Orphan Tests + Sentinel/Checkpoint Inventory

**Date:** 2026-06-28
**Scope:** Council 136 Option-7 design-vs-armed audit, CAT-5 + CAT-6
**Sub-agent:** Audit-C
**Method:** Read-only; no source/doc changes
**Inputs:** `pytest --collect-only -q`, `glob backtest/tests/test_*.py`, grep over `CLAUDE.md / LEARNINGS.md / EXECUTION_QUEUE.md / AUDIT.md / writer.py / launch_r5_master_4y_v2.sh`

---

## CAT-5 - Test Inventory (Pyramid Discoverability)

**Methodology.** Glob `backtest/tests/test_*.py` (candidate set) vs `pytest --collect-only -q` (collected set). Both base-name-normalized + sorted + diff'd.

| Metric | Value |
|---|---|
| Candidate `test_*.py` files (project) | **364** |
| Files COLLECTED by pytest | **364** |
| Files ORPHAN (file exists but not discovered) | **0** |
| Total tests collected | 5,257 |
| Collection time | 13–28 s |
| Tests with `@pytest.mark.skip` markers | 26 files (intentional MARKED-SKIP - guards for env-dependent / deferred-phase paths) |
| Collection errors | 0 |

**Verdict CAT-5: CLEAN.** Every `test_*.py` under `backtest/tests/` is COLLECTED by pytest under `[pytest] testpaths = backtest/tests` per `pytest.ini`. No file-level orphan tests. Diff `comm -23 candidate collected` = empty set. The 26 files containing `@pytest.mark.skip` use them at the per-test level for environment-conditional skips (e.g., AWS, freezegun edge cases), not file-level disable. CAT-5 Pattern A (test file exists, has tests, never run) is **NOT observed**.

---

## CAT-6 - Sentinel / Checkpoint Inventory

### 6A. `backtest/results/writer.py` - `Wrote *` log claims

27 `logger.info("Wrote ...")` lines in `write_all_outputs`. Status table (consumer = downstream `.py` reader):

| Output file | Producer | Consumer wired? | Verdict |
|---|---|---|---|
| `trade_log.parquet` / `.csv` | writer:77/98 | dashboard + cube_populator + many | WIRED |
| `backtest_results.csv` | writer:123 | site_generator, dashboards | WIRED |
| `strategy_regime_matrix.json` | writer:162 | dashboard_stage_2, regime_selector | WIRED |
| `winning_strategies.json` | writer:178 | extract_phase_1a_beta_winners | WIRED |
| `regime_performance.csv` | writer:195 | dashboard, regime_selector | WIRED |
| `trade_exit_detail.csv` | writer:204 | merge_batch_outputs, exit_conditional_analyzer | WIRED |
| `exit_strategy_comparison.csv` / `_best.csv` | writer:209 | dashboards | WIRED |
| `exit_method_multi_dim_cube.csv` | writer:251 | cube_populator + walk_forward_batch414_cells | WIRED |
| `exit_sweet_spots.csv` | writer:258 | dashboards | WIRED |
| `exit_pairwise_dominance.csv` | writer:265 | dashboards | WIRED |
| `exit_by_<dim>.csv` (1D marginals) | writer:329 | dashboards | WIRED |
| `sector_neutral_hedge_stub.json` (DEC-141) | writer:649 | only test_batch464_writer_outputs_registry | **ORPHAN (Pattern C - stub-by-design Phase 1B+)** |
| `chart_pattern_skeleton_stub.json` (DEC-148) | writer:663 | only registry test | **ORPHAN (Phase 1B+)** |
| `short_long_conversion_stub.json` (DEC-338) | writer:684 | only registry test | **ORPHAN (Phase 1B+)** |
| `analyst_data_stub.json` (DEC-461/BUG-271) | writer:700 | only registry test | **ORPHAN (Phase 1B+)** |
| `yfinance_hardcut_verify.json` (BUG-228) | writer:724 | only registry test | **ORPHAN (verification artifact only)** |
| `fx_exposure_stub.json` (DEC-134/255) | writer:741 | only registry test | **ORPHAN (Stage 4 stub)** |
| `cache_freshness_checksum_stub.json` (DEC-260/330) | writer:768 | only registry test | **ORPHAN (deferred)** |
| `dec_constants_verification.json` (Batch 166) | writer:1066 | only registry test | **ORPHAN (verification only)** |
| `equity_curve.parquet` | writer:1099 | analyst_overlay_from_trade_log + dashboards | WIRED |
| `benchmark_curve.parquet` | writer:1105 | analyst overlay scripts | WIRED |
| `walk_forward_validation.csv` | writer:1145 | merge_batch_outputs + dashboards | WIRED |
| `walk_forward_IS_trade_log.csv` / `_OOS_` | writer:1156 | dashboards | WIRED |
| `tier_adjustment_analysis.csv` | writer:1224 | merge_batch_outputs only | WIRED-NARROW |
| `backtest_report.html` | writer:1480 | user-facing artifact | WIRED |

**Stubs (8) are documented as Phase-1B+ deferred** - labels in code already say "stub". They are Pattern C (emitted but never read) by-design, and `test_batch464_writer_outputs_registry.py` asserts existence so a future Phase-1B consumer flip lands without writer rebuild. **Recommend DOCUMENT-AS-DEFERRED**; do NOT delete (future consumers depend on output-contract stability).

### 6B. `scripts/launch_r5_master_4y_v2.sh` - AWS S3 sentinels

22 `aws s3 cp /tmp/sentinels/* s3://.../` calls. Sentinel set: `BOOT, PYTHON_VERSION, PYTHON_3_11_FAIL, MANDATORY_DEPS_MISSING, PANDAS_TA_STATUS, SMARTMONEYCONCEPTS_STATUS, STRATEGY_IMPORT_FAIL, DATA_SYNC_DONE, SYNC_LOOP_PID, PHASE_{N}_RUNNING, PHASE_{N}_TIMEOUT_HALT, PHASE_{N}_B1019_PID, PHASE_{N}_B1019_HALT, PHASE_{N}_PASS, PHASE_{N}_FAIL, SMOKE_COMPLETE, AUTOLADDER_COMPLETE`.

| Sentinel | Producer (script line) | Documented in canonical docs? | Verdict |
|---|---|---|---|
| `PHASE_*_RUNNING/PASS/FAIL` | launch:179/239/230 | [OK] LEARNINGS L161 (B1028 meta-bug) | WIRED + DOCUMENTED |
| `PHASE_*_B1019_HALT` | launch:210 | [OK] LEARNINGS implicit | WIRED |
| `BOOT / DATA_SYNC_DONE / SYNC_LOOP_PID` | launch:86/138/154 | [WARN] Undocumented at name level | WIRED, ORPHAN-IN-DOCS (Pattern A) |
| `PYTHON_VERSION / PANDAS_TA_STATUS / SMARTMONEYCONCEPTS_STATUS` | launch:91/113/128 | [WARN] Undocumented; partial reference in feedback_silent_failure_pairing_rule | WIRED, ORPHAN-IN-DOCS |
| `AUTOLADDER_COMPLETE / SMOKE_COMPLETE` | launch:273/252 | [WARN] Undocumented | WIRED, ORPHAN-IN-DOCS |

Producer side: every emitted sentinel is paired with `aws s3 cp` (no Pattern B emit-code-missing). Consumer side: poll consumers are Claude's `s3api head-object` calls per `LEARNINGS L153` (CHECKLIST #90.b). No automated reader script wired - relies on Claude-in-session polling. Pattern C orphan at automation level if Claude session terminates.

### 6C. SPOF / silent-producer sentinels in Python code

| Claim | Source doc | Producer | Consumer | Verdict |
|---|---|---|---|---|
| B832 news_sentiment SPOF (3-counter + rate-limited WARNING) | CLAUDE.md banner, EXECUTION_QUEUE row 2/59 | `backtest/signals/news_sentiment.py:50-91` (`_SPOF_EMPTY_RETURNS / _SPOF_ZERO_SCORE_RETURNS / _SPOF_RULE_FALLBACK_ONLY` + `_spof_record`) | Engine log scraper (grep `B832 SPOF SENTINEL`) | WIRED (log-channel consumer) |
| B901 raw-signal fire counter | LEARNINGS B901 (env-flag gated) | `screener.py:62/8393` (`_RAW_SIGNAL_FIRE_COUNTER`) + `writer.py:111` (emit) | `merge_batch_outputs.py` sum-aggregator | WIRED (env-flag gated) |
| Engine `closed_trades` incremental checkpoint | AUDIT BUG-90/107 | `engine/backtest.py` (every 100 days) | crash-recovery only | WIRED (in-memory, S3-orphan per LEARNINGS:2246 #11) |

---

## Summary

| Category | Total | Wired | Orphan | Pattern |
|---|---|---|---|---|
| Test files | 364 | 364 | 0 | - |
| `writer.py "Wrote"` claims | 27 | 19 | 8 (all stubs, by-design) | Pattern C / DOCUMENT-AS-DEFERRED |
| AWS launch-script sentinels | 22 | 22 (code) | 14 undocumented-by-name | Pattern A (doc-orphan), Pattern C (no automated reader) |
| SPOF Python sentinels (B832, B901) | 2 | 2 | 0 | - |
| Engine `closed_trades` checkpoint | 1 | 1 | mid-run S3-blind | Pattern C - meta-bug per LEARNINGS:2246 #11 |

**Top finding (consistent with B1019 design-vs-armed meta-bug):** AWS launch-script sentinels are FULLY ARMED at code level (no Pattern B emit-missing), but consumer side has **no automated reader process**. Polling depends on Claude-in-session `head-object` per CHECKLIST #90.b. When the session ends (B1028 1h 38m blind window), sentinels accumulate in S3 unread until owner asks. This is the **same design-vs-armed gap** that B1019 Monitor exists to solve but was not wrapped around the engine in B1028 user-data.

## Recommendations

- DOCUMENT-AS-DEFERRED: 8 writer.py stubs (DEC-141 / DEC-148 / DEC-338 / DEC-461 / BUG-228 / DEC-134 / DEC-260 / Batch-166). Status-quo + add to `PHASE_1B_PRELAUNCH_TODO.md` consumer-flip checklist.
- DOCUMENT (CLAUDE.md or LEARNINGS sentinel-registry section): the 14 undocumented AWS sentinel names with their semantic meaning. Single new section `AWS Sentinel Registry` ~30 lines. Solves CAT-6 Pattern A doc-orphan.
- WIRE: an automated S3 sentinel reader (CloudWatch Events on S3 PutObject -> SNS/email) so Pattern C consumer-orphan does not require Claude-in-session polling. Mid-priority; matches B1019 design-vs-armed lesson.
- NO ACTION on CAT-5: clean.
