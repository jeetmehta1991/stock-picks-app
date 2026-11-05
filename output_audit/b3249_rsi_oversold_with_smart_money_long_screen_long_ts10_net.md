# COMPANION-SIGNAL SCREEN - rsi_oversold_with_smart_money_long (exact names)

exit time_stop_10d; basis net; window is; 2135 unique entries; 569 signals tested; BH-FDR q=0.05 threshold p<=0.0026362; 30 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | cot_copper_commercials_pctile_3y | numeric | Q5-Q1 +3.08 (rho +0.180) | n 2135, Q5 1.76 vs Q1 -1.33 | 4.53e-17 |
| 2 | vix_term_backwardation | bool | +3.07 (T 2.92 vs F -0.15) | n 258/1877, WR 0.736 vs 0.490 | 9.34e-11 |
| 3 | vix_term_contango | bool | -3.07 (T -0.15 vs F 2.92) | n 1877/258, WR 0.490 vs 0.736 | 9.34e-11 |
| 4 | cot_copper_commercials_net_pct | numeric | Q5-Q1 +2.64 (rho +0.194) | n 2135, Q5 2.14 vs Q1 -0.50 | 1.85e-19 |
| 5 | cot_rut_commercials_net_pct | numeric | Q5-Q1 -2.50 (rho -0.172) | n 2135, Q5 -0.70 vs Q1 1.80 | 1.10e-15 |
| 6 | vix_percentile | numeric | Q5-Q1 +2.18 (rho +0.105) | n 2135, Q5 2.43 vs Q1 0.26 | 1.22e-06 |
| 7 | gold_silver_20d_pct_change | numeric | Q5-Q1 +2.13 (rho +0.082) | n 2135, Q5 2.46 vs Q1 0.32 | 1.57e-04 |
| 8 | vix_vix3m_ratio | numeric | Q5-Q1 +2.07 (rho +0.107) | n 2135, Q5 1.86 vs Q1 -0.21 | 8.03e-07 |
| 9 | sector_weakest_rs | numeric | Q5-Q1 -1.80 (rho -0.071) | n 2135, Q5 -0.22 vs Q1 1.58 | 9.84e-04 |
| 10 | atr_pct | numeric | Q5-Q1 +1.58 (rho +0.080) | n 2135, Q5 1.38 vs Q1 -0.20 | 2.20e-04 |
| 11 | po3_accum_range_pct | numeric | Q5-Q1 +1.56 (rho +0.097) | n 2135, Q5 1.16 vs Q1 -0.40 | 6.51e-06 |
| 12 | xs_max_anomaly | numeric | Q5-Q1 +1.55 (rho +0.072) | n 2118, Q5 1.46 vs Q1 -0.09 | 8.89e-04 |
| 13 | double_top_detected | bool | +1.52 (T 1.50 vs F -0.02) | n 336/1799, WR 0.580 vs 0.509 | 4.39e-04 |
| 14 | xs_momentum_top_decile | bool | +1.34 (T 1.28 vs F -0.06) | n 457/1663, WR 0.567 vs 0.508 | 2.02e-03 |
| 15 | avg_position_age_quarters | numeric | Q5-Q1 -1.25 (rho -0.072) | n 2092, Q5 -0.58 vs Q1 0.67 | 1.02e-03 |
| 16 | vix_today | numeric | Q5-Q1 +1.25 (rho +0.087) | n 2135, Q5 1.51 vs Q1 0.26 | 5.89e-05 |
| 17 | vix_value | numeric | Q5-Q1 +1.25 (rho +0.087) | n 2135, Q5 1.51 vs Q1 0.26 | 5.89e-05 |
| 18 | cot_dxy_mmoney_pctile_3y | numeric | Q5-Q1 +1.23 (rho +0.079) | n 2135, Q5 1.39 vs Q1 0.16 | 2.44e-04 |
| 19 | cpr_width | numeric | Q5-Q1 +1.01 (rho +0.075) | n 2135, Q5 0.85 vs Q1 -0.16 | 4.94e-04 |
| 20 | cot_dow_mmoney_pctile_3y | numeric | Q5-Q1 -0.93 (rho -0.065) | n 2135, Q5 -0.10 vs Q1 0.83 | 2.61e-03 |
| 21 | ema_20_50_bearish | bool | +0.92 (T 0.80 vs F -0.13) | n 800/1335, WR 0.539 vs 0.509 | 2.43e-03 |
| 22 | ema_20_50_bullish | bool | -0.92 (T -0.13 vs F 0.80) | n 1335/800, WR 0.509 vs 0.539 | 2.43e-03 |
| 23 | gold_silver_ratio | numeric | Q5-Q1 +0.91 (rho +0.108) | n 2135, Q5 0.72 vs Q1 -0.19 | 5.98e-07 |
| 24 | bb_10_20_squeeze | bool | -0.91 (T -0.35 vs F 0.56) | n 808/1327, WR 0.478 vs 0.546 | 1.21e-03 |
| 25 | smc_ob_bullish_active | bool | -0.90 (T -0.31 vs F 0.58) | n 872/1263, WR 0.503 vs 0.531 | 2.59e-03 |
| 26 | bb_10_20_bandwidth | numeric | Q5-Q1 +0.83 (rho +0.082) | n 2135, Q5 0.75 vs Q1 -0.08 | 1.52e-04 |
| 27 | pair_zscore_signed | numeric | Q5-Q1 +0.73 (rho +0.079) | n 1987, Q5 0.83 vs Q1 0.10 | 4.09e-04 |
| 28 | short_interest_observations | numeric | Q5-Q1 +0.73 (rho +0.096) | n 2135, Q5 0.32 vs Q1 -0.41 | 8.43e-06 |
| 29 | dxy_proxy_close | numeric | Q5-Q1 +0.48 (rho +0.077) | n 2135, Q5 -0.62 vs Q1 -1.10 | 3.60e-04 |
| 30 | sector_strongest_rs | numeric | Q5-Q1 -0.28 (rho -0.065) | n 2135, Q5 0.49 vs Q1 0.77 | 2.51e-03 |
