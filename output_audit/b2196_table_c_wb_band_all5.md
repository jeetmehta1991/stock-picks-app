# W-B BAND COMPLETE - 5-arm Table C (B2196; S6-B2173a disposition)

All five swing_length bands of smc_breaker_block_long's W-B axis, run END TO END
locally by the autonomous chain (owner directive 2026-08-25): sw20+sw30 landed
pre-chain; sw50 (resumed), sw10 and sw5 landed unattended via run_serial_chain.py
with the post-config battery auto-run per landing. Sources: the five
*_grid_auto.json artifacts named per row; noise floor 0.333 per B2009.

_`starved-IS` = no exit cleared min_n IN-SAMPLE, a SAMPLE-SIZE fact rather than a quality verdict. `graded` = reached `evaluate()` and produced a Sharpe. `distinct` = graded outcomes after equivalence-class collapse (L473). `bands` = distinct parameter VALUES exercised. `ci_lo` = the LOWER bound of the Sharpe confidence interval, which is what `best` ranks on - a higher Sharpe can carry a NEGATIVE lower bound (L455)._

| config | combos | starved-IS | no-Sharpe | graded | distinct | bands | P1-P6 bands tested | median IS-Sharpe | best IS-Sharpe | best IS-CI-lo | best combination |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `b2190_sw5` | 300 | 40 | 0 | 250 | 132 | 18 | P1=5(fixed); P2=False,True; P3=1,2,3,5,10,20; P4=60,120,180,250,None; P5=0.01,0.02,0.03,0.05,None; P6=200(fixed) | 0.389 | 0.625 | 0.123 | cm=True brk=0.020 age=120 tail=5 / earnings_blackout |
| `b2190_sw10` | 300 | 45 | 0 | 245 | 133 | 18 | P1=10(fixed); P2=False,True; P3=1,2,3,5,10,20; P4=60,120,180,250,None; P5=0.01,0.02,0.03,0.05,None; P6=200(fixed) | 0.46 | 0.746 | -0.091 | cm=False brk=0.020 age=none tail=10 / fixed_4r_2r |
| `b2174_sw20` | 300 | 82 | 0 | 218 | 89 | 18 | P1=20(fixed); P2=False,True; P3=1,2,3,5,10,20; P4=60,120,180,250,None; P5=0.01,0.02,0.03,0.05,None; P6=200(fixed) | 0.204 | 0.282 | -0.196 | cm=False brk=none age=250 tail=20 / hybrid_50pct_target |
| `b2183_sw30` | 300 | 106 | 0 | 184 | 61 | 18 | P1=30(fixed); P2=False,True; P3=1,2,3,5,10,20; P4=60,120,180,250,None; P5=0.01,0.02,0.03,0.05,None; P6=200(fixed) | 0.565 | 2.757 | 0.362 | cm=False brk=0.020 age=120 tail=20 / time_stop_20d |
| `b2177_sw50` | 300 | 225 | 0 | 75 | 29 | 18 | P1=50(fixed); P2=False,True; P3=1,2,3,5,10,20; P4=60,120,180,250,None; P5=0.01,0.02,0.03,0.05,None; P6=200(fixed) | 0.697 | 0.889 | -0.508 | cm=True brk=none age=none tail=3 / chandelier_3x |

**Parameters tested** - distinct values each config exercised per axis, read from the result rows themselves. `1 value` = the axis was PINNED and contributed no search; an axis absent from the artifact reads `not recorded`, never `1`. **P1 `swing_length` and P6 `span` are the CROSS-CONFIG axes** - they define which config a cube IS and are held FIXED within it, so they show a value rather than a count. Recorded in the artifact since B2138; anything graded before that reads `not recorded`, which is what let a swing-10 cube be re-graded as swing-20 (S6-B2136).

| config | P1 swing_length | P2 close_mitigation | P3 tail_n | P4 age_bars_max | P5 break_pct_max | P6 span |
|---|---|---|---|---|---|---|
| `b2190_sw5` | FIXED at 5 | 2: False,True | 6: 1,2,3,5,10,20 | 5: 60,120,180,250,None | 5: 0.01,0.02,0.03,0.05,None | FIXED at 200 |
| `b2190_sw10` | FIXED at 10 | 2: False,True | 6: 1,2,3,5,10,20 | 5: 60,120,180,250,None | 5: 0.01,0.02,0.03,0.05,None | FIXED at 200 |
| `b2174_sw20` | FIXED at 20 | 2: False,True | 6: 1,2,3,5,10,20 | 5: 60,120,180,250,None | 5: 0.01,0.02,0.03,0.05,None | FIXED at 200 |
| `b2183_sw30` | FIXED at 30 | 2: False,True | 6: 1,2,3,5,10,20 | 5: 60,120,180,250,None | 5: 0.01,0.02,0.03,0.05,None | FIXED at 200 |
| `b2177_sw50` | FIXED at 50 | 2: False,True | 6: 1,2,3,5,10,20 | 5: 60,120,180,250,None | 5: 0.01,0.02,0.03,0.05,None | FIXED at 200 |


## BAND VERDICT vs the 0.333 noise floor (B2009)

**1 of 5 arms produced a best cell above the selection-noise floor** (denominator:
5 arms x 300 combinations each, graded per-arm as the funnel rows show):

| arm | best IS-CI-lo | vs floor 0.333 | caveat |
|---|---|---|---|
| sw30 | **+0.362** | **ABOVE** | 11 fires - under the admission power floor; a thin cell |
| sw5 | +0.123 | below | - |
| sw10 | -0.091 | below | - |
| sw20 | -0.196 | below | - |
| sw50 | -0.508 | below | - |

The band shape is non-monotone with a peak at swing 30. The single above-floor
cell carries 11 fires, so it cannot clear Step-2 admission gates as-is (holdout
n>=25 required); it is a CANDIDATE for the owner's Step-2 decision, not a
validated edge - and it is the maximum of ~1,500 graded combinations across the
band, so winner's-curse discounting applies (L455/L636 discipline).

## S6-B2173a DISPOSITION

The W-B (swing_length) band for smc_breaker_block_long is COMPLETE: 5 of 5 arms
run, graded, battery-verified, and committed - sw20+sw30 pre-chain, sw50/sw10/sw5
landed UNATTENDED by the autonomous chain (serial_chain.log: CHAIN DONE
06:30:08Z). This document is the end-to-end local evidence the owner named as the
venue-decision precondition (ruling 4, 2026-08-25): the workflow ran a full
multi-config program locally with zero mid-run prompting - launch, cap-respecting
legs, battery, grading, chain advancement, hourly reporting all mechanical.
