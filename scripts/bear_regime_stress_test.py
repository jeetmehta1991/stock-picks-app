"""scripts/bear_regime_stress_test.py (B1455) -- grade the roster's shorts on REAL bear data.

OWNER DIRECTIVE (2026-08-04): "Run bear inclusive window but retain mirror shorts irrespective."

WHY A NEW WINDOW COULD NOT BE RUN
The literal request -- re-run the cube over a window that includes a bear market -- is
BLOCKED BY DATA, not by effort:
  * the OHLCV cache begins 2021-05-06 (EXECUTED: min date across a 12-ticker sample)
  * so the only pre-window year obtainable without a fresh prefetch is 2021, which was bull
  * real bear regimes outside the locked window (2020 COVID, 2018Q4, 2008) would each need a
    paid prefetch AND an owner unlock of the 2022-05-05 -> 2026-05-05 window lock
Neither is authorised, so a new run cannot answer the question.

WHY THE EXISTING CUBE CAN ANSWER IT ANYWAY
The locked window already CONTAINS the 2022 bear market. The problem was never missing bear
data -- it was which fold the bear data landed in:
  bear-SHORT trades in the current holdout (2025-05->2026-05):  33,644  -> cells with n>=100:     0
  bear-SHORT trades in the bear year      (2022-05->2023-05): 567,814  -> cells with n>=100: 1,560
The current holdout is 88% bull; its 33k bear-short trades spread across 93 strategies x 26
exits leave EVERY cell under the n>=100 floor. That -- not weak short edge -- is why B1385's
regime-conditional gate returned 0 PASS / 77 UNEVAL. It measured nothing.

So this script REPARTITIONS the existing cube rather than re-running it:
  SELECT on 2023-05-05 -> 2026-05-05   (the post-bear period; bull-dominant)
  GRADE  on 2022-05-05 -> 2023-05-05   BEAR-REGIME ENTRIES ONLY (567,814 short trades)

HONEST LIMITATION -- READ BEFORE QUOTING ANY NUMBER FROM THIS SCRIPT
This is TEMPORALLY BACKWARDS: it selects on later data and grades on earlier data. It is
therefore NOT a walk-forward test and its output is NOT an out-of-sample promotion verdict.
It is a REGIME STRESS TEST: "conditional on the exit we would choose from post-bear data,
how would this cell have behaved in the bear market we actually have?"
Use it to size bear risk, never to promote. Promotion verdicts come from PHASE_1B_ROSTER.md,
which uses the correct IS-select / holdout-grade discipline.

Per the owner directive the SHORT mirrors are retained regardless of what this reports --
the purpose is to know the exposure, not to re-litigate the roster.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backtest.config import PASSING_CRITERIA as PC          # noqa: E402
from backtest.results.metrics import _sortino_ratio, _deflated_sharpe  # noqa: E402
from walk_forward_r5_cells import _sharpe                    # noqa: E402

SEL_START, SEL_END = date(2023, 5, 5), date(2026, 5, 5)     # exit chosen here
BEAR_START, BEAR_END = date(2022, 5, 5), date(2023, 5, 5)   # graded here, bear entries only
WINSORIZE, COST_BPS = 300.0, 20.0
MIN_N = 30

LIVE_GATES = ("sharpe_per_regime", "profit_factor", "sortino", "psr", "min_trades")


def evaluate(pnl: pd.Series, hold: pd.Series) -> dict | None:
    """The five live gates on one (cell, window). None under the power floor."""
    n = len(pnl)
    if n < MIN_N:
        return None
    sh = _sharpe(pnl.values, hold)
    sharpe = sh["sharpe"] if sh else None
    sortino = _sortino_ratio(pnl, hold)
    dsr = _deflated_sharpe(sharpe or 0.0, n, float(pnl.skew()), float(pnl.kurtosis()))
    wins, loss = pnl[pnl > 0], pnl[pnl <= 0]
    pf = float(wins.sum() / abs(loss.sum())) if len(loss) and loss.sum() != 0 else float("inf")
    gates = {
        "sharpe_per_regime": sharpe is not None and sharpe >= PC["min_sharpe_per_regime"],
        "profit_factor":     pf >= PC["min_profit_factor_overall"],
        "sortino":           sortino is not None and sortino >= PC["min_sortino_per_regime"],
        "psr":               dsr.get("psr") is not None and dsr["psr"] >= PC["min_psr"],
        "min_trades":        n >= PC["min_trades"],
    }
    return {"n": n, "sharpe": sharpe, "sortino": sortino, "psr": dsr.get("psr"),
            "profit_factor": round(pf, 3), "expectancy": round(float(pnl.mean()), 4),
            "win_rate": round(float((pnl > 0).mean()), 3),
            "gates": gates, "n_gates": sum(1 for v in gates.values() if v),
            "all_live_gates": all(gates.values())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube", default="output_r5_merged_1_7")
    ap.add_argument("--output", default="output_audit/b1455_bear_regime_stress_test.json")
    args = ap.parse_args()

    print("=" * 100)
    print("BEAR-REGIME STRESS TEST (B1455) -- NOT a walk-forward test, NOT a promotion verdict")
    print("=" * 100)
    print(f"  SELECT exit on {SEL_START}..{SEL_END} (post-bear, bull-dominant)")
    print(f"  GRADE       on {BEAR_START}..{BEAR_END}, BEAR-regime entries only")
    print("  Temporally backwards by construction -- see module docstring before quoting.\n")

    df = pd.read_csv(REPO / args.cube / "trade_exit_detail.csv",
                     usecols=["strategy", "direction", "exit_method", "entry_date",
                              "regime_at_entry", "pnl_pct", "hold_days"], low_memory=False)
    df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    df["pnl_pct"] = df["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0

    rows = []
    for (strat, direction), g in df.groupby(["strategy", "direction"]):
        sel = g[(g.entry_date >= SEL_START) & (g.entry_date < SEL_END)]
        bear = g[(g.entry_date >= BEAR_START) & (g.entry_date < BEAR_END)
                 & (g.regime_at_entry == "bear")]
        cands = []
        for ex, ge in sel.groupby("exit_method"):
            r = evaluate(ge["pnl_pct"], ge["hold_days"])
            if r:
                r["exit"] = ex
                cands.append(r)
        if not cands:
            continue
        # selection-justified: gates-cleared is the promotion objective (owner directive
        # 2026-08-04), IS Sharpe breaks ties. Chosen on the SELECT fold only -- the bear
        # fold is never searched over. CHECKLIST #165.
        pick = max(cands, key=lambda c: (c["n_gates"], c["sharpe"] or -9))
        be = bear[bear.exit_method == pick["exit"]]
        graded = evaluate(be["pnl_pct"], be["hold_days"])
        rows.append({
            "strategy": strat, "direction": direction, "exit": pick["exit"],
            "select_n_gates": pick["n_gates"], "select_sharpe": pick["sharpe"],
            "bear": graded,
            "bear_all_gates": bool(graded and graded["all_live_gates"]),
            "bear_n_gates": graded["n_gates"] if graded else None,
            "bear_uneval": graded is None,
        })

    for d in ("short", "long"):
        sub = [r for r in rows if r["direction"] == d]
        ev = [r for r in sub if not r["bear_uneval"]]
        ps = [r for r in ev if r["bear_all_gates"]]
        print(f"  {d.upper():<6} {len(sub):>4} cells | {len(ev):>4} gradable in bear "
              f"| {len(ps):>4} clear all 5 live gates IN BEAR")
        if ev:
            pos = sum(1 for r in ev if (r["bear"]["expectancy"] or 0) > 0)
            print(f"         {pos}/{len(ev)} positive expectancy in bear "
                  f"({100*pos/len(ev):.0f}%)")

    shorts = sorted([r for r in rows if r["direction"] == "short" and not r["bear_uneval"]],
                    key=lambda x: -(x["bear"]["sharpe"] or -9))
    print(f"\n  TOP SHORTS IN BEAR (by bear Sharpe):")
    print(f"  {'strategy':<44}{'exit':<22}{'bearShrp':>9}{'bearPF':>8}{'n':>7}{'gates':>7}")
    for r in shorts[:15]:
        print(f"  {r['strategy']:<44}{r['exit']:<22}{(r['bear']['sharpe'] or 0):>9.2f}"
              f"{(r['bear']['profit_factor'] or 0):>8.2f}{r['bear']['n']:>7}"
              f"{r['bear_n_gates']:>5}/5")

    out = REPO / args.output
    out.write_text(json.dumps({
        "cube": args.cube,
        "IS_NOT_A_PROMOTION_VERDICT": True,
        "design": "temporally backwards regime stress test; select post-bear, grade in bear",
        "select_window": [str(SEL_START), str(SEL_END)],
        "bear_grading_window": [str(BEAR_START), str(BEAR_END)],
        "live_gates": list(LIVE_GATES),
        "n_cells": len(rows), "rows": rows}, indent=2, default=str), encoding="utf-8")
    print(f"\n[OK] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
