<!-- Source: per CHECKLIST #77 canonical-source; Council 287 B1234 2026-07-07 doc-sync sweep -->

<!-- COUNCIL 278-287 SYNC BANNER (B1234 2026-07-07) - READ FIRST -->
> **Sync status:** Body may contain refs stale as of 2026-06-27 or earlier. Canonical current state (B1231):
> - `len(ALL_STRATEGIES) = 219` (post-B1189 DELETE dxy_headwind); `STRATEGIES_DISABLED_MISSING_PRODUCER = set()`
> - Test count: 880 passed, 2 skipped on test_unit + test_integration
> - CHECKLIST items #1-#158, LEARNINGS through L209, latest batch B1310
> - Councils 278-287: 40 strategies loosened + 11 silent misses remediated + 25+ producer coverage audits + historical timeline finding + 2 critical bugs FIXED via graceful degradation
> - Stage 4 walks: ARCHIVED to `archive/2026-07-07-stage-4-walks-complete/`
> - Sprint 5 tickets: 3 queued (S5-B1214 HIGH / S5-B1216 MED post-B1230 correction / S5-B1212 MED)
> - Comprehensive coverage report: `output_audit/PRODUCER_COVERAGE_COMPREHENSIVE_REPORT.md`

---

# R5 Workflow - Canonical Launch Reference for R6 Reuse

# Source: B1052 sub-agent Alpha synthesis of B1042-B1051 R5 launch lineage per owner directive 2026-06-28 "Document the current workflow, processes, phases etc for reuse in r6" per CHECKLIST #77.

**Doc A of 7-doc r6_workflow_reuse bundle.**

**⚠ Superseded-for-model note:** this doc describes the ORIGINAL monolith autoladder (single instance runs phases 1->4, sentinel-gated). The CURRENT model is chunk-based — see `docs/r6_workflow_reuse/RUN_WORKFLOWS.md` (Doc G) for local + AWS run workflows + unified gate reference. Doc A remains valid for the sentinel contract + phase-gating philosophy.

**Cross-link:** companion playbook `docs/r6_workflow_reuse/AWS_LAUNCH_PLAYBOOK.md` (Doc F) covers AWS-mechanics + AZ failover + spot capacity handling.

---

## How to use this in R6

**R6 owner / Claude:** when planning an R6 cube re-run on a refreshed universe (per `P1-UNIVERSE-REFRESH-POST-R5` queue item), use this doc as the operational ground truth for **what every phase does + what success looks like + how each phase gates the next**. Treat the launch script `scripts/launch_r5_master_4y_v2.sh` as the executable artifact and this doc as the spec it implements. Modify the launch script for R6-specific changes (universe size, window, MAX_MIN ladder); do NOT re-derive workflow from scratch.

**Specific R6 consumers:**

1. R6 launch-readiness audit (analog of B1015-B1017 checklist for R5) - use Section 5 (per-phase failure modes + recovery) as the audit checklist.
2. R6 budget sign-off - use Section 7 (cost arithmetic + 17-hour cap).
3. R6 launch-script diff review - use Section 3 (sentinel-emission order) to verify R6 changes preserve the contract.
4. R6 post-mortem - if R6 fails at phase N, use Section 5 to triage by sentinel + recovery action.

---

## 1. Top-level workflow diagram

```
LOCAL LAPTOP                                      AWS EC2 (c6a.16xlarge spot)
============                                      ============================
bash scripts/launch_r5_master_4y_v2.sh
   |
   +-- Pre-flight (laptop) --------------------+
   |     #124 IAM SSM verify                   |
   |     #121 monitor-armed grep on USERDATA   |
   |     #116 user-data 16KB base64 size check |
   |     (if raw > 12KB:                       |
   |       externalize to S3 + small loader)   |
   |                                           |
   +-- aws ec2 run-instances --user-data <b64> ---->
                                                       BOOTSTRAP (15-25 min)
                                                       sentinels: BOOT,
                                                       PYTHON_VERSION, PANDAS_TA,
                                                       SMARTMONEYCONCEPTS,
                                                       DATA_SYNC_DONE, SYNC_LOOP_PID
                                                       |
                                                       +-- B1019 PREFLIGHT
                                                       |       (data coverage check)
                                                       |
                                                       +-- Phase 1: NVDA  x 4y       (~30-90 min)
                                                       +-- Phase 2: 10    x 4y       (~1-2.5 hr)
                                                       +-- Phase 3: 50    x 4y       (~1.5-3.5 hr)
                                                       +-- Phase 4: 1929  x 4y       (~1.4-2.8 hr)
                                                       |
                                                       +-- B1019 POST-RUN ANALYZER
                                                       +-- AUTOLADDER_COMPLETE
                                                       +-- sudo shutdown -h +1
```

Each phase is **gated by the prior**: a non-zero exit from Phase N HALTs the ladder. Phase N is launched ONLY after Phase N-1 sentinel `PHASE_<N-1>_PASS` writes to S3.

---

## 2. Phase-by-phase reference

### Phase 0: Pre-flight (laptop, ~30 s)

**Purpose:** catch launch-blocking issues BEFORE any AWS spend.

| Gate | Check | Fail behavior |
|---|---|---|
| #124 IAM SSM | `aws iam list-attached-role-policies` shows `AmazonSSMManagedInstanceCore` | `exit 1` before any EC2 cost |
| #121 Monitor armed | `grep -E 'b1019_phase_1_runtime_monitor.py' <USERDATA>` returns match | `exit 1` (no monitor = blind run) |
| #116 16KB size | `wc -c <USERDATA-base64>` <= 16,384 | If raw >12KB: switch to S3 externalization (see Doc F) |
| MASTER_TICKERS format | Verify file in S3 (CSV vs newline) | If newline: pre-process via `tr '\n' ','` (C-1 from B1050) |

**Source:** `scripts/launch_r5_master_4y_v2.sh` lines 56-75. Pre-flight is REQUIRED - never bypass.

### Phase 1: Bootstrap (AWS, 15-25 min)

**Purpose:** instance OS prep + repo clone + venv + dep install + S3 data sync.

**Sentinels (in emission order):**

| # | Sentinel | What it proves | Fail-mode |
|---|---|---|---|
| 1 | `BOOTSTRAP_LOADER` (only if externalized) | S3 user-data download path works | No further sentinels (cloud-init failed) |
| 2 | `BOOT` | Instance + AL2023 ready; `/tmp/sentinels/` writable | OS boot failure (rare) |
| 3 | `PYTHON_VERSION` | Python 3.11 installed | `dnf` failure or AMI drift |
| 4 | `PANDAS_TA_STATUS=0` or `=1` | Optional pandas-ta install logged (#122 paired) | Never fatal |
| 5 | `SMARTMONEYCONCEPTS_STATUS=1` | B1039 vendored library installed; 18 SMC strategies fireable | `=0` -> SMC strategies short-circuit (degraded but non-fatal) |
| 6 | `MANDATORY_DEPS_MISSING` (only on fail) | pandas/numpy/scipy/pyarrow check | HALT - `shutdown +5` |
| 7 | `STRATEGY_IMPORT_FAIL` (only on fail) | `from backtest.signals.screener import ALL_STRATEGIES` raises | HALT - `shutdown +5` |
| 8 | `DATA_SYNC_DONE` | S3 -> instance `data_prefetch` sync (~3 GB) complete | Long-tail 15-25 min normal |
| 9 | `SYNC_LOOP_PID` | 60s background S3 sync loop running | Always emitted |
| 10 | `B1019_PREFLIGHT_PASS` (B1043 F-07) | Data coverage check for Phase 1 ticker passes | `B1019_PREFLIGHT_FAIL` -> HALT |

**Wall-clock:** 15-25 min. **Cost:** $0.30-0.50.

### Phase 1 (sub-cube): NVDA x 4-year

**Purpose:** smallest realistic scale validates full pipeline before committing to multi-ticker scale.

**Scope:** 1 ticker x 1006 trading days x 219 strategies x 26 exits = ~5,694 cube cells.
**Window:** 2022-05-05 -> 2026-05-05.
**MAX_MIN:** 120 (was 30; raised B1043 Sub-C per timing extrapolation).
**Expected wall-clock:** 30-90 min.
**Cost:** $0.50-1.50.

**Sentinels (in order):**

| Sentinel | When | What it proves |
|---|---|---|
| `PHASE_1_RUNNING n=1` | T+0 | Engine subprocess launched; `ENGINE_PID` captured (F-02 fix B1043) |
| `PHASE_1_B1019_PID` | T+0 | B1019 monitor wrap fired (F-09 fix B1043) |
| `engine_state.json` (sim_day=50) | T+~10 min | Layer 1 emit BEFORE 30-min cap; schema matches monitor reader (F-01+F-05 B1043) |
| `engine_state.json` (sim_day=100,200,...) | every ~10 min | Continuous progress visibility |
| `trade_log_checkpoint.csv` | every 100 sim-days when trades > 0 | Mid-run persistence to S3 via sync_loop |
| `PHASE_1_PASS n=1` | T+~30-90 min | Engine completed; `trade_log.parquet` exists |

**Gate to Phase 2:** `PHASE_1_PASS` must land. `PHASE_1_FAIL rc=<N>` -> ladder aborts.

### Phase 2: 10 tickers x 4-year

**Purpose:** validate parallel-ticker handling + multi-ticker memory profile.

**Tickers:** `NVDA,AAPL,MSFT,GOOGL,META,XLF,UUP,COIN,SOFI,IONQ` (deliberately heterogeneous: 4 mega-cap tech + 1 broad ETF + 1 dollar ETF + 3 high-vol speculative).

**MAX_MIN:** 180. **Expected wall-clock:** 1-2.5 hr. **Cost:** $1.50-3.00. **Cube cells:** ~56,940.

**Sentinels:** same pattern as Phase 1 with `_2` suffix.

**Gate to Phase 3:** `PHASE_2_PASS`. Failure here = multi-ticker-specific bug (pool concurrency / memory / heterogeneous-regime).

### Phase 3: 50 tickers x 4-year (stride sample)

**Purpose:** scale test before R5 commit.

**Tickers:** stride sample from Master 1929 -> `ts[::step][:50]`. **Format-contract caveat (C-1 from B1050):** the python `--%-c "ts=...".split(',')` substitution assumes CSV; verify `master_ops_tickers.txt` format in S3 pre-launch.

**MAX_MIN:** 240. **Expected wall-clock:** 1.5-3.5 hr. **Cost:** $3.00-4.50. **Cube cells:** ~284,700.

**Gate to Phase 4:** `PHASE_3_PASS`.

### Phase 4: R5 Master 1929 x 4-year (THE PRODUCTION RUN)

**Purpose:** full Phase 1A-β empirical cube.

**Tickers:** Master Dedup CSV ∩ S3 OHLCV cache = 1,929 (CLAUDE.md ops intersection; PROJECT_PLAN spec line 193 = Master 1937).

**Window:** 2022-05-05 -> 2026-05-05.
**MAX_MIN:** 480 (8 hr; raised from 240 per B1043 Sub-C).
**Engine self-timeout:** `--warn-run-hours=4.0` + `--max-run-hours=6.0` + B1043 F-06 SIGTERM-handler (`kill -15` flushes checkpoint before exit).
**Expected wall-clock:** 1.4-2.8 hr (Sub-C estimate) or up to 8 hr cap.
**Cost:** $2-10 (spot). **Cube cells:** ~10,983,726 (~11M).

**Sentinels:** same pattern with `_4_r5` suffix. Mid-run `engine_state.json` emits every ~10 min so owner can watch progress without SSH (#125).

### Phase 5: Post-run (B1043 F-08)

**Steps:**

1. `scripts/b1019_phase_1_post_run_analyzer.py` against `output_phase_4_r5/trade_log.parquet`
2. Emit `b1019_post_run_report.json` (machine) + `b1019_post_run_summary.md` (owner)
3. Sync both to S3
4. `AUTOLADDER_COMPLETE <UTC> scope=Master-1929 4y` sentinel
5. `sudo shutdown -h +1` (instance self-terminates)

**Cost:** negligible (~2 min).

---

## 3. Sentinel-emission order + contract

**Ordering rule:** sentinels are append-only S3 objects. A later sentinel never overwrites an earlier one - they coexist. Phase N+1 launches ONLY after Phase N's `PHASE_<N>_PASS` lands. Failure sentinels (`*_FAIL`, `*_HALT`, `*_TIMEOUT_HALT`) end the ladder regardless of subsequent sentinels.

**Canonical full sequence (success path):**

```
BOOTSTRAP_LOADER (optional)
BOOT
PYTHON_VERSION
PANDAS_TA_STATUS
SMARTMONEYCONCEPTS_STATUS
DATA_SYNC_DONE
SYNC_LOOP_PID
B1019_PREFLIGHT_PASS
PHASE_1_RUNNING n=1
PHASE_1_B1019_PID
[engine_state.json emits @ sim_day=50,100,...,1000]
PHASE_1_PASS n=1
PHASE_2_RUNNING n=10
...
PHASE_2_PASS
PHASE_3_RUNNING n=50
...
PHASE_3_PASS
PHASE_4_R5_RUNNING n=1929
...
PHASE_4_R5_PASS
B1019_POST_RUN_REPORT.json
B1019_POST_RUN_SUMMARY.md
AUTOLADDER_COMPLETE
```

**Owner monitoring:** poll `aws s3 ls s3://<bucket>/<run_id>/` every 5-10 min during the run. Use Bash `run_in_background` polling agent (see Doc F Section 6).

---

## 4. B1042-B1051 fix lineage (R6 must preserve)

Each fix below was an R5-session honest-finding pivot. **R6 launch script must preserve all of these** unless owner explicitly approves regression.

| Batch | Fix ID | What broke | Resolution |
|---|---|---|---|
| B1042 | Audit A | Monitor-validator wrapper missing | Added `b1019_phase_1_runtime_monitor.py` invocation in run_phase() |
| B1042 | Audit B | Hooks producers not wired to consumers | Aligned hooks with PRODUCER_CONSUMER_PAIRS.md |
| B1042 | Audit C | Orphan tests / sentinels with no consumer | Tagged + dispositioned 12 orphans |
| B1042 | Audit D | Banner DEC-508 gates stale | Refreshed gates rationale |
| B1043 | F-01 | `engine_state.json` schema mismatch (monitor reader expected diff fields) | Engine now emits {simulated_day, cells_completed, status} |
| B1043 | F-02 | `ENGINE_PID` not captured (process substitution lost rc) | `coproc` or explicit `&` + `$!` capture |
| B1043 | F-05 | First `engine_state.json` emit landed AFTER 30-min cap | First emit at sim_day=50 (~10 min) |
| B1043 | F-06 | SIGTERM handler missing -> engine killed without checkpoint flush | `_install_sigterm_handler` in `run_phase1a.py` |
| B1043 | F-07 | Phase 1 preflight coverage check missing | `b1019_a5_phase_1_preflight_coverage_check.py` invoked pre-Phase-1 |
| B1043 | F-08 | Post-run analyzer missing -> no per-strategy summary | `b1019_phase_1_post_run_analyzer.py` invoked post-Phase-4 |
| B1043 | F-09 | Monitor wrap only fired in Phase 1, not Phases 2/3/4 | Wrap applied to every phase |
| B1043 | Sub-C | MAX_MIN values too tight (30/60/90/240) | Raised to 120/180/240/480 |
| B1045 | #27 | HoldoutUnlock context missing in `run_phase1a.py:main` | Added context manager |
| B1045 | Warn-findings | 14 WARN-level findings dispositioned | 9 RESOLVED + 5 DEFERRED-POST-R5 |
| B1046 | Sub-phase doc | No canonical reference for ops team | This doc's predecessor `b1046_phase_d_r5_sub_phases.md` |
| B1047 | Engine-armed retrospective | "Engine armed" claim was code-presence not evidence | New evidence-artifact standard (#126) |
| B1048 | `PHASE_DIR` scope bug | Function-local var used at outer scope (preflight) | B1049 fix |
| B1049 | A-1 fix | `PHASE_DIR` preflight reference now literal `output_phase_1` | Confirmed via rendered file (B1050 Sub-B audit) |
| B1050 | Class A-F adversarial scan | 7 actionable bugs (C-1 critical, A-2/3 low, C-2/4/5 moderate, C-3 moderate) | Pyramid tests proposed; not all applied |
| B1051 | (next) | Pyramid tests for B1050 findings | Pending |

---

## 5. Failure-mode catalog (R6 triage reference)

| Stage | Failure | Sentinel | Owner action |
|---|---|---|---|
| Pre-flight | IAM SSM not attached | (laptop `exit 1` before launch) | `aws iam attach-role-policy ...` |
| Pre-flight | user-data >16KB base64 | (laptop `exit 1` before launch) | Externalize to S3 (Doc F Section 3) |
| Bootstrap | Python install fails | `PYTHON_3_11_FAIL` | Investigate AL2023 `dnf` log |
| Bootstrap | Mandatory deps missing | `MANDATORY_DEPS_MISSING` | Pip resolution issue; check `requirements.txt` |
| Bootstrap | Strategy import fails | `STRATEGY_IMPORT_FAIL` | Repo state issue; verify SHA pinned |
| Preflight | Coverage check fails | `B1019_PREFLIGHT_FAIL` | `data_prefetch` incomplete; check `DATA_SYNC_DONE` |
| Phase N | Engine crashes | `PHASE_<N>_FAIL rc=<X>` | Read `engine.log` from S3 |
| Phase N | Monitor HALT-CRITICAL | `PHASE_<N>_B1019_HALT` | Read `b1019_monitor.log` |
| Phase N | Watchdog timeout | `PHASE_<N>_TIMEOUT_HALT` | MAX_MIN too tight; bump or investigate |
| Phase N | No trade_log | `PHASE_<N>_FAIL no-trade-log` | Engine silent failure; read engine.log |
| Post-run | trade_log missing | `[B1043 F-08 WARN]` | Phase 4 failed silently; AUTOLADDER_COMPLETE still fires |

---

## 6. Cumulative timing + 17-hr cap

| Phase | MAX_MIN | Expected wall-clock | Expected cost |
|---|---|---|---|
| Bootstrap | n/a | 15-25 min | $0.30-0.50 |
| Phase 1 | 120 | 30-90 min | $0.50-1.50 |
| Phase 2 | 180 | 1-2.5 hr | $1.50-3.00 |
| Phase 3 | 240 | 1.5-3.5 hr | $3.00-4.50 |
| Phase 4 | 480 | 1.4-2.8 hr (Sub-C) | $2.00-5.00 |
| Post-run | n/a | ~2 min | negligible |
| **Total** | **17 hr cap** | **~5-12 hr expected** | **~$7-15 expected** |

**Cap is honest upper-bound** per Sub-C timing analysis (B1028 1h 38m actual vs 30-min estimate precedent). The 17-hr ceiling is the `shutdown +1` failsafe; the spot price * 17 hr * c6a.16xlarge ($1.05/hr) = ~$18 absolute cost ceiling.

---

## 7. L86/L95 cost-discipline embedded

**L86:** "Past mistakes cost $150 in discarded work - same pattern, different operation, same outcome unless this discipline is mandatory."
**L95:** "All API runs costing money: small test batch -> manual review -> owner approval -> scale. NEVER jump from data ready to full run."

**How R5 ladder embeds this:**

1. **Phase 1 = small test batch** (single ticker, $0.50-1.50 ceiling).
2. **Phase 1 PASS -> owner-approval gate before Phase 2** (in autonomous mode this is the sentinel `PHASE_1_PASS` landing; in owner-gated mode it's an explicit owner OK).
3. **Phase 2 = small scale-up** (10 tickers, $1.50-3.00 ceiling).
4. **Phase 4 only after Phase 3 PASS** (50 tickers proves saturation behavior).
5. **17-hr cap = absolute kill** (spot interruption + watchdog + `shutdown +1` failsafe).
6. **No phase exceeds MAX_MIN** without owner explicit raise.

**R6 must preserve this gating.** Skipping Phase 1 -> Phase 4 directly is a direct L95 violation.

---

## 8. Cross-references

**Code:**
- `scripts/launch_r5_master_4y_v2.sh` (canonical launcher; B1042+B1043+B1045+B1049 fixes)
- `scripts/b1019_a5_phase_1_preflight_coverage_check.py` (preflight)
- `scripts/b1019_phase_1_runtime_monitor.py` (per-phase B1019 monitor wrap)
- `scripts/b1019_phase_1_post_run_analyzer.py` (post-Phase-4 analyzer)
- `backtest/engine/backtest.py:574-619` (Layer 1 `engine_state.json` emit; F-01 schema match)
- `backtest/run_phase1a.py:_install_sigterm_handler` (F-06 SIGTERM flush)
- `backtest/run_phase1a.py:main` HoldoutUnlock context (B1045 fix #27)

**Docs:**
- `docs/r6_workflow_reuse/AWS_LAUNCH_PLAYBOOK.md` (Doc F - AWS operational mechanics)
- `docs/PRODUCER_CONSUMER_PAIRS.md` (42-row sentinel + output registry)
- `output_audit/b1046_phase_d_r5_sub_phases_2026_06_28.md` (B1046 source; this doc extends it for R6)
- `output_audit/b1043_phase_d_timing_analysis_2026_06_28.md` (Sub-C timing math)
- `output_audit/b1043_adversarial_monitor_review_2026_06_28.md` (Sub-A monitor review)
- `output_audit/b1050_launch_script_class_a_to_f_audit_2026_06_28.md` (B1050 7-bug audit)
- `PATH_TO_PHASE_1B_ALPHA.md` Section 13.7 (15 launch gates)

**CHECKLIST items in force:**
- #77 doc Source header
- #116 user-data 16KB
- #117 monitor arm-at-event
- #121 monitor-armed grep
- #122 silent-failure pairing
- #123 phase-ladder timing validation
- #124 IAM SSM precondition
- #125 engine progress emit
- #126 designed-vs-verified evidence artifact
- #127 AWS smoke mandatory gate

**Memory rules in force:**
- `feedback_monitor_design_vs_operational_gap`
- `feedback_silent_failure_pairing_rule`
- `feedback_phase_ladder_timing_validation`
- `feedback_aws_user_data_size_preflight`
- `feedback_ask_before_relaunching_corrected_version`
- `feedback_banner_is_status_not_scope_authority`
- `feedback_readiness_audit_must_verify_universe_scope`

---

## 9. Honest gap acknowledgments for R6

1. **Phase 4 wall-clock is unverified empirically.** The 1.4-2.8 hr estimate is Sub-C extrapolation from Phase C smoke. R5 production run will be the first empirical Phase 4-size measurement. R6 should use R5's measured wall-clock as the empirical anchor (per `feedback_phase_ladder_timing_validation`).
2. **Universe scope authority:** PROJECT_PLAN line 193 = Master 1937; banner CLAUDE.md illustrative = T1a 503; ops intersection = 1929. **For R6 verify universe scope with 3-way reconciliation** (PROJECT_PLAN + Master CSV + S3 OHLCV cache).
3. **MASTER_TICKERS format contract** (C-1 from B1050) - verify `master_ops_tickers.txt` is CSV before relying on the python `--%-c "ts=...".split(',')` substitution.
4. **`STRATEGIES_DISABLED_MISSING_PRODUCER` status** - B1035 reversed B975+B984 disablements; R6 should re-verify producers BEFORE launch (per CHECKLIST #44(b)).
