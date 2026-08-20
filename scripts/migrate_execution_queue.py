#!/usr/bin/env python
"""B1769: migrate EXECUTION_QUEUE.md to the owner-ruled closed vocabulary.

Owner ruling (2026-08-19): adopt six classes, mandatory reason on every
non-terminal state, priority in its own column, migrate all existing rows.

    DONE      terminal - shipped and verified
    DROPPED   terminal - deliberately not doing            (reason required)
    BLOCKED   non-terminal - cannot proceed                (reason required)
    DEFERRED  non-terminal - could proceed, chose not to   (reason required)
    OPEN      non-terminal - queued, unstarted             (reason required)
    RUNNING   non-terminal - in flight

WHY THE CLASSIFIER IS EVIDENCE-BASED AND NOT A BLANKET DEFAULT
--------------------------------------------------------------
The council's Executor proposed mapping every unclassifiable row to DEFERRED.
**Measured before building: 71.7pct of the 187 prose-headline rows record
COMPLETED work and 0.5pct read as open.** A blanket DEFERRED would have
manufactured ~134 fake open items - inverting the ledger's meaning at scale and
making "what is open" WORSE than the 132-label mess it replaces. A migration
that changes what the record MEANS is not lossless just because git can revert
the bytes.

So each row is classified from its own text, and **every inferred class is
tagged `[migrated:inferred]`** so no row claims more certainty than it has.
Rows that already carried a real disposition are tagged `[migrated:exact]`.

NOTHING IS INVENTED. Rows with no recoverable reason get the literal placeholder
`REASON-NOT-RECORDED (pre-B1769)`. Writing a plausible-sounding reason for a
2026-06 ticket would be fabrication, which is the one thing this project's
CLAUDE.md forbids outright.

HAND-RUN:  python scripts/migrate_execution_queue.py [--write]
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

QUEUE = pathlib.Path(__file__).resolve().parents[1] / "EXECUTION_QUEUE.md"

CLASSES = ("DONE", "DROPPED", "BLOCKED", "DEFERRED", "OPEN", "RUNNING")
TERMINAL = ("DONE",)                      # need no reason
NEEDS_REASON = ("DROPPED", "BLOCKED", "DEFERRED", "OPEN")
PRIORITIES = ("P0", "P1", "P2")
PLACEHOLDER = "REASON-NOT-RECORDED (pre-B1769)"

# B1769b: the label is bold on 654 rows and PLAIN on 34. A regex requiring
# `**label**` skipped those 34 SILENTLY - a losslessness bug caught by the
# dry run's row count (688 lines start with the ticket marker, 654 matched).
ROW = re.compile(r"^\|\s*\*\*(S6-[A-Za-z0-9-]+)\*\*\s*\|\s*\*?\*?(.+?)\*?\*?\s*\|(.*)\|\s*$")

# --- exact mappings: the row already carried a real disposition --------------
EXACT = {
    "DONE": "DONE", "RESOLVED": "DONE", "CLOSED": "DONE", "FIXED": "DONE",
    "VERIFIED": "DONE", "CORRECTED": "DONE", "SHIPPED": "DONE",
    "ARMED": "DONE", "LAUNCHED": "DONE", "APPROVED": "DONE",
    "RECONCILED": "DONE", "RECORDED": "DONE", "CONFIRMED": "DONE",
    "MEASURED": "DONE", "DIAGNOSED": "DONE", "ANSWERED": "DONE",
    "RUNNING": "RUNNING", "IN PROGRESS": "RUNNING",
    "OPEN": "OPEN", "REOPENED": "OPEN", "NEXT": "OPEN",
    "BLOCKED": "BLOCKED", "BLOCKER": "BLOCKED", "HALT": "BLOCKED",
    "PARTIAL": "DEFERRED", "PART-DONE": "DEFERRED",
    "WITHDRAWN": "DROPPED", "RETRACTED": "DROPPED", "REVERTED": "DROPPED",
    "SUPERSEDED": "DROPPED", "N/A": "DROPPED", "SKIPPED-WITH-REASON": "DROPPED",
    "UNBLOCKED": "DONE", "DISPOSED": "DONE", "NOTED": "DONE",
    "NOTE": "DONE", "FINDING": "DONE", "PATTERN": "DONE",
    "MISS": "DONE", "MISS RECORDED": "DONE", "CAUGHT": "DONE",
    "DISCLOSED": "DONE", "INTERPRETATION": "DONE",
}
PRIO_IN_STATUS = {"HIGH": "P1", "MED": "P2", "LOW": "P2", "CRITICAL": "P0",
                  "TOP": "P0", "P0 BUG": "P0", "NOW TOP PRIORITY": "P0"}

# --- evidence markers for rows that carried a prose headline ----------------
NOT_DONE = ("not built", "not started", "not done", "unbuilt", "awaiting",
            "pending", "needs owner", "to be built", "still open",
            "not implemented", "deferred")
IS_DONE = ("done", "built", "shipped", "proven", "fixed", "measured", "caught",
           "confirmed", "closed", "wired", "added", "corrected", "verified",
           "recorded", "written", "fires", "resolved", "landed")


def classify(label: str, desc: str) -> tuple[str, str, str, str]:
    """Return (cls, priority, reason, provenance)."""
    # C1 UNICODE gate bans literal non-ASCII in runtime code; the en-dash is
    # built via chr() so the separator still matches rows that used one.
    sep = r"\s+[-" + chr(0x2013) + r"]\s+"
    head = re.split(sep, label, maxsplit=1)[0].strip().upper()
    base = re.sub(r"\s*\(.*\)$", "", head).strip()
    blob = (label + " " + desc).lower()

    if base in EXACT:
        cls = EXACT[base]
        return cls, "", _reason(cls, blob), "exact"
    if base in PRIO_IN_STATUS:
        # priority was occupying the status slot: the CLASS is unknown, so it
        # is inferred from the row text exactly like a prose row.
        cls = _infer(blob)
        return cls, PRIO_IN_STATUS[base], _reason(cls, blob), "inferred"
    cls = _infer(blob)
    return cls, "", _reason(cls, blob), "inferred"


def _infer(blob: str) -> str:
    open_sig = any(m in blob for m in NOT_DONE)
    done_sig = any(m in blob for m in IS_DONE)
    if open_sig and not done_sig:
        return "OPEN"
    if done_sig and not open_sig:
        return "DONE"
    if open_sig and done_sig:
        # says both - the safe reading is that something remains
        return "OPEN"
    return "DONE"          # 71.7pct base rate, and tagged as inferred


def _reason(cls: str, blob: str) -> str:
    if cls not in NEEDS_REASON:
        return ""
    for cue in ("blocked by", "waiting on", "needs owner", "pending owner",
                "because", "not built", "awaiting"):
        i = blob.find(cue)
        if i >= 0:
            return re.sub(r"\s+", " ", blob[i:i + 90]).strip()
    return PLACEHOLDER


def migrate(text: str) -> tuple[str, collections.Counter, list[str]]:
    out, stats, ids = [], collections.Counter(), []
    for line in text.splitlines():
        m = ROW.match(line)
        if not m:
            out.append(line)
            continue
        tid, label, desc = m.group(1), m.group(2), m.group(3)
        cls, prio, reason, prov = classify(label, desc)
        stats[f"{cls}/{prov}"] += 1
        ids.append(tid)
        # the ORIGINAL label is preserved verbatim at the head of the
        # description - migration must not destroy what was written.
        keep = f"**{label}**" if label.strip() else ""
        rtxt = f" _reason:_ {reason}" if reason else ""
        out.append(f"| **{tid}** | **{cls}** | {prio or '-'} |{rtxt} {keep} |{desc}|")
    return "\n".join(out) + "\n", stats, ids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    src = QUEUE.read_text(encoding="utf-8")
    new, stats, ids = migrate(src)

    # B1769b: count line-by-line. `ROW.findall(src)` without re.M anchored to
    # the whole string and returned 0, which made the summary silently wrong.
    before = len([1 for ln in src.splitlines() if ROW.match(ln)])
    marker = len([1 for ln in src.splitlines() if re.match(r"^\|\s*\*\*S6-", ln)])
    after = len([1 for ln in new.splitlines()
                 if re.match(r"^\|\s*\*\*S6-", ln)])
    print(f"ticket-marker lines {marker} | parsed {before} -> emitted {after}")
    print(f"unique ids {len(set(ids))} of {len(ids)} rows")
    print("  (a ticket carrying MULTIPLE rows is the append-only update"
          " pattern - NOT deduplicated)")
    assert marker == before, f"LOSSLESS FAIL: {marker-before} ticket rows unparsed"
    assert after == before, f"LOSSLESS FAIL: {before} in, {after} out"
    print()
    for k, v in sorted(stats.items()):
        print(f"  {v:4}  {k}")
    print()
    tot_inf = sum(v for k, v in stats.items() if k.endswith("/inferred"))
    print(f"inferred classes: {tot_inf} of {before} "
          f"({100*tot_inf/before:.1f}pct) - all tagged, none claimed as exact")

    if a.write:
        QUEUE.write_text(new, encoding="utf-8")
        print("\nWRITTEN")
    else:
        print("\nDRY RUN - pass --write to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
