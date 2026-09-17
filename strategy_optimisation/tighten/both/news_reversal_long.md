# Table A - news_reversal_long

**Build (L803/#309):** generator scripts/build_table_a.py | cube output_r5_merged_1_7 | status build 6c19c4cf9 | commit 8233e68a5 at 2026-09-17 00:26:53 - a copy without this line, or with a stale stamp, is NOT the current band set

**Lane:** BOTH | **family:** news_sentiment | **status:** NOT-STARTED | **R5 fires:** 1 | **surviving fires (T1):** 1 (unchanged since R5 - filter is identity)

**SPECS entry:** NONE - build at R1 before any engine leg (W-T T0)

## Formula (Section 1 of the SS6/#183 locked artifact)

=============================== PRODUCER LAYER ===============================

P1  close_above_open  <- backtest/signals/screener.py +1
       knobs P1.1-P1.1 (band rows in Table A)
P2  close_in_top_40pct_of_range  <- backtest/signals/screener.py +1
       knobs P2.1-P2.1 (band rows in Table A)

============================== STRATEGY LAYER ==============================

P3  news_count_5d >= 3   [EXISTING-THRESHOLD]
P4  news_sentiment_5d <= -0.3   [EXISTING-THRESHOLD]
P5  news_sentiment_shift > 0.2   [EXISTING-THRESHOLD]
P6  pct_change_5d < -0.1   [EXISTING-THRESHOLD]

Gate body, VERBATIM from backtest/signals/screener.py strat_news_reversal_long (docstring and return dropped):

```python
fires = s.get('news_sentiment_5d', 0.0) <= -0.3 and s.get('pct_change_5d', 0.0) < -0.1 and (s.get('news_count_5d', 0) >= 3) and (s.get('news_sentiment_shift', 0.0) > 0.2) and s.get('close_above_open', False) and s.get('close_in_top_40pct_of_range', False)
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

| id | layer | producer / parameter | production | free_band (OFFLINE) | resim_band (RESIM) | status |
|---|---|---|---|---|---|---|
| P1 | PRODUCER | close_above_open - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P1.x) | BANDS-DEFINED |
| P1.1 | BAND | (structural) c > o - optional min body pct - backtest/signals/technical.py bar-anatomy block | 0.0 | none - bar OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET zero; T3 review before any grid |
| P2 | PRODUCER | close_in_top_40pct_of_range - emitted by backtest/signals/screener.py +1; the boolean's UNDERLYING condition is bandable through its producer's internals | leg required True | only where the condition's input magnitudes are persisted on the fires - else none | variants over unpersisted bars/inputs - RESIM; a shared producer's resim runs the FULL OPEN consumer set and its one cube is graded per consumer (11.2s - results reused by construction); knobs DEFINED below (P2.x) | BANDS-DEFINED |
| P2.1 | BAND | range-position cutoff - backtest/signals/technical.py:1682 | 0.4 | none - bar OHLC unpersisted | the whole band; DEFINED-NO-ACTUATOR | BRACKET production 0.40; T3 review before any grid |
| P3 | STRATEGY | news_count_5d `>= 3` [EXISTING-THRESHOLD] | `>= 3` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P4 | STRATEGY | news_sentiment_5d `<= -0.3` [EXISTING-THRESHOLD] | `<= -0.3` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P5 | STRATEGY | news_sentiment_shift `> 0.2` [EXISTING-THRESHOLD] | `> 0.2` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| P6 | STRATEGY | pct_change_5d `< -0.1` [EXISTING-THRESHOLD] | `< -0.1` | measured tighter QUANTS levels - see the free-band section below | looser side - band at R1 | MEASURED-PRE-R1 |
| B-rows | BREADTH | every companion in the B-row candidate census below is Table A inventory once REGISTERED at the T3 band review (11.2b3; B-rows are Table A members by owner ruling) | - | census levels below | sub-floor / unpersisted producers | CANDIDATE |

### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]

Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine
hours). Looser side = RESIM (engine) by construction - a looser level admits
bars the cube never recorded. Levels are QUANTS quantiles [0.2, 0.4, 0.6, 0.8] of the key's values on the surviving fires; only levels
STRICTLY tighter than production enter the free band.

| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |
|---|---|---|---|---|---|
| news_count_5d | backtest/signals/news_sentiment.py +1 | `>= 3` | 100.0% | TIGHTER = RAISE the floor: 12 -> 1 (100%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |
| news_sentiment_5d | backtest/signals/news_sentiment.py +1 | `<= -0.3` | 100.0% | TIGHTER = LOWER the ceiling: -0.5 -> 1 (100%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |
| news_sentiment_shift | backtest/signals/news_sentiment.py +1 | `> 0.2` | 100.0% | TIGHTER = RAISE the floor: 0.2157 -> 1 (100%) | LOOSER = LOWER the threshold: RESIM - band from the SPECS entry (to be built) |
| pct_change_5d | backtest/signals/screener.py | `< -0.1` | 100.0% | TIGHTER = LOWER the ceiling: -0.102 -> 0 (0%) | LOOSER = RAISE the threshold: RESIM - band from the SPECS entry (to be built) |

### B-row candidate census - companion producers persisted on the fires [NEW-GATE]

**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a
companion threshold is an AND-leg the strategy does not currently have -
**no grid runs before the T3 owner band review words the band**. All
companion levels are OFFLINE (subset selection). Coverage floor 0.98
(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as
RESIM-ONLY - offline grading would silently drop their absent rows.

| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |
|---|---|---|---|---|---|---|

### Binary companions (offline AND-able; no band - a boolean has no threshold)

(none with a non-degenerate rate)

### Below the 0.98 coverage floor - RESIM-ONLY

(none)

### Price-denominated keys - EXCLUDED from banding (|Spearman| >= 0.95 vs proxy `bb_20_20_mid`)

A cross-sectional threshold on an absolute price level selects by SHARE
PRICE, not by signal state. Usable only as a RATIO to price - which is
producer work, i.e. RESIM, never an offline band.

`bb_20_20_mid` (1.0)

**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is
invisible to this table and to every offline instrument - genuinely new
breadth producers are an engine-side design act, never an offline sweep.
