# Table A - squeeze_breakout

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build adafdd452 | commit adafdd452 at 2026-10-25 20:32:52 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** NONE | **family:** breakout | **status:** IN-CAMPAIGN | **R5 fires:** 1141 (closed fires in the exit cube: 1141 of 1141, S6-B3258) | **surviving fires (T1):** 1141 (unchanged since R5 - filter is identity)

**SPECS entry:** registered in producer_variant_table

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  squeeze_fire_up  <- backtest/signals/technical.py
       DEFN: NOT in a squeeze (BB(20, 2.0) not inside KC(20, 2.0 x ATR20)) AND close-minus-20-bar-midpoint momentum crosses above zero (technical.py compute_squeeze) - no prior squeeze is required (S6-B3254)
       knobs P1.1-P1.5 (band rows in Table A)

============================== STRATEGY LAYER ==============================


Gate body, VERBATIM from backtest/signals/screener.py strat_squeeze_breakout (docstring and return dropped):

```python
fires = s.get('squeeze_fire_up')
```

## Table A - parameter inventory (canonical shape - READY FOR OWNER BAND REVIEW)

One row per parameter the entry condition touches, BOTH layers, nothing
omitted (L785: an axis left out of Table A is invisible at close).
Every producer row carries its DEFINED BANDS in the P<n>.x rows beneath
it (B2845, owner-corrected: a ready and FINAL Table A per strategy);
the engine-spec (SPECS) entry is built from these before any engine
leg runs.

| id | layer | producer / parameter | what it does | production | band VALUES | free_band (OFFLINE) | resim_band (RESIM) | status |
|---|---|---|---|---|---|---|---|---|
| P1 | PRODUCER | squeeze_fire_up - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | NOT in a squeeze (BB(20, 2.0) not inside KC(20, 2.0 x ATR20)) AND close-minus-20-bar-midpoint momentum crosses above zero (technical.py compute_squeeze) - no prior squeeze is required (S6-B3254) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P1.1 | BAND | squeeze definition: Keltner multiplier (BB inside KC = squeeze) - backtest/signals/technical.py compute_keltner + compute_squeeze | BRACKET production; canon TTM squeeze (Carter 2005) uses 1.5 | 2.0 | 1.5, 2, 2.5 | offline 1 of 3 levels - TIGHTER (2.5) - a wider channel holds more bars in the squeeze; derived from persisted kc_mid / kc_upper and bb_20_20 bands | LOOSER (1.5) - the canon value; adds bars the cube never fired; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P1.2 | BAND | squeeze definition: Bollinger std multiplier - backtest/signals/technical.py compute_bollinger + compute_squeeze | BRACKET production; bb_20_15 is already emitted | 2.0 | 1.5, 2, 2.5 | offline 1 of 3 levels - TIGHTER (1.5) - a narrower band sits inside the channel more often; persisted bb_20_15 bands | LOOSER (2.5) - adds bars the cube never fired; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P1.3 | BAND | momentum window (close vs the N-bar high/low midpoint) - backtest/signals/technical.py compute_squeeze | BRACKET production | 20 | 10, 20, 30 | offline 0 of 3 levels - none - the high/low midpoint at other windows is unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P1.4 | BAND | Keltner EMA / ATR period - backtest/signals/technical.py compute_keltner | BRACKET production (Wilder 14 adjacent) | 20 | 14, 20, 30 | offline 0 of 3 levels - none - the channel at other periods is unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P1.5 | BAND | [NEW-GATE] prior squeeze: in a squeeze on at least one of the last N bars (0 = none required) - backtest/signals/technical.py compute_squeeze | NEW-GATE offered at T3 (S6-B3254); Carter 2005 fires on the first bar OUT of a squeeze, which is N = 1 | 0 | 0, 1, 5, 10 | offline 0 of 4 levels - none - the prior bars' squeeze state is unpersisted | N = 1, 5, 10 - fewer signals, engine-only; the trades are not a subset (a dropped signal stops blocking a later one - L812); DEFINED-NO-ACTUATOR | T3 review before any grid |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (runbook section 3.6; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (module writing the key) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (module writing the key) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/technical.py | 100.0% | 17.6, 21.6, 26.09, 32.11 | 17.6: 913 (80%); 21.6: 685 (60%); 26.09: 457 (40%); 32.11: 229 (20%) | 17.6: 229 (20%); 21.6: 458 (40%); 26.09: 685 (60%); 32.11: 913 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 22.03, 24.46, 26.75, 29.36 | 22.03: 913 (80%); 24.46: 685 (60%); 26.75: 457 (40%); 29.36: 230 (20%) | 22.03: 229 (20%); 24.46: 457 (40%); 26.75: 686 (60%); 29.36: 913 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 18.16, 20.95, 23.47, 27.09 | 18.16: 913 (80%); 20.95: 685 (60%); 23.47: 458 (40%); 27.09: 229 (20%) | 18.16: 229 (20%); 20.95: 457 (40%); 23.47: 687 (60%); 27.09: 913 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -8.8488, -4.3084, -2.0319, -0.5967 | -8.8488: 913 (80%); -4.3084: 685 (60%); -2.0319: 457 (40%); -0.5967: 229 (20%) | -8.8488: 229 (20%); -4.3084: 457 (40%); -2.0319: 685 (60%); -0.5967: 913 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.2097, 2.1538, 3.7404, 6.7347 | 1.2097: 913 (80%); 2.1538: 685 (60%); 3.7404: 457 (40%); 6.7347: 229 (20%) | 1.2097: 229 (20%); 2.1538: 457 (40%); 3.7404: 685 (60%); 6.7347: 913 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.2097, 2.1538, 3.7404, 6.7347 | 1.2097: 913 (80%); 2.1538: 685 (60%); 3.7404: 457 (40%); 6.7347: 229 (20%) | 1.2097: 229 (20%); 2.1538: 457 (40%); 3.7404: 685 (60%); 6.7347: 913 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.422, 3.005, 3.772, 4.573 | 2.422: 913 (80%); 3.005: 685 (60%); 3.772: 457 (40%); 4.573: 229 (20%) | 2.422: 230 (20%); 3.005: 457 (40%); 3.772: 685 (60%); 4.573: 913 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0674, 0.0945, 0.128, 0.1879 | 0.0674: 913 (80%); 0.0945: 685 (60%); 0.128: 457 (40%); 0.1879: 229 (20%) | 0.0674: 230 (20%); 0.0945: 459 (40%); 0.128: 685 (60%); 0.1879: 913 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.4768, 0.6328, 0.812, 0.954 | 0.4768: 913 (80%); 0.6328: 685 (60%); 0.812: 457 (40%); 0.954: 229 (20%) | 0.4768: 229 (20%); 0.6328: 457 (40%); 0.812: 685 (60%); 0.954: 913 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0782, 0.1013, 0.1308, 0.1673 | 0.0782: 913 (80%); 0.1013: 685 (60%); 0.1308: 457 (40%); 0.1673: 230 (20%) | 0.0782: 229 (20%); 0.1013: 457 (40%); 0.1308: 686 (60%); 0.1673: 913 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.444, 0.5516, 0.6381, 0.7505 | 0.444: 913 (80%); 0.5516: 685 (60%); 0.6381: 457 (40%); 0.7505: 229 (20%) | 0.444: 229 (20%); 0.5516: 457 (40%); 0.6381: 685 (60%); 0.7505: 913 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.1042, 0.1351, 0.1743, 0.2231 | 0.1042: 913 (80%); 0.1351: 685 (60%); 0.1743: 457 (40%); 0.2231: 229 (20%) | 0.1042: 229 (20%); 0.1351: 457 (40%); 0.1743: 685 (60%); 0.2231: 913 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.458, 0.5387, 0.6036, 0.6879 | 0.458: 913 (80%); 0.5387: 685 (60%); 0.6036: 457 (40%); 0.6879: 229 (20%) | 0.458: 229 (20%); 0.5387: 457 (40%); 0.6036: 685 (60%); 0.6879: 913 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0387, -0.0088, 0.0075, 0.0279 | -0.0387: 913 (80%); -0.0088: 687 (60%); 0.0075: 522 (46%); 0.0279: 229 (20%) | -0.0387: 229 (20%); -0.0088: 457 (40%); 0.0075: 783 (69%); 0.0279: 914 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1505, 0.162, 0.2016, 0.268 | 0.1505: 911 (80%); 0.162: 649 (57%); 0.2016: 454 (40%); 0.268: 236 (21%) | 0.1505: 230 (20%); 0.162: 492 (43%); 0.2016: 687 (60%); 0.268: 905 (79%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1141 (100%) | 0: 1044 (91%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0773, -0.0097, 0.0491, 0.1122 | -0.0773: 913 (80%); -0.0097: 686 (60%); 0.0491: 457 (40%); 0.1122: 230 (20%) | -0.0773: 229 (20%); -0.0097: 457 (40%); 0.0491: 685 (60%); 0.1122: 913 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 1141 (100%); 1: 365 (32%) | 0: 776 (68%); 1: 968 (85%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2295, -0.1585, -0.1285, -0.1141 | -0.2295: 918 (80%); -0.1585: 686 (60%); -0.1285: 471 (41%); -0.1141: 389 (34%) | -0.2295: 232 (20%); -0.1585: 461 (40%); -0.1285: 713 (62%); -0.1141: 939 (82%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.5128, 0.6731, 0.7564, 0.7692 | 0.5128: 914 (80%); 0.6731: 691 (61%); 0.7564: 492 (43%); 0.7692: 427 (37%) | 0.5128: 233 (20%); 0.6731: 487 (43%); 0.7564: 699 (61%); 0.7692: 914 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2564, 0.3718, 0.5897, 0.7821 | 0.2564: 938 (82%); 0.3718: 685 (60%); 0.5897: 571 (50%); 0.7821: 240 (21%) | 0.2564: 237 (21%); 0.3718: 457 (40%); 0.5897: 758 (66%); 0.7821: 924 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0462, 0.0167, 0.0853, 0.2798 | -0.0462: 915 (80%); 0.0167: 745 (65%); 0.0853: 458 (40%); 0.2798: 229 (20%) | -0.0462: 273 (24%); 0.0167: 583 (51%); 0.0853: 689 (60%); 0.2798: 914 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3846, 0.4872, 0.5897, 0.8782 | 0.3846: 923 (81%); 0.4872: 762 (67%); 0.5897: 490 (43%); 0.8782: 229 (20%) | 0.3846: 237 (21%); 0.4872: 567 (50%); 0.5897: 696 (61%); 0.8782: 914 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1474, 0.3526, 0.4551, 0.5962 | 0.1474: 917 (80%); 0.3526: 731 (64%); 0.4551: 598 (52%); 0.5962: 235 (21%) | 0.1474: 234 (21%); 0.3526: 471 (41%); 0.4551: 755 (66%); 0.5962: 926 (81%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.5101, -0.3562, -0.0869, 0.0029 | -0.5101: 917 (80%); -0.3562: 690 (60%); -0.0869: 483 (42%); 0.0029: 246 (22%) | -0.5101: 230 (20%); -0.3562: 465 (41%); -0.0869: 845 (74%); 0.0029: 938 (82%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3269, 0.5, 0.8013, 0.9038 | 0.3269: 921 (81%); 0.5: 689 (60%); 0.8013: 459 (40%); 0.9038: 230 (20%) | 0.3269: 234 (21%); 0.5: 463 (41%); 0.8013: 686 (60%); 0.9038: 924 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1474, 0.4423, 0.6795, 0.8526 | 0.1474: 922 (81%); 0.4423: 685 (60%); 0.6795: 467 (41%); 0.8526: 350 (31%) | 0.1474: 234 (21%); 0.4423: 474 (42%); 0.6795: 688 (60%); 0.8526: 978 (86%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0681, -0.0521, -0.0254, 0 | -0.0681: 940 (82%); -0.0521: 687 (60%); -0.0254: 459 (40%); 0: 417 (37%) | -0.0681: 229 (20%); -0.0521: 462 (40%); -0.0254: 699 (61%); 0: 1117 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4679, 0.7949, 0.9038, 1 | 0.4679: 919 (81%); 0.7949: 696 (61%); 0.9038: 462 (40%); 1: 367 (32%) | 0.4679: 234 (21%); 0.7949: 462 (40%); 0.9038: 702 (62%); 1: 1141 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.109, 0.3141, 0.3397, 0.7564 | 0.109: 913 (80%); 0.3141: 694 (61%); 0.3397: 459 (40%); 0.7564: 231 (20%) | 0.109: 246 (22%); 0.3141: 490 (43%); 0.3397: 686 (60%); 0.7564: 918 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0092, 0.054, 0.1353, 0.2489 | 0.0092: 942 (83%); 0.054: 686 (60%); 0.1353: 459 (40%); 0.2489: 341 (30%) | 0.0092: 233 (20%); 0.054: 472 (41%); 0.1353: 690 (60%); 0.2489: 987 (87%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.6346, 0.8929, 0.9615, 0.9744 | 0.6346: 913 (80%); 0.8929: 699 (61%); 0.9615: 496 (43%); 0.9744: 409 (36%) | 0.6346: 229 (20%); 0.8929: 462 (40%); 0.9615: 702 (62%); 0.9744: 961 (84%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0897, 0.2949, 0.3739, 0.7727 | 0.0897: 913 (80%); 0.2949: 692 (61%); 0.3739: 459 (40%); 0.7727: 235 (21%) | 0.0897: 232 (20%); 0.2949: 636 (56%); 0.3739: 686 (60%); 0.7727: 919 (81%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.3493, -0.0238, 0.1048, 0.2381 | -0.3493: 1058 (93%); -0.0238: 692 (61%); 0.1048: 457 (40%); 0.2381: 239 (21%) | -0.3493: 270 (24%); -0.0238: 468 (41%); 0.1048: 687 (60%); 0.2381: 914 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.3459, -0.0217, 0.0444, 0.0869 | -0.3459: 1092 (96%); -0.0217: 691 (61%); 0.0444: 465 (41%); 0.0869: 237 (21%) | -0.3459: 236 (21%); -0.0217: 458 (40%); 0.0444: 691 (61%); 0.0869: 915 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2628, 0.5385, 0.7372, 0.859 | 0.2628: 1019 (89%); 0.5385: 685 (60%); 0.7372: 492 (43%); 0.859: 238 (21%) | 0.2628: 309 (27%); 0.5385: 458 (40%); 0.7372: 689 (60%); 0.859: 914 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1474, 0.3846, 0.5641, 0.7436 | 0.1474: 916 (80%); 0.3846: 710 (62%); 0.5641: 575 (50%); 0.7436: 235 (21%) | 0.1474: 251 (22%); 0.3846: 471 (41%); 0.5641: 764 (67%); 0.7436: 916 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0567, 0.1467, 0.3075, 0.65 | 0.0567: 914 (80%); 0.1467: 685 (60%); 0.3075: 458 (40%); 0.65: 231 (20%) | 0.0567: 230 (20%); 0.1467: 461 (40%); 0.3075: 685 (60%); 0.65: 913 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +1 | 98.1% | 28, 63, 89, 157 | 28: 911 (80%); 63: 686 (60%); 89: 451 (40%); 157: 226 (20%) | 28: 225 (20%); 63: 452 (40%); 89: 674 (59%); 157: 896 (79%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 99.6% | 1.6552, 2.19, 2.7719, 3.7993 | 1.6552: 909 (80%); 2.19: 682 (60%); 2.7719: 455 (40%); 3.7993: 228 (20%) | 1.6552: 228 (20%); 2.19: 455 (40%); 2.7719: 682 (60%); 3.7993: 909 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 12, 20, 28, 30 | 12: 945 (83%); 20: 714 (63%); 28: 501 (44%); 30: 249 (22%) | 12: 241 (21%); 20: 462 (40%); 28: 843 (74%); 30: 921 (81%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 1, 2, 3 | 1: 957 (84%); 2: 762 (67%); 3: 412 (36%) | 1: 379 (33%); 2: 729 (64%); 3: 928 (81%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0149, -0.0014, 0.003, 0.0202 | -0.0149: 920 (81%); -0.0014: 687 (60%); 0.003: 459 (40%); 0.0202: 229 (20%) | -0.0149: 236 (21%); -0.0014: 458 (40%); 0.003: 692 (61%); 0.0202: 914 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.6388, 25.9751, 26.6402, 27.3557 | 24.6388: 917 (80%); 25.9751: 685 (60%); 26.6402: 457 (40%); 27.3557: 319 (28%) | 24.6388: 232 (20%); 25.9751: 460 (40%); 26.6402: 685 (60%); 27.3557: 986 (86%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -1.22, -0.455, 0, 0.567 | -1.22: 913 (80%); -0.455: 685 (60%); 0: 465 (41%); 0.567: 229 (20%) | -1.22: 229 (20%); -0.455: 457 (40%); 0: 705 (62%); 0.567: 913 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -0.567, 0, 0.455, 1.22 | -0.567: 913 (80%); 0: 705 (62%); 0.455: 457 (40%); 1.22: 229 (20%) | -0.567: 229 (20%); 0: 465 (41%); 0.455: 685 (60%); 1.22: 913 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0264, 0.0097, 0.0472, 0.1221 | -0.0264: 913 (80%); 0.0097: 698 (61%); 0.0472: 457 (40%); 0.1221: 229 (20%) | -0.0264: 229 (20%); 0.0097: 457 (40%); 0.0472: 685 (60%); 0.1221: 913 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.2486, 8.5985, 8.9584, 10.0827 | 8.2486: 913 (80%); 8.5985: 685 (60%); 8.9584: 457 (40%); 10.0827: 230 (20%) | 8.2486: 228 (20%); 8.5985: 456 (40%); 8.9584: 684 (60%); 10.0827: 911 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 1131 (99%); 1: 391 (34%) | 0: 740 (65%); 1: 986 (86%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.1% | -1, 0 | -1: 1055 (92%); 0: 858 (75%) | -1: 273 (24%); 0: 963 (84%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 1131 (99%); 1: 459 (40%) | 0: 672 (59%); 1: 954 (84%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 3, 6, 147, 268 | 3: 944 (83%); 6: 735 (64%); 147: 457 (40%); 268: 229 (20%) | 3: 265 (23%); 6: 457 (40%); 147: 686 (60%); 268: 915 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 1, 5, 87, 138 | 1: 929 (81%); 5: 697 (61%); 87: 458 (40%); 138: 231 (20%) | 1: 305 (27%); 5: 472 (41%); 87: 693 (61%); 138: 914 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.2625, 0.0581, 0.2902, 0.75 | -0.2625: 913 (80%); 0.0581: 685 (60%); 0.2902: 457 (40%); 0.75: 230 (20%) | -0.2625: 229 (20%); 0.0581: 457 (40%); 0.2902: 685 (60%); 0.75: 913 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -3.7874, -1.8414, -0.8241, -0.2337 | -3.7874: 913 (80%); -1.8414: 685 (60%); -0.8241: 457 (40%); -0.2337: 229 (20%) | -3.7874: 229 (20%); -1.8414: 457 (40%); -0.8241: 685 (60%); -0.2337: 913 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -4.2737, -2.1129, -0.9641, -0.2517 | -4.2737: 913 (80%); -2.1129: 685 (60%); -0.9641: 457 (40%); -0.2517: 229 (20%) | -4.2737: 229 (20%); -2.1129: 457 (40%); -0.9641: 685 (60%); -0.2517: 913 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.1277, 0.1416, 0.3957, 0.9029 | -0.1277: 913 (80%); 0.1416: 685 (60%); 0.3957: 457 (40%); 0.9029: 229 (20%) | -0.1277: 229 (20%); 0.1416: 457 (40%); 0.3957: 685 (60%); 0.9029: 913 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -2.9875, -1.3192, -0.6139, -0.1425 | -2.9875: 913 (80%); -1.3192: 685 (60%); -0.6139: 457 (40%); -0.1425: 229 (20%) | -2.9875: 229 (20%); -1.3192: 457 (40%); -0.6139: 685 (60%); -0.1425: 913 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -3.854, -1.8648, -0.8613, -0.2731 | -3.854: 913 (80%); -1.8648: 685 (60%); -0.8613: 457 (40%); -0.2731: 229 (20%) | -3.854: 229 (20%); -1.8648: 457 (40%); -0.8613: 685 (60%); -0.2731: 913 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 40.09, 46.95, 52.33, 59.83 | 40.09: 913 (80%); 46.95: 685 (60%); 52.33: 457 (40%); 59.83: 229 (20%) | 40.09: 229 (20%); 46.95: 457 (40%); 52.33: 685 (60%); 59.83: 913 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 98.3% | -0.2113, -0.1301, -0.0585, 0.021 | -0.2113: 898 (79%); -0.1301: 673 (59%); -0.0585: 450 (39%); 0.021: 225 (20%) | -0.2113: 226 (20%); -0.1301: 449 (39%); -0.0585: 674 (59%); 0.021: 898 (79%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.1% | 0.0063, 0.0145, 0.0262, 0.0464 | 0.0063: 904 (79%); 0.0145: 677 (59%); 0.0262: 449 (39%); 0.0464: 227 (20%) | 0.0063: 227 (20%); 0.0145: 454 (40%); 0.0262: 682 (60%); 0.0464: 904 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 1141 (100%); 1: 843 (74%); 3: 516 (45%); 8: 237 (21%) | 0: 298 (26%); 1: 507 (44%); 3: 708 (62%); 8: 936 (82%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1875 | 0: 1141 (100%); 0.1875: 229 (20%) | 0: 775 (68%); 0.1875: 913 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.375, 0.6667 | 0: 1141 (100%); 0.375: 464 (41%); 0.6667: 246 (22%) | 0: 483 (42%); 0.375: 685 (60%); 0.6667: 922 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 6 | 0: 1141 (100%); 1: 754 (66%); 2: 544 (48%); 6: 232 (20%) | 0: 387 (34%); 1: 597 (52%); 2: 721 (63%); 6: 938 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 1141 (100%); 1: 843 (74%); 3: 516 (45%); 8: 237 (21%) | 0: 298 (26%); 1: 507 (44%); 3: 708 (62%); 8: 936 (82%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 6 | 0: 1141 (100%); 1: 747 (65%); 3: 461 (40%); 6: 237 (21%) | 0: 394 (35%); 1: 556 (49%); 3: 776 (68%); 6: 929 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1652, 0.3333, 0.625 | 0: 1015 (89%); 0.1652: 685 (60%); 0.3333: 462 (40%); 0.625: 229 (20%) | 0: 325 (28%); 0.1652: 457 (40%); 0.3333: 704 (62%); 0.625: 915 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0909, 0.6 | 0: 1032 (90%); 0.0909: 458 (40%); 0.6: 232 (20%) | 0: 657 (58%); 0.0909: 686 (60%); 0.6: 917 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2433, 0.5714 | 0: 1022 (90%); 0.2433: 457 (40%); 0.5714: 232 (20%) | 0: 558 (49%); 0.2433: 685 (60%); 0.5714: 915 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2433, 0.5714 | 0: 1022 (90%); 0.2433: 457 (40%); 0.5714: 232 (20%) | 0: 558 (49%); 0.2433: 685 (60%); 0.5714: 915 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.1111, 0, 0.1246 | -0.1111: 913 (80%); 0: 856 (75%); 0.1246: 229 (20%) | -0.1111: 231 (20%); 0: 840 (74%); 0.1246: 913 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.6554, -0.3053, 0, 1.3013 | -0.6554: 913 (80%); -0.3053: 685 (60%); 0: 635 (56%); 1.3013: 229 (20%) | -0.6554: 229 (20%); -0.3053: 457 (40%); 0: 695 (61%); 1.3013: 913 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 7, 11 | 2: 965 (85%); 4: 757 (66%); 7: 525 (46%); 11: 257 (23%) | 2: 277 (24%); 4: 468 (41%); 7: 696 (61%); 11: 919 (81%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0327, -0.0005, 0.0258, 0.0571 | -0.0327: 913 (80%); -0.0005: 683 (60%); 0.0258: 458 (40%); 0.0571: 229 (20%) | -0.0327: 228 (20%); -0.0005: 458 (40%); 0.0258: 683 (60%); 0.0571: 912 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0589, -0.0363, -0.0144, 0.0236 | -0.0589: 911 (80%); -0.0363: 685 (60%); -0.0144: 456 (40%); 0.0236: 229 (20%) | -0.0589: 230 (20%); -0.0363: 456 (40%); -0.0144: 685 (60%); 0.0236: 912 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.026, 0.0085, 0.0386, 0.0681 | -0.026: 913 (80%); 0.0085: 686 (60%); 0.0386: 456 (40%); 0.0681: 228 (20%) | -0.026: 228 (20%); 0.0085: 455 (40%); 0.0386: 685 (60%); 0.0681: 913 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -25.537, -13.851, -3.369, 13.201 | -25.537: 913 (80%); -13.851: 685 (60%); -3.369: 457 (40%); 13.201: 229 (20%) | -25.537: 229 (20%); -13.851: 457 (40%); -3.369: 685 (60%); 13.201: 913 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.0496, 0.0681, 0.0896, 0.1287 | 0.0496: 914 (80%); 0.0681: 685 (60%); 0.0896: 458 (40%); 0.1287: 230 (20%) | 0.0496: 230 (20%); 0.0681: 458 (40%); 0.0896: 685 (60%); 0.1287: 913 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.6685, 0.8137, 0.8972, 0.9487 | 0.6685: 913 (80%); 0.8137: 685 (60%); 0.8972: 458 (40%); 0.9487: 229 (20%) | 0.6685: 229 (20%); 0.8137: 457 (40%); 0.8972: 685 (60%); 0.9487: 915 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -3.1145, -2.0588, -1.3715, -0.5104 | -3.1145: 913 (80%); -2.0588: 685 (60%); -1.3715: 457 (40%); -0.5104: 229 (20%) | -3.1145: 229 (20%); -2.0588: 457 (40%); -1.3715: 686 (60%); -0.5104: 913 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | -0.3999, 0.0952, 0.4093, 0.7229 | -0.3999: 913 (80%); 0.0952: 685 (60%); 0.4093: 457 (40%); 0.7229: 229 (20%) | -0.3999: 229 (20%); 0.0952: 457 (40%); 0.4093: 685 (60%); 0.7229: 913 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -3.5269, -2.3314, -1.5826, -0.4349 | -3.5269: 913 (80%); -2.3314: 685 (60%); -1.5826: 457 (40%); -0.4349: 229 (20%) | -3.5269: 229 (20%); -2.3314: 457 (40%); -1.5826: 685 (60%); -0.4349: 913 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -3.89, -0.64, 2.002, 5.291 | -3.89: 913 (80%); -0.64: 685 (60%); 2.002: 457 (40%); 5.291: 229 (20%) | -3.89: 229 (20%); -0.64: 457 (40%); 2.002: 685 (60%); 5.291: 913 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 45.86, 48.4, 50.65, 53.67 | 45.86: 913 (80%); 48.4: 685 (60%); 50.65: 457 (40%); 53.67: 229 (20%) | 45.86: 229 (20%); 48.4: 458 (40%); 50.65: 685 (60%); 53.67: 914 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 67.25, 80.5, 88.02, 93.61 | 67.25: 913 (80%); 80.5: 685 (60%); 88.02: 457 (40%); 93.61: 229 (20%) | 67.25: 229 (20%); 80.5: 457 (40%); 88.02: 685 (60%); 93.61: 913 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 44.04, 46.55, 48.62, 51.5 | 44.04: 915 (80%); 46.55: 685 (60%); 48.62: 458 (40%); 51.5: 229 (20%) | 44.04: 229 (20%); 46.55: 457 (40%); 48.62: 686 (60%); 51.5: 913 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 48.23, 51.88, 54.87, 58.39 | 48.23: 913 (80%); 51.88: 685 (60%); 54.87: 458 (40%); 58.39: 229 (20%) | 48.23: 229 (20%); 51.88: 457 (40%); 54.87: 685 (60%); 58.39: 914 (80%) | OFFLINE |
| sector_etf_return_pct | (no module found writing the key) | 100.0% | 0 | 0: 1140 (100%) | 0: 1140 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0235, 0.0436, 0.0597, 0.0857 | 0.0235: 913 (80%); 0.0436: 715 (63%); 0.0597: 459 (40%); 0.0857: 229 (20%) | 0.0235: 229 (20%); 0.0436: 457 (40%); 0.0597: 685 (60%); 0.0857: 915 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0878, -0.0595, -0.0434, -0.039 | -0.0878: 914 (80%); -0.0595: 685 (60%); -0.0434: 477 (42%); -0.039: 233 (20%) | -0.0878: 236 (21%); -0.0595: 458 (40%); -0.0434: 829 (73%); -0.039: 914 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 1141 (100%); 1: 237 (21%) | 0: 904 (79%); 1: 982 (86%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 24, 41, 63, 66 | 24: 945 (83%); 41: 702 (62%); 63: 467 (41%); 66: 241 (21%) | 24: 270 (24%); 41: 462 (40%); 63: 685 (60%); 66: 948 (83%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.1% | 0.0122, 0.0186, 0.0276, 0.0456 | 0.0122: 894 (78%); 0.0186: 671 (59%); 0.0276: 448 (39%); 0.0456: 224 (20%) | 0.0122: 225 (20%); 0.0186: 448 (39%); 0.0276: 671 (59%); 0.0456: 895 (78%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 100.0% | 0.2825, 0.3579, 0.4294, 0.5512 | 0.2825: 913 (80%); 0.3579: 685 (60%); 0.4294: 457 (40%); 0.5512: 229 (20%) | 0.2825: 229 (20%); 0.3579: 457 (40%); 0.4294: 685 (60%); 0.5512: 913 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 100.0% | 43.7, 82.1, 115.3, 167.9 | 43.7: 913 (80%); 82.1: 685 (60%); 115.3: 458 (40%); 167.9: 229 (20%) | 43.7: 229 (20%); 82.1: 458 (40%); 115.3: 685 (60%); 167.9: 913 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | 0.205, 0.53, 1.16, 2.9 | 0.205: 914 (80%); 0.53: 685 (60%); 1.16: 458 (40%); 2.9: 229 (20%) | 0.205: 231 (20%); 0.53: 458 (40%); 1.16: 686 (60%); 2.9: 913 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 26.59, 38.53, 48.19, 60.13 | 26.59: 913 (80%); 38.53: 685 (60%); 48.19: 457 (40%); 60.13: 229 (20%) | 26.59: 229 (20%); 38.53: 457 (40%); 48.19: 685 (60%); 60.13: 913 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 35.97, 45.3, 54.48, 66.35 | 35.97: 913 (80%); 45.3: 686 (60%); 54.48: 457 (40%); 66.35: 229 (20%) | 35.97: 229 (20%); 45.3: 457 (40%); 54.48: 685 (60%); 66.35: 913 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 24.11, 49, 77.83, 93.76 | 24.11: 914 (80%); 49: 685 (60%); 77.83: 457 (40%); 93.76: 230 (20%) | 24.11: 229 (20%); 49: 457 (40%); 77.83: 685 (60%); 93.76: 913 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 43.15, 69.55, 96.7, 100 | 43.15: 913 (80%); 69.55: 685 (60%); 96.7: 457 (40%); 100: 420 (37%) | 43.15: 229 (20%); 69.55: 457 (40%); 96.7: 685 (60%); 100: 1141 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 7, 11, 17 | 4: 942 (83%); 7: 795 (70%); 11: 477 (42%); 17: 269 (24%) | 4: 248 (22%); 7: 542 (48%); 11: 706 (62%); 17: 954 (84%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 11, 15, 18 | 5: 959 (84%); 11: 705 (62%); 15: 535 (47%); 18: 236 (21%) | 5: 270 (24%); 11: 480 (42%); 15: 814 (71%); 18: 947 (83%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 47.84, 51.36, 54.35, 58.34 | 47.84: 914 (80%); 51.36: 685 (60%); 54.35: 457 (40%); 58.34: 230 (20%) | 47.84: 229 (20%); 51.36: 460 (40%); 54.35: 686 (60%); 58.34: 914 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.246, 0.6071, 0.8016, 0.9444 | 0.246: 913 (80%); 0.6071: 686 (60%); 0.8016: 462 (40%); 0.9444: 230 (20%) | 0.246: 233 (20%); 0.6071: 462 (40%); 0.8016: 707 (62%); 0.9444: 914 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.81, 19.31, 24.76, 30.19 | 15.81: 913 (80%); 19.31: 685 (60%); 24.76: 457 (40%); 30.19: 229 (20%) | 15.81: 230 (20%); 19.31: 458 (40%); 24.76: 686 (60%); 30.19: 918 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 15.81, 19.31, 24.76, 30.19 | 15.81: 913 (80%); 19.31: 685 (60%); 24.76: 457 (40%); 30.19: 229 (20%) | 15.81: 230 (20%); 19.31: 458 (40%); 24.76: 686 (60%); 30.19: 918 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8704, 0.9135, 0.9495, 1.0044 | 0.8704: 915 (80%); 0.9135: 686 (60%); 0.9495: 460 (40%); 1.0044: 229 (20%) | 0.8704: 229 (20%); 0.9135: 462 (40%); 0.9495: 686 (60%); 1.0044: 916 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.71, 0.86, 1.02, 1.47 | 0.71: 919 (81%); 0.86: 691 (61%); 1.02: 462 (40%); 1.47: 231 (20%) | 0.71: 236 (21%); 0.86: 462 (40%); 1.02: 695 (61%); 1.47: 914 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 100.0% | 0.0185, 0.0393, 0.0632, 0.0984 | 0.0185: 913 (80%); 0.0393: 686 (60%); 0.0632: 457 (40%); 0.0984: 229 (20%) | 0.0185: 229 (20%); 0.0393: 458 (40%); 0.0632: 686 (60%); 0.0984: 913 (80%) | OFFLINE |
| vwap | backtest/signals/technical.py | 100.0% | 43.7859, 76.6735, 116.8301, 193.6947 | 43.7859: 913 (80%); 76.6735: 685 (60%); 116.8301: 457 (40%); 193.6947: 229 (20%) | 43.7859: 229 (20%); 76.6735: 457 (40%); 116.8301: 685 (60%); 193.6947: 913 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 42.1442, 73.7093, 112.3377, 186.6127 | 42.1442: 913 (80%); 73.7093: 685 (60%); 112.3377: 457 (40%); 186.6127: 229 (20%) | 42.1442: 229 (20%); 73.7093: 457 (40%); 112.3377: 685 (60%); 186.6127: 913 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 40.5537, 70.0964, 108.6676, 178.1466 | 40.5537: 913 (80%); 70.0964: 685 (60%); 108.6676: 457 (40%); 178.1466: 229 (20%) | 40.5537: 229 (20%); 70.0964: 457 (40%); 108.6676: 685 (60%); 178.1466: 913 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 45.6195, 79.191, 121.5831, 202.6933 | 45.6195: 913 (80%); 79.191: 685 (60%); 121.5831: 457 (40%); 202.6933: 229 (20%) | 45.6195: 229 (20%); 79.191: 457 (40%); 121.5831: 685 (60%); 202.6933: 913 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 47.51, 81.4702, 126.7475, 209.327 | 47.51: 913 (80%); 81.4702: 685 (60%); 126.7475: 457 (40%); 209.327: 229 (20%) | 47.51: 229 (20%); 81.4702: 457 (40%); 126.7475: 685 (60%); 209.327: 913 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1141 (100%) | 0: 1072 (94%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1141 (100%) | 0: 1011 (89%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0447, -0.0243, -0.002, 0.0333 | -0.0447: 913 (80%); -0.0243: 687 (60%); -0.002: 458 (40%); 0.0333: 230 (20%) | -0.0447: 229 (20%); -0.0243: 458 (40%); -0.002: 685 (60%); 0.0333: 913 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -46.99, -39.41, -29.21, -14.21 | -46.99: 913 (80%); -39.41: 685 (60%); -29.21: 457 (40%); -14.21: 229 (20%) | -46.99: 229 (20%); -39.41: 458 (40%); -29.21: 686 (60%); -14.21: 914 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 98.9% | 0.6028, 0.8531, 1.0665, 1.3809 | 0.6028: 903 (79%); 0.8531: 677 (59%); 1.0665: 452 (40%); 1.3809: 226 (20%) | 0.6028: 226 (20%); 0.8531: 452 (40%); 1.0665: 677 (59%); 1.3809: 903 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 98.9% | 3, 5, 7, 9 | 3: 985 (86%); 5: 786 (69%); 7: 555 (49%); 9: 321 (28%) | 3: 230 (20%); 5: 453 (40%); 7: 685 (60%); 9: 947 (83%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 98.9% | 0.2056, 0.247, 0.3033, 0.3991 | 0.2056: 903 (79%); 0.247: 677 (59%); 0.3033: 452 (40%); 0.3991: 226 (20%) | 0.2056: 227 (20%); 0.247: 452 (40%); 0.3033: 677 (59%); 0.3991: 903 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 98.9% | 3, 6, 8, 9 | 3: 970 (85%); 6: 696 (61%); 8: 498 (44%); 9: 374 (33%) | 3: 229 (20%); 6: 515 (45%); 8: 755 (66%); 9: 914 (80%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 98.9% | 0.0316, 0.0422, 0.0609, 0.0934 | 0.0316: 904 (79%); 0.0422: 678 (59%); 0.0609: 455 (40%); 0.0934: 227 (20%) | 0.0316: 230 (20%); 0.0422: 452 (40%); 0.0609: 678 (59%); 0.0934: 903 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 98.9% | 4, 6, 8, 9 | 4: 947 (83%); 6: 755 (66%); 8: 519 (45%); 9: 392 (34%) | 4: 277 (24%); 6: 487 (43%); 8: 737 (65%); 9: 905 (79%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.0% | -0.2605, -0.1358, -0.0207, 0.1256 | -0.2605: 904 (79%); -0.1358: 678 (59%); -0.0207: 452 (40%); 0.1256: 226 (20%) | -0.2605: 226 (20%); -0.1358: 452 (40%); -0.0207: 678 (59%); 0.1256: 904 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.0% | 2, 3, 5, 7 | 2: 910 (80%); 3: 753 (66%); 5: 478 (42%); 7: 300 (26%) | 2: 377 (33%); 3: 517 (45%); 5: 754 (66%); 7: 925 (81%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 3.6% |
| 8k_item_5_02_filed_within_7d | 3.5% |
| above_avwap_20high | 81.8% |
| above_avwap_20low | 92.9% |
| above_avwap_252low | 70.8% |
| above_avwap_50low | 94.2% |
| above_cam_r3 | 86.3% |
| above_cam_r4 | 65.7% |
| above_cpr | 92.8% |
| above_pivot | 95.1% |
| above_prev_high | 72.9% |
| above_prev_high_clearance_atr_05 | 41.4% |
| above_prev_low | 99.8% |
| above_r1 | 69.8% |
| above_r2 | 40.6% |
| above_vwap | 33.9% |
| above_wood_p | 89.4% |
| ad_rising | 68.8% |
| adx_cross_up | 0.6% |
| adx_cross_up_20 | 0.4% |
| adx_di_bear | 64.6% |
| adx_di_bull | 35.4% |
| adx_strong | 6.3% |
| adx_trending | 45.5% |
| ao_cross_dn | 1.3% |
| ao_cross_up | 0.5% |
| ao_positive | 13.3% |
| ao_twin_peaks_bull | 8.6% |
| at_key_fib | 23.8% |
| at_key_fib_wide | 55.7% |
| avwap_20high_loss_recent_3d | 2.2% |
| avwap_20high_reclaim_recent_3d | 66.9% |
| avwap_20low_loss_recent_3d | 4.3% |
| avwap_20low_reclaim_recent_3d | 42.8% |
| avwap_252low_loss_recent_3d | 2.4% |
| avwap_252low_reclaim_recent_3d | 33.0% |
| avwap_50low_loss_recent_3d | 3.0% |
| avwap_50low_reclaim_recent_3d | 43.3% |
| bb_10_20_above_mid | 76.8% |
| bb_10_20_expanding | 46.2% |
| bb_10_20_pctb_gt_75 | 47.2% |
| bb_10_20_pctb_gt_8 | 42.2% |
| bb_10_20_pctb_gt_85 | 35.2% |
| bb_10_20_pctb_gt_9 | 28.5% |
| bb_10_20_pctb_gt_95 | 20.4% |
| bb_10_20_pctb_lt_1 | 0.1% |
| bb_10_20_pctb_lt_15 | 0.4% |
| bb_10_20_pctb_lt_2 | 1.5% |
| bb_10_20_pctb_lt_25 | 2.9% |
| bb_10_20_reclaim_from_lower_recent_3d | 16.7% |
| bb_10_20_reclaim_from_upper_recent_3d | 2.6% |
| bb_10_20_squeeze | 28.7% |
| bb_10_20_touch_upper | 21.4% |
| bb_20_15_above_mid | 70.4% |
| bb_20_15_expanding | 23.3% |
| bb_20_15_pctb_gt_75 | 20.2% |
| bb_20_15_pctb_gt_8 | 14.7% |
| bb_20_15_pctb_gt_85 | 10.1% |
| bb_20_15_pctb_gt_9 | 7.7% |
| bb_20_15_pctb_gt_95 | 6.0% |
| bb_20_15_pctb_lt_15 | 0.3% |
| bb_20_15_pctb_lt_2 | 0.5% |
| bb_20_15_pctb_lt_25 | 1.8% |
| bb_20_15_reclaim_from_lower_recent_3d | 24.7% |
| bb_20_15_reclaim_from_upper_recent_3d | 1.1% |
| bb_20_15_squeeze | 20.9% |
| bb_20_15_touch_upper | 6.4% |
| bb_20_20_above_mid | 70.4% |
| bb_20_20_expanding | 23.3% |
| bb_20_20_pctb_gt_75 | 11.7% |
| bb_20_20_pctb_gt_8 | 7.7% |
| bb_20_20_pctb_gt_85 | 5.5% |
| bb_20_20_pctb_gt_9 | 4.0% |
| bb_20_20_pctb_gt_95 | 3.3% |
| bb_20_20_pctb_lt_25 | 0.3% |
| bb_20_20_reclaim_from_lower_recent_3d | 17.4% |
| bb_20_20_reclaim_from_upper_recent_3d | 0.5% |
| bb_20_20_squeeze | 6.8% |
| bb_20_20_touch_upper | 3.1% |
| bearish_pin_bar | 2.0% |
| below_avwap_20high | 18.2% |
| below_avwap_20low | 7.1% |
| below_avwap_252low | 29.2% |
| below_avwap_50low | 5.8% |
| below_cam_s3 | 0.5% |
| below_cam_s4 | 0.1% |
| below_cpr | 4.9% |
| below_ema_20 | 36.7% |
| below_ema_200 | 84.2% |
| below_ema_200_break_recent_5d | 6.2% |
| below_ema_20_break_recent_5d | 16.9% |
| below_ema_21 | 39.4% |
| below_ema_21_break_recent_5d | 16.8% |
| below_ema_50 | 75.7% |
| below_ema_50_break_recent_5d | 11.0% |
| below_ema_9 | 14.0% |
| below_ema_9_break_recent_5d | 12.9% |
| below_prev_high | 26.9% |
| below_prev_low | 0.2% |
| below_s1 | 0.1% |
| below_sma_20 | 29.6% |
| below_sma_200 | 81.9% |
| below_sma_21 | 31.1% |
| below_sma_50 | 75.7% |
| below_sma_9 | 21.8% |
| below_vwap | 66.1% |
| break_52w_high | 0.2% |
| break_52w_high_clearance_atr_05 | 0.2% |
| bullish_engulfing | 18.5% |
| bullish_pin_bar | 2.1% |
| capitulation_recent_3d | 1.1% |
| ceo_buy | 2.8% |
| cfo_buy | 0.8% |
| chandelier_long_bullish | 78.6% |
| chandelier_long_flip_dn | 0.2% |
| chandelier_short_bearish | 58.7% |
| chandelier_short_flip_up | 35.1% |
| classification_change_from_tech | 50.0% |
| classification_change_to_defensive | 50.0% |
| close_in_bottom_40pct_of_range | 3.6% |
| close_in_top_40pct_of_range | 85.5% |
| cluster_buy | 1.2% |
| cmf_cross_dn | 0.6% |
| cmf_cross_up | 14.2% |
| cmf_negative | 44.0% |
| cmf_positive | 56.0% |
| concentrated_sell | 3.4% |
| cpr_narrow | 91.1% |
| cpr_narrow_tight | 22.2% |
| cup_handle_detected | 10.7% |
| cup_handle_neckline_break_retest_long | 0.4% |
| dc10_breakout_dn_1pct | 0.2% |
| dc10_breakout_up | 22.4% |
| dc10_breakout_up_1pct | 30.2% |
| dc10_new_high | 25.3% |
| dc10_strong_breakout_up | 9.4% |
| dc20_breakout_up | 1.9% |
| dc20_new_high | 2.3% |
| dc20_resistance_break_retest_strong | 1.3% |
| dc20_support_break_retest_strong | 9.8% |
| defensive_leadership | 67.2% |
| director_only_buy | 5.3% |
| doji | 1.9% |
| double_bottom_detected | 7.3% |
| double_top_detected | 14.8% |
| dpi_elevated | 59.8% |
| drying_volume_on_up_turn | 58.5% |
| ema_20_50_bearish | 87.1% |
| ema_20_50_bullish | 12.9% |
| ema_20_50_golden_cross | 0.9% |
| ema_50_200_bearish | 78.4% |
| ema_50_200_bullish | 21.6% |
| ema_50_200_death_cross | 0.4% |
| ema_50_200_golden_cross | 0.1% |
| ema_9_21_bearish | 86.1% |
| ema_9_21_bullish | 13.9% |
| ema_9_21_death_cross | 0.2% |
| ema_9_21_golden_cross | 2.7% |
| flag_bear_break_retest_short | 1.1% |
| flag_bear_broke | 1.1% |
| flag_bear_detected | 0.9% |
| flag_bull_break_retest_long | 0.1% |
| flag_bull_broke | 0.1% |
| flag_bull_detected | 0.1% |
| force_index_cross_dn | 0.3% |
| force_index_cross_up | 35.8% |
| force_index_positive | 68.9% |
| gap_dn_1_5pct | 6.0% |
| gap_dn_2pct | 2.5% |
| gap_up_1_5pct | 16.1% |
| gap_up_2pct | 10.6% |
| hammer | 1.8% |
| head_shoulders_bottom_detected | 1.3% |
| head_shoulders_top_detected | 5.2% |
| house_cluster_buy | 6.5% |
| house_cluster_sell | 7.8% |
| htf_aligned_bear | 64.0% |
| htf_aligned_bull | 8.3% |
| htf_disagreement | 0.8% |
| hull_bearish | 38.8% |
| hull_bullish | 61.2% |
| hull_flip_dn | 1.7% |
| hull_flip_up | 11.8% |
| ichi_above_cloud | 13.7% |
| ichi_above_cloud_break_recent_5d | 8.9% |
| ichi_below_cloud | 73.6% |
| ichi_below_cloud_break_recent_5d | 4.7% |
| ichi_cloud_thick | 86.6% |
| ichi_tk_bearish | 78.8% |
| ichi_tk_bullish | 17.7% |
| ichi_tk_cross_dn | 1.0% |
| ichi_tk_cross_up | 1.9% |
| ichi_weekly_above_cloud | 16.9% |
| ichi_weekly_below_cloud | 48.4% |
| ichi_weekly_in_cloud | 34.7% |
| in_reversal_window | 2.7% |
| inside_bar | 8.9% |
| inside_cpr | 2.5% |
| inside_kc | 97.5% |
| insider_cluster_active | 25.7% |
| institutional_buy | 89.8% |
| institutional_negative | 3.9% |
| institutional_persistence_growing | 48.3% |
| institutional_persistence_strong | 62.2% |
| institutional_strong_buy | 79.6% |
| inverted_cup_handle_detected | 10.1% |
| is_friday | 18.7% |
| is_halloween_period | 57.2% |
| is_halloween_period_first_day | 0.3% |
| is_january | 7.2% |
| is_january_extended | 7.9% |
| is_monday | 16.1% |
| is_pre_holiday | 4.9% |
| is_summer_period | 42.8% |
| is_totm_window | 33.4% |
| is_totm_window_first_day | 8.3% |
| is_week_open | 17.8% |
| kc_touch_upper | 2.5% |
| large_dollar_buy | 1.5% |
| macd_12_26_9_bearish | 35.1% |
| macd_12_26_9_bullish | 64.9% |
| macd_12_26_9_crossover_dn | 1.2% |
| macd_12_26_9_crossover_up | 11.9% |
| macd_8_21_5_bearish | 28.7% |
| macd_8_21_5_bullish | 71.3% |
| macd_8_21_5_crossover_dn | 0.4% |
| macd_8_21_5_crossover_up | 11.9% |
| marubozu_bull | 5.4% |
| mfi_broad_overbought | 3.7% |
| mfi_broad_oversold | 3.8% |
| mfi_overbought | 0.1% |
| mfi_oversold | 0.2% |
| monthly_above_sma_12 | 18.3% |
| monthly_above_sma_6 | 16.9% |
| monthly_bias_bear | 74.0% |
| monthly_bias_bull | 9.2% |
| monthly_momentum_pos | 24.5% |
| morning_star | 9.3% |
| near_52w_high | 0.3% |
| near_52w_high_95pct | 1.2% |
| near_52w_high_retest_long | 0.5% |
| near_52w_low_105pct | 1.3% |
| near_avwap_20high_atr_05x | 40.5% |
| near_avwap_20high_atr_10x | 79.2% |
| near_avwap_20high_atr_15x | 94.2% |
| near_avwap_20high_atr_20x | 98.0% |
| near_avwap_20low_atr_05x | 19.6% |
| near_avwap_20low_atr_10x | 40.9% |
| near_avwap_20low_atr_15x | 69.5% |
| near_avwap_20low_atr_20x | 89.3% |
| near_avwap_252low_atr_05x | 18.8% |
| near_avwap_252low_atr_10x | 40.0% |
| near_avwap_252low_atr_15x | 61.9% |
| near_avwap_252low_atr_20x | 77.5% |
| near_avwap_50low_atr_05x | 17.4% |
| near_avwap_50low_atr_10x | 40.7% |
| near_avwap_50low_atr_15x | 68.4% |
| near_avwap_50low_atr_20x | 87.2% |
| near_cam_r3 | 15.1% |
| near_cam_s3 | 1.1% |
| near_cam_s4 | 0.1% |
| near_fib_236 | 1.8% |
| near_fib_382 | 4.2% |
| near_fib_500 | 8.3% |
| near_fib_618 | 11.4% |
| near_fib_786 | 3.9% |
| near_pivot | 5.8% |
| near_prev_close | 3.6% |
| near_prev_high | 9.6% |
| near_prev_low | 0.7% |
| near_r1 | 14.3% |
| near_r1_wide | 54.8% |
| near_r2 | 10.8% |
| near_r2_wide | 52.3% |
| near_s1 | 0.2% |
| near_s1_wide | 8.1% |
| near_s2 | 0.1% |
| near_s2_wide | 1.7% |
| near_wood_r1 | 7.4% |
| near_wood_s1 | 2.5% |
| news_uses_polygon_score | 26.9% |
| obv_bearish | 40.9% |
| obv_bullish | 59.1% |
| obv_diverge_bull | 5.3% |
| obv_falling | 35.7% |
| obv_rising | 64.3% |
| outside_bar | 14.5% |
| pead_negative_surprise | 24.7% |
| pead_positive_surprise | 14.7% |
| pin_bar | 4.1% |
| po3_accumulation_active | 20.3% |
| po3_bullish | 21.6% |
| po3_manipulation_sweep_down | 2.0% |
| po3_manipulation_sweep_up | 11.7% |
| po3_mmbm_setup | 2.0% |
| po3_sweep_above_prior_high | 83.0% |
| po3_sweep_below_prior_low | 26.8% |
| ppo_bullish | 64.2% |
| ppo_crossover_dn | 1.2% |
| ppo_crossover_up | 11.8% |
| pre_fomc_d0 | 2.3% |
| pre_fomc_d1 | 1.3% |
| pre_fomc_window | 3.6% |
| price_above_dema | 88.9% |
| price_above_ema_20 | 63.3% |
| price_above_ema_200 | 15.8% |
| price_above_ema_200_break_recent_5d | 10.0% |
| price_above_ema_20_break_recent_5d | 62.5% |
| price_above_ema_21 | 60.6% |
| price_above_ema_21_break_recent_5d | 59.9% |
| price_above_ema_50 | 24.3% |
| price_above_ema_50_break_recent_5d | 20.6% |
| price_above_ema_9 | 86.0% |
| price_above_ema_9_break_recent_5d | 81.2% |
| price_above_hull | 80.4% |
| price_above_sma_200 | 18.1% |
| price_above_sma_21 | 68.8% |
| price_above_sma_50 | 24.3% |
| price_above_tema | 87.5% |
| price_below_dema | 11.1% |
| price_below_hull | 19.6% |
| price_below_tema | 12.5% |
| psar_bullish | 63.2% |
| psar_flip_dn | 1.2% |
| psar_flip_up | 18.0% |
| r1_break_retest_long | 66.2% |
| recent_capitulation_at_s3 | 0.4% |
| resistance_break_retest | 1.8% |
| risk_off_regime_bond_signal | 23.0% |
| risk_off_regime_bond_signal_strong | 6.9% |
| risk_off_regime_gold_signal | 54.3% |
| risk_on_regime_bond_signal | 30.1% |
| risk_on_regime_bond_signal_strong | 13.1% |
| roc_positive | 54.7% |
| roc_turning_dn | 2.3% |
| roc_turning_up | 21.5% |
| rsi_14_bullish | 45.7% |
| rsi_14_cross_dn_overbought_recent_3d | 0.1% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.7% |
| rsi_14_cross_up_oversold_recent_3d | 15.0% |
| rsi_14_overbought | 0.3% |
| rsi_14_rising | 98.0% |
| rsi_21_bullish | 28.4% |
| rsi_21_cross_up_oversold_recent_3d | 8.2% |
| rsi_21_oversold | 0.1% |
| rsi_21_rising | 98.0% |
| rsi_2_bullish | 91.6% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 12.0% |
| rsi_2_cross_dn_overbought_recent_3d | 9.8% |
| rsi_2_cross_up_extreme_os_recent_3d | 50.7% |
| rsi_2_cross_up_oversold_recent_3d | 59.3% |
| rsi_2_extreme_ob | 61.4% |
| rsi_2_extreme_os | 0.6% |
| rsi_2_overbought | 77.4% |
| rsi_2_oversold | 1.8% |
| rsi_2_rising | 98.0% |
| rsi_9_bullish | 70.2% |
| rsi_9_cross_dn_overbought_recent_3d | 0.7% |
| rsi_9_cross_up_extreme_os_recent_3d | 6.7% |
| rsi_9_cross_up_oversold_recent_3d | 22.6% |
| rsi_9_extreme_ob | 0.1% |
| rsi_9_overbought | 1.9% |
| rsi_9_rising | 98.0% |
| s1_break_retest_short | 42.2% |
| sc_13d_filed_within_30d | 0.9% |
| sc_13g_filed_within_30d | 1.9% |
| sector_outperforming_spy | 42.4% |
| sector_underperforming_spy | 57.6% |
| shooting_star | 1.8% |
| sma_20_50_bullish | 16.9% |
| sma_20_50_golden_cross | 0.7% |
| sma_50_200_bullish | 28.4% |
| sma_9_21_bullish | 28.0% |
| sma_9_21_golden_cross | 5.5% |
| smc_bos_bearish | 27.8% |
| smc_bos_bullish | 5.3% |
| smc_bos_retest_long | 2.4% |
| smc_bos_retest_short | 4.6% |
| smc_breaker_block_bearish | 26.1% |
| smc_breaker_block_bullish | 13.5% |
| smc_choch_bearish | 10.9% |
| smc_choch_bullish | 1.5% |
| smc_equal_highs_swept | 1.1% |
| smc_equal_lows_swept | 8.2% |
| smc_fvg_bearish_active | 41.3% |
| smc_fvg_bullish_active | 46.4% |
| smc_fvg_retest_long_zone | 0.5% |
| smc_fvg_retest_short_zone | 21.2% |
| smc_in_discount_zone | 84.8% |
| smc_in_premium_zone | 48.6% |
| smc_inverse_fvg_bearish | 96.1% |
| smc_inverse_fvg_bullish | 84.1% |
| smc_liquidity_swept_dn | 0.5% |
| smc_liquidity_swept_up | 2.4% |
| smc_mitigation_block_long | 0.1% |
| smc_mitigation_block_short | 1.1% |
| smc_ob_bearish_active | 65.1% |
| smc_ob_bullish_active | 9.1% |
| smc_ote_long_zone | 11.1% |
| smc_ote_short_zone | 1.1% |
| stoch_bearish_cross | 2.5% |
| stoch_broad_overbought | 8.7% |
| stoch_broad_oversold | 3.4% |
| stoch_bullish_cross | 20.3% |
| stoch_overbought | 5.3% |
| stoch_oversold | 0.4% |
| stochrsi_cross_dn | 11.6% |
| stochrsi_cross_up | 36.4% |
| stochrsi_overbought | 52.8% |
| stochrsi_oversold | 5.5% |
| supertrend_bearish | 0.4% |
| supertrend_bullish | 99.6% |
| supertrend_flip_recent_long_5d | 6.3% |
| supertrend_flip_recent_short_5d | 4.6% |
| supertrend_flip_up | 2.6% |
| support_break_retest | 11.4% |
| tema_above_dema | 50.4% |
| tema_cross_dn | 0.5% |
| tema_cross_up | 11.0% |
| three_white_soldiers | 13.8% |
| triangle_apex_break_retest_long | 5.2% |
| triangle_ascending_detected | 3.7% |
| triangle_descending_detected | 7.8% |
| uo_overbought | 0.5% |
| usd_strengthening | 20.2% |
| usd_weakening | 12.9% |
| vix_band_high | 56.2% |
| vix_band_low | 23.8% |
| vix_band_mid | 20.0% |
| vix_term_backwardation | 22.9% |
| vix_term_contango | 77.1% |
| vol_above_avg | 41.5% |
| vol_below_avg | 58.5% |
| vol_spike_12x | 29.3% |
| vol_spike_15x | 19.3% |
| vol_spike_17x | 14.2% |
| vol_spike_2x | 7.8% |
| vol_spike_2x_on_down_day_recent_3d | 4.9% |
| vol_spike_2x_on_up_day_recent_3d | 4.9% |
| vol_spike_3x | 1.4% |
| vp_above_value_area | 6.0% |
| vp_below_value_area | 20.9% |
| vp_close_above_poc | 36.8% |
| vp_close_below_poc | 63.2% |
| vp_in_value_area | 73.2% |
| week_open_gap_down_15pct | 0.6% |
| week_open_gap_up_15pct | 2.6% |
| weekly_above_ema_10 | 26.6% |
| weekly_above_ema_20 | 16.7% |
| weekly_bias_bear | 72.0% |
| weekly_bias_bull | 15.3% |
| weekly_momentum_pos | 38.8% |
| williams_r_overbought | 27.8% |
| williams_r_oversold | 0.3% |
| williams_r_rising | 95.4% |
| within_pead_window | 36.4% |
| within_post_deletion_window | 6.6% |
| within_post_inclusion_window | 1.4% |
| xs_avoid_high_ivol | 66.9% |
| xs_avoid_high_max | 65.3% |
| xs_high_beta_decile | 28.4% |
| xs_low_beta_bottom_quintile | 28.4% |
| xs_low_beta_decile | 12.8% |
| xs_low_beta_decile_entry_recent_5d | 0.4% |
| xs_low_beta_top_quintile | 12.8% |
| xs_momentum_bottom_decile | 19.5% |
| xs_momentum_bottom_quintile | 33.4% |
| xs_momentum_top_decile | 5.0% |
| xs_momentum_top_quintile | 11.2% |
| xs_quality_bottom_quintile | 24.0% |
| xs_quality_top_quintile | 19.7% |
| xs_quality_top_tercile | 37.2% |
| year_low_break_retest_short | 2.6% |
| yoy_surprise_high | 41.2% |
| yoy_surprise_negative | 48.8% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 90.6% |
| committed_growth_holders | 90.6% |
| corp_donations_1y | 5.3% |
| corp_donations_count_1y | 5.3% |
| corp_donations_unique_pacs | 5.3% |
| cot_rut_commercials_pctile_3y | 55.7% |
| cot_rut_mmoney_pctile_3y | 55.7% |
| cup_handle_depth_pct | 19.0% |
| days_since_classification_change | 0.4% |
| days_since_deletion | 9.3% |
| days_since_inclusion | 13.0% |
| days_to_next_holiday | 70.2% |
| days_to_rebalance | 12.8% |
| dpi_30d_avg | 95.4% |
| dpi_recent | 95.4% |
| earnings_announcement_return | 89.9% |
| earnings_eps_yoy_growth | 93.3% |
| flag_bear_pole_move_pct | 0.9% |
| gov_contracts_4q_sum | 40.9% |
| gov_contracts_last_qtr_amount | 40.9% |
| gov_contracts_qoq_growth | 40.9% |
| head_shoulders_magnitude_pct | 6.4% |
| insider_director_buyers_30d | 9.9% |
| insider_officer_buyers_30d | 9.9% |
| insider_total_shares_bought_30d | 9.9% |
| insider_unique_buyers_30d | 9.9% |
| inverted_cup_handle_height_pct | 16.0% |
| lobbying_amount_1y | 69.6% |
| lobbying_amount_q | 69.6% |
| lobbying_amount_yoy | 69.6% |
| otc_short_ratio_recent | 95.4% |
| otc_volume_recent | 95.4% |
| pair_half_life | 92.2% |
| pair_max_abs_zscore | 92.2% |
| pair_zscore_signed | 92.2% |
| pct_from_avwap_20high | 97.5% |
| pct_from_avwap_20low | 97.0% |
| pct_from_avwap_252low | 97.2% |
| pct_from_avwap_50low | 97.2% |
| persistent_holders_4q | 90.6% |
| persistent_holders_8q | 90.6% |
| sc_13g_latest_percent_owned | 1.3% |
| search_volume_index_recent | 77.5% |
| search_volume_observations | 77.5% |
| search_volume_zscore_30d | 77.5% |
| sector_etf_return_20d | 2.9% |
| spy_return_20d | 2.9% |
| total_active_holders | 90.6% |
| triangle_breakdown_pct | 7.8% |
| triangle_breakout_pct | 3.7% |
| xs_quality_decile | 59.2% |
| xs_quality_gross_profitability | 59.2% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (1.0), `avwap_20low` (0.999), `avwap_252low` (0.996), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.998), `cam_s2` (0.998), `cam_s3` (0.998), `cam_s4` (0.998), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.997), `dc10_lower` (0.998), `dc10_mid` (0.999), `dc10_upper` (1.0), `dc20_lower` (0.998), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.997), `double_bottom_trough` (0.998), `double_top_neckline` (0.994), `double_top_peak` (0.996), `entry_stop_long` (0.999), `entry_stop_short` (0.999), `fib_236` (0.996), `fib_382` (0.997), `fib_500` (0.998), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.991), `fib_ext_162` (0.987), `flag_bear_breakdown_level` (1.0), `head_shoulders_bottom_neckline` (1.0), `head_shoulders_top_neckline` (0.996), `hull_ma` (0.999), `ichi_kijun` (0.999), `ichi_senkou_a` (0.995), `ichi_senkou_b` (0.992), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.987), `monthly_sma_6` (0.996), `pivot` (0.999), `prev_close` (0.998), `prev_high` (0.999), `prev_low` (0.998), `psar_value` (0.997), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.998), `s2` (0.997), `s3` (0.996), `supertrend_value` (0.995), `swing_high` (0.994), `swing_low` (0.997), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.996), `vp_value_area_low` (0.997), `weekly_close` (1.0), `weekly_ema_10` (0.999), `weekly_ema_20` (0.997), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.998), `year_high` (0.97), `year_low` (0.977)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P1.1 | squeeze definition: Keltner multiplier ( | 3 | MIXED - offline AND pending levels | no - production only; 1 offline; 1 pending (DEFINED-NO-ACTUATOR) | 1 | 1 | 1 |
| P1.2 | squeeze definition: Bollinger std multip | 3 | MIXED - offline AND pending levels | no - production only; 1 offline; 1 pending (DEFINED-NO-ACTUATOR) | 1 | 1 | 1 |
| P1.3 | momentum window (close vs the N-bar high | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P1.4 | Keltner EMA / ATR period | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P1.5 | [NEW-GATE] prior squeeze: in a squeeze o | 4 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 3 |

```
FULL FACTORIAL     3 x 3 x 3 x 3 x 4 = 324
offline gradings   3 level-combinations x 24 exits = 72 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  320 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 3 + 320 = 324 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 603 census axes join it only when REGISTERED at the T3 band review.
