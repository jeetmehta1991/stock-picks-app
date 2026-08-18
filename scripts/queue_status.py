#!/usr/bin/env python
"""B1635 / S6-B1634d - the queue's CURRENT status, without rewriting history.

`EXECUTION_QUEUE.md` APPENDS resolutions rather than restatusing rows, which is
the right call for an audit ledger - every row stays as it was written - but it
makes the raw open-count useless. MEASURED: 49 tickets carry multiple rows and
17 have a resolving row appended after an open one, so a naive scan reports 97
of 225 open when most are closed. That is why this session's pre-sweep triage
read LIVE CODE instead of trusting the queue.

This resolves LAST-ROW-WINS at read time. History is untouched.

Usage:
    python scripts/queue_status.py                # counts by resolved status
    python scripts/queue_status.py --open         # only what is still open
    python scripts/queue_status.py --stale        # rows a later row resolves
"""
from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path

QUEUE = Path("EXECUTION_QUEUE.md")
CLOSED_PREFIXES = ("DONE", "RESOLVED", "CLOSED", "SUPERSEDED", "RETRACTED",
                   "NOTE", "N/A", "REVERTED")
ROW = re.compile(r"^\|\s*\*\*(S6-B\d+\w*)\*\*\s*\|\s*\*{0,2}([^|]*?)\*{0,2}\s*\|", re.M)


def parse(text: str) -> dict[str, list[str]]:
    """ticket -> every status it has carried, in document order."""
    out: dict[str, list[str]] = collections.defaultdict(list)
    for tid, status in ROW.findall(text):
        out[tid].append(status.strip())
    return dict(out)


def is_closed(status: str) -> bool:
    return any(status.upper().startswith(p) for p in CLOSED_PREFIXES)


def resolve(history: dict[str, list[str]]) -> dict[str, str]:
    """LAST row wins - the queue's own convention, made explicit."""
    return {t: v[-1] for t, v in history.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--stale", action="store_true")
    ap.add_argument("--queue", default=str(QUEUE))
    a = ap.parse_args()

    text = Path(a.queue).read_text(encoding="utf-8", errors="ignore")
    hist = parse(text)
    cur = resolve(hist)
    still_open = {t: s for t, s in cur.items() if not is_closed(s)}

    if a.stale:
        stale = {t: v for t, v in hist.items()
                 if len(v) > 1 and is_closed(v[-1])
                 and any(not is_closed(x) for x in v[:-1])}
        print(f"{len(stale)} tickets have an OPEN row that a LATER row resolves "
              f"(history preserved on purpose):")
        for t, v in sorted(stale.items()):
            print(f"   {t:<14} {' -> '.join(v)}")
        return 0

    if a.open:
        print(f"{len(still_open)} tickets OPEN by last-row-wins "
              f"(of {len(cur)} total):")
        for t, s in sorted(still_open.items()):
            print(f"   {t:<14} {s}")
        return 0

    print(f"tickets: {len(cur)} | rows: {sum(len(v) for v in hist.values())}")
    print(f"  OPEN   {len(still_open)}")
    print(f"  CLOSED {len(cur) - len(still_open)}")
    naive = sum(1 for v in hist.values() for s in v if not is_closed(s))
    print(f"\nA naive row-scan would report {naive} open rows - "
          f"{naive - len(still_open)} of them already superseded. Use this "
          f"resolver, not the raw count (L489).")
    by = collections.Counter(s.split(" -")[0].split("(")[0].strip()
                             for s in still_open.values())
    print("\nopen by status:", dict(by.most_common()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
