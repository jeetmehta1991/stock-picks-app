#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""B2678 (S6-B2671c, owner word 'S6-b2671c proceed' 2026-09-11): the breadth
STEP-2 - ONE holdout read of the Step-1 grid's cells, all of them, six
LIVE_GATES - plus the control-family comparison on every all-six qualifier
(the promoted B2658 rule, runbook 11.2b2).

FAIL-CLOSED: refuses to run without --ruling (the 11.2c word, recorded into
the artifact verbatim). The cells come from the Step-1 ARTIFACT's own rows
(the pre-registration), never re-derived - re-derivation could drift from
what was registered. The frame comes from breadth_step1_grid.build_frame,
the ONE loader both steps share.

PROVENANCE, on the artifact's face: the subject strategy's holdout was
previously read (the B2668 depth admission), and the spent-holdout
disclosure was accepted by the owner 2026-09-11 before this word - this
read is DISCLOSED-RE-READ, and the label travels with any admission.

CONTROL COMPARISON: for each all-six non-npt qualifier, the same axis at the
same level is applied to the CONTROL strategy's recorded fires (no depth
base) and the control's holdout sharpe lift (filtered minus unfiltered, same
exit) is reported beside the subject's. A control that shows the same lift
says the axis is general market structure, not the subject's edge. The
control's holdout was also previously read (its own campaign) - same
disclosed label.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import roster_core as rc  # noqa: E402
from breadth_step1_grid import BARRED_EXIT, build_frame  # noqa: E402


def grade_holdout(sub) -> dict | None:
    ho = rc.holdout(sub)
    return rc.evaluate(ho["pnl_pct"], ho["hold_days"], min_n=15,
                       full_period_n=len(sub))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step1-artifact", required=True)
    ap.add_argument("--ruling", required=True,
                    help="the owner's Step-2 word, verbatim (11.2c fail-closed)")
    ap.add_argument("--control", default="pead_long_high_yoy_growth_only",
                    help="control strategy for the B2658 comparison")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if not a.ruling.strip():
        raise SystemExit("REFUSED: empty --ruling")
    t0 = time.time()

    art = json.loads(Path(a.step1_artifact).read_text(encoding="utf-8"))
    strategy = art["strategy"]
    depth = art["depth_base"]
    cells = sorted({(r["axis"], r["op"], r["level"]) for r in art["rows"]})
    axis_keys = sorted({c[0] for c in cells})
    m, _ = build_frame(strategy, depth, axis_keys)
    print(f"frame {len(m):,} rows; {len(cells)} registered (axis,op,level) cells "
          f"({time.time()-t0:.0f}s)")

    def mask(frame, key, op, lev):
        if op == "ge":
            return (frame[key] >= lev) & frame[key].notna()
        if op == "le":
            return (frame[key] <= lev) & frame[key].notna()
        return (frame[key] == 1.0) & frame[key].notna()

    rows = []
    for key, op, lev in cells:
        sub_all = m[mask(m, key, op, lev)]
        for ex, sub in sub_all.groupby("exit_method"):
            r = grade_holdout(sub)
            si = rc.in_sample(sub)
            isr = rc._sharpe(si["pnl_pct"].values, si["hold_days"], min_n=10)
            rows.append({
                "holdout_sharpe": r["sharpe"] if r else None,
                "axis": key, "op": op, "level": float(lev), "exit": ex,
                "psr": r["psr"] if r else None,
                "profit_factor": r["profit_factor"] if r else None,
                "sortino": r["sortino"] if r else None,
                "ci_lo": r.get("ci_lo") if r else None,
                "holdout_n": r["n"] if r else None,
                "full_n": int(len(sub)),
                "is_sharpe": isr["sharpe"] if isr else None,
                "all_live_gates": bool(r and r["all_live_gates"]),
                "npt_barred": ex == BARRED_EXIT})
    quals = [r for r in rows if r["all_live_gates"] and not r["npt_barred"]]
    quals.sort(key=lambda r: -r["holdout_sharpe"])
    print(f"{len(rows)} cells read | {len(quals)} all-six non-npt qualifiers "
          f"({time.time()-t0:.0f}s)")

    # ---- control comparison on each qualifier (deduped axis/level/exit) -----
    controls = []
    if quals:
        ckeys = sorted({q["axis"] for q in quals})
        cm, _ = build_frame(a.control, None, ckeys)
        for q in quals:
            base_cell = cm[cm.exit_method == q["exit"]]
            filt = base_cell[mask(base_cell, q["axis"], q["op"], q["level"])]
            hb = rc.holdout(base_cell)
            hf = rc.holdout(filt)
            rb = rc._sharpe(hb["pnl_pct"].values, hb["hold_days"], min_n=10)
            rf = rc._sharpe(hf["pnl_pct"].values, hf["hold_days"], min_n=10)
            controls.append({
                "axis": q["axis"], "op": q["op"], "level": q["level"],
                "exit": q["exit"],
                "control_base_ho_sharpe": rb["sharpe"] if rb else None,
                "control_filtered_ho_sharpe": rf["sharpe"] if rf else None,
                "control_lift": (round(rf["sharpe"] - rb["sharpe"], 3)
                                 if (rb and rf) else None),
                "control_filtered_ho_n": int(len(hf)),
                "subject_qualifier_ho_sharpe": q["holdout_sharpe"]})

    rec = {"_doc": ("B2678 breadth Step-2 - one holdout read of every registered "
                    "b2673 cell (S6-B2671c) + B2658 control comparison; "
                    "DISCLOSED-RE-READ provenance travels with any admission"),
           "ruling_verbatim": a.ruling,
           "strategy": strategy, "depth_base": depth,
           "step1_artifact": a.step1_artifact,
           "provenance": {
               "subject_holdout_previously_read": "B2668 depth admission",
               "disclosure_accepted": "owner 2026-09-11 'I am ok with the disclosure'",
               "label": "DISCLOSED-RE-READ / GRID-SELECTED"},
           "cells_read": len(rows),
           "qualifiers_all_six_non_npt": len(quals),
           "qualifiers": quals,
           "control": {"strategy": a.control,
                       "note": "same axis/level/exit on the control's own fires, "
                               "no depth base; lift = filtered minus unfiltered "
                               "holdout sharpe",
                       "rows": controls},
           "rows": rows}
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
