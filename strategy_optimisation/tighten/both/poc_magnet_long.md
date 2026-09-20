# Table A - poc_magnet_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit f55b7c1e7 at 2026-09-19 23:26:39 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** volume_profile | **status:** STALLED-CAMPAIGN | **R5 fires:** 589 | **surviving fires (T1):** 589 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  price_above_ema_200  <- backtest/signals/index_rebalance.py +1
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P1.1-P1.1 (band rows in Table A)
P2  vp_close_above_poc  <- backtest/signals/screener.py +1
       DEFN: today's close above the 60d/40-bin volume-profile POC (volume_profile.py:140)
       knobs P2.1-P2.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  vp_close_near_poc_pct < 0.03   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_poc_magnet_long (docstring and return dropped):

```python
fires = s.get('vp_close_near_poc_pct', 1.0) < 0.03 and s.get('vp_close_above_poc', False) and s.get('price_above_ema_200', False)
dist = s.get('vp_close_near_poc_pct', 0.0)
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
| P1 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/index_rebalance.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | BRACKET production; 150/250 are the adjacent canon spans | 200 | 150, 200, 250 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | vp_close_above_poc - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | today's close above the 60d/40-bin volume-profile POC (volume_profile.py:140) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | profile (lookback_days, n_bins) + side rule - backtest/signals/volume_profile.py:46-58 | BRACKET production | (60, 40) | lookback [30, 60, 120]; bins [30, 40, 50] | none - POC at other params unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | STRATEGY | vp_close_near_poc_pct `< 0.03` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `< 0.03` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | `< 0.03` | 100.0% | TIGHTER = LOWER the ceiling: 0.0047 -> 121 (21%); 0.0095 -> 236 (40%); 0.0162 -> 355 (60%); 0.0226 -> 471 (80%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 14.924, 18.806, 21.774, 26.76 | 14.924: 471 (80%); 18.806: 353 (60%); 21.774: 236 (40%); 26.76: 118 (20%) | 14.924: 118 (20%); 18.806: 236 (40%); 21.774: 353 (60%); 26.76: 471 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 17.916, 20.664, 23.278, 27.224 | 17.916: 471 (80%); 20.664: 353 (60%); 23.278: 236 (40%); 27.224: 118 (20%) | 17.916: 118 (20%); 20.664: 236 (40%); 23.278: 353 (60%); 27.224: 471 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 19.216, 22.112, 24.958, 28.372 | 19.216: 471 (80%); 22.112: 353 (60%); 24.958: 236 (40%); 28.372: 118 (20%) | 19.216: 118 (20%); 22.112: 236 (40%); 24.958: 353 (60%); 28.372: 471 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -3.7771, -0.5914, 0.7779, 2.778 | -3.7771: 471 (80%); -0.5914: 353 (60%); 0.7779: 236 (40%); 2.778: 118 (20%) | -3.7771: 118 (20%); -0.5914: 236 (40%); 0.7779: 353 (60%); 2.778: 471 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.3172, 2.3192, 3.6831, 6.7081 | 1.3172: 471 (80%); 2.3192: 353 (60%); 3.6831: 236 (40%); 6.7081: 118 (20%) | 1.3172: 118 (20%); 2.3192: 236 (40%); 3.6831: 353 (60%); 6.7081: 471 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.3172, 2.3192, 3.6831, 6.7081 | 1.3172: 471 (80%); 2.3192: 353 (60%); 3.6831: 236 (40%); 6.7081: 118 (20%) | 1.3172: 118 (20%); 2.3192: 236 (40%); 3.6831: 353 (60%); 6.7081: 471 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.9864, 2.3894, 2.8602, 3.541 | 1.9864: 471 (80%); 2.3894: 353 (60%); 2.8602: 236 (40%); 3.541: 119 (20%) | 1.9864: 118 (20%); 2.3894: 236 (40%); 2.8602: 353 (60%); 3.541: 472 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0485, 0.0669, 0.0969, 0.144 | 0.0485: 472 (80%); 0.0669: 353 (60%); 0.0969: 237 (40%); 0.144: 118 (20%) | 0.0485: 119 (20%); 0.0669: 236 (40%); 0.0969: 354 (60%); 0.144: 471 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.3766, 0.5729, 0.7296, 0.8602 | 0.3766: 471 (80%); 0.5729: 354 (60%); 0.7296: 236 (40%); 0.8602: 119 (20%) | 0.3766: 118 (20%); 0.5729: 236 (40%); 0.7296: 354 (60%); 0.8602: 471 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0515, 0.0734, 0.0973, 0.1311 | 0.0515: 471 (80%); 0.0734: 353 (60%); 0.0973: 236 (40%); 0.1311: 118 (20%) | 0.0515: 118 (20%); 0.0734: 236 (40%); 0.0973: 354 (60%); 0.1311: 471 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.3004, 0.5607, 0.7552, 0.9604 | 0.3004: 471 (80%); 0.5607: 353 (60%); 0.7552: 236 (40%); 0.9604: 118 (20%) | 0.3004: 118 (20%); 0.5607: 236 (40%); 0.7552: 353 (60%); 0.9604: 471 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0686, 0.0979, 0.1298, 0.1749 | 0.0686: 471 (80%); 0.0979: 353 (60%); 0.1298: 236 (40%); 0.1749: 118 (20%) | 0.0686: 118 (20%); 0.0979: 236 (40%); 0.1298: 354 (60%); 0.1749: 471 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.3503, 0.5456, 0.6914, 0.8452 | 0.3503: 471 (80%); 0.5456: 353 (60%); 0.6914: 236 (40%); 0.8452: 118 (20%) | 0.3503: 118 (20%); 0.5456: 236 (40%); 0.6914: 353 (60%); 0.8452: 471 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0448, -0.0196, 0.0022, 0.0263 | -0.0448: 471 (80%); -0.0196: 358 (61%); 0.0022: 237 (40%); 0.0263: 118 (20%) | -0.0448: 118 (20%); -0.0196: 241 (41%); 0.0022: 355 (60%); 0.0263: 471 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1373, 0.1621, 0.2015, 0.261 | 0.1373: 470 (80%); 0.1621: 353 (60%); 0.2015: 236 (40%); 0.261: 118 (20%) | 0.1373: 119 (20%); 0.1621: 236 (40%); 0.2015: 353 (60%); 0.261: 471 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 589 (100%) | 0: 570 (97%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0814, -0.0063, 0.0656, 0.1396 | -0.0814: 471 (80%); -0.0063: 353 (60%); 0.0656: 236 (40%); 0.1396: 118 (20%) | -0.0814: 118 (20%); -0.0063: 236 (40%); 0.0656: 353 (60%); 0.1396: 471 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 589 (100%); 1: 232 (39%) | 0: 357 (61%); 1: 489 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2461, -0.2015, -0.1579, -0.1197 | -0.2461: 473 (80%); -0.2015: 355 (60%); -0.1579: 238 (40%); -0.1197: 119 (20%) | -0.2461: 119 (20%); -0.2015: 237 (40%); -0.1579: 354 (60%); -0.1197: 474 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3013, 0.6026, 0.6859, 0.7692 | 0.3013: 473 (80%); 0.6026: 357 (61%); 0.6859: 238 (40%); 0.7692: 139 (24%) | 0.3013: 119 (20%); 0.6026: 245 (42%); 0.6859: 354 (60%); 0.7692: 488 (83%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2692, 0.4295, 0.6128, 0.8539 | 0.2692: 474 (80%); 0.4295: 358 (61%); 0.6128: 236 (40%); 0.8539: 118 (20%) | 0.2692: 122 (21%); 0.4295: 250 (42%); 0.6128: 353 (60%); 0.8539: 471 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0921, -0.0184, 0.0374, 0.1946 | -0.0921: 475 (81%); -0.0184: 363 (62%); 0.0374: 237 (40%); 0.1946: 119 (20%) | -0.0921: 119 (20%); -0.0184: 237 (40%); 0.0374: 355 (60%); 0.1946: 472 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.4551, 0.5513, 0.7628 | 0.2628: 475 (81%); 0.4551: 361 (61%); 0.5513: 239 (41%); 0.7628: 119 (20%) | 0.2628: 120 (20%); 0.4551: 247 (42%); 0.5513: 355 (60%); 0.7628: 472 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1346, 0.2949, 0.4551, 0.6667 | 0.1346: 473 (80%); 0.2949: 359 (61%); 0.4551: 269 (46%); 0.6667: 123 (21%) | 0.1346: 124 (21%); 0.2949: 239 (41%); 0.4551: 358 (61%); 0.6667: 472 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.4904, -0.3066, -0.1164, 0.0848 | -0.4904: 473 (80%); -0.3066: 358 (61%); -0.1164: 237 (40%); 0.0848: 118 (20%) | -0.4904: 119 (20%); -0.3066: 239 (41%); -0.1164: 355 (60%); 0.0848: 471 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3846, 0.5398, 0.7821, 0.9167 | 0.3846: 478 (81%); 0.5398: 353 (60%); 0.7821: 239 (41%); 0.9167: 144 (24%) | 0.3846: 126 (21%); 0.5398: 236 (40%); 0.7821: 354 (60%); 0.9167: 472 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1282, 0.3333, 0.5641, 0.8526 | 0.1282: 473 (80%); 0.3333: 356 (60%); 0.5641: 238 (40%); 0.8526: 146 (25%) | 0.1282: 119 (20%); 0.3333: 240 (41%); 0.5641: 354 (60%); 0.8526: 477 (81%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0659, -0.0577, -0.0372, 0 | -0.0659: 471 (80%); -0.0577: 355 (60%); -0.0372: 240 (41%); 0: 201 (34%) | -0.0659: 118 (20%); -0.0577: 236 (40%); -0.0372: 355 (60%); 0: 571 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4141, 0.6808, 0.8974, 1 | 0.4141: 471 (80%); 0.6808: 353 (60%); 0.8974: 242 (41%); 1: 155 (26%) | 0.4141: 118 (20%); 0.6808: 236 (40%); 0.8974: 355 (60%); 1: 589 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1384, 0.309, 0.5449, 0.8795 | 0.1384: 471 (80%); 0.309: 353 (60%); 0.5449: 239 (41%); 0.8795: 118 (20%) | 0.1384: 118 (20%); 0.309: 236 (40%); 0.5449: 355 (60%); 0.8795: 471 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0013, 0.04, 0.1031, 0.2489 | 0.0013: 472 (80%); 0.04: 354 (60%); 0.1031: 237 (40%); 0.2489: 136 (23%) | 0.0013: 128 (22%); 0.04: 237 (40%); 0.1031: 354 (60%); 0.2489: 487 (83%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4965, 0.8026, 0.9487, 0.9744 | 0.4965: 472 (80%); 0.8026: 353 (60%); 0.9487: 238 (40%); 0.9744: 164 (28%) | 0.4965: 119 (20%); 0.8026: 236 (40%); 0.9487: 364 (62%); 0.9744: 494 (84%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0962, 0.2949, 0.5577, 0.7795 | 0.0962: 472 (80%); 0.2949: 355 (60%); 0.5577: 237 (40%); 0.7795: 118 (20%) | 0.0962: 124 (21%); 0.2949: 268 (46%); 0.5577: 363 (62%); 0.7795: 471 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0203, 0.0667, 0.1474 | -0.0812: 484 (82%); -0.0203: 380 (65%); 0.0667: 236 (40%); 0.1474: 118 (20%) | -0.0812: 157 (27%); -0.0203: 239 (41%); 0.0667: 353 (60%); 0.1474: 471 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2669, -0.0425, 0.0253, 0.0916 | -0.2669: 478 (81%); -0.0425: 356 (60%); 0.0253: 236 (40%); 0.0916: 121 (21%) | -0.2669: 122 (21%); -0.0425: 237 (40%); 0.0253: 353 (60%); 0.0916: 472 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.5321, 0.7051, 0.8705 | 0.2628: 482 (82%); 0.5321: 354 (60%); 0.7051: 238 (40%); 0.8705: 118 (20%) | 0.2628: 141 (24%); 0.5321: 243 (41%); 0.7051: 355 (60%); 0.8705: 471 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1795, 0.4103, 0.5641, 0.8205 | 0.1795: 473 (80%); 0.4103: 358 (61%); 0.5641: 270 (46%); 0.8205: 119 (20%) | 0.1795: 125 (21%); 0.4103: 244 (41%); 0.5641: 358 (61%); 0.8205: 476 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.055, 0.1483, 0.27, 0.5997 | 0.055: 472 (80%); 0.1483: 354 (60%); 0.27: 237 (40%); 0.5997: 118 (20%) | 0.055: 121 (21%); 0.1483: 237 (40%); 0.27: 354 (60%); 0.5997: 471 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.8% | 19.2, 61, 82, 138 | 19.2: 465 (79%); 61: 352 (60%); 82: 235 (40%); 138: 120 (20%) | 19.2: 117 (20%); 61: 246 (42%); 82: 354 (60%); 138: 467 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.8% | 1.7023, 2.2506, 2.8931, 3.9398 | 1.7023: 470 (80%); 2.2506: 353 (60%); 2.8931: 235 (40%); 3.9398: 118 (20%) | 1.7023: 118 (20%); 2.2506: 235 (40%); 2.8931: 353 (60%); 3.9398: 470 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 9, 21, 28, 35 | 9: 487 (83%); 21: 354 (60%); 28: 250 (42%); 35: 131 (22%) | 9: 120 (20%); 21: 248 (42%); 28: 383 (65%); 35: 472 (80%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 4 | 1: 478 (81%); 2: 349 (59%); 4: 128 (22%) | 1: 240 (41%); 2: 363 (62%); 4: 589 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0155, -0.0054, 0.0068, 0.0201 | -0.0155: 472 (80%); -0.0054: 354 (60%); 0.0068: 236 (40%); 0.0201: 118 (20%) | -0.0155: 120 (20%); -0.0054: 236 (40%); 0.0068: 353 (60%); 0.0201: 471 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.4768, 25.7272, 26.5725, 27.279 | 24.4768: 471 (80%); 25.7272: 353 (60%); 26.5725: 237 (40%); 27.279: 118 (20%) | 24.4768: 118 (20%); 25.7272: 236 (40%); 26.5725: 354 (60%); 27.279: 471 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.5464, -0.0956, 0.2512, 0.663 | -0.5464: 471 (80%); -0.0956: 353 (60%); 0.2512: 236 (40%); 0.663: 118 (20%) | -0.5464: 118 (20%); -0.0956: 236 (40%); 0.2512: 353 (60%); 0.663: 471 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.663, -0.2512, 0.0956, 0.5464 | -0.663: 471 (80%); -0.2512: 353 (60%); 0.0956: 236 (40%); 0.5464: 118 (20%) | -0.663: 118 (20%); -0.2512: 236 (40%); 0.0956: 353 (60%); 0.5464: 471 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0398, -0.0115, 0.026, 0.0708 | -0.0398: 471 (80%); -0.0115: 356 (60%); 0.026: 237 (40%); 0.0708: 118 (20%) | -0.0398: 118 (20%); -0.0115: 237 (40%); 0.026: 356 (60%); 0.0708: 471 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.9845, 8.4837, 8.767, 9.0266 | 7.9845: 471 (80%); 8.4837: 352 (60%); 8.767: 237 (40%); 9.0266: 118 (20%) | 7.9845: 118 (20%); 8.4837: 237 (40%); 8.767: 352 (60%); 9.0266: 471 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.7% | 0, 1 | 0: 587 (100%); 1: 188 (32%) | 0: 399 (68%); 1: 514 (87%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.7% | 0 | 0: 475 (81%) | 0: 476 (81%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.7% | 0, 1 | 0: 587 (100%); 1: 191 (32%) | 0: 396 (67%); 1: 523 (89%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 4, 14.8, 261.4 | 2: 475 (81%); 4: 387 (66%); 14.8: 236 (40%); 261.4: 118 (20%) | 2: 167 (28%); 4: 241 (41%); 14.8: 353 (60%); 261.4: 471 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 0, 3, 74.8, 144 | 0: 589 (100%); 3: 358 (61%); 74.8: 236 (40%); 144: 119 (20%) | 0: 129 (22%); 3: 256 (43%); 74.8: 353 (60%); 144: 472 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.7032, -0.1718, 0.1275, 0.5931 | -0.7032: 471 (80%); -0.1718: 353 (60%); 0.1275: 236 (40%); 0.5931: 118 (20%) | -0.7032: 118 (20%); -0.1718: 236 (40%); 0.1275: 353 (60%); 0.5931: 471 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -0.9959, -0.1422, 0.324, 1.0478 | -0.9959: 471 (80%); -0.1422: 353 (60%); 0.324: 236 (40%); 1.0478: 118 (20%) | -0.9959: 118 (20%); -0.1422: 236 (40%); 0.324: 353 (60%); 1.0478: 471 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.0258, -0.1876, 0.3398, 1.2064 | -1.0258: 471 (80%); -0.1876: 353 (60%); 0.3398: 236 (40%); 1.2064: 118 (20%) | -1.0258: 118 (20%); -0.1876: 236 (40%); 0.3398: 353 (60%); 1.2064: 471 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.403, -0.0469, 0.167, 0.5487 | -0.403: 471 (80%); -0.0469: 353 (60%); 0.167: 236 (40%); 0.5487: 118 (20%) | -0.403: 118 (20%); -0.0469: 236 (40%); 0.167: 353 (60%); 0.5487: 471 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -1.2516, -0.1556, 0.4439, 1.3225 | -1.2516: 471 (80%); -0.1556: 353 (60%); 0.4439: 236 (40%); 1.3225: 118 (20%) | -1.2516: 118 (20%); -0.1556: 236 (40%); 0.4439: 353 (60%); 1.3225: 471 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -1.3813, -0.1986, 0.3704, 1.1125 | -1.3813: 471 (80%); -0.1986: 353 (60%); 0.3704: 236 (40%); 1.1125: 118 (20%) | -1.3813: 118 (20%); -0.1986: 236 (40%); 0.3704: 353 (60%); 1.1125: 471 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 40.05, 48.536, 55.902, 63.736 | 40.05: 471 (80%); 48.536: 353 (60%); 55.902: 236 (40%); 63.736: 118 (20%) | 40.05: 118 (20%); 48.536: 236 (40%); 55.902: 353 (60%); 63.736: 471 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.3% | 0.0033, 0.0073, 0.0132, 0.0206 | 0.0033: 468 (79%); 0.0073: 351 (60%); 0.0132: 234 (40%); 0.0206: 116 (20%) | 0.0033: 117 (20%); 0.0073: 234 (40%); 0.0132: 351 (60%); 0.0206: 469 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1.2, 4, 10 | 0: 589 (100%); 1.2: 353 (60%); 4: 245 (42%); 10: 122 (21%) | 0: 152 (26%); 1.2: 236 (40%); 4: 376 (64%); 10: 479 (81%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1356 | 0: 589 (100%); 0.1356: 118 (20%) | 0: 405 (69%); 0.1356: 471 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1776, 0.4271, 0.6667 | 0: 589 (100%); 0.1776: 353 (60%); 0.4271: 236 (40%); 0.6667: 138 (23%) | 0: 224 (38%); 0.1776: 236 (40%); 0.4271: 353 (60%); 0.6667: 476 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 2, 7 | 0: 589 (100%); 1: 411 (70%); 2: 307 (52%); 7: 120 (20%) | 0: 178 (30%); 1: 282 (48%); 2: 354 (60%); 7: 485 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1.2, 4, 10 | 0: 589 (100%); 1.2: 353 (60%); 4: 245 (42%); 10: 122 (21%) | 0: 152 (26%); 1.2: 236 (40%); 4: 376 (64%); 10: 479 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 589 (100%); 1: 417 (71%); 3: 265 (45%); 8: 127 (22%) | 0: 172 (29%); 1: 269 (46%); 3: 361 (61%); 8: 475 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.0827, 0.2691, 0.4091, 0.6456 | 0.0827: 471 (80%); 0.2691: 353 (60%); 0.4091: 236 (40%); 0.6456: 118 (20%) | 0.0827: 118 (20%); 0.2691: 236 (40%); 0.4091: 353 (60%); 0.6456: 471 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2296, 0.625 | 0: 546 (93%); 0.2296: 236 (40%); 0.625: 119 (20%) | 0: 312 (53%); 0.2296: 353 (60%); 0.625: 472 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.302, 0.6 | 0: 552 (94%); 0.302: 236 (40%); 0.6: 123 (21%) | 0: 258 (44%); 0.302: 353 (60%); 0.6: 473 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.302, 0.6 | 0: 552 (94%); 0.302: 236 (40%); 0.6: 123 (21%) | 0: 258 (44%); 0.302: 353 (60%); 0.6: 473 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1472, 0, 0.114 | -0.1472: 471 (80%); 0: 422 (72%); 0.114: 118 (20%) | -0.1472: 118 (20%); 0: 434 (74%); 0.114: 471 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.7571, -0.4439, 0.1259, 1.368 | -0.7571: 472 (80%); -0.4439: 353 (60%); 0.1259: 236 (40%); 1.368: 118 (20%) | -0.7571: 122 (21%); -0.4439: 236 (40%); 0.1259: 353 (60%); 1.368: 471 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 5, 8, 12 | 2: 498 (85%); 5: 372 (63%); 8: 247 (42%); 12: 125 (21%) | 2: 134 (23%); 5: 260 (44%); 8: 377 (64%); 12: 490 (83%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0298, 0.0012, 0.0197, 0.0536 | -0.0298: 471 (80%); 0.0012: 353 (60%); 0.0197: 236 (40%); 0.0536: 116 (20%) | -0.0298: 118 (20%); 0.0012: 236 (40%); 0.0197: 353 (60%); 0.0536: 473 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0364, -0.0023, 0.0239, 0.059 | -0.0364: 471 (80%); -0.0023: 353 (60%); 0.0239: 236 (40%); 0.059: 117 (20%) | -0.0364: 118 (20%); -0.0023: 236 (40%); 0.0239: 353 (60%); 0.059: 472 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0193, 0.004, 0.019, 0.0408 | -0.0193: 471 (80%); 0.004: 353 (60%); 0.019: 236 (40%); 0.0408: 118 (20%) | -0.0193: 118 (20%); 0.004: 236 (40%); 0.019: 353 (60%); 0.0408: 471 (80%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 98.5% | -0.2772, 1.939, 3.5646, 5.6146 | -0.2772: 464 (79%); 1.939: 348 (59%); 3.5646: 232 (39%); 5.6146: 116 (20%) | -0.2772: 116 (20%); 1.939: 232 (39%); 3.5646: 348 (59%); 5.6146: 464 (79%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -2.0714, 4.9918, 13.0806, 31.7086 | -2.0714: 471 (80%); 4.9918: 353 (60%); 13.0806: 236 (40%); 31.7086: 118 (20%) | -2.0714: 118 (20%); 4.9918: 236 (40%); 13.0806: 353 (60%); 31.7086: 471 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0372, 0.0509, 0.0708, 0.1034 | 0.0372: 471 (80%); 0.0509: 353 (60%); 0.0708: 236 (40%); 0.1034: 118 (20%) | 0.0372: 120 (20%); 0.0509: 236 (40%); 0.0708: 353 (60%); 0.1034: 471 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.5357, 0.6948, 0.8062, 0.9138 | 0.5357: 471 (80%); 0.6948: 353 (60%); 0.8062: 236 (40%); 0.9138: 118 (20%) | 0.5357: 118 (20%); 0.6948: 236 (40%); 0.8062: 353 (60%); 0.9138: 471 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -0.8294, -0.206, 0.3886, 0.9721 | -0.8294: 471 (80%); -0.206: 353 (60%); 0.3886: 236 (40%); 0.9721: 118 (20%) | -0.8294: 118 (20%); -0.206: 236 (40%); 0.3886: 353 (60%); 0.9721: 471 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.577, -0.2166, 0.159, 0.5759 | -0.577: 471 (80%); -0.2166: 353 (60%); 0.159: 236 (40%); 0.5759: 118 (20%) | -0.577: 118 (20%); -0.2166: 236 (40%); 0.159: 353 (60%); 0.5759: 471 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -0.9198, -0.2232, 0.4448, 1.0869 | -0.9198: 471 (80%); -0.2232: 353 (60%); 0.4448: 236 (40%); 1.0869: 118 (20%) | -0.9198: 118 (20%); -0.2232: 236 (40%); 0.4448: 353 (60%); 1.0869: 471 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -3.539, -0.0438, 2.135, 5.8478 | -3.539: 471 (80%); -0.0438: 353 (60%); 2.135: 236 (40%); 5.8478: 118 (20%) | -3.539: 118 (20%); -0.0438: 236 (40%); 2.135: 353 (60%); 5.8478: 471 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 46.904, 51.382, 55.228, 58.962 | 46.904: 471 (80%); 51.382: 353 (60%); 55.228: 236 (40%); 58.962: 118 (20%) | 46.904: 118 (20%); 51.382: 236 (40%); 55.228: 353 (60%); 58.962: 471 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 49.088, 69.412, 81.458, 90.394 | 49.088: 471 (80%); 69.412: 353 (60%); 81.458: 236 (40%); 90.394: 118 (20%) | 49.088: 118 (20%); 69.412: 236 (40%); 81.458: 353 (60%); 90.394: 471 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 48.084, 51.022, 53.73, 56.68 | 48.084: 471 (80%); 51.022: 353 (60%); 53.73: 236 (40%); 56.68: 119 (20%) | 48.084: 118 (20%); 51.022: 236 (40%); 53.73: 353 (60%); 56.68: 472 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 45.61, 52.69, 57.474, 63.448 | 45.61: 471 (80%); 52.69: 353 (60%); 57.474: 236 (40%); 63.448: 118 (20%) | 45.61: 118 (20%); 52.69: 236 (40%); 57.474: 353 (60%); 63.448: 471 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 587 (100%) | 0: 589 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0298, 0.0447, 0.0597, 0.0865 | 0.0298: 472 (80%); 0.0447: 354 (60%); 0.0597: 236 (40%); 0.0865: 119 (20%) | 0.0298: 121 (21%); 0.0447: 236 (40%); 0.0597: 354 (60%); 0.0865: 472 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0832, -0.0604, -0.0448, -0.0348 | -0.0832: 471 (80%); -0.0604: 355 (60%); -0.0448: 236 (40%); -0.0348: 119 (20%) | -0.0832: 121 (21%); -0.0604: 236 (40%); -0.0448: 353 (60%); -0.0348: 471 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 3 | 0: 589 (100%); 3: 125 (21%) | 0: 364 (62%); 3: 492 (84%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.8% | 28, 45, 60, 69.6 | 28: 487 (83%); 45: 354 (60%); 60: 247 (42%); 69.6: 118 (20%) | 28: 135 (23%); 45: 261 (44%); 60: 362 (61%); 69.6: 470 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 99.0% | 0.011, 0.0157, 0.0225, 0.0354 | 0.011: 466 (79%); 0.0157: 351 (60%); 0.0225: 233 (40%); 0.0354: 117 (20%) | 0.011: 117 (20%); 0.0157: 232 (39%); 0.0225: 350 (59%); 0.0354: 466 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.3728, 0.5074, 0.6475, 0.7792 | 0.3728: 471 (80%); 0.5074: 353 (60%); 0.6475: 236 (40%); 0.7792: 118 (20%) | 0.3728: 118 (20%); 0.5074: 236 (40%); 0.6475: 353 (60%); 0.7792: 471 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 36.32, 53.1, 68.08, 94.14 | 36.32: 471 (80%); 53.1: 354 (60%); 68.08: 236 (40%); 94.14: 118 (20%) | 36.32: 118 (20%); 53.1: 237 (40%); 68.08: 353 (60%); 94.14: 471 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -2, 0.14, 1.791, 5.041 | -2: 471 (80%); 0.14: 353 (60%); 1.791: 236 (40%); 5.041: 118 (20%) | -2: 118 (20%); 0.14: 236 (40%); 1.791: 353 (60%); 5.041: 471 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 25.026, 41.382, 61.364, 77.936 | 25.026: 471 (80%); 41.382: 353 (60%); 61.364: 236 (40%); 77.936: 118 (20%) | 25.026: 118 (20%); 41.382: 236 (40%); 61.364: 353 (60%); 77.936: 471 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 28.028, 44.022, 64.958, 81.176 | 28.028: 471 (80%); 44.022: 353 (60%); 64.958: 236 (40%); 81.176: 118 (20%) | 28.028: 118 (20%); 44.022: 236 (40%); 64.958: 353 (60%); 81.176: 471 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 12.96, 33.378, 64.284, 90.384 | 12.96: 471 (80%); 33.378: 353 (60%); 64.284: 236 (40%); 90.384: 118 (20%) | 12.96: 118 (20%); 33.378: 236 (40%); 64.284: 353 (60%); 90.384: 471 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 18.564, 44.624, 73.708, 100 | 18.564: 471 (80%); 44.624: 353 (60%); 73.708: 236 (40%); 100: 128 (22%) | 18.564: 118 (20%); 44.624: 236 (40%); 73.708: 353 (60%); 100: 589 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 7, 12, 17 | 4: 483 (82%); 7: 386 (66%); 12: 248 (42%); 17: 125 (21%) | 4: 130 (22%); 7: 238 (40%); 12: 366 (62%); 17: 488 (83%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 15, 18 | 5: 482 (82%); 10: 365 (62%); 15: 240 (41%); 18: 138 (23%) | 5: 131 (22%); 10: 247 (42%); 15: 388 (66%); 18: 494 (84%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 46.06, 50.6, 55.17, 59.4 | 46.06: 471 (80%); 50.6: 353 (60%); 55.17: 237 (40%); 59.4: 119 (20%) | 46.06: 118 (20%); 50.6: 236 (40%); 55.17: 354 (60%); 59.4: 472 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.123, 0.3452, 0.6865, 0.8921 | 0.123: 473 (80%); 0.3452: 354 (60%); 0.6865: 238 (40%); 0.8921: 118 (20%) | 0.123: 120 (20%); 0.3452: 237 (40%); 0.6865: 354 (60%); 0.8921: 471 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.722, 17.284, 20.58, 25.38 | 14.722: 471 (80%); 17.284: 353 (60%); 20.58: 237 (40%); 25.38: 118 (20%) | 14.722: 118 (20%); 17.284: 236 (40%); 20.58: 354 (60%); 25.38: 471 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 14.722, 17.284, 20.58, 25.38 | 14.722: 471 (80%); 17.284: 353 (60%); 20.58: 237 (40%); 25.38: 118 (20%) | 14.722: 118 (20%); 17.284: 236 (40%); 20.58: 354 (60%); 25.38: 471 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8555, 0.8872, 0.9237, 0.969 | 0.8555: 472 (80%); 0.8872: 353 (60%); 0.9237: 236 (40%); 0.969: 118 (20%) | 0.8555: 119 (20%); 0.8872: 236 (40%); 0.9237: 353 (60%); 0.969: 471 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.676, 0.82, 0.95, 1.24 | 0.676: 471 (80%); 0.82: 359 (61%); 0.95: 245 (42%); 1.24: 120 (20%) | 0.676: 118 (20%); 0.82: 239 (41%); 0.95: 354 (60%); 1.24: 472 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 48.7298, 78.8598, 116.2163, 187.6526 | 48.7298: 471 (80%); 78.8598: 353 (60%); 116.2163: 236 (40%); 187.6526: 118 (20%) | 48.7298: 118 (20%); 78.8598: 236 (40%); 116.2163: 353 (60%); 187.6526: 471 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 47.2203, 75.4505, 110.8816, 179.6057 | 47.2203: 471 (80%); 75.4505: 353 (60%); 110.8816: 236 (40%); 179.6057: 118 (20%) | 47.2203: 118 (20%); 75.4505: 236 (40%); 110.8816: 353 (60%); 179.6057: 471 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 44.4606, 72.7379, 106.3481, 171.6061 | 44.4606: 471 (80%); 72.7379: 353 (60%); 106.3481: 236 (40%); 171.6061: 118 (20%) | 44.4606: 118 (20%); 72.7379: 236 (40%); 106.3481: 353 (60%); 171.6061: 471 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 589 (100%) | 0: 516 (88%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 589 (100%) | 0: 537 (91%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0328, 0.001, 0.0245, 0.0557 | -0.0328: 471 (80%); 0.001: 354 (60%); 0.0245: 236 (40%); 0.0557: 119 (20%) | -0.0328: 119 (20%); 0.001: 236 (40%); 0.0245: 356 (60%); 0.0557: 471 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -64.876, -46.86, -27.274, -10.308 | -64.876: 471 (80%); -46.86: 353 (60%); -27.274: 236 (40%); -10.308: 118 (20%) | -64.876: 118 (20%); -46.86: 236 (40%); -27.274: 353 (60%); -10.308: 471 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.0% | 0.5191, 0.7781, 1.0053, 1.2771 | 0.5191: 467 (79%); 0.7781: 350 (59%); 1.0053: 233 (40%); 1.2771: 117 (20%) | 0.5191: 117 (20%); 0.7781: 233 (40%); 1.0053: 350 (59%); 1.2771: 466 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.0% | 3, 5, 7, 9 | 3: 471 (80%); 5: 359 (61%); 7: 245 (42%); 9: 131 (22%) | 3: 176 (30%); 5: 280 (48%); 7: 387 (66%); 9: 515 (87%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.0% | 0.1884, 0.2219, 0.2588, 0.337 | 0.1884: 466 (79%); 0.2219: 350 (59%); 0.2588: 233 (40%); 0.337: 117 (20%) | 0.1884: 117 (20%); 0.2219: 233 (40%); 0.2588: 350 (59%); 0.337: 466 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.0% | 3, 5, 7, 9 | 3: 482 (82%); 5: 365 (62%); 7: 240 (41%); 9: 135 (23%) | 3: 161 (27%); 5: 283 (48%); 7: 398 (68%); 9: 515 (87%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.0% | 0.0239, 0.0324, 0.0423, 0.0583 | 0.0239: 468 (79%); 0.0324: 350 (59%); 0.0423: 235 (40%); 0.0583: 117 (20%) | 0.0239: 120 (20%); 0.0324: 237 (40%); 0.0423: 351 (60%); 0.0583: 467 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.0% | 3, 5, 7, 9 | 3: 478 (81%); 5: 368 (62%); 7: 250 (42%); 9: 135 (23%) | 3: 160 (27%); 5: 274 (47%); 7: 391 (66%); 9: 517 (88%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.3% | -0.056, 0.0284, 0.1426, 0.3362 | -0.056: 468 (79%); 0.0284: 351 (60%); 0.1426: 234 (40%); 0.3362: 117 (20%) | -0.056: 117 (20%); 0.0284: 234 (40%); 0.1426: 351 (60%); 0.3362: 468 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.3% | 4, 6, 8, 9 | 4: 496 (84%); 6: 372 (63%); 8: 235 (40%); 9: 160 (27%) | 4: 149 (25%); 6: 274 (47%); 8: 425 (72%); 9: 496 (84%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.3% |
| 8k_item_5_02_filed_within_7d | 3.1% |
| above_avwap_20high | 51.4% |
| above_avwap_20low | 90.8% |
| above_avwap_252low | 94.5% |
| above_avwap_50low | 78.1% |
| above_cam_r3 | 61.5% |
| above_cam_r4 | 34.6% |
| above_cpr | 80.8% |
| above_pivot | 82.9% |
| above_prev_high | 48.6% |
| above_prev_high_clearance_atr_05 | 15.4% |
| above_prev_low | 96.4% |
| above_r1 | 40.4% |
| above_r2 | 16.6% |
| above_vwap | 74.5% |
| above_wood_p | 77.6% |
| ad_rising | 65.7% |
| adx_cross_up | 1.0% |
| adx_cross_up_20 | 2.0% |
| adx_di_bear | 42.8% |
| adx_di_bull | 57.2% |
| adx_strong | 1.7% |
| adx_trending | 25.8% |
| ao_cross_dn | 3.1% |
| ao_cross_up | 4.2% |
| ao_positive | 51.4% |
| ao_twin_peaks_bull | 6.1% |
| at_key_fib | 23.3% |
| at_key_fib_wide | 59.9% |
| avwap_20high_loss_recent_3d | 10.2% |
| avwap_20high_reclaim_recent_3d | 36.1% |
| avwap_20low_loss_recent_3d | 5.2% |
| avwap_20low_reclaim_recent_3d | 30.5% |
| avwap_252low_loss_recent_3d | 1.2% |
| avwap_252low_reclaim_recent_3d | 19.4% |
| avwap_50low_loss_recent_3d | 6.4% |
| avwap_50low_reclaim_recent_3d | 18.6% |
| bb_10_20_above_mid | 67.1% |
| bb_10_20_expanding | 48.6% |
| bb_10_20_pctb_gt_75 | 36.0% |
| bb_10_20_pctb_gt_8 | 28.7% |
| bb_10_20_pctb_gt_85 | 21.2% |
| bb_10_20_pctb_gt_9 | 13.8% |
| bb_10_20_pctb_gt_95 | 7.1% |
| bb_10_20_pctb_lt_05 | 1.4% |
| bb_10_20_pctb_lt_1 | 2.2% |
| bb_10_20_pctb_lt_15 | 3.6% |
| bb_10_20_pctb_lt_2 | 6.6% |
| bb_10_20_pctb_lt_25 | 9.3% |
| bb_10_20_reclaim_from_lower_recent_3d | 10.2% |
| bb_10_20_reclaim_from_upper_recent_3d | 6.8% |
| bb_10_20_squeeze | 49.6% |
| bb_10_20_touch_lower | 1.5% |
| bb_10_20_touch_upper | 10.5% |
| bb_20_15_above_mid | 63.3% |
| bb_20_15_expanding | 44.5% |
| bb_20_15_pctb_gt_75 | 41.3% |
| bb_20_15_pctb_gt_8 | 35.0% |
| bb_20_15_pctb_gt_85 | 29.9% |
| bb_20_15_pctb_gt_9 | 25.5% |
| bb_20_15_pctb_gt_95 | 20.7% |
| bb_20_15_pctb_lt_05 | 6.3% |
| bb_20_15_pctb_lt_1 | 8.1% |
| bb_20_15_pctb_lt_15 | 10.4% |
| bb_20_15_pctb_lt_2 | 13.9% |
| bb_20_15_pctb_lt_25 | 17.1% |
| bb_20_15_reclaim_from_lower_recent_3d | 16.1% |
| bb_20_15_reclaim_from_upper_recent_3d | 8.8% |
| bb_20_15_squeeze | 44.0% |
| bb_20_15_touch_lower | 6.3% |
| bb_20_15_touch_upper | 22.9% |
| bb_20_20_above_mid | 63.3% |
| bb_20_20_expanding | 44.7% |
| bb_20_20_pctb_gt_75 | 31.4% |
| bb_20_20_pctb_gt_8 | 25.5% |
| bb_20_20_pctb_gt_85 | 19.5% |
| bb_20_20_pctb_gt_9 | 12.4% |
| bb_20_20_pctb_gt_95 | 8.0% |
| bb_20_20_pctb_lt_05 | 2.5% |
| bb_20_20_pctb_lt_1 | 4.2% |
| bb_20_20_pctb_lt_15 | 5.8% |
| bb_20_20_pctb_lt_2 | 8.1% |
| bb_20_20_pctb_lt_25 | 11.7% |
| bb_20_20_reclaim_from_lower_recent_3d | 9.8% |
| bb_20_20_reclaim_from_upper_recent_3d | 4.6% |
| bb_20_20_squeeze | 28.9% |
| bb_20_20_touch_lower | 1.9% |
| bb_20_20_touch_upper | 8.8% |
| bearish_pin_bar | 4.8% |
| below_avwap_20high | 48.6% |
| below_avwap_20low | 9.2% |
| below_avwap_252low | 5.5% |
| below_avwap_50low | 21.9% |
| below_cam_s3 | 3.4% |
| below_cam_s4 | 1.5% |
| below_cpr | 17.1% |
| below_ema_20 | 32.8% |
| below_ema_20_break_recent_5d | 15.4% |
| below_ema_21 | 32.8% |
| below_ema_21_break_recent_5d | 15.4% |
| below_ema_50 | 31.7% |
| below_ema_50_break_recent_5d | 15.6% |
| below_ema_9 | 28.9% |
| below_ema_9_break_recent_5d | 17.3% |
| below_prev_high | 51.3% |
| below_prev_low | 3.4% |
| below_prev_low_clearance_atr_05 | 1.2% |
| below_s1 | 2.0% |
| below_s2 | 0.8% |
| below_sma_20 | 36.7% |
| below_sma_200 | 14.8% |
| below_sma_21 | 36.8% |
| below_sma_50 | 37.7% |
| below_sma_9 | 31.4% |
| below_vwap | 25.5% |
| break_52w_high | 0.3% |
| bullish_engulfing | 10.5% |
| bullish_pin_bar | 4.8% |
| capitulation_recent_3d | 1.0% |
| ceo_buy | 0.3% |
| cfo_buy | 0.2% |
| chandelier_long_bullish | 74.7% |
| chandelier_long_flip_dn | 0.7% |
| chandelier_short_bearish | 59.4% |
| chandelier_short_flip_up | 9.0% |
| close_in_bottom_40pct_of_range | 7.6% |
| close_in_top_40pct_of_range | 74.4% |
| cmf_cross_dn | 3.1% |
| cmf_cross_up | 8.5% |
| cmf_negative | 41.1% |
| cmf_positive | 58.9% |
| concentrated_sell | 7.6% |
| cpr_narrow | 88.5% |
| cpr_narrow_tight | 25.1% |
| cup_handle_detected | 24.3% |
| cup_handle_neckline_break_retest_long | 4.6% |
| dc10_breakout_dn | 1.9% |
| dc10_breakout_dn_1pct | 4.2% |
| dc10_breakout_up | 16.3% |
| dc10_breakout_up_1pct | 30.4% |
| dc10_new_high | 22.1% |
| dc10_strong_breakout_dn | 0.7% |
| dc10_strong_breakout_up | 3.6% |
| dc20_breakout_dn | 1.2% |
| dc20_breakout_up | 9.0% |
| dc20_new_high | 11.5% |
| dc20_resistance_break_retest_strong | 11.4% |
| dc20_support_break_retest_strong | 7.1% |
| defensive_leadership | 54.3% |
| director_only_buy | 2.6% |
| doji | 3.7% |
| double_bottom_detected | 14.4% |
| double_top_detected | 13.9% |
| dpi_elevated | 58.1% |
| drying_volume_on_up_turn | 65.9% |
| ema_20_50_bearish | 37.5% |
| ema_20_50_bullish | 62.5% |
| ema_20_50_death_cross | 0.2% |
| ema_20_50_golden_cross | 2.5% |
| ema_50_200_bearish | 25.6% |
| ema_50_200_bullish | 74.4% |
| ema_50_200_golden_cross | 0.5% |
| ema_9_21_bearish | 44.7% |
| ema_9_21_bullish | 55.3% |
| ema_9_21_death_cross | 1.9% |
| ema_9_21_golden_cross | 6.5% |
| flag_bear_detected | 0.3% |
| flag_bull_break_retest_long | 0.7% |
| flag_bull_broke | 1.2% |
| flag_bull_detected | 1.7% |
| force_index_cross_dn | 0.5% |
| force_index_cross_up | 13.1% |
| force_index_positive | 62.3% |
| gap_dn_1_5pct | 7.5% |
| gap_dn_2pct | 3.7% |
| gap_up_1_5pct | 7.0% |
| gap_up_2pct | 3.9% |
| hammer | 3.2% |
| head_shoulders_bottom_detected | 5.6% |
| head_shoulders_top_detected | 5.9% |
| house_cluster_buy | 5.1% |
| house_cluster_sell | 4.1% |
| htf_aligned_bear | 1.4% |
| htf_aligned_bull | 44.3% |
| htf_disagreement | 4.8% |
| hull_bearish | 43.8% |
| hull_bullish | 56.2% |
| hull_flip_dn | 3.6% |
| hull_flip_up | 8.3% |
| ichi_above_cloud | 52.6% |
| ichi_above_cloud_break_recent_5d | 23.1% |
| ichi_below_cloud | 22.1% |
| ichi_below_cloud_break_recent_5d | 4.8% |
| ichi_cloud_thick | 86.4% |
| ichi_tk_bearish | 47.5% |
| ichi_tk_bullish | 47.2% |
| ichi_tk_cross_dn | 2.2% |
| ichi_tk_cross_up | 3.2% |
| ichi_weekly_above_cloud | 60.0% |
| ichi_weekly_below_cloud | 9.5% |
| ichi_weekly_in_cloud | 30.5% |
| in_reversal_window | 4.7% |
| inside_bar | 11.7% |
| inside_cpr | 3.2% |
| inside_kc | 94.2% |
| insider_cluster_active | 11.8% |
| institutional_buy | 84.2% |
| institutional_negative | 7.1% |
| institutional_persistence_growing | 40.9% |
| institutional_persistence_strong | 57.0% |
| institutional_strong_buy | 75.4% |
| inverted_cup_handle_detected | 18.2% |
| is_friday | 21.7% |
| is_halloween_period | 58.6% |
| is_halloween_period_first_day | 0.2% |
| is_january | 12.4% |
| is_january_extended | 14.6% |
| is_monday | 18.8% |
| is_pre_holiday | 4.4% |
| is_summer_period | 41.4% |
| is_totm_window | 36.2% |
| is_totm_window_first_day | 12.9% |
| is_week_open | 22.1% |
| kc_touch_lower | 1.7% |
| kc_touch_upper | 7.3% |
| large_dollar_buy | 0.9% |
| macd_12_26_9_bearish | 53.0% |
| macd_12_26_9_bullish | 47.0% |
| macd_12_26_9_crossover_dn | 2.0% |
| macd_12_26_9_crossover_up | 3.7% |
| macd_8_21_5_bearish | 45.3% |
| macd_8_21_5_bullish | 54.7% |
| macd_8_21_5_crossover_dn | 1.4% |
| macd_8_21_5_crossover_up | 6.8% |
| marubozu_bull | 1.2% |
| mfi_broad_overbought | 9.8% |
| mfi_broad_oversold | 6.5% |
| mfi_overbought | 2.7% |
| mfi_oversold | 1.2% |
| monthly_above_sma_12 | 85.2% |
| monthly_above_sma_6 | 68.9% |
| monthly_bias_bear | 6.4% |
| monthly_bias_bull | 60.5% |
| monthly_momentum_pos | 70.9% |
| morning_star | 11.5% |
| near_52w_high | 1.2% |
| near_52w_high_95pct | 6.8% |
| near_52w_high_retest_long | 5.9% |
| near_avwap_20high_atr_05x | 48.5% |
| near_avwap_20high_atr_10x | 76.4% |
| near_avwap_20high_atr_15x | 88.8% |
| near_avwap_20high_atr_20x | 95.0% |
| near_avwap_20low_atr_05x | 26.8% |
| near_avwap_20low_atr_10x | 57.3% |
| near_avwap_20low_atr_15x | 74.9% |
| near_avwap_20low_atr_20x | 87.1% |
| near_avwap_252low_atr_05x | 11.4% |
| near_avwap_252low_atr_10x | 24.8% |
| near_avwap_252low_atr_15x | 33.8% |
| near_avwap_252low_atr_20x | 45.2% |
| near_avwap_50low_atr_05x | 18.4% |
| near_avwap_50low_atr_10x | 41.7% |
| near_avwap_50low_atr_15x | 61.7% |
| near_avwap_50low_atr_20x | 74.8% |
| near_cam_r3 | 24.6% |
| near_cam_s3 | 6.5% |
| near_cam_s4 | 1.9% |
| near_fib_236 | 9.3% |
| near_fib_382 | 8.8% |
| near_fib_500 | 7.0% |
| near_fib_618 | 7.6% |
| near_fib_786 | 2.9% |
| near_pivot | 15.6% |
| near_prev_close | 17.5% |
| near_prev_high | 19.9% |
| near_prev_low | 4.2% |
| near_r1 | 22.8% |
| near_r1_wide | 75.4% |
| near_r2 | 7.5% |
| near_r2_wide | 53.3% |
| near_s1 | 2.2% |
| near_s1_wide | 29.2% |
| near_s2 | 0.2% |
| near_s2_wide | 8.7% |
| near_wood_r1 | 12.4% |
| near_wood_s1 | 6.3% |
| news_uses_polygon_score | 23.4% |
| obv_bearish | 40.1% |
| obv_bullish | 59.9% |
| obv_diverge_bull | 9.0% |
| obv_falling | 39.0% |
| obv_rising | 61.0% |
| outside_bar | 9.8% |
| pead_negative_surprise | 13.4% |
| pead_positive_surprise | 25.7% |
| pin_bar | 9.5% |
| po3_accumulation_active | 39.4% |
| po3_bullish | 21.1% |
| po3_manipulation_sweep_down | 4.8% |
| po3_manipulation_sweep_up | 13.4% |
| po3_mmbm_setup | 3.6% |
| po3_sweep_above_prior_high | 69.9% |
| po3_sweep_below_prior_low | 34.3% |
| ppo_bullish | 46.5% |
| ppo_crossover_dn | 1.9% |
| ppo_crossover_up | 3.6% |
| pre_fomc_d0 | 1.7% |
| pre_fomc_d1 | 2.4% |
| pre_fomc_window | 4.1% |
| price_above_dema | 62.3% |
| price_above_ema_20 | 67.2% |
| price_above_ema_200_break_recent_5d | 45.1% |
| price_above_ema_20_break_recent_5d | 42.4% |
| price_above_ema_21 | 67.2% |
| price_above_ema_21_break_recent_5d | 41.8% |
| price_above_ema_50 | 68.3% |
| price_above_ema_50_break_recent_5d | 39.7% |
| price_above_ema_9 | 71.1% |
| price_above_ema_9_break_recent_5d | 50.9% |
| price_above_hull | 68.6% |
| price_above_sma_200 | 85.2% |
| price_above_sma_21 | 63.2% |
| price_above_sma_50 | 62.3% |
| price_above_tema | 67.1% |
| price_below_dema | 37.7% |
| price_below_hull | 31.4% |
| price_below_tema | 32.9% |
| psar_bullish | 52.0% |
| psar_flip_dn | 1.9% |
| psar_flip_up | 5.6% |
| r1_break_retest_long | 65.0% |
| recent_blowoff_at_r3 | 0.2% |
| resistance_break_retest | 18.8% |
| risk_off_regime_bond_signal | 22.1% |
| risk_off_regime_bond_signal_strong | 7.6% |
| risk_off_regime_gold_signal | 43.0% |
| risk_on_regime_bond_signal | 38.9% |
| risk_on_regime_bond_signal_strong | 16.3% |
| roc_positive | 59.6% |
| roc_turning_dn | 3.7% |
| roc_turning_up | 12.6% |
| rsi_14_bullish | 67.4% |
| rsi_14_cross_dn_overbought_recent_3d | 1.5% |
| rsi_14_cross_up_oversold_recent_3d | 1.4% |
| rsi_14_overbought | 1.0% |
| rsi_14_oversold | 0.2% |
| rsi_14_rising | 84.6% |
| rsi_21_bullish | 67.1% |
| rsi_21_cross_dn_overbought_recent_3d | 0.7% |
| rsi_21_overbought | 0.3% |
| rsi_21_rising | 84.6% |
| rsi_2_bullish | 78.4% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 16.8% |
| rsi_2_cross_dn_overbought_recent_3d | 17.5% |
| rsi_2_cross_up_extreme_os_recent_3d | 37.9% |
| rsi_2_cross_up_oversold_recent_3d | 47.0% |
| rsi_2_extreme_ob | 42.1% |
| rsi_2_extreme_os | 5.4% |
| rsi_2_overbought | 58.4% |
| rsi_2_oversold | 9.5% |
| rsi_2_rising | 84.6% |
| rsi_9_bullish | 67.1% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 0.8% |
| rsi_9_cross_dn_overbought_recent_3d | 4.1% |
| rsi_9_cross_up_extreme_os_recent_3d | 0.5% |
| rsi_9_cross_up_oversold_recent_3d | 10.9% |
| rsi_9_extreme_ob | 0.7% |
| rsi_9_overbought | 7.3% |
| rsi_9_oversold | 2.0% |
| rsi_9_rising | 84.6% |
| s1_break_retest_short | 41.4% |
| sc_13d_filed_within_30d | 2.4% |
| sc_13g_filed_within_30d | 2.5% |
| sector_outperforming_spy | 44.4% |
| sector_underperforming_spy | 55.6% |
| shooting_star | 4.2% |
| sma_20_50_bullish | 56.0% |
| sma_20_50_golden_cross | 2.0% |
| sma_50_200_bullish | 70.6% |
| sma_50_200_golden_cross | 0.5% |
| sma_9_21_bullish | 52.0% |
| sma_9_21_golden_cross | 2.7% |
| smc_bos_bearish | 6.1% |
| smc_bos_bullish | 10.0% |
| smc_bos_retest_long | 6.6% |
| smc_bos_retest_short | 3.6% |
| smc_breaker_block_bearish | 8.7% |
| smc_breaker_block_bullish | 25.3% |
| smc_choch_bearish | 5.3% |
| smc_choch_bullish | 4.1% |
| smc_equal_highs_swept | 5.3% |
| smc_equal_lows_swept | 2.2% |
| smc_fvg_bearish_active | 34.0% |
| smc_fvg_bullish_active | 38.4% |
| smc_fvg_retest_long_zone | 1.4% |
| smc_fvg_retest_short_zone | 11.2% |
| smc_in_discount_zone | 54.0% |
| smc_in_premium_zone | 76.2% |
| smc_inverse_fvg_bearish | 81.8% |
| smc_inverse_fvg_bullish | 98.0% |
| smc_liquidity_swept_dn | 0.8% |
| smc_liquidity_swept_up | 1.9% |
| smc_mitigation_block_long | 0.3% |
| smc_mitigation_block_short | 2.9% |
| smc_ob_bearish_active | 20.7% |
| smc_ob_bullish_active | 36.2% |
| smc_ote_long_zone | 11.5% |
| smc_ote_short_zone | 12.2% |
| squeeze_fire_dn | 0.7% |
| squeeze_fire_up | 5.4% |
| squeeze_in | 35.3% |
| squeeze_positive | 62.0% |
| stoch_bearish_cross | 5.8% |
| stoch_broad_overbought | 28.0% |
| stoch_broad_oversold | 17.1% |
| stoch_bullish_cross | 18.5% |
| stoch_overbought | 21.1% |
| stoch_oversold | 12.2% |
| stochrsi_cross_dn | 18.0% |
| stochrsi_cross_up | 38.9% |
| stochrsi_overbought | 34.6% |
| stochrsi_oversold | 21.1% |
| supertrend_bearish | 1.0% |
| supertrend_bullish | 99.0% |
| supertrend_flip_dn | 0.2% |
| supertrend_flip_recent_long_5d | 2.5% |
| supertrend_flip_recent_short_5d | 2.2% |
| supertrend_flip_up | 0.7% |
| support_break_retest | 10.5% |
| tema_above_dema | 46.7% |
| tema_cross_dn | 1.7% |
| tema_cross_up | 3.2% |
| three_white_soldiers | 8.8% |
| triangle_apex_break_retest_long | 17.0% |
| triangle_ascending_detected | 15.3% |
| triangle_descending_detected | 11.9% |
| uo_overbought | 2.5% |
| uo_oversold | 0.2% |
| usd_strengthening | 20.0% |
| usd_weakening | 13.2% |
| vix_band_high | 41.9% |
| vix_band_low | 38.5% |
| vix_band_mid | 19.5% |
| vix_term_backwardation | 10.5% |
| vix_term_contango | 89.5% |
| vol_above_avg | 34.1% |
| vol_below_avg | 65.9% |
| vol_spike_12x | 21.1% |
| vol_spike_15x | 10.9% |
| vol_spike_17x | 6.6% |
| vol_spike_2x | 3.2% |
| vol_spike_2x_on_down_day_recent_3d | 4.2% |
| vol_spike_2x_on_up_day_recent_3d | 3.2% |
| vol_spike_3x | 0.7% |
| vp_above_value_area | 5.8% |
| vp_in_value_area | 94.2% |
| week_open_gap_down_15pct | 2.0% |
| week_open_gap_up_15pct | 1.7% |
| weekly_above_ema_10 | 69.4% |
| weekly_above_ema_20 | 80.5% |
| weekly_bias_bear | 14.6% |
| weekly_bias_bull | 64.5% |
| weekly_momentum_pos | 60.6% |
| williams_r_overbought | 31.1% |
| williams_r_oversold | 6.1% |
| williams_r_rising | 80.0% |
| within_pead_window | 39.5% |
| within_post_deletion_window | 4.2% |
| within_post_inclusion_window | 7.1% |
| xs_avoid_high_ivol | 76.8% |
| xs_avoid_high_max | 76.8% |
| xs_high_beta_decile | 22.5% |
| xs_low_beta_bottom_quintile | 22.5% |
| xs_low_beta_decile | 19.2% |
| xs_low_beta_decile_entry_recent_5d | 0.9% |
| xs_low_beta_top_quintile | 19.2% |
| xs_momentum_bottom_decile | 2.1% |
| xs_momentum_bottom_quintile | 6.5% |
| xs_momentum_top_decile | 15.2% |
| xs_momentum_top_quintile | 27.4% |
| xs_quality_bottom_quintile | 18.8% |
| xs_quality_top_quintile | 25.9% |
| xs_quality_top_tercile | 44.9% |
| yoy_surprise_high | 55.5% |
| yoy_surprise_negative | 34.8% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 90.8% |
| committed_growth_holders | 90.8% |
| corp_donations_1y | 10.4% |
| corp_donations_count_1y | 10.4% |
| corp_donations_unique_pacs | 10.4% |
| cot_rut_commercials_pctile_3y | 55.2% |
| cot_rut_mmoney_pctile_3y | 55.2% |
| cup_handle_depth_pct | 30.7% |
| days_since_deletion | 4.1% |
| days_since_inclusion | 14.4% |
| days_to_next_holiday | 70.8% |
| days_to_rebalance | 3.9% |
| dpi_30d_avg | 95.9% |
| dpi_recent | 95.9% |
| earnings_announcement_return | 91.0% |
| earnings_eps_yoy_growth | 95.1% |
| flag_bull_pole_move_pct | 1.7% |
| gov_contracts_4q_sum | 46.0% |
| gov_contracts_last_qtr_amount | 46.0% |
| gov_contracts_qoq_growth | 46.0% |
| head_shoulders_magnitude_pct | 10.9% |
| insider_director_buyers_30d | 2.9% |
| insider_officer_buyers_30d | 2.9% |
| insider_total_shares_bought_30d | 2.9% |
| insider_unique_buyers_30d | 2.9% |
| inverted_cup_handle_height_pct | 25.8% |
| lobbying_amount_1y | 74.2% |
| lobbying_amount_q | 74.2% |
| lobbying_amount_yoy | 74.2% |
| monthly_momentum_6m | 95.1% |
| otc_short_ratio_recent | 95.9% |
| otc_volume_recent | 95.9% |
| pair_half_life | 91.9% |
| pair_max_abs_zscore | 91.9% |
| pair_zscore_signed | 91.9% |
| pct_from_avwap_20high | 87.9% |
| pct_from_avwap_20low | 94.6% |
| pct_from_avwap_252low | 96.4% |
| persistent_holders_4q | 90.8% |
| persistent_holders_8q | 90.8% |
| sc_13g_latest_percent_owned | 1.2% |
| search_volume_index_recent | 76.1% |
| search_volume_observations | 76.1% |
| search_volume_zscore_30d | 76.1% |
| sector_etf_return_20d | 3.1% |
| spy_return_20d | 3.1% |
| total_active_holders | 90.8% |
| triangle_breakdown_pct | 11.9% |
| triangle_breakout_pct | 15.3% |
| xs_quality_decile | 59.8% |
| xs_quality_gross_profitability | 59.8% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.999), `avwap_252low` (0.993), `avwap_50low` (0.999), `bb_10_20_lower` (0.999), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.998), `cam_s4` (0.998), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.999), `days_since_classification_change` (-1.0), `dc10_lower` (0.999), `dc10_mid` (1.0), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (1.0), `double_bottom_neckline` (0.999), `double_bottom_trough` (0.999), `double_top_neckline` (0.999), `double_top_peak` (0.999), `entry_stop_long` (0.998), `entry_stop_short` (0.999), `fib_236` (0.998), `fib_382` (0.998), `fib_500` (0.999), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.996), `fib_ext_162` (0.994), `flag_bear_breakdown_level` (1.0), `flag_bear_pole_move_pct` (1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.997), `head_shoulders_top_neckline` (0.999), `hull_ma` (0.999), `ichi_kijun` (1.0), `ichi_senkou_a` (0.997), `ichi_senkou_b` (0.995), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.993), `monthly_sma_6` (0.997), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.998), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.998), `s2` (0.998), `s3` (0.997), `supertrend_value` (0.997), `swing_high` (0.997), `swing_low` (0.996), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.999), `vp_value_area_high` (0.998), `vp_value_area_low` (0.998), `vwap_upper_1` (0.953), `vwap_upper_2` (0.96), `weekly_close` (0.999), `weekly_ema_10` (0.999), `weekly_ema_20` (0.998), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.998), `year_high` (0.994), `year_low` (0.959)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | ema span (the 200 in above/below_ema_200 | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1.1 | profile (lookback_days, n_bins) + side r | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1.2 | profile (lookback_days, n_bins) + side r | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P3 | vp_close_near_poc_pct < 0.03 | 5 | subset-safe | no - derives offline |

```
FULL FACTORIAL     3 x 3 x 3 x 5 = 135
offline gradings   5 level-combinations x 24 exits = 120
ENGINE RUNS        1 (actuated fire-adding axes only)
PENDING ACTUATION  27 level-combinations are DEFINED but have no env knob - they are a FEATURE REQUEST, not a runnable band (plan 11.0b state 1; B2866)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 611 census axes join it only when REGISTERED at the T3 band review.
