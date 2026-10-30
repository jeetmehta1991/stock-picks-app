# COMPANION-SIGNAL SCREEN - pivot_r1_breakout (exact names)

exit breakeven_plus_trail; basis net; window is; 4288 unique entries; 314 signals tested; BH-FDR q=0.05 threshold p<=0.026274; 165 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | vix_term_backwardation | bool | +13.68 (T 15.39 vs F 1.71) | n 676/3612, WR 0.589 vs 0.277 | 5.06e-32 |
| 2 | vix_term_contango | bool | -13.68 (T 1.71 vs F 15.39) | n 3612/676, WR 0.277 vs 0.589 | 5.06e-32 |
| 3 | xs_max_anomaly | numeric | Q5-Q1 +12.09 (rho +0.205) | n 4255, Q5 12.42 vs Q1 0.33 | 1.38e-41 |
| 4 | short_interest_observations | numeric | Q5-Q1 +11.52 (rho +0.140) | n 4274, Q5 11.16 vs Q1 -0.36 | 4.73e-20 |
| 5 | gold_silver_20d_pct_change | numeric | Q5-Q1 +11.13 (rho +0.168) | n 4288, Q5 12.57 vs Q1 1.44 | 1.68e-28 |
| 6 | atr_pct | numeric | Q5-Q1 +11.04 (rho +0.147) | n 4288, Q5 11.78 vs Q1 0.75 | 4.89e-22 |
| 7 | gap_dn_2pct | bool | +10.60 (T 14.19 vs F 3.60) | n 108/4180, WR 0.556 vs 0.320 | 4.63e-05 |
| 8 | gold_silver_ratio | numeric | Q5-Q1 +10.11 (rho +0.158) | n 4288, Q5 12.02 vs Q1 1.91 | 2.51e-25 |
| 9 | vix_percentile | numeric | Q5-Q1 +10.00 (rho +0.126) | n 4288, Q5 12.44 vs Q1 2.44 | 1.39e-16 |
| 10 | vix_vix3m_ratio | numeric | Q5-Q1 +9.74 (rho +0.151) | n 4288, Q5 12.66 vs Q1 2.92 | 2.05e-23 |
| 11 | house_cluster_sell | bool | +8.94 (T 12.38 vs F 3.44) | n 218/4047, WR 0.472 vs 0.319 | 2.45e-07 |
| 12 | vix_today | numeric | Q5-Q1 +8.75 (rho +0.154) | n 4288, Q5 11.70 vs Q1 2.95 | 4.46e-24 |
| 13 | vix_value | numeric | Q5-Q1 +8.75 (rho +0.154) | n 4288, Q5 11.70 vs Q1 2.95 | 4.46e-24 |
| 14 | po3_accum_range_pct | numeric | Q5-Q1 +8.52 (rho +0.142) | n 4288, Q5 9.83 vs Q1 1.31 | 7.12e-21 |
| 15 | gap_dn_1_5pct | bool | +8.42 (T 11.93 vs F 3.51) | n 179/4109, WR 0.559 vs 0.316 | 3.09e-06 |
| 16 | vol_spike_2x_on_up_day_recent_3d | bool | +7.54 (T 11.17 vs F 3.63) | n 132/4156, WR 0.439 vs 0.322 | 2.96e-03 |
| 17 | cot_dxy_mmoney_pctile_3y | numeric | Q5-Q1 +7.09 (rho +0.150) | n 4288, Q5 7.32 vs Q1 0.23 | 5.12e-23 |
| 18 | bond_equity_ratio | numeric | Q5-Q1 -7.01 (rho -0.067) | n 4288, Q5 -0.54 vs Q1 6.47 | 1.12e-05 |
| 19 | dxy_proxy_close | numeric | Q5-Q1 +6.77 (rho +0.117) | n 4288, Q5 5.47 vs Q1 -1.30 | 1.32e-14 |
| 20 | cot_rut_mmoney_pctile_3y | numeric | Q5-Q1 +6.60 (rho +0.165) | n 4288, Q5 5.94 vs Q1 -0.65 | 1.24e-27 |
| 21 | macd_8_21_5_line | numeric | Q5-Q1 -6.54 (rho -0.101) | n 4288, Q5 1.77 vs Q1 8.31 | 2.71e-11 |
| 22 | xs_beta_decile | numeric | Q5-Q1 +6.54 (rho +0.082) | n 4255, Q5 7.04 vs Q1 0.50 | 7.12e-08 |
| 23 | macd_12_26_9_signal | numeric | Q5-Q1 -6.45 (rho -0.090) | n 4288, Q5 1.29 vs Q1 7.74 | 4.05e-09 |
| 24 | macd_12_26_9_bearish | bool | +6.27 (T 9.17 vs F 2.90) | n 660/3628, WR 0.427 vs 0.307 | 1.73e-10 |
| 25 | macd_12_26_9_bullish | bool | -6.27 (T 2.90 vs F 9.17) | n 3628/660, WR 0.307 vs 0.427 | 1.73e-10 |
| 26 | macd_12_26_9_line | numeric | Q5-Q1 -6.23 (rho -0.101) | n 4288, Q5 1.54 vs Q1 7.76 | 4.13e-11 |
| 27 | days_since_last_earnings | numeric | Q5-Q1 +6.21 (rho +0.057) | n 4236, Q5 8.50 vs Q1 2.30 | 2.09e-04 |
| 28 | cot_copper_commercials_pctile_3y | numeric | Q5-Q1 +6.04 (rho +0.136) | n 4288, Q5 5.72 vs Q1 -0.32 | 4.04e-19 |
| 29 | xs_beta | numeric | Q5-Q1 +6.04 (rho +0.083) | n 4255, Q5 6.84 vs Q1 0.80 | 5.65e-08 |
| 30 | cot_rut_commercials_net_pct | numeric | Q5-Q1 -5.80 (rho -0.048) | n 4288, Q5 -0.81 vs Q1 4.98 | 1.53e-03 |
| 31 | xs_max_anomaly_decile | numeric | Q5-Q1 +5.80 (rho +0.090) | n 4255, Q5 6.90 vs Q1 1.11 | 4.72e-09 |
| 32 | news_uses_polygon_score | bool | +5.79 (T 8.68 vs F 2.89) | n 723/3565, WR 0.423 vs 0.306 | 1.15e-10 |
| 33 | macd_8_21_5_signal | numeric | Q5-Q1 -5.70 (rho -0.086) | n 4288, Q5 1.93 vs Q1 7.63 | 1.63e-08 |
| 34 | macd_8_21_5_bearish | bool | +5.66 (T 8.73 vs F 3.07) | n 599/3689, WR 0.426 vs 0.310 | 2.09e-08 |
| 35 | macd_8_21_5_bullish | bool | -5.66 (T 3.07 vs F 8.73) | n 3689/599, WR 0.310 vs 0.426 | 2.09e-08 |
| 36 | house_cluster_buy | bool | +5.50 (T 9.13 vs F 3.63) | n 202/4063, WR 0.416 vs 0.322 | 8.17e-04 |
| 37 | otc_volume_recent | numeric | Q5-Q1 +5.42 (rho +0.090) | n 4092, Q5 7.60 vs Q1 2.18 | 9.63e-09 |
| 38 | weekly_momentum_4w | numeric | Q5-Q1 -5.41 (rho -0.061) | n 4286, Q5 2.29 vs Q1 7.70 | 5.62e-05 |
| 39 | xs_high_beta_decile | bool | +4.47 (T 6.97 vs F 2.50) | n 1298/2957, WR 0.425 vs 0.282 | 7.19e-11 |
| 40 | xs_low_beta_bottom_quintile | bool | +4.47 (T 6.97 vs F 2.50) | n 1298/2957, WR 0.425 vs 0.282 | 7.19e-11 |
