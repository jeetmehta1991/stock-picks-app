#!/usr/bin/env python
"""S6-B3353 (B3139q-r142): THE TWO LEGS OF A STEP-2 VERDICT, RECORDED BY THE
READER THAT GIVES IT.

WHY. The owner asked 2026-10-29T13:14:30Z, verbatim 'Why wasnt breath step
followed if all runbook workflow is mechanically enforced?'. The 2026-10-28
runbook census classes 'every per-strategy campaign has two legs' and 'every
campaign runs the breadth leg or waives it' TEXT-PIN-ONLY, and 'no campaign
closes while a mandatory leg is unrun' UNENFORCED: only breadth_step2_read.py
asked for a leg, and only the breadth one. A FAIL could be read with no word
on the other leg (L975: the LEVER4 pivot_r1_breakout arm, FAIL 5 of 6 with
neither leg named).

WHAT. A leg is one of three states, each carrying what proves it:
  ran      - evidence: the artifact or record that ran it;
  waived   - word: the owner's words, quoted by a row of the cited ticket
             (scripts/owner_word.py);
  not_run  - ticket: the ticket that decides it, which must have a row.
A Step-2 reader takes both legs before it reads anything, records them in its
artifact, and a negative verdict with a leg not run reads 'leg negative; <leg>
leg NOT RUN', never a strategy failure (#299). The closure reader
(build_strategy_status.load_owner_closures) asks the same of every closure
after the grandfathered set.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEGS = ("depth", "breadth")
STATES = ("ran", "waived", "not_run")


def leg_refusals(name: str, rec, *, queue=None) -> list:
    """[] when `rec` is a proven leg; else one refusal naming what is missing.
    Fails CLOSED on every absent part (L642)."""
    door = f"{name} leg (S6-B3353)"
    if not isinstance(rec, dict) or rec.get("state") not in STATES:
        return [f"REFUSED ({door}): no {name} leg - state one of {', '.join(STATES)}"]
    st = rec["state"]
    if st == "ran":
        if not str(rec.get("evidence") or "").strip():
            return [f"REFUSED ({door}): ran, with no evidence - name the artifact or "
                    "record that ran it"]
        return []
    if st == "waived":
        if str(ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(ROOT / "scripts"))
        import owner_word as _ow
        return [f"{r} - a waived leg carries the owner's recorded words"
                for r in _ow.refusals(rec.get("word"), door=door, queue=queue)]
    ticket = str(rec.get("ticket") or "").strip()
    if not ticket:
        return [f"REFUSED ({door}): not run, with no ticket - name the ticket that "
                "decides it"]
    if str(ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(ROOT / "scripts"))
    import owner_word as _ow
    import queue_state as _qs
    try:
        # the ledger owner_word reads, so one seam (owner_word.QUEUE) moves both
        rows = _qs.history(ticket, path=str(queue or _ow.QUEUE))
    except Exception as exc:  # noqa: BLE001 - an unread ledger refuses (L642)
        return [f"REFUSED ({door}): the ledger could not be read ({type(exc).__name__})"]
    if not rows:
        return [f"REFUSED ({door}): not run under {ticket}, which has no row - record "
                "the decision on its ticket first"]
    return []


def legs_refusals(legs, *, queue=None) -> list:
    """Every refusal of both legs; [] when both are proven."""
    if not isinstance(legs, dict):
        return ["REFUSED (S6-B3353): no legs record - a Step-2 verdict names its "
                "depth and breadth legs"]
    out = []
    for name in LEGS:
        out += leg_refusals(name, legs.get(name), queue=queue)
    return out


def not_run(legs) -> list:
    return [n for n in LEGS if (legs.get(n) or {}).get("state") == "not_run"]


def disposition(negative: bool, legs) -> str:
    """The words a verdict carries: a negative read with a leg not run is that
    leg's verdict, never the strategy's (#299)."""
    if not negative:
        return "QUALIFIERS FOUND - see rows"
    missing = not_run(legs)
    if missing:
        return (f"STEP-2 LEG NEGATIVE; {' AND '.join(m.upper() for m in missing)} "
                "LEG NOT RUN - NO STRATEGY FAILURE (#299, S6-B3353)")
    return "STEP-2 NEGATIVE - BOTH LEGS RAN OR WAIVED (S6-B3353)"


def add_cli(ap, name: str) -> None:
    """--<name>-leg plus the field that proves it."""
    ap.add_argument(f"--{name}-leg", required=True, choices=STATES,
                    help=f"S6-B3353: the {name} leg - ran, waived or not_run")
    ap.add_argument(f"--{name}-evidence", default=None,
                    help=f"ran: the artifact or record that ran the {name} leg")
    ap.add_argument(f"--{name}-word", default=None,
                    help=f"waived: the owner's words waiving the {name} leg, verbatim")
    ap.add_argument(f"--{name}-word-ticket", default=None,
                    help=f"waived: the ticket whose row records --{name}-word")
    ap.add_argument(f"--{name}-ticket", default=None,
                    help=f"not_run: the ticket that decides the {name} leg")


def from_args(a, name: str) -> dict:
    g = lambda f: getattr(a, f"{name}_{f}", None)  # noqa: E731
    st = g("leg")
    if st == "ran":
        return {"state": st, "evidence": (g("evidence") or "").strip()}
    if st == "waived":
        if str(ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(ROOT / "scripts"))
        import owner_word as _ow
        return {"state": st, "word": {"ticket": (g("word_ticket") or "").strip(),
                                      "verbatim": _ow.normalise(g("word"))}}
    return {"state": st, "ticket": (g("ticket") or "").strip()}
