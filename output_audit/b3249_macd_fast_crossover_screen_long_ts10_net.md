# COMPANION-SIGNAL SCREEN - macd_fast_crossover (exact names)

exit time_stop_10d; basis net; window is; 1534 unique entries; 461 signals tested; BH-FDR q=0.05 threshold p<=0.002603; 24 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | xs_max_anomaly_decile | numeric | Q5-Q1 +4.63 (rho +0.078) | n 1520, Q5 4.35 vs Q1 -0.28 | 2.32e-03 |
| 2 | xs_max_anomaly | numeric | Q5-Q1 +4.56 (rho +0.134) | n 1520, Q5 4.15 vs Q1 -0.41 | 1.54e-07 |
| 3 | po3_accum_range_pct | numeric | Q5-Q1 +4.36 (rho +0.123) | n 1534, Q5 3.82 vs Q1 -0.54 | 1.46e-06 |
| 4 | dxy_20d_pct_change | numeric | Q5-Q1 -4.22 (rho -0.124) | n 1534, Q5 -1.37 vs Q1 2.85 | 1.16e-06 |
| 5 | sector_weakest_rs | numeric | Q5-Q1 -4.07 (rho -0.168) | n 1534, Q5 -0.99 vs Q1 3.08 | 3.24e-11 |
| 6 | atr_pct | numeric | Q5-Q1 +3.99 (rho +0.107) | n 1534, Q5 3.60 vs Q1 -0.40 | 2.45e-05 |
| 7 | ppo_hist | numeric | Q5-Q1 +3.92 (rho +0.083) | n 1534, Q5 3.48 vs Q1 -0.44 | 1.12e-03 |
| 8 | stoch_d | numeric | Q5-Q1 +3.21 (rho +0.087) | n 1534, Q5 3.10 vs Q1 -0.11 | 6.23e-04 |
| 9 | bond_equity_20d_pct_change | numeric | Q5-Q1 +2.78 (rho +0.146) | n 1534, Q5 2.50 vs Q1 -0.28 | 8.71e-09 |
| 10 | is_january_extended | bool | +2.54 (T 3.06 vs F 0.51) | n 163/1371, WR 0.675 vs 0.519 | 1.20e-04 |
| 11 | ema_20_50_bearish | bool | +2.49 (T 1.00 vs F -1.49) | n 1399/135, WR 0.544 vs 0.444 | 5.95e-04 |
| 12 | ema_20_50_bullish | bool | -2.49 (T -1.49 vs F 1.00) | n 135/1399, WR 0.444 vs 0.544 | 5.95e-04 |
| 13 | rsi_2_extreme_ob | bool | -2.36 (T -0.42 vs F 1.94) | n 752/782, WR 0.493 vs 0.575 | 3.52e-04 |
| 14 | smc_fvg_bullish_active | bool | -2.35 (T -0.80 vs F 1.55) | n 499/1035, WR 0.485 vs 0.559 | 3.95e-05 |
| 15 | risk_on_regime_bond_signal | bool | -2.34 (T -0.71 vs F 1.63) | n 557/977, WR 0.440 vs 0.590 | 1.19e-04 |
| 16 | usd_strengthening | bool | -2.24 (T -0.70 vs F 1.54) | n 520/1014, WR 0.465 vs 0.571 | 1.74e-04 |
| 17 | vix_band_mid | bool | -2.19 (T -0.98 vs F 1.22) | n 302/1232, WR 0.470 vs 0.551 | 6.66e-04 |
| 18 | ppo_signal | numeric | Q5-Q1 -2.18 (rho -0.089) | n 1534, Q5 0.49 vs Q1 2.66 | 4.58e-04 |
| 19 | cot_gold_mmoney_pctile_3y | numeric | Q5-Q1 +2.03 (rho +0.121) | n 1534, Q5 2.11 vs Q1 0.08 | 2.04e-06 |
| 20 | psar_flip_up | bool | -1.99 (T -0.84 vs F 1.15) | n 284/1250, WR 0.500 vs 0.543 | 1.93e-03 |
| 21 | rsi_2 | numeric | Q5-Q1 -1.75 (rho -0.092) | n 1534, Q5 -0.83 vs Q1 0.93 | 2.91e-04 |
| 22 | stochrsi_d | numeric | Q5-Q1 +1.69 (rho +0.084) | n 1534, Q5 1.30 vs Q1 -0.39 | 9.51e-04 |
| 23 | pct_change_5d | numeric | Q5-Q1 -1.34 (rho -0.084) | n 1534, Q5 0.22 vs Q1 1.56 | 9.52e-04 |
| 24 | macd_12_26_9_signal | numeric | Q5-Q1 +0.04 (rho -0.087) | n 1534, Q5 1.74 vs Q1 1.70 | 6.47e-04 |
