# Table A - hammer_at_support_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit fa06ebf3e at 2026-09-19 13:07:41 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** candle | **status:** NOT-STARTED | **R5 fires:** 110 | **surviving fires (T1):** 110 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  bb_20_20_touch_lower  <- backtest/signals/screener.py
       DEFN: close at/beyond the Bollinger(20, 2.0) band (bb block)
       knobs P1.1-P1.1 (band rows in Table A)
P2  hammer  <- backtest/signals/screener.py +1
       DEFN: canonical single/two-candle reversal pattern (Nison; compute_candle_signals - geometry in producer)
       knobs P2.1-P2.1 (band rows in Table A)
P3  near_s1  <- backtest/signals/screener.py +2
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P3.1-P3.1 (band rows in Table A)
P4  near_s2  <- backtest/signals/screener.py +1
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P4.1-P4.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P5  rsi_14 < 35   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_hammer_at_support_long (docstring and return dropped):

```python
fires = s.get('hammer') and (s.get('near_s1') or s.get('near_s2') or s.get('bb_20_20_touch_lower')) and (s.get('rsi_14', 50) < 35)
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
| P1 | PRODUCER | bb_20_20_touch_lower - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close at/beyond the Bollinger(20, 2.0) band (bb block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | bb (period, k) - backtest/signals/technical.py bb block | BRACKET canon k | (20, 2.0) | k [1.5, 2.0, 2.5]; period [20] | none - bands at other k unpersisted for the touch | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | hammer - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | canonical single/two-candle reversal pattern (Nison; compute_candle_signals - geometry in producer) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | implicit anatomy knobs (min body/wick/step pct) - backtest/signals/technical.py:candle block (compute_candle_signals) | CANON candle anatomy (Nison); production accepts any magnitude | 0 / absent (any magnitude counts) | [0, 0.3, 0.5] per knob | none - pattern bars' OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | near_s1 - emitted by backtest/signals/screener.py +2; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | proximity tolerance to S1 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | PRODUCER | near_s2 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P4.x) | BANDS-DEFINED |
| P4.1 | BAND | proximity tolerance to S2 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | STRATEGY | rsi_14 `< 35` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `< 35` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P5.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `< 35` | 100.0% | TIGHTER = LOWER the ceiling: 25.566 -> 22 (20%); 28.634 -> 44 (40%); 30.838 -> 66 (60%); 33.212 -> 88 (80%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 20.446, 24.614, 29.04, 33.598 | 20.446: 88 (80%); 24.614: 66 (60%); 29.04: 44 (40%); 33.598: 22 (20%) | 20.446: 22 (20%); 24.614: 44 (40%); 29.04: 66 (60%); 33.598: 88 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 34.222, 37.574, 41.338, 44.318 | 34.222: 88 (80%); 37.574: 66 (60%); 41.338: 44 (40%); 44.318: 22 (20%) | 34.222: 22 (20%); 37.574: 44 (40%); 41.338: 66 (60%); 44.318: 88 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 10.018, 11.934, 13.396, 15.564 | 10.018: 88 (80%); 11.934: 66 (60%); 13.396: 44 (40%); 15.564: 22 (20%) | 10.018: 22 (20%); 11.934: 44 (40%); 13.396: 66 (60%); 15.564: 88 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -12.1255, -6.9908, -4.8141, -2.577 | -12.1255: 88 (80%); -6.9908: 66 (60%); -4.8141: 44 (40%); -2.577: 22 (20%) | -12.1255: 22 (20%); -6.9908: 44 (40%); -4.8141: 66 (60%); -2.577: 88 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.2768, 1.981, 3.4852, 5.6057 | 1.2768: 88 (80%); 1.981: 66 (60%); 3.4852: 44 (40%); 5.6057: 22 (20%) | 1.2768: 22 (20%); 1.981: 44 (40%); 3.4852: 66 (60%); 5.6057: 88 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.2768, 1.981, 3.4852, 5.6057 | 1.2768: 88 (80%); 1.981: 66 (60%); 3.4852: 44 (40%); 5.6057: 22 (20%) | 1.2768: 22 (20%); 1.981: 44 (40%); 3.4852: 66 (60%); 5.6057: 88 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.3932, 2.9396, 3.4438, 4.3696 | 2.3932: 88 (80%); 2.9396: 66 (60%); 3.4438: 44 (40%); 4.3696: 22 (20%) | 2.3932: 22 (20%); 2.9396: 44 (40%); 3.4438: 66 (60%); 4.3696: 88 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0929, 0.1454, 0.1891, 0.2305 | 0.0929: 88 (80%); 0.1454: 66 (60%); 0.1891: 44 (40%); 0.2305: 22 (20%) | 0.0929: 22 (20%); 0.1454: 44 (40%); 0.1891: 66 (60%); 0.2305: 88 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.0628, 0.1073, 0.1384, 0.1694 | 0.0628: 88 (80%); 0.1073: 66 (60%); 0.1384: 44 (40%); 0.1694: 22 (20%) | 0.0628: 22 (20%); 0.1073: 44 (40%); 0.1384: 66 (60%); 0.1694: 88 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0837, 0.1139, 0.1303, 0.1629 | 0.0837: 88 (80%); 0.1139: 66 (60%); 0.1303: 44 (40%); 0.1629: 22 (20%) | 0.0837: 22 (20%); 0.1139: 44 (40%); 0.1303: 66 (60%); 0.1629: 88 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.2814, -0.2083, -0.1768, -0.126 | -0.2814: 88 (80%); -0.2083: 66 (60%); -0.1768: 44 (40%); -0.126: 22 (20%) | -0.2814: 22 (20%); -0.2083: 44 (40%); -0.1768: 66 (60%); -0.126: 88 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.1116, 0.152, 0.1737, 0.2172 | 0.1116: 88 (80%); 0.152: 66 (60%); 0.1737: 44 (40%); 0.2172: 22 (20%) | 0.1116: 22 (20%); 0.152: 44 (40%); 0.1737: 66 (60%); 0.2172: 88 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | -0.0861, -0.0313, -0.0075, 0.0305 | -0.0861: 88 (80%); -0.0313: 66 (60%); -0.0075: 44 (40%); 0.0305: 22 (20%) | -0.0861: 22 (20%); -0.0313: 44 (40%); -0.0075: 66 (60%); 0.0305: 88 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0325, -0.0085, 0.0191, 0.0686 | -0.0325: 88 (80%); -0.0085: 66 (60%); 0.0191: 46 (42%); 0.0686: 25 (23%) | -0.0325: 22 (20%); -0.0085: 44 (40%); 0.0191: 69 (63%); 0.0686: 94 (85%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1365, 0.175, 0.2105, 0.2762 | 0.1365: 88 (80%); 0.175: 66 (60%); 0.2105: 44 (40%); 0.2762: 24 (22%) | 0.1365: 22 (20%); 0.175: 44 (40%); 0.2105: 66 (60%); 0.2762: 86 (78%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 110 (100%) | 0: 109 (99%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1761, -0.1073, -0.0185, 0.0385 | -0.1761: 88 (80%); -0.1073: 66 (60%); -0.0185: 44 (40%); 0.0385: 22 (20%) | -0.1761: 22 (20%); -0.1073: 44 (40%); -0.0185: 66 (60%); 0.0385: 88 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 2 | 0: 110 (100%); 2: 25 (23%) | 0: 68 (62%); 2: 104 (95%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2334, -0.1934, -0.1443, -0.1109 | -0.2334: 89 (81%); -0.1934: 66 (60%); -0.1443: 44 (40%); -0.1109: 28 (25%) | -0.2334: 23 (21%); -0.1934: 44 (40%); -0.1443: 66 (60%); -0.1109: 91 (83%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2116, 0.6102, 0.7372, 0.8013 | 0.2116: 88 (80%); 0.6102: 66 (60%); 0.7372: 46 (42%); 0.8013: 23 (21%) | 0.2116: 22 (20%); 0.6102: 44 (40%); 0.7372: 68 (62%); 0.8013: 91 (83%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2102, 0.3141, 0.6526, 0.8654 | 0.2102: 88 (80%); 0.3141: 70 (64%); 0.6526: 44 (40%); 0.8654: 23 (21%) | 0.2102: 22 (20%); 0.3141: 51 (46%); 0.6526: 66 (60%); 0.8654: 91 (83%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0561, 0.0117, 0.0997, 0.1975 | -0.0561: 89 (81%); 0.0117: 70 (64%); 0.0997: 45 (41%); 0.1975: 22 (20%) | -0.0561: 23 (21%); 0.0117: 46 (42%); 0.0997: 67 (61%); 0.1975: 88 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3423, 0.5385, 0.659, 0.7885 | 0.3423: 88 (80%); 0.5385: 70 (64%); 0.659: 44 (40%); 0.7885: 24 (22%) | 0.3423: 22 (20%); 0.5385: 46 (42%); 0.659: 66 (60%); 0.7885: 89 (81%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0795, 0.2564, 0.4436, 0.5962 | 0.0795: 88 (80%); 0.2564: 67 (61%); 0.4436: 44 (40%); 0.5962: 25 (23%) | 0.0795: 22 (20%); 0.2564: 47 (43%); 0.4436: 66 (60%); 0.5962: 91 (83%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5101, -0.3583, -0.1519, 0.0839 | -0.5101: 89 (81%); -0.3583: 66 (60%); -0.1519: 44 (40%); 0.0839: 26 (24%) | -0.5101: 23 (21%); -0.3583: 44 (40%); -0.1519: 66 (60%); 0.0839: 90 (82%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3064, 0.5321, 0.6923, 0.9167 | 0.3064: 88 (80%); 0.5321: 71 (65%); 0.6923: 45 (41%); 0.9167: 23 (21%) | 0.3064: 22 (20%); 0.5321: 49 (45%); 0.6923: 68 (62%); 0.9167: 91 (83%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0962, 0.2885, 0.5833, 0.7257 | 0.0962: 90 (82%); 0.2885: 67 (61%); 0.5833: 45 (41%); 0.7257: 22 (20%) | 0.0962: 29 (26%); 0.2885: 45 (41%); 0.5833: 67 (61%); 0.7257: 88 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0635, -0.0419, -0.0291, 0 | -0.0635: 88 (80%); -0.0419: 67 (61%); -0.0291: 45 (41%); 0: 32 (29%) | -0.0635: 22 (20%); -0.0419: 46 (42%); -0.0291: 74 (67%); 0: 108 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4679, 0.7538, 0.9103, 1 | 0.4679: 93 (85%); 0.7538: 66 (60%); 0.9103: 46 (42%); 1: 28 (25%) | 0.4679: 23 (21%); 0.7538: 44 (40%); 0.9103: 77 (70%); 1: 110 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0321, 0.1859, 0.477, 0.609 | 0.0321: 91 (83%); 0.1859: 67 (61%); 0.477: 44 (40%); 0.609: 29 (26%) | 0.0321: 23 (21%); 0.1859: 45 (41%); 0.477: 66 (60%); 0.609: 89 (81%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0136, 0.0302, 0.0848, 0.2045 | -0.0136: 88 (80%); 0.0302: 66 (60%); 0.0848: 48 (44%); 0.2045: 23 (21%) | -0.0136: 23 (21%); 0.0302: 44 (40%); 0.0848: 67 (61%); 0.2045: 89 (81%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5155, 0.7624, 0.9193, 0.9692 | 0.5155: 94 (85%); 0.7624: 66 (60%); 0.9193: 44 (40%); 0.9692: 22 (20%) | 0.5155: 25 (23%); 0.7624: 44 (40%); 0.9193: 66 (60%); 0.9692: 88 (80%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1208, 0.2373, 0.3928, 0.6389 | 0.1208: 88 (80%); 0.2373: 66 (60%); 0.3928: 44 (40%); 0.6389: 22 (20%) | 0.1208: 22 (20%); 0.2373: 44 (40%); 0.3928: 66 (60%); 0.6389: 88 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0264, 0.0599, 0.1338, 0.3175 | -0.0264: 88 (80%); 0.0599: 66 (60%); 0.1338: 45 (41%); 0.3175: 25 (23%) | -0.0264: 22 (20%); 0.0599: 44 (40%); 0.1338: 68 (62%); 0.3175: 105 (95%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1561, 0.0141, 0.0497, 0.1218 | -0.1561: 88 (80%); 0.0141: 68 (62%); 0.0497: 44 (40%); 0.1218: 22 (20%) | -0.1561: 22 (20%); 0.0141: 46 (42%); 0.0497: 66 (60%); 0.1218: 88 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3961, 0.5846, 0.7436, 0.9692 | 0.3961: 88 (80%); 0.5846: 66 (60%); 0.7436: 45 (41%); 0.9692: 22 (20%) | 0.3961: 22 (20%); 0.5846: 44 (40%); 0.7436: 67 (61%); 0.9692: 88 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1474, 0.2115, 0.4564, 0.7436 | 0.1474: 91 (83%); 0.2115: 71 (65%); 0.4564: 44 (40%); 0.7436: 24 (22%) | 0.1474: 23 (21%); 0.2115: 46 (42%); 0.4564: 66 (60%); 0.7436: 89 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0789, 0.1602, 0.3285, 0.7562 | 0.0789: 88 (80%); 0.1602: 66 (60%); 0.3285: 44 (40%); 0.7562: 22 (20%) | 0.0789: 22 (20%); 0.1602: 44 (40%); 0.3285: 66 (60%); 0.7562: 88 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 100.0% | 32.4, 61.8, 88.4, 137.6 | 32.4: 88 (80%); 61.8: 66 (60%); 88.4: 44 (40%); 137.6: 22 (20%) | 32.4: 22 (20%); 61.8: 44 (40%); 88.4: 66 (60%); 137.6: 88 (80%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 100.0% | 1.7334, 2.3739, 2.8995, 3.8148 | 1.7334: 88 (80%); 2.3739: 66 (60%); 2.8995: 44 (40%); 3.8148: 22 (20%) | 1.7334: 22 (20%); 2.3739: 44 (40%); 2.8995: 66 (60%); 3.8148: 88 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 8, 20, 31.2, 40 | 8: 90 (82%); 20: 67 (61%); 31.2: 44 (40%); 40: 30 (27%) | 8: 23 (21%); 20: 46 (42%); 31.2: 66 (60%); 40: 96 (87%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3, 4 | 1: 90 (82%); 2: 75 (68%); 3: 58 (53%); 4: 37 (34%) | 1: 35 (32%); 2: 52 (47%); 3: 73 (66%); 4: 110 (100%) | OFFLINE |
| dpi_30d_avg | backtest/signals/congressional_alt_data.py | 99.1% | 0.4, 0.4671, 0.5271, 0.5613 | 0.4: 87 (79%); 0.4671: 65 (59%); 0.5271: 44 (40%); 0.5613: 22 (20%) | 0.4: 22 (20%); 0.4671: 44 (40%); 0.5271: 65 (59%); 0.5613: 87 (79%) | OFFLINE |
| dpi_recent | backtest/signals/congressional_alt_data.py | 99.1% | 0.3457, 0.4497, 0.5133, 0.6206 | 0.3457: 87 (79%); 0.4497: 65 (59%); 0.5133: 44 (40%); 0.6206: 22 (20%) | 0.3457: 22 (20%); 0.4497: 44 (40%); 0.5133: 65 (59%); 0.6206: 87 (79%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0053, 0.01, 0.018, 0.0262 | -0.0053: 88 (80%); 0.01: 66 (60%); 0.018: 44 (40%); 0.0262: 23 (21%) | -0.0053: 22 (20%); 0.01: 44 (40%); 0.018: 66 (60%); 0.0262: 88 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.9792, 25.9863, 26.6331, 27.3267 | 24.9792: 88 (80%); 25.9863: 66 (60%); 26.6331: 44 (40%); 27.3267: 23 (21%) | 24.9792: 22 (20%); 25.9863: 44 (40%); 26.6331: 66 (60%); 27.3267: 93 (85%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | 0, 0.6874, 1.3818, 2.93 | 0: 90 (82%); 0.6874: 66 (60%); 1.3818: 44 (40%); 2.93: 22 (20%) | 0: 23 (21%); 0.6874: 44 (40%); 1.3818: 66 (60%); 2.93: 88 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -2.93, -1.3818, -0.6874, 0 | -2.93: 88 (80%); -1.3818: 66 (60%); -0.6874: 44 (40%); 0: 23 (21%) | -2.93: 22 (20%); -1.3818: 44 (40%); -0.6874: 66 (60%); 0: 90 (82%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0467, -0.0186, 0.0193, 0.0533 | -0.0467: 89 (81%); -0.0186: 67 (61%); 0.0193: 44 (40%); 0.0533: 22 (20%) | -0.0467: 23 (21%); -0.0186: 45 (41%); 0.0193: 66 (60%); 0.0533: 88 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.9889, 8.5263, 8.7811, 9.0109 | 7.9889: 88 (80%); 8.5263: 66 (60%); 8.7811: 44 (40%); 9.0109: 22 (20%) | 7.9889: 22 (20%); 8.5263: 44 (40%); 8.7811: 66 (60%); 9.0109: 88 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 1 | 0: 110 (100%); 1: 37 (34%) | 0: 73 (66%); 1: 96 (87%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0 | 0: 90 (82%) | 0: 89 (81%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 1 | 0: 110 (100%); 1: 40 (36%) | 0: 70 (64%); 1: 102 (93%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 6, 154.4, 224.4 | 2: 91 (83%); 6: 69 (63%); 154.4: 44 (40%); 224.4: 22 (20%) | 2: 23 (21%); 6: 47 (43%); 154.4: 66 (60%); 224.4: 88 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 0, 4, 82, 132.4 | 0: 110 (100%); 4: 67 (61%); 82: 45 (41%); 132.4: 22 (20%) | 0: 24 (22%); 4: 46 (42%); 82: 67 (61%); 132.4: 88 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -1.9116, -0.9848, -0.574, -0.2051 | -1.9116: 88 (80%); -0.9848: 66 (60%); -0.574: 44 (40%); -0.2051: 22 (20%) | -1.9116: 22 (20%); -0.9848: 44 (40%); -0.574: 66 (60%); -0.2051: 88 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -4.4356, -2.5081, -1.8366, -0.8575 | -4.4356: 88 (80%); -2.5081: 66 (60%); -1.8366: 44 (40%); -0.8575: 22 (20%) | -4.4356: 22 (20%); -2.5081: 44 (40%); -1.8366: 66 (60%); -0.8575: 88 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -2.628, -1.6957, -1.0087, -0.2828 | -2.628: 88 (80%); -1.6957: 66 (60%); -1.0087: 44 (40%); -0.2828: 22 (20%) | -2.628: 22 (20%); -1.6957: 44 (40%); -1.0087: 66 (60%); -0.2828: 88 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -1.7137, -0.9057, -0.4573, -0.1806 | -1.7137: 88 (80%); -0.9057: 66 (60%); -0.4573: 44 (40%); -0.1806: 22 (20%) | -1.7137: 22 (20%); -0.9057: 44 (40%); -0.4573: 66 (60%); -0.1806: 88 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -5.7198, -3.4404, -2.2308, -1.2482 | -5.7198: 88 (80%); -3.4404: 66 (60%); -2.2308: 44 (40%); -1.2482: 22 (20%) | -5.7198: 22 (20%); -3.4404: 44 (40%); -2.2308: 66 (60%); -1.2482: 88 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -4.4224, -2.4031, -1.6833, -0.8153 | -4.4224: 88 (80%); -2.4031: 66 (60%); -1.6833: 44 (40%); -0.8153: 22 (20%) | -4.4224: 22 (20%); -2.4031: 44 (40%); -1.6833: 66 (60%); -0.8153: 88 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 21.394, 26.698, 31.308, 37.818 | 21.394: 88 (80%); 26.698: 66 (60%); 31.308: 44 (40%); 37.818: 22 (20%) | 21.394: 22 (20%); 26.698: 44 (40%); 31.308: 66 (60%); 37.818: 88 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 99.1% | -0.2597, -0.1809, -0.0875, 0.0172 | -0.2597: 87 (79%); -0.1809: 65 (59%); -0.0875: 44 (40%); 0.0172: 22 (20%) | -0.2597: 22 (20%); -0.1809: 44 (40%); -0.0875: 65 (59%); 0.0172: 87 (79%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 100.0% | 0.0133, 0.0322, 0.064, 0.1062 | 0.0133: 88 (80%); 0.0322: 66 (60%); 0.064: 44 (40%); 0.1062: 23 (21%) | 0.0133: 22 (20%); 0.0322: 44 (40%); 0.064: 66 (60%); 0.1062: 87 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 1, 2, 4, 13.2 | 1: 91 (83%); 2: 73 (66%); 4: 52 (47%); 13.2: 22 (20%) | 1: 37 (34%); 2: 54 (49%); 4: 67 (61%); 13.2: 88 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1504, 0.3333 | 0: 110 (100%); 0.1504: 44 (40%); 0.3333: 25 (23%) | 0: 57 (52%); 0.1504: 66 (60%); 0.3333: 89 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0639, 0.375, 0.5 | 0: 110 (100%); 0.0639: 66 (60%); 0.375: 45 (41%); 0.5: 29 (26%) | 0: 42 (38%); 0.0639: 44 (40%); 0.375: 68 (62%); 0.5: 91 (83%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 4, 9.2 | 0: 110 (100%); 1: 83 (75%); 4: 45 (41%); 9.2: 22 (20%) | 0: 27 (25%); 1: 49 (45%); 4: 73 (66%); 9.2: 88 (80%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 1, 2, 4, 13.2 | 1: 91 (83%); 2: 73 (66%); 4: 52 (47%); 13.2: 22 (20%) | 1: 37 (34%); 2: 54 (49%); 4: 67 (61%); 13.2: 88 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 6.2 | 0: 110 (100%); 1: 75 (68%); 3: 49 (45%); 6.2: 22 (20%) | 0: 35 (32%); 1: 50 (45%); 3: 67 (61%); 6.2: 88 (80%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1419, 0.292, 0.5479 | 0: 94 (85%); 0.1419: 66 (60%); 0.292: 44 (40%); 0.5479: 22 (20%) | 0: 26 (24%); 0.1419: 44 (40%); 0.292: 66 (60%); 0.5479: 88 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.0942, 0, 0.0036, 0.4033 | -0.0942: 88 (80%); 0: 82 (75%); 0.0036: 44 (40%); 0.4033: 22 (20%) | -0.0942: 22 (20%); 0: 66 (60%); 0.0036: 66 (60%); 0.4033: 88 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | -0.0171, 0, 0.1282, 0.5 | -0.0171: 88 (80%); 0: 87 (79%); 0.1282: 44 (40%); 0.5: 23 (21%) | -0.0171: 22 (20%); 0: 58 (53%); 0.1282: 66 (60%); 0.5: 91 (83%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | -0.0171, 0, 0.1282, 0.5 | -0.0171: 88 (80%); 0: 87 (79%); 0.1282: 44 (40%); 0.5: 23 (21%) | -0.0171: 22 (20%); 0: 58 (53%); 0.1282: 66 (60%); 0.5: 91 (83%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.2906, 0, 0.0102 | -0.2906: 88 (80%); 0: 70 (64%); 0.0102: 22 (20%) | -0.2906: 22 (20%); 0: 87 (79%); 0.0102: 88 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.6461, 0, 0.5394, 2.7057 | -0.6461: 92 (84%); 0: 68 (62%); 0.5394: 49 (45%); 2.7057: 22 (20%) | -0.6461: 23 (21%); 0: 54 (49%); 0.5394: 67 (61%); 2.7057: 88 (80%) | OFFLINE |
| otc_short_ratio_recent | backtest/signals/congressional_alt_data.py | 99.1% | 0.3457, 0.4497, 0.5133, 0.6206 | 0.3457: 87 (79%); 0.4497: 65 (59%); 0.5133: 44 (40%); 0.6206: 22 (20%) | 0.3457: 22 (20%); 0.4497: 44 (40%); 0.5133: 65 (59%); 0.6206: 87 (79%) | OFFLINE |
| otc_volume_recent | backtest/signals/congressional_alt_data.py | 99.1% | 449156.8, 968076.8, 1925186, 4983368.6 | 449156.8: 87 (79%); 968076.8: 65 (59%); 1925186: 44 (40%); 4983368.6: 22 (20%) | 449156.8: 22 (20%); 968076.8: 44 (40%); 1925186: 65 (59%); 4983368.6: 87 (79%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 1.8, 4, 6, 10 | 1.8: 88 (80%); 4: 68 (62%); 6: 49 (45%); 10: 24 (22%) | 1.8: 22 (20%); 4: 52 (47%); 6: 70 (64%); 10: 94 (85%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.1362, -0.1115, -0.088, -0.0558 | -0.1362: 88 (80%); -0.1115: 66 (60%); -0.088: 44 (40%); -0.0558: 22 (20%) | -0.1362: 22 (20%); -0.1115: 44 (40%); -0.088: 66 (60%); -0.0558: 88 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.1709, -0.1271, -0.1017, -0.0824 | -0.1709: 88 (80%); -0.1271: 66 (60%); -0.1017: 44 (40%); -0.0824: 22 (20%) | -0.1709: 22 (20%); -0.1271: 44 (40%); -0.1017: 66 (60%); -0.0824: 88 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.1103, -0.0915, -0.066, -0.0385 | -0.1103: 88 (80%); -0.0915: 66 (60%); -0.066: 44 (40%); -0.0385: 22 (20%) | -0.1103: 22 (20%); -0.0915: 44 (40%); -0.066: 66 (60%); -0.0385: 88 (80%) | OFFLINE |
| pct_from_avwap_20high | backtest/signals/screener.py | 100.0% | -9.4368, -7.337, -5.954, -4.8308 | -9.4368: 88 (80%); -7.337: 66 (60%); -5.954: 44 (40%); -4.8308: 22 (20%) | -9.4368: 22 (20%); -7.337: 44 (40%); -5.954: 66 (60%); -4.8308: 88 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -31.299, -19.3618, -7.7568, 2.186 | -31.299: 88 (80%); -19.3618: 66 (60%); -7.7568: 44 (40%); 2.186: 22 (20%) | -31.299: 22 (20%); -19.3618: 44 (40%); -7.7568: 66 (60%); 2.186: 88 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0577, 0.0815, 0.1062, 0.1365 | 0.0577: 88 (80%); 0.0815: 67 (61%); 0.1062: 44 (40%); 0.1365: 22 (20%) | 0.0577: 22 (20%); 0.0815: 45 (41%); 0.1062: 66 (60%); 0.1365: 88 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.8572, 0.8921, 0.9303, 0.9666 | 0.8572: 88 (80%); 0.8921: 66 (60%); 0.9303: 44 (40%); 0.9666: 22 (20%) | 0.8572: 22 (20%); 0.8921: 44 (40%); 0.9303: 66 (60%); 0.9666: 88 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -4.0522, -2.6412, -2.0934, -1.5335 | -4.0522: 88 (80%); -2.6412: 66 (60%); -2.0934: 44 (40%); -1.5335: 22 (20%) | -4.0522: 22 (20%); -2.6412: 44 (40%); -2.0934: 66 (60%); -1.5335: 88 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -1.4161, -1.1144, -0.8492, -0.4815 | -1.4161: 88 (80%); -1.1144: 66 (60%); -0.8492: 44 (40%); -0.4815: 22 (20%) | -1.4161: 22 (20%); -1.1144: 44 (40%); -0.8492: 66 (60%); -0.4815: 88 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -2.9143, -1.7642, -1.0928, -0.4587 | -2.9143: 88 (80%); -1.7642: 66 (60%); -1.0928: 44 (40%); -0.4587: 22 (20%) | -2.9143: 22 (20%); -1.7642: 44 (40%); -1.0928: 66 (60%); -0.4587: 88 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -14.5082, -11.614, -9.1882, -6.2958 | -14.5082: 88 (80%); -11.614: 66 (60%); -9.1882: 44 (40%); -6.2958: 22 (20%) | -14.5082: 22 (20%); -11.614: 44 (40%); -9.1882: 66 (60%); -6.2958: 88 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 2.17, 6.63, 13.476, 20.118 | 2.17: 88 (80%); 6.63: 66 (60%); 13.476: 44 (40%); 20.118: 22 (20%) | 2.17: 22 (20%); 6.63: 44 (40%); 13.476: 66 (60%); 20.118: 88 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 30.632, 32.836, 35.498, 37.668 | 30.632: 88 (80%); 32.836: 66 (60%); 35.498: 44 (40%); 37.668: 22 (20%) | 30.632: 22 (20%); 32.836: 44 (40%); 35.498: 66 (60%); 37.668: 88 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 20.55, 22.99, 25.096, 28.43 | 20.55: 88 (80%); 22.99: 67 (61%); 25.096: 44 (40%); 28.43: 22 (20%) | 20.55: 22 (20%); 22.99: 45 (41%); 25.096: 66 (60%); 28.43: 88 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0318, 0.0486, 0.0602, 0.0869 | 0.0318: 88 (80%); 0.0486: 66 (60%); 0.0602: 51 (46%); 0.0869: 25 (23%) | 0.0318: 22 (20%); 0.0486: 44 (40%); 0.0602: 68 (62%); 0.0869: 91 (83%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0708, -0.0487, -0.0429, -0.0359 | -0.0708: 88 (80%); -0.0487: 66 (60%); -0.0429: 49 (45%); -0.0359: 23 (21%) | -0.0708: 22 (20%); -0.0487: 44 (40%); -0.0429: 67 (61%); -0.0359: 88 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 110 (100%); 1: 23 (21%) | 0: 87 (79%); 1: 95 (86%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 100.0% | 23, 40, 57.2, 72 | 23: 99 (90%); 40: 67 (61%); 57.2: 44 (40%); 72: 23 (21%) | 23: 24 (22%); 40: 45 (41%); 57.2: 66 (60%); 72: 89 (81%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.0715, 0.0961, 0.123, 0.1801 | 0.0715: 88 (80%); 0.0961: 66 (60%); 0.123: 44 (40%); 0.1801: 22 (20%) | 0.0715: 23 (21%); 0.0961: 44 (40%); 0.123: 66 (60%); 0.1801: 88 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 19.36, 82.6, 109.3, 161.34 | 19.36: 88 (80%); 82.6: 66 (60%); 109.3: 44 (40%); 161.34: 22 (20%) | 19.36: 22 (20%); 82.6: 44 (40%); 109.3: 66 (60%); 161.34: 88 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -11.173, -6.565, -4.1935, -2.054 | -11.173: 88 (80%); -6.565: 67 (61%); -4.1935: 44 (40%); -2.054: 22 (20%) | -11.173: 22 (20%); -6.565: 45 (41%); -4.1935: 66 (60%); -2.054: 88 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 7.418, 10.088, 15.076, 23.528 | 7.418: 88 (80%); 10.088: 66 (60%); 15.076: 44 (40%); 23.528: 22 (20%) | 7.418: 22 (20%); 10.088: 44 (40%); 15.076: 66 (60%); 23.528: 88 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 6.104, 9.118, 13.22, 19.46 | 6.104: 88 (80%); 9.118: 66 (60%); 13.22: 44 (40%); 19.46: 22 (20%) | 6.104: 22 (20%); 9.118: 44 (40%); 13.22: 66 (60%); 19.46: 88 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 0.96, 10.654, 22.228, 42.612 | 0.96: 88 (80%); 10.654: 66 (60%); 22.228: 44 (40%); 42.612: 22 (20%) | 0.96: 22 (20%); 10.654: 44 (40%); 22.228: 66 (60%); 42.612: 88 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 1.336, 14.532, 28.994 | 0: 110 (100%); 1.336: 66 (60%); 14.532: 44 (40%); 28.994: 22 (20%) | 0: 40 (36%); 1.336: 44 (40%); 14.532: 66 (60%); 28.994: 88 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 6.6, 11, 16 | 4: 92 (84%); 6.6: 66 (60%); 11: 50 (45%); 16: 24 (22%) | 4: 26 (24%); 6.6: 44 (40%); 11: 71 (65%); 16: 102 (93%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 7, 11, 15.4, 18 | 7: 90 (82%); 11: 68 (62%); 15.4: 44 (40%); 18: 32 (29%) | 7: 28 (25%); 11: 47 (43%); 15.4: 66 (60%); 18: 97 (88%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 33.5, 37.436, 40.538, 44.44 | 33.5: 89 (81%); 37.436: 66 (60%); 40.538: 44 (40%); 44.44: 22 (20%) | 33.5: 23 (21%); 37.436: 44 (40%); 40.538: 66 (60%); 44.44: 88 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.2945, 0.5635, 0.6905, 0.8738 | 0.2945: 88 (80%); 0.5635: 67 (61%); 0.6905: 45 (41%); 0.8738: 22 (20%) | 0.2945: 22 (20%); 0.5635: 46 (42%); 0.6905: 69 (63%); 0.8738: 88 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 16.038, 18.28, 24.02, 29.49 | 16.038: 88 (80%); 18.28: 66 (60%); 24.02: 44 (40%); 29.49: 24 (22%) | 16.038: 22 (20%); 18.28: 44 (40%); 24.02: 66 (60%); 29.49: 91 (83%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 16.038, 18.28, 24.02, 29.49 | 16.038: 88 (80%); 18.28: 66 (60%); 24.02: 44 (40%); 29.49: 24 (22%) | 16.038: 22 (20%); 18.28: 44 (40%); 24.02: 66 (60%); 29.49: 91 (83%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8793, 0.9084, 0.9519, 0.9868 | 0.8793: 88 (80%); 0.9084: 66 (60%); 0.9519: 45 (41%); 0.9868: 26 (24%) | 0.8793: 22 (20%); 0.9084: 44 (40%); 0.9519: 67 (61%); 0.9868: 93 (85%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.996, 1.14, 1.444, 1.998 | 0.996: 88 (80%); 1.14: 67 (61%); 1.444: 44 (40%); 1.998: 22 (20%) | 0.996: 22 (20%); 1.14: 45 (41%); 1.444: 66 (60%); 1.998: 88 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0639, 0.0906, 0.1134, 0.1617 | 0.0639: 88 (80%); 0.0906: 66 (60%); 0.1134: 44 (40%); 0.1617: 22 (20%) | 0.0639: 22 (20%); 0.0906: 44 (40%); 0.1134: 66 (60%); 0.1617: 88 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 47.1278, 75.6433, 121.2383, 208.3235 | 47.1278: 88 (80%); 75.6433: 66 (60%); 121.2383: 44 (40%); 208.3235: 22 (20%) | 47.1278: 22 (20%); 75.6433: 44 (40%); 121.2383: 66 (60%); 208.3235: 88 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 44.8794, 71.8329, 113.7424, 201.7763 | 44.8794: 88 (80%); 71.8329: 66 (60%); 113.7424: 44 (40%); 201.7763: 22 (20%) | 44.8794: 22 (20%); 71.8329: 44 (40%); 113.7424: 66 (60%); 201.7763: 88 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 42.3649, 68.0263, 107.9668, 195.2291 | 42.3649: 88 (80%); 68.0263: 66 (60%); 107.9668: 44 (40%); 195.2291: 22 (20%) | 42.3649: 22 (20%); 68.0263: 44 (40%); 107.9668: 66 (60%); 195.2291: 88 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 110 (100%) | 0: 96 (87%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 110 (100%) | 0: 104 (95%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.1606, -0.1235, -0.096, -0.074 | -0.1606: 88 (80%); -0.1235: 66 (60%); -0.096: 44 (40%); -0.074: 22 (20%) | -0.1606: 22 (20%); -0.1235: 44 (40%); -0.096: 66 (60%); -0.074: 88 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -89.188, -87.13, -82.732, -77.884 | -89.188: 88 (80%); -87.13: 66 (60%); -82.732: 44 (40%); -77.884: 22 (20%) | -89.188: 22 (20%); -87.13: 44 (40%); -82.732: 66 (60%); -77.884: 88 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 100.0% | 0.5098, 0.7406, 1.031, 1.2652 | 0.5098: 88 (80%); 0.7406: 66 (60%); 1.031: 44 (40%); 1.2652: 22 (20%) | 0.5098: 22 (20%); 0.7406: 44 (40%); 1.031: 66 (60%); 1.2652: 88 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 100.0% | 2.8, 4, 7, 8.2 | 2.8: 88 (80%); 4: 76 (69%); 7: 49 (45%); 8.2: 22 (20%) | 2.8: 22 (20%); 4: 46 (42%); 7: 74 (67%); 8.2: 88 (80%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 100.0% | 0.2027, 0.2413, 0.2712, 0.352 | 0.2027: 88 (80%); 0.2413: 66 (60%); 0.2712: 44 (40%); 0.352: 22 (20%) | 0.2027: 22 (20%); 0.2413: 44 (40%); 0.2712: 66 (60%); 0.352: 88 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 100.0% | 4, 6, 7.4, 9 | 4: 97 (88%); 6: 75 (68%); 7.4: 44 (40%); 9: 31 (28%) | 4: 26 (24%); 6: 48 (44%); 7.4: 66 (60%); 9: 94 (85%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 100.0% | 0.0173, 0.0223, 0.0289, 0.0399 | 0.0173: 88 (80%); 0.0223: 66 (60%); 0.0289: 45 (41%); 0.0399: 22 (20%) | 0.0173: 22 (20%); 0.0223: 44 (40%); 0.0289: 67 (61%); 0.0399: 88 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 100.0% | 2, 3, 5, 7 | 2: 90 (82%); 3: 76 (69%); 5: 48 (44%); 7: 28 (25%) | 2: 34 (31%); 3: 50 (45%); 5: 75 (68%); 7: 91 (83%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 100.0% | -0.191, -0.0763, 0.0166, 0.1641 | -0.191: 88 (80%); -0.0763: 66 (60%); 0.0166: 44 (40%); 0.1641: 22 (20%) | -0.191: 22 (20%); -0.0763: 44 (40%); 0.0166: 66 (60%); 0.1641: 88 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 100.0% | 2, 4, 5, 7.2 | 2: 92 (84%); 4: 69 (63%); 5: 54 (49%); 7.2: 22 (20%) | 2: 27 (25%); 4: 56 (51%); 5: 67 (61%); 7.2: 88 (80%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 7.5% |
| 8k_item_5_02_filed_within_7d | 1.9% |
| above_avwap_20low | 96.4% |
| above_avwap_252low | 49.5% |
| above_avwap_50low | 84.5% |
| above_cam_r3 | 4.5% |
| above_cpr | 8.2% |
| above_pivot | 13.6% |
| above_prev_low | 48.2% |
| above_vwap | 23.6% |
| above_wood_p | 3.6% |
| ad_rising | 36.4% |
| adx_cross_up | 6.4% |
| adx_cross_up_20 | 10.0% |
| adx_strong | 9.1% |
| adx_trending | 58.2% |
| ao_cross_dn | 2.7% |
| at_key_fib | 0.9% |
| at_key_fib_wide | 1.8% |
| avwap_20high_loss_recent_3d | 10.0% |
| avwap_20low_loss_recent_3d | 6.7% |
| avwap_20low_reclaim_recent_3d | 40.0% |
| avwap_252low_loss_recent_3d | 21.1% |
| avwap_252low_reclaim_recent_3d | 3.9% |
| avwap_50low_loss_recent_3d | 14.8% |
| avwap_50low_reclaim_recent_3d | 22.2% |
| bb_10_20_expanding | 87.3% |
| bb_10_20_pctb_lt_05 | 15.5% |
| bb_10_20_pctb_lt_1 | 36.4% |
| bb_10_20_pctb_lt_15 | 65.5% |
| bb_10_20_pctb_lt_2 | 93.6% |
| bb_10_20_pctb_lt_25 | 96.4% |
| bb_10_20_reclaim_from_lower_recent_3d | 51.8% |
| bb_10_20_squeeze | 13.6% |
| bb_10_20_touch_lower | 14.5% |
| bb_20_15_expanding | 90.0% |
| bb_20_15_pctb_lt_05 | 93.6% |
| bb_20_15_pctb_lt_1 | 97.3% |
| bb_20_15_pctb_lt_15 | 98.2% |
| bb_20_15_pctb_lt_2 | 99.1% |
| bb_20_15_reclaim_from_lower_recent_3d | 2.7% |
| bb_20_15_squeeze | 17.3% |
| bb_20_15_touch_lower | 93.6% |
| bb_20_20_expanding | 90.0% |
| bb_20_20_pctb_lt_05 | 87.3% |
| bb_20_20_pctb_lt_1 | 90.9% |
| bb_20_20_pctb_lt_15 | 93.6% |
| bb_20_20_pctb_lt_2 | 97.3% |
| bb_20_20_pctb_lt_25 | 98.2% |
| bb_20_20_reclaim_from_lower_recent_3d | 19.1% |
| bb_20_20_squeeze | 7.3% |
| bb_20_20_touch_lower | 83.6% |
| below_avwap_20low | 3.6% |
| below_avwap_252low | 50.5% |
| below_avwap_50low | 15.5% |
| below_cam_s3 | 35.5% |
| below_cam_s4 | 18.2% |
| below_cpr | 86.4% |
| below_ema_200 | 90.9% |
| below_ema_200_break_recent_5d | 21.8% |
| below_ema_20_break_recent_5d | 20.0% |
| below_ema_21_break_recent_5d | 19.1% |
| below_ema_50_break_recent_5d | 21.8% |
| below_ema_9_break_recent_5d | 31.8% |
| below_prev_low | 50.9% |
| below_prev_low_clearance_atr_05 | 12.7% |
| below_s1 | 27.3% |
| below_s2 | 13.6% |
| below_sma_200 | 82.7% |
| below_sma_9 | 99.1% |
| below_vwap | 76.4% |
| break_52w_low | 13.6% |
| bullish_pin_bar | 65.5% |
| capitulation_recent_3d | 1.8% |
| chandelier_long_bullish | 0.9% |
| chandelier_long_flip_dn | 3.6% |
| cmf_cross_up | 16.4% |
| cmf_negative | 65.5% |
| cmf_positive | 34.5% |
| concentrated_sell | 3.7% |
| cpr_narrow | 85.5% |
| cpr_narrow_tight | 18.2% |
| cup_handle_detected | 8.2% |
| dc10_breakout_dn | 46.4% |
| dc10_breakout_dn_1pct | 70.9% |
| dc10_strong_breakout_dn | 9.1% |
| dc20_breakout_dn | 46.4% |
| dc20_support_break_retest_strong | 55.5% |
| defensive_leadership | 74.5% |
| director_only_buy | 0.9% |
| doji | 1.8% |
| double_bottom_detected | 19.1% |
| double_top_detected | 21.8% |
| dpi_elevated | 44.0% |
| drying_volume_on_up_turn | 20.9% |
| ema_20_50_bearish | 86.4% |
| ema_20_50_bullish | 13.6% |
| ema_20_50_death_cross | 2.7% |
| ema_50_200_bearish | 57.3% |
| ema_50_200_bullish | 42.7% |
| ema_9_21_death_cross | 0.9% |
| flag_bear_break_retest_short | 3.6% |
| flag_bear_broke | 3.6% |
| force_index_cross_dn | 1.8% |
| force_index_cross_up | 0.9% |
| force_index_positive | 0.9% |
| gap_dn_1_5pct | 38.2% |
| gap_dn_2pct | 30.9% |
| head_shoulders_bottom_detected | 2.7% |
| head_shoulders_top_detected | 7.3% |
| house_cluster_buy | 4.5% |
| house_cluster_sell | 2.7% |
| htf_aligned_bear | 80.0% |
| htf_disagreement | 5.5% |
| hull_bearish | 99.1% |
| hull_bullish | 0.9% |
| hull_flip_dn | 4.5% |
| ichi_above_cloud | 1.8% |
| ichi_below_cloud | 92.7% |
| ichi_below_cloud_break_recent_5d | 30.0% |
| ichi_cloud_thick | 84.5% |
| ichi_tk_bearish | 94.5% |
| ichi_tk_cross_dn | 1.8% |
| ichi_weekly_above_cloud | 13.8% |
| ichi_weekly_below_cloud | 53.2% |
| ichi_weekly_in_cloud | 33.0% |
| inside_bar | 8.2% |
| inside_cpr | 5.5% |
| inside_kc | 19.1% |
| institutional_buy | 85.5% |
| institutional_negative | 4.5% |
| institutional_persistence_growing | 48.4% |
| institutional_persistence_strong | 61.3% |
| institutional_strong_buy | 76.4% |
| inverted_cup_handle_detected | 5.5% |
| is_friday | 33.6% |
| is_halloween_period | 44.5% |
| is_january | 3.6% |
| is_january_extended | 4.5% |
| is_monday | 18.2% |
| is_pre_holiday | 1.8% |
| is_summer_period | 55.5% |
| is_totm_window | 21.8% |
| is_totm_window_first_day | 4.5% |
| is_week_open | 19.1% |
| kc_touch_lower | 87.3% |
| macd_12_26_9_bearish | 94.5% |
| macd_12_26_9_bullish | 5.5% |
| macd_12_26_9_crossover_dn | 3.6% |
| macd_8_21_5_bearish | 92.7% |
| macd_8_21_5_bullish | 7.3% |
| macd_8_21_5_crossover_dn | 6.4% |
| mfi_broad_overbought | 0.9% |
| mfi_broad_oversold | 55.5% |
| mfi_oversold | 18.2% |
| monthly_above_sma_12 | 18.3% |
| monthly_above_sma_6 | 7.3% |
| monthly_bias_bear | 80.7% |
| monthly_bias_bull | 6.4% |
| monthly_momentum_pos | 22.9% |
| near_52w_high_retest_long | 0.9% |
| near_52w_low | 30.0% |
| near_52w_low_105pct | 43.6% |
| near_avwap_20high_atr_10x | 3.6% |
| near_avwap_20high_atr_15x | 15.5% |
| near_avwap_20high_atr_20x | 41.8% |
| near_avwap_20low_atr_05x | 80.0% |
| near_avwap_252low_atr_05x | 15.8% |
| near_avwap_252low_atr_10x | 28.9% |
| near_avwap_252low_atr_15x | 34.2% |
| near_avwap_252low_atr_20x | 47.4% |
| near_avwap_50low_atr_05x | 40.7% |
| near_avwap_50low_atr_10x | 51.9% |
| near_avwap_50low_atr_15x | 55.6% |
| near_avwap_50low_atr_20x | 66.7% |
| near_cam_r3 | 12.7% |
| near_cam_s3 | 18.2% |
| near_cam_s4 | 7.3% |
| near_fib_618 | 0.9% |
| near_fib_786 | 11.8% |
| near_pivot | 15.5% |
| near_prev_close | 19.1% |
| near_prev_high | 1.8% |
| near_prev_low | 20.0% |
| near_r1_wide | 21.8% |
| near_r2_wide | 1.8% |
| near_s1 | 20.0% |
| near_s1_wide | 58.2% |
| near_s2 | 5.5% |
| near_s2_wide | 26.4% |
| near_s3 | 1.8% |
| near_wood_r1 | 0.9% |
| near_wood_s1 | 11.8% |
| news_uses_polygon_score | 24.5% |
| obv_bearish | 97.3% |
| obv_bullish | 2.7% |
| obv_diverge_bull | 2.7% |
| obv_falling | 96.4% |
| obv_rising | 3.6% |
| pead_negative_surprise | 24.5% |
| pead_positive_surprise | 16.3% |
| pin_bar | 65.5% |
| po3_accumulation_active | 13.6% |
| po3_bullish | 91.8% |
| po3_manipulation_sweep_down | 12.7% |
| po3_mmbm_setup | 4.5% |
| po3_sweep_above_prior_high | 1.8% |
| po3_sweep_below_prior_low | 91.8% |
| ppo_bullish | 5.5% |
| ppo_crossover_dn | 1.8% |
| pre_fomc_d1 | 1.8% |
| pre_fomc_window | 1.8% |
| price_above_dema | 6.4% |
| price_above_ema_200 | 9.1% |
| price_above_ema_200_break_recent_5d | 0.9% |
| price_above_hull | 5.5% |
| price_above_sma_200 | 17.3% |
| price_above_tema | 8.2% |
| price_below_dema | 93.6% |
| price_below_hull | 94.5% |
| price_below_tema | 91.8% |
| psar_flip_dn | 8.2% |
| r1_break_retest_long | 0.9% |
| recent_capitulation_at_s3 | 1.8% |
| risk_off_regime_bond_signal | 37.3% |
| risk_off_regime_bond_signal_strong | 28.2% |
| risk_off_regime_gold_signal | 40.0% |
| risk_on_regime_bond_signal | 30.9% |
| risk_on_regime_bond_signal_strong | 8.2% |
| roc_turning_dn | 0.9% |
| rsi_14_cross_up_oversold_recent_3d | 8.2% |
| rsi_14_extreme_os | 5.5% |
| rsi_14_oversold | 51.8% |
| rsi_14_rising | 31.8% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.9% |
| rsi_21_cross_up_oversold_recent_3d | 6.4% |
| rsi_21_oversold | 17.3% |
| rsi_21_rising | 31.8% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 10.9% |
| rsi_2_cross_dn_overbought_recent_3d | 19.1% |
| rsi_2_cross_up_extreme_os_recent_3d | 16.4% |
| rsi_2_cross_up_oversold_recent_3d | 4.5% |
| rsi_2_extreme_os | 80.0% |
| rsi_2_oversold | 95.5% |
| rsi_2_rising | 31.8% |
| rsi_9_cross_up_extreme_os_recent_3d | 8.2% |
| rsi_9_cross_up_oversold_recent_3d | 6.4% |
| rsi_9_extreme_os | 19.1% |
| rsi_9_oversold | 90.0% |
| rsi_9_rising | 31.8% |
| s1_break_retest_short | 99.1% |
| sc_13d_filed_within_30d | 5.7% |
| sc_13g_filed_within_30d | 2.9% |
| sector_outperforming_spy | 25.0% |
| sector_underperforming_spy | 75.0% |
| sma_20_50_bullish | 23.6% |
| sma_50_200_bullish | 45.5% |
| sma_9_21_bullish | 0.9% |
| smc_bos_bearish | 30.0% |
| smc_bos_bullish | 3.6% |
| smc_bos_retest_long | 3.6% |
| smc_bos_retest_short | 3.6% |
| smc_breaker_block_bearish | 35.5% |
| smc_breaker_block_bullish | 8.2% |
| smc_choch_bearish | 9.1% |
| smc_choch_bullish | 0.9% |
| smc_equal_highs_swept | 1.8% |
| smc_equal_lows_swept | 10.9% |
| smc_fvg_bearish_active | 91.8% |
| smc_fvg_bullish_active | 6.4% |
| smc_fvg_retest_long_zone | 0.9% |
| smc_fvg_retest_short_zone | 64.5% |
| smc_in_premium_zone | 1.8% |
| smc_inverse_fvg_bullish | 22.7% |
| smc_liquidity_swept_dn | 3.6% |
| smc_liquidity_swept_up | 2.7% |
| smc_mitigation_block_long | 7.3% |
| smc_ob_bearish_active | 58.2% |
| smc_ob_bullish_active | 17.3% |
| smc_ote_long_zone | 11.8% |
| squeeze_fire_dn | 1.8% |
| squeeze_in | 9.1% |
| stoch_bearish_cross | 4.5% |
| stoch_broad_oversold | 89.1% |
| stoch_bullish_cross | 21.8% |
| stoch_oversold | 81.8% |
| stochrsi_cross_dn | 23.6% |
| stochrsi_cross_up | 22.7% |
| stochrsi_overbought | 0.9% |
| stochrsi_oversold | 65.5% |
| supertrend_bearish | 21.8% |
| supertrend_bullish | 78.2% |
| supertrend_flip_dn | 6.4% |
| supertrend_flip_recent_long_5d | 0.9% |
| supertrend_flip_recent_short_5d | 22.7% |
| supertrend_flip_up | 0.9% |
| support_break_retest | 82.7% |
| tema_above_dema | 4.5% |
| tema_cross_dn | 2.7% |
| triangle_ascending_detected | 0.9% |
| triangle_descending_detected | 11.8% |
| uo_oversold | 8.2% |
| usd_strengthening | 30.0% |
| usd_weakening | 3.6% |
| vix_band_high | 48.2% |
| vix_band_low | 22.7% |
| vix_band_mid | 29.1% |
| vix_term_backwardation | 14.5% |
| vix_term_contango | 85.5% |
| vol_above_avg | 79.1% |
| vol_below_avg | 20.9% |
| vol_spike_12x | 54.5% |
| vol_spike_15x | 35.5% |
| vol_spike_17x | 27.3% |
| vol_spike_2x | 20.0% |
| vol_spike_2x_on_down_day_recent_3d | 21.8% |
| vol_spike_2x_on_up_day_recent_3d | 0.9% |
| vol_spike_3x | 10.0% |
| vp_below_value_area | 86.4% |
| vp_close_above_poc | 2.7% |
| vp_close_below_poc | 97.3% |
| vp_in_value_area | 13.6% |
| week_open_gap_down_15pct | 4.5% |
| weekly_above_ema_20 | 0.9% |
| weekly_bias_bear | 99.1% |
| williams_r_oversold | 70.0% |
| williams_r_rising | 85.5% |
| within_pead_window | 40.0% |
| within_post_deletion_window | 21.4% |
| xs_avoid_high_ivol | 71.8% |
| xs_avoid_high_max | 86.4% |
| xs_high_beta_decile | 20.0% |
| xs_low_beta_bottom_quintile | 20.0% |
| xs_low_beta_decile | 20.0% |
| xs_low_beta_top_quintile | 20.0% |
| xs_momentum_bottom_decile | 16.4% |
| xs_momentum_bottom_quintile | 24.5% |
| xs_momentum_top_decile | 6.4% |
| xs_momentum_top_quintile | 10.9% |
| xs_quality_bottom_quintile | 19.0% |
| xs_quality_top_quintile | 27.0% |
| xs_quality_top_tercile | 46.0% |
| year_low_break_retest_short | 13.6% |
| yoy_surprise_high | 46.2% |
| yoy_surprise_negative | 43.4% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 84.5% |
| committed_growth_holders | 84.5% |
| corp_donations_1y | 7.3% |
| corp_donations_count_1y | 7.3% |
| corp_donations_unique_pacs | 7.3% |
| cot_rut_commercials_pctile_3y | 49.1% |
| cot_rut_mmoney_pctile_3y | 49.1% |
| cup_handle_depth_pct | 15.5% |
| days_since_deletion | 12.7% |
| days_since_inclusion | 9.1% |
| days_to_next_holiday | 59.1% |
| days_to_rebalance | 12.7% |
| earnings_announcement_return | 89.1% |
| earnings_eps_yoy_growth | 96.4% |
| gov_contracts_4q_sum | 40.9% |
| gov_contracts_last_qtr_amount | 40.9% |
| gov_contracts_qoq_growth | 40.9% |
| head_shoulders_magnitude_pct | 10.0% |
| insider_director_buyers_30d | 5.5% |
| insider_officer_buyers_30d | 5.5% |
| insider_total_shares_bought_30d | 5.5% |
| inverted_cup_handle_height_pct | 15.5% |
| lobbying_amount_1y | 72.7% |
| lobbying_amount_q | 72.7% |
| lobbying_amount_yoy | 72.7% |
| pair_half_life | 88.2% |
| pair_max_abs_zscore | 88.2% |
| pair_zscore_signed | 88.2% |
| pct_from_avwap_20low | 13.6% |
| pct_from_avwap_252low | 69.1% |
| pct_from_avwap_50low | 24.5% |
| persistent_holders_4q | 84.5% |
| persistent_holders_8q | 84.5% |
| search_volume_index_recent | 79.1% |
| search_volume_observations | 79.1% |
| search_volume_zscore_30d | 79.1% |
| sector_etf_return_20d | 3.6% |
| short_interest_pct | 97.3% |
| spy_return_20d | 3.6% |
| total_active_holders | 84.5% |
| triangle_breakdown_pct | 11.8% |
| xs_quality_decile | 57.3% |
| xs_quality_gross_profitability | 57.3% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.998), `avwap_252low` (0.996), `avwap_50low` (0.997), `bb_10_20_lower` (0.997), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.998), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.998), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.998), `cam_s2` (0.998), `cam_s3` (0.998), `cam_s4` (0.998), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.995), `cup_handle_rim` (0.988), `dc10_lower` (0.997), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.997), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.991), `double_bottom_trough` (0.996), `double_top_neckline` (0.997), `double_top_peak` (0.999), `entry_stop_long` (0.996), `entry_stop_short` (0.999), `fib_236` (0.997), `fib_382` (0.998), `fib_500` (0.998), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.994), `fib_ext_162` (0.993), `head_shoulders_bottom_neckline` (1.0), `head_shoulders_top_neckline` (1.0), `hull_ma` (0.999), `ichi_kijun` (0.999), `ichi_senkou_a` (0.996), `ichi_senkou_b` (0.992), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.998), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.998), `monthly_sma_12` (0.985), `monthly_sma_6` (0.995), `pivot` (0.999), `prev_close` (0.998), `prev_high` (0.999), `prev_low` (0.998), `psar_value` (0.999), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.998), `s2` (0.997), `s3` (0.995), `supertrend_value` (0.994), `swing_high` (0.996), `swing_low` (0.997), `tema` (0.999), `triangle_support_level` (0.995), `vp_poc` (0.996), `vp_value_area_high` (0.996), `vp_value_area_low` (0.998), `vwap_upper_1` (0.951), `vwap_upper_2` (0.953), `weekly_close` (0.998), `weekly_ema_10` (0.999), `weekly_ema_20` (0.996), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.998), `year_high` (0.97), `year_low` (0.979)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | bb (period, k) | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1 | implicit anatomy knobs (min body/wick/st | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P3.1 | proximity tolerance to S1 (abs dist/leve | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P4.1 | proximity tolerance to S2 (abs dist/leve | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P5 | rsi_14 < 35 | 5 | subset-safe | no - derives offline |

```
FULL FACTORIAL     1 x 1 x 1 x 1 x 5 = 5
offline gradings   5 level-combinations x 24 exits = 120
ENGINE RUNS        1 (every fire-adding axis sits at production-only until its env actuator exists)
check              1 x 5 = 5
```

B-row candidates NOT in this factorial: 473 census axes join it only when REGISTERED at the T3 band review.
