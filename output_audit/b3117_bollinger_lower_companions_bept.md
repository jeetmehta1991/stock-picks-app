# COMPANION-SIGNAL SCREEN - bollinger_lowerfamily

exit breakeven_plus_trail; window is; 1192 unique entries; 535 signals tested; BH-FDR q=0.05 threshold p<=0.021495; 230 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | vix_term_backwardation | bool | +8.58 (T 9.23 vs F 0.65) | n 140/1052, WR 0.479 vs 0.252 | 4.71e-08 |
| 2 | vix_term_contango | bool | -8.58 (T 0.65 vs F 9.23) | n 1052/140, WR 0.252 vs 0.479 | 4.71e-08 |
| 3 | cot_rut_commercials_net_pct | numeric | Q5-Q1 -6.99 (rho -0.180) | n 1192, Q5 -0.78 vs Q1 6.21 | 3.94e-10 |
| 4 | vix_percentile | numeric | Q5-Q1 +6.40 (rho +0.200) | n 1192, Q5 5.41 vs Q1 -0.99 | 3.21e-12 |
| 5 | vix_vix3m_ratio | numeric | Q5-Q1 +5.84 (rho +0.139) | n 1192, Q5 6.24 vs Q1 0.40 | 1.37e-06 |
| 6 | avwap_252low_reclaim_recent_3d | bool | +5.47 (T 6.75 vs F 1.28) | n 104/1035, WR 0.385 vs 0.278 | 2.32e-03 |
| 7 | price_above_ema_200_break_recent_5d | bool | +5.33 (T 6.35 vs F 1.02) | n 142/1050, WR 0.387 vs 0.264 | 2.45e-04 |
| 8 | rsi_14_cross_up_oversold_recent_3d | bool | +5.30 (T 6.51 vs F 1.21) | n 100/1092, WR 0.380 vs 0.269 | 1.89e-03 |
| 9 | ppo | numeric | Q5-Q1 -5.25 (rho -0.138) | n 1192, Q5 -0.05 vs Q1 5.20 | 1.78e-06 |
| 10 | defensive_leadership | bool | +5.20 (T 4.29 vs F -0.91) | n 588/604, WR 0.364 vs 0.195 | 1.90e-14 |
| 11 | bb_20_15_reclaim_from_lower_recent_3d | bool | +5.11 (T 5.55 vs F 0.43) | n 285/907, WR 0.312 vs 0.268 | 7.17e-07 |
| 12 | short_interest_observations | numeric | Q5-Q1 +4.99 (rho +0.130) | n 1183, Q5 4.99 vs Q1 -0.00 | 7.18e-06 |
| 13 | vix_today | numeric | Q5-Q1 +4.91 (rho +0.103) | n 1192, Q5 4.91 vs Q1 0.00 | 3.92e-04 |
| 14 | vix_value | numeric | Q5-Q1 +4.91 (rho +0.103) | n 1192, Q5 4.91 vs Q1 0.00 | 3.92e-04 |
| 15 | smc_fvg_retest_short_zone | bool | +4.70 (T 5.94 vs F 1.24) | n 105/1087, WR 0.362 vs 0.270 | 8.26e-03 |
| 16 | above_r1 | bool | +4.68 (T 5.77 vs F 1.09) | n 143/1049, WR 0.350 vs 0.269 | 1.37e-03 |
| 17 | pct_from_vwap | numeric | Q5-Q1 +4.67 (rho +0.119) | n 1192, Q5 5.39 vs Q1 0.72 | 4.05e-05 |
| 18 | above_prev_high | bool | +4.65 (T 5.65 vs F 1.00) | n 168/1024, WR 0.351 vs 0.267 | 3.60e-04 |
| 19 | macd_12_26_9_line | numeric | Q5-Q1 -4.59 (rho -0.127) | n 1192, Q5 -0.56 vs Q1 4.03 | 1.08e-05 |
| 20 | roc_12 | numeric | Q5-Q1 -4.59 (rho -0.098) | n 1192, Q5 -0.38 vs Q1 4.20 | 6.64e-04 |
| 21 | above_cam_r4 | bool | +4.54 (T 5.68 vs F 1.15) | n 134/1058, WR 0.351 vs 0.269 | 2.41e-03 |
| 22 | below_prev_high | bool | -4.40 (T 1.02 vs F 5.43) | n 1021/171, WR 0.267 vs 0.345 | 6.23e-04 |
| 23 | institutional_new_positions | numeric | Q5-Q1 +4.37 (rho +0.079) | n 1192, Q5 4.22 vs Q1 -0.15 | 6.20e-03 |
| 24 | pct_change_10d | numeric | Q5-Q1 -4.37 (rho -0.099) | n 1192, Q5 -0.37 vs Q1 4.00 | 6.26e-04 |
| 25 | ao | numeric | Q5-Q1 -4.25 (rho -0.112) | n 1192, Q5 -0.26 vs Q1 3.99 | 1.03e-04 |
| 26 | cot_ndx_commercials_net_pct | numeric | Q5-Q1 +4.18 (rho +0.115) | n 1192, Q5 5.34 vs Q1 1.16 | 6.57e-05 |
| 27 | rsi_9_cross_up_oversold_recent_3d | bool | +4.11 (T 4.67 vs F 0.56) | n 318/874, WR 0.318 vs 0.264 | 9.47e-06 |
| 28 | macd_8_21_5_signal | numeric | Q5-Q1 -4.07 (rho -0.115) | n 1192, Q5 -0.43 vs Q1 3.65 | 7.04e-05 |
| 29 | xs_momentum_top_decile | bool | +4.03 (T 5.02 vs F 0.99) | n 200/990, WR 0.360 vs 0.263 | 2.23e-03 |
| 30 | rsi_21_bullish | bool | -3.98 (T -0.28 vs F 3.70) | n 611/581, WR 0.250 vs 0.308 | 6.01e-09 |
| 31 | below_ema_50 | bool | +3.92 (T 3.64 vs F -0.28) | n 588/604, WR 0.318 vs 0.240 | 8.80e-09 |
| 32 | price_above_ema_50 | bool | -3.92 (T -0.28 vs F 3.64) | n 604/588, WR 0.240 vs 0.318 | 8.80e-09 |
| 33 | macd_8_21_5_line | numeric | Q5-Q1 -3.91 (rho -0.108) | n 1192, Q5 0.01 vs Q1 3.92 | 1.83e-04 |
| 34 | bb_10_20_reclaim_from_lower_recent_3d | bool | +3.91 (T 4.82 vs F 0.91) | n 228/964, WR 0.342 vs 0.263 | 1.28e-04 |
| 35 | pct_change_5d | numeric | Q5-Q1 -3.86 (rho -0.119) | n 1192, Q5 0.08 vs Q1 3.94 | 3.96e-05 |
| 36 | po3_bullish | bool | +3.82 (T 5.08 vs F 1.26) | n 125/1067, WR 0.432 vs 0.261 | 1.42e-02 |
| 37 | xs_momentum_12_1 | numeric | Q5-Q1 +3.78 (rho +0.102) | n 1190, Q5 4.31 vs Q1 0.53 | 4.06e-04 |
| 38 | vix_band_high | bool | +3.78 (T 3.54 vs F -0.24) | n 599/593, WR 0.349 vs 0.207 | 2.27e-08 |
| 39 | weekly_above_ema_10 | bool | -3.77 (T -0.22 vs F 3.55) | n 598/594, WR 0.246 vs 0.311 | 2.78e-08 |
| 40 | ichi_weekly_above_cloud | bool | +3.72 (T 4.09 vs F 0.37) | n 424/711, WR 0.311 vs 0.273 | 4.45e-06 |
