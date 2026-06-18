# Phase 1A-beta single-batch per-(strategy x exit) forensic

> **B909 SUPERSEDED-BY-NOTICE (2026-06-19 per owner directive Dec-2 update in place):** This doc was authored Batch 376 (2026-05-26) per owner directive to forensically analyze single-batch Phase 1A-β run from `output_phase_1a_beta_single_local/`. **Superseded-by-effect:**
> - **Phase 1A-β R4 cube data:** `output_batch395_final/` (2026-05-31; 29,360 trades; canonical R4 source)
> - **Phase 1A-β R5 readiness + Path to 1B-α:** [PATH_TO_PHASE_1B_ALPHA.md](PATH_TO_PHASE_1B_ALPHA.md) (B894 canonical)
> - **R4 quiet/low-fire diagnosis:** [output_audit/b900_r4_quiet_low_fire_audit.json](output_audit/b900_r4_quiet_low_fire_audit.json) (B900; per-strategy categorization)
> - **R4 calibration drift forensic findings:** EXECUTION_QUEUE.md B902-MISSED-K1 RESOLVED B908 ticket
>
> Single-batch forensic findings below retained for batch-lineage traceability (B376 pre-R4 era). Forward-looking forensic work uses output_batch395_final/ + b900 audit JSON + post-B907 measurement framework.

**Source:** owner directive 2026-05-26 - pause next Phase 1A-beta + optimize each strategy and exit. Generated from output_phase_1a_beta_single_local/ artifacts.

## Headline
- 361 trades / 31 strategies fired / 154 quiet (active but zero fires)
- Cube: 17 strategies x 25 exits = 425 populated cells (vs 185x25=4625 possible)
- Verdict: 158 verdict-cube rows / ALL  (DEC-426 Gate-1 n>=30 fails universally)
- Cells with n>=5 (smallest sample for any decision): 425

## Section 1: Per-strategy fired (31 strategies)

| strategy | n_trades | win_rate | sum_pnl_pct | mean_pnl_pct | median_hold |
|---|---:|---:|---:|---:|---:|
| buyback_8k_recent_long | 86 | 27.9 | 78.1 | 0.908 | 39.0 |
| orb_stocks_in_play_long | 66 | 36.4 | 205.84 | 3.119 | 33.5 |
| xs_low_beta_long | 28 | 17.9 | -91.83 | -3.28 | 42.5 |
| htf_aligned_breakout_long | 24 | 37.5 | 274.89 | 11.454 | 61.5 |
| xs_quality_top_quintile_long | 22 | 22.7 | 112.38 | 5.108 | 36.5 |
| orb_stocks_in_play_short | 21 | 42.9 | -18.21 | -0.867 | 8.0 |
| po3_bullish | 19 | 47.4 | -1.83 | -0.097 | 21.0 |
| vix_backwardation_long | 9 | 33.3 | -14.96 | -1.663 | 29.0 |
| force_index_breakout | 8 | 25.0 | -53.88 | -6.734 | 51.0 |
| xs_momentum_top_decile | 8 | 37.5 | -15.22 | -1.903 | 21.0 |
| avwap_50_reclaim | 7 | 0.0 | -66.07 | -9.439 | 9.0 |
| pead_long | 6 | 16.7 | -123.8 | -20.633 | 19.0 |
| pre_fomc_long_sleeve | 6 | 50.0 | -0.09 | -0.015 | 27.0 |
| camarilla_r3_breakout | 6 | 16.7 | 4.09 | 0.681 | 8.5 |
| monthly_bias_momentum_long | 5 | 20.0 | 39.5 | 7.899 | 280.0 |
| htf_aligned_breakout_short | 5 | 60.0 | 42.15 | 8.429 | 2.0 |
| po3_bearish | 5 | 40.0 | -16.48 | -3.296 | 2.0 |
| volume_spike_breakout | 4 | 25.0 | 1.28 | 0.32 | 86.5 |
| avwap_252_breakout | 4 | 0.0 | -30.32 | -7.579 | 13.5 |
| insider_cluster_long | 3 | 0.0 | -27.32 | -9.106 | 20.0 |
| pairs_mean_reversion_long | 3 | 33.3 | -7.29 | -2.43 | 107.0 |
| pead_short | 3 | 33.3 | -14.82 | -4.938 | 14.0 |
| hull_rsi | 2 | 0.0 | -3.1 | -1.552 | 164.0 |
| xs_combined_momentum_low_ivol | 2 | 50.0 | -1.08 | -0.54 | 191.5 |
| xs_momentum_bottom_decile_short | 2 | 100.0 | 8.38 | 4.192 | 21.0 |
| stochrsi_overbought_short | 2 | 0.0 | -3.06 | -1.532 | 76.0 |
| cmf_flip | 1 | 0.0 | -5.44 | -5.435 | 11.0 |
| macd_fast_crossover | 1 | 100.0 | 3.66 | 3.658 | 211.0 |
| cpr_narrow_bullish | 1 | 0.0 | -13.36 | -13.356 | 45.0 |
| pre_rebalance_long | 1 | 0.0 | -0.2 | -0.201 | 7.0 |
| pivot_s3_capitulation | 1 | 0.0 | -0.16 | -0.158 | 71.0 |

## Section 2: Quiet-strategy dominant skip reasons (154 strategies)

Strategies that fired 0 trades. Dominant reason indicates the primary gate preventing fires.

| strategy | skipped_count | dominant_reason |
|---|---:|---|
| break_retest_volume | 13302 | portfolio_gate_max_open_positions_25_reached |
| break_retest_confluence | 13189 | portfolio_gate_max_open_positions_25_reached |
| cpr_narrow_momentum | 12671 | portfolio_gate_max_open_positions_25_reached |
| donchian_10_breakout_retest | 11214 | portfolio_gate_max_open_positions_25_reached |
| r1_break_retest | 11180 | portfolio_gate_max_open_positions_25_reached |
| supertrend_macd | 10871 | portfolio_gate_max_open_positions_25_reached |
| institutional_buy_momentum_long | 10503 | portfolio_gate_max_open_positions_25_reached |
| institutional_cluster_long | 10104 | portfolio_gate_max_open_positions_25_reached |
| institutional_breakout_confirmation_long | 9989 | portfolio_gate_max_open_positions_25_reached |
| institutional_persistent_holders_long | 9801 | portfolio_gate_max_open_positions_25_reached |
| prev_day_high_break | 9320 | no_next_bar |
| pivot_r1_breakout | 9314 | no_next_bar |
| institutional_persistence_momentum_long | 9259 | portfolio_gate_max_open_positions_25_reached |
| institutional_persistence_breakout_long | 8739 | portfolio_gate_max_open_positions_25_reached |
| 52wh_break_retest | 7553 | no_next_bar |
| volume_spike_breakout_retest | 6978 | no_next_bar |
| naked_poc_retest_long | 6844 | no_next_bar |
| ichimoku_cloud_breakout | 6821 | portfolio_gate_max_open_positions_25_reached |
| halloween_seasonal_long | 6596 | portfolio_gate_max_open_positions_25_reached |
| value_area_breakout_long | 6348 | no_next_bar |
| dc20_break_retest | 5833 | no_next_bar |
| donchian_10_breakout | 5407 | no_next_bar |
| institutional_volume_confirmation_long | 4964 | no_next_bar |
| poc_magnet_long | 4893 | no_next_bar |
| totm_long | 4655 | portfolio_gate_max_open_positions_25_reached |
| po3_htf_aligned_long | 4012 | no_next_bar |
| institutional_persistence_volume_long | 3951 | portfolio_gate_max_open_positions_25_reached |
| institutional_multi_quarter_persistence_long | 3598 | portfolio_gate_max_open_positions_25_reached |
| supertrend_ichimoku_adx | 2869 | no_next_bar |
| double_bottom_long | 2838 | portfolio_gate_max_open_positions_25_reached |
| institutional_committed_growth_long | 2828 | portfolio_gate_max_open_positions_25_reached |
| adx_initiation | 2748 | portfolio_gate_max_open_positions_25_reached |
| pairs_mean_reversion_short | 2425 | portfolio_gate_max_open_positions_25_reached |
| macd_crossover | 2413 | portfolio_gate_max_open_positions_25_reached |
| macd_ichimoku | 2326 | portfolio_gate_max_open_positions_25_reached |
| pivot_r2_continuation | 2008 | no_next_bar |
| hull_rsi_short | 1571 | portfolio_gate_max_open_positions_15_reached |
| cpr_narrow_momentum_short | 1479 | portfolio_gate_max_open_positions_15_reached |
| prev_day_low_breakdown | 1326 | portfolio_gate_max_open_positions_15_reached |
| donchian_breakdown_retest_short | 1256 | portfolio_gate_max_open_positions_15_reached |
| news_sentiment_long | 1164 | portfolio_gate_max_open_positions_25_reached |
| ppo_crossover | 1004 | portfolio_gate_max_open_positions_25_reached |
| tema_dema | 997 | portfolio_gate_max_open_positions_25_reached |
| roc_burst | 990 | portfolio_gate_max_open_positions_25_reached |
| ichimoku_tk_cross | 938 | no_next_bar |
| pivot_s1_bounce | 801 | regime_affinity_block_bull_batch203 |
| cup_and_handle_retest_long | 797 | portfolio_gate_max_open_positions_25_reached |
| risk_off_bond_equity_short | 755 | portfolio_gate_max_open_positions_15_reached |
| parabolic_sar_flip | 690 | portfolio_gate_max_open_positions_25_reached |
| golden_cross_9_21 | 584 | portfolio_gate_max_open_positions_25_reached |
| awesome_oscillator | 576 | portfolio_gate_max_open_positions_25_reached |
| pre_holiday_long | 547 | portfolio_gate_max_open_positions_25_reached |
| bollinger_upper_short | 529 | regime_affinity_block_bull_batch203 |
| news_sentiment_shift_long | 520 | portfolio_gate_max_open_positions_25_reached |
| institutional_with_directors_long | 460 | portfolio_gate_max_open_positions_25_reached |
| 52w_high_breakout | 460 | no_next_bar |
| golden_cross_20_50 | 454 | portfolio_gate_max_open_positions_25_reached |
| institutional_increased_with_directors_long | 446 | portfolio_gate_max_open_positions_25_reached |
| macd_crossover_short | 440 | regime_affinity_block_bull_batch203 |
| prev_day_low_bounce | 363 | regime_affinity_block_bull_batch203 |
| head_and_shoulders_bottom_long | 357 | portfolio_gate_max_open_positions_25_reached |
| supertrend_macd_short | 342 | regime_affinity_block_bull_batch203 |
| inside_bar_breakout | 299 | portfolio_gate_max_open_positions_25_reached |
| donchian_breakdown_short | 274 | portfolio_gate_max_open_positions_15_reached |
| xs_momentum_quality_combined | 244 | portfolio_gate_max_open_positions_25_reached |
| ultimate_oscillator | 232 | regime_affinity_block_bear_batch203 |
| po3_htf_aligned_short | 227 | portfolio_gate_max_open_positions_15_reached |
| institutional_with_officers_long | 188 | portfolio_gate_max_open_positions_25_reached |
| golden_cross_50_200 | 180 | portfolio_gate_max_open_positions_25_reached |
| insider_cluster_with_director_long | 177 | portfolio_gate_max_open_positions_25_reached |
| institutional_insider_combo_long | 177 | portfolio_gate_max_open_positions_25_reached |
| parabolic_sar_flip_short | 156 | regime_affinity_block_bull_batch203 |
| cup_and_handle_long | 151 | portfolio_gate_max_open_positions_25_reached |
| flag_bull_long | 150 | portfolio_gate_max_open_positions_25_reached |
| flag_bull_retest_long | 150 | portfolio_gate_max_open_positions_25_reached |
| three_white_soldiers | 139 | regime_affinity_block_bear_batch203 |
| bollinger_tight | 121 | regime_affinity_block_bear_batch203 |
| january_effect_small_cap_long | 94 | portfolio_gate_max_open_positions_25_reached |
| institutional_distribution_short | 82 | portfolio_gate_max_open_positions_15_reached |
| golden_cross_volume | 64 | portfolio_gate_max_open_positions_25_reached |
| bollinger_lower | 56 | portfolio_gate_max_open_positions_15_reached |
| institutional_capitulation_short | 44 | regime_affinity_block_bull_batch203 |
| pre_fomc_quality_momentum_long | 43 | portfolio_gate_max_open_positions_25_reached |
| bullish_engulfing_support | 41 | portfolio_gate_max_open_positions_25_reached |
| ichimoku_cloud_breakdown | 35 | regime_affinity_block_bull_batch203 |
| rsi_oversold | 31 | regime_affinity_block_bear_batch203 |
| death_cross_50_200_volume | 23 | regime_affinity_block_bull_batch203 |
| pead_with_insider_confirmation_long | 22 | portfolio_gate_max_open_positions_25_reached |
| post_inclusion_drift_long | 22 | portfolio_gate_max_open_positions_25_reached |
| post_inclusion_reversal_short | 22 | portfolio_gate_max_open_positions_25_reached |
| stochrsi_oversold | 21 | regime_affinity_block_bear_batch203 |
| williams_r_oversold | 20 | regime_affinity_block_bear_batch203 |
| pivot_s2_bounce | 15 | portfolio_gate_max_open_positions_15_reached |
| camarilla_s3_bounce | 14 | portfolio_gate_max_open_positions_15_reached |
| 52w_low_breakdown | 9 | portfolio_gate_max_open_positions_15_reached |
| pivot_fib_confluence | 7 | portfolio_gate_max_open_positions_25_reached |
| post_deletion_drift_short | 5 | portfolio_gate_max_open_positions_15_reached |
| mfi_oversold | 4 | portfolio_gate_max_open_positions_25_reached |
| institutional_persistence_oversold_long | 4 | regime_affinity_block_bear_batch203 |
| doji_at_support | 2 | regime_affinity_block_bear_batch203 |
| institutional_oversold_long | 1 | regime_affinity_block_bear_batch203 |
| stoch_oversold | 1 | portfolio_gate_max_open_positions_25_reached |
| morning_star | 1 | regime_affinity_block_bear_batch203 |
| keltner_lower | 1 | EVENT_SUPPRESSION_CPI_d0_dec348 |
| rsi_volume_200ema | 1 | regime_affinity_block_bear_batch203 |
| bb_squeeze_volume | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| classification_change_with_institutional_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| classification_change_with_insider_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| classification_change_volume_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| classification_change_to_tech_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| classification_change_to_defensive_short | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| classification_change_recent_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| classification_change_oversold_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| classification_change_momentum_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| classification_change_from_tech_short | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| classification_change_breakout_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| camarilla_rsi_obv_short | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| camarilla_rsi_obv | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| avwap_20high_rejection_short | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| evening_star_short | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| gold_silver_risk_off_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| institutional_strong_conviction_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| institutional_high_conviction_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| institutional_recent_init_momentum_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| institutional_recent_init_volume_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_breaker_block_short | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_choch_reversal | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| shooting_star_short | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| sector_rotation_defensive_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| rsi_overbought_short | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| rsi21_slow | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| rsi9_extreme | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_breaker_block_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_bos_retest_entry | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_bos_continuation | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_fvg_retest_short | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_discount_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_equal_highs_sweep_short | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_premium_short | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| squeeze_breakout | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_ote_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_ote_short | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_order_block_bounce | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_mitigation_block_short | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_liquidity_sweep_reversal | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_mitigation_block_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_fvg_retest_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_equal_lows_sweep_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| smc_inverse_fvg | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| triangle_ascending_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| triangle_ascending_retest_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| weekly_bias_pullback_long | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| weekly_bias_pullback_short | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |
| williams_stoch_dual | 0 | PRODUCER_LAYER_ZERO_CANDIDATES |

## Section 3: Cube cells with n>=5 trades

Top 30 of 425 eligible cells (verdict requires n>=30 per DEC-426 Gate 1; this list shows cells with at least n=5).

| strategy | exit_method | n | win_rate | sum_pnl | mean_pnl |
|---|---|---:|---:|---:|---:|
| buyback_8k_recent_long | breakeven_plus_trail | 86 | 31.4 | 327.5 | 3.808 |
| buyback_8k_recent_long | break_even_at_1r | 86 | 10.5 | -38.25 | -0.445 |
| buyback_8k_recent_long | ma_exit_ema9 | 86 | 39.5 | 68.83 | 0.8 |
| buyback_8k_recent_long | hybrid_50pct_target | 86 | 58.1 | 237.66 | 2.764 |
| buyback_8k_recent_long | fixed_4r_2r | 86 | 33.7 | 65.8 | 0.765 |
| buyback_8k_recent_long | earnings_blackout | 86 | 58.1 | 3178.59 | 36.96 |
| buyback_8k_recent_long | atr_trail_vix_conditional | 86 | 23.3 | -50.43 | -0.586 |
| buyback_8k_recent_long | atr_trail_mae_conditional | 86 | 23.3 | -120.19 | -1.398 |
| buyback_8k_recent_long | atr_trail_2x | 86 | 33.7 | 15.18 | 0.177 |
| buyback_8k_recent_long | atr_trail_1x | 86 | 23.3 | -120.19 | -1.398 |
| buyback_8k_recent_long | chandelier_3x | 86 | 31.4 | -2.68 | -0.031 |
| buyback_8k_recent_long | class_time_stop | 86 | 48.8 | 60.92 | 0.708 |
| buyback_8k_recent_long | r_multiple_2r | 86 | 36.0 | 37.04 | 0.431 |
| buyback_8k_recent_long | r_multiple_3r | 86 | 26.7 | 34.56 | 0.402 |
| buyback_8k_recent_long | regime_flip | 86 | 59.3 | 226.98 | 2.639 |
| buyback_8k_recent_long | reverse_signal | 86 | 23.3 | -120.19 | -1.398 |
| buyback_8k_recent_long | smc_mitigation_zone | 86 | 23.3 | -120.19 | -1.398 |
| buyback_8k_recent_long | time_stop_10d | 86 | 46.5 | 37.14 | 0.432 |
| buyback_8k_recent_long | time_stop_20d | 86 | 59.3 | 226.98 | 2.639 |
| buyback_8k_recent_long | trailing_10pct | 86 | 34.9 | 199.21 | 2.316 |
| buyback_8k_recent_long | trailing_15pct | 86 | 36.0 | 401.26 | 4.666 |
| buyback_8k_recent_long | trailing_5pct | 86 | 23.3 | -68.49 | -0.796 |
| buyback_8k_recent_long | mfe_lockin_trail | 86 | 23.3 | -126.78 | -1.474 |
| buyback_8k_recent_long | multi_tier_partial | 86 | 45.3 | -69.4 | -0.807 |
| buyback_8k_recent_long | next_pivot_target | 86 | 59.3 | 124.27 | 1.445 |
| orb_stocks_in_play_long | class_time_stop | 66 | 63.6 | 224.78 | 3.406 |
| orb_stocks_in_play_long | earnings_blackout | 66 | 71.2 | 4031.55 | 61.084 |
| orb_stocks_in_play_long | r_multiple_3r | 66 | 40.9 | 184.1 | 2.789 |
| orb_stocks_in_play_long | hybrid_50pct_target | 66 | 65.2 | 299.48 | 4.538 |
| orb_stocks_in_play_long | fixed_4r_2r | 66 | 51.5 | 286.05 | 4.334 |

## Section 4: Quiet-reason bucket counts

| dominant_reason | n_strategies | implication |
|---|---:|---|
| portfolio_gate_max_open_positions_25_reached | 56 | Cap-saturation - Batch 370 Fix 1 raised to 59 unblocks (next run) |
| PRODUCER_LAYER_ZERO_CANDIDATES | 49 | Strategy never produces a candidate - producer wiring bug |
| no_next_bar | 15 | End-of-data edge - normal for terminal dates |
| portfolio_gate_max_open_positions_15_reached | 13 | Bear cap saturation - Batch 203 intentional risk control |
| regime_affinity_block_bear_batch203 | 11 | Bear narrowing - Batch 370 Fix 2 restored 4 calendar strategies (next run) |
| regime_affinity_block_bull_batch203 | 9 | Bull narrowing for short strategies - intentional |
| EVENT_SUPPRESSION_CPI_d0_dec348 | 1 | Macro event blackout - DEC-348 |
