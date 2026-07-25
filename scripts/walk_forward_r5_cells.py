"""R5 (strategy x exit) CELL-level walk-forward for the 1A-alpha gate.

Source attribution (per CHECKLIST #77):
  - Cube: output_r5_merged_1_7/trade_exit_detail.csv (the merged 7-batch R5 cube)
  - Shortlist: output_optimization_candidates_2026_07_25/exit_method_analysis.json
    layer_2_per_strategy_exit_cell (the DEC-426 5-Gate qualifying cells)
  - Method: DEC-505 4-fold expanding-window, disjoint 1y OOS -- the SAME folds +
    per-cell Sharpe as scripts/walk_forward_batch414_cells.py (which is hardcoded
    to the R4 output_batch395_final cube + 9 R4-era winners). This is the R5
    generalization: read the current cube + the current 5-Gate shortlist, not
    round-specific hardcodes.
  - Owner gate (CLAUDE.md): >=1 (strategy x exit) cell with rules-only OOS
    Sharpe >= 0.7 in >=1 fold (proxy for >=1 regime) AND OOS n >= 30 for the
    $300 Phase 1B-alpha agent overlay budget to be eligible. Prints GATE OPEN /
    GATE LOCKED.

Usage:
  python scripts/walk_forward_r5_cells.py
  python scripts/walk_forward_r5_cells.py --cube-dir output_r5_merged_1_7 \
      --analysis output_optimization_candidates_2026_07_25/exit_method_analysis.json
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


def _sharpe(pnl: pd.Series):
    n = len(pnl)
    if n < 5:
        return None
    a = pnl.values
    std = a.std(ddof=1) if n > 1 else 0.0
    sh = float(a.mean() / std) if std > 0 else 0.0
    return {"n": int(n), "sharpe": round(sh, 3), "wr": round(float((a > 0).mean()), 3)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube-dir", default="output_r5_merged_1_7")
    ap.add_argument("--analysis",
                    default="output_optimization_candidates_2026_07_25/exit_method_analysis.json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    cube = REPO / args.cube_dir / "trade_exit_detail.csv"
    out = Path(args.out) if args.out else (REPO / args.cube_dir / "walk_forward_r5_cells.json")

    # shortlist = every L2 qualifying (strategy x exit) cell from the optimizer
    an = json.loads((REPO / args.analysis).read_text(encoding="utf-8"))
    l2 = an.get("layer_2_per_strategy_exit_cell", [])
    cells = [(c.get("strategy"), c.get("exit_method")) for c in l2
             if c.get("strategy") and c.get("exit_method")]
    print(f"[INFO] {len(cells)} shortlist cells from {args.analysis}")

    print(f"[INFO] reading {cube} (usecols only) ...")
    df = pd.read_csv(cube, usecols=["strategy", "entry_date", "exit_method", "pnl_pct"],
                     low_memory=False)
    df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    print(f"[INFO] cube rows={len(df):,}")

    results, gate_open_cells = [], []
    for strat, exit_m in cells:
        sub = df[(df["strategy"] == strat) & (df["exit_method"] == exit_m)]
        folds = {}
        best_oos = None
        for name, o0, o1 in FOLDS:
            m = sub[(sub["entry_date"] >= o0) & (sub["entry_date"] < o1)]
            st = _sharpe(m["pnl_pct"])
            folds[name] = st
            if st and st["n"] >= OOS_MIN_N:
                if best_oos is None or st["sharpe"] > best_oos:
                    best_oos = st["sharpe"]
        passes = best_oos is not None and best_oos >= GATE_SHARPE
        row = {"strategy": strat, "exit_method": exit_m, "best_oos_sharpe_n>=30": best_oos,
               "gate_pass": passes, "folds": folds}
        results.append(row)
        if passes:
            gate_open_cells.append(row)

    results.sort(key=lambda r: (r["best_oos_sharpe_n>=30"] is None, -(r["best_oos_sharpe_n>=30"] or -9)))
    out.write_text(json.dumps({"gate_threshold": GATE_SHARPE, "oos_min_n": OOS_MIN_N,
                               "n_cells": len(results), "n_gate_pass": len(gate_open_cells),
                               "cells": results}, indent=1), encoding="utf-8")
    print(f"[OK] wrote {out}")

    print("\n=== top cells by best OOS Sharpe (n>=30 folds) ===")
    for r in results[:12]:
        b = r["best_oos_sharpe_n>=30"]
        print(f"  {r['strategy']} x {r['exit_method']}: best_OOS_Sharpe={b} "
              f"{'<= PASS' if r['gate_pass'] else ''}")

    print("\n" + "=" * 56)
    if gate_open_cells:
        print(f"1A-ALPHA GATE: OPEN -- {len(gate_open_cells)} cell(s) with OOS Sharpe "
              f">= {GATE_SHARPE} at n>=30 in >=1 fold.")
        print("  -> $300 Phase 1B-alpha agent overlay is ELIGIBLE (owner decision).")
    else:
        print(f"1A-ALPHA GATE: LOCKED -- no cell reached OOS Sharpe >= {GATE_SHARPE} "
              f"at n>=30 in any fold.")
        print("  -> loop back to entry-side optimization (Lens A/B) + re-cube; "
              "do NOT commit the 1B-alpha budget.")
    print("=" * 56)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
