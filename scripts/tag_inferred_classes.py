#!/usr/bin/env python
"""One-off retro-tagger for the B1769 migration's inferred classes (B2020).

H ruling 2026-08-22: "S6-B1870a gets a correcting row + one-off tag script."

S6-B1870a MEASURED that `S6-B1769b`'s claim - "39.4pct of classes INFERRED
from row text, every one tagged" - was false: the migration commit
`49493c67f` wrote the tag ZERO times (one prose mention only). This script
writes the tags that were claimed, with provenance recovered from the
migration diff itself:

  * a migrated row whose PRE-migration 2nd column was a PRIORITY label
    (HIGH/MED/LOW/...) had NO state to copy, so its class was INFERRED;
  * a migrated row whose pre-migration 2nd column was already a class
    label was EXACT and gets no tag.

The tag lands on the FIRST row for the ticket id in today's file - the
migration rewrote the whole file, and every later change either appended a
row or edited that same physical row in place, so first-occurrence IS the
migrated row. Idempotent: rows already carrying `[inferred-class` are
skipped. Dry-run by default; `--write` mutates EXECUTION_QUEUE.md.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / "EXECUTION_QUEUE.md"
MIGRATION_SHA = "49493c67f"
# The vocabulary AT the migration (B1769). DONE was later re-ruled (B1784)
# but was a valid class label on migration day, so an old row carrying it
# was copied EXACT, not inferred.
CLASSES = {"DONE", "DROPPED", "BLOCKED", "DEFERRED", "OPEN", "RUNNING", "CLOSED"}
ROW_RE = re.compile(r"^[+-]\| \*\*(S6-B[0-9]+[a-z]?)\*\* \| ([^|]+) \|")


def migration_pairs() -> tuple[dict, dict]:
    diff = subprocess.run(
        ["git", "show", MIGRATION_SHA, "--", "EXECUTION_QUEUE.md"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT), check=True).stdout
    old, new = {}, {}
    for line in diff.splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        tid, cell2 = m.group(1), m.group(2).strip().strip("*").strip()
        # keep the FIRST occurrence per side: the migration is one rewrite,
        # so a tid should appear once per side; first wins deterministically.
        side = old if line.startswith("-") else new
        side.setdefault(tid, cell2)
    return old, new


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true",
                    help="mutate EXECUTION_QUEUE.md (default: dry-run report)")
    a = ap.parse_args()

    old, new = migration_pairs()
    migrated = sorted(set(old) & set(new))
    inferred = [t for t in migrated if old[t] not in CLASSES]
    exact = [t for t in migrated if old[t] in CLASSES]

    text = QUEUE.read_text(encoding="utf-8")
    lines = text.splitlines()
    first_row = {}
    for i, ln in enumerate(lines):
        m = re.match(r"^\| \*\*(S6-B[0-9]+[a-z]?)\*\* \|", ln)
        if m and m.group(1) not in first_row:
            first_row[m.group(1)] = i

    tagged, already, unfindable = [], [], []
    for tid in inferred:
        i = first_row.get(tid)
        if i is None:
            unfindable.append(tid)
            continue
        if "[inferred-class" in lines[i]:
            already.append(tid)
            continue
        ln = lines[i].rstrip()
        if not ln.endswith("|"):
            unfindable.append(tid)  # malformed row: do not guess (#275)
            continue
        lines[i] = (ln[:-1].rstrip()
                    + f" [inferred-class B1870-retro: pre-migration 2nd col was '{old[tid]}'] |")
        tagged.append(tid)

    print(f"migrated pairs : {len(migrated)}")
    print(f"inferred       : {len(inferred)} ({len(inferred)/max(len(migrated),1):.1%})")
    print(f"exact          : {len(exact)}")
    print(f"tagged         : {len(tagged)}")
    print(f"already tagged : {len(already)}")
    print(f"unfindable     : {len(unfindable)} {unfindable[:10]}")
    if a.write and tagged:
        QUEUE.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("WROTE EXECUTION_QUEUE.md")
    elif not a.write:
        print("DRY-RUN - nothing written. Sample tags:")
        for tid in tagged[:3]:
            print(" ", lines[first_row[tid]][-160:])
    return 0


if __name__ == "__main__":
    sys.exit(main())
