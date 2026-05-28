# Phase 1A-beta IS/OOS validity report

**IS window**: 2022-01 -> 2024-06 (~2.5y)
**OOS window**: 2024-07 -> 2026-04 (~1.8y)
**Source**: output_stage_d\trade_log.csv

## Aggregate
| | IS | OOS |
|---|---:|---:|
| n | 211 | 199 |
| WR | 31.28% | 36.68% |
| Mean PnL | -0.98% | +2.69% |
| Sum pp | -207.3 | +535.0 |
| Sharpe proxy | -1.27 | 1.89 |

## Overfitting verdict
**OVERFITTING SUSPECT**: OOS mean PnL differs from IS by >1pp. Per-strategy exit assignments may be over-tuned to 2022-2023 data.

## Top 10 strategies by OOS aggregate

| Strategy | IS n | IS mean | OOS n | OOS mean | OOS-IS delta |
|---|---:|---:|---:|---:|---:|
| htf_aligned_breakout_long | 4 | -3.45% | 12 | +17.24% | 20.7 |
| monthly_bias_momentum_long | 15 | -1.53% | 11 | +14.95% | 16.49 |
| orb_stocks_in_play_long | 11 | -0.98% | 24 | +3.98% | 4.96 |
| buyback_8k_recent_long | 7 | -4.82% | 17 | +5.03% | 9.86 |
| pivot_r1_breakout | 5 | +0.38% | 5 | +15.66% | 15.28 |
| williams_r_oversold | 2 | +29.80% | 3 | +22.26% | -7.55 |
| xs_low_beta_long | 17 | +0.38% | 13 | +3.57% | 3.19 |
| smc_inverse_fvg | 14 | -0.57% | 14 | +3.26% | 3.83 |
| avwap_50_reclaim | 12 | +3.26% | 6 | +4.99% | 1.73 |
| xs_momentum_top_decile | 6 | +1.59% | 6 | +3.18% | 1.6 |

## Bottom 10 by OOS aggregate

| Strategy | IS n | IS mean | OOS n | OOS mean | OOS-IS delta |
|---|---:|---:|---:|---:|---:|
| smc_order_block_bounce | 0 | +0.00% | 1 | -10.93% | nan |
| macd_fast_crossover | 4 | -6.72% | 2 | -7.41% | -0.69 |
| cpr_narrow_bullish | 8 | -1.87% | 10 | -1.64% | 0.23 |
| ultimate_oscillator | 2 | +5.00% | 2 | -9.47% | -14.47 |
| xs_momentum_bottom_decile_short | 2 | +10.76% | 2 | -10.39% | -21.15 |
| po3_bearish | 11 | +1.64% | 8 | -3.22% | -4.86 |
| smc_choch_reversal | 4 | -3.25% | 15 | -2.70% | 0.55 |
| orb_stocks_in_play_short | 10 | -1.93% | 4 | -10.37% | -8.43 |
| smc_bos_continuation | 6 | -5.88% | 13 | -3.31% | 2.56 |
| po3_bullish | 7 | -0.25% | 12 | -4.40% | -4.15 |

Per-(strategy x exit) cube: see per_cell_is_oos.csv
