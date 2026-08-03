"""scripts/canonical_criteria_check.py (B1387) -- run the FULL canonical PASSING_CRITERIA
against the promoted R5 cells, before any 1B-alpha commitment.

Owner decision 2026-07-26 (c): "compute the remaining canonical criteria before 1B-alpha."

The R5 holdout gate tests three things (n-floor, Sharpe bar, BH-FDR). The project's canonical
`PASSING_CRITERIA` has 14 criteria + 3 AUTO-FAIL screens. This script closes that gap for the
promoted set using the EXISTING implementations in `backtest/results/metrics.py` -- deflated
Sharpe / PSR, Sortino, Calmar, max drawdown, cost-sensitivity, Chow break-point, ADF -- rather
than reimplementing any of them, so the numbers here are the same ones a canonical backtest
would produce.

Evaluated on the HOLDOUT fold (2025-05-05 -> 2026-05-05) on NET winsorized per-trade returns,
i.e. the same data the promotion verdict was made on.

Note on win rate: per the owner's B1387 ruling it is a DIAGNOSTIC, not a gate
(`PASSING_CRITERIA["win_rate_gate"] = False`) -- it is reported below, never gated on.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backtest.config import PASSING_CRITERIA as PC          # noqa: E402
from backtest.results.metrics import (                       # noqa: E402
    _max_drawdown, _calmar, _sortino_ratio, _deflated_sharpe,
    _cost_sensitivity_sharpe, _chow_test, _adf_test,
)
from walk_forward_r5_cells import _sharpe                    # noqa: E402

CUBE = REPO / "output_r5_merged_1_7"
HO = (date(2025, 5, 5), date(2026, 5, 5))
WINSORIZE, COST_BPS = 300.0, 20.0


def main() -> int:
    # B1435: made set-selectable. Previously hardcoded to the B1387 promoted cells,
    # so grading any OTHER candidate set meant reimplementing the criteria - exactly
    # what this script exists to prevent. --strategies-file + --exit let it grade any
    # roster at any exit while still reusing the metrics.py implementations.
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategies-file", default=None,
                    help="newline-delimited strategy names; default = B1387 promoted cells")
    ap.add_argument("--exit", default=None,
                    help="grade every strategy at THIS exit (required with --strategies-file, "
                         "since a bare strategy name does not identify a cube cell)")
    ap.add_argument("--label", default="the promoted cells")
    ap.add_argument("--output", default="output_audit/b1387_canonical_criteria.json")
    args = ap.parse_args()

    df = pd.read_csv(CUBE / "trade_exit_detail.csv",
                     usecols=["strategy", "direction", "exit_method", "entry_date",
                              "pnl_pct", "hold_days"], low_memory=False)

    if args.strategies_file:
        if not args.exit:
            raise SystemExit("[B1435] --strategies-file requires --exit: a strategy name alone "
                             "does not identify a (strategy x direction x exit) cube cell.")
        want = {ln.strip() for ln in Path(args.strategies_file).read_text(
            encoding="utf-8").splitlines() if ln.strip()}
        sub = df[(df.strategy.isin(want)) & (df.exit_method == args.exit)]
        keys = set(map(tuple, sub[["strategy", "direction", "exit_method"]].drop_duplicates().values))
        missing = want - {k[0] for k in keys}
        print(f"[INFO] {len(want)} requested | {len(keys)} cells resolved at exit={args.exit}"
              + (f" | ABSENT from cube: {len(missing)}" if missing else ""))
        if missing:
            print(f"[WARN] not in cube at this exit: {sorted(missing)[:10]}"
                  + (" ..." if len(missing) > 10 else ""))
    else:
        graded = json.loads((CUBE / "passed_strategy_exit_holdout_graded.json").read_text(encoding="utf-8"))
        promoted = [r for r in graded["rows"] if r["verdict"] == "PASS" and not r.get("redundant_of")]
        keys = {(r["strategy"], r["direction"], r["exit"]) for r in promoted}
        print(f"[INFO] {len(promoted)} promoted cells | canonical criteria from backtest/config.py")
    print(f"[INFO] win_rate_gate={PC.get('win_rate_gate')} (B1387: diagnostic, not gated)")

    df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    df["pnl_pct"] = df["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0
    df = df[(df.entry_date >= HO[0]) & (df.entry_date < HO[1])]

    out = []
    for s, d, e in sorted(keys):
        g = df[(df.strategy == s) & (df.direction == d) & (df.exit_method == e)].sort_values("entry_date")
        if g.empty:
            continue
        pnl, hold = g["pnl_pct"], g["hold_days"]
        n = len(pnl)
        sh = _sharpe(pnl.values, hold.values)
        sharpe = sh["sharpe"] if sh else None
        eq = pnl.cumsum()
        mdd = _max_drawdown(pnl)
        sortino = _sortino_ratio(pnl, hold)
        calmar = _calmar(pnl, hold)
        dsr = _deflated_sharpe(sharpe or 0.0, n, float(pnl.skew()), float(pnl.kurtosis()))
        cs = _cost_sensitivity_sharpe(pnl, hold)
        chow = _chow_test(eq)
        adf = _adf_test(eq)
        wins, loss = pnl[pnl > 0], pnl[pnl <= 0]
        pf = float(wins.sum() / abs(loss.sum())) if len(loss) and loss.sum() != 0 else float("inf")
        r = {
            "strategy": s, "direction": d, "exit": e, "n": n,
            "sharpe": sharpe, "win_rate": round(float((pnl > 0).mean()), 3),
            "profit_factor": round(pf, 2), "max_drawdown": round(float(mdd), 2),
            "sortino": sortino, "calmar": calmar,
            "psr": dsr.get("psr"), "deflated_sharpe": dsr.get("deflated_sharpe"),
            "cost_sensitivity_ratio": cs.get("ratio") if isinstance(cs, dict) else cs,
            "chow_p": chow.get("p_value") if isinstance(chow, dict) else None,
            "chow_post_sharpe": chow.get("post_break_sharpe") if isinstance(chow, dict) else None,
            "adf_p": adf.get("p_value") if isinstance(adf, dict) else None,
        }
        gates = {
            "sharpe_per_regime": (sharpe is not None and sharpe >= PC["min_sharpe_per_regime"]),
            "profit_factor": pf >= PC["min_profit_factor_overall"],
            # B1436: honour the config flags rather than hardcoding the gate, so this
            # script cannot drift from what a canonical backtest actually gates on.
            "max_drawdown": (not PC.get("max_drawdown_gate", True))
                            or float(mdd) >= -PC["max_drawdown"],
            "sortino": (sortino is not None and sortino >= PC["min_sortino_per_regime"]),
            "calmar": (calmar is not None and calmar >= PC["min_calmar"]),
            "psr": (r["psr"] is not None and r["psr"] >= PC["min_psr"]),
            "deflated_sharpe": (not PC.get("deflated_sharpe_gate", True))
                               or (r["deflated_sharpe"] is not None
                                   and r["deflated_sharpe"] >= PC["min_deflated_sharpe"]),
            "min_trades": n >= PC["min_trades"],
        }
        r["gates"] = gates
        r["n_gates_passed"] = sum(1 for v in gates.values() if v)
        r["all_gates"] = all(gates.values())
        out.append(r)

    print("\n" + "=" * 108)
    print(f"FULL CANONICAL CRITERIA on {args.label} (holdout fold, NET winsorized)")
    print("=" * 108)
    names = ["sharpe_per_regime", "profit_factor", "max_drawdown", "sortino",
             "calmar", "psr", "deflated_sharpe", "min_trades"]
    print(f"  {'criterion':<26}{'threshold':>12}{'clearing':>12}")
    thr = {"sharpe_per_regime": PC["min_sharpe_per_regime"], "profit_factor": PC["min_profit_factor_overall"],
           "max_drawdown": f"> -{PC['max_drawdown']}", "sortino": PC["min_sortino_per_regime"],
           "calmar": PC["min_calmar"], "psr": PC["min_psr"],
           "deflated_sharpe": PC["min_deflated_sharpe"], "min_trades": PC["min_trades"]}
    for k in names:
        print(f"  {k:<26}{str(thr[k]):>12}{sum(1 for r in out if r['gates'][k]):>8}/{len(out)}")
    print(f"\n  ALL canonical gates simultaneously: {sum(1 for r in out if r['all_gates'])}/{len(out)}")
    print(f"  (win rate reported but NOT gated per B1387 owner ruling)")

    print(f"\n  {'strategy':<42}{'shrp':>6}{'sortino':>8}{'calmar':>8}{'PSR':>7}{'DSR':>7}"
          f"{'MDD':>9}{'n':>6}{'gates':>7}")
    for r in sorted(out, key=lambda x: -x["n_gates_passed"]):
        f = lambda v, w=7, p=2: (f"{v:>{w}.{p}f}" if isinstance(v, (int, float)) else f"{'-':>{w}}")  # noqa: E731
        print(f"  {r['strategy']:<42}{f(r['sharpe'],6)}{f(r['sortino'],8)}{f(r['calmar'],8)}"
              f"{f(r['psr'],7)}{f(r['deflated_sharpe'],7)}{f(r['max_drawdown'],9,1)}{r['n']:>6}"
              f"{r['n_gates_passed']:>4}/{len(names)}")

    p = REPO / args.output
    p.write_text(json.dumps({"criteria": {k: thr[k] for k in names},
                             "n_promoted": len(out),
                             "clearing": {k: sum(1 for r in out if r["gates"][k]) for k in names},
                             "all_gates": sum(1 for r in out if r["all_gates"]),
                             "cells": out}, indent=2, default=str), encoding="utf-8")
    print(f"\n[OK] wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
