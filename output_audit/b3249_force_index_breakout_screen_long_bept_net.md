# COMPANION-SIGNAL SCREEN - force_index_breakout (exact names)

exit breakeven_plus_trail; basis net; window is; 952 unique entries; 430 signals tested; BH-FDR q=0.05 threshold p<=0.012907; 111 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | vix_term_backwardation | bool | +12.88 (T 14.13 vs F 1.25) | n 119/833, WR 0.580 vs 0.261 | 4.59e-08 |
| 2 | vix_term_contango | bool | -12.88 (T 1.25 vs F 14.13) | n 833/119, WR 0.261 vs 0.580 | 4.59e-08 |
| 3 | cot_sp500_commercials_net_pct | numeric | Q5-Q1 -9.93 (rho -0.167) | n 952, Q5 -0.06 vs Q1 9.87 | 2.27e-07 |
| 4 | pct_from_avwap_20low | numeric | Q5-Q1 +9.65 (rho +0.135) | n 941, Q5 10.44 vs Q1 0.80 | 3.32e-05 |
| 5 | gold_silver_20d_pct_change | numeric | Q5-Q1 +9.64 (rho +0.155) | n 952, Q5 9.86 vs Q1 0.22 | 1.63e-06 |
| 6 | sector_strongest_rs | numeric | Q5-Q1 -9.52 (rho -0.205) | n 952, Q5 -0.59 vs Q1 8.94 | 1.74e-10 |
| 7 | cot_sp500_commercials_pctile_3y | numeric | Q5-Q1 -9.49 (rho -0.168) | n 952, Q5 -0.29 vs Q1 9.20 | 1.85e-07 |
| 8 | xs_max_anomaly | numeric | Q5-Q1 +9.49 (rho +0.124) | n 946, Q5 9.86 vs Q1 0.37 | 1.30e-04 |
| 9 | pct_from_avwap_20high | numeric | Q5-Q1 +9.40 (rho +0.208) | n 885, Q5 9.46 vs Q1 0.06 | 4.28e-10 |
| 10 | po3_accum_range_pct | numeric | Q5-Q1 +9.34 (rho +0.114) | n 952, Q5 10.64 vs Q1 1.29 | 4.35e-04 |
| 11 | atr_pct | numeric | Q5-Q1 +8.89 (rho +0.093) | n 952, Q5 10.33 vs Q1 1.44 | 4.16e-03 |
| 12 | short_interest_observations | numeric | Q5-Q1 +8.78 (rho +0.143) | n 947, Q5 7.98 vs Q1 -0.81 | 9.88e-06 |
| 13 | vix_vix3m_ratio | numeric | Q5-Q1 +8.07 (rho +0.146) | n 952, Q5 10.47 vs Q1 2.39 | 5.67e-06 |
| 14 | bb_20_15_reclaim_from_lower_recent_3d | bool | +8.01 (T 9.29 vs F 1.29) | n 187/765, WR 0.487 vs 0.255 | 9.40e-07 |
| 15 | pct_from_avwap_50low | numeric | Q5-Q1 +7.97 (rho +0.090) | n 945, Q5 8.82 vs Q1 0.86 | 5.80e-03 |
| 16 | dxy_proxy_close | numeric | Q5-Q1 +7.95 (rho +0.149) | n 952, Q5 6.63 vs Q1 -1.32 | 3.71e-06 |
| 17 | bb_10_20_bandwidth | numeric | Q5-Q1 +7.90 (rho +0.090) | n 952, Q5 9.23 vs Q1 1.33 | 5.63e-03 |
| 18 | bond_equity_ratio | numeric | Q5-Q1 -7.51 (rho -0.081) | n 952, Q5 -0.35 vs Q1 7.16 | 1.29e-02 |
| 19 | squeeze_momentum | numeric | Q5-Q1 +6.96 (rho +0.197) | n 952, Q5 6.86 vs Q1 -0.09 | 8.94e-10 |
| 20 | gold_silver_ratio | numeric | Q5-Q1 +6.79 (rho +0.105) | n 952, Q5 9.27 vs Q1 2.48 | 1.17e-03 |
| 21 | vol_ratio_20d | numeric | Q5-Q1 +6.71 (rho +0.117) | n 952, Q5 7.43 vs Q1 0.73 | 2.92e-04 |
| 22 | rsi_9_cross_up_oversold_recent_3d | bool | +6.45 (T 8.39 vs F 1.94) | n 136/816, WR 0.463 vs 0.273 | 6.38e-04 |
| 23 | vix_percentile | numeric | Q5-Q1 +6.43 (rho +0.099) | n 952, Q5 8.64 vs Q1 2.20 | 2.30e-03 |
| 24 | ppo | numeric | Q5-Q1 -6.40 (rho -0.089) | n 952, Q5 0.61 vs Q1 7.02 | 6.10e-03 |
| 25 | near_avwap_20low_atr_15x | bool | -6.38 (T 1.47 vs F 7.85) | n 734/207, WR 0.252 vs 0.469 | 1.10e-05 |
| 26 | vix_today | numeric | Q5-Q1 +6.27 (rho +0.142) | n 952, Q5 9.18 vs Q1 2.92 | 1.04e-05 |
| 27 | vix_value | numeric | Q5-Q1 +6.27 (rho +0.142) | n 952, Q5 9.18 vs Q1 2.92 | 1.04e-05 |
| 28 | ppo_signal | numeric | Q5-Q1 -5.92 (rho -0.094) | n 952, Q5 0.46 vs Q1 6.38 | 3.79e-03 |
| 29 | cpr_width | numeric | Q5-Q1 +5.88 (rho +0.130) | n 952, Q5 8.45 vs Q1 2.57 | 5.89e-05 |
| 30 | cot_rut_commercials_net_pct | numeric | Q5-Q1 -5.79 (rho -0.158) | n 952, Q5 0.88 vs Q1 6.67 | 9.14e-07 |
| 31 | cot_copper_commercials_pctile_3y | numeric | Q5-Q1 +5.78 (rho +0.177) | n 952, Q5 4.99 vs Q1 -0.79 | 4.08e-08 |
| 32 | vol_spike_15x | bool | +5.72 (T 7.58 vs F 1.85) | n 167/785, WR 0.407 vs 0.278 | 3.93e-03 |
| 33 | macd_12_26_9_line | numeric | Q5-Q1 -5.54 (rho -0.099) | n 952, Q5 0.68 vs Q1 6.22 | 2.34e-03 |
| 34 | macd_8_21_5_signal | numeric | Q5-Q1 -5.44 (rho -0.082) | n 952, Q5 0.51 vs Q1 5.95 | 1.11e-02 |
| 35 | atr | numeric | Q5-Q1 +5.40 (rho +0.083) | n 952, Q5 7.72 vs Q1 2.32 | 1.04e-02 |
| 36 | atr_14 | numeric | Q5-Q1 +5.40 (rho +0.083) | n 952, Q5 7.72 vs Q1 2.32 | 1.04e-02 |
| 37 | macd_12_26_9_signal | numeric | Q5-Q1 -5.39 (rho -0.106) | n 952, Q5 0.28 vs Q1 5.67 | 1.09e-03 |
| 38 | chandelier_short_flip_up | bool | +5.35 (T 6.95 vs F 1.61) | n 223/729, WR 0.422 vs 0.263 | 5.87e-05 |
| 39 | ao | numeric | Q5-Q1 -5.22 (rho -0.082) | n 952, Q5 1.20 vs Q1 6.42 | 1.17e-02 |
| 40 | vol_spike_12x | bool | +4.95 (T 6.34 vs F 1.39) | n 282/670, WR 0.376 vs 0.269 | 4.33e-04 |
