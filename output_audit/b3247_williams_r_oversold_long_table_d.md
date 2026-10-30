_Rendered by scripts/table_d_render.py from output_audit/b3289_williams_r_oversold_long_step1_is_surface.json, output_audit/b3247_williams_r_oversold_breadth_net_long.json, all rows - commit 884d7e016, 2026-10-30T12:37Z (L803 build stamp)._

# TABLE D (OFFLINE FORM, unified) - williams_r_oversold step UNKNOWN (no readable run manifest recorded)

122 graded cells across 2 artifact(s); 2 in-sample-only artifact(s): holdout NOT read, no gates (B1608); npt excluded from ranking.
BASIS (S6-B3314) - b3289_williams_r_oversold_long_step1_is_surface.json: gross (not recorded - pre-S6-B3314 depth sweep, raw cube pnl); b3247_williams_r_oversold_breadth_net_long.json: net - MIXED BASES: a gross row and a net row are not comparable (net winsorizes and subtracts the round-trip cost from every trade, roster_core.net_pnl)
INVENTORY (one column per Table A row; '-' = breadth axis not applied, production behavior; MIXED design - a factorial row varies several axes at once, a sweep row one axis on the production base):
  - P1 below_ema_200 identity (SHORT trend leg): SHORT LEG ONLY - outside the long leg this table renders; graded in that leg's table
  - P2 cmf_negative level (SHORT leg): SHORT LEG ONLY - outside the long leg this table renders; graded in that leg's table
  - P3 cmf_positive level (LONG leg): TESTED at {0.0, 0.02, 0.05} (3 of 3 band levels)
  - P4 price_above_ema_200 identity (LONG trend leg): production span 200, band ['span 200'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P5 rsi_2 span (escape hatch): production 2, band [2] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P6 williams period: production 14, band [14] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P7 williams_r oversold threshold (LONG OR-arm): TESTED at {-80.0, -85.0, -90.0} (3 of 3 band levels)
  - P8 williams_r > -20 (SHORT OR-arm): SHORT LEG ONLY - outside the long leg this table renders; graded in that leg's table
  - P9 rsi_2 escape hatch (LONG OR-arm): TESTED at {3.0, 5.0} (2 of 2 band levels)
  - P10 rsi_2 escape hatch (SHORT OR-arm): SHORT LEG ONLY - outside the long leg this table renders; graded in that leg's table
  - P11 days_to_cover cap (borrow guard, SHORT leg): SHORT LEG ONLY - outside the long leg this table renders; graded in that leg's table
  - B1 cot_dow_commercials_pctile_3y: TESTED at {0.0513, 0.2564, 0.4487, 0.6474} (4 of 4 band levels)
  - B2 sector_weakest_rs: SHORT LEG ONLY - outside the long leg this table renders; graded in that leg's table
  - B3 vix_value: SHORT LEG ONLY - outside the long leg this table renders; graded in that leg's table
  - B4 xs_max_anomaly: SHORT LEG ONLY - outside the long leg this table renders; graded in that leg's table
  - B5 days_until_fomc: SHORT LEG ONLY - outside the long leg this table renders; graded in that leg's table
  - B6 cot_gold_commercials_net_pct: SHORT LEG ONLY - outside the long leg this table renders; graded in that leg's table
  - B7 po3_accum_range_pct: SHORT LEG ONLY - outside the long leg this table renders; graded in that leg's table
NULL PRICE - depth-surface null (18 of 18 cells graded, b3289_williams_r_oversold_long_step1_is_surface.json): best 0.592 vs q95 0.557, p 0.0396 (100 perms, SYNTHETIC)
NULL PRICE - breadth-grid null (1 of 1 axes graded, 100 non-npt cells, b3247_williams_r_oversold_breadth_net_long.json): best 1.171 vs q95 0.4898, p 0.0099 (100 perms, SYNTHETIC)
EPISODE (S6-B3315) - 12 of the 25 top-25 rows recording it put more than 0.5 of their IS trades in ONE month (the null shuffles magnitudes across fires and cannot see this; every row's share is in its artifact's 'episode' field): rank 1: 2024-01 holds 0.516 of 188 (without it n 91, IS sharpe 0.357); rank 2: 2024-01 holds 0.516 of 188 (without it n 91, IS sharpe 0.487); rank 3: 2024-01 holds 0.516 of 188 (without it n 91, IS sharpe 0.51); rank 4: 2024-01 holds 0.516 of 188 (without it n 91, IS sharpe 0.51); rank 5: 2024-01 holds 0.516 of 188 (without it n 91, IS sharpe 0.512); rank 6: 2024-01 holds 0.516 of 188 (without it n 91, IS sharpe 0.055); rank 8: 2024-01 holds 0.516 of 188 (without it n 91, IS sharpe 0.241); rank 13: 2024-01 holds 0.516 of 188 (without it n 91, IS sharpe 0.217); rank 18: 2024-01 holds 0.516 of 188 (without it n 91, IS sharpe -0.04); rank 19: 2024-01 holds 0.516 of 188 (without it n 91, IS sharpe 0.027); rank 21: 2024-01 holds 0.516 of 188 (without it n 91, IS sharpe -0.1); rank 24: 2024-01 holds 0.516 of 188 (without it n 91, IS sharpe -0.37)
DEPTH SURFACE - an offline_level_sweep surface stores each cell's BEST exit only and no lower bound, so its rows show that exit with IS ci_lo blank and rank after every row that records one (L580; S6-B3316)
TIER - DEEP n>=100, MID 30-99, THIN 10-29. Rank improves monotonically as evidence thins, so RANK IS NOT TRUSTWORTHINESS and the depth band sits beside the ranking key deliberately.
SORT - is_ci_lo DESCENDING, then IS n descending, nothing filtered (runbook section 7.5). Ranking on Sharpe is the REJECTED order: a higher Sharpe can carry a NEGATIVE lower bound (L455).
EXITS - Step 1 picks each cell's exit by SHARPE alone (B1605) while this table RANKS by is_ci_lo. Two objectives, so a leading row can carry the exit that won on Sharpe.
Showing top 118 of 118 ranked cells.

| rank | below_ema_200 identity (SHORT trend leg) | cmf_negative level (SHORT leg) | cmf_positive level (LONG leg) | price_above_ema_200 identity (LONG trend leg) | rsi_2 span (escape hatch) | williams period | williams_r oversold threshold (LONG OR-arm) | williams_r > -20 (SHORT OR-arm) | rsi_2 escape hatch (LONG OR-arm) | rsi_2 escape hatch (SHORT OR-arm) | days_to_cover cap (borrow guard, SHORT leg) | cot_dow_commercials_pctile_3y | sector_weakest_rs | vix_value | xs_max_anomaly | days_until_fomc | cot_gold_commercials_net_pct | po3_accum_range_pct | exit | IS sharpe | IS ci_lo | IS n | full n | tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | reverse_signal | 1.171 | 0.595 | 188 | 188 | DEEP |
| 2 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | class_time_stop | 0.991 | 0.526 | 188 | 188 | DEEP |
| 3 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | regime_flip | 1.006 | 0.489 | 188 | 188 | DEEP |
| 4 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | time_stop_20d | 1.006 | 0.489 | 188 | 188 | DEEP |
| 5 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | breakeven_plus_trail | 0.746 | 0.392 | 188 | 188 | DEEP |
| 6 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | earnings_blackout | 0.620 | 0.321 | 188 | 188 | DEEP |
| 7 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | class_time_stop | 0.636 | 0.314 | 380 | 387 | DEEP |
| 8 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | hybrid_50pct_target | 0.592 | 0.314 | 188 | 188 | DEEP |
| 9 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | reverse_signal | 0.699 | 0.312 | 380 | 387 | DEEP |
| 10 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | regime_flip | 0.655 | 0.295 | 380 | 387 | DEEP |
| 11 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | time_stop_20d | 0.655 | 0.295 | 380 | 387 | DEEP |
| 12 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | breakeven_plus_trail | 0.527 | 0.253 | 380 | 387 | DEEP |
| 13 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | time_stop_10d | 0.957 | 0.239 | 188 | 188 | DEEP |
| 14 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | breakeven_plus_trail | 0.316 | 0.114 | 737 | 1025 | DEEP |
| 15 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | hybrid_50pct_target | 0.316 | 0.113 | 380 | 387 | DEEP |
| 16 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | breakeven_plus_trail | 0.327 | 0.097 | 575 | 682 | DEEP |
| 17 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | trailing_15pct | 0.213 | 0.076 | 380 | 387 | DEEP |
| 18 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | trailing_10pct | 0.332 | 0.063 | 188 | 188 | DEEP |
| 19 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | trailing_15pct | 0.245 | 0.054 | 188 | 188 | DEEP |
| 20 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | earnings_blackout | 0.259 | 0.053 | 380 | 387 | DEEP |
| 21 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | trailing_5pct | 0.484 | 0.008 | 188 | 188 | DEEP |
| 22 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | trailing_15pct | 0.101 | -0.003 | 737 | 1025 | DEEP |
| 23 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | trailing_15pct | 0.083 | -0.035 | 575 | 682 | DEEP |
| 24 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | fixed_4r_2r | 0.484 | -0.039 | 188 | 188 | DEEP |
| 25 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | earnings_blackout | 0.104 | -0.044 | 737 | 1025 | DEEP |
| 26 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | r_multiple_3r | 0.708 | -0.058 | 188 | 188 | DEEP |
| 27 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | earnings_blackout | 0.100 | -0.067 | 575 | 682 | DEEP |
| 28 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | trailing_10pct | 0.122 | -0.082 | 380 | 387 | DEEP |
| 29 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | atr_trail_2x | 0.509 | -0.098 | 188 | 188 | DEEP |
| 30 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | hybrid_50pct_target | 0.053 | -0.099 | 737 | 1025 | DEEP |
| 31 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | hybrid_50pct_target | 0.066 | -0.106 | 575 | 682 | DEEP |
| 32 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | regime_flip | 0.172 | -0.118 | 575 | 682 | DEEP |
| 33 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | time_stop_20d | 0.172 | -0.118 | 575 | 682 | DEEP |
| 34 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | break_even_at_1r | 0.396 | -0.148 | 188 | 188 | DEEP |
| 35 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | time_stop_10d | 0.355 | -0.149 | 380 | 387 | DEEP |
| 36 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | class_time_stop | 0.066 | -0.193 | 575 | 682 | DEEP |
| 37 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | r_multiple_2r | 0.740 | -0.193 | 188 | 188 | DEEP |
| 38 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | trailing_10pct | -0.058 | -0.214 | 737 | 1025 | DEEP |
| 39 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | trailing_10pct | -0.041 | -0.215 | 575 | 682 | DEEP |
| 40 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | break_even_at_1r | 0.193 | -0.229 | 380 | 387 | DEEP |
| 41 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | reverse_signal | 0.013 | -0.256 | 737 | 1025 | DEEP |
| 42 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | reverse_signal | 0.050 | -0.256 | 575 | 682 | DEEP |
| 43 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | r_multiple_2r | 0.406 | -0.261 | 380 | 387 | DEEP |
| 44 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | r_multiple_3r | 0.297 | -0.262 | 380 | 387 | DEEP |
| 45 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | class_time_stop | -0.034 | -0.263 | 737 | 1025 | DEEP |
| 46 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | trailing_5pct | 0.086 | -0.277 | 380 | 387 | DEEP |
| 47 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | regime_flip | -0.030 | -0.286 | 737 | 1025 | DEEP |
| 48 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | time_stop_20d | -0.030 | -0.286 | 737 | 1025 | DEEP |
| 49 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | atr_trail_2x | 0.095 | -0.342 | 380 | 387 | DEEP |
| 50 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | fixed_4r_2r | 0.029 | -0.355 | 380 | 387 | DEEP |
| 51 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | trailing_5pct | -0.126 | -0.434 | 575 | 682 | DEEP |
| 52 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | time_stop_10d | -0.087 | -0.448 | 737 | 1025 | DEEP |
| 53 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | time_stop_10d | -0.066 | -0.475 | 575 | 682 | DEEP |
| 54 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | r_multiple_3r | -0.025 | -0.481 | 575 | 682 | DEEP |
| 55 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | atr_trail_2x | -0.128 | -0.483 | 575 | 682 | DEEP |
| 56 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | break_even_at_1r | -0.125 | -0.491 | 575 | 682 | DEEP |
| 57 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | r_multiple_3r | -0.130 | -0.546 | 737 | 1025 | DEEP |
| 58 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | r_multiple_2r | -0.018 | -0.55 | 575 | 682 | DEEP |
| 59 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | fixed_4r_2r | -0.264 | -0.577 | 575 | 682 | DEEP |
| 60 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | fixed_4r_2r | -0.307 | -0.587 | 737 | 1025 | DEEP |
| 61 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | atr_trail_2x | -0.282 | -0.603 | 737 | 1025 | DEEP |
| 62 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | trailing_5pct | -0.323 | -0.607 | 737 | 1025 | DEEP |
| 63 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | break_even_at_1r | -0.309 | -0.648 | 737 | 1025 | DEEP |
| 64 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | r_multiple_2r | -0.178 | -0.664 | 737 | 1025 | DEEP |
| 65 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | chandelier_3x | -1.069 | -1.913 | 380 | 387 | DEEP |
| 66 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | chandelier_3x | -1.332 | -2.045 | 575 | 682 | DEEP |
| 67 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | chandelier_3x | -1.455 | -2.101 | 737 | 1025 | DEEP |
| 68 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | atr_trail_vix_conditional | -1.710 | -2.438 | 380 | 387 | DEEP |
| 69 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | atr_trail_vix_conditional | -1.867 | -2.455 | 575 | 682 | DEEP |
| 70 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | chandelier_3x | -1.360 | -2.556 | 188 | 188 | DEEP |
| 71 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | multi_tier_partial | -1.535 | -2.711 | 188 | 188 | DEEP |
| 72 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | atr_trail_vix_conditional | -2.322 | -2.866 | 737 | 1025 | DEEP |
| 73 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | multi_tier_partial | -2.122 | -2.944 | 380 | 387 | DEEP |
| 74 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | ma_exit_ema9 | -1.105 | -2.979 | 188 | 188 | DEEP |
| 75 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | ma_exit_ema9 | -1.968 | -3.003 | 575 | 682 | DEEP |
| 76 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | mfe_lockin_trail | -1.955 | -3.15 | 188 | 188 | DEEP |
| 77 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | ma_exit_ema9 | -2.251 | -3.187 | 737 | 1025 | DEEP |
| 78 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | multi_tier_partial | -2.633 | -3.314 | 575 | 682 | DEEP |
| 79 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | ma_exit_ema9 | -2.027 | -3.316 | 380 | 387 | DEEP |
| 80 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | mfe_lockin_trail | -2.557 | -3.399 | 380 | 387 | DEEP |
| 81 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | smart_money_reversal | -2.235 | -3.415 | 188 | 188 | DEEP |
| 82 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | smart_money_reversal | -2.606 | -3.43 | 380 | 387 | DEEP |
| 83 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | multi_tier_partial | -2.843 | -3.459 | 737 | 1025 | DEEP |
| 84 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | atr_trail_1x | -2.670 | -3.491 | 380 | 387 | DEEP |
| 85 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | atr_trail_mae_conditional | -2.670 | -3.491 | 380 | 387 | DEEP |
| 86 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | atr_trail_1x | -2.333 | -3.504 | 188 | 188 | DEEP |
| 87 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | atr_trail_mae_conditional | -2.333 | -3.504 | 188 | 188 | DEEP |
| 88 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | mfe_lockin_trail | -3.008 | -3.702 | 575 | 682 | DEEP |
| 89 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | smart_money_reversal | -3.045 | -3.727 | 575 | 682 | DEEP |
| 90 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | atr_trail_1x | -3.076 | -3.753 | 575 | 682 | DEEP |
| 91 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | atr_trail_mae_conditional | -3.076 | -3.753 | 575 | 682 | DEEP |
| 92 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | atr_trail_vix_conditional | -2.758 | -3.958 | 188 | 188 | DEEP |
| 93 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | mfe_lockin_trail | -3.368 | -3.996 | 737 | 1025 | DEEP |
| 94 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | smart_money_reversal | -3.421 | -4.04 | 737 | 1025 | DEEP |
| 95 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | atr_trail_1x | -3.444 | -4.059 | 737 | 1025 | DEEP |
| 96 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | atr_trail_mae_conditional | -3.444 | -4.059 | 737 | 1025 | DEEP |
| 97 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.2564 | - | - | - | - | - | - | smc_mitigation_zone | -4.168 | -5.392 | 380 | 387 | DEEP |
| 98 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.4487 | - | - | - | - | - | - | smc_mitigation_zone | -4.690 | -5.696 | 575 | 682 | DEEP |
| 99 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.6474 | - | - | - | - | - | - | smc_mitigation_zone | -5.068 | -5.972 | 737 | 1025 | DEEP |
| 100 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80 | -20 | 5 | 95 | 5.0 | <=0.0513 | - | - | - | - | - | - | smc_mitigation_zone | -5.028 | -6.846 | 188 | 188 | DEEP |
| 101 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80.0 | -20 | 5.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.334 |  | 922 | - | DEEP |
| 102 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -80.0 | -20 | 3.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.327 |  | 823 | - | DEEP |
| 103 | span 200 | 0.0 | 0.02 | span 200 | 2 | 14 | -80.0 | -20 | 5.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.342 |  | 812 | - | DEEP |
| 104 | span 200 | 0.0 | 0.02 | span 200 | 2 | 14 | -80.0 | -20 | 3.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.337 |  | 718 | - | DEEP |
| 105 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -85.0 | -20 | 5.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.321 |  | 718 | - | DEEP |
| 106 | span 200 | 0.0 | 0.05 | span 200 | 2 | 14 | -80.0 | -20 | 5.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.416 |  | 651 | - | DEEP |
| 107 | span 200 | 0.0 | 0.02 | span 200 | 2 | 14 | -85.0 | -20 | 5.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.341 |  | 635 | - | DEEP |
| 108 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -85.0 | -20 | 3.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.285 |  | 600 | - | DEEP |
| 109 | span 200 | 0.0 | 0.05 | span 200 | 2 | 14 | -80.0 | -20 | 3.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.411 |  | 568 | - | DEEP |
| 110 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -90.0 | -20 | 5.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.437 |  | 546 | - | DEEP |
| 111 | span 200 | 0.0 | 0.02 | span 200 | 2 | 14 | -85.0 | -20 | 3.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.305 |  | 522 | - | DEEP |
| 112 | span 200 | 0.0 | 0.05 | span 200 | 2 | 14 | -85.0 | -20 | 5.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.433 |  | 506 | - | DEEP |
| 113 | span 200 | 0.0 | 0.02 | span 200 | 2 | 14 | -90.0 | -20 | 5.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.435 |  | 484 | - | DEEP |
| 114 | span 200 | 0.0 | 0.05 | span 200 | 2 | 14 | -85.0 | -20 | 3.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.409 |  | 409 | - | DEEP |
| 115 | span 200 | 0.0 | 0.0 | span 200 | 2 | 14 | -90.0 | -20 | 3.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.474 |  | 395 | - | DEEP |
| 116 | span 200 | 0.0 | 0.05 | span 200 | 2 | 14 | -90.0 | -20 | 5.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.526 |  | 387 | - | DEEP |
| 117 | span 200 | 0.0 | 0.02 | span 200 | 2 | 14 | -90.0 | -20 | 3.0 | 95 | 5.0 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.475 |  | 340 | - | DEEP |
| 118 | span 200 | 0.0 | 0.05 | span 200 | 2 | 14 | -90.0 | -20 | 3.0 | 95 | 5.0 | - | - | - | - | - | - | - | time_stop_10d | 0.592 |  | 267 | - | DEEP |
