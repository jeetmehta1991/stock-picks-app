"""scripts/best_exit_by_gates.py (B1451, CORRECTED B1452) -- select each cell's exit by
GATES CLEARED **ON IN-SAMPLE**, then grade the chosen exit on the untouched holdout.

OWNER DIRECTIVE (2026-08-04)
"It should be the exit that clears most gates. You need to change argmax criteria to the exit
that clears most gates 5 of them as of now and re-evaluate results from r5 run."

THE FIRST VERSION OF THIS SCRIPT WAS WRONG AND ITS RESULT (35 passing) IS RETRACTED.
It filtered to the holdout FIRST and then chose, per cell, whichever of the 26 exits cleared
the most gates *there* - selecting on the test set and then reporting a pass on the test set.
That is circular: with 26 candidates per cell, a maximum-over-26 on the graded window will
almost always find something that passes, so the 35 measured nothing but selection freedom.

CORRECT DESIGN (matches build_passed_strategy_exit_list.py, which was right all along):
  SELECT  on IS folds F1-F3 pooled (2022-05-05 -> 2025-05-05) - the holdout is never read
  GRADE   the single chosen exit on F4 (2025-05-05 -> 2026-05-05)
One test per cell, no search on the graded window.

WHAT CHANGES vs THE CANONICAL GENERATOR
The generator selects by argmax IS-pooled SHARPE. This selects by argmax IS GATES-CLEARED
(tie-break IS Sharpe), which is the owner's directive: Sharpe is one of five live gates, so
maximising Sharpe alone can pick an exit that fails profit_factor, sortino, psr or min_trades
when another exit would have cleared all five. Both are IS-only, so both are honest; they
differ only in the objective.

LIVE GATES ONLY: max_drawdown / calmar / deflated_sharpe / win_rate are diagnostics after
B1436/B1437, so including them would add a constant +3 to every candidate and blind the argmax.
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

# S6-B1452a (B1463): fold boundaries, conditioning, gates and the selection objective are
# imported from roster_core so this file and build_phase_1b_roster.py cannot drift apart.
# The objective difference that justified two scripts is now roster_core.select_exit's
# `objective=` switch ("gates" here, the owner's 2026-08-04 directive).
from roster_core import (                                    # noqa: E402
    IS_START, IS_END, HO_START, HO_END, WINSORIZE, COST_BPS, MIN_N, LIVE_GATES,
    evaluate as _core_evaluate, rank_key,
)



evaluate = _core_evaluate   # S6-B1452a: one implementation


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube", default="output_r5_merged_1_7")
    ap.add_argument("--output", default="output_audit/b1452_best_exit_by_gates_is_selected.json")
    args = ap.parse_args()

    print(f"[INFO] SELECT on IS {IS_START}..{IS_END} by argmax GATES-CLEARED (tie-break IS Sharpe)")
    print(f"[INFO] GRADE  the chosen exit on HOLDOUT {HO_START}..{HO_END} - never selected on")
    print(f"[INFO] live gates ({len(LIVE_GATES)}): {', '.join(LIVE_GATES)}")

    df = pd.read_csv(REPO / args.cube / "trade_exit_detail.csv",
                     usecols=["strategy", "direction", "exit_method", "entry_date",
                              "pnl_pct", "hold_days"], low_memory=False)
    df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    df["pnl_pct"] = df["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0

    rows = []
    # group by (strategy, DIRECTION, exit): a dual strategy's legs have independent edges;
    # pooling them drags a passing leg below the bar with its failing twin (B1451 fix).
    for (strat, direction), g in df.groupby(["strategy", "direction"]):
        is_g = g[(g.entry_date >= IS_START) & (g.entry_date < IS_END)]
        ho_g = g[(g.entry_date >= HO_START) & (g.entry_date < HO_END)]
        cands = []
        for ex, ge in is_g.groupby("exit_method"):
            r = evaluate(ge["pnl_pct"], ge["hold_days"])
            if r:
                r["exit"] = ex
                cands.append(r)
        if not cands:
            continue
        # selection-justified: gates-cleared IS the promotion criterion (owner directive), so
        # maximising it is the objective itself; IS Sharpe breaks ties because among equally
        # compliant exits the better risk-adjusted one is preferable. IS ONLY - CHECKLIST #165.
        # B1975: rank_key, not `or -9` - 0.0 is a VALUE, and only an ABSENT
        # Sharpe may take the sentinel. Shared definition in roster_core.
        pick = max(cands, key=lambda c: (c["n_gates"], rank_key(c["sharpe"])))
        by_sharpe = max(cands, key=lambda c: (rank_key(c["sharpe"]),))   # what the generator picks

        he = ho_g[ho_g.exit_method == pick["exit"]]
        graded = evaluate(he["pnl_pct"], he["hold_days"])
        rows.append({
            "strategy": strat, "direction": direction, "exit": pick["exit"],
            "is_n_gates": pick["n_gates"], "is_sharpe": pick["sharpe"], "is_n": pick["n"],
            "generator_would_pick": by_sharpe["exit"],
            "objective_disagrees": pick["exit"] != by_sharpe["exit"],
            "holdout": graded,
            "holdout_all_gates": bool(graded and graded["all_live_gates"]),
            "holdout_n_gates": graded["n_gates"] if graded else None,
            "holdout_uneval": graded is None,
        })

    passing = [r for r in rows if r["holdout_all_gates"]]
    uneval = [r for r in rows if r["holdout_uneval"]]
    disagree = [r for r in rows if r["objective_disagrees"]]

    print(f"\n[RESULT] {len(rows)} (strategy x direction) cells with a selectable IS exit")
    print(f"         {len(disagree)} where gates-argmax picks a DIFFERENT exit than Sharpe-argmax")
    print(f"         {len(uneval)} UNEVAL on the holdout (n<{MIN_N} at the chosen exit)")
    print(f"         **{len(passing)} clear all {len(LIVE_GATES)} live gates ON THE HOLDOUT**")
    print(f"         (contrast: the RETRACTED holdout-selected version reported 35 - inflated by "
          f"choosing among 26 exits on the graded window itself)\n")

    print(f"  {'strategy':<42}{'dir':<7}{'exit':<22}{'IS shrp':>8}{'HO shrp':>8}{'HO n':>6}")
    for r in sorted(passing, key=lambda x: -rank_key(x["holdout"]["sharpe"])):
        print(f"  {r['strategy']:<42}{r['direction']:<7}{r['exit']:<22}"
              f"{(r['is_sharpe'] or 0):>8.2f}{(r['holdout']['sharpe'] or 0):>8.2f}{r['holdout']['n']:>6}")

    out = REPO / args.output
    out.write_text(json.dumps({
        "cube": args.cube, "live_gates": list(LIVE_GATES),
        "selection_window": [str(IS_START), str(IS_END)],
        "grading_window": [str(HO_START), str(HO_END)],
        "method": "argmax IS gates-cleared, tie-break IS Sharpe; graded once on the holdout",
        "n_cells": len(rows), "n_passing_holdout": len(passing),
        "n_uneval": len(uneval), "n_objective_disagree": len(disagree),
        "rows": rows}, indent=2, default=str), encoding="utf-8")
    print(f"\n[OK] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
