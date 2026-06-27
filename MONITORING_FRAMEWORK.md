# Monitoring Framework

**Created 2026-05-28** (owner directive: "Document monitoring framework in a separate md file"; CHECKLIST #92 explicit approval given).

> **B1029 doc-sync 2026-06-27:** New monitoring components SHIPPED post-B1019 (Council 108 Option-5 Modified 7-enhancement bundle owner-approved): (1) `scripts/b1019_a5_phase_1_preflight_coverage_check.py` — A5 PRE-FLIGHT signal-coverage completeness; (2) `scripts/b1019_phase_1_runtime_monitor.py` — A1 per-strategy fire-rate vs B660 baseline + B2 schema-invariant sentinel + D1 cube-cell completion ETA + F1 periodic owner-chatback; (3) `scripts/b1019_phase_1_post_run_analyzer.py` — D2 dimension-rollup + F2 structured JSON report; (4) `output_audit/b1019_f2_structured_log_schema.json` — F2 schema spec. Plus AWS direct-execution monitoring: persistent Bash `Monitor` polls S3 sentinels (`PHASE_N_RUNNING/PASS/FAIL` + `AUTOLADDER_BOOT/COMPLETE`) every 90s; CloudWatch billing alarms at $5/$10/$20 (`batch395-phase1-cost-5usd` + `batch395-autoladder-cost-10usd` + `batch395-autoladder-cost-20usd`); instance `AutoTerminateAt=launch+10hr` tag for lifetime cap. R5 LAUNCHED 2026-06-27 B1028 on AWS i-0940a53c75d049381 using this monitoring stack.

**Status.** Canonical reference for every monitor / heartbeat / health-check / watchdog / forensic check that runs across Phase 1A-β (cube), Phase 1A-α (rules-only deployment), Phase 1B-α (agent overlay), Stage 3 paper-trading, and Stage 4 live trading. Single source of truth for what each monitor does, where it lives, what it ACTS ON, and who consumes its output. Maintained per `feedback_no_write_only_md_files.md` — every entry below has a documented consumer or action-path.

---

## Core principles (HARD RULES)

1. **CHECKLIST #91 — Monitoring that doesn't ACT or get READ is dead infrastructure.** A monitor must have one of: (a) an ACT-ON-DETECTION path (auto-terminate / auto-relaunch / auto-abort downstream), OR (b) an ingested digest that the orchestrator or I read at every status request. Log-only is unacceptable. Multi-layer monitors must have DIFFERENT act-on paths (two log-only monitors are still zero monitors). Codified after L162 (Batch 411 lesson — owner critique: *"What is the use of monitoring if you don't even read the results?"*).
2. **CHECKLIST #90 — Status updates re-verify current state via API/files at report time, not from memory.** Caching prior state from earlier in the same session is NOT acceptable for resources that can change asynchronously (spot instances, billable jobs, jobs with hard timeouts). Codified after L161 (Batch 410 lesson — batch_3 spot-reclaim reported as RUNNING for 1.5h).
3. **`feedback_monitor_intermediate_counts.md` — Monitor intermediate counts during long runs.** Don't wait for terminal events. Per-100-day cumulative-count check would have caught the Phase 1A-β 20× trade-count drop at ~10-15% completion (Batch 377 lesson).
4. **`feedback_strategy_x_exit_cell_analysis.md` — Forensic verdicts at (strategy × exit × regime) CELL level, never aggregated.** Batch-aggregate PnL (bear/bull/neutral sums) is noise dressed as signal.

---

## Layer inventory

### L0 — Engine wall-time guard (in-process)

| Field | Value |
|---|---|
| Code | `backtest/run_phase1a.py` + `backtest/engine/backtest.py` |
| Shipped | Batch 394 (2026-05-27) |
| Auto-enable | `--phase=1a-beta` → `--warn-run-hours=4.0` + `--max-run-hours=6.0` |
| **Act on detection** | WARN: log a single `[WALLTIME-WARN]` line and continue. HARD KILL: flush final checkpoint via `save_all_outputs` then `sys.exit(1)`. Engine-side circuit-breaker; survives orchestrator death. |
| Consumer | Watchdog (L4) backs this up at +5 min if engine hangs past `max_run_hours`. |
| Purpose | Prevent runaway cube runs. Belt-and-braces with L4 external timeout. |

### L1 — In-bootstrap heartbeat (per-AWS-instance)

| Field | Value |
|---|---|
| Code | `scripts/aws_batch395_bootstrap.sh` (line 144 — `aws s3 cp - s3://.../heartbeat/batch_N.txt`) |
| Shipped | Batch 395 (2026-05-27) |
| Cadence | Every 5 minutes from bootstrap onwards |
| Payload | `ts=<UTC ISO>`, `batch_index=N`, `elapsed_seconds=<int>`, `tmux=alive`, plus last 2 screener log lines (incl. engine-date) |
| **Act on detection** | None at L1. Pure write-only artifact for downstream consumption. |
| Consumer | L4 orchestrator (Batch 411 `aws_batch395_parallel.py::read_heartbeat`); cube-run status reports |
| Failure mode caught earlier | L162 — heartbeats landed but went unread for 10h. Fixed by L4 reading them every poll. |

### L2 — Per-strategy silent-producer logging (in-screener)

| Field | Value |
|---|---|
| Code | `backtest/signals/screener.py::_log_silent_producer_failure` / `_log_silent_producer_empty` |
| Shipped | Batch 416 (2026-05-28) |
| Rate-limited | 1 log per (producer, exception_type) per process; 1 log per producer per process for empty-return |
| **Act on detection** | Emits one-shot WARN to `backtest.signals.screener` logger. No abort; trade continues without the failed producer's signals. |
| Consumer | Engine log file → S3 sync → owner read post-run |
| Failure mode caught | SMC silent-failure investigation 2026-05-28: 0 of 29,159 trades had any smc_* key despite `compute_smc_signals` returning 28 keys in isolation. Pre-Batch-416 `try/except: pass` blocks hid the AWS-environment failure. |
| Producers instrumented | `classification_change`, `institutional_signal`, `smc_ict` |

### L3 — Per-batch forensic check (post-`_COMPLETE`)

| Field | Value |
|---|---|
| Code | `scripts/aws_batch395_forensic_per_batch.py` |
| Shipped | Batch 409 (2026-05-27) |
| Triggered by | L4 orchestrator detecting new `outputs/batch_N/_COMPLETE` sentinel in S3 |
| Checks (8 ABORT + 7 WARN triggers — see source) | engine log clean / strategy fire coverage / **per-(strategy×exit×regime) cell-level outputs** / cube cell n≥5 coverage / signal fire rates / trade volume vs baseline / regime PnL |
| **Act on detection** | rc=0 PASS, rc=1 WARN (continue), rc=2 ABORT (terminate all downstream batches + alert). Verdict JSON uploaded to `s3://bucket/forensic/batch_N.json`. |
| Consumer | L4 orchestrator (auto-aborts on rc=2). Post-merge owner review. |
| Known gap | Current checks include some batch-aggregate PnL (e.g., `all_regimes_negative_pnl`) which is noise per `feedback_strategy_x_exit_cell_analysis`. Owner-flagged 2026-05-28: aggregate findings ignore; only cell-level cube data informs Stage 4 decisions. |

### L4 — Cross-batch orchestrator + action-taking monitor

| Field | Value |
|---|---|
| Code | `scripts/aws_batch395_parallel.py` (action-taking variant) + `scripts/aws_batch395_monitor.py` (read-only multi-instance) |
| Action-taking variant shipped | Batch 411 (2026-05-27) |
| Slot logic | Batch 424 (2026-05-28): binary `ondemand_busy`/`spot_busy` flags → integer `ondemand_count`/`spot_count` counters. `--spot-slots` (default 1) + `--od-slots` (default 1). Shape A topology = `--spot-slots 3 --od-slots 0` = 3 × c7a.8xlarge spot = 96 vCPU = full quota ≈ $9.30 / ~5h cube wall-time. |
| Cadence | 5-minute poll loop |
| **Act on detection** | (a) Heartbeat stale > 30 min → `terminate_instance` + re-add to `pending` → next poll relaunches. (b) Spot reclaim detected via `describe-spot-instance-requests` → same auto-relaunch. (c) Per-poll one-line `[DIGEST hh:mmZ b1=DONE b3=PENDING b4=s/120m@2025-06-13(hb15s) b5=o/40m@2023-01-25(hb45s)]` summary line — this is what I read at every owner status request, replacing recall-from-memory. (d) Forensic rc=2 ABORT → terminate all downstream. |
| Consumer | Owner status reports; per-poll digest is the read protocol |
| **Stdout caveat (Batch 424 observation)** | When orchestrator runs with stdout redirected to file (background launch), Python block-buffers parent-process prints — `[INIT] parallel runner`, `[LAUNCH] batch_N spot`, `[STATE]`, `[DIGEST]` lines never flush in real-time. The `subprocess.run(capture_output=False)` calls to `aws_batch395_launch.py` DO flow through inherited stdout — so `[OK] batch_N: launched i-...` and `[FORENSIC batch_N] verdict=...` ARE visible in real-time. **Monitor patterns must include launch.py / forensic markers, not just orchestrator markers.** Real-time status verification still uses direct S3 + EC2 queries (per L4 protocol below), not log-tail. |
| **PATH prerequisite** | `aws` binary must be on PATH BEFORE the orchestrator starts (it calls `subprocess.run(["aws", ...])`). On Windows: prepend `C:\Program Files\Amazon\AWSCLIV2` to PATH in the parent shell. Symptom of missing PATH: `FileNotFoundError: [WinError 2]` at first poll. |
| Failure mode caught | L162 — pre-Batch-411 `monitor_phase_1a_beta_health.py` died at startup on PowerShell `NativeCommandError` and was never re-read across 10h. Batch 411 folds action-taking INTO the orchestrator so the same process that polls also relaunches + emits digest. |

### L5 — Per-(strategy × exit) cube cell forensic (post-merge)

| Field | Value |
|---|---|
| Code | `scripts/optimize_strategies_from_cube.py` (Batches 388 + 391) |
| Shipped | Batch 388 (Dim A-I per strategy) + Batch 391 (`analyze_exit_methods` 3-layer) |
| Inputs | `output_batch395_final/trade_log.csv` + `trade_exit_detail.csv` + `skipped_trades.csv` |
| **Outputs (Stage 3 of locked workflow)** | `optimization_summary.md` + 101 per-strategy JSONs + `exit_method_analysis.json` + `producer_zero_post_cube_audit.json` |
| Verdict gate | DEC-426 5-Gate per cell: n ≥ 30, p < 0.05 Bonferroni (4625 cells/regime), PSR ≥ 0.95, t ≥ 3.4, R:R ≥ 2.0 |
| **Act on detection** | None automatically — owner-mediated per locked-workflow Stage 4 (per-change approval). Surfaces cell-level winners (`STRATEGY_EXIT_OVERRIDE` candidates) + losers (deprecation candidates) + producer-zero gaps |
| Consumer | Dashboard tabs 10-13 (Batch 419); owner review via `dashboard_phase_1a/index.html` |

### L6 — Walk-forward validator (Stage 6 of locked workflow)

| Field | Value |
|---|---|
| Code | `scripts/walk_forward_batch414_cells.py` + `backtest/engine/improvements.py::run_walk_forward` |
| Shipped | Batch 414 walk-forward script (2026-05-28) on top of DEC-505 4-fold framework |
| Methodology | DEC-505 4-fold expanding-window walk-forward. 1y warmup + 4×1y disjoint OOS folds. |
| **Act on detection** | rc=0 GATE OPEN (≥1 strategy passes Sharpe ≥ 0.7 OOS in ≥1 fold), rc=2 GATE LOCKED. CLAUDE.md owner-gate rule: Phase 1B-α $300 Haiku budget eligible only when GATE OPEN. |
| Consumer | Owner 1A-α gate decision; auto-emitted JSON at `output_batch395_final/walk_forward_batch414_cells.json` |

### L7 — Per-turn doc-sync sweep (process-level)

| Field | Value |
|---|---|
| Code | preflight hook (`scripts/preflight.py`) + per-turn discipline |
| Codified | CHECKLIST #67 / #67.b / #75; `feedback_pyramid_no_exceptions.md`; `feedback_all_docs_sweep.md` |
| **Act on detection** | Preflight BLOCKs commit on rule violations (C1 Unicode / C3 canonical-source / count-sync drift). Hook patched in Batch 411 to exclude `archive/**` paths. |
| Consumer | Every commit; per-turn doc sync mandatory before push |

---

## Status-reporting protocol (CHECKLIST #90)

Before issuing any status update that references long-running resources:

1. **EC2 / spot instances** — run `aws ec2 describe-instances` for current `State.Name` + `StateReason.Message`; for spot, also `describe-spot-instance-requests` for `Status.Code`.
2. **S3 sentinels** — `aws s3 ls s3://bucket/path/_COMPLETE` for each tracked batch.
3. **S3 heartbeats** — pull each tracked batch's heartbeat file + compare `ts=` to current time (> 15 min stale = surface in report).
4. **Background tasks** — read tail of each task's output file at report time. **Caveat (Batch 424):** when the task is the L4 orchestrator with stdout redirected, the parent-process print lines (`[DIGEST]`, `[STATE]`) may be stuck in Python's block buffer. Treat absence of digest lines as "buffered, not absent" — fall back to direct S3 + EC2 queries (steps 1-3).
5. **L4 monitor output** — read the latest poll digest and include any WARN/KILL signals. If digest is missing due to buffering (see step 4), reconstruct status from S3 `_COMPLETE` + `heartbeat/` + `forensic/` listings.

Caching prior state from earlier in the same session is NOT acceptable for resources that can change asynchronously. Cost of re-verification = 1-2 seconds; cost of stale reporting = the entire delta between actual change and detection (1.5 hours in the Batch 410 incident).

---

## Pre-launch operational protocol (L4)

Before invoking `scripts/aws_batch395_parallel.py` for a fresh cube run:

1. **PATH** — confirm `aws` is on PATH in the parent shell (`which aws` returns a path). If not: `export PATH="/c/Program Files/Amazon/AWSCLIV2:$PATH"` (Git Bash) or PowerShell equivalent.
2. **Quota** — confirm spot vCPU quota covers the topology: 3 × c7a.8xlarge = 96 vCPU. `aws service-quotas get-service-quota --quota-code L-34B43A08` (or trust an explicit owner quota report — the `batch395-runner` IAM user lacks ServiceQuotas read permission by default).
3. **Live spot price floor** — `aws ec2 describe-spot-price-history --instance-types c7a.8xlarge --product-descriptions "Linux/UNIX"` for the cheapest AZ. Compare to `--spot-max-price` (default 0.90) and update if spot floor exceeds it.
4. **S3 archive prior run** — `aws s3 mv s3://bucket/outputs/ s3://bucket/outputs_<YYYY-MM-DD>_run/ --recursive` (and same for `heartbeat/`, `forensic/`, `final/`). Skipping archive = orchestrator finds prior `_COMPLETE` markers and short-circuits, treating "already done" as success. Same-bucket S3 mv = $0 in-region transfer.
5. **AMI + key pair + SG + IAM role** — confirm `aws_batch395_state.json` or recent successful launch shows still-valid resource IDs. AMI must be `available` (`aws ec2 describe-images --image-ids <id>`).
6. **Commit hash** — `--commit <sha>` must reference a pushed commit (the user-data bootstrap script does `git fetch && git checkout <sha>`); CI Test Pyramid must be green for that sha.
7. **Slot flags** — explicit `--spot-slots N --od-slots M` matching the approved Shape (do not rely on Batch 424 defaults 1+1, which were preserved only for backward-compat).

---

## Forensic verdict semantics (L3 + L5)

**Per-batch (L3 — `aws_batch395_forensic_per_batch.py` exit codes):**
- `rc=0` PASS → continue downstream
- `rc=1` WARN → continue; surface in owner report
- `rc=2` ABORT → terminate all downstream batches; bug fix + full relaunch required (owner directive Batch 409)

**Per-cell (L5 — DEC-426 5-Gate):**
- `n ≥ 30` AND `p < 0.05` Bonferroni AND `PSR ≥ 0.95` AND `t ≥ 3.4` AND `R:R ≥ 2.0` → strict PASS
- 4-of-5 (excludes PSR) → relaxed PASS (verdict label "PASS" but `five_gate_pass=False`)
- Otherwise FAIL
- `n < 30` → INSUFFICIENT_SAMPLE

**1A-α gate (CLAUDE.md owner gate):**
- ≥1 strategy with rules-only Sharpe ≥ 0.7 OOS in ≥1 regime → GATE OPEN
- Otherwise GATE LOCKED → $300 Phase 1B-α agent budget NOT eligible to commit

---

## Known gaps + future work

| Gap | Where | Open Question |
|---|---|---|
| L3 forensic has batch-aggregate PnL checks (`all_regimes_negative_pnl`) which conflict with `feedback_strategy_x_exit_cell_analysis` cell-level mandate | `scripts/aws_batch395_forensic_per_batch.py` | Should L3 ABORT triggers be cell-level (verdict matrix) instead of batch-aggregate? Owner deferred 2026-05-28. |
| L2 instrumentation (Batch 416) active in cube re-run launched 2026-05-28 commit 948769bf2 Shape A | `backtest/signals/screener.py` | First diagnostic logs surface in batch_1..5 engine logs post-merge; SMC silent-failure root cause expected in the log tail |
| L4 digest format is single-line; not all signals visible (e.g., engine-date stuck for 2+ polls = stall not yet detected) | `scripts/aws_batch395_parallel.py` | Add `[DIGEST stale-detect]` row if engine_date doesn't advance across N polls |
| L5 PSR gate at 0.95 may be too aggressive for current universe (0 strict-5-gate cells in `output_batch395_final` despite 26 cells passing 4 of 5) | `scripts/optimize_strategies_from_cube.py::_dec426_verdict` | Owner-discussion: lower PSR to 0.9 OR multi-regime PASS requirement OR accept current threshold |
| L6 walk-forward only computed for Batch 414 winners (9 strategies × 4 folds) | `scripts/walk_forward_batch414_cells.py` | Extend to all 100 fired strategies post-cube-rerun |
| Stage 3 paper-trading monitoring | `STAGE_3_PAPER_TRADING_ACTIVATION.md` | Future scope; live broker monitoring (Stage 4) |
| Stage 4 live-trading monitoring | `scripts/run_live_end_of_day.py` (Batch 373) | Future scope; IB fills + slippage reconciliation |

---

## Failure-mode history (lessons codified)

| Lesson | Batch | Failure | Resolution |
|---|---|---|---|
| L161 / CHECKLIST #90 | 410 | batch_3 spot-reclaim reported as RUNNING for 1.5h (cached state from launch event, not re-queried) | Status updates re-verify current state via API/files at report time |
| L162 / CHECKLIST #91 | 411 | L4 14-check monitor died at startup on PowerShell `NativeCommandError`; produced 9 lines total over 10h; never re-read. S3 heartbeats also went unread. | Action-taking monitor folded INTO orchestrator with per-poll digest |
| (SMC silent-failure) | 416 | 0 of 29,159 trades had any smc_* key despite `compute_smc_signals` returning 28 keys in isolation. `try/except: pass` swallowed actual AWS-environment error. | Replace silent passes with rate-limited diagnostic logging helpers |
| (L4 stdout buffering) | 424 | Orchestrator parent-process prints (`[DIGEST]`, `[STATE]`, `[LAUNCH]`) silently buffered when stdout redirected to file in background launch; Monitor patterns targeting orchestrator markers fired zero events across an hour of cube run, while launch.py + forensic markers DID flow through. | Document buffering caveat in L4 row + Status-reporting step 4; use direct S3/EC2 queries (not log-tail) for status; include launch.py/forensic markers in Monitor patterns. Open follow-up: `PYTHONUNBUFFERED=1` env var or `-u` flag on next launch to flush in real-time. |
| (AWS CLI PATH prereq) | 424 | First orchestrator launch failed with `FileNotFoundError: [WinError 2]` because `aws` was not on PATH in the parent shell — the orchestrator calls `subprocess.run(["aws", ...])` requiring `aws` resolvable. | Documented in L4 row + Pre-launch operational protocol step 1. |

---

## Cross-references

- `CLAUDE.md` — owner gate at 1A-α; auto-enabled cube flags table; HARD RULES on git/PAT/destructive operations
- `CHECKLIST.md` — #67 doc-sync per turn; #69 full 13-tier pyramid; #90 status updates re-verify; #91 monitor must act; #92 no new .md without approval
- `LEARNINGS.md` — L161 status updates; L162 monitor without action-on-read
- `PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md` — locked workflow Stage 1-6; locks dashboard expectations per stage
- `PHASE_1A_BETA_STATUS.md` — **ARCHIVED B893 2026-06-18** per owner approval (see `.archive/2026-06-18-stale-md/`); live run-readiness now in EXECUTION_QUEUE.md (Completed log + TIER entries)
- Feedback memory: `feedback_monitor_intermediate_counts.md`, `feedback_no_write_only_md_files.md`, `feedback_strategy_x_exit_cell_analysis.md`, `feedback_audit_recommendations_against_existing_directives.md`
