# Table A - vix_backwardation_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit e29a15af2 at 2026-09-17 17:07:43 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** cross_asset | **status:** NOT-STARTED | **R5 fires:** 543 | **surviving fires (T1):** 543 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  vix_term_backwardation  <- backtest/signals/cross_asset.py +1
       DEFN: VIX close above VIX3M close - term-structure stress (cross_asset.py:216-231)
       knobs P1.1-P1.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P2  xs_quality_decile >= 7   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_vix_backwardation_long (docstring and return dropped):

```python
fires = s.get('vix_term_backwardation', False) and s.get('xs_quality_decile', 0) >= 7
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
| P1 | PRODUCER | vix_term_backwardation - emitted by backtest/signals/cross_asset.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | VIX close above VIX3M close - term-structure stress (cross_asset.py:216-231) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | backwardation margin (VIX over VIX3M) - backtest/signals/cross_asset.py:216-231 | BRACKET zero (strict > today) | 0.0 | [0, 2, 5] pct | none - vix3m is not persisted per-fire | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | STRATEGY | xs_quality_decile `>= 7` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `>= 7` | production + 3 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| xs_quality_decile | backtest/signals/cross_sectional.py +1 | `>= 7` | 100.0% | TIGHTER = RAISE the floor: 8 -> 414 (76%); 9 -> 282 (52%); 10 -> 140 (26%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 18.364, 23.04, 28.374, 34.686 | 18.364: 434 (80%); 23.04: 326 (60%); 28.374: 217 (40%); 34.686: 109 (20%) | 18.364: 109 (20%); 23.04: 217 (40%); 28.374: 326 (60%); 34.686: 434 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 24.684, 28.604, 31.334, 36.072 | 24.684: 434 (80%); 28.604: 326 (60%); 31.334: 217 (40%); 36.072: 109 (20%) | 24.684: 109 (20%); 28.604: 217 (40%); 31.334: 326 (60%); 36.072: 434 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 12.852, 15.296, 17.84, 20.828 | 12.852: 434 (80%); 15.296: 326 (60%); 17.84: 218 (40%); 20.828: 109 (20%) | 12.852: 109 (20%); 15.296: 217 (40%); 17.84: 329 (61%); 20.828: 434 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -17.6347, -9.8283, -5.2364, -1.4083 | -17.6347: 434 (80%); -9.8283: 326 (60%); -5.2364: 217 (40%); -1.4083: 109 (20%) | -17.6347: 109 (20%); -9.8283: 217 (40%); -5.2364: 326 (60%); -1.4083: 434 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 2.2039, 3.8841, 5.8732, 9.7612 | 2.2039: 434 (80%); 3.8841: 326 (60%); 5.8732: 217 (40%); 9.7612: 109 (20%) | 2.2039: 109 (20%); 3.8841: 217 (40%); 5.8732: 326 (60%); 9.7612: 434 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 2.2039, 3.8841, 5.8732, 9.7612 | 2.2039: 434 (80%); 3.8841: 326 (60%); 5.8732: 217 (40%); 9.7612: 109 (20%) | 2.2039: 109 (20%); 3.8841: 217 (40%); 5.8732: 326 (60%); 9.7612: 434 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.9546, 3.668, 4.5622, 5.6688 | 2.9546: 434 (80%); 3.668: 326 (60%); 4.5622: 217 (40%); 5.6688: 109 (20%) | 2.9546: 109 (20%); 3.668: 217 (40%); 4.5622: 326 (60%); 5.6688: 434 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0896, 0.1256, 0.1712, 0.2375 | 0.0896: 435 (80%); 0.1256: 326 (60%); 0.1712: 217 (40%); 0.2375: 109 (20%) | 0.0896: 109 (20%); 0.1256: 219 (40%); 0.1712: 326 (60%); 0.2375: 435 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.1505, 0.2486, 0.4006, 0.5522 | 0.1505: 434 (80%); 0.2486: 326 (60%); 0.4006: 217 (40%); 0.5522: 109 (20%) | 0.1505: 109 (20%); 0.2486: 217 (40%); 0.4006: 326 (60%); 0.5522: 434 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.085, 0.1171, 0.1465, 0.2023 | 0.085: 435 (80%); 0.1171: 326 (60%); 0.1465: 218 (40%); 0.2023: 109 (20%) | 0.085: 109 (20%); 0.1171: 218 (40%); 0.1465: 327 (60%); 0.2023: 435 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.0933, 0.1087, 0.2358, 0.4185 | -0.0933: 434 (80%); 0.1087: 326 (60%); 0.2358: 217 (40%); 0.4185: 109 (20%) | -0.0933: 109 (20%); 0.1087: 217 (40%); 0.2358: 326 (60%); 0.4185: 434 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.1134, 0.1561, 0.1953, 0.2697 | 0.1134: 434 (80%); 0.1561: 326 (60%); 0.1953: 218 (40%); 0.2697: 109 (20%) | 0.1134: 109 (20%); 0.1561: 218 (40%); 0.1953: 327 (60%); 0.2697: 435 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.0551, 0.2066, 0.3018, 0.4389 | 0.0551: 434 (80%); 0.2066: 326 (60%); 0.3018: 217 (40%); 0.4389: 109 (20%) | 0.0551: 109 (20%); 0.2066: 217 (40%); 0.3018: 326 (60%); 0.4389: 434 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | 0.0075, 0.0159, 0.0379, 0.0992 | 0.0075: 459 (85%); 0.0159: 326 (60%); 0.0379: 236 (43%); 0.0992: 111 (20%) | 0.0075: 176 (32%); 0.0159: 226 (42%); 0.0379: 333 (61%); 0.0992: 482 (89%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1521, 0.162, 0.1627, 0.1785 | 0.1521: 431 (79%); 0.162: 274 (50%); 0.1627: 256 (47%); 0.1785: 158 (29%) | 0.1521: 112 (21%); 0.162: 269 (50%); 0.1627: 287 (53%); 0.1785: 385 (71%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 543 (100%) | 0: 502 (92%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1073, -0.0315, 0.0432, 0.1121 | -0.1073: 435 (80%); -0.0315: 326 (60%); 0.0432: 217 (40%); 0.1121: 109 (20%) | -0.1073: 110 (20%); -0.0315: 217 (40%); 0.0432: 326 (60%); 0.1121: 434 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 543 (100%); 1: 120 (22%) | 0: 423 (78%); 1: 495 (91%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2152, -0.1433, -0.1296, -0.1141 | -0.2152: 435 (80%); -0.1433: 339 (62%); -0.1296: 233 (43%); -0.1141: 153 (28%) | -0.2152: 110 (20%); -0.1433: 223 (41%); -0.1296: 345 (64%); -0.1141: 525 (97%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4167, 0.6474, 0.7244, 0.7692 | 0.4167: 435 (80%); 0.6474: 343 (63%); 0.7244: 242 (45%); 0.7692: 146 (27%) | 0.4167: 110 (20%); 0.6474: 219 (40%); 0.7244: 337 (62%); 0.7692: 532 (98%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.5, 0.5897, 0.6795, 0.8269 | 0.5: 448 (83%); 0.5897: 398 (73%); 0.6795: 235 (43%); 0.8269: 175 (32%) | 0.5: 135 (25%); 0.5897: 280 (52%); 0.6795: 335 (62%); 0.8269: 446 (82%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0304, 0.0117, 0.0167 | -0.0304: 459 (85%); 0.0117: 361 (66%); 0.0167: 242 (45%) | -0.0304: 111 (20%); 0.0117: 260 (48%); 0.0167: 436 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4487, 0.4679, 0.4872, 0.5385 | 0.4487: 455 (84%); 0.4679: 395 (73%); 0.4872: 308 (57%); 0.5385: 128 (24%) | 0.4487: 148 (27%); 0.4679: 235 (43%); 0.4872: 370 (68%); 0.5385: 463 (85%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.3526, 0.3782, 0.4551, 0.5897 | 0.3526: 437 (80%); 0.3782: 331 (61%); 0.4551: 250 (46%); 0.5897: 115 (21%) | 0.3526: 212 (39%); 0.3782: 252 (46%); 0.4551: 428 (79%); 0.5897: 435 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.4608, -0.0978, -0.0869, 0.0029 | -0.4608: 458 (84%); -0.0978: 363 (67%); -0.0869: 285 (52%); 0.0029: 113 (21%) | -0.4608: 120 (22%); -0.0978: 258 (48%); -0.0869: 393 (72%); 0.0029: 457 (84%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3974, 0.6795, 0.8205 | 0.3974: 447 (82%); 0.6795: 367 (68%); 0.8205: 315 (58%) | 0.3974: 123 (23%); 0.6795: 224 (41%); 0.8205: 441 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.3205, 0.7244, 0.8526, 0.9167 | 0.3205: 449 (83%); 0.7244: 345 (64%); 0.8526: 265 (49%); 0.9167: 129 (24%) | 0.3205: 121 (22%); 0.7244: 276 (51%); 0.8526: 413 (76%); 0.9167: 454 (84%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0416, 0 | -0.0416: 464 (85%); 0: 358 (66%) | -0.0416: 114 (21%); 0: 537 (99%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4679, 0.9936, 1 | 0.4679: 459 (85%); 0.9936: 358 (66%); 1: 325 (60%) | 0.4679: 132 (24%); 0.9936: 218 (40%); 1: 543 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2372, 0.3205, 0.5705 | 0.2372: 437 (80%); 0.3205: 345 (64%); 0.5705: 116 (21%) | 0.2372: 110 (20%); 0.3205: 333 (61%); 0.5705: 445 (82%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0911, 0.179, 0.2489, 0.39 | 0.0911: 469 (86%); 0.179: 335 (62%); 0.2489: 263 (48%); 0.39: 115 (21%) | 0.0911: 152 (28%); 0.179: 235 (43%); 0.2489: 415 (76%); 0.39: 444 (82%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.7692, 0.9615, 0.9744, 0.9872 | 0.7692: 469 (86%); 0.9615: 343 (63%); 0.9744: 290 (53%); 0.9872: 120 (22%) | 0.7692: 152 (28%); 0.9615: 231 (43%); 0.9744: 388 (71%); 0.9872: 471 (87%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0641, 0.2051, 0.2949, 0.4295 | 0.0641: 463 (85%); 0.2051: 330 (61%); 0.2949: 297 (55%); 0.4295: 153 (28%) | 0.0641: 128 (24%); 0.2051: 219 (40%); 0.2949: 381 (70%); 0.4295: 468 (86%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.3493, -0.0473, 0.1182, 0.2205 | -0.3493: 498 (92%); -0.0473: 361 (66%); 0.1182: 220 (41%); 0.2205: 113 (21%) | -0.3493: 180 (33%); -0.0473: 220 (41%); 0.1182: 333 (61%); 0.2205: 436 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.3459, -0.033, 0.068, 0.1667 | -0.3459: 466 (86%); -0.033: 326 (60%); 0.068: 242 (45%); 0.1667: 177 (33%) | -0.3459: 212 (39%); -0.033: 217 (40%); 0.068: 336 (62%); 0.1667: 444 (82%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.5449, 0.8013, 1 | 0.2628: 466 (86%); 0.5449: 331 (61%); 0.8013: 225 (41%); 1: 130 (24%) | 0.2628: 212 (39%); 0.5449: 241 (44%); 0.8013: 334 (62%); 1: 543 (100%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2115, 0.2308, 0.5641 | 0.2115: 436 (80%); 0.2308: 358 (66%); 0.5641: 246 (45%) | 0.2115: 185 (34%); 0.2308: 220 (41%); 0.5641: 451 (83%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.12, 0.2926, 0.5136, 1.0263 | 0.12: 435 (80%); 0.2926: 326 (60%); 0.5136: 217 (40%); 1.0263: 109 (20%) | 0.12: 110 (20%); 0.2926: 217 (40%); 0.5136: 326 (60%); 1.0263: 434 (80%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.1% | 1.7333, 2.2287, 2.7384, 3.7249 | 1.7333: 430 (79%); 2.2287: 324 (60%); 2.7384: 217 (40%); 3.7249: 108 (20%) | 1.7333: 108 (20%); 2.2287: 217 (40%); 2.7384: 324 (60%); 3.7249: 430 (79%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 15, 22, 28, 33.6 | 15: 437 (80%); 22: 364 (67%); 28: 280 (52%); 33.6: 109 (20%) | 15: 145 (27%); 22: 220 (41%); 28: 355 (65%); 33.6: 434 (80%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 0, 1, 2, 3 | 0: 543 (100%); 1: 382 (70%); 2: 273 (50%); 3: 137 (25%) | 0: 161 (30%); 1: 270 (50%); 2: 406 (75%); 3: 479 (88%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0286, -0.0018, -0.0011, 0.0174 | -0.0286: 436 (80%); -0.0018: 331 (61%); -0.0011: 323 (59%); 0.0174: 110 (20%) | -0.0286: 113 (21%); -0.0018: 220 (41%); -0.0011: 362 (67%); 0.0174: 446 (82%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 26.4178, 27.3094, 27.3557, 27.4718 | 26.4178: 439 (81%); 27.3094: 326 (60%); 27.3557: 308 (57%); 27.4718: 110 (20%) | 26.4178: 110 (20%); 27.3094: 217 (40%); 27.3557: 327 (60%); 27.4718: 439 (81%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.257, 0.3918, 1.136, 2.3736 | -0.257: 434 (80%); 0.3918: 326 (60%); 1.136: 217 (40%); 2.3736: 109 (20%) | -0.257: 109 (20%); 0.3918: 217 (40%); 1.136: 326 (60%); 2.3736: 434 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -2.3736, -1.136, -0.3918, 0.257 | -2.3736: 434 (80%); -1.136: 326 (60%); -0.3918: 217 (40%); 0.257: 109 (20%) | -2.3736: 109 (20%); -1.136: 217 (40%); -0.3918: 326 (60%); 0.257: 434 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | 0.0021, 0.0684, 0.1226, 0.1369 | 0.0021: 437 (80%); 0.0684: 326 (60%); 0.1226: 219 (40%); 0.1369: 199 (37%) | 0.0021: 125 (23%); 0.0684: 217 (40%); 0.1226: 333 (61%); 0.1369: 436 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.44, 8.957, 10.0851, 10.1703 | 8.44: 435 (80%); 8.957: 325 (60%); 10.0851: 229 (42%); 10.1703: 175 (32%) | 8.44: 108 (20%); 8.957: 218 (40%); 10.0851: 314 (58%); 10.1703: 368 (68%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1, 2 | 0: 538 (99%); 1: 274 (50%); 2: 144 (27%) | 0: 264 (49%); 1: 394 (73%); 2: 445 (82%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.1% | -1, 0, 1 | -1: 477 (88%); 0: 394 (73%); 1: 113 (21%) | -1: 144 (27%); 0: 425 (78%); 1: 489 (90%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1, 2 | 0: 538 (99%); 1: 293 (54%); 2: 148 (27%) | 0: 245 (45%); 1: 390 (72%); 2: 450 (83%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 5, 17.4, 215.6, 323.6 | 5: 437 (80%); 17.4: 326 (60%); 215.6: 217 (40%); 323.6: 109 (20%) | 5: 116 (21%); 17.4: 217 (40%); 215.6: 326 (60%); 323.6: 434 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 2, 72.8, 132.2, 177.6 | 2: 443 (82%); 72.8: 326 (60%); 132.2: 217 (40%); 177.6: 109 (20%) | 2: 110 (20%); 72.8: 217 (40%); 132.2: 326 (60%); 177.6: 434 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -1.4655, -0.6221, -0.2139, 0.1444 | -1.4655: 434 (80%); -0.6221: 326 (60%); -0.2139: 217 (40%); 0.1444: 109 (20%) | -1.4655: 109 (20%); -0.6221: 217 (40%); -0.2139: 326 (60%); 0.1444: 434 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -6.9045, -4.0427, -2.0227, -0.592 | -6.9045: 434 (80%); -4.0427: 326 (60%); -2.0227: 217 (40%); -0.592: 109 (20%) | -6.9045: 109 (20%); -4.0427: 217 (40%); -2.0227: 326 (60%); -0.592: 434 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -6.4577, -3.4658, -1.5598, -0.2382 | -6.4577: 434 (80%); -3.4658: 326 (60%); -1.5598: 217 (40%); -0.2382: 109 (20%) | -6.4577: 109 (20%); -3.4658: 217 (40%); -1.5598: 326 (60%); -0.2382: 434 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -1.0596, -0.428, -0.059, 0.2931 | -1.0596: 434 (80%); -0.428: 326 (60%); -0.059: 217 (40%); 0.2931: 109 (20%) | -1.0596: 109 (20%); -0.428: 217 (40%); -0.059: 326 (60%); 0.2931: 434 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -7.4379, -4.2437, -2.3123, -0.8207 | -7.4379: 434 (80%); -4.2437: 326 (60%); -2.3123: 217 (40%); -0.8207: 109 (20%) | -7.4379: 109 (20%); -4.2437: 217 (40%); -2.3123: 326 (60%); -0.8207: 434 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -6.8791, -4.0707, -1.9741, -0.5793 | -6.8791: 434 (80%); -4.0707: 326 (60%); -1.9741: 217 (40%); -0.5793: 109 (20%) | -6.8791: 109 (20%); -4.0707: 217 (40%); -1.9741: 326 (60%); -0.5793: 434 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 30.844, 36.874, 43.006, 50.678 | 30.844: 434 (80%); 36.874: 326 (60%); 43.006: 217 (40%); 50.678: 109 (20%) | 30.844: 109 (20%); 36.874: 217 (40%); 43.006: 326 (60%); 50.678: 434 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 100.0% | -0.2679, -0.1658, -0.0822, 0.0243 | -0.2679: 434 (80%); -0.1658: 326 (60%); -0.0822: 217 (40%); 0.0243: 109 (20%) | -0.2679: 109 (20%); -0.1658: 218 (40%); -0.0822: 326 (60%); 0.0243: 434 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 100.0% | 0.0081, 0.021, 0.0423, 0.0942 | 0.0081: 434 (80%); 0.021: 325 (60%); 0.0423: 217 (40%); 0.0942: 109 (20%) | 0.0081: 109 (20%); 0.021: 218 (40%); 0.0423: 326 (60%); 0.0942: 434 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 2, 6 | 0: 543 (100%); 1: 365 (67%); 2: 253 (47%); 6: 114 (21%) | 0: 178 (33%); 1: 290 (53%); 2: 339 (62%); 6: 443 (82%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.197 | 0: 543 (100%); 0.197: 109 (20%) | 0: 376 (69%); 0.197: 434 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.4507, 1 | 0: 543 (100%); 0.4507: 217 (40%); 1: 111 (20%) | 0: 248 (46%); 0.4507: 326 (60%); 1: 543 (100%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 4 | 0: 543 (100%); 1: 321 (59%); 4: 127 (23%) | 0: 222 (41%); 1: 327 (60%); 4: 441 (81%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 6 | 0: 543 (100%); 1: 365 (67%); 2: 253 (47%); 6: 114 (21%) | 0: 178 (33%); 1: 290 (53%); 2: 339 (62%); 6: 443 (82%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 5 | 0: 543 (100%); 2: 221 (41%); 5: 115 (21%) | 0: 234 (43%); 2: 372 (69%); 5: 436 (80%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1345, 0.4547, 0.8333 | 0: 468 (86%); 0.1345: 326 (60%); 0.4547: 217 (40%); 0.8333: 110 (20%) | 0: 193 (36%); 0.1345: 217 (40%); 0.4547: 326 (60%); 0.8333: 435 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.7094 | 0: 499 (92%); 0.7094: 109 (20%) | 0: 328 (60%); 0.7094: 434 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2671, 1 | 0: 489 (90%); 0.2671: 217 (40%); 1: 110 (20%) | 0: 280 (52%); 0.2671: 326 (60%); 1: 543 (100%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2671, 1 | 0: 489 (90%); 0.2671: 217 (40%); 1: 110 (20%) | 0: 280 (52%); 0.2671: 326 (60%); 1: 543 (100%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.0043, 0 | -0.0043: 434 (80%); 0: 433 (80%) | -0.0043: 109 (20%); 0: 436 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.6461, -0.4472, 0, 0.7676 | -0.6461: 442 (81%); -0.4472: 384 (71%); 0: 278 (51%); 0.7676: 109 (20%) | -0.6461: 129 (24%); -0.4472: 223 (41%); 0: 369 (68%); 0.7676: 434 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 11 | 2: 445 (82%); 4: 339 (62%); 7: 221 (41%); 11: 117 (22%) | 2: 148 (27%); 4: 253 (47%); 7: 349 (64%); 11: 454 (84%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.1074, -0.067, -0.0358, -0.0019 | -0.1074: 434 (80%); -0.067: 326 (60%); -0.0358: 217 (40%); -0.0019: 109 (20%) | -0.1074: 109 (20%); -0.067: 217 (40%); -0.0358: 326 (60%); -0.0019: 434 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.1463, -0.0962, -0.0571, -0.009 | -0.1463: 434 (80%); -0.0962: 326 (60%); -0.0571: 217 (40%); -0.009: 109 (20%) | -0.1463: 109 (20%); -0.0962: 217 (40%); -0.0571: 326 (60%); -0.009: 434 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0821, -0.0509, -0.0287, 0.0062 | -0.0821: 434 (80%); -0.0509: 326 (60%); -0.0287: 217 (40%); 0.0062: 109 (20%) | -0.0821: 109 (20%); -0.0509: 217 (40%); -0.0287: 326 (60%); 0.0062: 434 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -33.6184, -14.1616, 2.7144, 25.0064 | -33.6184: 434 (80%); -14.1616: 326 (60%); 2.7144: 217 (40%); 25.0064: 109 (20%) | -33.6184: 109 (20%); -14.1616: 217 (40%); 2.7144: 326 (60%); 25.0064: 434 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0672, 0.0981, 0.1268, 0.1737 | 0.0672: 435 (80%); 0.0981: 326 (60%); 0.1268: 217 (40%); 0.1737: 110 (20%) | 0.0672: 110 (20%); 0.0981: 218 (40%); 0.1268: 326 (60%); 0.1737: 435 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.5457, 0.6992, 0.8297, 0.9238 | 0.5457: 436 (80%); 0.6992: 326 (60%); 0.8297: 217 (40%); 0.9238: 109 (20%) | 0.5457: 110 (20%); 0.6992: 217 (40%); 0.8297: 326 (60%); 0.9238: 435 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -4.7844, -3.179, -1.9408, -0.7289 | -4.7844: 434 (80%); -3.179: 326 (60%); -1.9408: 217 (40%); -0.7289: 109 (20%) | -4.7844: 109 (20%); -3.179: 217 (40%); -1.9408: 326 (60%); -0.7289: 434 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -1.1656, -0.6034, -0.2758, 0.0808 | -1.1656: 434 (80%); -0.6034: 326 (60%); -0.2758: 217 (40%); 0.0808: 109 (20%) | -1.1656: 109 (20%); -0.6034: 217 (40%); -0.2758: 326 (60%); 0.0808: 434 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -4.2114, -2.8363, -1.6165, -0.2623 | -4.2114: 434 (80%); -2.8363: 326 (60%); -1.6165: 217 (40%); -0.2623: 109 (20%) | -4.2114: 109 (20%); -2.8363: 217 (40%); -1.6165: 326 (60%); -0.2623: 434 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -11.2246, -6.9216, -4.233, -1.0364 | -11.2246: 434 (80%); -6.9216: 326 (60%); -4.233: 217 (40%); -1.0364: 109 (20%) | -11.2246: 109 (20%); -6.9216: 217 (40%); -4.233: 326 (60%); -1.0364: 434 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 33.19, 38.046, 42.654, 46.536 | 33.19: 435 (80%); 38.046: 326 (60%); 42.654: 217 (40%); 46.536: 109 (20%) | 33.19: 110 (20%); 38.046: 217 (40%); 42.654: 326 (60%); 46.536: 434 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 14.552, 40.236, 60.374, 73.83 | 14.552: 434 (80%); 40.236: 326 (60%); 60.374: 217 (40%); 73.83: 109 (20%) | 14.552: 109 (20%); 40.236: 217 (40%); 60.374: 326 (60%); 73.83: 434 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 35.586, 39.55, 43.062, 46.536 | 35.586: 434 (80%); 39.55: 326 (60%); 43.062: 217 (40%); 46.536: 109 (20%) | 35.586: 109 (20%); 39.55: 217 (40%); 43.062: 326 (60%); 46.536: 434 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 29.944, 37.146, 42.458, 47.914 | 29.944: 434 (80%); 37.146: 326 (60%); 42.458: 217 (40%); 47.914: 109 (20%) | 29.944: 109 (20%); 37.146: 217 (40%); 42.458: 326 (60%); 47.914: 434 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0395, 0.0624, 0.0911, 0.1173 | 0.0395: 437 (80%); 0.0624: 328 (60%); 0.0911: 219 (40%); 0.1173: 110 (20%) | 0.0395: 156 (29%); 0.0624: 224 (41%); 0.0911: 330 (61%); 0.1173: 451 (83%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0698, -0.054, -0.0434, -0.0406 | -0.0698: 439 (81%); -0.054: 326 (60%); -0.0434: 263 (48%); -0.0406: 109 (20%) | -0.0698: 129 (24%); -0.054: 217 (40%); -0.0434: 372 (69%); -0.0406: 438 (81%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1, 3 | 0: 543 (100%); 1: 222 (41%); 3: 120 (22%) | 0: 321 (59%); 1: 379 (70%); 3: 436 (80%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.1% | 59, 65, 66 | 59: 434 (80%); 65: 369 (68%); 66: 148 (27%) | 59: 117 (22%); 65: 390 (72%); 66: 433 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.9% | 0.0134, 0.0212, 0.0319, 0.0492 | 0.0134: 429 (79%); 0.0212: 322 (59%); 0.0319: 213 (39%); 0.0492: 108 (20%) | 0.0134: 108 (20%); 0.0212: 215 (40%); 0.0319: 324 (60%); 0.0492: 429 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.1048, 0.1692, 0.2575, 0.3983 | 0.1048: 434 (80%); 0.1692: 326 (60%); 0.2575: 218 (40%); 0.3983: 109 (20%) | 0.1048: 109 (20%); 0.1692: 217 (40%); 0.2575: 326 (60%); 0.3983: 434 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 44.24, 86.58, 123.38, 160.24 | 44.24: 434 (80%); 86.58: 326 (60%); 123.38: 217 (40%); 160.24: 109 (20%) | 44.24: 109 (20%); 86.58: 217 (40%); 123.38: 326 (60%); 160.24: 434 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -10.218, -4.626, -1.879, 0.651 | -10.218: 434 (80%); -4.626: 326 (60%); -1.879: 217 (40%); 0.651: 109 (20%) | -10.218: 109 (20%); -4.626: 217 (40%); -1.879: 326 (60%); 0.651: 434 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 15.008, 21.698, 30.016, 44.62 | 15.008: 434 (80%); 21.698: 326 (60%); 30.016: 217 (40%); 44.62: 109 (20%) | 15.008: 109 (20%); 21.698: 217 (40%); 30.016: 326 (60%); 44.62: 434 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 13.416, 21.378, 31.412, 43.886 | 13.416: 434 (80%); 21.378: 326 (60%); 31.412: 217 (40%); 43.886: 109 (20%) | 13.416: 109 (20%); 21.378: 217 (40%); 31.412: 326 (60%); 43.886: 434 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 10.386, 23.212, 42.942, 68.728 | 10.386: 434 (80%); 23.212: 326 (60%); 42.942: 217 (40%); 68.728: 109 (20%) | 10.386: 109 (20%); 23.212: 217 (40%); 42.942: 326 (60%); 68.728: 434 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 10.068, 32.808, 54.896, 78.11 | 10.068: 434 (80%); 32.808: 326 (60%); 54.896: 217 (40%); 78.11: 109 (20%) | 10.068: 109 (20%); 32.808: 217 (40%); 54.896: 326 (60%); 78.11: 434 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 6, 7, 13 | 4: 453 (83%); 6: 351 (65%); 7: 322 (59%); 13: 120 (22%) | 4: 127 (23%); 6: 221 (41%); 7: 333 (61%); 13: 435 (80%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 8, 15, 17, 18 | 8: 438 (81%); 15: 333 (61%); 17: 218 (40%); 18: 138 (25%) | 8: 121 (22%); 15: 322 (59%); 17: 405 (75%); 18: 446 (82%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 40.786, 45.73, 48.926, 52.936 | 40.786: 434 (80%); 45.73: 327 (60%); 48.926: 217 (40%); 52.936: 109 (20%) | 40.786: 109 (20%); 45.73: 218 (40%); 48.926: 326 (60%); 52.936: 434 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.9325, 0.9643, 0.9841, 0.996 | 0.9325: 456 (84%); 0.9643: 329 (61%); 0.9841: 241 (44%); 0.996: 111 (20%) | 0.9325: 136 (25%); 0.9643: 218 (40%); 0.9841: 419 (77%); 0.996: 447 (82%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 24.69, 29.65, 33.62, 37.56 | 24.69: 444 (82%); 29.65: 327 (60%); 33.62: 238 (44%); 37.56: 124 (23%) | 24.69: 112 (21%); 29.65: 224 (41%); 33.62: 397 (73%); 37.56: 444 (82%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 24.69, 29.65, 33.62, 37.56 | 24.69: 444 (82%); 29.65: 327 (60%); 33.62: 238 (44%); 37.56: 124 (23%) | 24.69: 112 (21%); 29.65: 224 (41%); 33.62: 397 (73%); 37.56: 444 (82%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 1.0081, 1.019, 1.1076, 1.1237 | 1.0081: 445 (82%); 1.019: 329 (61%); 1.1076: 220 (41%); 1.1237: 195 (36%) | 1.0081: 117 (22%); 1.019: 219 (40%); 1.1076: 348 (64%); 1.1237: 440 (81%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.794, 1, 1.24, 1.66 | 0.794: 434 (80%); 1: 328 (60%); 1.24: 218 (40%); 1.66: 112 (21%) | 0.794: 109 (20%); 1: 220 (41%); 1.24: 330 (61%); 1.66: 435 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0284, 0.0574, 0.094, 0.1598 | 0.0284: 434 (80%); 0.0574: 326 (60%); 0.094: 217 (40%); 0.1598: 109 (20%) | 0.0284: 109 (20%); 0.0574: 219 (40%); 0.094: 326 (60%); 0.1598: 434 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 63.3043, 101.4345, 153.6817, 271.9881 | 63.3043: 434 (80%); 101.4345: 326 (60%); 153.6817: 217 (40%); 271.9881: 109 (20%) | 63.3043: 109 (20%); 101.4345: 217 (40%); 153.6817: 326 (60%); 271.9881: 434 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 59.733, 96.6993, 145.4439, 253.4523 | 59.733: 434 (80%); 96.6993: 326 (60%); 145.4439: 217 (40%); 253.4523: 109 (20%) | 59.733: 109 (20%); 96.6993: 217 (40%); 145.4439: 326 (60%); 253.4523: 434 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 56.6408, 91.8979, 138.6134, 232.4447 | 56.6408: 434 (80%); 91.8979: 326 (60%); 138.6134: 217 (40%); 232.4447: 109 (20%) | 56.6408: 109 (20%); 91.8979: 217 (40%); 138.6134: 326 (60%); 232.4447: 434 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 68.2414, 106.9497, 158.8045, 287.1277 | 68.2414: 434 (80%); 106.9497: 326 (60%); 158.8045: 217 (40%); 287.1277: 109 (20%) | 68.2414: 109 (20%); 106.9497: 217 (40%); 158.8045: 326 (60%); 287.1277: 434 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 71.7183, 110.1426, 169.0149, 297.475 | 71.7183: 434 (80%); 110.1426: 326 (60%); 169.0149: 217 (40%); 297.475: 109 (20%) | 71.7183: 109 (20%); 110.1426: 217 (40%); 169.0149: 326 (60%); 297.475: 434 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0, 0.8364 | 0: 543 (100%); 0.8364: 109 (20%) | 0: 413 (76%); 0.8364: 434 (80%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 543 (100%) | 0: 513 (94%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.1307, -0.0873, -0.0541, -0.0119 | -0.1307: 434 (80%); -0.0873: 327 (60%); -0.0541: 217 (40%); -0.0119: 109 (20%) | -0.1307: 109 (20%); -0.0873: 218 (40%); -0.0541: 326 (60%); -0.0119: 435 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -80.424, -71.772, -60.976, -44.152 | -80.424: 434 (80%); -71.772: 326 (60%); -60.976: 217 (40%); -44.152: 109 (20%) | -80.424: 109 (20%); -71.772: 217 (40%); -60.976: 326 (60%); -44.152: 434 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 100.0% | 0.5725, 0.8503, 1.1008, 1.4055 | 0.5725: 434 (80%); 0.8503: 326 (60%); 1.1008: 217 (40%); 1.4055: 109 (20%) | 0.5725: 109 (20%); 0.8503: 217 (40%); 1.1008: 326 (60%); 1.4055: 434 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 100.0% | 4, 6, 8, 10 | 4: 441 (81%); 6: 336 (62%); 8: 250 (46%); 10: 112 (21%) | 4: 156 (29%); 6: 254 (47%); 8: 348 (64%); 10: 543 (100%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 100.0% | 0.2354, 0.2747, 0.3424, 0.4316 | 0.2354: 434 (80%); 0.2747: 326 (60%); 0.3424: 217 (40%); 0.4316: 109 (20%) | 0.2354: 109 (20%); 0.2747: 219 (40%); 0.3424: 326 (60%); 0.4316: 434 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 100.0% | 4, 7, 8, 10 | 4: 463 (85%); 7: 327 (60%); 8: 275 (51%); 10: 113 (21%) | 4: 129 (24%); 7: 268 (49%); 8: 332 (61%); 10: 543 (100%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 100.0% | 0.0277, 0.0387, 0.0579, 0.0951 | 0.0277: 437 (80%); 0.0387: 327 (60%); 0.0579: 219 (40%); 0.0951: 109 (20%) | 0.0277: 110 (20%); 0.0387: 218 (40%); 0.0579: 326 (60%); 0.0951: 434 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 100.0% | 3, 6, 8, 9 | 3: 471 (87%); 6: 342 (63%); 8: 237 (44%); 9: 165 (30%) | 3: 118 (22%); 6: 255 (47%); 8: 378 (70%); 9: 463 (85%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 100.0% | -0.2531, -0.1141, 0.016, 0.2126 | -0.2531: 434 (80%); -0.1141: 326 (60%); 0.016: 217 (40%); 0.2126: 109 (20%) | -0.2531: 109 (20%); -0.1141: 218 (40%); 0.016: 326 (60%); 0.2126: 434 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 100.0% | 1, 3, 5, 8 | 1: 543 (100%); 3: 364 (67%); 5: 242 (45%); 8: 124 (23%) | 1: 113 (21%); 3: 241 (44%); 5: 352 (65%); 8: 448 (83%) | OFFLINE |
| xs_quality_gross_profitability | backtest/signals/cross_sectional.py | 100.0% | 0.0922, 0.1071, 0.1248, 0.1473 | 0.0922: 435 (80%); 0.1071: 329 (61%); 0.1248: 222 (41%); 0.1473: 110 (20%) | 0.0922: 110 (20%); 0.1071: 219 (40%); 0.1248: 326 (60%); 0.1473: 437 (80%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 6.1% |
| 8k_item_5_02_filed_within_7d | 3.3% |
| above_avwap_20high | 21.5% |
| above_avwap_20low | 84.0% |
| above_avwap_252low | 61.7% |
| above_avwap_50low | 75.9% |
| above_cam_r3 | 53.6% |
| above_cam_r4 | 35.0% |
| above_cpr | 65.2% |
| above_pivot | 70.2% |
| above_prev_high | 34.6% |
| above_prev_high_clearance_atr_05 | 11.0% |
| above_prev_low | 89.3% |
| above_r1 | 36.8% |
| above_r2 | 11.8% |
| above_vwap | 43.5% |
| above_wood_p | 60.4% |
| ad_rising | 49.0% |
| adx_cross_up | 2.2% |
| adx_cross_up_20 | 3.7% |
| adx_di_bear | 91.2% |
| adx_di_bull | 8.8% |
| adx_strong | 10.7% |
| adx_trending | 51.9% |
| ao_cross_dn | 3.7% |
| ao_cross_up | 0.6% |
| ao_positive | 11.0% |
| ao_twin_peaks_bull | 6.3% |
| at_key_fib | 8.8% |
| at_key_fib_wide | 24.1% |
| avwap_20high_loss_recent_3d | 15.8% |
| avwap_20high_reclaim_recent_3d | 18.2% |
| avwap_20low_loss_recent_3d | 12.4% |
| avwap_20low_reclaim_recent_3d | 48.5% |
| avwap_252low_loss_recent_3d | 12.0% |
| avwap_252low_reclaim_recent_3d | 23.3% |
| avwap_50low_loss_recent_3d | 14.4% |
| avwap_50low_reclaim_recent_3d | 40.7% |
| bb_10_20_above_mid | 25.6% |
| bb_10_20_expanding | 49.0% |
| bb_10_20_pctb_gt_75 | 8.3% |
| bb_10_20_pctb_gt_8 | 5.2% |
| bb_10_20_pctb_gt_85 | 3.5% |
| bb_10_20_pctb_gt_9 | 2.4% |
| bb_10_20_pctb_gt_95 | 1.7% |
| bb_10_20_pctb_lt_05 | 6.3% |
| bb_10_20_pctb_lt_1 | 11.6% |
| bb_10_20_pctb_lt_15 | 19.9% |
| bb_10_20_pctb_lt_2 | 29.3% |
| bb_10_20_pctb_lt_25 | 40.1% |
| bb_10_20_reclaim_from_lower_recent_3d | 31.7% |
| bb_10_20_reclaim_from_upper_recent_3d | 1.3% |
| bb_10_20_squeeze | 14.7% |
| bb_10_20_touch_lower | 5.2% |
| bb_10_20_touch_upper | 1.7% |
| bb_20_15_above_mid | 15.7% |
| bb_20_15_expanding | 56.0% |
| bb_20_15_pctb_gt_75 | 6.6% |
| bb_20_15_pctb_gt_8 | 6.1% |
| bb_20_15_pctb_gt_85 | 4.8% |
| bb_20_15_pctb_gt_9 | 4.2% |
| bb_20_15_pctb_gt_95 | 3.3% |
| bb_20_15_pctb_lt_05 | 33.7% |
| bb_20_15_pctb_lt_1 | 38.7% |
| bb_20_15_pctb_lt_15 | 47.3% |
| bb_20_15_pctb_lt_2 | 54.7% |
| bb_20_15_pctb_lt_25 | 62.2% |
| bb_20_15_reclaim_from_lower_recent_3d | 35.9% |
| bb_20_15_reclaim_from_upper_recent_3d | 1.5% |
| bb_20_15_squeeze | 16.9% |
| bb_20_15_touch_lower | 32.4% |
| bb_20_15_touch_upper | 3.3% |
| bb_20_20_above_mid | 15.7% |
| bb_20_20_expanding | 56.0% |
| bb_20_20_pctb_gt_75 | 5.3% |
| bb_20_20_pctb_gt_8 | 4.2% |
| bb_20_20_pctb_gt_85 | 2.9% |
| bb_20_20_pctb_gt_9 | 2.8% |
| bb_20_20_pctb_gt_95 | 1.7% |
| bb_20_20_pctb_lt_05 | 19.3% |
| bb_20_20_pctb_lt_1 | 25.0% |
| bb_20_20_pctb_lt_15 | 32.2% |
| bb_20_20_pctb_lt_2 | 38.7% |
| bb_20_20_pctb_lt_25 | 50.1% |
| bb_20_20_reclaim_from_lower_recent_3d | 32.6% |
| bb_20_20_reclaim_from_upper_recent_3d | 1.5% |
| bb_20_20_squeeze | 5.2% |
| bb_20_20_touch_lower | 16.2% |
| bb_20_20_touch_upper | 1.3% |
| bearish_pin_bar | 5.2% |
| below_avwap_20high | 78.5% |
| below_avwap_20low | 16.0% |
| below_avwap_252low | 38.3% |
| below_avwap_50low | 24.1% |
| below_cam_s3 | 12.0% |
| below_cam_s4 | 6.6% |
| below_cpr | 29.8% |
| below_ema_20 | 86.2% |
| below_ema_200 | 82.5% |
| below_ema_200_break_recent_5d | 15.1% |
| below_ema_20_break_recent_5d | 28.0% |
| below_ema_21 | 86.7% |
| below_ema_21_break_recent_5d | 27.6% |
| below_ema_50 | 88.4% |
| below_ema_50_break_recent_5d | 18.8% |
| below_ema_9 | 72.9% |
| below_ema_9_break_recent_5d | 41.3% |
| below_prev_high | 65.2% |
| below_prev_low | 10.3% |
| below_prev_low_clearance_atr_05 | 3.1% |
| below_s1 | 7.7% |
| below_s2 | 2.4% |
| below_sma_20 | 84.3% |
| below_sma_200 | 80.5% |
| below_sma_21 | 84.3% |
| below_sma_50 | 89.0% |
| below_sma_9 | 71.3% |
| below_vwap | 56.5% |
| break_52w_low | 1.3% |
| bullish_engulfing | 22.3% |
| bullish_pin_bar | 4.2% |
| capitulation_recent_3d | 0.6% |
| ceo_buy | 2.2% |
| cfo_buy | 0.7% |
| chandelier_long_bullish | 34.1% |
| chandelier_long_flip_dn | 2.4% |
| chandelier_short_bearish | 87.7% |
| chandelier_short_flip_up | 7.6% |
| close_in_bottom_40pct_of_range | 7.9% |
| close_in_top_40pct_of_range | 74.6% |
| cluster_buy | 0.2% |
| cmf_cross_dn | 1.7% |
| cmf_cross_up | 12.7% |
| cmf_negative | 47.0% |
| cmf_positive | 53.0% |
| concentrated_sell | 7.1% |
| cpr_narrow | 92.4% |
| cpr_narrow_tight | 23.6% |
| cup_handle_detected | 6.4% |
| cup_handle_neckline_break_retest_long | 0.4% |
| dc10_breakout_dn | 8.8% |
| dc10_breakout_dn_1pct | 18.4% |
| dc10_breakout_up | 1.8% |
| dc10_breakout_up_1pct | 3.3% |
| dc10_new_high | 3.5% |
| dc10_strong_breakout_dn | 2.2% |
| dc10_strong_breakout_up | 0.2% |
| dc20_breakout_dn | 7.2% |
| dc20_breakout_up | 1.1% |
| dc20_new_high | 2.0% |
| dc20_resistance_break_retest_strong | 1.3% |
| dc20_support_break_retest_strong | 37.4% |
| defensive_leadership | 92.6% |
| director_only_buy | 4.5% |
| doji | 3.9% |
| double_bottom_detected | 7.4% |
| double_top_detected | 12.5% |
| dpi_elevated | 51.7% |
| drying_volume_on_up_turn | 40.5% |
| ema_20_50_bearish | 83.6% |
| ema_20_50_bullish | 16.4% |
| ema_20_50_death_cross | 1.1% |
| ema_20_50_golden_cross | 0.4% |
| ema_50_200_bearish | 67.4% |
| ema_50_200_bullish | 32.6% |
| ema_50_200_death_cross | 0.9% |
| ema_9_21_bearish | 90.8% |
| ema_9_21_bullish | 9.2% |
| ema_9_21_death_cross | 2.4% |
| ema_9_21_golden_cross | 0.4% |
| flag_bear_break_retest_short | 2.0% |
| flag_bear_broke | 2.0% |
| flag_bear_detected | 0.2% |
| force_index_cross_dn | 0.9% |
| force_index_cross_up | 13.1% |
| force_index_positive | 23.6% |
| gap_dn_1_5pct | 33.0% |
| gap_dn_2pct | 24.7% |
| gap_up_1_5pct | 5.0% |
| gap_up_2pct | 2.8% |
| hammer | 3.7% |
| head_shoulders_bottom_detected | 2.0% |
| head_shoulders_top_detected | 5.0% |
| house_cluster_buy | 17.3% |
| house_cluster_sell | 16.4% |
| htf_aligned_bear | 72.0% |
| htf_aligned_bull | 6.6% |
| htf_disagreement | 1.5% |
| hull_bearish | 80.8% |
| hull_bullish | 19.2% |
| hull_flip_dn | 5.0% |
| hull_flip_up | 4.4% |
| ichi_above_cloud | 9.2% |
| ichi_above_cloud_break_recent_5d | 3.5% |
| ichi_below_cloud | 82.3% |
| ichi_below_cloud_break_recent_5d | 13.4% |
| ichi_cloud_thick | 81.4% |
| ichi_tk_bearish | 84.3% |
| ichi_tk_bullish | 11.2% |
| ichi_tk_cross_dn | 2.9% |
| ichi_tk_cross_up | 0.6% |
| ichi_weekly_above_cloud | 22.8% |
| ichi_weekly_below_cloud | 54.3% |
| ichi_weekly_in_cloud | 22.8% |
| in_reversal_window | 5.7% |
| inside_bar | 7.4% |
| inside_cpr | 5.3% |
| inside_kc | 79.9% |
| insider_cluster_active | 12.2% |
| institutional_buy | 86.6% |
| institutional_negative | 5.9% |
| institutional_persistence_growing | 62.8% |
| institutional_persistence_strong | 83.7% |
| institutional_strong_buy | 82.9% |
| inverted_cup_handle_detected | 4.6% |
| is_friday | 11.8% |
| is_halloween_period | 80.8% |
| is_monday | 29.7% |
| is_pre_holiday | 1.5% |
| is_summer_period | 19.2% |
| is_totm_window | 26.3% |
| is_totm_window_first_day | 2.8% |
| is_week_open | 29.7% |
| kc_touch_lower | 22.1% |
| kc_touch_upper | 0.9% |
| large_dollar_buy | 2.8% |
| macd_12_26_9_bearish | 75.1% |
| macd_12_26_9_bullish | 24.9% |
| macd_12_26_9_crossover_dn | 4.4% |
| macd_12_26_9_crossover_up | 3.9% |
| macd_8_21_5_bearish | 65.9% |
| macd_8_21_5_bullish | 34.1% |
| macd_8_21_5_crossover_dn | 3.9% |
| macd_8_21_5_crossover_up | 11.0% |
| marubozu_bull | 1.7% |
| mfi_broad_overbought | 2.0% |
| mfi_broad_oversold | 17.3% |
| mfi_overbought | 0.4% |
| mfi_oversold | 2.4% |
| monthly_above_sma_12 | 22.3% |
| monthly_above_sma_6 | 14.5% |
| monthly_bias_bear | 73.8% |
| monthly_bias_bull | 10.7% |
| monthly_momentum_pos | 22.7% |
| morning_star | 2.6% |
| near_52w_high | 0.2% |
| near_52w_high_95pct | 0.9% |
| near_52w_high_retest_long | 0.6% |
| near_52w_low | 6.8% |
| near_52w_low_105pct | 18.0% |
| near_avwap_20high_atr_05x | 24.6% |
| near_avwap_20high_atr_10x | 54.3% |
| near_avwap_20high_atr_15x | 75.6% |
| near_avwap_20high_atr_20x | 88.5% |
| near_avwap_20low_atr_05x | 47.6% |
| near_avwap_20low_atr_10x | 73.3% |
| near_avwap_20low_atr_15x | 87.6% |
| near_avwap_20low_atr_20x | 95.8% |
| near_avwap_252low_atr_05x | 27.2% |
| near_avwap_252low_atr_10x | 43.1% |
| near_avwap_252low_atr_15x | 57.7% |
| near_avwap_252low_atr_20x | 68.6% |
| near_avwap_50low_atr_05x | 42.0% |
| near_avwap_50low_atr_10x | 68.6% |
| near_avwap_50low_atr_15x | 84.0% |
| near_avwap_50low_atr_20x | 93.0% |
| near_cam_r3 | 13.3% |
| near_cam_s3 | 5.0% |
| near_cam_s4 | 2.9% |
| near_fib_236 | 1.1% |
| near_fib_382 | 1.5% |
| near_fib_500 | 3.3% |
| near_fib_618 | 4.1% |
| near_fib_786 | 7.0% |
| near_pivot | 12.2% |
| near_prev_close | 11.8% |
| near_prev_high | 10.7% |
| near_prev_low | 5.3% |
| near_r1 | 10.7% |
| near_r1_wide | 45.1% |
| near_r2 | 4.6% |
| near_r2_wide | 24.7% |
| near_s1 | 2.0% |
| near_s1_wide | 22.1% |
| near_s2 | 1.5% |
| near_s2_wide | 7.6% |
| near_wood_r1 | 8.1% |
| near_wood_s1 | 7.4% |
| news_uses_polygon_score | 51.6% |
| obv_bearish | 73.8% |
| obv_bullish | 26.2% |
| obv_diverge_bull | 9.9% |
| obv_falling | 66.5% |
| obv_rising | 33.5% |
| outside_bar | 21.5% |
| pead_negative_surprise | 16.6% |
| pead_positive_surprise | 24.0% |
| pin_bar | 9.4% |
| po3_accumulation_active | 7.4% |
| po3_bullish | 34.1% |
| po3_manipulation_sweep_down | 2.9% |
| po3_manipulation_sweep_up | 1.7% |
| po3_mmbm_setup | 2.4% |
| po3_sweep_above_prior_high | 57.6% |
| po3_sweep_below_prior_low | 59.5% |
| ppo_bullish | 22.1% |
| ppo_crossover_dn | 4.1% |
| ppo_crossover_up | 2.6% |
| pre_fomc_d0 | 0.7% |
| pre_fomc_window | 0.7% |
| price_above_dema | 44.4% |
| price_above_ema_20 | 13.8% |
| price_above_ema_200 | 17.5% |
| price_above_ema_200_break_recent_5d | 6.1% |
| price_above_ema_20_break_recent_5d | 10.9% |
| price_above_ema_21 | 13.3% |
| price_above_ema_21_break_recent_5d | 10.1% |
| price_above_ema_50 | 11.6% |
| price_above_ema_50_break_recent_5d | 7.6% |
| price_above_ema_9 | 27.1% |
| price_above_ema_9_break_recent_5d | 24.5% |
| price_above_hull | 46.4% |
| price_above_sma_200 | 19.5% |
| price_above_sma_21 | 15.7% |
| price_above_sma_50 | 11.0% |
| price_above_tema | 54.3% |
| price_below_dema | 55.6% |
| price_below_hull | 53.6% |
| price_below_tema | 45.7% |
| psar_bullish | 21.7% |
| psar_flip_dn | 4.4% |
| psar_flip_up | 6.1% |
| r1_break_retest_long | 28.7% |
| recent_capitulation_at_s3 | 0.9% |
| resistance_break_retest | 3.1% |
| risk_off_regime_bond_signal | 51.7% |
| risk_off_regime_bond_signal_strong | 32.2% |
| risk_off_regime_gold_signal | 66.3% |
| risk_on_regime_bond_signal | 2.9% |
| risk_on_regime_bond_signal_strong | 0.4% |
| roc_positive | 15.3% |
| roc_turning_dn | 1.1% |
| roc_turning_up | 5.3% |
| rsi_14_bullish | 12.9% |
| rsi_14_cross_dn_overbought_recent_3d | 0.6% |
| rsi_14_cross_up_extreme_os_recent_3d | 2.4% |
| rsi_14_cross_up_oversold_recent_3d | 23.6% |
| rsi_14_extreme_os | 0.2% |
| rsi_14_overbought | 0.4% |
| rsi_14_oversold | 10.3% |
| rsi_14_rising | 75.0% |
| rsi_21_bullish | 12.2% |
| rsi_21_cross_dn_overbought_recent_3d | 0.4% |
| rsi_21_cross_up_oversold_recent_3d | 9.9% |
| rsi_21_overbought | 0.2% |
| rsi_21_oversold | 5.3% |
| rsi_21_rising | 75.0% |
| rsi_2_bullish | 49.4% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 15.1% |
| rsi_2_cross_dn_overbought_recent_3d | 23.6% |
| rsi_2_cross_up_extreme_os_recent_3d | 60.2% |
| rsi_2_cross_up_oversold_recent_3d | 58.0% |
| rsi_2_extreme_ob | 12.5% |
| rsi_2_extreme_os | 24.1% |
| rsi_2_overbought | 26.3% |
| rsi_2_oversold | 32.6% |
| rsi_2_rising | 75.0% |
| rsi_9_bullish | 15.7% |
| rsi_9_cross_dn_overbought_recent_3d | 0.9% |
| rsi_9_cross_up_extreme_os_recent_3d | 13.1% |
| rsi_9_cross_up_oversold_recent_3d | 30.4% |
| rsi_9_extreme_ob | 0.2% |
| rsi_9_extreme_os | 2.4% |
| rsi_9_overbought | 1.3% |
| rsi_9_oversold | 20.3% |
| rsi_9_rising | 75.0% |
| s1_break_retest_short | 80.8% |
| sc_13d_filed_within_30d | 2.5% |
| sc_13g_filed_within_30d | 0.6% |
| sector_outperforming_spy | 62.5% |
| sector_underperforming_spy | 37.5% |
| shooting_star | 4.8% |
| sma_20_50_bullish | 20.3% |
| sma_20_50_golden_cross | 0.7% |
| sma_50_200_bullish | 35.7% |
| sma_50_200_golden_cross | 0.2% |
| sma_9_21_bullish | 18.8% |
| sma_9_21_golden_cross | 1.5% |
| smc_bos_bearish | 24.3% |
| smc_bos_bullish | 8.8% |
| smc_bos_retest_long | 3.9% |
| smc_bos_retest_short | 3.9% |
| smc_breaker_block_bearish | 29.5% |
| smc_breaker_block_bullish | 23.2% |
| smc_choch_bearish | 14.7% |
| smc_choch_bullish | 1.7% |
| smc_equal_highs_swept | 2.4% |
| smc_equal_lows_swept | 13.8% |
| smc_fvg_bearish_active | 70.3% |
| smc_fvg_bullish_active | 11.2% |
| smc_fvg_retest_long_zone | 1.1% |
| smc_fvg_retest_short_zone | 20.3% |
| smc_in_discount_zone | 92.8% |
| smc_in_premium_zone | 19.9% |
| smc_inverse_fvg_bearish | 97.6% |
| smc_inverse_fvg_bullish | 42.4% |
| smc_liquidity_swept_dn | 4.4% |
| smc_liquidity_swept_up | 3.9% |
| smc_mitigation_block_long | 1.3% |
| smc_mitigation_block_short | 0.6% |
| smc_ob_bearish_active | 62.8% |
| smc_ob_bullish_active | 12.5% |
| smc_ote_long_zone | 8.8% |
| smc_ote_short_zone | 1.8% |
| squeeze_fire_dn | 0.4% |
| squeeze_fire_up | 8.3% |
| squeeze_in | 22.7% |
| squeeze_positive | 23.2% |
| stoch_bearish_cross | 4.4% |
| stoch_broad_overbought | 4.8% |
| stoch_broad_oversold | 47.5% |
| stoch_bullish_cross | 23.0% |
| stoch_overbought | 3.3% |
| stoch_oversold | 36.6% |
| stochrsi_cross_dn | 15.3% |
| stochrsi_cross_up | 48.1% |
| stochrsi_overbought | 19.2% |
| stochrsi_oversold | 30.4% |
| supertrend_bearish | 5.5% |
| supertrend_bullish | 94.5% |
| supertrend_flip_dn | 0.4% |
| supertrend_flip_recent_long_5d | 6.8% |
| supertrend_flip_recent_short_5d | 9.0% |
| supertrend_flip_up | 0.7% |
| support_break_retest | 47.5% |
| tema_above_dema | 23.4% |
| tema_cross_dn | 2.6% |
| tema_cross_up | 2.2% |
| three_white_soldiers | 1.5% |
| triangle_apex_break_retest_long | 2.6% |
| triangle_ascending_detected | 2.0% |
| triangle_descending_detected | 5.7% |
| uo_overbought | 0.6% |
| uo_oversold | 1.7% |
| usd_strengthening | 14.7% |
| usd_weakening | 24.7% |
| vol_above_avg | 59.5% |
| vol_below_avg | 40.5% |
| vol_spike_12x | 42.0% |
| vol_spike_15x | 26.2% |
| vol_spike_17x | 18.6% |
| vol_spike_2x | 7.7% |
| vol_spike_2x_on_down_day_recent_3d | 9.9% |
| vol_spike_2x_on_up_day_recent_3d | 4.1% |
| vol_spike_3x | 0.7% |
| vp_above_value_area | 3.7% |
| vp_below_value_area | 45.1% |
| vp_close_above_poc | 19.3% |
| vp_close_below_poc | 80.7% |
| vp_in_value_area | 51.2% |
| week_open_gap_down_15pct | 17.3% |
| week_open_gap_up_15pct | 1.8% |
| weekly_above_ema_10 | 12.2% |
| weekly_above_ema_20 | 13.1% |
| weekly_bias_bear | 84.5% |
| weekly_bias_bull | 9.8% |
| weekly_momentum_pos | 16.6% |
| williams_r_overbought | 6.1% |
| williams_r_oversold | 21.2% |
| williams_r_rising | 88.0% |
| within_pead_window | 19.7% |
| within_post_deletion_window | 1.2% |
| xs_avoid_high_ivol | 61.1% |
| xs_avoid_high_max | 69.6% |
| xs_high_beta_decile | 35.9% |
| xs_low_beta_bottom_quintile | 35.9% |
| xs_low_beta_decile | 12.7% |
| xs_low_beta_decile_entry_recent_5d | 0.7% |
| xs_low_beta_top_quintile | 12.7% |
| xs_momentum_bottom_decile | 20.8% |
| xs_momentum_bottom_quintile | 33.0% |
| xs_momentum_top_decile | 10.9% |
| xs_momentum_top_quintile | 17.5% |
| xs_quality_top_quintile | 51.9% |
| year_low_break_retest_short | 14.4% |
| yoy_surprise_high | 55.5% |
| yoy_surprise_negative | 31.8% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 82.7% |
| committed_growth_holders | 82.7% |
| corp_donations_1y | 5.9% |
| corp_donations_count_1y | 5.9% |
| corp_donations_unique_pacs | 5.9% |
| cot_rut_commercials_pctile_3y | 90.2% |
| cot_rut_mmoney_pctile_3y | 90.2% |
| cup_handle_depth_pct | 19.3% |
| days_since_deletion | 15.5% |
| days_since_inclusion | 19.5% |
| days_since_last_earnings | 98.0% |
| days_to_next_holiday | 70.2% |
| days_to_rebalance | 8.7% |
| dpi_30d_avg | 93.0% |
| dpi_recent | 93.0% |
| earnings_announcement_return | 93.0% |
| earnings_eps_yoy_growth | 94.8% |
| gov_contracts_4q_sum | 45.9% |
| gov_contracts_last_qtr_amount | 45.9% |
| gov_contracts_qoq_growth | 45.9% |
| head_shoulders_magnitude_pct | 6.8% |
| insider_director_buyers_30d | 9.0% |
| insider_officer_buyers_30d | 9.0% |
| insider_total_shares_bought_30d | 9.0% |
| insider_unique_buyers_30d | 9.0% |
| inverted_cup_handle_height_pct | 12.2% |
| lobbying_amount_1y | 69.4% |
| lobbying_amount_q | 69.4% |
| lobbying_amount_yoy | 69.4% |
| otc_short_ratio_recent | 93.0% |
| otc_volume_recent | 93.0% |
| pair_half_life | 89.5% |
| pair_max_abs_zscore | 89.5% |
| pair_zscore_signed | 89.5% |
| pct_from_avwap_20high | 98.0% |
| pct_from_avwap_20low | 60.8% |
| pct_from_avwap_252low | 84.5% |
| pct_from_avwap_50low | 68.0% |
| persistent_holders_4q | 82.7% |
| persistent_holders_8q | 82.7% |
| search_volume_index_recent | 82.3% |
| search_volume_observations | 82.3% |
| search_volume_zscore_30d | 82.3% |
| sector_etf_return_20d | 2.9% |
| spy_return_20d | 2.9% |
| total_active_holders | 82.7% |
| triangle_breakdown_pct | 5.7% |
| triangle_breakout_pct | 2.0% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.997), `avwap_252low` (0.993), `avwap_50low` (0.997), `bb_10_20_lower` (0.996), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.998), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.997), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.998), `cam_r1` (0.997), `cam_r2` (0.997), `cam_r3` (0.997), `cam_r4` (0.997), `cam_s1` (0.997), `cam_s2` (0.997), `cam_s3` (0.996), `cam_s4` (0.996), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.997), `cpr_top` (0.997), `cup_handle_breakout_level` (0.998), `cup_handle_rim` (0.994), `dc10_lower` (0.996), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.996), `dc20_mid` (0.999), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.991), `double_bottom_trough` (0.994), `double_top_neckline` (0.996), `double_top_peak` (0.995), `entry_stop_long` (0.995), `entry_stop_short` (0.997), `fib_236` (0.993), `fib_382` (0.995), `fib_500` (0.996), `fib_618` (0.997), `fib_786` (0.998), `fib_ext_127` (0.985), `fib_ext_162` (0.979), `head_shoulders_bottom_neckline` (0.998), `head_shoulders_top_neckline` (0.998), `hull_ma` (0.997), `ichi_kijun` (0.999), `ichi_senkou_a` (0.993), `ichi_senkou_b` (0.989), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.998), `inverted_cup_handle_rim_low` (0.997), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (0.999), `monthly_close` (0.997), `monthly_sma_12` (0.978), `monthly_sma_6` (0.993), `pivot` (0.997), `prev_close` (0.997), `prev_high` (0.998), `prev_low` (0.997), `psar_value` (0.996), `r1` (0.998), `r2` (0.998), `r3` (0.998), `s1` (0.996), `s2` (0.995), `s3` (0.993), `supertrend_value` (0.99), `swing_high` (0.989), `swing_low` (0.996), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.995), `vp_value_area_high` (0.993), `vp_value_area_low` (0.996), `weekly_close` (0.997), `weekly_ema_10` (0.999), `weekly_ema_20` (0.995), `wood_p` (0.997), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.997), `wood_s2` (0.996), `year_high` (0.952), `year_low` (0.966)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | backwardation margin (VIX over VIX3M) | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2 | xs_quality_decile >= 7 | 4 | subset-safe | no - derives offline |

```
FULL FACTORIAL     1 x 4 = 4
offline gradings   4 level-combinations x 24 exits = 96
ENGINE RUNS        1 (every fire-adding axis sits at production-only until its env actuator exists)
check              1 x 4 = 4
```

B-row candidates NOT in this factorial: 614 census axes join it only when REGISTERED at the T3 band review.
