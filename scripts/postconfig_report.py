#!/usr/bin/env python
"""B2198 (L651): RENDER the post-config battery's result for one config.

Source: output_audit/postconfig_ledger.json + output_audit/<cube>_grid_auto.json
(the battery's own artifacts, written by scripts/run_postconfig.py); per CHECKLIST #77.

THE MISS THIS CLOSES: the battery has run automatically on every landing since
B2177 and its output went to DISK ONLY - the ledger entry and the auto grid.
Every hourly report VERIFIED that it ran (a boolean) and quoted one headline
number; the owner asked "if they were triggered, why didn't I see the result
for each config run?" and was right - "the mandatory post config analysis is to
be run each time a config lands" is a directive about a DELIVERED analysis, not
about a file written somewhere.

So the report card is a SCRIPT, not a habit: one command renders every step's
status with its evidence, the funnel, and the headline cell, from the artifacts
the battery already wrote. A per-landing report that depends on remembering to
write prose is the thing that failed.

Usage:
  python scripts/postconfig_report.py --cube-dir output_b2190_sw5_sw5
  python scripts/postconfig_report.py --cube-dir <dir> --md   # markdown table
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "output_audit" / "postconfig_ledger.json"

# The battery's own step set. AUTO steps must be DONE on a healthy landing;
# JUDGMENT steps ride the wave review by design (never silently absent - they
# are listed here so a reader sees WHAT was not done, not just what was).
AUTO_STEPS = ("1_cube_sanity", "2_grade_with_config_params",
              "3_outlier_discrepancy_sweep", "4_three_leg_spot_check",
              "6b_equivalence_class_check")
JUDGMENT_STEPS = ("5_adversarial_lens_review", "6_post_fix_recheck",
                  "7_implement_in_engine", "8_verdict_with_denominators")
NOISE_FLOOR = 0.333   # B2009 selection-noise floor, per-cell


def grid_path(cube_dir: str) -> Path:
    return ROOT / "output_audit" / f"{cube_dir}_grid_auto.json"


def report(cube_dir: str) -> dict:
    """Every field the report card shows, read from the battery's artifacts."""
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    entry = ledger.get(cube_dir)
    out: dict = {"cube_dir": cube_dir, "ledger_present": entry is not None,
                 "auto": {}, "judgment": {}, "grid_present": False}
    if entry:
        for k in AUTO_STEPS:
            row = entry.get(k)
            out["auto"][k] = {"status": (row or {}).get("status", "ABSENT"),
                              "evidence": (row or {}).get("evidence", "")}
        for k in JUDGMENT_STEPS:
            row = entry.get(k)
            out["judgment"][k] = {"status": (row or {}).get("status", "ABSENT"),
                                  "evidence": (row or {}).get("evidence", "")}
    out["all_auto_done"] = bool(entry) and all(
        v["status"] == "DONE" for v in out["auto"].values())

    gp = grid_path(cube_dir)
    if gp.exists():
        g = json.loads(gp.read_text(encoding="utf-8"))
        out["grid_present"] = True
        out["config"] = g.get("config")
        out["carried"] = g.get("step1_combinations_carried")
        out["distinct"] = g.get("step1_distinct_outcomes")
        rank = g.get("step1_ranking") or []
        if rank:
            r = rank[0]
            out["best"] = {"is_ci_lo": r.get("is_ci_lo"),
                           "is_sharpe": r.get("is_sharpe"),
                           "fires": r.get("fires"), "exit": r.get("exit"),
                           "verdict": (r.get("admit") or {}).get("verdict")}
            # An unmeasured value renders as None here and as "-" below; a real
            # 0.0 renders as 0.0 (L580 - a measured zero is evidence).
            cl = r.get("is_ci_lo")
            out["above_floor"] = None if cl is None else cl > NOISE_FLOOR
    return out


def render(rep: dict, md: bool = False) -> list[str]:
    lines = [f"# POST-CONFIG BATTERY REPORT - {rep['cube_dir']}", ""]
    if not rep["ledger_present"]:
        lines.append("**NO LEDGER ENTRY** - the battery did not record this "
                     "config. Absence is DEAD, not in-progress (L641).")
        return lines
    lines += ["| step | class | status | evidence (truncated) |",
              "|---|---|---|---|"]
    for k, v in rep["auto"].items():
        ev = (v["evidence"] or "")[:150].replace("|", "/")
        lines.append(f"| {k} | AUTO | **{v['status']}** | {ev} |")
    for k, v in rep["judgment"].items():
        ev = (v["evidence"] or "")[:150].replace("|", "/")
        lines.append(f"| {k} | JUDGMENT | {v['status']} | {ev} |")
    lines += ["", f"**All AUTO steps DONE: {rep['all_auto_done']}**", ""]
    if rep["grid_present"]:
        b = rep.get("best") or {}
        cl = b.get("is_ci_lo")
        floor = ("-" if cl is None else
                 ("ABOVE" if rep.get("above_floor") else "below"))
        lines += [f"**Grid** {rep.get('config')} - carried "
                  f"{rep.get('carried')} / distinct {rep.get('distinct')}",
                  f"**Best cell** is_ci_lo "
                  f"{'-' if cl is None else cl} ({floor} the "
                  f"{NOISE_FLOOR} noise floor) | is_sharpe "
                  f"{b.get('is_sharpe', '-')} | fires {b.get('fires', '-')} | "
                  f"exit {b.get('exit', '-')} | verdict {b.get('verdict', '-')}"]
    else:
        lines.append("**NO AUTO GRID** - step 2 produced no artifact.")
    return lines


def all_cube_dirs() -> list[str]:
    """Every config the battery has recorded, oldest ledger entry first.

    B2200: the ledger is the battery's own record, so its key set IS the
    population of processed configs - no glob heuristic, no guessing.
    """
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    return list(ledger)


def summary_table(cube_dirs: list[str]) -> list[str]:
    """One row per config: the battery's verdict at a glance.

    B2200 (owner: "where can I see the results for the last 4 configs?"):
    per-config cards answer one config at a time; a program spanning 35 runs
    needs the whole set in one view or the reader is left doing the joining.
    """
    rows = ["| config | AUTO steps | judgment steps | best IS-CI-lo | vs 0.333 floor | best exit |",
            "|---|---|---|---|---|---|"]
    for cd in cube_dirs:
        r = report(cd)
        auto = (f"{sum(1 for v in r['auto'].values() if v['status'] == 'DONE')}"
                f"/{len(AUTO_STEPS)} DONE")
        jud = (f"{sum(1 for v in r['judgment'].values() if v['status'] == 'SKIPPED')}"
               f"/{len(JUDGMENT_STEPS)} pending review")
        b = r.get("best") or {}
        cl = b.get("is_ci_lo")
        floor = "-" if cl is None else ("ABOVE" if r.get("above_floor") else "below")
        rows.append(f"| {cd} | {auto} | {jud} | {'-' if cl is None else cl} | "
                    f"{floor} | {b.get('exit', '-')} |")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube-dir", default="")
    ap.add_argument("--all", action="store_true",
                    help="one summary row per config the battery has recorded")
    ap.add_argument("--last", type=int, default=0,
                    help="with --all: only the N most recent configs")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    if a.all:
        dirs = all_cube_dirs()
        if a.last:
            dirs = dirs[-a.last:]
        print(f"# POST-CONFIG BATTERY - {len(dirs)} config(s)")
        print("")
        for line in summary_table(dirs):
            print(line)
        return 0
    if not a.cube_dir:
        print("--cube-dir required (or --all)")
        return 2
    for line in render(report(a.cube_dir), md=a.md):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
