# Table A - cpr_narrow_momentum_short

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit fa06ebf3e at 2026-09-19 13:06:49 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** confluence | **status:** NOT-STARTED | **R5 fires:** 1696 | **surviving fires (T1):** 1696 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  below_cpr  <- backtest/signals/screener.py +1
       DEFN: today's price below cpr_bottom (technical.py:146)
       knobs P1.1-P1.1 (band rows in Table A)
P2  cpr_narrow_tight  <- backtest/signals/screener.py +1
       DEFN: CPR width < 0.05 x prior range - the B654 tight local variant (technical.py:103)
       knobs P2.1-P2.1 (band rows in Table A)
P3  macd_12_26_9_bearish  <- backtest/signals/screener.py
       DEFN: MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648)
       knobs P3.1-P3.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P4  rsi_14 < 50   [EXISTING-THRESHOLD]
P5  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_cpr_narrow_momentum_short (docstring and return dropped):

```python
fires = s.get('cpr_narrow_tight') and s.get('below_cpr') and (s.get('rsi_14', 50) < 50) and s.get('macd_12_26_9_bearish') and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | below_cpr - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | today's price below cpr_bottom (technical.py:146) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | buffer pct (price below cpr_bottom by) - backtest/signals/technical.py:146 | BRACKET zero | 0.0 | 0, 0.25 | none - entry price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | cpr_narrow_tight - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | CPR width < 0.05 x prior range - the B654 tight local variant (technical.py:103) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | width threshold (cpr_width < rng * X) - backtest/signals/technical.py:103 | BRACKET production (B654 local 0.05; the family's 0.15 stays with its own consumers) | 0.05 | 0.03, 0.05, 0.08 | none - cpr_width IS persisted but the denominator (prior-day range) is not | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | macd_12_26_9_bearish - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | span triple (fast, slow, signal) - backtest/signals/technical.py:634-648 | MEASURED availability - both triples are emitted and macd_8_21_5_* IS persisted | (12,26,9) | [(8,21,5), (12,26,9)] both computed in production; other triples are new | the (8,21,5) SWAP - re-evaluate on persisted macd_8_21_5 keys | any third triple; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | STRATEGY | rsi_14 `< 50` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `< 50` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P4.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `< 50` | 100.0% | TIGHTER = LOWER the ceiling: 34.98 -> 340 (20%); 39.97 -> 679 (40%); 44.03 -> 1019 (60%); 47.31 -> 1358 (80%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 16.37, 19.8, 23.84, 28.88 | 16.37: 1357 (80%); 19.8: 1018 (60%); 23.84: 679 (40%); 28.88: 340 (20%) | 16.37: 340 (20%); 19.8: 679 (40%); 23.84: 1019 (60%); 28.88: 1357 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 22.72, 25.7, 28.74, 32.92 | 22.72: 1358 (80%); 25.7: 1018 (60%); 28.74: 679 (40%); 32.92: 341 (20%) | 22.72: 340 (20%); 25.7: 682 (40%); 28.74: 1019 (60%); 32.92: 1357 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 14.6, 17.06, 19.39, 22.32 | 14.6: 1357 (80%); 17.06: 1018 (60%); 19.39: 679 (40%); 22.32: 340 (20%) | 14.6: 341 (20%); 17.06: 681 (40%); 19.39: 1019 (60%); 22.32: 1357 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -6.9633, -2.6844, -0.7413, 0.9015 | -6.9633: 1357 (80%); -2.6844: 1018 (60%); -0.7413: 679 (40%); 0.9015: 340 (20%) | -6.9633: 340 (20%); -2.6844: 679 (40%); -0.7413: 1018 (60%); 0.9015: 1357 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.2637, 2.2332, 3.6936, 6.3833 | 1.2637: 1357 (80%); 2.2332: 1018 (60%); 3.6936: 679 (40%); 6.3833: 340 (20%) | 1.2637: 340 (20%); 2.2332: 679 (40%); 3.6936: 1018 (60%); 6.3833: 1357 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.2637, 2.2332, 3.6936, 6.3833 | 1.2637: 1357 (80%); 2.2332: 1018 (60%); 3.6936: 679 (40%); 6.3833: 340 (20%) | 1.2637: 340 (20%); 2.2332: 679 (40%); 3.6936: 1018 (60%); 6.3833: 1357 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.927, 2.369, 2.857, 3.735 | 1.927: 1357 (80%); 2.369: 1018 (60%); 2.857: 680 (40%); 3.735: 341 (20%) | 1.927: 340 (20%); 2.369: 680 (40%); 2.857: 1018 (60%); 3.735: 1357 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0489, 0.0693, 0.0958, 0.1427 | 0.0489: 1358 (80%); 0.0693: 1018 (60%); 0.0958: 679 (40%); 0.1427: 340 (20%) | 0.0489: 342 (20%); 0.0693: 680 (40%); 0.0958: 1018 (60%); 0.1427: 1357 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.0579, 0.1434, 0.2301, 0.3682 | 0.0579: 1357 (80%); 0.1434: 1018 (60%); 0.2301: 680 (40%); 0.3682: 340 (20%) | 0.0579: 341 (20%); 0.1434: 679 (40%); 0.2301: 1018 (60%); 0.3682: 1357 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0522, 0.0731, 0.0978, 0.1367 | 0.0522: 1357 (80%); 0.0731: 1018 (60%); 0.0978: 679 (40%); 0.1367: 341 (20%) | 0.0522: 340 (20%); 0.0731: 679 (40%); 0.0978: 1020 (60%); 0.1367: 1357 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.1372, 0.0129, 0.133, 0.25 | -0.1372: 1358 (80%); 0.0129: 1018 (60%); 0.133: 679 (40%); 0.25: 340 (20%) | -0.1372: 341 (20%); 0.0129: 680 (40%); 0.133: 1018 (60%); 0.25: 1357 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0696, 0.0974, 0.1304, 0.1823 | 0.0696: 1357 (80%); 0.0974: 1020 (60%); 0.1304: 679 (40%); 0.1823: 341 (20%) | 0.0696: 340 (20%); 0.0974: 679 (40%); 0.1304: 1020 (60%); 0.1823: 1357 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.0221, 0.1347, 0.2248, 0.3125 | 0.0221: 1358 (80%); 0.1347: 1018 (60%); 0.2248: 679 (40%); 0.3125: 340 (20%) | 0.0221: 341 (20%); 0.1347: 680 (40%); 0.2248: 1018 (60%); 0.3125: 1357 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0457, -0.0209, 0.0005, 0.0272 | -0.0457: 1359 (80%); -0.0209: 1018 (60%); 0.0005: 684 (40%); 0.0272: 345 (20%) | -0.0457: 342 (20%); -0.0209: 680 (40%); 0.0005: 1019 (60%); 0.0272: 1358 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1413, 0.1671, 0.1882, 0.2567 | 0.1413: 1355 (80%); 0.1671: 1016 (60%); 0.1882: 677 (40%); 0.2567: 339 (20%) | 0.1413: 341 (20%); 0.1671: 680 (40%); 0.1882: 1019 (60%); 0.2567: 1357 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1696 (100%) | 0: 1634 (96%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1371, -0.0682, -0.0084, 0.0769 | -0.1371: 1357 (80%); -0.0682: 1018 (60%); -0.0084: 679 (40%); 0.0769: 340 (20%) | -0.1371: 340 (20%); -0.0682: 679 (40%); -0.0084: 1019 (60%); 0.0769: 1357 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 1696 (100%); 1: 702 (41%) | 0: 994 (59%); 1: 1409 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2365, -0.2011, -0.1572, -0.1207 | -0.2365: 1357 (80%); -0.2011: 1024 (60%); -0.1572: 679 (40%); -0.1207: 384 (23%) | -0.2365: 344 (20%); -0.2011: 681 (40%); -0.1572: 1030 (61%); -0.1207: 1362 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3782, 0.5897, 0.6923, 0.7692 | 0.3782: 1368 (81%); 0.5897: 1076 (63%); 0.6923: 691 (41%); 0.7692: 343 (20%) | 0.3782: 347 (20%); 0.5897: 682 (40%); 0.6923: 1058 (62%); 0.7692: 1432 (84%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2692, 0.4231, 0.6282, 0.8718 | 0.2692: 1364 (80%); 0.4231: 1024 (60%); 0.6282: 728 (43%); 0.8718: 342 (20%) | 0.2692: 341 (20%); 0.4231: 686 (40%); 0.6282: 1024 (60%); 0.8718: 1365 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1296, -0.0304, 0.0223, 0.138 | -0.1296: 1357 (80%); -0.0304: 1019 (60%); 0.0223: 706 (42%); 0.138: 340 (20%) | -0.1296: 340 (20%); -0.0304: 691 (41%); 0.0223: 1040 (61%); 0.138: 1361 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2115, 0.3846, 0.5064, 0.7051 | 0.2115: 1369 (81%); 0.3846: 1025 (60%); 0.5064: 685 (40%); 0.7051: 366 (22%) | 0.2115: 343 (20%); 0.3846: 693 (41%); 0.5064: 1033 (61%); 0.7051: 1358 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1474, 0.3526, 0.4808, 0.7244 | 0.1474: 1361 (80%); 0.3526: 1028 (61%); 0.4808: 688 (41%); 0.7244: 340 (20%) | 0.1474: 350 (21%); 0.3526: 721 (43%); 0.4808: 1047 (62%); 0.7244: 1366 (81%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.4759, -0.2655, -0.0869, 0.0892 | -0.4759: 1374 (81%); -0.2655: 1024 (60%); -0.0869: 687 (41%); 0.0892: 345 (20%) | -0.4759: 345 (20%); -0.2655: 696 (41%); -0.0869: 1067 (63%); 0.0892: 1360 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3974, 0.5897, 0.8205, 0.9551 | 0.3974: 1367 (81%); 0.5897: 1029 (61%); 0.8205: 713 (42%); 0.9551: 350 (21%) | 0.3974: 354 (21%); 0.5897: 679 (40%); 0.8205: 1065 (63%); 0.9551: 1380 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1026, 0.2885, 0.5577, 0.7885 | 0.1026: 1363 (80%); 0.2885: 1032 (61%); 0.5577: 679 (40%); 0.7885: 350 (21%) | 0.1026: 342 (20%); 0.2885: 688 (41%); 0.5577: 1039 (61%); 0.7885: 1357 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0668, -0.0576, -0.0372, 0 | -0.0668: 1369 (81%); -0.0576: 1019 (60%); -0.0372: 689 (41%); 0: 550 (32%) | -0.0668: 342 (20%); -0.0576: 681 (40%); -0.0372: 1025 (60%); 0: 1655 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.391, 0.6667, 0.8718, 1 | 0.391: 1372 (81%); 0.6667: 1040 (61%); 0.8718: 693 (41%); 1: 440 (26%) | 0.391: 378 (22%); 0.6667: 707 (42%); 0.8718: 1022 (60%); 1: 1696 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1346, 0.3077, 0.5705, 0.9103 | 0.1346: 1360 (80%); 0.3077: 1027 (61%); 0.5705: 712 (42%); 0.9103: 344 (20%) | 0.1346: 340 (20%); 0.3077: 687 (41%); 0.5705: 1034 (61%); 0.9103: 1360 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0065, 0.0378, 0.0875, 0.2045 | 0.0065: 1357 (80%); 0.0378: 1026 (60%); 0.0875: 688 (41%); 0.2045: 351 (21%) | 0.0065: 341 (20%); 0.0378: 692 (41%); 0.0875: 1022 (60%); 0.2045: 1363 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5211, 0.7815, 0.9359, 0.9744 | 0.5211: 1367 (81%); 0.7815: 1025 (60%); 0.9359: 686 (40%); 0.9744: 381 (22%) | 0.5211: 344 (20%); 0.7815: 693 (41%); 0.9359: 1038 (61%); 0.9744: 1415 (83%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0952, 0.2949, 0.5385, 0.7664 | 0.0952: 1359 (80%); 0.2949: 1053 (62%); 0.5385: 695 (41%); 0.7664: 341 (20%) | 0.0952: 342 (20%); 0.2949: 701 (41%); 0.5385: 1022 (60%); 0.7664: 1358 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0141, 0.0787, 0.1491 | -0.0812: 1477 (87%); -0.0141: 1020 (60%); 0.0787: 682 (40%); 0.1491: 347 (20%) | -0.0812: 362 (21%); -0.0141: 679 (40%); 0.0787: 1021 (60%); 0.1491: 1360 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2049, -0.0125, 0.0457, 0.0978 | -0.2049: 1366 (81%); -0.0125: 1028 (61%); 0.0457: 680 (40%); 0.0978: 340 (20%) | -0.2049: 341 (20%); -0.0125: 679 (40%); 0.0457: 1018 (60%); 0.0978: 1366 (81%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2821, 0.5449, 0.75, 0.9103 | 0.2821: 1363 (80%); 0.5449: 1023 (60%); 0.75: 683 (40%); 0.9103: 369 (22%) | 0.2821: 344 (20%); 0.5449: 692 (41%); 0.75: 1029 (61%); 0.9103: 1383 (82%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1859, 0.3846, 0.5641, 0.8205 | 0.1859: 1360 (80%); 0.3846: 1044 (62%); 0.5641: 753 (44%); 0.8205: 341 (20%) | 0.1859: 369 (22%); 0.3846: 686 (40%); 0.5641: 1019 (60%); 0.8205: 1369 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.015, 0.035, 0.0683, 0.1433 | 0.015: 1374 (81%); 0.035: 1038 (61%); 0.0683: 680 (40%); 0.1433: 343 (20%) | 0.015: 341 (20%); 0.035: 679 (40%); 0.0683: 1022 (60%); 0.1433: 1361 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.6% | 33, 62, 86, 146 | 33: 1350 (80%); 62: 1031 (61%); 86: 673 (40%); 146: 336 (20%) | 33: 336 (20%); 62: 681 (40%); 86: 1008 (59%); 146: 1344 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.4% | 1.8001, 2.2841, 2.818, 3.571 | 1.8001: 1349 (80%); 2.2841: 1012 (60%); 2.818: 675 (40%); 3.571: 338 (20%) | 1.8001: 338 (20%); 2.2841: 675 (40%); 2.818: 1012 (60%); 3.571: 1349 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 8, 20, 28, 35 | 8: 1401 (83%); 20: 1040 (61%); 28: 742 (44%); 35: 370 (22%) | 8: 343 (20%); 20: 695 (41%); 28: 1019 (60%); 35: 1384 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3 | 1: 1423 (84%); 2: 1000 (59%); 3: 621 (37%) | 1: 696 (41%); 2: 1075 (63%); 3: 1403 (83%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0098, 0, 0.0146, 0.0255 | -0.0098: 1357 (80%); 0: 1054 (62%); 0.0146: 680 (40%); 0.0255: 360 (21%) | -0.0098: 343 (20%); 0: 709 (42%); 0.0146: 1027 (61%); 0.0255: 1359 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.7166, 26.0182, 26.63, 27.3171 | 24.7166: 1357 (80%); 26.0182: 1021 (60%); 26.63: 679 (40%); 27.3171: 379 (22%) | 24.7166: 345 (20%); 26.0182: 680 (40%); 26.63: 1022 (60%); 27.3171: 1372 (81%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.454, -0.081, 0.195, 0.74 | -0.454: 1358 (80%); -0.081: 1019 (60%); 0.195: 679 (40%); 0.74: 340 (20%) | -0.454: 340 (20%); -0.081: 679 (40%); 0.195: 1018 (60%); 0.74: 1357 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.74, -0.195, 0.081, 0.454 | -0.74: 1357 (80%); -0.195: 1018 (60%); 0.081: 679 (40%); 0.454: 340 (20%) | -0.74: 340 (20%); -0.195: 679 (40%); 0.081: 1019 (60%); 0.454: 1358 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0428, -0.0097, 0.0231, 0.0624 | -0.0428: 1362 (80%); -0.0097: 1019 (60%); 0.0231: 680 (40%); 0.0624: 340 (20%) | -0.0428: 342 (20%); -0.0097: 679 (40%); 0.0231: 1021 (60%); 0.0624: 1357 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0454, 8.4948, 8.7775, 9.1044 | 8.0454: 1356 (80%); 8.4948: 1005 (59%); 8.7775: 679 (40%); 9.1044: 341 (20%) | 8.0454: 340 (20%); 8.4948: 691 (41%); 8.7775: 1017 (60%); 9.1044: 1355 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 1684 (99%); 1: 498 (29%) | 0: 1186 (70%); 1: 1524 (90%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.3% | -1, 0 | -1: 1609 (95%); 0: 1346 (79%) | -1: 338 (20%); 0: 1398 (82%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 1684 (99%); 1: 528 (31%) | 0: 1156 (68%); 1: 1501 (89%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 3, 5, 110, 271 | 3: 1362 (80%); 5: 1112 (66%); 110: 680 (40%); 271: 342 (20%) | 3: 460 (27%); 5: 692 (41%); 110: 1018 (60%); 271: 1358 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 4, 87, 145 | 1: 1393 (82%); 4: 1062 (63%); 87: 682 (40%); 145: 340 (20%) | 1: 454 (27%); 4: 683 (40%); 87: 1022 (60%); 145: 1357 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -1.4027, -0.6887, -0.382, -0.1825 | -1.4027: 1357 (80%); -0.6887: 1018 (60%); -0.382: 679 (40%); -0.1825: 340 (20%) | -1.4027: 340 (20%); -0.6887: 679 (40%); -0.382: 1018 (60%); -0.1825: 1357 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -2.3569, -0.7106, -0.0495, 0.6415 | -2.3569: 1357 (80%); -0.7106: 1018 (60%); -0.0495: 679 (40%); 0.6415: 340 (20%) | -2.3569: 340 (20%); -0.7106: 679 (40%); -0.0495: 1018 (60%); 0.6415: 1357 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.5146, -0.2493, 0.373, 1.4047 | -1.5146: 1357 (80%); -0.2493: 1018 (60%); 0.373: 679 (40%); 1.4047: 340 (20%) | -1.5146: 340 (20%); -0.2493: 679 (40%); 0.373: 1018 (60%); 1.4047: 1357 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -1.1005, -0.471, -0.2237, -0.0403 | -1.1005: 1357 (80%); -0.471: 1018 (60%); -0.2237: 679 (40%); -0.0403: 340 (20%) | -1.1005: 340 (20%); -0.471: 679 (40%); -0.2237: 1018 (60%); -0.0403: 1357 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -3.1506, -1.2153, -0.4246, 0.1197 | -3.1506: 1357 (80%); -1.2153: 1018 (60%); -0.4246: 679 (40%); 0.1197: 340 (20%) | -3.1506: 340 (20%); -1.2153: 679 (40%); -0.4246: 1018 (60%); 0.1197: 1357 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -2.4594, -0.8531, -0.1483, 0.5614 | -2.4594: 1357 (80%); -0.8531: 1018 (60%); -0.1483: 679 (40%); 0.5614: 340 (20%) | -2.4594: 340 (20%); -0.8531: 679 (40%); -0.1483: 1018 (60%); 0.5614: 1357 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 29.92, 36.93, 43.11, 50.52 | 29.92: 1357 (80%); 36.93: 1018 (60%); 43.11: 679 (40%); 50.52: 340 (20%) | 29.92: 340 (20%); 36.93: 679 (40%); 43.11: 1018 (60%); 50.52: 1357 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.8% | 0.0052, 0.0119, 0.0209, 0.0382 | 0.0052: 1355 (80%); 0.0119: 1017 (60%); 0.0209: 676 (40%); 0.0382: 338 (20%) | 0.0052: 337 (20%); 0.0119: 675 (40%); 0.0209: 1016 (60%); 0.0382: 1354 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 9 | 0: 1696 (100%); 1: 1248 (74%); 3: 800 (47%); 9: 340 (20%) | 0: 448 (26%); 1: 713 (42%); 3: 1026 (60%); 9: 1395 (82%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1429 | 0: 1696 (100%); 0.1429: 353 (21%) | 0: 1174 (69%); 0.1429: 1371 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1111, 0.4211, 0.6667 | 0: 1696 (100%); 0.1111: 1018 (60%); 0.4211: 682 (40%); 0.6667: 387 (23%) | 0: 672 (40%); 0.1111: 684 (40%); 0.4211: 1018 (60%); 0.6667: 1371 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 2, 6 | 0: 1696 (100%); 1: 1137 (67%); 2: 845 (50%); 6: 356 (21%) | 0: 559 (33%); 1: 851 (50%); 2: 1034 (61%); 6: 1402 (83%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 9 | 0: 1696 (100%); 1: 1248 (74%); 3: 800 (47%); 9: 340 (20%) | 0: 448 (26%); 1: 713 (42%); 3: 1026 (60%); 9: 1395 (82%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 1696 (100%); 1: 1161 (68%); 3: 733 (43%); 8: 342 (20%) | 0: 535 (32%); 1: 804 (47%); 3: 1098 (65%); 8: 1399 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2576, 0.4118, 0.625 | 0: 1598 (94%); 0.2576: 1018 (60%); 0.4118: 680 (40%); 0.625: 345 (20%) | 0: 363 (21%); 0.2576: 679 (40%); 0.4118: 1018 (60%); 0.625: 1357 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.15, 0.5911 | 0: 1538 (91%); 0.15: 681 (40%); 0.5911: 340 (20%) | 0: 944 (56%); 0.15: 1019 (60%); 0.5911: 1357 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.32, 0.6161 | 0: 1543 (91%); 0.32: 680 (40%); 0.6161: 340 (20%) | 0: 771 (45%); 0.32: 1020 (60%); 0.6161: 1357 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.32, 0.6161 | 0: 1543 (91%); 0.32: 680 (40%); 0.6161: 340 (20%) | 0: 771 (45%); 0.32: 1020 (60%); 0.6161: 1357 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1746, 0, 0.125 | -0.1746: 1357 (80%); 0: 1227 (72%); 0.125: 341 (20%) | -0.1746: 340 (20%); 0: 1247 (74%); 0.125: 1358 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.7571, -0.4472, 0, 1.1002 | -0.7571: 1357 (80%); -0.4472: 1125 (66%); 0: 908 (54%); 1.1002: 340 (20%) | -0.7571: 347 (20%); -0.4472: 679 (40%); 0: 1035 (61%); 1.1002: 1357 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 11 | 2: 1412 (83%); 4: 1063 (63%); 7: 688 (41%); 11: 363 (21%) | 2: 468 (28%); 4: 772 (46%); 7: 1098 (65%); 11: 1384 (82%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0855, -0.0536, -0.0337, -0.0165 | -0.0855: 1357 (80%); -0.0536: 1017 (60%); -0.0337: 679 (40%); -0.0165: 342 (20%) | -0.0855: 339 (20%); -0.0536: 679 (40%); -0.0337: 1017 (60%); -0.0165: 1354 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0991, -0.0578, -0.0296, -0.0046 | -0.0991: 1357 (80%); -0.0578: 1017 (60%); -0.0296: 679 (40%); -0.0046: 340 (20%) | -0.0991: 339 (20%); -0.0578: 679 (40%); -0.0296: 1017 (60%); -0.0046: 1356 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0586, -0.0338, -0.0182, -0.0024 | -0.0586: 1356 (80%); -0.0338: 1021 (60%); -0.0182: 680 (40%); -0.0024: 340 (20%) | -0.0586: 340 (20%); -0.0338: 676 (40%); -0.0182: 1016 (60%); -0.0024: 1356 (80%) | OFFLINE |
| pct_from_avwap_20high | backtest/signals/screener.py | 99.9% | -6.0268, -3.7328, -2.5354, -1.5976 | -6.0268: 1355 (80%); -3.7328: 1016 (60%); -2.5354: 678 (40%); -1.5976: 339 (20%) | -6.0268: 339 (20%); -3.7328: 678 (40%); -2.5354: 1016 (60%); -1.5976: 1355 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -11.27, 0.52, 11.866, 31.242 | -11.27: 1357 (80%); 0.52: 1018 (60%); 11.866: 679 (40%); 31.242: 340 (20%) | -11.27: 340 (20%); 0.52: 679 (40%); 11.866: 1018 (60%); 31.242: 1357 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0359, 0.0487, 0.064, 0.089 | 0.0359: 1359 (80%); 0.0487: 1018 (60%); 0.064: 681 (40%); 0.089: 340 (20%) | 0.0359: 340 (20%); 0.0487: 680 (40%); 0.064: 1018 (60%); 0.089: 1358 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.0855, 0.1863, 0.3232, 0.4865 | 0.0855: 1357 (80%); 0.1863: 1019 (60%); 0.3232: 679 (40%); 0.4865: 340 (20%) | 0.0855: 340 (20%); 0.1863: 679 (40%); 0.3232: 1018 (60%); 0.4865: 1357 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.957, -0.867, -0.0744, 0.635 | -1.957: 1357 (80%); -0.867: 1018 (60%); -0.0744: 679 (40%); 0.635: 340 (20%) | -1.957: 340 (20%); -0.867: 679 (40%); -0.0744: 1018 (60%); 0.635: 1357 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.9713, -0.6465, -0.4227, -0.2372 | -0.9713: 1357 (80%); -0.6465: 1018 (60%); -0.4227: 679 (40%); -0.2372: 341 (20%) | -0.9713: 340 (20%); -0.6465: 679 (40%); -0.4227: 1018 (60%); -0.2372: 1357 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.376, -0.3407, 0.4644, 1.2135 | -1.376: 1357 (80%); -0.3407: 1018 (60%); 0.4644: 679 (40%); 1.2135: 340 (20%) | -1.376: 340 (20%); -0.3407: 679 (40%); 0.4644: 1018 (60%); 1.2135: 1357 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -9.213, -5.728, -3.693, -1.853 | -9.213: 1357 (80%); -5.728: 1018 (60%); -3.693: 679 (40%); -1.853: 341 (20%) | -9.213: 340 (20%); -5.728: 679 (40%); -3.693: 1018 (60%); -1.853: 1357 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 4.41, 10.08, 18.35, 32.62 | 4.41: 1357 (80%); 10.08: 1018 (60%); 18.35: 679 (40%); 32.62: 340 (20%) | 4.41: 340 (20%); 10.08: 679 (40%); 18.35: 1018 (60%); 32.62: 1357 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 39.02, 43.58, 47.37, 50.18 | 39.02: 1357 (80%); 43.58: 1019 (60%); 47.37: 679 (40%); 50.18: 341 (20%) | 39.02: 340 (20%); 43.58: 679 (40%); 47.37: 1018 (60%); 50.18: 1357 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 28.7, 35.14, 39.39, 43.15 | 28.7: 1358 (80%); 35.14: 1018 (60%); 39.39: 679 (40%); 43.15: 342 (20%) | 28.7: 341 (20%); 35.14: 679 (40%); 39.39: 1018 (60%); 43.15: 1357 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 1693 (100%) | 0: 1696 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0321, 0.0458, 0.0582, 0.0863 | 0.0321: 1358 (80%); 0.0458: 1020 (60%); 0.0582: 679 (40%); 0.0863: 350 (21%) | 0.0321: 345 (20%); 0.0458: 682 (40%); 0.0582: 1019 (60%); 0.0863: 1357 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0757, -0.056, -0.0429, -0.0315 | -0.0757: 1357 (80%); -0.056: 1021 (60%); -0.0429: 688 (41%); -0.0315: 341 (20%) | -0.0757: 340 (20%); -0.056: 682 (40%); -0.0429: 1030 (61%); -0.0315: 1362 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 1696 (100%); 2: 427 (25%) | 0: 1064 (63%); 2: 1384 (82%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.4% | 30, 45, 60, 68 | 30: 1353 (80%); 45: 1077 (64%); 60: 686 (40%); 68: 365 (22%) | 30: 358 (21%); 45: 679 (40%); 60: 1065 (63%); 68: 1362 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.8% | 0.0111, 0.0155, 0.0221, 0.0334 | 0.0111: 1342 (79%); 0.0155: 1010 (60%); 0.0221: 667 (39%); 0.0334: 335 (20%) | 0.0111: 335 (20%); 0.0155: 666 (39%); 0.0221: 1009 (59%); 0.0334: 1341 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 99.9% | 0.1085, 0.2768, 0.4705, 0.5973 | 0.1085: 1355 (80%); 0.2768: 1016 (60%); 0.4705: 678 (40%); 0.5973: 340 (20%) | 0.1085: 339 (20%); 0.2768: 678 (40%); 0.4705: 1016 (60%); 0.5973: 1355 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 99.9% | 30.3, 52.9, 79.56, 127.52 | 30.3: 1356 (80%); 52.9: 1017 (60%); 79.56: 678 (40%); 127.52: 339 (20%) | 30.3: 340 (20%); 52.9: 680 (40%); 79.56: 1016 (60%); 127.52: 1355 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -9.3813, -4.605, -2.525, -1.1975 | -9.3813: 1357 (80%); -4.605: 1018 (60%); -2.525: 679 (40%); -1.1975: 340 (20%) | -9.3813: 340 (20%); -4.605: 679 (40%); -2.525: 1018 (60%); -1.1975: 1358 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 14.14, 22.05, 31.16, 44.88 | 14.14: 1357 (80%); 22.05: 1018 (60%); 31.16: 679 (40%); 44.88: 340 (20%) | 14.14: 340 (20%); 22.05: 679 (40%); 31.16: 1018 (60%); 44.88: 1357 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 11.34, 19.17, 28.2, 39.72 | 11.34: 1357 (80%); 19.17: 1018 (60%); 28.2: 679 (40%); 39.72: 340 (20%) | 11.34: 340 (20%); 19.17: 679 (40%); 28.2: 1018 (60%); 39.72: 1357 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 1.82, 10.25, 23.61, 45.88 | 1.82: 1358 (80%); 10.25: 1018 (60%); 23.61: 679 (40%); 45.88: 340 (20%) | 1.82: 341 (20%); 10.25: 680 (40%); 23.61: 1018 (60%); 45.88: 1357 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 13.25, 41.02 | 0: 1696 (100%); 13.25: 679 (40%); 41.02: 340 (20%) | 0: 701 (41%); 13.25: 1018 (60%); 41.02: 1357 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 8, 12, 17 | 4: 1448 (85%); 8: 1058 (62%); 12: 753 (44%); 17: 375 (22%) | 4: 356 (21%); 8: 717 (42%); 12: 1032 (61%); 17: 1393 (82%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 14, 18 | 5: 1381 (81%); 10: 1033 (61%); 14: 728 (43%); 18: 360 (21%) | 5: 378 (22%); 10: 753 (44%); 14: 1049 (62%); 18: 1442 (85%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 37.51, 41.3, 45.22, 49.74 | 37.51: 1357 (80%); 41.3: 1018 (60%); 45.22: 680 (40%); 49.74: 341 (20%) | 37.51: 340 (20%); 41.3: 680 (40%); 45.22: 1018 (60%); 49.74: 1357 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1944, 0.4325, 0.7143, 0.9206 | 0.1944: 1360 (80%); 0.4325: 1020 (60%); 0.7143: 681 (40%); 0.9206: 340 (20%) | 0.1944: 342 (20%); 0.4325: 679 (40%); 0.7143: 1021 (60%); 0.9206: 1365 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.29, 17.36, 20.64, 26.21 | 15.29: 1358 (80%); 17.36: 1018 (60%); 20.64: 679 (40%); 26.21: 341 (20%) | 15.29: 341 (20%); 17.36: 679 (40%); 20.64: 1019 (60%); 26.21: 1370 (81%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 15.29, 17.36, 20.64, 26.21 | 15.29: 1358 (80%); 17.36: 1018 (60%); 20.64: 679 (40%); 26.21: 341 (20%) | 15.29: 341 (20%); 17.36: 679 (40%); 20.64: 1019 (60%); 26.21: 1370 (81%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.864, 0.9001, 0.9389, 0.9791 | 0.864: 1360 (80%); 0.9001: 1019 (60%); 0.9389: 680 (40%); 0.9791: 343 (20%) | 0.864: 344 (20%); 0.9001: 680 (40%); 0.9389: 1018 (60%); 0.9791: 1357 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.71, 0.86, 1.01, 1.28 | 0.71: 1360 (80%); 0.86: 1021 (60%); 1.01: 694 (41%); 1.28: 343 (20%) | 0.71: 355 (21%); 0.86: 695 (41%); 1.01: 1020 (60%); 1.28: 1360 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0121, 0.0293, 0.0533, 0.1001 | 0.0121: 1359 (80%); 0.0293: 1018 (60%); 0.0533: 679 (40%); 0.1001: 340 (20%) | 0.0121: 342 (20%); 0.0293: 683 (40%); 0.0533: 1018 (60%); 0.1001: 1358 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 49.111, 78.5255, 123.9594, 209.0372 | 49.111: 1357 (80%); 78.5255: 1018 (60%); 123.9594: 679 (40%); 209.0372: 340 (20%) | 49.111: 340 (20%); 78.5255: 679 (40%); 123.9594: 1018 (60%); 209.0372: 1357 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 46.6231, 75.6208, 118.2974, 201.6201 | 46.6231: 1357 (80%); 75.6208: 1018 (60%); 118.2974: 679 (40%); 201.6201: 340 (20%) | 46.6231: 340 (20%); 75.6208: 679 (40%); 118.2974: 1018 (60%); 201.6201: 1357 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 44.7335, 72.7025, 112.5792, 194.1231 | 44.7335: 1357 (80%); 72.7025: 1018 (60%); 112.5792: 679 (40%); 194.1231: 340 (20%) | 44.7335: 340 (20%); 72.7025: 679 (40%); 112.5792: 1018 (60%); 194.1231: 1357 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1696 (100%) | 0: 1504 (89%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1696 (100%) | 0: 1567 (92%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 99.9% | -0.0957, -0.0587, -0.0331, -0.011 | -0.0957: 1355 (80%); -0.0587: 1017 (60%); -0.0331: 684 (40%); -0.011: 339 (20%) | -0.0957: 339 (20%); -0.0587: 678 (40%); -0.0331: 1017 (60%); -0.011: 1355 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -94.01, -88.44, -80.56, -69.31 | -94.01: 1357 (80%); -88.44: 1019 (60%); -80.56: 679 (40%); -69.31: 341 (20%) | -94.01: 340 (20%); -88.44: 679 (40%); -80.56: 1018 (60%); -69.31: 1357 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.6% | 0.4966, 0.7804, 1.0168, 1.2986 | 0.4966: 1351 (80%); 0.7804: 1013 (60%); 1.0168: 676 (40%); 1.2986: 338 (20%) | 0.4966: 338 (20%); 0.7804: 676 (40%); 1.0168: 1013 (60%); 1.2986: 1351 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.6% | 3, 5, 7, 9 | 3: 1369 (81%); 5: 1061 (63%); 7: 737 (43%); 9: 408 (24%) | 3: 457 (27%); 5: 797 (47%); 7: 1106 (65%); 9: 1469 (87%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.5% | 0.1821, 0.2172, 0.2616, 0.3318 | 0.1821: 1350 (80%); 0.2172: 1012 (60%); 0.2616: 676 (40%); 0.3318: 338 (20%) | 0.1821: 338 (20%); 0.2172: 675 (40%); 0.2616: 1013 (60%); 0.3318: 1350 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.5% | 3, 5, 7, 9 | 3: 1356 (80%); 5: 1043 (61%); 7: 714 (42%); 9: 371 (22%) | 3: 486 (29%); 5: 814 (48%); 7: 1134 (67%); 9: 1493 (88%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.5% | 0.0181, 0.0248, 0.0328, 0.0457 | 0.0181: 1354 (80%); 0.0248: 1013 (60%); 0.0328: 677 (40%); 0.0457: 338 (20%) | 0.0181: 338 (20%); 0.0248: 675 (40%); 0.0328: 1019 (60%); 0.0457: 1350 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.5% | 2, 4, 6, 8 | 2: 1436 (85%); 4: 1074 (63%); 6: 759 (45%); 8: 441 (26%) | 2: 448 (26%); 4: 780 (46%); 6: 1090 (64%); 8: 1411 (83%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.8% | -0.0851, 0.056, 0.1873, 0.3659 | -0.0851: 1353 (80%); 0.056: 1015 (60%); 0.1873: 677 (40%); 0.3659: 339 (20%) | -0.0851: 339 (20%); 0.056: 677 (40%); 0.1873: 1015 (60%); 0.3659: 1353 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.8% | 4, 6, 8, 9 | 4: 1355 (80%); 6: 1040 (61%); 8: 715 (42%); 9: 504 (30%) | 4: 479 (28%); 6: 814 (48%); 8: 1188 (70%); 9: 1416 (83%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 8.0% |
| 8k_item_5_02_filed_within_7d | 3.0% |
| above_avwap_20high | 2.2% |
| above_avwap_20low | 25.9% |
| above_avwap_252low | 68.4% |
| above_avwap_50low | 37.2% |
| above_cpr | 1.2% |
| above_prev_low | 52.5% |
| above_vwap | 60.9% |
| above_wood_p | 7.5% |
| ad_rising | 30.1% |
| adx_cross_up | 2.9% |
| adx_cross_up_20 | 1.7% |
| adx_di_bear | 87.9% |
| adx_di_bull | 12.1% |
| adx_strong | 3.1% |
| adx_trending | 35.4% |
| ao_cross_dn | 5.1% |
| ao_cross_up | 0.2% |
| ao_positive | 30.1% |
| ao_twin_peaks_bull | 5.0% |
| at_key_fib | 22.1% |
| at_key_fib_wide | 50.3% |
| avwap_20high_loss_recent_3d | 18.9% |
| avwap_20high_reclaim_recent_3d | 1.2% |
| avwap_20low_loss_recent_3d | 53.9% |
| avwap_20low_reclaim_recent_3d | 5.9% |
| avwap_252low_loss_recent_3d | 11.6% |
| avwap_252low_reclaim_recent_3d | 1.9% |
| avwap_50low_loss_recent_3d | 35.5% |
| avwap_50low_reclaim_recent_3d | 4.8% |
| bb_10_20_above_mid | 8.3% |
| bb_10_20_expanding | 58.1% |
| bb_10_20_pctb_gt_75 | 0.3% |
| bb_10_20_pctb_lt_05 | 18.8% |
| bb_10_20_pctb_lt_1 | 29.1% |
| bb_10_20_pctb_lt_15 | 41.3% |
| bb_10_20_pctb_lt_2 | 54.3% |
| bb_10_20_pctb_lt_25 | 63.0% |
| bb_10_20_reclaim_from_lower_recent_3d | 11.9% |
| bb_10_20_reclaim_from_upper_recent_3d | 0.5% |
| bb_10_20_squeeze | 48.7% |
| bb_10_20_touch_lower | 23.1% |
| bb_10_20_touch_upper | 0.1% |
| bb_20_15_above_mid | 0.2% |
| bb_20_15_expanding | 62.6% |
| bb_20_15_pctb_lt_05 | 46.5% |
| bb_20_15_pctb_lt_1 | 55.2% |
| bb_20_15_pctb_lt_15 | 62.9% |
| bb_20_15_pctb_lt_2 | 72.1% |
| bb_20_15_pctb_lt_25 | 80.0% |
| bb_20_15_reclaim_from_lower_recent_3d | 12.2% |
| bb_20_15_reclaim_from_upper_recent_3d | 2.2% |
| bb_20_15_squeeze | 47.0% |
| bb_20_15_touch_lower | 50.3% |
| bb_20_20_above_mid | 0.2% |
| bb_20_20_expanding | 62.6% |
| bb_20_20_pctb_lt_05 | 24.5% |
| bb_20_20_pctb_lt_1 | 32.7% |
| bb_20_20_pctb_lt_15 | 43.3% |
| bb_20_20_pctb_lt_2 | 55.2% |
| bb_20_20_pctb_lt_25 | 65.6% |
| bb_20_20_reclaim_from_lower_recent_3d | 7.8% |
| bb_20_20_reclaim_from_upper_recent_3d | 0.2% |
| bb_20_20_squeeze | 27.9% |
| bb_20_20_touch_lower | 25.1% |
| bearish_engulfing | 13.7% |
| bearish_pin_bar | 3.7% |
| below_avwap_20high | 97.8% |
| below_avwap_20low | 74.1% |
| below_avwap_252low | 31.6% |
| below_avwap_50low | 62.8% |
| below_cam_s3 | 69.3% |
| below_cam_s4 | 41.2% |
| below_ema_20 | 99.9% |
| below_ema_200 | 43.0% |
| below_ema_200_break_recent_5d | 14.4% |
| below_ema_20_break_recent_5d | 48.5% |
| below_ema_21 | 99.9% |
| below_ema_21_break_recent_5d | 49.0% |
| below_ema_50 | 70.0% |
| below_ema_50_break_recent_5d | 26.2% |
| below_ema_9 | 97.2% |
| below_ema_9_break_recent_5d | 54.0% |
| below_prev_low | 47.1% |
| below_prev_low_clearance_atr_05 | 18.1% |
| below_s1 | 45.8% |
| below_s2 | 23.6% |
| below_sma_20 | 99.8% |
| below_sma_200 | 40.1% |
| below_sma_21 | 99.6% |
| below_sma_50 | 69.3% |
| below_sma_9 | 89.9% |
| below_vwap | 39.1% |
| blowoff_recent_3d | 0.4% |
| break_52w_low | 1.7% |
| bullish_pin_bar | 6.8% |
| ceo_buy | 0.4% |
| cfo_buy | 0.1% |
| chandelier_long_bullish | 27.4% |
| chandelier_long_flip_dn | 16.8% |
| chandelier_short_bearish | 97.5% |
| close_in_bottom_40pct_of_range | 70.2% |
| close_in_top_40pct_of_range | 10.1% |
| cluster_buy | 0.2% |
| cmf_cross_dn | 11.6% |
| cmf_cross_up | 1.5% |
| cmf_negative | 63.4% |
| cmf_positive | 36.6% |
| concentrated_sell | 6.8% |
| cup_handle_detected | 17.2% |
| cup_handle_neckline_break_retest_long | 0.1% |
| dc10_breakout_dn | 28.5% |
| dc10_breakout_dn_1pct | 49.2% |
| dc10_breakout_up_1pct | 0.1% |
| dc10_new_high | 0.5% |
| dc10_strong_breakout_dn | 9.8% |
| dc20_breakout_dn | 18.0% |
| dc20_new_high | 0.1% |
| dc20_support_break_retest_strong | 30.2% |
| defensive_leadership | 59.0% |
| director_only_buy | 2.5% |
| doji | 3.9% |
| double_bottom_detected | 15.9% |
| double_top_detected | 21.0% |
| dpi_elevated | 45.8% |
| drying_volume_on_down_turn | 58.5% |
| ema_20_50_bearish | 41.0% |
| ema_20_50_bullish | 59.0% |
| ema_20_50_death_cross | 3.3% |
| ema_50_200_bearish | 28.0% |
| ema_50_200_bullish | 72.0% |
| ema_50_200_death_cross | 0.4% |
| ema_9_21_bearish | 73.1% |
| ema_9_21_bullish | 26.9% |
| ema_9_21_death_cross | 7.3% |
| evening_star | 16.5% |
| flag_bear_break_retest_short | 0.5% |
| flag_bear_broke | 0.6% |
| flag_bear_detected | 0.3% |
| flag_bull_break_retest_long | 0.1% |
| flag_bull_broke | 0.1% |
| flag_bull_detected | 0.2% |
| force_index_cross_dn | 9.5% |
| force_index_positive | 4.0% |
| gap_dn_1_5pct | 8.4% |
| gap_dn_2pct | 5.9% |
| gap_up_1_5pct | 4.5% |
| gap_up_2pct | 3.7% |
| hammer | 5.7% |
| head_shoulders_bottom_detected | 2.9% |
| head_shoulders_top_detected | 5.5% |
| house_cluster_buy | 3.4% |
| house_cluster_sell | 3.4% |
| htf_aligned_bear | 33.0% |
| htf_aligned_bull | 23.8% |
| htf_disagreement | 4.4% |
| hull_bearish | 84.8% |
| hull_bullish | 15.2% |
| hull_flip_dn | 7.3% |
| hull_flip_up | 2.9% |
| ichi_above_cloud | 36.3% |
| ichi_above_cloud_break_recent_5d | 1.9% |
| ichi_below_cloud | 43.4% |
| ichi_below_cloud_break_recent_5d | 16.8% |
| ichi_cloud_thick | 86.6% |
| ichi_tk_bearish | 65.6% |
| ichi_tk_bullish | 29.1% |
| ichi_tk_cross_dn | 5.5% |
| ichi_tk_cross_up | 0.5% |
| ichi_weekly_above_cloud | 50.7% |
| ichi_weekly_below_cloud | 24.8% |
| ichi_weekly_in_cloud | 24.5% |
| in_reversal_window | 1.7% |
| inside_bar | 15.3% |
| inside_kc | 81.4% |
| insider_cluster_active | 15.2% |
| institutional_buy | 89.6% |
| institutional_negative | 4.7% |
| institutional_persistence_growing | 43.0% |
| institutional_persistence_strong | 60.1% |
| institutional_strong_buy | 79.8% |
| inverted_cup_handle_detected | 10.3% |
| is_friday | 17.3% |
| is_halloween_period | 56.0% |
| is_halloween_period_first_day | 0.3% |
| is_january | 10.7% |
| is_january_extended | 14.9% |
| is_monday | 16.1% |
| is_pre_holiday | 3.1% |
| is_summer_period | 44.0% |
| is_totm_window | 33.2% |
| is_totm_window_first_day | 9.6% |
| is_week_open | 19.5% |
| kc_touch_lower | 22.8% |
| large_dollar_buy | 0.7% |
| macd_12_26_9_crossover_dn | 6.2% |
| macd_8_21_5_bearish | 83.6% |
| macd_8_21_5_bullish | 16.4% |
| macd_8_21_5_crossover_dn | 3.8% |
| macd_8_21_5_crossover_up | 1.7% |
| marubozu_bear | 1.4% |
| mfi_broad_overbought | 0.6% |
| mfi_broad_oversold | 20.2% |
| mfi_oversold | 5.7% |
| monthly_above_sma_12 | 59.7% |
| monthly_above_sma_6 | 49.6% |
| monthly_bias_bear | 34.5% |
| monthly_bias_bull | 43.8% |
| monthly_momentum_pos | 59.8% |
| near_52w_high | 0.1% |
| near_52w_high_95pct | 6.0% |
| near_52w_low | 4.0% |
| near_52w_low_105pct | 8.0% |
| near_52w_low_retest_short | 0.8% |
| near_avwap_20high_atr_05x | 12.6% |
| near_avwap_20high_atr_10x | 36.5% |
| near_avwap_20high_atr_15x | 64.9% |
| near_avwap_20high_atr_20x | 82.8% |
| near_avwap_20low_atr_05x | 62.2% |
| near_avwap_20low_atr_10x | 87.1% |
| near_avwap_20low_atr_15x | 96.5% |
| near_avwap_20low_atr_20x | 99.3% |
| near_avwap_252low_atr_05x | 14.0% |
| near_avwap_252low_atr_10x | 26.2% |
| near_avwap_252low_atr_15x | 35.3% |
| near_avwap_252low_atr_20x | 44.9% |
| near_avwap_50low_atr_05x | 46.5% |
| near_avwap_50low_atr_10x | 71.8% |
| near_avwap_50low_atr_15x | 85.1% |
| near_avwap_50low_atr_20x | 93.1% |
| near_cam_r3 | 0.2% |
| near_cam_s3 | 32.9% |
| near_cam_s4 | 22.1% |
| near_fib_236 | 2.4% |
| near_fib_382 | 7.8% |
| near_fib_500 | 8.5% |
| near_fib_618 | 5.9% |
| near_fib_786 | 6.5% |
| near_pivot | 14.9% |
| near_prev_close | 14.3% |
| near_prev_high | 0.1% |
| near_prev_low | 24.4% |
| near_r1 | 0.1% |
| near_r1_wide | 28.7% |
| near_r2_wide | 6.4% |
| near_s1 | 24.4% |
| near_s1_wide | 78.0% |
| near_s2 | 9.4% |
| near_s2_wide | 58.0% |
| near_s3 | 5.2% |
| near_wood_r1 | 1.3% |
| near_wood_s1 | 20.4% |
| news_uses_polygon_score | 23.6% |
| obv_bearish | 85.8% |
| obv_bullish | 14.2% |
| obv_diverge_bull | 8.0% |
| obv_falling | 80.1% |
| obv_rising | 19.9% |
| outside_bar | 12.8% |
| pead_negative_surprise | 12.2% |
| pead_positive_surprise | 24.7% |
| pin_bar | 10.6% |
| po3_accumulation_active | 42.1% |
| po3_bearish | 18.8% |
| po3_manipulation_sweep_down | 20.9% |
| po3_manipulation_sweep_up | 1.6% |
| po3_mmsm_setup | 1.6% |
| po3_sweep_above_prior_high | 26.2% |
| po3_sweep_below_prior_low | 80.1% |
| ppo_crossover_dn | 5.8% |
| pre_fomc_d0 | 3.8% |
| pre_fomc_d1 | 3.2% |
| pre_fomc_window | 7.0% |
| price_above_dema | 7.0% |
| price_above_ema_20 | 0.1% |
| price_above_ema_200 | 57.0% |
| price_above_ema_200_break_recent_5d | 3.0% |
| price_above_ema_20_break_recent_5d | 0.1% |
| price_above_ema_21 | 0.1% |
| price_above_ema_21_break_recent_5d | 0.1% |
| price_above_ema_50 | 30.0% |
| price_above_ema_50_break_recent_5d | 4.7% |
| price_above_ema_9 | 2.8% |
| price_above_ema_9_break_recent_5d | 2.8% |
| price_above_hull | 27.9% |
| price_above_sma_200 | 59.9% |
| price_above_sma_21 | 0.4% |
| price_above_sma_50 | 30.7% |
| price_above_tema | 25.4% |
| price_below_dema | 93.0% |
| price_below_hull | 72.1% |
| price_below_tema | 74.6% |
| psar_bullish | 13.6% |
| psar_flip_dn | 5.1% |
| psar_flip_up | 1.1% |
| r1_break_retest_long | 17.2% |
| recent_capitulation_at_s3 | 0.3% |
| risk_off_regime_bond_signal | 24.8% |
| risk_off_regime_bond_signal_strong | 11.6% |
| risk_off_regime_gold_signal | 41.5% |
| risk_on_regime_bond_signal | 40.3% |
| risk_on_regime_bond_signal_strong | 16.9% |
| roc_positive | 5.8% |
| roc_turning_dn | 11.3% |
| roc_turning_up | 1.5% |
| rsi_14_cross_dn_overbought_recent_3d | 1.1% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.2% |
| rsi_14_cross_up_oversold_recent_3d | 2.2% |
| rsi_14_extreme_os | 0.9% |
| rsi_14_oversold | 10.1% |
| rsi_14_rising | 1.6% |
| rsi_21_bullish | 21.1% |
| rsi_21_cross_dn_overbought_recent_3d | 0.4% |
| rsi_21_cross_up_oversold_recent_3d | 0.9% |
| rsi_21_extreme_os | 0.2% |
| rsi_21_oversold | 3.4% |
| rsi_21_rising | 1.5% |
| rsi_2_bullish | 6.7% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 21.6% |
| rsi_2_cross_dn_overbought_recent_3d | 35.9% |
| rsi_2_cross_up_extreme_os_recent_3d | 15.7% |
| rsi_2_cross_up_oversold_recent_3d | 12.5% |
| rsi_2_extreme_ob | 0.2% |
| rsi_2_extreme_os | 63.0% |
| rsi_2_overbought | 0.8% |
| rsi_2_oversold | 77.7% |
| rsi_2_rising | 1.5% |
| rsi_9_bullish | 0.4% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 0.1% |
| rsi_9_cross_dn_overbought_recent_3d | 2.5% |
| rsi_9_cross_up_extreme_os_recent_3d | 1.6% |
| rsi_9_cross_up_oversold_recent_3d | 5.8% |
| rsi_9_extreme_os | 4.9% |
| rsi_9_oversold | 23.4% |
| rsi_9_rising | 1.5% |
| s1_break_retest_short | 88.9% |
| sc_13d_filed_within_30d | 4.4% |
| sc_13g_filed_within_30d | 3.3% |
| sector_outperforming_spy | 33.3% |
| sector_underperforming_spy | 66.7% |
| shooting_star | 4.1% |
| sma_20_50_bullish | 61.2% |
| sma_20_50_golden_cross | 0.3% |
| sma_50_200_bullish | 72.9% |
| sma_50_200_golden_cross | 0.4% |
| sma_9_21_bullish | 23.6% |
| sma_9_21_golden_cross | 0.5% |
| smc_bos_bearish | 5.4% |
| smc_bos_bullish | 16.9% |
| smc_bos_retest_long | 5.7% |
| smc_bos_retest_short | 3.7% |
| smc_breaker_block_bearish | 9.3% |
| smc_breaker_block_bullish | 26.9% |
| smc_choch_bearish | 4.5% |
| smc_choch_bullish | 3.2% |
| smc_equal_highs_swept | 3.8% |
| smc_equal_lows_swept | 2.5% |
| smc_fvg_bearish_active | 52.8% |
| smc_fvg_bullish_active | 18.8% |
| smc_fvg_retest_long_zone | 6.4% |
| smc_fvg_retest_short_zone | 0.4% |
| smc_in_discount_zone | 80.6% |
| smc_in_premium_zone | 48.2% |
| smc_inverse_fvg_bearish | 98.1% |
| smc_inverse_fvg_bullish | 71.7% |
| smc_liquidity_swept_dn | 2.2% |
| smc_liquidity_swept_up | 0.5% |
| smc_mitigation_block_long | 3.2% |
| smc_mitigation_block_short | 0.1% |
| smc_ob_bearish_active | 21.9% |
| smc_ob_bullish_active | 43.5% |
| smc_ote_long_zone | 7.0% |
| smc_ote_short_zone | 8.4% |
| squeeze_fire_dn | 6.1% |
| squeeze_fire_up | 0.1% |
| squeeze_in | 28.4% |
| squeeze_positive | 3.6% |
| stoch_bearish_cross | 14.5% |
| stoch_broad_overbought | 0.1% |
| stoch_broad_oversold | 52.6% |
| stoch_bullish_cross | 6.3% |
| stoch_oversold | 42.3% |
| stochrsi_cross_dn | 15.9% |
| stochrsi_cross_up | 21.5% |
| stochrsi_overbought | 5.5% |
| stochrsi_oversold | 66.3% |
| supertrend_bearish | 3.8% |
| supertrend_bullish | 96.2% |
| supertrend_flip_dn | 2.2% |
| supertrend_flip_recent_long_5d | 3.9% |
| supertrend_flip_recent_short_5d | 4.9% |
| supertrend_flip_up | 1.0% |
| support_break_retest | 43.8% |
| tema_above_dema | 8.1% |
| tema_cross_dn | 5.5% |
| tema_cross_up | 0.1% |
| three_black_crows | 15.4% |
| triangle_apex_break_retest_long | 3.9% |
| triangle_ascending_detected | 10.7% |
| triangle_descending_detected | 12.5% |
| uo_oversold | 3.7% |
| usd_strengthening | 31.0% |
| usd_weakening | 8.7% |
| vix_band_high | 46.7% |
| vix_band_low | 30.8% |
| vix_band_mid | 22.5% |
| vix_term_backwardation | 13.5% |
| vix_term_contango | 86.5% |
| vol_above_avg | 41.5% |
| vol_below_avg | 58.5% |
| vol_spike_12x | 23.6% |
| vol_spike_15x | 11.6% |
| vol_spike_17x | 7.9% |
| vol_spike_2x | 4.6% |
| vol_spike_2x_on_down_day_recent_3d | 5.2% |
| vol_spike_2x_on_up_day_recent_3d | 2.1% |
| vol_spike_3x | 1.6% |
| vp_above_value_area | 2.3% |
| vp_below_value_area | 29.2% |
| vp_close_above_poc | 27.4% |
| vp_close_below_poc | 72.6% |
| vp_in_value_area | 68.5% |
| week_open_gap_down_15pct | 1.8% |
| week_open_gap_up_15pct | 0.3% |
| weekly_above_ema_10 | 27.4% |
| weekly_above_ema_20 | 45.5% |
| weekly_bias_bear | 53.8% |
| weekly_bias_bull | 26.7% |
| weekly_momentum_pos | 11.9% |
| williams_r_oversold | 61.1% |
| williams_r_rising | 11.1% |
| within_pead_window | 36.5% |
| within_post_deletion_window | 5.1% |
| within_post_inclusion_window | 2.1% |
| within_pre_rebalance_window | 0.8% |
| xs_avoid_high_ivol | 78.0% |
| xs_avoid_high_max | 83.6% |
| xs_high_beta_decile | 24.2% |
| xs_low_beta_bottom_quintile | 24.2% |
| xs_low_beta_decile | 18.9% |
| xs_low_beta_decile_entry_recent_5d | 0.8% |
| xs_low_beta_top_quintile | 18.9% |
| xs_momentum_bottom_decile | 3.6% |
| xs_momentum_bottom_quintile | 12.1% |
| xs_momentum_top_decile | 16.3% |
| xs_momentum_top_quintile | 29.8% |
| xs_quality_bottom_quintile | 19.3% |
| xs_quality_top_quintile | 19.0% |
| xs_quality_top_tercile | 40.0% |
| year_low_break_retest_short | 2.7% |
| yoy_surprise_high | 58.0% |
| yoy_surprise_negative | 30.4% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.1% |
| committed_growth_holders | 91.1% |
| corp_donations_1y | 8.7% |
| corp_donations_count_1y | 8.7% |
| corp_donations_unique_pacs | 8.7% |
| cot_rut_commercials_pctile_3y | 59.2% |
| cot_rut_mmoney_pctile_3y | 59.2% |
| cup_handle_depth_pct | 22.2% |
| days_since_deletion | 7.0% |
| days_since_inclusion | 14.2% |
| days_to_next_holiday | 63.4% |
| days_to_rebalance | 7.6% |
| dpi_30d_avg | 96.2% |
| dpi_recent | 96.2% |
| earnings_announcement_return | 92.3% |
| earnings_eps_yoy_growth | 95.5% |
| flag_bear_pole_move_pct | 0.3% |
| flag_bull_pole_move_pct | 0.2% |
| gov_contracts_4q_sum | 39.6% |
| gov_contracts_last_qtr_amount | 39.6% |
| gov_contracts_qoq_growth | 39.6% |
| head_shoulders_magnitude_pct | 8.3% |
| insider_director_buyers_30d | 3.9% |
| insider_officer_buyers_30d | 3.9% |
| insider_total_shares_bought_30d | 3.9% |
| insider_unique_buyers_30d | 3.9% |
| inverted_cup_handle_height_pct | 16.0% |
| lobbying_amount_1y | 71.2% |
| lobbying_amount_q | 71.2% |
| lobbying_amount_yoy | 71.2% |
| monthly_momentum_6m | 97.8% |
| otc_short_ratio_recent | 96.2% |
| otc_volume_recent | 96.2% |
| pair_half_life | 91.6% |
| pair_max_abs_zscore | 91.6% |
| pair_zscore_signed | 91.6% |
| pct_from_avwap_20low | 71.7% |
| pct_from_avwap_252low | 95.8% |
| pct_from_avwap_50low | 88.6% |
| persistent_holders_4q | 91.1% |
| persistent_holders_8q | 91.1% |
| sc_13g_latest_percent_owned | 1.8% |
| search_volume_index_recent | 78.4% |
| search_volume_observations | 78.4% |
| search_volume_zscore_30d | 78.4% |
| sector_etf_return_20d | 2.5% |
| spy_return_20d | 2.5% |
| total_active_holders | 91.1% |
| triangle_breakdown_pct | 12.5% |
| triangle_breakout_pct | 10.7% |
| xs_quality_decile | 61.7% |
| xs_quality_gross_profitability | 61.7% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.998), `avwap_252low` (0.994), `avwap_50low` (0.998), `bb_10_20_lower` (0.997), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.998), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.998), `cam_r1` (0.998), `cam_r2` (0.998), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.998), `cam_s2` (0.998), `cam_s3` (0.998), `cam_s4` (0.998), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.998), `cpr_top` (0.998), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.999), `days_since_classification_change` (-1.0), `dc10_lower` (0.998), `dc10_mid` (1.0), `dc10_upper` (0.999), `dc20_lower` (0.998), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.998), `double_bottom_trough` (0.999), `double_top_neckline` (0.999), `double_top_peak` (0.999), `entry_stop_long` (0.996), `entry_stop_short` (0.999), `fib_236` (0.998), `fib_382` (0.999), `fib_500` (0.999), `fib_618` (0.999), `fib_786` (0.998), `fib_ext_127` (0.995), `fib_ext_162` (0.993), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.995), `head_shoulders_top_neckline` (0.998), `hull_ma` (0.998), `ichi_kijun` (1.0), `ichi_senkou_a` (0.996), `ichi_senkou_b` (0.994), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.998), `monthly_sma_12` (0.99), `monthly_sma_6` (0.997), `pivot` (0.998), `prev_close` (0.998), `prev_high` (0.999), `prev_low` (0.998), `psar_value` (0.999), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.998), `s2` (0.997), `s3` (0.997), `supertrend_value` (0.996), `swing_high` (0.997), `swing_low` (0.996), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.997), `vp_value_area_low` (0.996), `vwap_upper_1` (0.952), `vwap_upper_2` (0.954), `weekly_close` (0.998), `weekly_ema_10` (1.0), `weekly_ema_20` (0.998), `wood_p` (0.998), `wood_r1` (0.998), `wood_r2` (0.999), `wood_s1` (0.998), `wood_s2` (0.997), `year_high` (0.985), `year_low` (0.97)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | buffer pct (price below cpr_bottom by) | 2 | **FIRE-ADDING** | **YES** |
| P2.1 | width threshold (cpr_width < rng * X) | 3 | **FIRE-ADDING** | **YES** |
| P3.1 | span triple (fast, slow, signal) | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P4 | rsi_14 < 50 | 5 | subset-safe | no - derives offline |
| P5 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     2 x 3 x 1 x 5 x 1 = 30
offline gradings   5 level-combinations x 24 exits = 120
ENGINE RUNS        6 (every fire-adding axis sits at production-only until its env actuator exists)
check              6 x 5 = 30
```

B-row candidates NOT in this factorial: 578 census axes join it only when REGISTERED at the T3 band review.
