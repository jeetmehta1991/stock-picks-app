# Table A - inside_bar_breakout

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit e29a15af2 at 2026-09-17 17:07:43 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** breakout | **status:** NOT-STARTED | **R5 fires:** 677 | **surviving fires (T1):** 677 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  above_vwap  <- backtest/signals/screener.py +1
       DEFN: close vs session VWAP (vwap block)
       knobs P1.1-P1.1 (band rows in Table A)
P2  inside_bar  <- backtest/signals/screener.py +1
       DEFN: inside bar: high < prior high AND low > prior low (technical.py:2027)
       knobs P2.1-P2.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  adx > 20   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_inside_bar_breakout (docstring and return dropped):

```python
fires = s.get('inside_bar') and s.get('adx', 0) > 20 and s.get('above_vwap')
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
| P1 | PRODUCER | above_vwap - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs session VWAP (vwap block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | buffer pct (price vs vwap) - backtest/signals/technical.py vwap block | BRACKET zero; strict inequality today | 0.0 | [0, 0.25, 0.5] | none - today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | inside_bar - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | inside bar: high < prior high AND low > prior low (technical.py:2027) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | (structural) h[-1]<h[-2] and l[-1]>l[-2] - no parameter - backtest/signals/technical.py:2027 | BRACKET zero; strict containment today | - | optional containment-margin pct [0, 0.1, 0.25] | none - bar OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | STRATEGY | adx `> 20` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `> 20` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | `> 20` | 100.0% | TIGHTER = RAISE the floor: 22.478 -> 541 (80%); 25.286 -> 406 (60%); 28.716 -> 271 (40%); 33.962 -> 136 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx_di_minus | backtest/signals/technical.py | 100.0% | 22.246, 26.294, 29.966, 34.39 | 22.246: 541 (80%); 26.294: 406 (60%); 29.966: 271 (40%); 34.39: 136 (20%) | 22.246: 136 (20%); 26.294: 271 (40%); 29.966: 406 (60%); 34.39: 541 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 11.964, 14.43, 17.676, 22.912 | 11.964: 541 (80%); 14.43: 408 (60%); 17.676: 271 (40%); 22.912: 136 (20%) | 11.964: 136 (20%); 14.43: 272 (40%); 17.676: 406 (60%); 22.912: 541 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -13.5004, -6.5008, -2.6163, 0.188 | -13.5004: 541 (80%); -6.5008: 406 (60%); -2.6163: 271 (40%); 0.188: 136 (20%) | -13.5004: 136 (20%); -6.5008: 271 (40%); -2.6163: 406 (60%); 0.188: 541 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.6736, 2.8715, 4.6894, 8.1259 | 1.6736: 541 (80%); 2.8715: 406 (60%); 4.6894: 271 (40%); 8.1259: 136 (20%) | 1.6736: 136 (20%); 2.8715: 271 (40%); 4.6894: 406 (60%); 8.1259: 541 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.6736, 2.8715, 4.6894, 8.1259 | 1.6736: 541 (80%); 2.8715: 406 (60%); 4.6894: 271 (40%); 8.1259: 136 (20%) | 1.6736: 136 (20%); 2.8715: 271 (40%); 4.6894: 406 (60%); 8.1259: 541 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.0556, 2.578, 3.1284, 3.9118 | 2.0556: 541 (80%); 2.578: 406 (60%); 3.1284: 271 (40%); 3.9118: 136 (20%) | 2.0556: 136 (20%); 2.578: 271 (40%); 3.1284: 406 (60%); 3.9118: 541 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0539, 0.0854, 0.1173, 0.1779 | 0.0539: 542 (80%); 0.0854: 408 (60%); 0.1173: 271 (40%); 0.1779: 136 (20%) | 0.0539: 137 (20%); 0.0854: 272 (40%); 0.1173: 406 (60%); 0.1779: 541 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.1957, 0.2931, 0.441, 0.6944 | 0.1957: 542 (80%); 0.2931: 406 (60%); 0.441: 271 (40%); 0.6944: 136 (20%) | 0.1957: 136 (20%); 0.2931: 271 (40%); 0.441: 406 (60%); 0.6944: 541 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0654, 0.0944, 0.1251, 0.1654 | 0.0654: 542 (80%); 0.0944: 409 (60%); 0.1251: 271 (40%); 0.1654: 136 (20%) | 0.0654: 137 (20%); 0.0944: 271 (40%); 0.1251: 406 (60%); 0.1654: 541 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.0356, 0.1109, 0.3182, 0.6456 | -0.0356: 541 (80%); 0.1109: 407 (60%); 0.3182: 271 (40%); 0.6456: 136 (20%) | -0.0356: 136 (20%); 0.1109: 272 (40%); 0.3182: 406 (60%); 0.6456: 541 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0871, 0.1259, 0.1668, 0.2204 | 0.0871: 542 (80%); 0.1259: 409 (60%); 0.1668: 271 (40%); 0.2204: 136 (20%) | 0.0871: 136 (20%); 0.1259: 271 (40%); 0.1668: 406 (60%); 0.2204: 541 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.0983, 0.2081, 0.3637, 0.6092 | 0.0983: 541 (80%); 0.2081: 407 (60%); 0.3637: 271 (40%); 0.6092: 136 (20%) | 0.0983: 136 (20%); 0.2081: 271 (40%); 0.3637: 406 (60%); 0.6092: 541 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0368, -0.0141, 0.0023, 0.0292 | -0.0368: 542 (80%); -0.0141: 406 (60%); 0.0023: 272 (40%); 0.0292: 144 (21%) | -0.0368: 139 (21%); -0.0141: 271 (40%); 0.0023: 407 (60%); 0.0292: 542 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1333, 0.1475, 0.1647, 0.2075 | 0.1333: 544 (80%); 0.1475: 405 (60%); 0.1647: 272 (40%); 0.2075: 136 (20%) | 0.1333: 136 (20%); 0.1475: 272 (40%); 0.1647: 405 (60%); 0.2075: 541 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 677 (100%) | 0: 641 (95%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1657, -0.0834, -0.0055, 0.0887 | -0.1657: 541 (80%); -0.0834: 406 (60%); -0.0055: 271 (40%); 0.0887: 136 (20%) | -0.1657: 136 (20%); -0.0834: 271 (40%); -0.0055: 406 (60%); 0.0887: 542 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1, 1.8 | 0: 677 (100%); 1: 276 (41%); 1.8: 136 (20%) | 0: 401 (59%); 1: 541 (80%); 1.8: 541 (80%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2638, -0.2105, -0.1544, -0.1285 | -0.2638: 545 (81%); -0.2105: 406 (60%); -0.1544: 272 (40%); -0.1285: 141 (21%) | -0.2638: 137 (20%); -0.2105: 271 (40%); -0.1544: 407 (60%); -0.1285: 553 (82%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.0846, 0.5256, 0.6538, 0.7436 | 0.0846: 541 (80%); 0.5256: 409 (60%); 0.6538: 283 (42%); 0.7436: 151 (22%) | 0.0846: 136 (20%); 0.5256: 272 (40%); 0.6538: 410 (61%); 0.7436: 546 (81%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.3205, 0.5897, 0.7308, 0.891 | 0.3205: 544 (80%); 0.5897: 415 (61%); 0.7308: 281 (42%); 0.891: 149 (22%) | 0.3205: 138 (20%); 0.5897: 285 (42%); 0.7308: 409 (60%); 0.891: 551 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0921, -0.0304, 0.0223, 0.1466 | -0.0921: 551 (81%); -0.0304: 411 (61%); 0.0223: 275 (41%); 0.1466: 137 (20%) | -0.0921: 137 (20%); -0.0304: 274 (40%); 0.0223: 417 (62%); 0.1466: 543 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2756, 0.4295, 0.5385, 0.7244 | 0.2756: 546 (81%); 0.4295: 410 (61%); 0.5385: 273 (40%); 0.7244: 138 (20%) | 0.2756: 137 (20%); 0.4295: 274 (40%); 0.5385: 411 (61%); 0.7244: 544 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1282, 0.25, 0.3974, 0.6218 | 0.1282: 542 (80%); 0.25: 415 (61%); 0.3974: 272 (40%); 0.6218: 140 (21%) | 0.1282: 140 (21%); 0.25: 281 (42%); 0.3974: 409 (60%); 0.6218: 542 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.4878, -0.2655, -0.0837, 0.0965 | -0.4878: 541 (80%); -0.2655: 411 (61%); -0.0837: 282 (42%); 0.0965: 138 (20%) | -0.4878: 136 (20%); -0.2655: 272 (40%); -0.0837: 410 (61%); 0.0965: 544 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3397, 0.5321, 0.7692, 0.9487 | 0.3397: 546 (81%); 0.5321: 413 (61%); 0.7692: 276 (41%); 0.9487: 137 (20%) | 0.3397: 140 (21%); 0.5321: 275 (41%); 0.7692: 407 (60%); 0.9487: 555 (82%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1667, 0.3936, 0.5962, 0.8526 | 0.1667: 542 (80%); 0.3936: 406 (60%); 0.5962: 273 (40%); 0.8526: 153 (23%) | 0.1667: 144 (21%); 0.3936: 271 (40%); 0.5962: 413 (61%); 0.8526: 544 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0694, -0.0569, -0.0274, 0 | -0.0694: 560 (83%); -0.0569: 406 (60%); -0.0274: 272 (40%); 0: 251 (37%) | -0.0694: 137 (20%); -0.0569: 271 (40%); -0.0274: 413 (61%); 0: 638 (94%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3205, 0.5385, 0.8974, 1 | 0.3205: 544 (80%); 0.5385: 407 (60%); 0.8974: 275 (41%); 1: 182 (27%) | 0.3205: 140 (21%); 0.5385: 278 (41%); 0.8974: 408 (60%); 1: 677 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.141, 0.2821, 0.5705, 0.7949 | 0.141: 547 (81%); 0.2821: 412 (61%); 0.5705: 281 (42%); 0.7949: 142 (21%) | 0.141: 138 (20%); 0.2821: 278 (41%); 0.5705: 411 (61%); 0.7949: 543 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0111, 0.084, 0.1724, 0.3352 | 0.0111: 543 (80%); 0.084: 409 (60%); 0.1724: 272 (40%); 0.3352: 146 (22%) | 0.0111: 140 (21%); 0.084: 271 (40%); 0.1724: 410 (61%); 0.3352: 550 (81%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.6101, 0.9038, 0.9615, 0.9856 | 0.6101: 541 (80%); 0.9038: 409 (60%); 0.9615: 290 (43%); 0.9856: 136 (20%) | 0.6101: 136 (20%); 0.9038: 287 (42%); 0.9615: 433 (64%); 0.9856: 541 (80%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0954, 0.2115, 0.5064, 0.7244 | 0.0954: 541 (80%); 0.2115: 408 (60%); 0.5064: 276 (41%); 0.7244: 138 (20%) | 0.0954: 136 (20%); 0.2115: 277 (41%); 0.5064: 407 (60%); 0.7244: 542 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, 0.0325, 0.1204, 0.1523 | -0.0812: 572 (84%); 0.0325: 406 (60%); 0.1204: 271 (40%); 0.1523: 153 (23%) | -0.0812: 141 (21%); 0.0325: 271 (40%); 0.1204: 406 (60%); 0.1523: 544 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2049, -0.0125, 0.0533, 0.1216 | -0.2049: 545 (81%); -0.0125: 407 (60%); 0.0533: 273 (40%); 0.1216: 140 (21%) | -0.2049: 139 (21%); -0.0125: 274 (40%); 0.0533: 407 (60%); 0.1216: 550 (81%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.5897, 0.8013, 0.9808 | 0.2628: 560 (83%); 0.5897: 408 (60%); 0.8013: 273 (40%); 0.9808: 144 (21%) | 0.2628: 137 (20%); 0.5897: 288 (43%); 0.8013: 414 (61%); 0.9808: 570 (84%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1346, 0.5, 0.6731, 0.8205 | 0.1346: 542 (80%); 0.5: 409 (60%); 0.6731: 277 (41%); 0.8205: 142 (21%) | 0.1346: 140 (21%); 0.5: 286 (42%); 0.6731: 411 (61%); 0.8205: 544 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.097, 0.2083, 0.4188, 0.8264 | 0.097: 541 (80%); 0.2083: 407 (60%); 0.4188: 271 (40%); 0.8264: 136 (20%) | 0.097: 136 (20%); 0.2083: 272 (40%); 0.4188: 406 (60%); 0.8264: 541 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.7% | 31, 62, 91, 147 | 31: 535 (79%); 62: 412 (61%); 91: 269 (40%); 147: 140 (21%) | 31: 135 (20%); 62: 271 (40%); 91: 404 (60%); 147: 535 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.9% | 1.7442, 2.2668, 2.847, 3.7863 | 1.7442: 541 (80%); 2.2668: 406 (60%); 2.847: 271 (40%); 3.7863: 136 (20%) | 1.7442: 136 (20%); 2.2668: 271 (40%); 2.847: 406 (60%); 3.7863: 541 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 8, 19, 27, 36 | 8: 544 (80%); 19: 417 (62%); 27: 279 (41%); 36: 156 (23%) | 8: 147 (22%); 19: 280 (41%); 27: 428 (63%); 36: 549 (81%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3, 4 | 1: 545 (81%); 2: 428 (63%); 3: 306 (45%); 4: 155 (23%) | 1: 249 (37%); 2: 371 (55%); 3: 522 (77%); 4: 677 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.018, -0.0048, 0.0108, 0.0218 | -0.018: 541 (80%); -0.0048: 407 (60%); 0.0108: 273 (40%); 0.0218: 137 (20%) | -0.018: 136 (20%); -0.0048: 272 (40%); 0.0108: 409 (60%); 0.0218: 543 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 25.621, 26.4661, 27.0139, 27.55 | 25.621: 542 (80%); 26.4661: 407 (60%); 27.0139: 271 (40%); 27.55: 137 (20%) | 25.621: 137 (20%); 26.4661: 272 (40%); 27.0139: 406 (60%); 27.55: 542 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.5588, -0.1972, 0.0888, 0.4584 | -0.5588: 541 (80%); -0.1972: 406 (60%); 0.0888: 271 (40%); 0.4584: 136 (20%) | -0.5588: 136 (20%); -0.1972: 271 (40%); 0.0888: 406 (60%); 0.4584: 541 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.4584, -0.0888, 0.1972, 0.5588 | -0.4584: 541 (80%); -0.0888: 406 (60%); 0.1972: 271 (40%); 0.5588: 136 (20%) | -0.4584: 136 (20%); -0.0888: 271 (40%); 0.1972: 406 (60%); 0.5588: 541 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0427, 0.0007, 0.0239, 0.0684 | -0.0427: 541 (80%); 0.0007: 407 (60%); 0.0239: 272 (40%); 0.0684: 136 (20%) | -0.0427: 136 (20%); 0.0007: 273 (40%); 0.0239: 408 (60%); 0.0684: 541 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.6251, 8.4873, 8.8411, 9.0786 | 7.6251: 541 (80%); 8.4873: 407 (60%); 8.8411: 271 (40%); 9.0786: 134 (20%) | 7.6251: 136 (20%); 8.4873: 270 (40%); 8.8411: 406 (60%); 9.0786: 543 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.9% | 0, 1 | 0: 676 (100%); 1: 254 (38%) | 0: 422 (62%); 1: 579 (86%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.9% | 0 | 0: 542 (80%) | 0: 546 (81%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.9% | 0, 1 | 0: 676 (100%); 1: 256 (38%) | 0: 420 (62%); 1: 583 (86%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 6, 207, 345.6 | 2: 545 (81%); 6: 431 (64%); 207: 272 (40%); 345.6: 136 (20%) | 2: 163 (24%); 6: 275 (41%); 207: 407 (60%); 345.6: 541 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 7, 111, 177.4 | 1: 542 (80%); 7: 408 (60%); 111: 273 (40%); 177.4: 136 (20%) | 1: 178 (26%); 7: 277 (41%); 111: 407 (60%); 177.4: 541 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -1.3452, -0.4469, -0.0798, 0.5068 | -1.3452: 541 (80%); -0.4469: 406 (60%); -0.0798: 271 (40%); 0.5068: 136 (20%) | -1.3452: 136 (20%); -0.4469: 271 (40%); -0.0798: 406 (60%); 0.5068: 541 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -5.5015, -2.5458, -1.0662, -0.1668 | -5.5015: 541 (80%); -2.5458: 406 (60%); -1.0662: 271 (40%); -0.1668: 136 (20%) | -5.5015: 136 (20%); -2.5458: 271 (40%); -1.0662: 406 (60%); -0.1668: 541 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -4.7917, -1.9087, -0.8266, 0.3642 | -4.7917: 541 (80%); -1.9087: 406 (60%); -0.8266: 271 (40%); 0.3642: 136 (20%) | -4.7917: 136 (20%); -1.9087: 271 (40%); -0.8266: 406 (60%); 0.3642: 541 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.9187, -0.2658, 0.014, 0.4758 | -0.9187: 541 (80%); -0.2658: 408 (60%); 0.014: 271 (40%); 0.4758: 136 (20%) | -0.9187: 136 (20%); -0.2658: 271 (40%); 0.014: 406 (60%); 0.4758: 541 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -5.8351, -2.7857, -1.1642, -0.0294 | -5.8351: 541 (80%); -2.7857: 406 (60%); -1.1642: 271 (40%); -0.0294: 136 (20%) | -5.8351: 136 (20%); -2.7857: 271 (40%); -1.1642: 406 (60%); -0.0294: 541 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -5.6928, -2.5843, -1.0245, 0.0567 | -5.6928: 541 (80%); -2.5843: 406 (60%); -1.0245: 271 (40%); 0.0567: 136 (20%) | -5.6928: 136 (20%); -2.5843: 271 (40%); -1.0245: 406 (60%); 0.0567: 541 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 31.544, 39.044, 46.96, 57.332 | 31.544: 541 (80%); 39.044: 406 (60%); 46.96: 272 (40%); 57.332: 136 (20%) | 31.544: 136 (20%); 39.044: 271 (40%); 46.96: 407 (60%); 57.332: 541 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.3% | 0.0044, 0.0114, 0.0228, 0.0448 | 0.0044: 539 (80%); 0.0114: 404 (60%); 0.0228: 268 (40%); 0.0448: 134 (20%) | 0.0044: 133 (20%); 0.0114: 268 (40%); 0.0228: 404 (60%); 0.0448: 538 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 4, 9 | 0: 677 (100%); 1: 499 (74%); 4: 277 (41%); 9: 145 (21%) | 0: 178 (26%); 1: 277 (41%); 4: 440 (65%); 9: 551 (81%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2 | 0: 677 (100%); 0.2: 143 (21%) | 0: 435 (64%); 0.2: 549 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1044, 0.4, 0.6667 | 0: 677 (100%); 0.1044: 406 (60%); 0.4: 277 (41%); 0.6667: 137 (20%) | 0: 269 (40%); 0.1044: 271 (40%); 0.4: 412 (61%); 0.6667: 569 (84%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 6 | 0: 677 (100%); 1: 463 (68%); 3: 284 (42%); 6: 156 (23%) | 0: 214 (32%); 1: 319 (47%); 3: 454 (67%); 6: 542 (80%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 4, 9 | 0: 677 (100%); 1: 499 (74%); 4: 277 (41%); 9: 145 (21%) | 0: 178 (26%); 1: 277 (41%); 4: 440 (65%); 9: 551 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 677 (100%); 1: 456 (67%); 3: 288 (43%); 8: 142 (21%) | 0: 221 (33%); 1: 334 (49%); 3: 419 (62%); 8: 553 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2335, 0.4129, 0.6667 | 0: 631 (93%); 0.2335: 406 (60%); 0.4129: 271 (40%); 0.6667: 148 (22%) | 0: 158 (23%); 0.2335: 271 (40%); 0.4129: 406 (60%); 0.6667: 545 (81%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.1278, 0.5431 | 0: 614 (91%); 0.1278: 271 (40%); 0.5431: 136 (20%) | 0: 372 (55%); 0.1278: 406 (60%); 0.5431: 541 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2573, 0.562 | 0: 620 (92%); 0.2573: 271 (40%); 0.562: 136 (20%) | 0: 309 (46%); 0.2573: 406 (60%); 0.562: 541 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2573, 0.562 | 0: 620 (92%); 0.2573: 271 (40%); 0.562: 136 (20%) | 0: 309 (46%); 0.2573: 406 (60%); 0.562: 541 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.221, 0, 0.099 | -0.221: 541 (80%); 0: 481 (71%); 0.099: 136 (20%) | -0.221: 136 (20%); 0: 503 (74%); 0.099: 541 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.6461, -0.1992, 0.1207, 1.5501 | -0.6461: 549 (81%); -0.1992: 406 (60%); 0.1207: 271 (40%); 1.5501: 136 (20%) | -0.6461: 158 (23%); -0.1992: 271 (40%); 0.1207: 406 (60%); 1.5501: 541 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 11 | 2: 565 (83%); 4: 449 (66%); 7: 283 (42%); 11: 143 (21%) | 2: 167 (25%); 4: 292 (43%); 7: 430 (64%); 11: 555 (82%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0797, -0.045, -0.0109, 0.0212 | -0.0797: 542 (80%); -0.045: 406 (60%); -0.0109: 271 (40%); 0.0212: 136 (20%) | -0.0797: 135 (20%); -0.045: 271 (40%); -0.0109: 406 (60%); 0.0212: 541 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.1152, -0.0742, -0.0423, 0.0102 | -0.1152: 540 (80%); -0.0742: 405 (60%); -0.0423: 271 (40%); 0.0102: 136 (20%) | -0.1152: 137 (20%); -0.0742: 272 (40%); -0.0423: 406 (60%); 0.0102: 541 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0543, -0.0222, -0.0043, 0.0216 | -0.0543: 540 (80%); -0.0222: 407 (60%); -0.0043: 271 (40%); 0.0216: 137 (20%) | -0.0543: 137 (20%); -0.0222: 270 (40%); -0.0043: 406 (60%); 0.0216: 540 (80%) | OFFLINE |
| pct_from_avwap_20high | backtest/signals/screener.py | 100.0% | -5.5182, -2.977, -1.3736, 0.1042 | -5.5182: 541 (80%); -2.977: 406 (60%); -1.3736: 271 (40%); 0.1042: 136 (20%) | -5.5182: 136 (20%); -2.977: 271 (40%); -1.3736: 406 (60%); 0.1042: 541 (80%) | OFFLINE |
| pct_from_avwap_20low | (not found by literal grep) | 100.0% | 0.0072, 0.5208, 1.1596, 2.5782 | 0.0072: 541 (80%); 0.5208: 406 (60%); 1.1596: 271 (40%); 2.5782: 136 (20%) | 0.0072: 136 (20%); 0.5208: 271 (40%); 1.1596: 406 (60%); 2.5782: 541 (80%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 100.0% | -0.8604, 0.3996, 1.292, 3.4908 | -0.8604: 541 (80%); 0.3996: 406 (60%); 1.292: 272 (40%); 3.4908: 136 (20%) | -0.8604: 136 (20%); 0.3996: 271 (40%); 1.292: 407 (60%); 3.4908: 541 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | 3.8714, 10.2364, 17.8308, 32.046 | 3.8714: 541 (80%); 10.2364: 406 (60%); 17.8308: 271 (40%); 32.046: 136 (20%) | 3.8714: 136 (20%); 10.2364: 271 (40%); 17.8308: 406 (60%); 32.046: 541 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0443, 0.0631, 0.0866, 0.1281 | 0.0443: 542 (80%); 0.0631: 407 (60%); 0.0866: 272 (40%); 0.1281: 136 (20%) | 0.0443: 136 (20%); 0.0631: 273 (40%); 0.0866: 407 (60%); 0.1281: 541 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.4813, 0.6529, 0.7658, 0.8729 | 0.4813: 541 (80%); 0.6529: 406 (60%); 0.7658: 271 (40%); 0.8729: 136 (20%) | 0.4813: 136 (20%); 0.6529: 271 (40%); 0.7658: 406 (60%); 0.8729: 541 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.9156, -1.956, -1.1831, -0.2158 | -2.9156: 541 (80%); -1.956: 406 (60%); -1.1831: 271 (40%); -0.2158: 136 (20%) | -2.9156: 136 (20%); -1.956: 271 (40%); -1.1831: 406 (60%); -0.2158: 541 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -1.0018, -0.505, -0.0868, 0.3664 | -1.0018: 541 (80%); -0.505: 406 (60%); -0.0868: 271 (40%); 0.3664: 136 (20%) | -1.0018: 136 (20%); -0.505: 271 (40%); -0.0868: 406 (60%); 0.3664: 541 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -2.6701, -1.6502, -0.967, 0.4234 | -2.6701: 541 (80%); -1.6502: 406 (60%); -0.967: 271 (40%); 0.4234: 136 (20%) | -2.6701: 136 (20%); -1.6502: 271 (40%); -0.967: 406 (60%); 0.4234: 541 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -9.119, -5.1484, -1.9954, 2.5518 | -9.119: 541 (80%); -5.1484: 406 (60%); -1.9954: 271 (40%); 2.5518: 136 (20%) | -9.119: 136 (20%); -5.1484: 271 (40%); -1.9954: 406 (60%); 2.5518: 541 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 34.218, 38.918, 43.654, 50.36 | 34.218: 541 (80%); 38.918: 406 (60%); 43.654: 271 (40%); 50.36: 138 (20%) | 34.218: 136 (20%); 38.918: 271 (40%); 43.654: 406 (60%); 50.36: 542 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 32.56, 44.454, 56.974, 70.94 | 32.56: 542 (80%); 44.454: 406 (60%); 56.974: 271 (40%); 70.94: 136 (20%) | 32.56: 137 (20%); 44.454: 271 (40%); 56.974: 406 (60%); 70.94: 541 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 37.702, 41.444, 44.412, 48.776 | 37.702: 541 (80%); 41.444: 406 (60%); 44.412: 271 (40%); 48.776: 136 (20%) | 37.702: 136 (20%); 41.444: 271 (40%); 44.412: 406 (60%); 48.776: 541 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 30.894, 37.104, 44.584, 53.496 | 30.894: 541 (80%); 37.104: 406 (60%); 44.584: 271 (40%); 53.496: 136 (20%) | 30.894: 136 (20%); 37.104: 271 (40%); 44.584: 406 (60%); 53.496: 541 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 677 (100%) | 0: 676 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0339, 0.0507, 0.068, 0.0934 | 0.0339: 544 (80%); 0.0507: 406 (60%); 0.068: 271 (40%); 0.0934: 136 (20%) | 0.0339: 136 (20%); 0.0507: 271 (40%); 0.068: 408 (60%); 0.0934: 541 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0743, -0.0569, -0.0438, -0.0341 | -0.0743: 541 (80%); -0.0569: 432 (64%); -0.0438: 273 (40%); -0.0341: 142 (21%) | -0.0743: 136 (20%); -0.0569: 274 (40%); -0.0438: 408 (60%); -0.0341: 542 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 677 (100%); 2: 169 (25%) | 0: 424 (63%); 2: 545 (81%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.9% | 41, 59, 65, 76 | 41: 542 (80%); 59: 407 (60%); 65: 275 (41%); 76: 139 (21%) | 41: 156 (23%); 59: 277 (41%); 65: 424 (63%); 76: 556 (82%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 99.1% | 0.0116, 0.0164, 0.0227, 0.0342 | 0.0116: 536 (79%); 0.0164: 402 (59%); 0.0227: 270 (40%); 0.0342: 134 (20%) | 0.0116: 135 (20%); 0.0164: 269 (40%); 0.0227: 401 (59%); 0.0342: 537 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.1192, 0.1995, 0.304, 0.4895 | 0.1192: 541 (80%); 0.1995: 406 (60%); 0.304: 271 (40%); 0.4895: 136 (20%) | 0.1192: 136 (20%); 0.1995: 271 (40%); 0.304: 406 (60%); 0.4895: 541 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 37.52, 66.08, 97.36, 135.98 | 37.52: 541 (80%); 66.08: 406 (60%); 97.36: 271 (40%); 135.98: 136 (20%) | 37.52: 136 (20%); 66.08: 271 (40%); 97.36: 406 (60%); 135.98: 541 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -10.0175, -4.268, -1.6485, 1.394 | -10.0175: 541 (80%); -4.268: 406 (60%); -1.6485: 271 (40%); 1.394: 136 (20%) | -10.0175: 136 (20%); -4.268: 271 (40%); -1.6485: 406 (60%); 1.394: 541 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 13.464, 23.156, 40.2, 63.776 | 13.464: 541 (80%); 23.156: 406 (60%); 40.2: 272 (40%); 63.776: 136 (20%) | 13.464: 136 (20%); 23.156: 271 (40%); 40.2: 407 (60%); 63.776: 541 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 12.752, 21.736, 37.802, 67.066 | 12.752: 541 (80%); 21.736: 406 (60%); 37.802: 271 (40%); 67.066: 136 (20%) | 12.752: 136 (20%); 21.736: 271 (40%); 37.802: 406 (60%); 67.066: 541 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 8.242, 25.49, 54.4, 86.57 | 8.242: 541 (80%); 25.49: 406 (60%); 54.4: 271 (40%); 86.57: 136 (20%) | 8.242: 136 (20%); 25.49: 271 (40%); 54.4: 406 (60%); 86.57: 541 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 10.802, 29.898, 56.568, 92.384 | 10.802: 541 (80%); 29.898: 406 (60%); 56.568: 271 (40%); 92.384: 136 (20%) | 10.802: 136 (20%); 29.898: 271 (40%); 56.568: 406 (60%); 92.384: 541 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 13, 17 | 5: 548 (81%); 9: 434 (64%); 13: 308 (45%); 17: 163 (24%) | 5: 169 (25%); 9: 274 (40%); 13: 415 (61%); 17: 549 (81%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 8, 13, 17 | 5: 548 (81%); 8: 439 (65%); 13: 275 (41%); 17: 167 (25%) | 5: 178 (26%); 8: 275 (41%); 13: 432 (64%); 17: 550 (81%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 37.416, 43.272, 48.574, 54.43 | 37.416: 541 (80%); 43.272: 406 (60%); 48.574: 271 (40%); 54.43: 137 (20%) | 37.416: 136 (20%); 43.272: 271 (40%); 48.574: 406 (60%); 54.43: 542 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.2341, 0.5873, 0.7524, 0.9167 | 0.2341: 542 (80%); 0.5873: 408 (60%); 0.7524: 271 (40%); 0.9167: 140 (21%) | 0.2341: 139 (21%); 0.5873: 274 (40%); 0.7524: 406 (60%); 0.9167: 557 (82%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.418, 17.44, 20.362, 24.17 | 15.418: 541 (80%); 17.44: 412 (61%); 20.362: 271 (40%); 24.17: 153 (23%) | 15.418: 136 (20%); 17.44: 272 (40%); 20.362: 406 (60%); 24.17: 542 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 15.418, 17.44, 20.362, 24.17 | 15.418: 541 (80%); 17.44: 412 (61%); 20.362: 271 (40%); 24.17: 153 (23%) | 15.418: 136 (20%); 17.44: 272 (40%); 20.362: 406 (60%); 24.17: 542 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8614, 0.8997, 0.9393, 0.982 | 0.8614: 542 (80%); 0.8997: 409 (60%); 0.9393: 273 (40%); 0.982: 139 (21%) | 0.8614: 136 (20%); 0.8997: 277 (41%); 0.9393: 408 (60%); 0.982: 557 (82%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.69, 0.834, 0.97, 1.198 | 0.69: 542 (80%); 0.834: 406 (60%); 0.97: 273 (40%); 1.198: 136 (20%) | 0.69: 141 (21%); 0.834: 271 (40%); 0.97: 414 (61%); 1.198: 541 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0267, 0.0521, 0.0805, 0.1225 | 0.0267: 542 (80%); 0.0521: 407 (60%); 0.0805: 271 (40%); 0.1225: 136 (20%) | 0.0267: 137 (20%); 0.0521: 272 (40%); 0.0805: 406 (60%); 0.1225: 542 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 47.9625, 80.6486, 118.9983, 209.0425 | 47.9625: 541 (80%); 80.6486: 406 (60%); 118.9983: 271 (40%); 209.0425: 136 (20%) | 47.9625: 136 (20%); 80.6486: 271 (40%); 118.9983: 406 (60%); 209.0425: 541 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 677 (100%) | 0: 613 (91%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 677 (100%) | 0: 600 (89%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.1128, -0.0695, -0.0318, 0.0134 | -0.1128: 542 (80%); -0.0695: 406 (60%); -0.0318: 271 (40%); 0.0134: 136 (20%) | -0.1128: 136 (20%); -0.0695: 271 (40%); -0.0318: 407 (60%); 0.0134: 541 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -84.344, -75.042, -59.316, -30.502 | -84.344: 541 (80%); -75.042: 406 (60%); -59.316: 271 (40%); -30.502: 136 (20%) | -84.344: 136 (20%); -75.042: 271 (40%); -59.316: 406 (60%); -30.502: 541 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.1% | 0.4996, 0.7246, 0.9606, 1.2508 | 0.4996: 537 (79%); 0.7246: 403 (60%); 0.9606: 269 (40%); 1.2508: 135 (20%) | 0.4996: 135 (20%); 0.7246: 269 (40%); 0.9606: 403 (60%); 1.2508: 537 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 5, 7, 9 | 3: 544 (80%); 5: 405 (60%); 7: 273 (40%); 9: 140 (21%) | 3: 193 (29%); 5: 326 (48%); 7: 459 (68%); 9: 599 (88%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.0% | 0.1915, 0.2254, 0.2675, 0.3427 | 0.1915: 536 (79%); 0.2254: 402 (59%); 0.2675: 268 (40%); 0.3427: 134 (20%) | 0.1915: 135 (20%); 0.2254: 269 (40%); 0.2675: 402 (59%); 0.3427: 536 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.0% | 3, 5, 7, 9 | 3: 551 (81%); 5: 420 (62%); 7: 280 (41%); 9: 148 (22%) | 3: 186 (27%); 5: 327 (48%); 7: 449 (66%); 9: 603 (89%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.1% | 0.0196, 0.0261, 0.0357, 0.052 | 0.0196: 538 (79%); 0.0261: 406 (60%); 0.0357: 269 (40%); 0.052: 135 (20%) | 0.0196: 135 (20%); 0.0261: 269 (40%); 0.0357: 404 (60%); 0.052: 537 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.1% | 2, 4, 6, 8 | 2: 580 (86%); 4: 422 (62%); 6: 293 (43%); 8: 169 (25%) | 2: 174 (26%); 4: 315 (47%); 6: 431 (64%); 8: 570 (84%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.3% | -0.0261, 0.0992, 0.2106, 0.3651 | -0.0261: 537 (79%); 0.0992: 403 (60%); 0.2106: 269 (40%); 0.3651: 135 (20%) | -0.0261: 135 (20%); 0.0992: 269 (40%); 0.2106: 403 (60%); 0.3651: 537 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.3% | 4, 6, 8, 9 | 4: 572 (84%); 6: 449 (66%); 8: 302 (45%); 9: 194 (29%) | 4: 165 (24%); 6: 293 (43%); 8: 478 (71%); 9: 567 (84%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 4.7% |
| 8k_item_5_02_filed_within_7d | 2.9% |
| above_avwap_20high | 22.3% |
| above_avwap_20low | 80.2% |
| above_avwap_252low | 50.2% |
| above_avwap_50low | 69.9% |
| above_cam_r3 | 41.1% |
| above_cam_r4 | 8.9% |
| above_cpr | 67.5% |
| above_pivot | 76.8% |
| above_r1 | 5.6% |
| above_wood_p | 49.9% |
| ad_rising | 48.6% |
| adx_cross_up | 5.6% |
| adx_cross_up_20 | 6.6% |
| adx_di_bear | 81.4% |
| adx_di_bull | 18.6% |
| adx_strong | 9.6% |
| adx_trending | 63.4% |
| ao_cross_dn | 2.2% |
| ao_cross_up | 1.0% |
| ao_positive | 20.4% |
| ao_twin_peaks_bull | 5.3% |
| at_key_fib | 10.5% |
| at_key_fib_wide | 27.6% |
| avwap_20high_loss_recent_3d | 12.4% |
| avwap_20high_reclaim_recent_3d | 15.2% |
| avwap_20low_loss_recent_3d | 8.7% |
| avwap_20low_reclaim_recent_3d | 43.3% |
| avwap_252low_loss_recent_3d | 12.0% |
| avwap_252low_reclaim_recent_3d | 10.0% |
| avwap_50low_loss_recent_3d | 10.5% |
| avwap_50low_reclaim_recent_3d | 32.5% |
| bb_10_20_above_mid | 36.3% |
| bb_10_20_expanding | 48.6% |
| bb_10_20_pctb_gt_75 | 14.9% |
| bb_10_20_pctb_gt_8 | 10.5% |
| bb_10_20_pctb_gt_85 | 7.1% |
| bb_10_20_pctb_gt_9 | 3.1% |
| bb_10_20_pctb_gt_95 | 1.6% |
| bb_10_20_pctb_lt_05 | 0.6% |
| bb_10_20_pctb_lt_1 | 4.6% |
| bb_10_20_pctb_lt_15 | 10.6% |
| bb_10_20_pctb_lt_2 | 21.0% |
| bb_10_20_pctb_lt_25 | 31.6% |
| bb_10_20_reclaim_from_lower_recent_3d | 23.2% |
| bb_10_20_reclaim_from_upper_recent_3d | 6.1% |
| bb_10_20_squeeze | 36.9% |
| bb_10_20_touch_lower | 0.9% |
| bb_10_20_touch_upper | 2.5% |
| bb_20_15_above_mid | 27.9% |
| bb_20_15_expanding | 52.3% |
| bb_20_15_pctb_gt_75 | 15.7% |
| bb_20_15_pctb_gt_8 | 13.1% |
| bb_20_15_pctb_gt_85 | 10.5% |
| bb_20_15_pctb_gt_9 | 8.6% |
| bb_20_15_pctb_gt_95 | 6.6% |
| bb_20_15_pctb_lt_05 | 31.6% |
| bb_20_15_pctb_lt_1 | 38.0% |
| bb_20_15_pctb_lt_15 | 44.6% |
| bb_20_15_pctb_lt_2 | 50.1% |
| bb_20_15_pctb_lt_25 | 54.9% |
| bb_20_15_reclaim_from_lower_recent_3d | 23.9% |
| bb_20_15_reclaim_from_upper_recent_3d | 5.6% |
| bb_20_15_squeeze | 31.2% |
| bb_20_15_touch_lower | 32.5% |
| bb_20_15_touch_upper | 7.2% |
| bb_20_20_above_mid | 27.9% |
| bb_20_20_expanding | 52.3% |
| bb_20_20_pctb_gt_75 | 11.7% |
| bb_20_20_pctb_gt_8 | 8.6% |
| bb_20_20_pctb_gt_85 | 6.2% |
| bb_20_20_pctb_gt_9 | 4.1% |
| bb_20_20_pctb_gt_95 | 3.2% |
| bb_20_20_pctb_lt_05 | 12.3% |
| bb_20_20_pctb_lt_1 | 20.7% |
| bb_20_20_pctb_lt_15 | 29.7% |
| bb_20_20_pctb_lt_2 | 38.0% |
| bb_20_20_pctb_lt_25 | 47.1% |
| bb_20_20_reclaim_from_lower_recent_3d | 26.7% |
| bb_20_20_reclaim_from_upper_recent_3d | 4.0% |
| bb_20_20_squeeze | 16.0% |
| bb_20_20_touch_lower | 10.3% |
| bb_20_20_touch_upper | 2.7% |
| bearish_pin_bar | 8.3% |
| below_avwap_20high | 77.7% |
| below_avwap_20low | 19.8% |
| below_avwap_252low | 49.8% |
| below_avwap_50low | 30.1% |
| below_cam_s3 | 1.5% |
| below_cpr | 23.2% |
| below_ema_20 | 75.5% |
| below_ema_200 | 67.8% |
| below_ema_200_break_recent_5d | 22.1% |
| below_ema_20_break_recent_5d | 19.2% |
| below_ema_21 | 75.6% |
| below_ema_21_break_recent_5d | 18.6% |
| below_ema_50 | 82.9% |
| below_ema_50_break_recent_5d | 18.6% |
| below_ema_9 | 66.9% |
| below_ema_9_break_recent_5d | 27.9% |
| below_sma_20 | 72.1% |
| below_sma_200 | 61.8% |
| below_sma_21 | 72.2% |
| below_sma_50 | 82.4% |
| below_sma_9 | 63.1% |
| break_52w_high_confirmed_today | 0.1% |
| bullish_engulfing | 4.3% |
| bullish_pin_bar | 7.8% |
| capitulation_recent_3d | 2.2% |
| ceo_buy | 0.9% |
| cfo_buy | 0.1% |
| chandelier_long_bullish | 35.9% |
| chandelier_long_flip_dn | 0.4% |
| chandelier_short_bearish | 80.1% |
| chandelier_short_flip_up | 2.4% |
| close_in_bottom_40pct_of_range | 12.3% |
| close_in_top_40pct_of_range | 67.9% |
| cluster_buy | 0.1% |
| cmf_cross_dn | 2.1% |
| cmf_cross_up | 5.0% |
| cmf_negative | 61.6% |
| cmf_positive | 38.4% |
| concentrated_sell | 7.9% |
| cpr_narrow | 93.5% |
| cpr_narrow_tight | 29.0% |
| cup_handle_detected | 11.5% |
| cup_handle_neckline_break_retest_long | 2.8% |
| dc10_breakout_dn | 0.1% |
| dc10_breakout_dn_1pct | 4.7% |
| dc10_breakout_up | 0.1% |
| dc10_breakout_up_1pct | 7.4% |
| dc20_breakout_dn | 0.1% |
| dc20_breakout_up | 0.1% |
| dc20_resistance_break_retest_strong | 9.0% |
| dc20_support_break_retest_strong | 34.0% |
| defensive_leadership | 62.0% |
| director_only_buy | 3.6% |
| doji | 6.5% |
| double_bottom_detected | 12.3% |
| double_top_detected | 16.2% |
| dpi_elevated | 45.2% |
| drying_volume_on_up_turn | 65.1% |
| ema_20_50_bearish | 73.6% |
| ema_20_50_bullish | 26.4% |
| ema_20_50_death_cross | 1.5% |
| ema_20_50_golden_cross | 0.3% |
| ema_50_200_bearish | 32.4% |
| ema_50_200_bullish | 67.6% |
| ema_50_200_death_cross | 0.9% |
| ema_50_200_golden_cross | 0.3% |
| ema_9_21_bearish | 80.6% |
| ema_9_21_bullish | 19.4% |
| ema_9_21_death_cross | 1.5% |
| ema_9_21_golden_cross | 1.0% |
| flag_bear_break_retest_short | 1.6% |
| flag_bear_broke | 1.6% |
| flag_bear_detected | 0.9% |
| flag_bull_break_retest_long | 1.6% |
| flag_bull_broke | 1.6% |
| flag_bull_detected | 1.8% |
| force_index_cross_dn | 0.3% |
| force_index_cross_up | 3.5% |
| force_index_positive | 28.5% |
| gap_dn_1_5pct | 3.0% |
| gap_dn_2pct | 1.2% |
| gap_up_1_5pct | 4.7% |
| gap_up_2pct | 2.8% |
| hammer | 4.3% |
| head_shoulders_bottom_detected | 2.5% |
| head_shoulders_top_detected | 6.8% |
| house_cluster_buy | 6.5% |
| house_cluster_sell | 5.8% |
| htf_aligned_bear | 52.4% |
| htf_aligned_bull | 11.5% |
| htf_disagreement | 3.7% |
| hull_bearish | 64.7% |
| hull_bullish | 35.3% |
| hull_flip_dn | 3.1% |
| hull_flip_up | 3.7% |
| ichi_above_cloud | 16.1% |
| ichi_above_cloud_break_recent_5d | 3.0% |
| ichi_below_cloud | 72.2% |
| ichi_below_cloud_break_recent_5d | 12.7% |
| ichi_cloud_thick | 82.0% |
| ichi_tk_bearish | 73.9% |
| ichi_tk_bullish | 19.5% |
| ichi_tk_cross_dn | 1.8% |
| ichi_tk_cross_up | 1.2% |
| ichi_weekly_above_cloud | 48.8% |
| ichi_weekly_below_cloud | 24.8% |
| ichi_weekly_in_cloud | 26.4% |
| inside_cpr | 10.6% |
| inside_kc | 80.8% |
| insider_cluster_active | 9.5% |
| institutional_buy | 84.5% |
| institutional_negative | 6.9% |
| institutional_persistence_growing | 45.4% |
| institutional_persistence_strong | 64.0% |
| institutional_strong_buy | 77.4% |
| inverted_cup_handle_detected | 12.1% |
| is_friday | 22.9% |
| is_halloween_period | 62.8% |
| is_halloween_period_first_day | 0.4% |
| is_january | 10.8% |
| is_january_extended | 12.3% |
| is_monday | 19.5% |
| is_pre_holiday | 5.6% |
| is_summer_period | 37.2% |
| is_totm_window | 34.6% |
| is_totm_window_first_day | 7.1% |
| is_week_open | 21.0% |
| kc_touch_lower | 21.1% |
| kc_touch_upper | 4.0% |
| large_dollar_buy | 0.9% |
| macd_12_26_9_bearish | 63.2% |
| macd_12_26_9_bullish | 36.8% |
| macd_12_26_9_crossover_dn | 1.8% |
| macd_12_26_9_crossover_up | 3.7% |
| macd_8_21_5_bearish | 58.3% |
| macd_8_21_5_bullish | 41.7% |
| macd_8_21_5_crossover_dn | 1.5% |
| macd_8_21_5_crossover_up | 3.8% |
| marubozu_bull | 0.7% |
| mfi_broad_overbought | 5.3% |
| mfi_broad_oversold | 16.5% |
| mfi_overbought | 0.7% |
| mfi_oversold | 3.7% |
| monthly_above_sma_12 | 40.3% |
| monthly_above_sma_6 | 23.4% |
| monthly_bias_bear | 56.5% |
| monthly_bias_bull | 20.2% |
| monthly_momentum_pos | 40.6% |
| morning_star | 3.8% |
| near_52w_high | 2.2% |
| near_52w_high_95pct | 5.2% |
| near_52w_high_retest_long | 2.1% |
| near_52w_low | 1.2% |
| near_52w_low_105pct | 5.0% |
| near_avwap_20high_atr_05x | 31.5% |
| near_avwap_20high_atr_10x | 51.6% |
| near_avwap_20high_atr_15x | 71.0% |
| near_avwap_20high_atr_20x | 86.1% |
| near_avwap_20low_atr_05x | 62.8% |
| near_avwap_20low_atr_10x | 82.1% |
| near_avwap_20low_atr_15x | 90.8% |
| near_avwap_20low_atr_20x | 95.1% |
| near_avwap_252low_atr_05x | 18.6% |
| near_avwap_252low_atr_10x | 35.9% |
| near_avwap_252low_atr_15x | 49.7% |
| near_avwap_252low_atr_20x | 60.8% |
| near_avwap_50low_atr_05x | 46.1% |
| near_avwap_50low_atr_10x | 67.2% |
| near_avwap_50low_atr_15x | 79.0% |
| near_avwap_50low_atr_20x | 85.7% |
| near_cam_r3 | 31.9% |
| near_cam_s3 | 5.3% |
| near_fib_236 | 1.0% |
| near_fib_382 | 1.8% |
| near_fib_500 | 3.2% |
| near_fib_618 | 5.5% |
| near_fib_786 | 9.2% |
| near_pivot | 30.1% |
| near_prev_close | 20.8% |
| near_prev_high | 5.9% |
| near_prev_low | 0.3% |
| near_r1 | 12.3% |
| near_r1_wide | 70.2% |
| near_r2_wide | 12.0% |
| near_s1_wide | 24.4% |
| near_s2_wide | 2.1% |
| near_wood_r1 | 8.7% |
| near_wood_s1 | 11.8% |
| news_uses_polygon_score | 35.6% |
| obv_bearish | 64.1% |
| obv_bullish | 35.9% |
| obv_diverge_bull | 12.3% |
| obv_falling | 56.9% |
| obv_rising | 43.1% |
| pead_negative_surprise | 13.6% |
| pead_positive_surprise | 20.9% |
| pin_bar | 16.1% |
| po3_accumulation_active | 26.1% |
| po3_bullish | 4.6% |
| po3_sweep_above_prior_high | 12.9% |
| po3_sweep_below_prior_low | 10.3% |
| ppo_bullish | 35.3% |
| ppo_crossover_dn | 1.5% |
| ppo_crossover_up | 2.7% |
| pre_fomc_d0 | 1.8% |
| pre_fomc_d1 | 3.2% |
| pre_fomc_window | 5.0% |
| price_above_dema | 43.1% |
| price_above_ema_20 | 24.5% |
| price_above_ema_200 | 32.2% |
| price_above_ema_200_break_recent_5d | 7.1% |
| price_above_ema_20_break_recent_5d | 13.0% |
| price_above_ema_21 | 24.4% |
| price_above_ema_21_break_recent_5d | 12.4% |
| price_above_ema_50 | 17.1% |
| price_above_ema_50_break_recent_5d | 5.3% |
| price_above_ema_9 | 33.1% |
| price_above_ema_9_break_recent_5d | 24.1% |
| price_above_hull | 49.8% |
| price_above_sma_200 | 38.2% |
| price_above_sma_21 | 27.8% |
| price_above_sma_50 | 17.6% |
| price_above_tema | 53.9% |
| price_below_dema | 56.9% |
| price_below_hull | 50.2% |
| price_below_tema | 46.1% |
| psar_bullish | 31.3% |
| r1_break_retest_long | 38.7% |
| resistance_break_retest | 10.8% |
| risk_off_regime_bond_signal | 25.8% |
| risk_off_regime_bond_signal_strong | 12.9% |
| risk_off_regime_gold_signal | 41.8% |
| risk_on_regime_bond_signal | 34.9% |
| risk_on_regime_bond_signal_strong | 12.9% |
| roc_positive | 31.9% |
| roc_turning_dn | 0.9% |
| roc_turning_up | 5.3% |
| rsi_14_bullish | 20.7% |
| rsi_14_cross_dn_overbought_recent_3d | 3.2% |
| rsi_14_cross_up_extreme_os_recent_3d | 1.2% |
| rsi_14_cross_up_oversold_recent_3d | 17.3% |
| rsi_14_extreme_os | 0.3% |
| rsi_14_overbought | 1.3% |
| rsi_14_oversold | 7.2% |
| rsi_14_rising | 82.4% |
| rsi_21_bullish | 18.0% |
| rsi_21_cross_dn_overbought_recent_3d | 0.7% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.1% |
| rsi_21_cross_up_oversold_recent_3d | 5.5% |
| rsi_21_overbought | 0.1% |
| rsi_21_oversold | 2.2% |
| rsi_21_rising | 82.4% |
| rsi_2_bullish | 52.0% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 22.6% |
| rsi_2_cross_dn_overbought_recent_3d | 27.6% |
| rsi_2_cross_up_extreme_os_recent_3d | 57.6% |
| rsi_2_cross_up_oversold_recent_3d | 60.9% |
| rsi_2_extreme_ob | 13.3% |
| rsi_2_extreme_os | 8.7% |
| rsi_2_overbought | 20.8% |
| rsi_2_oversold | 17.3% |
| rsi_2_rising | 82.4% |
| rsi_9_bullish | 26.3% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 1.0% |
| rsi_9_cross_dn_overbought_recent_3d | 5.3% |
| rsi_9_cross_up_extreme_os_recent_3d | 10.0% |
| rsi_9_cross_up_oversold_recent_3d | 23.2% |
| rsi_9_extreme_ob | 0.3% |
| rsi_9_extreme_os | 1.9% |
| rsi_9_overbought | 3.7% |
| rsi_9_oversold | 18.6% |
| rsi_9_rising | 82.4% |
| s1_break_retest_short | 64.0% |
| sc_13d_filed_within_30d | 1.5% |
| sc_13g_filed_within_30d | 1.1% |
| sector_outperforming_spy | 28.6% |
| sector_underperforming_spy | 71.4% |
| shooting_star | 7.1% |
| sma_20_50_bullish | 29.8% |
| sma_20_50_golden_cross | 0.4% |
| sma_50_200_bullish | 63.9% |
| sma_50_200_golden_cross | 0.4% |
| sma_9_21_bullish | 26.0% |
| sma_9_21_golden_cross | 1.8% |
| smc_bos_bearish | 16.0% |
| smc_bos_bullish | 9.7% |
| smc_bos_retest_long | 4.9% |
| smc_bos_retest_short | 3.7% |
| smc_breaker_block_bearish | 13.9% |
| smc_breaker_block_bullish | 35.9% |
| smc_choch_bearish | 10.9% |
| smc_choch_bullish | 2.8% |
| smc_equal_highs_swept | 3.8% |
| smc_equal_lows_swept | 4.4% |
| smc_fvg_bearish_active | 49.6% |
| smc_fvg_bullish_active | 24.7% |
| smc_fvg_retest_long_zone | 0.1% |
| smc_fvg_retest_short_zone | 8.9% |
| smc_in_discount_zone | 85.8% |
| smc_in_premium_zone | 28.1% |
| smc_inverse_fvg_bearish | 92.2% |
| smc_inverse_fvg_bullish | 58.2% |
| smc_liquidity_swept_dn | 1.5% |
| smc_liquidity_swept_up | 2.7% |
| smc_mitigation_block_long | 2.4% |
| smc_mitigation_block_short | 0.6% |
| smc_ob_bearish_active | 46.4% |
| smc_ob_bullish_active | 21.9% |
| smc_ote_long_zone | 12.1% |
| smc_ote_short_zone | 5.5% |
| squeeze_fire_dn | 0.4% |
| squeeze_fire_up | 2.5% |
| squeeze_in | 17.0% |
| squeeze_positive | 27.2% |
| stoch_bearish_cross | 7.4% |
| stoch_broad_overbought | 14.5% |
| stoch_broad_oversold | 45.3% |
| stoch_bullish_cross | 14.9% |
| stoch_overbought | 10.2% |
| stoch_oversold | 36.0% |
| stochrsi_cross_dn | 20.7% |
| stochrsi_cross_up | 40.8% |
| stochrsi_overbought | 28.5% |
| stochrsi_oversold | 31.5% |
| supertrend_bearish | 5.0% |
| supertrend_bullish | 95.0% |
| supertrend_flip_recent_long_5d | 4.3% |
| supertrend_flip_recent_short_5d | 6.2% |
| supertrend_flip_up | 0.6% |
| support_break_retest | 45.6% |
| tema_above_dema | 31.5% |
| tema_cross_dn | 1.9% |
| tema_cross_up | 2.1% |
| three_white_soldiers | 2.5% |
| triangle_apex_break_retest_long | 4.1% |
| triangle_ascending_detected | 4.1% |
| triangle_descending_detected | 8.9% |
| uo_overbought | 0.6% |
| uo_oversold | 4.6% |
| usd_strengthening | 21.6% |
| usd_weakening | 17.9% |
| vix_band_high | 54.8% |
| vix_band_low | 24.4% |
| vix_band_mid | 20.8% |
| vix_term_backwardation | 12.9% |
| vix_term_contango | 87.1% |
| vol_above_avg | 34.9% |
| vol_below_avg | 65.1% |
| vol_spike_12x | 19.5% |
| vol_spike_15x | 7.8% |
| vol_spike_17x | 4.7% |
| vol_spike_2x | 2.2% |
| vol_spike_2x_on_down_day_recent_3d | 12.7% |
| vol_spike_2x_on_up_day_recent_3d | 4.1% |
| vol_spike_3x | 0.3% |
| vp_above_value_area | 8.9% |
| vp_below_value_area | 40.9% |
| vp_close_above_poc | 25.7% |
| vp_close_below_poc | 74.3% |
| vp_in_value_area | 50.2% |
| week_open_gap_down_15pct | 0.3% |
| week_open_gap_up_15pct | 1.6% |
| weekly_above_ema_10 | 17.4% |
| weekly_above_ema_20 | 21.0% |
| weekly_bias_bear | 76.5% |
| weekly_bias_bull | 14.9% |
| weekly_momentum_pos | 24.5% |
| williams_r_overbought | 13.9% |
| williams_r_oversold | 29.8% |
| williams_r_rising | 82.6% |
| within_pead_window | 37.0% |
| within_post_inclusion_window | 1.7% |
| xs_avoid_high_ivol | 77.9% |
| xs_avoid_high_max | 84.9% |
| xs_high_beta_decile | 20.9% |
| xs_low_beta_bottom_quintile | 20.9% |
| xs_low_beta_decile | 18.9% |
| xs_low_beta_decile_entry_recent_5d | 0.3% |
| xs_low_beta_top_quintile | 18.9% |
| xs_momentum_bottom_decile | 2.1% |
| xs_momentum_bottom_quintile | 7.9% |
| xs_momentum_top_decile | 15.6% |
| xs_momentum_top_quintile | 28.9% |
| xs_quality_bottom_quintile | 16.3% |
| xs_quality_top_quintile | 23.6% |
| xs_quality_top_tercile | 42.0% |
| year_high_break_retest_long | 1.3% |
| year_low_break_retest_short | 1.2% |
| yoy_surprise_high | 52.7% |
| yoy_surprise_negative | 37.2% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.1% |
| committed_growth_holders | 91.1% |
| corp_donations_1y | 13.4% |
| corp_donations_count_1y | 13.4% |
| corp_donations_unique_pacs | 13.4% |
| cot_rut_commercials_pctile_3y | 73.4% |
| cot_rut_mmoney_pctile_3y | 73.4% |
| cup_handle_depth_pct | 18.9% |
| days_since_deletion | 5.2% |
| days_since_inclusion | 17.9% |
| days_to_next_holiday | 65.3% |
| days_to_rebalance | 4.4% |
| dpi_30d_avg | 96.8% |
| dpi_recent | 96.8% |
| earnings_announcement_return | 89.1% |
| earnings_eps_yoy_growth | 91.4% |
| flag_bear_pole_move_pct | 0.9% |
| flag_bull_pole_move_pct | 1.8% |
| gov_contracts_4q_sum | 42.8% |
| gov_contracts_last_qtr_amount | 42.8% |
| gov_contracts_qoq_growth | 42.8% |
| head_shoulders_magnitude_pct | 9.0% |
| insider_director_buyers_30d | 6.2% |
| insider_officer_buyers_30d | 6.2% |
| insider_total_shares_bought_30d | 6.2% |
| insider_unique_buyers_30d | 6.2% |
| inverted_cup_handle_height_pct | 22.3% |
| lobbying_amount_1y | 74.9% |
| lobbying_amount_q | 74.9% |
| lobbying_amount_yoy | 74.9% |
| monthly_momentum_6m | 97.2% |
| otc_short_ratio_recent | 96.8% |
| otc_volume_recent | 96.8% |
| pair_half_life | 92.8% |
| pair_max_abs_zscore | 92.8% |
| pair_zscore_signed | 92.8% |
| pct_from_avwap_252low | 97.5% |
| persistent_holders_4q | 91.1% |
| persistent_holders_8q | 91.1% |
| sc_13g_latest_percent_owned | 0.7% |
| search_volume_index_recent | 76.5% |
| search_volume_observations | 76.5% |
| search_volume_zscore_30d | 76.5% |
| sector_etf_return_20d | 2.1% |
| spy_return_20d | 2.1% |
| total_active_holders | 91.1% |
| triangle_breakdown_pct | 8.9% |
| triangle_breakout_pct | 4.1% |
| xs_quality_decile | 57.0% |
| xs_quality_gross_profitability | 57.0% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.998), `avwap_252low` (0.992), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.998), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.998), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.997), `cam_r2` (0.998), `cam_r3` (0.998), `cam_r4` (0.998), `cam_s1` (0.997), `cam_s2` (0.997), `cam_s3` (0.997), `cam_s4` (0.997), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.998), `cpr_top` (0.998), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.998), `dc10_lower` (0.998), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.998), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.993), `double_bottom_trough` (0.998), `double_top_neckline` (0.996), `double_top_peak` (0.998), `entry_stop_long` (0.997), `entry_stop_short` (0.998), `fib_236` (0.997), `fib_382` (0.997), `fib_500` (0.998), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.994), `fib_ext_162` (0.991), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.998), `head_shoulders_top_neckline` (0.995), `hull_ma` (0.998), `ichi_kijun` (0.999), `ichi_senkou_a` (0.995), `ichi_senkou_b` (0.992), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.998), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (0.999), `monthly_close` (0.998), `monthly_sma_12` (0.99), `monthly_sma_6` (0.995), `pivot` (0.998), `prev_close` (0.997), `prev_high` (0.998), `prev_low` (0.997), `psar_value` (0.998), `r1` (0.998), `r2` (0.998), `r3` (0.998), `s1` (0.997), `s2` (0.996), `s3` (0.995), `supertrend_value` (0.994), `swing_high` (0.995), `swing_low` (0.996), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.996), `vp_value_area_low` (0.996), `vwap` (0.968), `vwap_lower_1` (0.959), `vwap_upper_1` (0.974), `vwap_upper_2` (0.978), `weekly_close` (0.998), `weekly_ema_10` (0.999), `weekly_ema_20` (0.997), `wood_p` (0.998), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.998), `wood_s2` (0.997), `year_high` (0.989), `year_low` (0.968)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | buffer pct (price vs vwap) | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1 | (structural) h[-1]<h[-2] and l[-1]>l[-2] | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P3 | adx > 20 | 5 | subset-safe | no - derives offline |

```
FULL FACTORIAL     1 x 1 x 5 = 5
offline gradings   5 level-combinations x 24 exits = 120
ENGINE RUNS        1 (every fire-adding axis sits at production-only until its env actuator exists)
check              1 x 5 = 5
```

B-row candidates NOT in this factorial: 600 census axes join it only when REGISTERED at the T3 band review.
