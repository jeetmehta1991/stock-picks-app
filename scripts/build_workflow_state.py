#!/usr/bin/env python
"""S6-B3120e D1 (owner-approved 2026-09-29 "Approve all recs"): the
workflow-state header - a small state derivation (campaign tickets, engine
state, next mandated action) REBUILT FROM THE LEDGER at every turn boundary
and prepended by the prompt hook beside the compact index, so a tangent meets
the workflow at the TURN BOUNDARY instead of at the close
(output_audit/b3120_optimisation_workflow_deep_audit.md section 5, D1).

Derivation only - no heuristics that invent a campaign: the state IS the
ledger's non-terminal rows (queue_state, last-row-wins) plus the process
table's engine-inflight reading (pyramid_gate's detector, one definition -
L593). Every figure is derived at call time; generated_utc says when.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

OUT = ROOT / "output_audit" / "workflow_state.json"
# S6-B3130a (B3139): a test session points the file copy elsewhere.
# MEASURED - the production copy was the only non-gate output_audit path
# the batch-2 full pyramid moved (output_audit/b3139_pyramid_batch2.out):
# four tests drive this derivation, in-process and through the hook's
# child, and the read-set re-run of one of them rewrote it again, so the
# gate read SUSPECT on every run. Same shape as POSTCONFIG_LANDINGS_PATH.
ENV_OUT = "WORKFLOW_STATE_OUT"
_NONTERMINAL = ("OPEN", "RUNNING", "BLOCKED")


def out_path() -> Path:
    """Where build() writes its file copy: WORKFLOW_STATE_OUT when set,
    else the production output_audit/workflow_state.json."""
    return Path(os.environ.get(ENV_OUT) or OUT)


def build() -> dict:
    """The workflow state, derived fresh. Raises on a broken ledger - the
    CALLER (the hook banner) decides fail-open; a library must not hide it."""
    import queue_state as qs
    import pyramid_gate as pg

    # STATES come from the ledger's ONE reducer (last row wins per distinct
    # ticket - the L794 rule: a lookup is not exempt). Priority and a display
    # head are joined on afterwards from a lightweight scan; they are DISPLAY
    # data only and decide nothing.
    states = qs.tickets()
    pat = re.compile(
        r"^\|\s*\*\*(" + qs.TICKET_ID + r")\*\*\s*\|\s*[^|]*\|\s*(P\d)\s*\|"
        r"\s*(.{0,110})", re.M)
    text = (ROOT / "EXECUTION_QUEUE.md").read_text(
        encoding="utf-8", errors="replace")
    meta: dict[str, tuple[str, str]] = {}
    for m in pat.finditer(text):            # later rows overwrite - same rule
        meta[m.group(1)] = (m.group(2),
                            m.group(3).replace("**", "").strip())
    open_rows = [
        {"id": tid, "state": st,
         "prio": meta.get(tid, ("P?", ""))[0],
         "head": meta.get(tid, ("P?", ""))[1]}
        for tid, st in states.items() if st in _NONTERMINAL]
    open_rows.sort(key=lambda r: (r["prio"], r["state"] != "RUNNING", r["id"]))

    engine = pg._engine_inflight()
    workable = [r for r in open_rows if r["state"] == "OPEN"]
    if engine and engine not in ("none", "unknown"):
        next_action = f"engine run in flight ({engine}) - await its landing; no pyramid beside it (B3108)"
    elif any(r["state"] == "RUNNING" for r in open_rows):
        rid = next(r["id"] for r in open_rows if r["state"] == "RUNNING")
        next_action = f"{rid} is RUNNING - monitor it; detours carry a DETOUR line (Phase 6.2)"
    elif workable:
        top = workable[0]
        next_action = f"work {top['id']} ({top['prio']}): {top['head'][:80]}"
    elif open_rows:
        next_action = ("nothing OPEN; blocked on "
                       + ", ".join(r["id"] for r in open_rows[:3]))
    else:
        next_action = "no non-terminal tickets - consult the owner or the optimisation backlog"

    state = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "engine_inflight": engine,
        "open_tickets": open_rows[:5],
        "n_nonterminal": len(open_rows),
        "next_mandated_action": next_action,
    }
    try:
        out_path().write_text(json.dumps(state, indent=1) + "\n",
                       encoding="utf-8", newline="\n")
    except OSError as e:
        # #122: a degraded output announces itself - the header is the
        # deliverable and still returns, but the missing file copy is said.
        print(f"[workflow_state] state file not written: {e}", file=sys.stderr)
    return state


def banner() -> str:
    """The D1 header the prompt hook prepends. NEVER raises; empty on any
    failure (a broken hook must never block a turn - fail-open like its
    sibling banners, and an empty banner is visible by absence at the close
    where the gates still hold)."""
    try:
        st = build()
        lines = [f"[WORKFLOW STATE (D1, S6-B3120e) - derived {st['generated_utc']}"
                 f"; engine_inflight={st['engine_inflight']}]",
                 f"  NEXT: {st['next_mandated_action']}"]
        for r in st["open_tickets"]:
            lines.append(f"  {r['prio']} {r['state']:8s} {r['id']}: "
                         f"{r['head'][:90]}")
        return "\n".join(lines).encode("ascii", "replace").decode("ascii") + "\n\n"
    except Exception:
        return ""


if __name__ == "__main__":
    print(banner() or "(banner empty - derivation failed)")
