# Phase 1 (B1063) Strategy-Fire Coverage Audit

**Generated:** 2026-06-28
**Source data:** `trade_log_checkpoint.csv` from B1063 i-05e26af3963feca9c Phase 1 output
**Council:** 165 RECOMMEND Option-4 + Option-5 hybrid (CLASSIFIED COVERAGE + EXIT-METHOD-CUBE)

---

## 🔴 CRITICAL FINDING #1 — PIVOT #38 CANDIDATE: ENGINE RUNNING DEPLOYMENT MODE, NOT CUBE MODE

**Evidence:** trade ratio = trades/entries = **1.00** (CUBE mode would be ~26).

| Metric | Value | Expected (CUBE) |
|---|---|---|
| Total trades | 109 | 109 entries × 26 exits = **2,834** |
| Unique (strategy, ticker, entry_date) entries | 109 | 109 |
| Trades per entry ratio | **1.00** | **26** |
| Distinct exit methods used | **4 of 26** | 26 |
| Mean exits tested per fired strategy | **1.10** | 26 |
| Max exits tested per fired strategy | 2 | 26 |
| Single-exit-only strategies | **38 of 42** | 0 |

**Per memory rule `project_phase_1a_beta_is_exit_cube`:** *"every entry must simulate every exit (4,650 cells). Single-config-per-strategy via STRATEGY_EXIT_OVERRIDE is the DEPLOYMENT mode, not the backtest mode."*

**Phase 1A-β cube spec:** 219 × 26 = **5,694 cells**. Phase 1 NVDA produced ~109 entries × 1 exit = 109 cells covered. **CUBE mode would have produced ~2,834 cells (109 × 26)** — but engine ran in deployment mode (one exit per strategy from STRATEGY_EXIT_OVERRIDE).

### 22 of 26 exit methods NEVER triggered in Phase 1

```
atr_trail_1x                        atr_trail_2x
atr_trail_mae_conditional           atr_trail_vix_conditional
break_even_at_1r                    breakeven_plus_trail
chandelier_3x                       class_time_stop
earnings_blackout                   fixed_4r_2r
hybrid_50pct_target                 ma_exit_ema9
mfe_lockin_trail                    multi_tier_partial
next_pivot_target                   r_multiple_2r
r_multiple_3r                       regime_flip
reverse_signal                      smart_money_reversal
smc_mitigation_zone                 time_stop_10d
time_stop_20d                       trailing_10pct
trailing_15pct                      trailing_5pct
```

### 4 of 26 exit methods used (all from deployment defaults)

| Exit method | Trades | % |
|---|---|---|
| `trailing_stop` | 101 | 92.6% |
| `time_stop_20d_mfe<0.5pct_batch213` | 6 | 5.5% |
| `time_stop_50d_mfe<0.5pct_batch213` | 1 | 0.9% |
| `fixed_4r_2r_target_hit_batch284` | 1 | 0.9% |

---

## 🔴 CRITICAL FINDING #2 — PIVOT #39 CANDIDATE: 119 SUSPECT SILENT STRATEGIES

**Engine processed 219 active strategies on NVDA × 4y. Only 42 fired (19.2%).**

### Silent strategy classification

| Class | Count | Expected behavior |
|---|---|---|
| **SINGLE_TICKER_NOOP** (cross-sectional, pairs, xs, breadth) | 8 | ✅ Expected silent on 1-ticker |
| **EVENT_REQUIRED** (earnings, insider, 13F, M&A, analyst) | 17 | ✅ Expected silent on NVDA-only (event scarcity) |
| **SECTOR_MISMATCH** (bond, vix, dxy, fx, commodity) | 2 | ✅ Expected silent (NVDA is tech) |
| **DIRECTION_BIAS_UPTREND** (_short variants on uptrending NVDA) | 31 | ⚠ Partially expected |
| **🔴 SUSPECT SILENT (potential PIVOT #39)** | **119** | ❌ Should fire — investigate |

### 🔴 Top 50 SUSPECT SILENT strategies (basic price-action/momentum/trend; SHOULD fire on NVDA × 4y)

```
 1. 52w_high_breakout                    26. cup_and_handle_long
 2. 52w_high_breakout_pullback_long      27. cup_and_handle_retest_long
 3. 52w_high_breakout_with_smart_money   28. death_cross_50_200_volume
 4. 52w_low_breakdown                    29. doji_at_support
 5. 52wh_break_retest                    30. donchian_breakout_long
 6. adx_initiation                       31. donchian_breakout_retest_long
 7. avwap_252_breakout                   32. double_bottom_long
 8. avwap_50_reclaim                     33. flag_bull_long
 9. bb_squeeze_volume                    34. flag_bull_retest_long
10. bollinger_tight_with_smart_money     35. golden_cross_20_50
11. break_retest_confluence              36. golden_cross_50_200
12. bullish_engulfing_support            37. golden_cross_9_21
13. camarilla_r4_breakout                38. golden_cross_volume
14. camarilla_s3_bounce                  39. halloween_seasonal_long
15. classification_change_breakout_long  40. hammer_at_support_long
16. classification_change_momentum_long  41. head_and_shoulders_bottom_long
17. classification_change_oversold_long  42. htf_aligned_breakout_long
18. classification_change_recent_long    43. hull_rsi
19. classification_change_to_tech_long   44. ichimoku_cloud_breakdown
20. classification_change_volume_long    45. ichimoku_cloud_breakout
21. classification_change_with_institut  46. ichimoku_tk_cross
22. cpr_narrow_bullish                   47. institutional_breakout_confirm
23. cpr_narrow_momentum                  48. institutional_cluster_long
24. donchian_breakout_with_smart_money   49. institutional_committed_growth
25. ...                                  50. institutional_high_conviction
... and 69 more
```

**These are STANDARD strategies that fired countless times in prior runs.** Their silence on NVDA × 4y is suspicious. Possible causes:
- (a) Producer bug: signal not computed
- (b) Threshold too tight: FIRE_STARVED at single-ticker scale
- (c) MAX 30 candidates/day cap: filtered before exit_manager
- (d) Confidence tier filter: too restrictive
- (e) Engine-internal bug (deployment-mode cube fan-out missing)

---

## What DID fire (42 strategies, 109 trades)

### Top 20 by fire count

| Strategy | Fires | Direction | Note |
|---|---|---|---|
| pairs_mean_reversion_long | 10 | long | ⚠ Cross-sectional on 1 ticker?! |
| pairs_mean_reversion_short | 8 | short | ⚠ Cross-sectional on 1 ticker?! |
| mmsm_short | 7 | short | ICT pattern |
| stochrsi_overbought_short | 6 | short | Mean reversion |
| xs_momentum_quality_combined | 6 | long | Cross-sectional fired?! |
| tema_dema | 5 | long | Trend |
| macd_fast_crossover | 4 | long/short | Momentum |
| macd_crossover | 4 | long/short | Momentum |
| risk_off_bond_equity_short | 4 | short | Macro-pair |
| cmf_flip | 4 | long/short | Volume flow |
| week_opening_gap_fill_down | 4 | short | Gap fade |
| smc_choch_reversal | 4 | long/short | ICT |
| r1_break_retest | 3 | long | Pivot break |
| morning_star | 3 | long | Candle |
| force_index_breakout | 3 | long | Volume momentum |
| donchian_10_breakout | 3 | long | Channel break |

**Anomaly:** `pairs_mean_reversion_long/short` and `xs_momentum_quality_combined` are CROSS-SECTIONAL strategies. They should NOT fire with 1 ticker. Their fire suggests engine treating NVDA as both legs of a pair, or some default reference index being used as the second ticker.

### Direction balance (sanity check)

| Direction | Count | % |
|---|---|---|
| short | 61 | 56% |
| long | 48 | 44% |

✅ Reasonable balance (counter-intuitive for uptrending NVDA but consistent with mean-reversion strategies firing on dips).

### Regime distribution

| Regime | Count | % |
|---|---|---|
| bull | 57 | 52% |
| bear | 49 | 45% |
| neutral | 3 | 3% |

✅ Reasonable across 4y window (2022-05 → 2026-05 includes 2022 bear).

---

## Strategy × Exit_Method matrix (sparse; deployment mode)

42 strategies × 4 exit methods = 168 possible cells. Only 49 cells non-zero (~29%). Per-strategy diversity: mean 1.10 exits (max 2), 38 strategies tested only 1 exit method.

```
Most common pattern: every strategy uses trailing_stop as exit.
3 exceptions (mmsm_short, week_opening_gap_fill_down, risk_off_bond_equity_short)
also used time_stop_20d_mfe<0.5pct (B213 batch convergence).
bollinger_lower used fixed_4r_2r_target_hit (B284 batch).
tema_dema used time_stop_50d_mfe<0.5pct (B213 batch).
```

---

## Gaps summary

| Gap | Status | Action |
|---|---|---|
| 🔴 PIVOT #38 — engine in DEPLOYMENT mode not CUBE mode | unfixed | Surface to owner; Council decision needed |
| 🔴 PIVOT #39 — 119 SUSPECT SILENT strategies | unfixed | Per-strategy investigation; cross-ref with FIRE_STARVED list |
| ⚠ Cross-sectional strategies firing on 1 ticker | anomaly | Investigate pairs/xs strategy logic on single-ticker scope |
| ⚠ 22 of 26 exit methods untested | consequence of #38 | Will resolve when cube mode active |

## Next steps (Council 166 needed)

1. **Surface findings to owner** ✅ this report
2. **Decide on PIVOT #38**: abort Phase D + relaunch in CUBE mode OR let deployment-mode run complete + relaunch cube separately
3. **Decide on PIVOT #39**: investigate 119 SUSPECT SILENT in parallel during Phase D wait OR defer to post-completion
4. **Phase 2 re-audit** (when Phase 2 PASS lands ~16:13 UTC): same coverage analysis on 10-ticker data; classifications get more meaningful

## Pre-flight CHECKLIST compliance

- #25 Owner forensics request
- #45 Pre-flight visible
- #67 Per-turn doc-sync (this report + commit)
- #94 EXECUTION_QUEUE pivots #38 + #39 candidates
- #105 Source-read writer.py + screener.py + config to verify ALL_STRATEGIES + DEPRECATED + DISABLED + EXIT_STRATEGIES
- #110 Council 165 BEFORE analysis
- #115 Council 165 enumerate + recommend (6 options + Option-4+5 hybrid)
- #126 Real Phase 1 data = evidence artifact

## Compliance with `feedback_audit_recommendations_against_existing_directives`

Honest disclosure: the high silent-strategy count (177 of 219) is partially expected (single-ticker NVDA structural limits) and partially suspicious (PIVOT #39 candidate). The PIVOT #38 deployment-vs-cube finding contradicts `project_phase_1a_beta_is_exit_cube` memory and the CLAUDE.md banner's "219 × 26 = 5,694 cells" cube spec. Surfacing both as candidates for owner direction.
