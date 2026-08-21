#!/usr/bin/env python
"""The single canonical reader of EXECUTION_QUEUE.md ticket state.

B1795. **The ledger is an APPEND LOG, not a table of tickets.** Closing a
ticket appends a new row rather than editing the old one, so 81 ticket ids
carry two or more rows and 69 of those sit in CONTRADICTORY states:

    | **S6-B1500d** | **OPEN**     | P2 | **MED**    | Reconcile n=356 ... |
    | **S6-B1500d** | **EXECUTED** | -  | **CLOSED** | Holdout n MEASURED = 147 ... |

Same ticket. Both rows live. 57 ids are EXECUTED AND OPEN at once.

**Every queue count reported this session counted ROWS while calling them
TICKETS** - 823 rows vs 721 tickets. That is the structural cause of the
arithmetic the owner caught by addition, and it silently violates the owner's
"I want mutually exclusive groups" ruling at the DATA level even after the
vocabulary was made exclusive at the LABEL level.

A ticket's state is the state of its LAST row. That invariant is verified, not
assumed: `audit()` reports any id whose terminal row is not its last, and the
count is 0 at B1795.

Import `state()` for counts. Do not re-implement this parse - the whole point
is that there is one reader.
"""
from __future__ import annotations

import collections
import pathlib
import re

QUEUE = pathlib.Path(__file__).resolve().parents[1] / "EXECUTION_QUEUE.md"

CLASSES = ("EXECUTED", "DROPPED", "BLOCKED", "DEFERRED", "OPEN", "RUNNING")
TERMINAL = ("EXECUTED", "DROPPED")

_ROW = re.compile(r"^\|\s*\*\*(S6-[A-Za-z0-9-]+)\*\*\s*\|\s*\*\*([A-Z-]+)\*\*")


def rows(path: pathlib.Path | str | None = None) -> list[tuple[int, str, str]]:
    """Every ledger row as (line_no, ticket_id, state) in file order."""
    p = pathlib.Path(path) if path else QUEUE
    out = []
    with p.open(encoding="utf-8") as fh:
        for n, ln in enumerate(fh, 1):
            m = _ROW.match(ln)
            if m:
                out.append((n, m.group(1), m.group(2)))
    return out


def tickets(path=None) -> dict[str, str]:
    """ticket id -> state, LAST ROW WINS. This is the ledger's real content."""
    last: dict[str, str] = {}
    for _, tid, st in rows(path):
        last[tid] = st
    return last


def state(path=None) -> collections.Counter:
    """Counts per class, per DISTINCT TICKET. The only figure fit to quote."""
    return collections.Counter(tickets(path).values())


def audit(path=None) -> dict[str, object]:
    """Structural health of the ledger. Everything here is measured, not assumed."""
    rs = rows(path)
    by_id = collections.defaultdict(list)
    for n, tid, st in rs:
        by_id[tid].append((n, st))
    dups = {k: v for k, v in by_id.items() if len(v) > 1}
    contra = {k: v for k, v in dups.items() if len({s for _, s in v}) > 1}
    # the invariant last-row-wins depends on: a terminal row is never followed
    # by a non-terminal one for the same id.
    reopened = {k: v for k, v in dups.items()
                if any(s in TERMINAL for _, s in v) and v[-1][1] not in TERMINAL}
    off = {s for _, _, s in rs} - set(CLASSES)
    return {
        "rows": len(rs),
        "tickets": len(by_id),
        "duplicated_ids": len(dups),
        "contradictory_ids": len(contra),
        "terminal_not_last": len(reopened),
        "off_vocabulary": sorted(off),
    }


def main() -> int:
    a = audit()
    print(f"EXECUTION_QUEUE.md  {a['rows']} rows -> {a['tickets']} distinct tickets")
    print(f"  duplicated ids      : {a['duplicated_ids']}")
    print(f"  contradictory state : {a['contradictory_ids']}  "
          f"(append-log closure - expected, not a defect)")
    print(f"  terminal-not-last   : {a['terminal_not_last']}  "
          f"(MUST be 0 for last-row-wins to hold)")
    print(f"  off-vocabulary      : {a['off_vocabulary'] or 'none'}")
    print()
    st = state()
    for k in CLASSES:
        print(f"   {st.get(k, 0):>4}  {k}")
    print(f"   {sum(st.values()):>4}  TOTAL distinct tickets")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
