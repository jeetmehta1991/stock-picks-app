#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""B2678 (S6-B2671c, owner word 'S6-b2671c proceed' 2026-09-11): the breadth
STEP-2 - ONE holdout read of the Step-1 grid's cells, all of them, six
LIVE_GATES - plus the control-family comparison on every all-six qualifier
(the promoted B2658 rule, runbook §3.5).

FAIL-CLOSED: refuses to run without --ruling (the runbook §0.6 word, recorded into
the artifact verbatim). The cells come from the Step-1 ARTIFACT's own rows
(the pre-registration), never re-derived - re-derivation could drift from
what was registered. The frame comes from breadth_step1_grid.build_frame,
the ONE loader both steps share.

PROVENANCE, on the artifact's face, from the CALLER (S6-B3139ah): which of
the subject's holdout reads came before this one (--prior-read, 'none' for
a first read) and the owner's words accepting the spent-holdout disclosure
(--disclosure, required whenever a prior read exists). The label follows:
DISCLOSED-RE-READ after a prior read, FIRST-READ otherwise, and it travels
with any admission. This block was once a literal naming one campaign's
prior read (B2668) and its disclosure quote, so every later read inherited
another campaign's history (L868).

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
from band_coverage_gate import coverage_report  # noqa: E402  (B2704 #299)
from breadth_step1_grid import BARRED_EXIT, _cell_mask, build_frame  # noqa: E402


def grade_holdout(sub) -> dict | None:
    ho = rc.holdout(sub)
    return rc.evaluate(ho["pnl_pct"], ho["hold_days"], min_n=15,
                       full_period_n=len(sub))


def require_multiplicity(art: dict, source: str) -> None:
    """S6-B2836a (B2839): a Step-2 holdout read may only follow a Step-1 whose
    MULTIPLICITY BLOCK RECONCILED. Under the B2836 no-pruning ruling the full
    combination population touches the holdout, so the trials-count honesty
    lives entirely in Step-1's multiplicity instrument - and this reader
    previously never looked (found by the B2836 enforcement-map grep).
    FAIL CLOSED on the absent key (L642: the absent case is the case the
    guard exists for), and on any value other than True.
    """
    mult = art.get("multiplicity")
    if not isinstance(mult, dict) or "reconciles" not in mult:
        raise SystemExit(
            f"REFUSED: {source} carries NO multiplicity block - Step-1 must "
            "run the runbook section 1.4 multiplicity instrument before any holdout read "
            "(S6-B2836a; fail closed on absence)")
    if mult.get("reconciles") is not True:
        raise SystemExit(
            f"REFUSED: {source} multiplicity.reconciles = "
            f"{mult.get('reconciles')!r} - a non-reconciled Step-1 cannot "
            "feed a holdout read (S6-B2836a)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step1-artifact", required=True)
    ap.add_argument("--ruling", required=True,
                    help="the owner's Step-2 word, verbatim (runbook section 0.6, fail-closed)")
    ap.add_argument("--control", default="pead_long_high_yoy_growth_only",
                    help="control strategy for the B2658 comparison")
    # B2849 (S6-B2848d, owner-approved): T5's ran-or-waived stops being
    # prose - the Step-2 read refuses unless the breadth leg's disposition
    # is stated, and a waiver carries a non-empty reason, both recorded
    # into the artifact.
    ap.add_argument("--breadth-disposition", required=True,
                    choices=("ran", "waived"))
    ap.add_argument("--breadth-reason", default="",
                    help="required non-empty when --breadth-disposition=waived")
    ap.add_argument("--out", required=True)
    # S6-B3139ah: provenance is the CALLER's statement, recorded verbatim -
    # no default, so a read can never inherit another campaign's history.
    ap.add_argument("--prior-read", required=True,
                    help="the subject's earlier holdout read(s), named, or "
                         "'none' for a first read")
    ap.add_argument("--disclosure", default="",
                    help="the owner's words accepting the spent-holdout "
                         "disclosure - required when --prior-read is not 'none'")
    ap.add_argument("--cube-dir", default=None,
                    help="SUBJECT run-dir override: read"
                         " <dir>/trade_exit_detail.csv + trade_log.csv for the"
                         " subject frame; the CONTROL comparison keeps the R5"
                         " default - its own fires (S6-B3113a)")
    a = ap.parse_args()
    if not a.ruling.strip():
        raise SystemExit("REFUSED: empty --ruling")
    if a.breadth_disposition == "waived" and not a.breadth_reason.strip():
        raise SystemExit(
            "REFUSED: --breadth-disposition=waived with no --breadth-reason "
            "- a waiver without its reason is a silent skip (S6-B2848d)")
    prior = a.prior_read.strip()
    if not prior:
        raise SystemExit("REFUSED: empty --prior-read - name the subject's "
                         "earlier holdout read(s), or 'none' (S6-B3139ah)")
    first_read = prior.lower() == "none"
    if not first_read and not a.disclosure.strip():
        raise SystemExit(
            "REFUSED: --prior-read names an earlier holdout read but "
            "--disclosure is empty - a re-read needs the owner's words "
            "accepting the spent-holdout disclosure (S6-B3139ah)")
    t0 = time.time()

    # S6-B3113a: the subject's fires live only in its own cube when the
    # depth line is a producer reconfiguration; the control leg below
    # RESTORES the R5 default (the control's own fires, per this file's
    # own note).
    import breadth_step1_grid as _g
    _default_paths = (_g.CUBE, _g.TRADE_LOG)
    if a.cube_dir:
        _g.CUBE = _g.ROOT / a.cube_dir / "trade_exit_detail.csv"
        _g.TRADE_LOG = _g.ROOT / a.cube_dir / "trade_log.csv"
        for _f in (_g.CUBE, _g.TRADE_LOG):
            if not _f.exists():
                raise SystemExit(f"REFUSED: --cube-dir file missing: {_f}")
        print(f"cube-dir override (subject frame): {a.cube_dir} (S6-B3113a)")
    art = json.loads(Path(a.step1_artifact).read_text(encoding="utf-8"))
    require_multiplicity(art, a.step1_artifact)   # S6-B2836a, fail closed
    strategy = art["strategy"]
    # S6-B3139g: the SUBJECT's holdout is refused for a CLOSED strategy
    # (the CONTROL is a comparison baseline, never a re-test)
    import producer_variant_table as _pvt
    _closed = _pvt.offline_retest_refusal(strategy)
    if _closed:
        raise SystemExit("REFUSED (S6-B3139g): " + _closed)
    depth = art["depth_base"]
    # S6-B3139ag: the read scores on the basis its Step-1 grid RECORDED -
    # never a second flag that could disagree with it. A grid built before
    # the basis field existed scored raw cube pnl, so absent reads "gross",
    # and the artifact says where the basis came from.
    basis = art.get("basis") or "gross"
    basis_source = ("the Step-1 artifact's recorded basis" if art.get("basis")
                    else "absent on the Step-1 artifact - grids before "
                         "S6-B3139ag scored gross")
    cells = sorted({(r["axis"], r["op"], r["level"]) for r in art["rows"]})
    axis_keys = sorted({c[0] for c in cells})
    # S6-B3139am: grade the leg the Step-1 artifact RECORDED. An artifact
    # without the key predates per-leg grids (B3118) and was graded on both.
    leg = art.get("leg") or "both"
    m, _ = build_frame(strategy, depth, axis_keys, basis=basis, leg=leg)
    print(f"leg {leg} (from the Step-1 artifact)")
    print(f"frame {len(m):,} rows; {len(cells)} registered (axis,op,level) cells "
          f"; basis {basis} ({time.time()-t0:.0f}s)")

    def mask(frame, key, op, lev):
        # S6-B3139ag: the grid's ONE mask definition. This local copy handled
        # ge / le / else ==1.0, so a B3118 eq_false cell read its COMPLEMENT
        # (0 of 2 committed reads carried eq_false cells - measured).
        return _cell_mask(frame, key, op, lev) & frame[key].notna()

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
        # S6-B3113a: control on its OWN fires - the R5 default, always
        _g.CUBE, _g.TRADE_LOG = _default_paths
        cm, _ = build_frame(a.control, None, ckeys, basis=basis)
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

    # B2704 (#299, owner-mandated): the band-coverage verdict is stamped
    # UNCONDITIONALLY; a zero-qualifier outcome with incomplete coverage
    # is "leg negative; depth leg NOT RUN", never a strategy failure.
    try:
        bc = coverage_report(strategy, [a.step1_artifact])
    except SystemExit as e:
        bc = {"evaluable": False, "reason": str(e)}
    disposition = (
        "STEP-2 NEGATIVE - ALL TABLE A BANDS TESTED - failure declarable"
        if (not quals) and bc.get("complete") else
        "READ LEG NEGATIVE; UNTESTED TABLE A BAND LEVELS REMAIN - NO "
        "FAILURE VERDICT (CHECKLIST #299/B2704)" if not quals else
        "QUALIFIERS FOUND - see rows")
    rec = {"band_coverage": bc, "disposition": disposition,
           "_doc": ("B2678 breadth Step-2 - one holdout read of every registered "
                    "b2673 cell (S6-B2671c) + B2658 control comparison; "
                    "DISCLOSED-RE-READ provenance travels with any admission"),
           "ruling_verbatim": a.ruling,
           "breadth_leg": {"disposition": a.breadth_disposition,
                           "reason": a.breadth_reason.strip()},
           "strategy": strategy, "depth_base": depth, "leg": leg,
           "basis": basis, "basis_source": basis_source,
           "step1_artifact": a.step1_artifact,
           "provenance": {
               "subject_holdout_previously_read": prior,
               "disclosure_accepted": (None if first_read
                                       else a.disclosure.strip()),
               "label": ("FIRST-READ / GRID-SELECTED" if first_read
                         else "DISCLOSED-RE-READ / GRID-SELECTED")},
           "cube_dir": a.cube_dir or "output_r5_merged_1_7 (default)",
           "control_source": "output_r5_merged_1_7 (control's own fires)",
           "cells_read": len(rows),
           "qualifiers_all_six_non_npt": len(quals),
           "qualifiers": quals,
           "control": {"strategy": a.control,
                       "note": "same axis/level/exit on the control's own fires, "
                               "no depth base; lift = filtered minus unfiltered "
                               "holdout sharpe",
                       "rows": controls},
           "rows": rows}
    from roster_core import stamp_metric_code as _smc  # S6-B3139i
    _smc(rec)
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
