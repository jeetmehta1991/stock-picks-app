#!/usr/bin/env python
"""B1776: re-derive the numeric claim in every open ticket before working it.

**A ticket is a claim about the world at the moment it was written.** This queue
carries 646 tickets over ~95 batches in 48 hours; several open ones describe
states that later work already changed. Working from them wastes attention on
problems that no longer exist, and - worse - a stale count repeated in a
response is a Truth-Standard violation with a paper trail that looks like
evidence.

Measured precedents, each found by re-deriving rather than trusting:
    S6-B1702d  "11 gates unwired"          -> 0 of 43
    S6-B1767d  "64 markers in 22 lists"    -> 67 in 19, of which 17 invert
    S6-B1719e  "4 hooks remain"            -> all 4 built and wired
    S6-B1766a  "vocabulary unruled"        -> ruled and migrated
    S6-B1712c  "14 uncorroborated"         -> matcher replaced underneath it

This script extracts every NUMERIC claim from open tickets and prints it beside
a freshly measured value where one is derivable, so the reader can see which
tickets still describe the world.

HAND-RUN: python scripts/audit_ticket_staleness.py [--all]
"""
from __future__ import annotations

import argparse
import ast
import inspect
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

LIVE = ("OPEN", "BLOCKED", "DEFERRED", "RUNNING")
ROW = re.compile(
    r"^\|\s*\*\*(S6-[A-Za-z0-9-]+)\*\*\s*\|\s*\*\*([A-Z-]+)\*\*\s*\|\s*(\S*)\s*\|(.*)$")

# claims we can re-derive automatically, as (regex, prober-name)
PROBES: dict[str, callable] = {}


def probe(name):
    def deco(fn):
        PROBES[name] = fn
        return fn
    return deco


@probe("scan_ gates with no injectable seam")
def _seamless():
    import verify_turn_compliance as tg
    out = []
    for n, f in vars(tg).items():
        if not (n.startswith("scan_") and callable(f) and hasattr(f, "__code__")
                and f.__module__ == tg.__name__):
            continue
        ps = inspect.signature(f).parameters
        if not [k for k in ps if k != "entries"
                and ps[k].kind == inspect.Parameter.KEYWORD_ONLY]:
            out.append(n)
    return len(out), sorted(out)


@probe("gate functions never referenced outside their own def")
def _unwired():
    import verify_turn_compliance as tg
    src = (ROOT / "scripts" / "verify_turn_compliance.py").read_text(encoding="utf-8")
    out = [n for n, f in vars(tg).items()
           if n.startswith(("scan_", "check_")) and callable(f)
           and hasattr(f, "__code__") and f.__module__ == tg.__name__
           and len(re.findall(rf"\b{re.escape(n)}\b", src)) <= 1]
    return len(out), sorted(out)


@probe("ALL-CAPS marker lists")
def _lists():
    src = (ROOT / "scripts" / "verify_turn_compliance.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id.isupper():
            try:
                v = ast.literal_eval(node.value)
            except Exception:
                continue
            if isinstance(v, (tuple, list, set)) and v and \
                    all(isinstance(x, str) for x in v):
                names.append(node.targets[0].id)
    return len(names), sorted(names)


@probe("queue classes outside the ruled vocabulary")
def _vocab():
    q = (ROOT / "EXECUTION_QUEUE.md").read_text(encoding="utf-8")
    seen = set(re.findall(
        r"^\|\s*\*\*S6-[A-Za-z0-9-]+\*\*\s*\|\s*\*\*([A-Z-]+)\*\*\s*\|", q, re.M))
    bad = sorted(seen - set(LIVE) - {"DONE", "DROPPED"})
    return len(bad), bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true",
                    help="list every open ticket carrying a number")
    a = ap.parse_args()

    print("FRESHLY MEASURED VALUES (what the world says today)\n")
    for label, fn in PROBES.items():
        try:
            n, detail = fn()
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR {label}: {type(exc).__name__}: {exc}")
            continue
        shown = ", ".join(detail[:6]) + (" ..." if len(detail) > 6 else "")
        print(f"  {n:>4}  {label}")
        if detail:
            print(f"        {shown}")

    q = (ROOT / "EXECUTION_QUEUE.md").read_text(encoding="utf-8")
    latest = {}
    for line in q.splitlines():
        m = ROW.match(line)
        if m:
            latest[m.group(1)] = (m.group(2), m.group(3), m.group(4))
    live = {k: v for k, v in latest.items() if v[0] in LIVE}
    numeric = {k: v for k, v in live.items() if re.search(r"\b\d+\b", v[2])}

    print(f"\nOPEN tickets: {len(live)} | carrying a NUMBER: {len(numeric)}")
    print("Each number below is a claim about a past moment. Re-derive before "
          "acting on it.\n")
    if a.all:
        for tid, (c, p, d) in sorted(numeric.items()):
            nums = re.findall(r"\b\d+\b", d)[:6]
            txt = re.sub(r"\s+", " ", re.sub(r"[*_`]", "", d)).strip()
            print(f"  {tid:<14} {c:<8} numbers={nums}")
            print(f"      {txt[:110]}")
    else:
        print("  (pass --all to list them)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
