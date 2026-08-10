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
| P5 | `break test (close > top)` | `-` | strict | - | - | **N/A** | NO PARAMETER EXISTS. Adding one is NEW-GATE class -> ask owner first. |
| P6 | `compute_ema_sma` | `span` | 200 | 50, 200 | NO - needs engine resim | **UNTESTED** | producer emits ONLY spans 9/21/20/50/200. 100/250 do not exist. |

## Table B - combination results

| close_mitigation | age_bars_max | tail_n | fires | holdout n | full n | exit | Sharpe | gates | failing | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| False | none | 10 | 352 | 147 | 352 | breakeven_plus_trail | 0.473 | 5/6 | pooled_sharpe | FAIL |
| False | none | 20 | 352 | 147 | 352 | breakeven_plus_trail | 0.473 | 5/6 | pooled_sharpe | FAIL |
| True | none | 10 | 351 | 146 | 351 | breakeven_plus_trail | 0.476 | 5/6 | pooled_sharpe | FAIL |
| True | none | 20 | 351 | 146 | 351 | breakeven_plus_trail | 0.476 | 5/6 | pooled_sharpe | FAIL |
| False | none | 5 | 305 | 121 | 305 | breakeven_plus_trail | 0.558 | 5/6 | pooled_sharpe | FAIL |
| False | none | 3 | 207 | 83 | 207 | breakeven_plus_trail | 0.395 | 5/6 | pooled_sharpe | FAIL |
| True | none | 3 | 202 | 81 | 202 | breakeven_plus_trail | 0.399 | 5/6 | pooled_sharpe | FAIL |
| False | 180 | 3 | 109 | 34 | 109 | breakeven_plus_trail | 0.563 | 5/6 | pooled_sharpe | FAIL |
| False | 180 | 5 | 109 | 34 | 109 | breakeven_plus_trail | 0.563 | 5/6 | pooled_sharpe | FAIL |
| False | 180 | 10 | 109 | 34 | 109 | breakeven_plus_trail | 0.563 | 5/6 | pooled_sharpe | FAIL |
| False | 180 | 20 | 109 | 34 | 109 | breakeven_plus_trail | 0.563 | 5/6 | pooled_sharpe | FAIL |
| True | none | 5 | 298 | 115 | 298 | breakeven_plus_trail | 0.617 | 4/6 | pooled_sharpe, psr | FAIL |
| False | 250 | 5 | 149 | 48 | 149 | breakeven_plus_trail | 0.266 | 4/6 | pooled_sharpe, sortino | FAIL |
| False | 250 | 10 | 149 | 48 | 149 | breakeven_plus_trail | 0.266 | 4/6 | pooled_sharpe, sortino | FAIL |
| False | 250 | 20 | 149 | 48 | 149 | breakeven_plus_trail | 0.266 | 4/6 | pooled_sharpe, sortino | FAIL |
| True | 250 | 5 | 148 | 46 | 148 | breakeven_plus_trail | 0.271 | 4/6 | pooled_sharpe, sortino | FAIL |
| True | 250 | 10 | 148 | 46 | 148 | breakeven_plus_trail | 0.271 | 4/6 | pooled_sharpe, sortino | FAIL |
| True | 250 | 20 | 148 | 46 | 148 | breakeven_plus_trail | 0.271 | 4/6 | pooled_sharpe, sortino | FAIL |
| False | 250 | 3 | 141 | 47 | 141 | breakeven_plus_trail | 0.230 | 4/6 | pooled_sharpe, sortino | FAIL |
| True | 250 | 3 | 139 | 45 | 139 | breakeven_plus_trail | 0.235 | 4/6 | pooled_sharpe, sortino | FAIL |
| True | 180 | 3 | 108 | 32 | 108 | breakeven_plus_trail | 0.577 | 4/6 | pooled_sharpe, psr | FAIL |
| True | 180 | 5 | 108 | 32 | 108 | breakeven_plus_trail | 0.577 | 4/6 | pooled_sharpe, psr | FAIL |
| True | 180 | 10 | 108 | 32 | 108 | breakeven_plus_trail | 0.577 | 4/6 | pooled_sharpe, psr | FAIL |
| True | 180 | 20 | 108 | 32 | 108 | breakeven_plus_trail | 0.577 | 4/6 | pooled_sharpe, psr | FAIL |
| False | 120 | 3 | 59 | 20 | 59 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| False | 120 | 5 | 59 | 20 | 59 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| False | 120 | 10 | 59 | 20 | 59 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| False | 120 | 20 | 59 | 20 | 59 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| True | 120 | 3 | 57 | 18 | 57 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| True | 120 | 5 | 57 | 18 | 57 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| True | 120 | 10 | 57 | 18 | 57 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| True | 120 | 20 | 57 | 18 | 57 | breakeven_plus_trail | none | -/6 | - | BELOW_POWER_FLOOR |
| True | 60 | 3 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 5 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 10 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| True | 60 | 20 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 3 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 5 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 10 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |
| False | 60 | 20 | 14 | none | none | - | none | -/6 | - | NO_EXIT_SELECTABLE |

## Verdict (CHECKLIST #182 - denominator required)

**0 of 40 combinations passed, across 3 of 5 applicable producers.**

- graded: 24 | non-gradable: 16
- UNTESTED producers: P1 swing_length, P6 span

*Generated by `scripts/producer_variant_table.py` - regenerate, do not hand-edit.*