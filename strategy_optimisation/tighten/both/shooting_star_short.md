# Table A - shooting_star_short

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit fa06ebf3e at 2026-09-19 13:07:41 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** candle | **status:** NOT-STARTED | **R5 fires:** 250 | **surviving fires (T1):** 250 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  bb_20_20_touch_upper  <- backtest/signals/screener.py
       DEFN: close at/beyond the Bollinger(20, 2.0) band (bb block)
       knobs P1.1-P1.1 (band rows in Table A)
P2  bearish_pin_bar  <- backtest/signals/screener.py +1
       DEFN: canonical single/two-candle reversal pattern (Nison; compute_candle_signals - geometry in producer)
       knobs P2.1-P2.1 (band rows in Table A)
P3  dark_cloud_cover  <- backtest/signals/screener.py +1
       DEFN: canonical single/two-candle reversal pattern (Nison; compute_candle_signals - geometry in producer)
       knobs P3.1-P3.1 (band rows in Table A)
P4  hanging_man  <- backtest/signals/screener.py +1
       DEFN: canonical single/two-candle reversal pattern (Nison; compute_candle_signals - geometry in producer)
       knobs P4.1-P4.1 (band rows in Table A)
P5  near_r1  <- backtest/signals/screener.py +1
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P5.1-P5.1 (band rows in Table A)
P6  near_r2  <- backtest/signals/screener.py +1
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P6.1-P6.1 (band rows in Table A)
P7  shooting_star  <- backtest/signals/screener.py +1
       DEFN: canonical single/two-candle reversal pattern (Nison; compute_candle_signals - geometry in producer)
       knobs P7.1-P7.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P8  rsi_14 > 65   [EXISTING-THRESHOLD]
P9  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_shooting_star_short (docstring and return dropped):

```python
fires = (s.get('shooting_star') or s.get('bearish_pin_bar') or s.get('hanging_man') or s.get('dark_cloud_cover')) and (s.get('near_r1') or s.get('near_r2') or s.get('bb_20_20_touch_upper')) and (s.get('rsi_14', 50) > 65) and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | bb_20_20_touch_upper - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close at/beyond the Bollinger(20, 2.0) band (bb block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | mirror of touch_lower - backtest/signals/technical.py bb block | mirror | (20, 2.0) | k [1.5, 2.0, 2.5] | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | bearish_pin_bar - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | canonical single/two-candle reversal pattern (Nison; compute_candle_signals - geometry in producer) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | implicit anatomy knobs (min body/wick/step pct) - backtest/signals/technical.py:candle block (B641 W3) (compute_candle_signals) | CANON candle anatomy (Nison); production accepts any magnitude | 0 / absent (any magnitude counts) | [0, 0.3, 0.5] per knob | none - pattern bars' OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | dark_cloud_cover - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | canonical single/two-candle reversal pattern (Nison; compute_candle_signals - geometry in producer) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | implicit anatomy knobs (min body/wick/step pct) - backtest/signals/technical.py:candle block (compute_candle_signals) | CANON candle anatomy (Nison); production accepts any magnitude | 0 / absent (any magnitude counts) | [0, 0.3, 0.5] per knob | none - pattern bars' OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | PRODUCER | hanging_man - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | canonical single/two-candle reversal pattern (Nison; compute_candle_signals - geometry in producer) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P4.x) | BANDS-DEFINED |
| P4.1 | BAND | implicit anatomy knobs (min body/wick/step pct) - backtest/signals/technical.py:candle block (compute_candle_signals) | CANON candle anatomy (Nison); production accepts any magnitude | 0 / absent (any magnitude counts) | [0, 0.3, 0.5] per knob | none - pattern bars' OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | PRODUCER | near_r1 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P5.x) | BANDS-DEFINED |
| P5.1 | BAND | proximity tolerance to R1 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P6 | PRODUCER | near_r2 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P6.x) | BANDS-DEFINED |
| P6.1 | BAND | proximity tolerance to R2 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P7 | PRODUCER | shooting_star - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | canonical single/two-candle reversal pattern (Nison; compute_candle_signals - geometry in producer) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P7.x) | BANDS-DEFINED |
| P7.1 | BAND | implicit anatomy knobs (min body/wick/step pct) - backtest/signals/technical.py:candle block (compute_candle_signals) | CANON candle anatomy (Nison); production accepts any magnitude | 0 / absent (any magnitude counts) | [0, 0.3, 0.5] per knob | none - pattern bars' OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P8 | STRATEGY | rsi_14 `> 65` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `> 65` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P8.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P9 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `> 65` | 100.0% | TIGHTER = RAISE the floor: 67.164 -> 200 (80%); 69.504 -> 150 (60%); 71.588 -> 100 (40%); 75.124 -> 50 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 19.218, 23.328, 27.282, 34.856 | 19.218: 200 (80%); 23.328: 150 (60%); 27.282: 100 (40%); 34.856: 50 (20%) | 19.218: 50 (20%); 23.328: 100 (40%); 27.282: 150 (60%); 34.856: 200 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 10.164, 12.298, 13.88, 15.552 | 10.164: 200 (80%); 12.298: 150 (60%); 13.88: 101 (40%); 15.552: 50 (20%) | 10.164: 50 (20%); 12.298: 100 (40%); 13.88: 151 (60%); 15.552: 200 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 34.478, 37.412, 40.434, 44.792 | 34.478: 200 (80%); 37.412: 150 (60%); 40.434: 100 (40%); 44.792: 50 (20%) | 34.478: 50 (20%); 37.412: 100 (40%); 40.434: 150 (60%); 44.792: 200 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | 2.4261, 4.1937, 8.4562, 14.5685 | 2.4261: 200 (80%); 4.1937: 150 (60%); 8.4562: 100 (40%); 14.5685: 50 (20%) | 2.4261: 50 (20%); 4.1937: 100 (40%); 8.4562: 150 (60%); 14.5685: 200 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.2409, 2.1542, 3.684, 5.897 | 1.2409: 200 (80%); 2.1542: 150 (60%); 3.684: 100 (40%); 5.897: 50 (20%) | 1.2409: 50 (20%); 2.1542: 100 (40%); 3.684: 150 (60%); 5.897: 200 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.2409, 2.1542, 3.684, 5.897 | 1.2409: 200 (80%); 2.1542: 150 (60%); 3.684: 100 (40%); 5.897: 50 (20%) | 1.2409: 50 (20%); 2.1542: 100 (40%); 3.684: 150 (60%); 5.897: 200 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.8074, 2.135, 2.46, 2.968 | 1.8074: 200 (80%); 2.135: 150 (60%); 2.46: 101 (40%); 2.968: 50 (20%) | 1.8074: 50 (20%); 2.135: 100 (40%); 2.46: 151 (60%); 2.968: 200 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0747, 0.1032, 0.1319, 0.1802 | 0.0747: 200 (80%); 0.1032: 151 (60%); 0.1319: 100 (40%); 0.1802: 50 (20%) | 0.0747: 51 (20%); 0.1032: 101 (40%); 0.1319: 150 (60%); 0.1802: 200 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.8299, 0.8678, 0.9075, 0.9635 | 0.8299: 200 (80%); 0.8678: 150 (60%); 0.9075: 100 (40%); 0.9635: 50 (20%) | 0.8299: 50 (20%); 0.8678: 100 (40%); 0.9075: 150 (60%); 0.9635: 200 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0653, 0.088, 0.1096, 0.1405 | 0.0653: 200 (80%); 0.088: 150 (60%); 0.1096: 100 (40%); 0.1405: 50 (20%) | 0.0653: 50 (20%); 0.088: 100 (40%); 0.1096: 150 (60%); 0.1405: 200 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 1.1031, 1.1555, 1.2136, 1.3083 | 1.1031: 200 (80%); 1.1555: 150 (60%); 1.2136: 100 (40%); 1.3083: 50 (20%) | 1.1031: 50 (20%); 1.1555: 100 (40%); 1.2136: 150 (60%); 1.3083: 200 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.087, 0.1173, 0.1461, 0.1874 | 0.087: 200 (80%); 0.1173: 150 (60%); 0.1461: 100 (40%); 0.1874: 50 (20%) | 0.087: 50 (20%); 0.1173: 100 (40%); 0.1461: 150 (60%); 0.1874: 200 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.9523, 0.9917, 1.0352, 1.1063 | 0.9523: 200 (80%); 0.9917: 150 (60%); 1.0352: 100 (40%); 1.1063: 50 (20%) | 0.9523: 50 (20%); 0.9917: 100 (40%); 1.0352: 150 (60%); 1.1063: 200 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0602, -0.029, -0.0138, 0.0128 | -0.0602: 202 (81%); -0.029: 150 (60%); -0.0138: 100 (40%); 0.0128: 51 (20%) | -0.0602: 51 (20%); -0.029: 100 (40%); -0.0138: 150 (60%); 0.0128: 201 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.144, 0.1691, 0.1925, 0.2488 | 0.144: 200 (80%); 0.1691: 152 (61%); 0.1925: 100 (40%); 0.2488: 51 (20%) | 0.144: 50 (20%); 0.1691: 98 (39%); 0.1925: 150 (60%); 0.2488: 199 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 250 (100%) | 0: 244 (98%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | 0.0001, 0.0668, 0.1348, 0.2127 | 0.0001: 200 (80%); 0.0668: 150 (60%); 0.1348: 100 (40%); 0.2127: 50 (20%) | 0.0001: 50 (20%); 0.0668: 100 (40%); 0.1348: 150 (60%); 0.2127: 200 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1, 2 | 0: 250 (100%); 1: 111 (44%); 2: 51 (20%) | 0: 139 (56%); 1: 199 (80%); 2: 223 (89%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2381, -0.2048, -0.1647, -0.1336 | -0.2381: 207 (83%); -0.2048: 151 (60%); -0.1647: 100 (40%); -0.1336: 50 (20%) | -0.2381: 51 (20%); -0.2048: 103 (41%); -0.1647: 150 (60%); -0.1336: 200 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3974, 0.5372, 0.6667, 0.7949 | 0.3974: 202 (81%); 0.5372: 150 (60%); 0.6667: 109 (44%); 0.7949: 52 (21%) | 0.3974: 51 (20%); 0.5372: 100 (40%); 0.6667: 151 (60%); 0.7949: 211 (84%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.25, 0.3974, 0.6603, 0.8744 | 0.25: 209 (84%); 0.3974: 152 (61%); 0.6603: 101 (40%); 0.8744: 50 (20%) | 0.25: 52 (21%); 0.3974: 101 (40%); 0.6603: 151 (60%); 0.8744: 200 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1781, -0.0749, 0.0281, 0.1543 | -0.1781: 201 (80%); -0.0749: 150 (60%); 0.0281: 100 (40%); 0.1543: 51 (20%) | -0.1781: 52 (21%); -0.0749: 100 (40%); 0.0281: 150 (60%); 0.1543: 201 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.1538, 0.3154, 0.4641, 0.7115 | 0.1538: 204 (82%); 0.3154: 150 (60%); 0.4641: 100 (40%); 0.7115: 51 (20%) | 0.1538: 58 (23%); 0.3154: 100 (40%); 0.4641: 150 (60%); 0.7115: 202 (81%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0962, 0.273, 0.4551, 0.6616 | 0.0962: 202 (81%); 0.273: 150 (60%); 0.4551: 106 (42%); 0.6616: 50 (20%) | 0.0962: 52 (21%); 0.273: 100 (40%); 0.4551: 152 (61%); 0.6616: 200 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5101, -0.3181, -0.1164, 0.1049 | -0.5101: 203 (81%); -0.3181: 151 (60%); -0.1164: 104 (42%); 0.1049: 50 (20%) | -0.5101: 53 (21%); -0.3181: 101 (40%); -0.1164: 152 (61%); 0.1049: 200 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3077, 0.5833, 0.9038, 0.9615 | 0.3077: 201 (80%); 0.5833: 153 (61%); 0.9038: 101 (40%); 0.9615: 55 (22%) | 0.3077: 52 (21%); 0.5833: 106 (42%); 0.9038: 154 (62%); 0.9615: 201 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0705, 0.3141, 0.5833, 0.9167 | 0.0705: 201 (80%); 0.3141: 152 (61%); 0.5833: 105 (42%); 0.9167: 52 (21%) | 0.0705: 53 (21%); 0.3141: 101 (40%); 0.5833: 151 (60%); 0.9167: 204 (82%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0665, -0.0619, -0.0511, 0 | -0.0665: 200 (80%); -0.0619: 152 (61%); -0.0511: 104 (42%); 0: 69 (28%) | -0.0665: 52 (21%); -0.0619: 105 (42%); -0.0511: 151 (60%); 0: 250 (100%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3077, 0.4936, 0.7756, 1 | 0.3077: 205 (82%); 0.4936: 153 (61%); 0.7756: 101 (40%); 1: 58 (23%) | 0.3077: 51 (20%); 0.4936: 102 (41%); 0.7756: 154 (62%); 1: 250 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.191, 0.4705, 0.6795, 0.9423 | 0.191: 200 (80%); 0.4705: 150 (60%); 0.6795: 102 (41%); 0.9423: 58 (23%) | 0.191: 50 (20%); 0.4705: 100 (40%); 0.6795: 152 (61%); 0.9423: 201 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.036, 0.0222, 0.0645, 0.142 | -0.036: 200 (80%); 0.0222: 150 (60%); 0.0645: 100 (40%); 0.142: 50 (20%) | -0.036: 50 (20%); 0.0222: 100 (40%); 0.0645: 150 (60%); 0.142: 200 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3269, 0.7097, 0.8814, 0.9615 | 0.3269: 207 (83%); 0.7097: 152 (61%); 0.8814: 100 (40%); 0.9615: 51 (20%) | 0.3269: 51 (20%); 0.7097: 101 (40%); 0.8814: 150 (60%); 0.9615: 204 (82%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1795, 0.4782, 0.7179, 0.8475 | 0.1795: 203 (81%); 0.4782: 150 (60%); 0.7179: 107 (43%); 0.8475: 50 (20%) | 0.1795: 53 (21%); 0.4782: 100 (40%); 0.7179: 151 (60%); 0.8475: 200 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0203, 0.0325, 0.1234 | -0.0812: 228 (91%); -0.0203: 153 (61%); 0.0325: 100 (40%); 0.1234: 52 (21%) | -0.0812: 52 (21%); -0.0203: 118 (47%); 0.0325: 150 (60%); 0.1234: 201 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.3022, -0.0788, 0.0239, 0.0754 | -0.3022: 202 (81%); -0.0788: 156 (62%); 0.0239: 100 (40%); 0.0754: 52 (21%) | -0.3022: 52 (21%); -0.0788: 102 (41%); 0.0239: 150 (60%); 0.0754: 200 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.0577, 0.3948, 0.641, 0.8026 | 0.0577: 204 (82%); 0.3948: 150 (60%); 0.641: 104 (42%); 0.8026: 50 (20%) | 0.0577: 52 (21%); 0.3948: 100 (40%); 0.641: 152 (61%); 0.8026: 200 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2692, 0.4602, 0.641, 0.8269 | 0.2692: 204 (82%); 0.4602: 150 (60%); 0.641: 101 (40%); 0.8269: 58 (23%) | 0.2692: 51 (20%); 0.4602: 100 (40%); 0.641: 151 (60%); 0.8269: 204 (82%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0767, 0.1588, 0.3627, 0.7504 | 0.0767: 202 (81%); 0.1588: 150 (60%); 0.3627: 100 (40%); 0.7504: 50 (20%) | 0.0767: 53 (21%); 0.1588: 100 (40%); 0.3627: 150 (60%); 0.7504: 200 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.4% | 11, 56, 77, 111 | 11: 197 (79%); 56: 149 (60%); 77: 101 (40%); 111: 51 (20%) | 11: 50 (20%); 56: 100 (40%); 77: 149 (60%); 111: 197 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.6% | 1.811, 2.4093, 2.8318, 3.6274 | 1.811: 199 (80%); 2.4093: 149 (60%); 2.8318: 100 (40%); 3.6274: 50 (20%) | 1.811: 50 (20%); 2.4093: 100 (40%); 2.8318: 149 (60%); 3.6274: 199 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 9, 19, 27, 40 | 9: 201 (80%); 19: 151 (60%); 27: 105 (42%); 40: 55 (22%) | 9: 62 (25%); 19: 109 (44%); 27: 152 (61%); 40: 207 (83%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3 | 1: 202 (81%); 2: 160 (64%); 3: 110 (44%) | 1: 90 (36%); 2: 140 (56%); 3: 203 (81%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0137, -0.0074, 0, 0.0165 | -0.0137: 201 (80%); -0.0074: 150 (60%); 0: 101 (40%); 0.0165: 51 (20%) | -0.0137: 51 (20%); -0.0074: 100 (40%); 0: 151 (60%); 0.0165: 200 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.6139, 25.7515, 26.4146, 27.0004 | 24.6139: 200 (80%); 25.7515: 152 (61%); 26.4146: 100 (40%); 27.0004: 50 (20%) | 24.6139: 50 (20%); 25.7515: 101 (40%); 26.4146: 150 (60%); 27.0004: 200 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -1.7136, -0.7302, -0.3706, 0 | -1.7136: 200 (80%); -0.7302: 150 (60%); -0.3706: 100 (40%); 0: 51 (20%) | -1.7136: 50 (20%); -0.7302: 100 (40%); -0.3706: 150 (60%); 0: 203 (81%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | 0, 0.3706, 0.7302, 1.7136 | 0: 203 (81%); 0.3706: 150 (60%); 0.7302: 100 (40%); 1.7136: 50 (20%) | 0: 51 (20%); 0.3706: 100 (40%); 0.7302: 150 (60%); 1.7136: 200 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0549, -0.0228, 0.0062, 0.0341 | -0.0549: 200 (80%); -0.0228: 150 (60%); 0.0062: 101 (40%); 0.0341: 50 (20%) | -0.0549: 50 (20%); -0.0228: 100 (40%); 0.0062: 151 (60%); 0.0341: 200 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0796, 8.4646, 8.6405, 8.9746 | 8.0796: 201 (80%); 8.4646: 151 (60%); 8.6405: 100 (40%); 8.9746: 50 (20%) | 8.0796: 51 (20%); 8.4646: 99 (40%); 8.6405: 150 (60%); 8.9746: 200 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.6% | 0, 1 | 0: 249 (100%); 1: 75 (30%) | 0: 174 (70%); 1: 225 (90%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.6% | -1, 0 | -1: 231 (92%); 0: 197 (79%) | -1: 52 (21%); 0: 206 (82%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.6% | 0, 1 | 0: 249 (100%); 1: 84 (34%) | 0: 165 (66%); 1: 222 (89%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 6, 51, 259.2 | 2: 215 (86%); 6: 151 (60%); 51: 101 (40%); 259.2: 50 (20%) | 2: 54 (22%); 6: 115 (46%); 51: 152 (61%); 259.2: 200 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 4, 83, 129.2 | 1: 209 (84%); 4: 157 (63%); 83: 101 (40%); 129.2: 50 (20%) | 1: 60 (24%); 4: 105 (42%); 83: 151 (60%); 129.2: 200 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | 0.2387, 0.4861, 0.935, 1.9204 | 0.2387: 200 (80%); 0.4861: 150 (60%); 0.935: 100 (40%); 1.9204: 50 (20%) | 0.2387: 50 (20%); 0.4861: 100 (40%); 0.935: 150 (60%); 1.9204: 200 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | 0.9793, 1.6979, 3.2925, 5.8792 | 0.9793: 200 (80%); 1.6979: 150 (60%); 3.2925: 100 (40%); 5.8792: 50 (20%) | 0.9793: 50 (20%); 1.6979: 100 (40%); 3.2925: 150 (60%); 5.8792: 200 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | 0.4688, 0.9652, 1.9881, 4.3007 | 0.4688: 200 (80%); 0.9652: 150 (60%); 1.9881: 100 (40%); 4.3007: 50 (20%) | 0.4688: 50 (20%); 0.9652: 100 (40%); 1.9881: 150 (60%); 4.3007: 200 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | 0.2173, 0.4323, 0.8684, 1.6184 | 0.2173: 200 (80%); 0.4323: 150 (60%); 0.8684: 100 (40%); 1.6184: 50 (20%) | 0.2173: 50 (20%); 0.4323: 100 (40%); 0.8684: 150 (60%); 1.6184: 200 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | 1.1987, 2.1774, 3.9777, 7.2571 | 1.1987: 200 (80%); 2.1774: 150 (60%); 3.9777: 100 (40%); 7.2571: 50 (20%) | 1.1987: 50 (20%); 2.1774: 100 (40%); 3.9777: 150 (60%); 7.2571: 200 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | 0.866, 1.6061, 3.2142, 5.3708 | 0.866: 200 (80%); 1.6061: 150 (60%); 3.2142: 100 (40%); 5.3708: 50 (20%) | 0.866: 50 (20%); 1.6061: 100 (40%); 3.2142: 150 (60%); 5.3708: 200 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 62.214, 68.92, 74.746, 79.494 | 62.214: 200 (80%); 68.92: 150 (60%); 74.746: 100 (40%); 79.494: 50 (20%) | 62.214: 50 (20%); 68.92: 100 (40%); 74.746: 150 (60%); 79.494: 200 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 99.2% | 0.0111, 0.1, 0.1732, 0.2962 | 0.0111: 198 (79%); 0.1: 149 (60%); 0.1732: 99 (40%); 0.2962: 50 (20%) | 0.0111: 50 (20%); 0.1: 99 (40%); 0.1732: 149 (60%); 0.2962: 198 (79%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.2% | 0.0137, 0.0339, 0.0551, 0.0869 | 0.0137: 198 (79%); 0.0339: 149 (60%); 0.0551: 99 (40%); 0.0869: 50 (20%) | 0.0137: 50 (20%); 0.0339: 99 (40%); 0.0551: 149 (60%); 0.0869: 198 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 1, 2, 5, 12 | 1: 205 (82%); 2: 175 (70%); 5: 111 (44%); 12: 53 (21%) | 1: 75 (30%); 2: 104 (42%); 5: 153 (61%); 12: 201 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0909 | 0: 250 (100%); 0.0909: 52 (21%) | 0: 175 (70%); 0.0909: 201 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.4088, 0.5616, 0.75 | 0: 250 (100%); 0.4088: 150 (60%); 0.5616: 100 (40%); 0.75: 54 (22%) | 0: 61 (24%); 0.4088: 100 (40%); 0.5616: 150 (60%); 0.75: 202 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 2, 4, 9 | 0: 250 (100%); 2: 158 (63%); 4: 103 (41%); 9: 52 (21%) | 0: 56 (22%); 2: 127 (51%); 4: 160 (64%); 9: 202 (81%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 1, 2, 5, 12 | 1: 205 (82%); 2: 175 (70%); 5: 111 (44%); 12: 53 (21%) | 1: 75 (30%); 2: 104 (42%); 5: 153 (61%); 12: 201 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 250 (100%); 1: 174 (70%); 3: 103 (41%); 8: 51 (20%) | 0: 76 (30%); 1: 113 (45%); 3: 163 (65%); 8: 203 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.1641, 0.3273, 0.4708, 0.6667 | 0.1641: 200 (80%); 0.3273: 150 (60%); 0.4708: 100 (40%); 0.6667: 52 (21%) | 0.1641: 50 (20%); 0.3273: 100 (40%); 0.4708: 150 (60%); 0.6667: 203 (81%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.0563, 0.4251, 0.7394 | 0: 241 (96%); 0.0563: 150 (60%); 0.4251: 100 (40%); 0.7394: 50 (20%) | 0: 98 (39%); 0.0563: 100 (40%); 0.4251: 150 (60%); 0.7394: 200 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3098, 0.5, 0.7 | 0: 245 (98%); 0.3098: 150 (60%); 0.5: 107 (43%); 0.7: 51 (20%) | 0: 69 (28%); 0.3098: 100 (40%); 0.5: 160 (64%); 0.7: 201 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3098, 0.5, 0.7 | 0: 245 (98%); 0.3098: 150 (60%); 0.5: 107 (43%); 0.7: 51 (20%) | 0: 69 (28%); 0.3098: 100 (40%); 0.5: 160 (64%); 0.7: 201 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.0988, 0, 0.1911 | -0.0988: 200 (80%); 0: 186 (74%); 0.1911: 50 (20%) | -0.0988: 50 (20%); 0: 166 (66%); 0.1911: 200 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.5043, 0, 0.6843, 2.6305 | -0.5043: 200 (80%); 0: 166 (66%); 0.6843: 101 (40%); 2.6305: 50 (20%) | -0.5043: 50 (20%); 0: 121 (48%); 0.6843: 152 (61%); 2.6305: 200 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 11 | 2: 211 (84%); 4: 156 (62%); 7: 101 (40%); 11: 51 (20%) | 2: 66 (26%); 4: 112 (45%); 7: 164 (66%); 11: 203 (81%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | 0.0454, 0.0678, 0.0901, 0.1299 | 0.0454: 200 (80%); 0.0678: 150 (60%); 0.0901: 100 (40%); 0.1299: 50 (20%) | 0.0454: 50 (20%); 0.0678: 100 (40%); 0.0901: 150 (60%); 0.1299: 200 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | 0.0624, 0.0863, 0.1121, 0.1522 | 0.0624: 200 (80%); 0.0863: 149 (60%); 0.1121: 100 (40%); 0.1522: 50 (20%) | 0.0624: 50 (20%); 0.0863: 101 (40%); 0.1121: 150 (60%); 0.1522: 200 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | 0.0342, 0.0509, 0.0658, 0.1074 | 0.0342: 200 (80%); 0.0509: 150 (60%); 0.0658: 100 (40%); 0.1074: 51 (20%) | 0.0342: 50 (20%); 0.0509: 100 (40%); 0.0658: 150 (60%); 0.1074: 199 (80%) | OFFLINE |
| pct_from_avwap_20low | (not found by literal grep) | 100.0% | 3.6012, 5.015, 6.4362, 8.375 | 3.6012: 200 (80%); 5.015: 150 (60%); 6.4362: 100 (40%); 8.375: 50 (20%) | 3.6012: 50 (20%); 5.015: 100 (40%); 6.4362: 150 (60%); 8.375: 200 (80%) | OFFLINE |
| pct_from_avwap_252low | (not found by literal grep) | 99.2% | 9.4742, 12.5264, 17.7222, 25.9426 | 9.4742: 198 (79%); 12.5264: 149 (60%); 17.7222: 99 (40%); 25.9426: 50 (20%) | 9.4742: 50 (20%); 12.5264: 99 (40%); 17.7222: 149 (60%); 25.9426: 198 (79%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 100.0% | 6.2456, 7.8822, 9.749, 12.8794 | 6.2456: 200 (80%); 7.8822: 150 (60%); 9.749: 100 (40%); 12.8794: 50 (20%) | 6.2456: 50 (20%); 7.8822: 100 (40%); 9.749: 150 (60%); 12.8794: 200 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -0.7626, 11.3006, 22.0404, 37.0664 | -0.7626: 200 (80%); 11.3006: 150 (60%); 22.0404: 100 (40%); 37.0664: 50 (20%) | -0.7626: 50 (20%); 11.3006: 100 (40%); 22.0404: 150 (60%); 37.0664: 200 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.047, 0.0657, 0.0802, 0.119 | 0.047: 200 (80%); 0.0657: 150 (60%); 0.0802: 100 (40%); 0.119: 50 (20%) | 0.047: 50 (20%); 0.0657: 100 (40%); 0.0802: 150 (60%); 0.119: 200 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.0763, 0.1243, 0.1641, 0.2103 | 0.0763: 200 (80%); 0.1243: 150 (60%); 0.1641: 100 (40%); 0.2103: 50 (20%) | 0.0763: 50 (20%); 0.1243: 100 (40%); 0.1641: 150 (60%); 0.2103: 200 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | 1.3516, 1.8256, 2.4617, 3.2252 | 1.3516: 200 (80%); 1.8256: 150 (60%); 2.4617: 100 (40%); 3.2252: 50 (20%) | 1.3516: 50 (20%); 1.8256: 100 (40%); 2.4617: 150 (60%); 3.2252: 200 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | 0.2779, 0.5096, 0.7882, 1.2682 | 0.2779: 200 (80%); 0.5096: 150 (60%); 0.7882: 100 (40%); 1.2682: 50 (20%) | 0.2779: 50 (20%); 0.5096: 100 (40%); 0.7882: 150 (60%); 1.2682: 200 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | 0.5801, 1.102, 1.7312, 2.6261 | 0.5801: 200 (80%); 1.102: 150 (60%); 1.7312: 100 (40%); 2.6261: 50 (20%) | 0.5801: 50 (20%); 1.102: 100 (40%); 1.7312: 150 (60%); 2.6261: 200 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | 4.9128, 7.2324, 9.488, 13.072 | 4.9128: 200 (80%); 7.2324: 150 (60%); 9.488: 100 (40%); 13.072: 50 (20%) | 4.9128: 50 (20%); 7.2324: 100 (40%); 9.488: 150 (60%); 13.072: 200 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 81.678, 91.752, 96.362, 98.412 | 81.678: 200 (80%); 91.752: 150 (60%); 96.362: 100 (40%); 98.412: 50 (20%) | 81.678: 50 (20%); 91.752: 100 (40%); 96.362: 150 (60%); 98.412: 200 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 63.05, 65.178, 67.066, 70.35 | 63.05: 200 (80%); 65.178: 150 (60%); 67.066: 100 (40%); 70.35: 50 (20%) | 63.05: 50 (20%); 65.178: 100 (40%); 67.066: 150 (60%); 70.35: 200 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 72.198, 74.79, 77.77, 81.31 | 72.198: 200 (80%); 74.79: 150 (60%); 77.77: 100 (40%); 81.31: 50 (20%) | 72.198: 50 (20%); 74.79: 100 (40%); 77.77: 150 (60%); 81.31: 200 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 250 (100%) | 0: 248 (99%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0288, 0.0382, 0.0508, 0.0671 | 0.0288: 200 (80%); 0.0382: 151 (60%); 0.0508: 102 (41%); 0.0671: 50 (20%) | 0.0288: 50 (20%); 0.0382: 101 (40%); 0.0508: 154 (62%); 0.0671: 200 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0664, -0.0528, -0.0422, -0.0305 | -0.0664: 200 (80%); -0.0528: 150 (60%); -0.0422: 102 (41%); -0.0305: 51 (20%) | -0.0664: 50 (20%); -0.0528: 101 (40%); -0.0422: 151 (60%); -0.0305: 200 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1.2 | 0: 250 (100%); 1.2: 50 (20%) | 0: 166 (66%); 1.2: 200 (80%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 33, 45.2, 54.8, 67.4 | 33: 207 (83%); 45.2: 149 (60%); 54.8: 100 (40%); 67.4: 50 (20%) | 33: 53 (21%); 45.2: 100 (40%); 54.8: 149 (60%); 67.4: 199 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.4% | 0.0103, 0.0152, 0.0204, 0.0303 | 0.0103: 197 (79%); 0.0152: 147 (59%); 0.0204: 98 (39%); 0.0303: 50 (20%) | 0.0103: 49 (20%); 0.0152: 99 (40%); 0.0204: 148 (59%); 0.0303: 196 (78%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.8374, 0.874, 0.9042, 0.9291 | 0.8374: 200 (80%); 0.874: 150 (60%); 0.9042: 100 (40%); 0.9291: 50 (20%) | 0.8374: 50 (20%); 0.874: 100 (40%); 0.9042: 150 (60%); 0.9291: 200 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 10.88, 71.38, 112.12, 172 | 10.88: 200 (80%); 71.38: 150 (60%); 112.12: 100 (40%); 172: 50 (20%) | 10.88: 50 (20%); 71.38: 100 (40%); 112.12: 150 (60%); 172: 200 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | 2.3435, 4.294, 7.2002, 12.747 | 2.3435: 200 (80%); 4.294: 150 (60%); 7.2002: 100 (40%); 12.747: 50 (20%) | 2.3435: 50 (20%); 4.294: 100 (40%); 7.2002: 150 (60%); 12.747: 200 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 77.636, 85.344, 88.524, 92.368 | 77.636: 200 (80%); 85.344: 150 (60%); 88.524: 100 (40%); 92.368: 50 (20%) | 77.636: 50 (20%); 85.344: 100 (40%); 88.524: 150 (60%); 92.368: 200 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 82.71, 87.192, 90.364, 92.786 | 82.71: 200 (80%); 87.192: 150 (60%); 90.364: 100 (40%); 92.786: 50 (20%) | 82.71: 50 (20%); 87.192: 100 (40%); 90.364: 150 (60%); 92.786: 200 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 51.476, 82.124, 95.288, 98.36 | 51.476: 200 (80%); 82.124: 150 (60%); 95.288: 100 (40%); 98.36: 51 (20%) | 51.476: 50 (20%); 82.124: 100 (40%); 95.288: 150 (60%); 98.36: 201 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 68.652, 91.294, 99.624, 100 | 68.652: 200 (80%); 91.294: 150 (60%); 99.624: 100 (40%); 100: 99 (40%) | 68.652: 50 (20%); 91.294: 100 (40%); 99.624: 150 (60%); 100: 250 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 12, 17 | 5: 206 (82%); 9: 153 (61%); 12: 109 (44%); 17: 60 (24%) | 5: 60 (24%); 9: 111 (44%); 12: 151 (60%); 17: 203 (81%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 4, 10, 13, 17 | 4: 211 (84%); 10: 151 (60%); 13: 109 (44%); 17: 54 (22%) | 4: 52 (21%); 10: 117 (47%); 13: 153 (61%); 17: 207 (83%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 55.744, 59.51, 62.546, 66.16 | 55.744: 200 (80%); 59.51: 150 (60%); 62.546: 100 (40%); 66.16: 50 (20%) | 55.744: 50 (20%); 59.51: 100 (40%); 62.546: 150 (60%); 66.16: 200 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.0936, 0.2341, 0.4762, 0.7318 | 0.0936: 200 (80%); 0.2341: 154 (62%); 0.4762: 101 (40%); 0.7318: 50 (20%) | 0.0936: 50 (20%); 0.2341: 101 (40%); 0.4762: 151 (60%); 0.7318: 200 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 13.876, 15.408, 17.614, 20.64 | 13.876: 200 (80%); 15.408: 150 (60%); 17.614: 100 (40%); 20.64: 51 (20%) | 13.876: 50 (20%); 15.408: 100 (40%); 17.614: 150 (60%); 20.64: 202 (81%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 13.876, 15.408, 17.614, 20.64 | 13.876: 200 (80%); 15.408: 150 (60%); 17.614: 100 (40%); 20.64: 51 (20%) | 13.876: 50 (20%); 15.408: 100 (40%); 17.614: 150 (60%); 20.64: 202 (81%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8499, 0.8711, 0.8995, 0.9391 | 0.8499: 200 (80%); 0.8711: 150 (60%); 0.8995: 100 (40%); 0.9391: 53 (21%) | 0.8499: 50 (20%); 0.8711: 100 (40%); 0.8995: 150 (60%); 0.9391: 200 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.92, 1.13, 1.33, 1.8 | 0.92: 201 (80%); 1.13: 151 (60%); 1.33: 101 (40%); 1.8: 51 (20%) | 0.92: 54 (22%); 1.13: 103 (41%); 1.33: 151 (60%); 1.8: 201 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.06, 0.0912, 0.1173, 0.1695 | 0.06: 200 (80%); 0.0912: 150 (60%); 0.1173: 100 (40%); 0.1695: 50 (20%) | 0.06: 50 (20%); 0.0912: 100 (40%); 0.1173: 150 (60%); 0.1695: 200 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 50.4721, 82.311, 131.7401, 225.1873 | 50.4721: 200 (80%); 82.311: 150 (60%); 131.7401: 100 (40%); 225.1873: 50 (20%) | 50.4721: 50 (20%); 82.311: 100 (40%); 131.7401: 150 (60%); 225.1873: 200 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 47.9402, 77.6756, 126.8352, 218.682 | 47.9402: 200 (80%); 77.6756: 150 (60%); 126.8352: 100 (40%); 218.682: 50 (20%) | 47.9402: 50 (20%); 77.6756: 100 (40%); 126.8352: 150 (60%); 218.682: 200 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 45.6859, 72.9542, 122.7324, 208.8367 | 45.6859: 200 (80%); 72.9542: 150 (60%); 122.7324: 100 (40%); 208.8367: 50 (20%) | 45.6859: 50 (20%); 72.9542: 100 (40%); 122.7324: 150 (60%); 208.8367: 200 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 250 (100%) | 0: 241 (96%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 250 (100%) | 0: 203 (81%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | 0.0563, 0.0817, 0.1028, 0.1447 | 0.0563: 200 (80%); 0.0817: 150 (60%); 0.1028: 100 (40%); 0.1447: 50 (20%) | 0.0563: 50 (20%); 0.0817: 101 (40%); 0.1028: 150 (60%); 0.1447: 200 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -21.776, -17.436, -14.726, -11.572 | -21.776: 200 (80%); -17.436: 150 (60%); -14.726: 100 (40%); -11.572: 50 (20%) | -21.776: 50 (20%); -17.436: 100 (40%); -14.726: 150 (60%); -11.572: 200 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 98.4% | 0.5095, 0.7869, 1.0319, 1.3152 | 0.5095: 197 (79%); 0.7869: 148 (59%); 1.0319: 99 (40%); 1.3152: 50 (20%) | 0.5095: 50 (20%); 0.7869: 99 (40%); 1.0319: 148 (59%); 1.3152: 197 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 98.4% | 3, 5, 7, 9 | 3: 202 (81%); 5: 158 (63%); 7: 108 (43%); 9: 65 (26%) | 3: 68 (27%); 5: 116 (46%); 7: 161 (64%); 9: 212 (85%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 98.4% | 0.1729, 0.2188, 0.2635, 0.3291 | 0.1729: 197 (79%); 0.2188: 148 (59%); 0.2635: 99 (40%); 0.3291: 50 (20%) | 0.1729: 51 (20%); 0.2188: 99 (40%); 0.2635: 148 (59%); 0.3291: 197 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 98.4% | 2, 5, 7, 9 | 2: 218 (87%); 5: 155 (62%); 7: 117 (47%); 9: 58 (23%) | 2: 56 (22%); 5: 108 (43%); 7: 160 (64%); 9: 213 (85%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 98.4% | 0.0283, 0.0379, 0.0488, 0.0702 | 0.0283: 198 (79%); 0.0379: 148 (59%); 0.0488: 99 (40%); 0.0702: 50 (20%) | 0.0283: 52 (21%); 0.0379: 99 (40%); 0.0488: 148 (59%); 0.0702: 197 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 98.4% | 5, 7, 9, 10 | 5: 197 (79%); 7: 165 (66%); 9: 106 (42%); 10: 65 (26%) | 5: 67 (27%); 7: 105 (42%); 9: 181 (72%); 10: 246 (98%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.2% | -0.1053, 0.0113, 0.1418, 0.3215 | -0.1053: 198 (79%); 0.0113: 149 (60%); 0.1418: 99 (40%); 0.3215: 50 (20%) | -0.1053: 50 (20%); 0.0113: 99 (40%); 0.1418: 149 (60%); 0.3215: 198 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.2% | 3, 5, 7, 9 | 3: 206 (82%); 5: 167 (67%); 7: 119 (48%); 9: 65 (26%) | 3: 61 (24%); 5: 103 (41%); 7: 156 (62%); 9: 217 (87%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 7.0% |
| 8k_item_5_02_filed_within_7d | 3.7% |
| above_avwap_20high | 3.6% |
| above_avwap_252low | 99.2% |
| above_cam_r3 | 34.0% |
| above_cam_r4 | 21.2% |
| above_cpr | 88.4% |
| above_pivot | 83.6% |
| above_prev_high | 41.6% |
| above_prev_high_clearance_atr_05 | 14.0% |
| above_prev_low | 99.6% |
| above_r1 | 24.8% |
| above_r2 | 15.6% |
| above_vwap | 78.0% |
| above_wood_p | 93.6% |
| ad_rising | 65.2% |
| adx_cross_up | 7.6% |
| adx_cross_up_20 | 7.6% |
| adx_strong | 11.6% |
| adx_trending | 51.6% |
| ao_cross_up | 2.0% |
| at_key_fib | 1.2% |
| at_key_fib_wide | 2.4% |
| avwap_20high_loss_recent_3d | 50.0% |
| avwap_20high_reclaim_recent_3d | 12.5% |
| avwap_20low_reclaim_recent_3d | 6.4% |
| avwap_252low_reclaim_recent_3d | 2.8% |
| avwap_50low_reclaim_recent_3d | 3.6% |
| bb_10_20_above_mid | 99.2% |
| bb_10_20_expanding | 86.4% |
| bb_10_20_pctb_gt_75 | 96.4% |
| bb_10_20_pctb_gt_8 | 90.4% |
| bb_10_20_pctb_gt_85 | 69.6% |
| bb_10_20_pctb_gt_9 | 44.8% |
| bb_10_20_pctb_gt_95 | 24.0% |
| bb_10_20_pctb_lt_1 | 0.4% |
| bb_10_20_pctb_lt_15 | 0.4% |
| bb_10_20_pctb_lt_2 | 0.4% |
| bb_10_20_pctb_lt_25 | 0.4% |
| bb_10_20_reclaim_from_lower_recent_3d | 0.4% |
| bb_10_20_reclaim_from_upper_recent_3d | 49.2% |
| bb_10_20_squeeze | 22.4% |
| bb_10_20_touch_lower | 0.4% |
| bb_10_20_touch_upper | 24.0% |
| bb_20_15_expanding | 87.2% |
| bb_20_15_pctb_gt_75 | 99.2% |
| bb_20_15_pctb_gt_8 | 98.8% |
| bb_20_15_pctb_gt_85 | 98.0% |
| bb_20_15_pctb_gt_9 | 95.2% |
| bb_20_15_pctb_gt_95 | 93.2% |
| bb_20_15_reclaim_from_upper_recent_3d | 2.0% |
| bb_20_15_squeeze | 32.0% |
| bb_20_15_touch_upper | 93.2% |
| bb_20_20_expanding | 87.2% |
| bb_20_20_pctb_gt_75 | 98.0% |
| bb_20_20_pctb_gt_8 | 95.2% |
| bb_20_20_pctb_gt_85 | 92.8% |
| bb_20_20_pctb_gt_9 | 88.4% |
| bb_20_20_pctb_gt_95 | 80.0% |
| bb_20_20_reclaim_from_upper_recent_3d | 24.8% |
| bb_20_20_squeeze | 16.0% |
| bb_20_20_touch_upper | 82.0% |
| bearish_pin_bar | 84.4% |
| below_avwap_20high | 96.4% |
| below_avwap_252low | 0.8% |
| below_cam_s3 | 6.4% |
| below_cam_s4 | 1.2% |
| below_cpr | 16.4% |
| below_ema_200 | 10.0% |
| below_prev_high | 57.2% |
| below_prev_low | 0.4% |
| below_s1 | 1.2% |
| below_sma_200 | 12.9% |
| below_sma_9 | 0.8% |
| below_vwap | 22.0% |
| blowoff_recent_3d | 3.2% |
| break_52w_high | 14.0% |
| break_52w_high_clearance_atr_05 | 2.8% |
| break_52w_high_confirmed_today | 30.8% |
| ceo_buy | 0.8% |
| chandelier_long_bullish | 98.8% |
| chandelier_long_flip_dn | 0.8% |
| chandelier_short_bearish | 0.8% |
| chandelier_short_flip_up | 3.2% |
| cmf_cross_dn | 9.6% |
| cmf_negative | 20.0% |
| cmf_positive | 80.0% |
| concentrated_sell | 7.8% |
| cpr_narrow | 87.2% |
| cpr_narrow_tight | 21.6% |
| cup_handle_detected | 15.2% |
| cup_handle_neckline_break_retest_long | 29.6% |
| dc10_breakout_dn_1pct | 0.8% |
| dc10_breakout_up | 46.0% |
| dc10_breakout_up_1pct | 72.8% |
| dc10_new_high | 87.6% |
| dc10_strong_breakout_up | 13.6% |
| dc20_breakout_up | 44.0% |
| dc20_new_high | 87.2% |
| dc20_resistance_break_retest_strong | 59.6% |
| defensive_leadership | 35.6% |
| director_only_buy | 1.6% |
| doji | 22.0% |
| double_bottom_detected | 16.0% |
| double_top_detected | 21.2% |
| dpi_elevated | 47.2% |
| drying_volume_on_down_turn | 30.4% |
| ema_20_50_bearish | 9.6% |
| ema_20_50_bullish | 90.4% |
| ema_20_50_golden_cross | 5.2% |
| ema_50_200_bearish | 28.9% |
| ema_50_200_bullish | 71.1% |
| ema_50_200_golden_cross | 1.6% |
| ema_9_21_golden_cross | 0.4% |
| evening_star | 0.8% |
| flag_bull_break_retest_long | 7.6% |
| flag_bull_broke | 8.0% |
| flag_bull_detected | 1.6% |
| force_index_cross_up | 0.8% |
| gap_dn_1_5pct | 0.4% |
| gap_up_1_5pct | 23.2% |
| gap_up_2pct | 16.8% |
| head_shoulders_bottom_detected | 6.4% |
| head_shoulders_top_detected | 2.8% |
| house_cluster_buy | 2.8% |
| house_cluster_sell | 7.6% |
| htf_aligned_bull | 83.6% |
| htf_disagreement | 1.2% |
| hull_bearish | 2.4% |
| hull_bullish | 97.6% |
| hull_flip_up | 2.4% |
| ichi_above_cloud | 94.0% |
| ichi_above_cloud_break_recent_5d | 20.8% |
| ichi_cloud_thick | 86.8% |
| ichi_tk_bullish | 92.4% |
| ichi_tk_cross_up | 2.8% |
| ichi_weekly_above_cloud | 72.6% |
| ichi_weekly_below_cloud | 15.7% |
| ichi_weekly_in_cloud | 11.7% |
| inside_bar | 7.6% |
| inside_cpr | 1.2% |
| inside_kc | 24.0% |
| insider_cluster_active | 11.1% |
| institutional_buy | 88.8% |
| institutional_negative | 4.8% |
| institutional_persistence_growing | 39.7% |
| institutional_persistence_strong | 59.1% |
| institutional_strong_buy | 81.2% |
| inverted_cup_handle_detected | 10.4% |
| is_friday | 18.8% |
| is_halloween_period | 52.8% |
| is_halloween_period_first_day | 0.4% |
| is_january | 10.8% |
| is_january_extended | 11.6% |
| is_monday | 19.2% |
| is_pre_holiday | 1.2% |
| is_summer_period | 47.2% |
| is_totm_window | 33.2% |
| is_totm_window_first_day | 8.4% |
| is_week_open | 22.8% |
| kc_touch_upper | 90.4% |
| large_dollar_buy | 0.8% |
| macd_12_26_9_bearish | 4.4% |
| macd_12_26_9_bullish | 95.6% |
| macd_12_26_9_crossover_up | 3.6% |
| macd_8_21_5_bearish | 4.4% |
| macd_8_21_5_bullish | 95.6% |
| macd_8_21_5_crossover_up | 4.0% |
| mfi_broad_overbought | 54.4% |
| mfi_overbought | 19.2% |
| monthly_above_sma_12 | 84.7% |
| monthly_above_sma_6 | 96.8% |
| monthly_bias_bear | 2.8% |
| monthly_bias_bull | 84.3% |
| monthly_momentum_pos | 82.7% |
| near_52w_high | 44.0% |
| near_52w_high_95pct | 62.0% |
| near_avwap_20high_atr_05x | 90.6% |
| near_avwap_20high_atr_10x | 96.9% |
| near_avwap_20low_atr_10x | 1.6% |
| near_avwap_20low_atr_15x | 9.2% |
| near_avwap_20low_atr_20x | 24.4% |
| near_avwap_252low_atr_05x | 0.4% |
| near_avwap_252low_atr_10x | 0.8% |
| near_avwap_252low_atr_15x | 1.2% |
| near_avwap_252low_atr_20x | 2.8% |
| near_avwap_50low_atr_15x | 0.4% |
| near_avwap_50low_atr_20x | 2.0% |
| near_cam_r3 | 26.4% |
| near_cam_s3 | 9.6% |
| near_cam_s4 | 3.6% |
| near_fib_236 | 3.6% |
| near_fib_382 | 1.2% |
| near_pivot | 16.0% |
| near_prev_close | 29.6% |
| near_prev_high | 23.6% |
| near_prev_low | 2.8% |
| near_r1 | 20.4% |
| near_r1_wide | 61.2% |
| near_r2 | 8.4% |
| near_r2_wide | 44.8% |
| near_s1 | 2.8% |
| near_s1_wide | 33.2% |
| near_s2 | 0.4% |
| near_s2_wide | 8.4% |
| near_s3 | 0.4% |
| near_wood_r1 | 23.2% |
| near_wood_s1 | 1.2% |
| news_uses_polygon_score | 28.8% |
| obv_bearish | 3.2% |
| obv_bullish | 96.8% |
| obv_diverge_bull | 0.8% |
| obv_falling | 5.2% |
| obv_rising | 94.8% |
| outside_bar | 0.4% |
| pead_negative_surprise | 10.7% |
| pead_positive_surprise | 32.1% |
| pin_bar | 84.4% |
| po3_accumulation_active | 22.8% |
| po3_bearish | 83.6% |
| po3_manipulation_sweep_up | 21.2% |
| po3_mmsm_setup | 6.4% |
| po3_sweep_above_prior_high | 92.4% |
| po3_sweep_below_prior_low | 2.0% |
| ppo_bullish | 94.4% |
| ppo_crossover_dn | 0.8% |
| ppo_crossover_up | 4.0% |
| pre_fomc_d0 | 4.0% |
| pre_fomc_d1 | 2.4% |
| pre_fomc_window | 6.4% |
| price_above_dema | 96.8% |
| price_above_ema_200 | 90.0% |
| price_above_ema_200_break_recent_5d | 12.9% |
| price_above_ema_20_break_recent_5d | 16.0% |
| price_above_ema_21_break_recent_5d | 16.4% |
| price_above_ema_50_break_recent_5d | 15.2% |
| price_above_ema_9_break_recent_5d | 29.2% |
| price_above_hull | 93.6% |
| price_above_sma_200 | 87.1% |
| price_above_tema | 91.6% |
| price_below_dema | 3.2% |
| price_below_hull | 6.4% |
| price_below_tema | 8.4% |
| psar_bullish | 99.2% |
| psar_flip_up | 1.6% |
| r1_break_retest_long | 95.2% |
| recent_blowoff_at_r3 | 1.2% |
| resistance_break_retest | 83.6% |
| risk_off_regime_bond_signal | 16.8% |
| risk_off_regime_bond_signal_strong | 7.2% |
| risk_off_regime_gold_signal | 28.4% |
| risk_on_regime_bond_signal | 48.8% |
| risk_on_regime_bond_signal_strong | 24.8% |
| roc_positive | 98.8% |
| roc_turning_up | 1.6% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 2.0% |
| rsi_14_cross_dn_overbought_recent_3d | 6.4% |
| rsi_14_extreme_ob | 7.6% |
| rsi_14_overbought | 56.0% |
| rsi_14_rising | 69.6% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 1.6% |
| rsi_21_cross_dn_overbought_recent_3d | 4.0% |
| rsi_21_extreme_ob | 0.8% |
| rsi_21_overbought | 21.6% |
| rsi_21_rising | 69.6% |
| rsi_2_bullish | 99.2% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 17.6% |
| rsi_2_cross_dn_overbought_recent_3d | 6.8% |
| rsi_2_cross_up_extreme_os_recent_3d | 8.4% |
| rsi_2_cross_up_oversold_recent_3d | 12.4% |
| rsi_2_extreme_ob | 81.6% |
| rsi_2_extreme_os | 0.4% |
| rsi_2_overbought | 92.8% |
| rsi_2_oversold | 0.4% |
| rsi_2_rising | 69.6% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 9.2% |
| rsi_9_cross_dn_overbought_recent_3d | 2.4% |
| rsi_9_extreme_ob | 26.0% |
| rsi_9_overbought | 94.0% |
| rsi_9_rising | 69.6% |
| s1_break_retest_short | 1.6% |
| sc_13d_filed_within_30d | 2.8% |
| sc_13g_filed_within_30d | 6.0% |
| sector_outperforming_spy | 66.7% |
| sector_underperforming_spy | 33.3% |
| shooting_star | 49.6% |
| sma_20_50_bullish | 82.8% |
| sma_20_50_golden_cross | 4.0% |
| sma_50_200_bullish | 66.7% |
| sma_50_200_golden_cross | 0.4% |
| sma_9_21_bullish | 97.6% |
| sma_9_21_golden_cross | 2.0% |
| smc_bos_bearish | 7.2% |
| smc_bos_bullish | 25.2% |
| smc_bos_retest_long | 5.2% |
| smc_bos_retest_short | 2.4% |
| smc_breaker_block_bearish | 6.8% |
| smc_breaker_block_bullish | 36.8% |
| smc_choch_bearish | 0.4% |
| smc_choch_bullish | 13.2% |
| smc_equal_highs_swept | 6.4% |
| smc_equal_lows_swept | 3.6% |
| smc_fvg_bearish_active | 6.0% |
| smc_fvg_bullish_active | 94.0% |
| smc_fvg_retest_long_zone | 50.4% |
| smc_fvg_retest_short_zone | 2.8% |
| smc_in_discount_zone | 0.4% |
| smc_inverse_fvg_bearish | 11.6% |
| smc_liquidity_swept_dn | 2.4% |
| smc_liquidity_swept_up | 2.4% |
| smc_mitigation_block_short | 10.8% |
| smc_ob_bearish_active | 12.0% |
| smc_ob_bullish_active | 65.2% |
| smc_ote_long_zone | 1.6% |
| smc_ote_short_zone | 7.6% |
| squeeze_in | 10.8% |
| stoch_bearish_cross | 24.0% |
| stoch_broad_overbought | 92.4% |
| stoch_bullish_cross | 3.6% |
| stoch_overbought | 88.4% |
| stochrsi_cross_dn | 27.2% |
| stochrsi_cross_up | 16.0% |
| stochrsi_overbought | 73.2% |
| stochrsi_oversold | 4.0% |
| tema_above_dema | 95.6% |
| tema_cross_up | 7.2% |
| triangle_apex_break_retest_long | 33.6% |
| triangle_ascending_detected | 17.6% |
| triangle_descending_detected | 0.4% |
| uo_overbought | 6.0% |
| usd_strengthening | 16.8% |
| usd_weakening | 6.8% |
| vix_band_high | 22.0% |
| vix_band_low | 47.2% |
| vix_band_mid | 30.8% |
| vix_term_backwardation | 4.8% |
| vix_term_contango | 95.2% |
| vol_above_avg | 69.6% |
| vol_below_avg | 30.4% |
| vol_spike_12x | 50.4% |
| vol_spike_15x | 30.8% |
| vol_spike_17x | 22.8% |
| vol_spike_2x | 14.4% |
| vol_spike_2x_on_down_day_recent_3d | 1.6% |
| vol_spike_2x_on_up_day_recent_3d | 24.8% |
| vol_spike_3x | 4.8% |
| vp_above_value_area | 90.0% |
| vp_close_above_poc | 99.6% |
| vp_close_below_poc | 0.4% |
| vp_in_value_area | 10.0% |
| week_open_gap_up_15pct | 4.4% |
| weekly_above_ema_20 | 98.4% |
| weekly_bias_bull | 98.4% |
| williams_r_overbought | 73.6% |
| williams_r_oversold | 0.4% |
| williams_r_rising | 11.2% |
| within_pead_window | 40.7% |
| xs_avoid_high_ivol | 76.4% |
| xs_avoid_high_max | 56.9% |
| xs_high_beta_decile | 26.4% |
| xs_low_beta_bottom_quintile | 26.4% |
| xs_low_beta_decile | 17.9% |
| xs_low_beta_decile_entry_recent_5d | 1.6% |
| xs_low_beta_top_quintile | 17.9% |
| xs_momentum_bottom_decile | 8.1% |
| xs_momentum_bottom_quintile | 16.9% |
| xs_momentum_top_decile | 12.5% |
| xs_momentum_top_quintile | 26.2% |
| xs_quality_bottom_quintile | 25.8% |
| xs_quality_top_quintile | 17.0% |
| xs_quality_top_tercile | 35.8% |
| year_high_break_retest_long | 22.4% |
| yoy_surprise_high | 56.1% |
| yoy_surprise_negative | 31.4% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 92.8% |
| committed_growth_holders | 92.8% |
| corp_donations_1y | 9.6% |
| corp_donations_count_1y | 9.6% |
| corp_donations_unique_pacs | 9.6% |
| cot_rut_commercials_pctile_3y | 54.8% |
| cot_rut_mmoney_pctile_3y | 54.8% |
| cup_handle_depth_pct | 19.2% |
| days_since_deletion | 5.6% |
| days_since_inclusion | 11.6% |
| days_to_next_holiday | 61.6% |
| days_to_rebalance | 6.4% |
| dpi_30d_avg | 94.0% |
| dpi_recent | 94.0% |
| earnings_announcement_return | 89.6% |
| earnings_eps_yoy_growth | 95.6% |
| flag_bull_pole_move_pct | 1.6% |
| gov_contracts_4q_sum | 44.0% |
| gov_contracts_last_qtr_amount | 44.0% |
| gov_contracts_qoq_growth | 44.0% |
| head_shoulders_magnitude_pct | 8.4% |
| insider_director_buyers_30d | 3.6% |
| insider_officer_buyers_30d | 3.6% |
| insider_total_shares_bought_30d | 3.6% |
| insider_unique_buyers_30d | 3.6% |
| inverted_cup_handle_height_pct | 20.4% |
| lobbying_amount_1y | 69.6% |
| lobbying_amount_q | 69.6% |
| lobbying_amount_yoy | 69.6% |
| otc_short_ratio_recent | 94.0% |
| otc_volume_recent | 94.0% |
| pair_half_life | 93.2% |
| pair_max_abs_zscore | 93.2% |
| pair_zscore_signed | 93.2% |
| pct_from_avwap_20high | 12.8% |
| persistent_holders_4q | 92.8% |
| persistent_holders_8q | 92.8% |
| sc_13g_latest_percent_owned | 2.8% |
| search_volume_index_recent | 84.4% |
| search_volume_observations | 84.4% |
| search_volume_zscore_30d | 84.4% |
| sector_etf_return_20d | 2.4% |
| spy_return_20d | 2.4% |
| total_active_holders | 92.8% |
| triangle_breakout_pct | 17.6% |
| xs_quality_decile | 63.6% |
| xs_quality_gross_profitability | 63.6% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.998), `avwap_20low` (1.0), `avwap_252low` (0.995), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.998), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.998), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.998), `cam_r2` (0.998), `cam_r3` (0.998), `cam_r4` (0.998), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (0.998), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.998), `dc10_lower` (0.999), `dc10_mid` (0.999), `dc10_upper` (0.998), `dc20_lower` (0.999), `dc20_mid` (0.999), `dc20_upper` (0.998), `dema` (1.0), `double_bottom_neckline` (0.996), `double_bottom_trough` (0.995), `double_top_neckline` (0.997), `double_top_peak` (0.999), `entry_stop_long` (0.999), `entry_stop_short` (0.998), `fib_236` (0.998), `fib_382` (0.999), `fib_500` (0.998), `fib_618` (0.998), `fib_786` (0.997), `fib_ext_127` (0.996), `fib_ext_162` (0.994), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (1.0), `head_shoulders_top_neckline` (1.0), `hull_ma` (0.999), `ichi_kijun` (0.999), `ichi_senkou_a` (0.997), `ichi_senkou_b` (0.994), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (1.0), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (0.999), `monthly_close` (0.999), `monthly_sma_12` (0.988), `monthly_sma_6` (0.996), `pivot` (0.999), `prev_close` (0.998), `prev_high` (0.998), `prev_low` (0.999), `psar_value` (0.999), `r1` (0.998), `r2` (0.998), `r3` (0.997), `s1` (0.999), `s2` (0.999), `s3` (0.999), `supertrend_value` (0.999), `swing_high` (0.997), `swing_low` (0.994), `tema` (0.999), `triangle_resistance_level` (0.999), `vp_poc` (0.996), `vp_value_area_high` (0.998), `vp_value_area_low` (0.994), `vwap_upper_1` (0.952), `vwap_upper_2` (0.954), `weekly_close` (0.999), `weekly_ema_10` (0.999), `weekly_ema_20` (0.998), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.998), `wood_s1` (0.999), `wood_s2` (0.999), `year_high` (0.978), `year_low` (0.98)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | mirror of touch_lower | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1 | implicit anatomy knobs (min body/wick/st | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P3.1 | implicit anatomy knobs (min body/wick/st | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P4.1 | implicit anatomy knobs (min body/wick/st | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P5.1 | proximity tolerance to R1 (abs dist/leve | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P6.1 | proximity tolerance to R2 (abs dist/leve | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P7.1 | implicit anatomy knobs (min body/wick/st | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P8 | rsi_14 > 65 | 5 | subset-safe | no - derives offline |
| P9 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     1 x 1 x 1 x 1 x 1 x 1 x 1 x 5 x 1 = 5
offline gradings   5 level-combinations x 24 exits = 120
ENGINE RUNS        1 (every fire-adding axis sits at production-only until its env actuator exists)
check              1 x 5 = 5
```

B-row candidates NOT in this factorial: 502 census axes join it only when REGISTERED at the T3 band review.
