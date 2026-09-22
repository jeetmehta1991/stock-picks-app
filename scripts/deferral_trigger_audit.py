#!/usr/bin/env python
# Source: EXECUTION_QUEUE.md (the ledger itself) read through
# scripts/queue_state.py, plus .queue_exempt_log; per CHECKLIST #77 this
# script derives every figure from those two artifacts and stores none.
"""S6-B2971 / L838: a named re-open trigger that NOTHING EVALUATES.

WHY THIS EXISTS. A deferral in this ledger is allowed only with a named
trigger - the rule that a deferral without one is a silent drop. That rule
made the deferrals honest and stopped one step short: it says the trigger
must be WRITTEN, never that anything must READ it. So a trigger is prose in
a queue cell, consulted only when a human happens to open the row.

MEASURED 2026-09-22: S6-B2620b's trigger is "the logged exempt-commit count
for ledger flips exceeds 5". S6-B2933 measured 5 on 2026-09-14 and recorded
that it sat one landing away. The true count that morning was 8 - it had
crossed on 2026-09-21 and stayed over the line for three commits, and it
surfaced only because an unrelated turn-gate violation forced a grep of the
identifier. Nothing in the system was looking.

WHAT THIS DOES, AND WHAT IT REFUSES TO DO.

  registered   a trigger with an EVALUATOR - a function that reads a real
               artifact and returns (value, threshold, fired). These are
               checked every run and reported with their numbers.

  unevaluated  a DEFERRED row whose text carries re-open language and has
               no evaluator. These are DISCLOSED BY ID, never counted as
               zero - a trigger nobody can evaluate is exactly the state
               this tool exists to make visible, so hiding it behind a
               clean "0 fired" would reproduce the defect in the
               instrument built to catch it (L644).

THE DETECTOR'S OWN LIMIT, STATED RATHER THAN DISCOVERED LATER. The
re-open-language pattern below was written from the rows in front of me,
so its recall is a LOWER BOUND (L950). A control run over the rows it did
NOT flag found three more carrying a re-open condition in different words -
"hold until Phase 1B", "waits for the optimisation program to finish",
"revisit only if profiling re-ranks the panel pre-pass". The pattern cannot
see a milestone phrased as an ordinary sentence, and no widening makes that
claim safe. So the count this prints is reported as AT LEAST N.

    python scripts/deferral_trigger_audit.py
"""
from __future__ import annotations

import argparse
import ast
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

QUEUE = ROOT / "EXECUTION_QUEUE.md"
EXEMPT_LOG = ROOT / ".queue_exempt_log"

# Written from the rows in front of me; recall is a LOWER BOUND (see the
# module docstring's control run). Kept deliberately narrow: a wider pattern
# would flag prose that merely discusses triggers, and a false "this row has
# an unevaluated trigger" trains the reader to skim the disclosure.
_REOPEN_LANGUAGE = re.compile(
    r"re-?open when|re-?open if|named trigger|trigger[: =]|exceeds", re.I)


SANCTIONED_LANDING_FILES = ("output_audit/postconfig_landings.jsonl",
                            "output_audit/postconfig_ledger.json",
                            "output_audit/POSTCONFIG_REPORT.md")


def _mixed_class_ledger_flips() -> int:
    """S6-B2620b REFINED (B2999): count only the SUSPICIOUS class.

    The raw count of exempt commits staging the landings jsonl grows by
    ONE PER LANDING by design - the engine hook and the landing-report
    stamp are the sanctioned automation (B2520), so a static threshold
    over the raw count re-fires forever and trains the reader to ignore
    it (L721). The deferral's actual worry was ledger flips OUTSIDE the
    sanctioned shape: an exempt commit that stages the landings jsonl
    BESIDE files that are not landing bookkeeping - canonical docs,
    tests, code - which is a doc batch borrowing the exemption.

    The log records each exempt commit's full staged list, so the
    discriminator is derivable per line: sanctioned = every staged file
    is a landing artifact (the three fixed names plus any
    output_audit/*_gate.json); mixed = anything else beside the jsonl."""
    if not EXEMPT_LOG.exists():
        return 0
    mixed = 0
    for line in io.open(EXEMPT_LOG, encoding="utf-8",
                        errors="replace").read().splitlines():
        if ("exempt commit staging" not in line
                or "postconfig_landings.jsonl" not in line):
            continue
        try:
            staged = ast.literal_eval(line.split("staging:", 1)[1].strip())
        except (ValueError, SyntaxError, IndexError):
            mixed += 1          # an unparseable flip line counts as mixed
            continue
        extra = [f for f in staged
                 if f not in SANCTIONED_LANDING_FILES
                 and not (f.startswith("output_audit/")
                          and f.endswith("_gate.json"))]
        if extra:
            mixed += 1
    return mixed


def _flip_exempt_commits() -> int:
    """S6-B2620b's trigger quantity, read from the log that records it.

    The count is DERIVED, never stored: a stored number is the thing that
    went stale in the first place. The ledger flip is a commit staging
    output_audit/postconfig_landings.jsonl, which is where reported_to_owner
    lives - S6-B2933 states that reading explicitly, and it is an inference,
    not a fact the log labels.
    """
    if not EXEMPT_LOG.exists():
        return 0
    text = io.open(EXEMPT_LOG, encoding="utf-8", errors="replace").read()
    return sum(1 for line in text.splitlines()
               if "exempt commit staging" in line
               and "postconfig_landings.jsonl" in line)


# ticket id -> (what the trigger says, threshold, evaluator, comparison)
REGISTERED = {
    "S6-B2620b": {
        # B2999: REFINED from the raw flip count (which grows one per
        # landing by design and had fired at 11). Baseline of 2 mixed-
        # class flips dispositioned in the S6-B2620b closing row -
        # 2026-09-22T00:19:10 and T06:01:28, both this session's gate-
        # storm closes, content verified benign in HEAD - so the
        # tripwire re-arms on the THIRD.
        "trigger": ("exempt commits staging the landings jsonl beside "
                    "non-landing files exceed the dispositioned "
                    "baseline of 2"),
        "threshold": 2,
        "value": _mixed_class_ledger_flips,
        "fired": lambda v, t: v > t,
        "source": ".queue_exempt_log",
    },
}


def _deferred_rows() -> dict[str, str]:
    """ticket id -> its last row's text, for tickets whose state is DEFERRED.

    Routed through queue_state so the append-log reduction is the ledger's
    one reader (#271) - a hand-written regex over the file would count rows
    rather than tickets.
    """
    import queue_state as qs

    lines = io.open(QUEUE, encoding="utf-8", newline="").read().split("\n")
    last: dict[str, tuple[str, int]] = {}
    for lineno, tid, state in qs.rows():
        last[tid] = (state, lineno)
    out: dict[str, str] = {}
    for tid, (state, lineno) in last.items():
        if state != "DEFERRED":
            continue
        if 0 < lineno <= len(lines):
            out[tid] = lines[lineno - 1]
    return out


def audit() -> dict:
    """Evaluate every registered trigger; disclose every one that is not."""
    fired, quiet = [], []
    for tid, spec in sorted(REGISTERED.items()):
        value = spec["value"]()
        hit = spec["fired"](value, spec["threshold"])
        row = {"ticket": tid, "trigger": spec["trigger"],
               "value": value, "threshold": spec["threshold"],
               "source": spec["source"]}
        (fired if hit else quiet).append(row)

    unevaluated = []
    for tid, text in sorted(_deferred_rows().items()):
        if tid in REGISTERED:
            continue
        m = _REOPEN_LANGUAGE.search(text)
        if not m:
            continue
        unevaluated.append({"ticket": tid,
                            "excerpt": text[max(0, m.start() - 60):
                                            m.start() + 160].strip()})

    return {
        "registered_total": len(REGISTERED),
        "fired": fired,
        "quiet": quiet,
        "unevaluated": unevaluated,
        "recall_caveat": (
            "the unevaluated list is a LOWER BOUND and carries a measured "
            "error rate, both hand-read rather than asserted. RECALL: the "
            "re-open-language pattern was written from the rows in front of "
            "its author, and a control run over the rows it did NOT flag "
            "found three further DEFERRED rows carrying a re-open condition "
            "in wording it cannot match. PRECISION: hand-reading all 9 rows "
            "it flagged on 2026-09-22 found 8 genuine and 1 false positive "
            "- S6-B2420 matches the word trigger inside a sentence DENYING "
            "it has one (no trigger date set), which is the negation class "
            "a keyword matcher cannot see"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fail-on-fired", action="store_true",
                    help="exit 2 when any registered trigger has fired")
    a = ap.parse_args()

    doc = audit()
    print("=== deferral trigger audit ===")
    print(f"  registered triggers           {doc['registered_total']}")
    for r in doc["fired"]:
        print(f"  FIRED  {r['ticket']}: {r['value']} against a threshold of "
              f"{r['threshold']} ({r['source']})")
        print(f"         trigger reads: {r['trigger']}")
    for r in doc["quiet"]:
        print(f"  quiet  {r['ticket']}: {r['value']} against a threshold of "
              f"{r['threshold']} ({r['source']})")
    print(f"  UNEVALUATED (at least)        {len(doc['unevaluated'])}")
    for r in doc["unevaluated"]:
        print(f"    - {r['ticket']}: ...{r['excerpt']}")
    print("  NOTE: " + doc["recall_caveat"])

    if a.fail_on_fired and doc["fired"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
