"""scripts/build_r5_cube_dashboard.py (B1347, Council 371) -- R5 cube explorer
on the ESTABLISHED dashboard_phase_1a_beta template (owner directive
2026-07-23: match the template used for previous batches; do not reinvent).

Pools the committed R5 batches (output_batches/batch_*/trade_log.parquet) into
the input the established generator consumes, runs
scripts/build_phase_1a_beta_dashboard.py against it, reuses that dashboard's
index.html, and stores this R5 cube as the R6 delta BASELINE (owner: "new R5
baseline; per-cell delta starts at R6"). Regenerate after each batch merges.

Output: dashboard_r5_cube/{data.json,index.html} + output_audit/r5_baseline/
r5_cell_baseline.json (per-(strategy x exit x regime) baseline for r5_delta_analyzer).
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
MERGED = REPO / "output_r5_cube_merged"
CUBE_DIR = REPO / "dashboard_r5_cube"
TEMPLATE_UI = REPO / "dashboard_phase_1a_beta" / "index.html"
FROZEN_SHA = "e846b6d2cfb3"


IS_END = pd.Timestamp("2024-06-30")
OOS_START = pd.Timestamp("2024-07-01")
R5_IS_WINDOW = "2022-05-05..2024-06-30"
R5_OOS_WINDOW = "2024-07-01..2026-05-05"


def _wide_is_oos(tl: pd.DataFrame):
    """B1348 FIX: the established generator's AUTO-gen writes LONG-format
    per_cell (is_in_sample bool) but its survivor/underperformer logic reads
    WIDE columns (is_n/oos_n/is_sum_pp/oos_wr_pct/...). Pre-write the WIDE
    files so those tabs populate instead of coming back empty."""
    tl = tl.copy()
    tl["entry_dt"] = pd.to_datetime(tl["entry_date"], errors="coerce")
    tl["seg"] = tl["entry_dt"].apply(lambda d: "is" if d <= IS_END else "oos")

    def agg(g):
        out = {}
        for seg in ("is", "oos"):
            s = g[g.seg == seg]
            out[f"{seg}_n"] = len(s)
            out[f"{seg}_sum_pp"] = round(float(s.pnl_pct.sum()), 1) if len(s) else 0.0
            out[f"{seg}_wr_pct"] = round(100 * s.win.astype(bool).mean(), 1) if len(s) else 0.0
            out[f"{seg}_mean_pct"] = round(float(s.pnl_pct.mean()), 2) if len(s) else 0.0
        return pd.Series(out)

    exit_col = "exit_reason" if "exit_reason" in tl.columns else "strategy"
    per_cell = tl.groupby(["strategy", exit_col]).apply(agg).reset_index()
    per_cell.to_csv(MERGED / "per_cell_is_oos.csv", index=False)
    per_strat = tl.groupby("strategy").apply(agg).reset_index()
    per_strat.to_csv(MERGED / "per_strategy_is_oos.csv", index=False)


def build_merged_input() -> int:
    MERGED.mkdir(exist_ok=True)
    frames = [pd.read_parquet(f)
              for f in sorted(glob.glob(str(REPO / "output_batches" / "batch_*" / "trade_log.parquet")))]
    if not frames:
        print("no committed batches yet")
        return 0
    tl = pd.concat(frames, ignore_index=True)
    tl.to_csv(MERGED / "trade_log.csv", index=False)
    _wide_is_oos(tl)  # WIDE per_cell + per_strategy so survivors/underperformers populate
    # loaded-but-unused by the established generator -> header-only stubs
    pd.DataFrame(columns=["strategy", "metric"]).to_csv(MERGED / "backtest_results.csv", index=False)
    pd.DataFrame(columns=["strategy", "verdict"]).to_csv(MERGED / "walk_forward_validation.csv", index=False)
    print(f"merged {len(frames)} batches -> {len(tl)} trades, "
          f"{tl.strategy.nunique()} strategies, {tl.ticker.nunique()} tickers")
    return len(tl)


def main() -> int:
    n = build_merged_input()
    if not n:
        return 1
    # reuse the ESTABLISHED generator verbatim (template parity)
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "build_phase_1a_beta_dashboard.py"),
         "--input-dir", str(MERGED), "--output-dir", str(CUBE_DIR)],
        cwd=str(REPO))
    if r.returncode != 0:
        print("established generator failed")
        return r.returncode
    shutil.copy(TEMPLATE_UI, CUBE_DIR / "index.html")  # same UI as previous batches

    # tag as R5 baseline + persist per-cell baseline for R6 delta
    d = json.loads((CUBE_DIR / "data.json").read_text(encoding="utf-8"))
    d["r_iteration"] = "R5"
    d["is_baseline"] = True
    d["delta_baseline"] = ("R5 (this run) -- per-(strategy x exit x regime) delta "
                           "populates at R6 re-run (owner 2026-07-23)")
    # B1348: correct the window labels (generator hardcodes R4's 2022-01..2024-06)
    d["is_window"] = R5_IS_WINDOW
    d["oos_window"] = R5_OOS_WINDOW
    d["walk_forward_note"] = "N/A -- R5 ran --no-walk-forward (cube-isolation run)"
    (CUBE_DIR / "data.json").write_text(json.dumps(d, default=str, indent=1), encoding="utf-8")

    base_dir = REPO / "output_audit" / "r5_baseline"
    base_dir.mkdir(parents=True, exist_ok=True)
    cells = d["slices"].get("strategy_x_exit_x_regime", [])
    (base_dir / "r5_cell_baseline.json").write_text(json.dumps(
        {"r_iteration": "R5", "frozen_sha": FROZEN_SHA, "cells": cells,
         "note": "R5 baseline cube for R6 per-cell delta (r5_delta_analyzer)"},
        default=str, indent=1), encoding="utf-8")
    print(f"R5 cube dashboard on established template; {len(cells)} cells stored as R6 baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main())
