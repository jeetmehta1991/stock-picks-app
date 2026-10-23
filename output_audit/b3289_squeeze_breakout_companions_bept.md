# COMPANION-SIGNAL SCREEN - squeeze_breakout (exact names)

exit breakeven_plus_trail; window is; 953 unique entries; 440 signals tested; BH-FDR q=0.05 threshold p<=0.029432; 259 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | xs_max_anomaly | numeric | Q5-Q1 +19.83 (rho +0.346) | n 942, Q5 21.24 vs Q1 1.41 | 8.16e-28 |
| 2 | gold_silver_20d_pct_change | numeric | Q5-Q1 +18.69 (rho +0.343) | n 953, Q5 20.04 vs Q1 1.36 | 1.03e-27 |
| 3 | short_interest_observations | numeric | Q5-Q1 +18.33 (rho +0.315) | n 951, Q5 19.87 vs Q1 1.54 | 2.72e-23 |
| 4 | vix_percentile | numeric | Q5-Q1 +17.88 (rho +0.326) | n 953, Q5 20.21 vs Q1 2.32 | 4.24e-25 |
| 5 | po3_accum_range_pct | numeric | Q5-Q1 +17.81 (rho +0.274) | n 953, Q5 20.06 vs Q1 2.25 | 7.41e-18 |
| 6 | sector_strongest_rs | numeric | Q5-Q1 -17.16 (rho -0.326) | n 953, Q5 0.96 vs Q1 18.12 | 4.92e-25 |
| 7 | vix_today | numeric | Q5-Q1 +16.79 (rho +0.330) | n 953, Q5 19.81 vs Q1 3.02 | 1.31e-25 |
| 8 | vix_value | numeric | Q5-Q1 +16.79 (rho +0.330) | n 953, Q5 19.81 vs Q1 3.02 | 1.31e-25 |
| 9 | vix_vix3m_ratio | numeric | Q5-Q1 +16.71 (rho +0.359) | n 953, Q5 19.80 vs Q1 3.09 | 1.97e-30 |
| 10 | bb_10_20_bandwidth | numeric | Q5-Q1 +16.57 (rho +0.268) | n 953, Q5 18.18 vs Q1 1.61 | 3.41e-17 |
| 11 | vix_term_backwardation | bool | +16.54 (T 18.75 vs F 2.21) | n 249/704, WR 0.711 vs 0.290 | 1.11e-20 |
| 12 | vix_term_contango | bool | -16.54 (T 2.21 vs F 18.75) | n 704/249, WR 0.290 vs 0.711 | 1.11e-20 |
| 13 | cot_rut_commercials_net_pct | numeric | Q5-Q1 -16.36 (rho -0.319) | n 953, Q5 3.20 vs Q1 19.56 | 5.44e-24 |
| 14 | bb_20_20_reclaim_from_lower_recent_3d | bool | +15.37 (T 18.89 vs F 3.51) | n 187/766, WR 0.727 vs 0.320 | 1.48e-14 |
| 15 | atr_pct | numeric | Q5-Q1 +15.23 (rho +0.243) | n 953, Q5 17.05 vs Q1 1.82 | 2.60e-14 |
| 16 | bb_20_15_bandwidth | numeric | Q5-Q1 +14.79 (rho +0.232) | n 953, Q5 16.63 vs Q1 1.84 | 3.69e-13 |
| 17 | bb_20_20_bandwidth | numeric | Q5-Q1 +14.79 (rho +0.232) | n 953, Q5 16.63 vs Q1 1.84 | 3.70e-13 |
| 18 | pct_change_10d | numeric | Q5-Q1 -13.98 (rho -0.259) | n 953, Q5 2.66 vs Q1 16.64 | 4.85e-16 |
| 19 | macd_8_21_5_line | numeric | Q5-Q1 -13.92 (rho -0.213) | n 953, Q5 2.21 vs Q1 16.13 | 2.94e-11 |
| 20 | rsi_14_cross_up_oversold_recent_3d | bool | +13.85 (T 18.04 vs F 4.19) | n 161/792, WR 0.702 vs 0.338 | 2.13e-11 |
| 21 | smc_choch_bearish | bool | +13.74 (T 18.71 vs F 4.97) | n 108/845, WR 0.648 vs 0.368 | 9.69e-07 |
| 22 | pct_from_avwap_20low | numeric | Q5-Q1 +13.73 (rho +0.221) | n 920, Q5 15.89 vs Q1 2.16 | 1.30e-11 |
| 23 | ppo | numeric | Q5-Q1 -13.14 (rho -0.208) | n 953, Q5 2.52 vs Q1 15.65 | 9.34e-11 |
| 24 | bb_10_20_reclaim_from_lower_recent_3d | bool | +13.01 (T 17.12 vs F 4.11) | n 177/776, WR 0.661 vs 0.340 | 2.68e-10 |
| 25 | bb_20_15_pctb | numeric | Q5-Q1 -12.94 (rho -0.215) | n 953, Q5 2.20 vs Q1 15.14 | 2.09e-11 |
| 26 | bb_20_20_pctb | numeric | Q5-Q1 -12.94 (rho -0.215) | n 953, Q5 2.20 vs Q1 15.14 | 2.10e-11 |
| 27 | pct_from_avwap_50low | numeric | Q5-Q1 +12.51 (rho +0.196) | n 922, Q5 15.08 vs Q1 2.57 | 1.77e-09 |
| 28 | bond_equity_ratio | numeric | Q5-Q1 -12.51 (rho -0.192) | n 953, Q5 1.32 vs Q1 13.83 | 2.22e-09 |
| 29 | roc_12 | numeric | Q5-Q1 -12.50 (rho -0.236) | n 953, Q5 4.72 vs Q1 17.22 | 1.67e-13 |
| 30 | stoch_d | numeric | Q5-Q1 -12.41 (rho -0.229) | n 953, Q5 3.26 vs Q1 15.67 | 7.92e-13 |
| 31 | ppo_hist | numeric | Q5-Q1 -12.31 (rho -0.230) | n 953, Q5 4.23 vs Q1 16.54 | 6.18e-13 |
| 32 | macd_12_26_9_hist | numeric | Q5-Q1 -12.23 (rho -0.214) | n 953, Q5 3.87 vs Q1 16.10 | 2.33e-11 |
| 33 | macd_8_21_5_signal | numeric | Q5-Q1 -12.23 (rho -0.164) | n 953, Q5 2.73 vs Q1 14.95 | 3.75e-07 |
| 34 | ao | numeric | Q5-Q1 -11.96 (rho -0.175) | n 953, Q5 2.45 vs Q1 14.41 | 5.40e-08 |
| 35 | macd_12_26_9_line | numeric | Q5-Q1 -11.86 (rho -0.180) | n 953, Q5 2.65 vs Q1 14.52 | 2.15e-08 |
| 36 | rsi_9_cross_up_oversold_recent_3d | bool | +11.61 (T 15.24 vs F 3.63) | n 238/715, WR 0.630 vs 0.323 | 3.16e-12 |
| 37 | bb_20_15_reclaim_from_lower_recent_3d | bool | +11.52 (T 14.95 vs F 3.44) | n 256/697, WR 0.625 vs 0.317 | 1.08e-12 |
| 38 | gold_silver_ratio | numeric | Q5-Q1 +10.93 (rho +0.351) | n 953, Q5 13.80 vs Q1 2.88 | 4.74e-29 |
| 39 | support_break_retest | bool | +10.93 (T 16.02 vs F 5.10) | n 125/828, WR 0.672 vs 0.359 | 1.07e-06 |
| 40 | smc_retracement_pct | numeric | Q5-Q1 +10.62 (rho +0.195) | n 953, Q5 13.09 vs Q1 2.47 | 1.31e-09 |
