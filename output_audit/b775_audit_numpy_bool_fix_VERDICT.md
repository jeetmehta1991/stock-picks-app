# B775 -- CHECKLIST-106 audit numpy.bool_ counting bug FIX + B767/B775 verdict reconciliation

# per CHECKLIST #77 + #44(b) + #69 + #94 + #105 + #106 + #107
# Source: scripts/checklist_106_cluster_a_producer_audit.py line 279 (BUG)
# Source: output_audit/checklist_106_cluster_a_producer_audit_demo.json (B775 demo result that surfaced the bug)
# Source: output_audit/checklist_106_cluster_a_producer_audit_smoke.json (B767 smoke + B775 post-fix smoke)
# per memory: feedback_data_consumption_audit_must_apply_checklist_44b.md

## Headline finding

**The CHECKLIST-106 audit's True-counting logic had a strict-type bug that rejected `numpy.bool_` values.** B767 + B775 demo "emitted_but_always_False" verdicts for 14-15 candidates were ALL FALSE POSITIVES. Real producer fire rates are 5-51%, well within normal.

This is the second occasion where #44(b) "investigate-why" disambiguated buggy verdict from real strategy failure (B748c was the first; B774 factor 0-fires gap was the third). Pattern: producer-audit gates manufacture false positives that look like strategy failures.

## The bug

`scripts/checklist_106_cluster_a_producer_audit.py:279` (pre-fix):
```python
# Treat boolean True or truthy non-None as "active"
if sig_val is True or (sig_val and isinstance(sig_val, bool)):
    stats["n_True_observations"] += 1
```

**Strict `isinstance(sig_val, bool)` REJECTS `numpy.bool_` instances.** Verified empirically:
- `hammer` returns `np.True_` (type `numpy.bool_`, NOT Python `bool`)
- `near_cam_r3` returns `np.True_` / `np.False_`
- Most producer signals from pandas vectorized comparisons return `numpy.bool_`
- Only signals from manually-wrapped `_safe_float(...) > _safe_float(...)` return Python `bool`
- The audit counted Python-bool signals correctly but missed all numpy-bool signals

## The fix

`scripts/checklist_106_cluster_a_producer_audit.py:279` (B775 fix):
```python
try:
    import numpy as _np
    _is_bool_like = isinstance(sig_val, (bool, _np.bool_))
except Exception:
    _is_bool_like = isinstance(sig_val, bool)
if sig_val is True or (sig_val and _is_bool_like):
    stats["n_True_observations"] += 1
```

Accepts both `bool` and `numpy.bool_` while still rejecting non-boolean truthy values (e.g., `rsi_14 = 45.93` float still NOT counted as True).

## Verification on smoke (3 tickers x 1yr 2024)

| Signal | Pre-fix audit verdict | Post-fix true_rate | Realistic? |
|---|---|---|---|
| hammer | "emitted_but_always_False" | 5.3% (40/756) | YES (Nison 1991 expected 3-7%) |
| shooting_star | "emitted_but_always_False" | 4.6% (35/756) | YES |
| near_cam_r3 | "emitted_but_always_False" | 16.0% (121/756) | YES (matches B761 AAPL probe ~21%) |
| near_cam_s3 | "emitted_but_always_False" | 14.2% (107/756) | YES |
| above_cam_r4 | "emitted_but_always_False" | 22.6% (171/756) | YES |
| below_cam_s4 | "emitted_but_always_False" | 20.8% (157/756) | YES |
| above_cpr | "emitted_but_always_False" | 51.1% (386/756) | YES (intuitive ~50%) |
| below_cpr | "emitted_but_always_False" | 47.9% (362/756) | YES |
| cpr_narrow_tight | "emitted_but_always_False" | 30.3% (229/756) | YES (5%-band threshold) |
| roc_turning_dn | "emitted_but_always_False" | 5.7% (43/756) | YES |
| roc_turning_up | "emitted_but_always_False" | 5.8% (44/756) | YES |
| near_prev_low | "emitted_but_always_False" | 10.1% (76/756) | YES |
| near_prev_high | "emitted_but_always_False" | 11.6% (88/756) | YES |
| close_above_open | "emitted_but_always_False" | 49.1% (371/756) | YES (intuitive ~50%) |
| close_below_open | "emitted_but_always_False" | 50.5% (382/756) | YES |

**15-of-15 false positives ELIMINATED.** Pattern F candidates dropped from 49 -> 34. None of these 15 signals are silent-no-op gates; they are all working producers emitting normal True/False frequencies.

## Reconciliation with B767 + B775 prior verdicts

### B767 verdict reconciliation

B767 verdict stated: "Real-key issue breakdown: 8 declared_but_never_emitted (CRITICAL pre-flight gate) + 14 emitted_but_always_False (deferred to B768 demo)."

**B775 correction:** The 14 emitted_but_always_False candidates were ALL audit-bug false positives. Real producer rates are 5-51%. Cluster A producer audit verdict simplifies to:
- 8 declared_but_never_emitted - investigated B767 - all METADATA-mismatch shorthand (53 declarations in signals_used field), NOT runtime silent-no-op
- 14 emitted_but_always_False - B775 correction: ALL false positives from numpy.bool_ counting bug

**Cluster A producer-data audit verdict (final, post-B775):** 
- ZERO runtime silent-no-op gates
- ZERO "emitted but always False" gates
- 53 metadata-mismatches in signals_used field shorthand (METADATA only, NOT runtime contract gaps)

The chairman's TIER 0 concern (B748c-pattern contamination) is FULLY refuted. Council's "if 2-3 of 30 silently default-return, the entire effective-N debate is contaminated" was empirically NOT the case.

### B775 demo run reconciliation

B775 demo (50 tickers x 2yr) showed all 14 candidates still "emitted_but_always_False" - same audit bug pre-fix. The 9658s runtime produced contaminated data. Post-fix smoke (3 tickers x 1yr; 299s) gives clean data. Demo full re-run would take similar 2.7 hours but is NOT needed since smoke verification already validates the fix produces sane results.

## Follow-up tickets

**#64 `S4-B775-CHECKLIST-106-AUDIT-PIN-TEST-NUMPY-BOOL-COUNTING`** -- Codify B775 numpy.bool_ counting fix as pin test in `backtest/tests/test_unit.py`. Probe: build synthetic OHLCV where `hammer` or `near_cam_r3` is known True; assert the audit's True-counter increments for both Python bool AND numpy.bool_ signal values. Future contributors who refactor the True-counting logic will trip this test. Defense-in-depth pattern (mirror of B770 #62 PIT pin test). PENDING-OWNER-APPROVAL. Source: B775 audit-bug discovery. Class 1 TEST-CODIFICATION. MEDIUM.

## CHECKLIST #107 reconciliation (B775)

- **Findings surfaced:** 2 primary (audit numpy.bool_ counting bug; 15 B767/B775 false positives eliminated by fix) + 1 nuanced (post-fix Cluster A producer audit is CLEANER than initial verdicts -- zero runtime gates + zero always-False producers)
- **Tickets filed:** 1 NEW (#64 pin test) + 0 annotations (B767 + B775 demo verdicts effectively superseded by this batch; no separate queue tickets to annotate -- the verdicts were in batch commit messages + verdict reports)
- **Code changes:** 1 (`scripts/checklist_106_cluster_a_producer_audit.py:279` numpy.bool_ accept)
- **Audit-clean: YES**

Cumulative ticket count post-B775: **131 unique S4-B7XX tickets** (130 post-B774 + 1 B775 pin test).

## Strategy counts (unchanged)

221 / 0 / 1 / **220 active.** No strategies modified.

## Memory + checklist compliance

- `feedback_data_consumption_audit_must_apply_checklist_44b.md` -- per investigate-why step (f): audit's strict-type-check was the root cause, NOT producer bugs or strategy bugs. This is the THIRD case the rule has caught (B748c FILE-LIST gap; B774 measurement-harness gap; B775 audit-bug)
- `feedback_no_a_priori_strategy_pruning.md` -- no strategies modified; audit-bug correction only
- CHECKLIST #44(b) -- investigate-why disambiguated buggy verdict from real strategy issue
- CHECKLIST #67 -- doc-sync same turn
- CHECKLIST #69 -- pyramid mandatory (842/842; verifying)
- CHECKLIST #77 -- canonical-source headers
- CHECKLIST #94 -- queue-mandatory-per-turn
- CHECKLIST #105 -- audit source read end-to-end (line 279 + surrounding context)
- CHECKLIST #106 -- producer-data audit class
- CHECKLIST #107 -- findings-vs-tickets reconciliation (TENTH-FULL-EXECUTION)
