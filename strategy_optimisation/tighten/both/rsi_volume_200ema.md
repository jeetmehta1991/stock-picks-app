# Table A - rsi_volume_200ema

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit f55b7c1e7 at 2026-09-19 23:26:39 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** confluence | **status:** NOT-STARTED | **R5 fires:** 548 | **surviving fires (T1):** 548 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  below_ema_200  <- backtest/signals/screener.py
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P1.1-P1.1 (band rows in Table A)
P2  price_above_ema_200  <- backtest/signals/index_rebalance.py +1
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P2.1-P2.1 (band rows in Table A)
P3  vol_above_avg  <- backtest/signals/screener.py +1
       DEFN: volume / 20d average >= 1.0 (technical.py:1600)
       knobs P3.1-P3.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P4  rsi_14 < 40   [EXISTING-THRESHOLD]
P5  rsi_14 > 60   [EXISTING-THRESHOLD]
P6  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_rsi_volume_200ema (docstring and return dropped):

```python
fl = s.get('rsi_14', 50) < 40 and s.get('vol_above_avg') and s.get('price_above_ema_200')
fs = (s.get('rsi_14', 50) > 60 and s.get('vol_above_avg') and s.get('below_ema_200')) and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | below_ema_200 - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | BRACKET production; 150/250 are the adjacent canon spans | 200 | 150, 200, 250 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/index_rebalance.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | BRACKET production; 150/250 are the adjacent canon spans | 200 | 150, 200, 250 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | vol_above_avg - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | volume / 20d average >= 1.0 (technical.py:1600) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | volume ratio floor (vol / avg) - backtest/signals/technical.py:1600 | BRACKET production 1.0; avg window is the second knob [10, 20, 50] | 1.0 | [1.0, 1.2, 1.5, 2.0] | TIGHTER floors where the vol ratio key is persisted on the fires; else none | LOOSER, and any window change; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | STRATEGY | rsi_14 `< 40` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `< 40` | production + 2 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P4.1 | BAND | rsi span - backtest/signals/technical.py rsi block | BRACKET production with adjacent canon spans | 14 | [9, 14, 21] | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | STRATEGY | rsi_14 `> 60` [EXISTING-THRESHOLD] | Wilder RSI over the named period - the persisted numeric the strategy thresholds (technical.py:540) | `> 60` | production + 2 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
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
| rsi_14 | backtest/signals/screener.py | `< 40` | 100.0% | TIGHTER = LOWER the ceiling: 35.498 -> 110 (20%); 39.296 -> 219 (40%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |
| rsi_14 | backtest/signals/screener.py | `> 60` | 100.0% | TIGHTER = RAISE the floor: 62.114 -> 219 (40%); 65.732 -> 110 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 18.78, 22.506, 26.176, 29.742 | 18.78: 438 (80%); 22.506: 329 (60%); 26.176: 219 (40%); 29.742: 110 (20%) | 18.78: 110 (20%); 22.506: 219 (40%); 26.176: 329 (60%); 29.742: 438 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 14.18, 17.134, 27.702, 36.3 | 14.18: 439 (80%); 17.134: 329 (60%); 27.702: 219 (40%); 36.3: 110 (20%) | 14.18: 111 (20%); 17.134: 219 (40%); 27.702: 329 (60%); 36.3: 438 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 14.726, 20.686, 32.406, 36.738 | 14.726: 438 (80%); 20.686: 329 (60%); 32.406: 219 (40%); 36.738: 110 (20%) | 14.726: 110 (20%); 20.686: 219 (40%); 32.406: 329 (60%); 36.738: 438 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -6.0826, -0.4961, 1.6662, 5.1671 | -6.0826: 438 (80%); -0.4961: 329 (60%); 1.6662: 219 (40%); 5.1671: 110 (20%) | -6.0826: 110 (20%); -0.4961: 219 (40%); 1.6662: 329 (60%); 5.1671: 438 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.4392, 2.9978, 3.4756, 4.1724 | 2.4392: 438 (80%); 2.9978: 329 (60%); 3.4756: 219 (40%); 4.1724: 110 (20%) | 2.4392: 110 (20%); 2.9978: 219 (40%); 3.4756: 329 (60%); 4.1724: 438 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0995, 0.1327, 0.1624, 0.213 | 0.0995: 440 (80%); 0.1327: 329 (60%); 0.1624: 220 (40%); 0.213: 110 (20%) | 0.0995: 111 (20%); 0.1327: 220 (40%); 0.1624: 329 (60%); 0.213: 438 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.1406, 0.3556, 0.8022, 0.896 | 0.1406: 438 (80%); 0.3556: 329 (60%); 0.8022: 220 (40%); 0.896: 110 (20%) | 0.1406: 110 (20%); 0.3556: 219 (40%); 0.8022: 329 (60%); 0.896: 438 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0892, 0.1138, 0.134, 0.1736 | 0.0892: 439 (80%); 0.1138: 329 (60%); 0.134: 219 (40%); 0.1736: 110 (20%) | 0.0892: 111 (20%); 0.1138: 221 (40%); 0.134: 329 (60%); 0.1736: 439 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.128, 0.1273, 1.0351, 1.1806 | -0.128: 438 (80%); 0.1273: 329 (60%); 1.0351: 219 (40%); 1.1806: 110 (20%) | -0.128: 110 (20%); 0.1273: 219 (40%); 1.0351: 329 (60%); 1.1806: 438 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.119, 0.1517, 0.1786, 0.2314 | 0.119: 439 (80%); 0.1517: 331 (60%); 0.1786: 219 (40%); 0.2314: 110 (20%) | 0.119: 111 (20%); 0.1517: 221 (40%); 0.1786: 329 (60%); 0.2314: 439 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.029, 0.2205, 0.9013, 1.0104 | 0.029: 438 (80%); 0.2205: 329 (60%); 0.9013: 219 (40%); 1.0104: 110 (20%) | 0.029: 110 (20%); 0.2205: 219 (40%); 0.9013: 329 (60%); 1.0104: 438 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0545, -0.0226, -0.0061, 0.035 | -0.0545: 438 (80%); -0.0226: 330 (60%); -0.0061: 225 (41%); 0.035: 110 (20%) | -0.0545: 110 (20%); -0.0226: 220 (40%); -0.0061: 331 (60%); 0.035: 438 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1409, 0.1627, 0.2024, 0.2635 | 0.1409: 438 (80%); 0.1627: 329 (60%); 0.2024: 219 (40%); 0.2635: 110 (20%) | 0.1409: 110 (20%); 0.1627: 219 (40%); 0.2024: 329 (60%); 0.2635: 438 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 548 (100%) | 0: 527 (96%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0883, 0, 0.0755, 0.1591 | -0.0883: 438 (80%); 0: 329 (60%); 0.0755: 219 (40%); 0.1591: 110 (20%) | -0.0883: 110 (20%); 0: 219 (40%); 0.0755: 329 (60%); 0.1591: 438 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 548 (100%); 1: 198 (36%) | 0: 350 (64%); 1: 460 (84%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2515, -0.1932, -0.1529, -0.1297 | -0.2515: 439 (80%); -0.1932: 329 (60%); -0.1529: 229 (42%); -0.1297: 110 (20%) | -0.2515: 112 (20%); -0.1932: 219 (40%); -0.1529: 330 (60%); -0.1297: 438 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3782, 0.5897, 0.6667, 0.7692 | 0.3782: 441 (80%); 0.5897: 331 (60%); 0.6667: 258 (47%); 0.7692: 121 (22%) | 0.3782: 111 (20%); 0.5897: 230 (42%); 0.6667: 333 (61%); 0.7692: 439 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.4231, 0.6538, 0.8795 | 0.2628: 451 (82%); 0.4231: 338 (62%); 0.6538: 221 (40%); 0.8795: 110 (20%) | 0.2628: 115 (21%); 0.4231: 225 (41%); 0.6538: 332 (61%); 0.8795: 438 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0749, 0.0028, 0.0498, 0.1902 | -0.0749: 438 (80%); 0.0028: 331 (60%); 0.0498: 223 (41%); 0.1902: 111 (20%) | -0.0749: 110 (20%); 0.0028: 220 (40%); 0.0498: 331 (60%); 0.1902: 439 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3077, 0.4538, 0.6154, 0.7628 | 0.3077: 439 (80%); 0.4538: 329 (60%); 0.6154: 225 (41%); 0.7628: 113 (21%) | 0.3077: 112 (20%); 0.4538: 219 (40%); 0.6154: 330 (60%); 0.7628: 443 (81%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1474, 0.2821, 0.4038, 0.6218 | 0.1474: 449 (82%); 0.2821: 335 (61%); 0.4038: 222 (41%); 0.6218: 117 (21%) | 0.1474: 114 (21%); 0.2821: 224 (41%); 0.4038: 330 (60%); 0.6218: 448 (82%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5641, -0.4451, -0.2179, 0.0839 | -0.5641: 438 (80%); -0.4451: 334 (61%); -0.2179: 226 (41%); 0.0839: 117 (21%) | -0.5641: 110 (20%); -0.4451: 223 (41%); -0.2179: 331 (60%); 0.0839: 442 (81%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2821, 0.4615, 0.6923, 0.9167 | 0.2821: 445 (81%); 0.4615: 336 (61%); 0.6923: 221 (40%); 0.9167: 117 (21%) | 0.2821: 114 (21%); 0.4615: 222 (41%); 0.6923: 340 (62%); 0.9167: 454 (83%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1974, 0.4218, 0.5897, 0.891 | 0.1974: 438 (80%); 0.4218: 329 (60%); 0.5897: 223 (41%); 0.891: 113 (21%) | 0.1974: 110 (20%); 0.4218: 219 (40%); 0.5897: 330 (60%); 0.891: 448 (82%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0665, -0.0565, -0.0384, 0 | -0.0665: 444 (81%); -0.0565: 339 (62%); -0.0384: 228 (42%); 0: 153 (28%) | -0.0665: 114 (21%); -0.0565: 220 (40%); -0.0384: 334 (61%); 0: 534 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4167, 0.641, 0.8846, 1 | 0.4167: 446 (81%); 0.641: 333 (61%); 0.8846: 221 (40%); 1: 118 (22%) | 0.4167: 112 (20%); 0.641: 220 (40%); 0.8846: 332 (61%); 1: 548 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1141, 0.2436, 0.5782, 0.8526 | 0.1141: 438 (80%); 0.2436: 330 (60%); 0.5782: 219 (40%); 0.8526: 124 (23%) | 0.1141: 110 (20%); 0.2436: 220 (40%); 0.5782: 329 (60%); 0.8526: 449 (82%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0019, 0.0398, 0.0911, 0.2284 | 0.0019: 438 (80%); 0.0398: 329 (60%); 0.0911: 234 (43%); 0.2284: 110 (20%) | 0.0019: 110 (20%); 0.0398: 219 (40%); 0.0911: 332 (61%); 0.2284: 438 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5625, 0.7929, 0.9306, 0.9756 | 0.5625: 439 (80%); 0.7929: 329 (60%); 0.9306: 219 (40%); 0.9756: 111 (20%) | 0.5625: 112 (20%); 0.7929: 219 (40%); 0.9306: 329 (60%); 0.9756: 439 (80%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0962, 0.326, 0.4808, 0.7308 | 0.0962: 439 (80%); 0.326: 329 (60%); 0.4808: 226 (41%); 0.7308: 111 (20%) | 0.0962: 120 (22%); 0.326: 219 (40%); 0.4808: 332 (61%); 0.7308: 439 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0495, 0.0123, 0.1182, 0.1876 | -0.0495: 442 (81%); 0.0123: 334 (61%); 0.1182: 224 (41%); 0.1876: 127 (23%) | -0.0495: 113 (21%); 0.0123: 220 (40%); 0.1182: 330 (60%); 0.1876: 446 (81%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2022, -0.0471, 0.0301, 0.0968 | -0.2022: 438 (80%); -0.0471: 330 (60%); 0.0301: 219 (40%); 0.0968: 113 (21%) | -0.2022: 110 (20%); -0.0471: 221 (40%); 0.0301: 329 (60%); 0.0968: 440 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.1923, 0.5256, 0.7179, 0.8782 | 0.1923: 451 (82%); 0.5256: 330 (60%); 0.7179: 230 (42%); 0.8782: 130 (24%) | 0.1923: 111 (20%); 0.5256: 228 (42%); 0.7179: 332 (61%); 0.8782: 443 (81%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1795, 0.3782, 0.5513, 0.8269 | 0.1795: 448 (82%); 0.3782: 337 (61%); 0.5513: 220 (40%); 0.8269: 119 (22%) | 0.1795: 111 (20%); 0.3782: 226 (41%); 0.5513: 333 (61%); 0.8269: 449 (82%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.077, 0.1848, 0.3719, 0.7818 | 0.077: 438 (80%); 0.1848: 329 (60%); 0.3719: 219 (40%); 0.7818: 110 (20%) | 0.077: 110 (20%); 0.1848: 219 (40%); 0.3719: 329 (60%); 0.7818: 438 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 99.1% | 24, 55.8, 83, 125.6 | 24: 435 (79%); 55.8: 326 (59%); 83: 225 (41%); 125.6: 109 (20%) | 24: 110 (20%); 55.8: 217 (40%); 83: 333 (61%); 125.6: 434 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.6% | 1.7995, 2.3623, 2.9527, 3.8456 | 1.7995: 437 (80%); 2.3623: 328 (60%); 2.9527: 219 (40%); 3.8456: 110 (20%) | 1.7995: 110 (20%); 2.3623: 219 (40%); 2.9527: 329 (60%); 3.8456: 437 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 7, 15, 29, 40 | 7: 443 (81%); 15: 330 (60%); 29: 226 (41%); 40: 128 (23%) | 7: 122 (22%); 15: 233 (43%); 29: 334 (61%); 40: 448 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 0, 1, 2, 4 | 0: 548 (100%); 1: 432 (79%); 2: 325 (59%); 4: 118 (22%) | 0: 116 (21%); 1: 223 (41%); 2: 332 (61%); 4: 548 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0162, -0.0055, 0.0057, 0.019 | -0.0162: 440 (80%); -0.0055: 329 (60%); 0.0057: 219 (40%); 0.019: 113 (21%) | -0.0162: 112 (20%); -0.0055: 220 (40%); 0.0057: 329 (60%); 0.019: 440 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5287, 25.8628, 26.6649, 27.3828 | 24.5287: 438 (80%); 25.8628: 329 (60%); 26.6649: 220 (40%); 27.3828: 110 (20%) | 24.5287: 110 (20%); 25.8628: 219 (40%); 26.6649: 331 (60%); 27.3828: 438 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -1.862, -0.539, 0.2286, 1.4276 | -1.862: 438 (80%); -0.539: 329 (60%); 0.2286: 219 (40%); 1.4276: 110 (20%) | -1.862: 110 (20%); -0.539: 219 (40%); 0.2286: 329 (60%); 1.4276: 438 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -1.4276, -0.2286, 0.539, 1.862 | -1.4276: 438 (80%); -0.2286: 329 (60%); 0.539: 219 (40%); 1.862: 110 (20%) | -1.4276: 110 (20%); -0.2286: 219 (40%); 0.539: 329 (60%); 1.862: 438 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0488, -0.0084, 0.0173, 0.0578 | -0.0488: 438 (80%); -0.0084: 329 (60%); 0.0173: 220 (40%); 0.0578: 111 (20%) | -0.0488: 110 (20%); -0.0084: 220 (40%); 0.0173: 330 (60%); 0.0578: 439 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0173, 8.5193, 8.7745, 9.0856 | 8.0173: 438 (80%); 8.5193: 329 (60%); 8.7745: 220 (40%); 9.0856: 110 (20%) | 8.0173: 110 (20%); 8.5193: 219 (40%); 8.7745: 328 (60%); 9.0856: 438 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 543 (99%); 1: 175 (32%) | 0: 368 (67%); 1: 486 (89%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0 | 0: 440 (80%) | 0: 460 (84%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 543 (99%); 1: 191 (35%) | 0: 352 (64%); 1: 485 (89%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 3, 7, 154, 271 | 3: 445 (81%); 7: 330 (60%); 154: 220 (40%); 271: 111 (20%) | 3: 134 (24%); 7: 232 (42%); 154: 330 (60%); 271: 440 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 7, 87, 147 | 1: 471 (86%); 7: 331 (60%); 87: 221 (40%); 147: 111 (20%) | 1: 119 (22%); 7: 222 (41%); 87: 332 (61%); 147: 440 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -1.5904, -0.2507, 0.3779, 1.0868 | -1.5904: 438 (80%); -0.2507: 329 (60%); 0.3779: 219 (40%); 1.0868: 110 (20%) | -1.5904: 110 (20%); -0.2507: 219 (40%); 0.3779: 329 (60%); 1.0868: 438 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -1.6625, -0.1677, 0.4802, 1.5305 | -1.6625: 438 (80%); -0.1677: 329 (60%); 0.4802: 219 (40%); 1.5305: 110 (20%) | -1.6625: 110 (20%); -0.1677: 219 (40%); 0.4802: 329 (60%); 1.5305: 438 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.0006, -0.106, 0.356, 1.175 | -1.0006: 438 (80%); -0.106: 329 (60%); 0.356: 219 (40%); 1.175: 110 (20%) | -1.0006: 110 (20%); -0.106: 219 (40%); 0.356: 329 (60%); 1.175: 438 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -1.1462, -0.091, 0.2568, 0.7425 | -1.1462: 438 (80%); -0.091: 329 (60%); 0.2568: 219 (40%); 0.7425: 110 (20%) | -1.1462: 110 (20%); -0.091: 219 (40%); 0.2568: 329 (60%); 0.7425: 438 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -2.9572, -0.5761, 0.934, 2.3447 | -2.9572: 438 (80%); -0.5761: 329 (60%); 0.934: 219 (40%); 2.3447: 110 (20%) | -2.9572: 110 (20%); -0.5761: 219 (40%); 0.934: 329 (60%); 2.3447: 438 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -1.8586, -0.1038, 0.5656, 1.6886 | -1.8586: 438 (80%); -0.1038: 329 (60%); 0.5656: 219 (40%); 1.6886: 110 (20%) | -1.8586: 110 (20%); -0.1038: 219 (40%); 0.5656: 329 (60%); 1.6886: 438 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 32.786, 49, 63.71, 73.14 | 32.786: 438 (80%); 49: 329 (60%); 63.71: 219 (40%); 73.14: 111 (20%) | 32.786: 110 (20%); 49: 219 (40%); 63.71: 329 (60%); 73.14: 439 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.1% | 0.0104, 0.0227, 0.0394, 0.067 | 0.0104: 435 (79%); 0.0227: 326 (59%); 0.0394: 217 (40%); 0.067: 109 (20%) | 0.0104: 108 (20%); 0.0227: 217 (40%); 0.0394: 326 (59%); 0.067: 434 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0.4, 2, 5, 12.6 | 0.4: 438 (80%); 2: 358 (65%); 5: 242 (44%); 12.6: 110 (20%) | 0.4: 110 (20%); 2: 243 (44%); 5: 340 (62%); 12.6: 438 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0769, 0.2 | 0: 548 (100%); 0.0769: 220 (40%); 0.2: 125 (23%) | 0: 309 (56%); 0.0769: 330 (60%); 0.2: 440 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.25, 0.4615, 0.6667 | 0: 548 (100%); 0.25: 334 (61%); 0.4615: 220 (40%); 0.6667: 119 (22%) | 0: 176 (32%); 0.25: 230 (42%); 0.4615: 331 (60%); 0.6667: 451 (82%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 4, 9 | 0: 548 (100%); 1: 407 (74%); 4: 234 (43%); 9: 118 (22%) | 0: 141 (26%); 1: 221 (40%); 4: 348 (64%); 9: 440 (80%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0.4, 2, 5, 12.6 | 0.4: 438 (80%); 2: 358 (65%); 5: 242 (44%); 12.6: 110 (20%) | 0.4: 110 (20%); 2: 243 (44%); 5: 340 (62%); 12.6: 438 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 548 (100%); 1: 374 (68%); 3: 240 (44%); 8: 122 (22%) | 0: 174 (32%); 1: 245 (45%); 3: 344 (63%); 8: 446 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.0303, 0.2342, 0.3775, 0.6 | 0.0303: 438 (80%); 0.2342: 329 (60%); 0.3775: 219 (40%); 0.6: 112 (20%) | 0.0303: 110 (20%); 0.2342: 219 (40%); 0.3775: 329 (60%); 0.6: 441 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2308, 0.5061 | 0: 469 (86%); 0.2308: 220 (40%); 0.5061: 110 (20%) | 0: 271 (49%); 0.2308: 330 (60%); 0.5061: 438 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.0278, 0.3172, 0.56 | 0: 493 (90%); 0.0278: 329 (60%); 0.3172: 219 (40%); 0.56: 111 (20%) | 0: 217 (40%); 0.0278: 219 (40%); 0.3172: 329 (60%); 0.56: 439 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0278, 0.3172, 0.56 | 0: 493 (90%); 0.0278: 329 (60%); 0.3172: 219 (40%); 0.56: 111 (20%) | 0: 217 (40%); 0.0278: 219 (40%); 0.3172: 329 (60%); 0.56: 439 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1395, 0, 0.1759 | -0.1395: 438 (80%); 0: 392 (72%); 0.1759: 110 (20%) | -0.1395: 110 (20%); 0: 385 (70%); 0.1759: 438 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.4472, 0, 0.7715, 2.4342 | -0.4472: 441 (80%); 0: 372 (68%); 0.7715: 219 (40%); 2.4342: 110 (20%) | -0.4472: 143 (26%); 0: 252 (46%); 0.7715: 329 (60%); 2.4342: 438 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 11 | 2: 458 (84%); 4: 373 (68%); 7: 235 (43%); 11: 113 (21%) | 2: 128 (23%); 4: 230 (42%); 7: 349 (64%); 11: 451 (82%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0984, -0.0306, 0.0713, 0.1125 | -0.0984: 438 (80%); -0.0306: 328 (60%); 0.0713: 220 (40%); 0.1125: 110 (20%) | -0.0984: 110 (20%); -0.0306: 220 (40%); 0.0713: 328 (60%); 0.1125: 438 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0976, -0.0242, 0.0829, 0.1321 | -0.0976: 438 (80%); -0.0242: 329 (60%); 0.0829: 220 (40%); 0.1321: 110 (20%) | -0.0976: 110 (20%); -0.0242: 219 (40%); 0.0829: 328 (60%); 0.1321: 438 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0737, -0.009, 0.0424, 0.0822 | -0.0737: 438 (80%); -0.009: 329 (60%); 0.0424: 219 (40%); 0.0822: 110 (20%) | -0.0737: 110 (20%); -0.009: 219 (40%); 0.0424: 329 (60%); 0.0822: 438 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -24.3344, -11.4734, 3.2278, 30.0568 | -24.3344: 438 (80%); -11.4734: 329 (60%); 3.2278: 219 (40%); 30.0568: 110 (20%) | -24.3344: 110 (20%); -11.4734: 219 (40%); 3.2278: 329 (60%); 30.0568: 438 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0581, 0.0812, 0.1064, 0.1456 | 0.0581: 439 (80%); 0.0812: 330 (60%); 0.1064: 220 (40%); 0.1456: 110 (20%) | 0.0581: 110 (20%); 0.0812: 220 (40%); 0.1064: 332 (61%); 0.1456: 439 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1706, 0.3596, 0.5529, 0.7706 | 0.1706: 438 (80%); 0.3596: 329 (60%); 0.5529: 219 (40%); 0.7706: 110 (20%) | 0.1706: 110 (20%); 0.3596: 219 (40%); 0.5529: 329 (60%); 0.7706: 438 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.6006, -0.2295, 1.0536, 2.1556 | -1.6006: 438 (80%); -0.2295: 329 (60%); 1.0536: 219 (40%); 2.1556: 110 (20%) | -1.6006: 110 (20%); -0.2295: 219 (40%); 1.0536: 329 (60%); 2.1556: 438 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -1.2608, -0.4059, 0.858, 1.3289 | -1.2608: 438 (80%); -0.4059: 329 (60%); 0.858: 219 (40%); 1.3289: 110 (20%) | -1.2608: 110 (20%); -0.4059: 219 (40%); 0.858: 329 (60%); 1.3289: 438 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.0287, -0.1933, 0.5518, 1.4258 | -1.0287: 438 (80%); -0.1933: 329 (60%); 0.5518: 219 (40%); 1.4258: 110 (20%) | -1.0287: 110 (20%); -0.1933: 219 (40%); 0.5518: 329 (60%); 1.4258: 438 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -9.9826, -3.7878, 7.7046, 11.7472 | -9.9826: 438 (80%); -3.7878: 329 (60%); 7.7046: 219 (40%); 11.7472: 110 (20%) | -9.9826: 110 (20%); -3.7878: 219 (40%); 7.7046: 329 (60%); 11.7472: 438 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 19.46, 42.138, 69.236, 93.202 | 19.46: 438 (80%); 42.138: 329 (60%); 69.236: 219 (40%); 93.202: 110 (20%) | 19.46: 110 (20%); 42.138: 219 (40%); 69.236: 329 (60%); 93.202: 438 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 40.52, 44.474, 57.352, 59.69 | 40.52: 439 (80%); 44.474: 329 (60%); 57.352: 219 (40%); 59.69: 110 (20%) | 40.52: 111 (20%); 44.474: 219 (40%); 57.352: 329 (60%); 59.69: 438 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 28.866, 37.002, 67.822, 72.768 | 28.866: 438 (80%); 37.002: 329 (60%); 67.822: 219 (40%); 72.768: 110 (20%) | 28.866: 110 (20%); 37.002: 219 (40%); 67.822: 329 (60%); 72.768: 438 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.031, 0.0438, 0.06, 0.0872 | 0.031: 438 (80%); 0.0438: 329 (60%); 0.06: 223 (41%); 0.0872: 110 (20%) | 0.031: 110 (20%); 0.0438: 220 (40%); 0.06: 331 (60%); 0.0872: 438 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0787, -0.0585, -0.045, -0.0327 | -0.0787: 438 (80%); -0.0585: 329 (60%); -0.045: 220 (40%); -0.0327: 110 (20%) | -0.0787: 110 (20%); -0.0585: 221 (40%); -0.045: 329 (60%); -0.0327: 438 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 548 (100%); 1: 137 (25%) | 0: 411 (75%); 1: 461 (84%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 26, 43, 59, 68 | 26: 438 (80%); 43: 333 (61%); 59: 221 (40%); 68: 121 (22%) | 26: 110 (20%); 43: 221 (40%); 59: 330 (60%); 68: 438 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.4% | 0.0132, 0.0195, 0.0282, 0.047 | 0.0132: 432 (79%); 0.0195: 323 (59%); 0.0282: 216 (39%); 0.047: 108 (20%) | 0.0132: 107 (20%); 0.0195: 216 (39%); 0.0282: 323 (59%); 0.047: 431 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.1965, 0.4425, 0.7114, 0.8478 | 0.1965: 438 (80%); 0.4425: 329 (60%); 0.7114: 219 (40%); 0.8478: 110 (20%) | 0.1965: 110 (20%); 0.4425: 219 (40%); 0.7114: 329 (60%); 0.8478: 438 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 29.24, 47.74, 66.3, 103.74 | 29.24: 438 (80%); 47.74: 329 (60%); 66.3: 220 (40%); 103.74: 110 (20%) | 29.24: 110 (20%); 47.74: 219 (40%); 66.3: 330 (60%); 103.74: 438 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -8.228, -1.488, 2.281, 5.796 | -8.228: 438 (80%); -1.488: 329 (60%); 2.281: 219 (40%); 5.796: 110 (20%) | -8.228: 110 (20%); -1.488: 219 (40%); 2.281: 329 (60%); 5.796: 438 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 13.718, 42.718, 80.866, 89.308 | 13.718: 438 (80%); 42.718: 329 (60%); 80.866: 219 (40%); 89.308: 110 (20%) | 13.718: 110 (20%); 42.718: 219 (40%); 80.866: 329 (60%); 89.308: 438 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 13.264, 33.92, 82.878, 89.152 | 13.264: 438 (80%); 33.92: 329 (60%); 82.878: 219 (40%); 89.152: 110 (20%) | 13.264: 110 (20%); 33.92: 219 (40%); 82.878: 329 (60%); 89.152: 438 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 7.314, 33.096, 81.204, 95.1 | 7.314: 438 (80%); 33.096: 329 (60%); 81.204: 219 (40%); 95.1: 110 (20%) | 7.314: 110 (20%); 33.096: 219 (40%); 81.204: 329 (60%); 95.1: 438 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 4.35, 36.328, 82.126, 99.74 | 4.35: 438 (80%); 36.328: 329 (60%); 82.126: 219 (40%); 99.74: 110 (20%) | 4.35: 110 (20%); 36.328: 219 (40%); 82.126: 329 (60%); 99.74: 438 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 8, 12, 16 | 5: 443 (81%); 8: 346 (63%); 12: 243 (44%); 16: 127 (23%) | 5: 150 (27%); 8: 231 (42%); 12: 331 (60%); 16: 446 (81%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 14, 17 | 5: 451 (82%); 10: 335 (61%); 14: 223 (41%); 17: 153 (28%) | 5: 120 (22%); 10: 255 (47%); 14: 352 (64%); 17: 452 (82%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 38.986, 49.1, 57.066, 62.902 | 38.986: 438 (80%); 49.1: 329 (60%); 57.066: 219 (40%); 62.902: 110 (20%) | 38.986: 110 (20%); 49.1: 219 (40%); 57.066: 329 (60%); 62.902: 438 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.15, 0.4524, 0.6318, 0.873 | 0.15: 438 (80%); 0.4524: 331 (60%); 0.6318: 219 (40%); 0.873: 112 (20%) | 0.15: 110 (20%); 0.4524: 220 (40%); 0.6318: 329 (60%); 0.873: 442 (81%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.18, 17.788, 20.34, 24.654 | 15.18: 438 (80%); 17.788: 329 (60%); 20.34: 224 (41%); 24.654: 110 (20%) | 15.18: 110 (20%); 17.788: 219 (40%); 20.34: 331 (60%); 24.654: 438 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 15.18, 17.788, 20.34, 24.654 | 15.18: 438 (80%); 17.788: 329 (60%); 20.34: 224 (41%); 24.654: 110 (20%) | 15.18: 110 (20%); 17.788: 219 (40%); 20.34: 331 (60%); 24.654: 438 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8523, 0.8875, 0.922, 0.9661 | 0.8523: 443 (81%); 0.8875: 329 (60%); 0.922: 219 (40%); 0.9661: 111 (20%) | 0.8523: 112 (20%); 0.8875: 219 (40%); 0.922: 329 (60%); 0.9661: 439 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 1.11, 1.248, 1.452, 1.878 | 1.11: 445 (81%); 1.248: 329 (60%); 1.452: 219 (40%); 1.878: 110 (20%) | 1.11: 115 (21%); 1.248: 219 (40%); 1.452: 329 (60%); 1.878: 438 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0372, 0.0663, 0.0951, 0.1289 | 0.0372: 439 (80%); 0.0663: 329 (60%); 0.0951: 220 (40%); 0.1289: 110 (20%) | 0.0372: 110 (20%); 0.0663: 220 (40%); 0.0951: 331 (60%); 0.1289: 438 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 40.0929, 71.3648, 121.6057, 198.5631 | 40.0929: 438 (80%); 71.3648: 329 (60%); 121.6057: 219 (40%); 198.5631: 110 (20%) | 40.0929: 110 (20%); 71.3648: 219 (40%); 121.6057: 329 (60%); 198.5631: 438 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 37.4684, 68.1943, 116.1478, 189.1616 | 37.4684: 438 (80%); 68.1943: 329 (60%); 116.1478: 219 (40%); 189.1616: 110 (20%) | 37.4684: 110 (20%); 68.1943: 219 (40%); 116.1478: 329 (60%); 189.1616: 438 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 35.0873, 64.8598, 110.6128, 180.7102 | 35.0873: 438 (80%); 64.8598: 329 (60%); 110.6128: 219 (40%); 180.7102: 110 (20%) | 35.0873: 110 (20%); 64.8598: 219 (40%); 110.6128: 329 (60%); 180.7102: 438 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 42.1078, 73.9475, 125.1997, 213.6573 | 42.1078: 438 (80%); 73.9475: 329 (60%); 125.1997: 219 (40%); 213.6573: 110 (20%) | 42.1078: 110 (20%); 73.9475: 219 (40%); 125.1997: 329 (60%); 213.6573: 438 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 44.0952, 77.6714, 130.664, 223.2902 | 44.0952: 438 (80%); 77.6714: 329 (60%); 130.664: 219 (40%); 223.2902: 110 (20%) | 44.0952: 110 (20%); 77.6714: 219 (40%); 130.664: 329 (60%); 223.2902: 438 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 548 (100%) | 0: 466 (85%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 548 (100%) | 0: 502 (92%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0988, -0.0342, 0.0844, 0.131 | -0.0988: 438 (80%); -0.0342: 329 (60%); 0.0844: 219 (40%); 0.131: 110 (20%) | -0.0988: 110 (20%); -0.0342: 219 (40%); 0.0844: 329 (60%); 0.131: 438 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -83.132, -65.45, -21.79, -15.406 | -83.132: 438 (80%); -65.45: 329 (60%); -21.79: 220 (40%); -15.406: 110 (20%) | -83.132: 110 (20%); -65.45: 219 (40%); -21.79: 330 (60%); -15.406: 438 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.1% | 0.6133, 0.9094, 1.1305, 1.4598 | 0.6133: 434 (79%); 0.9094: 326 (59%); 1.1305: 217 (40%); 1.4598: 109 (20%) | 0.6133: 109 (20%); 0.9094: 217 (40%); 1.1305: 326 (59%); 1.4598: 434 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 6, 8, 9 | 3: 472 (86%); 6: 354 (65%); 8: 237 (43%); 9: 179 (33%) | 3: 113 (21%); 6: 252 (46%); 8: 364 (66%); 9: 437 (80%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.1% | 0.2198, 0.2682, 0.3317, 0.4173 | 0.2198: 434 (79%); 0.2682: 326 (59%); 0.3317: 217 (40%); 0.4173: 109 (20%) | 0.2198: 109 (20%); 0.2682: 217 (40%); 0.3317: 326 (59%); 0.4173: 434 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.1% | 4, 7, 9, 10 | 4: 466 (85%); 7: 350 (64%); 9: 226 (41%); 10: 127 (23%) | 4: 111 (20%); 7: 251 (46%); 9: 416 (76%); 10: 543 (99%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.1% | 0.0264, 0.0367, 0.0483, 0.0714 | 0.0264: 434 (79%); 0.0367: 327 (60%); 0.0483: 218 (40%); 0.0714: 109 (20%) | 0.0264: 109 (20%); 0.0367: 218 (40%); 0.0483: 326 (59%); 0.0714: 434 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.1% | 4, 6, 8, 10 | 4: 446 (81%); 6: 364 (66%); 8: 260 (47%); 10: 120 (22%) | 4: 132 (24%); 6: 228 (42%); 8: 349 (64%); 10: 543 (99%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.1% | -0.3478, -0.2009, 0.0708, 0.4072 | -0.3478: 434 (79%); -0.2009: 326 (59%); 0.0708: 217 (40%); 0.4072: 109 (20%) | -0.3478: 109 (20%); -0.2009: 217 (40%); 0.0708: 326 (59%); 0.4072: 434 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.1% | 1, 2, 6, 9 | 1: 543 (99%); 2: 392 (72%); 6: 229 (42%); 9: 151 (28%) | 1: 151 (28%); 2: 219 (40%); 6: 333 (61%); 9: 444 (81%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 10.0% |
| 8k_item_5_02_filed_within_7d | 3.0% |
| above_avwap_20high | 9.7% |
| above_avwap_20low | 92.9% |
| above_avwap_252low | 93.3% |
| above_avwap_50low | 78.3% |
| above_cam_r3 | 30.5% |
| above_cam_r4 | 17.5% |
| above_cpr | 52.6% |
| above_pivot | 54.7% |
| above_prev_high | 23.7% |
| above_prev_high_clearance_atr_05 | 11.3% |
| above_prev_low | 80.3% |
| above_r1 | 19.2% |
| above_r2 | 11.5% |
| above_vwap | 43.2% |
| above_wood_p | 53.5% |
| ad_rising | 55.1% |
| adx_cross_up | 8.6% |
| adx_cross_up_20 | 7.5% |
| adx_di_bear | 42.5% |
| adx_di_bull | 57.5% |
| adx_strong | 2.2% |
| adx_trending | 47.4% |
| ao_cross_dn | 2.9% |
| ao_cross_up | 3.6% |
| ao_positive | 58.0% |
| ao_twin_peaks_bull | 0.9% |
| at_key_fib | 9.3% |
| at_key_fib_wide | 24.6% |
| avwap_20high_loss_recent_3d | 24.0% |
| avwap_20high_reclaim_recent_3d | 3.0% |
| avwap_20low_loss_recent_3d | 1.7% |
| avwap_20low_reclaim_recent_3d | 18.4% |
| avwap_252low_loss_recent_3d | 1.5% |
| avwap_252low_reclaim_recent_3d | 5.4% |
| avwap_50low_loss_recent_3d | 10.6% |
| avwap_50low_reclaim_recent_3d | 9.6% |
| bb_10_20_above_mid | 57.8% |
| bb_10_20_expanding | 71.2% |
| bb_10_20_pctb_gt_75 | 47.6% |
| bb_10_20_pctb_gt_8 | 40.1% |
| bb_10_20_pctb_gt_85 | 29.0% |
| bb_10_20_pctb_gt_9 | 19.3% |
| bb_10_20_pctb_gt_95 | 12.8% |
| bb_10_20_pctb_lt_05 | 6.9% |
| bb_10_20_pctb_lt_1 | 13.7% |
| bb_10_20_pctb_lt_15 | 21.2% |
| bb_10_20_pctb_lt_2 | 28.8% |
| bb_10_20_pctb_lt_25 | 34.5% |
| bb_10_20_reclaim_from_lower_recent_3d | 20.4% |
| bb_10_20_reclaim_from_upper_recent_3d | 22.4% |
| bb_10_20_squeeze | 10.6% |
| bb_10_20_touch_lower | 6.4% |
| bb_10_20_touch_upper | 12.4% |
| bb_20_15_above_mid | 57.5% |
| bb_20_15_expanding | 87.2% |
| bb_20_15_pctb_gt_75 | 57.5% |
| bb_20_15_pctb_gt_8 | 57.3% |
| bb_20_15_pctb_gt_85 | 56.0% |
| bb_20_15_pctb_gt_9 | 52.9% |
| bb_20_15_pctb_gt_95 | 49.8% |
| bb_20_15_pctb_lt_05 | 37.2% |
| bb_20_15_pctb_lt_1 | 39.2% |
| bb_20_15_pctb_lt_15 | 40.7% |
| bb_20_15_pctb_lt_2 | 41.8% |
| bb_20_15_pctb_lt_25 | 42.3% |
| bb_20_15_reclaim_from_lower_recent_3d | 5.8% |
| bb_20_15_reclaim_from_upper_recent_3d | 10.0% |
| bb_20_15_squeeze | 13.5% |
| bb_20_15_touch_lower | 36.5% |
| bb_20_15_touch_upper | 48.9% |
| bb_20_20_above_mid | 57.5% |
| bb_20_20_expanding | 87.2% |
| bb_20_20_pctb_gt_75 | 56.2% |
| bb_20_20_pctb_gt_8 | 52.9% |
| bb_20_20_pctb_gt_85 | 48.7% |
| bb_20_20_pctb_gt_9 | 40.1% |
| bb_20_20_pctb_gt_95 | 31.0% |
| bb_20_20_pctb_lt_05 | 23.7% |
| bb_20_20_pctb_lt_1 | 30.7% |
| bb_20_20_pctb_lt_15 | 36.3% |
| bb_20_20_pctb_lt_2 | 39.2% |
| bb_20_20_pctb_lt_25 | 41.4% |
| bb_20_20_reclaim_from_lower_recent_3d | 16.2% |
| bb_20_20_reclaim_from_upper_recent_3d | 20.3% |
| bb_20_20_squeeze | 4.9% |
| bb_20_20_touch_lower | 19.9% |
| bb_20_20_touch_upper | 29.2% |
| bearish_engulfing | 2.2% |
| bearish_pin_bar | 10.2% |
| below_avwap_20high | 90.3% |
| below_avwap_20low | 7.1% |
| below_avwap_252low | 6.7% |
| below_avwap_50low | 21.7% |
| below_cam_s3 | 26.5% |
| below_cam_s4 | 14.8% |
| below_cpr | 45.3% |
| below_ema_20 | 42.5% |
| below_ema_200 | 57.5% |
| below_ema_200_break_recent_5d | 4.4% |
| below_ema_20_break_recent_5d | 12.8% |
| below_ema_21 | 42.5% |
| below_ema_21_break_recent_5d | 13.3% |
| below_ema_50 | 42.9% |
| below_ema_50_break_recent_5d | 24.3% |
| below_ema_9 | 42.3% |
| below_ema_9_break_recent_5d | 14.1% |
| below_prev_high | 76.3% |
| below_prev_low | 18.8% |
| below_prev_low_clearance_atr_05 | 6.9% |
| below_s1 | 16.2% |
| below_s2 | 6.9% |
| below_sma_20 | 42.5% |
| below_sma_200 | 54.2% |
| below_sma_21 | 42.5% |
| below_sma_50 | 42.5% |
| below_sma_9 | 41.6% |
| below_vwap | 56.8% |
| bullish_engulfing | 1.8% |
| bullish_pin_bar | 7.8% |
| ceo_buy | 0.2% |
| cfo_buy | 0.2% |
| chandelier_long_bullish | 57.5% |
| chandelier_long_flip_dn | 2.0% |
| chandelier_short_bearish | 44.0% |
| chandelier_short_flip_up | 4.2% |
| close_above_open | 42.5% |
| close_below_open | 57.5% |
| close_in_bottom_40pct_of_range | 43.8% |
| close_in_top_40pct_of_range | 35.6% |
| cluster_buy | 0.2% |
| cmf_cross_dn | 3.6% |
| cmf_cross_up | 5.1% |
| cmf_negative | 40.0% |
| cmf_positive | 60.0% |
| concentrated_sell | 5.4% |
| cpr_narrow | 83.6% |
| cpr_narrow_tight | 21.9% |
| cup_handle_detected | 3.1% |
| cup_handle_neckline_break_retest_long | 2.2% |
| dc10_breakout_dn | 12.6% |
| dc10_breakout_dn_1pct | 17.5% |
| dc10_breakout_up | 19.5% |
| dc10_breakout_up_1pct | 28.1% |
| dc10_new_high | 38.7% |
| dc10_strong_breakout_dn | 5.1% |
| dc10_strong_breakout_up | 10.0% |
| dc20_breakout_dn | 11.7% |
| dc20_breakout_up | 19.0% |
| dc20_new_high | 38.5% |
| dc20_resistance_break_retest_strong | 30.8% |
| dc20_support_break_retest_strong | 21.5% |
| defensive_leadership | 42.9% |
| director_only_buy | 2.4% |
| doji | 6.9% |
| double_bottom_detected | 12.4% |
| double_top_detected | 13.5% |
| dpi_elevated | 56.4% |
| ema_20_50_bearish | 48.2% |
| ema_20_50_bullish | 51.8% |
| ema_20_50_death_cross | 1.3% |
| ema_20_50_golden_cross | 3.5% |
| ema_50_200_bearish | 57.5% |
| ema_50_200_bullish | 42.5% |
| ema_9_21_bearish | 42.2% |
| ema_9_21_bullish | 57.8% |
| ema_9_21_death_cross | 2.2% |
| ema_9_21_golden_cross | 3.1% |
| evening_star | 2.0% |
| flag_bear_break_retest_short | 0.2% |
| flag_bear_broke | 0.2% |
| flag_bull_break_retest_long | 1.1% |
| flag_bull_broke | 1.1% |
| flag_bull_detected | 0.2% |
| force_index_cross_dn | 1.5% |
| force_index_cross_up | 1.3% |
| force_index_positive | 57.1% |
| gap_dn_1_5pct | 19.5% |
| gap_dn_2pct | 15.5% |
| gap_up_1_5pct | 22.6% |
| gap_up_2pct | 18.6% |
| hammer | 6.2% |
| head_shoulders_bottom_detected | 3.5% |
| head_shoulders_top_detected | 3.1% |
| house_cluster_buy | 4.2% |
| house_cluster_sell | 4.2% |
| htf_aligned_bear | 0.5% |
| htf_aligned_bull | 1.5% |
| htf_disagreement | 14.6% |
| hull_bearish | 42.5% |
| hull_bullish | 57.5% |
| hull_flip_dn | 1.1% |
| hull_flip_up | 1.6% |
| ichi_above_cloud | 38.5% |
| ichi_above_cloud_break_recent_5d | 22.4% |
| ichi_below_cloud | 32.5% |
| ichi_below_cloud_break_recent_5d | 18.6% |
| ichi_cloud_thick | 92.7% |
| ichi_tk_bearish | 37.2% |
| ichi_tk_bullish | 52.4% |
| ichi_tk_cross_dn | 3.1% |
| ichi_tk_cross_up | 2.6% |
| ichi_weekly_above_cloud | 34.9% |
| ichi_weekly_below_cloud | 44.6% |
| ichi_weekly_in_cloud | 20.5% |
| in_reversal_window | 1.4% |
| inside_bar | 15.0% |
| inside_cpr | 4.9% |
| inside_kc | 56.4% |
| insider_cluster_active | 10.7% |
| institutional_buy | 92.3% |
| institutional_negative | 3.5% |
| institutional_persistence_growing | 49.2% |
| institutional_persistence_strong | 63.0% |
| institutional_strong_buy | 84.1% |
| inverted_cup_handle_detected | 2.7% |
| is_friday | 21.5% |
| is_halloween_period | 57.8% |
| is_halloween_period_first_day | 0.5% |
| is_january | 10.8% |
| is_january_extended | 12.0% |
| is_monday | 21.2% |
| is_pre_holiday | 1.5% |
| is_summer_period | 42.2% |
| is_totm_window | 31.0% |
| is_totm_window_first_day | 7.8% |
| is_week_open | 23.9% |
| kc_touch_lower | 25.2% |
| kc_touch_upper | 30.3% |
| large_dollar_buy | 0.9% |
| macd_12_26_9_bearish | 42.9% |
| macd_12_26_9_bullish | 57.1% |
| macd_12_26_9_crossover_dn | 0.5% |
| macd_12_26_9_crossover_up | 1.1% |
| macd_8_21_5_bearish | 42.3% |
| macd_8_21_5_bullish | 57.7% |
| macd_8_21_5_crossover_dn | 1.8% |
| macd_8_21_5_crossover_up | 2.7% |
| marubozu_bear | 0.4% |
| marubozu_bull | 0.2% |
| mfi_broad_overbought | 27.2% |
| mfi_broad_oversold | 15.3% |
| mfi_overbought | 6.4% |
| mfi_oversold | 3.8% |
| monthly_above_sma_12 | 43.8% |
| monthly_above_sma_6 | 46.8% |
| monthly_bias_bear | 26.1% |
| monthly_bias_bull | 16.8% |
| monthly_momentum_pos | 44.6% |
| morning_star | 1.1% |
| near_avwap_20high_atr_05x | 27.9% |
| near_avwap_20high_atr_10x | 36.2% |
| near_avwap_20high_atr_15x | 53.7% |
| near_avwap_20high_atr_20x | 75.4% |
| near_avwap_20low_atr_05x | 17.4% |
| near_avwap_20low_atr_10x | 24.6% |
| near_avwap_20low_atr_15x | 36.5% |
| near_avwap_20low_atr_20x | 59.3% |
| near_avwap_252low_atr_05x | 4.7% |
| near_avwap_252low_atr_10x | 10.2% |
| near_avwap_252low_atr_15x | 18.4% |
| near_avwap_252low_atr_20x | 31.1% |
| near_avwap_50low_atr_05x | 9.8% |
| near_avwap_50low_atr_10x | 17.0% |
| near_avwap_50low_atr_15x | 24.3% |
| near_avwap_50low_atr_20x | 38.9% |
| near_cam_r3 | 11.3% |
| near_cam_s3 | 11.1% |
| near_cam_s4 | 4.9% |
| near_fib_236 | 6.0% |
| near_fib_382 | 3.8% |
| near_fib_500 | 3.3% |
| near_fib_618 | 2.2% |
| near_fib_786 | 5.7% |
| near_pivot | 14.1% |
| near_prev_close | 12.4% |
| near_prev_high | 8.2% |
| near_prev_low | 7.1% |
| near_r1 | 7.3% |
| near_r1_wide | 32.5% |
| near_r2 | 1.3% |
| near_r2_wide | 15.9% |
| near_s1 | 6.6% |
| near_s1_wide | 34.9% |
| near_s2 | 2.4% |
| near_s2_wide | 13.9% |
| near_s3 | 0.7% |
| near_wood_r1 | 8.2% |
| near_wood_s1 | 7.8% |
| news_uses_polygon_score | 28.6% |
| obv_bearish | 42.7% |
| obv_bullish | 57.3% |
| obv_diverge_bull | 4.7% |
| obv_falling | 43.4% |
| obv_rising | 56.6% |
| outside_bar | 6.8% |
| pead_negative_surprise | 19.6% |
| pead_positive_surprise | 26.0% |
| pin_bar | 18.1% |
| po3_accumulation_active | 11.5% |
| po3_bearish | 21.9% |
| po3_bullish | 15.9% |
| po3_manipulation_sweep_down | 4.0% |
| po3_manipulation_sweep_up | 5.3% |
| po3_mmbm_setup | 1.5% |
| po3_mmsm_setup | 1.8% |
| po3_sweep_above_prior_high | 51.5% |
| po3_sweep_below_prior_low | 43.4% |
| ppo_bullish | 56.6% |
| ppo_crossover_dn | 0.7% |
| ppo_crossover_up | 0.7% |
| pre_fomc_d0 | 3.3% |
| pre_fomc_d1 | 3.5% |
| pre_fomc_window | 6.8% |
| price_above_dema | 57.5% |
| price_above_ema_20 | 57.5% |
| price_above_ema_200 | 42.5% |
| price_above_ema_200_break_recent_5d | 7.7% |
| price_above_ema_20_break_recent_5d | 17.2% |
| price_above_ema_21 | 57.5% |
| price_above_ema_21_break_recent_5d | 17.2% |
| price_above_ema_50 | 57.1% |
| price_above_ema_50_break_recent_5d | 30.1% |
| price_above_ema_9 | 57.7% |
| price_above_ema_9_break_recent_5d | 19.7% |
| price_above_hull | 55.5% |
| price_above_sma_200 | 45.8% |
| price_above_sma_21 | 57.5% |
| price_above_sma_50 | 57.5% |
| price_above_tema | 53.3% |
| price_below_dema | 42.5% |
| price_below_hull | 44.5% |
| price_below_tema | 46.7% |
| psar_bullish | 57.1% |
| psar_flip_dn | 1.6% |
| psar_flip_up | 2.2% |
| r1_break_retest_long | 56.0% |
| recent_blowoff_at_r3 | 0.2% |
| resistance_break_retest | 44.2% |
| risk_off_regime_bond_signal | 24.6% |
| risk_off_regime_bond_signal_strong | 15.9% |
| risk_off_regime_gold_signal | 37.8% |
| risk_on_regime_bond_signal | 42.3% |
| risk_on_regime_bond_signal_strong | 21.4% |
| roc_positive | 57.3% |
| roc_turning_dn | 0.5% |
| roc_turning_up | 1.5% |
| rsi_14_bullish | 57.5% |
| rsi_14_cross_dn_overbought_recent_3d | 7.3% |
| rsi_14_cross_up_oversold_recent_3d | 7.1% |
| rsi_14_extreme_ob | 0.4% |
| rsi_14_overbought | 7.1% |
| rsi_14_oversold | 3.1% |
| rsi_14_rising | 51.3% |
| rsi_21_bullish | 57.5% |
| rsi_21_cross_dn_overbought_recent_3d | 0.4% |
| rsi_21_cross_up_oversold_recent_3d | 1.1% |
| rsi_21_extreme_ob | 0.2% |
| rsi_21_overbought | 0.7% |
| rsi_21_rising | 51.3% |
| rsi_2_bullish | 54.4% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 32.3% |
| rsi_2_cross_dn_overbought_recent_3d | 28.3% |
| rsi_2_cross_up_extreme_os_recent_3d | 25.2% |
| rsi_2_cross_up_oversold_recent_3d | 24.1% |
| rsi_2_extreme_ob | 31.4% |
| rsi_2_extreme_os | 20.4% |
| rsi_2_overbought | 39.8% |
| rsi_2_oversold | 29.0% |
| rsi_2_rising | 51.3% |
| rsi_9_bullish | 57.5% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 5.8% |
| rsi_9_cross_dn_overbought_recent_3d | 17.5% |
| rsi_9_cross_up_extreme_os_recent_3d | 5.7% |
| rsi_9_cross_up_oversold_recent_3d | 12.6% |
| rsi_9_extreme_ob | 4.6% |
| rsi_9_extreme_os | 0.7% |
| rsi_9_overbought | 31.9% |
| rsi_9_oversold | 23.5% |
| rsi_9_rising | 51.3% |
| s1_break_retest_short | 40.5% |
| sc_13d_filed_within_30d | 2.4% |
| sc_13g_filed_within_30d | 2.4% |
| sector_outperforming_spy | 57.1% |
| sector_underperforming_spy | 42.9% |
| shooting_star | 5.3% |
| sma_20_50_bullish | 54.4% |
| sma_20_50_golden_cross | 3.6% |
| sma_50_200_bullish | 42.9% |
| sma_9_21_bullish | 58.2% |
| sma_9_21_golden_cross | 2.6% |
| smc_bos_bearish | 8.2% |
| smc_bos_bullish | 10.8% |
| smc_bos_retest_long | 3.5% |
| smc_bos_retest_short | 3.8% |
| smc_breaker_block_bearish | 18.6% |
| smc_breaker_block_bullish | 24.1% |
| smc_choch_bearish | 3.5% |
| smc_choch_bullish | 2.7% |
| smc_equal_highs_swept | 2.7% |
| smc_equal_lows_swept | 3.3% |
| smc_fvg_bearish_active | 40.0% |
| smc_fvg_bullish_active | 53.8% |
| smc_fvg_retest_long_zone | 19.0% |
| smc_fvg_retest_short_zone | 15.7% |
| smc_in_discount_zone | 52.4% |
| smc_in_premium_zone | 62.8% |
| smc_inverse_fvg_bearish | 75.7% |
| smc_inverse_fvg_bullish | 83.8% |
| smc_liquidity_swept_dn | 2.0% |
| smc_liquidity_swept_up | 1.8% |
| smc_mitigation_block_long | 1.5% |
| smc_mitigation_block_short | 1.5% |
| smc_ob_bearish_active | 35.9% |
| smc_ob_bullish_active | 31.2% |
| smc_ote_long_zone | 7.1% |
| smc_ote_short_zone | 9.3% |
| squeeze_fire_dn | 0.9% |
| squeeze_fire_up | 0.4% |
| squeeze_in | 11.1% |
| squeeze_positive | 57.5% |
| stoch_bearish_cross | 18.8% |
| stoch_broad_overbought | 50.0% |
| stoch_broad_oversold | 34.5% |
| stoch_bullish_cross | 14.6% |
| stoch_overbought | 46.0% |
| stoch_oversold | 30.7% |
| stochrsi_cross_dn | 27.7% |
| stochrsi_cross_up | 21.4% |
| stochrsi_overbought | 41.4% |
| stochrsi_oversold | 32.7% |
| supertrend_bearish | 8.2% |
| supertrend_bullish | 91.8% |
| supertrend_flip_dn | 2.0% |
| supertrend_flip_recent_long_5d | 1.1% |
| supertrend_flip_recent_short_5d | 8.8% |
| support_break_retest | 31.8% |
| tema_above_dema | 57.1% |
| tema_cross_dn | 0.9% |
| tema_cross_up | 0.4% |
| three_white_soldiers | 0.2% |
| triangle_apex_break_retest_long | 18.1% |
| triangle_ascending_detected | 8.6% |
| triangle_descending_detected | 7.3% |
| uo_overbought | 2.0% |
| uo_oversold | 2.7% |
| usd_strengthening | 17.5% |
| usd_weakening | 11.3% |
| vix_band_high | 38.5% |
| vix_band_low | 31.8% |
| vix_band_mid | 29.7% |
| vix_term_backwardation | 11.1% |
| vix_term_contango | 88.9% |
| vol_spike_12x | 65.5% |
| vol_spike_15x | 36.1% |
| vol_spike_17x | 25.7% |
| vol_spike_2x | 17.3% |
| vol_spike_2x_on_down_day_recent_3d | 13.0% |
| vol_spike_2x_on_up_day_recent_3d | 9.9% |
| vol_spike_3x | 5.5% |
| vp_above_value_area | 36.3% |
| vp_below_value_area | 22.4% |
| vp_close_above_poc | 58.9% |
| vp_close_below_poc | 41.1% |
| vp_in_value_area | 41.2% |
| week_open_gap_down_15pct | 7.7% |
| week_open_gap_up_15pct | 4.4% |
| weekly_above_ema_10 | 57.1% |
| weekly_above_ema_20 | 48.4% |
| weekly_bias_bear | 33.6% |
| weekly_bias_bull | 39.1% |
| weekly_momentum_pos | 58.0% |
| williams_r_overbought | 34.1% |
| williams_r_oversold | 25.5% |
| williams_r_rising | 45.6% |
| within_pead_window | 42.4% |
| within_pre_rebalance_window | 4.5% |
| xs_avoid_high_ivol | 58.4% |
| xs_avoid_high_max | 64.3% |
| xs_high_beta_decile | 33.0% |
| xs_low_beta_bottom_quintile | 33.0% |
| xs_low_beta_decile | 13.1% |
| xs_low_beta_decile_entry_recent_5d | 1.1% |
| xs_low_beta_top_quintile | 13.1% |
| xs_momentum_bottom_decile | 27.8% |
| xs_momentum_bottom_quintile | 40.3% |
| xs_momentum_top_decile | 18.2% |
| xs_momentum_top_quintile | 27.8% |
| xs_quality_bottom_quintile | 22.8% |
| xs_quality_top_quintile | 21.1% |
| xs_quality_top_tercile | 40.1% |
| yoy_surprise_high | 49.6% |
| yoy_surprise_negative | 42.2% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 92.3% |
| committed_growth_holders | 92.3% |
| corp_donations_1y | 10.0% |
| corp_donations_count_1y | 10.0% |
| corp_donations_unique_pacs | 10.0% |
| cot_rut_commercials_pctile_3y | 54.4% |
| cot_rut_mmoney_pctile_3y | 54.4% |
| cup_handle_depth_pct | 6.6% |
| days_since_deletion | 10.2% |
| days_since_inclusion | 13.5% |
| days_to_next_holiday | 66.6% |
| days_to_rebalance | 12.2% |
| dpi_30d_avg | 95.1% |
| dpi_recent | 95.1% |
| earnings_announcement_return | 88.3% |
| earnings_eps_yoy_growth | 94.2% |
| gov_contracts_4q_sum | 39.4% |
| gov_contracts_last_qtr_amount | 39.4% |
| gov_contracts_qoq_growth | 39.4% |
| head_shoulders_magnitude_pct | 6.6% |
| insider_director_buyers_30d | 5.1% |
| insider_officer_buyers_30d | 5.1% |
| insider_total_shares_bought_30d | 5.1% |
| insider_unique_buyers_30d | 5.1% |
| inverted_cup_handle_height_pct | 8.6% |
| lobbying_amount_1y | 72.4% |
| lobbying_amount_q | 72.4% |
| lobbying_amount_yoy | 72.4% |
| monthly_momentum_6m | 97.8% |
| otc_short_ratio_recent | 95.1% |
| otc_volume_recent | 95.1% |
| pair_half_life | 91.4% |
| pair_max_abs_zscore | 91.4% |
| pair_zscore_signed | 91.4% |
| pct_from_avwap_20high | 61.5% |
| pct_from_avwap_20low | 73.5% |
| pct_from_avwap_252low | 98.0% |
| pct_from_avwap_50low | 85.8% |
| persistent_holders_4q | 92.3% |
| persistent_holders_8q | 92.3% |
| sc_13g_latest_percent_owned | 1.3% |
| search_volume_index_recent | 78.3% |
| search_volume_observations | 78.3% |
| search_volume_zscore_30d | 78.3% |
| sector_etf_return_20d | 2.6% |
| spy_return_20d | 2.6% |
| total_active_holders | 92.3% |
| triangle_breakdown_pct | 7.3% |
| triangle_breakout_pct | 8.6% |
| xs_quality_decile | 61.5% |
| xs_quality_gross_profitability | 61.5% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`atr` (0.952), `atr_14` (0.952), `avwap_20high` (0.998), `avwap_20low` (0.998), `avwap_252low` (0.993), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (1.0), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.996), `cam_r2` (0.996), `cam_r3` (0.996), `cam_r4` (0.996), `cam_s1` (0.996), `cam_s2` (0.996), `cam_s3` (0.996), `cam_s4` (0.995), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.996), `cpr_top` (0.997), `cup_handle_breakout_level` (0.997), `cup_handle_rim` (0.995), `dc10_lower` (0.998), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.998), `double_bottom_trough` (0.998), `double_top_neckline` (0.998), `double_top_peak` (0.999), `entry_stop_long` (0.994), `entry_stop_short` (0.996), `fib_236` (0.998), `fib_382` (0.999), `fib_500` (0.999), `fib_618` (0.999), `fib_786` (0.998), `fib_ext_127` (0.997), `fib_ext_162` (0.995), `head_shoulders_bottom_neckline` (0.998), `head_shoulders_top_neckline` (0.995), `hull_ma` (0.998), `ichi_kijun` (1.0), `ichi_senkou_a` (0.997), `ichi_senkou_b` (0.994), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.997), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.995), `monthly_sma_12` (0.976), `monthly_sma_6` (0.995), `pivot` (0.996), `prev_close` (0.996), `prev_high` (0.997), `prev_low` (0.996), `psar_value` (0.999), `r1` (0.996), `r2` (0.997), `r3` (0.996), `s1` (0.996), `s2` (0.995), `s3` (0.994), `supertrend_value` (0.994), `swing_high` (0.998), `swing_low` (0.997), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.997), `vp_value_area_high` (0.998), `vp_value_area_low` (0.997), `weekly_close` (0.995), `weekly_ema_10` (0.999), `weekly_ema_20` (0.996), `wood_p` (0.997), `wood_r1` (0.997), `wood_r2` (0.997), `wood_s1` (0.997), `wood_s2` (0.996), `year_high` (0.96), `year_low` (0.962)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | ema span (the 200 in above/below_ema_200 | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1 | ema span (the 200 in above/below_ema_200 | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P3.1 | volume ratio floor (vol / avg) | 4 | subset-safe | no - derives offline |
| P4 | rsi_14 < 40 | 3 | subset-safe | no - derives offline |
| P4.1 | rsi span | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P5 | rsi_14 > 60 | 3 | subset-safe | no - derives offline |
| P5.1 | rsi span | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P6 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     3 x 3 x 4 x 3 x 3 x 3 x 3 x 1 = 2916
offline gradings   36 level-combinations x 24 exits = 864
ENGINE RUNS        1 (actuated fire-adding axes only)
PENDING ACTUATION  81 level-combinations are DEFINED but have no env knob - they are a FEATURE REQUEST, not a runnable band (plan 11.0b state 1; B2866)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 617 census axes join it only when REGISTERED at the T3 band review.
