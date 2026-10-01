# TABLE D (OFFLINE FORM, unified) - bollinger_lower step UNKNOWN (no readable run manifest recorded)

598 graded cells across 1 artifact(s); holdout NOT read; no gates (B1608); npt excluded from ranking.
INVENTORY (one column per Table A row; '-' = breadth axis not applied, production behavior; one-at-a-time design):
  - P1 bb (period, k, recency) identity - lower reclaim: production 20/2.0/3, band ['20/2.0/3'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P2 bb identity - upper reclaim (mirror): production 20/2.0/3, band ['20/2.0/3'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P3 ema span (below_ema_N, SHORT leg): production 200, free band [200] - NOT TESTED in this campaign (offline-gradable; no rows varied it); run value UNKNOWN - no readable run_manifest.json arm env for this cube, production NOT assumed
  - P4 ema span (price_above_ema_N, LONG leg): production 200, free band [200] - NOT TESTED in this campaign (offline-gradable; no rows varied it); run value UNKNOWN - no readable run_manifest.json arm env for this cube, production NOT assumed
  - P5 rsi span (slow): production 14, band [14] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P6 rsi span (fast escape-hatch): production 2, band [2] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P7 vix_band_high flag (upper edge feed): production edge per P8, band ['edge per P8'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P8 vix band edges on persisted vix_percentile: production 1/3,2/3, free band ['1/3,2/3', '0.25,0.75'] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - P9 adx ceiling: production 35, free band [35, 27.51, 23.96, 20.976, 17.69] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - P10 days_to_cover cap (borrow guard, SHORT leg): production 5.0, band ['5.0'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P11 VIX-conditional rsi edges: production B1147 set (40/60, 45/55, 50/50), free band ['B1147 set (40/60, 45/55, 50/50)', 'edges 5 tighter per band'] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - B1 cot_rut_commercials_net_pct: TESTED at {-0.0203, 0.1035, 0.167, 0.3175} (4 of 4 band levels)
  - B2 defensive_leadership: TESTED at {1.0} (1 of 1 band levels)
  - B3 macd_12_26_9_line: TESTED at {0.1648, 0.4919, 1.1078, 2.1457} (4 of 4 band levels)
  - B4 dc20_new_high: TESTED at {0.0} (1 of 1 band levels)
  - B5 pct_from_vwap: TESTED at {-11.1146, -17.518, -26.113, -4.8914} (4 of 4 band levels)
  - B7 bb_20_15_pctb: TESTED at {0.9121, 0.998, 1.0573, 1.115} (4 of 4 band levels)
  - B8 bb_10_20_pctb: TESTED at {0.6757, 0.7363, 0.7866, 0.8339} (4 of 4 band levels)
  - B6 institutional_new_positions: TESTED at {1.0} (1 of 1 band levels)
NULL PRICE - numeric-breadth null (3-of-4 axes swept in b3139_bollinger_lower_breadth_net_short.json): best None vs q95 None, p None (200 perms, SYNTHETIC)
TIER - DEEP n>=100, MID 30-99, THIN 10-29. Rank improves monotonically as evidence thins, so RANK IS NOT TRUSTWORTHINESS and the depth band sits beside the ranking key deliberately.
SORT - is_ci_lo DESCENDING, then IS n descending, nothing filtered (runbook section 7.5). Ranking on Sharpe is the REJECTED order: a higher Sharpe can carry a NEGATIVE lower bound (L455).
EXITS - Step 1 picks each cell's exit by SHARPE alone (B1605) while this table RANKS by is_ci_lo. Two objectives, so a leading row can carry the exit that won on Sharpe.
Showing top 12 of 575 ranked cells.

| rank | bb (period, k, recency) identity - lower reclaim | bb identity - upper reclaim (mirror) | ema span (below_ema_N, SHORT leg) | ema span (price_above_ema_N, LONG leg) | rsi span (slow) | rsi span (fast escape-hatch) | vix_band_high flag (upper edge feed) | vix band edges on persisted vix_percentile | adx ceiling | days_to_cover cap (borrow guard, SHORT leg) | VIX-conditional rsi edges | cot_rut_commercials_net_pct | defensive_leadership | macd_12_26_9_line | dc20_new_high | pct_from_vwap | bb_20_15_pctb | bb_10_20_pctb | institutional_new_positions | exit | IS sharpe | IS ci_lo | IS n | full n | tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20/2.0/3 | 20/2.0/3 | UNKNOWN | UNKNOWN | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | 1.0 | - | - | - | - | - | - | time_stop_10d | 1.558 | 0.852 | 206 | 268 | DEEP |
| 2 | 20/2.0/3 | 20/2.0/3 | UNKNOWN | UNKNOWN | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | 1.0 | - | - | - | - | - | - | breakeven_plus_trail | 0.826 | 0.377 | 206 | 268 | DEEP |
| 3 | 20/2.0/3 | 20/2.0/3 | UNKNOWN | UNKNOWN | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | 1.0 | - | - | - | - | - | - | regime_flip | 0.844 | 0.354 | 206 | 268 | DEEP |
| 4 | 20/2.0/3 | 20/2.0/3 | UNKNOWN | UNKNOWN | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | 1.0 | - | - | - | - | - | - | time_stop_20d | 0.844 | 0.354 | 206 | 268 | DEEP |
| 5 | 20/2.0/3 | 20/2.0/3 | UNKNOWN | UNKNOWN | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | 1.0 | - | - | - | - | - | - | class_time_stop | 1.188 | 0.346 | 206 | 268 | DEEP |
| 6 | 20/2.0/3 | 20/2.0/3 | UNKNOWN | UNKNOWN | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | 1.0 | - | - | - | - | - | - | hybrid_50pct_target | 0.631 | 0.263 | 206 | 268 | DEEP |
| 7 | 20/2.0/3 | 20/2.0/3 | UNKNOWN | UNKNOWN | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | 1.0 | - | - | - | - | - | - | r_multiple_3r | 0.851 | 0.061 | 206 | 268 | DEEP |
| 8 | 20/2.0/3 | 20/2.0/3 | UNKNOWN | UNKNOWN | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | 1.0 | - | - | - | - | - | - | fixed_4r_2r | 0.469 | -0.023 | 206 | 268 | DEEP |
| 9 | 20/2.0/3 | 20/2.0/3 | UNKNOWN | UNKNOWN | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | 1.0 | - | - | - | - | - | - | trailing_10pct | 0.388 | -0.023 | 206 | 268 | DEEP |
| 10 | 20/2.0/3 | 20/2.0/3 | UNKNOWN | UNKNOWN | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | <=0.167 | - | - | - | - | - | - | - | breakeven_plus_trail | 0.321 | -0.028 | 382 | 528 | DEEP |
| 11 | 20/2.0/3 | 20/2.0/3 | UNKNOWN | UNKNOWN | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | 1.0 | - | - | - | - | - | - | trailing_15pct | 0.253 | -0.035 | 206 | 268 | DEEP |
| 12 | 20/2.0/3 | 20/2.0/3 | UNKNOWN | UNKNOWN | 14 | 2 | edge per P8 | 1/3,2/3 | 35 | 5.0 | B1147 set (40/60, 45/55, 50/50) | - | - | - | - | - | <=0.998 | - | - | hybrid_50pct_target | 0.254 | -0.076 | 247 | 336 | DEEP |
