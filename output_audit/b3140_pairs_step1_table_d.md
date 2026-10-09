# TABLE D (OFFLINE FORM, unified) - pairs_mean_reversion_long Step-1

24 graded cells across 3 artifact(s); 3 in-sample-only artifact(s): holdout NOT read, no gates (B1608); npt excluded from ranking.
ROWS NOT RENDERED - 14112 artifact row(s) whose axis is neither a Table A label nor a declared signal key (B2708 prunes them from this view; their history stays in the artifacts): atr (192), atr_pct (192), bond_equity_20d_pct_change (192), bond_equity_ratio (192), buy_count (48), cnn_fg_days_since_publish (96), cot_copper_commercials_net_pct (192), cot_copper_commercials_pctile_3y (192), cot_copper_mmoney_pctile_3y (192), cot_dow_commercials_net_pct (192), cot_dow_commercials_pctile_3y (192), cot_dow_mmoney_pctile_3y (192), cot_dxy_commercials_net_pct (192), cot_dxy_commercials_pctile_3y (192), cot_dxy_mmoney_pctile_3y (192), cot_gold_commercials_net_pct (192), cot_gold_commercials_pctile_3y (192), cot_gold_mmoney_pctile_3y (192), cot_ndx_commercials_net_pct (192), cot_ndx_commercials_pctile_3y (192), cot_ndx_mmoney_pctile_3y (192), cot_rut_commercials_net_pct (192), cot_sp500_commercials_net_pct (192), cot_sp500_commercials_pctile_3y (192), cot_sp500_mmoney_pctile_3y (192), cpr_width (192), days_to_cover (192), days_until_fomc (192), dow (192), dxy_20d_pct_change (192), dxy_proxy_close (192), gap_dn_pct (192), gap_up_pct (192), gold_silver_20d_pct_change (192), gold_silver_ratio (192), house_buy_count_90d (144), house_net_buy_90d (144), house_sell_count_90d (144), institutional_increased (192), institutional_new_positions (192), naked_poc_nearest_distance_pct (192), news_article_count (192), news_bearish_pct (96), news_bullish_pct (192), news_count_5d (192), news_count_7d (192), news_prior_article_count (192), news_sentiment_30d (192), news_sentiment_5d (144), news_sentiment_mean (144), news_sentiment_score (144), news_sentiment_shift (144), news_volume_zscore_5d (192), pair_max_abs_zscore (192), po3_accum_range_pct (192), po3_close_position (192), sector_strongest_rs (192), sector_weakest_rs (192), sell_count (96), short_interest_observations (192), smc_dealing_range_pct (192), trading_day_of_month (192), trading_days_left_in_month (192), vix_percentile (192), vix_today (192), vix_value (192), vix_vix3m_ratio (192), vp_close_near_poc_pct (192), week_open_gap_down_pct (48), week_open_gap_up_pct (48), weekly_momentum_4w (192), xs_beta (192), xs_beta_decile (192), xs_ivol (192), xs_ivol_decile (192), xs_max_anomaly (192), xs_max_anomaly_decile (192), xs_momentum_12_1 (192), xs_momentum_decile (192)
INVENTORY (one column per Table A row; '-' = breadth axis not applied, production behavior; one-at-a-time design):
  - P1 pairs precompute identity (T5b cointegrated pairs): production EG 0.05 / z-window 60 / hl-bounds 5-30, band ['EG 0.05 / z-window 60 / hl-bounds 5-30'] - resim-only, UNTESTED-OFFLINE (no env knob; engine re-simulation required)
  - P2 pair_count_active floor: production 0, free band [0, 4, 6, 9, 13] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - P3 pair_half_life floor (days): production 5, free band [5, 6.94, 8.59, 10.08, 11.96] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
  - P4 pair_zscore_signed ceiling: production -2.0, free band [-2.0, -2.1619, -2.3749, -2.6313, -3.0505] - NOT TESTED in this campaign (offline-gradable; no rows varied it)
TIER - DEEP n>=100, MID 30-99, THIN 10-29. Rank improves monotonically as evidence thins, so RANK IS NOT TRUSTWORTHINESS and the depth band sits beside the ranking key deliberately.
SORT - is_ci_lo DESCENDING, then IS n descending, nothing filtered (runbook section 7.5). Ranking on Sharpe is the REJECTED order: a higher Sharpe can carry a NEGATIVE lower bound (L455).
EXITS - Step 1 picks each cell's exit by SHARPE alone (B1605) while this table RANKS by is_ci_lo. Two objectives, so a leading row can carry the exit that won on Sharpe.
Showing top 24 of 24 ranked cells.

| rank | pairs precompute identity (T5b cointegrated pairs) | pair_count_active floor | pair_half_life floor (days) | pair_zscore_signed ceiling | exit | IS sharpe | IS ci_lo | IS n | full n | tier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | time_stop_10d | 1.011 | 0.659 | 797 | 797 | DEEP |
| 2 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | r_multiple_3r | 0.966 | 0.585 | 797 | 797 | DEEP |
| 3 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | breakeven_plus_trail | 0.803 | 0.581 | 797 | 797 | DEEP |
| 4 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | regime_flip | 0.860 | 0.58 | 797 | 797 | DEEP |
| 5 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | r_multiple_2r | 0.999 | 0.55 | 797 | 797 | DEEP |
| 6 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | time_stop_20d | 0.752 | 0.499 | 797 | 797 | DEEP |
| 7 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | next_pivot_target | 0.796 | 0.472 | 797 | 797 | DEEP |
| 8 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | hybrid_50pct_target | 0.559 | 0.377 | 797 | 797 | DEEP |
| 9 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | fixed_4r_2r | 0.542 | 0.285 | 797 | 797 | DEEP |
| 10 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | class_time_stop | 0.491 | 0.278 | 797 | 797 | DEEP |
| 11 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | earnings_blackout | 0.407 | 0.245 | 797 | 797 | DEEP |
| 12 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | trailing_15pct | 0.114 | -0.034 | 797 | 797 | DEEP |
| 13 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | trailing_10pct | 0.150 | -0.042 | 797 | 797 | DEEP |
| 14 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | atr_trail_2x | 0.195 | -0.115 | 797 | 797 | DEEP |
| 15 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | break_even_at_1r | 0.113 | -0.208 | 797 | 797 | DEEP |
| 16 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | ma_exit_ema9 | 0.461 | -0.262 | 797 | 797 | DEEP |
| 17 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | atr_trail_vix_conditional | -0.240 | -0.669 | 797 | 797 | DEEP |
| 18 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | trailing_5pct | -0.351 | -0.682 | 797 | 797 | DEEP |
| 19 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | multi_tier_partial | -0.444 | -0.978 | 797 | 797 | DEEP |
| 20 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | chandelier_3x | -0.771 | -1.368 | 797 | 797 | DEEP |
| 21 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | atr_trail_1x | -1.126 | -1.648 | 797 | 797 | DEEP |
| 22 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | reverse_signal | -1.126 | -1.648 | 797 | 797 | DEEP |
| 23 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | mfe_lockin_trail | -1.365 | -1.909 | 797 | 797 | DEEP |
| 24 | EG 0.05 / z-window 60 / hl-bounds 5-30 | 0 | 5 | -2.0 | smc_mitigation_zone | -4.002 | -4.882 | 797 | 797 | DEEP |
