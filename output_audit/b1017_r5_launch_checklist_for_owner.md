# B1017 R5 Launch Checklist for Owner

# Source: Council 106 Option-5 BUILD-OWNER-FACING-R5-LAUNCH-CHECKLIST-DOC
# per owner directive 2026-06-26 "Proceed council this. Proceed council
# this." per CHECKLIST #77.

## Gate status (at top of doc per Council 106 verdict)

**R5 LAUNCH STATUS: 🔴 BLOCKED TILL EXPLICIT OWNER APPROVAL.**

Per 3x reinforcement of "R5 stays blocked till my explicit approval"
during session B979-B1010. Council 103 precedent: blanket "Approve all"
did NOT lift R5 gate. Likewise, blanket "Proceed" does NOT lift R5
gate. Only explicit "Launch R5" or "Unblock R5" directive from owner
lifts gate.

**3 outstanding owner-only action items.** Claude has shipped all
autonomous pre-R5 work (B979-B1016; 38 batches; 27 councils; 14
honest-finding pivots). The 3 remaining R5-launch-gate blockers
require owner actions Claude cannot perform.

## Action item 1 — A2 cube re-measurement of earnings_blackout cells

### Status
🔴 OWNER-PRE-APPROVAL-GATED per CHECKLIST #13 expensive-job protocol.

### Why
B1009 shipped INV-057 + INV-058 fixes to `backtest/engine/exit_strategies.py`
(passes `as_of=entry_date` to `fetch_earnings_dates`) and `backtest/data/
fetcher.py` (uses `end_date + 30 days` proxy for earnings announce date).

These fixes affect any R4 cube cells that consumed the `earnings_blackout`
exit method (1 of 26 exit methods × 217 active strategies = potentially
217 × 1 = 217 cells affected, though most strategies won't use this exit
in their best-config).

### Owner action required
1. Approve cube re-measurement scope + budget per CHECKLIST #13 expensive-
   job protocol (L86/L95 precedent: $150 discarded-work).
2. Specify scope: full 217-strategy × earnings_blackout exit re-run, OR
   subset (e.g., strategies where earnings_blackout was best-config in
   prior R4).
3. Specify execution: laptop background (3+ days based on prior R4
   timing) or compute provider (faster but $).

### Suggested owner-facing decision template
```
[ ] APPROVE A2 cube re-measurement
    Scope: full / earnings_blackout-best-only / declined
    Execution: laptop / compute-provider / other
    Budget cap: $___ (CHECKLIST #29 expensive-job)
    ETA expected: ___
```

## Action item 2 — A4 OOS seal hash countersign

### Status
✅ Template prepared B1011 at `output_audit/oos_seal_hash_template.json`.
🔴 Owner countersign required per PATH §13.7 gates #8 + #12.

### Why
DEC #4 OOS Seal Protocol mandates 2026-Q2+ slice integrity hash + ≥24h
posting before Stream-D first batch. Owner countersigns to confirm
slice has NOT been touched in code/data/strategy changes since seal
date.

### Owner action required (3 commands)

**Command 1 — compute OOS slice hash:**
```powershell
cd c:\Users\jeetm\Github\stock-picks-app
python -c "import hashlib, json; from pathlib import Path; q2_files = sorted(Path('data_prefetch/polygon/ohlcv_daily').rglob('*.parquet')); print(hashlib.sha256(''.join(str(f.stat().st_mtime) for f in q2_files).encode()).hexdigest())"
```

**Command 2 — populate + rename template:**
1. Copy `output_audit/oos_seal_hash_template.json` to `output_audit/oos_seal_hash.json` (drop `_template` suffix).
2. Edit `output_audit/oos_seal_hash.json`:
   - Replace `<TBD-OWNER-COMPUTE>` with hash from Command 1.
   - Replace `<TBD-OWNER-DATE>` with today's date (ISO 8601).
   - Replace `<TBD-OWNER-INITIALS>` with typed initials.
   - Replace `<TBD-OWNER-TIMESTAMP>` with countersign timestamp (ISO 8601).
   - Replace `<TBD-OWNER-ETA>` with Stream-D first-batch ETA (must be ≥24h after countersign timestamp).

**Command 3 — commit + push (≥24h pre-Stream-D):**
```bash
git add output_audit/oos_seal_hash.json
git commit -m "B1017 A4: OOS seal hash countersigned for R5 launch (PATH §13.7 gates #8 + #12)"
git push origin main
```

### Verification post-action
- File `output_audit/oos_seal_hash.json` exists with no `<TBD-OWNER-*>` placeholders.
- Commit timestamp + Stream-D-first-batch ETA differ by ≥24h.

## Action item 3 — A5 planted-bug canary injection

### Status
✅ Framework prepared B1011 at `scripts/a5_planted_bug_canary_framework.py`.
🔴 Owner injection + verification required per PATH §13.7 gate #15.

### Why
Council 39 5-advisor synthesis: walk methodology must catch a planted
bug Claude-blind. If walk doesn't catch it, walk methodology is theater.
Gate #15 enforces this empirical verification of methodology soundness.

### Owner action required (4 steps)

**Step 1 — choose bug catalog item:**
```bash
python scripts/a5_planted_bug_canary_framework.py --list-bugs
```

Owner picks one of 5 bug types (silent-lookahead / signal-orphan /
fire-count-drift / inverse-unsafe / regime-affinity-drift). Claude is
blind to which type owner chose.

**Step 2 — inject bug:**
```bash
python scripts/a5_planted_bug_canary_framework.py --inject \
    --bug-type <CHOSEN_TYPE> \
    --target <CHOSEN_FILE_OR_STRATEGY>
```

Owner applies the suggested diff template (or owner-crafted equivalent)
to the target file. Pyramid (test_unit + test_integration) should
still pass after injection.

**Step 3 — run Stage 4 walk on bugged strategy:**
Walk methodology (per `scripts/run_stage_4_walk.py` or equivalent)
should surface the bug in walk-output disposition.

**Step 4 — record verdict + revert:**
- Record verdict in `output_audit/a5_planted_bug_canary_log.json`:
  ```json
  {
    "date": "2026-06-DD",
    "bug_type": "X",
    "target": "...",
    "walk_caught_bug": true,
    "owner_initials": "..."
  }
  ```
- Revert bug via `git diff` + `git checkout -- <bugged-file>`.
- Verify pyramid still GREEN post-revert.

### Verification post-action
- `output_audit/a5_planted_bug_canary_log.json` exists with verdict.
- If `walk_caught_bug == true` → gate #15 PASS; methodology is sound.
- If `walk_caught_bug == false` → gate #15 FAIL; walk methodology
  needs methodology repair before R5 launch (BLOCKING).

## R5 launch protocol (post-all-3-actions)

### Pre-launch gate verification (final)

After A2 + A4 + A5 are complete:

| Gate | Verification command |
|---|---|
| #1 | `python -c "from pathlib import Path; print(len(list(Path('output_audit/dossiers').glob('*'))))"` (expect 220) |
| #2-#7 | `python scripts/populate_all_dossiers.py` (verify all 220/220 0 errors) |
| #8 + #12 | Verify `output_audit/oos_seal_hash.json` exists + commit timestamp ≥24h pre-Stream-D ETA |
| #9 | `python -m pytest backtest/tests/ -q --tb=no` (focused: 859+2 OR full 5067+) |
| #10 | `git log --oneline -5` (verify EXECUTION_QUEUE drained per B1012 disposition) |
| #11 | `python scripts/stream_v_verify_reproducibility.py` (Stream V verifier) |
| #13 | (PSR gate landed via B983; verify metrics.py imports without error) |
| #14 | (seed_registry refreshed B1012 post-B1010) |
| #15 | `cat output_audit/a5_planted_bug_canary_log.json` (verify `walk_caught_bug == true`) |

### R5 launch directive (owner-facing)

When ALL 3 action items complete + ALL 15 gates verified:

**Owner posts explicit directive in chat:**
```
Launch R5. All 15 PATH §13.7 gates verified per B1017 checklist.
A2 cube re-measurement complete; A4 OOS seal countersigned; A5
planted-bug canary verdict: PASS.
```

Claude then proceeds with R5 cube execution per established protocol.

## Session handoff state (B979-B1016 summary)

| Metric | Value |
|---|---|
| Batches B979-B1016 | 38 |
| Councils 79-105 + 106 | 28 |
| Honest-finding pivots | 14 |
| Strategies registered | 220 |
| Strategies active | 217 |
| EXPLORATORY tagged | 12 |
| DISABLED | 3 |
| 5 parallel pyramid runs | All cross-verified |
| EXECUTION_QUEUE drain | COMPLETE |
| Category C+D dispositioned | 30/30 |
| Last commit | `2fcf57fdd` (B1016) pushed origin/main |

## Critical-rules preservation

- R5 launch BLOCKED TILL EXPLICIT OWNER (3rd reinforcement preserved)
- A2 cube re-measurement requires CHECKLIST #13 explicit approval
- A4 OOS seal countersign cannot be auto-applied (owner-only)
- A5 planted-bug injection cannot be Claude-side (Claude-blind discipline)
- L86/L95 $150 discarded-work precedent enforced (CHECKLIST #13)
- DO-NOT-DELETE preserved
- `feedback_audit_recommendations_against_existing_directives` preserved

## Memory rule references

- `feedback_no_prior_edge_consolidate_before_tune` (B705)
- `feedback_audit_recommendations_against_existing_directives`
- `feedback_council_enumerate_plus_recommend`
- `feedback_no_greek_alphabets`
- `feedback_pyramid_full_13_tiers_mandatory`
- B725 + Council 92/98/102/103 precedent
- DEC #4 OOS Seal Protocol
- PATH §13.7 R5 launch gates
- Council 106 Option-5 verdict

## Owner sign-off block (when ready)

```
[ ] A2 cube re-measurement: APPROVED / DECLINED / DEFERRED
    Scope: ___ Budget cap: $___ ETA: ___

[ ] A4 OOS seal countersigned (commit ___ at ___)

[ ] A5 planted-bug canary PASS (verdict logged ___)

[ ] R5 LAUNCH DIRECTIVE: "Launch R5..."

Owner initials: ___ Date: ___
```
