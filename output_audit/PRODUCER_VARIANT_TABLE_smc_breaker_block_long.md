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

**R5 baseline:** 352 fires / 161 tickers / holdout n=147 / 2022-05-06..2026-05-04 (`output_r5_rung4_chunk1`)

## Section 2 - Table A: parameter inventory

| ID | producer | parameter | production | band tested | subset-safe | status | why this band |
|---|---|---|---|---|---|---|---|
| P1 | `_smc.swing_highs_lows` | `swing_length` | 20 | 10, 20, 30, 50 | NO - needs engine resim | **UNTESTED** | library default is 50; production overrides to 20. Band brackets both. |
| P2 | `_smc.ob` | `close_mitigation` | False | False, True | YES - cube-gradable, free | **TESTED** | boolean - both values ARE the band. True = mitigated on CLOSE only. |
| P3 | `ob_events.tail(N)` | `tail_n` | 20 | 3, 5, 10, 20 | YES - cube-gradable, free | **TESTED** | measured rank of qualifying event was 1-4 (B1501); band spans that. |
| P4 | `recency filter on OB age` | `age_bars_max` | none | 60, 120, 180, 250, none | YES - cube-gradable, free | **TESTED** | measured real retests 45-134 bars, latches 294-469, gap 134-294 (B1501). |
| P5 | `break test (close > top)` | `break_pct_max` | none | 0.010, 0.020, 0.030, 0.050, none | YES - cube-gradable, free | **PENDING** | NEW-GATE, OWNER-APPROVED B1507 (was N/A - production has no such parameter; `close > top` is a strict inequality). Band from the B1501 measurement: real retests 0.5-2.7pct from the zone, stale latches 7.5-60pct, empty gap 3-7pct. Caps at 1/2/3pct bracket the retest population; 5pct sits in the gap; None = production. Direction is an UPPER bound (L359: a breaker block is a RETEST, so CLOSER is stricter). |
| P6 | `compute_ema_sma` | `span` | 200 | 9, 20, 21, 50, 200 | NO - needs engine resim | **UNTESTED** | ALL spans the producer emits (READ technical.py:750 pairs (9,21),(20,50),(50,200)). B1507 widened from [50,200] - the earlier band silently dropped 9/20/21 with no stated rule (#165). 9/20/21 are short-horizon and weak trend filters economically, but exclusion must be a MEASURED result, not a pre-judgement. Spans 100/250 do NOT exist -> NEW-GATE, ask owner. |

## Section 3 - Table B: combination results

| close_mitigation | break_pct_max | age_bars_max | tail_n | fires | ho n | full n | exit | **Sharpe** | **PF** | **Sortino** | **PSR** | win% | payoff | expectancy | p | CI-lo | gates | failing | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| False | none | none | 10 | 235 | 109 | 235 | breakeven_plus_trail | 0.845 | 2.919 | 3.447 | 1.000 | 0.486 | 3.080 | 7.265 | 0.003 | 0.231 | 5/6 | pooled_sharpe | FAIL |
| False | none | none | 20 | 235 | 109 | 235 | breakeven_plus_trail | 0.845 | 2.919 | 3.447 | 1.000 | 0.486 | 3.080 | 7.265 | 0.003 | 0.231 | 5/6 | pooled_sharpe | FAIL |
| True | none | none | 10 | 234 | 108 | 234 | breakeven_plus_trail | 0.860 | 2.980 | 3.491 | 1.000 | 0.491 | 3.090 | 7.411 | 0.003 | 0.243 | 5/6 | pooled_sharpe | FAIL |
| True | none | none | 20 | 234 | 108 | 234 | breakeven_plus_trail | 0.860 | 2.980 | 3.491 | 1.000 | 0.491 | 3.090 | 7.411 | 0.003 | 0.243 | 5/6 | pooled_sharpe | FAIL |
| False | none | none | 3 | 130 | 54 | 130 | breakeven_plus_trail | 0.409 | 1.507 | 1.090 | 1.000 | 0.389 | 2.370 | 2.170 | 0.153 | -0.379 | 5/6 | pooled_sharpe | FAIL |
| True | none | none | 3 | 126 | 52 | 126 | breakeven_plus_trail | 0.401 | 1.432 | 1.038 | 1.000 | 0.385 | 2.290 | 1.848 | 0.193 | -0.508 | 5/6 | pooled_sharpe | FAIL |
| False | none | none | 5 | 204 | 84 | 204 | breakeven_plus_trail | 0.773 | 2.169 | 2.191 | none | 0.464 | 2.500 | 4.675 | 0.012 | 0.095 | 4/6 | pooled_sharpe, psr | FAIL |
| True | none | none | 5 | 203 | 83 | 203 | breakeven_plus_trail | 0.799 | 2.229 | 2.251 | none | 0.482 | 2.400 | 4.843 | 0.010 | 0.116 | 4/6 | pooled_sharpe, psr | FAIL |
| True | none | 250 | 5 | 81 | 25 | 81 | breakeven_plus_trail | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| True | none | 250 | 10 | 81 | 25 | 81 | breakeven_plus_trail | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| True | none | 250 | 20 | 81 | 25 | 81 | breakeven_plus_trail | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| False | none | 250 | 5 | 79 | 24 | 79 | time_stop_10d | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| False | none | 250 | 10 | 79 | 24 | 79 | time_stop_10d | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| False | none | 250 | 20 | 79 | 24 | 79 | time_stop_10d | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| True | none | 250 | 3 | 77 | 25 | 77 | breakeven_plus_trail | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| False | none | 250 | 3 | 76 | 24 | 76 | time_stop_10d | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| True | none | 180 | 5 | 56 | 15 | 56 | time_stop_10d | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| True | none | 180 | 10 | 56 | 15 | 56 | time_stop_10d | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| True | none | 180 | 20 | 56 | 15 | 56 | time_stop_10d | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| False | none | 180 | 3 | 56 | 16 | 56 | breakeven_plus_trail | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| False | none | 180 | 5 | 56 | 16 | 56 | breakeven_plus_trail | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| False | none | 180 | 10 | 56 | 16 | 56 | breakeven_plus_trail | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| False | none | 180 | 20 | 56 | 16 | 56 | breakeven_plus_trail | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| True | none | 180 | 3 | 55 | 15 | 55 | time_stop_10d | none | none | none | none | none | none | none | none | none | -/6 | - | BELOW_POWER_FLOOR |
| False | none | 120 | 3 | 29 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 120 | 5 | 29 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 120 | 10 | 29 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 120 | 20 | 29 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 120 | 3 | 28 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 120 | 5 | 28 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 120 | 10 | 28 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 120 | 20 | 28 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | none | 10 | 20 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | none | 20 | 20 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | none | 5 | 19 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | none | 5 | 18 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | none | 10 | 18 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | none | 20 | 18 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | none | 3 | 15 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | none | 3 | 13 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | none | 10 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | none | 20 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 250 | 3 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 250 | 5 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 250 | 10 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 250 | 20 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 250 | 3 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 250 | 5 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 250 | 10 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 250 | 20 | 9 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | none | 5 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 180 | 3 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 180 | 5 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 180 | 10 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 180 | 20 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | none | 5 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | none | 10 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | none | 20 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 180 | 3 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 180 | 5 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 180 | 10 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 180 | 20 | 8 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 120 | 3 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 120 | 5 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 120 | 10 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 120 | 20 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | none | 3 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 120 | 3 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 120 | 5 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 120 | 10 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 120 | 20 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 60 | 3 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 60 | 5 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 60 | 10 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 60 | 20 | 7 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | none | 10 | 6 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | none | 20 | 6 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 60 | 3 | 6 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 60 | 5 | 6 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 60 | 10 | 6 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 60 | 20 | 6 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | none | 5 | 5 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | none | 3 | 5 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | none | 5 | 5 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | none | 10 | 5 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | none | 20 | 5 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 120 | 3 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 120 | 5 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 120 | 10 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 120 | 20 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 180 | 3 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 180 | 5 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 180 | 10 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 180 | 20 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 250 | 3 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 250 | 5 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 250 | 10 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 250 | 20 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | none | 3 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 120 | 3 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 120 | 5 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 120 | 10 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 120 | 20 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 180 | 3 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 180 | 5 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 180 | 10 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 180 | 20 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 250 | 3 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 250 | 5 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 250 | 10 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 250 | 20 | 4 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 120 | 3 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 120 | 5 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 120 | 10 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 120 | 20 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 180 | 3 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 180 | 5 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 180 | 10 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 180 | 20 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 250 | 3 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 250 | 5 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 250 | 10 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 250 | 20 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | none | 3 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 120 | 3 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 120 | 5 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 120 | 10 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 120 | 20 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 180 | 3 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 180 | 5 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 180 | 10 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 180 | 20 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 250 | 3 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 250 | 5 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 250 | 10 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 250 | 20 | 3 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | none | 10 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | none | 20 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 60 | 3 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 60 | 5 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 60 | 10 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 60 | 20 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 60 | 3 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 60 | 5 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 60 | 10 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 60 | 20 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 60 | 3 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 60 | 5 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 60 | 10 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 60 | 20 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 60 | 3 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 60 | 5 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 60 | 10 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 60 | 20 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 60 | 3 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 60 | 5 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 60 | 10 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 60 | 20 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 60 | 3 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 60 | 5 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 60 | 10 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 60 | 20 | 1 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 60 | 3 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 60 | 5 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 60 | 10 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 60 | 20 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 120 | 3 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 120 | 5 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 120 | 10 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 120 | 20 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 180 | 3 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 180 | 5 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 180 | 10 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 180 | 20 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 250 | 3 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 250 | 5 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 250 | 10 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | 250 | 20 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | none | 3 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| True | 0.010 | none | 5 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 60 | 3 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 60 | 5 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 60 | 10 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 60 | 20 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 120 | 3 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 120 | 5 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 120 | 10 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 120 | 20 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 180 | 3 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 180 | 5 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 180 | 10 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 180 | 20 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 250 | 3 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 250 | 5 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 250 | 10 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | 250 | 20 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | none | 3 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | none | 5 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | none | 10 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |
| False | 0.010 | none | 20 | 0 | none | none | - | none | none | none | none | none | none | none | none | none | -/6 | - | ZERO_FIRES |

## Verdict (CHECKLIST #182 - denominator required)

**0 of 200 combinations passed, across 3 of 6 applicable producers.**

- graded: 8 | non-gradable: 192
- **FULL FACTORIAL = 4000** (4 (P1) x 2 (P2) x 4 (P3) x 5 (P4) x 5 (P5) x 5 (P6)); combinations run = 200 = **5% of factorial**
- free (subset-safe) subspace = 200 | needs engine resim = 3800
- UNTESTED producers: P1 swing_length, P6 span

*Generated by `scripts/producer_variant_table.py` - regenerate, do not hand-edit.*