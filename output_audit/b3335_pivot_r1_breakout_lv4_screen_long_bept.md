# COMPANION-SIGNAL SCREEN - pivot_r1_breakout (exact names)

exit breakeven_plus_trail; window is; 4288 unique entries; 314 signals tested; BH-FDR q=0.05 threshold p<=0.026274; 165 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | vix_term_backwardation | bool | +13.68 (T 15.59 vs F 1.91) | n 676/3612, WR 0.596 vs 0.279 | 5.06e-32 |
| 2 | vix_term_contango | bool | -13.68 (T 1.91 vs F 15.59) | n 3612/676, WR 0.279 vs 0.596 | 5.06e-32 |
| 3 | xs_max_anomaly | numeric | Q5-Q1 +12.09 (rho +0.205) | n 4255, Q5 12.62 vs Q1 0.53 | 1.38e-41 |
| 4 | short_interest_observations | numeric | Q5-Q1 +11.52 (rho +0.140) | n 4274, Q5 11.36 vs Q1 -0.16 | 4.73e-20 |
| 5 | gold_silver_20d_pct_change | numeric | Q5-Q1 +11.13 (rho +0.168) | n 4288, Q5 12.77 vs Q1 1.64 | 1.68e-28 |
| 6 | atr_pct | numeric | Q5-Q1 +11.04 (rho +0.147) | n 4288, Q5 11.98 vs Q1 0.95 | 4.89e-22 |
| 7 | gap_dn_2pct | bool | +10.60 (T 14.39 vs F 3.80) | n 108/4180, WR 0.565 vs 0.323 | 4.63e-05 |
| 8 | gold_silver_ratio | numeric | Q5-Q1 +10.11 (rho +0.158) | n 4288, Q5 12.22 vs Q1 2.11 | 2.51e-25 |
| 9 | vix_percentile | numeric | Q5-Q1 +10.00 (rho +0.126) | n 4288, Q5 12.64 vs Q1 2.64 | 1.39e-16 |
| 10 | vix_vix3m_ratio | numeric | Q5-Q1 +9.74 (rho +0.151) | n 4288, Q5 12.86 vs Q1 3.12 | 2.05e-23 |
| 11 | house_cluster_sell | bool | +8.94 (T 12.58 vs F 3.64) | n 218/4047, WR 0.472 vs 0.322 | 2.45e-07 |
| 12 | vix_today | numeric | Q5-Q1 +8.75 (rho +0.154) | n 4288, Q5 11.90 vs Q1 3.15 | 4.46e-24 |
| 13 | vix_value | numeric | Q5-Q1 +8.75 (rho +0.154) | n 4288, Q5 11.90 vs Q1 3.15 | 4.46e-24 |
| 14 | po3_accum_range_pct | numeric | Q5-Q1 +8.52 (rho +0.142) | n 4288, Q5 10.03 vs Q1 1.51 | 7.12e-21 |
| 15 | gap_dn_1_5pct | bool | +8.42 (T 12.13 vs F 3.71) | n 179/4109, WR 0.564 vs 0.319 | 3.09e-06 |
| 16 | vol_spike_2x_on_up_day_recent_3d | bool | +7.54 (T 11.37 vs F 3.83) | n 132/4156, WR 0.455 vs 0.325 | 2.96e-03 |
| 17 | cot_dxy_mmoney_pctile_3y | numeric | Q5-Q1 +7.09 (rho +0.150) | n 4288, Q5 7.52 vs Q1 0.43 | 5.12e-23 |
| 18 | bond_equity_ratio | numeric | Q5-Q1 -7.01 (rho -0.067) | n 4288, Q5 -0.34 vs Q1 6.67 | 1.12e-05 |
| 19 | dxy_proxy_close | numeric | Q5-Q1 +6.77 (rho +0.117) | n 4288, Q5 5.67 vs Q1 -1.10 | 1.32e-14 |
| 20 | cot_rut_mmoney_pctile_3y | numeric | Q5-Q1 +6.60 (rho +0.165) | n 4288, Q5 6.14 vs Q1 -0.45 | 1.24e-27 |
| 21 | macd_8_21_5_line | numeric | Q5-Q1 -6.54 (rho -0.101) | n 4288, Q5 1.97 vs Q1 8.51 | 2.71e-11 |
| 22 | xs_beta_decile | numeric | Q5-Q1 +6.54 (rho +0.082) | n 4255, Q5 7.24 vs Q1 0.70 | 7.12e-08 |
| 23 | macd_12_26_9_signal | numeric | Q5-Q1 -6.45 (rho -0.090) | n 4288, Q5 1.49 vs Q1 7.94 | 4.05e-09 |
| 24 | macd_12_26_9_bearish | bool | +6.27 (T 9.37 vs F 3.10) | n 660/3628, WR 0.435 vs 0.310 | 1.73e-10 |
| 25 | macd_12_26_9_bullish | bool | -6.27 (T 3.10 vs F 9.37) | n 3628/660, WR 0.310 vs 0.435 | 1.73e-10 |
| 26 | macd_12_26_9_line | numeric | Q5-Q1 -6.23 (rho -0.101) | n 4288, Q5 1.74 vs Q1 7.96 | 4.13e-11 |
| 27 | days_since_last_earnings | numeric | Q5-Q1 +6.21 (rho +0.057) | n 4236, Q5 8.70 vs Q1 2.50 | 2.09e-04 |
| 28 | cot_copper_commercials_pctile_3y | numeric | Q5-Q1 +6.04 (rho +0.136) | n 4288, Q5 5.92 vs Q1 -0.12 | 4.04e-19 |
| 29 | xs_beta | numeric | Q5-Q1 +6.04 (rho +0.083) | n 4255, Q5 7.04 vs Q1 1.00 | 5.65e-08 |
| 30 | cot_rut_commercials_net_pct | numeric | Q5-Q1 -5.80 (rho -0.048) | n 4288, Q5 -0.61 vs Q1 5.18 | 1.53e-03 |
| 31 | xs_max_anomaly_decile | numeric | Q5-Q1 +5.80 (rho +0.090) | n 4255, Q5 7.10 vs Q1 1.31 | 4.72e-09 |
| 32 | news_uses_polygon_score | bool | +5.79 (T 8.88 vs F 3.09) | n 723/3565, WR 0.430 vs 0.309 | 1.15e-10 |
| 33 | macd_8_21_5_signal | numeric | Q5-Q1 -5.70 (rho -0.086) | n 4288, Q5 2.13 vs Q1 7.83 | 1.63e-08 |
| 34 | macd_8_21_5_bearish | bool | +5.66 (T 8.93 vs F 3.27) | n 599/3689, WR 0.431 vs 0.313 | 2.09e-08 |
| 35 | macd_8_21_5_bullish | bool | -5.66 (T 3.27 vs F 8.93) | n 3689/599, WR 0.313 vs 0.431 | 2.09e-08 |
| 36 | house_cluster_buy | bool | +5.50 (T 9.33 vs F 3.83) | n 202/4063, WR 0.416 vs 0.325 | 8.17e-04 |
| 37 | otc_volume_recent | numeric | Q5-Q1 +5.42 (rho +0.090) | n 4092, Q5 7.80 vs Q1 2.38 | 9.63e-09 |
| 38 | weekly_momentum_4w | numeric | Q5-Q1 -5.41 (rho -0.061) | n 4286, Q5 2.49 vs Q1 7.90 | 5.62e-05 |
| 39 | xs_high_beta_decile | bool | +4.47 (T 7.17 vs F 2.70) | n 1298/2957, WR 0.428 vs 0.285 | 7.19e-11 |
| 40 | xs_low_beta_bottom_quintile | bool | +4.47 (T 7.17 vs F 2.70) | n 1298/2957, WR 0.428 vs 0.285 | 7.19e-11 |
