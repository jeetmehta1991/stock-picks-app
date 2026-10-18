#!/usr/bin/env python
"""S6-B3204 (DECISION A, owner approved 2026-10-18): the Phase-1B PORTFOLIO-UNIT
evaluation - stage 1, admission -> trade-source resolution.

WHY THIS STAGE EXISTS SEPARATELY. The 16 Step-2 admissions carry heterogeneous
provenance: 3 name a Step-2 cube directly; 13 are offline campaigns whose
grids re-scored the R5 merged cube (their own _doc lines, or the grader's CUBE
constant in institutional_companion_grid.py, name output_r5_merged_1_7). A
blend built on a guessed join would inherit every accident of the guess
(L722/L724), so resolution is its own stage with its own artifact, and ANY
admission the resolver cannot trace is REFUSED BY NAME - never skipped
silently (#279). Stage 2 (trade extraction + NET blend at the tiered position
sizes) consumes this artifact and refuses while any admission is unresolved.

Resolution rules, in order, each keyed on the admission's OWN artifact:
  1. grid_artifact named output_<cube>_grid_auto.json -> that cube dir.
  2. the artifact json carries cube_dir -> that cube dir.
  3. the artifact's _doc names output_r5_merged_1_7 -> the R5 merged cube
     (an offline re-score; the combination re-applies at stage 2).
  4. otherwise REFUSED with the reason.
A resolved source must hold trade_exit_detail.csv on disk or the admission is
REFUSED (fail closed - absence of the data is not a quiet shrink of the book).

Usage:
  python scripts/build_phase1b_portfolio.py --resolve
      writes output_audit/b3204_portfolio_resolution.json and prints the table.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADMISSIONS = ROOT / "output_audit" / "phase_1b_step2_admissions.json"
RESOLUTION = ROOT / "output_audit" / "b3204_portfolio_resolution.json"
R5_CUBE = "output_r5_merged_1_7"
TRADE_FILE = "trade_exit_detail.csv"
GRID_SUFFIX = "_grid_auto.json"


def load_admissions(path=None) -> list[dict]:
    p = Path(path) if path else ADMISSIONS
    return json.loads(p.read_text(encoding="utf-8"))["admissions"]


def resolve_one(adm: dict, root=None) -> dict:
    """One admission -> its trade-source record (or a REFUSED record)."""
    root = Path(root) if root else ROOT
    strat = adm.get("strategy") or "<unnamed>"
    ga = adm.get("grid_artifact") or ""
    out = {"strategy": strat, "grid_artifact": ga,
           "combination": adm.get("combination"), "exit": adm.get("exit"),
           "direction": adm.get("direction")}
    gp = root / ga
    if not ga or not gp.exists():
        return {**out, "resolution": "REFUSED",
                "reason": f"grid artifact missing: {ga!r}"}
    name = gp.name
    cube = None
    how = None
    if name.startswith("output_") and name.endswith(GRID_SUFFIX):
        # the cube DIR keeps the output_ prefix: output_<x>_grid_auto.json
        # names the dir output_<x> (first run refused smc by stripping it)
        cube = name[:-len(GRID_SUFFIX)]
        how = "DIRECT (cube named by the grid artifact's own filename)"
    else:
        art = json.loads(gp.read_text(encoding="utf-8"))
        cd = art.get("cube_dir") or art.get("cube") or ""
        doc = str(art.get("_doc") or "")
        if cd:
            cube = cd
            how = "DIRECT (artifact's own cube_dir field)"
        elif R5_CUBE in doc:
            cube = R5_CUBE
            how = ("R5_RESCORE (the artifact's _doc names the R5 merged cube "
                   "as its source; the combination re-applies at stage 2)")
    if cube is None:
        return {**out, "resolution": "REFUSED",
                "reason": "no cube pointer: filename not output_*_grid_auto, "
                          "no cube_dir field, _doc names no known cube"}
    tf = root / cube / TRADE_FILE
    if not tf.exists():
        return {**out, "resolution": "REFUSED", "cube": cube,
                "reason": f"{cube}/{TRADE_FILE} not on disk"}
    return {**out, "resolution": "RESOLVED", "cube": cube, "how": how,
            "trade_file": f"{cube}/{TRADE_FILE}",
            "trade_file_bytes": tf.stat().st_size}


def resolve(admissions=None, root=None) -> dict:
    adms = admissions if admissions is not None else load_admissions()
    rows = [resolve_one(a, root=root) for a in adms]
    refused = [r for r in rows if r["resolution"] == "REFUSED"]
    return {
        "_doc": ("S6-B3204 stage 1 - admission -> trade-source resolution for "
                 "the Phase-1B portfolio-unit evaluation (owner approved "
                 "2026-10-18). Every admission resolves or is REFUSED by "
                 "name; stage 2 refuses to blend while any row is REFUSED."),
        "admissions": len(rows),
        "resolved": len(rows) - len(refused),
        "refused": [r["strategy"] for r in refused],
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolve", action="store_true",
                    help="run stage 1 and write the resolution artifact")
    a = ap.parse_args()
    if not a.resolve:
        ap.print_help()
        return 2
    res = resolve()
    RESOLUTION.write_bytes(
        (json.dumps(res, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"admissions {res['admissions']} | resolved {res['resolved']} | "
          f"refused {len(res['refused'])}")
    for r in res["rows"]:
        tag = r["resolution"]
        tgt = r.get("cube") or r.get("reason")
        print(f"  {r['strategy'][:44]:44} {tag:9} {tgt}")
    if res["refused"]:
        print(f"REFUSED by name: {', '.join(res['refused'])}")
        return 1
    print(f"wrote {RESOLUTION}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
