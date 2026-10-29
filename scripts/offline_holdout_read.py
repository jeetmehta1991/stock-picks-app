#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} via
# offline_level_sweep.load, per CHECKLIST #77.
"""B2644 (S6-B2638b, owner-fired 2026-09-08): STEP 2 for an offline-free
strategy - the one-shot holdout read, all cells x exits in a single artifact.

OWNER RULING 2026-09-08 (runbook §3.4 F5): since the campaign is offline,
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

THE BASIS IS THE STEP-1 ARTIFACT'S (S6-B3314, owner ruling 2026-10-27, option
(a)): the read scores on the P&L basis the sweep RECORDED - net through
roster_core.net_pnl when the sweep says net. A sweep written before S6-B3314
records none and graded raw cube pnl, so an absent field reads 'gross' and the
artifact says where the basis came from (basis_source), as the breadth read
does (S6-B3139ag).

Refusals inherited from the sweep (fail closed, L642): reproduction of the
landed fire set at production levels, signal coverage, join completeness. Plus
one of its own: the axes and production levels passed here must EQUAL the
Step-1 artifact's - grading a different grid than the one pre-registered is a
different experiment wearing the same name.

Usage:
  python scripts/offline_holdout_read.py \
      --sweep-artifact output_audit/b2638_pead_step1_is_surface.json \
      --out output_audit/b2644_pead_step2_holdout.json --ruling WORDS --ruling-ticket S6-Bnnnn

--ruling / --ruling-ticket (S6-B3338): required. The owner's own word for THIS
read - a Step-2 holdout read is a one-way door - checked against the ticket's
ledger rows (scripts/owner_word.py) before the read, and stamped into the
artifact as owner_word.
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
               min_n: int, *, band_coverage=None, coverage_artifacts=()) -> dict:
    rec1 = json.loads(sweep_artifact.read_text(encoding="utf-8"))
    # S6-B3294 (L912): the read's SUBJECT comes from the Step-1 artifact it
    # re-scores - the leg it swept, whether the survival filter restricted
    # the fires, and the derive module whose keys its axes read - never from
    # a flag or a default; a derive module that moved since the
    # pre-registration is a different experiment and refuses.
    # S6-B3314: the basis is part of the subject - the sweep RECORDED it, and
    # a sweep from before S6-B3314 scored raw cube pnl, so absent reads gross
    basis = rec1.get("basis") or "gross"
    basis_source = ("the Step-1 artifact's recorded basis" if rec1.get("basis")
                    else "absent from the Step-1 artifact - read as gross, the "
                         "raw cube pnl every depth sweep graded before S6-B3314")
    subject = {"direction": rec1.get("direction"),
               "survival": bool(((rec1.get("evidence") or {}).get("survival_filter")
                                 or {}).get("applied")),
               "derive": rec1.get("derive"),
               "basis": basis,
               "coverage_artifacts": [str(c) for c in coverage_artifacts]}
    derive_fn = None
    if subject["derive"]:
        derive_fn, now = ols.load_derive(ROOT / subject["derive"]["path"])
        if now["sha256"] != subject["derive"].get("sha256"):
            raise SystemExit(
                f"REFUSED (S6-B3294): derive module {subject['derive']['path']} has "
                f"sha {now['sha256'][:12]} but the pre-registered sweep recorded "
                f"{str(subject['derive'].get('sha256'))[:12]} - a changed derivation "
                "is a different experiment wearing the pre-registration's name")
    axes = [dict(a) for a in rec1["axes"]]  # S6-B3313: every field the sweep wrote
    # rides - a key/op/levels rebuild dropped the OR 'group' and ANDed the arms
    production = tuple(rec1["production_levels"])
    prereg = rec1["preregistration_candidate"]
    strategy = rec1["strategy"]
    # S6-B3293: re-evaluated HERE as well, so an artifact written before the
    # rule (one still naming a negative or noise best cell) is refused too.
    _why = rec1.get("preregistration_refusal") or ols.preregistration_refusal(rec1)
    if _why:
        raise SystemExit(
            "REFUSED (S6-B3293): the Step-1 artifact names no preregistration "
            f"candidate worth the read - {_why}. A holdout read spends a one-way "
            "door; nothing here is worth it.")

    # ---- S6-B2886: THE BAND-COVERAGE REFUSAL -----------------------
    # THIS SCRIPT SPENDS THE PRE-REGISTRATION - a one-way door. The
    # refusals below it all ask whether the DATA is sound; this one asks
    # whether the QUESTION is whole, which is the thing that actually
    # went wrong. MEASURED at B2859: a 130-trial read was taken covering
    # ONE axis of five and the owner had to overrule relying on it. No R1
    # gate would have touched that - the inventory was clean and the read
    # was pre-registered. So the durable question is not how to stop a
    # band inventory being written; it is what must be true before a read
    # is PERMITTED to spend the door (S6-B2886, council First Principles).
    #
    # The three ways to satisfy it are all MACHINE-CHECKABLE fields of
    # the Step-1 artifact, never prose: a level is GRADED (a row carrying
    # axis/level with a non-null is_sharpe), or listed in
    # `discarded_levels`, or named in `resim_configs`. A gate whose exit
    # is an argument is not a gate (council Outsider).
    if band_coverage is None:
        from band_coverage_gate import coverage_report
        try:
            band_coverage = coverage_report(
                strategy, [str(sweep_artifact)] + [str(c) for c in coverage_artifacts])
        except SystemExit as exc:
            # the helper exits hard when a strategy has no Table A spec;
            # translate it into THIS script's refusal rather than
            # inheriting a crash that reads like a bug
            raise SystemExit(
                f"REFUSED (S6-B2886): {exc}. A holdout read spends a "
                "one-way door, and a strategy with no band inventory has "
                "no way to show the door is being spent on the whole "
                "question. Write the Table A entry first.") from None
    if not band_coverage.get("evaluable", False):
        raise SystemExit(
            "REFUSED (S6-B2886): band coverage is NOT EVALUABLE for "
            f"{strategy} - {band_coverage.get('reason', 'no reason given')}. "
            "Fail closed: an unevaluable coverage report is not a clean "
            "one (L642).")
    if not band_coverage.get("complete", False):
        gaps = [(p.get("param"), p.get("untested"))
                for p in band_coverage.get("params", [])
                if p.get("untested")]
        detail = "; ".join(f"{k}={v}" for k, v in gaps[:6])
        raise SystemExit(
            f"REFUSED (S6-B2886): {len(gaps)} of "
            f"{len(band_coverage.get('params', []))} banded parameters "
            f"carry UNTESTED levels, so this read would spend the "
            "pre-registration on part of the question: " + detail +
            ". Each level must be GRADED in the cited Step-1 artifact, "
            "listed in its `discarded_levels`, or named in its "
            "`resim_configs` - all three are fields, not prose. B2859 "
            "spent a 130-trial read on 1 of 5 axes and the owner "
            "overruled relying on it; that is the outcome this refuses.")

    # S6-B3139g: a CLOSED strategy's holdout is not read offline either -
    # the launch path's refusal, the owner's override register as the
    # escape. Placed AFTER the band-coverage refusal (it asks whether the
    # question is whole; this asks whether it may be asked at all) and
    # BEFORE the first data read, so no holdout row is ever touched.
    import producer_variant_table as _pvt
    _closed = _pvt.offline_retest_refusal(strategy)
    if _closed:
        raise SystemExit("REFUSED (S6-B3139g): " + _closed)
    m, ev = ols.load(strategy, axes, direction=subject["direction"],
                     survival=subject["survival"], derive=derive_fn,
                     basis=basis)
    if ev["coverage"] < coverage_min:
        raise SystemExit(f"REFUSED: coverage {ev['coverage']:.4f} < {coverage_min}")
    if ev["unmatched_join_rows"]:
        raise SystemExit(f"REFUSED: {ev['unmatched_join_rows']} unmatched cube rows")
    fires = m.drop_duplicates(["ticker", "entry_date"])
    repro = len(ols.keep(fires, axes, production)) / max(len(fires), 1)
    if repro < repro_min:
        raise SystemExit(f"REFUSED: production reproduces {repro:.4f} < {repro_min}")
    # S6-B3195: after the reproduction refusal, before any cell is read
    _loose = ols.looser_levels(axes, production)
    if _loose:
        raise SystemExit("REFUSED (S6-B3195): " + "; ".join(_loose) + " - a "
                         "looser level's holdout cell would be production's")

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
            "basis": basis, "basis_source": basis_source,     # S6-B3314
            "subject": subject, "band_coverage": band_coverage,
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
            f"{rec['graded']} graded"
            # S6-B3314: the basis the read records - a pre-S6-B3314 read
            # records none, and its render stays byte-identical to the
            # committed table beside it (test_b2644's writer-reader contract)
            + (f"; basis {rec['basis']} ({rec['basis_source']})" if rec.get("basis") else "")
            + ".\n\n"
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
    ap.add_argument("--coverage-artifact", action="append", default=[],
                    help="S6-B3294: a sibling Step-1 artifact (the other leg's "
                         "sweep) whose graded levels count toward the band-"
                         "coverage gate beside --sweep-artifact's")
    # S6-B3338: the holdout read is a one-way door that needs the owner's
    # own word (runbook 0.6) - quoted in a row of its ticket and stamped
    # into the artifact (scripts/owner_word.py; breadth_step2_read.py has
    # required --ruling since B2678, this read had none)
    ap.add_argument("--ruling", required=True,
                    help="the owner's words opening this read, verbatim as its "
                         "ledger row records them")
    ap.add_argument("--ruling-ticket", required=True,
                    help="the ticket whose row records --ruling")
    a = ap.parse_args()

    import owner_word
    word = {"ticket": a.ruling_ticket.strip(),
            "verbatim": owner_word.normalise(a.ruling)}
    werrs = owner_word.refusals(word, door="Step-2 holdout read")
    if werrs:
        raise SystemExit(werrs[0])
    out = Path(a.out)
    if out.exists() and not a.force_rerun:
        raise SystemExit(f"REFUSED: {out} exists - the holdout is already spent; "
                         "--force-rerun labels a re-read as such")
    rec = read_step2(Path(a.sweep_artifact), a.coverage_min, a.repro_min, a.min_n,
                     coverage_artifacts=[Path(c) for c in a.coverage_artifact])
    rec["owner_word"] = word
    if a.force_rerun:
        rec["rerun_of_spent_holdout"] = True
    from roster_core import stamp_metric_code as _smc  # S6-B3139i
    _smc(rec)
    out.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    out.with_suffix(".md").write_text(render_table(rec), encoding="utf-8")

    adm = rec["admission"]
    print(f"{rec['strategy']} STEP 2: {rec['verdict']} (basis {rec['basis']}: "
          f"{rec['basis_source']})")
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
