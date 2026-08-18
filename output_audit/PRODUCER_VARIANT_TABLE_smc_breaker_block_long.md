# Producer variant table - `smc_breaker_block_long`

**Gate:** `(breaker_bullish) AND (price_above_ema_200)`

## Section 1 - boolean formula (READ from source, never recalled)

```
=============================== PRODUCER LAYER ===============================

P1  swings  =  swing_highs_lows( ohlc, swing_length = 20 )
                   -> a bar is a swing high if its high is the highest
                      across swing_length bars BEFORE and AFTER it
                   PARAMETER: swing_length = 20   (library default is 50)

P2  ob_df   =  ob( ohlc, swings, close_mitigation = False )
                   -> emits, per detected block:  OB (+1 bull / -1 bear),
                      Top, Bottom, MitigatedIndex
                   PARAMETER: close_mitigation = False
                      False -> a block counts as mitigated when the HIGH/LOW
                               pierces it
                      True  -> only when the CLOSE pierces it  (stricter)

P3  events  =  ob_df[ OB != 0 ].tail( 20 )
                   PARAMETER: tail N = 20     (hardcoded literal, not an argument)

P4  per event e:   e.is_mitigated = ( MitigatedIndex > 0 )
                                    AND ( MitigatedIndex < today_index )
                   -> no parameter; derived from P2's MitigatedIndex
                   -> MitigatedIndex = the BAR INDEX of the candle that broke
                      through the zone (smc.py:69); 0 means never mitigated.
                      It is an INDEX, not a flag - which is why an ancient block
                      stays eligible forever with no age check (S6-B1500a).

P5  per event e:   e.broken_up    = ( close > e.Top )
                   -> no parameter; strict inequality, zero buffer

P6  ema_50_200 =  compute_ema_sma( df )      # pairs (9,21),(20,50),(50,200)
       price_above_ema_200  =  close > EMA(close, span = 200)
                   PARAMETER: span = 200, emitted only from the (50,200) pair

=============================== STRATEGY LAYER ===============================

breaker_bullish  =  AT LEAST ONE event e in P3 satisfies ALL of:
                        ( e.OB == -1 )          <- bearish block      [from P2]
                        AND ( e.is_mitigated )                        [from P4]
                        AND ( e.broken_up )                           [from P5]

fires            =  ( breaker_bullish )  AND  ( price_above_ema_200 ) [from P6]
```

**R5 baseline:** None fires / 161 tickers / holdout n=147 / 2022-05-06..2026-05-04 (`output_r5_merged_1_7`)

## Section 2 - Table A: parameter inventory

| ID | producer | parameter | production | band tested | subset-safe | status | why this band |
|---|---|---|---|---|---|---|---|
| P1 | `_smc.swing_highs_lows` | `swing_length` | 20 | 5, 10, 20, 30, 50 | NO - needs engine resim | **UNTESTED** | library default is 50; production overrides to 20. Band brackets both. |
| P2 | `_smc.ob` | `close_mitigation` | False | False, True | YES - cube-gradable, free | **TESTED** | boolean - both values ARE the band. True = mitigated on CLOSE only. |
| P3 | `ob_events.tail(N)` | `tail_n` | 20 | 1, 2, 3, 5, 10, 20 | YES - cube-gradable, free | **RE-BANDED-AND-TESTED** | B1610 DEFECT - this text says the band spans the measured rank range 1-4, and it does NOT: its floor is 3, the TOP of that range. MEASURED on 420 cfg2 fires: levels 3/5/10/20 admit 39.8/68.8/98.6/100.0pct, so 10->20 moved 0 of 50 cfg1 groups. The discriminating region is 1-3 (tail_n=2 alone cuts 73pct). Also COLLINEAR with P4 age_bars_max, Spearman +0.881. RE-BAND OWNER-APPROVED AND SHIPPED (B1611): band is now 1,2,3,5,10,20. VINDICATED - tail_n=2, a level that did not exist under the old floor, won BOTH wave-1 top-10s. |
| P4 | `recency filter on OB age` | `age_bars_max` | none | 60, 120, 180, 250, none | YES - cube-gradable, free | **TESTED** | measured real retests 45-134 bars, latches 294-469, gap 134-294 (B1501). |
| P5 | `break test (close > top)` | `break_pct_max` | none | 0.010, 0.020, 0.030, 0.050, none | YES - cube-gradable, free | **PENDING** | NEW-GATE, OWNER-APPROVED B1507 (was N/A - production has no such parameter; `close > top` is a strict inequality). Band from the B1501 measurement: real retests 0.5-2.7pct from the zone, stale latches 7.5-60pct, empty gap 3-7pct. Caps at 1/2/3pct bracket the retest population; 5pct sits in the gap; None = production. Direction is an UPPER bound (L359: a breaker block is a RETEST, so CLOSER is stricter). |
| P6 | `compute_ema_sma` | `span` | 200 | 9, 20, 21, 50, 100, 150, 200 | NO - needs engine resim | **UNTESTED** | ALL spans the producer emits (READ technical.py:750 pairs (9,21),(20,50),(50,200)). B1507 widened from [50,200] - the earlier band silently dropped 9/20/21 with no stated rule (#165). 9/20/21 are short-horizon and weak trend filters economically, but exclusion must be a MEASURED result, not a pre-judgement. B1686: spans 100 and 150 ADDED to the producer on owner directive 2026-08-18 - they did not exist, which is why P6 could not sweep them (S6-B1507b). Band is now 7 values; 250 still absent. |

## Section 3 - Table B: combination results

| close_mitigation | age_bars_max | tail_n | fires | ho n | full n | exit | **Sharpe** | **PF** | **Sortino** | **PSR** | win% | payoff | expectancy | p | CI-lo | gates | failing | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| False | none | 2 | 114 | 66 | 114 | hybrid_50pct_target | 1.018 | 2.969 | 999.000 | 1.000 | 0.742 | 1.030 | 5.173 | 0.000 | 0.425 | 6/6 | - | PASS |
| False | 250 | 5 | 120 | 68 | 120 | hybrid_50pct_target | 0.519 | 1.711 | 999.000 | 1.000 | 0.647 | 0.930 | 2.559 | 0.037 | -0.058 | 5/6 | pooled_sharpe | FAIL |
| False | 250 | 10 | 120 | 68 | 120 | hybrid_50pct_target | 0.519 | 1.711 | 999.000 | 1.000 | 0.647 | 0.930 | 2.559 | 0.037 | -0.058 | 5/6 | pooled_sharpe | FAIL |
| False | 250 | 20 | 120 | 68 | 120 | hybrid_50pct_target | 0.519 | 1.711 | 999.000 | 1.000 | 0.647 | 0.930 | 2.559 | 0.037 | -0.058 | 5/6 | pooled_sharpe | FAIL |
| True | none | 2 | 89 | 50 | 89 | hybrid_50pct_target | 1.305 | 4.202 | 999.000 | 1.000 | 0.800 | 1.050 | 6.532 | 0.000 | 0.607 | 5/6 | min_trades_full_period | FAIL |
| True | 250 | 2 | 79 | 43 | 79 | hybrid_50pct_target | 1.016 | 3.120 | 999.000 | 1.000 | 0.767 | 0.950 | 5.029 | 0.002 | 0.282 | 5/6 | min_trades_full_period | FAIL |
| True | none | 3 | 148 | 75 | 148 | r_multiple_3r | 0.413 | 1.198 | 1.145 | 1.000 | 0.320 | 2.550 | 0.535 | 0.270 | -0.911 | 4/6 | pooled_sharpe, profit_factor | FAIL |
| True | 250 | 5 | 105 | 57 | 105 | breakeven_plus_trail | 0.958 | 3.170 | 2.977 | none | 0.386 | 5.040 | 4.251 | 0.009 | 0.148 | 4/6 | pooled_sharpe, psr | FAIL |
| True | 250 | 10 | 105 | 57 | 105 | breakeven_plus_trail | 0.958 | 3.170 | 2.977 | none | 0.386 | 5.040 | 4.251 | 0.009 | 0.148 | 4/6 | pooled_sharpe, psr | FAIL |
| True | 250 | 20 | 105 | 57 | 105 | breakeven_plus_trail | 0.958 | 3.170 | 2.977 | none | 0.386 | 5.040 | 4.251 | 0.009 | 0.148 | 4/6 | pooled_sharpe, psr | FAIL |
| True | 250 | 3 | 99 | 52 | 99 | breakeven_plus_trail | 1.037 | 3.772 | 3.949 | none | 0.365 | 6.550 | 4.707 | 0.007 | 0.194 | 4/6 | psr, min_trades_full_period | FAIL |
| False | 250 | 2 | 98 | 55 | 98 | hybrid_50pct_target | 0.767 | 2.332 | 999.000 | 1.000 | 0.709 | 0.960 | 3.954 | 0.007 | 0.136 | 4/6 | pooled_sharpe, min_trades_full_period | FAIL |
| False | 180 | 5 | 93 | 55 | 93 | hybrid_50pct_target | 0.754 | 2.327 | 999.000 | 1.000 | 0.709 | 0.950 | 3.936 | 0.007 | 0.132 | 4/6 | pooled_sharpe, min_trades_full_period | FAIL |
| False | 180 | 10 | 93 | 55 | 93 | hybrid_50pct_target | 0.754 | 2.327 | 999.000 | 1.000 | 0.709 | 0.950 | 3.936 | 0.007 | 0.132 | 4/6 | pooled_sharpe, min_trades_full_period | FAIL |
| False | 180 | 20 | 93 | 55 | 93 | hybrid_50pct_target | 0.754 | 2.327 | 999.000 | 1.000 | 0.709 | 0.950 | 3.936 | 0.007 | 0.132 | 4/6 | pooled_sharpe, min_trades_full_period | FAIL |
| False | 180 | 3 | 92 | 55 | 92 | hybrid_50pct_target | 0.754 | 2.327 | 999.000 | 1.000 | 0.709 | 0.950 | 3.936 | 0.007 | 0.132 | 4/6 | pooled_sharpe, min_trades_full_period | FAIL |
| False | 180 | 2 | 85 | 51 | 85 | hybrid_50pct_target | 0.811 | 2.533 | 999.000 | 1.000 | 0.725 | 0.960 | 4.293 | 0.006 | 0.166 | 4/6 | pooled_sharpe, min_trades_full_period | FAIL |
| True | 180 | 5 | 78 | 44 | 78 | trailing_10pct | 0.568 | 2.014 | 1.795 | 1.000 | 0.500 | 2.010 | 2.864 | 0.061 | -0.163 | 4/6 | pooled_sharpe, min_trades_full_period | FAIL |
| True | 180 | 10 | 78 | 44 | 78 | trailing_10pct | 0.568 | 2.014 | 1.795 | 1.000 | 0.500 | 2.010 | 2.864 | 0.061 | -0.163 | 4/6 | pooled_sharpe, min_trades_full_period | FAIL |
| True | 180 | 20 | 78 | 44 | 78 | trailing_10pct | 0.568 | 2.014 | 1.795 | 1.000 | 0.500 | 2.010 | 2.864 | 0.061 | -0.163 | 4/6 | pooled_sharpe, min_trades_full_period | FAIL |
| True | 180 | 3 | 76 | 43 | 76 | trailing_10pct | 0.562 | 2.000 | 1.800 | 1.000 | 0.488 | 2.090 | 2.889 | 0.064 | -0.172 | 4/6 | pooled_sharpe, min_trades_full_period | FAIL |
| False | none | 10 | 320 | 153 | 320 | r_multiple_2r | -0.107 | 0.962 | -0.279 | 0.104 | 0.320 | 2.040 | -0.094 | 0.580 | -1.150 | 2/6 | pooled_sharpe, profit_factor, sortino, psr | FAIL |
| False | none | 20 | 320 | 153 | 320 | r_multiple_2r | -0.107 | 0.962 | -0.279 | 0.104 | 0.320 | 2.040 | -0.094 | 0.580 | -1.150 | 2/6 | pooled_sharpe, profit_factor, sortino, psr | FAIL |
| True | none | 10 | 298 | 139 | 298 | r_multiple_2r | -0.115 | 0.960 | -0.299 | 0.099 | 0.324 | 2.000 | -0.103 | 0.581 | -1.217 | 2/6 | pooled_sharpe, profit_factor, sortino, psr | FAIL |
| True | none | 20 | 298 | 139 | 298 | r_multiple_2r | -0.115 | 0.960 | -0.299 | 0.099 | 0.324 | 2.000 | -0.103 | 0.581 | -1.217 | 2/6 | pooled_sharpe, profit_factor, sortino, psr | FAIL |
| False | none | 5 | 248 | 117 | 248 | r_multiple_2r | 0.072 | 1.026 | 0.180 | 0.788 | 0.333 | 2.050 | 0.065 | 0.453 | -1.123 | 2/6 | pooled_sharpe, profit_factor, sortino, psr | FAIL |
| True | none | 5 | 216 | 99 | 216 | r_multiple_3r | -0.050 | 0.979 | -0.146 | 0.316 | 0.273 | 2.610 | -0.061 | 0.533 | -1.223 | 2/6 | pooled_sharpe, profit_factor, sortino, psr | FAIL |
| False | none | 3 | 173 | 93 | 173 | r_multiple_3r | 0.073 | 1.032 | 0.206 | 0.769 | 0.280 | 2.660 | 0.088 | 0.452 | -1.116 | 2/6 | pooled_sharpe, profit_factor, sortino, psr | FAIL |
| False | 250 | 3 | 117 | 66 | 117 | r_multiple_3r | -0.037 | 0.983 | -0.094 | 0.385 | 0.258 | 2.830 | -0.045 | 0.521 | -1.404 | 2/6 | pooled_sharpe, profit_factor, sortino, psr | FAIL |
| False | none | 10 | 89 | 53 | 89 | next_pivot_target | 0.000 | 1.000 | 0.000 | none | 0.679 | 0.470 | 0.000 | 0.500 | -1.389 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | none | 20 | 89 | 53 | 89 | next_pivot_target | 0.000 | 1.000 | 0.000 | none | 0.679 | 0.470 | 0.000 | 0.500 | -1.389 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | none | 5 | 86 | 52 | 86 | next_pivot_target | -0.148 | 0.920 | -0.153 | 0.139 | 0.673 | 0.450 | -0.143 | 0.579 | -1.603 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | none | 3 | 78 | 50 | 78 | atr_trail_1x | -2.733 | 0.406 | -5.929 | 0.000 | 0.220 | 1.440 | -0.937 | 0.994 | -4.954 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 180 | 2 | 70 | 41 | 70 | atr_trail_1x | -1.687 | 0.545 | -2.510 | 0.000 | 0.268 | 1.490 | -0.825 | 0.921 | -4.060 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 3 | 70 | 46 | 70 | atr_trail_1x | -2.422 | 0.444 | -5.274 | 0.000 | 0.239 | 1.410 | -0.873 | 0.984 | -4.694 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 5 | 70 | 46 | 70 | atr_trail_1x | -2.422 | 0.444 | -5.274 | 0.000 | 0.239 | 1.410 | -0.873 | 0.984 | -4.694 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 10 | 70 | 46 | 70 | atr_trail_1x | -2.422 | 0.444 | -5.274 | 0.000 | 0.239 | 1.410 | -0.873 | 0.984 | -4.694 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 20 | 70 | 46 | 70 | atr_trail_1x | -2.422 | 0.444 | -5.274 | 0.000 | 0.239 | 1.410 | -0.873 | 0.984 | -4.694 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | none | 2 | 70 | 45 | 70 | atr_trail_1x | -2.353 | 0.446 | -5.278 | 0.000 | 0.222 | 1.560 | -0.852 | 0.982 | -4.616 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | none | 10 | 68 | 43 | 68 | atr_trail_1x | -2.442 | 0.429 | -6.061 | 0.000 | 0.209 | 1.620 | -0.860 | 0.983 | -4.771 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | none | 20 | 68 | 43 | 68 | atr_trail_1x | -2.442 | 0.429 | -6.061 | 0.000 | 0.209 | 1.620 | -0.860 | 0.983 | -4.771 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | none | 5 | 66 | 43 | 66 | atr_trail_1x | -2.442 | 0.429 | -6.061 | 0.000 | 0.209 | 1.620 | -0.860 | 0.983 | -4.771 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 2 | 66 | 43 | 66 | atr_trail_1x | -2.188 | 0.470 | -4.892 | 0.000 | 0.233 | 1.550 | -0.809 | 0.971 | -4.493 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | none | 10 | 65 | 38 | 65 | atr_trail_1x | -3.930 | 0.302 | -6.376 | 0.000 | 0.211 | 1.130 | -1.166 | 0.999 | -6.584 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | none | 20 | 65 | 38 | 65 | atr_trail_1x | -3.930 | 0.302 | -6.376 | 0.000 | 0.211 | 1.130 | -1.166 | 0.999 | -6.584 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 120 | 2 | 63 | 37 | 63 | atr_trail_1x | -1.194 | 0.631 | -1.734 | 0.000 | 0.324 | 1.310 | -0.659 | 0.846 | -3.510 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 120 | 3 | 63 | 37 | 63 | atr_trail_1x | -1.194 | 0.631 | -1.734 | 0.000 | 0.324 | 1.310 | -0.659 | 0.846 | -3.510 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 120 | 5 | 63 | 37 | 63 | atr_trail_1x | -1.194 | 0.631 | -1.734 | 0.000 | 0.324 | 1.310 | -0.659 | 0.846 | -3.510 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 120 | 10 | 63 | 37 | 63 | atr_trail_1x | -1.194 | 0.631 | -1.734 | 0.000 | 0.324 | 1.310 | -0.659 | 0.846 | -3.510 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 120 | 20 | 63 | 37 | 63 | atr_trail_1x | -1.194 | 0.631 | -1.734 | 0.000 | 0.324 | 1.310 | -0.659 | 0.846 | -3.510 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | none | 5 | 62 | 37 | 62 | atr_trail_1x | -4.109 | 0.297 | -6.720 | 0.000 | 0.189 | 1.270 | -1.206 | 0.999 | -6.857 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | none | 3 | 61 | 42 | 61 | atr_trail_1x | -2.345 | 0.442 | -5.787 | 0.000 | 0.214 | 1.620 | -0.832 | 0.977 | -4.699 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 180 | 3 | 61 | 41 | 61 | atr_trail_1x | -1.659 | 0.554 | -3.722 | 0.000 | 0.268 | 1.510 | -0.630 | 0.923 | -3.966 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 180 | 5 | 61 | 41 | 61 | atr_trail_1x | -1.659 | 0.554 | -3.722 | 0.000 | 0.268 | 1.510 | -0.630 | 0.923 | -3.966 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 180 | 10 | 61 | 41 | 61 | atr_trail_1x | -1.659 | 0.554 | -3.722 | 0.000 | 0.268 | 1.510 | -0.630 | 0.923 | -3.966 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 180 | 20 | 61 | 41 | 61 | atr_trail_1x | -1.659 | 0.554 | -3.722 | 0.000 | 0.268 | 1.510 | -0.630 | 0.923 | -3.966 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 180 | 2 | 60 | 40 | 60 | atr_trail_1x | -1.758 | 0.533 | -3.973 | 0.000 | 0.250 | 1.600 | -0.676 | 0.933 | -4.086 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | none | 3 | 54 | 35 | 54 | atr_trail_1x | -3.742 | 0.333 | -6.534 | 0.000 | 0.200 | 1.330 | -1.076 | 0.997 | -6.563 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 3 | 54 | 38 | 54 | atr_trail_1x | -1.971 | 0.495 | -4.888 | 0.000 | 0.237 | 1.600 | -0.744 | 0.948 | -4.390 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 5 | 54 | 38 | 54 | atr_trail_1x | -1.971 | 0.495 | -4.888 | 0.000 | 0.237 | 1.600 | -0.744 | 0.948 | -4.390 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 10 | 54 | 38 | 54 | atr_trail_1x | -1.971 | 0.495 | -4.888 | 0.000 | 0.237 | 1.600 | -0.744 | 0.948 | -4.390 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 20 | 54 | 38 | 54 | atr_trail_1x | -1.971 | 0.495 | -4.888 | 0.000 | 0.237 | 1.600 | -0.744 | 0.948 | -4.390 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | none | 10 | 53 | 33 | 53 | atr_trail_1x | -1.519 | 0.568 | -4.157 | 0.001 | 0.242 | 1.780 | -0.599 | 0.882 | -4.058 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | none | 20 | 53 | 33 | 53 | atr_trail_1x | -1.519 | 0.568 | -4.157 | 0.001 | 0.242 | 1.780 | -0.599 | 0.882 | -4.058 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | none | 2 | 53 | 37 | 53 | atr_trail_1x | -1.885 | 0.501 | -5.003 | 0.000 | 0.216 | 1.810 | -0.715 | 0.941 | -4.291 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 120 | 2 | 51 | 31 | 51 | atr_trail_1x | -1.917 | 0.504 | -2.488 | 0.000 | 0.290 | 1.230 | -0.939 | 0.921 | -4.628 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 120 | 3 | 51 | 31 | 51 | atr_trail_1x | -1.917 | 0.504 | -2.488 | 0.000 | 0.290 | 1.230 | -0.939 | 0.921 | -4.628 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 120 | 5 | 51 | 31 | 51 | atr_trail_1x | -1.917 | 0.504 | -2.488 | 0.000 | 0.290 | 1.230 | -0.939 | 0.921 | -4.628 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 120 | 10 | 51 | 31 | 51 | atr_trail_1x | -1.917 | 0.504 | -2.488 | 0.000 | 0.290 | 1.230 | -0.939 | 0.921 | -4.628 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 120 | 20 | 51 | 31 | 51 | atr_trail_1x | -1.917 | 0.504 | -2.488 | 0.000 | 0.290 | 1.230 | -0.939 | 0.921 | -4.628 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | none | 5 | 51 | 33 | 51 | atr_trail_1x | -1.519 | 0.568 | -4.157 | 0.001 | 0.242 | 1.780 | -0.599 | 0.882 | -4.058 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 2 | 50 | 35 | 50 | atr_trail_1x | -1.680 | 0.537 | -4.444 | 0.000 | 0.229 | 1.810 | -0.655 | 0.913 | -4.139 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 120 | 2 | 49 | 31 | 49 | atr_trail_1x | -0.850 | 0.722 | -1.953 | 0.003 | 0.323 | 1.520 | -0.383 | 0.750 | -3.328 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 120 | 3 | 49 | 31 | 49 | atr_trail_1x | -0.850 | 0.722 | -1.953 | 0.003 | 0.323 | 1.520 | -0.383 | 0.750 | -3.328 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 120 | 5 | 49 | 31 | 49 | atr_trail_1x | -0.850 | 0.722 | -1.953 | 0.003 | 0.323 | 1.520 | -0.383 | 0.750 | -3.328 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 120 | 10 | 49 | 31 | 49 | atr_trail_1x | -0.850 | 0.722 | -1.953 | 0.003 | 0.323 | 1.520 | -0.383 | 0.750 | -3.328 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 120 | 20 | 49 | 31 | 49 | atr_trail_1x | -0.850 | 0.722 | -1.953 | 0.003 | 0.323 | 1.520 | -0.383 | 0.750 | -3.328 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 250 | 3 | 48 | 32 | 48 | atr_trail_1x | -3.412 | 0.362 | -6.017 | 0.000 | 0.219 | 1.290 | -1.037 | 0.992 | -6.303 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 250 | 5 | 48 | 32 | 48 | atr_trail_1x | -3.412 | 0.362 | -6.017 | 0.000 | 0.219 | 1.290 | -1.037 | 0.992 | -6.303 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 250 | 10 | 48 | 32 | 48 | atr_trail_1x | -3.412 | 0.362 | -6.017 | 0.000 | 0.219 | 1.290 | -1.037 | 0.992 | -6.303 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 250 | 20 | 48 | 32 | 48 | atr_trail_1x | -3.412 | 0.362 | -6.017 | 0.000 | 0.219 | 1.290 | -1.037 | 0.992 | -6.303 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | none | 2 | 46 | 29 | 46 | atr_trail_1x | none | 0.464 | -4.370 | none | 0.241 | 1.460 | -0.751 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 180 | 3 | 46 | 34 | 46 | atr_trail_1x | -1.278 | 0.617 | -3.382 | 0.001 | 0.265 | 1.710 | -0.506 | 0.847 | -3.745 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 180 | 5 | 46 | 34 | 46 | atr_trail_1x | -1.278 | 0.617 | -3.382 | 0.001 | 0.265 | 1.710 | -0.506 | 0.847 | -3.745 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 180 | 10 | 46 | 34 | 46 | atr_trail_1x | -1.278 | 0.617 | -3.382 | 0.001 | 0.265 | 1.710 | -0.506 | 0.847 | -3.745 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 180 | 20 | 46 | 34 | 46 | atr_trail_1x | -1.278 | 0.617 | -3.382 | 0.001 | 0.265 | 1.710 | -0.506 | 0.847 | -3.745 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | none | 10 | 45 | 29 | 45 | atr_trail_1x | none | 0.322 | -7.305 | none | 0.172 | 1.540 | -1.055 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | none | 20 | 45 | 29 | 45 | atr_trail_1x | none | 0.322 | -7.305 | none | 0.172 | 1.540 | -1.055 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | none | 3 | 45 | 31 | 45 | atr_trail_1x | -1.232 | 0.625 | -3.319 | 0.002 | 0.258 | 1.800 | -0.503 | 0.827 | -3.816 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 180 | 2 | 45 | 33 | 45 | atr_trail_1x | -1.386 | 0.590 | -3.705 | 0.001 | 0.242 | 1.850 | -0.558 | 0.864 | -3.878 | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | none | 5 | 43 | 29 | 43 | atr_trail_1x | none | 0.322 | -7.305 | none | 0.172 | 1.540 | -1.055 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 250 | 2 | 43 | 28 | 43 | atr_trail_1x | none | 0.479 | -4.184 | none | 0.250 | 1.440 | -0.731 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 180 | 2 | 42 | 28 | 42 | atr_trail_1x | none | 0.479 | -4.184 | none | 0.250 | 1.440 | -0.731 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 180 | 3 | 42 | 28 | 42 | atr_trail_1x | none | 0.479 | -4.184 | none | 0.250 | 1.440 | -0.731 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 180 | 5 | 42 | 28 | 42 | atr_trail_1x | none | 0.479 | -4.184 | none | 0.250 | 1.440 | -0.731 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 180 | 10 | 42 | 28 | 42 | atr_trail_1x | none | 0.479 | -4.184 | none | 0.250 | 1.440 | -0.731 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 180 | 20 | 42 | 28 | 42 | atr_trail_1x | none | 0.479 | -4.184 | none | 0.250 | 1.440 | -0.731 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 3 | 41 | 29 | 41 | atr_trail_1x | none | 0.684 | -2.632 | none | 0.276 | 1.790 | -0.415 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 5 | 41 | 29 | 41 | atr_trail_1x | none | 0.684 | -2.632 | none | 0.276 | 1.790 | -0.415 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 10 | 41 | 29 | 41 | atr_trail_1x | none | 0.684 | -2.632 | none | 0.276 | 1.790 | -0.415 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 20 | 41 | 29 | 41 | atr_trail_1x | none | 0.684 | -2.632 | none | 0.276 | 1.790 | -0.415 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | none | 2 | 41 | 29 | 41 | atr_trail_1x | none | 0.642 | -3.138 | none | 0.241 | 2.020 | -0.478 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | none | 3 | 38 | 28 | 38 | atr_trail_1x | none | 0.337 | -6.942 | none | 0.179 | 1.550 | -1.022 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| False | 250 | 2 | 38 | 27 | 38 | atr_trail_1x | none | 0.706 | -2.401 | none | 0.259 | 2.020 | -0.382 | none | none | 1/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_full_period | FAIL |
| True | 120 | 2 | 36 | 24 | 36 | atr_trail_1x | none | 0.561 | -3.227 | none | 0.292 | 1.360 | -0.613 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| True | 120 | 3 | 36 | 24 | 36 | atr_trail_1x | none | 0.561 | -3.227 | none | 0.292 | 1.360 | -0.613 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| True | 120 | 5 | 36 | 24 | 36 | atr_trail_1x | none | 0.561 | -3.227 | none | 0.292 | 1.360 | -0.613 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| True | 120 | 10 | 36 | 24 | 36 | atr_trail_1x | none | 0.561 | -3.227 | none | 0.292 | 1.360 | -0.613 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| True | 120 | 20 | 36 | 24 | 36 | atr_trail_1x | none | 0.561 | -3.227 | none | 0.292 | 1.360 | -0.613 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| False | 180 | 3 | 35 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 180 | 5 | 35 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 180 | 10 | 35 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 180 | 20 | 35 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 2 | 35 | 24 | 35 | atr_trail_1x | none | 0.891 | -0.765 | none | 0.333 | 1.780 | -0.135 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| False | 120 | 3 | 35 | 24 | 35 | atr_trail_1x | none | 0.891 | -0.765 | none | 0.333 | 1.780 | -0.135 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| False | 120 | 5 | 35 | 24 | 35 | atr_trail_1x | none | 0.891 | -0.765 | none | 0.333 | 1.780 | -0.135 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| False | 120 | 10 | 35 | 24 | 35 | atr_trail_1x | none | 0.891 | -0.765 | none | 0.333 | 1.780 | -0.135 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| False | 120 | 20 | 35 | 24 | 35 | atr_trail_1x | none | 0.891 | -0.765 | none | 0.333 | 1.780 | -0.135 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| False | 180 | 2 | 34 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 3 | 33 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 5 | 33 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 10 | 33 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 20 | 33 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 2 | 30 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 10 | 29 | 19 | 29 | atr_trail_1x | none | 0.489 | -4.692 | none | 0.211 | 1.830 | -0.706 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| True | none | 20 | 29 | 19 | 29 | atr_trail_1x | none | 0.489 | -4.692 | none | 0.211 | 1.830 | -0.706 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| True | 180 | 3 | 28 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 5 | 28 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 10 | 28 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 20 | 28 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 2 | 28 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 5 | 27 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 2 | 27 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 5 | 27 | 17 | 27 | atr_trail_1x | none | 0.503 | -4.899 | none | 0.176 | 2.350 | -0.742 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| False | none | 10 | 27 | 17 | 27 | atr_trail_1x | none | 0.503 | -4.899 | none | 0.176 | 2.350 | -0.742 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| False | none | 20 | 27 | 17 | 27 | atr_trail_1x | none | 0.503 | -4.899 | none | 0.176 | 2.350 | -0.742 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| False | 120 | 2 | 26 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 3 | 26 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 5 | 26 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 10 | 26 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 20 | 26 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 2 | 26 | 16 | 26 | atr_trail_1x | none | 0.653 | -2.395 | none | 0.375 | 1.090 | -0.378 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| False | 60 | 3 | 26 | 16 | 26 | atr_trail_1x | none | 0.653 | -2.395 | none | 0.375 | 1.090 | -0.378 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| False | 60 | 5 | 26 | 16 | 26 | atr_trail_1x | none | 0.653 | -2.395 | none | 0.375 | 1.090 | -0.378 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| False | 60 | 10 | 26 | 16 | 26 | atr_trail_1x | none | 0.653 | -2.395 | none | 0.375 | 1.090 | -0.378 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| False | 60 | 20 | 26 | 16 | 26 | atr_trail_1x | none | 0.653 | -2.395 | none | 0.375 | 1.090 | -0.378 | none | none | 0/6 | pooled_sharpe, profit_factor, sortino, psr, min_trades_holdout, min_trades_full_period | FAIL |
| False | 60 | 2 | 24 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 3 | 24 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 5 | 24 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 10 | 24 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 20 | 24 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 3 | 23 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 3 | 22 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 2 | 22 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 3 | 22 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 5 | 22 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 10 | 22 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 20 | 22 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 2 | 22 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 3 | 22 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 5 | 22 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 10 | 22 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 20 | 22 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 250 | 3 | 21 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 250 | 5 | 21 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 250 | 10 | 21 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 250 | 20 | 21 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 3 | 20 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 5 | 20 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 10 | 20 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 20 | 20 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 2 | 20 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 2 | 19 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 2 | 19 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 3 | 19 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 5 | 19 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 10 | 19 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 20 | 19 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 250 | 2 | 19 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 2 | 19 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 3 | 19 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 5 | 19 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 10 | 19 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 20 | 19 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 180 | 3 | 18 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 180 | 5 | 18 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 180 | 10 | 18 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 180 | 20 | 18 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 2 | 17 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 3 | 17 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 5 | 17 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 10 | 17 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 20 | 17 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 2 | 17 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 180 | 2 | 17 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 2 | 14 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 3 | 14 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 5 | 14 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 10 | 14 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 20 | 14 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 2 | 13 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 3 | 13 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 5 | 13 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 10 | 13 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 20 | 13 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 2 | 13 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 3 | 13 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 5 | 13 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 10 | 13 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 20 | 13 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 5 | 12 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 10 | 12 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 20 | 12 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 2 | 11 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 3 | 11 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 5 | 11 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 10 | 11 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 20 | 11 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 3 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 5 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 10 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 20 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 3 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 2 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 3 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 5 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 10 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 20 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 2 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 3 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 5 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 10 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 20 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 2 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 2 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 2 | 6 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 3 | 6 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 5 | 6 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 10 | 6 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 20 | 6 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 2 | 5 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 3 | 5 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 5 | 5 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 10 | 5 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 20 | 5 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 2 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 3 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 5 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 10 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 20 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 180 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 250 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 180 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 250 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 180 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 250 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 180 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 250 | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 1 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 1 | 2 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 120 | 1 | 2 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 180 | 1 | 2 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 250 | 1 | 2 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 1 | 2 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 120 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 180 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 250 | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 1 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |

## Verdict (CHECKLIST #182 - denominator required)

**1 of 300 combinations passed, across 2 of 6 applicable producers.**

- graded: 124 | non-gradable: 176
- **FULL FACTORIAL = 10500** (5 (P1) x 2 (P2) x 6 (P3) x 5 (P4) x 5 (P5) x 7 (P6)); combinations run = 300 = **3% of factorial**
- free (subset-safe) subspace = 300 | needs engine resim = 10200
- UNTESTED producers: P1 swing_length, P6 span

*Generated by `scripts/producer_variant_table.py` - regenerate, do not hand-edit.*