# Table A - m_and_a_target_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build adafdd452 | commit adafdd452 at 2026-10-25 20:59:24 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** sec_edgar_sleeve | **status:** NOT-STARTED | **R5 fires:** 1023 (closed fires in the exit cube: 1023 of 1023, S6-B3258) | **surviving fires (T1):** 751 (survives_pct 0.7341)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  8k_item_1_01_filed_within_30d  <- backtest/signals/sec_edgar_extractor.py (f-string template)
       DEFN: an 8-K carrying Item 1.01 (material definitive agreement) filed in the last 30 days (sec_edgar_extractor.py eight_k_item_filed_within_days)
       knobs P1.1-P1.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P2  po3_accum_range_pct >= 0.0556   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_m_and_a_target_long (docstring and return dropped):

```python
fires = bool(s.get('8k_item_1_01_filed_within_30d', False))
fires = fires and s.get('po3_accum_range_pct', float('-inf')) >= 0.0556
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
| P1 | PRODUCER | 8k_item_1_01_filed_within_30d - emitted by backtest/signals/sec_edgar_extractor.py (f-string template); the boolean's UNDERLYING condition is bandable through its producer's internals | an 8-K carrying Item 1.01 (material definitive agreement) filed in the last 30 days (sec_edgar_extractor.py eight_k_item_filed_within_days) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (runbook section 4.3 - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | filing window - an Item 1.01 8-K filed within the last N days - backtest/signals/sec_edgar_extractor.py eight_k_item_filed_within_days | BRACKET production | 30 | 7, 14, 30, 60 | offline 0 of 4 levels - none - no filing date is persisted on the fire, only the 30-day boolean (the 7-day key on the fires is item 5.02's) | the whole band - 7 and 14 are tighter and 60 looser, and every one needs the producer re-run; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | STRATEGY | po3_accum_range_pct `>= 0.0556` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `>= 0.0556` | production + 4 tighter measured levels | offline 4 of 5 levels - measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (runbook section 3.6; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (module writing the key) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| po3_accum_range_pct | backtest/signals/ict_producers.py | `>= 0.0556` | 100.0% | TIGHTER = RAISE the floor: 0.0679 -> 603 (80%); 0.0844 -> 451 (60%); 0.1112 -> 301 (40%); 0.1559 -> 151 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (module writing the key) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/technical.py | 100.0% | 17.5, 21.74, 26.34, 32.08 | 17.5: 601 (80%); 21.74: 451 (60%); 26.34: 301 (40%); 32.08: 151 (20%) | 17.5: 151 (20%); 21.74: 302 (40%); 26.34: 451 (60%); 32.08: 601 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 23.67, 27.99, 31.57, 36.33 | 23.67: 601 (80%); 27.99: 451 (60%); 31.57: 301 (40%); 36.33: 151 (20%) | 23.67: 151 (20%); 27.99: 301 (40%); 31.57: 451 (60%); 36.33: 601 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 13.04, 15.69, 18.88, 23.27 | 13.04: 601 (80%); 15.69: 451 (60%); 18.88: 301 (40%); 23.27: 151 (20%) | 13.04: 151 (20%); 15.69: 301 (40%); 18.88: 452 (60%); 23.27: 601 (80%) | OFFLINE |
| ao | backtest/signals/technical.py | 100.0% | -10.9529, -4.9044, -1.9299, -0.0347 | -10.9529: 601 (80%); -4.9044: 451 (60%); -1.9299: 301 (40%); -0.0347: 151 (20%) | -10.9529: 151 (20%); -4.9044: 301 (40%); -1.9299: 451 (60%); -0.0347: 601 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +1 | 100.0% | 1.0759, 2.2027, 3.7985, 6.4376 | 1.0759: 601 (80%); 2.2027: 451 (60%); 3.7985: 301 (40%); 6.4376: 151 (20%) | 1.0759: 151 (20%); 2.2027: 301 (40%); 3.7985: 451 (60%); 6.4376: 601 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py | 100.0% | 1.0759, 2.2027, 3.7985, 6.4376 | 1.0759: 601 (80%); 2.2027: 451 (60%); 3.7985: 301 (40%); 6.4376: 151 (20%) | 1.0759: 151 (20%); 2.2027: 301 (40%); 3.7985: 451 (60%); 6.4376: 601 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.718, 3.303, 4.037, 5.249 | 2.718: 601 (80%); 3.303: 452 (60%); 4.037: 301 (40%); 5.249: 151 (20%) | 2.718: 151 (20%); 3.303: 301 (40%); 4.037: 451 (60%); 5.249: 601 (80%) | OFFLINE |
| bb_10_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0895, 0.125, 0.1629, 0.2263 | 0.0895: 601 (80%); 0.125: 451 (60%); 0.1629: 301 (40%); 0.2263: 151 (20%) | 0.0895: 151 (20%); 0.125: 301 (40%); 0.1629: 451 (60%); 0.2263: 601 (80%) | OFFLINE |
| bb_10_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.1681, 0.2562, 0.3785, 0.6034 | 0.1681: 601 (80%); 0.2562: 451 (60%); 0.3785: 301 (40%); 0.6034: 151 (20%) | 0.1681: 151 (20%); 0.2562: 301 (40%); 0.3785: 451 (60%); 0.6034: 601 (80%) | OFFLINE |
| bb_20_15_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.0846, 0.1158, 0.1472, 0.2056 | 0.0846: 602 (80%); 0.1158: 451 (60%); 0.1472: 302 (40%); 0.2056: 151 (20%) | 0.0846: 151 (20%); 0.1158: 302 (40%); 0.1472: 451 (60%); 0.2056: 601 (80%) | OFFLINE |
| bb_20_15_pctb | backtest/signals/technical.py (f-string template) | 100.0% | -0.0687, 0.0796, 0.2301, 0.5064 | -0.0687: 601 (80%); 0.0796: 451 (60%); 0.2301: 301 (40%); 0.5064: 151 (20%) | -0.0687: 151 (20%); 0.0796: 301 (40%); 0.2301: 451 (60%); 0.5064: 601 (80%) | OFFLINE |
| bb_20_20_bandwidth | backtest/signals/technical.py (f-string template) | 100.0% | 0.1129, 0.1544, 0.1963, 0.2741 | 0.1129: 601 (80%); 0.1544: 451 (60%); 0.1963: 301 (40%); 0.2741: 151 (20%) | 0.1129: 152 (20%); 0.1544: 301 (40%); 0.1963: 451 (60%); 0.2741: 601 (80%) | OFFLINE |
| bb_20_20_pctb | backtest/signals/technical.py (f-string template) | 100.0% | 0.0735, 0.1847, 0.2975, 0.5048 | 0.0735: 601 (80%); 0.1847: 451 (60%); 0.2975: 301 (40%); 0.5048: 151 (20%) | 0.0735: 151 (20%); 0.1847: 301 (40%); 0.2975: 451 (60%); 0.5048: 601 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0391, -0.0099, 0.0087, 0.0427 | -0.0391: 602 (80%); -0.0099: 453 (60%); 0.0087: 301 (40%); 0.0427: 151 (20%) | -0.0391: 153 (20%); -0.0099: 301 (40%); 0.0087: 451 (60%); 0.0427: 606 (81%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1373, 0.162, 0.195, 0.2658 | 0.1373: 601 (80%); 0.162: 443 (59%); 0.195: 300 (40%); 0.2658: 150 (20%) | 0.1373: 150 (20%); 0.162: 308 (41%); 0.195: 451 (60%); 0.2658: 601 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 751 (100%) | 0: 693 (92%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1633, -0.0821, -0.0081, 0.0752 | -0.1633: 601 (80%); -0.0821: 451 (60%); -0.0081: 301 (40%); 0.0752: 151 (20%) | -0.1633: 151 (20%); -0.0821: 301 (40%); -0.0081: 451 (60%); 0.0752: 601 (80%) | OFFLINE |
| cnn_fg_days_since_publish | (no module found writing the key) | 100.0% | 0, 1 | 0: 751 (100%); 1: 266 (35%) | 0: 485 (65%); 1: 622 (83%) | OFFLINE |
| cot_copper_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2434, -0.1896, -0.1472, -0.1141 | -0.2434: 601 (80%); -0.1896: 454 (60%); -0.1472: 302 (40%); -0.1141: 155 (21%) | -0.2434: 153 (20%); -0.1896: 301 (40%); -0.1472: 460 (61%); -0.1141: 648 (86%) | OFFLINE |
| cot_copper_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2564, 0.6218, 0.6923, 0.7692 | 0.2564: 602 (80%); 0.6218: 451 (60%); 0.6923: 309 (41%); 0.7692: 181 (24%) | 0.2564: 152 (20%); 0.6218: 301 (40%); 0.6923: 457 (61%); 0.7692: 626 (83%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.2564, 0.4231, 0.6282, 0.8333 | 0.2564: 614 (82%); 0.4231: 454 (60%); 0.6282: 308 (41%); 0.8333: 157 (21%) | 0.2564: 151 (20%); 0.4231: 304 (40%); 0.6282: 456 (61%); 0.8333: 605 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0474, 0.0117, 0.0789, 0.1806 | -0.0474: 602 (80%); 0.0117: 471 (63%); 0.0789: 301 (40%); 0.1806: 155 (21%) | -0.0474: 164 (22%); 0.0117: 312 (42%); 0.0789: 452 (60%); 0.1806: 607 (81%) | OFFLINE |
| cot_dow_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3846, 0.4872, 0.5897, 0.7308 | 0.3846: 602 (80%); 0.4872: 464 (62%); 0.5897: 311 (41%); 0.7308: 164 (22%) | 0.3846: 180 (24%); 0.4872: 339 (45%); 0.5897: 452 (60%); 0.7308: 605 (81%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1474, 0.2949, 0.4551, 0.6218 | 0.1474: 610 (81%); 0.2949: 454 (60%); 0.4551: 311 (41%); 0.6218: 157 (21%) | 0.1474: 163 (22%); 0.2949: 301 (40%); 0.4551: 502 (67%); 0.6218: 605 (81%) | OFFLINE |
| cot_dxy_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.4997, -0.3338, -0.0978, 0.0612 | -0.4997: 601 (80%); -0.3338: 451 (60%); -0.0978: 310 (41%); 0.0612: 155 (21%) | -0.4997: 155 (21%); -0.3338: 302 (40%); -0.0978: 473 (63%); 0.0612: 603 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3269, 0.5192, 0.7372, 0.9103 | 0.3269: 603 (80%); 0.5192: 454 (60%); 0.7372: 312 (42%); 0.9103: 152 (20%) | 0.3269: 164 (22%); 0.5192: 313 (42%); 0.7372: 451 (60%); 0.9103: 608 (81%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1346, 0.3654, 0.5962, 0.8526 | 0.1346: 611 (81%); 0.3654: 452 (60%); 0.5962: 305 (41%); 0.8526: 165 (22%) | 0.1346: 151 (20%); 0.3654: 301 (40%); 0.5962: 452 (60%); 0.8526: 638 (85%) | OFFLINE |
| cot_gold_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0667, -0.0535, -0.0322, 0 | -0.0667: 603 (80%); -0.0535: 451 (60%); -0.0322: 303 (40%); 0: 261 (35%) | -0.0667: 154 (21%); -0.0535: 301 (40%); -0.0322: 454 (60%); 0: 726 (97%) | OFFLINE |
| cot_gold_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.4487, 0.7308, 0.8974, 1 | 0.4487: 602 (80%); 0.7308: 452 (60%); 0.8974: 303 (40%); 1: 210 (28%) | 0.4487: 154 (21%); 0.7308: 304 (40%); 0.8974: 459 (61%); 1: 751 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.109, 0.2821, 0.4936, 0.75 | 0.109: 612 (81%); 0.2821: 454 (60%); 0.4936: 303 (40%); 0.75: 155 (21%) | 0.109: 153 (20%); 0.2821: 304 (40%); 0.4936: 457 (61%); 0.75: 607 (81%) | OFFLINE |
| cot_ndx_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.011, 0.0456, 0.1218, 0.2661 | 0.011: 601 (80%); 0.0456: 452 (60%); 0.1218: 302 (40%); 0.2661: 151 (20%) | 0.011: 151 (20%); 0.0456: 305 (41%); 0.1218: 451 (60%); 0.2661: 606 (81%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.6144, 0.8013, 0.9494, 0.9744 | 0.6144: 601 (80%); 0.8013: 451 (60%); 0.9494: 301 (40%); 0.9744: 210 (28%) | 0.6144: 152 (20%); 0.8013: 301 (40%); 0.9494: 457 (61%); 0.9744: 618 (82%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.0833, 0.1803, 0.359, 0.7188 | 0.0833: 606 (81%); 0.1803: 454 (60%); 0.359: 305 (41%); 0.7188: 157 (21%) | 0.0833: 157 (21%); 0.1803: 308 (41%); 0.359: 455 (61%); 0.7188: 601 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.0812, 0.0123, 0.0931, 0.1876 | -0.0812: 628 (84%); 0.0123: 453 (60%); 0.0931: 302 (40%); 0.1876: 165 (22%) | -0.0812: 196 (26%); 0.0123: 307 (41%); 0.0931: 451 (60%); 0.1876: 603 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | backtest/signals/cot_positioning.py (f-string template) | 100.0% | -0.2049, 0, 0.0551, 0.1209 | -0.2049: 603 (80%); 0: 456 (61%); 0.0551: 302 (40%); 0.1209: 151 (20%) | -0.2049: 154 (21%); 0: 304 (40%); 0.0551: 460 (61%); 0.1209: 602 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.3205, 0.5705, 0.7628, 0.9551 | 0.3205: 602 (80%); 0.5705: 453 (60%); 0.7628: 304 (40%); 0.9551: 153 (20%) | 0.3205: 153 (20%); 0.5705: 312 (42%); 0.7628: 461 (61%); 0.9551: 602 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | backtest/signals/cot_positioning.py (f-string template) | 100.0% | 0.1538, 0.3782, 0.5641, 0.8205 | 0.1538: 601 (80%); 0.3782: 452 (60%); 0.5641: 357 (48%); 0.8205: 154 (21%) | 0.1538: 154 (21%); 0.3782: 312 (42%); 0.5641: 454 (60%); 0.8205: 605 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0658, 0.155, 0.3017, 0.5983 | 0.0658: 602 (80%); 0.155: 451 (60%); 0.3017: 301 (40%); 0.5983: 151 (20%) | 0.0658: 151 (20%); 0.155: 301 (40%); 0.3017: 451 (60%); 0.5983: 602 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +1 | 98.7% | 29, 60, 92, 149 | 29: 598 (80%); 60: 447 (60%); 92: 299 (40%); 149: 150 (20%) | 29: 152 (20%); 60: 297 (40%); 92: 446 (59%); 149: 593 (79%) | OFFLINE |
| days_to_cover | backtest/signals/short_interest.py | 99.7% | 1.7023, 2.3145, 2.9978, 4.1126 | 1.7023: 599 (80%); 2.3145: 449 (60%); 2.9978: 301 (40%); 4.1126: 150 (20%) | 1.7023: 150 (20%); 2.3145: 300 (40%); 2.9978: 450 (60%); 4.1126: 599 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py | 100.0% | 9, 20, 28, 35 | 9: 611 (81%); 20: 476 (63%); 28: 336 (45%); 35: 165 (22%) | 9: 165 (22%); 20: 301 (40%); 28: 482 (64%); 35: 617 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +1 | 100.0% | 0, 2, 3 | 0: 751 (100%); 2: 456 (61%); 3: 277 (37%) | 0: 167 (22%); 2: 474 (63%); 3: 615 (82%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0143, -0.0011, 0.0112, 0.0226 | -0.0143: 601 (80%); -0.0011: 453 (60%); 0.0112: 304 (40%); 0.0226: 152 (20%) | -0.0143: 151 (20%); -0.0011: 363 (48%); 0.0112: 455 (61%); 0.0226: 603 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.6475, 26.0037, 26.79, 27.4428 | 24.6475: 602 (80%); 26.0037: 453 (60%); 26.79: 301 (40%); 27.4428: 160 (21%) | 24.6475: 152 (20%); 26.0037: 301 (40%); 26.79: 452 (60%); 27.4428: 613 (82%) | OFFLINE |
| gap_dn_pct | backtest/signals/technical.py | 100.0% | -0.716, -0.039, 0.439, 1.269 | -0.716: 601 (80%); -0.039: 451 (60%); 0.439: 301 (40%); 1.269: 152 (20%) | -0.716: 152 (20%); -0.039: 301 (40%); 0.439: 451 (60%); 1.269: 601 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/technical.py | 100.0% | -1.269, -0.439, 0.039, 0.716 | -1.269: 601 (80%); -0.439: 451 (60%); 0.039: 301 (40%); 0.716: 152 (20%) | -1.269: 152 (20%); -0.439: 301 (40%); 0.039: 451 (60%); 0.716: 601 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0379, 0.0021, 0.0266, 0.0805 | -0.0379: 601 (80%); 0.0021: 451 (60%); 0.0266: 304 (40%); 0.0805: 151 (20%) | -0.0379: 152 (20%); 0.0021: 304 (40%); 0.0266: 451 (60%); 0.0805: 601 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.0002, 8.5466, 8.883, 9.2922 | 8.0002: 603 (80%); 8.5466: 450 (60%); 8.883: 301 (40%); 9.2922: 150 (20%) | 8.0002: 148 (20%); 8.5466: 301 (40%); 8.883: 450 (60%); 9.2922: 601 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 746 (99%); 1: 235 (31%) | 0: 511 (68%); 1: 681 (91%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0 | 0: 598 (80%) | 0: 643 (86%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 99.3% | 0, 1 | 0: 746 (99%); 1: 277 (37%) | 0: 469 (62%); 1: 671 (89%) | OFFLINE |
| institutional_increased | backtest/data/signal_loader.py | 100.0% | 3, 7, 175, 279 | 3: 601 (80%); 7: 461 (61%); 175: 302 (40%); 279: 154 (21%) | 3: 180 (24%); 7: 310 (41%); 175: 451 (60%); 279: 602 (80%) | OFFLINE |
| institutional_new_positions | backtest/data/signal_loader.py | 100.0% | 1, 9, 96, 151 | 1: 613 (82%); 9: 454 (60%); 96: 301 (40%); 151: 151 (20%) | 1: 189 (25%); 9: 302 (40%); 96: 456 (61%); 151: 601 (80%) | OFFLINE |
| macd_12_26_9_hist | backtest/signals/technical.py (f-string template) | 100.0% | -1.2302, -0.5053, -0.1786, 0.1366 | -1.2302: 601 (80%); -0.5053: 451 (60%); -0.1786: 301 (40%); 0.1366: 151 (20%) | -1.2302: 151 (20%); -0.5053: 301 (40%); -0.1786: 451 (60%); 0.1366: 601 (80%) | OFFLINE |
| macd_12_26_9_line | backtest/signals/technical.py (f-string template) | 100.0% | -4.1774, -1.8782, -0.7633, -0.1013 | -4.1774: 601 (80%); -1.8782: 451 (60%); -0.7633: 301 (40%); -0.1013: 151 (20%) | -4.1774: 151 (20%); -1.8782: 301 (40%); -0.7633: 451 (60%); -0.1013: 601 (80%) | OFFLINE |
| macd_12_26_9_signal | backtest/signals/technical.py (f-string template) | 100.0% | -3.3694, -1.4899, -0.4881, 0.1839 | -3.3694: 601 (80%); -1.4899: 451 (60%); -0.4881: 301 (40%); 0.1839: 151 (20%) | -3.3694: 151 (20%); -1.4899: 301 (40%); -0.4881: 451 (60%); 0.1839: 601 (80%) | OFFLINE |
| macd_8_21_5_hist | backtest/signals/technical.py (f-string template) | 100.0% | -0.9298, -0.3633, -0.0899, 0.2065 | -0.9298: 601 (80%); -0.3633: 451 (60%); -0.0899: 301 (40%); 0.2065: 151 (20%) | -0.9298: 151 (20%); -0.3633: 301 (40%); -0.0899: 451 (60%); 0.2065: 602 (80%) | OFFLINE |
| macd_8_21_5_line | backtest/signals/technical.py (f-string template) | 100.0% | -4.8033, -2.1652, -0.9418, -0.1831 | -4.8033: 601 (80%); -2.1652: 451 (60%); -0.9418: 301 (40%); -0.1831: 151 (20%) | -4.8033: 151 (20%); -2.1652: 301 (40%); -0.9418: 451 (60%); -0.1831: 601 (80%) | OFFLINE |
| macd_8_21_5_signal | backtest/signals/technical.py (f-string template) | 100.0% | -4.2514, -1.7693, -0.7049, -0.0348 | -4.2514: 601 (80%); -1.7693: 451 (60%); -0.7049: 301 (40%); -0.0348: 151 (20%) | -4.2514: 151 (20%); -1.7693: 301 (40%); -0.7049: 451 (60%); -0.0348: 601 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 29.01, 36.99, 44.69, 53.37 | 29.01: 602 (80%); 36.99: 451 (60%); 44.69: 301 (40%); 53.37: 151 (20%) | 29.01: 151 (20%); 36.99: 301 (40%); 44.69: 452 (60%); 53.37: 601 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.7% | 0.009, 0.0219, 0.0418, 0.0793 | 0.009: 599 (80%); 0.0219: 449 (60%); 0.0418: 301 (40%); 0.0793: 150 (20%) | 0.009: 150 (20%); 0.0219: 300 (40%); 0.0418: 448 (60%); 0.0793: 599 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 751 (100%); 1: 577 (77%); 3: 346 (46%); 8: 170 (23%) | 0: 174 (23%); 1: 325 (43%); 3: 455 (61%); 8: 603 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.25 | 0: 751 (100%); 0.25: 164 (22%) | 0: 457 (61%); 0.25: 607 (81%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.375, 0.6 | 0: 751 (100%); 0.375: 303 (40%); 0.6: 161 (21%) | 0: 308 (41%); 0.375: 453 (60%); 0.6: 601 (80%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 6 | 0: 751 (100%); 1: 514 (68%); 2: 364 (48%); 6: 170 (23%) | 0: 237 (32%); 1: 387 (52%); 2: 461 (61%); 6: 617 (82%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 8 | 0: 751 (100%); 1: 577 (77%); 3: 346 (46%); 8: 170 (23%) | 0: 174 (23%); 1: 325 (43%); 3: 455 (61%); 8: 603 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 6 | 0: 751 (100%); 1: 522 (70%); 2: 388 (52%); 6: 168 (22%) | 0: 229 (30%); 1: 363 (48%); 2: 454 (60%); 6: 620 (83%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1534, 0.3333, 0.6 | 0: 644 (86%); 0.1534: 451 (60%); 0.3333: 302 (40%); 0.6: 151 (20%) | 0: 215 (29%); 0.1534: 301 (40%); 0.3333: 456 (61%); 0.6: 603 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.4545 | 0: 630 (84%); 0.4545: 151 (20%) | 0: 464 (62%); 0.4545: 601 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2, 0.5 | 0: 633 (84%); 0.2: 301 (40%); 0.5: 179 (24%) | 0: 390 (52%); 0.2: 462 (62%); 0.5: 604 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2, 0.5 | 0: 633 (84%); 0.2: 301 (40%); 0.5: 179 (24%) | 0: 390 (52%); 0.2: 462 (62%); 0.5: 604 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py | 100.0% | -0.2202, 0, 0.0692 | -0.2202: 601 (80%); 0: 527 (70%); 0.0692: 151 (20%) | -0.2202: 151 (20%); 0: 582 (77%); 0.0692: 601 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py | 100.0% | -0.6928, -0.2474, 0.0976, 1.3119 | -0.6928: 601 (80%); -0.2474: 451 (60%); 0.0976: 302 (40%); 1.3119: 151 (20%) | -0.6928: 153 (20%); -0.2474: 301 (40%); 0.0976: 451 (60%); 1.3119: 601 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py | 100.0% | 2, 4, 7, 10 | 2: 609 (81%); 4: 477 (64%); 7: 308 (41%); 10: 170 (23%) | 2: 215 (29%); 4: 339 (45%); 7: 499 (66%); 10: 615 (82%) | OFFLINE |
| pct_change_10d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.1059, -0.0659, -0.032, 0.0096 | -0.1059: 601 (80%); -0.0659: 451 (60%); -0.032: 299 (40%); 0.0096: 150 (20%) | -0.1059: 150 (20%); -0.0659: 300 (40%); -0.032: 452 (60%); 0.0096: 601 (80%) | OFFLINE |
| pct_change_20d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.1413, -0.0926, -0.0479, 0.0073 | -0.1413: 600 (80%); -0.0926: 450 (60%); -0.0479: 301 (40%); 0.0073: 151 (20%) | -0.1413: 151 (20%); -0.0926: 301 (40%); -0.0479: 450 (60%); 0.0073: 600 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/technical.py (f-string template) +1 | 100.0% | -0.0778, -0.0468, -0.0229, 0.0192 | -0.0778: 601 (80%); -0.0468: 451 (60%); -0.0229: 300 (40%); 0.0192: 150 (20%) | -0.0778: 150 (20%); -0.0468: 300 (40%); -0.0229: 451 (60%); 0.0192: 601 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/technical.py | 100.0% | -31.213, -19.137, -7.801, 7.374 | -31.213: 601 (80%); -19.137: 451 (60%); -7.801: 301 (40%); 7.374: 151 (20%) | -31.213: 151 (20%); -19.137: 301 (40%); -7.801: 451 (60%); 7.374: 601 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.537, 0.6765, 0.8086, 0.9113 | 0.537: 601 (80%); 0.6765: 451 (60%); 0.8086: 301 (40%); 0.9113: 151 (20%) | 0.537: 151 (20%); 0.6765: 301 (40%); 0.8086: 451 (60%); 0.9113: 601 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -4.1265, -2.493, -1.3208, -0.1709 | -4.1265: 601 (80%); -2.493: 451 (60%); -1.3208: 301 (40%); -0.1709: 151 (20%) | -4.1265: 151 (20%); -2.493: 301 (40%); -1.3208: 451 (60%); -0.1709: 601 (80%) | OFFLINE |
| ppo_hist | backtest/signals/technical.py | 100.0% | -1.2461, -0.7501, -0.3587, 0.2182 | -1.2461: 601 (80%); -0.7501: 451 (60%); -0.3587: 301 (40%); 0.2182: 151 (20%) | -1.2461: 151 (20%); -0.7501: 301 (40%); -0.3587: 451 (60%); 0.2182: 601 (80%) | OFFLINE |
| ppo_signal | backtest/signals/technical.py | 100.0% | -3.4337, -1.9331, -0.9068, 0.2724 | -3.4337: 601 (80%); -1.9331: 451 (60%); -0.9068: 301 (40%); 0.2724: 151 (20%) | -3.4337: 151 (20%); -1.9331: 301 (40%); -0.9068: 451 (60%); 0.2724: 601 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -12.318, -7.56, -3.76, 0.305 | -12.318: 601 (80%); -7.56: 451 (60%); -3.76: 301 (40%); 0.305: 151 (20%) | -12.318: 151 (20%); -7.56: 301 (40%); -3.76: 451 (60%); 0.305: 601 (80%) | OFFLINE |
| rsi_14 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 32.41, 38.3, 43.53, 49.17 | 32.41: 601 (80%); 38.3: 451 (60%); 43.53: 301 (40%); 49.17: 151 (20%) | 32.41: 151 (20%); 38.3: 301 (40%); 43.53: 451 (60%); 49.17: 601 (80%) | OFFLINE |
| rsi_2 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 21.48, 41.96, 58.56, 76.02 | 21.48: 601 (80%); 41.96: 451 (60%); 58.56: 301 (40%); 76.02: 151 (20%) | 21.48: 151 (20%); 41.96: 301 (40%); 58.56: 451 (60%); 76.02: 601 (80%) | OFFLINE |
| rsi_21 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 35.15, 40.47, 44.25, 48.87 | 35.15: 601 (80%); 40.47: 451 (60%); 44.25: 301 (40%); 48.87: 151 (20%) | 35.15: 151 (20%); 40.47: 301 (40%); 44.25: 452 (60%); 48.87: 601 (80%) | OFFLINE |
| rsi_9 | backtest/signals/polars_panel.py (f-string template) +2 | 100.0% | 28.1, 36.43, 42.21, 50.51 | 28.1: 602 (80%); 36.43: 451 (60%); 42.21: 301 (40%); 50.51: 151 (20%) | 28.1: 151 (20%); 36.43: 301 (40%); 42.21: 452 (60%); 50.51: 601 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0313, 0.0498, 0.0651, 0.0931 | 0.0313: 602 (80%); 0.0498: 453 (60%); 0.0651: 301 (40%); 0.0931: 152 (20%) | 0.0313: 152 (20%); 0.0498: 302 (40%); 0.0651: 451 (60%); 0.0931: 601 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0858, -0.0569, -0.0434, -0.0333 | -0.0858: 602 (80%); -0.0569: 456 (61%); -0.0434: 321 (43%); -0.0333: 151 (20%) | -0.0858: 153 (20%); -0.0569: 307 (41%); -0.0434: 469 (62%); -0.0333: 601 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 1 | 0: 751 (100%); 1: 193 (26%) | 0: 558 (74%); 1: 645 (86%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.7% | 27, 42, 64, 68.4 | 27: 600 (80%); 42: 451 (60%); 64: 317 (42%); 68.4: 150 (20%) | 27: 157 (21%); 42: 305 (41%); 64: 465 (62%); 68.4: 599 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/short_interest.py | 99.7% | 0.0163, 0.0253, 0.0372, 0.0583 | 0.0163: 599 (80%); 0.0253: 450 (60%); 0.0372: 300 (40%); 0.0583: 150 (20%) | 0.0163: 150 (20%); 0.0253: 299 (40%); 0.0372: 449 (60%); 0.0583: 599 (80%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/smc_ict.py | 100.0% | 0.1051, 0.1821, 0.291, 0.475 | 0.1051: 601 (80%); 0.1821: 451 (60%); 0.291: 301 (40%); 0.475: 151 (20%) | 0.1051: 151 (20%); 0.1821: 301 (40%); 0.291: 451 (60%); 0.475: 601 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/smc_ict.py | 100.0% | 28.3, 64.7, 98.3, 150.3 | 28.3: 601 (80%); 64.7: 451 (60%); 98.3: 301 (40%); 150.3: 151 (20%) | 28.3: 151 (20%); 64.7: 302 (40%); 98.3: 451 (60%); 150.3: 601 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/technical.py | 100.0% | -7.74, -3.495, -1.38, 0.21 | -7.74: 602 (80%); -3.495: 451 (60%); -1.38: 301 (40%); 0.21: 151 (20%) | -7.74: 152 (20%); -3.495: 301 (40%); -1.38: 451 (60%); 0.21: 601 (80%) | OFFLINE |
| stoch_d | backtest/signals/technical.py | 100.0% | 10.72, 16.74, 28.02, 47.93 | 10.72: 601 (80%); 16.74: 451 (60%); 28.02: 301 (40%); 47.93: 151 (20%) | 10.72: 151 (20%); 16.74: 301 (40%); 28.02: 451 (60%); 47.93: 601 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 9.29, 17.63, 27.38, 46.77 | 9.29: 601 (80%); 17.63: 451 (60%); 27.38: 301 (40%); 46.77: 151 (20%) | 9.29: 151 (20%); 17.63: 301 (40%); 27.38: 451 (60%); 46.77: 601 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 5.56, 17.57, 35.91, 71.44 | 5.56: 601 (80%); 17.57: 451 (60%); 35.91: 301 (40%); 71.44: 151 (20%) | 5.56: 151 (20%); 17.57: 301 (40%); 35.91: 451 (60%); 71.44: 601 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 5.54, 22.78, 44.27, 80.86 | 5.54: 601 (80%); 22.78: 451 (60%); 44.27: 301 (40%); 80.86: 151 (20%) | 5.54: 151 (20%); 22.78: 301 (40%); 44.27: 451 (60%); 80.86: 601 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 8, 12, 17 | 5: 624 (83%); 8: 475 (63%); 12: 331 (44%); 17: 178 (24%) | 5: 173 (23%); 8: 312 (42%); 12: 457 (61%); 17: 609 (81%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 14, 17 | 5: 615 (82%); 9: 476 (63%); 14: 315 (42%); 17: 176 (23%) | 5: 171 (23%); 9: 301 (40%); 14: 478 (64%); 17: 637 (85%) | OFFLINE |
| uo | backtest/signals/technical.py | 100.0% | 36.75, 41.96, 46.72, 52.58 | 36.75: 601 (80%); 41.96: 451 (60%); 46.72: 301 (40%); 52.58: 151 (20%) | 36.75: 151 (20%); 41.96: 301 (40%); 46.72: 451 (60%); 52.58: 601 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.246, 0.6071, 0.8175, 0.9325 | 0.246: 601 (80%); 0.6071: 451 (60%); 0.8175: 303 (40%); 0.9325: 154 (21%) | 0.246: 152 (20%); 0.6071: 302 (40%); 0.8175: 454 (60%); 0.9325: 607 (81%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 16.64, 19.49, 22.99, 29.65 | 16.64: 601 (80%); 19.49: 452 (60%); 22.99: 303 (40%); 29.65: 151 (20%) | 16.64: 151 (20%); 19.49: 302 (40%); 22.99: 452 (60%); 29.65: 606 (81%) | OFFLINE |
| vix_value | backtest/signals/technical.py +1 | 100.0% | 16.64, 19.49, 22.99, 29.65 | 16.64: 601 (80%); 19.49: 452 (60%); 22.99: 303 (40%); 29.65: 151 (20%) | 16.64: 151 (20%); 19.49: 302 (40%); 22.99: 452 (60%); 29.65: 606 (81%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8746, 0.9135, 0.9554, 0.9955 | 0.8746: 601 (80%); 0.9135: 451 (60%); 0.9554: 302 (40%); 0.9955: 153 (20%) | 0.8746: 151 (20%); 0.9135: 301 (40%); 0.9554: 456 (61%); 0.9955: 601 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.73, 0.89, 1.09, 1.44 | 0.73: 611 (81%); 0.89: 455 (61%); 1.09: 306 (41%); 1.44: 155 (21%) | 0.73: 153 (20%); 0.89: 301 (40%); 1.09: 452 (60%); 1.44: 602 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/volume_profile.py | 100.0% | 0.0233, 0.0537, 0.0894, 0.1413 | 0.0233: 601 (80%); 0.0537: 453 (60%); 0.0894: 302 (40%); 0.1413: 151 (20%) | 0.0233: 151 (20%); 0.0537: 301 (40%); 0.0894: 451 (60%); 0.1413: 601 (80%) | OFFLINE |
| vwap | backtest/signals/technical.py | 100.0% | 38.7788, 72.1062, 111.8781, 185.976 | 38.7788: 601 (80%); 72.1062: 451 (60%); 111.8781: 301 (40%); 185.976: 151 (20%) | 38.7788: 151 (20%); 72.1062: 301 (40%); 111.8781: 451 (60%); 185.976: 601 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 37.4778, 67.8974, 104.2302, 182.4954 | 37.4778: 601 (80%); 67.8974: 451 (60%); 104.2302: 301 (40%); 182.4954: 151 (20%) | 37.4778: 151 (20%); 67.8974: 301 (40%); 104.2302: 451 (60%); 182.4954: 601 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 35.4289, 62.697, 98.1766, 173.3631 | 35.4289: 601 (80%); 62.697: 451 (60%); 98.1766: 301 (40%); 173.3631: 151 (20%) | 35.4289: 151 (20%); 62.697: 301 (40%); 98.1766: 451 (60%); 173.3631: 601 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 40.2254, 75.6354, 116.7095, 194.4712 | 40.2254: 601 (80%); 75.6354: 451 (60%); 116.7095: 301 (40%); 194.4712: 151 (20%) | 40.2254: 151 (20%); 75.6354: 301 (40%); 116.7095: 451 (60%); 194.4712: 601 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 41.589, 77.6671, 121.906, 203.3791 | 41.589: 601 (80%); 77.6671: 451 (60%); 121.906: 301 (40%); 203.3791: 151 (20%) | 41.589: 151 (20%); 77.6671: 301 (40%); 121.906: 451 (60%); 203.3791: 601 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 751 (100%) | 0: 653 (87%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 751 (100%) | 0: 676 (90%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.1393, -0.0876, -0.0473, 0.0038 | -0.1393: 601 (80%); -0.0876: 451 (60%); -0.0473: 302 (40%); 0.0038: 151 (20%) | -0.1393: 151 (20%); -0.0876: 301 (40%); -0.0473: 451 (60%); 0.0038: 601 (80%) | OFFLINE |
| williams_r | backtest/signals/technical.py | 100.0% | -86.26, -78.07, -66.67, -43.59 | -86.26: 601 (80%); -78.07: 451 (60%); -66.67: 302 (40%); -43.59: 151 (20%) | -86.26: 151 (20%); -78.07: 302 (40%); -66.67: 451 (60%); -43.59: 601 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 99.7% | 0.6289, 0.9387, 1.1402, 1.5471 | 0.6289: 599 (80%); 0.9387: 449 (60%); 1.1402: 300 (40%); 1.5471: 150 (20%) | 0.6289: 150 (20%); 0.9387: 300 (40%); 1.1402: 449 (60%); 1.5471: 599 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 99.7% | 4, 6, 8, 10 | 4: 622 (83%); 6: 489 (65%); 8: 338 (45%); 10: 166 (22%) | 4: 191 (25%); 6: 332 (44%); 8: 489 (65%); 10: 749 (100%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py | 99.6% | 0.2347, 0.2879, 0.3434, 0.4286 | 0.2347: 598 (80%); 0.2879: 449 (60%); 0.3434: 299 (40%); 0.4286: 150 (20%) | 0.2347: 150 (20%); 0.2879: 300 (40%); 0.3434: 449 (60%); 0.4286: 598 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py | 99.6% | 5, 7.8, 9, 10 | 5: 634 (84%); 7.8: 449 (60%); 9: 329 (44%); 10: 183 (24%) | 5: 161 (21%); 7.8: 299 (40%); 9: 565 (75%); 10: 748 (100%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 99.7% | 0.0265, 0.0368, 0.0497, 0.073 | 0.0265: 600 (80%); 0.0368: 451 (60%); 0.0497: 301 (40%); 0.073: 151 (20%) | 0.0265: 153 (20%); 0.0368: 301 (40%); 0.0497: 450 (60%); 0.073: 600 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 99.7% | 4, 6, 8, 9 | 4: 619 (82%); 6: 517 (69%); 8: 355 (47%); 9: 250 (33%) | 4: 180 (24%); 6: 307 (41%); 8: 499 (66%); 9: 615 (82%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.7% | -0.3006, -0.1679, -0.0294, 0.1276 | -0.3006: 599 (80%); -0.1679: 450 (60%); -0.0294: 300 (40%); 0.1276: 150 (20%) | -0.3006: 150 (20%); -0.1679: 300 (40%); -0.0294: 450 (60%); 0.1276: 599 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.7% | 1, 3, 4, 7 | 1: 749 (100%); 3: 455 (61%); 4: 366 (49%); 7: 182 (24%) | 1: 181 (24%); 3: 383 (51%); 4: 460 (61%); 7: 605 (81%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_5_02_filed_within_7d | 4.4% |
| above_avwap_20high | 18.2% |
| above_avwap_20low | 80.3% |
| above_avwap_252low | 60.9% |
| above_avwap_50low | 70.2% |
| above_cam_r3 | 54.5% |
| above_cam_r4 | 29.7% |
| above_cpr | 64.3% |
| above_pivot | 69.6% |
| above_prev_high | 31.3% |
| above_prev_high_clearance_atr_05 | 9.2% |
| above_prev_low | 91.7% |
| above_r1 | 30.6% |
| above_r2 | 11.3% |
| above_vwap | 27.6% |
| above_wood_p | 55.3% |
| ad_rising | 43.9% |
| adx_cross_up | 3.7% |
| adx_cross_up_20 | 4.9% |
| adx_di_bear | 82.7% |
| adx_di_bull | 17.3% |
| adx_strong | 8.1% |
| adx_trending | 45.7% |
| ao_cross_dn | 5.1% |
| ao_cross_up | 1.2% |
| ao_positive | 19.3% |
| ao_twin_peaks_bull | 5.3% |
| at_key_fib | 10.1% |
| at_key_fib_wide | 25.7% |
| avwap_20high_loss_recent_3d | 10.3% |
| avwap_20high_reclaim_recent_3d | 12.1% |
| avwap_20low_loss_recent_3d | 13.4% |
| avwap_20low_reclaim_recent_3d | 40.7% |
| avwap_252low_loss_recent_3d | 13.1% |
| avwap_252low_reclaim_recent_3d | 20.9% |
| avwap_50low_loss_recent_3d | 15.6% |
| avwap_50low_reclaim_recent_3d | 32.4% |
| bb_10_20_above_mid | 27.6% |
| bb_10_20_expanding | 57.0% |
| bb_10_20_pctb_gt_75 | 13.2% |
| bb_10_20_pctb_gt_8 | 10.7% |
| bb_10_20_pctb_gt_85 | 7.3% |
| bb_10_20_pctb_gt_9 | 4.7% |
| bb_10_20_pctb_gt_95 | 3.3% |
| bb_10_20_pctb_lt_05 | 3.5% |
| bb_10_20_pctb_lt_1 | 9.6% |
| bb_10_20_pctb_lt_15 | 16.8% |
| bb_10_20_pctb_lt_2 | 26.1% |
| bb_10_20_pctb_lt_25 | 38.7% |
| bb_10_20_reclaim_from_lower_recent_3d | 28.0% |
| bb_10_20_reclaim_from_upper_recent_3d | 4.7% |
| bb_10_20_squeeze | 12.6% |
| bb_10_20_touch_lower | 2.5% |
| bb_10_20_touch_upper | 3.2% |
| bb_20_15_above_mid | 20.4% |
| bb_20_15_expanding | 60.7% |
| bb_20_15_pctb_gt_75 | 11.3% |
| bb_20_15_pctb_gt_8 | 10.0% |
| bb_20_15_pctb_gt_85 | 8.8% |
| bb_20_15_pctb_gt_9 | 7.3% |
| bb_20_15_pctb_gt_95 | 6.4% |
| bb_20_15_pctb_lt_05 | 35.3% |
| bb_20_15_pctb_lt_1 | 44.1% |
| bb_20_15_pctb_lt_15 | 50.6% |
| bb_20_15_pctb_lt_2 | 57.0% |
| bb_20_15_pctb_lt_25 | 62.1% |
| bb_20_15_reclaim_from_lower_recent_3d | 30.4% |
| bb_20_15_reclaim_from_upper_recent_3d | 3.2% |
| bb_20_15_squeeze | 16.5% |
| bb_20_15_touch_lower | 33.4% |
| bb_20_15_touch_upper | 6.4% |
| bb_20_20_above_mid | 20.4% |
| bb_20_20_expanding | 60.7% |
| bb_20_20_pctb_gt_75 | 9.1% |
| bb_20_20_pctb_gt_8 | 7.3% |
| bb_20_20_pctb_gt_85 | 6.4% |
| bb_20_20_pctb_gt_9 | 4.7% |
| bb_20_20_pctb_gt_95 | 4.0% |
| bb_20_20_pctb_lt_05 | 16.8% |
| bb_20_20_pctb_lt_1 | 24.5% |
| bb_20_20_pctb_lt_15 | 32.8% |
| bb_20_20_pctb_lt_2 | 44.1% |
| bb_20_20_pctb_lt_25 | 52.5% |
| bb_20_20_reclaim_from_lower_recent_3d | 29.7% |
| bb_20_20_reclaim_from_upper_recent_3d | 1.9% |
| bb_20_20_squeeze | 5.5% |
| bb_20_20_touch_lower | 14.8% |
| bb_20_20_touch_upper | 3.7% |
| bearish_pin_bar | 5.5% |
| below_avwap_20high | 81.8% |
| below_avwap_20low | 19.7% |
| below_avwap_252low | 39.1% |
| below_avwap_50low | 29.8% |
| below_cam_s3 | 8.5% |
| below_cam_s4 | 3.7% |
| below_cpr | 30.2% |
| below_ema_20 | 80.3% |
| below_ema_200 | 83.2% |
| below_ema_200_break_recent_5d | 12.7% |
| below_ema_20_break_recent_5d | 26.6% |
| below_ema_21 | 80.8% |
| below_ema_21_break_recent_5d | 26.5% |
| below_ema_50 | 84.7% |
| below_ema_50_break_recent_5d | 23.0% |
| below_ema_9 | 72.4% |
| below_ema_9_break_recent_5d | 30.6% |
| below_prev_high | 68.4% |
| below_prev_low | 8.1% |
| below_prev_low_clearance_atr_05 | 2.0% |
| below_s1 | 4.9% |
| below_s2 | 1.9% |
| below_sma_20 | 79.6% |
| below_sma_200 | 81.9% |
| below_sma_21 | 79.8% |
| below_sma_50 | 81.6% |
| below_sma_9 | 71.4% |
| below_vwap | 72.4% |
| break_52w_high | 0.1% |
| break_52w_high_confirmed_today | 0.1% |
| break_52w_low | 1.6% |
| bullish_engulfing | 11.7% |
| bullish_pin_bar | 7.2% |
| capitulation_recent_3d | 1.3% |
| ceo_buy | 1.6% |
| cfo_buy | 0.4% |
| chandelier_long_bullish | 35.3% |
| chandelier_long_flip_dn | 0.9% |
| chandelier_short_bearish | 85.1% |
| chandelier_short_flip_up | 4.8% |
| classification_change_from_tech | 50.0% |
| classification_change_to_defensive | 50.0% |
| close_in_bottom_40pct_of_range | 8.3% |
| close_in_top_40pct_of_range | 72.7% |
| cluster_buy | 1.1% |
| cmf_cross_dn | 1.9% |
| cmf_cross_up | 7.1% |
| cmf_negative | 62.1% |
| cmf_positive | 37.9% |
| concentrated_sell | 3.6% |
| cpr_narrow | 87.0% |
| cpr_narrow_tight | 23.0% |
| cup_handle_detected | 9.2% |
| cup_handle_neckline_break_retest_long | 1.7% |
| dc10_breakout_dn | 7.1% |
| dc10_breakout_dn_1pct | 14.4% |
| dc10_breakout_up | 5.1% |
| dc10_breakout_up_1pct | 7.2% |
| dc10_new_high | 7.5% |
| dc10_strong_breakout_dn | 1.2% |
| dc10_strong_breakout_up | 1.7% |
| dc20_breakout_dn | 6.1% |
| dc20_breakout_up | 3.1% |
| dc20_new_high | 4.3% |
| dc20_resistance_break_retest_strong | 3.7% |
| dc20_support_break_retest_strong | 38.2% |
| defensive_leadership | 63.8% |
| director_only_buy | 5.4% |
| doji | 4.7% |
| double_bottom_detected | 13.0% |
| double_top_detected | 13.0% |
| dpi_elevated | 43.8% |
| drying_volume_on_up_turn | 53.5% |
| ema_20_50_bearish | 77.1% |
| ema_20_50_bullish | 22.9% |
| ema_20_50_death_cross | 1.5% |
| ema_20_50_golden_cross | 0.8% |
| ema_50_200_bearish | 72.0% |
| ema_50_200_bullish | 28.0% |
| ema_50_200_death_cross | 0.7% |
| ema_50_200_golden_cross | 0.1% |
| ema_9_21_bearish | 82.7% |
| ema_9_21_bullish | 17.3% |
| ema_9_21_death_cross | 2.0% |
| ema_9_21_golden_cross | 1.2% |
| flag_bear_break_retest_short | 1.5% |
| flag_bear_broke | 1.5% |
| flag_bull_break_retest_long | 0.3% |
| flag_bull_broke | 0.3% |
| force_index_cross_dn | 1.7% |
| force_index_cross_up | 6.9% |
| force_index_positive | 23.3% |
| gap_dn_1_5pct | 16.2% |
| gap_dn_2pct | 12.0% |
| gap_up_1_5pct | 7.1% |
| gap_up_2pct | 4.1% |
| hammer | 4.8% |
| head_shoulders_bottom_detected | 4.7% |
| head_shoulders_top_detected | 6.8% |
| house_cluster_buy | 2.7% |
| house_cluster_sell | 2.8% |
| htf_aligned_bear | 67.5% |
| htf_aligned_bull | 6.4% |
| htf_disagreement | 2.1% |
| hull_bearish | 75.8% |
| hull_bullish | 24.2% |
| hull_flip_dn | 1.9% |
| hull_flip_up | 3.6% |
| ichi_above_cloud | 14.1% |
| ichi_above_cloud_break_recent_5d | 6.1% |
| ichi_below_cloud | 73.6% |
| ichi_below_cloud_break_recent_5d | 16.4% |
| ichi_cloud_thick | 86.3% |
| ichi_tk_bearish | 72.8% |
| ichi_tk_bullish | 20.6% |
| ichi_tk_cross_dn | 3.1% |
| ichi_tk_cross_up | 1.1% |
| ichi_weekly_above_cloud | 16.7% |
| ichi_weekly_below_cloud | 59.0% |
| ichi_weekly_in_cloud | 24.4% |
| in_reversal_window | 3.0% |
| inside_bar | 16.5% |
| inside_cpr | 6.3% |
| inside_kc | 74.2% |
| insider_cluster_active | 24.6% |
| institutional_buy | 87.7% |
| institutional_negative | 5.6% |
| institutional_persistence_growing | 54.7% |
| institutional_persistence_strong | 66.8% |
| institutional_strong_buy | 80.3% |
| inverted_cup_handle_detected | 5.6% |
| is_friday | 18.1% |
| is_halloween_period | 59.9% |
| is_january | 4.4% |
| is_january_extended | 4.8% |
| is_monday | 22.2% |
| is_pre_holiday | 4.9% |
| is_summer_period | 40.1% |
| is_totm_window | 30.4% |
| is_totm_window_first_day | 7.3% |
| is_week_open | 23.3% |
| kc_touch_lower | 26.6% |
| kc_touch_upper | 3.5% |
| large_dollar_buy | 1.7% |
| macd_12_26_9_bearish | 73.6% |
| macd_12_26_9_bullish | 26.4% |
| macd_12_26_9_crossover_dn | 2.4% |
| macd_12_26_9_crossover_up | 3.3% |
| macd_8_21_5_bearish | 68.7% |
| macd_8_21_5_bullish | 31.3% |
| macd_8_21_5_crossover_dn | 1.5% |
| macd_8_21_5_crossover_up | 5.1% |
| marubozu_bull | 1.1% |
| mfi_broad_overbought | 3.6% |
| mfi_broad_oversold | 22.2% |
| mfi_overbought | 0.8% |
| mfi_oversold | 6.8% |
| monthly_above_sma_12 | 19.7% |
| monthly_above_sma_6 | 17.9% |
| monthly_bias_bear | 73.6% |
| monthly_bias_bull | 11.2% |
| monthly_momentum_pos | 26.3% |
| morning_star | 8.3% |
| near_52w_high | 0.5% |
| near_52w_high_95pct | 0.9% |
| near_52w_high_retest_long | 0.4% |
| near_52w_low | 6.7% |
| near_52w_low_105pct | 18.4% |
| near_avwap_20high_atr_05x | 22.0% |
| near_avwap_20high_atr_10x | 47.0% |
| near_avwap_20high_atr_15x | 66.2% |
| near_avwap_20high_atr_20x | 81.9% |
| near_avwap_20low_atr_05x | 51.4% |
| near_avwap_20low_atr_10x | 76.9% |
| near_avwap_20low_atr_15x | 86.4% |
| near_avwap_20low_atr_20x | 93.6% |
| near_avwap_252low_atr_05x | 28.7% |
| near_avwap_252low_atr_10x | 45.0% |
| near_avwap_252low_atr_15x | 58.1% |
| near_avwap_252low_atr_20x | 68.4% |
| near_avwap_50low_atr_05x | 42.6% |
| near_avwap_50low_atr_10x | 66.4% |
| near_avwap_50low_atr_15x | 79.7% |
| near_avwap_50low_atr_20x | 88.5% |
| near_cam_r3 | 18.4% |
| near_cam_s3 | 5.1% |
| near_cam_s4 | 1.5% |
| near_fib_236 | 1.2% |
| near_fib_382 | 2.4% |
| near_fib_500 | 4.0% |
| near_fib_618 | 3.7% |
| near_fib_786 | 8.8% |
| near_pivot | 13.2% |
| near_prev_close | 10.7% |
| near_prev_high | 10.3% |
| near_prev_low | 4.7% |
| near_r1 | 13.0% |
| near_r1_wide | 53.5% |
| near_r2 | 4.8% |
| near_r2_wide | 28.4% |
| near_s1 | 2.4% |
| near_s1_wide | 19.6% |
| near_s2 | 0.3% |
| near_s2_wide | 5.1% |
| near_s3 | 0.1% |
| near_wood_r1 | 7.6% |
| near_wood_s1 | 8.9% |
| news_uses_polygon_score | 29.4% |
| obv_bearish | 72.6% |
| obv_bullish | 27.4% |
| obv_diverge_bull | 10.4% |
| obv_falling | 63.4% |
| obv_rising | 36.6% |
| outside_bar | 10.8% |
| pead_negative_surprise | 24.1% |
| pead_positive_surprise | 18.2% |
| pin_bar | 12.6% |
| po3_bullish | 26.2% |
| po3_sweep_above_prior_high | 50.7% |
| po3_sweep_below_prior_low | 49.4% |
| ppo_bullish | 24.9% |
| ppo_crossover_dn | 2.1% |
| ppo_crossover_up | 2.9% |
| pre_fomc_d0 | 2.1% |
| pre_fomc_d1 | 1.5% |
| pre_fomc_window | 3.6% |
| price_above_dema | 38.1% |
| price_above_ema_20 | 19.7% |
| price_above_ema_200 | 16.8% |
| price_above_ema_200_break_recent_5d | 5.3% |
| price_above_ema_20_break_recent_5d | 13.8% |
| price_above_ema_21 | 19.2% |
| price_above_ema_21_break_recent_5d | 13.4% |
| price_above_ema_50 | 15.3% |
| price_above_ema_50_break_recent_5d | 8.7% |
| price_above_ema_9 | 27.6% |
| price_above_ema_9_break_recent_5d | 22.4% |
| price_above_hull | 46.1% |
| price_above_sma_200 | 18.1% |
| price_above_sma_21 | 20.2% |
| price_above_sma_50 | 18.4% |
| price_above_tema | 49.8% |
| price_below_dema | 61.9% |
| price_below_hull | 53.9% |
| price_below_tema | 50.2% |
| psar_bullish | 23.8% |
| psar_flip_dn | 1.1% |
| psar_flip_up | 3.5% |
| r1_break_retest_long | 28.2% |
| recent_capitulation_at_s3 | 0.7% |
| resistance_break_retest | 5.5% |
| risk_off_regime_bond_signal | 32.8% |
| risk_off_regime_bond_signal_strong | 16.6% |
| risk_off_regime_gold_signal | 45.0% |
| risk_on_regime_bond_signal | 31.4% |
| risk_on_regime_bond_signal_strong | 14.9% |
| roc_positive | 20.8% |
| roc_turning_dn | 2.3% |
| roc_turning_up | 4.9% |
| rsi_14_bullish | 17.7% |
| rsi_14_cross_dn_overbought_recent_3d | 0.7% |
| rsi_14_cross_up_extreme_os_recent_3d | 1.9% |
| rsi_14_cross_up_oversold_recent_3d | 15.2% |
| rsi_14_extreme_ob | 0.1% |
| rsi_14_extreme_os | 1.1% |
| rsi_14_overbought | 1.2% |
| rsi_14_oversold | 15.8% |
| rsi_14_rising | 79.8% |
| rsi_21_bullish | 17.0% |
| rsi_21_cross_dn_overbought_recent_3d | 0.1% |
| rsi_21_cross_up_extreme_os_recent_3d | 0.3% |
| rsi_21_cross_up_oversold_recent_3d | 8.7% |
| rsi_21_extreme_os | 0.3% |
| rsi_21_overbought | 0.3% |
| rsi_21_oversold | 6.1% |
| rsi_21_rising | 79.8% |
| rsi_2_bullish | 49.4% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 11.9% |
| rsi_2_cross_dn_overbought_recent_3d | 16.2% |
| rsi_2_cross_up_extreme_os_recent_3d | 58.5% |
| rsi_2_cross_up_oversold_recent_3d | 53.9% |
| rsi_2_extreme_ob | 16.1% |
| rsi_2_extreme_os | 18.6% |
| rsi_2_overbought | 26.9% |
| rsi_2_oversold | 29.0% |
| rsi_2_rising | 79.8% |
| rsi_9_bullish | 20.9% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 0.4% |
| rsi_9_cross_dn_overbought_recent_3d | 1.5% |
| rsi_9_cross_up_extreme_os_recent_3d | 13.8% |
| rsi_9_cross_up_oversold_recent_3d | 24.2% |
| rsi_9_extreme_ob | 0.7% |
| rsi_9_extreme_os | 4.9% |
| rsi_9_overbought | 3.5% |
| rsi_9_oversold | 24.0% |
| rsi_9_rising | 79.8% |
| s1_break_retest_short | 76.8% |
| sc_13d_filed_within_30d | 3.2% |
| sc_13g_filed_within_30d | 2.6% |
| sector_outperforming_spy | 50.0% |
| sector_underperforming_spy | 50.0% |
| shooting_star | 4.5% |
| sma_20_50_bullish | 29.6% |
| sma_20_50_golden_cross | 0.7% |
| sma_50_200_bullish | 34.1% |
| sma_9_21_bullish | 23.7% |
| sma_9_21_golden_cross | 0.7% |
| smc_bos_bearish | 24.0% |
| smc_bos_bullish | 8.3% |
| smc_bos_retest_long | 1.7% |
| smc_bos_retest_short | 4.1% |
| smc_breaker_block_bearish | 29.4% |
| smc_breaker_block_bullish | 12.1% |
| smc_choch_bearish | 10.9% |
| smc_choch_bullish | 1.9% |
| smc_equal_highs_swept | 3.3% |
| smc_equal_lows_swept | 9.1% |
| smc_fvg_bearish_active | 69.6% |
| smc_fvg_bullish_active | 21.3% |
| smc_fvg_retest_long_zone | 0.7% |
| smc_fvg_retest_short_zone | 22.2% |
| smc_in_discount_zone | 88.7% |
| smc_in_premium_zone | 27.3% |
| smc_inverse_fvg_bearish | 94.5% |
| smc_inverse_fvg_bullish | 52.2% |
| smc_liquidity_swept_dn | 2.1% |
| smc_liquidity_swept_up | 2.4% |
| smc_mitigation_block_long | 2.3% |
| smc_mitigation_block_short | 1.1% |
| smc_ob_bearish_active | 57.9% |
| smc_ob_bullish_active | 16.9% |
| smc_ote_long_zone | 7.9% |
| smc_ote_short_zone | 5.3% |
| squeeze_fire_dn | 0.1% |
| squeeze_fire_up | 4.4% |
| squeeze_in | 21.2% |
| squeeze_positive | 21.3% |
| stoch_bearish_cross | 6.0% |
| stoch_broad_overbought | 8.0% |
| stoch_broad_oversold | 55.9% |
| stoch_bullish_cross | 21.3% |
| stoch_overbought | 6.7% |
| stoch_oversold | 45.8% |
| stochrsi_cross_dn | 14.4% |
| stochrsi_cross_up | 46.2% |
| stochrsi_overbought | 20.5% |
| stochrsi_oversold | 36.9% |
| supertrend_bearish | 7.2% |
| supertrend_bullish | 92.8% |
| supertrend_flip_dn | 0.1% |
| supertrend_flip_recent_long_5d | 4.8% |
| supertrend_flip_recent_short_5d | 9.6% |
| supertrend_flip_up | 1.2% |
| support_break_retest | 48.3% |
| tema_above_dema | 27.8% |
| tema_cross_dn | 3.2% |
| tema_cross_up | 1.9% |
| three_white_soldiers | 3.6% |
| triangle_apex_break_retest_long | 4.8% |
| triangle_ascending_detected | 6.1% |
| triangle_descending_detected | 9.2% |
| uo_overbought | 0.7% |
| uo_oversold | 5.9% |
| usd_strengthening | 24.2% |
| usd_weakening | 13.8% |
| vix_band_high | 55.7% |
| vix_band_low | 24.2% |
| vix_band_mid | 20.1% |
| vix_term_backwardation | 19.4% |
| vix_term_contango | 80.6% |
| vol_above_avg | 46.5% |
| vol_below_avg | 53.5% |
| vol_spike_12x | 33.6% |
| vol_spike_15x | 17.3% |
| vol_spike_17x | 12.8% |
| vol_spike_2x | 6.8% |
| vol_spike_2x_on_down_day_recent_3d | 10.9% |
| vol_spike_2x_on_up_day_recent_3d | 4.0% |
| vol_spike_3x | 2.1% |
| vp_above_value_area | 6.7% |
| vp_below_value_area | 44.7% |
| vp_close_above_poc | 25.0% |
| vp_close_below_poc | 75.0% |
| vp_in_value_area | 48.6% |
| week_open_gap_down_15pct | 5.2% |
| week_open_gap_up_15pct | 2.5% |
| weekly_above_ema_10 | 16.5% |
| weekly_above_ema_20 | 15.0% |
| weekly_bias_bear | 79.4% |
| weekly_bias_bull | 10.9% |
| weekly_momentum_pos | 21.2% |
| williams_r_overbought | 9.3% |
| williams_r_oversold | 34.6% |
| williams_r_rising | 85.6% |
| within_pead_window | 40.1% |
| within_post_deletion_window | 10.7% |
| within_post_inclusion_window | 0.7% |
| within_pre_rebalance_window | 1.3% |
| xs_avoid_high_ivol | 56.0% |
| xs_avoid_high_max | 66.6% |
| xs_high_beta_decile | 34.7% |
| xs_low_beta_bottom_quintile | 34.7% |
| xs_low_beta_decile | 10.3% |
| xs_low_beta_decile_entry_recent_5d | 0.5% |
| xs_low_beta_top_quintile | 10.3% |
| xs_momentum_bottom_decile | 24.2% |
| xs_momentum_bottom_quintile | 39.3% |
| xs_momentum_top_decile | 8.5% |
| xs_momentum_top_quintile | 13.9% |
| xs_quality_bottom_quintile | 25.4% |
| xs_quality_top_quintile | 13.0% |
| xs_quality_top_tercile | 30.8% |
| year_high_break_retest_long | 0.3% |
| year_low_break_retest_short | 11.7% |
| yoy_surprise_high | 45.6% |
| yoy_surprise_negative | 46.2% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 89.9% |
| committed_growth_holders | 89.9% |
| corp_donations_1y | 7.3% |
| corp_donations_count_1y | 7.3% |
| corp_donations_unique_pacs | 7.3% |
| cot_rut_commercials_pctile_3y | 57.8% |
| cot_rut_mmoney_pctile_3y | 57.8% |
| cup_handle_depth_pct | 20.2% |
| days_since_deletion | 10.0% |
| days_since_inclusion | 17.8% |
| days_to_next_holiday | 70.7% |
| days_to_rebalance | 10.4% |
| dpi_30d_avg | 95.7% |
| dpi_recent | 95.7% |
| earnings_announcement_return | 92.8% |
| earnings_eps_yoy_growth | 94.5% |
| gov_contracts_4q_sum | 38.9% |
| gov_contracts_last_qtr_amount | 38.9% |
| gov_contracts_qoq_growth | 38.9% |
| head_shoulders_magnitude_pct | 11.3% |
| insider_director_buyers_30d | 8.7% |
| insider_officer_buyers_30d | 8.7% |
| insider_total_shares_bought_30d | 8.7% |
| insider_unique_buyers_30d | 8.7% |
| inverted_cup_handle_height_pct | 14.2% |
| lobbying_amount_1y | 71.2% |
| lobbying_amount_q | 71.2% |
| lobbying_amount_yoy | 71.2% |
| monthly_momentum_6m | 97.3% |
| otc_short_ratio_recent | 95.7% |
| otc_volume_recent | 95.7% |
| pair_half_life | 90.1% |
| pair_max_abs_zscore | 90.1% |
| pair_zscore_signed | 90.1% |
| pct_from_avwap_20high | 95.7% |
| pct_from_avwap_20low | 72.6% |
| pct_from_avwap_252low | 87.4% |
| pct_from_avwap_50low | 80.0% |
| persistent_holders_4q | 89.9% |
| persistent_holders_8q | 89.9% |
| sc_13g_latest_percent_owned | 1.7% |
| search_volume_index_recent | 79.2% |
| search_volume_observations | 79.2% |
| search_volume_zscore_30d | 79.2% |
| sector_etf_return_20d | 3.2% |
| spy_return_20d | 3.2% |
| total_active_holders | 89.9% |
| triangle_breakdown_pct | 9.2% |
| triangle_breakout_pct | 6.1% |
| xs_quality_decile | 68.7% |
| xs_quality_gross_profitability | 68.7% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.999), `avwap_20low` (0.998), `avwap_252low` (0.995), `avwap_50low` (0.998), `bb_10_20_lower` (0.997), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.999), `bb_20_15_lower` (0.998), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.997), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.998), `cam_r1` (0.997), `cam_r2` (0.997), `cam_r3` (0.997), `cam_r4` (0.997), `cam_s1` (0.997), `cam_s2` (0.997), `cam_s3` (0.997), `cam_s4` (0.996), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.997), `cpr_top` (0.997), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.997), `days_since_classification_change` (1.0), `dc10_lower` (0.997), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.997), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.999), `double_bottom_neckline` (0.996), `double_bottom_trough` (0.997), `double_top_neckline` (0.996), `double_top_peak` (0.996), `entry_stop_long` (0.996), `entry_stop_short` (0.998), `fib_236` (0.997), `fib_382` (0.997), `fib_500` (0.998), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.993), `fib_ext_162` (0.99), `head_shoulders_bottom_neckline` (0.995), `head_shoulders_top_neckline` (0.996), `hull_ma` (0.998), `ichi_kijun` (0.999), `ichi_senkou_a` (0.995), `ichi_senkou_b` (0.993), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.998), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.997), `monthly_sma_12` (0.985), `monthly_sma_6` (0.995), `pivot` (0.997), `prev_close` (0.997), `prev_high` (0.998), `prev_low` (0.997), `psar_value` (0.998), `r1` (0.997), `r2` (0.998), `r3` (0.998), `s1` (0.996), `s2` (0.996), `s3` (0.994), `supertrend_value` (0.994), `swing_high` (0.995), `swing_low` (0.997), `tema` (0.998), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.996), `vp_value_area_low` (0.997), `weekly_close` (0.997), `weekly_ema_10` (0.999), `weekly_ema_20` (0.997), `wood_p` (0.998), `wood_r1` (0.998), `wood_r2` (0.998), `wood_s1` (0.997), `wood_s2` (0.996), `year_high` (0.972), `year_low` (0.98)

**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? | engine | offline | pending |
|---|---|---|---|---|---|---|---|
| P1.1 | filing window - an Item 1.01 8-K filed w | 4 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) | 1 | 0 | 3 |
| P2 | po3_accum_range_pct >= 0.0556 | 5 | subset-safe | no - derives offline | 1 | 4 | 0 |

```
FULL FACTORIAL     4 x 5 = 20
offline gradings   4 level-combinations x 24 exits = 96 (graded from the engine runs' cubes, never run themselves)
ENGINE RUNS        1 (per axis: the production level plus any actuated non-production level)
PENDING ACTUATION  15 level-combinations need an env knob that does not exist - a FEATURE REQUEST, not a runnable band (runbook section 2.3 state 1; B2866)
TILING             1 + 4 + 15 = 20 (engine + offline + pending: every level of every axis sits in exactly one class - the three count columns above; S6-B3189)
STEP-1 SERIAL COST 1 x 3.66 h = 4 h at the ruled 1y x 200-ticker shape
                   per-run 3.66 h is within the 5 h local cap (B2107); the TOTAL is not a plan until the owner rules a budget on it
```

B-row candidates NOT in this factorial: 630 census axes join it only when REGISTERED at the T3 band review.
