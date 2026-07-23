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


def build_merged_input() -> int:
    MERGED.mkdir(exist_ok=True)
    frames = [pd.read_parquet(f)
              for f in sorted(glob.glob(str(REPO / "output_batches" / "batch_*" / "trade_log.parquet")))]
    if not frames:
        print("no committed batches yet")
        return 0
    tl = pd.concat(frames, ignore_index=True)
    tl.to_csv(MERGED / "trade_log.csv", index=False)
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
