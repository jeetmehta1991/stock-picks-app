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

## Per-(strategy x exit_method) cell verdicts -- PRIMARY (Batch 356)

Cell-level pass/fail at the CANONICAL exit_method granularity. Multiple `exit_reason` rows (e.g. fixed_4r_2r_target_hit + fixed_4r_2r_stop_hit) are collapsed into one method (fixed_4r_2r) via EXIT_REASON_TO_METHOD mapping so 2-leg exits do not split into cherry-picked target/stop sub-cells.

**Fired cells**: 167
**Verdict counts**: {'FAIL': 42, 'INSUFFICIENT_DATA': 124, 'PASS': 1}

| Strategy | Exit method | n | WR% | PF | Sharpe | Mean PnL% | Sum pp | Band | Verdict | Failures |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|
| `avwap_50_reclaim` | `atr_trail_1x` | 203 | 4.93 | 0.03 | -0.45 | -10.208 | -2072.16 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `cpr_narrow_bullish` | `atr_trail_1x` | 385 | 17.66 | 0.39 | -0.32 | -4.34 | -1670.92 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `xs_momentum_bottom_decile_short` | `atr_trail_1x` | 314 | 24.2 | 0.38 | -0.19 | -5.106 | -1603.25 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `hull_rsi` | `atr_trail_1x` | 406 | 25.37 | 0.44 | -0.33 | -3.377 | -1371.1 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `po3_bullish` | `atr_trail_1x` | 119 | 0.84 | 0.01 | -2.15 | -8.636 | -1027.74 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `htf_aligned_breakout_short` | `atr_trail_1x` | 187 | 18.72 | 0.23 | -0.65 | -5.183 | -969.18 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `po3_bearish` | `ma_exit_ema9` | 361 | 24.1 | 0.33 | -0.37 | -2.265 | -817.79 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `bollinger_lower` | `atr_trail_1x` | 301 | 0.0 | 0.0 | -2.02 | -2.588 | -778.98 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `monthly_bias_momentum_long` | `atr_trail_1x` | 413 | 25.67 | 0.8 | -0.07 | -1.23 | -507.85 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `smc_inverse_fvg` | `atr_trail_1x` | 248 | 29.03 | 0.72 | -0.11 | -1.578 | -391.46 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `cpr_narrow_momentum` | `atr_trail_1x` | 170 | 30.59 | 0.6 | -0.21 | -2.091 | -355.49 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `po3_bearish` | `atr_trail_1x` | 40 | 20.0 | 0.16 | -0.44 | -7.778 | -311.13 | per_regime | FAIL | wr<50;pf<1.3;sharpe<0.7 |
| `stochrsi_overbought_short` | `atr_trail_1x` | 275 | 37.09 | 0.79 | -0.09 | -1.055 | -290.14 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `cpr_narrow_bullish` | `circuit_breaker` | 13 | 15.38 | 0.03 | -0.97 | -21.752 | -282.78 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `xs_momentum_top_decile` | `atr_trail_1x` | 31 | 3.23 | 0.02 | -2.27 | -9.069 | -281.14 | per_regime | FAIL | wr<50;pf<1.3;sharpe<0.7 |
| `pivot_r1_breakout` | `atr_trail_1x` | 89 | 24.72 | 0.54 | -0.25 | -3.155 | -280.81 | per_regime | FAIL | wr<50;pf<1.3;sharpe<0.7 |
| `orb_stocks_in_play_short` | `atr_trail_1x` | 113 | 31.86 | 0.57 | -0.23 | -2.303 | -260.26 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `buyback_8k_recent_long` | `atr_trail_1x` | 90 | 21.11 | 0.58 | -0.2 | -2.827 | -254.46 | per_regime | FAIL | wr<50;pf<1.3;sharpe<0.7 |
| `macd_fast_crossover` | `atr_trail_1x` | 107 | 34.58 | 0.65 | -0.16 | -1.977 | -211.53 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `xs_momentum_bottom_decile_short` | `end_of_backtest` | 1 | 0.0 | 0.0 | 0.0 | -205.133 | -205.13 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_liquidity_sweep_reversal` | `atr_trail_1x` | 43 | 16.28 | 0.35 | -0.44 | -4.533 | -194.92 | per_regime | FAIL | wr<50;pf<1.3;sharpe<0.7 |
| `xs_low_beta_long` | `time_stop_mfe` | 38 | 0.0 | 0.0 | -1.83 | -4.744 | -180.26 | per_regime | FAIL | wr<50;pf<1.3;sharpe<0.7 |
| `cpr_narrow_momentum` | `end_of_backtest` | 1 | 0.0 | 0.0 | 0.0 | -176.966 | -176.97 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `ultimate_oscillator` | `atr_trail_1x` | 138 | 32.61 | 0.78 | -0.1 | -1.241 | -171.23 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `smc_choch_reversal` | `atr_trail_1x` | 237 | 25.32 | 0.89 | -0.04 | -0.7 | -165.87 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `monthly_bias_momentum_long` | `circuit_breaker` | 19 | 26.32 | 0.35 | -0.39 | -8.725 | -165.78 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_bos_continuation` | `atr_trail_1x` | 58 | 20.69 | 0.56 | -0.23 | -2.765 | -160.35 | per_regime | FAIL | wr<50;pf<1.3;sharpe<0.7 |
| `cpr_narrow_bullish` | `end_of_backtest` | 33 | 42.42 | 0.41 | -0.22 | -4.812 | -158.8 | per_regime | FAIL | wr<50;pf<1.3;sharpe<0.7 |
| `macd_ichimoku` | `atr_trail_1x` | 15 | 13.33 | 0.14 | -0.55 | -9.902 | -148.53 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_inverse_fvg` | `circuit_breaker` | 10 | 10.0 | 0.03 | -1.43 | -14.1 | -141.0 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_order_block_bounce` | `atr_trail_1x` | 57 | 28.07 | 0.5 | -0.28 | -2.459 | -140.19 | per_regime | FAIL | wr<50;pf<1.3;sharpe<0.7 |
| `avwap_50_reclaim` | `circuit_breaker` | 8 | 0.0 | 0.0 | -1.83 | -15.157 | -121.25 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `po3_htf_aligned_long` | `atr_trail_1x` | 40 | 15.0 | 0.59 | -0.18 | -2.995 | -119.79 | per_regime | FAIL | wr<50;pf<1.3;sharpe<0.7 |
| `smc_breaker_block_short` | `atr_trail_1x` | 22 | 18.18 | 0.29 | -0.57 | -5.136 | -112.98 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `insider_cluster_long` | `atr_trail_1x` | 19 | 21.05 | 0.12 | -0.89 | -5.638 | -107.12 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `stochrsi_oversold` | `atr_trail_1x` | 33 | 6.06 | 0.17 | -0.69 | -3.243 | -107.02 | per_regime | FAIL | wr<50;pf<1.3;sharpe<0.7 |
| `xs_combined_momentum_low_ivol` | `circuit_breaker` | 2 | 0.0 | 0.0 | -0.88 | -53.14 | -106.28 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `williams_r_oversold` | `atr_trail_1x` | 138 | 28.99 | 0.87 | -0.05 | -0.7 | -96.65 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `monthly_bias_momentum_long` | `time_stop_mfe` | 17 | 0.0 | 0.0 | -2.25 | -5.6 | -95.2 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_premium_short` | `atr_trail_1x` | 13 | 15.38 | 0.08 | -1.19 | -6.638 | -86.3 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `prev_day_low_bounce` | `atr_trail_1x` | 11 | 9.09 | 0.02 | -1.27 | -6.794 | -74.73 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `xs_low_beta_long` | `circuit_breaker` | 8 | 12.5 | 0.2 | -0.74 | -8.426 | -67.41 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `stochrsi_overbought_short` | `circuit_breaker` | 5 | 20.0 | 0.24 | -0.55 | -12.846 | -64.23 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `po3_htf_aligned_long` | `end_of_backtest` | 3 | 33.33 | 0.06 | -0.55 | -19.773 | -59.32 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `prev_day_high_break` | `atr_trail_1x` | 5 | 40.0 | 0.31 | -0.35 | -10.689 | -53.44 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `htf_aligned_breakout_long` | `atr_trail_1x` | 122 | 27.87 | 0.92 | -0.03 | -0.428 | -52.2 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `avwap_252_breakout` | `circuit_breaker` | 5 | 0.0 | 0.0 | -0.8 | -9.536 | -47.68 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `xs_momentum_bottom_decile_short` | `circuit_breaker` | 9 | 22.22 | 0.31 | -0.49 | -5.253 | -47.28 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `cpr_narrow_bullish` | `time_stop_mfe` | 11 | 0.0 | 0.0 | -3.31 | -4.209 | -46.3 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `xs_combined_momentum_low_ivol` | `atr_trail_1x` | 28 | 17.86 | 0.76 | -0.09 | -1.618 | -45.3 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_choch_reversal` | `time_stop_mfe` | 10 | 0.0 | 0.0 | -1.55 | -4.36 | -43.6 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `po3_bullish` | `circuit_breaker` | 3 | 0.0 | 0.0 | -1.05 | -13.447 | -40.34 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `avwap_252_breakout` | `atr_trail_1x` | 99 | 30.3 | 0.91 | -0.03 | -0.395 | -39.09 | per_regime | FAIL | wr<50;pf<1.3;sharpe<0.7 |
| `stochrsi_overbought_short` | `time_stop_mfe` | 7 | 0.0 | 0.0 | -2.62 | -5.169 | -36.18 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_fvg_retest_short` | `atr_trail_1x` | 4 | 0.0 | 0.0 | -2.95 | -8.963 | -35.85 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_discount_long` | `atr_trail_1x` | 4 | 0.0 | 0.0 | -2.05 | -8.949 | -35.8 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `avwap_50_reclaim` | `time_stop_mfe` | 6 | 0.0 | 0.0 | -2.53 | -5.791 | -34.74 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `avwap_50_reclaim` | `end_of_backtest` | 18 | 38.89 | 0.67 | -0.1 | -1.912 | -34.42 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `cpr_narrow_momentum` | `circuit_breaker` | 3 | 33.33 | 0.12 | -0.53 | -11.421 | -34.26 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `roc_burst` | `atr_trail_1x` | 3 | 0.0 | 0.0 | -66.08 | -10.438 | -31.31 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `ichimoku_tk_cross` | `atr_trail_1x` | 10 | 30.0 | 0.51 | -0.31 | -2.889 | -28.89 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `macd_fast_crossover` | `circuit_breaker` | 3 | 33.33 | 0.25 | -0.55 | -8.26 | -24.78 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_fvg_retest_long` | `atr_trail_1x` | 2 | 0.0 | 0.0 | -5.33 | -12.279 | -24.56 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_liquidity_sweep_reversal` | `circuit_breaker` | 2 | 50.0 | 0.14 | -0.54 | -11.888 | -23.78 | per_regime | INSUFFICIENT_DATA | n<30;pf<1.3;sharpe<0.7 |
| `adx_initiation` | `atr_trail_1x` | 4 | 25.0 | 0.25 | -0.65 | -5.829 | -23.32 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `hull_rsi` | `circuit_breaker` | 6 | 33.33 | 0.17 | -0.52 | -3.873 | -23.24 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `break_retest_confluence` | `atr_trail_1x` | 2 | 0.0 | 0.0 | -9.46 | -11.24 | -22.48 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `pivot_r1_breakout` | `circuit_breaker` | 2 | 0.0 | 0.0 | -1.02 | -10.918 | -21.84 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_inverse_fvg` | `time_stop_mfe` | 8 | 0.0 | 0.0 | -1.81 | -2.367 | -18.93 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `po3_htf_aligned_short` | `atr_trail_1x` | 18 | 27.78 | 0.81 | -0.07 | -1.041 | -18.74 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `cmf_flip` | `time_stop_mfe` | 5 | 0.0 | 0.0 | -2.45 | -3.695 | -18.48 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `htf_aligned_breakout_long` | `time_stop_mfe` | 2 | 0.0 | 0.0 | -7.19 | -9.138 | -18.28 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `risk_off_bond_equity_short` | `atr_trail_1x` | 3 | 0.0 | 0.0 | -1.16 | -5.937 | -17.81 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `hull_rsi_short` | `atr_trail_1x` | 5 | 20.0 | 0.2 | -0.56 | -3.522 | -17.61 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `cpr_narrow_momentum` | `time_stop_mfe` | 3 | 0.0 | 0.0 | -2.55 | -5.663 | -16.99 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `r1_break_retest` | `circuit_breaker` | 1 | 0.0 | 0.0 | 0.0 | -16.735 | -16.74 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `bollinger_lower` | `circuit_breaker` | 1 | 0.0 | 0.0 | 0.0 | -15.986 | -15.99 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_bos_continuation` | `circuit_breaker` | 3 | 33.33 | 0.18 | -0.69 | -5.142 | -15.43 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `volume_spike_breakout` | `circuit_breaker` | 1 | 0.0 | 0.0 | 0.0 | -15.028 | -15.03 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `buyback_8k_recent_long` | `end_of_backtest` | 3 | 33.33 | 0.02 | -1.05 | -4.809 | -14.43 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `williams_r_oversold` | `time_stop_mfe` | 3 | 0.0 | 0.0 | -7.03 | -4.73 | -14.19 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `roc_burst` | `circuit_breaker` | 1 | 0.0 | 0.0 | 0.0 | -13.799 | -13.8 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `pivot_s3_capitulation` | `atr_trail_1x` | 3 | 33.33 | 0.37 | -0.42 | -4.303 | -12.91 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_bos_retest_entry` | `time_stop_mfe` | 2 | 0.0 | 0.0 | -6.95 | -5.992 | -11.98 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `orb_stocks_in_play_short` | `circuit_breaker` | 1 | 0.0 | 0.0 | 0.0 | -10.576 | -10.58 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `pivot_r2_continuation` | `atr_trail_1x` | 1 | 0.0 | 0.0 | 0.0 | -10.523 | -10.52 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `dc20_break_retest` | `atr_trail_1x` | 1 | 0.0 | 0.0 | 0.0 | -10.412 | -10.41 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `rsi_oversold` | `atr_trail_1x` | 1 | 0.0 | 0.0 | 0.0 | -10.308 | -10.31 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `buyback_8k_recent_long` | `time_stop_mfe` | 2 | 0.0 | 0.0 | -4.92 | -5.019 | -10.04 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_ote_long` | `atr_trail_1x` | 2 | 50.0 | 0.08 | -0.6 | -4.814 | -9.63 | per_regime | INSUFFICIENT_DATA | n<30;pf<1.3;sharpe<0.7 |
| `hull_rsi` | `time_stop_mfe` | 2 | 0.0 | 0.0 | -1.14 | -4.719 | -9.44 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `ultimate_oscillator` | `time_stop_mfe` | 3 | 0.0 | 0.0 | -1.47 | -3.111 | -9.33 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `bollinger_lower` | `time_stop_mfe` | 7 | 0.0 | 0.0 | -1.85 | -1.318 | -9.23 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_breaker_block_long` | `circuit_breaker` | 1 | 0.0 | 0.0 | 0.0 | -9.035 | -9.03 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `xs_combined_momentum_low_ivol` | `time_stop_mfe` | 3 | 0.0 | 0.0 | -0.73 | -2.994 | -8.98 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `lead_lag_sector_rotation` | `time_stop_mfe` | 1 | 0.0 | 0.0 | 0.0 | -7.844 | -7.84 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `stochrsi_overbought_short` | `end_of_backtest` | 1 | 0.0 | 0.0 | 0.0 | -7.736 | -7.74 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `williams_r_oversold` | `circuit_breaker` | 4 | 25.0 | 0.77 | -0.1 | -1.749 | -7.0 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `htf_aligned_breakout_short` | `time_stop_mfe` | 2 | 0.0 | 0.0 | -0.99 | -3.323 | -6.65 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `bollinger_tight` | `time_stop_mfe` | 3 | 0.0 | 0.0 | -1.99 | -2.184 | -6.55 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `macd_fast_crossover` | `time_stop_mfe` | 1 | 0.0 | 0.0 | 0.0 | -6.528 | -6.53 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `xs_momentum_top_decile` | `end_of_backtest` | 2 | 0.0 | 0.0 | -4.67 | -2.883 | -5.77 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `bollinger_upper_short` | `time_stop_mfe` | 1 | 0.0 | 0.0 | 0.0 | -5.593 | -5.59 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_fvg_retest_short` | `time_stop_mfe` | 1 | 0.0 | 0.0 | 0.0 | -5.555 | -5.56 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `po3_htf_aligned_long` | `time_stop_mfe` | 1 | 0.0 | 0.0 | 0.0 | -4.854 | -4.85 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_breaker_block_short` | `end_of_backtest` | 1 | 0.0 | 0.0 | 0.0 | -4.413 | -4.41 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `cmf_flip` | `end_of_backtest` | 2 | 0.0 | 0.0 | -0.89 | -1.819 | -3.64 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_liquidity_sweep_reversal` | `time_stop_mfe` | 2 | 0.0 | 0.0 | -1.79 | -1.778 | -3.56 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `po3_bullish` | `end_of_backtest` | 14 | 42.86 | 0.86 | -0.05 | -0.243 | -3.4 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_bos_continuation` | `time_stop_mfe` | 1 | 0.0 | 0.0 | 0.0 | -3.035 | -3.04 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_ote_short` | `atr_trail_1x` | 7 | 42.86 | 0.81 | -0.09 | -0.435 | -3.04 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `lead_lag_sector_rotation` | `circuit_breaker` | 1 | 0.0 | 0.0 | 0.0 | -2.728 | -2.73 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `buyback_8k_recent_long` | `circuit_breaker` | 3 | 0.0 | 0.0 | -13.79 | -0.796 | -2.39 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `htf_aligned_breakout_short` | `circuit_breaker` | 1 | 0.0 | 0.0 | 0.0 | -2.018 | -2.02 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `stochrsi_oversold` | `end_of_backtest` | 1 | 0.0 | 0.0 | 0.0 | -0.834 | -0.83 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `avwap_252_breakout` | `time_stop_mfe` | 1 | 0.0 | 0.0 | 0.0 | -0.806 | -0.81 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_order_block_bounce` | `time_stop_mfe` | 1 | 0.0 | 0.0 | 0.0 | -0.774 | -0.77 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `ichimoku_cloud_breakout` | `end_of_backtest` | 1 | 0.0 | 0.0 | 0.0 | -0.732 | -0.73 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `xs_combined_momentum_low_ivol` | `end_of_backtest` | 4 | 75.0 | 0.69 | -0.12 | -0.086 | -0.34 | per_regime | INSUFFICIENT_DATA | n<30;pf<1.3;sharpe<0.7 |
| `pivot_s1_bounce` | `end_of_backtest` | 3 | 33.33 | 0.99 | -0.0 | -0.009 | -0.03 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_breaker_block_short` | `circuit_breaker` | 1 | 100.0 | inf | 0.0 | 0.336 | 0.34 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `smc_breaker_block_long` | `atr_trail_1x` | 1 | 100.0 | inf | 0.0 | 0.455 | 0.46 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `htf_aligned_breakout_short` | `end_of_backtest` | 3 | 66.67 | 1.03 | 0.01 | 0.171 | 0.51 | per_regime | INSUFFICIENT_DATA | n<30;pf<1.3;sharpe<0.7 |
| `smc_bos_retest_entry` | `end_of_backtest` | 1 | 100.0 | inf | 0.0 | 0.635 | 0.64 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `stoch_oversold` | `atr_trail_1x` | 1 | 100.0 | inf | 0.0 | 0.915 | 0.91 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `smc_inverse_fvg` | `end_of_backtest` | 9 | 55.56 | 1.03 | 0.01 | 0.299 | 2.69 | per_regime | INSUFFICIENT_DATA | n<30;pf<1.3;sharpe<0.7 |
| `bollinger_upper_short` | `atr_trail_1x` | 5 | 40.0 | 1.27 | 0.08 | 1.023 | 5.12 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `ultimate_oscillator` | `circuit_breaker` | 7 | 28.57 | 1.1 | 0.03 | 0.848 | 5.94 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `smc_breaker_block_long` | `end_of_backtest` | 1 | 100.0 | inf | 0.0 | 7.382 | 7.38 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `smc_order_block_bounce` | `circuit_breaker` | 1 | 100.0 | inf | 0.0 | 7.572 | 7.57 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `macd_fast_crossover` | `end_of_backtest` | 4 | 25.0 | 1.48 | 0.13 | 3.45 | 13.8 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;sharpe<0.7 |
| `avwap_252_breakout` | `end_of_backtest` | 2 | 100.0 | inf | 8.74 | 7.317 | 14.63 | per_regime | INSUFFICIENT_DATA | n<30 |
| `rsi21_slow` | `atr_trail_1x` | 1 | 100.0 | inf | 0.0 | 16.848 | 16.85 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `po3_bearish` | `circuit_breaker` | 2 | 50.0 | 2.86 | 0.34 | 9.201 | 18.4 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `htf_aligned_breakout_long` | `end_of_backtest` | 10 | 60.0 | 4.97 | 0.5 | 1.92 | 19.2 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `smc_bos_continuation` | `end_of_backtest` | 4 | 75.0 | 87.9 | 0.85 | 4.812 | 19.25 | per_regime | INSUFFICIENT_DATA | n<30 |
| `pivot_s2_bounce` | `atr_trail_1x` | 6 | 50.0 | 1.84 | 0.23 | 3.441 | 20.65 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `smc_choch_reversal` | `circuit_breaker` | 9 | 22.22 | 1.24 | 0.08 | 2.422 | 21.8 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;pf<1.3;sharpe<0.7 |
| `cmf_flip` | `circuit_breaker` | 1 | 100.0 | inf | 0.0 | 22.756 | 22.76 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `supertrend_macd` | `atr_trail_1x` | 2 | 50.0 | 3.48 | 0.39 | 12.42 | 24.84 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `smc_liquidity_sweep_reversal` | `end_of_backtest` | 5 | 60.0 | 5.49 | 0.68 | 5.297 | 26.48 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `ichimoku_cloud_breakout` | `atr_trail_1x` | 14 | 35.71 | 1.61 | 0.17 | 2.889 | 40.44 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;sharpe<0.7 |
| `pivot_r1_breakout` | `end_of_backtest` | 5 | 80.0 | 24.13 | 1.28 | 9.497 | 47.48 | per_regime | INSUFFICIENT_DATA | n<30 |
| `htf_aligned_breakout_long` | `circuit_breaker` | 7 | 28.57 | 1.77 | 0.16 | 7.271 | 50.9 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;sharpe<0.7 |
| `ultimate_oscillator` | `end_of_backtest` | 9 | 55.56 | 7.35 | 0.57 | 5.843 | 52.58 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `orb_stocks_in_play_long` | `end_of_backtest` | 9 | 77.78 | 43.87 | 0.69 | 6.52 | 58.68 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `orb_stocks_in_play_long` | `circuit_breaker` | 7 | 42.86 | 4.69 | 0.36 | 9.805 | 68.63 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;sharpe<0.7 |
| `lead_lag_sector_rotation` | `atr_trail_1x` | 19 | 26.32 | 1.9 | 0.15 | 4.791 | 91.02 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;sharpe<0.7 |
| `smc_bos_retest_entry` | `atr_trail_1x` | 11 | 36.36 | 3.72 | 0.44 | 8.3 | 91.3 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;sharpe<0.7 |
| `hull_rsi` | `end_of_backtest` | 6 | 83.33 | 17.98 | 0.5 | 16.996 | 101.98 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `bollinger_tight` | `end_of_backtest` | 4 | 100.0 | inf | 3.3 | 29.92 | 119.68 | per_regime | INSUFFICIENT_DATA | n<30 |
| `pivot_s1_bounce` | `atr_trail_1x` | 17 | 47.06 | 2.75 | 0.27 | 7.17 | 121.89 | per_regime | INSUFFICIENT_DATA | n<30;wr<50;sharpe<0.7 |
| `stochrsi_oversold` | `strategy_time_stop_10d` | 31 | 77.42 | 20.27 | 0.66 | 4.118 | 127.66 | per_regime | FAIL | sharpe<0.7 |
| `bollinger_tight` | `atr_trail_1x` | 63 | 11.11 | 1.63 | 0.1 | 2.103 | 132.46 | per_regime | FAIL | wr<50;sharpe<0.7 |
| `smc_order_block_bounce` | `end_of_backtest` | 10 | 80.0 | 3.75 | 0.47 | 15.613 | 156.13 | per_regime | INSUFFICIENT_DATA | n<30;sharpe<0.7 |
| `cmf_flip` | `atr_trail_1x` | 117 | 30.77 | 1.27 | 0.07 | 1.419 | 166.06 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `smc_choch_reversal` | `end_of_backtest` | 18 | 77.78 | 27.28 | 0.82 | 10.84 | 195.11 | per_regime | INSUFFICIENT_DATA | n<30 |
| `bollinger_lower` | `fixed_4r_2r` | 119 | 46.22 | 1.57 | 0.22 | 1.943 | 231.17 | overall | FAIL | wr<55;sharpe<1.0 |
| `xs_momentum_top_decile` | `time_stop_class_factor` | 92 | 61.96 | 2.68 | 0.36 | 2.688 | 247.28 | per_regime | FAIL | sharpe<0.7 |
| `orb_stocks_in_play_long` | `atr_trail_1x` | 76 | 22.37 | 1.52 | 0.07 | 3.45 | 262.23 | per_regime | FAIL | wr<50;sharpe<0.7 |
| `xs_low_beta_long` | `atr_trail_1x` | 263 | 33.46 | 1.19 | 0.05 | 1.062 | 279.43 | overall | FAIL | wr<55;pf<1.5;sharpe<1.0 |
| `xs_low_beta_long` | `end_of_backtest` | 35 | 88.57 | 36.38 | 0.43 | 9.804 | 343.15 | per_regime | FAIL | sharpe<0.7 |
| `monthly_bias_momentum_long` | `end_of_backtest` | 52 | 82.69 | 23.85 | 0.7 | 7.446 | 387.2 | per_regime | FAIL | sharpe<0.7 |
| `williams_r_oversold` | `end_of_backtest` | 32 | 90.62 | 35.85 | 0.49 | 16.002 | 512.06 | per_regime | FAIL | sharpe<0.7 |
| `cpr_narrow_bullish` | `regime_flip` | 308 | 50.97 | 1.95 | 0.21 | 1.876 | 577.84 | overall | FAIL | wr<55;sharpe<1.0 |
| `po3_bullish` | `time_stop_class_po3` | 280 | 54.29 | 2.33 | 0.29 | 2.379 | 666.17 | overall | FAIL | wr<55;sharpe<1.0 |
| `avwap_50_reclaim` | `hybrid_50pct_3xatr` | 163 | 100.0 | inf | 2.03 | 9.269 | 1510.89 | overall | PASS | - |

## Per-(strategy x exit_reason) cell verdicts -- SECONDARY (debug-only)

Raw exit_reason granularity (target_hit + stop_hit split). **Apparent 100%-WR cells on 2-leg exits are sampling artifacts**: selecting only target_hit rows trivially yields 100% WR. The PRIMARY table above collapses these legs and is the correct verdict.

**Fired cells**: 171
**Verdict counts**: {'FAIL': 44, 'INSUFFICIENT_DATA': 125, 'PASS': 2}

| Strategy | Exit reason | n | WR% | PF | Sharpe | Mean PnL% | Sum pp | Verdict | Note |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `avwap_50_reclaim` | `trailing_stop` | 203 | 4.93 | 0.03 | -0.45 | -10.208 | -2072.16 | FAIL | - |
| `cpr_narrow_bullish` | `trailing_stop` | 385 | 17.66 | 0.39 | -0.32 | -4.34 | -1670.92 | FAIL | - |
| `xs_momentum_bottom_decile_short` | `trailing_stop` | 314 | 24.2 | 0.38 | -0.19 | -5.106 | -1603.25 | FAIL | - |
| `hull_rsi` | `trailing_stop` | 406 | 25.37 | 0.44 | -0.33 | -3.377 | -1371.1 | FAIL | - |
| `po3_bullish` | `trailing_stop` | 119 | 0.84 | 0.01 | -2.15 | -8.636 | -1027.74 | FAIL | - |
| `htf_aligned_breakout_short` | `trailing_stop` | 187 | 18.72 | 0.23 | -0.65 | -5.183 | -969.18 | FAIL | - |
| `po3_bearish` | `ma_exit_ema9_above_batch285` | 361 | 24.1 | 0.33 | -0.37 | -2.265 | -817.79 | FAIL | - |
| `bollinger_lower` | `trailing_stop` | 301 | 0.0 | 0.0 | -2.02 | -2.588 | -778.98 | FAIL | - |
| `monthly_bias_momentum_long` | `trailing_stop` | 413 | 25.67 | 0.8 | -0.07 | -1.23 | -507.85 | FAIL | - |
| `bollinger_lower` | `fixed_4r_2r_stop_hit_batch284` | 64 | 0.0 | 0.0 | -70.21 | -6.337 | -405.6 | FAIL | (2-leg target/stop split) |
| `smc_inverse_fvg` | `trailing_stop` | 248 | 29.03 | 0.72 | -0.11 | -1.578 | -391.46 | FAIL | - |
| `cpr_narrow_momentum` | `trailing_stop` | 170 | 30.59 | 0.6 | -0.21 | -2.091 | -355.49 | FAIL | - |
| `po3_bearish` | `trailing_stop` | 40 | 20.0 | 0.16 | -0.44 | -7.778 | -311.13 | FAIL | - |
| `stochrsi_overbought_short` | `trailing_stop` | 275 | 37.09 | 0.79 | -0.09 | -1.055 | -290.14 | FAIL | - |
| `cpr_narrow_bullish` | `circuit_breaker_1` | 13 | 15.38 | 0.03 | -0.97 | -21.752 | -282.78 | INSUFFICIENT_DATA | - |
| `xs_momentum_top_decile` | `trailing_stop` | 31 | 3.23 | 0.02 | -2.27 | -9.069 | -281.14 | FAIL | - |
| `pivot_r1_breakout` | `trailing_stop` | 89 | 24.72 | 0.54 | -0.25 | -3.155 | -280.81 | FAIL | - |
| `orb_stocks_in_play_short` | `trailing_stop` | 113 | 31.86 | 0.57 | -0.23 | -2.303 | -260.26 | FAIL | - |
| `buyback_8k_recent_long` | `trailing_stop` | 90 | 21.11 | 0.58 | -0.2 | -2.827 | -254.46 | FAIL | - |
| `macd_fast_crossover` | `trailing_stop` | 107 | 34.58 | 0.65 | -0.16 | -1.977 | -211.53 | FAIL | - |
| `xs_momentum_bottom_decile_short` | `end_of_backtest` | 1 | 0.0 | 0.0 | 0.0 | -205.133 | -205.13 | INSUFFICIENT_DATA | - |
| `smc_liquidity_sweep_reversal` | `trailing_stop` | 43 | 16.28 | 0.35 | -0.44 | -4.533 | -194.92 | FAIL | - |
| `xs_low_beta_long` | `time_stop_20d_mfe<0.5pct_batch213` | 38 | 0.0 | 0.0 | -1.83 | -4.744 | -180.26 | FAIL | - |
| `cpr_narrow_momentum` | `end_of_backtest` | 1 | 0.0 | 0.0 | 0.0 | -176.966 | -176.97 | INSUFFICIENT_DATA | - |
| `ultimate_oscillator` | `trailing_stop` | 138 | 32.61 | 0.78 | -0.1 | -1.241 | -171.23 | FAIL | - |
| `smc_choch_reversal` | `trailing_stop` | 237 | 25.32 | 0.89 | -0.04 | -0.7 | -165.87 | FAIL | - |
| `monthly_bias_momentum_long` | `circuit_breaker_1` | 19 | 26.32 | 0.35 | -0.39 | -8.725 | -165.78 | INSUFFICIENT_DATA | - |
| `smc_bos_continuation` | `trailing_stop` | 58 | 20.69 | 0.56 | -0.23 | -2.765 | -160.35 | FAIL | - |
| `cpr_narrow_bullish` | `end_of_backtest` | 33 | 42.42 | 0.41 | -0.22 | -4.812 | -158.8 | FAIL | - |
| `macd_ichimoku` | `trailing_stop` | 15 | 13.33 | 0.14 | -0.55 | -9.902 | -148.53 | INSUFFICIENT_DATA | - |
| `smc_inverse_fvg` | `circuit_breaker_1` | 10 | 10.0 | 0.03 | -1.43 | -14.1 | -141.0 | INSUFFICIENT_DATA | - |
| `smc_order_block_bounce` | `trailing_stop` | 57 | 28.07 | 0.5 | -0.28 | -2.459 | -140.19 | FAIL | - |
| `avwap_50_reclaim` | `circuit_breaker_1` | 8 | 0.0 | 0.0 | -1.83 | -15.157 | -121.25 | INSUFFICIENT_DATA | - |
| `po3_htf_aligned_long` | `trailing_stop` | 40 | 15.0 | 0.59 | -0.18 | -2.995 | -119.79 | FAIL | - |
| `smc_breaker_block_short` | `trailing_stop` | 22 | 18.18 | 0.29 | -0.57 | -5.136 | -112.98 | INSUFFICIENT_DATA | - |
| `insider_cluster_long` | `trailing_stop` | 19 | 21.05 | 0.12 | -0.89 | -5.638 | -107.12 | INSUFFICIENT_DATA | - |
| `stochrsi_oversold` | `trailing_stop` | 33 | 6.06 | 0.17 | -0.69 | -3.243 | -107.02 | FAIL | - |
| `xs_combined_momentum_low_ivol` | `circuit_breaker_1` | 2 | 0.0 | 0.0 | -0.88 | -53.14 | -106.28 | INSUFFICIENT_DATA | - |
| `williams_r_oversold` | `trailing_stop` | 138 | 28.99 | 0.87 | -0.05 | -0.7 | -96.65 | FAIL | - |
| `monthly_bias_momentum_long` | `time_stop_20d_mfe<0.5pct_batch213` | 17 | 0.0 | 0.0 | -2.25 | -5.6 | -95.2 | INSUFFICIENT_DATA | - |
| `smc_premium_short` | `trailing_stop` | 13 | 15.38 | 0.08 | -1.19 | -6.638 | -86.3 | INSUFFICIENT_DATA | - |
| `prev_day_low_bounce` | `trailing_stop` | 11 | 9.09 | 0.02 | -1.27 | -6.794 | -74.73 | INSUFFICIENT_DATA | - |
| `xs_low_beta_long` | `circuit_breaker_1` | 8 | 12.5 | 0.2 | -0.74 | -8.426 | -67.41 | INSUFFICIENT_DATA | - |
| `stochrsi_overbought_short` | `circuit_breaker_1` | 5 | 20.0 | 0.24 | -0.55 | -12.846 | -64.23 | INSUFFICIENT_DATA | - |
| `po3_htf_aligned_long` | `end_of_backtest` | 3 | 33.33 | 0.06 | -0.55 | -19.773 | -59.32 | INSUFFICIENT_DATA | - |
| `prev_day_high_break` | `trailing_stop` | 5 | 40.0 | 0.31 | -0.35 | -10.689 | -53.44 | INSUFFICIENT_DATA | - |
| `htf_aligned_breakout_long` | `trailing_stop` | 122 | 27.87 | 0.92 | -0.03 | -0.428 | -52.2 | FAIL | - |
| `avwap_252_breakout` | `circuit_breaker_1` | 5 | 0.0 | 0.0 | -0.8 | -9.536 | -47.68 | INSUFFICIENT_DATA | - |
| `xs_momentum_bottom_decile_short` | `circuit_breaker_1` | 9 | 22.22 | 0.31 | -0.49 | -5.253 | -47.28 | INSUFFICIENT_DATA | - |
| `cpr_narrow_bullish` | `time_stop_20d_mfe<0.5pct_batch213` | 11 | 0.0 | 0.0 | -3.31 | -4.209 | -46.3 | INSUFFICIENT_DATA | - |
| `xs_combined_momentum_low_ivol` | `trailing_stop` | 28 | 17.86 | 0.76 | -0.09 | -1.618 | -45.3 | INSUFFICIENT_DATA | - |
| `smc_choch_reversal` | `time_stop_20d_mfe<0.5pct_batch213` | 10 | 0.0 | 0.0 | -1.55 | -4.36 | -43.6 | INSUFFICIENT_DATA | - |
| `po3_bullish` | `circuit_breaker_1` | 3 | 0.0 | 0.0 | -1.05 | -13.447 | -40.34 | INSUFFICIENT_DATA | - |
| `avwap_252_breakout` | `trailing_stop` | 99 | 30.3 | 0.91 | -0.03 | -0.395 | -39.09 | FAIL | - |
| `stochrsi_overbought_short` | `time_stop_30d_mfe<0.5pct_batch213` | 7 | 0.0 | 0.0 | -2.62 | -5.169 | -36.18 | INSUFFICIENT_DATA | - |
| `smc_fvg_retest_short` | `trailing_stop` | 4 | 0.0 | 0.0 | -2.95 | -8.963 | -35.85 | INSUFFICIENT_DATA | - |
| `smc_discount_long` | `trailing_stop` | 4 | 0.0 | 0.0 | -2.05 | -8.949 | -35.8 | INSUFFICIENT_DATA | - |
| `avwap_50_reclaim` | `time_stop_20d_mfe<0.5pct_batch213` | 6 | 0.0 | 0.0 | -2.53 | -5.791 | -34.74 | INSUFFICIENT_DATA | - |
| `avwap_50_reclaim` | `end_of_backtest` | 18 | 38.89 | 0.67 | -0.1 | -1.912 | -34.42 | INSUFFICIENT_DATA | - |
| `cpr_narrow_momentum` | `circuit_breaker_1` | 3 | 33.33 | 0.12 | -0.53 | -11.421 | -34.26 | INSUFFICIENT_DATA | - |
| `roc_burst` | `trailing_stop` | 3 | 0.0 | 0.0 | -66.08 | -10.438 | -31.31 | INSUFFICIENT_DATA | - |
| `ichimoku_tk_cross` | `trailing_stop` | 10 | 30.0 | 0.51 | -0.31 | -2.889 | -28.89 | INSUFFICIENT_DATA | - |
| `macd_fast_crossover` | `circuit_breaker_1` | 3 | 33.33 | 0.25 | -0.55 | -8.26 | -24.78 | INSUFFICIENT_DATA | - |
| `smc_fvg_retest_long` | `trailing_stop` | 2 | 0.0 | 0.0 | -5.33 | -12.279 | -24.56 | INSUFFICIENT_DATA | - |
| `smc_liquidity_sweep_reversal` | `circuit_breaker_1` | 2 | 50.0 | 0.14 | -0.54 | -11.888 | -23.78 | INSUFFICIENT_DATA | - |
| `adx_initiation` | `trailing_stop` | 4 | 25.0 | 0.25 | -0.65 | -5.829 | -23.32 | INSUFFICIENT_DATA | - |
| `hull_rsi` | `circuit_breaker_1` | 6 | 33.33 | 0.17 | -0.52 | -3.873 | -23.24 | INSUFFICIENT_DATA | - |
| `break_retest_confluence` | `trailing_stop` | 2 | 0.0 | 0.0 | -9.46 | -11.24 | -22.48 | INSUFFICIENT_DATA | - |
| `pivot_r1_breakout` | `circuit_breaker_1` | 2 | 0.0 | 0.0 | -1.02 | -10.918 | -21.84 | INSUFFICIENT_DATA | - |
| `smc_inverse_fvg` | `time_stop_20d_mfe<0.5pct_batch213` | 8 | 0.0 | 0.0 | -1.81 | -2.367 | -18.93 | INSUFFICIENT_DATA | - |
| `po3_htf_aligned_short` | `trailing_stop` | 18 | 27.78 | 0.81 | -0.07 | -1.041 | -18.74 | INSUFFICIENT_DATA | - |
| `cmf_flip` | `time_stop_10d_mfe<0.5pct_batch213` | 5 | 0.0 | 0.0 | -2.45 | -3.695 | -18.48 | INSUFFICIENT_DATA | - |
| `htf_aligned_breakout_long` | `time_stop_20d_mfe<0.5pct_batch213` | 2 | 0.0 | 0.0 | -7.19 | -9.138 | -18.28 | INSUFFICIENT_DATA | - |
| `risk_off_bond_equity_short` | `trailing_stop` | 3 | 0.0 | 0.0 | -1.16 | -5.937 | -17.81 | INSUFFICIENT_DATA | - |
| `hull_rsi_short` | `trailing_stop` | 5 | 20.0 | 0.2 | -0.56 | -3.522 | -17.61 | INSUFFICIENT_DATA | - |
| `cpr_narrow_momentum` | `time_stop_20d_mfe<0.5pct_batch213` | 3 | 0.0 | 0.0 | -2.55 | -5.663 | -16.99 | INSUFFICIENT_DATA | - |
| `r1_break_retest` | `circuit_breaker_1` | 1 | 0.0 | 0.0 | 0.0 | -16.735 | -16.74 | INSUFFICIENT_DATA | - |
| `bollinger_lower` | `circuit_breaker_1` | 1 | 0.0 | 0.0 | 0.0 | -15.986 | -15.99 | INSUFFICIENT_DATA | - |
| `smc_bos_continuation` | `circuit_breaker_1` | 3 | 33.33 | 0.18 | -0.69 | -5.142 | -15.43 | INSUFFICIENT_DATA | - |
| `volume_spike_breakout` | `circuit_breaker_1` | 1 | 0.0 | 0.0 | 0.0 | -15.028 | -15.03 | INSUFFICIENT_DATA | - |
| `buyback_8k_recent_long` | `end_of_backtest` | 3 | 33.33 | 0.02 | -1.05 | -4.809 | -14.43 | INSUFFICIENT_DATA | - |
| `williams_r_oversold` | `time_stop_30d_mfe<0.5pct_batch213` | 3 | 0.0 | 0.0 | -7.03 | -4.73 | -14.19 | INSUFFICIENT_DATA | - |
| `roc_burst` | `circuit_breaker_1` | 1 | 0.0 | 0.0 | 0.0 | -13.799 | -13.8 | INSUFFICIENT_DATA | - |
| `pivot_s3_capitulation` | `trailing_stop` | 3 | 33.33 | 0.37 | -0.42 | -4.303 | -12.91 | INSUFFICIENT_DATA | - |
| `smc_bos_retest_entry` | `time_stop_20d_mfe<0.5pct_batch213` | 2 | 0.0 | 0.0 | -6.95 | -5.992 | -11.98 | INSUFFICIENT_DATA | - |
| `orb_stocks_in_play_short` | `circuit_breaker_1` | 1 | 0.0 | 0.0 | 0.0 | -10.576 | -10.58 | INSUFFICIENT_DATA | - |
| `pivot_r2_continuation` | `trailing_stop` | 1 | 0.0 | 0.0 | 0.0 | -10.523 | -10.52 | INSUFFICIENT_DATA | - |
| `dc20_break_retest` | `trailing_stop` | 1 | 0.0 | 0.0 | 0.0 | -10.412 | -10.41 | INSUFFICIENT_DATA | - |
| `rsi_oversold` | `trailing_stop` | 1 | 0.0 | 0.0 | 0.0 | -10.308 | -10.31 | INSUFFICIENT_DATA | - |
| `buyback_8k_recent_long` | `time_stop_20d_mfe<0.5pct_batch213` | 2 | 0.0 | 0.0 | -4.92 | -5.019 | -10.04 | INSUFFICIENT_DATA | - |
| `smc_ote_long` | `trailing_stop` | 2 | 50.0 | 0.08 | -0.6 | -4.814 | -9.63 | INSUFFICIENT_DATA | - |
| `hull_rsi` | `time_stop_30d_mfe<0.5pct_batch213` | 2 | 0.0 | 0.0 | -1.14 | -4.719 | -9.44 | INSUFFICIENT_DATA | - |
| `ultimate_oscillator` | `time_stop_30d_mfe<0.5pct_batch213` | 3 | 0.0 | 0.0 | -1.47 | -3.111 | -9.33 | INSUFFICIENT_DATA | - |
| `bollinger_lower` | `time_stop_10d_mfe<0.5pct_batch213` | 7 | 0.0 | 0.0 | -1.85 | -1.318 | -9.23 | INSUFFICIENT_DATA | - |
| `smc_breaker_block_long` | `circuit_breaker_1` | 1 | 0.0 | 0.0 | 0.0 | -9.035 | -9.03 | INSUFFICIENT_DATA | - |
| `xs_combined_momentum_low_ivol` | `time_stop_20d_mfe<0.5pct_batch213` | 3 | 0.0 | 0.0 | -0.73 | -2.994 | -8.98 | INSUFFICIENT_DATA | - |
| `lead_lag_sector_rotation` | `time_stop_20d_mfe<0.5pct_batch213` | 1 | 0.0 | 0.0 | 0.0 | -7.844 | -7.84 | INSUFFICIENT_DATA | - |
| `stochrsi_overbought_short` | `end_of_backtest` | 1 | 0.0 | 0.0 | 0.0 | -7.736 | -7.74 | INSUFFICIENT_DATA | - |
| `williams_r_oversold` | `circuit_breaker_1` | 4 | 25.0 | 0.77 | -0.1 | -1.749 | -7.0 | INSUFFICIENT_DATA | - |
| `htf_aligned_breakout_short` | `time_stop_20d_mfe<0.5pct_batch213` | 2 | 0.0 | 0.0 | -0.99 | -3.323 | -6.65 | INSUFFICIENT_DATA | - |
| `bollinger_tight` | `time_stop_10d_mfe<0.5pct_batch213` | 3 | 0.0 | 0.0 | -1.99 | -2.184 | -6.55 | INSUFFICIENT_DATA | - |
| `macd_fast_crossover` | `time_stop_30d_mfe<0.5pct_batch213` | 1 | 0.0 | 0.0 | 0.0 | -6.528 | -6.53 | INSUFFICIENT_DATA | - |
| `xs_momentum_top_decile` | `end_of_backtest` | 2 | 0.0 | 0.0 | -4.67 | -2.883 | -5.77 | INSUFFICIENT_DATA | - |
| `bollinger_upper_short` | `time_stop_10d_mfe<0.5pct_batch213` | 1 | 0.0 | 0.0 | 0.0 | -5.593 | -5.59 | INSUFFICIENT_DATA | - |
| `smc_fvg_retest_short` | `time_stop_20d_mfe<0.5pct_batch213` | 1 | 0.0 | 0.0 | 0.0 | -5.555 | -5.56 | INSUFFICIENT_DATA | - |
| `po3_htf_aligned_long` | `time_stop_20d_mfe<0.5pct_batch213` | 1 | 0.0 | 0.0 | 0.0 | -4.854 | -4.85 | INSUFFICIENT_DATA | - |
| `smc_breaker_block_short` | `end_of_backtest` | 1 | 0.0 | 0.0 | 0.0 | -4.413 | -4.41 | INSUFFICIENT_DATA | - |
| `cmf_flip` | `end_of_backtest` | 2 | 0.0 | 0.0 | -0.89 | -1.819 | -3.64 | INSUFFICIENT_DATA | - |
| `smc_liquidity_sweep_reversal` | `time_stop_20d_mfe<0.5pct_batch213` | 2 | 0.0 | 0.0 | -1.79 | -1.778 | -3.56 | INSUFFICIENT_DATA | - |
| `po3_bullish` | `end_of_backtest` | 14 | 42.86 | 0.86 | -0.05 | -0.243 | -3.4 | INSUFFICIENT_DATA | - |
| `smc_bos_continuation` | `time_stop_20d_mfe<0.5pct_batch213` | 1 | 0.0 | 0.0 | 0.0 | -3.035 | -3.04 | INSUFFICIENT_DATA | - |
| `smc_ote_short` | `trailing_stop` | 7 | 42.86 | 0.81 | -0.09 | -0.435 | -3.04 | INSUFFICIENT_DATA | - |
| `lead_lag_sector_rotation` | `circuit_breaker_1` | 1 | 0.0 | 0.0 | 0.0 | -2.728 | -2.73 | INSUFFICIENT_DATA | - |
| `buyback_8k_recent_long` | `circuit_breaker_1` | 3 | 0.0 | 0.0 | -13.79 | -0.796 | -2.39 | INSUFFICIENT_DATA | - |
| `htf_aligned_breakout_short` | `circuit_breaker_1` | 1 | 0.0 | 0.0 | 0.0 | -2.018 | -2.02 | INSUFFICIENT_DATA | - |
| `stochrsi_oversold` | `end_of_backtest` | 1 | 0.0 | 0.0 | 0.0 | -0.834 | -0.83 | INSUFFICIENT_DATA | - |
| `avwap_252_breakout` | `time_stop_20d_mfe<0.5pct_batch213` | 1 | 0.0 | 0.0 | 0.0 | -0.806 | -0.81 | INSUFFICIENT_DATA | - |
| `smc_order_block_bounce` | `time_stop_20d_mfe<0.5pct_batch213` | 1 | 0.0 | 0.0 | 0.0 | -0.774 | -0.77 | INSUFFICIENT_DATA | - |
| `ichimoku_cloud_breakout` | `end_of_backtest` | 1 | 0.0 | 0.0 | 0.0 | -0.732 | -0.73 | INSUFFICIENT_DATA | - |
| `xs_combined_momentum_low_ivol` | `end_of_backtest` | 4 | 75.0 | 0.69 | -0.12 | -0.086 | -0.34 | INSUFFICIENT_DATA | - |
| `pivot_s1_bounce` | `end_of_backtest` | 3 | 33.33 | 0.99 | -0.0 | -0.009 | -0.03 | INSUFFICIENT_DATA | - |
| `cpr_narrow_bullish` | `regime_flip_neutral_to_bear_batch285` | 12 | 41.67 | 1.0 | -0.0 | -0.001 | -0.01 | INSUFFICIENT_DATA | - |
| `smc_breaker_block_short` | `circuit_breaker_1` | 1 | 100.0 | inf | 0.0 | 0.336 | 0.34 | INSUFFICIENT_DATA | - |
| `smc_breaker_block_long` | `trailing_stop` | 1 | 100.0 | inf | 0.0 | 0.455 | 0.46 | INSUFFICIENT_DATA | - |
| `htf_aligned_breakout_short` | `end_of_backtest` | 3 | 66.67 | 1.03 | 0.01 | 0.171 | 0.51 | INSUFFICIENT_DATA | - |
| `smc_bos_retest_entry` | `end_of_backtest` | 1 | 100.0 | inf | 0.0 | 0.635 | 0.64 | INSUFFICIENT_DATA | - |
| `stoch_oversold` | `trailing_stop` | 1 | 100.0 | inf | 0.0 | 0.915 | 0.91 | INSUFFICIENT_DATA | - |
| `smc_inverse_fvg` | `end_of_backtest` | 9 | 55.56 | 1.03 | 0.01 | 0.299 | 2.69 | INSUFFICIENT_DATA | - |
| `bollinger_upper_short` | `trailing_stop` | 5 | 40.0 | 1.27 | 0.08 | 1.023 | 5.12 | INSUFFICIENT_DATA | - |
| `ultimate_oscillator` | `circuit_breaker_1` | 7 | 28.57 | 1.1 | 0.03 | 0.848 | 5.94 | INSUFFICIENT_DATA | - |
| `smc_breaker_block_long` | `end_of_backtest` | 1 | 100.0 | inf | 0.0 | 7.382 | 7.38 | INSUFFICIENT_DATA | - |
| `smc_order_block_bounce` | `circuit_breaker_1` | 1 | 100.0 | inf | 0.0 | 7.572 | 7.57 | INSUFFICIENT_DATA | - |
| `macd_fast_crossover` | `end_of_backtest` | 4 | 25.0 | 1.48 | 0.13 | 3.45 | 13.8 | INSUFFICIENT_DATA | - |
| `avwap_252_breakout` | `end_of_backtest` | 2 | 100.0 | inf | 8.74 | 7.317 | 14.63 | INSUFFICIENT_DATA | - |
| `rsi21_slow` | `trailing_stop` | 1 | 100.0 | inf | 0.0 | 16.848 | 16.85 | INSUFFICIENT_DATA | - |
| `po3_bearish` | `circuit_breaker_1` | 2 | 50.0 | 2.86 | 0.34 | 9.201 | 18.4 | INSUFFICIENT_DATA | - |
| `htf_aligned_breakout_long` | `end_of_backtest` | 10 | 60.0 | 4.97 | 0.5 | 1.92 | 19.2 | INSUFFICIENT_DATA | - |
| `smc_bos_continuation` | `end_of_backtest` | 4 | 75.0 | 87.9 | 0.85 | 4.812 | 19.25 | INSUFFICIENT_DATA | - |
| `pivot_s2_bounce` | `trailing_stop` | 6 | 50.0 | 1.84 | 0.23 | 3.441 | 20.65 | INSUFFICIENT_DATA | - |
| `smc_choch_reversal` | `circuit_breaker_1` | 9 | 22.22 | 1.24 | 0.08 | 2.422 | 21.8 | INSUFFICIENT_DATA | - |
| `cmf_flip` | `circuit_breaker_1` | 1 | 100.0 | inf | 0.0 | 22.756 | 22.76 | INSUFFICIENT_DATA | - |
| `supertrend_macd` | `trailing_stop` | 2 | 50.0 | 3.48 | 0.39 | 12.42 | 24.84 | INSUFFICIENT_DATA | - |
| `smc_liquidity_sweep_reversal` | `end_of_backtest` | 5 | 60.0 | 5.49 | 0.68 | 5.297 | 26.48 | INSUFFICIENT_DATA | - |
| `ichimoku_cloud_breakout` | `trailing_stop` | 14 | 35.71 | 1.61 | 0.17 | 2.889 | 40.44 | INSUFFICIENT_DATA | - |
| `pivot_r1_breakout` | `end_of_backtest` | 5 | 80.0 | 24.13 | 1.28 | 9.497 | 47.48 | INSUFFICIENT_DATA | - |
| `htf_aligned_breakout_long` | `circuit_breaker_1` | 7 | 28.57 | 1.77 | 0.16 | 7.271 | 50.9 | INSUFFICIENT_DATA | - |
| `ultimate_oscillator` | `end_of_backtest` | 9 | 55.56 | 7.35 | 0.57 | 5.843 | 52.58 | INSUFFICIENT_DATA | - |
| `orb_stocks_in_play_long` | `end_of_backtest` | 9 | 77.78 | 43.87 | 0.69 | 6.52 | 58.68 | INSUFFICIENT_DATA | - |
| `orb_stocks_in_play_long` | `circuit_breaker_1` | 7 | 42.86 | 4.69 | 0.36 | 9.805 | 68.63 | INSUFFICIENT_DATA | - |
| `cpr_narrow_bullish` | `regime_flip_neutral_to_bull_batch285` | 92 | 53.26 | 1.88 | 0.2 | 0.836 | 76.93 | FAIL | - |
| `lead_lag_sector_rotation` | `trailing_stop` | 19 | 26.32 | 1.9 | 0.15 | 4.791 | 91.02 | INSUFFICIENT_DATA | - |
| `smc_bos_retest_entry` | `trailing_stop` | 11 | 36.36 | 3.72 | 0.44 | 8.3 | 91.3 | INSUFFICIENT_DATA | - |
| `hull_rsi` | `end_of_backtest` | 6 | 83.33 | 17.98 | 0.5 | 16.996 | 101.98 | INSUFFICIENT_DATA | - |
| `cpr_narrow_bullish` | `regime_flip_bull_to_bear_batch285` | 149 | 42.28 | 1.28 | 0.09 | 0.778 | 115.93 | FAIL | - |
| `bollinger_tight` | `end_of_backtest` | 4 | 100.0 | inf | 3.3 | 29.92 | 119.68 | INSUFFICIENT_DATA | - |
| `pivot_s1_bounce` | `trailing_stop` | 17 | 47.06 | 2.75 | 0.27 | 7.17 | 121.89 | INSUFFICIENT_DATA | - |
| `stochrsi_oversold` | `strategy_time_stop_10d_batch282` | 31 | 77.42 | 20.27 | 0.66 | 4.118 | 127.66 | FAIL | - |
| `bollinger_tight` | `trailing_stop` | 63 | 11.11 | 1.63 | 0.1 | 2.103 | 132.46 | FAIL | - |
| `smc_order_block_bounce` | `end_of_backtest` | 10 | 80.0 | 3.75 | 0.47 | 15.613 | 156.13 | INSUFFICIENT_DATA | - |
| `cmf_flip` | `trailing_stop` | 117 | 30.77 | 1.27 | 0.07 | 1.419 | 166.06 | FAIL | - |
| `smc_choch_reversal` | `end_of_backtest` | 18 | 77.78 | 27.28 | 0.82 | 10.84 | 195.11 | INSUFFICIENT_DATA | - |
| `xs_momentum_top_decile` | `class_time_stop_factor_20d_batch284` | 92 | 61.96 | 2.68 | 0.36 | 2.688 | 247.28 | FAIL | - |
| `orb_stocks_in_play_long` | `trailing_stop` | 76 | 22.37 | 1.52 | 0.07 | 3.45 | 262.23 | FAIL | - |
| `xs_low_beta_long` | `trailing_stop` | 263 | 33.46 | 1.19 | 0.05 | 1.062 | 279.43 | FAIL | - |
| `xs_low_beta_long` | `end_of_backtest` | 35 | 88.57 | 36.38 | 0.43 | 9.804 | 343.15 | FAIL | - |
| `cpr_narrow_bullish` | `regime_flip_bull_to_neutral_batch285` | 55 | 72.73 | 5.35 | 0.58 | 7.0 | 384.99 | FAIL | - |
| `monthly_bias_momentum_long` | `end_of_backtest` | 52 | 82.69 | 23.85 | 0.7 | 7.446 | 387.2 | FAIL | - |
| `williams_r_oversold` | `end_of_backtest` | 32 | 90.62 | 35.85 | 0.49 | 16.002 | 512.06 | FAIL | - |
| `bollinger_lower` | `fixed_4r_2r_target_hit_batch284` | 55 | 100.0 | inf | 48.2 | 11.578 | 636.76 | PASS | (2-leg target/stop split) |
| `po3_bullish` | `class_time_stop_po3_20d_batch284` | 280 | 54.29 | 2.33 | 0.29 | 2.379 | 666.17 | FAIL | - |
| `avwap_50_reclaim` | `hybrid_50pct_target_3xatr_batch285` | 163 | 100.0 | inf | 2.03 | 9.269 | 1510.89 | PASS | - |

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
