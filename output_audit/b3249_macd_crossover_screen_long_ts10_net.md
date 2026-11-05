# COMPANION-SIGNAL SCREEN - macd_crossover (exact names)

exit time_stop_10d; basis net; window is; 1121 unique entries; 429 signals tested; BH-FDR q=0.05 threshold p<=0.0039627; 34 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | three_white_soldiers | bool | -3.21 (T -2.44 vs F 0.78) | n 171/950, WR 0.404 vs 0.546 | 1.03e-05 |
| 2 | gold_silver_20d_pct_change | numeric | Q5-Q1 +3.16 (rho +0.168) | n 1121, Q5 2.67 vs Q1 -0.49 | 1.53e-08 |
| 3 | rsi_2 | numeric | Q5-Q1 -3.03 (rho -0.163) | n 1121, Q5 -1.39 vs Q1 1.64 | 4.35e-08 |
| 4 | pct_change_5d | numeric | Q5-Q1 -3.01 (rho -0.118) | n 1121, Q5 -0.89 vs Q1 2.12 | 7.73e-05 |
| 5 | vix_term_backwardation | bool | +2.98 (T 2.91 vs F -0.07) | n 134/987, WR 0.657 vs 0.507 | 2.87e-06 |
| 6 | vix_term_contango | bool | -2.98 (T -0.07 vs F 2.91) | n 987/134, WR 0.507 vs 0.657 | 2.87e-06 |
| 7 | is_january_extended | bool | +2.63 (T 2.65 vs F 0.02) | n 115/1006, WR 0.670 vs 0.508 | 1.14e-04 |
| 8 | sector_weakest_rs | numeric | Q5-Q1 -2.47 (rho -0.098) | n 1121, Q5 -0.64 vs Q1 1.83 | 1.07e-03 |
| 9 | days_to_cover | numeric | Q5-Q1 -2.39 (rho -0.103) | n 1118, Q5 -0.89 vs Q1 1.50 | 5.30e-04 |
| 10 | bb_10_20_pctb | numeric | Q5-Q1 -2.37 (rho -0.165) | n 1121, Q5 -0.87 vs Q1 1.49 | 2.81e-08 |
| 11 | trading_day_of_month | numeric | Q5-Q1 -2.35 (rho -0.100) | n 1121, Q5 -1.08 vs Q1 1.27 | 7.64e-04 |
| 12 | trading_days_left_in_month | numeric | Q5-Q1 +2.34 (rho +0.093) | n 1121, Q5 0.67 vs Q1 -1.67 | 1.75e-03 |
| 13 | hull_bearish | bool | +2.23 (T 1.97 vs F -0.26) | n 276/845, WR 0.634 vs 0.489 | 3.62e-06 |
| 14 | hull_bullish | bool | -2.23 (T -0.26 vs F 1.97) | n 845/276, WR 0.489 vs 0.634 | 3.62e-06 |
| 15 | rsi_14_cross_up_oversold_recent_3d | bool | -2.17 (T -1.54 vs F 0.63) | n 180/941, WR 0.439 vs 0.541 | 6.60e-04 |
| 16 | bb_10_20_pctb_gt_85 | bool | -2.07 (T -1.23 vs F 0.84) | n 301/820, WR 0.419 vs 0.563 | 9.52e-05 |
| 17 | bb_10_20_pctb_gt_75 | bool | -2.03 (T -0.83 vs F 1.20) | n 505/616, WR 0.451 vs 0.584 | 6.61e-06 |
| 18 | rsi_2_extreme_ob | bool | -1.99 (T -0.57 vs F 1.43) | n 641/480, WR 0.484 vs 0.579 | 6.96e-06 |
| 19 | smc_fvg_bullish_active | bool | -1.99 (T -0.77 vs F 1.22) | n 527/594, WR 0.465 vs 0.577 | 1.02e-05 |
| 20 | bb_10_20_pctb_gt_8 | bool | -1.86 (T -0.90 vs F 0.96) | n 408/713, WR 0.444 vs 0.571 | 7.82e-05 |
| 21 | below_ema_9 | bool | +1.76 (T 1.67 vs F -0.09) | n 239/882, WR 0.598 vs 0.505 | 2.15e-03 |
| 22 | price_above_ema_9 | bool | -1.76 (T -0.09 vs F 1.67) | n 882/239, WR 0.505 vs 0.598 | 2.15e-03 |
| 23 | price_above_ema_9_break_recent_5d | bool | -1.73 (T -0.09 vs F 1.64) | n 878/243, WR 0.505 vs 0.597 | 2.26e-03 |
| 24 | rsi_2_overbought | bool | -1.64 (T -0.12 vs F 1.51) | n 841/280, WR 0.505 vs 0.582 | 1.87e-03 |
| 25 | risk_off_regime_gold_signal | bool | +1.55 (T 1.04 vs F -0.51) | n 574/547, WR 0.564 vs 0.483 | 5.40e-04 |
| 26 | near_avwap_50low_atr_05x | bool | +1.53 (T 1.27 vs F -0.26) | n 354/744, WR 0.573 vs 0.499 | 1.40e-03 |
| 27 | pair_max_abs_zscore | numeric | Q5-Q1 +1.52 (rho +0.089) | n 1039, Q5 0.66 vs Q1 -0.86 | 3.91e-03 |
| 28 | obv_falling | bool | +1.51 (T 1.41 vs F -0.11) | n 291/830, WR 0.567 vs 0.510 | 1.17e-03 |
| 29 | obv_rising | bool | -1.51 (T -0.11 vs F 1.41) | n 830/291, WR 0.510 vs 0.567 | 1.17e-03 |
| 30 | near_avwap_20low_atr_05x | bool | +1.45 (T 1.25 vs F -0.20) | n 327/771, WR 0.572 vs 0.502 | 2.86e-03 |
| 31 | xs_max_anomaly | numeric | Q5-Q1 +1.31 (rho +0.102) | n 1111, Q5 1.12 vs Q1 -0.19 | 6.39e-04 |
| 32 | atr_pct | numeric | Q5-Q1 +1.22 (rho +0.097) | n 1121, Q5 0.79 vs Q1 -0.43 | 1.12e-03 |
| 33 | bond_equity_20d_pct_change | numeric | Q5-Q1 +0.87 (rho +0.097) | n 1121, Q5 1.33 vs Q1 0.46 | 1.12e-03 |
| 34 | gold_silver_ratio | numeric | Q5-Q1 +0.86 (rho +0.103) | n 1121, Q5 1.37 vs Q1 0.51 | 5.74e-04 |
