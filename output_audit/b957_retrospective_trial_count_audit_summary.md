# Batch 957 (2026-06-20): Retrospective Trial-Count Audit

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.2 + Council 61+62 UNANIMOUS per CHECKLIST #77.

## Owner Question Trigger (2026-06-20)

> "In any phases will we be undertaking parameter optimization so we improve the performance of the strategies?"

## Council 61 Critical Finding

DEC #5 baseline DSR N = 5,694 (219 strategies x 26 exits). But Stage 4 walks edited gates across ~221 strategies over 100+ batches (B500-B956). Each gate edit was a TRIAL against the same 2020-2026 data. The roster you have today is the SURVIVOR of an UNBUDGETED SEARCH.

## Council 62 Verdict (UNANIMOUS unconditional ship for C)

- C (this audit) ships unconditionally: pure measurement, no DSR/OOS/B705 violation possible.
- B (Phase 6.5 design) follows next turn with informed data, not assumption.
- Council 62 REJECTS owner's proposed 28,500-cell pre-R5 exit sweep + 730-review FIRE_STARVED gate loosening as overfitting machines.
- Council 62 RECOMMENDS NARROW Phase 6.5 (see batch 18).

## Measurement Results

- **Walk-era commits scanned:** 492 (B500-B956)
- **Trial commits (gate/threshold/regime/STATE-EVENT/producer/new-strat/deletion):** 100
- **Average strategies affected per trial commit:** 2.0
- **Estimated walk-era added trials:** ~200
- **DEC #5 baseline N:** 5,694
- **N_effective total estimate:** ~5894
- **Inflation factor vs baseline:** 1.04x
- **DSR threshold inflation:** ~1.002x

## Trial Categories (commits matching each pattern)

| Category | Count |
|---|---|
| gate_change | 49 |
| threshold_change | 17 |
| producer_rewrite | 17 |
| strategy_deletion | 14 |
| new_strategy | 8 |
| state_event_conversion | 7 |
| regime_affinity | 5 |
| docstring_only | 5 |

## Interpretation

Walk-era B500-B956 added ~200 parameter trials to DEC #5 baseline 5,694. N_effective ~5894 (1.04x inflation).

DSR threshold inflation ~1.002x means original 0.95 calibration may correspond to ~0.952 at corrected N.

## Council 61 Recommendation (informs Phase 6.5)

If N_effective >> 5,694, options:

- Recalibrate DSR gate threshold downward to reflect inflated N
- OR seal OOS 2026-Q2+ mandatory before R5 PASS honored
- OR both

## Council 62 Phase 6.5 Anchor (next turn batch 18)

- Type 1 POST-R5 narrow refinement: limit to <200 new trials (cells within ±15% of passing gates)
- Type 2 Track A consolidation (pre-R5): 0 new trials added (deletion reduces N)
- Type 2 Track B loosening (post-R5): trial-budgeted in DSR; survivor-only
- Council 7 binding 'R5 -> no changes' RESET via logged DEC explicitly (not silent)
- DEC #4 OOS seal preserved: 2026-Q2+ held-out for any refinement

## Per-Strategy Named Trial Counts (best-effort from commit subjects)

Top-20 strategies with most-named trial commits:

| Strategy | Trials | 
|---|---|
| `borrow_ok` | 4 |
| `hull_rsi` | 2 |
| `bollinger_lower` | 1 |
| `ichimoku_cloud_breakout` | 1 |
| `hull_rsi_short` | 1 |
| `52w_high_breakout` | 1 |
| `pivot_r3_blowoff_short` | 1 |
| `pivot_s3_capitulation` | 1 |
| `morning_star` | 1 |
| `three_white_soldiers` | 1 |
| `three_black_crows_short` | 1 |
| `squeeze_setup_event_only_long` | 1 |

## Honest Limitations

- Per-strategy trial count is BEST-EFFORT from commit subjects; cluster-walk commits affect multiple strategies
- Trial classification uses keyword patterns; may miss / over-count
- avg_strategies_per_trial_commit=2.0 is conservative; real may be 1-5
- Earlier batches (B100-B499) NOT scanned this batch; Council 62 scope was B500-B956
- DSR threshold inflation formula uses sqrt(log) approximation; exact recalibration requires Lo 2002 formula

## Compliance Statement

| Council 61+62 mandate | Status |
|---|---|
| C ships this turn unconditionally | OK |
| Pure measurement; no DSR/OOS/B705 violation | OK |
| Honest limitations surfaced | OK |
| Informs B (Phase 6.5) next turn | OK |
| Single artifact per Council 55-60 mandate | OK |
