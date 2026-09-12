# TABLE D ADDENDUM (OFFLINE FORM, standard shape) - smc_liquidity_sweep_reversal Step-1: monthly_momentum_6m re-sweep

104 graded cells; reproduction 2933 fires = b2690; holdout NOT read; no gates (B1608); npt excluded from ranking.
WIDENED COVERAGE RULE (owner option (b) 2026-09-12): coverage 0.942 of IS fires - the 5.8% uncovered gap is EXCLUDED from both arms; the verdict binds the covered subpopulation only. This axis was COVERAGE-SKIPPED in b2694 (0.942 < 0.98) and is swept here on the owner's word.
BANDS SWEPT - breadth numeric (retention quantiles on covered IS fires, derived at grid time): monthly_momentum_6m in {-0.2167, -0.1122, -0.0205, 0.0871}. '-' = axis not applied (production behavior); single-axis design.
Single-axis null: best 0.486 vs q95 0.235, p 0.0099 (100 perms, SYNTHETIC).

| rank | leg | confirmation_arm | monthly_momentum_6m | bb_20_20_bandwidth | vp_close_near_poc_pct | atr_pct | bullish_engulfing | gap_up_2pct | exit | IS sharpe | IS ci_lo | IS n | full n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | both | either | >=0.0871 | - | - | - | - | - | breakeven_plus_trail | 0.486 | 0.222 | 445 | 581 |
| 2 | both | either | >=-0.1122 | - | - | - | - | - | breakeven_plus_trail | 0.475 | 0.327 | 1335 | 1710 |
| 3 | both | either | >=-0.0205 | - | - | - | - | - | breakeven_plus_trail | 0.452 | 0.269 | 891 | 1146 |
| 4 | both | either | >=-0.2167 | - | - | - | - | - | breakeven_plus_trail | 0.397 | 0.265 | 1780 | 2262 |
| 5 | both | either | >=0.0871 | - | - | - | - | - | earnings_blackout | 0.397 | 0.206 | 445 | 581 |
| 6 | both | either | >=0.0871 | - | - | - | - | - | class_time_stop | 0.387 | 0.118 | 445 | 581 |
| 7 | both | either | >=-0.0205 | - | - | - | - | - | class_time_stop | 0.359 | 0.168 | 891 | 1146 |
| 8 | both | either | >=-0.0205 | - | - | - | - | - | earnings_blackout | 0.346 | 0.211 | 891 | 1146 |
| 9 | both | either | >=-0.0205 | - | - | - | - | - | regime_flip | 0.339 | 0.106 | 891 | 1146 |
| 10 | both | either | >=-0.0205 | - | - | - | - | - | time_stop_20d | 0.339 | 0.106 | 891 | 1146 |
| 11 | both | either | >=0.0871 | - | - | - | - | - | regime_flip | 0.338 | 0.009 | 445 | 581 |
| 12 | both | either | >=0.0871 | - | - | - | - | - | time_stop_20d | 0.338 | 0.009 | 445 | 581 |
| 13 | both | either | >=-0.1122 | - | - | - | - | - | earnings_blackout | 0.302 | 0.192 | 1335 | 1710 |
| 14 | both | either | >=-0.1122 | - | - | - | - | - | class_time_stop | 0.286 | 0.13 | 1335 | 1710 |
| 15 | both | either | >=-0.0205 | - | - | - | - | - | hybrid_50pct_target | 0.245 | 0.107 | 891 | 1146 |
| 16 | both | either | >=-0.1122 | - | - | - | - | - | hybrid_50pct_target | 0.239 | 0.126 | 1335 | 1710 |
| 17 | both | either | >=0.0871 | - | - | - | - | - | hybrid_50pct_target | 0.238 | 0.04 | 445 | 581 |
| 18 | both | either | >=-0.0205 | - | - | - | - | - | time_stop_10d | 0.233 | -0.095 | 891 | 1146 |
| 19 | both | either | >=-0.1122 | - | - | - | - | - | regime_flip | 0.218 | 0.028 | 1335 | 1710 |
| 20 | both | either | >=-0.1122 | - | - | - | - | - | time_stop_20d | 0.218 | 0.028 | 1335 | 1710 |
| 21 | both | either | >=0.0871 | - | - | - | - | - | time_stop_10d | 0.204 | -0.259 | 445 | 581 |
| 22 | both | either | >=-0.2167 | - | - | - | - | - | earnings_blackout | 0.177 | 0.082 | 1780 | 2262 |
| 23 | both | either | >=-0.2167 | - | - | - | - | - | hybrid_50pct_target | 0.151 | 0.049 | 1780 | 2262 |
| 24 | both | either | >=0.0871 | - | - | - | - | - | trailing_15pct | 0.140 | -0.009 | 445 | 581 |
| 25 | both | either | >=-0.1122 | - | - | - | - | - | fixed_4r_2r | 0.138 | -0.041 | 1335 | 1710 |
