# B1052 Phase D Silent Engine - Root Cause Analysis

# Source: Council 146 Option-3 PRIORITY-PHASED debug deliverable +
# CHECKLIST #126 evidence-artifact rule per CHECKLIST #77.

## Summary

**HONEST-FINDING PIVOT #30 (B1052): `--no-agents` flag MISSING from launch script.**

Phase D Phase 1 (`i-00fe60c77558f5548`) ran for 1h 37m on NVDA x 4y window, reached sim_day=20 of 1003 (2% complete), and was manually terminated by owner. Watchdog would have fired at 01:56:48 UTC; owner authorized abort earlier (cost saved: ~$0.30 spot vs ~$1.80 if let to MAX_MIN=120 cap).

## Root cause

The engine invocation in `scripts/launch_r5_master_4y_v2.sh:215` (B1043+B1046 era) reads:

```bash
setsid python -m backtest.run_phase1a --phase 1a-beta \
    --tickers "${TICKERS}" --start ${START_DATE} --end ${END_DATE} \
    --no-news --no-git --no-walk-forward \
    --output-dir ${PHASE_DIR} --screen-pool-workers 60 \
    > ${PHASE_DIR}/engine.log 2>&1 &
```

**Missing flag: `--no-agents`.**

Per `backtest/run_phase1a.py:main` auto-enables for Phase 1A-beta:
- `--no-portfolio-cap` (Batch 377)
- `--no-dd-halt` (Batch 383)
- `--no-regime-affinity` (Batch 384)
- `--no-event-suppression` (Batch 384)
- `--max-cands=200` (Batch 386)

But NOT `--no-agents`. The launch script must pass it explicitly.

## Failure mechanism

1. Engine enters Phase 1A-beta cube evaluation loop
2. Per sim_day, runs agent pipeline for each candidate ticker
3. `ANTHROPIC_API_KEY` is NOT SET on AWS instance (this is correct - agents are NOT needed for Phase 1A-beta cube)
4. Agent pipeline retries Claude API call 5 times x ~1.5s each = ~7.5s overhead per agent call
5. With ~10 candidate tickers/day x 7.5s = 75s/day agent overhead (over base ~6s/day base engine work)
6. Total per-day cost: ~21s
7. Phase 1 NVDA x 1003 days = 21,063s = **5.85 HOURS** vs MAX_MIN=120min cap

## Evidence (engine.log final state)

```
2026-06-28 00:04:30,667 [INFO] Running agent pipeline: SPY [2022-06-02]
2026-06-28 00:04:30,671 [ERROR] ANTHROPIC_API_KEY not set
2026-06-28 00:04:32,171 [WARNING] Agent agent: empty/None response
2026-06-28 00:04:33,672 [WARNING] Agent agent: empty/None response
2026-06-28 00:04:35,173 [WARNING] Agent agent: empty/None response
2026-06-28 00:04:36,673 [WARNING] Agent agent: empty/None response
2026-06-28 00:04:38,174 [WARNING] Agent agent: empty/None response
2026-06-28 00:04:39,677 [INFO] Progress: 20/1003 [2022-06-03] elapsed_hours=0.12
2026-06-28 00:06:06,190 [INFO] Running agent pipeline: NVDA [2022-06-09]
```

Pattern: every sim_day -> 5 retry warnings + 1 progress log + repeat.

## Why CHECKLIST #127 didn't catch this

Phase C v1 / v2 / v2.5b smoke ran NVDA x 22 days:
- 22 days x ~21s/day = ~7.7 min agent overhead
- Plus ~2.5 min base engine = 10 min total smoke
- Within 15-min cap -> PASS

Phase D Phase 1 ran NVDA x 1003 days:
- 1003 days x ~21s/day = 5.85 hr
- Plus ~17 min base engine = ~6 hr total
- Exceeds 120-min cap by 3x -> would have hit watchdog

**The bug is SCALE-DEPENDENT** - smoke validated at small N where the overhead was bounded. Beyond ~344 days, the agent retry overhead exceeds the smoke cap.

## CHECKLIST #127 honest limitation (B1052 finding)

CHECKLIST #127 (AWS-smoke-mandatory-gate) catches:
- [OK] Schema mismatches (F-01)
- [OK] PID semantics bugs (F-02)
- [OK] Path bugs (F-03, F-04)
- [OK] Library install bugs (B1039 SMC)
- [OK] Holdout bugs (B1045 #27)
- [OK] Variable scope bugs (B1049 #29)

CHECKLIST #127 does NOT reliably catch:
- [X] **Scale-dependent bugs** (this finding #30)

Per `feedback_audit_recommendations_against_existing_directives`: honestly acknowledge the limitation. Smoke is necessary BUT NOT SUFFICIENT for scale-dependent bugs.

## Mitigation (B1052 fix shipped)

### Code fix
`scripts/launch_r5_master_4y_v2.sh:215` - added `--no-agents` flag to engine invocation. Phase 1A-beta cube evaluation doesn't need agents (agents are for Phase 1B+ when agent overlay is the experiment).

### Pyramid test
`backtest/tests/test_b1052_launch_script_no_agents_flag.py` - asserts the launch script invokes engine with `--no-agents` for Phase 1A-beta.

### CHECKLIST update
CHECKLIST #128 (proposed): "Scale-dependent bugs require an interim batch BEFORE Phase D - run 1 phase at intermediate scale (e.g., 100 sim-days) to extrapolate per-day cost". To be added in follow-up batch with owner approval.

## Cost incurred

| Phase | Time | Spot cost |
|---|---|---|
| Bootstrap + data sync | 16 min | $0.30 |
| Phase 1 partial (sim_day 0-20) | 1h 37m | ~$1.50 |
| **Total this launch** | **~2h** | **~$1.80** |

Without owner-mandated manual abort, would have run full 120 min then hit `PHASE_1_TIMEOUT_HALT`. Owner-mandated abort saved ~$0.30 + 23 min wall-clock.

## Session cumulative

- Honest-finding pivots: **29 -> 30** (this finding)
- Session AWS spend: ~$5.75 (smokes + B1048 partial + B1049 retry + B1052 abort)
- Phase D status: **NOT LAUNCHED** (3 attempts: B1048 preflight HALT, B1049 retry started but not yet validated for scale, B1052 root cause caught at scale)

## What's needed before next Phase D launch

1. **Verify `--no-agents` fix locally** - run engine with smoke window + verify NO agent pipeline lines in engine.log
2. **Pyramid test passes** - `test_b1052_launch_script_no_agents_flag.py` green
3. **Phase C v2.5c smoke ON AWS** - validate `--no-agents` end-to-end (~$0.49; 10 min)
4. **Per-day timing extrapolation** - engine.log Progress lines should show ~6s/day (no agent overhead) -> 1003 days x 6s = 100 min Phase 1 expected
5. **Owner explicit go** per `feedback_ask_before_relaunching_corrected_version`

## Cross-references

- B1042 (Layer 1+2 monitor wrap) - operational for this run; B1019 monitor was wrapping correctly
- B1043 (9 BLOCKERS + Sub-C MAX_MIN) - MAX_MIN=120 would have hit; B1043 F-06 SIGTERM handler would have flushed checkpoint
- B1045 (HoldoutUnlock) - verified working; engine ran past holdout window
- B1047 (retrospective audit) - 16-claim verification confirmed structural fixes work
- B1049 (PHASE_DIR fix) - verified working; preflight passed cleanly
- B1051 (CLASS B-F audit) - 7 bugs found; C-3 fixed; C-1 NOT-FIRING per S3 check
- run_phase1a.py `--no-agents` flag - pre-existing; just needed to be wired into launch script
- CHECKLIST #127 (AWS-smoke-mandatory-gate) - honest limitation surfaced this batch
