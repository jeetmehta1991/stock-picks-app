"""S6-B3135 (B3135): the ONE reader of Phase 1B roster membership.

WHY. The owner asked (2026-09-29): "Only 15 admitted strategies in phase 1B
roster? ... I believe we have more." He was right. PHASE_1B_ROSTER.md holds
31 distinct deployable strategies - 7 graded funnel cells + 15 owner-ruled
Step-2 admissions (22 longs) + 9 distinct short mirrors - but three consumers
each read a DIFFERENT partial set: the status view counted the admissions
file only (15) and put the other 16 in work lanes; the launch gate parses
one rendered line of the roster (18 names); the roster's own mirror roll-up
summed the funnel cells only. A set with three readers has three meanings.

WHAT. members() returns one typed record per roster strategy, built from the
roster's own two sources - output_audit/b1453_phase_1b_roster.json (the
funnel's kept cells and their mirror resolution, written by
build_phase_1b_roster.py) and output_audit/phase_1b_step2_admissions.json
(the owner-ruled admissions) - with admission mirrors resolved by
build_phase_1b_roster.mirror_status, the SAME classifier the roster document
renders with (one definition, L593). Any unreadable input RAISES: a reader
of a closure set must never return a smaller set because a file was missing
(L642).

ROLES (a strategy can hold more than one - xs_momentum_bottom_decile_short
mirrors a funnel cell AND an admission):
  FUNNEL_CELL       graded 3-cube funnel cell (a long)
  STEP2_ADMISSION   owner-ruled Step-2 admission (a long)
  FUNNEL_MIRROR     registered short mirror of a funnel cell
  ADMISSION_MIRROR  registered short mirror of an admission
  DUAL_SELF         a funnel cell whose own short branch is its mirror
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SIDECAR = Path("output_audit") / "b1453_phase_1b_roster.json"
ADMISSIONS = Path("output_audit") / "phase_1b_step2_admissions.json"
# S6-B3135 (B3139, council): the owner's ruling closed the roster AS IT
# STOOD; this tracked file freezes those names so a later re-score or
# regeneration that drops one from the derived records cannot reopen it.
FROZEN = Path("output_audit") / "phase1b_closed_set_frozen.json"
LONG_ROLES = ("FUNNEL_CELL", "STEP2_ADMISSION")
MIRROR_ROLES = ("FUNNEL_MIRROR", "ADMISSION_MIRROR")


def members(root=None, mirror_status=None) -> dict:
    """{strategy: {"strategy", "roles": [...], "parents": {role: [...]}}}.
    `mirror_status` is injectable for tests; default is the roster's own."""
    root = Path(root) if root is not None else REPO
    roster = json.loads((root / SIDECAR).read_text(encoding="utf-8"))
    adm = json.loads((root / ADMISSIONS).read_text(encoding="utf-8"))
    if mirror_status is None:
        sp = str(REPO / "scripts")
        if sp not in sys.path:
            sys.path.insert(0, sp)
        from build_phase_1b_roster import mirror_status  # noqa: WPS433
    out: dict = {}

    def add(name, role, parent=None):
        rec = out.setdefault(name, {"strategy": name, "roles": [], "parents": {}})
        if role not in rec["roles"]:
            rec["roles"].append(role)
        ps = rec["parents"].setdefault(role, [])
        if parent and parent not in ps:
            ps.append(parent)

    cells = roster.get("roster")
    if not isinstance(cells, list):
        raise ValueError(f"{SIDECAR}: no 'roster' list - refusing a partial set")
    for r in cells:
        s = r["strategy"]
        add(s, "FUNNEL_CELL")
        ms, mn = r.get("mirror_status"), r.get("mirror")
        if ms == "REGISTERED" and mn:
            add(mn, "FUNNEL_MIRROR", s)
        elif ms == "DUAL-SELF":
            add(s, "DUAL_SELF", s)
    rows = adm.get("admissions")
    if not isinstance(rows, list):
        raise ValueError(f"{ADMISSIONS}: no 'admissions' list - refusing a partial set")
    for a in rows:
        s = a.get("strategy")
        if not s:
            raise ValueError(f"{ADMISSIONS}: an admission without a strategy")
        add(s, "STEP2_ADMISSION")
        ms, mn = mirror_status(s)
        if ms == "REGISTERED" and mn:
            add(mn, "ADMISSION_MIRROR", s)
    return out


def frozen_closed_set(root=None) -> set:
    """The names frozen at the owner's 2026-09-29 ruling (FROZEN). RAISES
    when the file is absent, unreadable or carries no names - a closure
    set must never read smaller because a file went missing (L642)."""
    root = Path(root) if root is not None else REPO
    doc = json.loads((root / FROZEN).read_text(encoding="utf-8"))
    names = doc.get("names") if isinstance(doc, dict) else None
    if not isinstance(names, list) or not names:
        raise ValueError(f"{FROZEN}: no frozen names - refusing an empty closure")
    return {str(n) for n in names}


def removed_since_freeze(root=None, mem: dict | None = None) -> list:
    """Frozen names the DERIVED membership no longer holds - each stays
    closed (the gate unions FROZEN) and is the owner's to rule on; the
    roster renders the list. [] when nothing moved."""
    mem = members(root) if mem is None else mem
    return sorted(frozen_closed_set(root) - set(mem))


def summary(mem: dict) -> dict:
    """The roster's headline arithmetic. A short that is itself a long cell
    (DUAL_SELF) is counted once, as the long."""
    longs = {n for n, r in mem.items() if set(LONG_ROLES) & set(r["roles"])}
    shorts = {n for n, r in mem.items()
              if set(MIRROR_ROLES) & set(r["roles"]) and n not in longs}
    return {"funnel_cells": sum("FUNNEL_CELL" in r["roles"] for r in mem.values()),
            "step2_admissions": sum("STEP2_ADMISSION" in r["roles"] for r in mem.values()),
            "mirrors": len(shorts), "long": len(longs), "short": len(shorts),
            "total": len(longs | shorts)}


def roster_status(name: str, mem: dict) -> str | None:
    """The status-view label a roster member carries when it is not a Step-2
    admission: a graded funnel cell is IN-ROSTER-FUNNEL (terminal - on the
    roster, closed like an admission); a policy mirror is IN-ROSTER-MIRROR
    (NOT terminal - ungraded, and the owner scheduled Step 2 on the short
    legs, S6-B2420). None for a non-member."""
    r = mem.get(name)
    if r is None:
        return None
    if "FUNNEL_CELL" in r["roles"]:
        return "IN-ROSTER-FUNNEL"
    if set(MIRROR_ROLES) & set(r["roles"]):
        return "IN-ROSTER-MIRROR"
    return None


if __name__ == "__main__":
    m = members()
    print(json.dumps(summary(m), indent=1))
    for n in sorted(m):
        print(f"  {n:48s} {','.join(m[n]['roles'])}  parents={m[n]['parents']}")
