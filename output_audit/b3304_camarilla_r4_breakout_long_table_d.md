_Rendered by scripts/table_d_render.py from output_audit/b3304_camarilla_r4_breakout_long_step1_is_surface.json, all rows - working tree on db046c8a9, 2026-10-26T15:54Z (L803 build stamp)._

# TABLE D (OFFLINE FORM, unified) - camarilla_r4_breakout step UNKNOWN (no readable run manifest recorded)

80 graded cells across 1 artifact(s); 1 in-sample-only artifact(s): holdout NOT read, no gates (B1608); npt excluded from ranking.
INVENTORY (one column per Table A row; '-' = breadth axis not applied, production behavior; FACTORIAL design - a row is one corner, several axes at once):
  - P1 above_cam_r4 identity (LONG): production R4 = C + 1.1/2 x range, band ['R4 = C + 1.1/2 x range'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P2 R4 distance multiplier (LONG): TESTED at {0.55, 0.75, 1.0, 1.25} (4 of 4 band levels)
  - P3 below_cam_s4 identity (SHORT): production S4 = C - 1.1/2 x range, band ['S4 = C - 1.1/2 x range'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P4 S4 distance multiplier (SHORT): production 0.55, free band [0.55, 0.75, 1.0, 1.25] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - P5 vol_above_avg identity: production vol / avg20 >= 1.0, band ['vol / avg20 >= 1.0'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P6 volume ratio floor (both legs): TESTED at {1.0, 1.2, 1.5, 2.0} (4 of 4 band levels)
  - P7 volume average window: production 20, band [20] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P8 xs_ivol floor (both legs): TESTED at {0.2598, 0.2918, 0.3301, 0.3814, 0.4621} (5 of 5 band levels)
  - P9 days_to_cover cap (borrow guard, SHORT leg): production 5.0, band ['5.0'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
NULL PRICE - depth-surface null (80 of 80 cells graded, b3304_camarilla_r4_breakout_long_step1_is_surface.json): best 1.335 vs q95 2.333, p 0.4455 (100 perms, SYNTHETIC)
EPISODE (S6-B3315) - 0 of the 25 top-25 rows recording it put more than 0.5 of their IS trades in ONE month (the null shuffles magnitudes across fires and cannot see this; every row's share is in its artifact's 'episode' field)
DEPTH SURFACE - an offline_level_sweep surface stores each cell's BEST exit only and no lower bound, so its rows show that exit with IS ci_lo blank and rank after every row that records one (L580; S6-B3316)
TIER - DEEP n>=100, MID 30-99, THIN 10-29. Rank improves monotonically as evidence thins, so RANK IS NOT TRUSTWORTHINESS and the depth band sits beside the ranking key deliberately.
SORT - is_ci_lo DESCENDING, then IS n descending, nothing filtered (runbook section 7.5). Ranking on Sharpe is the REJECTED order: a higher Sharpe can carry a NEGATIVE lower bound (L455).
EXITS - Step 1 picks each cell's exit by SHARPE alone (B1605) while this table RANKS by is_ci_lo. Two objectives, so a leading row can carry the exit that won on Sharpe.
Showing top 80 of 80 ranked cells.

| rank | above_cam_r4 identity (LONG) | R4 distance multiplier (LONG) | below_cam_s4 identity (SHORT) | S4 distance multiplier (SHORT) | vol_above_avg identity | volume ratio floor (both legs) | volume average window | xs_ivol floor (both legs) | days_to_cover cap (borrow guard, SHORT leg) | exit | IS sharpe | IS ci_lo | IS n | full n | tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.664 |  | 1194 | - | DEEP |
| 2 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.701 |  | 958 | - | DEEP |
| 3 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 0.706 |  | 950 | - | DEEP |
| 4 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.738 |  | 795 | - | DEEP |
| 5 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 0.736 |  | 766 | - | DEEP |
| 6 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 0.717 |  | 717 | - | DEEP |
| 7 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.750 |  | 683 | - | DEEP |
| 8 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.793 |  | 655 | - | DEEP |
| 9 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 0.805 |  | 622 | - | DEEP |
| 10 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 0.748 |  | 572 | - | DEEP |
| 11 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 0.792 |  | 551 | - | DEEP |
| 12 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 0.843 |  | 510 | - | DEEP |
| 13 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.732 |  | 496 | - | DEEP |
| 14 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 0.805 |  | 494 | - | DEEP |
| 15 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.846 |  | 488 | - | DEEP |
| 16 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 0.830 |  | 477 | - | DEEP |
| 17 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.885 |  | 443 | - | DEEP |
| 18 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 0.812 |  | 421 | - | DEEP |
| 19 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 0.818 |  | 403 | - | DEEP |
| 20 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 0.828 |  | 399 | - | DEEP |
| 21 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 0.893 |  | 385 | - | DEEP |
| 22 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 0.858 |  | 385 | - | DEEP |
| 23 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.945 |  | 371 | - | DEEP |
| 24 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.841 |  | 362 | - | DEEP |
| 25 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 0.959 |  | 353 | - | DEEP |
| 26 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 0.904 |  | 333 | - | DEEP |
| 27 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 0.841 |  | 310 | - | DEEP |
| 28 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 0.909 |  | 296 | - | DEEP |
| 29 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 1.015 |  | 295 | - | DEEP |
| 30 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.970 |  | 294 | - | DEEP |
| 31 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 0.867 |  | 293 | - | DEEP |
| 32 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 0.933 |  | 285 | - | DEEP |
| 33 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 1.000 |  | 270 | - | DEEP |
| 34 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 0.937 |  | 269 | - | DEEP |
| 35 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.4621 | 5.0 | next_pivot_target | 0.854 |  | 258 | - | DEEP |
| 36 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 1.053 |  | 237 | - | DEEP |
| 37 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.988 |  | 233 | - | DEEP |
| 38 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 0.882 |  | 222 | - | DEEP |
| 39 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 1.058 |  | 221 | - | DEEP |
| 40 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 0.944 |  | 219 | - | DEEP |
| 41 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 0.942 |  | 211 | - | DEEP |
| 42 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.4621 | 5.0 | next_pivot_target | 0.832 |  | 209 | - | DEEP |
| 43 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 1.046 |  | 197 | - | DEEP |
| 44 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 1.117 |  | 191 | - | DEEP |
| 45 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 1.093 |  | 182 | - | DEEP |
| 46 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.4621 | 5.0 | next_pivot_target | 0.931 |  | 181 | - | DEEP |
| 47 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.861 |  | 179 | - | DEEP |
| 48 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 1.117 |  | 162 | - | DEEP |
| 49 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 0.989 |  | 160 | - | DEEP |
| 50 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.4621 | 5.0 | next_pivot_target | 0.949 |  | 159 | - | DEEP |
| 51 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.889 |  | 154 | - | DEEP |
| 52 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 0.925 |  | 152 | - | DEEP |
| 53 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.4621 | 5.0 | hybrid_50pct_target | 0.907 |  | 148 | - | DEEP |
| 54 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 1.119 |  | 147 | - | DEEP |
| 55 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 1.133 |  | 133 | - | DEEP |
| 56 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 0.946 |  | 131 | - | DEEP |
| 57 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 0.975 |  | 129 | - | DEEP |
| 58 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.4621 | 5.0 | next_pivot_target | 0.955 |  | 122 | - | DEEP |
| 59 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 0.956 |  | 121 | - | DEEP |
| 60 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.0 | 20 | 0.4621 | 5.0 | hybrid_50pct_target | 1.002 |  | 118 | - | DEEP |
| 61 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 1.167 |  | 114 | - | DEEP |
| 62 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.4621 | 5.0 | next_pivot_target | 1.071 |  | 113 | - | DEEP |
| 63 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 1.037 |  | 110 | - | DEEP |
| 64 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2598 | 5.0 | hybrid_50pct_target | 1.016 |  | 107 | - | DEEP |
| 65 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 0.994 |  | 105 | - | DEEP |
| 66 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.4621 | 5.0 | hybrid_50pct_target | 1.072 |  | 97 | - | MID |
| 67 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.2 | 20 | 0.4621 | 5.0 | hybrid_50pct_target | 1.065 |  | 93 | - | MID |
| 68 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.2918 | 5.0 | hybrid_50pct_target | 1.108 |  | 92 | - | MID |
| 69 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3301 | 5.0 | atr_trail_vix_conditional | 1.130 |  | 91 | - | MID |
| 70 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 1.037 |  | 87 | - | MID |
| 71 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.4621 | 5.0 | hybrid_50pct_target | 1.103 |  | 83 | - | MID |
| 72 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3301 | 5.0 | hybrid_50pct_target | 1.153 |  | 75 | - | MID |
| 73 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 1.089 |  | 74 | - | MID |
| 74 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 1.5 | 20 | 0.4621 | 5.0 | hybrid_50pct_target | 1.121 |  | 69 | - | MID |
| 75 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 1.161 |  | 65 | - | MID |
| 76 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.3814 | 5.0 | hybrid_50pct_target | 1.204 |  | 57 | - | MID |
| 77 | R4 = C + 1.1/2 x range | 0.55 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.4621 | 5.0 | next_pivot_target | 1.202 |  | 48 | - | MID |
| 78 | R4 = C + 1.1/2 x range | 0.75 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.4621 | 5.0 | class_time_stop | 1.191 |  | 44 | - | MID |
| 79 | R4 = C + 1.1/2 x range | 1.0 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.4621 | 5.0 | multi_tier_partial | 1.312 |  | 40 | - | MID |
| 80 | R4 = C + 1.1/2 x range | 1.25 | S4 = C - 1.1/2 x range | 0.55 | vol / avg20 >= 1.0 | 2.0 | 20 | 0.4621 | 5.0 | smc_mitigation_zone | 1.335 |  | 34 | - | MID |
