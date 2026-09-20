# Table A - news_momentum_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit f55b7c1e7 at 2026-09-19 23:26:39 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** news_sentiment | **status:** NOT-STARTED | **R5 fires:** 113 | **surviving fires (T1):** 113 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  close_above_open  <- backtest/signals/screener.py +1
       DEFN: bar direction: close vs open (bar-anatomy block)
       knobs P1.1-P1.1 (band rows in Table A)
P2  close_in_top_40pct_of_range  <- backtest/signals/screener.py +1
       DEFN: close inside the top/bottom 40pct of the bar's range (technical.py:1682)
       knobs P2.1-P2.1 (band rows in Table A)
P3  dc20_breakout_up  <- backtest/signals/screener.py
       DEFN: close beyond the prior-20d extreme with 0.2pct tolerance (technical.py:1470 region)
       knobs P3.1-P3.1 (band rows in Table A)
P4  vol_above_avg  <- backtest/signals/screener.py +1
       DEFN: volume / 20d average >= 1.0 (technical.py:1600)
       knobs P4.1-P4.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P5  news_sentiment_5d >= 0.3   [EXISTING-THRESHOLD]
P6  news_volume_zscore_5d >= 0.9091   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_news_momentum_long (docstring and return dropped):

```python
fires = s.get('news_sentiment_5d', 0.0) >= 0.3 and s.get('news_volume_zscore_5d', 0.0) >= 0.90909 and s.get('dc20_breakout_up', False) and s.get('close_above_open', False) and s.get('close_in_top_40pct_of_range', False) and s.get('vol_above_avg', False)
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
| P1 | PRODUCER | close_above_open - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | bar direction: close vs open (bar-anatomy block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | (structural) c > o - optional min body pct - backtest/signals/technical.py bar-anatomy block | BRACKET zero | 0.0 | [0, 0.2, 0.5] pct | none - bar OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | close_in_top_40pct_of_range - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close inside the top/bottom 40pct of the bar's range (technical.py:1682) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | range-position cutoff - backtest/signals/technical.py:1682 | BRACKET production 0.40 | 0.4 | [0.25, 0.40, 0.50] | none - bar OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | dc20_breakout_up - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | close beyond the prior-20d extreme with 0.2pct tolerance (technical.py:1470 region) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | breakout tolerance (close >= upper * (1-t)) - backtest/signals/technical.py:1470 region | BRACKET production 0.2pct (B591 1pct variant exists for dc10 only) | 0.002 | [0, 0.002, 0.005, 0.01] | none - close unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | PRODUCER | vol_above_avg - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | volume / 20d average >= 1.0 (technical.py:1600) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P4.x) | BANDS-DEFINED |
| P4.1 | BAND | volume ratio floor (vol / avg) - backtest/signals/technical.py:1600 | BRACKET production 1.0; avg window is the second knob [10, 20, 50] | 1.0 | [1.0, 1.2, 1.5, 2.0] | TIGHTER floors where the vol ratio key is persisted on the fires; else none | LOOSER, and any window change; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | STRATEGY | news_sentiment_5d `>= 0.3` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `>= 0.3` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P6 | STRATEGY | news_volume_zscore_5d `>= 0.9091` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `>= 0.9091` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | `>= 0.3` | 100.0% | TIGHTER = RAISE the floor: 0.3755 -> 90 (80%); 0.5 -> 69 (61%); 0.6256 -> 45 (40%); 0.8979 -> 23 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | `>= 0.9091` | 100.0% | TIGHTER = RAISE the floor: 1.7889 -> 92 (81%); 2.4223 -> 68 (60%); 3.7461 -> 45 (40%); 5.2629 -> 23 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 17.2, 20.222, 22.332, 25.358 | 17.2: 90 (80%); 20.222: 68 (60%); 22.332: 45 (40%); 25.358: 23 (20%) | 17.2: 23 (20%); 20.222: 45 (40%); 22.332: 68 (60%); 25.358: 90 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 14.112, 17.488, 19.072, 21.706 | 14.112: 90 (80%); 17.488: 68 (60%); 19.072: 45 (40%); 21.706: 23 (20%) | 14.112: 23 (20%); 17.488: 45 (40%); 19.072: 68 (60%); 21.706: 90 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 28.69, 30.862, 34.464, 38.312 | 28.69: 90 (80%); 30.862: 68 (60%); 34.464: 45 (40%); 38.312: 23 (20%) | 28.69: 23 (20%); 30.862: 45 (40%); 34.464: 68 (60%); 38.312: 90 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -0.4588, 1.0485, 2.5405, 6.7101 | -0.4588: 90 (80%); 1.0485: 68 (60%); 2.5405: 45 (40%); 6.7101: 23 (20%) | -0.4588: 23 (20%); 1.0485: 45 (40%); 2.5405: 68 (60%); 6.7101: 90 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.203, 2.5386, 3.9282, 5.9916 | 1.203: 90 (80%); 2.5386: 68 (60%); 3.9282: 45 (40%); 5.9916: 23 (20%) | 1.203: 23 (20%); 2.5386: 45 (40%); 3.9282: 68 (60%); 5.9916: 90 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.203, 2.5386, 3.9282, 5.9916 | 1.203: 90 (80%); 2.5386: 68 (60%); 3.9282: 45 (40%); 5.9916: 23 (20%) | 1.203: 23 (20%); 2.5386: 45 (40%); 3.9282: 68 (60%); 5.9916: 90 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.3256, 2.6152, 2.9942, 3.9308 | 2.3256: 90 (80%); 2.6152: 68 (60%); 2.9942: 45 (40%); 3.9308: 23 (20%) | 2.3256: 23 (20%); 2.6152: 45 (40%); 2.9942: 68 (60%); 3.9308: 90 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0909, 0.1216, 0.1562, 0.2088 | 0.0909: 90 (80%); 0.1216: 68 (60%); 0.1562: 45 (40%); 0.2088: 23 (20%) | 0.0909: 23 (20%); 0.1216: 45 (40%); 0.1562: 68 (60%); 0.2088: 90 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.9245, 0.9636, 1.0239, 1.0968 | 0.9245: 90 (80%); 0.9636: 68 (60%); 1.0239: 45 (40%); 1.0968: 23 (20%) | 0.9245: 23 (20%); 0.9636: 45 (40%); 1.0239: 68 (60%); 1.0968: 90 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0682, 0.0923, 0.1145, 0.1536 | 0.0682: 90 (80%); 0.0923: 68 (60%); 0.1145: 45 (40%); 0.1536: 23 (20%) | 0.0682: 23 (20%); 0.0923: 45 (40%); 0.1145: 68 (60%); 0.1536: 90 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 1.16, 1.2475, 1.3238, 1.4206 | 1.16: 90 (80%); 1.2475: 68 (60%); 1.3238: 45 (40%); 1.4206: 23 (20%) | 1.16: 23 (20%); 1.2475: 45 (40%); 1.3238: 68 (60%); 1.4206: 90 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0909, 0.1232, 0.1526, 0.2048 | 0.0909: 90 (80%); 0.1232: 68 (60%); 0.1526: 45 (40%); 0.2048: 23 (20%) | 0.0909: 23 (20%); 0.1232: 45 (40%); 0.1526: 68 (60%); 0.2048: 90 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.995, 1.0606, 1.1179, 1.1905 | 0.995: 90 (80%); 1.0606: 68 (60%); 1.1179: 45 (40%); 1.1905: 23 (20%) | 0.995: 23 (20%); 1.0606: 45 (40%); 1.1179: 68 (60%); 1.1905: 90 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0644, -0.0314, -0.0132, -0.0016 | -0.0644: 90 (80%); -0.0314: 69 (61%); -0.0132: 45 (40%); -0.0016: 23 (20%) | -0.0644: 23 (20%); -0.0314: 50 (44%); -0.0132: 68 (60%); -0.0016: 90 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.161, 0.2242, 0.2599, 0.29 | 0.161: 90 (80%); 0.2242: 68 (60%); 0.2599: 45 (40%); 0.29: 21 (19%) | 0.161: 23 (20%); 0.2242: 45 (40%); 0.2599: 68 (60%); 0.29: 92 (81%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 113 (100%) | 0: 112 (99%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | 0.0495, 0.1077, 0.1813, 0.2551 | 0.0495: 90 (80%); 0.1077: 68 (60%); 0.1813: 45 (40%); 0.2551: 23 (20%) | 0.0495: 23 (20%); 0.1077: 45 (40%); 0.1813: 68 (60%); 0.2551: 90 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 113 (100%); 1: 38 (34%) | 0: 75 (66%); 1: 93 (82%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.232, -0.1668, -0.1097, -0.0949 | -0.232: 90 (80%); -0.1668: 70 (62%); -0.1097: 45 (40%); -0.0949: 27 (24%) | -0.232: 23 (20%); -0.1668: 48 (42%); -0.1097: 68 (60%); -0.0949: 101 (89%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5628, 0.6731, 0.7577, 0.7949 | 0.5628: 90 (80%); 0.6731: 69 (61%); 0.7577: 45 (40%); 0.7949: 36 (32%) | 0.5628: 23 (20%); 0.6731: 51 (45%); 0.7577: 68 (60%); 0.7949: 93 (82%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1923, 0.2782, 0.3384, 0.7218 | 0.1923: 102 (90%); 0.2782: 68 (60%); 0.3384: 45 (40%); 0.7218: 23 (20%) | 0.1923: 26 (23%); 0.2782: 45 (40%); 0.3384: 68 (60%); 0.7218: 90 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0078, 0.1587, 0.2556, 0.3775 | -0.0078: 90 (80%); 0.1587: 68 (60%); 0.2556: 45 (40%); 0.3775: 26 (23%) | -0.0078: 23 (20%); 0.1587: 45 (40%); 0.2556: 68 (60%); 0.3775: 103 (91%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4513, 0.7166, 0.9038, 0.9487 | 0.4513: 90 (80%); 0.7166: 68 (60%); 0.9038: 48 (42%); 0.9487: 28 (25%) | 0.4513: 23 (20%); 0.7166: 45 (40%); 0.9038: 70 (62%); 0.9487: 102 (90%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0974, 0.3462, 0.5398, 0.6026 | 0.0974: 90 (80%); 0.3462: 71 (63%); 0.5398: 45 (40%); 0.6026: 30 (27%) | 0.0974: 23 (20%); 0.3462: 47 (42%); 0.5398: 68 (60%); 0.6026: 98 (87%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.6296, -0.5034, -0.4263, -0.2046 | -0.6296: 97 (86%); -0.5034: 68 (60%); -0.4263: 49 (43%); -0.2046: 23 (20%) | -0.6296: 31 (27%); -0.5034: 45 (40%); -0.4263: 69 (61%); -0.2046: 90 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2436, 0.3, 0.4949, 0.6923 | 0.2436: 96 (85%); 0.3: 68 (60%); 0.4949: 45 (40%); 0.6923: 25 (22%) | 0.2436: 33 (29%); 0.3: 45 (40%); 0.4949: 68 (60%); 0.6923: 91 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1602, 0.4615, 0.5192, 0.7628 | 0.1602: 90 (80%); 0.4615: 70 (62%); 0.5192: 54 (48%); 0.7628: 26 (23%) | 0.1602: 23 (20%); 0.4615: 58 (51%); 0.5192: 71 (63%); 0.7628: 91 (81%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0628, -0.0535, -0.0412, -0.0254 | -0.0628: 91 (81%); -0.0535: 69 (61%); -0.0412: 56 (50%); -0.0254: 25 (22%) | -0.0628: 24 (21%); -0.0535: 46 (41%); -0.0412: 72 (64%); -0.0254: 92 (81%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.609, 0.8103, 0.9038, 0.9103 | 0.609: 91 (81%); 0.8103: 68 (60%); 0.9038: 54 (48%); 0.9103: 34 (30%) | 0.609: 24 (21%); 0.8103: 45 (40%); 0.9038: 79 (70%); 0.9103: 92 (81%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0321, 0.1269, 0.2384, 0.7667 | 0.0321: 107 (95%); 0.1269: 68 (60%); 0.2384: 45 (40%); 0.7667: 23 (20%) | 0.0321: 38 (34%); 0.1269: 45 (40%); 0.2384: 68 (60%); 0.7667: 90 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0088, 0.0424, 0.0546, 0.0927 | 0.0088: 90 (80%); 0.0424: 69 (61%); 0.0546: 45 (40%); 0.0927: 23 (20%) | 0.0088: 23 (20%); 0.0424: 59 (52%); 0.0546: 68 (60%); 0.0927: 90 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.6042, 0.8764, 0.9351, 0.9612 | 0.6042: 90 (80%); 0.8764: 72 (64%); 0.9351: 47 (42%); 0.9612: 23 (20%) | 0.6042: 23 (20%); 0.8764: 56 (50%); 0.9351: 71 (63%); 0.9612: 90 (80%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1083, 0.3577, 0.6247, 0.7584 | 0.1083: 90 (80%); 0.3577: 68 (60%); 0.6247: 45 (40%); 0.7584: 23 (20%) | 0.1083: 23 (20%); 0.3577: 45 (40%); 0.6247: 68 (60%); 0.7584: 90 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, 0.0606, 0.1876, 0.3175 | -0.0812: 102 (90%); 0.0606: 68 (60%); 0.1876: 46 (41%); 0.3175: 36 (32%) | -0.0812: 24 (21%); 0.0606: 45 (40%); 0.1876: 75 (66%); 0.3175: 112 (99%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1436, -0.0039, 0.0494, 0.0916 | -0.1436: 91 (81%); -0.0039: 72 (64%); 0.0494: 45 (40%); 0.0916: 27 (24%) | -0.1436: 25 (22%); -0.0039: 53 (47%); 0.0494: 68 (60%); 0.0916: 101 (89%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3461, 0.6512, 0.75, 0.8731 | 0.3461: 90 (80%); 0.6512: 68 (60%); 0.75: 48 (42%); 0.8731: 23 (20%) | 0.3461: 23 (20%); 0.6512: 45 (40%); 0.75: 70 (62%); 0.8731: 90 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1987, 0.2846, 0.4821, 0.8064 | 0.1987: 96 (85%); 0.2846: 68 (60%); 0.4821: 45 (40%); 0.8064: 23 (20%) | 0.1987: 29 (26%); 0.2846: 45 (40%); 0.4821: 68 (60%); 0.8064: 90 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0713, 0.1762, 0.3786, 0.6857 | 0.0713: 90 (80%); 0.1762: 68 (60%); 0.3786: 45 (40%); 0.6857: 23 (20%) | 0.0713: 23 (20%); 0.1762: 45 (40%); 0.3786: 68 (60%); 0.6857: 90 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 100.0% | 3, 73.8, 82.4, 91 | 3: 92 (81%); 73.8: 68 (60%); 82.4: 45 (40%); 91: 26 (23%) | 3: 24 (21%); 73.8: 45 (40%); 82.4: 68 (60%); 91: 91 (81%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.1% | 1.6963, 2.2112, 2.9333, 4.0547 | 1.6963: 89 (79%); 2.2112: 67 (59%); 2.9333: 45 (40%); 4.0547: 23 (20%) | 1.6963: 23 (20%); 2.2112: 45 (40%); 2.9333: 67 (59%); 4.0547: 89 (79%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 7, 13, 22, 40 | 7: 94 (83%); 13: 69 (61%); 22: 47 (42%); 40: 27 (24%) | 7: 29 (26%); 13: 47 (42%); 22: 69 (61%); 40: 94 (83%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3, 4 | 1: 104 (92%); 2: 82 (73%); 3: 59 (52%); 4: 34 (30%) | 1: 31 (27%); 2: 54 (48%); 3: 79 (70%); 4: 113 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0139, -0.0044, 0.0125, 0.0215 | -0.0139: 90 (80%); -0.0044: 69 (61%); 0.0125: 47 (42%); 0.0215: 23 (20%) | -0.0139: 23 (20%); -0.0044: 46 (41%); 0.0125: 72 (64%); 0.0215: 90 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.363, 24.5871, 25.6734, 26.6088 | 24.363: 91 (81%); 24.5871: 70 (62%); 25.6734: 47 (42%); 26.6088: 23 (20%) | 24.363: 24 (21%); 24.5871: 47 (42%); 25.6734: 69 (61%); 26.6088: 90 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -2.8964, -1.0544, -0.394, 0 | -2.8964: 90 (80%); -1.0544: 68 (60%); -0.394: 45 (40%); 0: 24 (21%) | -2.8964: 23 (20%); -1.0544: 45 (40%); -0.394: 68 (60%); 0: 92 (81%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | 0, 0.394, 1.0544, 2.8964 | 0: 92 (81%); 0.394: 68 (60%); 1.0544: 45 (40%); 2.8964: 23 (20%) | 0: 24 (21%); 0.394: 45 (40%); 1.0544: 68 (60%); 2.8964: 90 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0398, -0.003, 0.018, 0.0616 | -0.0398: 90 (80%); -0.003: 68 (60%); 0.018: 45 (40%); 0.0616: 23 (20%) | -0.0398: 23 (20%); -0.003: 45 (40%); 0.018: 68 (60%); 0.0616: 90 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.146, 8.5192, 8.8222, 9.1937 | 8.146: 90 (80%); 8.5192: 68 (60%); 8.8222: 46 (41%); 9.1937: 25 (22%) | 8.146: 23 (20%); 8.5192: 45 (40%); 8.8222: 67 (59%); 9.1937: 88 (78%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 112 (99%); 1: 37 (33%) | 0: 75 (66%); 1: 99 (88%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.1% | -1, 0 | -1: 106 (94%); 0: 85 (75%) | -1: 27 (24%); 0: 93 (82%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 112 (99%); 1: 41 (36%) | 0: 71 (63%); 1: 95 (84%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 1, 3, 5.2, 135.6 | 1: 98 (87%); 3: 77 (68%); 5.2: 45 (40%); 135.6: 23 (20%) | 1: 28 (25%); 3: 47 (42%); 5.2: 68 (60%); 135.6: 90 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 0, 1, 4, 74 | 0: 113 (100%); 1: 79 (70%); 4: 46 (41%); 74: 24 (21%) | 0: 34 (30%); 1: 50 (44%); 4: 72 (64%); 74: 91 (81%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | 0.3457, 0.8554, 1.437, 2.126 | 0.3457: 90 (80%); 0.8554: 68 (60%); 1.437: 45 (40%); 2.126: 23 (20%) | 0.3457: 23 (20%); 0.8554: 45 (40%); 1.437: 68 (60%); 2.126: 90 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -0.4308, 0.127, 0.9047, 1.8104 | -0.4308: 90 (80%); 0.127: 68 (60%); 0.9047: 45 (40%); 1.8104: 23 (20%) | -0.4308: 23 (20%); 0.127: 45 (40%); 0.9047: 68 (60%); 1.8104: 90 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.6735, -0.4368, -0.0266, 0.5487 | -1.6735: 90 (80%); -0.4368: 68 (60%); -0.0266: 45 (40%); 0.5487: 23 (20%) | -1.6735: 23 (20%); -0.4368: 45 (40%); -0.0266: 68 (60%); 0.5487: 90 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | 0.3147, 0.7284, 1.3131, 1.8925 | 0.3147: 90 (80%); 0.7284: 68 (60%); 1.3131: 45 (40%); 1.8925: 23 (20%) | 0.3147: 23 (20%); 0.7284: 45 (40%); 1.3131: 68 (60%); 1.8925: 90 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | 0.2172, 0.9142, 1.8095, 3.4825 | 0.2172: 90 (80%); 0.9142: 68 (60%); 1.8095: 45 (40%); 3.4825: 23 (20%) | 0.2172: 23 (20%); 0.9142: 45 (40%); 1.8095: 68 (60%); 3.4825: 90 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -0.4357, 0.2021, 0.6215, 1.845 | -0.4357: 90 (80%); 0.2021: 68 (60%); 0.6215: 45 (40%); 1.845: 23 (20%) | -0.4357: 23 (20%); 0.2021: 45 (40%); 0.6215: 68 (60%); 1.845: 90 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 56.162, 62.158, 67.136, 72.654 | 56.162: 90 (80%); 62.158: 68 (60%); 67.136: 45 (40%); 72.654: 23 (20%) | 56.162: 23 (20%); 62.158: 45 (40%); 67.136: 68 (60%); 72.654: 90 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 100.0% | 0.0124, 0.0233, 0.0352, 0.0537 | 0.0124: 90 (80%); 0.0233: 68 (60%); 0.0352: 45 (40%); 0.0537: 23 (20%) | 0.0124: 23 (20%); 0.0233: 45 (40%); 0.0352: 68 (60%); 0.0537: 90 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 3, 6, 11.2, 20 | 3: 100 (88%); 6: 72 (64%); 11.2: 45 (40%); 20: 24 (21%) | 3: 24 (21%); 6: 51 (45%); 11.2: 68 (60%); 20: 91 (81%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.046, 0.125 | 0: 113 (100%); 0.046: 45 (40%); 0.125: 25 (22%) | 0: 66 (58%); 0.046: 68 (60%); 0.125: 93 (82%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0.4594, 0.5402, 0.6667, 0.8333 | 0.4594: 90 (80%); 0.5402: 68 (60%); 0.6667: 47 (42%); 0.8333: 24 (21%) | 0.4594: 23 (20%); 0.5402: 45 (40%); 0.6667: 74 (65%); 0.8333: 92 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 3, 5, 9, 16.6 | 3: 94 (83%); 5: 72 (64%); 9: 47 (42%); 16.6: 23 (20%) | 3: 30 (27%); 5: 50 (44%); 9: 70 (62%); 16.6: 90 (80%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 3, 6, 11.2, 20 | 3: 100 (88%); 6: 72 (64%); 11.2: 45 (40%); 20: 24 (21%) | 3: 24 (21%); 6: 51 (45%); 11.2: 68 (60%); 20: 91 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 1, 2, 4, 8.6 | 1: 93 (82%); 2: 74 (65%); 4: 48 (42%); 8.6: 23 (20%) | 1: 39 (35%); 2: 50 (44%); 4: 72 (64%); 8.6: 90 (80%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.2715, 0.3614, 0.4591, 0.5864 | 0.2715: 90 (80%); 0.3614: 68 (60%); 0.4591: 45 (40%); 0.5864: 23 (20%) | 0.2715: 23 (20%); 0.3614: 45 (40%); 0.4591: 68 (60%); 0.5864: 90 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0.3322, 0.4377, 0.6, 0.7578 | 0.3322: 90 (80%); 0.4377: 68 (60%); 0.6: 46 (41%); 0.7578: 23 (20%) | 0.3322: 23 (20%); 0.4377: 45 (40%); 0.6: 72 (64%); 0.7578: 90 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0.3322, 0.4377, 0.6, 0.7578 | 0.3322: 90 (80%); 0.4377: 68 (60%); 0.6: 46 (41%); 0.7578: 23 (20%) | 0.3322: 23 (20%); 0.4377: 45 (40%); 0.6: 72 (64%); 0.7578: 90 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.0252, 0, 0.2307, 0.5 | -0.0252: 90 (80%); 0: 88 (78%); 0.2307: 45 (40%); 0.5: 25 (22%) | -0.0252: 23 (20%); 0: 47 (42%); 0.2307: 68 (60%); 0.5: 92 (81%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 3, 5, 8, 11.6 | 3: 91 (81%); 5: 73 (65%); 8: 48 (42%); 11.6: 23 (20%) | 3: 33 (29%); 5: 46 (41%); 8: 77 (68%); 11.6: 90 (80%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | 0.0629, 0.089, 0.1211, 0.1606 | 0.0629: 90 (80%); 0.089: 68 (60%); 0.1211: 45 (40%); 0.1606: 23 (20%) | 0.0629: 23 (20%); 0.089: 45 (40%); 0.1211: 68 (60%); 0.1606: 90 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | 0.0524, 0.0871, 0.1162, 0.1479 | 0.0524: 90 (80%); 0.0871: 68 (60%); 0.1162: 45 (40%); 0.1479: 23 (20%) | 0.0524: 23 (20%); 0.0871: 45 (40%); 0.1162: 68 (60%); 0.1479: 90 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | 0.0434, 0.066, 0.0942, 0.1339 | 0.0434: 90 (80%); 0.066: 68 (60%); 0.0942: 45 (40%); 0.1339: 23 (20%) | 0.0434: 23 (20%); 0.066: 45 (40%); 0.0942: 68 (60%); 0.1339: 90 (80%) | OFFLINE |
| pct_from_avwap_20low | (not found by literal grep) | 99.1% | 4.8854, 6.5556, 7.8086, 11.2122 | 4.8854: 89 (79%); 6.5556: 67 (59%); 7.8086: 45 (40%); 11.2122: 23 (20%) | 4.8854: 23 (20%); 6.5556: 45 (40%); 7.8086: 67 (59%); 11.2122: 89 (79%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 99.1% | 6.0716, 7.6668, 9.6846, 12.173 | 6.0716: 89 (79%); 7.6668: 67 (59%); 9.6846: 45 (40%); 12.173: 23 (20%) | 6.0716: 23 (20%); 7.6668: 45 (40%); 9.6846: 67 (59%); 12.173: 89 (79%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -18.327, -8.0422, -2.2574, 8.9092 | -18.327: 90 (80%); -8.0422: 68 (60%); -2.2574: 45 (40%); 8.9092: 23 (20%) | -18.327: 23 (20%); -8.0422: 45 (40%); -2.2574: 68 (60%); 8.9092: 90 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0454, 0.0619, 0.0796, 0.1139 | 0.0454: 90 (80%); 0.0619: 68 (60%); 0.0796: 46 (41%); 0.1139: 23 (20%) | 0.0454: 23 (20%); 0.0619: 45 (40%); 0.0796: 68 (60%); 0.1139: 90 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.7333, 0.8453, 0.895, 0.9501 | 0.7333: 91 (81%); 0.8453: 68 (60%); 0.895: 45 (40%); 0.9501: 23 (20%) | 0.7333: 24 (21%); 0.8453: 45 (40%); 0.895: 68 (60%); 0.9501: 90 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -0.5512, 0.4275, 1.0527, 1.7683 | -0.5512: 90 (80%); 0.4275: 68 (60%); 1.0527: 45 (40%); 1.7683: 23 (20%) | -0.5512: 23 (20%); 0.4275: 45 (40%); 1.0527: 68 (60%); 1.7683: 90 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | 0.692, 0.9375, 1.1493, 1.5304 | 0.692: 90 (80%); 0.9375: 68 (60%); 1.1493: 45 (40%); 1.5304: 23 (20%) | 0.692: 23 (20%); 0.9375: 45 (40%); 1.1493: 68 (60%); 1.5304: 90 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.6379, -0.9004, -0.0283, 0.6389 | -1.6379: 90 (80%); -0.9004: 68 (60%); -0.0283: 45 (40%); 0.6389: 23 (20%) | -1.6379: 23 (20%); -0.9004: 45 (40%); -0.0283: 68 (60%); 0.6389: 90 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | 5.5018, 8.3308, 10.9408, 14.2108 | 5.5018: 90 (80%); 8.3308: 68 (60%); 10.9408: 45 (40%); 14.2108: 23 (20%) | 5.5018: 23 (20%); 8.3308: 45 (40%); 10.9408: 68 (60%); 14.2108: 90 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 60.646, 63.24, 66.296, 70.808 | 60.646: 90 (80%); 63.24: 68 (60%); 66.296: 45 (40%); 70.808: 23 (20%) | 60.646: 23 (20%); 63.24: 45 (40%); 66.296: 68 (60%); 70.808: 90 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 92.188, 94.748, 96.798, 98.52 | 92.188: 90 (80%); 94.748: 68 (60%); 96.798: 45 (40%); 98.52: 24 (21%) | 92.188: 23 (20%); 94.748: 45 (40%); 96.798: 68 (60%); 98.52: 91 (81%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 54.826, 57.424, 60.28, 63.642 | 54.826: 90 (80%); 57.424: 68 (60%); 60.28: 45 (40%); 63.642: 23 (20%) | 54.826: 23 (20%); 57.424: 45 (40%); 60.28: 68 (60%); 63.642: 90 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 67.96, 71.14, 73.92, 78.796 | 67.96: 90 (80%); 71.14: 68 (60%); 73.92: 46 (41%); 78.796: 23 (20%) | 67.96: 23 (20%); 71.14: 45 (40%); 73.92: 69 (61%); 78.796: 90 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0341, 0.0453, 0.0604, 0.0923 | 0.0341: 90 (80%); 0.0453: 68 (60%); 0.0604: 45 (40%); 0.0923: 25 (22%) | 0.0341: 23 (20%); 0.0453: 45 (40%); 0.0604: 68 (60%); 0.0923: 91 (81%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0973, -0.0642, -0.0439, -0.0371 | -0.0973: 96 (85%); -0.0642: 68 (60%); -0.0439: 45 (40%); -0.0371: 23 (20%) | -0.0973: 24 (21%); -0.0642: 45 (40%); -0.0439: 68 (60%); -0.0371: 90 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 113 (100%) | 0: 99 (88%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.1% | 20, 24, 37, 59.8 | 20: 102 (90%); 24: 71 (63%); 37: 46 (41%); 59.8: 23 (20%) | 20: 40 (35%); 24: 49 (43%); 37: 70 (62%); 59.8: 89 (79%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 99.1% | 0.0103, 0.0156, 0.0223, 0.0371 | 0.0103: 89 (79%); 0.0156: 67 (59%); 0.0223: 45 (40%); 0.0371: 23 (20%) | 0.0103: 23 (20%); 0.0156: 45 (40%); 0.0223: 67 (59%); 0.0371: 89 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.5538, 0.7463, 0.8949, 0.9655 | 0.5538: 90 (80%); 0.7463: 68 (60%); 0.8949: 45 (40%); 0.9655: 23 (20%) | 0.5538: 23 (20%); 0.7463: 45 (40%); 0.8949: 68 (60%); 0.9655: 90 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 29.96, 53.54, 78.38, 130.2 | 29.96: 90 (80%); 53.54: 68 (60%); 78.38: 45 (40%); 130.2: 23 (20%) | 29.96: 23 (20%); 53.54: 45 (40%); 78.38: 68 (60%); 130.2: 90 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | 3.0281, 5.1121, 9.965, 14.473 | 3.0281: 90 (80%); 5.1121: 68 (60%); 9.965: 45 (40%); 14.473: 23 (20%) | 3.0281: 23 (20%); 5.1121: 45 (40%); 9.965: 68 (60%); 14.473: 90 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 58.196, 73.946, 84.692, 89.022 | 58.196: 90 (80%); 73.946: 68 (60%); 84.692: 45 (40%); 89.022: 23 (20%) | 58.196: 23 (20%); 73.946: 45 (40%); 84.692: 68 (60%); 89.022: 90 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 70.96, 83.342, 89.072, 92.854 | 70.96: 90 (80%); 83.342: 68 (60%); 89.072: 45 (40%); 92.854: 23 (20%) | 70.96: 23 (20%); 83.342: 45 (40%); 89.072: 68 (60%); 92.854: 90 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 68.416, 79.9, 93.47, 99.442 | 68.416: 90 (80%); 79.9: 68 (60%); 93.47: 45 (40%); 99.442: 23 (20%) | 68.416: 23 (20%); 79.9: 45 (40%); 93.47: 68 (60%); 99.442: 90 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 89.072, 100 | 89.072: 90 (80%); 100: 78 (69%) | 89.072: 23 (20%); 100: 113 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 13, 18 | 5: 92 (81%); 10: 69 (61%); 13: 49 (43%); 18: 28 (25%) | 5: 26 (23%); 10: 52 (46%); 13: 74 (65%); 18: 92 (81%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 3, 8, 12, 17 | 3: 95 (84%); 8: 73 (65%); 12: 49 (43%); 17: 27 (24%) | 3: 27 (24%); 8: 49 (43%); 12: 69 (61%); 17: 91 (81%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 58.492, 63.136, 66.222, 69.214 | 58.492: 90 (80%); 63.136: 68 (60%); 66.222: 45 (40%); 69.214: 23 (20%) | 58.492: 23 (20%); 63.136: 45 (40%); 66.222: 68 (60%); 69.214: 90 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1111, 0.4635, 0.5754, 0.6929 | 0.1111: 91 (81%); 0.4635: 68 (60%); 0.5754: 46 (41%); 0.6929: 23 (20%) | 0.1111: 24 (21%); 0.4635: 45 (40%); 0.5754: 75 (66%); 0.6929: 90 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.774, 18.39, 22.4, 24.5 | 15.774: 90 (80%); 18.39: 69 (61%); 22.4: 45 (40%); 24.5: 26 (23%) | 15.774: 23 (20%); 18.39: 46 (41%); 22.4: 68 (60%); 24.5: 91 (81%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 15.774, 18.39, 22.4, 24.5 | 15.774: 90 (80%); 18.39: 69 (61%); 22.4: 45 (40%); 24.5: 26 (23%) | 15.774: 23 (20%); 18.39: 46 (41%); 22.4: 68 (60%); 24.5: 91 (81%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8659, 0.8935, 0.9103, 0.9344 | 0.8659: 91 (81%); 0.8935: 68 (60%); 0.9103: 45 (40%); 0.9344: 26 (23%) | 0.8659: 24 (21%); 0.8935: 45 (40%); 0.9103: 68 (60%); 0.9344: 91 (81%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 1.154, 1.286, 1.502, 2.03 | 1.154: 90 (80%); 1.286: 68 (60%); 1.502: 45 (40%); 2.03: 24 (21%) | 1.154: 23 (20%); 1.286: 45 (40%); 1.502: 68 (60%); 2.03: 91 (81%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0389, 0.0601, 0.0891, 0.1365 | 0.0389: 90 (80%); 0.0601: 68 (60%); 0.0891: 45 (40%); 0.1365: 23 (20%) | 0.0389: 23 (20%); 0.0601: 45 (40%); 0.0891: 68 (60%); 0.1365: 90 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 113 (100%) | 0: 110 (97%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 113 (100%) | 0: 106 (94%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | 0.0452, 0.0721, 0.1124, 0.1555 | 0.0452: 90 (80%); 0.0721: 68 (60%); 0.1124: 45 (40%); 0.1555: 23 (20%) | 0.0452: 23 (20%); 0.0721: 45 (40%); 0.1124: 68 (60%); 0.1555: 90 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -6.672, -4.672, -2.93, -1.564 | -6.672: 90 (80%); -4.672: 68 (60%); -2.93: 46 (41%); -1.564: 23 (20%) | -6.672: 23 (20%); -4.672: 45 (40%); -2.93: 69 (61%); -1.564: 90 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 100.0% | 0.6649, 0.8935, 1.0483, 1.3681 | 0.6649: 90 (80%); 0.8935: 68 (60%); 1.0483: 45 (40%); 1.3681: 23 (20%) | 0.6649: 23 (20%); 0.8935: 45 (40%); 1.0483: 68 (60%); 1.3681: 90 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 100.0% | 3.4, 5.8, 7, 9 | 3.4: 90 (80%); 5.8: 68 (60%); 7: 53 (47%); 9: 29 (26%) | 3.4: 23 (20%); 5.8: 45 (40%); 7: 75 (66%); 9: 100 (88%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 100.0% | 0.1894, 0.2358, 0.2909, 0.3828 | 0.1894: 90 (80%); 0.2358: 68 (60%); 0.2909: 45 (40%); 0.3828: 23 (20%) | 0.1894: 23 (20%); 0.2358: 45 (40%); 0.2909: 68 (60%); 0.3828: 90 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 100.0% | 3, 5, 8, 9.6 | 3: 96 (85%); 5: 76 (67%); 8: 51 (45%); 9.6: 23 (20%) | 3: 32 (28%); 5: 47 (42%); 8: 77 (68%); 9.6: 90 (80%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 100.0% | 0.0364, 0.0473, 0.0612, 0.1023 | 0.0364: 91 (81%); 0.0473: 68 (60%); 0.0612: 45 (40%); 0.1023: 23 (20%) | 0.0364: 23 (20%); 0.0473: 46 (41%); 0.0612: 68 (60%); 0.1023: 90 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 100.0% | 5, 7, 9, 10 | 5: 96 (85%); 7: 78 (69%); 9: 53 (47%); 10: 39 (35%) | 5: 28 (25%); 7: 48 (42%); 9: 74 (65%); 10: 113 (100%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 100.0% | -0.2804, -0.1716, -0.1007, 0.0255 | -0.2804: 90 (80%); -0.1716: 68 (60%); -0.1007: 45 (40%); 0.0255: 23 (20%) | -0.2804: 23 (20%); -0.1716: 46 (41%); -0.1007: 68 (60%); 0.0255: 90 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 100.0% | 2, 3, 5, 6 | 2: 96 (85%); 3: 79 (70%); 5: 52 (46%); 6: 37 (33%) | 2: 34 (30%); 3: 47 (42%); 5: 76 (67%); 6: 91 (81%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 0.9% |
| 8k_item_5_02_filed_within_7d | 5.4% |
| above_avwap_252low | 92.6% |
| above_cam_r3 | 91.2% |
| above_cam_r4 | 71.7% |
| above_prev_high | 95.6% |
| above_prev_high_clearance_atr_05 | 66.4% |
| above_r1 | 84.1% |
| above_r2 | 61.1% |
| above_vwap | 35.4% |
| ad_rising | 96.5% |
| adx_cross_up | 5.3% |
| adx_cross_up_20 | 6.2% |
| adx_di_bear | 1.8% |
| adx_di_bull | 98.2% |
| adx_trending | 22.1% |
| ao_cross_up | 12.4% |
| ao_positive | 71.7% |
| ao_twin_peaks_bull | 2.7% |
| at_key_fib | 8.8% |
| at_key_fib_wide | 29.2% |
| avwap_20low_reclaim_recent_3d | 22.3% |
| avwap_252low_reclaim_recent_3d | 29.6% |
| avwap_50low_reclaim_recent_3d | 18.8% |
| bb_10_20_expanding | 94.7% |
| bb_10_20_pctb_gt_8 | 96.5% |
| bb_10_20_pctb_gt_85 | 94.7% |
| bb_10_20_pctb_gt_9 | 87.6% |
| bb_10_20_pctb_gt_95 | 68.1% |
| bb_10_20_reclaim_from_lower_recent_3d | 0.9% |
| bb_10_20_reclaim_from_upper_recent_3d | 15.9% |
| bb_10_20_squeeze | 14.2% |
| bb_10_20_touch_upper | 68.1% |
| bb_20_15_expanding | 95.6% |
| bb_20_15_reclaim_from_upper_recent_3d | 1.8% |
| bb_20_15_squeeze | 26.5% |
| bb_20_20_expanding | 95.6% |
| bb_20_20_pctb_gt_9 | 94.7% |
| bb_20_20_pctb_gt_95 | 89.4% |
| bb_20_20_reclaim_from_lower_recent_3d | 0.9% |
| bb_20_20_reclaim_from_upper_recent_3d | 2.7% |
| bb_20_20_squeeze | 11.5% |
| bb_20_20_touch_upper | 86.7% |
| below_avwap_252low | 7.4% |
| below_ema_200 | 55.8% |
| below_ema_50 | 7.1% |
| below_prev_high | 4.4% |
| below_sma_200 | 61.1% |
| below_sma_50 | 8.8% |
| below_vwap | 64.6% |
| break_52w_high | 5.3% |
| break_52w_high_clearance_atr_05 | 1.8% |
| break_52w_high_confirmed_today | 0.9% |
| bullish_engulfing | 2.7% |
| bullish_pin_bar | 3.5% |
| chandelier_short_bearish | 3.5% |
| chandelier_short_flip_up | 29.2% |
| cmf_cross_up | 11.5% |
| cmf_negative | 15.9% |
| cmf_positive | 84.1% |
| concentrated_sell | 2.7% |
| cpr_narrow | 91.2% |
| cpr_narrow_tight | 15.9% |
| cup_handle_detected | 13.3% |
| cup_handle_neckline_break_retest_long | 13.3% |
| dc10_new_high | 99.1% |
| dc10_strong_breakout_up | 59.3% |
| dc20_new_high | 99.1% |
| dc20_resistance_break_retest_strong | 24.8% |
| defensive_leadership | 33.6% |
| director_only_buy | 0.9% |
| doji | 0.9% |
| double_bottom_detected | 15.9% |
| double_top_detected | 11.5% |
| dpi_elevated | 68.2% |
| ema_20_50_bearish | 72.6% |
| ema_20_50_bullish | 27.4% |
| ema_20_50_golden_cross | 8.0% |
| ema_50_200_bearish | 84.1% |
| ema_50_200_bullish | 15.9% |
| ema_50_200_golden_cross | 0.9% |
| ema_9_21_bearish | 13.3% |
| ema_9_21_bullish | 86.7% |
| ema_9_21_golden_cross | 22.1% |
| flag_bull_break_retest_long | 0.9% |
| flag_bull_broke | 1.8% |
| force_index_cross_up | 12.4% |
| gap_dn_1_5pct | 1.8% |
| gap_dn_2pct | 1.8% |
| gap_up_1_5pct | 34.5% |
| gap_up_2pct | 28.3% |
| hammer | 4.4% |
| head_shoulders_bottom_detected | 5.3% |
| head_shoulders_top_detected | 4.4% |
| house_cluster_buy | 5.4% |
| house_cluster_sell | 8.9% |
| htf_aligned_bear | 5.3% |
| htf_aligned_bull | 30.1% |
| htf_disagreement | 8.8% |
| hull_bearish | 0.9% |
| hull_bullish | 99.1% |
| hull_flip_up | 14.2% |
| ichi_above_cloud | 55.8% |
| ichi_above_cloud_break_recent_5d | 42.5% |
| ichi_below_cloud | 27.4% |
| ichi_cloud_thick | 87.6% |
| ichi_tk_bearish | 7.1% |
| ichi_tk_bullish | 70.8% |
| ichi_tk_cross_up | 15.9% |
| ichi_weekly_above_cloud | 21.3% |
| ichi_weekly_below_cloud | 32.4% |
| ichi_weekly_in_cloud | 46.3% |
| inside_kc | 36.3% |
| institutional_buy | 85.0% |
| institutional_negative | 3.5% |
| institutional_persistence_growing | 32.4% |
| institutional_persistence_strong | 38.2% |
| institutional_strong_buy | 62.8% |
| inverted_cup_handle_detected | 12.4% |
| is_friday | 30.1% |
| is_halloween_period | 33.6% |
| is_january | 7.1% |
| is_january_extended | 8.0% |
| is_monday | 8.0% |
| is_pre_holiday | 2.7% |
| is_summer_period | 66.4% |
| is_totm_window | 42.5% |
| is_totm_window_first_day | 4.4% |
| is_week_open | 8.8% |
| kc_touch_upper | 69.0% |
| macd_12_26_9_bearish | 0.9% |
| macd_12_26_9_bullish | 99.1% |
| macd_12_26_9_crossover_up | 7.1% |
| macd_8_21_5_crossover_up | 6.2% |
| marubozu_bull | 4.4% |
| mfi_broad_overbought | 28.3% |
| mfi_broad_oversold | 0.9% |
| mfi_overbought | 4.4% |
| mfi_oversold | 0.9% |
| monthly_above_sma_12 | 36.1% |
| monthly_above_sma_6 | 54.6% |
| monthly_bias_bear | 40.7% |
| monthly_bias_bull | 31.5% |
| monthly_momentum_pos | 37.0% |
| morning_star | 9.7% |
| near_52w_high | 5.3% |
| near_52w_high_95pct | 9.7% |
| near_avwap_20low_atr_10x | 0.9% |
| near_avwap_20low_atr_15x | 8.9% |
| near_avwap_20low_atr_20x | 24.1% |
| near_avwap_252low_atr_05x | 5.6% |
| near_avwap_252low_atr_10x | 12.0% |
| near_avwap_252low_atr_15x | 20.4% |
| near_avwap_252low_atr_20x | 25.0% |
| near_avwap_50low_atr_10x | 0.9% |
| near_avwap_50low_atr_15x | 7.1% |
| near_avwap_50low_atr_20x | 17.0% |
| near_cam_r3 | 9.7% |
| near_fib_236 | 7.1% |
| near_fib_382 | 4.4% |
| near_fib_500 | 2.7% |
| near_fib_618 | 1.8% |
| near_prev_close | 0.9% |
| near_prev_high | 11.5% |
| near_r1 | 15.0% |
| near_r1_wide | 45.1% |
| near_r2 | 8.0% |
| near_r2_wide | 46.9% |
| near_s1_wide | 2.7% |
| near_wood_r1 | 7.1% |
| news_uses_polygon_score | 17.7% |
| obv_bearish | 3.5% |
| obv_bullish | 96.5% |
| obv_falling | 5.3% |
| obv_rising | 94.7% |
| outside_bar | 3.5% |
| pead_negative_surprise | 22.7% |
| pead_positive_surprise | 23.7% |
| pin_bar | 3.5% |
| po3_accumulation_active | 27.4% |
| po3_bullish | 5.3% |
| po3_manipulation_sweep_down | 0.9% |
| po3_manipulation_sweep_up | 26.5% |
| po3_mmbm_setup | 0.9% |
| po3_sweep_below_prior_low | 5.3% |
| ppo_bullish | 99.1% |
| ppo_crossover_up | 7.1% |
| pre_fomc_d0 | 4.4% |
| pre_fomc_d1 | 1.8% |
| pre_fomc_window | 6.2% |
| price_above_ema_200 | 44.2% |
| price_above_ema_200_break_recent_5d | 31.0% |
| price_above_ema_20_break_recent_5d | 56.6% |
| price_above_ema_21_break_recent_5d | 58.4% |
| price_above_ema_50 | 92.9% |
| price_above_ema_50_break_recent_5d | 68.1% |
| price_above_ema_9_break_recent_5d | 54.9% |
| price_above_hull | 98.2% |
| price_above_sma_200 | 38.9% |
| price_above_sma_50 | 91.2% |
| price_above_tema | 99.1% |
| price_below_hull | 1.8% |
| price_below_tema | 0.9% |
| psar_bullish | 98.2% |
| psar_flip_dn | 0.9% |
| psar_flip_up | 9.7% |
| r1_break_retest_long | 90.3% |
| resistance_break_retest | 51.3% |
| risk_off_regime_bond_signal | 10.6% |
| risk_off_regime_bond_signal_strong | 3.5% |
| risk_off_regime_gold_signal | 38.9% |
| risk_on_regime_bond_signal | 48.7% |
| risk_on_regime_bond_signal_strong | 26.5% |
| roc_turning_up | 13.3% |
| rsi_14_extreme_ob | 1.8% |
| rsi_14_overbought | 22.1% |
| rsi_21_bullish | 97.3% |
| rsi_21_overbought | 5.3% |
| rsi_2_cross_up_extreme_os_recent_3d | 23.0% |
| rsi_2_cross_up_oversold_recent_3d | 31.9% |
| rsi_9_cross_dn_overbought_recent_3d | 1.8% |
| rsi_9_cross_up_oversold_recent_3d | 3.5% |
| rsi_9_extreme_ob | 15.9% |
| rsi_9_overbought | 68.1% |
| sector_outperforming_spy | 33.3% |
| sector_underperforming_spy | 66.7% |
| sma_20_50_bullish | 25.7% |
| sma_20_50_golden_cross | 1.8% |
| sma_50_200_bullish | 16.8% |
| sma_9_21_bullish | 81.4% |
| sma_9_21_golden_cross | 10.6% |
| smc_bos_bearish | 10.6% |
| smc_bos_bullish | 4.4% |
| smc_bos_retest_long | 4.4% |
| smc_bos_retest_short | 4.4% |
| smc_breaker_block_bearish | 17.7% |
| smc_breaker_block_bullish | 11.5% |
| smc_choch_bearish | 6.2% |
| smc_choch_bullish | 0.9% |
| smc_equal_highs_swept | 1.8% |
| smc_equal_lows_swept | 4.4% |
| smc_fvg_bearish_active | 15.0% |
| smc_fvg_bullish_active | 81.4% |
| smc_fvg_retest_short_zone | 14.2% |
| smc_in_discount_zone | 26.5% |
| smc_in_premium_zone | 96.5% |
| smc_inverse_fvg_bearish | 61.9% |
| smc_inverse_fvg_bullish | 99.1% |
| smc_liquidity_swept_dn | 0.9% |
| smc_mitigation_block_short | 5.3% |
| smc_ob_bearish_active | 61.1% |
| smc_ob_bullish_active | 15.0% |
| smc_ote_long_zone | 9.7% |
| smc_ote_short_zone | 5.3% |
| squeeze_fire_up | 8.8% |
| squeeze_in | 21.2% |
| stoch_bearish_cross | 2.7% |
| stoch_broad_overbought | 77.0% |
| stoch_bullish_cross | 17.7% |
| stoch_overbought | 69.0% |
| stochrsi_cross_dn | 5.3% |
| stochrsi_cross_up | 10.6% |
| stochrsi_overbought | 85.8% |
| tema_above_dema | 95.6% |
| tema_cross_up | 7.1% |
| three_white_soldiers | 28.3% |
| triangle_apex_break_retest_long | 23.9% |
| triangle_ascending_detected | 14.2% |
| triangle_descending_detected | 13.3% |
| uo_overbought | 15.0% |
| usd_strengthening | 25.7% |
| usd_weakening | 9.7% |
| vix_band_high | 21.2% |
| vix_band_low | 30.1% |
| vix_band_mid | 48.7% |
| vix_term_backwardation | 1.8% |
| vix_term_contango | 98.2% |
| vol_spike_12x | 73.5% |
| vol_spike_15x | 40.7% |
| vol_spike_17x | 30.1% |
| vol_spike_2x | 21.2% |
| vol_spike_2x_on_down_day_recent_3d | 1.8% |
| vol_spike_2x_on_up_day_recent_3d | 12.4% |
| vol_spike_3x | 8.0% |
| vp_above_value_area | 48.7% |
| vp_close_above_poc | 87.6% |
| vp_close_below_poc | 12.4% |
| vp_in_value_area | 51.3% |
| week_open_gap_up_15pct | 3.5% |
| weekly_above_ema_10 | 94.7% |
| weekly_above_ema_20 | 68.1% |
| weekly_bias_bear | 5.3% |
| weekly_bias_bull | 68.1% |
| williams_r_rising | 81.4% |
| within_pead_window | 31.9% |
| xs_avoid_high_ivol | 68.1% |
| xs_avoid_high_max | 53.1% |
| xs_high_beta_decile | 25.7% |
| xs_low_beta_bottom_quintile | 25.7% |
| xs_low_beta_decile | 13.3% |
| xs_low_beta_decile_entry_recent_5d | 0.9% |
| xs_low_beta_top_quintile | 13.3% |
| xs_momentum_bottom_decile | 15.0% |
| xs_momentum_bottom_quintile | 30.1% |
| xs_momentum_top_decile | 3.5% |
| xs_momentum_top_quintile | 8.8% |
| xs_quality_bottom_quintile | 14.5% |
| xs_quality_top_quintile | 21.7% |
| xs_quality_top_tercile | 36.2% |
| yoy_surprise_high | 41.8% |
| yoy_surprise_negative | 45.5% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 90.3% |
| committed_growth_holders | 90.3% |
| corp_donations_1y | 5.3% |
| corp_donations_count_1y | 5.3% |
| corp_donations_unique_pacs | 5.3% |
| cot_rut_commercials_pctile_3y | 25.7% |
| cot_rut_mmoney_pctile_3y | 25.7% |
| cup_handle_depth_pct | 23.9% |
| days_since_deletion | 5.3% |
| days_since_inclusion | 8.0% |
| days_to_next_holiday | 48.7% |
| days_to_rebalance | 13.3% |
| dpi_30d_avg | 94.7% |
| dpi_recent | 94.7% |
| earnings_announcement_return | 85.8% |
| earnings_eps_yoy_growth | 97.3% |
| gov_contracts_4q_sum | 38.1% |
| gov_contracts_last_qtr_amount | 38.1% |
| gov_contracts_qoq_growth | 38.1% |
| head_shoulders_magnitude_pct | 9.7% |
| insider_director_buyers_30d | 3.5% |
| insider_officer_buyers_30d | 3.5% |
| inverted_cup_handle_height_pct | 19.5% |
| lobbying_amount_1y | 72.6% |
| lobbying_amount_q | 72.6% |
| lobbying_amount_yoy | 72.6% |
| monthly_momentum_6m | 95.6% |
| otc_short_ratio_recent | 94.7% |
| otc_volume_recent | 94.7% |
| pair_half_life | 94.7% |
| pair_max_abs_zscore | 94.7% |
| pair_zscore_signed | 94.7% |
| pct_from_avwap_252low | 95.6% |
| persistent_holders_4q | 90.3% |
| persistent_holders_8q | 90.3% |
| search_volume_index_recent | 79.6% |
| search_volume_observations | 79.6% |
| search_volume_zscore_30d | 79.6% |
| sector_etf_return_20d | 2.7% |
| spy_return_20d | 2.7% |
| total_active_holders | 90.3% |
| triangle_breakdown_pct | 13.3% |
| triangle_breakout_pct | 14.2% |
| xs_quality_decile | 61.1% |
| xs_quality_gross_profitability | 61.1% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.998), `avwap_20low` (0.999), `avwap_252low` (0.999), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.998), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.998), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.998), `cam_r1` (0.998), `cam_r2` (0.998), `cam_r3` (0.998), `cam_r4` (0.998), `cam_s1` (0.998), `cam_s2` (0.998), `cam_s3` (0.998), `cam_s4` (0.998), `chandelier_long_value` (0.998), `chandelier_short_value` (0.999), `cpr_bottom` (0.998), `cpr_top` (0.998), `cup_handle_breakout_level` (0.998), `cup_handle_rim` (0.998), `dc10_lower` (0.999), `dc10_mid` (0.999), `dc10_upper` (0.998), `dc20_lower` (0.998), `dc20_mid` (0.999), `dc20_upper` (0.998), `dema` (0.999), `double_bottom_neckline` (0.994), `double_bottom_trough` (0.998), `double_top_neckline` (1.0), `double_top_peak` (1.0), `entry_stop_long` (0.998), `entry_stop_short` (0.997), `fib_236` (0.997), `fib_382` (0.998), `fib_500` (0.998), `fib_618` (0.998), `fib_786` (0.999), `fib_ext_127` (0.995), `fib_ext_162` (0.992), `head_shoulders_bottom_neckline` (1.0), `head_shoulders_top_neckline` (1.0), `hull_ma` (0.998), `ichi_kijun` (0.999), `ichi_senkou_a` (0.997), `ichi_senkou_b` (0.993), `ichi_tenkan` (0.999), `insider_total_shares_bought_30d` (-1.0), `inverted_cup_handle_breakdown_level` (1.0), `inverted_cup_handle_rim_low` (1.0), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (0.999), `monthly_close` (0.998), `monthly_sma_12` (0.989), `monthly_sma_6` (0.997), `pivot` (0.998), `prev_close` (0.998), `prev_high` (0.998), `prev_low` (0.998), `psar_value` (0.998), `r1` (0.998), `r2` (0.998), `r3` (0.998), `s1` (0.998), `s2` (0.998), `s3` (0.998), `supertrend_value` (0.998), `swing_high` (0.996), `swing_low` (0.998), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (0.996), `vp_poc` (0.997), `vp_value_area_high` (0.997), `vp_value_area_low` (0.998), `vwap` (0.965), `vwap_lower_1` (0.963), `vwap_lower_2` (0.959), `vwap_upper_1` (0.965), `vwap_upper_2` (0.966), `weekly_close` (0.998), `weekly_ema_10` (0.999), `weekly_ema_20` (0.996), `wood_p` (0.998), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.998), `wood_s2` (0.998), `year_high` (0.961), `year_low` (0.982)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | (structural) c > o - optional min body p | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1 | range-position cutoff | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P3.1 | breakout tolerance (close >= upper * (1- | 4 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P4.1 | volume ratio floor (vol / avg) | 4 | subset-safe | no - derives offline |
| P5 | news_sentiment_5d >= 0.3 | 5 | subset-safe | no - derives offline |
| P6 | news_volume_zscore_5d >= 0.9091 | 5 | subset-safe | no - derives offline |

```
FULL FACTORIAL     3 x 3 x 4 x 4 x 5 x 5 = 3600
offline gradings   100 level-combinations x 24 exits = 2400
ENGINE RUNS        1 (actuated fire-adding axes only)
PENDING ACTUATION  36 level-combinations are DEFINED but have no env knob - they are a FEATURE REQUEST, not a runnable band (plan 11.0b state 1; B2866)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 432 census axes join it only when REGISTERED at the T3 band review.
