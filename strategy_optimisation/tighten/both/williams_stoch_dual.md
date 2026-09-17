# Table A - williams_stoch_dual

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit e29a15af2 at 2026-09-17 17:07:43 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** confluence | **status:** NOT-STARTED | **R5 fires:** 750 | **surviving fires (T1):** 750 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  near_cam_r3  <- backtest/signals/screener.py +1
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P1.1-P1.1 (band rows in Table A)
P2  near_cam_s3  <- backtest/signals/screener.py +1
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P2.1-P2.1 (band rows in Table A)
P3  near_r1  <- backtest/signals/screener.py +1
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P3.1-P3.1 (band rows in Table A)
P4  near_r2  <- backtest/signals/screener.py +1
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P4.1-P4.1 (band rows in Table A)
P5  near_s1  <- backtest/signals/screener.py +2
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P5.1-P5.1 (band rows in Table A)
P6  near_s2  <- backtest/signals/screener.py +1
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P6.1-P6.1 (band rows in Table A)
P7  near_s3  <- backtest/signals/screener.py +1
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P7.1-P7.1 (band rows in Table A)
P8  near_wood_r1  <- backtest/signals/screener.py +1
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P8.1-P8.1 (band rows in Table A)
P9  near_wood_s1  <- backtest/signals/screener.py +1
       DEFN: price within 0.3pct of the named pivot level (near(); technical.py:76)
       knobs P9.1-P9.1 (band rows in Table A)
P10  stoch_bearish_cross  <- backtest/signals/screener.py +1
       DEFN: stochastic (14,3,3) k/d cross with prior-bar confirmation (technical.py:604-630)
       knobs P10.1-P10.1 (band rows in Table A)
P11  stoch_bullish_cross  <- backtest/signals/screener.py +1
       DEFN: stochastic (14,3,3) k/d cross with prior-bar confirmation (technical.py:604-630)
       knobs P11.1-P11.2 (band rows in Table A)
P12  williams_r_oversold  <- backtest/signals/screener.py +3
       DEFN: Williams %R(14) < -80 (technical.py:702)
       knobs P12.1-P12.2 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P13  williams_r > -20   [EXISTING-THRESHOLD]
P14  _short_borrow_trap_active(s)   [helper gate]

Gate body, VERBATIM from backtest/signals/screener.py strat_williams_stoch_dual (docstring and return dropped):

```python
fl = s.get('williams_r_oversold') and s.get('stoch_bullish_cross') and (s.get('near_s1') or s.get('near_s2') or s.get('near_s3') or s.get('near_cam_s3') or s.get('near_wood_s1'))
fs = (s.get('williams_r', 0) > -20 and s.get('stoch_bearish_cross') and (s.get('near_r1') or s.get('near_r2') or s.get('near_cam_r3') or s.get('near_wood_r1'))) and (not _short_borrow_trap_active(s))
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
| P1 | PRODUCER | near_cam_r3 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | proximity tolerance to Camarilla R3 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P2 | PRODUCER | near_cam_s3 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | proximity tolerance to Camarilla S3 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P3 | PRODUCER | near_r1 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P3.x) | BANDS-DEFINED |
| P3.1 | BAND | proximity tolerance to R1 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P4 | PRODUCER | near_r2 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P4.x) | BANDS-DEFINED |
| P4.1 | BAND | proximity tolerance to R2 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P5 | PRODUCER | near_s1 - emitted by backtest/signals/screener.py +2; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P5.x) | BANDS-DEFINED |
| P5.1 | BAND | proximity tolerance to S1 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P6 | PRODUCER | near_s2 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P6.x) | BANDS-DEFINED |
| P6.1 | BAND | proximity tolerance to S2 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P7 | PRODUCER | near_s3 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P7.x) | BANDS-DEFINED |
| P7.1 | BAND | proximity tolerance to S3 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P8 | PRODUCER | near_wood_r1 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P8.x) | BANDS-DEFINED |
| P8.1 | BAND | proximity tolerance to Woodie R1 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P9 | PRODUCER | near_wood_s1 - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | price within 0.3pct of the named pivot level (near(); technical.py:76) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P9.x) | BANDS-DEFINED |
| P9.1 | BAND | proximity tolerance to Woodie S1 (abs dist/level) - backtest/signals/technical.py:76 (near), :81 (near_wide) | BRACKET production 0.003; 0.015 is the shipped near_*_wide | 0.003 | [0.002, 0.003, 0.005, 0.015 (the _wide variant)] | none - the level is persisted but today's price is not a signal key | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P10 | PRODUCER | stoch_bearish_cross - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | stochastic (14,3,3) k/d cross with prior-bar confirmation (technical.py:604-630) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P10.x) | BANDS-DEFINED |
| P10.1 | BAND | mirror of stoch_bullish_cross - backtest/signals/technical.py:604-630 | mirror | (14,3,3) | as bullish, mirrored (guard k above [70, 80]) | guard-band side on persisted k/d | freshness; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P11 | PRODUCER | stoch_bullish_cross - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | stochastic (14,3,3) k/d cross with prior-bar confirmation (technical.py:604-630) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P11.x) | BANDS-DEFINED |
| P11.1 | BAND | stochastic (k, smooth, d) - backtest/signals/technical.py:604-624 | BRACKET canon | (14, 3, 3) | [(14,3,3), (5,3,3), (21,5,5)] | none - other spans unpersisted | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P11.2 | BAND | cross freshness (k over d today) - technical.py:629 | BRACKET the oversold zone | structural | add guard band: k below [20, 30] at cross | guard-band side on persisted stoch_k/stoch_d | the freshness itself (prior k/d unpersisted); DEFINED-NO-ACTUATOR | T3 review before any grid |
| P12 | PRODUCER | williams_r_oversold - emitted by backtest/signals/screener.py +3; the boolean's UNDERLYING condition is bandable through its producer's internals | Williams %R(14) < -80 (technical.py:702) | leg required True | - (knobs below) | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P12.x) | BANDS-DEFINED |
| P12.1 | BAND | period - backtest/signals/technical.py:692 | BRACKET production | 14 | 10, 14, 20 | none | the whole band; DEFINED-NO-ACTUATOR | T3 review before any grid |
| P12.2 | BAND | oversold threshold - technical.py:702 | BRACKET canon -80; williams_r IS persisted | -80 | -90, -85, -80 | TIGHTER (< -85, < -90) - subset on persisted williams_r | LOOSER (> -80); DEFINED-NO-ACTUATOR | T3 review before any grid |
| P13 | STRATEGY | williams_r `> -20` [EXISTING-THRESHOLD] | gate threshold on the persisted magnitude | `> -20` | production + 3 tighter measured levels | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P14 | STRATEGY-HELPER | _short_borrow_trap_active(s) - underlying condition: days_to_cover > 5.0 (blocks the fire) | blocks SHORT fires when days_to_cover > 5.0 (B718a) | cap 5.0 (B718a owner-ruled risk guard) | tighter = LOWER cap on persisted days_to_cover - OFFLINE subset | raising the cap admits engine-blocked fires - RESIM; shared helper (6 consumers) so any band is a per-strategy override on the owner's word | BANDABLE-OWNER-GATED |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | AND-leg companions on persisted keys | - | census levels below | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| williams_r | backtest/signals/screener.py +1 | `> -20` | 100.0% | TIGHTER = RAISE the floor: -19.12 -> 451 (60%); -13.472 -> 300 (40%); -9.556 -> 150 (20%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|
| adx | backtest/signals/screener.py +1 | 100.0% | 18.572, 23.16, 27.814, 34.804 | 18.572: 600 (80%); 23.16: 450 (60%); 27.814: 300 (40%); 34.804: 150 (20%) | 18.572: 150 (20%); 23.16: 300 (40%); 27.814: 450 (60%); 34.804: 600 (80%) | OFFLINE |
| adx_di_minus | backtest/signals/technical.py | 100.0% | 11.416, 14.93, 21.26, 32.698 | 11.416: 600 (80%); 14.93: 452 (60%); 21.26: 300 (40%); 32.698: 150 (20%) | 11.416: 150 (20%); 14.93: 301 (40%); 21.26: 450 (60%); 32.698: 600 (80%) | OFFLINE |
| adx_di_plus | backtest/signals/technical.py | 100.0% | 15.11, 24.068, 31.004, 36.04 | 15.11: 601 (80%); 24.068: 450 (60%); 31.004: 300 (40%); 36.04: 151 (20%) | 15.11: 151 (20%); 24.068: 300 (40%); 31.004: 450 (60%); 36.04: 601 (80%) | OFFLINE |
| ao | backtest/signals/screener.py +1 | 100.0% | -3.4754, 0.8035, 4.0835, 10.3869 | -3.4754: 600 (80%); 0.8035: 450 (60%); 4.0835: 300 (40%); 10.3869: 150 (20%) | -3.4754: 150 (20%); 0.8035: 300 (40%); 4.0835: 450 (60%); 10.3869: 600 (80%) | OFFLINE |
| atr | backtest/signals/screener.py +4 | 100.0% | 1.1794, 1.9888, 3.3362, 5.6409 | 1.1794: 600 (80%); 1.9888: 450 (60%); 3.3362: 300 (40%); 5.6409: 150 (20%) | 1.1794: 150 (20%); 1.9888: 300 (40%); 3.3362: 450 (60%); 5.6409: 600 (80%) | OFFLINE |
| atr_14 | backtest/signals/technical.py +1 | 100.0% | 1.1794, 1.9888, 3.3362, 5.6409 | 1.1794: 600 (80%); 1.9888: 450 (60%); 3.3362: 300 (40%); 5.6409: 150 (20%) | 1.1794: 150 (20%); 1.9888: 300 (40%); 3.3362: 450 (60%); 5.6409: 600 (80%) | OFFLINE |
| atr_pct | backtest/signals/technical.py | 100.0% | 1.8458, 2.1926, 2.6186, 3.2276 | 1.8458: 600 (80%); 2.1926: 450 (60%); 2.6186: 300 (40%); 3.2276: 150 (20%) | 1.8458: 150 (20%); 2.1926: 300 (40%); 2.6186: 450 (60%); 3.2276: 600 (80%) | OFFLINE |
| bb_10_20_bandwidth | (not found by literal grep) | 100.0% | 0.0686, 0.0962, 0.1248, 0.1695 | 0.0686: 600 (80%); 0.0962: 450 (60%); 0.1248: 300 (40%); 0.1695: 151 (20%) | 0.0686: 151 (20%); 0.0962: 301 (40%); 0.1248: 450 (60%); 0.1695: 600 (80%) | OFFLINE |
| bb_10_20_pctb | (not found by literal grep) | 100.0% | 0.1916, 0.6314, 0.7806, 0.827 | 0.1916: 600 (80%); 0.6314: 450 (60%); 0.7806: 300 (40%); 0.827: 152 (20%) | 0.1916: 150 (20%); 0.6314: 300 (40%); 0.7806: 450 (60%); 0.827: 600 (80%) | OFFLINE |
| bb_20_15_bandwidth | (not found by literal grep) | 100.0% | 0.0751, 0.0993, 0.124, 0.1633 | 0.0751: 601 (80%); 0.0993: 452 (60%); 0.124: 301 (40%); 0.1633: 150 (20%) | 0.0751: 151 (20%); 0.0993: 301 (40%); 0.124: 451 (60%); 0.1633: 600 (80%) | OFFLINE |
| bb_20_15_pctb | (not found by literal grep) | 100.0% | -0.0396, 0.8176, 0.999, 1.0842 | -0.0396: 600 (80%); 0.8176: 450 (60%); 0.999: 300 (40%); 1.0842: 150 (20%) | -0.0396: 150 (20%); 0.8176: 300 (40%); 0.999: 450 (60%); 1.0842: 600 (80%) | OFFLINE |
| bb_20_20_bandwidth | (not found by literal grep) | 100.0% | 0.1002, 0.1325, 0.1653, 0.2177 | 0.1002: 600 (80%); 0.1325: 450 (60%); 0.1653: 301 (40%); 0.2177: 150 (20%) | 0.1002: 152 (20%); 0.1325: 301 (40%); 0.1653: 451 (60%); 0.2177: 600 (80%) | OFFLINE |
| bb_20_20_pctb | (not found by literal grep) | 100.0% | 0.0953, 0.7382, 0.8742, 0.9382 | 0.0953: 600 (80%); 0.7382: 450 (60%); 0.8742: 300 (40%); 0.9382: 150 (20%) | 0.0953: 150 (20%); 0.7382: 300 (40%); 0.8742: 450 (60%); 0.9382: 600 (80%) | OFFLINE |
| bond_equity_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0504, -0.0379, -0.0142, 0.0092 | -0.0504: 604 (81%); -0.0379: 453 (60%); -0.0142: 304 (41%); 0.0092: 150 (20%) | -0.0504: 153 (20%); -0.0379: 303 (40%); -0.0142: 451 (60%); 0.0092: 600 (80%) | OFFLINE |
| bond_equity_ratio | backtest/signals/cross_asset.py | 100.0% | 0.1393, 0.1725, 0.2072, 0.2621 | 0.1393: 598 (80%); 0.1725: 449 (60%); 0.2072: 301 (40%); 0.2621: 152 (20%) | 0.1393: 152 (20%); 0.1725: 301 (40%); 0.2072: 449 (60%); 0.2621: 598 (80%) | OFFLINE |
| buy_count | backtest/data/smart_money.py | 100.0% | 0 | 0: 750 (100%) | 0: 729 (97%) | OFFLINE |
| cmf | backtest/signals/technical.py | 100.0% | -0.1057, 0.013, 0.1202, 0.211 | -0.1057: 600 (80%); 0.013: 450 (60%); 0.1202: 300 (40%); 0.211: 150 (20%) | -0.1057: 150 (20%); 0.013: 300 (40%); 0.1202: 450 (60%); 0.211: 600 (80%) | OFFLINE |
| cnn_fg_days_since_publish | backtest/engine/backtest.py | 100.0% | 0, 1 | 0: 750 (100%); 1: 326 (43%) | 0: 424 (57%); 1: 606 (81%) | OFFLINE |
| cot_copper_commercials_net_pct | (not found by literal grep) | 100.0% | -0.2365, -0.2064, -0.1546, -0.1096 | -0.2365: 603 (80%); -0.2064: 457 (61%); -0.1546: 303 (40%); -0.1096: 151 (20%) | -0.2365: 159 (21%); -0.2064: 306 (41%); -0.1546: 452 (60%); -0.1096: 603 (80%) | OFFLINE |
| cot_copper_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3782, 0.5897, 0.6859, 0.7756 | 0.3782: 605 (81%); 0.5897: 455 (61%); 0.6859: 305 (41%); 0.7756: 159 (21%) | 0.3782: 153 (20%); 0.5897: 311 (41%); 0.6859: 451 (60%); 0.7756: 602 (80%) | OFFLINE |
| cot_copper_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.2615, 0.3744, 0.6218, 0.8654 | 0.2615: 600 (80%); 0.3744: 450 (60%); 0.6218: 303 (40%); 0.8654: 158 (21%) | 0.2615: 150 (20%); 0.3744: 300 (40%); 0.6218: 451 (60%); 0.8654: 602 (80%) | OFFLINE |
| cot_dow_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1195, -0.0264, 0.0646, 0.1806 | -0.1195: 601 (80%); -0.0264: 451 (60%); 0.0646: 319 (43%); 0.1806: 152 (20%) | -0.1195: 153 (20%); -0.0264: 305 (41%); 0.0646: 468 (62%); 0.1806: 603 (80%) | OFFLINE |
| cot_dow_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.2436, 0.3974, 0.5897, 0.7308 | 0.2436: 601 (80%); 0.3974: 453 (60%); 0.5897: 320 (43%); 0.7308: 153 (20%) | 0.2436: 156 (21%); 0.3974: 302 (40%); 0.5897: 475 (63%); 0.7308: 606 (81%) | OFFLINE |
| cot_dow_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.109, 0.2821, 0.4898, 0.6936 | 0.109: 602 (80%); 0.2821: 452 (60%); 0.4898: 300 (40%); 0.6936: 150 (20%) | 0.109: 151 (20%); 0.2821: 314 (42%); 0.4898: 450 (60%); 0.6936: 600 (80%) | OFFLINE |
| cot_dxy_commercials_net_pct | (not found by literal grep) | 100.0% | -0.5301, -0.3462, -0.169, 0.0939 | -0.5301: 600 (80%); -0.3462: 450 (60%); -0.169: 304 (41%); 0.0939: 151 (20%) | -0.5301: 150 (20%); -0.3462: 300 (40%); -0.169: 452 (60%); 0.0939: 601 (80%) | OFFLINE |
| cot_dxy_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3013, 0.5321, 0.759, 0.9551 | 0.3013: 610 (81%); 0.5321: 453 (60%); 0.759: 300 (40%); 0.9551: 157 (21%) | 0.3013: 155 (21%); 0.5321: 316 (42%); 0.759: 450 (60%); 0.9551: 618 (82%) | OFFLINE |
| cot_dxy_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1154, 0.3782, 0.5577, 0.7244 | 0.1154: 604 (81%); 0.3782: 455 (61%); 0.5577: 306 (41%); 0.7244: 156 (21%) | 0.1154: 152 (20%); 0.3782: 308 (41%); 0.5577: 453 (60%); 0.7244: 601 (80%) | OFFLINE |
| cot_gold_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0665, -0.0598, -0.0442, 0 | -0.0665: 602 (80%); -0.0598: 450 (60%); -0.0442: 301 (40%); 0: 201 (27%) | -0.0665: 157 (21%); -0.0598: 300 (40%); -0.0442: 457 (61%); 0: 739 (99%) | OFFLINE |
| cot_gold_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3526, 0.6859, 0.8782, 1 | 0.3526: 607 (81%); 0.6859: 453 (60%); 0.8782: 303 (40%); 1: 160 (21%) | 0.3526: 155 (21%); 0.6859: 301 (40%); 0.8782: 460 (61%); 1: 750 (100%) | OFFLINE |
| cot_gold_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1154, 0.2179, 0.5577, 0.8974 | 0.1154: 609 (81%); 0.2179: 462 (62%); 0.5577: 302 (40%); 0.8974: 151 (20%) | 0.1154: 154 (21%); 0.2179: 302 (40%); 0.5577: 457 (61%); 0.8974: 607 (81%) | OFFLINE |
| cot_ndx_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0191, 0.0324, 0.0697, 0.147 | -0.0191: 600 (80%); 0.0324: 454 (61%); 0.0697: 301 (40%); 0.147: 151 (20%) | -0.0191: 151 (20%); 0.0324: 302 (40%); 0.0697: 455 (61%); 0.147: 601 (80%) | OFFLINE |
| cot_ndx_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.4186, 0.7692, 0.8951, 0.9679 | 0.4186: 600 (80%); 0.7692: 451 (60%); 0.8951: 300 (40%); 0.9679: 152 (20%) | 0.4186: 150 (20%); 0.7692: 305 (41%); 0.8951: 450 (60%); 0.9679: 607 (81%) | OFFLINE |
| cot_ndx_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.0962, 0.3684, 0.618, 0.8333 | 0.0962: 608 (81%); 0.3684: 456 (61%); 0.618: 300 (40%); 0.8333: 151 (20%) | 0.0962: 151 (20%); 0.3684: 303 (40%); 0.618: 450 (60%); 0.8333: 618 (82%) | OFFLINE |
| cot_rut_commercials_net_pct | (not found by literal grep) | 100.0% | -0.0812, -0.0189, 0.1048, 0.3175 | -0.0812: 679 (91%); -0.0189: 454 (61%); 0.1048: 305 (41%); 0.3175: 155 (21%) | -0.0812: 156 (21%); -0.0189: 302 (40%); 0.1048: 451 (60%); 0.3175: 695 (93%) | OFFLINE |
| cot_sp500_commercials_net_pct | (not found by literal grep) | 100.0% | -0.1886, -0.0532, 0.0256, 0.0682 | -0.1886: 601 (80%); -0.0532: 457 (61%); 0.0256: 304 (41%); 0.0682: 158 (21%) | -0.1886: 152 (20%); -0.0532: 302 (40%); 0.0256: 451 (60%); 0.0682: 605 (81%) | OFFLINE |
| cot_sp500_commercials_pctile_3y | (not found by literal grep) | 100.0% | 0.3192, 0.5256, 0.6731, 0.8333 | 0.3192: 600 (80%); 0.5256: 464 (62%); 0.6731: 302 (40%); 0.8333: 152 (20%) | 0.3192: 150 (20%); 0.5256: 334 (45%); 0.6731: 452 (60%); 0.8333: 611 (81%) | OFFLINE |
| cot_sp500_mmoney_pctile_3y | (not found by literal grep) | 100.0% | 0.1218, 0.3782, 0.6308, 0.8269 | 0.1218: 633 (84%); 0.3782: 458 (61%); 0.6308: 300 (40%); 0.8269: 168 (22%) | 0.1218: 159 (21%); 0.3782: 303 (40%); 0.6308: 450 (60%); 0.8269: 604 (81%) | OFFLINE |
| cpr_width | backtest/signals/technical.py | 100.0% | 0.0651, 0.1392, 0.2565, 0.5412 | 0.0651: 600 (80%); 0.1392: 451 (60%); 0.2565: 300 (40%); 0.5412: 150 (20%) | 0.0651: 151 (20%); 0.1392: 301 (40%); 0.2565: 450 (60%); 0.5412: 600 (80%) | OFFLINE |
| days_since_last_earnings | backtest/signals/earnings_surprise_yoy.py +2 | 98.5% | 25, 48, 76, 120.4 | 25: 592 (79%); 48: 445 (59%); 76: 297 (40%); 120.4: 148 (20%) | 25: 151 (20%); 48: 302 (40%); 76: 446 (59%); 120.4: 591 (79%) | OFFLINE |
| days_to_cover | backtest/signals/screener.py +1 | 99.6% | 1.8365, 2.3203, 2.8757, 3.8021 | 1.8365: 597 (80%); 2.3203: 448 (60%); 2.8757: 299 (40%); 3.8021: 150 (20%) | 1.8365: 150 (20%); 2.3203: 299 (40%); 2.8757: 448 (60%); 3.8021: 597 (80%) | OFFLINE |
| days_until_fomc | backtest/signals/macro_events.py +1 | 100.0% | 8, 20, 28, 36 | 8: 610 (81%); 20: 462 (62%); 28: 302 (40%); 36: 160 (21%) | 8: 157 (21%); 20: 341 (45%); 28: 464 (62%); 36: 611 (81%) | OFFLINE |
| dow | backtest/signals/calendar_effects.py +2 | 100.0% | 1, 2, 3, 4 | 1: 641 (85%); 2: 497 (66%); 3: 363 (48%); 4: 183 (24%) | 1: 253 (34%); 2: 387 (52%); 3: 567 (76%); 4: 750 (100%) | OFFLINE |
| dxy_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0139, -0.0051, 0.0093, 0.0238 | -0.0139: 602 (80%); -0.0051: 450 (60%); 0.0093: 307 (41%); 0.0238: 151 (20%) | -0.0139: 158 (21%); -0.0051: 301 (40%); 0.0093: 451 (60%); 0.0238: 603 (80%) | OFFLINE |
| dxy_proxy_close | backtest/signals/cross_asset.py | 100.0% | 24.6818, 25.6303, 26.3966, 26.9258 | 24.6818: 601 (80%); 25.6303: 452 (60%); 26.3966: 301 (40%); 26.9258: 150 (20%) | 24.6818: 152 (20%); 25.6303: 308 (41%); 26.3966: 451 (60%); 26.9258: 600 (80%) | OFFLINE |
| gap_dn_pct | backtest/signals/screener.py +1 | 100.0% | -0.7078, -0.2824, 0.0992, 0.79 | -0.7078: 600 (80%); -0.2824: 450 (60%); 0.0992: 300 (40%); 0.79: 150 (20%) | -0.7078: 150 (20%); -0.2824: 300 (40%); 0.0992: 450 (60%); 0.79: 600 (80%) | OFFLINE |
| gap_up_pct | backtest/signals/screener.py +1 | 100.0% | -0.79, -0.0992, 0.2824, 0.7078 | -0.79: 600 (80%); -0.0992: 450 (60%); 0.2824: 300 (40%); 0.7078: 150 (20%) | -0.79: 150 (20%); -0.0992: 300 (40%); 0.2824: 450 (60%); 0.7078: 600 (80%) | OFFLINE |
| gold_silver_20d_pct_change | backtest/signals/cross_asset.py | 100.0% | -0.0459, -0.0159, 0.0132, 0.0491 | -0.0459: 600 (80%); -0.0159: 450 (60%); 0.0132: 300 (40%); 0.0491: 152 (20%) | -0.0459: 150 (20%); -0.0159: 300 (40%); 0.0132: 450 (60%); 0.0491: 600 (80%) | OFFLINE |
| gold_silver_ratio | backtest/signals/cross_asset.py | 100.0% | 8.103, 8.5062, 8.776, 9.043 | 8.103: 601 (80%); 8.5062: 449 (60%); 8.776: 301 (40%); 9.043: 150 (20%) | 8.103: 149 (20%); 8.5062: 301 (40%); 8.776: 449 (60%); 9.043: 600 (80%) | OFFLINE |
| house_buy_count_90d | backtest/signals/congressional_alt_data.py | 98.9% | 0, 1 | 0: 742 (99%); 1: 236 (31%) | 0: 506 (67%); 1: 659 (88%) | OFFLINE |
| house_net_buy_90d | backtest/signals/congressional_alt_data.py | 98.9% | 0 | 0: 606 (81%) | 0: 623 (83%) | OFFLINE |
| house_sell_count_90d | backtest/signals/congressional_alt_data.py | 98.9% | 0, 1 | 0: 742 (99%); 1: 238 (32%) | 0: 504 (67%); 1: 649 (87%) | OFFLINE |
| institutional_increased | backtest/signals/screener.py +1 | 100.0% | 2, 5, 20.2, 240.8 | 2: 636 (85%); 5: 473 (63%); 20.2: 300 (40%); 240.8: 150 (20%) | 2: 170 (23%); 5: 317 (42%); 20.2: 450 (60%); 240.8: 600 (80%) | OFFLINE |
| institutional_new_positions | backtest/signals/screener.py +1 | 100.0% | 1, 3, 68, 129.2 | 1: 608 (81%); 3: 481 (64%); 68: 303 (40%); 129.2: 150 (20%) | 1: 214 (29%); 3: 304 (41%); 68: 451 (60%); 129.2: 600 (80%) | OFFLINE |
| macd_12_26_9_hist | (not found by literal grep) | 100.0% | -0.6033, -0.0043, 0.5147, 1.239 | -0.6033: 600 (80%); -0.0043: 450 (60%); 0.5147: 301 (40%); 1.239: 150 (20%) | -0.6033: 150 (20%); -0.0043: 300 (40%); 0.5147: 451 (60%); 1.239: 600 (80%) | OFFLINE |
| macd_12_26_9_line | (not found by literal grep) | 100.0% | -1.26, 0.268, 1.5846, 4.1981 | -1.26: 600 (80%); 0.268: 450 (60%); 1.5846: 300 (40%); 4.1981: 150 (20%) | -1.26: 150 (20%); 0.268: 300 (40%); 1.5846: 450 (60%); 4.1981: 600 (80%) | OFFLINE |
| macd_12_26_9_signal | (not found by literal grep) | 100.0% | -0.781, 0.0998, 1.0212, 3.0207 | -0.781: 600 (80%); 0.0998: 450 (60%); 1.0212: 300 (40%); 3.0207: 150 (20%) | -0.781: 150 (20%); 0.0998: 300 (40%); 1.0212: 450 (60%); 3.0207: 600 (80%) | OFFLINE |
| macd_8_21_5_hist | (not found by literal grep) | 100.0% | -0.4022, -0.0095, 0.2977, 0.786 | -0.4022: 600 (80%); -0.0095: 450 (60%); 0.2977: 300 (40%); 0.786: 150 (20%) | -0.4022: 150 (20%); -0.0095: 300 (40%); 0.2977: 450 (60%); 0.786: 600 (80%) | OFFLINE |
| macd_8_21_5_line | (not found by literal grep) | 100.0% | -1.7175, 0.3994, 2.0083, 4.9978 | -1.7175: 600 (80%); 0.3994: 450 (60%); 2.0083: 300 (40%); 4.9978: 150 (20%) | -1.7175: 150 (20%); 0.3994: 300 (40%); 2.0083: 450 (60%); 4.9978: 600 (80%) | OFFLINE |
| macd_8_21_5_signal | (not found by literal grep) | 100.0% | -1.2945, 0.2845, 1.6051, 4.1713 | -1.2945: 600 (80%); 0.2845: 450 (60%); 1.6051: 300 (40%); 4.1713: 150 (20%) | -1.2945: 150 (20%); 0.2845: 300 (40%); 1.6051: 450 (60%); 4.1713: 600 (80%) | OFFLINE |
| mfi | backtest/signals/technical.py | 100.0% | 29.32, 53.36, 69.144, 78.536 | 29.32: 601 (80%); 53.36: 451 (60%); 69.144: 300 (40%); 78.536: 150 (20%) | 29.32: 151 (20%); 53.36: 301 (40%); 69.144: 450 (60%); 78.536: 600 (80%) | OFFLINE |
| monthly_momentum_6m | backtest/signals/multi_timeframe.py | 98.3% | -0.1279, -0.0046, 0.0976, 0.213 | -0.1279: 589 (79%); -0.0046: 442 (59%); 0.0976: 295 (39%); 0.213: 148 (20%) | -0.1279: 148 (20%); -0.0046: 295 (39%); 0.0976: 442 (59%); 0.213: 589 (79%) | OFFLINE |
| naked_poc_nearest_distance_pct | backtest/signals/screener.py | 99.2% | 0.0079, 0.0228, 0.0452, 0.0856 | 0.0079: 595 (79%); 0.0228: 445 (59%); 0.0452: 298 (40%); 0.0856: 149 (20%) | 0.0079: 149 (20%); 0.0228: 299 (40%); 0.0452: 446 (59%); 0.0856: 595 (79%) | OFFLINE |
| news_article_count | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 2, 4, 8 | 0: 750 (100%); 2: 467 (62%); 4: 302 (40%); 8: 168 (22%) | 0: 185 (25%); 2: 382 (51%); 4: 486 (65%); 8: 607 (81%) | OFFLINE |
| news_bearish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.1124 | 0: 750 (100%); 0.1124: 150 (20%) | 0: 537 (72%); 0.1124: 600 (80%) | OFFLINE |
| news_bullish_pct | backtest/signals/news_sentiment.py | 100.0% | 0, 0.115, 0.4286, 0.6667 | 0: 750 (100%); 0.115: 450 (60%); 0.4286: 305 (41%); 0.6667: 165 (22%) | 0: 298 (40%); 0.115: 300 (40%); 0.4286: 452 (60%); 0.6667: 615 (82%) | OFFLINE |
| news_count_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 1, 2.4, 6 | 0: 750 (100%); 1: 528 (70%); 2.4: 300 (40%); 6: 160 (21%) | 0: 222 (30%); 1: 354 (47%); 2.4: 450 (60%); 6: 621 (83%) | OFFLINE |
| news_count_7d | backtest/signals/news_sentiment.py | 100.0% | 0, 2, 4, 8 | 0: 750 (100%); 2: 467 (62%); 4: 302 (40%); 8: 168 (22%) | 0: 185 (25%); 2: 382 (51%); 4: 486 (65%); 8: 607 (81%) | OFFLINE |
| news_prior_article_count | backtest/signals/news_sentiment.py | 100.0% | 0, 1, 3, 7 | 0: 750 (100%); 1: 552 (74%); 3: 337 (45%); 7: 165 (22%) | 0: 198 (26%); 1: 326 (43%); 3: 474 (63%); 7: 607 (81%) | OFFLINE |
| news_sentiment_30d | backtest/signals/news_sentiment.py | 100.0% | 0.034, 0.2531, 0.3927, 0.5732 | 0.034: 600 (80%); 0.2531: 450 (60%); 0.3927: 300 (40%); 0.5732: 150 (20%) | 0.034: 150 (20%); 0.2531: 300 (40%); 0.3927: 450 (60%); 0.5732: 600 (80%) | OFFLINE |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.1915, 0.5714 | 0: 692 (92%); 0.1915: 300 (40%); 0.5714: 151 (20%) | 0: 405 (54%); 0.1915: 450 (60%); 0.5714: 603 (80%) | OFFLINE |
| news_sentiment_mean | backtest/signals/news_sentiment.py +1 | 100.0% | 0, 0.3333, 0.612 | 0: 694 (93%); 0.3333: 304 (41%); 0.612: 150 (20%) | 0: 327 (44%); 0.3333: 469 (63%); 0.612: 600 (80%) | OFFLINE |
| news_sentiment_score | backtest/signals/news_sentiment.py | 100.0% | 0, 0.3333, 0.612 | 0: 694 (93%); 0.3333: 304 (41%); 0.612: 150 (20%) | 0: 327 (44%); 0.3333: 469 (63%); 0.612: 600 (80%) | OFFLINE |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | 100.0% | -0.1472, 0, 0.1911 | -0.1472: 600 (80%); 0: 541 (72%); 0.1911: 150 (20%) | -0.1472: 150 (20%); 0: 534 (71%); 0.1911: 600 (80%) | OFFLINE |
| news_volume_zscore_5d | backtest/signals/news_sentiment.py +1 | 100.0% | -0.7373, -0.339, 0.1028, 1.0467 | -0.7373: 600 (80%); -0.339: 450 (60%); 0.1028: 301 (40%); 1.0467: 150 (20%) | -0.7373: 150 (20%); -0.339: 300 (40%); 0.1028: 451 (60%); 1.0467: 600 (80%) | OFFLINE |
| pair_count_active | backtest/signals/pairs_trading.py +1 | 100.0% | 2, 4, 7, 11 | 2: 616 (82%); 4: 467 (62%); 7: 306 (41%); 11: 165 (22%) | 2: 216 (29%); 4: 342 (46%); 7: 485 (65%); 11: 610 (81%) | OFFLINE |
| pct_change_10d | (not found by literal grep) | 100.0% | -0.0753, 0.0131, 0.0542, 0.0889 | -0.0753: 601 (80%); 0.0131: 450 (60%); 0.0542: 300 (40%); 0.0889: 150 (20%) | -0.0753: 149 (20%); 0.0131: 300 (40%); 0.0542: 450 (60%); 0.0889: 600 (80%) | OFFLINE |
| pct_change_20d | (not found by literal grep) | 100.0% | -0.0862, 0.013, 0.0761, 0.1258 | -0.0862: 600 (80%); 0.013: 450 (60%); 0.0761: 300 (40%); 0.1258: 150 (20%) | -0.0862: 150 (20%); 0.013: 300 (40%); 0.0761: 450 (60%); 0.1258: 600 (80%) | OFFLINE |
| pct_change_5d | backtest/signals/screener.py | 100.0% | -0.0523, 0.0045, 0.0314, 0.0547 | -0.0523: 600 (80%); 0.0045: 450 (60%); 0.0314: 300 (40%); 0.0547: 150 (20%) | -0.0523: 150 (20%); 0.0045: 300 (40%); 0.0314: 450 (60%); 0.0547: 600 (80%) | OFFLINE |
| pct_from_vwap | backtest/signals/screener.py +1 | 100.0% | -14.9182, -2.0324, 11.0314, 30.8 | -14.9182: 600 (80%); -2.0324: 450 (60%); 11.0314: 300 (40%); 30.8: 150 (20%) | -14.9182: 150 (20%); -2.0324: 300 (40%); 11.0314: 450 (60%); 30.8: 600 (80%) | OFFLINE |
| po3_accum_range_pct | backtest/signals/ict_producers.py +1 | 100.0% | 0.0429, 0.0583, 0.0754, 0.0999 | 0.0429: 600 (80%); 0.0583: 450 (60%); 0.0754: 301 (40%); 0.0999: 150 (20%) | 0.0429: 152 (20%); 0.0583: 301 (40%); 0.0754: 450 (60%); 0.0999: 600 (80%) | OFFLINE |
| po3_close_position | backtest/signals/multi_timeframe.py | 100.0% | 0.2101, 0.3728, 0.5481, 0.7629 | 0.2101: 600 (80%); 0.3728: 450 (60%); 0.5481: 300 (40%); 0.7629: 150 (20%) | 0.2101: 150 (20%); 0.3728: 300 (40%); 0.5481: 450 (60%); 0.7629: 600 (80%) | OFFLINE |
| ppo | backtest/signals/technical.py | 100.0% | -1.8074, 0.3341, 1.6874, 2.8129 | -1.8074: 600 (80%); 0.3341: 450 (60%); 1.6874: 300 (40%); 2.8129: 150 (20%) | -1.8074: 150 (20%); 0.3341: 301 (40%); 1.6874: 450 (60%); 2.8129: 600 (80%) | OFFLINE |
| ppo_hist | backtest/signals/screener.py +1 | 100.0% | -0.8247, -0.0505, 0.5315, 0.907 | -0.8247: 600 (80%); -0.0505: 450 (60%); 0.5315: 300 (40%); 0.907: 150 (20%) | -0.8247: 150 (20%); -0.0505: 300 (40%); 0.5315: 450 (60%); 0.907: 600 (80%) | OFFLINE |
| ppo_signal | backtest/signals/screener.py +1 | 100.0% | -1.0644, 0.1615, 1.1538, 2.1136 | -1.0644: 600 (80%); 0.1615: 450 (60%); 1.1538: 300 (40%); 2.1136: 150 (20%) | -1.0644: 150 (20%); 0.1615: 300 (40%); 1.1538: 450 (60%); 2.1136: 600 (80%) | OFFLINE |
| roc_12 | backtest/signals/technical.py | 100.0% | -8.2292, 1.8168, 6.1992, 9.95 | -8.2292: 600 (80%); 1.8168: 450 (60%); 6.1992: 300 (40%); 9.95: 150 (20%) | -8.2292: 150 (20%); 1.8168: 300 (40%); 6.1992: 450 (60%); 9.95: 600 (80%) | OFFLINE |
| rsi_14 | backtest/signals/screener.py | 100.0% | 34.906, 56.26, 65.554, 71.424 | 34.906: 600 (80%); 56.26: 450 (60%); 65.554: 300 (40%); 71.424: 150 (20%) | 34.906: 150 (20%); 56.26: 300 (40%); 65.554: 450 (60%); 71.424: 600 (80%) | OFFLINE |
| rsi_2 | backtest/signals/screener.py | 100.0% | 20.666, 49.688, 71.836, 89.604 | 20.666: 600 (80%); 49.688: 450 (60%); 71.836: 300 (40%); 89.604: 150 (20%) | 20.666: 150 (20%); 49.688: 300 (40%); 71.836: 450 (60%); 89.604: 600 (80%) | OFFLINE |
| rsi_21 | backtest/signals/screener.py | 100.0% | 39.354, 52.572, 61.426, 67.224 | 39.354: 600 (80%); 52.572: 450 (60%); 61.426: 300 (40%); 67.224: 150 (20%) | 39.354: 150 (20%); 52.572: 300 (40%); 61.426: 450 (60%); 67.224: 600 (80%) | OFFLINE |
| rsi_9 | (not found by literal grep) | 100.0% | 29.348, 60.8, 70.834, 76.696 | 29.348: 600 (80%); 60.8: 450 (60%); 70.834: 300 (40%); 76.696: 150 (20%) | 29.348: 150 (20%); 60.8: 300 (40%); 70.834: 450 (60%); 76.696: 600 (80%) | OFFLINE |
| sector_etf_return_pct | backtest/engine/backtest.py | 100.0% | 0 | 0: 746 (99%) | 0: 750 (100%) | OFFLINE |
| sector_strongest_rs | backtest/signals/cross_asset.py | 100.0% | 0.0275, 0.0412, 0.0545, 0.0847 | 0.0275: 600 (80%); 0.0412: 450 (60%); 0.0545: 300 (40%); 0.0847: 150 (20%) | 0.0275: 153 (20%); 0.0412: 302 (40%); 0.0545: 450 (60%); 0.0847: 600 (80%) | OFFLINE |
| sector_weakest_rs | backtest/signals/cross_asset.py | 100.0% | -0.0749, -0.0604, -0.0437, -0.037 | -0.0749: 600 (80%); -0.0604: 450 (60%); -0.0437: 301 (40%); -0.037: 151 (20%) | -0.0749: 154 (21%); -0.0604: 301 (40%); -0.0437: 486 (65%); -0.037: 600 (80%) | OFFLINE |
| sell_count | backtest/data/smart_money.py | 100.0% | 0, 2 | 0: 750 (100%); 2: 166 (22%) | 0: 502 (67%); 2: 633 (84%) | OFFLINE |
| short_interest_observations | backtest/signals/short_interest.py | 99.6% | 26, 41, 54, 68.8 | 26: 605 (81%); 41: 463 (62%); 54: 302 (40%); 68.8: 150 (20%) | 26: 156 (21%); 41: 301 (40%); 54: 451 (60%); 68.8: 597 (80%) | OFFLINE |
| short_interest_pct | backtest/signals/screener.py +1 | 98.1% | 0.0111, 0.0159, 0.0219, 0.0358 | 0.0111: 589 (79%); 0.0159: 443 (59%); 0.0219: 296 (39%); 0.0358: 149 (20%) | 0.0111: 148 (20%); 0.0159: 293 (39%); 0.0219: 440 (59%); 0.0358: 587 (78%) | OFFLINE |
| smc_dealing_range_pct | backtest/signals/screener.py +1 | 100.0% | 0.1146, 0.5531, 0.8868, 0.936 | 0.1146: 600 (80%); 0.5531: 450 (60%); 0.8868: 300 (40%); 0.936: 151 (20%) | 0.1146: 150 (20%); 0.5531: 300 (40%); 0.8868: 450 (60%); 0.936: 600 (80%) | OFFLINE |
| smc_retracement_pct | backtest/signals/demand_pruning.py +2 | 100.0% | 18, 54.46, 87.9, 149.88 | 18: 601 (80%); 54.46: 450 (60%); 87.9: 302 (40%); 149.88: 150 (20%) | 18: 151 (20%); 54.46: 300 (40%); 87.9: 452 (60%); 149.88: 600 (80%) | OFFLINE |
| squeeze_momentum | backtest/signals/screener.py +1 | 100.0% | -4.415, 1.077, 4.4555, 10.46 | -4.415: 600 (80%); 1.077: 450 (60%); 4.4555: 300 (40%); 10.46: 150 (20%) | -4.415: 150 (20%); 1.077: 300 (40%); 4.4555: 450 (60%); 10.46: 600 (80%) | OFFLINE |
| stoch_d | backtest/signals/screener.py +1 | 100.0% | 7.794, 82.066, 91.9, 94.822 | 7.794: 600 (80%); 82.066: 450 (60%); 91.9: 300 (40%); 94.822: 150 (20%) | 7.794: 150 (20%); 82.066: 300 (40%); 91.9: 450 (60%); 94.822: 600 (80%) | OFFLINE |
| stoch_k | backtest/signals/technical.py | 100.0% | 9.042, 80.722, 90.788, 93.802 | 9.042: 600 (80%); 80.722: 450 (60%); 90.788: 300 (40%); 93.802: 150 (20%) | 9.042: 150 (20%); 80.722: 300 (40%); 90.788: 450 (60%); 93.802: 600 (80%) | OFFLINE |
| stochrsi_d | backtest/signals/technical.py | 100.0% | 4.02, 46.326, 88.756, 97.46 | 4.02: 601 (80%); 46.326: 450 (60%); 88.756: 300 (40%); 97.46: 150 (20%) | 4.02: 151 (20%); 46.326: 300 (40%); 88.756: 450 (60%); 97.46: 600 (80%) | OFFLINE |
| stochrsi_k | backtest/signals/technical.py | 100.0% | 4.304, 45.178, 85.338, 99.464 | 4.304: 600 (80%); 45.178: 450 (60%); 85.338: 300 (40%); 99.464: 150 (20%) | 4.304: 150 (20%); 45.178: 300 (40%); 85.338: 450 (60%); 99.464: 600 (80%) | OFFLINE |
| trading_day_of_month | backtest/signals/calendar_effects.py | 100.0% | 5, 9, 13, 17 | 5: 611 (81%); 9: 475 (63%); 13: 314 (42%); 17: 173 (23%) | 5: 172 (23%); 9: 305 (41%); 13: 464 (62%); 17: 612 (82%) | OFFLINE |
| trading_days_left_in_month | backtest/signals/calendar_effects.py | 100.0% | 4, 9, 13, 17 | 4: 629 (84%); 9: 470 (63%); 13: 303 (40%); 17: 177 (24%) | 4: 151 (20%); 9: 316 (42%); 13: 478 (64%); 17: 608 (81%) | OFFLINE |
| uo | backtest/signals/screener.py +1 | 100.0% | 38.444, 51.498, 61.34, 66.742 | 38.444: 600 (80%); 51.498: 450 (60%); 61.34: 300 (40%); 66.742: 150 (20%) | 38.444: 150 (20%); 51.498: 300 (40%); 61.34: 450 (60%); 66.742: 600 (80%) | OFFLINE |
| vix_percentile | backtest/signals/technical.py | 100.0% | 0.1151, 0.3285, 0.5754, 0.7421 | 0.1151: 601 (80%); 0.3285: 450 (60%); 0.5754: 304 (41%); 0.7421: 151 (20%) | 0.1151: 153 (20%); 0.3285: 300 (40%); 0.5754: 451 (60%); 0.7421: 601 (80%) | OFFLINE |
| vix_today | backtest/signals/cross_asset.py | 100.0% | 14.212, 16.356, 18.574, 23.936 | 14.212: 600 (80%); 16.356: 450 (60%); 18.574: 300 (40%); 23.936: 150 (20%) | 14.212: 150 (20%); 16.356: 300 (40%); 18.574: 450 (60%); 23.936: 600 (80%) | OFFLINE |
| vix_value | backtest/signals/technical.py +3 | 100.0% | 14.212, 16.356, 18.574, 23.936 | 14.212: 600 (80%); 16.356: 450 (60%); 18.574: 300 (40%); 23.936: 150 (20%) | 14.212: 150 (20%); 16.356: 300 (40%); 18.574: 450 (60%); 23.936: 600 (80%) | OFFLINE |
| vix_vix3m_ratio | backtest/signals/cross_asset.py | 100.0% | 0.8482, 0.8747, 0.9069, 0.9584 | 0.8482: 600 (80%); 0.8747: 452 (60%); 0.9069: 301 (40%); 0.9584: 151 (20%) | 0.8482: 150 (20%); 0.8747: 301 (40%); 0.9069: 454 (61%); 0.9584: 601 (80%) | OFFLINE |
| vol_ratio_20d | backtest/signals/technical.py | 100.0% | 0.74, 0.9, 1.03, 1.26 | 0.74: 602 (80%); 0.9: 452 (60%); 1.03: 305 (41%); 1.26: 152 (20%) | 0.74: 157 (21%); 0.9: 316 (42%); 1.03: 455 (61%); 1.26: 603 (80%) | OFFLINE |
| vp_close_near_poc_pct | backtest/signals/screener.py +1 | 100.0% | 0.0351, 0.068, 0.0984, 0.1499 | 0.0351: 600 (80%); 0.068: 450 (60%); 0.0984: 301 (40%); 0.1499: 150 (20%) | 0.0351: 150 (20%); 0.068: 300 (40%); 0.0984: 451 (60%); 0.1499: 600 (80%) | OFFLINE |
| vwap_lower_2 | backtest/signals/technical.py | 100.0% | 42.4853, 71.9964, 115.3636, 198.7089 | 42.4853: 600 (80%); 71.9964: 450 (60%); 115.3636: 300 (40%); 198.7089: 150 (20%) | 42.4853: 150 (20%); 71.9964: 300 (40%); 115.3636: 450 (60%); 198.7089: 600 (80%) | OFFLINE |
| week_open_gap_down_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 750 (100%) | 0: 690 (92%) | OFFLINE |
| week_open_gap_up_pct | backtest/signals/ict_producers.py | 100.0% | 0 | 0: 750 (100%) | 0: 685 (91%) | OFFLINE |
| weekly_momentum_4w | backtest/signals/multi_timeframe.py | 100.0% | -0.0862, 0.0137, 0.0768, 0.1152 | -0.0862: 600 (80%); 0.0137: 450 (60%); 0.0768: 301 (40%); 0.1152: 151 (20%) | -0.0862: 151 (20%); 0.0137: 300 (40%); 0.0768: 451 (60%); 0.1152: 600 (80%) | OFFLINE |
| xs_beta | backtest/signals/cross_sectional.py | 98.7% | 0.5111, 0.8069, 1.0315, 1.2839 | 0.5111: 592 (79%); 0.8069: 444 (59%); 1.0315: 297 (40%); 1.2839: 148 (20%) | 0.5111: 148 (20%); 0.8069: 296 (39%); 1.0315: 444 (59%); 1.2839: 592 (79%) | OFFLINE |
| xs_beta_decile | backtest/signals/cross_sectional.py | 98.7% | 3, 5, 7, 9 | 3: 600 (80%); 5: 481 (64%); 7: 327 (44%); 9: 161 (21%) | 3: 185 (25%); 5: 341 (45%); 7: 491 (65%); 9: 650 (87%) | OFFLINE |
| xs_ivol | backtest/signals/cross_sectional.py +1 | 98.7% | 0.1798, 0.2152, 0.2627, 0.3215 | 0.1798: 592 (79%); 0.2152: 445 (59%); 0.2627: 297 (40%); 0.3215: 148 (20%) | 0.1798: 149 (20%); 0.2152: 297 (40%); 0.2627: 444 (59%); 0.3215: 592 (79%) | OFFLINE |
| xs_ivol_decile | backtest/signals/cross_sectional.py +1 | 98.7% | 3, 5, 7, 9 | 3: 603 (80%); 5: 464 (62%); 7: 330 (44%); 9: 164 (22%) | 3: 202 (27%); 5: 350 (47%); 7: 478 (64%); 9: 673 (90%) | OFFLINE |
| xs_max_anomaly | backtest/signals/cross_sectional.py | 98.7% | 0.0215, 0.0295, 0.0393, 0.0542 | 0.0215: 593 (79%); 0.0295: 444 (59%); 0.0393: 297 (40%); 0.0542: 149 (20%) | 0.0215: 150 (20%); 0.0295: 300 (40%); 0.0393: 444 (59%); 0.0542: 592 (79%) | OFFLINE |
| xs_max_anomaly_decile | backtest/signals/cross_sectional.py | 98.7% | 3, 5, 7, 9 | 3: 597 (80%); 5: 470 (63%); 7: 341 (45%); 9: 176 (23%) | 3: 194 (26%); 5: 331 (44%); 7: 476 (63%); 9: 657 (88%) | OFFLINE |
| xs_momentum_12_1 | backtest/signals/cross_sectional.py | 99.2% | -0.1659, -0.0389, 0.0856, 0.2446 | -0.1659: 595 (79%); -0.0389: 447 (60%); 0.0856: 298 (40%); 0.2446: 149 (20%) | -0.1659: 149 (20%); -0.0389: 298 (40%); 0.0856: 446 (59%); 0.2446: 595 (79%) | OFFLINE |
| xs_momentum_decile | backtest/signals/cross_sectional.py | 99.2% | 3, 5, 6, 8.4 | 3: 598 (80%); 5: 450 (60%); 6: 375 (50%); 8.4: 149 (20%) | 3: 223 (30%); 5: 369 (49%); 6: 448 (60%); 8.4: 595 (79%) | OFFLINE |

### Binary companions (offline AND-able; no band - a boolean has no threshold)

| key | fire-rate on surviving fires |
|---|---|
| 8k_item_1_01_filed_within_30d | 5.1% |
| 8k_item_5_02_filed_within_7d | 3.6% |
| above_avwap_20high | 13.2% |
| above_avwap_20low | 92.7% |
| above_avwap_252low | 76.6% |
| above_avwap_50low | 79.7% |
| above_cam_r3 | 18.3% |
| above_cam_r4 | 3.3% |
| above_cpr | 53.5% |
| above_pivot | 51.7% |
| above_prev_high | 10.1% |
| above_prev_high_clearance_atr_05 | 0.1% |
| above_prev_low | 89.2% |
| above_r1 | 4.5% |
| above_r2 | 0.3% |
| above_vwap | 56.9% |
| above_wood_p | 59.5% |
| ad_rising | 60.3% |
| adx_cross_up | 4.4% |
| adx_cross_up_20 | 4.3% |
| adx_di_bear | 38.3% |
| adx_di_bull | 61.7% |
| adx_strong | 11.2% |
| adx_trending | 51.6% |
| ao_cross_dn | 1.7% |
| ao_cross_up | 0.4% |
| ao_positive | 62.0% |
| ao_twin_peaks_bull | 0.4% |
| at_key_fib | 6.7% |
| at_key_fib_wide | 15.7% |
| avwap_20high_loss_recent_3d | 12.1% |
| avwap_20high_reclaim_recent_3d | 7.6% |
| avwap_20low_loss_recent_3d | 2.2% |
| avwap_20low_reclaim_recent_3d | 7.3% |
| avwap_252low_loss_recent_3d | 4.7% |
| avwap_252low_reclaim_recent_3d | 3.0% |
| avwap_50low_loss_recent_3d | 3.5% |
| avwap_50low_reclaim_recent_3d | 2.5% |
| bb_10_20_above_mid | 61.6% |
| bb_10_20_expanding | 58.1% |
| bb_10_20_pctb_gt_75 | 49.1% |
| bb_10_20_pctb_gt_8 | 33.5% |
| bb_10_20_pctb_gt_85 | 11.2% |
| bb_10_20_pctb_gt_9 | 2.1% |
| bb_10_20_pctb_gt_95 | 0.7% |
| bb_10_20_pctb_lt_05 | 0.5% |
| bb_10_20_pctb_lt_1 | 2.8% |
| bb_10_20_pctb_lt_15 | 10.4% |
| bb_10_20_pctb_lt_2 | 22.3% |
| bb_10_20_pctb_lt_25 | 31.6% |
| bb_10_20_reclaim_from_lower_recent_3d | 10.4% |
| bb_10_20_reclaim_from_upper_recent_3d | 18.0% |
| bb_10_20_squeeze | 27.9% |
| bb_10_20_touch_lower | 0.9% |
| bb_10_20_touch_upper | 2.0% |
| bb_20_15_above_mid | 61.5% |
| bb_20_15_expanding | 80.1% |
| bb_20_15_pctb_gt_75 | 61.3% |
| bb_20_15_pctb_gt_8 | 60.5% |
| bb_20_15_pctb_gt_85 | 58.9% |
| bb_20_15_pctb_gt_9 | 55.1% |
| bb_20_15_pctb_gt_95 | 48.5% |
| bb_20_15_pctb_lt_05 | 30.7% |
| bb_20_15_pctb_lt_1 | 34.0% |
| bb_20_15_pctb_lt_15 | 35.9% |
| bb_20_15_pctb_lt_2 | 37.5% |
| bb_20_15_pctb_lt_25 | 38.1% |
| bb_20_15_reclaim_from_lower_recent_3d | 7.9% |
| bb_20_15_reclaim_from_upper_recent_3d | 14.5% |
| bb_20_15_squeeze | 23.9% |
| bb_20_15_touch_lower | 29.7% |
| bb_20_15_touch_upper | 48.4% |
| bb_20_20_above_mid | 61.5% |
| bb_20_20_expanding | 80.1% |
| bb_20_20_pctb_gt_75 | 59.7% |
| bb_20_20_pctb_gt_8 | 55.1% |
| bb_20_20_pctb_gt_85 | 45.7% |
| bb_20_20_pctb_gt_9 | 32.1% |
| bb_20_20_pctb_gt_95 | 16.7% |
| bb_20_20_pctb_lt_05 | 10.8% |
| bb_20_20_pctb_lt_1 | 20.7% |
| bb_20_20_pctb_lt_15 | 28.9% |
| bb_20_20_pctb_lt_2 | 34.0% |
| bb_20_20_pctb_lt_25 | 36.4% |
| bb_20_20_reclaim_from_lower_recent_3d | 15.1% |
| bb_20_20_reclaim_from_upper_recent_3d | 26.7% |
| bb_20_20_squeeze | 9.7% |
| bb_20_20_touch_lower | 8.8% |
| bb_20_20_touch_upper | 14.8% |
| bearish_pin_bar | 9.3% |
| below_avwap_20high | 86.8% |
| below_avwap_20low | 7.2% |
| below_avwap_252low | 23.4% |
| below_avwap_50low | 20.1% |
| below_cam_s3 | 19.9% |
| below_cam_s4 | 3.9% |
| below_cpr | 48.1% |
| below_ema_20 | 38.5% |
| below_ema_200 | 41.6% |
| below_ema_200_break_recent_5d | 10.3% |
| below_ema_20_break_recent_5d | 6.7% |
| below_ema_21 | 38.5% |
| below_ema_21_break_recent_5d | 7.1% |
| below_ema_50 | 38.7% |
| below_ema_50_break_recent_5d | 10.1% |
| below_ema_9 | 38.5% |
| below_ema_9_break_recent_5d | 6.4% |
| below_prev_high | 89.6% |
| below_prev_low | 10.5% |
| below_prev_low_clearance_atr_05 | 1.1% |
| below_s1 | 4.7% |
| below_s2 | 1.2% |
| below_sma_20 | 38.5% |
| below_sma_200 | 40.0% |
| below_sma_21 | 38.5% |
| below_sma_50 | 37.9% |
| below_sma_9 | 38.4% |
| below_vwap | 43.1% |
| blowoff_recent_3d | 1.1% |
| break_52w_high | 2.9% |
| break_52w_high_confirmed_today | 12.0% |
| break_52w_low | 1.6% |
| bullish_pin_bar | 11.1% |
| capitulation_recent_3d | 1.1% |
| ceo_buy | 0.3% |
| cfo_buy | 0.1% |
| chandelier_long_bullish | 62.5% |
| chandelier_long_flip_dn | 0.9% |
| chandelier_short_bearish | 40.0% |
| chandelier_short_flip_up | 0.4% |
| close_above_open | 38.5% |
| close_below_open | 61.5% |
| close_in_bottom_40pct_of_range | 43.7% |
| close_in_top_40pct_of_range | 34.8% |
| cluster_buy | 0.3% |
| cmf_cross_dn | 1.9% |
| cmf_cross_up | 2.8% |
| cmf_negative | 36.9% |
| cmf_positive | 63.1% |
| concentrated_sell | 8.3% |
| cpr_narrow | 85.5% |
| cpr_narrow_tight | 19.3% |
| cup_handle_detected | 15.8% |
| cup_handle_neckline_break_retest_long | 15.2% |
| dc10_breakout_dn | 9.7% |
| dc10_breakout_dn_1pct | 21.7% |
| dc10_breakout_up | 12.4% |
| dc10_breakout_up_1pct | 40.4% |
| dc10_new_high | 42.0% |
| dc10_strong_breakout_dn | 0.7% |
| dc10_strong_breakout_up | 0.1% |
| dc20_breakout_dn | 9.2% |
| dc20_breakout_up | 12.0% |
| dc20_new_high | 41.3% |
| dc20_resistance_break_retest_strong | 43.5% |
| dc20_support_break_retest_strong | 25.2% |
| defensive_leadership | 46.0% |
| director_only_buy | 2.2% |
| doji | 8.5% |
| double_bottom_detected | 15.5% |
| double_top_detected | 16.1% |
| dpi_elevated | 49.5% |
| drying_volume_on_down_turn | 38.0% |
| drying_volume_on_up_turn | 17.9% |
| ema_20_50_bearish | 39.1% |
| ema_20_50_bullish | 60.9% |
| ema_20_50_death_cross | 1.7% |
| ema_20_50_golden_cross | 1.2% |
| ema_50_200_bearish | 43.1% |
| ema_50_200_bullish | 56.9% |
| ema_50_200_death_cross | 0.5% |
| ema_50_200_golden_cross | 0.7% |
| ema_9_21_bearish | 38.4% |
| ema_9_21_bullish | 61.6% |
| ema_9_21_death_cross | 0.7% |
| ema_9_21_golden_cross | 0.4% |
| evening_star | 0.8% |
| flag_bear_break_retest_short | 0.5% |
| flag_bear_broke | 0.5% |
| flag_bear_detected | 0.4% |
| flag_bull_break_retest_long | 3.6% |
| flag_bull_broke | 3.9% |
| flag_bull_detected | 1.1% |
| force_index_cross_dn | 0.3% |
| force_index_cross_up | 0.1% |
| force_index_positive | 61.6% |
| gap_dn_1_5pct | 9.1% |
| gap_dn_2pct | 4.8% |
| gap_up_1_5pct | 4.8% |
| gap_up_2pct | 2.0% |
| hammer | 8.1% |
| head_shoulders_bottom_detected | 4.8% |
| head_shoulders_top_detected | 4.3% |
| house_cluster_buy | 4.7% |
| house_cluster_sell | 5.0% |
| htf_aligned_bear | 30.3% |
| htf_aligned_bull | 51.2% |
| htf_disagreement | 2.0% |
| hull_bearish | 38.4% |
| hull_bullish | 61.6% |
| hull_flip_dn | 0.7% |
| hull_flip_up | 0.7% |
| ichi_above_cloud | 58.5% |
| ichi_above_cloud_break_recent_5d | 13.2% |
| ichi_below_cloud | 31.9% |
| ichi_below_cloud_break_recent_5d | 10.1% |
| ichi_cloud_thick | 85.1% |
| ichi_tk_bearish | 36.5% |
| ichi_tk_bullish | 59.7% |
| ichi_tk_cross_dn | 2.0% |
| ichi_tk_cross_up | 1.7% |
| ichi_weekly_above_cloud | 47.8% |
| ichi_weekly_below_cloud | 26.9% |
| ichi_weekly_in_cloud | 25.4% |
| in_reversal_window | 1.2% |
| inside_bar | 15.9% |
| inside_cpr | 7.3% |
| inside_kc | 50.7% |
| insider_cluster_active | 15.4% |
| institutional_buy | 88.8% |
| institutional_negative | 5.1% |
| institutional_persistence_growing | 38.1% |
| institutional_persistence_strong | 56.9% |
| institutional_strong_buy | 77.7% |
| inverted_cup_handle_detected | 10.0% |
| is_friday | 24.4% |
| is_halloween_period | 44.9% |
| is_halloween_period_first_day | 0.1% |
| is_january | 10.1% |
| is_january_extended | 12.5% |
| is_monday | 14.5% |
| is_pre_holiday | 5.6% |
| is_summer_period | 55.1% |
| is_totm_window | 35.2% |
| is_totm_window_first_day | 11.2% |
| is_week_open | 16.8% |
| kc_touch_lower | 20.3% |
| kc_touch_upper | 39.9% |
| large_dollar_buy | 0.7% |
| macd_12_26_9_bearish | 40.1% |
| macd_12_26_9_bullish | 59.9% |
| macd_12_26_9_crossover_dn | 0.8% |
| macd_12_26_9_crossover_up | 0.3% |
| macd_8_21_5_bearish | 40.8% |
| macd_8_21_5_bullish | 59.2% |
| macd_8_21_5_crossover_dn | 0.9% |
| macd_8_21_5_crossover_up | 0.4% |
| marubozu_bear | 0.3% |
| mfi_broad_overbought | 38.3% |
| mfi_broad_oversold | 21.2% |
| mfi_overbought | 16.7% |
| mfi_oversold | 9.5% |
| monthly_above_sma_12 | 58.8% |
| monthly_above_sma_6 | 61.2% |
| monthly_bias_bear | 33.9% |
| monthly_bias_bull | 53.9% |
| monthly_momentum_pos | 59.2% |
| morning_star | 1.2% |
| near_52w_high | 24.8% |
| near_52w_high_95pct | 32.3% |
| near_52w_high_retest_long | 0.1% |
| near_52w_low | 7.1% |
| near_52w_low_105pct | 11.7% |
| near_52w_low_retest_short | 0.1% |
| near_avwap_20high_atr_05x | 32.0% |
| near_avwap_20high_atr_10x | 38.4% |
| near_avwap_20high_atr_15x | 53.3% |
| near_avwap_20high_atr_20x | 71.6% |
| near_avwap_20low_atr_05x | 14.5% |
| near_avwap_20low_atr_10x | 16.5% |
| near_avwap_20low_atr_15x | 25.6% |
| near_avwap_20low_atr_20x | 42.7% |
| near_avwap_252low_atr_05x | 8.3% |
| near_avwap_252low_atr_10x | 15.4% |
| near_avwap_252low_atr_15x | 22.7% |
| near_avwap_252low_atr_20x | 30.6% |
| near_avwap_50low_atr_05x | 9.0% |
| near_avwap_50low_atr_10x | 13.2% |
| near_avwap_50low_atr_15x | 20.6% |
| near_avwap_50low_atr_20x | 31.7% |
| near_cam_r3 | 30.0% |
| near_cam_s3 | 35.5% |
| near_cam_s4 | 8.0% |
| near_fib_236 | 3.9% |
| near_fib_382 | 2.4% |
| near_fib_500 | 2.0% |
| near_fib_618 | 2.3% |
| near_fib_786 | 1.7% |
| near_pivot | 46.7% |
| near_prev_close | 30.1% |
| near_prev_high | 16.1% |
| near_prev_low | 7.5% |
| near_r1 | 11.2% |
| near_r1_wide | 69.1% |
| near_r2 | 1.5% |
| near_r2_wide | 33.7% |
| near_s1 | 9.1% |
| near_s1_wide | 73.5% |
| near_s2 | 2.0% |
| near_s2_wide | 26.1% |
| near_s3 | 0.4% |
| near_wood_r1 | 44.4% |
| near_wood_s1 | 23.7% |
| news_uses_polygon_score | 20.3% |
| obv_bearish | 39.2% |
| obv_bullish | 60.8% |
| obv_diverge_bull | 3.7% |
| obv_falling | 41.9% |
| obv_rising | 58.1% |
| outside_bar | 4.7% |
| pead_negative_surprise | 15.2% |
| pead_positive_surprise | 27.3% |
| pin_bar | 20.4% |
| po3_accumulation_active | 28.8% |
| po3_bearish | 22.1% |
| po3_bullish | 18.7% |
| po3_manipulation_sweep_down | 3.7% |
| po3_manipulation_sweep_up | 14.0% |
| po3_mmbm_setup | 2.7% |
| po3_mmsm_setup | 10.7% |
| po3_sweep_above_prior_high | 53.7% |
| po3_sweep_below_prior_low | 42.8% |
| ppo_bullish | 58.9% |
| ppo_crossover_dn | 0.4% |
| pre_fomc_d0 | 2.3% |
| pre_fomc_d1 | 2.5% |
| pre_fomc_window | 4.8% |
| price_above_dema | 60.0% |
| price_above_ema_20 | 61.5% |
| price_above_ema_200 | 58.4% |
| price_above_ema_200_break_recent_5d | 7.6% |
| price_above_ema_20_break_recent_5d | 4.1% |
| price_above_ema_21 | 61.5% |
| price_above_ema_21_break_recent_5d | 4.4% |
| price_above_ema_50 | 61.3% |
| price_above_ema_50_break_recent_5d | 8.7% |
| price_above_ema_9 | 61.5% |
| price_above_ema_9_break_recent_5d | 5.3% |
| price_above_hull | 54.7% |
| price_above_sma_200 | 60.0% |
| price_above_sma_21 | 61.5% |
| price_above_sma_50 | 62.1% |
| price_above_tema | 53.1% |
| price_below_dema | 40.0% |
| price_below_hull | 45.3% |
| price_below_tema | 46.9% |
| psar_bullish | 61.5% |
| psar_flip_dn | 0.1% |
| psar_flip_up | 0.3% |
| r1_break_retest_long | 61.1% |
| recent_blowoff_at_r3 | 0.9% |
| recent_capitulation_at_s3 | 0.4% |
| resistance_break_retest | 55.6% |
| risk_off_regime_bond_signal | 14.4% |
| risk_off_regime_bond_signal_strong | 5.1% |
| risk_off_regime_gold_signal | 34.8% |
| risk_on_regime_bond_signal | 55.5% |
| risk_on_regime_bond_signal_strong | 20.8% |
| roc_positive | 61.3% |
| roc_turning_dn | 0.3% |
| roc_turning_up | 0.1% |
| rsi_14_bullish | 61.3% |
| rsi_14_cross_dn_extreme_ob_recent_3d | 1.5% |
| rsi_14_cross_dn_overbought_recent_3d | 5.7% |
| rsi_14_cross_up_extreme_os_recent_3d | 0.7% |
| rsi_14_cross_up_oversold_recent_3d | 2.1% |
| rsi_14_extreme_ob | 3.5% |
| rsi_14_extreme_os | 1.2% |
| rsi_14_overbought | 25.6% |
| rsi_14_oversold | 10.9% |
| rsi_14_rising | 44.9% |
| rsi_21_bullish | 61.5% |
| rsi_21_cross_dn_extreme_ob_recent_3d | 0.7% |
| rsi_21_cross_dn_overbought_recent_3d | 4.3% |
| rsi_21_cross_up_oversold_recent_3d | 1.3% |
| rsi_21_extreme_ob | 1.2% |
| rsi_21_extreme_os | 0.3% |
| rsi_21_overbought | 10.4% |
| rsi_21_oversold | 4.4% |
| rsi_21_rising | 44.9% |
| rsi_2_bullish | 59.9% |
| rsi_2_cross_dn_extreme_ob_recent_3d | 31.6% |
| rsi_2_cross_dn_overbought_recent_3d | 20.7% |
| rsi_2_cross_up_extreme_os_recent_3d | 18.3% |
| rsi_2_cross_up_oversold_recent_3d | 13.1% |
| rsi_2_extreme_ob | 28.4% |
| rsi_2_extreme_os | 19.5% |
| rsi_2_overbought | 41.3% |
| rsi_2_oversold | 25.9% |
| rsi_2_rising | 44.9% |
| rsi_9_bullish | 61.5% |
| rsi_9_cross_dn_extreme_ob_recent_3d | 8.1% |
| rsi_9_cross_dn_overbought_recent_3d | 6.8% |
| rsi_9_cross_up_extreme_os_recent_3d | 3.5% |
| rsi_9_cross_up_oversold_recent_3d | 4.9% |
| rsi_9_extreme_ob | 11.5% |
| rsi_9_extreme_os | 4.8% |
| rsi_9_overbought | 42.5% |
| rsi_9_oversold | 22.0% |
| rsi_9_rising | 44.9% |
| s1_break_retest_short | 38.0% |
| sc_13d_filed_within_30d | 1.0% |
| sc_13g_filed_within_30d | 2.7% |
| sector_outperforming_spy | 52.9% |
| sector_underperforming_spy | 47.1% |
| shooting_star | 5.9% |
| sma_20_50_bullish | 62.8% |
| sma_20_50_golden_cross | 2.0% |
| sma_50_200_bullish | 55.0% |
| sma_50_200_golden_cross | 0.4% |
| sma_9_21_bullish | 61.2% |
| sma_9_21_golden_cross | 0.7% |
| smc_bos_bearish | 10.9% |
| smc_bos_bullish | 16.1% |
| smc_bos_retest_long | 5.2% |
| smc_bos_retest_short | 3.6% |
| smc_breaker_block_bearish | 14.8% |
| smc_breaker_block_bullish | 26.5% |
| smc_choch_bearish | 4.3% |
| smc_choch_bullish | 4.9% |
| smc_equal_highs_swept | 5.3% |
| smc_equal_lows_swept | 3.5% |
| smc_fvg_bearish_active | 32.5% |
| smc_fvg_bullish_active | 54.0% |
| smc_fvg_retest_long_zone | 6.8% |
| smc_fvg_retest_short_zone | 4.7% |
| smc_in_discount_zone | 41.3% |
| smc_in_premium_zone | 67.5% |
| smc_inverse_fvg_bearish | 55.7% |
| smc_inverse_fvg_bullish | 76.0% |
| smc_liquidity_swept_dn | 2.5% |
| smc_liquidity_swept_up | 1.2% |
| smc_mitigation_block_long | 1.9% |
| smc_mitigation_block_short | 5.2% |
| smc_ob_bearish_active | 28.8% |
| smc_ob_bullish_active | 41.1% |
| smc_ote_long_zone | 3.6% |
| smc_ote_short_zone | 8.7% |
| squeeze_fire_dn | 0.1% |
| squeeze_in | 6.0% |
| squeeze_positive | 61.5% |
| stoch_bearish_cross | 61.5% |
| stoch_broad_overbought | 61.5% |
| stoch_broad_oversold | 38.3% |
| stoch_bullish_cross | 38.5% |
| stoch_overbought | 60.7% |
| stoch_oversold | 37.9% |
| stochrsi_cross_dn | 33.1% |
| stochrsi_cross_up | 20.0% |
| stochrsi_overbought | 45.3% |
| stochrsi_oversold | 30.8% |
| supertrend_bearish | 1.5% |
| supertrend_bullish | 98.5% |
| supertrend_flip_recent_long_5d | 1.2% |
| supertrend_flip_recent_short_5d | 1.5% |
| supertrend_flip_up | 0.4% |
| support_break_retest | 33.2% |
| tema_above_dema | 61.5% |
| tema_cross_dn | 1.1% |
| tema_cross_up | 1.1% |
| triangle_apex_break_retest_long | 18.4% |
| triangle_ascending_detected | 12.9% |
| triangle_descending_detected | 6.7% |
| uo_overbought | 9.6% |
| uo_oversold | 4.5% |
| usd_strengthening | 24.7% |
| usd_weakening | 8.4% |
| vix_band_high | 28.1% |
| vix_band_low | 40.0% |
| vix_band_mid | 31.9% |
| vix_term_backwardation | 3.3% |
| vix_term_contango | 96.7% |
| vol_above_avg | 44.1% |
| vol_below_avg | 55.9% |
| vol_spike_12x | 23.6% |
| vol_spike_15x | 8.4% |
| vol_spike_17x | 5.6% |
| vol_spike_2x | 3.3% |
| vol_spike_2x_on_down_day_recent_3d | 3.1% |
| vol_spike_2x_on_up_day_recent_3d | 2.1% |
| vol_spike_3x | 0.7% |
| vp_above_value_area | 44.7% |
| vp_below_value_area | 20.9% |
| vp_close_above_poc | 64.3% |
| vp_close_below_poc | 35.7% |
| vp_in_value_area | 34.4% |
| week_open_gap_down_15pct | 2.1% |
| week_open_gap_up_15pct | 0.8% |
| weekly_above_ema_10 | 61.1% |
| weekly_above_ema_20 | 60.8% |
| weekly_bias_bear | 37.3% |
| weekly_bias_bull | 59.2% |
| weekly_momentum_pos | 61.6% |
| williams_r_overbought | 61.5% |
| williams_r_oversold | 38.5% |
| williams_r_rising | 42.1% |
| within_pead_window | 48.7% |
| within_post_deletion_window | 3.7% |
| xs_avoid_high_ivol | 77.8% |
| xs_avoid_high_max | 76.2% |
| xs_high_beta_decile | 21.8% |
| xs_low_beta_bottom_quintile | 21.8% |
| xs_low_beta_decile | 18.9% |
| xs_low_beta_decile_entry_recent_5d | 0.7% |
| xs_low_beta_top_quintile | 18.9% |
| xs_momentum_bottom_decile | 10.2% |
| xs_momentum_bottom_quintile | 19.6% |
| xs_momentum_top_decile | 10.1% |
| xs_momentum_top_quintile | 20.0% |
| xs_quality_bottom_quintile | 20.0% |
| xs_quality_top_quintile | 23.0% |
| xs_quality_top_tercile | 41.6% |
| year_high_break_retest_long | 17.2% |
| year_low_break_retest_short | 5.5% |
| yoy_surprise_high | 52.3% |
| yoy_surprise_negative | 37.1% |

### Below the 0.98 coverage floor - RESIM-ONLY

| key | coverage |
|---|---|
| avg_position_age_quarters | 90.9% |
| committed_growth_holders | 90.9% |
| corp_donations_1y | 8.9% |
| corp_donations_count_1y | 8.9% |
| corp_donations_unique_pacs | 8.9% |
| cot_rut_commercials_pctile_3y | 49.9% |
| cot_rut_mmoney_pctile_3y | 49.9% |
| cup_handle_depth_pct | 21.7% |
| days_since_deletion | 7.2% |
| days_since_inclusion | 11.1% |
| days_to_next_holiday | 67.1% |
| days_to_rebalance | 8.4% |
| dpi_30d_avg | 95.9% |
| dpi_recent | 95.9% |
| earnings_announcement_return | 91.2% |
| earnings_eps_yoy_growth | 94.5% |
| flag_bear_pole_move_pct | 0.4% |
| flag_bull_pole_move_pct | 1.1% |
| gov_contracts_4q_sum | 40.8% |
| gov_contracts_last_qtr_amount | 40.8% |
| gov_contracts_qoq_growth | 40.8% |
| head_shoulders_magnitude_pct | 9.1% |
| insider_director_buyers_30d | 3.5% |
| insider_officer_buyers_30d | 3.5% |
| insider_total_shares_bought_30d | 3.5% |
| insider_unique_buyers_30d | 3.5% |
| inverted_cup_handle_height_pct | 19.6% |
| lobbying_amount_1y | 71.2% |
| lobbying_amount_q | 71.2% |
| lobbying_amount_yoy | 71.2% |
| otc_short_ratio_recent | 95.9% |
| otc_volume_recent | 95.9% |
| pair_half_life | 89.5% |
| pair_max_abs_zscore | 89.5% |
| pair_zscore_signed | 89.5% |
| pct_from_avwap_20high | 58.3% |
| pct_from_avwap_20low | 72.8% |
| pct_from_avwap_252low | 92.9% |
| pct_from_avwap_50low | 84.1% |
| persistent_holders_4q | 90.9% |
| persistent_holders_8q | 90.9% |
| sc_13g_latest_percent_owned | 0.9% |
| search_volume_index_recent | 79.3% |
| search_volume_observations | 79.3% |
| search_volume_zscore_30d | 79.3% |
| sector_etf_return_20d | 2.3% |
| spy_return_20d | 2.3% |
| total_active_holders | 90.9% |
| triangle_breakdown_pct | 6.7% |
| triangle_breakout_pct | 12.9% |
| xs_quality_decile | 63.2% |
| xs_quality_gross_profitability | 63.2% |

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`avwap_20high` (0.998), `avwap_20low` (0.997), `avwap_252low` (0.996), `avwap_50low` (0.998), `bb_10_20_lower` (0.996), `bb_10_20_mid` (0.999), `bb_10_20_upper` (0.998), `bb_20_15_lower` (0.998), `bb_20_15_mid` (1.0), `bb_20_15_upper` (0.999), `bb_20_20_lower` (0.997), `bb_20_20_mid` (1.0), `bb_20_20_upper` (0.999), `cam_r1` (0.995), `cam_r2` (0.995), `cam_r3` (0.995), `cam_r4` (0.995), `cam_s1` (0.995), `cam_s2` (0.995), `cam_s3` (0.995), `cam_s4` (0.995), `chandelier_long_value` (0.999), `chandelier_short_value` (0.999), `cpr_bottom` (0.995), `cpr_top` (0.996), `cup_handle_breakout_level` (0.999), `cup_handle_rim` (0.999), `dc10_lower` (0.997), `dc10_mid` (0.999), `dc10_upper` (0.999), `dc20_lower` (0.998), `dc20_mid` (1.0), `dc20_upper` (0.999), `dema` (0.998), `double_bottom_neckline` (0.997), `double_bottom_trough` (0.998), `double_top_neckline` (0.997), `double_top_peak` (0.997), `entry_stop_long` (0.994), `entry_stop_short` (0.996), `fib_236` (0.998), `fib_382` (0.998), `fib_500` (0.998), `fib_618` (0.998), `fib_786` (0.998), `fib_ext_127` (0.996), `fib_ext_162` (0.994), `flag_bear_breakdown_level` (1.0), `flag_bull_breakout_level` (1.0), `head_shoulders_bottom_neckline` (0.999), `head_shoulders_top_neckline` (0.998), `hull_ma` (0.996), `ichi_kijun` (1.0), `ichi_senkou_a` (0.995), `ichi_senkou_b` (0.993), `ichi_tenkan` (0.999), `inverted_cup_handle_breakdown_level` (0.998), `inverted_cup_handle_rim_low` (0.998), `kc_lower` (0.999), `kc_mid` (1.0), `kc_upper` (1.0), `monthly_close` (0.996), `monthly_sma_12` (0.99), `monthly_sma_6` (0.997), `pivot` (0.995), `prev_close` (0.995), `prev_high` (0.996), `prev_low` (0.995), `psar_value` (0.999), `r1` (0.995), `r2` (0.996), `r3` (0.995), `s1` (0.995), `s2` (0.995), `s3` (0.994), `supertrend_value` (0.995), `swing_high` (0.997), `swing_low` (0.995), `tema` (0.996), `triangle_resistance_level` (1.0), `triangle_support_level` (1.0), `vp_poc` (0.996), `vp_value_area_high` (0.997), `vp_value_area_low` (0.996), `vwap` (0.958), `vwap_lower_1` (0.954), `vwap_upper_1` (0.961), `vwap_upper_2` (0.963), `weekly_close` (0.995), `weekly_ema_10` (0.999), `weekly_ema_20` (0.998), `wood_p` (0.996), `wood_r1` (0.996), `wood_r2` (0.996), `wood_s1` (0.996), `wood_s2` (0.995), `year_high` (0.982), `year_low` (0.979)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.

## Factorial - configs this table implies (computed from the rows above; pairs with the Formula in Section 1)

| axis | parameter | n levels | class | own engine run? |
|---|---|---|---|---|
| P1.1 | proximity tolerance to Camarilla R3 (abs | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P2.1 | proximity tolerance to Camarilla S3 (abs | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P3.1 | proximity tolerance to R1 (abs dist/leve | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P4.1 | proximity tolerance to R2 (abs dist/leve | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P5.1 | proximity tolerance to S1 (abs dist/leve | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P6.1 | proximity tolerance to S2 (abs dist/leve | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P7.1 | proximity tolerance to S3 (abs dist/leve | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P8.1 | proximity tolerance to Woodie R1 (abs di | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P9.1 | proximity tolerance to Woodie S1 (abs di | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P10.1 | mirror of stoch_bullish_cross | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P11.1 | stochastic (k, smooth, d) | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P11.2 | cross freshness (k over d today) | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |
| P12.1 | period | 3 | **FIRE-ADDING** | **YES** |
| P12.2 | oversold threshold | 3 | subset-safe | no - derives offline |
| P13 | williams_r > -20 | 4 | subset-safe | no - derives offline |
| P14 | days_to_cover cap 5.0 | 1 | **FIRE-ADDING** | no - production only (DEFINED-NO-ACTUATOR) |

```
FULL FACTORIAL     1 x 1 x 1 x 1 x 1 x 1 x 1 x 1 x 1 x 1 x 1 x 1 x 3 x 3 x 4 x 1 = 36
offline gradings   12 level-combinations x 24 exits = 288
ENGINE RUNS        3 (every fire-adding axis sits at production-only until its env actuator exists)
check              3 x 12 = 36
```

B-row candidates NOT in this factorial: 639 census axes join it only when REGISTERED at the T3 band review.
