# STEP-2 HOLDOUT READ - squeeze_breakout

owner ruling 2026-09-08 - all cells x exits, one read; pre-registered cell carries admission. Window 2025-05-05 .. 2026-05-05; 104 (cell, exit) lines, 104 graded.

**ADMISSION-BEARING CELL VERDICT: FAIL**

Pre-registered: levels [2.5, 2.0], exit class_time_stop, holdout n 86, full n 578, holdout sharpe -0.154, PF 0.87, sortino -0.185, PSR 0.3346.
Gates: pooled_sharpe=FAIL, profit_factor=FAIL, sortino=FAIL, psr=FAIL, min_trades_holdout=PASS, min_trades_full_period=PASS.

| rank | levels | exit | HO n | HO sharpe | PF | sortino | PSR | gates | verdict | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [2.5, 1.5] | next_pivot_target | 77 | 0.306 | 1.177 | 0.737 | 0.6956 | 2/6 | FAIL | peeked |
| 2 | [2.0, 2.0] | breakeven_plus_trail | 188 | 0.300 | 1.487 | 1.294 | 0.943 | 4/6 | FAIL | peeked |
| 3 | [2.5, 2.0] | next_pivot_target | 86 | 0.250 | 1.153 | 0.574 | 0.6762 | 2/6 | FAIL | peeked |
| 4 | [2.0, 2.0] | earnings_blackout | 188 | 0.225 | 1.349 | 0.347 | 0.929 | 3/6 | FAIL | peeked |
| 5 | [2.0, 2.0] | hybrid_50pct_target | 188 | 0.220 | 1.227 | 0.777 | 0.8909 | 2/6 | FAIL | peeked |
| 6 | [2.0, 1.5] | next_pivot_target | 79 | 0.217 | 1.122 | 0.526 | 0.6419 | 2/6 | FAIL | peeked |
| 7 | [2.0, 1.5] | breakeven_plus_trail | 79 | 0.205 | 1.269 | 0.737 | 0.7198 | 2/6 | FAIL | peeked |
| 8 | [2.5, 1.5] | breakeven_plus_trail | 77 | 0.192 | 1.258 | 0.693 | 0.7042 | 2/6 | FAIL | peeked |
| 9 | [2.5, 2.0] | breakeven_plus_trail | 86 | 0.173 | 1.225 | 0.577 | 0.6926 | 2/6 | FAIL | peeked |
| 10 | [2.0, 1.5] | trailing_15pct | 79 | 0.152 | 1.229 | 0.515 | 0.7339 | 2/6 | FAIL | peeked |
| 11 | [2.0, 2.0] | trailing_15pct | 188 | 0.144 | 1.232 | 0.459 | 0.8422 | 2/6 | FAIL | peeked |
| 12 | [2.5, 1.5] | trailing_15pct | 77 | 0.099 | 1.145 | 0.335 | 0.6522 | 2/6 | FAIL | peeked |
| 13 | [2.0, 1.5] | hybrid_50pct_target | 79 | 0.084 | 1.072 | 0.288 | 0.6055 | 2/6 | FAIL | peeked |
| 14 | [2.5, 2.0] | trailing_15pct | 86 | 0.073 | 1.108 | 0.228 | 0.6198 | 2/6 | FAIL | peeked |
| 15 | [2.5, 2.0] | hybrid_50pct_target | 86 | 0.070 | 1.061 | 0.216 | 0.5938 | 2/6 | FAIL | peeked |
| 16 | [2.5, 1.5] | hybrid_50pct_target | 77 | 0.067 | 1.058 | 0.226 | 0.5836 | 2/6 | FAIL | peeked |
| 17 | [2.0, 2.0] | class_time_stop | 188 | 0.054 | 1.055 | 0.087 | 0.5919 | 2/6 | FAIL | peeked |
| 18 | [2.0, 2.0] | ma_exit_ema9 | 188 | 0.048 | 1.04 | 0.177 | 0.5396 | 2/6 | FAIL | peeked |
| 19 | [2.0, 1.5] | earnings_blackout | 79 | 0.019 | 1.025 | 0.026 | 0.5295 | 2/6 | FAIL | peeked |
| 20 | [2.0, 2.0] | r_multiple_2r | 188 | -0.001 | 1.0 | -0.002 | 0.4995 | 2/6 | FAIL | peeked |
