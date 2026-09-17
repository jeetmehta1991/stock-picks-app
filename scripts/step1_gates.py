#!/usr/bin/env python
"""B2848 (S6-B2848a/b, owner-approved 'Approved implement' 2026-09-17): the
two mechanical gates every STEP-1 instrument runs before any grid work.

ONE definition, imported by offline_level_sweep.py and breadth_step1_grid.py
(L593: the instrument that measured a rule and the pin that holds it share
code; here the two consumers share the gate).

1. require_band_ruling: the owner's T3 band words, verbatim, REQUIRED and
   non-empty - the breadth_step2_read --ruling pattern applied to Step-1.
   Before this, a Step-1 grid could run with no owner word at all; only
   discipline stopped it (the enforcement audit the owner forced,
   2026-09-17).
2. require_fresh_status: the stamped status view's build.source_commit must
   equal git HEAD - SS11.2w's regenerate-first precondition made mechanical.
   FAIL CLOSED on a missing or unreadable stamp (L642: the absent case is
   the case the guard exists for). `head` is injectable for tests only.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUS_JSON = ROOT / "output_audit" / "strategy_optimisation_status.json"


def require_band_ruling(text) -> str:
    if not isinstance(text, str) or not text.strip():
        raise SystemExit(
            "REFUSED: no --band-ruling. A Step-1 grid runs only after the "
            "owner's T3 band words, recorded verbatim into the artifact "
            "(S6-B2848a; the breadth_step2_read --ruling pattern).")
    return text.strip()


def require_fresh_status(head: str | None = None) -> str:
    try:
        stamp = json.loads(STATUS_JSON.read_text(encoding="utf-8"))[
            "build"]["source_commit"]
    except Exception as exc:
        raise SystemExit(
            f"REFUSED: status view stamp unreadable ({type(exc).__name__}) - "
            "regenerate scripts/build_strategy_status.py first (S6-B2848b, "
            "fail closed on the absent stamp)")
    if head is None:
        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, timeout=15).stdout.strip()
    if not head or stamp != head:
        raise SystemExit(
            f"REFUSED: status view stamped {stamp!r} but HEAD is {head!r} - "
            "REGENERATE FIRST (scripts/build_strategy_status.py) and commit "
            "the fresh build; SS11.2w made mechanical (S6-B2848b)")
    return stamp
