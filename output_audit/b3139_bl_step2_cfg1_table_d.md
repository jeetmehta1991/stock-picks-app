# TABLE D (OFFLINE FORM, unified) - bollinger_lower Step-1

24 graded cells across 4 artifact(s); holdout NOT read; no gates (B1608); npt excluded from ranking.
INVENTORY (one column per Table A row; '-' = breadth axis not applied, production behavior; one-at-a-time design):
  - P1 bb (period, k, recency) identity - lower reclaim: production 20/2.0/3, band ['20/2.0/3'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P2 bb identity - upper reclaim (mirror): production 20/2.0/3, band ['20/2.0/3'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P3 ema span (below_ema_N, SHORT leg): production 200, free band [200] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - P4 ema span (price_above_ema_N, LONG leg): production 200, free band [200] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - P5 rsi span (slow): production 14, band [14] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P6 rsi span (fast escape-hatch): production 2, band [2] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P7 vix_band_high flag (upper edge feed): production edge per P8, band ['edge per P8'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P8 vix band edges on persisted vix_percentile: production 1/3,2/3, free band ['1/3,2/3', '0.25,0.75'] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - P9 adx ceiling: production 35, free band [35, 27.51, 23.96, 20.976, 17.69] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - P10 days_to_cover cap (borrow guard, SHORT leg): production 5.0, band ['5.0'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P11 VIX-conditional rsi edges: production B1147 set (40/60, 45/55, 50/50), free band ['B1147 set (40/60, 45/55, 50/50)', 'edges 5 tighter per band'] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - B1 cot_rut_commercials_net_pct: production not gated, free band ['q20', 'q40', 'q60', 'q80'] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - B2 defensive_leadership: production not gated, free band ['require_true'] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - B3 macd_12_26_9_line: production not gated, free band ['q20', 'q40', 'q60', 'q80'] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - B4 dc20_new_high: production not gated, free band ['require_false'] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - B5 pct_from_vwap: production not gated, free band ['q20', 'q40', 'q60', 'q80'] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - B7 bb_20_15_pctb: production not gated, free band ['q20', 'q40', 'q60', 'q80'] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - B8 bb_10_20_pctb: production not gated, free band ['q20', 'q40', 'q60', 'q80'] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - B6 institutional_new_positions: production not gated, free band ['require_true'] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
TIER - DEEP n>=100, MID 30-99, THIN 10-29. Rank improves monotonically as evidence thins, so RANK IS NOT TRUSTWORTHINESS and the depth band sits beside the ranking key deliberately.
SORT - is_ci_lo DESCENDING, then IS n descending, nothing filtered (runbook section 7.5). Ranking on Sharpe is the REJECTED order: a higher Sharpe can carry a NEGATIVE lower bound (L455).
EXITS - Step 1 picks each cell's exit by SHARPE alone (B1605) while this table RANKS by is_ci_lo. Two objectives, so a leading row can carry the exit that won on Sharpe.
Showing top 24 of 24 ranked cells.

| rank | bb (period, k, recency) identity - lower reclaim | bb identity - upper reclaim (mirror) | ema span (below_ema_N, SHORT leg) | ema span (price_above_ema_N, LONG leg) | rsi span (slow) | rsi span (fast escape-hatch) | vix_band_high flag (upper edge feed) | vix band edges on persisted vix_percentile | adx ceiling | days_to_cover cap (borrow guard, SHORT leg) | VIX-conditional rsi edges | cot_rut_commercials_net_pct | defensive_leadership | macd_12_26_9_line | dc20_new_high | pct_from_vwap | bb_20_15_pctb | bb_10_20_pctb | institutional_new_positions | exit | IS sharpe | IS ci_lo | IS n | full n | tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | breakeven_plus_trail | 0.694 | 0.554 | 1272 | 1737 | DEEP |
| 2 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | earnings_blackout | 0.574 | 0.46 | 1272 | 1737 | DEEP |
| 3 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | regime_flip | 0.632 | 0.411 | 1272 | 1737 | DEEP |
| 4 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | reverse_signal | 0.547 | 0.404 | 1272 | 1737 | DEEP |
| 5 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | fixed_4r_2r | 0.538 | 0.363 | 1272 | 1737 | DEEP |
| 6 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | hybrid_50pct_target | 0.472 | 0.359 | 1272 | 1737 | DEEP |
| 7 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | time_stop_10d | 0.543 | 0.267 | 1272 | 1737 | DEEP |
| 8 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | atr_trail_2x | 0.471 | 0.253 | 1272 | 1737 | DEEP |
| 9 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | time_stop_20d | 0.447 | 0.251 | 1272 | 1737 | DEEP |
| 10 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | trailing_15pct | 0.268 | 0.183 | 1272 | 1737 | DEEP |
| 11 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | next_pivot_target | 0.430 | 0.149 | 1272 | 1737 | DEEP |
| 12 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | trailing_10pct | 0.254 | 0.132 | 1272 | 1737 | DEEP |
| 13 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | break_even_at_1r | -0.026 | -0.251 | 1272 | 1737 | DEEP |
| 14 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | atr_trail_vix_conditional | -0.003 | -0.29 | 1272 | 1737 | DEEP |
| 15 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | r_multiple_3r | -0.122 | -0.422 | 1272 | 1737 | DEEP |
| 16 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | trailing_5pct | -0.324 | -0.554 | 1272 | 1737 | DEEP |
| 17 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | r_multiple_2r | -0.293 | -0.656 | 1272 | 1737 | DEEP |
| 18 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | class_time_stop | -0.456 | -0.783 | 1272 | 1737 | DEEP |
| 19 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | chandelier_3x | -0.566 | -0.907 | 1272 | 1737 | DEEP |
| 20 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | ma_exit_ema9 | -0.903 | -1.309 | 1272 | 1737 | DEEP |
| 21 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | atr_trail_1x | -2.612 | -3.054 | 1272 | 1737 | DEEP |
| 22 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | multi_tier_partial | -2.617 | -3.072 | 1272 | 1737 | DEEP |
| 23 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | mfe_lockin_trail | -3.352 | -3.817 | 1272 | 1737 | DEEP |
| 24 | 20/2.0/3 | 20/2.0/3 | 200 | 200 | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | - | - | - | smc_mitigation_zone | -4.270 | -4.92 | 1272 | 1737 | DEEP |
