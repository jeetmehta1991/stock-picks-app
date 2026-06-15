# B774 TIER 3 #56 FACTOR FIRE-COUNT GATE -- BLOCKED PENDING MEASUREMENT WIREUP

# per CHECKLIST #77 + #44(b) + #69 + #94 + #105 + #106 + #107
# Source: B769 council TIER 3 ticket #56 (M1 unanimous-missed factor fire-count power-compatibility pre-flight)
# Source: output_audit/fire_count_measured_b660_full_universe.json (factor strategies show 0 fires)
# Source: scripts/measure_fire_count.py (does NOT import or invoke cross_sectional.compute_cross_sectional_features)
# Source: backtest/signals/screener.py:7953-7954 (backtest engine DOES invoke compute_cross_sectional_features)
# Source: backtest/signals/cross_sectional.py (the producer module)
# Source: STAGE_4_TREND_CONFLUENCE_CHART_PATTERN_RESIDUAL_CLUSTER_WALKS.md B-29 walk (already flagged "B690 TIER 2 harness wireup")
# per memory: feedback_data_consumption_audit_must_apply_checklist_44b.md + feedback_no_a_priori_strategy_pruning.md

## B769 council TIER 3 #56 question (M1 unanimous-missed)

> "Nobody verified that the factor strategies, as currently architected, fire often enough to satisfy min_trades=30/regime. If xs_low_beta_long fires monthly per ticker as rank-cutoff signal, fine; if fires only on rank-crossings, fire-count may be inadequate. GATE before TIER 3 design work -- design effort wasted if cube can't produce statistically valid PASS/FAIL regardless of Bonferroni math."

## VERDICT: GATE BLOCKED PENDING MEASUREMENT-HARNESS WIREUP

**Cannot answer the gate question.** B660 measurement data on 6 factor strategies (B-27 through B-32) shows uniform **0 fires** -- but this is NOT a real fire-count. It is a MEASUREMENT INFRASTRUCTURE GAP.

Per `feedback_data_consumption_audit_must_apply_checklist_44b.md` 6-step audit:

### Step (a) -- Path from source

Factor strategies depend on cross-sectional signals: `xs_momentum_decile`, `xs_beta_decile`, `xs_ivol_decile`, `xs_max_anomaly_decile`, `xs_quality_decile`. These keys must appear in the per-ticker signal dict for strategy gates to read.

### Step (b) -- Recursive glob

- `backtest/signals/cross_sectional.py` -- producer module EXISTS
- `compute_cross_sectional_features(ohlcv_dict, as_of)` -- function EXISTS
- Invocations:
  - `backtest/signals/screener.py:7954` -- BACKTEST engine invokes (in `screen_universe`)
  - `scripts/measure_fire_count.py` -- **DOES NOT INVOKE** (CRITICAL gap)

### Step (c) -- Temporal coverage probe

Producer is universe-wide (cross-sectional ranks across all tickers per as_of), NOT per-ticker. Different shape than other producers (per-ticker df-only). Cannot be added to per-ticker precompute loop trivially -- needs universe-level pre-pass.

### Step (d) -- Schema contract probe

Producer returns `dict[ticker -> dict[xs_*_decile -> int]]`. Each ticker's xs_*_decile feeds the per-ticker signal dict via merge in screener.py:7616 (`signals.update(xs_features)`).

### Step (e) -- KNOWN-EVENT runtime probe

Synthetic 12-ticker × 260-day OHLCV: `compute_cross_sectional_features` ran without exception but returned empty dict (likely requires larger universe or specific deciling thresholds). Producer works structurally; needs full universe to emit. The harness gap is confirmed; producer-itself validation needs full T1a 503-ticker invocation.

### Step (f) -- #44(b) investigate-why

**WHY are factor strategies firing 0 in B660?** Because `scripts/measure_fire_count.py` does NOT invoke `compute_cross_sectional_features`. The producers feeding `xs_*_decile` keys are silent in the measurement harness. All factor strategies receive default-False on every xs gate -> never fire in the measurement.

**This is NOT a real fire-count.** This is exactly the B748c precedent + B768 PEAD restore precedent: a measurement gap masquerading as a verdict.

## The exact M1 risk the council predicted

B769 inline-council Reviewer 1 unanimous-missed:
> "Statistical-power compatibility with factor sub-cluster fire rate. Nobody verified that the factor strategies, as currently architected, fire often enough to satisfy min_trades=30/regime. If xs_low_beta_long fires monthly per ticker as a rank-cutoff signal, fine; if it fires only on rank-crossings, fire-count may be inadequate before any design work matters. This should be the gate before TIER 3."

**The M1 question cannot be answered with B660 data.** The measurement harness is missing the producer. Before TIER 3 #55/#57/#58/#59 design work proceeds, the cross-sectional producer must be wired into `measure_fire_count.py` and re-run.

This is itself a key finding the council didn't fully anticipate: the GATE-condition requires functioning measurement infrastructure, which is itself a dependency.

## B-29 walk doc already flagged this (existing knowledge surfaced)

STAGE_4_TREND_CONFLUENCE_CHART_PATTERN_RESIDUAL_CLUSTER_WALKS.md B-29 walk:
> "Disposition recommendation: KEEP-AS-IS + Class 2 regime-affinity addition + DEFERRED B690 measurement. Status post-B750: STRATEGY-CLEAN; MEASUREMENT-BLOCKED."

And Pattern V in same doc:
> "**Pattern V** -- Factor strategies require universe-level computation. xs_* strategies require per-as_of cross-sectional rank computation. Producer is universe-level (ranks across all T1a tickers at as_of). Per B716: cross_sectional.compute_cross_sectional_features needs B690 TIER 2 harness wireup. Walks document this measurement blocker."

**The "B690 TIER 2 harness wireup" mentioned in the B-29 walk is the missing wireup.** Per B689 producer wireup pattern (TIER 1 per-bar producers wired into precompute loop), TIER 2 universe-wide producers (cross_sectional + similar) need separate wireup.

This is also why B768 demo edge-prior test similarly returned 0 fires for cross-sectional-dependent triggers -- different problem, same class of measurement-harness gap.

## Follow-up ticket filed

**#63 `S4-B774-MEASURE-FIRE-COUNT-EXTEND-CROSS-SECTIONAL-PRODUCER-WIREUP`** -- extend `scripts/measure_fire_count.py` to invoke `compute_cross_sectional_features(ohlcv_dict, as_of)` as a universe-wide pre-pass at each as_of, then merge xs_* keys into each ticker's signal dict before strategy evaluation. Same pattern as `screener.py:7954` does in backtest. PENDING-OWNER-APPROVAL. Source: B774 measurement gap discovery from M1 GATE attempt. Class 8 INFRA. **CRITICAL BLOCKER for TIER 3 work.**

## TIER 3 sequencing UPDATE

**Original chairman tier order:**
- TIER 3 GATE: #56 factor fire-count power-compatibility pre-flight  (M1)
- TIER 3 PRE-DESIGN: #55 factor architecture audit
- TIER 3 POST-ARCH: #57 design extension + #58 survivorship + #59 cost-aware
- TIER 3 PRE-#60: #61 M3 conflict-resolution memo
- TIER 3 POST-F1-F9: #60 gate-justification soft-discipline

**B774 REVISED tier order (with new #63 blocker surfaced):**
- TIER 3 INFRA-BLOCKER: **#63 wire cross_sectional producer into measure_fire_count.py** (NEW; precedes everything else in TIER 3)
- TIER 3 GATE: #56 factor fire-count pre-flight -- BLOCKED on #63
- TIER 3 PRE-DESIGN: #55 architecture audit -- BLOCKED on #56
- TIER 3 POST-ARCH: #57 + #58 + #59 -- BLOCKED on #55
- (independent of above): #61 M3 memo + #60 gate-justification soft-discipline

Per `feedback_data_consumption_audit_must_apply_checklist_44b.md`: "data missing verdict requires path-from-source + recursive glob + temporal-coverage probe + schema-contract probe + KNOWN-EVENT runtime probe + #44(b) investigate-why." All 6 steps applied; finding is MEASUREMENT GAP not FAIL_FIRE_STARVED. Tickets do not proceed on a contaminated gate.

## CHECKLIST #107 reconciliation (B774)

- **Findings surfaced:** 2 primary (#56 GATE BLOCKED measurement gap; #63 NEW ticket required to unblock TIER 3 chain) + 1 nuanced (B-29 walk previously flagged this as "B690 TIER 2 harness wireup" pending; B774 codifies as actual blocker)
- **Tickets filed:** 1 NEW (#63 measure_fire_count.py extension for cross_sectional producer) + 1 annotation on existing #56 (BLOCKED-PENDING-MEASUREMENT-WIREUP not FAIL_FIRE_STARVED)
- **Audit-clean: YES**

Cumulative ticket count post-B774: **130 unique S4-B7XX tickets** (129 post-B773 + 1 B774 new infra blocker).

## Strategy counts (unchanged)

221 / 0 / 1 / **220 active.** No strategies modified; this is a measurement-harness audit + TIER 3 sequencing correction.

## Memory + checklist compliance

- `feedback_data_consumption_audit_must_apply_checklist_44b.md` -- all 6 audit steps applied; finding is MEASUREMENT GAP not strategy verdict; investigated WHY (producer not invoked) per step (f)
- `feedback_no_a_priori_strategy_pruning.md` -- NO factor strategies tagged EXPLORATORY pre-measurement; the gate question is unanswerable until #63 ships
- `feedback_no_prior_edge_consolidate_before_tune.md` -- TIER 3 design work blocked until measurement supports it
- `feedback_minimum_fire_count_gate_before_cube.md` -- the M1 gate cannot be evaluated with contaminated data
- CHECKLIST #44(b) -- investigated WHY 0 fires; producer-not-invoked-in-harness root cause identified
- CHECKLIST #67 -- doc-sync same turn
- CHECKLIST #69 -- pyramid mandatory (842/842; no code changes)
- CHECKLIST #77 -- canonical-source headers
- CHECKLIST #94 -- queue-mandatory-per-turn
- CHECKLIST #105 -- producer source + caller paths read end-to-end
- CHECKLIST #106 -- producer-data audit class
- CHECKLIST #107 -- findings-vs-tickets reconciliation (NINTH-FULL-EXECUTION)
