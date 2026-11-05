# COMPANION-SIGNAL SCREEN - r1_break_retest (exact names)

exit breakeven_plus_trail; basis net; window is; 1389 unique entries; 448 signals tested; BH-FDR q=0.05 threshold p<=0.0125; 112 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | vix_term_backwardation | bool | +14.37 (T 16.89 vs F 2.51) | n 130/1259, WR 0.585 vs 0.304 | 2.14e-07 |
| 2 | vix_term_contango | bool | -14.37 (T 2.51 vs F 16.89) | n 1259/130, WR 0.304 vs 0.585 | 2.14e-07 |
| 3 | xs_max_anomaly | numeric | Q5-Q1 +12.18 (rho +0.138) | n 1373, Q5 12.66 vs Q1 0.48 | 2.59e-07 |
| 4 | atr_pct | numeric | Q5-Q1 +11.47 (rho +0.093) | n 1389, Q5 12.20 vs Q1 0.73 | 5.23e-04 |
| 5 | cot_dxy_mmoney_pctile_3y | numeric | Q5-Q1 +11.34 (rho +0.173) | n 1389, Q5 11.59 vs Q1 0.25 | 8.17e-11 |
| 6 | bb_20_15_bandwidth | numeric | Q5-Q1 +11.13 (rho +0.090) | n 1389, Q5 12.03 vs Q1 0.90 | 7.88e-04 |
| 7 | bb_20_20_bandwidth | numeric | Q5-Q1 +11.13 (rho +0.090) | n 1389, Q5 12.03 vs Q1 0.90 | 7.88e-04 |
| 8 | short_interest_observations | numeric | Q5-Q1 +9.29 (rho +0.113) | n 1384, Q5 9.12 vs Q1 -0.17 | 2.35e-05 |
| 9 | gold_silver_20d_pct_change | numeric | Q5-Q1 +9.23 (rho +0.198) | n 1389, Q5 11.03 vs Q1 1.80 | 8.52e-14 |
| 10 | ppo | numeric | Q5-Q1 -8.94 (rho -0.091) | n 1389, Q5 1.33 vs Q1 10.27 | 6.90e-04 |
| 11 | vix_percentile | numeric | Q5-Q1 +8.47 (rho +0.099) | n 1389, Q5 10.84 vs Q1 2.38 | 2.25e-04 |
| 12 | ppo_signal | numeric | Q5-Q1 -8.26 (rho -0.092) | n 1389, Q5 1.43 vs Q1 9.69 | 6.07e-04 |
| 13 | vix_vix3m_ratio | numeric | Q5-Q1 +8.03 (rho +0.164) | n 1389, Q5 11.50 vs Q1 3.48 | 7.04e-10 |
| 14 | gold_silver_ratio | numeric | Q5-Q1 +7.92 (rho +0.171) | n 1389, Q5 10.09 vs Q1 2.17 | 1.28e-10 |
| 15 | usd_weakening | bool | +7.59 (T 9.91 vs F 2.32) | n 282/1107, WR 0.433 vs 0.304 | 1.82e-06 |
| 16 | near_r2_wide | bool | -7.40 (T 2.89 vs F 10.29) | n 1207/182, WR 0.316 vs 0.423 | 1.19e-02 |
| 17 | cot_copper_commercials_pctile_3y | numeric | Q5-Q1 +7.30 (rho +0.220) | n 1389, Q5 6.68 vs Q1 -0.62 | 1.15e-16 |
| 18 | vix_today | numeric | Q5-Q1 +7.13 (rho +0.148) | n 1389, Q5 9.78 vs Q1 2.65 | 2.90e-08 |
| 19 | vix_value | numeric | Q5-Q1 +7.13 (rho +0.148) | n 1389, Q5 9.78 vs Q1 2.65 | 2.90e-08 |
| 20 | near_avwap_20low_atr_05x | bool | +6.59 (T 9.63 vs F 3.04) | n 165/1219, WR 0.455 vs 0.313 | 1.24e-02 |
| 21 | rsi_21 | numeric | Q5-Q1 -6.49 (rho -0.081) | n 1389, Q5 0.79 vs Q1 7.28 | 2.61e-03 |
| 22 | pct_change_20d | numeric | Q5-Q1 -6.45 (rho -0.073) | n 1389, Q5 3.39 vs Q1 9.84 | 6.68e-03 |
| 23 | cot_sp500_commercials_net_pct | numeric | Q5-Q1 +6.13 (rho +0.080) | n 1389, Q5 9.98 vs Q1 3.85 | 2.74e-03 |
| 24 | rsi_14 | numeric | Q5-Q1 -5.37 (rho -0.072) | n 1389, Q5 1.28 vs Q1 6.66 | 7.07e-03 |
| 25 | smc_choch_bearish | bool | +5.36 (T 8.75 vs F 3.39) | n 119/1268, WR 0.454 vs 0.319 | 7.50e-03 |
| 26 | trading_days_left_in_month | numeric | Q5-Q1 +4.82 (rho +0.091) | n 1389, Q5 6.12 vs Q1 1.30 | 6.82e-04 |
| 27 | rsi_9 | numeric | Q5-Q1 -4.71 (rho -0.076) | n 1389, Q5 2.00 vs Q1 6.71 | 4.69e-03 |
| 28 | monthly_momentum_6m | numeric | Q5-Q1 -4.64 (rho -0.084) | n 1368, Q5 2.67 vs Q1 7.31 | 1.89e-03 |
| 29 | trading_day_of_month | numeric | Q5-Q1 -4.50 (rho -0.100) | n 1389, Q5 1.14 vs Q1 5.64 | 1.81e-04 |
| 30 | smc_inverse_fvg_bullish | bool | -4.48 (T 3.10 vs F 7.58) | n 1153/234, WR 0.317 vs 0.397 | 4.90e-03 |
| 31 | bb_10_20_squeeze | bool | -4.36 (T 1.27 vs F 5.63) | n 565/824, WR 0.239 vs 0.393 | 3.39e-06 |
| 32 | sma_20_50_bullish | bool | -4.32 (T -0.09 vs F 4.23) | n 118/1270, WR 0.212 vs 0.342 | 7.98e-06 |
| 33 | macd_12_26_9_line | numeric | Q5-Q1 -4.24 (rho -0.072) | n 1389, Q5 2.83 vs Q1 7.07 | 7.05e-03 |
| 34 | stochrsi_overbought | bool | -4.21 (T 2.71 vs F 6.92) | n 1010/379, WR 0.305 vs 0.398 | 1.54e-03 |
| 35 | smc_inverse_fvg_bearish | bool | +4.06 (T 4.19 vs F 0.13) | n 1270/117, WR 0.340 vs 0.222 | 4.17e-05 |
| 36 | bb_20_20_touch_upper | bool | -4.01 (T 0.42 vs F 4.43) | n 197/1192, WR 0.269 vs 0.341 | 6.32e-06 |
| 37 | vix_band_mid | bool | -4.00 (T 0.70 vs F 4.70) | n 292/1097, WR 0.301 vs 0.338 | 2.49e-06 |
| 38 | days_to_cover | numeric | Q5-Q1 -3.99 (rho -0.090) | n 1384, Q5 3.22 vs Q1 7.21 | 7.52e-04 |
| 39 | ichi_above_cloud | bool | -3.98 (T 0.38 vs F 4.36) | n 174/1214, WR 0.230 vs 0.345 | 4.59e-06 |
| 40 | ichi_above_cloud_break_recent_5d | bool | -3.95 (T 0.23 vs F 4.18) | n 113/1275, WR 0.265 vs 0.336 | 8.95e-06 |
