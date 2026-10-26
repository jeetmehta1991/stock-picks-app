"""Print a ticket's WHOLE history - every row whose first cell is its id, bold
or not (S6-B3307, B3139q-r113, L960).

The turn gate scan_ticket_history_unread blocks a close that appended a row to
a ticket whose earlier rows are not in the tool output since the last
compaction; this is the command its message names. A grep for the BOLD id is
not enough: the queue's oldest rows carry an unbolded id, and the B3139q-r113
context pass missed two of them that way. Rows come from queue_state.history,
which shares queue_state.row_id with the gate. If the tool layer persists a
long print to a file and shows a preview, Read that file - the gate counts what
reached the context, and a preview is not the history.

    python scripts/ticket_history.py S6-B1248-LEVER4-GATE-BUDGET [S6-B3306 ...]

Exit 1 when an id has no row, so a mistyped id cannot print an empty history
and pass.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import queue_state  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="print every row of each ticket, bold id or not")
    ap.add_argument("ids", nargs="+", help="ticket ids, e.g. S6-B3306")
    ap.add_argument("--queue", default=None, help="EXECUTION_QUEUE.md path (default: the repo's)")
    a = ap.parse_args(argv)
    empty = 0
    for tid in a.ids:
        rows = queue_state.history(tid, path=a.queue)
        print(f"{tid}: {len(rows)} row(s)")
        for n, ln in rows:
            print(f"{n}:{ln}")
        empty += not rows
    return 1 if empty else 0


if __name__ == "__main__":
    sys.exit(main())
