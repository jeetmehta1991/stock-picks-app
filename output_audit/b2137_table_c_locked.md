_`starved-IS` = no exit cleared min_n IN-SAMPLE, a SAMPLE-SIZE fact rather than a quality verdict. `graded` = reached `evaluate()` and produced a Sharpe. `distinct` = graded outcomes after equivalence-class collapse (L473). `bands` = distinct parameter VALUES exercised. `ci_lo` = the LOWER bound of the Sharpe confidence interval, which is what `best` ranks on - a higher Sharpe can carry a NEGATIVE lower bound (L455)._

| config | combos | starved-IS | no-Sharpe | graded | distinct | bands | best IS-Sharpe | best IS-CI-lo | best combination |
|---|---|---|---|---|---|---|---|---|---|
| `cfg1` | 300 | 181 | 0 | 119 | 60 | 18 | 0.51 | 0.129 | cm=True brk=none age=none tail=20 / breakeven_plus_trail |
| `cfg2` | 300 | 97 | 0 | 198 | 93 | 18 | 0.617 | 0.094 | cm=False brk=none age=180 tail=2 / hybrid_50pct_target |
| `w1_span21` | 300 | 176 | 0 | 124 | 60 | 18 | 0.764 | -0.14 | cm=False brk=none age=none tail=20 / r_multiple_2r |
| `w1_span50` | 300 | 179 | 0 | 121 | 59 | 18 | 1.307 | 0.259 | cm=False brk=none age=none tail=5 / r_multiple_2r |

**Parameters tested** - distinct values each config exercised per axis, read from the result rows themselves. `1 value` = the axis was PINNED and contributed no search; an axis absent from the artifact reads `not recorded`, never `1`. **P1 `swing_length` and P6 `span` are the CROSS-CONFIG axes** - they define which config a cube IS, are held fixed within it, and are NOT written into the grid artifact (S6-B2136: the grader defaults swing_length to 20, so a cube run at 10 re-grades wrong unless the value is recovered from the run log).

| config | P1 swing_length | P2 close_mitigation | P3 tail_n | P4 age_bars_max | P5 break_pct_max | P6 span |
|---|---|---|---|---|---|---|
| `cfg1` | not recorded | 2: False, True | 6: 1, 2, 3, 5, 10, 20 | 5: 60, 120, 180, 250, None | 5: 0.01, 0.02, 0.03, 0.05, None | not recorded |
| `cfg2` | not recorded | 2: False, True | 6: 1, 2, 3, 5, 10, 20 | 5: 60, 120, 180, 250, None | 5: 0.01, 0.02, 0.03, 0.05, None | not recorded |
| `w1_span21` | not recorded | 2: False, True | 6: 1, 2, 3, 5, 10, 20 | 5: 60, 120, 180, 250, None | 5: 0.01, 0.02, 0.03, 0.05, None | not recorded |
| `w1_span50` | not recorded | 2: False, True | 6: 1, 2, 3, 5, 10, 20 | 5: 60, 120, 180, 250, None | 5: 0.01, 0.02, 0.03, 0.05, None | not recorded |
