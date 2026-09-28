# COMPANION-SIGNAL SCREEN - bollinger_lowerfamily

exit time_stop_10d; window is; 1192 unique entries; 535 signals tested; BH-FDR q=0.05 threshold p<=0.02; 214 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | cot_rut_commercials_net_pct | numeric | Q5-Q1 -4.67 (rho -0.208) | n 1192, Q5 -3.27 vs Q1 1.40 | 3.82e-13 |
| 2 | cot_gold_mmoney_pctile_3y | numeric | Q5-Q1 +3.86 (rho +0.139) | n 1192, Q5 1.13 vs Q1 -2.72 | 1.58e-06 |
| 3 | defensive_leadership | bool | +3.82 (T 1.60 vs F -2.22) | n 588/604, WR 0.605 vs 0.361 | 1.33e-17 |
| 4 | vix_term_backwardation | bool | +3.57 (T 2.82 vs F -0.75) | n 140/1052, WR 0.714 vs 0.451 | 2.76e-08 |
| 5 | vix_term_contango | bool | -3.57 (T -0.75 vs F 2.82) | n 1052/140, WR 0.451 vs 0.714 | 2.76e-08 |
| 6 | macd_12_26_9_line | numeric | Q5-Q1 -3.54 (rho -0.170) | n 1192, Q5 -2.53 vs Q1 1.01 | 3.42e-09 |
| 7 | cot_dxy_commercials_net_pct | numeric | Q5-Q1 +3.49 (rho +0.211) | n 1192, Q5 0.68 vs Q1 -2.82 | 1.74e-13 |
| 8 | ao | numeric | Q5-Q1 -3.45 (rho -0.169) | n 1192, Q5 -2.34 vs Q1 1.12 | 4.33e-09 |
| 9 | vix_percentile | numeric | Q5-Q1 +3.40 (rho +0.200) | n 1192, Q5 1.51 vs Q1 -1.89 | 3.00e-12 |
| 10 | macd_8_21_5_signal | numeric | Q5-Q1 -3.34 (rho -0.169) | n 1192, Q5 -2.47 vs Q1 0.88 | 4.56e-09 |
| 11 | macd_8_21_5_line | numeric | Q5-Q1 -3.05 (rho -0.161) | n 1192, Q5 -1.96 vs Q1 1.09 | 2.12e-08 |
| 12 | days_to_next_holiday | numeric | Q5-Q1 +3.00 (rho +0.112) | n 697, Q5 1.50 vs Q1 -1.50 | 3.01e-03 |
| 13 | cot_dxy_commercials_pctile_3y | numeric | Q5-Q1 +2.93 (rho +0.220) | n 1192, Q5 0.66 vs Q1 -2.27 | 1.79e-14 |
| 14 | vix_band_high | bool | +2.83 (T 1.08 vs F -1.75) | n 599/593, WR 0.576 vs 0.386 | 3.03e-10 |
| 15 | pct_from_avwap_50low | numeric | Q5-Q1 -2.79 (rho -0.133) | n 1151, Q5 -2.09 vs Q1 0.70 | 6.19e-06 |
| 16 | rsi_9_overbought | bool | -2.73 (T -2.75 vs F -0.02) | n 137/1055, WR 0.285 vs 0.507 | 8.47e-05 |
| 17 | dc20_new_high | bool | -2.72 (T -2.55 vs F 0.17) | n 220/972, WR 0.327 vs 0.516 | 1.64e-05 |
| 18 | dc10_new_high | bool | -2.71 (T -2.54 vs F 0.18) | n 223/969, WR 0.327 vs 0.517 | 1.42e-05 |
| 19 | pct_change_10d | numeric | Q5-Q1 -2.61 (rho -0.133) | n 1192, Q5 -1.83 vs Q1 0.78 | 3.90e-06 |
| 20 | mfi_broad_overbought | bool | -2.59 (T -2.51 vs F 0.09) | n 193/999, WR 0.342 vs 0.509 | 2.94e-05 |
| 21 | macd_12_26_9_signal | numeric | Q5-Q1 -2.58 (rho -0.089) | n 1192, Q5 -1.56 vs Q1 1.02 | 2.16e-03 |
| 22 | vix_vix3m_ratio | numeric | Q5-Q1 +2.56 (rho +0.123) | n 1192, Q5 1.82 vs Q1 -0.74 | 2.08e-05 |
| 23 | gap_dn_1_5pct | bool | +2.54 (T 2.00 vs F -0.55) | n 101/1091, WR 0.663 vs 0.465 | 1.34e-02 |
| 24 | pct_change_5d | numeric | Q5-Q1 -2.52 (rho -0.168) | n 1192, Q5 -1.93 vs Q1 0.59 | 5.00e-09 |
| 25 | gap_dn_pct | numeric | Q5-Q1 +2.50 (rho +0.079) | n 1192, Q5 1.90 vs Q1 -0.60 | 6.66e-03 |
| 26 | gap_up_pct | numeric | Q5-Q1 -2.50 (rho -0.079) | n 1192, Q5 -0.60 vs Q1 1.90 | 6.66e-03 |
| 27 | stoch_d | numeric | Q5-Q1 -2.42 (rho -0.143) | n 1192, Q5 -2.23 vs Q1 0.19 | 7.33e-07 |
| 28 | dc20_resistance_break_retest_strong | bool | -2.41 (T -1.92 vs F 0.49) | n 405/787, WR 0.360 vs 0.544 | 7.37e-07 |
| 29 | pct_from_vwap | numeric | Q5-Q1 +2.37 (rho +0.137) | n 1192, Q5 1.00 vs Q1 -1.36 | 2.00e-06 |
| 30 | mfi | numeric | Q5-Q1 -2.37 (rho -0.149) | n 1192, Q5 -2.19 vs Q1 0.17 | 2.39e-07 |
| 31 | smc_ote_short_zone | bool | -2.35 (T -2.47 vs F -0.12) | n 107/1085, WR 0.327 vs 0.497 | 3.81e-04 |
| 32 | price_above_ema_200_break_recent_5d | bool | +2.29 (T 1.69 vs F -0.60) | n 142/1050, WR 0.655 vs 0.458 | 7.60e-05 |
| 33 | below_sma_50 | bool | +2.29 (T 0.84 vs F -1.45) | n 582/610, WR 0.576 vs 0.392 | 3.68e-07 |
| 34 | price_above_sma_50 | bool | -2.29 (T -1.45 vs F 0.84) | n 610/582, WR 0.392 vs 0.576 | 3.68e-07 |
| 35 | below_ema_50 | bool | +2.26 (T 0.81 vs F -1.45) | n 588/604, WR 0.578 vs 0.387 | 5.65e-07 |
| 36 | price_above_ema_50 | bool | -2.26 (T -1.45 vs F 0.81) | n 604/588, WR 0.387 vs 0.578 | 5.65e-07 |
| 37 | ppo | numeric | Q5-Q1 -2.24 (rho -0.165) | n 1192, Q5 -1.26 vs Q1 0.98 | 9.94e-09 |
| 38 | rsi_21_bullish | bool | -2.24 (T -1.42 vs F 0.82) | n 611/581, WR 0.383 vs 0.585 | 6.56e-07 |
| 39 | resistance_break_retest | bool | -2.23 (T -1.63 vs F 0.60) | n 499/693, WR 0.375 vs 0.558 | 1.77e-06 |
| 40 | rsi_14_cross_up_oversold_recent_3d | bool | +2.21 (T 1.69 vs F -0.52) | n 100/1092, WR 0.660 vs 0.465 | 4.03e-04 |
