#!/usr/bin/env python
"""S6-B2330: print THE Step-1 ranked list (Table D) - never retype it.

Source: output_audit/<cube_dir>_grid_auto.json artifacts (the graders' own
output), rendered through producer_variant_table.table_d, which owns the column
set; per CHECKLIST #77 and the show_table_c.py precedent.

WHY THIS EXISTS AS A COMMAND. Table C's docstring records the miss this
prevents: a locked table was retyped into chat three times and silently lost
four columns each time, until the owner caught it. A format enforced by the
writer is not enforced by the QUOTER. So Table D is printed, never transcribed.

WHAT THE TABLE IS FOR. Table C answers "what happened inside one config".
Table D answers "across every config, which outcomes rank highest" - a
different grain, one row per (config x exit) outcome.

WHAT IT DELIBERATELY DOES NOT DO. It applies no gate. Step-1 admission is
min-trades >= 10 plus a ranked list with NO gates (owner ruling B1608), so
every column is displayed and none is used to exclude a row. Duplicate
signatures are LABELLED rather than dropped, because suppressing them would be
a gate in a step ruled to have none.

Usage:
  python scripts/show_table_d.py                 # top 20 across every grid
  python scripts/show_table_d.py --top 50        # deeper slice
  python scripts/show_table_d.py --only b2197_sw30sp150
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

    Ordered by the artifact's own mtime, matching show_table_c.py, so a newly
    landed config appears last and the reader sees the program's progression.
    """
    grids: dict[str, dict] = {}
    for p in sorted((ROOT / "output_audit").glob(GRID_GLOB),
                    key=lambda x: x.stat().st_mtime):
        name = p.name[len("output_"):-len("_grid_auto.json")]
        grids[name] = json.loads(p.read_text(encoding="utf-8"))
    return grids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20,
                    help="rows to show (default 20, the owner's ask)")
    ap.add_argument("--only", default="",
                    help="comma-separated config names to include")
    a = ap.parse_args()
    from producer_variant_table import table_d, table_d_params

    grids = discover()
    if a.only:
        want = {s.strip() for s in a.only.split(",") if s.strip()}
        grids = {k: v for k, v in grids.items()
                 if any(w in k for w in want)}
    if not grids:
        print("no graded grids found - nothing to rank")
        return 1
    for line in table_d(grids, top=a.top):
        print(line)
    # S6-B2334: the six axes follow in the SAME order, joined on `#`
    print()
    print("### TABLE D-2 - THE SIX SWEPT AXES")
    print()
    for line in table_d_params(grids, top=a.top):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
