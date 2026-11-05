# COMPANION-SIGNAL SCREEN - rsi_oversold_with_smart_money_long (exact names)

exit breakeven_plus_trail; basis net; window is; 2135 unique entries; 569 signals tested; BH-FDR q=0.05 threshold p<=0.0085237; 97 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | vix_term_backwardation | bool | +7.46 (T 9.08 vs F 1.62) | n 258/1877, WR 0.477 vs 0.246 | 5.42e-10 |
| 2 | vix_term_contango | bool | -7.46 (T 1.62 vs F 9.08) | n 1877/258, WR 0.246 vs 0.477 | 5.42e-10 |
| 3 | cot_rut_commercials_net_pct | numeric | Q5-Q1 -6.68 (rho -0.193) | n 2135, Q5 -0.29 vs Q1 6.39 | 2.06e-19 |
| 4 | smc_choch_bearish | bool | +6.17 (T 8.36 vs F 2.19) | n 114/2021, WR 0.412 vs 0.266 | 1.51e-03 |
| 5 | gold_silver_20d_pct_change | numeric | Q5-Q1 +6.04 (rho +0.114) | n 2135, Q5 7.30 vs Q1 1.26 | 1.44e-07 |
| 6 | cot_copper_commercials_pctile_3y | numeric | Q5-Q1 +5.23 (rho +0.200) | n 2135, Q5 5.14 vs Q1 -0.09 | 1.27e-20 |
| 7 | cot_copper_commercials_net_pct | numeric | Q5-Q1 +5.22 (rho +0.224) | n 2135, Q5 5.72 vs Q1 0.50 | 1.09e-25 |
| 8 | xs_max_anomaly | numeric | Q5-Q1 +5.12 (rho +0.068) | n 2118, Q5 6.25 vs Q1 1.13 | 1.78e-03 |
| 9 | squeeze_fire_up | bool | +4.82 (T 7.05 vs F 2.22) | n 132/2003, WR 0.432 vs 0.264 | 3.16e-03 |
| 10 | vix_percentile | numeric | Q5-Q1 +4.64 (rho +0.100) | n 2135, Q5 6.64 vs Q1 2.00 | 3.54e-06 |
| 11 | short_interest_observations | numeric | Q5-Q1 +4.55 (rho +0.119) | n 2135, Q5 4.64 vs Q1 0.09 | 3.65e-08 |
| 12 | ppo_signal | numeric | Q5-Q1 -4.49 (rho -0.081) | n 2135, Q5 1.00 vs Q1 5.49 | 1.73e-04 |
| 13 | vix_vix3m_ratio | numeric | Q5-Q1 +4.32 (rho +0.088) | n 2135, Q5 6.74 vs Q1 2.42 | 4.25e-05 |
| 14 | gold_silver_ratio | numeric | Q5-Q1 +4.30 (rho +0.126) | n 2135, Q5 5.57 vs Q1 1.27 | 5.60e-09 |
| 15 | monthly_above_sma_6 | bool | -4.00 (T 1.36 vs F 5.35) | n 1328/684, WR 0.239 vs 0.360 | 6.32e-08 |
| 16 | macd_12_26_9_signal | numeric | Q5-Q1 -3.94 (rho -0.076) | n 2135, Q5 0.85 vs Q1 4.79 | 4.47e-04 |
| 17 | pct_from_avwap_20low | numeric | Q5-Q1 +3.93 (rho +0.080) | n 1891, Q5 4.97 vs Q1 1.04 | 4.87e-04 |
| 18 | chandelier_short_flip_up | bool | +3.62 (T 5.82 vs F 2.20) | n 190/1945, WR 0.405 vs 0.261 | 6.21e-03 |
| 19 | xs_momentum_12_1 | numeric | Q5-Q1 +3.59 (rho +0.073) | n 2120, Q5 4.47 vs Q1 0.87 | 7.74e-04 |
| 20 | xs_momentum_top_decile | bool | +3.52 (T 5.32 vs F 1.80) | n 457/1663, WR 0.381 vs 0.245 | 7.48e-05 |
| 21 | ema_20_50_bearish | bool | +3.38 (T 4.63 vs F 1.26) | n 800/1335, WR 0.349 vs 0.229 | 4.44e-07 |
| 22 | ema_20_50_bullish | bool | -3.38 (T 1.26 vs F 4.63) | n 1335/800, WR 0.229 vs 0.349 | 4.44e-07 |
| 23 | rsi_9_cross_up_oversold_recent_3d | bool | +3.33 (T 5.32 vs F 1.99) | n 337/1798, WR 0.353 vs 0.259 | 3.65e-04 |
| 24 | ichi_below_cloud | bool | +3.27 (T 4.84 vs F 1.57) | n 618/1517, WR 0.343 vs 0.246 | 1.89e-05 |
| 25 | sector_weakest_rs | numeric | Q5-Q1 -3.24 (rho -0.100) | n 2135, Q5 2.24 vs Q1 5.49 | 3.70e-06 |
| 26 | ichi_weekly_above_cloud | bool | +3.16 (T 4.01 vs F 0.85) | n 1188/824, WR 0.303 vs 0.248 | 3.17e-08 |
| 27 | sector_strongest_rs | numeric | Q5-Q1 -3.03 (rho -0.118) | n 2135, Q5 1.38 vs Q1 4.42 | 4.64e-08 |
| 28 | smc_choch_bullish | bool | -3.01 (T -0.31 vs F 2.70) | n 128/2007, WR 0.141 vs 0.283 | 3.57e-04 |
| 29 | cot_dxy_mmoney_pctile_3y | numeric | Q5-Q1 +2.99 (rho +0.096) | n 2135, Q5 5.08 vs Q1 2.09 | 9.81e-06 |
| 30 | news_uses_polygon_score | bool | +2.97 (T 4.97 vs F 1.99) | n 380/1755, WR 0.337 vs 0.260 | 1.29e-03 |
| 31 | cot_dow_mmoney_pctile_3y | numeric | Q5-Q1 -2.95 (rho -0.074) | n 2135, Q5 1.27 vs Q1 4.22 | 6.44e-04 |
| 32 | dxy_proxy_close | numeric | Q5-Q1 +2.94 (rho +0.102) | n 2135, Q5 2.05 vs Q1 -0.89 | 2.47e-06 |
| 33 | sma_20_50_bullish | bool | -2.92 (T 1.29 vs F 4.20) | n 1232/903, WR 0.229 vs 0.336 | 2.95e-06 |
| 34 | ichi_weekly_in_cloud | bool | -2.89 (T 0.73 vs F 3.62) | n 629/1383, WR 0.246 vs 0.296 | 4.10e-07 |
| 35 | avwap_252low_reclaim_recent_3d | bool | +2.89 (T 5.12 vs F 2.23) | n 364/1674, WR 0.354 vs 0.265 | 3.84e-03 |
| 36 | bb_20_20_reclaim_from_lower_recent_3d | bool | +2.87 (T 4.92 vs F 2.05) | n 348/1787, WR 0.325 vs 0.264 | 2.84e-03 |
| 37 | monthly_bias_bull | bool | -2.84 (T 1.53 vs F 4.37) | n 1171/841, WR 0.244 vs 0.331 | 1.30e-05 |
| 38 | bb_10_20_reclaim_from_lower_recent_3d | bool | +2.84 (T 4.92 vs F 2.08) | n 329/1806, WR 0.371 vs 0.256 | 1.15e-03 |
| 39 | smc_ote_short_zone | bool | -2.82 (T 0.02 vs F 2.85) | n 247/1888, WR 0.178 vs 0.287 | 1.57e-06 |
| 40 | smc_ob_bearish_active | bool | +2.77 (T 4.66 vs F 1.89) | n 487/1648, WR 0.331 vs 0.257 | 1.52e-03 |
