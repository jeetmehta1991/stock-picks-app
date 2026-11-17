#!/usr/bin/env python
"""S6-B3454 (B3139q-r217, L1019): A HOLDOUT-READ PACKET IS GENERATED FROM THE
STEP-1 ARTIFACTS AND THE READERS' OWN REFUSALS, NEVER TYPED.

WHY. The B3139q-r216 close put S6-B3423's step-5 packet to the owner as
'Read the holdout once for each of the 3 survivors?' - typed from the campaign
log - and the owner approved it (sent 2026-11-17T16:13:49Z). It could not run
as approved: scripts/offline_holdout_read.py refused all 3 on the band-coverage
gate (S6-B2886 / S6-B3339) - 22 engine-only Table A levels no waiver covered -
and the packet left out the 5 breadth grids the plan's step 5 puts in it
('every Step-1 survivor'). The owner was asked a second time (L1019; a
compliance failure against #164 with L945 - a packet option's scope comes from
its reach - and #230 with L972 - a route names every gate it crosses).

WHAT IT DOES, reading no holdout row and recording nothing:
  1. classifies each given Step-1 artifact by the fields its writer stamps -
     a DEPTH surface (offline_level_sweep: preregistration_candidate and
     cells_graded) or a BREADTH grid (breadth_step1_grid: depth_base, leg and
     step1_ranking); anything else is listed as not a Step-1 read source;
  2. names the SURVIVORS - a depth surface whose
     offline_level_sweep.preregistration_refusal is empty (positive IS best,
     its null at or under producer_variant_table.DEPTH_NULL_P_MAX); a breadth
     grid whose own permutation null prices its best cell at or under the same
     DEPTH_NULL_P_MAX with a positive IS best - the one ruled noise bar
     (S6-B3206); no breadth-specific bar is ruled, and the packet says so;
  3. runs, per survivor, every refusal its reader applies BEFORE any holdout
     row is read: the Step-1 artifact committed and its multiplicity block
     reconciling (holdout_reads), the closed-strategy refusal
     (producer_variant_table.offline_retest_refusal) and the holdout-read
     ledger's prior reads of the subject; for a depth read also the
     band-coverage gate (sibling surfaces of the same strategy and leg counted
     as offline_holdout_read's --coverage-artifact counts them) and the
     looser-level refusal; a breadth read STAMPS coverage instead of refusing,
     so its gaps are listed as a disclosure;
  4. orders the reads of one subject (strategy, leg - a leg of None overlaps
     every leg, as the ledger reads it): the first is a clean read, every
     later one a DISCLOSED-RE-READ that needs the owner's disclosure words.
The owner word each read needs is not checked here - it is the decision the
packet is for.

Usage:
  python scripts/holdout_packet.py --artifacts output_audit/b3423_*_surface.json \
      output_audit/b3423_*_breadth_net_long.json [--out output_audit/x.json]
Exit 0 always when the packet is built (a refusal is a row, not a failure);
2 when an artifact cannot be read.
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def classify(doc) -> str | None:
    """'depth', 'breadth' or None, from the fields each Step-1 writer stamps."""
    if not isinstance(doc, dict):
        return None
    if "preregistration_candidate" in doc and "cells_graded" in doc:
        return "depth"
    if ("depth_base" in doc and "leg" in doc and "step1_ranking" in doc
            and isinstance(doc.get("rows"), list)):
        return "breadth"
    return None


def subject(kind: str, doc: dict) -> tuple:
    """(strategy, leg) as the holdout-read ledger keys a read - the depth
    reader's direction, the breadth reader's leg; None reads as both legs."""
    leg = doc.get("direction") if kind == "depth" else doc.get("leg")
    return doc.get("strategy"), (leg or "both")


def survivor(kind: str, doc: dict) -> tuple[bool, str]:
    """(is a survivor, why) by the readers' own candidate rules."""
    from producer_variant_table import DEPTH_NULL_P_MAX
    if kind == "depth":
        import offline_level_sweep as ols
        why = doc.get("preregistration_refusal") or ols.preregistration_refusal(doc)
        if why:
            return False, why
        c = doc["preregistration_candidate"]
        p = (doc.get("permutation_null") or {}).get("p_value_best")
        return True, (f"pre-registered {c.get('levels')} @ {c.get('best_exit')}, IS "
                      f"{c.get('is_sharpe')}, null p {p}")
    pn = doc.get("permutation_null") or {}
    p, best = pn.get("p_value"), pn.get("observed_best_is_sharpe")
    if p is None or best is None:
        return False, "the grid carries no permutation null - its best cell is unpriced"
    if float(best) <= 0:
        return False, f"best IS sharpe {best} is not positive"
    if float(p) > DEPTH_NULL_P_MAX:
        return False, (f"its null prices the best cell at p {p} > {DEPTH_NULL_P_MAX} "
                       "(the S6-B3206 bar; no breadth-specific bar is ruled)")
    return True, (f"{doc.get('trials')} trials, best IS {best}, null p {p} (the "
                  f"S6-B3206 bar {DEPTH_NULL_P_MAX}; no breadth-specific bar is ruled)")


def _coverage_gaps(cov: dict) -> list[str]:
    out = [f"{p.get('param')}: untested {p.get('untested')}"
           for p in cov.get("params") or [] if p.get("untested")]
    ta = cov.get("table_a") or {}
    out += [f"Table A {a.get('axis')} {a.get('param')}: {a.get('pending')} engine-only "
            "level(s) unwaived" for a in ta.get("pending") or [] if not a.get("waived")]
    out += [f"struck {s.get('param_id')} {s.get('levels')}" for s in ta.get("struck") or []
            if not s.get("waived")]
    out += [str(b) for b in ta.get("blocked") or []]
    return out


def preflight(kind: str, path: str, doc: dict, siblings: list[str],
              *, coverage=None, prior=None) -> dict:
    """Every refusal the reader applies before a holdout row is read, as
    {refusals, clears, disclosures}. `coverage` and `prior` are seams (#241)."""
    import holdout_reads
    import producer_variant_table as pvt
    refusals, clears, disclosures = [], [], []
    why = holdout_reads.step1_uncommitted(path)
    if why:
        refusals.append(why)
        clears.append("commit the Step-1 artifact (the commit is the pre-registration)")
    try:
        holdout_reads.require_multiplicity(doc, path)
    except SystemExit as exc:
        refusals.append(str(exc))
        clears.append("re-run the Step-1 search so its multiplicity block reconciles")
    strategy, leg = subject(kind, doc)
    closed = pvt.offline_retest_refusal(strategy)
    if closed:
        refusals.append(closed)
        clears.append("the owner's override reopening the strategy")
    if kind == "depth":
        if coverage is None:
            import band_coverage_gate as bcg
            try:
                coverage = bcg.coverage_report(strategy, [path] + list(siblings))
            except SystemExit as exc:
                coverage = {"evaluable": False, "reason": str(exc)}
        if not coverage.get("evaluable", False):
            refusals.append(f"band coverage NOT EVALUABLE: {coverage.get('reason')}")
            clears.append("write the strategy's Table A / SPECS entry")
        elif not coverage.get("complete", False):
            gaps = _coverage_gaps(coverage)
            refusals.append(f"band coverage incomplete (S6-B2886 / S6-B3339): {len(gaps)} "
                            "gap(s) - " + "; ".join(gaps))
            clears.append("grade the listed levels, or the owner's waiver of each "
                          "engine-only level in output_audit/producer_level_waivers.json")
        import offline_level_sweep as ols
        loose = ols.looser_levels([dict(a) for a in doc.get("axes") or []],
                                  tuple(doc.get("production_levels") or ()))
        if loose:
            refusals.append("looser level(s): " + "; ".join(loose))
            clears.append("drop the looser levels from the Step-1 surface")
    else:
        if coverage is None:
            import band_coverage_gate as bcg
            try:
                coverage = bcg.coverage_report(strategy, [path])
            except SystemExit as exc:
                coverage = {"evaluable": False, "reason": str(exc)}
        if not coverage.get("complete", False):
            gaps = (_coverage_gaps(coverage) if coverage.get("evaluable")
                    else [str(coverage.get("reason"))])
            disclosures.append(f"band coverage stamped, not refused: {len(gaps)} gap(s) - "
                               + "; ".join(gaps[:8]) + ("; ..." if len(gaps) > 8 else "")
                               + " - a negative read declares no failure (#299)")
    if prior is None:
        prior = [e.get("read_id") for e in holdout_reads.binding_reads(strategy, leg)]
    if prior:
        disclosures.append(f"the ledger records {len(prior)} binding read(s) of "
                           f"{strategy} ({leg}): {prior[:3]} - this read is a "
                           "DISCLOSED-RE-READ")
    return {"refusals": refusals, "clears": clears, "disclosures": disclosures,
            "ready": not refusals}


def build(paths: list[str], *, prior_of=None, coverage_of=None) -> dict:
    """The packet over `paths`. `prior_of(strategy, leg)` -> the ledger's binding
    reads and `coverage_of(strategy, artifact_paths)` -> a coverage report are
    seams (#241); None reads the live ledger and the live gate."""
    docs = []
    for p in paths:
        doc = json.loads((ROOT / p).read_text(encoding="utf-8")
                         if not Path(p).is_absolute() else Path(p).read_text(encoding="utf-8"))
        docs.append((p, doc, classify(doc)))
    rows, skipped = [], []
    for p, doc, kind in docs:
        if kind is None:
            skipped.append(p)
            continue
        ok, why = survivor(kind, doc)
        strat, leg = subject(kind, doc)
        # a depth read counts every other Step-1 artifact of the strategy
        # toward band coverage - any leg, depth or breadth - as its reader's
        # --coverage-artifact allows; MEASURED on S6-B3249's r1_break_retest,
        # its breadth grid takes the untested parameters from 10 to 1
        sib = [q for q, d2, k2 in docs if k2 in ("depth", "breadth") and q != p
               and kind == "depth" and d2.get("strategy") == strat]
        row = {"artifact": p, "kind": kind, "strategy": strat, "leg": leg,
               "survivor": ok, "why": why}
        if ok:
            row.update(preflight(
                kind, p, doc, sib,
                coverage=(coverage_of(strat, [p] + sib) if coverage_of else None),
                prior=(prior_of(strat, leg) if prior_of else None)))
            row["coverage_artifacts"] = sib
        rows.append(row)
    # read order per subject: depth first (one pre-registered line), then
    # breadth; a leg of 'both' overlaps every leg, as the ledger reads it
    order = sorted((r for r in rows if r["survivor"]),
                   key=lambda r: (r["strategy"], 0 if r["kind"] == "depth" else 1))
    seen: dict = {}
    for r in order:
        legs = seen.setdefault(r["strategy"], [])
        overlap = [x for x in legs if x == r["leg"] or "both" in (x, r["leg"])]
        r["read_order"] = ("DISCLOSED-RE-READ - needs the owner's disclosure words"
                           if overlap or any("DISCLOSED-RE-READ" in d
                                             for d in r.get("disclosures", []))
                           else "clean first read")
        legs.append(r["leg"])
    surv = [r for r in rows if r["survivor"]]
    return {"generator": "scripts/holdout_packet.py (S6-B3454)",
            "artifacts": len(paths), "step1_sources": len(rows), "skipped": skipped,
            "survivors": len(surv), "ready": sum(1 for r in surv if r.get("ready")),
            "refused": sum(1 for r in surv if not r.get("ready")),
            "rereads": sum(1 for r in surv if r.get("read_order", "").startswith("DISCLOSED")),
            "rows": rows}


def render(pk: dict) -> str:
    head = (f"# Holdout-read packet (generated by {pk['generator']})\n\n"
            f"{pk['step1_sources']} Step-1 artifacts read ({len(pk['skipped'])} skipped as "
            f"not a read source); {pk['survivors']} survivors - {pk['ready']} ready, "
            f"{pk['refused']} refused before any read, {pk['rereads']} DISCLOSED-RE-READ.\n\n"
            "| # | strategy | leg | reader | survivor | before the read | clears with | "
            "read order |\n|---|---|---|---|---|---|---|---|\n")
    out = []
    for i, r in enumerate(pk["rows"], 1):
        reader = "offline_holdout_read" if r["kind"] == "depth" else "breadth_step2_read"
        if not r["survivor"]:
            out.append(f"| {i} | {r['strategy']} | {r['leg']} | {reader} | no - {r['why']} "
                       "| - | - | - |")
            continue
        pre = ("READY" if r["ready"] else "REFUSED: " + " / ".join(r["refusals"]))
        if r.get("disclosures"):
            pre += " (disclosed: " + " / ".join(r["disclosures"]) + ")"
        out.append(f"| {i} | {r['strategy']} | {r['leg']} | {reader} | yes - {r['why']} | "
                   f"{pre} | {'; '.join(r['clears']) or '-'} | {r['read_order']} |")
    return head + "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="S6-B3454: build a holdout-read packet "
                                 "from Step-1 artifacts and the readers' own refusals; "
                                 "reads no holdout row, records nothing.")
    ap.add_argument("--artifacts", nargs="+", required=True,
                    help="Step-1 artifacts (repo-relative paths or globs)")
    ap.add_argument("--out", default=None, help="write the packet JSON here (and .md)")
    a = ap.parse_args(argv)
    paths = []
    for pat in a.artifacts:
        hits = sorted(glob.glob(str(ROOT / pat))) if any(c in pat for c in "*?[") else [pat]
        for h in hits:
            hp = Path(h)
            paths.append(str(hp.relative_to(ROOT)).replace(chr(92), "/")
                         if hp.is_absolute() else h)
    try:
        pk = build(paths)
    except (OSError, ValueError) as exc:
        print(f"REFUSED (holdout_packet): an artifact could not be read - {exc!r}")
        return 2
    md = render(pk)
    print(md)
    if a.out:
        out = ROOT / a.out
        out.write_bytes(json.dumps(pk, indent=1).encode("utf-8"))
        out.with_suffix(".md").write_bytes(md.encode("utf-8"))
        print(f"wrote {a.out} and {Path(a.out).with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
