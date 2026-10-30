#!/usr/bin/env python
"""S6-B3346 (B3139q-r143): A PENDING-DECISION CLAIM NAMING A TICKET THE
LEDGER SHOWS TERMINAL.

WHY. The owner ruled the pyramid gate's stamp demotion on 2026-09-30
(S6-B3139k, EXECUTED at B3139q-r13: DEMOTION STAYS OFF), yet
scripts/pyramid_gate.py's docstring kept the demotion pending, quoting
'until the owner rules on the demotion (S6-B3130a, ...)', and a row said
'the demotion half stays with the owner's S6-B3130a ruling' - S6-B3330's,
at B3139q-r131 - with S6-B3130a EXECUTED. A sentence saying a decision is still owed, naming the
ticket that carries it, is checkable against the ledger: if that ticket is
terminal, the sentence is stale.

WHAT. `claims(text)` finds the pending-decision phrases below followed,
within one clause, by a ticket id; quoted spans are stripped first, so a row
QUOTING the defect (S6-B3346's own) is a mention, not a use (B1738).
`stale(text, states)` keeps the claims whose ticket is EXECUTED or DROPPED.
`live_surfaces()` reads what is still asserted today: the live code under
scripts/ and backtest/ that git tracks (a new file is read once it is
staged; tests and the gate corpus are fixtures), the
governing docs (runbook, CHECKLIST, CLAUDE.md, the skill), and the LAST row
of every non-terminal ticket. The append-log's earlier rows, LEARNINGS, the
campaign log, archive/ and output_audit/ are dated records - true on their
date - and are not read.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TERMINAL = ("EXECUTED", "DROPPED")
_ID = r"S6-B[0-9]+[A-Za-z0-9-]*"
PENDING = re.compile(
    r"(until the owner rules|pending the owner|stays with the owner|"
    r"awaits the owner|awaiting the owner|waits on the owner|"
    r"subject to the owner|pending (?:an |the )?owner(?:'s)? (?:ruling|decision|word))"
    r"[^.;\n]{0,80}?(" + _ID + r")", re.I)
# a quoted span is a MENTION: 'single', "double" and the typographic pairs.
# A single quote opens or closes a span only at a word boundary, so the
# apostrophe of "owner's" is never a quote - MEASURED on the first draft,
# which paired that apostrophe with a later one and blanked the very claim
# S6-B3330's row makes, reading 0 where the live repo held 1 (L687). A span
# never crosses a line: a quotation wrapped over two lines is NOT a mention,
# so a false alarm (loud) is preferred to blanking a real claim (silent, L596).
# The typographic pairs are built with chr() - runtime code stays ASCII (C1).
_LS, _RS, _LD, _RD = chr(0x2018), chr(0x2019), chr(0x201C), chr(0x201D)
_QUOTED = re.compile(r"(?<![A-Za-z0-9])'(?:[^'\n]|(?<=[A-Za-z0-9])'(?=[A-Za-z0-9])){1,400}?"
                     r"'(?![A-Za-z0-9])|\"[^\"\n]{1,400}\"|"
                     + _LS + "[^" + _RS + r"\n]{1,400}" + _RS + "|"
                     + _LD + "[^" + _RD + r"\n]{1,400}" + _RD)
GOVERNING_DOCS = ("STRATEGY_OPTIMISATION_PLAN.md", "CHECKLIST.md", "CLAUDE.md",
                  ".claude/skills/execution-discipline/SKILL.md")
FIXTURE_PARTS = ("backtest/tests/", "scripts/gate_incident_corpus.py")


def _unquote(text: str) -> str:
    # blank in place so offsets and line numbers survive (L582)
    return _QUOTED.sub(lambda m: " " * len(m.group(0)), text)


def claims(text: str) -> list:
    """[(ticket, line_no, phrase)] for every pending-decision claim."""
    t = _unquote(text)
    return [(m.group(2), t.count("\n", 0, m.start()) + 1, m.group(0))
            for m in PENDING.finditer(t)]


def stale(text: str, states: dict) -> list:
    return [c for c in claims(text) if states.get(c[0]) in TERMINAL]


def live_surfaces(root: Path = ROOT) -> list:
    """[(label, text)] - what is still asserted today."""
    if str(root / "scripts") not in sys.path:
        sys.path.insert(0, str(root / "scripts"))
    out = []
    files = subprocess.run(["git", "ls-files", "scripts/*.py", "backtest/*.py"],
                           cwd=root, capture_output=True, text=True,
                           check=True).stdout.split()
    for f in [x for x in files if not x.startswith(FIXTURE_PARTS)] + list(GOVERNING_DOCS):
        p = root / f
        if p.exists():
            out.append((f, p.read_text(encoding="utf-8", errors="replace")))
    import queue_state as qs
    states = qs.tickets(root / "EXECUTION_QUEUE.md")
    last = {}
    for ln in (root / "EXECUTION_QUEUE.md").read_text(
            encoding="utf-8", errors="replace").splitlines():
        rid = qs.row_id(ln)
        if rid:
            last[rid] = ln
    for tid, ln in last.items():
        if states.get(tid) not in TERMINAL:
            out.append((f"EXECUTION_QUEUE.md last row of {tid}", ln))
    return out


def findings(root: Path = ROOT) -> list:
    if str(root / "scripts") not in sys.path:
        sys.path.insert(0, str(root / "scripts"))
    import queue_state as qs
    states = qs.tickets(root / "EXECUTION_QUEUE.md")
    return [(label, ln, tid, states.get(tid), phrase)
            for label, text in live_surfaces(root)
            for tid, ln, phrase in stale(text, states)]


if __name__ == "__main__":
    import argparse
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    found = findings()
    for f in found:
        print(f"STALE PENDING CLAIM: {f[0]}:{f[1]} names {f[2]} ({f[3]}) - {f[4]!r}")
    print(f"stale_pending_claims={len(found)}")
    sys.exit(1 if found else 0)
