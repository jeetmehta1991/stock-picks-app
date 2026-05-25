# Phase 1A-beta forensic re-categorization

**Source** (per CHECKLIST #77 canonical-source attribution):
- Trade log: `output_phase_1a_beta_merged_local\trade_log.csv` (7191 trades, 66 fired strategies)
- Bucket lists: PHASE_1A_BETA_QUIET_STRATEGY_FORENSIC.md
- Generator: `scripts/forensic_phase1a_beta_recat.py` (Batch 352)

**Verdict legend:**
- `QUIET`: 0 trades fired in Phase 1A-beta
- `RARE`: 1-19 trades (sub-threshold for per-regime statistical power)
- `NORMAL`: 20+ trades

## Cat-A_Tight

**Verdict counts:** {'QUIET': 14}

| Strategy | n | WR% | Mean PnL% | Sum pp | Verdict |
|---|---:|---:|---:|---:|---|
| `52w_high_breakout` | 0 | - | - | - | QUIET |
| `52w_low_breakdown` | 0 | - | - | - | QUIET |
| `52wh_break_retest` | 0 | - | - | - | QUIET |
| `bb_squeeze_volume` | 0 | - | - | - | QUIET |
| `squeeze_breakout` | 0 | - | - | - | QUIET |
| `cup_and_handle_long` | 0 | - | - | - | QUIET |
| `head_and_shoulders_bottom_long` | 0 | - | - | - | QUIET |
| `double_bottom_long` | 0 | - | - | - | QUIET |
| `triangle_ascending_long` | 0 | - | - | - | QUIET |
| `flag_bull_long` | 0 | - | - | - | QUIET |
| `inside_bar_breakout` | 0 | - | - | - | QUIET |
| `pre_holiday_long` | 0 | - | - | - | QUIET |
| `halloween_seasonal_long` | 0 | - | - | - | QUIET |
| `totm_long` | 0 | - | - | - | QUIET |

## Cat-B_Data-Missing

**Verdict counts:** {'QUIET': 20}

| Strategy | n | WR% | Mean PnL% | Sum pp | Verdict |
|---|---:|---:|---:|---:|---|
| `post_inclusion_drift_long` | 0 | - | - | - | QUIET |
| `post_inclusion_reversal_short` | 0 | - | - | - | QUIET |
| `post_deletion_drift_short` | 0 | - | - | - | QUIET |
| `pre_rebalance_long` | 0 | - | - | - | QUIET |
| `pairs_mean_reversion_long` | 0 | - | - | - | QUIET |
| `pairs_mean_reversion_short` | 0 | - | - | - | QUIET |
| `pre_fomc_long_sleeve` | 0 | - | - | - | QUIET |
| `pre_fomc_quality_momentum_long` | 0 | - | - | - | QUIET |
| `gold_silver_risk_off_long` | 0 | - | - | - | QUIET |
| `dxy_headwind_multinational_short` | 0 | - | - | - | QUIET |
| `sector_rotation_defensive_long` | 0 | - | - | - | QUIET |
| `weekly_bias_pullback_long` | 0 | - | - | - | QUIET |
| `weekly_bias_pullback_short` | 0 | - | - | - | QUIET |
| `smc_equal_highs_sweep_short` | 0 | - | - | - | QUIET |
| `smc_equal_lows_sweep_long` | 0 | - | - | - | QUIET |
| `smc_mitigation_block_long` | 0 | - | - | - | QUIET |
| `smc_mitigation_block_short` | 0 | - | - | - | QUIET |
| `news_sentiment_shift_long` | 0 | - | - | - | QUIET |
| `insider_cluster_with_director_long` | 0 | - | - | - | QUIET |
| `pivot_fib_confluence` | 0 | - | - | - | QUIET |

## Cat-C_Investigate

**Verdict counts:** {'QUIET': 16}

| Strategy | n | WR% | Mean PnL% | Sum pp | Verdict |
|---|---:|---:|---:|---:|---|
| `avwap_20high_rejection_short` | 0 | - | - | - | QUIET |
| `camarilla_rsi_obv` | 0 | - | - | - | QUIET |
| `camarilla_rsi_obv_short` | 0 | - | - | - | QUIET |
| `cpr_narrow_momentum_short` | 0 | - | - | - | QUIET |
| `donchian_10_breakout` | 0 | - | - | - | QUIET |
| `donchian_breakdown_short` | 0 | - | - | - | QUIET |
| `ichimoku_cloud_breakdown` | 0 | - | - | - | QUIET |
| `keltner_lower` | 0 | - | - | - | QUIET |
| `prev_day_low_breakdown` | 0 | - | - | - | QUIET |
| `rsi9_extreme` | 0 | - | - | - | QUIET |
| `rsi_overbought_short` | 0 | - | - | - | QUIET |
| `rsi_volume_200ema` | 0 | - | - | - | QUIET |
| `supertrend_ichimoku_adx` | 0 | - | - | - | QUIET |
| `supertrend_macd_short` | 0 | - | - | - | QUIET |
| `break_retest_volume` | 0 | - | - | - | QUIET |
| `value_area_breakout_long` | 0 | - | - | - | QUIET |

## Un-Deprecated 23 (Batch 316a)

Strategies un-deprecated by Batch 316a 2026-05-25 (Batch 218 deprecation reversed).
At Phase 1A-beta run time, most of these were filtered OUT by Batch 218; few legacy trades remain.

**Verdict counts:** {'QUIET': 23}

| Strategy | n | WR% | Mean PnL% | Sum pp | Verdict |
|---|---:|---:|---:|---:|---|
| `golden_cross_50_200` | 0 | - | - | - | QUIET |
| `golden_cross_9_21` | 0 | - | - | - | QUIET |
| `golden_cross_20_50` | 0 | - | - | - | QUIET |
| `golden_cross_volume` | 0 | - | - | - | QUIET |
| `death_cross_50_200_volume` | 0 | - | - | - | QUIET |
| `awesome_oscillator` | 0 | - | - | - | QUIET |
| `ppo_crossover` | 0 | - | - | - | QUIET |
| `tema_dema` | 0 | - | - | - | QUIET |
| `force_index_breakout` | 0 | - | - | - | QUIET |
| `mfi_oversold` | 0 | - | - | - | QUIET |
| `parabolic_sar_flip` | 0 | - | - | - | QUIET |
| `parabolic_sar_flip_short` | 0 | - | - | - | QUIET |
| `morning_star` | 0 | - | - | - | QUIET |
| `evening_star_short` | 0 | - | - | - | QUIET |
| `three_white_soldiers` | 0 | - | - | - | QUIET |
| `doji_at_support` | 0 | - | - | - | QUIET |
| `bullish_engulfing_support` | 0 | - | - | - | QUIET |
| `shooting_star_short` | 0 | - | - | - | QUIET |
| `williams_stoch_dual` | 0 | - | - | - | QUIET |
| `macd_crossover` | 0 | - | - | - | QUIET |
| `macd_crossover_short` | 0 | - | - | - | QUIET |
| `camarilla_r3_breakout` | 0 | - | - | - | QUIET |
| `camarilla_s3_bounce` | 0 | - | - | - | QUIET |

## Passing-Criteria Verdicts (66 fired strategies)

Per-strategy verdict against CLAUDE.md passing criteria. n>=100 uses overall thresholds (WR>=55, PF>=1.5, Sharpe>=1.0); 30<=n<100 uses per-regime thresholds (WR>=50, PF>=1.3, Sharpe>=0.7).

**Aggregate:** {'PASS': 0, 'FAIL': 32, 'INSUFFICIENT_DATA': 34}

| Strategy | n | WR% | PF | Sharpe | DD pp | Band | Verdict | Failures |
|---|---:|---:|---:|---:|---:|---|---|---|
| `avwap_252_breakout` | 107 | 29.91 | 0.85 | -0.06 | 203.17 | overall | FAIL | wr=29.9 < 55; pf=0.85 < 1.5; sharpe=-0.06 < 1.0; dd=203.2 > 20.0 |
| `avwap_50_reclaim` | 398 | 45.23 | 0.69 | -0.1 | 772.41 | overall | FAIL | wr=45.2 < 55; pf=0.69 < 1.5; sharpe=-0.10 < 1.0; dd=772.4 > 20.0 |
| `bollinger_lower` | 428 | 12.85 | 0.53 | -0.25 | 583.17 | overall | FAIL | wr=12.9 < 55; pf=0.53 < 1.5; sharpe=-0.25 < 1.0; dd=583.2 > 20.0 |
| `bollinger_tight` | 70 | 15.71 | 2.13 | 0.17 | 68.5 | per_regime | FAIL | wr=15.7 < 50; sharpe=0.17 < 0.7; dd=68.5 > 20.0 |
| `buyback_8k_recent_long` | 98 | 20.41 | 0.55 | -0.21 | 385.36 | per_regime | FAIL | wr=20.4 < 50; pf=0.55 < 1.3; sharpe=-0.21 < 0.7; dd=385.4 > 20.0 |
| `cmf_flip` | 125 | 29.6 | 1.26 | 0.07 | 155.62 | overall | FAIL | wr=29.6 < 55; pf=1.26 < 1.5; sharpe=0.07 < 1.0; dd=155.6 > 20.0 |
| `cpr_narrow_bullish` | 750 | 32.13 | 0.6 | -0.16 | 1648.84 | overall | FAIL | wr=32.1 < 55; pf=0.60 < 1.5; sharpe=-0.16 < 1.0; dd=1648.8 > 20.0 |
| `cpr_narrow_momentum` | 177 | 29.94 | 0.48 | -0.2 | 614.02 | overall | FAIL | wr=29.9 < 55; pf=0.48 < 1.5; sharpe=-0.20 < 1.0; dd=614.0 > 20.0 |
| `htf_aligned_breakout_long` | 141 | 29.79 | 1.0 | -0.0 | 202.58 | overall | FAIL | wr=29.8 < 55; pf=1.00 < 1.5; sharpe=-0.00 < 1.0; dd=202.6 > 20.0 |
| `htf_aligned_breakout_short` | 193 | 19.17 | 0.24 | -0.63 | 974.23 | overall | FAIL | wr=19.2 < 55; pf=0.24 < 1.5; sharpe=-0.63 < 1.0; dd=974.2 > 20.0 |
| `hull_rsi` | 420 | 26.19 | 0.47 | -0.28 | 1333.63 | overall | FAIL | wr=26.2 < 55; pf=0.47 < 1.5; sharpe=-0.28 < 1.0; dd=1333.6 > 20.0 |
| `macd_fast_crossover` | 115 | 33.91 | 0.66 | -0.16 | 279.77 | overall | FAIL | wr=33.9 < 55; pf=0.66 < 1.5; sharpe=-0.16 < 1.0; dd=279.8 > 20.0 |
| `monthly_bias_momentum_long` | 501 | 30.74 | 0.87 | -0.05 | 554.62 | overall | FAIL | wr=30.7 < 55; pf=0.87 < 1.5; sharpe=-0.05 < 1.0; dd=554.6 > 20.0 |
| `orb_stocks_in_play_long` | 92 | 29.35 | 1.75 | 0.09 | 94.73 | per_regime | FAIL | wr=29.3 < 50; sharpe=0.09 < 0.7; dd=94.7 > 20.0 |
| `orb_stocks_in_play_short` | 114 | 31.58 | 0.56 | -0.24 | 291.23 | overall | FAIL | wr=31.6 < 55; pf=0.56 < 1.5; sharpe=-0.24 < 1.0; dd=291.2 > 20.0 |
| `pivot_r1_breakout` | 96 | 27.08 | 0.6 | -0.21 | 256.78 | per_regime | FAIL | wr=27.1 < 50; pf=0.60 < 1.3; sharpe=-0.21 < 0.7; dd=256.8 > 20.0 |
| `po3_bearish` | 403 | 23.82 | 0.3 | -0.33 | 1104.31 | overall | FAIL | wr=23.8 < 55; pf=0.30 < 1.5; sharpe=-0.33 < 1.0; dd=1104.3 > 20.0 |
| `po3_bullish` | 416 | 38.22 | 0.75 | -0.11 | 512.69 | overall | FAIL | wr=38.2 < 55; pf=0.75 < 1.5; sharpe=-0.11 < 1.0; dd=512.7 > 20.0 |
| `po3_htf_aligned_long` | 44 | 15.91 | 0.49 | -0.23 | 204.41 | per_regime | FAIL | wr=15.9 < 50; pf=0.49 < 1.3; sharpe=-0.23 < 0.7; dd=204.4 > 20.0 |
| `smc_bos_continuation` | 66 | 24.24 | 0.59 | -0.21 | 149.29 | per_regime | FAIL | wr=24.2 < 50; pf=0.59 < 1.3; sharpe=-0.21 < 0.7; dd=149.3 > 20.0 |
| `smc_choch_reversal` | 274 | 27.74 | 1.0 | 0.0 | 243.29 | overall | FAIL | wr=27.7 < 55; pf=1.00 < 1.5; sharpe=0.00 < 1.0; dd=243.3 > 20.0 |
| `smc_inverse_fvg` | 275 | 28.36 | 0.66 | -0.14 | 566.32 | overall | FAIL | wr=28.4 < 55; pf=0.66 < 1.5; sharpe=-0.14 < 1.0; dd=566.3 > 20.0 |
| `smc_liquidity_sweep_reversal` | 52 | 21.15 | 0.42 | -0.35 | 222.89 | per_regime | FAIL | wr=21.2 < 50; pf=0.42 < 1.3; sharpe=-0.35 < 0.7; dd=222.9 > 20.0 |
| `smc_order_block_bounce` | 69 | 36.23 | 1.07 | 0.02 | 84.84 | per_regime | FAIL | wr=36.2 < 50; pf=1.07 < 1.3; sharpe=0.02 < 0.7; dd=84.8 > 20.0 |
| `stochrsi_overbought_short` | 288 | 35.76 | 0.74 | -0.12 | 449.3 | overall | FAIL | wr=35.8 < 55; pf=0.74 < 1.5; sharpe=-0.12 < 1.0; dd=449.3 > 20.0 |
| `stochrsi_oversold` | 65 | 40.0 | 1.15 | 0.05 | 36.89 | per_regime | FAIL | wr=40.0 < 50; pf=1.15 < 1.3; sharpe=0.05 < 0.7; dd=36.9 > 20.0 |
| `ultimate_oscillator` | 157 | 33.12 | 0.85 | -0.06 | 161.31 | overall | FAIL | wr=33.1 < 55; pf=0.85 < 1.5; sharpe=-0.06 < 1.0; dd=161.3 > 20.0 |
| `williams_r_oversold` | 177 | 39.55 | 1.5 | 0.11 | 118.7 | overall | FAIL | wr=39.5 < 55; sharpe=0.11 < 1.0; dd=118.7 > 20.0 |
| `xs_combined_momentum_low_ivol` | 37 | 21.62 | 0.47 | -0.2 | 164.35 | per_regime | FAIL | wr=21.6 < 50; pf=0.47 < 1.3; sharpe=-0.20 < 0.7; dd=164.4 > 20.0 |
| `xs_low_beta_long` | 344 | 34.88 | 1.21 | 0.05 | 192.64 | overall | FAIL | wr=34.9 < 55; pf=1.21 < 1.5; sharpe=0.05 < 1.0; dd=192.6 > 20.0 |
| `xs_momentum_bottom_decile_short` | 324 | 24.07 | 0.35 | -0.2 | 1902.48 | overall | FAIL | wr=24.1 < 55; pf=0.35 < 1.5; sharpe=-0.20 < 1.0; dd=1902.5 > 20.0 |
| `xs_momentum_top_decile` | 125 | 46.4 | 0.91 | -0.04 | 99.9 | overall | FAIL | wr=46.4 < 55; pf=0.91 < 1.5; sharpe=-0.04 < 1.0; dd=99.9 > 20.0 |
| `adx_initiation` | 4 | 25.0 | 0.25 | -0.65 | 20.62 | per_regime | INSUFFICIENT_DATA | n=4 < 30; wr=25.0 < 50; pf=0.25 < 1.3; sharpe=-0.65 < 0.7; dd=20.6 > 20.0 |
| `bollinger_upper_short` | 6 | 33.33 | 0.98 | -0.01 | 12.77 | per_regime | INSUFFICIENT_DATA | n=6 < 30; wr=33.3 < 50; pf=0.98 < 1.3; sharpe=-0.01 < 0.7 |
| `break_retest_confluence` | 2 | 0.0 | 0.0 | -9.46 | 10.4 | per_regime | INSUFFICIENT_DATA | n=2 < 30; wr=0.0 < 50; pf=0.00 < 1.3; sharpe=-9.46 < 0.7 |
| `dc20_break_retest` | 1 | 0.0 | 0.0 | 0.0 | 0.0 | per_regime | INSUFFICIENT_DATA | n=1 < 30; wr=0.0 < 50; pf=0.00 < 1.3; sharpe=0.00 < 0.7 |
| `hull_rsi_short` | 5 | 20.0 | 0.2 | -0.56 | 20.63 | per_regime | INSUFFICIENT_DATA | n=5 < 30; wr=20.0 < 50; pf=0.20 < 1.3; sharpe=-0.56 < 0.7; dd=20.6 > 20.0 |
| `ichimoku_cloud_breakout` | 15 | 33.33 | 1.59 | 0.16 | 40.86 | per_regime | INSUFFICIENT_DATA | n=15 < 30; wr=33.3 < 50; sharpe=0.16 < 0.7; dd=40.9 > 20.0 |
| `ichimoku_tk_cross` | 10 | 30.0 | 0.51 | -0.31 | 40.33 | per_regime | INSUFFICIENT_DATA | n=10 < 30; wr=30.0 < 50; pf=0.51 < 1.3; sharpe=-0.31 < 0.7; dd=40.3 > 20.0 |
| `insider_cluster_long` | 19 | 21.05 | 0.12 | -0.89 | 96.32 | per_regime | INSUFFICIENT_DATA | n=19 < 30; wr=21.1 < 50; pf=0.12 < 1.3; sharpe=-0.89 < 0.7; dd=96.3 > 20.0 |
| `lead_lag_sector_rotation` | 21 | 23.81 | 1.72 | 0.12 | 65.51 | per_regime | INSUFFICIENT_DATA | n=21 < 30; wr=23.8 < 50; sharpe=0.12 < 0.7; dd=65.5 > 20.0 |
| `macd_ichimoku` | 15 | 13.33 | 0.14 | -0.55 | 170.54 | per_regime | INSUFFICIENT_DATA | n=15 < 30; wr=13.3 < 50; pf=0.14 < 1.3; sharpe=-0.55 < 0.7; dd=170.5 > 20.0 |
| `pivot_r2_continuation` | 1 | 0.0 | 0.0 | 0.0 | 0.0 | per_regime | INSUFFICIENT_DATA | n=1 < 30; wr=0.0 < 50; pf=0.00 < 1.3; sharpe=0.00 < 0.7 |
| `pivot_s1_bounce` | 20 | 45.0 | 2.7 | 0.25 | 30.84 | per_regime | INSUFFICIENT_DATA | n=20 < 30; wr=45.0 < 50; sharpe=0.25 < 0.7; dd=30.8 > 20.0 |
| `pivot_s2_bounce` | 6 | 50.0 | 1.84 | 0.23 | 20.81 | per_regime | INSUFFICIENT_DATA | n=6 < 30; sharpe=0.23 < 0.7; dd=20.8 > 20.0 |
| `pivot_s3_capitulation` | 3 | 33.33 | 0.37 | -0.42 | 10.28 | per_regime | INSUFFICIENT_DATA | n=3 < 30; wr=33.3 < 50; pf=0.37 < 1.3; sharpe=-0.42 < 0.7 |
| `po3_htf_aligned_short` | 18 | 27.78 | 0.81 | -0.07 | 49.9 | per_regime | INSUFFICIENT_DATA | n=18 < 30; wr=27.8 < 50; pf=0.81 < 1.3; sharpe=-0.07 < 0.7; dd=49.9 > 20.0 |
| `prev_day_high_break` | 5 | 40.0 | 0.31 | -0.35 | 65.1 | per_regime | INSUFFICIENT_DATA | n=5 < 30; wr=40.0 < 50; pf=0.31 < 1.3; sharpe=-0.35 < 0.7; dd=65.1 > 20.0 |
| `prev_day_low_bounce` | 11 | 9.09 | 0.02 | -1.27 | 65.1 | per_regime | INSUFFICIENT_DATA | n=11 < 30; wr=9.1 < 50; pf=0.02 < 1.3; sharpe=-1.27 < 0.7; dd=65.1 > 20.0 |
| `r1_break_retest` | 1 | 0.0 | 0.0 | 0.0 | 0.0 | per_regime | INSUFFICIENT_DATA | n=1 < 30; wr=0.0 < 50; pf=0.00 < 1.3; sharpe=0.00 < 0.7 |
| `risk_off_bond_equity_short` | 3 | 0.0 | 0.0 | -1.16 | 10.72 | per_regime | INSUFFICIENT_DATA | n=3 < 30; wr=0.0 < 50; pf=0.00 < 1.3; sharpe=-1.16 < 0.7 |
| `roc_burst` | 4 | 0.0 | 0.0 | -6.69 | 34.72 | per_regime | INSUFFICIENT_DATA | n=4 < 30; wr=0.0 < 50; pf=0.00 < 1.3; sharpe=-6.69 < 0.7; dd=34.7 > 20.0 |
| `rsi21_slow` | 1 | 100.0 | inf | 0.0 | 0.0 | per_regime | INSUFFICIENT_DATA | n=1 < 30; sharpe=0.00 < 0.7 |
| `rsi_oversold` | 1 | 0.0 | 0.0 | 0.0 | 0.0 | per_regime | INSUFFICIENT_DATA | n=1 < 30; wr=0.0 < 50; pf=0.00 < 1.3; sharpe=0.00 < 0.7 |
| `smc_bos_retest_entry` | 14 | 35.71 | 2.75 | 0.33 | 38.19 | per_regime | INSUFFICIENT_DATA | n=14 < 30; wr=35.7 < 50; sharpe=0.33 < 0.7; dd=38.2 > 20.0 |
| `smc_breaker_block_long` | 3 | 66.67 | 0.87 | -0.05 | 9.03 | per_regime | INSUFFICIENT_DATA | n=3 < 30; pf=0.87 < 1.3; sharpe=-0.05 < 0.7 |
| `smc_breaker_block_short` | 24 | 20.83 | 0.28 | -0.56 | 134.12 | per_regime | INSUFFICIENT_DATA | n=24 < 30; wr=20.8 < 50; pf=0.28 < 1.3; sharpe=-0.56 < 0.7; dd=134.1 > 20.0 |
| `smc_discount_long` | 4 | 0.0 | 0.0 | -2.05 | 25.52 | per_regime | INSUFFICIENT_DATA | n=4 < 30; wr=0.0 < 50; pf=0.00 < 1.3; sharpe=-2.05 < 0.7; dd=25.5 > 20.0 |
| `smc_fvg_retest_long` | 2 | 0.0 | 0.0 | -5.33 | 10.65 | per_regime | INSUFFICIENT_DATA | n=2 < 30; wr=0.0 < 50; pf=0.00 < 1.3; sharpe=-5.33 < 0.7 |
| `smc_fvg_retest_short` | 5 | 0.0 | 0.0 | -2.72 | 35.85 | per_regime | INSUFFICIENT_DATA | n=5 < 30; wr=0.0 < 50; pf=0.00 < 1.3; sharpe=-2.72 < 0.7; dd=35.9 > 20.0 |
| `smc_ote_long` | 2 | 50.0 | 0.08 | -0.6 | 0.0 | per_regime | INSUFFICIENT_DATA | n=2 < 30; pf=0.08 < 1.3; sharpe=-0.60 < 0.7 |
| `smc_ote_short` | 7 | 42.86 | 0.81 | -0.09 | 7.14 | per_regime | INSUFFICIENT_DATA | n=7 < 30; wr=42.9 < 50; pf=0.81 < 1.3; sharpe=-0.09 < 0.7 |
| `smc_premium_short` | 13 | 15.38 | 0.08 | -1.19 | 80.35 | per_regime | INSUFFICIENT_DATA | n=13 < 30; wr=15.4 < 50; pf=0.08 < 1.3; sharpe=-1.19 < 0.7; dd=80.4 > 20.0 |
| `stoch_oversold` | 1 | 100.0 | inf | 0.0 | 0.0 | per_regime | INSUFFICIENT_DATA | n=1 < 30; sharpe=0.00 < 0.7 |
| `supertrend_macd` | 2 | 50.0 | 3.48 | 0.39 | 10.0 | per_regime | INSUFFICIENT_DATA | n=2 < 30; sharpe=0.39 < 0.7 |
| `volume_spike_breakout` | 1 | 0.0 | 0.0 | 0.0 | 0.0 | per_regime | INSUFFICIENT_DATA | n=1 < 30; wr=0.0 < 50; pf=0.00 < 1.3; sharpe=0.00 < 0.7 |

## Regime-Bias Breakdown (Batch 354)

### Per-regime aggregate

| Regime | n | WR% | Mean PnL% | Sum pp |
|---|---:|---:|---:|---:|
| bear | 2910 | 25.12 | -2.706 | -7874.97 |
| bull | 3810 | 32.99 | -0.693 | -2641.14 |
| neutral | 471 | 33.97 | -1.849 | -871.04 |

### Worst-5 strategies per regime (largest negative PnL contributors)

#### bear

| Strategy | n | Sum pp | Mean PnL% |
|---|---:|---:|---:|
| `xs_momentum_bottom_decile_short` | 324 | -1855.66 | -5.727 |
| `hull_rsi` | 380 | -1340.88 | -3.529 |
| `htf_aligned_breakout_short` | 188 | -944.52 | -5.024 |
| `po3_bearish` | 350 | -925.53 | -2.644 |
| `cpr_narrow_momentum` | 176 | -572.35 | -3.252 |

#### bull

| Strategy | n | Sum pp | Mean PnL% |
|---|---:|---:|---:|
| `cpr_narrow_bullish` | 642 | -1616.59 | -2.518 |
| `avwap_50_reclaim` | 382 | -722.36 | -1.891 |
| `monthly_bias_momentum_long` | 470 | -411.79 | -0.876 |
| `po3_bullish` | 383 | -274.15 | -0.716 |
| `smc_inverse_fvg` | 97 | -255.43 | -2.633 |

#### neutral

| Strategy | n | Sum pp | Mean PnL% |
|---|---:|---:|---:|
| `xs_low_beta_long` | 30 | -186.59 | -6.22 |
| `po3_bearish` | 53 | -184.99 | -3.49 |
| `smc_choch_reversal` | 34 | -166.13 | -4.886 |
| `po3_bullish` | 33 | -131.16 | -3.975 |
| `pivot_r1_breakout` | 21 | -102.47 | -4.88 |
