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
                           # B2724: the graded strategy, so a RIDER cube
                           # (B2710) is spot-checked on its OWN rows -
                           # measured 25 of 50 DISAGREE without this.
                           "extra": ["--n", "50", "--strategy",
                                     "smc_breaker_block_long"],
                           "window": False,
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
             # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
             # A level is FREE only if it selects a strict SUBSET of the landed
             # fires AND its discriminating quantity is PERSISTED per trade so the
             # subset can be identified. Across ALL rows of this strategy in
             # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
             # BOOLEAN keys computed AT the production setting, and this knob's
             # discriminator is not among them - so no level is identifiable
             # offline and every one needs the engine. (P6 span looked gradable:
             # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
             # not imply price_above_ema_50, so a different span is a DIFFERENT set,
             # not a subset - evaluable is not subset-safe.) METADATA ONLY:
             # production is untouched and no run is scheduled, so no landed grade
             # is recomputed. L726 / L812 / L824.
             "free_band": [],
             "resim_band": [5, 10, 20, 30, 50],
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
             # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
             # A level is FREE only if it selects a strict SUBSET of the landed
             # fires AND its discriminating quantity is PERSISTED per trade so the
             # subset can be identified. Across ALL rows of this strategy in
             # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
             # BOOLEAN keys computed AT the production setting, and this knob's
             # discriminator is not among them - so no level is identifiable
             # offline and every one needs the engine. (P6 span looked gradable:
             # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
             # not imply price_above_ema_50, so a different span is a DIFFERENT set,
             # not a subset - evaluable is not subset-safe.) METADATA ONLY:
             # production is untouched and no run is scheduled, so no landed grade
             # is recomputed. L726 / L812 / L824.
             "free_band": [],
             "resim_band": [False, True],
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
             # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
             # A level is FREE only if it selects a strict SUBSET of the landed
             # fires AND its discriminating quantity is PERSISTED per trade so the
             # subset can be identified. Across ALL rows of this strategy in
             # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
             # BOOLEAN keys computed AT the production setting, and this knob's
             # discriminator is not among them - so no level is identifiable
             # offline and every one needs the engine. (P6 span looked gradable:
             # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
             # not imply price_above_ema_50, so a different span is a DIFFERENT set,
             # not a subset - evaluable is not subset-safe.) METADATA ONLY:
             # production is untouched and no run is scheduled, so no landed grade
             # is recomputed. L726 / L812 / L824.
             "free_band": [],
             "resim_band": [1, 2, 3, 5, 10, 20],
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
             # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
             # A level is FREE only if it selects a strict SUBSET of the landed
             # fires AND its discriminating quantity is PERSISTED per trade so the
             # subset can be identified. Across ALL rows of this strategy in
             # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
             # BOOLEAN keys computed AT the production setting, and this knob's
             # discriminator is not among them - so no level is identifiable
             # offline and every one needs the engine. (P6 span looked gradable:
             # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
             # not imply price_above_ema_50, so a different span is a DIFFERENT set,
             # not a subset - evaluable is not subset-safe.) METADATA ONLY:
             # production is untouched and no run is scheduled, so no landed grade
             # is recomputed. L726 / L812 / L824.
             "free_band": [],
             "resim_band": [60, 120, 180, 250, None],
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
             # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
             # A level is FREE only if it selects a strict SUBSET of the landed
             # fires AND its discriminating quantity is PERSISTED per trade so the
             # subset can be identified. Across ALL rows of this strategy in
             # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
             # BOOLEAN keys computed AT the production setting, and this knob's
             # discriminator is not among them - so no level is identifiable
             # offline and every one needs the engine. (P6 span looked gradable:
             # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
             # not imply price_above_ema_50, so a different span is a DIFFERENT set,
             # not a subset - evaluable is not subset-safe.) METADATA ONLY:
             # production is untouched and no run is scheduled, so no landed grade
             # is recomputed. L726 / L812 / L824.
             "free_band": [],
             "resim_band": [0.01, 0.02, 0.03, 0.05, None],
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
             # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
             # A level is FREE only if it selects a strict SUBSET of the landed
             # fires AND its discriminating quantity is PERSISTED per trade so the
             # subset can be identified. Across ALL rows of this strategy in
             # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
             # BOOLEAN keys computed AT the production setting, and this knob's
             # discriminator is not among them - so no level is identifiable
             # offline and every one needs the engine. (P6 span looked gradable:
             # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
             # not imply price_above_ema_50, so a different span is a DIFFERENT set,
             # not a subset - evaluable is not subset-safe.) METADATA ONLY:
             # production is untouched and no run is scheduled, so no landed grade
             # is recomputed. L726 / L812 / L824.
             "free_band": [],
             "resim_band": [9, 20, 21, 50, 100, 150, 200],
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

# B2634 (S6-B2633 Phase 0): inventories whose FAMILY ADAPTER does not exist
# yet. They render Table A and validate like any SPEC, but the battery and
# the launch gate read SPECS alone, so nothing can treat a Phase-0 draft as
# a runnable family (family_refusal's tools contract stays intact - a fake
# tools block naming graders that do not exist would be WORSE than none).
# An entry graduates by gaining its real tools block and moving into SPECS.
SPECS_PHASE0: dict[str, dict] = {
    "smc_liquidity_sweep_reversal": {
        "formula": """
ID SEMANTICS (owner ruling 2026-09-12): P<n> = a numbered COMPUTATION STEP in
the producer->gate derivation below (each step that carries a tunable value is
also a Table A row with that id). B<n> = a BREADTH COMPANION AXIS - a signal
from ANOTHER producer family, surfaced by the family companion screen, entering
the campaign's combination space as an added AND-condition candidate; breadth
axes are Table A members because anything in the combination space is inventory.

=============================== PRODUCER LAYER ===============================

P1  swings  =  swing_highs_lows( ohlc, swing_length = 20 )
                   PARAMETER: swing_length = 20 (smc_ict.py:194)

P2  liq_df  =  liquidity( ohlc, swings, range_percent = 0.01 )
                   -> clusters equal highs / equal lows within 1pct and flags
                      the bar that SWEEPS the cluster (Liquidity +1 up / -1 dn)
                   PARAMETER: liquidity_range_pct = 0.01 (smc_ict.py:196,:503)

P3  smc_liquidity_swept_dn = most_recent_event_within( liq_df.Liquidity == -1,
                                                       event_recency_bars = 90 )
    smc_liquidity_swept_up = same, == +1
                   PARAMETER: event_recency_bars = 90 (smc_ict.py:198,:507-509)
                   -> the PERSISTED key is this post-recency boolean

P4  bos/choch_df = bos_choch( ohlc, swings )  ->  smc_bos_bullish/bearish,
    smc_choch_bullish/bearish, same recency treatment (P3's parameter)
                   -> no own parameter beyond P1/P3

=============================== STRATEGY LAYER ===============================

long_fires  =  ( smc_liquidity_swept_dn )                              [from P3]
               AND ( smc_choch_bullish OR smc_bos_bullish )            [from P4]

short_fires =  ( smc_liquidity_swept_up )                              [from P3]
               AND ( smc_choch_bearish OR smc_bos_bearish )            [from P4]
               AND ( borrow_ok )

P4  confirmation_arm: the OR in clause two - FREE depth axis
        either (production) / choch_only / bos_only
P5  leg: long / short graded separately - FREE depth axis

=============================== BREADTH LAYER (11.2b3) =======================
Candidate added AND-conditions from the b2691 family screen (56 consistent
FDR survivors; one representative per cluster). Levels are retention
quantiles (QUANTS, breadth_step1_grid.py:44) of each axis over THIS
strategy's own fires, derived at grid time:

B1  monthly_momentum_6m       >= q   (momentum cluster rep - the ONE
    axis retained: cleared its null IS p 0.0099 b2698, 5 of 6 gates at
    Step 2 b2701. B2-B6 REMOVED by owner ruling 2026-09-12 after the
    b2694/b2701 verdicts; history in the committed artifacts)
""",
        # B2692 (S6-B2690 Wave-1 hub 1, Phase 0): boolean-only gate, so the
        # FREE depth axes are structural splits (confirmation arm + leg);
        # every producer knob below is resim-only (no env knob exists - the
        # S6-B2569a class, stated not hidden). Baseline from the B2690
        # pre-gate artifact.
        "baseline": {"artifact": "output_r5_merged_1_7", "fires": 2933,
                     "tickers": 544, "holdout_n": 570, "band": "T",
                     "window": "2022-05-05..2026-05-05"},
        "gate": "(smc_liquidity_swept_dn AND (choch_bullish OR bos_bullish)) "
                "| short mirror + borrow gate (screener strat_smc_liquidity_sweep_reversal)",
        "params": [
            {"id": "P1", "producer": "_smc.swing_highs_lows",
             "param": "swing_length", "production": 20,
             "band": [5, 10, 20, 30, 50], "free_band": [],
             "resim_band": [5, 10, 20, 30, 50], "env": "SMC_SWING_LENGTH",
             "consumers": ["backtest/config.py", "backtest/engine/exit_strategies.py", "backtest/signals/screener.py"],
             "sweep_levels": [], "subset_safe": False,
             "status": "UNTESTED", "type": "int", "engine_implemented": True,
             "evidence": "smc_ict.py:194 (default 20); band CHOSEN = the "
                         "smc_breaker_block P1 precedent; env knob B1616",
             "derivation": "feeds swings -> liquidity + structure detection; "
                           "resim-only (no env knob)"},
            {"id": "P2", "producer": "_smc.liquidity",
             "param": "liquidity_range_pct", "production": 0.01,
             "band": [0.005, 0.01, 0.02], "free_band": [],
             "resim_band": [0.005, 0.01, 0.02],
             "env": "SMC_LIQUIDITY_RANGE_PCT",
             "consumers": ["backtest/config.py", "backtest/signals/screener.py"],
             "sweep_levels": [], "subset_safe": False,
             "status": "UNTESTED", "type": "float", "engine_implemented": True,
             "evidence": "smc_ict.py:196 + :503 (range_percent); band CHOSEN "
                         "(half/double production); env knob B2706",
             "derivation": "equal-highs/lows clustering tolerance; resim-only"},
            {"id": "P3", "producer": "_most_recent_event_within",
             "param": "event_recency_bars", "production": 90,
             "band": [20, 45, 90], "free_band": [],
             "resim_band": [20, 45, 90],
             "env": "SMC_EVENT_RECENCY_BARS",
             "consumers": ["backtest/config.py", "backtest/signals/screener.py"],
             "sweep_levels": [], "subset_safe": False,
             "status": "UNTESTED", "type": "int", "engine_implemented": True,
             "evidence": "smc_ict.py:198 + :507-509 (Batch 273 lag fix); band "
                         "CHOSEN (tighter recency = fresher sweeps); env knob B2706",
             "derivation": "how recent the sweep/CHoCH/BOS event must be; the "
                           "persisted key is the POST-recency boolean, so this "
                           "cannot be re-derived offline - resim-only"},
            {"id": "P4", "producer": "gate structure (screener)",
             "param": "confirmation_arm", "production": "either",
             "band": ["either", "choch_only", "bos_only"],
             "free_band": ["either", "choch_only", "bos_only"], "resim_band": [],
             "sweep_levels": [], "subset_safe": True,
             "status": "UNTESTED", "type": "str", "engine_implemented": True,
             "evidence": "strat source (B2075 restored sweep-required; B1202 "
                         "added the BOS arm); smc_choch_*/smc_bos_* persisted "
                         "booleans - offline subset-safe",
             "derivation": "FREE depth axis 1: requiring one arm keeps a "
                           "subset of recorded fires"},
            {"id": "P5", "producer": "gate structure (screener)",
             "param": "leg", "production": "both",
             "band": ["long", "short"], "free_band": ["long", "short"],
             "resim_band": [], "sweep_levels": [], "subset_safe": True,
             "status": "UNTESTED", "type": "str", "engine_implemented": True,
             "evidence": "dual _strat3; direction persisted per trade",
             "derivation": "FREE depth axis 2: per-leg grading"},
            {"id": "B1", "producer": "compute (cross_sectional/monthly momentum)",
             "param": "monthly_momentum_6m", "production": "not gated",
             "band": ["q20", "q40", "q60", "q80"],
             "free_band": ["q20", "q40", "q60", "q80"], "resim_band": [],
             "sweep_levels": [], "subset_safe": True,
             "status": "TESTED-B2694/B2698; STEP2 5-of-6 (B2701)",
             "type": "float>=q", "engine_implemented": False,
             "evidence": "b2691_smc_companions_consistent.json rank 1 "
                         "(ts10 +1.764 / bept +13.586); persisted numeric",
             "derivation": "BREADTH axis (11.2b3): momentum-cluster rep; "
                           "levels = retention quantiles on own fires at grid time"},
            # B2708 (owner ruling 2026-09-12): B2 bb_20_20_bandwidth,
            # B3 vp_close_near_poc_pct, B4 atr_pct (inside their own null,
            # p 0.2079 b2694), B5 bullish_engulfing (IS 2.078 -> holdout
            # -0.37, refused at Step 2 b2701) and B6 gap_up_2pct (flat)
            # REMOVED - "Remove all breadth producers that did not give the
            # uplift and retain the 1." Tested history stays in the
            # committed b2694/b2698/b2701 artifacts.
        ],
    },
    "smc_order_block_bounce": {
        # B2692 (Wave-1 hub 2, Phase 0): carries a PERSISTED numeric gate
        # knob (rsi_14) - the only free threshold; producer knobs resim-only.
        "baseline": {"artifact": "output_r5_merged_1_7", "fires": 1340,
                     "holdout_n": 352, "band": "T",
                     "window": "2022-05-05..2026-05-05"},
        "gate": "(smc_ob_bullish_tap_recent_5d AND rsi_14<45 AND above_ema_200) "
                "| short mirror + borrow gate (screener strat_smc_order_block_bounce)",
        "params": [
            {"id": "P1", "producer": "_smc.swing_highs_lows",
             "param": "swing_length", "production": 20,
             "band": [5, 10, 20, 30, 50], "free_band": [], "resim_band": [5, 10, 30, 50],
             "sweep_levels": [], "subset_safe": False,
             "status": "UNTESTED", "type": "int", "engine_implemented": True,
             "evidence": "smc_ict.py:194; shared family knob",
             "derivation": "feeds swings -> OB detection; resim-only"},
            {"id": "P2", "producer": "_smc.ob",
             "param": "close_mitigation", "production": False,
             "band": [False, True], "free_band": [], "resim_band": [True],
             "sweep_levels": [], "subset_safe": False,
             "status": "UNTESTED", "type": "bool", "engine_implemented": True,
             "evidence": "smc_ict.py:375 (ob call); breaker P2 precedent",
             "derivation": "OB mitigation rule; resim-only"},
            {"id": "P3", "producer": "_ob_tap_scan",
             "param": "tap_window", "production": 5,
             "band": [3, 5, 10], "free_band": [], "resim_band": [],
             "sweep_levels": [], "subset_safe": False,
             "status": "NOT-ENGINE-REACHABLE", "type": "int",
             "engine_implemented": False,
             "evidence": "smc_ict.py:75 (signature default 5) BUT the call at "
                         "smc_ict.py:387 passes NO tap_window, and grep of "
                         "backtest/config.py finds no SMC_OB_TAP_WINDOW - "
                         "MEASURED S6-B2752a",
             "derivation": "the bounce-tap lookback. `engine_implemented` READ "
                           "True here until S6-B2752a measured it: there is no "
                           "env knob and no call-site plumbing, so no arm can "
                           "actuate this level and a resim_band would be a "
                           "promise the engine cannot keep (B2578 class). The "
                           "persisted key NAME hardcodes the window "
                           "(smc_ob_*_tap_recent_5d), so varying it would also "
                           "make the key lie. Plumbing ticketed S6-B2752c"},
            {"id": "P4", "producer": "gate threshold (screener)",
             "param": "rsi_threshold_long", "production": 45,
             "band": [45, 40, 35, 30], "free_band": [45, 40, 35, 30],
             "resim_band": [], "sweep_levels": [], "subset_safe": True,
             "status": "UNTESTED", "type": "int", "engine_implemented": True,
             "evidence": "strat source rsi_14<45; rsi_14 persisted numeric "
                         "(b2691 screen population carries it)",
             "derivation": "FREE: lowering the ceiling keeps a subset"},
            {"id": "P5", "producer": "gate threshold (screener)",
             "param": "rsi_threshold_short", "production": 55,
             "band": [55, 60, 65, 70], "free_band": [55, 60, 65, 70],
             "resim_band": [], "sweep_levels": [], "subset_safe": True,
             "status": "UNTESTED", "type": "int", "engine_implemented": True,
             "evidence": "strat source rsi_14>55",
             "derivation": "FREE: raising the floor keeps a subset"},
            {"id": "P6", "producer": "gate structure (screener)",
             "param": "leg", "production": "both",
             "band": ["long", "short"], "free_band": ["long", "short"],
             "resim_band": [], "sweep_levels": [], "subset_safe": True,
             "status": "UNTESTED", "type": "str", "engine_implemented": True,
             "evidence": "dual _strat3",
             "derivation": "FREE depth axis: per-leg grading"},
        ],
    },

    "pead_long_high_yoy_growth_only": {
        # B2634 (S6-B2633 Phase 0): the pead family's first inventory. NO
        # `tools` block yet - this is DELIBERATE and load-bearing: the B2578
        # launch gate refuses a spec whose family has no complete adapter
        # (fail closed, L642), so nothing can launch this family until its
        # graders exist. The pre-gate artifact for the family split is
        # output_audit/b2633_pead_pregate.json.
        #
        # ENGINE-REACHABILITY FINDING (the S6-B2569a class, found at Phase 0
        # instead of after 11 configs): BOTH engine call sites pass NO
        # parameters - signal_loader.py:238 compute_yoy_surprise_signal(
        # ticker, df, as_of) and :278 compute_pead_signals(ticker, df,
        # as_of) - so every knob below is a Python default with no env knob.
        # A resim sweep as coded would produce IDENTICAL cubes (the L387
        # class). B2686 CORRECTION (S6-B2645a, owner word 2026-09-11): TWO
        # env knobs now exist and are pinned - PEAD_DRIFT_WINDOW_DAYS
        # (reaches drift_window_days at BOTH call sites) and
        # PEAD_YOY_LONG_THRESHOLD (reaches long_threshold at :238);
        # kwargs are built only when set, so production stays
        # byte-identical unset (test_b2686_pead_env_knobs_reach_the_
        # producers). The admitted cell (drift<=20 / yoy>=0.10) is now
        # RESIM-CAPABLE; resim_band membership stays a band-review call.
        # Consequence AS ORIGINALLY WRITTEN (pre-B2686): every resim_band
        # here is EMPTY; the free
        # (tightening) levels are gradable from the cube because the
        # CONTINUOUS earnings_eps_yoy_growth and days_since_last_earnings
        # persist in signals_at_entry (verified on the R5 trade log,
        # 2,116/2,116 parsed rows carry both).
        "baseline": {"artifact": "output_r5_merged_1_7", "fires": 2116,
                     "tickers": 480, "holdout_n": 422,
                     "window": "2022-05-05..2026-05-05"},
        "gate": "within_pead_window AND yoy_surprise_high (screener.py:5041)",
        "params": [
            {"id": "P1", "producer": "pead.load_quarterly_eps",
             "param": "eps_source", "production": "polygon_financials",
             "band": ["polygon_financials"],
             "free_band": ["polygon_financials"], "resim_band": [],
             "sweep_levels": [], "subset_safe": None,
             "status": "NOT-SWEPT-BY-DESIGN", "type": "str",
             "engine_implemented": True,
             "evidence": "pead.py:75-131",
             "derivation": "data availability, not an edge knob: quarterly "
                           "diluted-else-basic EPS from data_prefetch/polygon/"
                           "financials/<T>.parquet, PIT via filing_date <= as_of"},
            {"id": "P2", "producer": "pead.load_quarterly_eps",
             "param": "quarter_filter", "production": "Q1-Q4_only",
             "band": ["Q1-Q4_only"],
             "free_band": ["Q1-Q4_only"], "resim_band": [],
             "sweep_levels": [], "subset_safe": None,
             "status": "NOT-SWEPT-BY-DESIGN", "type": "str",
             "engine_implemented": True,
             "evidence": "pead.py:115-117",
             "derivation": "structural: TTM rows are skipped so YoY compare "
                           "is well-defined per quarter"},
            {"id": "P3", "producer": "pead.compute_pead_signals",
             "param": "drift_window_days", "production": 60,
             "band": [20, 40, 60],
             "free_band": [20, 40, 60], "resim_band": [],
             "sweep_levels": [], "subset_safe": None,
             "status": "UNTESTED", "type": "int",
             "engine_implemented": True,
             "evidence": "pead.py:136 + signal_loader.py:278 (called with NO args)",
             "derivation": "TIGHTENING-ONLY band, retention MEASURED "
                           "2026-09-07 on the 2,116 R5 fires (days_since "
                           "persisted): <=20d keeps 53pct, <=40d keeps 76pct; "
                           "quartiles 6/19/40. Loosening (>60d) was struck "
                           "for lack of a knob; B2686 built the env knob "
                           "PEAD_DRIFT_WINDOW_DAYS (pinned), so >60d is now "
                           "resim-capable pending a band review"},
            {"id": "P4", "producer": "pead.compute_pead_signals",
             "param": "yoy_growth_threshold", "production": 0.0,
             "band": [0.0, 0.02, 0.05, 0.10],
             "free_band": [0.0, 0.02, 0.05, 0.10], "resim_band": [],
             "sweep_levels": [], "subset_safe": None,
             "status": "NOT-SWEPT-BY-DESIGN", "type": "float",
             "engine_implemented": True,
             "evidence": "pead.py:137",
             "derivation": "SIBLING knob (pead_long/pead_short surprise flags), "
                           "banded for the FAMILY campaign (owner 2026-09-07). "
                           "TIGHTENING-ONLY, free: continuous yoy persists on "
                           "140/140 pead_long R5 rows; retention MEASURED "
                           "2026-09-07: 0.02 keeps 94pct, 0.05 86pct, 0.10 "
                           "74pct. Loosening impossible (0.0 is the floor)"},
            {"id": "P5", "producer": "pead.compute_pead_signals",
             "param": "announcement_return_threshold", "production": 0.01,
             "band": [0.01, 0.02, 0.03, 0.05],
             "free_band": [0.01, 0.02, 0.03, 0.05], "resim_band": [],
             "sweep_levels": [], "subset_safe": None,
             "status": "NOT-SWEPT-BY-DESIGN", "type": "float",
             "engine_implemented": True,
             "evidence": "pead.py:138 (B1136 loosened 0.02 -> 0.01)",
             "derivation": "SIBLING knob, banded for the FAMILY campaign. "
                           "TIGHTENING-ONLY, free: earnings_announcement_return "
                           "persists on 140/140 pead_long rows; retention "
                           "MEASURED 2026-09-07: 0.02 keeps 76pct, 0.03 53pct, "
                           "0.05 31pct. Loosening (<0.01) has NO env knob - "
                           "struck (S6-B2569a class)"},
            {"id": "P6", "producer": "earnings_surprise_yoy.compute_yoy_surprise_signal",
             "param": "YOY_GROWTH_LONG_THRESHOLD", "production": 0.05,
             "band": [0.05, 0.10, 0.20, 0.35, 0.50],
             "free_band": [0.05, 0.10, 0.20, 0.35, 0.50], "resim_band": [],
             "sweep_levels": [], "subset_safe": None,
             "status": "UNTESTED", "type": "float",
             "engine_implemented": True,
             "evidence": "earnings_surprise_yoy.py:42 + signal_loader.py:238 (NO args)",
             "derivation": "THE strategy's primary knob. TIGHTENING-ONLY "
                           "band, retention MEASURED 2026-09-07 (continuous "
                           "earnings_eps_yoy_growth persisted on all 2,116 "
                           "fires): >=0.10 keeps 88pct, >=0.20 keeps 69pct, "
                           ">=0.35 keeps 53pct, >=0.50 keeps 44pct; yoy "
                           "quantiles 0.091/0.167/0.383/1.182/3.391 at "
                           "p10/p25/p50/p75/p90. Loosening (<0.05) has NO "
                           "env knob - struck until built"},
            {"id": "P7", "producer": "earnings_surprise_yoy.compute_yoy_surprise_signal",
             "param": "YOY_GROWTH_SHORT_THRESHOLD", "production": -0.05,
             "band": [-0.05, -0.10, -0.20, -0.35, -0.50],
             "free_band": [-0.05, -0.10, -0.20, -0.35, -0.50], "resim_band": [],
             "sweep_levels": [], "subset_safe": None,
             "status": "NOT-SWEPT-BY-DESIGN", "type": "float",
             "engine_implemented": True,
             "evidence": "earnings_surprise_yoy.py:43",
             "derivation": "short-sleeve knob, banded for the FAMILY "
                           "campaign even though the B2633 pre-gate excluded "
                           "the short cluster from campaigning (negative "
                           "holdout) - the levels are FREE, so recording them "
                           "costs nothing. TIGHTENING-ONLY: yoy persists on "
                           "2,215/2,215 short-sleeve R5 rows; retention "
                           "MEASURED 2026-09-07: -0.10 keeps 90pct, -0.20 "
                           "73pct, -0.35 53pct, -0.50 38pct (quantiles "
                           "-1.40/-0.72/-0.38/-0.19/-0.10 at p10..p90)"},
        ],
        "formula": """=============================== PRODUCER LAYER ===============================

P1  eps history  =  load_quarterly_eps(ticker): quarterly diluted-else-basic
                    EPS from data_prefetch/polygon/financials/<T>.parquet,
                    PIT via filing_date <= as_of
                    PARAMETER: eps_source = polygon_financials (fixed)

P2  quarter rows =  keep fiscal_period in {Q1..Q4}; TTM skipped
                    PARAMETER: quarter_filter = Q1-Q4_only (fixed)

P3  drift window =  days_since_last_earnings <= N  ->  within_pead_window
                    PARAMETER: drift_window_days = 60
                    (calendar-day proxy; engine call passes NO args)

P4  surprise flags (SIBLING-only): yoy > t AND ann_ret > t
                    PARAMETER: yoy_growth_threshold = 0.0

P5  surprise flags (SIBLING-only): announcement-day return leg
                    PARAMETER: announcement_return_threshold = 0.01

P6  yoy_surprise_high  =  earnings_eps_yoy_growth >= T
                    PARAMETER: YOY_GROWTH_LONG_THRESHOLD = 0.05
                    (current-quarter EPS vs same quarter prior year;
                     the CONTINUOUS yoy value persists in signals_at_entry,
                     so tighter T re-scores FREE from the cube)

P7  yoy_surprise_negative = yoy <= T   (short sleeve, excluded cluster)
                    PARAMETER: YOY_GROWTH_SHORT_THRESHOLD = -0.05

=============================== STRATEGY LAYER ===============================

fires  =  within_pead_window  AND  yoy_surprise_high     (screener.py:5041)
""",
    },
}

GATE_ORDER = ("pooled_sharpe", "profit_factor", "sortino", "psr",
              "min_trades_holdout", "min_trades_full_period")


FORMULA_SMC_OBB = (
    "=============================== PRODUCER LAYER ===============================\n\nP1  swings  =  swing_highs_lows( ohlc, swing_length = 20 )\n                   -> feeds ob(); a bar is a swing high if its high is the\n                      highest across swing_length bars BEFORE and AFTER it\n\nP2  ob      =  ob( ohlc, swings, close_mitigation = False )\n                   -> the order-block zones; close_mitigation decides\n                      whether a zone is mitigated on CLOSE or on WICK\n\nP3  tap     =  _ob_tap_scan( ob, ohlc, i, recency, tap_window = 5 )\n                   -> price RETURNING to a zone within tap_window bars.\n                      NOT ENGINE-REACHABLE: the call at smc_ict.py:387\n                      passes no tap_window and no env knob exists, so no\n                      arm can actuate a level (S6-B2752c). Inventoried\n                      here rather than omitted, because an axis left out\n                      of Table A is invisible at close (L785).\n\n============================== STRATEGY LAYER ===============================\n\nP4  long    =  smc_ob_bullish_tap_recent_5d AND rsi_14 < 45\n                                            AND price_above_ema_200\n                   -> rsi_threshold_long is FREE: lowering the ceiling\n                      keeps a strict subset of the recorded fires\n\nP5  short   =  smc_ob_bearish_tap_recent_5d AND rsi_14 > 55\n                                            AND below_ema_200\n                                            AND NOT borrow_trap\n                   -> rsi_threshold_short is FREE: raising the floor\n                      keeps a strict subset\n\nP6  leg     =  {both (production), long, short}\n                   -> FREE depth axis: per-leg grading of the same cube\n"
)


FORMULA_SMC_LSR = (
    "=============================== PRODUCER LAYER ===============================\n\nP1  swings  =  swing_highs_lows( ohlc, swing_length = 20 )\n                   -> a bar is a swing high if its high is the highest\n                      across swing_length bars BEFORE and AFTER it\n\nP2  liq     =  liquidity( ohlc, swings, range_percent = 0.01 )\n                   -> clusters swing highs/lows within range_percent of\n                      each other; a SWEEP is price taking out the cluster\n\nP3  recency =  _most_recent_event_within( <event series>, i,\n                                          event_recency_bars = 90 )\n                   -> the lookback that turns a dated event (sweep, BOS,\n                      CHoCH) into a boolean ACTIVE at bar i\n\n============================== STRATEGY LAYER ===============================\n\nlong   =  smc_liquidity_swept_dn  AND ( smc_choch_bullish OR smc_bos_bullish )\nshort  =  smc_liquidity_swept_up  AND ( smc_choch_bearish OR smc_bos_bearish )\n                                  AND NOT _short_borrow_trap_active\n"
)

# S6-B2732a (owner "Step 1 code change approved" 2026-09-12): hub-1 registered.
# MEASURED BLOCKER this closes - 1 of 22 smc consumers had a SPECS entry and it
# was the ADMITTED smc_breaker_block_long, so launch_refusals correctly refused
# hub-1 (no SPECS entry = the battery fails closed at landing AFTER the engine
# spend, S6-B2573b) while the only launchable smc strategy was the one B2731
# refuses as banked. FAMILIES is DERIVED from SPECS (run_postconfig.py:732), so
# this entry registers the battery family too.
SPECS["smc_liquidity_sweep_reversal"] = {
    "gate": ("(smc_liquidity_swept_dn) AND (smc_choch_bullish OR "
             "smc_bos_bullish)"),
    "formula": FORMULA_SMC_LSR,
    "baseline": {"artifact": "output_r5_merged_1_7", "fires": 2933,
                 "tickers": 544, "holdout_n": 570,
                 "window": "2022-05-06..2026-05-04"},
    "params": [
        {"id": "P1", "producer": "_smc.swing_highs_lows",
         "param": "swing_length", "env": "SMC_SWING_LENGTH",
         # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
         # A level is FREE only if it selects a strict SUBSET of the landed
         # fires AND its discriminating quantity is PERSISTED per trade so the
         # subset can be identified. Across ALL rows of this strategy in
         # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
         # BOOLEAN keys computed AT the production setting, and this knob's
         # discriminator is not among them - so no level is identifiable
         # offline and every one needs the engine. (P6 span looked gradable:
         # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
         # not imply price_above_ema_50, so a different span is a DIFFERENT set,
         # not a subset - evaluable is not subset-safe.) METADATA ONLY:
         # production is untouched and no run is scheduled, so no landed grade
         # is recomputed. L726 / L812 / L824.
         "free_band": [],
         "resim_band": [5, 10, 20, 30, 50],
         "consumers": ["backtest/config.py",
                       "backtest/engine/exit_strategies.py",
                       "backtest/signals/screener.py"],
         "production": 20, "type": "int", "band": [5, 10, 20, 30, 50],
         "derivation": ("library default 50, production 20; band brackets both "
                        "- SHARED with the breaker family, which is why one "
                        "variant cube serves 19 of 22 smc consumers (B2735)"),
         "subset_safe": False, "status": "UNTESTED",
         "evidence": "smc_ict.py:368", "engine_implemented": True},
        {"id": "P2", "producer": "_smc.liquidity",
         "param": "liquidity_range_pct", "env": "SMC_LIQUIDITY_RANGE_PCT",
         # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
         # A level is FREE only if it selects a strict SUBSET of the landed
         # fires AND its discriminating quantity is PERSISTED per trade so the
         # subset can be identified. Across ALL rows of this strategy in
         # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
         # BOOLEAN keys computed AT the production setting, and this knob's
         # discriminator is not among them - so no level is identifiable
         # offline and every one needs the engine. (P6 span looked gradable:
         # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
         # not imply price_above_ema_50, so a different span is a DIFFERENT set,
         # not a subset - evaluable is not subset-safe.) METADATA ONLY:
         # production is untouched and no run is scheduled, so no landed grade
         # is recomputed. L726 / L812 / L824.
         "free_band": [],
         "resim_band": [0.005, 0.01, 0.02, 0.03],
         "consumers": ["backtest/config.py", "backtest/signals/screener.py"],
         "production": 0.01, "type": "float",
         "band": [0.005, 0.01, 0.02, 0.03],
         "derivation": ("the cluster width that defines 'equal' highs/lows; "
                        "production 0.01 = 1pct. Band brackets it either side. "
                        "Reaches 7 of 22 consumers - the liquidity primitive "
                        "only (B2743)"),
         "subset_safe": False, "status": "UNTESTED",
         "evidence": "smc_ict.py:503", "engine_implemented": True},
        {"id": "P3", "producer": "_most_recent_event_within",
         "param": "event_recency_bars", "env": "SMC_EVENT_RECENCY_BARS",
         # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
         # A level is FREE only if it selects a strict SUBSET of the landed
         # fires AND its discriminating quantity is PERSISTED per trade so the
         # subset can be identified. Across ALL rows of this strategy in
         # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
         # BOOLEAN keys computed AT the production setting, and this knob's
         # discriminator is not among them - so no level is identifiable
         # offline and every one needs the engine. (P6 span looked gradable:
         # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
         # not imply price_above_ema_50, so a different span is a DIFFERENT set,
         # not a subset - evaluable is not subset-safe.) METADATA ONLY:
         # production is untouched and no run is scheduled, so no landed grade
         # is recomputed. L726 / L812 / L824.
         "free_band": [],
         "resim_band": [30, 60, 90, 120, 180],
         "consumers": ["backtest/config.py", "backtest/signals/screener.py"],
         "production": 90, "type": "int", "band": [30, 60, 90, 120, 180],
         "derivation": ("the lookback turning a dated sweep/BOS/CHoCH into an "
                        "ACTIVE boolean; production 90 per Batch 273 (a 5-bar "
                        "tail never catches an OB). Reaches the same 19 of 22 "
                        "as P1 (B2743)"),
         "subset_safe": False, "status": "UNTESTED",
         "evidence": "smc_ict.py:381,459,464,507", "engine_implemented": True},
    ],
    "tools": {
        "keys": {"P1": "swing", "P2": "liq_range", "P3": "recency"},
        # the OFFLINE combination space - leg x confirmation arm. The three
        # knobs above are FIRE-ADDING and baked into each cube by the engine,
        # so they identify a config rather than being searched inside one.
        "grid_keys": ["leg", "confirmation_arm"],
        "grade": {"script": "smc_lsr_step1.py",
                  "cube": "",                      # the DIRECTORY, not a csv
                  "flags": {"P1": "--swing-length",
                            "P2": "--liquidity-range-pct",
                            "P3": "--event-recency-bars"},
                  "extra": ["--min-n", "10"],
                  "pythonpath": ".;scripts",
                  "note": "AUTO (S6-B2732a)"},
        "free_levels": None,
        "spot_check": {"script": "spot_check_smc_lsr.py",
                       "cube": "",
                       "flags": {"P1": "--swing-length",
                                 "P2": "--liquidity-range-pct",
                                 "P3": "--event-recency-bars"},
                       "extra": ["--n", "50"],
                       "window": False, "precompute_check": False,
                       "pythonpath": ".",
                       "note": "AUTO (S6-B2732a); hub-1 has its OWN checker - "
                               "spot_check_trades.py re-derives the BREAKER "
                               "condition and produced the B2724 defect when "
                               "pointed at a strategy that does not read it"},
        "engine_anchors": {"script": "verify_engine_implemented.py"},
        "single_combination": False,
    },
}




# B2819 (S6-B2752, owner 'before' ruling + 'implement all' 2026-09-15):
# smc_equal_lows_sweep_long REGISTERED - subject 2 of 3. NO free numeric axis:
# both gate legs are persisted BOOLEANS, so Step 1 is legs x exits on the
# recorded fires (the shared smc_family_step1 grader) and depth lives in the
# producer knobs. CORRECTION to the B2752 row recorded here: this strategy IS
# swing-reachable - smc_equal_lows_swept rides the liquidity primitive, which
# takes swings (smc_ict.py:503) - the row's 'neither is swing-reachable'
# brushed it with inverse_fvg's fvg-only reach.
FORMULA_SMC_ELS = (
    "=============================== PRODUCER LAYER ===============================\n"
    "\n"
    "P1  swings  =  swing_highs_lows( ohlc, swing_length = 20 )\n"
    "                   -> swings feed the liquidity primitive, whose Swept\n"
    "                      flag is this strategy's primary key\n"
    "\n"
    "P2  liq     =  liquidity( ohlc, swings, range_percent = 0.01 )\n"
    "                   -> clusters swing lows within range_percent; the\n"
    "                      equal-lows key is a cluster's Swept flag set on a\n"
    "                      recent bar (last 20 events / 50-bar window, B390)\n"
    "\n"
    "P3  recency =  _most_recent_event_within( <fvg events>, i,\n"
    "                                          event_recency_bars = 90 )\n"
    "                   -> the recency window on the confluence leg\n"
    "                      smc_fvg_bullish_active\n"
    "\n"
    "============================== STRATEGY LAYER ===============================\n"
    "\n"
    "long   =  smc_equal_lows_swept AND smc_fvg_bullish_active\n"
    "          (both persisted booleans - NO free numeric axis; Step 1 is\n"
    "          legs x exits via the shared smc_family_step1 grader)\n")

SPECS["smc_equal_lows_sweep_long"] = {
    "gate": "smc_equal_lows_swept AND smc_fvg_bullish_active",
    "formula": FORMULA_SMC_ELS,
    "baseline": {"artifact": "output_r5_merged_1_7", "fires": 382,
                 "tickers": 544, "holdout_n": 113,
                 "window": "2022-05-06..2026-05-04"},
    "params": [
        {"id": "P1", "producer": "_smc.swing_highs_lows",
         "param": "swing_length", "env": "SMC_SWING_LENGTH",
         # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
         # A level is FREE only if it selects a strict SUBSET of the landed
         # fires AND its discriminating quantity is PERSISTED per trade so the
         # subset can be identified. Across ALL rows of this strategy in
         # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
         # BOOLEAN keys computed AT the production setting, and this knob's
         # discriminator is not among them - so no level is identifiable
         # offline and every one needs the engine. (P6 span looked gradable:
         # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
         # not imply price_above_ema_50, so a different span is a DIFFERENT set,
         # not a subset - evaluable is not subset-safe.) METADATA ONLY:
         # production is untouched and no run is scheduled, so no landed grade
         # is recomputed. L726 / L812 / L824.
         "free_band": [],
         "resim_band": [5, 10, 20, 30, 50],
         "consumers": ["backtest/config.py",
                       "backtest/engine/exit_strategies.py",
                       "backtest/signals/screener.py"],
         "production": 20, "type": "int", "band": [5, 10, 20, 30, 50],
         "derivation": ("shared family knob - swings feed liquidity, whose "
                        "Swept flag is this strategy's primary key"),
         "subset_safe": False, "status": "UNTESTED",
         "evidence": "smc_ict.py:368,503", "engine_implemented": True},
        {"id": "P2", "producer": "_smc.liquidity",
         "param": "liquidity_range_pct", "env": "SMC_LIQUIDITY_RANGE_PCT",
         # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
         # A level is FREE only if it selects a strict SUBSET of the landed
         # fires AND its discriminating quantity is PERSISTED per trade so the
         # subset can be identified. Across ALL rows of this strategy in
         # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
         # BOOLEAN keys computed AT the production setting, and this knob's
         # discriminator is not among them - so no level is identifiable
         # offline and every one needs the engine. (P6 span looked gradable:
         # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
         # not imply price_above_ema_50, so a different span is a DIFFERENT set,
         # not a subset - evaluable is not subset-safe.) METADATA ONLY:
         # production is untouched and no run is scheduled, so no landed grade
         # is recomputed. L726 / L812 / L824.
         "free_band": [],
         "resim_band": [0.005, 0.01, 0.02, 0.03],
         "consumers": ["backtest/config.py", "backtest/signals/screener.py"],
         "production": 0.01, "type": "float",
         "band": [0.005, 0.01, 0.02, 0.03],
         "derivation": ("cluster width for 'equal' lows; the hub-1 loosening "
                        "measurement (11.2b4) applies to this key family"),
         "subset_safe": False, "status": "UNTESTED",
         "evidence": "smc_ict.py:503,512", "engine_implemented": True},
        {"id": "P3", "producer": "_most_recent_event_within",
         "param": "event_recency_bars", "env": "SMC_EVENT_RECENCY_BARS",
         # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
         # A level is FREE only if it selects a strict SUBSET of the landed
         # fires AND its discriminating quantity is PERSISTED per trade so the
         # subset can be identified. Across ALL rows of this strategy in
         # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
         # BOOLEAN keys computed AT the production setting, and this knob's
         # discriminator is not among them - so no level is identifiable
         # offline and every one needs the engine. (P6 span looked gradable:
         # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
         # not imply price_above_ema_50, so a different span is a DIFFERENT set,
         # not a subset - evaluable is not subset-safe.) METADATA ONLY:
         # production is untouched and no run is scheduled, so no landed grade
         # is recomputed. L726 / L812 / L824.
         "free_band": [],
         "resim_band": [30, 60, 90, 120, 180],
         "consumers": ["backtest/config.py", "backtest/signals/screener.py"],
         "production": 90, "type": "int", "band": [30, 60, 90, 120, 180],
         "derivation": "recency window on the fvg_bullish_active confluence leg",
         "subset_safe": False, "status": "UNTESTED",
         "evidence": "smc_ict.py:381", "engine_implemented": True},
    ],
    "tools": {
        "keys": {"P1": "swing", "P2": "liq_range", "P3": "recency"},
        "grid_keys": ["leg"],
        "grade": {"script": "smc_family_step1.py", "cube": "",
                  "flags": {"P1": "--swing-length",
                            "P2": "--liquidity-range-pct",
                            "P3": "--event-recency-bars"},
                  "extra": ["--strategy", "smc_equal_lows_sweep_long",
                            "--min-n", "10"],
                  "pythonpath": ".;scripts",
                  "note": "AUTO (S6-B2752/B2819); shared no-free-axis grader"},
        "free_levels": None,
        "spot_check": {"script": "spot_check_smc_family.py", "cube": "",
                       "flags": {"P1": "--swing-length",
                                 "P2": "--liquidity-range-pct",
                                 "P3": "--event-recency-bars"},
                       "extra": ["--strategy", "smc_equal_lows_sweep_long",
                                 "--n", "50"],
                       "window": False, "precompute_check": False,
                       "pythonpath": ".",
                       "note": "AUTO (B2819); LEG A fully sighted - every "
                               "gate key persists"},
        "engine_anchors": {"script": "verify_engine_implemented.py"},
        "single_combination": False,
    },
}


# B2820 (S6-B2752): smc_inverse_fvg REGISTERED - subject 3 of 3, closing the
# owner's 'before' ruling. THE HONEST KNOB SET IS ONE: the inverse-fvg keys
# are derived from _smc.fvg(ohlc) with NO parameter, a hardcoded 20-event
# tail and a hardcoded 0.20 zone tolerance (smc_ict.py:296-360 READ this
# batch) - none of SMC_SWING_LENGTH / SMC_LIQUIDITY_RANGE_PCT /
# SMC_EVENT_RECENCY_BARS reaches them, and declaring them would be the
# S6-B2136 manifest lie. The one engine lever is the trend legs' span
# (STRAT_EMA_SPAN, the breaker's P6 pattern); the FVG internals are a
# candidate future lever, recorded as such rather than invented as knobs.
FORMULA_SMC_IFVG = (
    "=============================== PRODUCER LAYER ===============================\n"
    "\n"
    "P1  span    =  price_above_ema_{STRAT_EMA_SPAN} / below_ema_{span}\n"
    "                   -> the trend leg reads the CONFIGURED span (B1519);\n"
    "                      default 200 reproduces production exactly\n"
    "\n"
    "fvg (NO KNOB) =  fvg( ohlc )  - takes no parameters (smc_ict.py:298);\n"
    "                   inverse keys derive from MITIGATED FVGs with price\n"
    "                   beyond the flipped zone, over a hardcoded 20-event\n"
    "                   tail with hardcoded 0.20 tolerance (B1137)\n"
    "\n"
    "============================== STRATEGY LAYER ===============================\n"
    "\n"
    "long   =  smc_inverse_fvg_bullish AND price_above_ema_{span}\n"
    "short  =  smc_inverse_fvg_bearish AND below_ema_200 AND borrow_ok\n"
    "          (all persisted booleans - NO free numeric axis; Step 1 is\n"
    "          legs x exits via the shared smc_family_step1 grader)\n")

SPECS["smc_inverse_fvg"] = {
    "gate": ("long: smc_inverse_fvg_bullish AND price_above_ema_{span} | "
             "short: smc_inverse_fvg_bearish AND below_ema_200 AND borrow_ok"),
    "formula": FORMULA_SMC_IFVG,
    "baseline": {"artifact": "output_r5_merged_1_7", "fires": 953,
                 "tickers": 544, "holdout_n": 231,
                 "window": "2022-05-06..2026-05-04"},
    "params": [
        {"id": "P1", "producer": "ema trend leg (screener)",
         "param": "span", "env": "STRAT_EMA_SPAN",
         # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
         # A level is FREE only if it selects a strict SUBSET of the landed
         # fires AND its discriminating quantity is PERSISTED per trade so the
         # subset can be identified. Across ALL rows of this strategy in
         # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
         # BOOLEAN keys computed AT the production setting, and this knob's
         # discriminator is not among them - so no level is identifiable
         # offline and every one needs the engine. (P6 span looked gradable:
         # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
         # not imply price_above_ema_50, so a different span is a DIFFERENT set,
         # not a subset - evaluable is not subset-safe.) METADATA ONLY:
         # production is untouched and no run is scheduled, so no landed grade
         # is recomputed. L726 / L812 / L824.
         "free_band": [],
         "resim_band": [9, 20, 21, 50, 200],
         "consumers": ["backtest/config.py",
                       "backtest/engine/exit_strategies.py",
                       "backtest/signals/screener.py"],
         "production": 200, "type": "int", "band": [9, 20, 21, 50, 200],
         "derivation": ("the ONLY engine knob reaching this gate - the fvg "
                        "internals take no parameters (smc_ict.py:296-360); "
                        "the emitted spans are the breaker P6 set"),
         "subset_safe": False, "status": "UNTESTED",
         "evidence": "screener.py strat_smc_inverse_fvg; smc_ict.py:298",
         "engine_implemented": True},
    ],
    "tools": {
        "keys": {"P1": "span"},
        "grid_keys": ["leg"],
        "grade": {"script": "smc_family_step1.py", "cube": "",
                  "flags": {},
                  "extra": ["--strategy", "smc_inverse_fvg", "--min-n", "10"],
                  "pythonpath": ".;scripts",
                  "note": "AUTO (B2820); shared no-free-axis grader; the smc "
                          "knob flags are inapplicable - fvg takes none"},
        "free_levels": None,
        "spot_check": {"script": "spot_check_smc_family.py", "cube": "",
                       "flags": {},
                       "extra": ["--strategy", "smc_inverse_fvg", "--n", "50"],
                       "window": False, "precompute_check": False,
                       "pythonpath": ".",
                       "note": "AUTO (B2820); LEG A fully sighted; knob flags "
                               "default to production - the keys are "
                               "knob-independent"},
        "engine_anchors": {"script": "verify_engine_implemented.py"},
        "single_combination": False,
    },
}


# B2816 (S6-B2703, owner-ruled schedule-later 2026-09-15): Table-A depth
# inventories for the 9 admitted strategies whose depth was never searched
# (8 institutional + xs_low_beta; top_decile is depth-done via its own
# B2667 grid, breaker + icg via engine resim, the pead pair via the
# offline env-knob route). INVENTORY ONLY: no tools block, so the
# B2578/B2579 launch gates keep refusing these families - fail closed,
# the pead precedent. Bands are CANDIDATES; scheduling needs the owner's
# band word (11.2c). Admitted lines stay BANKED (B2731).
SPECS_PHASE0.update({'institutional_oversold_long': {'gate': 'institutional_buy AND rsi_14 < 40 '
                                         'AND price_above_ema_200',
                                 'baseline': {'artifact': 'output_r5_merged_1_7',
                                              'fires': 386,
                                              'admitted_via': 'output_audit/b2664_inst_admission_grid.json'},
                                 'status': 'DEPTH-NOT-RUN (S6-B2703); depth '
                                           'SCHEDULE-LATER by owner ruling '
                                           '2026-09-15 (B2810 audit rec 1 '
                                           'approved); admitted line BANKED '
                                           '(B2731); band is CANDIDATE only, '
                                           'sweep needs its own owner band '
                                           'word (11.2c)',
                                 'shared_family': 'INST_* producer knobs are '
                                                  'FAMILY-SHARED and '
                                                  'inventoried on '
                                                  "SPECS['institutional_committed_growth_long'] "
                                                  '(9 params, per-level '
                                                  'free/resim bands; '
                                                  'run-producers-once B2633)',
                                 'params': [{'id': 'P1',
                                             'producer': 'gate threshold '
                                                         '(screener)',
                                             'param': 'rsi_threshold',
                                             'production': 40,
                                             'band': [40, 35, 30],
                                             'sweep_levels': [],
                                             'subset_safe': None,
                                             'status': 'UNSCHEDULED',
                                             'type': 'int',
                                             'engine_implemented': True,
                                             'evidence': 'screener.py strat '
                                                         'source, read B2816',
                                             'derivation': 'tightening the '
                                                           'oversold ceiling '
                                                           'keeps a subset; '
                                                           'rsi_14 '
                                                           'persisted. depth '
                                                           'SCHEDULE-LATER '
                                                           'by owner ruling '
                                                           '2026-09-15 '
                                                           '(B2810 audit rec '
                                                           '1 approved); '
                                                           'admitted line '
                                                           'BANKED (B2731); '
                                                           'band is '
                                                           'CANDIDATE only, '
                                                           'sweep needs its '
                                                           'own owner band '
                                                           'word (11.2c)'}]},
 'institutional_breakout_confirmation_long': {'gate': 'institutional_buy AND '
                                                      'resistance_break_retest '
                                                      'AND '
                                                      'price_above_ema_200 '
                                                      'AND close_above_open',
                                              'baseline': {'artifact': 'output_r5_merged_1_7',
                                                           'fires': 642,
                                                           'admitted_via': 'output_audit/b2664_inst_admission_grid.json'},
                                              'status': 'DEPTH-NOT-RUN '
                                                        '(S6-B2703); depth '
                                                        'SCHEDULE-LATER by '
                                                        'owner ruling '
                                                        '2026-09-15 (B2810 '
                                                        'audit rec 1 '
                                                        'approved); admitted '
                                                        'line BANKED '
                                                        '(B2731); band is '
                                                        'CANDIDATE only, '
                                                        'sweep needs its own '
                                                        'owner band word '
                                                        '(11.2c)',
                                              'shared_family': 'INST_* '
                                                               'producer '
                                                               'knobs are '
                                                               'FAMILY-SHARED '
                                                               'and '
                                                               'inventoried '
                                                               'on '
                                                               "SPECS['institutional_committed_growth_long'] "
                                                               '(9 params, '
                                                               'per-level '
                                                               'free/resim '
                                                               'bands; '
                                                               'run-producers-once '
                                                               'B2633)',
                                              'params': [],
                                              'no_gate_knob': 'all four gate '
                                                              'legs are '
                                                              'booleans - '
                                                              'depth here is '
                                                              'the shared '
                                                              'producer '
                                                              'family only; '
                                                              'no '
                                                              'per-strategy '
                                                              'numeric knob '
                                                              'exists'},
 'institutional_persistence_oversold_long': {'gate': 'institutional_increased '
                                                     '>= 3 AND rsi_14 < 45 '
                                                     'AND '
                                                     'price_above_ema_200',
                                             'baseline': {'artifact': 'output_r5_merged_1_7',
                                                          'fires': 716,
                                                          'admitted_via': 'output_audit/b2664_inst_admission_grid.json'},
                                             'status': 'DEPTH-NOT-RUN '
                                                       '(S6-B2703); depth '
                                                       'SCHEDULE-LATER by '
                                                       'owner ruling '
                                                       '2026-09-15 (B2810 '
                                                       'audit rec 1 '
                                                       'approved); admitted '
                                                       'line BANKED (B2731); '
                                                       'band is CANDIDATE '
                                                       'only, sweep needs '
                                                       'its own owner band '
                                                       'word (11.2c)',
                                             'shared_family': 'INST_* '
                                                              'producer '
                                                              'knobs are '
                                                              'FAMILY-SHARED '
                                                              'and '
                                                              'inventoried '
                                                              'on '
                                                              "SPECS['institutional_committed_growth_long'] "
                                                              '(9 params, '
                                                              'per-level '
                                                              'free/resim '
                                                              'bands; '
                                                              'run-producers-once '
                                                              'B2633)',
                                             'params': [{'id': 'P1',
                                                         'producer': 'gate '
                                                                     'threshold '
                                                                     '(screener)',
                                                         'param': 'institutional_increased_min',
                                                         'production': 3,
                                                         'band': [3, 4, 5],
                                                         'sweep_levels': [],
                                                         'subset_safe': None,
                                                         'status': 'UNSCHEDULED',
                                                         'type': 'int',
                                                         'engine_implemented': True,
                                                         'evidence': 'screener.py '
                                                                     'strat '
                                                                     'source, '
                                                                     'read '
                                                                     'B2816',
                                                         'derivation': 'raising '
                                                                       'the '
                                                                       'floor '
                                                                       'keeps '
                                                                       'a '
                                                                       'subset; '
                                                                       'count '
                                                                       'persisted. '
                                                                       'depth '
                                                                       'SCHEDULE-LATER '
                                                                       'by '
                                                                       'owner '
                                                                       'ruling '
                                                                       '2026-09-15 '
                                                                       '(B2810 '
                                                                       'audit '
                                                                       'rec '
                                                                       '1 '
                                                                       'approved); '
                                                                       'admitted '
                                                                       'line '
                                                                       'BANKED '
                                                                       '(B2731); '
                                                                       'band '
                                                                       'is '
                                                                       'CANDIDATE '
                                                                       'only, '
                                                                       'sweep '
                                                                       'needs '
                                                                       'its '
                                                                       'own '
                                                                       'owner '
                                                                       'band '
                                                                       'word '
                                                                       '(11.2c)'},
                                                        {'id': 'P2',
                                                         'producer': 'gate '
                                                                     'threshold '
                                                                     '(screener)',
                                                         'param': 'rsi_threshold',
                                                         'production': 45,
                                                         'band': [45, 40, 35],
                                                         'sweep_levels': [],
                                                         'subset_safe': None,
                                                         'status': 'UNSCHEDULED',
                                                         'type': 'int',
                                                         'engine_implemented': True,
                                                         'evidence': 'screener.py '
                                                                     'strat '
                                                                     'source, '
                                                                     'read '
                                                                     'B2816',
                                                         'derivation': 'tightening '
                                                                       'the '
                                                                       'ceiling '
                                                                       'keeps '
                                                                       'a '
                                                                       'subset. '
                                                                       'depth '
                                                                       'SCHEDULE-LATER '
                                                                       'by '
                                                                       'owner '
                                                                       'ruling '
                                                                       '2026-09-15 '
                                                                       '(B2810 '
                                                                       'audit '
                                                                       'rec '
                                                                       '1 '
                                                                       'approved); '
                                                                       'admitted '
                                                                       'line '
                                                                       'BANKED '
                                                                       '(B2731); '
                                                                       'band '
                                                                       'is '
                                                                       'CANDIDATE '
                                                                       'only, '
                                                                       'sweep '
                                                                       'needs '
                                                                       'its '
                                                                       'own '
                                                                       'owner '
                                                                       'band '
                                                                       'word '
                                                                       '(11.2c)'}]},
 'institutional_recent_init_momentum_long': {'gate': 'institutional_new_positions '
                                                     '>= 2 AND '
                                                     'macd_12_26_9_bullish '
                                                     'AND '
                                                     '(price_above_ema_200 '
                                                     'OR price_above_ema_50)',
                                             'baseline': {'artifact': 'output_r5_merged_1_7',
                                                          'fires': 2268,
                                                          'admitted_via': 'output_audit/b2664_inst_admission_grid.json'},
                                             'status': 'DEPTH-NOT-RUN '
                                                       '(S6-B2703); depth '
                                                       'SCHEDULE-LATER by '
                                                       'owner ruling '
                                                       '2026-09-15 (B2810 '
                                                       'audit rec 1 '
                                                       'approved); admitted '
                                                       'line BANKED (B2731); '
                                                       'band is CANDIDATE '
                                                       'only, sweep needs '
                                                       'its own owner band '
                                                       'word (11.2c)',
                                             'shared_family': 'INST_* '
                                                              'producer '
                                                              'knobs are '
                                                              'FAMILY-SHARED '
                                                              'and '
                                                              'inventoried '
                                                              'on '
                                                              "SPECS['institutional_committed_growth_long'] "
                                                              '(9 params, '
                                                              'per-level '
                                                              'free/resim '
                                                              'bands; '
                                                              'run-producers-once '
                                                              'B2633)',
                                             'params': [{'id': 'P1',
                                                         'producer': 'gate '
                                                                     'threshold '
                                                                     '(screener)',
                                                         'param': 'new_positions_min',
                                                         'production': 2,
                                                         'band': [2, 3, 4],
                                                         'sweep_levels': [],
                                                         'subset_safe': None,
                                                         'status': 'UNSCHEDULED',
                                                         'type': 'int',
                                                         'engine_implemented': True,
                                                         'evidence': 'screener.py '
                                                                     'strat '
                                                                     'source, '
                                                                     'read '
                                                                     'B2816',
                                                         'derivation': 'raising '
                                                                       'the '
                                                                       'floor '
                                                                       'keeps '
                                                                       'a '
                                                                       'subset; '
                                                                       'count '
                                                                       'persisted. '
                                                                       'depth '
                                                                       'SCHEDULE-LATER '
                                                                       'by '
                                                                       'owner '
                                                                       'ruling '
                                                                       '2026-09-15 '
                                                                       '(B2810 '
                                                                       'audit '
                                                                       'rec '
                                                                       '1 '
                                                                       'approved); '
                                                                       'admitted '
                                                                       'line '
                                                                       'BANKED '
                                                                       '(B2731); '
                                                                       'band '
                                                                       'is '
                                                                       'CANDIDATE '
                                                                       'only, '
                                                                       'sweep '
                                                                       'needs '
                                                                       'its '
                                                                       'own '
                                                                       'owner '
                                                                       'band '
                                                                       'word '
                                                                       '(11.2c)'}]},
 'institutional_recent_init_volume_long': {'gate': 'institutional_new_positions '
                                                   '>= 2 AND vol_above_avg '
                                                   'AND price_above_ema_50',
                                           'baseline': {'artifact': 'output_r5_merged_1_7',
                                                        'fires': 1075,
                                                        'admitted_via': 'output_audit/b2664_inst_admission_grid.json'},
                                           'status': 'DEPTH-NOT-RUN '
                                                     '(S6-B2703); depth '
                                                     'SCHEDULE-LATER by '
                                                     'owner ruling '
                                                     '2026-09-15 (B2810 '
                                                     'audit rec 1 approved); '
                                                     'admitted line BANKED '
                                                     '(B2731); band is '
                                                     'CANDIDATE only, sweep '
                                                     'needs its own owner '
                                                     'band word (11.2c)',
                                           'shared_family': 'INST_* producer '
                                                            'knobs are '
                                                            'FAMILY-SHARED '
                                                            'and inventoried '
                                                            'on '
                                                            "SPECS['institutional_committed_growth_long'] "
                                                            '(9 params, '
                                                            'per-level '
                                                            'free/resim '
                                                            'bands; '
                                                            'run-producers-once '
                                                            'B2633)',
                                           'params': [{'id': 'P1',
                                                       'producer': 'gate '
                                                                   'threshold '
                                                                   '(screener)',
                                                       'param': 'new_positions_min',
                                                       'production': 2,
                                                       'band': [2, 3, 4],
                                                       'sweep_levels': [],
                                                       'subset_safe': None,
                                                       'status': 'UNSCHEDULED',
                                                       'type': 'int',
                                                       'engine_implemented': True,
                                                       'evidence': 'screener.py '
                                                                   'strat '
                                                                   'source, '
                                                                   'read '
                                                                   'B2816',
                                                       'derivation': 'raising '
                                                                     'the '
                                                                     'floor '
                                                                     'keeps '
                                                                     'a '
                                                                     'subset. '
                                                                     'depth '
                                                                     'SCHEDULE-LATER '
                                                                     'by '
                                                                     'owner '
                                                                     'ruling '
                                                                     '2026-09-15 '
                                                                     '(B2810 '
                                                                     'audit '
                                                                     'rec 1 '
                                                                     'approved); '
                                                                     'admitted '
                                                                     'line '
                                                                     'BANKED '
                                                                     '(B2731); '
                                                                     'band '
                                                                     'is '
                                                                     'CANDIDATE '
                                                                     'only, '
                                                                     'sweep '
                                                                     'needs '
                                                                     'its '
                                                                     'own '
                                                                     'owner '
                                                                     'band '
                                                                     'word '
                                                                     '(11.2c)'}]},
 'institutional_multi_quarter_persistence_long': {'gate': 'persistent_holders_4q '
                                                          '>= 5 AND '
                                                          'price_above_ema_200',
                                                  'baseline': {'artifact': 'output_r5_merged_1_7',
                                                               'fires': 2516,
                                                               'admitted_via': 'output_audit/b2664_inst_admission_grid.json'},
                                                  'status': 'DEPTH-NOT-RUN '
                                                            '(S6-B2703); '
                                                            'depth '
                                                            'SCHEDULE-LATER '
                                                            'by owner ruling '
                                                            '2026-09-15 '
                                                            '(B2810 audit '
                                                            'rec 1 '
                                                            'approved); '
                                                            'admitted line '
                                                            'BANKED (B2731); '
                                                            'band is '
                                                            'CANDIDATE only, '
                                                            'sweep needs its '
                                                            'own owner band '
                                                            'word (11.2c)',
                                                  'shared_family': 'INST_* '
                                                                   'producer '
                                                                   'knobs '
                                                                   'are '
                                                                   'FAMILY-SHARED '
                                                                   'and '
                                                                   'inventoried '
                                                                   'on '
                                                                   "SPECS['institutional_committed_growth_long'] "
                                                                   '(9 '
                                                                   'params, '
                                                                   'per-level '
                                                                   'free/resim '
                                                                   'bands; '
                                                                   'run-producers-once '
                                                                   'B2633)',
                                                  'params': [{'id': 'P1',
                                                              'producer': 'gate '
                                                                          'threshold '
                                                                          '(screener)',
                                                              'param': 'persistent_holders_min',
                                                              'production': 5,
                                                              'band': [5,
                                                                       6,
                                                                       8],
                                                              'sweep_levels': [],
                                                              'subset_safe': None,
                                                              'status': 'UNSCHEDULED',
                                                              'type': 'int',
                                                              'engine_implemented': True,
                                                              'evidence': 'screener.py '
                                                                          'strat '
                                                                          'source, '
                                                                          'read '
                                                                          'B2816',
                                                              'derivation': 'raising '
                                                                            'the '
                                                                            'floor '
                                                                            'keeps '
                                                                            'a '
                                                                            'subset; '
                                                                            'count '
                                                                            'persisted. '
                                                                            'depth '
                                                                            'SCHEDULE-LATER '
                                                                            'by '
                                                                            'owner '
                                                                            'ruling '
                                                                            '2026-09-15 '
                                                                            '(B2810 '
                                                                            'audit '
                                                                            'rec '
                                                                            '1 '
                                                                            'approved); '
                                                                            'admitted '
                                                                            'line '
                                                                            'BANKED '
                                                                            '(B2731); '
                                                                            'band '
                                                                            'is '
                                                                            'CANDIDATE '
                                                                            'only, '
                                                                            'sweep '
                                                                            'needs '
                                                                            'its '
                                                                            'own '
                                                                            'owner '
                                                                            'band '
                                                                            'word '
                                                                            '(11.2c)'}]},
 'institutional_strong_conviction_long': {'gate': 'institutional_increased '
                                                  '>= 5 AND '
                                                  'institutional_new_positions '
                                                  '>= 2 AND '
                                                  'price_above_ema_200',
                                          'baseline': {'artifact': 'output_r5_merged_1_7',
                                                       'fires': 1826,
                                                       'admitted_via': 'output_audit/b2664_inst_admission_grid.json'},
                                          'status': 'DEPTH-NOT-RUN '
                                                    '(S6-B2703); depth '
                                                    'SCHEDULE-LATER by owner '
                                                    'ruling 2026-09-15 '
                                                    '(B2810 audit rec 1 '
                                                    'approved); admitted '
                                                    'line BANKED (B2731); '
                                                    'band is CANDIDATE only, '
                                                    'sweep needs its own '
                                                    'owner band word (11.2c)',
                                          'shared_family': 'INST_* producer '
                                                           'knobs are '
                                                           'FAMILY-SHARED '
                                                           'and inventoried '
                                                           'on '
                                                           "SPECS['institutional_committed_growth_long'] "
                                                           '(9 params, '
                                                           'per-level '
                                                           'free/resim '
                                                           'bands; '
                                                           'run-producers-once '
                                                           'B2633)',
                                          'params': [{'id': 'P1',
                                                      'producer': 'gate '
                                                                  'threshold '
                                                                  '(screener)',
                                                      'param': 'increased_min',
                                                      'production': 5,
                                                      'band': [5, 6, 8],
                                                      'sweep_levels': [],
                                                      'subset_safe': None,
                                                      'status': 'UNSCHEDULED',
                                                      'type': 'int',
                                                      'engine_implemented': True,
                                                      'evidence': 'screener.py '
                                                                  'strat '
                                                                  'source, '
                                                                  'read '
                                                                  'B2816',
                                                      'derivation': 'raising '
                                                                    'the '
                                                                    'floor '
                                                                    'keeps a '
                                                                    'subset. '
                                                                    'depth '
                                                                    'SCHEDULE-LATER '
                                                                    'by '
                                                                    'owner '
                                                                    'ruling '
                                                                    '2026-09-15 '
                                                                    '(B2810 '
                                                                    'audit '
                                                                    'rec 1 '
                                                                    'approved); '
                                                                    'admitted '
                                                                    'line '
                                                                    'BANKED '
                                                                    '(B2731); '
                                                                    'band is '
                                                                    'CANDIDATE '
                                                                    'only, '
                                                                    'sweep '
                                                                    'needs '
                                                                    'its own '
                                                                    'owner '
                                                                    'band '
                                                                    'word '
                                                                    '(11.2c)'},
                                                     {'id': 'P2',
                                                      'producer': 'gate '
                                                                  'threshold '
                                                                  '(screener)',
                                                      'param': 'new_positions_min',
                                                      'production': 2,
                                                      'band': [2, 3],
                                                      'sweep_levels': [],
                                                      'subset_safe': None,
                                                      'status': 'UNSCHEDULED',
                                                      'type': 'int',
                                                      'engine_implemented': True,
                                                      'evidence': 'screener.py '
                                                                  'strat '
                                                                  'source, '
                                                                  'read '
                                                                  'B2816',
                                                      'derivation': 'raising '
                                                                    'the '
                                                                    'floor '
                                                                    'keeps a '
                                                                    'subset. '
                                                                    'depth '
                                                                    'SCHEDULE-LATER '
                                                                    'by '
                                                                    'owner '
                                                                    'ruling '
                                                                    '2026-09-15 '
                                                                    '(B2810 '
                                                                    'audit '
                                                                    'rec 1 '
                                                                    'approved); '
                                                                    'admitted '
                                                                    'line '
                                                                    'BANKED '
                                                                    '(B2731); '
                                                                    'band is '
                                                                    'CANDIDATE '
                                                                    'only, '
                                                                    'sweep '
                                                                    'needs '
                                                                    'its own '
                                                                    'owner '
                                                                    'band '
                                                                    'word '
                                                                    '(11.2c)'}]},
 'institutional_high_conviction_long': {'gate': 'institutional_new_positions '
                                                '>= 3 AND price_above_ema_50',
                                        'baseline': {'artifact': 'output_r5_merged_1_7',
                                                     'fires': 2473,
                                                     'admitted_via': 'output_audit/b2664_inst_admission_grid.json'},
                                        'status': 'DEPTH-NOT-RUN (S6-B2703); '
                                                  'depth SCHEDULE-LATER by '
                                                  'owner ruling 2026-09-15 '
                                                  '(B2810 audit rec 1 '
                                                  'approved); admitted line '
                                                  'BANKED (B2731); band is '
                                                  'CANDIDATE only, sweep '
                                                  'needs its own owner band '
                                                  'word (11.2c)',
                                        'shared_family': 'INST_* producer '
                                                         'knobs are '
                                                         'FAMILY-SHARED and '
                                                         'inventoried on '
                                                         "SPECS['institutional_committed_growth_long'] "
                                                         '(9 params, '
                                                         'per-level '
                                                         'free/resim bands; '
                                                         'run-producers-once '
                                                         'B2633)',
                                        'params': [{'id': 'P1',
                                                    'producer': 'gate '
                                                                'threshold '
                                                                '(screener)',
                                                    'param': 'new_positions_min',
                                                    'production': 3,
                                                    'band': [3, 4, 5],
                                                    'sweep_levels': [],
                                                    'subset_safe': None,
                                                    'status': 'UNSCHEDULED',
                                                    'type': 'int',
                                                    'engine_implemented': True,
                                                    'evidence': 'screener.py '
                                                                'strat '
                                                                'source, '
                                                                'read B2816',
                                                    'derivation': 'raising '
                                                                  'the floor '
                                                                  'keeps a '
                                                                  'subset. '
                                                                  'depth '
                                                                  'SCHEDULE-LATER '
                                                                  'by owner '
                                                                  'ruling '
                                                                  '2026-09-15 '
                                                                  '(B2810 '
                                                                  'audit rec '
                                                                  '1 '
                                                                  'approved); '
                                                                  'admitted '
                                                                  'line '
                                                                  'BANKED '
                                                                  '(B2731); '
                                                                  'band is '
                                                                  'CANDIDATE '
                                                                  'only, '
                                                                  'sweep '
                                                                  'needs its '
                                                                  'own owner '
                                                                  'band word '
                                                                  '(11.2c)'}]},
 'xs_low_beta_with_smart_money_long': {'gate': 'xs_low_beta_top_quintile AND '
                                               'price_above_ema_200 AND '
                                               '_has_smart_money_buy(s) AND '
                                               'pair_half_life >= 6.55',
                                       'baseline': {'artifact': 'output_r5_merged_1_7',
                                                    'fires': 452,
                                                    'admitted_via': 'output_audit/b2685_xslowbeta_admission_grid.json'},
                                       'status': 'DEPTH-NOT-RUN (S6-B2703; '
                                                 'admitted at its BASELINE '
                                                 'ts10 line, B2685 - no knob '
                                                 'was ever searched); depth '
                                                 'SCHEDULE-LATER by owner '
                                                 'ruling 2026-09-15 (B2810 '
                                                 'audit rec 1 approved); '
                                                 'admitted line BANKED '
                                                 '(B2731); band is CANDIDATE '
                                                 'only, sweep needs its own '
                                                 'owner band word (11.2c)',
                                       'shared_family': 'factor producer '
                                                        '(xs_low_beta '
                                                        'quintile) + '
                                                        'smart-money helper; '
                                                        'no INST_* family '
                                                        'reference',
                                       'params': [{'id': 'P1',
                                                   'producer': 'gate '
                                                               'threshold '
                                                               '(screener)',
                                                   'param': 'pair_half_life_min',
                                                   'production': 6.55,
                                                   'band': [6.55, 8.0, 10.0],
                                                   'sweep_levels': [],
                                                   'subset_safe': None,
                                                   'status': 'UNSCHEDULED',
                                                   'type': 'float',
                                                   'engine_implemented': True,
                                                   'evidence': 'screener.py '
                                                               'strat '
                                                               'source, read '
                                                               'B2816',
                                                   'derivation': 'raising '
                                                                 'the floor '
                                                                 'keeps a '
                                                                 'subset; '
                                                                 'the 6.55 '
                                                                 'is the '
                                                                 'B2678-era '
                                                                 'companion '
                                                                 'knob on '
                                                                 'the '
                                                                 'admitted '
                                                                 'line. '
                                                                 'depth '
                                                                 'SCHEDULE-LATER '
                                                                 'by owner '
                                                                 'ruling '
                                                                 '2026-09-15 '
                                                                 '(B2810 '
                                                                 'audit rec '
                                                                 '1 '
                                                                 'approved); '
                                                                 'admitted '
                                                                 'line '
                                                                 'BANKED '
                                                                 '(B2731); '
                                                                 'band is '
                                                                 'CANDIDATE '
                                                                 'only, '
                                                                 'sweep '
                                                                 'needs its '
                                                                 'own owner '
                                                                 'band word '
                                                                 '(11.2c)'}]}})



# ---------------------------------------------------------------------------
# B2850 (owner word "do SPECS + the 0.5 smoke" 2026-09-17): the candle pair.
# Producer anatomy knobs are DEFINED in strategy_optimisation Table A with
# candidate bands but have NO env actuators yet - so each SPECS band here is
# PRODUCTION-ONLY (validate_spec S6-B2569a: a resim level beyond production
# without an env knob is unrunnable and refused); candidates live in the
# derivation text until actuators are built. The rsi_14 free band carries the
# MEASURED tighter quantile levels from the Table A build. 0.5 smoke
# (output_audit/b2850_candle_step05_smoke.json, 6 megacaps, 4y): soldiers
# pattern 479 / gate 199; crows pattern 302 / gate 165 (upper bound - the
# borrow leg is data-dependent, unevaluated in the smoke).
# ---------------------------------------------------------------------------

FORMULA_TWS = (
    "=============================== PRODUCER LAYER ===============================\n"
    "\n"
    "P1  pattern  =  three_white_soldiers (compute_candle_signals,\n"
    "                technical.py:2104-2107): three consecutive bullish\n"
    "                bodies, each close and open above the prior bar\n"
    "                   -> strict inequalities; anatomy knobs P2-P4 are the\n"
    "                      implicit magnitudes (all zero/absent today)\n"
    "\n"
    "P2  n_bars                = 3     (band [3, 4]; env CANDLE_N_BARS)\n"
    "P3  min_body_pct_of_range = 0.0   (band [0, 0.3, 0.5]; env CANDLE_MIN_BODY_PCT)\n"
    "P4  min_step_up_pct       = 0.0   (band [0, 0.1, 0.25]; env CANDLE_MIN_STEP_PCT)\n"
    "P5  max_upper_wick_pct    = None  (band [None, 0.3, 0.2]; env CANDLE_MAX_WICK_PCT)\n"
    "\n"
    "============================== STRATEGY LAYER ===============================\n"
    "\n"
    "P6  long  =  three_white_soldiers AND rsi_14 < 60\n"
    "             (rsi_14 TIGHTER = LOWER the ceiling: free levels are the\n"
    "              measured retention quantiles on the 1,596 R5 fires)\n")

SPECS["three_white_soldiers"] = {  # B2897 (owner ruling 2026-09-20 "Candle goes first"): PROMOTED from SPECS_PHASE0 to SPECS. It is no longer pre-engine inventory - the 54-config anatomy campaign runs, so the battery adapter is owed NOW. Moved, never copied: the two names that sit in BOTH registries carry tools={} in PHASE0 and a complete block in SPECS, so duplication is what makes a family droppable.
    "gate": "three_white_soldiers AND rsi_14 < 60",
    "formula": FORMULA_TWS,
    "baseline": {"artifact": "output_r5_merged_1_7", "fires": 1596,
                 "tickers": 544, "holdout_n": 321,
                 "window": "2022-05-05..2026-04-28"},
    "params": [
        {"id": "P1", "producer": "compute_candle_signals",
         "param": "three_white_soldiers (boolean leg)", "env": None,
         "consumers": ["backtest/signals/screener.py"],
         "production": True, "type": "bool", "band": [True],
         "free_band": [], "resim_band": [True],
         "derivation": "the pattern leg itself; its magnitudes are P2-P4",
         "subset_safe": False,
         "status": "SMOKED-0.5 (479 pattern fires, 6 megacaps 4y)",
         "evidence": "technical.py:2104-2107", "engine_implemented": True},
        {"id": "P2", "producer": "compute_candles",
         "param": "n_bars (pattern length)", "env": "CANDLE_N_BARS", "cfg_key": "P2_n_bars",
         "consumers": ["backtest/config.py", "backtest/signals/technical.py",
                           "scripts/spot_check_candle.py"],
         "production": 3, "type": "int", "band": [3, 4],
         "free_band": [], "resim_band": [3, 4],
         "sweep_levels": [],
         "sweep_skip_reason": ("n_bars stays at production 3. Level 4 clears the holdout floor in only 4 of 27 cel"
                               "ls on EACH leg (B2937 feasibility) - rare by construction, not bad luck. DEPRIORIT"
                               "ISED not rejected; the count is a LOWER bound (L812) so it returns if the occupanc"
                               "y correction proves large"),
         "derivation": ("CANON Nison 1991 three; 4 the strict extension. "
                        "B2865: ACTUATED - the literal range(1,4) became a "
                        "knob; measured bite 1175 -> 466 soldiers fires on "
                        "25 tickers x 600 bars"),
         "subset_safe": False, "status": "ACTUATED-B2865",
         "evidence": "technical.py five-bar block; config.py CANDLE_N_BARS",
         "engine_implemented": True},
        {"id": "P3", "producer": "compute_candles",
         "param": "min_body_pct_of_range", "env": "CANDLE_MIN_BODY_PCT", "cfg_key": "P3_min_body_pct",
         "consumers": ["backtest/config.py", "backtest/signals/technical.py",
                           "scripts/spot_check_candle.py"],
         "production": 0.0, "type": "float", "band": [0.0, 0.3, 0.5],
         "free_band": [], "resim_band": [0.0, 0.3, 0.5],
         "sweep_levels": [0.3, 0.5],
         "derivation": ("CANON long-body soldiers, as a FRACTION OF THE BAR RANGE (#165 scale criterion). B2865 ACTUATED; measured bite at 0.5: 1175 -> 153 fires"),
         "subset_safe": False, "status": "ACTUATED-B2865",
         "evidence": "technical.py five-bar block; config.py CANDLE_MIN_BODY_PCT", "engine_implemented": True},
        {"id": "P4", "producer": "compute_candles",
         "param": "min_step_up_pct", "env": "CANDLE_MIN_STEP_PCT", "cfg_key": "P4_min_step_pct",
         "consumers": ["backtest/config.py", "backtest/signals/technical.py",
                           "scripts/spot_check_candle.py"],
         "production": 0.0, "type": "float", "band": [0.0, 0.1, 0.25],
         "free_band": [], "resim_band": [0.0, 0.1, 0.25],
         "sweep_levels": [0.1, 0.25],
         "derivation": ("BRACKET zero upward, as a fraction of the PRIOR bar's range; 0.0 preserves production's strict >. B2865 ACTUATED; measured bite at 0.25: 1175 -> 688 fires"),
         "subset_safe": False, "status": "ACTUATED-B2865",
         "evidence": "technical.py five-bar block; config.py CANDLE_MIN_STEP_PCT", "engine_implemented": True},
        {"id": "P5", "producer": "compute_candles",
         "param": "max_upper_wick_pct", "env": "CANDLE_MAX_WICK_PCT", "cfg_key": "P5_max_wick_pct",
         "consumers": ["backtest/config.py", "backtest/signals/technical.py",
                           "scripts/spot_check_candle.py"],
         "production": None, "type": "float", "band": [None, 0.3, 0.2],
         "free_band": [], "resim_band": [None, 0.3, 0.2],
         "sweep_levels": [0.3],
         "sweep_skip_reason": ("max_wick 0.2 dropped: clears in 5 of 18 (soldiers) and 4 of 18 (crows), the tighte"
                               "st bound and the second-largest source of unevaluable cells. DEPRIORITISED not rej"
                               "ected (L812)"),
         "derivation": ("CANON soldiers close at/near highs; unset = unenforced. B2865 ACTUATED; measured bite at 0.2: 1175 -> 138 fires"),
         "subset_safe": False, "status": "ACTUATED-B2865",
         "evidence": "technical.py five-bar block; config.py CANDLE_MAX_WICK_PCT", "engine_implemented": True},
        {"id": "P6", "producer": "strategy gate", "param": "rsi_14 ceiling",
         "env": None, "consumers": ["backtest/signals/screener.py"],
         "production": 60, "type": "float",
         "band": [41.97, 46.31, 50.16, 54.42, 60],
         "free_band": [41.97, 46.31, 50.16, 54.42], "resim_band": [60],
         "derivation": ("MEASURED retention quantiles on the 1,596 surviving "
                        "R5 fires (Table A build): 54.42 keeps 80pct, 50.16 "
                        "60pct, 46.31 40pct, 41.97 20pct; TIGHTER = LOWER "
                        "the ceiling; looser needs an env knob"),
         "subset_safe": True, "status": "MEASURED",
         "evidence": "strategy_optimisation/tighten/three_white_soldiers.md",
         "engine_implemented": True},
    ],
    "tools": {
        "keys": {"P2": "n_bars", "P3": "min_body_pct",
                 "P4": "min_step_pct", "P5": "max_wick_pct"},
        # B2897: the ENGINE axes (CANDLE_N_BARS / MIN_BODY_PCT /
        # MIN_STEP_PCT / MAX_WICK_PCT) - what the 54-config campaign
        # sweeps. P6 (the rsi_14 bound) has env=None and a
        # production-only band: it is the OFFLINE axis and belongs in the
        # free_levels leg. Naming it here made family_refusal refuse
        # outright on the missing env knob (MEASURED).
        "grid_keys": ["combo"],
        "single_combination": False,
        # S6-B2899: the spot_check leg - the last adapter gap
        # family_refusal named. Three legs: raw bar arithmetic,
        # compute_candles on the same PIT slice, and the cube record.
        "spot_check": {"script": "spot_check_candle.py", "cube": "",
                       # S6-B2917: the family is a long/short PAIR, so the
                       # checker must be TOLD the leg - it no longer
                       # defaults to one.
                       "strategy_flag": "--strategy",
                       "flags": {"P2": "--n-bars",
                                 "P3": "--min-body-pct",
                                 "P4": "--min-step-pct",
                                 "P5": "--max-wick-pct"},
                       "extra": ["--n", "50"],
                       "window": False, "precompute_check": False,
                       "pythonpath": None,
                       "note": "AUTO (S6-B2899)"},
        "grade": {"script": "grade_candle_config.py",
                  "cube": "",
                  # S6-B2900: the ENGINE axes P2-P5, which are what the
                  # 54-config campaign sweeps. The previous block named P6
                  # (rsi_14, env=None) - the OFFLINE axis - through an
                  # unsubstituted argv token "--axes rsi_14:le:<levels>",
                  # and pointed at offline_level_sweep.py, which has no
                  # --cube flag at all, pins its cube as a MODULE CONSTANT,
                  # and is in-sample by construction so it can never emit
                  # the Step-2 gate verdict the battery fails closed
                  # without. P6 FREE levels are a SEPARATE leg, ticketed
                  # S6-B2904 - not silently dropped (B2569 / #290).
                  "flags": {"P2": "--n-bars", "P3": "--min-body-pct",
                            "P4": "--min-step-pct",
                            "P5": "--max-wick-pct"},
                  "extra": [],
                  "step2_flag": "--step2",
                  "preregistered_flag": "--preregistered-exit",
                  "pythonpath": None,
                  "note": "AUTO (S6-B2900)"},
        # S6-B2904: P6 carries FREE levels on both legs and B2569/#290
        # requires them graded on EVERY landing - a missing leg produces no
        # row and no FAIL, so 54 configs would have landed with the axis
        # silently ungraded. Offline, zero engine hours: rsi_14 sits in
        # signals_at_entry for 1596 of 1596 soldiers and 1674 of 1674 crows
        # rows of output_r5_merged_1_7/trade_log.csv - coverage 1.0000.
        "free_levels": {"script": "grade_free_levels_candle.py",
                        "note": "AUTO (S6-B2904); reproduction-gated, and "
                                "the occupancy correction is DISCLOSED "
                                "rather than simulated (L812)"},
    },
}

FORMULA_TBC = (
    "=============================== PRODUCER LAYER ===============================\n"
    "\n"
    "P1  pattern  =  three_black_crows (compute_candle_signals,\n"
    "                technical.py:2108-2111): the soldiers pattern mirrored\n"
    "                   -> anatomy knobs P2-P4 mirror the soldiers knobs\n"
    "\n"
    "P2  n_bars                = 3     (band [3, 4]; env CANDLE_N_BARS)\n"
    "P3  min_body_pct_of_range = 0.0   (band [0, 0.3, 0.5]; env CANDLE_MIN_BODY_PCT)\n"
    "P4  min_step_down_pct     = 0.0   (band [0, 0.1, 0.25]; env CANDLE_MIN_STEP_PCT)\n"
    "P5  max_lower_wick_pct    = None  (band [None, 0.3, 0.2]; env CANDLE_MAX_WICK_PCT)\n"
    "\n"
    "============================== STRATEGY LAYER ===============================\n"
    "\n"
    "P6  short =  three_black_crows AND rsi_14 > 40\n"
    "             (TIGHTER = RAISE the floor; measured quantiles on the\n"
    "              1,674 R5 fires)\n"
    "P7  guard =  NOT _short_borrow_trap_active  (days_to_cover cap 5.0,\n"
    "             B718a owner-ruled risk guard - BANDABLE-OWNER-GATED)\n")

SPECS["three_black_crows_short"] = {  # B2897 (owner ruling 2026-09-20 "Candle goes first"): PROMOTED from SPECS_PHASE0 to SPECS. It is no longer pre-engine inventory - the 54-config anatomy campaign runs, so the battery adapter is owed NOW. Moved, never copied: the two names that sit in BOTH registries carry tools={} in PHASE0 and a complete block in SPECS, so duplication is what makes a family droppable.
    "gate": ("three_black_crows AND rsi_14 > 40 "
             "AND NOT _short_borrow_trap_active"),
    "formula": FORMULA_TBC,
    "baseline": {"artifact": "output_r5_merged_1_7", "fires": 1674,
                 "tickers": 544, "holdout_n": 470,
                 "window": "2022-05-06..2026-04-29"},
    "params": [
        {"id": "P1", "producer": "compute_candle_signals",
         "param": "three_black_crows (boolean leg)", "env": None,
         "consumers": ["backtest/signals/screener.py"],
         "production": True, "type": "bool", "band": [True],
         "free_band": [], "resim_band": [True],
         "derivation": "the pattern leg; magnitudes are P2-P4",
         "subset_safe": False,
         "status": "SMOKED-0.5 (302 pattern fires, 6 megacaps 4y)",
         "evidence": "technical.py:2108-2111", "engine_implemented": True},
        {"id": "P2", "producer": "compute_candles",
         "param": "n_bars (pattern length)", "env": "CANDLE_N_BARS", "cfg_key": "P2_n_bars",
         "consumers": ["backtest/config.py", "backtest/signals/technical.py",
                           "scripts/spot_check_candle.py"],
         "production": 3, "type": "int", "band": [3, 4],
         "free_band": [], "resim_band": [3, 4],
         "sweep_levels": [],
         "sweep_skip_reason": ("n_bars stays at production 3. Level 4 clears the holdout floor in only 4 of 27 cel"
                               "ls on EACH leg (B2937 feasibility) - rare by construction, not bad luck. DEPRIORIT"
                               "ISED not rejected; the count is a LOWER bound (L812) so it returns if the occupanc"
                               "y correction proves large"),
         "derivation": ("CANON Nison 1991 three; 4 the strict extension. "
                        "B2865: ACTUATED - the literal range(1,4) became a "
                        "knob; measured bite 1175 -> 466 soldiers fires on "
                        "25 tickers x 600 bars"),
         "subset_safe": False, "status": "ACTUATED-B2865",
         "evidence": "technical.py five-bar block; config.py CANDLE_N_BARS",
         "engine_implemented": True},
        {"id": "P3", "producer": "compute_candles",
         "param": "min_body_pct_of_range", "env": "CANDLE_MIN_BODY_PCT", "cfg_key": "P3_min_body_pct",
         "consumers": ["backtest/config.py", "backtest/signals/technical.py",
                           "scripts/spot_check_candle.py"],
         "production": 0.0, "type": "float", "band": [0.0, 0.3, 0.5],
         "free_band": [], "resim_band": [0.0, 0.3, 0.5],
         "sweep_levels": [0.3, 0.5],
         "derivation": ("mirror of the soldiers body band, fraction of the bar range. B2865 ACTUATED; measured bite at 0.5: 920 -> 97 crows fires"),
         "subset_safe": False, "status": "ACTUATED-B2865",
         "evidence": "technical.py five-bar block; config.py CANDLE_MIN_BODY_PCT", "engine_implemented": True},
        {"id": "P4", "producer": "compute_candles",
         "param": "min_step_down_pct", "env": "CANDLE_MIN_STEP_PCT", "cfg_key": "P4_min_step_pct",
         "consumers": ["backtest/config.py", "backtest/signals/technical.py",
                           "scripts/spot_check_candle.py"],
         "production": 0.0, "type": "float", "band": [0.0, 0.1, 0.25],
         "free_band": [], "resim_band": [0.0, 0.1, 0.25],
         "sweep_levels": [0.1, 0.25],
         "derivation": ("mirror: each close BELOW the prior by a fraction of the prior bar's range. B2865 ACTUATED; measured bite at 0.25: 920 -> 508"),
         "subset_safe": False, "status": "ACTUATED-B2865",
         "evidence": "technical.py five-bar block; config.py CANDLE_MIN_STEP_PCT", "engine_implemented": True},
        {"id": "P5", "producer": "compute_candles",
         "param": "max_lower_wick_pct", "env": "CANDLE_MAX_WICK_PCT", "cfg_key": "P5_max_wick_pct",
         "consumers": ["backtest/config.py", "backtest/signals/technical.py",
                           "scripts/spot_check_candle.py"],
         "production": None, "type": "float", "band": [None, 0.3, 0.2],
         "free_band": [], "resim_band": [None, 0.3, 0.2],
         "sweep_levels": [0.3],
         "sweep_skip_reason": ("max_wick 0.2 dropped: clears in 5 of 18 (soldiers) and 4 of 18 (crows), the tighte"
                               "st bound and the second-largest source of unevaluable cells. DEPRIORITISED not rej"
                               "ected (L812)"),
         "derivation": ("mirror: crows close at/near lows. B2865 ACTUATED; measured bite at 0.2: 920 -> 66 fires"),
         "subset_safe": False, "status": "ACTUATED-B2865",
         "evidence": "technical.py five-bar block; config.py CANDLE_MAX_WICK_PCT", "engine_implemented": True},
        {"id": "P6", "producer": "strategy gate", "param": "rsi_14 floor",
         "env": None, "consumers": ["backtest/signals/screener.py"],
         "production": 40, "type": "float",
         "band": [40, 45.094, 50.132, 54.066, 58.812],
         "free_band": [45.094, 50.132, 54.066, 58.812], "resim_band": [40],
         "derivation": ("MEASURED retention quantiles on the 1,674 surviving "
                        "R5 fires: 45.094 keeps 80pct ... 58.812 keeps "
                        "20pct; TIGHTER = RAISE the floor"),
         "subset_safe": True, "status": "MEASURED",
         "evidence": "strategy_optimisation/tighten/three_black_crows_short.md",
         "engine_implemented": True},
        {"id": "P7", "producer": "_short_borrow_trap_active",
         "param": "days_to_cover cap", "env": None,
         "consumers": ["backtest/signals/screener.py (6 short consumers)"],
         "production": 5.0, "type": "float", "band": [5.0],
         "free_band": [], "resim_band": [5.0],
         "derivation": ("B718a owner-ruled risk guard; tighter caps offline "
                        "via persisted days_to_cover but shared by 6 "
                        "consumers - BANDABLE-OWNER-GATED, per-strategy "
                        "override on the owner word only"),
         "subset_safe": False, "status": "BANDABLE-OWNER-GATED",
         "evidence": "screener.py:148 (B718a)", "engine_implemented": True},
    ],
    "tools": {
        "keys": {"P2": "n_bars", "P3": "min_body_pct",
                 "P4": "min_step_pct", "P5": "max_wick_pct"},
        # B2897: the ENGINE axes (CANDLE_N_BARS / MIN_BODY_PCT /
        # MIN_STEP_PCT / MAX_WICK_PCT) - what the 54-config campaign
        # sweeps. P6 (the rsi_14 bound) has env=None and a
        # production-only band: it is the OFFLINE axis and belongs in the
        # free_levels leg. Naming it here made family_refusal refuse
        # outright on the missing env knob (MEASURED).
        "grid_keys": ["combo"],
        "single_combination": False,
        # S6-B2899: the spot_check leg - the last adapter gap
        # family_refusal named. Three legs: raw bar arithmetic,
        # compute_candles on the same PIT slice, and the cube record.
        "spot_check": {"script": "spot_check_candle.py", "cube": "",
                       # S6-B2917: the family is a long/short PAIR, so the
                       # checker must be TOLD the leg - it no longer
                       # defaults to one.
                       "strategy_flag": "--strategy",
                       "flags": {"P2": "--n-bars",
                                 "P3": "--min-body-pct",
                                 "P4": "--min-step-pct",
                                 "P5": "--max-wick-pct"},
                       "extra": ["--n", "50"],
                       "window": False, "precompute_check": False,
                       "pythonpath": None,
                       "note": "AUTO (S6-B2899)"},
        "grade": {"script": "grade_candle_config.py",
                  "cube": "",
                  # S6-B2900: the ENGINE axes P2-P5, which are what the
                  # 54-config campaign sweeps. The previous block named P6
                  # (rsi_14, env=None) - the OFFLINE axis - through an
                  # unsubstituted argv token "--axes rsi_14:le:<levels>",
                  # and pointed at offline_level_sweep.py, which has no
                  # --cube flag at all, pins its cube as a MODULE CONSTANT,
                  # and is in-sample by construction so it can never emit
                  # the Step-2 gate verdict the battery fails closed
                  # without. P6 FREE levels are a SEPARATE leg, ticketed
                  # S6-B2904 - not silently dropped (B2569 / #290).
                  "flags": {"P2": "--n-bars", "P3": "--min-body-pct",
                            "P4": "--min-step-pct",
                            "P5": "--max-wick-pct"},
                  "extra": [],
                  "step2_flag": "--step2",
                  "preregistered_flag": "--preregistered-exit",
                  "pythonpath": None,
                  "note": "AUTO (S6-B2900)"},
        # S6-B2904: P6 carries FREE levels on both legs and B2569/#290
        # requires them graded on EVERY landing - a missing leg produces no
        # row and no FAIL, so 54 configs would have landed with the axis
        # silently ungraded. Offline, zero engine hours: rsi_14 sits in
        # signals_at_entry for 1596 of 1596 soldiers and 1674 of 1674 crows
        # rows of output_r5_merged_1_7/trade_log.csv - coverage 1.0000.
        "free_levels": {"script": "grade_free_levels_candle.py",
                        "note": "AUTO (S6-B2904); reproduction-gated, and "
                                "the occupancy correction is DISCLOSED "
                                "rather than simulated (L812)"},
    },
}


def validate_spec(spec: dict) -> list[str]:
    """Formula and Table A must not drift apart. Every P-id in the formula needs
    a params row and every params row needs a formula step - a mechanical check,
    because a hand-maintained pair of views silently diverges (L368 class)."""
    import re as _re
    # B2708: [PB] - B-rows are Table A inventory (owner ruling) and the
    # P-only regex false-fired "no formula step" on every breadth row
    ids_formula = set(_re.findall(r"^([PB]\d+)\s", spec.get("formula", ""), _re.M))
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
    # B2866 (owner-directed 2026-09-19): THE SECOND HALF OF THE SAME RULE.
    # The check above accepts any env NAME - MEASURED this turn, a spec
    # declaring CANDLE_TOTALLY_FAKE_KNOB_NOBODY_READS validated CLEAN. So the
    # escape it offers (add the knob) could be satisfied by TYPING one, which
    # is exactly the class that blocked Step 1: the candle anatomy bands named
    # parameters compute_candles did not contain (S6-B2860). A declared knob
    # that no ENGINE file reads is a name, not an actuator.
    for _p in spec["params"]:
        _k = _p.get("env")
        if _k and not _engine_reads_knob(_k):
            errs.append(f"{_p['id']} {_p['param']}: env knob {_k} is declared "
                        "but NO file under backtest/ reads it - a band whose "
                        "parameter does not exist in the producer is a FEATURE "
                        "REQUEST, not a band (B2866; implement it, then band it)")
    # B2870 (council-directed 2026-09-19): THE THIRD HALF OF THE SAME RULE.
    # B2866 proves the knob EXISTS; this proves the entry knows WHERE it bites.
    # The drift refusal used to live in launch_refusals, which enumerates SPECS
    # alone - so a SPECS_PHASE0 entry could declare a blast radius that is
    # fiction and validate_spec still returned CLEAN, which is exactly what
    # happened to the candle pair between B2865 and B2869. validate_spec is
    # called on BOTH registries, so siting the check here covers PHASE0 by
    # construction instead of by remembering to widen a second pin population.
    # MEASURED this turn: 16 distinct knobs across both registries, 2.91 s cold
    # / 0.0000 s warm - the "61 specs, over two minutes" note on knob_consumers
    # describes a larger population, not this one.
    _drift_knobs = [_p.get("env") for _p in spec["params"] if _p.get("env")]
    _drift_knobs += list(spec.get("env_actuators") or {})
    for _k in _drift_knobs:
        _dec = declared_consumers(spec, _k)
        _got = knob_consumers(_k)
        if _dec is None:
            errs.append(f"knob {_k} declares no `consumers` list - its blast "
                        "radius is unknown (S6-B2573d/B2870; the tree reads it "
                        f"in {_got}). Declaring NOTHING must fail exactly as "
                        "declaring fiction does, or the class escapes by "
                        "omission")
        elif _dec != _got:
            errs.append(f"knob {_k} consumer DRIFT - the entry declares {_dec} "
                        f"but the tree reads it in {_got} (S6-B2573d/B2870; "
                        "re-measure with knob_consumers and update the entry)")
    # B2883 (owner-directed 2026-09-20): R1 REFUSES A BAND INVENTORY WHOSE
    # BATTERY ADAPTER IS INCOMPLETE.
    #
    # Owner: "Neither strategy is a registered battery family ensure this class
    # of error doesnt happen again ... the r1 step of the workflow is modified
    # in the code base as well as the strategy optimization doc."
    #
    # MEASURED, and NOT what the incident's own comment claims: the candle pair
    # carry a tools block of {grade, keys} and lack {grid_keys,
    # single_combination, spot_check}. The adapters were HALF-WRITTEN, not
    # deferred - and `'tools' in getsource(validate_spec)` was False, so no
    # check anywhere in the tree could see a half-written adapter. Both entries
    # validated CLEAN (0 errors) while being unrunnable, which is precisely how
    # a complete-looking band inventory reached a launch that then refused it.
    #
    # The discriminator is ENGINE-REQUIRING bands, not band-presence: measured
    # across both registries, this refuses 2 of 18 entries - exactly the two of
    # the incident - leaves the 6 family-ready entries passing on their complete
    # tools block, and does not touch the 10 that carry no resim level beyond
    # production. There is therefore no historical backlog to disposal-plan
    # (the L721 class, checked rather than assumed).
    _eng = engine_requiring_params(spec)
    if _eng:
        _req, _greq, _cerr = _adapter_contract()
        _ids = ", ".join(f"{p['id']} {p['param']}" for p in _eng[:4])
        if _cerr:
            errs.append("the battery adapter contract could not be read "
                        f"({_cerr}) - refusing rather than certifying this "
                        "spec adapter-complete (L642, fail CLOSED)")
        else:
            _tools = spec.get("tools")
            if not isinstance(_tools, dict):
                errs.append(
                    f"carries {len(_eng)} ENGINE-REQUIRING band(s) ({_ids}) "
                    "but has NO `tools` adapter block - the landing would fail "
                    "closed AFTER the engine spend, and the refusal would "
                    "arrive at launch instead of here (S6-B2883; write the "
                    "adapter with the band, or drop the resim levels)")
            else:
                _miss = [k for k in _req if k not in _tools]
                _gmiss = sorted({f"{sec}.{k}" for sec in ("grade", "spot_check")
                                 if isinstance(_tools.get(sec), dict)
                                 for k in _greq
                                 if k not in (_tools.get(sec) or {})})
                if _miss:
                    errs.append(
                        f"carries {len(_eng)} ENGINE-REQUIRING band(s) ({_ids}) "
                        f"but its `tools` adapter block lacks {_miss} - a "
                        "HALF-WRITTEN adapter is what made this spec validate "
                        "clean while being unrunnable (S6-B2883)")
                elif _gmiss:
                    errs.append(
                        f"carries {len(_eng)} ENGINE-REQUIRING band(s) but its "
                        f"adapter sections lack {_gmiss} - the battery leg "
                        "would fail closed at landing (S6-B2883)")
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


_ENGINE_BLOB: dict = {}


def _engine_tree_text(code_root=None) -> str:
    """B2866: every non-test engine source, concatenated ONCE and memoised.
    knob_consumers is per-knob and re-reads the tree each time (its docstring
    records 61 specs taking over two minutes); this answers the cheaper
    question - does ANY engine file mention this name at all - in one pass."""
    root = Path(code_root) if code_root is not None else CODE_ROOT
    key = str(root)
    if key not in _ENGINE_BLOB:
        parts = []
        for p in sorted((root / "backtest").rglob("*.py")):
            if "tests" in p.parts:
                continue
            try:
                parts.append(p.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
        _ENGINE_BLOB[key] = chr(10).join(parts)
    return _ENGINE_BLOB[key]


def _engine_reads_knob(knob: str, code_root=None) -> bool:
    """B2866: is this knob READ anywhere that can actuate a run?

    Cheap path first - any mention in the engine tree. MEASURED when this
    shipped: that alone flagged the three INST_* knobs, which are NOT a
    defect - their SPECS rows say `read at precompute build time`, i.e. a
    script consumes them before the engine ever starts. A sweep must
    CLASSIFY, not count (L643), so a miss falls through to knob_consumers,
    which reads scripts/ env accesses from the AST. Only a genuinely
    unread name pays that cost."""
    if not knob:
        return False
    if knob in _engine_tree_text(code_root):
        return True
    try:
        return bool(knob_consumers(knob, code_root))
    except Exception:
        return False


def unactuated_knobs(specs: dict, code_root=None) -> dict:
    """B2866: {strategy: [(param id, knob)]} for every DECLARED env knob no
    engine file reads. Empty dict = every band in these specs names a
    parameter that exists. This is the mechanised form of the S6-B2860 class:
    Table A carried four candle anatomy bands whose parameters were absent
    from compute_candles, so the ruled Step-1 SEARCH had nothing to vary."""
    bad: dict = {}
    for name, spec in (specs or {}).items():
        for prm in (spec.get("params") or []):
            k = prm.get("env")
            if k and not _engine_reads_knob(k, code_root):
                bad.setdefault(name, []).append((prm.get("id"), k))
    return bad


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


def _adapter_contract() -> tuple[tuple, tuple, str]:
    """The battery's ADAPTER contract (_TOOLS_REQUIRED / _GRADE_REQUIRED),
    imported from run_postconfig rather than retyped - same lazy-import shape
    as _battery_families, so there is no import cycle (run_postconfig imports
    SPECS from here at module scope). An import failure is REPORTED, never
    swallowed: a missing contract must fail CLOSED (L642), because the
    alternative is silently certifying every spec as adapter-complete."""
    try:
        import run_postconfig as _rp
        return tuple(_rp._TOOLS_REQUIRED), tuple(_rp._GRADE_REQUIRED), ""
    except Exception as exc:                       # noqa: BLE001 - report ANY
        return (), (), f"{type(exc).__name__}: {exc}"


def engine_requiring_params(spec: dict) -> list[dict]:
    """Params whose band implies an ENGINE RUN: an env knob PLUS at least one
    resim level away from production. This is the band work whose grading needs
    a battery adapter, and it is the discriminator R1 refuses on (B2883).

    Deliberately NOT 'has any band' - MEASURED across both registries, 10 of 18
    entries carry no such param and must stay allowed; the 6 family-ready
    entries carry them and pass on their complete tools block."""
    out = []
    for p in spec.get("params") or []:
        if not p.get("env"):
            continue
        if any(str(x) != str(p.get("production"))
               for x in (p.get("resim_band") or [])):
            out.append(p)
    return out


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


# B2711 (owner-caught 2026-09-12): the RULED Step-1 search shape, from the
# runbook's step table (STRATEGY_OPTIMISATION_PLAN.md section 1.2, row "1 SEARCH |
# all fire-adding configs | 1 year, 2024-05..2025-05 | 200"; formerly SS10.1). The
# window ENDS at the IS/HO boundary 2025-05-05 BY DESIGN: a Step-1 search
# that reaches past it ranks combinations on holdout data and destroys the
# pre-registration for the whole family. Step 2 is the 4y/544 shape and is
# NOT a Step-1 option.
def _spec_identity(doc: dict) -> frozenset:
    """B2717: exact register candidates for `doc` (delegates to
    phase_table.spec_identity; empty when the resolver is absent)."""
    import importlib.util as _ilu
    if _ilu.find_spec("phase_table") is None:
        return frozenset()
    import phase_table as _pt
    return _pt.spec_identity(doc)


def _legacy_names() -> frozenset:
    """B2715: the grandfather register, read WITHOUT a silent swallow.
    An unavailable resolver or register yields the empty set, i.e. the
    typed-scope rule applies to every spec (the strict direction)."""
    import importlib.util as _ilu
    if _ilu.find_spec("phase_table") is None:
        return frozenset()
    import phase_table as _pt
    return _pt.legacy_typed_specs()


RULED_STEP1_WINDOW = {"start": "2024-05-05", "end": "2025-05-05"}
RULED_STEP1_TICKERS = "output_audit/_sweep_200.txt"
IS_HO_BOUNDARY = "2025-05-05"


def _step1_shape_refusals(doc: dict) -> list[str]:
    """A wave spec is a Step-1 search config by construction (launch_refusals
    require_subset). Refuse any window that reaches past the IS/HO boundary,
    and any deviation from the ruled shape that carries no explicit owner
    waiver. `step1_shape_waiver` must name the owner's words - a bare true
    is not a waiver (L642: the absent case is the case the guard exists for).
    """
    # B2713c LAYERING: a spec declaring `step` does not TYPE its scope -
    # phase_table.resolve owns it and refuses a past-boundary resolution
    # at source. Judging an absent field here would refuse the very
    # pointer form the council verdict mandates (caught by test_b2711).
    if "step" in doc or doc.get("_derived_from_spec"):
        return []
    # B2714: grandfathered legacy specs (register) are exempt - a
    # no-step spec cannot be judged against a step's row, and the two
    # committed STEP-2 specs legitimately carry the 4-year window.
    # B2715: this read used `except ImportError: pass` and tripped the
    # B2128 silent-swallow ratchet (correctly, #122). No swallow now:
    # _legacy_names() returns an EMPTY set when the register or the
    # resolver is unavailable, which applies the rule to everything -
    # the strict direction - and launch_refusals separately REFUSES on
    # an unimportable phase_table, so the loud path is not lost.
    # B2717: EXACT identity (phase_table.spec_identity) - the first form
    # was substring-based and let a short wave name grandfather itself.
    if _spec_identity(doc) & _legacy_names():
        return []
    w = doc.get("window") or {}
    start, end = str(w.get("start", "")), str(w.get("end", ""))
    # B2714d: this gate judges a TYPED window. A doc that types none is
    # not deviating - it relies on the resolver or the launcher default,
    # and the "declare your step" requirement lives in
    # phase_table.spec_refusals. Treating absent as WRONG refused a spec
    # that typed nothing at all (caught by test_b2578's good-spec arm).
    if not (start or end):
        return []
    # B2714b: accept EITHER waiver key - phase_table.spec_refusals takes
    # `shape_waiver` too, and two gates with two vocabularies refused a
    # doc the sibling accepted (L602 class, in code I wrote an hour apart).
    waiver = doc.get("step1_shape_waiver") or doc.get("shape_waiver")
    errs: list[str] = []
    if end > IS_HO_BOUNDARY:
        errs.append(
            f"window end {end} reaches PAST the IS/HO boundary "
            f"{IS_HO_BOUNDARY} - a Step-1 search on holdout data destroys the "
            "pre-registration (B2711; this is refused WITH or WITHOUT a "
            "waiver, it is not a scope choice)")
    if (start, end) != (RULED_STEP1_WINDOW["start"], RULED_STEP1_WINDOW["end"]):
        if not (isinstance(waiver, str) and len(waiver.strip()) >= 20):
            errs.append(
                f"window {start}..{end} is not the RULED Step-1 window "
                f"{RULED_STEP1_WINDOW['start']}..{RULED_STEP1_WINDOW['end']} "
                "(runbook step table, section 1.2) and carries no "
                "`step1_shape_waiver` quoting the owner's words (B2711)")
    tf = str(doc.get("tickers_file", ""))
    if tf and tf != RULED_STEP1_TICKERS:
        if not (isinstance(waiver, str) and len(waiver.strip()) >= 20):
            errs.append(
                f"tickers_file {tf} is not the ruled Step-1 universe "
                f"{RULED_STEP1_TICKERS} and carries no `step1_shape_waiver` "
                "(B2711)")
    return errs


def _rider_refusals(doc: dict, root: Path, graded: list[str]) -> list[str]:
    """B2710 (B2707 reuse doctrine): `cube_riders` names strategies the
    ENGINE runs for cube trades only - BATTERY-EXEMPT BY DESIGN, exemption
    stamped in the merged engine file and the manifest, never silent. Fail
    closed on: missing file, overlap with the graded subset, unreadable
    strategy registry, unregistered rider (L642)."""
    rel = doc.get("cube_riders")
    if not rel:
        return []
    p = root / str(rel)
    if not p.exists():
        return [f"cube_riders {rel} does not exist under {root} (fail CLOSED, L642)"]
    riders = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()
              if ln.strip() and not ln.lstrip().startswith("#")]
    errs: list[str] = []
    both = sorted(set(riders) & set(graded))
    if both:
        errs.append(f"cube_riders overlap the graded subset: {both} - a "
                    "strategy is graded or a rider, never both (B2710)")
    try:
        from backtest.signals.screener import ALL_STRATEGIES as _ALL
        if isinstance(_ALL, dict):
            names = set(_ALL.keys())
        else:
            names = {getattr(f, "__name__", str(f)) for f in _ALL}
            names |= {str(getattr(f, "name", "")) for f in _ALL}
    except Exception as e:
        return errs + [f"cube_riders: strategy registry unreadable ({e}) - "
                       "refusing rather than guessing (L642)"]
    for r in riders:
        if r not in names:
            errs.append(f"cube rider {r}: not a registered strategy "
                        "(fail CLOSED, B2710)")
    return errs


def leverage(spec: dict) -> dict:
    """Engine runs, free combinations and their ratio for ONE spec.

    B2767. THE PRECEDENCE RULE IS THE POINT: where a parameter carries
    per-level `free_band` / `resim_band`, those are authoritative and the
    coarse boolean `subset_safe` is IGNORED. B2467/L726 split the overloaded
    field because one boolean cannot say "half this band is free"; this
    helper exists because splitting it was not enough - both encodings then
    coexist, the coarse one stays readable, and reading it understates in a
    PREDICTABLE direction (free levels counted as resim).

    MEASURED at B2767: institutional_committed_growth_long read 1:1 over
    4800 engine runs off the boolean, and 8:1 over 600 off its per-level
    bands - a 8x error, published in an owner-facing table before it was
    caught. The error direction always inflates cost, so it always argues
    for NOT running something.

    Returns {engine_runs, free_combos, ratio, basis} where basis names
    which encoding was used, so a caller can never quote the number without
    also being able to quote its provenance.
    """
    params = spec.get("params") or []
    per_level = any(("free_band" in q or "resim_band" in q) for q in params)
    # S6-B2752f: an axis the engine cannot REACH costs no engine runs.
    # MEASURED on hub-2: counting a knob with no env actuator and no
    # call-site plumbing returned 30 engine runs against a true 10 - the
    # SAME DIRECTION L796 names as the dangerous one, since an inflated
    # cost always argues for not running something. Reported, not dropped:
    # an omitted axis is invisible at close (L785).
    unreachable = [q for q in params if q.get("engine_implemented") is False]
    params = [q for q in params if q.get("engine_implemented") is not False]
    engine = free = 1
    for q in params:
        if per_level:
            fb = q.get("free_band") or []
            rb = q.get("resim_band") or []
            if fb:
                free *= len(fb)
            if rb:
                engine *= len(rb)
        else:
            levels = max(len(q.get("band") or []), 1)
            if q.get("subset_safe") is True:
                free *= levels
            else:
                engine *= levels
    return {"engine_runs": engine, "free_combos": free,
            "ratio": free,
            "basis": "per_level" if per_level else "subset_safe",
            "unreachable_axes": [f"{q['id']} {q['param']}"
                                 for q in unreachable]}


def phase1b_admitted(root: Path | None = None) -> tuple:
    """(admitted strategy names, why-unreadable) from the Phase 1B admissions.

    B2731. A strategy admitted to Phase 1B is CLOSED to further optimisation
    testing - owner ruling 2026-09-12: "We stop testing the strategies once
    they are in the phase 1B unless you get specific over rides from me".

    Returns (frozenset(), reason) when the file cannot be read, and the caller
    REFUSES on that - unknown admission status is not permission (L642).

    B2739: the ledger is read from CODE_ROOT, not from the caller's `root`.
    The admissions JSON and PHASE_1B_ROSTER.md are REPO facts; `root` is
    where a SPEC'S FILES live and a test (or a staged launch) may relocate
    it. Reading `root` made the fail-closed branch fire on every launch
    whose spec directory was not the repo - MEASURED: test_b2578 refused a
    valid spec with "admissions unreadable" pointing at a pytest tmp dir,
    i.e. the gate refused everything for an environmental reason. The
    precedent is three lines away at the consumer-drift check: "Measured
    against THIS repo's code (CODE_ROOT) - `root` is where the spec's files
    live, which a test may relocate; the code tree is not." An explicit
    `root` is still honored so the pins can drive both trees.
    """
    import json as _json
    root = Path(root) if root is not None else CODE_ROOT
    f = root / "output_audit" / "phase_1b_step2_admissions.json"
    if not f.exists():
        return frozenset(), f"{f} does not exist"
    try:
        d = _json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return frozenset(), f"{f} unreadable: {exc!r}"
    names = set()
    for a in (d.get("admissions") or []):
        s = a.get("strategy")
        if s:
            names.add(str(s))
        # a declared mirror leg is admitted too - it rides the same decision
        m = a.get("mirror") or a.get("declared_mirror")
        if m:
            names.add(str(m))
    # B2733: the JSON is NOT the only record of an admission. MEASURED -
    # PHASE_1B_ROSTER.md line 123 retains smc_breaker_block_short and
    # pead_short_negative_yoy_growth as Step-2 admissions, and NEITHER
    # appears in the JSON (no admission carries a mirror field either), so
    # the B2731 gate would have passed a spec grading a banked SHORT leg.
    # A mirror rides its long's decision - same defect, same refusal. The
    # roster is source-of-truth per its own header, so both are read and
    # unioned; either being unreadable fails CLOSED (L642/L742).
    r = root / "PHASE_1B_ROSTER.md"
    if not r.exists():
        return frozenset(), f"{r} does not exist"
    import re as _re
    try:
        rt = r.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return frozenset(), f"{r} unreadable: {exc!r}"
    for line in rt.splitlines():
        if "retained, Step-2 admissions" in line:
            names.update(_re.findall(r"`([A-Za-z0-9_]+)`", line))
    return frozenset(names), ""


def _admitted_retest_refusals(doc: dict, root: Path, strats: list) -> list:
    """B2731: refuse to spend engine time re-testing an ADMITTED strategy.

    The escape is an explicit owner override IN THE SPEC:

        "owner_override_retest_admitted": {"<strategy>": "<owner words + date>"}

    so an override is a dated artifact rather than a claim in a turn. The
    override must NAME the strategy - a bare `true` is refused, because a
    blanket flag is exactly the silent exemption L789 warns about.
    """
    # B2739: CODE_ROOT, not the spec-relative root (see phase1b_admitted)
    admitted, why = phase1b_admitted(None)
    if why:
        return [f"Phase 1B admissions unreadable ({why}) - refusing rather "
                "than launching against unknown admission status (L642/B2731)"]
    ov = doc.get("owner_override_retest_admitted") or {}
    if ov is True or ov is False:
        return ["owner_override_retest_admitted must be a MAPPING of strategy "
                "-> the owner's words; a bare boolean is a blanket exemption "
                "(L789 - an escape must name its target)"]
    out = []
    for s in strats:
        if s not in admitted:
            continue
        quote = (ov or {}).get(s)
        if not quote or not str(quote).strip():
            out.append(
                f"{s}: ALREADY ADMITTED to Phase 1B - a strategy in the roster "
                "is CLOSED to further optimisation testing (owner ruling "
                "2026-09-12: 'We stop testing the strategies once they are in "
                "the phase 1B unless you get specific over rides from me'). "
                "MEASURED COST OF THE INSTANCE THAT PRODUCED THIS GATE: 2.41 h "
                "of engine time graded an admitted strategy while the actual "
                "campaign subject rode along ungraded (S6-B2731). To override, "
                "put the owner's words in the spec under "
                f"owner_override_retest_admitted[{s!r}]")
    return out


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
    # B2710: riders validated up front; graded-subset checks unchanged
    errs += _rider_refusals(doc, root, strats)
    # B2731: an ADMITTED strategy is closed to re-testing (owner ruling)
    errs += _admitted_retest_refusals(doc, root, strats)
    # B2711: the ruled Step-1 search shape (holdout reach is absolute)
    errs += _step1_shape_refusals(doc)
    # S6-B2945 (L835): enforce at SPEC time what prelaunch_gate enforces
    # at LAUNCH time. A wave spec (keyed on `wave`; manifests carry
    # `sequence`) in the MODERN shape (`step` declared, window and
    # universe resolver-owned per B2713) that omits fires_at_production
    # produces a manifest the gate refuses - MEASURED, a 36-spec chain
    # HALTED on spec 1 after registering a task and writing a wave
    # summary, for a field knowable in seconds. Same reason string as
    # the gate, so the two cannot drift apart.
    #
    # APPENDED, never returned early: B2883 above records what an early
    # exit here costs - one refusal earned, every check below it
    # skipped. The first draft of THIS check returned, and test_b2713
    # caught the admitted-retest refusal going missing.
    if ("wave" in doc and "step" in doc
            and "fires_at_production" not in doc):
        errs.append(
            "spec carries no fires_at_production - run the 0.5 smoke "
            "(fires at PRODUCTION params on live data) and record the "
            "count in the spec before launch (S6-B2848c; fail closed on "
            "the absent field). prelaunch_gate refuses the derived "
            "manifest otherwise (S6-B2945)")
    # B2713 (council verdict): resolver-owned fields are not typeable
    try:
        from phase_table import spec_refusals as _pt_spec_refusals
        errs += _pt_spec_refusals(doc)
    except ImportError as _e:  # fail CLOSED (L642)
        errs.append(f"phase_table resolver unavailable ({_e}) - refusing "
                    "rather than launching on typed scope (B2713)")
    for s in strats:
        # B2883: RESOLVE BOTH REGISTRIES, AND DO NOT SUPPRESS THE REST.
        # MEASURED: this read SPECS alone and `continue`d, so a PHASE0-only
        # strategy earned ONE refusal and skipped every check below it -
        # FAMILIES, validate_spec, knob_is_read, consumer drift and band
        # membership, nine checks in all. A probe setting a knob named in no
        # spec anywhere drew no complaint. So the gate looked like it caught
        # B2850 when it caught one reason of five.
        #
        # The old message was also FALSE: it said "no SPECS entry" for a pair
        # that has a complete, validate_spec-clean entry in SPECS_PHASE0 in
        # THIS FILE. That wording invites exactly one repair - copy it into
        # SPECS - which manufactures another duplicate-registry instance
        # (S6-B2874: 4 consumers resolve the two registries in 3 different
        # precedence orders).
        spec = SPECS.get(s)
        _phase0_only = False
        if spec is None:
            spec = SPECS_PHASE0.get(s)
            _phase0_only = spec is not None
        if spec is None:
            errs.append(f"{s}: no entry in producer_variant_table (neither "
                        "SPECS nor SPECS_PHASE0) - the post-config battery "
                        "would FAIL closed at landing AFTER the engine spend "
                        "(S6-B2573b; fail CLOSED at launch)")
            continue
        if _phase0_only:
            errs.append(f"{s}: its entry is in SPECS_PHASE0 (pre-engine "
                        "inventory), not SPECS - so it is not a registered "
                        "post-config battery family and the landing would FAIL "
                        "closed. A PHASE0 entry cannot become a family by "
                        "completing its `tools` block alone - MEASURED, "
                        "run_postconfig.family_refusal reads SPECS.get(name), "
                        "so a COMPLETE block left in SPECS_PHASE0 still "
                        "returns 'no SPECS entry'. MOVE the entry into SPECS "
                        "(never COPY - duplication across the two registries "
                        "is what makes a live family droppable) AND complete "
                        "its `tools` block, in ONE change (S6-B2897; the "
                        "B2883 wording here was unexecutable). Every further "
                        "refusal below is now reported too, instead of being "
                        "suppressed.")
        if fams is None:
            errs.append(f"{s}: the battery registry could not be read ({why}) "
                        "- refusing rather than guessing (L642)")
        elif s not in fams:
            # B2883: say WHICH registry the entry is in. Saying "has a SPECS
            # entry" about a PHASE0-only strategy is the same false-message
            # class this batch is fixing one line above.
            _where = "SPECS_PHASE0" if _phase0_only else "SPECS"
            errs.append(f"{s}: has a {_where} entry but is NOT a registered "
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
        # B2870: the consumer-drift loop that stood here MOVED into
        # validate_spec (called just above at the `errs +=` line), because this
        # function enumerates SPECS alone and the check has to reach
        # SPECS_PHASE0 too. Siting it in validate_spec covers both registries by
        # construction; re-adding it here would double-report every error.
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
                        # B2637 (S6-B2622a): the provenance check moves to the
                        # LAUNCH gate. B2622 put it in the battery, which fires
                        # at LANDING - after the engine has already spent 2-4 h
                        # on a tag built at the wrong parameters. A dir with no
                        # record is DISCLOSED, not refused: the pre-B2622 tags
                        # carry none and refusing them would HALT every live arm
                        # (the tightening-over-a-backlog rule).
                        elif (d / "build_params.json").is_file():
                            import json as _j
                            try:
                                _rec = _j.loads((d / "build_params.json")
                                                .read_text(encoding="utf-8"))
                            except (OSError, ValueError) as _exc:
                                errs.append(f"{s}: arm '{tag}' precompute dir {d} "
                                            f"has an unreadable build_params.json "
                                            f"({_exc!r}) - fail CLOSED (L642)")
                                _rec = None
                            if _rec:
                                _pairs = (("min_consecutive_quarters",
                                           "INST_MIN_CONSECUTIVE_QUARTERS", int, 4),
                                          ("growth_lookback_quarters",
                                           "INST_GROWTH_LOOKBACK_QUARTERS", int, 4),
                                          ("growth_multiple",
                                           "INST_GROWTH_MULTIPLE", float, 1.10))
                                _env = dict(arm.get("env") or {})
                                for _rk, _ek, _cast, _dflt in _pairs:
                                    _want = _cast(_env.get(_ek, _dflt))
                                    _got = _rec.get(_rk)
                                    if _got is not None and _cast(_got) != _want:
                                        errs.append(
                                            f"{s}: arm '{tag}' precompute {d.name} "
                                            f"was BUILT at {_rk}={_got} but the arm "
                                            f"declares {_want} - the engine would "
                                            "grade a wrong-population cube "
                                            "(S6-B2578a; refused BEFORE the spend)")
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
# S6-B3012: the columns Table D emits for EVERY family, independent of
# the per-family axis registry. ONE definition: table_d builds its header
# from this tuple and scan_retyped_locked_table in
# scripts/verify_turn_compliance.py reads the SAME tuple to refuse a
# response that retypes the table with columns dropped. Two copies of a
# column list diverge the first time one is edited (L593).
TABLE_D_FIXED_COLUMNS = ("exit", "is_ci_lo", "n", "tier", "dup",
                        "is_sharpe", "cls", "holdout_n",
                        "full_period_n", "verdict", "npt_excl")

D_AXIS_FAMILIES = {
    # S6-B2940: the candle pair. WITHOUT this a candle cfg falls through
    # _d_family to smc's columns and Table D renders P1 swing / P2
    # close_mit / P3 tail_n / P4 age_bars / P5 break_pct / P6 span as six
    # dashes, with all four candle knobs invisible - the L790 class (a
    # locked format wired to one family), caught by the R2 rung BEFORE
    # the 18-config campaign rather than after it.
    #
    # BOTH LEGS share ONE entry because they share one producer and the
    # same four env knobs (technical.py:2143-2150), so `detect` keys on
    # P2_n_bars, which only the candle grader emits. It is listed FIRST
    # so its detect key is tested before smc's catch-all default.
    "candle_anatomy": {
        "serves": ("three_white_soldiers", "three_black_crows_short"),
        "detect": "P2_n_bars",
        "d1": (("body", "cfg", "P3_min_body_pct"),
               ("step", "cfg", "P4_min_step_pct")),
        # S6-B3012 (owner catch): BOTH LEGS SHARING ONE ENTRY IS WHY THE
        # LEG WAS INVISIBLE. The note above says the pair shares one
        # producer and four env knobs - true, and it silently made the
        # LEG a non-axis, so a reader could tell tws from tbc only by
        # squinting at the config string. It is the FIRST axis of this
        # campaign (36 configs = 18 knob cells x 2 legs), hence P1.
        "d2": (("P1 leg", "art", "strategy"),
               ("P2 n_bars", "cfg", "P2_n_bars"),
               ("P3 body", "cfg", "P3_min_body_pct"),
               ("P4 step", "cfg", "P4_min_step_pct"),
               ("P5 wick", "cfg", "P5_max_wick_pct")),
    },
    "smc_breaker_block": {
        # S6-B2941: records the CURRENT fallback for the four non-breaker
        # smc families. Whether these six columns are RIGHT for
        # smc_inverse_fvg or smc_liquidity_sweep_reversal is a separate
        # question - this makes the claim visible and testable, not true.
        "serves": ("smc_breaker_block_long", "smc_equal_lows_sweep_long",
                   "smc_inverse_fvg", "smc_liquidity_sweep_reversal",
                   "smc_order_block_bounce"),
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
        "serves": ("institutional_committed_growth_long",),
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


def _d_axis_value(spec, cfg: dict, admit: dict, art=None):
    """S6-B3012: THREE sources, not two. `cfg` and `admit` reach the
    swept knobs; an axis that is a property of the RUN rather than of a
    knob - the leg a config belongs to - lives on the artifact, and with
    only two sources it was unreachable, so it was left out of the
    registry entirely. That omission is what made P1 invisible for the
    candle pair (owner catch 2026-09-23)."""
    _, src, key = spec
    if src == "art":
        return (art or {}).get(key)
    return (cfg if src == "cfg" else (admit or {})).get(key)


def table_d(grids: dict[str, dict], top: int = 25) -> list[str]:
    """STEP-1 RANKED LIST - one row per (config x exit) outcome, top N.

    B2725, OWNER CATCH: this is ONE UNIFIED TABLE carrying a column per
    producer band. It used to show only `sw` and `sp` and exile the other
    four swept axes to a second table (`table_d_params`, "TABLE D-2"), on
    a readability rationale authored BEFORE the owner ruled "no separate
    table ds are logical" - so the ruling was applied to the OFFLINE
    renderer (table_d_render.py, B2699) and this GRID sibling kept the
    rejected shape, which B2723 then wired into every landing. The
    duplicated `sw`/`sp` columns are GONE because they ARE P1 and P6.

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
    fam_seen = None
    for name, g in grids.items():
        cfg = g.get("config") or {}
        _fam = _d_family(cfg)
        fam_seen = fam_seen or _fam
        for r in (g.get("step1_ranking") or []):
            a = r.get("admit") or {}
            row = {
                "config": name,
                "exit": r.get("exit"),
                "ci": r.get("is_ci_lo"), "n": r.get("fires"),
                "sh": r.get("is_sharpe"), "cls": r.get("class_size"),
                "ho": a.get("holdout_n"), "fp": a.get("full_period_n"),
                "verdict": a.get("verdict"),
                "npt": a.get("npt_excluded_identity_boundary"),
            }
            # B2725: every producer band is a COLUMN of this table now
            for _j, spec in enumerate(_fam["d2"], 1):
                row[f"A{_j}"] = _d_axis_value(spec, cfg, a, g)
            rows.append(row)

    sig = lambda r: (round(r["ci"], 3) if r["ci"] is not None else None,
                     round(r["sh"], 3) if r["sh"] is not None else None,
                     r["n"], r["exit"])
    counts = Counter(sig(r) for r in rows)
    rows.sort(key=lambda r: (-(r["ci"] if r["ci"] is not None else -9e9),
                             -(r["n"] or 0)))
    seen = Counter()
    _fam_d = fam_seen or D_AXIS_FAMILIES["smc_breaker_block"]
    _labels = [spec[0] for spec in _fam_d["d2"]]

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
        # B2725: the producer-band glossary belongs ON the unified table.
        ("_**EVERY PRODUCER BAND IS A COLUMN HERE** (owner ruling: one "
         "unified table, no separate Table Ds). Axis labels come from the "
         "per-family registry D_AXIS_FAMILIES: " + ", ".join(_labels) +
         ". For smc_breaker_block: P2 close_mitigation (False = "
         "production, mitigate on high/low), P4 age_bars_max (None = "
         "production, no cap), P5 break_pct_max (None = production, no "
         "cap). `npt_excl` = next_pivot_target refused on this cell as "
         "boundary-spanning (B2014), one of the two exits missing from "
         "24._"),
        "",
        ("| # | config | " + " | ".join(_labels) + " | "
         + " | ".join(TABLE_D_FIXED_COLUMNS) + " |"),
        "|" + "---|" * (len(_labels) + 2 + len(TABLE_D_FIXED_COLUMNS)),
    ]
    for i, r in enumerate(rows[:top], 1):
        k = sig(r)
        seen[k] += 1
        dup = f"{seen[k]} of {counts[k]}" if counts[k] > 1 else "-"
        ci = f"{r['ci']:+.3f}" if r["ci"] is not None else "n/a"
        sh = f"{r['sh']:.3f}" if r["sh"] is not None else "n/a"
        _axes = " | ".join(str(r.get(f"A{_j}"))
                           for _j in range(1, len(_labels) + 1))
        _npt = "yes" if r.get("npt") else "-"
        out.append(
            f"| {i} | {r['config']} | {_axes} | {r['exit']} | "
            f"{ci} | {r['n']} | {_d_tier(r['n'])} | {dup} | {sh} | {r['cls']} | "
            f"{r['ho']} | {r['fp']} | {r['verdict']} | {_npt} |")

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


def table_d_params(grids: dict[str, dict], top: int = 25) -> list[str]:
    """SUPERSEDED at B2725 - its columns are now IN table_d.

    Kept callable because scripts/show_table_d.py offers it as an
    axes-only view, but it is NO LONGER part of any report: emitting it
    beside table_d recreates the two-table shape the owner rejected, and
    test_b2725 fails the landing report if a "TABLE D-2" section returns.

    Historical docstring below; its readability rationale ("at 18 a
    markdown table wraps") predates the ruling and no longer governs.

    TABLE D-2 - the SIX swept axes for the same top-N rows as table_d.

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


_PIN_ABSENT = object()  # S6-B3019: distinguishes "key missing" from "pinned None"


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
        # S6-B3015: `param` is a DISPLAY LABEL - "n_bars (pattern
        # length)", "min_body_pct_of_range" - while the artifact key is
        # the engine's own spelling ("P3_min_body_pct"). Building the key
        # as pid + "_" + label silently missed all four candle axes and
        # rendered `?`, which by this function's own precedence means NOT
        # RECORDED, about values sitting in the artifact's config block.
        # One field doing two jobs (L728); `cfg_key` splits them and
        # defaults to the old expression, so every smc entry - whose
        # labels ARE their keys - resolves byte-identically.
        # S6-B3019: a PINNED None is a VALUE, not an absence. Seven of
        # the fourteen landed candle configs pin P5_max_wick_pct to
        # null - "no wick cap" IS the setting - and `cfg.get(k)`
        # returns None for that and for a key that is simply missing,
        # so `pin is not None` sent them to `?`, which this function
        # defines as NOT RECORDED. Same false-absence class as the
        # cfg_key defect one commit earlier, surviving in the tail
        # (L605/B1972: a lookup default cannot tell "no value" from
        # "the value None"). A sentinel separates them; _fmt already
        # renders None as "none".
        _pin_key = _p.get("cfg_key") or (pid + "_" + nm)
        pin = cfg[_pin_key] if _pin_key in cfg else _PIN_ABSENT
        obs = observed.get(nm)
        fl = freed.get(pid.lower())
        band = [str(x) for x in (_p.get("band") or [])]
        if pin is not _PIN_ABSENT:
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


# S6-B3016: ONE LINE ON PURPOSE. test_b1510_producer_artifact_standard
# asserts the locked header appears VERBATIM in this source, so
# splitting it across string fragments defeats that pin - the guard
# over a locked format must keep reading as one literal.
_TABLE_C_HEADER = "| config | combos | starved-IS | no-Sharpe | graded | distinct | bands | all producer bands tested | median IS-Sharpe | max IS-Sharpe | IS-Sharpe at best ci_lo | best IS-CI-lo | best combination | entry window |"


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
            _TABLE_C_HEADER,
            # S6-B3016: DERIVED, never typed. The header gained `entry
            # window` and the separator literal stayed at 12 cells, so a
            # locked format emitted malformed markdown and the trailing
            # column - the window every figure was measured over - drops
            # in any strict renderer. One definition (L593).
            "|" + "---|" * (len(_TABLE_C_HEADER.split("|")) - 2)]
    for name, g in grids.items():
        # B2521 (S6-B2520m): the declared population, not the field name.
        res, _pf, _pu = grid_population(g)
        # B2619 (S6-B2566): the "combos" header is locked; when the population
        # is NOT combinations the CELL names its unit, so a single-combination
        # grid reads "1 combination (24 exits ranked)" instead of a bare 24 -
        # the owner-found mislabel ("why is it just 24 combinations?").
        _combo_cell = (str(len(res)) if _pu == "combinations"
                       else f"1 combination ({len(res)} {_pu} ranked)")
        # B2625 (S6-B2612e, owner blanket 2026-09-06 + the row's own
        # recommendation): the 13th column reads the grid's OWN window
        # block (cube entry span), so a 4-year Step-2 cube and a 1-year
        # Step-1 config are distinguishable from the table itself. A
        # grid with no window block renders "-" (absent, never guessed);
        # tickers stay OUT - the artifact carries no such field (#230a).
        _w = g.get("window") or {}
        _win_cell = (f"{_w['cube_entry_min']}..{_w['cube_entry_max']}"
                     if _w.get("cube_entry_min") and _w.get("cube_entry_max")
                     else "-")
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
        # S6-B3017: AXIS_KEYS is the hardcoded smc six, and it is read
        # from the RESULT ROWS. A family that PINS its axes in the config
        # block and searches ACROSS configs (the candle campaign: one
        # engine cell per config) therefore had no axes at all, so the
        # count fell to None and rendered `-` - "not recorded" - about
        # four values the artifact records. Seeding from the family spec
        # makes it read 0: recorded, and nothing was searched WITHIN this
        # cube, which is the truth. Counts are unchanged for smc: a pinned
        # axis contributes a 1-element set and the sum counts len > 1.
        _fspec = SPECS.get(g.get("strategy"))
        _fcfg = g.get("config") or {}
        for _fp in (_fspec or {}).get("params", []):
            _fk = _fp.get("cfg_key") or (_fp["id"] + "_" + _fp["param"])
            if _fk in _fcfg:
                axes.setdefault(_fk, set()).add(repr(_fcfg[_fk]))
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
        # S6-B3023 (owner ruling 2026-09-23, option c). The single column
        # named `best IS-Sharpe` held the Sharpe OF THE BEST-CI_LO ROW,
        # not a maximum - correct selection (L455) under a label that
        # claims otherwise. The B2182 comment above states the intent:
        # max - median IS the selection artifact. With the selected row
        # in that cell the diagnostic was UNDERSTATED wherever the two
        # rankings disagree: MEASURED 2 of 14 landed candle configs,
        # c06 printing 0.310 against a true max 0.379 and c12 printing
        # 0.205 against 0.394. Now BOTH are columns.
        #
        # THE MAX COMES FROM `graded`, THE SAME POPULATION AS THE MEDIAN -
        # never from step1_ranking, which holds the top 10 rows by ci_lo
        # and is a SELECTED set (L708). For the candle family the two
        # happen to agree at 24 graded rows; for a family with hundreds of
        # combinations a top-10 by ci_lo can easily exclude the max
        # Sharpe, and max - median must be one population or it is not a
        # difference.
        mx = round(max(_med_vals), 3) if _med_vals else None
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
                        f"{_measured_fmt(mx)} | {sh} | {cl} | {combo} | {_win_cell} |")
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
                        f"{_measured_fmt(mx)} | {sh} | {cl} | {combo} | {_win_cell} |")
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
                    f"{_measured_fmt(med)} | {_measured_fmt(mx)} | {sh} | {cl} | {combo} | {_win_cell} |")
        if other:
            rows.append(f"| | | | | | | | | | | | | **UNCLASSIFIED {other} rows - the funnel does not "
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

    # B2634: the RENDER path also serves Phase-0 drafts (Table A before the
    # family adapter exists); battery/launch lookups read SPECS alone.
    spec = SPECS.get(a.strategy) or SPECS_PHASE0.get(a.strategy)
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

# S6-B2752e: hub-2 registered. S6-B2752 framed this as "the S6-B2732a template
# applied three more times"; MEASURED at B2752a it is not (L800) - P3 has no env
# knob, and the gate's PRIMARY key is persisted on 0 of 1340 fires. Both facts
# are inventoried here rather than smoothed over. FAMILIES is DERIVED from SPECS
# (run_postconfig.py:732), so this registers the battery family too.
SPECS["smc_order_block_bounce"] = {
    "gate": ("(smc_ob_bullish_tap_recent_5d AND rsi_14<45 AND "
             "price_above_ema_200) | short mirror + borrow gate "
             "(screener.py:4693 strat_smc_order_block_bounce)"),
    "formula": FORMULA_SMC_OBB,
    "baseline": {"artifact": "output_r5_merged_1_7", "fires": 1340,
                 "tickers": 475, "holdout_n": 352,
                 "window": "2022-05-05..2026-04-29",
                 "tickers_basis": ("DISTINCT TICKERS THAT FIRED, measured "
                                   "S6-B2752e - the universe is 544, and "
                                   "quoting that here would be a grain error "
                                   "(L664)")},
    "params": [
        {"id": "P1", "producer": "_smc.swing_highs_lows",
         "param": "swing_length", "env": "SMC_SWING_LENGTH",
         # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
         # A level is FREE only if it selects a strict SUBSET of the landed
         # fires AND its discriminating quantity is PERSISTED per trade so the
         # subset can be identified. Across ALL rows of this strategy in
         # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
         # BOOLEAN keys computed AT the production setting, and this knob's
         # discriminator is not among them - so no level is identifiable
         # offline and every one needs the engine. (P6 span looked gradable:
         # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
         # not imply price_above_ema_50, so a different span is a DIFFERENT set,
         # not a subset - evaluable is not subset-safe.) METADATA ONLY:
         # production is untouched and no run is scheduled, so no landed grade
         # is recomputed. L726 / L812 / L824.
         "free_band": [],
         "resim_band": [5, 10, 20, 30, 50],
         "consumers": ["backtest/config.py",
                       "backtest/engine/exit_strategies.py",
                       "backtest/signals/screener.py"],
         "production": 20, "type": "int", "band": [5, 10, 20, 30, 50],
         "derivation": ("library default 50, production 20; band brackets "
                        "both. SHARED with the breaker and hub-1 families, so "
                        "hub-2's depth leg grades OFFLINE from the same "
                        "variant cubes a hub-1 factorial produces - zero "
                        "additional engine hours (B2735/B2743)"),
         "subset_safe": False, "status": "UNTESTED",
         "evidence": "smc_ict.py:194", "engine_implemented": True},
        {"id": "P2", "producer": "_smc.ob",
         "param": "close_mitigation", "env": "SMC_OB_CLOSE_MITIGATION",
         # S6-B2885 (owner ruling "Migrate them"): FREE vs RESIM, MEASURED.
         # A level is FREE only if it selects a strict SUBSET of the landed
         # fires AND its discriminating quantity is PERSISTED per trade so the
         # subset can be identified. Across ALL rows of this strategy in
         # output_r5_merged_1_7/trade_log.csv the signal dicts carry 833-837
         # BOOLEAN keys computed AT the production setting, and this knob's
         # discriminator is not among them - so no level is identifiable
         # offline and every one needs the engine. (P6 span looked gradable:
         # below_ema_9/20/21/50/200 ARE persisted, but price_above_ema_200 does
         # not imply price_above_ema_50, so a different span is a DIFFERENT set,
         # not a subset - evaluable is not subset-safe.) METADATA ONLY:
         # production is untouched and no run is scheduled, so no landed grade
         # is recomputed. L726 / L812 / L824.
         "free_band": [],
         "resim_band": [False, True],
         "consumers": ["backtest/config.py",
                       "backtest/engine/exit_strategies.py",
                       "backtest/signals/screener.py"],
         "production": False, "type": "bool", "band": [False, True],
         "derivation": ("whether an order block is mitigated on CLOSE or on "
                        "WICK; the breaker family's P2 precedent"),
         "subset_safe": False, "status": "UNTESTED",
         "evidence": "smc_ict.py:375 (ob call)", "engine_implemented": True},
        {"id": "P3", "producer": "_ob_tap_scan",
        # S6-B2885: an OFFLINE axis (no env knob) is graded from the landed
        # cube, so every level is FREE. Migrated in the SAME pass as this
        # entry's env knobs because leverage() switches encoding on whether ANY
        # param carries free_band/resim_band - migrating half an entry flips it
        # to per-level while leaving the rest invisible, which collapsed this
        # entry's free_combos from 32 to 1 (the B2767 both-encodings hazard).
        "free_band": [3, 5, 10],
        "resim_band": [],
         "param": "tap_window", "production": 5, "type": "int",
         "band": [3, 5, 10],
         "derivation": ("the bounce-tap lookback. NOT ENGINE-REACHABLE: "
                        "smc_ict.py:387 calls _ob_tap_scan passing no "
                        "tap_window and backtest/config.py carries no "
                        "SMC_OB_TAP_WINDOW, so no arm can actuate a level and "
                        "a resim_band here would be a promise the engine "
                        "cannot keep (B2578 class). The persisted key NAME "
                        "also hardcodes the window, so varying it makes the "
                        "key lie. Plumbing ticketed S6-B2752c"),
         "subset_safe": False, "status": "NOT-ENGINE-REACHABLE",
         "evidence": "smc_ict.py:75 (signature default 5); call site 387 "
                     "passes none - MEASURED S6-B2752a",
         "engine_implemented": False},
        {"id": "P4", "producer": "gate threshold (screener)",
        # S6-B2885: an OFFLINE axis (no env knob) is graded from the landed
        # cube, so every level is FREE. Migrated in the SAME pass as this
        # entry's env knobs because leverage() switches encoding on whether ANY
        # param carries free_band/resim_band - migrating half an entry flips it
        # to per-level while leaving the rest invisible, which collapsed this
        # entry's free_combos from 32 to 1 (the B2767 both-encodings hazard).
        "free_band": [45, 40, 35, 30],
        "resim_band": [],
         "param": "rsi_threshold_long", "production": 45, "type": "int",
         "band": [45, 40, 35, 30],
         "derivation": ("FREE - lowering the ceiling keeps a strict SUBSET of "
                        "recorded fires. MEASURED S6-B2752a: rsi_14 is "
                        "persisted on 1340 of 1340 fires and gate-consistent "
                        "per leg (long max 44.99), so it is the AT-ENTRY value "
                        "and the subset property holds"),
         "subset_safe": True, "status": "UNTESTED",
         "evidence": "screener.py:4705 rsi_14<45; rsi_14 persisted",
         "engine_implemented": True},
        {"id": "P5", "producer": "gate threshold (screener)",
        # S6-B2885: an OFFLINE axis (no env knob) is graded from the landed
        # cube, so every level is FREE. Migrated in the SAME pass as this
        # entry's env knobs because leverage() switches encoding on whether ANY
        # param carries free_band/resim_band - migrating half an entry flips it
        # to per-level while leaving the rest invisible, which collapsed this
        # entry's free_combos from 32 to 1 (the B2767 both-encodings hazard).
        "free_band": [55, 60, 65, 70],
        "resim_band": [],
         "param": "rsi_threshold_short", "production": 55, "type": "int",
         "band": [55, 60, 65, 70],
         "derivation": ("FREE - raising the floor keeps a strict subset; "
                        "short min 55.04 measured on the same 1340 fires"),
         "subset_safe": True, "status": "UNTESTED",
         "evidence": "screener.py:4710 rsi_14>55", "engine_implemented": True},
        {"id": "P6", "producer": "gate structure (screener)",
        # S6-B2885: an OFFLINE axis (no env knob) is graded from the landed
        # cube, so every level is FREE. Migrated in the SAME pass as this
        # entry's env knobs because leverage() switches encoding on whether ANY
        # param carries free_band/resim_band - migrating half an entry flips it
        # to per-level while leaving the rest invisible, which collapsed this
        # entry's free_combos from 32 to 1 (the B2767 both-encodings hazard).
        "free_band": ['long', 'short'],
        "resim_band": [],
         "param": "leg", "production": "both", "type": "str",
         "band": ["long", "short"],
         "derivation": "FREE depth axis: per-leg grading of the same cube",
         "subset_safe": True, "status": "UNTESTED",
         "evidence": "dual _strat3 at screener.py:4713",
         "engine_implemented": True},
    ],
    "tools": {
        # only P1/P2 carry env knobs, so only they identify a CUBE; P4-P6 are
        # searched OFFLINE inside one and belong to grid_keys
        "keys": {"P1": "swing", "P2": "close_mitigation"},
        "grid_keys": ["rsi_threshold", "leg"],
        "grade": {"script": "smc_obb_step1.py",
                  "cube": "",                      # the DIRECTORY, not a csv
                  "flags": {"P1": "--swing-length",
                            "P2": "--ob-close-mitigation"},
                  "extra": ["--min-n", "10"],
                  "pythonpath": ".;scripts",
                  "note": "AUTO (S6-B2752e)"},
        "free_levels": None,
        "spot_check": {"script": "spot_check_smc_obb.py",
                       "cube": "",
                       "flags": {"P1": "--swing-length",
                                 "P2": "--ob-close-mitigation"},
                       "extra": ["--n", "50"],
                       "window": False, "precompute_check": False,
                       "pythonpath": ".",
                       "note": ("AUTO (S6-B2752e); hub-2 has its OWN checker - "
                                "pointing it at the breaker or hub-1 checker "
                                "re-derives a condition this strategy does not "
                                "read, which is the B2724 defect. Its LEG A is "
                                "narrower than usual BY MEASUREMENT and says "
                                "so on the artifact's face: the gate's primary "
                                "key is persisted on 0 of 1340 fires")},
        "engine_anchors": {"script": "verify_engine_implemented.py"},
        "single_combination": False,
    },
}

