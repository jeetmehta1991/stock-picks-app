# Table A - supertrend_macd_short

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 72739db05 | commit fa06ebf3e at 2026-09-19 13:07:41 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** trend | **status:** NOT-STARTED | **R5 fires:** 271 | **surviving fires (T1):** 238 (survives_pct 0.8782)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  macd_12_26_9_bearish  <- backtest/signals/screener.py
       DEFN: MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648)
       knobs P1.1-P1.1 (band rows in Table A)
P2  supertrend_flip_recent_short_5d  <- backtest/signals/screener.py +1
       DEFN: Supertrend(7, 3.0) flipped short within the last 5 bars (B655 EVENT form; technical.py:1179+)
       knobs P2.1-P2.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  adx > 20   [EXISTING-THRESHOLD]
P4  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_supertrend_macd_short (docstring and return dropped):

```python
fires = s.get('supertrend_flip_recent_short_5d') and s.get('macd_12_26_9_bearish') and (s.get('adx', 0) > 20) and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | macd_12_26_9_bearish - emitted by backtest/signals/screener.py; the boolean's UNDERLYING condition is bandable through its producer's internals | MACD(12,26,9) line vs signal, bearish/bullish state (technical.py:634-648) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | span triple (fast, slow, signal) - backtest/signals/technical.py:634-648 | MEASURED availability - both triples are emitted and macd_8_21_5_* IS persisted | (12,26,9) | [(8,21,5), (12,26,9)] both computed in production; other triples are new | the (8,21,5) SWAP - re-evaluate on persisted macd_8_21_5 keys | any third triple; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | supertrend_flip_recent_short_5d - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | Supertrend(7, 3.0) flipped short within the last 5 bars (B655 EVENT form; technical.py:1179+) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | (period, multiplier) + flip lookback - backtest/signals/technical.py:1179 + flip block | BRACKET canon (B655 EVENT conversion) | (7, 3.0) + 5d | period/mult [(7,3),(10,3),(7,2)]; lookback [3, 5, 10] | none - flip history unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | STRATEGY | adx `> 20` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `> 20` | production + 4 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P4 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | `> 20` | 100.0% | TIGHTER = RAISE the floor: 22.786 -> 190 (80%); 25.806 -> 143 (60%); 29.876 -> 95 (40%); 35.624 -> 48 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx_di_minus | backtest/signals/technical.py | 100.0% | 32.89, 36.8, 41.486, 45.862 | 32.89: 191 (80%); 36.8: 143 (60%); 41.486: 95 (40%); 45.862: 48 (20%) | 32.89: 49 (21%); 36.8: 95 (40%); 41.486: 143 (60%); 45.862: 190 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 11.27, 14.122, 18.314, 22.17 | 11.27: 191 (80%); 14.122: 143 (60%); 18.314: 95 (40%); 22.17: 48 (20%) | 11.27: 49 (21%); 14.122: 95 (40%); 18.314: 143 (60%); 22.17: 190 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -6.4797, -2.5566, 0.3089, 4.3382 | -6.4797: 190 (80%); -2.5566: 143 (60%); 0.3089: 95 (40%); 4.3382: 48 (20%) | -6.4797: 48 (20%); -2.5566: 95 (40%); 0.3089: 143 (60%); 4.3382: 190 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.6298, 2.8661, 4.287, 7.9934 | 1.6298: 190 (80%); 2.8661: 143 (60%); 4.287: 95 (40%); 7.9934: 48 (20%) | 1.6298: 48 (20%); 2.8661: 95 (40%); 4.287: 143 (60%); 7.9934: 190 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.6298, 2.8661, 4.287, 7.9934 | 1.6298: 190 (80%); 2.8661: 143 (60%); 4.287: 95 (40%); 7.9934: 48 (20%) | 1.6298: 48 (20%); 2.8661: 95 (40%); 4.287: 143 (60%); 7.9934: 190 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 2.4974, 3.0978, 3.7034, 4.958 | 2.4974: 190 (80%); 3.0978: 143 (60%); 3.7034: 95 (40%); 4.958: 48 (20%) | 2.4974: 48 (20%); 3.0978: 95 (40%); 3.7034: 143 (60%); 4.958: 190 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.1185, 0.1636, 0.2037, 0.2593 | 0.1185: 190 (80%); 0.1636: 143 (60%); 0.2037: 96 (40%); 0.2593: 48 (20%) | 0.1185: 48 (20%); 0.1636: 96 (40%); 0.2037: 143 (60%); 0.2593: 190 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | -0.1494, -0.043, 0.0412, 0.1305 | -0.1494: 190 (80%); -0.043: 143 (60%); 0.0412: 95 (40%); 0.1305: 48 (20%) | -0.1494: 48 (20%); -0.043: 95 (40%); 0.0412: 143 (60%); 0.1305: 190 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0886, 0.1111, 0.1323, 0.1831 | 0.0886: 190 (80%); 0.1111: 143 (60%); 0.1323: 95 (40%); 0.1831: 48 (20%) | 0.0886: 48 (20%); 0.1111: 97 (41%); 0.1323: 143 (60%); 0.1831: 190 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.5206, -0.3347, -0.2171, -0.0309 | -0.5206: 190 (80%); -0.3347: 143 (60%); -0.2171: 95 (40%); -0.0309: 48 (20%) | -0.5206: 48 (20%); -0.3347: 95 (40%); -0.2171: 143 (60%); -0.0309: 190 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.1181, 0.148, 0.1764, 0.2441 | 0.1181: 190 (80%); 0.148: 143 (60%); 0.1764: 95 (40%); 0.2441: 48 (20%) | 0.1181: 48 (20%); 0.148: 95 (40%); 0.1764: 143 (60%); 0.2441: 190 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | -0.2654, -0.126, -0.0379, 0.1018 | -0.2654: 190 (80%); -0.126: 143 (60%); -0.0379: 95 (40%); 0.1018: 48 (20%) | -0.2654: 48 (20%); -0.126: 95 (40%); -0.0379: 143 (60%); 0.1018: 190 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0533, -0.021, 0.0014, 0.0777 | -0.0533: 190 (80%); -0.021: 143 (60%); 0.0014: 95 (40%); 0.0777: 48 (20%) | -0.0533: 48 (20%); -0.021: 97 (41%); 0.0014: 143 (60%); 0.0777: 190 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1461, 0.1757, 0.1838, 0.2159 | 0.1461: 190 (80%); 0.1757: 143 (60%); 0.1838: 84 (35%); 0.2159: 48 (20%) | 0.1461: 48 (20%); 0.1757: 95 (40%); 0.1838: 154 (65%); 0.2159: 190 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 238 (100%) | 0: 233 (98%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1959, -0.1355, -0.0529, 0.0382 | -0.1959: 190 (80%); -0.1355: 143 (60%); -0.0529: 96 (40%); 0.0382: 48 (20%) | -0.1959: 48 (20%); -0.1355: 95 (40%); -0.0529: 143 (60%); 0.0382: 190 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 238 (100%); 1: 79 (33%) | 0: 159 (67%); 1: 208 (87%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2319, -0.1936, -0.1554, -0.14 | -0.2319: 190 (80%); -0.1936: 144 (61%); -0.1554: 95 (40%); -0.14: 74 (31%) | -0.2319: 48 (20%); -0.1936: 97 (41%); -0.1554: 143 (60%); -0.14: 192 (81%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4744, 0.6026, 0.6667, 0.7666 | 0.4744: 192 (81%); 0.6026: 144 (61%); 0.6667: 117 (49%); 0.7666: 48 (20%) | 0.4744: 54 (23%); 0.6026: 97 (41%); 0.6667: 155 (65%); 0.7666: 190 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.3103, 0.5359, 0.7372, 0.8654 | 0.3103: 190 (80%); 0.5359: 143 (60%); 0.7372: 98 (41%); 0.8654: 50 (21%) | 0.3103: 48 (20%); 0.5359: 95 (40%); 0.7372: 144 (61%); 0.8654: 192 (81%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1578, -0.0377, 0.0117, 0.0995 | -0.1578: 190 (80%); -0.0377: 143 (60%); 0.0117: 115 (48%); 0.0995: 48 (20%) | -0.1578: 48 (20%); -0.0377: 95 (40%); 0.0117: 151 (63%); 0.0995: 190 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.1757, 0.3833, 0.4808, 0.7089 | 0.1757: 190 (80%); 0.3833: 143 (60%); 0.4808: 97 (41%); 0.7089: 48 (20%) | 0.1757: 48 (20%); 0.3833: 95 (40%); 0.4808: 146 (61%); 0.7089: 190 (80%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1667, 0.3513, 0.4385, 0.6256 | 0.1667: 192 (81%); 0.3513: 143 (60%); 0.4385: 95 (40%); 0.6256: 48 (20%) | 0.1667: 54 (23%); 0.3513: 95 (40%); 0.4385: 143 (60%); 0.6256: 190 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.4146, -0.1957, -0.0978, 0.0949 | -0.4146: 191 (80%); -0.1957: 148 (62%); -0.0978: 120 (50%); 0.0949: 48 (20%) | -0.4146: 49 (21%); -0.1957: 99 (42%); -0.0978: 146 (61%); 0.0949: 190 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4308, 0.7051, 0.8205, 0.9589 | 0.4308: 190 (80%); 0.7051: 149 (63%); 0.8205: 125 (53%); 0.9589: 48 (20%) | 0.4308: 48 (20%); 0.7051: 99 (42%); 0.8205: 156 (66%); 0.9589: 190 (80%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.109, 0.4231, 0.7244, 0.8526 | 0.109: 193 (81%); 0.4231: 147 (62%); 0.7244: 97 (41%); 0.8526: 55 (23%) | 0.109: 49 (21%); 0.4231: 98 (41%); 0.7244: 170 (71%); 0.8526: 198 (83%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0614, -0.0444, 0 | -0.0614: 193 (81%); -0.0444: 145 (61%); 0: 105 (44%) | -0.0614: 50 (21%); -0.0444: 99 (42%); 0: 235 (99%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4936, 0.7051, 0.9936, 1 | 0.4936: 194 (82%); 0.7051: 148 (62%); 0.9936: 102 (43%); 1: 93 (39%) | 0.4936: 50 (21%); 0.7051: 97 (41%); 0.9936: 145 (61%); 1: 238 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1923, 0.3205, 0.5449, 0.9128 | 0.1923: 193 (81%); 0.3205: 159 (67%); 0.5449: 96 (40%); 0.9128: 48 (20%) | 0.1923: 57 (24%); 0.3205: 96 (40%); 0.5449: 147 (62%); 0.9128: 190 (80%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0099, 0.0362, 0.0911, 0.1507 | -0.0099: 198 (83%); 0.0362: 143 (60%); 0.0911: 109 (46%); 0.1507: 48 (20%) | -0.0099: 49 (21%); 0.0362: 95 (40%); 0.0911: 157 (66%); 0.1507: 190 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.5211, 0.7692, 0.9103, 0.9589 | 0.5211: 197 (83%); 0.7692: 150 (63%); 0.9103: 100 (42%); 0.9589: 48 (20%) | 0.5211: 50 (21%); 0.7692: 116 (49%); 0.9103: 146 (61%); 0.9589: 190 (80%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2141, 0.4295, 0.5577, 0.7628 | 0.2141: 190 (80%); 0.4295: 145 (61%); 0.5577: 102 (43%); 0.7628: 50 (21%) | 0.2141: 48 (20%); 0.4295: 121 (51%); 0.5577: 144 (61%); 0.7628: 191 (80%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0203, 0.0525, 0.1225 | -0.0812: 209 (88%); -0.0203: 152 (64%); 0.0525: 113 (47%); 0.1225: 54 (23%) | -0.0812: 63 (26%); -0.0203: 101 (42%); 0.0525: 153 (64%); 0.1225: 191 (80%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2448, -0.0216, 0.0617, 0.1106 | -0.2448: 190 (80%); -0.0216: 150 (63%); 0.0617: 95 (40%); 0.1106: 50 (21%) | -0.2448: 48 (20%); -0.0216: 97 (41%); 0.0617: 143 (60%); 0.1106: 191 (80%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2628, 0.5359, 0.7577, 0.9808 | 0.2628: 196 (82%); 0.5359: 143 (60%); 0.7577: 95 (40%); 0.9808: 50 (21%) | 0.2628: 57 (24%); 0.5359: 95 (40%); 0.7577: 143 (60%); 0.9808: 201 (84%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2115, 0.4782, 0.7436, 0.8269 | 0.2115: 203 (85%); 0.4782: 143 (60%); 0.7436: 96 (40%); 0.8269: 58 (24%) | 0.2115: 64 (27%); 0.4782: 95 (40%); 0.7436: 147 (62%); 0.8269: 194 (82%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0729, 0.1867, 0.4311, 1.0226 | 0.0729: 190 (80%); 0.1867: 144 (61%); 0.4311: 95 (40%); 1.0226: 48 (20%) | 0.0729: 48 (20%); 0.1867: 96 (40%); 0.4311: 143 (60%); 1.0226: 190 (80%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 98.7% | 1.8436, 2.3291, 2.7315, 3.4435 | 1.8436: 188 (79%); 2.3291: 141 (59%); 2.7315: 94 (39%); 3.4435: 47 (20%) | 1.8436: 47 (20%); 2.3291: 94 (39%); 2.7315: 141 (59%); 3.4435: 188 (79%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 7, 20, 33, 41 | 7: 192 (81%); 20: 144 (61%); 33: 101 (42%); 41: 53 (22%) | 7: 55 (23%); 20: 100 (42%); 33: 163 (68%); 41: 196 (82%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3, 4 | 1: 213 (89%); 2: 154 (65%); 3: 115 (48%); 4: 60 (25%) | 1: 84 (35%); 2: 123 (52%); 3: 178 (75%); 4: 238 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0059, -0.0015, 0.0068, 0.019 | -0.0059: 191 (80%); -0.0015: 143 (60%); 0.0068: 98 (41%); 0.019: 49 (21%) | -0.0059: 51 (21%); -0.0015: 95 (40%); 0.0068: 147 (62%); 0.019: 192 (81%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.7965, 26.3535, 26.8208, 27.3267 | 24.7965: 190 (80%); 26.3535: 143 (60%); 26.8208: 95 (40%); 27.3267: 54 (23%) | 24.7965: 48 (20%); 26.3535: 95 (40%); 26.8208: 143 (60%); 27.3267: 208 (87%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.8344, -0.0446, 0.8742, 4.963 | -0.8344: 190 (80%); -0.0446: 143 (60%); 0.8742: 95 (40%); 4.963: 49 (21%) | -0.8344: 48 (20%); -0.0446: 95 (40%); 0.8742: 143 (60%); 4.963: 191 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -4.963, -0.8742, 0.0446, 0.8344 | -4.963: 191 (80%); -0.8742: 143 (60%); 0.0446: 95 (40%); 0.8344: 48 (20%) | -4.963: 49 (21%); -0.8742: 95 (40%); 0.0446: 143 (60%); 0.8344: 190 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.028, -0.0009, 0.0354, 0.1035 | -0.028: 190 (80%); -0.0009: 143 (60%); 0.0354: 95 (40%); 0.1035: 49 (21%) | -0.028: 48 (20%); -0.0009: 96 (40%); 0.0354: 143 (60%); 0.1035: 191 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.3005, 8.5865, 8.8904, 9.3673 | 8.3005: 191 (80%); 8.5865: 143 (60%); 8.8904: 93 (39%); 9.3673: 48 (20%) | 8.3005: 47 (20%); 8.5865: 95 (40%); 8.8904: 145 (61%); 9.3673: 190 (80%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 3, 7, 192, 290.6 | 3: 203 (85%); 7: 150 (63%); 192: 96 (40%); 290.6: 48 (20%) | 3: 49 (21%); 7: 96 (40%); 192: 145 (61%); 290.6: 190 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 2.4, 49.4, 108.2, 153.2 | 2.4: 190 (80%); 49.4: 143 (60%); 108.2: 95 (40%); 153.2: 48 (20%) | 2.4: 48 (20%); 49.4: 95 (40%); 108.2: 143 (60%); 153.2: 190 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -3.0093, -1.4974, -0.8133, -0.4161 | -3.0093: 190 (80%); -1.4974: 143 (60%); -0.8133: 95 (40%); -0.4161: 48 (20%) | -3.0093: 48 (20%); -1.4974: 95 (40%); -0.8133: 143 (60%); -0.4161: 190 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -2.4111, -0.8969, 0.2485, 1.4979 | -2.4111: 190 (80%); -0.8969: 143 (60%); 0.2485: 95 (40%); 1.4979: 48 (20%) | -2.4111: 48 (20%); -0.8969: 95 (40%); 0.2485: 143 (60%); 1.4979: 190 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -1.0493, 0.2184, 1.2718, 2.8995 | -1.0493: 190 (80%); 0.2184: 143 (60%); 1.2718: 95 (40%); 2.8995: 48 (20%) | -1.0493: 48 (20%); 0.2184: 95 (40%); 1.2718: 143 (60%); 2.8995: 190 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -3.7267, -1.8458, -1.0563, -0.5505 | -3.7267: 190 (80%); -1.8458: 143 (60%); -1.0563: 95 (40%); -0.5505: 48 (20%) | -3.7267: 48 (20%); -1.8458: 95 (40%); -1.0563: 143 (60%); -0.5505: 190 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -4.2145, -1.8441, -0.5598, 0.6666 | -4.2145: 190 (80%); -1.8441: 143 (60%); -0.5598: 95 (40%); 0.6666: 48 (20%) | -4.2145: 48 (20%); -1.8441: 95 (40%); -0.5598: 143 (60%); 0.6666: 190 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -2.0712, -0.61, 0.3964, 2.1459 | -2.0712: 190 (80%); -0.61: 143 (60%); 0.3964: 95 (40%); 2.1459: 48 (20%) | -2.0712: 48 (20%); -0.61: 95 (40%); 0.3964: 143 (60%); 2.1459: 190 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 28.444, 35.618, 43.364, 53.186 | 28.444: 190 (80%); 35.618: 143 (60%); 43.364: 95 (40%); 53.186: 48 (20%) | 28.444: 48 (20%); 35.618: 95 (40%); 43.364: 143 (60%); 53.186: 190 (80%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.2% | 0.0092, 0.0199, 0.0371, 0.084 | 0.0092: 189 (79%); 0.0199: 142 (60%); 0.0371: 94 (39%); 0.084: 48 (20%) | 0.0092: 47 (20%); 0.0199: 94 (39%); 0.0371: 142 (60%); 0.084: 188 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 1, 2, 7, 17.6 | 1: 196 (82%); 2: 157 (66%); 7: 97 (41%); 17.6: 48 (20%) | 1: 81 (34%); 2: 100 (42%); 7: 144 (61%); 17.6: 190 (80%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1667, 0.3333 | 0: 238 (100%); 0.1667: 97 (41%); 0.3333: 52 (22%) | 0: 98 (41%); 0.1667: 144 (61%); 0.3333: 196 (82%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3213, 0.4692, 0.63 | 0: 238 (100%); 0.3213: 143 (60%); 0.4692: 95 (40%); 0.63: 48 (20%) | 0: 75 (32%); 0.3213: 95 (40%); 0.4692: 143 (60%); 0.63: 190 (80%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 2, 6, 14.6 | 0: 238 (100%); 2: 149 (63%); 6: 96 (40%); 14.6: 48 (20%) | 0: 53 (22%); 2: 108 (45%); 6: 149 (63%); 14.6: 190 (80%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 1, 2, 7, 17.6 | 1: 196 (82%); 2: 157 (66%); 7: 97 (41%); 17.6: 48 (20%) | 1: 81 (34%); 2: 100 (42%); 7: 144 (61%); 17.6: 190 (80%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 2, 7 | 0: 238 (100%); 1: 155 (65%); 2: 116 (49%); 7: 54 (23%) | 0: 83 (35%); 1: 122 (51%); 2: 146 (61%); 7: 191 (80%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2346, 0.3822, 0.5847 | 0: 216 (91%); 0.2346: 143 (60%); 0.3822: 95 (40%); 0.5847: 48 (20%) | 0: 55 (23%); 0.2346: 95 (40%); 0.3822: 143 (60%); 0.5847: 190 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.0798, 0, 0.1245, 0.3832 | -0.0798: 190 (80%); 0: 183 (77%); 0.1245: 95 (40%); 0.3832: 48 (20%) | -0.0798: 48 (20%); 0: 125 (53%); 0.1245: 143 (60%); 0.3832: 190 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.2737, 0.5 | 0: 198 (83%); 0.2737: 95 (40%); 0.5: 52 (22%) | 0: 97 (41%); 0.2737: 143 (60%); 0.5: 196 (82%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.2737, 0.5 | 0: 198 (83%); 0.2737: 95 (40%); 0.5: 52 (22%) | 0: 97 (41%); 0.2737: 143 (60%); 0.5: 196 (82%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.3278, 0 | -0.3278: 190 (80%); 0: 151 (63%) | -0.3278: 48 (20%); 0: 191 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.5394, 1.8074, 4.7331 | 0: 192 (81%); 0.5394: 146 (61%); 1.8074: 95 (40%); 4.7331: 48 (20%) | 0: 83 (35%); 0.5394: 96 (40%); 1.8074: 143 (60%); 4.7331: 190 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 5, 8, 13 | 2: 202 (85%); 5: 145 (61%); 8: 104 (44%); 13: 53 (22%) | 2: 55 (23%); 5: 107 (45%); 8: 147 (62%); 13: 192 (81%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.1695, -0.1215, -0.0941, -0.0578 | -0.1695: 190 (80%); -0.1215: 143 (60%); -0.0941: 95 (40%); -0.0578: 48 (20%) | -0.1695: 48 (20%); -0.1215: 95 (40%); -0.0941: 143 (60%); -0.0578: 190 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.17, -0.1144, -0.0699, -0.0204 | -0.17: 190 (80%); -0.1144: 143 (60%); -0.0699: 95 (40%); -0.0204: 48 (20%) | -0.17: 48 (20%); -0.1144: 95 (40%); -0.0699: 143 (60%); -0.0204: 190 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.1611, -0.1281, -0.1005, -0.0655 | -0.1611: 190 (80%); -0.1281: 143 (60%); -0.1005: 95 (40%); -0.0655: 48 (20%) | -0.1611: 48 (20%); -0.1281: 95 (40%); -0.1005: 143 (60%); -0.0655: 190 (80%) | OFFLINE |
| pct_from_avwap_20high | backtest/signals/screener.py | 100.0% | -10.8682, -8.2752, -6.5208, -4.348 | -10.8682: 190 (80%); -8.2752: 143 (60%); -6.5208: 95 (40%); -4.348: 48 (20%) | -10.8682: 48 (20%); -8.2752: 95 (40%); -6.5208: 143 (60%); -4.348: 190 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -22.3748, -3.2186, 11.4684, 31.934 | -22.3748: 190 (80%); -3.2186: 143 (60%); 11.4684: 95 (40%); 31.934: 48 (20%) | -22.3748: 48 (20%); -3.2186: 95 (40%); 11.4684: 143 (60%); 31.934: 190 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0419, 0.0755, 0.1184, 0.1762 | 0.0419: 190 (80%); 0.0755: 143 (60%); 0.1184: 95 (40%); 0.1762: 48 (20%) | 0.0419: 48 (20%); 0.0755: 95 (40%); 0.1184: 143 (60%); 0.1762: 190 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.0699, 0.1352, 0.2433, 0.4122 | 0.0699: 190 (80%); 0.1352: 143 (60%); 0.2433: 95 (40%); 0.4122: 48 (20%) | 0.0699: 48 (20%); 0.1352: 95 (40%); 0.2433: 143 (60%); 0.4122: 190 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -2.5107, -1.0485, 0.3152, 1.1989 | -2.5107: 190 (80%); -1.0485: 143 (60%); 0.3152: 95 (40%); 1.1989: 48 (20%) | -2.5107: 48 (20%); -1.0485: 95 (40%); 0.3152: 143 (60%); 1.1989: 190 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -1.7143, -1.3125, -0.8893, -0.5559 | -1.7143: 190 (80%); -1.3125: 143 (60%); -0.8893: 95 (40%); -0.5559: 48 (20%) | -1.7143: 48 (20%); -1.3125: 95 (40%); -0.8893: 143 (60%); -0.5559: 190 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.2467, 0.2613, 1.2115, 2.0951 | -1.2467: 190 (80%); 0.2613: 143 (60%); 1.2115: 95 (40%); 2.0951: 48 (20%) | -1.2467: 48 (20%); 0.2613: 95 (40%); 1.2115: 143 (60%); 2.0951: 190 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -16.5416, -12.4226, -8.6268, -4.9304 | -16.5416: 190 (80%); -12.4226: 143 (60%); -8.6268: 95 (40%); -4.9304: 48 (20%) | -16.5416: 48 (20%); -12.4226: 95 (40%); -8.6268: 143 (60%); -4.9304: 190 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 23.342, 29.112, 34.308, 39.414 | 23.342: 190 (80%); 29.112: 143 (60%); 34.308: 95 (40%); 39.414: 48 (20%) | 23.342: 48 (20%); 29.112: 95 (40%); 34.308: 143 (60%); 39.414: 190 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 1.482, 3.328, 5.474, 12.996 | 1.482: 190 (80%); 3.328: 143 (60%); 5.474: 95 (40%); 12.996: 48 (20%) | 1.482: 48 (20%); 3.328: 95 (40%); 5.474: 143 (60%); 12.996: 190 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 30.092, 34.97, 39.814, 44.75 | 30.092: 190 (80%); 34.97: 144 (61%); 39.814: 95 (40%); 44.75: 48 (20%) | 30.092: 48 (20%); 34.97: 96 (40%); 39.814: 143 (60%); 44.75: 190 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 16.896, 22.204, 26.57, 31.976 | 16.896: 190 (80%); 22.204: 143 (60%); 26.57: 95 (40%); 31.976: 48 (20%) | 16.896: 48 (20%); 22.204: 95 (40%); 26.57: 143 (60%); 31.976: 190 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 237 (100%) | 0: 238 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0335, 0.0494, 0.0604, 0.0869 | 0.0335: 192 (81%); 0.0494: 143 (60%); 0.0604: 95 (40%); 0.0869: 61 (26%) | 0.0335: 49 (21%); 0.0494: 98 (41%); 0.0604: 143 (60%); 0.0869: 201 (84%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0674, -0.0453, -0.0401, -0.031 | -0.0674: 191 (80%); -0.0453: 144 (61%); -0.0401: 95 (40%); -0.031: 48 (20%) | -0.0674: 50 (21%); -0.0453: 96 (40%); -0.0401: 143 (60%); -0.031: 191 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 238 (100%); 2: 64 (27%) | 0: 153 (64%); 2: 196 (82%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 98.7% | 37, 50, 62, 65.2 | 37: 193 (81%); 50: 144 (61%); 62: 96 (40%); 65.2: 47 (20%) | 37: 50 (21%); 50: 97 (41%); 62: 143 (60%); 65.2: 188 (79%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.0395, 0.1015, 0.2398, 0.4492 | 0.0395: 190 (80%); 0.1015: 143 (60%); 0.2398: 96 (40%); 0.4492: 48 (20%) | 0.0395: 48 (20%); 0.1015: 95 (40%); 0.2398: 143 (60%); 0.4492: 190 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 37.6, 72.46, 108.92, 193.14 | 37.6: 190 (80%); 72.46: 143 (60%); 108.92: 95 (40%); 193.14: 48 (20%) | 37.6: 48 (20%); 72.46: 95 (40%); 108.92: 143 (60%); 193.14: 190 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -18.438, -9.93, -5.701, -3.097 | -18.438: 190 (80%); -9.93: 143 (60%); -5.701: 95 (40%); -3.097: 48 (20%) | -18.438: 48 (20%); -9.93: 95 (40%); -5.701: 143 (60%); -3.097: 190 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 16.478, 26.71, 44.488, 66.174 | 16.478: 190 (80%); 26.71: 143 (60%); 44.488: 95 (40%); 66.174: 48 (20%) | 16.478: 48 (20%); 26.71: 95 (40%); 44.488: 143 (60%); 66.174: 190 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 9.92, 17.624, 28.624, 50.016 | 9.92: 191 (80%); 17.624: 143 (60%); 28.624: 95 (40%); 50.016: 48 (20%) | 9.92: 49 (21%); 17.624: 95 (40%); 28.624: 143 (60%); 50.016: 190 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 0.898, 6.22, 19.804, 44.78 | 0.898: 190 (80%); 6.22: 143 (60%); 19.804: 95 (40%); 44.78: 48 (20%) | 0.898: 48 (20%); 6.22: 95 (40%); 19.804: 143 (60%); 44.78: 190 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 0, 8.854 | 0: 238 (100%); 8.854: 48 (20%) | 0: 152 (64%); 8.854: 190 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 4, 5.8, 10, 17 | 4: 194 (82%); 5.8: 143 (60%); 10: 107 (45%); 17: 53 (22%) | 4: 84 (35%); 5.8: 95 (40%); 10: 144 (61%); 17: 194 (82%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 5, 11, 17, 18 | 5: 195 (82%); 11: 145 (61%); 17: 96 (40%); 18: 83 (35%) | 5: 53 (22%); 11: 98 (41%); 17: 155 (65%); 18: 194 (82%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 29.718, 33.364, 37.008, 41.626 | 29.718: 190 (80%); 33.364: 143 (60%); 37.008: 95 (40%); 41.626: 48 (20%) | 29.718: 48 (20%); 33.364: 95 (40%); 37.008: 143 (60%); 41.626: 190 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.2135, 0.4921, 0.7349, 0.9683 | 0.2135: 190 (80%); 0.4921: 149 (63%); 0.7349: 95 (40%); 0.9683: 51 (21%) | 0.2135: 48 (20%); 0.4921: 96 (40%); 0.7349: 143 (60%); 0.9683: 191 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 15.352, 16.928, 19.55, 31.104 | 15.352: 190 (80%); 16.928: 143 (60%); 19.55: 95 (40%); 31.104: 48 (20%) | 15.352: 48 (20%); 16.928: 95 (40%); 19.55: 143 (60%); 31.104: 190 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 15.352, 16.928, 19.55, 31.104 | 15.352: 190 (80%); 16.928: 143 (60%); 19.55: 95 (40%); 31.104: 48 (20%) | 15.352: 48 (20%); 16.928: 95 (40%); 19.55: 143 (60%); 31.104: 190 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8692, 0.8984, 0.9525, 1.0246 | 0.8692: 190 (80%); 0.8984: 146 (61%); 0.9525: 95 (40%); 1.0246: 48 (20%) | 0.8692: 48 (20%); 0.8984: 97 (41%); 0.9525: 143 (60%); 1.0246: 190 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 1.2, 1.628, 2.334, 3.616 | 1.2: 191 (80%); 1.628: 143 (60%); 2.334: 95 (40%); 3.616: 48 (20%) | 1.2: 49 (21%); 1.628: 95 (40%); 2.334: 143 (60%); 3.616: 190 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0273, 0.0658, 0.1111, 0.1653 | 0.0273: 191 (80%); 0.0658: 143 (60%); 0.1111: 95 (40%); 0.1653: 48 (20%) | 0.0273: 48 (20%); 0.0658: 95 (40%); 0.1111: 143 (60%); 0.1653: 190 (80%) | OFFLINE |
| vwap | backtest/signals/screener.py +1 | 100.0% | 52.9078, 77.1424, 112.6286, 209.9757 | 52.9078: 190 (80%); 77.1424: 143 (60%); 112.6286: 95 (40%); 209.9757: 48 (20%) | 52.9078: 48 (20%); 77.1424: 95 (40%); 112.6286: 143 (60%); 209.9757: 190 (80%) | OFFLINE |
| vwap_lower_1 | backtest/signals/technical.py | 100.0% | 49.0091, 73.2782, 102.6817, 200.0108 | 49.0091: 190 (80%); 73.2782: 143 (60%); 102.6817: 95 (40%); 200.0108: 48 (20%) | 49.0091: 48 (20%); 73.2782: 95 (40%); 102.6817: 143 (60%); 200.0108: 190 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 45.0134, 67.3815, 98.5607, 192.3034 | 45.0134: 190 (80%); 67.3815: 143 (60%); 98.5607: 95 (40%); 192.3034: 48 (20%) | 45.0134: 48 (20%); 67.3815: 95 (40%); 98.5607: 143 (60%); 192.3034: 190 (80%) | OFFLINE |
| vwap_upper_1 | backtest/signals/technical.py | 100.0% | 55.8249, 81.6966, 119.3111, 220.2336 | 55.8249: 190 (80%); 81.6966: 143 (60%); 119.3111: 95 (40%); 220.2336: 48 (20%) | 55.8249: 48 (20%); 81.6966: 95 (40%); 119.3111: 143 (60%); 220.2336: 190 (80%) | OFFLINE |
| vwap_upper_2 | backtest/signals/technical.py | 100.0% | 57.7965, 85.989, 125.7084, 228.9187 | 57.7965: 190 (80%); 85.989: 143 (60%); 125.7084: 95 (40%); 228.9187: 48 (20%) | 57.7965: 48 (20%); 85.989: 95 (40%); 125.7084: 143 (60%); 228.9187: 190 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 238 (100%) | 0: 217 (91%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 238 (100%) | 0: 230 (97%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.1695, -0.115, -0.0753, -0.0232 | -0.1695: 190 (80%); -0.115: 143 (60%); -0.0753: 95 (40%); -0.0232: 48 (20%) | -0.1695: 48 (20%); -0.115: 96 (40%); -0.0753: 143 (60%); -0.0232: 190 (80%) | OFFLINE |
| williams_r | backtest/signals/screener.py +1 | 100.0% | -97.356, -94.908, -91.198, -83.736 | -97.356: 190 (80%); -94.908: 143 (60%); -91.198: 95 (40%); -83.736: 48 (20%) | -97.356: 48 (20%); -94.908: 95 (40%); -91.198: 143 (60%); -83.736: 190 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 98.3% | 0.4655, 0.7826, 1.0002, 1.2792 | 0.4655: 187 (79%); 0.7826: 140 (59%); 1.0002: 94 (39%); 1.2792: 47 (20%) | 0.4655: 47 (20%); 0.7826: 94 (39%); 1.0002: 140 (59%); 1.2792: 187 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 98.3% | 3, 5, 7, 9 | 3: 192 (81%); 5: 148 (62%); 7: 101 (42%); 9: 55 (23%) | 3: 57 (24%); 5: 111 (47%); 7: 155 (65%); 9: 200 (84%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 98.7% | -0.0904, 0.0558, 0.191, 0.3968 | -0.0904: 188 (79%); 0.0558: 142 (60%); 0.191: 94 (39%); 0.3968: 47 (20%) | -0.0904: 47 (20%); 0.0558: 95 (40%); 0.191: 141 (59%); 0.3968: 188 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 98.7% | 3, 6, 8, 9 | 3: 198 (83%); 6: 144 (61%); 8: 100 (42%); 9: 73 (31%) | 3: 55 (23%); 6: 113 (47%); 8: 162 (68%); 9: 190 (80%) | OFFLINE |
| year_low | backtest/signals/technical.py | 100.0% | 34.2784, 63.4002, 89.408, 163.883 | 34.2784: 190 (80%); 63.4002: 143 (60%); 89.408: 95 (40%); 163.883: 48 (20%) | 34.2784: 48 (20%); 63.4002: 95 (40%); 89.408: 143 (60%); 163.883: 190 (80%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.8% |
| 8k_item_5_02_filed_within_7d | 4.4% |
| above_avwap_20high | 0.4% |
| above_avwap_20low | 15.1% |
| above_avwap_252low | 51.1% |
| above_avwap_50low | 18.1% |
| above_cam_r3 | 2.5% |
| above_cam_r4 | 0.4% |
| above_cpr | 13.9% |
| above_pivot | 11.3% |
| above_prev_high | 2.1% |
| above_prev_high_clearance_atr_05 | 0.4% |
| above_prev_low | 35.3% |
| above_r1 | 0.8% |
| above_r2 | 0.4% |
| above_vwap | 55.5% |
| above_wood_p | 15.1% |
| ad_rising | 8.8% |
| adx_cross_up | 9.2% |
| adx_cross_up_20 | 10.9% |
| adx_di_bear | 98.7% |
| adx_di_bull | 1.3% |
| adx_strong | 7.6% |
| adx_trending | 66.0% |
| ao_cross_dn | 13.0% |
| ao_positive | 42.9% |
| ao_twin_peaks_bull | 0.4% |
| at_key_fib | 13.9% |
| at_key_fib_wide | 29.4% |
| avwap_20high_loss_recent_3d | 31.9% |
| avwap_20high_reclaim_recent_3d | 0.4% |
| avwap_20low_loss_recent_3d | 55.6% |
| avwap_20low_reclaim_recent_3d | 10.0% |
| avwap_252low_loss_recent_3d | 38.4% |
| avwap_252low_reclaim_recent_3d | 2.3% |
| avwap_50low_loss_recent_3d | 66.0% |
| avwap_50low_reclaim_recent_3d | 4.7% |
| bb_10_20_expanding | 99.2% |
| bb_10_20_pctb_lt_05 | 61.3% |
| bb_10_20_pctb_lt_1 | 76.1% |
| bb_10_20_pctb_lt_15 | 87.8% |
| bb_10_20_pctb_lt_2 | 93.3% |
| bb_10_20_pctb_lt_25 | 97.9% |
| bb_10_20_reclaim_from_lower_recent_3d | 40.8% |
| bb_10_20_reclaim_from_upper_recent_3d | 1.3% |
| bb_10_20_squeeze | 5.0% |
| bb_10_20_touch_lower | 53.8% |
| bb_20_15_expanding | 87.8% |
| bb_20_15_pctb_lt_05 | 85.7% |
| bb_20_15_pctb_lt_1 | 87.8% |
| bb_20_15_pctb_lt_15 | 91.6% |
| bb_20_15_pctb_lt_2 | 92.0% |
| bb_20_15_pctb_lt_25 | 93.7% |
| bb_20_15_reclaim_from_lower_recent_3d | 2.9% |
| bb_20_15_reclaim_from_upper_recent_3d | 5.9% |
| bb_20_15_squeeze | 15.5% |
| bb_20_15_touch_lower | 85.7% |
| bb_20_20_expanding | 87.8% |
| bb_20_20_pctb_lt_05 | 73.1% |
| bb_20_20_pctb_lt_1 | 79.8% |
| bb_20_20_pctb_lt_15 | 85.3% |
| bb_20_20_pctb_lt_2 | 87.8% |
| bb_20_20_pctb_lt_25 | 92.0% |
| bb_20_20_reclaim_from_lower_recent_3d | 8.4% |
| bb_20_20_reclaim_from_upper_recent_3d | 0.8% |
| bb_20_20_squeeze | 5.5% |
| bb_20_20_touch_lower | 71.4% |
| bearish_engulfing | 4.2% |
| bearish_pin_bar | 3.8% |
| below_avwap_20high | 99.6% |
| below_avwap_20low | 84.9% |
| below_avwap_252low | 48.9% |
| below_avwap_50low | 81.9% |
| below_cam_s3 | 63.9% |
| below_cam_s4 | 50.8% |
| below_cpr | 88.7% |
| below_ema_200 | 60.9% |
| below_ema_200_break_recent_5d | 40.7% |
| below_ema_20_break_recent_5d | 71.8% |
| below_ema_21_break_recent_5d | 71.8% |
| below_ema_50 | 91.6% |
| below_ema_50_break_recent_5d | 64.7% |
| below_ema_9 | 99.6% |
| below_ema_9_break_recent_5d | 76.5% |
| below_prev_high | 97.9% |
| below_prev_low | 64.7% |
| below_prev_low_clearance_atr_05 | 51.3% |
| below_s1 | 55.0% |
| below_s2 | 44.5% |
| below_sma_200 | 56.3% |
| below_sma_50 | 86.1% |
| below_vwap | 44.5% |
| blowoff_recent_3d | 0.8% |
| break_52w_low | 6.7% |
| bullish_pin_bar | 2.5% |
| ceo_buy | 0.4% |
| cfo_buy | 0.4% |
| chandelier_long_bullish | 2.1% |
| chandelier_long_flip_dn | 32.8% |
| chandelier_short_bearish | 95.8% |
| chandelier_short_flip_up | 1.3% |
| close_in_bottom_40pct_of_range | 79.0% |
| close_in_top_40pct_of_range | 6.7% |
| cmf_cross_dn | 18.9% |
| cmf_cross_up | 1.3% |
| cmf_negative | 70.2% |
| cmf_positive | 29.8% |
| concentrated_sell | 4.4% |
| cpr_narrow | 86.6% |
| cpr_narrow_tight | 25.2% |
| cup_handle_detected | 7.6% |
| dc10_breakout_dn | 65.1% |
| dc10_breakout_dn_1pct | 73.5% |
| dc10_strong_breakout_dn | 46.2% |
| dc20_breakout_dn | 51.7% |
| dc20_support_break_retest_strong | 22.3% |
| defensive_leadership | 61.8% |
| director_only_buy | 1.3% |
| doji | 2.9% |
| double_bottom_detected | 15.5% |
| double_top_detected | 16.4% |
| dpi_elevated | 39.0% |
| drying_volume_on_down_turn | 8.8% |
| ema_20_50_bearish | 35.7% |
| ema_20_50_bullish | 64.3% |
| ema_20_50_death_cross | 4.2% |
| ema_50_200_bearish | 26.9% |
| ema_50_200_bullish | 73.1% |
| ema_50_200_death_cross | 0.8% |
| ema_9_21_bearish | 66.8% |
| ema_9_21_bullish | 33.2% |
| ema_9_21_death_cross | 15.5% |
| evening_star | 16.8% |
| flag_bear_break_retest_short | 0.4% |
| flag_bear_broke | 1.7% |
| force_index_cross_dn | 24.8% |
| gap_dn_1_5pct | 35.3% |
| gap_dn_2pct | 32.8% |
| gap_up_1_5pct | 15.5% |
| gap_up_2pct | 12.2% |
| hammer | 2.1% |
| head_shoulders_bottom_detected | 3.8% |
| head_shoulders_top_detected | 2.1% |
| house_cluster_buy | 4.3% |
| house_cluster_sell | 3.9% |
| htf_aligned_bear | 47.9% |
| htf_aligned_bull | 7.6% |
| htf_disagreement | 3.8% |
| hull_bearish | 99.2% |
| hull_bullish | 0.8% |
| hull_flip_dn | 21.8% |
| ichi_above_cloud | 24.4% |
| ichi_above_cloud_break_recent_5d | 0.4% |
| ichi_below_cloud | 59.7% |
| ichi_below_cloud_break_recent_5d | 39.1% |
| ichi_cloud_thick | 90.3% |
| ichi_tk_bearish | 47.5% |
| ichi_tk_bullish | 23.1% |
| ichi_tk_cross_dn | 5.5% |
| ichi_weekly_above_cloud | 44.6% |
| ichi_weekly_below_cloud | 37.7% |
| ichi_weekly_in_cloud | 17.7% |
| inside_bar | 13.0% |
| inside_cpr | 0.4% |
| inside_kc | 22.3% |
| insider_cluster_active | 36.4% |
| institutional_buy | 91.6% |
| institutional_negative | 2.1% |
| institutional_persistence_growing | 52.1% |
| institutional_persistence_strong | 68.9% |
| institutional_strong_buy | 86.1% |
| inverted_cup_handle_detected | 3.4% |
| is_friday | 25.2% |
| is_halloween_period | 59.2% |
| is_halloween_period_first_day | 1.7% |
| is_january | 9.2% |
| is_january_extended | 11.8% |
| is_monday | 10.5% |
| is_pre_holiday | 0.8% |
| is_summer_period | 40.8% |
| is_totm_window | 36.6% |
| is_totm_window_first_day | 10.1% |
| is_week_open | 12.6% |
| kc_touch_lower | 81.1% |
| large_dollar_buy | 0.4% |
| macd_12_26_9_crossover_dn | 22.7% |
| macd_8_21_5_crossover_dn | 18.9% |
| marubozu_bear | 1.7% |
| mfi_broad_overbought | 2.5% |
| mfi_broad_oversold | 23.5% |
| mfi_overbought | 0.4% |
| mfi_oversold | 9.2% |
| monthly_above_sma_12 | 46.8% |
| monthly_above_sma_6 | 29.9% |
| monthly_bias_bear | 49.8% |
| monthly_bias_bull | 26.4% |
| monthly_momentum_pos | 47.2% |
| near_52w_high_95pct | 1.3% |
| near_52w_low | 9.2% |
| near_52w_low_105pct | 16.4% |
| near_avwap_20high_atr_05x | 3.8% |
| near_avwap_20high_atr_10x | 7.6% |
| near_avwap_20high_atr_15x | 18.1% |
| near_avwap_20high_atr_20x | 42.0% |
| near_avwap_20low_atr_05x | 57.8% |
| near_avwap_20low_atr_10x | 71.1% |
| near_avwap_20low_atr_15x | 85.6% |
| near_avwap_20low_atr_20x | 92.2% |
| near_avwap_252low_atr_05x | 25.5% |
| near_avwap_252low_atr_10x | 32.9% |
| near_avwap_252low_atr_15x | 44.0% |
| near_avwap_252low_atr_20x | 54.6% |
| near_avwap_50low_atr_05x | 40.0% |
| near_avwap_50low_atr_10x | 57.3% |
| near_avwap_50low_atr_15x | 72.7% |
| near_avwap_50low_atr_20x | 88.0% |
| near_cam_r3 | 1.7% |
| near_cam_s3 | 9.7% |
| near_cam_s4 | 2.1% |
| near_fib_382 | 3.4% |
| near_fib_500 | 5.5% |
| near_fib_618 | 5.5% |
| near_fib_786 | 3.8% |
| near_pivot | 5.9% |
| near_prev_close | 7.1% |
| near_prev_high | 1.3% |
| near_prev_low | 6.7% |
| near_r1 | 1.3% |
| near_r1_wide | 8.8% |
| near_r2_wide | 1.3% |
| near_s1 | 7.1% |
| near_s1_wide | 27.7% |
| near_s2 | 0.8% |
| near_s2_wide | 8.0% |
| near_s3 | 1.3% |
| near_wood_r1 | 1.7% |
| near_wood_s1 | 4.2% |
| news_uses_polygon_score | 37.0% |
| obv_bearish | 82.8% |
| obv_bullish | 17.2% |
| obv_diverge_bull | 6.7% |
| obv_falling | 92.9% |
| obv_rising | 7.1% |
| outside_bar | 1.3% |
| pead_negative_surprise | 17.1% |
| pead_positive_surprise | 22.8% |
| pin_bar | 6.3% |
| po3_accumulation_active | 25.6% |
| po3_bearish | 10.1% |
| po3_manipulation_sweep_down | 25.6% |
| po3_sweep_above_prior_high | 16.0% |
| po3_sweep_below_prior_low | 74.4% |
| ppo_crossover_dn | 21.4% |
| pre_fomc_d0 | 5.0% |
| pre_fomc_d1 | 5.9% |
| pre_fomc_window | 10.9% |
| price_above_ema_200 | 39.1% |
| price_above_ema_200_break_recent_5d | 1.3% |
| price_above_ema_50 | 8.4% |
| price_above_ema_50_break_recent_5d | 1.7% |
| price_above_ema_9 | 0.4% |
| price_above_ema_9_break_recent_5d | 0.4% |
| price_above_hull | 0.4% |
| price_above_sma_200 | 43.7% |
| price_above_sma_50 | 13.9% |
| price_above_tema | 0.4% |
| price_below_hull | 99.6% |
| price_below_tema | 99.6% |
| psar_bullish | 0.4% |
| psar_flip_dn | 23.9% |
| psar_flip_up | 0.4% |
| r1_break_retest_long | 0.4% |
| recent_capitulation_at_s3 | 0.8% |
| risk_off_regime_bond_signal | 30.7% |
| risk_off_regime_bond_signal_strong | 25.6% |
| risk_off_regime_gold_signal | 47.9% |
| risk_on_regime_bond_signal | 40.8% |
| risk_on_regime_bond_signal_strong | 21.4% |
| roc_positive | 0.8% |
| roc_turning_dn | 27.3% |
| rsi_14_bullish | 0.4% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 1.7% |
| rsi_14_cross_dn_overbought_recent_3d | 10.9% |
| rsi_14_cross_up_extreme_os_recent_3d | 1.7% |
| rsi_14_cross_up_oversold_recent_3d | 2.9% |
| rsi_14_extreme_os | 11.3% |
| rsi_14_oversold | 43.7% |
| rsi_14_rising | 16.4% |
| rsi_21_bullish | 5.9% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.4% |
| rsi_21_cross_dn_overbought_recent_3d | 5.5% |
| rsi_21_cross_up_extreme_os_recent_3d | 1.3% |
| rsi_21_cross_up_oversold_recent_3d | 1.7% |
| rsi_21_extreme_os | 4.2% |
| rsi_21_oversold | 20.2% |
| rsi_21_rising | 16.4% |
| rsi_2_bullish | 1.3% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 34.5% |
| rsi_2_cross_dn_overbought_recent_3d | 45.8% |
| rsi_2_cross_up_extreme_os_recent_3d | 10.1% |
| rsi_2_cross_up_oversold_recent_3d | 5.5% |
| rsi_2_extreme_os | 89.9% |
| rsi_2_overbought | 0.4% |
| rsi_2_oversold | 94.5% |
| rsi_2_rising | 16.4% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 3.4% |
| rsi_9_cross_dn_overbought_recent_3d | 20.6% |
| rsi_9_cross_up_extreme_os_recent_3d | 4.6% |
| rsi_9_cross_up_oversold_recent_3d | 4.2% |
| rsi_9_extreme_os | 32.4% |
| rsi_9_oversold | 71.8% |
| rsi_9_rising | 16.4% |
| s1_break_retest_short | 78.2% |
| sc_13d_filed_within_30d | 4.3% |
| sc_13g_filed_within_30d | 4.2% |
| sector_outperforming_spy | 50.0% |
| sector_underperforming_spy | 50.0% |
| shooting_star | 3.4% |
| sma_20_50_bullish | 65.1% |
| sma_50_200_bullish | 73.1% |
| sma_9_21_bullish | 40.8% |
| sma_9_21_golden_cross | 0.4% |
| smc_bos_bearish | 8.8% |
| smc_bos_bullish | 18.1% |
| smc_bos_retest_long | 7.1% |
| smc_bos_retest_short | 2.1% |
| smc_breaker_block_bearish | 24.4% |
| smc_breaker_block_bullish | 31.9% |
| smc_choch_bearish | 7.1% |
| smc_choch_bullish | 3.8% |
| smc_equal_highs_swept | 5.0% |
| smc_equal_lows_swept | 3.8% |
| smc_fvg_bearish_active | 74.4% |
| smc_fvg_bullish_active | 15.5% |
| smc_fvg_retest_long_zone | 12.2% |
| smc_fvg_retest_short_zone | 15.1% |
| smc_in_discount_zone | 94.1% |
| smc_in_premium_zone | 25.6% |
| smc_inverse_fvg_bullish | 53.8% |
| smc_liquidity_swept_dn | 2.1% |
| smc_liquidity_swept_up | 0.4% |
| smc_mitigation_block_long | 7.1% |
| smc_ob_bearish_active | 33.2% |
| smc_ob_bullish_active | 40.3% |
| smc_ote_long_zone | 5.9% |
| smc_ote_short_zone | 7.6% |
| squeeze_fire_dn | 23.1% |
| squeeze_fire_up | 0.8% |
| squeeze_in | 5.0% |
| squeeze_positive | 0.8% |
| stoch_bearish_cross | 14.7% |
| stoch_broad_oversold | 54.6% |
| stoch_bullish_cross | 4.6% |
| stoch_oversold | 45.4% |
| stochrsi_cross_dn | 6.3% |
| stochrsi_cross_up | 14.3% |
| stochrsi_oversold | 88.7% |
| supertrend_flip_dn | 42.9% |
| support_break_retest | 37.0% |
| tema_above_dema | 13.4% |
| tema_cross_dn | 13.0% |
| three_black_crows | 18.9% |
| triangle_apex_break_retest_long | 2.5% |
| triangle_ascending_detected | 6.3% |
| triangle_descending_detected | 4.2% |
| uo_oversold | 21.8% |
| usd_strengthening | 17.2% |
| usd_weakening | 2.1% |
| vix_band_high | 49.6% |
| vix_band_low | 26.9% |
| vix_band_mid | 23.5% |
| vix_term_backwardation | 21.8% |
| vix_term_contango | 78.2% |
| vol_above_avg | 91.2% |
| vol_below_avg | 8.8% |
| vol_spike_12x | 80.3% |
| vol_spike_15x | 65.1% |
| vol_spike_17x | 56.7% |
| vol_spike_2x | 46.2% |
| vol_spike_2x_on_down_day_recent_3d | 43.3% |
| vol_spike_2x_on_up_day_recent_3d | 6.3% |
| vol_spike_3x | 26.9% |
| vp_above_value_area | 2.5% |
| vp_below_value_area | 54.2% |
| vp_close_above_poc | 22.3% |
| vp_close_below_poc | 77.7% |
| vp_in_value_area | 43.3% |
| week_open_gap_down_15pct | 5.0% |
| week_open_gap_up_15pct | 0.4% |
| weekly_above_ema_10 | 8.0% |
| weekly_above_ema_20 | 24.8% |
| weekly_bias_bear | 75.2% |
| weekly_bias_bull | 8.0% |
| weekly_momentum_pos | 8.8% |
| williams_r_oversold | 87.4% |
| williams_r_rising | 30.3% |
| within_pead_window | 39.2% |
| within_post_deletion_window | 18.8% |
| within_post_inclusion_window | 2.9% |
| xs_avoid_high_ivol | 61.2% |
| xs_avoid_high_max | 83.6% |
| xs_high_beta_decile | 23.5% |
| xs_low_beta_bottom_quintile | 23.5% |
| xs_low_beta_decile | 17.9% |
| xs_low_beta_decile_entry_recent_5d | 1.3% |
| xs_low_beta_top_quintile | 17.9% |
| xs_momentum_bottom_decile | 6.8% |
| xs_momentum_bottom_quintile | 15.7% |
| xs_momentum_top_decile | 19.1% |
| xs_momentum_top_quintile | 31.1% |
| xs_quality_bottom_quintile | 23.5% |
| xs_quality_top_quintile | 21.3% |
| xs_quality_top_tercile | 42.6% |
| year_low_break_retest_short | 6.3% |
| yoy_surprise_high | 58.0% |
| yoy_surprise_negative | 30.4% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 92.0% |
| committed_growth_holders | 92.0% |
| corp_donations_1y | 7.1% |
| corp_donations_count_1y | 7.1% |
| corp_donations_unique_pacs | 7.1% |
| cot_rut_commercials_pctile_3y | 65.5% |
| cot_rut_mmoney_pctile_3y | 65.5% |
| cup_handle_depth_pct | 21.0% |
| days_since_deletion | 6.7% |
| days_since_inclusion | 14.3% |
| days_since_last_earnings | 97.5% |
| days_to_next_holiday | 69.3% |
| days_to_rebalance | 10.9% |
| dpi_30d_avg | 95.8% |
| dpi_recent | 95.8% |
| earnings_announcement_return | 81.1% |
| earnings_eps_yoy_growth | 94.1% |
| gov_contracts_4q_sum | 38.2% |
| gov_contracts_last_qtr_amount | 38.2% |
| gov_contracts_qoq_growth | 38.2% |
| head_shoulders_bottom_neckline | 3.8% |
| head_shoulders_magnitude_pct | 5.5% |
| house_buy_count_90d | 97.5% |
| house_net_buy_90d | 97.5% |
| house_sell_count_90d | 97.5% |
| insider_director_buyers_30d | 4.6% |
| insider_officer_buyers_30d | 4.6% |
| insider_total_shares_bought_30d | 4.6% |
| insider_unique_buyers_30d | 4.6% |
| inverted_cup_handle_height_pct | 13.9% |
| lobbying_amount_1y | 73.9% |
| lobbying_amount_q | 73.9% |
| lobbying_amount_yoy | 73.9% |
| monthly_momentum_6m | 97.1% |
| otc_short_ratio_recent | 95.8% |
| otc_volume_recent | 95.8% |
| pair_half_life | 93.3% |
| pair_max_abs_zscore | 93.3% |
| pair_zscore_signed | 93.3% |
| pct_from_avwap_20low | 37.8% |
| pct_from_avwap_252low | 90.8% |
| pct_from_avwap_50low | 63.0% |
| persistent_holders_4q | 92.0% |
| persistent_holders_8q | 92.0% |
| sc_13g_latest_percent_owned | 2.5% |
| search_volume_index_recent | 81.1% |
| search_volume_observations | 81.1% |
| search_volume_zscore_30d | 81.1% |
| sector_etf_return_20d | 2.5% |
| short_interest_pct | 96.6% |
| spy_return_20d | 2.5% |
| total_active_holders | 92.0% |
| triangle_breakdown_pct | 4.2% |
| triangle_breakout_pct | 6.3% |
| xs_ivol | 97.5% |
| xs_ivol_decile | 97.5% |
| xs_max_anomaly | 97.5% |
| xs_max_anomaly_decile | 97.5% |
| xs_quality_decile | 57.1% |
| xs_quality_gross_profitability | 57.1% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.987), `avwap_20low` (0.977), `avwap_252low` (0.979), `avwap_50low` (0.977), `bb_10_20_lower` (0.977), `bb_10_20_mid` (0.998), `bb_10_20_upper` (0.993), `bb_20_15_lower` (0.99), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.995), `bb_20_20_lower` (0.985), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.993), `cam_r1` (0.98), `cam_r2` (0.981), `cam_r3` (0.982), `cam_r4` (0.983), `cam_s1` (0.978), `cam_s2` (0.977), `cam_s3` (0.976), `cam_s4` (0.973), `chandelier_long_value` (0.999), `chandelier_short_value` (0.983), `cpr_bottom` (0.98), `cpr_top` (0.98), `cup_handle_breakout_level` (0.997), `cup_handle_rim` (0.996), `dc10_lower` (0.972), `dc10_mid` (0.994), `dc10_upper` (0.999), `dc20_lower` (0.972), `dc20_mid` (0.996), `dc20_upper` (0.998), `dema` (0.994), `double_bottom_neckline` (0.998), `double_bottom_trough` (0.999), `double_top_neckline` (0.994), `double_top_peak` (0.995), `entry_stop_long` (0.969), `entry_stop_short` (0.985), `fib_236` (0.998), `fib_382` (0.999), `fib_500` (0.997), `fib_618` (0.994), `fib_786` (0.986), `fib_ext_127` (0.991), `fib_ext_162` (0.986), `head_shoulders_top_neckline` (1.0), `hull_ma` (0.992), `ichi_kijun` (0.997), `ichi_senkou_a` (0.993), `ichi_senkou_b` (0.992), `ichi_tenkan` (0.994), `inverted_cup_handle_breakdown_level` (0.997), `inverted_cup_handle_rim_low` (0.996), `kc_lower` (0.998), `kc_mid` (0.999), `kc_upper` (1.0), `monthly_close` (0.982), `monthly_sma_12` (0.984), `monthly_sma_6` (0.996), `pivot` (0.98), `prev_close` (0.979), `prev_high` (0.984), `prev_low` (0.975), `psar_value` (0.998), `r1` (0.983), `r2` (0.985), `r3` (0.986), `s1` (0.974), `s2` (0.97), `s3` (0.967), `supertrend_value` (0.991), `swing_high` (0.996), `swing_low` (0.972), `tema` (0.988), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.983), `vp_value_area_high` (0.992), `vp_value_area_low` (0.979), `weekly_close` (0.977), `weekly_ema_10` (0.999), `weekly_ema_20` (0.997), `wood_p` (0.98), `wood_r1` (0.982), `wood_r2` (0.984), `wood_s1` (0.977), `wood_s2` (0.971), `year_high` (0.978)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | span triple (fast, slow, signal) | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1 | (period, multiplier) + flip lookback | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P3 | adx > 20 | 5 | subset-safe | no - derives offline |
| P4 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     1 x 1 x 5 x 1 = 5
offline gradings   5 level-combinations x 24 exits = 120
ENGINE RUNS        1 (every fire-adding axis sits at production-only until its env actuator exists)
check              1 x 5 = 5
```

B-row candidates NOT in this factorial: 535 census axes join it only when REGISTERED at the T3 band review.
