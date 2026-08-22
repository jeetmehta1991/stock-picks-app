# -*- coding: utf-8 -*-
"""Which OPEN tickets are about the SAME THING (B1895 / L579).

L578 was found by holding two rows on one subject side by side. Nothing does
that on a 979-row ledger, so this does.

THREE PROBES FAILED BEFORE THIS ONE, and each returned a PLAUSIBLE NUMBER
rather than an obvious error. They are recorded here so the next reader does
not re-run them:

    1. token overlap                 -> 530 "contradictions". The shared words
                                        were the B1794/B1795 stamp every row
                                        carries. The probe measured the stamp.
    2. token overlap, stamp stripped -> 146. A SECOND stamp layer remained.
    3. identifier regex including
       `[A-Z][A-Z0-9_]{4,}`          -> matched GATES, OWNER, LEDGER,
                                        CONFIRMED. This ledger is written in
                                        emphatic ALL-CAPS, so the house style
                                        reads as code.
    4. TRUE identifiers only         -> clean.

**The ledger's own style is what defeats machine reading of it.** Stamped
prose and bold-caps emphasis are both deliberate, both useful to a human, and
both hostile to a tool.

HAND-RUN: python scripts/queue_crossref.py
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

# an identifier must carry an underscore or a .py suffix - a bare ALL-CAPS word
# is emphasis, not code (trap 3)
IDENT = re.compile(r"\b(scan_\w+|check_\w+|[a-z]\w*_\w+(?:\.py)?|\w+\.py)\b")
# tokens that come from the B1794/B1795 stamp rather than the row's subject
NOISE = {"test_bnnn", "_reason", "read_end", "end_to", "no_silent", "not_started"}


def clusters(state: str = "OPEN") -> dict[str, list[str]]:
    """identifier -> the live tickets citing it, for identifiers cited twice+."""
    import queue_state as qs

    lines = (ROOT / "EXECUTION_QUEUE.md").read_text(encoding="utf-8").split("\n")
    last = {t: l for l, t, s in qs.rows()}
    live = sorted(t for t, s in qs.tickets().items() if s == state)

    by = collections.defaultdict(set)
    for t in live:
        for m in IDENT.findall(lines[last[t] - 1]):
            ml = m.lower()
            if ml in NOISE or ml.startswith("test_b") or m.isupper():
                continue
            by[m].add(t)
    return {k: sorted(v) for k, v in by.items() if len(v) > 1}


def main() -> int:
    c = clusters()
    print(f"identifiers cited by more than one OPEN ticket: {len(c)}\n")
    for k, v in sorted(c.items(), key=lambda x: (-len(x[1]), x[0])):
        print(f"  {k:38} {', '.join(v)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
