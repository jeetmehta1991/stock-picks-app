"""R5 (strategy x exit) CELL-level walk-forward for the 1A-alpha gate.

Source attribution (per CHECKLIST #77):
  - Cube: output_r5_merged_1_7/trade_exit_detail.csv (the merged 7-batch R5 cube)
  - Cell set: either the DEC-426 5-Gate shortlist
    (output_optimization_candidates_2026_07_25/exit_method_analysis.json
    layer_2_per_strategy_exit_cell) OR --all-cells = every (strategy x exit)
    cell with in-sample n >= --min-n from exit_strategy_comparison.csv.
  - Method: DEC-505 4-fold expanding-window, disjoint 1y OOS -- the SAME folds +
    per-cell Sharpe as scripts/walk_forward_batch414_cells.py (which is hardcoded
    to the R4 cube + 9 R4-era winners). This is the R5 generalization: read the
    current cube + a configurable cell set, evaluated by groupby in one pass.
  - Owner gate (CLAUDE.md): >=1 (strategy x exit) cell with rules-only OOS
    Sharpe >= 0.7 at OOS n >= 30 in >=1 fold for the $300 Phase 1B-alpha budget.

Multiple-testing note: scanning all ~4.7k n>=30 cells x 4 folds inflates the
best-of-folds false-positive rate. So this reports BOTH the loose count (>=0.7
in >=1 fold) AND the robust count (>=0.7 in >=2 folds) -- the robust count is
the multiple-testing-aware read. It does NOT weaken any threshold.

Usage:
  python scripts/walk_forward_r5_cells.py                 # 5-Gate shortlist
  python scripts/walk_forward_r5_cells.py --all-cells     # every n>=30 cell
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent

# DEC-505 4-fold expanding-window, disjoint 1y OOS (identical to
# walk_forward_batch414_cells.py). Warmup 1y 2021-05-05 -> 2022-05-05.
FOLDS = [
    ("fold_1", date(2022, 5, 5), date(2023, 5, 5)),
    ("fold_2", date(2023, 5, 5), date(2024, 5, 5)),
    ("fold_3", date(2024, 5, 5), date(2025, 5, 5)),
    ("fold_4", date(2025, 5, 5), date(2026, 5, 5)),
]
OOS_MIN_N = 30          # per-fold statistical-power floor (criterion 9 per-regime)
GATE_SHARPE = 0.7       # 1A-alpha OOS Sharpe threshold


def _sharpe(a, hold):
    """ANNUALIZED per-trade Sharpe, IDENTICAL to backtest/results/metrics.py::_sharpe
    (B1371 fix): per_trade_sharpe * sqrt(252/avg_hold). The gate threshold 0.7 was
    calibrated against this annualized number; the prior version returned raw
    per-trade mean/std, which is ~sqrt(trades/yr) too small and made the 0.7 bar
    effectively require an annualized Sharpe of ~5 (owner-surfaced, only 10/4758
    passed)."""
    n = len(a)
    if n < OOS_MIN_N:
        return None
    std = a.std(ddof=1) if n > 1 else 0.0
    if std <= 0:
        return {"n": int(n), "sharpe": 0.0, "wr": round(float((a > 0).mean()), 3)}
    avg_hold = float(hold.mean()) if len(hold) > 0 else 10.0
    trades_per_year = max(1.0, 252.0 / max(avg_hold, 1e-9))
    sh = float(a.mean() / std) * (trades_per_year ** 0.5)
    return {"n": int(n), "sharpe": round(sh, 3), "wr": round(float((a > 0).mean()), 3),
            "avg_hold": round(avg_hold, 1)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube-dir", default="output_r5_merged_1_7")
    ap.add_argument("--analysis",
                    default="output_optimization_candidates_2026_07_25/exit_method_analysis.json")
    ap.add_argument("--all-cells", action="store_true",
                    help="evaluate every (strategy x exit) cell with in-sample n>=--min-n "
                         "from exit_strategy_comparison.csv (not just the 5-Gate shortlist)")
    ap.add_argument("--min-n", type=int, default=30, help="in-sample n floor for --all-cells")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    cdir = REPO / args.cube_dir
    cube = cdir / "trade_exit_detail.csv"
    out = Path(args.out) if args.out else (cdir / (
        "walk_forward_r5_all_cells.json" if args.all_cells else "walk_forward_r5_cells.json"))

    if args.all_cells:
        cmp = pd.read_csv(cdir / "exit_strategy_comparison.csv")
        ncol = "trades" if "trades" in cmp.columns else "n"
        cellset = set(map(tuple, cmp[cmp[ncol] >= args.min_n][["strategy", "exit_method"]].values))
        print(f"[INFO] --all-cells: {len(cellset)} cells with in-sample {ncol}>={args.min_n}")
    else:
        an = json.loads((REPO / args.analysis).read_text(encoding="utf-8"))
        l2 = an.get("layer_2_per_strategy_exit_cell", [])
        cellset = set((c.get("strategy"), c.get("exit_method")) for c in l2
                      if c.get("strategy") and c.get("exit_method"))
        print(f"[INFO] 5-Gate shortlist: {len(cellset)} cells")

    print(f"[INFO] reading {cube} (usecols) ...")
    df = pd.read_csv(cube, usecols=["strategy", "entry_date", "exit_method", "pnl_pct", "hold_days"],
                     low_memory=False)
    df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    print(f"[INFO] cube rows={len(df):,}; grouping by (strategy, exit_method) ...")

    results = []
    for (strat, exit_m), g in df.groupby(["strategy", "exit_method"], sort=False):
        if (strat, exit_m) not in cellset:
            continue
        ed = g["entry_date"].values
        pn = g["pnl_pct"].values
        hd = g["hold_days"].values
        folds, qualifying = {}, []
        for name, o0, o1 in FOLDS:
            mask = (ed >= o0) & (ed < o1)
            st = _sharpe(pn[mask], hd[mask])
            folds[name] = st
            if st:
                qualifying.append(st["sharpe"])
        n_ge_07 = sum(1 for s in qualifying if s >= GATE_SHARPE)
        best = max(qualifying) if qualifying else None
        results.append({"strategy": strat, "exit_method": exit_m,
                        "best_oos_sharpe": best, "n_folds_ge_0.7": n_ge_07,
                        "n_qualifying_folds": len(qualifying), "folds": folds})

    pass1 = [r for r in results if r["n_folds_ge_0.7"] >= 1]
    pass2 = [r for r in results if r["n_folds_ge_0.7"] >= 2]
    results.sort(key=lambda r: (r["best_oos_sharpe"] is None, -(r["best_oos_sharpe"] or -9)))
    out.write_text(json.dumps({"gate_threshold": GATE_SHARPE, "oos_min_n": OOS_MIN_N,
                               "mode": "all_cells" if args.all_cells else "shortlist",
                               "n_cells_evaluated": len(results),
                               "n_pass_1fold": len(pass1), "n_pass_2fold": len(pass2),
                               "cells": results}, indent=1), encoding="utf-8")
    print(f"[OK] wrote {out}")

    print("\n=== top cells by best OOS Sharpe (n>=30 folds) ===")
    for r in results[:15]:
        print(f"  {r['strategy'][:30]:30} x {r['exit_method'][:18]:18} "
              f"best={r['best_oos_sharpe']} folds>=0.7={r['n_folds_ge_0.7']}/{r['n_qualifying_folds']}")

    print("\n" + "=" * 60)
    print(f"CELLS EVALUATED: {len(results)}")
    print(f"PASS loose  (>=0.7 in >=1 fold): {len(pass1)}   <- headline count")
    print(f"PASS ROBUST (>=0.7 in >=2 folds): {len(pass2)}   <- multiple-testing-aware")
    print("=" * 60)
    if pass2:
        print(f"1A-ALPHA GATE: OPEN (robust) -- {len(pass2)} cell(s) clear >=0.7 in >=2 folds.")
    elif pass1:
        print(f"1A-ALPHA GATE: OPEN (loose only) -- {len(pass1)} cell(s) at >=1 fold, "
              f"but 0 clear >=2 folds. Treat as marginal.")
    else:
        print("1A-ALPHA GATE: LOCKED.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
