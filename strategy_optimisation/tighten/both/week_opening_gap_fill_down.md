# Table A - week_opening_gap_fill_down

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit fa06ebf3e at 2026-09-19 13:07:41 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** ict | **status:** NOT-STARTED | **R5 fires:** 633 | **surviving fires (T1):** 633 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  week_open_gap_up_15pct  <- backtest/signals/ict_producers.py +1
       DEFN: Monday-equivalent open gapped up >= 1.5pct vs prior close (ict_producers.py:147-149; DECIMAL-SHIFTED name)
       knobs P1.1-P1.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P2  days_since_last_earnings > 2   [EXISTING-THRESHOLD]
P3  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_week_opening_gap_fill_down (docstring and return dropped):

```python
fires = bool(s.get('week_open_gap_up_15pct', False)) and s.get('days_since_last_earnings', 999) > 2 and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | week_open_gap_up_15pct - emitted by backtest/signals/ict_producers.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | Monday-equivalent open gapped up >= 1.5pct vs prior close (ict_producers.py:147-149; DECIMAL-SHIFTED name) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | gap threshold pct (NAME IS DECIMAL-SHIFTED: 15pct = 1.5pct, the vol_spike naming convention) - backtest/signals/ict_producers.py:147-149 | BRACKET production 1.5 | 1.5 | [1.0, 1.5, 2.0, 3.0] | none - the gap pct is not persisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | STRATEGY | days_since_last_earnings `> 2` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `> 2` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P3 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | `> 2` | 98.4% | TIGHTER = RAISE the floor: 33 -> 499 (79%); 67 -> 376 (59%); 88.2 -> 249 (39%); 146 -> 128 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 16.92, 21.41, 25.774, 31.516 | 16.92: 507 (80%); 21.41: 381 (60%); 25.774: 253 (40%); 31.516: 127 (20%) | 16.92: 128 (20%); 21.41: 254 (40%); 25.774: 380 (60%); 31.516: 506 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 15.904, 19.354, 23.818, 27.86 | 15.904: 506 (80%); 19.354: 380 (60%); 23.818: 253 (40%); 27.86: 128 (20%) | 15.904: 127 (20%); 19.354: 253 (40%); 23.818: 380 (60%); 27.86: 508 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 18.752, 24.164, 28.99, 35.532 | 18.752: 506 (80%); 24.164: 380 (60%); 28.99: 254 (40%); 35.532: 127 (20%) | 18.752: 127 (20%); 24.164: 253 (40%); 28.99: 382 (60%); 35.532: 506 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -6.4604, -1.5584, 0.9285, 6.165 | -6.4604: 506 (80%); -1.5584: 380 (60%); 0.9285: 253 (40%); 6.165: 127 (20%) | -6.4604: 127 (20%); -1.5584: 254 (40%); 0.9285: 380 (60%); 6.165: 506 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.4381, 2.6963, 4.5924, 8.5224 | 1.4381: 506 (80%); 2.6963: 380 (60%); 4.5924: 253 (40%); 8.5224: 127 (20%) | 1.4381: 127 (20%); 2.6963: 253 (40%); 4.5924: 380 (60%); 8.5224: 506 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.4381, 2.6963, 4.5924, 8.5224 | 1.4381: 506 (80%); 2.6963: 380 (60%); 4.5924: 253 (40%); 8.5224: 127 (20%) | 1.4381: 127 (20%); 2.6963: 253 (40%); 4.5924: 380 (60%); 8.5224: 506 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.7004, 3.2694, 3.9822, 5.0502 | 2.7004: 506 (80%); 3.2694: 380 (60%); 3.9822: 253 (40%); 5.0502: 127 (20%) | 2.7004: 127 (20%); 3.2694: 253 (40%); 3.9822: 380 (60%); 5.0502: 506 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0717, 0.1015, 0.1461, 0.2152 | 0.0717: 506 (80%); 0.1015: 380 (60%); 0.1461: 254 (40%); 0.2152: 127 (20%) | 0.0717: 127 (20%); 0.1015: 253 (40%); 0.1461: 380 (60%); 0.2152: 506 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.4106, 0.6027, 0.7915, 0.9185 | 0.4106: 506 (80%); 0.6027: 380 (60%); 0.7915: 253 (40%); 0.9185: 127 (20%) | 0.4106: 127 (20%); 0.6027: 253 (40%); 0.7915: 380 (60%); 0.9185: 506 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.082, 0.1095, 0.1444, 0.2041 | 0.082: 506 (80%); 0.1095: 383 (61%); 0.1444: 253 (40%); 0.2041: 127 (20%) | 0.082: 127 (20%); 0.1095: 254 (40%); 0.1444: 380 (60%); 0.2041: 506 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.2382, 0.4876, 0.8321, 1.1001 | 0.2382: 506 (80%); 0.4876: 380 (60%); 0.8321: 253 (40%); 1.1001: 127 (20%) | 0.2382: 127 (20%); 0.4876: 253 (40%); 0.8321: 380 (60%); 1.1001: 506 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.1093, 0.146, 0.1925, 0.2722 | 0.1093: 506 (80%); 0.146: 381 (60%); 0.1925: 253 (40%); 0.2722: 127 (20%) | 0.1093: 127 (20%); 0.146: 254 (40%); 0.1925: 380 (60%); 0.2722: 506 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.3036, 0.4907, 0.7491, 0.9501 | 0.3036: 506 (80%); 0.4907: 380 (60%); 0.7491: 253 (40%); 0.9501: 127 (20%) | 0.3036: 127 (20%); 0.4907: 253 (40%); 0.7491: 380 (60%); 0.9501: 506 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0435, -0.0271, -0.0016, 0.0159 | -0.0435: 506 (80%); -0.0271: 382 (60%); -0.0016: 254 (40%); 0.0159: 140 (22%) | -0.0435: 127 (20%); -0.0271: 257 (41%); -0.0016: 392 (62%); 0.0159: 554 (88%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1339, 0.1552, 0.1781, 0.2664 | 0.1339: 506 (80%); 0.1552: 379 (60%); 0.1781: 255 (40%); 0.2664: 129 (20%) | 0.1339: 127 (20%); 0.1552: 254 (40%); 0.1781: 381 (60%); 0.2664: 504 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 633 (100%) | 0: 597 (94%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0959, -0.0189, 0.0564, 0.1304 | -0.0959: 507 (80%); -0.0189: 380 (60%); 0.0564: 254 (40%); 0.1304: 127 (20%) | -0.0959: 127 (20%); -0.0189: 253 (40%); 0.0564: 380 (60%); 0.1304: 506 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0 | 0: 633 (100%) | 0: 515 (81%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2591, -0.2038, -0.1541, -0.1236 | -0.2591: 508 (80%); -0.2038: 382 (60%); -0.1541: 259 (41%); -0.1236: 132 (21%) | -0.2591: 137 (22%); -0.2038: 262 (41%); -0.1541: 384 (61%); -0.1236: 511 (81%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.1282, 0.5833, 0.6923, 0.7692 | 0.1282: 507 (80%); 0.5833: 403 (64%); 0.6923: 274 (43%); 0.7692: 151 (24%) | 0.1282: 132 (21%); 0.5833: 270 (43%); 0.6923: 388 (61%); 0.7692: 555 (88%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.3077, 0.4487, 0.7308, 0.891 | 0.3077: 513 (81%); 0.4487: 385 (61%); 0.7308: 260 (41%); 0.891: 156 (25%) | 0.3077: 143 (23%); 0.4487: 254 (40%); 0.7308: 386 (61%); 0.891: 536 (85%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0912, -0.014, 0.036, 0.1739 | -0.0912: 534 (84%); -0.014: 380 (60%); 0.036: 253 (40%); 0.1739: 131 (21%) | -0.0912: 142 (22%); -0.014: 253 (40%); 0.036: 380 (60%); 0.1739: 516 (82%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3526, 0.4551, 0.5141, 0.7372 | 0.3526: 523 (83%); 0.4551: 400 (63%); 0.5141: 253 (40%); 0.7372: 138 (22%) | 0.3526: 153 (24%); 0.4551: 273 (43%); 0.5141: 380 (60%); 0.7372: 509 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1346, 0.3654, 0.4551, 0.6731 | 0.1346: 508 (80%); 0.3654: 381 (60%); 0.4551: 304 (48%); 0.6731: 128 (20%) | 0.1346: 139 (22%); 0.3654: 258 (41%); 0.4551: 395 (62%); 0.6731: 528 (83%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.4584, -0.2992, -0.0869, 0.077 | -0.4584: 506 (80%); -0.2992: 398 (63%); -0.0869: 283 (45%); 0.077: 127 (20%) | -0.4584: 127 (20%); -0.2992: 262 (41%); -0.0869: 411 (65%); 0.077: 506 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3846, 0.5385, 0.8051, 0.9167 | 0.3846: 543 (86%); 0.5385: 382 (60%); 0.8051: 253 (40%); 0.9167: 164 (26%) | 0.3846: 137 (22%); 0.5385: 265 (42%); 0.8051: 380 (60%); 0.9167: 511 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1346, 0.2692, 0.4872, 0.8526 | 0.1346: 508 (80%); 0.2692: 388 (61%); 0.4872: 254 (40%); 0.8526: 136 (21%) | 0.1346: 128 (20%); 0.2692: 255 (40%); 0.4872: 401 (63%); 0.8526: 558 (88%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0699, -0.055, -0.0416, 0 | -0.0699: 508 (80%); -0.055: 384 (61%); -0.0416: 267 (42%); 0: 208 (33%) | -0.0699: 131 (21%); -0.055: 257 (41%); -0.0416: 396 (63%); 0: 625 (99%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4487, 0.6667, 0.8718, 1 | 0.4487: 514 (81%); 0.6667: 394 (62%); 0.8718: 269 (42%); 1: 130 (21%) | 0.4487: 128 (20%); 0.6667: 266 (42%); 0.8718: 395 (62%); 1: 633 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0833, 0.3205, 0.5128, 0.7949 | 0.0833: 542 (86%); 0.3205: 382 (60%); 0.5128: 266 (42%); 0.7949: 130 (21%) | 0.0833: 146 (23%); 0.3205: 326 (52%); 0.5128: 405 (64%); 0.7949: 510 (81%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.012, 0.0445, 0.1512, 0.2846 | 0.012: 510 (81%); 0.0445: 401 (63%); 0.1512: 256 (40%); 0.2846: 159 (25%) | 0.012: 153 (24%); 0.0445: 259 (41%); 0.1512: 381 (60%); 0.2846: 512 (81%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.6218, 0.8482, 0.9551, 0.9744 | 0.6218: 507 (80%); 0.8482: 404 (64%); 0.9551: 283 (45%); 0.9744: 210 (33%) | 0.6218: 129 (20%); 0.8482: 256 (40%); 0.9551: 401 (63%); 0.9744: 531 (84%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0667, 0.1518, 0.3103, 0.7628 | 0.0667: 506 (80%); 0.1518: 403 (64%); 0.3103: 271 (43%); 0.7628: 131 (21%) | 0.0667: 127 (20%); 0.1518: 257 (41%); 0.3103: 381 (60%); 0.7628: 508 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1198, -0.0203, 0.1182, 0.3175 | -0.1198: 512 (81%); -0.0203: 388 (61%); 0.1182: 254 (40%); 0.3175: 137 (22%) | -0.1198: 144 (23%); -0.0203: 255 (40%); 0.1182: 381 (60%); 0.3175: 576 (91%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.3213, 0.0192, 0.0546, 0.0994 | -0.3213: 510 (81%); 0.0192: 380 (60%); 0.0546: 268 (42%); 0.0994: 127 (20%) | -0.3213: 129 (20%); 0.0192: 253 (40%); 0.0546: 384 (61%); 0.0994: 506 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3205, 0.6013, 0.7628, 0.9103 | 0.3205: 511 (81%); 0.6013: 380 (60%); 0.7628: 280 (44%); 0.9103: 129 (20%) | 0.3205: 160 (25%); 0.6013: 253 (40%); 0.7628: 391 (62%); 0.9103: 524 (83%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1154, 0.3462, 0.559, 0.773 | 0.1154: 508 (80%); 0.3462: 383 (61%); 0.559: 253 (40%); 0.773: 127 (20%) | 0.1154: 129 (20%); 0.3462: 258 (41%); 0.559: 380 (60%); 0.773: 506 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0651, 0.1717, 0.347, 0.782 | 0.0651: 506 (80%); 0.1717: 381 (60%); 0.347: 253 (40%); 0.782: 127 (20%) | 0.0651: 127 (20%); 0.1717: 255 (40%); 0.347: 380 (60%); 0.782: 507 (80%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 100.0% | 1.5431, 2.0831, 2.6009, 3.3042 | 1.5431: 506 (80%); 2.0831: 380 (60%); 2.6009: 253 (40%); 3.3042: 127 (20%) | 1.5431: 127 (20%); 2.0831: 253 (40%); 2.6009: 380 (60%); 3.3042: 506 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 10, 23, 37 | 10: 508 (80%); 23: 391 (62%); 37: 163 (26%) | 10: 132 (21%); 23: 388 (61%); 37: 600 (95%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 0 | 0: 633 (100%) | 0: 557 (88%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0161, -0.0018, 0.0173, 0.0251 | -0.0161: 506 (80%); -0.0018: 384 (61%); 0.0173: 259 (41%); 0.0251: 127 (20%) | -0.0161: 127 (20%); -0.0018: 256 (40%); 0.0173: 418 (66%); 0.0251: 506 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.647, 26.1375, 26.7315, 27.33 | 24.647: 513 (81%); 26.1375: 381 (60%); 26.7315: 253 (40%); 27.33: 128 (20%) | 24.647: 133 (21%); 26.1375: 255 (40%); 26.7315: 380 (60%); 27.33: 511 (81%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -3.8114, -2.692, -2.1136, -1.7404 | -3.8114: 506 (80%); -2.692: 380 (60%); -2.1136: 253 (40%); -1.7404: 127 (20%) | -3.8114: 127 (20%); -2.692: 253 (40%); -2.1136: 380 (60%); -1.7404: 506 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | 1.7404, 2.1136, 2.692, 3.8114 | 1.7404: 506 (80%); 2.1136: 380 (60%); 2.692: 253 (40%); 3.8114: 127 (20%) | 1.7404: 127 (20%); 2.1136: 253 (40%); 2.692: 380 (60%); 3.8114: 506 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0364, -0.009, 0.023, 0.0828 | -0.0364: 507 (80%); -0.009: 383 (61%); 0.023: 254 (40%); 0.0828: 139 (22%) | -0.0364: 133 (21%); -0.009: 254 (40%); 0.023: 381 (60%); 0.0828: 537 (85%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.7578, 8.439, 8.8214, 9.2509 | 7.7578: 513 (81%); 8.439: 380 (60%); 8.8214: 253 (40%); 9.2509: 127 (20%) | 7.7578: 120 (19%); 8.439: 253 (40%); 8.8214: 380 (60%); 9.2509: 506 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.8% | 0, 1 | 0: 632 (100%); 1: 239 (38%) | 0: 393 (62%); 1: 535 (85%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.8% | -1, 0 | -1: 587 (93%); 0: 478 (76%) | -1: 154 (24%); 0: 521 (82%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.8% | 0, 1 | 0: 632 (100%); 1: 252 (40%) | 0: 380 (60%); 1: 518 (82%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 5.8, 68, 287.6 | 2: 535 (85%); 5.8: 380 (60%); 68: 254 (40%); 287.6: 127 (20%) | 2: 141 (22%); 5.8: 253 (40%); 68: 381 (60%); 287.6: 506 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 5, 86.2, 159.6 | 1: 510 (81%); 5: 387 (61%); 86.2: 253 (40%); 159.6: 127 (20%) | 1: 169 (27%); 5: 258 (41%); 86.2: 380 (60%); 159.6: 506 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.5568, -0.0563, 0.2597, 0.933 | -0.5568: 506 (80%); -0.0563: 380 (60%); 0.2597: 253 (40%); 0.933: 127 (20%) | -0.5568: 127 (20%); -0.0563: 253 (40%); 0.2597: 380 (60%); 0.933: 506 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -2.5226, -0.5631, 0.4385, 2.6394 | -2.5226: 506 (80%); -0.5631: 380 (60%); 0.4385: 253 (40%); 2.6394: 127 (20%) | -2.5226: 127 (20%); -0.5631: 253 (40%); 0.4385: 380 (60%); 2.6394: 506 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -2.4031, -0.714, 0.3358, 2.371 | -2.4031: 506 (80%); -0.714: 380 (60%); 0.3358: 253 (40%); 2.371: 127 (20%) | -2.4031: 127 (20%); -0.714: 253 (40%); 0.3358: 380 (60%); 2.371: 506 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.2772, 0.1172, 0.3792, 0.9246 | -0.2772: 506 (80%); 0.1172: 380 (60%); 0.3792: 254 (40%); 0.9246: 127 (20%) | -0.2772: 127 (20%); 0.1172: 253 (40%); 0.3792: 380 (60%); 0.9246: 506 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -2.5837, -0.5799, 0.5282, 2.8148 | -2.5837: 506 (80%); -0.5799: 380 (60%); 0.5282: 253 (40%); 2.8148: 127 (20%) | -2.5837: 127 (20%); -0.5799: 253 (40%); 0.5282: 380 (60%); 2.8148: 506 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -2.6632, -0.6816, 0.3571, 2.4839 | -2.6632: 506 (80%); -0.6816: 380 (60%); 0.3571: 253 (40%); 2.4839: 127 (20%) | -2.6632: 127 (20%); -0.6816: 253 (40%); 0.3571: 380 (60%); 2.4839: 506 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 40.846, 49.84, 59.648, 69.198 | 40.846: 506 (80%); 49.84: 381 (60%); 59.648: 253 (40%); 69.198: 127 (20%) | 40.846: 127 (20%); 49.84: 254 (40%); 59.648: 380 (60%); 69.198: 506 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 98.9% | -0.1369, 0.0036, 0.1335, 0.3482 | -0.1369: 501 (79%); 0.0036: 376 (59%); 0.1335: 251 (40%); 0.3482: 126 (20%) | -0.1369: 126 (20%); 0.0036: 251 (40%); 0.1335: 376 (59%); 0.3482: 501 (79%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 98.9% | 0.0086, 0.0218, 0.0419, 0.0864 | 0.0086: 500 (79%); 0.0218: 375 (59%); 0.0419: 250 (39%); 0.0864: 126 (20%) | 0.0086: 126 (20%); 0.0218: 251 (40%); 0.0419: 376 (59%); 0.0864: 500 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 1, 2, 6, 14 | 1: 514 (81%); 2: 425 (67%); 6: 263 (42%); 14: 134 (21%) | 1: 208 (33%); 2: 271 (43%); 6: 396 (63%); 14: 509 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667 | 0: 633 (100%); 0.1667: 129 (20%) | 0: 387 (61%); 0.1667: 513 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3, 0.5, 0.75 | 0: 633 (100%); 0.3: 384 (61%); 0.5: 267 (42%); 0.75: 131 (21%) | 0: 184 (29%); 0.3: 255 (40%); 0.5: 418 (66%); 0.75: 518 (82%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 2, 4, 10 | 0: 633 (100%); 2: 390 (62%); 4: 282 (45%); 10: 133 (21%) | 0: 145 (23%); 2: 310 (49%); 4: 392 (62%); 10: 510 (81%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 1, 2, 6, 14 | 1: 514 (81%); 2: 425 (67%); 6: 263 (42%); 14: 134 (21%) | 1: 208 (33%); 2: 271 (43%); 6: 396 (63%); 14: 509 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3.2, 9 | 0: 633 (100%); 1: 491 (78%); 3.2: 253 (40%); 9: 146 (23%) | 0: 142 (22%); 1: 261 (41%); 3.2: 380 (60%); 9: 509 (80%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.0609, 0.2734, 0.4217, 0.6667 | 0.0609: 506 (80%); 0.2734: 380 (60%); 0.4217: 253 (40%); 0.6667: 133 (21%) | 0.0609: 127 (20%); 0.2734: 254 (40%); 0.4217: 380 (60%); 0.6667: 512 (81%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3536, 0.75 | 0: 584 (92%); 0.3536: 253 (40%); 0.75: 128 (20%) | 0: 272 (43%); 0.3536: 380 (60%); 0.75: 507 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.1136, 0.3703, 0.6667 | 0: 584 (92%); 0.1136: 380 (60%); 0.3703: 253 (40%); 0.6667: 137 (22%) | 0: 233 (37%); 0.1136: 254 (40%); 0.3703: 380 (60%); 0.6667: 509 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1136, 0.3703, 0.6667 | 0: 584 (92%); 0.1136: 380 (60%); 0.3703: 253 (40%); 0.6667: 137 (22%) | 0: 233 (37%); 0.1136: 254 (40%); 0.3703: 380 (60%); 0.6667: 509 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1252, 0, 0.2032 | -0.1252: 506 (80%); 0: 457 (72%); 0.2032: 127 (20%) | -0.1252: 127 (20%); 0: 412 (65%); 0.2032: 506 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.5499, 0, 0.6881, 1.9432 | -0.5499: 507 (80%); 0: 401 (63%); 0.6881: 253 (40%); 1.9432: 127 (20%) | -0.5499: 128 (20%); 0: 291 (46%); 0.6881: 380 (60%); 1.9432: 506 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 11 | 2: 524 (83%); 4: 409 (65%); 7: 271 (43%); 11: 144 (23%) | 2: 164 (26%); 4: 268 (42%); 7: 402 (64%); 11: 512 (81%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0502, -0.0008, 0.0468, 0.0901 | -0.0502: 506 (80%); -0.0008: 379 (60%); 0.0468: 253 (40%); 0.0901: 127 (20%) | -0.0502: 127 (20%); -0.0008: 254 (40%); 0.0468: 380 (60%); 0.0901: 506 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0739, -0.0177, 0.0403, 0.1236 | -0.0739: 506 (80%); -0.0177: 380 (60%); 0.0403: 253 (40%); 0.1236: 127 (20%) | -0.0739: 127 (20%); -0.0177: 253 (40%); 0.0403: 380 (60%); 0.1236: 506 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0123, 0.0173, 0.0466, 0.0786 | -0.0123: 506 (80%); 0.0173: 381 (60%); 0.0466: 254 (40%); 0.0786: 127 (20%) | -0.0123: 127 (20%); 0.0173: 252 (40%); 0.0466: 379 (60%); 0.0786: 506 (80%) | OFFLINE |
| pct_from_avwap_20low | (not found by literal grep) | 99.2% | 0.7952, 2.4864, 4.2216, 6.9478 | 0.7952: 502 (79%); 2.4864: 377 (60%); 4.2216: 251 (40%); 6.9478: 126 (20%) | 0.7952: 126 (20%); 2.4864: 251 (40%); 4.2216: 377 (60%); 6.9478: 502 (79%) | OFFLINE |
| pct_from_avwap_252low | (not found by literal grep) | 98.6% | 1.1184, 6.2504, 13.3148, 25.0628 | 1.1184: 499 (79%); 6.2504: 374 (59%); 13.3148: 250 (39%); 25.0628: 125 (20%) | 1.1184: 125 (20%); 6.2504: 250 (39%); 13.3148: 374 (59%); 25.0628: 499 (79%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 99.5% | 0.9852, 3.1338, 5.9958, 10.4602 | 0.9852: 504 (80%); 3.1338: 378 (60%); 5.9958: 252 (40%); 10.4602: 126 (20%) | 0.9852: 126 (20%); 3.1338: 252 (40%); 5.9958: 378 (60%); 10.4602: 504 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -15.0754, 2.7388, 22.0578, 48.93 | -15.0754: 506 (80%); 2.7388: 380 (60%); 22.0578: 253 (40%); 48.93: 127 (20%) | -15.0754: 127 (20%); 2.7388: 253 (40%); 22.0578: 380 (60%); 48.93: 506 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0534, 0.0727, 0.0956, 0.1416 | 0.0534: 510 (81%); 0.0727: 381 (60%); 0.0956: 254 (40%); 0.1416: 127 (20%) | 0.0534: 127 (20%); 0.0727: 254 (40%); 0.0956: 381 (60%); 0.1416: 506 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.117, 0.2186, 0.3309, 0.478 | 0.117: 506 (80%); 0.2186: 380 (60%); 0.3309: 254 (40%); 0.478: 127 (20%) | 0.117: 127 (20%); 0.2186: 253 (40%); 0.3309: 380 (60%); 0.478: 506 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.5451, -0.964, 0.649, 2.3856 | -2.5451: 506 (80%); -0.964: 380 (60%); 0.649: 253 (40%); 2.3856: 127 (20%) | -2.5451: 127 (20%); -0.964: 253 (40%); 0.649: 380 (60%); 2.3856: 506 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.6099, -0.1391, 0.401, 0.904 | -0.6099: 506 (80%); -0.1391: 380 (60%); 0.401: 253 (40%); 0.904: 127 (20%) | -0.6099: 127 (20%); -0.1391: 253 (40%); 0.401: 380 (60%); 0.904: 506 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -2.6503, -1.2095, 0.5479, 2.0807 | -2.6503: 506 (80%); -1.2095: 380 (60%); 0.5479: 253 (40%); 2.0807: 127 (20%) | -2.6503: 127 (20%); -1.2095: 253 (40%); 0.5479: 380 (60%); 2.0807: 506 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -6.294, -0.5264, 4.457, 9.368 | -6.294: 506 (80%); -0.5264: 380 (60%); 4.457: 253 (40%); 9.368: 127 (20%) | -6.294: 127 (20%); -0.5264: 253 (40%); 4.457: 380 (60%); 9.368: 506 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 42.408, 49.796, 56.552, 64.816 | 42.408: 506 (80%); 49.796: 380 (60%); 56.552: 253 (40%); 64.816: 127 (20%) | 42.408: 127 (20%); 49.796: 253 (40%); 56.552: 380 (60%); 64.816: 506 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 54.276, 70.534, 83.178, 93.372 | 54.276: 506 (80%); 70.534: 380 (60%); 83.178: 253 (40%); 93.372: 127 (20%) | 54.276: 127 (20%); 70.534: 253 (40%); 83.178: 380 (60%); 93.372: 506 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 43.834, 49.56, 54.992, 61.378 | 43.834: 506 (80%); 49.56: 380 (60%); 54.992: 253 (40%); 61.378: 127 (20%) | 43.834: 127 (20%); 49.56: 253 (40%); 54.992: 380 (60%); 61.378: 506 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 42.564, 51.218, 59.676, 70.112 | 42.564: 506 (80%); 51.218: 380 (60%); 59.676: 253 (40%); 70.112: 127 (20%) | 42.564: 127 (20%); 51.218: 253 (40%); 59.676: 380 (60%); 70.112: 506 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 633 (100%) | 0: 632 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0324, 0.0514, 0.0624, 0.0866 | 0.0324: 508 (80%); 0.0514: 385 (61%); 0.0624: 258 (41%); 0.0866: 127 (20%) | 0.0324: 129 (20%); 0.0514: 254 (40%); 0.0624: 436 (69%); 0.0866: 506 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0976, -0.071, -0.0485, -0.0385 | -0.0976: 524 (83%); -0.071: 385 (61%); -0.0485: 262 (41%); -0.0385: 133 (21%) | -0.0976: 139 (22%); -0.071: 254 (40%); -0.0485: 387 (61%); -0.0385: 510 (81%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 633 (100%); 2: 141 (22%) | 0: 416 (66%); 2: 524 (83%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 100.0% | 28, 48, 65, 74 | 28: 515 (81%); 48: 382 (60%); 65: 259 (41%); 74: 135 (21%) | 28: 146 (23%); 48: 255 (40%); 65: 433 (68%); 74: 510 (81%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 99.1% | 0.0127, 0.0186, 0.0259, 0.0397 | 0.0127: 500 (79%); 0.0186: 375 (59%); 0.0259: 251 (40%); 0.0397: 125 (20%) | 0.0127: 127 (20%); 0.0186: 252 (40%); 0.0259: 376 (59%); 0.0397: 502 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.2485, 0.4277, 0.674, 0.8517 | 0.2485: 507 (80%); 0.4277: 380 (60%); 0.674: 253 (40%); 0.8517: 127 (20%) | 0.2485: 127 (20%); 0.4277: 253 (40%); 0.674: 380 (60%); 0.8517: 506 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 29.88, 60.18, 91.56, 156.84 | 29.88: 506 (80%); 60.18: 380 (60%); 91.56: 253 (40%); 156.84: 127 (20%) | 29.88: 127 (20%); 60.18: 253 (40%); 91.56: 380 (60%); 156.84: 506 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -3.004, 0.1815, 2.275, 7.011 | -3.004: 506 (80%); 0.1815: 380 (60%); 2.275: 253 (40%); 7.011: 127 (20%) | -3.004: 127 (20%); 0.1815: 253 (40%); 2.275: 380 (60%); 7.011: 506 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 24.638, 43.436, 63.46, 81.04 | 24.638: 506 (80%); 43.436: 380 (60%); 63.46: 253 (40%); 81.04: 127 (20%) | 24.638: 127 (20%); 43.436: 253 (40%); 63.46: 380 (60%); 81.04: 506 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 27.952, 47.948, 68.032, 84.456 | 27.952: 506 (80%); 47.948: 380 (60%); 68.032: 253 (40%); 84.456: 127 (20%) | 27.952: 127 (20%); 47.948: 253 (40%); 68.032: 380 (60%); 84.456: 506 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 18.726, 41.992, 73.908, 95.312 | 18.726: 506 (80%); 41.992: 380 (60%); 73.908: 253 (40%); 95.312: 127 (20%) | 18.726: 127 (20%); 41.992: 253 (40%); 73.908: 380 (60%); 95.312: 506 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 24.078, 50.008, 84.234, 100 | 24.078: 506 (80%); 50.008: 380 (60%); 84.234: 253 (40%); 100: 165 (26%) | 24.078: 127 (20%); 50.008: 253 (40%); 84.234: 380 (60%); 100: 633 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 11, 16 | 5: 517 (82%); 10: 400 (63%); 11: 332 (52%); 16: 181 (29%) | 5: 138 (22%); 10: 301 (48%); 11: 391 (62%); 16: 526 (83%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 6, 10, 12, 17 | 6: 516 (82%); 10: 389 (61%); 12: 326 (52%); 17: 135 (21%) | 6: 133 (21%); 10: 273 (43%); 12: 396 (63%); 17: 512 (81%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 43.536, 48.762, 53.326, 58.178 | 43.536: 506 (80%); 48.762: 380 (60%); 53.326: 253 (40%); 58.178: 127 (20%) | 43.536: 127 (20%); 48.762: 253 (40%); 53.326: 380 (60%); 58.178: 506 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.2143, 0.523, 0.6905, 0.9206 | 0.2143: 508 (80%); 0.523: 380 (60%); 0.6905: 259 (41%); 0.9206: 134 (21%) | 0.2143: 138 (22%); 0.523: 253 (40%); 0.6905: 382 (60%); 0.9206: 542 (86%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 16.04, 18.39, 21.972, 26.19 | 16.04: 510 (81%); 18.39: 398 (63%); 21.972: 253 (40%); 26.19: 138 (22%) | 16.04: 133 (21%); 18.39: 273 (43%); 21.972: 380 (60%); 26.19: 508 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 16.04, 18.39, 21.972, 26.19 | 16.04: 510 (81%); 18.39: 398 (63%); 21.972: 253 (40%); 26.19: 138 (22%) | 16.04: 133 (21%); 18.39: 273 (43%); 21.972: 380 (60%); 26.19: 508 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8663, 0.9092, 0.9357, 0.9883 | 0.8663: 506 (80%); 0.9092: 381 (60%); 0.9357: 261 (41%); 0.9883: 146 (23%) | 0.8663: 127 (20%); 0.9092: 260 (41%); 0.9357: 385 (61%); 0.9883: 517 (82%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.734, 0.94, 1.11, 1.4 | 0.734: 506 (80%); 0.94: 382 (60%); 1.11: 261 (41%); 1.4: 128 (20%) | 0.734: 127 (20%); 0.94: 258 (41%); 1.11: 381 (60%); 1.4: 508 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0254, 0.0636, 0.1071, 0.1785 | 0.0254: 509 (80%); 0.0636: 380 (60%); 0.1071: 254 (40%); 0.1785: 127 (20%) | 0.0254: 127 (20%); 0.0636: 253 (40%); 0.1071: 380 (60%); 0.1785: 506 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 40.9716, 69.6051, 108.5934, 166.7974 | 40.9716: 506 (80%); 69.6051: 380 (60%); 108.5934: 253 (40%); 166.7974: 127 (20%) | 40.9716: 127 (20%); 69.6051: 253 (40%); 108.5934: 380 (60%); 166.7974: 506 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 38.7212, 65.7741, 101.5452, 159.2716 | 38.7212: 506 (80%); 65.7741: 380 (60%); 101.5452: 253 (40%); 159.2716: 127 (20%) | 38.7212: 127 (20%); 65.7741: 253 (40%); 101.5452: 380 (60%); 159.2716: 506 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 35.5836, 60.9511, 96.1775, 150.6218 | 35.5836: 506 (80%); 60.9511: 380 (60%); 96.1775: 253 (40%); 150.6218: 127 (20%) | 35.5836: 127 (20%); 60.9511: 253 (40%); 96.1775: 380 (60%); 150.6218: 506 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 43.4409, 74.0324, 115.4179, 182.0577 | 43.4409: 506 (80%); 74.0324: 380 (60%); 115.4179: 253 (40%); 182.0577: 127 (20%) | 43.4409: 127 (20%); 74.0324: 253 (40%); 115.4179: 380 (60%); 182.0577: 506 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 45.9468, 77.732, 122.1488, 194.8891 | 45.9468: 506 (80%); 77.732: 380 (60%); 122.1488: 253 (40%); 194.8891: 127 (20%) | 45.9468: 127 (20%); 77.732: 253 (40%); 122.1488: 380 (60%); 194.8891: 506 (80%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 1.7404, 2.1136, 2.692, 3.8114 | 1.7404: 506 (80%); 2.1136: 380 (60%); 2.692: 253 (40%); 3.8114: 127 (20%) | 1.7404: 127 (20%); 2.1136: 253 (40%); 2.692: 380 (60%); 3.8114: 506 (80%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0711, -0.0119, 0.0375, 0.1002 | -0.0711: 506 (80%); -0.0119: 381 (60%); 0.0375: 253 (40%); 0.1002: 127 (20%) | -0.0711: 127 (20%); -0.0119: 254 (40%); 0.0375: 380 (60%); 0.1002: 506 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -65.718, -44.066, -27.22, -16.728 | -65.718: 506 (80%); -44.066: 380 (60%); -27.22: 253 (40%); -16.728: 127 (20%) | -65.718: 127 (20%); -44.066: 253 (40%); -27.22: 380 (60%); -16.728: 506 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 98.7% | 0.8475, 1.0864, 1.3228, 1.6059 | 0.8475: 500 (79%); 1.0864: 375 (59%); 1.3228: 250 (39%); 1.6059: 125 (20%) | 0.8475: 125 (20%); 1.0864: 251 (40%); 1.3228: 375 (59%); 1.6059: 500 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 98.7% | 5, 8, 9, 10 | 5: 539 (85%); 8: 388 (61%); 9: 300 (47%); 10: 186 (29%) | 5: 130 (21%); 8: 325 (51%); 9: 439 (69%); 10: 625 (99%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 98.6% | 0.0321, 0.0438, 0.0596, 0.0892 | 0.0321: 500 (79%); 0.0438: 375 (59%); 0.0596: 250 (39%); 0.0892: 125 (20%) | 0.0321: 126 (20%); 0.0438: 250 (39%); 0.0596: 376 (59%); 0.0892: 499 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 98.6% | 5, 8, 9, 10 | 5: 531 (84%); 8: 377 (60%); 9: 291 (46%); 10: 169 (27%) | 5: 140 (22%); 8: 333 (53%); 9: 455 (72%); 10: 624 (99%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 98.7% | -0.1611, 0.0057, 0.1813, 0.4651 | -0.1611: 500 (79%); 0.0057: 375 (59%); 0.1813: 250 (39%); 0.4651: 125 (20%) | -0.1611: 126 (20%); 0.0057: 250 (39%); 0.1813: 375 (59%); 0.4651: 500 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 98.7% | 3, 5, 8, 10 | 3: 510 (81%); 5: 418 (66%); 8: 263 (42%); 10: 136 (21%) | 3: 165 (26%); 5: 258 (41%); 8: 422 (67%); 10: 625 (99%) | OFFLINE |
| year_low | backtest/signals/technical.py | 100.0% | 28.394, 53.9021, 82.87, 138.8025 | 28.394: 506 (80%); 53.9021: 380 (60%); 82.87: 253 (40%); 138.8025: 128 (20%) | 28.394: 127 (20%); 53.9021: 253 (40%); 82.87: 380 (60%); 138.8025: 509 (80%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 10.0% |
| 8k_item_5_02_filed_within_7d | 4.4% |
| above_avwap_20high | 30.3% |
| above_avwap_20low | 87.8% |
| above_avwap_252low | 82.6% |
| above_avwap_50low | 87.0% |
| above_cam_r3 | 60.0% |
| above_cam_r4 | 37.9% |
| above_cpr | 82.9% |
| above_pivot | 83.6% |
| above_prev_high | 52.3% |
| above_prev_high_clearance_atr_05 | 15.5% |
| above_prev_low | 96.5% |
| above_r1 | 43.9% |
| above_r2 | 19.7% |
| above_vwap | 63.3% |
| above_wood_p | 81.4% |
| ad_rising | 47.6% |
| adx_cross_up | 2.4% |
| adx_cross_up_20 | 1.6% |
| adx_di_bear | 38.1% |
| adx_di_bull | 61.9% |
| adx_strong | 7.7% |
| adx_trending | 43.4% |
| ao_cross_dn | 1.1% |
| ao_cross_up | 5.5% |
| ao_positive | 47.6% |
| ao_twin_peaks_bull | 7.6% |
| at_key_fib | 11.1% |
| at_key_fib_wide | 28.8% |
| avwap_20high_loss_recent_3d | 11.4% |
| avwap_20high_reclaim_recent_3d | 28.9% |
| avwap_20low_loss_recent_3d | 5.7% |
| avwap_20low_reclaim_recent_3d | 28.0% |
| avwap_252low_loss_recent_3d | 2.6% |
| avwap_252low_reclaim_recent_3d | 12.7% |
| avwap_50low_loss_recent_3d | 3.8% |
| avwap_50low_reclaim_recent_3d | 21.0% |
| bb_10_20_above_mid | 70.9% |
| bb_10_20_expanding | 49.6% |
| bb_10_20_pctb_gt_75 | 45.7% |
| bb_10_20_pctb_gt_8 | 38.4% |
| bb_10_20_pctb_gt_85 | 31.1% |
| bb_10_20_pctb_gt_9 | 23.5% |
| bb_10_20_pctb_gt_95 | 16.0% |
| bb_10_20_pctb_lt_05 | 0.9% |
| bb_10_20_pctb_lt_1 | 0.9% |
| bb_10_20_pctb_lt_15 | 1.9% |
| bb_10_20_pctb_lt_2 | 3.9% |
| bb_10_20_pctb_lt_25 | 6.2% |
| bb_10_20_reclaim_from_lower_recent_3d | 6.0% |
| bb_10_20_reclaim_from_upper_recent_3d | 9.8% |
| bb_10_20_squeeze | 26.4% |
| bb_10_20_touch_lower | 0.6% |
| bb_10_20_touch_upper | 16.1% |
| bb_20_15_above_mid | 59.6% |
| bb_20_15_expanding | 55.5% |
| bb_20_15_pctb_gt_75 | 46.6% |
| bb_20_15_pctb_gt_8 | 43.3% |
| bb_20_15_pctb_gt_85 | 38.4% |
| bb_20_15_pctb_gt_9 | 35.1% |
| bb_20_15_pctb_gt_95 | 32.7% |
| bb_20_15_pctb_lt_05 | 5.8% |
| bb_20_15_pctb_lt_1 | 9.0% |
| bb_20_15_pctb_lt_15 | 13.1% |
| bb_20_15_pctb_lt_2 | 17.1% |
| bb_20_15_pctb_lt_25 | 21.6% |
| bb_20_15_reclaim_from_lower_recent_3d | 16.7% |
| bb_20_15_reclaim_from_upper_recent_3d | 5.1% |
| bb_20_15_squeeze | 19.0% |
| bb_20_15_touch_lower | 5.8% |
| bb_20_15_touch_upper | 32.1% |
| bb_20_20_above_mid | 59.6% |
| bb_20_20_expanding | 55.5% |
| bb_20_20_pctb_gt_75 | 40.0% |
| bb_20_20_pctb_gt_8 | 35.1% |
| bb_20_20_pctb_gt_85 | 31.4% |
| bb_20_20_pctb_gt_9 | 26.7% |
| bb_20_20_pctb_gt_95 | 20.1% |
| bb_20_20_pctb_lt_05 | 1.1% |
| bb_20_20_pctb_lt_1 | 3.3% |
| bb_20_20_pctb_lt_15 | 5.4% |
| bb_20_20_pctb_lt_2 | 9.0% |
| bb_20_20_pctb_lt_25 | 13.9% |
| bb_20_20_reclaim_from_lower_recent_3d | 9.0% |
| bb_20_20_reclaim_from_upper_recent_3d | 5.8% |
| bb_20_20_squeeze | 8.8% |
| bb_20_20_touch_lower | 0.8% |
| bb_20_20_touch_upper | 19.1% |
| bearish_engulfing | 3.0% |
| bearish_pin_bar | 7.1% |
| below_avwap_20high | 69.5% |
| below_avwap_20low | 12.2% |
| below_avwap_252low | 17.4% |
| below_avwap_50low | 13.0% |
| below_cam_s3 | 6.3% |
| below_cam_s4 | 2.2% |
| below_cpr | 16.4% |
| below_ema_20 | 39.0% |
| below_ema_200 | 39.6% |
| below_ema_200_break_recent_5d | 3.3% |
| below_ema_20_break_recent_5d | 8.7% |
| below_ema_21 | 39.3% |
| below_ema_21_break_recent_5d | 8.4% |
| below_ema_50 | 42.5% |
| below_ema_50_break_recent_5d | 3.5% |
| below_ema_9 | 28.3% |
| below_ema_9_break_recent_5d | 11.4% |
| below_prev_high | 47.4% |
| below_prev_low | 3.5% |
| below_prev_low_clearance_atr_05 | 0.9% |
| below_s1 | 2.5% |
| below_s2 | 1.1% |
| below_sma_20 | 40.4% |
| below_sma_200 | 38.8% |
| below_sma_21 | 40.6% |
| below_sma_50 | 46.4% |
| below_sma_9 | 26.7% |
| below_vwap | 36.7% |
| blowoff_recent_3d | 1.9% |
| break_52w_high | 5.4% |
| break_52w_high_clearance_atr_05 | 2.2% |
| break_52w_high_confirmed_today | 4.4% |
| break_52w_low | 0.3% |
| bullish_pin_bar | 6.0% |
| ceo_buy | 0.6% |
| cfo_buy | 0.3% |
| chandelier_long_bullish | 70.8% |
| chandelier_long_flip_dn | 1.1% |
| chandelier_short_bearish | 55.0% |
| chandelier_short_flip_up | 7.4% |
| close_in_bottom_40pct_of_range | 68.9% |
| close_in_top_40pct_of_range | 8.8% |
| cluster_buy | 0.3% |
| cmf_cross_dn | 7.9% |
| cmf_cross_up | 1.7% |
| cmf_negative | 44.1% |
| cmf_positive | 55.9% |
| concentrated_sell | 5.9% |
| cpr_narrow | 85.3% |
| cpr_narrow_tight | 22.3% |
| cup_handle_detected | 7.1% |
| cup_handle_neckline_break_retest_long | 3.8% |
| dc10_breakout_dn | 1.1% |
| dc10_breakout_dn_1pct | 2.2% |
| dc10_breakout_up | 25.1% |
| dc10_breakout_up_1pct | 31.9% |
| dc10_new_high | 44.5% |
| dc10_strong_breakout_dn | 0.3% |
| dc10_strong_breakout_up | 9.5% |
| dc20_breakout_dn | 0.6% |
| dc20_breakout_up | 17.5% |
| dc20_new_high | 32.7% |
| dc20_resistance_break_retest_strong | 16.9% |
| dc20_support_break_retest_strong | 18.2% |
| defensive_leadership | 51.2% |
| director_only_buy | 4.5% |
| doji | 5.1% |
| double_bottom_detected | 9.8% |
| double_top_detected | 12.0% |
| dpi_elevated | 46.5% |
| drying_volume_on_down_turn | 46.4% |
| ema_20_50_bearish | 49.8% |
| ema_20_50_bullish | 50.2% |
| ema_20_50_death_cross | 0.2% |
| ema_20_50_golden_cross | 1.7% |
| ema_50_200_bearish | 38.8% |
| ema_50_200_bullish | 61.2% |
| ema_50_200_death_cross | 0.2% |
| ema_50_200_golden_cross | 1.0% |
| ema_9_21_bearish | 49.6% |
| ema_9_21_bullish | 50.4% |
| ema_9_21_death_cross | 0.5% |
| ema_9_21_golden_cross | 4.9% |
| evening_star | 1.3% |
| flag_bear_break_retest_short | 0.3% |
| flag_bear_broke | 0.3% |
| flag_bear_detected | 0.2% |
| flag_bull_break_retest_long | 1.4% |
| flag_bull_broke | 1.4% |
| flag_bull_detected | 0.2% |
| force_index_cross_dn | 0.8% |
| force_index_cross_up | 7.9% |
| force_index_positive | 64.1% |
| gap_up_2pct | 64.1% |
| hammer | 5.5% |
| head_shoulders_bottom_detected | 4.7% |
| head_shoulders_top_detected | 4.9% |
| house_cluster_buy | 7.1% |
| house_cluster_sell | 9.8% |
| htf_aligned_bear | 28.1% |
| htf_aligned_bull | 45.5% |
| htf_disagreement | 2.1% |
| hull_bearish | 35.4% |
| hull_bullish | 64.6% |
| hull_flip_dn | 1.4% |
| hull_flip_up | 11.5% |
| ichi_above_cloud | 46.0% |
| ichi_above_cloud_break_recent_5d | 12.6% |
| ichi_below_cloud | 41.5% |
| ichi_below_cloud_break_recent_5d | 4.3% |
| ichi_cloud_thick | 88.6% |
| ichi_tk_bearish | 48.2% |
| ichi_tk_bullish | 45.7% |
| ichi_tk_cross_dn | 0.9% |
| ichi_tk_cross_up | 4.7% |
| ichi_weekly_above_cloud | 51.1% |
| ichi_weekly_below_cloud | 21.1% |
| ichi_weekly_in_cloud | 27.8% |
| in_reversal_window | 4.5% |
| inside_bar | 9.3% |
| inside_cpr | 2.4% |
| inside_kc | 78.7% |
| insider_cluster_active | 13.5% |
| institutional_buy | 86.9% |
| institutional_negative | 7.0% |
| institutional_persistence_growing | 46.4% |
| institutional_persistence_strong | 61.2% |
| institutional_strong_buy | 78.5% |
| inverted_cup_handle_detected | 3.6% |
| is_halloween_period | 57.0% |
| is_halloween_period_first_day | 0.3% |
| is_january | 10.7% |
| is_january_extended | 11.1% |
| is_monday | 88.0% |
| is_summer_period | 43.0% |
| is_totm_window | 29.2% |
| is_totm_window_first_day | 14.1% |
| kc_touch_lower | 4.1% |
| kc_touch_upper | 20.2% |
| large_dollar_buy | 0.6% |
| macd_12_26_9_bearish | 43.9% |
| macd_12_26_9_bullish | 56.1% |
| macd_12_26_9_crossover_dn | 0.6% |
| macd_12_26_9_crossover_up | 7.3% |
| macd_8_21_5_bearish | 30.0% |
| macd_8_21_5_bullish | 70.0% |
| macd_8_21_5_crossover_dn | 0.9% |
| macd_8_21_5_crossover_up | 10.1% |
| marubozu_bear | 0.6% |
| mfi_broad_overbought | 18.5% |
| mfi_broad_oversold | 5.5% |
| mfi_overbought | 5.8% |
| mfi_oversold | 0.6% |
| monthly_above_sma_12 | 61.3% |
| monthly_above_sma_6 | 56.5% |
| monthly_bias_bear | 33.2% |
| monthly_bias_bull | 51.1% |
| monthly_momentum_pos | 60.4% |
| near_52w_high | 11.2% |
| near_52w_high_95pct | 20.4% |
| near_52w_low | 0.8% |
| near_52w_low_105pct | 2.5% |
| near_52w_low_retest_short | 1.1% |
| near_avwap_20high_atr_05x | 43.4% |
| near_avwap_20high_atr_10x | 73.2% |
| near_avwap_20high_atr_15x | 90.0% |
| near_avwap_20high_atr_20x | 96.2% |
| near_avwap_20low_atr_05x | 31.1% |
| near_avwap_20low_atr_10x | 52.1% |
| near_avwap_20low_atr_15x | 70.5% |
| near_avwap_20low_atr_20x | 78.8% |
| near_avwap_252low_atr_05x | 11.2% |
| near_avwap_252low_atr_10x | 23.7% |
| near_avwap_252low_atr_15x | 33.0% |
| near_avwap_252low_atr_20x | 39.1% |
| near_avwap_50low_atr_05x | 24.4% |
| near_avwap_50low_atr_10x | 41.3% |
| near_avwap_50low_atr_15x | 56.8% |
| near_avwap_50low_atr_20x | 65.4% |
| near_cam_r3 | 16.0% |
| near_cam_s3 | 5.2% |
| near_cam_s4 | 1.4% |
| near_fib_236 | 5.4% |
| near_fib_382 | 4.6% |
| near_fib_500 | 2.5% |
| near_fib_618 | 3.9% |
| near_fib_786 | 3.3% |
| near_pivot | 9.3% |
| near_prev_close | 10.6% |
| near_prev_high | 13.6% |
| near_prev_low | 1.4% |
| near_r1 | 16.1% |
| near_r1_wide | 62.4% |
| near_r2 | 7.6% |
| near_r2_wide | 39.0% |
| near_s1 | 1.7% |
| near_s1_wide | 13.0% |
| near_s2 | 0.2% |
| near_s2_wide | 3.5% |
| near_s3 | 0.2% |
| near_wood_r1 | 10.1% |
| near_wood_s1 | 3.0% |
| news_uses_polygon_score | 34.6% |
| obv_bearish | 38.7% |
| obv_bullish | 61.3% |
| obv_diverge_bull | 7.6% |
| obv_falling | 28.3% |
| obv_rising | 71.7% |
| outside_bar | 5.7% |
| pead_negative_surprise | 11.7% |
| pead_positive_surprise | 31.5% |
| pin_bar | 13.1% |
| po3_accumulation_active | 15.2% |
| po3_bearish | 41.9% |
| po3_manipulation_sweep_down | 0.6% |
| po3_manipulation_sweep_up | 10.6% |
| po3_mmsm_setup | 4.9% |
| po3_sweep_above_prior_high | 87.8% |
| po3_sweep_below_prior_low | 10.4% |
| ppo_bullish | 54.2% |
| ppo_crossover_dn | 0.5% |
| ppo_crossover_up | 6.8% |
| price_above_dema | 71.2% |
| price_above_ema_20 | 61.0% |
| price_above_ema_200 | 60.4% |
| price_above_ema_200_break_recent_5d | 13.2% |
| price_above_ema_20_break_recent_5d | 31.9% |
| price_above_ema_21 | 60.7% |
| price_above_ema_21_break_recent_5d | 31.4% |
| price_above_ema_50 | 57.5% |
| price_above_ema_50_break_recent_5d | 21.6% |
| price_above_ema_9 | 71.7% |
| price_above_ema_9_break_recent_5d | 49.3% |
| price_above_hull | 79.9% |
| price_above_sma_200 | 61.2% |
| price_above_sma_21 | 59.4% |
| price_above_sma_50 | 53.6% |
| price_above_tema | 75.8% |
| price_below_dema | 28.8% |
| price_below_hull | 20.1% |
| price_below_tema | 24.2% |
| psar_bullish | 66.7% |
| psar_flip_dn | 0.2% |
| psar_flip_up | 14.2% |
| r1_break_retest_long | 71.4% |
| recent_blowoff_at_r3 | 0.5% |
| recent_capitulation_at_s3 | 0.2% |
| resistance_break_retest | 25.1% |
| risk_off_regime_bond_signal | 11.7% |
| risk_off_regime_bond_signal_strong | 2.5% |
| risk_off_regime_gold_signal | 44.5% |
| risk_on_regime_bond_signal | 44.9% |
| risk_on_regime_bond_signal_strong | 17.2% |
| roc_positive | 57.3% |
| roc_turning_dn | 2.2% |
| roc_turning_up | 8.8% |
| rsi_14_bullish | 59.2% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.9% |
| rsi_14_cross_dn_overbought_recent_3d | 2.5% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.2% |
| rsi_14_cross_up_oversold_recent_3d | 4.7% |
| rsi_14_extreme_ob | 1.7% |
| rsi_14_extreme_os | 0.8% |
| rsi_14_overbought | 11.7% |
| rsi_14_oversold | 1.6% |
| rsi_14_rising | 82.3% |
| rsi_21_bullish | 58.1% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.6% |
| rsi_21_cross_dn_overbought_recent_3d | 1.7% |
| rsi_21_cross_up_oversold_recent_3d | 1.6% |
| rsi_21_extreme_ob | 0.3% |
| rsi_21_extreme_os | 0.6% |
| rsi_21_overbought | 5.5% |
| rsi_21_oversold | 1.1% |
| rsi_21_rising | 82.3% |
| rsi_2_bullish | 83.1% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 21.8% |
| rsi_2_cross_dn_overbought_recent_3d | 20.4% |
| rsi_2_cross_up_extreme_os_recent_3d | 37.1% |
| rsi_2_cross_up_oversold_recent_3d | 48.5% |
| rsi_2_extreme_ob | 44.5% |
| rsi_2_extreme_os | 2.7% |
| rsi_2_overbought | 61.0% |
| rsi_2_oversold | 4.6% |
| rsi_2_rising | 82.3% |
| rsi_9_bullish | 62.7% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 2.2% |
| rsi_9_cross_dn_overbought_recent_3d | 3.6% |
| rsi_9_cross_up_extreme_os_recent_3d | 2.4% |
| rsi_9_cross_up_oversold_recent_3d | 11.1% |
| rsi_9_extreme_ob | 6.3% |
| rsi_9_extreme_os | 0.8% |
| rsi_9_overbought | 20.2% |
| rsi_9_oversold | 3.5% |
| rsi_9_rising | 82.3% |
| s1_break_retest_short | 43.0% |
| sc_13d_filed_within_30d | 2.2% |
| sc_13g_filed_within_30d | 3.0% |
| sector_outperforming_spy | 25.0% |
| sector_underperforming_spy | 75.0% |
| shooting_star | 6.2% |
| sma_20_50_bullish | 44.1% |
| sma_20_50_golden_cross | 0.8% |
| sma_50_200_bullish | 62.5% |
| sma_50_200_golden_cross | 0.3% |
| sma_9_21_bullish | 46.8% |
| sma_9_21_golden_cross | 3.0% |
| smc_bos_bearish | 7.6% |
| smc_bos_bullish | 16.4% |
| smc_bos_retest_long | 3.2% |
| smc_bos_retest_short | 3.2% |
| smc_breaker_block_bearish | 10.0% |
| smc_breaker_block_bullish | 31.0% |
| smc_choch_bearish | 7.3% |
| smc_choch_bullish | 4.6% |
| smc_equal_highs_swept | 4.4% |
| smc_equal_lows_swept | 2.7% |
| smc_fvg_bearish_active | 30.3% |
| smc_fvg_bullish_active | 56.6% |
| smc_fvg_retest_long_zone | 13.6% |
| smc_fvg_retest_short_zone | 8.4% |
| smc_in_discount_zone | 52.8% |
| smc_in_premium_zone | 63.0% |
| smc_inverse_fvg_bearish | 70.8% |
| smc_inverse_fvg_bullish | 82.9% |
| smc_liquidity_swept_dn | 1.1% |
| smc_liquidity_swept_up | 1.4% |
| smc_mitigation_block_long | 0.5% |
| smc_mitigation_block_short | 3.5% |
| smc_ob_bearish_active | 31.6% |
| smc_ob_bullish_active | 34.8% |
| smc_ote_long_zone | 10.0% |
| smc_ote_short_zone | 4.9% |
| squeeze_fire_up | 5.1% |
| squeeze_in | 24.3% |
| squeeze_positive | 62.1% |
| stoch_bearish_cross | 10.3% |
| stoch_broad_overbought | 33.6% |
| stoch_broad_oversold | 17.4% |
| stoch_bullish_cross | 12.8% |
| stoch_overbought | 26.5% |
| stoch_oversold | 13.1% |
| stochrsi_cross_dn | 18.5% |
| stochrsi_cross_up | 36.0% |
| stochrsi_overbought | 43.4% |
| stochrsi_oversold | 16.7% |
| supertrend_bearish | 0.8% |
| supertrend_bullish | 99.2% |
| supertrend_flip_recent_long_5d | 2.7% |
| supertrend_flip_recent_short_5d | 0.5% |
| supertrend_flip_up | 0.2% |
| support_break_retest | 21.3% |
| tema_above_dema | 51.2% |
| tema_cross_dn | 0.5% |
| tema_cross_up | 5.8% |
| three_black_crows | 0.5% |
| triangle_apex_break_retest_long | 12.8% |
| triangle_ascending_detected | 5.2% |
| triangle_descending_detected | 7.1% |
| uo_overbought | 1.6% |
| uo_oversold | 1.4% |
| usd_strengthening | 30.0% |
| usd_weakening | 12.8% |
| vix_band_high | 43.1% |
| vix_band_low | 29.5% |
| vix_band_mid | 27.3% |
| vix_term_backwardation | 18.2% |
| vix_term_contango | 81.8% |
| vol_above_avg | 53.6% |
| vol_below_avg | 46.4% |
| vol_spike_12x | 32.2% |
| vol_spike_15x | 15.0% |
| vol_spike_17x | 10.1% |
| vol_spike_2x | 7.1% |
| vol_spike_2x_on_down_day_recent_3d | 4.7% |
| vol_spike_2x_on_up_day_recent_3d | 6.3% |
| vol_spike_3x | 2.5% |
| vp_above_value_area | 31.0% |
| vp_below_value_area | 15.8% |
| vp_close_above_poc | 58.9% |
| vp_close_below_poc | 41.1% |
| vp_in_value_area | 53.2% |
| weekly_above_ema_10 | 58.5% |
| weekly_above_ema_20 | 57.7% |
| weekly_bias_bear | 37.3% |
| weekly_bias_bull | 53.4% |
| weekly_momentum_pos | 54.7% |
| williams_r_overbought | 26.5% |
| williams_r_oversold | 9.3% |
| williams_r_rising | 65.4% |
| within_pead_window | 35.8% |
| within_post_deletion_window | 4.0% |
| within_post_inclusion_window | 4.5% |
| within_pre_rebalance_window | 3.1% |
| xs_avoid_high_ivol | 53.5% |
| xs_avoid_high_max | 53.4% |
| xs_high_beta_decile | 48.0% |
| xs_low_beta_bottom_quintile | 48.0% |
| xs_low_beta_decile | 5.1% |
| xs_low_beta_top_quintile | 5.1% |
| xs_momentum_bottom_decile | 9.8% |
| xs_momentum_bottom_quintile | 18.4% |
| xs_momentum_top_decile | 21.8% |
| xs_momentum_top_quintile | 32.5% |
| xs_quality_bottom_quintile | 26.8% |
| xs_quality_top_quintile | 18.0% |
| xs_quality_top_tercile | 40.5% |
| year_high_break_retest_long | 8.4% |
| year_low_break_retest_short | 3.5% |
| yoy_surprise_high | 61.8% |
| yoy_surprise_negative | 30.9% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 89.9% |
| committed_growth_holders | 89.9% |
| corp_donations_1y | 11.7% |
| corp_donations_count_1y | 11.7% |
| corp_donations_unique_pacs | 11.7% |
| cot_rut_commercials_pctile_3y | 62.1% |
| cot_rut_mmoney_pctile_3y | 62.1% |
| cup_handle_depth_pct | 15.0% |
| days_since_deletion | 7.9% |
| days_since_inclusion | 17.4% |
| days_to_next_holiday | 72.2% |
| days_to_rebalance | 10.3% |
| dpi_30d_avg | 96.8% |
| dpi_recent | 96.8% |
| earnings_announcement_return | 93.4% |
| earnings_eps_yoy_growth | 94.0% |
| gov_contracts_4q_sum | 40.0% |
| gov_contracts_last_qtr_amount | 40.0% |
| gov_contracts_qoq_growth | 40.0% |
| head_shoulders_magnitude_pct | 9.6% |
| insider_director_buyers_30d | 5.8% |
| insider_officer_buyers_30d | 5.8% |
| insider_total_shares_bought_30d | 5.8% |
| insider_unique_buyers_30d | 5.8% |
| inverted_cup_handle_height_pct | 10.3% |
| lobbying_amount_1y | 75.2% |
| lobbying_amount_q | 75.2% |
| lobbying_amount_yoy | 75.2% |
| otc_short_ratio_recent | 96.8% |
| otc_volume_recent | 96.8% |
| pair_half_life | 91.8% |
| pair_max_abs_zscore | 91.8% |
| pair_zscore_signed | 91.8% |
| pct_from_avwap_20high | 66.7% |
| persistent_holders_4q | 89.9% |
| persistent_holders_8q | 89.9% |
| sc_13g_latest_percent_owned | 1.7% |
| search_volume_index_recent | 80.1% |
| search_volume_observations | 80.1% |
| search_volume_zscore_30d | 80.1% |
| sector_etf_return_20d | 1.3% |
| spy_return_20d | 1.3% |
| total_active_holders | 89.9% |
| triangle_breakdown_pct | 7.1% |
| triangle_breakout_pct | 5.2% |
| xs_ivol | 97.8% |
| xs_ivol_decile | 97.8% |
| xs_quality_decile | 61.3% |
| xs_quality_gross_profitability | 61.3% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.996), `avwap_20low` (0.996), `avwap_252low` (0.988), `avwap_50low` (0.996), `bb_10_20_lower` (0.995), `bb_10_20_mid` (0.998), `bb_10_20_upper` (0.998), `bb_20_15_lower` (0.996), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.997), `bb_20_20_lower` (0.995), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.995), `cam_r1` (0.995), `cam_r2` (0.995), `cam_r3` (0.995), `cam_r4` (0.995), `cam_s1` (0.995), `cam_s2` (0.995), `cam_s3` (0.995), `cam_s4` (0.995), `chandelier_long_value` (0.997), `chandelier_short_value` (0.998), `cpr_bottom` (0.995), `cpr_top` (0.995), `cup_handle_breakout_level` (0.996), `cup_handle_rim` (0.991), `dc10_lower` (0.995), `dc10_mid` (0.998), `dc10_upper` (0.998), `dc20_lower` (0.996), `dc20_mid` (0.999), `dc20_upper` (0.996), `dema` (0.997), `double_bottom_neckline` (0.997), `double_bottom_trough` (0.997), `double_top_neckline` (0.991), `double_top_peak` (0.992), `entry_stop_long` (0.994), `entry_stop_short` (0.996), `fib_236` (0.993), `fib_382` (0.995), `fib_500` (0.996), `fib_618` (0.996), `fib_786` (0.996), `fib_ext_127` (0.985), `fib_ext_162` (0.98), `head_shoulders_bottom_neckline` (0.991), `head_shoulders_top_neckline` (0.999), `hull_ma` (0.995), `ichi_kijun` (0.999), `ichi_senkou_a` (0.989), `ichi_senkou_b` (0.983), `ichi_tenkan` (0.998), `inverted_cup_handle_breakdown_level` (0.998), `inverted_cup_handle_rim_low` (0.996), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (0.999), `monthly_close` (0.995), `monthly_sma_12` (0.969), `monthly_sma_6` (0.99), `pivot` (0.995), `prev_close` (0.995), `prev_high` (0.995), `prev_low` (0.995), `psar_value` (0.997), `r1` (0.995), `r2` (0.995), `r3` (0.995), `s1` (0.995), `s2` (0.995), `s3` (0.994), `supertrend_value` (0.993), `swing_high` (0.99), `swing_low` (0.992), `tema` (0.995), `triangle_resistance_level` (1.0), `triangle_support_level` (0.999), `vp_poc` (0.99), `vp_value_area_high` (0.993), `vp_value_area_low` (0.991), `weekly_close` (0.995), `weekly_ema_10` (0.999), `weekly_ema_20` (0.993), `wood_p` (0.995), `wood_r1` (0.995), `wood_r2` (0.995), `wood_s1` (0.995), `wood_s2` (0.995), `year_high` (0.96)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | gap threshold pct (NAME IS DECIMAL-SHIFT | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2 | days_since_last_earnings > 2 | 5 | subset-safe | no - derives offline |
| P3 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     1 x 5 x 1 = 5
offline gradings   5 level-combinations x 24 exits = 120
ENGINE RUNS        1 (every fire-adding axis sits at production-only until its env actuator exists)
check              1 x 5 = 5
```

B-row candidates NOT in this factorial: 630 census axes join it only when REGISTERED at the T3 band review.
