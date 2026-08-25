_`starved-IS` = no exit cleared min_n IN-SAMPLE, a SAMPLE-SIZE fact rather than a quality verdict. `graded` = reached `evaluate()` and produced a Sharpe. `distinct` = graded outcomes after equivalence-class collapse (L473). `bands` = distinct parameter VALUES exercised. `ci_lo` = the LOWER bound of the Sharpe confidence interval, which is what `best` ranks on - a higher Sharpe can carry a NEGATIVE lower bound (L455)._

| config | combos | starved-IS | no-Sharpe | graded | distinct | bands | P1-P6 bands tested | best IS-Sharpe | best IS-CI-lo | best combination |
|---|---|---|---|---|---|---|---|---|---|---|
| `cfg1` | 300 | 181 | 0 | 119 | 60 | 18 | P1=20(fixed); P2=False,True; P3=1,2,3,5,10,20; P4=60,120,180,250,None; P5=0.01,0.02,0.03,0.05,None; P6=200(fixed) | 0.51 | 0.129 | cm=True brk=none age=none tail=20 / breakeven_plus_trail |
| `cfg2` | 300 | 97 | 0 | 198 | 93 | 18 | P1=10(fixed); P2=False,True; P3=1,2,3,5,10,20; P4=60,120,180,250,None; P5=0.01,0.02,0.03,0.05,None; P6=50(fixed) | 0.617 | 0.094 | cm=False brk=none age=180 tail=2 / hybrid_50pct_target |
| `w1_span21` | 300 | 176 | 0 | 124 | 60 | 18 | P1=20(fixed); P2=False,True; P3=1,2,3,5,10,20; P4=60,120,180,250,None; P5=0.01,0.02,0.03,0.05,None; P6=21(fixed) | 0.764 | -0.14 | cm=False brk=none age=none tail=20 / r_multiple_2r |
| `w1_span50` | 300 | 179 | 0 | 121 | 59 | 18 | P1=20(fixed); P2=False,True; P3=1,2,3,5,10,20; P4=60,120,180,250,None; P5=0.01,0.02,0.03,0.05,None; P6=50(fixed) | 1.307 | 0.259 | cm=False brk=none age=none tail=5 / r_multiple_2r |
| `b2174_sw20` | 300 | 82 | 218 | 0 | 89 | 18 | P1=20(fixed); P2=False,True; P3=1,2,3,5,10,20; P4=60,120,180,250,None; P5=0.01,0.02,0.03,0.05,None; P6=200(fixed) | 0.282 | -0.196 | cm=False brk=none age=250 tail=20 / hybrid_50pct_target |

**Parameters tested** - distinct values each config exercised per axis, read from the result rows themselves. `1 value` = the axis was PINNED and contributed no search; an axis absent from the artifact reads `not recorded`, never `1`. **P1 `swing_length` and P6 `span` are the CROSS-CONFIG axes** - they define which config a cube IS and are held FIXED within it, so they show a value rather than a count. Recorded in the artifact since B2138; anything graded before that reads `not recorded`, which is what let a swing-10 cube be re-graded as swing-20 (S6-B2136).

| config | P1 swing_length | P2 close_mitigation | P3 tail_n | P4 age_bars_max | P5 break_pct_max | P6 span |
|---|---|---|---|---|---|---|
| `cfg1` | FIXED at 20 | 2: False,True | 6: 1,2,3,5,10,20 | 5: 60,120,180,250,None | 5: 0.01,0.02,0.03,0.05,None | FIXED at 200 |
| `cfg2` | FIXED at 10 | 2: False,True | 6: 1,2,3,5,10,20 | 5: 60,120,180,250,None | 5: 0.01,0.02,0.03,0.05,None | FIXED at 50 |
| `w1_span21` | FIXED at 20 | 2: False,True | 6: 1,2,3,5,10,20 | 5: 60,120,180,250,None | 5: 0.01,0.02,0.03,0.05,None | FIXED at 21 |
| `w1_span50` | FIXED at 20 | 2: False,True | 6: 1,2,3,5,10,20 | 5: 60,120,180,250,None | 5: 0.01,0.02,0.03,0.05,None | FIXED at 50 |
| `b2174_sw20` | FIXED at 20 | 2: False,True | 6: 1,2,3,5,10,20 | 5: 60,120,180,250,None | 5: 0.01,0.02,0.03,0.05,None | FIXED at 200 |
