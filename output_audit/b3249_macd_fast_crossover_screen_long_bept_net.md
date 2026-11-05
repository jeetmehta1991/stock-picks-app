# COMPANION-SIGNAL SCREEN - macd_fast_crossover (exact names)

exit breakeven_plus_trail; basis net; window is; 1534 unique entries; 461 signals tested; BH-FDR q=0.05 threshold p<=0.010954; 101 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | xs_max_anomaly | numeric | Q5-Q1 +13.06 (rho +0.186) | n 1520, Q5 13.89 vs Q1 0.83 | 2.55e-13 |
| 2 | atr_pct | numeric | Q5-Q1 +12.25 (rho +0.132) | n 1534, Q5 13.01 vs Q1 0.76 | 2.14e-07 |
| 3 | po3_accum_range_pct | numeric | Q5-Q1 +12.12 (rho +0.140) | n 1534, Q5 13.19 vs Q1 1.07 | 3.79e-08 |
| 4 | vix_term_backwardation | bool | +11.59 (T 13.82 vs F 2.23) | n 207/1327, WR 0.594 vs 0.295 | 8.23e-11 |
| 5 | vix_term_contango | bool | -11.59 (T 2.23 vs F 13.82) | n 1327/207, WR 0.295 vs 0.594 | 8.23e-11 |
| 6 | bb_10_20_bandwidth | numeric | Q5-Q1 +11.20 (rho +0.106) | n 1534, Q5 11.88 vs Q1 0.67 | 3.16e-05 |
| 7 | ppo_signal | numeric | Q5-Q1 -10.96 (rho -0.159) | n 1534, Q5 0.60 vs Q1 11.55 | 3.92e-10 |
| 8 | xs_max_anomaly_decile | numeric | Q5-Q1 +10.89 (rho +0.108) | n 1520, Q5 11.64 vs Q1 0.75 | 2.64e-05 |
| 9 | vol_spike_15x | bool | +10.56 (T 13.38 vs F 2.82) | n 142/1392, WR 0.472 vs 0.322 | 1.37e-03 |
| 10 | bb_20_15_bandwidth | numeric | Q5-Q1 +9.07 (rho +0.066) | n 1534, Q5 10.97 vs Q1 1.91 | 9.61e-03 |
| 11 | bb_20_20_bandwidth | numeric | Q5-Q1 +9.07 (rho +0.066) | n 1534, Q5 10.97 vs Q1 1.91 | 9.61e-03 |
| 12 | ppo | numeric | Q5-Q1 -8.90 (rho -0.130) | n 1534, Q5 1.64 vs Q1 10.53 | 3.34e-07 |
| 13 | cot_sp500_commercials_pctile_3y | numeric | Q5-Q1 -8.36 (rho -0.092) | n 1534, Q5 1.57 vs Q1 9.93 | 3.10e-04 |
| 14 | short_interest_observations | numeric | Q5-Q1 +8.32 (rho +0.114) | n 1528, Q5 7.78 vs Q1 -0.54 | 7.26e-06 |
| 15 | cmf | numeric | Q5-Q1 +7.62 (rho +0.097) | n 1534, Q5 8.84 vs Q1 1.22 | 1.34e-04 |
| 16 | dxy_20d_pct_change | numeric | Q5-Q1 -7.33 (rho -0.127) | n 1534, Q5 0.03 vs Q1 7.36 | 6.01e-07 |
| 17 | vix_today | numeric | Q5-Q1 +7.08 (rho +0.133) | n 1534, Q5 11.32 vs Q1 4.24 | 1.69e-07 |
| 18 | vix_value | numeric | Q5-Q1 +7.08 (rho +0.133) | n 1534, Q5 11.32 vs Q1 4.24 | 1.69e-07 |
| 19 | vp_close_near_poc_pct | numeric | Q5-Q1 +7.07 (rho +0.100) | n 1534, Q5 8.69 vs Q1 1.62 | 9.18e-05 |
| 20 | naked_poc_nearest_distance_pct | numeric | Q5-Q1 +6.56 (rho +0.071) | n 1523, Q5 8.36 vs Q1 1.80 | 5.33e-03 |
| 21 | days_since_last_earnings | numeric | Q5-Q1 +6.52 (rho +0.088) | n 1509, Q5 7.76 vs Q1 1.24 | 6.30e-04 |
| 22 | vix_vix3m_ratio | numeric | Q5-Q1 +6.52 (rho +0.094) | n 1534, Q5 10.64 vs Q1 4.12 | 2.10e-04 |
| 23 | xs_avoid_high_max | bool | -6.20 (T 2.14 vs F 8.35) | n 1106/414, WR 0.288 vs 0.461 | 1.13e-04 |
| 24 | ema_20_50_bearish | bool | +6.10 (T 4.33 vs F -1.76) | n 1399/135, WR 0.351 vs 0.178 | 1.64e-12 |
| 25 | ema_20_50_bullish | bool | -6.10 (T -1.76 vs F 4.33) | n 135/1399, WR 0.178 vs 0.351 | 1.64e-12 |
| 26 | chandelier_short_flip_up | bool | +6.05 (T 9.32 vs F 3.27) | n 133/1401, WR 0.466 vs 0.323 | 8.14e-04 |
| 27 | vol_spike_12x | bool | +5.43 (T 8.25 vs F 2.82) | n 276/1258, WR 0.417 vs 0.318 | 3.03e-03 |
| 28 | squeeze_fire_up | bool | +5.20 (T 8.60 vs F 3.40) | n 117/1417, WR 0.453 vs 0.326 | 9.98e-03 |
| 29 | sector_strongest_rs | numeric | Q5-Q1 -5.20 (rho -0.106) | n 1534, Q5 1.10 vs Q1 6.30 | 3.21e-05 |
| 30 | vix_percentile | numeric | Q5-Q1 +5.07 (rho +0.091) | n 1534, Q5 9.47 vs Q1 4.40 | 3.69e-04 |
| 31 | near_r1_wide | bool | -4.80 (T 2.14 vs F 6.95) | n 1006/528, WR 0.281 vs 0.439 | 2.04e-04 |
| 32 | cot_copper_commercials_pctile_3y | numeric | Q5-Q1 +4.67 (rho +0.095) | n 1534, Q5 5.72 vs Q1 1.05 | 1.89e-04 |
| 33 | cmf_negative | bool | -4.64 (T 2.01 vs F 6.65) | n 943/591, WR 0.310 vs 0.377 | 1.01e-04 |
| 34 | sma_20_50_bullish | bool | -4.56 (T 0.04 vs F 4.61) | n 272/1262, WR 0.210 vs 0.363 | 3.22e-05 |
| 35 | double_bottom_detected | bool | -4.55 (T -0.22 vs F 4.33) | n 180/1354, WR 0.239 vs 0.349 | 2.72e-08 |
| 36 | gold_silver_ratio | numeric | Q5-Q1 +4.36 (rho +0.066) | n 1534, Q5 8.33 vs Q1 3.97 | 1.02e-02 |
| 37 | force_index_positive | bool | +4.21 (T 6.54 vs F 2.33) | n 536/998, WR 0.386 vs 0.309 | 9.10e-04 |
| 38 | bb_20_20_reclaim_from_lower_recent_3d | bool | +4.18 (T 7.38 vs F 3.20) | n 218/1316, WR 0.408 vs 0.324 | 3.30e-03 |
| 39 | near_r2_wide | bool | -4.13 (T 2.12 vs F 6.25) | n 910/624, WR 0.290 vs 0.402 | 2.55e-04 |
| 40 | xs_low_beta_decile | bool | -4.09 (T 0.34 vs F 4.43) | n 222/1298, WR 0.180 vs 0.362 | 1.11e-06 |
