# Table A - ichimoku_tk_cross

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build f8636206d | commit f8636206d at 2026-10-27 16:39:23 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** TIGHTEN | **family:** trend | **status:** NOT-STARTED | **R5 fires:** 1319 (closed fires in the exit cube: 1319 of 1319, S6-B3258) | **surviving fires (T1):** 1228 (survives_pct 0.931)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  ichi_tk_cross_dn  <- backtest/signals/technical.py
       DEFN: Ichimoku Tenkan(9) crosses above / below Kijun(26) against the prior bar (technical.py compute_ichimoku)
       knobs P1.1-P1.1 (band rows in Table A)
P2  ichi_tk_cross_up  <- backtest/signals/technical.py
       DEFN: Ichimoku Tenkan(9) crosses above / below Kijun(26) against the prior bar (technical.py compute_ichimoku)
       knobs P2.1-P2.2 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  news_sentiment_5d >= 0   [EXISTING-THRESHOLD]
P4  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_ichimoku_tk_cross (docstring and return dropped):

```python
fl = s.get('ichi_tk_cross_up')
fl = fl and s.get('news_sentiment_5d', float('-inf')) >= 0.0
fs = s.get('ichi_tk_cross_dn') and (not _short_borrow_trap_active(s))
fs = fs and s.get('news_sentiment_5d', float('-inf')) >= 0.0
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
| P1 | PRODUCER | ichi_tk_cross_dn - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | Ichimoku Tenkan(9) crosses above / below Kijun(26) against the prior bar (technical.py compute_ichimoku) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | mirror of ichi_tk_cross_up (the same periods and margin) - backtest/signals/technical.py compute_ichimoku | mirror | (9, 26) / 0 | as long, mirrored | counted on the mirrored leg - TIGHTER margin - mirrored, on the same persisted keys | the periods and a looser margin - mirrored; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | ichi_tk_cross_up - emitted by backtest/signals/technical.py; the boolean's UNDERLYING condition is bandable through its producer's internals | Ichimoku Tenkan(9) crosses above / below Kijun(26) against the prior bar (technical.py compute_ichimoku) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | Tenkan / Kijun periods - backtest/signals/technical.py compute_ichimoku | BRACKET production (Hosoda 9 / 26 on six-day weeks; 7 / 22 rescales them to five-day weeks) | (9, 26) | tenkan [7, 9, 12]; kijun [22, 26, 30] | offline 0 of 3, 0 of 3 levels - none - the midpoints at other periods are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2.2 | BAND | cross margin - Tenkan above Kijun by m on the cross bar (t > k x (1 + m)) - backtest/signals/technical.py compute_ichimoku | MEASURED - production strict t > k; levels near the R5 fires' Tenkan-over-Kijun gap (q20 0.17pct, q40 0.36pct, q60 0.62pct, q80 1.18pct of kijun) | 0.0 | 0, 0.0025, 0.005, 0.01 | offline 3 of 4 levels - TIGHTER (0.0025, 0.005, 0.01) - subset on the persisted ichi_tenkan / ichi_kijun; the level side reproduces on 1319 of 1319 R5 fires | LOOSER - adds fires; outside the band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | STRATEGY | news_sentiment_5d `>= 0` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `>= 0` | production + 2 tighter measured levels | offline 2 of 3 levels - measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P4 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | - (no band ruled) | offline 0 of 1 levels (no band ruled) - tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (the short-side borrow gate the B744 lint checks for) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (runbook section 3.6; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (module writing the key) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| news_sentiment_5d | backtest/signals/news_sentiment.py | `>= 0` | 100.0% | TIGHTER = RAISE the floor: 0.2 -> 497 (40%); 0.5695 -> 246 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (module writing the key) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/technical.py | 100.0% | 15.604, 18.686, 22.12, 26.99 | 15.604: 982 (80%); 18.686: 737 (60%); 22.12: 492 (40%); 26.99: 247 (20%) | 15.604: 246 (20%); 18.686: 491 (40%); 22.12: 739 (60%); 26.99: 983 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 19.184, 21.948, 24.632, 28.676 | 19.184: 982 (80%); 21.948: 737 (60%); 24.632: 491 (40%); 28.676: 246 (20%) | 19.184: 246 (20%); 21.948: 491 (40%); 24.632: 737 (60%); 28.676: 982 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 17.994, 20.908, 23.94, 27.586 | 17.994: 982 (80%); 20.908: 737 (60%); 23.94: 492 (40%); 27.586: 246 (20%) | 17.994: 246 (20%); 20.908: 491 (40%); 23.94: 739 (60%); 27.586: 982 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -2.1126, -0.5189, 0.1399, 1.3272 | -2.1126: 982 (80%); -0.5189: 737 (60%); 0.1399: 491 (40%); 1.3272: 246 (20%) | -2.1126: 246 (20%); -0.5189: 491 (40%); 0.1399: 737 (60%); 1.3272: 982 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.2634, 2.1889, 3.5061, 5.8886 | 1.2634: 982 (80%); 2.1889: 737 (60%); 3.5061: 491 (40%); 5.8886: 246 (20%) | 1.2634: 246 (20%); 2.1889: 491 (40%); 3.5061: 737 (60%); 5.8886: 982 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.2634, 2.1889, 3.5061, 5.8886 | 1.2634: 982 (80%); 2.1889: 737 (60%); 3.5061: 491 (40%); 5.8886: 246 (20%) | 1.2634: 246 (20%); 2.1889: 491 (40%); 3.5061: 737 (60%); 5.8886: 982 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.0044, 2.4184, 2.8528, 3.5718 | 2.0044: 982 (80%); 2.4184: 737 (60%); 2.8528: 491 (40%); 3.5718: 246 (20%) | 2.0044: 246 (20%); 2.4184: 491 (40%); 2.8528: 737 (60%); 3.5718: 982 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0514, 0.0725, 0.0978, 0.1397 | 0.0514: 983 (80%); 0.0725: 737 (60%); 0.0978: 493 (40%); 0.1397: 246 (20%) | 0.0514: 247 (20%); 0.0725: 492 (40%); 0.0978: 737 (60%); 0.1397: 982 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.1767, 0.3725, 0.6141, 0.8283 | 0.1767: 982 (80%); 0.3725: 737 (60%); 0.6141: 491 (40%); 0.8283: 246 (20%) | 0.1767: 246 (20%); 0.3725: 491 (40%); 0.6141: 737 (60%); 0.8283: 982 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0474, 0.0626, 0.0823, 0.1139 | 0.0474: 983 (80%); 0.0626: 739 (60%); 0.0823: 492 (40%); 0.1139: 247 (20%) | 0.0474: 246 (20%); 0.0626: 493 (40%); 0.0823: 737 (60%); 0.1139: 983 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.0102, 0.293, 0.5926, 0.9539 | 0.0102: 982 (80%); 0.293: 737 (60%); 0.5926: 491 (40%); 0.9539: 246 (20%) | 0.0102: 246 (20%); 0.293: 491 (40%); 0.5926: 737 (60%); 0.9539: 982 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0632, 0.0835, 0.1098, 0.1519 | 0.0632: 983 (80%); 0.0835: 738 (60%); 0.1098: 492 (40%); 0.1519: 247 (20%) | 0.0632: 246 (20%); 0.0835: 494 (40%); 0.1098: 737 (60%); 0.1519: 983 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.1326, 0.3448, 0.5695, 0.8404 | 0.1326: 982 (80%); 0.3448: 737 (60%); 0.5695: 491 (40%); 0.8404: 246 (20%) | 0.1326: 246 (20%); 0.3448: 491 (40%); 0.5695: 737 (60%); 0.8404: 982 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0508, -0.024, -0.0042, 0.0238 | -0.0508: 984 (80%); -0.024: 737 (60%); -0.0042: 492 (40%); 0.0238: 247 (20%) | -0.0508: 247 (20%); -0.024: 493 (40%); -0.0042: 740 (60%); 0.0238: 984 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1438, 0.1637, 0.1937, 0.2594 | 0.1438: 982 (80%); 0.1637: 735 (60%); 0.1937: 487 (40%); 0.2594: 241 (20%) | 0.1438: 246 (20%); 0.1637: 493 (40%); 0.1937: 741 (60%); 0.2594: 987 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1228 (100%) | 0: 1179 (96%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0878, -0.0127, 0.0506, 0.13 | -0.0878: 982 (80%); -0.0127: 737 (60%); 0.0506: 492 (40%); 0.13: 247 (20%) | -0.0878: 246 (20%); -0.0127: 491 (40%); 0.0506: 737 (60%); 0.13: 983 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 1228 (100%); 1: 471 (38%) | 0: 757 (62%); 1: 999 (81%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2387, -0.1936, -0.1572, -0.1207 | -0.2387: 983 (80%); -0.1936: 738 (60%); -0.1572: 499 (41%); -0.1207: 268 (22%) | -0.2387: 251 (20%); -0.1936: 498 (41%); -0.1572: 740 (60%); -0.1207: 994 (81%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4167, 0.5897, 0.6667, 0.7692 | 0.4167: 988 (80%); 0.5897: 762 (62%); 0.6667: 534 (43%); 0.7692: 248 (20%) | 0.4167: 255 (21%); 0.5897: 512 (42%); 0.6667: 739 (60%); 0.7692: 1001 (82%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2628, 0.4038, 0.6474, 0.8333 | 0.2628: 1011 (82%); 0.4038: 741 (60%); 0.6474: 493 (40%); 0.8333: 275 (22%) | 0.2628: 264 (21%); 0.4038: 492 (40%); 0.6474: 739 (60%); 0.8333: 985 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1119, -0.0362, 0.0355, 0.1789 | -0.1119: 985 (80%); -0.0362: 737 (60%); 0.0355: 493 (40%); 0.1789: 247 (20%) | -0.1119: 249 (20%); -0.0362: 491 (40%); 0.0355: 739 (60%); 0.1789: 983 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2436, 0.391, 0.5462, 0.741 | 0.2436: 997 (81%); 0.391: 751 (61%); 0.5462: 491 (40%); 0.741: 246 (20%) | 0.2436: 252 (21%); 0.391: 492 (40%); 0.5462: 737 (60%); 0.741: 982 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1346, 0.2821, 0.4551, 0.6731 | 0.1346: 984 (80%); 0.2821: 755 (61%); 0.4551: 510 (42%); 0.6731: 259 (21%) | 0.1346: 252 (21%); 0.2821: 492 (40%); 0.4551: 748 (61%); 0.6731: 991 (81%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.497, -0.3214, -0.0842, 0.0936 | -0.497: 983 (80%); -0.3214: 741 (60%); -0.0842: 493 (40%); 0.0936: 261 (21%) | -0.497: 263 (21%); -0.3214: 494 (40%); -0.0842: 745 (61%); 0.0936: 987 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3333, 0.5321, 0.8269, 0.9551 | 0.3333: 985 (80%); 0.5321: 760 (62%); 0.8269: 492 (40%); 0.9551: 249 (20%) | 0.3333: 258 (21%); 0.5321: 496 (40%); 0.8269: 783 (64%); 0.9551: 1017 (83%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0769, 0.3269, 0.5641, 0.8462 | 0.0769: 1008 (82%); 0.3269: 738 (60%); 0.5641: 502 (41%); 0.8462: 252 (21%) | 0.0769: 257 (21%); 0.3269: 498 (41%); 0.5641: 742 (60%); 0.8462: 987 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0694, -0.0588, -0.0424, 0 | -0.0694: 984 (80%); -0.0588: 762 (62%); -0.0424: 496 (40%); 0: 344 (28%) | -0.0694: 250 (20%); -0.0588: 500 (41%); -0.0424: 738 (60%); 0: 1198 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.368, 0.6397, 0.8654, 1 | 0.368: 982 (80%); 0.6397: 737 (60%); 0.8654: 501 (41%); 1: 286 (23%) | 0.368: 246 (20%); 0.6397: 491 (40%); 0.8654: 738 (60%); 1: 1228 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1474, 0.3077, 0.5705, 0.9103 | 0.1474: 986 (80%); 0.3077: 746 (61%); 0.5705: 522 (43%); 0.9103: 249 (20%) | 0.1474: 248 (20%); 0.3077: 500 (41%); 0.5705: 740 (60%); 0.9103: 984 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0027, 0.0423, 0.0911, 0.2309 | 0.0027: 983 (80%); 0.0423: 737 (60%); 0.0911: 494 (40%); 0.2309: 251 (20%) | 0.0027: 249 (20%); 0.0423: 491 (40%); 0.0911: 740 (60%); 0.2309: 995 (81%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4966, 0.8013, 0.9423, 0.9744 | 0.4966: 984 (80%); 0.8013: 741 (60%); 0.9423: 500 (41%); 0.9744: 288 (23%) | 0.4966: 247 (20%); 0.8013: 494 (40%); 0.9423: 740 (60%); 0.9744: 1002 (82%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0833, 0.291, 0.5833, 0.7778 | 0.0833: 983 (80%); 0.291: 737 (60%); 0.5833: 493 (40%); 0.7778: 255 (21%) | 0.0833: 260 (21%); 0.291: 491 (40%); 0.5833: 745 (61%); 0.7778: 985 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0812, -0.0169, 0.0874, 0.167 | -0.0812: 1048 (85%); -0.0169: 743 (61%); 0.0874: 496 (40%); 0.167: 248 (20%) | -0.0812: 291 (24%); -0.0169: 502 (41%); 0.0874: 755 (61%); 0.167: 984 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.1695, -0.0115, 0.0457, 0.0978 | -0.1695: 986 (80%); -0.0115: 737 (60%); 0.0457: 499 (41%); 0.0978: 251 (20%) | -0.1695: 247 (20%); -0.0115: 491 (40%); 0.0457: 741 (60%); 0.0978: 984 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3526, 0.5705, 0.7436, 0.9103 | 0.3526: 983 (80%); 0.5705: 739 (60%); 0.7436: 504 (41%); 0.9103: 258 (21%) | 0.3526: 257 (21%); 0.5705: 526 (43%); 0.7436: 742 (60%); 0.9103: 994 (81%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1564, 0.4064, 0.6282, 0.8269 | 0.1564: 982 (80%); 0.4064: 737 (60%); 0.6282: 495 (40%); 0.8269: 248 (20%) | 0.1564: 246 (20%); 0.4064: 491 (40%); 0.6282: 740 (60%); 0.8269: 1011 (82%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.062, 0.1366, 0.267, 0.5154 | 0.062: 982 (80%); 0.1366: 737 (60%); 0.267: 491 (40%); 0.5154: 246 (20%) | 0.062: 246 (20%); 0.1366: 491 (40%); 0.267: 737 (60%); 0.5154: 982 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +1 | 98.8% | 31, 61, 85, 141.6 | 31: 974 (79%); 61: 738 (60%); 85: 493 (40%); 141.6: 243 (20%) | 31: 245 (20%); 61: 492 (40%); 85: 740 (60%); 141.6: 970 (79%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 99.3% | 1.7762, 2.3277, 2.8665, 3.727 | 1.7762: 975 (79%); 2.3277: 731 (60%); 2.8665: 489 (40%); 3.727: 244 (20%) | 1.7762: 244 (20%); 2.3277: 488 (40%); 2.8665: 732 (60%); 3.727: 975 (79%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 7, 15, 23, 35 | 7: 1027 (84%); 15: 745 (61%); 23: 512 (42%); 35: 257 (21%) | 7: 256 (21%); 15: 519 (42%); 23: 742 (60%); 35: 996 (81%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 1, 2, 3 | 1: 1004 (82%); 2: 742 (60%); 3: 487 (40%) | 1: 486 (40%); 2: 741 (60%); 3: 987 (80%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.015, -0.0049, 0.0088, 0.0228 | -0.015: 984 (80%); -0.0049: 739 (60%); 0.0088: 492 (40%); 0.0228: 248 (20%) | -0.015: 253 (21%); -0.0049: 493 (40%); 0.0088: 737 (60%); 0.0228: 997 (81%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5871, 25.9254, 26.5446, 27.2494 | 24.5871: 988 (80%); 25.9254: 738 (60%); 26.5446: 498 (41%); 27.2494: 247 (20%) | 24.5871: 254 (21%); 25.9254: 493 (40%); 26.5446: 740 (60%); 27.2494: 984 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -0.7656, -0.2582, 0.035, 0.5244 | -0.7656: 982 (80%); -0.2582: 737 (60%); 0.035: 492 (40%); 0.5244: 246 (20%) | -0.7656: 246 (20%); -0.2582: 491 (40%); 0.035: 738 (60%); 0.5244: 982 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -0.5244, -0.035, 0.2582, 0.7656 | -0.5244: 982 (80%); -0.035: 738 (60%); 0.2582: 491 (40%); 0.7656: 246 (20%) | -0.5244: 246 (20%); -0.035: 492 (40%); 0.2582: 737 (60%); 0.7656: 982 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.046, -0.0134, 0.0171, 0.0611 | -0.046: 982 (80%); -0.0134: 738 (60%); 0.0171: 492 (40%); 0.0611: 248 (20%) | -0.046: 246 (20%); -0.0134: 494 (40%); 0.0171: 739 (60%); 0.0611: 983 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0431, 8.4948, 8.7885, 9.1549 | 8.0431: 982 (80%); 8.4948: 736 (60%); 8.7885: 491 (40%); 9.1549: 243 (20%) | 8.0431: 246 (20%); 8.4948: 492 (40%); 8.7885: 737 (60%); 9.1549: 985 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 1217 (99%); 1: 389 (32%) | 0: 828 (67%); 1: 1096 (89%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0 | 0: 976 (79%) | 0: 1020 (83%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.1% | 0, 1 | 0: 1217 (99%); 1: 408 (33%) | 0: 809 (66%); 1: 1059 (86%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 2, 6, 139.4, 277 | 2: 1032 (84%); 6: 742 (60%); 139.4: 491 (40%); 277: 249 (20%) | 2: 260 (21%); 6: 532 (43%); 139.4: 737 (60%); 277: 984 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 1, 5, 89, 138 | 1: 1001 (82%); 5: 738 (60%); 89: 492 (40%); 138: 249 (20%) | 1: 320 (26%); 5: 518 (42%); 89: 739 (60%); 138: 984 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.8602, -0.256, 0.1002, 0.6355 | -0.8602: 982 (80%); -0.256: 737 (60%); 0.1002: 491 (40%); 0.6355: 246 (20%) | -0.8602: 246 (20%); -0.256: 491 (40%); 0.1002: 737 (60%); 0.6355: 982 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -0.9627, -0.2602, 0.1028, 0.733 | -0.9627: 982 (80%); -0.2602: 737 (60%); 0.1028: 491 (40%); 0.733: 246 (20%) | -0.9627: 246 (20%); -0.2602: 491 (40%); 0.1028: 737 (60%); 0.733: 982 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -1.3639, -0.3627, 0.2875, 1.2507 | -1.3639: 982 (80%); -0.3627: 737 (60%); 0.2875: 491 (40%); 1.2507: 246 (20%) | -1.3639: 246 (20%); -0.3627: 491 (40%); 0.2875: 737 (60%); 1.2507: 982 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.5582, -0.142, 0.1005, 0.5058 | -0.5582: 982 (80%); -0.142: 737 (60%); 0.1005: 491 (40%); 0.5058: 246 (20%) | -0.5582: 246 (20%); -0.142: 491 (40%); 0.1005: 737 (60%); 0.5058: 982 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -0.9205, -0.2028, 0.1196, 0.6795 | -0.9205: 982 (80%); -0.2028: 737 (60%); 0.1196: 491 (40%); 0.6795: 246 (20%) | -0.9205: 246 (20%); -0.2028: 491 (40%); 0.1196: 737 (60%); 0.6795: 982 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -0.7824, -0.2221, 0.0645, 0.542 | -0.7824: 983 (80%); -0.2221: 737 (60%); 0.0645: 491 (40%); 0.542: 246 (20%) | -0.7824: 246 (20%); -0.2221: 491 (40%); 0.0645: 737 (60%); 0.542: 982 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 38.744, 46.748, 54.032, 61.722 | 38.744: 982 (80%); 46.748: 737 (60%); 54.032: 491 (40%); 61.722: 246 (20%) | 38.744: 246 (20%); 46.748: 491 (40%); 54.032: 737 (60%); 61.722: 982 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.3% | 0.004, 0.0098, 0.0189, 0.0349 | 0.004: 976 (79%); 0.0098: 729 (59%); 0.0189: 487 (40%); 0.0349: 244 (20%) | 0.004: 243 (20%); 0.0098: 490 (40%); 0.0189: 732 (60%); 0.0349: 975 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 1228 (100%); 1: 877 (71%); 3: 559 (46%); 7: 279 (23%) | 0: 351 (29%); 1: 542 (44%); 3: 770 (63%); 7: 986 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0824 | 0: 1228 (100%); 0.0824: 246 (20%) | 0: 937 (76%); 0.0824: 982 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.4286, 0.6667 | 0: 1228 (100%); 0.4286: 502 (41%); 0.6667: 277 (23%) | 0: 499 (41%); 0.4286: 738 (60%); 0.6667: 991 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 5 | 0: 1228 (100%); 1: 802 (65%); 2: 581 (47%); 5: 289 (24%) | 0: 426 (35%); 1: 647 (53%); 2: 765 (62%); 5: 991 (81%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 1228 (100%); 1: 877 (71%); 3: 559 (46%); 7: 279 (23%) | 0: 351 (29%); 1: 542 (44%); 3: 770 (63%); 7: 986 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 1228 (100%); 1: 819 (67%); 3: 518 (42%); 7: 285 (23%) | 0: 409 (33%); 1: 580 (47%); 3: 798 (65%); 7: 992 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.25, 0.3928, 0.624 | 0: 1172 (95%); 0.25: 745 (61%); 0.3928: 492 (40%); 0.624: 246 (20%) | 0: 259 (21%); 0.25: 495 (40%); 0.3928: 737 (60%); 0.624: 982 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.6008 | 0: 1203 (98%); 0.3333: 501 (41%); 0.6008: 246 (20%) | 0: 531 (43%); 0.3333: 780 (64%); 0.6008: 982 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.6008 | 0: 1203 (98%); 0.3333: 501 (41%); 0.6008: 246 (20%) | 0: 531 (43%); 0.3333: 780 (64%); 0.6008: 982 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.0545, 0, 0.1667 | -0.0545: 982 (80%); 0: 944 (77%); 0.1667: 247 (20%) | -0.0545: 246 (20%); 0: 879 (72%); 0.1667: 993 (81%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.7425, -0.4114, 0, 1.1381 | -0.7425: 982 (80%); -0.4114: 737 (60%); 0: 632 (51%); 1.1381: 246 (20%) | -0.7425: 246 (20%); -0.4114: 491 (40%); 0: 769 (63%); 1.1381: 982 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 7, 10 | 2: 1031 (84%); 4: 783 (64%); 7: 497 (40%); 10: 286 (23%) | 2: 334 (27%); 4: 549 (45%); 7: 808 (66%); 10: 990 (81%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.057, -0.0271, 0.0061, 0.061 | -0.057: 983 (80%); -0.0271: 737 (60%); 0.0061: 491 (40%); 0.061: 246 (20%) | -0.057: 245 (20%); -0.0271: 491 (40%); 0.0061: 737 (60%); 0.061: 982 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0352, -0.011, 0.0075, 0.04 | -0.0352: 982 (80%); -0.011: 734 (60%); 0.0075: 492 (40%); 0.04: 247 (20%) | -0.0352: 246 (20%); -0.011: 494 (40%); 0.0075: 736 (60%); 0.04: 982 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0315, -0.008, 0.0118, 0.0379 | -0.0315: 982 (80%); -0.008: 737 (60%); 0.0118: 491 (40%); 0.0379: 246 (20%) | -0.0315: 246 (20%); -0.008: 491 (40%); 0.0118: 737 (60%); 0.0379: 982 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -17.4542, -4.0084, 7.2006, 27.9858 | -17.4542: 982 (80%); -4.0084: 737 (60%); 7.2006: 491 (40%); 27.9858: 246 (20%) | -17.4542: 246 (20%); -4.0084: 491 (40%); 7.2006: 737 (60%); 27.9858: 982 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.0371, 0.0486, 0.0624, 0.0865 | 0.0371: 983 (80%); 0.0486: 737 (60%); 0.0624: 495 (40%); 0.0865: 246 (20%) | 0.0371: 246 (20%); 0.0486: 494 (40%); 0.0624: 737 (60%); 0.0865: 982 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.1977, 0.3898, 0.5634, 0.7638 | 0.1977: 982 (80%); 0.3898: 737 (60%); 0.5634: 491 (40%); 0.7638: 246 (20%) | 0.1977: 246 (20%); 0.3898: 491 (40%); 0.5634: 737 (60%); 0.7638: 982 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -0.9903, -0.3596, 0.1538, 0.684 | -0.9903: 982 (80%); -0.3596: 737 (60%); 0.1538: 491 (40%); 0.684: 246 (20%) | -0.9903: 246 (20%); -0.3596: 491 (40%); 0.1538: 737 (60%); 0.684: 982 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | -0.6633, -0.3444, 0.1491, 0.7887 | -0.6633: 982 (80%); -0.3444: 737 (60%); 0.1491: 491 (40%); 0.7887: 246 (20%) | -0.6633: 246 (20%); -0.3444: 491 (40%); 0.1491: 737 (60%); 0.7887: 982 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -1.4597, -0.5727, 0.3669, 1.1037 | -1.4597: 982 (80%); -0.5727: 737 (60%); 0.3669: 491 (40%); 1.1037: 246 (20%) | -1.4597: 246 (20%); -0.5727: 491 (40%); 0.3669: 737 (60%); 1.1037: 982 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -4.8478, -2.1354, 0.7788, 5.7236 | -4.8478: 982 (80%); -2.1354: 737 (60%); 0.7788: 491 (40%); 5.7236: 246 (20%) | -4.8478: 246 (20%); -2.1354: 491 (40%); 0.7788: 737 (60%); 5.7236: 982 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 41.63, 47.546, 51.57, 56.726 | 41.63: 983 (80%); 47.546: 737 (60%); 51.57: 492 (40%); 56.726: 246 (20%) | 41.63: 247 (20%); 47.546: 491 (40%); 51.57: 738 (60%); 56.726: 982 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 14.234, 36.052, 61.584, 87.372 | 14.234: 982 (80%); 36.052: 737 (60%); 61.584: 491 (40%); 87.372: 246 (20%) | 14.234: 246 (20%); 36.052: 491 (40%); 61.584: 737 (60%); 87.372: 982 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 44.372, 48.19, 51.234, 54.616 | 44.372: 982 (80%); 48.19: 739 (60%); 51.234: 491 (40%); 54.616: 246 (20%) | 44.372: 246 (20%); 48.19: 492 (40%); 51.234: 737 (60%); 54.616: 982 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 37.166, 45.91, 52.65, 61.552 | 37.166: 982 (80%); 45.91: 738 (60%); 52.65: 491 (40%); 61.552: 246 (20%) | 37.166: 246 (20%); 45.91: 492 (40%); 52.65: 737 (60%); 61.552: 982 (80%) | OFFLINE |
| sector_etf_return_pct | (no module found writing the key) | 100.0% | 0 | 0: 1227 (100%) | 0: 1227 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0313, 0.0457, 0.0577, 0.0797 | 0.0313: 983 (80%); 0.0457: 737 (60%); 0.0577: 492 (40%); 0.0797: 247 (20%) | 0.0313: 248 (20%); 0.0457: 492 (40%); 0.0577: 737 (60%); 0.0797: 983 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0813, -0.0616, -0.046, -0.034 | -0.0813: 985 (80%); -0.0616: 738 (60%); -0.046: 492 (40%); -0.034: 247 (20%) | -0.0813: 251 (20%); -0.0616: 493 (40%); -0.046: 738 (60%); -0.034: 983 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 1228 (100%); 1: 385 (31%) | 0: 843 (69%); 1: 983 (80%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.3% | 28, 45, 60, 68 | 28: 1009 (82%); 45: 747 (61%); 60: 493 (40%); 68: 254 (21%) | 28: 264 (21%); 45: 514 (42%); 60: 776 (63%); 68: 998 (81%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.6% | 0.0113, 0.017, 0.0245, 0.0379 | 0.0113: 966 (79%); 0.017: 729 (59%); 0.0245: 482 (39%); 0.0379: 242 (20%) | 0.0113: 245 (20%); 0.017: 482 (39%); 0.0245: 729 (59%); 0.0379: 969 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 100.0% | 0.2764, 0.4354, 0.5665, 0.7125 | 0.2764: 982 (80%); 0.4354: 737 (60%); 0.5665: 492 (40%); 0.7125: 246 (20%) | 0.2764: 246 (20%); 0.4354: 492 (40%); 0.5665: 737 (60%); 0.7125: 982 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 100.0% | 30.24, 54.18, 85.52, 134.92 | 30.24: 982 (80%); 54.18: 737 (60%); 85.52: 491 (40%); 134.92: 246 (20%) | 30.24: 246 (20%); 54.18: 491 (40%); 85.52: 737 (60%); 134.92: 982 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -3.8337, -0.988, 0.754, 3.195 | -3.8337: 982 (80%); -0.988: 737 (60%); 0.754: 491 (40%); 3.195: 246 (20%) | -3.8337: 246 (20%); -0.988: 491 (40%); 0.754: 737 (60%); 3.195: 982 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 22.772, 39.312, 57.02, 76.282 | 22.772: 982 (80%); 39.312: 737 (60%); 57.02: 491 (40%); 76.282: 246 (20%) | 22.772: 246 (20%); 39.312: 491 (40%); 57.02: 737 (60%); 76.282: 982 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 20.256, 39.296, 58.714, 79.564 | 20.256: 982 (80%); 39.296: 737 (60%); 58.714: 491 (40%); 79.564: 246 (20%) | 20.256: 246 (20%); 39.296: 491 (40%); 58.714: 737 (60%); 79.564: 982 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 8.27, 26.88, 59.24, 89.318 | 8.27: 982 (80%); 26.88: 737 (60%); 59.24: 491 (40%); 89.318: 246 (20%) | 8.27: 246 (20%); 26.88: 491 (40%); 59.24: 737 (60%); 89.318: 982 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 22.13, 58.954, 99.326 | 0: 1228 (100%); 22.13: 738 (60%); 58.954: 491 (40%); 99.326: 246 (20%) | 0: 267 (22%); 22.13: 492 (40%); 58.954: 737 (60%); 99.326: 982 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4.4, 9, 12, 17 | 4.4: 982 (80%); 9: 766 (62%); 12: 578 (47%); 17: 288 (23%) | 4.4: 246 (20%); 9: 529 (43%); 12: 742 (60%); 17: 992 (81%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 13, 17 | 5: 985 (80%); 9: 770 (63%); 13: 526 (43%); 17: 292 (24%) | 5: 294 (24%); 9: 513 (42%); 13: 765 (62%); 17: 994 (81%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 40.904, 48.026, 53.45, 59.2 | 40.904: 982 (80%); 48.026: 737 (60%); 53.45: 492 (40%); 59.2: 246 (20%) | 40.904: 246 (20%); 48.026: 491 (40%); 53.45: 738 (60%); 59.2: 982 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1587, 0.4246, 0.6587, 0.8571 | 0.1587: 985 (80%); 0.4246: 739 (60%); 0.6587: 498 (41%); 0.8571: 250 (20%) | 0.1587: 249 (20%); 0.4246: 503 (41%); 0.6587: 743 (61%); 0.8571: 992 (81%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.91, 17.15, 19.814, 24.5 | 14.91: 986 (80%); 17.15: 738 (60%); 19.814: 491 (40%); 24.5: 248 (20%) | 14.91: 252 (21%); 17.15: 492 (40%); 19.814: 737 (60%); 24.5: 993 (81%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 14.91, 17.15, 19.814, 24.5 | 14.91: 986 (80%); 17.15: 738 (60%); 19.814: 491 (40%); 24.5: 248 (20%) | 14.91: 252 (21%); 17.15: 492 (40%); 19.814: 737 (60%); 24.5: 993 (81%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8547, 0.8862, 0.9182, 0.9628 | 0.8547: 982 (80%); 0.8862: 737 (60%); 0.9182: 494 (40%); 0.9628: 246 (20%) | 0.8547: 246 (20%); 0.8862: 513 (42%); 0.9182: 741 (60%); 0.9628: 982 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.68, 0.82, 0.99, 1.27 | 0.68: 984 (80%); 0.82: 753 (61%); 0.99: 495 (40%); 1.27: 251 (20%) | 0.68: 256 (21%); 0.82: 499 (41%); 0.99: 744 (61%); 1.27: 984 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 100.0% | 0.009, 0.023, 0.0419, 0.0758 | 0.009: 983 (80%); 0.023: 738 (60%); 0.0419: 492 (40%); 0.0758: 246 (20%) | 0.009: 248 (20%); 0.023: 494 (40%); 0.0419: 737 (60%); 0.0758: 983 (80%) | OFFLINE |
| vwap | backtest/signals/technical.py | 100.0% | 50.536, 80.6833, 127.7216, 208.1809 | 50.536: 982 (80%); 80.6833: 737 (60%); 127.7216: 491 (40%); 208.1809: 246 (20%) | 50.536: 246 (20%); 80.6833: 491 (40%); 127.7216: 737 (60%); 208.1809: 982 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 49.2871, 78.363, 124.5109, 202.1791 | 49.2871: 982 (80%); 78.363: 737 (60%); 124.5109: 491 (40%); 202.1791: 246 (20%) | 49.2871: 246 (20%); 78.363: 491 (40%); 124.5109: 737 (60%); 202.1791: 982 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 47.7621, 76.4487, 120.5246, 195.7187 | 47.7621: 982 (80%); 76.4487: 737 (60%); 120.5246: 491 (40%); 195.7187: 246 (20%) | 47.7621: 246 (20%); 76.4487: 491 (40%); 120.5246: 737 (60%); 195.7187: 982 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 52.0164, 83.1273, 131.2232, 213.7248 | 52.0164: 982 (80%); 83.1273: 737 (60%); 131.2232: 491 (40%); 213.7248: 246 (20%) | 52.0164: 246 (20%); 83.1273: 491 (40%); 131.2232: 737 (60%); 213.7248: 982 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 52.9352, 84.7383, 134.058, 219.5734 | 52.9352: 982 (80%); 84.7383: 737 (60%); 134.058: 491 (40%); 219.5734: 246 (20%) | 52.9352: 246 (20%); 84.7383: 491 (40%); 134.058: 737 (60%); 219.5734: 982 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1228 (100%) | 0: 1114 (91%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1228 (100%) | 0: 1092 (89%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0389, -0.0151, 0.0068, 0.0437 | -0.0389: 983 (80%); -0.0151: 739 (60%); 0.0068: 492 (40%); 0.0437: 246 (20%) | -0.0389: 246 (20%); -0.0151: 492 (40%); 0.0068: 737 (60%); 0.0437: 982 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -86.18, -65, -39.972, -14.1 | -86.18: 982 (80%); -65: 737 (60%); -39.972: 491 (40%); -14.1: 246 (20%) | -86.18: 246 (20%); -65: 491 (40%); -39.972: 737 (60%); -14.1: 982 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.1% | 0.5118, 0.7815, 0.9884, 1.2749 | 0.5118: 973 (79%); 0.7815: 730 (59%); 0.9884: 487 (40%); 1.2749: 244 (20%) | 0.5118: 244 (20%); 0.7815: 487 (40%); 0.9884: 730 (59%); 1.2749: 973 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 5, 7, 9 | 3: 999 (81%); 5: 754 (61%); 7: 511 (42%); 9: 268 (22%) | 3: 335 (27%); 5: 593 (48%); 7: 817 (67%); 9: 1077 (88%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 99.1% | 0.1887, 0.2263, 0.2775, 0.3502 | 0.1887: 973 (79%); 0.2263: 731 (60%); 0.2775: 487 (40%); 0.3502: 244 (20%) | 0.1887: 244 (20%); 0.2263: 488 (40%); 0.2775: 730 (59%); 0.3502: 975 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 5, 7, 9 | 3: 1019 (83%); 5: 813 (66%); 7: 567 (46%); 9: 316 (26%) | 3: 307 (25%); 5: 536 (44%); 7: 766 (62%); 9: 1054 (86%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.1% | 0.0213, 0.0294, 0.0386, 0.0563 | 0.0213: 977 (80%); 0.0294: 733 (60%); 0.0386: 487 (40%); 0.0563: 245 (20%) | 0.0213: 246 (20%); 0.0294: 487 (40%); 0.0386: 730 (59%); 0.0563: 974 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.1% | 3, 5, 7, 9 | 3: 983 (80%); 5: 765 (62%); 7: 523 (43%); 9: 290 (24%) | 3: 347 (28%); 5: 579 (47%); 7: 797 (65%); 9: 1061 (86%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.3% | -0.1922, -0.0506, 0.0863, 0.2826 | -0.1922: 975 (79%); -0.0506: 732 (60%); 0.0863: 488 (40%); 0.2826: 244 (20%) | -0.1922: 244 (20%); -0.0506: 488 (40%); 0.0863: 731 (60%); 0.2826: 975 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.3% | 2, 4, 6, 9 | 2: 1071 (87%); 4: 817 (67%); 6: 578 (47%); 9: 272 (22%) | 2: 281 (23%); 4: 539 (44%); 6: 739 (60%); 9: 1075 (88%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 6.1% |
| 8k_item_5_02_filed_within_7d | 3.5% |
| above_avwap_20high | 40.4% |
| above_avwap_20low | 65.0% |
| above_avwap_252low | 73.7% |
| above_avwap_50low | 70.7% |
| above_cam_r3 | 30.6% |
| above_cam_r4 | 17.9% |
| above_cpr | 48.9% |
| above_pivot | 48.5% |
| above_prev_high | 23.8% |
| above_prev_high_clearance_atr_05 | 9.4% |
| above_prev_low | 73.9% |
| above_r1 | 20.0% |
| above_r2 | 10.7% |
| above_vwap | 52.2% |
| above_wood_p | 49.1% |
| ad_rising | 54.0% |
| adx_cross_up | 0.7% |
| adx_cross_up_20 | 1.4% |
| adx_di_bear | 54.4% |
| adx_di_bull | 45.6% |
| adx_strong | 1.2% |
| adx_trending | 27.2% |
| ao_cross_dn | 6.3% |
| ao_cross_up | 6.2% |
| ao_positive | 43.9% |
| ao_twin_peaks_bull | 5.0% |
| at_key_fib | 22.9% |
| at_key_fib_wide | 52.0% |
| avwap_20high_loss_recent_3d | 19.5% |
| avwap_20high_reclaim_recent_3d | 17.8% |
| avwap_20low_loss_recent_3d | 20.2% |
| avwap_20low_reclaim_recent_3d | 18.6% |
| avwap_252low_loss_recent_3d | 8.2% |
| avwap_252low_reclaim_recent_3d | 8.7% |
| avwap_50low_loss_recent_3d | 18.7% |
| avwap_50low_reclaim_recent_3d | 15.1% |
| bb_10_20_above_mid | 48.5% |
| bb_10_20_expanding | 44.9% |
| bb_10_20_pctb_gt_75 | 26.1% |
| bb_10_20_pctb_gt_8 | 22.9% |
| bb_10_20_pctb_gt_85 | 18.5% |
| bb_10_20_pctb_gt_9 | 14.7% |
| bb_10_20_pctb_gt_95 | 11.2% |
| bb_10_20_pctb_lt_05 | 8.8% |
| bb_10_20_pctb_lt_1 | 12.2% |
| bb_10_20_pctb_lt_15 | 16.5% |
| bb_10_20_pctb_lt_2 | 22.1% |
| bb_10_20_pctb_lt_25 | 26.8% |
| bb_10_20_reclaim_from_lower_recent_3d | 6.5% |
| bb_10_20_reclaim_from_upper_recent_3d | 4.1% |
| bb_10_20_squeeze | 46.5% |
| bb_10_20_touch_lower | 10.0% |
| bb_10_20_touch_upper | 12.0% |
| bb_20_15_above_mid | 45.4% |
| bb_20_15_expanding | 65.8% |
| bb_20_15_pctb_gt_75 | 31.1% |
| bb_20_15_pctb_gt_8 | 28.9% |
| bb_20_15_pctb_gt_85 | 26.5% |
| bb_20_15_pctb_gt_9 | 23.4% |
| bb_20_15_pctb_gt_95 | 20.4% |
| bb_20_15_pctb_lt_05 | 23.3% |
| bb_20_15_pctb_lt_1 | 27.7% |
| bb_20_15_pctb_lt_15 | 30.9% |
| bb_20_15_pctb_lt_2 | 34.2% |
| bb_20_15_pctb_lt_25 | 37.9% |
| bb_20_15_reclaim_from_lower_recent_3d | 10.1% |
| bb_20_15_reclaim_from_upper_recent_3d | 6.4% |
| bb_20_15_squeeze | 57.7% |
| bb_20_15_touch_lower | 26.5% |
| bb_20_15_touch_upper | 21.9% |
| bb_20_20_above_mid | 45.4% |
| bb_20_20_expanding | 65.8% |
| bb_20_20_pctb_gt_75 | 27.2% |
| bb_20_20_pctb_gt_8 | 23.4% |
| bb_20_20_pctb_gt_85 | 19.5% |
| bb_20_20_pctb_gt_9 | 16.8% |
| bb_20_20_pctb_gt_95 | 13.0% |
| bb_20_20_pctb_lt_05 | 11.8% |
| bb_20_20_pctb_lt_1 | 16.4% |
| bb_20_20_pctb_lt_15 | 21.9% |
| bb_20_20_pctb_lt_2 | 27.7% |
| bb_20_20_pctb_lt_25 | 31.8% |
| bb_20_20_reclaim_from_lower_recent_3d | 6.5% |
| bb_20_20_reclaim_from_upper_recent_3d | 3.3% |
| bb_20_20_squeeze | 36.7% |
| bb_20_20_touch_lower | 12.5% |
| bb_20_20_touch_upper | 13.0% |
| bearish_engulfing | 3.3% |
| bearish_pin_bar | 5.8% |
| below_avwap_20high | 59.6% |
| below_avwap_20low | 35.0% |
| below_avwap_252low | 26.3% |
| below_avwap_50low | 29.3% |
| below_cam_s3 | 34.4% |
| below_cam_s4 | 18.9% |
| below_cpr | 51.5% |
| below_ema_20 | 52.5% |
| below_ema_200 | 53.0% |
| below_ema_200_break_recent_5d | 7.9% |
| below_ema_20_break_recent_5d | 33.6% |
| below_ema_21 | 52.3% |
| below_ema_21_break_recent_5d | 33.6% |
| below_ema_50 | 51.5% |
| below_ema_50_break_recent_5d | 20.0% |
| below_ema_9 | 51.9% |
| below_ema_9_break_recent_5d | 31.4% |
| below_prev_high | 76.0% |
| below_prev_low | 25.7% |
| below_prev_low_clearance_atr_05 | 9.3% |
| below_s1 | 22.1% |
| below_s2 | 10.3% |
| below_sma_20 | 54.5% |
| below_sma_200 | 52.2% |
| below_sma_21 | 54.4% |
| below_sma_50 | 51.1% |
| below_sma_9 | 49.9% |
| below_vwap | 47.8% |
| blowoff_recent_3d | 0.2% |
| break_52w_high | 0.5% |
| break_52w_high_clearance_atr_05 | 0.2% |
| break_52w_low | 0.2% |
| bullish_engulfing | 1.7% |
| bullish_pin_bar | 7.1% |
| capitulation_recent_3d | 0.2% |
| ceo_buy | 0.7% |
| cfo_buy | 0.2% |
| chandelier_long_bullish | 71.8% |
| chandelier_long_flip_dn | 8.5% |
| chandelier_short_bearish | 72.4% |
| chandelier_short_flip_up | 8.1% |
| classification_change_from_tech | 80.0% |
| classification_change_to_defensive | 20.0% |
| close_above_open | 42.6% |
| close_below_open | 57.4% |
| close_in_bottom_40pct_of_range | 41.1% |
| close_in_top_40pct_of_range | 36.1% |
| cluster_buy | 0.5% |
| cmf_cross_dn | 7.0% |
| cmf_cross_up | 5.4% |
| cmf_negative | 44.5% |
| cmf_positive | 55.4% |
| concentrated_sell | 6.4% |
| cpr_narrow | 86.8% |
| cpr_narrow_tight | 23.7% |
| cup_handle_detected | 13.7% |
| cup_handle_neckline_break_retest_long | 1.1% |
| dc10_breakout_dn | 15.0% |
| dc10_breakout_dn_1pct | 21.7% |
| dc10_breakout_up | 16.3% |
| dc10_breakout_up_1pct | 21.8% |
| dc10_new_high | 21.3% |
| dc10_strong_breakout_dn | 6.1% |
| dc10_strong_breakout_up | 6.7% |
| dc20_breakout_dn | 9.6% |
| dc20_breakout_up | 11.5% |
| dc20_new_high | 15.1% |
| dc20_resistance_break_retest_strong | 3.0% |
| dc20_support_break_retest_strong | 7.1% |
| defensive_leadership | 52.5% |
| director_only_buy | 2.8% |
| doji | 5.5% |
| double_bottom_detected | 15.4% |
| double_top_detected | 17.1% |
| dpi_elevated | 57.7% |
| drying_volume_on_down_turn | 33.9% |
| drying_volume_on_up_turn | 27.3% |
| ema_20_50_bearish | 52.0% |
| ema_20_50_bullish | 48.0% |
| ema_20_50_death_cross | 1.0% |
| ema_20_50_golden_cross | 0.5% |
| ema_50_200_bearish | 50.7% |
| ema_50_200_bullish | 49.3% |
| ema_50_200_death_cross | 0.2% |
| ema_50_200_golden_cross | 0.2% |
| ema_9_21_bearish | 52.2% |
| ema_9_21_bullish | 47.8% |
| ema_9_21_death_cross | 7.1% |
| ema_9_21_golden_cross | 8.6% |
| evening_star | 4.8% |
| flag_bear_break_retest_short | 0.2% |
| flag_bear_broke | 0.2% |
| flag_bear_detected | 0.8% |
| flag_bull_break_retest_long | 0.3% |
| flag_bull_broke | 0.6% |
| flag_bull_detected | 0.3% |
| force_index_cross_dn | 6.7% |
| force_index_cross_up | 4.8% |
| force_index_positive | 44.1% |
| gap_dn_1_5pct | 7.2% |
| gap_dn_2pct | 4.4% |
| gap_up_1_5pct | 8.4% |
| gap_up_2pct | 5.7% |
| hammer | 5.5% |
| head_shoulders_bottom_detected | 3.7% |
| head_shoulders_top_detected | 2.7% |
| house_cluster_buy | 4.3% |
| house_cluster_sell | 5.3% |
| htf_aligned_bear | 32.5% |
| htf_aligned_bull | 27.6% |
| htf_disagreement | 3.3% |
| hull_bearish | 52.3% |
| hull_bullish | 47.7% |
| hull_flip_dn | 4.3% |
| hull_flip_up | 4.8% |
| ichi_above_cloud | 40.6% |
| ichi_above_cloud_break_recent_5d | 7.7% |
| ichi_below_cloud | 43.9% |
| ichi_below_cloud_break_recent_5d | 7.8% |
| ichi_cloud_thick | 85.7% |
| ichi_tk_bearish | 57.4% |
| ichi_tk_bullish | 42.6% |
| ichi_tk_cross_dn | 57.4% |
| ichi_tk_cross_up | 42.6% |
| ichi_weekly_above_cloud | 40.7% |
| ichi_weekly_below_cloud | 36.0% |
| ichi_weekly_in_cloud | 23.3% |
| in_reversal_window | 1.8% |
| inside_bar | 11.6% |
| inside_cpr | 2.2% |
| inside_kc | 89.9% |
| insider_cluster_active | 21.8% |
| institutional_buy | 87.6% |
| institutional_negative | 5.3% |
| institutional_persistence_growing | 44.1% |
| institutional_persistence_strong | 61.4% |
| institutional_strong_buy | 78.8% |
| inverted_cup_handle_detected | 12.8% |
| is_friday | 19.6% |
| is_halloween_period | 54.0% |
| is_halloween_period_first_day | 0.2% |
| is_january | 8.3% |
| is_january_extended | 12.7% |
| is_monday | 18.2% |
| is_pre_holiday | 4.4% |
| is_summer_period | 46.0% |
| is_totm_window | 34.6% |
| is_totm_window_first_day | 11.6% |
| is_week_open | 21.5% |
| kc_touch_lower | 7.1% |
| kc_touch_upper | 5.9% |
| large_dollar_buy | 1.0% |
| macd_12_26_9_bearish | 54.9% |
| macd_12_26_9_bullish | 45.1% |
| macd_12_26_9_crossover_dn | 1.5% |
| macd_12_26_9_crossover_up | 2.0% |
| macd_8_21_5_bearish | 52.2% |
| macd_8_21_5_bullish | 47.8% |
| macd_8_21_5_crossover_dn | 2.2% |
| macd_8_21_5_crossover_up | 3.4% |
| marubozu_bear | 0.7% |
| marubozu_bull | 1.0% |
| mfi_broad_overbought | 7.0% |
| mfi_broad_oversold | 6.2% |
| mfi_overbought | 1.2% |
| mfi_oversold | 1.1% |
| monthly_above_sma_12 | 47.1% |
| monthly_above_sma_6 | 46.7% |
| monthly_bias_bear | 43.7% |
| monthly_bias_bull | 37.5% |
| monthly_momentum_pos | 48.2% |
| morning_star | 2.9% |
| near_52w_high | 1.3% |
| near_52w_high_95pct | 10.7% |
| near_52w_high_retest_long | 0.2% |
| near_52w_low | 0.7% |
| near_52w_low_105pct | 3.5% |
| near_52w_low_retest_short | 0.1% |
| near_avwap_20high_atr_05x | 36.5% |
| near_avwap_20high_atr_10x | 62.6% |
| near_avwap_20high_atr_15x | 80.6% |
| near_avwap_20high_atr_20x | 91.1% |
| near_avwap_20low_atr_05x | 41.9% |
| near_avwap_20low_atr_10x | 61.7% |
| near_avwap_20low_atr_15x | 76.8% |
| near_avwap_20low_atr_20x | 86.1% |
| near_avwap_252low_atr_05x | 15.3% |
| near_avwap_252low_atr_10x | 29.1% |
| near_avwap_252low_atr_15x | 40.3% |
| near_avwap_252low_atr_20x | 49.7% |
| near_avwap_50low_atr_05x | 26.0% |
| near_avwap_50low_atr_10x | 49.4% |
| near_avwap_50low_atr_15x | 68.4% |
| near_avwap_50low_atr_20x | 80.2% |
| near_cam_r3 | 15.3% |
| near_cam_s3 | 19.1% |
| near_cam_s4 | 11.6% |
| near_fib_236 | 5.7% |
| near_fib_382 | 8.2% |
| near_fib_500 | 8.4% |
| near_fib_618 | 6.6% |
| near_fib_786 | 4.2% |
| near_pivot | 16.7% |
| near_prev_close | 17.7% |
| near_prev_high | 10.7% |
| near_prev_low | 12.5% |
| near_r1 | 11.1% |
| near_r1_wide | 51.2% |
| near_r2 | 3.7% |
| near_r2_wide | 28.7% |
| near_s1 | 14.1% |
| near_s1_wide | 53.6% |
| near_s2 | 5.0% |
| near_s2_wide | 31.0% |
| near_s3 | 2.4% |
| near_wood_r1 | 10.2% |
| near_wood_s1 | 12.6% |
| news_uses_polygon_score | 23.0% |
| obv_bearish | 50.7% |
| obv_bullish | 49.3% |
| obv_diverge_bull | 8.6% |
| obv_falling | 49.8% |
| obv_rising | 50.2% |
| outside_bar | 6.8% |
| pead_negative_surprise | 15.0% |
| pead_positive_surprise | 25.0% |
| pin_bar | 12.9% |
| po3_accumulation_active | 43.0% |
| po3_bearish | 10.7% |
| po3_bullish | 5.9% |
| po3_manipulation_sweep_down | 12.8% |
| po3_manipulation_sweep_up | 11.1% |
| po3_mmbm_setup | 2.0% |
| po3_mmsm_setup | 2.3% |
| po3_sweep_above_prior_high | 51.9% |
| po3_sweep_below_prior_low | 48.9% |
| ppo_bullish | 44.9% |
| ppo_crossover_dn | 1.6% |
| ppo_crossover_up | 1.9% |
| pre_fomc_d0 | 3.2% |
| pre_fomc_d1 | 2.5% |
| pre_fomc_window | 5.7% |
| price_above_dema | 47.1% |
| price_above_ema_20 | 47.5% |
| price_above_ema_200 | 47.0% |
| price_above_ema_200_break_recent_5d | 7.1% |
| price_above_ema_20_break_recent_5d | 34.8% |
| price_above_ema_21 | 47.7% |
| price_above_ema_21_break_recent_5d | 35.0% |
| price_above_ema_50 | 48.5% |
| price_above_ema_50_break_recent_5d | 23.0% |
| price_above_ema_9 | 48.1% |
| price_above_ema_9_break_recent_5d | 32.0% |
| price_above_hull | 53.4% |
| price_above_sma_200 | 47.8% |
| price_above_sma_21 | 45.6% |
| price_above_sma_50 | 48.9% |
| price_above_tema | 49.8% |
| price_below_dema | 52.9% |
| price_below_hull | 46.6% |
| price_below_tema | 50.2% |
| psar_bullish | 46.3% |
| psar_flip_dn | 4.3% |
| psar_flip_up | 4.1% |
| r1_break_retest_long | 52.9% |
| recent_blowoff_at_r3 | 0.1% |
| resistance_break_retest | 7.7% |
| risk_off_regime_bond_signal | 21.7% |
| risk_off_regime_bond_signal_strong | 7.1% |
| risk_off_regime_gold_signal | 37.5% |
| risk_on_regime_bond_signal | 44.5% |
| risk_on_regime_bond_signal_strong | 20.8% |
| roc_positive | 44.9% |
| roc_turning_dn | 7.2% |
| roc_turning_up | 5.8% |
| rsi_14_bullish | 49.1% |
| rsi_14_cross_up_oversold_recent_3d | 0.4% |
| rsi_14_extreme_ob | 0.1% |
| rsi_14_overbought | 1.0% |
| rsi_14_oversold | 1.2% |
| rsi_14_rising | 47.2% |
| rsi_21_bullish | 49.0% |
| rsi_21_cross_up_oversold_recent_3d | 0.2% |
| rsi_21_extreme_ob | 0.1% |
| rsi_21_extreme_os | 0.1% |
| rsi_21_overbought | 0.2% |
| rsi_21_oversold | 0.2% |
| rsi_21_rising | 47.3% |
| rsi_2_bullish | 48.7% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 26.3% |
| rsi_2_cross_dn_overbought_recent_3d | 34.9% |
| rsi_2_cross_up_extreme_os_recent_3d | 22.9% |
| rsi_2_cross_up_oversold_recent_3d | 28.9% |
| rsi_2_extreme_ob | 26.5% |
| rsi_2_extreme_os | 25.5% |
| rsi_2_overbought | 33.0% |
| rsi_2_oversold | 33.6% |
| rsi_2_rising | 47.2% |
| rsi_9_bullish | 47.1% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 0.1% |
| rsi_9_cross_dn_overbought_recent_3d | 0.8% |
| rsi_9_cross_up_extreme_os_recent_3d | 0.4% |
| rsi_9_cross_up_oversold_recent_3d | 2.7% |
| rsi_9_extreme_ob | 0.7% |
| rsi_9_extreme_os | 1.0% |
| rsi_9_overbought | 7.4% |
| rsi_9_oversold | 7.1% |
| rsi_9_rising | 47.2% |
| s1_break_retest_short | 57.6% |
| sc_13d_filed_within_30d | 2.9% |
| sc_13g_filed_within_30d | 2.7% |
| sector_outperforming_spy | 23.5% |
| sector_underperforming_spy | 76.5% |
| shooting_star | 4.2% |
| sma_20_50_bullish | 50.9% |
| sma_20_50_golden_cross | 0.5% |
| sma_50_200_bullish | 49.8% |
| sma_50_200_golden_cross | 0.5% |
| sma_9_21_bullish | 45.8% |
| sma_9_21_golden_cross | 5.8% |
| smc_bos_bearish | 10.6% |
| smc_bos_bullish | 9.4% |
| smc_bos_retest_long | 4.0% |
| smc_bos_retest_short | 4.4% |
| smc_breaker_block_bearish | 16.0% |
| smc_breaker_block_bullish | 22.1% |
| smc_choch_bearish | 4.2% |
| smc_choch_bullish | 2.2% |
| smc_equal_highs_swept | 3.5% |
| smc_equal_lows_swept | 4.2% |
| smc_fvg_bearish_active | 35.6% |
| smc_fvg_bullish_active | 38.8% |
| smc_fvg_retest_long_zone | 6.3% |
| smc_fvg_retest_short_zone | 3.9% |
| smc_in_discount_zone | 64.8% |
| smc_in_premium_zone | 63.5% |
| smc_inverse_fvg_bearish | 90.4% |
| smc_inverse_fvg_bullish | 86.0% |
| smc_liquidity_swept_dn | 0.7% |
| smc_liquidity_swept_up | 0.8% |
| smc_mitigation_block_long | 0.6% |
| smc_mitigation_block_short | 1.0% |
| smc_ob_bearish_active | 35.4% |
| smc_ob_bullish_active | 29.1% |
| smc_ote_long_zone | 7.3% |
| smc_ote_short_zone | 7.6% |
| squeeze_fire_dn | 2.9% |
| squeeze_fire_up | 2.1% |
| squeeze_in | 40.2% |
| squeeze_positive | 48.1% |
| stoch_bearish_cross | 10.4% |
| stoch_broad_overbought | 24.5% |
| stoch_broad_oversold | 25.4% |
| stoch_bullish_cross | 9.6% |
| stoch_overbought | 19.4% |
| stoch_oversold | 19.8% |
| stochrsi_cross_dn | 19.6% |
| stochrsi_cross_up | 19.9% |
| stochrsi_overbought | 30.0% |
| stochrsi_oversold | 37.9% |
| supertrend_bearish | 1.5% |
| supertrend_bullish | 98.5% |
| supertrend_flip_dn | 1.0% |
| supertrend_flip_recent_long_5d | 2.5% |
| supertrend_flip_recent_short_5d | 1.9% |
| supertrend_flip_up | 0.3% |
| support_break_retest | 12.2% |
| tema_above_dema | 44.9% |
| tema_cross_dn | 1.9% |
| tema_cross_up | 1.5% |
| three_black_crows | 5.9% |
| three_white_soldiers | 5.0% |
| triangle_apex_break_retest_long | 7.3% |
| triangle_ascending_detected | 17.3% |
| triangle_descending_detected | 17.2% |
| uo_overbought | 1.9% |
| uo_oversold | 0.9% |
| usd_strengthening | 24.3% |
| usd_weakening | 12.5% |
| vix_band_high | 39.4% |
| vix_band_low | 34.2% |
| vix_band_mid | 26.4% |
| vix_term_backwardation | 9.0% |
| vix_term_contango | 91.0% |
| vol_above_avg | 38.8% |
| vol_below_avg | 61.2% |
| vol_spike_12x | 23.9% |
| vol_spike_15x | 11.6% |
| vol_spike_17x | 8.1% |
| vol_spike_2x | 4.5% |
| vol_spike_2x_on_down_day_recent_3d | 2.4% |
| vol_spike_2x_on_up_day_recent_3d | 2.2% |
| vol_spike_3x | 1.2% |
| vp_above_value_area | 9.0% |
| vp_below_value_area | 10.3% |
| vp_close_above_poc | 49.1% |
| vp_close_below_poc | 50.9% |
| vp_in_value_area | 80.8% |
| week_open_gap_down_15pct | 1.6% |
| week_open_gap_up_15pct | 1.7% |
| weekly_above_ema_10 | 48.3% |
| weekly_above_ema_20 | 46.7% |
| weekly_bias_bear | 43.2% |
| weekly_bias_bull | 38.3% |
| weekly_momentum_pos | 45.2% |
| williams_r_overbought | 25.7% |
| williams_r_oversold | 25.9% |
| williams_r_rising | 47.5% |
| within_pead_window | 39.2% |
| within_post_deletion_window | 1.1% |
| within_post_inclusion_window | 1.2% |
| xs_avoid_high_ivol | 74.0% |
| xs_avoid_high_max | 76.2% |
| xs_high_beta_decile | 22.0% |
| xs_low_beta_bottom_quintile | 22.0% |
| xs_low_beta_decile | 17.9% |
| xs_low_beta_decile_entry_recent_5d | 0.4% |
| xs_low_beta_top_quintile | 17.9% |
| xs_momentum_bottom_decile | 12.1% |
| xs_momentum_bottom_quintile | 23.1% |
| xs_momentum_top_decile | 11.8% |
| xs_momentum_top_quintile | 22.3% |
| xs_quality_bottom_quintile | 21.0% |
| xs_quality_top_quintile | 22.4% |
| xs_quality_top_tercile | 40.7% |
| year_low_break_retest_short | 0.7% |
| yoy_surprise_high | 54.8% |
| yoy_surprise_negative | 33.6% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 90.6% |
| committed_growth_holders | 90.6% |
| corp_donations_1y | 6.1% |
| corp_donations_count_1y | 6.1% |
| corp_donations_unique_pacs | 6.1% |
| cot_rut_commercials_pctile_3y | 57.5% |
| cot_rut_mmoney_pctile_3y | 57.5% |
| cup_handle_depth_pct | 17.3% |
| days_since_classification_change | 0.4% |
| days_since_deletion | 7.4% |
| days_since_inclusion | 13.6% |
| days_to_next_holiday | 63.8% |
| days_to_rebalance | 9.3% |
| dpi_30d_avg | 95.2% |
| dpi_recent | 95.2% |
| earnings_announcement_return | 92.6% |
| earnings_eps_yoy_growth | 95.4% |
| flag_bear_pole_move_pct | 0.8% |
| flag_bull_pole_move_pct | 0.3% |
| gov_contracts_4q_sum | 39.8% |
| gov_contracts_last_qtr_amount | 39.8% |
| gov_contracts_qoq_growth | 39.8% |
| head_shoulders_magnitude_pct | 6.2% |
| insider_director_buyers_30d | 4.5% |
| insider_officer_buyers_30d | 4.5% |
| insider_total_shares_bought_30d | 4.5% |
| insider_unique_buyers_30d | 4.5% |
| inverted_cup_handle_height_pct | 15.8% |
| lobbying_amount_1y | 67.4% |
| lobbying_amount_q | 67.4% |
| lobbying_amount_yoy | 67.4% |
| monthly_momentum_6m | 97.6% |
| otc_short_ratio_recent | 95.2% |
| otc_volume_recent | 95.2% |
| pair_half_life | 91.3% |
| pair_max_abs_zscore | 91.3% |
| pair_zscore_signed | 91.3% |
| pct_from_avwap_20high | 84.3% |
| pct_from_avwap_20low | 85.3% |
| pct_from_avwap_252low | 97.1% |
| pct_from_avwap_50low | 97.3% |
| persistent_holders_4q | 90.6% |
| persistent_holders_8q | 90.6% |
| sc_13g_latest_percent_owned | 1.1% |
| search_volume_index_recent | 76.7% |
| search_volume_observations | 76.7% |
| search_volume_zscore_30d | 76.7% |
| sector_etf_return_20d | 2.8% |
| spy_return_20d | 2.8% |
| total_active_holders | 90.6% |
| triangle_breakdown_pct | 17.2% |
| triangle_breakout_pct | 17.3% |
| xs_quality_decile | 63.8% |
| xs_quality_gross_profitability | 63.8% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.999), `avwap_252low` (0.993), `avwap_50low` (0.999), `bb_10_20_lower` (0.999), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (1.0), `bb_20_15_mid` (1.0), `bb_20_15_upper` (1.0), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (1.0), `chandelier_short_value` (1.0), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.998), `dc10_lower` (0.999), `dc10_mid` (1.0), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (1.0), `double_bottom_neckline` (0.999), `double_bottom_trough` (0.999), `double_top_neckline` (0.998), `double_top_peak` (0.999), `entry_stop_long` (0.998), `entry_stop_short` (0.998), `fib_236` (0.996), `fib_382` (0.997), `fib_500` (0.997), `fib_618` (0.998), `fib_786` (0.997), `fib_ext_127` (0.993), `fib_ext_162` (0.991), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.999), `head_shoulders_top_neckline` (0.994), `hull_ma` (0.999), `ichi_kijun` (1.0), `ichi_senkou_a` (0.995), `ichi_senkou_b` (0.99), `ichi_tenkan` (1.0), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (0.999), `monthly_close` (0.998), `monthly_sma_12` (0.982), `monthly_sma_6` (0.994), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.998), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.999), `s2` (0.999), `s3` (0.998), `supertrend_value` (0.998), `swing_high` (0.995), `swing_low` (0.996), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.997), `vp_value_area_high` (0.997), `vp_value_area_low` (0.997), `weekly_close` (0.998), `weekly_ema_10` (0.999), `weekly_ema_20` (0.996), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.999), `year_high` (0.967), `year_low` (0.968)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P2.1.1 | Tenkan / Kijun periods | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P2.1.2 | Tenkan / Kijun periods | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 2 |
| P2.2 | cross margin - Tenkan above Kijun by m o | 4 | subset-safe | no - derives offline | 1 | 3 | 0 |
| P3 | news_sentiment_5d >= 0 | 3 | subset-safe | no - derives offline | 1 | 2 | 0 |
| P4 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 0 |

```
FULL FACTORIAL     3 x 3 x 4 x 3 x 1 = 108
offline gradings   11 level-combinations x 24 exits = 264 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  96 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 11 + 96 = 108 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 645 census axes join it only when REGISTERED at the T3 band review.
