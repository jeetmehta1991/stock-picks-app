# Table A - news_sentiment_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit e29a15af2 at 2026-09-17 17:07:43 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** news_sentiment | **status:** NOT-STARTED | **R5 fires:** 906 | **surviving fires (T1):** 906 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  price_above_ema_200  <- backtest/signals/index_rebalance.py +1
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P1.1-P1.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P2  news_article_count >= 3   [EXISTING-THRESHOLD]
P3  news_sentiment_mean > 0.3   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_news_sentiment_long (docstring and return dropped):

```python
fires = s.get('news_sentiment_mean', 0.0) > 0.3 and s.get('news_article_count', 0) >= 3 and s.get('price_above_ema_200', False)
sent = s.get('news_sentiment_mean', 0.0)
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
| P2 | STRATEGY | news_article_count `>= 3` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `>= 3` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P3 | STRATEGY | news_sentiment_mean `> 0.3` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `> 0.3` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| news_article_count | backtest/signals/news_sentiment.py +1 | `>= 3` | 100.0% | TIGHTER = RAISE the floor: 4 -> 744 (82%); 6 -> 574 (63%); 9 -> 400 (44%); 16 -> 188 (21%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | `> 0.3` | 100.0% | TIGHTER = RAISE the floor: 0.3593 -> 725 (80%); 0.4474 -> 544 (60%); 0.56 -> 363 (40%); 0.6667 -> 251 (28%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 16.42, 20.21, 24.4, 29.32 | 16.42: 725 (80%); 20.21: 544 (60%); 24.4: 364 (40%); 29.32: 183 (20%) | 16.42: 182 (20%); 20.21: 364 (40%); 24.4: 545 (60%); 29.32: 725 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 16.17, 20.35, 24.26, 29.07 | 16.17: 725 (80%); 20.35: 544 (60%); 24.26: 363 (40%); 29.07: 182 (20%) | 16.17: 182 (20%); 20.35: 364 (40%); 24.26: 544 (60%); 29.07: 726 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 18.49, 22.66, 27.05, 32.38 | 18.49: 725 (80%); 22.66: 545 (60%); 27.05: 365 (40%); 32.38: 182 (20%) | 18.49: 182 (20%); 22.66: 363 (40%); 27.05: 544 (60%); 32.38: 725 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -4.7055, -0.7599, 1.6826, 5.8703 | -4.7055: 725 (80%); -0.7599: 544 (60%); 1.6826: 363 (40%); 5.8703: 182 (20%) | -4.7055: 182 (20%); -0.7599: 363 (40%); 1.6826: 544 (60%); 5.8703: 725 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.3767, 2.514, 4.2507, 7.545 | 1.3767: 725 (80%); 2.514: 544 (60%); 4.2507: 363 (40%); 7.545: 182 (20%) | 1.3767: 182 (20%); 2.514: 363 (40%); 4.2507: 544 (60%); 7.545: 725 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.3767, 2.514, 4.2507, 7.545 | 1.3767: 725 (80%); 2.514: 544 (60%); 4.2507: 363 (40%); 7.545: 182 (20%) | 1.3767: 182 (20%); 2.514: 363 (40%); 4.2507: 544 (60%); 7.545: 725 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.082, 2.579, 3.162, 4.068 | 2.082: 726 (80%); 2.579: 544 (60%); 3.162: 363 (40%); 4.068: 182 (20%) | 2.082: 183 (20%); 2.579: 363 (40%); 3.162: 544 (60%); 4.068: 725 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.06, 0.0879, 0.1234, 0.1733 | 0.06: 725 (80%); 0.0879: 544 (60%); 0.1234: 363 (40%); 0.1733: 182 (20%) | 0.06: 182 (20%); 0.0879: 363 (40%); 0.1234: 544 (60%); 0.1733: 726 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.2866, 0.5212, 0.7417, 0.8967 | 0.2866: 725 (80%); 0.5212: 544 (60%); 0.7417: 363 (40%); 0.8967: 182 (20%) | 0.2866: 182 (20%); 0.5212: 363 (40%); 0.7417: 544 (60%); 0.8967: 725 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0662, 0.0901, 0.1191, 0.1571 | 0.0662: 725 (80%); 0.0901: 544 (60%); 0.1191: 363 (40%); 0.1571: 182 (20%) | 0.0662: 182 (20%); 0.0901: 363 (40%); 0.1191: 544 (60%); 0.1571: 725 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.1724, 0.5082, 0.8054, 1.0919 | 0.1724: 725 (80%); 0.5082: 544 (60%); 0.8054: 364 (40%); 1.0919: 182 (20%) | 0.1724: 182 (20%); 0.5082: 363 (40%); 0.8054: 544 (60%); 1.0919: 725 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.0883, 0.1201, 0.1588, 0.2094 | 0.0883: 725 (80%); 0.1201: 544 (60%); 0.1588: 363 (40%); 0.2094: 182 (20%) | 0.0883: 182 (20%); 0.1201: 363 (40%); 0.1588: 544 (60%); 0.2094: 725 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.2543, 0.5061, 0.729, 0.9439 | 0.2543: 725 (80%); 0.5061: 544 (60%); 0.729: 364 (40%); 0.9439: 182 (20%) | 0.2543: 182 (20%); 0.5061: 363 (40%); 0.729: 544 (60%); 0.9439: 725 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0512, -0.0239, -0.0046, 0.0272 | -0.0512: 727 (80%); -0.0239: 549 (61%); -0.0046: 363 (40%); 0.0272: 184 (20%) | -0.0512: 182 (20%); -0.0239: 363 (40%); -0.0046: 544 (60%); 0.0272: 726 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1469, 0.1796, 0.2383, 0.2706 | 0.1469: 726 (80%); 0.1796: 545 (60%); 0.2383: 363 (40%); 0.2706: 183 (20%) | 0.1469: 180 (20%); 0.1796: 361 (40%); 0.2383: 543 (60%); 0.2706: 723 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 906 (100%) | 0: 873 (96%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0771, 0.0048, 0.0695, 0.1597 | -0.0771: 725 (80%); 0.0048: 544 (60%); 0.0695: 363 (40%); 0.1597: 182 (20%) | -0.0771: 182 (20%); 0.0048: 363 (40%); 0.0695: 544 (60%); 0.1597: 726 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 906 (100%); 1: 353 (39%) | 0: 553 (61%); 1: 750 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2461, -0.2132, -0.16, -0.1189 | -0.2461: 728 (80%); -0.2132: 552 (61%); -0.16: 366 (40%); -0.1189: 184 (20%) | -0.2461: 185 (20%); -0.2132: 368 (41%); -0.16: 545 (60%); -0.1189: 725 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3974, 0.6282, 0.6923, 0.7821 | 0.3974: 728 (80%); 0.6282: 549 (61%); 0.6923: 387 (43%); 0.7821: 184 (20%) | 0.3974: 185 (20%); 0.6282: 376 (42%); 0.6923: 545 (60%); 0.7821: 729 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.25, 0.3141, 0.5256, 0.8333 | 0.25: 738 (81%); 0.3141: 601 (66%); 0.5256: 363 (40%); 0.8333: 182 (20%) | 0.25: 182 (20%); 0.3141: 373 (41%); 0.5256: 547 (60%); 0.8333: 730 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0908, 0.0117, 0.1092, 0.254 | -0.0908: 730 (81%); 0.0117: 544 (60%); 0.1092: 364 (40%); 0.254: 190 (21%) | -0.0908: 183 (20%); 0.0117: 368 (41%); 0.1092: 547 (60%); 0.254: 725 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2692, 0.4808, 0.6731, 0.9038 | 0.2692: 727 (80%); 0.4808: 544 (60%); 0.6731: 363 (40%); 0.9038: 186 (21%) | 0.2692: 186 (21%); 0.4808: 366 (40%); 0.6731: 550 (61%); 0.9038: 764 (84%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1282, 0.3462, 0.4808, 0.6731 | 0.1282: 730 (81%); 0.3462: 547 (60%); 0.4808: 390 (43%); 0.6731: 191 (21%) | 0.1282: 191 (21%); 0.3462: 372 (41%); 0.4808: 573 (63%); 0.6731: 728 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.53, -0.4339, -0.23, -0.0277 | -0.53: 726 (80%); -0.4339: 546 (60%); -0.23: 369 (41%); -0.0277: 183 (20%) | -0.53: 184 (20%); -0.4339: 363 (40%); -0.23: 545 (60%); -0.0277: 729 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3013, 0.4615, 0.5897, 0.8462 | 0.3013: 726 (80%); 0.4615: 559 (62%); 0.5897: 366 (40%); 0.8462: 191 (21%) | 0.3013: 193 (21%); 0.4615: 376 (42%); 0.5897: 554 (61%); 0.8462: 730 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.141, 0.3269, 0.5449, 0.8013 | 0.141: 732 (81%); 0.3269: 547 (60%); 0.5449: 365 (40%); 0.8013: 185 (20%) | 0.141: 185 (20%); 0.3269: 368 (41%); 0.5449: 546 (60%); 0.8013: 729 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0649, -0.0588, -0.0424, 0 | -0.0649: 726 (80%); -0.0588: 544 (60%); -0.0424: 363 (40%); 0: 226 (25%) | -0.0649: 187 (21%); -0.0588: 363 (40%); -0.0424: 554 (61%); 0: 869 (96%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4744, 0.7051, 0.8718, 0.9936 | 0.4744: 725 (80%); 0.7051: 558 (62%); 0.8718: 374 (41%); 0.9936: 203 (22%) | 0.4744: 183 (20%); 0.7051: 366 (40%); 0.8718: 544 (60%); 0.9936: 748 (83%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1218, 0.2179, 0.5769, 0.891 | 0.1218: 731 (81%); 0.2179: 555 (61%); 0.5769: 366 (40%); 0.891: 188 (21%) | 0.1218: 187 (21%); 0.2179: 365 (40%); 0.5769: 552 (61%); 0.891: 728 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0063, 0.0292, 0.0549, 0.179 | -0.0063: 727 (80%); 0.0292: 545 (60%); 0.0549: 375 (41%); 0.179: 184 (20%) | -0.0063: 182 (20%); 0.0292: 373 (41%); 0.0549: 548 (60%); 0.179: 729 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5211, 0.7778, 0.9167, 0.9744 | 0.5211: 725 (80%); 0.7778: 549 (61%); 0.9167: 369 (41%); 0.9744: 193 (21%) | 0.5211: 191 (21%); 0.7778: 364 (40%); 0.9167: 545 (60%); 0.9744: 761 (84%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0962, 0.2278, 0.5385, 0.7882 | 0.0962: 733 (81%); 0.2278: 552 (61%); 0.5385: 369 (41%); 0.7882: 187 (21%) | 0.0962: 194 (21%); 0.2278: 368 (41%); 0.5385: 544 (60%); 0.7882: 725 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0095, 0.0787, 0.1523 | -0.0812: 812 (90%); -0.0095: 547 (60%); 0.0787: 364 (40%); 0.1523: 182 (20%) | -0.0812: 206 (23%); -0.0095: 370 (41%); 0.0787: 546 (60%); 0.1523: 729 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1699, -0.0216, 0.0256, 0.0822 | -0.1699: 726 (80%); -0.0216: 549 (61%); 0.0256: 364 (40%); 0.0822: 191 (21%) | -0.1699: 184 (20%); -0.0216: 367 (41%); 0.0256: 546 (60%); 0.0822: 726 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.5321, 0.7115, 0.8205 | 0.2628: 734 (81%); 0.5321: 553 (61%); 0.7115: 376 (42%); 0.8205: 197 (22%) | 0.2628: 189 (21%); 0.5321: 363 (40%); 0.7115: 547 (60%); 0.8205: 725 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1474, 0.3782, 0.6026, 0.8462 | 0.1474: 727 (80%); 0.3782: 549 (61%); 0.6026: 365 (40%); 0.8462: 188 (21%) | 0.1474: 193 (21%); 0.3782: 381 (42%); 0.6026: 549 (61%); 0.8462: 725 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.07, 0.1875, 0.3683, 0.7867 | 0.07: 726 (80%); 0.1875: 544 (60%); 0.3683: 363 (40%); 0.7867: 182 (20%) | 0.07: 186 (21%); 0.1875: 363 (40%); 0.3683: 545 (60%); 0.7867: 725 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 99.0% | 20, 61, 83, 145 | 20: 723 (80%); 61: 547 (60%); 83: 365 (40%); 145: 181 (20%) | 20: 191 (21%); 61: 372 (41%); 83: 539 (59%); 145: 720 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.6% | 1.6467, 2.1003, 2.7131, 3.6904 | 1.6467: 721 (80%); 2.1003: 541 (60%); 2.7131: 361 (40%); 3.6904: 181 (20%) | 1.6467: 181 (20%); 2.1003: 361 (40%); 2.7131: 541 (60%); 3.6904: 721 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 12, 21, 29, 37 | 12: 731 (81%); 21: 558 (62%); 29: 372 (41%); 37: 197 (22%) | 12: 198 (22%); 21: 371 (41%); 29: 568 (63%); 37: 741 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 0, 2, 3 | 0: 906 (100%); 2: 544 (60%); 3: 369 (41%) | 0: 189 (21%); 2: 537 (59%); 3: 730 (81%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0148, -0.0044, 0.0112, 0.0226 | -0.0148: 728 (80%); -0.0044: 549 (61%); 0.0112: 363 (40%); 0.0226: 182 (20%) | -0.0148: 182 (20%); -0.0044: 363 (40%); 0.0112: 545 (60%); 0.0226: 727 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.3078, 25.047, 26.1857, 27.08 | 24.3078: 727 (80%); 25.047: 544 (60%); 26.1857: 363 (40%); 27.08: 182 (20%) | 24.3078: 187 (21%); 25.047: 363 (40%); 26.1857: 544 (60%); 27.08: 730 (81%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.743, -0.19, 0.217, 0.849 | -0.743: 726 (80%); -0.19: 544 (60%); 0.217: 363 (40%); 0.849: 183 (20%) | -0.743: 182 (20%); -0.19: 363 (40%); 0.217: 544 (60%); 0.849: 725 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.849, -0.217, 0.19, 0.743 | -0.849: 725 (80%); -0.217: 544 (60%); 0.19: 363 (40%); 0.743: 182 (20%) | -0.849: 183 (20%); -0.217: 363 (40%); 0.19: 544 (60%); 0.743: 726 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0461, -0.0095, 0.0262, 0.0653 | -0.0461: 725 (80%); -0.0095: 545 (60%); 0.0262: 366 (40%); 0.0653: 184 (20%) | -0.0461: 182 (20%); -0.0095: 363 (40%); 0.0262: 550 (61%); 0.0653: 725 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 7.9719, 8.4278, 8.6311, 8.949 | 7.9719: 727 (80%); 8.4278: 554 (61%); 8.6311: 358 (40%); 8.949: 182 (20%) | 7.9719: 179 (20%); 8.4278: 352 (39%); 8.6311: 548 (60%); 8.949: 724 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.4% | 0, 1 | 0: 901 (99%); 1: 342 (38%) | 0: 559 (62%); 1: 750 (83%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.4% | -1, 0, 1 | -1: 851 (94%); 0: 714 (79%); 1: 185 (20%) | -1: 187 (21%); 0: 716 (79%); 1: 844 (93%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.4% | 0, 1 | 0: 901 (99%); 1: 336 (37%) | 0: 565 (62%); 1: 758 (84%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 1, 3, 6, 100 | 1: 760 (84%); 3: 605 (67%); 6: 377 (42%); 100: 182 (20%) | 1: 210 (23%); 3: 384 (42%); 6: 585 (65%); 100: 726 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 0, 2, 5, 90 | 0: 906 (100%); 2: 568 (63%); 5: 365 (40%); 90: 182 (20%) | 0: 242 (27%); 2: 437 (48%); 5: 568 (63%); 90: 727 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.813, -0.1954, 0.1846, 0.9581 | -0.813: 725 (80%); -0.1954: 544 (60%); 0.1846: 363 (40%); 0.9581: 182 (20%) | -0.813: 182 (20%); -0.1954: 364 (40%); 0.1846: 544 (60%); 0.9581: 725 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -1.4539, -0.1013, 0.6566, 2.1789 | -1.4539: 725 (80%); -0.1013: 544 (60%); 0.6566: 363 (40%); 2.1789: 182 (20%) | -1.4539: 182 (20%); -0.1013: 363 (40%); 0.6566: 544 (60%); 2.1789: 725 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.2658, -0.1116, 0.551, 1.8329 | -1.2658: 725 (80%); -0.1116: 544 (60%); 0.551: 363 (40%); 1.8329: 182 (20%) | -1.2658: 182 (20%); -0.1116: 363 (40%); 0.551: 544 (60%); 1.8329: 725 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.6378, -0.1171, 0.1798, 0.7647 | -0.6378: 725 (80%); -0.1171: 544 (60%); 0.1798: 364 (40%); 0.7647: 182 (20%) | -0.6378: 182 (20%); -0.1171: 363 (40%); 0.1798: 544 (60%); 0.7647: 725 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -1.724, -0.1849, 0.8025, 2.6581 | -1.724: 725 (80%); -0.1849: 544 (60%); 0.8025: 363 (40%); 2.6581: 182 (20%) | -1.724: 182 (20%); -0.1849: 363 (40%); 0.8025: 544 (60%); 2.6581: 725 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -1.7836, -0.2085, 0.6395, 2.2303 | -1.7836: 725 (80%); -0.2085: 544 (60%); 0.6395: 363 (40%); 2.2303: 182 (20%) | -1.7836: 182 (20%); -0.2085: 363 (40%); 0.6395: 544 (60%); 2.2303: 725 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 38.27, 48.83, 57.76, 69.22 | 38.27: 725 (80%); 48.83: 544 (60%); 57.76: 363 (40%); 69.22: 182 (20%) | 38.27: 182 (20%); 48.83: 363 (40%); 57.76: 544 (60%); 69.22: 725 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.4% | 0.0055, 0.0135, 0.023, 0.0422 | 0.0055: 721 (80%); 0.0135: 538 (59%); 0.023: 361 (40%); 0.0422: 181 (20%) | 0.0055: 180 (20%); 0.0135: 363 (40%); 0.023: 540 (60%); 0.0422: 720 (79%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1111 | 0: 906 (100%); 0.1111: 184 (20%) | 0: 562 (62%); 0.1111: 743 (82%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0.4545, 0.5517, 0.6557, 0.75 | 0.4545: 728 (80%); 0.5517: 544 (60%); 0.6557: 363 (40%); 0.75: 191 (21%) | 0.4545: 187 (21%); 0.5517: 363 (40%); 0.6557: 544 (60%); 0.75: 762 (84%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 3, 4, 7, 12 | 3: 769 (85%); 4: 620 (68%); 7: 368 (41%); 12: 190 (21%) | 3: 286 (32%); 4: 389 (43%); 7: 583 (64%); 12: 739 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 4, 6, 9, 16 | 4: 744 (82%); 6: 574 (63%); 9: 400 (44%); 16: 188 (21%) | 4: 247 (27%); 6: 411 (45%); 9: 551 (61%); 16: 730 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 2, 4, 7, 13 | 2: 753 (83%); 4: 577 (64%); 7: 381 (42%); 13: 195 (22%) | 2: 231 (25%); 4: 410 (45%); 7: 570 (63%); 13: 725 (80%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.3, 0.3792, 0.4691, 0.5882 | 0.3: 728 (80%); 0.3792: 544 (60%); 0.4691: 363 (40%); 0.5882: 182 (20%) | 0.3: 183 (20%); 0.3792: 363 (40%); 0.4691: 544 (60%); 0.5882: 725 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0.2711, 0.4323, 0.5833, 0.8333 | 0.2711: 725 (80%); 0.4323: 544 (60%); 0.5833: 364 (40%); 0.8333: 183 (20%) | 0.2711: 182 (20%); 0.4323: 363 (40%); 0.5833: 547 (60%); 0.8333: 732 (81%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0.3593, 0.4474, 0.56, 0.6667 | 0.3593: 725 (80%); 0.4474: 544 (60%); 0.56: 363 (40%); 0.6667: 251 (28%) | 0.3593: 182 (20%); 0.4474: 364 (40%); 0.56: 546 (60%); 0.6667: 732 (81%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.125, 0, 0.1667, 0.3751 | -0.125: 726 (80%); 0: 633 (70%); 0.1667: 368 (41%); 0.3751: 182 (20%) | -0.125: 183 (20%); 0: 377 (42%); 0.1667: 555 (61%); 0.3751: 725 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.3788, 0.2981, 1.1321, 2.5842 | -0.3788: 725 (80%); 0.2981: 545 (60%); 1.1321: 363 (40%); 2.5842: 183 (20%) | -0.3788: 182 (20%); 0.2981: 363 (40%); 1.1321: 544 (60%); 2.5842: 726 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 12 | 2: 768 (85%); 4: 605 (67%); 7: 412 (45%); 12: 183 (20%) | 2: 223 (25%); 4: 364 (40%); 7: 552 (61%); 12: 742 (82%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0447, -0.0037, 0.0304, 0.0791 | -0.0447: 725 (80%); -0.0037: 544 (60%); 0.0304: 363 (40%); 0.0791: 182 (20%) | -0.0447: 181 (20%); -0.0037: 362 (40%); 0.0304: 543 (60%); 0.0791: 724 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0582, -0.0043, 0.0448, 0.0962 | -0.0582: 724 (80%); -0.0043: 543 (60%); 0.0448: 362 (40%); 0.0962: 181 (20%) | -0.0582: 182 (20%); -0.0043: 363 (40%); 0.0448: 544 (60%); 0.0962: 725 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0316, -0.0021, 0.0225, 0.0597 | -0.0316: 724 (80%); -0.0021: 543 (60%); 0.0225: 363 (40%); 0.0597: 181 (20%) | -0.0316: 182 (20%); -0.0021: 363 (40%); 0.0225: 543 (60%); 0.0597: 725 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -1.029, 6.596, 15.127, 38.813 | -1.029: 725 (80%); 6.596: 544 (60%); 15.127: 363 (40%); 38.813: 182 (20%) | -1.029: 182 (20%); 6.596: 363 (40%); 15.127: 544 (60%); 38.813: 725 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0445, 0.0617, 0.083, 0.1137 | 0.0445: 725 (80%); 0.0617: 544 (60%); 0.083: 364 (40%); 0.1137: 182 (20%) | 0.0445: 184 (20%); 0.0617: 363 (40%); 0.083: 544 (60%); 0.1137: 725 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.5325, 0.7024, 0.8087, 0.9089 | 0.5325: 725 (80%); 0.7024: 544 (60%); 0.8087: 363 (40%); 0.9089: 182 (20%) | 0.5325: 182 (20%); 0.7024: 363 (40%); 0.8087: 544 (60%); 0.9089: 725 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.2609, -0.1926, 0.8337, 1.9478 | -1.2609: 725 (80%); -0.1926: 544 (60%); 0.8337: 363 (40%); 1.9478: 182 (20%) | -1.2609: 182 (20%); -0.1926: 363 (40%); 0.8337: 544 (60%); 1.9478: 725 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.7351, -0.2406, 0.2659, 0.8099 | -0.7351: 725 (80%); -0.2406: 544 (60%); 0.2659: 363 (40%); 0.8099: 182 (20%) | -0.7351: 182 (20%); -0.2406: 363 (40%); 0.2659: 544 (60%); 0.8099: 725 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.1703, -0.1324, 0.7253, 1.7125 | -1.1703: 725 (80%); -0.1324: 544 (60%); 0.7253: 363 (40%); 1.7125: 182 (20%) | -1.1703: 183 (20%); -0.1324: 363 (40%); 0.7253: 544 (60%); 1.7125: 725 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -5.07, -0.47, 3.685, 8.241 | -5.07: 725 (80%); -0.47: 544 (60%); 3.685: 363 (40%); 8.241: 182 (20%) | -5.07: 182 (20%); -0.47: 363 (40%); 3.685: 544 (60%); 8.241: 725 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 43.94, 50.79, 58.03, 64.15 | 43.94: 726 (80%); 50.79: 544 (60%); 58.03: 363 (40%); 64.15: 182 (20%) | 43.94: 183 (20%); 50.79: 363 (40%); 58.03: 544 (60%); 64.15: 725 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 38.79, 62.56, 80.52, 93.05 | 38.79: 725 (80%); 62.56: 544 (60%); 80.52: 363 (40%); 93.05: 182 (20%) | 38.79: 182 (20%); 62.56: 363 (40%); 80.52: 544 (60%); 93.05: 725 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 46.51, 51.1, 55.7, 60.59 | 46.51: 726 (80%); 51.1: 544 (60%); 55.7: 364 (40%); 60.59: 182 (20%) | 46.51: 182 (20%); 51.1: 363 (40%); 55.7: 544 (60%); 60.59: 725 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 41.11, 51.18, 60.48, 69.34 | 41.11: 725 (80%); 51.18: 544 (60%); 60.48: 363 (40%); 69.34: 182 (20%) | 41.11: 182 (20%); 51.18: 363 (40%); 60.48: 544 (60%); 69.34: 725 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 905 (100%) | 0: 906 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0337, 0.0492, 0.0624, 0.0951 | 0.0337: 727 (80%); 0.0492: 544 (60%); 0.0624: 364 (40%); 0.0951: 182 (20%) | 0.0337: 184 (20%); 0.0492: 366 (40%); 0.0624: 544 (60%); 0.0951: 725 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0877, -0.0611, -0.0443, -0.0337 | -0.0877: 732 (81%); -0.0611: 544 (60%); -0.0443: 363 (40%); -0.0337: 183 (20%) | -0.0877: 184 (20%); -0.0611: 363 (40%); -0.0443: 548 (60%); -0.0337: 725 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 3 | 0: 906 (100%); 3: 182 (20%) | 0: 594 (66%); 3: 753 (83%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 24, 34, 48, 65 | 24: 733 (81%); 34: 542 (60%); 48: 365 (40%); 65: 199 (22%) | 24: 190 (21%); 34: 368 (41%); 48: 542 (60%); 65: 728 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.1% | 0.0102, 0.015, 0.0228, 0.036 | 0.0102: 710 (78%); 0.015: 534 (59%); 0.0228: 354 (39%); 0.036: 178 (20%) | 0.0102: 179 (20%); 0.015: 355 (39%); 0.0228: 536 (59%); 0.036: 711 (78%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.3488, 0.5219, 0.6959, 0.8872 | 0.3488: 725 (80%); 0.5219: 544 (60%); 0.6959: 363 (40%); 0.8872: 182 (20%) | 0.3488: 182 (20%); 0.5219: 363 (40%); 0.6959: 544 (60%); 0.8872: 725 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 41, 57.7, 74.1, 108.5 | 41: 725 (80%); 57.7: 545 (60%); 74.1: 363 (40%); 108.5: 182 (20%) | 41: 183 (20%); 57.7: 363 (40%); 74.1: 545 (60%); 108.5: 725 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -3.325, -0.0975, 2.52, 7.305 | -3.325: 725 (80%); -0.0975: 544 (60%); 2.52: 363 (40%); 7.305: 182 (20%) | -3.325: 182 (20%); -0.0975: 363 (40%); 2.52: 544 (60%); 7.305: 725 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 21.69, 42.75, 64.56, 83.38 | 21.69: 725 (80%); 42.75: 544 (60%); 64.56: 363 (40%); 83.38: 182 (20%) | 21.69: 182 (20%); 42.75: 363 (40%); 64.56: 544 (60%); 83.38: 725 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 22.33, 43.25, 68.35, 86.91 | 22.33: 725 (80%); 43.25: 544 (60%); 68.35: 363 (40%); 86.91: 182 (20%) | 22.33: 184 (20%); 43.25: 363 (40%); 68.35: 544 (60%); 86.91: 725 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 11.99, 32.46, 67.54, 92.65 | 11.99: 725 (80%); 32.46: 544 (60%); 67.54: 363 (40%); 92.65: 182 (20%) | 11.99: 182 (20%); 32.46: 363 (40%); 67.54: 544 (60%); 92.65: 725 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 11.89, 39.83, 76.71, 100 | 11.89: 725 (80%); 39.83: 544 (60%); 76.71: 363 (40%); 100: 224 (25%) | 11.89: 182 (20%); 39.83: 363 (40%); 76.71: 544 (60%); 100: 906 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 7, 12, 17 | 4: 744 (82%); 7: 583 (64%); 12: 393 (43%); 17: 196 (22%) | 4: 214 (24%); 7: 364 (40%); 12: 566 (62%); 17: 752 (83%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 10, 14, 18 | 5: 744 (82%); 10: 548 (60%); 14: 385 (42%); 18: 211 (23%) | 5: 195 (22%); 10: 406 (45%); 14: 557 (61%); 18: 752 (83%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 44.51, 50.67, 55.72, 62.2 | 44.51: 725 (80%); 50.67: 544 (60%); 55.72: 364 (40%); 62.2: 182 (20%) | 44.51: 182 (20%); 50.67: 363 (40%); 55.72: 544 (60%); 62.2: 725 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.123, 0.3333, 0.627, 0.8571 | 0.123: 725 (80%); 0.3333: 549 (61%); 0.627: 364 (40%); 0.8571: 186 (21%) | 0.123: 186 (21%); 0.3333: 363 (40%); 0.627: 546 (60%); 0.8571: 727 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.77, 17.44, 20.68, 25.72 | 14.77: 725 (80%); 17.44: 546 (60%); 20.68: 363 (40%); 25.72: 183 (20%) | 14.77: 182 (20%); 17.44: 363 (40%); 20.68: 546 (60%); 25.72: 726 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 14.77, 17.44, 20.68, 25.72 | 14.77: 725 (80%); 17.44: 546 (60%); 20.68: 363 (40%); 25.72: 183 (20%) | 14.77: 182 (20%); 17.44: 363 (40%); 20.68: 546 (60%); 25.72: 726 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8607, 0.8886, 0.9229, 0.9604 | 0.8607: 726 (80%); 0.8886: 545 (60%); 0.9229: 363 (40%); 0.9604: 183 (20%) | 0.8607: 184 (20%); 0.8886: 363 (40%); 0.9229: 546 (60%); 0.9604: 730 (81%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.74, 0.87, 1.01, 1.3 | 0.74: 725 (80%); 0.87: 544 (60%); 1.01: 366 (40%); 1.3: 186 (21%) | 0.74: 193 (21%); 0.87: 379 (42%); 1.01: 545 (60%); 1.3: 727 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0187, 0.0412, 0.0701, 0.1128 | 0.0187: 725 (80%); 0.0412: 544 (60%); 0.0701: 363 (40%); 0.1128: 182 (20%) | 0.0187: 182 (20%); 0.0412: 363 (40%); 0.0701: 545 (60%); 0.1128: 725 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 45.2138, 79.3358, 115.7005, 213.8643 | 45.2138: 725 (80%); 79.3358: 544 (60%); 115.7005: 363 (40%); 213.8643: 182 (20%) | 45.2138: 182 (20%); 79.3358: 363 (40%); 115.7005: 544 (60%); 213.8643: 725 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 43.0487, 75.369, 110.3625, 204.9788 | 43.0487: 725 (80%); 75.369: 544 (60%); 110.3625: 363 (40%); 204.9788: 182 (20%) | 43.0487: 182 (20%); 75.369: 363 (40%); 110.3625: 544 (60%); 204.9788: 725 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 40.3509, 70.7858, 106.2776, 193.7556 | 40.3509: 725 (80%); 70.7858: 544 (60%); 106.2776: 363 (40%); 193.7556: 182 (20%) | 40.3509: 182 (20%); 70.7858: 363 (40%); 106.2776: 544 (60%); 193.7556: 725 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 47.4808, 85.1563, 123.5141, 221.9574 | 47.4808: 725 (80%); 85.1563: 544 (60%); 123.5141: 363 (40%); 221.9574: 182 (20%) | 47.4808: 182 (20%); 85.1563: 363 (40%); 123.5141: 544 (60%); 221.9574: 725 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 906 (100%) | 0: 781 (86%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 906 (100%) | 0: 823 (91%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0568, -0.0071, 0.0429, 0.0966 | -0.0568: 725 (80%); -0.0071: 544 (60%); 0.0429: 363 (40%); 0.0966: 182 (20%) | -0.0568: 182 (20%); -0.0071: 363 (40%); 0.0429: 546 (60%); 0.0966: 725 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -72.89, -48.88, -23.39, -7.65 | -72.89: 725 (80%); -48.88: 544 (60%); -23.39: 363 (40%); -7.65: 182 (20%) | -72.89: 182 (20%); -48.88: 363 (40%); -23.39: 544 (60%); -7.65: 725 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.3% | 0.5555, 0.8334, 1.1053, 1.4362 | 0.5555: 720 (79%); 0.8334: 540 (60%); 1.1053: 360 (40%); 1.4362: 180 (20%) | 0.5555: 180 (20%); 0.8334: 360 (40%); 1.1053: 540 (60%); 1.4362: 720 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.3% | 3, 5, 8, 9 | 3: 732 (81%); 5: 596 (66%); 8: 370 (41%); 9: 273 (30%) | 3: 228 (25%); 5: 395 (44%); 8: 627 (69%); 9: 738 (81%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 99.3% | 0.1948, 0.2355, 0.2907, 0.3842 | 0.1948: 721 (80%); 0.2355: 540 (60%); 0.2907: 360 (40%); 0.3842: 180 (20%) | 0.1948: 181 (20%); 0.2355: 361 (40%); 0.2907: 540 (60%); 0.3842: 720 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 99.3% | 3, 6, 8, 9 | 3: 775 (86%); 6: 547 (60%); 8: 393 (43%); 9: 290 (32%) | 3: 194 (21%); 6: 426 (47%); 8: 610 (67%); 9: 726 (80%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.3% | 0.0254, 0.0349, 0.0463, 0.0698 | 0.0254: 720 (79%); 0.0349: 541 (60%); 0.0463: 360 (40%); 0.0698: 181 (20%) | 0.0254: 182 (20%); 0.0349: 364 (40%); 0.0463: 540 (60%); 0.0698: 720 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.3% | 3, 6, 8, 10 | 3: 781 (86%); 6: 570 (63%); 8: 396 (44%); 10: 183 (20%) | 3: 185 (20%); 6: 414 (46%); 8: 595 (66%); 10: 900 (99%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.4% | -0.0805, 0.0535, 0.1739, 0.4252 | -0.0805: 721 (80%); 0.0535: 541 (60%); 0.1739: 361 (40%); 0.4252: 181 (20%) | -0.0805: 181 (20%); 0.0535: 361 (40%); 0.1739: 541 (60%); 0.4252: 721 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.4% | 4, 6, 8, 10 | 4: 756 (83%); 6: 594 (66%); 8: 428 (47%); 10: 207 (23%) | 4: 227 (25%); 6: 385 (42%); 8: 581 (64%); 10: 901 (99%) | OFFLINE |
| year_low | backtest/signals/technical.py | 100.0% | 35.91, 61.93, 95.77, 165.03 | 35.91: 725 (80%); 61.93: 544 (60%); 95.77: 363 (40%); 165.03: 182 (20%) | 35.91: 182 (20%); 61.93: 363 (40%); 95.77: 545 (60%); 165.03: 725 (80%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 4.4% |
| 8k_item_5_02_filed_within_7d | 3.0% |
| above_avwap_20high | 47.1% |
| above_avwap_20low | 89.4% |
| above_avwap_252low | 95.3% |
| above_avwap_50low | 79.2% |
| above_cam_r3 | 58.7% |
| above_cam_r4 | 35.1% |
| above_cpr | 73.2% |
| above_pivot | 78.0% |
| above_prev_high | 44.9% |
| above_prev_high_clearance_atr_05 | 19.1% |
| above_prev_low | 94.3% |
| above_r1 | 40.0% |
| above_r2 | 18.3% |
| above_vwap | 77.9% |
| above_wood_p | 70.1% |
| ad_rising | 63.6% |
| adx_cross_up | 1.9% |
| adx_cross_up_20 | 2.3% |
| adx_di_bear | 42.7% |
| adx_di_bull | 57.3% |
| adx_strong | 3.5% |
| adx_trending | 37.5% |
| ao_cross_dn | 2.4% |
| ao_cross_up | 3.0% |
| ao_positive | 53.8% |
| ao_twin_peaks_bull | 4.4% |
| at_key_fib | 15.6% |
| at_key_fib_wide | 41.1% |
| avwap_20high_loss_recent_3d | 13.0% |
| avwap_20high_reclaim_recent_3d | 29.5% |
| avwap_20low_loss_recent_3d | 7.0% |
| avwap_20low_reclaim_recent_3d | 27.0% |
| avwap_252low_loss_recent_3d | 1.3% |
| avwap_252low_reclaim_recent_3d | 14.6% |
| avwap_50low_loss_recent_3d | 8.6% |
| avwap_50low_reclaim_recent_3d | 15.8% |
| bb_10_20_above_mid | 61.7% |
| bb_10_20_expanding | 53.2% |
| bb_10_20_pctb_gt_75 | 39.1% |
| bb_10_20_pctb_gt_8 | 33.1% |
| bb_10_20_pctb_gt_85 | 26.7% |
| bb_10_20_pctb_gt_9 | 19.9% |
| bb_10_20_pctb_gt_95 | 13.5% |
| bb_10_20_pctb_lt_05 | 1.1% |
| bb_10_20_pctb_lt_1 | 2.8% |
| bb_10_20_pctb_lt_15 | 6.2% |
| bb_10_20_pctb_lt_2 | 10.5% |
| bb_10_20_pctb_lt_25 | 15.3% |
| bb_10_20_reclaim_from_lower_recent_3d | 11.0% |
| bb_10_20_reclaim_from_upper_recent_3d | 10.0% |
| bb_10_20_squeeze | 34.7% |
| bb_10_20_touch_lower | 1.0% |
| bb_10_20_touch_upper | 14.3% |
| bb_20_15_above_mid | 60.2% |
| bb_20_15_expanding | 55.8% |
| bb_20_15_pctb_gt_75 | 44.3% |
| bb_20_15_pctb_gt_8 | 40.4% |
| bb_20_15_pctb_gt_85 | 37.4% |
| bb_20_15_pctb_gt_9 | 35.2% |
| bb_20_15_pctb_gt_95 | 31.1% |
| bb_20_15_pctb_lt_05 | 13.6% |
| bb_20_15_pctb_lt_1 | 16.4% |
| bb_20_15_pctb_lt_15 | 19.2% |
| bb_20_15_pctb_lt_2 | 21.9% |
| bb_20_15_pctb_lt_25 | 25.6% |
| bb_20_15_reclaim_from_lower_recent_3d | 16.2% |
| bb_20_15_reclaim_from_upper_recent_3d | 7.6% |
| bb_20_15_squeeze | 30.9% |
| bb_20_15_touch_lower | 13.5% |
| bb_20_15_touch_upper | 32.6% |
| bb_20_20_above_mid | 60.2% |
| bb_20_20_expanding | 55.8% |
| bb_20_20_pctb_gt_75 | 38.3% |
| bb_20_20_pctb_gt_8 | 35.2% |
| bb_20_20_pctb_gt_85 | 30.1% |
| bb_20_20_pctb_gt_9 | 25.3% |
| bb_20_20_pctb_gt_95 | 19.0% |
| bb_20_20_pctb_lt_05 | 4.6% |
| bb_20_20_pctb_lt_1 | 8.6% |
| bb_20_20_pctb_lt_15 | 12.1% |
| bb_20_20_pctb_lt_2 | 16.4% |
| bb_20_20_pctb_lt_25 | 19.9% |
| bb_20_20_reclaim_from_lower_recent_3d | 12.3% |
| bb_20_20_reclaim_from_upper_recent_3d | 6.6% |
| bb_20_20_squeeze | 15.0% |
| bb_20_20_touch_lower | 4.2% |
| bb_20_20_touch_upper | 18.5% |
| bearish_pin_bar | 5.4% |
| below_avwap_20high | 52.9% |
| below_avwap_20low | 10.6% |
| below_avwap_252low | 4.7% |
| below_avwap_50low | 20.8% |
| below_cam_s3 | 6.8% |
| below_cam_s4 | 2.0% |
| below_cpr | 21.9% |
| below_ema_20 | 37.6% |
| below_ema_20_break_recent_5d | 16.2% |
| below_ema_21 | 37.9% |
| below_ema_21_break_recent_5d | 16.4% |
| below_ema_50 | 34.4% |
| below_ema_50_break_recent_5d | 17.0% |
| below_ema_9 | 36.3% |
| below_ema_9_break_recent_5d | 19.9% |
| below_prev_high | 55.0% |
| below_prev_low | 5.5% |
| below_prev_low_clearance_atr_05 | 1.3% |
| below_s1 | 3.1% |
| below_s2 | 1.2% |
| below_sma_20 | 39.8% |
| below_sma_200 | 11.6% |
| below_sma_21 | 39.7% |
| below_sma_50 | 38.1% |
| below_sma_9 | 37.9% |
| below_vwap | 22.1% |
| break_52w_high | 1.2% |
| break_52w_high_clearance_atr_05 | 0.3% |
| break_52w_high_confirmed_today | 0.3% |
| bullish_engulfing | 8.1% |
| bullish_pin_bar | 5.4% |
| capitulation_recent_3d | 1.9% |
| ceo_buy | 0.8% |
| cfo_buy | 0.3% |
| chandelier_long_bullish | 70.1% |
| chandelier_long_flip_dn | 1.2% |
| chandelier_short_bearish | 48.6% |
| chandelier_short_flip_up | 9.6% |
| close_in_bottom_40pct_of_range | 8.2% |
| close_in_top_40pct_of_range | 73.1% |
| cluster_buy | 0.4% |
| cmf_cross_dn | 2.3% |
| cmf_cross_up | 8.2% |
| cmf_negative | 38.7% |
| cmf_positive | 61.3% |
| concentrated_sell | 7.9% |
| cpr_narrow | 88.0% |
| cpr_narrow_tight | 22.8% |
| cup_handle_detected | 17.2% |
| cup_handle_neckline_break_retest_long | 8.5% |
| dc10_breakout_dn | 3.6% |
| dc10_breakout_dn_1pct | 6.8% |
| dc10_breakout_up | 22.6% |
| dc10_breakout_up_1pct | 30.9% |
| dc10_new_high | 26.4% |
| dc10_strong_breakout_dn | 0.9% |
| dc10_strong_breakout_up | 8.9% |
| dc20_breakout_dn | 2.3% |
| dc20_breakout_up | 17.7% |
| dc20_new_high | 20.4% |
| dc20_resistance_break_retest_strong | 22.4% |
| dc20_support_break_retest_strong | 13.2% |
| defensive_leadership | 54.3% |
| director_only_buy | 2.6% |
| doji | 4.2% |
| double_bottom_detected | 11.4% |
| double_top_detected | 15.3% |
| dpi_elevated | 56.6% |
| drying_volume_on_up_turn | 59.3% |
| ema_20_50_bearish | 36.8% |
| ema_20_50_bullish | 63.2% |
| ema_20_50_death_cross | 1.0% |
| ema_20_50_golden_cross | 2.8% |
| ema_50_200_bearish | 28.4% |
| ema_50_200_bullish | 71.6% |
| ema_50_200_golden_cross | 0.8% |
| ema_9_21_bearish | 43.8% |
| ema_9_21_bullish | 56.2% |
| ema_9_21_death_cross | 1.9% |
| ema_9_21_golden_cross | 4.5% |
| flag_bear_break_retest_short | 0.2% |
| flag_bear_broke | 0.2% |
| flag_bear_detected | 0.1% |
| flag_bull_break_retest_long | 1.1% |
| flag_bull_broke | 1.4% |
| flag_bull_detected | 1.9% |
| force_index_cross_dn | 1.2% |
| force_index_cross_up | 7.9% |
| force_index_positive | 60.3% |
| gap_dn_1_5pct | 10.6% |
| gap_dn_2pct | 7.2% |
| gap_up_1_5pct | 10.2% |
| gap_up_2pct | 7.1% |
| hammer | 4.1% |
| head_shoulders_bottom_detected | 4.6% |
| head_shoulders_top_detected | 4.3% |
| house_cluster_buy | 7.7% |
| house_cluster_sell | 6.9% |
| htf_aligned_bear | 0.9% |
| htf_aligned_bull | 44.7% |
| htf_disagreement | 5.0% |
| hull_bearish | 46.8% |
| hull_bullish | 53.2% |
| hull_flip_dn | 3.2% |
| hull_flip_up | 7.2% |
| ichi_above_cloud | 54.6% |
| ichi_above_cloud_break_recent_5d | 17.1% |
| ichi_below_cloud | 25.9% |
| ichi_below_cloud_break_recent_5d | 7.3% |
| ichi_cloud_thick | 88.3% |
| ichi_tk_bearish | 42.6% |
| ichi_tk_bullish | 51.5% |
| ichi_tk_cross_dn | 2.5% |
| ichi_tk_cross_up | 3.1% |
| ichi_weekly_above_cloud | 57.5% |
| ichi_weekly_below_cloud | 10.3% |
| ichi_weekly_in_cloud | 32.2% |
| in_reversal_window | 4.6% |
| inside_bar | 13.9% |
| inside_cpr | 5.8% |
| inside_kc | 79.2% |
| insider_cluster_active | 21.9% |
| institutional_buy | 82.1% |
| institutional_negative | 8.1% |
| institutional_persistence_growing | 31.0% |
| institutional_persistence_strong | 42.4% |
| institutional_strong_buy | 70.0% |
| inverted_cup_handle_detected | 12.8% |
| is_friday | 19.4% |
| is_halloween_period | 54.5% |
| is_halloween_period_first_day | 0.2% |
| is_january | 9.2% |
| is_january_extended | 10.9% |
| is_monday | 20.9% |
| is_pre_holiday | 3.8% |
| is_summer_period | 45.5% |
| is_totm_window | 35.8% |
| is_totm_window_first_day | 11.4% |
| is_week_open | 23.3% |
| kc_touch_lower | 4.3% |
| kc_touch_upper | 20.6% |
| large_dollar_buy | 0.8% |
| macd_12_26_9_bearish | 51.1% |
| macd_12_26_9_bullish | 48.9% |
| macd_12_26_9_crossover_dn | 2.5% |
| macd_12_26_9_crossover_up | 4.0% |
| macd_8_21_5_bearish | 48.0% |
| macd_8_21_5_bullish | 52.0% |
| macd_8_21_5_crossover_dn | 1.9% |
| macd_8_21_5_crossover_up | 6.4% |
| marubozu_bull | 1.9% |
| mfi_broad_overbought | 18.3% |
| mfi_broad_oversold | 8.8% |
| mfi_overbought | 4.1% |
| mfi_oversold | 1.8% |
| monthly_above_sma_12 | 87.8% |
| monthly_above_sma_6 | 71.2% |
| monthly_bias_bear | 3.8% |
| monthly_bias_bull | 62.8% |
| monthly_momentum_pos | 77.7% |
| morning_star | 9.4% |
| near_52w_high | 3.3% |
| near_52w_high_95pct | 9.9% |
| near_52w_high_retest_long | 4.3% |
| near_avwap_20high_atr_05x | 45.4% |
| near_avwap_20high_atr_10x | 67.7% |
| near_avwap_20high_atr_15x | 83.9% |
| near_avwap_20high_atr_20x | 93.6% |
| near_avwap_20low_atr_05x | 27.0% |
| near_avwap_20low_atr_10x | 47.2% |
| near_avwap_20low_atr_15x | 62.3% |
| near_avwap_20low_atr_20x | 73.5% |
| near_avwap_252low_atr_05x | 6.9% |
| near_avwap_252low_atr_10x | 15.5% |
| near_avwap_252low_atr_15x | 25.1% |
| near_avwap_252low_atr_20x | 34.4% |
| near_avwap_50low_atr_05x | 15.8% |
| near_avwap_50low_atr_10x | 31.2% |
| near_avwap_50low_atr_15x | 47.0% |
| near_avwap_50low_atr_20x | 58.7% |
| near_cam_r3 | 20.8% |
| near_cam_s3 | 6.2% |
| near_cam_s4 | 2.1% |
| near_fib_236 | 4.6% |
| near_fib_382 | 4.9% |
| near_fib_500 | 6.7% |
| near_fib_618 | 4.0% |
| near_fib_786 | 2.8% |
| near_pivot | 13.8% |
| near_prev_close | 15.5% |
| near_prev_high | 16.2% |
| near_prev_low | 4.6% |
| near_r1 | 16.4% |
| near_r1_wide | 64.8% |
| near_r2 | 7.1% |
| near_r2_wide | 41.9% |
| near_s1 | 4.0% |
| near_s1_wide | 26.5% |
| near_s2 | 0.4% |
| near_s2_wide | 7.9% |
| near_s3 | 0.1% |
| near_wood_r1 | 10.2% |
| near_wood_s1 | 7.3% |
| news_uses_polygon_score | 26.5% |
| obv_bearish | 41.4% |
| obv_bullish | 58.6% |
| obv_diverge_bull | 7.4% |
| obv_falling | 41.2% |
| obv_rising | 58.8% |
| outside_bar | 6.6% |
| pead_negative_surprise | 11.4% |
| pead_positive_surprise | 28.6% |
| pin_bar | 10.8% |
| po3_accumulation_active | 26.7% |
| po3_bullish | 20.8% |
| po3_manipulation_sweep_down | 3.5% |
| po3_manipulation_sweep_up | 9.6% |
| po3_mmbm_setup | 2.6% |
| po3_sweep_above_prior_high | 62.5% |
| po3_sweep_below_prior_low | 35.3% |
| ppo_bullish | 48.3% |
| ppo_crossover_dn | 2.3% |
| ppo_crossover_up | 4.1% |
| pre_fomc_d0 | 1.4% |
| pre_fomc_d1 | 2.0% |
| pre_fomc_window | 3.4% |
| price_above_dema | 55.4% |
| price_above_ema_20 | 62.4% |
| price_above_ema_200_break_recent_5d | 40.3% |
| price_above_ema_20_break_recent_5d | 29.2% |
| price_above_ema_21 | 62.1% |
| price_above_ema_21_break_recent_5d | 29.0% |
| price_above_ema_50 | 65.6% |
| price_above_ema_50_break_recent_5d | 28.5% |
| price_above_ema_9 | 63.7% |
| price_above_ema_9_break_recent_5d | 39.3% |
| price_above_hull | 60.6% |
| price_above_sma_200 | 88.4% |
| price_above_sma_21 | 60.3% |
| price_above_sma_50 | 61.9% |
| price_above_tema | 61.0% |
| price_below_dema | 44.6% |
| price_below_hull | 39.4% |
| price_below_tema | 39.0% |
| psar_bullish | 51.3% |
| psar_flip_dn | 2.3% |
| psar_flip_up | 5.2% |
| r1_break_retest_long | 59.9% |
| recent_blowoff_at_r3 | 0.1% |
| resistance_break_retest | 30.8% |
| risk_off_regime_bond_signal | 23.2% |
| risk_off_regime_bond_signal_strong | 9.2% |
| risk_off_regime_gold_signal | 43.3% |
| risk_on_regime_bond_signal | 43.8% |
| risk_on_regime_bond_signal_strong | 20.6% |
| roc_positive | 57.1% |
| roc_turning_dn | 2.5% |
| roc_turning_up | 7.8% |
| rsi_14_bullish | 62.7% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.3% |
| rsi_14_cross_dn_overbought_recent_3d | 3.4% |
| rsi_14_cross_up_oversold_recent_3d | 3.3% |
| rsi_14_extreme_ob | 0.3% |
| rsi_14_overbought | 8.9% |
| rsi_14_oversold | 0.9% |
| rsi_14_rising | 82.6% |
| rsi_21_bullish | 64.5% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.1% |
| rsi_21_cross_dn_overbought_recent_3d | 0.9% |
| rsi_21_cross_up_oversold_recent_3d | 0.2% |
| rsi_21_overbought | 2.3% |
| rsi_21_rising | 82.6% |
| rsi_2_bullish | 71.0% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 17.8% |
| rsi_2_cross_dn_overbought_recent_3d | 18.4% |
| rsi_2_cross_up_extreme_os_recent_3d | 41.1% |
| rsi_2_cross_up_oversold_recent_3d | 47.4% |
| rsi_2_extreme_ob | 41.2% |
| rsi_2_extreme_os | 9.4% |
| rsi_2_overbought | 53.4% |
| rsi_2_oversold | 13.7% |
| rsi_2_rising | 82.6% |
| rsi_9_bullish | 62.9% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 1.5% |
| rsi_9_cross_dn_overbought_recent_3d | 6.6% |
| rsi_9_cross_up_extreme_os_recent_3d | 1.4% |
| rsi_9_cross_up_oversold_recent_3d | 11.1% |
| rsi_9_extreme_ob | 4.9% |
| rsi_9_extreme_os | 0.2% |
| rsi_9_overbought | 18.8% |
| rsi_9_oversold | 5.0% |
| rsi_9_rising | 82.6% |
| s1_break_retest_short | 45.7% |
| sc_13d_filed_within_30d | 2.5% |
| sc_13g_filed_within_30d | 2.1% |
| sector_outperforming_spy | 63.6% |
| sector_underperforming_spy | 36.4% |
| shooting_star | 4.3% |
| sma_20_50_bullish | 55.6% |
| sma_20_50_golden_cross | 1.3% |
| sma_50_200_bullish | 70.0% |
| sma_50_200_golden_cross | 0.4% |
| sma_9_21_bullish | 53.5% |
| sma_9_21_golden_cross | 2.3% |
| smc_bos_bearish | 5.4% |
| smc_bos_bullish | 14.3% |
| smc_bos_retest_long | 5.3% |
| smc_bos_retest_short | 3.8% |
| smc_breaker_block_bearish | 6.5% |
| smc_breaker_block_bullish | 26.3% |
| smc_choch_bearish | 3.9% |
| smc_choch_bullish | 5.6% |
| smc_equal_highs_swept | 4.4% |
| smc_equal_lows_swept | 1.8% |
| smc_fvg_bearish_active | 38.6% |
| smc_fvg_bullish_active | 42.4% |
| smc_fvg_retest_long_zone | 1.8% |
| smc_fvg_retest_short_zone | 13.6% |
| smc_in_discount_zone | 49.6% |
| smc_in_premium_zone | 75.4% |
| smc_inverse_fvg_bearish | 72.6% |
| smc_inverse_fvg_bullish | 92.4% |
| smc_liquidity_swept_dn | 1.3% |
| smc_liquidity_swept_up | 1.0% |
| smc_mitigation_block_long | 0.6% |
| smc_mitigation_block_short | 3.3% |
| smc_ob_bearish_active | 21.2% |
| smc_ob_bullish_active | 40.2% |
| smc_ote_long_zone | 10.2% |
| smc_ote_short_zone | 12.1% |
| squeeze_fire_dn | 0.3% |
| squeeze_fire_up | 5.0% |
| squeeze_in | 21.3% |
| squeeze_positive | 59.7% |
| stoch_bearish_cross | 7.4% |
| stoch_broad_overbought | 32.9% |
| stoch_broad_oversold | 23.2% |
| stoch_bullish_cross | 16.9% |
| stoch_overbought | 28.5% |
| stoch_oversold | 16.9% |
| stochrsi_cross_dn | 16.7% |
| stochrsi_cross_up | 33.8% |
| stochrsi_overbought | 38.0% |
| stochrsi_oversold | 25.6% |
| supertrend_bearish | 1.7% |
| supertrend_bullish | 98.3% |
| supertrend_flip_dn | 0.4% |
| supertrend_flip_recent_long_5d | 1.7% |
| supertrend_flip_recent_short_5d | 2.4% |
| supertrend_flip_up | 0.6% |
| support_break_retest | 18.7% |
| tema_above_dema | 51.1% |
| tema_cross_dn | 1.5% |
| tema_cross_up | 3.3% |
| three_white_soldiers | 11.9% |
| triangle_apex_break_retest_long | 15.8% |
| triangle_ascending_detected | 11.0% |
| triangle_descending_detected | 8.4% |
| uo_overbought | 5.5% |
| uo_oversold | 0.3% |
| usd_strengthening | 23.3% |
| usd_weakening | 11.3% |
| vix_band_high | 38.1% |
| vix_band_low | 39.4% |
| vix_band_mid | 22.5% |
| vix_term_backwardation | 7.1% |
| vix_term_contango | 92.9% |
| vol_above_avg | 40.7% |
| vol_below_avg | 59.3% |
| vol_spike_12x | 25.9% |
| vol_spike_15x | 12.6% |
| vol_spike_17x | 7.9% |
| vol_spike_2x | 5.2% |
| vol_spike_2x_on_down_day_recent_3d | 6.0% |
| vol_spike_2x_on_up_day_recent_3d | 6.2% |
| vol_spike_3x | 1.3% |
| vp_above_value_area | 31.3% |
| vp_below_value_area | 9.6% |
| vp_close_above_poc | 65.0% |
| vp_close_below_poc | 35.0% |
| vp_in_value_area | 59.1% |
| week_open_gap_down_15pct | 3.3% |
| week_open_gap_up_15pct | 1.4% |
| weekly_above_ema_10 | 65.2% |
| weekly_above_ema_20 | 77.9% |
| weekly_bias_bear | 20.1% |
| weekly_bias_bull | 63.2% |
| weekly_momentum_pos | 58.1% |
| williams_r_overbought | 36.9% |
| williams_r_oversold | 11.5% |
| williams_r_rising | 76.6% |
| within_pead_window | 39.0% |
| within_post_inclusion_window | 8.5% |
| xs_avoid_high_ivol | 67.8% |
| xs_avoid_high_max | 66.1% |
| xs_high_beta_decile | 30.3% |
| xs_low_beta_bottom_quintile | 30.3% |
| xs_low_beta_decile | 18.7% |
| xs_low_beta_decile_entry_recent_5d | 1.0% |
| xs_low_beta_top_quintile | 18.7% |
| xs_momentum_bottom_decile | 3.4% |
| xs_momentum_bottom_quintile | 10.4% |
| xs_momentum_top_decile | 23.0% |
| xs_momentum_top_quintile | 35.5% |
| xs_quality_bottom_quintile | 21.4% |
| xs_quality_top_quintile | 22.1% |
| xs_quality_top_tercile | 44.0% |
| year_high_break_retest_long | 1.3% |
| yoy_surprise_high | 57.4% |
| yoy_surprise_negative | 34.4% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 88.3% |
| committed_growth_holders | 88.3% |
| corp_donations_1y | 8.1% |
| corp_donations_count_1y | 8.1% |
| corp_donations_unique_pacs | 8.1% |
| cot_rut_commercials_pctile_3y | 41.6% |
| cot_rut_mmoney_pctile_3y | 41.6% |
| cup_handle_depth_pct | 26.4% |
| days_since_deletion | 5.1% |
| days_since_inclusion | 14.3% |
| days_to_next_holiday | 68.1% |
| days_to_rebalance | 6.6% |
| dpi_30d_avg | 96.8% |
| dpi_recent | 96.8% |
| earnings_announcement_return | 89.4% |
| earnings_eps_yoy_growth | 94.9% |
| flag_bull_pole_move_pct | 1.9% |
| gov_contracts_4q_sum | 44.2% |
| gov_contracts_last_qtr_amount | 44.2% |
| gov_contracts_qoq_growth | 44.2% |
| head_shoulders_magnitude_pct | 8.7% |
| insider_director_buyers_30d | 3.5% |
| insider_officer_buyers_30d | 3.5% |
| insider_total_shares_bought_30d | 3.5% |
| insider_unique_buyers_30d | 3.5% |
| inverted_cup_handle_height_pct | 21.6% |
| lobbying_amount_1y | 77.3% |
| lobbying_amount_q | 77.3% |
| lobbying_amount_yoy | 77.3% |
| monthly_momentum_6m | 93.2% |
| otc_short_ratio_recent | 96.8% |
| otc_volume_recent | 96.8% |
| pair_half_life | 93.3% |
| pair_max_abs_zscore | 93.3% |
| pair_zscore_signed | 93.3% |
| pct_from_avwap_20high | 79.0% |
| pct_from_avwap_20low | 90.1% |
| pct_from_avwap_252low | 94.7% |
| pct_from_avwap_50low | 96.7% |
| persistent_holders_4q | 88.3% |
| persistent_holders_8q | 88.3% |
| sc_13g_latest_percent_owned | 1.0% |
| search_volume_index_recent | 78.8% |
| search_volume_observations | 78.8% |
| search_volume_zscore_30d | 78.8% |
| sector_etf_return_20d | 1.2% |
| spy_return_20d | 1.2% |
| total_active_holders | 88.3% |
| triangle_breakdown_pct | 8.4% |
| triangle_breakout_pct | 11.0% |
| xs_quality_decile | 64.0% |
| xs_quality_gross_profitability | 64.0% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.999), `avwap_252low` (0.991), `avwap_50low` (0.999), `bb_10_20_lower` (0.998), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.998), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.998), `cam_r2` (0.998), `cam_r3` (0.998), `cam_r4` (0.998), `cam_s1` (0.998), `cam_s2` (0.998), `cam_s3` (0.998), `cam_s4` (0.997), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.998), `cpr_top` (0.998), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.998), `dc10_lower` (0.999), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.997), `double_bottom_trough` (0.998), `double_top_neckline` (0.998), `double_top_peak` (0.998), `entry_stop_long` (0.997), `entry_stop_short` (0.997), `fib_236` (0.998), `fib_382` (0.998), `fib_500` (0.998), `fib_618` (0.998), `fib_786` (0.997), `fib_ext_127` (0.996), `fib_ext_162` (0.993), `flag_bull_breakout_level` (0.998), `head_shoulders_bottom_neckline` (0.997), `head_shoulders_top_neckline` (0.999), `hull_ma` (0.998), `ichi_kijun` (1.0), `ichi_senkou_a` (0.995), `ichi_senkou_b` (0.993), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.999), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (0.999), `monthly_close` (0.998), `monthly_sma_12` (0.989), `monthly_sma_6` (0.996), `pivot` (0.998), `prev_close` (0.998), `prev_high` (0.998), `prev_low` (0.998), `psar_value` (0.998), `r1` (0.998), `r2` (0.998), `r3` (0.998), `s1` (0.998), `s2` (0.997), `s3` (0.996), `supertrend_value` (0.996), `swing_high` (0.997), `swing_low` (0.995), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.998), `vp_value_area_low` (0.995), `vwap_upper_2` (0.955), `weekly_close` (0.997), `weekly_ema_10` (0.999), `weekly_ema_20` (0.998), `wood_p` (0.998), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.998), `wood_s2` (0.998), `year_high` (0.992)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | ema span (the 200 in above/below_ema_200 | 3 | **FIRE-ADDING** | **YES** |
| P2 | news_article_count >= 3 | 5 | subset-safe | no - derives offline |
| P3 | news_sentiment_mean > 0.3 | 5 | subset-safe | no - derives offline |

```
FULL FACTORIAL     3 x 5 x 5 = 75
offline gradings   25 level-combinations x 24 exits = 600
ENGINE RUNS        3 (every fire-adding axis sits at production-only until its env actuator exists)
check              3 x 25 = 75
```

B-row candidates NOT in this factorial: 625 census axes join it only when REGISTERED at the T3 band review.
