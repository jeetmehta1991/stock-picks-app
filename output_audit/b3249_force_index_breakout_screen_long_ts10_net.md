# COMPANION-SIGNAL SCREEN - force_index_breakout (exact names)

exit time_stop_10d; basis net; window is; 952 unique entries; 430 signals tested; BH-FDR q=0.05 threshold p<=0.0044186; 38 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | po3_accum_range_pct | numeric | Q5-Q1 +4.16 (rho +0.128) | n 952, Q5 3.58 vs Q1 -0.58 | 7.93e-05 |
| 2 | sector_weakest_rs | numeric | Q5-Q1 -4.15 (rho -0.125) | n 952, Q5 -1.66 vs Q1 2.49 | 1.04e-04 |
| 3 | pct_from_avwap_20high | numeric | Q5-Q1 +4.01 (rho +0.195) | n 885, Q5 2.89 vs Q1 -1.12 | 5.17e-09 |
| 4 | cot_sp500_commercials_pctile_3y | numeric | Q5-Q1 -3.80 (rho -0.114) | n 952, Q5 -1.71 vs Q1 2.09 | 4.17e-04 |
| 5 | weekly_momentum_4w | numeric | Q5-Q1 +3.80 (rho +0.135) | n 952, Q5 2.23 vs Q1 -1.56 | 3.13e-05 |
| 6 | gold_silver_20d_pct_change | numeric | Q5-Q1 +3.60 (rho +0.118) | n 952, Q5 3.21 vs Q1 -0.39 | 2.61e-04 |
| 7 | squeeze_momentum | numeric | Q5-Q1 +3.47 (rho +0.177) | n 952, Q5 1.86 vs Q1 -1.61 | 3.89e-08 |
| 8 | xs_max_anomaly | numeric | Q5-Q1 +3.44 (rho +0.140) | n 946, Q5 2.97 vs Q1 -0.47 | 1.63e-05 |
| 9 | atr_pct | numeric | Q5-Q1 +3.35 (rho +0.129) | n 952, Q5 2.95 vs Q1 -0.40 | 6.95e-05 |
| 10 | cot_sp500_commercials_net_pct | numeric | Q5-Q1 -3.32 (rho -0.122) | n 952, Q5 -1.61 vs Q1 1.71 | 1.61e-04 |
| 11 | pct_from_avwap_20low | numeric | Q5-Q1 +3.17 (rho +0.121) | n 941, Q5 2.98 vs Q1 -0.20 | 2.00e-04 |
| 12 | bb_20_15_above_mid | bool | +3.02 (T 0.86 vs F -2.16) | n 804/148, WR 0.558 vs 0.439 | 7.88e-06 |
| 13 | bb_20_20_above_mid | bool | +3.02 (T 0.86 vs F -2.16) | n 804/148, WR 0.558 vs 0.439 | 7.88e-06 |
| 14 | below_sma_20 | bool | -3.02 (T -2.16 vs F 0.86) | n 148/804, WR 0.439 vs 0.558 | 7.88e-06 |
| 15 | chandelier_long_bullish | bool | +3.02 (T 0.80 vs F -2.22) | n 823/129, WR 0.561 vs 0.403 | 6.92e-05 |
| 16 | vix_term_backwardation | bool | +3.01 (T 3.02 vs F 0.01) | n 119/833, WR 0.748 vs 0.510 | 2.87e-06 |
| 17 | vix_term_contango | bool | -3.01 (T 0.01 vs F 3.02) | n 833/119, WR 0.510 vs 0.748 | 2.87e-06 |
| 18 | bb_20_15_pctb | numeric | Q5-Q1 +3.00 (rho +0.122) | n 952, Q5 1.24 vs Q1 -1.75 | 1.63e-04 |
| 19 | bb_20_20_pctb | numeric | Q5-Q1 +3.00 (rho +0.122) | n 952, Q5 1.24 vs Q1 -1.75 | 1.64e-04 |
| 20 | bb_10_20_bandwidth | numeric | Q5-Q1 +2.83 (rho +0.102) | n 952, Q5 2.67 vs Q1 -0.16 | 1.71e-03 |
| 21 | below_sma_21 | bool | -2.80 (T -1.91 vs F 0.89) | n 170/782, WR 0.465 vs 0.556 | 1.24e-05 |
| 22 | price_above_sma_21 | bool | +2.80 (T 0.89 vs F -1.91) | n 782/170, WR 0.556 vs 0.465 | 1.24e-05 |
| 23 | pead_positive_surprise | bool | +2.16 (T 2.01 vs F -0.15) | n 134/721, WR 0.582 vs 0.530 | 1.95e-03 |
| 24 | sector_strongest_rs | numeric | Q5-Q1 -2.13 (rho -0.143) | n 952, Q5 -1.04 vs Q1 1.08 | 9.39e-06 |
| 25 | above_avwap_20high | bool | +2.05 (T 0.77 vs F -1.28) | n 775/177, WR 0.566 vs 0.424 | 6.53e-04 |
| 26 | below_avwap_20high | bool | -2.05 (T -1.28 vs F 0.77) | n 177/775, WR 0.424 vs 0.566 | 6.53e-04 |
| 27 | dxy_proxy_close | numeric | Q5-Q1 +2.04 (rho +0.096) | n 952, Q5 0.66 vs Q1 -1.37 | 2.99e-03 |
| 28 | chandelier_short_flip_up | bool | +1.96 (T 1.89 vs F -0.07) | n 223/729, WR 0.664 vs 0.502 | 7.16e-04 |
| 29 | near_r1_wide | bool | -1.68 (T -0.41 vs F 1.27) | n 500/452, WR 0.500 vs 0.584 | 2.29e-03 |
| 30 | sma_20_50_bullish | bool | -1.68 (T -0.85 vs F 0.83) | n 250/702, WR 0.480 vs 0.561 | 2.54e-03 |
| 31 | above_avwap_252low | bool | +1.60 (T 0.88 vs F -0.72) | n 665/264, WR 0.570 vs 0.485 | 3.74e-03 |
| 32 | below_avwap_252low | bool | -1.60 (T -0.72 vs F 0.88) | n 264/665, WR 0.485 vs 0.570 | 3.74e-03 |
| 33 | vix_vix3m_ratio | numeric | Q5-Q1 +1.60 (rho +0.109) | n 952, Q5 2.01 vs Q1 0.42 | 7.52e-04 |
| 34 | weekly_momentum_pos | bool | +1.54 (T 1.13 vs F -0.41) | n 493/459, WR 0.560 vs 0.519 | 4.15e-03 |
| 35 | cot_rut_commercials_net_pct | numeric | Q5-Q1 -1.46 (rho -0.109) | n 952, Q5 0.04 vs Q1 1.50 | 7.84e-04 |
| 36 | vix_today | numeric | Q5-Q1 +1.32 (rho +0.127) | n 952, Q5 1.84 vs Q1 0.52 | 8.55e-05 |
| 37 | vix_value | numeric | Q5-Q1 +1.32 (rho +0.127) | n 952, Q5 1.84 vs Q1 0.52 | 8.55e-05 |
| 38 | cpr_width | numeric | Q5-Q1 +1.29 (rho +0.109) | n 952, Q5 1.79 vs Q1 0.51 | 7.76e-04 |
