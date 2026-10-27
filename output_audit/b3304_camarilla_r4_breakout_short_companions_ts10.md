# COMPANION-SIGNAL SCREEN - camarilla_r4_breakout (exact names)

exit time_stop_10d; window is; 1025 unique entries; 472 signals tested; BH-FDR q=0.05 threshold p<=0.0085805; 81 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | vix_term_backwardation | bool | -6.08 (T -5.57 vs F 0.51) | n 137/888, WR 0.234 vs 0.503 | 6.77e-16 |
| 2 | vix_term_contango | bool | +6.08 (T 0.51 vs F -5.57) | n 888/137, WR 0.503 vs 0.234 | 6.77e-16 |
| 3 | short_interest_observations | numeric | Q5-Q1 -4.96 (rho -0.163) | n 1025, Q5 -2.45 vs Q1 2.51 | 1.51e-07 |
| 4 | vix_vix3m_ratio | numeric | Q5-Q1 -4.42 (rho -0.129) | n 1025, Q5 -3.47 vs Q1 0.95 | 3.58e-05 |
| 5 | monthly_momentum_6m | numeric | Q5-Q1 +4.24 (rho +0.212) | n 930, Q5 1.45 vs Q1 -2.79 | 6.29e-11 |
| 6 | risk_off_regime_bond_signal_strong | bool | -3.80 (T -3.60 vs F 0.21) | n 136/889, WR 0.338 vs 0.487 | 1.09e-06 |
| 7 | usd_weakening | bool | -3.72 (T -3.63 vs F 0.10) | n 109/916, WR 0.275 vs 0.490 | 3.00e-06 |
| 8 | dxy_proxy_close | numeric | Q5-Q1 -3.47 (rho -0.143) | n 1025, Q5 -0.59 vs Q1 2.87 | 4.12e-06 |
| 9 | ppo_signal | numeric | Q5-Q1 +3.34 (rho +0.140) | n 1025, Q5 1.48 vs Q1 -1.86 | 7.36e-06 |
| 10 | htf_aligned_bear | bool | -3.27 (T -2.47 vs F 0.81) | n 346/679, WR 0.370 vs 0.517 | 2.02e-08 |
| 11 | bb_10_20_bandwidth | numeric | Q5-Q1 -3.21 (rho -0.162) | n 1025, Q5 -3.26 vs Q1 -0.05 | 1.75e-07 |
| 12 | dxy_20d_pct_change | numeric | Q5-Q1 +3.20 (rho +0.137) | n 1025, Q5 1.27 vs Q1 -1.94 | 1.12e-05 |
| 13 | near_avwap_252low_atr_10x | bool | -2.98 (T -2.91 vs F 0.06) | n 195/684, WR 0.328 vs 0.491 | 2.03e-05 |
| 14 | avwap_252low_loss_recent_3d | bool | -2.88 (T -2.94 vs F -0.06) | n 166/713, WR 0.343 vs 0.481 | 2.01e-04 |
| 15 | weekly_momentum_4w | numeric | Q5-Q1 +2.86 (rho +0.104) | n 1025, Q5 0.29 vs Q1 -2.57 | 8.79e-04 |
| 16 | monthly_above_sma_6 | bool | +2.82 (T 0.62 vs F -2.19) | n 454/476, WR 0.524 vs 0.363 | 2.51e-07 |
| 17 | pct_change_20d | numeric | Q5-Q1 +2.80 (rho +0.108) | n 1025, Q5 0.46 vs Q1 -2.34 | 5.04e-04 |
| 18 | monthly_bias_bear | bool | -2.79 (T -2.46 vs F 0.33) | n 381/549, WR 0.360 vs 0.499 | 8.94e-07 |
| 19 | total_active_holders | numeric | Q5-Q1 -2.77 (rho -0.091) | n 943, Q5 -1.56 vs Q1 1.21 | 5.03e-03 |
| 20 | pct_from_avwap_252low | numeric | Q5-Q1 +2.75 (rho +0.146) | n 879, Q5 0.98 vs Q1 -1.78 | 1.46e-05 |
| 21 | pct_from_avwap_20high | numeric | Q5-Q1 +2.68 (rho +0.099) | n 955, Q5 0.01 vs Q1 -2.67 | 2.28e-03 |
| 22 | sector_weakest_rs | numeric | Q5-Q1 +2.66 (rho +0.137) | n 1025, Q5 -0.07 vs Q1 -2.73 | 1.10e-05 |
| 23 | monthly_bias_bull | bool | +2.62 (T 0.70 vs F -1.93) | n 393/537, WR 0.524 vs 0.382 | 1.70e-06 |
| 24 | supertrend_flip_recent_short_5d | bool | -2.60 (T -2.62 vs F -0.02) | n 109/916, WR 0.339 vs 0.483 | 3.31e-03 |
| 25 | ppo | numeric | Q5-Q1 +2.58 (rho +0.123) | n 1025, Q5 0.90 vs Q1 -1.68 | 7.93e-05 |
| 26 | monthly_momentum_pos | bool | +2.55 (T 0.41 vs F -2.14) | n 483/447, WR 0.513 vs 0.365 | 3.26e-06 |
| 27 | vp_below_value_area | bool | -2.54 (T -2.09 vs F 0.44) | n 300/725, WR 0.393 vs 0.498 | 1.82e-05 |
| 28 | above_avwap_252low | bool | +2.46 (T 0.03 vs F -2.43) | n 613/318, WR 0.483 vs 0.365 | 4.93e-05 |
| 29 | below_avwap_252low | bool | -2.46 (T -2.43 vs F 0.03) | n 318/613, WR 0.365 vs 0.483 | 4.93e-05 |
| 30 | monthly_above_sma_12 | bool | +2.45 (T 0.35 vs F -2.10) | n 488/442, WR 0.496 vs 0.382 | 8.73e-06 |
| 31 | risk_off_regime_bond_signal | bool | -2.43 (T -2.14 vs F 0.29) | n 248/777, WR 0.403 vs 0.488 | 8.90e-05 |
| 32 | near_avwap_252low_atr_15x | bool | -2.38 (T -2.22 vs F 0.16) | n 280/599, WR 0.375 vs 0.492 | 9.39e-05 |
| 33 | rsi_21 | numeric | Q5-Q1 +2.38 (rho +0.115) | n 1025, Q5 0.50 vs Q1 -1.87 | 2.36e-04 |
| 34 | macd_12_26_9_line | numeric | Q5-Q1 +2.27 (rho +0.093) | n 1025, Q5 0.62 vs Q1 -1.65 | 2.84e-03 |
| 35 | ichi_above_cloud | bool | +2.25 (T 1.06 vs F -1.19) | n 406/619, WR 0.539 vs 0.420 | 2.22e-05 |
| 36 | near_avwap_252low_atr_20x | bool | -2.22 (T -1.90 vs F 0.31) | n 362/517, WR 0.387 vs 0.503 | 9.01e-05 |
| 37 | ichi_weekly_below_cloud | bool | -2.21 (T -2.32 vs F -0.11) | n 296/634, WR 0.392 vs 0.465 | 3.71e-04 |
| 38 | below_sma_50 | bool | -2.15 (T -1.24 vs F 0.91) | n 575/450, WR 0.419 vs 0.529 | 4.97e-05 |
| 39 | price_above_sma_50 | bool | +2.15 (T 0.91 vs F -1.24) | n 450/575, WR 0.529 vs 0.419 | 4.97e-05 |
| 40 | inside_kc | bool | +2.12 (T 0.34 vs F -1.78) | n 717/308, WR 0.490 vs 0.416 | 2.75e-04 |
