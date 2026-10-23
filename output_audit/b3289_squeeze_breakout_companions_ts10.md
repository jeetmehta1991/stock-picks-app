# COMPANION-SIGNAL SCREEN - squeeze_breakout (exact names)

exit time_stop_10d; window is; 953 unique entries; 440 signals tested; BH-FDR q=0.05 threshold p<=0.014091; 124 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | short_interest_observations | numeric | Q5-Q1 +7.12 (rho +0.235) | n 951, Q5 6.48 vs Q1 -0.64 | 2.37e-13 |
| 2 | gold_silver_ratio | numeric | Q5-Q1 +5.01 (rho +0.243) | n 953, Q5 5.96 vs Q1 0.95 | 2.55e-14 |
| 3 | xs_max_anomaly | numeric | Q5-Q1 +4.29 (rho +0.265) | n 942, Q5 4.25 vs Q1 -0.04 | 1.19e-16 |
| 4 | cot_dxy_mmoney_pctile_3y | numeric | Q5-Q1 +4.19 (rho +0.204) | n 953, Q5 2.96 vs Q1 -1.23 | 1.90e-10 |
| 5 | sector_strongest_rs | numeric | Q5-Q1 -3.69 (rho -0.186) | n 953, Q5 -0.87 vs Q1 2.81 | 7.54e-09 |
| 6 | cot_rut_commercials_net_pct | numeric | Q5-Q1 -3.44 (rho -0.245) | n 953, Q5 0.71 vs Q1 4.15 | 1.70e-14 |
| 7 | vix_today | numeric | Q5-Q1 +3.34 (rho +0.233) | n 953, Q5 3.54 vs Q1 0.21 | 3.49e-13 |
| 8 | vix_value | numeric | Q5-Q1 +3.34 (rho +0.233) | n 953, Q5 3.54 vs Q1 0.21 | 3.49e-13 |
| 9 | vix_term_backwardation | bool | +3.26 (T 3.42 vs F 0.16) | n 249/704, WR 0.831 vs 0.555 | 1.27e-13 |
| 10 | vix_term_contango | bool | -3.26 (T 0.16 vs F 3.42) | n 704/249, WR 0.555 vs 0.831 | 1.27e-13 |
| 11 | vix_vix3m_ratio | numeric | Q5-Q1 +3.19 (rho +0.248) | n 953, Q5 3.40 vs Q1 0.21 | 7.30e-15 |
| 12 | gold_silver_20d_pct_change | numeric | Q5-Q1 +3.16 (rho +0.233) | n 953, Q5 3.72 vs Q1 0.56 | 3.52e-13 |
| 13 | bond_equity_ratio | numeric | Q5-Q1 -3.02 (rho -0.130) | n 953, Q5 -0.78 vs Q1 2.24 | 5.81e-05 |
| 14 | vix_percentile | numeric | Q5-Q1 +2.94 (rho +0.229) | n 953, Q5 3.52 vs Q1 0.58 | 8.57e-13 |
| 15 | bb_10_20_bandwidth | numeric | Q5-Q1 +2.92 (rho +0.184) | n 953, Q5 2.65 vs Q1 -0.27 | 1.08e-08 |
| 16 | trading_day_of_month | numeric | Q5-Q1 -2.92 (rho -0.124) | n 953, Q5 -1.44 vs Q1 1.48 | 1.26e-04 |
| 17 | po3_accum_range_pct | numeric | Q5-Q1 +2.86 (rho +0.168) | n 953, Q5 3.48 vs Q1 0.61 | 1.89e-07 |
| 18 | three_white_soldiers | bool | -2.79 (T -1.38 vs F 1.41) | n 134/819, WR 0.448 vs 0.657 | 2.11e-04 |
| 19 | bb_20_20_reclaim_from_lower_recent_3d | bool | +2.65 (T 3.14 vs F 0.49) | n 187/766, WR 0.840 vs 0.576 | 2.65e-08 |
| 20 | bb_10_20_reclaim_from_lower_recent_3d | bool | +2.56 (T 3.09 vs F 0.54) | n 177/776, WR 0.825 vs 0.582 | 1.51e-07 |
| 21 | risk_off_regime_gold_signal | bool | +2.46 (T 2.03 vs F -0.43) | n 559/394, WR 0.707 vs 0.515 | 1.29e-07 |
| 22 | ppo_hist | numeric | Q5-Q1 -2.42 (rho -0.114) | n 953, Q5 0.25 vs Q1 2.68 | 4.28e-04 |
| 23 | news_sentiment_30d | numeric | Q5-Q1 +2.42 (rho +0.131) | n 953, Q5 2.76 vs Q1 0.34 | 5.01e-05 |
| 24 | days_since_last_earnings | numeric | Q5-Q1 +2.41 (rho +0.142) | n 935, Q5 2.86 vs Q1 0.45 | 1.35e-05 |
| 25 | pct_from_avwap_20low | numeric | Q5-Q1 +2.40 (rho +0.142) | n 920, Q5 2.30 vs Q1 -0.09 | 1.54e-05 |
| 26 | usd_weakening | bool | +2.38 (T 3.04 vs F 0.66) | n 141/812, WR 0.674 vs 0.619 | 9.69e-05 |
| 27 | atr | numeric | Q5-Q1 +2.38 (rho +0.120) | n 953, Q5 2.76 vs Q1 0.38 | 2.06e-04 |
| 28 | atr_14 | numeric | Q5-Q1 +2.38 (rho +0.120) | n 953, Q5 2.76 vs Q1 0.38 | 2.06e-04 |
| 29 | total_active_holders | numeric | Q5-Q1 +2.34 (rho +0.148) | n 869, Q5 2.69 vs Q1 0.34 | 1.14e-05 |
| 30 | pct_change_5d | numeric | Q5-Q1 -2.29 (rho -0.123) | n 953, Q5 0.52 vs Q1 2.81 | 1.42e-04 |
| 31 | is_halloween_period | bool | +2.26 (T 2.01 vs F -0.24) | n 531/422, WR 0.693 vs 0.545 | 7.77e-07 |
| 32 | is_summer_period | bool | -2.26 (T -0.24 vs F 2.01) | n 422/531, WR 0.545 vs 0.693 | 7.77e-07 |
| 33 | smc_inverse_fvg_bullish | bool | -2.24 (T 0.65 vs F 2.88) | n 798/155, WR 0.605 vs 0.742 | 6.98e-05 |
| 34 | bb_20_15_pctb | numeric | Q5-Q1 -2.23 (rho -0.092) | n 953, Q5 0.72 vs Q1 2.95 | 4.37e-03 |
| 35 | bb_20_20_pctb | numeric | Q5-Q1 -2.23 (rho -0.092) | n 953, Q5 0.72 vs Q1 2.95 | 4.38e-03 |
| 36 | stoch_k | numeric | Q5-Q1 -2.21 (rho -0.094) | n 953, Q5 0.35 vs Q1 2.56 | 3.63e-03 |
| 37 | trading_days_left_in_month | numeric | Q5-Q1 +2.19 (rho +0.127) | n 953, Q5 1.46 vs Q1 -0.73 | 8.79e-05 |
| 38 | smc_fvg_bullish_active | bool | -2.11 (T -0.13 vs F 1.98) | n 435/518, WR 0.552 vs 0.691 | 3.51e-06 |
| 39 | macd_12_26_9_signal | numeric | Q5-Q1 -2.00 (rho -0.086) | n 953, Q5 0.10 vs Q1 2.10 | 7.87e-03 |
| 40 | above_cam_r3 | bool | +2.00 (T 1.27 vs F -0.73) | n 829/124, WR 0.644 vs 0.516 | 4.98e-03 |
