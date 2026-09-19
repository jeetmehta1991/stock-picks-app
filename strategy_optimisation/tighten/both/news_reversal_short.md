# Table A - news_reversal_short

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit fa06ebf3e at 2026-09-19 13:07:41 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** news_sentiment | **status:** NOT-STARTED | **R5 fires:** 60 | **surviving fires (T1):** 60 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  close_below_open  <- backtest/signals/screener.py +1
       DEFN: bar direction: close vs open (bar-anatomy block)
       knobs P1.1-P1.1 (band rows in Table A)
P2  close_in_bottom_40pct_of_range  <- backtest/signals/screener.py +1
       DEFN: close inside the top/bottom 40pct of the bar's range (technical.py:1682)
       knobs P2.1-P2.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  news_count_5d >= 3   [EXISTING-THRESHOLD]
P4  news_sentiment_5d >= 0.3   [EXISTING-THRESHOLD]
P5  news_sentiment_shift < -0.2   [EXISTING-THRESHOLD]
P6  pct_change_5d > 0.08   [EXISTING-THRESHOLD]
P7  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_news_reversal_short (docstring and return dropped):

```python
fires = s.get('news_sentiment_5d', 0.0) >= 0.3 and s.get('pct_change_5d', 0.0) > 0.08 and (s.get('news_count_5d', 0) >= 3) and (s.get('news_sentiment_shift', 0.0) < -0.2) and s.get('close_below_open', False) and s.get('close_in_bottom_40pct_of_range', False) and (not _short_borrow_trap_active(s))
sent = s.get('news_sentiment_5d', 0.0)
pct = s.get('pct_change_5d', 0.0)
shift = s.get('news_sentiment_shift', 0.0)
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
| P1 | PRODUCER | close_below_open - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | bar direction: close vs open (bar-anatomy block) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | mirror of close_above_open - technical.py bar-anatomy block | mirror | 0.0 | [0, 0.2, 0.5] pct | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | close_in_bottom_40pct_of_range - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close inside the top/bottom 40pct of the bar's range (technical.py:1682) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | mirror of top_40pct - backtest/signals/technical.py:1682 region | mirror | 0.4 | [0.25, 0.40, 0.50] | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | STRATEGY | news_count_5d `>= 3` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `>= 3` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P4 | STRATEGY | news_sentiment_5d `>= 0.3` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `>= 0.3` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P5 | STRATEGY | news_sentiment_shift `< -0.2` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `< -0.2` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P6 | STRATEGY | pct_change_5d `> 0.08` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `> 0.08` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P7 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| news_count_5d | backtest/signals/news_sentiment.py +1 | `>= 3` | 100.0% | TIGHTER = RAISE the floor: 4 -> 50 (83%); 5.6 -> 36 (60%); 10 -> 25 (42%); 17.2 -> 12 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | `>= 0.3` | 100.0% | TIGHTER = RAISE the floor: 0.3762 -> 48 (80%); 0.4425 -> 36 (60%); 0.557 -> 24 (40%); 0.6938 -> 12 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | `< -0.2` | 100.0% | TIGHTER = LOWER the ceiling: -0.4109 -> 12 (20%); -0.3456 -> 24 (40%); -0.3145 -> 36 (60%); -0.25 -> 51 (85%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |
| pct_change_5d | backtest/signals/screener.py | `> 0.08` | 100.0% | TIGHTER = RAISE the floor: 0.0856 -> 48 (80%); 0.1014 -> 36 (60%); 0.1195 -> 24 (40%); 0.1374 -> 12 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 18.528, 21.28, 25.126, 34.066 | 18.528: 48 (80%); 21.28: 36 (60%); 25.126: 24 (40%); 34.066: 12 (20%) | 18.528: 12 (20%); 21.28: 24 (40%); 25.126: 36 (60%); 34.066: 48 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 9.976, 13.812, 16.114, 19.876 | 9.976: 48 (80%); 13.812: 36 (60%); 16.114: 24 (40%); 19.876: 12 (20%) | 9.976: 12 (20%); 13.812: 24 (40%); 16.114: 36 (60%); 19.876: 48 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 32.544, 34.956, 40.362, 46.576 | 32.544: 48 (80%); 34.956: 36 (60%); 40.362: 24 (40%); 46.576: 12 (20%) | 32.544: 12 (20%); 34.956: 24 (40%); 40.362: 36 (60%); 46.576: 48 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | 1.7091, 5.2107, 8.7279, 23.8317 | 1.7091: 48 (80%); 5.2107: 36 (60%); 8.7279: 24 (40%); 23.8317: 12 (20%) | 1.7091: 12 (20%); 5.2107: 24 (40%); 8.7279: 36 (60%); 23.8317: 48 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.9938, 3.2129, 4.8192, 9.2957 | 1.9938: 48 (80%); 3.2129: 36 (60%); 4.8192: 24 (40%); 9.2957: 12 (20%) | 1.9938: 12 (20%); 3.2129: 24 (40%); 4.8192: 36 (60%); 9.2957: 48 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.9938, 3.2129, 4.8192, 9.2957 | 1.9938: 48 (80%); 3.2129: 36 (60%); 4.8192: 24 (40%); 9.2957: 12 (20%) | 1.9938: 12 (20%); 3.2129: 24 (40%); 4.8192: 36 (60%); 9.2957: 48 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.5408, 3.1078, 3.8434, 4.4064 | 2.5408: 48 (80%); 3.1078: 36 (60%); 3.8434: 24 (40%); 4.4064: 12 (20%) | 2.5408: 12 (20%); 3.1078: 24 (40%); 3.8434: 36 (60%); 4.4064: 48 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.1693, 0.2066, 0.2365, 0.2894 | 0.1693: 48 (80%); 0.2066: 36 (60%); 0.2365: 24 (40%); 0.2894: 12 (20%) | 0.1693: 13 (22%); 0.2066: 24 (40%); 0.2365: 36 (60%); 0.2894: 48 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.785, 0.8211, 0.8462, 0.897 | 0.785: 48 (80%); 0.8211: 36 (60%); 0.8462: 24 (40%); 0.897: 12 (20%) | 0.785: 12 (20%); 0.8211: 24 (40%); 0.8462: 36 (60%); 0.897: 48 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.1259, 0.1531, 0.1767, 0.2136 | 0.1259: 48 (80%); 0.1531: 36 (60%); 0.1767: 24 (40%); 0.2136: 12 (20%) | 0.1259: 12 (20%); 0.1531: 24 (40%); 0.1767: 36 (60%); 0.2136: 48 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 1.0074, 1.09, 1.1496, 1.1968 | 1.0074: 48 (80%); 1.09: 36 (60%); 1.1496: 24 (40%); 1.1968: 12 (20%) | 1.0074: 12 (20%); 1.09: 24 (40%); 1.1496: 36 (60%); 1.1968: 48 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.1679, 0.2042, 0.2357, 0.2848 | 0.1679: 48 (80%); 0.2042: 36 (60%); 0.2357: 24 (40%); 0.2848: 12 (20%) | 0.1679: 12 (20%); 0.2042: 24 (40%); 0.2357: 36 (60%); 0.2848: 48 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.8806, 0.9425, 0.9872, 1.0226 | 0.8806: 48 (80%); 0.9425: 36 (60%); 0.9872: 24 (40%); 1.0226: 12 (20%) | 0.8806: 12 (20%); 0.9425: 24 (40%); 0.9872: 36 (60%); 1.0226: 48 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0741, -0.0329, -0.0113, -0.0034 | -0.0741: 48 (80%); -0.0329: 36 (60%); -0.0113: 24 (40%); -0.0034: 12 (20%) | -0.0741: 12 (20%); -0.0329: 24 (40%); -0.0113: 36 (60%); -0.0034: 48 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1314, 0.1698, 0.2034, 0.2565 | 0.1314: 48 (80%); 0.1698: 36 (60%); 0.2034: 24 (40%); 0.2565: 14 (23%) | 0.1314: 12 (20%); 0.1698: 24 (40%); 0.2034: 36 (60%); 0.2565: 46 (77%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 60 (100%) | 0: 59 (98%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0237, 0.0381, 0.1387, 0.2274 | -0.0237: 48 (80%); 0.0381: 36 (60%); 0.1387: 24 (40%); 0.2274: 12 (20%) | -0.0237: 12 (20%); 0.0381: 24 (40%); 0.1387: 36 (60%); 0.2274: 48 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 0.4, 1 | 0: 60 (100%); 0.4: 24 (40%); 1: 24 (40%) | 0: 36 (60%); 0.4: 36 (60%); 1: 50 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2586, -0.2101, -0.1736, -0.1267 | -0.2586: 49 (82%); -0.2101: 36 (60%); -0.1736: 26 (43%); -0.1267: 12 (20%) | -0.2586: 14 (23%); -0.2101: 24 (40%); -0.1736: 37 (62%); -0.1267: 48 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.109, 0.5513, 0.6667, 0.7782 | 0.109: 49 (82%); 0.5513: 37 (62%); 0.6667: 25 (42%); 0.7782: 12 (20%) | 0.109: 14 (23%); 0.5513: 25 (42%); 0.6667: 38 (63%); 0.7782: 48 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.25, 0.391, 0.7051, 0.8974 | 0.25: 49 (82%); 0.391: 37 (62%); 0.7051: 24 (40%); 0.8974: 13 (22%) | 0.25: 13 (22%); 0.391: 25 (42%); 0.7051: 36 (60%); 0.8974: 49 (82%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1065, -0.0139, 0.1038, 0.2087 | -0.1065: 48 (80%); -0.0139: 37 (62%); 0.1038: 24 (40%); 0.2087: 12 (20%) | -0.1065: 12 (20%); -0.0139: 26 (43%); 0.1038: 36 (60%); 0.2087: 48 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2526, 0.5038, 0.6641, 0.7898 | 0.2526: 48 (80%); 0.5038: 36 (60%); 0.6641: 24 (40%); 0.7898: 12 (20%) | 0.2526: 12 (20%); 0.5038: 24 (40%); 0.6641: 36 (60%); 0.7898: 48 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1474, 0.2423, 0.4385, 0.591 | 0.1474: 50 (83%); 0.2423: 36 (60%); 0.4385: 24 (40%); 0.591: 12 (20%) | 0.1474: 14 (23%); 0.2423: 24 (40%); 0.4385: 36 (60%); 0.591: 48 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.455, -0.3466, -0.0344, 0.0891 | -0.455: 48 (80%); -0.3466: 36 (60%); -0.0344: 24 (40%); 0.0891: 13 (22%) | -0.455: 12 (20%); -0.3466: 24 (40%); -0.0344: 36 (60%); 0.0891: 50 (83%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3526, 0.5193, 0.7398, 0.9257 | 0.3526: 51 (85%); 0.5193: 36 (60%); 0.7398: 24 (40%); 0.9257: 12 (20%) | 0.3526: 13 (22%); 0.5193: 24 (40%); 0.7398: 36 (60%); 0.9257: 48 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0769, 0.2821, 0.4577, 0.7308 | 0.0769: 49 (82%); 0.2821: 37 (62%); 0.4577: 24 (40%); 0.7308: 13 (22%) | 0.0769: 13 (22%); 0.2821: 25 (42%); 0.4577: 36 (60%); 0.7308: 49 (82%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0623, -0.0444, -0.0318, 0 | -0.0623: 48 (80%); -0.0444: 36 (60%); -0.0318: 25 (42%); 0: 17 (28%) | -0.0623: 12 (20%); -0.0444: 24 (40%); -0.0318: 37 (62%); 0: 57 (95%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4936, 0.7051, 0.9038, 0.9936 | 0.4936: 50 (83%); 0.7051: 36 (60%); 0.9038: 25 (42%); 0.9936: 14 (23%) | 0.4936: 14 (23%); 0.7051: 24 (40%); 0.9038: 41 (68%); 0.9936: 51 (85%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0795, 0.1936, 0.5449, 0.8475 | 0.0795: 48 (80%); 0.1936: 36 (60%); 0.5449: 25 (42%); 0.8475: 12 (20%) | 0.0795: 12 (20%); 0.1936: 24 (40%); 0.5449: 38 (63%); 0.8475: 48 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | 0.0032, 0.0404, 0.0898, 0.1887 | 0.0032: 48 (80%); 0.0404: 36 (60%); 0.0898: 24 (40%); 0.1887: 12 (20%) | 0.0032: 12 (20%); 0.0404: 24 (40%); 0.0898: 36 (60%); 0.1887: 48 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5061, 0.8397, 0.957, 0.9872 | 0.5061: 48 (80%); 0.8397: 37 (62%); 0.957: 24 (40%); 0.9872: 13 (22%) | 0.5061: 12 (20%); 0.8397: 26 (43%); 0.957: 36 (60%); 0.9872: 49 (82%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0784, 0.1795, 0.5872, 0.7782 | 0.0784: 50 (83%); 0.1795: 37 (62%); 0.5872: 24 (40%); 0.7782: 12 (20%) | 0.0784: 14 (23%); 0.1795: 26 (43%); 0.5872: 36 (60%); 0.7782: 48 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0136, 0.1225, 0.1568 | -0.0812: 52 (87%); -0.0136: 37 (62%); 0.1225: 25 (42%); 0.1568: 12 (20%) | -0.0812: 14 (23%); -0.0136: 25 (42%); 0.1225: 38 (63%); 0.1568: 48 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1561, 0.0102, 0.057, 0.0978 | -0.1561: 48 (80%); 0.0102: 36 (60%); 0.057: 25 (42%); 0.0978: 13 (22%) | -0.1561: 12 (20%); 0.0102: 24 (40%); 0.057: 37 (62%); 0.0978: 50 (83%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3603, 0.6487, 0.7885, 0.8795 | 0.3603: 48 (80%); 0.6487: 36 (60%); 0.7885: 25 (42%); 0.8795: 12 (20%) | 0.3603: 12 (20%); 0.6487: 24 (40%); 0.7885: 39 (65%); 0.8795: 48 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2949, 0.5269, 0.7436, 0.9064 | 0.2949: 48 (80%); 0.5269: 36 (60%); 0.7436: 26 (43%); 0.9064: 12 (20%) | 0.2949: 12 (20%); 0.5269: 24 (40%); 0.7436: 37 (62%); 0.9064: 48 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.1742, 0.2805, 0.5276, 0.9017 | 0.1742: 48 (80%); 0.2805: 36 (60%); 0.5276: 24 (40%); 0.9017: 12 (20%) | 0.1742: 12 (20%); 0.2805: 24 (40%); 0.5276: 36 (60%); 0.9017: 48 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 100.0% | 5.8, 43.2, 82, 99.2 | 5.8: 48 (80%); 43.2: 36 (60%); 82: 25 (42%); 99.2: 12 (20%) | 5.8: 12 (20%); 43.2: 24 (40%); 82: 38 (63%); 99.2: 48 (80%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 100.0% | 1.7465, 2.2527, 2.7704, 3.2303 | 1.7465: 48 (80%); 2.2527: 36 (60%); 2.7704: 24 (40%); 3.2303: 12 (20%) | 1.7465: 12 (20%); 2.2527: 24 (40%); 2.7704: 36 (60%); 3.2303: 48 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 6.8, 14.6, 30, 37 | 6.8: 48 (80%); 14.6: 36 (60%); 30: 25 (42%); 37: 16 (27%) | 6.8: 12 (20%); 14.6: 24 (40%); 30: 38 (63%); 37: 49 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 0, 1, 3 | 0: 60 (100%); 1: 47 (78%); 3: 25 (42%) | 0: 13 (22%); 1: 26 (43%); 3: 52 (87%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0145, -0.004, 0.0113, 0.0173 | -0.0145: 48 (80%); -0.004: 37 (62%); 0.0113: 24 (40%); 0.0173: 12 (20%) | -0.0145: 12 (20%); -0.004: 25 (42%); 0.0113: 36 (60%); 0.0173: 48 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.6492, 25.7217, 26.6649, 27.2706 | 24.6492: 48 (80%); 25.7217: 36 (60%); 26.6649: 25 (42%); 27.2706: 12 (20%) | 24.6492: 12 (20%); 25.7217: 24 (40%); 26.6649: 37 (62%); 27.2706: 48 (80%) | OFFLINE |
| earnings_eps_yoy_growth | backtest/signals/earnings_surprise_yoy.py +2 | 98.3% | -0.5432, -0.0298, 0.3451, 0.9418 | -0.5432: 47 (78%); -0.0298: 35 (58%); 0.3451: 24 (40%); 0.9418: 12 (20%) | -0.5432: 12 (20%); -0.0298: 24 (40%); 0.3451: 35 (58%); 0.9418: 47 (78%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -2.1912, -0.7104, -0.0296, 0.4492 | -2.1912: 48 (80%); -0.7104: 36 (60%); -0.0296: 24 (40%); 0.4492: 12 (20%) | -2.1912: 12 (20%); -0.7104: 24 (40%); -0.0296: 36 (60%); 0.4492: 48 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.4492, 0.0296, 0.7104, 2.1912 | -0.4492: 48 (80%); 0.0296: 36 (60%); 0.7104: 24 (40%); 2.1912: 12 (20%) | -0.4492: 12 (20%); 0.0296: 24 (40%); 0.7104: 36 (60%); 2.1912: 48 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0457, -0.0161, 0.0064, 0.0383 | -0.0457: 48 (80%); -0.0161: 36 (60%); 0.0064: 24 (40%); 0.0383: 12 (20%) | -0.0457: 12 (20%); -0.0161: 24 (40%); 0.0064: 36 (60%); 0.0383: 48 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.2874, 8.1482, 8.6, 8.8719 | 7.2874: 48 (80%); 8.1482: 37 (62%); 8.6: 24 (40%); 8.8719: 12 (20%) | 7.2874: 12 (20%); 8.1482: 23 (38%); 8.6: 36 (60%); 8.8719: 48 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 1 | 0: 60 (100%); 1: 17 (28%) | 0: 43 (72%); 1: 51 (85%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0 | 0: 52 (87%) | 0: 51 (85%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 100.0% | 0, 1 | 0: 60 (100%); 1: 17 (28%) | 0: 43 (72%); 1: 50 (83%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 3, 5, 10, 156.8 | 3: 51 (85%); 5: 40 (67%); 10: 26 (43%); 156.8: 12 (20%) | 3: 17 (28%); 5: 25 (42%); 10: 38 (63%); 156.8: 48 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 3, 73.4, 163.6 | 1: 51 (85%); 3: 40 (67%); 73.4: 24 (40%); 163.6: 12 (20%) | 1: 17 (28%); 3: 25 (42%); 73.4: 36 (60%); 163.6: 48 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | 0.5356, 1.0495, 1.6901, 3.9725 | 0.5356: 48 (80%); 1.0495: 36 (60%); 1.6901: 24 (40%); 3.9725: 12 (20%) | 0.5356: 12 (20%); 1.0495: 24 (40%); 1.6901: 36 (60%); 3.9725: 48 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | 0.5551, 1.7493, 3.4119, 8.245 | 0.5551: 48 (80%); 1.7493: 36 (60%); 3.4119: 24 (40%); 8.245: 12 (20%) | 0.5551: 12 (20%); 1.7493: 24 (40%); 3.4119: 36 (60%); 8.245: 48 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -0.0696, 0.7915, 1.839, 4.5247 | -0.0696: 48 (80%); 0.7915: 36 (60%); 1.839: 24 (40%); 4.5247: 12 (20%) | -0.0696: 12 (20%); 0.7915: 24 (40%); 1.839: 36 (60%); 4.5247: 48 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | 0.5679, 0.9667, 1.8444, 3.0394 | 0.5679: 48 (80%); 0.9667: 36 (60%); 1.8444: 24 (40%); 3.0394: 12 (20%) | 0.5679: 12 (20%); 0.9667: 24 (40%); 1.8444: 36 (60%); 3.0394: 48 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | 0.976, 2.8591, 4.2458, 11.6821 | 0.976: 48 (80%); 2.8591: 36 (60%); 4.2458: 24 (40%); 11.6821: 12 (20%) | 0.976: 12 (20%); 2.8591: 24 (40%); 4.2458: 36 (60%); 11.6821: 48 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | 0.5034, 1.6769, 3.0121, 8.0625 | 0.5034: 48 (80%); 1.6769: 36 (60%); 3.0121: 24 (40%); 8.0625: 12 (20%) | 0.5034: 12 (20%); 1.6769: 24 (40%); 3.0121: 36 (60%); 8.0625: 48 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 61.48, 68.028, 74.242, 79.894 | 61.48: 48 (80%); 68.028: 36 (60%); 74.242: 24 (40%); 79.894: 12 (20%) | 61.48: 12 (20%); 68.028: 24 (40%); 74.242: 36 (60%); 79.894: 48 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 98.3% | 0.0149, 0.0298, 0.0562, 0.1085 | 0.0149: 47 (78%); 0.0298: 35 (58%); 0.0562: 25 (42%); 0.1085: 12 (20%) | 0.0149: 12 (20%); 0.0298: 24 (40%); 0.0562: 34 (57%); 0.1085: 47 (78%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 5, 8, 14, 25.4 | 5: 51 (85%); 8: 37 (62%); 14: 25 (42%); 25.4: 12 (20%) | 5: 15 (25%); 8: 29 (48%); 14: 40 (67%); 25.4: 48 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0861, 0.1429 | 0: 60 (100%); 0.0861: 24 (40%); 0.1429: 13 (22%) | 0: 26 (43%); 0.0861: 36 (60%); 0.1429: 49 (82%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0.4, 0.5161, 0.59, 0.6667 | 0.4: 50 (83%); 0.5161: 37 (62%); 0.59: 24 (40%); 0.6667: 17 (28%) | 0.4: 13 (22%); 0.5161: 25 (42%); 0.59: 36 (60%); 0.6667: 51 (85%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 5, 8, 14, 25.4 | 5: 51 (85%); 8: 37 (62%); 14: 25 (42%); 25.4: 12 (20%) | 5: 15 (25%); 8: 29 (48%); 14: 40 (67%); 25.4: 48 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 1, 3, 6, 11.2 | 1: 60 (100%); 3: 42 (70%); 6: 25 (42%); 11.2: 12 (20%) | 1: 15 (25%); 3: 27 (45%); 6: 37 (62%); 11.2: 48 (80%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.3138, 0.4193, 0.501, 0.6688 | 0.3138: 48 (80%); 0.4193: 36 (60%); 0.501: 24 (40%); 0.6688: 12 (20%) | 0.3138: 12 (20%); 0.4193: 24 (40%); 0.501: 36 (60%); 0.6688: 48 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0.2883, 0.4057, 0.5273, 0.6667 | 0.2883: 48 (80%); 0.4057: 36 (60%); 0.5273: 24 (40%); 0.6667: 16 (27%) | 0.2883: 12 (20%); 0.4057: 24 (40%); 0.5273: 36 (60%); 0.6667: 51 (85%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0.2883, 0.4057, 0.5273, 0.6667 | 0.2883: 48 (80%); 0.4057: 36 (60%); 0.5273: 24 (40%); 0.6667: 16 (27%) | 0.2883: 12 (20%); 0.4057: 24 (40%); 0.5273: 36 (60%); 0.6667: 51 (85%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0.2388, 1.3307, 2.8551, 4.2539 | 0.2388: 48 (80%); 1.3307: 36 (60%); 2.8551: 24 (40%); 4.2539: 12 (20%) | 0.2388: 12 (20%); 1.3307: 24 (40%); 2.8551: 36 (60%); 4.2539: 48 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 1.8, 3, 7, 9 | 1.8: 48 (80%); 3: 42 (70%); 7: 25 (42%); 9: 13 (22%) | 1.8: 12 (20%); 3: 26 (43%); 7: 41 (68%); 9: 49 (82%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | 0.0917, 0.1221, 0.14, 0.2011 | 0.0917: 48 (80%); 0.1221: 36 (60%); 0.14: 24 (40%); 0.2011: 12 (20%) | 0.0917: 12 (20%); 0.1221: 24 (40%); 0.14: 36 (60%); 0.2011: 48 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | 0.0586, 0.1025, 0.1596, 0.2092 | 0.0586: 48 (80%); 0.1025: 36 (60%); 0.1596: 24 (40%); 0.2092: 12 (20%) | 0.0586: 12 (20%); 0.1025: 24 (40%); 0.1596: 36 (60%); 0.2092: 48 (80%) | OFFLINE |
| pct_from_avwap_20low | (not found by literal grep) | 100.0% | 6.45, 7.8872, 8.8836, 11.7568 | 6.45: 48 (80%); 7.8872: 36 (60%); 8.8836: 24 (40%); 11.7568: 12 (20%) | 6.45: 12 (20%); 7.8872: 24 (40%); 8.8836: 36 (60%); 11.7568: 48 (80%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 100.0% | 8.0788, 10.979, 13.2246, 17.526 | 8.0788: 48 (80%); 10.979: 36 (60%); 13.2246: 24 (40%); 17.526: 12 (20%) | 8.0788: 12 (20%); 10.979: 24 (40%); 13.2246: 36 (60%); 17.526: 48 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -11.401, -0.1324, 19.1402, 57.9206 | -11.401: 48 (80%); -0.1324: 36 (60%); 19.1402: 24 (40%); 57.9206: 12 (20%) | -11.401: 12 (20%); -0.1324: 24 (40%); 19.1402: 36 (60%); 57.9206: 48 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.1089, 0.1305, 0.1457, 0.1896 | 0.1089: 48 (80%); 0.1305: 36 (60%); 0.1457: 24 (40%); 0.1896: 12 (20%) | 0.1089: 12 (20%); 0.1305: 24 (40%); 0.1457: 36 (60%); 0.1896: 48 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1086, 0.1844, 0.2916, 0.3396 | 0.1086: 48 (80%); 0.1844: 36 (60%); 0.2916: 24 (40%); 0.3396: 12 (20%) | 0.1086: 12 (20%); 0.1844: 24 (40%); 0.2916: 36 (60%); 0.3396: 48 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | 1.3177, 2.2091, 3.6797, 4.3177 | 1.3177: 48 (80%); 2.2091: 36 (60%); 3.6797: 24 (40%); 4.3177: 12 (20%) | 1.3177: 12 (20%); 2.2091: 24 (40%); 3.6797: 36 (60%); 4.3177: 48 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | 0.8696, 1.1869, 1.4917, 1.9958 | 0.8696: 48 (80%); 1.1869: 36 (60%); 1.4917: 24 (40%); 1.9958: 12 (20%) | 0.8696: 12 (20%); 1.1869: 24 (40%); 1.4917: 36 (60%); 1.9958: 48 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -0.3415, 1.2919, 1.7845, 2.8593 | -0.3415: 48 (80%); 1.2919: 36 (60%); 1.7845: 24 (40%); 2.8593: 12 (20%) | -0.3415: 12 (20%); 1.2919: 24 (40%); 1.7845: 36 (60%); 2.8593: 48 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | 8.4474, 11.8996, 14.9432, 20.1824 | 8.4474: 48 (80%); 11.8996: 36 (60%); 14.9432: 24 (40%); 20.1824: 12 (20%) | 8.4474: 12 (20%); 11.8996: 24 (40%); 14.9432: 36 (60%); 20.1824: 48 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 59.944, 64.964, 69.764, 75.02 | 59.944: 48 (80%); 64.964: 36 (60%); 69.764: 24 (40%); 75.02: 12 (20%) | 59.944: 12 (20%); 64.964: 24 (40%); 69.764: 36 (60%); 75.02: 48 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 58.42, 69.292, 85.65, 95.072 | 58.42: 48 (80%); 69.292: 36 (60%); 85.65: 24 (40%); 95.072: 12 (20%) | 58.42: 12 (20%); 69.292: 24 (40%); 85.65: 36 (60%); 95.072: 48 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 56.314, 60.932, 66.588, 70.396 | 56.314: 48 (80%); 60.932: 36 (60%); 66.588: 24 (40%); 70.396: 12 (20%) | 56.314: 12 (20%); 60.932: 24 (40%); 66.588: 36 (60%); 70.396: 48 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 64.882, 70.646, 73.442, 80.76 | 64.882: 48 (80%); 70.646: 36 (60%); 73.442: 24 (40%); 80.76: 12 (20%) | 64.882: 12 (20%); 70.646: 24 (40%); 73.442: 36 (60%); 80.76: 48 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0309, 0.0488, 0.067, 0.0981 | 0.0309: 48 (80%); 0.0488: 36 (60%); 0.067: 25 (42%); 0.0981: 12 (20%) | 0.0309: 12 (20%); 0.0488: 24 (40%); 0.067: 36 (60%); 0.0981: 48 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0706, -0.0627, -0.0435, -0.0329 | -0.0706: 48 (80%); -0.0627: 37 (62%); -0.0435: 24 (40%); -0.0329: 12 (20%) | -0.0706: 12 (20%); -0.0627: 25 (42%); -0.0435: 36 (60%); -0.0329: 48 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 60 (100%); 2: 13 (22%) | 0: 39 (65%); 2: 51 (85%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 100.0% | 25, 37.6, 53, 76 | 25: 49 (82%); 37.6: 36 (60%); 53: 26 (43%); 76: 13 (22%) | 25: 14 (23%); 37.6: 24 (40%); 53: 37 (62%); 76: 49 (82%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.3% | 0.0133, 0.0181, 0.0295, 0.0437 | 0.0133: 47 (78%); 0.0181: 36 (60%); 0.0295: 24 (40%); 0.0437: 12 (20%) | 0.0133: 12 (20%); 0.0181: 23 (38%); 0.0295: 35 (58%); 0.0437: 47 (78%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.7243, 0.8395, 0.8903, 0.9158 | 0.7243: 48 (80%); 0.8395: 36 (60%); 0.8903: 24 (40%); 0.9158: 12 (20%) | 0.7243: 12 (20%); 0.8395: 24 (40%); 0.8903: 36 (60%); 0.9158: 48 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 15.3, 63.42, 95.88, 162.66 | 15.3: 48 (80%); 63.42: 36 (60%); 95.88: 24 (40%); 162.66: 12 (20%) | 15.3: 12 (20%); 63.42: 24 (40%); 95.88: 36 (60%); 162.66: 48 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | 2.9555, 5.913, 9.987, 20.734 | 2.9555: 48 (80%); 5.913: 36 (60%); 9.987: 24 (40%); 20.734: 12 (20%) | 2.9555: 12 (20%); 5.913: 24 (40%); 9.987: 36 (60%); 20.734: 48 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 75.89, 87.302, 90.162, 93.672 | 75.89: 48 (80%); 87.302: 36 (60%); 90.162: 24 (40%); 93.672: 12 (20%) | 75.89: 12 (20%); 87.302: 24 (40%); 90.162: 36 (60%); 93.672: 48 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 86.13, 89.026, 92.286, 93.746 | 86.13: 48 (80%); 89.026: 36 (60%); 92.286: 24 (40%); 93.746: 12 (20%) | 86.13: 12 (20%); 89.026: 24 (40%); 92.286: 36 (60%); 93.746: 48 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 77.566, 90.014, 95.206, 98.744 | 77.566: 48 (80%); 90.014: 36 (60%); 95.206: 24 (40%); 98.744: 12 (20%) | 77.566: 12 (20%); 90.014: 24 (40%); 95.206: 36 (60%); 98.744: 48 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 73.3, 86.064, 97.992, 100 | 73.3: 48 (80%); 86.064: 36 (60%); 97.992: 24 (40%); 100: 20 (33%) | 73.3: 12 (20%); 86.064: 24 (40%); 97.992: 36 (60%); 100: 60 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 8, 10, 15.2 | 4: 50 (83%); 8: 37 (62%); 10: 30 (50%); 15.2: 12 (20%) | 4: 16 (27%); 8: 25 (42%); 10: 39 (65%); 15.2: 48 (80%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 6, 11, 13, 18 | 6: 49 (82%); 11: 38 (63%); 13: 27 (45%); 18: 14 (23%) | 6: 13 (22%); 11: 26 (43%); 13: 38 (63%); 18: 51 (85%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 57.992, 61.294, 63.942, 67.614 | 57.992: 48 (80%); 61.294: 36 (60%); 63.942: 24 (40%); 67.614: 12 (20%) | 57.992: 12 (20%); 61.294: 24 (40%); 63.942: 36 (60%); 67.614: 48 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1802, 0.4063, 0.5849, 0.7222 | 0.1802: 48 (80%); 0.4063: 36 (60%); 0.5849: 24 (40%); 0.7222: 14 (23%) | 0.1802: 12 (20%); 0.4063: 24 (40%); 0.5849: 36 (60%); 0.7222: 49 (82%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.866, 17.136, 19.122, 23.77 | 14.866: 48 (80%); 17.136: 36 (60%); 19.122: 24 (40%); 23.77: 12 (20%) | 14.866: 12 (20%); 17.136: 24 (40%); 19.122: 36 (60%); 23.77: 48 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 14.866, 17.136, 19.122, 23.77 | 14.866: 48 (80%); 17.136: 36 (60%); 19.122: 24 (40%); 23.77: 12 (20%) | 14.866: 12 (20%); 17.136: 24 (40%); 19.122: 36 (60%); 23.77: 48 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8577, 0.8828, 0.9085, 0.9494 | 0.8577: 48 (80%); 0.8828: 36 (60%); 0.9085: 24 (40%); 0.9494: 13 (22%) | 0.8577: 12 (20%); 0.8828: 24 (40%); 0.9085: 36 (60%); 0.9494: 48 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.782, 0.95, 1.158, 1.422 | 0.782: 48 (80%); 0.95: 37 (62%); 1.158: 24 (40%); 1.422: 12 (20%) | 0.782: 12 (20%); 0.95: 25 (42%); 1.158: 36 (60%); 1.422: 48 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0841, 0.1189, 0.1642, 0.23 | 0.0841: 48 (80%); 0.1189: 36 (60%); 0.1642: 24 (40%); 0.23: 12 (20%) | 0.0841: 12 (20%); 0.1189: 24 (40%); 0.1642: 36 (60%); 0.23: 48 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 46.706, 92.2837, 125.5089, 190.7344 | 46.706: 48 (80%); 92.2837: 36 (60%); 125.5089: 24 (40%); 190.7344: 12 (20%) | 46.706: 12 (20%); 92.2837: 24 (40%); 125.5089: 36 (60%); 190.7344: 48 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 41.7853, 88.0908, 113.7698, 176.0258 | 41.7853: 48 (80%); 88.0908: 36 (60%); 113.7698: 24 (40%); 176.0258: 12 (20%) | 41.7853: 12 (20%); 88.0908: 24 (40%); 113.7698: 36 (60%); 176.0258: 48 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 37.8635, 83.0614, 107.3812, 165.7901 | 37.8635: 48 (80%); 83.0614: 36 (60%); 107.3812: 24 (40%); 165.7901: 12 (20%) | 37.8635: 12 (20%); 83.0614: 24 (40%); 107.3812: 36 (60%); 165.7901: 48 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 49.4337, 97.2979, 140.3123, 200.0554 | 49.4337: 48 (80%); 97.2979: 36 (60%); 140.3123: 24 (40%); 200.0554: 12 (20%) | 49.4337: 12 (20%); 97.2979: 24 (40%); 140.3123: 36 (60%); 200.0554: 48 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 53.1611, 101.0383, 151.068, 209.1826 | 53.1611: 48 (80%); 101.0383: 36 (60%); 151.068: 24 (40%); 209.1826: 12 (20%) | 53.1611: 12 (20%); 101.0383: 24 (40%); 151.068: 36 (60%); 209.1826: 48 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 60 (100%) | 0: 52 (87%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 60 (100%) | 0: 52 (87%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | 0.0776, 0.1065, 0.1414, 0.2049 | 0.0776: 48 (80%); 0.1065: 36 (60%); 0.1414: 24 (40%); 0.2049: 12 (20%) | 0.0776: 12 (20%); 0.1065: 25 (42%); 0.1414: 36 (60%); 0.2049: 48 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -21.672, -15.484, -13.136, -10.792 | -21.672: 48 (80%); -15.484: 36 (60%); -13.136: 24 (40%); -10.792: 12 (20%) | -21.672: 12 (20%); -15.484: 24 (40%); -13.136: 36 (60%); -10.792: 48 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 98.3% | 0.9735, 1.251, 1.4375, 1.6666 | 0.9735: 47 (78%); 1.251: 35 (58%); 1.4375: 24 (40%); 1.6666: 12 (20%) | 0.9735: 12 (20%); 1.251: 24 (40%); 1.4375: 35 (58%); 1.6666: 47 (78%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 98.3% | 6, 8, 9.8, 10 | 6: 51 (85%); 8: 42 (70%); 9.8: 24 (40%); 10: 24 (40%) | 6: 14 (23%); 8: 25 (42%); 9.8: 35 (58%); 10: 59 (98%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 98.3% | 0.2639, 0.3212, 0.3944, 0.4786 | 0.2639: 47 (78%); 0.3212: 35 (58%); 0.3944: 24 (40%); 0.4786: 12 (20%) | 0.2639: 12 (20%); 0.3212: 24 (40%); 0.3944: 35 (58%); 0.4786: 47 (78%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 98.3% | 7, 8, 10 | 7: 49 (82%); 8: 41 (68%); 10: 25 (42%) | 7: 18 (30%); 8: 25 (42%); 10: 59 (98%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 98.3% | 0.0549, 0.0692, 0.1027, 0.1367 | 0.0549: 47 (78%); 0.0692: 35 (58%); 0.1027: 24 (40%); 0.1367: 12 (20%) | 0.0549: 12 (20%); 0.0692: 24 (40%); 0.1027: 35 (58%); 0.1367: 47 (78%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 98.3% | 8, 10 | 8: 52 (87%); 10: 39 (65%) | 8: 13 (22%); 10: 59 (98%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 98.3% | -0.2653, -0.0807, 0.0668, 0.3507 | -0.2653: 47 (78%); -0.0807: 35 (58%); 0.0668: 24 (40%); 0.3507: 12 (20%) | -0.2653: 12 (20%); -0.0807: 24 (40%); 0.0668: 35 (58%); 0.3507: 47 (78%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 98.3% | 2, 3, 6, 9 | 2: 49 (82%); 3: 40 (67%); 6: 25 (42%); 9: 16 (27%) | 2: 19 (32%); 3: 25 (42%); 6: 36 (60%); 9: 50 (83%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 3.4% |
| 8k_item_5_02_filed_within_7d | 3.4% |
| above_avwap_20high | 13.3% |
| above_cam_r3 | 15.0% |
| above_cam_r4 | 13.3% |
| above_cpr | 60.0% |
| above_pivot | 51.7% |
| above_prev_high | 18.3% |
| above_prev_high_clearance_atr_05 | 10.0% |
| above_prev_low | 88.3% |
| above_r1 | 13.3% |
| above_r2 | 10.0% |
| above_vwap | 60.0% |
| above_wood_p | 71.7% |
| ad_rising | 78.3% |
| adx_cross_up | 8.3% |
| adx_cross_up_20 | 6.7% |
| adx_strong | 10.0% |
| adx_trending | 41.7% |
| ao_positive | 86.7% |
| at_key_fib | 10.0% |
| at_key_fib_wide | 13.3% |
| avwap_20high_loss_recent_3d | 61.5% |
| avwap_20high_reclaim_recent_3d | 23.1% |
| avwap_20low_reclaim_recent_3d | 6.7% |
| avwap_252low_reclaim_recent_3d | 12.1% |
| avwap_50low_reclaim_recent_3d | 5.0% |
| bb_10_20_expanding | 76.7% |
| bb_10_20_pctb_gt_75 | 86.7% |
| bb_10_20_pctb_gt_8 | 75.0% |
| bb_10_20_pctb_gt_85 | 36.7% |
| bb_10_20_pctb_gt_9 | 20.0% |
| bb_10_20_pctb_gt_95 | 11.7% |
| bb_10_20_reclaim_from_upper_recent_3d | 51.7% |
| bb_10_20_touch_upper | 10.0% |
| bb_20_15_expanding | 91.7% |
| bb_20_15_pctb_gt_75 | 96.7% |
| bb_20_15_pctb_gt_8 | 96.7% |
| bb_20_15_pctb_gt_85 | 95.0% |
| bb_20_15_pctb_gt_9 | 91.7% |
| bb_20_15_pctb_gt_95 | 86.7% |
| bb_20_15_reclaim_from_lower_recent_3d | 3.3% |
| bb_20_15_reclaim_from_upper_recent_3d | 13.3% |
| bb_20_15_touch_upper | 83.3% |
| bb_20_20_expanding | 91.7% |
| bb_20_20_pctb_gt_75 | 95.0% |
| bb_20_20_pctb_gt_8 | 91.7% |
| bb_20_20_pctb_gt_85 | 85.0% |
| bb_20_20_pctb_gt_9 | 75.0% |
| bb_20_20_pctb_gt_95 | 60.0% |
| bb_20_20_reclaim_from_lower_recent_3d | 1.7% |
| bb_20_20_reclaim_from_upper_recent_3d | 48.3% |
| bb_20_20_touch_upper | 46.7% |
| bearish_engulfing | 8.3% |
| bearish_pin_bar | 8.3% |
| below_avwap_20high | 86.7% |
| below_cam_s3 | 40.0% |
| below_cam_s4 | 16.7% |
| below_cpr | 48.3% |
| below_ema_200 | 16.9% |
| below_ema_200_break_recent_5d | 1.7% |
| below_ema_50 | 1.7% |
| below_ema_50_break_recent_5d | 1.7% |
| below_prev_high | 81.7% |
| below_prev_low | 11.7% |
| below_prev_low_clearance_atr_05 | 5.0% |
| below_s1 | 13.3% |
| below_s2 | 5.0% |
| below_sma_200 | 22.0% |
| below_sma_50 | 6.7% |
| below_vwap | 40.0% |
| blowoff_recent_3d | 15.0% |
| break_52w_high | 3.3% |
| break_52w_high_clearance_atr_05 | 1.7% |
| break_52w_high_confirmed_today | 16.7% |
| chandelier_long_bullish | 98.3% |
| chandelier_long_flip_dn | 1.7% |
| chandelier_short_flip_up | 3.3% |
| cmf_cross_dn | 11.7% |
| cmf_negative | 28.3% |
| cmf_positive | 71.7% |
| concentrated_sell | 6.7% |
| cpr_narrow | 81.7% |
| cpr_narrow_tight | 16.7% |
| cup_handle_neckline_break_retest_long | 15.0% |
| dc10_breakout_up | 20.0% |
| dc10_breakout_up_1pct | 33.3% |
| dc10_new_high | 61.7% |
| dc10_strong_breakout_up | 10.0% |
| dc20_breakout_up | 18.3% |
| dc20_new_high | 55.0% |
| dc20_resistance_break_retest_strong | 60.0% |
| defensive_leadership | 40.0% |
| director_only_buy | 1.7% |
| doji | 3.3% |
| double_bottom_detected | 13.3% |
| double_top_detected | 13.3% |
| dpi_elevated | 53.4% |
| drying_volume_on_down_turn | 48.3% |
| ema_20_50_bearish | 25.0% |
| ema_20_50_bullish | 75.0% |
| ema_20_50_golden_cross | 3.3% |
| ema_50_200_bearish | 44.1% |
| ema_50_200_bullish | 55.9% |
| ema_50_200_golden_cross | 1.7% |
| ema_9_21_bearish | 6.7% |
| ema_9_21_bullish | 93.3% |
| ema_9_21_golden_cross | 5.0% |
| evening_star | 3.3% |
| flag_bull_break_retest_long | 3.3% |
| flag_bull_broke | 3.3% |
| force_index_cross_up | 1.7% |
| gap_dn_1_5pct | 5.0% |
| gap_dn_2pct | 3.3% |
| gap_up_1_5pct | 21.7% |
| gap_up_2pct | 21.7% |
| head_shoulders_bottom_detected | 6.7% |
| head_shoulders_top_detected | 5.0% |
| house_cluster_buy | 10.0% |
| house_cluster_sell | 6.7% |
| htf_aligned_bull | 68.3% |
| htf_disagreement | 1.7% |
| hull_flip_up | 3.3% |
| ichi_above_cloud | 78.3% |
| ichi_above_cloud_break_recent_5d | 26.7% |
| ichi_below_cloud | 15.0% |
| ichi_below_cloud_break_recent_5d | 3.3% |
| ichi_cloud_thick | 90.0% |
| ichi_tk_bearish | 8.3% |
| ichi_tk_bullish | 78.3% |
| ichi_tk_cross_dn | 1.7% |
| ichi_tk_cross_up | 8.3% |
| ichi_weekly_above_cloud | 53.4% |
| ichi_weekly_below_cloud | 19.0% |
| ichi_weekly_in_cloud | 27.6% |
| inside_bar | 21.7% |
| inside_cpr | 1.7% |
| inside_kc | 35.0% |
| institutional_buy | 91.7% |
| institutional_negative | 5.0% |
| institutional_persistence_growing | 30.8% |
| institutional_persistence_strong | 46.2% |
| institutional_strong_buy | 81.7% |
| inverted_cup_handle_detected | 1.7% |
| is_friday | 13.3% |
| is_halloween_period | 53.3% |
| is_halloween_period_first_day | 1.7% |
| is_january | 11.7% |
| is_january_extended | 11.7% |
| is_monday | 21.7% |
| is_pre_holiday | 1.7% |
| is_summer_period | 46.7% |
| is_totm_window | 31.7% |
| is_totm_window_first_day | 6.7% |
| is_week_open | 26.7% |
| kc_touch_upper | 68.3% |
| macd_12_26_9_crossover_up | 5.0% |
| macd_8_21_5_crossover_up | 1.7% |
| mfi_broad_overbought | 55.0% |
| mfi_overbought | 18.3% |
| monthly_above_sma_12 | 77.6% |
| monthly_above_sma_6 | 82.8% |
| monthly_bias_bear | 10.3% |
| monthly_bias_bull | 70.7% |
| monthly_momentum_pos | 81.0% |
| near_52w_high | 18.3% |
| near_52w_high_95pct | 35.0% |
| near_avwap_20high_atr_05x | 65.4% |
| near_avwap_20high_atr_10x | 80.8% |
| near_avwap_20high_atr_15x | 92.3% |
| near_avwap_20high_atr_20x | 96.2% |
| near_avwap_20low_atr_10x | 3.3% |
| near_avwap_20low_atr_15x | 11.7% |
| near_avwap_20low_atr_20x | 36.7% |
| near_avwap_252low_atr_10x | 8.6% |
| near_avwap_252low_atr_15x | 12.1% |
| near_avwap_252low_atr_20x | 20.7% |
| near_avwap_50low_atr_15x | 3.3% |
| near_avwap_50low_atr_20x | 20.0% |
| near_cam_r3 | 5.0% |
| near_cam_s3 | 20.0% |
| near_cam_s4 | 11.7% |
| near_fib_236 | 10.0% |
| near_fib_382 | 1.7% |
| near_fib_500 | 5.0% |
| near_fib_618 | 3.3% |
| near_pivot | 21.7% |
| near_prev_close | 11.7% |
| near_prev_high | 6.7% |
| near_prev_low | 6.7% |
| near_r1 | 1.7% |
| near_r1_wide | 23.3% |
| near_r2_wide | 5.0% |
| near_s1 | 6.7% |
| near_s1_wide | 45.0% |
| near_s2_wide | 13.3% |
| near_wood_r1 | 18.3% |
| news_uses_polygon_score | 30.0% |
| obv_bearish | 5.0% |
| obv_bullish | 95.0% |
| obv_diverge_bull | 1.7% |
| obv_falling | 8.3% |
| obv_rising | 91.7% |
| outside_bar | 5.0% |
| pead_negative_surprise | 17.0% |
| pead_positive_surprise | 35.8% |
| pin_bar | 8.3% |
| po3_accumulation_active | 1.7% |
| po3_bearish | 41.7% |
| po3_manipulation_sweep_up | 1.7% |
| po3_sweep_above_prior_high | 66.7% |
| po3_sweep_below_prior_low | 20.0% |
| ppo_crossover_up | 5.0% |
| pre_fomc_d0 | 1.7% |
| pre_fomc_d1 | 3.3% |
| pre_fomc_window | 5.0% |
| price_above_dema | 98.3% |
| price_above_ema_200 | 83.1% |
| price_above_ema_200_break_recent_5d | 32.2% |
| price_above_ema_20_break_recent_5d | 40.0% |
| price_above_ema_21_break_recent_5d | 40.0% |
| price_above_ema_50 | 98.3% |
| price_above_ema_50_break_recent_5d | 38.3% |
| price_above_ema_9_break_recent_5d | 41.7% |
| price_above_hull | 96.7% |
| price_above_sma_200 | 78.0% |
| price_above_sma_50 | 93.3% |
| price_above_tema | 96.7% |
| price_below_dema | 1.7% |
| price_below_hull | 3.3% |
| price_below_tema | 3.3% |
| psar_flip_up | 3.3% |
| r1_break_retest_long | 93.3% |
| resistance_break_retest | 80.0% |
| risk_off_regime_bond_signal | 5.0% |
| risk_off_regime_bond_signal_strong | 1.7% |
| risk_off_regime_gold_signal | 28.3% |
| risk_on_regime_bond_signal | 50.0% |
| risk_on_regime_bond_signal_strong | 31.7% |
| roc_turning_up | 1.7% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 3.3% |
| rsi_14_cross_dn_overbought_recent_3d | 13.3% |
| rsi_14_extreme_ob | 6.7% |
| rsi_14_overbought | 40.0% |
| rsi_14_rising | 28.3% |
| rsi_21_cross_dn_overbought_recent_3d | 10.0% |
| rsi_21_extreme_ob | 1.7% |
| rsi_21_overbought | 23.3% |
| rsi_21_rising | 28.3% |
| rsi_2_bullish | 88.3% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 51.7% |
| rsi_2_cross_dn_overbought_recent_3d | 41.7% |
| rsi_2_cross_up_extreme_os_recent_3d | 1.7% |
| rsi_2_cross_up_oversold_recent_3d | 6.7% |
| rsi_2_extreme_ob | 48.3% |
| rsi_2_overbought | 58.3% |
| rsi_2_oversold | 1.7% |
| rsi_2_rising | 28.3% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 16.7% |
| rsi_9_cross_dn_overbought_recent_3d | 20.0% |
| rsi_9_extreme_ob | 21.7% |
| rsi_9_overbought | 61.7% |
| rsi_9_rising | 28.3% |
| s1_break_retest_short | 1.7% |
| sc_13g_filed_within_30d | 5.8% |
| shooting_star | 6.7% |
| sma_20_50_bullish | 70.0% |
| sma_50_200_bullish | 54.2% |
| sma_9_21_bullish | 83.3% |
| sma_9_21_golden_cross | 3.3% |
| smc_bos_bearish | 1.7% |
| smc_bos_bullish | 25.0% |
| smc_bos_retest_short | 5.0% |
| smc_breaker_block_bearish | 15.0% |
| smc_breaker_block_bullish | 33.3% |
| smc_choch_bearish | 3.3% |
| smc_choch_bullish | 3.3% |
| smc_equal_highs_swept | 3.3% |
| smc_equal_lows_swept | 1.7% |
| smc_fvg_bearish_active | 1.7% |
| smc_fvg_retest_long_zone | 40.0% |
| smc_fvg_retest_short_zone | 1.7% |
| smc_in_discount_zone | 15.0% |
| smc_in_premium_zone | 96.7% |
| smc_inverse_fvg_bearish | 31.7% |
| smc_liquidity_swept_up | 3.3% |
| smc_mitigation_block_short | 1.7% |
| smc_ob_bearish_active | 21.7% |
| smc_ob_bullish_active | 58.3% |
| smc_ote_long_zone | 6.7% |
| smc_ote_short_zone | 6.7% |
| squeeze_fire_up | 3.3% |
| squeeze_in | 3.3% |
| stoch_bearish_cross | 25.0% |
| stoch_broad_overbought | 90.0% |
| stoch_bullish_cross | 1.7% |
| stoch_overbought | 85.0% |
| stochrsi_cross_dn | 50.0% |
| stochrsi_cross_up | 3.3% |
| stochrsi_overbought | 73.3% |
| supertrend_flip_recent_long_5d | 1.7% |
| tema_above_dema | 91.7% |
| tema_cross_up | 3.3% |
| triangle_apex_break_retest_long | 26.7% |
| triangle_ascending_detected | 5.0% |
| triangle_descending_detected | 3.3% |
| uo_overbought | 13.3% |
| usd_strengthening | 16.7% |
| usd_weakening | 10.0% |
| vix_band_high | 25.0% |
| vix_band_low | 33.3% |
| vix_band_mid | 41.7% |
| vol_above_avg | 51.7% |
| vol_below_avg | 48.3% |
| vol_spike_12x | 35.0% |
| vol_spike_15x | 20.0% |
| vol_spike_17x | 13.3% |
| vol_spike_2x | 10.0% |
| vol_spike_2x_on_down_day_recent_3d | 1.7% |
| vol_spike_2x_on_up_day_recent_3d | 35.0% |
| vol_spike_3x | 5.0% |
| vp_above_value_area | 78.3% |
| vp_close_above_poc | 95.0% |
| vp_close_below_poc | 5.0% |
| vp_in_value_area | 21.7% |
| week_open_gap_down_15pct | 1.7% |
| week_open_gap_up_15pct | 3.3% |
| weekly_above_ema_10 | 98.3% |
| weekly_above_ema_20 | 90.0% |
| weekly_bias_bear | 1.7% |
| weekly_bias_bull | 90.0% |
| weekly_momentum_pos | 95.0% |
| williams_r_overbought | 76.7% |
| williams_r_rising | 10.0% |
| within_pead_window | 41.7% |
| within_post_deletion_window | 14.3% |
| xs_avoid_high_ivol | 42.4% |
| xs_avoid_high_max | 22.0% |
| xs_high_beta_decile | 57.6% |
| xs_low_beta_bottom_quintile | 57.6% |
| xs_low_beta_decile | 5.1% |
| xs_low_beta_top_quintile | 5.1% |
| xs_momentum_bottom_decile | 16.9% |
| xs_momentum_bottom_quintile | 32.2% |
| xs_momentum_top_decile | 15.3% |
| xs_momentum_top_quintile | 27.1% |
| xs_quality_bottom_quintile | 30.0% |
| xs_quality_top_quintile | 22.5% |
| xs_quality_top_tercile | 40.0% |
| year_high_break_retest_long | 13.3% |
| yoy_surprise_high | 57.6% |
| yoy_surprise_negative | 39.0% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 86.7% |
| committed_growth_holders | 86.7% |
| corp_donations_1y | 13.3% |
| corp_donations_count_1y | 13.3% |
| corp_donations_unique_pacs | 13.3% |
| cot_rut_commercials_pctile_3y | 51.7% |
| cot_rut_mmoney_pctile_3y | 51.7% |
| cup_handle_depth_pct | 10.0% |
| days_since_deletion | 11.7% |
| days_since_inclusion | 23.3% |
| days_to_next_holiday | 73.3% |
| days_to_rebalance | 13.3% |
| dpi_30d_avg | 96.7% |
| dpi_recent | 96.7% |
| earnings_announcement_return | 88.3% |
| gov_contracts_4q_sum | 30.0% |
| gov_contracts_last_qtr_amount | 30.0% |
| gov_contracts_qoq_growth | 30.0% |
| head_shoulders_magnitude_pct | 11.7% |
| insider_director_buyers_30d | 6.7% |
| insider_officer_buyers_30d | 6.7% |
| insider_total_shares_bought_30d | 6.7% |
| inverted_cup_handle_height_pct | 11.7% |
| lobbying_amount_1y | 73.3% |
| lobbying_amount_q | 73.3% |
| lobbying_amount_yoy | 73.3% |
| monthly_momentum_6m | 96.7% |
| otc_short_ratio_recent | 96.7% |
| otc_volume_recent | 96.7% |
| pair_half_life | 83.3% |
| pair_max_abs_zscore | 83.3% |
| pair_zscore_signed | 83.3% |
| pct_from_avwap_20high | 43.3% |
| pct_from_avwap_252low | 96.7% |
| persistent_holders_4q | 86.7% |
| persistent_holders_8q | 86.7% |
| search_volume_index_recent | 81.7% |
| search_volume_observations | 81.7% |
| search_volume_zscore_30d | 81.7% |
| total_active_holders | 86.7% |
| triangle_breakout_pct | 5.0% |
| xs_quality_decile | 66.7% |
| xs_quality_gross_profitability | 66.7% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.995), `avwap_20low` (0.999), `avwap_252low` (0.992), `avwap_50low` (0.997), `bb_10_20_lower` (0.998), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.996), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.998), `bb_20_20_lower` (0.997), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.998), `cam_r1` (0.996), `cam_r2` (0.996), `cam_r3` (0.996), `cam_r4` (0.996), `cam_s1` (0.996), `cam_s2` (0.996), `cam_s3` (0.996), `cam_s4` (0.996), `chandelier_long_value` (0.998), `chandelier_short_value` (0.998), `cpr_bottom` (0.996), `cpr_top` (0.996), `cup_handle_breakout_level` (1.0), `cup_handle_rim` (1.0), `dc10_lower` (0.997), `dc10_mid` (0.998), `dc10_upper` (0.997), `dc20_lower` (0.997), `dc20_mid` (0.999), `dc20_upper` (0.997), `dema` (0.998), `double_bottom_neckline` (1.0), `double_bottom_trough` (1.0), `double_top_neckline` (0.976), `double_top_peak` (0.976), `entry_stop_long` (0.998), `entry_stop_short` (0.996), `fib_236` (0.996), `fib_382` (0.996), `fib_500` (0.996), `fib_618` (0.996), `fib_786` (0.995), `fib_ext_127` (0.994), `fib_ext_162` (0.992), `head_shoulders_bottom_neckline` (1.0), `head_shoulders_top_neckline` (1.0), `hull_ma` (0.996), `ichi_kijun` (0.998), `ichi_senkou_a` (0.992), `ichi_senkou_b` (0.991), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (1.0), `inverted_cup_handle_rim_low` (1.0), `kc_lower` (0.998), `kc_mid` (0.999), `kc_upper` (0.998), `monthly_close` (0.997), `monthly_sma_12` (0.987), `monthly_sma_6` (0.994), `pivot` (0.996), `prev_close` (0.996), `prev_high` (0.996), `prev_low` (0.995), `psar_value` (0.996), `r1` (0.996), `r2` (0.996), `r3` (0.996), `s1` (0.996), `s2` (0.995), `s3` (0.995), `sc_13g_latest_percent_owned` (-1.0), `supertrend_value` (0.997), `swing_high` (0.995), `swing_low` (0.993), `tema` (0.996), `triangle_breakdown_pct` (1.0), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.995), `vp_value_area_high` (0.996), `vp_value_area_low` (0.994), `weekly_close` (0.997), `weekly_ema_10` (0.998), `weekly_ema_20` (0.996), `wood_p` (0.995), `wood_r1` (0.995), `wood_r2` (0.996), `wood_s1` (0.995), `wood_s2` (0.995), `year_high` (0.971), `year_low` (0.967)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | mirror of close_above_open | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1 | mirror of top_40pct | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P3 | news_count_5d >= 3 | 5 | subset-safe | no - derives offline |
| P4 | news_sentiment_5d >= 0.3 | 5 | subset-safe | no - derives offline |
| P5 | news_sentiment_shift < -0.2 | 5 | subset-safe | no - derives offline |
| P6 | pct_change_5d > 0.08 | 5 | subset-safe | no - derives offline |
| P7 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     1 x 1 x 5 x 5 x 5 x 5 x 1 = 625
offline gradings   625 level-combinations x 24 exits = 15000
ENGINE RUNS        1 (every fire-adding axis sits at production-only until its env actuator exists)
check              1 x 625 = 625
```

B-row candidates NOT in this factorial: 477 census axes join it only when REGISTERED at the T3 band review.
