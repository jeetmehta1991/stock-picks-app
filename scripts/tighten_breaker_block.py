"""Vary tightening levels on smc_breaker_block_long and grade every combination.

THE ECONOMY THAT MAKES THIS FREE: tightening only ever REMOVES fires, so every
tightened variant is a strict SUBSET of R5's fires. The R5 cube already holds
each of those trades under all 26 exits, so a variant is graded by subsetting
the cube -- no resimulation, and the P&L is exact rather than modelled.

Levels are DERIVED, not chosen (L356). Candidate values come from the measured
distributions in B1501: true retests sit at 0.5-2.7pct distance / 45-134 bars
old, latches at 7.5-60pct / 294-469 bars, with an empty gap between. Direction
is an UPPER bound on both axes (L359: a breaker block is a RETEST, so closer
and fresher is stricter).

Gate evaluation delegates to scripts/roster_core.py so the bar is identical to
the one the Phase 1B roster uses. Exit is selected IN-SAMPLE only, then the
holdout is graded once -- the same discipline the roster applies.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import itertools
import json
import sys
from pathlib import Path

import pandas as pd

import roster_core as rc

with contextlib.redirect_stdout(io.StringIO()):
    from vendored.smartmoneyconcepts.smartmoneyconcepts import smc as _smc

STRATEGY = "smc_breaker_block_long"
# B1575: was output_r5_rung4_chunk1 - an ABANDONED alphabetically-
# partitioned chunk (380/381 tickers A-C, no MSFT/NVDA/GOOGL, 248
# tickers the real R5 never ran). L445. The real baseline is
# output_r5_merged_1_7 (544 tickers, A-Z).
R5_CUBE = Path("output_r5_merged_1_7/trade_exit_detail.csv")

# Candidate levels. Each list ANCHORS at the production default (last element)
# so "no change" is always in the grid and the baseline is reproducible.
# P5 break_pct_max: NEW-GATE, OWNER-APPROVED B1507. Production has no such
# parameter (`close > top` is strict). Band from the B1501 measurement: real
# retests 0.5-2.7pct, stale latches 7.5-60pct, empty gap 3-7pct. UPPER bound
# per L359 - a breaker block is a RETEST, so closer is stricter.
BREAK_PCT_MAX = [0.01, 0.02, 0.03, 0.05, None]   # None = production (no cap)
AGE_BARS_MAX = [60, 120, 180, 250, None]         # None = production (no cap)
# B1610/B1611 (owner-approved 2026-08-17). WAS [3, 5, 10, 20] - MEASURED on 420
# cfg2 fires those admit 39.8/68.8/98.6/100.0pct, i.e. three of four levels sat
# PAST saturation and 10->20 moved 0 of 50 cfg1 parameter groups. The region that
# discriminates is 1-3 (tail_n=2 alone cuts 73pct) and it lay BELOW the old floor.
# The plan's own derivation already said rank 1-4; the band never spanned it (L473).
# 20 is RETAINED as the production anchor per plan design-rule 7.
TAIL_N = [1, 2, 3, 5, 10, 20]                    # 20 = production
# P2 close_mitigation (READ smc.py:380). False = mitigated on high/low (production);
# True = mitigated only on CLOSE, strictly fewer mitigations => strictly fewer fires.
CLOSE_MITIGATION = [True, False]                 # False = production


def _load_ohlcv(ticker: str) -> pd.DataFrame | None:
    # B1621: production resolves a ticker to a file via
    # `cache._cache_path`, which normalises `-` and `.` to `_`
    # (BF-B -> BF_B.parquet). This opened `{ticker}.parquet` VERBATIM.
    # Today that lands on correct data only by coincidence - BF-B.parquet is a
    # byte-identical duplicate of BF_B.parquet (VERIFIED `.equals()` True) -
    # but BF.B.parquet is a DIFFERENT 1,316-row series (last close 26.44 vs
    # 26.26), so a cube using dot notation would have been diagnosed against
    # the wrong prices with no error: a file IS found, so the loss-threshold
    # abort never trips. Use the production resolver first.
    _norm = ticker.replace("-", "_").replace(".", "_")
    for rel in (f"backtest/data/cache/ohlcv/{_norm}.parquet",
                f"backtest/data/cache/ohlcv/{ticker}.parquet",
                f"data/cache/ohlcv/{_norm}.parquet",
                f"data/cache/ohlcv/{ticker}.parquet"):
        p = Path(rel)
        if p.exists():
            df = pd.read_parquet(p)
            if not isinstance(df.index, pd.DatetimeIndex) and "date" in df.columns:
                df = df.set_index("date")
            return df.sort_index()
    return None


def diagnose_fire(df: pd.DataFrame, when: pd.Timestamp,
                  swing_length: int = 20,
                  close_mitigation: bool = False) -> dict | None:
    """Recover age_bars / break_pct / rank for the OB events qualifying at `when`.

    PIT preserved: the producer sees ohlc.iloc[:i+1] only, exactly as production.
    """
    locs = df.index.get_indexer([when], method="pad")
    i = int(locs[0])
    if i < 250:
        return None
    sub = df.iloc[:i + 1]
    swings = _smc.swing_highs_lows(sub, swing_length=swing_length)
    ob_df = _smc.ob(sub, swings, close_mitigation=close_mitigation)
    if ob_df is None or "OB" not in ob_df.columns:
        return None
    nz = ob_df[ob_df["OB"].fillna(0) != 0]
    if nz.empty:
        return None
    col = "close" if "close" in sub.columns else "Close"
    close = float(sub[col].iloc[-1])
    pos = {lbl: p for p, lbl in enumerate(ob_df.index)}
    out = []
    for rank, (lbl, row) in enumerate(list(nz.tail(max(TAIL_N)).iterrows())[::-1]):
        ob_val, top, bot = row.get("OB"), row.get("Top"), row.get("Bottom")
        mit = row.get("MitigatedIndex")
        if pd.isna(ob_val) or ob_val == 0 or pd.isna(top) or pd.isna(bot):
            continue
        if (not pd.isna(mit)) and mit > 0 and int(mit) < i \
                and ob_val == -1 and close > float(top):
            out.append({"rank": rank,
                        "age_bars": i - pos.get(lbl, i),
                        "break_pct": (close - float(top)) / float(top)})
    return {"events": out} if out else None


def survives(diag: dict, break_max, age_max, tail_n) -> bool:
    """A fire survives if ANY qualifying event satisfies every active cap."""
    for e in diag["events"]:
        if e["rank"] >= tail_n:
            continue
        if break_max is not None and e["break_pct"] > break_max:
            continue
        if age_max is not None and e["age_bars"] > age_max:
            continue
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="output_audit/b1502_tightening_grid.json")
    ap.add_argument("--limit-tickers", type=int, default=0)
    ap.add_argument("--cube", default="", help="cube to grade against; default R5")
    ap.add_argument("--tickers-file", default="")
    # S6-B1584a: the grader RE-DERIVES every fire from OHLCV. Re-deriving
    # with different producer params than the run that made the cube means
    # fires cannot reproduce and are DROPPED. cfg2 ran sw=10, was graded at
    # the hardcoded 20, and lost 167 of 420 fires - a biased 60pct
    # subsample, not a random one.
    ap.add_argument("--swing-length", type=int, default=20,
                    help="SMC_SWING_LENGTH the CUBE was generated with")
    # S6-B1584c (owner ruling 2026-08-15): Step 1 ranks on 100 tickers x 2y,
    # ~1/5 the ticker-days MIN_N=30 was calibrated for. 30 produced
    # NO_EXIT_SELECTABLE on 84-92pct of combinations - a sample-size verdict
    # dressed as an exit-quality one. NEVER changes roster_core.MIN_N.
    # B1605 (owner ruling 2026-08-16): STEP 1 selects the best exit by
    # SHARPE alone - it is a cheap RANKING pass. STEP 2 re-ranks ALL 26
    # exits and takes the one clearing the MOST GATES, which is the
    # admission criterion. Separating the two removes the need for any
    # selection-noise haircut: Step 1 never decides admission.
    ap.add_argument("--objective", choices=("sharpe", "gates"),
                    default="sharpe",
                    help="STEP 1 = sharpe (rank). STEP 2 = gates (admit).")
    ap.add_argument("--min-n", type=int, default=10,
                    help="SEARCH-phase min trades (owner: 10)")
    # B1608: STEP 1 produces "ranked combinations" per plan section 10.1 -
    # NOT gate verdicts. The script had been applying all six admission
    # gates and emitting PASS/FAIL, so "0 PASS across 400 combinations"
    # was reported as a Step-1 result when Step 1 was never meant to
    # produce a PASS. Gates belong to STEP 2 (L471).
    ap.add_argument("--rank-only", action="store_true", default=True,
                    help="STEP 1: emit a SHARPE-RANKED list, no gate "
                         "verdicts. Excludes NO_EXIT_SELECTABLE.")
    ap.add_argument("--top-n", type=int, default=10,
                    help="how many ranked combinations go to STEP 2 "
                         "(plan section 10.1: top 10)")
    ap.add_argument("--max-diag-loss", type=float, default=0.02,
                    help="abort if more than this fraction of fires cannot be re-diagnosed")
    a = ap.parse_args()

    # B1623 (S6-B1620c): a dropped ticker used to vanish silently. Counted and
    # surfaced now, and ABORTED above a threshold - a silent drop is a BIASED
    # subsample, which is exactly how cfg2 lost 167 of 420 fires and reported
    # metrics on the survivors as though they were the population (L454).
    DROPS: dict = {"no_parquet": [], "no_diag": []}
    cube = rc.load_cube(Path(a.cube) if a.cube else R5_CUBE)
    g = cube[cube["strategy"] == STRATEGY].copy()
    # load_cube yields entry_date as datetime.date; roster_core's window
    # helpers compare against date objects, so do NOT convert to datetime64.
    fires = g[["ticker", "entry_date"]].drop_duplicates()
    print(f"R5 baseline: {len(fires)} fires x {g.exit_method.nunique()} exits "
          f"= {len(g)} cube rows")

    tickers = sorted(fires.ticker.unique())
    if a.tickers_file:
        allow = {l.strip() for l in open(a.tickers_file) if l.strip()}
        before = len(tickers)
        tickers = [t for t in tickers if t in allow]
        fires = fires[fires.ticker.isin(tickers)]
        print(f"ticker filter {a.tickers_file}: {before} -> {len(tickers)} tickers, "
              f"{len(fires)} fires retained")
    if a.limit_tickers:
        tickers = tickers[:a.limit_tickers]

    # One instrumented pass per fire; results reused by every combination.
    diags: dict[bool, dict] = {cm: {} for cm in CLOSE_MITIGATION}
    for t in tickers:
        df = _load_ohlcv(t)
        if df is None:
            # B1623: was a bare `continue`. A whole ticker vanishing without a
            # counter is the cfg2 defect wearing a different costume - the run
            # completes, the numbers look self-consistent, and they describe a
            # subsample nobody chose.
            DROPS["no_parquet"].append(t)
            continue
        for when in fires[fires.ticker == t].entry_date:
            for cm in CLOSE_MITIGATION:
                d = diagnose_fire(df, pd.Timestamp(when),
                                  swing_length=a.swing_length,
                                  close_mitigation=cm)
                if d:
                    diags[cm][(t, when)] = d
                else:
                    # S6-B1584b / #122: the third silent swallow. `DROPS`
                    # declared this key at the top and NOTHING ever wrote to
                    # it, so a falsy diagnosis was only ever inferable from a
                    # shortfall. The UNION gate below already catches a fire no
                    # branch can diagnose - this makes it COUNTED rather than
                    # inferred, which is what #122 asks for.
                    DROPS["no_diag"].append((t, str(when), cm))
    # S6-B1586: the loss gate must apply to the UNION of branches, not each
    # one. close_mitigation is a SWEPT dimension: cm=True is a strictly tighter
    # variant that is SUPPOSED to find fewer order blocks. Checking each branch
    # separately flagged a variant doing its job as a 4pct failure. A fire is
    # genuinely un-reproducible only if NO branch can diagnose it - that is what
    # indicates the grader cannot reconstruct what the engine did.
    union = set()
    for cm in CLOSE_MITIGATION:
        union |= set(diags[cm].keys())
    n_f = len(fires)
    # B1623 (S6-B1620c): surface the drops BEFORE any metric is printed, and
    # abort if they are material. Silence here is what let a biased 60pct
    # subsample be reported as a result (L454).
    if DROPS["no_parquet"]:
        lost = int(fires[fires.ticker.isin(DROPS["no_parquet"])].shape[0])
        share = lost / n_f if n_f else 0.0
        print(f"DROPPED {len(DROPS['no_parquet'])} tickers with no parquet "
              f"({lost} fires, {share:.1%}): {sorted(DROPS['no_parquet'])[:8]}")
        if share > a.max_diag_loss:
            print(f"ABORT: dropped-ticker share {share:.1%} exceeds "
                  f"--max-diag-loss {a.max_diag_loss:.1%}. Metrics computed on "
                  f"the survivors would describe a subsample nobody chose.",
                  file=sys.stderr)
            return 2
    # S6-B1584b: report the per-branch falsy diagnoses BEFORE any metric, on
    # the same footing as the no_parquet drops. A branch-level drop is not
    # itself a defect - a tighter close_mitigation legitimately finds fewer
    # order blocks - so this is REPORTED, and the UNION gate below is what
    # decides whether anything is wrong.
    if DROPS["no_diag"]:
        by_branch: dict = {}
        for _t, _w, _cm in DROPS["no_diag"]:
            by_branch[_cm] = by_branch.get(_cm, 0) + 1
        print(f"UNDIAGNOSED (branch-level, not necessarily lost): "
              f"{len(DROPS['no_diag'])} fire-branch pairs {by_branch}")
    union_loss = 1.0 - (len(union) / n_f) if n_f else 0.0
    for cm in CLOSE_MITIGATION:
        print(f"close_mitigation={cm}: diagnosed {len(diags[cm])} of {n_f} "
              f"fires (branch-level; tighter branches legitimately find fewer)")
    print(f"UNION across branches: {len(union)} of {n_f} "
          f"({union_loss:.1%} un-reproducible)")
    for cm in [CLOSE_MITIGATION[0]]:
        n_d = len(union)
        loss = union_loss
        print(f"close_mitigation={cm}: diagnosed {n_d} of {n_f} fires "
              f"({loss:.1%} lost)")
        # S6-B1584b: this line ALWAYS printed the shortfall and nothing
        # ever asserted on it, so a 40pct loss sat in plain sight. A silent
        # subsample is worse than a crash - it yields plausible metrics on
        # a biased population.
        if loss > a.max_diag_loss:
            raise SystemExit(
                "FATAL: {:.1%} of fires could not be re-diagnosed (limit {:.1%}). "
                    "The grader re-derives fires from OHLCV; if "
                    "--swing-length ({}) does not match the "
                    "SMC_SWING_LENGTH the cube was RUN with, fires cannot "
                    "reproduce and would be dropped silently, biasing "
                    "every metric. Pass the correct --swing-length or "
                    "raise --max-diag-loss deliberately."
                    .format(loss, a.max_diag_loss, a.swing_length))

    rows = []
    for cm, bmax, amax, tn in itertools.product(
            CLOSE_MITIGATION, BREAK_PCT_MAX, AGE_BARS_MAX, TAIL_N):
        keep = {k for k, d in diags[cm].items() if survives(d, bmax, amax, tn)}
        if not keep:
            rows.append({"close_mitigation": cm, "break_pct_max": bmax,
                         "age_bars_max": amax, "tail_n": tn, "fires": 0,
                         "verdict": "ZERO_FIRES"})
            continue
        sub = g[[(r.ticker, r.entry_date) in keep
                 for r in g.itertuples()]]
        is_m = rc.in_sample(sub)
        ho_m = rc.holdout(sub)
        # B1715 DIAGNOSTIC ONLY - the ranking is untouched. `select_exit`
        # already computes IN-SAMPLE stats for the chosen exit and the caller
        # discarded them. Keeping the IS Sharpe lets the P0-2 selection leak be
        # MEASURED (step-1 ranks 300 combinations by HOLDOUT Sharpe, line ~334)
        # without changing what step 1 delivers, which would need owner approval.
        exit_pick, _is_stats = rc.select_exit(is_m, objective=a.objective,
                                              min_n=a.min_n)
        if exit_pick is None:
            rows.append({"close_mitigation": cm, "break_pct_max": bmax,
                         "age_bars_max": amax, "tail_n": tn, "fires": len(keep),
                         "verdict": "NO_EXIT_SELECTABLE"})
            continue
        hb = ho_m[ho_m.exit_method == exit_pick]
        fp_n = int((sub.exit_method == exit_pick).sum())
        res = rc.evaluate(hb["pnl_pct"], hb["hold_days"],
                          min_n=a.min_n, full_period_n=fp_n)
        row = {"close_mitigation": cm, "break_pct_max": bmax,
               "age_bars_max": amax, "tail_n": tn,
               "fires": len(keep), "exit": exit_pick,
               "holdout_n": len(hb), "full_period_n": fp_n,
               # B1715: diagnostic, never ranked on.
               "is_sharpe": (_is_stats or {}).get("sharpe")}
        if res is None:
            row["verdict"] = "BELOW_POWER_FLOOR"
        else:
            gates = {k: bool(res["gates"][k]) for k in rc.LIVE_GATES}
            row.update({k: res.get(k) for k in
                        ("sharpe", "sortino", "psr", "profit_factor", "payoff",
                         "expectancy", "win_rate", "p", "ci_lo")})
            row.update({"gates": gates,
                        "gates_passed": sum(gates.values()),
                        "verdict": "PASS" if all(gates.values()) else "FAIL"})
        rows.append(row)

    rows.sort(key=lambda r: (-(r.get("gates_passed") or 0), -(r.get("fires") or 0)))
    # B1608: STEP-1 DELIVERABLE - a Sharpe-ranked list with NO gates applied,
    # NO_EXIT_SELECTABLE excluded (owner ruling 2026-08-17). The per-combination
    # `gates`/`verdict` fields remain in the payload for STEP 2, but the ranking
    # below is what Step 1 hands forward.
    rankable = [r for r in rows if r.get("verdict") != "NO_EXIT_SELECTABLE"
                and r.get("sharpe") is not None
                # B1718: an IS Sharpe is now REQUIRED - it is the ranking key.
                and r.get("is_sharpe") is not None]
    # B1615 OPTION D (owner-approved 2026-08-17): rank DISTINCT OUTCOMES and
    # carry the whole equivalence class forward. Ranking ROWS meant the top 10
    # held only 4 real candidates on cfg2 - combinations differing solely in a
    # SATURATED parameter are the SAME FIRE SET, so they occupied slots without
    # adding evidence and crowded out 6 genuine candidates (L473).
    #
    # We do NOT collapse to a member. Which member to deploy is decided ONCE, at
    # ADMISSION, by taking the PRODUCTION-CLOSEST value - a tie is not evidence
    # to change production. Collapsing at Step 1 would also destroy real
    # information: the class is SAMPLE-SPECIFIC, and if it SPLITS on Step 2's
    # wider universe that split is itself the finding (S6-B1612e).
    #
    # Carrying the class is free for a SUBSET-SAFE parameter - MEASURED at
    # 0.01-0.03 s per extra combination against a 3.5 s fixed diagnosis. It is
    # NOT free for a FIRE-ADDING one (swing_length, EMA span), where each value
    # needs its own engine run; those are the sweep's CONFIGS and are never
    # carried as a class (plan section 6b).
    classes: dict[tuple, list] = {}
    # B1718 P0-2 (owner-approved): rank on the IN-SAMPLE Sharpe. Ranking on
    # `sharpe` - the HOLDOUT Sharpe - meant 300 combinations were ordered by
    # out-of-sample performance and the top-10 carried forward: best-of-300
    # selection on the very data reserved to judge it.
    #
    # This does NOT make the winners better. MEASURED Spearman between IS and
    # holdout Sharpe is -0.779 / -0.865, so the IS-ranked top-10 will very
    # likely score WORSE out of sample than the old holdout-ranked one. That is
    # the point: the old number was leaked, the new one is honest. Removing a
    # leak and finding an edge are different jobs, and only the first is a bug
    # fix.
    #
    # `sharpe` remains in every row as the holdout MEASUREMENT of whatever the
    # in-sample ranking selected - reported, never ranked on.
    for r in sorted(rankable, key=lambda r: -(r.get("is_sharpe")
                                              if r.get("is_sharpe") is not None else -9)):
        # B1718: equivalence collapses on the IS Sharpe too, since that is now
        # the ranking key - two combos with the same fires/exit/IS-Sharpe are
        # the same STEP-1 outcome.
        key = (r.get("fires"), r.get("exit"), round(r.get("is_sharpe"), 9))
        classes.setdefault(key, []).append(r)
    ranked = list(classes.values())[:a.top_n]
    carried = sum(len(c) for c in ranked)
    print(f"\nSTEP-1 RANKING (no gates; {len(rankable)} rankable of {len(rows)}; "
          f"{len(rows) - len(rankable)} excluded as NO_EXIT_SELECTABLE)")
    print(f"{len(classes)} DISTINCT outcomes; top {len(ranked)} carry "
          f"{carried} combinations to STEP 2")
    # B1905: PRINT THE KEY THIS LIST IS RANKED ON.
    #
    # B1820 added `is_sharpe` to the JSON artifact and wrote the reason down:
    # without it "an auditor would conclude Step 1 ranks on the holdout - the
    # exact defect B1718 fixed. The separation was real and unverifiable from
    # its own output." **That fix went to the JSON and not to this table**,
    # which renders the same ranked list.
    #
    # MEASURED on output_audit/b1820_cfg2_ranked.json: rank 1 has
    # is_sharpe=3.373 and sharpe=-0.077, and the printed column is NOT
    # descending. With the measured IS-vs-holdout Spearman at -0.779/-0.865
    # that is the EXPECTED shape - so the console showed a list sorted by an
    # invisible key with its worst-looking number at the top.
    #
    # Missing values route through `measured.fmt` rather than `float("nan")`:
    # a value nobody measured must not render as a number (L580).
    import measured as _measured

    def _f(v, spec=".3f"):
        return _measured.fmt(v, spec=spec)

    print(f"{'#':>3} {'is_sharpe':>10} {'ho_sharpe':>10} {'ci_lo':>8} "
          f"{'fires':>7} {'cls':>4}  {'exit':<22} class members (tail_n)")
    print("    ranked on is_sharpe (IN-SAMPLE, B1718). ho_sharpe is the "
          "HOLDOUT measurement of what the in-sample ranking picked - "
          "reported, NEVER ranked on, and negatively correlated with the key.")
    for i, members in enumerate(ranked, 1):
        r = members[0]
        print(f"{i:>3} {_f(r.get('is_sharpe')):>10} {_f(r.get('sharpe')):>10} "
              f"{_f(r.get('ci_lo')):>8} "
              f"{r.get('fires', 0):>7} {len(members):>4}  {str(r.get('exit')):<22} "
              f"{sorted(m['tail_n'] for m in members)}")

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(
        {"strategy": STRATEGY, "r5_baseline_fires": len(fires),
         # B1517: was len(diags) which, after close_mitigation became the outer
         # key, reported 2 (the number of flag values) instead of the fire count.
         "diagnosed": {str(k): len(v) for k, v in diags.items()},
         # B1615: one entry per DISTINCT outcome. `members` is the full
         # equivalence class - every parameter tuple that produces this exact
         # fire set - and ALL of them are graded in Step 2. `admit` names the
         # production-closest member, which is the tie-break applied only if
         # the class survives Step 2 intact.
         "step1_ranking": [
             # S6-B1705c/B1820: emit `is_sharpe` FIRST - it is the key this
             # list is ranked on (B1718). Without it the artifact showed only
             # `sharpe`, the HOLDOUT measurement, so an auditor would conclude
             # Step 1 ranks on the holdout - the exact defect B1718 fixed. The
             # separation was real and unverifiable from its own output.
             {"rank": i, "is_sharpe": c[0].get("is_sharpe"),
              "sharpe": c[0].get("sharpe"), "ci_lo": c[0].get("ci_lo"),
              "fires": c[0].get("fires"), "exit": c[0].get("exit"),
              "class_size": len(c),
              "admit": max(c, key=lambda m: (m["tail_n"],
                                             m["age_bars_max"] is None,
                                             m["break_pct_max"] is None,
                                             not m["close_mitigation"])),
              "members": [{"close_mitigation": m.get("close_mitigation"),
                           "break_pct_max": m.get("break_pct_max"),
                           "age_bars_max": m.get("age_bars_max"),
                           "tail_n": m.get("tail_n")} for m in c]}
             for i, c in enumerate(ranked, 1)],
         "step1_combinations_carried": sum(len(c) for c in ranked),
         "step1_distinct_outcomes": len(classes),
         "results": rows}, indent=2))

    # B1623 (S6-B1620d): STEP 1 no longer PRINTS gate verdicts. They stay in the
    # payload for STEP 2, but printing a PASS/FAIL column here is what produced
    # "0 PASS across 400 combinations" reported as a Step-1 result - a category
    # error, since Step 1 can never produce a PASS (L471, CHECKLIST #202). With
    # 18 configs to come, that output would have been read 18 more times.
    print(f"\n{'cm':>6} {'break':>6} {'age':>5} {'tail':>4} {'fires':>6} "
          f"{'ho_n':>5} {'fp_n':>5} {'sharpe':>7}   (STEP 1 = RANKING, no gates)")
    for r in rows[:18]:
        print(f"{str(r['close_mitigation']):>6} {str(r['break_pct_max']):>6} "
              f"{str(r['age_bars_max']):>5} "
              f"{r['tail_n']:>4} {r.get('fires', 0):>6} "
              f"{(r.get('holdout_n') if r.get('holdout_n') is not None else '-'):>5} "
              f"{r.get('full_period_n', 0):>5} "
              f"{(f'{r.get(chr(115)+chr(104)+chr(97)+chr(114)+chr(112)+chr(101)):.3f}' if r.get('sharpe') is not None else '-'):>7}")
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
