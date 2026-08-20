#!/usr/bin/env python
"""B1761: sweep EVERY gate for whether it fires on the words that motivated it.

B1760 checked 8 gates against a hand-built corpus and found 3 silent. The owner
asked for the retroactive sweep the fix implies: **all** gates, and the two
distinct questions kept apart --

  Q1  Does the gate have a recorded incident at all?     (corpus coverage)
  Q2  Given its incident, does the gate fire on it?      (gate correctness)

There is a THIRD question that B1760 did not ask and that turns out to matter
more than either:

  Q3  Can the gate be ASKED?  A gate with no injectable text parameter reads
      the live transcript and nothing else, so it can never be exercised
      against a fixed string. Its pin test can only ever assert
      `gate([]) == []` - which passes for a gate that is wired to nothing.

Q3 is the structural version of the B1760 defect. `scan_uninspected_constant`
HAD a `text=` parameter and ignored it in two places; a gate with no parameter
at all has the same untestability without even the appearance of a seam.

HAND-RUN: python scripts/sweep_gate_incidents.py
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import verify_turn_compliance as tg  # noqa: E402
from gate_incident_corpus import INCIDENTS  # noqa: E402

# Gates whose subject is a STATE of the repo (dirty tree, missing stamp,
# unpushed commits), not a sentence in the response. Text injection is
# meaningless for these - they are legitimately state-gates, and their
# incidents are reproduced by fixtures rather than strings.
STATE_GATES = {
    "check_dirty_tree",
    "check_pyramid_stamp",
    "check_queue_entry",
    "check_compliance_marker",
    "check_unpushed",
    "check_stop_exempt",
}


def gates() -> list[tuple[str, object]]:
    out = []
    for name, fn in vars(tg).items():
        if not callable(fn) or not hasattr(fn, "__code__"):
            continue
        if name.startswith(("scan_", "check_")) and fn.__module__ == tg.__name__:
            out.append((name, fn))
    return sorted(out)


def accepts_text(fn) -> bool:
    try:
        return "text" in inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False


def fires(name, fn, text: str, state: dict | None = None) -> bool | None:
    """Return True/False, or None if the gate could not be invoked.

    B1761: the STATE comes from the corpus entry, not from harness guesses.
    Guessed neutral values made three correct gates look silent - a harness
    that starves a hybrid gate manufactures a false failure just as surely as
    a circular probe manufactures a false pass.
    """
    params = inspect.signature(fn).parameters
    kw = {"text": text}
    for extra, val in (state or {}).items():
        if extra in params:
            kw[extra] = val
    try:
        return bool(fn([], **kw))
    except Exception as exc:  # noqa: BLE001
        print(f"      ! {name} raised: {type(exc).__name__}: {exc}")
        return None


def main() -> int:
    rows = gates()
    no_seam, no_incident, silent, ok, errored = [], [], [], [], []

    print(f"{len(rows)} gate functions found\n")
    print(f"{'GATE':<38} {'SEAM':<6} {'INCIDENT':<10} RESULT")
    print("-" * 78)

    for name, fn in rows:
        if name in STATE_GATES:
            print(f"{name:<38} {'state':<6} {'n/a':<10} STATE-GATE (fixture, not text)")
            continue
        seam = accepts_text(fn)
        has_inc = name in INCIDENTS
        if not seam:
            no_seam.append(name)
            print(f"{name:<38} {'NO':<6} {'yes' if has_inc else 'NO':<10} CANNOT-BE-ASKED")
            continue
        if not has_inc:
            no_incident.append(name)
            print(f"{name:<38} {'yes':<6} {'NO':<10} NO RECORDED INCIDENT")
            continue
        got = fires(name, fn, INCIDENTS[name][0], INCIDENTS[name][2])
        if got is None:
            errored.append(name)
            print(f"{name:<38} {'yes':<6} {'yes':<10} ERROR")
        elif got:
            ok.append(name)
            print(f"{name:<38} {'yes':<6} {'yes':<10} FIRES")
        else:
            silent.append(name)
            print(f"{name:<38} {'yes':<6} {'yes':<10} *** SILENT ON ITS OWN INCIDENT")

    # The negative control is a bare sentence, so gates that legitimately
    # require RESPONSE STRUCTURE (a SKILLS block, a compliance block) will
    # demand it. Those are excluded by name, with the reason recorded.
    STRUCTURE_GATES = {"scan_missing_skill_confirmation", "scan_skill_block_incomplete",
                       "scan_compliance_is_content"}
    neg = INCIDENTS["_negative_control"][0]
    tripped = [n for n, f in rows
               if n not in STATE_GATES and n not in STRUCTURE_GATES
               and accepts_text(f) and fires(n, f, neg, {})]

    print("\n" + "=" * 78)
    print(f"  FIRES on own incident ......... {len(ok)}")
    print(f"  SILENT on own incident ........ {len(silent)}  {silent}")
    print(f"  ERRORED ....................... {len(errored)}  {errored}")
    print(f"  NO recorded incident .......... {len(no_incident)}")
    print(f"  CANNOT BE ASKED (no seam) ..... {len(no_seam)}")
    print(f"  negative control tripped ...... {len(tripped)}  {tripped}")
    print("=" * 78)

    if no_incident:
        print("\nNO RECORDED INCIDENT (gate exists; the words that caused it were never kept):")
        for n in no_incident:
            print(f"  - {n}")
    if no_seam:
        print("\nCANNOT BE ASKED (no `text=` parameter; testable only as gate([])==[]):")
        for n in no_seam:
            print(f"  - {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
