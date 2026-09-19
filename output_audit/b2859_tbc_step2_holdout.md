# STEP-2 HOLDOUT READ - three_black_crows_short

owner ruling 2026-09-08 - all cells x exits, one read; pre-registered cell carries admission. Window 2025-05-05 .. 2026-05-05; 130 (cell, exit) lines, 130 graded.

**ADMISSION-BEARING CELL VERDICT: FAIL**

Pre-registered: levels [40.0], exit breakeven_plus_trail, holdout n 470, full n 1674, holdout sharpe -0.118, PF 0.896, sortino -0.357, PSR 0.241.
Gates: pooled_sharpe=FAIL, profit_factor=FAIL, sortino=FAIL, psr=FAIL, min_trades_holdout=PASS, min_trades_full_period=PASS.

| rank | levels | exit | HO n | HO sharpe | PF | sortino | PSR | gates | verdict | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [58.812] | ma_exit_ema9 | 101 | 0.015 | 1.006 | 0.038 | 0.507 | 2/6 | FAIL | peeked |
| 2 | [50.132] | breakeven_plus_trail | 287 | -0.075 | 0.935 | -0.19 | 0.3598 | 2/6 | FAIL | peeked |
| 3 | [45.094] | breakeven_plus_trail | 386 | -0.084 | 0.926 | -0.243 | 0.3225 | 2/6 | FAIL | peeked |
| 4 | [58.812] | breakeven_plus_trail | 101 | -0.110 | 0.904 | -0.368 | 0.3773 | 2/6 | FAIL | peeked |
| 5 | [40.0] | breakeven_plus_trail | 470 | -0.118 | 0.896 | -0.357 | 0.241 | 2/6 | FAIL | **ADMISSION** |
| 6 | [54.066] | breakeven_plus_trail | 187 | -0.120 | 0.898 | -0.299 | 0.3233 | 2/6 | FAIL | peeked |
| 7 | [58.812] | earnings_blackout | 101 | -0.351 | 0.617 | -0.312 | 0.0306 | 2/6 | FAIL | peeked |
| 8 | [50.132] | earnings_blackout | 287 | -0.352 | 0.606 | -0.299 | 0.0005 | 2/6 | FAIL | peeked |
| 9 | [54.066] | ma_exit_ema9 | 187 | -0.391 | 0.846 | -0.795 | 0.2627 | 2/6 | FAIL | peeked |
| 10 | [54.066] | earnings_blackout | 187 | -0.431 | 0.522 | -0.357 | 0.0002 | 2/6 | FAIL | peeked |
| 11 | [54.066] | time_stop_10d | 187 | -0.444 | 0.788 | -0.477 | 0.1093 | 2/6 | FAIL | peeked |
| 12 | [50.132] | hybrid_50pct_target | 287 | -0.451 | 0.665 | -1.808 | 0.0014 | 2/6 | FAIL | peeked |
| 13 | [45.094] | earnings_blackout | 386 | -0.454 | 0.536 | -0.411 | 0.0 | 2/6 | FAIL | peeked |
| 14 | [54.066] | hybrid_50pct_target | 187 | -0.502 | 0.631 | -2.039 | 0.0037 | 2/6 | FAIL | peeked |
| 15 | [50.132] | ma_exit_ema9 | 287 | -0.509 | 0.793 | -1.037 | 0.1549 | 2/6 | FAIL | peeked |
| 16 | [40.0] | earnings_blackout | 470 | -0.511 | 0.499 | -0.475 | 0.0 | 2/6 | FAIL | peeked |
| 17 | [58.812] | hybrid_50pct_target | 101 | -0.526 | 0.616 | -2.302 | 0.0204 | 2/6 | FAIL | peeked |
| 18 | [45.094] | hybrid_50pct_target | 386 | -0.537 | 0.623 | -2.229 | 0.0 | 2/6 | FAIL | peeked |
| 19 | [50.132] | trailing_15pct | 287 | -0.554 | 0.533 | -1.151 | 0.0 | 2/6 | FAIL | peeked |
| 20 | [58.812] | trailing_10pct | 101 | -0.560 | 0.585 | -1.065 | 0.0349 | 2/6 | FAIL | peeked |
