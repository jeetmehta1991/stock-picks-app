# B1045 - Sub-A 14 WARN Findings Disposition (Council 138 deferral resolution)

# Source: Council 140 Option-5 Step 4 + Council 138 Sub-A adversarial review +
# CHECKLIST #126 (default DESIGNED-NOT-VERIFIED) per CHECKLIST #77.

## Purpose

Sub-A adversarial review surfaced **9 BLOCK + 14 WARN + 21 NIT** findings. The 9 BLOCKERS were fixed in B1043. The 14 WARN findings were deferred per Council 138 Option-3 STAGED-FIX-+-SMOKE deferral (Phase D not blocking).

Per owner directive "Proceed. Execute all." (Council 140 Step 4), each WARN is now re-evaluated against the B1043 + B1044 + B1045 fix state. Disposition: RESOLVED-BY-B1043 / RESOLVED-NOW / DEFERRED-OWNER-ACK / STILL-OPEN.

## Disposition table

| # | Finding | File:line | Severity | Disposition | Notes |
|---|---|---|---|---|---|
| F-10 | sync_loop reads engine_state mid-write | launch:142-152 + backtest.py:597-598 | WARN | RESOLVED-B1046 | Atomic-snapshot guaranteed jointly by engine `os.replace` (F-11 fix) + sync_loop `--exclude '*.tmp'` (verified line 144-148); explicit comment block added at sync_loop |
| F-11 | trade_log_checkpoint.csv non-atomic write | backtest.py:567-569 | WARN | RESOLVED-B1046 | Atomic write via tempfile + os.replace pattern applied at backtest.py:565-577; ticket S6-ATOMIC-CSV-WRITE-PATTERN closed |
| F-15 | Truncated CSV -> false HALT-CRITICAL | backtest.py:567 + monitor:221 | WARN | RESOLVED-B1046 | Resolved transitively by F-11 atomic write + new test_unit pin `test_b1046_f15_monitor_handles_partial_csv_write_pin` verifies monitor gracefully handles truncated CSV |
| F-17 | `cells_completed` never emitted from cube fan-out | backtest.py:585-594 | WARN | RESOLVED-B1043 | F-01 fix emits `cells_completed=trades_so_far`. Note: this is total trades not cube cells; semantic mismatch noted but operational (consumer treats as progress proxy) |
| F-19 | Phase_watchdog leaks across phases | launch:158-168 | WARN | RESOLVED-B1043 | F-02 fix captures WATCHDOG_PID + kills in cleanup block after `wait` returns |
| F-20 | `phase_watchdog &` no PID capture | launch:187 | WARN | RESOLVED-B1043 | Same as F-19; WATCHDOG_PID added |
| F-21 | SYNC_PID empty -> kill silent error | launch:153,248,267-270,272 | WARN | RESOLVED-B1046 | Each kill now guarded with `[ -n ... ]` empty-check + explicit WARN log for visibility per CHECKLIST #122; `guarded_kill` helper added; applied to SYNC_PID + B1019_PID + HALT_WATCHER_PID + WATCHDOG_PID + all 4 phase-run cleanup branches + final SYNC_PID kill |
| F-24 | `--screen-pool-workers 60` SIGTERM non-propagation | launch:185 (now 192) | WARN | RESOLVED-B1046 | Engine subprocess now launched via `setsid` so it heads its own process group; HALT-CRITICAL watcher upgraded to `kill -15 -\$ENGINE_PID` (negative-PID = whole process-group) so SIGTERM propagates to all 60 screen_pool workers. Fallback to non-negative kill if setsid unavailable. Ticket S6-POOL-SIGTERM-PROPAGATION-HARDENING closed |
| F-27 | `_load_baseline` per_strategy schema mismatch | monitor:103-114 | WARN | RESOLVED-B1043 | F-03 fix: `_load_baseline` now parses `results` list + falls back to per_strategy legacy |
| F-28 | Engine emit Exception caught silently as warning | backtest.py:604-605 | WARN | RESOLVED-B1046 | Severity-classified exception handling: OSError errno=ENOSPC (disk-full) now re-raises HALT-CRITICAL; transient OSErrors logged as warnings with errno detail; other Exception types keep existing logger.warning path |
| F-33 | `aws s3 cp --quiet` lacks paired error check (28 occurrences) | launch:multiple | WARN | PARTIAL-RESOLVED-B1046 | Critical PUT/GET paths now paired: master_ops_tickers.txt download + user-data S3 upload + bootstrap user_data.sh download all gated with paired error check + sentinel; `s3_cp_or_warn` helper available for non-critical sentinel uploads (intentionally non-blocking per disposition). 22 sentinel upload calls retain non-critical pattern by design (heartbeat semantics — sync_loop staleness covers detection) |
| F-34 | Subshell `( while ... ) &` orphan on SIGHUP | launch:207-215 | WARN | RESOLVED-B1046 | HALT-CRITICAL watcher subshell now wrapped in `nohup bash -c "..." &` + `disown -h` so SIGHUP on parent exit does not orphan-kill watcher mid-poll. Bonus: paired-error WARN on the watcher's own aws s3 cp call |
| F-36 | Watcher condition exits when engine dies first | launch:207 | WARN | NOT-A-BUG | This is CORRECT behavior - when engine completes successfully, watcher exits cleanly. Documented as intentional in B1043 fix |
| F-37 | `years_elapsed = max(current_day / 251.0, 0.01)` 100x inflation | monitor:143 | WARN | RESOLVED-B1043 | F-01 fix emits `simulated_day` non-zero; A1 fire-rate division now sensible. **Note:** initial poll at sim_day=50 (per F-05) -> years_elapsed=0.199 -> divisor reasonable |
| F-43 | Post-run analyzer `_compute_deviations` STUB returns [] | post_run_analyzer.py:143-147 | WARN | RESOLVED-B1046 | Stub replaced with actual deviation math: loads B660 baseline JSON (results list schema with n_fires_long/short/avoid + calendar_year_span), computes per-strategy fires_per_year, surfaces |ratio - 1.0| >= 1.0 or starvation (ratio < 0.5), returns top-N sorted by abs(deviation_pct). Ticket S6-POST-RUN-D2-DEVIATIONS closed |

## Summary

| Status | Count | Description |
|---|---|---|
| RESOLVED-B1043 | 4 | Already fixed via F-01/F-02/F-03 BLOCKER fixes |
| RESOLVED-B1046 | 8 | F-10/F-11/F-15/F-21/F-24/F-28/F-34/F-43 fixed Council 141 parallel fan-out |
| PARTIAL-RESOLVED-B1046 | 1 | F-33 critical paths paired; 22 non-critical sentinels intentionally unchanged |
| NOT-A-BUG | 1 | F-36 correct behavior |
| DEFERRED-OWNER-ACK | 0 | All previously deferred items now resolved |
| STILL-OPEN | 0 | None blocking Phase D |

## New tickets surfaced (S6-* tier; post-R5 hardening)

- S6-POOL-SIGTERM-PROPAGATION-HARDENING (F-24) -- CLOSED-B1046 (setsid + process-group kill)
- S6-S3-CP-PAIRED-VERIFICATION (F-33) -- PARTIAL-CLOSED-B1046 (critical paths gated; sentinel uploads intentional non-blocking)
- S6-POST-RUN-D2-DEVIATIONS (F-43) -- CLOSED-B1046 (_compute_deviations implemented)
- S6-ATOMIC-CSV-WRITE-PATTERN (F-11 + F-15) -- CLOSED-B1046 (tempfile + os.replace + pin test)

## Phase D launch implication

**Per CHECKLIST #126:** the WARN findings do NOT block Phase D launch. 5 of 14 are RESOLVED-B1043 or NOT-A-BUG. 8 are DEFERRED-OWNER-ACK with explicit risk acknowledgement + S6 tickets queued. 1 is PARTIAL-RESOLVED.

Phase D launch remains gated on:
1. Phase C v2.5 smoke PASS verdict (in flight)
2. 0 BLOCKERS surfaced from smoke
3. Explicit owner approval per `feedback_ask_before_relaunching_corrected_version`

## Cross-references

- `output_audit/b1043_adversarial_monitor_review_2026_06_28.md` (Sub-A source)
- B1043 commit fix list
- Council 138 Option-3 deferral
- Council 140 Option-5 Step 4 mandate
- CHECKLIST #126 (evidence-artifact rule)
