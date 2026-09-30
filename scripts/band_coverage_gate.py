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

ARTIFACT KINDS (B3139, S6-B3139a council). Every artifact is CLASSIFIED
before it is read; coverage is taken only from a kind whose fields can say
WHICH level ran. MEASURED on bollinger's campaign: five shapes reach this
gate - axis grids (rows = a list of {axis, level, is_sharpe}), family
grid_auto files (rows = an INT count - 7,392 on span 9 - on which
'for r in rows' raised TypeError inside both Step-2 readers), free-level
grids (a levels dict), companion screens and permutation nulls. The last
four add NO coverage and each is REPORTED with its reason; free-level
evaluations appear as a report column (counting them as coverage would
change which failures can be declared - the owner's, #310); a grid_auto's
landed producer config is reported under landed_configs for the operator
to pass as --resim-evidence by judgement. An UNKNOWN shape refuses with a
named reason - never a crash, never a silent skip. The refusal exits 2 as
documented (a string SystemExit exits 1 - MEASURED - so it never did).
A strategy present in BOTH SPECS_PHASE0 and SPECS is read from PHASE0 (as
before) and every id whose band differs between the two is DISCLOSED under
registry_conflicts - MEASURED: bollinger_lower's P4 reads [200] in PHASE0
and the 8 campaign spans in SPECS; choosing a winner moves coverage
verdicts and is the owner's.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

_TOL = 1e-9
# S6-B3139a (B3139): a boolean axis's band may be written as a STRING label;
# MEASURED 3 rows (bollinger_lower B2 / B4 / B6) - each read UNTESTED with
# 26 graded rows behind it until these labels took the boolean branch.
BOOL_BAND_LABELS = ("require_true", "require_false")


class BandCoverageError(SystemExit):
    """Raised when a Step-2 failure declaration is attempted with untested
    Table A band levels remaining, or an input artifact is of no known kind.
    EXITS 2 as documented (B3139: a string SystemExit exits 1, MEASURED);
    str() stays the message, which both Step-2 readers record as the
    reason (breadth_step2_read.py, offline_holdout_read.py)."""

    def __init__(self, message):
        super().__init__(2)
        self.message = str(message)

    def __str__(self):
        return self.message


KIND_AXIS_GRID = "axis_grid"
KIND_GRID_AUTO = "grid_auto"
KIND_FREE_LEVELS = "free_levels"
KIND_COMPANION_SCREEN = "companion_screen"
KIND_PERMUTATION_NULL = "permutation_null"
KIND_IS_SURFACE = "is_surface"
ZERO_COVERAGE = {
    KIND_GRID_AUTO: "rows is a COUNT - it cannot say which levels ran; the "
                    "landed producer config is reported under landed_configs",
    KIND_FREE_LEVELS: "evaluations are REPORTED under free_level_evaluations; "
                      "counting them as coverage is the owner's (#310)",
    KIND_COMPANION_SCREEN: "a screen of candidate companions grades no band level",
    KIND_PERMUTATION_NULL: "a null distribution grades no band level",
    # B3139 (found by test_b2886 on the pead family): an in-sample search
    # surface reports; whether it may COUNT toward band coverage is the
    # S6-B3139o policy question, so until that ruling it never counts.
    KIND_IS_SURFACE: "an in-sample search surface - reported, never counted "
                     "toward coverage pending the S6-B3139o ruling",
}


def artifact_kind(doc):
    """The declared kind of one artifact, or None when its shape is none of
    the known kinds (the caller REFUSES by name). Order matters: a list of
    row dicts is an axis grid even when the file also carries 'levels'."""
    if not isinstance(doc, dict):
        return None
    rows = doc.get("rows")
    if isinstance(rows, list):
        return KIND_AXIS_GRID if all(isinstance(r, dict) for r in rows) else None
    if rows is None and ("discarded_levels" in doc or "resim_configs" in doc):
        return KIND_AXIS_GRID
    if isinstance(rows, int) and not isinstance(rows, bool) and "results" in doc:
        return KIND_GRID_AUTO
    if isinstance(doc.get("levels"), dict) and "grade_free_levels" in str(
            doc.get("grader") or ""):
        return KIND_FREE_LEVELS
    if (isinstance(doc.get("results"), list) and "fdr_threshold" in doc
            and "survivors" in doc):
        return KIND_COMPANION_SCREEN
    if "n_perms" in doc and "legs" in doc:
        return KIND_PERMUTATION_NULL
    if "cells_graded" in doc and "axes" in doc and "ranked" in doc:
        return KIND_IS_SURFACE
    return None


def _registry_conflicts(strategy: str) -> dict:
    """{id: {'phase0': band, 'specs': band}} for every param id whose band
    differs between SPECS_PHASE0 and SPECS (both registries hold the
    strategy); {} otherwise. Disclosed, never resolved here."""
    try:
        from producer_variant_table import SPECS_PHASE0, SPECS
    except ImportError:  # pragma: no cover
        return {}
    a, b = SPECS_PHASE0.get(strategy), SPECS.get(strategy)
    if not a or not b:
        return {}
    pa = {r.get("id"): r.get("band") for r in a.get("params", [])}
    pb = {r.get("id"): r.get("band") for r in b.get("params", [])}
    return {i: {"phase0": pa.get(i), "specs": pb.get(i)}
            for i in sorted(set(pa) | set(pb), key=str)
            if pa.get(i) != pb.get(i)}


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
        names = [Path(p).name for p in artifact_paths]
        arts = [json.loads(Path(p).read_text(encoding="utf-8"))
                for p in artifact_paths]
    else:
        names = [f"arts[{i}]" for i in range(len(arts))]
    # S6-B3139a (B3139): classify first; an unknown shape refuses by name
    kinds = [artifact_kind(a) for a in arts]
    unknown = [n for n, k in zip(names, kinds) if k is None]
    if unknown:
        raise BandCoverageError(
            f"REFUSED (S6-B3139a): {len(unknown)} artifact(s) of no known "
            f"kind - {unknown}; the gate reads coverage only from a declared "
            f"kind ({sorted([KIND_AXIS_GRID] + list(ZERO_COVERAGE))}) and "
            "never guesses at an unfamiliar shape")
    artifacts = [{"artifact": n, "kind": k,
                  "coverage": ("counted" if k == KIND_AXIS_GRID
                               else "none - " + ZERO_COVERAGE[k])}
                 for n, k in zip(names, kinds)]
    free_evals = {}
    landed = []
    for n, k, a in zip(names, kinds, arts):
        if k == KIND_FREE_LEVELS:
            ev = free_evals.setdefault(str(a.get("axis") or "unnamed axis"), [])
            ev.append({"artifact": n,
                       "levels": list(a.get("levels_searched")
                                     or list((a.get("levels") or {}).keys())),
                       "extra_evaluations": sorted(
                           x for x in ("p11_tight", "p8_tight") if a.get(x))})
        elif k == KIND_GRID_AUTO and isinstance(a.get("config"), dict):
            landed.append({"artifact": n, "config": a["config"]})
    graded, structural, discarded, resim = _gather(
        [a for a, k in zip(arts, kinds) if k == KIND_AXIS_GRID])
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
                if isinstance(lev, bool) or lev in BOOL_BAND_LABELS:
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
            "artifacts": artifacts,
            "free_level_evaluations": free_evals,
            "landed_configs": landed,
            "registry_conflicts": (_registry_conflicts(strategy)
                                   if spec is None else {}),
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
    try:
        if a.declare_step2_failure:
            rep = declare_step2_failure(a.strategy, a.artifacts,
                                        resim_evidence=ev)
            print("COVERAGE COMPLETE - failure declaration permitted")
        else:
            rep = coverage_report(a.strategy, a.artifacts, resim_evidence=ev)
    except BandCoverageError as exc:
        # the documented exit 2 (S6-B3139a): the message first, then 2
        print(exc.message, file=sys.stderr)
        return 2
    print(json.dumps(rep, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
