#!/usr/bin/env python
# Source: output_audit/*_grid*.json + output_r5_merged_1_7/{skipped_trades,
# trade_log}.csv; per CHECKLIST #77 every figure is derived at run time.
"""S6-B2938 / S6-B2995: the two load-bearing figures with no persisted
artifact, re-derived and written down; the population's four members named.

THE POPULATION (S6-B2995's ask - the sweep's four members, named):
  1. '27 of 54 soldiers cells below the holdout floor'  - closed by
     scripts/candle_grid_feasibility.py (B2937), artifact
     output_audit/output_r5_merged_1_7_three_white_soldiers_grid_feasibility.json
  2. '28 of 54 crows cells below the holdout floor'     - closed by the
     same script's crows artifact
  3. '82.1 pct of 17,927 cells across 110 grid artifacts died on sample
     size' - CLOSED HERE, re-derived from every tracked grid artifact
  4. 'occupancy blocks outnumber landed trades 2.07x (391,782 vs 189,471)'
     - CLOSED HERE, re-derived from the R5 cube's own files
So the original row's arithmetic reconciles as: population 4; members 1-2
counted as one PAIR in 'of which 3 had none'; the pair closed by B2937;
members 3-4 are 'these two remain', now persisted by this script.

    python scripts/b2938_figures.py
"""
from __future__ import annotations

import io
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if not (ROOT / "scripts" / "roster_core.py").exists():
    ROOT = Path.cwd()   # draft run from the scratchpad; repo is the cwd
assert (ROOT / "scripts" / "roster_core.py").exists(), ROOT
R5 = ROOT / "output_r5_merged_1_7"
OUT = ROOT / "output_audit" / "b2938_figures.json"

SAMPLE_SIZE_VERDICTS = {"BELOW_POWER_FLOOR", "NO_HOLDOUT_ROWS",
                        "NO_EXIT_SELECTABLE", "ZERO_FIRES", "NOT_GRADED"}


def grid_cells() -> dict:
    """Figure 3: every verdict-bearing row across every grid artifact."""
    files, total, starved = [], 0, 0
    for p in sorted((ROOT / "output_audit").glob("*grid*.json")):
        try:
            d = json.loads(io.open(p, encoding="utf-8").read())
        except Exception:
            continue
        rows = d.get("results")
        if not isinstance(rows, list) or not rows:
            continue
        n = len([r for r in rows if isinstance(r, dict)])
        s = len([r for r in rows if isinstance(r, dict)
                 and (r.get("verdict") in SAMPLE_SIZE_VERDICTS
                      or (r.get("admit") or {}).get("verdict")
                      in SAMPLE_SIZE_VERDICTS)])
        if n:
            files.append({"file": p.name, "rows": n, "sample_size_dead": s})
            total += n
            starved += s
    return {"grid_artifacts": len(files), "cells": total,
            "sample_size_dead": starved,
            "pct": round(100.0 * starved / total, 1) if total else None,
            "per_file": files}


def occupancy_ratio() -> dict:
    """Figure 4: occupancy skip rows vs landed trades, R5 cube."""
    import pandas as pd
    sk = pd.read_csv(R5 / "skipped_trades.csv", usecols=["reason"],
                     low_memory=False)
    occ = int(sk["reason"].astype(str)
              .str.contains("ticker_already_open", na=False).sum())
    tl = pd.read_csv(R5 / "trade_log.csv", usecols=["ticker"],
                     low_memory=False)
    landed = int(len(tl))
    return {"occupancy_skip_rows": occ, "landed_trades": landed,
            "ratio": round(occ / landed, 2) if landed else None}


def main() -> int:
    t0 = time.time()
    doc = {
        "ticket": "S6-B2938 (+ S6-B2995: members named)",
        "members": {
            "1_soldiers_below_floor": "closed by candle_grid_feasibility.py "
                                      "(B2937)",
            "2_crows_below_floor": "closed by the same script",
            "3_grid_cells_sample_size": grid_cells(),
            "4_occupancy_ratio": occupancy_ratio(),
        },
        "elapsed_s": round(time.time() - t0, 1),
    }
    OUT.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    g, o = doc["members"]["3_grid_cells_sample_size"], \
        doc["members"]["4_occupancy_ratio"]
    print(f"=== S6-B2938 figures, derived ===")
    print(f"  grid cells dead on sample size: {g['sample_size_dead']} of "
          f"{g['cells']} across {g['grid_artifacts']} artifacts = {g['pct']}%")
    print(f"  occupancy rows vs landed: {o['occupancy_skip_rows']} vs "
          f"{o['landed_trades']} = {o['ratio']}x")
    print(f"  -> {OUT} ({doc['elapsed_s']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
