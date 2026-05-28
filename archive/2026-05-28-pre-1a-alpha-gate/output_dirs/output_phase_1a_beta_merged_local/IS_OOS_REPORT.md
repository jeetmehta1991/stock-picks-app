# Phase 1A-beta IS/OOS validity report

**IS window**: 2022-01 -> 2024-06 (~2.5y)
**OOS window**: 2024-07 -> 2026-04 (~1.8y)
**Source**: /root/stock-picks-app/output_phase_1a_beta_merged_local/trade_log.csv

## Aggregate
| | IS | OOS |
|---|---:|---:|
| n | 4387 | 2804 |
| WR | 29.34% | 30.71% |
| Mean PnL | -1.62% | -1.53% |
| Sum pp | -7094.5 | -4292.7 |
| Sharpe proxy | -1.55 | -1.6 |

## Overfitting verdict
**OOS HOLDS**: OOS within 0.5pp of IS. Per-strategy assignments generalize.

## Top 10 strategies by OOS aggregate

| Strategy | IS n | IS mean | OOS n | OOS mean | OOS-IS delta |
|---|---:|---:|---:|---:|---:|
| williams_r_oversold | 60 | +0.85% | 117 | +2.93% | 2.08 |
| lead_lag_sector_rotation | 15 | -4.47% | 6 | +24.58% | 29.05 |
| bollinger_tight | 28 | +5.54% | 42 | +2.15% | -3.39 |
| smc_order_block_bounce | 31 | -1.83% | 38 | +2.09% | 3.93 |
| smc_bos_retest_entry | 10 | +3.37% | 4 | +11.57% | 8.2 |
| stochrsi_oversold | 13 | -0.84% | 52 | +0.59% | 1.43 |
| smc_choch_reversal | 130 | -0.17% | 144 | +0.21% | 0.38 |
| ichimoku_cloud_breakout | 5 | +2.42% | 10 | +2.76% | 0.33 |
| orb_stocks_in_play_long | 25 | +14.62% | 67 | +0.36% | -14.26 |
| bollinger_lower | 403 | -1.48% | 25 | +0.94% | 2.42 |

## Bottom 10 by OOS aggregate

| Strategy | IS n | IS mean | OOS n | OOS mean | OOS-IS delta |
|---|---:|---:|---:|---:|---:|
| stochrsi_overbought_short | 262 | -0.98% | 26 | -5.44% | -4.46 |
| smc_inverse_fvg | 191 | -2.02% | 84 | -1.94% | 0.08 |
| po3_bullish | 193 | -1.17% | 223 | -0.81% | 0.36 |
| hull_rsi | 364 | -3.07% | 56 | -3.30% | -0.23 |
| htf_aligned_breakout_short | 138 | -5.59% | 55 | -3.75% | 1.84 |
| buyback_8k_recent_long | 29 | -2.00% | 69 | -3.24% | -1.24 |
| xs_momentum_bottom_decile_short | 276 | -5.60% | 48 | -6.43% | -0.83 |
| po3_bearish | 261 | -1.45% | 142 | -5.16% | -3.72 |
| avwap_50_reclaim | 156 | +0.01% | 242 | -3.11% | -3.12 |
| cpr_narrow_bullish | 375 | -1.27% | 375 | -2.94% | -1.67 |

Per-(strategy x exit) cube: see per_cell_is_oos.csv
