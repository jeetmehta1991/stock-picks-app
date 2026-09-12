#!/usr/bin/env python
"""B2704 (owner-mandated 2026-09-12, verbatim): "Each and every band once
approved in table A needs to be tested before a strategy can be declared as
a failure in step 2. Bands can be discarded in step 1 as per our methodology
thats allowed as testing."

THE MECHANICAL CHECK behind CHECKLIST #299's declare-failure path. Coverage
is derived from the CAMPAIGN ARTIFACTS, never from Table A "status" fields
(a status inside a record decays - L639); "tested" for a band level means
any of:
  - it is the PRODUCTION value (the baseline line is graded by construction);
  - a Step-1 row graded it (axis rows for breadth/threshold params; depth
    cell tags for structural params like leg / confirmation_arm);
  - a Step-1 artifact records it in "discarded_levels" {param: [levels]}
    (discard-in-Step-1 counts as testing, per the ruling);
  - engine resim evidence names it ("resim_configs" in an artifact, or the
    --resim-evidence JSON of {param: [values]} - e.g. a landed config
    identity like breaker's P1_swing_length 50).
Quantile-labelled bands (["q20","q40","q60","q80"]) are covered when at
least that many DISTINCT levels of the axis were graded (levels resolve at
grid time, so labels cannot be matched literally).

FAIL-CLOSED: a strategy present only in the SPECS adapter schema (no
band-inventoried "params" list) cannot be declared a Step-2 failure through
this gate - the Table A inventory is a precondition, not an option.

Wired: breadth_step2_read.py stamps coverage_report() into every Step-2
artifact unconditionally; the CLI --declare-step2-failure exits 2 on any
untested level; pinned by test_b2704_* (must-fire on the REAL hub-1
artifacts, must-quiet + discard arms on labelled SYNTHETIC fixtures).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

_TOL = 1e-9


class BandCoverageError(SystemExit):
    """Raised (exit 2) when a Step-2 failure declaration is attempted with
    untested Table A band levels remaining."""


def _load_spec(strategy: str, spec: dict | None):
    if spec is not None:
        return spec
    from producer_variant_table import SPECS_PHASE0
    try:
        from producer_variant_table import SPECS
    except ImportError:  # pragma: no cover - SPECS always exists today
        SPECS = {}
    entry = SPECS_PHASE0.get(strategy) or SPECS.get(strategy)
    if not entry:
        raise SystemExit(f"REFUSED: no Table A spec for {strategy!r}")
    return entry


def _gather(arts: list) -> tuple[dict, dict, dict, dict]:
    """(graded axis levels, structural values seen, discarded, resim) from
    the artifacts' own rows and fields."""
    graded: dict[str, set] = {}
    structural: dict[str, set] = {"leg": set(), "confirmation_arm": set()}
    discarded: dict[str, set] = {}
    resim: dict[str, set] = {}
    for a in arts:
        for r in a.get("rows", []):
            if r.get("is_sharpe") is None:
                continue  # a SKIP row is NOT coverage (the L783 incident)
            if r.get("axis"):
                graded.setdefault(r["axis"], set()).add(r["level"])
            tag = r.get("cell", "")
            if tag.startswith("depth:"):
                leg, arm = tag.split(":", 1)[1].split("/")
                structural["leg"].add(leg)
                structural["confirmation_arm"].add(arm)
        for p, levs in (a.get("discarded_levels") or {}).items():
            discarded.setdefault(p, set()).update(levs)
        for cfg in a.get("resim_configs") or []:
            for p, v in cfg.items():
                resim.setdefault(p, set()).add(v)
    return graded, structural, discarded, resim


def _num_eq(a, b) -> bool:
    try:
        return abs(float(a) - float(b)) <= _TOL
    except (TypeError, ValueError):
        return str(a) == str(b)


def coverage_report(strategy: str, artifact_paths: list, *,
                    spec: dict | None = None, arts: list | None = None,
                    resim_evidence: dict | None = None) -> dict:
    """Per-param tested/untested split for every Table A band level.
    `spec` and `arts` are injection seams (#241); production callers pass
    paths and let the spec come from producer_variant_table."""
    entry = _load_spec(strategy, spec)
    if "params" not in entry:
        return {"strategy": strategy, "complete": False, "evaluable": False,
                "reason": "spec has no band-inventoried 'params' list (SPECS "
                          "adapter schema) - Table A inventory is a "
                          "precondition for any failure declaration",
                "params": []}
    if arts is None:
        arts = [json.loads(Path(p).read_text(encoding="utf-8"))
                for p in artifact_paths]
    graded, structural, discarded, resim = _gather(arts)
    for p, vals in (resim_evidence or {}).items():
        resim.setdefault(p, set()).update(vals)

    out, untested_total = [], 0
    for p in entry["params"]:
        name, band, prod = p["param"], p["band"], p["production"]
        q_labels = [b for b in band if isinstance(b, str) and b.startswith("q")]
        tested, untested = [], []
        if q_labels:
            got = len(graded.get(name, set()))
            if got >= len(q_labels):
                tested = list(band)
            else:
                tested = [f"{got} distinct graded levels"]
                untested = [f"needs >= {len(q_labels)} distinct levels "
                            f"({len(q_labels)} quantile labels), got {got}"]
        else:
            seen = graded.get(name, set()) | discarded.get(name, set()) \
                   | resim.get(name, set()) | structural.get(name, set())
            for lev in band:
                if isinstance(lev, bool):
                    # a boolean axis has ONE tested state per band entry and
                    # its graded level may carry a leg qualifier ("True(long)")
                    # - any graded row of the axis covers it
                    ok = bool(graded.get(name))
                else:
                    ok = (_num_eq(lev, prod)
                          or any(_num_eq(lev, s) for s in seen))
                (tested if ok else untested).append(lev)
        untested_total += len(untested)
        out.append({"id": p["id"], "param": name, "band": band,
                    "production": prod, "tested": tested,
                    "untested": untested})
    return {"strategy": strategy, "evaluable": True,
            "complete": untested_total == 0,
            "untested_total": untested_total, "params": out,
            "rule": "owner ruling 2026-09-12 verbatim: every approved Table A "
                    "band tested before a Step-2 failure declaration; "
                    "Step-1 discards count as testing"}


def declare_step2_failure(strategy: str, artifact_paths: list, **kw) -> dict:
    """Fail-closed: returns the report only when coverage is COMPLETE;
    otherwise raises BandCoverageError naming every untested level."""
    rep = coverage_report(strategy, artifact_paths, **kw)
    if not rep.get("evaluable", True):
        raise BandCoverageError(
            f"FAILURE DECLARATION REFUSED (#299): {rep['reason']}")
    if not rep["complete"]:
        missing = "; ".join(
            f"{p['id']} {p['param']}: untested {p['untested']}"
            for p in rep["params"] if p["untested"])
        raise BandCoverageError(
            "FAILURE DECLARATION REFUSED (CHECKLIST #299 / B2704): "
            f"{rep['untested_total']} untested Table A band level(s) remain - "
            f"{missing}. Test them (engine resim if offline cannot reach "
            "them) or obtain an explicit owner waiver; until then the "
            "disposition is 'leg negative; depth leg NOT RUN', never "
            "'strategy failed'.")
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--artifacts", nargs="+", required=True)
    ap.add_argument("--resim-evidence", default=None,
                    help="JSON file {param: [values]} of engine-landed levels")
    ap.add_argument("--declare-step2-failure", action="store_true")
    a = ap.parse_args()
    ev = (json.loads(Path(a.resim_evidence).read_text(encoding="utf-8"))
          if a.resim_evidence else None)
    if a.declare_step2_failure:
        rep = declare_step2_failure(a.strategy, a.artifacts, resim_evidence=ev)
        print("COVERAGE COMPLETE - failure declaration permitted")
    else:
        rep = coverage_report(a.strategy, a.artifacts, resim_evidence=ev)
    print(json.dumps(rep, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
