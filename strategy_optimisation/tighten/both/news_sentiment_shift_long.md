# Table A - news_sentiment_shift_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit f55b7c1e7 at 2026-09-19 23:26:39 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** news_sentiment | **status:** NOT-STARTED | **R5 fires:** 357 | **surviving fires (T1):** 357 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  price_above_ema_200  <- backtest/signals/index_rebalance.py +1
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P1.1-P1.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P2  news_article_count >= 2   [EXISTING-THRESHOLD]
P3  news_sentiment_shift > 0.3   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_news_sentiment_shift_long (docstring and return dropped):

```python
fires = s.get('news_sentiment_shift', 0.0) > 0.3 and s.get('news_article_count', 0) >= 2 and s.get('price_above_ema_200', False)
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
| P1 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/index_rebalance.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | BRACKET production; 150/250 are the adjacent canon spans | 200 | 150, 200, 250 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | STRATEGY | news_article_count `>= 2` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `>= 2` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P3 | STRATEGY | news_sentiment_shift `> 0.3` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `> 0.3` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| news_article_count | backtest/signals/news_sentiment.py +1 | `>= 2` | 100.0% | TIGHTER = RAISE the floor: 3 -> 290 (81%); 4 -> 227 (64%); 6 -> 154 (43%); 10 -> 82 (23%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | `> 0.3` | 100.0% | TIGHTER = RAISE the floor: 0.3597 -> 285 (80%); 0.4444 -> 217 (61%); 0.5238 -> 144 (40%); 0.7488 -> 72 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 16.428, 20.642, 24.776, 29.146 | 16.428: 285 (80%); 20.642: 214 (60%); 24.776: 143 (40%); 29.146: 72 (20%) | 16.428: 72 (20%); 20.642: 143 (40%); 24.776: 214 (60%); 29.146: 285 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 16.902, 20.6, 24.302, 28.97 | 16.902: 285 (80%); 20.6: 215 (60%); 24.302: 143 (40%); 28.97: 72 (20%) | 16.902: 72 (20%); 20.6: 144 (40%); 24.302: 214 (60%); 28.97: 285 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 18.432, 22.068, 26.582, 32.102 | 18.432: 285 (80%); 22.068: 214 (60%); 26.582: 143 (40%); 32.102: 72 (20%) | 18.432: 72 (20%); 22.068: 143 (40%); 26.582: 214 (60%); 32.102: 285 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -4.6665, -0.9047, 1.3025, 3.9149 | -4.6665: 285 (80%); -0.9047: 214 (60%); 1.3025: 143 (40%); 3.9149: 72 (20%) | -4.6665: 72 (20%); -0.9047: 143 (40%); 1.3025: 214 (60%); 3.9149: 285 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.2197, 2.0174, 3.4011, 6.0755 | 1.2197: 285 (80%); 2.0174: 214 (60%); 3.4011: 143 (40%); 6.0755: 72 (20%) | 1.2197: 72 (20%); 2.0174: 143 (40%); 3.4011: 214 (60%); 6.0755: 285 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.2197, 2.0174, 3.4011, 6.0755 | 1.2197: 285 (80%); 2.0174: 214 (60%); 3.4011: 143 (40%); 6.0755: 72 (20%) | 1.2197: 72 (20%); 2.0174: 143 (40%); 3.4011: 214 (60%); 6.0755: 285 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.0296, 2.5544, 3.0508, 4.0326 | 2.0296: 285 (80%); 2.5544: 214 (60%); 3.0508: 143 (40%); 4.0326: 72 (20%) | 2.0296: 72 (20%); 2.5544: 143 (40%); 3.0508: 214 (60%); 4.0326: 285 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0566, 0.0786, 0.1118, 0.1585 | 0.0566: 288 (81%); 0.0786: 214 (60%); 0.1118: 143 (40%); 0.1585: 72 (20%) | 0.0566: 72 (20%); 0.0786: 143 (40%); 0.1118: 214 (60%); 0.1585: 285 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.261, 0.4949, 0.7381, 0.902 | 0.261: 285 (80%); 0.4949: 214 (60%); 0.7381: 143 (40%); 0.902: 72 (20%) | 0.261: 72 (20%); 0.4949: 143 (40%); 0.7381: 214 (60%); 0.902: 285 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.065, 0.093, 0.1182, 0.15 | 0.065: 286 (80%); 0.093: 214 (60%); 0.1182: 143 (40%); 0.15: 72 (20%) | 0.065: 72 (20%); 0.093: 143 (40%); 0.1182: 214 (60%); 0.15: 285 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.1446, 0.4616, 0.7572, 1.0449 | 0.1446: 285 (80%); 0.4616: 214 (60%); 0.7572: 143 (40%); 1.0449: 72 (20%) | 0.1446: 72 (20%); 0.4616: 143 (40%); 0.7572: 214 (60%); 1.0449: 285 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0867, 0.1239, 0.1576, 0.2 | 0.0867: 286 (80%); 0.1239: 214 (60%); 0.1576: 143 (40%); 0.2: 72 (20%) | 0.0867: 73 (20%); 0.1239: 143 (40%); 0.1576: 214 (60%); 0.2: 285 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.2334, 0.4712, 0.6929, 0.9087 | 0.2334: 285 (80%); 0.4712: 214 (60%); 0.6929: 143 (40%); 0.9087: 72 (20%) | 0.2334: 72 (20%); 0.4712: 143 (40%); 0.6929: 214 (60%); 0.9087: 285 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.049, -0.021, -0.0005, 0.0297 | -0.049: 286 (80%); -0.021: 216 (61%); -0.0005: 143 (40%); 0.0297: 73 (20%) | -0.049: 74 (21%); -0.021: 144 (40%); -0.0005: 215 (60%); 0.0297: 286 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1462, 0.18, 0.2287, 0.27 | 0.1462: 286 (80%); 0.18: 214 (60%); 0.2287: 143 (40%); 0.27: 71 (20%) | 0.1462: 71 (20%); 0.18: 143 (40%); 0.2287: 214 (60%); 0.27: 286 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 357 (100%) | 0: 342 (96%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0767, 0.0042, 0.0732, 0.1632 | -0.0767: 285 (80%); 0.0042: 214 (60%); 0.0732: 143 (40%); 0.1632: 72 (20%) | -0.0767: 72 (20%); 0.0042: 143 (40%); 0.0732: 215 (60%); 0.1632: 285 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 357 (100%); 1: 149 (42%) | 0: 208 (58%); 1: 295 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2496, -0.2184, -0.163, -0.1299 | -0.2496: 285 (80%); -0.2184: 214 (60%); -0.163: 143 (40%); -0.1299: 78 (22%) | -0.2496: 72 (20%); -0.2184: 143 (40%); -0.163: 214 (60%); -0.1299: 286 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3628, 0.609, 0.6923, 0.7756 | 0.3628: 285 (80%); 0.609: 219 (61%); 0.6923: 145 (41%); 0.7756: 74 (21%) | 0.3628: 72 (20%); 0.609: 145 (41%); 0.6923: 220 (62%); 0.7756: 286 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.3205, 0.5192, 0.8256 | 0.2628: 286 (80%); 0.3205: 216 (61%); 0.5192: 149 (42%); 0.8256: 72 (20%) | 0.2628: 86 (24%); 0.3205: 144 (40%); 0.5192: 217 (61%); 0.8256: 285 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0908, -0.0058, 0.0985, 0.2734 | -0.0908: 286 (80%); -0.0058: 214 (60%); 0.0985: 143 (40%); 0.2734: 73 (20%) | -0.0908: 74 (21%); -0.0058: 143 (40%); 0.0985: 215 (60%); 0.2734: 289 (81%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2692, 0.477, 0.6603, 0.9025 | 0.2692: 286 (80%); 0.477: 214 (60%); 0.6603: 144 (40%); 0.9025: 72 (20%) | 0.2692: 73 (20%); 0.477: 143 (40%); 0.6603: 217 (61%); 0.9025: 285 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1474, 0.3462, 0.4808, 0.6731 | 0.1474: 288 (81%); 0.3462: 216 (61%); 0.4808: 152 (43%); 0.6731: 73 (20%) | 0.1474: 76 (21%); 0.3462: 145 (41%); 0.4808: 223 (62%); 0.6731: 289 (81%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.521, -0.4451, -0.221, -0.0395 | -0.521: 287 (80%); -0.4451: 215 (60%); -0.221: 143 (40%); -0.0395: 72 (20%) | -0.521: 76 (21%); -0.4451: 145 (41%); -0.221: 214 (60%); -0.0395: 285 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3013, 0.4615, 0.5782, 0.8462 | 0.3013: 287 (80%); 0.4615: 218 (61%); 0.5782: 143 (40%); 0.8462: 73 (20%) | 0.3013: 73 (20%); 0.4615: 150 (42%); 0.5782: 214 (60%); 0.8462: 293 (82%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1218, 0.3231, 0.5064, 0.8013 | 0.1218: 293 (82%); 0.3231: 214 (60%); 0.5064: 144 (40%); 0.8013: 74 (21%) | 0.1218: 73 (20%); 0.3231: 143 (40%); 0.5064: 218 (61%); 0.8013: 286 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0655, -0.0597, -0.0424, 0 | -0.0655: 287 (80%); -0.0597: 216 (61%); -0.0424: 144 (40%); 0: 89 (25%) | -0.0655: 72 (20%); -0.0597: 144 (40%); -0.0424: 216 (61%); 0: 342 (96%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4551, 0.7128, 0.8718, 0.9936 | 0.4551: 288 (81%); 0.7128: 214 (60%); 0.8718: 144 (40%); 0.9936: 81 (23%) | 0.4551: 73 (20%); 0.7128: 143 (40%); 0.8718: 217 (61%); 0.9936: 299 (84%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.109, 0.2115, 0.5807, 0.9103 | 0.109: 290 (81%); 0.2115: 220 (62%); 0.5807: 143 (40%); 0.9103: 73 (20%) | 0.109: 75 (21%); 0.2115: 146 (41%); 0.5807: 214 (60%); 0.9103: 287 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0129, 0.0285, 0.0544, 0.179 | -0.0129: 285 (80%); 0.0285: 214 (60%); 0.0544: 144 (40%); 0.179: 75 (21%) | -0.0129: 72 (20%); 0.0285: 143 (40%); 0.0544: 217 (61%); 0.179: 286 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4966, 0.7775, 0.9103, 0.9744 | 0.4966: 288 (81%); 0.7775: 214 (60%); 0.9103: 145 (41%); 0.9744: 77 (22%) | 0.4966: 73 (20%); 0.7775: 143 (40%); 0.9103: 216 (61%); 0.9744: 295 (83%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0954, 0.2203, 0.6026, 0.7971 | 0.0954: 285 (80%); 0.2203: 217 (61%); 0.6026: 146 (41%); 0.7971: 75 (21%) | 0.0954: 72 (20%); 0.2203: 144 (40%); 0.6026: 221 (62%); 0.7971: 286 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0783, -0.0139, 0.0791, 0.1603 | -0.0783: 285 (80%); -0.0139: 214 (60%); 0.0791: 144 (40%); 0.1603: 74 (21%) | -0.0783: 72 (20%); -0.0139: 143 (40%); 0.0791: 219 (61%); 0.1603: 286 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1858, -0.0331, 0.023, 0.0752 | -0.1858: 285 (80%); -0.0331: 214 (60%); 0.023: 151 (42%); 0.0752: 72 (20%) | -0.1858: 72 (20%); -0.0331: 143 (40%); 0.023: 219 (61%); 0.0752: 285 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.1923, 0.5192, 0.6961, 0.8141 | 0.1923: 291 (82%); 0.5192: 217 (61%); 0.6961: 143 (40%); 0.8141: 73 (20%) | 0.1923: 74 (21%); 0.5192: 146 (41%); 0.6961: 214 (60%); 0.8141: 286 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1487, 0.3808, 0.5949, 0.8846 | 0.1487: 285 (80%); 0.3808: 214 (60%); 0.5949: 143 (40%); 0.8846: 77 (22%) | 0.1487: 72 (20%); 0.3808: 143 (40%); 0.5949: 214 (60%); 0.8846: 286 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.055, 0.1273, 0.2527, 0.629 | 0.055: 286 (80%); 0.1273: 214 (60%); 0.2527: 143 (40%); 0.629: 72 (20%) | 0.055: 73 (20%); 0.1273: 143 (40%); 0.2527: 214 (60%); 0.629: 285 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.9% | 23, 61.8, 85, 143.2 | 23: 283 (79%); 61.8: 212 (59%); 85: 142 (40%); 143.2: 71 (20%) | 23: 72 (20%); 61.8: 141 (39%); 85: 214 (60%); 143.2: 282 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.7% | 1.7082, 2.3337, 3.0318, 4.1732 | 1.7082: 285 (80%); 2.3337: 214 (60%); 3.0318: 143 (40%); 4.1732: 72 (20%) | 1.7082: 72 (20%); 2.3337: 143 (40%); 3.0318: 214 (60%); 4.1732: 285 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 12, 21, 28, 36 | 12: 291 (82%); 21: 215 (60%); 28: 152 (43%); 36: 77 (22%) | 12: 78 (22%); 21: 157 (44%); 28: 223 (62%); 36: 294 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3 | 1: 292 (82%); 2: 221 (62%); 3: 148 (41%) | 1: 136 (38%); 2: 209 (59%); 3: 286 (80%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0149, -0.0049, 0.0115, 0.0209 | -0.0149: 286 (80%); -0.0049: 218 (61%); 0.0115: 143 (40%); 0.0209: 72 (20%) | -0.0149: 73 (20%); -0.0049: 143 (40%); 0.0115: 214 (60%); 0.0209: 286 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.3659, 25.0475, 26.1613, 27.088 | 24.3659: 285 (80%); 25.0475: 214 (60%); 26.1613: 143 (40%); 27.088: 72 (20%) | 24.3659: 72 (20%); 25.0475: 143 (40%); 26.1613: 214 (60%); 27.088: 285 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.6812, -0.114, 0.352, 0.8718 | -0.6812: 285 (80%); -0.114: 214 (60%); 0.352: 143 (40%); 0.8718: 72 (20%) | -0.6812: 72 (20%); -0.114: 143 (40%); 0.352: 214 (60%); 0.8718: 285 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.8718, -0.352, 0.114, 0.6812 | -0.8718: 285 (80%); -0.352: 214 (60%); 0.114: 143 (40%); 0.6812: 72 (20%) | -0.8718: 72 (20%); -0.352: 143 (40%); 0.114: 214 (60%); 0.6812: 285 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0479, -0.0093, 0.0261, 0.061 | -0.0479: 285 (80%); -0.0093: 214 (60%); 0.0261: 143 (40%); 0.061: 72 (20%) | -0.0479: 72 (20%); -0.0093: 143 (40%); 0.0261: 214 (60%); 0.061: 285 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.7931, 8.365, 8.5985, 8.8998 | 7.7931: 285 (80%); 8.365: 214 (60%); 8.5985: 144 (40%); 8.8998: 72 (20%) | 7.7931: 72 (20%); 8.365: 143 (40%); 8.5985: 213 (60%); 8.8998: 285 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.7% | 0, 1 | 0: 356 (100%); 1: 111 (31%) | 0: 245 (69%); 1: 319 (89%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.7% | -1, 0 | -1: 332 (93%); 0: 281 (79%) | -1: 75 (21%); 0: 294 (82%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.7% | 0, 1 | 0: 356 (100%); 1: 125 (35%) | 0: 231 (65%); 1: 307 (86%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 4, 7, 192.8 | 2: 294 (82%); 4: 238 (67%); 7: 154 (43%); 192.8: 72 (20%) | 2: 95 (27%); 4: 146 (41%); 7: 216 (61%); 192.8: 285 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 2, 7, 118.6 | 1: 293 (82%); 2: 247 (69%); 7: 149 (42%); 118.6: 72 (20%) | 1: 110 (31%); 2: 152 (43%); 7: 215 (60%); 118.6: 285 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.6905, -0.1622, 0.1431, 0.5999 | -0.6905: 285 (80%); -0.1622: 214 (60%); 0.1431: 143 (40%); 0.5999: 72 (20%) | -0.6905: 72 (20%); -0.1622: 143 (40%); 0.1431: 215 (60%); 0.5999: 285 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -1.5293, -0.097, 0.4819, 1.4636 | -1.5293: 285 (80%); -0.097: 214 (60%); 0.4819: 143 (40%); 1.4636: 72 (20%) | -1.5293: 72 (20%); -0.097: 143 (40%); 0.4819: 214 (60%); 1.4636: 285 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.2794, -0.0193, 0.5779, 1.4805 | -1.2794: 285 (80%); -0.0193: 214 (60%); 0.5779: 143 (40%); 1.4805: 72 (20%) | -1.2794: 72 (20%); -0.0193: 143 (40%); 0.5779: 214 (60%); 1.4805: 285 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.4136, -0.1012, 0.1504, 0.6147 | -0.4136: 285 (80%); -0.1012: 214 (60%); 0.1504: 143 (40%); 0.6147: 72 (20%) | -0.4136: 72 (20%); -0.1012: 143 (40%); 0.1504: 214 (60%); 0.6147: 285 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -1.7274, -0.3154, 0.5957, 1.7684 | -1.7274: 285 (80%); -0.3154: 214 (60%); 0.5957: 143 (40%); 1.7684: 72 (20%) | -1.7274: 72 (20%); -0.3154: 143 (40%); 0.5957: 214 (60%); 1.7684: 285 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -1.6999, -0.3113, 0.4483, 1.6155 | -1.6999: 285 (80%); -0.3113: 214 (60%); 0.4483: 143 (40%); 1.6155: 72 (20%) | -1.6999: 72 (20%); -0.3113: 143 (40%); 0.4483: 214 (60%); 1.6155: 285 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 36.774, 46.764, 55.178, 67.718 | 36.774: 285 (80%); 46.764: 214 (60%); 55.178: 143 (40%); 67.718: 72 (20%) | 36.774: 72 (20%); 46.764: 143 (40%); 55.178: 214 (60%); 67.718: 285 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 100.0% | 0.0047, 0.0131, 0.0238, 0.04 | 0.0047: 285 (80%); 0.0131: 214 (60%); 0.0238: 143 (40%); 0.04: 71 (20%) | 0.0047: 72 (20%); 0.0131: 143 (40%); 0.0238: 214 (60%); 0.04: 286 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0994 | 0: 357 (100%); 0.0994: 72 (20%) | 0: 262 (73%); 0.0994: 285 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0.4464, 0.5661, 0.6667, 1 | 0.4464: 285 (80%); 0.5661: 214 (60%); 0.6667: 165 (46%); 1: 74 (21%) | 0.4464: 72 (20%); 0.5661: 143 (40%); 0.6667: 227 (64%); 1: 357 (100%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 2, 3, 4, 7 | 2: 306 (86%); 3: 233 (65%); 4: 178 (50%); 7: 81 (23%) | 2: 124 (35%); 3: 179 (50%); 4: 221 (62%); 7: 294 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 3, 4, 6, 10 | 3: 290 (81%); 4: 227 (64%); 6: 154 (43%); 10: 82 (23%) | 3: 130 (36%); 4: 163 (46%); 6: 227 (64%); 10: 287 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 1, 3, 5, 8 | 1: 357 (100%); 3: 236 (66%); 5: 146 (41%); 8: 73 (20%) | 1: 74 (21%); 3: 170 (48%); 5: 239 (67%); 8: 294 (82%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.213, 0.2984, 0.3965, 0.5137 | 0.213: 285 (80%); 0.2984: 214 (60%); 0.3965: 143 (40%); 0.5137: 72 (20%) | 0.213: 72 (20%); 0.2984: 143 (40%); 0.3965: 214 (60%); 0.5137: 285 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0.1482, 0.4783, 0.6667, 1 | 0.1482: 285 (80%); 0.4783: 215 (60%); 0.6667: 149 (42%); 1: 85 (24%) | 0.1482: 72 (20%); 0.4783: 145 (41%); 0.6667: 217 (61%); 1: 357 (100%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0.3575, 0.5, 0.6272, 0.8523 | 0.3575: 285 (80%); 0.5: 229 (64%); 0.6272: 143 (40%); 0.8523: 72 (20%) | 0.3575: 72 (20%); 0.5: 167 (47%); 0.6272: 214 (60%); 0.8523: 285 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0.3575, 0.5, 0.6272, 0.8523 | 0.3575: 285 (80%); 0.5: 229 (64%); 0.6272: 143 (40%); 0.8523: 72 (20%) | 0.3575: 72 (20%); 0.5: 167 (47%); 0.6272: 214 (60%); 0.8523: 285 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.5941, -0.1092, 0.8047, 2.0954 | -0.5941: 285 (80%); -0.1092: 214 (60%); 0.8047: 143 (40%); 2.0954: 72 (20%) | -0.5941: 72 (20%); -0.1092: 143 (40%); 0.8047: 214 (60%); 2.0954: 285 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 5, 8, 13 | 2: 312 (87%); 5: 216 (61%); 8: 149 (42%); 13: 78 (22%) | 2: 82 (23%); 5: 169 (47%); 8: 228 (64%); 13: 299 (84%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.045, -0.0042, 0.022, 0.0723 | -0.045: 285 (80%); -0.0042: 214 (60%); 0.022: 143 (40%); 0.0723: 72 (20%) | -0.045: 72 (20%); -0.0042: 143 (40%); 0.022: 214 (60%); 0.0723: 285 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0632, -0.0059, 0.0438, 0.0922 | -0.0632: 285 (80%); -0.0059: 214 (60%); 0.0438: 143 (40%); 0.0922: 72 (20%) | -0.0632: 72 (20%); -0.0059: 143 (40%); 0.0438: 214 (60%); 0.0922: 285 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.031, -0.0026, 0.0205, 0.0548 | -0.031: 285 (80%); -0.0026: 214 (60%); 0.0205: 143 (40%); 0.0548: 71 (20%) | -0.031: 72 (20%); -0.0026: 143 (40%); 0.0205: 214 (60%); 0.0548: 286 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -3.0146, 4.4746, 11.8802, 27.4226 | -3.0146: 285 (80%); 4.4746: 214 (60%); 11.8802: 143 (40%); 27.4226: 72 (20%) | -3.0146: 72 (20%); 4.4746: 143 (40%); 11.8802: 214 (60%); 27.4226: 285 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0406, 0.0561, 0.0786, 0.1063 | 0.0406: 285 (80%); 0.0561: 214 (60%); 0.0786: 144 (40%); 0.1063: 72 (20%) | 0.0406: 72 (20%); 0.0561: 143 (40%); 0.0786: 215 (60%); 0.1063: 285 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.5007, 0.6697, 0.799, 0.9017 | 0.5007: 285 (80%); 0.6697: 214 (60%); 0.799: 144 (40%); 0.9017: 72 (20%) | 0.5007: 72 (20%); 0.6697: 143 (40%); 0.799: 215 (60%); 0.9017: 285 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.4045, -0.1578, 0.7819, 1.8729 | -1.4045: 285 (80%); -0.1578: 214 (60%); 0.7819: 143 (40%); 1.8729: 72 (20%) | -1.4045: 72 (20%); -0.1578: 143 (40%); 0.7819: 214 (60%); 1.8729: 285 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.7229, -0.2503, 0.1929, 0.661 | -0.7229: 285 (80%); -0.2503: 214 (60%); 0.1929: 143 (40%); 0.661: 72 (20%) | -0.7229: 72 (20%); -0.2503: 143 (40%); 0.1929: 214 (60%); 0.661: 285 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.4535, -0.0205, 0.7809, 1.7462 | -1.4535: 285 (80%); -0.0205: 214 (60%); 0.7809: 143 (40%); 1.7462: 72 (20%) | -1.4535: 72 (20%); -0.0205: 143 (40%); 0.7809: 214 (60%); 1.7462: 285 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -4.9606, -0.9296, 3.061, 7.3674 | -4.9606: 285 (80%); -0.9296: 214 (60%); 3.061: 143 (40%); 7.3674: 72 (20%) | -4.9606: 72 (20%); -0.9296: 143 (40%); 3.061: 214 (60%); 7.3674: 285 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 43.368, 50.368, 57.086, 63.31 | 43.368: 285 (80%); 50.368: 214 (60%); 57.086: 143 (40%); 63.31: 73 (20%) | 43.368: 72 (20%); 50.368: 143 (40%); 57.086: 214 (60%); 63.31: 286 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 35.062, 59.224, 81.364, 92.26 | 35.062: 285 (80%); 59.224: 214 (60%); 81.364: 143 (40%); 92.26: 72 (20%) | 35.062: 72 (20%); 59.224: 143 (40%); 81.364: 214 (60%); 92.26: 285 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 45.962, 50.814, 55.622, 59.702 | 45.962: 285 (80%); 50.814: 214 (60%); 55.622: 143 (40%); 59.702: 72 (20%) | 45.962: 72 (20%); 50.814: 143 (40%); 55.622: 214 (60%); 59.702: 285 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 40.086, 50.684, 59.396, 68.616 | 40.086: 285 (80%); 50.684: 214 (60%); 59.396: 143 (40%); 68.616: 72 (20%) | 40.086: 72 (20%); 50.684: 143 (40%); 59.396: 214 (60%); 68.616: 285 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0323, 0.0462, 0.0626, 0.0931 | 0.0323: 286 (80%); 0.0462: 214 (60%); 0.0626: 143 (40%); 0.0931: 74 (21%) | 0.0323: 72 (20%); 0.0462: 143 (40%); 0.0626: 214 (60%); 0.0931: 286 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0869, -0.0611, -0.045, -0.034 | -0.0869: 285 (80%); -0.0611: 215 (60%); -0.045: 145 (41%); -0.034: 72 (20%) | -0.0869: 72 (20%); -0.0611: 144 (40%); -0.045: 215 (60%); -0.034: 286 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 357 (100%); 2: 81 (23%) | 0: 234 (66%); 2: 298 (83%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.7% | 24, 36, 48, 66 | 24: 288 (81%); 36: 214 (60%); 48: 144 (40%); 66: 72 (20%) | 24: 74 (21%); 36: 144 (40%); 48: 215 (60%); 66: 286 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.3% | 0.0121, 0.0176, 0.0262, 0.0399 | 0.0121: 281 (79%); 0.0176: 210 (59%); 0.0262: 143 (40%); 0.0399: 70 (20%) | 0.0121: 70 (20%); 0.0176: 141 (39%); 0.0262: 209 (59%); 0.0399: 281 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.347, 0.5225, 0.6994, 0.8799 | 0.347: 286 (80%); 0.5225: 214 (60%); 0.6994: 143 (40%); 0.8799: 72 (20%) | 0.347: 72 (20%); 0.5225: 143 (40%); 0.6994: 214 (60%); 0.8799: 285 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 41.38, 58.3, 74.52, 106.56 | 41.38: 285 (80%); 58.3: 215 (60%); 74.52: 143 (40%); 106.56: 72 (20%) | 41.38: 72 (20%); 58.3: 144 (40%); 74.52: 214 (60%); 106.56: 285 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -3.323, -0.563, 1.635, 5.3347 | -3.323: 285 (80%); -0.563: 214 (60%); 1.635: 143 (40%); 5.3347: 72 (20%) | -3.323: 72 (20%); -0.563: 143 (40%); 1.635: 214 (60%); 5.3347: 285 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 21.584, 36.636, 62.708, 79.776 | 21.584: 285 (80%); 36.636: 214 (60%); 62.708: 143 (40%); 79.776: 72 (20%) | 21.584: 72 (20%); 36.636: 143 (40%); 62.708: 214 (60%); 79.776: 285 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 21.402, 38.844, 64.666, 83.788 | 21.402: 285 (80%); 38.844: 214 (60%); 64.666: 143 (40%); 83.788: 72 (20%) | 21.402: 72 (20%); 38.844: 143 (40%); 64.666: 214 (60%); 83.788: 285 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 9.518, 32.21, 63.784, 90.022 | 9.518: 285 (80%); 32.21: 214 (60%); 63.784: 143 (40%); 90.022: 72 (20%) | 9.518: 72 (20%); 32.21: 143 (40%); 63.784: 214 (60%); 90.022: 285 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 7.146, 38.45, 74.666, 100 | 7.146: 285 (80%); 38.45: 214 (60%); 74.666: 143 (40%); 100: 84 (24%) | 7.146: 72 (20%); 38.45: 143 (40%); 74.666: 214 (60%); 100: 357 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 8, 13, 17.8 | 4: 286 (80%); 8: 217 (61%); 13: 145 (41%); 17.8: 72 (20%) | 4: 88 (25%); 8: 148 (41%); 13: 225 (63%); 17.8: 285 (80%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 4.2, 9, 13, 18 | 4.2: 285 (80%); 9: 221 (62%); 13: 157 (44%); 18: 88 (25%) | 4.2: 72 (20%); 9: 154 (43%); 13: 215 (60%); 18: 291 (82%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 44.846, 51.36, 55.908, 62.366 | 44.846: 285 (80%); 51.36: 214 (60%); 55.908: 143 (40%); 62.366: 72 (20%) | 44.846: 72 (20%); 51.36: 143 (40%); 55.908: 214 (60%); 62.366: 285 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1032, 0.254, 0.6071, 0.8286 | 0.1032: 288 (81%); 0.254: 216 (61%); 0.6071: 144 (40%); 0.8286: 72 (20%) | 0.1032: 76 (21%); 0.254: 144 (40%); 0.6071: 215 (60%); 0.8286: 285 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.008, 17.062, 20.816, 25.29 | 14.008: 285 (80%); 17.062: 214 (60%); 20.816: 143 (40%); 25.29: 72 (20%) | 14.008: 72 (20%); 17.062: 143 (40%); 20.816: 214 (60%); 25.29: 285 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 14.008, 17.062, 20.816, 25.29 | 14.008: 285 (80%); 17.062: 214 (60%); 20.816: 143 (40%); 25.29: 72 (20%) | 14.008: 72 (20%); 17.062: 143 (40%); 20.816: 214 (60%); 25.29: 285 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8576, 0.8862, 0.9188, 0.9554 | 0.8576: 286 (80%); 0.8862: 216 (61%); 0.9188: 143 (40%); 0.9554: 74 (21%) | 0.8576: 72 (20%); 0.8862: 145 (41%); 0.9188: 214 (60%); 0.9554: 286 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.7, 0.84, 1, 1.318 | 0.7: 286 (80%); 0.84: 215 (60%); 1: 144 (40%); 1.318: 72 (20%) | 0.7: 73 (20%); 0.84: 147 (41%); 1: 215 (60%); 1.318: 285 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0162, 0.0425, 0.0725, 0.1168 | 0.0162: 285 (80%); 0.0425: 214 (60%); 0.0725: 143 (40%); 0.1168: 72 (20%) | 0.0162: 72 (20%); 0.0425: 143 (40%); 0.0725: 214 (60%); 0.1168: 286 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 41.7534, 67.7563, 103.8755, 164.2433 | 41.7534: 285 (80%); 67.7563: 214 (60%); 103.8755: 143 (40%); 164.2433: 72 (20%) | 41.7534: 72 (20%); 67.7563: 143 (40%); 103.8755: 214 (60%); 164.2433: 285 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 39.4062, 65.0149, 97.3495, 158.7682 | 39.4062: 285 (80%); 65.0149: 214 (60%); 97.3495: 143 (40%); 158.7682: 72 (20%) | 39.4062: 72 (20%); 65.0149: 143 (40%); 97.3495: 214 (60%); 158.7682: 285 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 37.4117, 61.6957, 91.975, 152.6653 | 37.4117: 285 (80%); 61.6957: 214 (60%); 91.975: 143 (40%); 152.6653: 72 (20%) | 37.4117: 72 (20%); 61.6957: 143 (40%); 91.975: 214 (60%); 152.6653: 285 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 43.6251, 69.1023, 107.6065, 171.6066 | 43.6251: 285 (80%); 69.1023: 214 (60%); 107.6065: 143 (40%); 171.6066: 72 (20%) | 43.6251: 72 (20%); 69.1023: 143 (40%); 107.6065: 214 (60%); 171.6066: 285 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 357 (100%) | 0: 300 (84%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 357 (100%) | 0: 334 (94%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.058, -0.0089, 0.0372, 0.0826 | -0.058: 285 (80%); -0.0089: 214 (60%); 0.0372: 143 (40%); 0.0826: 72 (20%) | -0.058: 72 (20%); -0.0089: 143 (40%); 0.0372: 214 (60%); 0.0826: 285 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -74.368, -53.2, -26.91, -8.848 | -74.368: 285 (80%); -53.2: 214 (60%); -26.91: 143 (40%); -8.848: 72 (20%) | -74.368: 72 (20%); -53.2: 143 (40%); -26.91: 214 (60%); -8.848: 285 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 100.0% | 0.5912, 0.8472, 1.0387, 1.4037 | 0.5912: 285 (80%); 0.8472: 214 (60%); 1.0387: 143 (40%); 1.4037: 72 (20%) | 0.5912: 72 (20%); 0.8472: 143 (40%); 1.0387: 214 (60%); 1.4037: 285 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 100.0% | 3, 5, 7, 9 | 3: 294 (82%); 5: 229 (64%); 7: 157 (44%); 9: 95 (27%) | 3: 95 (27%); 5: 169 (47%); 7: 223 (62%); 9: 298 (83%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 100.0% | 0.199, 0.2382, 0.2976, 0.384 | 0.199: 285 (80%); 0.2382: 214 (60%); 0.2976: 143 (40%); 0.384: 72 (20%) | 0.199: 72 (20%); 0.2382: 143 (40%); 0.2976: 214 (60%); 0.384: 285 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 100.0% | 3, 6, 8, 9 | 3: 312 (87%); 6: 218 (61%); 8: 153 (43%); 9: 111 (31%) | 3: 73 (20%); 6: 164 (46%); 8: 246 (69%); 9: 288 (81%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 100.0% | 0.0248, 0.0335, 0.044, 0.0678 | 0.0248: 287 (80%); 0.0335: 215 (60%); 0.044: 144 (40%); 0.0678: 72 (20%) | 0.0248: 73 (20%); 0.0335: 143 (40%); 0.044: 215 (60%); 0.0678: 285 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 100.0% | 3, 6, 7, 9 | 3: 310 (87%); 6: 216 (61%); 7: 182 (51%); 9: 104 (29%) | 3: 81 (23%); 6: 175 (49%); 7: 217 (61%); 9: 286 (80%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 100.0% | -0.0753, 0.039, 0.1641, 0.3712 | -0.0753: 285 (80%); 0.039: 214 (60%); 0.1641: 143 (40%); 0.3712: 72 (20%) | -0.0753: 72 (20%); 0.039: 143 (40%); 0.1641: 214 (60%); 0.3712: 285 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 100.0% | 4, 6, 8, 10 | 4: 304 (85%); 6: 234 (66%); 8: 173 (48%); 10: 75 (21%) | 4: 88 (25%); 6: 155 (43%); 8: 236 (66%); 10: 357 (100%) | OFFLINE |
| year_low | backtest/signals/technical.py | 100.0% | 32.202, 54.1644, 78.842, 137.502 | 32.202: 285 (80%); 54.1644: 214 (60%); 78.842: 143 (40%); 137.502: 72 (20%) | 32.202: 72 (20%); 54.1644: 143 (40%); 78.842: 214 (60%); 137.502: 285 (80%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 4.9% |
| 8k_item_5_02_filed_within_7d | 2.6% |
| above_avwap_20high | 44.3% |
| above_avwap_20low | 87.1% |
| above_avwap_252low | 94.1% |
| above_avwap_50low | 78.4% |
| above_cam_r3 | 54.1% |
| above_cam_r4 | 33.6% |
| above_cpr | 69.7% |
| above_pivot | 74.2% |
| above_prev_high | 41.2% |
| above_prev_high_clearance_atr_05 | 18.5% |
| above_prev_low | 91.6% |
| above_r1 | 36.4% |
| above_r2 | 18.8% |
| above_vwap | 74.8% |
| above_wood_p | 68.9% |
| ad_rising | 66.1% |
| adx_cross_up | 2.5% |
| adx_cross_up_20 | 2.2% |
| adx_di_bear | 43.4% |
| adx_di_bull | 56.6% |
| adx_strong | 2.8% |
| adx_trending | 39.2% |
| ao_cross_dn | 2.8% |
| ao_cross_up | 3.1% |
| ao_positive | 51.3% |
| ao_twin_peaks_bull | 4.8% |
| at_key_fib | 15.7% |
| at_key_fib_wide | 39.5% |
| avwap_20high_loss_recent_3d | 13.8% |
| avwap_20high_reclaim_recent_3d | 28.3% |
| avwap_20low_loss_recent_3d | 8.0% |
| avwap_20low_reclaim_recent_3d | 26.2% |
| avwap_252low_loss_recent_3d | 1.5% |
| avwap_252low_reclaim_recent_3d | 16.7% |
| avwap_50low_loss_recent_3d | 8.6% |
| avwap_50low_reclaim_recent_3d | 15.5% |
| bb_10_20_above_mid | 58.8% |
| bb_10_20_expanding | 51.5% |
| bb_10_20_pctb_gt_75 | 38.4% |
| bb_10_20_pctb_gt_8 | 32.5% |
| bb_10_20_pctb_gt_85 | 27.7% |
| bb_10_20_pctb_gt_9 | 20.2% |
| bb_10_20_pctb_gt_95 | 13.7% |
| bb_10_20_pctb_lt_05 | 1.7% |
| bb_10_20_pctb_lt_1 | 3.9% |
| bb_10_20_pctb_lt_15 | 9.5% |
| bb_10_20_pctb_lt_2 | 14.0% |
| bb_10_20_pctb_lt_25 | 18.2% |
| bb_10_20_reclaim_from_lower_recent_3d | 10.6% |
| bb_10_20_reclaim_from_upper_recent_3d | 9.0% |
| bb_10_20_squeeze | 40.3% |
| bb_10_20_touch_lower | 2.0% |
| bb_10_20_touch_upper | 12.9% |
| bb_20_15_above_mid | 57.4% |
| bb_20_15_expanding | 53.2% |
| bb_20_15_pctb_gt_75 | 40.6% |
| bb_20_15_pctb_gt_8 | 37.0% |
| bb_20_15_pctb_gt_85 | 33.9% |
| bb_20_15_pctb_gt_9 | 30.0% |
| bb_20_15_pctb_gt_95 | 26.9% |
| bb_20_15_pctb_lt_05 | 14.8% |
| bb_20_15_pctb_lt_1 | 17.9% |
| bb_20_15_pctb_lt_15 | 20.2% |
| bb_20_15_pctb_lt_2 | 24.1% |
| bb_20_15_pctb_lt_25 | 26.3% |
| bb_20_15_reclaim_from_lower_recent_3d | 13.7% |
| bb_20_15_reclaim_from_upper_recent_3d | 6.2% |
| bb_20_15_squeeze | 31.7% |
| bb_20_15_touch_lower | 15.4% |
| bb_20_15_touch_upper | 28.0% |
| bb_20_20_above_mid | 57.4% |
| bb_20_20_expanding | 53.5% |
| bb_20_20_pctb_gt_75 | 34.5% |
| bb_20_20_pctb_gt_8 | 30.0% |
| bb_20_20_pctb_gt_85 | 25.8% |
| bb_20_20_pctb_gt_9 | 20.7% |
| bb_20_20_pctb_gt_95 | 16.2% |
| bb_20_20_pctb_lt_05 | 5.0% |
| bb_20_20_pctb_lt_1 | 10.1% |
| bb_20_20_pctb_lt_15 | 13.7% |
| bb_20_20_pctb_lt_2 | 17.9% |
| bb_20_20_pctb_lt_25 | 21.6% |
| bb_20_20_reclaim_from_lower_recent_3d | 10.4% |
| bb_20_20_reclaim_from_upper_recent_3d | 4.2% |
| bb_20_20_squeeze | 17.4% |
| bb_20_20_touch_lower | 5.0% |
| bb_20_20_touch_upper | 14.8% |
| bearish_pin_bar | 5.3% |
| below_avwap_20high | 55.7% |
| below_avwap_20low | 12.9% |
| below_avwap_252low | 5.9% |
| below_avwap_50low | 21.6% |
| below_cam_s3 | 9.8% |
| below_cam_s4 | 3.4% |
| below_cpr | 25.8% |
| below_ema_20 | 38.7% |
| below_ema_20_break_recent_5d | 15.1% |
| below_ema_21 | 39.2% |
| below_ema_21_break_recent_5d | 15.4% |
| below_ema_50 | 35.9% |
| below_ema_50_break_recent_5d | 15.7% |
| below_ema_9 | 38.7% |
| below_ema_9_break_recent_5d | 22.4% |
| below_prev_high | 58.8% |
| below_prev_low | 8.1% |
| below_prev_low_clearance_atr_05 | 1.7% |
| below_s1 | 4.8% |
| below_s2 | 1.4% |
| below_sma_20 | 42.6% |
| below_sma_200 | 13.7% |
| below_sma_21 | 42.9% |
| below_sma_50 | 38.4% |
| below_sma_9 | 41.7% |
| below_vwap | 25.2% |
| break_52w_high | 1.7% |
| break_52w_high_clearance_atr_05 | 0.6% |
| bullish_engulfing | 6.4% |
| bullish_pin_bar | 5.9% |
| capitulation_recent_3d | 1.1% |
| ceo_buy | 1.4% |
| cfo_buy | 0.8% |
| chandelier_long_bullish | 66.4% |
| chandelier_long_flip_dn | 1.7% |
| chandelier_short_bearish | 51.8% |
| chandelier_short_flip_up | 8.4% |
| close_in_bottom_40pct_of_range | 9.0% |
| close_in_top_40pct_of_range | 68.1% |
| cluster_buy | 0.6% |
| cmf_cross_dn | 2.2% |
| cmf_cross_up | 7.6% |
| cmf_negative | 39.8% |
| cmf_positive | 60.2% |
| concentrated_sell | 6.5% |
| cpr_narrow | 88.2% |
| cpr_narrow_tight | 24.6% |
| cup_handle_detected | 16.0% |
| cup_handle_neckline_break_retest_long | 7.6% |
| dc10_breakout_dn | 5.6% |
| dc10_breakout_dn_1pct | 9.0% |
| dc10_breakout_up | 22.4% |
| dc10_breakout_up_1pct | 30.5% |
| dc10_new_high | 27.5% |
| dc10_strong_breakout_dn | 0.6% |
| dc10_strong_breakout_up | 8.7% |
| dc20_breakout_dn | 3.6% |
| dc20_breakout_up | 16.5% |
| dc20_new_high | 18.8% |
| dc20_resistance_break_retest_strong | 17.6% |
| dc20_support_break_retest_strong | 12.3% |
| defensive_leadership | 55.5% |
| director_only_buy | 1.7% |
| doji | 5.9% |
| double_bottom_detected | 11.2% |
| double_top_detected | 13.2% |
| dpi_elevated | 53.2% |
| drying_volume_on_up_turn | 59.9% |
| ema_20_50_bearish | 38.1% |
| ema_20_50_bullish | 61.9% |
| ema_20_50_death_cross | 0.6% |
| ema_20_50_golden_cross | 2.0% |
| ema_50_200_bearish | 29.7% |
| ema_50_200_bullish | 70.3% |
| ema_50_200_golden_cross | 0.3% |
| ema_9_21_bearish | 46.2% |
| ema_9_21_bullish | 53.8% |
| ema_9_21_death_cross | 0.3% |
| ema_9_21_golden_cross | 3.9% |
| flag_bear_detected | 0.6% |
| flag_bull_break_retest_long | 0.6% |
| flag_bull_broke | 1.4% |
| flag_bull_detected | 1.1% |
| force_index_cross_dn | 1.1% |
| force_index_cross_up | 8.4% |
| force_index_positive | 58.0% |
| gap_dn_1_5pct | 10.6% |
| gap_dn_2pct | 7.8% |
| gap_up_1_5pct | 9.2% |
| gap_up_2pct | 7.6% |
| hammer | 4.5% |
| head_shoulders_bottom_detected | 4.5% |
| head_shoulders_top_detected | 5.3% |
| house_cluster_buy | 5.1% |
| house_cluster_sell | 4.5% |
| htf_aligned_bear | 0.8% |
| htf_aligned_bull | 42.3% |
| htf_disagreement | 5.9% |
| hull_bearish | 48.2% |
| hull_bullish | 51.8% |
| hull_flip_dn | 3.6% |
| hull_flip_up | 8.1% |
| ichi_above_cloud | 56.0% |
| ichi_above_cloud_break_recent_5d | 13.4% |
| ichi_below_cloud | 27.2% |
| ichi_below_cloud_break_recent_5d | 6.4% |
| ichi_cloud_thick | 88.5% |
| ichi_tk_bearish | 45.4% |
| ichi_tk_bullish | 48.2% |
| ichi_tk_cross_dn | 2.5% |
| ichi_tk_cross_up | 2.5% |
| ichi_weekly_above_cloud | 50.7% |
| ichi_weekly_below_cloud | 13.0% |
| ichi_weekly_in_cloud | 36.3% |
| in_reversal_window | 4.2% |
| inside_bar | 15.4% |
| inside_cpr | 5.0% |
| inside_kc | 82.6% |
| insider_cluster_active | 25.0% |
| institutional_buy | 88.0% |
| institutional_negative | 5.3% |
| institutional_persistence_growing | 36.1% |
| institutional_persistence_strong | 47.9% |
| institutional_strong_buy | 77.9% |
| inverted_cup_handle_detected | 11.5% |
| is_friday | 19.9% |
| is_halloween_period | 55.5% |
| is_halloween_period_first_day | 0.3% |
| is_january | 9.8% |
| is_january_extended | 12.3% |
| is_monday | 18.2% |
| is_pre_holiday | 4.5% |
| is_summer_period | 44.5% |
| is_totm_window | 40.1% |
| is_totm_window_first_day | 14.6% |
| is_week_open | 22.7% |
| kc_touch_lower | 3.6% |
| kc_touch_upper | 19.3% |
| large_dollar_buy | 0.6% |
| macd_12_26_9_bearish | 51.5% |
| macd_12_26_9_bullish | 48.5% |
| macd_12_26_9_crossover_dn | 3.4% |
| macd_12_26_9_crossover_up | 6.7% |
| macd_8_21_5_bearish | 49.0% |
| macd_8_21_5_bullish | 51.0% |
| macd_8_21_5_crossover_dn | 2.0% |
| macd_8_21_5_crossover_up | 6.2% |
| marubozu_bull | 0.6% |
| mfi_broad_overbought | 16.8% |
| mfi_broad_oversold | 7.8% |
| mfi_overbought | 4.8% |
| mfi_oversold | 1.1% |
| monthly_above_sma_12 | 86.4% |
| monthly_above_sma_6 | 70.2% |
| monthly_bias_bear | 3.8% |
| monthly_bias_bull | 60.5% |
| monthly_momentum_pos | 73.7% |
| morning_star | 10.1% |
| near_52w_high | 2.5% |
| near_52w_high_95pct | 7.3% |
| near_52w_high_retest_long | 3.9% |
| near_avwap_20high_atr_05x | 42.1% |
| near_avwap_20high_atr_10x | 64.1% |
| near_avwap_20high_atr_15x | 84.1% |
| near_avwap_20high_atr_20x | 93.1% |
| near_avwap_20low_atr_05x | 29.0% |
| near_avwap_20low_atr_10x | 50.9% |
| near_avwap_20low_atr_15x | 66.4% |
| near_avwap_20low_atr_20x | 76.5% |
| near_avwap_252low_atr_05x | 10.0% |
| near_avwap_252low_atr_10x | 18.2% |
| near_avwap_252low_atr_15x | 29.3% |
| near_avwap_252low_atr_20x | 41.6% |
| near_avwap_50low_atr_05x | 15.5% |
| near_avwap_50low_atr_10x | 31.5% |
| near_avwap_50low_atr_15x | 48.1% |
| near_avwap_50low_atr_20x | 61.3% |
| near_cam_r3 | 19.9% |
| near_cam_s3 | 9.5% |
| near_cam_s4 | 3.6% |
| near_fib_236 | 5.6% |
| near_fib_382 | 5.0% |
| near_fib_500 | 6.7% |
| near_fib_618 | 3.9% |
| near_fib_786 | 3.4% |
| near_pivot | 15.7% |
| near_prev_close | 18.5% |
| near_prev_high | 15.1% |
| near_prev_low | 4.5% |
| near_r1 | 17.1% |
| near_r1_wide | 60.8% |
| near_r2 | 8.1% |
| near_r2_wide | 38.9% |
| near_s1 | 5.0% |
| near_s1_wide | 31.7% |
| near_s2 | 0.8% |
| near_s2_wide | 10.9% |
| near_s3 | 0.3% |
| near_wood_r1 | 11.5% |
| near_wood_s1 | 9.8% |
| news_uses_polygon_score | 23.8% |
| obv_bearish | 44.5% |
| obv_bullish | 55.5% |
| obv_diverge_bull | 7.6% |
| obv_falling | 44.5% |
| obv_rising | 55.5% |
| outside_bar | 6.2% |
| pead_negative_surprise | 12.2% |
| pead_positive_surprise | 26.4% |
| pin_bar | 11.2% |
| po3_accumulation_active | 32.8% |
| po3_bullish | 19.3% |
| po3_manipulation_sweep_down | 4.2% |
| po3_manipulation_sweep_up | 13.2% |
| po3_mmbm_setup | 2.5% |
| po3_sweep_above_prior_high | 60.5% |
| po3_sweep_below_prior_low | 36.7% |
| ppo_bullish | 47.9% |
| ppo_crossover_dn | 2.8% |
| ppo_crossover_up | 7.0% |
| pre_fomc_d0 | 3.1% |
| pre_fomc_d1 | 2.0% |
| pre_fomc_window | 5.0% |
| price_above_dema | 53.8% |
| price_above_ema_20 | 61.3% |
| price_above_ema_200_break_recent_5d | 43.7% |
| price_above_ema_20_break_recent_5d | 28.9% |
| price_above_ema_21 | 60.8% |
| price_above_ema_21_break_recent_5d | 28.6% |
| price_above_ema_50 | 64.1% |
| price_above_ema_50_break_recent_5d | 26.6% |
| price_above_ema_9 | 61.3% |
| price_above_ema_9_break_recent_5d | 39.8% |
| price_above_hull | 57.7% |
| price_above_sma_200 | 86.3% |
| price_above_sma_21 | 57.1% |
| price_above_sma_50 | 61.6% |
| price_above_tema | 55.7% |
| price_below_dema | 46.2% |
| price_below_hull | 42.3% |
| price_below_tema | 44.3% |
| psar_bullish | 51.5% |
| psar_flip_dn | 2.8% |
| psar_flip_up | 8.1% |
| r1_break_retest_long | 58.3% |
| resistance_break_retest | 27.2% |
| risk_off_regime_bond_signal | 24.9% |
| risk_off_regime_bond_signal_strong | 10.4% |
| risk_off_regime_gold_signal | 43.1% |
| risk_on_regime_bond_signal | 40.6% |
| risk_on_regime_bond_signal_strong | 19.0% |
| roc_positive | 54.3% |
| roc_turning_dn | 3.6% |
| roc_turning_up | 10.6% |
| rsi_14_bullish | 61.1% |
| rsi_14_cross_dn_overbought_recent_3d | 3.4% |
| rsi_14_cross_up_oversold_recent_3d | 2.2% |
| rsi_14_overbought | 5.3% |
| rsi_14_rising | 75.9% |
| rsi_21_bullish | 62.7% |
| rsi_21_cross_dn_overbought_recent_3d | 0.6% |
| rsi_21_cross_up_oversold_recent_3d | 0.3% |
| rsi_21_overbought | 1.4% |
| rsi_21_rising | 75.9% |
| rsi_2_bullish | 67.2% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 15.7% |
| rsi_2_cross_dn_overbought_recent_3d | 19.0% |
| rsi_2_cross_up_extreme_os_recent_3d | 39.2% |
| rsi_2_cross_up_oversold_recent_3d | 46.2% |
| rsi_2_extreme_ob | 41.5% |
| rsi_2_extreme_os | 12.3% |
| rsi_2_overbought | 49.9% |
| rsi_2_oversold | 17.1% |
| rsi_2_rising | 75.9% |
| rsi_9_bullish | 61.6% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 1.4% |
| rsi_9_cross_dn_overbought_recent_3d | 6.7% |
| rsi_9_cross_up_extreme_os_recent_3d | 1.4% |
| rsi_9_cross_up_oversold_recent_3d | 10.6% |
| rsi_9_extreme_ob | 2.5% |
| rsi_9_overbought | 16.8% |
| rsi_9_oversold | 4.2% |
| rsi_9_rising | 75.9% |
| s1_break_retest_short | 45.9% |
| sc_13d_filed_within_30d | 2.4% |
| sc_13g_filed_within_30d | 0.9% |
| sector_outperforming_spy | 42.9% |
| sector_underperforming_spy | 57.1% |
| shooting_star | 5.9% |
| sma_20_50_bullish | 58.3% |
| sma_20_50_golden_cross | 0.8% |
| sma_50_200_bullish | 66.7% |
| sma_50_200_golden_cross | 0.6% |
| sma_9_21_bullish | 47.9% |
| sma_9_21_golden_cross | 1.4% |
| smc_bos_bearish | 5.9% |
| smc_bos_bullish | 13.2% |
| smc_bos_retest_long | 4.2% |
| smc_bos_retest_short | 5.6% |
| smc_breaker_block_bearish | 5.0% |
| smc_breaker_block_bullish | 24.4% |
| smc_choch_bearish | 3.6% |
| smc_choch_bullish | 4.2% |
| smc_equal_highs_swept | 4.2% |
| smc_equal_lows_swept | 1.1% |
| smc_fvg_bearish_active | 38.4% |
| smc_fvg_bullish_active | 40.1% |
| smc_fvg_retest_long_zone | 3.1% |
| smc_fvg_retest_short_zone | 14.0% |
| smc_in_discount_zone | 47.3% |
| smc_in_premium_zone | 73.7% |
| smc_inverse_fvg_bearish | 73.4% |
| smc_inverse_fvg_bullish | 93.0% |
| smc_liquidity_swept_dn | 1.4% |
| smc_liquidity_swept_up | 2.2% |
| smc_mitigation_block_long | 0.3% |
| smc_mitigation_block_short | 3.6% |
| smc_ob_bearish_active | 24.1% |
| smc_ob_bullish_active | 38.1% |
| smc_ote_long_zone | 10.9% |
| smc_ote_short_zone | 13.7% |
| squeeze_fire_dn | 0.3% |
| squeeze_fire_up | 3.9% |
| squeeze_in | 23.0% |
| squeeze_positive | 56.0% |
| stoch_bearish_cross | 6.2% |
| stoch_broad_overbought | 28.9% |
| stoch_broad_oversold | 25.5% |
| stoch_bullish_cross | 16.2% |
| stoch_overbought | 24.4% |
| stoch_oversold | 18.2% |
| stochrsi_cross_dn | 16.8% |
| stochrsi_cross_up | 32.2% |
| stochrsi_overbought | 36.4% |
| stochrsi_oversold | 29.1% |
| supertrend_bearish | 1.4% |
| supertrend_bullish | 98.6% |
| supertrend_flip_recent_long_5d | 1.1% |
| supertrend_flip_recent_short_5d | 1.4% |
| supertrend_flip_up | 0.6% |
| support_break_retest | 18.5% |
| tema_above_dema | 46.8% |
| tema_cross_dn | 1.4% |
| tema_cross_up | 3.4% |
| three_white_soldiers | 14.0% |
| triangle_apex_break_retest_long | 13.4% |
| triangle_ascending_detected | 12.6% |
| triangle_descending_detected | 7.6% |
| uo_overbought | 4.5% |
| usd_strengthening | 22.1% |
| usd_weakening | 10.9% |
| vix_band_high | 37.5% |
| vix_band_low | 45.7% |
| vix_band_mid | 16.8% |
| vix_term_backwardation | 5.6% |
| vix_term_contango | 94.4% |
| vol_above_avg | 40.1% |
| vol_below_avg | 59.9% |
| vol_spike_12x | 26.1% |
| vol_spike_15x | 12.9% |
| vol_spike_17x | 9.0% |
| vol_spike_2x | 5.9% |
| vol_spike_2x_on_down_day_recent_3d | 5.0% |
| vol_spike_2x_on_up_day_recent_3d | 6.2% |
| vol_spike_3x | 2.0% |
| vp_above_value_area | 34.2% |
| vp_below_value_area | 9.2% |
| vp_close_above_poc | 65.3% |
| vp_close_below_poc | 34.7% |
| vp_in_value_area | 56.6% |
| week_open_gap_down_15pct | 3.4% |
| week_open_gap_up_15pct | 0.8% |
| weekly_above_ema_10 | 64.7% |
| weekly_above_ema_20 | 76.5% |
| weekly_bias_bear | 21.3% |
| weekly_bias_bull | 62.5% |
| weekly_momentum_pos | 56.0% |
| williams_r_overbought | 35.6% |
| williams_r_oversold | 12.9% |
| williams_r_rising | 72.3% |
| within_pead_window | 38.0% |
| within_post_inclusion_window | 7.0% |
| xs_avoid_high_ivol | 68.9% |
| xs_avoid_high_max | 70.9% |
| xs_high_beta_decile | 26.6% |
| xs_low_beta_bottom_quintile | 26.6% |
| xs_low_beta_decile | 17.6% |
| xs_low_beta_decile_entry_recent_5d | 0.8% |
| xs_low_beta_top_quintile | 17.6% |
| xs_momentum_bottom_decile | 2.8% |
| xs_momentum_bottom_quintile | 9.5% |
| xs_momentum_top_decile | 21.0% |
| xs_momentum_top_quintile | 33.9% |
| xs_quality_bottom_quintile | 20.4% |
| xs_quality_top_quintile | 22.2% |
| xs_quality_top_tercile | 42.6% |
| year_high_break_retest_long | 0.6% |
| yoy_surprise_high | 53.8% |
| yoy_surprise_negative | 38.4% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 92.4% |
| committed_growth_holders | 92.4% |
| corp_donations_1y | 9.0% |
| corp_donations_count_1y | 9.0% |
| corp_donations_unique_pacs | 9.0% |
| cot_rut_commercials_pctile_3y | 41.2% |
| cot_rut_mmoney_pctile_3y | 41.2% |
| cup_handle_depth_pct | 25.2% |
| days_since_deletion | 5.3% |
| days_since_inclusion | 19.9% |
| days_to_next_holiday | 66.9% |
| days_to_rebalance | 7.8% |
| dpi_30d_avg | 97.5% |
| dpi_recent | 97.5% |
| earnings_announcement_return | 87.1% |
| earnings_eps_yoy_growth | 93.3% |
| flag_bull_pole_move_pct | 1.1% |
| gov_contracts_4q_sum | 39.2% |
| gov_contracts_last_qtr_amount | 39.2% |
| gov_contracts_qoq_growth | 39.2% |
| head_shoulders_magnitude_pct | 9.5% |
| insider_director_buyers_30d | 3.4% |
| insider_officer_buyers_30d | 3.4% |
| insider_total_shares_bought_30d | 3.4% |
| insider_unique_buyers_30d | 3.4% |
| inverted_cup_handle_height_pct | 21.3% |
| lobbying_amount_1y | 69.5% |
| lobbying_amount_q | 69.5% |
| lobbying_amount_yoy | 69.5% |
| monthly_momentum_6m | 95.0% |
| otc_short_ratio_recent | 97.5% |
| otc_volume_recent | 97.5% |
| pair_half_life | 94.7% |
| pair_max_abs_zscore | 94.7% |
| pair_zscore_signed | 94.7% |
| pct_from_avwap_20high | 81.2% |
| pct_from_avwap_20low | 90.8% |
| pct_from_avwap_252low | 95.5% |
| pct_from_avwap_50low | 97.8% |
| persistent_holders_4q | 92.4% |
| persistent_holders_8q | 92.4% |
| search_volume_index_recent | 79.3% |
| search_volume_observations | 79.3% |
| search_volume_zscore_30d | 79.3% |
| sector_etf_return_20d | 2.0% |
| spy_return_20d | 2.0% |
| total_active_holders | 92.4% |
| triangle_breakdown_pct | 7.6% |
| triangle_breakout_pct | 12.6% |
| xs_quality_decile | 60.5% |
| xs_quality_gross_profitability | 60.5% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.999), `avwap_252low` (0.992), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.998), `cam_r2` (0.998), `cam_r3` (0.998), `cam_r4` (0.998), `cam_s1` (0.998), `cam_s2` (0.998), `cam_s3` (0.998), `cam_s4` (0.998), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.998), `cpr_top` (0.998), `cup_handle_breakout_level` (0.997), `cup_handle_rim` (0.997), `dc10_lower` (0.998), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.998), `double_bottom_trough` (0.998), `double_top_neckline` (0.992), `double_top_peak` (0.992), `entry_stop_long` (0.997), `entry_stop_short` (0.997), `fib_236` (0.997), `fib_382` (0.998), `fib_500` (0.998), `fib_618` (0.998), `fib_786` (0.997), `fib_ext_127` (0.995), `fib_ext_162` (0.993), `flag_bear_breakdown_level` (1.0), `flag_bear_pole_move_pct` (-1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.988), `head_shoulders_top_neckline` (0.998), `hull_ma` (0.998), `ichi_kijun` (0.999), `ichi_senkou_a` (0.995), `ichi_senkou_b` (0.994), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (0.999), `monthly_close` (0.997), `monthly_sma_12` (0.989), `monthly_sma_6` (0.996), `pivot` (0.998), `prev_close` (0.998), `prev_high` (0.998), `prev_low` (0.998), `psar_value` (0.997), `r1` (0.998), `r2` (0.998), `r3` (0.998), `s1` (0.998), `s2` (0.998), `s3` (0.997), `sc_13g_latest_percent_owned` (-1.0), `supertrend_value` (0.996), `swing_high` (0.997), `swing_low` (0.996), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (0.998), `vp_poc` (0.995), `vp_value_area_high` (0.997), `vp_value_area_low` (0.995), `vwap_upper_2` (0.955), `weekly_close` (0.997), `weekly_ema_10` (0.999), `weekly_ema_20` (0.998), `wood_p` (0.998), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.998), `wood_s2` (0.998), `year_high` (0.992)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | ema span (the 200 in above/below_ema_200 | 3 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2 | news_article_count >= 2 | 5 | subset-safe | no - derives offline |
| P3 | news_sentiment_shift > 0.3 | 5 | subset-safe | no - derives offline |

```
FULL FACTORIAL     3 x 5 x 5 = 75
offline gradings   25 level-combinations x 24 exits = 600
ENGINE RUNS        1 (actuated fire-adding axes only)
PENDING ACTUATION  3 level-combinations are DEFINED but have no env knob - they are a FEATURE REQUEST, not a runnable band (plan 11.0b state 1; B2866)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 613 census axes join it only when REGISTERED at the T3 band review.
