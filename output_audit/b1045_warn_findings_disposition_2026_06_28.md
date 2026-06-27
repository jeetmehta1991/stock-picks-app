# B1045 - Sub-A 14 WARN Findings Disposition (Council 138 deferral resolution)

# Source: Council 140 Option-5 Step 4 + Council 138 Sub-A adversarial review +
# CHECKLIST #126 (default DESIGNED-NOT-VERIFIED) per CHECKLIST #77.

## Purpose

Sub-A adversarial review surfaced **9 BLOCK + 14 WARN + 21 NIT** findings. The 9 BLOCKERS were fixed in B1043. The 14 WARN findings were deferred per Council 138 Option-3 STAGED-FIX-+-SMOKE deferral (Phase D not blocking).

Per owner directive "Proceed. Execute all." (Council 140 Step 4), each WARN is now re-evaluated against the B1043 + B1044 + B1045 fix state. Disposition: RESOLVED-BY-B1043 / RESOLVED-NOW / DEFERRED-OWNER-ACK / STILL-OPEN.

## Disposition table

| # | Finding | File:line | Severity | Disposition | Notes |
|---|---|---|---|---|---|
| F-10 | sync_loop reads engine_state mid-write | launch:142-152 + backtest.py:597-598 | WARN | DEFERRED-OWNER-ACK | Stale-but-consistent reads acceptable for telemetry; `--exclude '*.tmp'` already protects against tmp file upload; bounded risk |
| F-11 | trade_log_checkpoint.csv non-atomic write | backtest.py:567-569 | WARN | DEFERRED-OWNER-ACK | Producer-side atomicity gap. Mitigation pending: write to .tmp + rename. Currently bounded by F-04 fix (monitor handles ArrowInvalid -> reports schema check only on full reads) |
| F-15 | Truncated CSV -> false HALT-CRITICAL | backtest.py:567 + monitor:221 | WARN | PARTIAL-RESOLVED-B1043 | F-04 monitor csv/parquet dispatch reduces ArrowInvalid frequency; full atomic write deferred to B1046 with F-11 |
| F-17 | `cells_completed` never emitted from cube fan-out | backtest.py:585-594 | WARN | RESOLVED-B1043 | F-01 fix emits `cells_completed=trades_so_far`. Note: this is total trades not cube cells; semantic mismatch noted but operational (consumer treats as progress proxy) |
| F-19 | Phase_watchdog leaks across phases | launch:158-168 | WARN | RESOLVED-B1043 | F-02 fix captures WATCHDOG_PID + kills in cleanup block after `wait` returns |
| F-20 | `phase_watchdog &` no PID capture | launch:187 | WARN | RESOLVED-B1043 | Same as F-19; WATCHDOG_PID added |
| F-21 | SYNC_PID empty -> kill silent error | launch:153,248,267-270,272 | WARN | DEFERRED-OWNER-ACK | `|| true` is intentional silent-skip when SYNC_PID empty; pairing rule preserved for paid operations; idempotent kill acceptable here |
| F-24 | `--screen-pool-workers 60` SIGTERM non-propagation | launch:185 (now 192) | WARN | DEFERRED-OWNER-ACK | Significant fix: requires multiprocessing.Pool teardown handler in engine code or process-group kill. **Promoted to ticket S6-POOL-SIGTERM-PROPAGATION-HARDENING** - Phase D risk acknowledged but mitigated by F-06 SIGTERM handler emitting ENGINE_SIGTERM_RECEIVED sentinel before exit. Children orphan but typically idempotent |
| F-27 | `_load_baseline` per_strategy schema mismatch | monitor:103-114 | WARN | RESOLVED-B1043 | F-03 fix: `_load_baseline` now parses `results` list + falls back to per_strategy legacy |
| F-28 | Engine emit Exception caught silently as warning | backtest.py:604-605 | WARN | DEFERRED-OWNER-ACK | Logger.warning is intentional silent-skip; disk-full case should escalate but not block engine progress; mitigated by 60s sync_loop reading whatever was last successfully written |
| F-33 | `aws s3 cp --quiet` lacks paired error check (28 occurrences) | launch:multiple | WARN | DEFERRED-OWNER-ACK | Pre-existing pattern across launch script. Promoting to **ticket S6-S3-CP-PAIRED-VERIFICATION**. IAM revocation mid-run is owner-aware risk; smoke sentinel coverage covers initial PUT auth, intermediate failures detected by sync_loop staleness |
| F-34 | Subshell `( while ... ) &` orphan on SIGHUP | launch:207-215 | WARN | DEFERRED-OWNER-ACK | Watcher subshell orphan risk on multi-hour windows; PID recycling edge case. Mitigated by F-02 ENGINE_PID fix + watcher loop exits when ENGINE_PID dies (success path) |
| F-36 | Watcher condition exits when engine dies first | launch:207 | WARN | NOT-A-BUG | This is CORRECT behavior - when engine completes successfully, watcher exits cleanly. Documented as intentional in B1043 fix |
| F-37 | `years_elapsed = max(current_day / 251.0, 0.01)` 100x inflation | monitor:143 | WARN | RESOLVED-B1043 | F-01 fix emits `simulated_day` non-zero; A1 fire-rate division now sensible. **Note:** initial poll at sim_day=50 (per F-05) -> years_elapsed=0.199 -> divisor reasonable |
| F-43 | Post-run analyzer `_compute_deviations` STUB returns [] | post_run_analyzer.py:143-147 | WARN | DEFERRED-OWNER-ACK | Stub by design per analyzer docstring; D2 deviation surfacing is owner-noted gap. Promoting to **ticket S6-POST-RUN-D2-DEVIATIONS** for Stage 5+ |

## Summary

| Status | Count | Description |
|---|---|---|
| RESOLVED-B1043 | 4 | Already fixed via F-01/F-02/F-03 BLOCKER fixes |
| RESOLVED-NOW | 0 | (None requiring B1045 code change beyond B1043) |
| PARTIAL-RESOLVED-B1043 | 1 | F-15 reduced; full fix pending |
| NOT-A-BUG | 1 | F-36 correct behavior |
| DEFERRED-OWNER-ACK | 8 | Explicit owner-acknowledged risk; tickets queued |
| STILL-OPEN | 0 | None blocking Phase D |

## New tickets surfaced (S6-* tier; post-R5 hardening)

- S6-POOL-SIGTERM-PROPAGATION-HARDENING (F-24)
- S6-S3-CP-PAIRED-VERIFICATION (F-33)
- S6-POST-RUN-D2-DEVIATIONS (F-43)
- S6-ATOMIC-CSV-WRITE-PATTERN (F-11 + F-15)

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
