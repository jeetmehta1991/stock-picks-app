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

# S6-B3164 option (a), DISPLAY ONLY: an OPEN row whose reason's LEADING
# clause says it waits on the owner is not the next piece of work - NEXT
# skips it and the banner marks it. MEASURED over the ledger at B3139q-r69k:
# 910 OPEN rows, 848 with a reason cell, 804 distinct leading wordings - so
# the match keys on DECISION-PENDING forms, never on a citation of a ruling
# already made (the scan_owner_decision_taken rule, L586), and reads only
# the first clause, so a later clause about another option (S6-B3164's own
# reason) does not gate a workable row. The six-class vocabulary is
# unchanged: an awaiting-owner CLASS would be a ruling (option (b), L524).
OWNER_PENDING_FORMS = (
    "owner decision:", "owner decision -", "needs your ruling",
    "needs the owner", "needs owner", "needs an owner", "awaiting owner",
    "awaiting the owner", "awaits the owner", "awaiting your",
    "pending approval", "pending the owner", "explicit owner word",
    "owner go")


def awaits_owner(reason: str) -> bool:
    """True when the reason's FIRST clause (up to ';' or '|') names a
    decision pending with the owner."""
    lead = re.split(r"[;|]", (reason or "").lower(), maxsplit=1)[0]
    return any(f in lead for f in OWNER_PENDING_FORMS)


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
    # S6-B3164: each ticket's LAST reason cell (display data, same rule)
    reason: dict[str, str] = {}
    for line in text.splitlines():
        mm = re.match(r"^\|\s*\*\*(" + qs.TICKET_ID + r")\*\*\s*\|", line)
        if mm and "_reason:_" in line:
            reason[mm.group(1)] = line.rsplit("_reason:_", 1)[1].strip().rstrip("|").strip()
    open_rows = [
        {"id": tid, "state": st,
         "prio": meta.get(tid, ("P?", ""))[0],
         "head": meta.get(tid, ("P?", ""))[1],
         "awaits_owner": st == "OPEN" and awaits_owner(reason.get(tid, ""))}
        for tid, st in states.items() if st in _NONTERMINAL]
    open_rows.sort(key=lambda r: (r["prio"], r["state"] != "RUNNING", r["id"]))

    engine = pg._engine_inflight()
    power = pg._power_state()           # S6-B3163: one definition
    workable = [r for r in open_rows
                if r["state"] == "OPEN" and not r["awaits_owner"]]
    gated = [r for r in open_rows if r["awaits_owner"]]
    if engine and engine not in ("none", "unknown"):
        next_action = f"engine run in flight ({engine}) - await its landing; no pyramid beside it (B3108)"
    elif any(r["state"] == "RUNNING" for r in open_rows):
        rid = next(r["id"] for r in open_rows if r["state"] == "RUNNING")
        next_action = f"{rid} is RUNNING - monitor it; detours carry a DETOUR line (Phase 6.2)"
    elif workable:
        top = workable[0]
        next_action = f"work {top['id']} ({top['prio']}): {top['head'][:80]}"
    elif gated:
        next_action = (f"nothing workable OPEN; {len(gated)} OPEN row(s) await "
                       "the owner: " + ", ".join(r["id"] for r in gated[:4]))
    elif open_rows:
        next_action = ("nothing OPEN; blocked on "
                       + ", ".join(r["id"] for r in open_rows[:3]))
    else:
        next_action = "no non-terminal tickets - consult the owner or the optimisation backlog"

    state = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "engine_inflight": engine,
        "power": power,
        "open_tickets": open_rows[:5],
        "n_nonterminal": len(open_rows),
        "next_mandated_action": next_action,
    }
    # S6-B3390 (B3139q-r165): the hook calls build() on every owner message
    # AND every system notification, so the copy is rewritten only when the
    # STATE moved - every field but the derivation stamp. MEASURED at
    # B3139q-r164 (times from the transcript's hook records): a rewrite at
    # 09:24:02Z in a full gate's main pass and one at 09:42:21Z inside its
    # read-set re-run made it SUSPECT, exit 6. The file's stamp is therefore
    # the time the state last CHANGED; the banner still prints this call's
    # own stamp.
    if not _same_state(out_path(), state):
        try:
            out_path().write_text(json.dumps(state, indent=1) + "\n",
                           encoding="utf-8", newline="\n")
        except OSError as e:
            # #122: a degraded output announces itself - the header is the
            # deliverable and still returns, but the missing file copy is said.
            print(f"[workflow_state] state file not written: {e}", file=sys.stderr)
    return state


def _same_state(path: Path, state: dict) -> bool:
    """True when `path` holds `state` in every field but generated_utc. An
    unreadable or absent copy is not the same state - it is written."""
    try:
        prev = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if not isinstance(prev, dict):
        return False
    return ({k: v for k, v in prev.items() if k != "generated_utc"}
            == {k: v for k, v in state.items() if k != "generated_utc"})


def banner() -> str:
    """The D1 header the prompt hook prepends. NEVER raises; empty on any
    failure (a broken hook must never block a turn - fail-open like its
    sibling banners, and an empty banner is visible by absence at the close
    where the gates still hold)."""
    try:
        st = build()
        lines = [f"[WORKFLOW STATE (D1, S6-B3120e) - derived {st['generated_utc']}"
                 f"; engine_inflight={st['engine_inflight']}"
                 f"; power={st.get('power', 'unknown')}]",
                 f"  NEXT: {st['next_mandated_action']}"]
        for r in st["open_tickets"]:
            mark = " [awaits owner]" if r.get("awaits_owner") else ""
            lines.append(f"  {r['prio']} {r['state']:8s} {r['id']}{mark}: "
                         f"{r['head'][:90]}")
        return "\n".join(lines).encode("ascii", "replace").decode("ascii") + "\n\n"
    except Exception:
        return ""


if __name__ == "__main__":
    print(banner() or "(banner empty - derivation failed)")
