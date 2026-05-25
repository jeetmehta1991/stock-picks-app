# Phase 1A-β loser strategy audit + fix recommendations

**Source** (per CHECKLIST #77 canonical-source attribution):
- Empirical input: `output_audit/phase1a_beta_recat.json` (Batch 354 regime
  breakdown — worst-5 strategies per regime by sum_pp)
- Code paths audited: `backtest/signals/screener.py` strategy functions
  by `def strat_<name>` definition
- Generator: owner directive 2026-05-25 "Per-strategy fix-queue investigation"
  (option 2 from forensic batch summary)

**Created:** Batch 355 2026-05-25
**Status:** AUDIT FINDINGS + RECOMMENDATIONS. Per CLAUDE.md: no code/gate
changes implemented; owner approval required before any change.

## Scope

10 strategies audited (union of worst-5 per regime). For each, gate logic
read verbatim from `screener.py` and cross-checked against the empirical
n / WR / mean_PnL / sum_pp from Phase 1A-β.

| # | Strategy | Regime | n | Sum pp | Mean PnL% |
|---|---|---|---:|---:|---:|
| 1 | `xs_momentum_bottom_decile_short` | bear | 324 | -1855.66 | -5.73 |
| 2 | `hull_rsi` | bear | 380 | -1340.88 | -3.53 |
| 3 | `htf_aligned_breakout_short` | bear | 188 | -944.52 | -5.02 |
| 4 | `po3_bearish` | bear/neutral | 350+53 | -925+-185 | -2.64/-3.49 |
| 5 | `cpr_narrow_momentum` (long+short) | bear | 176 | -572.35 | -3.25 |
| 6 | `cpr_narrow_bullish` (long+short) | bull | 642 | -1616.59 | -2.52 |
| 7 | `avwap_50_reclaim` | bull | 382 | -722.36 | -1.89 |
| 8 | `monthly_bias_momentum_long` | bull | 470 | -411.79 | -0.88 |
| 9 | `xs_low_beta_long` | neutral | 30 | -186.59 | -6.22 |
| 10 | `pivot_r1_breakout` | neutral | 21 | -102.47 | -4.88 |

## Headline findings

1. **No code bugs / sign-flips.** Every gate read is symmetric and correctly
   directed (long fires on bullish setup, short fires on bearish setup).
   The losses are not coming from a single inverted comparison.

2. **Structural pattern: missing bear-regime long-block.** Long-only
   mean-reversion strategies (`hull_rsi`, `cpr_narrow_bullish`,
   `cpr_narrow_momentum`) have NO `not price_above_ema_200`-style
   bear-regime gate. They fire long into bear regimes and catch falling
   knives. This is consistent across the worst bear-regime drivers.

3. **Inverted-application defect on Frazzini-Pedersen BAB
   (`xs_low_beta_long`).** The strategy gates LONG low-beta on
   `price_above_ema_200` (bull regime). Per Frazzini-Pedersen 2014 JFE +
   Blitz-van Vliet 2024 JPM, the BAB anomaly's *absolute* edge is in
   bear/neutral regimes (low-beta cushions drawdowns; bull regimes are
   where low-beta UNDER-performs absolutely). The Phase 1A-β data
   confirms: n=30 in neutral with mean -6.22% — the strategy is
   capturing the side of the anomaly where BAB long-only is weakest.
   *This is the only candidate that looks like a code/gate-config bug
   rather than a strategy-design issue.*

4. **Short-side momentum factor structurally weak**
   (`xs_momentum_bottom_decile_short` mean PnL -5.73 in bear, n=324).
   Bottom-decile momentum stocks have already crashed; shorting them
   exposes to bounce-risk + short-squeeze + borrow cost. Literature
   (Asness-Frazzini-Pedersen 2013; Israel-Moskowitz 2013) consistently
   finds the long-leg of the momentum anomaly carries 70-90% of the
   alpha; the short-leg is weak/null after costs.

5. **Signal-timeframe vs hold-period mismatch.** `cpr_narrow_*`, `po3_*`,
   `htf_aligned_breakout_short` are all 1-day-candle-based signals. The
   alpha decays within 1-3 trading days, but the engine's
   `atr_trail_1x` exit holds positions through the trailing-stop window
   (typically 5-20 days). Result: enter on signal, watch alpha
   evaporate, eventually exit at the trailing stop for a small-to-mid
   loss. Consistent with the moderate-negative mean PnLs observed
   (-2.5 to -3.5).

6. **Asymmetric long-vs-short edge.** `htf_aligned_breakout_long` mean
   PnL is ~0 (n=141, sum=-202pp), but `htf_aligned_breakout_short` mean
   is -5.02 (n=188, sum=-944pp). Same-mechanic short variant performs
   materially worse — consistent with Stambaugh-Yu-Yuan 2012 finding
   that anomaly short-legs are systematically weaker than their long-leg
   counterparts.

## Per-strategy fix recommendations

**HARD RULE:** None of the below is implemented. All are RECOMMENDATIONS
for owner review per CLAUDE.md.

### A. Inverted gate (most likely real bug)

#### `xs_low_beta_long` — Recommended: reverse the regime gate
Current gate (`screener.py:1487`):
```python
fires = (
    s.get("xs_low_beta_decile", False)
    and s.get("price_above_ema_200", True)   # bull regime
    and s.get("xs_avoid_high_ivol", True)
)
```
Recommended:
```python
# Option A: remove regime gate entirely (BAB is regime-agnostic risk-adjusted)
fires = (
    s.get("xs_low_beta_decile", False)
    and s.get("xs_avoid_high_ivol", True)
)
# Option B: invert (gate on bear/neutral)
fires = (
    s.get("xs_low_beta_decile", False)
    and (not s.get("price_above_ema_200", True))
    and s.get("xs_avoid_high_ivol", True)
)
```
Confidence the current gate is wrong: MEDIUM-HIGH. Literature application
(Frazzini-Pedersen 2014 JFE) does not gate on bull regime; the BAB
factor's published Sharpe is across full sample.

### B. Missing bear-regime long-block

For each long-only strategy below, the gate has NO bear-regime exclusion
and the Phase 1A-β data shows catastrophic bear-regime losses.

| Strategy | Current line | Recommended addition |
|---|---:|---|
| `hull_rsi` (long leg) | 313 | Add `and s.get("price_above_ema_200", True)` |
| `cpr_narrow_bullish` (long leg) | 231 | Add `and s.get("price_above_ema_200", True)` |
| `cpr_narrow_momentum` (long leg) | 994 | Add `and s.get("price_above_ema_200", True)` |
| `monthly_bias_momentum_long` | 1633 | (Already filtered by monthly_bias_bull but bull bias is monthly-grained; consider adding daily `price_above_ema_200`.) |

Confidence the gate addition would have prevented the observed losses:
HIGH. The 200-EMA test is cheap, well-documented (Faber 2013 GMR), and
already used as a regime gate elsewhere in the screener.

### C. Short-side momentum factor weakness

#### `xs_momentum_bottom_decile_short`
Three paths, owner choice:
1. **Tighten gate**: require additional bear-confirmation signals
   (e.g., `+ s.get("smart_money_distribution_signal", False)` + `+
   (s.get("vix_value", 20) > 25)`). Reduces fire rate but improves
   signal quality on the residual fires.
2. **Mark Layer-1 baseline only, no scaling**: keep the strategy active
   for completeness (per `project_no_apriori_strategy_pruning` memory)
   but flag it as "literature-weak short-leg" in metadata so the
   walk-forward / Phase 1B-α verdicts don't get distorted.
3. **Empirical re-deprecation**: per the owner's "empirical validation
   over literature" directive (Batch 316a), the strategy now has
   empirical evidence (-5.73 mean / 324 trades / -1856pp) supporting
   re-deprecation. This is consistent with Asness-Frazzini-Pedersen
   2013 + Israel-Moskowitz 2013 findings.

### D. Signal-timeframe vs hold-period mismatch

For `cpr_narrow_*`, `po3_*`, `htf_aligned_breakout_short`: signal alpha
decays in 1-3 days but exit holds 5-20 days. Recommended:

- **Time-stop fallback**: add T+3 close-out per DEC-018 / DEC-135 if the
  position hasn't moved >+1R by T+3. Codify in `STRATEGY_EXIT_OVERRIDE`
  for these strategies specifically.
- **OR** convert exit method to a fast-decay-aware exit (e.g.,
  `fixed_3r_2r` if it survives DEC-353 re-review, or a new
  `time_stop_3d_or_atr_trail` method).
- **NOT recommended**: removing the strategies entirely until time-stop
  variant is tested.

### E. Asymmetric short-leg

`htf_aligned_breakout_short` is the canonical example: same gate as the
long variant but mean PnL is -5.02 vs ~0 for the long.

Recommended: codify a portfolio-level "short-leg multiplier" config
(e.g., `SHORT_LEG_POSITION_SIZE_MULT = 0.5`) reflecting Stambaugh-Yu-Yuan
2012 + Avramov-Cheng-Hameed 2016 findings that anomaly short-legs are
systematically weaker. Already partially implemented for `crisis_CRISIS_FLAG`
regime (50% sizing) per CLAUDE.md; extend the concept to short direction
in general.

## What is NOT recommended

- **Bulk deprecation**: per `project_no_apriori_strategy_pruning` memory
  (owner directive 2026-05-25 Batch 316a), all 148 strategies get Stage D
  + Phase 1A-β empirical verdicts before any pruning. The above are
  recommended FIXES not deprecations.
- **Removing the regime classifier entirely**: it correctly identifies
  the regime; the issue is that not every strategy USES it.
- **Force-zero short sizing**: 50% multiplier preserves the empirical
  edge measurement without giving away the alpha when it does appear.

## Cross-batch context

These recommendations target the 5 fired strategies (~2700 trades of the
7191 total) driving roughly -5800pp of the -11,387pp aggregate. Even
modest improvement (e.g., bear-block on `hull_rsi` + `cpr_narrow_*`
eliminates ~50-60% of those strategies' losses) would shift Phase 1A-β
aggregate from -11k to ~-5k pp — still net-negative but materially
better.

The forensic verdict (0/66 PASS criteria) is unlikely to flip to many
PASS verdicts from these fixes alone. The actual remediation pathway is
multi-pronged: (1) gate fixes here, (2) Wave 3 + Batch 312-314 fixes
unblock the 73 QUIET strategies, (3) Phase 1A-β full re-run to measure
the post-fix verdict, (4) per-strategy walk-forward + DSR per DEC-503.

## Next batch hand-off

If owner approves recommendation **A** (xs_low_beta_long inverted gate)
+ **B** (bear-regime long-block on hull_rsi / cpr_narrow_*):
- Batch 356: implement the gate changes
- Per-addressal pyramid per `feedback_pyramid_per_addressal` memory
- Golden output regen + diff review
- Commit + push
- Phase 1A-β re-run measurement on Hetzner

If owner approves **D** (time-stop on signal-timeframe-mismatched strategies):
- Batch 357: extend `STRATEGY_EXIT_OVERRIDE` for the named strategies
- New exit-method test in `backtest/tests/test_exit_strategies.py`
- Per-addressal pyramid
