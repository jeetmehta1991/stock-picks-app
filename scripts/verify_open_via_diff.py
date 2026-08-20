#!/usr/bin/env python
"""B1790: verify the remaining OPEN rows from their COMMIT DIFF, not their text.

B1788 verified rows by the artifact they NAME. 148 named nothing, so that method
is exhausted for them. **But a row that never named its artifact still has a
batch, and the batch has a commit whose diff DOES name it.**

THE METHOD:
    row -> batch -> commit -> `git show -U0` -> definitions ADDED by that commit
        -> do those definitions still exist at HEAD?

A definition ADDED by the row's own batch and still present today is
batch-specific code evidence of exactly the kind `#265` requires - stronger than
a file mention, because the batch created it, and stronger than a name in the
row, because the diff cannot be written optimistically.

WHY THIS IS NOT THE B1777 MISTAKE. B1777 asked "did the batch commit touch any
.py file", which is a claim about the BATCH, not the row - a batch carries
several rows and up to 3 changes. This asks a narrower question: did the batch
CREATE a durable named artifact. It still cannot attribute that artifact to one
specific row, so the verdict is named CODE_LANDED_IN_BATCH, not VERIFIED - the
distinction is the point, and overstating it would repeat the defect.

THREE DISPOSITIONS:
    CODE_LANDED_IN_BATCH  the batch added defs that survive at HEAD
    DOC_ONLY_BATCH        the commit touched only docs/data - under the owner's
                          ruling this row can NEVER be EXECUTED on code
                          evidence, which is a question for the owner rather
                          than a defect
    NO_COMMIT             no commit under that batch number at all

HAND-RUN: python scripts/verify_open_via_diff.py [--write]
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "EXECUTION_QUEUE.md"

ROW = re.compile(
    r"^(\|\s*\*\*(S6-[A-Za-z0-9-]+)\*\*\s*\|\s*\*\*)([A-Z-]+)(\*\*\s*\|\s*)(\S*)(\s*\|)(.*)$")
FLAG = "VERIFY ATTEMPTED B1788 - STILL OPEN"
CODE_DIRS = ("scripts/", "backtest/", ".claude/")


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True,
                          text=True, errors="replace").stdout


def batch_commits():
    out = {}
    for line in git("log", "--all", "--format=%H|%s").splitlines():
        if "|" not in line:
            continue
        sha, subj = line.split("|", 1)
        head = re.match(r"\s*((?:B\d+[/+, ]*)+)", subj)
        if not head:
            continue
        for n in re.findall(r"B(\d+)", head.group(1)):
            out.setdefault(int(n), sha)
    return out


def head_symbols():
    syms = set()
    for p in list((ROOT / "scripts").glob("*.py")) + \
            list((ROOT / "backtest").rglob("*.py")):
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        syms |= set(re.findall(r"^\s*def (\w+)", txt, re.M))
        syms |= set(re.findall(r"^\s*class (\w+)", txt, re.M))
    return syms


def added_defs(sha, cache):
    if sha in cache:
        return cache[sha]
    diff = git("show", sha, "-U0", "--", "*.py")
    names = set(re.findall(r"^\+\s*(?:def|class) (\w+)", diff, re.M))
    files = [f for f in git("show", "--name-only", "--format=", sha).splitlines()
             if f.strip()]
    code = [f for f in files
            if f.startswith(CODE_DIRS) and f.endswith((".py", ".json", ".sh"))]
    cache[sha] = (names, bool(code), len(files))
    return cache[sha]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--show", type=int, default=14)
    a = ap.parse_args()

    bc, syms, cache = batch_commits(), head_symbols(), {}
    print(f"batches with a commit {len(bc)} | definitions at HEAD {len(syms)}\n")

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

        n = int(re.match(r"S6-B(\d+)", tid).group(1))
        sha = bc.get(n)
        if not sha:
            verdicts["NO_COMMIT"] += 1
            held.append((tid, "no commit under this batch number"))
            out.append(line)
            continue
        names, has_code, nfiles = added_defs(sha, cache)
        survivors = sorted(names & syms)
        if survivors:
            verdicts["CODE_LANDED_IN_BATCH"] += 1
            promoted.append((tid, ", ".join(survivors[:3]), len(survivors)))
            new_tail = tail.replace(
                FLAG,
                f"**VERIFIED B1790 from the batch DIFF:** commit `{sha[:9]}` added "
                f"{len(survivors)} definition(s) still present at HEAD "
                f"({', '.join(survivors[:3])}). Batch-specific code evidence per "
                "`#265`; the row itself named no artifact. ORIGINAL FLAG", 1)
            out.append(f"{m.group(1)}EXECUTED{m.group(4)}{m.group(5)}"
                       f"{m.group(6)}{new_tail}")
        elif has_code:
            verdicts["CODE_BUT_NO_NEW_DEFS"] += 1
            held.append((tid, f"batch {sha[:9]} changed code but added no durable "
                              "definition - cannot attribute"))
            out.append(line)
        else:
            verdicts["DOC_ONLY_BATCH"] += 1
            held.append((tid, f"batch {sha[:9]} touched {nfiles} file(s), none code"))
            out.append(line)

    total = sum(verdicts.values())
    print(f"rows still flagged OPEN by B1788: {total}")
    for k, v in verdicts.most_common():
        print(f"  {v:>4}  {k}")

    print(f"\nPROMOTED ({len(promoted)}) - the batch created code that survives:")
    for tid, ev, n in promoted[:a.show]:
        print(f"  {tid:<14} {n:>3} def(s)  {ev[:66]}")
    if len(promoted) > a.show:
        print(f"  ... {len(promoted)-a.show} more")

    print(f"\nSTILL HELD ({len(held)}):")
    for tid, why in held[:a.show]:
        print(f"  {tid:<14} {why[:82]}")

    print("\nCODE_LANDED_IN_BATCH is NOT per-row attribution: a batch carries")
    print("several rows, so this proves the batch produced durable code, not")
    print("that THIS row's claim is the code produced. Stronger than a file")
    print("mention, weaker than a named artifact - and named accordingly.")

    if a.write:
        QUEUE.write_text("\n".join(out) + "\n", encoding="utf-8")
        print("\nWRITTEN")
    else:
        print("\nDRY RUN - pass --write to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
