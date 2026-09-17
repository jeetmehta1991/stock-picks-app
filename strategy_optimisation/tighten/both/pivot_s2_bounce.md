# Table A - pivot_s2_bounce

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit 8233e68a5 at 2026-09-17 00:26:53 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** pivot | **status:** NOT-STARTED | **R5 fires:** 55 | **surviving fires (T1):** 55 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  bearish_engulfing  <- backtest/signals/screener.py +1
       knobs P1.1-P1.1 (band rows in Table A)
P2  bullish_engulfing  <- backtest/signals/screener.py +1
       knobs P2.1-P2.1 (band rows in Table A)
P3  hammer  <- backtest/signals/screener.py +1
       knobs P3.1-P3.1 (band rows in Table A)
P4  near_r2  <- backtest/signals/screener.py +1
       knobs P4.1-P4.1 (band rows in Table A)
P5  near_s2  <- backtest/signals/screener.py +1
       knobs P5.1-P5.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P6  rsi_14 < 45   [EXISTING-THRESHOLD]
P7  rsi_14 > 60   [EXISTING-THRESHOLD]
P8  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_pivot_s2_bounce (docstring and return dropped):

```python
fl = s.get('near_s2') and s.get('rsi_14', 50) < 45 and (s.get('hammer') or s.get('bullish_engulfing'))
fs = (s.get('near_r2') and s.get('rsi_14', 50) > 60 and s.get('bearish_engulfing')) and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | bearish_engulfing - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | implicit anatomy knobs (min body/wick/step pct) - backtest/signals/technical.py:candle block (compute_candle_signals) | 0 / absent (any magnitude counts) | none - pattern bars' OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | CANON candle anatomy (Nison); production accepts any magnitude; T3 review before any grid |
| P2 | PRODUCER | bullish_engulfing - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | implicit anatomy knobs (min body/wick/step pct) - backtest/signals/technical.py:candle block (compute_candle_signals) | 0 / absent (any magnitude counts) | none - pattern bars' OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | CANON candle anatomy (Nison); production accepts any magnitude; T3 review before any grid |
| P3 | PRODUCER | hammer - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | implicit anatomy knobs (min body/wick/step pct) - backtest/signals/technical.py:candle block (compute_candle_signals) | 0 / absent (any magnitude counts) | none - pattern bars' OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | CANON candle anatomy (Nison); production accepts any magnitude; T3 review before any grid |
| P4 | PRODUCER | near_r2 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P4.x) | BANDS-DEFINED |
| P4.1 | BAND | proximity tolerance to R2 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | 0.003 | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | BRACKET production 0.003; 0.015 is the shipped near_*_wide; T3 review before any grid |
| P5 | PRODUCER | near_s2 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P5.x) | BANDS-DEFINED |
| P5.1 | BAND | proximity tolerance to S2 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | 0.003 | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | BRACKET production 0.003; 0.015 is the shipped near_*_wide; T3 review before any grid |
| P6 | STRATEGY | rsi_14 `< 45` [EXISTING-THRESHOLD] | `< 45` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P6.1 | BAND | rsi span - backtest/signals/technical.py rsi block | 14 | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production with adjacent canon spans; T3 review before any grid |
| P7 | STRATEGY | rsi_14 `> 60` [EXISTING-THRESHOLD] | `> 60` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P7.1 | BAND | rsi span - backtest/signals/technical.py rsi block | 14 | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production with adjacent canon spans; T3 review before any grid |
| P8 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | - | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `< 45` | 100.0% | TIGHTER = LOWER the ceiling: 33.274 -> 11 (20%); 37.038 -> 22 (40%); 40.148 -> 33 (60%); 42.694 -> 44 (80%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |
| rsi_14 | backtest/signals/screener.py | `> 60` | 100.0% | TIGHTER = RAISE the floor: (no QUANTS level sits tighter than production - band at T3) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 15.89, 18.55, 22.288, 28.666 | 15.89: 44 (80%); 18.55: 34 (62%); 22.288: 22 (40%); 28.666: 11 (20%) | 15.89: 11 (20%); 18.55: 23 (42%); 22.288: 33 (60%); 28.666: 44 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 27.94, 30.098, 33.264, 36.21 | 27.94: 44 (80%); 30.098: 33 (60%); 33.264: 22 (40%); 36.21: 11 (20%) | 27.94: 11 (20%); 30.098: 22 (40%); 33.264: 33 (60%); 36.21: 44 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 13.576, 16.502, 18.496, 21.036 | 13.576: 44 (80%); 16.502: 33 (60%); 18.496: 22 (40%); 21.036: 11 (20%) | 13.576: 11 (20%); 16.502: 22 (40%); 18.496: 33 (60%); 21.036: 44 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -5.5192, -3.2545, -1.8192, -0.8928 | -5.5192: 44 (80%); -3.2545: 33 (60%); -1.8192: 22 (40%); -0.8928: 11 (20%) | -5.5192: 11 (20%); -3.2545: 22 (40%); -1.8192: 33 (60%); -0.8928: 44 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.0525, 1.5751, 2.3905, 4.3055 | 1.0525: 45 (82%); 1.5751: 33 (60%); 2.3905: 22 (40%); 4.3055: 11 (20%) | 1.0525: 12 (22%); 1.5751: 22 (40%); 2.3905: 33 (60%); 4.3055: 44 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.0525, 1.5751, 2.3905, 4.3055 | 1.0525: 45 (82%); 1.5751: 33 (60%); 2.3905: 22 (40%); 4.3055: 11 (20%) | 1.0525: 12 (22%); 1.5751: 22 (40%); 2.3905: 33 (60%); 4.3055: 44 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.0028, 2.3716, 2.9096, 3.3922 | 2.0028: 44 (80%); 2.3716: 33 (60%); 2.9096: 22 (40%); 3.3922: 11 (20%) | 2.0028: 11 (20%); 2.3716: 22 (40%); 2.9096: 33 (60%); 3.3922: 44 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0477, 0.0697, 0.0885, 0.1167 | 0.0477: 44 (80%); 0.0697: 33 (60%); 0.0885: 22 (40%); 0.1167: 11 (20%) | 0.0477: 11 (20%); 0.0697: 23 (42%); 0.0885: 33 (60%); 0.1167: 44 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.0522, 0.0995, 0.188, 0.3081 | 0.0522: 44 (80%); 0.0995: 33 (60%); 0.188: 22 (40%); 0.3081: 11 (20%) | 0.0522: 11 (20%); 0.0995: 22 (40%); 0.188: 33 (60%); 0.3081: 44 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0468, 0.0642, 0.079, 0.1265 | 0.0468: 44 (80%); 0.0642: 33 (60%); 0.079: 22 (40%); 0.1265: 11 (20%) | 0.0468: 11 (20%); 0.0642: 22 (40%); 0.079: 33 (60%); 0.1265: 44 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.1796, -0.0717, 0.0594, 0.2207 | -0.1796: 44 (80%); -0.0717: 33 (60%); 0.0594: 22 (40%); 0.2207: 11 (20%) | -0.1796: 11 (20%); -0.0717: 22 (40%); 0.0594: 33 (60%); 0.2207: 44 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0624, 0.0856, 0.1053, 0.1687 | 0.0624: 44 (80%); 0.0856: 33 (60%); 0.1053: 22 (40%); 0.1687: 11 (20%) | 0.0624: 11 (20%); 0.0856: 22 (40%); 0.1053: 33 (60%); 0.1687: 44 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | -0.0097, 0.0713, 0.1696, 0.2906 | -0.0097: 44 (80%); 0.0713: 33 (60%); 0.1696: 22 (40%); 0.2906: 11 (20%) | -0.0097: 11 (20%); 0.0713: 22 (40%); 0.1696: 33 (60%); 0.2906: 44 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0417, -0.0364, -0.0107, 0.0191 | -0.0417: 44 (80%); -0.0364: 33 (60%); -0.0107: 23 (42%); 0.0191: 13 (24%) | -0.0417: 11 (20%); -0.0364: 22 (40%); -0.0107: 33 (60%); 0.0191: 45 (82%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1367, 0.1648, 0.213, 0.2724 | 0.1367: 44 (80%); 0.1648: 33 (60%); 0.213: 22 (40%); 0.2724: 11 (20%) | 0.1367: 11 (20%); 0.1648: 22 (40%); 0.213: 33 (60%); 0.2724: 44 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 55 (100%) | 0: 51 (93%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1616, -0.0544, 0.0361, 0.0976 | -0.1616: 44 (80%); -0.0544: 33 (60%); 0.0361: 22 (40%); 0.0976: 11 (20%) | -0.1616: 11 (20%); -0.0544: 22 (40%); 0.0361: 33 (60%); 0.0976: 44 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1, 2 | 0: 55 (100%); 1: 25 (45%); 2: 12 (22%) | 0: 30 (55%); 1: 43 (78%); 2: 51 (93%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2372, -0.2172, -0.1605, -0.1247 | -0.2372: 44 (80%); -0.2172: 33 (60%); -0.1605: 22 (40%); -0.1247: 11 (20%) | -0.2372: 11 (20%); -0.2172: 22 (40%); -0.1605: 33 (60%); -0.1247: 44 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2244, 0.5577, 0.6987, 0.7628 | 0.2244: 46 (84%); 0.5577: 34 (62%); 0.6987: 22 (40%); 0.7628: 12 (22%) | 0.2244: 12 (22%); 0.5577: 23 (42%); 0.6987: 33 (60%); 0.7628: 46 (84%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2821, 0.3795, 0.5846, 0.8846 | 0.2821: 46 (84%); 0.3795: 33 (60%); 0.5846: 22 (40%); 0.8846: 12 (22%) | 0.2821: 13 (24%); 0.3795: 22 (40%); 0.5846: 33 (60%); 0.8846: 46 (84%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0756, -0.0107, 0.0857, 0.1361 | -0.0756: 44 (80%); -0.0107: 33 (60%); 0.0857: 22 (40%); 0.1361: 12 (22%) | -0.0756: 11 (20%); -0.0107: 22 (40%); 0.0857: 33 (60%); 0.1361: 45 (82%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2602, 0.5128, 0.5897, 0.7244 | 0.2602: 44 (80%); 0.5128: 34 (62%); 0.5897: 23 (42%); 0.7244: 12 (22%) | 0.2602: 11 (20%); 0.5128: 23 (42%); 0.5897: 34 (62%); 0.7244: 46 (84%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0936, 0.2102, 0.441, 0.6359 | 0.0936: 44 (80%); 0.2102: 33 (60%); 0.441: 22 (40%); 0.6359: 11 (20%) | 0.0936: 11 (20%); 0.2102: 22 (40%); 0.441: 33 (60%); 0.6359: 44 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5392, -0.3279, -0.1941, 0.0892 | -0.5392: 44 (80%); -0.3279: 33 (60%); -0.1941: 23 (42%); 0.0892: 11 (20%) | -0.5392: 11 (20%); -0.3279: 22 (40%); -0.1941: 34 (62%); 0.0892: 44 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2949, 0.5321, 0.7013, 0.9615 | 0.2949: 46 (84%); 0.5321: 37 (67%); 0.7013: 22 (40%); 0.9615: 12 (22%) | 0.2949: 12 (22%); 0.5321: 24 (44%); 0.7013: 33 (60%); 0.9615: 49 (89%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0807, 0.2628, 0.4936, 0.7423 | 0.0807: 44 (80%); 0.2628: 35 (64%); 0.4936: 23 (42%); 0.7423: 11 (20%) | 0.0807: 11 (20%); 0.2628: 23 (42%); 0.4936: 35 (64%); 0.7423: 44 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0575, -0.0515, -0.0421, -0.0291 | -0.0575: 44 (80%); -0.0515: 33 (60%); -0.0421: 22 (40%); -0.0291: 13 (24%) | -0.0575: 11 (20%); -0.0515: 22 (40%); -0.0421: 33 (60%); -0.0291: 45 (82%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4731, 0.7244, 0.8077, 0.9103 | 0.4731: 44 (80%); 0.7244: 34 (62%); 0.8077: 23 (42%); 0.9103: 15 (27%) | 0.4731: 11 (20%); 0.7244: 23 (42%); 0.8077: 34 (62%); 0.9103: 45 (82%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1231, 0.3026, 0.5475, 0.7692 | 0.1231: 44 (80%); 0.3026: 33 (60%); 0.5475: 22 (40%); 0.7692: 11 (20%) | 0.1231: 11 (20%); 0.3026: 22 (40%); 0.5475: 33 (60%); 0.7692: 44 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0077, 0.0378, 0.0859, 0.1528 | -0.0077: 44 (80%); 0.0378: 34 (62%); 0.0859: 22 (40%); 0.1528: 11 (20%) | -0.0077: 11 (20%); 0.0378: 23 (42%); 0.0859: 33 (60%); 0.1528: 44 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5531, 0.741, 0.8969, 0.9757 | 0.5531: 44 (80%); 0.741: 33 (60%); 0.8969: 22 (40%); 0.9757: 11 (20%) | 0.5531: 11 (20%); 0.741: 22 (40%); 0.8969: 33 (60%); 0.9757: 44 (80%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.084, 0.3221, 0.5411, 0.7107 | 0.084: 45 (82%); 0.3221: 33 (60%); 0.5411: 22 (40%); 0.7107: 11 (20%) | 0.084: 12 (22%); 0.3221: 22 (40%); 0.5411: 33 (60%); 0.7107: 44 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0609, 0.0566, 0.123, 0.3175 | -0.0609: 44 (80%); 0.0566: 36 (65%); 0.123: 22 (40%); 0.3175: 16 (29%) | -0.0609: 11 (20%); 0.0566: 24 (44%); 0.123: 33 (60%); 0.3175: 49 (89%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1781, -0.0462, 0.0546, 0.1439 | -0.1781: 44 (80%); -0.0462: 33 (60%); 0.0546: 23 (42%); 0.1439: 11 (20%) | -0.1781: 11 (20%); -0.0462: 22 (40%); 0.0546: 34 (62%); 0.1439: 44 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2051, 0.5333, 0.7282, 0.9628 | 0.2051: 44 (80%); 0.5333: 33 (60%); 0.7282: 22 (40%); 0.9628: 11 (20%) | 0.2051: 11 (20%); 0.5333: 22 (40%); 0.7282: 33 (60%); 0.9628: 44 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1859, 0.3307, 0.5372, 0.7679 | 0.1859: 45 (82%); 0.3307: 33 (60%); 0.5372: 22 (40%); 0.7679: 11 (20%) | 0.1859: 16 (29%); 0.3307: 22 (40%); 0.5372: 33 (60%); 0.7679: 44 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0341, 0.0823, 0.1604, 0.2773 | 0.0341: 44 (80%); 0.0823: 33 (60%); 0.1604: 22 (40%); 0.2773: 11 (20%) | 0.0341: 11 (20%); 0.0823: 22 (40%); 0.1604: 33 (60%); 0.2773: 44 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 100.0% | 27, 48, 68.8, 102.2 | 27: 45 (82%); 48: 33 (60%); 68.8: 22 (40%); 102.2: 11 (20%) | 27: 13 (24%); 48: 22 (40%); 68.8: 33 (60%); 102.2: 44 (80%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 100.0% | 2.0201, 2.6696, 3.7308, 5.963 | 2.0201: 44 (80%); 2.6696: 33 (60%); 3.7308: 22 (40%); 5.963: 11 (20%) | 2.0201: 11 (20%); 2.6696: 22 (40%); 3.7308: 33 (60%); 5.963: 44 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 7.8, 14, 24.2, 36.2 | 7.8: 44 (80%); 14: 34 (62%); 24.2: 22 (40%); 36.2: 11 (20%) | 7.8: 11 (20%); 14: 26 (47%); 24.2: 33 (60%); 36.2: 44 (80%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3, 4 | 1: 51 (93%); 2: 39 (71%); 3: 27 (49%); 4: 14 (25%) | 1: 16 (29%); 2: 28 (51%); 3: 41 (75%); 4: 55 (100%) | OFFLINE |
| dpi_30d_avg | backtest/signals/congressional_alt_data.py | 100.0% | 0.4083, 0.4495, 0.5452, 0.5971 | 0.4083: 44 (80%); 0.4495: 34 (62%); 0.5452: 22 (40%); 0.5971: 11 (20%) | 0.4083: 11 (20%); 0.4495: 23 (42%); 0.5452: 33 (60%); 0.5971: 44 (80%) | OFFLINE |
| dpi_recent | backtest/signals/congressional_alt_data.py | 100.0% | 0.3771, 0.4339, 0.5366, 0.6667 | 0.3771: 44 (80%); 0.4339: 33 (60%); 0.5366: 22 (40%); 0.6667: 11 (20%) | 0.3771: 11 (20%); 0.4339: 22 (40%); 0.5366: 33 (60%); 0.6667: 44 (80%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0056, 0.0049, 0.0198, 0.0297 | -0.0056: 44 (80%); 0.0049: 33 (60%); 0.0198: 22 (40%); 0.0297: 11 (20%) | -0.0056: 11 (20%); 0.0049: 22 (40%); 0.0198: 33 (60%); 0.0297: 44 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.8609, 25.9759, 26.6168, 27.1615 | 24.8609: 44 (80%); 25.9759: 33 (60%); 26.6168: 22 (40%); 27.1615: 11 (20%) | 24.8609: 11 (20%); 25.9759: 22 (40%); 26.6168: 33 (60%); 27.1615: 44 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | 0.558, 0.9686, 1.3536, 2.2024 | 0.558: 44 (80%); 0.9686: 33 (60%); 1.3536: 22 (40%); 2.2024: 11 (20%) | 0.558: 11 (20%); 0.9686: 22 (40%); 1.3536: 33 (60%); 2.2024: 44 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -2.2024, -1.3536, -0.9686, -0.558 | -2.2024: 44 (80%); -1.3536: 33 (60%); -0.9686: 22 (40%); -0.558: 11 (20%) | -2.2024: 11 (20%); -1.3536: 22 (40%); -0.9686: 33 (60%); -0.558: 44 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0457, -0.0166, 0.0047, 0.0453 | -0.0457: 45 (82%); -0.0166: 33 (60%); 0.0047: 22 (40%); 0.0453: 11 (20%) | -0.0457: 13 (24%); -0.0166: 22 (40%); 0.0047: 33 (60%); 0.0453: 44 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0178, 8.6157, 8.7642, 8.9748 | 8.0178: 44 (80%); 8.6157: 33 (60%); 8.7642: 20 (36%); 8.9748: 11 (20%) | 8.0178: 11 (20%); 8.6157: 22 (40%); 8.7642: 35 (64%); 8.9748: 44 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 1 | 0: 55 (100%); 1: 21 (38%) | 0: 34 (62%); 1: 48 (87%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 100.0% | -0.2, 0, 1 | -0.2: 44 (80%); 0: 44 (80%); 1: 13 (24%) | -0.2: 11 (20%); 0: 42 (76%); 1: 51 (93%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 1 | 0: 55 (100%); 1: 19 (35%) | 0: 36 (65%); 1: 49 (89%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 7, 134.6, 311 | 2: 48 (87%); 7: 34 (62%); 134.6: 22 (40%); 311: 11 (20%) | 2: 13 (24%); 7: 25 (45%); 134.6: 33 (60%); 311: 44 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 6.2, 86.4, 160.8 | 1: 47 (85%); 6.2: 33 (60%); 86.4: 22 (40%); 160.8: 11 (20%) | 1: 12 (22%); 6.2: 22 (40%); 86.4: 33 (60%); 160.8: 44 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.808, -0.3078, -0.0999, 0.0734 | -0.808: 44 (80%); -0.3078: 33 (60%); -0.0999: 22 (40%); 0.0734: 11 (20%) | -0.808: 11 (20%); -0.3078: 22 (40%); -0.0999: 33 (60%); 0.0734: 44 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -2.1653, -1.1628, -0.6741, -0.3259 | -2.1653: 44 (80%); -1.1628: 33 (60%); -0.6741: 22 (40%); -0.3259: 11 (20%) | -2.1653: 11 (20%); -1.1628: 22 (40%); -0.6741: 33 (60%); -0.3259: 44 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.5597, -0.7102, -0.3731, 0.0079 | -1.5597: 44 (80%); -0.7102: 33 (60%); -0.3731: 22 (40%); 0.0079: 11 (20%) | -1.5597: 11 (20%); -0.7102: 22 (40%); -0.3731: 33 (60%); 0.0079: 44 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.5714, -0.236, -0.0992, -0.0161 | -0.5714: 44 (80%); -0.236: 33 (60%); -0.0992: 22 (40%); -0.0161: 11 (20%) | -0.5714: 11 (20%); -0.236: 22 (40%); -0.0992: 33 (60%); -0.0161: 44 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -2.4964, -1.4101, -0.8343, -0.4477 | -2.4964: 44 (80%); -1.4101: 33 (60%); -0.8343: 22 (40%); -0.4477: 11 (20%) | -2.4964: 11 (20%); -1.4101: 22 (40%); -0.8343: 33 (60%); -0.4477: 44 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -2.1653, -1.1382, -0.701, -0.2326 | -2.1653: 44 (80%); -1.1382: 33 (60%); -0.701: 22 (40%); -0.2326: 11 (20%) | -2.1653: 11 (20%); -1.1382: 22 (40%); -0.701: 33 (60%); -0.2326: 44 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 32.398, 37.38, 41.9, 48.928 | 32.398: 44 (80%); 37.38: 33 (60%); 41.9: 22 (40%); 48.928: 11 (20%) | 32.398: 11 (20%); 37.38: 22 (40%); 41.9: 33 (60%); 48.928: 44 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 100.0% | -0.1916, -0.087, -0.0252, 0.0694 | -0.1916: 44 (80%); -0.087: 33 (60%); -0.0252: 22 (40%); 0.0694: 11 (20%) | -0.1916: 11 (20%); -0.087: 22 (40%); -0.0252: 33 (60%); 0.0694: 44 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 100.0% | 0.0046, 0.0105, 0.0193, 0.0357 | 0.0046: 44 (80%); 0.0105: 33 (60%); 0.0193: 22 (40%); 0.0357: 11 (20%) | 0.0046: 11 (20%); 0.0105: 22 (40%); 0.0193: 33 (60%); 0.0357: 44 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1.6, 3.4, 7 | 0: 55 (100%); 1.6: 33 (60%); 3.4: 22 (40%); 7: 13 (24%) | 0: 14 (25%); 1.6: 22 (40%); 3.4: 33 (60%); 7: 46 (84%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2 | 0: 55 (100%); 0.2: 12 (22%) | 0: 37 (67%); 0.2: 46 (84%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.5316 | 0: 55 (100%); 0.3333: 24 (44%); 0.5316: 11 (20%) | 0: 26 (47%); 0.3333: 34 (62%); 0.5316: 44 (80%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 2.4, 4.2 | 0: 55 (100%); 1: 35 (64%); 2.4: 22 (40%); 4.2: 11 (20%) | 0: 20 (36%); 1: 27 (49%); 2.4: 33 (60%); 4.2: 44 (80%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1.6, 3.4, 7 | 0: 55 (100%); 1.6: 33 (60%); 3.4: 22 (40%); 7: 13 (24%) | 0: 14 (25%); 1.6: 22 (40%); 3.4: 33 (60%); 7: 46 (84%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2.4, 6.2 | 0: 55 (100%); 1: 37 (67%); 2.4: 22 (40%); 6.2: 11 (20%) | 0: 18 (33%); 1: 25 (45%); 2.4: 33 (60%); 6.2: 44 (80%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1184, 0.2418, 0.4663 | 0: 51 (93%); 0.1184: 33 (60%); 0.2418: 22 (40%); 0.4663: 11 (20%) | 0: 16 (29%); 0.1184: 22 (40%); 0.2418: 33 (60%); 0.4663: 44 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.09, 0.4226 | 0: 49 (89%); 0.09: 22 (40%); 0.4226: 11 (20%) | 0: 32 (58%); 0.09: 33 (60%); 0.4226: 44 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.1832, 0.4177 | 0: 50 (91%); 0.1832: 22 (40%); 0.4177: 11 (20%) | 0: 29 (53%); 0.1832: 33 (60%); 0.4177: 44 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1832, 0.4177 | 0: 50 (91%); 0.1832: 22 (40%); 0.4177: 11 (20%) | 0: 29 (53%); 0.1832: 33 (60%); 0.4177: 44 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.4191, 0, 0.0557 | -0.4191: 44 (80%); 0: 36 (65%); 0.0557: 11 (20%) | -0.4191: 11 (20%); 0: 42 (76%); 0.0557: 44 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.6964, -0.4698, 0, 0.7157 | -0.6964: 44 (80%); -0.4698: 33 (60%); 0: 27 (49%); 0.7157: 11 (20%) | -0.6964: 11 (20%); -0.4698: 22 (40%); 0: 39 (71%); 0.7157: 44 (80%) | OFFLINE |
| otc_short_ratio_recent | backtest/signals/congressional_alt_data.py | 100.0% | 0.3771, 0.4339, 0.5366, 0.6667 | 0.3771: 44 (80%); 0.4339: 33 (60%); 0.5366: 22 (40%); 0.6667: 11 (20%) | 0.3771: 11 (20%); 0.4339: 22 (40%); 0.5366: 33 (60%); 0.6667: 44 (80%) | OFFLINE |
| otc_volume_recent | backtest/signals/congressional_alt_data.py | 100.0% | 333406.2, 682333, 1626479.6, 2800211.2 | 333406.2: 44 (80%); 682333: 33 (60%); 1626479.6: 22 (40%); 2800211.2: 11 (20%) | 333406.2: 11 (20%); 682333: 22 (40%); 1626479.6: 33 (60%); 2800211.2: 44 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2.8, 4, 7, 10 | 2.8: 44 (80%); 4: 35 (64%); 7: 23 (42%); 10: 13 (24%) | 2.8: 11 (20%); 4: 26 (47%); 7: 35 (64%); 10: 46 (84%) | OFFLINE |
| pair_half_life | backtest/signals/pairs_trading.py +1 | 98.2% | 6.564, 8.85, 10.696, 13.468 | 6.564: 43 (78%); 8.85: 32 (58%); 10.696: 22 (40%); 13.468: 11 (20%) | 6.564: 11 (20%); 8.85: 22 (40%); 10.696: 32 (58%); 13.468: 43 (78%) | OFFLINE |
| pair_max_abs_zscore | backtest/signals/pairs_trading.py | 98.2% | 1.1102, 1.4767, 1.7652, 2.2271 | 1.1102: 43 (78%); 1.4767: 32 (58%); 1.7652: 22 (40%); 2.2271: 11 (20%) | 1.1102: 11 (20%); 1.4767: 22 (40%); 1.7652: 32 (58%); 2.2271: 43 (78%) | OFFLINE |
| pair_zscore_signed | backtest/signals/pairs_trading.py +1 | 98.2% | -1.9144, -1.345, -0.1141, 1.5225 | -1.9144: 43 (78%); -1.345: 32 (58%); -0.1141: 22 (40%); 1.5225: 11 (20%) | -1.9144: 11 (20%); -1.345: 22 (40%); -0.1141: 32 (58%); 1.5225: 43 (78%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0808, -0.0586, -0.0367, -0.0038 | -0.0808: 44 (80%); -0.0586: 33 (60%); -0.0367: 22 (40%); -0.0038: 11 (20%) | -0.0808: 11 (20%); -0.0586: 22 (40%); -0.0367: 33 (60%); -0.0038: 44 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.1039, -0.0671, -0.0396, -0.0144 | -0.1039: 44 (80%); -0.0671: 33 (60%); -0.0396: 22 (40%); -0.0144: 11 (20%) | -0.1039: 11 (20%); -0.0671: 22 (40%); -0.0396: 33 (60%); -0.0144: 44 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0626, -0.0353, -0.0238, -0.0092 | -0.0626: 44 (80%); -0.0353: 33 (60%); -0.0238: 22 (40%); -0.0092: 11 (20%) | -0.0626: 11 (20%); -0.0353: 22 (40%); -0.0238: 33 (60%); -0.0092: 44 (80%) | OFFLINE |
| pct_from_avwap_20high | backtest/signals/screener.py | 100.0% | -5.9168, -3.7578, -2.5336, -1.6308 | -5.9168: 44 (80%); -3.7578: 33 (60%); -2.5336: 22 (40%); -1.6308: 11 (20%) | -5.9168: 11 (20%); -3.7578: 22 (40%); -2.5336: 33 (60%); -1.6308: 44 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -18.5256, -7.6896, 5.023, 17.1442 | -18.5256: 44 (80%); -7.6896: 33 (60%); 5.023: 22 (40%); 17.1442: 11 (20%) | -18.5256: 11 (20%); -7.6896: 22 (40%); 5.023: 33 (60%); 17.1442: 44 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0361, 0.0444, 0.0542, 0.0702 | 0.0361: 44 (80%); 0.0444: 33 (60%); 0.0542: 22 (40%); 0.0702: 11 (20%) | 0.0361: 11 (20%); 0.0444: 22 (40%); 0.0542: 33 (60%); 0.0702: 44 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.6158, 0.6689, 0.7658, 0.9152 | 0.6158: 44 (80%); 0.6689: 33 (60%); 0.7658: 22 (40%); 0.9152: 11 (20%) | 0.6158: 11 (20%); 0.6689: 22 (40%); 0.7658: 33 (60%); 0.9152: 44 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.9953, -1.4583, -0.986, -0.5106 | -1.9953: 44 (80%); -1.4583: 33 (60%); -0.986: 22 (40%); -0.5106: 11 (20%) | -1.9953: 11 (20%); -1.4583: 22 (40%); -0.986: 33 (60%); -0.5106: 44 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.8612, -0.5274, -0.213, 0.0643 | -0.8612: 44 (80%); -0.5274: 33 (60%); -0.213: 22 (40%); 0.0643: 11 (20%) | -0.8612: 11 (20%); -0.5274: 22 (40%); -0.213: 33 (60%); 0.0643: 44 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.6646, -0.9495, -0.5737, 0.0107 | -1.6646: 44 (80%); -0.9495: 33 (60%); -0.5737: 22 (40%); 0.0107: 11 (20%) | -1.6646: 11 (20%); -0.9495: 22 (40%); -0.5737: 33 (60%); 0.0107: 44 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -8.8348, -6.2478, -3.855, -1.0946 | -8.8348: 44 (80%); -6.2478: 33 (60%); -3.855: 22 (40%); -1.0946: 11 (20%) | -8.8348: 11 (20%); -6.2478: 22 (40%); -3.855: 33 (60%); -1.0946: 44 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 3.19, 6.768, 13.168, 20 | 3.19: 46 (84%); 6.768: 33 (60%); 13.168: 22 (40%); 20: 11 (20%) | 3.19: 12 (22%); 6.768: 22 (40%); 13.168: 33 (60%); 20: 44 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 37.64, 40.152, 42.228, 45.538 | 37.64: 44 (80%); 40.152: 33 (60%); 42.228: 22 (40%); 45.538: 11 (20%) | 37.64: 11 (20%); 40.152: 22 (40%); 42.228: 33 (60%); 45.538: 44 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 27.988, 32.284, 36.972, 39.978 | 27.988: 44 (80%); 32.284: 33 (60%); 36.972: 22 (40%); 39.978: 11 (20%) | 27.988: 11 (20%); 32.284: 22 (40%); 36.972: 33 (60%); 39.978: 44 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.033, 0.0455, 0.0562, 0.0841 | 0.033: 44 (80%); 0.0455: 35 (64%); 0.0562: 22 (40%); 0.0841: 12 (22%) | 0.033: 11 (20%); 0.0455: 23 (42%); 0.0562: 33 (60%); 0.0841: 44 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0791, -0.0526, -0.0462, -0.0389 | -0.0791: 44 (80%); -0.0526: 34 (62%); -0.0462: 22 (40%); -0.0389: 11 (20%) | -0.0791: 11 (20%); -0.0526: 23 (42%); -0.0462: 33 (60%); -0.0389: 44 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 55 (100%); 2: 12 (22%) | 0: 41 (75%); 2: 50 (91%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 100.0% | 28, 39.2, 56.2, 71 | 28: 45 (82%); 39.2: 33 (60%); 56.2: 22 (40%); 71: 13 (24%) | 28: 12 (22%); 39.2: 22 (40%); 56.2: 33 (60%); 71: 45 (82%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.2% | 0.0123, 0.0203, 0.0318, 0.049 | 0.0123: 43 (78%); 0.0203: 32 (58%); 0.0318: 22 (40%); 0.049: 11 (20%) | 0.0123: 11 (20%); 0.0203: 22 (40%); 0.0318: 32 (58%); 0.049: 43 (78%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.1, 0.1353, 0.2269, 0.3774 | 0.1: 44 (80%); 0.1353: 33 (60%); 0.2269: 22 (40%); 0.3774: 11 (20%) | 0.1: 11 (20%); 0.1353: 22 (40%); 0.2269: 33 (60%); 0.3774: 44 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 24.66, 43.4, 67.08, 98.86 | 24.66: 44 (80%); 43.4: 33 (60%); 67.08: 22 (40%); 98.86: 11 (20%) | 24.66: 11 (20%); 43.4: 22 (40%); 67.08: 33 (60%); 98.86: 44 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -6.078, -3.5277, -1.9294, -1.258 | -6.078: 44 (80%); -3.5277: 33 (60%); -1.9294: 22 (40%); -1.258: 11 (20%) | -6.078: 11 (20%); -3.5277: 22 (40%); -1.9294: 33 (60%); -1.258: 44 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 14.278, 22.642, 30.402, 47.894 | 14.278: 44 (80%); 22.642: 33 (60%); 30.402: 22 (40%); 47.894: 11 (20%) | 14.278: 11 (20%); 22.642: 22 (40%); 30.402: 33 (60%); 47.894: 44 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 11.466, 18.924, 27.646, 39.93 | 11.466: 44 (80%); 18.924: 33 (60%); 27.646: 22 (40%); 39.93: 11 (20%) | 11.466: 11 (20%); 18.924: 22 (40%); 27.646: 33 (60%); 39.93: 44 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 2.346, 17.198, 30.124, 73.946 | 2.346: 44 (80%); 17.198: 33 (60%); 30.124: 22 (40%); 73.946: 11 (20%) | 2.346: 11 (20%); 17.198: 22 (40%); 30.124: 33 (60%); 73.946: 44 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 1.754, 29.21, 62.398 | 0: 55 (100%); 1.754: 33 (60%); 29.21: 22 (40%); 62.398: 11 (20%) | 0: 20 (36%); 1.754: 22 (40%); 29.21: 33 (60%); 62.398: 44 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 3.8, 8, 12, 16 | 3.8: 44 (80%); 8: 34 (62%); 12: 24 (44%); 16: 18 (33%) | 3.8: 11 (20%); 8: 23 (42%); 12: 34 (62%); 16: 45 (82%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 6, 9, 13.4, 18 | 6: 45 (82%); 9: 34 (62%); 13.4: 22 (40%); 18: 17 (31%) | 6: 17 (31%); 9: 24 (44%); 13.4: 33 (60%); 18: 46 (84%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 39.762, 44.022, 48.122, 51.138 | 39.762: 44 (80%); 44.022: 33 (60%); 48.122: 22 (40%); 51.138: 11 (20%) | 39.762: 11 (20%); 44.022: 22 (40%); 48.122: 33 (60%); 51.138: 44 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.169, 0.4349, 0.6262, 0.7302 | 0.169: 44 (80%); 0.4349: 33 (60%); 0.6262: 22 (40%); 0.7302: 11 (20%) | 0.169: 11 (20%); 0.4349: 22 (40%); 0.6262: 33 (60%); 0.7302: 44 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.918, 17.166, 19.162, 25.676 | 14.918: 44 (80%); 17.166: 33 (60%); 19.162: 22 (40%); 25.676: 11 (20%) | 14.918: 11 (20%); 17.166: 22 (40%); 19.162: 33 (60%); 25.676: 44 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 14.918, 17.166, 19.162, 25.676 | 14.918: 44 (80%); 17.166: 33 (60%); 19.162: 22 (40%); 25.676: 11 (20%) | 14.918: 11 (20%); 17.166: 22 (40%); 19.162: 33 (60%); 25.676: 44 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8671, 0.8914, 0.9243, 0.9663 | 0.8671: 44 (80%); 0.8914: 33 (60%); 0.9243: 23 (42%); 0.9663: 11 (20%) | 0.8671: 11 (20%); 0.8914: 22 (40%); 0.9243: 34 (62%); 0.9663: 44 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.88, 0.996, 1.194, 1.582 | 0.88: 45 (82%); 0.996: 33 (60%); 1.194: 22 (40%); 1.582: 11 (20%) | 0.88: 13 (24%); 0.996: 22 (40%); 1.194: 33 (60%); 1.582: 44 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0132, 0.0254, 0.0445, 0.0801 | 0.0132: 44 (80%); 0.0254: 33 (60%); 0.0445: 22 (40%); 0.0801: 11 (20%) | 0.0132: 12 (22%); 0.0254: 22 (40%); 0.0445: 33 (60%); 0.0801: 44 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 44.2035, 64.2497, 99.6133, 161.2004 | 44.2035: 44 (80%); 64.2497: 33 (60%); 99.6133: 22 (40%); 161.2004: 11 (20%) | 44.2035: 11 (20%); 64.2497: 22 (40%); 99.6133: 33 (60%); 161.2004: 44 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 42.1672, 62.843, 97.2905, 154.9811 | 42.1672: 44 (80%); 62.843: 33 (60%); 97.2905: 22 (40%); 154.9811: 11 (20%) | 42.1672: 11 (20%); 62.843: 22 (40%); 97.2905: 33 (60%); 154.9811: 44 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 40.4507, 60.7121, 94.4523, 148.1597 | 40.4507: 44 (80%); 60.7121: 33 (60%); 94.4523: 22 (40%); 148.1597: 11 (20%) | 40.4507: 11 (20%); 60.7121: 22 (40%); 94.4523: 33 (60%); 148.1597: 44 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 45.4655, 65.6562, 101.9023, 167.0488 | 45.4655: 44 (80%); 65.6562: 33 (60%); 101.9023: 22 (40%); 167.0488: 11 (20%) | 45.4655: 11 (20%); 65.6562: 22 (40%); 101.9023: 33 (60%); 167.0488: 44 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 47.0456, 67.0629, 104.1912, 172.8973 | 47.0456: 44 (80%); 67.0629: 33 (60%); 104.1912: 22 (40%); 172.8973: 11 (20%) | 47.0456: 11 (20%); 67.0629: 22 (40%); 104.1912: 33 (60%); 172.8973: 44 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 55 (100%) | 0: 47 (85%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0984, -0.0626, -0.0389, -0.0124 | -0.0984: 44 (80%); -0.0626: 33 (60%); -0.0389: 22 (40%); -0.0124: 11 (20%) | -0.0984: 11 (20%); -0.0626: 22 (40%); -0.0389: 33 (60%); -0.0124: 44 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -88.98, -83.776, -79.504, -68.644 | -88.98: 44 (80%); -83.776: 33 (60%); -79.504: 22 (40%); -68.644: 11 (20%) | -88.98: 11 (20%); -83.776: 22 (40%); -79.504: 33 (60%); -68.644: 44 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 100.0% | 0.4313, 0.7881, 0.9939, 1.2425 | 0.4313: 44 (80%); 0.7881: 33 (60%); 0.9939: 22 (40%); 1.2425: 11 (20%) | 0.4313: 11 (20%); 0.7881: 22 (40%); 0.9939: 33 (60%); 1.2425: 44 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 100.0% | 2, 5, 7, 9 | 2: 47 (85%); 5: 34 (62%); 7: 26 (47%); 9: 12 (22%) | 2: 13 (24%); 5: 26 (47%); 7: 36 (65%); 9: 49 (89%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 100.0% | 0.1819, 0.2096, 0.247, 0.3213 | 0.1819: 44 (80%); 0.2096: 33 (60%); 0.247: 22 (40%); 0.3213: 11 (20%) | 0.1819: 11 (20%); 0.2096: 22 (40%); 0.247: 33 (60%); 0.3213: 44 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 100.0% | 3, 5, 6, 8.2 | 3: 46 (84%); 5: 36 (65%); 6: 24 (44%); 8.2: 11 (20%) | 3: 13 (24%); 5: 31 (56%); 6: 35 (64%); 8.2: 44 (80%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 100.0% | 0.0173, 0.0242, 0.0324, 0.0415 | 0.0173: 44 (80%); 0.0242: 33 (60%); 0.0324: 23 (42%); 0.0415: 11 (20%) | 0.0173: 11 (20%); 0.0242: 22 (40%); 0.0324: 33 (60%); 0.0415: 44 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 100.0% | 2, 3, 6, 8 | 2: 48 (87%); 3: 38 (69%); 6: 24 (44%); 8: 13 (24%) | 2: 17 (31%); 3: 25 (45%); 6: 38 (69%); 8: 45 (82%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 100.0% | -0.1509, -0.0167, 0.0758, 0.2701 | -0.1509: 44 (80%); -0.0167: 33 (60%); 0.0758: 23 (42%); 0.2701: 11 (20%) | -0.1509: 11 (20%); -0.0167: 22 (40%); 0.0758: 34 (62%); 0.2701: 44 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 100.0% | 3, 4, 7, 8 | 3: 46 (84%); 4: 37 (67%); 7: 25 (45%); 8: 18 (33%) | 3: 18 (33%); 4: 23 (42%); 7: 37 (67%); 8: 45 (82%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.8% |
| 8k_item_5_02_filed_within_7d | 1.9% |
| above_avwap_20high | 1.8% |
| above_avwap_20low | 67.3% |
| above_avwap_252low | 49.1% |
| above_avwap_50low | 43.6% |
| above_prev_low | 3.6% |
| above_vwap | 47.3% |
| ad_rising | 52.7% |
| adx_cross_up | 5.5% |
| adx_cross_up_20 | 3.6% |
| adx_di_bear | 96.4% |
| adx_di_bull | 3.6% |
| adx_strong | 5.5% |
| adx_trending | 30.9% |
| ao_cross_dn | 7.3% |
| ao_positive | 7.3% |
| at_key_fib | 7.3% |
| at_key_fib_wide | 25.5% |
| avwap_20high_loss_recent_3d | 23.6% |
| avwap_20low_loss_recent_3d | 56.5% |
| avwap_252low_loss_recent_3d | 20.8% |
| avwap_50low_loss_recent_3d | 41.7% |
| bb_10_20_above_mid | 7.3% |
| bb_10_20_expanding | 69.1% |
| bb_10_20_pctb_lt_05 | 20.0% |
| bb_10_20_pctb_lt_1 | 40.0% |
| bb_10_20_pctb_lt_15 | 54.5% |
| bb_10_20_pctb_lt_2 | 61.8% |
| bb_10_20_pctb_lt_25 | 72.7% |
| bb_10_20_reclaim_from_lower_recent_3d | 12.7% |
| bb_10_20_squeeze | 45.5% |
| bb_10_20_touch_lower | 30.9% |
| bb_10_20_touch_upper | 3.6% |
| bb_20_15_above_mid | 3.6% |
| bb_20_15_expanding | 65.5% |
| bb_20_15_pctb_gt_75 | 1.8% |
| bb_20_15_pctb_gt_8 | 1.8% |
| bb_20_15_pctb_lt_05 | 58.2% |
| bb_20_15_pctb_lt_1 | 65.5% |
| bb_20_15_pctb_lt_15 | 69.1% |
| bb_20_15_pctb_lt_2 | 78.2% |
| bb_20_15_pctb_lt_25 | 83.6% |
| bb_20_15_reclaim_from_lower_recent_3d | 3.6% |
| bb_20_15_reclaim_from_upper_recent_3d | 1.8% |
| bb_20_15_squeeze | 61.8% |
| bb_20_15_touch_lower | 61.8% |
| bb_20_15_touch_upper | 1.8% |
| bb_20_20_above_mid | 3.6% |
| bb_20_20_expanding | 65.5% |
| bb_20_20_pctb_lt_05 | 38.2% |
| bb_20_20_pctb_lt_1 | 43.6% |
| bb_20_20_pctb_lt_15 | 58.2% |
| bb_20_20_pctb_lt_2 | 65.5% |
| bb_20_20_pctb_lt_25 | 70.9% |
| bb_20_20_reclaim_from_lower_recent_3d | 10.9% |
| bb_20_20_squeeze | 34.5% |
| bb_20_20_touch_lower | 32.7% |
| bearish_engulfing | 3.6% |
| below_avwap_20high | 98.2% |
| below_avwap_20low | 32.7% |
| below_avwap_252low | 50.9% |
| below_avwap_50low | 56.4% |
| below_cam_s4 | 94.5% |
| below_ema_20 | 96.4% |
| below_ema_200 | 70.9% |
| below_ema_200_break_recent_5d | 18.2% |
| below_ema_20_break_recent_5d | 34.5% |
| below_ema_21 | 96.4% |
| below_ema_21_break_recent_5d | 34.5% |
| below_ema_50 | 96.4% |
| below_ema_50_break_recent_5d | 34.5% |
| below_ema_9 | 96.4% |
| below_ema_9_break_recent_5d | 58.2% |
| below_prev_low | 96.4% |
| below_prev_low_clearance_atr_05 | 18.2% |
| below_s1 | 96.4% |
| below_s2 | 36.4% |
| below_sma_20 | 96.4% |
| below_sma_200 | 69.1% |
| below_sma_21 | 96.4% |
| below_sma_50 | 94.5% |
| below_sma_9 | 94.5% |
| below_vwap | 52.7% |
| break_52w_low | 9.1% |
| bullish_pin_bar | 54.5% |
| ceo_buy | 1.8% |
| cfo_buy | 1.8% |
| chandelier_long_bullish | 32.7% |
| chandelier_long_flip_dn | 9.1% |
| chandelier_short_bearish | 98.2% |
| close_above_open | 32.7% |
| close_below_open | 67.3% |
| close_in_bottom_40pct_of_range | 1.8% |
| close_in_top_40pct_of_range | 81.8% |
| cmf_cross_up | 9.1% |
| cmf_negative | 50.9% |
| cmf_positive | 49.1% |
| cpr_narrow | 90.9% |
| cpr_narrow_tight | 18.2% |
| cup_handle_detected | 9.1% |
| dc10_breakout_dn | 47.3% |
| dc10_breakout_dn_1pct | 74.5% |
| dc10_breakout_up | 1.8% |
| dc10_breakout_up_1pct | 3.6% |
| dc10_strong_breakout_dn | 12.7% |
| dc20_breakout_dn | 38.2% |
| dc20_breakout_up | 1.8% |
| dc20_resistance_break_retest_strong | 1.8% |
| dc20_support_break_retest_strong | 36.4% |
| defensive_leadership | 58.2% |
| director_only_buy | 3.6% |
| doji | 3.6% |
| double_bottom_detected | 14.5% |
| double_top_detected | 23.6% |
| dpi_elevated | 52.7% |
| drying_volume_on_down_turn | 30.9% |
| drying_volume_on_up_turn | 9.1% |
| ema_20_50_bearish | 72.7% |
| ema_20_50_bullish | 27.3% |
| ema_20_50_death_cross | 1.8% |
| ema_50_200_bearish | 54.5% |
| ema_50_200_bullish | 45.5% |
| ema_50_200_death_cross | 1.8% |
| ema_9_21_bearish | 92.7% |
| ema_9_21_bullish | 7.3% |
| ema_9_21_death_cross | 5.5% |
| evening_star | 10.9% |
| flag_bull_break_retest_long | 1.8% |
| flag_bull_broke | 1.8% |
| force_index_cross_dn | 10.9% |
| force_index_positive | 3.6% |
| gap_dn_1_5pct | 36.4% |
| gap_dn_2pct | 21.8% |
| hammer | 96.4% |
| head_shoulders_bottom_detected | 5.5% |
| head_shoulders_top_detected | 3.6% |
| house_cluster_buy | 1.8% |
| house_cluster_sell | 3.6% |
| htf_aligned_bear | 63.6% |
| htf_aligned_bull | 3.6% |
| htf_disagreement | 5.5% |
| hull_bearish | 83.6% |
| hull_bullish | 16.4% |
| hull_flip_dn | 3.6% |
| ichi_above_cloud | 12.7% |
| ichi_below_cloud | 74.5% |
| ichi_below_cloud_break_recent_5d | 23.6% |
| ichi_cloud_thick | 87.3% |
| ichi_tk_bearish | 80.0% |
| ichi_tk_bullish | 14.5% |
| ichi_tk_cross_dn | 5.5% |
| ichi_weekly_above_cloud | 30.9% |
| ichi_weekly_below_cloud | 36.4% |
| ichi_weekly_in_cloud | 32.7% |
| inside_kc | 72.7% |
| insider_cluster_active | 33.3% |
| institutional_buy | 92.7% |
| institutional_negative | 3.6% |
| institutional_persistence_growing | 47.2% |
| institutional_persistence_strong | 62.3% |
| institutional_strong_buy | 80.0% |
| inverted_cup_handle_detected | 18.2% |
| is_friday | 25.5% |
| is_halloween_period | 41.8% |
| is_halloween_period_first_day | 1.8% |
| is_january | 1.8% |
| is_january_extended | 5.5% |
| is_monday | 7.3% |
| is_summer_period | 58.2% |
| is_totm_window | 36.4% |
| is_totm_window_first_day | 16.4% |
| is_week_open | 14.5% |
| kc_touch_lower | 30.9% |
| kc_touch_upper | 1.8% |
| large_dollar_buy | 1.8% |
| macd_12_26_9_bearish | 70.9% |
| macd_12_26_9_bullish | 29.1% |
| macd_12_26_9_crossover_dn | 3.6% |
| macd_8_21_5_bearish | 81.8% |
| macd_8_21_5_bullish | 18.2% |
| macd_8_21_5_crossover_dn | 14.5% |
| mfi_broad_oversold | 10.9% |
| mfi_oversold | 5.5% |
| monthly_above_sma_12 | 29.1% |
| monthly_above_sma_6 | 23.6% |
| monthly_bias_bear | 63.6% |
| monthly_bias_bull | 16.4% |
| monthly_momentum_pos | 36.4% |
| near_52w_high | 3.6% |
| near_52w_high_95pct | 3.6% |
| near_52w_low | 16.4% |
| near_52w_low_105pct | 20.0% |
| near_avwap_20high_atr_05x | 12.7% |
| near_avwap_20high_atr_10x | 40.0% |
| near_avwap_20high_atr_15x | 61.8% |
| near_avwap_20high_atr_20x | 78.2% |
| near_avwap_20low_atr_05x | 47.8% |
| near_avwap_20low_atr_10x | 91.3% |
| near_avwap_20low_atr_15x | 95.7% |
| near_avwap_20low_atr_20x | 95.7% |
| near_avwap_252low_atr_05x | 16.7% |
| near_avwap_252low_atr_10x | 31.2% |
| near_avwap_252low_atr_15x | 39.6% |
| near_avwap_252low_atr_20x | 56.2% |
| near_avwap_50low_atr_05x | 27.8% |
| near_avwap_50low_atr_10x | 50.0% |
| near_avwap_50low_atr_15x | 66.7% |
| near_avwap_50low_atr_20x | 80.6% |
| near_cam_r3 | 3.6% |
| near_cam_s3 | 3.6% |
| near_cam_s4 | 40.0% |
| near_fib_500 | 1.8% |
| near_fib_618 | 5.5% |
| near_fib_786 | 5.5% |
| near_pivot | 3.6% |
| near_prev_close | 3.6% |
| near_prev_high | 3.6% |
| near_prev_low | 3.6% |
| near_r1 | 3.6% |
| near_r1_wide | 7.3% |
| near_r2 | 3.6% |
| near_r2_wide | 3.6% |
| near_s1 | 12.7% |
| near_s1_wide | 96.4% |
| near_s3 | 3.6% |
| near_wood_r1 | 3.6% |
| near_wood_s1 | 10.9% |
| news_uses_polygon_score | 16.4% |
| obv_bearish | 87.3% |
| obv_bullish | 12.7% |
| obv_diverge_bull | 1.8% |
| obv_falling | 89.1% |
| obv_rising | 10.9% |
| pead_negative_surprise | 17.0% |
| pead_positive_surprise | 7.5% |
| pin_bar | 54.5% |
| po3_accumulation_active | 56.4% |
| po3_bearish | 1.8% |
| po3_bullish | 32.7% |
| po3_manipulation_sweep_down | 43.6% |
| po3_mmbm_setup | 1.8% |
| po3_sweep_above_prior_high | 3.6% |
| ppo_bullish | 27.3% |
| ppo_crossover_dn | 3.6% |
| pre_fomc_d0 | 1.8% |
| pre_fomc_d1 | 5.5% |
| pre_fomc_window | 7.3% |
| price_above_dema | 7.3% |
| price_above_ema_20 | 3.6% |
| price_above_ema_200 | 29.1% |
| price_above_ema_200_break_recent_5d | 1.8% |
| price_above_ema_21 | 3.6% |
| price_above_ema_50 | 3.6% |
| price_above_ema_9 | 3.6% |
| price_above_hull | 12.7% |
| price_above_sma_200 | 30.9% |
| price_above_sma_21 | 3.6% |
| price_above_sma_50 | 5.5% |
| price_above_tema | 14.5% |
| price_below_dema | 92.7% |
| price_below_hull | 87.3% |
| price_below_tema | 85.5% |
| psar_bullish | 14.5% |
| psar_flip_dn | 16.4% |
| r1_break_retest_long | 12.7% |
| resistance_break_retest | 3.6% |
| risk_off_regime_bond_signal | 18.2% |
| risk_off_regime_bond_signal_strong | 14.5% |
| risk_off_regime_gold_signal | 36.4% |
| risk_on_regime_bond_signal | 52.7% |
| risk_on_regime_bond_signal_strong | 10.9% |
| roc_positive | 9.1% |
| roc_turning_dn | 9.1% |
| rsi_14_bullish | 3.6% |
| rsi_14_cross_dn_overbought_recent_3d | 1.8% |
| rsi_14_extreme_os | 1.8% |
| rsi_14_oversold | 7.3% |
| rsi_21_bullish | 3.6% |
| rsi_21_oversold | 1.8% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 20.0% |
| rsi_2_cross_dn_overbought_recent_3d | 27.3% |
| rsi_2_cross_up_extreme_os_recent_3d | 1.8% |
| rsi_2_cross_up_oversold_recent_3d | 1.8% |
| rsi_2_extreme_os | 80.0% |
| rsi_2_oversold | 90.9% |
| rsi_9_bullish | 3.6% |
| rsi_9_cross_up_oversold_recent_3d | 1.8% |
| rsi_9_extreme_os | 3.6% |
| rsi_9_overbought | 1.8% |
| rsi_9_oversold | 30.9% |
| s1_break_retest_short | 83.6% |
| sc_13d_filed_within_30d | 20.0% |
| sc_13g_filed_within_30d | 10.0% |
| sector_outperforming_spy | 50.0% |
| sector_underperforming_spy | 50.0% |
| sma_20_50_bullish | 32.7% |
| sma_50_200_bullish | 45.5% |
| sma_50_200_golden_cross | 1.8% |
| sma_9_21_bullish | 25.5% |
| sma_9_21_golden_cross | 1.8% |
| smc_bos_bearish | 5.5% |
| smc_bos_bullish | 5.5% |
| smc_bos_retest_long | 9.1% |
| smc_bos_retest_short | 1.8% |
| smc_breaker_block_bearish | 18.2% |
| smc_breaker_block_bullish | 18.2% |
| smc_choch_bearish | 5.5% |
| smc_choch_bullish | 3.6% |
| smc_equal_highs_swept | 3.6% |
| smc_equal_lows_swept | 5.5% |
| smc_fvg_bearish_active | 78.2% |
| smc_fvg_bullish_active | 12.7% |
| smc_fvg_retest_long_zone | 12.7% |
| smc_fvg_retest_short_zone | 16.4% |
| smc_in_discount_zone | 94.5% |
| smc_in_premium_zone | 20.0% |
| smc_inverse_fvg_bearish | 98.2% |
| smc_inverse_fvg_bullish | 49.1% |
| smc_liquidity_swept_dn | 1.8% |
| smc_liquidity_swept_up | 1.8% |
| smc_mitigation_block_long | 1.8% |
| smc_ob_bearish_active | 29.1% |
| smc_ob_bullish_active | 25.5% |
| smc_ote_long_zone | 14.5% |
| smc_ote_short_zone | 5.5% |
| squeeze_in | 47.3% |
| squeeze_positive | 9.1% |
| stoch_bearish_cross | 7.3% |
| stoch_broad_overbought | 3.6% |
| stoch_broad_oversold | 50.9% |
| stoch_bullish_cross | 16.4% |
| stoch_overbought | 3.6% |
| stoch_oversold | 41.8% |
| stochrsi_cross_dn | 29.1% |
| stochrsi_cross_up | 14.5% |
| stochrsi_overbought | 10.9% |
| stochrsi_oversold | 52.7% |
| supertrend_flip_recent_long_5d | 1.8% |
| supertrend_flip_recent_short_5d | 1.8% |
| supertrend_flip_up | 1.8% |
| support_break_retest | 49.1% |
| tema_above_dema | 25.5% |
| tema_cross_dn | 3.6% |
| three_black_crows | 12.7% |
| triangle_ascending_detected | 3.6% |
| triangle_descending_detected | 16.4% |
| uo_overbought | 1.8% |
| usd_strengthening | 40.0% |
| usd_weakening | 3.6% |
| vix_band_high | 36.4% |
| vix_band_low | 29.1% |
| vix_band_mid | 34.5% |
| vix_term_backwardation | 7.3% |
| vix_term_contango | 92.7% |
| vol_above_avg | 60.0% |
| vol_below_avg | 40.0% |
| vol_spike_12x | 38.2% |
| vol_spike_15x | 21.8% |
| vol_spike_17x | 18.2% |
| vol_spike_2x | 7.3% |
| vol_spike_2x_on_down_day_recent_3d | 1.8% |
| vol_spike_2x_on_up_day_recent_3d | 1.8% |
| vp_above_value_area | 1.8% |
| vp_below_value_area | 47.3% |
| vp_close_above_poc | 14.5% |
| vp_close_below_poc | 85.5% |
| vp_in_value_area | 50.9% |
| week_open_gap_down_15pct | 5.5% |
| weekly_above_ema_10 | 3.6% |
| weekly_above_ema_20 | 10.9% |
| weekly_bias_bear | 89.1% |
| weekly_bias_bull | 3.6% |
| weekly_momentum_pos | 14.5% |
| williams_r_overbought | 3.6% |
| williams_r_oversold | 58.2% |
| williams_r_rising | 38.2% |
| within_pead_window | 52.7% |
| xs_avoid_high_ivol | 80.0% |
| xs_avoid_high_max | 81.8% |
| xs_high_beta_decile | 21.8% |
| xs_low_beta_bottom_quintile | 21.8% |
| xs_low_beta_decile | 23.6% |
| xs_low_beta_top_quintile | 23.6% |
| xs_momentum_bottom_decile | 7.3% |
| xs_momentum_bottom_quintile | 16.4% |
| xs_momentum_top_decile | 9.1% |
| xs_momentum_top_quintile | 18.2% |
| xs_quality_bottom_quintile | 17.9% |
| xs_quality_top_quintile | 20.5% |
| xs_quality_top_tercile | 41.0% |
| year_low_break_retest_short | 5.5% |
| yoy_surprise_high | 45.3% |
| yoy_surprise_negative | 45.3% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 96.4% |
| committed_growth_holders | 96.4% |
| corp_donations_1y | 10.9% |
| corp_donations_count_1y | 10.9% |
| corp_donations_unique_pacs | 10.9% |
| cot_rut_commercials_pctile_3y | 50.9% |
| cot_rut_mmoney_pctile_3y | 50.9% |
| cup_handle_depth_pct | 16.4% |
| days_since_inclusion | 9.1% |
| days_to_next_holiday | 52.7% |
| days_to_rebalance | 14.5% |
| double_bottom_neckline | 14.5% |
| double_bottom_trough | 14.5% |
| earnings_announcement_return | 96.4% |
| earnings_eps_yoy_growth | 96.4% |
| gov_contracts_4q_sum | 41.8% |
| gov_contracts_last_qtr_amount | 41.8% |
| gov_contracts_qoq_growth | 41.8% |
| head_shoulders_bottom_neckline | 5.5% |
| head_shoulders_magnitude_pct | 9.1% |
| insider_director_buyers_30d | 5.5% |
| insider_officer_buyers_30d | 5.5% |
| insider_unique_buyers_30d | 5.5% |
| inverted_cup_handle_height_pct | 27.3% |
| lobbying_amount_1y | 78.2% |
| lobbying_amount_q | 78.2% |
| lobbying_amount_yoy | 78.2% |
| pct_from_avwap_20low | 41.8% |
| pct_from_avwap_252low | 87.3% |
| pct_from_avwap_50low | 65.5% |
| persistent_holders_4q | 96.4% |
| persistent_holders_8q | 96.4% |
| sc_13g_latest_percent_owned | 7.3% |
| search_volume_index_recent | 81.8% |
| search_volume_observations | 81.8% |
| search_volume_zscore_30d | 81.8% |
| total_active_holders | 96.4% |
| triangle_breakdown_pct | 16.4% |
| xs_quality_decile | 70.9% |
| xs_quality_gross_profitability | 70.9% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.997), `avwap_252low` (0.991), `avwap_50low` (0.998), `bb_10_20_lower` (0.997), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.998), `bb_20_15_lower` (0.998), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.997), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.998), `cam_r1` (0.998), `cam_r2` (0.997), `cam_r3` (0.997), `cam_r4` (0.997), `cam_s1` (0.998), `cam_s2` (0.998), `cam_s3` (0.998), `cam_s4` (0.998), `chandelier_long_value` (0.999), `chandelier_short_value` (0.998), `cpr_bottom` (0.997), `cpr_top` (0.997), `cup_handle_breakout_level` (0.983), `cup_handle_rim` (1.0), `dc10_lower` (0.997), `dc10_mid` (0.999), `dc10_upper` (0.998), `dc20_lower` (0.998), `dc20_mid` (0.999), `dc20_upper` (0.998), `dema` (0.999), `double_top_neckline` (0.995), `double_top_peak` (0.978), `entry_stop_long` (0.996), `entry_stop_short` (0.998), `fib_236` (0.993), `fib_382` (0.993), `fib_500` (0.994), `fib_618` (0.996), `fib_786` (0.997), `fib_ext_127` (0.986), `fib_ext_162` (0.981), `head_shoulders_top_neckline` (1.0), `hull_ma` (0.997), `ichi_kijun` (0.998), `ichi_senkou_a` (0.99), `ichi_senkou_b` (0.986), `ichi_tenkan` (0.998), `insider_total_shares_bought_30d` (-1.0), `inverted_cup_handle_breakdown_level` (0.993), `inverted_cup_handle_rim_low` (0.993), `kc_lower` (0.998), `kc_mid` (0.999), `kc_upper` (0.999), `monthly_close` (0.998), `monthly_sma_12` (0.977), `monthly_sma_6` (0.99), `pivot` (0.997), `prev_close` (0.998), `prev_high` (0.997), `prev_low` (0.998), `psar_value` (0.999), `r1` (0.997), `r2` (0.997), `r3` (0.997), `s1` (0.998), `s2` (0.997), `s3` (0.997), `sector_etf_return_20d` (1.0), `spy_return_20d` (1.0), `supertrend_value` (0.996), `swing_high` (0.99), `swing_low` (0.997), `tema` (0.999), `triangle_breakout_pct` (-1.0), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.99), `vp_value_area_low` (0.996), `weekly_close` (0.998), `weekly_ema_10` (0.997), `weekly_ema_20` (0.993), `wood_p` (0.998), `wood_r1` (0.997), `wood_r2` (0.997), `wood_s1` (0.998), `wood_s2` (0.998), `year_high` (0.965), `year_low` (0.955)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.
