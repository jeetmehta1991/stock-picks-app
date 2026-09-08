#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} via
# offline_level_sweep.load, per CHECKLIST #77.
"""B2644 (S6-B2638b, owner-fired 2026-09-08): STEP 2 for an offline-free
strategy - the one-shot holdout read, all cells x exits in a single artifact.

OWNER RULING 2026-09-08 (runbook SS11.2b F5): since the campaign is offline,
Step 2 computes the holdout for ALL cells x exits IN ONE READ. The
PRE-REGISTERED cell - read from the Step-1 artifact's preregistration_candidate,
which was committed BEFORE any holdout code existed - CARRIES ADMISSION against
the six LIVE_GATES. Every other cell's line is DIAGNOSTIC and labelled
peeked_by_construction: it was not chosen before holdout contact, so it can
never be used to promote a different winner (the icg challenge-bound pattern,
output_audit/b2628_family_pass_prereg.json precedent).

THIS SCRIPT SPENDS THE PRE-REGISTRATION. Running it a second time re-reads a
holdout that is already spent; the artifact records the first run's identity so
a re-run cannot masquerade as a fresh test (it REFUSES if the out file exists,
unless --force-rerun, which labels the artifact RERUN_OF_SPENT_HOLDOUT).

Refusals inherited from the sweep (fail closed, L642): reproduction of the
landed fire set at production levels, signal coverage, join completeness. Plus
one of its own: the axes and production levels passed here must EQUAL the
Step-1 artifact's - grading a different grid than the one pre-registered is a
different experiment wearing the same name.

Usage:
  python scripts/offline_holdout_read.py \
      --sweep-artifact output_audit/b2638_pead_step1_is_surface.json \
      --out output_audit/b2644_pead_step2_holdout.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import offline_level_sweep as ols  # noqa: E402  (load/keep/parse_axis + refusals)
import roster_core as rc           # noqa: E402


def read_step2(sweep_artifact: Path, coverage_min: float, repro_min: float,
               min_n: int) -> dict:
    rec1 = json.loads(sweep_artifact.read_text(encoding="utf-8"))
    axes = [{"key": a["key"], "op": a["op"], "levels": a["levels"]}
            for a in rec1["axes"]]
    production = tuple(rec1["production_levels"])
    prereg = rec1["preregistration_candidate"]
    strategy = rec1["strategy"]

    m, ev = ols.load(strategy, axes)
    if ev["coverage"] < coverage_min:
        raise SystemExit(f"REFUSED: coverage {ev['coverage']:.4f} < {coverage_min}")
    if ev["unmatched_join_rows"]:
        raise SystemExit(f"REFUSED: {ev['unmatched_join_rows']} unmatched cube rows")
    fires = m.drop_duplicates(["ticker", "entry_date"])
    repro = len(ols.keep(fires, axes, production)) / max(len(fires), 1)
    if repro < repro_min:
        raise SystemExit(f"REFUSED: production reproduces {repro:.4f} < {repro_min}")

    import itertools
    rows = []
    for combo in itertools.product(*[a["levels"] for a in axes]):
        cell = ols.keep(m, axes, combo)
        for ex, sub in cell.groupby("exit_method"):
            ho = rc.holdout(sub)
            r = rc.evaluate(ho["pnl_pct"], ho["hold_days"], min_n=min_n,
                            full_period_n=len(sub))
            is_prereg = (list(combo) == list(prereg["levels"])
                         and ex == prereg["best_exit"])
            row = {"levels": list(combo), "exit": ex,
                   "holdout_n": int(len(ho)), "full_n": int(len(sub)),
                   "admission_bearing": is_prereg,
                   "peeked_by_construction": not is_prereg}
            if r is None:
                row["verdict"] = "BELOW_POWER_FLOOR"
            else:
                row.update({"holdout_sharpe": r["sharpe"], "sortino": r["sortino"],
                            "psr": r["psr"], "profit_factor": r["profit_factor"],
                            "win_rate": r["win_rate"], "gates": r["gates"],
                            "n_gates": r["n_gates"],
                            "n_gates_evaluable": r["n_gates_evaluable"],
                            "all_live_gates": r["all_live_gates"]})
                row["verdict"] = ("QUALIFIES" if r["all_live_gates"] else "FAIL")
                if r["all_live_gates"] and r["sharpe"] is not None:
                    row["margin"] = rc.qualifier_margin(r["sharpe"])
            rows.append(row)

    adm = [r for r in rows if r["admission_bearing"]]
    assert len(adm) == 1, f"admission-bearing rows: {len(adm)} (must be exactly 1)"
    graded = [r for r in rows if r["verdict"] != "BELOW_POWER_FLOOR"]
    peek_pass = [r for r in rows if r["peeked_by_construction"]
                 and r["verdict"] == "QUALIFIES"]
    return {"strategy": strategy, "step": 2,
            "design": "owner ruling 2026-09-08 - all cells x exits, one read; "
                      "pre-registered cell carries admission",
            "window": {"holdout": [str(rc.HO_START), str(rc.HO_END)]},
            "sweep_artifact": str(sweep_artifact),
            "preregistered": prereg, "evidence": ev, "reproduction": repro,
            "trials": len(rows), "graded": len(graded),
            "admission": adm[0],
            "verdict": adm[0]["verdict"],
            "peek_bound": {"cells_clearing_all_gates_besides_admission":
                           len(peek_pass),
                           "note": "diagnostic only - none of these was chosen "
                                   "before holdout contact and none can be "
                                   "promoted off this read"},
            # B2644b: ALL lines persist - computing 390 and writing 1 was the
            # L659 class (the disclosure dies at the caller). The owner asked
            # for every combination's holdout line; here they all are.
            "rows": rows}


def render_table(rec: dict, top: int = 20) -> str:
    rows = []
    head = (f"# STEP-2 HOLDOUT READ - {rec['strategy']}\n\n"
            f"{rec['design']}. Window {rec['window']['holdout'][0]} .. "
            f"{rec['window']['holdout'][1]}; {rec['trials']} (cell, exit) lines, "
            f"{rec['graded']} graded.\n\n"
            f"**ADMISSION-BEARING CELL VERDICT: {rec['verdict']}**\n\n")
    a = rec["admission"]
    g = a.get("gates", {})
    gate_line = ", ".join(f"{k}={'PASS' if v is True else ('FAIL' if v is False else 'N/E')}"
                          for k, v in g.items())
    head += (f"Pre-registered: levels {a['levels']}, exit {a['exit']}, holdout n "
             f"{a['holdout_n']}, full n {a['full_n']}, holdout sharpe "
             f"{a.get('holdout_sharpe')}, PF {a.get('profit_factor')}, sortino "
             f"{a.get('sortino')}, PSR {a.get('psr')}.\nGates: {gate_line}.\n\n")
    # the full ranked holdout view (top N by holdout sharpe) - every line
    # labelled ADMISSION or peeked, so the artifact cannot be misread as a menu
    ranked = sorted((r for r in rec["rows"] if r.get("holdout_sharpe") is not None),
                    key=lambda r: r["holdout_sharpe"], reverse=True)
    rows.append("| rank | levels | exit | HO n | HO sharpe | PF | sortino | PSR "
                "| gates | verdict | status |")
    rows.append("|" + "---|" * 11)
    for i, r in enumerate(ranked[:top], 1):
        status = "**ADMISSION**" if r["admission_bearing"] else "peeked"
        rows.append(
            f"| {i} | {r['levels']} | {r['exit']} | {r['holdout_n']} | "
            f"{r['holdout_sharpe']:.3f} | {r.get('profit_factor')} | "
            f"{r.get('sortino')} | {r.get('psr')} | "
            f"{r.get('n_gates')}/{r.get('n_gates_evaluable')} | {r['verdict']} "
            f"| {status} |")
    return head + "\n".join(rows) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep-artifact", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--coverage-min", type=float, default=0.99)
    ap.add_argument("--repro-min", type=float, default=0.999)
    ap.add_argument("--min-n", type=int, default=15)
    ap.add_argument("--force-rerun", action="store_true")
    a = ap.parse_args()

    out = Path(a.out)
    if out.exists() and not a.force_rerun:
        raise SystemExit(f"REFUSED: {out} exists - the holdout is already spent; "
                         "--force-rerun labels a re-read as such")
    rec = read_step2(Path(a.sweep_artifact), a.coverage_min, a.repro_min, a.min_n)
    if a.force_rerun:
        rec["rerun_of_spent_holdout"] = True
    out.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    out.with_suffix(".md").write_text(render_table(rec), encoding="utf-8")

    adm = rec["admission"]
    print(f"{rec['strategy']} STEP 2: {rec['verdict']}")
    print(f"  pre-registered {adm['levels']} exit {adm['exit']}: holdout sharpe "
          f"{adm.get('holdout_sharpe')} on n={adm['holdout_n']} "
          f"(full {adm['full_n']}); PF {adm.get('profit_factor')} sortino "
          f"{adm.get('sortino')} PSR {adm.get('psr')}")
    print(f"  gates passed {adm.get('n_gates')} of {adm.get('n_gates_evaluable')}")
    print(f"  peek bound (diagnostic): {rec['peek_bound']['cells_clearing_all_gates_besides_admission']} "
          f"other lines of {rec['trials']} clear all gates")
    print(f"wrote {out} and {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
