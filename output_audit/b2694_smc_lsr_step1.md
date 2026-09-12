# TABLE D (OFFLINE FORM, standard shape) - smc_liquidity_sweep_reversal Step-1

598 graded cells; reproduction 2933 fires = b2690; holdout NOT read; no gates (B1608); npt excluded from ranking.
BANDS SWEPT - depth: leg {both, long, short} x confirmation_arm {either(prod), choch_only, bos_only}; breadth numeric (retention quantiles derived at grid time): atr_pct in {2.2554, 2.8846, 3.5642, 4.757}; bb_20_20_bandwidth in {0.103, 0.1431, 0.1865, 0.2586}; vp_close_near_poc_pct in {0.0304, 0.0605, 0.0982, 0.1479}; breadth boolean: bullish_engulfing {True, long leg only}, gap_up_2pct {False}. '-' = axis not applied in that cell (production behavior); one-at-a-time design, so each row constrains at most one breadth axis.
Numeric-breadth null: best 0.284 vs q95 0.408, p 0.2079 (100 perms, SYNTHETIC).

| rank | leg | confirmation_arm | monthly_momentum_6m | bb_20_20_bandwidth | vp_close_near_poc_pct | atr_pct | bullish_engulfing | gap_up_2pct | exit | IS sharpe | IS ci_lo | IS n | full n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | both | either | - | - | - | - | True(long) | - | class_time_stop | 2.078 | 1.474 | 111 | 129 |
| 2 | both | either | - | - | - | - | True(long) | - | regime_flip | 1.777 | 1.08 | 111 | 129 |
| 3 | both | either | - | - | - | - | True(long) | - | time_stop_20d | 1.777 | 1.08 | 111 | 129 |
| 4 | both | either | - | - | - | - | True(long) | - | earnings_blackout | 1.493 | 1.068 | 111 | 129 |
| 5 | both | either | - | - | - | - | True(long) | - | fixed_4r_2r | 1.426 | 0.904 | 111 | 129 |
| 6 | long | choch_only | - | - | - | - | - | - | r_multiple_3r | 1.100 | -2.135 | 10 | 12 |
| 7 | long | choch_only | - | - | - | - | - | - | smc_mitigation_zone | 1.099 | -5.644 | 10 | 12 |
| 8 | both | either | - | - | - | - | True(long) | - | hybrid_50pct_target | 1.064 | 0.729 | 111 | 129 |
| 9 | both | either | - | - | - | - | True(long) | - | breakeven_plus_trail | 1.010 | 0.647 | 111 | 129 |
| 10 | both | either | - | - | - | - | True(long) | - | atr_trail_2x | 0.954 | 0.313 | 111 | 129 |
| 11 | both | either | - | - | - | - | True(long) | - | time_stop_10d | 0.918 | -0.011 | 111 | 129 |
| 12 | both | either | - | - | - | - | True(long) | - | trailing_10pct | 0.754 | 0.408 | 111 | 129 |
| 13 | both | either | - | - | - | - | True(long) | - | trailing_15pct | 0.670 | 0.419 | 111 | 129 |
| 14 | long | choch_only | - | - | - | - | - | - | r_multiple_2r | 0.650 | -2.948 | 10 | 12 |
| 15 | long | bos_only | - | - | - | - | - | - | breakeven_plus_trail | 0.612 | 0.446 | 892 | 1118 |
| 16 | long | either | - | - | - | - | - | - | breakeven_plus_trail | 0.607 | 0.442 | 901 | 1128 |
| 17 | long | bos_only | - | - | - | - | - | - | earnings_blackout | 0.522 | 0.385 | 892 | 1118 |
| 18 | long | either | - | - | - | - | - | - | earnings_blackout | 0.520 | 0.384 | 901 | 1128 |
| 19 | both | choch_only | - | - | - | - | - | - | r_multiple_2r | 0.505 | -1.453 | 41 | 52 |
| 20 | short | choch_only | - | - | - | - | - | - | r_multiple_2r | 0.454 | -1.88 | 31 | 40 |
| 21 | long | bos_only | - | - | - | - | - | - | class_time_stop | 0.447 | 0.256 | 892 | 1118 |
| 22 | long | either | - | - | - | - | - | - | class_time_stop | 0.445 | 0.255 | 901 | 1128 |
| 23 | long | either | - | - | - | - | - | - | regime_flip | 0.436 | 0.205 | 901 | 1128 |
| 24 | long | either | - | - | - | - | - | - | time_stop_20d | 0.436 | 0.205 | 901 | 1128 |
| 25 | long | bos_only | - | - | - | - | - | - | regime_flip | 0.436 | 0.203 | 892 | 1118 |
