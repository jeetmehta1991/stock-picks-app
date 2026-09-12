#!/usr/bin/env python
"""B2713 (LLM-council verdict, owner-directed 2026-09-12): THE RULED PHASE
TABLE, PARSED - so a campaign's window and universe stop being typeable.

All five council advisors converged on one change: the numbers that decide a
step's scope live as prose in a 3,400-line runbook, are retrieved in
competition with 787 lessons that carry equal apparent authority, and are
re-derived at the point of use. Five of seven owner-caught misses in one
session were that act. The fix is not another refusal - it is deleting the
authoring surface: the launcher RESOLVES window and universe from the
runbook's own phase table, and a spec that declares `step` may not carry
them at all.

SOURCE OF TRUTH stays the runbook (CLAUDE.md's CSV-first rule: a table is
data living in prose). This module PARSES it - never a hand-copied JSON -
and stamps a content hash of the parsed block, so a table edit is visible
to every artifact that ran under it.

Usage:
  python scripts/phase_table.py                 # print the parsed table
  python scripts/phase_table.py --step 1        # print one resolved row
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "STRATEGY_OPTIMISATION_PLAN.md"

# The IS/HO boundary is a PROGRAMME invariant (roster_core's 2025-05-05), not
# a per-step choice: a Step-1 search whose window reaches past it ranks on
# holdout data. Kept here so the resolver can refuse that independently of
# whatever the table says.
IS_HO_BOUNDARY = "2025-05-05"

_ROW = re.compile(
    r"^\|\s*\*{0,2}(?P<step>\d)\s+(?P<name>[A-Z]+)\*{0,2}\s*\|"
    r"(?P<scope>[^|]*)\|(?P<window>[^|]*)\|(?P<universe>[^|]*)\|"
    r"(?P<produces>[^|]*)\|", re.M)
_DATES = re.compile(r"(\d{4}-\d{2}-\d{2})")
_YEARS = re.compile(r"(\d+)\s*year")
_INT = re.compile(r"(\d{2,4})")


def _clean(cell: str) -> str:
    """Strip markdown emphasis from a table cell. Parentheticals are
    KEPT here (they carry the ruling lineage a reader needs) and removed
    only by _values() before numbers are extracted."""
    s = cell.replace("**", "").replace("`", "").strip()
    return re.sub(r"\s+", " ", s)


def _values(cell: str) -> str:
    """The cell with parenthetical rulings dropped, for NUMBER reading.

    B2713b: the first version extracted ints from the raw cell and took
    max(), so step 2's "ALL 544 (owner 2026-08-29; was 344 disjoint)"
    resolved to universe 2026 - a YEAR inside a parenthetical ruling
    beating the real count. The L597 class (an enumeration pattern
    encodes the examples in front of it: every Step-1 cell is a bare
    number) and L733 (the docstring claimed to strip parentheticals and
    did not). Caught by this module's own pin refusing step 2."""
    return re.sub(r"\([^)]*\)", " ", cell)


def parse(runbook: Path | None = None) -> dict:
    """The phase table as data. Injectable path for tests (#241)."""
    path = Path(runbook) if runbook else RUNBOOK
    text = path.read_text(encoding="utf-8", errors="replace")
    rows: dict[str, dict] = {}
    block: list[str] = []
    for m in _ROW.finditer(text):
        win_raw, uni_raw = _clean(m.group("window")), _clean(m.group("universe"))
        win_v, uni_v = _values(win_raw), _values(uni_raw)
        dates = _DATES.findall(win_v)
        years = _YEARS.search(win_v)
        ints = [int(x) for x in _INT.findall(uni_v)]
        rows[m.group("step")] = {
            "step": int(m.group("step")),
            "name": m.group("name"),
            "scope": _clean(m.group("scope")),
            "window_raw": win_raw,
            "window_start": dates[0] if len(dates) >= 2 else None,
            "window_end": dates[1] if len(dates) >= 2 else None,
            "window_years": int(years.group(1)) if years else None,
            "universe_raw": uni_raw,
            "universe_n": max(ints) if ints else None,
            "produces": _clean(m.group("produces")),
        }
        block.append(m.group(0))
    if not rows:
        raise SystemExit(f"REFUSED: no phase-table rows parsed from {path} - "
                         "the table's shape changed; fix the parser rather "
                         "than typing the numbers (B2713)")
    return {"rows": rows,
            "source": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            "source_sha256": hashlib.sha256(
                "\n".join(block).encode("utf-8")).hexdigest()[:16],
            "is_ho_boundary": IS_HO_BOUNDARY}


# The Step-1 row states "1 year, 2024-05..2025-05" - a MONTH-precision window,
# so the day-precision bounds come from the boundary invariant plus that
# year count. Any step whose row carries explicit dates uses them verbatim.
def resolve(step: int, runbook: Path | None = None) -> dict:
    """The ruled window + universe for `step`. Fails CLOSED (L642) on a row
    that cannot be resolved rather than guessing a bound."""
    tbl = parse(runbook)
    row = tbl["rows"].get(str(step))
    if row is None:
        raise SystemExit(f"REFUSED: no phase-table row for step {step}")
    start, end = row["window_start"], row["window_end"]
    if not (start and end):
        yrs = row["window_years"]
        if not yrs:
            raise SystemExit(
                f"REFUSED: step {step} row window {row['window_raw']!r} carries "
                "neither explicit dates nor a year count - cannot resolve "
                "(fix the table or the parser, do not type a window)")
        end = IS_HO_BOUNDARY if step == 1 else row["window_end"] or IS_HO_BOUNDARY
        y, m, d = (int(x) for x in end.split("-"))
        start = f"{y - yrs:04d}-{m:02d}-{d:02d}"
    if step == 1 and end > IS_HO_BOUNDARY:
        raise SystemExit(
            f"REFUSED: resolved Step-1 window ends {end}, past the IS/HO "
            f"boundary {IS_HO_BOUNDARY} - a search on holdout data spends the "
            "family's pre-registration (B2711/B2713)")
    n = row["universe_n"]
    # Registered universes, each named by the runbook: Step-1 sweep sets
    # (APPENDIX S1-200) and the Step-2/3 full R5 baseline (line 1401 -
    # NOT r5_universe_381.txt, the abandoned alphabetical chunk, L445).
    tickers_file = {200: "output_audit/_sweep_200.txt",
                    100: "output_audit/_sweep_100.txt",
                    544: "output_audit/r5_universe_544.txt"}.get(n)
    if tickers_file is None:
        raise SystemExit(
            f"REFUSED: step {step} universe {row['universe_raw']!r} has no "
            "registered ticker file - register it rather than typing a path")
    return {"step": step, "window": {"start": start, "end": end},
            "tickers_file": tickers_file, "universe_n": n,
            "produces": row["produces"], "scope": row["scope"],
            "phase_table_sha256": tbl["source_sha256"],
            "resolved_from": tbl["source"]}


# Keys a step-declaring spec may NOT carry: the resolver owns them.
RESOLVER_OWNED = ("window", "tickers_file", "universe", "start", "end")

LEGACY_REGISTER = ROOT / "output_audit" / "_legacy_typed_specs.json"


def spec_identity(doc: dict) -> frozenset:
    """B2717: the EXACT names a doc could carry in the register.

    The first version matched substrings - `src + "_spec.json" in n`
    and `n.startswith(src)` - so a one-character wave name ("t") hit
    "b2709_smc_sw10_pilot_spec.json", because that name CONTAINS
    "t_spec.json", and the spec grandfathered ITSELF out of the rule.
    A loose ESCAPE is the dangerous direction: it lets work through in
    silence (L596). Exact candidates only, basename-normalised."""
    src = str(doc.get("_spec_path") or doc.get("wave") or "")
    if not src:
        return frozenset()
    base = src.replace("\\", "/").rsplit("/", 1)[-1]
    return frozenset({base, base + "_spec.json", base + ".json"})


def legacy_typed_specs() -> frozenset:
    """B2714 (the B2450 disposal plan): spec files that predate the
    typed-scope rule, grandfathered BY NAME and shrink-only. A no-step
    spec cannot be judged - nothing in it says which step's row to
    compare - so the rule binds NEW specs, and these 66 keep working
    until each is rewritten in pointer form. Missing register = empty
    set, i.e. the rule applies to everything (fail CLOSED, L642)."""
    try:
        return frozenset(json.loads(
            LEGACY_REGISTER.read_text(encoding="utf-8"))["names"])
    except (OSError, KeyError, ValueError):
        return frozenset()


def spec_refusals(doc: dict) -> list[str]:
    """B2713: the authoring-surface deletion, enforced.

    A spec declaring `step` must NOT type the resolver-owned fields. A spec
    typing them without a `step` is a legacy/hand-authored shape and needs a
    waiver quoting the owner - the same fail-closed posture as B2711, one
    level earlier: there the value was checked, here it cannot be written.
    """
    errs: list[str] = []
    # B2714c: a GENERATED manifest is not an authoring surface - its
    # source spec was judged before it existed (run_wave.build_manifest
    # stamps _derived_from_spec).
    if doc.get("_derived_from_spec"):
        return []
    # B2714: a grandfathered spec (named in the register) is exempt -
    # the disposal plan for this rule's own backlog.
    if spec_identity(doc) & legacy_typed_specs():
        return []
    typed = [k for k in RESOLVER_OWNED if k in doc]
    waiver = doc.get("step1_shape_waiver") or doc.get("shape_waiver")
    has_waiver = isinstance(waiver, str) and len(waiver.strip()) >= 20
    if "step" in doc:
        if typed:
            errs.append(
                f"spec declares step {doc['step']} AND types {typed} - the "
                "phase table owns those fields (B2713); delete them and let "
                "phase_table.resolve inject the ruled values")
    elif typed and not has_waiver:
        errs.append(
            f"spec types {typed} and declares no `step` - a campaign spec "
            "names its step and lets the ruled window/universe resolve "
            "(B2713); typing them needs a waiver quoting the owner")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=int, default=None)
    a = ap.parse_args()
    out = resolve(a.step) if a.step else parse()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
