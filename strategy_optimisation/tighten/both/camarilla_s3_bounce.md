# Table A - camarilla_s3_bounce

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit fa06ebf3e at 2026-09-19 13:07:41 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** pivot | **status:** NOT-STARTED | **R5 fires:** 228 | **surviving fires (T1):** 228 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  near_cam_r3  <- backtest/signals/screener.py +1
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P1.1-P1.1 (band rows in Table A)
P2  near_cam_s3  <- backtest/signals/screener.py +1
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P2.1-P2.1 (band rows in Table A)
P3  obv_bearish  <- backtest/signals/screener.py +1
       DEFN: OBV vs its moving average (technical.py:1570)
       knobs P3.1-P3.1 (band rows in Table A)
P4  obv_bullish  <- backtest/signals/screener.py +1
       DEFN: OBV vs its moving average (technical.py:1570)
       knobs P4.1-P4.2 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P5  rsi_14 < 40   [EXISTING-THRESHOLD]
P6  rsi_14 > 60   [EXISTING-THRESHOLD]
P7  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_camarilla_s3_bounce (docstring and return dropped):

```python
fl = s.get('near_cam_s3') and s.get('rsi_14', 50) < 40 and s.get('obv_bullish')
fs = (s.get('near_cam_r3') and s.get('rsi_14', 50) > 60 and s.get('obv_bearish')) and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | near_cam_r3 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | proximity tolerance to Camarilla R3 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | near_cam_s3 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | proximity tolerance to Camarilla S3 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | obv_bearish - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | OBV vs its moving average (technical.py:1570) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | mirror of obv_bullish - backtest/signals/technical.py obv block | mirror | obv < obv_ma | as obv_bullish, mirrored | tighter margins on persisted obv/obv_ma | looser; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | PRODUCER | obv_bullish - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | OBV vs its moving average (technical.py:1570) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P4.x) | BANDS-DEFINED |
| P4.1 | BAND | obv vs its moving average - backtest/signals/technical.py:1570 | BRACKET the shipped span | obv > obv_ma | MA span [10, 20, 50] | none - obv_ma at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4.2 | BAND | margin pct over the MA - technical.py:1570 | BRACKET zero | 0.0 | [0, 1, 2] pct | TIGHTER margins where obv and obv_ma are persisted | LOOSER; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | STRATEGY | rsi_14 `< 40` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `< 40` | production + 2 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P5.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P6 | STRATEGY | rsi_14 `> 60` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `> 60` | production + 1 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P6.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P7 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `< 40` | 100.0% | TIGHTER = LOWER the ceiling: 36.704 -> 46 (20%); 38.558 -> 91 (40%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |
| rsi_14 | backtest/signals/screener.py | `> 60` | 100.0% | TIGHTER = RAISE the floor: 62.598 -> 46 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 21.682, 27.652, 33.008, 39.112 | 21.682: 182 (80%); 27.652: 137 (60%); 33.008: 91 (40%); 39.112: 46 (20%) | 21.682: 46 (20%); 27.652: 91 (40%); 33.008: 137 (60%); 39.112: 182 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 16.228, 21.648, 27.862, 31.21 | 16.228: 182 (80%); 21.648: 137 (60%); 27.862: 91 (40%); 31.21: 46 (20%) | 16.228: 46 (20%); 21.648: 91 (40%); 27.862: 137 (60%); 31.21: 182 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 13.968, 17.178, 22.622, 30.106 | 13.968: 182 (80%); 17.178: 137 (60%); 22.622: 91 (40%); 30.106: 46 (20%) | 13.968: 46 (20%); 17.178: 91 (40%); 22.622: 137 (60%); 30.106: 182 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -6.6559, -2.5504, -0.0706, 3.6457 | -6.6559: 182 (80%); -2.5504: 137 (60%); -0.0706: 91 (40%); 3.6457: 46 (20%) | -6.6559: 46 (20%); -2.5504: 91 (40%); -0.0706: 137 (60%); 3.6457: 182 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 0.9613, 1.6587, 2.5651, 4.9344 | 0.9613: 182 (80%); 1.6587: 137 (60%); 2.5651: 91 (40%); 4.9344: 46 (20%) | 0.9613: 46 (20%); 1.6587: 91 (40%); 2.5651: 137 (60%); 4.9344: 182 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 0.9613, 1.6587, 2.5651, 4.9344 | 0.9613: 182 (80%); 1.6587: 137 (60%); 2.5651: 91 (40%); 4.9344: 46 (20%) | 0.9613: 46 (20%); 1.6587: 91 (40%); 2.5651: 137 (60%); 4.9344: 182 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.7348, 2.0476, 2.388, 3.0432 | 1.7348: 182 (80%); 2.0476: 137 (60%); 2.388: 92 (40%); 3.0432: 46 (20%) | 1.7348: 46 (20%); 2.0476: 91 (40%); 2.388: 138 (61%); 3.0432: 182 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0362, 0.0529, 0.0692, 0.092 | 0.0362: 183 (80%); 0.0529: 137 (60%); 0.0692: 92 (40%); 0.092: 46 (20%) | 0.0362: 47 (21%); 0.0529: 93 (41%); 0.0692: 137 (60%); 0.092: 182 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.2322, 0.3815, 0.5996, 0.7346 | 0.2322: 182 (80%); 0.3815: 137 (60%); 0.5996: 91 (40%); 0.7346: 46 (20%) | 0.2322: 46 (20%); 0.3815: 91 (40%); 0.5996: 137 (60%); 0.7346: 182 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0451, 0.063, 0.084, 0.1283 | 0.0451: 182 (80%); 0.063: 137 (60%); 0.084: 91 (40%); 0.1283: 46 (20%) | 0.0451: 46 (20%); 0.063: 92 (40%); 0.084: 137 (60%); 0.1283: 182 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.1045, 0.2685, 0.4969, 0.8426 | 0.1045: 182 (80%); 0.2685: 137 (60%); 0.4969: 91 (40%); 0.8426: 46 (20%) | 0.1045: 46 (20%); 0.2685: 91 (40%); 0.4969: 137 (60%); 0.8426: 182 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0602, 0.084, 0.1119, 0.1712 | 0.0602: 182 (80%); 0.084: 137 (60%); 0.1119: 91 (40%); 0.1712: 46 (20%) | 0.0602: 46 (20%); 0.084: 92 (40%); 0.1119: 137 (60%); 0.1712: 182 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.2034, 0.3263, 0.4977, 0.757 | 0.2034: 182 (80%); 0.3263: 137 (60%); 0.4977: 91 (40%); 0.757: 46 (20%) | 0.2034: 46 (20%); 0.3263: 91 (40%); 0.4977: 137 (60%); 0.757: 182 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0496, -0.0282, -0.0049, 0.0193 | -0.0496: 183 (80%); -0.0282: 137 (60%); -0.0049: 91 (40%); 0.0193: 50 (22%) | -0.0496: 47 (21%); -0.0282: 91 (40%); -0.0049: 137 (60%); 0.0193: 183 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1376, 0.1621, 0.2004, 0.2478 | 0.1376: 181 (79%); 0.1621: 137 (60%); 0.2004: 90 (39%); 0.2478: 46 (20%) | 0.1376: 47 (21%); 0.1621: 91 (40%); 0.2004: 138 (61%); 0.2478: 182 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 228 (100%) | 0: 220 (96%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1348, -0.0556, 0.0238, 0.1172 | -0.1348: 182 (80%); -0.0556: 137 (60%); 0.0238: 91 (40%); 0.1172: 46 (20%) | -0.1348: 46 (20%); -0.0556: 92 (40%); 0.0238: 137 (60%); 0.1172: 182 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1, 2 | 0: 228 (100%); 1: 112 (49%); 2: 50 (22%) | 0: 116 (51%); 1: 178 (78%); 2: 201 (88%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2358, -0.1875, -0.1546, -0.1189 | -0.2358: 182 (80%); -0.1875: 137 (60%); -0.1546: 97 (43%); -0.1189: 47 (21%) | -0.2358: 46 (20%); -0.1875: 91 (40%); -0.1546: 137 (60%); -0.1189: 184 (81%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3782, 0.5807, 0.6885, 0.8013 | 0.3782: 184 (81%); 0.5807: 137 (60%); 0.6885: 91 (40%); 0.8013: 51 (22%) | 0.3782: 49 (21%); 0.5807: 91 (40%); 0.6885: 137 (60%); 0.8013: 183 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2372, 0.3961, 0.7257, 0.8333 | 0.2372: 184 (81%); 0.3961: 137 (60%); 0.7257: 91 (40%); 0.8333: 49 (21%) | 0.2372: 47 (21%); 0.3961: 91 (40%); 0.7257: 137 (60%); 0.8333: 184 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1288, -0.0304, 0.0498, 0.1722 | -0.1288: 183 (80%); -0.0304: 139 (61%); 0.0498: 92 (40%); 0.1722: 47 (21%) | -0.1288: 47 (21%); -0.0304: 95 (42%); 0.0498: 138 (61%); 0.1722: 183 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2372, 0.4449, 0.591, 0.7244 | 0.2372: 183 (80%); 0.4449: 137 (60%); 0.591: 91 (40%); 0.7244: 49 (21%) | 0.2372: 49 (21%); 0.4449: 91 (40%); 0.591: 137 (60%); 0.7244: 183 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0923, 0.2564, 0.4359, 0.6218 | 0.0923: 182 (80%); 0.2564: 142 (62%); 0.4359: 95 (42%); 0.6218: 51 (22%) | 0.0923: 46 (20%); 0.2564: 97 (43%); 0.4359: 142 (62%); 0.6218: 183 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.521, -0.2719, -0.168, 0.0839 | -0.521: 183 (80%); -0.2719: 137 (60%); -0.168: 91 (40%); 0.0839: 47 (21%) | -0.521: 47 (21%); -0.2719: 91 (40%); -0.168: 137 (60%); 0.0839: 183 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3013, 0.5321, 0.759, 0.9551 | 0.3013: 185 (81%); 0.5321: 138 (61%); 0.759: 91 (40%); 0.9551: 48 (21%) | 0.3013: 48 (21%); 0.5321: 92 (40%); 0.759: 137 (60%); 0.9551: 185 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1039, 0.3205, 0.559, 0.7244 | 0.1039: 182 (80%); 0.3205: 138 (61%); 0.559: 91 (40%); 0.7244: 50 (22%) | 0.1039: 46 (20%); 0.3205: 96 (42%); 0.559: 137 (60%); 0.7244: 184 (81%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0657, -0.0587, -0.0408, 0 | -0.0657: 183 (80%); -0.0587: 137 (60%); -0.0408: 93 (41%); 0: 73 (32%) | -0.0657: 48 (21%); -0.0587: 93 (41%); -0.0408: 140 (61%); 0: 223 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3526, 0.6821, 0.8846, 1 | 0.3526: 183 (80%); 0.6821: 137 (60%); 0.8846: 96 (42%); 1: 53 (23%) | 0.3526: 52 (23%); 0.6821: 91 (40%); 0.8846: 144 (63%); 1: 228 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1218, 0.2385, 0.6026, 0.9231 | 0.1218: 183 (80%); 0.2385: 137 (60%); 0.6026: 94 (41%); 0.9231: 48 (21%) | 0.1218: 47 (21%); 0.2385: 91 (40%); 0.6026: 140 (61%); 0.9231: 183 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0213, 0.0111, 0.0438, 0.1259 | -0.0213: 183 (80%); 0.0111: 141 (62%); 0.0438: 91 (40%); 0.1259: 46 (20%) | -0.0213: 47 (21%); 0.0111: 92 (40%); 0.0438: 137 (60%); 0.1259: 182 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3343, 0.5974, 0.7987, 0.9491 | 0.3343: 182 (80%); 0.5974: 138 (61%); 0.7987: 93 (41%); 0.9491: 46 (20%) | 0.3343: 46 (20%); 0.5974: 92 (40%); 0.7987: 138 (61%); 0.9491: 182 (80%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1867, 0.4744, 0.7076, 0.8421 | 0.1867: 183 (80%); 0.4744: 139 (61%); 0.7076: 91 (40%); 0.8421: 47 (21%) | 0.1867: 47 (21%); 0.4744: 92 (40%); 0.7076: 137 (60%); 0.8421: 184 (81%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0297, 0.0382, 0.0966, 0.2073 | -0.0297: 183 (80%); 0.0382: 137 (60%); 0.0966: 91 (40%); 0.2073: 46 (20%) | -0.0297: 47 (21%); 0.0382: 91 (40%); 0.0966: 137 (60%); 0.2073: 182 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1814, -0.0471, 0.0246, 0.0658 | -0.1814: 182 (80%); -0.0471: 138 (61%); 0.0246: 91 (40%); 0.0658: 47 (21%) | -0.1814: 46 (20%); -0.0471: 95 (42%); 0.0246: 137 (60%); 0.0658: 184 (81%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.1731, 0.5256, 0.6821, 0.8269 | 0.1731: 183 (80%); 0.5256: 144 (63%); 0.6821: 91 (40%); 0.8269: 47 (21%) | 0.1731: 47 (21%); 0.5256: 96 (42%); 0.6821: 137 (60%); 0.8269: 183 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1474, 0.332, 0.5654, 0.8141 | 0.1474: 186 (82%); 0.332: 137 (60%); 0.5654: 91 (40%); 0.8141: 47 (21%) | 0.1474: 50 (22%); 0.332: 91 (40%); 0.5654: 137 (60%); 0.8141: 183 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0328, 0.0814, 0.1771, 0.3613 | 0.0328: 182 (80%); 0.0814: 137 (60%); 0.1771: 91 (40%); 0.3613: 46 (20%) | 0.0328: 46 (20%); 0.0814: 91 (40%); 0.1771: 137 (60%); 0.3613: 182 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.2% | 27, 51.2, 74.8, 126.4 | 27: 181 (79%); 51.2: 134 (59%); 74.8: 90 (39%); 126.4: 45 (20%) | 27: 47 (21%); 51.2: 90 (39%); 74.8: 134 (59%); 126.4: 179 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 98.2% | 1.6819, 2.4402, 3.2526, 4.8851 | 1.6819: 179 (79%); 2.4402: 134 (59%); 3.2526: 90 (39%); 4.8851: 45 (20%) | 1.6819: 45 (20%); 2.4402: 90 (39%); 3.2526: 134 (59%); 4.8851: 179 (79%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 9, 19, 27, 34 | 9: 191 (84%); 19: 147 (64%); 27: 92 (40%); 34: 54 (24%) | 9: 47 (21%); 19: 94 (41%); 27: 146 (64%); 34: 188 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3 | 1: 187 (82%); 2: 147 (64%); 3: 96 (42%) | 1: 81 (36%); 2: 132 (58%); 3: 183 (80%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0096, 0.0004, 0.0147, 0.0255 | -0.0096: 182 (80%); 0.0004: 138 (61%); 0.0147: 91 (40%); 0.0255: 47 (21%) | -0.0096: 46 (20%); 0.0004: 92 (40%); 0.0147: 137 (60%); 0.0255: 183 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.9173, 25.8636, 26.5338, 27.4428 | 24.9173: 182 (80%); 25.8636: 137 (60%); 26.5338: 92 (40%); 27.4428: 48 (21%) | 24.9173: 46 (20%); 25.8636: 91 (40%); 26.5338: 138 (61%); 27.4428: 183 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.589, -0.249, 0.0248, 0.5856 | -0.589: 182 (80%); -0.249: 137 (60%); 0.0248: 91 (40%); 0.5856: 46 (20%) | -0.589: 46 (20%); -0.249: 91 (40%); 0.0248: 137 (60%); 0.5856: 182 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.5856, -0.0248, 0.249, 0.589 | -0.5856: 182 (80%); -0.0248: 137 (60%); 0.249: 91 (40%); 0.589: 46 (20%) | -0.5856: 46 (20%); -0.0248: 91 (40%); 0.249: 137 (60%); 0.589: 182 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.045, -0.0127, 0.0191, 0.0484 | -0.045: 183 (80%); -0.0127: 137 (60%); 0.0191: 91 (40%); 0.0484: 49 (21%) | -0.045: 46 (20%); -0.0127: 91 (40%); 0.0191: 137 (60%); 0.0484: 183 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.1257, 8.5093, 8.7829, 9.0376 | 8.1257: 182 (80%); 8.5093: 138 (61%); 8.7829: 91 (40%); 9.0376: 45 (20%) | 8.1257: 46 (20%); 8.5093: 90 (39%); 8.7829: 137 (60%); 9.0376: 183 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 98.2% | 0, 1 | 0: 224 (98%); 1: 62 (27%) | 0: 162 (71%); 1: 204 (89%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 98.2% | 0 | 0: 188 (82%) | 0: 192 (84%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 98.2% | 0, 1 | 0: 224 (98%); 1: 72 (32%) | 0: 152 (67%); 1: 208 (91%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 3, 7, 167.4, 285.4 | 3: 189 (83%); 7: 141 (62%); 167.4: 91 (40%); 285.4: 46 (20%) | 3: 59 (26%); 7: 96 (42%); 167.4: 137 (60%); 285.4: 182 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 5, 84.2, 127.2 | 1: 188 (82%); 5: 142 (62%); 84.2: 91 (40%); 127.2: 46 (20%) | 1: 63 (28%); 5: 93 (41%); 84.2: 137 (60%); 127.2: 182 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.422, -0.0819, 0.0612, 0.2616 | -0.422: 182 (80%); -0.0819: 137 (60%); 0.0612: 91 (40%); 0.2616: 46 (20%) | -0.422: 46 (20%); -0.0819: 91 (40%); 0.0612: 137 (60%); 0.2616: 182 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -2.7929, -1.0319, -0.0672, 1.6245 | -2.7929: 182 (80%); -1.0319: 137 (60%); -0.0672: 91 (40%); 1.6245: 46 (20%) | -2.7929: 46 (20%); -1.0319: 91 (40%); -0.0672: 137 (60%); 1.6245: 182 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -2.8137, -1.0366, -0.1374, 1.9636 | -2.8137: 182 (80%); -1.0366: 137 (60%); -0.1374: 91 (40%); 1.9636: 46 (20%) | -2.8137: 46 (20%); -1.0366: 91 (40%); -0.1374: 137 (60%); 1.9636: 182 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.2548, -0.0725, 0.076, 0.3309 | -0.2548: 182 (80%); -0.0725: 137 (60%); 0.076: 91 (40%); 0.3309: 46 (20%) | -0.2548: 46 (20%); -0.0725: 91 (40%); 0.076: 137 (60%); 0.3309: 182 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -2.8814, -1.0462, 0.0791, 1.4719 | -2.8814: 182 (80%); -1.0462: 137 (60%); 0.0791: 91 (40%); 1.4719: 46 (20%) | -2.8814: 46 (20%); -1.0462: 91 (40%); 0.0791: 137 (60%); 1.4719: 182 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -2.8244, -1.0698, 0.034, 1.5338 | -2.8244: 182 (80%); -1.0698: 137 (60%); 0.034: 91 (40%); 1.5338: 46 (20%) | -2.8244: 46 (20%); -1.0698: 91 (40%); 0.034: 137 (60%); 1.5338: 182 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 38.254, 47.158, 51.848, 57.884 | 38.254: 182 (80%); 47.158: 137 (60%); 51.848: 91 (40%); 57.884: 46 (20%) | 38.254: 46 (20%); 47.158: 91 (40%); 51.848: 137 (60%); 57.884: 182 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 98.7% | 0.0026, 0.0083, 0.0214, 0.0448 | 0.0026: 179 (79%); 0.0083: 135 (59%); 0.0214: 90 (39%); 0.0448: 45 (20%) | 0.0026: 46 (20%); 0.0083: 90 (39%); 0.0214: 135 (59%); 0.0448: 180 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3, 7 | 0: 228 (100%); 1: 158 (69%); 3: 102 (45%); 7: 50 (22%) | 0: 70 (31%); 1: 106 (46%); 3: 142 (62%); 7: 185 (81%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1067 | 0: 228 (100%); 0.1067: 46 (20%) | 0: 171 (75%); 0.1067: 182 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.4, 0.6667 | 0: 228 (100%); 0.4: 92 (40%); 0.6667: 49 (21%) | 0: 103 (45%); 0.4: 143 (63%); 0.6667: 186 (82%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 2, 5 | 0: 228 (100%); 1: 142 (62%); 2: 105 (46%); 5: 52 (23%) | 0: 86 (38%); 1: 123 (54%); 2: 147 (64%); 5: 185 (81%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 228 (100%); 1: 158 (69%); 3: 102 (45%); 7: 50 (22%) | 0: 70 (31%); 1: 106 (46%); 3: 142 (62%); 7: 185 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 6 | 0: 228 (100%); 1: 150 (66%); 3: 94 (41%); 6: 56 (25%) | 0: 78 (34%); 1: 110 (48%); 3: 146 (64%); 6: 183 (80%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2088, 0.3666, 0.6208 | 0: 211 (93%); 0.2088: 137 (60%); 0.3666: 91 (40%); 0.6208: 46 (20%) | 0: 58 (25%); 0.2088: 91 (40%); 0.3666: 137 (60%); 0.6208: 182 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.5 | 0: 208 (91%); 0.5: 51 (22%) | 0: 141 (62%); 0.5: 185 (81%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2545, 0.6 | 0: 205 (90%); 0.2545: 91 (40%); 0.6: 47 (21%) | 0: 116 (51%); 0.2545: 137 (60%); 0.6: 183 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2545, 0.6 | 0: 205 (90%); 0.2545: 91 (40%); 0.6: 47 (21%) | 0: 116 (51%); 0.2545: 137 (60%); 0.6: 183 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.0904, 0, 0.1146 | -0.0904: 182 (80%); 0: 172 (75%); 0.1146: 46 (20%) | -0.0904: 46 (20%); 0: 168 (74%); 0.1146: 182 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.8018, -0.4472, 0, 0.9277 | -0.8018: 182 (80%); -0.4472: 143 (63%); 0: 114 (50%); 0.9277: 46 (20%) | -0.8018: 46 (20%); -0.4472: 99 (43%); 0: 147 (64%); 0.9277: 182 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 6.2, 10 | 2: 188 (82%); 4: 145 (64%); 6.2: 91 (40%); 10: 52 (23%) | 2: 67 (29%); 4: 103 (45%); 6.2: 137 (60%); 10: 187 (82%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0375, -0.0127, 0.0043, 0.0243 | -0.0375: 182 (80%); -0.0127: 138 (61%); 0.0043: 91 (40%); 0.0243: 46 (20%) | -0.0375: 46 (20%); -0.0127: 90 (39%); 0.0043: 137 (60%); 0.0243: 182 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0892, -0.0495, 0.0023, 0.0521 | -0.0892: 182 (80%); -0.0495: 137 (60%); 0.0023: 91 (40%); 0.0521: 46 (20%) | -0.0892: 46 (20%); -0.0495: 91 (40%); 0.0023: 137 (60%); 0.0521: 182 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0258, -0.0087, 0.0054, 0.019 | -0.0258: 182 (80%); -0.0087: 137 (60%); 0.0054: 91 (40%); 0.019: 46 (20%) | -0.0258: 46 (20%); -0.0087: 91 (40%); 0.0054: 137 (60%); 0.019: 182 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -16.4926, -4.2406, 7.2024, 26.5222 | -16.4926: 182 (80%); -4.2406: 137 (60%); 7.2024: 91 (40%); 26.5222: 46 (20%) | -16.4926: 46 (20%); -4.2406: 91 (40%); 7.2024: 137 (60%); 26.5222: 182 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0295, 0.0418, 0.0523, 0.0684 | 0.0295: 183 (80%); 0.0418: 137 (60%); 0.0523: 93 (41%); 0.0684: 46 (20%) | 0.0295: 47 (21%); 0.0418: 91 (40%); 0.0523: 137 (60%); 0.0684: 182 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 99.6% | 0.2, 0.3359, 0.45, 0.6557 | 0.2: 182 (80%); 0.3359: 136 (60%); 0.45: 91 (40%); 0.6557: 46 (20%) | 0.2: 47 (21%); 0.3359: 91 (40%); 0.45: 136 (60%); 0.6557: 181 (79%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.9003, -1.68, -0.1861, 1.65 | -2.9003: 182 (80%); -1.68: 137 (60%); -0.1861: 91 (40%); 1.65: 46 (20%) | -2.9003: 46 (20%); -1.68: 91 (40%); -0.1861: 137 (60%); 1.65: 182 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.4057, -0.1349, 0.0411, 0.3062 | -0.4057: 182 (80%); -0.1349: 137 (60%); 0.0411: 91 (40%); 0.3062: 46 (20%) | -0.4057: 46 (20%); -0.1349: 91 (40%); 0.0411: 137 (60%); 0.3062: 182 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -2.9334, -1.6465, -0.2014, 1.7949 | -2.9334: 182 (80%); -1.6465: 137 (60%); -0.2014: 91 (40%); 1.7949: 46 (20%) | -2.9334: 46 (20%); -1.6465: 92 (40%); -0.2014: 137 (60%); 1.7949: 182 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -4.2082, -1.8218, 0.0758, 2.0978 | -4.2082: 182 (80%); -1.8218: 137 (60%); 0.0758: 91 (40%); 2.0978: 46 (20%) | -4.2082: 46 (20%); -1.8218: 91 (40%); 0.0758: 137 (60%); 2.0978: 182 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 17.352, 35.422, 50.81, 76.302 | 17.352: 182 (80%); 35.422: 137 (60%); 50.81: 91 (40%); 76.302: 46 (20%) | 17.352: 46 (20%); 35.422: 91 (40%); 50.81: 137 (60%); 76.302: 182 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 37.95, 39.77, 45.848, 62.016 | 37.95: 183 (80%); 39.77: 138 (61%); 45.848: 91 (40%); 62.016: 46 (20%) | 37.95: 47 (21%); 39.77: 92 (40%); 45.848: 137 (60%); 62.016: 182 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 35.074, 38.646, 46.476, 64.234 | 35.074: 182 (80%); 38.646: 137 (60%); 46.476: 91 (40%); 64.234: 46 (20%) | 35.074: 46 (20%); 38.646: 91 (40%); 46.476: 137 (60%); 64.234: 182 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 227 (100%) | 0: 227 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.029, 0.0382, 0.0549, 0.0739 | 0.029: 182 (80%); 0.0382: 138 (61%); 0.0549: 91 (40%); 0.0739: 46 (20%) | 0.029: 46 (20%); 0.0382: 92 (40%); 0.0549: 137 (60%); 0.0739: 182 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0741, -0.0549, -0.0426, -0.032 | -0.0741: 182 (80%); -0.0549: 137 (60%); -0.0426: 92 (40%); -0.032: 46 (20%) | -0.0741: 46 (20%); -0.0549: 91 (40%); -0.0426: 137 (60%); -0.032: 182 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 228 (100%); 2: 50 (22%) | 0: 160 (70%); 2: 190 (83%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 98.2% | 32.6, 45, 59, 69 | 32.6: 179 (79%); 45: 138 (61%); 59: 92 (40%); 69: 46 (20%) | 32.6: 45 (20%); 45: 97 (43%); 59: 135 (59%); 69: 182 (80%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 99.6% | 0.105, 0.169, 0.4203, 0.8728 | 0.105: 182 (80%); 0.169: 136 (60%); 0.4203: 91 (40%); 0.8728: 46 (20%) | 0.105: 46 (20%); 0.169: 91 (40%); 0.4203: 136 (60%); 0.8728: 181 (79%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 99.6% | 31.16, 75.84, 119.6, 168.34 | 31.16: 181 (79%); 75.84: 136 (60%); 119.6: 91 (40%); 168.34: 46 (20%) | 31.16: 46 (20%); 75.84: 91 (40%); 119.6: 136 (60%); 168.34: 181 (79%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -4.218, -1.519, -0.0174, 3.104 | -4.218: 182 (80%); -1.519: 137 (60%); -0.0174: 91 (40%); 3.104: 46 (20%) | -4.218: 46 (20%); -1.519: 91 (40%); -0.0174: 137 (60%); 3.104: 182 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 22.744, 33.482, 53.952, 72.58 | 22.744: 182 (80%); 33.482: 137 (60%); 53.952: 91 (40%); 72.58: 46 (20%) | 22.744: 46 (20%); 33.482: 91 (40%); 53.952: 137 (60%); 72.58: 182 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 22.848, 33.838, 49.852, 72.276 | 22.848: 182 (80%); 33.838: 137 (60%); 49.852: 91 (40%); 72.276: 46 (20%) | 22.848: 46 (20%); 33.838: 91 (40%); 49.852: 137 (60%); 72.276: 182 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 14.444, 40.842, 63.892, 89.186 | 14.444: 182 (80%); 40.842: 137 (60%); 63.892: 91 (40%); 89.186: 46 (20%) | 14.444: 46 (20%); 40.842: 91 (40%); 63.892: 137 (60%); 89.186: 182 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 11.922, 41.182, 66.544, 96.722 | 11.922: 182 (80%); 41.182: 137 (60%); 66.544: 91 (40%); 96.722: 46 (20%) | 11.922: 46 (20%); 41.182: 91 (40%); 66.544: 137 (60%); 96.722: 182 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 14, 18 | 5: 188 (82%); 9: 141 (62%); 14: 102 (45%); 18: 64 (28%) | 5: 51 (22%); 9: 97 (43%); 14: 138 (61%); 18: 183 (80%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 4, 7, 13, 17 | 4: 187 (82%); 7: 146 (64%); 13: 98 (43%); 17: 50 (22%) | 4: 62 (27%); 7: 93 (41%); 13: 143 (63%); 17: 194 (85%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 40.848, 45.812, 51.406, 57.504 | 40.848: 182 (80%); 45.812: 137 (60%); 51.406: 91 (40%); 57.504: 46 (20%) | 40.848: 46 (20%); 45.812: 91 (40%); 51.406: 137 (60%); 57.504: 182 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1127, 0.3087, 0.631, 0.8095 | 0.1127: 182 (80%); 0.3087: 137 (60%); 0.631: 92 (40%); 0.8095: 48 (21%) | 0.1127: 46 (20%); 0.3087: 91 (40%); 0.631: 139 (61%); 0.8095: 183 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.01, 16.028, 17.93, 24.086 | 14.01: 183 (80%); 16.028: 137 (60%); 17.93: 92 (40%); 24.086: 46 (20%) | 14.01: 47 (21%); 16.028: 91 (40%); 17.93: 139 (61%); 24.086: 182 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 14.01, 16.028, 17.93, 24.086 | 14.01: 183 (80%); 16.028: 137 (60%); 17.93: 92 (40%); 24.086: 46 (20%) | 14.01: 47 (21%); 16.028: 91 (40%); 17.93: 139 (61%); 24.086: 182 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8469, 0.8699, 0.9143, 0.9548 | 0.8469: 182 (80%); 0.8699: 137 (60%); 0.9143: 91 (40%); 0.9548: 46 (20%) | 0.8469: 46 (20%); 0.8699: 91 (40%); 0.9143: 137 (60%); 0.9548: 183 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.624, 0.74, 0.85, 1.02 | 0.624: 182 (80%); 0.74: 141 (62%); 0.85: 92 (40%); 1.02: 47 (21%) | 0.624: 46 (20%); 0.74: 92 (40%); 0.85: 139 (61%); 1.02: 183 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0141, 0.046, 0.0853, 0.1245 | 0.0141: 182 (80%); 0.046: 137 (60%); 0.0853: 91 (40%); 0.1245: 46 (20%) | 0.0141: 46 (20%); 0.046: 91 (40%); 0.0853: 137 (60%); 0.1245: 182 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 46.3557, 70.4068, 104.7919, 186.9783 | 46.3557: 182 (80%); 70.4068: 137 (60%); 104.7919: 91 (40%); 186.9783: 46 (20%) | 46.3557: 46 (20%); 70.4068: 91 (40%); 104.7919: 137 (60%); 186.9783: 182 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 45.2951, 68.171, 100.0629, 178.3846 | 45.2951: 182 (80%); 68.171: 137 (60%); 100.0629: 91 (40%); 178.3846: 46 (20%) | 45.2951: 46 (20%); 68.171: 91 (40%); 100.0629: 137 (60%); 178.3846: 182 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 43.479, 66.2818, 97.4469, 169.4782 | 43.479: 182 (80%); 66.2818: 137 (60%); 97.4469: 91 (40%); 169.4782: 46 (20%) | 43.479: 46 (20%); 66.2818: 91 (40%); 97.4469: 137 (60%); 169.4782: 182 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 47.3962, 74.0104, 110.5359, 194.7519 | 47.3962: 182 (80%); 74.0104: 137 (60%); 110.5359: 91 (40%); 194.7519: 46 (20%) | 47.3962: 46 (20%); 74.0104: 91 (40%); 110.5359: 137 (60%); 194.7519: 182 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 48.2081, 75.3736, 114.1931, 205.2593 | 48.2081: 182 (80%); 75.3736: 137 (60%); 114.1931: 91 (40%); 205.2593: 46 (20%) | 48.2081: 46 (20%); 75.3736: 91 (40%); 114.1931: 137 (60%); 205.2593: 182 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 228 (100%) | 0: 203 (89%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 228 (100%) | 0: 205 (90%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 99.6% | -0.0738, -0.0417, 0.0032, 0.0407 | -0.0738: 182 (80%); -0.0417: 136 (60%); 0.0032: 91 (40%); 0.0407: 46 (20%) | -0.0738: 46 (20%); -0.0417: 91 (40%); 0.0032: 136 (60%); 0.0407: 182 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -83.06, -68.028, -48.924, -23.996 | -83.06: 182 (80%); -68.028: 137 (60%); -48.924: 91 (40%); -23.996: 46 (20%) | -83.06: 46 (20%); -68.028: 91 (40%); -48.924: 137 (60%); -23.996: 182 (80%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 98.7% | -0.115, -0.0307, 0.0969, 0.236 | -0.115: 180 (79%); -0.0307: 135 (59%); 0.0969: 90 (39%); 0.236: 45 (20%) | -0.115: 45 (20%); -0.0307: 90 (39%); 0.0969: 135 (59%); 0.236: 180 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 98.7% | 3, 4, 6, 8 | 3: 188 (82%); 4: 161 (71%); 6: 104 (46%); 8: 61 (27%) | 3: 64 (28%); 4: 102 (45%); 6: 141 (62%); 8: 186 (82%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.6% |
| 8k_item_5_02_filed_within_7d | 3.7% |
| above_avwap_20high | 24.1% |
| above_avwap_20low | 71.5% |
| above_avwap_252low | 60.1% |
| above_avwap_50low | 68.0% |
| above_cam_r3 | 12.3% |
| above_cam_r4 | 0.4% |
| above_cpr | 41.7% |
| above_pivot | 37.7% |
| above_prev_high | 10.5% |
| above_prev_low | 82.9% |
| above_r1 | 2.6% |
| above_vwap | 51.8% |
| above_wood_p | 46.5% |
| ad_rising | 46.1% |
| adx_cross_up_20 | 0.4% |
| adx_di_bear | 60.1% |
| adx_di_bull | 39.9% |
| adx_strong | 18.4% |
| adx_trending | 68.4% |
| ao_cross_dn | 2.2% |
| ao_cross_up | 0.9% |
| ao_positive | 39.9% |
| ao_twin_peaks_bull | 3.1% |
| at_key_fib | 2.6% |
| at_key_fib_wide | 9.6% |
| avwap_20high_loss_recent_3d | 13.1% |
| avwap_20high_reclaim_recent_3d | 14.0% |
| avwap_20low_loss_recent_3d | 23.1% |
| avwap_20low_reclaim_recent_3d | 11.5% |
| avwap_252low_loss_recent_3d | 8.8% |
| avwap_252low_reclaim_recent_3d | 4.7% |
| avwap_50low_loss_recent_3d | 20.4% |
| avwap_50low_reclaim_recent_3d | 7.4% |
| bb_10_20_above_mid | 47.8% |
| bb_10_20_expanding | 50.0% |
| bb_10_20_pctb_gt_75 | 18.0% |
| bb_10_20_pctb_gt_8 | 12.7% |
| bb_10_20_pctb_gt_85 | 7.0% |
| bb_10_20_pctb_gt_9 | 3.5% |
| bb_10_20_pctb_gt_95 | 2.2% |
| bb_10_20_pctb_lt_05 | 2.6% |
| bb_10_20_pctb_lt_1 | 7.5% |
| bb_10_20_pctb_lt_15 | 9.2% |
| bb_10_20_pctb_lt_2 | 14.9% |
| bb_10_20_pctb_lt_25 | 23.2% |
| bb_10_20_reclaim_from_lower_recent_3d | 7.9% |
| bb_10_20_reclaim_from_upper_recent_3d | 7.5% |
| bb_10_20_squeeze | 71.9% |
| bb_10_20_touch_lower | 4.8% |
| bb_10_20_touch_upper | 7.0% |
| bb_20_15_above_mid | 39.9% |
| bb_20_15_expanding | 38.6% |
| bb_20_15_pctb_gt_75 | 27.6% |
| bb_20_15_pctb_gt_8 | 22.8% |
| bb_20_15_pctb_gt_85 | 18.9% |
| bb_20_15_pctb_gt_9 | 15.8% |
| bb_20_15_pctb_gt_95 | 11.0% |
| bb_20_15_pctb_lt_05 | 12.3% |
| bb_20_15_pctb_lt_1 | 19.3% |
| bb_20_15_pctb_lt_15 | 26.3% |
| bb_20_15_pctb_lt_2 | 33.8% |
| bb_20_15_pctb_lt_25 | 38.6% |
| bb_20_15_reclaim_from_lower_recent_3d | 8.8% |
| bb_20_15_reclaim_from_upper_recent_3d | 6.6% |
| bb_20_15_squeeze | 56.1% |
| bb_20_15_touch_lower | 16.2% |
| bb_20_15_touch_upper | 18.9% |
| bb_20_20_above_mid | 39.9% |
| bb_20_20_expanding | 38.6% |
| bb_20_20_pctb_gt_75 | 20.6% |
| bb_20_20_pctb_gt_8 | 15.8% |
| bb_20_20_pctb_gt_85 | 8.8% |
| bb_20_20_pctb_gt_9 | 5.7% |
| bb_20_20_pctb_gt_95 | 4.8% |
| bb_20_20_pctb_lt_05 | 3.5% |
| bb_20_20_pctb_lt_1 | 8.3% |
| bb_20_20_pctb_lt_15 | 11.4% |
| bb_20_20_pctb_lt_2 | 19.3% |
| bb_20_20_pctb_lt_25 | 28.9% |
| bb_20_20_reclaim_from_lower_recent_3d | 4.8% |
| bb_20_20_reclaim_from_upper_recent_3d | 4.4% |
| bb_20_20_squeeze | 36.4% |
| bb_20_20_touch_lower | 4.4% |
| bb_20_20_touch_upper | 6.6% |
| bearish_engulfing | 5.3% |
| bearish_pin_bar | 11.8% |
| below_avwap_20high | 75.9% |
| below_avwap_20low | 28.5% |
| below_avwap_252low | 39.9% |
| below_avwap_50low | 32.0% |
| below_cam_s3 | 30.3% |
| below_cam_s4 | 1.3% |
| below_cpr | 61.4% |
| below_ema_20 | 60.1% |
| below_ema_200 | 56.6% |
| below_ema_200_break_recent_5d | 3.5% |
| below_ema_20_break_recent_5d | 10.1% |
| below_ema_21 | 60.1% |
| below_ema_21_break_recent_5d | 10.1% |
| below_ema_50 | 60.1% |
| below_ema_50_break_recent_5d | 6.1% |
| below_ema_9 | 58.3% |
| below_ema_9_break_recent_5d | 35.5% |
| below_prev_high | 89.0% |
| below_prev_low | 15.8% |
| below_prev_low_clearance_atr_05 | 0.4% |
| below_s1 | 3.5% |
| below_s2 | 0.4% |
| below_sma_20 | 60.1% |
| below_sma_200 | 58.4% |
| below_sma_21 | 60.5% |
| below_sma_50 | 60.1% |
| below_sma_9 | 53.1% |
| below_vwap | 48.2% |
| blowoff_recent_3d | 1.3% |
| break_52w_high | 0.4% |
| break_52w_high_confirmed_today | 0.4% |
| break_52w_low | 0.9% |
| bullish_engulfing | 0.4% |
| bullish_pin_bar | 11.0% |
| ceo_buy | 0.9% |
| chandelier_long_bullish | 50.0% |
| chandelier_long_flip_dn | 2.2% |
| chandelier_short_bearish | 68.4% |
| chandelier_short_flip_up | 1.3% |
| close_above_open | 27.6% |
| close_below_open | 70.6% |
| close_in_bottom_40pct_of_range | 52.2% |
| close_in_top_40pct_of_range | 25.0% |
| cmf_cross_dn | 3.5% |
| cmf_cross_up | 2.6% |
| cmf_negative | 51.8% |
| cmf_positive | 47.8% |
| concentrated_sell | 6.8% |
| cpr_narrow | 86.4% |
| cpr_narrow_tight | 29.8% |
| cup_handle_detected | 17.6% |
| cup_handle_neckline_break_retest_long | 3.9% |
| dc10_breakout_dn | 9.2% |
| dc10_breakout_dn_1pct | 18.0% |
| dc10_breakout_up | 7.0% |
| dc10_breakout_up_1pct | 18.0% |
| dc10_new_high | 11.4% |
| dc10_strong_breakout_dn | 0.4% |
| dc20_breakout_dn | 3.5% |
| dc20_breakout_up | 4.4% |
| dc20_new_high | 6.1% |
| dc20_resistance_break_retest_strong | 11.8% |
| dc20_support_break_retest_strong | 18.9% |
| defensive_leadership | 51.3% |
| director_only_buy | 2.7% |
| doji | 8.3% |
| double_bottom_detected | 9.2% |
| double_top_detected | 13.2% |
| dpi_elevated | 53.9% |
| drying_volume_on_down_turn | 54.4% |
| drying_volume_on_up_turn | 21.5% |
| ema_20_50_bearish | 62.3% |
| ema_20_50_bullish | 37.7% |
| ema_20_50_death_cross | 0.4% |
| ema_20_50_golden_cross | 0.9% |
| ema_50_200_bearish | 53.5% |
| ema_50_200_bullish | 46.5% |
| ema_50_200_death_cross | 0.9% |
| ema_9_21_bearish | 60.1% |
| ema_9_21_bullish | 39.9% |
| ema_9_21_death_cross | 0.4% |
| ema_9_21_golden_cross | 0.4% |
| evening_star | 3.9% |
| flag_bear_break_retest_short | 2.6% |
| flag_bear_broke | 2.2% |
| flag_bear_detected | 4.4% |
| flag_bull_break_retest_long | 1.8% |
| flag_bull_broke | 1.8% |
| flag_bull_detected | 4.8% |
| force_index_cross_dn | 2.2% |
| force_index_cross_up | 1.8% |
| force_index_positive | 43.4% |
| gap_dn_1_5pct | 5.7% |
| gap_dn_2pct | 2.2% |
| gap_up_1_5pct | 2.2% |
| gap_up_2pct | 0.4% |
| hammer | 7.0% |
| head_shoulders_bottom_detected | 2.2% |
| head_shoulders_top_detected | 3.5% |
| house_cluster_buy | 3.6% |
| house_cluster_sell | 2.7% |
| htf_aligned_bear | 49.3% |
| htf_aligned_bull | 33.9% |
| htf_disagreement | 1.8% |
| hull_bearish | 49.1% |
| hull_bullish | 50.9% |
| hull_flip_dn | 7.9% |
| hull_flip_up | 6.6% |
| ichi_above_cloud | 36.4% |
| ichi_above_cloud_break_recent_5d | 3.9% |
| ichi_below_cloud | 60.5% |
| ichi_below_cloud_break_recent_5d | 7.9% |
| ichi_cloud_thick | 86.0% |
| ichi_tk_bearish | 58.8% |
| ichi_tk_bullish | 39.0% |
| ichi_tk_cross_dn | 0.9% |
| ichi_tk_cross_up | 0.9% |
| ichi_weekly_above_cloud | 40.4% |
| ichi_weekly_below_cloud | 39.5% |
| ichi_weekly_in_cloud | 20.2% |
| inside_bar | 11.4% |
| inside_cpr | 3.9% |
| inside_kc | 93.9% |
| insider_cluster_active | 42.9% |
| institutional_buy | 89.5% |
| institutional_negative | 2.6% |
| institutional_persistence_growing | 47.5% |
| institutional_persistence_strong | 60.9% |
| institutional_strong_buy | 80.3% |
| inverted_cup_handle_detected | 11.5% |
| is_friday | 19.7% |
| is_halloween_period | 44.7% |
| is_halloween_period_first_day | 0.4% |
| is_january | 9.2% |
| is_january_extended | 13.2% |
| is_monday | 18.0% |
| is_pre_holiday | 5.3% |
| is_summer_period | 55.3% |
| is_totm_window | 38.6% |
| is_totm_window_first_day | 14.5% |
| is_week_open | 21.1% |
| kc_touch_lower | 6.1% |
| kc_touch_upper | 6.6% |
| large_dollar_buy | 0.5% |
| macd_12_26_9_bearish | 50.9% |
| macd_12_26_9_bullish | 49.1% |
| macd_12_26_9_crossover_dn | 2.6% |
| macd_12_26_9_crossover_up | 3.9% |
| macd_8_21_5_bearish | 50.4% |
| macd_8_21_5_bullish | 49.6% |
| macd_8_21_5_crossover_dn | 2.6% |
| macd_8_21_5_crossover_up | 1.8% |
| mfi_broad_overbought | 2.6% |
| mfi_broad_oversold | 7.0% |
| mfi_oversold | 1.3% |
| monthly_above_sma_12 | 43.5% |
| monthly_above_sma_6 | 39.0% |
| monthly_bias_bear | 53.4% |
| monthly_bias_bull | 35.9% |
| monthly_momentum_pos | 46.2% |
| morning_star | 0.9% |
| near_52w_high | 12.3% |
| near_52w_high_95pct | 21.5% |
| near_52w_low | 6.6% |
| near_52w_low_105pct | 17.5% |
| near_52w_low_retest_short | 2.2% |
| near_avwap_20high_atr_05x | 42.5% |
| near_avwap_20high_atr_10x | 67.8% |
| near_avwap_20high_atr_15x | 89.3% |
| near_avwap_20high_atr_20x | 97.2% |
| near_avwap_20low_atr_05x | 54.3% |
| near_avwap_20low_atr_10x | 76.0% |
| near_avwap_20low_atr_15x | 90.4% |
| near_avwap_20low_atr_20x | 93.8% |
| near_avwap_252low_atr_05x | 18.6% |
| near_avwap_252low_atr_10x | 26.5% |
| near_avwap_252low_atr_15x | 32.1% |
| near_avwap_252low_atr_20x | 42.8% |
| near_avwap_50low_atr_05x | 37.5% |
| near_avwap_50low_atr_10x | 48.1% |
| near_avwap_50low_atr_15x | 55.6% |
| near_avwap_50low_atr_20x | 63.4% |
| near_cam_r3 | 40.8% |
| near_cam_s3 | 69.7% |
| near_cam_s4 | 15.8% |
| near_fib_236 | 3.9% |
| near_fib_382 | 0.9% |
| near_fib_500 | 1.3% |
| near_fib_618 | 0.9% |
| near_fib_786 | 8.8% |
| near_pivot | 41.7% |
| near_prev_close | 27.6% |
| near_prev_high | 15.4% |
| near_prev_low | 23.7% |
| near_r1 | 15.8% |
| near_r1_wide | 71.5% |
| near_r2 | 3.9% |
| near_r2_wide | 42.1% |
| near_s1 | 22.8% |
| near_s1_wide | 90.4% |
| near_s2 | 2.6% |
| near_s2_wide | 50.0% |
| near_s3 | 1.8% |
| near_wood_r1 | 17.1% |
| near_wood_s1 | 21.9% |
| news_uses_polygon_score | 20.2% |
| obv_bearish | 39.9% |
| obv_bullish | 60.1% |
| obv_diverge_bull | 15.4% |
| obv_falling | 48.2% |
| obv_rising | 51.8% |
| outside_bar | 9.2% |
| pead_negative_surprise | 13.4% |
| pead_positive_surprise | 23.0% |
| pin_bar | 22.8% |
| po3_accumulation_active | 56.1% |
| po3_bearish | 17.2% |
| po3_bullish | 6.2% |
| po3_manipulation_sweep_down | 10.1% |
| po3_manipulation_sweep_up | 13.2% |
| po3_mmbm_setup | 1.3% |
| po3_mmsm_setup | 7.0% |
| po3_sweep_above_prior_high | 56.4% |
| po3_sweep_below_prior_low | 55.1% |
| ppo_bullish | 46.1% |
| ppo_crossover_dn | 2.6% |
| ppo_crossover_up | 3.5% |
| pre_fomc_d0 | 3.9% |
| pre_fomc_d1 | 2.2% |
| pre_fomc_window | 6.1% |
| price_above_dema | 47.8% |
| price_above_ema_20 | 39.9% |
| price_above_ema_200 | 43.4% |
| price_above_ema_200_break_recent_5d | 6.2% |
| price_above_ema_20_break_recent_5d | 9.2% |
| price_above_ema_21 | 39.9% |
| price_above_ema_21_break_recent_5d | 8.8% |
| price_above_ema_50 | 39.9% |
| price_above_ema_50_break_recent_5d | 7.5% |
| price_above_ema_9 | 41.7% |
| price_above_ema_9_break_recent_5d | 26.3% |
| price_above_hull | 53.9% |
| price_above_sma_200 | 41.6% |
| price_above_sma_21 | 39.5% |
| price_above_sma_50 | 39.9% |
| price_above_tema | 57.9% |
| price_below_dema | 52.2% |
| price_below_hull | 46.1% |
| price_below_tema | 42.1% |
| psar_bullish | 51.3% |
| psar_flip_dn | 3.1% |
| psar_flip_up | 6.1% |
| r1_break_retest_long | 51.3% |
| resistance_break_retest | 14.5% |
| risk_off_regime_bond_signal | 19.7% |
| risk_off_regime_bond_signal_strong | 6.6% |
| risk_off_regime_gold_signal | 39.0% |
| risk_on_regime_bond_signal | 49.6% |
| risk_on_regime_bond_signal_strong | 19.7% |
| roc_positive | 41.2% |
| roc_turning_dn | 6.1% |
| roc_turning_up | 4.4% |
| rsi_14_bullish | 39.9% |
| rsi_14_cross_dn_overbought_recent_3d | 2.6% |
| rsi_14_cross_up_oversold_recent_3d | 5.3% |
| rsi_14_extreme_os | 0.4% |
| rsi_14_overbought | 3.1% |
| rsi_14_oversold | 0.9% |
| rsi_14_rising | 32.5% |
| rsi_21_bullish | 39.9% |
| rsi_21_cross_dn_overbought_recent_3d | 1.3% |
| rsi_21_cross_up_oversold_recent_3d | 0.4% |
| rsi_21_extreme_os | 0.4% |
| rsi_21_overbought | 1.8% |
| rsi_21_oversold | 0.4% |
| rsi_21_rising | 32.5% |
| rsi_2_bullish | 42.5% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 31.1% |
| rsi_2_cross_dn_overbought_recent_3d | 39.5% |
| rsi_2_cross_up_extreme_os_recent_3d | 19.3% |
| rsi_2_cross_up_oversold_recent_3d | 28.9% |
| rsi_2_extreme_ob | 16.7% |
| rsi_2_extreme_os | 22.8% |
| rsi_2_overbought | 24.1% |
| rsi_2_oversold | 33.3% |
| rsi_2_rising | 32.5% |
| rsi_9_bullish | 39.9% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 0.4% |
| rsi_9_cross_dn_overbought_recent_3d | 4.8% |
| rsi_9_cross_up_extreme_os_recent_3d | 0.4% |
| rsi_9_cross_up_oversold_recent_3d | 10.5% |
| rsi_9_extreme_os | 0.4% |
| rsi_9_overbought | 6.6% |
| rsi_9_oversold | 5.7% |
| rsi_9_rising | 32.5% |
| s1_break_retest_short | 51.3% |
| sc_13d_filed_within_30d | 5.6% |
| sc_13g_filed_within_30d | 1.4% |
| sector_outperforming_spy | 66.7% |
| sector_underperforming_spy | 33.3% |
| shooting_star | 7.0% |
| sma_20_50_bullish | 39.0% |
| sma_20_50_golden_cross | 0.9% |
| sma_50_200_bullish | 50.9% |
| sma_9_21_bullish | 40.8% |
| sma_9_21_golden_cross | 2.6% |
| smc_bos_bearish | 18.9% |
| smc_bos_bullish | 14.1% |
| smc_bos_retest_long | 4.0% |
| smc_bos_retest_short | 3.1% |
| smc_breaker_block_bearish | 16.3% |
| smc_breaker_block_bullish | 24.7% |
| smc_choch_bearish | 7.0% |
| smc_choch_bullish | 4.8% |
| smc_equal_highs_swept | 2.6% |
| smc_equal_lows_swept | 7.0% |
| smc_fvg_bearish_active | 32.2% |
| smc_fvg_bullish_active | 30.8% |
| smc_fvg_retest_long_zone | 4.4% |
| smc_fvg_retest_short_zone | 3.1% |
| smc_in_discount_zone | 62.6% |
| smc_in_premium_zone | 40.1% |
| smc_inverse_fvg_bearish | 72.2% |
| smc_inverse_fvg_bullish | 61.7% |
| smc_liquidity_swept_dn | 0.9% |
| smc_liquidity_swept_up | 0.4% |
| smc_mitigation_block_long | 0.9% |
| smc_mitigation_block_short | 2.2% |
| smc_ob_bearish_active | 43.6% |
| smc_ob_bullish_active | 31.7% |
| smc_ote_long_zone | 7.9% |
| smc_ote_short_zone | 4.8% |
| squeeze_fire_dn | 0.9% |
| squeeze_fire_up | 0.4% |
| squeeze_in | 30.3% |
| squeeze_positive | 39.9% |
| stoch_bearish_cross | 8.8% |
| stoch_broad_overbought | 18.4% |
| stoch_broad_oversold | 23.2% |
| stoch_bullish_cross | 5.7% |
| stoch_overbought | 12.3% |
| stoch_oversold | 15.8% |
| stochrsi_cross_dn | 25.0% |
| stochrsi_cross_up | 31.1% |
| stochrsi_overbought | 31.1% |
| stochrsi_oversold | 25.9% |
| supertrend_bearish | 1.8% |
| supertrend_bullish | 98.2% |
| supertrend_flip_recent_long_5d | 3.1% |
| supertrend_flip_recent_short_5d | 1.8% |
| support_break_retest | 26.8% |
| tema_above_dema | 35.5% |
| tema_cross_dn | 2.6% |
| tema_cross_up | 1.8% |
| three_black_crows | 4.4% |
| three_white_soldiers | 1.8% |
| triangle_apex_break_retest_long | 8.3% |
| triangle_ascending_detected | 8.3% |
| triangle_descending_detected | 8.3% |
| uo_overbought | 0.4% |
| uo_oversold | 2.6% |
| usd_strengthening | 31.6% |
| usd_weakening | 6.6% |
| vix_band_high | 36.8% |
| vix_band_low | 42.1% |
| vix_band_mid | 21.1% |
| vix_term_backwardation | 7.0% |
| vix_term_contango | 93.0% |
| vol_above_avg | 22.8% |
| vol_below_avg | 77.2% |
| vol_spike_12x | 11.4% |
| vol_spike_15x | 2.6% |
| vol_spike_17x | 0.9% |
| vol_spike_2x | 0.4% |
| vol_spike_2x_on_down_day_recent_3d | 0.9% |
| vol_spike_2x_on_up_day_recent_3d | 3.5% |
| vp_above_value_area | 23.7% |
| vp_below_value_area | 34.6% |
| vp_close_above_poc | 39.5% |
| vp_close_below_poc | 60.5% |
| vp_in_value_area | 41.7% |
| week_open_gap_down_15pct | 2.6% |
| weekly_above_ema_10 | 40.1% |
| weekly_above_ema_20 | 39.2% |
| weekly_bias_bear | 59.0% |
| weekly_bias_bull | 38.3% |
| weekly_momentum_pos | 41.4% |
| williams_r_overbought | 15.8% |
| williams_r_oversold | 21.9% |
| williams_r_rising | 39.5% |
| within_pead_window | 46.0% |
| within_post_deletion_window | 12.5% |
| within_post_inclusion_window | 8.7% |
| xs_avoid_high_ivol | 81.2% |
| xs_avoid_high_max | 83.4% |
| xs_high_beta_decile | 11.2% |
| xs_low_beta_bottom_quintile | 11.2% |
| xs_low_beta_decile | 23.8% |
| xs_low_beta_decile_entry_recent_5d | 0.4% |
| xs_low_beta_top_quintile | 23.8% |
| xs_momentum_bottom_decile | 6.2% |
| xs_momentum_bottom_quintile | 16.4% |
| xs_momentum_top_decile | 8.9% |
| xs_momentum_top_quintile | 17.3% |
| xs_quality_bottom_quintile | 12.4% |
| xs_quality_top_quintile | 22.1% |
| xs_quality_top_tercile | 46.2% |
| year_high_break_retest_long | 2.6% |
| year_low_break_retest_short | 3.9% |
| yoy_surprise_high | 55.3% |
| yoy_surprise_negative | 32.7% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 88.6% |
| committed_growth_holders | 88.6% |
| corp_donations_1y | 6.1% |
| corp_donations_count_1y | 6.1% |
| corp_donations_unique_pacs | 6.1% |
| cot_rut_commercials_pctile_3y | 56.1% |
| cot_rut_mmoney_pctile_3y | 56.1% |
| cup_handle_depth_pct | 20.6% |
| days_since_deletion | 7.0% |
| days_since_inclusion | 10.1% |
| days_to_next_holiday | 67.5% |
| days_to_rebalance | 8.3% |
| dpi_30d_avg | 96.1% |
| dpi_recent | 96.1% |
| earnings_announcement_return | 91.7% |
| earnings_eps_yoy_growth | 95.2% |
| flag_bear_pole_move_pct | 4.4% |
| flag_bull_pole_move_pct | 4.8% |
| gov_contracts_4q_sum | 43.0% |
| gov_contracts_last_qtr_amount | 43.0% |
| gov_contracts_qoq_growth | 43.0% |
| head_shoulders_magnitude_pct | 5.7% |
| insider_director_buyers_30d | 3.1% |
| insider_officer_buyers_30d | 3.1% |
| insider_total_shares_bought_30d | 3.1% |
| insider_unique_buyers_30d | 3.1% |
| inverted_cup_handle_height_pct | 17.1% |
| lobbying_amount_1y | 65.8% |
| lobbying_amount_q | 65.8% |
| lobbying_amount_yoy | 65.8% |
| monthly_momentum_6m | 97.8% |
| otc_short_ratio_recent | 96.1% |
| otc_volume_recent | 96.1% |
| pair_half_life | 92.1% |
| pair_max_abs_zscore | 92.1% |
| pair_zscore_signed | 92.1% |
| pct_from_avwap_20high | 93.9% |
| pct_from_avwap_20low | 91.2% |
| pct_from_avwap_252low | 94.3% |
| pct_from_avwap_50low | 94.7% |
| persistent_holders_4q | 88.6% |
| persistent_holders_8q | 88.6% |
| search_volume_index_recent | 80.7% |
| search_volume_observations | 80.7% |
| search_volume_zscore_30d | 80.7% |
| sector_etf_return_20d | 2.6% |
| short_interest_pct | 94.7% |
| spy_return_20d | 2.6% |
| total_active_holders | 88.6% |
| triangle_breakdown_pct | 8.3% |
| triangle_breakout_pct | 8.3% |
| xs_beta | 97.8% |
| xs_beta_decile | 97.8% |
| xs_ivol | 97.8% |
| xs_ivol_decile | 97.8% |
| xs_max_anomaly | 97.8% |
| xs_max_anomaly_decile | 97.8% |
| xs_quality_decile | 63.6% |
| xs_quality_gross_profitability | 63.6% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.996), `avwap_252low` (0.993), `avwap_50low` (0.996), `bb_10_20_lower` (0.995), `bb_10_20_mid` (0.998), `bb_10_20_upper` (0.998), `bb_20_15_lower` (0.995), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.997), `bb_20_20_lower` (0.995), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.997), `cam_r1` (0.996), `cam_r2` (0.996), `cam_r3` (0.996), `cam_r4` (0.996), `cam_s1` (0.996), `cam_s2` (0.996), `cam_s3` (0.996), `cam_s4` (0.996), `chandelier_long_value` (0.998), `chandelier_short_value` (0.997), `cpr_bottom` (0.996), `cpr_top` (0.996), `cup_handle_breakout_level` (0.998), `cup_handle_rim` (0.996), `days_since_classification_change` (1.0), `dc10_lower` (0.996), `dc10_mid` (1.0), `dc10_upper` (0.999), `dc20_lower` (0.996), `dc20_mid` (1.0), `dc20_upper` (0.998), `dema` (0.997), `double_bottom_neckline` (0.992), `double_bottom_trough` (0.991), `double_top_neckline` (0.995), `double_top_peak` (0.996), `entry_stop_long` (0.995), `entry_stop_short` (0.997), `fib_236` (0.995), `fib_382` (0.996), `fib_500` (0.996), `fib_618` (0.996), `fib_786` (0.995), `fib_ext_127` (0.992), `fib_ext_162` (0.989), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (1.0), `head_shoulders_top_neckline` (1.0), `hull_ma` (0.995), `ichi_kijun` (0.999), `ichi_senkou_a` (0.991), `ichi_senkou_b` (0.988), `ichi_tenkan` (1.0), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.987), `monthly_sma_6` (0.994), `pivot` (0.996), `prev_close` (0.996), `prev_high` (0.996), `prev_low` (0.996), `psar_value` (0.999), `r1` (0.996), `r2` (0.996), `r3` (0.996), `s1` (0.996), `s2` (0.996), `s3` (0.996), `sc_13g_latest_percent_owned` (-1.0), `supertrend_value` (0.997), `swing_high` (0.994), `swing_low` (0.991), `tema` (0.996), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.994), `vp_value_area_high` (0.994), `vp_value_area_low` (0.993), `weekly_close` (0.996), `weekly_ema_10` (0.999), `weekly_ema_20` (0.995), `wood_p` (0.996), `wood_r1` (0.996), `wood_r2` (0.996), `wood_s1` (0.996), `wood_s2` (0.996), `year_high` (0.984), `year_low` (0.978)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | proximity tolerance to Camarilla R3 (abs | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1 | proximity tolerance to Camarilla S3 (abs | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P3.1 | mirror of obv_bullish | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P4.1 | obv vs its moving average | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P4.2 | margin pct over the MA | 1 | subset-safe | no - derives offline |
| P5 | rsi_14 < 40 | 3 | subset-safe | no - derives offline |
| P6 | rsi_14 > 60 | 2 | subset-safe | no - derives offline |
| P7 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     1 x 1 x 1 x 1 x 1 x 3 x 2 x 1 = 6
offline gradings   6 level-combinations x 24 exits = 144
ENGINE RUNS        1 (every fire-adding axis sits at production-only until its env actuator exists)
check              1 x 6 = 6
```

B-row candidates NOT in this factorial: 618 census axes join it only when REGISTERED at the T3 band review.
