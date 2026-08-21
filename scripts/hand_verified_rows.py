#!/usr/bin/env python
"""B1793: the hand-read verdicts, as LABELLED GROUND TRUTH for any classifier.

`#268` says a classifier inherits its author's model of the data, and that the
cure is to hand-read a sample first. **That instruction cannot be mechanically
verified - but its OUTPUT can be kept and reused.**

Four classifiers were built to sort these rows and all four over-promoted,
because each was built on a wrong model of the population. **There was no way to
find that out except by reading rows.** These are the rows I read, with the
verdict I reached and the phrase that decided it, so the next classifier is
scored against evidence rather than against my expectations of it.

This is `gate_incident_corpus.py`'s pattern moved from gates to classifiers: a
gate is unproven until it fires on the words that motivated it; **a classifier
is unproven until it reproduces verdicts a human reached by reading.**

VERDICTS ARE THE HUMAN'S, NOT A TOOL'S. Each was reached by reading the row's
ORIGINAL text - annotations stripped - and asking the owner's question: is a
measurement or action completed, and is anything pending?

HAND-RUN: python scripts/hand_verified_rows.py
"""
from __future__ import annotations

# ticket -> (verdict, the phrase that decided it)
#
# EXECUTED - a finding plus its consequence, no verb pointing forward
# OPEN     - a task with a verb; work directed, not reported
# BLOCKED  - the row states its own blocker
LABELS: dict[str, tuple[str, str]] = {
    # --- complete: a result and its consequence
    "S6-B1526a": ("EXECUTED",
                  "Cliff SHARP; band NOT extended; sweep stays 20 engine runs."),
    "S6-B1529b": ("EXECUTED",
                  "R5 wall-clock NOT recoverable from artifacts (L403)."),
    # --- wrong class: states its own blocker
    "S6-B1532c": ("BLOCKED",
                  "BLOCKED: import pandas hangs, so no Python profiling can run "
                  "until WMI recovers"),
    # --- open work: every one is a task with a verb
    "S6-B1503a": ("OPEN", "Never tested. Run first."),
    "S6-B1503b": ("OPEN", "needs resimulation ~50 s/ticker"),
    "S6-B1503c": ("OPEN", "would need a producer edit = NEW-GATE class, so ASK"),
    "S6-B1503d": ("OPEN", "Re-run the full grid ... once the above land"),
    "S6-B1512a": ("OPEN", "Verify the 8-vs-6 mechanism before any resim is costed"),
    "S6-B1513a": ("OPEN", "Establish WHY R5 ran 381 of 503 ... Needed before"),
    "S6-B1515a": ("OPEN", "Owner go/no-go with the measured slope before the 381 run"),
    "S6-B1518b": ("OPEN", "Pin test: set SMC_SWING_LENGTH to a non-default"),
    "S6-B1518c": ("OPEN", "Audit every other SPEC parameter the same way before"),
    "S6-B1522a": ("OPEN", "Add to plan SS9 as item 21"),
    "S6-B1527a": ("OPEN", "Verify at next launch that the cron's state-file path"),
    "S6-B1528a": ("OPEN", "If P1 results later look anomalous, run a per-BAR set diff"),
    "S6-B1531b": ("OPEN", "Build the harvester"),
    "S6-B1531c": ("OPEN", "Map producer axes per strategy FAMILY"),
    "S6-B1532a": ("OPEN", "Re-open the universe ladder as a COST question"),
    "S6-B1532b": ("OPEN", "Recompute the slope at run completion"),
    "S6-B1541a": ("OPEN", "Owner approval required to enable."),
}


def score(classify) -> tuple[int, int, list[str]]:
    """Score a classifier against the hand labels.

    `classify` takes the row's ORIGINAL text and returns a class string.
    Returns (correct, total, disagreements).
    """
    ok, wrong = 0, []
    for tid, (verdict, phrase) in LABELS.items():
        got = classify(phrase)
        if got == verdict:
            ok += 1
        else:
            wrong.append(f"{tid}: hand={verdict} classifier={got} -- {phrase[:52]}")
    return ok, len(LABELS), wrong


def main() -> int:
    import collections
    c = collections.Counter(v for v, _ in LABELS.values())
    print(f"hand-verified rows: {len(LABELS)}")
    for k, n in c.most_common():
        print(f"  {n:>3}  {k}")
    print(f"\ncompletion rate: {100*c['EXECUTED']/len(LABELS):.0f}pct")
    print("\nFour classifiers promoted 17-57 of this population. The rate here is")
    print("the reason all four were wrong: they hunted for a recorded result in")
    print("rows that are overwhelmingly TASKS WITH VERBS.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
