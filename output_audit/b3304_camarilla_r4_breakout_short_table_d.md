_Rendered by scripts/table_d_render.py from output_audit/b3304_camarilla_r4_breakout_short_step1_is_surface.json, all rows - working tree on db046c8a9, 2026-10-26T15:54Z (L803 build stamp)._

# TABLE D (OFFLINE FORM, unified) - camarilla_r4_breakout step UNKNOWN (no readable run manifest recorded)

80 graded cells across 1 artifact(s); 1 in-sample-only artifact(s): holdout NOT read, no gates (B1608); npt excluded from ranking.
INVENTORY (one column per Table A row; '-' = breadth axis not applied, production behavior; FACTORIAL design - a row is one corner, several axes at once):
  - P1 above_cam_r4 identity (LONG): production R4 = C + 1.1/2 x range, band ['R4 = C + 1.1/2 x range'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P2 R4 distance multiplier (LONG): production 0.55, free band [0.55, 0.75, 1.0, 1.25] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - P3 below_cam_s4 identity (SHORT): production S4 = C - 1.1/2 x range, band ['S4 = C - 1.1/2 x range'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P4 S4 distance multiplier (SHORT): TESTED at {0.55, 0.75, 1.0, 1.25} (4 of 4 band levels)
  - P5 vol_above_avg identity: production vol / avg20 >= 1.0, band ['vol / avg20 >= 1.0'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P6 volume ratio floor (both legs): TESTED at {1.0, 1.2, 1.5, 2.0} (4 of 4 band levels)
  - P7 volume average window: production 20, band [20] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P8 xs_ivol floor (both legs): TESTED at {0.2598, 0.2918, 0.3301, 0.3814, 0.4621} (5 of 5 band levels)
  - P9 days_to_cover cap (borrow guard, SHORT leg): production 5.0, band ['5.0'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
NULL PRICE - depth-surface null (80 of 80 cells graded, b3304_camarilla_r4_breakout_short_step1_is_surface.json): best 0.902 vs q95 2.065, p 0.5842 (100 perms, SYNTHETIC)
EPISODE (S6-B3315) - 0 of the 25 top-25 rows recording it put more than 0.5 of their IS trades in ONE month (the null shuffles magnitudes across fires and cannot see this; every row's share is in its artifact's 'episode' field)
DEPTH SURFACE - an offline_level_sweep surface stores each cell's BEST exit only and no lower bound, so its rows show that exit with IS ci_lo blank and rank after every row that records one (L580; S6-B3316)
TIER - DEEP n>=100, MID 30-99, THIN 10-29. Rank improves monotonically as evidence thins, so RANK IS NOT TRUSTWORTHINESS and the depth band sits beside the ranking key deliberately.
SORT - is_ci_lo DESCENDING, then IS n descending, nothing filtered (runbook section 7.5). Ranking on Sharpe is the REJECTED order: a higher Sharpe can carry a NEGATIVE lower bound (L455).
EXITS - Step 1 picks each cell's exit by SHARPE alone (B1605) while this table RANKS by is_ci_lo. Two objectives, so a leading row can carry the exit that won on Sharpe.
Showing top 80 of 80 ranked cells.

| rank | above_cam_r4 identity (LONG) | R4 distance multiplier (LONG) | below_cam_s4 identity (SHORT) | S4 distance multiplier (SHORT) | vol_above_avg identity | volume ratio floor (both legs) | volume average window | xs_ivol floor (both legs) | days_to_cover cap (borrow guard, SHORT leg) | exit | IS sharpe | IS ci_lo | IS n | full n | tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.333 |  | 1025 | - | DEEP |
| 2 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.474 |  | 797 | - | DEEP |
| 3 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.295 |  | 792 | - | DEEP |
| 4 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.282 |  | 638 | - | DEEP |
| 5 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.412 |  | 618 | - | DEEP |
| 6 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.550 |  | 599 | - | DEEP |
| 7 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3301 | 5.0 | breakeven_plus_trail | 0.286 |  | 587 | - | DEEP |
| 8 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.452 |  | 503 | - | DEEP |
| 9 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.240 |  | 488 | - | DEEP |
| 10 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.462 |  | 468 | - | DEEP |
| 11 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3301 | 5.0 | breakeven_plus_trail | 0.397 |  | 457 | - | DEEP |
| 12 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.531 |  | 443 | - | DEEP |
| 13 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.462 |  | 400 | - | DEEP |
| 14 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.411 |  | 389 | - | DEEP |
| 15 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3301 | 5.0 | breakeven_plus_trail | 0.190 |  | 362 | - | DEEP |
| 16 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3814 | 5.0 | breakeven_plus_trail | 0.254 |  | 357 | - | DEEP |
| 17 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.426 |  | 349 | - | DEEP |
| 18 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3301 | 5.0 | breakeven_plus_trail | 0.459 |  | 345 | - | DEEP |
| 19 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.134 |  | 345 | - | DEEP |
| 20 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.432 |  | 310 | - | DEEP |
| 21 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.377 |  | 309 | - | DEEP |
| 22 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3301 | 5.0 | breakeven_plus_trail | 0.362 |  | 288 | - | DEEP |
| 23 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3814 | 5.0 | breakeven_plus_trail | 0.367 |  | 280 | - | DEEP |
| 24 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.213 |  | 280 | - | DEEP |
| 25 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.106 |  | 269 | - | DEEP |
| 26 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3301 | 5.0 | breakeven_plus_trail | 0.377 |  | 259 | - | DEEP |
| 27 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.342 |  | 240 | - | DEEP |
| 28 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.201 |  | 234 | - | DEEP |
| 29 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3301 | 5.0 | breakeven_plus_trail | 0.328 |  | 229 | - | DEEP |
| 30 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.181 |  | 223 | - | DEEP |
| 31 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3814 | 5.0 | breakeven_plus_trail | 0.473 |  | 220 | - | DEEP |
| 32 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3814 | 5.0 | breakeven_plus_trail | 0.209 |  | 216 | - | DEEP |
| 33 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 0.007 |  | 203 | - | DEEP |
| 34 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.215 |  | 193 | - | DEEP |
| 35 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.137 |  | 185 | - | DEEP |
| 36 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3301 | 5.0 | breakeven_plus_trail | 0.227 |  | 179 | - | DEEP |
| 37 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3814 | 5.0 | breakeven_plus_trail | 0.404 |  | 173 | - | DEEP |
| 38 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.4621 | 5.0 | breakeven_plus_trail | 0.354 |  | 169 | - | DEEP |
| 39 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3814 | 5.0 | breakeven_plus_trail | 0.253 |  | 167 | - | DEEP |
| 40 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3301 | 5.0 | breakeven_plus_trail | 0.051 |  | 164 | - | DEEP |
| 41 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.556 |  | 157 | - | DEEP |
| 42 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.170 |  | 157 | - | DEEP |
| 43 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.469 |  | 143 | - | DEEP |
| 44 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3814 | 5.0 | breakeven_plus_trail | 0.380 |  | 143 | - | DEEP |
| 45 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3301 | 5.0 | breakeven_plus_trail | 0.012 |  | 136 | - | DEEP |
| 46 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.4621 | 5.0 | breakeven_plus_trail | 0.348 |  | 135 | - | DEEP |
| 47 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.451 |  | 134 | - | DEEP |
| 48 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.512 |  | 126 | - | DEEP |
| 49 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3814 | 5.0 | breakeven_plus_trail | 0.050 |  | 121 | - | DEEP |
| 50 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2598 | 5.0 | breakeven_plus_trail | 0.493 |  | 118 | - | DEEP |
| 51 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3301 | 5.0 | breakeven_plus_trail | 0.020 |  | 118 | - | DEEP |
| 52 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.421 |  | 117 | - | DEEP |
| 53 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.4621 | 5.0 | breakeven_plus_trail | 0.274 |  | 115 | - | DEEP |
| 54 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3814 | 5.0 | breakeven_plus_trail | 0.173 |  | 114 | - | DEEP |
| 55 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.4621 | 5.0 | class_time_stop | 0.672 |  | 110 | - | DEEP |
| 56 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.398 |  | 109 | - | DEEP |
| 57 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2918 | 5.0 | breakeven_plus_trail | 0.452 |  | 99 | - | MID |
| 58 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 0.097 |  | 98 | - | MID |
| 59 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.4621 | 5.0 | breakeven_plus_trail | 0.331 |  | 96 | - | MID |
| 60 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3301 | 5.0 | r_multiple_3r | 0.581 |  | 92 | - | MID |
| 61 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3301 | 5.0 | breakeven_plus_trail | 0.321 |  | 85 | - | MID |
| 62 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.4621 | 5.0 | breakeven_plus_trail | 0.222 |  | 84 | - | MID |
| 63 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 0.017 |  | 83 | - | MID |
| 64 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.4621 | 5.0 | breakeven_plus_trail | 0.286 |  | 80 | - | MID |
| 65 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3301 | 5.0 | breakeven_plus_trail | 0.243 |  | 79 | - | MID |
| 66 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3301 | 5.0 | breakeven_plus_trail | 0.269 |  | 74 | - | MID |
| 67 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 0.070 |  | 73 | - | MID |
| 68 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.4621 | 5.0 | breakeven_plus_trail | 0.215 |  | 69 | - | MID |
| 69 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.4621 | 5.0 | breakeven_plus_trail | 0.007 |  | 64 | - | MID |
| 70 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.4621 | 5.0 | breakeven_plus_trail | 0.242 |  | 59 | - | MID |
| 71 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3814 | 5.0 | r_multiple_2r | 0.641 |  | 54 | - | MID |
| 72 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.4621 | 5.0 | class_time_stop | 0.169 |  | 53 | - | MID |
| 73 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 0.506 |  | 50 | - | MID |
| 74 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 0.362 |  | 46 | - | MID |
| 75 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.4621 | 5.0 | r_multiple_3r | 0.075 |  | 46 | - | MID |
| 76 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 0.441 |  | 44 | - | MID |
| 77 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.4621 | 5.0 | r_multiple_2r | 0.902 |  | 34 | - | MID |
| 78 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.75 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.4621 | 5.0 | r_multiple_2r | 0.471 |  | 33 | - | MID |
| 79 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.0 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.4621 | 5.0 | r_multiple_2r | 0.516 |  | 32 | - | MID |
| 80 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 1.25 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.4621 | 5.0 | r_multiple_3r | 0.404 |  | 30 | - | MID |
