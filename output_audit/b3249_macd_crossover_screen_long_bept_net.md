# COMPANION-SIGNAL SCREEN - macd_crossover (exact names)

exit breakeven_plus_trail; basis net; window is; 1121 unique entries; 429 signals tested; BH-FDR q=0.05 threshold p<=0.0099068; 85 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | vix_term_backwardation | bool | +19.34 (T 20.86 vs F 1.52) | n 134/987, WR 0.657 vs 0.306 | 2.53e-10 |
| 2 | vix_term_contango | bool | -19.34 (T 1.52 vs F 20.86) | n 987/134, WR 0.306 vs 0.657 | 2.53e-10 |
| 3 | vix_today | numeric | Q5-Q1 +12.87 (rho +0.177) | n 1121, Q5 14.23 vs Q1 1.35 | 2.66e-09 |
| 4 | vix_value | numeric | Q5-Q1 +12.87 (rho +0.177) | n 1121, Q5 14.23 vs Q1 1.35 | 2.66e-09 |
| 5 | cot_dxy_mmoney_pctile_3y | numeric | Q5-Q1 +12.77 (rho +0.130) | n 1121, Q5 12.89 vs Q1 0.11 | 1.24e-05 |
| 6 | vix_vix3m_ratio | numeric | Q5-Q1 +11.94 (rho +0.157) | n 1121, Q5 14.11 vs Q1 2.16 | 1.37e-07 |
| 7 | usd_weakening | bool | +11.93 (T 13.87 vs F 1.93) | n 178/943, WR 0.466 vs 0.326 | 1.12e-05 |
| 8 | vix_percentile | numeric | Q5-Q1 +11.30 (rho +0.118) | n 1121, Q5 13.94 vs Q1 2.64 | 7.49e-05 |
| 9 | short_interest_observations | numeric | Q5-Q1 +11.04 (rho +0.118) | n 1118, Q5 11.24 vs Q1 0.20 | 7.65e-05 |
| 10 | xs_max_anomaly | numeric | Q5-Q1 +11.02 (rho +0.145) | n 1111, Q5 12.28 vs Q1 1.26 | 1.24e-06 |
| 11 | news_uses_polygon_score | bool | +10.27 (T 12.65 vs F 2.38) | n 158/963, WR 0.456 vs 0.330 | 3.49e-05 |
| 12 | atr_pct | numeric | Q5-Q1 +10.12 (rho +0.104) | n 1121, Q5 11.16 vs Q1 1.05 | 4.60e-04 |
| 13 | gold_silver_20d_pct_change | numeric | Q5-Q1 +9.96 (rho +0.200) | n 1121, Q5 13.07 vs Q1 3.11 | 1.38e-11 |
| 14 | bb_20_15_bandwidth | numeric | Q5-Q1 +9.67 (rho +0.080) | n 1121, Q5 10.13 vs Q1 0.46 | 7.32e-03 |
| 15 | bb_20_20_bandwidth | numeric | Q5-Q1 +9.67 (rho +0.080) | n 1121, Q5 10.13 vs Q1 0.46 | 7.30e-03 |
| 16 | gold_silver_ratio | numeric | Q5-Q1 +8.93 (rho +0.148) | n 1121, Q5 12.46 vs Q1 3.53 | 6.52e-07 |
| 17 | ppo | numeric | Q5-Q1 -8.12 (rho -0.085) | n 1121, Q5 0.33 vs Q1 8.45 | 4.59e-03 |
| 18 | ppo_signal | numeric | Q5-Q1 -7.78 (rho -0.080) | n 1121, Q5 0.44 vs Q1 8.22 | 7.20e-03 |
| 19 | bb_10_20_bandwidth | numeric | Q5-Q1 +7.48 (rho +0.084) | n 1121, Q5 9.69 vs Q1 2.21 | 4.68e-03 |
| 20 | rsi_2 | numeric | Q5-Q1 -7.28 (rho -0.152) | n 1121, Q5 1.02 vs Q1 8.30 | 3.35e-07 |
| 21 | macd_12_26_9_line | numeric | Q5-Q1 -7.27 (rho -0.090) | n 1121, Q5 0.58 vs Q1 7.86 | 2.70e-03 |
| 22 | macd_12_26_9_signal | numeric | Q5-Q1 -7.15 (rho -0.084) | n 1121, Q5 0.69 vs Q1 7.84 | 4.96e-03 |
| 23 | days_to_cover | numeric | Q5-Q1 -7.12 (rho -0.127) | n 1118, Q5 1.63 vs Q1 8.75 | 2.02e-05 |
| 24 | days_since_last_earnings | numeric | Q5-Q1 +6.87 (rho +0.089) | n 1104, Q5 8.22 vs Q1 1.35 | 3.17e-03 |
| 25 | macd_8_21_5_line | numeric | Q5-Q1 -6.78 (rho -0.092) | n 1121, Q5 0.94 vs Q1 7.72 | 2.03e-03 |
| 26 | macd_8_21_5_signal | numeric | Q5-Q1 -6.61 (rho -0.078) | n 1121, Q5 1.01 vs Q1 7.62 | 9.42e-03 |
| 27 | cot_dxy_commercials_net_pct | numeric | Q5-Q1 +5.58 (rho +0.080) | n 1121, Q5 8.19 vs Q1 2.61 | 7.52e-03 |
| 28 | below_sma_50 | bool | +5.07 (T 4.49 vs F -0.58) | n 974/147, WR 0.361 vs 0.259 | 1.12e-08 |
| 29 | price_above_sma_50 | bool | -5.07 (T -0.58 vs F 4.49) | n 147/974, WR 0.259 vs 0.361 | 1.12e-08 |
| 30 | rsi_2_overbought | bool | -4.96 (T 2.59 vs F 7.55) | n 841/280, WR 0.328 vs 0.407 | 4.44e-03 |
| 31 | bb_10_20_squeeze | bool | -4.90 (T 1.05 vs F 5.95) | n 485/636, WR 0.266 vs 0.410 | 2.40e-06 |
| 32 | smc_inverse_fvg_bullish | bool | -4.57 (T 2.17 vs F 6.74) | n 714/407, WR 0.328 vs 0.383 | 6.05e-04 |
| 33 | cpr_narrow | bool | +4.53 (T 4.37 vs F -0.16) | n 987/134, WR 0.362 vs 0.246 | 1.28e-06 |
| 34 | is_halloween_period | bool | +4.48 (T 6.34 vs F 1.87) | n 491/630, WR 0.381 vs 0.322 | 2.05e-04 |
| 35 | is_summer_period | bool | -4.48 (T 1.87 vs F 6.34) | n 630/491, WR 0.322 vs 0.381 | 2.05e-04 |
| 36 | risk_on_regime_bond_signal_strong | bool | -4.47 (T -0.04 vs F 4.43) | n 150/971, WR 0.267 vs 0.360 | 1.73e-06 |
| 37 | bb_10_20_pctb | numeric | Q5-Q1 -4.45 (rho -0.105) | n 1121, Q5 1.99 vs Q1 6.44 | 4.28e-04 |
| 38 | cot_copper_commercials_pctile_3y | numeric | Q5-Q1 +4.36 (rho +0.142) | n 1121, Q5 3.15 vs Q1 -1.22 | 1.95e-06 |
| 39 | ichi_below_cloud | bool | +4.31 (T 4.51 vs F 0.20) | n 944/177, WR 0.361 vs 0.277 | 1.68e-06 |
| 40 | stochrsi_overbought | bool | -4.20 (T 1.84 vs F 6.04) | n 590/531, WR 0.314 vs 0.386 | 2.52e-04 |
