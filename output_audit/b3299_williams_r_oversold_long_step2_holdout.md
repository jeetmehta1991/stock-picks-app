# STEP-2 HOLDOUT READ - williams_r_oversold

owner ruling 2026-09-08 - all cells x exits, one read; pre-registered cell carries admission. Window 2025-05-05 .. 2026-05-05; 468 (cell, exit) lines, 468 graded.

**ADMISSION-BEARING CELL VERDICT: FAIL**

Pre-registered: levels [-90.0, 3.0, 0.05], exit time_stop_10d, holdout n 125, full n 392, holdout sharpe 0.639, PF 1.402, sortino 0.869, PSR 0.9204.
Gates: pooled_sharpe=FAIL, profit_factor=PASS, sortino=FAIL, psr=FAIL, min_trades_holdout=PASS, min_trades_full_period=PASS.

| rank | levels | exit | HO n | HO sharpe | PF | sortino | PSR | gates | verdict | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [-90.0, 3.0, 0.02] | reverse_signal | 153 | 1.121 | 2.142 | 0.892 | 0.9973 | 5/6 | FAIL | peeked |
| 2 | [-85.0, 3.0, 0.02] | reverse_signal | 221 | 1.088 | 2.093 | 0.882 | 0.9995 | 5/6 | FAIL | peeked |
| 3 | [-85.0, 3.0, 0.0] | reverse_signal | 252 | 1.034 | 2.03 | 0.836 | 0.9996 | 5/6 | FAIL | peeked |
| 4 | [-90.0, 3.0, 0.0] | reverse_signal | 169 | 0.968 | 1.962 | 0.769 | 0.996 | 4/6 | FAIL | peeked |
| 5 | [-90.0, 3.0, 0.05] | reverse_signal | 125 | 0.940 | 1.954 | 0.754 | 0.9866 | 4/6 | FAIL | peeked |
| 6 | [-85.0, 3.0, 0.05] | reverse_signal | 172 | 0.924 | 1.929 | 0.736 | 0.9945 | 4/6 | FAIL | peeked |
| 7 | [-90.0, 3.0, 0.02] | time_stop_10d | 153 | 0.888 | 1.591 | 1.133 | 0.9834 | 5/6 | FAIL | peeked |
| 8 | [-90.0, 3.0, 0.0] | next_pivot_target | 169 | 0.871 | 1.669 | 1.638 | 0.9897 | 5/6 | FAIL | peeked |
| 9 | [-90.0, 3.0, 0.02] | next_pivot_target | 153 | 0.825 | 1.636 | 1.518 | 0.9834 | 5/6 | FAIL | peeked |
| 10 | [-85.0, 3.0, 0.02] | breakeven_plus_trail | 221 | 0.807 | 2.881 | 3.765 | 1.0 | 5/6 | FAIL | peeked |
| 11 | [-85.0, 5.0, 0.02] | reverse_signal | 279 | 0.806 | 1.735 | 0.67 | 0.9982 | 4/6 | FAIL | peeked |
| 12 | [-90.0, 3.0, 0.02] | regime_flip | 153 | 0.795 | 1.835 | 1.019 | 0.9965 | 5/6 | FAIL | peeked |
| 13 | [-90.0, 3.0, 0.02] | time_stop_20d | 153 | 0.795 | 1.835 | 1.019 | 0.9965 | 5/6 | FAIL | peeked |
| 14 | [-85.0, 3.0, 0.0] | next_pivot_target | 252 | 0.793 | 1.599 | 1.465 | 0.9953 | 5/6 | FAIL | peeked |
| 15 | [-85.0, 3.0, 0.02] | time_stop_10d | 221 | 0.788 | 1.509 | 0.994 | 0.9884 | 4/6 | FAIL | peeked |
| 16 | [-85.0, 5.0, 0.0] | reverse_signal | 315 | 0.783 | 1.713 | 0.651 | 0.9988 | 4/6 | FAIL | peeked |
| 17 | [-90.0, 5.0, 0.02] | reverse_signal | 219 | 0.783 | 1.712 | 0.638 | 0.9939 | 4/6 | FAIL | peeked |
| 18 | [-85.0, 3.0, 0.02] | class_time_stop | 221 | 0.779 | 2.031 | 1.291 | 1.0 | 5/6 | FAIL | peeked |
| 19 | [-85.0, 3.0, 0.0] | breakeven_plus_trail | 252 | 0.760 | 2.73 | 3.167 | 1.0 | 5/6 | FAIL | peeked |
| 20 | [-85.0, 5.0, 0.02] | breakeven_plus_trail | 279 | 0.748 | 2.71 | 3.592 | 1.0 | 5/6 | FAIL | peeked |
