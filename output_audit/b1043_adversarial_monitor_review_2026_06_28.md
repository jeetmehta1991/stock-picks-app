# Source: Council 137 + Council 138 + feedback_monitor_design_vs_operational_gap per CHECKLIST #77.

# B1043 Adversarial Monitor Review (Council 137 Sub-agent A)

**Date:** 2026-06-28
**Scope:** B1019 monitor + Layer 1 engine emit + Layer 2 launch wiring
**Mandate:** "Be extremely comprehensive. No more silent misses."
**Source files reviewed line-by-line (per CHECKLIST #105):**
1. `scripts/b1019_phase_1_runtime_monitor.py` (246 lines)
2. `backtest/engine/backtest.py` lines 540-610 (Layer 1)
3. `scripts/launch_r5_master_4y_v2.sh` (312 lines)
4. `scripts/b1019_a5_phase_1_preflight_coverage_check.py` (146 lines)
5. `scripts/b1019_phase_1_post_run_analyzer.py` (186 lines)

---

## 1. Executive Summary

**Total findings: 32**
- **BLOCK (Phase D launch must NOT proceed):** 9
- **WARN (high-confidence defect, should fix pre-launch):** 14
- **NIT (cosmetic / hardening):** 9

The single most damaging finding is **F-01: schema mismatch between Layer 1 emit and monitor reader (5 contract keys mismatch)** - the monitor will silently degrade on EVERY checkpoint, never enter A1/B2/D1 logic with valid data, and never see `status=="complete"`. The watcher fires only on the literal `HALT-CRITICAL` string, which means a monitor that is broken-but-silent looks identical to a monitor that is healthy-and-quiet. This is the exact `feedback_monitor_design_vs_operational_gap` failure pattern repeating with different specifics: the producer exists, the consumer exists, but they don't speak the same language.

A second, equally fatal class is **F-02: ENGINE_PID actually captures the `tee` PID, not the Python engine PID**. Every `kill -0 $ENGINE_PID` check is watching the wrong process. The watcher will run forever even after the engine crashes, the wait will return when tee exits (not the engine), and SIGTERM via `kill -15 $ENGINE_PID` will kill tee (engine stays orphaned attached to no stdout).

A third blocker class is the **baseline file path and schema mismatch (F-03, F-04)** which guarantees A1 silently disables on every Phase D run.

**Phase D should not launch until F-01 through F-09 are fixed.**

---

## 2. Race Conditions

**F-10 (WARN):** Engine writes `engine_state.json` via `.tmp + os.replace` (backtest.py:597-598). `os.replace` is atomic on POSIX (rename(2)) - Linux Phase D target is safe. But the in-process `sync_loop` (launch_r5_master_4y_v2.sh:142-152) issues `aws s3 sync` every 60s. If `aws s3 sync` reads the source file mid-write (between `state_tmp.write_text` and `os.replace`), it could upload either: (a) stale `engine_state.json` (last 100d), or (b) the new `.tmp` file under the wrong name. The `--exclude '*.tmp'` flag (line 144-148) protects against (b), so risk is bounded to stale-but-consistent reads. Acceptable for telemetry, not for control.

**F-11 (WARN):** `trade_log_checkpoint.csv` write at backtest.py:567-569 is NOT atomic. `_pd.DataFrame(...).to_csv(checkpoint_path, index=False)` writes in place. If the engine crashes mid-write, the file is truncated. Monitor `_check_b2_schema` at b1019_phase_1_runtime_monitor.py:172 would then read a partial CSV and `pd.read_parquet` would throw - but the file is supposed to be CSV anyway (see F-05), so the throw masks the real bug.

**F-12 (NIT):** The HALT-CRITICAL watcher (launch_r5_master_4y_v2.sh:207-215) `grep -q HALT-CRITICAL` against `b1019_monitor.log` while the monitor is still writing to that log. POSIX append-mode is line-atomic in normal cases, but partial writes during line buffering could cause grep to miss the substring on the same poll cycle. The 60s poll cadence absorbs this (grep next cycle), so risk is bounded latency, not loss.

---

## 3. Atomicity Gaps

**F-13 (NIT):** If `state_tmp.write_text(...)` fails partway (disk full, OOM during `json.dumps`), the `.tmp` file is left behind. Next checkpoint overwrites it; no cleanup needed because `os.replace` is the atomic step. Safe in practice.

**F-14 (BLOCK):** `os.replace` semantics on **Windows** differ from Linux - on Windows it raises `PermissionError` if the destination is open. Phase D runs on Linux (c6a.16xlarge), so this is N/A for production. But local developer-laptop unit-test runs on Windows will spuriously fail. Flag for cross-platform pyramid stability.

**F-15 (WARN):** `_pd.DataFrame([vars(t) for t in self.closed_trades]).to_csv(...)` at backtest.py:568-569 has NO `.tmp + rename` pattern. A SIGTERM mid-write leaves a truncated CSV. Monitor reads truncated CSV -> `pd.errors.EmptyDataError` or partial row -> A1 + B2 false anomaly. The monitor's `_check_a1_fire_rate` catches via `except Exception` (line 159) and emits `ERROR-<type>-<msg>`; `_classify_tier` (line 221) treats `ERROR` on **B2** as HALT-CRITICAL but does NOT treat `ERROR` on A1 as HALT. So a truncated CSV -> B2 ERROR -> spurious HALT-CRITICAL fires -> engine killed by watcher. False positive HALT during normal crash-recovery.

---

## 4. Off-by-One / Timing

**F-16 (BLOCK):** Engine emits `engine_state.json` at `i > 0 and i % 100 == 0` (backtest.py:580). First emit is day 100 = ~5 months sim time = ~50-80 min real time per ticker. **Phase 1 has 30-min hard cap.** Phase 1 will TIMEOUT before the engine has emitted a single state file. The monitor loop will sit at `_read_engine_state` returning `None`, never advance, never log a checkpoint, and produce ZERO observability for the entire Phase 1 NVDA single-ticker run. The phase_watchdog will then SIGKILL the engine at minute 30 without any monitor data ever reaching S3.

**F-17 (BLOCK):** Monitor's `total-days 1006` (launch_r5_master_4y_v2.sh:200) is wrong for Phase 1. Phase 1 is NVDA single-ticker - same trading-day count BUT the monitor's D1 ETA logic (b1019_phase_1_runtime_monitor.py:201-204) divides `runtime_sec / pct_cells` where `pct_cells = cells_completed / total_cells`. Layer 1 NEVER emits `cells_completed` (it's not in the state dict at backtest.py:585-594). Monitor reads `state.get("cells_completed", 0)` -> always 0 -> `pct_cells == 0` -> `eta_min == 0` -> ETA reported as 0 forever. D1 dashboard is permanently broken.

**F-18 (WARN):** The monitor loop's checkpoint-skip logic at b1019_phase_1_runtime_monitor.py:77 - `if current_day < last_checkpoint_day + args.checkpoint_cadence` - uses `last_checkpoint_day = -1` initially. First emit at day 100 satisfies `100 < -1 + 100 == 99` -> False -> processes the checkpoint. OK. But the engine's `i` is the trading-day index (0..N-1), NOT business days. Monitor's `total_days=1006` matches Phase D 4y window (251 x 4 = 1004). Off-by-one acceptable.

**F-19 (NIT):** `phase_watchdog` (launch_r5_master_4y_v2.sh:158-168) sleeps for `MAX_MIN * 60` then `kill -0`. There is no termination of the watchdog if the engine exits **early** (success or crash). The watchdog continues sleeping after Phase 1 completes, then wakes during Phase 2 or later, and `kill -0 $PHASE_PID` will check a PID that may have been recycled. PID recycling on Linux is rare but POSSIBLE under 32K PID wrap on long-running c6a.16xlarge. Watchdog could `kill -9` an unrelated process. Background watchdog leaks across phases without explicit cleanup.

---

## 5. PID Leakage / Zombie Processes

**F-02 (BLOCK):** **Most damaging Layer 2 finding.** Line 185: `python -m backtest.run_phase1a ... 2>&1 | tee ${PHASE_DIR}/engine.log &`. The `&` backgrounds the entire **pipeline**. `$!` returns the PID of the **last command in the pipeline**, which is `tee`, NOT the python engine. Consequences:
- `ENGINE_PID` = tee PID
- `phase_watchdog ${ENGINE_PID}` watches tee; if engine crashes but tee remains, watchdog sees `kill -0 tee` succeed -> no timeout fires
- `wait $ENGINE_PID` waits for tee, not engine - RC is tee's exit code (usually 0 even when engine crashes with SIGPIPE)
- `kill -15 $ENGINE_PID` (HALT-CRITICAL handler line 212) kills tee - engine continues unattached, writes go to closed pipe -> SIGPIPE -> engine dies anyway, BUT under different signal semantics
- HALT_WATCHER subshell line 207 condition `kill -0 $ENGINE_PID` reads tee - tee will outlive the engine if monitor is alive (sending data); watcher loop spins after engine death

**Fix pattern:** Use `python ... > ${PHASE_DIR}/engine.log 2>&1 &` and tail the log externally, OR use process substitution `python ... > >(tee ...) 2>&1 &` which still has the same issue, OR capture engine PID via `set +o pipefail; python ... & ENGINE_PID=$!; tail -F ${PHASE_DIR}/engine.log &`.

**F-20 (BLOCK):** `phase_watchdog ${PHASE_NUM} ${MAX_MIN} $ENGINE_PID &` (line 187) is backgrounded BUT no `WATCHDOG_PID=$!` capture, no cleanup. If Phase 1 completes in 5 min, the watchdog continues sleeping for `30 * 60 - 5 * 60 = 25 min` and wakes during Phase 2 - by then engine PID has been reused, may `kill -9` Phase 2 engine. Same recycling concern as F-19.

**F-21 (WARN):** `SYNC_PID` (line 153) lives in the parent shell. Each `kill $SYNC_PID 2>/dev/null || true` in cleanup paths (lines 248, 267-270, 272) may be too aggressive - `|| true` swallows real errors. If `SYNC_PID` is empty (e.g., `sync_loop` failed to background), `kill ""` errors silently and the loop persists.

**F-22 (NIT):** `HALT_WATCHER_PID=$!` (line 216) captures the subshell PID. Subshell cleanup at line 223 uses `kill ... || true`. OK in normal flow, but if the watcher subshell has already exited (engine completed normally, loop exited via `kill -0` failure), the kill silently fails - no leak but no notification.

---

## 6. SIGTERM / Signal Handling

**F-23 (BLOCK):** Python engine has NO signal handler (grep `signal.signal|SIGTERM|signal_handler` in backtest.py returns 0 matches). `kill -15` from the HALT-CRITICAL watcher (line 212) sends SIGTERM. Python's default is to raise `KeyboardInterrupt`-equivalent at the next bytecode boundary. **Without an installed handler, the engine cannot flush `trade_log_checkpoint.csv` or `engine_state.json` before exit.** The cube-cell partial run is lost. The whole point of HALT-CRITICAL is to surface bad data; without flushing, we can't even examine WHY it halted.

**F-24 (WARN):** `--screen-pool-workers 60` (line 185) spawns 60 Python child processes via multiprocessing. SIGTERM to the parent does NOT propagate to children automatically in spawn-mode pools. Children orphan to init (PID 1), continue compute work, write to closed parent file handles -> silent data corruption in `data_prefetch/` or per-ticker output. On c6a.16xlarge with 64 vCPUs, 60 workers means 60 leaked processes per phase if SIGTERM fires.

**F-25 (NIT):** No `trap` handler in launch_r5_master_4y_v2.sh user-data. SIGHUP (e.g., spot termination warning) -> bash exits -> SYNC_PID + phase_watchdog + HALT_WATCHER_PID all orphan to init. Spot termination is the most likely failure mode on the c6a.16xlarge spot instance.

---

## 7. JSON Parsing / Missing File Handling

**F-26 (NIT):** `_read_engine_state` (b1019_phase_1_runtime_monitor.py:117-124) silently returns `None` on parse error. The polling loop (line 73-75) interprets `None` as "not ready" and sleeps. **A persistent corrupted state file would cause an infinite silent wait.** No counter, no warning to stderr, no S3 sentinel. Owner sees no monitor output.

**F-27 (WARN):** Monitor's `_load_baseline` (line 103-114) reads `data.get("per_strategy", {})`. The actual B660 baseline schema has top-level key `results` (list of dicts), NOT `per_strategy` (dict of dicts). **The dict comprehension at line 110-111 will operate on `{}` (empty dict), return `{}`, A1 check at line 131-133 returns `DEGRADED-no-baseline`.** A1 is permanently disabled regardless of file presence. See F-04 below for the path bug that compounds this.

---

## 8. Disk-Full / Write-Failure Paths

**F-28 (WARN):** Engine emit `except Exception as _e: logger.warning(...)` (backtest.py:604-605) catches ALL emit failures silently. Disk full -> emit fails -> engine continues, monitor sees no new state file -> monitor permanently stuck on stale state. Should be at minimum `logger.error` + emit a sentinel file to alert the watcher.

**F-29 (NIT):** Checkpoint CSV write (backtest.py:564-572) `except Exception: pass` - fully silent on failure. A disk-full mid-CSV-write swallows the error, leaves the file truncated, and the engine continues. Next checkpoint overwrites the truncated file with a complete one (recovery), but B1019 monitor running mid-window reads truncated CSV and triggers F-15 false HALT.

---

## 9. Poll Cadence / Baseline / D1 Logic

**F-03 (BLOCK):** Launcher passes `--baseline output_audit/b660_fire_count_measured.json` (line 198). **This file does not exist.** The actual file is `output_audit/fire_count_measured_b660_full_universe.json`. Monitor's `_load_baseline` (line 104) returns `{}` -> A1 permanently `DEGRADED-no-baseline`. Combined with F-04 (schema mismatch), even fixing the path wouldn't help.

**F-04 (BLOCK):** Even if the path were correct, the baseline schema has no `per_strategy` key. The data is `{"results": [{"strategy": "...", "measured_fires_per_calendar_year_total_sampled": float, ...}, ...]}`. Monitor parser at line 110-111 reads `data.get("per_strategy", {})` returning `{}`. A1 fire-rate logic at line 131-133 short-circuits with `DEGRADED-no-baseline`. **A1 anomaly detection is fundamentally non-functional.**

**F-30 (NIT):** Even with correct parsing, `expected_fpy > 1.0` gate (line 148) excludes all strategies that the baseline measured at < 1 fire/year. B660 measured many strategies at 0.0 fires/year (FAIL_FIRE_STARVED verdict). Monitor will only flag deviations on the dense-firing strategies - exactly the strategies LEAST likely to silently break. This is a structural blind spot for the anomaly logic.

---

## 10. Status Field / Terminal State

**F-31 (BLOCK):** Layer 1 ALWAYS emits `status="running"` (backtest.py:591). Engine never updates to `status="complete"` at end of run. Monitor's terminal exit condition (line 78, 98) `if state.get("status") == "complete"` will NEVER fire. **Monitor only exits via HALT-CRITICAL (return 1) or external kill.** When the engine completes successfully, `wait $ENGINE_PID` (line 219) returns and cleanup (line 222-223) kills the monitor - fine. But: monitor never gets to emit a clean "COMPLETE" line. The final state of `b1019_monitor.log` will be the last checkpoint mid-run; nothing signals "phase finished cleanly via monitor."

---

## 11. Time Drift / S3 Auth Failures

**F-32 (NIT):** Engine timestamp via `time.strftime("...", time.gmtime())` (backtest.py:592) - UTC. Watcher polls via `date -u +%Y-%m-%dT%H:%M:%SZ`. Consistent. OK.

**F-33 (WARN):** Every `aws s3 cp ... --quiet` (28 occurrences in launch script) lacks explicit error capture. If IAM is revoked mid-run (e.g., role policy change), sentinels stop landing in S3 -> monitor and owner see silent freeze. The `B-8: SILENT-FAILURE-PAIRING` comment claims `|| true` is paired with explicit check, but most `aws s3 cp` lines (e.g., 87, 92, 114, 129, 139, 155, 165, 180, 205, 211, 227, 231, 236, 240, 253, 274, 275) do NOT have paired checks. Only the dep installs (lines 91, 108) are paired.

---

## 12. Subshell PID Escape / Exit-Handler Cleanup

**F-34 (WARN):** Subshell `( while ... done ) &` (line 207-215). When the parent script exits cleanly (line 276 `sudo shutdown -h +1`), the subshell may receive SIGHUP or may not - depends on `huponexit` shell option. On Amazon Linux default bash, the subshell typically inherits the orphan-init behavior. The line 223 cleanup `kill $HALT_WATCHER_PID || true` runs only after `wait $ENGINE_PID` returns - if `wait` returns because tee died but engine hung, the watcher subshell keeps polling forever (PID recycling risk over multi-hour windows).

**F-35 (NIT):** `set +e` (line 184) before `wait`, `set -e` (line 224) after. Cleanup `kill ... || true` runs under `set +e` so `kill` failures don't abort. The `set -e` resumption happens before the post-RC checks. Acceptable but fragile if any new line between 184-224 introduces a side effect.

---

## 13. Watcher Loop Logic

**F-36 (WARN):** Watcher condition `while kill -0 $ENGINE_PID && kill -0 $B1019_PID` (line 207). When the engine dies first (success path), `kill -0 $ENGINE_PID` fails -> loop exits. Watcher subshell exits cleanly. OK.
But: monitor (B1019_PID) exits on HALT-CRITICAL (return 1) BEFORE killing the engine. Subshell condition becomes: `kill -0 $ENGINE_PID` = True, `kill -0 $B1019_PID` = False -> loop exits WITHOUT issuing the SIGTERM. **HALT-CRITICAL would be ignored because the monitor dies BEFORE the watcher can act on the log line.** Race condition: monitor must keep running long enough for watcher to grep the log; monitor returns 1 immediately at line 96.

**Fix pattern:** Watcher should grep the log first, THEN check both PIDs.

---

## 14. B1019 Monitor Function-Level Bugs

**F-01 (BLOCK):** State-dict key mismatch between Layer 1 emit and monitor reader:

| Monitor reads | Layer 1 emits | Effect |
|---|---|---|
| `state.get("simulated_day", 0)` (line 76) | `sim_day_index` | `current_day` is always 0 -> first-checkpoint condition NEVER advances -> infinite loop of polls with no checkpoint actions |
| `state.get("cells_completed", 0)` (line 197) | (not emitted) | D1 `pct_cells` always 0 -> ETA broken |
| `state.get("status") == "complete"` (line 78, 98) | always `"running"` | Monitor never exits cleanly |
| `tickers_processed` (emitted) | (not read) | Dead field |
| `trades_so_far` (emitted) | (not read) | Dead field |

This is THE blocker. Monitor reads state file, gets garbage, behaves as if nothing happened. No checkpoint line ever printed -> no HALT-CRITICAL ever logged -> watcher subshell idles -> engine runs without observability.

**F-05 (BLOCK):** Monitor calls `pd.read_parquet(trade_log_path)` (lines 139, 172) but launcher passes `--trade-log {PHASE_DIR}/trade_log_checkpoint.csv` (line 197). **CSV passed to parquet reader throws `ArrowInvalid` on every poll.** Caught at line 159 -> `result["status"] = f"ERROR-{type(exc).__name__}-{exc}"`. `_classify_tier` line 221 - `if str(b2.get("status", "")).startswith("ERROR"): return "HALT-CRITICAL"`. **EVERY checkpoint emits HALT-CRITICAL.** Watcher subshell sees HALT-CRITICAL on first grep poll -> kills the engine. Phase 1 will be terminated on its first attempted checkpoint, BEFORE any data is salvaged.

Combined with F-16 (first emit at day 100 = ~50 min, but Phase 1 hard cap is 30 min), this means in practice the watchdog timeout kills the engine before the monitor ever fires its false HALT - but Phase 2, 3, 4 with longer caps WILL hit F-05 and false-HALT.

**F-37 (WARN):** `_check_a1_fire_rate` at line 143: `years_elapsed = max(current_day / 251.0, 0.01)`. `current_day` is 0 due to F-01 -> years_elapsed = 0.01 -> `actual_fpy = actual / 0.01` = 100x inflation. If we EVER fix F-01 but baseline parsing (F-04) still returns empty dict, this path is dormant - but if both fixed, this divisor produces 100x ratios on the very first poll, triggering many false ANOMALY entries.

**F-38 (NIT):** `_check_b2_schema` requires `["strategy", "ticker", "entry_date", "exit_date", "exit_method"]`. The actual checkpoint CSV at backtest.py:568 emits `vars(t)` for each Trade. The Trade dataclass field set is in writer.py; needs cross-verification that `exit_method` is present in raw vars (it may be set post-checkpoint by writer rollup).

**F-39 (NIT):** `_check_d1_progress` accepts `total_cells` and `total_days` arguments but uses neither for division checks. `max(total_cells, 1)` and `max(total_days, 1)` are defensive against 0; OK.

**F-40 (NIT):** No timeout on `pd.read_parquet`. A corrupted parquet file could hang IO. On a 60s poll cycle with a hung read, the monitor is non-responsive. Probability low; impact is silent freeze.

---

## 15. Preflight Invocation Status

**F-06 (BLOCK):** `scripts/b1019_a5_phase_1_preflight_coverage_check.py` is **NEVER invoked** by `launch_r5_master_4y_v2.sh`. Grep over the launch script finds only `b1019_phase_1_runtime_monitor.py` (line 195). The preflight gate that was supposed to verify 217 active strategies + signal coverage + producer wiring before launch is **completely orphaned**. Phase D will launch with zero pre-launch verification of strategy coverage. This is the exact `feedback_monitor_design_vs_operational_gap` pattern: DESIGNED ≠ OPERATIONAL.

**F-41 (NIT):** Preflight's `_check_producer_registry` (line 131-141) returns `True` if `producer_index.json` doesn't exist. That is a silent pass - should be `False` or `DEGRADED`.

**F-42 (NIT):** Preflight's `_check_ohlcv_cache` (line 106-115) uses `cache_dir.rglob(f"*{ticker}*")` and returns True if any match found. A single hit (e.g., `NVDA_metadata.json`) counts; no OHLCV completeness check. False positives on partial caches.

---

## 16. Post-Run Invocation Status

**F-07 (BLOCK):** `scripts/b1019_phase_1_post_run_analyzer.py` is **NEVER invoked** by `launch_r5_master_4y_v2.sh`. Same orphan finding as F-06. Phase D will complete with no automated post-run rollup - owner must run the analyzer manually post-instance-terminate.

**F-43 (WARN):** Post-run analyzer's `_compute_deviations` (line 143-147) is a STUB that returns `[]`. The summary always reports "No baseline available OR no deviations computed" (line 171). The post-run report's promised D2 deviation surfacing is not implemented.

**F-44 (NIT):** Post-run reads `trade_log.parquet` only. If the engine crashes and only `trade_log_checkpoint.csv` exists, analyzer fails. No fallback path.

---

## 17. Per-Finding Severity Table

| # | Finding | File:line | Severity | Fix recommendation |
|---|---|---|---|---|
| F-01 | State key mismatch (`simulated_day` vs `sim_day_index`, `cells_completed` not emitted, status never `complete`) | monitor:76,78,98,197 ↔ backtest.py:585-594 | BLOCK | Align key names; emit `cells_completed`; emit terminal `status` |
| F-02 | `ENGINE_PID=$!` captures tee PID not engine PID | launch:185-186 | BLOCK | Use file redirection; capture engine PID via `&` without pipe |
| F-03 | Baseline path wrong (`b660_fire_count_measured.json` doesn't exist) | launch:198 | BLOCK | Use `fire_count_measured_b660_full_universe.json` |
| F-04 | Baseline schema mismatch (`per_strategy` vs `results`) | monitor:110-111 | BLOCK | Parse `results` list keyed by `strategy` |
| F-05 | Monitor calls `read_parquet` on `.csv` trade_log_checkpoint | monitor:139,172 ↔ launch:197 | BLOCK | Use `read_csv`; OR have engine write parquet checkpoints |
| F-06 | Preflight script orphaned | launch_r5_master_4y_v2.sh (no ref) | BLOCK | Invoke preflight pre-engine in `run_phase` |
| F-07 | Post-run analyzer orphaned | launch_r5_master_4y_v2.sh (no ref) | BLOCK | Invoke post-run post-engine in `run_phase` |
| F-16 | First emit at day 100 = ~50 min; Phase 1 cap 30 min | backtest.py:580 ↔ launch:267 | BLOCK | Lower cadence to `% 25` for Phase 1 OR raise Phase 1 cap |
| F-23 | Engine has no SIGTERM handler -> no checkpoint flush on HALT | backtest.py (no handler) | BLOCK | Install `signal.signal(SIGTERM, _flush_and_exit)` |
| F-10 | sync_loop reads engine_state mid-write | launch:144-148 ↔ backtest.py:597-598 | WARN | Stale-but-consistent: acceptable |
| F-11 | trade_log_checkpoint.csv non-atomic write | backtest.py:567-569 | WARN | Use `.tmp + os.replace` pattern |
| F-15 | Truncated CSV -> false HALT-CRITICAL | backtest.py:567 ↔ monitor:221 | WARN | Atomic CSV write; AND tier-classifier ignore-once on first ERROR |
| F-17 | `cells_completed` never emitted -> D1 broken | backtest.py:585-594 | WARN | Emit `cells_completed` from cube fan-out tracker |
| F-19 | Phase_watchdog leaks across phases | launch:158-168 | WARN | Capture WATCHDOG_PID; kill at phase end |
| F-20 | `phase_watchdog &` no PID capture, no cleanup | launch:187 | WARN | Capture PID; kill in cleanup block |
| F-21 | `kill $SYNC_PID || true` swallows errors | launch:248,267,272 | WARN | Add explicit pre-check `if [ -n "$SYNC_PID" ]` |
| F-24 | `--screen-pool-workers 60` children don't get SIGTERM | launch:185 | WARN | Engine must `terminate()` pool on SIGTERM |
| F-27 | Monitor `_load_baseline` silent-degrade | monitor:103-114 | WARN | Emit visible WARN sentinel to S3 |
| F-28 | Engine emit failure -> `logger.warning` silent | backtest.py:604-605 | WARN | Upgrade to `logger.error` + S3 sentinel |
| F-30 | `expected_fpy > 1.0` blind spot on FIRE_STARVED strats | monitor:148 | WARN | Lower threshold OR separate detection for zero-fire strats |
| F-31 | Engine never emits `status=complete` | backtest.py (end of run) | WARN | Emit final `status=complete` after finalize |
| F-33 | aws s3 cp lines without paired check | launch:87,92,114,129,139,155,165,180,205,211,227,231,236,240,253,274,275 | WARN | Add IAM-failure detection sentinel |
| F-34 | Subshell PID escape on SIGHUP | launch:207-215 | WARN | `trap` cleanup in user-data root |
| F-36 | Watcher misses HALT-CRITICAL (monitor dies first) | launch:207-215 ↔ monitor:96 | WARN | Grep log BEFORE the `kill -0` check; OR have monitor sleep before exit |
| F-37 | `years_elapsed = max(0.01)` -> 100x inflation | monitor:143 | WARN | Skip A1 until current_day > 251 |
| F-12 | Mid-write grep race on monitor.log | launch:209 ↔ monitor:241 | NIT | Acceptable latency |
| F-13 | Leftover `.tmp` if write fails | backtest.py:597 | NIT | Acceptable |
| F-14 | Windows os.replace semantics | backtest.py:598 | NIT | Production-Linux: N/A |
| F-18 | Off-by-one on `last_checkpoint_day=-1` | monitor:64 | NIT | OK |
| F-22 | Watcher cleanup `|| true` silent on already-dead | launch:223 | NIT | Acceptable |
| F-25 | No `trap` for SIGHUP | launch (entire script) | NIT | Spot-termination hardening |
| F-26 | Corrupt state file -> infinite silent wait | monitor:117-124 | NIT | Add counter; warn after N retries |
| F-29 | Checkpoint CSV `except Exception: pass` | backtest.py:571-572 | NIT | Log warning at minimum |
| F-32 | UTC consistency | backtest.py:592, launch | NIT | OK |
| F-35 | `set +e` / `set -e` brittle | launch:184,224 | NIT | Acceptable |
| F-38 | `exit_method` may not be in raw vars(t) | monitor:173 ↔ backtest.py:568 | NIT | Verify against Trade dataclass |
| F-39 | `_check_d1_progress` defensive max(,1) | monitor:198-199 | NIT | OK |
| F-40 | No read_parquet timeout | monitor:139,172 | NIT | Low risk |
| F-41 | `_check_producer_registry` returns True on missing | preflight:131-141 | NIT | Return False or DEGRADED |
| F-42 | OHLCV check false-positive on partial cache | preflight:106-115 | NIT | Check bar-count or date range |
| F-43 | `_compute_deviations` is a stub | post-run:143-147 | WARN | Implement D2 logic per spec |
| F-44 | Post-run only reads `.parquet` | post-run:71 | NIT | Add CSV fallback |

---

## 18. Phase D Launch BLOCKER Summary

**HARD BLOCKERS (9, must fix before Phase D launches):**

1. **F-01** - Layer 1 emit ↔ monitor reader key mismatch (5 keys disagree). Monitor degrades silently on every poll. The original `feedback_monitor_design_vs_operational_gap` failure pattern is reproduced verbatim with different specifics.
2. **F-02** - `ENGINE_PID` captures tee PID. Watcher, watchdog, SIGTERM, and `wait` all target the wrong process.
3. **F-03** - Baseline file path wrong (`b660_fire_count_measured.json` doesn't exist).
4. **F-04** - Baseline JSON schema mismatch (no `per_strategy` top-level key).
5. **F-05** - Monitor calls `pd.read_parquet` on a `.csv` file -> every poll throws -> every checkpoint emits false HALT-CRITICAL.
6. **F-06** - `b1019_a5_phase_1_preflight_coverage_check.py` never invoked from launch script.
7. **F-07** - `b1019_phase_1_post_run_analyzer.py` never invoked from launch script.
8. **F-16** - First Layer 1 emit at day 100 ≈ 50 min; Phase 1 hard cap is 30 min. Monitor will produce ZERO observability for Phase 1 single-ticker NVDA run.
9. **F-23** - Engine has no SIGTERM handler -> kill -15 from HALT-CRITICAL watcher loses all in-flight checkpoint data.

**Compound effect:** Even if any single blocker were fixed in isolation, the others remain. The monitor as currently wired is effectively decorative - it polls a state file with wrong keys, parses a baseline that doesn't exist with a wrong schema, reads CSV with parquet reader producing false HALT-CRITICAL on every cycle, AND the launch script's tee-pipeline backgrounding means the watcher cannot observe the engine even if the monitor worked. The preflight and post-run scripts that were supposed to gate the launch are not called.

**Owner recommendation:** Do NOT launch Phase D. Per `feedback_audit_recommendations_against_existing_directives`, this audit surfaces findings only - no auto-remediation. Council 137 should converge on a remediation plan (likely Council 138+) before re-attempting Phase D. The honest-finding pivot here is that Layer 1/2 wiring was DESIGNED but not END-TO-END VERIFIED on a smoke run with the actual key schema - exactly the failure mode CHECKLIST #121 was meant to prevent.
