"""Standard producer-variant table - S6-OPT-196 reporting contract (B1506).

ONE repeatable artifact per strategy, so every optimisation run is reported the
same way and results are comparable across strategies. Two tables:

  TABLE A - PARAMETER INVENTORY. Every producer parameter the strategy touches,
            whether it was TESTED, and WHY its band holds those values. This is
            the CHECKLIST #182 denominator made explicit: the verdict must cite
            "N of M producers" and M is the row count of Table A.

  TABLE B - COMBINATION RESULTS. Every combination actually graded, with the
            gates it passed and the gates it failed.

SUBSET-SAFE is the field that decides cost. A parameter that can only REMOVE
fires keeps every variant inside the R5 cube, so it grades for free. One that
can ADD fires needs engine resimulation, because the cube holds no P&L for a
trade R5 never took.

Adding a strategy = adding a SPECS entry. The renderer is strategy-agnostic.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from grid_population import grid_population  # noqa: E402  (B2521 S6-B2520m)

# --------------------------------------------------------------------------
# SPECS - the parameter inventory per strategy. Every value here is READ from
# source; `evidence` cites where. Never populate a row from memory.
# --------------------------------------------------------------------------
SPECS: dict[str, dict] = {
    "smc_breaker_block_long": {
        "gate": "(breaker_bullish) AND (price_above_ema_200)",
        # B2579 (S6-B2573a): the post-config battery's ADAPTER CONTRACT.
        # run_postconfig.run_family reads THIS block and nothing else that is
        # family-specific: which Pids are the manifest's swept knobs and the
        # params key each maps to, the grader / free-level grader / spot
        # checker scripts with the CLI flag per Pid, the grid row keys, and
        # the engine-anchor script. A SPECS entry with no complete `tools`
        # block is NOT a battery family (run_postconfig.family_refusal) and
        # the B2578 launch gate refuses its spec before the engine.
        "tools": {
            "keys": {"P1": "swing", "P6": "span"},
            "grid_keys": ["close_mitigation", "break_pct_max", "age_bars_max", "tail_n"],
            "grade": {"script": "tighten_breaker_block.py", "cube": "trade_exit_detail.csv",
                      "flags": {"P1": "--swing-length", "P6": "--span"},
                      "extra": ["--min-n", "10"], "pythonpath": ".;scripts",
                      "note": "AUTO (B2177)"},
            "free_levels": None,
            "spot_check": {"script": "spot_check_trades.py", "cube": "trade_exit_detail.csv",
                           "flags": {"P1": "--swing-length", "P6": "--ema-span"},
                           "extra": ["--n", "50"], "window": False,
                           "precompute_check": False, "pythonpath": ".",
                           "note": "AUTO (B2177)"},
            "engine_anchors": {"script": "verify_engine_implemented.py"},
            "single_combination": False,
        },
        "formula": """=============================== PRODUCER LAYER ===============================

P1  swings  =  swing_highs_lows( ohlc, swing_length = 20 )
                   -> a bar is a swing high if its high is the highest
                      across swing_length bars BEFORE and AFTER it
                   PARAMETER: swing_length = 20   (library default is 50)

P2  ob_df   =  ob( ohlc, swings, close_mitigation = False )
                   -> emits, per detected block:  OB (+1 bull / -1 bear),
                      Top, Bottom, MitigatedIndex
                   PARAMETER: close_mitigation = False
                      False -> a block counts as mitigated when the HIGH/LOW
                               pierces it
                      True  -> only when the CLOSE pierces it  (stricter)

P3  events  =  ob_df[ OB != 0 ].tail( 20 )
                   PARAMETER: tail N = 20     (hardcoded literal, not an argument)

P4  per event e:   e.is_mitigated = ( MitigatedIndex > 0 )
                                    AND ( MitigatedIndex < today_index )
                   -> no parameter; derived from P2's MitigatedIndex
                   -> MitigatedIndex = the BAR INDEX of the candle that broke
                      through the zone (smc.py:69); 0 means never mitigated.
                      It is an INDEX, not a flag - which is why an ancient block
                      stays eligible forever with no age check (S6-B1500a).

P5  per event e:   e.broken_up    = ( close > e.Top )
                   -> no parameter; strict inequality, zero buffer

P6  ema_50_200 =  compute_ema_sma( df )      # pairs (9,21),(20,50),(50,200)
       price_above_ema_200  =  close > EMA(close, span = 200)
                   PARAMETER: span = 200, emitted only from the (50,200) pair

=============================== STRATEGY LAYER ===============================

breaker_bullish  =  AT LEAST ONE event e in P3 satisfies ALL of:
                        ( e.OB == -1 )          <- bearish block      [from P2]
                        AND ( e.is_mitigated )                        [from P4]
                        AND ( e.broken_up )                           [from P5]

fires            =  ( breaker_bullish )  AND  ( price_above_ema_200 ) [from P6]""",
        # B1575: baseline artifact corrected per L445 - rung4_chunk1 was an
        # abandoned A-C chunk. Fire count is from that defective cube and is
        # NOT comparable to merged_1_7; re-measure before citing it.
        "baseline": {"artifact": "output_r5_merged_1_7", "fires": None,
                     "tickers": 161, "holdout_n": 147,
                     "window": "2022-05-06..2026-05-04"},
        # B1689: this dict is HAND-MAINTAINED and drifted TWICE - P3 still
        # carried the pre-B1611 band [3,5,10,20] after the owner-approved
        # re-band, and engine_implemented stayed False for P2-P5 after B1616
        # implemented them. The AUTHORITIES are: tighten_breaker_block.py
        # constants (P2-P5 bands), technical.py + config.py (P1/P6), and
        # verify_engine_implemented.py (engine status). Cross-check before
        # quoting this table (#202).
        "params": [
            {"id": "P1", "producer": "_smc.swing_highs_lows", "param": "swing_length",
             "env": "SMC_SWING_LENGTH",   # B2578: the knob the engine reads (config.py)
             "consumers": [   # S6-B2573d: measured by knob_consumers, pinned equal
                           "backtest/config.py",
                           "backtest/engine/exit_strategies.py",
                           "backtest/signals/screener.py"],
             "production": 20, "type": "int", "band": [5, 10, 20, 30, 50],
             # B1691 owner directive: swing_length=5 ADDED. The band had ONE level
             # below production and TWO above - built on the hypothesis that higher
             # swing_length = fewer, cleaner swings = less noise. A band shaped by a
             # directional hypothesis can only CONFIRM it. This is the tail_n mistake
             # exactly: that band floored at 3, was re-banded to [1,2,...], and 2 -
             # a level that had not existed - won BOTH wave-1 top-10s.
             "derivation": "library default is 50; production overrides to 20. Band brackets both.",
             "subset_safe": False, "status": "UNTESTED",
             "evidence": "smc.py:137",
             "engine_implemented": True},
            {"id": "P2", "producer": "_smc.ob", "param": "close_mitigation",
             "env": "SMC_OB_CLOSE_MITIGATION",
             "consumers": [   # S6-B2573d: measured by knob_consumers, pinned equal
                           "backtest/config.py",
                           "backtest/engine/exit_strategies.py",
                           "backtest/signals/screener.py"],
             "production": False, "type": "bool", "band": [False, True],
             "derivation": "boolean - both values ARE the band. True = mitigated on CLOSE only.",
             "subset_safe": True, "status": "TESTED",
             "evidence": "smc.py:380",
             "engine_implemented": True},
            {"id": "P3", "producer": "ob_events.tail(N)", "param": "tail_n",
             "env": "SMC_OB_TAIL_N",
             "consumers": [   # S6-B2573d: measured by knob_consumers, pinned equal
                           "backtest/config.py",
                           "backtest/engine/exit_strategies.py",
                           "backtest/signals/screener.py"],
             "production": 20, "type": "int", "band": [1, 2, 3, 5, 10, 20],
             "derivation": "B1610 DEFECT - this text says the band spans the measured "
                           "rank range 1-4, and it does NOT: its floor is 3, the TOP of "
                           "that range. MEASURED on 420 cfg2 fires: levels 3/5/10/20 admit "
                           "39.8/68.8/98.6/100.0pct, so 10->20 moved 0 of 50 cfg1 groups. "
                           "The discriminating region is 1-3 (tail_n=2 alone cuts 73pct). "
                           "Also COLLINEAR with P4 age_bars_max, Spearman +0.881. "
                           "RE-BAND OWNER-APPROVED AND SHIPPED (B1611): band is now 1,2,3,5,10,20. VINDICATED - tail_n=2, a level that did not exist under the old floor, won BOTH wave-1 top-10s.",
             "subset_safe": True, "status": "RE-BANDED-AND-TESTED",
             "evidence": "smc_ict.py:266-268",
             "engine_implemented": True},
            {"id": "P4", "producer": "recency filter on OB age", "param": "age_bars_max",
             "env": "SMC_BREAKER_AGE_BARS_MAX",
             "consumers": [   # S6-B2573d: measured by knob_consumers, pinned equal
                           "backtest/config.py",
                           "backtest/engine/exit_strategies.py",
                           "backtest/signals/screener.py"],
             "production": None, "type": "int|None", "band": [60, 120, 180, 250, None],
             "derivation": "measured real retests 45-134 bars, latches 294-469, gap 134-294 (B1501).",
             "subset_safe": True, "status": "TESTED",
             "evidence": "B1614 CORRECTION - the prior citation "
                         "'smc_ict.py:252 (event_recency_bars)' was WRONG on both "
                         "counts: line 252 is `_smc.ob(ohlc, swings)` which takes no "
                         "such argument, and `event_recency_bars` (line 257) governs "
                         "`smc_ob_bullish_active` - a DIFFERENT signal. The breaker "
                         "loop (273-296) has NO age filter. P4 is a NEW GATE with no "
                         "engine counterpart; see S6-B1612f.",
             "engine_implemented": True},
            {"id": "P5", "producer": "break test (close > top)", "param": "break_pct_max",
             "env": "SMC_BREAKER_BREAK_PCT_MAX",
             "consumers": [   # S6-B2573d: measured by knob_consumers, pinned equal
                           "backtest/config.py",
                           "backtest/engine/exit_strategies.py",
                           "backtest/signals/screener.py"],
             "production": None, "type": "float|None", "band": [0.01, 0.02, 0.03, 0.05, None],
             "derivation": "NEW-GATE, OWNER-APPROVED B1507 (was N/A - production has no such "
                           "parameter; `close > top` is a strict inequality). Band from the "
                           "B1501 measurement: real retests 0.5-2.7pct from the zone, stale "
                           "latches 7.5-60pct, empty gap 3-7pct. Caps at 1/2/3pct bracket the "
                           "retest population; 5pct sits in the gap; None = production. "
                           "Direction is an UPPER bound (L359: a breaker block is a RETEST, so "
                           "CLOSER is stricter).",
             "subset_safe": True, "status": "PENDING",
             "evidence": "smc_ict.py:283-284 (no parameter today)",
             "engine_implemented": True},
            {"id": "P6", "producer": "compute_ema_sma", "param": "span",
             "env": "STRAT_EMA_SPAN",
             "consumers": [   # S6-B2573d: measured by knob_consumers, pinned equal
                           "backtest/config.py",
                           "backtest/engine/exit_strategies.py",
                           "backtest/signals/screener.py"],
             "production": 200, "type": "int", "band": [9, 20, 21, 50, 100, 150, 200],
             "derivation": "ALL spans the producer emits (READ technical.py:750 pairs "
                           "(9,21),(20,50),(50,200)). B1507 widened from [50,200] - the "
                           "earlier band silently dropped 9/20/21 with no stated rule "
                           "(#165). 9/20/21 are short-horizon and weak trend filters "
                           "economically, but exclusion must be a MEASURED result, not a "
                           "pre-judgement. B1686: spans 100 and 150 ADDED to the producer on owner "
                           "directive 2026-08-18 - they did not exist, which is why P6 could "
                           "not sweep them (S6-B1507b). Band is now 7 values; 250 still absent.",
             "subset_safe": False, "status": "UNTESTED",
             "evidence": "technical.py:750"},
        ],
    },
    # S6-B2435 (owner directive 2026-08-30: "lets take this strategy ... create
    # bands and show table A", and "EMA can not stay as is - EMA span itself may
    # help drive higher sharpe"). Every value READ from source; evidence cites
    # the line. The EMA row is P7 and is BANDED, not pinned, on that directive.
    "institutional_committed_growth_long": {
        # B2578 (S6-B2573b): env values an arm may set that are NOT a
        # parameter knob. INST_PERSIST_CACHE_TAG routes the strategy's
        # persistence read to data_prefetch/derived/
        # institutional_persistence_t1a_<tag> (persistence_cache_dir);
        # the tagged precompute is built OUT OF BAND at the arm's P4/P5/P6
        # values and records none of them (S6-B2578a) - the gate can only
        # check the tagged directory exists and holds parquet.
        "env_actuators": {"INST_PERSIST_CACHE_TAG": "persistence precompute tag"},
        # B2579 (S6-B2573d): every file that READS the actuator - measured by
        # knob_consumers and pinned equal (test_b2579).
        "actuator_consumers": {"INST_PERSIST_CACHE_TAG": [
            "scripts/build_institutional_persistence_precompute.py",
            "scripts/prescreen_persistence_configs.py"]},
        # B2579 (S6-B2573a): the battery adapter contract (see the smc entry).
        # `cube: ""` passes the cube DIRECTORY; the institutional grid rows
        # carry one `combo` (single_combination), the free levels have their
        # own reproduction-gated grader, and the spot check takes the
        # manifest window and must record the arm's precompute dir (B2576).
        "tools": {
            "keys": {"P4": "min_consecutive_quarters", "P5": "growth_lookback_quarters",
                     "P6": "growth_multiple", "P9": "ema_span"},
            "grid_keys": ["combo"],
            "grade": {"script": "grade_institutional_config.py", "cube": "",
                      "flags": {"P4": "--min-consecutive-quarters",
                                "P5": "--growth-lookback-quarters",
                                "P6": "--growth-multiple", "P9": "--span"},
                      "extra": ["--min-n", "10"], "pythonpath": None,
                      # B2612: the battery TELLS this grader the step (its
                      # holdout read is by declaration) and hands it the spec
                      # arm's pre-registered exit to record beside its own
                      # selection; tighten_breaker_block has neither flag.
                      "step2_flag": "--step2",
                      "preregistered_flag": "--preregistered-exit",
                      "note": "AUTO (B2520/B2569/B2612)"},
            "free_levels": {"script": "grade_free_levels_institutional.py"},
            "spot_check": {"script": "spot_check_institutional.py", "cube": "",
                           "flags": {"P9": "--ema-span"}, "extra": ["--n", "50"],
                           "window": True, "precompute_check": True,
                           "pythonpath": None, "note": "AUTO (B2520)"},
            "engine_anchors": {"script": None},
            "single_combination": True,
        },
        # S6-B2465: MEASURED from output_r5_merged_1_7/trade_log.csv,
        # not recalled. holdout_n 666 and is_n 1275 reproduce S6-B2435
        # and the B2419 pre-registration exactly.
        "baseline": {"artifact": "output_r5_merged_1_7", "fires": 1941,
                     "tickers": 464, "holdout_n": 666,
                     "window": "2022-05-05..2026-05-05"},
        "gate": "(committed_growth_holders >= 3 OR (committed_growth_holders == 0 AND institutional_increased >= 5)) AND (price_above_ema_200)",
        "formula": """
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
   both counts below ARE persisted in signals_at_entry - measured S6-B2504:
   96.2pct of this strategy's 1,941 fired rows carry the committed key; the
   3.8pct without it are B1230 no-artifact-row fallback fires where the
   engine's s.get read 0 (an earlier revision said "100pct coverage", which
   was true of the counts' presence as FIELDS but not of every fired row).
   A threshold over them re-scores off the cached cube, defaulting absent
   keys to 0 exactly as the engine did.

P7  primary arm            =  committed_growth_holders >= T
                   PARAMETER: min_committed_growth = 3

P8  fallback arm           =  committed_growth_holders == 0
                                AND institutional_increased >= T
                   PARAMETER: fallback_min_increased = 5

P9  regime leg             =  close > EMA(span)
                   PARAMETER: span = 200, from config EMA_PAIRS

fires =  ( P7  OR  P8 )  AND  P9
""",
        "params": [
            {"id": "P1", "producer": "_per_ticker_persistence (persistence precompute)",
             "param": "REPORTING_LAG_DAYS", "production": 45, "sweep_levels": [],
             "band": [45],
             "free_band": [], "resim_band": [45],
             "subset_safe": False, "status": "NOT-SWEPT-BY-DESIGN",
             "evidence": "build_institutional_persistence_precompute.py:46 + :68",
             "type": "int", "engine_implemented": True,
             "derivation": "NEW ROW - absent from the pre-B2467 table entirely, so the #182 denominator read 7 when the inventory is 9. The SEC 13F filing deadline is 45 days after quarter end; this is the PIT guard that keeps a backtest from seeing a filing before it existed. NOT SWEPT: shortening it is lookahead and lengthening it only discards real information. NOT PERSISTED: the cube stores this step's OUTPUT (committed_growth_holders), never its inputs, so the value cannot be recomputed by re-filtering an existing cube. Resim in BOTH directions - monotonicity is irrelevant here, availability is what decides."},
            {"id": "P2", "producer": "_per_ticker_persistence (persistence precompute)",
             "param": "positive_shares_floor", "production": 0, "sweep_levels": [],
             "band": [0],
             "free_band": [], "resim_band": [0],
             "subset_safe": False, "status": "NOT-SWEPT-BY-DESIGN",
             "evidence": "build_institutional_persistence_precompute.py:73-74",
             "type": "int", "engine_implemented": True,
             "derivation": "NEW ROW - also absent before. Collapses a fund's multiple share classes into one quarterly position and drops closed positions. NOT SWEPT: a floor above 0 would silently redefine 'holds the stock' mid-chain. NOT PERSISTED: the cube stores this step's OUTPUT (committed_growth_holders), never its inputs, so the value cannot be recomputed by re-filtering an existing cube. Resim in BOTH directions - monotonicity is irrelevant here, availability is what decides."},
            {"id": "P3", "producer": "_per_ticker_persistence (persistence precompute)",
             "param": "quarterly_gap_tolerance_days", "production": "70..100", "sweep_levels": [],
             "band": ["70..100"],
             "free_band": [], "resim_band": ["70..100"],
             "subset_safe": False, "status": "NOT-SWEPT-BY-DESIGN",
             "evidence": "build_institutional_persistence_precompute.py:91",
             "type": "int", "engine_implemented": True,
             "derivation": "data hygiene against 13F filing jitter, not an edge knob: it decides what counts as a consecutive quarter, and moving it changes chain lengths for reasons unrelated to the thesis. NOT PERSISTED: the cube stores this step's OUTPUT (committed_growth_holders), never its inputs, so the value cannot be recomputed by re-filtering an existing cube. Resim in BOTH directions - monotonicity is irrelevant here, availability is what decides."},
            {"id": "P4", "producer": "_per_ticker_persistence (persistence precompute)",
             "param": "min_consecutive_quarters", "production": 4, "sweep_levels": [2, 3, 6, 8],
             "env": "INST_MIN_CONSECUTIVE_QUARTERS",   # read at precompute build time
             "consumers": [   # S6-B2573d: measured by knob_consumers, pinned equal
                           "scripts/build_institutional_persistence_precompute.py"],
             "band": [2, 3, 4, 6, 8],
             "free_band": [], "resim_band": [2, 3, 4, 6, 8],
             "subset_safe": False, "status": "UNTESTED",
             "evidence": "build_institutional_persistence_precompute.py:108",
             "type": "int", "engine_implemented": True,
             "derivation": "Yan-Zhang 2009 persistence spans multiple quarters but the canonical count varies; 4 is this repo's choice. Band brackets production BOTH ways per B1691. NOT PERSISTED: the cube stores this step's OUTPUT (committed_growth_holders), never its inputs, so the value cannot be recomputed by re-filtering an existing cube. Resim in BOTH directions - monotonicity is irrelevant here, availability is what decides. AND NOTE the fallback: tightening this can drive committed_growth_holders to 0, which switches P8 ON and can ADD fires - so it is not even monotone at the producer level."},
            {"id": "P5", "producer": "_per_ticker_persistence (persistence precompute)",
             "param": "growth_lookback_quarters", "production": 4, "sweep_levels": [2, 3, 6, 8],
             "env": "INST_GROWTH_LOOKBACK_QUARTERS",
             "consumers": [   # S6-B2573d: measured by knob_consumers, pinned equal
                           "scripts/build_institutional_persistence_precompute.py"],
             "band": [2, 3, 4, 6, 8],
             "free_band": [], "resim_band": [2, 3, 4, 6, 8],
             "subset_safe": False, "status": "UNTESTED",
             "evidence": "build_institutional_persistence_precompute.py:112",
             "type": "int", "engine_implemented": True,
             "derivation": "the window P6 measures growth across. COLLINEAR WITH P4 BY CONSTRUCTION - P4 gates which funds reach P5 and both default to 4, so a joint sweep must report their correlation rather than crediting either alone. NOT PERSISTED: the cube stores this step's OUTPUT (committed_growth_holders), never its inputs, so the value cannot be recomputed by re-filtering an existing cube. Resim in BOTH directions - monotonicity is irrelevant here, availability is what decides."},
            {"id": "P6", "producer": "_per_ticker_persistence (persistence precompute)",
             "param": "growth_multiple", "production": 1.100, "sweep_levels": [1.0, 1.25, 1.5],
             "env": "INST_GROWTH_MULTIPLE",
             "consumers": [   # S6-B2573d: measured by knob_consumers, pinned equal
                           "scripts/build_institutional_persistence_precompute.py"],
             "band": [1.0, 1.1, 1.25, 1.5],
             "free_band": [], "resim_band": [1.0, 1.1, 1.25, 1.5],
             "subset_safe": False, "status": "UNTESTED",
             "evidence": "build_institutional_persistence_precompute.py:113",
             "type": "int", "engine_implemented": True,
             "derivation": "1.10 = '+10pct over the window'. 1.0 is the meaningful floor (ANY growth) and is included deliberately - it sits below production, and B1691's lesson is that the winning level is often one the old floor excluded. NOT PERSISTED: the cube stores this step's OUTPUT (committed_growth_holders), never its inputs, so the value cannot be recomputed by re-filtering an existing cube. Resim in BOTH directions - monotonicity is irrelevant here, availability is what decides."},
            {"id": "P7", "producer": "strat_institutional_committed_growth_long",
             "param": "min_committed_growth", "production": 3, "sweep_levels": [],
             # S6-B2569a STRIKE (owner-approved 2026-09-03, B2578): resim
             # levels 1 and 2 REMOVED. The threshold is the literal
             # `n_grow >= 3` at screener.py:6648 with NO env knob, so the
             # looser levels were scheduled with no mechanism (L752 class:
             # scheduled-with-mechanism or struck). NOT-MEASURED-BY-DESIGN
             # until a knob exists; the free (tighter) levels grade on every
             # landing (step2_free_levels).
             "band": [3, 5, 11, 14],
             "free_band": [3, 5, 11, 14], "resim_band": [],
             "subset_safe": None, "status": "UNTESTED",
             "evidence": "screener.py:6648",
             "type": "int", "engine_implemented": True,
             "derivation": "PERSISTED, so this row splits PER LEVEL - which the pre-B2467 binary field could not express and which is why the old factorial read 31,500. Raising the bar (5, 11, 14) selects a STRICT SUBSET of rows already in the cube and grades FREE; lowering it (1, 2) would admit rows the cube never contains and need the engine - and the engine has no knob for it, so those two levels were STRUCK at B2578 (S6-B2569a). The fallback does NOT break this: raising the primary threshold leaves committed_growth_holders unchanged, so rows at 0 still take P8 identically and rows at 3-4 simply stop firing. Levels are the measured IS deciles over 1,275 IS rows."},
            {"id": "P8", "producer": "strat_institutional_committed_growth_long",
             "param": "fallback_min_increased", "production": 5, "sweep_levels": [],
             # S6-B2569a STRIKE (B2578): resim levels 2 and 3 REMOVED - the
             # literal `n_incr >= 5` at screener.py:6648 has no env knob.
             "band": [5, 6],
             "free_band": [5, 6], "resim_band": [],
             "subset_safe": None, "status": "UNTESTED",
             "evidence": "screener.py:6648",
             "type": "int", "engine_implemented": True,
             "derivation": "the B1230 fallback, live wherever the persistence precompute has no row (~4pct of fired rows). PERSISTED, so the same per-level split as P7: raising it only removes fires and grades FREE; 2 and 3 would add fires and need resim - no knob exists, STRUCK at B2578 (S6-B2569a). Levels are the measured IS deciles of institutional_increased."},
            {"id": "P9", "producer": "compute_ema_sma",
             "param": "span", "production": 200, "sweep_levels": [9, 20, 50, 100, 150],
             "env": "STRAT_EMA_SPAN",
             "consumers": [   # S6-B2573d: measured by knob_consumers, pinned equal
                           "backtest/config.py",
                           "backtest/engine/exit_strategies.py",
                           "backtest/signals/screener.py"],
             "band": [9, 20, 50, 100, 150, 200],
             "free_band": [], "resim_band": [9, 20, 50, 100, 150, 200],
             "subset_safe": False, "status": "UNTESTED",
             "evidence": "technical.py:768 + config.py:2496-2497",
             "type": "int", "engine_implemented": True,
             "derivation": "SWEEP-CONSIDERED SET, NOT FULL AVAILABILITY (S6-B2498 corrects this sentence: an earlier revision claimed the band 'lists every span EMA_PAIRS emits' while deliberately excluding 21 - availability and sweep scope are DIFFERENT claims, the L728 overloaded-field defect in prose, and this column carries SWEEP SCOPE). EMA_PAIRS emits spans {9, 21, 20, 50, 100, 150, 200} (config.py:2496-2497 default '9:21,20:50,50:200,100:150'); the band EXCLUDES 21 per owner directive 2026-08-31: MEASURED from the b2197 run ledger, that wave ran 21 ONCE at sw20 and omitted it from sw5/sw10/sw30/sw50 - 26 configs, not 30 - a near-duplicate of 20 that did not earn an engine run. OWNER DIRECTIVE 2026-08-30: 'EMA can not stay as is - EMA span itself may help drive higher sharpe.' NOT subset-safe in EITHER direction and this is MEASURED, not argued (recorded S6-B2427): of 13,440 EMA200-gated family rows, 5,770 sit above the 200 EMA and below the 50, and 1,401 high_conviction rows are the reverse - the legs do not nest, so no span change re-scores off a cube. CHEAP TO VARY, NOT CHEAP TO RUN: EMA_PAIRS is env-driven (config.py:2496-2497, verified) so no code change is needed, but each span still costs one engine run."},
        ],
    },
}

GATE_ORDER = ("pooled_sharpe", "profit_factor", "sortino", "psr",
              "min_trades_holdout", "min_trades_full_period")


def validate_spec(spec: dict) -> list[str]:
    """Formula and Table A must not drift apart. Every P-id in the formula needs
    a params row and every params row needs a formula step - a mechanical check,
    because a hand-maintained pair of views silently diverges (L368 class)."""
    import re as _re
    ids_formula = set(_re.findall(r"^(P\d+)\s", spec.get("formula", ""), _re.M))
    ids_params = {p["id"] for p in spec["params"]}
    errs = []
    for i in sorted(ids_formula - ids_params):
        errs.append(f"{i} appears in the formula but has no Table A row")
    for i in sorted(ids_params - ids_formula):
        errs.append(f"{i} has a Table A row but no formula step")
    if not spec.get("formula"):
        errs.append("SPEC has no `formula` - it is REQUIRED (B1510 standard)")
    # S6-B2465: validate_spec returned CLEAN for a spec with no `baseline`,
    # which main() dereferences unconditionally - so the standard 3-section
    # path CRASHED on a spec this function had just approved. A validator
    # that passes an input its own caller cannot consume is not validating.
    # S6-B2467: a per-level split must PARTITION the band - no level may be
    # missing and none may be claimed both free and needing resim.
    for _p in spec["params"]:
        if _p.get("free_band") is None and _p.get("resim_band") is None:
            continue
        _fr = list(_p.get("free_band") or [])
        _rs = list(_p.get("resim_band") or [])
        _band = list(_p["band"])
        if sorted(map(str, _fr + _rs)) != sorted(map(str, _band)):
            errs.append(f"{_p['id']}: free_band + resim_band must partition "
                        f"band exactly (got {_fr} + {_rs} vs {_band})")
        if set(map(str, _fr)) & set(map(str, _rs)):
            errs.append(f"{_p['id']}: a level is in BOTH free_band and "
                        "resim_band")
    # S6-B2474: a scheduled sweep level must EXIST in the band, and must not
    # repeat production - the OAT baseline already covers production, so a
    # duplicate there would silently inflate the config count.
    for _p in spec["params"]:
        _sl = _p.get("sweep_levels")
        if _sl is None:
            continue
        _extra = [x for x in _sl if str(x) not in [str(y) for y in _p["band"]]]
        if _extra:
            errs.append(f"{_p['id']}: sweep_levels {_extra} are not in band")
        if any(str(x) == str(_p["production"]) for x in _sl):
            errs.append(f"{_p['id']}: sweep_levels repeats production "
                        "- the OAT baseline already covers it")
    # B2578 (S6-B2573b / S6-B2569a class): a resim level other than
    # production is a promise to run the engine at that value. Without a
    # declared env knob nothing can honour it - the P7/P8 defect that sat
    # in this table for 11 configs. Fail CLOSED here so the launch gate
    # and Table A read the same rule.
    for _p in spec["params"]:
        _extra = [x for x in (_p.get("resim_band") or [])
                  if str(x) != str(_p.get("production"))]
        if _extra and not _p.get("env"):
            errs.append(f"{_p['id']} {_p['param']}: resim levels {_extra} "
                        "have no env knob - unrunnable by design "
                        "(S6-B2569a class): strike them or add the knob")
    b = spec.get("baseline")
    if not isinstance(b, dict):
        errs.append("SPEC has no `baseline` block - main() reads it for the "
                    "R5 baseline line and will raise KeyError")
    else:
        for _f in ("artifact", "tickers", "holdout_n", "window"):
            if _f not in b:
                errs.append("SPEC baseline missing %r - main() reads it" % _f)
    return errs


# --------------------------------------------------------------------------
# B2578 (S6-B2573b): the LAUNCH GATE. Before B2578 nothing between a spec file
# and the engine asked whether the strategy was registered anywhere or whether
# the env values an arm set were knobs the engine reads - four institutional
# configs landed ungraded pre-B2520 and the P7/P8 resim levels sat unrunnable
# for 11 configs. Everything here fails CLOSED (L642): an absent entry, an
# unreadable registry, an undeclared env key or an off-band level is a refusal.
# Called by run_wave.main BEFORE any arm runs and by prelaunch_gate.check for
# every LOCAL manifest (so the around-the-gate launch_sweep route refuses too).
# --------------------------------------------------------------------------
KNOB_READERS = ("backtest/config.py",
                "scripts/build_institutional_persistence_precompute.py")


def strategies_of(doc: dict, root: Path) -> list[str]:
    """The strategies a spec/manifest runs: one per non-comment line of its
    strategy_subset file (the launcher passes that file to the engine)."""
    rel = doc.get("strategy_subset")
    if not rel:
        return []
    p = root / str(rel)
    if not p.exists():
        return []
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]


def knob_is_read(knob: str, root: Path) -> bool:
    """A knob is PROVEN when a reader module literally reads it from the
    environment - the same code-presence shape verify_engine_implemented uses
    for engine anchors. A typo'd knob (SMC_SWING_LEN) proves nothing. The
    read may wrap (config.py:2511 `os.environ.get(<newline> "SMC_OB_..."`),
    so the match is whitespace-tolerant - measured at B2578 when the literal
    needle refused a knob the engine does read."""
    import re as _re
    pat = _re.compile(r'environ\.get\(\s*"' + _re.escape(knob) + '"')
    for rel in KNOB_READERS:
        try:
            if pat.search((root / rel).read_text(encoding="utf-8")):
                return True
        except OSError:
            continue
    return False


CODE_ROOT = Path(__file__).resolve().parents[1]
_CODE_TOKENS: dict = {}
# B2579c (#122): files the tokenizer could not read. NOT the same as 'no mention'
# - an unreadable file makes a knob's blast radius UNKNOWN, so the launch gate
# refuses while this is non-empty. path -> the exception that stopped it.
_UNMEASURABLE: dict[str, str] = {}


def _code_tokens(path: Path) -> tuple[set, list]:
    """(NAME tokens, code STRING tokens) of a module, cached on (size, mtime).
    A STRING that opens a logical line (a docstring, a bare string statement)
    is NOT code: a docstring naming a knob consumes nothing. Comments are
    COMMENT tokens and never counted."""
    import io as _io
    import tokenize as _tk
    try:
        st = path.stat()
    except OSError:
        return set(), []
    key = (str(path), st.st_size, st.st_mtime_ns)
    if key in _CODE_TOKENS:
        return _CODE_TOKENS[key]
    names, strings = set(), []
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        prev = None
        for tok in _tk.generate_tokens(_io.StringIO(src).readline):
            if tok.type == _tk.NAME:
                names.add(tok.string)
            elif tok.type == _tk.STRING:
                if prev not in (None, _tk.NEWLINE, _tk.NL, _tk.INDENT, _tk.DEDENT,
                                _tk.ENCODING):
                    strings.append(tok.string)
            if tok.type not in (_tk.NL, _tk.COMMENT):
                prev = tok.type
    except (SyntaxError, _tk.TokenError, UnicodeDecodeError) as _exc:
        # #122: never a silent swallow. Partial tokens would read as "this file
        # does not mention the knob", which under-states the blast radius in
        # the direction that lets a launch through - so record it and let
        # launch_refusals fail CLOSED (L642).
        _UNMEASURABLE[str(path)] = f"{type(_exc).__name__}: {_exc}"
        print(f"[knob_consumers] UNMEASURABLE {path}: {type(_exc).__name__}",
              file=_sys.stderr)
    _CODE_TOKENS[key] = (names, strings)
    return names, strings


_ENV_READS: dict[str, frozenset] = {}


def _env_reads(path: Path) -> frozenset:
    """Every LITERAL environment key a script reads, via the AST.

    B2579b: this was a regex over the file's text, and knob_consumers' own
    docstring - which names `environ.get("SMC_SWING_LENGTH")` as the example -
    made producer_variant_table.py report itself as a consumer of that knob
    (L748: the better the comment, the more reliably it poisons a text match).
    The AST sees `os.environ.get(K)`, `environ[K]`, `.pop(K)`, `.setdefault(K)`
    and `os.getenv(K)`, and cannot see prose. A file that will not parse
    contributes nothing (it cannot be a consumer of anything).
    """
    key = str(path)
    if key in _ENV_READS:
        return _ENV_READS[key]
    import ast as _ast

    def _is_environ(node) -> bool:
        return ((isinstance(node, _ast.Name) and node.id == "environ")
                or (isinstance(node, _ast.Attribute) and node.attr == "environ"))

    found: set = set()
    try:
        tree = _ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError):
        _ENV_READS[key] = frozenset()
        return _ENV_READS[key]
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Call):
            f = node.func
            named = (isinstance(f, _ast.Attribute)
                     and f.attr in ("get", "pop", "setdefault")
                     and _is_environ(f.value))
            getenv = ((isinstance(f, _ast.Attribute) and f.attr == "getenv")
                      or (isinstance(f, _ast.Name) and f.id == "getenv"))
            if (named or getenv) and node.args:
                a = node.args[0]
                if isinstance(a, _ast.Constant) and isinstance(a.value, str):
                    found.add(a.value)
        elif isinstance(node, _ast.Subscript) and _is_environ(node.value):
            sl = node.slice
            if isinstance(sl, _ast.Constant) and isinstance(sl.value, str):
                found.add(sl.value)
    _ENV_READS[key] = frozenset(found)
    return _ENV_READS[key]


_CONSUMERS: dict[tuple, list[str]] = {}


def knob_consumers(knob: str, code_root: Path | None = None) -> list[str]:
    """B2579 (S6-B2573d): every file that CONSUMES an env knob - the blast
    radius of setting it in an arm. MEASURED, never recalled:
      * under backtest/ (engine; tests excluded): a code mention - the knob
        as a NAME (`_cfg.STRAT_EMA_SPAN`) or inside a code STRING
        (`environ.get("SMC_SWING_LENGTH")`, `getattr(_c, "STRAT_EMA_SPAN")`);
      * under scripts/: an ENVIRON access of the knob in CODE, read from the
        AST by `_env_reads` (`os.environ.get(K)`, `environ[K]`, `.pop(K)`,
        `.setdefault(K)`, `os.getenv(K)`) - launch and grade tooling passes
        knob names around as strings without consuming them, so a string
        mention there is not a read, and neither is this docstring.
    Paths are repo-relative with forward slashes, sorted. Memoised per
    (knob, root): MEASURED 2026-09-03, an uncached call costs ~0.27 s once the
    backtest token cache is warm (the scripts/ regex re-reads ~80 files), and
    the launch gate asks for every knob of every strategy in a spec - 61 live
    specs took over 2 minutes to check. A process that patches the tree and
    re-measures in the same run must clear `_CONSUMERS`."""
    root = Path(code_root) if code_root is not None else CODE_ROOT
    ck = (knob, str(root))
    if ck in _CONSUMERS:
        return list(_CONSUMERS[ck])
    out = []
    for p in sorted((root / "backtest").rglob("*.py")):
        if "tests" in p.parts:
            continue
        names, strings = _code_tokens(p)
        if knob in names or any(knob in s for s in strings):
            out.append(p)
    for p in sorted((root / "scripts").glob("*.py")):
        if knob in _env_reads(p):
            out.append(p)
    _CONSUMERS[ck] = sorted(
        str(p.relative_to(root)).replace("\\", "/") for p in out)
    return list(_CONSUMERS[ck])


def declared_consumers(spec: dict, knob: str) -> list[str] | None:
    """The consumer list the SPECS entry declares for `knob` (a param's
    `consumers` or an actuator's `actuator_consumers`), or None when the
    entry declares the knob without a list."""
    for p in spec.get("params") or []:
        if p.get("env") == knob:
            return sorted(p.get("consumers") or []) if "consumers" in p else None
    ac = spec.get("actuator_consumers") or {}
    if knob in (spec.get("env_actuators") or {}):
        return sorted(ac[knob]) if knob in ac else None
    return None


def _battery_families() -> tuple[set | None, str]:
    """The post-config battery's registry (run_postconfig.FAMILIES - since
    B2579 derived from the SPECS `tools` adapter contract). Imported, never
    retyped; an import failure is reported, not swallowed."""
    try:
        import run_postconfig as _rp
        return set(_rp.FAMILIES), ""
    except Exception as exc:                       # noqa: BLE001 - report ANY
        return None, f"{type(exc).__name__}: {exc}"


def _level_in_band(value, row: dict) -> bool:
    """Does an env/arm value name a level of the row's band? Env values are
    strings: '1'/'0' for bools, '' for None, '1.25' for floats."""
    t = str(row.get("type", ""))
    band = list(row.get("band") or [])
    s = str(value).strip()
    if t.startswith("bool"):
        low = s.lower()
        if low in ("1", "true"):
            return True in band
        if low in ("0", "false"):
            return False in band
        return False    # "2" names no bool level (the engine reads == "1")
    if s == "" or s.lower() == "none":
        return None in band
    for b in band:
        if b is None:
            continue
        try:
            if float(b) == float(s):
                return True
        except (TypeError, ValueError):
            if str(b) == s:
                return True
    return False


def launch_refusals(doc: dict, root: Path | None = None,
                    require_subset: bool = True) -> list[str]:
    """Reasons NOT to launch `doc` (a wave spec or a run manifest - both carry
    strategy_subset + arms). Empty list = launch. Every reason names the
    class it refuses under so the HALT record reads without this file open.

    require_subset: a wave spec (run_wave) is a Step-1 config by construction
    and MUST name its strategy. A LOCAL manifest without one is a full-roster
    run (the B1488 shape) - nothing here to gate unless it also sets arms,
    in which case the arms have no strategy to be checked against."""
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    rel = doc.get("strategy_subset")
    if not rel:
        if require_subset or doc.get("arms"):
            return ["spec/manifest carries no strategy_subset - the gate cannot "
                    "tell which strategy the run is for (fail CLOSED, L642)"]
        return []
    if not (root / str(rel)).exists():
        # B2578 addendum: the field has historically been used as free text in
        # hand-written manifests - MEASURED 2026-09-03, six pre-B2118 ones read
        # "output_audit/_subset_one.txt (smc_breaker_block_long)" and
        # output_b2099_iso2's is prose only. A path field that is sometimes
        # prose cannot be checked, so the annotated form is refused (L642) with
        # the diagnostic rather than silently parsed. Every LIVE manifest
        # run_wave writes carries a bare path.
        head = str(rel).split(" (")[0].strip()
        why = ("" if head == str(rel) or not (root / head).exists() else
               f" - the field carries a parenthetical annotation and must be a "
               f"BARE path ({head} exists); pre-B2118 hand-written manifests use "
               "the annotated form and are refused deliberately")
        return [f"strategy_subset {rel} does not exist under {root}{why}"]
    strats = strategies_of(doc, root)
    if not strats:
        return [f"strategy_subset {rel} lists no strategy"]
    fams, why = _battery_families()
    errs: list[str] = []
    for s in strats:
        spec = SPECS.get(s)
        if spec is None:
            errs.append(f"{s}: no SPECS entry in producer_variant_table - the "
                        "post-config battery would FAIL closed at landing AFTER "
                        "the engine spend (S6-B2573b; fail CLOSED at launch)")
            continue
        if fams is None:
            errs.append(f"{s}: the battery registry could not be read ({why}) "
                        "- refusing rather than guessing (L642)")
        elif s not in fams:
            errs.append(f"{s}: has a SPECS entry but is NOT a registered "
                        "post-config battery family (run_postconfig.FAMILIES) - "
                        "the landing would FAIL closed (S6-B2573b)")
        errs += [f"{s}: {e}" for e in validate_spec(spec)]
        knobs = {p["env"]: p for p in spec["params"] if p.get("env")}
        for k in knobs:
            if not knob_is_read(k, root):
                errs.append(f"{s}: declared knob {k} ({knobs[k]['id']} "
                            f"{knobs[k]['param']}) is read by none of "
                            f"{KNOB_READERS} - a knob the engine never reads "
                            "makes the manifest lie (S6-B2136 class)")
        actuators = dict(spec.get("env_actuators") or {})
        # B2579 (S6-B2573d): the declared blast radius must equal the tree's.
        # Measured against THIS repo's code (CODE_ROOT) - `root` is where the
        # spec's files live, which a test may relocate; the code tree is not.
        for k in list(knobs) + list(actuators):
            dec = declared_consumers(spec, k)
            got = knob_consumers(k)
            if dec is None:
                errs.append(f"{s}: knob {k} declares no `consumers` list - its "
                            "blast radius is unknown (S6-B2573d; the tree reads "
                            f"it in {got})")
            elif dec != got:
                errs.append(f"{s}: knob {k} consumer DRIFT - SPECS declares "
                            f"{dec} but the tree reads it in {got} (S6-B2573d; "
                            "re-measure with knob_consumers and update the entry)")
        by_param = {p["param"]: p for p in spec["params"]}
        for arm in (doc.get("arms") or []):
            tag = arm.get("tag", "?")
            for k, v in dict(arm.get("env") or {}).items():
                if k in knobs:
                    if not _level_in_band(v, knobs[k]):
                        errs.append(f"{s}: arm '{tag}' sets {k}={v!r} but that is "
                                    f"not a level of {knobs[k]['id']} "
                                    f"{knobs[k]['param']} band "
                                    f"{knobs[k]['band']} - the cube would be "
                                    "graded under a label Table A does not carry")
                elif k in actuators:
                    if k == "INST_PERSIST_CACHE_TAG":
                        from build_institutional_persistence_precompute import (
                            persistence_cache_dir)
                        d = Path(persistence_cache_dir(root, str(v)))
                        n = len(list(d.glob("*.parquet"))) if d.is_dir() else 0
                        if n == 0:
                            errs.append(f"{s}: arm '{tag}' routes the persistence "
                                        f"read to {d} via {k}={v!r} but that "
                                        "directory holds no parquet - the engine "
                                        "would run on nothing (S6-B2484 class)")
                else:
                    errs.append(f"{s}: arm '{tag}' sets {k}={v!r}, which the SPECS "
                                "entry declares neither as a param knob nor as an "
                                "actuator - an undeclared env value is the "
                                "S6-B2573d blast-radius class; declare it or drop it")
            for pk, pv in arm.items():
                row = by_param.get(pk)
                if row is None or pk in ("tag", "env", "note"):
                    continue
                if not _level_in_band(pv, row):
                    errs.append(f"{s}: arm '{tag}' declares {pk}={pv!r} but that is "
                                f"not a level of {row['id']} band {row['band']}")
    if _UNMEASURABLE:
        errs.append("knob blast radius is UNMEASURABLE - the tokenizer could not "
                    "read " + ", ".join(f"{k} ({v})" for k, v in
                                        sorted(_UNMEASURABLE.items()))
                    + " (S6-B2573d): a file that will not parse reads as 'does "
                      "not use this knob', so fix the file or the measurement "
                      "rather than launch on a partial radius")
    return errs


def _fmt(v) -> str:
    if v is None:
        return "none"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def table_a(spec: dict) -> list[str]:
    # S6-B2465: `evidence` is a REQUIRED Table A field under CHECKLIST #183;
    # it was carried on every params row and asserted by test_b1510 IN THE
    # SPEC - never in the RENDERED table, so the owner-locked standard has
    # shipped a column short since it landed.
    rows = ["| ID | producer | parameter | production | band tested | subset-safe | status | sweep (OAT) | evidence | why this band |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for p in spec["params"]:
        band = ", ".join(_fmt(b) for b in p["band"]) or "-"
        # S6-B2467: subset-safety is PER LEVEL, not per parameter. The binary
        # field forced 'raise the bar = free' and 'lower the bar = resim' into
        # ONE flag, which rounded to resim and inflated the factorial. A row may
        # now carry free_band/resim_band; the binary remains the fallback.
        if p.get("free_band") is not None or p.get("resim_band") is not None:
            _f = ", ".join(_fmt(b) for b in (p.get("free_band") or [])) or "none"
            _r = ", ".join(_fmt(b) for b in (p.get("resim_band") or [])) or "none"
            ss = f"FREE: {_f}<br>RESIM: {_r}"
        else:
            ss = {True: "YES - cube-gradable, free",
                  False: "NO - needs engine resim",
                  None: "-"}[p["subset_safe"]]
        # S6-B2474 (owner ruling 2026-08-31: '17 is the feasible design'): the
        # SWEEP column carries the SCHEDULED one-at-a-time design. `band` stays
        # what the producer OFFERS - the contract verify_describing_artifacts
        # checks - so the two claims never collide again (S6-B2472).
        _swl = p.get("sweep_levels")
        if _swl is None:
            _sw = "-"
        elif not _swl:
            _sw = "**0 configs** - not swept"
        else:
            _sw = "**%d configs**: %s" % (len(_swl),
                                          ", ".join(_fmt(b) for b in _swl))
        rows.append(f"| {p['id']} | `{p['producer']}` | `{p['param']}` | "
                    f"{_fmt(p['production'])} | {band} | {ss} | **{p['status']}** | "
                    f"{_sw} | `{p['evidence']}` | {p['derivation']} |")
    return rows


def _measured_fmt(value):
    """B1899 (L580): one carrier for "this was never measured".

    Learned at B1889b when a renderer crashed on None, then broken at B1898
    when THIS renderer printed `0` for an unrecorded value. L536 - a rule
    learned on one site does not travel unless something carries it.
    """
    import importlib.util
    import pathlib as _p

    spec = importlib.util.spec_from_file_location(
        "measured_pvt", _p.Path(__file__).resolve().parent / "measured.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.fmt(value)


# B2137: the P-id <-> parameter-name map, from the SPEC inventory (Table A).
P_AXES = (("P1", "swing_length"), ("P2", "close_mitigation"), ("P3", "tail_n"),
          ("P4", "age_bars_max"), ("P5", "break_pct_max"), ("P6", "span"))
AXIS_KEYS = tuple(nm for _, nm in P_AXES)


def _band_key(x: str):
    """Order band values NUMERICALLY, with None last and booleans False<True.

    ONE definition, used by both the in-row P1-P6 column and the
    Parameters-tested block - two sorts of the same values diverge the moment
    someone edits one (L593).
    """
    if x == "None":
        return (2, 0.0)
    try:
        return (0, float(x))
    except ValueError:
        return (1, 0.0) if x == "False" else (1, 1.0)


def _band_str(vals) -> str:
    """The band as COMMA-SEPARATED VALUES - owner directive B2141.

    A COUNT says how wide the search was; the VALUES say which grid it was,
    and two configs with the same count can be different searches entirely.
    """
    return ",".join(v.replace("'", "") for v in sorted(vals, key=_band_key))


DEPTH_TIERS = ((100, None, "DEEP"), (30, 100, "MID"), (0, 30, "THIN"))


def _d_tier(n) -> str:
    """The depth band a row's sample sits in. Named, not a raw number, because
    the reader needs to compare rows at a glance and 128-vs-40 is not a
    comparison anyone makes correctly while scanning a rank order."""
    if n is None:
        return "?"
    for lo, hi, name in DEPTH_TIERS:
        if n >= lo and (hi is None or n < hi):
            return name
    return "?"


# S6-B2500/B2505: Table D/D-2 axes per STRATEGY FAMILY. The smc entry
# mirrors the previously hardcoded keys exactly (golden-diff proven at
# landing). The institutional entry is a CONTRACT, not a description: no
# institutional grid exists yet, so these are the config keys its future
# grader MUST emit (pinned by test_b2505) - defining the schema now beats
# guessing it later (L722).
D_AXIS_FAMILIES = {
    "smc_breaker_block": {
        "detect": "P1_swing_length",
        "d1": (("sw", "cfg", "P1_swing_length"), ("sp", "cfg", "P6_span")),
        "d2": (("P1 swing", "cfg", "P1_swing_length"),
               ("P2 close_mit", "admit", "close_mitigation"),
               ("P3 tail_n", "admit", "tail_n"),
               ("P4 age_bars", "admit", "age_bars_max"),
               ("P5 break_pct", "admit", "break_pct_max"),
               ("P6 span", "cfg", "P6_span")),
    },
    "institutional_committed_growth_long": {
        "detect": "P4_min_consecutive_quarters",
        "d1": (("sw", "cfg", "P4_min_consecutive_quarters"),
               ("sp", "cfg", "P9_span")),
        "d2": (("P4 minq", "cfg", "P4_min_consecutive_quarters"),
               ("P5 lookback", "cfg", "P5_growth_lookback_quarters"),
               ("P6 mult", "cfg", "P6_growth_multiple"),
               ("P7 min_committed", "admit", "min_committed_growth"),
               ("P8 fb_min_incr", "admit", "fallback_min_increased"),
               ("P9 span", "cfg", "P9_span")),
    },
}


def _d_family(cfg: dict) -> dict:
    """Pick the axis family by its detect key; smc stays the default so the
    existing grids render byte-identically. An UNREGISTERED family falls back
    to smc's columns, which then render '-' - visible, never silent."""
    for fam in D_AXIS_FAMILIES.values():
        if fam["detect"] in (cfg or {}):
            return fam
    return D_AXIS_FAMILIES["smc_breaker_block"]


def _d_axis_value(spec, cfg: dict, admit: dict):
    _, src, key = spec
    return (cfg if src == "cfg" else (admit or {})).get(key)


def table_d(grids: dict[str, dict], top: int = 20) -> list[str]:
    """STEP-1 RANKED LIST - one row per (config x exit) outcome, top N.

    Owner directive 2026-08-28. Table C answers "what happened inside one
    config"; this answers "across every config, which outcomes rank highest".
    Different grain, so a different table rather than more columns on C.

    SORT: `is_ci_lo` descending, and nothing else. Step-1 admission is
    min-trades >= 10 plus a ranked list with NO GATES (owner ruling B1608), so
    this table FILTERS NOTHING - every column below is displayed, never applied.
    Sorting on Sharpe was rejected: L455 records that the higher Sharpe can
    carry a NEGATIVE lower bound.

    `n` SITS BESIDE THE SORT KEY, DELIBERATELY. Measured when this table was
    built: of a naive top-20, **0 rows had n >= 100** and the best result in
    each depth band was +0.098 at n=128, +0.179 at n=40, +1.214 at n=11 -
    rank improving monotonically as evidence thins. A conservative lower bound
    still favours a tight small sample over a noisy deep one, so rank must not
    be read as trustworthiness. The `tier` column exists so that is visible
    without arithmetic.

    DUPLICATES ARE LABELLED, NOT DROPPED. Measured: 210 ranked rows carry 187
    distinct (ci_lo, sharpe, n, exit) signatures; 18 signatures repeat, and
    **7 of a naive top-20 were restatements of an earlier row** - three
    swing-30 configs produced byte-identical best cells. Suppressing them would
    be a gate in a step the owner ruled has none, and showing them unmarked
    would read as three independent confirmations. So `dup` reads `2 of 3` and
    the reader sees one discovery wearing three swing-lengths.

    The renderer is the only source. Table C's docstring records that hand-
    retyping a locked table dropped four columns three times before the owner
    caught it; `scripts/show_table_d.py` prints this, and nothing else should.
    """
    from collections import Counter

    rows = []
    for name, g in grids.items():
        cfg = g.get("config") or {}
        _fam = _d_family(cfg)
        for r in (g.get("step1_ranking") or []):
            a = r.get("admit") or {}
            rows.append({
                "config": name,
                "sw": _d_axis_value(_fam["d1"][0], cfg, a),
                "sp": _d_axis_value(_fam["d1"][1], cfg, a),
                "exit": r.get("exit"),
                "ci": r.get("is_ci_lo"), "n": r.get("fires"),
                "sh": r.get("is_sharpe"), "cls": r.get("class_size"),
                "ho": a.get("holdout_n"), "fp": a.get("full_period_n"),
                "verdict": a.get("verdict"),
            })

    sig = lambda r: (round(r["ci"], 3) if r["ci"] is not None else None,
                     round(r["sh"], 3) if r["sh"] is not None else None,
                     r["n"], r["exit"])
    counts = Counter(sig(r) for r in rows)
    rows.sort(key=lambda r: (-(r["ci"] if r["ci"] is not None else -9e9),
                             -(r["n"] or 0)))
    seen = Counter()

    out = [
        "_Step-1 ranked list. `is_ci_lo` is the RANKING KEY, not a gate - Step-1 "
        "admission is min-trades >= 10 plus this list, with NO gates applied "
        "(owner ruling B1608). `n` = fires in-sample, placed beside the sort key "
        "on purpose. `tier` = DEEP n>=100 / MID 30-99 / THIN 10-29. `dup` = this "
        "row's (ci_lo, sharpe, n, exit) signature appears in more than one "
        "config - one discovery, several parameter pairs, NOT independent "
        "confirmations. `cls` = equivalence-class size. Nothing here is "
        "filtered._",
        "",
        "**RANK IS NOT TRUSTWORTHINESS.** A conservative lower bound still "
        "favours a tight small sample over a noisy deep one; read `n` and `tier` "
        "beside every rank.",
        "",
        "**HOW `exit` WAS CHOSEN, AND BY WHICH RULER.** Step 1 picks each cell's "
        "exit by SHARPE alone - a cheap ranking pass (owner ruling B1605) - while "
        "this table RANKS by is_ci_lo. Two different objectives, disclosed because "
        "a row can lead on is_ci_lo while carrying the exit that won on Sharpe. "
        "Step 2 re-ranks ALL exits by gates passed and is the admission criterion; "
        "it has not run. **24 exit methods are registered; 22 are effective per "
        "cell** - next_pivot_target is refused on boundary-spanning cells (B2014, "
        "flagged by npt_excluded_identity_boundary) and 1 more is collapsed as "
        "byte-identical to a survivor (B1593). 24 - 1 - 1 = 22.",
        "",
        "| # | config | sw | sp | exit | is_ci_lo | n | tier | dup | is_sharpe "
        "| cls | holdout_n | full_period_n | verdict |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(rows[:top], 1):
        k = sig(r)
        seen[k] += 1
        dup = f"{seen[k]} of {counts[k]}" if counts[k] > 1 else "-"
        ci = f"{r['ci']:+.3f}" if r["ci"] is not None else "n/a"
        sh = f"{r['sh']:.3f}" if r["sh"] is not None else "n/a"
        out.append(
            f"| {i} | {r['config']} | {r['sw']} | {r['sp']} | {r['exit']} | "
            f"{ci} | {r['n']} | {_d_tier(r['n'])} | {dup} | {sh} | {r['cls']} | "
            f"{r['ho']} | {r['fp']} | {r['verdict']} |")

    out += ["", f"_{len(rows)} ranked outcomes across {len(grids)} graded "
                f"configs; {len(counts)} distinct signatures._"]

    # per-tier best - the comparison the rank order actively hides
    out += ["", "**Best within each depth tier** (the comparison a rank order hides):",
            "", "| tier | best is_ci_lo | at n | rows |", "|---|---|---|---|"]
    for lo, hi, name in DEPTH_TIERS:
        sub = [r for r in rows if r["ci"] is not None and r["n"] is not None
               and r["n"] >= lo and (hi is None or r["n"] < hi)]
        if sub:
            b = max(sub, key=lambda r: r["ci"])
            out.append(f"| {name} | {b['ci']:+.3f} | {b['n']} | {len(sub)} |")
    return out


def table_d_params(grids: dict[str, dict], top: int = 20) -> list[str]:
    """TABLE D-2 - the SIX swept axes for the same top-N rows as table_d.

    Owner directive 2026-08-28: show all of P1-P6, not just swing and span.

    WHY A SECOND TABLE RATHER THAN FOUR MORE COLUMNS. D-1 is already 14 columns;
    at 18 a markdown table wraps in a terminal and becomes unreadable, which is
    how Table C lost four columns three times. So the axes get their own table
    in the SAME rank order, with the `#` column as the visual join - row 7 here
    is row 7 there.

    WHERE THE VALUES COME FROM. P1 and P6 are in the grid's `config`; P2-P5 were
    already recorded in every ranked row's `admit` dict and simply never
    displayed. Nothing new is computed - the data was always there, which is why
    hiding four of six swept axes was a display defect rather than a gap.
    """
    rows = []
    fam_seen = None
    for name, g in grids.items():
        cfg = g.get("config") or {}
        _fam = _d_family(cfg)
        fam_seen = fam_seen or _fam
        for r in (g.get("step1_ranking") or []):
            a = r.get("admit") or {}
            row = {"config": name, "ci": r.get("is_ci_lo"),
                   "n": r.get("fires"),
                   "npt": a.get("npt_excluded_identity_boundary")}
            for i, spec in enumerate(_fam["d2"], 1):
                row[f"A{i}"] = _d_axis_value(spec, cfg, a)
            rows.append(row)
    rows.sort(key=lambda r: (-(r["ci"] if r["ci"] is not None else -9e9),
                             -(r["n"] or 0)))
    fam = fam_seen or D_AXIS_FAMILIES["smc_breaker_block"]
    labels = [spec[0] for spec in fam["d2"]]
    _is_smc = fam is D_AXIS_FAMILIES["smc_breaker_block"]
    _preamble = (
        # BYTE-IDENTICAL to the pre-B2505 text for smc grids (golden diff)
        "_The SIX swept axes for the same rows, same order - join on `#`. "
        "P1 swing_length, P2 close_mitigation (False = production, mitigate on "
        "high/low), P3 tail_n, P4 age_bars_max (None = production, no cap), "
        "P5 break_pct_max (None = production, no cap), P6 span. `npt_excl` = "
        "next_pivot_target was refused on this cell as boundary-spanning "
        "(B2014), which is one of the two exits missing from 24._"
        if _is_smc else
        "_The swept axes for the same rows, same order - join on `#`. Axis "
        "labels come from the per-family registry (D_AXIS_FAMILIES); `npt_excl`"
        " = next_pivot_target refused as boundary-spanning (B2014)._")
    out = [
        _preamble,
        "",
        "| # | config | " + " | ".join(labels) + " | npt_excl |",
        "|" + "---|" * (len(labels) + 3),
    ]
    for i, r in enumerate(rows[:top], 1):
        vals = " | ".join(str(r[f"A{j}"]) for j in range(1, len(labels) + 1))
        out.append(f"| {i} | {r['config']} | {vals} | {r['npt']} |")
    return out


def free_levels_graded(name, root=None) -> dict:
    """Which levels of a FREE-graded parameter this config actually had graded.

    Read from the battery's own artifact
    output_audit/output_<name>_free_levels.json (B2569, written on every
    landing), keyed by the lowercased P-id: {"p7": [3, 5, 11, 14]}. The
    reproduction gate writes `levels: []` when it REFUSES to grade (coverage
    below floor), and that empty case reads as NOTHING GRADED rather than as
    the declared band - the point of the gate is that those levels were not
    measured on this cube.
    """
    root = Path(root) if root is not None else CODE_ROOT
    p = root / "output_audit" / ("output_" + name + "_free_levels.json")
    if not p.is_file():
        return {}
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    levels = doc.get("levels")
    if not isinstance(levels, dict):
        return {}
    out = {}
    for entry in levels.values():
        if not isinstance(entry, dict):
            continue
        for pid in ("p7", "p8"):
            if entry.get(pid) is not None:
                out.setdefault(pid, set()).add(entry[pid])
    return {k: sorted(v) for k, v in out.items()}


def producer_bands(name, grid, root=None):
    """One cell per parameter of the config's family - EVERY producer band.

    Owner directive 2026-09-03: the column is `all producer bands tested`, not
    the SMC six. MEASURED at that ruling: SPECS carries 6 params for
    smc_breaker_block_long and 9 for institutional_committed_growth_long, and
    ICG rows rendered 4 of 9 - P1/P2/P3 (precompute hygiene, not swept by
    design) and P7/P8 (graded FREE from the landed cube) were absent, so the
    row could not be read as a statement of what the config exercised.

    Returns [(pid, param, cell)], or None when the grid names no family this
    table knows - the caller then falls back to the config block. Precedence:
      1. PINNED in the artifact's config block -> `v(fixed)`
      2. OBSERVED in the result rows -> the values searched in-cube
      3. GRADED FREE on this cube -> `v1,v2(free)`
      4. declared free band, no artifact -> `v1,v2(free, declared)`
      5. NOT-SWEPT-BY-DESIGN -> `v(not swept)`
      6. otherwise `?` - never a number (L580)
    """
    spec = SPECS.get(grid.get("strategy"))
    if not spec:
        return None
    cfg = grid.get("config") or {}
    res, _pf, _pu = grid_population(grid)
    observed = {}
    for r in res:
        for _p in spec["params"]:
            k = _p["param"]
            if k in r:
                observed.setdefault(k, set()).add(repr(r[k]))
    freed = free_levels_graded(name, root)
    cells = []
    for _p in spec["params"]:
        pid, nm = _p["id"], _p["param"]
        pin = cfg.get(pid + "_" + nm)
        obs = observed.get(nm)
        fl = freed.get(pid.lower())
        band = [str(x) for x in (_p.get("band") or [])]
        if pin is not None:
            cell = _fmt(pin) + "(fixed)"
        elif obs:
            cell = _band_str(obs)
        elif fl:
            cell = _band_str({repr(v) for v in fl}) + "(free)"
        elif _p.get("free_band"):
            cell = _band_str({repr(v) for v in _p["free_band"]}) + "(free, declared)"
        elif not (_p.get("sweep_levels") or []) and band == [str(_p.get("production"))]:
            cell = _fmt(_p.get("production")) + "(not swept)"
        else:
            cell = "?"
        cells.append((pid, nm, cell))
    return cells


def table_c(grids: dict[str, dict], root=None) -> list[str]:
    """POST RUN CONFIG TABLE - one row per config, the whole funnel across it.

    B1701, owner directive: the post-config numbers were being reported as prose
    and were "pretty much unreadable". This is the third fixed template
    alongside TABLE A (parameter inventory) and TABLE B (combination results),
    and it answers ONE question: of everything this config tried, how much
    survived, and where did the rest stop?

    The columns are the funnel IN ORDER, because every drop-off has a different
    cause and lumping them hides which one is binding:

      combos      every parameter combination enumerated
      no-exit     died at exit SELECTION - no exit cleared min_n IN-SAMPLE, so
                  grading never happened. This is the dominant loss (85pct at
                  wave 1) and it is a SAMPLE-SIZE fact, not a quality verdict.
      graded      reached evaluate() and produced a Sharpe
      distinct    graded outcomes after equivalence-class collapse - combinations
                  differing only in a SATURATED parameter are the SAME fire set,
                  so counting rows overstates the evidence (L473)
      bands       distinct VALUES this config actually exercised, summed over
                  the parameter axes. B1898 (c): a config that tried one band
                  is not evidence of the same weight as one that tried four,
                  and the old table could not tell them apart.
      best        the top distinct outcome by ci_lo, not Sharpe (L455: the higher
                  Sharpe can carry a NEGATIVE lower bound)

    B1898 (a): the PASS column is GONE. Step 1 is a ranked list with NO GATES
    (B1608) - gates belong to Step 2 (L471) - so the column reported 0 forever
    and read as a verdict on work that had not been judged yet.

    B1898 (b): `no-exit` is renamed `starved-IS`. It is a SAMPLE-SIZE fact -
    no exit cleared min_n IN-SAMPLE - and "no-exit" reads as a selection
    failure. The docstring always said so; the HEADER did not, and the header
    is what gets quoted.

    `graded + no_exit + zero_fires` must equal `combos`; the renderer asserts it
    rather than trusting the arithmetic.
    """
    # B1898 (d), owner directive: every presentation of this table defines its
    # own terms. A reader who meets `graded` or `ci_lo` for the first time in a
    # pasted table has no way to look them up.
    per_config_axes: dict = {}
    _per_config_grid: dict = {}   # B2585: the grid itself, for producer_bands
    rows = ["_`starved-IS` = no exit cleared min_n IN-SAMPLE, a SAMPLE-SIZE fact "
            "rather than a quality verdict. `graded` = reached `evaluate()` and "
            "produced a Sharpe. `distinct` = graded outcomes after "
            "equivalence-class collapse (L473). `bands` = distinct parameter "
            "VALUES exercised. `ci_lo` = the LOWER bound of the Sharpe "
            "confidence interval, which is what `best` ranks on - a higher "
            "Sharpe can carry a NEGATIVE lower bound (L455). `all producer "
            "bands tested` = EVERY parameter of this config's family (owner "
            "directive 2026-09-03), each marked how it was exercised: (fixed) "
            "pinned by this config, a bare list searched in-cube, (free) graded "
            "from the landed cube by the battery, (free, declared) gradable but "
            "not graded here, (not swept) held by design. The count is the "
            "family's own SPECS entry - 6 for smc_breaker_block_long, 9 for "
            "institutional_committed_growth_long._",
            "",
            "| config | combos | starved-IS | no-Sharpe | graded | distinct | bands | all producer bands tested | median IS-Sharpe | best IS-Sharpe | best IS-CI-lo | best combination |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, g in grids.items():
        # B2521 (S6-B2520m): the declared population, not the field name.
        res, _pf, _pu = grid_population(g)
        # B2619 (S6-B2566): the "combos" header is locked; when the population
        # is NOT combinations the CELL names its unit, so a single-combination
        # grid reads "1 combination (24 exits ranked)" instead of a bare 24 -
        # the owner-found mislabel ("why is it just 24 combinations?").
        _combo_cell = (str(len(res)) if _pu == "combinations"
                       else f"1 combination ({len(res)} {_pu} ranked)")
        # B2181 (S6-B2176b): a pure Step-1 grid populates ONLY the IS fields
        # (holdout untouched by design post-B2136), so bucketing on the
        # holdout `sharpe` rendered graded=0 beside 89 real distinct
        # outcomes. An IS-only artifact buckets on is_sharpe instead;
        # detection is from the artifact itself: any row carrying a
        # non-None holdout sharpe marks a mixed/legacy grid.
        is_only = not any(r.get("sharpe") is not None for r in res)
        _sk = "is_sharpe" if is_only else "sharpe"
        graded = [r for r in res if r.get(_sk) is not None]
        no_exit = [r for r in res if r.get("verdict") == "NO_EXIT_SELECTABLE"]
        zero = [r for r in res if r.get("verdict") == "ZERO_FIRES"]
        # B1701: the FOURTH bucket, found because the reconciliation assert
        # fired on its first render. These rows HAVE a verdict but no Sharpe -
        # evaluate() returned a dict and `_sharpe` did not, at holdout_n 16-29.
        # Without this bucket 31-66 rows per config vanished from the funnel,
        # which is exactly the silent loss the assert exists to catch.
        no_sh = [r for r in res if r.get(_sk) is None
                 and r.get("verdict") not in ("NO_EXIT_SELECTABLE", "ZERO_FIRES")]
        other = len(res) - len(graded) - len(no_exit) - len(zero) - len(no_sh)
        # B1898 (c): count the distinct VALUES actually exercised per axis.
        # Reading them from the enumerated combinations rather than from the
        # grid spec, because the spec is what was INTENDED and the results are
        # what ran.
        # B2137 (S6-B2135c): read the axes from the result rows' OWN top-level
        # parameter keys. This looked in `r["admit"]`, which exists only on the
        # carried top-10 ranking rows - so `bands` rendered `-` for every config
        # ever graded, and the evidence-weight question B1898(c) added the
        # column to answer had no answer for any of them.
        axes = {}
        for r in res:
            for k in AXIS_KEYS:
                if k in r:
                    axes.setdefault(k, set()).add(repr(r[k]))
        # B1898b: render '-' when the artifact records no `admit` block.
        # The first version emitted 0, which reads as 'tested nothing'
        # when the truth is 'not recorded' - the exact rule written one
        # batch earlier at B1889b, that a value which cannot be measured
        # must not render as a number.
        # B2585: a level graded FREE from the landed cube is a value this
        # config exercised - the battery grades them on every landing
        # (B2569) - so the count includes them. Before this, a family that
        # searches nothing in-cube but grades four free levels read `-`,
        # which says 'not recorded' about work that WAS done.
        _freed = free_levels_graded(name, root)
        _free_n = sum(len(v) for v in _freed.values() if len(v) > 1)
        bands = (sum(len(v) for v in axes.values() if len(v) > 1) + _free_n
                 if (axes or _freed) else None)
        rank = g.get("step1_ranking") or []
        # B2136 (S6-B2135a): rank on the IN-SAMPLE key when the artifact carries
        # it. This selected on `ci_lo`, which is HOLDOUT-derived - so the table
        # reported a holdout-selected pick as "best" even for artifacts that
        # ranked honestly, perpetuating the contamination it was built to
        # expose. Pre-B2010 artifacts have no is_ci_lo; they fall back to the
        # holdout key AND are marked, because a reader cannot otherwise tell a
        # holdout-selected row from an in-sample one (the L558 test).
        _has_is = any(r.get("is_ci_lo") is not None for r in rank)
        _key = "is_ci_lo" if _has_is else "ci_lo"
        top = max(rank, key=lambda r: (r.get(_key) if r.get(_key) is not None
                                       else -9)) if rank else None
        if top:
            a = top["admit"]
            # B2542: FAMILY-AWARE. This read the SMC family's four parameter
            # names directly and raised KeyError on every institutional grid,
            # so no config of that family had ever rendered - the same family
            # boundary as L741, crossed from the consumer's side. The locked
            # 12-column format is unchanged; only this cell's content adapts.
            _exit = a.get("exit") or top.get("exit") or "-"
            if "close_mitigation" in a:
                combo = (f"cm={a['close_mitigation']} brk={_fmt(a['break_pct_max'])} "
                         f"age={_fmt(a['age_bars_max'])} tail={a['tail_n']} / {_exit}")
            else:
                _cfg = g.get("config") or {}
                _parts = " ".join(f"{k}={_fmt(v)}" for k, v in sorted(_cfg.items()))
                combo = f"{_parts or '?'} / {_exit}"
            if _has_is:
                sh, cl = _measured_fmt(top.get("is_sharpe")), _measured_fmt(top.get("is_ci_lo"))
            else:
                sh = f"HOLDOUT {_measured_fmt(top.get('sharpe'))}"
                cl = f"HOLDOUT {_measured_fmt(top.get('ci_lo'))}"
        else:
            combo, sh, cl = "-", "-", "-"
        # B2138, owner directive: P1..P6 IN the table itself, one cell, so a
        # pasted row carries which axes were searched. P1/P6 come from the
        # artifact's own `config` block (recorded since B2138); an artifact
        # without it reads `?` for those two rather than a number, because the
        # cross-config axes were written nowhere before that (S6-B2136).
        # B2182 (S6-B2178b, SPP per Walton): the MEDIAN Sharpe across all
        # graded combos is a nearly unbiased estimate of live expectancy;
        # the max is biased by exactly the selection performed. max - median
        # = the selection artifact, printed beside each other so the reader
        # sees both every time.
        import statistics as _st
        _med_vals = [r.get(_sk) for r in graded if r.get(_sk) is not None]
        med = round(_st.median(_med_vals), 3) if _med_vals else None
        cfg = g.get("config") or {}
        # B2542: a family whose axes are not the SMC six records them as
        # P<N>_<name> in its own config block. Render THOSE rather than six
        # `?` cells, which said "not recorded" about axes that ARE recorded.
        # B2585, owner directive: EVERY producer parameter of the family,
        # derived from its SPECS entry. The two branches below survive as
        # fallbacks for a grid naming no family this table knows.
        _pb = producer_bands(name, g, root)
        if _pb:
            p_col = "; ".join(pid + "=" + cell for pid, _nm, cell in _pb)
            rows.append(f"| `{name}` | {_combo_cell} | {len(no_exit)} | {len(no_sh)} | "
                        f"{len(graded)} | {g.get('step1_distinct_outcomes', '-')} | "
                        f"{_measured_fmt(bands)} | {p_col} | {_measured_fmt(med)} | "
                        f"{sh} | {cl} | {combo} |")
            per_config_axes[name] = (axes, cfg)
            _per_config_grid[name] = g
            continue
        _smc_shaped = any(nm in axes for nm in AXIS_KEYS) or "P1_swing_length" in cfg
        if not _smc_shaped and cfg:
            p_col = "; ".join(
                f"{k.split('_', 1)[0]}={_fmt(v)}(fixed)" for k, v in sorted(cfg.items()))
            rows.append(f"| `{name}` | {_combo_cell} | {len(no_exit)} | {len(no_sh)} | "
                        f"{len(graded)} | {g.get('step1_distinct_outcomes', '-')} | "
                        f"{_measured_fmt(bands)} | {p_col} | {_measured_fmt(med)} | "
                        f"{sh} | {cl} | {combo} |")
            per_config_axes[name] = (axes, cfg)
            continue
        p_cells = []
        for pid, nm in P_AXES:
            if pid == "P1":
                v = cfg.get("P1_swing_length")
            elif pid == "P6":
                v = cfg.get("P6_span")
            else:
                v = _band_str(axes[nm]) if axes.get(nm) else None
            p_cells.append(f"{pid}={v if v is not None else '?'}"
                           + ("(fixed)" if pid in ("P1", "P6") and v is not None else ""))
        # B2141: a PIPE separator splits the cell into six columns and destroys
        # the table - caught by rendering it. Semicolon is safe inside a
        # markdown cell.
        p_col = "; ".join(p_cells)
        rows.append(f"| `{name}` | {_combo_cell} | {len(no_exit)} | {len(no_sh)} | {len(graded)} | "
                    f"{g.get('step1_distinct_outcomes', '-')} | {_measured_fmt(bands)} | {p_col} | "
                    f"{_measured_fmt(med)} | {sh} | {cl} | {combo} |")
        if other:
            rows.append(f"| | | | | | | | | | | | **UNCLASSIFIED {other} rows - the funnel does not "
                        f"reconcile, do not trust this row** |")
        per_config_axes[name] = (axes, cfg)

    # B2560 (S6-B2542a): a config whose family does not use the SMC six records
    # its OWN axes as P<N>_<name> in the artifact's config block. Rendering the
    # hard-coded six for it printed "not recorded" in all six cells - true,
    # useless, and indistinguishable from an axis that genuinely was not
    # recorded. Such configs are split out and rendered from their own keys,
    # the same source the funnel row above already reads (B2542). They are
    # RENDERED, not dropped: v1 of this patch removed them from the table and
    # emitted nothing, trading a visible defect for an invisible one.
    _foreign = {}
    for _n in list(per_config_axes):
        _axes, _cfg = per_config_axes[_n]
        _own = {k: v for k, v in (_cfg or {}).items()
                if k.startswith("P") and "_" in k}
        _is_smc = (any(nm in (_axes or {}) for _, nm in P_AXES)
                   or "P1_swing_length" in (_cfg or {}))
        if _own and not _is_smc:
            _foreign[_n] = _own
            del per_config_axes[_n]

    # B2137, owner directive: PARAMETERS TESTED - the P1..P6 bands each config
    # actually exercised, by P-id, so a reader can see WHICH axes carried the
    # search and which sat at one value. A `bands` COUNT says how many; this
    # says which, and an axis pinned at a single value is a dimension that
    # bought nothing.
    rows += ["", "**Parameters tested** - distinct values each config exercised per axis, read "
             "from the result rows themselves. `1 value` = the axis was PINNED and contributed "
             "no search; an axis absent from the artifact reads `not recorded`, never `1`. "
             "**P1 `swing_length` and P6 `span` are the CROSS-CONFIG axes** - they define which "
             "config a cube IS and are held FIXED within it, so they show a value rather than "
             "a count. Recorded in the artifact since B2138; anything graded before that reads "
             "`not recorded`, which is what let a swing-10 cube be re-graded as swing-20 "
             "(S6-B2136).", "",
             ]
    if per_config_axes:
        rows += ["| config | " + " | ".join(f"{pid} {nm}" for pid, nm in P_AXES) + " |",
                 "|---|" + "---|" * len(P_AXES)]
    for name, (axes, cfg) in per_config_axes.items():
        cells = []
        for pid, nm in P_AXES:
            # B2138: P1/P6 come from the artifact's config block - the SAME
            # source the in-table column uses. Reading them from `axes` made
            # the block print "not recorded" while the column printed the
            # value, so one render contradicted itself.
            if pid in ("P1", "P6"):
                cv = cfg.get("P1_swing_length" if pid == "P1" else "P6_span")
                cells.append(f"FIXED at {cv}" if cv is not None else "not recorded")
                continue
            vals = axes.get(nm)
            if not vals:
                cells.append("not recorded")
            else:
                # B2137: sort NUMERICALLY where the values are numbers - a
                # string sort renders tail_n as "1, 10, 2, 20, 3, 5", which
                # reads as a jumbled band and hides whether the axis is ordered.
                cells.append(f"{len(vals)}: " + _band_str(vals))
        rows.append(f"| `{name}` | " + " | ".join(cells) + " |")

    # B2560: the other families, each from its own recorded axes. One table per
    # axis-set, because a shared header would have to be the union and would
    # reintroduce the empty cells this fixes.
    if _foreign:
        rows += ["", "**Parameters tested - other strategy families.** These configs record "
                 "their own axes in the artifact's `config` block rather than the SMC six "
                 "above, so they are rendered from those keys. A family whose axes are all "
                 "held fixed within a config shows values rather than counts, exactly as P1 "
                 "and P6 do for SMC (S6-B2542a)."]
        # GROUP by axis-set: configs sharing an axis set share a table, or the
        # render repeats an identical header per config, which reads as several
        # families when it is one.
        _groups = {}
        for _n, _own in _foreign.items():
            _groups.setdefault(tuple(sorted(_own)), []).append((_n, _own))
        for _keys, _members in _groups.items():
            # B2585: prefer the family's FULL parameter set over the config
            # block's keys - the block recorded only what the launcher set,
            # so P1/P2/P3 (not swept) and P7/P8 (free) never appeared here
            # either. Falls back to the recorded keys for an unknown family.
            _pb0 = producer_bands(_members[0][0],
                                  _per_config_grid.get(_members[0][0]) or {}, root)
            if _pb0:
                rows += ["", "| config | " + " | ".join(
                    pid + " " + nm for pid, nm, _c in _pb0) + " |",
                         "|---|" + "---|" * len(_pb0)]
                for _n, _own in _members:
                    _cells = producer_bands(_n, _per_config_grid.get(_n) or {}, root) or []
                    rows.append(f"| `{_n}` | " + " | ".join(
                        c for _pid, _nm, c in _cells) + " |")
                continue
            rows += ["", "| config | " + " | ".join(_keys) + " |",
                     "|---|" + "---|" * len(_keys)]
            for _n, _own in _members:
                rows.append(f"| `{_n}` | " + " | ".join(
                    f"FIXED at {_fmt(_own[k])}" for k in _keys) + " |")
    return rows


def table_b(results: list[dict], keys: list[str]) -> list[str]:
    """Every metric roster_core.evaluate() computes, split GATED vs DIAGNOSTIC.

    GATED (6) decide PASS/FAIL. DIAGNOSTIC are computed and reported but do NOT
    gate - per CLAUDE.md, win_rate was demoted at B1387 and max_drawdown /
    calmar / deflated_sharpe at B1436-B1437. Reporting them keeps a cell's
    character visible even when the verdict is FAIL.
    """
    hdr = " | ".join(keys)
    rows = [f"| {hdr} | fires | ho n | full n | exit | **Sharpe** | **PF** | "
            f"**Sortino** | **PSR** | win% | payoff | expectancy | p | CI-lo | "
            f"gates | failing | verdict |",
            "|" + "---|" * (len(keys) + 16)]
    for r in results:
        vals = " | ".join(_fmt(r.get(k)) for k in keys)
        fail = ", ".join(k for k, v in (r.get("gates") or {}).items() if not v) or "-"
        rows.append(
            f"| {vals} | {r.get('fires', 0)} | {_fmt(r.get('holdout_n'))} | "
            f"{_fmt(r.get('full_period_n'))} | {r.get('exit', '-')} | "
            f"{_fmt(r.get('sharpe'))} | {_fmt(r.get('profit_factor'))} | "
            f"{_fmt(r.get('sortino'))} | {_fmt(r.get('psr'))} | "
            f"{_fmt(r.get('win_rate'))} | {_fmt(r.get('payoff'))} | "
            f"{_fmt(r.get('expectancy'))} | {_fmt(r.get('p'))} | "
            f"{_fmt(r.get('ci_lo'))} | "
            f"{r.get('gates_passed', '-')}/{len(GATE_ORDER)} | {fail} | {r['verdict']} |")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--results", default="", help="grid results JSON")
    # B1523 owner directive: "Everytime you show factorial you need to show
    # boolean producer formula again." This mode emits the FORMULA and the
    # FACTORIAL together and cannot emit one without the other - the coupling is
    # in the tool, not in anyone remembering.
    ap.add_argument("--factorial", action="store_true",
                    help="print Section 1 formula + factorial breakdown; no results needed")
    ap.add_argument("--keys", default=None,
                    help="grid row keys for Table B; default = the family's own "
                         "SPECS tools.grid_keys (S6-B2573c - the old default was "
                         "the smc keys for every family)")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    spec = SPECS.get(a.strategy)
    if spec is None:
        print(f"no SPEC for {a.strategy}; add one to SPECS (never infer at runtime)")
        return 1
    if a.factorial:
        errs = validate_spec(spec)
        if errs:
            print("SPEC VALIDATION FAILED:")
            for e in errs:
                print(f"  {e}")
            return 1
        applicable = [p for p in spec["params"] if p["status"] != "N/A"]
        fact = math.prod(len(p["band"]) for p in applicable)
        free = math.prod(len(p["band"]) for p in applicable if p["subset_safe"])
        runs = math.prod(len(p["band"]) for p in applicable if not p["subset_safe"])
        print(f"# {a.strategy} - FORMULA + FACTORIAL (never shown apart)")
        print("")
        print("## Boolean producer formula (READ from source)")
        print("")
        print("```")
        print(spec["formula"])
        print("```")
        print("")
        print("## Factorial")
        print("")
        print("| | parameter | production | band VALUES | n | class | own engine run? |")
        print("|---|---|---|---|---|---|---|")
        for p in applicable:
            cls = "subset-safe" if p["subset_safe"] else "**FIRE-ADDING**"
            need = "no - derives offline" if p["subset_safe"] else "**YES**"
            vals = ", ".join(_fmt(b) for b in p["band"]) or "-"
            print(f"| {p['id']} | `{p['param']}` | {_fmt(p['production'])} | {vals} | {len(p['band'])} | {cls} | {need} |")
        expr = " x ".join(str(len(p["band"])) for p in applicable)
        print("")
        print("```")
        print(f"FULL FACTORIAL   {expr} = {fact}")
        print(f"offline per run  {free}")
        print(f"ENGINE RUNS      {runs}")
        print(f"check            {runs} x {free} = {runs * free}")
        print("```")
        return 0

    if not a.results:
        print("--results is required unless --factorial is passed")
        return 1
    data = json.loads(Path(a.results).read_text())
    results = data["results"]
    keys = a.keys.split(",") if a.keys else list(
        (spec.get("tools") or {}).get("grid_keys") or [])
    if not keys:
        print(f"--keys not given and SPECS[{a.strategy!r}] declares no tools.grid_keys")
        return 1

    tested = [p for p in spec["params"] if p["status"] == "TESTED"]
    applicable = [p for p in spec["params"] if p["status"] != "N/A"]
    # Factorial + free subspace computed from the inventory, never hand-counted
    # (L368: hand-counting reintroduces the error #182 exists to prevent).
    factorial = math.prod(len(p["band"]) for p in applicable)
    free_space = math.prod(len(p["band"]) for p in applicable if p["subset_safe"])
    gradable = [r for r in results if r["verdict"] in ("PASS", "FAIL")]
    passed = [r for r in results if r["verdict"] == "PASS"]

    errs = validate_spec(spec)
    if errs:
        print("SPEC VALIDATION FAILED (formula <-> Table A drift):")
        for e in errs:
            print(f"  {e}")
        return 1

    out = [f"# Producer variant table - `{a.strategy}`", "",
           f"**Gate:** `{spec['gate']}`", "",
           "## Section 1 - boolean formula (READ from source, never recalled)", "",
           "```", spec["formula"], "```", "",
           f"**R5 baseline:** {spec['baseline']['fires']} fires / "
           f"{spec['baseline']['tickers']} tickers / holdout n="
           f"{spec['baseline']['holdout_n']} / {spec['baseline']['window']} "
           f"(`{spec['baseline']['artifact']}`)", "",
           "## Section 2 - Table A: parameter inventory", ""]
    out += table_a(spec)
    out += ["", "## Section 3 - Table B: combination results", ""]
    out += table_b(results, keys)
    out += ["", "## Verdict (CHECKLIST #182 - denominator required)", "",
            f"**{len(passed)} of {len(results)} combinations passed, across "
            f"{len(tested)} of {len(applicable)} applicable producers.**", "",
            f"- graded: {len(gradable)} | non-gradable: {len(results) - len(gradable)}",
            f"- **FULL FACTORIAL = {factorial}** "
            f"({' x '.join(str(len(p['band'])) + ' (' + p['id'] + ')' for p in applicable)}); "
            f"combinations run = {len(results)} = **{100 * len(results) / factorial:.0f}% of factorial**",
            f"- free (subset-safe) subspace = {free_space} | "
            f"needs engine resim = {factorial - free_space}",
            f"- UNTESTED producers: "
            f"{', '.join(p['id'] + ' ' + p['param'] for p in spec['params'] if p['status'] == 'UNTESTED') or 'none'}",
            "", "*Generated by `scripts/producer_variant_table.py` - regenerate, do not hand-edit.*"]

    text = "\n".join(out)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"wrote {a.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
