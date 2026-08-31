# Producer variant table - institutional_committed_growth_long

**Gate:** `(committed_growth_holders >= 3 OR (committed_growth_holders == 0 AND institutional_increased >= 5)) AND (price_above_ema_200)`

## Section 1 - boolean formula (READ from source, never recalled)

```

=============================== PRODUCER LAYER ===============================
   all six steps below run INSIDE _per_ticker_persistence (one function, one
   pass per ticker per snapshot) and write to the cached parquet under
   data_prefetch/derived/institutional_persistence_t1a/. NONE of their
   constants is persisted into signals_at_entry - only their OUTPUT is - so
   no change to any of them can be graded off an existing cube.

P1  PIT visibility cut     =  keep filings whose ReportPeriod + lag <= as_of
                   PARAMETER: REPORTING_LAG_DAYS = 45
                      decides WHICH filings exist before any count is formed

P2  per-fund quarter panel =  groupby(Fund, report_dt).Shares.sum(), keep > 0
                   PARAMETER: positive-shares floor = 0
                      collapses multi-class entries and drops closed positions

P3  consecutive-quarter chain = walk each fund's quarters back from the latest,
                   extending the chain while the gap stays inside the window
                   PARAMETER: quarterly gap tolerance = 70..100 days
                      a gap outside the window BREAKS the chain

P4  growth-eligible funds  =  funds whose chain length >= N
                   PARAMETER: min_consecutive_quarters = 4

P5  shares N quarters back =  fund's share count at iloc[N-1]
                   PARAMETER: growth_lookback_quarters = 4

P6  grew?(fund)            =  recent_shares > shares_back * multiple
                   PARAMETER: growth_multiple = 1.10

    committed_growth_holders = count of funds passing P4 AND P6

=============================== STRATEGY LAYER ===============================
   both counts below ARE persisted in signals_at_entry (measured 100pct
   coverage), so a threshold over them re-scores off the cached cube.

P7  primary arm            =  committed_growth_holders >= T
                   PARAMETER: min_committed_growth = 3

P8  fallback arm           =  committed_growth_holders == 0
                                AND institutional_increased >= T
                   PARAMETER: fallback_min_increased = 5

P9  regime leg             =  close > EMA(span)
                   PARAMETER: span = 200, from config EMA_PAIRS

fires =  ( P7  OR  P8 )  AND  P9

```

**R5 baseline:** 1941 fires / 464 tickers / holdout n=666 / 2022-05-05..2026-05-05 (`output_r5_merged_1_7`)

## Section 2 - Table A: parameter inventory

| ID | producer | parameter | production | band tested | subset-safe | status | evidence | why this band |
|---|---|---|---|---|---|---|---|---|
| P1 | `_per_ticker_persistence (persistence precompute)` | `REPORTING_LAG_DAYS` | 45 | 45 | FREE: none<br>RESIM: 45 | **NOT-SWEPT-BY-DESIGN** | `build_institutional_persistence_precompute.py:46 + :68` | NEW ROW - absent from the pre-B2467 table entirely, so the #182 denominator read 7 when the inventory is 9. The SEC 13F filing deadline is 45 days after quarter end; this is the PIT guard that keeps a backtest from seeing a filing before it existed. NOT SWEPT: shortening it is lookahead and lengthening it only discards real information. NOT PERSISTED: the cube stores this step's OUTPUT (committed_growth_holders), never its inputs, so the value cannot be recomputed by re-filtering an existing cube. Resim in BOTH directions - monotonicity is irrelevant here, availability is what decides. |
| P2 | `_per_ticker_persistence (persistence precompute)` | `positive_shares_floor` | 0 | 0 | FREE: none<br>RESIM: 0 | **NOT-SWEPT-BY-DESIGN** | `build_institutional_persistence_precompute.py:73-74` | NEW ROW - also absent before. Collapses a fund's multiple share classes into one quarterly position and drops closed positions. NOT SWEPT: a floor above 0 would silently redefine 'holds the stock' mid-chain. NOT PERSISTED: the cube stores this step's OUTPUT (committed_growth_holders), never its inputs, so the value cannot be recomputed by re-filtering an existing cube. Resim in BOTH directions - monotonicity is irrelevant here, availability is what decides. |
| P3 | `_per_ticker_persistence (persistence precompute)` | `quarterly_gap_tolerance_days` | 70..100 | 70..100 | FREE: none<br>RESIM: 70..100 | **NOT-SWEPT-BY-DESIGN** | `build_institutional_persistence_precompute.py:91` | data hygiene against 13F filing jitter, not an edge knob: it decides what counts as a consecutive quarter, and moving it changes chain lengths for reasons unrelated to the thesis. NOT PERSISTED: the cube stores this step's OUTPUT (committed_growth_holders), never its inputs, so the value cannot be recomputed by re-filtering an existing cube. Resim in BOTH directions - monotonicity is irrelevant here, availability is what decides. |
| P4 | `_per_ticker_persistence (persistence precompute)` | `min_consecutive_quarters` | 4 | 2, 3, 4, 6, 8 | FREE: none<br>RESIM: 2, 3, 4, 6, 8 | **UNTESTED** | `build_institutional_persistence_precompute.py:108` | Yan-Zhang 2009 persistence spans multiple quarters but the canonical count varies; 4 is this repo's choice. Band brackets production BOTH ways per B1691. NOT PERSISTED: the cube stores this step's OUTPUT (committed_growth_holders), never its inputs, so the value cannot be recomputed by re-filtering an existing cube. Resim in BOTH directions - monotonicity is irrelevant here, availability is what decides. AND NOTE the fallback: tightening this can drive committed_growth_holders to 0, which switches P8 ON and can ADD fires - so it is not even monotone at the producer level. |
| P5 | `_per_ticker_persistence (persistence precompute)` | `growth_lookback_quarters` | 4 | 2, 3, 4, 6, 8 | FREE: none<br>RESIM: 2, 3, 4, 6, 8 | **UNTESTED** | `build_institutional_persistence_precompute.py:112` | the window P6 measures growth across. COLLINEAR WITH P4 BY CONSTRUCTION - P4 gates which funds reach P5 and both default to 4, so a joint sweep must report their correlation rather than crediting either alone. NOT PERSISTED: the cube stores this step's OUTPUT (committed_growth_holders), never its inputs, so the value cannot be recomputed by re-filtering an existing cube. Resim in BOTH directions - monotonicity is irrelevant here, availability is what decides. |
| P6 | `_per_ticker_persistence (persistence precompute)` | `growth_multiple` | 1.100 | 1.000, 1.100, 1.250, 1.500 | FREE: none<br>RESIM: 1.000, 1.100, 1.250, 1.500 | **UNTESTED** | `build_institutional_persistence_precompute.py:113` | 1.10 = '+10pct over the window'. 1.0 is the meaningful floor (ANY growth) and is included deliberately - it sits below production, and B1691's lesson is that the winning level is often one the old floor excluded. NOT PERSISTED: the cube stores this step's OUTPUT (committed_growth_holders), never its inputs, so the value cannot be recomputed by re-filtering an existing cube. Resim in BOTH directions - monotonicity is irrelevant here, availability is what decides. |
| P7 | `strat_institutional_committed_growth_long` | `min_committed_growth` | 3 | 1, 2, 3, 5, 11, 142 | FREE: 3, 5, 11, 142<br>RESIM: 1, 2 | **UNTESTED** | `screener.py:6648` | PERSISTED, so this row splits PER LEVEL - which the pre-B2467 binary field could not express and which is why the old factorial read 31,500. Raising the bar (5, 11, 142) selects a STRICT SUBSET of rows already in the cube and grades FREE; lowering it (1, 2) admits rows the cube never contains and needs the engine. The fallback does NOT break this: raising the primary threshold leaves committed_growth_holders unchanged, so rows at 0 still take P8 identically and rows at 3-4 simply stop firing. Levels are the measured IS deciles over 1,275 IS rows. |
| P8 | `strat_institutional_committed_growth_long` | `fallback_min_increased` | 5 | 2, 3, 5, 6 | FREE: 5, 6<br>RESIM: 2, 3 | **UNTESTED** | `screener.py:6648` | the B1230 fallback, live wherever the persistence precompute has no row (~4pct of fired rows). PERSISTED, so the same per-level split as P7: raising it only removes fires and grades FREE; 2 and 3 add fires and need resim. Levels are the measured IS deciles of institutional_increased. |
| P9 | `compute_ema_sma` | `span` | 200 | 9, 20, 21, 50, 100, 150, 200 | FREE: none<br>RESIM: 9, 20, 21, 50, 100, 150, 200 | **UNTESTED** | `technical.py:768 + config.py:2496-2497` | SWEEP SCOPE, NOT AVAILABILITY: the band lists every span EMA_PAIRS emits, which is what this column asserts and what the drift verifier checks. Span 21 is listed because the producer offers it, and it should NOT be swept: MEASURED from the b2197 run ledger, that wave ran 21 ONCE at sw20 and omitted it from sw5/sw10/sw30/sw50 - 26 configs, not 30 - so the programme already found it a near-duplicate of 20 that did not earn an engine run. Carry that into the Step-1 design, not into this column. OWNER DIRECTIVE 2026-08-30: 'EMA can not stay as is - EMA span itself may help drive higher sharpe.' NOT subset-safe in EITHER direction and this is MEASURED, not argued (recorded S6-B2427): of 13,440 EMA200-gated family rows, 5,770 sit above the 200 EMA and below the 50, and 1,401 high_conviction rows are the reverse - the legs do not nest, so no span change re-scores off a cube. CHEAP TO VARY, NOT CHEAP TO RUN: EMA_PAIRS is env-driven (config.py:2496-2497, verified) so no code change is needed, but each span still costs one engine run. |

## Section 3 - Table B: combination results

*EMPTY BY CONSTRUCTION.* No combination has been scored for this strategy.

*Generated by `scripts/producer_variant_table.py` - regenerate, do not hand-edit.*