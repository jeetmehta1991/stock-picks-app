#!/usr/bin/env python
"""S6-B3393 (B3139q-r193, runbook section 11.1 / census 634): the on-ramp
probe - every R1-R9 check of the runbook's R-table, run through the same
functions the launch gate uses, each printing its expected line or the reason
it fails. make_spec runs it before it writes an engine spec (a --dry draft
prints the lines; a real run refuses on any FAIL), so the R-table is no
longer a list the operator must remember to run by hand.

  R1  validate_spec on the entry the R1 probe reads (SPECS first) -> SPEC OK
  R2  a D_AXIS_FAMILIES family SERVES the strategy (the map is keyed
      by family, so `'<strategy>' in D` is False for a served
      strategy whose family is named otherwise)                    -> True
  R3  run_postconfig.family_refusal is '' - its runner executes
      every _GRADER_CHECKS leg; a free-levels gap is refused by
      validate_spec under R1 (S6-B3385)                            -> ''
  R4  tools.grade's script exists and parses arguments            -> usage text
  R5  tools.free_levels' script, where declared                   -> usage text
  R6  tools.spot_check's script                                   -> usage text
  R7  tools.engine_anchors' script exists where one is declared
      (None or no key: battery step 7 relies on R8's knob reads)   -> every token found
  R8  every env knob is read and its consumer list matches          -> True
  R9  the precompute per scheduled level - CHECKED AT LAUNCH
      (launch_refusals), since the levels exist only once a spec
      names them                                                   -> one dir per level

R4-R6's "usage text" is checked as PARSER PRESENCE - the script constructs an
argparse.ArgumentParser - never by running --help (#327: a script without a
parser can run its main on any argument)."""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _has_parser(script: Path) -> bool:
    try:
        tree = ast.parse(script.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError):
        return False
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if name == "ArgumentParser":
                return True
    return False


def _script_row(rid: str, tools: dict, section: str, optional: bool = False) -> tuple:
    blk = tools.get(section) or {}
    script = blk.get("script") if isinstance(blk, dict) else None
    if not script:
        if optional:
            return (rid, True, f"no tools.{section} declared (optional here)")
        return (rid, False, f"tools.{section} names no script")
    p = SCRIPTS / str(script)
    if not p.is_file():
        return (rid, False, f"tools.{section}.script {script} does not exist under scripts/")
    if not _has_parser(p):
        return (rid, False, f"{script} builds no argparse parser - no usage text")
    return (rid, True, f"usage text ({script} parses its arguments)")


def _guard(rid: str, fn) -> tuple:
    """One R's row, or a FAIL naming the exception: the probe never raises into
    its caller - make_spec runs it on a --dry draft of any entry, and an entry
    that crashes a check is an entry that fails it (fail CLOSED, L642)."""
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001 - reported as the R's FAIL line
        return (rid, False, f"raised {type(exc).__name__}: {exc}")


def probe(strategy: str, root: Path = ROOT) -> list[tuple]:
    """[(R-id, ok, line)] for R1-R9; R9 is reported, checked at launch."""
    from producer_variant_table import (SPECS, SPECS_PHASE0, D_AXIS_FAMILIES,
                                        validate_spec, declared_consumers,
                                        knob_consumers, knob_is_read)
    from run_postconfig import family_refusal
    spec = SPECS.get(strategy) or SPECS_PHASE0.get(strategy)
    if spec is None:
        return [("R1", False, f"{strategy!r} has no SPECS/SPECS_PHASE0 entry")]

    def r1():
        errs = validate_spec(spec)
        return ("R1", not errs, "SPEC OK" if not errs else f"{len(errs)} error(s): {errs[:2]}")

    def r2():
        served = any(strategy in fam.get("serves", ()) for fam in D_AXIS_FAMILIES.values())
        return ("R2", served, "True" if served else "False - no D_AXIS_FAMILIES family serves it")

    def r3():
        why = family_refusal(strategy)
        return ("R3", not why, "''" if not why else why)

    tools = (SPECS.get(strategy) or {}).get("tools") or {}

    def r7():
        anchor = (tools.get("engine_anchors") or {}).get("script")
        if not anchor:
            return ("R7", True, "no anchor script declared - step 7 relies on R8's knob reads")
        ok7 = (SCRIPTS / str(anchor)).is_file()
        return ("R7", ok7, f"{anchor} present - battery step 7 runs it" if ok7
                else f"engine_anchors script {anchor} does not exist")

    def r8():
        knobs = [p["env"] for p in spec["params"] if p.get("env")]
        bad = [k for k in knobs if not (knob_is_read(k, root)
                                        and declared_consumers(spec, k) == knob_consumers(k))]
        return ("R8", not bad, "True" if not bad else f"knobs unread or drifted: {bad}")

    rows = [_guard("R1", r1), _guard("R2", r2)]
    row3 = _guard("R3", r3)
    rows.append(row3)
    if not row3[1]:
        rows += [(r, False, "the family refuses (R3)") for r in ("R4", "R5", "R6", "R7")]
    else:
        rows.append(_guard("R4", lambda: _script_row("R4", tools, "grade")))
        rows.append(_guard("R5", lambda: _script_row("R5", tools, "free_levels", optional=True)))
        rows.append(_guard("R6", lambda: _script_row("R6", tools, "spot_check")))
        rows.append(_guard("R7", r7))
    rows.append(_guard("R8", r8))
    rows.append(("R9", True, "checked at launch - launch_refusals reads each arm's "
                             "precompute dir once a spec names the levels"))
    return rows


def failures(strategy: str) -> list[str]:
    return [f"{rid}: {line}" for rid, ok, line in probe(strategy) if not ok]


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the runbook R1-R9 on-ramp probes for one strategy")
    ap.add_argument("--strategy", required=True)
    a = ap.parse_args()
    rows = probe(a.strategy)
    for rid, ok, line in rows:
        print(f"{rid} {'PASS' if ok else 'FAIL'}: {line}")
    bad = [r for r in rows if not r[1]]
    print(f"onramp: {len(rows) - len(bad)} of {len(rows)} pass for {a.strategy}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
