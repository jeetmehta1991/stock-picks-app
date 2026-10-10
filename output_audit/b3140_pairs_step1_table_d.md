# TABLE D (OFFLINE FORM, unified) - pairs_mean_reversion_long Step-1

96 graded cells across 12 artifact(s); 12 in-sample-only artifact(s): holdout NOT read, no gates (B1608); npt excluded from ranking.
ROWS NOT RENDERED - 56400 artifact row(s) whose axis is neither a Table A label nor a declared signal key (B2708 prunes them from this view; their history stays in the artifacts): atr (768), atr_pct (768), bond_equity_20d_pct_change (768), bond_equity_ratio (768), buy_count (192), cnn_fg_days_since_publish (288), cot_copper_commercials_net_pct (768), cot_copper_commercials_pctile_3y (768), cot_copper_mmoney_pctile_3y (768), cot_dow_commercials_net_pct (768), cot_dow_commercials_pctile_3y (768), cot_dow_mmoney_pctile_3y (768), cot_dxy_commercials_net_pct (768), cot_dxy_commercials_pctile_3y (768), cot_dxy_mmoney_pctile_3y (768), cot_gold_commercials_net_pct (768), cot_gold_commercials_pctile_3y (768), cot_gold_mmoney_pctile_3y (768), cot_ndx_commercials_net_pct (768), cot_ndx_commercials_pctile_3y (768), cot_ndx_mmoney_pctile_3y (768), cot_rut_commercials_net_pct (768), cot_sp500_commercials_net_pct (768), cot_sp500_commercials_pctile_3y (768), cot_sp500_mmoney_pctile_3y (768), cpr_width (768), days_to_cover (768), days_until_fomc (768), dow (768), dxy_20d_pct_change (768), dxy_proxy_close (768), gap_dn_pct (768), gap_up_pct (768), gold_silver_20d_pct_change (768), gold_silver_ratio (768), house_buy_count_90d (576), house_net_buy_90d (576), house_sell_count_90d (576), institutional_increased (768), institutional_new_positions (768), naked_poc_nearest_distance_pct (768), news_article_count (768), news_bearish_pct (432), news_bullish_pct (768), news_count_5d (768), news_count_7d (768), news_prior_article_count (768), news_sentiment_30d (768), news_sentiment_5d (576), news_sentiment_mean (576), news_sentiment_score (576), news_sentiment_shift (576), news_volume_zscore_5d (768), pair_max_abs_zscore (768), po3_accum_range_pct (768), po3_close_position (768), sector_strongest_rs (768), sector_weakest_rs (768), sell_count (384), short_interest_observations (768), smc_dealing_range_pct (768), trading_day_of_month (768), trading_days_left_in_month (768), vix_percentile (768), vix_today (768), vix_value (768), vix_vix3m_ratio (768), vp_close_near_poc_pct (768), week_open_gap_down_pct (192), week_open_gap_up_pct (192), weekly_momentum_4w (768), xs_beta (768), xs_beta_decile (768), xs_ivol (768), xs_ivol_decile (768), xs_max_anomaly (768), xs_max_anomaly_decile (768), xs_momentum_12_1 (768), xs_momentum_decile (768)
INVENTORY (one column per Table A row; '-' = breadth axis not applied, production behavior; one-at-a-time design):
  - P1 pairs precompute identity (T5b cointegrated pairs): production T5b build: EG p<0.05, half-life 5-30d, band ['T5b build: EG p<0.05, half-life 5-30d'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P2 pair_count_active floor: production 0, free band [0, 4, 6, 9, 13] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - P3 pair_half_life floor (days): production 5, free band [5, 6.94, 8.59, 10.08, 11.96] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - P4 pair_zscore_signed ceiling: production -2.0, free band [-2.0, -2.1619, -2.3749, -2.6313, -3.0505] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - P5 Engle-Granger cointegration significance: TESTED BY RE-SIMULATION at {0.01, 0.05} (2 of 2 band levels)
  - P6 pair z-score rolling window (bars): TESTED BY RE-SIMULATION at {40, 60, 90} (3 of 3 band levels)
TIER - DEEP n>=100, MID 30-99, THIN 10-29. Rank improves monotonically as evidence thins, so RANK IS NOT TRUSTWORTHINESS and the depth band sits beside the ranking key deliberately.
SORT - is_ci_lo DESCENDING, then IS n descending, nothing filtered (runbook section 7.5). Ranking on Sharpe is the REJECTED order: a higher Sharpe can carry a NEGATIVE lower bound (L455).
EXITS - Step 1 picks each cell's exit by SHARPE alone (B1605) while this table RANKS by is_ci_lo. Two objectives, so a leading row can carry the exit that won on Sharpe.
Showing top 96 of 96 ranked cells.

| rank | pairs precompute identity (T5b cointegrated pairs) | pair_count_active floor | pair_half_life floor (days) | pair_zscore_signed ceiling | Engle-Granger cointegration significance | pair z-score rolling window (bars) | exit | IS sharpe | IS ci_lo | IS n | full n | tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | time_stop_10d | 1.011 | 0.659 | 797 | 797 | DEEP |
| 2 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | breakeven_plus_trail | 0.882 | 0.6 | 497 | 497 | DEEP |
| 3 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | time_stop_20d | 0.920 | 0.598 | 497 | 497 | DEEP |
| 4 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | r_multiple_2r | 1.180 | 0.589 | 497 | 497 | DEEP |
| 5 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | next_pivot_target | 1.012 | 0.587 | 497 | 497 | DEEP |
| 6 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | r_multiple_3r | 0.966 | 0.585 | 797 | 797 | DEEP |
| 7 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | breakeven_plus_trail | 0.857 | 0.582 | 517 | 517 | DEEP |
| 8 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | r_multiple_3r | 1.091 | 0.582 | 476 | 476 | DEEP |
| 9 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | breakeven_plus_trail | 0.803 | 0.581 | 797 | 797 | DEEP |
| 10 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | regime_flip | 0.860 | 0.58 | 797 | 797 | DEEP |
| 11 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | breakeven_plus_trail | 0.870 | 0.578 | 476 | 476 | DEEP |
| 12 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | time_stop_10d | 1.016 | 0.57 | 497 | 497 | DEEP |
| 13 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | r_multiple_2r | 0.999 | 0.55 | 797 | 797 | DEEP |
| 14 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | next_pivot_target | 0.981 | 0.545 | 476 | 476 | DEEP |
| 15 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | regime_flip | 0.895 | 0.544 | 497 | 497 | DEEP |
| 16 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | time_stop_10d | 0.975 | 0.523 | 476 | 476 | DEEP |
| 17 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | r_multiple_2r | 1.111 | 0.518 | 476 | 476 | DEEP |
| 18 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | time_stop_20d | 0.752 | 0.499 | 797 | 797 | DEEP |
| 19 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | regime_flip | 0.856 | 0.499 | 476 | 476 | DEEP |
| 20 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | next_pivot_target | 0.904 | 0.493 | 517 | 517 | DEEP |
| 21 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | time_stop_20d | 0.805 | 0.489 | 517 | 517 | DEEP |
| 22 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | r_multiple_3r | 0.976 | 0.477 | 497 | 497 | DEEP |
| 23 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | next_pivot_target | 0.796 | 0.472 | 797 | 797 | DEEP |
| 24 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | time_stop_20d | 0.784 | 0.458 | 476 | 476 | DEEP |
| 25 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | hybrid_50pct_target | 0.653 | 0.418 | 497 | 497 | DEEP |
| 26 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | regime_flip | 0.730 | 0.388 | 517 | 517 | DEEP |
| 27 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | hybrid_50pct_target | 0.629 | 0.385 | 476 | 476 | DEEP |
| 28 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | hybrid_50pct_target | 0.559 | 0.377 | 797 | 797 | DEEP |
| 29 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | time_stop_10d | 0.812 | 0.376 | 517 | 517 | DEEP |
| 30 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | hybrid_50pct_target | 0.591 | 0.36 | 517 | 517 | DEEP |
| 31 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | fixed_4r_2r | 0.655 | 0.328 | 497 | 497 | DEEP |
| 32 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | r_multiple_3r | 0.797 | 0.3 | 517 | 517 | DEEP |
| 33 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | fixed_4r_2r | 0.632 | 0.295 | 476 | 476 | DEEP |
| 34 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | fixed_4r_2r | 0.542 | 0.285 | 797 | 797 | DEEP |
| 35 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | class_time_stop | 0.491 | 0.278 | 797 | 797 | DEEP |
| 36 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | fixed_4r_2r | 0.575 | 0.252 | 517 | 517 | DEEP |
| 37 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | earnings_blackout | 0.407 | 0.245 | 797 | 797 | DEEP |
| 38 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | class_time_stop | 0.487 | 0.221 | 517 | 517 | DEEP |
| 39 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | class_time_stop | 0.476 | 0.205 | 497 | 497 | DEEP |
| 40 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | earnings_blackout | 0.326 | 0.121 | 497 | 497 | DEEP |
| 41 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | class_time_stop | 0.383 | 0.107 | 476 | 476 | DEEP |
| 42 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | r_multiple_2r | 0.690 | 0.104 | 517 | 517 | DEEP |
| 43 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | earnings_blackout | 0.299 | 0.09 | 476 | 476 | DEEP |
| 44 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | earnings_blackout | 0.284 | 0.083 | 517 | 517 | DEEP |
| 45 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | trailing_15pct | 0.114 | -0.034 | 797 | 797 | DEEP |
| 46 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | trailing_10pct | 0.150 | -0.042 | 797 | 797 | DEEP |
| 47 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | trailing_15pct | 0.147 | -0.047 | 497 | 497 | DEEP |
| 48 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | trailing_15pct | 0.127 | -0.075 | 476 | 476 | DEEP |
| 49 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | trailing_10pct | 0.165 | -0.08 | 497 | 497 | DEEP |
| 50 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | trailing_15pct | 0.107 | -0.084 | 517 | 517 | DEEP |
| 51 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | atr_trail_2x | 0.195 | -0.115 | 797 | 797 | DEEP |
| 52 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | trailing_10pct | 0.126 | -0.116 | 517 | 517 | DEEP |
| 53 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | atr_trail_2x | 0.244 | -0.151 | 497 | 497 | DEEP |
| 54 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | atr_trail_2x | 0.252 | -0.154 | 476 | 476 | DEEP |
| 55 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | trailing_10pct | 0.081 | -0.18 | 476 | 476 | DEEP |
| 56 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | break_even_at_1r | 0.113 | -0.208 | 797 | 797 | DEEP |
| 57 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | break_even_at_1r | 0.151 | -0.245 | 497 | 497 | DEEP |
| 58 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | break_even_at_1r | 0.155 | -0.261 | 476 | 476 | DEEP |
| 59 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | ma_exit_ema9 | 0.461 | -0.262 | 797 | 797 | DEEP |
| 60 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | break_even_at_1r | 0.063 | -0.338 | 517 | 517 | DEEP |
| 61 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | atr_trail_2x | 0.014 | -0.38 | 517 | 517 | DEEP |
| 62 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | ma_exit_ema9 | 0.416 | -0.449 | 497 | 497 | DEEP |
| 63 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | ma_exit_ema9 | 0.337 | -0.514 | 476 | 476 | DEEP |
| 64 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | atr_trail_vix_conditional | -0.240 | -0.669 | 797 | 797 | DEEP |
| 65 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | trailing_5pct | -0.351 | -0.682 | 797 | 797 | DEEP |
| 66 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | atr_trail_vix_conditional | -0.267 | -0.824 | 476 | 476 | DEEP |
| 67 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | trailing_5pct | -0.467 | -0.883 | 497 | 497 | DEEP |
| 68 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | ma_exit_ema9 | -0.026 | -0.893 | 517 | 517 | DEEP |
| 69 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | atr_trail_vix_conditional | -0.383 | -0.936 | 497 | 497 | DEEP |
| 70 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | multi_tier_partial | -0.444 | -0.978 | 797 | 797 | DEEP |
| 71 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | trailing_5pct | -0.562 | -0.997 | 476 | 476 | DEEP |
| 72 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | trailing_5pct | -0.771 | -1.197 | 517 | 517 | DEEP |
| 73 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | atr_trail_vix_conditional | -0.703 | -1.26 | 517 | 517 | DEEP |
| 74 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | chandelier_3x | -0.610 | -1.302 | 497 | 497 | DEEP |
| 75 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | chandelier_3x | -0.610 | -1.302 | 476 | 476 | DEEP |
| 76 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | chandelier_3x | -0.771 | -1.368 | 797 | 797 | DEEP |
| 77 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | multi_tier_partial | -0.720 | -1.425 | 476 | 476 | DEEP |
| 78 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | multi_tier_partial | -0.853 | -1.554 | 497 | 497 | DEEP |
| 79 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | multi_tier_partial | -0.886 | -1.591 | 517 | 517 | DEEP |
| 80 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | atr_trail_1x | -1.126 | -1.648 | 797 | 797 | DEEP |
| 81 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | reverse_signal | -1.126 | -1.648 | 797 | 797 | DEEP |
| 82 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | mfe_lockin_trail | -1.365 | -1.909 | 797 | 797 | DEEP |
| 83 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | atr_trail_1x | -1.587 | -2.282 | 476 | 476 | DEEP |
| 84 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | reverse_signal | -1.587 | -2.282 | 476 | 476 | DEEP |
| 85 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | atr_trail_1x | -1.752 | -2.439 | 497 | 497 | DEEP |
| 86 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | reverse_signal | -1.752 | -2.439 | 497 | 497 | DEEP |
| 87 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | mfe_lockin_trail | -1.891 | -2.605 | 497 | 497 | DEEP |
| 88 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | atr_trail_1x | -1.946 | -2.634 | 517 | 517 | DEEP |
| 89 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | reverse_signal | -1.946 | -2.634 | 517 | 517 | DEEP |
| 90 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | chandelier_3x | -1.886 | -2.652 | 517 | 517 | DEEP |
| 91 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | mfe_lockin_trail | -2.115 | -2.831 | 517 | 517 | DEEP |
| 92 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | mfe_lockin_trail | -2.134 | -2.86 | 476 | 476 | DEEP |
| 93 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 60 | smc_mitigation_zone | -3.260 | -4.304 | 497 | 497 | DEEP |
| 94 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.05 | 60 | smc_mitigation_zone | -4.002 | -4.882 | 797 | 797 | DEEP |
| 95 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 90 | smc_mitigation_zone | -4.159 | -5.253 | 476 | 476 | DEEP |
| 96 | T5b build: EG p<0.05, half-life 5-30d | 0 | 5 | -2.0 | 0.01 | 40 | smc_mitigation_zone | -4.646 | -5.738 | 517 | 517 | DEEP |
