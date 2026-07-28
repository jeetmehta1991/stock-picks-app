"""scripts/build_exit_reassignment.py (B1415) -- propose EXIT reassignments, guarded against
the one thing we already know about exits: they overfit.

WHY THIS EXISTS
The owner's correction (B1412) showed the exit dominates the entry filter - `camarilla_r4_breakout`
is +3.235% on `breakeven_plus_trail` versus +0.389% with my best entry filter on its assigned
exit. So exit reassignment is the larger lever.

WHY IT IS DANGEROUS, AND WHAT THAT IMPLIES
L227, measured on this same cube: **exit selection transfers poorly** - an IS-picked exit cleared
the 0.7 holdout bar on 5.9% of rows against a hindsight oracle's 17.6%, i.e. about a third.
"Optimized exits are the most overfit component; `time_stop_10d` (a dumb time stop) is the exit
on 5 of the 11 R5 survivors." Naive argmax over 26 exits is therefore precisely the wrong
instrument: with 26 candidates per strategy the maximum is a high-variance statistic, and the
strategy with the luckiest exit wins the search rather than the one with the best exit.

GUARDS (all must hold; each targets a specific way argmax lies)
  1 CONSISTENCY   the proposed exit must be top-quartile in >= 2 of the 3 IS folds, not merely
                  best on the pooled window. This is the direct answer to L227: an exit that is
                  best only because of one good year is what fails out of sample.
  2 MARGIN        it must beat the CURRENT assigned exit by >= --min-margin expectancy, so we
                  do not churn an assignment for noise.
  3 SIGNIFICANCE  the pooled difference vs the current exit must clear a DATE-CLUSTERED test
                  (L244 - trades sharing a day are not independent observations).
  4 SAMPLE        >= --min-trades trades on the proposed exit.
  5 SIMPLICITY    reported, not enforced: whether the proposal is one of the structurally simple
                  exits (time stops, breakeven trails), which L227 found transfer best. A
                  complex exit winning by a small margin deserves more suspicion than a simple
                  one winning by a large margin.

IS window only; the holdout is never read.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402

from walk_forward_r5_cells import bh_fdr  # noqa: E402

IS_START, IS_END = date(2022, 5, 5), date(2025, 5, 5)
FOLDS = [(date(2022, 5, 5), date(2023, 5, 5)), (date(2023, 5, 5), date(2024, 5, 5)),
         (date(2024, 5, 5), date(2025, 5, 5))]
WINSORIZE, COST_BPS = 300.0, 20.0
SIMPLE_EXITS = {"time_stop_10d", "time_stop_20d", "class_time_stop", "breakeven_plus_trail",
                "break_even_at_1r", "atr_trail_1x", "atr_trail_2x"}


def clustered_p(a_pnl, a_dates, b_pnl, b_dates) -> float:
    """One-sided test that mean(a) > mean(b), on DATE-CLUSTERED means (L244)."""
    A = pd.DataFrame({"d": list(a_dates), "p": list(a_pnl)}).groupby("d")["p"].mean()
    B = pd.DataFrame({"d": list(b_dates), "p": list(b_pnl)}).groupby("d")["p"].mean()
    if len(A) < 10 or len(B) < 10:
        return 1.0
    se = math.sqrt(A.var(ddof=1) / len(A) + B.var(ddof=1) / len(B))
    if se <= 0:
        return 1.0
    return 0.5 * math.erfc(((A.mean() - B.mean()) / se) / math.sqrt(2.0))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-trades", type=int, default=100)
    ap.add_argument("--min-margin", type=float, default=0.50,
                    help="minimum expectancy advantage (pct/trade) over the CURRENT exit")
    ap.add_argument("--min-consistent-folds", type=int, default=2,
                    help="proposed exit must be top-quartile in at least this many of 3 IS folds")
    ap.add_argument("--fdr-q", type=float, default=0.05)
    ap.add_argument("--output", default="output_audit/b1415_exit_reassignment.json")
    args = ap.parse_args()

    print("[INFO] loading cube (per-exit pnl) + trade_log (current assignment) ...")
    cube = pd.read_csv(REPO / "output_r5_merged_1_7" / "trade_exit_detail.csv", low_memory=False,
                       usecols=["strategy", "ticker", "entry_date", "exit_method", "pnl_pct"])
    cube["entry_date"] = pd.to_datetime(cube["entry_date"]).dt.date
    cube = cube[(cube.entry_date >= IS_START) & (cube.entry_date < IS_END)]
    cube["pnl_pct"] = cube["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0

    cur = {}
    for ch in pd.read_csv(REPO / "output_r5_merged_1_7" / "trade_log.csv", chunksize=200000,
                          low_memory=False, usecols=["strategy", "exit_method"]):
        for s, g in ch.groupby("strategy"):
            cur.setdefault(s, g.exit_method.mode().iloc[0] if len(g) else None)
    print(f"[INFO] {cube.strategy.nunique()} strategies in cube; {len(cur)} current assignments")

    props, naive_only = [], 0
    for s, sd in cube.groupby("strategy"):
        cur_exit = cur.get(s)
        if cur_exit is None or cur_exit not in set(sd.exit_method):
            continue
        agg = sd.groupby("exit_method").pnl_pct.agg(n="size", exp="mean",
                                                    wr=lambda p: (p > 0).mean())
        agg = agg[agg.n >= args.min_trades]
        if len(agg) < 2 or cur_exit not in agg.index:
            continue
        best = agg.exp.idxmax()
        if best == cur_exit:
            continue
        naive_only += 1
        margin = float(agg.loc[best, "exp"] - agg.loc[cur_exit, "exp"])
        # GUARD 1 - per-fold consistency (the direct answer to L227)
        consistent = 0
        for lo, hi in FOLDS:
            f = sd[(sd.entry_date >= lo) & (sd.entry_date < hi)]
            fa = f.groupby("exit_method").pnl_pct.agg(n="size", exp="mean")
            fa = fa[fa.n >= 20]
            if best in fa.index and len(fa) >= 4:
                if fa.loc[best, "exp"] >= fa.exp.quantile(0.75):
                    consistent += 1
        b = sd[sd.exit_method == best]
        c = sd[sd.exit_method == cur_exit]
        p = clustered_p(b.pnl_pct, b.entry_date, c.pnl_pct, c.entry_date)
        props.append({
            "strategy": s, "current_exit": cur_exit, "proposed_exit": best,
            "exp_current": round(float(agg.loc[cur_exit, "exp"]), 4),
            "exp_proposed": round(float(agg.loc[best, "exp"]), 4),
            "margin": round(margin, 4),
            "wr_current": round(float(agg.loc[cur_exit, "wr"]), 4),
            "wr_proposed": round(float(agg.loc[best, "wr"]), 4),
            "n_proposed": int(agg.loc[best, "n"]),
            "consistent_folds": consistent, "p_date_clustered": p,
            "proposed_is_simple_exit": best in SIMPLE_EXITS,
        })

    if props:
        rej, thr = bh_fdr([p["p_date_clustered"] for p in props], q=args.fdr_q)
        for p_, ok in zip(props, rej):
            p_["bh_reject"] = bool(ok)
    survivors = [p for p in props
                 if p.get("bh_reject") and p["margin"] >= args.min_margin
                 and p["consistent_folds"] >= args.min_consistent_folds
                 and p["n_proposed"] >= args.min_trades]
    survivors.sort(key=lambda p: -p["margin"])

    print(f"\n[RESULT] {naive_only} strategies where NAIVE argmax would change the exit")
    print(f"         {sum(1 for p in props if p.get('bh_reject'))} clear date-clustered BH-FDR")
    print(f"         {sum(1 for p in props if p['margin'] >= args.min_margin)} clear the "
          f"{args.min_margin}% margin over the current exit")
    print(f"         {sum(1 for p in props if p['consistent_folds'] >= args.min_consistent_folds)} "
          f"are top-quartile in >= {args.min_consistent_folds} of 3 IS folds (the L227 guard)")
    print(f"         **{len(survivors)} pass ALL guards**\n")
    print(f"  {'strategy':<40}{'current':<22}{'proposed':<22}{'exp gain':>10}{'folds':>7}{'simple':>8}")
    for p_ in survivors[:25]:
        print(f"  {p_['strategy']:<40}{p_['current_exit']:<22}{p_['proposed_exit']:<22}"
              f"{p_['margin']:>+10.2f}{p_['consistent_folds']:>7}"
              f"{('yes' if p_['proposed_is_simple_exit'] else 'no'):>8}")
    out = REPO / args.output
    out.write_text(json.dumps({"window": [str(IS_START), str(IS_END)], "holdout_touched": False,
                               "guards": {"min_trades": args.min_trades, "min_margin": args.min_margin,
                                          "min_consistent_folds": args.min_consistent_folds,
                                          "fdr_q": args.fdr_q},
                               "n_naive_argmax_changes": naive_only,
                               "n_passing_all_guards": len(survivors),
                               "proposals": survivors, "all_candidates": props}, indent=2),
                   encoding="utf-8")
    print(f"\n[OK] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
