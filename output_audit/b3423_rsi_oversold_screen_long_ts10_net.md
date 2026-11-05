# COMPANION-SIGNAL SCREEN - rsi_oversold (exact names)

exit time_stop_10d; basis net; window is; 693 unique entries; 364 signals tested; BH-FDR q=0.05 threshold p<=0.0013736; 10 survivors. A SCREEN, not a gate (hypothesis list for producer design).

| rank | signal | kind | effect (pnl) | detail | p |
|---|---|---|---|---|---|
| 1 | cot_ndx_mmoney_pctile_3y | numeric | Q5-Q1 +4.30 (rho +0.164) | n 693, Q5 1.65 vs Q1 -2.65 | 1.44e-05 |
| 2 | cot_rut_commercials_net_pct | numeric | Q5-Q1 -4.10 (rho -0.223) | n 693, Q5 -3.81 vs Q1 0.29 | 3.15e-09 |
| 3 | cot_dow_commercials_pctile_3y | numeric | Q5-Q1 -2.96 (rho -0.197) | n 693, Q5 -1.93 vs Q1 1.04 | 1.74e-07 |
| 4 | cot_dow_commercials_net_pct | numeric | Q5-Q1 -2.59 (rho -0.181) | n 693, Q5 -1.95 vs Q1 0.64 | 1.70e-06 |
| 5 | cot_ndx_commercials_net_pct | numeric | Q5-Q1 -2.56 (rho -0.127) | n 693, Q5 -1.53 vs Q1 1.03 | 7.92e-04 |
| 6 | is_january | bool | +2.06 (T 1.10 vs F -0.96) | n 134/559, WR 0.604 vs 0.429 | 2.21e-04 |
| 7 | is_january_extended | bool | +2.03 (T 1.05 vs F -0.98) | n 141/552, WR 0.596 vs 0.429 | 1.63e-04 |
| 8 | avwap_20high_loss_recent_3d | bool | -1.80 (T -1.84 vs F -0.04) | n 199/492, WR 0.367 vs 0.502 | 2.67e-04 |
| 9 | sector_strongest_rs | numeric | Q5-Q1 -1.78 (rho -0.134) | n 693, Q5 -2.24 vs Q1 -0.46 | 4.08e-04 |
| 10 | cot_dxy_commercials_pctile_3y | numeric | Q5-Q1 +1.74 (rho +0.130) | n 693, Q5 -0.10 vs Q1 -1.84 | 6.25e-04 |
