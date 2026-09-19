# Table A - cmf_flip

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit fa06ebf3e at 2026-09-19 13:06:49 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** mean_reversion | **status:** STALLED-CAMPAIGN | **R5 fires:** 2994 | **surviving fires (T1):** 2250 (survives_pct 0.7515)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  cmf_cross_dn  <- backtest/signals/screener.py +1
       DEFN: CMF crosses the zero line vs the prior bar (technical.py:1706-1707)
       knobs P1.1-P1.1 (band rows in Table A)
P2  cmf_cross_up  <- backtest/signals/screener.py +1
       DEFN: CMF crosses the zero line vs the prior bar (technical.py:1706-1707)
       knobs P2.1-P2.2 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  po3_accum_range_pct >= 0.0458   [EXISTING-THRESHOLD]
P4  rsi_14 < 50   [EXISTING-THRESHOLD]
P5  rsi_14 > 50   [EXISTING-THRESHOLD]
P6  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_cmf_flip (docstring and return dropped):

```python
fl = s.get('cmf_cross_up') and s.get('rsi_14', 50) < 50
fl = fl and s.get('po3_accum_range_pct', float('-inf')) >= 0.0458
fs = (s.get('cmf_cross_dn') and s.get('rsi_14', 50) > 50) and (not _short_borrow_trap_active(s))
fs = fs and s.get('po3_accum_range_pct', float('-inf')) >= 0.0458
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
| P1 | PRODUCER | cmf_cross_dn - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | CMF crosses the zero line vs the prior bar (technical.py:1706-1707) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | as cmf_cross_up, mirrored - backtest/signals/technical.py:1707 | mirror | 0.0 | 0, -0.02, -0.05 | level side on persisted cmf | freshness; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | cmf_cross_up - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | CMF crosses the zero line vs the prior bar (technical.py:1706-1707) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | cmf window - backtest/signals/technical.py:1695 | BRACKET production | 20 | 14, 20, 30 | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2.2 | BAND | cross level (zero line) - technical.py:1706 | BRACKET zero upward (require conviction, not a graze) | 0.0 | 0, 0.02, 0.05 | LEVEL side (cmf > 0.02/0.05) - persisted cmf; the FRESHNESS (prior bar <= level) needs the unpersisted prior cmf | freshness at any non-production level; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | STRATEGY | po3_accum_range_pct `>= 0.0458` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `>= 0.0458` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P4 | STRATEGY | rsi_14 `< 50` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `< 50` | production + 3 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P4.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | STRATEGY | rsi_14 `> 50` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `> 50` | production + 1 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P5.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P6 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | `>= 0.0458` | 100.0% | TIGHTER = RAISE the floor: 0.0561 -> 1801 (80%); 0.0693 -> 1351 (60%); 0.0867 -> 903 (40%); 0.1203 -> 452 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |
| rsi_14 | backtest/signals/screener.py | `< 50` | 100.0% | TIGHTER = LOWER the ceiling: 38.624 -> 450 (20%); 44.24 -> 901 (40%); 49.234 -> 1350 (60%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |
| rsi_14 | backtest/signals/screener.py | `> 50` | 100.0% | TIGHTER = RAISE the floor: 57.128 -> 450 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 17.06, 20.8, 25.26, 31.45 | 17.06: 1801 (80%); 20.8: 1352 (60%); 25.26: 901 (40%); 31.45: 451 (20%) | 17.06: 451 (20%); 20.8: 901 (40%); 25.26: 1353 (60%); 31.45: 1801 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 18.58, 23.836, 27.998, 32.552 | 18.58: 1801 (80%); 23.836: 1350 (60%); 27.998: 900 (40%); 32.552: 450 (20%) | 18.58: 451 (20%); 23.836: 900 (40%); 27.998: 1350 (60%); 32.552: 1800 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 15.418, 19.15, 23.2, 29.222 | 15.418: 1800 (80%); 19.15: 1351 (60%); 23.2: 901 (40%); 29.222: 450 (20%) | 15.418: 450 (20%); 19.15: 901 (40%); 23.2: 1351 (60%); 29.222: 1800 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -6.7975, -2.4169, -0.2414, 3.2321 | -6.7975: 1800 (80%); -2.4169: 1350 (60%); -0.2414: 900 (40%); 3.2321: 450 (20%) | -6.7975: 450 (20%); -2.4169: 900 (40%); -0.2414: 1350 (60%); 3.2321: 1800 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.2821, 2.3052, 3.851, 6.4616 | 1.2821: 1800 (80%); 2.3052: 1350 (60%); 3.851: 900 (40%); 6.4616: 450 (20%) | 1.2821: 450 (20%); 2.3052: 900 (40%); 3.851: 1350 (60%); 6.4616: 1800 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.2821, 2.3052, 3.851, 6.4616 | 1.2821: 1800 (80%); 2.3052: 1350 (60%); 3.851: 900 (40%); 6.4616: 450 (20%) | 1.2821: 450 (20%); 2.3052: 900 (40%); 3.851: 1350 (60%); 6.4616: 1800 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.4468, 2.925, 3.4654, 4.3052 | 2.4468: 1800 (80%); 2.925: 1351 (60%); 3.4654: 900 (40%); 4.3052: 450 (20%) | 2.4468: 450 (20%); 2.925: 901 (40%); 3.4654: 1350 (60%); 4.3052: 1800 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0688, 0.0935, 0.1239, 0.1748 | 0.0688: 1800 (80%); 0.0935: 1351 (60%); 0.1239: 900 (40%); 0.1748: 451 (20%) | 0.0688: 451 (20%); 0.0935: 902 (40%); 0.1239: 1350 (60%); 0.1748: 1800 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.2295, 0.3864, 0.5728, 0.7528 | 0.2295: 1801 (80%); 0.3864: 1350 (60%); 0.5728: 900 (40%); 0.7528: 451 (20%) | 0.2295: 451 (20%); 0.3864: 900 (40%); 0.5728: 1350 (60%); 0.7528: 1800 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0675, 0.0916, 0.1181, 0.1568 | 0.0675: 1802 (80%); 0.0916: 1350 (60%); 0.1181: 903 (40%); 0.1568: 452 (20%) | 0.0675: 451 (20%); 0.0916: 903 (40%); 0.1181: 1351 (60%); 0.1568: 1800 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.0636, 0.2898, 0.5399, 0.8273 | 0.0636: 1800 (80%); 0.2898: 1350 (60%); 0.5399: 900 (40%); 0.8273: 451 (20%) | 0.0636: 450 (20%); 0.2898: 900 (40%); 0.5399: 1350 (60%); 0.8273: 1800 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.09, 0.1221, 0.1575, 0.2091 | 0.09: 1802 (80%); 0.1221: 1351 (60%); 0.1575: 902 (40%); 0.2091: 451 (20%) | 0.09: 451 (20%); 0.1221: 901 (40%); 0.1575: 1352 (60%); 0.2091: 1800 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.1727, 0.3423, 0.53, 0.7455 | 0.1727: 1800 (80%); 0.3423: 1350 (60%); 0.53: 900 (40%); 0.7455: 451 (20%) | 0.1727: 451 (20%); 0.3423: 900 (40%); 0.53: 1350 (60%); 0.7455: 1801 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0437, -0.0174, 0.0054, 0.0333 | -0.0437: 1800 (80%); -0.0174: 1352 (60%); 0.0054: 901 (40%); 0.0333: 453 (20%) | -0.0437: 451 (20%); -0.0174: 903 (40%); 0.0054: 1351 (60%); 0.0333: 1801 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1437, 0.164, 0.2113, 0.2723 | 0.1437: 1802 (80%); 0.164: 1358 (60%); 0.2113: 900 (40%); 0.2723: 453 (20%) | 0.1437: 448 (20%); 0.164: 892 (40%); 0.2113: 1350 (60%); 0.2723: 1797 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 2250 (100%) | 0: 2127 (95%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0189, 0.0011, 0.0134, 0.0346 | -0.0189: 1801 (80%); 0.0011: 1355 (60%); 0.0134: 902 (40%); 0.0346: 452 (20%) | -0.0189: 451 (20%); 0.0011: 903 (40%); 0.0134: 1352 (60%); 0.0346: 1802 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 2250 (100%); 1: 887 (39%) | 0: 1363 (61%); 1: 1859 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2368, -0.1852, -0.1481, -0.1141 | -0.2368: 1808 (80%); -0.1852: 1375 (61%); -0.1481: 929 (41%); -0.1141: 491 (22%) | -0.2368: 453 (20%); -0.1852: 901 (40%); -0.1481: 1356 (60%); -0.1141: 1876 (83%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4167, 0.6282, 0.6987, 0.7692 | 0.4167: 1804 (80%); 0.6282: 1374 (61%); 0.6987: 920 (41%); 0.7692: 565 (25%) | 0.4167: 468 (21%); 0.6282: 920 (41%); 0.6987: 1354 (60%); 0.7692: 1817 (81%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2564, 0.3846, 0.5962, 0.8333 | 0.2564: 1828 (81%); 0.3846: 1360 (60%); 0.5962: 921 (41%); 0.8333: 480 (21%) | 0.2564: 463 (21%); 0.3846: 913 (41%); 0.5962: 1360 (60%); 0.8333: 1813 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.078, 0.0117, 0.0857, 0.2047 | -0.078: 1806 (80%); 0.0117: 1360 (60%); 0.0857: 912 (41%); 0.2047: 469 (21%) | -0.078: 455 (20%); 0.0117: 930 (41%); 0.0857: 1353 (60%); 0.2047: 1804 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3077, 0.4872, 0.6295, 0.7949 | 0.3077: 1816 (81%); 0.4872: 1352 (60%); 0.6295: 900 (40%); 0.7949: 466 (21%) | 0.3077: 451 (20%); 0.4872: 1018 (45%); 0.6295: 1350 (60%); 0.7949: 1804 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1474, 0.3205, 0.4679, 0.6282 | 0.1474: 1827 (81%); 0.3205: 1354 (60%); 0.4679: 901 (40%); 0.6282: 452 (20%) | 0.1474: 469 (21%); 0.3205: 908 (40%); 0.4679: 1382 (61%); 0.6282: 1813 (81%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5046, -0.3562, -0.1203, 0.0839 | -0.5046: 1804 (80%); -0.3562: 1352 (60%); -0.1203: 906 (40%); 0.0839: 456 (20%) | -0.5046: 460 (20%); -0.3562: 933 (41%); -0.1203: 1354 (60%); 0.0839: 1814 (81%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3269, 0.5128, 0.7436, 0.9167 | 0.3269: 1803 (80%); 0.5128: 1352 (60%); 0.7436: 911 (40%); 0.9167: 505 (22%) | 0.3269: 465 (21%); 0.5128: 915 (41%); 0.7436: 1360 (60%); 0.9167: 1835 (82%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1346, 0.3782, 0.5641, 0.8333 | 0.1346: 1821 (81%); 0.3782: 1372 (61%); 0.5641: 930 (41%); 0.8333: 454 (20%) | 0.1346: 465 (21%); 0.3782: 911 (40%); 0.5641: 1355 (60%); 0.8333: 1805 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0673, -0.0565, -0.0358, 0 | -0.0673: 1800 (80%); -0.0565: 1353 (60%); -0.0358: 912 (41%); 0: 683 (30%) | -0.0673: 450 (20%); -0.0565: 913 (41%); -0.0358: 1351 (60%); 0: 2198 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4423, 0.7372, 0.891, 1 | 0.4423: 1811 (80%); 0.7372: 1359 (60%); 0.891: 926 (41%); 1: 563 (25%) | 0.4423: 451 (20%); 0.7372: 903 (40%); 0.891: 1351 (60%); 1: 2250 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0833, 0.2115, 0.4936, 0.7885 | 0.0833: 1868 (83%); 0.2115: 1373 (61%); 0.4936: 907 (40%); 0.7885: 462 (21%) | 0.0833: 467 (21%); 0.2115: 905 (40%); 0.4936: 1351 (60%); 0.7885: 1803 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0027, 0.04, 0.1031, 0.2489 | 0.0027: 1808 (80%); 0.04: 1354 (60%); 0.1031: 904 (40%); 0.2489: 456 (20%) | 0.0027: 451 (20%); 0.04: 914 (41%); 0.1031: 1355 (60%); 0.2489: 1911 (85%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5625, 0.785, 0.9423, 0.9744 | 0.5625: 1801 (80%); 0.785: 1355 (60%); 0.9423: 914 (41%); 0.9744: 573 (25%) | 0.5625: 470 (21%); 0.785: 904 (40%); 0.9423: 1352 (60%); 0.9744: 1861 (83%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0816, 0.2051, 0.4615, 0.7635 | 0.0816: 1833 (81%); 0.2051: 1358 (60%); 0.4615: 903 (40%); 0.7635: 450 (20%) | 0.0816: 453 (20%); 0.2051: 910 (40%); 0.4615: 1370 (61%); 0.7635: 1800 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, 0, 0.1225, 0.3175 | -0.0812: 1900 (84%); 0: 1352 (60%); 0.1225: 976 (43%); 0.3175: 452 (20%) | -0.0812: 563 (25%); 0: 901 (40%); 0.1225: 1394 (62%); 0.3175: 2148 (95%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.185, 0.0067, 0.0533, 0.0999 | -0.185: 1803 (80%); 0.0067: 1362 (61%); 0.0533: 907 (40%); 0.0999: 458 (20%) | -0.185: 455 (20%); 0.0067: 901 (40%); 0.0533: 1351 (60%); 0.0999: 1801 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3526, 0.5833, 0.7564, 0.8846 | 0.3526: 1808 (80%); 0.5833: 1358 (60%); 0.7564: 932 (41%); 0.8846: 467 (21%) | 0.3526: 455 (20%); 0.5833: 918 (41%); 0.7564: 1354 (60%); 0.8846: 1806 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1218, 0.3462, 0.5641, 0.7885 | 0.1218: 1825 (81%); 0.3462: 1351 (60%); 0.5641: 968 (43%); 0.7885: 473 (21%) | 0.1218: 474 (21%); 0.3462: 916 (41%); 0.5641: 1433 (64%); 0.7885: 1816 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0583, 0.1575, 0.3032, 0.619 | 0.0583: 1801 (80%); 0.1575: 1351 (60%); 0.3032: 900 (40%); 0.619: 450 (20%) | 0.0583: 452 (20%); 0.1575: 902 (40%); 0.3032: 1350 (60%); 0.619: 1800 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.7% | 29, 62, 85, 148 | 29: 1783 (79%); 62: 1333 (59%); 85: 902 (40%); 148: 446 (20%) | 29: 453 (20%); 62: 918 (41%); 85: 1334 (59%); 148: 1786 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.7% | 1.764, 2.3176, 2.9448, 3.9562 | 1.764: 1794 (80%); 2.3176: 1346 (60%); 2.9448: 897 (40%); 3.9562: 449 (20%) | 1.764: 449 (20%); 2.3176: 897 (40%); 2.9448: 1346 (60%); 3.9562: 1794 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 8, 19, 27, 35 | 8: 1866 (83%); 19: 1370 (61%); 27: 974 (43%); 35: 502 (22%) | 8: 457 (20%); 19: 937 (42%); 27: 1352 (60%); 35: 1805 (80%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3 | 1: 1838 (82%); 2: 1415 (63%); 3: 898 (40%) | 1: 835 (37%); 2: 1352 (60%); 3: 1830 (81%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0147, -0.0036, 0.01, 0.0227 | -0.0147: 1801 (80%); -0.0036: 1356 (60%); 0.01: 903 (40%); 0.0227: 457 (20%) | -0.0147: 456 (20%); -0.0036: 910 (40%); 0.01: 1355 (60%); 0.0227: 1800 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5861, 25.8645, 26.5446, 27.3461 | 24.5861: 1802 (80%); 25.8645: 1352 (60%); 26.5446: 904 (40%); 27.3461: 454 (20%) | 24.5861: 460 (20%); 25.8645: 902 (40%); 26.5446: 1353 (60%); 27.3461: 1802 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.8062, -0.1546, 0.338, 1.108 | -0.8062: 1800 (80%); -0.1546: 1350 (60%); 0.338: 901 (40%); 1.108: 451 (20%) | -0.8062: 450 (20%); -0.1546: 900 (40%); 0.338: 1351 (60%); 1.108: 1801 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -1.108, -0.338, 0.1546, 0.8062 | -1.108: 1801 (80%); -0.338: 1351 (60%); 0.1546: 900 (40%); 0.8062: 450 (20%) | -1.108: 451 (20%); -0.338: 901 (40%); 0.1546: 1350 (60%); 0.8062: 1800 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0443, -0.0043, 0.024, 0.0665 | -0.0443: 1800 (80%); -0.0043: 1351 (60%); 0.024: 900 (40%); 0.0665: 451 (20%) | -0.0443: 450 (20%); -0.0043: 905 (40%); 0.024: 1350 (60%); 0.0665: 1800 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.1019, 8.54, 8.8582, 9.2113 | 8.1019: 1800 (80%); 8.54: 1343 (60%); 8.8582: 896 (40%); 9.2113: 450 (20%) | 8.1019: 450 (20%); 8.54: 907 (40%); 8.8582: 1354 (60%); 9.2113: 1800 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.5% | 0, 1 | 0: 2238 (99%); 1: 715 (32%) | 0: 1523 (68%); 1: 1979 (88%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.5% | 0 | 0: 1795 (80%) | 0: 1886 (84%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.5% | 0, 1 | 0: 2238 (99%); 1: 767 (34%) | 0: 1471 (65%); 1: 1954 (87%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 3, 6, 140, 264 | 3: 1842 (82%); 6: 1403 (62%); 140: 901 (40%); 264: 453 (20%) | 3: 560 (25%); 6: 937 (42%); 140: 1355 (60%); 264: 1802 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 5, 84, 140 | 1: 1852 (82%); 5: 1363 (61%); 84: 906 (40%); 140: 456 (20%) | 1: 570 (25%); 5: 940 (42%); 84: 1352 (60%); 140: 1803 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.6722, -0.1532, 0.1004, 0.5981 | -0.6722: 1801 (80%); -0.1532: 1350 (60%); 0.1004: 900 (40%); 0.5981: 451 (20%) | -0.6722: 451 (20%); -0.1532: 900 (40%); 0.1004: 1350 (60%); 0.5981: 1801 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -2.631, -0.9746, -0.1295, 1.2604 | -2.631: 1800 (80%); -0.9746: 1350 (60%); -0.1295: 900 (40%); 1.2604: 450 (20%) | -2.631: 450 (20%); -0.9746: 900 (40%); -0.1295: 1350 (60%); 1.2604: 1800 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -2.5255, -0.8709, -0.0707, 1.0961 | -2.5255: 1800 (80%); -0.8709: 1350 (60%); -0.0707: 900 (40%); 1.0961: 450 (20%) | -2.5255: 450 (20%); -0.8709: 900 (40%); -0.0707: 1350 (60%); 1.0961: 1800 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.4889, -0.1005, 0.1179, 0.519 | -0.4889: 1800 (80%); -0.1005: 1350 (60%); 0.1179: 901 (40%); 0.519: 450 (20%) | -0.4889: 450 (20%); -0.1005: 900 (40%); 0.1179: 1351 (60%); 0.519: 1800 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -2.7601, -0.9897, -0.1259, 1.3543 | -2.7601: 1800 (80%); -0.9897: 1350 (60%); -0.1259: 900 (40%); 1.3543: 450 (20%) | -2.7601: 450 (20%); -0.9897: 900 (40%); -0.1259: 1350 (60%); 1.3543: 1800 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -2.6123, -0.9539, -0.1139, 1.2583 | -2.6123: 1800 (80%); -0.9539: 1350 (60%); -0.1139: 900 (40%); 1.2583: 450 (20%) | -2.6123: 450 (20%); -0.9539: 900 (40%); -0.1139: 1350 (60%); 1.2583: 1800 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 35.18, 43.87, 51.504, 61.088 | 35.18: 1801 (80%); 43.87: 1350 (60%); 51.504: 900 (40%); 61.088: 450 (20%) | 35.18: 451 (20%); 43.87: 900 (40%); 51.504: 1350 (60%); 61.088: 1800 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 98.1% | -0.2055, -0.1015, -0.008, 0.1367 | -0.2055: 1766 (78%); -0.1015: 1324 (59%); -0.008: 883 (39%); 0.1367: 442 (20%) | -0.2055: 443 (20%); -0.1015: 883 (39%); -0.008: 1325 (59%); 0.1367: 1765 (78%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.5% | 0.0065, 0.0162, 0.0329, 0.0609 | 0.0065: 1793 (80%); 0.0162: 1344 (60%); 0.0329: 895 (40%); 0.0609: 448 (20%) | 0.0065: 446 (20%); 0.0162: 895 (40%); 0.0329: 1344 (60%); 0.0609: 1791 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 4, 9 | 0: 2250 (100%); 1: 1670 (74%); 4: 904 (40%); 9: 465 (21%) | 0: 580 (26%); 1: 926 (41%); 4: 1480 (66%); 9: 1831 (81%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667 | 0: 2250 (100%); 0.1667: 465 (21%) | 0: 1522 (68%); 0.1667: 1821 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.4, 0.6667 | 0: 2250 (100%); 0.4: 939 (42%); 0.6667: 488 (22%) | 0: 901 (40%); 0.4: 1354 (60%); 0.6667: 1852 (82%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 6 | 0: 2250 (100%); 1: 1533 (68%); 3: 915 (41%); 6: 513 (23%) | 0: 717 (32%); 1: 1099 (49%); 3: 1501 (67%); 6: 1804 (80%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 4, 9 | 0: 2250 (100%); 1: 1670 (74%); 4: 904 (40%); 9: 465 (21%) | 0: 580 (26%); 1: 926 (41%); 4: 1480 (66%); 9: 1831 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 2250 (100%); 1: 1539 (68%); 3: 934 (42%); 7: 454 (20%) | 0: 711 (32%); 1: 1083 (48%); 3: 1501 (67%); 7: 1854 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2008, 0.3664, 0.5885 | 0: 2047 (91%); 0.2008: 1350 (60%); 0.3664: 900 (40%); 0.5885: 450 (20%) | 0: 551 (24%); 0.2008: 900 (40%); 0.3664: 1350 (60%); 0.5885: 1800 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.1176, 0.5339 | 0: 2021 (90%); 0.1176: 902 (40%); 0.5339: 450 (20%) | 0: 1265 (56%); 0.1176: 1352 (60%); 0.5339: 1800 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2619, 0.5761 | 0: 2034 (90%); 0.2619: 902 (40%); 0.5761: 450 (20%) | 0: 1051 (47%); 0.2619: 1350 (60%); 0.5761: 1800 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2619, 0.5761 | 0: 2034 (90%); 0.2619: 902 (40%); 0.5761: 450 (20%) | 0: 1051 (47%); 0.2619: 1350 (60%); 0.5761: 1800 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1646, 0, 0.1289 | -0.1646: 1800 (80%); 0: 1640 (73%); 0.1289: 450 (20%) | -0.1646: 450 (20%); 0: 1660 (74%); 0.1289: 1800 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.696, -0.2251, 0.1893, 1.4548 | -0.696: 1800 (80%); -0.2251: 1350 (60%); 0.1893: 901 (40%); 1.4548: 450 (20%) | -0.696: 450 (20%); -0.2251: 900 (40%); 0.1893: 1359 (60%); 1.4548: 1800 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 6, 10 | 2: 1884 (84%); 4: 1434 (64%); 6: 1068 (47%); 10: 534 (24%) | 2: 602 (27%); 4: 1007 (45%); 6: 1353 (60%); 10: 1816 (81%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0665, -0.0242, 0.0077, 0.0456 | -0.0665: 1802 (80%); -0.0242: 1351 (60%); 0.0077: 898 (40%); 0.0456: 450 (20%) | -0.0665: 448 (20%); -0.0242: 899 (40%); 0.0077: 1352 (60%); 0.0456: 1800 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.08, -0.0386, -0, 0.0469 | -0.08: 1800 (80%); -0.0386: 1350 (60%); -0: 900 (40%); 0.0469: 452 (20%) | -0.08: 450 (20%); -0.0386: 900 (40%); -0: 1351 (60%); 0.0469: 1798 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0484, -0.0188, 0.0088, 0.0383 | -0.0484: 1799 (80%); -0.0188: 1351 (60%); 0.0088: 899 (40%); 0.0383: 451 (20%) | -0.0484: 451 (20%); -0.0188: 899 (40%); 0.0088: 1351 (60%); 0.0383: 1799 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -24.1438, -10.7462, 1.0658, 23.1282 | -24.1438: 1800 (80%); -10.7462: 1350 (60%); 1.0658: 900 (40%); 23.1282: 450 (20%) | -24.1438: 450 (20%); -10.7462: 900 (40%); 1.0658: 1350 (60%); 23.1282: 1800 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1765, 0.4531, 0.7264, 0.8957 | 0.1765: 1801 (80%); 0.4531: 1350 (60%); 0.7264: 900 (40%); 0.8957: 451 (20%) | 0.1765: 451 (20%); 0.4531: 900 (40%); 0.7264: 1350 (60%); 0.8957: 1800 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.7919, -1.5224, -0.2289, 1.2824 | -2.7919: 1800 (80%); -1.5224: 1350 (60%); -0.2289: 900 (40%); 1.2824: 450 (20%) | -2.7919: 450 (20%); -1.5224: 900 (40%); -0.2289: 1350 (60%); 1.2824: 1800 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.7302, -0.2663, 0.1392, 0.6002 | -0.7302: 1800 (80%); -0.2663: 1350 (60%); 0.1392: 900 (40%); 0.6002: 450 (20%) | -0.7302: 450 (20%); -0.2663: 900 (40%); 0.1392: 1350 (60%); 0.6002: 1800 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -2.5906, -1.3238, -0.125, 1.1524 | -2.5906: 1800 (80%); -1.3238: 1350 (60%); -0.125: 900 (40%); 1.1524: 450 (20%) | -2.5906: 450 (20%); -1.3238: 900 (40%); -0.125: 1350 (60%); 1.1524: 1800 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -6.9682, -2.6314, 0.7828, 4.99 | -6.9682: 1800 (80%); -2.6314: 1350 (60%); 0.7828: 900 (40%); 4.99: 450 (20%) | -6.9682: 450 (20%); -2.6314: 900 (40%); 0.7828: 1350 (60%); 4.99: 1800 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 23.55, 43.202, 60.746, 78.162 | 23.55: 1801 (80%); 43.202: 1350 (60%); 60.746: 900 (40%); 78.162: 450 (20%) | 23.55: 451 (20%); 43.202: 900 (40%); 60.746: 1350 (60%); 78.162: 1800 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 40.23, 44.442, 48.694, 55.888 | 40.23: 1801 (80%); 44.442: 1350 (60%); 48.694: 900 (40%); 55.888: 450 (20%) | 40.23: 451 (20%); 44.442: 900 (40%); 48.694: 1350 (60%); 55.888: 1800 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 36.716, 44.222, 50.588, 58.86 | 36.716: 1800 (80%); 44.222: 1350 (60%); 50.588: 900 (40%); 58.86: 451 (20%) | 36.716: 450 (20%); 44.222: 900 (40%); 50.588: 1350 (60%); 58.86: 1801 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 2248 (100%) | 0: 2250 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0323, 0.0474, 0.0623, 0.094 | 0.0323: 1808 (80%); 0.0474: 1351 (60%); 0.0623: 902 (40%); 0.094: 454 (20%) | 0.0323: 453 (20%); 0.0474: 901 (40%); 0.0623: 1350 (60%); 0.094: 1801 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0872, -0.0598, -0.0438, -0.0349 | -0.0872: 1800 (80%); -0.0598: 1351 (60%); -0.0438: 900 (40%); -0.0349: 459 (20%) | -0.0872: 452 (20%); -0.0598: 902 (40%); -0.0438: 1350 (60%); -0.0349: 1805 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 2250 (100%); 1: 605 (27%) | 0: 1645 (73%); 1: 1844 (82%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.7% | 24, 37, 59.2, 68 | 24: 1832 (81%); 37: 1371 (61%); 59.2: 897 (40%); 68: 453 (20%) | 24: 503 (22%); 37: 898 (40%); 59.2: 1346 (60%); 68: 1838 (82%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.6% | 0.0126, 0.0193, 0.0275, 0.0456 | 0.0126: 1772 (79%); 0.0193: 1328 (59%); 0.0275: 887 (39%); 0.0456: 445 (20%) | 0.0126: 446 (20%); 0.0193: 891 (40%); 0.0275: 1331 (59%); 0.0456: 1773 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 99.9% | 0.1702, 0.2917, 0.4576, 0.7289 | 0.1702: 1798 (80%); 0.2917: 1349 (60%); 0.4576: 899 (40%); 0.7289: 450 (20%) | 0.1702: 450 (20%); 0.2917: 900 (40%); 0.4576: 1349 (60%); 0.7289: 1798 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 99.9% | 28.54, 61, 97.22, 146.26 | 28.54: 1798 (80%); 61: 1350 (60%); 97.22: 899 (40%); 146.26: 450 (20%) | 28.54: 450 (20%); 61: 902 (40%); 97.22: 1349 (60%); 146.26: 1798 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -3.814, -1.1135, 0.254, 2.908 | -3.814: 1800 (80%); -1.1135: 1350 (60%); 0.254: 900 (40%); 2.908: 450 (20%) | -3.814: 450 (20%); -1.1135: 900 (40%); 0.254: 1350 (60%); 2.908: 1800 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 18.828, 33.24, 53.834, 74.982 | 18.828: 1800 (80%); 33.24: 1351 (60%); 53.834: 900 (40%); 74.982: 450 (20%) | 18.828: 450 (20%); 33.24: 901 (40%); 53.834: 1350 (60%); 74.982: 1800 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 19.614, 33.154, 54.866, 76.71 | 19.614: 1800 (80%); 33.154: 1350 (60%); 54.866: 900 (40%); 76.71: 451 (20%) | 19.614: 450 (20%); 33.154: 900 (40%); 54.866: 1350 (60%); 76.71: 1801 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 12.718, 33.676, 63.946, 87.512 | 12.718: 1800 (80%); 33.676: 1350 (60%); 63.946: 900 (40%); 87.512: 450 (20%) | 12.718: 450 (20%); 33.676: 900 (40%); 63.946: 1350 (60%); 87.512: 1800 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 11.744, 37.81, 64.802, 91.872 | 11.744: 1800 (80%); 37.81: 1351 (60%); 64.802: 900 (40%); 91.872: 450 (20%) | 11.744: 450 (20%); 37.81: 901 (40%); 64.802: 1350 (60%); 91.872: 1800 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 8, 12, 17 | 5: 1816 (81%); 8: 1430 (64%); 12: 1018 (45%); 17: 494 (22%) | 5: 548 (24%); 8: 928 (41%); 12: 1367 (61%); 17: 1853 (82%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 14, 17 | 5: 1851 (82%); 10: 1352 (60%); 14: 905 (40%); 17: 534 (24%) | 5: 487 (22%); 10: 1013 (45%); 14: 1433 (64%); 17: 1837 (82%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 43.45, 47.83, 51.648, 56.022 | 43.45: 1802 (80%); 47.83: 1351 (60%); 51.648: 900 (40%); 56.022: 450 (20%) | 43.45: 451 (20%); 47.83: 902 (40%); 51.648: 1350 (60%); 56.022: 1800 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.2222, 0.5238, 0.7302, 0.9127 | 0.2222: 1801 (80%); 0.5238: 1357 (60%); 0.7302: 903 (40%); 0.9127: 455 (20%) | 0.2222: 454 (20%); 0.5238: 904 (40%); 0.7302: 1359 (60%); 0.9127: 1813 (81%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.78, 18.4, 22.68, 28.16 | 15.78: 1803 (80%); 18.4: 1353 (60%); 22.68: 903 (40%); 28.16: 452 (20%) | 15.78: 458 (20%); 18.4: 903 (40%); 22.68: 1354 (60%); 28.16: 1804 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 15.78, 18.4, 22.68, 28.16 | 15.78: 1803 (80%); 18.4: 1353 (60%); 22.68: 903 (40%); 28.16: 452 (20%) | 15.78: 458 (20%); 18.4: 903 (40%); 22.68: 1354 (60%); 28.16: 1804 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8614, 0.9003, 0.9424, 0.9808 | 0.8614: 1801 (80%); 0.9003: 1353 (60%); 0.9424: 902 (40%); 0.9808: 454 (20%) | 0.8614: 457 (20%); 0.9003: 905 (40%); 0.9424: 1353 (60%); 0.9808: 1808 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.74, 0.89, 1.07, 1.45 | 0.74: 1820 (81%); 0.89: 1361 (60%); 1.07: 912 (41%); 1.45: 456 (20%) | 0.74: 453 (20%); 0.89: 915 (41%); 1.07: 1360 (60%); 1.45: 1804 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 99.9% | 0.0203, 0.0462, 0.0775, 0.1308 | 0.0203: 1800 (80%); 0.0462: 1349 (60%); 0.0775: 901 (40%); 0.1308: 450 (20%) | 0.0203: 450 (20%); 0.0462: 901 (40%); 0.0775: 1349 (60%); 0.1308: 1800 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 44.141, 76.2178, 120.5089, 197.4173 | 44.141: 1800 (80%); 76.2178: 1350 (60%); 120.5089: 900 (40%); 197.4173: 450 (20%) | 44.141: 450 (20%); 76.2178: 900 (40%); 120.5089: 1350 (60%); 197.4173: 1800 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 42.1584, 73.3662, 115.1331, 191.3396 | 42.1584: 1800 (80%); 73.3662: 1350 (60%); 115.1331: 900 (40%); 191.3396: 450 (20%) | 42.1584: 450 (20%); 73.3662: 900 (40%); 115.1331: 1350 (60%); 191.3396: 1800 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 40.0839, 70.2105, 111.1489, 185.2088 | 40.0839: 1800 (80%); 70.2105: 1350 (60%); 111.1489: 900 (40%); 185.2088: 450 (20%) | 40.0839: 450 (20%); 70.2105: 900 (40%); 111.1489: 1350 (60%); 185.2088: 1800 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 45.7475, 79.5029, 125.1894, 204.7863 | 45.7475: 1800 (80%); 79.5029: 1350 (60%); 125.1894: 900 (40%); 204.7863: 450 (20%) | 45.7475: 450 (20%); 79.5029: 900 (40%); 125.1894: 1350 (60%); 204.7863: 1800 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 47.7202, 82.2453, 129.8661, 212.9415 | 47.7202: 1800 (80%); 82.2453: 1350 (60%); 129.8661: 900 (40%); 212.9415: 450 (20%) | 47.7202: 450 (20%); 82.2453: 900 (40%); 129.8661: 1350 (60%); 212.9415: 1800 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 2250 (100%) | 0: 2007 (89%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 2250 (100%) | 0: 2039 (91%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 99.9% | -0.0785, -0.0364, 0.0028, 0.0494 | -0.0785: 1800 (80%); -0.0364: 1349 (60%); 0.0028: 900 (40%); 0.0494: 452 (20%) | -0.0785: 450 (20%); -0.0364: 902 (40%); 0.0028: 1349 (60%); 0.0494: 1799 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -76.158, -61.044, -43.424, -25.88 | -76.158: 1800 (80%); -61.044: 1350 (60%); -43.424: 900 (40%); -25.88: 451 (20%) | -76.158: 450 (20%); -61.044: 900 (40%); -43.424: 1350 (60%); -25.88: 1802 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.4% | 0.6387, 0.9117, 1.119, 1.4091 | 0.6387: 1789 (80%); 0.9117: 1342 (60%); 1.119: 895 (40%); 1.4091: 448 (20%) | 0.6387: 448 (20%); 0.9117: 895 (40%); 1.119: 1343 (60%); 1.4091: 1789 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.4% | 4, 6, 8, 9 | 4: 1817 (81%); 6: 1426 (63%); 8: 985 (44%); 9: 701 (31%) | 4: 613 (27%); 6: 1017 (45%); 8: 1536 (68%); 9: 1855 (82%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.3% | 0.2084, 0.2512, 0.3026, 0.3907 | 0.2084: 1787 (79%); 0.2512: 1341 (60%); 0.3026: 895 (40%); 0.3907: 448 (20%) | 0.2084: 449 (20%); 0.2512: 894 (40%); 0.3026: 1341 (60%); 0.3907: 1787 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.3% | 4, 6, 8, 9 | 4: 1847 (82%); 6: 1492 (66%); 8: 1014 (45%); 9: 735 (33%) | 4: 545 (24%); 6: 969 (43%); 8: 1499 (67%); 9: 1816 (81%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.4% | 0.0275, 0.0361, 0.0473, 0.0679 | 0.0275: 1791 (80%); 0.0361: 1344 (60%); 0.0473: 896 (40%); 0.0679: 448 (20%) | 0.0275: 449 (20%); 0.0361: 899 (40%); 0.0473: 1345 (60%); 0.0679: 1792 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.4% | 4, 6, 8, 9 | 4: 1831 (81%); 6: 1427 (63%); 8: 939 (42%); 9: 673 (30%) | 4: 601 (27%); 6: 1039 (46%); 8: 1564 (70%); 9: 1883 (84%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.4% | -0.2294, -0.0917, 0.0392, 0.2258 | -0.2294: 1790 (80%); -0.0917: 1343 (60%); 0.0392: 895 (40%); 0.2258: 448 (20%) | -0.2294: 448 (20%); -0.0917: 896 (40%); 0.0392: 1342 (60%); 0.2258: 1789 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.4% | 2, 4, 6, 8 | 2: 1895 (84%); 4: 1392 (62%); 6: 976 (43%); 8: 617 (27%) | 2: 614 (27%); 4: 1090 (48%); 6: 1453 (65%); 8: 1804 (80%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 6.0% |
| 8k_item_5_02_filed_within_7d | 2.9% |
| above_avwap_20high | 21.2% |
| above_avwap_20low | 83.7% |
| above_avwap_252low | 68.8% |
| above_avwap_50low | 80.1% |
| above_cam_r3 | 34.0% |
| above_cam_r4 | 21.3% |
| above_cpr | 53.2% |
| above_pivot | 53.6% |
| above_prev_high | 25.0% |
| above_prev_high_clearance_atr_05 | 8.8% |
| above_prev_low | 80.6% |
| above_r1 | 23.1% |
| above_r2 | 9.6% |
| above_vwap | 42.0% |
| above_wood_p | 53.5% |
| ad_rising | 53.3% |
| adx_cross_up | 2.5% |
| adx_cross_up_20 | 3.2% |
| adx_di_bear | 62.0% |
| adx_di_bull | 38.0% |
| adx_strong | 5.8% |
| adx_trending | 41.4% |
| ao_cross_dn | 2.4% |
| ao_cross_up | 2.6% |
| ao_positive | 37.6% |
| ao_twin_peaks_bull | 5.2% |
| at_key_fib | 12.3% |
| at_key_fib_wide | 32.0% |
| avwap_20high_loss_recent_3d | 19.5% |
| avwap_20high_reclaim_recent_3d | 16.9% |
| avwap_20low_loss_recent_3d | 13.0% |
| avwap_20low_reclaim_recent_3d | 24.7% |
| avwap_252low_loss_recent_3d | 9.5% |
| avwap_252low_reclaim_recent_3d | 13.7% |
| avwap_50low_loss_recent_3d | 11.3% |
| avwap_50low_reclaim_recent_3d | 19.9% |
| bb_10_20_above_mid | 47.9% |
| bb_10_20_expanding | 49.2% |
| bb_10_20_pctb_gt_75 | 20.4% |
| bb_10_20_pctb_gt_8 | 15.0% |
| bb_10_20_pctb_gt_85 | 9.5% |
| bb_10_20_pctb_gt_9 | 5.5% |
| bb_10_20_pctb_gt_95 | 3.4% |
| bb_10_20_pctb_lt_05 | 3.2% |
| bb_10_20_pctb_lt_1 | 6.2% |
| bb_10_20_pctb_lt_15 | 11.2% |
| bb_10_20_pctb_lt_2 | 17.1% |
| bb_10_20_pctb_lt_25 | 22.8% |
| bb_10_20_reclaim_from_lower_recent_3d | 16.3% |
| bb_10_20_reclaim_from_upper_recent_3d | 11.0% |
| bb_10_20_squeeze | 29.6% |
| bb_10_20_touch_lower | 3.5% |
| bb_10_20_touch_upper | 3.7% |
| bb_20_15_above_mid | 43.4% |
| bb_20_15_expanding | 52.8% |
| bb_20_15_pctb_gt_75 | 25.2% |
| bb_20_15_pctb_gt_8 | 22.0% |
| bb_20_15_pctb_gt_85 | 18.1% |
| bb_20_15_pctb_gt_9 | 15.0% |
| bb_20_15_pctb_gt_95 | 12.4% |
| bb_20_15_pctb_lt_05 | 18.6% |
| bb_20_15_pctb_lt_1 | 23.1% |
| bb_20_15_pctb_lt_15 | 27.3% |
| bb_20_15_pctb_lt_2 | 31.3% |
| bb_20_15_pctb_lt_25 | 35.9% |
| bb_20_15_reclaim_from_lower_recent_3d | 21.1% |
| bb_20_15_reclaim_from_upper_recent_3d | 13.9% |
| bb_20_15_squeeze | 31.2% |
| bb_20_15_touch_lower | 18.9% |
| bb_20_15_touch_upper | 13.0% |
| bb_20_20_above_mid | 43.4% |
| bb_20_20_expanding | 52.8% |
| bb_20_20_pctb_gt_75 | 19.4% |
| bb_20_20_pctb_gt_8 | 15.0% |
| bb_20_20_pctb_gt_85 | 11.4% |
| bb_20_20_pctb_gt_9 | 8.7% |
| bb_20_20_pctb_gt_95 | 6.0% |
| bb_20_20_pctb_lt_05 | 9.4% |
| bb_20_20_pctb_lt_1 | 12.7% |
| bb_20_20_pctb_lt_15 | 17.4% |
| bb_20_20_pctb_lt_2 | 23.1% |
| bb_20_20_pctb_lt_25 | 28.7% |
| bb_20_20_reclaim_from_lower_recent_3d | 17.2% |
| bb_20_20_reclaim_from_upper_recent_3d | 9.8% |
| bb_20_20_squeeze | 13.8% |
| bb_20_20_touch_lower | 8.5% |
| bb_20_20_touch_upper | 5.6% |
| bearish_engulfing | 3.0% |
| bearish_pin_bar | 4.7% |
| below_avwap_20high | 78.8% |
| below_avwap_20low | 16.3% |
| below_avwap_252low | 31.2% |
| below_avwap_50low | 19.9% |
| below_cam_s3 | 28.5% |
| below_cam_s4 | 15.6% |
| below_cpr | 46.3% |
| below_ema_20 | 59.7% |
| below_ema_200 | 64.8% |
| below_ema_200_break_recent_5d | 10.7% |
| below_ema_20_break_recent_5d | 23.7% |
| below_ema_21 | 60.1% |
| below_ema_21_break_recent_5d | 23.6% |
| below_ema_50 | 64.3% |
| below_ema_50_break_recent_5d | 16.2% |
| below_ema_9 | 52.1% |
| below_ema_9_break_recent_5d | 32.2% |
| below_prev_high | 74.9% |
| below_prev_low | 19.2% |
| below_prev_low_clearance_atr_05 | 6.4% |
| below_s1 | 16.3% |
| below_s2 | 6.7% |
| below_sma_20 | 56.6% |
| below_sma_200 | 63.8% |
| below_sma_21 | 57.3% |
| below_sma_50 | 63.2% |
| below_sma_9 | 51.6% |
| below_vwap | 58.0% |
| blowoff_recent_3d | 0.7% |
| break_52w_high | 0.8% |
| break_52w_high_clearance_atr_05 | 0.3% |
| break_52w_high_confirmed_today | 1.6% |
| break_52w_low | 0.8% |
| bullish_engulfing | 7.2% |
| bullish_pin_bar | 9.1% |
| capitulation_recent_3d | 0.8% |
| ceo_buy | 0.9% |
| cfo_buy | 0.5% |
| chandelier_long_bullish | 57.0% |
| chandelier_long_flip_dn | 3.3% |
| chandelier_short_bearish | 71.6% |
| chandelier_short_flip_up | 3.7% |
| classification_change_from_tech | 71.4% |
| classification_change_to_defensive | 28.6% |
| close_above_open | 53.6% |
| close_below_open | 45.3% |
| close_in_bottom_40pct_of_range | 36.9% |
| close_in_top_40pct_of_range | 50.9% |
| cluster_buy | 0.5% |
| cmf_cross_dn | 37.7% |
| cmf_cross_up | 62.3% |
| cmf_negative | 37.7% |
| cmf_positive | 62.3% |
| concentrated_sell | 4.9% |
| cpr_narrow | 89.1% |
| cpr_narrow_tight | 25.0% |
| cup_handle_detected | 12.3% |
| cup_handle_neckline_break_retest_long | 3.8% |
| dc10_breakout_dn | 5.7% |
| dc10_breakout_dn_1pct | 10.5% |
| dc10_breakout_up | 5.3% |
| dc10_breakout_up_1pct | 10.0% |
| dc10_new_high | 15.4% |
| dc10_strong_breakout_dn | 1.7% |
| dc10_strong_breakout_up | 1.8% |
| dc20_breakout_dn | 4.4% |
| dc20_breakout_up | 3.6% |
| dc20_new_high | 11.0% |
| dc20_resistance_break_retest_strong | 10.9% |
| dc20_support_break_retest_strong | 19.7% |
| defensive_leadership | 61.4% |
| director_only_buy | 3.4% |
| doji | 5.2% |
| double_bottom_detected | 12.1% |
| double_top_detected | 14.1% |
| dpi_elevated | 50.9% |
| drying_volume_on_down_turn | 26.0% |
| drying_volume_on_up_turn | 27.2% |
| ema_20_50_bearish | 62.4% |
| ema_20_50_bullish | 37.6% |
| ema_20_50_death_cross | 1.2% |
| ema_20_50_golden_cross | 0.6% |
| ema_50_200_bearish | 60.0% |
| ema_50_200_bullish | 40.0% |
| ema_50_200_death_cross | 0.4% |
| ema_50_200_golden_cross | 0.3% |
| ema_9_21_bearish | 62.5% |
| ema_9_21_bullish | 37.5% |
| ema_9_21_death_cross | 1.8% |
| ema_9_21_golden_cross | 1.6% |
| evening_star | 3.9% |
| flag_bear_break_retest_short | 0.9% |
| flag_bear_broke | 1.0% |
| flag_bear_detected | 0.0% |
| flag_bull_break_retest_long | 0.9% |
| flag_bull_broke | 0.9% |
| flag_bull_detected | 0.4% |
| force_index_cross_dn | 4.9% |
| force_index_cross_up | 6.9% |
| force_index_positive | 43.6% |
| gap_dn_1_5pct | 14.6% |
| gap_dn_2pct | 9.7% |
| gap_up_1_5pct | 10.0% |
| gap_up_2pct | 7.0% |
| hammer | 7.7% |
| head_shoulders_bottom_detected | 3.9% |
| head_shoulders_top_detected | 5.5% |
| house_cluster_buy | 5.1% |
| house_cluster_sell | 5.6% |
| htf_aligned_bear | 51.5% |
| htf_aligned_bull | 25.7% |
| htf_disagreement | 1.6% |
| hull_bearish | 52.5% |
| hull_bullish | 47.5% |
| hull_flip_dn | 4.0% |
| hull_flip_up | 4.8% |
| ichi_above_cloud | 31.5% |
| ichi_above_cloud_break_recent_5d | 7.6% |
| ichi_below_cloud | 57.2% |
| ichi_below_cloud_break_recent_5d | 11.7% |
| ichi_cloud_thick | 86.8% |
| ichi_tk_bearish | 58.8% |
| ichi_tk_bullish | 35.7% |
| ichi_tk_cross_dn | 2.0% |
| ichi_tk_cross_up | 2.1% |
| ichi_weekly_above_cloud | 29.0% |
| ichi_weekly_below_cloud | 40.3% |
| ichi_weekly_in_cloud | 30.6% |
| in_reversal_window | 1.5% |
| inside_bar | 14.3% |
| inside_cpr | 3.5% |
| inside_kc | 86.6% |
| insider_cluster_active | 18.2% |
| institutional_buy | 90.6% |
| institutional_negative | 4.5% |
| institutional_persistence_growing | 45.0% |
| institutional_persistence_strong | 60.5% |
| institutional_strong_buy | 80.6% |
| inverted_cup_handle_detected | 8.4% |
| is_friday | 18.7% |
| is_halloween_period | 52.2% |
| is_halloween_period_first_day | 0.5% |
| is_january | 7.0% |
| is_january_extended | 8.0% |
| is_monday | 18.3% |
| is_pre_holiday | 4.0% |
| is_summer_period | 47.8% |
| is_totm_window | 31.3% |
| is_totm_window_first_day | 8.7% |
| is_week_open | 20.5% |
| kc_touch_lower | 10.3% |
| kc_touch_upper | 6.6% |
| large_dollar_buy | 1.1% |
| macd_12_26_9_bearish | 51.0% |
| macd_12_26_9_bullish | 49.0% |
| macd_12_26_9_crossover_dn | 3.0% |
| macd_12_26_9_crossover_up | 3.5% |
| macd_8_21_5_bearish | 49.1% |
| macd_8_21_5_bullish | 50.9% |
| macd_8_21_5_crossover_dn | 3.9% |
| macd_8_21_5_crossover_up | 4.8% |
| marubozu_bear | 0.6% |
| marubozu_bull | 1.2% |
| mfi_broad_overbought | 7.7% |
| mfi_broad_oversold | 11.5% |
| mfi_overbought | 1.5% |
| mfi_oversold | 2.8% |
| monthly_above_sma_12 | 36.7% |
| monthly_above_sma_6 | 35.9% |
| monthly_bias_bear | 56.8% |
| monthly_bias_bull | 29.4% |
| monthly_momentum_pos | 38.9% |
| morning_star | 4.4% |
| near_52w_high | 3.2% |
| near_52w_high_95pct | 10.8% |
| near_52w_high_retest_long | 0.2% |
| near_52w_low | 3.2% |
| near_52w_low_105pct | 10.8% |
| near_52w_low_retest_short | 0.8% |
| near_avwap_20high_atr_05x | 38.7% |
| near_avwap_20high_atr_10x | 69.5% |
| near_avwap_20high_atr_15x | 85.8% |
| near_avwap_20high_atr_20x | 94.4% |
| near_avwap_20low_atr_05x | 40.1% |
| near_avwap_20low_atr_10x | 67.5% |
| near_avwap_20low_atr_15x | 83.8% |
| near_avwap_20low_atr_20x | 92.0% |
| near_avwap_252low_atr_05x | 19.6% |
| near_avwap_252low_atr_10x | 35.9% |
| near_avwap_252low_atr_15x | 48.2% |
| near_avwap_252low_atr_20x | 57.8% |
| near_avwap_50low_atr_05x | 29.7% |
| near_avwap_50low_atr_10x | 52.7% |
| near_avwap_50low_atr_15x | 67.8% |
| near_avwap_50low_atr_20x | 78.4% |
| near_cam_r3 | 12.1% |
| near_cam_s3 | 13.0% |
| near_cam_s4 | 8.4% |
| near_fib_236 | 4.2% |
| near_fib_382 | 3.4% |
| near_fib_500 | 4.3% |
| near_fib_618 | 4.6% |
| near_fib_786 | 7.0% |
| near_pivot | 15.0% |
| near_prev_close | 14.0% |
| near_prev_high | 9.3% |
| near_prev_low | 9.1% |
| near_r1 | 9.3% |
| near_r1_wide | 44.2% |
| near_r2 | 3.5% |
| near_r2_wide | 24.0% |
| near_s1 | 8.8% |
| near_s1_wide | 40.9% |
| near_s2 | 3.0% |
| near_s2_wide | 19.2% |
| near_s3 | 1.5% |
| near_wood_r1 | 9.6% |
| near_wood_s1 | 10.1% |
| news_uses_polygon_score | 24.1% |
| obv_bearish | 54.4% |
| obv_bullish | 45.6% |
| obv_diverge_bull | 10.2% |
| obv_falling | 51.2% |
| obv_rising | 48.8% |
| outside_bar | 10.8% |
| pead_negative_surprise | 18.5% |
| pead_positive_surprise | 21.3% |
| pin_bar | 13.8% |
| po3_accumulation_active | 7.7% |
| po3_bearish | 15.6% |
| po3_bullish | 20.3% |
| po3_manipulation_sweep_down | 1.6% |
| po3_manipulation_sweep_up | 2.1% |
| po3_mmbm_setup | 0.8% |
| po3_mmsm_setup | 1.1% |
| po3_sweep_above_prior_high | 50.8% |
| po3_sweep_below_prior_low | 50.6% |
| ppo_bullish | 47.8% |
| ppo_crossover_dn | 3.2% |
| ppo_crossover_up | 4.1% |
| pre_fomc_d0 | 2.4% |
| pre_fomc_d1 | 2.6% |
| pre_fomc_window | 5.1% |
| price_above_dema | 52.7% |
| price_above_ema_20 | 40.3% |
| price_above_ema_200 | 35.2% |
| price_above_ema_200_break_recent_5d | 7.4% |
| price_above_ema_20_break_recent_5d | 20.5% |
| price_above_ema_21 | 39.9% |
| price_above_ema_21_break_recent_5d | 19.5% |
| price_above_ema_50 | 35.7% |
| price_above_ema_50_break_recent_5d | 11.6% |
| price_above_ema_9 | 47.9% |
| price_above_ema_9_break_recent_5d | 34.0% |
| price_above_hull | 53.0% |
| price_above_sma_200 | 36.2% |
| price_above_sma_21 | 42.7% |
| price_above_sma_50 | 36.8% |
| price_above_tema | 55.1% |
| price_below_dema | 47.3% |
| price_below_hull | 47.0% |
| price_below_tema | 44.9% |
| psar_bullish | 45.4% |
| psar_flip_dn | 3.2% |
| psar_flip_up | 4.2% |
| r1_break_retest_long | 49.9% |
| recent_blowoff_at_r3 | 0.2% |
| recent_capitulation_at_s3 | 0.4% |
| resistance_break_retest | 14.6% |
| risk_off_regime_bond_signal | 27.6% |
| risk_off_regime_bond_signal_strong | 11.2% |
| risk_off_regime_gold_signal | 41.8% |
| risk_on_regime_bond_signal | 37.6% |
| risk_on_regime_bond_signal_strong | 16.3% |
| roc_positive | 44.7% |
| roc_turning_dn | 5.5% |
| roc_turning_up | 6.7% |
| rsi_14_bullish | 37.7% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.4% |
| rsi_14_cross_dn_overbought_recent_3d | 4.0% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.6% |
| rsi_14_cross_up_oversold_recent_3d | 9.9% |
| rsi_14_extreme_ob | 0.2% |
| rsi_14_extreme_os | 0.5% |
| rsi_14_overbought | 2.7% |
| rsi_14_oversold | 3.9% |
| rsi_14_rising | 53.1% |
| rsi_21_bullish | 36.8% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.0% |
| rsi_21_cross_dn_overbought_recent_3d | 1.8% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.1% |
| rsi_21_cross_up_oversold_recent_3d | 3.9% |
| rsi_21_extreme_os | 0.1% |
| rsi_21_overbought | 1.1% |
| rsi_21_oversold | 1.8% |
| rsi_21_rising | 53.2% |
| rsi_2_bullish | 51.8% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 32.8% |
| rsi_2_cross_dn_overbought_recent_3d | 35.5% |
| rsi_2_cross_up_extreme_os_recent_3d | 39.2% |
| rsi_2_cross_up_oversold_recent_3d | 41.9% |
| rsi_2_extreme_ob | 17.9% |
| rsi_2_extreme_os | 17.3% |
| rsi_2_overbought | 29.7% |
| rsi_2_oversold | 26.7% |
| rsi_2_rising | 53.1% |
| rsi_9_bullish | 41.8% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 1.8% |
| rsi_9_cross_dn_overbought_recent_3d | 8.5% |
| rsi_9_cross_up_extreme_os_recent_3d | 5.2% |
| rsi_9_cross_up_oversold_recent_3d | 16.4% |
| rsi_9_extreme_ob | 0.8% |
| rsi_9_extreme_os | 1.5% |
| rsi_9_overbought | 5.6% |
| rsi_9_oversold | 9.3% |
| rsi_9_rising | 53.1% |
| s1_break_retest_short | 58.6% |
| sc_13d_filed_within_30d | 2.3% |
| sc_13g_filed_within_30d | 2.7% |
| sector_outperforming_spy | 44.3% |
| sector_underperforming_spy | 55.7% |
| shooting_star | 4.3% |
| sma_20_50_bullish | 40.5% |
| sma_20_50_golden_cross | 0.8% |
| sma_50_200_bullish | 43.0% |
| sma_50_200_golden_cross | 0.3% |
| sma_9_21_bullish | 40.6% |
| sma_9_21_golden_cross | 3.2% |
| smc_bos_bearish | 18.0% |
| smc_bos_bullish | 10.4% |
| smc_bos_retest_long | 3.2% |
| smc_bos_retest_short | 4.4% |
| smc_breaker_block_bearish | 20.1% |
| smc_breaker_block_bullish | 17.7% |
| smc_choch_bearish | 6.5% |
| smc_choch_bullish | 3.1% |
| smc_equal_highs_swept | 2.6% |
| smc_equal_lows_swept | 5.2% |
| smc_fvg_bearish_active | 47.5% |
| smc_fvg_bullish_active | 38.8% |
| smc_fvg_retest_long_zone | 11.5% |
| smc_fvg_retest_short_zone | 13.5% |
| smc_in_discount_zone | 70.5% |
| smc_in_premium_zone | 46.5% |
| smc_inverse_fvg_bearish | 83.5% |
| smc_inverse_fvg_bullish | 70.1% |
| smc_liquidity_swept_dn | 1.5% |
| smc_liquidity_swept_up | 1.6% |
| smc_mitigation_block_long | 1.1% |
| smc_mitigation_block_short | 1.2% |
| smc_ob_bearish_active | 44.4% |
| smc_ob_bullish_active | 25.1% |
| smc_ote_long_zone | 8.0% |
| smc_ote_short_zone | 5.4% |
| squeeze_fire_dn | 2.4% |
| squeeze_fire_up | 4.2% |
| squeeze_in | 28.9% |
| squeeze_positive | 43.8% |
| stoch_bearish_cross | 11.5% |
| stoch_broad_overbought | 21.6% |
| stoch_broad_oversold | 28.4% |
| stoch_bullish_cross | 13.8% |
| stoch_overbought | 15.7% |
| stoch_oversold | 20.4% |
| stochrsi_cross_dn | 26.6% |
| stochrsi_cross_up | 31.9% |
| stochrsi_overbought | 29.6% |
| stochrsi_oversold | 26.5% |
| supertrend_bearish | 3.4% |
| supertrend_bullish | 96.6% |
| supertrend_flip_dn | 0.8% |
| supertrend_flip_recent_long_5d | 3.1% |
| supertrend_flip_recent_short_5d | 5.3% |
| supertrend_flip_up | 1.2% |
| support_break_retest | 27.3% |
| tema_above_dema | 45.4% |
| tema_cross_dn | 2.4% |
| tema_cross_up | 2.8% |
| three_black_crows | 2.8% |
| three_white_soldiers | 2.4% |
| triangle_apex_break_retest_long | 10.9% |
| triangle_ascending_detected | 6.2% |
| triangle_descending_detected | 7.9% |
| uo_overbought | 0.2% |
| uo_oversold | 0.4% |
| usd_strengthening | 24.0% |
| usd_weakening | 12.9% |
| vix_band_high | 48.4% |
| vix_band_low | 26.5% |
| vix_band_mid | 25.1% |
| vix_term_backwardation | 14.0% |
| vix_term_contango | 86.0% |
| vol_above_avg | 46.1% |
| vol_below_avg | 53.9% |
| vol_spike_12x | 31.2% |
| vol_spike_15x | 18.5% |
| vol_spike_17x | 14.3% |
| vol_spike_2x | 9.6% |
| vol_spike_2x_on_down_day_recent_3d | 6.4% |
| vol_spike_2x_on_up_day_recent_3d | 4.3% |
| vol_spike_3x | 3.2% |
| vp_above_value_area | 17.4% |
| vp_below_value_area | 27.0% |
| vp_close_above_poc | 42.8% |
| vp_close_below_poc | 57.2% |
| vp_in_value_area | 55.6% |
| week_open_gap_down_15pct | 3.7% |
| week_open_gap_up_15pct | 2.0% |
| weekly_above_ema_10 | 36.1% |
| weekly_above_ema_20 | 34.7% |
| weekly_bias_bear | 61.1% |
| weekly_bias_bull | 31.9% |
| weekly_momentum_pos | 41.1% |
| williams_r_overbought | 12.9% |
| williams_r_oversold | 14.9% |
| williams_r_rising | 54.5% |
| within_pead_window | 38.9% |
| within_post_deletion_window | 6.6% |
| within_post_inclusion_window | 1.5% |
| within_pre_rebalance_window | 2.6% |
| xs_avoid_high_ivol | 67.1% |
| xs_avoid_high_max | 69.9% |
| xs_high_beta_decile | 31.3% |
| xs_low_beta_bottom_quintile | 31.3% |
| xs_low_beta_decile | 11.4% |
| xs_low_beta_decile_entry_recent_5d | 0.4% |
| xs_low_beta_top_quintile | 11.4% |
| xs_momentum_bottom_decile | 15.3% |
| xs_momentum_bottom_quintile | 27.4% |
| xs_momentum_top_decile | 11.5% |
| xs_momentum_top_quintile | 19.4% |
| xs_quality_bottom_quintile | 21.6% |
| xs_quality_top_quintile | 23.7% |
| xs_quality_top_tercile | 41.0% |
| year_high_break_retest_long | 2.5% |
| year_low_break_retest_short | 4.5% |
| yoy_surprise_high | 48.6% |
| yoy_surprise_negative | 41.4% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 91.6% |
| committed_growth_holders | 91.6% |
| corp_donations_1y | 6.5% |
| corp_donations_count_1y | 6.5% |
| corp_donations_unique_pacs | 6.5% |
| cot_rut_commercials_pctile_3y | 53.0% |
| cot_rut_mmoney_pctile_3y | 53.0% |
| cup_handle_depth_pct | 20.4% |
| days_since_classification_change | 0.3% |
| days_since_deletion | 8.8% |
| days_since_inclusion | 14.4% |
| days_to_next_holiday | 65.2% |
| days_to_rebalance | 11.9% |
| dpi_30d_avg | 95.7% |
| dpi_recent | 95.7% |
| earnings_announcement_return | 90.7% |
| earnings_eps_yoy_growth | 94.2% |
| flag_bull_pole_move_pct | 0.4% |
| gov_contracts_4q_sum | 38.3% |
| gov_contracts_last_qtr_amount | 38.3% |
| gov_contracts_qoq_growth | 38.3% |
| head_shoulders_magnitude_pct | 9.2% |
| insider_director_buyers_30d | 6.4% |
| insider_officer_buyers_30d | 6.4% |
| insider_total_shares_bought_30d | 6.4% |
| insider_unique_buyers_30d | 6.4% |
| inverted_cup_handle_height_pct | 15.9% |
| lobbying_amount_1y | 68.8% |
| lobbying_amount_q | 68.8% |
| lobbying_amount_yoy | 68.8% |
| otc_short_ratio_recent | 95.7% |
| otc_volume_recent | 95.7% |
| pair_half_life | 91.4% |
| pair_max_abs_zscore | 91.4% |
| pair_zscore_signed | 91.4% |
| pct_from_avwap_20high | 88.8% |
| pct_from_avwap_20low | 83.2% |
| pct_from_avwap_252low | 92.8% |
| pct_from_avwap_50low | 88.1% |
| persistent_holders_4q | 91.6% |
| persistent_holders_8q | 91.6% |
| sc_13g_latest_percent_owned | 1.4% |
| search_volume_index_recent | 76.6% |
| search_volume_observations | 76.6% |
| search_volume_zscore_30d | 76.6% |
| sector_etf_return_20d | 2.7% |
| spy_return_20d | 2.7% |
| total_active_holders | 91.6% |
| triangle_breakdown_pct | 7.9% |
| triangle_breakout_pct | 6.2% |
| xs_quality_decile | 63.7% |
| xs_quality_gross_profitability | 63.7% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.998), `avwap_252low` (0.994), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (1.0), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.998), `cam_r2` (0.998), `cam_r3` (0.998), `cam_r4` (0.998), `cam_s1` (0.998), `cam_s2` (0.998), `cam_s3` (0.997), `cam_s4` (0.997), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.998), `cpr_top` (0.998), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.998), `dc10_lower` (0.998), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.998), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.997), `double_bottom_trough` (0.998), `double_top_neckline` (0.997), `double_top_peak` (0.998), `entry_stop_long` (0.997), `entry_stop_short` (0.998), `fib_236` (0.995), `fib_382` (0.996), `fib_500` (0.997), `fib_618` (0.997), `fib_786` (0.997), `fib_ext_127` (0.99), `fib_ext_162` (0.986), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.998), `head_shoulders_top_neckline` (0.997), `hull_ma` (0.998), `ichi_kijun` (0.999), `ichi_senkou_a` (0.993), `ichi_senkou_b` (0.988), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.998), `monthly_sma_12` (0.98), `monthly_sma_6` (0.993), `pivot` (0.998), `prev_close` (0.998), `prev_high` (0.998), `prev_low` (0.998), `psar_value` (0.998), `r1` (0.998), `r2` (0.998), `r3` (0.998), `s1` (0.997), `s2` (0.997), `s3` (0.996), `supertrend_value` (0.995), `swing_high` (0.993), `swing_low` (0.996), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.996), `vp_value_area_low` (0.996), `weekly_close` (0.998), `weekly_ema_10` (0.999), `weekly_ema_20` (0.996), `wood_p` (0.998), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.998), `wood_s2` (0.997), `year_high` (0.966), `year_low` (0.972)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | as cmf_cross_up, mirrored | 3 | **FIRE-ADDING** | **YES** |
| P2.1 | cmf window | 3 | **FIRE-ADDING** | **YES** |
| P2.2 | cross level (zero line) | 3 | **FIRE-ADDING** | **YES** |
| P3 | po3_accum_range_pct >= 0.0458 | 5 | subset-safe | no - derives offline |
| P4 | rsi_14 < 50 | 4 | subset-safe | no - derives offline |
| P5 | rsi_14 > 50 | 2 | subset-safe | no - derives offline |
| P6 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     3 x 3 x 3 x 5 x 4 x 2 x 1 = 1080
offline gradings   40 level-combinations x 24 exits = 960
ENGINE RUNS        27 (every fire-adding axis sits at production-only until its env actuator exists)
check              27 x 40 = 1080
```

B-row candidates NOT in this factorial: 655 census axes join it only when REGISTERED at the T3 band review.
