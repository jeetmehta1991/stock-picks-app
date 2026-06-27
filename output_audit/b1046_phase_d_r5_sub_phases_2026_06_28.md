# Phase D R5 Sub-Phase Breakdown

# Source: Council 141 Sub-agent C + scripts/launch_r5_master_4y_v2.sh
# per owner directive 2026-06-28 "Explain all sub phases in phase 5 r5
# launch." per CHECKLIST #77.

## Purpose

Owner asked for a comprehensive explanation of every sub-phase that fires
when `bash scripts/launch_r5_master_4y_v2.sh` is invoked in `MODE=full`.
This is the canonical R5 launch sequence per Council 110 / 119 / 121.

This doc is the operational ground truth for "what happens when we launch
Phase D" - referenced by future councils before R5 launch decisions.

## Top-level launch sequence

```
Local laptop                           AWS EC2 (c6a.16xlarge spot)
============                           ============================
bash scripts/launch_r5_master_4y_v2.sh
   |
   +-- Pre-flight (laptop) -----------------------------------+
   |     CHECKLIST #124 IAM SSM verify                       |
   |     CHECKLIST #121 monitor-armed grep                   |
   |     CHECKLIST #116 user-data 16KB size check            |
   |     (if size>16KB: externalize user-data to S3 +        |
   |      generate small bootstrap loader)                   |
   |                                                         |
   +-- aws ec2 run-instances --user-data <base64> ---->     |
                                                             |
                                                BOOTSTRAP    |
                                                BOOT sentinel|
                                                |            |
                                                +-- Python 3.11 install
                                                +-- git clone repo
                                                +-- venv + pip install
                                                +-- vendored smartmoneyconcepts
                                                +-- DATA_SYNC from S3 (~15 min)
                                                |
                                                +-- B1019 PREFLIGHT
                                                +-- sync_loop (60s S3 sync) bg
                                                |
                                                +-- Phase 1: NVDA x 4y
                                                +-- Phase 2: 10 tickers x 4y
                                                +-- Phase 3: 50 tickers x 4y
                                                +-- Phase 4: Master 1929 x 4y
                                                |
                                                +-- B1019 POST-RUN ANALYZER
                                                +-- AUTOLADDER_COMPLETE
                                                +-- sudo shutdown -h +1
```

## Pre-Phase-1: Bootstrap (15-20 min)

**Sentinels (in order):**

| Sentinel | What it proves | Failure mode |
|---|---|---|
| `BOOTSTRAP_LOADER` | (only when externalized) S3 user-data download path works | bootstrap couldn't reach S3 -> no further sentinels |
| `BOOT` | Instance + AL2023 ready; `/tmp/sentinels/` writable | OS boot failure (rare) |
| `PYTHON_VERSION` | Python 3.11 installed + verifiable | dnf failure, AMI drift |
| `PANDAS_TA_STATUS=0` or `=1` | Optional pandas-ta install result logged (CHECKLIST #122 paired) | always logged; never fatal |
| `SMARTMONEYCONCEPTS_STATUS=1` | B1039 fix: vendored library installed; 18 SMC strategies can fire | `=0` -> SMC strategies short-circuit per SMC_PHASE flag |
| `MANDATORY_DEPS_MISSING` | Only if pandas/numpy/scipy/pyarrow missing | HALT - shutdown +5 |
| `STRATEGY_IMPORT_FAIL` | Only if `from backtest.signals.screener import ALL_STRATEGIES` raises | HALT - shutdown +5 |
| `DATA_SYNC_DONE` | ~3 GB S3 -> instance data_prefetch sync complete | Long-tail (15-25 min normal) |
| `SYNC_LOOP_PID` | 60s background S3 sync loop running | always emitted |

**Pre-Phase-1 last step: B1019 PREFLIGHT (F-07 fix B1043)**

Invokes `scripts/b1019_a5_phase_1_preflight_coverage_check.py`:
- Checks data_prefetch coverage for Phase 1 ticker
- Asserts >=X bars present per source
- Emits `B1019_PREFLIGHT_PASS` or `B1019_PREFLIGHT_FAIL`
- On FAIL: shutdown +5 (no Phase 1 launch)

## Phase 1: NVDA x 4-year (MAX_MIN=120 min per B1043 Sub-C)

**Purpose:** smallest realistic scale validates the full pipeline before
committing to multi-ticker scale. NVDA x 1006 trading days x 219
strategies x 26 exits = ~5,694 cube cells.

**Window:** 2022-05-05 -> 2026-05-05

**MAX_MIN:** 120 min (was 30; raised B1043 per Sub-C extrapolation)

**Sentinels (in order):**

| Sentinel | Time UTC | What it proves |
|---|---|---|
| `PHASE_1_RUNNING n=1` | T+0 | Engine subprocess launched; ENGINE_PID captured via process substitution (F-02 fix) |
| `PHASE_1_B1019_PID` | T+0 | Monitor wrap fired (F-09 fix: now active in all phases) |
| `engine_state.json` emit at sim_day=50 | T+~10 min | F-05 fix: first emit BEFORE 30-min cap; F-01 schema matches monitor reader (simulated_day, cells_completed, status) |
| `engine_state.json` emit at sim_day=100,200,...,1000 | every ~10 min | Continuous progress visibility |
| `trade_log_checkpoint.csv` | every 100 sim-days when trades > 0 | Mid-run trade log persisted to S3 via sync_loop |
| `PHASE_1_PASS n=1` | T+~30-90 min expected | Engine completed cleanly; `trade_log.parquet` exists |

**Failure modes:**

| Failure | Sentinel | Recovery |
|---|---|---|
| Engine HALTs (rc≠0) | `PHASE_1_FAIL rc=<N>` | Ladder aborts; sudo shutdown +5 |
| B1019 detects HALT-CRITICAL | `PHASE_1_B1019_HALT` | Watcher SIGTERMs engine; ladder aborts |
| 120 min watchdog fires | `PHASE_1_TIMEOUT_HALT max=120min` | Watchdog SIGKILLs engine; ladder aborts |
| No trade_log produced | `PHASE_1_FAIL no-trade-log` | Ladder aborts |

**Cost (spot c6a.16xlarge @ ~$1.05/hr):** ~$0.50-1.50

**Why Phase 1 first:** smallest cube validates engine + signal-loader +
exit + writers + dashboard at smallest realistic scale. If Phase 1 PASSes,
the upstream pipeline is proven. Failures in Phase 1 are CHEAP to diagnose.

## Phase 2: 10 tickers x 4-year (MAX_MIN=180 min per B1043 Sub-C)

**Purpose:** validates parallel ticker handling + multi-ticker memory
profile before committing to wider scale.

**Tickers:** `NVDA,AAPL,MSFT,GOOGL,META,XLF,UUP,COIN,SOFI,IONQ`

These are deliberately heterogeneous:
- 4 mega-cap tech (NVDA/AAPL/MSFT/GOOGL/META)
- 1 social (META - also tech)
- 1 broad financial ETF (XLF)
- 1 dollar ETF (UUP - DXY proxy)
- 3 high-vol speculative (COIN/SOFI/IONQ)

**Window:** 2022-05-05 -> 2026-05-05 (same as Phase 1)

**MAX_MIN:** 180 min

**Sentinels:** same pattern as Phase 1 with `_2` suffix

**Cube cells:** 10 x 5,694 = ~56,940

**Cost (spot):** ~$1.50-3.00

**Failure semantics:** if Phase 2 FAILs after Phase 1 PASSed, the bug is
multi-ticker-specific (pool concurrency, memory, regime classification
on heterogeneous tickers).

## Phase 3: 50 tickers x 4-year (MAX_MIN=240 min per B1043 Sub-C)

**Purpose:** validates stratified-sample scale; catches issues that
emerge at moderate scale before R5 commits.

**Tickers:** stride sample from Master 1929 universe:
```python
ts = MASTER_TICKERS.split(',')
step = max(1, len(ts) // 50)
TICKERS_PHASE_3 = ','.join(ts[::step][:50])
```

**Cube cells:** 50 x 5,694 = ~284,700

**Cost (spot):** ~$3.00-4.50

**Why stride sample (not stratified-vol or other):** simplicity. Phase 3
is a SCALE test not a representative-test; bias is acceptable because
Phase 4 tests full universe.

## Phase 4: R5 Master 1929 x 4-year (MAX_MIN=480 min per B1043 Sub-C)

**Purpose:** THE PRODUCTION RUN. Full Phase 1A-beta empirical cube.

**Tickers:** Master Dedup CSV intersection with S3 OHLCV cache:
1,929 tickers (per CLAUDE.md banner; PROJECT_PLAN.md spec line 193 = Master 1937; ops intersection = 1929)

**Window:** 2022-05-05 -> 2026-05-05 (4y per PROJECT_PLAN spec)

**MAX_MIN:** 480 min (8 hr; raised from 240 per B1043 Sub-C timing)

**Cube cells:** 1,929 x 5,694 = ~10,983,726 (~11M cells)

**Cost (spot):** ~$5-10 spot for full 8-hr cap, but realistic ~$2-5 for
expected 1.4-2.8 hr run per Sub-C timing analysis

**Engine self-timeout:**
- `--warn-run-hours=4.0` -> WARN log at 4 hr
- `--max-run-hours=6.0` -> engine self-flush + sys.exit(1) at 6 hr
- B1043 F-06 SIGTERM handler -> kill -15 flushes checkpoint before exit

**Sentinels:** same pattern as previous phases with `_4_r5` suffix

**This is the "R5" of R5 cube run.** Strategy verdicts derive from this
phase's `trade_log.parquet` consumed by `metrics.py::compute_strategy_metrics`.

## Post-Phase-4: Post-Run Analyzer (B1043 F-08 fix)

Invokes `scripts/b1019_phase_1_post_run_analyzer.py` against
`output_phase_4_r5/trade_log.parquet`:

- Reads trade log
- Computes per-strategy summary stats (B1019 standard set)
- Emits `b1019_post_run_report.json` (machine-readable)
- Emits `b1019_post_run_summary.md` (owner-readable)
- Syncs both to S3 as `B1019_POST_RUN_REPORT.json` + `B1019_POST_RUN_SUMMARY.md`

If Phase 4 trade_log missing: emits `[B1043 F-08 WARN]` and skips
(non-fatal; AUTOLADDER_COMPLETE still fires).

## Final: AUTOLADDER_COMPLETE + Shutdown

```
AUTOLADDER_COMPLETE <UTC> scope=Master-1929 4y
sudo shutdown -h +1
```

Instance self-terminates +1 min after the sentinel lands. S3 sync_loop
catches everything before shutdown.

## Total expected cost + wall-clock

| Phase | MAX_MIN | Expected wall-clock | Expected cost (spot) |
|---|---|---|---|
| Bootstrap | n/a | ~15-25 min | $0.30-0.50 |
| Phase 1 (NVDA) | 120 min | 30-90 min | $0.50-1.50 |
| Phase 2 (10) | 180 min | 1-2.5 hr | $1.50-3.00 |
| Phase 3 (50) | 240 min | 1.5-3.5 hr | $3.00-4.50 |
| Phase 4 (R5) | 480 min | 1.4-2.8 hr (Sub-C est) | $2.00-5.00 |
| Post-run | n/a | ~2 min | negligible |
| **Total** | **17 hr cap** | **~5-12 hr expected** | **~$7-15 expected** |

Cap is honest upper-bound per Sub-C timing analysis (B1028 1h38m
actual vs 30-min estimate precedent). Expected is empirical
extrapolation from Phase C v1+v2 smokes.

## Failure-mode catalog

| Stage | Failure | Sentinel | Owner-action |
|---|---|---|---|
| Bootstrap | Python install fails | `PYTHON_3_11_FAIL` | Investigate AL2023 dnf |
| Bootstrap | Mandatory deps missing | `MANDATORY_DEPS_MISSING` | Pip resolution issue |
| Bootstrap | Strategy import fails | `STRATEGY_IMPORT_FAIL` | Repo state issue |
| Preflight | Coverage check fails | `B1019_PREFLIGHT_FAIL` | data_prefetch incomplete |
| Phase N | Engine crashes | `PHASE_N_FAIL rc=<X>` | Read engine.log |
| Phase N | Monitor HALT-CRITICAL | `PHASE_N_B1019_HALT` | Read b1019_monitor.log |
| Phase N | Watchdog timeout | `PHASE_N_TIMEOUT_HALT` | MAX_MIN too tight |
| Post-run | trade_log missing | `[B1043 F-08 WARN]` | Phase 4 must have failed silently |

## Cross-references

- `scripts/launch_r5_master_4y_v2.sh` (canonical launcher; B1042 + B1043 + B1045 fixes)
- `scripts/b1019_a5_phase_1_preflight_coverage_check.py` (preflight)
- `scripts/b1019_phase_1_runtime_monitor.py` (per-phase monitor wrap)
- `scripts/b1019_phase_1_post_run_analyzer.py` (post-Phase-4 analyzer)
- `backtest/engine/backtest.py:574-619` (Layer 1 engine_state.json emit; F-01 schema match)
- `backtest/run_phase1a.py:_install_sigterm_handler` (F-06 fix; SIGTERM flush)
- `backtest/run_phase1a.py:main` HoldoutUnlock context (B1045 fix #27)
- `output_audit/b1043_phase_d_timing_analysis_2026_06_28.md` (Sub-C timing analysis)
- `output_audit/b1043_adversarial_monitor_review_2026_06_28.md` (Sub-A monitor review)
- `docs/PRODUCER_CONSUMER_PAIRS.md` (42-row registry covering all sentinels + outputs)
- CHECKLIST #116/#117/#121/#122/#123/#124/#125/#126/#127 (governance)
- PATH_TO_PHASE_1B_ALPHA.md Section 13.7 (15 launch gates)
