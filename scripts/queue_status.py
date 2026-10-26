#!/usr/bin/env python
"""B1635 / S6-B1634d - the queue's CURRENT status, without rewriting history.

`EXECUTION_QUEUE.md` APPENDS resolutions rather than restatusing rows, which is
the right call for an audit ledger - every row stays as it was written - but it
makes the raw open-count useless. MEASURED: 49 tickets carry multiple rows and
17 have a resolving row appended after an open one, so a naive scan reports 97
of 225 open when most are closed. That is why this session's pre-sweep triage
read LIVE CODE instead of trusting the queue.

This resolves LAST-ROW-WINS at read time. History is untouched.

S6-B3312 (B3139q-r115): it now reads rows through queue_state, the reducer
that superseded it (B1795). MEASURED before: its own bold-only pattern
missed 158 of 2749 ticket ids (every dashed id, LEVER4 and S6-B1250 among
them), and its closed-state list predated the six classes (B1784), so it
reported OPEN 2591 / CLOSED 0 - every EXECUTED and DROPPED ticket open. The
terminal set is queue_state.TERMINAL; the queue's unbolded legacy rows carry
no state cell and are DISCLOSED (queue_state.unparsed), never counted.

Usage:
    python scripts/queue_status.py                # counts by resolved status
    python scripts/queue_status.py --open         # only what is still open
    python scripts/queue_status.py --stale        # rows a later row resolves
"""
from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import queue_state  # noqa: E402

QUEUE = Path("EXECUTION_QUEUE.md")


def parse(path) -> dict[str, list[str]]:
    """ticket -> every state it has carried, in file order - read through
    queue_state.rows (S6-B3312), never a pattern of this module's own."""
    out: dict[str, list[str]] = collections.defaultdict(list)
    for _, tid, state in queue_state.rows(path):
        out[tid].append(state)
    return dict(out)


def is_closed(status: str) -> bool:
    return status in queue_state.TERMINAL


def resolve(history: dict[str, list[str]]) -> dict[str, str]:
    """LAST row wins - the queue's own convention, made explicit."""
    return {t: v[-1] for t, v in history.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--stale", action="store_true")
    ap.add_argument("--queue", default=str(QUEUE))
    a = ap.parse_args()

    hist = parse(a.queue)
    skipped = queue_state.unparsed(a.queue)
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
    print(f"  (+ {len(skipped)} ids in unbolded legacy rows with no state cell - "
          "disclosed, not counted; queue_state.unparsed)")
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
