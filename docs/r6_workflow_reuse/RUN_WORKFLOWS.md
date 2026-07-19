<!-- Source: per CHECKLIST #77 canonical-source; B1313 2026-07-18 owner directive "document local and aws run workflows, gates, etc. everything in the r6 document" -->

<!-- CANONICAL SYNC BANNER (B1313 2026-07-18) - READ FIRST -->
> **Sync status:** Canonical current state (B1312):
> - `len(ALL_STRATEGIES) = 219`; `STRATEGIES_DISABLED_MISSING_PRODUCER = set()`; cube = 219 x 26 = 5,694 cells/ticker
> - Test count: 880 passed, 2 skipped on test_unit + test_integration (the canonical pyramid; the full `backtest/tests/` dir also carries per-batch pins some of which are platform-sensitive - see Section 6A)
> - CHECKLIST items #1-#158, LEARNINGS through L209, latest batch B1312
> - Backtest window LOCKED for the entire R5 process: **2022-05-05 -> 2026-05-05** (~1002 NYSE trading days)

---

# Run Workflows (Local + AWS) & Unified Gate Reference

# Source: B1313 synthesis of the B1260-B1312 execution lineage (this session's chunk-based model) per owner directive 2026-07-18 per CHECKLIST #77.

**Doc G of the r6_workflow_reuse bundle.**

**Why this doc exists:** Docs A (`R5_WORKFLOW.md`) and F (`AWS_LAUNCH_PLAYBOOK.md`) describe the *original monolith autoladder* (`launch_r5_master_4y_v2.sh`, single instance runs all phases 1->4 gated by `PHASE_N_PASS` sentinels). This session replaced that with a **chunk-based model**: the universe is partitioned into ticker-disjoint chunks, each chunk runs either **locally** (laptop, free) or as an **AWS spot instance** (`scripts/aws_chunk_launch.py`), and the chunk outputs are merged into one cube. This doc is the ground truth for the current model. Docs A/F remain valid for the sentinel contract + AWS-mechanics recipes they carry; this doc supersedes them for *how a run is actually structured and gated today*.

---

## How to use this in R6

Read this doc **first** for the current model, then Doc F for AWS-mechanics recipes (AZ failover, spot-capacity errors, S3 externalization) that still apply. Treat `scripts/aws_chunk_launch.py` (AWS) and `backtest/run_phase1a.py` (local) as the executable artifacts and this doc as the spec they implement.

**Specific R6 consumers:**
1. R6 run-planning — Section 1 (execution modes) + Section 2 (validation ladder).
2. R6 local run — Section 3.
3. R6 AWS spot chunk — Section 4 + Section 5 (resume/controller).
4. R6 commit/turn discipline — Section 6A/6B (gate reference).
5. R6 pre-launch AWS sign-off — Section 6C.
6. R6 merge — Section 7 (**incl. the owner-mandated pre-merge $1 cross-check + env RCA**).
7. R6 budget — Section 8.

---

## 1. Two execution modes

| | LOCAL | AWS SPOT CHUNK |
|---|---|---|
| Command | `python -m backtest.run_phase1a ...` | `python scripts/aws_chunk_launch.py --chunk N [--resume]` |
| Instance | laptop (uses local cores) | `c6a.16xlarge` spot (64 vCPU) |
| Cost | free | ~$0.60-1.05/hr spot |
| Speed | bounded by laptop cores; ~4-5 days for a full ~482-ticker chunk | ~84 sim-days/hr with 16 pool workers; a ~482-ticker chunk ~ 12h (or capped at 8h -> resume) |
| Interruption risk | none (unless laptop sleeps/reboots) | spot reclaim (2-min notice) |
| Best for | 1 chunk in parallel with cloud; zero-budget rungs; the validation-ladder rungs 1-3 | the remaining chunks in parallel; scale |
| Merge-safe with cloud? | **only if env-fingerprint parity holds** (Section 6C Gate 6 / Section 7) | yes (all-cloud is one platform) |

**Hard rule (this session's origin lesson, L207/L208/L209):** LOCAL and AWS produce *slightly different* trade sets even on identical inputs — platform float nondeterminism (Windows/Py3.14 vs Linux/Py3.11 numpy-BLAS) flips threshold-boundary signals (~33% trade-level churn observed; common trades are bit-identical PnL). A clean measurement cube wants **one platform for all merged chunks**. Mixing requires the Section 7 pre-merge cross-check to earn the mix.

---

## 2. Validation ladder + chunk partitioning

**Never jump from "data ready" to full universe** (L86/L95). Scale through rungs; each rung is an owner gate.

| Rung | Scope | Purpose | Mode |
|---|---|---|---|
| 1 | 5 tickers | pipeline sanity | local or cloud |
| 2 | 50 tickers | multi-ticker/regime | local or cloud |
| 3 | 150 tickers (= "Batch A") | scale + first real metrics | local or cloud |
| 4 | full ~1927, **partitioned into 4 ticker-disjoint chunks of ~482** | production cube | chunks run local and/or cloud, merged |

**Chunk partitioning rule:** partition by **ticker**, disjoint sets. Ticker-disjoint chunks `concat` cleanly at merge (proven Gate-6). SPY benchmark is auto-added to every chunk -> the merge dedup (Section 7 fix-c) removes the duplicates. Do NOT partition by date or by strategy-band for the chunk model (that was the monolith's Phase-4 chunking; the current model partitions by ticker to keep each chunk a self-contained cube slice).

**Window is LOCKED:** `--start 2022-05-05 --end 2026-05-05` for every rung and every chunk. ~1002 NYSE trading days (via `pandas_market_calendars`; see Section 6C Gate 6 for the calendar-parity gate).

---

## 3. LOCAL run workflow

### 3.1 Launch
```bash
python -m backtest.run_phase1a --phase 1a-beta \
  --tickers "<CSV of chunk tickers>" \
  --start 2022-05-05 --end 2026-05-05 \
  --no-news --no-walk-forward --no-agents \
  --no-git --no-portfolio-cap --no-dd-halt \
  --screen-pool-workers <N> --output-dir output_chunk<N>
```
- `--screen-pool-workers N`: scale to (cores - 1); leave one core if running a second job.
- Output dir `output_chunk<N>/` accrues `engine_state.json` (progress), `trade_log*.parquet`, checkpoints.

### 3.2 Monitor
Arm a Monitor that tails `output_chunk<N>/engine_state.json` and emits on a cadence (owner default: **hourly** for local). Cover failure signatures, not just progress:
```bash
# emit day/status each poll; the grep alternation must catch crash/hang too
while true; do
  { cat output_chunk<N>/engine_state.json 2>/dev/null | grep -oE '"simulated_day": *[0-9]+'; } || echo "NO-STATE"
  sleep 3600
done
```
Silence is not success — a monitor that only greps progress stays quiet through a crash (memory: `feedback_monitor_baseline_must_scale_with_active_universe` + Monitor tool "coverage" rule).

### 3.3 Resume (local)
The engine checkpoints every 100 sim-days + periodically. To resume after a laptop reboot/kill:
```bash
python -m backtest.run_phase1a ... --resume-from-checkpoint output_chunk<N>
```
It reads `output_chunk<N>/engine_state.json`; if `status != complete` it continues from `simulated_day`. The writer-reader signal contract (`backtest/util/signals_serde.py`, ENG-1 fix B1260) preserves `signals_at_entry` across the resume boundary — do NOT hand-roll `literal_eval` on the checkpoint (that was the ENG-1 wipe bug).

### 3.4 Cadence
Owner-set per run. This session: **local = hourly**, AWS = 15-min (Section 5). Match the monitor timeout to the run wall-clock; `persistent: true` for multi-hour/day runs.

---

## 4. AWS SPOT CHUNK workflow (`scripts/aws_chunk_launch.py`)

### 4.1 One-command launch
```bash
python scripts/aws_chunk_launch.py --chunk N          # fresh
python scripts/aws_chunk_launch.py --chunk N --resume  # from S3 checkpoint
```
Constants (top of the script): `c6a.16xlarge`, spot max `$1.40`, `MAX_RUN_HOURS=8.0`, `POOL_WORKERS=16`, bucket `stock-picks-r5-jm-2026`, region `us-east-1`.

### 4.2 What the launcher does
1. **Presigned URLs (no IAM role needed).** GETs for `payload/r5_code.tar` (~5.8 GB engine+deps), `payload/r5_payload.tar` (~3.2 GB data_prefetch), `chunks/chunk{N}_tickers.txt`, and (on resume) `chunk{N}/ckpt.tar`. PUTs for `chunk{N}/heartbeat.txt`, `chunk{N}/ckpt.tar`, `chunk{N}/artifacts.tar`. This keeps user-data small (no embedded creds; Gate 1 size stays well under 16 KB).
2. **Gate 1 (size) + Gate 3 (monitor-in-userdata)** print PASS/FAIL before `run_instances`.
3. **User-data on the instance:** installs python3.11 + tar, pulls code+payload+tickers, `pip install -r requirements.txt`, (on resume) extracts `ckpt.tar` and adds `--resume-from-checkpoint`, **emits `env_fingerprint.json` (Gate 6)** before the engine burns compute, then runs the same engine command as Section 3.1 with `--max-run-hours 8.0 --warn-run-hours 7.0`.
4. **Self-terminate:** `InstanceInitiatedShutdownBehavior=terminate` + `shutdown -h now` at the end; spot `InstanceInterruptionBehavior=terminate`; 60 GB gp3 root, `DeleteOnTermination`.

### 4.3 Monitor v2 (baked into user-data)
Two background loops on the instance:
- **v2a heartbeat + periodic checkpoint:** every 60 s writes `hb_utc + engine_state.json` to `chunk{N}/heartbeat.txt`; every **5th** beat tars `output_chunk{N}` -> `chunk{N}/ckpt.tar`. Worst-case progress loss on ANY death mode <= 5 min (B1300 Catch 1 — manual/hard kill sends no IMDS notice, so checkpoint shipping cannot be interruption-only).
- **v2b IMDS interruption watcher:** polls `169.254.169.254/.../spot/instance-action` every 5 s; on the 2-min reclaim notice, flushes `ckpt.tar` immediately.

### 4.4 Completion marker (B1312 — do not regress)
After the engine exits, user-data reads `engine_state.json` status and emits:
- `CHUNK{N}_COMPLETE day=<D>` **only if** `status == "complete"` (full-window finalize; `backtest.py:1082`),
- else `CHUNK{N}_CAPPED day=<D> status=<S>`.

**Why:** `--max-run-hours` and spot-interruption leave `status="running"`. The pre-B1312 launcher wrote `COMPLETE` unconditionally after process exit -> chunk 2 capped at day 669/~1002 (67%) yet was marked COMPLETE -> the auto-resume controller saw COMPLETE and stopped a two-thirds-done run. Class rule: **a completion marker must reflect actual completion, not mere process exit.** Pin: `test_b1312_chunk_complete_marker_gated.py`.

---

## 5. Resume + auto-resume controller

### 5.1 Manual resume
`--resume` re-launches, pulls `chunk{N}/ckpt.tar`, continues from the checkpoint's `simulated_day`. Use the **same** `payload/r5_code.tar` the earlier portion ran on — never re-upload newer engine code mid-chunk, or the resumed portion becomes inconsistent with the completed portion.

### 5.2 Auto-resume controller (owner "run-through" option)
A local Monitor script (pattern: `scratchpad/chunk2_resume_controller.sh`) polls `chunk{N}/heartbeat.txt` + the instance state every **15 min** and:
- on a **fresh** `CHUNK{N}_COMPLETE` -> report + stop (then the Section 7 pre-merge reminders + owner-gate the next chunk);
- on instance `terminated/stopped` **without** a fresh COMPLETE (cap or spot reclaim) -> **auto-resume** via `aws_chunk_launch.py --chunk N --resume`, capturing the new instance id;
- **thrash-guard = 3** resumes max (bounded runaway spend), then STOP + escalate;
- checkpoint-existence check before every relaunch (no infinite loop on a missing `ckpt.tar`).

### 5.3 Two freshness guards (both mandatory — B1300 + B1312 lessons)
1. **Stale-marker clear:** before arming the controller, overwrite `chunk{N}/heartbeat.txt` with a fresh no-marker placeholder. The prior run's marker (e.g. a false `COMPLETE`) sits in S3 until the new instance boots (~5-10 min of install); an un-cleared stale marker re-fools the controller (this is the B1300 Catch 2 class — success markers must be freshness-checked).
2. **Launch-epoch guard:** the controller records a `LAUNCH_EPOCH` (UTC) and trusts a terminal marker **only if** its `hb_utc > LAUNCH_EPOCH`. On each auto-resume it updates `LAUNCH_EPOCH`, so a stale marker from a prior boot can never satisfy the check.

---

## 6. Unified gate reference

Three distinct gate systems operate. Do not conflate them.

### 6A. Commit gates C1-C9 (`scripts/preflight.py`, pre-commit hook)
Fire on every `git commit`; a violation BLOCKS the commit (bypass only via `--no-verify`, discouraged).

| Gate | Enforces |
|---|---|
| C1 UNICODE | no unicode in non-docstring runtime code (CHECKLIST #75) |
| C2 EM-DASH | no em-dash in `scripts/*.py` (most common #75 offender) |
| C3 CANONICAL-SOURCE | new docs/dashboards carry a `Source:` declaration (CHECKLIST #77) |
| C4 GIT-COMMIT-CAPTURE | `prefetch_*.py` use the `git_commit_paths()` path-restricted pattern (INV-041) |
| C5 | every `scripts/prefetch_*.py` is registered (INV-041 registry) |
| C6 PYRAMID-STAMP | a GREEN full-pyramid `.pyramid_stamp` exists AND is fresher than every staged `.py` (feedback_pyramid_no_exceptions) |
| C7 BANNED-PATTERNS | a: no `not s.get(...)`; b: no default-`True` strategy gate; c: no relative `data_prefetch` path; d: no `except: pass` silent-swallow |
| C8 QUEUE-ENTRY | the commit stages `EXECUTION_QUEUE.md` (every meaningful change gets a ticket, CHECKLIST #94) |
| C9 DOC-QUEUE-XCHECK | ticket IDs referenced in staged docs exist in the queue; **in merge context, also runs the env-fingerprint parity check** |

**C6 operational note:** the stamp is written by `backtest/tests/conftest.py::pytest_sessionfinish` only when a session includes BOTH `test_unit.py` and `test_integration.py` AND exits 0. Run exactly those two files (`880 passed, 2 skipped`) to produce it — running the whole `backtest/tests/` dir pulls in per-batch pins, some platform-sensitive (e.g. `test_engine_parity_pnl_sum_invariant` fails on float nondeterminism), which turns the session red and refuses the stamp. The canonical pyramid is the two-file set.

### 6B. Turn gate — Stop-hook Gate B (`scripts/verify_turn_compliance.py`)
Fires when a turn tries to end. Exit 2 BLOCKS turn-end if tracked files are modified-but-uncommitted (enforces CHECKLIST #67 per-turn doc-sweep + commit). Escape for legitimate work-in-progress: create `.stop_exempt` (one-shot, logged) — used when a live run is churning tracked cache files (`data/cache/info_cache.json`, `backtest/data/economic_calendar.json`) that should NOT ride in a fix commit.

### 6C. AWS launch gates 1-6 + cube Gate 7 (Doc F Section 1 has the full recipes)
Fire BEFORE any spot spend. `aws_chunk_launch.py` prints Gate 1 + Gate 3 inline.

| Gate | Enforces | This-model status |
|---|---|---|
| 1 | user-data <= 16 KB base64 (CHECKLIST #116) | presigned-URL design keeps it ~6.5 KB |
| 2 | Monitor armed at event boundary, not pre-launch (CHECKLIST #117) | 15-min controller armed same-turn as launch |
| 3 | monitor present in user-data (grep, CHECKLIST #121) | Monitor v2a/v2b baked in |
| 4 | IAM SSM precondition (CHECKLIST #124) | N/A for the presigned-URL pattern (no role); skip stated explicitly |
| 5 | install git hooks on fresh clones (B1256) | N/A — chunk instances are compute+S3-upload only, never `git commit`; skip stated |
| 6 | env-fingerprint parity: `grid_total`/`grid_hash`/`calendar_backend` (CHECKLIST #158) | `env_fingerprint.py --emit` at launch; `--check` HARD-HALT pre-merge |
| 7 | interrupt/resume drill (Gate-7, B1300-B1302) | proven at ~99% fidelity before production chunks |

---

## 7. Merge workflow + PRE-MERGE requirements

### 7.1 Merge
`python scripts/merge_batch_outputs.py <chunk dirs...>` concatenates the ticker-disjoint chunk cubes and rebuilds the engine-schema cube. Fixes shipped this session:
- **fix-a:** merged parquet writes `signals_at_entry`/`context_bullets`/`agent_reasoning` via `dumps_signals` (JSON strings), matching the writer-reader contract.
- **fix-b:** rebuilds the engine-schema cube (`exit_strategy_comparison.csv`, per-strategy x exit) and renames the older per-method summary to `exit_method_summary.csv` (resolves a name collision).
- **fix-c:** cross-batch dedup (removes the SPY benchmark duplicated into every chunk).
- **env-parity:** runs `env_fingerprint.py --check` on all input dirs and **HARD-HALTs on mismatch** (override `--allow-env-mismatch`, logged).

### 7.2 OWNER-MANDATED pre-merge preconditions (memory: `feedback_generalization_mandate_and_premerge_rca`)
**Before ANY chunk merge, REMIND the owner of BOTH — do not merge without surfacing these first:**
1. The cheaper **~$1 20-ticker cloud-vs-local cell-stability cross-check** (S6-B1308) — the owner PREFERS this over a full chunk re-run; run it and report before deciding whether a mixed-platform merge is trustworthy.
2. A **thorough root-cause analysis of the cross-environment measurement differences** (the ~33% local-vs-cloud trade churn: platform float / numpy-BLAS / Python 3.14-vs-3.11 / package versions) — REQUIRED before merging (S6-B1309-PREMERGE-RCA).

If all merged chunks share one platform (all-cloud), the parity check passes trivially and the RCA reminder still stands as documentation of why single-platform was chosen.

---

## 8. Cost, cadence, budget

- **Hard budget cap this session: $50 CAD.** Track sunk cost per launch; escalate before it's threatened.
- **Spot pricing:** c6a.16xlarge ~$0.60-1.05/hr; a ~482-ticker chunk ~ $8-12 full, ~$3-4 for a resume tail.
- **8h cap per instance** (`MAX_RUN_HOURS`) bounds a single spot-interrupt loss to <= that; the controller resumes the tail.
- **Cadence:** owner-set. This session — local hourly, AWS 15-min. Match Monitor timeout to wall-clock; `persistent: true` for long runs.
- **Ladder discipline (L86/L95):** rung 1 -> 2 -> 3 -> 4 with owner gates; never skip to full universe.

---

## 9. Lessons embedded (this session)

| Lesson | Rule it created |
|---|---|
| L207 | calendar silent Mon-Fri fallback when `pandas_market_calendars` absent -> **env-fingerprint parity gate** (#158) |
| L208 | a correctness fix landing mid-multi-run needs a **cross-run** consistency check, not just per-run |
| L209 | **measure materiality before asserting it** (the calendar was mis-blamed for platform-float churn until measured: 6/153 divergent trades) |
| B1300 Catch 1 | checkpoint shipping cannot be interruption-only (manual/hard kill sends no IMDS notice) -> every-5th-beat periodic ckpt |
| B1300 Catch 2 | success markers must be **freshness-checked** -> stale-marker clear + launch-epoch guard |
| B1305/B1308 | cross-chunk grid + platform must match to merge -> Gate 6 + Section 7 cross-check |
| B1312 | completion markers must reflect **actual completion**, not process exit -> status-gated `COMPLETE`/`CAPPED` |
| ENG-1 (B1260) | writer-reader signal contract via `signals_serde.py` -> `signals_at_entry` survives resume |

---

## 10. Cross-references

**Code:**
- `scripts/aws_chunk_launch.py` (AWS spot chunk launcher + Monitor v2 + B1312 marker)
- `backtest/run_phase1a.py` (local engine entry; `--resume-from-checkpoint`)
- `backtest/util/signals_serde.py` (ENG-1 writer-reader contract)
- `scripts/env_fingerprint.py` (`--emit` / `--check`; MERGE_CRITICAL fields)
- `scripts/merge_batch_outputs.py` (fix-a/b/c + env-parity)
- `scripts/preflight.py` (C1-C9 commit gates)
- `scripts/verify_turn_compliance.py` (Stop-hook Gate B)
- `backtest/tests/conftest.py::pytest_sessionfinish` (C6 pyramid stamp writer)

**Docs:**
- `docs/r6_workflow_reuse/R5_WORKFLOW.md` (Doc A — original monolith autoladder + sentinel contract)
- `docs/r6_workflow_reuse/AWS_LAUNCH_PLAYBOOK.md` (Doc F — AWS-mechanics recipes: AZ failover, spot-capacity, S3 externalization, cost)
- `CHECKLIST.md` #116/#117/#121/#124/#158
- `.claude/skills/execution-discipline/SKILL.md` (turn protocol + GENERALIZATION MANDATE)

**Memory rules in force:**
- `feedback_generalization_mandate_and_premerge_rca` (pre-merge $1 cross-check + RCA reminder)
- `feedback_ask_before_relaunching_corrected_version` (no auto-relaunch of a corrected version after halt)
- `feedback_monitor_design_vs_operational_gap`, `feedback_monitor_arm_at_event_not_pre_launch`
- `feedback_aws_user_data_size_preflight`, `feedback_check_existing_pids_before_long_background_launch`
- `feedback_powershell_authoritative_for_windows_process_truth`
- `feedback_no_auto_launch_batch_b`, `project_r5_path_decisions_2026_07_08`
