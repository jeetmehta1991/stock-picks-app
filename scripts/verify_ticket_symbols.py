#!/usr/bin/env python
"""B1779: does SYMBOL-level verification catch what BATCH-level missed?

The council's Contrarian set the test: *"ask what test it ran to prove
symbol-level catches what batch-level missed - if the answer is 'I reasoned
about it', that's the same failure reproducing inside the fix."* So this script
MEASURES the delta rather than asserting it.

THE METHOD (the Executor's, with one correction).
Build a symbol INDEX by `ast.parse`-ing every project .py, then extract
candidate identifiers from ticket text and INTERSECT with the index. The
intersection is the filter - an English phrase does not survive it - so no regex
has to be clever.

THE CORRECTION. The Executor also wanted `git log -S <symbol>` to prove the
symbol was introduced ON OR BEFORE the row's claimed batch. **B1777 disproved
that assumption**: `cfg_swing_length` landed at B1624 on a row claiming B1620,
and `scan_postfix_recheck` at B1602 on a row claiming B1601. Requiring
introduction <= claimed batch would mark CORRECT work unverified. Batch
attribution is exactly the thing we cannot trust, so symbol existence is checked
against HEAD, not against the batch.

WHAT THIS DOES NOT PROVE, stated up front because the Contrarian is right about
it: a symbol existing and being referenced is WEAKER than most ticket claims.
`scan_x blocks y` is not proven by finding `scan_x` next to a call site - only
by running it. **SYMBOL_MISSING is a strong negative; SYMBOL_PRESENT is a
triage pass, not a verification.** The verdict names are chosen to keep that
distinction visible.

HAND-RUN: python scripts/verify_ticket_symbols.py [--csv out.csv]
"""
from __future__ import annotations

import argparse
import ast
import collections
import csv
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

# three extraction lanes, none of them free-text
BACKTICK = re.compile(r"`([^`]{3,60})`")
SNAKE = re.compile(r"\b([a-z][a-z0-9]*(?:_[a-z0-9]+){1,})\b")
PYPATH = re.compile(r"\b((?:scripts|backtest)[/\\][\w/\\.]+\.py)\b")

ROW = re.compile(
    r"^\|\s*\*\*(S6-[A-Za-z0-9-]+)\*\*\s*\|\s*\*\*([A-Z-]+)\*\*\s*\|\s*(\S*)\s*\|(.*)$")


def symbol_index() -> tuple[dict[str, str], set[str]]:
    """Every def/class/module-level assignment in the project, name -> file."""
    idx: dict[str, str] = {}
    files: set[str] = set()
    for p in list((ROOT / "scripts").glob("*.py")) + \
            list((ROOT / "backtest").rglob("*.py")):
        rel = p.relative_to(ROOT).as_posix()
        files.add(rel)
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                idx.setdefault(node.name, rel)
            elif isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        idx.setdefault(t.id, rel)
            # B1779b: a "symbol" in a ticket is very often a REGISTRY KEY or a
            # CONFIG KEY, not a Python name - `regime_flip` and `next_pivot_target`
            # are exit-registry strings; `tail_n` and `age_bars_max` are grid dict
            # keys. Indexing only def/class names made all of those look MISSING,
            # which is how a 105-row "finding" turned out to be ~all false.
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                v = node.value.strip()
                if 3 < len(v) <= 60 and re.fullmatch(r"[A-Za-z0-9_.\-/]+", v or ""):
                    idx.setdefault(v, rel)
        idx.setdefault(p.name, rel)          # bare filename, e.g. "screener.py"
    return idx, files


def candidates(text: str) -> set[str]:
    t = re.sub(r"[*_]{1,2}", "", text)
    out = set()
    for m in BACKTICK.finditer(text):
        out.add(m.group(1).strip().strip("()"))
    out |= set(SNAKE.findall(t))
    return {c for c in out if c and len(c) > 3}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv")
    ap.add_argument("--show", type=int, default=14)
    a = ap.parse_args()

    idx, files = symbol_index()
    print(f"symbol index: {len(idx)} names across {len(files)} files\n")

    q = (ROOT / "EXECUTION_QUEUE.md").read_text(encoding="utf-8")
    latest: dict[str, tuple[str, str, str]] = {}
    for line in q.splitlines():
        m = ROW.match(line)
        if m:
            latest[m.group(1)] = (m.group(2), m.group(3), m.group(4))

    rows, tally = [], collections.Counter()
    for tid, (cls, prio, desc) in sorted(latest.items()):
        cands = candidates(desc)
        paths = set(PYPATH.findall(desc))
        hits = sorted(c for c in cands if c in idx)
        miss = sorted(c for c in cands if c not in idx and "_" in c)
        bad_paths = sorted(p for p in paths if p not in files)

        if not cands and not paths:
            v = "NO_CLAIM"          # nothing checkable was named
        elif bad_paths or (miss and not hits):
            v = "SYMBOL_MISSING"    # STRONG negative - the named thing is absent
        elif hits or paths:
            v = "SYMBOL_PRESENT"    # triage pass ONLY - see the module docstring
        else:
            v = "NO_CLAIM"
        tally[f"{cls}/{v}"] += 1
        rows.append(dict(ticket=tid, cls=cls, verdict=v,
                         hits=";".join(hits[:4]), missing=";".join(miss[:4]),
                         bad_paths=";".join(bad_paths[:2]),
                         desc=re.sub(r"\s+", " ", re.sub(r"[*_`]", "", desc))[:110]))

    print("verdict by current class:")
    for k, n in sorted(tally.items()):
        print(f"  {n:>4}  {k}")

    print("\n--- THE DELTA THE CONTRARIAN ASKED FOR ---")
    done = [r for r in rows if r["cls"] == "DONE"]
    closed = [r for r in rows if r["cls"] == "CLOSED"]
    dmiss = [r for r in done if r["verdict"] == "SYMBOL_MISSING"]
    cmiss = [r for r in closed if r["verdict"] == "SYMBOL_MISSING"]
    print(f"  DONE rows   : {len(done):>4}  of which SYMBOL_MISSING: {len(dmiss)}")
    print(f"  CLOSED rows : {len(closed):>4}  of which SYMBOL_MISSING: {len(cmiss)}")
    print(f"\n  {len(cmiss)} rows passed BATCH-level verification (CLOSED) while naming")
    print("  a symbol that does not exist. Those are what symbol-level adds.")
    if not cmiss:
        print("  ZERO - symbol-level found nothing batch-level missed among CLOSED "
              "rows.\n  On this evidence it is a TRIAGE aid, not a stronger gate.")

    for r in (cmiss + dmiss)[:a.show]:
        print(f"   {r['ticket']:<14} {r['cls']:<7} missing={r['missing'][:44]:<44} "
              f"{r['desc'][:44]}")

    if a.csv and rows:
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"\nwrote {a.csv} ({len(rows)} rows)")

    print("\nSYMBOL_PRESENT IS NOT VERIFICATION. A symbol existing next to a call")
    print("site does not prove the ticket's claim ('X blocks Y') - only running it")
    print("does. SYMBOL_MISSING is the strong signal here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
