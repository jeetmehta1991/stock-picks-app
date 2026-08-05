"""scripts/measure_roster_breadth.py (B1461, ticket S6-B1455c) -- how many INDEPENDENT bets are
in the Phase 1B roster?

THE GAP THIS CLOSES
De-duplication used Jaccard >= 0.70 on (ticker, entry_date) -- SIGNAL overlap. Two cells can share
almost no entry dates and still be highly correlated in P&L: same factor exposure, same sector tilt,
same market beta. Jaccard cannot see that. So "13 cells survived de-dup" does NOT mean 13
independent bets, and 4 of the 13 are `institutional_*` variants of one another.

WHAT IS MEASURED
For each roster cell, a daily P&L series over the holdout, attributing each trade's pnl to its
ENTRY date. Then:
  * the Pearson correlation matrix across cells
  * mean pairwise correlation rho_bar
  * effective breadth N_eff = N / (1 + (N-1)*rho_bar)   -- the standard equal-correlation result;
    with rho_bar=0 it returns N, with rho_bar=1 it returns 1
  * clusters at rho >= 0.5 (single-linkage), which is where diversification benefit degrades sharply

HONEST LIMITATIONS -- read before quoting
1. Entry-date attribution, not daily mark-to-market. A trade's P&L lands entirely on its entry day
   rather than spread over the holding period, so co-movement from OVERLAPPING HOLDS is understated.
   The true correlation is therefore >= what this reports: N_eff here is an UPPER bound on breadth.
2. Days with no trades are zeros, not missing. For sparse cells this pulls correlations toward zero,
   which again biases N_eff UPWARD. Both biases run the same way: this is optimistic.
3. One holdout year. Correlation estimates at n~250 daily observations are noisy.

So the number produced here is the FRIENDLIEST reading of the roster's breadth. If it is already
well below the cell count, the real figure is worse.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

HO_START, HO_END = date(2025, 5, 5), date(2026, 5, 5)
WINSORIZE, COST_BPS = 300.0, 20.0
CLUSTER_RHO = 0.50


def main() -> int:
    rj = json.loads((REPO / "output_audit" / "b1453_phase_1b_roster.json")
                    .read_text(encoding="utf-8"))
    cells = [(r["strategy"], r["direction"], r["exit"]) for r in rj["roster"]]

    df = pd.read_csv(REPO / "output_r5_merged_1_7" / "trade_exit_detail.csv",
                     usecols=["strategy", "direction", "exit_method", "entry_date",
                              "pnl_pct", "hold_days"], low_memory=False,
                     dtype={"strategy": "category", "direction": "category",
                            "exit_method": "category",
                            "pnl_pct": "float32", "hold_days": "float32"})
    df["entry_date"] = pd.to_datetime(df["entry_date"])
    df = df[(df.entry_date >= pd.Timestamp(HO_START)) & (df.entry_date < pd.Timestamp(HO_END))]
    df["pnl_pct"] = df["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0

    series = {}
    for s, d, e in cells:
        g = df[(df.strategy == s) & (df.direction == d) & (df.exit_method == e)]
        if g.empty:
            continue
        series[s] = g.groupby("entry_date")["pnl_pct"].sum()
    panel = pd.DataFrame(series).fillna(0.0).sort_index()

    print("=" * 96)
    print("ROSTER BREADTH (B1461 / S6-B1455c) -- optimistic by construction, see docstring")
    print("=" * 96)
    print(f"  cells with holdout trades: {panel.shape[1]} | trading days: {panel.shape[0]}\n")

    C = panel.corr()
    n = C.shape[0]
    iu = np.triu_indices(n, k=1)
    rho = C.values[iu]
    rho_bar = float(np.nanmean(rho))
    n_eff = n / (1.0 + (n - 1) * rho_bar) if rho_bar > -1 / (n - 1) else float(n)

    print(f"  mean pairwise correlation  rho_bar = {rho_bar:.3f}")
    print(f"  max pairwise correlation           = {np.nanmax(rho):.3f}")
    print(f"  pairs with rho >= {CLUSTER_RHO}            = {(rho >= CLUSTER_RHO).sum()} of {len(rho)}")
    print(f"  EFFECTIVE BREADTH N_eff            = {n_eff:.1f}  (nominal {n})")
    print(f"  -> the roster behaves like ~{n_eff:.0f} independent bets, not {n}\n")

    # single-linkage clusters at CLUSTER_RHO
    parent = {c: c for c in C.columns}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            if C.values[i, j] >= CLUSTER_RHO:
                a, b = find(C.columns[i]), find(C.columns[j])
                if a != b:
                    parent[a] = b
    groups = {}
    for c in C.columns:
        groups.setdefault(find(c), []).append(c)
    clusters = sorted(groups.values(), key=len, reverse=True)
    print(f"  CLUSTERS at rho >= {CLUSTER_RHO}: {len(clusters)} (each is ~one bet)")
    for cl in clusters:
        tag = "  <-- MERGED" if len(cl) > 1 else ""
        print(f"    [{len(cl)}] {', '.join(sorted(cl))}{tag}")

    print(f"\n  top correlated pairs:")
    pairs = sorted(((C.values[i, j], C.columns[i], C.columns[j])
                    for i in range(n) for j in range(i + 1, n)), reverse=True)
    for r, a, b in pairs[:8]:
        print(f"    {r:>6.3f}  {a}  x  {b}")

    out = REPO / "output_audit" / "b1461_roster_breadth.json"
    out.write_text(json.dumps({
        "OPTIMISTIC_UPPER_BOUND": True,
        "n_cells": int(n), "rho_bar": rho_bar, "n_effective": n_eff,
        "cluster_rho": CLUSTER_RHO,
        "clusters": [sorted(c) for c in clusters],
        "correlation": C.round(3).to_dict()}, indent=2), encoding="utf-8")
    print(f"\n[OK] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
