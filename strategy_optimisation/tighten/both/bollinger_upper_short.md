# Table A - bollinger_upper_short

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit fa06ebf3e at 2026-09-19 13:07:41 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** mean_reversion | **status:** STALLED-CAMPAIGN | **R5 fires:** 130 | **surviving fires (T1):** 130 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  bb_20_20_touch_upper  <- backtest/signals/screener.py
       DEFN: close at/beyond the Bollinger(20, 2.0) band (bb block)
       knobs P1.1-P1.1 (band rows in Table A)
P2  shooting_star  <- backtest/signals/screener.py +1
       DEFN: canonical single/two-candle reversal pattern (Nison; compute_candle_signals - geometry in producer)
       knobs P2.1-P2.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  rsi_14 > 65   [EXISTING-THRESHOLD]
P4  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_bollinger_upper_short (docstring and return dropped):

```python
fires = s.get('bb_20_20_touch_upper') and s.get('rsi_14', 50) > 65 and s.get('shooting_star') and (not _short_borrow_trap_active(s))
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
| P2 | PRODUCER | shooting_star - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | canonical single/two-candle reversal pattern (Nison; compute_candle_signals - geometry in producer) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | implicit anatomy knobs (min body/wick/step pct) - backtest/signals/technical.py:candle block (compute_candle_signals) | CANON candle anatomy (Nison); production accepts any magnitude | 0 / absent (any magnitude counts) | [0, 0.3, 0.5] per knob | none - pattern bars' OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | STRATEGY | rsi_14 `> 65` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `> 65` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P3.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `> 65` | 100.0% | TIGHTER = RAISE the floor: 67.134 -> 104 (80%); 69.404 -> 78 (60%); 71.286 -> 52 (40%); 75.238 -> 26 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 19.146, 23.604, 27.664, 32.502 | 19.146: 104 (80%); 23.604: 78 (60%); 27.664: 52 (40%); 32.502: 26 (20%) | 19.146: 26 (20%); 23.604: 52 (40%); 27.664: 78 (60%); 32.502: 104 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 9.776, 11.762, 13.53, 15.07 | 9.776: 104 (80%); 11.762: 78 (60%); 13.53: 52 (40%); 15.07: 27 (21%) | 9.776: 26 (20%); 11.762: 52 (40%); 13.53: 78 (60%); 15.07: 105 (81%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 34.472, 38.216, 40.322, 44.792 | 34.472: 104 (80%); 38.216: 78 (60%); 40.322: 52 (40%); 44.792: 26 (20%) | 34.472: 26 (20%); 38.216: 52 (40%); 40.322: 78 (60%); 44.792: 104 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | 2.0493, 3.6616, 6.2832, 13.072 | 2.0493: 104 (80%); 3.6616: 78 (60%); 6.2832: 52 (40%); 13.072: 26 (20%) | 2.0493: 26 (20%); 3.6616: 52 (40%); 6.2832: 78 (60%); 13.072: 104 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.1575, 1.8663, 3.1438, 5.1733 | 1.1575: 104 (80%); 1.8663: 78 (60%); 3.1438: 52 (40%); 5.1733: 26 (20%) | 1.1575: 26 (20%); 1.8663: 52 (40%); 3.1438: 78 (60%); 5.1733: 104 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.1575, 1.8663, 3.1438, 5.1733 | 1.1575: 104 (80%); 1.8663: 78 (60%); 3.1438: 52 (40%); 5.1733: 26 (20%) | 1.1575: 26 (20%); 1.8663: 52 (40%); 3.1438: 78 (60%); 5.1733: 104 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.8636, 2.1908, 2.449, 2.9836 | 1.8636: 104 (80%); 2.1908: 78 (60%); 2.449: 52 (40%); 2.9836: 26 (20%) | 1.8636: 26 (20%); 2.1908: 52 (40%); 2.449: 78 (60%); 2.9836: 104 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.092, 0.1076, 0.1354, 0.1979 | 0.092: 104 (80%); 0.1076: 78 (60%); 0.1354: 52 (40%); 0.1979: 26 (20%) | 0.092: 26 (20%); 0.1076: 53 (41%); 0.1354: 78 (60%); 0.1979: 104 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.8447, 0.8703, 0.9251, 0.9755 | 0.8447: 104 (80%); 0.8703: 78 (60%); 0.9251: 52 (40%); 0.9755: 26 (20%) | 0.8447: 26 (20%); 0.8703: 52 (40%); 0.9251: 78 (60%); 0.9755: 104 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0694, 0.0843, 0.1071, 0.135 | 0.0694: 104 (80%); 0.0843: 78 (60%); 0.1071: 52 (40%); 0.135: 26 (20%) | 0.0694: 27 (21%); 0.0843: 52 (40%); 0.1071: 78 (60%); 0.135: 104 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 1.1463, 1.1765, 1.2357, 1.3134 | 1.1463: 104 (80%); 1.1765: 78 (60%); 1.2357: 52 (40%); 1.3134: 26 (20%) | 1.1463: 26 (20%); 1.1765: 53 (41%); 1.2357: 78 (60%); 1.3134: 104 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0925, 0.1124, 0.1428, 0.18 | 0.0925: 104 (80%); 0.1124: 78 (60%); 0.1428: 52 (40%); 0.18: 26 (20%) | 0.0925: 27 (21%); 0.1124: 52 (40%); 0.1428: 78 (60%); 0.18: 104 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.9847, 1.0074, 1.0518, 1.11 | 0.9847: 104 (80%); 1.0074: 78 (60%); 1.0518: 52 (40%); 1.11: 26 (20%) | 0.9847: 26 (20%); 1.0074: 53 (41%); 1.0518: 78 (60%); 1.11: 104 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0651, -0.0372, -0.0167, 0.0187 | -0.0651: 104 (80%); -0.0372: 78 (60%); -0.0167: 52 (40%); 0.0187: 26 (20%) | -0.0651: 26 (20%); -0.0372: 52 (40%); -0.0167: 78 (60%); 0.0187: 104 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.144, 0.1637, 0.193, 0.2353 | 0.144: 104 (80%); 0.1637: 79 (61%); 0.193: 52 (40%); 0.2353: 26 (20%) | 0.144: 26 (20%); 0.1637: 54 (42%); 0.193: 78 (60%); 0.2353: 104 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 130 (100%) | 0: 125 (96%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.036, 0.0272, 0.0941, 0.1712 | -0.036: 104 (80%); 0.0272: 78 (60%); 0.0941: 52 (40%); 0.1712: 26 (20%) | -0.036: 26 (20%); 0.0272: 52 (40%); 0.0941: 78 (60%); 0.1712: 104 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 0.4, 2 | 0: 130 (100%); 0.4: 52 (40%); 2: 27 (21%) | 0: 78 (60%); 0.4: 78 (60%); 2: 118 (91%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2381, -0.2011, -0.1625, -0.1299 | -0.2381: 108 (83%); -0.2011: 79 (61%); -0.1625: 52 (40%); -0.1299: 28 (22%) | -0.2381: 28 (22%); -0.2011: 53 (41%); -0.1625: 78 (60%); -0.1299: 107 (82%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.409, 0.5449, 0.6667, 0.7949 | 0.409: 104 (80%); 0.5449: 79 (61%); 0.6667: 54 (42%); 0.7949: 29 (22%) | 0.409: 26 (20%); 0.5449: 53 (41%); 0.6667: 80 (62%); 0.7949: 110 (85%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2808, 0.418, 0.6795, 0.8333 | 0.2808: 104 (80%); 0.418: 78 (60%); 0.6795: 52 (40%); 0.8333: 29 (22%) | 0.2808: 26 (20%); 0.418: 52 (40%); 0.6795: 78 (60%); 0.8333: 105 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1741, -0.0556, 0.0355, 0.1362 | -0.1741: 104 (80%); -0.0556: 79 (61%); 0.0355: 53 (41%); 0.1362: 26 (20%) | -0.1741: 26 (20%); -0.0556: 53 (41%); 0.0355: 82 (63%); 0.1362: 104 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.1538, 0.3718, 0.4808, 0.7115 | 0.1538: 110 (85%); 0.3718: 79 (61%); 0.4808: 53 (41%); 0.7115: 27 (21%) | 0.1538: 28 (22%); 0.3718: 56 (43%); 0.4808: 79 (61%); 0.7115: 106 (82%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1116, 0.2602, 0.4359, 0.6372 | 0.1116: 104 (80%); 0.2602: 78 (60%); 0.4359: 55 (42%); 0.6372: 26 (20%) | 0.1116: 26 (20%); 0.2602: 52 (40%); 0.4359: 80 (62%); 0.6372: 104 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5654, -0.3194, -0.12, 0.1047 | -0.5654: 105 (81%); -0.3194: 78 (60%); -0.12: 52 (40%); 0.1047: 27 (21%) | -0.5654: 27 (21%); -0.3194: 52 (40%); -0.12: 78 (60%); 0.1047: 105 (81%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3, 0.5385, 0.8193, 0.9564 | 0.3: 104 (80%); 0.5385: 79 (61%); 0.8193: 52 (40%); 0.9564: 26 (20%) | 0.3: 26 (20%); 0.5385: 53 (41%); 0.8193: 78 (60%); 0.9564: 104 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.141, 0.4269, 0.6603, 0.9295 | 0.141: 105 (81%); 0.4269: 78 (60%); 0.6603: 53 (41%); 0.9295: 27 (21%) | 0.141: 27 (21%); 0.4269: 52 (40%); 0.6603: 81 (62%); 0.9295: 105 (81%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0646, -0.0602, -0.0412, 0 | -0.0646: 105 (81%); -0.0602: 78 (60%); -0.0412: 54 (42%); 0: 39 (30%) | -0.0646: 27 (21%); -0.0602: 52 (40%); -0.0412: 80 (62%); 0: 130 (100%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3307, 0.5128, 0.8039, 1 | 0.3307: 104 (80%); 0.5128: 80 (62%); 0.8039: 52 (40%); 1: 34 (26%) | 0.3307: 26 (20%); 0.5128: 53 (41%); 0.8039: 78 (60%); 1: 130 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.191, 0.3782, 0.5988, 0.8564 | 0.191: 104 (80%); 0.3782: 82 (63%); 0.5988: 52 (40%); 0.8564: 26 (20%) | 0.191: 26 (20%); 0.3782: 54 (42%); 0.5988: 78 (60%); 0.8564: 104 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0195, 0.0306, 0.0734, 0.1608 | -0.0195: 104 (80%); 0.0306: 78 (60%); 0.0734: 54 (42%); 0.1608: 26 (20%) | -0.0195: 26 (20%); 0.0306: 52 (40%); 0.0734: 82 (63%); 0.1608: 104 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3493, 0.7484, 0.9167, 0.9679 | 0.3493: 104 (80%); 0.7484: 78 (60%); 0.9167: 55 (42%); 0.9679: 29 (22%) | 0.3493: 26 (20%); 0.7484: 52 (40%); 0.9167: 83 (64%); 0.9679: 108 (83%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1518, 0.3933, 0.6407, 0.8268 | 0.1518: 105 (81%); 0.3933: 81 (62%); 0.6407: 52 (40%); 0.8268: 29 (22%) | 0.1518: 29 (22%); 0.3933: 53 (41%); 0.6407: 78 (60%); 0.8268: 104 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0203, 0.0566, 0.1246 | -0.0812: 115 (88%); -0.0203: 81 (62%); 0.0566: 54 (42%); 0.1246: 26 (20%) | -0.0812: 28 (22%); -0.0203: 60 (46%); 0.0566: 84 (65%); 0.1246: 104 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.3177, -0.1603, -0.0268, 0.0678 | -0.3177: 104 (80%); -0.1603: 78 (60%); -0.0268: 53 (41%); 0.0678: 26 (20%) | -0.3177: 26 (20%); -0.1603: 52 (40%); -0.0268: 79 (61%); 0.0678: 104 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.0385, 0.3205, 0.5705, 0.7911 | 0.0385: 105 (81%); 0.3205: 80 (62%); 0.5705: 54 (42%); 0.7911: 26 (20%) | 0.0385: 27 (21%); 0.3205: 53 (41%); 0.5705: 81 (62%); 0.7911: 104 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2666, 0.4295, 0.591, 0.8269 | 0.2666: 104 (80%); 0.4295: 78 (60%); 0.591: 52 (40%); 0.8269: 30 (23%) | 0.2666: 26 (20%); 0.4295: 52 (40%); 0.591: 78 (60%); 0.8269: 106 (82%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0717, 0.1467, 0.3773, 0.7952 | 0.0717: 105 (81%); 0.1467: 79 (61%); 0.3773: 52 (40%); 0.7952: 26 (20%) | 0.0717: 27 (21%); 0.1467: 53 (41%); 0.3773: 78 (60%); 0.7952: 104 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 100.0% | 14.6, 59.8, 77, 106 | 14.6: 104 (80%); 59.8: 78 (60%); 77: 54 (42%); 106: 26 (20%) | 14.6: 26 (20%); 59.8: 52 (40%); 77: 80 (62%); 106: 104 (80%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 98.5% | 1.8707, 2.3853, 2.8341, 3.6049 | 1.8707: 102 (78%); 2.3853: 77 (59%); 2.8341: 51 (39%); 3.6049: 26 (20%) | 1.8707: 26 (20%); 2.3853: 51 (39%); 2.8341: 77 (59%); 3.6049: 102 (78%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 9, 16, 27, 40 | 9: 108 (83%); 16: 80 (62%); 27: 53 (41%); 40: 29 (22%) | 9: 32 (25%); 16: 53 (41%); 27: 79 (61%); 40: 107 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 0, 1, 2, 3 | 0: 130 (100%); 1: 95 (73%); 2: 76 (58%); 3: 50 (38%) | 0: 35 (27%); 1: 54 (42%); 2: 80 (62%); 3: 106 (82%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0126, -0.0075, -0.0006, 0.0174 | -0.0126: 104 (80%); -0.0075: 78 (60%); -0.0006: 52 (40%); 0.0174: 26 (20%) | -0.0126: 28 (22%); -0.0075: 53 (41%); -0.0006: 78 (60%); 0.0174: 104 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.701, 25.8889, 26.4766, 27.0923 | 24.701: 104 (80%); 25.8889: 79 (61%); 26.4766: 52 (40%); 27.0923: 26 (20%) | 24.701: 26 (20%); 25.8889: 53 (41%); 26.4766: 78 (60%); 27.0923: 104 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -2.556, -0.633, -0.3028, 0.0798 | -2.556: 104 (80%); -0.633: 78 (60%); -0.3028: 52 (40%); 0.0798: 26 (20%) | -2.556: 26 (20%); -0.633: 52 (40%); -0.3028: 78 (60%); 0.0798: 104 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.0798, 0.3028, 0.633, 2.556 | -0.0798: 104 (80%); 0.3028: 78 (60%); 0.633: 52 (40%); 2.556: 26 (20%) | -0.0798: 26 (20%); 0.3028: 52 (40%); 0.633: 78 (60%); 2.556: 104 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.055, -0.0207, 0.01, 0.037 | -0.055: 104 (80%); -0.0207: 78 (60%); 0.01: 52 (40%); 0.037: 26 (20%) | -0.055: 26 (20%); -0.0207: 52 (40%); 0.01: 78 (60%); 0.037: 104 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.1173, 8.4675, 8.6684, 8.9899 | 8.1173: 104 (80%); 8.4675: 78 (60%); 8.6684: 52 (40%); 8.9899: 25 (19%) | 8.1173: 26 (20%); 8.4675: 52 (40%); 8.6684: 78 (60%); 8.9899: 105 (81%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 98.5% | 0, 1 | 0: 128 (98%); 1: 41 (32%) | 0: 87 (67%); 1: 112 (86%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 98.5% | 0 | 0: 106 (82%) | 0: 104 (80%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 98.5% | 0, 1 | 0: 128 (98%); 1: 42 (32%) | 0: 86 (66%); 1: 116 (89%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2.8, 6, 125.4, 253.2 | 2.8: 104 (80%); 6: 80 (62%); 125.4: 52 (40%); 253.2: 26 (20%) | 2.8: 26 (20%); 6: 57 (44%); 125.4: 78 (60%); 253.2: 104 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 4, 78.4, 132.4 | 1: 110 (85%); 4: 81 (62%); 78.4: 52 (40%); 132.4: 26 (20%) | 1: 29 (22%); 4: 56 (43%); 78.4: 78 (60%); 132.4: 104 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | 0.2443, 0.4861, 1.0988, 1.9894 | 0.2443: 104 (80%); 0.4861: 78 (60%); 1.0988: 52 (40%); 1.9894: 26 (20%) | 0.2443: 26 (20%); 0.4861: 52 (40%); 1.0988: 78 (60%); 1.9894: 104 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | 0.7879, 1.437, 2.2856, 4.3486 | 0.7879: 104 (80%); 1.437: 78 (60%); 2.2856: 52 (40%); 4.3486: 26 (20%) | 0.7879: 26 (20%); 1.437: 52 (40%); 2.2856: 78 (60%); 4.3486: 104 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | 0.2197, 0.746, 1.2252, 2.8483 | 0.2197: 104 (80%); 0.746: 78 (60%); 1.2252: 52 (40%); 2.8483: 26 (20%) | 0.2197: 26 (20%); 0.746: 52 (40%); 1.2252: 78 (60%); 2.8483: 104 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | 0.2459, 0.4674, 0.8965, 1.7736 | 0.2459: 104 (80%); 0.4674: 78 (60%); 0.8965: 52 (40%); 1.7736: 26 (20%) | 0.2459: 26 (20%); 0.4674: 52 (40%); 0.8965: 78 (60%); 1.7736: 104 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | 1.0976, 1.728, 3.4672, 6.4205 | 1.0976: 104 (80%); 1.728: 78 (60%); 3.4672: 52 (40%); 6.4205: 26 (20%) | 1.0976: 26 (20%); 1.728: 52 (40%); 3.4672: 78 (60%); 6.4205: 104 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | 0.723, 1.325, 2.238, 4.1607 | 0.723: 104 (80%); 1.325: 78 (60%); 2.238: 52 (40%); 4.1607: 26 (20%) | 0.723: 26 (20%); 1.325: 52 (40%); 2.238: 78 (60%); 4.1607: 104 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 63.774, 68.828, 75.834, 80.244 | 63.774: 104 (80%); 68.828: 78 (60%); 75.834: 52 (40%); 80.244: 26 (20%) | 63.774: 26 (20%); 68.828: 52 (40%); 75.834: 78 (60%); 80.244: 104 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 99.2% | -0.0401, 0.0691, 0.1415, 0.2482 | -0.0401: 103 (79%); 0.0691: 77 (59%); 0.1415: 52 (40%); 0.2482: 26 (20%) | -0.0401: 26 (20%); 0.0691: 52 (40%); 0.1415: 77 (59%); 0.2482: 103 (79%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.2% | 0.0165, 0.0303, 0.0509, 0.0723 | 0.0165: 103 (79%); 0.0303: 78 (60%); 0.0509: 52 (40%); 0.0723: 26 (20%) | 0.0165: 26 (20%); 0.0303: 51 (39%); 0.0509: 77 (59%); 0.0723: 103 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 2, 5, 10.2 | 0: 130 (100%); 2: 86 (66%); 5: 54 (42%); 10.2: 26 (20%) | 0: 31 (24%); 2: 62 (48%); 5: 82 (63%); 10.2: 104 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0719 | 0: 130 (100%); 0.0719: 26 (20%) | 0: 96 (74%); 0.0719: 104 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.5, 0.7143 | 0: 130 (100%); 0.3333: 81 (62%); 0.5: 66 (51%); 0.7143: 27 (21%) | 0: 39 (30%); 0.3333: 54 (42%); 0.5: 82 (63%); 0.7143: 105 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1.6, 3, 7.2 | 0: 130 (100%); 1.6: 78 (60%); 3: 57 (44%); 7.2: 26 (20%) | 0: 36 (28%); 1.6: 52 (40%); 3: 81 (62%); 7.2: 104 (80%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 5, 10.2 | 0: 130 (100%); 2: 86 (66%); 5: 54 (42%); 10.2: 26 (20%) | 0: 31 (24%); 2: 62 (48%); 5: 82 (63%); 10.2: 104 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 5 | 0: 130 (100%); 1: 79 (61%); 2: 64 (49%); 5: 33 (25%) | 0: 51 (39%); 1: 66 (51%); 2: 84 (65%); 5: 107 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.077, 0.2703, 0.4643, 0.6667 | 0.077: 104 (80%); 0.2703: 78 (60%); 0.4643: 52 (40%); 0.6667: 31 (24%) | 0.077: 26 (20%); 0.2703: 52 (40%); 0.4643: 78 (60%); 0.6667: 106 (82%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3829, 0.7217 | 0: 127 (98%); 0.3829: 52 (40%); 0.7217: 26 (20%) | 0: 54 (42%); 0.3829: 78 (60%); 0.7217: 104 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2, 0.5, 0.6667 | 0: 129 (99%); 0.2: 79 (61%); 0.5: 54 (42%); 0.6667: 31 (24%) | 0: 43 (33%); 0.2: 53 (41%); 0.5: 87 (67%); 0.6667: 105 (81%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2, 0.5, 0.6667 | 0: 129 (99%); 0.2: 79 (61%); 0.5: 54 (42%); 0.6667: 31 (24%) | 0: 43 (33%); 0.2: 53 (41%); 0.5: 87 (67%); 0.6667: 105 (81%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.0356, 0, 0.1533 | -0.0356: 104 (80%); 0: 101 (78%); 0.1533: 26 (20%) | -0.0356: 26 (20%); 0: 94 (72%); 0.1533: 104 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.5043, 0, 0.7238, 2.604 | -0.5043: 104 (80%); 0: 88 (68%); 0.7238: 52 (40%); 2.604: 26 (20%) | -0.5043: 26 (20%); 0: 64 (49%); 0.7238: 78 (60%); 2.604: 104 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 12 | 2: 110 (85%); 4: 82 (63%); 7: 56 (43%); 12: 28 (22%) | 2: 33 (25%); 4: 56 (43%); 7: 82 (63%); 12: 107 (82%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | 0.0587, 0.0787, 0.0933, 0.1359 | 0.0587: 104 (80%); 0.0787: 78 (60%); 0.0933: 52 (40%); 0.1359: 26 (20%) | 0.0587: 26 (20%); 0.0787: 52 (40%); 0.0933: 78 (60%); 0.1359: 104 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | 0.0619, 0.0841, 0.1103, 0.1515 | 0.0619: 104 (80%); 0.0841: 78 (60%); 0.1103: 52 (40%); 0.1515: 26 (20%) | 0.0619: 26 (20%); 0.0841: 52 (40%); 0.1103: 78 (60%); 0.1515: 104 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | 0.0416, 0.0563, 0.0692, 0.1109 | 0.0416: 104 (80%); 0.0563: 78 (60%); 0.0692: 52 (40%); 0.1109: 26 (20%) | 0.0416: 26 (20%); 0.0563: 52 (40%); 0.0692: 78 (60%); 0.1109: 104 (80%) | OFFLINE |
| pct_from_avwap_20low | (not found by literal grep) | 100.0% | 4.328, 5.2714, 6.7172, 8.335 | 4.328: 104 (80%); 5.2714: 78 (60%); 6.7172: 52 (40%); 8.335: 26 (20%) | 4.328: 26 (20%); 5.2714: 52 (40%); 6.7172: 78 (60%); 8.335: 104 (80%) | OFFLINE |
| pct_from_avwap_252low | (not found by literal grep) | 99.2% | 7.2698, 10.9908, 14.3364, 24.988 | 7.2698: 103 (79%); 10.9908: 77 (59%); 14.3364: 52 (40%); 24.988: 26 (20%) | 7.2698: 26 (20%); 10.9908: 52 (40%); 14.3364: 77 (59%); 24.988: 103 (79%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 100.0% | 6.5128, 8.0432, 9.5422, 12.8562 | 6.5128: 104 (80%); 8.0432: 78 (60%); 9.5422: 52 (40%); 12.8562: 26 (20%) | 6.5128: 26 (20%); 8.0432: 52 (40%); 9.5422: 78 (60%); 12.8562: 104 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -7.232, 7.2364, 15.3112, 34.6918 | -7.232: 104 (80%); 7.2364: 78 (60%); 15.3112: 52 (40%); 34.6918: 26 (20%) | -7.232: 26 (20%); 7.2364: 52 (40%); 15.3112: 78 (60%); 34.6918: 104 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0532, 0.0666, 0.0803, 0.1213 | 0.0532: 104 (80%); 0.0666: 78 (60%); 0.0803: 52 (40%); 0.1213: 27 (21%) | 0.0532: 26 (20%); 0.0666: 52 (40%); 0.0803: 78 (60%); 0.1213: 104 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.0517, 0.1009, 0.1524, 0.2157 | 0.0517: 104 (80%); 0.1009: 78 (60%); 0.1524: 53 (41%); 0.2157: 26 (20%) | 0.0517: 26 (20%); 0.1009: 52 (40%); 0.1524: 78 (60%); 0.2157: 104 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | 1.2147, 1.7252, 2.1425, 3.0509 | 1.2147: 104 (80%); 1.7252: 78 (60%); 2.1425: 52 (40%); 3.0509: 26 (20%) | 1.2147: 26 (20%); 1.7252: 52 (40%); 2.1425: 78 (60%); 3.0509: 104 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | 0.3859, 0.6929, 0.9473, 1.3858 | 0.3859: 104 (80%); 0.6929: 78 (60%); 0.9473: 52 (40%); 1.3858: 26 (20%) | 0.3859: 26 (20%); 0.6929: 52 (40%); 0.9473: 78 (60%); 1.3858: 104 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | 0.3238, 0.82, 1.4006, 2.2694 | 0.3238: 104 (80%); 0.82: 78 (60%); 1.4006: 52 (40%); 2.2694: 26 (20%) | 0.3238: 26 (20%); 0.82: 52 (40%); 1.4006: 78 (60%); 2.2694: 104 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | 5.9502, 7.9966, 9.8124, 13.3482 | 5.9502: 104 (80%); 7.9966: 78 (60%); 9.8124: 52 (40%); 13.3482: 26 (20%) | 5.9502: 26 (20%); 7.9966: 52 (40%); 9.8124: 78 (60%); 13.3482: 104 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 80.136, 91.976, 95.804, 98.584 | 80.136: 104 (80%); 91.976: 78 (60%); 95.804: 52 (40%); 98.584: 26 (20%) | 80.136: 26 (20%); 91.976: 52 (40%); 95.804: 78 (60%); 98.584: 104 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 61.596, 64.356, 67, 69.156 | 61.596: 104 (80%); 64.356: 78 (60%); 67: 52 (40%); 69.156: 26 (20%) | 61.596: 26 (20%); 64.356: 52 (40%); 67: 78 (60%); 69.156: 104 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 73.12, 75.414, 77.8, 81.448 | 73.12: 105 (81%); 75.414: 78 (60%); 77.8: 53 (41%); 81.448: 26 (20%) | 73.12: 27 (21%); 75.414: 52 (40%); 77.8: 79 (61%); 81.448: 104 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0299, 0.0386, 0.0508, 0.068 | 0.0299: 104 (80%); 0.0386: 78 (60%); 0.0508: 55 (42%); 0.068: 26 (20%) | 0.0299: 26 (20%); 0.0386: 52 (40%); 0.0508: 79 (61%); 0.068: 104 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0641, -0.0514, -0.0427, -0.032 | -0.0641: 104 (80%); -0.0514: 78 (60%); -0.0427: 53 (41%); -0.032: 28 (22%) | -0.0641: 26 (20%); -0.0514: 52 (40%); -0.0427: 79 (61%); -0.032: 104 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 130 (100%); 1: 37 (28%) | 0: 93 (72%); 1: 112 (86%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 98.5% | 33, 45, 56.2, 67 | 33: 105 (81%); 45: 81 (62%); 56.2: 51 (39%); 67: 30 (23%) | 33: 27 (21%); 45: 55 (42%); 56.2: 77 (59%); 67: 103 (79%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.5% | 0.0094, 0.0142, 0.0199, 0.0332 | 0.0094: 102 (78%); 0.0142: 77 (59%); 0.0199: 51 (39%); 0.0332: 26 (20%) | 0.0094: 26 (20%); 0.0142: 51 (39%); 0.0199: 77 (59%); 0.0332: 102 (78%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.814, 0.8616, 0.8904, 0.9207 | 0.814: 104 (80%); 0.8616: 78 (60%); 0.8904: 53 (41%); 0.9207: 27 (21%) | 0.814: 26 (20%); 0.8616: 52 (40%); 0.8904: 78 (60%); 0.9207: 104 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 22.64, 57.32, 95.94, 153.26 | 22.64: 104 (80%); 57.32: 78 (60%); 95.94: 52 (40%); 153.26: 26 (20%) | 22.64: 26 (20%); 57.32: 52 (40%); 95.94: 78 (60%); 153.26: 104 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | 2.1085, 3.2818, 6.639, 11.5495 | 2.1085: 104 (80%); 3.2818: 78 (60%); 6.639: 52 (40%); 11.5495: 26 (20%) | 2.1085: 26 (20%); 3.2818: 52 (40%); 6.639: 78 (60%); 11.5495: 104 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 77.852, 85.78, 88.926, 92.486 | 77.852: 104 (80%); 85.78: 79 (61%); 88.926: 52 (40%); 92.486: 26 (20%) | 77.852: 26 (20%); 85.78: 53 (41%); 88.926: 78 (60%); 92.486: 104 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 83.494, 87.326, 89.878, 91.792 | 83.494: 104 (80%); 87.326: 78 (60%); 89.878: 52 (40%); 91.792: 26 (20%) | 83.494: 26 (20%); 87.326: 52 (40%); 89.878: 78 (60%); 91.792: 104 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 72.274, 89.904, 97.454, 99.952 | 72.274: 104 (80%); 89.904: 78 (60%); 97.454: 52 (40%); 99.952: 26 (20%) | 72.274: 26 (20%); 89.904: 52 (40%); 97.454: 78 (60%); 99.952: 104 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 82.614, 92.988, 100 | 82.614: 104 (80%); 92.988: 78 (60%); 100: 60 (46%) | 82.614: 26 (20%); 92.988: 52 (40%); 100: 130 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 11, 16 | 5: 109 (84%); 9: 79 (61%); 11: 64 (49%); 16: 31 (24%) | 5: 28 (22%); 9: 58 (45%); 11: 79 (61%); 16: 105 (81%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5.8, 10, 13.4, 16 | 5.8: 104 (80%); 10: 85 (65%); 13.4: 52 (40%); 16: 36 (28%) | 5.8: 26 (20%); 10: 55 (42%); 13.4: 78 (60%); 16: 105 (81%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 55.744, 59.736, 62.304, 65.912 | 55.744: 104 (80%); 59.736: 78 (60%); 62.304: 52 (40%); 65.912: 26 (20%) | 55.744: 26 (20%); 59.736: 52 (40%); 62.304: 78 (60%); 65.912: 104 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.119, 0.2976, 0.5191, 0.808 | 0.119: 104 (80%); 0.2976: 79 (61%); 0.5191: 52 (40%); 0.808: 26 (20%) | 0.119: 26 (20%); 0.2976: 53 (41%); 0.5191: 78 (60%); 0.808: 104 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.04, 15.93, 18.39, 21.33 | 14.04: 105 (81%); 15.93: 79 (61%); 18.39: 54 (42%); 21.33: 27 (21%) | 14.04: 27 (21%); 15.93: 54 (42%); 18.39: 79 (61%); 21.33: 105 (81%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 14.04, 15.93, 18.39, 21.33 | 14.04: 105 (81%); 15.93: 79 (61%); 18.39: 54 (42%); 21.33: 27 (21%) | 14.04: 27 (21%); 15.93: 54 (42%); 18.39: 79 (61%); 21.33: 105 (81%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8485, 0.8727, 0.9095, 0.9614 | 0.8485: 104 (80%); 0.8727: 78 (60%); 0.9095: 54 (42%); 0.9614: 27 (21%) | 0.8485: 26 (20%); 0.8727: 52 (40%); 0.9095: 79 (61%); 0.9614: 105 (81%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.96, 1.156, 1.472, 1.912 | 0.96: 105 (81%); 1.156: 78 (60%); 1.472: 52 (40%); 1.912: 26 (20%) | 0.96: 29 (22%); 1.156: 52 (40%); 1.472: 78 (60%); 1.912: 104 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.055, 0.0825, 0.1158, 0.168 | 0.055: 104 (80%); 0.0825: 78 (60%); 0.1158: 52 (40%); 0.168: 26 (20%) | 0.055: 26 (20%); 0.0825: 52 (40%); 0.1158: 78 (60%); 0.168: 104 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 46.8872, 68.7194, 129.3698, 201.0402 | 46.8872: 104 (80%); 68.7194: 78 (60%); 129.3698: 52 (40%); 201.0402: 26 (20%) | 46.8872: 26 (20%); 68.7194: 52 (40%); 129.3698: 78 (60%); 201.0402: 104 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 44.6698, 67.3787, 124.1443, 195.0986 | 44.6698: 104 (80%); 67.3787: 78 (60%); 124.1443: 52 (40%); 195.0986: 26 (20%) | 44.6698: 26 (20%); 67.3787: 52 (40%); 124.1443: 78 (60%); 195.0986: 104 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 42.8897, 65.7735, 121.3603, 184.9651 | 42.8897: 104 (80%); 65.7735: 78 (60%); 121.3603: 52 (40%); 184.9651: 26 (20%) | 42.8897: 26 (20%); 65.7735: 52 (40%); 121.3603: 78 (60%); 184.9651: 104 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 47.9145, 70.6691, 134.9661, 206.8067 | 47.9145: 104 (80%); 70.6691: 78 (60%); 134.9661: 52 (40%); 206.8067: 26 (20%) | 47.9145: 26 (20%); 70.6691: 52 (40%); 134.9661: 78 (60%); 206.8067: 104 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 49.2681, 72.2127, 138.1784, 211.5629 | 49.2681: 104 (80%); 72.2127: 78 (60%); 138.1784: 52 (40%); 211.5629: 26 (20%) | 49.2681: 26 (20%); 72.2127: 52 (40%); 138.1784: 78 (60%); 211.5629: 104 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 130 (100%) | 0: 121 (93%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0, 0.1394 | 0: 130 (100%); 0.1394: 26 (20%) | 0: 101 (78%); 0.1394: 104 (80%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | 0.0606, 0.0854, 0.1037, 0.141 | 0.0606: 104 (80%); 0.0854: 78 (60%); 0.1037: 52 (40%); 0.141: 26 (20%) | 0.0606: 27 (21%); 0.0854: 53 (41%); 0.1037: 78 (60%); 0.141: 104 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -23.014, -18.36, -14.668, -11.566 | -23.014: 104 (80%); -18.36: 79 (61%); -14.668: 52 (40%); -11.566: 26 (20%) | -23.014: 26 (20%); -18.36: 53 (41%); -14.668: 78 (60%); -11.566: 104 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.2% | 0.4804, 0.7752, 0.997, 1.2495 | 0.4804: 103 (79%); 0.7752: 77 (59%); 0.997: 52 (40%); 1.2495: 26 (20%) | 0.4804: 26 (20%); 0.7752: 52 (40%); 0.997: 77 (59%); 1.2495: 103 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.2% | 3, 5, 7, 9 | 3: 108 (83%); 5: 83 (64%); 7: 53 (41%); 9: 29 (22%) | 3: 35 (27%); 5: 61 (47%); 7: 89 (68%); 9: 116 (89%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.2% | 0.1773, 0.2095, 0.262, 0.3298 | 0.1773: 103 (79%); 0.2095: 77 (59%); 0.262: 52 (40%); 0.3298: 26 (20%) | 0.1773: 26 (20%); 0.2095: 52 (40%); 0.262: 77 (59%); 0.3298: 103 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.2% | 2, 5, 7, 9 | 2: 115 (88%); 5: 78 (60%); 7: 57 (44%); 9: 34 (26%) | 2: 27 (21%); 5: 63 (48%); 7: 80 (62%); 9: 112 (86%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.2% | 0.0287, 0.038, 0.0485, 0.0618 | 0.0287: 103 (79%); 0.038: 78 (60%); 0.0485: 53 (41%); 0.0618: 27 (21%) | 0.0287: 26 (20%); 0.038: 52 (40%); 0.0485: 78 (60%); 0.0618: 103 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.2% | 5, 7, 9, 10 | 5: 104 (80%); 7: 83 (64%); 9: 54 (42%); 10: 30 (23%) | 5: 39 (30%); 7: 58 (45%); 9: 99 (76%); 10: 129 (99%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.2% | -0.1891, -0.0204, 0.0649, 0.2897 | -0.1891: 103 (79%); -0.0204: 77 (59%); 0.0649: 52 (40%); 0.2897: 26 (20%) | -0.1891: 26 (20%); -0.0204: 52 (40%); 0.0649: 77 (59%); 0.2897: 103 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.2% | 2, 5, 6, 9 | 2: 116 (89%); 5: 79 (61%); 6: 65 (50%); 9: 27 (21%) | 2: 28 (22%); 5: 64 (49%); 6: 78 (60%); 9: 116 (89%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 8.5% |
| 8k_item_5_02_filed_within_7d | 5.4% |
| above_avwap_20high | 2.3% |
| above_avwap_252low | 99.2% |
| above_cam_r3 | 33.1% |
| above_cam_r4 | 23.8% |
| above_cpr | 83.1% |
| above_pivot | 80.8% |
| above_prev_high | 40.8% |
| above_prev_high_clearance_atr_05 | 19.2% |
| above_r1 | 25.4% |
| above_r2 | 20.8% |
| above_vwap | 72.3% |
| above_wood_p | 91.5% |
| ad_rising | 63.1% |
| adx_cross_up | 12.3% |
| adx_cross_up_20 | 7.7% |
| adx_strong | 7.7% |
| adx_trending | 55.4% |
| ao_cross_up | 3.1% |
| at_key_fib | 3.8% |
| at_key_fib_wide | 9.2% |
| avwap_20high_loss_recent_3d | 56.2% |
| avwap_20high_reclaim_recent_3d | 6.2% |
| avwap_20low_reclaim_recent_3d | 6.2% |
| avwap_252low_reclaim_recent_3d | 6.2% |
| avwap_50low_reclaim_recent_3d | 3.8% |
| bb_10_20_expanding | 91.5% |
| bb_10_20_pctb_gt_8 | 95.4% |
| bb_10_20_pctb_gt_85 | 76.2% |
| bb_10_20_pctb_gt_9 | 50.8% |
| bb_10_20_pctb_gt_95 | 27.7% |
| bb_10_20_reclaim_from_upper_recent_3d | 50.0% |
| bb_10_20_squeeze | 11.5% |
| bb_10_20_touch_upper | 26.2% |
| bb_20_15_expanding | 93.1% |
| bb_20_15_squeeze | 33.8% |
| bb_20_20_expanding | 93.1% |
| bb_20_20_pctb_gt_95 | 96.9% |
| bb_20_20_reclaim_from_upper_recent_3d | 25.4% |
| bb_20_20_squeeze | 12.3% |
| bearish_pin_bar | 60.8% |
| below_avwap_20high | 97.7% |
| below_avwap_252low | 0.8% |
| below_cam_s3 | 8.5% |
| below_cam_s4 | 2.3% |
| below_cpr | 19.2% |
| below_ema_200 | 18.5% |
| below_prev_high | 58.5% |
| below_s1 | 1.5% |
| below_sma_200 | 22.3% |
| below_vwap | 27.7% |
| blowoff_recent_3d | 2.3% |
| break_52w_high | 10.8% |
| break_52w_high_clearance_atr_05 | 4.6% |
| break_52w_high_confirmed_today | 25.4% |
| ceo_buy | 1.6% |
| chandelier_long_bullish | 98.5% |
| chandelier_long_flip_dn | 1.5% |
| chandelier_short_bearish | 1.5% |
| chandelier_short_flip_up | 5.4% |
| close_above_open | 20.0% |
| close_below_open | 80.0% |
| close_in_bottom_40pct_of_range | 96.2% |
| cmf_cross_dn | 12.3% |
| cmf_negative | 29.2% |
| cmf_positive | 70.8% |
| concentrated_sell | 8.7% |
| cpr_narrow | 86.9% |
| cpr_narrow_tight | 20.0% |
| cup_handle_detected | 17.7% |
| cup_handle_neckline_break_retest_long | 27.7% |
| dc10_breakout_up | 42.3% |
| dc10_breakout_up_1pct | 70.0% |
| dc10_new_high | 87.7% |
| dc10_strong_breakout_up | 19.2% |
| dc20_breakout_up | 41.5% |
| dc20_new_high | 87.7% |
| dc20_resistance_break_retest_strong | 57.7% |
| defensive_leadership | 29.2% |
| director_only_buy | 2.4% |
| double_bottom_detected | 14.6% |
| double_top_detected | 21.5% |
| dpi_elevated | 47.9% |
| drying_volume_on_down_turn | 19.2% |
| drying_volume_on_up_turn | 6.9% |
| ema_20_50_bearish | 17.7% |
| ema_20_50_bullish | 82.3% |
| ema_20_50_golden_cross | 6.9% |
| ema_50_200_bearish | 43.8% |
| ema_50_200_bullish | 56.2% |
| ema_50_200_golden_cross | 0.8% |
| ema_9_21_golden_cross | 1.5% |
| flag_bull_break_retest_long | 10.0% |
| flag_bull_broke | 10.0% |
| force_index_cross_up | 1.5% |
| gap_up_1_5pct | 26.2% |
| gap_up_2pct | 23.1% |
| head_shoulders_bottom_detected | 8.5% |
| head_shoulders_top_detected | 4.6% |
| house_cluster_buy | 3.1% |
| house_cluster_sell | 6.2% |
| htf_aligned_bull | 74.6% |
| htf_disagreement | 3.8% |
| hull_flip_up | 2.3% |
| ichi_above_cloud | 85.4% |
| ichi_above_cloud_break_recent_5d | 26.2% |
| ichi_below_cloud | 0.8% |
| ichi_cloud_thick | 89.2% |
| ichi_tk_bullish | 92.3% |
| ichi_tk_cross_up | 4.6% |
| ichi_weekly_above_cloud | 62.8% |
| ichi_weekly_below_cloud | 24.0% |
| ichi_weekly_in_cloud | 13.2% |
| inside_bar | 10.0% |
| inside_cpr | 3.1% |
| inside_kc | 16.2% |
| institutional_buy | 90.0% |
| institutional_negative | 5.4% |
| institutional_persistence_growing | 35.0% |
| institutional_persistence_strong | 58.3% |
| institutional_strong_buy | 83.1% |
| inverted_cup_handle_detected | 10.8% |
| is_friday | 18.5% |
| is_halloween_period | 52.3% |
| is_halloween_period_first_day | 1.5% |
| is_january | 11.5% |
| is_january_extended | 11.5% |
| is_monday | 26.9% |
| is_pre_holiday | 1.5% |
| is_summer_period | 47.7% |
| is_totm_window | 30.0% |
| is_totm_window_first_day | 7.7% |
| is_week_open | 30.0% |
| kc_touch_upper | 94.6% |
| large_dollar_buy | 0.8% |
| macd_12_26_9_bearish | 2.3% |
| macd_12_26_9_bullish | 97.7% |
| macd_12_26_9_crossover_up | 6.9% |
| macd_8_21_5_crossover_up | 3.8% |
| mfi_broad_overbought | 53.1% |
| mfi_overbought | 20.8% |
| monthly_above_sma_12 | 76.0% |
| monthly_above_sma_6 | 91.5% |
| monthly_bias_bear | 7.8% |
| monthly_bias_bull | 75.2% |
| monthly_momentum_pos | 72.9% |
| morning_star | 0.8% |
| near_52w_high | 30.0% |
| near_52w_high_95pct | 48.5% |
| near_avwap_20low_atr_10x | 0.8% |
| near_avwap_20low_atr_15x | 6.9% |
| near_avwap_20low_atr_20x | 20.0% |
| near_avwap_252low_atr_05x | 0.8% |
| near_avwap_252low_atr_10x | 2.3% |
| near_avwap_252low_atr_15x | 3.1% |
| near_avwap_252low_atr_20x | 7.0% |
| near_avwap_50low_atr_20x | 0.8% |
| near_cam_r3 | 16.9% |
| near_cam_s3 | 9.2% |
| near_cam_s4 | 4.6% |
| near_fib_236 | 3.8% |
| near_fib_382 | 3.8% |
| near_pivot | 16.2% |
| near_prev_close | 31.5% |
| near_prev_high | 15.4% |
| near_prev_low | 3.8% |
| near_r1 | 9.2% |
| near_r1_wide | 54.6% |
| near_r2 | 4.6% |
| near_r2_wide | 27.7% |
| near_s1 | 3.8% |
| near_s1_wide | 26.9% |
| near_s2_wide | 6.9% |
| near_wood_r1 | 16.2% |
| near_wood_s1 | 1.5% |
| news_uses_polygon_score | 27.7% |
| obv_bearish | 3.8% |
| obv_bullish | 96.2% |
| obv_falling | 6.2% |
| obv_rising | 93.8% |
| pead_negative_surprise | 13.3% |
| pead_positive_surprise | 25.8% |
| pin_bar | 60.8% |
| po3_accumulation_active | 16.2% |
| po3_bearish | 70.0% |
| po3_manipulation_sweep_up | 15.4% |
| po3_mmsm_setup | 3.8% |
| po3_sweep_above_prior_high | 90.0% |
| po3_sweep_below_prior_low | 2.3% |
| ppo_bullish | 96.2% |
| ppo_crossover_up | 6.2% |
| pre_fomc_d0 | 3.1% |
| pre_fomc_d1 | 3.1% |
| pre_fomc_window | 6.2% |
| price_above_ema_200 | 81.5% |
| price_above_ema_200_break_recent_5d | 16.9% |
| price_above_ema_20_break_recent_5d | 18.5% |
| price_above_ema_21_break_recent_5d | 20.0% |
| price_above_ema_50_break_recent_5d | 24.6% |
| price_above_ema_9_break_recent_5d | 27.7% |
| price_above_sma_200 | 77.7% |
| psar_bullish | 99.2% |
| psar_flip_up | 1.5% |
| r1_break_retest_long | 96.2% |
| recent_blowoff_at_r3 | 1.5% |
| resistance_break_retest | 84.6% |
| risk_off_regime_bond_signal | 19.2% |
| risk_off_regime_bond_signal_strong | 8.5% |
| risk_off_regime_gold_signal | 30.8% |
| risk_on_regime_bond_signal | 55.4% |
| risk_on_regime_bond_signal_strong | 30.8% |
| roc_turning_up | 3.1% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 2.3% |
| rsi_14_cross_dn_overbought_recent_3d | 6.2% |
| rsi_14_extreme_ob | 6.9% |
| rsi_14_overbought | 56.2% |
| rsi_14_rising | 62.3% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 1.5% |
| rsi_21_cross_dn_overbought_recent_3d | 3.8% |
| rsi_21_overbought | 17.7% |
| rsi_21_rising | 62.3% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 20.0% |
| rsi_2_cross_dn_overbought_recent_3d | 9.2% |
| rsi_2_cross_up_extreme_os_recent_3d | 7.7% |
| rsi_2_cross_up_oversold_recent_3d | 8.5% |
| rsi_2_extreme_ob | 80.0% |
| rsi_2_overbought | 90.8% |
| rsi_2_rising | 62.3% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 13.1% |
| rsi_9_extreme_ob | 23.8% |
| rsi_9_overbought | 97.7% |
| rsi_9_rising | 62.3% |
| sc_13d_filed_within_30d | 2.6% |
| sc_13g_filed_within_30d | 2.4% |
| sma_20_50_bullish | 73.8% |
| sma_20_50_golden_cross | 5.4% |
| sma_50_200_bullish | 51.5% |
| sma_9_21_bullish | 96.2% |
| sma_9_21_golden_cross | 3.1% |
| smc_bos_bearish | 6.9% |
| smc_bos_bullish | 20.0% |
| smc_bos_retest_long | 4.6% |
| smc_bos_retest_short | 1.5% |
| smc_breaker_block_bearish | 12.3% |
| smc_breaker_block_bullish | 31.5% |
| smc_choch_bearish | 1.5% |
| smc_choch_bullish | 12.3% |
| smc_equal_highs_swept | 6.2% |
| smc_equal_lows_swept | 3.1% |
| smc_fvg_bearish_active | 3.8% |
| smc_fvg_bullish_active | 95.4% |
| smc_fvg_retest_long_zone | 57.7% |
| smc_fvg_retest_short_zone | 2.3% |
| smc_in_discount_zone | 3.1% |
| smc_inverse_fvg_bearish | 25.4% |
| smc_liquidity_swept_dn | 1.5% |
| smc_liquidity_swept_up | 3.1% |
| smc_mitigation_block_short | 9.2% |
| smc_ob_bearish_active | 21.5% |
| smc_ob_bullish_active | 52.3% |
| smc_ote_long_zone | 3.8% |
| smc_ote_short_zone | 10.0% |
| squeeze_in | 12.3% |
| stoch_bearish_cross | 27.7% |
| stoch_broad_overbought | 91.5% |
| stoch_bullish_cross | 6.2% |
| stoch_overbought | 86.9% |
| stochrsi_cross_dn | 29.2% |
| stochrsi_cross_up | 10.0% |
| stochrsi_overbought | 82.3% |
| stochrsi_oversold | 1.5% |
| tema_above_dema | 96.2% |
| tema_cross_up | 9.2% |
| three_white_soldiers | 6.2% |
| triangle_apex_break_retest_long | 33.1% |
| triangle_ascending_detected | 20.8% |
| triangle_descending_detected | 2.3% |
| uo_overbought | 6.2% |
| usd_strengthening | 19.2% |
| usd_weakening | 6.2% |
| vix_band_high | 27.7% |
| vix_band_low | 42.3% |
| vix_band_mid | 30.0% |
| vix_term_backwardation | 6.2% |
| vix_term_contango | 93.8% |
| vol_above_avg | 73.8% |
| vol_below_avg | 26.2% |
| vol_spike_12x | 53.1% |
| vol_spike_15x | 37.7% |
| vol_spike_17x | 28.5% |
| vol_spike_2x | 18.5% |
| vol_spike_2x_on_down_day_recent_3d | 1.5% |
| vol_spike_2x_on_up_day_recent_3d | 22.3% |
| vol_spike_3x | 6.2% |
| vp_above_value_area | 88.5% |
| vp_close_above_poc | 96.9% |
| vp_close_below_poc | 3.1% |
| vp_in_value_area | 11.5% |
| week_open_gap_up_15pct | 8.5% |
| weekly_above_ema_20 | 94.6% |
| weekly_bias_bull | 94.6% |
| williams_r_overbought | 68.5% |
| williams_r_rising | 10.0% |
| within_pead_window | 40.0% |
| xs_avoid_high_ivol | 73.6% |
| xs_avoid_high_max | 58.1% |
| xs_high_beta_decile | 22.5% |
| xs_low_beta_bottom_quintile | 22.5% |
| xs_low_beta_decile | 16.3% |
| xs_low_beta_decile_entry_recent_5d | 2.3% |
| xs_low_beta_top_quintile | 16.3% |
| xs_momentum_bottom_decile | 10.1% |
| xs_momentum_bottom_quintile | 21.7% |
| xs_momentum_top_decile | 10.1% |
| xs_momentum_top_quintile | 20.9% |
| xs_quality_bottom_quintile | 26.2% |
| xs_quality_top_quintile | 16.7% |
| xs_quality_top_tercile | 33.3% |
| year_high_break_retest_long | 14.6% |
| yoy_surprise_high | 50.8% |
| yoy_surprise_negative | 35.7% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 92.3% |
| committed_growth_holders | 92.3% |
| corp_donations_1y | 9.2% |
| corp_donations_count_1y | 9.2% |
| corp_donations_unique_pacs | 9.2% |
| cot_rut_commercials_pctile_3y | 56.2% |
| cot_rut_mmoney_pctile_3y | 56.2% |
| cup_handle_depth_pct | 20.8% |
| days_since_deletion | 9.2% |
| days_since_inclusion | 12.3% |
| days_to_next_holiday | 60.8% |
| days_to_rebalance | 5.4% |
| dpi_30d_avg | 93.1% |
| dpi_recent | 93.1% |
| earnings_announcement_return | 92.3% |
| earnings_eps_yoy_growth | 96.9% |
| gov_contracts_4q_sum | 45.4% |
| gov_contracts_last_qtr_amount | 45.4% |
| gov_contracts_qoq_growth | 45.4% |
| head_shoulders_magnitude_pct | 12.3% |
| insider_officer_buyers_30d | 3.1% |
| insider_total_shares_bought_30d | 3.1% |
| inverted_cup_handle_height_pct | 22.3% |
| lobbying_amount_1y | 71.5% |
| lobbying_amount_q | 71.5% |
| lobbying_amount_yoy | 71.5% |
| otc_short_ratio_recent | 93.1% |
| otc_volume_recent | 93.1% |
| pair_half_life | 93.1% |
| pair_max_abs_zscore | 93.1% |
| pair_zscore_signed | 93.1% |
| pct_from_avwap_20high | 12.3% |
| persistent_holders_4q | 92.3% |
| persistent_holders_8q | 92.3% |
| search_volume_index_recent | 86.9% |
| search_volume_observations | 86.9% |
| search_volume_zscore_30d | 86.9% |
| total_active_holders | 92.3% |
| triangle_breakdown_pct | 2.3% |
| triangle_breakout_pct | 20.8% |
| xs_quality_decile | 64.6% |
| xs_quality_gross_profitability | 64.6% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.998), `avwap_20low` (0.999), `avwap_252low` (0.993), `avwap_50low` (0.999), `bb_10_20_lower` (0.999), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.998), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.998), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.998), `cam_r2` (0.998), `cam_r3` (0.998), `cam_r4` (0.998), `cam_s1` (0.998), `cam_s2` (0.998), `cam_s3` (0.998), `cam_s4` (0.999), `chandelier_long_value` (0.998), `chandelier_short_value` (0.999), `cpr_bottom` (0.998), `cpr_top` (0.998), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.999), `dc10_lower` (0.999), `dc10_mid` (0.999), `dc10_upper` (0.997), `dc20_lower` (0.999), `dc20_mid` (0.999), `dc20_upper` (0.997), `dema` (0.999), `double_bottom_neckline` (1.0), `double_bottom_trough` (0.993), `double_top_neckline` (0.991), `double_top_peak` (0.998), `entry_stop_long` (0.999), `entry_stop_short` (0.997), `fib_236` (0.997), `fib_382` (0.998), `fib_500` (0.998), `fib_618` (0.997), `fib_786` (0.996), `fib_ext_127` (0.994), `fib_ext_162` (0.99), `head_shoulders_bottom_neckline` (0.991), `head_shoulders_top_neckline` (1.0), `hull_ma` (0.999), `ichi_kijun` (0.999), `ichi_senkou_a` (0.995), `ichi_senkou_b` (0.991), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.997), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (0.999), `monthly_close` (0.998), `monthly_sma_12` (0.984), `monthly_sma_6` (0.995), `pivot` (0.998), `prev_close` (0.998), `prev_high` (0.998), `prev_low` (0.998), `psar_value` (0.999), `r1` (0.998), `r2` (0.997), `r3` (0.996), `s1` (0.999), `s2` (0.999), `s3` (0.999), `supertrend_value` (0.999), `swing_high` (0.996), `swing_low` (0.994), `tema` (0.999), `triangle_resistance_level` (0.996), `triangle_support_level` (1.0), `vp_poc` (0.994), `vp_value_area_high` (0.997), `vp_value_area_low` (0.993), `weekly_close` (0.998), `weekly_ema_10` (0.999), `weekly_ema_20` (0.996), `wood_p` (0.998), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.998), `wood_s2` (0.999), `year_high` (0.967), `year_low` (0.975)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | mirror of touch_lower | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1 | implicit anatomy knobs (min body/wick/st | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P3 | rsi_14 > 65 | 5 | subset-safe | no - derives offline |
| P4 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     1 x 1 x 5 x 1 = 5
offline gradings   5 level-combinations x 24 exits = 120
ENGINE RUNS        1 (every fire-adding axis sits at production-only until its env actuator exists)
check              1 x 5 = 5
```

B-row candidates NOT in this factorial: 451 census axes join it only when REGISTERED at the T3 band review.
