# Producer variant table - `smc_breaker_block_long`

**Gate:** `(breaker_bullish) AND (price_above_ema_200)`

**R5 baseline:** 352 fires / 161 tickers / holdout n=147 / 2022-05-06..2026-05-04 (`output_r5_rung4_chunk1`)

## Table A - parameter inventory

| ID | producer | parameter | production | band tested | subset-safe | status | why this band |
|---|---|---|---|---|---|---|---|
| P1 | `_smc.swing_highs_lows` | `swing_length` | 20 | 10, 20, 30, 50 | NO - needs engine resim | **UNTESTED** | library default is 50; production overrides to 20. Band brackets both. |
| P2 | `_smc.ob` | `close_mitigation` | False | False, True | YES - cube-gradable, free | **TESTED** | boolean - both values ARE the band. True = mitigated on CLOSE only. |
| P3 | `ob_events.tail(N)` | `tail_n` | 20 | 3, 5, 10, 20 | YES - cube-gradable, free | **TESTED** | measured rank of qualifying event was 1-4 (B1501); band spans that. |
| P4 | `recency filter on OB age` | `age_bars_max` | none | 60, 120, 180, 250, none | YES - cube-gradable, free | **TESTED** | measured real retests 45-134 bars, latches 294-469, gap 134-294 (B1501). |
| P5 | `break test (close > top)` | `break_pct_max` | none | 0.010, 0.020, 0.030, 0.050, none | YES - cube-gradable, free | **PENDING** | NEW-GATE, OWNER-APPROVED B1507 (was N/A - production has no such parameter; `close > top` is a strict inequality). Band from the B1501 measurement: real retests 0.5-2.7pct from the zone, stale latches 7.5-60pct, empty gap 3-7pct. Caps at 1/2/3pct bracket the retest population; 5pct sits in the gap; None = production. Direction is an UPPER bound (L359: a breaker block is a RETEST, so CLOSER is stricter). |
| P6 | `compute_ema_sma` | `span` | 200 | 9, 20, 21, 50, 200 | NO - needs engine resim | **UNTESTED** | ALL spans the producer emits (READ technical.py:750 pairs (9,21),(20,50),(50,200)). B1507 widened from [50,200] - the earlier band silently dropped 9/20/21 with no stated rule (#165). 9/20/21 are short-horizon and weak trend filters economically, but exclusion must be a MEASURED result, not a pre-judgement. Spans 100/250 do NOT exist -> NEW-GATE, ask owner. |

## Table B - combination results

| close_mitigation | break_pct_max | age_bars_max | tail_n | fires | holdout n | full n | exit | Sharpe | gates | failing | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| False | none | none | 10 | 352 | 147 | 352 | breakeven_plus_trail | 0.473 | 5/6 | pooled_sharpe | FAIL |
| False | none | none | 20 | 352 | 147 | 352 | breakeven_plus_trail | 0.473 | 5/6 | pooled_sharpe | FAIL |
| True | none | none | 10 | 351 | 146 | 351 | breakeven_plus_trail | 0.476 | 5/6 | pooled_sharpe | FAIL |
| True | none | none | 20 | 351 | 146 | 351 | breakeven_plus_trail | 0.476 | 5/6 | pooled_sharpe | FAIL |
| False | none | none | 5 | 305 | 121 | 305 | breakeven_plus_trail | 0.558 | 5/6 | pooled_sharpe | FAIL |
| False | none | none | 3 | 207 | 83 | 207 | breakeven_plus_trail | 0.395 | 5/6 | pooled_sharpe | FAIL |
| True | none | none | 3 | 202 | 81 | 202 | breakeven_plus_trail | 0.399 | 5/6 | pooled_sharpe | FAIL |
| False | none | 180 | 3 | 109 | 34 | 109 | breakeven_plus_trail | 0.563 | 5/6 | pooled_sharpe | FAIL |
| False | none | 180 | 5 | 109 | 34 | 109 | breakeven_plus_trail | 0.563 | 5/6 | pooled_sharpe | FAIL |
| False | none | 180 | 10 | 109 | 34 | 109 | breakeven_plus_trail | 0.563 | 5/6 | pooled_sharpe | FAIL |
| False | none | 180 | 20 | 109 | 34 | 109 | breakeven_plus_trail | 0.563 | 5/6 | pooled_sharpe | FAIL |
| True | none | none | 5 | 298 | 115 | 298 | breakeven_plus_trail | 0.617 | 4/6 | pooled_sharpe, psr | FAIL |
| False | none | 250 | 5 | 149 | 48 | 149 | breakeven_plus_trail | 0.266 | 4/6 | pooled_sharpe, sortino | FAIL |
| False | none | 250 | 10 | 149 | 48 | 149 | breakeven_plus_trail | 0.266 | 4/6 | pooled_sharpe, sortino | FAIL |
| False | none | 250 | 20 | 149 | 48 | 149 | breakeven_plus_trail | 0.266 | 4/6 | pooled_sharpe, sortino | FAIL |
| True | none | 250 | 5 | 148 | 46 | 148 | breakeven_plus_trail | 0.271 | 4/6 | pooled_sharpe, sortino | FAIL |
| True | none | 250 | 10 | 148 | 46 | 148 | breakeven_plus_trail | 0.271 | 4/6 | pooled_sharpe, sortino | FAIL |
| True | none | 250 | 20 | 148 | 46 | 148 | breakeven_plus_trail | 0.271 | 4/6 | pooled_sharpe, sortino | FAIL |
| False | none | 250 | 3 | 141 | 47 | 141 | breakeven_plus_trail | 0.230 | 4/6 | pooled_sharpe, sortino | FAIL |
| True | none | 250 | 3 | 139 | 45 | 139 | breakeven_plus_trail | 0.235 | 4/6 | pooled_sharpe, sortino | FAIL |
| True | none | 180 | 3 | 108 | 32 | 108 | breakeven_plus_trail | 0.577 | 4/6 | pooled_sharpe, psr | FAIL |
| True | none | 180 | 5 | 108 | 32 | 108 | breakeven_plus_trail | 0.577 | 4/6 | pooled_sharpe, psr | FAIL |
| True | none | 180 | 10 | 108 | 32 | 108 | breakeven_plus_trail | 0.577 | 4/6 | pooled_sharpe, psr | FAIL |
| True | none | 180 | 20 | 108 | 32 | 108 | breakeven_plus_trail | 0.577 | 4/6 | pooled_sharpe, psr | FAIL |
| False | none | 120 | 3 | 59 | 20 | 59 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| False | none | 120 | 5 | 59 | 20 | 59 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| False | none | 120 | 10 | 59 | 20 | 59 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| False | none | 120 | 20 | 59 | 20 | 59 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| True | none | 120 | 3 | 57 | 18 | 57 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| True | none | 120 | 5 | 57 | 18 | 57 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| True | none | 120 | 10 | 57 | 18 | 57 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| True | none | 120 | 20 | 57 | 18 | 57 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| False | 0.050 | none | 10 | 44 | 14 | 44 | mfe_lockin_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| False | 0.050 | none | 20 | 44 | 14 | 44 | mfe_lockin_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| True | 0.050 | none | 10 | 42 | 12 | 42 | ma_exit_ema9 | none | -/6 | - | BELOW_POWER_FLOOR |
| True | 0.050 | none | 20 | 42 | 12 | 42 | ma_exit_ema9 | none | -/6 | - | BELOW_POWER_FLOOR |
| False | 0.050 | none | 5 | 41 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | none | 5 | 39 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | none | 3 | 35 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | none | 3 | 32 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 250 | 5 | 30 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 250 | 10 | 30 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 250 | 20 | 30 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | none | 10 | 29 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | none | 20 | 29 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 250 | 5 | 28 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 250 | 10 | 28 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 250 | 20 | 28 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 250 | 3 | 28 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | none | 10 | 27 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | none | 20 | 27 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | none | 5 | 27 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 250 | 3 | 26 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | none | 5 | 25 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 180 | 3 | 23 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 180 | 5 | 23 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 180 | 10 | 23 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 180 | 20 | 23 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 180 | 3 | 21 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 180 | 5 | 21 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 180 | 10 | 21 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 180 | 20 | 21 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | none | 3 | 21 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | none | 3 | 18 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | none | 10 | 18 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | none | 20 | 18 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 250 | 5 | 18 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 250 | 10 | 18 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 250 | 20 | 18 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | none | 5 | 17 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 250 | 5 | 16 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 250 | 10 | 16 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 250 | 20 | 16 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 250 | 3 | 16 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | none | 10 | 15 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | none | 20 | 15 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 120 | 3 | 15 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 120 | 5 | 15 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 120 | 10 | 15 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 120 | 20 | 15 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | none | 5 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 250 | 3 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 60 | 3 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 60 | 5 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 60 | 10 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | none | 60 | 20 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 180 | 3 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 180 | 5 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 180 | 10 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 180 | 20 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 60 | 3 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 60 | 5 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 60 | 10 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | none | 60 | 20 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 120 | 3 | 13 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 120 | 5 | 13 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 120 | 10 | 13 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 120 | 20 | 13 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | none | 3 | 13 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 180 | 3 | 12 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 180 | 5 | 12 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 180 | 10 | 12 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 180 | 20 | 12 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | none | 3 | 10 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | none | 5 | 10 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | none | 10 | 10 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | none | 20 | 10 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 250 | 5 | 10 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 250 | 10 | 10 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 250 | 20 | 10 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 120 | 3 | 10 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 120 | 5 | 10 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 120 | 10 | 10 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 120 | 20 | 10 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | none | 5 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | none | 10 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | none | 20 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 250 | 5 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 250 | 10 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 250 | 20 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 120 | 3 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 120 | 5 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 120 | 10 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 120 | 20 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 60 | 3 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 60 | 5 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 60 | 10 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.050 | 60 | 20 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | none | 3 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 180 | 3 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 180 | 5 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 180 | 10 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 180 | 20 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 250 | 3 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 60 | 3 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 60 | 5 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 60 | 10 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.050 | 60 | 20 | 8 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 250 | 5 | 7 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 250 | 10 | 7 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 250 | 20 | 7 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 120 | 3 | 7 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 120 | 5 | 7 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 120 | 10 | 7 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 120 | 20 | 7 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | none | 3 | 6 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 180 | 3 | 6 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 180 | 5 | 6 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 180 | 10 | 6 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 180 | 20 | 6 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 250 | 3 | 6 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 250 | 5 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 250 | 10 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 250 | 20 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 120 | 3 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 120 | 5 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 120 | 10 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 120 | 20 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 60 | 3 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 60 | 5 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 60 | 10 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.030 | 60 | 20 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 120 | 3 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 120 | 5 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 120 | 10 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 120 | 20 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 180 | 3 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 180 | 5 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 180 | 10 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 180 | 20 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 250 | 3 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 60 | 3 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 60 | 5 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 60 | 10 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.030 | 60 | 20 | 5 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 60 | 3 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 60 | 5 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 60 | 10 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 60 | 20 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 120 | 3 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 120 | 5 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 120 | 10 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 120 | 20 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 180 | 3 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 180 | 5 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 180 | 10 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 180 | 20 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.010 | 250 | 3 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 60 | 3 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 60 | 5 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 60 | 10 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 0.020 | 60 | 20 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 60 | 3 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 60 | 5 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 60 | 10 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.010 | 60 | 20 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 60 | 3 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 60 | 5 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 60 | 10 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 0.020 | 60 | 20 | 3 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |

## Verdict (CHECKLIST #182 - denominator required)

**0 of 200 combinations passed, across 3 of 6 applicable producers.**

- graded: 24 | non-gradable: 176
- **FULL FACTORIAL = 4000** (4 (P1) x 2 (P2) x 4 (P3) x 5 (P4) x 5 (P5) x 5 (P6)); combinations run = 200 = **5% of factorial**
- free (subset-safe) subspace = 200 | needs engine resim = 3800
- UNTESTED producers: P1 swing_length, P6 span

*Generated by `scripts/producer_variant_table.py` - regenerate, do not hand-edit.*