#!/usr/bin/env python
"""B1791: an analysis row may become EXECUTED only if NOTHING is pending.

OWNER RULING 2026-08-20:
    "EXECUTED. But before we do that, I want to verify that each of the 138
     tickets have measurements or actions completed and nothing is pending.
     Only then they move to EXECUTED."

So the ruling resolves `S6-B1790c` - an analysis row CAN reach EXECUTED - but
it attaches a condition that has to be checked per row, not assumed for the
population. `#266` said these rows have no code to verify; this asks the
question that IS answerable about them: **did the measurement actually happen,
and is anything left over?**

TWO TESTS, and a row must pass BOTH:

  1. COMPLETED   the row records a RESULT - a concrete figure, count, verdict
                 or named outcome. "measured X = 47" is a result;
                 "needs measuring" is not.
  2. NOTHING PENDING   no forward-looking or unfinished language anywhere in
                 the row - not built, awaiting, needs owner, to be, remains,
                 next step, TBD, unknown, will, should.

**Ambiguity keeps a row OPEN.** The owner's standing asymmetry from B1788 -
*"if anything to be done even potentially, keep them open"* - puts the burden of
proof on promotion, so a row that cannot be shown complete is not promoted.

WHY A NUMBER IS THE EVIDENCE HERE. For a build row the artifact is code; for a
measurement row the artifact IS the figure. A row asserting an analysis happened
without stating what it found has produced nothing durable - which is the same
`#264` defect (a claim that names no artifact) in its analysis form.

HAND-RUN: python scripts/verify_analysis_rows_complete.py [--write]
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
FLAG = "VERIFY ATTEMPTED B1788 - STILL OPEN"

# forward-looking / unfinished - ANY of these keeps the row OPEN
PENDING = (
    "not built", "not started", "not done", "unbuilt", "not implemented",
    "not yet", "to be built", "to be done", "to be decided", "remains",
    "remaining", "awaiting", "pending", "needs owner", "needs a ruling",
    "needs a decision", "needs the", "needs to", "must still", "still to",
    "next step", "next turn", "tbd", "unknown", "will be", "should be",
    "would be", "open question", "requires", "candidate for", "deferred",
    "not proposed", "no mechanism", "unresolved", "untraced", "unreviewed",
    # B1791d: "needs resimulation" slipped past fixed phrases like
    # "needs owner". Any "needs <something>" is outstanding work.
    "needs ", "need to", "needed", "resimulation", "resim",
    "not verified", "cannot be", "blocked",
)

# a recorded RESULT - the analysis artifact for a measurement row
RESULT = (
    re.compile(r"\b\d+\s*(?:of|/)\s*\d+\b"),          # 3 of 26
    re.compile(r"\b\d+(?:\.\d+)?\s*pct\b"),           # 71.7pct
    re.compile(r"\b\d+(?:\.\d+)?\s*%"),
    re.compile(r"\brho\s*=\s*[-+]?\d"),
    re.compile(r"=\s*[-+]?\d+(?:\.\d+)?\b"),
    re.compile(r"\b(?:measured|counted|found|confirmed|proven|reproduced|"
               r"disproved|ruled out)\b"),
)


def original_text(desc: str) -> str:
    """The ticket's OWN content, with my verification annotations removed.

    B1791b: every pass since B1769 has PREPENDED text to these rows - the
    migration reason, then B1788's flag, then B1790's verdict. The row now reads

        _reason:_ <my annotations ...> HIGH | <the original ticket text>

    and my first classifier scored the ANNOTATIONS. It was about to promote
    `S6-B1512a`, whose actual content says *"Verify the 8-vs-6 mechanism BEFORE
    any resim is costed"* - pending work, hidden behind 430 characters of my
    own prose. **A verifier that reads its own output is grading its own
    homework**, and each pass makes the contamination worse.
    """
    return re.sub(r"_reason:_.*?\|", "", desc, count=1, flags=re.S)


# B1791c: IMPERATIVE and CONDITIONAL-FUTURE constructions are pending work even
# when no not-done phrase appears. `S6-B1512a` reads "Verify the 8-vs-6
# mechanism BEFORE any resim is costed. If confirmed, resim..." - an instruction
# and a conditional, with no "not built" anywhere. It passed two versions of
# this classifier before the hand spot-check caught it.
IMPERATIVE = re.compile(
    r"(?:^|[.;:|]\s*)(verify|check|run|measure|decide|confirm|trace|re-run|"
    r"rerun|audit|review|split|compute|add|build|wire|fix|apply|drop|"
    r"reclassify|investigate|resolve|extend|convert)\b", re.I)
CONDITIONAL = re.compile(
    r"\b(if confirmed|if it|if that|if this|if any|once \w+|after \w+ing|"
    r"then \w+|would need|may want|worth \w+ing)\b", re.I)


def assess(desc):
    # B1791d: STRIP leading whitespace - the ^ anchor in IMPERATIVE was
    # defeated by the space left after the pipe, so rows literally
    # beginning "Add to plan..." and "Resolve the..." read as complete.
    low = re.sub(r"\*\*?", "", original_text(desc)).lower().strip()
    pending = [p for p in PENDING if p in low]
    if IMPERATIVE.search(low):
        pending.append("imperative instruction (work directed, not reported)")
    if CONDITIONAL.search(low):
        pending.append("conditional future ('if X then Y')")
    # B1791e: FOURTH attempt, and the first three failed their hand-checks
    # 3-of-4 and 3-of-5. The diagnosis was wrong: keyword matching cannot
    # separate "I measured X" from "measure X" across months of varied
    # prose. What DID separate the two correct rows from the three wrong
    # ones is position - a completed row LEADS with its result
    # ("400 combinations graded...", "cfg1 ELAPSED=11891s"), while a
    # pending row leads with an instruction, a plan or a conditional.
    # So the result must appear in the FIRST CLAUSE, not anywhere.
    first = re.split(r"[.;|]", low, maxsplit=1)[0]
    results = [r.pattern[:28] for r in RESULT if r.search(first)]
    return pending, results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--show", type=int, default=12)
    a = ap.parse_args()

    lines = QUEUE.read_text(encoding="utf-8").splitlines()
    last = {}
    for i, line in enumerate(lines):
        m = ROW.match(line)
        if m:
            last[m.group(2)] = i

    out, verdicts, promoted, held = [], collections.Counter(), [], []
    for i, line in enumerate(lines):
        m = ROW.match(line)
        if not m or last.get(m.group(2)) != i:
            out.append(line)
            continue
        tid, cls, tail = m.group(2), m.group(3), m.group(7)
        if cls != "OPEN" or FLAG not in tail:
            out.append(line)
            continue

        pending, results = assess(tail)
        if pending:
            verdicts["HELD - work still pending"] += 1
            held.append((tid, f"pending language: {', '.join(pending[:3])}"))
            out.append(line)
        elif not results:
            verdicts["HELD - no recorded result"] += 1
            held.append((tid, "records no figure, count or named outcome - the "
                              "analysis artifact is missing"))
            out.append(line)
        else:
            verdicts["EXECUTED - complete, nothing pending"] += 1
            promoted.append((tid, ", ".join(results[:2])))
            new_tail = tail.replace(
                FLAG,
                "**VERIFIED B1791 per owner ruling:** analysis row - the "
                "measurement is RECORDED and no pending or forward-looking "
                "work remains in the row. ORIGINAL FLAG", 1)
            out.append(f"{m.group(1)}EXECUTED{m.group(4)}{m.group(5)}"
                       f"{m.group(6)}{new_tail}")

    total = sum(verdicts.values())
    print(f"analysis rows examined: {total}")
    for k, v in verdicts.most_common():
        print(f"  {v:>4}  {k}")

    print(f"\nPROMOTED ({len(promoted)}) - result recorded, nothing pending:")
    for tid, ev in promoted[:a.show]:
        print(f"  {tid:<14} result evidence: {ev[:60]}")
    if len(promoted) > a.show:
        print(f"  ... {len(promoted)-a.show} more")

    print(f"\nHELD ({len(held)}):")
    for tid, why in held[:a.show]:
        print(f"  {tid:<14} {why[:84]}")
    if len(held) > a.show:
        print(f"  ... {len(held)-a.show} more")

    print("\nAMBIGUITY KEEPS A ROW OPEN. The owner's standing asymmetry puts the")
    print("burden of proof on promotion, so a row that cannot be SHOWN complete")
    print("is not promoted - being unable to find pending work is not the same")
    print("as showing there is none.")

    if a.write:
        QUEUE.write_text("\n".join(out) + "\n", encoding="utf-8")
        print("\nWRITTEN")
    else:
        print("\nDRY RUN - pass --write to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
