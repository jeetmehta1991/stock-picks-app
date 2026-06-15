# B768 EDGE-PRIOR DEMO VERDICT -- Mean-reversion has LONG edge, SHORT is structurally EV-negative

<!--
# Source: scripts/mean_reversion_edge_prior_test.py (B758 build) demo run completed 2026-06-15T11:53 UTC
# Source: output_audit/mean_reversion_edge_prior_test_demo.json (raw output, 50 tickers x 2024-2025, 24546 bars)
# per CHECKLIST #77 + #44(b) + #69 + #107
# per memory: feedback_no_prior_edge_consolidate_before_tune.md + feedback_no_a_priori_strategy_pruning.md
-->

## Scope

- 50 tickers x 2024-01-01 to 2025-12-31
- 24,546 ticker-bars
- 14 trigger conditions x 3 horizons (5d / 10d / 20d)
- Forward-return measurement (no entry/exit logic; pure conditional-expectation probe)
- Runtime: 9605s (~160 min)

## Aggregate verdict

**MEAN_REVERSION_EDGE_CONFIRMED**

## Per-trigger 10-day forward return table

| Trigger | Direction | N fires | Hit @10d | PnL @10d (bps) | Sharpe @10d | Verdict |
|---|---|---|---|---|---|---|
| rsi_14_lt_30 | LONG | 792 | 63.0% | +183.6 | **+0.281** | EDGE_EXISTS |
| rsi_14_lt_20 | LONG | 42 | 57.1% | +163.3 | +0.243 | EDGE_EXISTS (small N) |
| bb_lower_touch | LONG | 1808 | 58.9% | +137.0 | +0.219 | EDGE_EXISTS |
| ultimate_osc_lt_30 | LONG | 376 | 56.9% | +96.9 | +0.169 | EDGE_EXISTS |
| williams_r_lt_neg80 | LONG | 4633 | 56.0% | +104.3 | +0.151 | EDGE_EXISTS |
| mfi_lt_20 | LONG | 466 | 54.3% | +88.2 | +0.138 | EDGE_EXISTS |
| stoch_k_lt_20 | LONG | 4038 | 55.5% | +86.7 | +0.126 | EDGE_EXISTS |
| bb_upper_touch | SHORT | 2286 | 48.0% | -5.2 | -0.009 | EDGE_NEGATIVE |
| mfi_gt_80 | SHORT | 838 | 48.6% | -26.4 | -0.037 | EDGE_NEGATIVE |
| williams_r_gt_neg20 | SHORT | 6295 | 48.5% | -30.0 | -0.045 | EDGE_NEGATIVE |
| stoch_k_gt_80 | SHORT | 5773 | 48.4% | -34.2 | -0.049 | EDGE_NEGATIVE |
| ultimate_osc_gt_70 | SHORT | 562 | 51.2% | -46.8 | -0.072 | EDGE_NEGATIVE |
| rsi_14_gt_70 | SHORT | 1669 | 45.0% | -54.3 | -0.070 | EDGE_NEGATIVE |
| **rsi_14_gt_80** | SHORT | 144 | 45.8% | **-516.0** | **-0.299** | EDGE_NEGATIVE (extreme losses) |

## Direction-asymmetry analysis

| Aggregate | LONG | SHORT |
|---|---|---|
| n_triggers | 7 | 7 |
| EDGE_EXISTS verdicts | **7/7** | 0/7 |
| EDGE_NEGATIVE verdicts | 0/7 | **7/7** |
| Hit-rate range | 54.3% - 63.0% | 45.0% - 51.2% |
| Mean pnl@10d range | +86.7 to +183.6 bps | -5.2 to -516.0 bps |
| Sharpe@10d range | +0.126 to +0.281 | -0.009 to -0.299 |

**100% direction-asymmetric.** Every LONG oversold trigger has positive edge; every SHORT overbought trigger has negative edge. **Pattern S (short-side asymmetry) EMPIRICALLY VALIDATED on 50 tickers x 2yr.**

## Specific re-interpretation of B766 council recommendations

### Annotation on council ticket #49 (Pattern S pre-register)

**Status: EMPIRICALLY VALIDATED.** The reviewer's claim that mean-reversion overbought-shorts will look bad in cube for STRUCTURAL reasons (drift + borrow + squeeze) is now PRE-CUBE-EMPIRICALLY-CONFIRMED on 50 tickers x 2yr at single-trigger level (no entry/exit/sizing). The cube measurement will show effectively the same pattern with strategy-level gating. Recommend re-rate ticket #49 from MEDIUM to **HIGH** priority. Doc updates to STAGE_4_OSCILLATOR_MEAN_REVERSION_CLUSTER_WALKS.md needed.

### Annotation on council ticket #39 (Connors OR-disjunct emphasis)

**Status: PARTIALLY REFUTED.** Reviewer claimed "RSI(2)<5 is the documented edge; RSI(14)<35 is the slower fallback... NOISY leg that adds most fires." Demo measured rsi_14_lt_30 hit_rate=63% pnl=+184bp/10d Sharpe=0.281 -- **the STRONGEST 10d-Sharpe of all 14 triggers tested**. RSI(14)<30 is a genuine edge, not a noisy fallback. The reviewer's emphasis-backward claim does NOT survive direct measurement. Strategy's actual threshold is rsi_14<35 (looser); cube will measure that. Recommend keep the OR-disjunct in A-1 strat_rsi_oversold pending cube; rsi_14<30 is a strong leg, not noise.

### Validation of `feedback_no_prior_edge_consolidate_before_tune` applicability

**Owner memory rule:** tuning a no-edge strategy on historical data manufactures an overfit backtest.

**This batch's finding:** Mean-reversion LONG side has measurable prior edge (7/7 triggers EDGE_EXISTS) on a 50-ticker x 2yr sample with no strategy-specific gating. Therefore tuning LONG-side gates per council recs #38-#48 is NOT prior-edge-free tuning -- it is refinement of a measurable edge. Memory rule does NOT block LONG-side council tuning.

**SHORT side:** 7/7 EDGE_NEGATIVE. Tuning SHORT-side gates with goal of producing positive edge is exactly what `feedback_no_prior_edge_consolidate_before_tune` warns against. Recommend: keep SHORT-side strategies as EXPLORATORY (per `feedback_no_a_priori_strategy_pruning` no-deletion principle) but pre-register cube expectation = FAIL.

## New ticket surfaced

**#51 `S4-B768-PATTERN-S-EXPLORATORY-TAG-7-MEAN-REV-SHORT-STRATEGIES`** — Per Pattern S EMPIRICAL VALIDATION + `feedback_no_prior_edge_consolidate_before_tune`: tag the 7 SHORT mean-reversion strategies in Cluster A as EXPLORATORY pre-cube (mirror of A-23 / A-24 / W5m precedent). Affected: A-1-S strat_rsi_overbought_short / A-4-S strat_rsi21_overbought_short / A-5-S strat_rsi_volume_200ema_short / A-7-S strat_stochrsi_overbought_short / A-9-S strat_williams_r_overbought_short / A-10-S strat_uo_overbought_short / A-11-S strat_mfi_overbought_short / A-12-S strat_bollinger_upper_short. Cube will run them; cube verdict (per `feedback_no_a_priori_strategy_pruning`) is authoritative; EXPLORATORY tag pre-registers cube FAIL expectation so SHORT-side cube-failure is NOT misread as universal mean-rev failure.

## CHECKLIST #107 reconciliation (B768)

- **Findings surfaced:** 1 primary (MEAN_REVERSION_EDGE_CONFIRMED with 100% direction-asymmetry) + 2 annotation findings (council ticket #49 EMPIRICALLY VALIDATED; council ticket #39 PARTIALLY REFUTED)
- **Tickets filed:** 1 NEW (#51 Pattern S EXPLORATORY tag for 7-8 SHORT mean-rev strategies) + 2 annotations (#49 elevate MEDIUM -> HIGH; #39 partial refutation)
- **Audit-clean: YES**

## Connection to remaining background

- `biu7dcrbi` full fire-bar matrix: still running (~10hr remaining); will provide full-universe Pattern W / J / N validation
- `bh15ewc9v` demo audit (B767 launched): still running; will resolve 14 emitted-but-always-False from Cluster A audit on bigger sample

## Strategy counts (unchanged)

221 ALL_STRATEGIES / 0 DEPRECATED / 1 STRATEGIES_DISABLED_MISSING_PRODUCER / **220 active.** No strategies deleted (per `feedback_no_a_priori_strategy_pruning`); EXPLORATORY tag is non-deletion runtime tagging.
