# Table A - ultimate_oscillator

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit 8233e68a5 at 2026-09-17 00:26:53 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** momentum | **status:** NOT-STARTED | **R5 fires:** 592 | **surviving fires (T1):** 592 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  below_sma_200  <- backtest/signals/screener.py
       knobs P1.1-P1.1 (band rows in Table A)
P2  close_above_open  <- backtest/signals/screener.py +1
       knobs P2.1-P2.1 (band rows in Table A)
P3  close_below_open  <- backtest/signals/screener.py +1
       knobs P3.1-P3.1 (band rows in Table A)
P4  price_above_sma_200  <- backtest/signals/screener.py
       knobs P4.1-P4.1 (band rows in Table A)
P5  rsi_2  <- backtest/signals/screener.py
       knobs P5.1-P5.1 (band rows in Table A)
P6  uo_overbought  <- backtest/signals/screener.py +1
       knobs P6.1-P6.1 (band rows in Table A)
P7  uo_oversold  <- backtest/signals/screener.py +1
       knobs P7.1-P7.2 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P8  uo > 70   [EXISTING-THRESHOLD]
P9  _short_borrow_trap_active(s)   [helper gate]
P10  rsi_2 escape-hatch thresholds (long < 5, short > 95)   [local-variable gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_ultimate_oscillator (docstring and return dropped):

```python
rsi_2 = s.get('rsi_2', 50)
fl = (s.get('uo_oversold') or rsi_2 < 5) and s.get('price_above_sma_200') and s.get('close_above_open')
fs = (s.get('uo_overbought') or rsi_2 > 95) and s.get('below_sma_200') and s.get('close_below_open') and (not _short_borrow_trap_active(s))
```

## Table A - parameter inventory (canonical shape - READY FOR OWNER BAND REVIEW)

One row per parameter the entry condition touches, BOTH layers, nothing
omitted (L785: an axis left out of Table A is invisible at close).
Every producer row carries its DEFINED BANDS in the P<n>.x rows beneath
it (B2845, owner-corrected: a ready and FINAL Table A per strategy);
the engine-spec (SPECS) entry is built from these before any engine
leg runs.

| id | layer | producer / parameter | production | free_band (OFFLINE) | resim_band (RESIM) | status |
|---|---|---|---|---|---|---|
| P1 | PRODUCER | below_sma_200 - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | sma span - backtest/signals/technical.py sma block | 200 | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production with adjacent canon spans; T3 review before any grid |
| P2 | PRODUCER | close_above_open - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | (structural) c > o - optional min body pct - backtest/signals/technical.py bar-anatomy block | 0.0 | none - bar OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET zero; T3 review before any grid |
| P3 | PRODUCER | close_below_open - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | mirror of close_above_open - technical.py bar-anatomy block | 0.0 | none | the whole band; DEFINED-NO-ACTUATOR | mirror; T3 review before any grid |
| P4 | PRODUCER | price_above_sma_200 - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P4.x) | BANDS-DEFINED |
| P4.1 | BAND | sma span - backtest/signals/technical.py sma block | 200 | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production with adjacent canon spans; T3 review before any grid |
| P5 | PRODUCER | rsi_2 - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P5.x) | BANDS-DEFINED |
| P5.1 | BAND | rsi (fast escape-hatch) span - backtest/signals/technical.py rsi block | 2 | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production with adjacent canon spans; T3 review before any grid |
| P6 | PRODUCER | uo_overbought - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P6.x) | BANDS-DEFINED |
| P6.1 | BAND | overbought threshold - backtest/signals/technical.py:752 | 70 | TIGHTER (> 75, > 80) where `uo` is persisted | LOOSER; DEFINED-NO-ACTUATOR | BRACKET canon 70 (mirror of oversold); T3 review before any grid |
| P7 | PRODUCER | uo_oversold - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P7.x) | BANDS-DEFINED |
| P7.1 | BAND | oversold threshold - None | 30 | TIGHTER (< 25, < 20) where `uo` is persisted on the fires | LOOSER; and the (7,14,28) period triple; env backtest/signals/technical.py:751 | BRACKET canon 30; the uo value itself is persisted where emitted; T3 review before any grid |
| P7.2 | BAND | period triple - backtest/signals/technical.py:738-750 | (7, 14, 28) | none - other triples unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET canon triple; T3 review before any grid |
| P8 | STRATEGY | uo `> 70` [EXISTING-THRESHOLD] | `> 70` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P9 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| P10 | STRATEGY | rsi_2 escape-hatch thresholds (long < 5, short > 95) - backtest/signals/screener.py strat_ultimate_oscillator (local rsi_2 compare - invisible to the extractor) | 5 / 95 | TIGHTER (< 3, > 97) - subset on persisted rsi_2 | LOOSER | BRACKET production (Connors RSI-2 canon); rsi_2 persisted; T3 review |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | - | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| uo | backtest/signals/screener.py +1 | `> 70` | 100.0% | TIGHTER = RAISE the floor: (no QUANTS level sits tighter than production - band at T3) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 17.792, 21.398, 25.808, 30.378 | 17.792: 473 (80%); 21.398: 355 (60%); 25.808: 237 (40%); 30.378: 119 (20%) | 17.792: 119 (20%); 21.398: 237 (40%); 25.808: 355 (60%); 30.378: 473 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 15.624, 19.782, 25.024, 32.484 | 15.624: 473 (80%); 19.782: 355 (60%); 25.024: 237 (40%); 32.484: 119 (20%) | 15.624: 119 (20%); 19.782: 237 (40%); 25.024: 355 (60%); 32.484: 473 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 16.978, 24.078, 30.002, 35.556 | 16.978: 473 (80%); 24.078: 355 (60%); 30.002: 237 (40%); 35.556: 119 (20%) | 16.978: 119 (20%); 24.078: 237 (40%); 30.002: 355 (60%); 35.556: 473 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -4.1923, -0.885, 0.9049, 4.3556 | -4.1923: 473 (80%); -0.885: 355 (60%); 0.9049: 237 (40%); 4.3556: 119 (20%) | -4.1923: 119 (20%); -0.885: 237 (40%); 0.9049: 355 (60%); 4.3556: 473 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.0587, 1.9664, 3.4073, 6.0514 | 1.0587: 473 (80%); 1.9664: 355 (60%); 3.4073: 237 (40%); 6.0514: 119 (20%) | 1.0587: 119 (20%); 1.9664: 237 (40%); 3.4073: 355 (60%); 6.0514: 473 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.0587, 1.9664, 3.4073, 6.0514 | 1.0587: 473 (80%); 1.9664: 355 (60%); 3.4073: 237 (40%); 6.0514: 119 (20%) | 1.0587: 119 (20%); 1.9664: 237 (40%); 3.4073: 355 (60%); 6.0514: 473 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.3444, 2.776, 3.2692, 4.0184 | 2.3444: 473 (80%); 2.776: 356 (60%); 3.2692: 237 (40%); 4.0184: 119 (20%) | 2.3444: 119 (20%); 2.776: 238 (40%); 3.2692: 355 (60%); 4.0184: 473 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0875, 0.1209, 0.1528, 0.1963 | 0.0875: 473 (80%); 0.1209: 356 (60%); 0.1528: 237 (40%); 0.1963: 119 (20%) | 0.0875: 119 (20%); 0.1209: 237 (40%); 0.1528: 355 (60%); 0.1963: 474 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.1288, 0.7591, 0.8636, 0.9339 | 0.1288: 474 (80%); 0.7591: 355 (60%); 0.8636: 237 (40%); 0.9339: 119 (20%) | 0.1288: 120 (20%); 0.7591: 237 (40%); 0.8636: 355 (60%); 0.9339: 474 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0773, 0.1028, 0.1267, 0.1686 | 0.0773: 474 (80%); 0.1028: 355 (60%); 0.1267: 237 (40%); 0.1686: 120 (20%) | 0.0773: 119 (20%); 0.1028: 237 (40%); 0.1267: 356 (60%); 0.1686: 474 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.0827, 0.592, 1.0353, 1.1846 | -0.0827: 474 (80%); 0.592: 355 (60%); 1.0353: 237 (40%); 1.1846: 119 (20%) | -0.0827: 119 (20%); 0.592: 237 (40%); 1.0353: 355 (60%); 1.1846: 473 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.1031, 0.1371, 0.1689, 0.2248 | 0.1031: 474 (80%); 0.1371: 355 (60%); 0.1689: 237 (40%); 0.2248: 119 (20%) | 0.1031: 120 (20%); 0.1371: 237 (40%); 0.1689: 356 (60%); 0.2248: 474 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.063, 0.5689, 0.9015, 1.0134 | 0.063: 474 (80%); 0.5689: 355 (60%); 0.9015: 237 (40%); 1.0134: 119 (20%) | 0.063: 120 (20%); 0.5689: 237 (40%); 0.9015: 355 (60%); 1.0134: 473 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0463, -0.0214, -0.0061, 0.0261 | -0.0463: 473 (80%); -0.0214: 356 (60%); -0.0061: 244 (41%); 0.0261: 119 (20%) | -0.0463: 119 (20%); -0.0214: 237 (40%); -0.0061: 369 (62%); 0.0261: 473 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1412, 0.1692, 0.2098, 0.2664 | 0.1412: 472 (80%); 0.1692: 355 (60%); 0.2098: 238 (40%); 0.2664: 119 (20%) | 0.1412: 120 (20%); 0.1692: 237 (40%); 0.2098: 354 (60%); 0.2664: 473 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 592 (100%) | 0: 568 (96%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1088, -0.006, 0.0783, 0.1678 | -0.1088: 473 (80%); -0.006: 355 (60%); 0.0783: 237 (40%); 0.1678: 120 (20%) | -0.1088: 119 (20%); -0.006: 237 (40%); 0.0783: 356 (60%); 0.1678: 474 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 592 (100%); 1: 210 (35%) | 0: 382 (65%); 1: 502 (85%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.258, -0.1931, -0.1435, -0.1063 | -0.258: 473 (80%); -0.1931: 357 (60%); -0.1435: 239 (40%); -0.1063: 127 (21%) | -0.258: 119 (20%); -0.1931: 239 (40%); -0.1435: 356 (60%); -0.1063: 489 (83%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3795, 0.609, 0.7115, 0.7949 | 0.3795: 473 (80%); 0.609: 358 (60%); 0.7115: 238 (40%); 0.7949: 125 (21%) | 0.3795: 119 (20%); 0.609: 241 (41%); 0.7115: 356 (60%); 0.7949: 482 (81%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.25, 0.3526, 0.6641, 0.8526 | 0.25: 477 (81%); 0.3526: 356 (60%); 0.6641: 237 (40%); 0.8526: 123 (21%) | 0.25: 128 (22%); 0.3526: 242 (41%); 0.6641: 355 (60%); 0.8526: 475 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0892, -0.0097, 0.0722, 0.262 | -0.0892: 477 (81%); -0.0097: 364 (61%); 0.0722: 240 (41%); 0.262: 123 (21%) | -0.0892: 121 (20%); -0.0097: 250 (42%); 0.0722: 356 (60%); 0.262: 475 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3013, 0.4551, 0.6218, 0.8462 | 0.3013: 477 (81%); 0.4551: 367 (62%); 0.6218: 238 (40%); 0.8462: 121 (20%) | 0.3013: 120 (20%); 0.4551: 246 (42%); 0.6218: 359 (61%); 0.8462: 474 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1474, 0.2885, 0.4744, 0.6218 | 0.1474: 474 (80%); 0.2885: 357 (60%); 0.4744: 240 (41%); 0.6218: 146 (25%) | 0.1474: 125 (21%); 0.2885: 242 (41%); 0.4744: 356 (60%); 0.6218: 475 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5622, -0.3438, -0.169, 0.0839 | -0.5622: 476 (80%); -0.3438: 356 (60%); -0.169: 238 (40%); 0.0839: 120 (20%) | -0.5622: 120 (20%); -0.3438: 240 (41%); -0.169: 357 (60%); 0.0839: 494 (83%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2885, 0.5064, 0.6987, 0.9167 | 0.2885: 479 (81%); 0.5064: 358 (60%); 0.6987: 244 (41%); 0.9167: 151 (26%) | 0.2885: 123 (21%); 0.5064: 238 (40%); 0.6987: 368 (62%); 0.9167: 488 (82%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.141, 0.359, 0.5513, 0.7628 | 0.141: 484 (82%); 0.359: 370 (62%); 0.5513: 241 (41%); 0.7628: 127 (21%) | 0.141: 122 (21%); 0.359: 244 (41%); 0.5513: 363 (61%); 0.7628: 477 (81%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0646, -0.0525, -0.0384, 0 | -0.0646: 476 (80%); -0.0525: 360 (61%); -0.0384: 248 (42%); 0: 144 (24%) | -0.0646: 121 (20%); -0.0525: 243 (41%); -0.0384: 368 (62%); 0: 581 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4487, 0.6282, 0.882, 0.9936 | 0.4487: 474 (80%); 0.6282: 356 (60%); 0.882: 237 (40%); 0.9936: 135 (23%) | 0.4487: 123 (21%); 0.6282: 239 (40%); 0.882: 355 (60%); 0.9936: 481 (81%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0833, 0.2372, 0.5513, 0.8462 | 0.0833: 478 (81%); 0.2372: 363 (61%); 0.5513: 238 (40%); 0.8462: 120 (20%) | 0.0833: 120 (20%); 0.2372: 239 (40%); 0.5513: 356 (60%); 0.8462: 476 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0034, 0.0402, 0.0724, 0.2309 | 0.0034: 473 (80%); 0.0402: 357 (60%); 0.0724: 237 (40%); 0.2309: 121 (20%) | 0.0034: 119 (20%); 0.0402: 238 (40%); 0.0724: 355 (60%); 0.2309: 483 (82%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5, 0.7987, 0.9487, 0.9744 | 0.5: 475 (80%); 0.7987: 359 (61%); 0.9487: 239 (40%); 0.9744: 128 (22%) | 0.5: 120 (20%); 0.7987: 238 (40%); 0.9487: 373 (63%); 0.9744: 496 (84%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0784, 0.2743, 0.5385, 0.7188 | 0.0784: 479 (81%); 0.2743: 357 (60%); 0.5385: 238 (40%); 0.7188: 120 (20%) | 0.0784: 127 (21%); 0.2743: 239 (40%); 0.5385: 357 (60%); 0.7188: 475 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0003, 0.0874, 0.2381 | -0.0812: 516 (87%); -0.0003: 356 (60%); 0.0874: 241 (41%); 0.2381: 127 (21%) | -0.0812: 131 (22%); -0.0003: 251 (42%); 0.0874: 362 (61%); 0.2381: 487 (82%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1544, -0.013, 0.0387, 0.0968 | -0.1544: 474 (80%); -0.013: 356 (60%); 0.0387: 239 (40%); 0.0968: 122 (21%) | -0.1544: 120 (20%); -0.013: 240 (41%); 0.0387: 357 (60%); 0.0968: 476 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3333, 0.5513, 0.7308, 0.8782 | 0.3333: 475 (80%); 0.5513: 358 (60%); 0.7308: 240 (41%); 0.8782: 136 (23%) | 0.3333: 122 (21%); 0.5513: 245 (41%); 0.7308: 357 (60%); 0.8782: 475 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1859, 0.3782, 0.5641, 0.8141 | 0.1859: 479 (81%); 0.3782: 360 (61%); 0.5641: 241 (41%); 0.8141: 129 (22%) | 0.1859: 137 (23%); 0.3782: 257 (43%); 0.5641: 360 (61%); 0.8141: 475 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0583, 0.1573, 0.2827, 0.5975 | 0.0583: 475 (80%); 0.1573: 355 (60%); 0.2827: 237 (40%); 0.5975: 120 (20%) | 0.0583: 120 (20%); 0.1573: 237 (40%); 0.2827: 355 (60%); 0.5975: 474 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.3% | 26, 57.4, 82.6, 132.8 | 26: 467 (79%); 57.4: 349 (59%); 82.6: 233 (39%); 132.8: 117 (20%) | 26: 121 (20%); 57.4: 233 (39%); 82.6: 349 (59%); 132.8: 465 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.8% | 1.7158, 2.247, 2.7557, 3.6765 | 1.7158: 473 (80%); 2.247: 355 (60%); 2.7557: 237 (40%); 3.6765: 119 (20%) | 1.7158: 119 (20%); 2.247: 237 (40%); 2.7557: 355 (60%); 3.6765: 473 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 7, 14, 27, 37 | 7: 485 (82%); 14: 371 (63%); 27: 246 (42%); 37: 135 (23%) | 7: 127 (21%); 14: 245 (41%); 27: 359 (61%); 37: 481 (81%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 0, 1, 3, 4 | 0: 592 (100%); 1: 456 (77%); 3: 253 (43%); 4: 142 (24%) | 0: 136 (23%); 1: 238 (40%); 3: 450 (76%); 4: 592 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0156, -0.0042, 0.0109, 0.0219 | -0.0156: 473 (80%); -0.0042: 357 (60%); 0.0109: 237 (40%); 0.0219: 127 (21%) | -0.0156: 119 (20%); -0.0042: 238 (40%); 0.0109: 361 (61%); 0.0219: 475 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5526, 25.6303, 26.4793, 27.2532 | 24.5526: 475 (80%); 25.6303: 361 (61%); 26.4793: 237 (40%); 27.2532: 119 (20%) | 24.5526: 136 (23%); 25.6303: 238 (40%); 26.4793: 355 (60%); 27.2532: 473 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -2.1996, -0.8398, -0.1232, 1.133 | -2.1996: 473 (80%); -0.8398: 355 (60%); -0.1232: 237 (40%); 1.133: 119 (20%) | -2.1996: 119 (20%); -0.8398: 237 (40%); -0.1232: 355 (60%); 1.133: 473 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -1.133, 0.1232, 0.8398, 2.1996 | -1.133: 473 (80%); 0.1232: 355 (60%); 0.8398: 237 (40%); 2.1996: 119 (20%) | -1.133: 119 (20%); 0.1232: 237 (40%); 0.8398: 355 (60%); 2.1996: 473 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0526, -0.0118, 0.0204, 0.0644 | -0.0526: 473 (80%); -0.0118: 356 (60%); 0.0204: 237 (40%); 0.0644: 119 (20%) | -0.0526: 119 (20%); -0.0118: 237 (40%); 0.0204: 356 (60%); 0.0644: 473 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.9895, 8.4895, 8.8227, 9.1359 | 7.9895: 473 (80%); 8.4895: 355 (60%); 8.8227: 237 (40%); 9.1359: 119 (20%) | 7.9895: 119 (20%); 8.4895: 237 (40%); 8.8227: 355 (60%); 9.1359: 473 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.8% | 0, 1 | 0: 591 (100%); 1: 196 (33%) | 0: 395 (67%); 1: 534 (90%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.8% | 0 | 0: 485 (82%) | 0: 494 (83%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.8% | 0, 1 | 0: 591 (100%); 1: 197 (33%) | 0: 394 (67%); 1: 528 (89%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 3, 6, 156, 269.8 | 3: 474 (80%); 6: 377 (64%); 156: 238 (40%); 269.8: 119 (20%) | 3: 148 (25%); 6: 245 (41%); 156: 356 (60%); 269.8: 473 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 4, 86.6, 138.6 | 1: 488 (82%); 4: 371 (63%); 86.6: 237 (40%); 138.6: 119 (20%) | 1: 155 (26%); 4: 240 (41%); 86.6: 355 (60%); 138.6: 473 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.6397, 0.1627, 0.5607, 1.6157 | -0.6397: 473 (80%); 0.1627: 355 (60%); 0.5607: 237 (40%); 1.6157: 119 (20%) | -0.6397: 119 (20%); 0.1627: 237 (40%); 0.5607: 355 (60%); 1.6157: 473 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -1.6355, -0.3735, 0.2298, 1.3599 | -1.6355: 473 (80%); -0.3735: 355 (60%); 0.2298: 237 (40%); 1.3599: 119 (20%) | -1.6355: 119 (20%); -0.3735: 237 (40%); 0.2298: 355 (60%); 1.3599: 473 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.9672, -0.4993, 0.1384, 1.0581 | -1.9672: 473 (80%); -0.4993: 355 (60%); 0.1384: 237 (40%); 1.0581: 119 (20%) | -1.9672: 119 (20%); -0.4993: 237 (40%); 0.1384: 355 (60%); 1.0581: 473 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.5607, 0.1658, 0.5029, 1.376 | -0.5607: 473 (80%); 0.1658: 355 (60%); 0.5029: 237 (40%); 1.376: 119 (20%) | -0.5607: 119 (20%); 0.1658: 237 (40%); 0.5029: 355 (60%); 1.376: 473 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -1.4579, -0.383, 0.5124, 2.1628 | -1.4579: 473 (80%); -0.383: 355 (60%); 0.5124: 237 (40%); 2.1628: 119 (20%) | -1.4579: 119 (20%); -0.383: 237 (40%); 0.5124: 355 (60%); 2.1628: 473 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -1.825, -0.3759, 0.2309, 1.4753 | -1.825: 473 (80%); -0.3759: 355 (60%); 0.2309: 237 (40%); 1.4753: 119 (20%) | -1.825: 119 (20%); -0.3759: 237 (40%); 0.2309: 355 (60%); 1.4753: 473 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 35.43, 50.54, 62.462, 72.228 | 35.43: 473 (80%); 50.54: 356 (60%); 62.462: 237 (40%); 72.228: 119 (20%) | 35.43: 119 (20%); 50.54: 238 (40%); 62.462: 355 (60%); 72.228: 473 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 99.2% | -0.1612, -0.0748, -0.0116, 0.0958 | -0.1612: 469 (79%); -0.0748: 352 (59%); -0.0116: 235 (40%); 0.0958: 118 (20%) | -0.1612: 118 (20%); -0.0748: 235 (40%); -0.0116: 352 (59%); 0.0958: 469 (79%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.7% | 0.0075, 0.0174, 0.0315, 0.058 | 0.0075: 471 (80%); 0.0174: 354 (60%); 0.0315: 235 (40%); 0.058: 118 (20%) | 0.0075: 119 (20%); 0.0174: 236 (40%); 0.0315: 355 (60%); 0.058: 472 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 1, 2, 5, 10 | 1: 477 (81%); 2: 389 (66%); 5: 250 (42%); 10: 123 (21%) | 1: 203 (34%); 2: 265 (45%); 5: 382 (65%); 10: 482 (81%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1799 | 0: 592 (100%); 0.1799: 119 (20%) | 0: 371 (63%); 0.1799: 473 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2222, 0.4506, 0.6667 | 0: 592 (100%); 0.2222: 356 (60%); 0.4506: 237 (40%); 0.6667: 124 (21%) | 0: 205 (35%); 0.2222: 238 (40%); 0.4506: 355 (60%); 0.6667: 492 (83%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 3.6, 7 | 0: 592 (100%); 1: 448 (76%); 3.6: 237 (40%); 7: 136 (23%) | 0: 144 (24%); 1: 247 (42%); 3.6: 355 (60%); 7: 483 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 1, 2, 5, 10 | 1: 477 (81%); 2: 389 (66%); 5: 250 (42%); 10: 123 (21%) | 1: 203 (34%); 2: 265 (45%); 5: 382 (65%); 10: 482 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 592 (100%); 1: 423 (71%); 3: 273 (46%); 7: 131 (22%) | 0: 169 (29%); 1: 258 (44%); 3: 369 (62%); 7: 476 (80%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.212, 0.3523, 0.5231 | 0: 543 (92%); 0.212: 355 (60%); 0.3523: 237 (40%); 0.5231: 119 (20%) | 0: 130 (22%); 0.212: 237 (40%); 0.3523: 355 (60%); 0.5231: 473 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2338, 0.5755 | 0: 528 (89%); 0.2338: 237 (40%); 0.5755: 119 (20%) | 0: 298 (50%); 0.2338: 355 (60%); 0.5755: 473 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3333, 0.5686 | 0: 539 (91%); 0.3333: 239 (40%); 0.5686: 119 (20%) | 0: 238 (40%); 0.3333: 376 (64%); 0.5686: 473 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.5686 | 0: 539 (91%); 0.3333: 239 (40%); 0.5686: 119 (20%) | 0: 238 (40%); 0.3333: 376 (64%); 0.5686: 473 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.18, 0, 0.1988 | -0.18: 473 (80%); 0: 414 (70%); 0.1988: 119 (20%) | -0.18: 119 (20%); 0: 410 (69%); 0.1988: 473 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.583, 0, 0.4273, 1.8371 | -0.583: 473 (80%); 0: 369 (62%); 0.4273: 237 (40%); 1.8371: 119 (20%) | -0.583: 119 (20%); 0: 303 (51%); 0.4273: 355 (60%); 1.8371: 473 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 6, 10 | 2: 489 (83%); 4: 380 (64%); 6: 280 (47%); 10: 140 (24%) | 2: 161 (27%); 4: 263 (44%); 6: 364 (61%); 10: 483 (82%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.069, 0.0167, 0.0695, 0.1116 | -0.069: 473 (80%); 0.0167: 355 (60%); 0.0695: 237 (40%); 0.1116: 119 (20%) | -0.069: 119 (20%); 0.0167: 237 (40%); 0.0695: 355 (60%); 0.1116: 473 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0773, -0.0126, 0.0478, 0.1082 | -0.0773: 473 (80%); -0.0126: 355 (60%); 0.0478: 237 (40%); 0.1082: 119 (20%) | -0.0773: 119 (20%); -0.0126: 237 (40%); 0.0478: 355 (60%); 0.1082: 473 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0579, 0.0271, 0.0564, 0.0873 | -0.0579: 473 (80%); 0.0271: 355 (60%); 0.0564: 237 (40%); 0.0873: 119 (20%) | -0.0579: 119 (20%); 0.0271: 237 (40%); 0.0564: 355 (60%); 0.0873: 473 (80%) | OFFLINE |
| pct_from_avwap_252low | (not found by literal grep) | 99.3% | 0.7834, 4.671, 7.6176, 10.9458 | 0.7834: 470 (79%); 4.671: 353 (60%); 7.6176: 235 (40%); 10.9458: 118 (20%) | 0.7834: 118 (20%); 4.671: 235 (40%); 7.6176: 353 (60%); 10.9458: 470 (79%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -21.8246, -9.0994, 0.072, 14.6814 | -21.8246: 473 (80%); -9.0994: 355 (60%); 0.072: 237 (40%); 14.6814: 119 (20%) | -21.8246: 119 (20%); -9.0994: 237 (40%); 0.072: 355 (60%); 14.6814: 473 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.055, 0.0727, 0.0905, 0.1204 | 0.055: 474 (80%); 0.0727: 355 (60%); 0.0905: 237 (40%); 0.1204: 119 (20%) | 0.055: 119 (20%); 0.0727: 237 (40%); 0.0905: 356 (60%); 0.1204: 474 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.2093, 0.356, 0.5115, 0.6945 | 0.2093: 473 (80%); 0.356: 355 (60%); 0.5115: 238 (40%); 0.6945: 119 (20%) | 0.2093: 119 (20%); 0.356: 237 (40%); 0.5115: 356 (60%); 0.6945: 473 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.7047, -0.5031, 0.4024, 1.7669 | -1.7047: 473 (80%); -0.5031: 355 (60%); 0.4024: 237 (40%); 1.7669: 119 (20%) | -1.7047: 119 (20%); -0.5031: 237 (40%); 0.4024: 355 (60%); 1.7669: 473 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.9846, 0.2976, 0.8962, 1.3882 | -0.9846: 473 (80%); 0.2976: 355 (60%); 0.8962: 237 (40%); 1.3882: 119 (20%) | -0.9846: 119 (20%); 0.2976: 237 (40%); 0.8962: 355 (60%); 1.3882: 473 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.885, -0.8765, 0.252, 1.2951 | -1.885: 473 (80%); -0.8765: 355 (60%); 0.252: 237 (40%); 1.2951: 119 (20%) | -1.885: 119 (20%); -0.8765: 237 (40%); 0.252: 355 (60%); 1.2951: 473 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -6.9366, 1.1172, 6.834, 11.5082 | -6.9366: 473 (80%); 1.1172: 355 (60%); 6.834: 237 (40%); 11.5082: 119 (20%) | -6.9366: 119 (20%); 1.1172: 237 (40%); 6.834: 355 (60%); 11.5082: 473 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 36.936, 49.812, 59.846, 65.88 | 36.936: 473 (80%); 49.812: 355 (60%); 59.846: 237 (40%); 65.88: 119 (20%) | 36.936: 119 (20%); 49.812: 237 (40%); 59.846: 355 (60%); 65.88: 473 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 3.256, 66.262, 96.302, 98.018 | 3.256: 473 (80%); 66.262: 355 (60%); 96.302: 237 (40%); 98.018: 119 (20%) | 3.256: 119 (20%); 66.262: 237 (40%); 96.302: 355 (60%); 98.018: 473 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 42.304, 48.202, 54.386, 59.542 | 42.304: 473 (80%); 48.202: 355 (60%); 54.386: 237 (40%); 59.542: 119 (20%) | 42.304: 119 (20%); 48.202: 237 (40%); 54.386: 355 (60%); 59.542: 473 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 29.682, 55.344, 67.472, 73.048 | 29.682: 473 (80%); 55.344: 355 (60%); 67.472: 237 (40%); 73.048: 119 (20%) | 29.682: 119 (20%); 55.344: 237 (40%); 67.472: 355 (60%); 73.048: 473 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0343, 0.0476, 0.0606, 0.0882 | 0.0343: 473 (80%); 0.0476: 355 (60%); 0.0606: 237 (40%); 0.0882: 127 (21%) | 0.0343: 119 (20%); 0.0476: 237 (40%); 0.0606: 355 (60%); 0.0882: 475 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0887, -0.059, -0.0435, -0.0343 | -0.0887: 475 (80%); -0.059: 359 (61%); -0.0435: 237 (40%); -0.0343: 119 (20%) | -0.0887: 120 (20%); -0.059: 240 (41%); -0.0435: 356 (60%); -0.0343: 473 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 592 (100%); 1: 143 (24%) | 0: 449 (76%); 1: 500 (84%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.8% | 25, 40, 56, 68 | 25: 474 (80%); 40: 355 (60%); 56: 238 (40%); 68: 130 (22%) | 25: 125 (21%); 40: 238 (40%); 56: 366 (62%); 68: 479 (81%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.2599, 0.4284, 0.5965, 0.8226 | 0.2599: 473 (80%); 0.4284: 355 (60%); 0.5965: 237 (40%); 0.8226: 119 (20%) | 0.2599: 119 (20%); 0.4284: 237 (40%); 0.5965: 355 (60%); 0.8226: 473 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 31.84, 51.02, 73.42, 109.18 | 31.84: 473 (80%); 51.02: 355 (60%); 73.42: 237 (40%); 109.18: 119 (20%) | 31.84: 119 (20%); 51.02: 237 (40%); 73.42: 355 (60%); 109.18: 473 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -3.5925, 0.33, 2.575, 8.323 | -3.5925: 473 (80%); 0.33: 355 (60%); 2.575: 237 (40%); 8.323: 119 (20%) | -3.5925: 119 (20%); 0.33: 237 (40%); 2.575: 355 (60%); 8.323: 473 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 18.72, 50.552, 78.652, 90.76 | 18.72: 473 (80%); 50.552: 355 (60%); 78.652: 237 (40%); 90.76: 119 (20%) | 18.72: 119 (20%); 50.552: 237 (40%); 78.652: 355 (60%); 90.76: 473 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 12.35, 55.572, 85.166, 92.662 | 12.35: 473 (80%); 55.572: 355 (60%); 85.166: 237 (40%); 92.662: 119 (20%) | 12.35: 119 (20%); 55.572: 237 (40%); 85.166: 355 (60%); 92.662: 473 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 8.834, 58.896, 90.34, 98.494 | 8.834: 473 (80%); 58.896: 355 (60%); 90.34: 237 (40%); 98.494: 119 (20%) | 8.834: 119 (20%); 58.896: 237 (40%); 90.34: 355 (60%); 98.494: 473 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 4.91, 67.866, 96.194, 100 | 4.91: 473 (80%); 67.866: 355 (60%); 96.194: 237 (40%); 100: 199 (34%) | 4.91: 119 (20%); 67.866: 237 (40%); 96.194: 355 (60%); 100: 592 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 8, 12, 17 | 4: 489 (83%); 8: 362 (61%); 12: 260 (44%); 17: 132 (22%) | 4: 130 (22%); 8: 257 (43%); 12: 360 (61%); 17: 485 (82%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 14, 18 | 5: 480 (81%); 10: 362 (61%); 14: 258 (44%); 18: 134 (23%) | 5: 134 (23%); 10: 276 (47%); 14: 363 (61%); 18: 491 (83%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.2032, 0.4683, 0.6333, 0.8357 | 0.2032: 473 (80%); 0.4683: 358 (60%); 0.6333: 237 (40%); 0.8357: 119 (20%) | 0.2032: 119 (20%); 0.4683: 239 (40%); 0.6333: 355 (60%); 0.8357: 473 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.222, 18.014, 21.282, 24.93 | 15.222: 473 (80%); 18.014: 355 (60%); 21.282: 237 (40%); 24.93: 121 (20%) | 15.222: 119 (20%); 18.014: 237 (40%); 21.282: 355 (60%); 24.93: 474 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 15.222, 18.014, 21.282, 24.93 | 15.222: 473 (80%); 18.014: 355 (60%); 21.282: 237 (40%); 24.93: 121 (20%) | 15.222: 119 (20%); 18.014: 237 (40%); 21.282: 355 (60%); 24.93: 474 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8622, 0.8892, 0.9246, 0.9661 | 0.8622: 473 (80%); 0.8892: 355 (60%); 0.9246: 237 (40%); 0.9661: 120 (20%) | 0.8622: 119 (20%); 0.8892: 237 (40%); 0.9246: 355 (60%); 0.9661: 474 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.74, 0.92, 1.12, 1.57 | 0.74: 481 (81%); 0.92: 361 (61%); 1.12: 239 (40%); 1.57: 120 (20%) | 0.74: 124 (21%); 0.92: 240 (41%); 1.12: 362 (61%); 1.57: 477 (81%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0296, 0.0549, 0.0861, 0.1297 | 0.0296: 474 (80%); 0.0549: 355 (60%); 0.0861: 238 (40%); 0.1297: 119 (20%) | 0.0296: 119 (20%); 0.0549: 237 (40%); 0.0861: 357 (60%); 0.1297: 473 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 41.8581, 74.4029, 116.7694, 210.3283 | 41.8581: 473 (80%); 74.4029: 355 (60%); 116.7694: 237 (40%); 210.3283: 119 (20%) | 41.8581: 119 (20%); 74.4029: 237 (40%); 116.7694: 355 (60%); 210.3283: 473 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 40.2595, 70.7655, 113.2606, 202.1391 | 40.2595: 473 (80%); 70.7655: 355 (60%); 113.2606: 237 (40%); 202.1391: 119 (20%) | 40.2595: 119 (20%); 70.7655: 237 (40%); 113.2606: 355 (60%); 202.1391: 473 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 38.4163, 66.4332, 109.8802, 193.4907 | 38.4163: 473 (80%); 66.4332: 355 (60%); 109.8802: 237 (40%); 193.4907: 119 (20%) | 38.4163: 119 (20%); 66.4332: 237 (40%); 109.8802: 355 (60%); 193.4907: 473 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 44.2634, 77.4022, 119.893, 217.0214 | 44.2634: 473 (80%); 77.4022: 355 (60%); 119.893: 237 (40%); 217.0214: 119 (20%) | 44.2634: 119 (20%); 77.4022: 237 (40%); 119.893: 355 (60%); 217.0214: 473 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 45.3782, 80.0201, 125.7803, 224.7246 | 45.3782: 473 (80%); 80.0201: 355 (60%); 125.7803: 237 (40%); 224.7246: 119 (20%) | 45.3782: 119 (20%); 80.0201: 237 (40%); 125.7803: 355 (60%); 224.7246: 473 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 592 (100%) | 0: 521 (88%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 592 (100%) | 0: 519 (88%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0695, -0.006, 0.0588, 0.1129 | -0.0695: 473 (80%); -0.006: 355 (60%); 0.0588: 237 (40%); 0.1129: 119 (20%) | -0.0695: 119 (20%); -0.006: 237 (40%); 0.0588: 355 (60%); 0.1129: 473 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -83.946, -32.456, -15.06, -10.414 | -83.946: 473 (80%); -32.456: 355 (60%); -15.06: 238 (40%); -10.414: 119 (20%) | -83.946: 119 (20%); -32.456: 237 (40%); -15.06: 356 (60%); -10.414: 473 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.5% | 0.6495, 0.9291, 1.1298, 1.4493 | 0.6495: 471 (80%); 0.9291: 353 (60%); 1.1298: 236 (40%); 1.4493: 118 (20%) | 0.6495: 119 (20%); 0.9291: 236 (40%); 1.1298: 353 (60%); 1.4493: 471 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.5% | 4, 6, 8, 9 | 4: 481 (81%); 6: 383 (65%); 8: 260 (44%); 9: 196 (33%) | 4: 157 (27%); 6: 269 (45%); 8: 393 (66%); 9: 477 (81%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.5% | 0.2092, 0.2493, 0.3092, 0.3977 | 0.2092: 473 (80%); 0.2493: 353 (60%); 0.3092: 236 (40%); 0.3977: 118 (20%) | 0.2092: 119 (20%); 0.2493: 236 (40%); 0.3092: 353 (60%); 0.3977: 471 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.5% | 4, 6, 8, 10 | 4: 490 (83%); 6: 390 (66%); 8: 282 (48%); 10: 128 (22%) | 4: 140 (24%); 6: 250 (42%); 8: 378 (64%); 10: 589 (99%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.7% | 0.0265, 0.0359, 0.0494, 0.0687 | 0.0265: 472 (80%); 0.0359: 354 (60%); 0.0494: 237 (40%); 0.0687: 119 (20%) | 0.0265: 122 (21%); 0.0359: 237 (40%); 0.0494: 356 (60%); 0.0687: 473 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.7% | 4, 6, 8, 9.2 | 4: 486 (82%); 6: 393 (66%); 8: 278 (47%); 9.2: 118 (20%) | 4: 146 (25%); 6: 247 (42%); 8: 382 (65%); 9.2: 472 (80%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.5% | -0.2941, -0.1282, 0.0046, 0.1921 | -0.2941: 471 (80%); -0.1282: 353 (60%); 0.0046: 237 (40%); 0.1921: 118 (20%) | -0.2941: 118 (20%); -0.1282: 236 (40%); 0.0046: 354 (60%); 0.1921: 471 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.5% | 2, 3, 5, 8 | 2: 478 (81%); 3: 414 (70%); 5: 274 (46%); 8: 136 (23%) | 2: 175 (30%); 3: 248 (42%); 5: 370 (62%); 8: 500 (84%) | OFFLINE |
| year_high | backtest/signals/screener.py +1 | 100.0% | 51.99, 91.915, 156.2076, 274.7 | 51.99: 474 (80%); 91.915: 355 (60%); 156.2076: 237 (40%); 274.7: 120 (20%) | 51.99: 120 (20%); 91.915: 237 (40%); 156.2076: 355 (60%); 274.7: 474 (80%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 9.8% |
| 8k_item_5_02_filed_within_7d | 3.0% |
| above_avwap_20high | 24.5% |
| above_avwap_20low | 87.7% |
| above_avwap_252low | 84.2% |
| above_avwap_50low | 78.7% |
| above_cam_r3 | 31.4% |
| above_cam_r4 | 20.8% |
| above_cpr | 63.2% |
| above_pivot | 63.2% |
| above_prev_high | 33.1% |
| above_prev_high_clearance_atr_05 | 12.8% |
| above_prev_low | 82.3% |
| above_r1 | 23.8% |
| above_r2 | 13.7% |
| above_vwap | 40.7% |
| above_wood_p | 63.5% |
| ad_rising | 61.5% |
| adx_cross_up | 5.1% |
| adx_cross_up_20 | 4.6% |
| adx_di_bear | 40.9% |
| adx_di_bull | 59.1% |
| adx_strong | 2.7% |
| adx_trending | 43.8% |
| ao_cross_dn | 3.7% |
| ao_cross_up | 7.4% |
| ao_positive | 50.7% |
| ao_twin_peaks_bull | 1.4% |
| at_key_fib | 14.4% |
| at_key_fib_wide | 36.3% |
| avwap_20high_loss_recent_3d | 10.2% |
| avwap_20high_reclaim_recent_3d | 17.4% |
| avwap_20low_loss_recent_3d | 5.7% |
| avwap_20low_reclaim_recent_3d | 9.4% |
| avwap_252low_loss_recent_3d | 2.2% |
| avwap_252low_reclaim_recent_3d | 8.7% |
| avwap_50low_loss_recent_3d | 11.8% |
| avwap_50low_reclaim_recent_3d | 8.0% |
| bb_10_20_above_mid | 65.2% |
| bb_10_20_expanding | 81.1% |
| bb_10_20_pctb_gt_75 | 61.0% |
| bb_10_20_pctb_gt_8 | 55.2% |
| bb_10_20_pctb_gt_85 | 44.4% |
| bb_10_20_pctb_gt_9 | 29.1% |
| bb_10_20_pctb_gt_95 | 17.1% |
| bb_10_20_pctb_lt_05 | 7.9% |
| bb_10_20_pctb_lt_1 | 15.9% |
| bb_10_20_pctb_lt_15 | 24.7% |
| bb_10_20_pctb_lt_2 | 29.4% |
| bb_10_20_pctb_lt_25 | 32.8% |
| bb_10_20_reclaim_from_lower_recent_3d | 13.0% |
| bb_10_20_reclaim_from_upper_recent_3d | 19.9% |
| bb_10_20_squeeze | 16.4% |
| bb_10_20_touch_lower | 7.4% |
| bb_10_20_touch_upper | 17.7% |
| bb_20_15_above_mid | 63.0% |
| bb_20_15_expanding | 73.6% |
| bb_20_15_pctb_gt_75 | 55.6% |
| bb_20_15_pctb_gt_8 | 54.6% |
| bb_20_15_pctb_gt_85 | 52.5% |
| bb_20_15_pctb_gt_9 | 50.5% |
| bb_20_15_pctb_gt_95 | 48.3% |
| bb_20_15_pctb_lt_05 | 27.2% |
| bb_20_15_pctb_lt_1 | 29.6% |
| bb_20_15_pctb_lt_15 | 30.6% |
| bb_20_15_pctb_lt_2 | 31.8% |
| bb_20_15_pctb_lt_25 | 32.3% |
| bb_20_15_reclaim_from_lower_recent_3d | 2.4% |
| bb_20_15_reclaim_from_upper_recent_3d | 3.2% |
| bb_20_15_squeeze | 22.8% |
| bb_20_15_touch_lower | 27.0% |
| bb_20_15_touch_upper | 47.8% |
| bb_20_20_above_mid | 63.0% |
| bb_20_20_expanding | 73.6% |
| bb_20_20_pctb_gt_75 | 53.7% |
| bb_20_20_pctb_gt_8 | 50.5% |
| bb_20_20_pctb_gt_85 | 47.1% |
| bb_20_20_pctb_gt_9 | 40.0% |
| bb_20_20_pctb_gt_95 | 32.6% |
| bb_20_20_pctb_lt_05 | 18.9% |
| bb_20_20_pctb_lt_1 | 23.0% |
| bb_20_20_pctb_lt_15 | 26.5% |
| bb_20_20_pctb_lt_2 | 29.6% |
| bb_20_20_pctb_lt_25 | 31.1% |
| bb_20_20_reclaim_from_lower_recent_3d | 6.4% |
| bb_20_20_reclaim_from_upper_recent_3d | 11.7% |
| bb_20_20_squeeze | 9.5% |
| bb_20_20_touch_lower | 17.4% |
| bb_20_20_touch_upper | 30.6% |
| bearish_engulfing | 0.8% |
| bearish_pin_bar | 12.3% |
| below_avwap_20high | 75.5% |
| below_avwap_20low | 12.3% |
| below_avwap_252low | 15.8% |
| below_avwap_50low | 21.3% |
| below_cam_s3 | 18.1% |
| below_cam_s4 | 8.8% |
| below_cpr | 36.8% |
| below_ema_20 | 37.0% |
| below_ema_200 | 66.2% |
| below_ema_200_break_recent_5d | 13.7% |
| below_ema_20_break_recent_5d | 17.1% |
| below_ema_21 | 37.5% |
| below_ema_21_break_recent_5d | 17.2% |
| below_ema_50 | 47.1% |
| below_ema_50_break_recent_5d | 19.9% |
| below_ema_9 | 35.0% |
| below_ema_9_break_recent_5d | 15.4% |
| below_prev_high | 66.4% |
| below_prev_low | 17.2% |
| below_prev_low_clearance_atr_05 | 5.1% |
| below_s1 | 10.6% |
| below_s2 | 4.4% |
| below_sma_20 | 37.0% |
| below_sma_200 | 65.2% |
| below_sma_21 | 37.7% |
| below_sma_50 | 46.8% |
| below_sma_9 | 34.8% |
| below_vwap | 59.3% |
| blowoff_recent_3d | 0.7% |
| bullish_engulfing | 0.3% |
| bullish_pin_bar | 10.3% |
| capitulation_recent_3d | 0.3% |
| ceo_buy | 0.9% |
| cfo_buy | 0.3% |
| chandelier_long_bullish | 62.8% |
| chandelier_long_flip_dn | 2.0% |
| chandelier_short_bearish | 43.6% |
| chandelier_short_flip_up | 6.1% |
| close_above_open | 34.8% |
| close_below_open | 65.2% |
| close_in_bottom_40pct_of_range | 45.9% |
| close_in_top_40pct_of_range | 29.4% |
| cluster_buy | 0.2% |
| cmf_cross_dn | 4.6% |
| cmf_cross_up | 2.7% |
| cmf_negative | 41.0% |
| cmf_positive | 58.8% |
| concentrated_sell | 4.8% |
| cpr_narrow | 83.8% |
| cpr_narrow_tight | 21.5% |
| cup_handle_detected | 6.9% |
| cup_handle_neckline_break_retest_long | 1.9% |
| dc10_breakout_dn | 16.6% |
| dc10_breakout_dn_1pct | 25.7% |
| dc10_breakout_up | 31.6% |
| dc10_breakout_up_1pct | 48.0% |
| dc10_new_high | 53.0% |
| dc10_strong_breakout_dn | 4.2% |
| dc10_strong_breakout_up | 10.6% |
| dc20_breakout_dn | 12.0% |
| dc20_breakout_up | 23.1% |
| dc20_new_high | 40.7% |
| dc20_resistance_break_retest_strong | 20.3% |
| dc20_support_break_retest_strong | 10.6% |
| defensive_leadership | 50.8% |
| director_only_buy | 2.4% |
| doji | 11.7% |
| double_bottom_detected | 11.3% |
| double_top_detected | 12.7% |
| dpi_elevated | 56.8% |
| drying_volume_on_down_turn | 34.8% |
| drying_volume_on_up_turn | 14.9% |
| ema_20_50_bearish | 58.1% |
| ema_20_50_bullish | 41.9% |
| ema_20_50_death_cross | 2.0% |
| ema_20_50_golden_cross | 2.9% |
| ema_50_200_bearish | 64.5% |
| ema_50_200_bullish | 35.5% |
| ema_50_200_death_cross | 0.2% |
| ema_9_21_bearish | 47.1% |
| ema_9_21_bullish | 52.9% |
| ema_9_21_death_cross | 2.9% |
| ema_9_21_golden_cross | 6.9% |
| evening_star | 0.7% |
| flag_bear_break_retest_short | 0.3% |
| flag_bear_broke | 0.8% |
| flag_bear_detected | 0.2% |
| flag_bull_break_retest_long | 0.7% |
| flag_bull_broke | 1.0% |
| force_index_cross_dn | 1.0% |
| force_index_cross_up | 4.2% |
| force_index_positive | 63.0% |
| gap_dn_1_5pct | 15.7% |
| gap_dn_2pct | 11.7% |
| gap_up_1_5pct | 27.2% |
| gap_up_2pct | 21.3% |
| hammer | 6.2% |
| head_shoulders_bottom_detected | 4.1% |
| head_shoulders_top_detected | 4.4% |
| house_cluster_buy | 4.6% |
| house_cluster_sell | 3.2% |
| htf_aligned_bear | 15.0% |
| htf_aligned_bull | 3.9% |
| htf_disagreement | 11.7% |
| hull_bearish | 35.0% |
| hull_bullish | 65.0% |
| hull_flip_dn | 1.5% |
| hull_flip_up | 3.2% |
| ichi_above_cloud | 35.6% |
| ichi_above_cloud_break_recent_5d | 17.1% |
| ichi_below_cloud | 41.6% |
| ichi_below_cloud_break_recent_5d | 10.8% |
| ichi_cloud_thick | 87.5% |
| ichi_tk_bearish | 45.1% |
| ichi_tk_bullish | 43.9% |
| ichi_tk_cross_dn | 2.7% |
| ichi_tk_cross_up | 4.9% |
| ichi_weekly_above_cloud | 25.0% |
| ichi_weekly_below_cloud | 41.1% |
| ichi_weekly_in_cloud | 33.9% |
| in_reversal_window | 2.3% |
| inside_bar | 9.3% |
| inside_cpr | 1.4% |
| inside_kc | 63.7% |
| insider_cluster_active | 20.0% |
| institutional_buy | 90.7% |
| institutional_negative | 3.7% |
| institutional_persistence_growing | 46.8% |
| institutional_persistence_strong | 61.3% |
| institutional_strong_buy | 80.2% |
| inverted_cup_handle_detected | 5.7% |
| is_friday | 24.0% |
| is_halloween_period | 52.5% |
| is_halloween_period_first_day | 0.8% |
| is_january | 9.3% |
| is_january_extended | 11.0% |
| is_monday | 23.0% |
| is_pre_holiday | 2.5% |
| is_summer_period | 47.5% |
| is_totm_window | 36.3% |
| is_totm_window_first_day | 11.0% |
| is_week_open | 24.7% |
| kc_touch_lower | 18.6% |
| kc_touch_upper | 26.0% |
| large_dollar_buy | 1.2% |
| macd_12_26_9_bearish | 34.1% |
| macd_12_26_9_bullish | 65.9% |
| macd_12_26_9_crossover_dn | 0.5% |
| macd_12_26_9_crossover_up | 3.0% |
| macd_8_21_5_bearish | 34.8% |
| macd_8_21_5_bullish | 65.2% |
| macd_8_21_5_crossover_dn | 1.4% |
| macd_8_21_5_crossover_up | 0.8% |
| mfi_broad_overbought | 24.0% |
| mfi_broad_oversold | 14.0% |
| mfi_overbought | 7.8% |
| mfi_oversold | 3.7% |
| monthly_above_sma_12 | 34.9% |
| monthly_above_sma_6 | 43.1% |
| monthly_bias_bear | 38.0% |
| monthly_bias_bull | 16.0% |
| monthly_momentum_pos | 36.8% |
| near_52w_high_retest_long | 0.7% |
| near_52w_low_retest_short | 1.7% |
| near_avwap_20high_atr_05x | 19.5% |
| near_avwap_20high_atr_10x | 34.3% |
| near_avwap_20high_atr_15x | 54.1% |
| near_avwap_20high_atr_20x | 70.3% |
| near_avwap_20low_atr_05x | 11.2% |
| near_avwap_20low_atr_10x | 18.2% |
| near_avwap_20low_atr_15x | 34.4% |
| near_avwap_20low_atr_20x | 53.8% |
| near_avwap_252low_atr_05x | 11.7% |
| near_avwap_252low_atr_10x | 23.8% |
| near_avwap_252low_atr_15x | 36.7% |
| near_avwap_252low_atr_20x | 46.9% |
| near_avwap_50low_atr_05x | 9.3% |
| near_avwap_50low_atr_10x | 19.0% |
| near_avwap_50low_atr_15x | 33.2% |
| near_avwap_50low_atr_20x | 47.0% |
| near_cam_r3 | 16.6% |
| near_cam_s3 | 12.2% |
| near_cam_s4 | 4.1% |
| near_fib_236 | 4.2% |
| near_fib_382 | 3.9% |
| near_fib_500 | 5.6% |
| near_fib_618 | 4.9% |
| near_fib_786 | 3.4% |
| near_pivot | 12.2% |
| near_prev_close | 25.7% |
| near_prev_high | 13.5% |
| near_prev_low | 10.0% |
| near_r1 | 10.3% |
| near_r1_wide | 49.0% |
| near_r2 | 3.9% |
| near_r2_wide | 27.7% |
| near_s1 | 6.8% |
| near_s1_wide | 39.5% |
| near_s2 | 1.4% |
| near_s2_wide | 15.4% |
| near_s3 | 0.5% |
| near_wood_r1 | 9.3% |
| near_wood_s1 | 6.1% |
| news_uses_polygon_score | 24.5% |
| obv_bearish | 36.5% |
| obv_bullish | 63.5% |
| obv_diverge_bull | 0.5% |
| obv_falling | 35.5% |
| obv_rising | 64.5% |
| outside_bar | 2.2% |
| pead_negative_surprise | 17.6% |
| pead_positive_surprise | 22.3% |
| pin_bar | 22.6% |
| po3_accumulation_active | 14.5% |
| po3_bearish | 23.6% |
| po3_bullish | 10.8% |
| po3_manipulation_sweep_down | 4.1% |
| po3_manipulation_sweep_up | 8.6% |
| po3_mmbm_setup | 1.0% |
| po3_mmsm_setup | 1.4% |
| po3_sweep_above_prior_high | 60.5% |
| po3_sweep_below_prior_low | 35.0% |
| ppo_bullish | 65.4% |
| ppo_crossover_dn | 0.8% |
| ppo_crossover_up | 3.2% |
| pre_fomc_d0 | 2.0% |
| pre_fomc_d1 | 3.2% |
| pre_fomc_window | 5.2% |
| price_above_dema | 65.4% |
| price_above_ema_20 | 63.0% |
| price_above_ema_200 | 33.8% |
| price_above_ema_200_break_recent_5d | 13.3% |
| price_above_ema_20_break_recent_5d | 33.8% |
| price_above_ema_21 | 62.5% |
| price_above_ema_21_break_recent_5d | 34.0% |
| price_above_ema_50 | 52.9% |
| price_above_ema_50_break_recent_5d | 31.2% |
| price_above_ema_9 | 65.0% |
| price_above_ema_9_break_recent_5d | 29.7% |
| price_above_hull | 64.9% |
| price_above_sma_200 | 34.8% |
| price_above_sma_21 | 62.3% |
| price_above_sma_50 | 53.2% |
| price_above_tema | 64.9% |
| price_below_dema | 34.6% |
| price_below_hull | 35.1% |
| price_below_tema | 35.1% |
| psar_bullish | 63.5% |
| psar_flip_dn | 1.7% |
| psar_flip_up | 5.2% |
| r1_break_retest_long | 62.3% |
| recent_blowoff_at_r3 | 0.2% |
| resistance_break_retest | 29.7% |
| risk_off_regime_bond_signal | 22.6% |
| risk_off_regime_bond_signal_strong | 9.1% |
| risk_off_regime_gold_signal | 41.0% |
| risk_on_regime_bond_signal | 41.6% |
| risk_on_regime_bond_signal_strong | 17.6% |
| roc_positive | 62.7% |
| roc_turning_dn | 2.2% |
| roc_turning_up | 5.4% |
| rsi_14_bullish | 59.3% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.3% |
| rsi_14_cross_dn_overbought_recent_3d | 2.2% |
| rsi_14_cross_up_oversold_recent_3d | 2.2% |
| rsi_14_extreme_ob | 0.5% |
| rsi_14_extreme_os | 0.2% |
| rsi_14_overbought | 8.3% |
| rsi_14_oversold | 5.2% |
| rsi_14_rising | 58.3% |
| rsi_21_bullish | 55.6% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.2% |
| rsi_21_cross_dn_overbought_recent_3d | 0.2% |
| rsi_21_cross_up_oversold_recent_3d | 0.8% |
| rsi_21_extreme_ob | 0.2% |
| rsi_21_extreme_os | 0.2% |
| rsi_21_overbought | 1.2% |
| rsi_21_oversold | 0.3% |
| rsi_21_rising | 58.1% |
| rsi_2_bullish | 64.4% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 10.0% |
| rsi_2_cross_dn_overbought_recent_3d | 9.0% |
| rsi_2_cross_up_extreme_os_recent_3d | 6.9% |
| rsi_2_cross_up_oversold_recent_3d | 8.6% |
| rsi_2_extreme_ob | 56.8% |
| rsi_2_extreme_os | 29.6% |
| rsi_2_overbought | 58.6% |
| rsi_2_oversold | 30.7% |
| rsi_2_rising | 58.1% |
| rsi_9_bullish | 64.4% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 2.9% |
| rsi_9_cross_dn_overbought_recent_3d | 3.9% |
| rsi_9_cross_up_extreme_os_recent_3d | 2.2% |
| rsi_9_cross_up_oversold_recent_3d | 2.4% |
| rsi_9_extreme_ob | 5.7% |
| rsi_9_extreme_os | 2.4% |
| rsi_9_overbought | 31.4% |
| rsi_9_oversold | 20.9% |
| rsi_9_rising | 58.1% |
| s1_break_retest_short | 33.1% |
| sc_13d_filed_within_30d | 5.4% |
| sc_13g_filed_within_30d | 1.5% |
| sector_outperforming_spy | 64.3% |
| sector_underperforming_spy | 35.7% |
| shooting_star | 6.6% |
| sma_20_50_bullish | 43.4% |
| sma_20_50_golden_cross | 2.9% |
| sma_50_200_bullish | 36.8% |
| sma_9_21_bullish | 53.2% |
| sma_9_21_golden_cross | 5.4% |
| smc_bos_bearish | 12.5% |
| smc_bos_bullish | 8.1% |
| smc_bos_retest_long | 4.4% |
| smc_bos_retest_short | 4.7% |
| smc_breaker_block_bearish | 17.9% |
| smc_breaker_block_bullish | 14.7% |
| smc_choch_bearish | 3.0% |
| smc_choch_bullish | 2.4% |
| smc_equal_highs_swept | 2.7% |
| smc_equal_lows_swept | 6.8% |
| smc_fvg_bearish_active | 32.8% |
| smc_fvg_bullish_active | 60.6% |
| smc_fvg_retest_long_zone | 17.6% |
| smc_fvg_retest_short_zone | 11.3% |
| smc_in_discount_zone | 60.8% |
| smc_in_premium_zone | 64.0% |
| smc_inverse_fvg_bearish | 81.1% |
| smc_inverse_fvg_bullish | 87.8% |
| smc_liquidity_swept_dn | 0.7% |
| smc_liquidity_swept_up | 1.9% |
| smc_mitigation_block_long | 0.7% |
| smc_mitigation_block_short | 2.4% |
| smc_ob_bearish_active | 45.4% |
| smc_ob_bullish_active | 23.8% |
| smc_ote_long_zone | 8.8% |
| smc_ote_short_zone | 7.3% |
| squeeze_fire_dn | 1.4% |
| squeeze_fire_up | 2.9% |
| squeeze_in | 14.2% |
| squeeze_positive | 61.8% |
| stoch_bearish_cross | 12.0% |
| stoch_broad_overbought | 51.4% |
| stoch_broad_oversold | 28.2% |
| stoch_bullish_cross | 9.6% |
| stoch_overbought | 47.5% |
| stoch_oversold | 25.8% |
| stochrsi_cross_dn | 18.9% |
| stochrsi_cross_up | 19.1% |
| stochrsi_overbought | 54.6% |
| stochrsi_oversold | 26.5% |
| supertrend_bearish | 4.2% |
| supertrend_bullish | 95.8% |
| supertrend_flip_dn | 1.4% |
| supertrend_flip_recent_long_5d | 0.5% |
| supertrend_flip_recent_short_5d | 3.5% |
| supertrend_flip_up | 0.2% |
| support_break_retest | 17.9% |
| tema_above_dema | 62.0% |
| tema_cross_dn | 1.7% |
| tema_cross_up | 4.4% |
| triangle_apex_break_retest_long | 13.9% |
| triangle_ascending_detected | 6.6% |
| triangle_descending_detected | 9.5% |
| uo_overbought | 14.2% |
| uo_oversold | 7.6% |
| usd_strengthening | 24.2% |
| usd_weakening | 11.0% |
| vix_band_high | 36.5% |
| vix_band_low | 31.4% |
| vix_band_mid | 32.1% |
| vix_term_backwardation | 9.0% |
| vix_term_contango | 91.0% |
| vol_above_avg | 50.3% |
| vol_below_avg | 49.7% |
| vol_spike_12x | 34.0% |
| vol_spike_15x | 22.3% |
| vol_spike_17x | 15.2% |
| vol_spike_2x | 11.7% |
| vol_spike_2x_on_down_day_recent_3d | 4.1% |
| vol_spike_2x_on_up_day_recent_3d | 4.6% |
| vol_spike_3x | 3.2% |
| vp_above_value_area | 27.0% |
| vp_below_value_area | 16.2% |
| vp_close_above_poc | 58.3% |
| vp_close_below_poc | 41.7% |
| vp_in_value_area | 56.8% |
| week_open_gap_down_15pct | 5.1% |
| week_open_gap_up_15pct | 4.7% |
| weekly_above_ema_10 | 53.7% |
| weekly_above_ema_20 | 43.2% |
| weekly_bias_bear | 38.5% |
| weekly_bias_bull | 35.5% |
| weekly_momentum_pos | 59.1% |
| williams_r_overbought | 50.2% |
| williams_r_oversold | 26.5% |
| williams_r_rising | 47.0% |
| within_pead_window | 42.1% |
| within_post_deletion_window | 6.6% |
| within_post_inclusion_window | 2.3% |
| within_pre_rebalance_window | 1.5% |
| xs_avoid_high_ivol | 64.2% |
| xs_avoid_high_max | 64.7% |
| xs_high_beta_decile | 33.3% |
| xs_low_beta_bottom_quintile | 33.3% |
| xs_low_beta_decile | 11.9% |
| xs_low_beta_decile_entry_recent_5d | 0.7% |
| xs_low_beta_top_quintile | 11.9% |
| xs_momentum_bottom_decile | 18.8% |
| xs_momentum_bottom_quintile | 29.7% |
| xs_momentum_top_decile | 9.0% |
| xs_momentum_top_quintile | 15.1% |
| xs_quality_bottom_quintile | 21.7% |
| xs_quality_top_quintile | 22.7% |
| xs_quality_top_tercile | 40.9% |
| yoy_surprise_high | 48.1% |
| yoy_surprise_negative | 41.3% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 89.9% |
| committed_growth_holders | 89.9% |
| corp_donations_1y | 8.3% |
| corp_donations_count_1y | 8.3% |
| corp_donations_unique_pacs | 8.3% |
| cot_rut_commercials_pctile_3y | 50.5% |
| cot_rut_mmoney_pctile_3y | 50.5% |
| cup_handle_depth_pct | 12.7% |
| days_since_deletion | 10.3% |
| days_since_inclusion | 14.7% |
| days_to_next_holiday | 67.4% |
| days_to_rebalance | 11.1% |
| dpi_30d_avg | 97.5% |
| dpi_recent | 97.5% |
| earnings_announcement_return | 86.3% |
| earnings_eps_yoy_growth | 92.7% |
| gov_contracts_4q_sum | 38.5% |
| gov_contracts_last_qtr_amount | 38.5% |
| gov_contracts_qoq_growth | 38.5% |
| head_shoulders_magnitude_pct | 8.4% |
| insider_director_buyers_30d | 4.2% |
| insider_officer_buyers_30d | 4.2% |
| insider_total_shares_bought_30d | 4.2% |
| insider_unique_buyers_30d | 4.2% |
| inverted_cup_handle_height_pct | 10.6% |
| lobbying_amount_1y | 69.3% |
| lobbying_amount_q | 69.3% |
| lobbying_amount_yoy | 69.3% |
| otc_short_ratio_recent | 97.5% |
| otc_volume_recent | 97.5% |
| pair_half_life | 90.0% |
| pair_max_abs_zscore | 90.0% |
| pair_zscore_signed | 90.0% |
| pct_from_avwap_20high | 58.1% |
| pct_from_avwap_20low | 77.2% |
| pct_from_avwap_50low | 90.5% |
| persistent_holders_4q | 89.9% |
| persistent_holders_8q | 89.9% |
| sc_13g_latest_percent_owned | 0.7% |
| search_volume_index_recent | 78.2% |
| search_volume_observations | 78.2% |
| search_volume_zscore_30d | 78.2% |
| sector_etf_return_20d | 2.4% |
| short_interest_pct | 98.0% |
| spy_return_20d | 2.4% |
| total_active_holders | 89.9% |
| triangle_breakdown_pct | 9.5% |
| triangle_breakout_pct | 6.6% |
| xs_quality_decile | 66.9% |
| xs_quality_gross_profitability | 66.9% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.998), `avwap_20low` (0.999), `avwap_252low` (0.995), `avwap_50low` (0.999), `bb_10_20_lower` (0.999), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.998), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.997), `cam_r2` (0.997), `cam_r3` (0.997), `cam_r4` (0.997), `cam_s1` (0.997), `cam_s2` (0.997), `cam_s3` (0.997), `cam_s4` (0.997), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.998), `cpr_top` (0.998), `cup_handle_breakout_level` (0.998), `cup_handle_rim` (0.995), `dc10_lower` (0.999), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.997), `double_bottom_trough` (0.998), `double_top_neckline` (0.996), `double_top_peak` (0.997), `entry_stop_long` (0.996), `entry_stop_short` (0.996), `fib_236` (0.995), `fib_382` (0.996), `fib_500` (0.997), `fib_618` (0.997), `fib_786` (0.998), `fib_ext_127` (0.991), `fib_ext_162` (0.989), `head_shoulders_bottom_neckline` (0.999), `head_shoulders_top_neckline` (0.997), `hull_ma` (0.998), `ichi_kijun` (0.998), `ichi_senkou_a` (0.992), `ichi_senkou_b` (0.989), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (0.999), `monthly_close` (0.996), `monthly_sma_12` (0.982), `monthly_sma_6` (0.994), `pivot` (0.998), `prev_close` (0.997), `prev_high` (0.998), `prev_low` (0.998), `psar_value` (0.999), `r1` (0.997), `r2` (0.997), `r3` (0.997), `s1` (0.997), `s2` (0.997), `s3` (0.997), `supertrend_value` (0.996), `swing_high` (0.994), `swing_low` (0.997), `tema` (0.998), `triangle_resistance_level` (0.999), `triangle_support_level` (1.0), `vp_poc` (0.994), `vp_value_area_high` (0.994), `vp_value_area_low` (0.994), `weekly_close` (0.996), `weekly_ema_10` (0.998), `weekly_ema_20` (0.995), `wood_p` (0.998), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.998), `wood_s2` (0.998), `year_low` (0.979)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.
