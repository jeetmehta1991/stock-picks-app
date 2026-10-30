# COMPANION-SIGNAL SCREEN - pivot_r1_breakout (exact names)

exit time_stop_10d; window is; 4288 unique entries; 314 signals tested; BH-FDR q=0.05 threshold p<=0.014968; 94 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | xs_max_anomaly | numeric | Q5-Q1 +3.22 (rho +0.190) | n 4255, Q5 2.60 vs Q1 -0.62 | 4.85e-36 |
| 2 | cot_dxy_mmoney_pctile_3y | numeric | Q5-Q1 +3.10 (rho +0.100) | n 4288, Q5 1.92 vs Q1 -1.18 | 6.07e-11 |
| 3 | sector_weakest_rs | numeric | Q5-Q1 -2.91 (rho -0.121) | n 4288, Q5 -0.69 vs Q1 2.21 | 2.02e-15 |
| 4 | is_pre_holiday | bool | -2.75 (T -2.07 vs F 0.68) | n 234/4054, WR 0.423 vs 0.556 | 4.06e-06 |
| 5 | vix_term_backwardation | bool | +2.69 (T 2.79 vs F 0.11) | n 676/3612, WR 0.713 vs 0.518 | 2.38e-23 |
| 6 | vix_term_contango | bool | -2.69 (T 0.11 vs F 2.79) | n 3612/676, WR 0.518 vs 0.713 | 2.38e-23 |
| 7 | gold_silver_20d_pct_change | numeric | Q5-Q1 +2.47 (rho +0.137) | n 4288, Q5 2.63 vs Q1 0.16 | 1.85e-19 |
| 8 | atr_pct | numeric | Q5-Q1 +2.40 (rho +0.141) | n 4288, Q5 2.25 vs Q1 -0.16 | 1.44e-20 |
| 9 | po3_accum_range_pct | numeric | Q5-Q1 +2.31 (rho +0.140) | n 4288, Q5 2.05 vs Q1 -0.26 | 2.59e-20 |
| 10 | vix_vix3m_ratio | numeric | Q5-Q1 +2.19 (rho +0.109) | n 4288, Q5 2.24 vs Q1 0.05 | 8.12e-13 |
| 11 | vix_today | numeric | Q5-Q1 +2.03 (rho +0.138) | n 4288, Q5 2.34 vs Q1 0.31 | 1.07e-19 |
| 12 | vix_value | numeric | Q5-Q1 +2.03 (rho +0.138) | n 4288, Q5 2.34 vs Q1 0.31 | 1.07e-19 |
| 13 | days_to_next_holiday | numeric | Q5-Q1 +1.99 (rho +0.063) | n 2915, Q5 1.09 vs Q1 -0.90 | 6.49e-04 |
| 14 | vix_percentile | numeric | Q5-Q1 +1.95 (rho +0.098) | n 4288, Q5 2.21 vs Q1 0.26 | 1.45e-10 |
| 15 | cot_rut_mmoney_pctile_3y | numeric | Q5-Q1 +1.92 (rho +0.119) | n 4288, Q5 0.42 vs Q1 -1.50 | 5.68e-15 |
| 16 | cot_ndx_mmoney_pctile_3y | numeric | Q5-Q1 +1.72 (rho +0.118) | n 4288, Q5 1.04 vs Q1 -0.68 | 1.06e-14 |
| 17 | gap_dn_2pct | bool | +1.68 (T 2.17 vs F 0.49) | n 108/4180, WR 0.676 vs 0.545 | 1.29e-02 |
| 18 | cot_copper_commercials_pctile_3y | numeric | Q5-Q1 +1.62 (rho +0.096) | n 4288, Q5 0.25 vs Q1 -1.38 | 3.03e-10 |
| 19 | gap_dn_1_5pct | bool | +1.62 (T 2.09 vs F 0.46) | n 179/4109, WR 0.676 vs 0.543 | 3.28e-03 |
| 20 | is_week_open | bool | -1.58 (T -0.78 vs F 0.80) | n 738/3550, WR 0.474 vs 0.564 | 6.07e-07 |
| 21 | gap_up_2pct | bool | +1.54 (T 1.87 vs F 0.33) | n 559/3729, WR 0.637 vs 0.535 | 3.22e-05 |
| 22 | gap_up_1_5pct | bool | +1.53 (T 1.75 vs F 0.22) | n 882/3406, WR 0.636 vs 0.526 | 2.12e-07 |
| 23 | is_january | bool | +1.43 (T 1.85 vs F 0.42) | n 326/3962, WR 0.623 vs 0.542 | 5.75e-04 |
| 24 | macd_8_21_5_bearish | bool | +1.41 (T 1.74 vs F 0.33) | n 599/3689, WR 0.613 vs 0.538 | 9.62e-07 |
| 25 | macd_8_21_5_bullish | bool | -1.41 (T 0.33 vs F 1.74) | n 3689/599, WR 0.538 vs 0.613 | 9.62e-07 |
| 26 | usd_weakening | bool | +1.38 (T 1.68 vs F 0.30) | n 714/3574, WR 0.601 vs 0.538 | 6.53e-07 |
| 27 | director_only_buy | bool | +1.38 (T 1.89 vs F 0.51) | n 173/4059, WR 0.618 vs 0.547 | 3.88e-03 |
| 28 | avwap_20high_reclaim_held_2d | bool | -1.37 (T -0.58 vs F 0.79) | n 603/2898, WR 0.471 vs 0.560 | 2.85e-04 |
| 29 | smc_ob_bullish_active | bool | -1.35 (T -0.64 vs F 0.71) | n 572/3714, WR 0.469 vs 0.561 | 7.94e-06 |
| 30 | risk_off_regime_gold_signal | bool | +1.33 (T 1.17 vs F -0.16) | n 2221/2067, WR 0.588 vs 0.507 | 3.45e-09 |
| 31 | gold_silver_ratio | numeric | Q5-Q1 +1.31 (rho +0.122) | n 4288, Q5 1.74 vs Q1 0.43 | 1.21e-15 |
| 32 | is_monday | bool | -1.30 (T -0.57 vs F 0.73) | n 662/3626, WR 0.486 vs 0.560 | 9.66e-05 |
| 33 | xs_max_anomaly_decile | numeric | Q5-Q1 +1.27 (rho +0.081) | n 4255, Q5 1.26 vs Q1 -0.01 | 1.33e-07 |
| 34 | gap_dn_pct | numeric | Q5-Q1 -1.24 (rho -0.071) | n 4288, Q5 0.49 vs Q1 1.73 | 3.17e-06 |
| 35 | gap_up_pct | numeric | Q5-Q1 +1.24 (rho +0.071) | n 4288, Q5 1.73 vs Q1 0.49 | 3.17e-06 |
| 36 | trading_day_of_month | numeric | Q5-Q1 -1.23 (rho -0.055) | n 4288, Q5 -0.38 vs Q1 0.85 | 3.01e-04 |
| 37 | days_to_cover | numeric | Q5-Q1 -1.23 (rho -0.069) | n 4274, Q5 -0.16 vs Q1 1.07 | 7.04e-06 |
| 38 | near_s1_wide | bool | -1.23 (T -0.67 vs F 0.56) | n 105/4183, WR 0.457 vs 0.551 | 2.97e-03 |
| 39 | is_january_extended | bool | +1.23 (T 1.65 vs F 0.43) | n 367/3921, WR 0.613 vs 0.542 | 2.38e-03 |
| 40 | short_interest_observations | numeric | Q5-Q1 +1.19 (rho +0.065) | n 4274, Q5 1.27 vs Q1 0.08 | 2.19e-05 |
