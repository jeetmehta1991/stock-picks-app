#!/usr/bin/env python
"""B1788: verify the rows awaiting verification, against CODE - not prose.

Owner: *"92 tickets. Lets start verifying them. If verified and no further
potential action, move them to EXECUTED with the right comments. If anything to
be done even potentially, keep them open and flag for further action. As
relevant, verify against code vs docs and prose."*

THE RULE APPLIED. A row may become EXECUTED only when the artifact it NAMES is
present in the live codebase - and, for a gate, WIRED. Everything else stays
OPEN carrying what is missing, because *"anything to be done even potentially"*
means the burden of proof sits on promotion, never on staying open.

WHAT COUNTS AS EVIDENCE, and nothing else does:
    scan_/check_ gate  -> defined in verify_turn_compliance.py AND referenced
                          somewhere beyond its own def
    test_bNNN          -> defined in a test file (prefix match: a row may name
                          `test_b1597` for `test_b1597_something`)
    file path          -> the file exists anywhere under scripts/ or backtest/
    CHECKLIST #NNN     -> the item exists in CHECKLIST.md
    LEARNINGS LNNN     -> the entry exists in LEARNINGS.md

HARNESS LESSONS THIS SCRIPT ENCODES, each bought with a false finding earlier
in this session:
  - never strip bare `_` as markdown: it destroys every snake_case identifier
    and produced 17 false MISSING (B1787)
  - glob backtest/ as well as scripts/: a scripts-only inventory produced 4
    more (B1787)
  - match test names by PREFIX: exact matching produced 1 more (B1787)
  - a suspiciously clean result is a harness bug until proven (B1779, B1787)

HAND-RUN: python scripts/verify_awaiting_rows.py [--write]
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "EXECUTION_QUEUE.md"

ROW = re.compile(
    r"^(\|\s*\*\*(S6-[A-Za-z0-9-]+)\*\*\s*\|\s*\*\*)([A-Z-]+)(\*\*\s*\|\s*)(\S*)(\s*\|)(.*)$")

AWAITING = "self-reported and never verified against code"


def inventory():
    vtc = (ROOT / "scripts" / "verify_turn_compliance.py").read_text(encoding="utf-8")
    gates = set(re.findall(r"def (scan_\w+|check_\w+)", vtc))
    wired = {g for g in gates
             if len(re.findall(rf"\b{re.escape(g)}\b", vtc)) > 1}
    tests = set()
    for tf in (ROOT / "backtest" / "tests").glob("test_*.py"):
        tests |= set(re.findall(r"def (test_\w+)",
                                tf.read_text(encoding="utf-8", errors="replace")))
    files = {p.name for p in (ROOT / "scripts").glob("*.py")}
    files |= {p.name for p in (ROOT / "backtest").rglob("*.py")}
    ck = set(re.findall(r"###\s*#(\d+)",
                        (ROOT / "CHECKLIST.md").read_text(encoding="utf-8")))
    ln = set(re.findall(r"###\s*L(\d+)",
                        (ROOT / "LEARNINGS.md").read_text(encoding="utf-8")))
    return gates, wired, tests, files, ck, ln


def assess(desc, inv):
    gates, wired, tests, files, ck, ln = inv
    # strip PAIRED emphasis only - bare underscores are identifiers
    low = re.sub(r"\*\*?", "", desc).lower()
    found, missing, context = [], [], []

    for g in set(re.findall(r"\b((?:scan|check)_[a-z0-9_]+)", low)):
        if g not in gates:
            missing.append(f"gate absent: {g}")
        elif g not in wired:
            missing.append(f"gate defined but NOT WIRED: {g}")
        else:
            found.append(f"gate {g}")
    for t in set(re.findall(r"\b(test_b[a-z0-9_]+)", low)):
        if any(x.startswith(t) for x in tests):
            found.append(f"test {t}")
        else:
            missing.append(f"test absent: {t}")
    # B1788c: A FILE MENTION IS NOT EVIDENCE THAT THIS ROW'S WORK LANDED.
    # `technical.py` and `tighten_breaker_block.py` predate most rows naming
    # them by months, so "the file exists" proves only that the file exists.
    # Promotion needs a BATCH-SPECIFIC artifact - a wired gate, or a
    # `test_bNNN` whose number ties it to the batch. A missing file is still a
    # strong NEGATIVE, so absence keeps its weight while presence does not.
    for f in set(re.findall(r"\b([a-z0-9_]+\.py)\b", low)):
        if f in files:
            context.append(f"file {f} exists (predates row - not evidence)")
        else:
            missing.append(f"file absent: {f}")
    # B1788b: DOCS ARE NOT EVIDENCE. The owner ruled "verify against code vs
    # docs and prose", and my first pass would have promoted 85 rows on
    # LEARNINGS/CHECKLIST references alone - precisely the evidence excluded.
    # They are recorded as CONTEXT and never count toward promotion.
    for n in set(re.findall(r"#(\d{2,3})\b", low)):
        if n in ck:
            context.append(f"CHECKLIST #{n} (doc)")
    for n in set(re.findall(r"\bl(\d{3})\b", low)):
        if n in ln:
            context.append(f"LEARNINGS L{n} (doc)")

    # explicit not-done language always blocks promotion
    OPENISH = ("not built", "not started", "unbuilt", "needs owner",
               "awaiting", "pending", "to be built", "not implemented",
               "needs a decision", "not yet")
    stated_open = [m for m in OPENISH if m in low]
    return found, missing, stated_open, context


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--show", type=int, default=18)
    a = ap.parse_args()

    inv = inventory()
    print(f"live inventory: {len(inv[0])} gates ({len(inv[1])} wired), "
          f"{len(inv[2])} tests, {len(inv[3])} py files, "
          f"{len(inv[4])} checklist items, {len(inv[5])} learnings\n")

    lines = QUEUE.read_text(encoding="utf-8").splitlines()
    last: dict[str, int] = {}
    for i, line in enumerate(lines):
        m = ROW.match(line)
        if m:
            last[m.group(2)] = i

    out, verdicts = [], collections.Counter()
    promoted, flagged = [], []
    for i, line in enumerate(lines):
        m = ROW.match(line)
        if not m or last.get(m.group(2)) != i:
            out.append(line)
            continue
        tid, cls, tail = m.group(2), m.group(3), m.group(7)
        if cls != "OPEN" or AWAITING not in tail:
            out.append(line)
            continue

        found, missing, stated_open, context = assess(tail, inv)
        if missing or stated_open or not found:
            why = (missing[:2] or [f"row states: {stated_open[0]}"] if stated_open
                   else ["names no WIRED GATE and no test_bNNN - the only "
                         "batch-specific code artifacts. Nothing to verify "
                         "against (doc and file mentions do not count)"])
            verdicts["FLAGGED - stays OPEN"] += 1
            flagged.append((tid, why[0]))
            new_tail = re.sub(
                re.escape(AWAITING) + r"[^|]*?\.",
                f"{AWAITING}. **VERIFY ATTEMPTED B1788 - STILL OPEN:** "
                f"{'; '.join(why[:2])}.", tail, count=1)
            out.append(f"{m.group(1)}OPEN{m.group(4)}{m.group(5)}{m.group(6)}"
                       f"{new_tail}")
        else:
            verdicts["VERIFIED - promoted to EXECUTED"] += 1
            promoted.append((tid, "; ".join(found[:3])))
            new_tail = re.sub(
                re.escape(AWAITING) + r"[^|]*?\.",
                f"**VERIFIED B1788 against live code:** {'; '.join(found[:3])} "
                "present and wired. No further action identified.", tail, count=1)
            out.append(f"{m.group(1)}EXECUTED{m.group(4)}{m.group(5)}{m.group(6)}"
                       f"{new_tail}")

    total = sum(verdicts.values())
    print(f"rows awaiting verification: {total}")
    for k, n in verdicts.most_common():
        print(f"  {n:>4}  {k}")

    print(f"\nPROMOTED ({len(promoted)}) - artifact present and wired:")
    for tid, ev in promoted[:a.show]:
        print(f"  {tid:<14} {ev[:88]}")
    if len(promoted) > a.show:
        print(f"  ... {len(promoted)-a.show} more")

    print(f"\nFLAGGED ({len(flagged)}) - stays OPEN:")
    reasons = collections.Counter(
        "names nothing checkable" if "names no" in w else
        ("row states work remains" if "row states" in w else "artifact missing")
        for _, w in flagged)
    for k, n in reasons.most_common():
        print(f"  {n:>4}  {k}")
    for tid, w in flagged[:a.show]:
        print(f"  {tid:<14} {w[:88]}")

    if a.write:
        QUEUE.write_text("\n".join(out) + "\n", encoding="utf-8")
        print("\nWRITTEN")
    else:
        print("\nDRY RUN - pass --write to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
