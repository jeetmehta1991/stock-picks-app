# Table A - news_momentum_short

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit fa06ebf3e at 2026-09-19 13:07:41 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** news_sentiment | **status:** NOT-STARTED | **R5 fires:** 13 | **surviving fires (T1):** 13 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  below_avwap_20high  <- backtest/signals/screener.py
       DEFN: close below the anchored-VWAP from the 20d high (avwap block)
       knobs P1.1-P1.1 (band rows in Table A)
P2  close_below_open  <- backtest/signals/screener.py +1
       DEFN: bar direction: close vs open (bar-anatomy block)
       knobs P2.1-P2.1 (band rows in Table A)
P3  close_in_bottom_40pct_of_range  <- backtest/signals/screener.py +1
       DEFN: close inside the top/bottom 40pct of the bar's range (technical.py:1682)
       knobs P3.1-P3.1 (band rows in Table A)
P4  dc20_breakout_dn  <- backtest/signals/screener.py
       DEFN: close beyond the prior-20d extreme with 0.2pct tolerance (technical.py:1470 region)
       knobs P4.1-P4.1 (band rows in Table A)
P5  vol_above_avg  <- backtest/signals/screener.py +1
       DEFN: volume / 20d average >= 1.0 (technical.py:1600)
       knobs P5.1-P5.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P6  news_sentiment_5d <= -0.3   [EXISTING-THRESHOLD]
P7  news_volume_zscore_5d >= 1.5   [EXISTING-THRESHOLD]
P8  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_news_momentum_short (docstring and return dropped):

```python
fires = s.get('news_sentiment_5d', 0.0) <= -0.3 and s.get('news_volume_zscore_5d', 0.0) >= 1.5 and s.get('dc20_breakout_dn', False) and s.get('close_below_open', False) and s.get('close_in_bottom_40pct_of_range', False) and s.get('vol_above_avg', False) and s.get('below_avwap_20high', False) and (not _short_borrow_trap_active(s))
sent = s.get('news_sentiment_5d', 0.0)
vz = s.get('news_volume_zscore_5d', 0.0)
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
| P1 | PRODUCER | below_avwap_20high - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close below the anchored-VWAP from the 20d high (avwap block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | buffer pct (price vs avwap anchored at 20d high) + anchor choice [20high, 50high, 252high] - backtest/signals/technical.py avwap block | BRACKET zero; strict inequality today | 0.0 | [0, 0.25, 0.5] | none - today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | close_below_open - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | bar direction: close vs open (bar-anatomy block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | mirror of close_above_open - technical.py bar-anatomy block | mirror | 0.0 | [0, 0.2, 0.5] pct | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | close_in_bottom_40pct_of_range - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close inside the top/bottom 40pct of the bar's range (technical.py:1682) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | mirror of top_40pct - backtest/signals/technical.py:1682 region | mirror | 0.4 | [0.25, 0.40, 0.50] | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | PRODUCER | dc20_breakout_dn - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close beyond the prior-20d extreme with 0.2pct tolerance (technical.py:1470 region) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P4.x) | BANDS-DEFINED |
| P4.1 | BAND | mirror of dc20_breakout_up - backtest/signals/technical.py:1470 region | mirror | 0.002 | [0, 0.002, 0.005, 0.01] | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | PRODUCER | vol_above_avg - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | volume / 20d average >= 1.0 (technical.py:1600) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P5.x) | BANDS-DEFINED |
| P5.1 | BAND | volume ratio floor (vol / avg) - backtest/signals/technical.py:1600 | BRACKET production 1.0; avg window is the second knob [10, 20, 50] | 1.0 | [1.0, 1.2, 1.5, 2.0] | TIGHTER floors where the vol ratio key is persisted on the fires; else none | LOOSER, and any window change; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P6 | STRATEGY | news_sentiment_5d `<= -0.3` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `<= -0.3` | production + 3 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P7 | STRATEGY | news_volume_zscore_5d `>= 1.5` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `>= 1.5` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P8 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | `<= -0.3` | 100.0% | TIGHTER = LOWER the ceiling: -1 -> 6 (46%); -0.6334 -> 8 (62%); -0.4454 -> 10 (77%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | `>= 1.5` | 100.0% | TIGHTER = RAISE the floor: 1.8767 -> 10 (77%); 3.8247 -> 9 (69%); 4.0249 -> 7 (54%); 4.2932 -> 3 (23%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 23.174, 24.114, 27.17, 30.494 | 23.174: 10 (77%); 24.114: 8 (62%); 27.17: 5 (38%); 30.494: 3 (23%) | 23.174: 3 (23%); 24.114: 5 (38%); 27.17: 8 (62%); 30.494: 10 (77%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 39.642, 40.078, 42.792, 47.468 | 39.642: 10 (77%); 40.078: 8 (62%); 42.792: 5 (38%); 47.468: 3 (23%) | 39.642: 3 (23%); 40.078: 5 (38%); 42.792: 8 (62%); 47.468: 10 (77%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 11.48, 14.354, 16.202, 18.824 | 11.48: 10 (77%); 14.354: 8 (62%); 16.202: 5 (38%); 18.824: 3 (23%) | 11.48: 3 (23%); 14.354: 5 (38%); 16.202: 8 (62%); 18.824: 10 (77%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -5.9864, -2.8577, -1.6871, -0.1416 | -5.9864: 10 (77%); -2.8577: 8 (62%); -1.6871: 5 (38%); -0.1416: 3 (23%) | -5.9864: 3 (23%); -2.8577: 5 (38%); -1.6871: 8 (62%); -0.1416: 10 (77%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 2.153, 2.8406, 3.9808, 7.4724 | 2.153: 10 (77%); 2.8406: 8 (62%); 3.9808: 5 (38%); 7.4724: 3 (23%) | 2.153: 3 (23%); 2.8406: 5 (38%); 3.9808: 8 (62%); 7.4724: 10 (77%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 2.153, 2.8406, 3.9808, 7.4724 | 2.153: 10 (77%); 2.8406: 8 (62%); 3.9808: 5 (38%); 7.4724: 3 (23%) | 2.153: 3 (23%); 2.8406: 5 (38%); 3.9808: 8 (62%); 7.4724: 10 (77%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 3.107, 4.1212, 5.4938, 6.2878 | 3.107: 10 (77%); 4.1212: 8 (62%); 5.4938: 5 (38%); 6.2878: 3 (23%) | 3.107: 3 (23%); 4.1212: 5 (38%); 5.4938: 8 (62%); 6.2878: 10 (77%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.1938, 0.2191, 0.2495, 0.3147 | 0.1938: 10 (77%); 0.2191: 8 (62%); 0.2495: 5 (38%); 0.3147: 3 (23%) | 0.1938: 3 (23%); 0.2191: 5 (38%); 0.2495: 8 (62%); 0.3147: 10 (77%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | -0.1672, -0.1482, -0.0257, 0.0331 | -0.1672: 10 (77%); -0.1482: 8 (62%); -0.0257: 5 (38%); 0.0331: 3 (23%) | -0.1672: 3 (23%); -0.1482: 5 (38%); -0.0257: 8 (62%); 0.0331: 10 (77%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.1305, 0.1582, 0.1917, 0.2339 | 0.1305: 10 (77%); 0.1582: 8 (62%); 0.1917: 5 (38%); 0.2339: 3 (23%) | 0.1305: 3 (23%); 0.1582: 5 (38%); 0.1917: 8 (62%); 0.2339: 10 (77%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.5105, -0.4407, -0.3655, -0.2116 | -0.5105: 10 (77%); -0.4407: 8 (62%); -0.3655: 5 (38%); -0.2116: 3 (23%) | -0.5105: 3 (23%); -0.4407: 5 (38%); -0.3655: 8 (62%); -0.2116: 10 (77%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.174, 0.2109, 0.2556, 0.3119 | 0.174: 10 (77%); 0.2109: 8 (62%); 0.2556: 5 (38%); 0.3119: 3 (23%) | 0.174: 3 (23%); 0.2109: 5 (38%); 0.2556: 8 (62%); 0.3119: 10 (77%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | -0.2578, -0.2055, -0.1491, -0.0338 | -0.2578: 10 (77%); -0.2055: 8 (62%); -0.1491: 5 (38%); -0.0338: 3 (23%) | -0.2578: 3 (23%); -0.2055: 5 (38%); -0.1491: 8 (62%); -0.0338: 10 (77%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0279, -0.0133, -0.0074, 0.003 | -0.0279: 10 (77%); -0.0133: 8 (62%); -0.0074: 5 (38%); 0.003: 3 (23%) | -0.0279: 3 (23%); -0.0133: 5 (38%); -0.0074: 8 (62%); 0.003: 10 (77%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1271, 0.131, 0.1345, 0.1555 | 0.1271: 10 (77%); 0.131: 8 (62%); 0.1345: 5 (38%); 0.1555: 3 (23%) | 0.1271: 3 (23%); 0.131: 5 (38%); 0.1345: 8 (62%); 0.1555: 10 (77%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 13 (100%) | 0: 12 (92%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.336, -0.2764, -0.1636, -0.0729 | -0.336: 10 (77%); -0.2764: 8 (62%); -0.1636: 5 (38%); -0.0729: 3 (23%) | -0.336: 3 (23%); -0.2764: 5 (38%); -0.1636: 8 (62%); -0.0729: 10 (77%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1, 1.6 | 0: 13 (100%); 1: 6 (46%); 1.6: 3 (23%) | 0: 7 (54%); 1: 10 (77%); 1.6: 10 (77%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.344, -0.265, -0.2483, -0.1729 | -0.344: 10 (77%); -0.265: 8 (62%); -0.2483: 5 (38%); -0.1729: 3 (23%) | -0.344: 3 (23%); -0.265: 5 (38%); -0.2483: 8 (62%); -0.1729: 10 (77%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.0128, 0.0475, 0.1692, 0.5192 | 0.0128: 11 (85%); 0.0475: 8 (62%); 0.1692: 5 (38%); 0.5192: 4 (31%) | 0.0128: 4 (31%); 0.0475: 5 (38%); 0.1692: 8 (62%); 0.5192: 11 (85%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.6039, 0.8705, 0.891, 0.9167 | 0.6039: 10 (77%); 0.8705: 8 (62%); 0.891: 7 (54%); 0.9167: 3 (23%) | 0.6039: 3 (23%); 0.8705: 5 (38%); 0.891: 9 (69%); 0.9167: 10 (77%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0917, -0.0619, -0.0131, 0.0305 | -0.0917: 10 (77%); -0.0619: 8 (62%); -0.0131: 5 (38%); 0.0305: 3 (23%) | -0.0917: 3 (23%); -0.0619: 5 (38%); -0.0131: 8 (62%); 0.0305: 10 (77%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3154, 0.4141, 0.5128, 0.6487 | 0.3154: 10 (77%); 0.4141: 8 (62%); 0.5128: 5 (38%); 0.6487: 3 (23%) | 0.3154: 3 (23%); 0.4141: 5 (38%); 0.5128: 8 (62%); 0.6487: 10 (77%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1128, 0.1987, 0.4051, 0.5744 | 0.1128: 10 (77%); 0.1987: 9 (69%); 0.4051: 5 (38%); 0.5744: 3 (23%) | 0.1128: 3 (23%); 0.1987: 6 (46%); 0.4051: 8 (62%); 0.5744: 10 (77%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.3009, 0.0058, 0.0849, 0.0957 | -0.3009: 10 (77%); 0.0058: 8 (62%); 0.0849: 5 (38%); 0.0957: 3 (23%) | -0.3009: 3 (23%); 0.0058: 5 (38%); 0.0849: 8 (62%); 0.0957: 10 (77%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3731, 0.6321, 0.7372, 0.85 | 0.3731: 10 (77%); 0.6321: 8 (62%); 0.7372: 6 (46%); 0.85: 3 (23%) | 0.3731: 3 (23%); 0.6321: 5 (38%); 0.7372: 9 (69%); 0.85: 10 (77%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2385, 0.4052, 0.4551, 0.8077 | 0.2385: 10 (77%); 0.4052: 8 (62%); 0.4551: 5 (38%); 0.8077: 3 (23%) | 0.2385: 3 (23%); 0.4052: 5 (38%); 0.4551: 8 (62%); 0.8077: 10 (77%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0507, -0.0119, 0 | -0.0507: 10 (77%); -0.0119: 8 (62%); 0: 7 (54%) | -0.0507: 3 (23%); -0.0119: 5 (38%); 0: 12 (92%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4731, 0.7052, 0.9936 | 0.4731: 10 (77%); 0.7052: 8 (62%); 0.9936: 6 (46%) | 0.4731: 3 (23%); 0.7052: 5 (38%); 0.9936: 12 (92%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0564, 0.1449, 0.2897, 0.609 | 0.0564: 10 (77%); 0.1449: 8 (62%); 0.2897: 5 (38%); 0.609: 4 (31%) | 0.0564: 3 (23%); 0.1449: 5 (38%); 0.2897: 8 (62%); 0.609: 11 (85%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0287, 0.0538, 0.1579, 0.4725 | -0.0287: 10 (77%); 0.0538: 8 (62%); 0.1579: 5 (38%); 0.4725: 3 (23%) | -0.0287: 3 (23%); 0.0538: 5 (38%); 0.1579: 8 (62%); 0.4725: 10 (77%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2423, 0.7948, 0.9295, 0.9679 | 0.2423: 10 (77%); 0.7948: 8 (62%); 0.9295: 5 (38%); 0.9679: 4 (31%) | 0.2423: 3 (23%); 0.7948: 5 (38%); 0.9295: 8 (62%); 0.9679: 11 (85%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0962, 0.3923, 0.5705, 0.7631 | 0.0962: 11 (85%); 0.3923: 8 (62%); 0.5705: 5 (38%); 0.7631: 3 (23%) | 0.0962: 4 (31%); 0.3923: 5 (38%); 0.5705: 8 (62%); 0.7631: 10 (77%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.071, 0.0787, 0.1439, 0.2097 | -0.071: 10 (77%); 0.0787: 8 (62%); 0.1439: 5 (38%); 0.2097: 3 (23%) | -0.071: 3 (23%); 0.0787: 5 (38%); 0.1439: 8 (62%); 0.2097: 10 (77%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2691, -0.0828, 0.1112, 0.2845 | -0.2691: 10 (77%); -0.0828: 8 (62%); 0.1112: 5 (38%); 0.2845: 3 (23%) | -0.2691: 3 (23%); -0.0828: 5 (38%); 0.1112: 8 (62%); 0.2845: 10 (77%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3102, 0.5243, 0.8897, 0.9923 | 0.3102: 10 (77%); 0.5243: 8 (62%); 0.8897: 5 (38%); 0.9923: 3 (23%) | 0.3102: 3 (23%); 0.5243: 5 (38%); 0.8897: 8 (62%); 0.9923: 10 (77%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0833, 0.1705, 0.4615, 0.7551 | 0.0833: 11 (85%); 0.1705: 8 (62%); 0.4615: 5 (38%); 0.7551: 3 (23%) | 0.0833: 4 (31%); 0.1705: 5 (38%); 0.4615: 8 (62%); 0.7551: 10 (77%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0743, 0.1336, 0.362, 1.287 | 0.0743: 10 (77%); 0.1336: 8 (62%); 0.362: 5 (38%); 1.287: 3 (23%) | 0.0743: 3 (23%); 0.1336: 5 (38%); 0.362: 8 (62%); 1.287: 10 (77%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 100.0% | 1, 33.8, 75, 139.8 | 1: 12 (92%); 33.8: 8 (62%); 75: 5 (38%); 139.8: 3 (23%) | 1: 5 (38%); 33.8: 5 (38%); 75: 8 (62%); 139.8: 10 (77%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 100.0% | 1.5441, 2.2846, 2.832, 3.3528 | 1.5441: 10 (77%); 2.2846: 8 (62%); 2.832: 5 (38%); 3.3528: 3 (23%) | 1.5441: 3 (23%); 2.2846: 5 (38%); 2.832: 8 (62%); 3.3528: 10 (77%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 7, 12, 14.2, 37.6 | 7: 11 (85%); 12: 9 (69%); 14.2: 5 (38%); 37.6: 3 (23%) | 7: 4 (31%); 12: 7 (54%); 14.2: 8 (62%); 37.6: 10 (77%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1.4, 2, 3, 4 | 1.4: 10 (77%); 2: 10 (77%); 3: 6 (46%); 4: 4 (31%) | 1.4: 3 (23%); 2: 7 (54%); 3: 9 (69%); 4: 13 (100%) | OFFLINE |
| dpi_30d_avg | backtest/signals/congressional_alt_data.py | 100.0% | 0.4562, 0.4665, 0.487, 0.525 | 0.4562: 10 (77%); 0.4665: 8 (62%); 0.487: 5 (38%); 0.525: 3 (23%) | 0.4562: 3 (23%); 0.4665: 5 (38%); 0.487: 8 (62%); 0.525: 10 (77%) | OFFLINE |
| dpi_recent | backtest/signals/congressional_alt_data.py | 100.0% | 0.3635, 0.4488, 0.4877, 0.5919 | 0.3635: 10 (77%); 0.4488: 8 (62%); 0.4877: 5 (38%); 0.5919: 3 (23%) | 0.3635: 3 (23%); 0.4488: 5 (38%); 0.4877: 8 (62%); 0.5919: 10 (77%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0074, 0.0093, 0.0139, 0.0171 | -0.0074: 10 (77%); 0.0093: 8 (62%); 0.0139: 6 (46%); 0.0171: 3 (23%) | -0.0074: 3 (23%); 0.0093: 5 (38%); 0.0139: 8 (62%); 0.0171: 10 (77%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 26.6274, 27.0587, 27.352, 27.518 | 26.6274: 10 (77%); 27.0587: 8 (62%); 27.352: 5 (38%); 27.518: 3 (23%) | 26.6274: 3 (23%); 27.0587: 5 (38%); 27.352: 8 (62%); 27.518: 10 (77%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | 0.527, 3.3082, 6.5222, 13.8892 | 0.527: 10 (77%); 3.3082: 8 (62%); 6.5222: 5 (38%); 13.8892: 3 (23%) | 0.527: 3 (23%); 3.3082: 5 (38%); 6.5222: 8 (62%); 13.8892: 10 (77%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -13.8892, -6.5222, -3.3082, -0.527 | -13.8892: 10 (77%); -6.5222: 8 (62%); -3.3082: 5 (38%); -0.527: 3 (23%) | -13.8892: 3 (23%); -6.5222: 5 (38%); -3.3082: 8 (62%); -0.527: 10 (77%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.1515, -0.0605, -0.0135, 0.0244 | -0.1515: 10 (77%); -0.0605: 8 (62%); -0.0135: 5 (38%); 0.0244: 3 (23%) | -0.1515: 3 (23%); -0.0605: 5 (38%); -0.0135: 8 (62%); 0.0244: 10 (77%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 5.6411, 6.2108, 8.393, 8.4823 | 5.6411: 10 (77%); 6.2108: 8 (62%); 8.393: 5 (38%); 8.4823: 3 (23%) | 5.6411: 3 (23%); 6.2108: 5 (38%); 8.393: 8 (62%); 8.4823: 10 (77%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 1 | 0: 13 (100%); 1: 4 (31%) | 0: 9 (69%); 1: 11 (85%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 0.6 | 0: 11 (85%); 0.6: 3 (23%) | 0: 10 (77%); 0.6: 10 (77%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 1 | 0: 13 (100%); 1: 4 (31%) | 0: 9 (69%); 1: 12 (92%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 4, 210.4, 286.4, 418.4 | 4: 11 (85%); 210.4: 8 (62%); 286.4: 5 (38%); 418.4: 3 (23%) | 4: 4 (31%); 210.4: 5 (38%); 286.4: 8 (62%); 418.4: 10 (77%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 18.6, 74.8, 121, 132.2 | 18.6: 10 (77%); 74.8: 8 (62%); 121: 5 (38%); 132.2: 3 (23%) | 18.6: 3 (23%); 74.8: 5 (38%); 121: 8 (62%); 132.2: 10 (77%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -2.8378, -1.6804, -1.4713, -0.9785 | -2.8378: 10 (77%); -1.6804: 8 (62%); -1.4713: 5 (38%); -0.9785: 3 (23%) | -2.8378: 3 (23%); -1.6804: 5 (38%); -1.4713: 8 (62%); -0.9785: 10 (77%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -2.7733, -1.2326, -0.6842, 0.6587 | -2.7733: 10 (77%); -1.2326: 8 (62%); -0.6842: 5 (38%); 0.6587: 3 (23%) | -2.7733: 3 (23%); -1.2326: 5 (38%); -0.6842: 8 (62%); 0.6587: 10 (77%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.6659, -0.2727, 0.8456, 2.5331 | -1.6659: 10 (77%); -0.2727: 8 (62%); 0.8456: 5 (38%); 2.5331: 3 (23%) | -1.6659: 3 (23%); -0.2727: 5 (38%); 0.8456: 8 (62%); 2.5331: 10 (77%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -3.9022, -1.395, -1.2437, -1.065 | -3.9022: 10 (77%); -1.395: 8 (62%); -1.2437: 5 (38%); -1.065: 3 (23%) | -3.9022: 3 (23%); -1.395: 5 (38%); -1.2437: 8 (62%); -1.065: 10 (77%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -5.0694, -2.4606, -1.5911, -0.9958 | -5.0694: 10 (77%); -2.4606: 8 (62%); -1.5911: 5 (38%); -0.9958: 3 (23%) | -5.0694: 3 (23%); -2.4606: 5 (38%); -1.5911: 8 (62%); -0.9958: 10 (77%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -2.2938, -0.7336, -0.3117, 0.3422 | -2.2938: 10 (77%); -0.7336: 8 (62%); -0.3117: 5 (38%); 0.3422: 3 (23%) | -2.2938: 3 (23%); -0.7336: 5 (38%); -0.3117: 8 (62%); 0.3422: 10 (77%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 24.104, 29.878, 30.66, 33.582 | 24.104: 10 (77%); 29.878: 8 (62%); 30.66: 5 (38%); 33.582: 3 (23%) | 24.104: 3 (23%); 29.878: 5 (38%); 30.66: 8 (62%); 33.582: 10 (77%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 100.0% | -0.3073, -0.2014, -0.1041, -0.0307 | -0.3073: 10 (77%); -0.2014: 8 (62%); -0.1041: 5 (38%); -0.0307: 3 (23%) | -0.3073: 3 (23%); -0.2014: 5 (38%); -0.1041: 8 (62%); -0.0307: 10 (77%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 100.0% | 0.0257, 0.0503, 0.1146, 0.2804 | 0.0257: 10 (77%); 0.0503: 8 (62%); 0.1146: 5 (38%); 0.2804: 3 (23%) | 0.0257: 3 (23%); 0.0503: 5 (38%); 0.1146: 8 (62%); 0.2804: 10 (77%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 1.4, 2, 4, 5 | 1.4: 10 (77%); 2: 10 (77%); 4: 6 (46%); 5: 4 (31%) | 1.4: 3 (23%); 2: 6 (46%); 4: 9 (69%); 5: 11 (85%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0.5, 0.6667, 0.8, 1 | 0.5: 12 (92%); 0.6667: 9 (69%); 0.8: 5 (38%); 1: 5 (38%) | 0.5: 4 (31%); 0.6667: 6 (46%); 0.8: 8 (62%); 1: 13 (100%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1543, 0.3 | 0: 13 (100%); 0.1543: 5 (38%); 0.3: 3 (23%) | 0: 7 (54%); 0.1543: 8 (62%); 0.3: 10 (77%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 1.4, 2, 4 | 1.4: 10 (77%); 2: 10 (77%); 4: 6 (46%) | 1.4: 3 (23%); 2: 7 (54%); 4: 11 (85%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 1.4, 2, 4, 5 | 1.4: 10 (77%); 2: 10 (77%); 4: 6 (46%); 5: 4 (31%) | 1.4: 3 (23%); 2: 6 (46%); 4: 9 (69%); 5: 11 (85%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2 | 0: 13 (100%); 1: 6 (46%); 2: 4 (31%) | 0: 7 (54%); 1: 9 (69%); 2: 11 (85%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | -0.4333, -0.1667, 0, 0.03 | -0.4333: 10 (77%); -0.1667: 8 (62%); 0: 7 (54%); 0.03: 3 (23%) | -0.4333: 3 (23%); -0.1667: 5 (38%); 0: 10 (77%); 0.03: 10 (77%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | -1, -0.6571, -0.4667, -0.3133 | -1: 13 (100%); -0.6571: 8 (62%); -0.4667: 5 (38%); -0.3133: 3 (23%) | -1: 5 (38%); -0.6571: 5 (38%); -0.4667: 8 (62%); -0.3133: 10 (77%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | -1, -0.6571, -0.4667, -0.3133 | -1: 13 (100%); -0.6571: 8 (62%); -0.4667: 5 (38%); -0.3133: 3 (23%) | -1: 5 (38%); -0.6571: 5 (38%); -0.4667: 8 (62%); -0.3133: 10 (77%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.7, -0.04, 0 | -0.7: 10 (77%); -0.04: 8 (62%); 0: 8 (62%) | -0.7: 3 (23%); -0.04: 5 (38%); 0: 13 (100%) | OFFLINE |
| otc_short_ratio_recent | backtest/signals/congressional_alt_data.py | 100.0% | 0.3635, 0.4488, 0.4877, 0.5919 | 0.3635: 10 (77%); 0.4488: 8 (62%); 0.4877: 5 (38%); 0.5919: 3 (23%) | 0.3635: 3 (23%); 0.4488: 5 (38%); 0.4877: 8 (62%); 0.5919: 10 (77%) | OFFLINE |
| otc_volume_recent | backtest/signals/congressional_alt_data.py | 100.0% | 1412352.4, 3007487, 5381186.2, 11586394 | 1412352.4: 10 (77%); 3007487: 8 (62%); 5381186.2: 5 (38%); 11586394: 3 (23%) | 1412352.4: 3 (23%); 3007487: 5 (38%); 5381186.2: 8 (62%); 11586394: 10 (77%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 3.4, 4.8, 6.4, 11.4 | 3.4: 10 (77%); 4.8: 8 (62%); 6.4: 5 (38%); 11.4: 3 (23%) | 3.4: 3 (23%); 4.8: 5 (38%); 6.4: 8 (62%); 11.4: 10 (77%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.1832, -0.1696, -0.1597, -0.1277 | -0.1832: 10 (77%); -0.1696: 8 (62%); -0.1597: 5 (38%); -0.1277: 3 (23%) | -0.1832: 3 (23%); -0.1696: 5 (38%); -0.1597: 8 (62%); -0.1277: 10 (77%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.2512, -0.1709, -0.1411, -0.099 | -0.2512: 10 (77%); -0.1709: 8 (62%); -0.1411: 5 (38%); -0.099: 3 (23%) | -0.2512: 3 (23%); -0.1709: 5 (38%); -0.1411: 8 (62%); -0.099: 10 (77%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.1876, -0.1642, -0.1197, -0.0965 | -0.1876: 10 (77%); -0.1642: 8 (62%); -0.1197: 5 (38%); -0.0965: 3 (23%) | -0.1876: 3 (23%); -0.1642: 5 (38%); -0.1197: 8 (62%); -0.0965: 10 (77%) | OFFLINE |
| pct_from_avwap_20high | backtest/signals/screener.py | 100.0% | -16.1124, -11.6476, -9.7726, -8.2944 | -16.1124: 10 (77%); -11.6476: 8 (62%); -9.7726: 5 (38%); -8.2944: 3 (23%) | -16.1124: 3 (23%); -11.6476: 5 (38%); -9.7726: 8 (62%); -8.2944: 10 (77%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -30.9106, -22.3548, -14.0616, 5.6378 | -30.9106: 10 (77%); -22.3548: 8 (62%); -14.0616: 5 (38%); 5.6378: 3 (23%) | -30.9106: 3 (23%); -22.3548: 5 (38%); -14.0616: 8 (62%); 5.6378: 10 (77%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0646, 0.0751, 0.09, 0.1155 | 0.0646: 10 (77%); 0.0751: 8 (62%); 0.09: 5 (38%); 0.1155: 3 (23%) | 0.0646: 3 (23%); 0.0751: 5 (38%); 0.09: 8 (62%); 0.1155: 10 (77%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.0713, 0.0965, 0.1254, 0.2653 | 0.0713: 10 (77%); 0.0965: 8 (62%); 0.1254: 5 (38%); 0.2653: 3 (23%) | 0.0713: 3 (23%); 0.0965: 5 (38%); 0.1254: 8 (62%); 0.2653: 10 (77%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -4.1628, -2.6252, -0.8467, 0.6397 | -4.1628: 10 (77%); -2.6252: 8 (62%); -0.8467: 5 (38%); 0.6397: 3 (23%) | -4.1628: 3 (23%); -2.6252: 5 (38%); -0.8467: 8 (62%); 0.6397: 10 (77%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -2.0561, -1.794, -1.5657, -1.2234 | -2.0561: 10 (77%); -1.794: 8 (62%); -1.5657: 5 (38%); -1.2234: 3 (23%) | -2.0561: 3 (23%); -1.794: 5 (38%); -1.5657: 8 (62%); -1.2234: 10 (77%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -2.4226, -0.921, 0.7349, 2.2002 | -2.4226: 10 (77%); -0.921: 8 (62%); 0.7349: 5 (38%); 2.2002: 3 (23%) | -2.4226: 3 (23%); -0.921: 5 (38%); 0.7349: 8 (62%); 2.2002: 10 (77%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -19.9934, -17.1652, -16.407, -13.676 | -19.9934: 10 (77%); -17.1652: 8 (62%); -16.407: 5 (38%); -13.676: 3 (23%) | -19.9934: 3 (23%); -17.1652: 5 (38%); -16.407: 8 (62%); -13.676: 10 (77%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 24.566, 27.278, 29.452, 32.098 | 24.566: 10 (77%); 27.278: 8 (62%); 29.452: 5 (38%); 32.098: 3 (23%) | 24.566: 3 (23%); 27.278: 5 (38%); 29.452: 8 (62%); 32.098: 10 (77%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 0.952, 2.402, 2.93, 3.664 | 0.952: 10 (77%); 2.402: 8 (62%); 2.93: 5 (38%); 3.664: 3 (23%) | 0.952: 3 (23%); 2.402: 5 (38%); 2.93: 8 (62%); 3.664: 10 (77%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 31.542, 31.976, 34.684, 38.276 | 31.542: 10 (77%); 31.976: 8 (62%); 34.684: 5 (38%); 38.276: 3 (23%) | 31.542: 3 (23%); 31.976: 5 (38%); 34.684: 8 (62%); 38.276: 10 (77%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 16.648, 19.814, 22.506, 24.156 | 16.648: 10 (77%); 19.814: 8 (62%); 22.506: 5 (38%); 24.156: 3 (23%) | 16.648: 3 (23%); 19.814: 5 (38%); 22.506: 8 (62%); 24.156: 10 (77%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0308, 0.0386, 0.0491, 0.0898 | 0.0308: 10 (77%); 0.0386: 8 (62%); 0.0491: 5 (38%); 0.0898: 3 (23%) | 0.0308: 3 (23%); 0.0386: 5 (38%); 0.0491: 8 (62%); 0.0898: 10 (77%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0562, -0.0447, -0.0402, -0.0313 | -0.0562: 10 (77%); -0.0447: 8 (62%); -0.0402: 5 (38%); -0.0313: 3 (23%) | -0.0562: 3 (23%); -0.0447: 5 (38%); -0.0402: 8 (62%); -0.0313: 10 (77%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 13 (100%) | 0: 12 (92%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 100.0% | 60.6, 73.6, 78.2, 79 | 60.6: 10 (77%); 73.6: 8 (62%); 78.2: 5 (38%); 79: 5 (38%) | 60.6: 3 (23%); 73.6: 5 (38%); 78.2: 8 (62%); 79: 12 (92%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 100.0% | 0.0246, 0.0353, 0.0473, 0.0591 | 0.0246: 10 (77%); 0.0353: 8 (62%); 0.0473: 5 (38%); 0.0591: 3 (23%) | 0.0246: 3 (23%); 0.0353: 5 (38%); 0.0473: 8 (62%); 0.0591: 10 (77%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.01, 0.015, 0.0574, 0.2566 | 0.01: 10 (77%); 0.015: 8 (62%); 0.0574: 5 (38%); 0.2566: 3 (23%) | 0.01: 3 (23%); 0.015: 5 (38%); 0.0574: 8 (62%); 0.2566: 10 (77%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 17.34, 50.84, 75.58, 122.4 | 17.34: 10 (77%); 50.84: 8 (62%); 75.58: 5 (38%); 122.4: 3 (23%) | 17.34: 3 (23%); 50.84: 5 (38%); 75.58: 8 (62%); 122.4: 10 (77%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -21.426, -13.063, -8.346, -6.181 | -21.426: 10 (77%); -13.063: 8 (62%); -8.346: 5 (38%); -6.181: 3 (23%) | -21.426: 3 (23%); -13.063: 5 (38%); -8.346: 8 (62%); -6.181: 10 (77%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 11.116, 22.598, 29.456, 38.982 | 11.116: 10 (77%); 22.598: 8 (62%); 29.456: 5 (38%); 38.982: 3 (23%) | 11.116: 3 (23%); 22.598: 5 (38%); 29.456: 8 (62%); 38.982: 10 (77%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 9.452, 12.774, 20.766, 27.234 | 9.452: 10 (77%); 12.774: 8 (62%); 20.766: 5 (38%); 27.234: 3 (23%) | 9.452: 3 (23%); 12.774: 5 (38%); 20.766: 8 (62%); 27.234: 10 (77%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 0.668, 2.648, 7.088, 22.004 | 0.668: 10 (77%); 2.648: 8 (62%); 7.088: 5 (38%); 22.004: 3 (23%) | 0.668: 3 (23%); 2.648: 5 (38%); 7.088: 8 (62%); 22.004: 10 (77%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 0.282 | 0: 13 (100%); 0.282: 3 (23%) | 0: 10 (77%); 0.282: 10 (77%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 8, 9.6, 16.2 | 5: 11 (85%); 8: 9 (69%); 9.6: 5 (38%); 16.2: 3 (23%) | 5: 4 (31%); 8: 6 (46%); 9.6: 8 (62%); 16.2: 10 (77%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 6.8, 11.6, 14.2, 17.2 | 6.8: 10 (77%); 11.6: 8 (62%); 14.2: 5 (38%); 17.2: 3 (23%) | 6.8: 3 (23%); 11.6: 5 (38%); 14.2: 8 (62%); 17.2: 10 (77%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 22.396, 31.364, 36.288, 38.334 | 22.396: 10 (77%); 31.364: 8 (62%); 36.288: 5 (38%); 38.334: 3 (23%) | 22.396: 3 (23%); 31.364: 5 (38%); 36.288: 8 (62%); 38.334: 10 (77%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.4349, 0.5064, 0.8429, 0.9277 | 0.4349: 10 (77%); 0.5064: 8 (62%); 0.8429: 5 (38%); 0.9277: 3 (23%) | 0.4349: 3 (23%); 0.5064: 5 (38%); 0.8429: 8 (62%); 0.9277: 10 (77%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 16.814, 16.928, 18.156, 22.734 | 16.814: 10 (77%); 16.928: 8 (62%); 18.156: 5 (38%); 22.734: 3 (23%) | 16.814: 3 (23%); 16.928: 5 (38%); 18.156: 8 (62%); 22.734: 10 (77%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 16.814, 16.928, 18.156, 22.734 | 16.814: 10 (77%); 16.928: 8 (62%); 18.156: 5 (38%); 22.734: 3 (23%) | 16.814: 3 (23%); 16.928: 5 (38%); 18.156: 8 (62%); 22.734: 10 (77%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8495, 0.8572, 0.956, 0.9778 | 0.8495: 10 (77%); 0.8572: 8 (62%); 0.956: 5 (38%); 0.9778: 3 (23%) | 0.8495: 3 (23%); 0.8572: 5 (38%); 0.956: 8 (62%); 0.9778: 10 (77%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 1.53, 1.666, 3.284, 5.14 | 1.53: 11 (85%); 1.666: 8 (62%); 3.284: 5 (38%); 5.14: 3 (23%) | 1.53: 5 (38%); 1.666: 5 (38%); 3.284: 8 (62%); 5.14: 10 (77%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0766, 0.1142, 0.1705, 0.2721 | 0.0766: 10 (77%); 0.1142: 8 (62%); 0.1705: 5 (38%); 0.2721: 3 (23%) | 0.0766: 3 (23%); 0.1142: 5 (38%); 0.1705: 8 (62%); 0.2721: 10 (77%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 55.0302, 82.266, 96.2393, 182.1765 | 55.0302: 10 (77%); 82.266: 8 (62%); 96.2393: 5 (38%); 182.1765: 3 (23%) | 55.0302: 3 (23%); 82.266: 5 (38%); 96.2393: 8 (62%); 182.1765: 10 (77%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 51.731, 77.2694, 88.5484, 177.0421 | 51.731: 10 (77%); 77.2694: 8 (62%); 88.5484: 5 (38%); 177.0421: 3 (23%) | 51.731: 3 (23%); 77.2694: 5 (38%); 88.5484: 8 (62%); 177.0421: 10 (77%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 48.4318, 69.6793, 84.0324, 171.9077 | 48.4318: 10 (77%); 69.6793: 8 (62%); 84.0324: 5 (38%); 171.9077: 3 (23%) | 48.4318: 3 (23%); 69.6793: 5 (38%); 84.0324: 8 (62%); 171.9077: 10 (77%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 58.3293, 87.2625, 107.0067, 187.311 | 58.3293: 10 (77%); 87.2625: 8 (62%); 107.0067: 5 (38%); 187.311: 3 (23%) | 58.3293: 3 (23%); 87.2625: 5 (38%); 107.0067: 8 (62%); 187.311: 10 (77%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 13 (100%) | 0: 12 (92%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.2945, -0.1842, -0.1503, -0.097 | -0.2945: 10 (77%); -0.1842: 8 (62%); -0.1503: 5 (38%); -0.097: 3 (23%) | -0.2945: 3 (23%); -0.1842: 5 (38%); -0.1503: 8 (62%); -0.097: 10 (77%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -98.738, -98.254, -97.178, -95.624 | -98.738: 10 (77%); -98.254: 8 (62%); -97.178: 5 (38%); -95.624: 3 (23%) | -98.738: 3 (23%); -98.254: 5 (38%); -97.178: 8 (62%); -95.624: 10 (77%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 100.0% | 0.7672, 0.9858, 1.2079, 1.5881 | 0.7672: 10 (77%); 0.9858: 8 (62%); 1.2079: 5 (38%); 1.5881: 3 (23%) | 0.7672: 3 (23%); 0.9858: 5 (38%); 1.2079: 8 (62%); 1.5881: 10 (77%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 100.0% | 4.4, 6.8, 8, 9.6 | 4.4: 10 (77%); 6.8: 8 (62%); 8: 7 (54%); 9.6: 3 (23%) | 4.4: 3 (23%); 6.8: 5 (38%); 8: 9 (69%); 9.6: 10 (77%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 100.0% | 0.3236, 0.386, 0.484, 0.5427 | 0.3236: 10 (77%); 0.386: 8 (62%); 0.484: 5 (38%); 0.5427: 3 (23%) | 0.3236: 3 (23%); 0.386: 5 (38%); 0.484: 8 (62%); 0.5427: 10 (77%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 100.0% | 8, 8.8, 10 | 8: 11 (85%); 8.8: 8 (62%); 10: 6 (46%) | 8: 5 (38%); 8.8: 5 (38%); 10: 13 (100%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 100.0% | 0.0228, 0.0262, 0.0472, 0.0712 | 0.0228: 10 (77%); 0.0262: 8 (62%); 0.0472: 5 (38%); 0.0712: 3 (23%) | 0.0228: 3 (23%); 0.0262: 5 (38%); 0.0472: 8 (62%); 0.0712: 10 (77%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 100.0% | 2.4, 5.6, 7.2, 9 | 2.4: 10 (77%); 5.6: 8 (62%); 7.2: 5 (38%); 9: 4 (31%) | 2.4: 3 (23%); 5.6: 5 (38%); 7.2: 8 (62%); 9: 11 (85%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 100.0% | -0.1856, -0.0912, 0.0823, 0.1491 | -0.1856: 10 (77%); -0.0912: 8 (62%); 0.0823: 5 (38%); 0.1491: 3 (23%) | -0.1856: 3 (23%); -0.0912: 5 (38%); 0.0823: 8 (62%); 0.1491: 10 (77%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 100.0% | 2, 2.8, 3.4, 7.6 | 2: 11 (85%); 2.8: 8 (62%); 3.4: 5 (38%); 7.6: 3 (23%) | 2: 5 (38%); 2.8: 5 (38%); 3.4: 8 (62%); 7.6: 10 (77%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| above_avwap_252low | 15.4% |
| above_vwap | 23.1% |
| adx_cross_up | 15.4% |
| adx_trending | 53.8% |
| ao_cross_dn | 23.1% |
| ao_positive | 23.1% |
| at_key_fib | 7.7% |
| at_key_fib_wide | 7.7% |
| avwap_20high_loss_recent_3d | 23.1% |
| avwap_252low_loss_recent_3d | 50.0% |
| bb_10_20_pctb_lt_05 | 84.6% |
| bb_10_20_pctb_lt_1 | 84.6% |
| bb_10_20_reclaim_from_lower_recent_3d | 7.7% |
| bb_10_20_touch_lower | 69.2% |
| bb_20_20_reclaim_from_lower_recent_3d | 7.7% |
| bb_20_20_touch_lower | 92.3% |
| below_avwap_252low | 84.6% |
| below_cam_s4 | 84.6% |
| below_ema_200 | 92.3% |
| below_ema_200_break_recent_5d | 30.8% |
| below_ema_20_break_recent_5d | 53.8% |
| below_ema_21_break_recent_5d | 53.8% |
| below_ema_50_break_recent_5d | 46.2% |
| below_ema_9_break_recent_5d | 69.2% |
| below_prev_low_clearance_atr_05 | 76.9% |
| below_s1 | 84.6% |
| below_s2 | 61.5% |
| below_sma_200 | 84.6% |
| below_vwap | 76.9% |
| break_52w_low | 30.8% |
| chandelier_long_flip_dn | 30.8% |
| cmf_cross_dn | 23.1% |
| cpr_narrow | 84.6% |
| cpr_narrow_tight | 23.1% |
| dc10_strong_breakout_dn | 76.9% |
| dc20_support_break_retest_strong | 46.2% |
| defensive_leadership | 38.5% |
| director_only_buy | 8.3% |
| double_top_detected | 15.4% |
| dpi_elevated | 38.5% |
| ema_20_50_bearish | 61.5% |
| ema_20_50_bullish | 38.5% |
| ema_20_50_death_cross | 7.7% |
| ema_50_200_bearish | 53.8% |
| ema_50_200_bullish | 46.2% |
| ema_9_21_bearish | 84.6% |
| ema_9_21_bullish | 15.4% |
| ema_9_21_death_cross | 15.4% |
| evening_star | 7.7% |
| flag_bear_broke | 7.7% |
| force_index_cross_dn | 15.4% |
| gap_dn_1_5pct | 69.2% |
| gap_dn_2pct | 61.5% |
| head_shoulders_top_detected | 7.7% |
| htf_aligned_bear | 76.9% |
| hull_flip_dn | 23.1% |
| ichi_above_cloud | 7.7% |
| ichi_below_cloud | 84.6% |
| ichi_below_cloud_break_recent_5d | 46.2% |
| ichi_cloud_thick | 92.3% |
| ichi_tk_bearish | 69.2% |
| ichi_tk_cross_dn | 7.7% |
| ichi_weekly_above_cloud | 15.4% |
| ichi_weekly_below_cloud | 76.9% |
| ichi_weekly_in_cloud | 7.7% |
| inside_kc | 7.7% |
| institutional_buy | 84.6% |
| institutional_negative | 15.4% |
| institutional_persistence_growing | 83.3% |
| institutional_persistence_strong | 91.7% |
| institutional_strong_buy | 84.6% |
| is_friday | 30.8% |
| is_halloween_period | 69.2% |
| is_january | 23.1% |
| is_january_extended | 30.8% |
| is_monday | 7.7% |
| is_summer_period | 30.8% |
| is_totm_window | 30.8% |
| is_totm_window_first_day | 7.7% |
| is_week_open | 7.7% |
| kc_touch_lower | 92.3% |
| macd_12_26_9_crossover_dn | 23.1% |
| macd_8_21_5_crossover_dn | 23.1% |
| mfi_broad_oversold | 38.5% |
| mfi_oversold | 7.7% |
| monthly_above_sma_12 | 23.1% |
| monthly_above_sma_6 | 7.7% |
| monthly_bias_bear | 76.9% |
| monthly_bias_bull | 7.7% |
| monthly_momentum_pos | 15.4% |
| near_52w_low | 38.5% |
| near_52w_low_105pct | 53.8% |
| near_avwap_20high_atr_20x | 23.1% |
| near_avwap_252low_atr_05x | 12.5% |
| near_avwap_252low_atr_10x | 25.0% |
| near_avwap_252low_atr_15x | 37.5% |
| near_avwap_252low_atr_20x | 62.5% |
| near_avwap_50low_atr_10x | 25.0% |
| near_avwap_50low_atr_15x | 50.0% |
| near_cam_s3 | 7.7% |
| near_cam_s4 | 7.7% |
| near_fib_618 | 7.7% |
| near_fib_786 | 7.7% |
| near_s1 | 15.4% |
| near_s1_wide | 38.5% |
| near_s2 | 7.7% |
| near_s2_wide | 30.8% |
| news_uses_polygon_score | 92.3% |
| pead_negative_surprise | 45.5% |
| pead_positive_surprise | 9.1% |
| po3_accumulation_active | 7.7% |
| po3_manipulation_sweep_down | 7.7% |
| ppo_crossover_dn | 23.1% |
| pre_fomc_d0 | 7.7% |
| pre_fomc_window | 7.7% |
| price_above_ema_200 | 7.7% |
| price_above_sma_200 | 15.4% |
| psar_flip_dn | 23.1% |
| risk_off_regime_bond_signal | 7.7% |
| risk_off_regime_gold_signal | 23.1% |
| risk_on_regime_bond_signal | 30.8% |
| risk_on_regime_bond_signal_strong | 15.4% |
| roc_turning_dn | 23.1% |
| rsi_14_extreme_os | 7.7% |
| rsi_14_oversold | 61.5% |
| rsi_21_oversold | 7.7% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 23.1% |
| rsi_2_cross_dn_overbought_recent_3d | 38.5% |
| rsi_9_cross_dn_overbought_recent_3d | 15.4% |
| rsi_9_extreme_os | 38.5% |
| rsi_9_oversold | 92.3% |
| s1_break_retest_short | 92.3% |
| sc_13g_filed_within_30d | 7.7% |
| sma_20_50_bullish | 53.8% |
| sma_50_200_bullish | 30.8% |
| sma_9_21_bullish | 23.1% |
| smc_bos_bearish | 23.1% |
| smc_bos_retest_long | 15.4% |
| smc_breaker_block_bearish | 30.8% |
| smc_breaker_block_bullish | 15.4% |
| smc_choch_bearish | 7.7% |
| smc_equal_lows_swept | 23.1% |
| smc_fvg_bearish_active | 92.3% |
| smc_fvg_bullish_active | 30.8% |
| smc_fvg_retest_long_zone | 15.4% |
| smc_fvg_retest_short_zone | 15.4% |
| smc_in_premium_zone | 7.7% |
| smc_inverse_fvg_bullish | 38.5% |
| smc_mitigation_block_long | 7.7% |
| smc_ob_bearish_active | 53.8% |
| smc_ob_bullish_active | 7.7% |
| smc_ote_long_zone | 7.7% |
| squeeze_fire_dn | 15.4% |
| stoch_bearish_cross | 38.5% |
| stoch_broad_oversold | 69.2% |
| stoch_oversold | 53.8% |
| stochrsi_cross_dn | 7.7% |
| stochrsi_cross_up | 7.7% |
| stochrsi_oversold | 92.3% |
| supertrend_bearish | 61.5% |
| supertrend_bullish | 38.5% |
| supertrend_flip_dn | 46.2% |
| supertrend_flip_recent_long_5d | 7.7% |
| supertrend_flip_recent_short_5d | 61.5% |
| support_break_retest | 53.8% |
| tema_above_dema | 7.7% |
| tema_cross_dn | 7.7% |
| three_black_crows | 30.8% |
| uo_oversold | 38.5% |
| usd_strengthening | 15.4% |
| vix_band_high | 46.2% |
| vix_band_low | 15.4% |
| vix_band_mid | 38.5% |
| vix_term_backwardation | 15.4% |
| vix_term_contango | 84.6% |
| vol_spike_15x | 84.6% |
| vol_spike_17x | 61.5% |
| vol_spike_2x | 53.8% |
| vol_spike_2x_on_down_day_recent_3d | 30.8% |
| vol_spike_2x_on_up_day_recent_3d | 7.7% |
| vol_spike_3x | 46.2% |
| vp_below_value_area | 69.2% |
| vp_close_above_poc | 7.7% |
| vp_close_below_poc | 92.3% |
| vp_in_value_area | 30.8% |
| week_open_gap_down_15pct | 7.7% |
| weekly_above_ema_20 | 7.7% |
| weekly_bias_bear | 92.3% |
| williams_r_rising | 30.8% |
| within_pead_window | 53.8% |
| xs_avoid_high_ivol | 38.5% |
| xs_avoid_high_max | 69.2% |
| xs_high_beta_decile | 30.8% |
| xs_low_beta_bottom_quintile | 30.8% |
| xs_momentum_bottom_decile | 15.4% |
| xs_momentum_bottom_quintile | 38.5% |
| xs_momentum_top_decile | 7.7% |
| xs_momentum_top_quintile | 7.7% |
| xs_quality_bottom_quintile | 28.6% |
| xs_quality_top_quintile | 28.6% |
| xs_quality_top_tercile | 28.6% |
| yoy_surprise_high | 33.3% |
| yoy_surprise_negative | 50.0% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 92.3% |
| committed_growth_holders | 92.3% |
| cot_rut_commercials_pctile_3y | 92.3% |
| cot_rut_mmoney_pctile_3y | 92.3% |
| days_since_deletion | 23.1% |
| days_to_next_holiday | 84.6% |
| earnings_announcement_return | 84.6% |
| earnings_eps_yoy_growth | 92.3% |
| gov_contracts_4q_sum | 23.1% |
| gov_contracts_last_qtr_amount | 23.1% |
| gov_contracts_qoq_growth | 23.1% |
| lobbying_amount_1y | 53.8% |
| lobbying_amount_q | 53.8% |
| lobbying_amount_yoy | 53.8% |
| pair_half_life | 92.3% |
| pair_max_abs_zscore | 92.3% |
| pair_zscore_signed | 92.3% |
| pct_from_avwap_252low | 61.5% |
| persistent_holders_4q | 92.3% |
| persistent_holders_8q | 92.3% |
| search_volume_index_recent | 69.2% |
| search_volume_observations | 69.2% |
| search_volume_zscore_30d | 69.2% |
| total_active_holders | 92.3% |
| xs_quality_decile | 53.8% |
| xs_quality_gross_profitability | 53.8% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.995), `avwap_20low` (0.995), `avwap_252low` (0.995), `avwap_50low` (0.995), `bb_10_20_lower` (0.995), `bb_10_20_mid` (0.995), `bb_10_20_upper` (0.989), `bb_20_15_lower` (1.0), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.995), `bb_20_20_lower` (0.995), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.995), `cam_r1` (0.984), `cam_r2` (0.984), `cam_r3` (0.984), `cam_r4` (0.984), `cam_s1` (0.984), `cam_s2` (0.984), `cam_s3` (0.984), `cam_s4` (0.984), `chandelier_long_value` (1.0), `chandelier_short_value` (0.995), `cpr_bottom` (0.984), `cpr_top` (0.995), `cup_handle_breakout_level` (1.0), `cup_handle_depth_pct` (1.0), `cup_handle_rim` (1.0), `days_since_inclusion` (1.0), `days_to_rebalance` (-1.0), `dc10_lower` (0.995), `dc10_mid` (0.995), `dc10_upper` (0.989), `dc20_lower` (0.995), `dc20_mid` (0.995), `dc20_upper` (0.995), `dema` (0.989), `double_top_neckline` (1.0), `double_top_peak` (1.0), `entry_stop_long` (0.989), `entry_stop_short` (0.995), `fib_236` (1.0), `fib_382` (1.0), `fib_500` (1.0), `fib_618` (0.995), `fib_786` (0.995), `fib_ext_127` (0.984), `fib_ext_162` (0.973), `hull_ma` (0.995), `ichi_kijun` (0.995), `ichi_senkou_a` (0.989), `ichi_senkou_b` (0.973), `ichi_tenkan` (0.995), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.995), `monthly_sma_12` (0.973), `monthly_sma_6` (0.989), `pct_from_avwap_50low` (-1.0), `pivot` (0.984), `prev_close` (0.984), `prev_high` (0.995), `prev_low` (0.995), `psar_value` (0.995), `r1` (0.984), `r2` (0.984), `r3` (0.984), `s1` (0.984), `s2` (0.995), `s3` (0.995), `supertrend_value` (0.973), `swing_high` (0.995), `swing_low` (0.995), `tema` (0.995), `vp_poc` (0.962), `vp_value_area_high` (0.984), `vp_value_area_low` (0.962), `vwap_upper_2` (0.956), `weekly_close` (0.995), `weekly_ema_10` (0.995), `weekly_ema_20` (0.989), `wood_p` (0.995), `wood_r1` (0.995), `wood_r2` (0.995), `wood_s1` (0.995), `wood_s2` (0.995), `year_high` (0.973), `year_low` (0.973)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | buffer pct (price vs avwap anchored at 2 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1 | mirror of close_above_open | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P3.1 | mirror of top_40pct | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P4.1 | mirror of dc20_breakout_up | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P5.1 | volume ratio floor (vol / avg) | 1 | subset-safe | no - derives offline |
| P6 | news_sentiment_5d <= -0.3 | 4 | subset-safe | no - derives offline |
| P7 | news_volume_zscore_5d >= 1.5 | 5 | subset-safe | no - derives offline |
| P8 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     1 x 1 x 1 x 1 x 1 x 4 x 5 x 1 = 20
offline gradings   20 level-combinations x 24 exits = 480
ENGINE RUNS        1 (every fire-adding axis sits at production-only until its env actuator exists)
check              1 x 20 = 20
```

B-row candidates NOT in this factorial: 331 census axes join it only when REGISTERED at the T3 band review.
