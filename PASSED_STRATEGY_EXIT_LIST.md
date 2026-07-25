<!-- Source: per CHECKLIST #77; B1375 auto-built by scripts/build_passed_strategy_exit_list.py from the R5 cube (output_r5_merged_1_7) + STRATEGY_ROSTER.md. Do NOT hand-edit; regenerate. -->

# Passed Strategy -> Exit List (R5, 2026-07-25)

**What this is:** the strategies whose (strategy x exit) cleared the LOOSE OOS gate (annualized OOS Sharpe >= 0.7 in >=1 of 4 DEC-505 folds) on the full 614-ticker R5 cube, with each strategy's best backtested exit, entry-gate formula, and OOS metrics. Dual strategies (trade long and short) appear as two rows.

**Method / caveats (read before deploying):**
- Sharpe is ANNUALIZED (per-trade x sqrt(252/avg_hold), matching `metrics.py::_sharpe`; the B1371 fix).
- **LOOSE gate** = >=0.7 in >=1 fold: a cell can clear in a single lucky year -> higher false-positive rate than the strict >=2-fold set. This is a wide candidate pool; the 1B agent layer + paper trading are the downstream filters.
- **Regime-conditional (17):** the regime-varying exit BEAT the single best exit OUT-OF-SAMPLE (IS-pick 2022-2025 / OOS-measure 2025-2026, DeltaSharpe >= 0.3). Exit is assigned once at entry from `regime_at_entry`, held to close.
- Metrics recomputed per (strategy x direction x exit); best exit = highest single-fold OOS Sharpe (n>=30 per fold).


**KNOWN LIMITATIONS (self-review B1375 - this is a CANDIDATE list, not a deploy list):**
1. **GROSS Sharpe - no transaction costs/slippage.** The cube `pnl_pct` carries no friction; net-of-cost Sharpes are lower and some cells will fail. The AUTO-FAIL cost-sensitivity gate (`metrics.py`) was NOT applied here -> S6-B1375-NET-OF-COST.
2. **Small-sample noise, no confidence intervals.** ~14% of qualifying cells are n=30-40, where a Sharpe's 95% CI is ~+/-1.6 - a 0.7 point estimate is statistically indistinguishable from 0. Point Sharpes (incl. the 2.0-2.7 tops) are unreliable at low n -> S6-B1375-SHARPE-CI.
3. **The LOOSE 613 lacks a true train/test holdout.** They are 'consistent across >=1 annual slice' selected from the SAME window (multiple-testing across 4758 cells x 4 folds, uncorrected). Only the 17 regime-conditional overrides have a genuine IS-pick/OOS-measure split -> the 613 is weaker evidence than the 17 -> S6-B1375-OOS-HOLDOUT.
4. **Dual per-direction:** a strategy can clear the POOLED gate yet have neither direction clear individually (pooling averages long+short). Rows show per-direction metrics - a direction with best-fold OOS < 0.7 is a candidate to DROP, not deploy. The 'Entry gate' column currently shows the strategy-level compact for both direction rows (dual `fires` split by direction is TODO -> S6-B1375-DUAL-FORMULA).
5. **Crisis regime absent** (n<30 in the 2022-26 window) - this system is meant to buy dips in crisis; no crisis-regime evidence exists here.

**Counts:** 70 non-conditional + 17 regime-conditional strategies (dual strategies split by direction).


## A. Non-conditional strategies (single best exit)

| Strategy | Dir | Best Exit | Regime-Cond | Regimes->Exit | OOS Sharpe (best fold) | Folds>=0.7 | n | WR | Entry gate (compact) |
|---|---|---|---|---|---|---|---|---|---|
| `52w_high_breakout_pullback_long` | long | `next_pivot_target` | N | - | 1.415 | 3/3 | 146 | 0.856 | [Producer boolean] near_52w_high_retest_long (fires when producer emits True) |
| `awesome_oscillator` | long | `regime_flip` | N | - | 1.356 | 1/4 | 517 | 0.603 | LONG: (ao_cross_up AND price_above_ema_20) \ |
| `awesome_oscillator` | short | `next_pivot_target` | N | - | 0.251 | 0/4 | 495 | 0.721 | LONG: (ao_cross_up AND price_above_ema_20) \ |
| `bollinger_tight` | long | `r_multiple_2r` | N | - | 2.297 | 1/2 | 143 | 0.476 | LONG: ( (bb_20_15_reclaim_from_lower_recent_3d OR bb_20_20_reclaim_from_lower_recent_3d) AND rsi_long_ok AND above_200 ) \ |
| `bollinger_tight` | short | `earnings_blackout` | N | - | 0.884 | 1/1 | 128 | 0.602 | LONG: ( (bb_20_15_reclaim_from_lower_recent_3d OR bb_20_20_reclaim_from_lower_recent_3d) AND rsi_long_ok AND above_200 ) \ |
| `bollinger_tight_with_smart_money_long` | long | `time_stop_10d` | N | - | 1.27 | 1/4 | 840 | 0.537 | base_fires AND _has_smart_money_buy(s) |
| `bollinger_upper_short` | short | `ma_exit_ema9` | N | - | 1.736 | 2/3 | 129 | 0.527 | (bb_20_20_touch_upper AND rsi_14>65 AND shooting_star AND NOT short_borrow_trap) |
| `bullish_engulfing_support` | long | `time_stop_10d` | N | - | 1.688 | 2/4 | 409 | 0.545 | LONG: (bullish_candle AND (near_s1 OR near_s2 OR at_key_fib) AND obv_bullish) \ |
| `bullish_engulfing_support` | short | `next_pivot_target` | N | - | 0.461 | 0/4 | 582 | 0.794 | LONG: (bullish_candle AND (near_s1 OR near_s2 OR at_key_fib) AND obv_bullish) \ |
| `camarilla_s3_bounce` | long | `next_pivot_target` | N | - | 2.058 | 1/4 | 136 | 0.882 | LONG: (near_cam_s3 AND rsi_14<40 AND obv_bullish) \ |
| `camarilla_s3_bounce` | short | `earnings_blackout` | N | - | -0.28 | 0/1 | 91 | 0.352 | LONG: (near_cam_s3 AND rsi_14<40 AND obv_bullish) \ |
| `cpr_narrow_momentum` | long | `next_pivot_target` | N | - | 2.4 | 1/4 | 273 | 0.751 | LONG: (cpr_narrow_tight AND above_cpr AND rsi_14>50 AND macd_12_26_9_bullish AND above_200) \ |
| `cpr_narrow_momentum` | short | `next_pivot_target` | N | - | 0.668 | 0/4 | 728 | 0.672 | LONG: (cpr_narrow_tight AND above_cpr AND rsi_14>50 AND macd_12_26_9_bullish AND above_200) \ |
| `cup_and_handle_long` | long | `next_pivot_target` | N | - | 2.092 | 3/4 | 164 | 0.866 | ( cup_handle_detected AND price_above_ema_200 AND vol_above_avg AND price_above_ema_50 ) |
| `doji_at_support` | long | `ma_exit_ema9` | N | - | 1.177 | 1/4 | 229 | 0.371 | at_key_fib_wide, doji, near_s1_wide, near_s2_wide, vol_spike_12x |
| `donchian_breakout_long` | long | `next_pivot_target` | N | - | 0.907 | 1/4 | 507 | 0.604 | (dc10_breakout_up AND vol_spike_12x AND macd_12_26_9_bullish AND close_above_open AND close_in_top_40pct_of_range) |
| `donchian_breakout_with_smart_money_long` | long | `next_pivot_target` | N | - | 1.136 | 1/4 | 985 | 0.696 | base_fires AND _has_smart_money_buy(s) |
| `flag_bull_long` | long | `class_time_stop` | N | - | 1.541 | 1/1 | 63 | 0.698 | ( flag_bull_broke AND price_above_ema_200 ) |
| `golden_cross_50_200` | short | `hybrid_50pct_target` | N | - | -0.736 | 0/1 | 84 | 0.512 | LONG: ema_50_200_golden_cross \ |
| `golden_cross_9_21` | long | `next_pivot_target` | N | - | 0.932 | 2/4 | 450 | 0.733 | LONG: (ema_9_21_golden_cross AND price_above_sma_50) \ |
| `golden_cross_9_21` | short | `next_pivot_target` | N | - | 0.588 | 0/4 | 439 | 0.688 | LONG: (ema_9_21_golden_cross AND price_above_sma_50) \ |
| `head_and_shoulders_bottom_long` | long | `time_stop_10d` | N | - | 2.667 | 1/4 | 146 | 0.589 | ( head_shoulders_bottom_detected AND price_above_ema_200 ) |
| `htf_aligned_breakout_long` | long | `next_pivot_target` | N | - | 2.348 | 1/4 | 326 | 0.702 | ( above_prev_high AND vol_above_avg AND htf_aligned_bull ) |
| `inside_bar_breakout` | long | `regime_flip` | N | - | 0.886 | 1/4 | 677 | 0.548 | (inside_bar AND adx>20 AND above_vwap) |
| `insider_cluster_concentrated_sell_short` | short | `next_pivot_target` | N | - | 0.717 | 1/4 | 265 | 0.762 | ( concentrated_sell AND below_ema_200 AND NOT short_borrow_trap ) |
| `institutional_breakout_confirmation_long` | long | `next_pivot_target` | N | - | 1.745 | 1/4 | 642 | 0.793 | ( institutional_buy AND resistance_break_retest AND price_above_ema_200 AND close_above_open ) |
| `institutional_cluster_long` | long | `time_stop_10d` | N | - | 1.078 | 1/4 | 2451 | 0.539 | ( institutional_strong_buy AND price_above_ema_200 ) |
| `institutional_committed_growth_long` | long | `time_stop_10d` | N | - | 1.205 | 1/4 | 1941 | 0.547 | ( n_grow>=3 AND price_above_ema_200 ) |
| `institutional_high_conviction_long` | long | `ma_exit_ema9` | N | - | 0.955 | 1/4 | 2473 | 0.355 | ( institutional_new_positions>=3 AND price_above_ema_50 ) |
| `institutional_insider_combo_long` | long | `time_stop_10d` | N | - | 1.14 | 1/4 | 2751 | 0.534 | ( (institutional_buy OR insider_cluster_active) AND price_above_ema_200 ) |
| `institutional_multi_quarter_persistence_long` | long | `time_stop_10d` | N | - | 1.111 | 1/4 | 2516 | 0.537 | ( persistent_holders_4q>=5 AND price_above_ema_200 ) |
| `institutional_oversold_long` | long | `time_stop_10d` | N | - | 1.495 | 1/4 | 386 | 0.531 | ( institutional_buy AND rsi_14<40 AND price_above_ema_200 ) |
| `institutional_persistence_breakout_long` | long | `next_pivot_target` | N | - | 1.787 | 1/4 | 532 | 0.788 | ( institutional_increased>=3 AND resistance_break_retest AND price_above_ema_200 ) |
| `institutional_persistence_momentum_long` | long | `regime_flip` | N | - | 1.138 | 1/4 | 2324 | 0.545 | ( institutional_increased>=3 AND macd_12_26_9_bullish AND price_above_ema_50 ) |
| `institutional_persistence_oversold_long` | long | `time_stop_10d` | N | - | 1.205 | 1/4 | 716 | 0.552 | ( institutional_increased>=3 AND rsi_14<45 AND price_above_ema_200 ) |
| `institutional_persistence_volume_long` | long | `ma_exit_ema9` | N | - | 1.223 | 1/4 | 1199 | 0.405 | ( institutional_increased>=3 AND vol_above_avg AND price_above_ema_50 ) |
| `institutional_persistent_holders_long` | long | `time_stop_10d` | N | - | 1.098 | 1/4 | 1955 | 0.538 | ( institutional_increased>=5 AND price_above_ema_200 ) |
| `institutional_recent_init_momentum_long` | long | `time_stop_10d` | N | - | 1.182 | 1/4 | 2268 | 0.53 | ( institutional_new_positions>=2 AND macd_12_26_9_bullish AND (price_above_ema_200 OR price_above_ema_50) ) |
| `institutional_recent_init_volume_long` | long | `ma_exit_ema9` | N | - | 1.131 | 1/4 | 1075 | 0.399 | ( institutional_new_positions>=2 AND vol_above_avg AND price_above_ema_50 ) |
| `institutional_strong_conviction_long` | long | `time_stop_10d` | N | - | 1.179 | 1/4 | 1826 | 0.542 | ( institutional_increased>=5 AND institutional_new_positions>=2 AND price_above_ema_200 ) |
| `institutional_volume_confirmation_long` | long | `next_pivot_target` | N | - | 0.992 | 1/4 | 1387 | 0.722 | ( institutional_buy AND vol_above_avg AND price_above_ema_50 ) |
| `m_and_a_target_long` | long | `earnings_blackout` | N | - | 0.883 | 1/4 | 1023 | 0.583 | [Producer boolean] 8k_item_1_01_filed_within_30d (fires when producer emits True) |
| `macd_bullish_with_smart_money_long` | long | `next_pivot_target` | N | - | 1.825 | 1/4 | 1162 | 0.787 | base_fires AND _has_smart_money_buy(s) |
| `macd_crossover_short` | short | `class_time_stop` | N | - | 0.701 | 1/4 | 1524 | 0.495 | macd_12_26_9_crossover_dn AND NOT short_borrow_trap |
| `mmbm_long` | long | `r_multiple_3r` | N | - | 0.926 | 1/4 | 1337 | 0.302 | [Producer boolean] po3_mmbm_setup (fires when producer emits True) |
| `naked_poc_retest_long` | long | `time_stop_10d` | N | - | 1.24 | 1/4 | 1788 | 0.536 | ( naked_poc_count>0 AND naked_poc_nearest_distance_pct<0.02 AND price_above_ema_200 ) |
| `news_momentum_long` | long | `regime_flip` | N | - | 0.854 | 1/1 | 106 | 0.623 | ( news_sentiment_5d>=0.3 AND news_volume_zscore_5d>=1.0 AND dc20_breakout_up AND close_above_open AND close_in_top_40pct_of_range AND vol_above_avg ) |
| `news_sentiment_long` | long | `next_pivot_target` | N | - | 1.46 | 1/4 | 906 | 0.786 | ( news_sentiment_mean>0.3 AND news_article_count>=3 AND price_above_ema_200 ) |
| `news_sentiment_shift_long` | long | `next_pivot_target` | N | - | 1.348 | 1/4 | 357 | 0.776 | ( news_sentiment_shift>0.3 AND news_article_count>=2 AND price_above_ema_200 ) |
| `orb_stocks_in_play_short` | short | `regime_flip` | N | - | 1.319 | 1/2 | 108 | 0.463 | ( gap_dn_1_5pct AND close_below_open AND vol_spike_2x AND below_ema_200 AND NOT short_borrow_trap) |
| `pead_long_high_yoy_growth_only` | long | `time_stop_10d` | N | - | 1.217 | 3/4 | 2116 | 0.556 | ( within_pead_window AND yoy_surprise_high ) |
| `pead_short` | short | `r_multiple_2r` | N | - | 1.093 | 1/4 | 872 | 0.299 | ( within_pead_window AND pead_negative_surprise AND NOT short_borrow_trap) |
| `pead_with_smart_money_long` | long | `time_stop_10d` | N | - | 2.175 | 2/4 | 656 | 0.579 | base_fires AND _has_smart_money_buy(s) |
| `pivot_r1_breakout` | long | `reverse_signal` | N | - | 2.368 | 2/4 | 407 | 0.479 | LONG: ( above_r1 AND vol_spike_15x AND macd_12_26_9_bullish AND avwap_long_ok ) \ |
| `pivot_r1_breakout` | short | `breakeven_plus_trail` | N | - | 0.073 | 0/4 | 453 | 0.247 | LONG: ( above_r1 AND vol_spike_15x AND macd_12_26_9_bullish AND avwap_long_ok ) \ |
| `pivot_s1_bounce` | long | `next_pivot_target` | N | - | 1.721 | 1/4 | 360 | 0.844 | LONG: (near_s1 AND (hammer OR bullish_pin_bar) AND obv_bullish) \ |
| `pivot_s1_bounce` | short | `regime_flip` | N | - | 0.013 | 0/1 | 98 | 0.418 | LONG: (near_s1 AND (hammer OR bullish_pin_bar) AND obv_bullish) \ |
| `po3_bullish` | long | `time_stop_10d` | N | - | 0.925 | 2/4 | 731 | 0.547 | ( po3_bullish AND price_above_ema_200 ) |
| `poc_magnet_long` | long | `next_pivot_target` | N | - | 1.476 | 2/4 | 589 | 0.825 | ( vp_close_near_poc_pct<0.03 AND vp_close_above_poc AND price_above_ema_200 ) |
| `prev_day_high_break` | long | `regime_flip` | N | - | 1.487 | 2/4 | 636 | 0.618 | LONG: (above_prev_high AND vol_spike_12x AND above_vwap) \ |
| `prev_day_high_break` | short | `breakeven_plus_trail` | N | - | 0.177 | 0/4 | 788 | 0.269 | LONG: (above_prev_high AND vol_spike_12x AND above_vwap) \ |
| `prev_day_low_bounce` | long | `next_pivot_target` | N | - | 1.792 | 1/4 | 405 | 0.84 | LONG: (near_prev_low AND hammer AND cmf_positive) \ |
| `prev_day_low_bounce` | short | `class_time_stop` | N | - | 1.16 | 2/3 | 172 | 0.529 | LONG: (near_prev_low AND hammer AND cmf_positive) \ |
| `rsi_oversold_with_smart_money_long` | long | `time_stop_10d` | N | - | 1.14 | 1/4 | 2753 | 0.534 | base_fires AND _has_smart_money_buy(s) |
| `rsi_volume_200ema` | long | `ma_exit_ema9` | N | - | 2.072 | 1/4 | 233 | 0.429 | LONG: (rsi_14<40 AND vol_above_avg AND price_above_ema_200) \ |
| `rsi_volume_200ema` | short | `ma_exit_ema9` | N | - | 1.588 | 1/4 | 315 | 0.489 | LONG: (rsi_14<40 AND vol_above_avg AND price_above_ema_200) \ |
| `smc_breaker_block_long` | long | `next_pivot_target` | N | - | 1.295 | 2/4 | 948 | 0.824 | ( smc_breaker_block_bullish AND price_above_ema_200 ) |
| `smc_discount_long` | long | `time_stop_10d` | N | - | 0.915 | 1/4 | 333 | 0.541 | ( smc_in_discount_zone AND (smc_bos_bullish OR smc_choch_bullish) AND price_above_ema_200 ) |
| `smc_ote_long` | long | `chandelier_3x` | N | - | 0.969 | 1/4 | 228 | 0.053 | ( smc_ote_long_zone AND (smc_bos_bullish OR smc_choch_bullish) ) |
| `squeeze_breakout` | long | `class_time_stop` | N | - | 1.378 | 2/4 | 1141 | 0.607 | [Producer boolean] squeeze_fire_up (fires when producer emits True) |
| `stoch_oversold` | long | `chandelier_3x` | N | - | 0.57 | 0/2 | 115 | 0.07 | LONG: (stoch_broad_oversold AND stoch_bullish_cross AND price_above_ema_20) \ |
| `stoch_oversold` | short | `class_time_stop` | N | - | 1.062 | 1/3 | 169 | 0.497 | LONG: (stoch_broad_oversold AND stoch_bullish_cross AND price_above_ema_20) \ |
| `triangle_ascending_long` | long | `r_multiple_3r` | N | - | 1.895 | 2/4 | 330 | 0.309 | ( triangle_ascending_detected AND price_above_ema_200 ) |
| `ultimate_oscillator` | long | `next_pivot_target` | N | - | 2.205 | 1/4 | 206 | 0.85 | LONG: ( (uo_oversold OR (rsi_2<5)) AND price_above_sma_200 AND close_above_open ) \ |
| `ultimate_oscillator` | short | `breakeven_plus_trail` | N | - | 0.427 | 0/4 | 386 | 0.256 | LONG: ( (uo_oversold OR (rsi_2<5)) AND price_above_sma_200 AND close_above_open ) \ |
| `value_area_breakout_long` | long | `r_multiple_2r` | N | - | 1.967 | 1/4 | 375 | 0.392 | ( vp_above_value_area AND vol_above_avg AND price_above_ema_200 ) |
| `week_opening_gap_fill_up` | long | `class_time_stop` | N | - | 1.795 | 2/4 | 834 | 0.712 | ( bool(week_open_gap_down_15pct) AND days_since_last_earnings>2 ) |
| `xs_combined_momentum_low_ivol` | long | `chandelier_3x` | N | - | 1.81 | 1/3 | 211 | 0.152 | ( xs_momentum_top_quintile AND xs_ivol_decile<=4 AND price_above_ema_200 ) |
| `xs_low_beta_with_smart_money_long` | long | `next_pivot_target` | N | - | 1.544 | 2/4 | 452 | 0.832 | base_fires AND _has_smart_money_buy(s) |
| `xs_momentum_quality_combined` | long | `time_stop_10d` | N | - | 1.426 | 2/3 | 163 | 0.601 | ( xs_momentum_top_quintile AND xs_quality_top_quintile AND price_above_ema_200 ) |
| `xs_momentum_top_decile` | long | `next_pivot_target` | N | - | 2.474 | 3/4 | 253 | 0.838 | ( xs_momentum_top_decile AND xs_avoid_high_ivol AND xs_avoid_high_max AND price_above_ema_200 ) |
| `xs_momentum_with_smart_money_long` | long | `time_stop_10d` | N | - | 1.573 | 3/4 | 658 | 0.602 | ( xs_momentum_top_decile AND price_above_ema_200 ) |
| `xs_quality_top_quintile_long` | long | `time_stop_10d` | N | - | 1.419 | 1/2 | 85 | 0.647 | ( xs_quality_top_tercile AND price_above_ema_200 ) |

## B. Regime-conditional strategies (exit varies by entry regime)

| Strategy | Dir | Best Exit | Regime-Cond | Regimes->Exit | OOS Sharpe (best fold) | Folds>=0.7 | n | WR | Entry gate (compact) |
|---|---|---|---|---|---|---|---|---|---|
| `52w_high_breakout_with_smart_money_vol_below_long` | long | `next_pivot_target` | Y | bull:next_pivot_target(1.329), bear:time_stop_20d(0.271) | 2.191 | 2/4 | 203 | 0.813 | [Producer boolean] base_fires (fires when producer emits True) |
| `donchian_breakout_retest_long` | long | `multi_tier_partial` | Y | bear:r_multiple_2r(0.605), bull:multi_tier_partial(0.45) | 0.786 | 1/4 | 547 | 0.378 | (dc20_resistance_break_retest_strong AND vol_below_avg AND macd_12_26_9_bullish AND close_above_open AND close_in_top_40pct_of_range) |
| `double_bottom_long` | long | `time_stop_10d` | Y | bear:r_multiple_2r(1.332), bull:class_time_stop(0.249) | 1.385 | 1/4 | 287 | 0.537 | ( double_bottom_detected AND price_above_ema_200 AND close_in_top_40pct_of_range ) |
| `hammer_at_support_long` | long | `class_time_stop` | Y | bear:class_time_stop(2.236), bull:r_multiple_2r(0.403) | 1.887 | 1/2 | 110 | 0.582 | (hammer AND (near_s1 OR near_s2 OR bb_20_20_touch_lower) AND rsi_14<35) |
| `mfi_oversold_with_smart_money_long` | long | `r_multiple_2r` | Y | bear:chandelier_3x(1.05), bull:ma_exit_ema9(0.702) | 2.111 | 2/4 | 242 | 0.401 | base_fires AND _has_smart_money_buy(s) |
| `morning_star` | long | `class_time_stop` | Y | bear:breakeven_plus_trail(0.564), neutral:breakeven_plus_trail(0.267), bull:r_multiple_2r(0.151) | 1.228 | 1/4 | 1053 | 0.532 | LONG: (morning_star AND rsi_14<45) \ |
| `morning_star` | short | `regime_flip` | Y | bear:breakeven_plus_trail(0.564), neutral:breakeven_plus_trail(0.267), bull:r_multiple_2r(0.151) | 0.5 | 0/4 | 1227 | 0.455 | LONG: (morning_star AND rsi_14<45) \ |
| `r1_break_retest` | long | `class_time_stop` | Y | neutral:class_time_stop(1.508), bear:next_pivot_target(0.563), bull:breakeven_plus_trail(0.14) | 0.782 | 1/4 | 1727 | 0.553 | LONG: (r1_break_retest_long AND above_r1 AND macd_12_26_9_bullish AND close_above_open AND close_in_top_40pct_of_range AND vol_below_avg AND above_avwap_20low) \ |
| `r1_break_retest` | short | `r_multiple_2r` | Y | neutral:class_time_stop(1.508), bear:next_pivot_target(0.563), bull:breakeven_plus_trail(0.14) | 0.692 | 0/4 | 1644 | 0.313 | LONG: (r1_break_retest_long AND above_r1 AND macd_12_26_9_bullish AND close_above_open AND close_in_top_40pct_of_range AND vol_below_avg AND above_avwap_20low) \ |
| `risk_off_bond_equity_short` | short | `regime_flip` | Y | bull:breakeven_plus_trail(0.454), bear:hybrid_50pct_target(-0.417), neutral:earnings_blackout(-1.405) | 0.699 | 0/4 | 1895 | 0.417 | risk_off_regime_bond_signal_strong AND NOT short_borrow_trap |
| `shooting_star_short` | short | `ma_exit_ema9` | Y | bear:next_pivot_target(1.188), bull:ma_exit_ema9(0.354) | 2.713 | 2/4 | 250 | 0.52 | ((shooting_star OR bearish_pin_bar OR hanging_man OR dark_cloud_cover) AND (near_r1 OR near_r2 OR bb_20_20_touch_upper) AND rsi_14>65 AND NOT short_borrow_trap) |
| `smc_equal_lows_sweep_long` | long | `chandelier_3x` | Y | bear:class_time_stop(1.245), bull:breakeven_plus_trail(0.334) | 1.049 | 1/4 | 382 | 0.149 | ( smc_equal_lows_swept AND smc_fvg_bullish_active ) |
| `smc_fvg_retest_short` | short | `multi_tier_partial` | Y | bull:breakeven_plus_trail(0.151), bear:multi_tier_partial(-0.052) | 0.266 | 0/4 | 288 | 0.347 | ( smc_fvg_retest_short_zone AND below_ema_200 AND NOT short_borrow_trap) |
| `squeeze_breakout_with_smart_money_long` | long | `time_stop_10d` | Y | bear:time_stop_20d(1.382), bull:breakeven_plus_trail(0.136) | 1.217 | 1/4 | 1139 | 0.595 | ( squeeze_fire_up AND close_above_open ) |
| `supertrend_macd_short` | short | `multi_tier_partial` | Y | bear:multi_tier_partial(0.442), bull:hybrid_50pct_target(0.182) | 1.184 | 1/4 | 268 | 0.366 | (supertrend_bearish AND macd_12_26_9_bearish AND adx>20 AND NOT short_borrow_trap) |
| `three_white_soldiers` | long | `hybrid_50pct_target` | Y | neutral:class_time_stop(1.47), bear:breakeven_plus_trail(0.276), bull:r_multiple_2r(0.238) | 0.456 | 0/4 | 1596 | 0.549 | (three_white_soldiers AND rsi_14<60) |
| `totm_long` | long | `ma_exit_ema9` | Y | bear:r_multiple_2r(1.715), bull:breakeven_plus_trail(0.325) | 1.462 | 2/4 | 343 | 0.394 | is_totm_window_first_day AND price_above_ema_200 |
| `turtle_soup_long` | long | `r_multiple_2r` | Y | bull:r_multiple_2r(0.789), bear:breakeven_plus_trail(0.666) | 1.266 | 2/4 | 324 | 0.367 | ( smc_liquidity_swept_dn AND above_prev_low AND close_above_open ) |
| `vix_backwardation_long` | long | `time_stop_10d` | Y | bear:time_stop_20d(1.964), bull:breakeven_plus_trail(0.55) | 1.849 | 2/3 | 543 | 0.617 | ( vix_term_backwardation AND xs_quality_decile>=7 ) |

## Appendix - entry-gate formulas (exact `fires` expression)

### Non-conditional

- **`52w_high_breakout_pullback_long`** (long, breakout): ``(predicate not extracted - read source)`` | signals: near_52w_high_retest_long
- **`awesome_oscillator`** (dual, momentum): ``fl = (s.get("ao_cross_up") and s.get("price_above_ema_20")) <br> fs = (s.get("ao_cross_dn") and s.get("below_ema_20")) and not _short_borrow_trap_active(s)`` | signals: ao_cross_dn, ao_cross_up, below_ema_20, price_above_ema_20
- **`bollinger_tight`** (dual, mean_reversion): ``fl = ( (s.get("bb_20_15_reclaim_from_lower_recent_3d") or s.get("bb_20_20_reclaim_from_lower_recent_3d")) and rsi_long_ok and above_200 ) <br> fs = ( (s.get("bb_20_15_reclaim_from_upper_recent_3d") or s.get("bb_20_20_reclaim_from_upper_recent_3d")...`` | signals: bb_20_15_reclaim_from_lower_recent_3d, bb_20_15_reclaim_from_upper_recent_3d, bb_20_20_reclaim_from_lower_recent_3d, ...
- **`bollinger_tight_with_smart_money_long`** (long, smart_money_sleeve): ``(predicate not extracted - read source)`` | signals: bb_20_15_squeeze, bb_20_20_squeeze, close_above_open, price_above_ema_200
- **`bollinger_upper_short`** (short, mean_reversion): ``fires = (s.get("bb_20_20_touch_upper") and s.get("rsi_14", 50) > 65 and  # B1201: was >70 s.get("shooting_star") and not _short_borrow_trap_active(s))`` | signals: bb_20_20_touch_upper, rsi_14, shooting_star
- **`bullish_engulfing_support`** (dual, candle): ``fl = (bullish_candle and (s.get("near_s1") or s.get("near_s2") or s.get("at_key_fib")) and s.get("obv_bullish")) <br> fs = (bearish_candle and (s.get("near_r1") or s.get("near_r2") or s.get("at_key_fib")) and s.get("obv_bearish") and not _short_bo...`` | signals: at_key_fib, bearish_engulfing, bearish_pin_bar, bullish_engulfing, bullish_pin_bar, evening_star, morning_star, near_...
- **`camarilla_s3_bounce`** (dual, pivot): ``fl = (s.get("near_cam_s3") and s.get("rsi_14", 50) < 40 and s.get("obv_bullish")) <br> fs = (s.get("near_cam_r3") and s.get("rsi_14", 50) > 60 and s.get("obv_bearish")) and not _short_borrow_trap_active(s)`` | signals: near_cam_r3, near_cam_s3, obv_bearish, obv_bullish, rsi_14
- **`cpr_narrow_momentum`** (dual, confluence): ``fl = (s.get("cpr_narrow_tight") and s.get("above_cpr") and s.get("rsi_14", 50) > 50 and s.get("macd_12_26_9_bullish") and above_200) <br> fs = (s.get("cpr_narrow_tight") and s.get("below_cpr") and s.get("rsi_14", 50) < 50 and s.get("macd_12_26_9_b...`` | signals: above_cpr, below_cpr, below_ema_200, cpr_narrow_tight, macd_12_26_9_bearish, macd_12_26_9_bullish, price_above_ema_20...
- **`cup_and_handle_long`** (long, chart_pattern): ``fires = ( s.get("cup_handle_detected", False) and s.get("price_above_ema_200", False) and s.get("vol_above_avg", False)  # B1133 loosened from vol_spike_2x and s.get("price_above_ema_50", False) # B1133 dropped: rsi_14<70 (redundant with EMA trend...`` | signals: cup_handle_detected, price_above_ema_200, price_above_ema_50, vol_above_avg
- **`doji_at_support`** (long, candle): `close - open\` | signals: < 5% of today's (high - low) range -- indecision candle (buyers and sellers equally matched)<br>- OR today's close within +/-1.50% of pivot S1 (B574 doji-only wider tolerance variant)<br>- OR today's close within +/-1.50% of pivot S2 (B574 doji-only)<br>- OR today's volume >= 1.2x the 20-day average volume (B589 owner-tightened for smart-money sleeves)
- **`donchian_breakout_long`** (long, breakout): ``fires = (s.get("dc10_breakout_up") and s.get("vol_spike_12x") and s.get("macd_12_26_9_bullish") and s.get("close_above_open") and s.get("close_in_top_40pct_of_range"))`` | signals: close_above_open, close_in_top_40pct_of_range, dc10_breakout_up, macd_12_26_9_bullish, vol_spike_12x
- **`donchian_breakout_with_smart_money_long`** (long, smart_money_sleeve): ``(predicate not extracted - read source)`` | signals: close_above_open, dc20_breakout_up
- **`flag_bull_long`** (long, chart_pattern): ``fires = ( s.get("flag_bull_broke", False)         # B618: breakout-occurred gate and s.get("price_above_ema_200", False) )`` | signals: flag_bull_broke, price_above_ema_200
- **`golden_cross_50_200`** (dual, trend): ``(predicate not extracted - read source)`` | signals: ema_50_200_death_cross, ema_50_200_golden_cross
- **`golden_cross_9_21`** (dual, trend): ``fl = (s.get("ema_9_21_golden_cross") and s.get("price_above_sma_50")) <br> fs = (s.get("ema_9_21_death_cross") and s.get("below_sma_50")) and not _short_borrow_trap_active(s)`` | signals: below_sma_50, ema_9_21_death_cross, ema_9_21_golden_cross, price_above_sma_50
- **`head_and_shoulders_bottom_long`** (long, chart_pattern): ``fires = ( s.get("head_shoulders_bottom_detected", False) and s.get("price_above_ema_200", False) )`` | signals: head_shoulders_bottom_detected, price_above_ema_200
- **`htf_aligned_breakout_long`** (long, multi_timeframe): ``fires = ( s.get("above_prev_high", False) and s.get("vol_above_avg", False) and s.get("htf_aligned_bull", False) )`` | signals: above_prev_high, htf_aligned_bull, vol_above_avg
- **`inside_bar_breakout`** (long, breakout): ``fires = (s.get("inside_bar") and s.get("adx", 0) > 20 and  # B1158: was s.get("adx_trending") (which is adx > 25) s.get("above_vwap"))`` | signals: above_vwap, adx, adx_trending, inside_bar
- **`insider_cluster_concentrated_sell_short`** (short, event_driven): ``fires = ( s.get("concentrated_sell", False) and s.get("below_ema_200", False) and not _short_borrow_trap_active(s) )`` | signals: below_ema_200, concentrated_sell
- **`institutional_breakout_confirmation_long`** (long, smart_money_13f): ``fires = ( s.get("institutional_buy", False) and s.get("resistance_break_retest", False) and s.get("price_above_ema_200", False) and s.get("close_above_open", False) )`` | signals: close_above_open, institutional_buy, price_above_ema_200, resistance_break_retest
- **`institutional_cluster_long`** (long, smart_money_13f): ``fires = ( s.get("institutional_strong_buy", False) and s.get("price_above_ema_200", False) )`` | signals: institutional_increased, institutional_new_positions, institutional_strong_buy, price_above_ema_200
- **`institutional_committed_growth_long`** (long, institutional_persistence): ``fires = ( committed_growth_ok and s.get("price_above_ema_200", False) )`` | signals: committed_growth_holders, institutional_increased, price_above_ema_200
- **`institutional_high_conviction_long`** (long, smart_money_13f): ``fires = ( s.get("institutional_new_positions", 0) >= 3 and s.get("price_above_ema_50", False) )`` | signals: institutional_new_positions, price_above_ema_50
- **`institutional_insider_combo_long`** (long, smart_money_combo): ``fires = ( (s.get("institutional_buy", False) or s.get("insider_cluster_active", False)) and s.get("price_above_ema_200", False) )`` | signals: insider_cluster_active, institutional_buy, price_above_ema_200
- **`institutional_multi_quarter_persistence_long`** (long, institutional_persistence): ``fires = ( s.get("persistent_holders_4q", 0) >= 5  # B1164: was institutional_persistence_strong (>=10) and s.get("price_above_ema_200", False) )`` | signals: persistent_holders_4q, price_above_ema_200, total_active_holders
- **`institutional_oversold_long`** (long, smart_money_13f): ``fires = ( s.get("institutional_buy", False) and s.get("rsi_14", 50) < 40  # B1141: was < 35 and s.get("price_above_ema_200", False) )`` | signals: institutional_buy, price_above_ema_200, rsi_14
- **`institutional_persistence_breakout_long`** (long, institutional_persistence): ``fires = ( s.get("institutional_increased", 0) >= 3  # B1163: was >= 5 and s.get("resistance_break_retest", False) and s.get("price_above_ema_200", False) )`` | signals: institutional_increased, price_above_ema_200, resistance_break_retest
- **`institutional_persistence_momentum_long`** (long, institutional_persistence): ``fires = ( s.get("institutional_increased", 0) >= 3  # B1163: was >= 5 and s.get("macd_12_26_9_bullish", False) and s.get("price_above_ema_50", False) )`` | signals: institutional_increased, macd_12_26_9_bullish, price_above_ema_50
- **`institutional_persistence_oversold_long`** (long, institutional_persistence): ``fires = ( s.get("institutional_increased", 0) >= 3  # B1160: was >= 5 and s.get("rsi_14", 50) < 45  # B1160: was < 40 and s.get("price_above_ema_200", False) )`` | signals: institutional_increased, price_above_ema_200, rsi_14
- **`institutional_persistence_volume_long`** (long, institutional_persistence): ``fires = ( s.get("institutional_increased", 0) >= 3  # B1141: was >= 5 and s.get("vol_above_avg", False)  # B1141: was vol_spike_2x and s.get("price_above_ema_50", False) )`` | signals: institutional_increased, price_above_ema_50, vol_above_avg
- **`institutional_persistent_holders_long`** (long, institutional_persistence): ``fires = ( s.get("institutional_increased", 0) >= 5 and s.get("price_above_ema_200", False) )`` | signals: institutional_increased, price_above_ema_200
- **`institutional_recent_init_momentum_long`** (long, institutional_persistence): ``fires = ( s.get("institutional_new_positions", 0) >= 2 and s.get("macd_12_26_9_bullish", False) and (s.get("price_above_ema_200", False) or s.get("price_above_ema_50", False)) )`` | signals: institutional_new_positions, macd_12_26_9_bullish, price_above_ema_200, price_above_ema_50
- **`institutional_recent_init_volume_long`** (long, institutional_persistence): ``fires = ( s.get("institutional_new_positions", 0) >= 2 and s.get("vol_above_avg", False) and s.get("price_above_ema_50", False) )`` | signals: institutional_new_positions, price_above_ema_50, vol_above_avg
- **`institutional_strong_conviction_long`** (long, institutional_persistence): ``fires = ( s.get("institutional_increased", 0) >= 5 and s.get("institutional_new_positions", 0) >= 2 and s.get("price_above_ema_200", False) )`` | signals: institutional_increased, institutional_new_positions, price_above_ema_200
- **`institutional_volume_confirmation_long`** (long, smart_money_13f): ``fires = ( s.get("institutional_buy", False) and s.get("vol_above_avg", False)  # B1141: was vol_spike_2x (Lo-Wang canonical broad-participation) and s.get("price_above_ema_50", False) )`` | signals: institutional_buy, price_above_ema_50, vol_above_avg
- **`m_and_a_target_long`** (long, sec_edgar_sleeve): ``(predicate not extracted - read source)`` | signals: 8k_item_1_01_filed_within_30d
- **`macd_bullish_with_smart_money_long`** (long, smart_money_sleeve): ``(predicate not extracted - read source)`` | signals: macd_12_26_9_bullish, price_above_ema_200
- **`macd_crossover_short`** (short, momentum): ``(predicate not extracted - read source)`` | signals: macd_12_26_9_crossover_dn
- **`mmbm_long`** (long, ict): ``(predicate not extracted - read source)`` | signals: po3_mmbm_setup
- **`naked_poc_retest_long`** (long, volume_profile): ``fires = ( s.get("naked_poc_count", 0) > 0 and s.get("naked_poc_nearest_distance_pct", 1.0) < 0.02 and s.get("price_above_ema_200", False) )`` | signals: naked_poc_count, naked_poc_nearest_distance_pct, price_above_ema_200
- **`news_momentum_long`** (long, news_sentiment): ``fires = ( s.get("news_sentiment_5d", 0.0) >= 0.3  # B1136: was >= 0.5 and s.get("news_volume_zscore_5d", 0.0) >= 1.0  # B1136: was >= 1.5 and s.get("dc20_breakout_up", False) and s.get("close_above_open", False) and s.get("close_in_top_40pct_of_ra...`` | signals: close_above_open, close_in_top_40pct_of_range, dc20_breakout_up, news_sentiment_5d, news_volume_zscore_5d, vol_above_avg
- **`news_sentiment_long`** (long, news_sentiment): ``fires = ( s.get("news_sentiment_mean", 0.0) > 0.3  # B1136: was > 0.5 (Lopez-Lira-Tang 2023) and s.get("news_article_count", 0) >= 3 and s.get("price_above_ema_200", False) )`` | signals: news_article_count, news_sentiment_mean, price_above_ema_200
- **`news_sentiment_shift_long`** (long, news_sentiment): ``fires = ( s.get("news_sentiment_shift", 0.0) > 0.3  # B1203: was > 0.4 and s.get("news_article_count", 0) >= 2 and s.get("price_above_ema_200", False) )`` | signals: news_article_count, news_sentiment_shift, price_above_ema_200
- **`orb_stocks_in_play_short`** (short, orb): ``fires = ( s.get("gap_dn_1_5pct", False) and s.get("close_below_open", False) and s.get("vol_spike_2x", False) and s.get("below_ema_200", False)  # B630 sweep and not _short_borrow_trap_active(s))`` | signals: below_ema_200, close_below_open, gap_dn_1_5pct, gap_dn_pct, vol_spike_2x
- **`pead_long_high_yoy_growth_only`** (long, event_driven): ``fires = ( s.get("within_pead_window", False) and s.get("yoy_surprise_high", False) )`` | signals: earnings_eps_yoy_growth, within_pead_window, yoy_surprise_high, yoy_surprise_threshold_long
- **`pead_short`** (short, event_driven): ``fires = ( s.get("within_pead_window", False) and s.get("pead_negative_surprise", False) and not _short_borrow_trap_active(s))`` | signals: earnings_announcement_return, earnings_eps_yoy_growth, pead_negative_surprise, within_pead_window
- **`pead_with_smart_money_long`** (long, smart_money_sleeve): ``(predicate not extracted - read source)`` | signals: pead_positive_surprise, within_pead_window
- **`pivot_r1_breakout`** (dual, pivot): ``fl = ( s.get("above_r1") and s.get("vol_spike_15x") and s.get("macd_12_26_9_bullish") and avwap_long_ok ) <br> fs = ( s.get("below_s1") and s.get("vol_spike_15x") and s.get("macd_12_26_9_bearish") and avwap_short_ok and not _short_borrow_trap_acti...`` | signals: above_avwap_50low, above_r1, below_avwap_50low, below_s1, macd_12_26_9_bearish, macd_12_26_9_bullish, vol_spike_15x
- **`pivot_s1_bounce`** (dual, pivot): ``fl = (s.get("near_s1") and (s.get("hammer") or s.get("bullish_pin_bar")) and s.get("obv_bullish")) <br> fs = (s.get("near_r1") and (s.get("shooting_star") or s.get("bearish_engulfing")) and s.get("obv_bearish") and not _short_borrow_trap_active(s))`` | signals: bearish_engulfing, bullish_pin_bar, hammer, near_r1, near_s1, obv_bearish, obv_bullish, shooting_star
- **`po3_bullish`** (long, po3): ``fires = ( s.get("po3_bullish", False) and s.get("price_above_ema_200", False) )`` | signals: po3_bullish, price_above_ema_200
- **`poc_magnet_long`** (long, volume_profile): ``fires = ( s.get("vp_close_near_poc_pct", 1.0) < 0.03  # B1201: 0.02 -> 0.03 spirit-match and s.get("vp_close_above_poc", False) and s.get("price_above_ema_200", False) )`` | signals: price_above_ema_200, vp_close_above_poc, vp_close_near_poc_pct
- **`prev_day_high_break`** (dual, pivot): ``fl = (s.get("above_prev_high") and s.get("vol_spike_12x") and s.get("above_vwap")) <br> fs = (s.get("below_prev_low") and s.get("vol_spike_12x") and s.get("below_vwap")) and not _short_borrow_trap_active(s)`` | signals: above_prev_high, above_vwap, below_prev_low, below_vwap, vol_spike_12x
- **`prev_day_low_bounce`** (dual, pivot): ``fl = (s.get("near_prev_low") and s.get("hammer") and s.get("cmf_positive")) <br> fs = (s.get("near_prev_high") and s.get("shooting_star") and s.get("cmf_negative")) and not _short_borrow_trap_active(s)`` | signals: cmf_negative, cmf_positive, hammer, near_prev_high, near_prev_low, shooting_star
- **`rsi_oversold_with_smart_money_long`** (long, smart_money_sleeve): ``(predicate not extracted - read source)`` | signals: price_above_ema_200, rsi_14
- **`rsi_volume_200ema`** (dual, confluence): ``fl = (s.get("rsi_14", 50) < 40 and s.get("vol_above_avg") and s.get("price_above_ema_200")) <br> fs = (s.get("rsi_14", 50) > 60 and s.get("vol_above_avg") and s.get("below_ema_200")) and not _short_borrow_trap_active(s)`` | signals: below_ema_200, price_above_ema_200, rsi_14, vol_above_avg
- **`smc_breaker_block_long`** (long, smc): ``fires = ( s.get("smc_breaker_block_bullish", False) and s.get("price_above_ema_200", False) )`` | signals: price_above_ema_200, smc_breaker_block_bullish
- **`smc_discount_long`** (long, smc): ``fires = ( s.get("smc_in_discount_zone", False) and (s.get("smc_bos_bullish", False) or s.get("smc_choch_bullish", False)) and s.get("price_above_ema_200", False) )`` | signals: price_above_ema_200, smc_bos_bullish, smc_choch_bullish, smc_dealing_range_pct, smc_in_discount_zone
- **`smc_ote_long`** (long, smc): ``fires = ( s.get("smc_ote_long_zone", False) and (s.get("smc_bos_bullish", False) or s.get("smc_choch_bullish", False)) )`` | signals: smc_bos_bullish, smc_choch_bullish, smc_ote_long_zone, smc_retracement_pct
- **`squeeze_breakout`** (long, breakout): ``(predicate not extracted - read source)`` | signals: squeeze_fire_up
- **`stoch_oversold`** (dual, mean_reversion): ``fl = (s.get("stoch_broad_oversold")  # B1199: was stoch_oversold (<20) and s.get("stoch_bullish_cross") and s.get("price_above_ema_20")) <br> fs = (s.get("stoch_broad_overbought")  # B1199: was stoch_overbought and s.get("stoch_bearish_cross") and...`` | signals: below_ema_20, price_above_ema_20, stoch_bearish_cross, stoch_broad_overbought, stoch_broad_oversold, stoch_bullish_cross
- **`triangle_ascending_long`** (long, chart_pattern): ``fires = ( s.get("triangle_ascending_detected", False) and s.get("price_above_ema_200", False) )`` | signals: price_above_ema_200, triangle_ascending_detected
- **`ultimate_oscillator`** (dual, momentum): ``fl = ( (s.get("uo_oversold") or (rsi_2 < 5)) and s.get("price_above_sma_200") and s.get("close_above_open")          # B631 (a) ) <br> fs = ( (s.get("uo_overbought") or (rsi_2 > 95)) and s.get("below_sma_200") and s.get("close_below_open") and not...`` | signals: below_sma_200, close_above_open, close_below_open, price_above_sma_200, rsi_2, uo, uo_overbought, uo_oversold
- **`value_area_breakout_long`** (long, volume_profile): ``fires = ( s.get("vp_above_value_area", False) and s.get("vol_above_avg", False) and s.get("price_above_ema_200", False) )`` | signals: price_above_ema_200, vol_above_avg, vp_above_value_area
- **`week_opening_gap_fill_up`** (long, ict): ``fires = ( bool(s.get("week_open_gap_down_15pct", False)) and s.get("days_since_last_earnings", 999) > 2 )`` | signals: days_since_last_earnings, week_open_gap_down_15pct
- **`xs_combined_momentum_low_ivol`** (long, factor): ``fires = ( s.get("xs_momentum_top_quintile", False)  # B1193: was top_decile and s.get("xs_ivol_decile", 5) <= 4   # B1193: was <=3; bottom 40% IVOL and s.get("price_above_ema_200", False) )`` | signals: price_above_ema_200, xs_ivol_decile, xs_momentum_top_quintile
- **`xs_low_beta_with_smart_money_long`** (long, smart_money_sleeve): ``(predicate not extracted - read source)`` | signals: price_above_ema_200, xs_low_beta_top_quintile
- **`xs_momentum_quality_combined`** (long, factor): ``fires = ( s.get("xs_momentum_top_quintile", False)  # B1193: was top_decile and s.get("xs_quality_top_quintile", False)  # already quintile and s.get("price_above_ema_200", False) )`` | signals: price_above_ema_200, xs_momentum_top_quintile, xs_quality_top_quintile
- **`xs_momentum_top_decile`** (long, factor): ``fires = ( s.get("xs_momentum_top_decile", False) and s.get("xs_avoid_high_ivol", True) and s.get("xs_avoid_high_max", True) and s.get("price_above_ema_200", False) )`` | signals: price_above_ema_200, xs_avoid_high_ivol, xs_avoid_high_max, xs_momentum_top_decile
- **`xs_momentum_with_smart_money_long`** (long, smart_money_sleeve): ``fires = ( s.get("xs_momentum_top_decile", False) and s.get("price_above_ema_200", False) )`` | signals: price_above_ema_200, xs_momentum_top_decile
- **`xs_quality_top_quintile_long`** (long, factor): ``fires = ( s.get("xs_quality_top_tercile", False)  # B1193: was xs_quality_top_quintile and s.get("price_above_ema_200", False) )`` | signals: price_above_ema_200, xs_quality_top_tercile

### Regime-conditional

- **`52w_high_breakout_with_smart_money_vol_below_long`** (long, smart_money_sleeve): ``(predicate not extracted - read source)`` | signals: close_above_open, close_in_top_40pct_of_range, institutional_buy, near_52w_high_95pct, vol_below_avg
- **`donchian_breakout_retest_long`** (long, breakout): ``fires = (s.get("dc20_resistance_break_retest_strong") and s.get("vol_below_avg") and s.get("macd_12_26_9_bullish") and s.get("close_above_open") and s.get("close_in_top_40pct_of_range"))`` | signals: close_above_open, close_in_top_40pct_of_range, dc20_resistance_break_retest_strong, macd_12_26_9_bullish, vol_below_avg
- **`double_bottom_long`** (long, chart_pattern): ``fires = ( s.get("double_bottom_detected", False) and s.get("price_above_ema_200", False) and s.get("close_in_top_40pct_of_range", False)  # B730 anti-fakeout strong-close (retained) # B1133 dropped: vol_spike_15x (loosest B730 gate per Council 249) )`` | signals: close_in_top_40pct_of_range, double_bottom_detected, price_above_ema_200
- **`hammer_at_support_long`** (long, candle): ``fires = (s.get("hammer") and (s.get("near_s1") or s.get("near_s2") or s.get("bb_20_20_touch_lower")) and s.get("rsi_14", 50) < 35)`` | signals: bb_20_20_touch_lower, hammer, near_s1, near_s2, rsi_14
- **`mfi_oversold_with_smart_money_long`** (long, smart_money_sleeve): ``(predicate not extracted - read source)`` | signals: mfi_broad_oversold, price_above_ema_200
- **`morning_star`** (dual, candle): ``fl = (s.get("morning_star") and s.get("rsi_14", 50) < 45) <br> fs = (s.get("evening_star") and s.get("rsi_14", 50) > 55) and not _short_borrow_trap_active(s)`` | signals: evening_star, morning_star, rsi_14
- **`r1_break_retest`** (dual, pivot): ``fl = (s.get("r1_break_retest_long") and s.get("above_r1") and s.get("macd_12_26_9_bullish") and s.get("close_above_open") and s.get("close_in_top_40pct_of_range") and s.get("vol_below_avg") and s.get("above_avwap_20low")) <br> fs = (s.get("s1_brea...`` | signals: above_avwap_20low, above_r1, below_avwap_20high, below_s1, close_above_open, close_below_open, close_in_bottom_40pct_...
- **`risk_off_bond_equity_short`** (short, cross_asset): ``(predicate not extracted - read source)`` | signals: risk_off_regime_bond_signal_strong
- **`shooting_star_short`** (short, candle): ``fires = ((s.get("shooting_star") or s.get("bearish_pin_bar") or s.get("hanging_man") or s.get("dark_cloud_cover")) and (s.get("near_r1") or s.get("near_r2") or s.get("bb_20_20_touch_upper")) and s.get("rsi_14", 50) > 65 and not _short_borrow_trap_...`` | signals: bb_20_20_touch_upper, bearish_pin_bar, dark_cloud_cover, hanging_man, near_r1, near_r2, rsi_14, shooting_star
- **`smc_equal_lows_sweep_long`** (long, smc): ``fires = ( s.get("smc_equal_lows_swept", False) and s.get("smc_fvg_bullish_active", False) )`` | signals: smc_equal_lows_swept, smc_fvg_bullish_active
- **`smc_fvg_retest_short`** (short, smc): ``fires = ( s.get("smc_fvg_retest_short_zone", False) and s.get("below_ema_200", False)  # B630 sweep and not _short_borrow_trap_active(s))`` | signals: below_ema_200, smc_fvg_retest_short_zone
- **`squeeze_breakout_with_smart_money_long`** (long, smart_money_sleeve): ``fires = ( s.get("squeeze_fire_up", False) and s.get("close_above_open", True) )`` | signals: close_above_open, squeeze_fire_up
- **`supertrend_macd_short`** (short, trend): ``fires = (s.get("supertrend_bearish") and s.get("macd_12_26_9_bearish") and s.get("adx", 0) > 20 and not _short_borrow_trap_active(s))`` | signals: adx, macd_12_26_9_bearish, supertrend_bearish
- **`three_white_soldiers`** (long, candle): ``fires = (s.get("three_white_soldiers") and s.get("rsi_14", 50) < 60)`` | signals: rsi_14, three_white_soldiers
- **`totm_long`** (long, calendar): ``(predicate not extracted - read source)`` | signals: is_totm_window_first_day, price_above_ema_200
- **`turtle_soup_long`** (long, ict): ``fires = ( s.get("smc_liquidity_swept_dn", False) and s.get("above_prev_low", False)     # B616: closed back ABOVE prior-day-low and s.get("close_above_open", False)   # bullish reversal bar )`` | signals: above_prev_low, below_prev_low, close_above_open, smc_liquidity_swept_dn
- **`vix_backwardation_long`** (long, cross_asset): ``fires = ( s.get("vix_term_backwardation", False) and s.get("xs_quality_decile", 0) >= 7  # B1164: was >= 8 )`` | signals: vix_term_backwardation, xs_quality_decile