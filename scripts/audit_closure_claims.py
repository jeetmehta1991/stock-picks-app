#!/usr/bin/env python
"""S6-B2891 / L819: find ledger rows that assert a CLASS IS CLOSED.

WHY THIS EXISTS. A figure that CONTINUES the work gets acted on by someone and
therefore gets checked. A figure that ENDS it - "1 of 1", "exactly the
incident", "zero collateral", "no siblings" - gets neither, because nothing
downstream depends on it and nobody is waiting for it. The arithmetic is
identical in both directions and only one of them is scrutinised.

MEASURED at B2891 over one session's 58 rows: 3 asserted closure, 2 of the 3
were the same wrong claim repeated, 1 was the row recording the overclaim. So
every genuine closure assertion in that session was wrong.

WHAT IT DOES NOT DO, stated because the limit is the point (L819's own
detection line): it CANNOT tell a measured closure figure from an assumed one -
both are integers. It narrows a large ledger to the handful of rows that make
the claim, so a human can hand-read them. Report what you READ, and cite this
only as the thing that made the reading affordable (L644 addendum).

    python scripts/audit_closure_claims.py                 # whole ledger
    python scripts/audit_closure_claims.py --since S6-B2850
    python scripts/audit_closure_claims.py --json
"""
from __future__ import annotations

import argparse
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "EXECUTION_QUEUE.md"

# A row's own id. Bold-independent per L603/B1969 - 48 real tickets sit in an
# older schema with an unbolded id, and a parser that requires bold silently
# drops them from every count it feeds.
_ROW = re.compile(r"^\|\s*\**\s*(S6-B\d+[a-z]?)\s*\**\s*\|")

# The claim vocabulary. Stems, not conjugations (#239): "closes"/"closed"/
# "closing" all reach the same root.
CLOSURE = re.compile(
    r"clos(?:e|es|ed|ing|ure) the class|class is clos|"
    r"\b1 of 1\b|no historical backlog|zero collateral|"
    r"exactly the incident|no siblings|nothing else breaks the same way",
    re.I)

# A denominator anywhere in the row. Its PRESENCE does not make the claim true;
# its ABSENCE makes the claim unfalsifiable, which is the cheaper thing to spot.
DENOM = re.compile(r"\b\d[\d,]*\s+of\s+\d[\d,]*\b", re.I)


def rows(text: str) -> list[tuple[str, str]]:
    """(ticket_id, row_text) for every ledger row, in file order."""
    out = []
    for line in text.splitlines():
        m = _ROW.match(line)
        if m:
            out.append((m.group(1), line))
    return out


def closure_claims(text: str, since: str | None = None) -> list[dict]:
    """Rows asserting closure, each flagged for whether it names a scope."""
    found = []
    started = since is None
    for tid, line in rows(text):
        if since and tid == since:
            started = True
        if not started:
            continue
        m = CLOSURE.search(line)
        if not m:
            continue
        found.append({
            "ticket": tid,
            "phrase": m.group(0),
            "has_denominator": bool(DENOM.search(line)),
            "excerpt": line[max(0, m.start() - 70):m.end() + 70],
        })
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--since", default=None,
                    help="start at this ticket id (e.g. S6-B2850)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    text = io.open(a.ledger, encoding="utf-8", errors="replace").read()
    all_rows = rows(text)
    hits = closure_claims(text, since=a.since)

    if a.json:
        print(json.dumps({"rows_scanned": len(all_rows),
                          "since": a.since,
                          "claims": hits}, indent=1))
        return 0

    scope = f" since {a.since}" if a.since else ""
    print(f"instrument: scripts/audit_closure_claims.py over {a.ledger}")
    print(f"rows scanned{scope}: {len(all_rows)} total in the ledger")
    print(f"rows asserting CLASS CLOSURE: {len(hits)}")
    no_scope = [h for h in hits if not h["has_denominator"]]
    print(f"  of those, naming NO denominator: {len(no_scope)}"
          "   <- hand-read these first")
    for h in hits:
        flag = "NO-SCOPE" if not h["has_denominator"] else "has N of M"
        print(f"  {h['ticket']:<12} {flag:<10} {h['phrase']!r}")
    print()
    print("This narrows the ledger; it does NOT verify any figure. A measured "
          "closure claim and an assumed one are both integers (L819).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
