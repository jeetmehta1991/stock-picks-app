# COMPANION-SIGNAL SCREEN - r1_break_retest (exact names)

exit time_stop_10d; basis net; window is; 1389 unique entries; 448 signals tested; BH-FDR q=0.05 threshold p<=0.005692; 51 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | cot_dxy_mmoney_pctile_3y | numeric | Q5-Q1 +4.70 (rho +0.142) | n 1389, Q5 3.04 vs Q1 -1.66 | 1.03e-07 |
| 2 | sector_weakest_rs | numeric | Q5-Q1 -4.28 (rho -0.214) | n 1389, Q5 -1.12 vs Q1 3.16 | 8.21e-16 |
| 3 | cot_gold_mmoney_pctile_3y | numeric | Q5-Q1 -3.55 (rho -0.105) | n 1389, Q5 -0.12 vs Q1 3.44 | 8.69e-05 |
| 4 | gold_silver_20d_pct_change | numeric | Q5-Q1 +3.32 (rho +0.182) | n 1389, Q5 3.58 vs Q1 0.26 | 7.71e-12 |
| 5 | days_until_fomc | numeric | Q5-Q1 -2.92 (rho -0.125) | n 1389, Q5 -0.52 vs Q1 2.40 | 3.06e-06 |
| 6 | is_pre_holiday | bool | -2.66 (T -1.85 vs F 0.81) | n 109/1280, WR 0.459 vs 0.573 | 2.42e-03 |
| 7 | xs_max_anomaly | numeric | Q5-Q1 +2.59 (rho +0.131) | n 1373, Q5 2.51 vs Q1 -0.08 | 1.06e-06 |
| 8 | vix_term_backwardation | bool | +2.55 (T 2.92 vs F 0.36) | n 130/1259, WR 0.723 vs 0.547 | 1.10e-05 |
| 9 | vix_term_contango | bool | -2.55 (T 0.36 vs F 2.92) | n 1259/130, WR 0.547 vs 0.723 | 1.10e-05 |
| 10 | vix_vix3m_ratio | numeric | Q5-Q1 +2.48 (rho +0.124) | n 1389, Q5 2.18 vs Q1 -0.30 | 3.65e-06 |
| 11 | cot_copper_commercials_pctile_3y | numeric | Q5-Q1 +2.11 (rho +0.166) | n 1389, Q5 0.79 vs Q1 -1.32 | 5.39e-10 |
| 12 | pct_change_5d | numeric | Q5-Q1 -2.10 (rho -0.085) | n 1389, Q5 -0.10 vs Q1 2.00 | 1.51e-03 |
| 13 | risk_off_regime_gold_signal | bool | +2.02 (T 1.62 vs F -0.40) | n 688/701, WR 0.628 vs 0.501 | 3.49e-06 |
| 14 | ema_50_200_bearish | bool | +1.96 (T 0.84 vs F -1.12) | n 1201/180, WR 0.580 vs 0.444 | 6.94e-04 |
| 15 | ema_50_200_bullish | bool | -1.96 (T -1.12 vs F 0.84) | n 180/1201, WR 0.444 vs 0.580 | 6.94e-04 |
| 16 | monthly_momentum_6m | numeric | Q5-Q1 -1.96 (rho -0.101) | n 1368, Q5 -0.35 vs Q1 1.61 | 1.92e-04 |
| 17 | rsi_2 | numeric | Q5-Q1 -1.93 (rho -0.087) | n 1389, Q5 -0.11 vs Q1 1.82 | 1.24e-03 |
| 18 | trading_day_of_month | numeric | Q5-Q1 -1.89 (rho -0.075) | n 1389, Q5 -0.21 vs Q1 1.68 | 5.42e-03 |
| 19 | atr_pct | numeric | Q5-Q1 +1.85 (rho +0.111) | n 1389, Q5 1.63 vs Q1 -0.22 | 3.25e-05 |
| 20 | sector_strongest_rs | numeric | Q5-Q1 -1.85 (rho -0.090) | n 1389, Q5 -1.17 vs Q1 0.67 | 7.67e-04 |
| 21 | pair_zscore_signed | numeric | Q5-Q1 +1.81 (rho +0.087) | n 1301, Q5 1.85 vs Q1 0.04 | 1.78e-03 |
| 22 | smc_fvg_bearish_active | bool | +1.81 (T 2.08 vs F 0.28) | n 249/1138, WR 0.651 vs 0.544 | 7.97e-04 |
| 23 | bb_10_20_pctb | numeric | Q5-Q1 -1.79 (rho -0.099) | n 1389, Q5 0.41 vs Q1 2.20 | 2.15e-04 |
| 24 | usd_strengthening | bool | +1.79 (T 1.92 vs F 0.13) | n 364/1025, WR 0.648 vs 0.534 | 8.66e-05 |
| 25 | gold_silver_ratio | numeric | Q5-Q1 +1.77 (rho +0.153) | n 1389, Q5 2.51 vs Q1 0.74 | 1.09e-08 |
| 26 | vix_today | numeric | Q5-Q1 +1.75 (rho +0.148) | n 1389, Q5 2.18 vs Q1 0.43 | 3.34e-08 |
| 27 | vix_value | numeric | Q5-Q1 +1.75 (rho +0.148) | n 1389, Q5 2.18 vs Q1 0.43 | 3.34e-08 |
| 28 | dc10_new_high | bool | -1.69 (T -0.47 vs F 1.23) | n 512/877, WR 0.535 vs 0.580 | 2.58e-04 |
| 29 | rsi_2_extreme_ob | bool | -1.66 (T 0.11 vs F 1.77) | n 976/413, WR 0.542 vs 0.615 | 1.11e-03 |
| 30 | stochrsi_overbought | bool | -1.61 (T 0.16 vs F 1.77) | n 1010/379, WR 0.542 vs 0.623 | 2.03e-03 |
| 31 | bb_10_20_pctb_gt_75 | bool | -1.60 (T 0.13 vs F 1.73) | n 980/409, WR 0.542 vs 0.616 | 1.04e-03 |
| 32 | within_pead_window | bool | -1.60 (T -0.48 vs F 1.12) | n 483/881, WR 0.482 vs 0.603 | 1.78e-04 |
| 33 | usd_weakening | bool | +1.59 (T 1.87 vs F 0.28) | n 282/1107, WR 0.592 vs 0.556 | 7.28e-04 |
| 34 | sma_50_200_bullish | bool | -1.58 (T -0.71 vs F 0.87) | n 248/1133, WR 0.508 vs 0.575 | 2.80e-03 |
| 35 | pct_from_vwap | numeric | Q5-Q1 -1.51 (rho -0.084) | n 1389, Q5 -0.13 vs Q1 1.39 | 1.73e-03 |
| 36 | dc10_breakout_up | bool | -1.51 (T -0.38 vs F 1.14) | n 491/898, WR 0.536 vs 0.579 | 6.73e-04 |
| 37 | near_avwap_50low_atr_10x | bool | +1.48 (T 1.44 vs F -0.05) | n 593/790, WR 0.627 vs 0.514 | 1.19e-03 |
| 38 | earnings_announcement_return | numeric | Q5-Q1 +1.48 (rho +0.080) | n 1286, Q5 0.73 vs Q1 -0.75 | 4.06e-03 |
| 39 | bb_10_20_pctb_gt_8 | bool | -1.45 (T 0.01 vs F 1.46) | n 824/565, WR 0.534 vs 0.607 | 1.13e-03 |
| 40 | near_avwap_20low_atr_10x | bool | +1.45 (T 1.42 vs F -0.02) | n 586/798, WR 0.623 vs 0.519 | 1.65e-03 |
