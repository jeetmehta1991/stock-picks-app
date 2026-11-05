# Table A - macd_bullish_with_smart_money_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 55a39e45e | commit 55a39e45e at 2026-11-05 11:55:00 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** NONE | **family:** smart_money_sleeve | **status:** NOT-STARTED | **R5 fires:** 1162 (closed fires in the exit cube: 1162 of 1162, S6-B3258) | **surviving fires (T1):** 1162 (unchanged since R5 - filter is identity)

**SPECS entry:** registered in producer_variant_table

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  macd_12_26_9_bullish  <- backtest/signals/technical.py (f-string template)
       DEFN: MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648)
       knobs P1.1-P1.1 (band rows in Table A)
P2  price_above_ema_200  <- backtest/signals/technical.py (f-string template) +1
       DEFN: close vs the named SMA/EMA span (compute_ema_sma family)
       knobs P2.1-P2.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  _has_smart_money_buy(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_macd_bullish_with_smart_money_long (docstring and return dropped):

```python
base_fires = s.get('macd_12_26_9_bullish', False) and s.get('price_above_ema_200', False)
fires = base_fires and _has_smart_money_buy(s)
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
| P1 | PRODUCER | macd_12_26_9_bullish - emitted by backtest/signals/technical.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P1.1 | BAND | span triple (mirror of the bearish entry) - backtest/signals/technical.py:634-648 | MEASURED availability (both persisted) | (12,26,9) | [(8,21,5), (12,26,9)] both computed; others new | offline 0 of 2 levels - none - the (8,21,5) swap changes which bars fire; the persisted keys re-grade only fires the (12,26,9) cube holds (mirror of the bearish row) | any third triple; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | price_above_ema_200 - emitted by backtest/signals/technical.py (f-string template) +1; the boolean's UNDERLYING condition is bandable through its producer's internals | close vs the named SMA/EMA span (compute_ema_sma family) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs in the SPECS entry | SPECS-REGISTERED |
| P2.1 | BAND | ema span (the 200 in above/below_ema_200) - producer_variant_table.SPECS['bollinger_lower'] P3/P4; backtest/signals/technical.py compute_ema_sma | SPECS bollinger_lower P3/P4 (T3/Q2-APPROVED 2026-09-27): production 200 + resim spans [9, 20, 21, 50, 100, 150, 250] | 200 | 9, 20, 21, 50, 100, 150, 200, 250 | offline 0 of 8 levels - canon-span FLAGS (above/below ema 9/20/21/50/200) ARE persisted - measured 200-of-200 bollinger fires, S6-B3117b; offline as ADD-A-CONDITION legs only. The SWAP of the gate span, and non-canon spans, are RESIM | the whole band except production (resim_band [9, 20, 21, 50, 100, 150, 250]); env STRAT_EMA_SPAN does not reach this gate - it reads the literal key - DEFINED-NO-ACTUATOR here (S6-B3253) | T3 review before any grid |
| P3 | STRATEGY-HELPER | _has_smart_money_buy(s) - underlying condition: insider_cluster_active OR cfo_buy OR large_dollar_buy OR institutional_strong_buy OR institutional_buy | requires one smart-money buy flag on the fire bar | any of 5 | - (no band ruled) | offline 0 of 1 levels (no band ruled) - tighter = a NARROWER union of the persisted flags (an EVENT-only subset, say) - OFFLINE subset | a wider union admits fires the engine never recorded - RESIM; a helper shared by the smart-money sleeves, so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (runbook section 3.6; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (module writing the key) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (module writing the key) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/technical.py | 100.0% | 16.364, 19.774, 23.056, 28.152 | 16.364: 929 (80%); 19.774: 697 (60%); 23.056: 465 (40%); 28.152: 233 (20%) | 16.364: 233 (20%); 19.774: 465 (40%); 23.056: 697 (60%); 28.152: 929 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 14.4, 17.78, 20.452, 23.646 | 14.4: 929 (80%); 17.78: 699 (60%); 20.452: 465 (40%); 23.646: 233 (20%) | 14.4: 233 (20%); 17.78: 466 (40%); 20.452: 697 (60%); 23.646: 929 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 23.186, 27.002, 30.572, 34.918 | 23.186: 929 (80%); 27.002: 697 (60%); 30.572: 465 (40%); 34.918: 233 (20%) | 23.186: 233 (20%); 27.002: 465 (40%); 30.572: 697 (60%); 34.918: 929 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -1.4434, 0.7623, 2.6124, 6.4526 | -1.4434: 929 (80%); 0.7623: 697 (60%); 2.6124: 465 (40%); 6.4526: 233 (20%) | -1.4434: 233 (20%); 0.7623: 465 (40%); 2.6124: 697 (60%); 6.4526: 929 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.2689, 2.0737, 3.4276, 6.1852 | 1.2689: 930 (80%); 2.0737: 697 (60%); 3.4276: 465 (40%); 6.1852: 233 (20%) | 1.2689: 233 (20%); 2.0737: 465 (40%); 3.4276: 697 (60%); 6.1852: 929 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.2689, 2.0737, 3.4276, 6.1852 | 1.2689: 930 (80%); 2.0737: 697 (60%); 3.4276: 465 (40%); 6.1852: 233 (20%) | 1.2689: 233 (20%); 2.0737: 465 (40%); 3.4276: 697 (60%); 6.1852: 929 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.9954, 2.389, 2.8584, 3.6274 | 1.9954: 929 (80%); 2.389: 698 (60%); 2.8584: 465 (40%); 3.6274: 233 (20%) | 1.9954: 233 (20%); 2.389: 466 (40%); 2.8584: 697 (60%); 3.6274: 929 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0617, 0.0876, 0.1187, 0.1654 | 0.0617: 929 (80%); 0.0876: 698 (60%); 0.1187: 465 (40%); 0.1654: 233 (20%) | 0.0617: 233 (20%); 0.0876: 465 (40%); 0.1187: 697 (60%); 0.1654: 930 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.6853, 0.8059, 0.8866, 0.9668 | 0.6853: 930 (80%); 0.8059: 697 (60%); 0.8866: 465 (40%); 0.9668: 233 (20%) | 0.6853: 234 (20%); 0.8059: 465 (40%); 0.8866: 698 (60%); 0.9668: 931 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0673, 0.092, 0.1173, 0.1481 | 0.0673: 930 (80%); 0.092: 697 (60%); 0.1173: 465 (40%); 0.1481: 233 (20%) | 0.0673: 233 (20%); 0.092: 465 (40%); 0.1173: 697 (60%); 0.1481: 930 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.7449, 0.9226, 1.0587, 1.2016 | 0.7449: 930 (80%); 0.9226: 697 (60%); 1.0587: 465 (40%); 1.2016: 233 (20%) | 0.7449: 233 (20%); 0.9226: 465 (40%); 1.0587: 697 (60%); 1.2016: 930 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0898, 0.1226, 0.1564, 0.1975 | 0.0898: 929 (80%); 0.1226: 697 (60%); 0.1564: 465 (40%); 0.1975: 233 (20%) | 0.0898: 233 (20%); 0.1226: 465 (40%); 0.1564: 697 (60%); 0.1975: 930 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.6837, 0.8169, 0.9191, 1.0262 | 0.6837: 930 (80%); 0.8169: 698 (60%); 0.9191: 465 (40%); 1.0262: 233 (20%) | 0.6837: 233 (20%); 0.8169: 465 (40%); 0.9191: 697 (60%); 1.0262: 930 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0548, -0.0231, -0.0056, 0.0231 | -0.0548: 932 (80%); -0.0231: 697 (60%); -0.0056: 467 (40%); 0.0231: 233 (20%) | -0.0548: 234 (20%); -0.0231: 465 (40%); -0.0056: 700 (60%); 0.0231: 929 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1435, 0.164, 0.2035, 0.258 | 0.1435: 928 (80%); 0.164: 700 (60%); 0.2035: 465 (40%); 0.258: 234 (20%) | 0.1435: 234 (20%); 0.164: 462 (40%); 0.2035: 697 (60%); 0.258: 928 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 1162 (100%) | 0: 1097 (94%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.0298, 0.0419, 0.1072, 0.1771 | -0.0298: 930 (80%); 0.0419: 697 (60%); 0.1072: 465 (40%); 0.1771: 233 (20%) | -0.0298: 233 (20%); 0.0419: 465 (40%); 0.1072: 697 (60%); 0.1771: 930 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 1162 (100%); 1: 432 (37%) | 0: 730 (63%); 1: 994 (86%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.242, -0.1931, -0.1542, -0.1285 | -0.242: 931 (80%); -0.1931: 698 (60%); -0.1542: 467 (40%); -0.1285: 244 (21%) | -0.242: 235 (20%); -0.1931: 472 (41%); -0.1542: 700 (60%); -0.1285: 949 (82%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3846, 0.5962, 0.6731, 0.7692 | 0.3846: 932 (80%); 0.5962: 698 (60%); 0.6731: 501 (43%); 0.7692: 254 (22%) | 0.3846: 234 (20%); 0.5962: 472 (41%); 0.6731: 704 (61%); 0.7692: 930 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2628, 0.4167, 0.6474, 0.8333 | 0.2628: 963 (83%); 0.4167: 705 (61%); 0.6474: 473 (41%); 0.8333: 259 (22%) | 0.2628: 244 (21%); 0.4167: 470 (40%); 0.6474: 700 (60%); 0.8333: 932 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0919, -0.0081, 0.0961, 0.254 | -0.0919: 929 (80%); -0.0081: 700 (60%); 0.0961: 466 (40%); 0.254: 236 (20%) | -0.0919: 233 (20%); -0.0081: 467 (40%); 0.0961: 702 (60%); 0.254: 936 (81%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2692, 0.4551, 0.6538, 0.8462 | 0.2692: 934 (80%); 0.4551: 726 (62%); 0.6538: 468 (40%); 0.8462: 246 (21%) | 0.2692: 236 (20%); 0.4551: 476 (41%); 0.6538: 702 (60%); 0.8462: 930 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0962, 0.2436, 0.3974, 0.6026 | 0.0962: 934 (80%); 0.2436: 721 (62%); 0.3974: 468 (40%); 0.6026: 237 (20%) | 0.0962: 236 (20%); 0.2436: 467 (40%); 0.3974: 700 (60%); 0.6026: 944 (81%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.5212, -0.3786, -0.1925, 0.0648 | -0.5212: 930 (80%); -0.3786: 698 (60%); -0.1925: 467 (40%); 0.0648: 238 (20%) | -0.5212: 238 (20%); -0.3786: 467 (40%); -0.1925: 703 (60%); 0.0648: 938 (81%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3013, 0.4872, 0.7051, 0.9167 | 0.3013: 944 (81%); 0.4872: 701 (60%); 0.7051: 466 (40%); 0.9167: 307 (26%) | 0.3013: 243 (21%); 0.4872: 473 (41%); 0.7051: 701 (60%); 0.9167: 942 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1795, 0.4295, 0.5962, 0.8974 | 0.1795: 936 (81%); 0.4295: 701 (60%); 0.5962: 476 (41%); 0.8974: 246 (21%) | 0.1795: 246 (21%); 0.4295: 479 (41%); 0.5962: 698 (60%); 0.8974: 932 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0668, -0.0593, -0.0399, 0 | -0.0668: 950 (82%); -0.0593: 702 (60%); -0.0399: 466 (40%); 0: 344 (30%) | -0.0668: 236 (20%); -0.0593: 474 (41%); -0.0399: 715 (62%); 0: 1119 (96%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.391, 0.6859, 0.8846, 1 | 0.391: 931 (80%); 0.6859: 698 (60%); 0.8846: 480 (41%); 1: 265 (23%) | 0.391: 240 (21%); 0.6859: 469 (40%); 0.8846: 702 (60%); 1: 1162 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1282, 0.2244, 0.5936, 0.9231 | 0.1282: 942 (81%); 0.2244: 698 (60%); 0.5936: 465 (40%); 0.9231: 234 (20%) | 0.1282: 234 (20%); 0.2244: 467 (40%); 0.5936: 697 (60%); 0.9231: 948 (82%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0289, 0.0292, 0.1005, 0.2309 | -0.0289: 941 (81%); 0.0292: 707 (61%); 0.1005: 468 (40%); 0.2309: 254 (22%) | -0.0289: 240 (21%); 0.0292: 467 (40%); 0.1005: 700 (60%); 0.2309: 939 (81%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3846, 0.7782, 0.9351, 0.9744 | 0.3846: 931 (80%); 0.7782: 697 (60%); 0.9351: 471 (41%); 0.9744: 258 (22%) | 0.3846: 238 (20%); 0.7782: 465 (40%); 0.9351: 714 (61%); 0.9744: 967 (83%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0954, 0.3077, 0.6154, 0.8269 | 0.0954: 929 (80%); 0.3077: 699 (60%); 0.6154: 466 (40%); 0.8269: 234 (20%) | 0.0954: 233 (20%); 0.3077: 466 (40%); 0.6154: 704 (61%); 0.8269: 933 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0812, -0.0203, 0.0787, 0.167 | -0.0812: 982 (85%); -0.0203: 735 (63%); 0.0787: 468 (40%); 0.167: 236 (20%) | -0.0812: 320 (28%); -0.0203: 470 (40%); 0.0787: 701 (60%); 0.167: 934 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.186, -0.0392, 0.0345, 0.0916 | -0.186: 936 (81%); -0.0392: 698 (60%); 0.0345: 467 (40%); 0.0916: 240 (21%) | -0.186: 237 (20%); -0.0392: 467 (40%); 0.0345: 704 (61%); 0.0916: 941 (81%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2398, 0.5321, 0.7179, 0.8782 | 0.2398: 929 (80%); 0.5321: 704 (61%); 0.7179: 481 (41%); 0.8782: 236 (20%) | 0.2398: 233 (20%); 0.5321: 480 (41%); 0.7179: 698 (60%); 0.8782: 967 (83%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1795, 0.4167, 0.6667, 0.8269 | 0.1795: 944 (81%); 0.4167: 699 (60%); 0.6667: 473 (41%); 0.8269: 237 (20%) | 0.1795: 238 (20%); 0.4167: 474 (41%); 0.6667: 700 (60%); 0.8269: 942 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0617, 0.1437, 0.2755, 0.6054 | 0.0617: 931 (80%); 0.1437: 697 (60%); 0.2755: 465 (40%); 0.6054: 233 (20%) | 0.0617: 236 (20%); 0.1437: 465 (40%); 0.2755: 697 (60%); 0.6054: 929 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +1 | 99.3% | 20, 61, 78, 130.4 | 20: 925 (80%); 61: 698 (60%); 78: 476 (41%); 130.4: 231 (20%) | 20: 241 (21%); 61: 481 (41%); 78: 696 (60%); 130.4: 923 (79%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 100.0% | 1.7093, 2.2695, 2.8585, 3.9218 | 1.7093: 929 (80%); 2.2695: 698 (60%); 2.8585: 465 (40%); 3.9218: 233 (20%) | 1.7093: 233 (20%); 2.2695: 465 (40%); 2.8585: 697 (60%); 3.9218: 929 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 9, 19, 28, 35.8 | 9: 954 (82%); 19: 731 (63%); 28: 478 (41%); 35.8: 233 (20%) | 9: 242 (21%); 19: 466 (40%); 28: 745 (64%); 35.8: 929 (80%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 0, 1, 2, 3 | 0: 1162 (100%); 1: 925 (80%); 2: 694 (60%); 3: 456 (39%) | 0: 237 (20%); 1: 468 (40%); 2: 706 (61%); 3: 937 (81%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0184, -0.0095, 0, 0.0172 | -0.0184: 930 (80%); -0.0095: 704 (61%); 0: 470 (40%); 0.0172: 233 (20%) | -0.0184: 241 (21%); -0.0095: 474 (41%); 0: 700 (60%); 0.0172: 930 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5181, 25.6247, 26.4855, 27.1237 | 24.5181: 930 (80%); 25.6247: 697 (60%); 26.4855: 467 (40%); 27.1237: 236 (20%) | 24.5181: 238 (20%); 25.6247: 465 (40%); 26.4855: 707 (61%); 27.1237: 935 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -0.8398, -0.225, 0.0962, 0.58 | -0.8398: 929 (80%); -0.225: 698 (60%); 0.0962: 465 (40%); 0.58: 233 (20%) | -0.8398: 233 (20%); -0.225: 467 (40%); 0.0962: 697 (60%); 0.58: 929 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -0.58, -0.0962, 0.225, 0.8398 | -0.58: 929 (80%); -0.0962: 697 (60%); 0.225: 467 (40%); 0.8398: 233 (20%) | -0.58: 233 (20%); -0.0962: 465 (40%); 0.225: 698 (60%); 0.8398: 929 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0467, -0.0116, 0.0161, 0.0587 | -0.0467: 929 (80%); -0.0116: 700 (60%); 0.0161: 465 (40%); 0.0587: 233 (20%) | -0.0467: 233 (20%); -0.0116: 466 (40%); 0.0161: 697 (60%); 0.0587: 929 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0861, 8.4646, 8.6817, 9.0585 | 8.0861: 929 (80%); 8.4646: 702 (60%); 8.6817: 465 (40%); 9.0585: 235 (20%) | 8.0861: 233 (20%); 8.4646: 460 (40%); 8.6817: 697 (60%); 9.0585: 927 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.7% | 0, 1 | 0: 1159 (100%); 1: 356 (31%) | 0: 803 (69%); 1: 1039 (89%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.7% | -1, 0 | -1: 1087 (94%); 0: 922 (79%) | -1: 237 (20%); 0: 971 (84%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.7% | 0, 1 | 0: 1159 (100%); 1: 382 (33%) | 0: 777 (67%); 1: 1015 (87%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 3, 6, 100, 278.8 | 3: 993 (85%); 6: 734 (63%); 100: 466 (40%); 278.8: 233 (20%) | 3: 260 (22%); 6: 490 (42%); 100: 699 (60%); 278.8: 929 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 2, 5, 83.6, 146.8 | 2: 946 (81%); 5: 715 (62%); 83.6: 465 (40%); 146.8: 233 (20%) | 2: 312 (27%); 5: 470 (40%); 83.6: 697 (60%); 146.8: 929 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | 0.1884, 0.3836, 0.753, 1.465 | 0.1884: 929 (80%); 0.3836: 697 (60%); 0.753: 465 (40%); 1.465: 233 (20%) | 0.1884: 233 (20%); 0.3836: 465 (40%); 0.753: 697 (60%); 1.465: 929 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -0.6083, 0.1442, 0.7942, 2.1482 | -0.6083: 929 (80%); 0.1442: 697 (60%); 0.7942: 465 (40%); 2.1482: 233 (20%) | -0.6083: 233 (20%); 0.1442: 465 (40%); 0.7942: 697 (60%); 2.1482: 929 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -1.5377, -0.4047, 0.1993, 1.0988 | -1.5377: 929 (80%); -0.4047: 697 (60%); 0.1993: 465 (40%); 1.0988: 233 (20%) | -1.5377: 233 (20%); -0.4047: 465 (40%); 0.1993: 697 (60%); 1.0988: 929 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | 0.0875, 0.298, 0.6276, 1.3651 | 0.0875: 929 (80%); 0.298: 697 (60%); 0.6276: 465 (40%); 1.3651: 233 (20%) | 0.0875: 233 (20%); 0.298: 465 (40%); 0.6276: 697 (60%); 1.3651: 929 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -0.0833, 0.616, 1.363, 3.1845 | -0.0833: 929 (80%); 0.616: 697 (60%); 1.363: 465 (40%); 3.1845: 233 (20%) | -0.0833: 233 (20%); 0.616: 465 (40%); 1.363: 697 (60%); 3.1845: 929 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -0.8263, 0.1615, 0.8923, 2.3074 | -0.8263: 929 (80%); 0.1615: 697 (60%); 0.8923: 465 (40%); 2.3074: 233 (20%) | -0.8263: 233 (20%); 0.1615: 465 (40%); 0.8923: 697 (60%); 2.3074: 929 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 51.114, 59.056, 65.958, 72.386 | 51.114: 929 (80%); 59.056: 697 (60%); 65.958: 465 (40%); 72.386: 233 (20%) | 51.114: 233 (20%); 59.056: 465 (40%); 65.958: 697 (60%); 72.386: 929 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.4% | 0.0049, 0.0116, 0.0202, 0.0364 | 0.0049: 923 (79%); 0.0116: 692 (60%); 0.0202: 462 (40%); 0.0364: 232 (20%) | 0.0049: 232 (20%); 0.0116: 463 (40%); 0.0202: 693 (60%); 0.0364: 923 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 9 | 0: 1162 (100%); 2: 719 (62%); 4: 497 (43%); 9: 254 (22%) | 0: 257 (22%); 2: 587 (51%); 4: 744 (64%); 9: 935 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1 | 0: 1162 (100%); 0.1: 240 (21%) | 0: 844 (73%); 0.1: 938 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.25, 0.5, 0.75 | 0: 1162 (100%); 0.25: 706 (61%); 0.5: 495 (43%); 0.75: 234 (20%) | 0: 410 (35%); 0.25: 487 (42%); 0.5: 787 (68%); 0.75: 947 (81%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 1162 (100%); 1: 837 (72%); 3: 478 (41%); 7: 235 (20%) | 0: 325 (28%); 1: 554 (48%); 3: 760 (65%); 7: 961 (83%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 9 | 0: 1162 (100%); 2: 719 (62%); 4: 497 (43%); 9: 254 (22%) | 0: 257 (22%); 2: 587 (51%); 4: 744 (64%); 9: 935 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 1162 (100%); 1: 834 (72%); 3: 538 (46%); 7: 255 (22%) | 0: 328 (28%); 1: 506 (44%); 3: 714 (61%); 7: 933 (80%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.0769, 0.2774, 0.4074, 0.611 | 0.0769: 930 (80%); 0.2774: 697 (60%); 0.4074: 466 (40%); 0.611: 233 (20%) | 0.0769: 234 (20%); 0.2774: 465 (40%); 0.4074: 698 (60%); 0.611: 929 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2919, 0.6979 | 0: 1100 (95%); 0.2919: 465 (40%); 0.6979: 233 (20%) | 0: 575 (49%); 0.2919: 697 (60%); 0.6979: 929 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0629, 0.3778, 0.6667 | 0: 1102 (95%); 0.0629: 697 (60%); 0.3778: 466 (40%); 0.6667: 247 (21%) | 0: 458 (39%); 0.0629: 465 (40%); 0.3778: 699 (60%); 0.6667: 943 (81%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0629, 0.3778, 0.6667 | 0: 1102 (95%); 0.0629: 697 (60%); 0.3778: 466 (40%); 0.6667: 247 (21%) | 0: 458 (39%); 0.0629: 465 (40%); 0.3778: 699 (60%); 0.6667: 943 (81%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.155, 0, 0.1667 | -0.155: 929 (80%); 0: 840 (72%); 0.1667: 247 (21%) | -0.155: 233 (20%); 0: 823 (71%); 0.1667: 930 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.7452, -0.2417, 0.1929, 1.7889 | -0.7452: 929 (80%); -0.2417: 697 (60%); 0.1929: 465 (40%); 1.7889: 236 (20%) | -0.7452: 233 (20%); -0.2417: 465 (40%); 0.1929: 697 (60%); 1.7889: 957 (82%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 5, 8, 13 | 2: 998 (86%); 5: 722 (62%); 8: 483 (42%); 13: 250 (22%) | 2: 255 (22%); 5: 540 (46%); 8: 753 (65%); 13: 953 (82%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | 0.0221, 0.0454, 0.0714, 0.1082 | 0.0221: 929 (80%); 0.0454: 697 (60%); 0.0714: 465 (40%); 0.1082: 233 (20%) | 0.0221: 233 (20%); 0.0454: 465 (40%); 0.0714: 697 (60%); 0.1082: 930 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0001, 0.0402, 0.0785, 0.1189 | -0.0001: 929 (80%); 0.0402: 697 (60%); 0.0785: 465 (40%); 0.1189: 233 (20%) | -0.0001: 233 (20%); 0.0402: 465 (40%); 0.0785: 697 (60%); 0.1189: 929 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | 0.0101, 0.0301, 0.0523, 0.0845 | 0.0101: 928 (80%); 0.0301: 698 (60%); 0.0523: 465 (40%); 0.0845: 234 (20%) | 0.0101: 234 (20%); 0.0301: 464 (40%); 0.0523: 697 (60%); 0.0845: 928 (80%) | OFFLINE |
| pct_from_avwap_20low | backtest/signals/technical.py (f-string template) | 99.7% | 2.516, 4.0244, 5.4912, 7.9818 | 2.516: 926 (80%); 4.0244: 695 (60%); 5.4912: 463 (40%); 7.9818: 232 (20%) | 2.516: 232 (20%); 4.0244: 463 (40%); 5.4912: 695 (60%); 7.9818: 926 (80%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/technical.py (f-string template) | 99.7% | 3.0034, 4.8576, 6.8414, 9.747 | 3.0034: 926 (80%); 4.8576: 695 (60%); 6.8414: 463 (40%); 9.747: 232 (20%) | 3.0034: 232 (20%); 4.8576: 463 (40%); 6.8414: 695 (60%); 9.747: 926 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -3.5242, 5.1128, 12.5926, 29.1804 | -3.5242: 929 (80%); 5.1128: 697 (60%); 12.5926: 465 (40%); 29.1804: 233 (20%) | -3.5242: 233 (20%); 5.1128: 465 (40%); 12.5926: 697 (60%); 29.1804: 929 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py | 100.0% | 0.0412, 0.0562, 0.0741, 0.1013 | 0.0412: 931 (80%); 0.0562: 697 (60%); 0.0741: 467 (40%); 0.1013: 233 (20%) | 0.0412: 234 (20%); 0.0562: 465 (40%); 0.0741: 698 (60%); 0.1013: 931 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.5179, 0.6966, 0.8068, 0.9091 | 0.5179: 929 (80%); 0.6966: 697 (60%); 0.8068: 465 (40%); 0.9091: 233 (20%) | 0.5179: 233 (20%); 0.6966: 465 (40%); 0.8068: 697 (60%); 0.9091: 931 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -0.6811, 0.2303, 1.0544, 2.0378 | -0.6811: 929 (80%); 0.2303: 697 (60%); 1.0544: 465 (40%); 2.0378: 233 (20%) | -0.6811: 233 (20%); 0.2303: 465 (40%); 1.0544: 697 (60%); 2.0378: 929 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | 0.2465, 0.4857, 0.7579, 1.1485 | 0.2465: 929 (80%); 0.4857: 697 (60%); 0.7579: 465 (40%); 1.1485: 233 (20%) | 0.2465: 233 (20%); 0.4857: 465 (40%); 0.7579: 697 (60%); 1.1485: 929 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -1.4175, -0.527, 0.2676, 1.3529 | -1.4175: 929 (80%); -0.527: 697 (60%); 0.2676: 465 (40%); 1.3529: 233 (20%) | -1.4175: 233 (20%); -0.527: 465 (40%); 0.2676: 698 (60%); 1.3529: 929 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | 2.189, 4.9538, 7.4076, 11.0952 | 2.189: 929 (80%); 4.9538: 697 (60%); 7.4076: 465 (40%); 11.0952: 233 (20%) | 2.189: 233 (20%); 4.9538: 465 (40%); 7.4076: 697 (60%); 11.0952: 929 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 53.474, 58.234, 62.502, 67.616 | 53.474: 929 (80%); 58.234: 697 (60%); 62.502: 465 (40%); 67.616: 233 (20%) | 53.474: 233 (20%); 58.234: 465 (40%); 62.502: 697 (60%); 67.616: 929 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 64.386, 83.884, 92.56, 97.276 | 64.386: 929 (80%); 83.884: 697 (60%); 92.56: 466 (40%); 97.276: 233 (20%) | 64.386: 233 (20%); 83.884: 465 (40%); 92.56: 698 (60%); 97.276: 929 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 51.36, 55.054, 58.322, 62.326 | 51.36: 930 (80%); 55.054: 697 (60%); 58.322: 465 (40%); 62.326: 233 (20%) | 51.36: 234 (20%); 55.054: 465 (40%); 58.322: 697 (60%); 62.326: 929 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 57.104, 63, 68.326, 73.752 | 57.104: 929 (80%); 63: 698 (60%); 68.326: 465 (40%); 73.752: 233 (20%) | 57.104: 233 (20%); 63: 466 (40%); 68.326: 697 (60%); 73.752: 929 (80%) | OFFLINE |
| sector_etf_return_pct | (no module found writing the key) | 100.0% | 0 | 0: 1161 (100%) | 0: 1162 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0317, 0.0448, 0.0589, 0.0836 | 0.0317: 934 (80%); 0.0448: 700 (60%); 0.0589: 468 (40%); 0.0836: 234 (20%) | 0.0317: 236 (20%); 0.0448: 466 (40%); 0.0589: 700 (60%); 0.0836: 932 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0886, -0.0633, -0.0479, -0.0351 | -0.0886: 929 (80%); -0.0633: 703 (60%); -0.0479: 465 (40%); -0.0351: 233 (20%) | -0.0886: 233 (20%); -0.0633: 467 (40%); -0.0479: 702 (60%); -0.0351: 929 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 1162 (100%); 2: 244 (21%) | 0: 799 (69%); 2: 986 (85%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 100.0% | 27, 42, 57, 68 | 27: 933 (80%); 42: 715 (62%); 57: 468 (40%); 68: 242 (21%) | 27: 237 (20%); 42: 472 (41%); 57: 710 (61%); 68: 942 (81%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 98.6% | 0.0114, 0.0163, 0.0242, 0.0379 | 0.0114: 915 (79%); 0.0163: 686 (59%); 0.0242: 459 (40%); 0.0379: 230 (20%) | 0.0114: 231 (20%); 0.0163: 460 (40%); 0.0242: 687 (59%); 0.0379: 916 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 100.0% | 0.4504, 0.6273, 0.7945, 0.9237 | 0.4504: 929 (80%); 0.6273: 698 (60%); 0.7945: 465 (40%); 0.9237: 233 (20%) | 0.4504: 233 (20%); 0.6273: 465 (40%); 0.7945: 697 (60%); 0.9237: 929 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 100.0% | 39.22, 54.04, 68.02, 95.06 | 39.22: 929 (80%); 54.04: 697 (60%); 68.02: 465 (40%); 95.06: 233 (20%) | 39.22: 233 (20%); 54.04: 465 (40%); 68.02: 697 (60%); 95.06: 929 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | 1.1976, 2.7976, 5.426, 10.573 | 1.1976: 929 (80%); 2.7976: 697 (60%); 5.426: 465 (40%); 10.573: 233 (20%) | 1.1976: 233 (20%); 2.7976: 465 (40%); 5.426: 697 (60%); 10.573: 929 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 59.428, 72.802, 82.898, 89.012 | 59.428: 929 (80%); 72.802: 697 (60%); 82.898: 465 (40%); 89.012: 233 (20%) | 59.428: 233 (20%); 72.802: 465 (40%); 82.898: 697 (60%); 89.012: 929 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 66.042, 77.836, 85.96, 91.81 | 66.042: 929 (80%); 77.836: 697 (60%); 85.96: 465 (40%); 91.81: 234 (20%) | 66.042: 233 (20%); 77.836: 465 (40%); 85.96: 697 (60%); 91.81: 930 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 55.428, 79.784, 92.19, 98.566 | 55.428: 929 (80%); 79.784: 697 (60%); 92.19: 465 (40%); 98.566: 233 (20%) | 55.428: 233 (20%); 79.784: 465 (40%); 92.19: 697 (60%); 98.566: 929 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 60.278, 87.092, 100 | 60.278: 929 (80%); 87.092: 697 (60%); 100: 511 (44%) | 60.278: 233 (20%); 87.092: 465 (40%); 100: 1162 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 8, 13, 18 | 4: 952 (82%); 8: 726 (62%); 13: 466 (40%); 18: 235 (20%) | 4: 259 (22%); 8: 477 (41%); 13: 750 (65%); 18: 1000 (86%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 4, 9, 14, 18 | 4: 987 (85%); 9: 731 (63%); 14: 468 (40%); 18: 260 (22%) | 4: 234 (20%); 9: 485 (42%); 14: 737 (63%); 18: 962 (83%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 53.142, 57.516, 61.39, 65.494 | 53.142: 929 (80%); 57.516: 697 (60%); 61.39: 465 (40%); 65.494: 233 (20%) | 53.142: 233 (20%); 57.516: 465 (40%); 61.39: 697 (60%); 65.494: 929 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.0913, 0.3532, 0.619, 0.8056 | 0.0913: 935 (80%); 0.3532: 698 (60%); 0.619: 466 (40%); 0.8056: 246 (21%) | 0.0913: 236 (20%); 0.3532: 466 (40%); 0.619: 704 (61%); 0.8056: 930 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.65, 16.83, 19.272, 23.93 | 14.65: 930 (80%); 16.83: 699 (60%); 19.272: 465 (40%); 23.93: 235 (20%) | 14.65: 234 (20%); 16.83: 468 (40%); 19.272: 697 (60%); 23.93: 930 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 14.65, 16.83, 19.272, 23.93 | 14.65: 930 (80%); 16.83: 699 (60%); 19.272: 465 (40%); 23.93: 235 (20%) | 14.65: 234 (20%); 16.83: 468 (40%); 19.272: 697 (60%); 23.93: 930 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8523, 0.8798, 0.9082, 0.9476 | 0.8523: 933 (80%); 0.8798: 698 (60%); 0.9082: 468 (40%); 0.9476: 233 (20%) | 0.8523: 233 (20%); 0.8798: 466 (40%); 0.9082: 700 (60%); 0.9476: 933 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.7, 0.86, 1.006, 1.298 | 0.7: 943 (81%); 0.86: 700 (60%); 1.006: 465 (40%); 1.298: 233 (20%) | 0.7: 237 (20%); 0.86: 474 (41%); 1.006: 697 (60%); 1.298: 929 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 100.0% | 0.0182, 0.0405, 0.0651, 0.1083 | 0.0182: 932 (80%); 0.0405: 698 (60%); 0.0651: 465 (40%); 0.1083: 233 (20%) | 0.0182: 233 (20%); 0.0405: 466 (40%); 0.0651: 697 (60%); 0.1083: 931 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 40.1904, 67.9931, 104.0311, 182.7245 | 40.1904: 929 (80%); 67.9931: 697 (60%); 104.0311: 465 (40%); 182.7245: 233 (20%) | 40.1904: 233 (20%); 67.9931: 465 (40%); 104.0311: 697 (60%); 182.7245: 929 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1162 (100%) | 0: 1013 (87%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 1162 (100%) | 0: 1052 (91%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | 0.0113, 0.045, 0.0786, 0.1231 | 0.0113: 930 (80%); 0.045: 698 (60%); 0.0786: 465 (40%); 0.1231: 233 (20%) | 0.0113: 234 (20%); 0.045: 465 (40%); 0.0786: 697 (60%); 0.1231: 930 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -27.602, -14.912, -8.21, -4.062 | -27.602: 929 (80%); -14.912: 697 (60%); -8.21: 467 (40%); -4.062: 233 (20%) | -27.602: 233 (20%); -14.912: 465 (40%); -8.21: 698 (60%); -4.062: 929 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.3% | 0.5509, 0.843, 1.0626, 1.3294 | 0.5509: 923 (79%); 0.843: 692 (60%); 1.0626: 462 (40%); 1.3294: 231 (20%) | 0.5509: 231 (20%); 0.843: 462 (40%); 1.0626: 693 (60%); 1.3294: 923 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.3% | 3, 5, 7, 9 | 3: 966 (83%); 5: 765 (66%); 7: 543 (47%); 9: 290 (25%) | 3: 293 (25%); 5: 495 (43%); 7: 724 (62%); 9: 1009 (87%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 99.2% | 0.1902, 0.2279, 0.275, 0.352 | 0.1902: 923 (79%); 0.2279: 692 (60%); 0.275: 463 (40%); 0.352: 231 (20%) | 0.1902: 231 (20%); 0.2279: 463 (40%); 0.275: 692 (60%); 0.352: 922 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 99.2% | 3, 5, 7, 9 | 3: 963 (83%); 5: 767 (66%); 7: 541 (47%); 9: 303 (26%) | 3: 288 (25%); 5: 505 (43%); 7: 718 (62%); 9: 1007 (87%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.3% | 0.0273, 0.0376, 0.0503, 0.0731 | 0.0273: 926 (80%); 0.0376: 693 (60%); 0.0503: 462 (40%); 0.0731: 231 (20%) | 0.0273: 233 (20%); 0.0376: 462 (40%); 0.0503: 693 (60%); 0.0731: 923 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.3% | 4, 6, 8, 9 | 4: 953 (82%); 6: 742 (64%); 8: 518 (45%); 9: 384 (33%) | 4: 292 (25%); 6: 530 (46%); 8: 770 (66%); 9: 930 (80%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.4% | -0.1068, 0.0005, 0.1019, 0.2566 | -0.1068: 924 (80%); 0.0005: 694 (60%); 0.1019: 462 (40%); 0.2566: 231 (20%) | -0.1068: 231 (20%); 0.0005: 463 (40%); 0.1019: 693 (60%); 0.2566: 924 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.4% | 3, 5, 7, 9 | 3: 1021 (88%); 5: 775 (67%); 7: 526 (45%); 9: 258 (22%) | 3: 250 (22%); 5: 512 (44%); 7: 762 (66%); 9: 1019 (88%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 4.4% |
| 8k_item_5_02_filed_within_7d | 3.5% |
| above_avwap_20high | 73.7% |
| above_avwap_20low | 97.8% |
| above_avwap_252low | 93.5% |
| above_avwap_50low | 97.5% |
| above_cam_r3 | 66.2% |
| above_cam_r4 | 38.6% |
| above_cpr | 82.2% |
| above_pivot | 84.6% |
| above_prev_high | 54.9% |
| above_prev_high_clearance_atr_05 | 23.9% |
| above_prev_low | 96.8% |
| above_r1 | 45.7% |
| above_r2 | 23.2% |
| above_vwap | 72.9% |
| above_wood_p | 81.2% |
| ad_rising | 77.5% |
| adx_cross_up | 2.2% |
| adx_cross_up_20 | 3.8% |
| adx_di_bear | 17.6% |
| adx_di_bull | 82.4% |
| adx_strong | 2.7% |
| adx_trending | 31.4% |
| ao_cross_dn | 0.3% |
| ao_cross_up | 7.1% |
| ao_positive | 68.8% |
| ao_twin_peaks_bull | 1.9% |
| at_key_fib | 17.8% |
| at_key_fib_wide | 42.7% |
| avwap_20high_loss_recent_3d | 12.2% |
| avwap_20high_reclaim_recent_3d | 46.7% |
| avwap_20low_loss_recent_3d | 2.0% |
| avwap_20low_reclaim_recent_3d | 12.5% |
| avwap_252low_loss_recent_3d | 1.2% |
| avwap_252low_reclaim_recent_3d | 24.0% |
| avwap_50low_loss_recent_3d | 1.4% |
| avwap_50low_reclaim_recent_3d | 13.0% |
| bb_10_20_above_mid | 92.5% |
| bb_10_20_expanding | 63.8% |
| bb_10_20_pctb_gt_75 | 71.5% |
| bb_10_20_pctb_gt_8 | 61.4% |
| bb_10_20_pctb_gt_85 | 49.7% |
| bb_10_20_pctb_gt_9 | 37.4% |
| bb_10_20_pctb_gt_95 | 24.7% |
| bb_10_20_pctb_lt_05 | 0.2% |
| bb_10_20_pctb_lt_1 | 0.3% |
| bb_10_20_pctb_lt_15 | 0.4% |
| bb_10_20_pctb_lt_2 | 1.0% |
| bb_10_20_pctb_lt_25 | 1.4% |
| bb_10_20_reclaim_from_lower_recent_3d | 1.0% |
| bb_10_20_reclaim_from_upper_recent_3d | 16.9% |
| bb_10_20_squeeze | 34.3% |
| bb_10_20_touch_lower | 0.3% |
| bb_10_20_touch_upper | 25.2% |
| bb_20_15_above_mid | 94.6% |
| bb_20_15_expanding | 61.3% |
| bb_20_15_pctb_gt_75 | 79.5% |
| bb_20_15_pctb_gt_8 | 72.7% |
| bb_20_15_pctb_gt_85 | 67.5% |
| bb_20_15_pctb_gt_9 | 62.1% |
| bb_20_15_pctb_gt_95 | 56.2% |
| bb_20_15_pctb_lt_25 | 0.3% |
| bb_20_15_reclaim_from_lower_recent_3d | 1.5% |
| bb_20_15_reclaim_from_upper_recent_3d | 12.4% |
| bb_20_15_squeeze | 29.2% |
| bb_20_15_touch_upper | 57.5% |
| bb_20_20_above_mid | 94.6% |
| bb_20_20_expanding | 61.4% |
| bb_20_20_pctb_gt_75 | 69.9% |
| bb_20_20_pctb_gt_8 | 62.1% |
| bb_20_20_pctb_gt_85 | 53.4% |
| bb_20_20_pctb_gt_9 | 43.9% |
| bb_20_20_pctb_gt_95 | 33.1% |
| bb_20_20_reclaim_from_lower_recent_3d | 0.9% |
| bb_20_20_reclaim_from_upper_recent_3d | 10.3% |
| bb_20_20_squeeze | 14.6% |
| bb_20_20_touch_upper | 32.2% |
| bearish_pin_bar | 5.5% |
| below_avwap_20high | 26.3% |
| below_avwap_20low | 2.2% |
| below_avwap_252low | 6.5% |
| below_avwap_50low | 2.5% |
| below_cam_s3 | 4.0% |
| below_cam_s4 | 1.2% |
| below_cpr | 15.4% |
| below_ema_20 | 7.2% |
| below_ema_20_break_recent_5d | 3.6% |
| below_ema_21 | 7.6% |
| below_ema_21_break_recent_5d | 3.4% |
| below_ema_50 | 16.4% |
| below_ema_50_break_recent_5d | 3.6% |
| below_ema_9 | 6.1% |
| below_ema_9_break_recent_5d | 5.9% |
| below_prev_high | 44.8% |
| below_prev_low | 3.1% |
| below_prev_low_clearance_atr_05 | 0.5% |
| below_s1 | 1.3% |
| below_s2 | 0.7% |
| below_sma_20 | 5.4% |
| below_sma_200 | 18.9% |
| below_sma_21 | 6.1% |
| below_sma_50 | 23.8% |
| below_sma_9 | 8.9% |
| below_vwap | 27.1% |
| break_52w_high | 1.6% |
| break_52w_high_clearance_atr_05 | 0.4% |
| break_52w_high_confirmed_today | 0.5% |
| bullish_engulfing | 7.9% |
| bullish_pin_bar | 5.2% |
| capitulation_recent_3d | 0.7% |
| ceo_buy | 1.4% |
| cfo_buy | 0.4% |
| chandelier_long_bullish | 92.9% |
| chandelier_long_flip_dn | 0.3% |
| chandelier_short_bearish | 19.4% |
| chandelier_short_flip_up | 13.4% |
| classification_change_from_tech | 33.3% |
| classification_change_to_defensive | 66.7% |
| close_in_bottom_40pct_of_range | 8.6% |
| close_in_top_40pct_of_range | 72.2% |
| cluster_buy | 0.7% |
| cmf_cross_dn | 2.2% |
| cmf_cross_up | 10.1% |
| cmf_negative | 27.1% |
| cmf_positive | 72.9% |
| concentrated_sell | 6.1% |
| cpr_narrow | 87.6% |
| cpr_narrow_tight | 22.9% |
| cup_handle_detected | 19.9% |
| cup_handle_neckline_break_retest_long | 12.5% |
| dc10_breakout_dn | 0.1% |
| dc10_breakout_dn_1pct | 0.3% |
| dc10_breakout_up | 43.5% |
| dc10_breakout_up_1pct | 60.3% |
| dc10_new_high | 51.5% |
| dc10_strong_breakout_up | 16.9% |
| dc20_breakout_up | 32.5% |
| dc20_new_high | 38.7% |
| dc20_resistance_break_retest_strong | 33.0% |
| dc20_support_break_retest_strong | 0.2% |
| defensive_leadership | 44.9% |
| director_only_buy | 3.6% |
| doji | 4.5% |
| double_bottom_detected | 12.1% |
| double_top_detected | 15.0% |
| dpi_elevated | 61.6% |
| drying_volume_on_up_turn | 59.6% |
| ema_20_50_bearish | 53.8% |
| ema_20_50_bullish | 46.2% |
| ema_20_50_death_cross | 0.1% |
| ema_20_50_golden_cross | 5.3% |
| ema_50_200_bearish | 46.0% |
| ema_50_200_bullish | 54.0% |
| ema_50_200_golden_cross | 1.2% |
| ema_9_21_bearish | 24.1% |
| ema_9_21_bullish | 75.9% |
| ema_9_21_death_cross | 0.1% |
| ema_9_21_golden_cross | 9.0% |
| flag_bear_break_retest_short | 0.1% |
| flag_bear_broke | 0.2% |
| flag_bear_detected | 0.2% |
| flag_bull_break_retest_long | 0.9% |
| flag_bull_broke | 1.5% |
| flag_bull_detected | 0.5% |
| force_index_cross_dn | 1.1% |
| force_index_cross_up | 6.4% |
| force_index_positive | 90.3% |
| gap_dn_1_5pct | 4.9% |
| gap_dn_2pct | 3.1% |
| gap_up_1_5pct | 11.6% |
| gap_up_2pct | 7.6% |
| hammer | 4.0% |
| head_shoulders_bottom_detected | 6.5% |
| head_shoulders_top_detected | 4.0% |
| house_cluster_buy | 3.5% |
| house_cluster_sell | 4.7% |
| htf_aligned_bear | 1.2% |
| htf_aligned_bull | 49.2% |
| htf_disagreement | 4.6% |
| hull_bearish | 9.7% |
| hull_bullish | 90.3% |
| hull_flip_dn | 3.4% |
| hull_flip_up | 4.9% |
| ichi_above_cloud | 53.2% |
| ichi_above_cloud_break_recent_5d | 26.9% |
| ichi_below_cloud | 27.8% |
| ichi_below_cloud_break_recent_5d | 2.2% |
| ichi_cloud_thick | 85.8% |
| ichi_tk_bearish | 28.2% |
| ichi_tk_bullish | 65.5% |
| ichi_tk_cross_dn | 0.2% |
| ichi_tk_cross_up | 5.7% |
| ichi_weekly_above_cloud | 55.0% |
| ichi_weekly_below_cloud | 12.2% |
| ichi_weekly_in_cloud | 32.8% |
| in_reversal_window | 6.5% |
| inside_bar | 10.6% |
| inside_cpr | 3.3% |
| inside_kc | 71.3% |
| insider_cluster_active | 28.6% |
| institutional_buy | 99.7% |
| institutional_negative | 0.3% |
| institutional_persistence_growing | 39.2% |
| institutional_persistence_strong | 56.1% |
| institutional_strong_buy | 88.8% |
| inverted_cup_handle_detected | 18.2% |
| is_friday | 19.4% |
| is_halloween_period | 53.7% |
| is_halloween_period_first_day | 0.2% |
| is_january | 9.3% |
| is_january_extended | 10.7% |
| is_monday | 20.4% |
| is_pre_holiday | 4.9% |
| is_summer_period | 46.3% |
| is_totm_window | 38.2% |
| is_totm_window_first_day | 11.3% |
| is_week_open | 23.0% |
| kc_touch_upper | 34.8% |
| large_dollar_buy | 1.8% |
| macd_12_26_9_crossover_up | 8.1% |
| macd_8_21_5_bearish | 12.4% |
| macd_8_21_5_bullish | 87.6% |
| macd_8_21_5_crossover_dn | 3.7% |
| macd_8_21_5_crossover_up | 3.7% |
| marubozu_bull | 2.2% |
| mfi_broad_overbought | 27.5% |
| mfi_broad_oversold | 0.5% |
| mfi_overbought | 6.6% |
| monthly_above_sma_12 | 80.3% |
| monthly_above_sma_6 | 64.8% |
| monthly_bias_bear | 7.5% |
| monthly_bias_bull | 52.6% |
| monthly_momentum_pos | 65.8% |
| morning_star | 8.1% |
| near_52w_high | 3.6% |
| near_52w_high_95pct | 9.7% |
| near_52w_high_retest_long | 1.1% |
| near_avwap_20high_atr_05x | 56.0% |
| near_avwap_20high_atr_10x | 77.4% |
| near_avwap_20high_atr_15x | 90.0% |
| near_avwap_20high_atr_20x | 96.3% |
| near_avwap_20low_atr_05x | 7.1% |
| near_avwap_20low_atr_10x | 20.0% |
| near_avwap_20low_atr_15x | 37.2% |
| near_avwap_20low_atr_20x | 57.5% |
| near_avwap_252low_atr_05x | 11.3% |
| near_avwap_252low_atr_10x | 22.0% |
| near_avwap_252low_atr_15x | 32.8% |
| near_avwap_252low_atr_20x | 43.6% |
| near_avwap_50low_atr_05x | 6.0% |
| near_avwap_50low_atr_10x | 16.4% |
| near_avwap_50low_atr_15x | 29.2% |
| near_avwap_50low_atr_20x | 43.9% |
| near_cam_r3 | 23.8% |
| near_cam_s3 | 6.5% |
| near_cam_s4 | 1.7% |
| near_fib_236 | 6.0% |
| near_fib_382 | 7.4% |
| near_fib_500 | 4.9% |
| near_fib_618 | 5.5% |
| near_fib_786 | 0.9% |
| near_pivot | 13.5% |
| near_prev_close | 14.9% |
| near_prev_high | 18.3% |
| near_prev_low | 3.9% |
| near_r1 | 23.1% |
| near_r1_wide | 71.2% |
| near_r2 | 7.8% |
| near_r2_wide | 51.4% |
| near_s1 | 2.3% |
| near_s1_wide | 25.6% |
| near_s2 | 0.3% |
| near_s2_wide | 8.6% |
| near_s3 | 0.2% |
| near_wood_r1 | 11.0% |
| near_wood_s1 | 5.5% |
| news_uses_polygon_score | 24.2% |
| obv_bearish | 14.5% |
| obv_bullish | 85.5% |
| obv_diverge_bull | 4.0% |
| obv_falling | 21.8% |
| obv_rising | 78.2% |
| outside_bar | 6.9% |
| pead_negative_surprise | 14.5% |
| pead_positive_surprise | 24.7% |
| pin_bar | 10.8% |
| po3_accumulation_active | 32.2% |
| po3_bullish | 15.4% |
| po3_manipulation_sweep_down | 3.9% |
| po3_manipulation_sweep_up | 17.6% |
| po3_mmbm_setup | 3.5% |
| po3_sweep_above_prior_high | 72.7% |
| po3_sweep_below_prior_low | 27.6% |
| ppo_bullish | 98.9% |
| ppo_crossover_dn | 0.3% |
| ppo_crossover_up | 7.7% |
| pre_fomc_d0 | 2.4% |
| pre_fomc_d1 | 2.4% |
| pre_fomc_window | 4.8% |
| price_above_dema | 90.9% |
| price_above_ema_20 | 92.8% |
| price_above_ema_200_break_recent_5d | 60.2% |
| price_above_ema_20_break_recent_5d | 44.3% |
| price_above_ema_21 | 92.4% |
| price_above_ema_21_break_recent_5d | 44.2% |
| price_above_ema_50 | 83.6% |
| price_above_ema_50_break_recent_5d | 44.1% |
| price_above_ema_9 | 93.9% |
| price_above_ema_9_break_recent_5d | 48.5% |
| price_above_hull | 78.7% |
| price_above_sma_200 | 81.1% |
| price_above_sma_21 | 93.9% |
| price_above_sma_50 | 76.2% |
| price_above_tema | 80.1% |
| price_below_dema | 9.1% |
| price_below_hull | 21.3% |
| price_below_tema | 19.9% |
| psar_bullish | 88.1% |
| psar_flip_dn | 2.6% |
| psar_flip_up | 5.2% |
| r1_break_retest_long | 92.9% |
| recent_blowoff_at_r3 | 0.1% |
| resistance_break_retest | 47.7% |
| risk_off_regime_bond_signal | 21.4% |
| risk_off_regime_bond_signal_strong | 5.4% |
| risk_off_regime_gold_signal | 37.4% |
| risk_on_regime_bond_signal | 44.3% |
| risk_on_regime_bond_signal_strong | 22.5% |
| roc_positive | 91.7% |
| roc_turning_dn | 1.8% |
| roc_turning_up | 9.0% |
| rsi_14_bullish | 90.4% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 0.3% |
| rsi_14_cross_dn_overbought_recent_3d | 4.7% |
| rsi_14_cross_up_oversold_recent_3d | 0.6% |
| rsi_14_extreme_ob | 0.5% |
| rsi_14_overbought | 12.0% |
| rsi_14_rising | 86.1% |
| rsi_21_bullish | 85.6% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.1% |
| rsi_21_cross_dn_overbought_recent_3d | 1.1% |
| rsi_21_overbought | 2.8% |
| rsi_21_rising | 86.1% |
| rsi_2_bullish | 88.0% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 21.6% |
| rsi_2_cross_dn_overbought_recent_3d | 18.2% |
| rsi_2_cross_up_extreme_os_recent_3d | 15.7% |
| rsi_2_cross_up_oversold_recent_3d | 25.6% |
| rsi_2_extreme_ob | 65.4% |
| rsi_2_extreme_os | 2.8% |
| rsi_2_overbought | 74.6% |
| rsi_2_oversold | 5.6% |
| rsi_2_rising | 86.1% |
| rsi_9_bullish | 94.1% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 3.1% |
| rsi_9_cross_dn_overbought_recent_3d | 9.0% |
| rsi_9_cross_up_extreme_os_recent_3d | 0.2% |
| rsi_9_cross_up_oversold_recent_3d | 1.6% |
| rsi_9_extreme_ob | 6.6% |
| rsi_9_overbought | 33.2% |
| rsi_9_rising | 86.1% |
| s1_break_retest_short | 11.6% |
| sc_13d_filed_within_30d | 2.0% |
| sc_13g_filed_within_30d | 2.2% |
| sector_outperforming_spy | 45.0% |
| sector_underperforming_spy | 55.0% |
| shooting_star | 5.2% |
| sma_20_50_bullish | 37.8% |
| sma_20_50_golden_cross | 3.2% |
| sma_50_200_bullish | 53.7% |
| sma_50_200_golden_cross | 0.1% |
| sma_9_21_bullish | 73.3% |
| sma_9_21_golden_cross | 6.1% |
| smc_bos_bearish | 10.0% |
| smc_bos_bullish | 7.6% |
| smc_bos_retest_long | 7.3% |
| smc_bos_retest_short | 4.3% |
| smc_breaker_block_bearish | 8.5% |
| smc_breaker_block_bullish | 24.9% |
| smc_choch_bearish | 7.4% |
| smc_choch_bullish | 5.2% |
| smc_equal_highs_swept | 2.4% |
| smc_equal_lows_swept | 4.1% |
| smc_fvg_bearish_active | 13.9% |
| smc_fvg_bullish_active | 67.3% |
| smc_fvg_retest_long_zone | 3.2% |
| smc_fvg_retest_short_zone | 8.0% |
| smc_in_discount_zone | 37.1% |
| smc_in_premium_zone | 85.2% |
| smc_inverse_fvg_bearish | 68.0% |
| smc_inverse_fvg_bullish | 97.7% |
| smc_liquidity_swept_dn | 0.8% |
| smc_liquidity_swept_up | 2.1% |
| smc_mitigation_block_short | 5.5% |
| smc_ob_bearish_active | 38.0% |
| smc_ob_bullish_active | 23.6% |
| smc_ote_long_zone | 11.7% |
| smc_ote_short_zone | 12.4% |
| squeeze_fire_dn | 0.3% |
| squeeze_fire_up | 4.7% |
| squeeze_in | 20.4% |
| squeeze_positive | 92.3% |
| stoch_bearish_cross | 7.0% |
| stoch_broad_overbought | 65.2% |
| stoch_broad_oversold | 0.3% |
| stoch_bullish_cross | 12.0% |
| stoch_overbought | 55.9% |
| stoch_oversold | 0.2% |
| stochrsi_cross_dn | 25.1% |
| stochrsi_cross_up | 13.8% |
| stochrsi_overbought | 67.4% |
| stochrsi_oversold | 4.5% |
| supertrend_bearish | 0.2% |
| supertrend_bullish | 99.8% |
| supertrend_flip_recent_long_5d | 0.3% |
| supertrend_flip_recent_short_5d | 0.2% |
| support_break_retest | 0.4% |
| tema_above_dema | 84.6% |
| tema_cross_dn | 0.1% |
| tema_cross_up | 6.2% |
| three_white_soldiers | 20.4% |
| triangle_apex_break_retest_long | 21.3% |
| triangle_ascending_detected | 11.4% |
| triangle_descending_detected | 9.0% |
| uo_overbought | 8.3% |
| uo_oversold | 0.1% |
| usd_strengthening | 15.1% |
| usd_weakening | 17.2% |
| vix_band_high | 35.7% |
| vix_band_low | 38.4% |
| vix_band_mid | 25.9% |
| vix_term_backwardation | 5.2% |
| vix_term_contango | 94.8% |
| vol_above_avg | 40.4% |
| vol_below_avg | 59.6% |
| vol_spike_12x | 25.6% |
| vol_spike_15x | 13.2% |
| vol_spike_17x | 8.8% |
| vol_spike_2x | 5.5% |
| vol_spike_2x_on_down_day_recent_3d | 2.1% |
| vol_spike_2x_on_up_day_recent_3d | 6.3% |
| vol_spike_3x | 1.3% |
| vp_above_value_area | 40.1% |
| vp_below_value_area | 3.9% |
| vp_close_above_poc | 76.7% |
| vp_close_below_poc | 23.3% |
| vp_in_value_area | 56.0% |
| week_open_gap_down_15pct | 1.2% |
| week_open_gap_up_15pct | 1.9% |
| weekly_above_ema_10 | 84.7% |
| weekly_above_ema_20 | 81.8% |
| weekly_bias_bear | 12.8% |
| weekly_bias_bull | 79.3% |
| weekly_momentum_pos | 84.8% |
| williams_r_overbought | 70.1% |
| williams_r_oversold | 0.1% |
| williams_r_rising | 69.4% |
| within_pead_window | 39.5% |
| within_post_deletion_window | 1.5% |
| within_post_inclusion_window | 4.1% |
| xs_avoid_high_ivol | 73.7% |
| xs_avoid_high_max | 66.7% |
| xs_high_beta_decile | 25.1% |
| xs_low_beta_bottom_quintile | 25.1% |
| xs_low_beta_decile | 16.3% |
| xs_low_beta_decile_entry_recent_5d | 0.5% |
| xs_low_beta_top_quintile | 16.3% |
| xs_momentum_bottom_decile | 3.5% |
| xs_momentum_bottom_quintile | 11.6% |
| xs_momentum_top_decile | 11.8% |
| xs_momentum_top_quintile | 22.3% |
| xs_quality_bottom_quintile | 17.9% |
| xs_quality_top_quintile | 21.1% |
| xs_quality_top_tercile | 40.0% |
| year_high_break_retest_long | 1.2% |
| yoy_surprise_high | 54.8% |
| yoy_surprise_negative | 35.7% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 97.6% |
| committed_growth_holders | 97.6% |
| corp_donations_1y | 7.8% |
| corp_donations_count_1y | 7.8% |
| corp_donations_unique_pacs | 7.8% |
| cot_rut_commercials_pctile_3y | 52.1% |
| cot_rut_mmoney_pctile_3y | 52.1% |
| cup_handle_depth_pct | 31.4% |
| days_since_classification_change | 0.3% |
| days_since_deletion | 5.8% |
| days_since_inclusion | 14.5% |
| days_to_next_holiday | 68.6% |
| days_to_rebalance | 7.5% |
| dpi_30d_avg | 97.3% |
| dpi_recent | 97.3% |
| earnings_announcement_return | 90.5% |
| earnings_eps_yoy_growth | 95.1% |
| flag_bull_pole_move_pct | 0.5% |
| gov_contracts_4q_sum | 38.8% |
| gov_contracts_last_qtr_amount | 38.8% |
| gov_contracts_qoq_growth | 38.8% |
| head_shoulders_magnitude_pct | 10.2% |
| insider_director_buyers_30d | 5.4% |
| insider_officer_buyers_30d | 5.4% |
| insider_total_shares_bought_30d | 5.4% |
| insider_unique_buyers_30d | 5.4% |
| inverted_cup_handle_height_pct | 29.9% |
| lobbying_amount_1y | 72.4% |
| lobbying_amount_q | 72.4% |
| lobbying_amount_yoy | 72.4% |
| monthly_momentum_6m | 97.2% |
| otc_short_ratio_recent | 97.3% |
| otc_volume_recent | 97.3% |
| pair_half_life | 93.1% |
| pair_max_abs_zscore | 93.1% |
| pair_zscore_signed | 93.1% |
| pct_from_avwap_20high | 60.1% |
| pct_from_avwap_252low | 97.4% |
| persistent_holders_4q | 97.6% |
| persistent_holders_8q | 97.6% |
| sc_13g_latest_percent_owned | 1.4% |
| search_volume_index_recent | 76.1% |
| search_volume_observations | 76.1% |
| search_volume_zscore_30d | 76.1% |
| sector_etf_return_20d | 1.7% |
| spy_return_20d | 1.7% |
| total_active_holders | 97.6% |
| triangle_breakdown_pct | 9.0% |
| triangle_breakout_pct | 11.4% |
| xs_quality_decile | 60.5% |
| xs_quality_gross_profitability | 60.5% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (1.0), `avwap_252low` (0.997), `avwap_50low` (1.0), `bb_10_20_lower` (0.999), `bb_10_20_mid` (1.0), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.999), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.999), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.999), `cam_r2` (0.999), `cam_r3` (0.999), `cam_r4` (0.999), `cam_s1` (0.999), `cam_s2` (0.999), `cam_s3` (0.999), `cam_s4` (0.999), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.999), `cpr_top` (0.999), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.998), `dc10_lower` (0.999), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.999), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.999), `double_bottom_trough` (0.999), `double_top_neckline` (0.997), `double_top_peak` (0.997), `entry_stop_long` (0.999), `entry_stop_short` (0.998), `fib_236` (0.998), `fib_382` (0.998), `fib_500` (0.999), `fib_618` (0.999), `fib_786` (0.999), `fib_ext_127` (0.996), `fib_ext_162` (0.993), `flag_bear_breakdown_level` (1.0), `flag_bear_pole_move_pct` (-1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.998), `head_shoulders_top_neckline` (0.997), `hull_ma` (0.999), `ichi_kijun` (1.0), `ichi_senkou_a` (0.996), `ichi_senkou_b` (0.996), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (1.0), `inverted_cup_handle_rim_low` (0.999), `kc_lower` (1.0), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.999), `monthly_sma_12` (0.995), `monthly_sma_6` (0.998), `pivot` (0.999), `prev_close` (0.999), `prev_high` (0.999), `prev_low` (0.999), `psar_value` (0.998), `r1` (0.999), `r2` (0.999), `r3` (0.999), `s1` (0.999), `s2` (0.999), `s3` (0.999), `supertrend_value` (0.999), `swing_high` (0.997), `swing_low` (0.997), `tema` (0.999), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.997), `vp_value_area_high` (0.997), `vp_value_area_low` (0.997), `vwap` (0.963), `vwap_lower_1` (0.956), `vwap_upper_1` (0.967), `vwap_upper_2` (0.97), `weekly_close` (0.999), `weekly_ema_10` (1.0), `weekly_ema_20` (0.999), `wood_p` (0.999), `wood_r1` (0.999), `wood_r2` (0.999), `wood_s1` (0.999), `wood_s2` (0.999), `year_high` (0.993), `year_low` (0.971)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P1.1 | span triple (mirror of the bearish entry | 2 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 1 |
| P2.1 | ema span (the 200 in above/below_ema_200 | 8 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 7 |
| P3 | smart-money union (5 flags) | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 0 |

```
FULL FACTORIAL     2 x 8 x 1 = 16
offline gradings   0 level-combinations x 24 exits = 0 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  15 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 0 + 15 = 16 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 603 census axes join it only when REGISTERED at the T3 band review.
