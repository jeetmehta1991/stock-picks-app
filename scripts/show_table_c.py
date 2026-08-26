#!/usr/bin/env python
"""B2199 (L652): print THE locked Table C - never retype it.

Source: output_audit/<cube_dir>_grid_auto.json artifacts (the graders' own
output), rendered through producer_variant_table.table_c, which owns the locked
column set; per CHECKLIST #77.

THE MISS THIS CLOSES: Table C's format is LOCKED (B1701/B1898/B2137/B2181) at
12 columns, one of which - `P1-P6 bands tested` - is what distinguishes a config
that searched 18 parameter values from one that searched 2. The renderer has
always emitted it and the committed artifact carries it; I retyped the table
into chat three times and silently dropped four columns each time, including
that one. The owner caught it: "Table c is missing a column ... hasn't the
format been locked in?"

A locked format enforced by the writer is not enforced by the QUOTER. So
quoting is now a command: this prints every graded config's row, in the locked
order, from the artifacts - with no opportunity to abbreviate.

Usage:
  python scripts/show_table_c.py                 # every graded config found
  python scripts/show_table_c.py --only b2190_sw5,b2183_sw30
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

GRID_GLOB = "output_*_grid_auto.json"


def discover() -> dict[str, dict]:
    """Every auto-graded config on disk, keyed by its config name.

    Ordered by the artifact's own mtime so a newly landed config appears last -
    the reader sees the program's progression, not an alphabetical shuffle.
    """
    grids: dict[str, dict] = {}
    paths = sorted((ROOT / "output_audit").glob(GRID_GLOB),
                   key=lambda p: p.stat().st_mtime)
    for p in paths:
        # output_<cube_dir>_grid_auto.json -> the wave name inside cube_dir
        name = p.name[len("output_"):-len("_grid_auto.json")]
        grids[name] = json.loads(p.read_text(encoding="utf-8"))
    return grids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="",
                    help="comma-separated config names to include")
    a = ap.parse_args()
    from producer_variant_table import table_c

    grids = discover()
    if a.only:
        want = [w.strip() for w in a.only.split(",") if w.strip()]
        missing = [w for w in want if not any(w in k for k in grids)]
        if missing:
            print(f"NOT FOUND (no graded artifact): {', '.join(missing)}")
        grids = {k: v for k, v in grids.items() if any(w in k for w in want)}
    if not grids:
        print("NO GRADED CONFIGS FOUND - nothing has been graded yet, which is "
              "different from a table with no rows.")
        return 1
    print(f"# TABLE C - {len(grids)} graded config(s), locked format")
    print("")
    for line in table_c(grids):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
