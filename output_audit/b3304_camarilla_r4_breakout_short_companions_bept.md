# COMPANION-SIGNAL SCREEN - camarilla_r4_breakout (exact names)

exit breakeven_plus_trail; window is; 1025 unique entries; 472 signals tested; BH-FDR q=0.05 threshold p<=0.012712; 120 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | vix_term_backwardation | bool | -7.60 (T -5.48 vs F 2.12) | n 137/888, WR 0.124 vs 0.385 | 1.96e-15 |
| 2 | vix_term_contango | bool | +7.60 (T 2.12 vs F -5.48) | n 888/137, WR 0.385 vs 0.124 | 1.96e-15 |
| 3 | vix_vix3m_ratio | numeric | Q5-Q1 -6.92 (rho -0.179) | n 1025, Q5 -3.11 vs Q1 3.80 | 8.52e-09 |
| 4 | vix_percentile | numeric | Q5-Q1 -6.75 (rho -0.117) | n 1025, Q5 -3.63 vs Q1 3.12 | 1.68e-04 |
| 5 | ppo | numeric | Q5-Q1 +5.23 (rho +0.186) | n 1025, Q5 3.38 vs Q1 -1.86 | 1.89e-09 |
| 6 | monthly_momentum_6m | numeric | Q5-Q1 +5.22 (rho +0.214) | n 930, Q5 3.64 vs Q1 -1.58 | 3.98e-11 |
| 7 | gold_silver_20d_pct_change | numeric | Q5-Q1 -4.93 (rho -0.141) | n 1025, Q5 -3.63 vs Q1 1.30 | 5.98e-06 |
| 8 | weekly_momentum_4w | numeric | Q5-Q1 +4.88 (rho +0.157) | n 1025, Q5 2.92 vs Q1 -1.96 | 4.17e-07 |
| 9 | ppo_signal | numeric | Q5-Q1 +4.44 (rho +0.184) | n 1025, Q5 2.80 vs Q1 -1.64 | 2.88e-09 |
| 10 | near_52w_low_105pct | bool | -4.38 (T -2.77 vs F 1.61) | n 118/907, WR 0.246 vs 0.364 | 1.01e-03 |
| 11 | pct_change_20d | numeric | Q5-Q1 +4.16 (rho +0.148) | n 1025, Q5 2.58 vs Q1 -1.58 | 1.93e-06 |
| 12 | roc_12 | numeric | Q5-Q1 +4.09 (rho +0.151) | n 1025, Q5 2.70 vs Q1 -1.38 | 1.24e-06 |
| 13 | vix_today | numeric | Q5-Q1 -4.03 (rho -0.141) | n 1025, Q5 -1.58 vs Q1 2.44 | 5.93e-06 |
| 14 | vix_value | numeric | Q5-Q1 -4.03 (rho -0.141) | n 1025, Q5 -1.58 vs Q1 2.44 | 5.93e-06 |
| 15 | usd_weakening | bool | -3.95 (T -2.43 vs F 1.52) | n 109/916, WR 0.284 vs 0.358 | 1.33e-03 |
| 16 | rsi_21 | numeric | Q5-Q1 +3.78 (rho +0.162) | n 1025, Q5 2.81 vs Q1 -0.96 | 1.75e-07 |
| 17 | near_avwap_252low_atr_05x | bool | -3.76 (T -2.05 vs F 1.70) | n 100/779, WR 0.280 vs 0.353 | 2.76e-03 |
| 18 | monthly_above_sma_6 | bool | +3.71 (T 2.81 vs F -0.90) | n 454/476, WR 0.374 vs 0.292 | 8.24e-07 |
| 19 | close_in_bottom_40pct_of_range | bool | -3.64 (T 0.67 vs F 4.31) | n 902/123, WR 0.338 vs 0.439 | 2.67e-03 |
| 20 | htf_aligned_bear | bool | -3.60 (T -1.28 vs F 2.32) | n 346/679, WR 0.272 vs 0.390 | 1.22e-05 |
| 21 | monthly_bias_bear | bool | -3.43 (T -1.12 vs F 2.32) | n 381/549, WR 0.278 vs 0.370 | 2.05e-05 |
| 22 | adx_di_plus | numeric | Q5-Q1 +3.32 (rho +0.132) | n 1025, Q5 2.44 vs Q1 -0.88 | 2.29e-05 |
| 23 | avwap_252low_loss_recent_3d | bool | -3.32 (T -1.42 vs F 1.90) | n 166/713, WR 0.289 vs 0.358 | 2.78e-03 |
| 24 | ema_20_50_bearish | bool | -3.31 (T -0.78 vs F 2.53) | n 441/584, WR 0.308 vs 0.382 | 3.98e-06 |
| 25 | ema_20_50_bullish | bool | +3.31 (T 2.53 vs F -0.78) | n 584/441, WR 0.382 vs 0.308 | 3.98e-06 |
| 26 | short_interest_observations | numeric | Q5-Q1 -3.30 (rho -0.151) | n 1025, Q5 -0.65 vs Q1 2.65 | 1.22e-06 |
| 27 | sma_20_50_bullish | bool | +3.28 (T 2.52 vs F -0.77) | n 584/441, WR 0.385 vs 0.304 | 4.76e-06 |
| 28 | vp_below_value_area | bool | -3.27 (T -1.21 vs F 2.06) | n 300/725, WR 0.287 vs 0.377 | 1.72e-05 |
| 29 | sector_weakest_rs | numeric | Q5-Q1 +3.25 (rho +0.141) | n 1025, Q5 1.75 vs Q1 -1.50 | 5.61e-06 |
| 30 | ichi_below_cloud | bool | -3.19 (T -0.63 vs F 2.56) | n 467/558, WR 0.315 vs 0.380 | 7.83e-06 |
| 31 | macd_12_26_9_signal | numeric | Q5-Q1 +3.17 (rho +0.136) | n 1025, Q5 2.53 vs Q1 -0.63 | 1.22e-05 |
| 32 | uo | numeric | Q5-Q1 +3.14 (rho +0.129) | n 1025, Q5 3.04 vs Q1 -0.11 | 3.50e-05 |
| 33 | monthly_bias_bull | bool | +3.14 (T 2.72 vs F -0.42) | n 393/537, WR 0.372 vs 0.304 | 2.56e-05 |
| 34 | gold_silver_ratio | numeric | Q5-Q1 -3.11 (rho -0.141) | n 1025, Q5 -2.27 vs Q1 0.84 | 6.07e-06 |
| 35 | above_avwap_252low | bool | +3.04 (T 1.96 vs F -1.08) | n 613/318, WR 0.357 vs 0.286 | 5.64e-04 |
| 36 | below_avwap_252low | bool | -3.04 (T -1.08 vs F 1.96) | n 318/613, WR 0.286 vs 0.357 | 5.64e-04 |
| 37 | pct_change_10d | numeric | Q5-Q1 +3.03 (rho +0.121) | n 1025, Q5 1.96 vs Q1 -1.07 | 1.02e-04 |
| 38 | macd_12_26_9_line | numeric | Q5-Q1 +2.96 (rho +0.137) | n 1025, Q5 1.71 vs Q1 -1.25 | 1.08e-05 |
| 39 | near_avwap_50low_atr_05x | bool | -2.95 (T -0.88 vs F 2.07) | n 193/658, WR 0.295 vs 0.384 | 5.59e-04 |
| 40 | cot_rut_commercials_net_pct | numeric | Q5-Q1 +2.95 (rho +0.190) | n 1025, Q5 1.52 vs Q1 -1.43 | 9.56e-10 |
