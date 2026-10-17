#!/usr/bin/env python
"""S6-B3193 (L921 / L925 / #282): test a drafted close against the turn's scan
gates, then STAMP it, so the Stop hook can refuse a post that differs.

    python scripts/probe_close.py <draft.md> [--transcript T.jsonl]
                                  [--stamp-dir DIR] [--no-stamp]

The draft is appended to the transcript IN MEMORY as the turn's final assistant
message, so every gate reading the last block reads the DRAFT - the same input
the Stop hook gives them. Gates that would WRITE on a real close are judged
without writing: the landing and chain-halt gates get the draft as `text`, which
triggers their probe rule (an injected text against the production ledger keeps
the verdict and never writes, S6-B3148 / L910), and the deferral-trigger gate
gets its in-memory `state` seam - otherwise a draft check would record a newly
fired trigger as seen and the real close would never block on it. The only file written is the stamp:
.close_stamps/<turn>.json (git-ignored) - the draft's normalised lines and the
turn they belong to, the uuid of the instruction that opened it.
scan_close_differs_from_tested_draft then refuses a final response that is not
those lines: an edit after a test re-opens the test.

Exit 0 when no gate fires, 1 when any fires, 2 on a usage error (nothing is
stamped then). The stamp is written whether or not gates fire, unless
--no-stamp: a draft whose gates fire is blocked by those gates anyway.
"""
from __future__ import annotations

import argparse
import inspect
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# it judges the POSTED close against the stamp this run writes
SKIP = ("scan_close_differs_from_tested_draft",)
# a matching report on a REAL close marks the ledger record delivered; an
# injected text against the production ledger is their probe rule (S6-B3148)
WRITE_ON_CLOSE = ("scan_undelivered_landing", "scan_chain_halt")


def _deferral_state() -> dict:
    p = ROOT / "output_audit" / "deferral_trigger_state.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="test a drafted close, then stamp it")
    ap.add_argument("draft")
    ap.add_argument("--transcript", default=os.environ.get("TURN_GATE_TRANSCRIPT"))
    ap.add_argument("--stamp-dir", default=None)
    ap.add_argument("--no-stamp", action="store_true")
    a = ap.parse_args(argv)
    if not a.transcript or not Path(a.transcript).exists():
        print("REFUSED: no transcript - pass --transcript or set "
              "TURN_GATE_TRANSCRIPT (the turn and the gates both read it)",
              file=sys.stderr)
        return 2
    draft = Path(a.draft).read_text(encoding="utf-8")
    if not draft.strip():
        print("REFUSED: the draft is empty", file=sys.stderr)
        return 2
    os.environ["TURN_GATE_TRANSCRIPT"] = str(a.transcript)
    import verify_turn_compliance as v
    entries = list(v._read_entries())
    turn = v.turn_anchor(entries)
    if turn is None:
        print("REFUSED: the transcript holds no instruction - no turn to stamp",
              file=sys.stderr)
        return 2
    entries.append({"type": "assistant", "timestamp": "9999-12-31T00:00:00Z",
                    "message": {"role": "assistant",
                                "content": [{"type": "text", "text": draft}]}})
    print(f"transcript entries: {len(entries) - 1} + the draft as the final "
          f"message | turn {turn}")
    # S6-B3199: the check_ wrappers read the module cache, so a scan the Stop
    # hook reaches only through its check_ wrapper reads the draft too
    v._ENTRIES_CACHE = entries
    ran, firing, skipped = 0, [], []
    for name in sorted(n for n in dir(v) if n.startswith("scan_")):
        if name in SKIP:
            continue
        fn = getattr(v, name)
        try:
            params = inspect.signature(fn).parameters
        except (TypeError, ValueError):
            continue
        if not params or next(iter(params)) != "entries":
            skipped.append(name)
            continue
        # S6-B3199: a scan with another REQUIRED argument is called by the
        # Stop hook through its check_ wrapper, which computes that argument
        # (check_unrecorded_miss derives learnings_modified from git) - call
        # the wrapper the same way, never the bare scan with the argument
        # missing (that raised, and the raise read as a firing gate)
        req = [k for k, p in params.items() if k != "entries"
               and p.default is inspect.Parameter.empty
               and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)]
        if req:
            chk = getattr(v, "check_" + name[len("scan_"):], None)
            if chk is None:
                skipped.append(name)
                continue
            try:
                res = chk()
            except Exception as exc:
                firing.append(name)
                print(f"{name}: RAISED in {chk.__name__} {exc!r}")
                continue
            ran += 1
            if res:
                firing.append(name)
                print(f"{name} (via {chk.__name__}): {str(res)[:400]}")
            continue
        kw = {}
        if name in WRITE_ON_CLOSE:               # judge, never write (L910)
            kw = {"text": draft}
        elif name == "scan_deferral_trigger_fired":
            kw = {"state": _deferral_state()}    # judge in memory, never write
        try:
            out = fn(entries, **kw)
        except Exception as exc:
            firing.append(name)
            print(f"{name}: RAISED {exc!r}")
            continue
        ran += 1
        if out and not isinstance(out, tuple):
            firing.append(name)
            first = out[0] if isinstance(out, list) else out
            print(f"{name}: {str(first)[:400]}")
    print(f"gates run: {ran}; firing: {len(firing)}; skipped (not "
          f"entries-first): {len(skipped)}")
    if not a.no_stamp:
        p = v.write_close_stamp(draft, turn, draft=str(a.draft),
                                stamp_dir=a.stamp_dir,
                                extra={"gates_run": ran, "gates_firing": firing})
        print(f"STAMPED {p} - post this draft VERBATIM; any edit re-opens the test")
    return 1 if firing else 0


if __name__ == "__main__":
    sys.exit(main())
