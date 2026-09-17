# Table A - smc_mitigation_block_short

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit 8233e68a5 at 2026-09-17 00:26:53 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** smc | **status:** NOT-STARTED | **R5 fires:** 44 | **surviving fires (T1):** 44 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  below_ema_200  <- backtest/signals/screener.py
       knobs P1.1-P1.1 (band rows in Table A)
P2  smc_mitigation_block_short  <- backtest/signals/screener.py +2
       knobs P2.1-P2.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  rsi_14 > 50   [EXISTING-THRESHOLD]
P4  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_smc_mitigation_block_short (docstring and return dropped):

```python
fires = s.get('smc_mitigation_block_short', False) and s.get('below_ema_200', False) and (s.get('rsi_14', 50) > 50) and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | below_ema_200 - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | ema span (the 200 in above/below_ema_200) - backtest/signals/technical.py compute_ema_sma | 200 | none - other spans' values are unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production; 150/250 are the adjacent canon spans; T3 review before any grid |
| P2 | PRODUCER | smc_mitigation_block_short - emitted by backtest/signals/screener.py +2; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | mirror of mitigation_long - backtest/signals/smc_ict.py mitigation block | (20, 90) | none | the whole band; env SMC_SWING_LENGTH / SMC_EVENT_RECENCY_BARS | mirror; T3 review before any grid |
| P3 | STRATEGY | rsi_14 `> 50` [EXISTING-THRESHOLD] | `> 50` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P3.1 | BAND | rsi span - backtest/signals/technical.py rsi block | 14 | none - values at other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production with adjacent canon spans; T3 review before any grid |
| P4 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | - | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| rsi_14 | backtest/signals/screener.py | `> 50` | 100.0% | TIGHTER = RAISE the floor: 56.442 -> 35 (80%); 59.414 -> 26 (59%); 63.31 -> 18 (41%); 66.034 -> 9 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 15.846, 19.142, 21.418, 26.3 | 15.846: 35 (80%); 19.142: 26 (59%); 21.418: 18 (41%); 26.3: 9 (20%) | 15.846: 9 (20%); 19.142: 18 (41%); 21.418: 26 (59%); 26.3: 35 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 14.594, 16.126, 17.292, 19.206 | 14.594: 35 (80%); 16.126: 26 (59%); 17.292: 18 (41%); 19.206: 9 (20%) | 14.594: 9 (20%); 16.126: 18 (41%); 17.292: 26 (59%); 19.206: 35 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 25.762, 28.48, 31.8, 36.048 | 25.762: 35 (80%); 28.48: 27 (61%); 31.8: 18 (41%); 36.048: 9 (20%) | 25.762: 9 (20%); 28.48: 19 (43%); 31.8: 26 (59%); 36.048: 35 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | 0.7772, 1.2926, 2.971, 6.73 | 0.7772: 35 (80%); 1.2926: 26 (59%); 2.971: 18 (41%); 6.73: 9 (20%) | 0.7772: 9 (20%); 1.2926: 18 (41%); 2.971: 26 (59%); 6.73: 35 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 0.6786, 1.8521, 2.6144, 4.0644 | 0.6786: 35 (80%); 1.8521: 26 (59%); 2.6144: 18 (41%); 4.0644: 9 (20%) | 0.6786: 9 (20%); 1.8521: 18 (41%); 2.6144: 26 (59%); 4.0644: 35 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 0.6786, 1.8521, 2.6144, 4.0644 | 0.6786: 35 (80%); 1.8521: 26 (59%); 2.6144: 18 (41%); 4.0644: 9 (20%) | 0.6786: 9 (20%); 1.8521: 18 (41%); 2.6144: 26 (59%); 4.0644: 35 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.3138, 3.0342, 3.5218, 4.1526 | 2.3138: 35 (80%); 3.0342: 26 (59%); 3.5218: 18 (41%); 4.1526: 9 (20%) | 2.3138: 9 (20%); 3.0342: 18 (41%); 3.5218: 26 (59%); 4.1526: 35 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0998, 0.1366, 0.1706, 0.2075 | 0.0998: 35 (80%); 0.1366: 26 (59%); 0.1706: 18 (41%); 0.2075: 9 (20%) | 0.0998: 9 (20%); 0.1366: 18 (41%); 0.1706: 26 (59%); 0.2075: 35 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.6573, 0.7623, 0.8215, 0.8722 | 0.6573: 35 (80%); 0.7623: 26 (59%); 0.8215: 18 (41%); 0.8722: 9 (20%) | 0.6573: 9 (20%); 0.7623: 18 (41%); 0.8215: 26 (59%); 0.8722: 35 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0822, 0.1209, 0.1546, 0.1926 | 0.0822: 35 (80%); 0.1209: 26 (59%); 0.1546: 18 (41%); 0.1926: 9 (20%) | 0.0822: 9 (20%); 0.1209: 18 (41%); 0.1546: 26 (59%); 0.1926: 35 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | 0.813, 0.9078, 1.0329, 1.1302 | 0.813: 35 (80%); 0.9078: 26 (59%); 1.0329: 18 (41%); 1.1302: 9 (20%) | 0.813: 9 (20%); 0.9078: 18 (41%); 1.0329: 26 (59%); 1.1302: 35 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.1095, 0.1611, 0.2062, 0.2567 | 0.1095: 35 (80%); 0.1611: 26 (59%); 0.2062: 18 (41%); 0.2567: 9 (20%) | 0.1095: 9 (20%); 0.1611: 18 (41%); 0.2062: 26 (59%); 0.2567: 35 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.7347, 0.8058, 0.8996, 0.9727 | 0.7347: 35 (80%); 0.8058: 26 (59%); 0.8996: 18 (41%); 0.9727: 9 (20%) | 0.7347: 9 (20%); 0.8058: 18 (41%); 0.8996: 26 (59%); 0.9727: 35 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0489, -0.0164, -0.0094, 0.0121 | -0.0489: 35 (80%); -0.0164: 27 (61%); -0.0094: 18 (41%); 0.0121: 9 (20%) | -0.0489: 9 (20%); -0.0164: 18 (41%); -0.0094: 26 (59%); 0.0121: 35 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1623, 0.1785, 0.236, 0.2659 | 0.1623: 35 (80%); 0.1785: 26 (59%); 0.236: 18 (41%); 0.2659: 9 (20%) | 0.1623: 9 (20%); 0.1785: 18 (41%); 0.236: 26 (59%); 0.2659: 35 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 44 (100%) | 0: 38 (86%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | 0.0008, 0.0985, 0.1817, 0.2316 | 0.0008: 35 (80%); 0.0985: 26 (59%); 0.1817: 18 (41%); 0.2316: 9 (20%) | 0.0008: 9 (20%); 0.0985: 18 (41%); 0.1817: 26 (59%); 0.2316: 35 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 44 (100%); 1: 22 (50%) | 0: 22 (50%); 1: 38 (86%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.236, -0.1779, -0.1382, -0.1067 | -0.236: 35 (80%); -0.1779: 26 (59%); -0.1382: 18 (41%); -0.1067: 9 (20%) | -0.236: 9 (20%); -0.1779: 18 (41%); -0.1382: 26 (59%); -0.1067: 35 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5679, 0.6128, 0.7641, 0.8103 | 0.5679: 35 (80%); 0.6128: 26 (59%); 0.7641: 18 (41%); 0.8103: 9 (20%) | 0.5679: 9 (20%); 0.6128: 18 (41%); 0.7641: 26 (59%); 0.8103: 35 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2115, 0.332, 0.6205, 0.8218 | 0.2115: 37 (84%); 0.332: 26 (59%); 0.6205: 18 (41%); 0.8218: 9 (20%) | 0.2115: 10 (23%); 0.332: 18 (41%); 0.6205: 26 (59%); 0.8218: 35 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1655, 0.0272, 0.1347, 0.3045 | -0.1655: 35 (80%); 0.0272: 27 (61%); 0.1347: 18 (41%); 0.3045: 9 (20%) | -0.1655: 9 (20%); 0.0272: 19 (43%); 0.1347: 26 (59%); 0.3045: 35 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.1731, 0.4821, 0.7166, 0.8718 | 0.1731: 35 (80%); 0.4821: 26 (59%); 0.7166: 18 (41%); 0.8718: 9 (20%) | 0.1731: 9 (20%); 0.4821: 18 (41%); 0.7166: 26 (59%); 0.8718: 35 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0449, 0.209, 0.5346, 0.7628 | 0.0449: 36 (82%); 0.209: 26 (59%); 0.5346: 18 (41%); 0.7628: 10 (23%) | 0.0449: 12 (27%); 0.209: 18 (41%); 0.5346: 26 (59%); 0.7628: 37 (84%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.4951, -0.3589, -0.1586, 0.0218 | -0.4951: 35 (80%); -0.3589: 26 (59%); -0.1586: 18 (41%); 0.0218: 9 (20%) | -0.4951: 9 (20%); -0.3589: 18 (41%); -0.1586: 26 (59%); 0.0218: 35 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3231, 0.5179, 0.7333, 0.9359 | 0.3231: 35 (80%); 0.5179: 26 (59%); 0.7333: 18 (41%); 0.9359: 9 (20%) | 0.3231: 9 (20%); 0.5179: 18 (41%); 0.7333: 26 (59%); 0.9359: 35 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0962, 0.4423, 0.5628, 0.6474 | 0.0962: 35 (80%); 0.4423: 27 (61%); 0.5628: 18 (41%); 0.6474: 9 (20%) | 0.0962: 9 (20%); 0.4423: 20 (45%); 0.5628: 26 (59%); 0.6474: 35 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0698, -0.0542, -0.046, 0 | -0.0698: 35 (80%); -0.0542: 26 (59%); -0.046: 18 (41%); 0: 10 (23%) | -0.0698: 9 (20%); -0.0542: 18 (41%); -0.046: 26 (59%); 0: 43 (98%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4526, 0.7321, 0.8359, 1 | 0.4526: 35 (80%); 0.7321: 26 (59%); 0.8359: 18 (41%); 1: 10 (23%) | 0.4526: 9 (20%); 0.7321: 18 (41%); 0.8359: 26 (59%); 1: 44 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1667, 0.332, 0.5962, 0.9038 | 0.1667: 35 (80%); 0.332: 26 (59%); 0.5962: 19 (43%); 0.9038: 11 (25%) | 0.1667: 9 (20%); 0.332: 18 (41%); 0.5962: 27 (61%); 0.9038: 36 (82%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0488, 0.0239, 0.0543, 0.1562 | -0.0488: 35 (80%); 0.0239: 26 (59%); 0.0543: 18 (41%); 0.1562: 10 (23%) | -0.0488: 9 (20%); 0.0239: 18 (41%); 0.0543: 26 (59%); 0.1562: 37 (84%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2974, 0.7188, 0.8889, 0.977 | 0.2974: 35 (80%); 0.7188: 26 (59%); 0.8889: 20 (45%); 0.977: 9 (20%) | 0.2974: 9 (20%); 0.7188: 18 (41%); 0.8889: 27 (61%); 0.977: 35 (80%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1795, 0.394, 0.6987, 0.8982 | 0.1795: 36 (82%); 0.394: 26 (59%); 0.6987: 20 (45%); 0.8982: 9 (20%) | 0.1795: 10 (23%); 0.394: 18 (41%); 0.6987: 27 (61%); 0.8982: 35 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0154, 0.0566, 0.141 | -0.0812: 41 (93%); -0.0154: 26 (59%); 0.0566: 21 (48%); 0.141: 9 (20%) | -0.0812: 11 (25%); -0.0154: 18 (41%); 0.0566: 27 (61%); 0.141: 35 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0607, 0.0229, 0.035, 0.0705 | -0.0607: 36 (82%); 0.0229: 27 (61%); 0.035: 18 (41%); 0.0705: 9 (20%) | -0.0607: 10 (23%); 0.0229: 19 (43%); 0.035: 26 (59%); 0.0705: 35 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3526, 0.6026, 0.7244, 0.8372 | 0.3526: 35 (80%); 0.6026: 27 (61%); 0.7244: 19 (43%); 0.8372: 9 (20%) | 0.3526: 9 (20%); 0.6026: 20 (45%); 0.7244: 28 (64%); 0.8372: 35 (80%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1795, 0.3846, 0.5526, 0.8026 | 0.1795: 36 (82%); 0.3846: 26 (59%); 0.5526: 18 (41%); 0.8026: 9 (20%) | 0.1795: 11 (25%); 0.3846: 18 (41%); 0.5526: 26 (59%); 0.8026: 35 (80%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.06, 0.0971, 0.1983, 0.3747 | 0.06: 36 (82%); 0.0971: 26 (59%); 0.1983: 19 (43%); 0.3747: 9 (20%) | 0.06: 10 (23%); 0.0971: 18 (41%); 0.1983: 27 (61%); 0.3747: 35 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 100.0% | 31.6, 54.6, 82.6, 135 | 31.6: 35 (80%); 54.6: 26 (59%); 82.6: 18 (41%); 135: 9 (20%) | 31.6: 9 (20%); 54.6: 18 (41%); 82.6: 26 (59%); 135: 35 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 5.6, 14.2, 21, 33.4 | 5.6: 35 (80%); 14.2: 26 (59%); 21: 20 (45%); 33.4: 9 (20%) | 5.6: 9 (20%); 14.2: 18 (41%); 21: 27 (61%); 33.4: 35 (80%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3 | 1: 37 (84%); 2: 22 (50%); 3: 15 (34%) | 1: 22 (50%); 2: 29 (66%); 3: 37 (84%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0176, -0.0081, 0.0003, 0.0196 | -0.0176: 35 (80%); -0.0081: 26 (59%); 0.0003: 18 (41%); 0.0196: 9 (20%) | -0.0176: 9 (20%); -0.0081: 18 (41%); 0.0003: 26 (59%); 0.0196: 35 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.5354, 24.9009, 25.9917, 26.9048 | 24.5354: 36 (82%); 24.9009: 26 (59%); 25.9917: 18 (41%); 26.9048: 9 (20%) | 24.5354: 10 (23%); 24.9009: 18 (41%); 25.9917: 26 (59%); 26.9048: 35 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -1.3698, -0.558, -0.167, 0.3338 | -1.3698: 35 (80%); -0.558: 26 (59%); -0.167: 18 (41%); 0.3338: 9 (20%) | -1.3698: 9 (20%); -0.558: 18 (41%); -0.167: 26 (59%); 0.3338: 35 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.3338, 0.167, 0.558, 1.3698 | -0.3338: 35 (80%); 0.167: 26 (59%); 0.558: 18 (41%); 1.3698: 9 (20%) | -0.3338: 9 (20%); 0.167: 18 (41%); 0.558: 26 (59%); 1.3698: 35 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0306, -0.0141, 0.0038, 0.0434 | -0.0306: 35 (80%); -0.0141: 26 (59%); 0.0038: 18 (41%); 0.0434: 9 (20%) | -0.0306: 9 (20%); -0.0141: 18 (41%); 0.0038: 26 (59%); 0.0434: 35 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.1808, 8.443, 8.525, 8.976 | 8.1808: 35 (80%); 8.443: 26 (59%); 8.525: 18 (41%); 8.976: 9 (20%) | 8.1808: 9 (20%); 8.443: 18 (41%); 8.525: 26 (59%); 8.976: 35 (80%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 7.4, 115, 213 | 2: 36 (82%); 7.4: 26 (59%); 115: 19 (43%); 213: 10 (23%) | 2: 10 (23%); 7.4: 18 (41%); 115: 27 (61%); 213: 36 (82%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 2, 6.6, 77, 136.8 | 2: 36 (82%); 6.6: 26 (59%); 77: 19 (43%); 136.8: 9 (20%) | 2: 11 (25%); 6.6: 18 (41%); 77: 27 (61%); 136.8: 35 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | 0.2009, 0.3665, 0.6077, 1.372 | 0.2009: 35 (80%); 0.3665: 26 (59%); 0.6077: 18 (41%); 1.372: 9 (20%) | 0.2009: 9 (20%); 0.3665: 18 (41%); 0.6077: 26 (59%); 1.372: 35 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | 0.1235, 0.3348, 0.9069, 1.9817 | 0.1235: 35 (80%); 0.3348: 26 (59%); 0.9069: 18 (41%); 1.9817: 9 (20%) | 0.1235: 9 (20%); 0.3348: 18 (41%); 0.9069: 26 (59%); 1.9817: 35 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -0.254, 0.0302, 0.2911, 1.0708 | -0.254: 35 (80%); 0.0302: 26 (59%); 0.2911: 18 (41%); 1.0708: 9 (20%) | -0.254: 9 (20%); 0.0302: 18 (41%); 0.2911: 26 (59%); 1.0708: 35 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | 0.1079, 0.2395, 0.3765, 0.8489 | 0.1079: 35 (80%); 0.2395: 26 (59%); 0.3765: 18 (41%); 0.8489: 9 (20%) | 0.1079: 9 (20%); 0.2395: 18 (41%); 0.3765: 26 (59%); 0.8489: 35 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | 0.4332, 0.6641, 1.4138, 3.1049 | 0.4332: 35 (80%); 0.6641: 26 (59%); 1.4138: 18 (41%); 3.1049: 9 (20%) | 0.4332: 9 (20%); 0.6641: 18 (41%); 1.4138: 26 (59%); 3.1049: 35 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | 0.1107, 0.3839, 0.9898, 2.269 | 0.1107: 35 (80%); 0.3839: 26 (59%); 0.9898: 18 (41%); 2.269: 9 (20%) | 0.1107: 9 (20%); 0.3839: 18 (41%); 0.9898: 26 (59%); 2.269: 35 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 57.316, 63.824, 67.662, 72.518 | 57.316: 35 (80%); 63.824: 26 (59%); 67.662: 18 (41%); 72.518: 9 (20%) | 57.316: 9 (20%); 63.824: 18 (41%); 67.662: 26 (59%); 72.518: 35 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 100.0% | -0.1775, -0.09, -0.0488, 0.0211 | -0.1775: 35 (80%); -0.09: 26 (59%); -0.0488: 18 (41%); 0.0211: 9 (20%) | -0.1775: 9 (20%); -0.09: 18 (41%); -0.0488: 26 (59%); 0.0211: 35 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 100.0% | 0.0055, 0.0123, 0.02, 0.0425 | 0.0055: 35 (80%); 0.0123: 26 (59%); 0.02: 18 (41%); 0.0425: 9 (20%) | 0.0055: 9 (20%); 0.0123: 18 (41%); 0.02: 26 (59%); 0.0425: 35 (80%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 1, 2, 3, 6.8 | 1: 40 (91%); 2: 33 (75%); 3: 24 (55%); 6.8: 9 (20%) | 1: 11 (25%); 2: 20 (45%); 3: 29 (66%); 6.8: 35 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.0956 | 0: 44 (100%); 0.0956: 9 (20%) | 0: 32 (73%); 0.0956: 35 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.5, 0.85 | 0: 44 (100%); 0.3333: 29 (66%); 0.5: 20 (45%); 0.85: 9 (20%) | 0: 11 (25%); 0.3333: 19 (43%); 0.5: 30 (68%); 0.85: 35 (80%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 1, 2, 4.4 | 1: 38 (86%); 2: 23 (52%); 4.4: 9 (20%) | 1: 21 (48%); 2: 28 (64%); 4.4: 35 (80%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 1, 2, 3, 6.8 | 1: 40 (91%); 2: 33 (75%); 3: 24 (55%); 6.8: 9 (20%) | 1: 11 (25%); 2: 20 (45%); 3: 29 (66%); 6.8: 35 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0.6, 2, 3.8, 7 | 0.6: 35 (80%); 2: 28 (64%); 3.8: 18 (41%); 7: 10 (23%) | 0.6: 9 (20%); 2: 24 (55%); 3.8: 26 (59%); 7: 37 (84%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.0676, 0.2036, 0.2978, 0.4047 | 0.0676: 35 (80%); 0.2036: 26 (59%); 0.2978: 18 (41%); 0.4047: 9 (20%) | 0.0676: 9 (20%); 0.2036: 18 (41%); 0.2978: 26 (59%); 0.4047: 35 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.0967, 0.4286, 1 | 0: 43 (98%); 0.0967: 26 (59%); 0.4286: 19 (43%); 1: 12 (27%) | 0: 15 (34%); 0.0967: 18 (41%); 0.4286: 28 (64%); 1: 44 (100%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.1963, 0.4121, 0.7 | 0: 42 (95%); 0.1963: 26 (59%); 0.4121: 18 (41%); 0.7: 9 (20%) | 0: 11 (25%); 0.1963: 18 (41%); 0.4121: 26 (59%); 0.7: 35 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1963, 0.4121, 0.7 | 0: 42 (95%); 0.1963: 26 (59%); 0.4121: 18 (41%); 0.7: 9 (20%) | 0: 11 (25%); 0.1963: 18 (41%); 0.4121: 26 (59%); 0.7: 35 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.278, 0, 0.0261, 0.3253 | -0.278: 35 (80%); 0: 32 (73%); 0.0261: 18 (41%); 0.3253: 9 (20%) | -0.278: 9 (20%); 0: 25 (57%); 0.0261: 26 (59%); 0.3253: 35 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.6424, 0, 0.2383, 1.3293 | -0.6424: 35 (80%); 0: 27 (61%); 0.2383: 18 (41%); 1.3293: 9 (20%) | -0.6424: 9 (20%); 0: 22 (50%); 0.2383: 26 (59%); 1.3293: 35 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 3, 5, 6, 13.2 | 3: 36 (82%); 5: 27 (61%); 6: 21 (48%); 13.2: 9 (20%) | 3: 14 (32%); 5: 23 (52%); 6: 28 (64%); 13.2: 35 (80%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | 0.0332, 0.073, 0.09, 0.1358 | 0.0332: 35 (80%); 0.073: 26 (59%); 0.09: 18 (41%); 0.1358: 9 (20%) | 0.0332: 9 (20%); 0.073: 18 (41%); 0.09: 26 (59%); 0.1358: 35 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | 0.0275, 0.0811, 0.1117, 0.1917 | 0.0275: 35 (80%); 0.0811: 26 (59%); 0.1117: 18 (41%); 0.1917: 9 (20%) | 0.0275: 9 (20%); 0.0811: 18 (41%); 0.1117: 26 (59%); 0.1917: 35 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | 0.0194, 0.0394, 0.073, 0.0923 | 0.0194: 35 (80%); 0.0394: 26 (59%); 0.073: 18 (41%); 0.0923: 9 (20%) | 0.0194: 9 (20%); 0.0394: 18 (41%); 0.073: 26 (59%); 0.0923: 35 (80%) | OFFLINE |
| pct_from_avwap_20low | (not found by literal grep) | 100.0% | 2.7828, 5.7278, 7.577, 9.4656 | 2.7828: 35 (80%); 5.7278: 26 (59%); 7.577: 18 (41%); 9.4656: 9 (20%) | 2.7828: 9 (20%); 5.7278: 18 (41%); 7.577: 26 (59%); 9.4656: 35 (80%) | OFFLINE |
| pct_from_avwap_252low | (not found by literal grep) | 100.0% | 1.4872, 5.753, 7.9556, 12.5424 | 1.4872: 35 (80%); 5.753: 26 (59%); 7.9556: 18 (41%); 12.5424: 9 (20%) | 1.4872: 9 (20%); 5.753: 18 (41%); 7.9556: 26 (59%); 12.5424: 35 (80%) | OFFLINE |
| pct_from_avwap_50low | backtest/signals/screener.py | 100.0% | 3.2964, 6.1618, 8.2478, 12.5424 | 3.2964: 35 (80%); 6.1618: 26 (59%); 8.2478: 18 (41%); 12.5424: 9 (20%) | 3.2964: 9 (20%); 6.1618: 18 (41%); 8.2478: 26 (59%); 12.5424: 35 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -30.8656, -22.573, -13.7374, -4.8232 | -30.8656: 35 (80%); -22.573: 26 (59%); -13.7374: 18 (41%); -4.8232: 9 (20%) | -30.8656: 9 (20%); -22.573: 18 (41%); -13.7374: 26 (59%); -4.8232: 35 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0497, 0.0838, 0.1177, 0.1328 | 0.0497: 35 (80%); 0.0838: 26 (59%); 0.1177: 18 (41%); 0.1328: 10 (23%) | 0.0497: 9 (20%); 0.0838: 18 (41%); 0.1177: 26 (59%); 0.1328: 36 (82%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.182, 0.2647, 0.3887, 0.5362 | 0.182: 35 (80%); 0.2647: 26 (59%); 0.3887: 18 (41%); 0.5362: 9 (20%) | 0.182: 9 (20%); 0.2647: 18 (41%); 0.3887: 26 (59%); 0.5362: 35 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | 0.3538, 1.0127, 1.7091, 2.9395 | 0.3538: 35 (80%); 1.0127: 26 (59%); 1.7091: 18 (41%); 2.9395: 9 (20%) | 0.3538: 9 (20%); 1.0127: 18 (41%); 1.7091: 26 (59%); 2.9395: 35 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | 0.5034, 0.8625, 1.0888, 1.6396 | 0.5034: 35 (80%); 0.8625: 26 (59%); 1.0888: 18 (41%); 1.6396: 9 (20%) | 0.5034: 9 (20%); 0.8625: 18 (41%); 1.0888: 26 (59%); 1.6396: 35 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -0.3459, 0.0619, 0.7312, 1.7007 | -0.3459: 35 (80%); 0.0619: 26 (59%); 0.7312: 18 (41%); 1.7007: 9 (20%) | -0.3459: 9 (20%); 0.0619: 18 (41%); 0.7312: 26 (59%); 1.7007: 35 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | 3.8422, 6.6078, 9.3196, 13.224 | 3.8422: 35 (80%); 6.6078: 26 (59%); 9.3196: 18 (41%); 13.224: 9 (20%) | 3.8422: 9 (20%); 6.6078: 18 (41%); 9.3196: 26 (59%); 13.224: 35 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 42.372, 56.64, 73.088, 93.074 | 42.372: 35 (80%); 56.64: 26 (59%); 73.088: 18 (41%); 93.074: 9 (20%) | 42.372: 9 (20%); 56.64: 18 (41%); 73.088: 26 (59%); 93.074: 35 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 53.622, 55.216, 58.334, 61.418 | 53.622: 35 (80%); 55.216: 26 (59%); 58.334: 18 (41%); 61.418: 9 (20%) | 53.622: 9 (20%); 55.216: 18 (41%); 58.334: 26 (59%); 61.418: 35 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 58.85, 65.45, 67.428, 71.946 | 58.85: 35 (80%); 65.45: 26 (59%); 67.428: 18 (41%); 71.946: 9 (20%) | 58.85: 9 (20%); 65.45: 18 (41%); 67.428: 26 (59%); 71.946: 35 (80%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0417, 0.0503, 0.0673, 0.0896 | 0.0417: 35 (80%); 0.0503: 26 (59%); 0.0673: 18 (41%); 0.0896: 9 (20%) | 0.0417: 9 (20%); 0.0503: 18 (41%); 0.0673: 26 (59%); 0.0896: 35 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0855, -0.0589, -0.0449, -0.0352 | -0.0855: 35 (80%); -0.0589: 26 (59%); -0.0449: 18 (41%); -0.0352: 9 (20%) | -0.0855: 9 (20%); -0.0589: 18 (41%); -0.0449: 26 (59%); -0.0352: 35 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 44 (100%) | 0: 38 (86%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.6007, 0.7677, 0.8468, 0.8906 | 0.6007: 35 (80%); 0.7677: 26 (59%); 0.8468: 18 (41%); 0.8906: 9 (20%) | 0.6007: 9 (20%); 0.7677: 18 (41%); 0.8468: 26 (59%); 0.8906: 35 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 25.2, 44.04, 69.64, 93.22 | 25.2: 35 (80%); 44.04: 26 (59%); 69.64: 18 (41%); 93.22: 9 (20%) | 25.2: 9 (20%); 44.04: 18 (41%); 69.64: 26 (59%); 93.22: 35 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | 1.157, 2.305, 3.7555, 7.665 | 1.157: 35 (80%); 2.305: 26 (59%); 3.7555: 18 (41%); 7.665: 9 (20%) | 1.157: 9 (20%); 2.305: 18 (41%); 3.7555: 26 (59%); 7.665: 35 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 73.456, 79.286, 89.782, 92.828 | 73.456: 35 (80%); 79.286: 26 (59%); 89.782: 18 (41%); 92.828: 9 (20%) | 73.456: 9 (20%); 79.286: 18 (41%); 89.782: 26 (59%); 92.828: 35 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 73.97, 86.718, 90.318, 93.162 | 73.97: 35 (80%); 86.718: 26 (59%); 90.318: 18 (41%); 93.162: 9 (20%) | 73.97: 9 (20%); 86.718: 18 (41%); 90.318: 26 (59%); 93.162: 35 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 58.976, 85.644, 93.034, 98.458 | 58.976: 35 (80%); 85.644: 26 (59%); 93.034: 18 (41%); 98.458: 9 (20%) | 58.976: 9 (20%); 85.644: 18 (41%); 93.034: 26 (59%); 98.458: 35 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 58.738, 78.922, 89.504, 100 | 58.738: 35 (80%); 78.922: 26 (59%); 89.504: 18 (41%); 100: 11 (25%) | 58.738: 9 (20%); 78.922: 18 (41%); 89.504: 26 (59%); 100: 44 (100%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 7, 11.8, 15 | 4: 37 (84%); 7: 28 (64%); 11.8: 18 (41%); 15: 11 (25%) | 4: 10 (23%); 7: 19 (43%); 11.8: 26 (59%); 15: 38 (86%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 7, 10, 14, 18 | 7: 36 (82%); 10: 30 (68%); 14: 20 (45%); 18: 12 (27%) | 7: 10 (23%); 10: 19 (43%); 14: 27 (61%); 18: 39 (89%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 53.046, 59.85, 63.016, 67.172 | 53.046: 35 (80%); 59.85: 26 (59%); 63.016: 18 (41%); 67.172: 9 (20%) | 53.046: 9 (20%); 59.85: 18 (41%); 63.016: 26 (59%); 67.172: 35 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.0667, 0.2969, 0.5857, 0.7706 | 0.0667: 35 (80%); 0.2969: 26 (59%); 0.5857: 18 (41%); 0.7706: 9 (20%) | 0.0667: 9 (20%); 0.2969: 18 (41%); 0.5857: 26 (59%); 0.7706: 35 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.55, 16.634, 19.178, 22.082 | 14.55: 35 (80%); 16.634: 26 (59%); 19.178: 18 (41%); 22.082: 9 (20%) | 14.55: 9 (20%); 16.634: 18 (41%); 19.178: 26 (59%); 22.082: 35 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 14.55, 16.634, 19.178, 22.082 | 14.55: 35 (80%); 16.634: 26 (59%); 19.178: 18 (41%); 22.082: 9 (20%) | 14.55: 9 (20%); 16.634: 18 (41%); 19.178: 26 (59%); 22.082: 35 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8529, 0.8808, 0.9095, 0.9422 | 0.8529: 35 (80%); 0.8808: 26 (59%); 0.9095: 18 (41%); 0.9422: 9 (20%) | 0.8529: 9 (20%); 0.8808: 18 (41%); 0.9095: 26 (59%); 0.9422: 35 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.696, 0.752, 0.92, 1.172 | 0.696: 35 (80%); 0.752: 26 (59%); 0.92: 19 (43%); 1.172: 9 (20%) | 0.696: 9 (20%); 0.752: 18 (41%); 0.92: 27 (61%); 1.172: 35 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0218, 0.0298, 0.0632, 0.1057 | 0.0218: 35 (80%); 0.0298: 26 (59%); 0.0632: 18 (41%); 0.1057: 9 (20%) | 0.0218: 9 (20%); 0.0298: 18 (41%); 0.0632: 26 (59%); 0.1057: 35 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 37.4383, 53.7363, 99.6385, 150.6245 | 37.4383: 35 (80%); 53.7363: 26 (59%); 99.6385: 18 (41%); 150.6245: 9 (20%) | 37.4383: 9 (20%); 53.7363: 18 (41%); 99.6385: 26 (59%); 150.6245: 35 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 38.5237, 56.571, 103.2557, 155.8419 | 38.5237: 35 (80%); 56.571: 26 (59%); 103.2557: 18 (41%); 155.8419: 9 (20%) | 38.5237: 9 (20%); 56.571: 18 (41%); 103.2557: 26 (59%); 155.8419: 35 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 44 (100%) | 0: 43 (98%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 44 (100%) | 0: 37 (84%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | 0.0275, 0.0674, 0.1101, 0.1757 | 0.0275: 35 (80%); 0.0674: 26 (59%); 0.1101: 18 (41%); 0.1757: 9 (20%) | 0.0275: 9 (20%); 0.0674: 18 (41%); 0.1101: 27 (61%); 0.1757: 35 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -24.342, -17.992, -14.216, -10.532 | -24.342: 35 (80%); -17.992: 26 (59%); -14.216: 18 (41%); -10.532: 9 (20%) | -24.342: 9 (20%); -17.992: 18 (41%); -14.216: 26 (59%); -10.532: 35 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 100.0% | 0.5364, 0.9193, 1.3088, 1.4998 | 0.5364: 35 (80%); 0.9193: 26 (59%); 1.3088: 18 (41%); 1.4998: 9 (20%) | 0.5364: 9 (20%); 0.9193: 18 (41%); 1.3088: 26 (59%); 1.4998: 35 (80%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 100.0% | 3, 6, 8.8, 9.4 | 3: 37 (84%); 6: 27 (61%); 8.8: 18 (41%); 9.4: 9 (20%) | 3: 10 (23%); 6: 20 (45%); 8.8: 26 (59%); 9.4: 35 (80%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 100.0% | 0.2335, 0.2947, 0.3468, 0.4405 | 0.2335: 35 (80%); 0.2947: 26 (59%); 0.3468: 18 (41%); 0.4405: 9 (20%) | 0.2335: 9 (20%); 0.2947: 18 (41%); 0.3468: 27 (61%); 0.4405: 35 (80%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 100.0% | 6, 8, 9, 10 | 6: 36 (82%); 8: 31 (70%); 9: 23 (52%); 10: 14 (32%) | 6: 10 (23%); 8: 21 (48%); 9: 30 (68%); 10: 44 (100%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 100.0% | 0.0372, 0.0479, 0.0577, 0.1031 | 0.0372: 35 (80%); 0.0479: 27 (61%); 0.0577: 18 (41%); 0.1031: 9 (20%) | 0.0372: 9 (20%); 0.0479: 18 (41%); 0.0577: 26 (59%); 0.1031: 35 (80%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 100.0% | 5.6, 8, 9, 10 | 5.6: 35 (80%); 8: 31 (70%); 9: 22 (50%); 10: 13 (30%) | 5.6: 9 (20%); 8: 22 (50%); 9: 31 (70%); 10: 44 (100%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 100.0% | -0.4429, -0.3333, -0.1805, -0.1225 | -0.4429: 35 (80%); -0.3333: 26 (59%); -0.1805: 18 (41%); -0.1225: 9 (20%) | -0.4429: 9 (20%); -0.3333: 18 (41%); -0.1805: 26 (59%); -0.1225: 35 (80%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 100.0% | 1, 1.2, 2, 3 | 1: 44 (100%); 1.2: 26 (59%); 2: 26 (59%); 3: 11 (25%) | 1: 18 (41%); 1.2: 18 (41%); 2: 33 (75%); 3: 38 (86%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 16.7% |
| 8k_item_5_02_filed_within_7d | 2.4% |
| above_avwap_20high | 20.5% |
| above_avwap_20low | 95.5% |
| above_avwap_252low | 93.2% |
| above_cam_r3 | 6.8% |
| above_cam_r4 | 4.5% |
| above_cpr | 43.2% |
| above_pivot | 43.2% |
| above_prev_high | 9.1% |
| above_prev_high_clearance_atr_05 | 2.3% |
| above_prev_low | 88.6% |
| above_r1 | 4.5% |
| above_r2 | 2.3% |
| above_vwap | 11.4% |
| above_wood_p | 61.4% |
| ad_rising | 81.8% |
| adx_cross_up | 6.8% |
| adx_cross_up_20 | 2.3% |
| adx_di_bear | 2.3% |
| adx_di_bull | 97.7% |
| adx_trending | 31.8% |
| ao_cross_up | 13.6% |
| ao_positive | 95.5% |
| at_key_fib | 9.1% |
| at_key_fib_wide | 27.3% |
| avwap_20high_loss_recent_3d | 48.0% |
| avwap_20high_reclaim_recent_3d | 12.0% |
| avwap_20low_loss_recent_3d | 2.3% |
| avwap_20low_reclaim_recent_3d | 11.4% |
| avwap_252low_loss_recent_3d | 2.3% |
| avwap_252low_reclaim_recent_3d | 9.1% |
| avwap_50low_reclaim_recent_3d | 6.8% |
| bb_10_20_above_mid | 88.6% |
| bb_10_20_expanding | 56.8% |
| bb_10_20_pctb_gt_75 | 63.6% |
| bb_10_20_pctb_gt_8 | 50.0% |
| bb_10_20_pctb_gt_85 | 34.1% |
| bb_10_20_pctb_gt_9 | 11.4% |
| bb_10_20_pctb_gt_95 | 6.8% |
| bb_10_20_pctb_lt_1 | 2.3% |
| bb_10_20_pctb_lt_15 | 2.3% |
| bb_10_20_pctb_lt_2 | 2.3% |
| bb_10_20_pctb_lt_25 | 2.3% |
| bb_10_20_reclaim_from_lower_recent_3d | 2.3% |
| bb_10_20_reclaim_from_upper_recent_3d | 27.3% |
| bb_10_20_squeeze | 15.9% |
| bb_10_20_touch_lower | 2.3% |
| bb_10_20_touch_upper | 6.8% |
| bb_20_15_above_mid | 97.7% |
| bb_20_15_expanding | 63.6% |
| bb_20_15_pctb_gt_75 | 90.9% |
| bb_20_15_pctb_gt_8 | 84.1% |
| bb_20_15_pctb_gt_85 | 75.0% |
| bb_20_15_pctb_gt_9 | 63.6% |
| bb_20_15_pctb_gt_95 | 50.0% |
| bb_20_15_reclaim_from_upper_recent_3d | 34.1% |
| bb_20_15_squeeze | 13.6% |
| bb_20_15_touch_upper | 47.7% |
| bb_20_20_above_mid | 97.7% |
| bb_20_20_expanding | 63.6% |
| bb_20_20_pctb_gt_75 | 77.3% |
| bb_20_20_pctb_gt_8 | 63.6% |
| bb_20_20_pctb_gt_85 | 47.7% |
| bb_20_20_pctb_gt_9 | 40.9% |
| bb_20_20_pctb_gt_95 | 27.3% |
| bb_20_20_reclaim_from_upper_recent_3d | 34.1% |
| bb_20_20_squeeze | 9.1% |
| bb_20_20_touch_upper | 25.0% |
| bearish_engulfing | 9.1% |
| bearish_pin_bar | 9.1% |
| below_avwap_20high | 79.5% |
| below_avwap_20low | 4.5% |
| below_avwap_252low | 6.8% |
| below_cam_s3 | 31.8% |
| below_cam_s4 | 18.2% |
| below_cpr | 56.8% |
| below_ema_20 | 2.3% |
| below_ema_200_break_recent_5d | 20.5% |
| below_ema_20_break_recent_5d | 2.3% |
| below_ema_21 | 2.3% |
| below_ema_21_break_recent_5d | 2.3% |
| below_ema_50 | 2.3% |
| below_ema_9 | 6.8% |
| below_ema_9_break_recent_5d | 4.5% |
| below_prev_high | 90.9% |
| below_prev_low | 11.4% |
| below_prev_low_clearance_atr_05 | 2.3% |
| below_s1 | 20.5% |
| below_s2 | 2.3% |
| below_sma_20 | 2.3% |
| below_sma_200 | 88.6% |
| below_sma_21 | 2.3% |
| below_sma_9 | 11.4% |
| below_vwap | 88.6% |
| bullish_pin_bar | 4.5% |
| ceo_buy | 4.9% |
| cfo_buy | 2.4% |
| chandelier_short_bearish | 18.2% |
| chandelier_short_flip_up | 2.3% |
| close_in_bottom_40pct_of_range | 61.4% |
| close_in_top_40pct_of_range | 11.4% |
| cluster_buy | 2.4% |
| cmf_cross_dn | 11.4% |
| cmf_negative | 20.5% |
| cmf_positive | 79.5% |
| concentrated_sell | 2.4% |
| cpr_narrow | 88.6% |
| cpr_narrow_tight | 25.0% |
| cup_handle_detected | 6.8% |
| cup_handle_neckline_break_retest_long | 4.5% |
| dc10_breakout_dn_1pct | 2.3% |
| dc10_breakout_up | 11.4% |
| dc10_breakout_up_1pct | 31.8% |
| dc10_new_high | 47.7% |
| dc10_strong_breakout_up | 2.3% |
| dc20_breakout_up | 9.1% |
| dc20_new_high | 43.2% |
| dc20_resistance_break_retest_strong | 38.6% |
| defensive_leadership | 47.7% |
| director_only_buy | 12.2% |
| doji | 6.8% |
| double_bottom_detected | 9.1% |
| double_top_detected | 11.4% |
| dpi_elevated | 62.5% |
| drying_volume_on_down_turn | 72.7% |
| ema_20_50_bearish | 52.3% |
| ema_20_50_bullish | 47.7% |
| ema_20_50_golden_cross | 11.4% |
| ema_9_21_bearish | 2.3% |
| ema_9_21_bullish | 97.7% |
| ema_9_21_golden_cross | 9.1% |
| evening_star | 11.4% |
| force_index_cross_dn | 4.5% |
| force_index_positive | 93.2% |
| gap_dn_1_5pct | 2.3% |
| gap_dn_2pct | 2.3% |
| gap_up_1_5pct | 18.2% |
| gap_up_2pct | 13.6% |
| hammer | 4.5% |
| head_shoulders_bottom_detected | 6.8% |
| head_shoulders_top_detected | 4.5% |
| house_cluster_buy | 7.0% |
| htf_aligned_bear | 4.5% |
| htf_disagreement | 9.1% |
| hull_bearish | 6.8% |
| hull_bullish | 93.2% |
| ichi_above_cloud | 56.8% |
| ichi_above_cloud_break_recent_5d | 27.3% |
| ichi_below_cloud | 9.1% |
| ichi_below_cloud_break_recent_5d | 2.3% |
| ichi_cloud_thick | 81.8% |
| ichi_tk_bearish | 9.1% |
| ichi_tk_bullish | 86.4% |
| ichi_tk_cross_up | 4.5% |
| ichi_weekly_above_cloud | 2.3% |
| ichi_weekly_below_cloud | 79.5% |
| ichi_weekly_in_cloud | 18.2% |
| inside_bar | 18.2% |
| inside_cpr | 2.3% |
| inside_kc | 70.5% |
| insider_cluster_active | 33.3% |
| institutional_buy | 88.6% |
| institutional_persistence_growing | 55.6% |
| institutional_persistence_strong | 63.9% |
| institutional_strong_buy | 81.8% |
| inverted_cup_handle_detected | 18.2% |
| is_friday | 15.9% |
| is_halloween_period | 56.8% |
| is_january | 15.9% |
| is_january_extended | 20.5% |
| is_monday | 15.9% |
| is_summer_period | 43.2% |
| is_totm_window | 22.7% |
| is_totm_window_first_day | 2.3% |
| is_week_open | 18.2% |
| kc_touch_upper | 34.1% |
| large_dollar_buy | 4.9% |
| macd_12_26_9_bearish | 2.3% |
| macd_12_26_9_bullish | 97.7% |
| macd_12_26_9_crossover_up | 2.3% |
| macd_8_21_5_bearish | 9.1% |
| macd_8_21_5_bullish | 90.9% |
| macd_8_21_5_crossover_dn | 2.3% |
| macd_8_21_5_crossover_up | 2.3% |
| marubozu_bear | 2.3% |
| mfi_broad_overbought | 31.8% |
| mfi_overbought | 9.1% |
| monthly_above_sma_6 | 59.1% |
| monthly_bias_bear | 40.9% |
| monthly_momentum_pos | 31.8% |
| near_avwap_20high_atr_05x | 60.0% |
| near_avwap_20high_atr_10x | 88.0% |
| near_avwap_20high_atr_15x | 96.0% |
| near_avwap_20high_atr_20x | 96.0% |
| near_avwap_20low_atr_05x | 9.1% |
| near_avwap_20low_atr_10x | 13.6% |
| near_avwap_20low_atr_15x | 34.1% |
| near_avwap_20low_atr_20x | 56.8% |
| near_avwap_252low_atr_05x | 15.9% |
| near_avwap_252low_atr_10x | 27.3% |
| near_avwap_252low_atr_15x | 34.1% |
| near_avwap_252low_atr_20x | 45.5% |
| near_avwap_50low_atr_05x | 2.3% |
| near_avwap_50low_atr_10x | 9.1% |
| near_avwap_50low_atr_15x | 27.3% |
| near_avwap_50low_atr_20x | 38.6% |
| near_cam_r3 | 6.8% |
| near_cam_s3 | 13.6% |
| near_cam_s4 | 11.4% |
| near_fib_236 | 13.6% |
| near_fib_382 | 2.3% |
| near_fib_500 | 6.8% |
| near_pivot | 27.3% |
| near_prev_close | 27.3% |
| near_prev_high | 4.5% |
| near_prev_low | 9.1% |
| near_r1 | 4.5% |
| near_r1_wide | 40.9% |
| near_r2_wide | 9.1% |
| near_s1 | 11.4% |
| near_s1_wide | 54.5% |
| near_s2 | 2.3% |
| near_s2_wide | 22.7% |
| near_wood_r1 | 18.2% |
| near_wood_s1 | 9.1% |
| news_uses_polygon_score | 25.0% |
| obv_bearish | 11.4% |
| obv_bullish | 88.6% |
| obv_diverge_bull | 6.8% |
| obv_falling | 20.5% |
| obv_rising | 79.5% |
| outside_bar | 6.8% |
| pead_negative_surprise | 26.2% |
| pead_positive_surprise | 14.3% |
| pin_bar | 13.6% |
| po3_accumulation_active | 20.5% |
| po3_bearish | 29.5% |
| po3_manipulation_sweep_down | 4.5% |
| po3_manipulation_sweep_up | 2.3% |
| po3_mmsm_setup | 2.3% |
| po3_sweep_above_prior_high | 63.6% |
| po3_sweep_below_prior_low | 40.9% |
| ppo_bullish | 95.5% |
| pre_fomc_d0 | 2.3% |
| pre_fomc_d1 | 9.1% |
| pre_fomc_window | 11.4% |
| price_above_dema | 93.2% |
| price_above_ema_20 | 97.7% |
| price_above_ema_20_break_recent_5d | 31.8% |
| price_above_ema_21 | 97.7% |
| price_above_ema_21_break_recent_5d | 31.8% |
| price_above_ema_50 | 97.7% |
| price_above_ema_50_break_recent_5d | 43.2% |
| price_above_ema_9 | 93.2% |
| price_above_ema_9_break_recent_5d | 36.4% |
| price_above_hull | 65.9% |
| price_above_sma_200 | 11.4% |
| price_above_sma_21 | 97.7% |
| price_above_tema | 63.6% |
| price_below_dema | 6.8% |
| price_below_hull | 34.1% |
| price_below_tema | 36.4% |
| psar_bullish | 93.2% |
| r1_break_retest_long | 93.2% |
| resistance_break_retest | 54.5% |
| risk_off_regime_bond_signal | 18.2% |
| risk_off_regime_bond_signal_strong | 6.8% |
| risk_off_regime_gold_signal | 34.1% |
| risk_on_regime_bond_signal | 38.6% |
| risk_on_regime_bond_signal_strong | 20.5% |
| roc_positive | 97.7% |
| rsi_14_cross_dn_overbought_recent_3d | 9.1% |
| rsi_14_overbought | 4.5% |
| rsi_14_rising | 34.1% |
| rsi_21_rising | 34.1% |
| rsi_2_bullish | 75.0% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 52.3% |
| rsi_2_cross_dn_overbought_recent_3d | 43.2% |
| rsi_2_cross_up_extreme_os_recent_3d | 4.5% |
| rsi_2_cross_up_oversold_recent_3d | 9.1% |
| rsi_2_extreme_ob | 34.1% |
| rsi_2_extreme_os | 4.5% |
| rsi_2_overbought | 47.7% |
| rsi_2_oversold | 9.1% |
| rsi_2_rising | 34.1% |
| rsi_9_bullish | 95.5% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 6.8% |
| rsi_9_cross_dn_overbought_recent_3d | 22.7% |
| rsi_9_extreme_ob | 2.3% |
| rsi_9_overbought | 34.1% |
| rsi_9_rising | 34.1% |
| s1_break_retest_short | 9.1% |
| sc_13g_filed_within_30d | 4.8% |
| shooting_star | 2.3% |
| sma_20_50_bullish | 40.9% |
| sma_20_50_golden_cross | 9.1% |
| sma_9_21_bullish | 86.4% |
| sma_9_21_golden_cross | 4.5% |
| smc_bos_bearish | 20.5% |
| smc_bos_bullish | 4.5% |
| smc_bos_retest_long | 4.5% |
| smc_bos_retest_short | 2.3% |
| smc_breaker_block_bearish | 38.6% |
| smc_breaker_block_bullish | 4.5% |
| smc_choch_bearish | 13.6% |
| smc_choch_bullish | 2.3% |
| smc_equal_lows_swept | 15.9% |
| smc_fvg_bearish_active | 6.8% |
| smc_fvg_bullish_active | 79.5% |
| smc_fvg_retest_long_zone | 18.2% |
| smc_in_discount_zone | 20.5% |
| smc_inverse_fvg_bearish | 47.7% |
| smc_liquidity_swept_dn | 4.5% |
| smc_liquidity_swept_up | 15.9% |
| smc_ob_bearish_active | 95.5% |
| smc_ob_bullish_active | 4.5% |
| smc_ote_long_zone | 6.8% |
| smc_ote_short_zone | 15.9% |
| squeeze_in | 15.9% |
| squeeze_positive | 97.7% |
| stoch_bearish_cross | 29.5% |
| stoch_broad_overbought | 77.3% |
| stoch_broad_oversold | 2.3% |
| stoch_overbought | 75.0% |
| stochrsi_cross_dn | 50.0% |
| stochrsi_cross_up | 9.1% |
| stochrsi_overbought | 59.1% |
| stochrsi_oversold | 6.8% |
| tema_cross_up | 2.3% |
| three_black_crows | 2.3% |
| triangle_apex_break_retest_long | 22.7% |
| triangle_ascending_detected | 6.8% |
| triangle_descending_detected | 6.8% |
| uo_overbought | 11.4% |
| usd_strengthening | 20.5% |
| usd_weakening | 18.2% |
| vix_band_high | 34.1% |
| vix_band_low | 43.2% |
| vix_band_mid | 22.7% |
| vix_term_backwardation | 6.8% |
| vix_term_contango | 93.2% |
| vol_above_avg | 27.3% |
| vol_below_avg | 72.7% |
| vol_spike_12x | 18.2% |
| vol_spike_15x | 9.1% |
| vol_spike_17x | 2.3% |
| vol_spike_2x_on_up_day_recent_3d | 4.5% |
| vp_above_value_area | 40.9% |
| vp_close_above_poc | 90.9% |
| vp_close_below_poc | 9.1% |
| vp_in_value_area | 59.1% |
| week_open_gap_up_15pct | 4.5% |
| weekly_above_ema_10 | 95.5% |
| weekly_above_ema_20 | 61.4% |
| weekly_bias_bear | 4.5% |
| weekly_bias_bull | 61.4% |
| weekly_momentum_pos | 95.5% |
| williams_r_overbought | 70.5% |
| williams_r_rising | 9.1% |
| within_pead_window | 40.9% |
| xs_avoid_high_ivol | 47.7% |
| xs_avoid_high_max | 50.0% |
| xs_high_beta_decile | 40.9% |
| xs_low_beta_bottom_quintile | 40.9% |
| xs_low_beta_decile | 15.9% |
| xs_low_beta_top_quintile | 15.9% |
| xs_momentum_bottom_decile | 40.9% |
| xs_momentum_bottom_quintile | 75.0% |
| xs_quality_bottom_quintile | 17.2% |
| xs_quality_top_quintile | 34.5% |
| xs_quality_top_tercile | 51.7% |
| yoy_surprise_high | 33.3% |
| yoy_surprise_negative | 47.6% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 81.8% |
| committed_growth_holders | 81.8% |
| cot_rut_commercials_pctile_3y | 43.2% |
| cot_rut_mmoney_pctile_3y | 43.2% |
| cup_handle_depth_pct | 25.0% |
| days_since_deletion | 27.3% |
| days_to_cover | 97.7% |
| days_to_next_holiday | 68.2% |
| days_to_rebalance | 11.4% |
| dpi_30d_avg | 90.9% |
| dpi_recent | 90.9% |
| earnings_announcement_return | 95.5% |
| earnings_eps_yoy_growth | 95.5% |
| gov_contracts_4q_sum | 43.2% |
| gov_contracts_last_qtr_amount | 43.2% |
| gov_contracts_qoq_growth | 43.2% |
| head_shoulders_magnitude_pct | 11.4% |
| house_buy_count_90d | 97.7% |
| house_net_buy_90d | 97.7% |
| house_sell_count_90d | 97.7% |
| insider_director_buyers_30d | 13.6% |
| insider_officer_buyers_30d | 13.6% |
| insider_total_shares_bought_30d | 13.6% |
| insider_unique_buyers_30d | 13.6% |
| inverted_cup_handle_breakdown_level | 29.5% |
| inverted_cup_handle_height_pct | 29.5% |
| lobbying_amount_1y | 68.2% |
| lobbying_amount_q | 68.2% |
| lobbying_amount_yoy | 68.2% |
| otc_short_ratio_recent | 90.9% |
| otc_volume_recent | 90.9% |
| pair_half_life | 93.2% |
| pair_max_abs_zscore | 93.2% |
| pair_zscore_signed | 93.2% |
| pct_from_avwap_20high | 56.8% |
| persistent_holders_4q | 81.8% |
| persistent_holders_8q | 81.8% |
| search_volume_index_recent | 75.0% |
| search_volume_observations | 75.0% |
| search_volume_zscore_30d | 75.0% |
| sector_etf_return_20d | 6.8% |
| short_interest_observations | 97.7% |
| short_interest_pct | 93.2% |
| spy_return_20d | 6.8% |
| total_active_holders | 81.8% |
| triangle_breakdown_pct | 6.8% |
| triangle_breakout_pct | 6.8% |
| xs_quality_decile | 65.9% |
| xs_quality_gross_profitability | 65.9% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.992), `avwap_20low` (0.999), `avwap_252low` (0.997), `avwap_50low` (0.998), `bb_10_20_lower` (0.998), `bb_10_20_mid` (0.997), `bb_10_20_upper` (0.992), `bb_20_15_lower` (0.998), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.994), `bb_20_20_lower` (0.996), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.993), `cam_r1` (0.993), `cam_r2` (0.993), `cam_r3` (0.993), `cam_r4` (0.991), `cam_s1` (0.993), `cam_s2` (0.994), `cam_s3` (0.994), `cam_s4` (0.994), `chandelier_long_value` (0.997), `chandelier_short_value` (0.998), `cpr_bottom` (0.994), `cpr_top` (0.994), `cup_handle_breakout_level` (1.0), `cup_handle_rim` (0.991), `days_since_inclusion` (1.0), `dc10_lower` (0.998), `dc10_mid` (0.997), `dc10_upper` (0.993), `dc20_lower` (0.994), `dc20_mid` (0.998), `dc20_upper` (0.993), `dema` (0.997), `double_bottom_neckline` (1.0), `double_bottom_trough` (1.0), `double_top_neckline` (0.975), `double_top_peak` (0.975), `entry_stop_long` (0.997), `entry_stop_short` (0.989), `fib_236` (0.994), `fib_382` (0.994), `fib_500` (0.994), `fib_618` (0.994), `fib_786` (0.994), `fib_ext_127` (0.989), `fib_ext_162` (0.986), `head_shoulders_bottom_neckline` (1.0), `head_shoulders_top_neckline` (1.0), `hull_ma` (0.996), `ichi_kijun` (0.996), `ichi_senkou_a` (0.99), `ichi_senkou_b` (0.988), `ichi_tenkan` (0.997), `inverted_cup_handle_rim_low` (0.95), `kc_lower` (0.997), `kc_mid` (0.998), `kc_upper` (0.994), `monthly_close` (0.993), `monthly_sma_12` (0.979), `monthly_sma_6` (0.987), `pivot` (0.994), `prev_close` (0.993), `prev_high` (0.993), `prev_low` (0.994), `psar_value` (0.995), `r1` (0.993), `r2` (0.99), `r3` (0.989), `s1` (0.994), `s2` (0.995), `s3` (0.996), `supertrend_value` (0.997), `swing_high` (0.991), `swing_low` (0.991), `tema` (0.995), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.987), `vp_value_area_high` (0.991), `vp_value_area_low` (0.995), `vwap` (0.951), `vwap_lower_1` (0.953), `vwap_lower_2` (0.95), `weekly_close` (0.993), `weekly_ema_10` (0.995), `weekly_ema_20` (0.99), `wood_p` (0.994), `wood_r1` (0.994), `wood_r2` (0.993), `wood_s1` (0.994), `wood_s2` (0.995), `year_high` (0.96), `year_low` (0.991)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.
