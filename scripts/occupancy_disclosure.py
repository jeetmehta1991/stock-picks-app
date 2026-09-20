"""S6-B2871 part B: the correction an offline free-level re-score cannot compute.

WHY THIS IS ONE MODULE AND NOT A METHOD ON EITHER GRADER. Every free-level
re-scorer in this repo rests on the same premise - that raising a threshold
selects a STRICT SUBSET of trades already in the cube, so the level can be
graded offline for zero engine hours. MEASURED, the premise is false in one
direction that matters:

  A subset of SIGNALS is not a subset of TRADES (L812).

Under `cube_isolation` the engine forces `_bug61_mode = "ticker_strategy"` and
DROPS a candidate whenever the same strategy already holds an open position on
that ticker (backtest/engine/backtest.py:2497-2511). So REMOVING trades at a
tighter level FREES occupancy, and fires that were blocked while a position was
open can now open instead. Those trades exist in NO cube. Only the engine can
produce them.

The honest consequence: every trade count an offline re-score reports for a
TIGHTER level is a LOWER BOUND, and its verdicts are candidates, not
admissions. This module makes that statement a field in the artifact rather
than a caveat someone remembers.

MEASURED on output_r5_merged_1_7: 391,782 of 444,226 skip rows are occupancy
blocks - 88.2 pct - and they outnumber LANDED trades 2.07x (391,782 vs
189,471). Every one is stamped "(same-strategy)" because the pre-B2905 writer
discarded the name, so on that cube the per-strategy correction is
UNQUANTIFIABLE. B2905 fixed the stamp forward-only (owner ruling 2026-09-20,
"gate only future ones and leave the record as-is"), so cubes written after it
carry a real per-strategy count and this module reports it.

IT DISCLOSES, IT DOES NOT REFUSE. A refusal would fail the institutional
free-levels leg on every landing over a historical backlog nothing can fix
retroactively, which is the L721 trap - the gate's own noise trains everyone to
read past it. The owner's ruling is forward-only, and a field that says "this
number is a lower bound and here is by how much" is what forward-only means
here.
"""
from __future__ import annotations

from pathlib import Path

_OCC_REASON = "already_open"

LOWER_BOUND_NOTE = (
    "Every trade count for a TIGHTER level is a LOWER BOUND: removing trades "
    "frees occupancy, and fires the engine blocked while a position was open "
    "would then be taken. Those trades exist in no cube and only the engine "
    "can produce them (L812)."
)


def occupancy_disclosure(cube_dir, strategy: str) -> dict:
    """The occupancy correction for `strategy`, as a disclosable dict.

    Always returns a dict carrying `attribution_available` and
    `lower_bound_note`, so a caller cannot accidentally omit the disclosure by
    forgetting a key. Never raises and never refuses - see the module
    docstring for why the owner's ruling makes this a disclosure.
    """
    cube_dir = Path(cube_dir)
    out = {
        "artifact": "skipped_trades.csv",
        "attribution_available": False,
        "blocked_rows_total": None,
        "blocked_rows_attributable": None,
        "lower_bound_note": LOWER_BOUND_NOTE,
    }
    f = cube_dir / "skipped_trades.csv"
    if not f.exists():
        out["note"] = ("no skipped_trades.csv in this cube - the occupancy "
                       "correction cannot be bounded at all, so the counts "
                       "below are lower bounds of UNKNOWN slack")
        return out
    try:
        import pandas as pd
        sk = pd.read_csv(f, usecols=["strategy", "reason"], low_memory=False)
    except Exception as exc:                            # noqa: BLE001
        out["note"] = f"skipped_trades.csv unreadable ({exc!r}) - see above"
        return out

    occ = sk[sk["reason"].astype(str).str.contains(_OCC_REASON, na=False)]
    out["blocked_rows_total"] = int(len(occ))
    if not len(occ):
        out["attribution_available"] = True
        out["blocked_rows_attributable"] = 0
        out["note"] = ("no occupancy blocks recorded on this cube, so the "
                       "subset premise holds here and the counts are exact")
        return out

    names = occ["strategy"].astype(str)
    literal = int(names.str.startswith("(").sum())
    if literal:
        out["note"] = (
            f"{literal} of {len(occ)} occupancy rows carry a LITERAL stamp "
            "instead of a strategy name (the pre-B2905 writer), so the "
            "per-strategy correction is UNQUANTIFIABLE on this cube. "
            + LOWER_BOUND_NOTE)
        return out

    out["attribution_available"] = True
    out["blocked_rows_attributable"] = int(
        names.str.split(",").apply(lambda xs: strategy in xs).sum())
    out["note"] = (
        f"{out['blocked_rows_attributable']} of {len(occ)} occupancy blocks "
        f"name {strategy}. A tighter level frees some of them, so each count "
        "below is short by at most that many. " + LOWER_BOUND_NOTE)
    return out
