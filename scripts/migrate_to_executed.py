#!/usr/bin/env python
"""B1784: SIX mutually exclusive classes. DONE becomes EXECUTED.

OWNER RULING 2026-08-20:
    "Lets use those 6 classes itself. In the 6 classes, replace DONE with
     EXECUTED. I doubt the result of 'done self-reported, NOT verified - no
     longer terminal'. Done will be moved to EXECUTED after verifying each
     ticket comprehensively. All CLOSED tickets will be under EXECUTED. I want
     MUTUALLY EXCLUSIVE groups. You can not say 7 groups while combining the
     groups of two different sets when they are not mutually exclusive."

The criticism is exact. B1769 ruled six classes; B1778 added CLOSED as a
seventh without retiring DONE, so the ledger carried TWO terminal-ish states
whose meanings overlapped - and I reported their union as a taxonomy. That is
not a classification, it is two half-migrations presented as one.

THE SIX, mutually exclusive and collectively exhaustive:

    EXECUTED   verified against code and the change log        (terminal)
    DROPPED    deliberately not doing                          (terminal)
    BLOCKED    cannot proceed                                  (non-terminal)
    DEFERRED   could proceed, chose not to                     (non-terminal)
    OPEN       queued, unstarted, or UNVERIFIED                (non-terminal)
    RUNNING    in flight                                       (non-terminal)

THE MAPPING:
    CLOSED -> EXECUTED   already code-verified; the owner's word replaces mine
    DONE   -> OPEN       self-reported and unverified. Under the ruling there is
                         no resting place for "finished but unchecked": a row is
                         either verified (EXECUTED) or it is still work (OPEN).
                         Each carries a reason naming what verification it awaits.

**The OPEN count rises sharply and that is the ruling working.** A row that was
never checked was never finished; calling the rise a regression would be the
same category-to-claim error that produced "271 closed".

HAND-RUN:  python scripts/migrate_to_executed.py [--write]
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "EXECUTION_QUEUE.md"

CLASSES = ("EXECUTED", "DROPPED", "BLOCKED", "DEFERRED", "OPEN", "RUNNING")

ROW = re.compile(
    r"^(\|\s*\*\*(S6-[A-Za-z0-9-]+)\*\*\s*\|\s*\*\*)([A-Z-]+)(\*\*\s*\|\s*)(\S*)(\s*\|)(.*)$")

UNVERIFIED_REASON = (
    " _reason:_ self-reported and never verified against code or the change "
    "log. Under the B1784 ruling a row is either EXECUTED (verified) or still "
    "work - there is no 'finished but unchecked' state. Needs comprehensive "
    "verification before it may become EXECUTED.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    lines = QUEUE.read_text(encoding="utf-8").splitlines()
    last: dict[str, int] = {}
    for i, line in enumerate(lines):
        m = ROW.match(line)
        if m:
            last[m.group(2)] = i

    out, moved = [], collections.Counter()
    for i, line in enumerate(lines):
        m = ROW.match(line)
        if not m:
            out.append(line)
            continue
        tid, cls, tail = m.group(2), m.group(3), m.group(7)
        # every ROW is rewritten so no stale class survives anywhere in the
        # file, not only on the latest row per ticket - a reader scrolling the
        # ledger must never meet a retired word.
        if cls == "CLOSED":
            new, extra = "EXECUTED", ""
        elif cls == "DONE":
            new = "OPEN"
            extra = UNVERIFIED_REASON if last.get(tid) == i else ""
        else:
            new, extra = cls, ""
        if new != cls:
            moved[f"{cls} -> {new}"] += 1
        out.append(f"{m.group(1)}{new}{m.group(4)}{m.group(5)}{m.group(6)}"
                   f"{extra}{tail}")

    print("MIGRATION to the six ruled classes\n")
    for k, n in sorted(moved.items(), key=lambda kv: -kv[1]):
        print(f"  {n:>4}  {k}")
    print(f"\n  {sum(moved.values())} rows rewritten")

    # post-state, computed from the OUTPUT so the report cannot drift from it
    latest: dict[str, str] = {}
    for line in out:
        m = ROW.match(line)
        if m:
            latest[m.group(2)] = m.group(3)
    c = collections.Counter(latest.values())
    print("\n  RESULTING STATE - all six classes, mutually exclusive:")
    for cls in CLASSES:
        print(f"    {c.get(cls, 0):>4}  {cls}")
    stray = sorted(set(c) - set(CLASSES))
    print(f"    ----\n    {sum(c.values()):>4}  TOTAL"
          f"{'   STRAY: ' + str(stray) if stray else ''}")

    if a.write:
        QUEUE.write_text("\n".join(out) + "\n", encoding="utf-8")
        print("\nWRITTEN")
    else:
        print("\nDRY RUN - pass --write to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
