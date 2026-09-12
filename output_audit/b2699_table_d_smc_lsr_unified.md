# TABLE D (OFFLINE FORM, unified) - smc_liquidity_sweep_reversal Step-1

702 graded cells across 2 artifact(s); reproduction 2933 fires; holdout NOT read; no gates (B1608); npt excluded from ranking.
INVENTORY (one column per Table A row; '-' = breadth axis not applied, production behavior; one-at-a-time design):
  - P1 swing_length: production 20, band [5, 10, 20, 30, 50] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P2 liquidity_range_pct: production 0.01, band [0.005, 0.01, 0.02] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P3 event_recency_bars: production 90, band [20, 45, 90] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P4 confirmation_arm: TESTED at {either, choch_only, bos_only}
  - P5 leg: TESTED at {long, short}
  - B1 monthly_momentum_6m: TESTED at {-0.0205, -0.1122, -0.2167, 0.0871} under WIDENED COVERAGE 0.942 (owner option (b); 5.8% gap excluded from both arms - verdict binds the covered subpopulation only)
  - B2 bb_20_20_bandwidth: TESTED at {0.103, 0.1431, 0.1865, 0.2586}
  - B3 vp_close_near_poc_pct: TESTED at {0.0304, 0.0605, 0.0982, 0.1479}
  - B4 atr_pct: TESTED at {2.2554, 2.8846, 3.5642, 4.757}
  - B5 bullish_engulfing: TESTED at {True(long)}
  - B6 gap_up_2pct: TESTED at {False}
NULL PRICE - numeric-breadth null (3-of-4 axes swept in b2694_smc_lsr_step1.json): best 0.284 vs q95 0.408, p 0.2079 (100 perms, SYNTHETIC)
NULL PRICE - single-axis null (monthly_momentum_6m, b2698_momentum_resweep.json): best 0.486 vs q95 0.235, p 0.0099 (100 perms, SYNTHETIC)
DISPOSITION - monthly_momentum_6m was coverage-SKIPPED (coverage 0.942) and is SUPERSEDED by its re-sweep - rows integrated in this table
Showing top 25 of 675 ranked cells.

| rank | swing_length | liquidity_range_pct | event_recency_bars | confirmation_arm | leg | monthly_momentum_6m | bb_20_20_bandwidth | vp_close_near_poc_pct | atr_pct | bullish_engulfing | gap_up_2pct | exit | IS sharpe | IS ci_lo | IS n | full n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 0.01 | 90 | either | both | - | - | - | - | True(long) | - | class_time_stop | 2.078 | 1.474 | 111 | 129 |
| 2 | 20 | 0.01 | 90 | either | both | - | - | - | - | True(long) | - | regime_flip | 1.777 | 1.08 | 111 | 129 |
| 3 | 20 | 0.01 | 90 | either | both | - | - | - | - | True(long) | - | time_stop_20d | 1.777 | 1.08 | 111 | 129 |
| 4 | 20 | 0.01 | 90 | either | both | - | - | - | - | True(long) | - | earnings_blackout | 1.493 | 1.068 | 111 | 129 |
| 5 | 20 | 0.01 | 90 | either | both | - | - | - | - | True(long) | - | fixed_4r_2r | 1.426 | 0.904 | 111 | 129 |
| 6 | 20 | 0.01 | 90 | choch_only | long | - | - | - | - | - | - | r_multiple_3r | 1.100 | -2.135 | 10 | 12 |
| 7 | 20 | 0.01 | 90 | choch_only | long | - | - | - | - | - | - | smc_mitigation_zone | 1.099 | -5.644 | 10 | 12 |
| 8 | 20 | 0.01 | 90 | either | both | - | - | - | - | True(long) | - | hybrid_50pct_target | 1.064 | 0.729 | 111 | 129 |
| 9 | 20 | 0.01 | 90 | either | both | - | - | - | - | True(long) | - | breakeven_plus_trail | 1.010 | 0.647 | 111 | 129 |
| 10 | 20 | 0.01 | 90 | either | both | - | - | - | - | True(long) | - | atr_trail_2x | 0.954 | 0.313 | 111 | 129 |
| 11 | 20 | 0.01 | 90 | either | both | - | - | - | - | True(long) | - | time_stop_10d | 0.918 | -0.011 | 111 | 129 |
| 12 | 20 | 0.01 | 90 | either | both | - | - | - | - | True(long) | - | trailing_10pct | 0.754 | 0.408 | 111 | 129 |
| 13 | 20 | 0.01 | 90 | either | both | - | - | - | - | True(long) | - | trailing_15pct | 0.670 | 0.419 | 111 | 129 |
| 14 | 20 | 0.01 | 90 | choch_only | long | - | - | - | - | - | - | r_multiple_2r | 0.650 | -2.948 | 10 | 12 |
| 15 | 20 | 0.01 | 90 | bos_only | long | - | - | - | - | - | - | breakeven_plus_trail | 0.612 | 0.446 | 892 | 1118 |
| 16 | 20 | 0.01 | 90 | either | long | - | - | - | - | - | - | breakeven_plus_trail | 0.607 | 0.442 | 901 | 1128 |
| 17 | 20 | 0.01 | 90 | bos_only | long | - | - | - | - | - | - | earnings_blackout | 0.522 | 0.385 | 892 | 1118 |
| 18 | 20 | 0.01 | 90 | either | long | - | - | - | - | - | - | earnings_blackout | 0.520 | 0.384 | 901 | 1128 |
| 19 | 20 | 0.01 | 90 | choch_only | both | - | - | - | - | - | - | r_multiple_2r | 0.505 | -1.453 | 41 | 52 |
| 20 | 20 | 0.01 | 90 | either | both | >=0.0871 | - | - | - | - | - | breakeven_plus_trail | 0.486 | 0.222 | 445 | 581 |
| 21 | 20 | 0.01 | 90 | either | both | >=-0.1122 | - | - | - | - | - | breakeven_plus_trail | 0.475 | 0.327 | 1335 | 1710 |
| 22 | 20 | 0.01 | 90 | choch_only | short | - | - | - | - | - | - | r_multiple_2r | 0.454 | -1.88 | 31 | 40 |
| 23 | 20 | 0.01 | 90 | either | both | >=-0.0205 | - | - | - | - | - | breakeven_plus_trail | 0.452 | 0.269 | 891 | 1146 |
| 24 | 20 | 0.01 | 90 | bos_only | long | - | - | - | - | - | - | class_time_stop | 0.447 | 0.256 | 892 | 1118 |
| 25 | 20 | 0.01 | 90 | either | long | - | - | - | - | - | - | class_time_stop | 0.445 | 0.255 | 901 | 1128 |
