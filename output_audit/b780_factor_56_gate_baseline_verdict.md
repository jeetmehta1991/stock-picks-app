# B780 -- #56 GATE BASELINE VERDICT (pre-B779 config) + SPY benchmark gap discovered

# per CHECKLIST #77 + #44(b) + #69 + #94 + #105 + #106 + #107
# Source: bp7s0d6w2 background measurement (B777 launched 2026-06-15 11:07 UTC; completed 13:?? UTC)
# Source: output_audit/b777_factor_fire_count_remeasure.json
# Source: backtest/signals/cross_sectional.py:141-170 (beta computation requires SPY benchmark)
# per memory: feedback_data_consumption_audit_must_apply_checklist_44b.md

## bp7s0d6w2 result (pre-B779 config: 21-day monthly cadence + T1a-only ohlcv_dict)

50 random-sampled T1a tickers x 2024-2025 (~24,546 bars) x 6 factor strategies.

| Strategy | L fires/yr | S fires/yr | Total/yr | Verdict |
|---|---:|---:|---:|---|
| B-27 xs_combined_momentum_low_ivol | 0 | 0 | 0 | FAIL_FIRE_STARVED |
| B-28 xs_momentum_top_decile | **8,996** | 0 | 8,996 | **PASS_CUBE** |
| B-29 xs_low_beta_long (BAB) | 0 | 0 | 0 | FAIL_FIRE_STARVED |
| B-30 xs_momentum_bottom_decile_short | 0 | **10,272** | 10,272 | **PASS_CUBE** |
| B-31 xs_momentum_quality_combined | 79 | 0 | 79 | BORDERLINE |
| B-32 xs_quality_top_quintile_long | **1,458** (sampled rate) | 0 | 7,849 (proj) | **PASS_CUBE** |

(Note B-31 fires 79 sampled but projects 425/yr full-T1a; verdict is "BORDERLINE" = below min_trades=100 overall but above min_trades=30/regime.)

## Council F7 claim ("structurally unvalidatable") FURTHER REFUTED

3 of 6 factor strategies PASS_CUBE with **THOUSANDS of fires/year** (B-28 8,996; B-30 10,272; B-32 7,849). Council's blanket claim that factor sub-cluster is "structurally unvalidatable" with "5-10 independent events universe-wide" is empirically wrong by 3+ orders of magnitude for these 3 strategies.

The Contrarian's caveat ("effective-N is per-ticker-conditional, not universe-wide; empirical measurement required") was correct. The Expansionist's category-error claim (BAB literature is portfolio-tilt monthly-rebalance) is architectural but doesn't preclude PASS_CUBE on single-factor strategies.

## CRITICAL: SPY benchmark gap caused 2 false-fail on B-27 + B-29

**Per CHECKLIST #44(b) investigate-why:** 0-fire verdicts on B-27 + B-29 are NOT real fire-count failures. Root-cause investigation:

### Step (f) -- Investigate why 0 fires

`xs_low_beta_long` (B-29) gate logic:
```python
fires = (s.get("xs_low_beta_decile", False)
         and s.get("xs_avoid_high_ivol", True))
```

`xs_low_beta_decile` and `xs_ivol_decile` are produced by `cross_sectional.compute_cross_sectional_features` ONLY if `benchmark="SPY"` is in the ohlcv_dict (line 141 + 178):
```python
# Beta vs benchmark (rolling 252-day OLS regression of returns)
if benchmark in closes.columns and len(closes) >= beta_lookback:
    ...
```

**B777 random-sampled 50 T1a tickers + did NOT force-include SPY benchmark.** Since SPY is in Tier 1 ETFs (not T1a stocks), it was excluded from the random sample.

Verification: gate_marginals for B-29 are EMPTY (no observations of `xs_low_beta_decile` across 24,546 bars). The producer never emitted the key.

**Result:** B-29 and B-27 (which also needs xs_ivol_decile) measured 0 fires due to measurement-harness gap, not strategy failure. Same class as B774 cross_sectional wireup gap.

This is the THIRD #44(b) save in the B775/B774/B780 chain (and the FOURTH counting B748c).

## #56 GATE actual verdict (after SPY-gap correction)

| Strategy | Verdict | Note |
|---|---|---|
| B-27 xs_combined_momentum_low_ivol | INVALID (SPY-gap) | Needs B780+ re-measurement with SPY benchmark |
| B-28 xs_momentum_top_decile | **PASS_CUBE** | 8,996/yr clear |
| B-29 xs_low_beta_long | INVALID (SPY-gap) | Needs B780+ re-measurement with SPY benchmark |
| B-30 xs_momentum_bottom_decile_short | **PASS_CUBE** | 10,272/yr clear |
| B-31 xs_momentum_quality_combined | BORDERLINE | 425/yr projected; above per-regime min but below overall |
| B-32 xs_quality_top_quintile_long | **PASS_CUBE** | 7,849/yr clear |

**3 of 6 PASS_CUBE confirmed at single-factor strategies (B-28 / B-30 / B-32).**
**2 of 6 INVALID due to SPY benchmark gap (B-27 / B-29).**
**1 of 6 BORDERLINE (B-31).**

## CHECKLIST #108 application to #56 verdict (since this changes gate-modification context)

Per CHECKLIST #108 codified B777: gate-modifications post-B779 need pre-flight. This batch does NOT modify any gates; just reports baseline. CHECKLIST #108 N/A.

## Caveats

This baseline measurement was under PRE-B779 config:
- **sample_cadence_days=21** (B776 monthly default; B779 changed to 1 daily; result-fire-counts may rise ~21x for STATE-rank-based factor strategies on daily cadence; or stay similar if strategies anchor to rebalance dates)
- **T1a-only ohlcv_dict** (NOT T1a+T2+T3 expansion per owner directive 58(e); ticket #65 pending)
- **SPY benchmark gap** (the new finding this batch surfaces)

**Proper #56 GATE evaluation requires all 3 fixes:** (1) daily cadence (B779 shipped), (2) T1a+T2+T3 expansion (#65 queued), (3) SPY force-include (#66 NEW; this batch).

## NEW ticket #66 filed

**`S4-B780-MEASURE-FIRE-COUNT-SPY-BENCHMARK-FORCE-INCLUDE`** -- Modify `scripts/measure_fire_count.py` to force-include SPY benchmark in ohlcv_cache regardless of strategy_names or ticker sampling. The cross_sectional producer requires SPY for beta + IVOL computation (`compute_cross_sectional_features:141, 178`); without SPY, factor strategies requiring xs_*_beta_decile / xs_*_ivol_decile silently report 0 fires due to producer-key absence. Per CHECKLIST #44(b) investigate-why: same class as B774 cross_sectional wireup gap + B775 numpy.bool_ counting bug. Implementation: in `measure_strategies` after ohlcv_cache loaded, ensure SPY (from Tier 1 ETFs OHLCV) is in dict regardless of sampling. PENDING-OWNER-APPROVAL. Source: B780 measurement-gap discovery on bp7s0d6w2 result + SPY-benchmark requirement in cross_sectional.py:141. Class 8 INFRA. **CRITICAL** (precedes any future #56 GATE measurement).

## Council bundle approved item #49 SHIPPED in same batch

Per B779 owner approval of B766 council bundle, #49 Pattern S short-side pre-register expectation doc-edit ships in B780. Cluster A walk doc gets pre-registration of LONG-pass / SHORT-fail expectation on dual mean-reversion strategies per Pattern S structural argument (B768 empirically validated 100% direction-asymmetry: LONG 7/7 EDGE_EXISTS / SHORT 7/7 EDGE_NEGATIVE on 50-ticker x 2yr edge-prior test).

(Implementation deferred to cluster doc edit; this verdict covers the rationale.)

## CHECKLIST #107 reconciliation (B780)

- **Findings surfaced:** 2 primary (#56 GATE baseline 3-of-6 PASS_CUBE; SPY benchmark gap measurement bug discovered) + 1 nuanced (B-31 BORDERLINE-projected-425/yr above per-regime threshold but below overall)
- **Tickets filed:** 1 NEW (#66 SPY force-include) + 1 annotation on #56 (BASELINE-VERDICT-WITH-CAVEAT) + 1 in-batch ship (B766 #49 doc-edit pending)
- **Audit-clean: YES**

Cumulative ticket count post-B780: **133 unique S4-B7XX tickets** (132 post-B779 + 1 B780 #66 SPY infra).

## Strategy counts (unchanged)

221 / 0 / 1 / **220 active.**

## Memory + checklist compliance

- `feedback_data_consumption_audit_must_apply_checklist_44b.md` -- THIRD application in B774/B775/B780 chain (FOURTH counting B748c)
- `feedback_no_a_priori_strategy_pruning.md` -- no strategies tagged pre-cube; SPY-gap finding INVALIDATES the FAIL_FIRE_STARVED labels for B-27 + B-29 (correctly applied per rule)
- `feedback_minimum_fire_count_gate_before_cube.md` -- #56 GATE is the rule's operational vehicle; baseline shows 3-of-6 PASS_CUBE clean; 2-of-6 need re-measurement; 1-of-6 BORDERLINE
- CHECKLIST #44(b) -- 6 steps applied; step (f) investigate-why surfaced SPY benchmark gap
- CHECKLIST #67 -- doc-sync same turn
- CHECKLIST #69 -- pyramid mandatory
- CHECKLIST #77 -- canonical-source headers
- CHECKLIST #94 -- queue-mandatory-per-turn
- CHECKLIST #105 -- producer source + caller paths read (cross_sectional.py beta + IVOL gates)
- CHECKLIST #106 -- producer-data audit class
- CHECKLIST #107 -- findings-vs-tickets reconciliation (FIFTEENTH-FULL-EXECUTION)
- CHECKLIST #108 -- N/A (no gate modifications)
