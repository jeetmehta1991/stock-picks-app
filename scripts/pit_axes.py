#!/usr/bin/env python
"""S6-B3455 (B3139q-r217): AN AXIS WHOSE STORED VALUES IN A CUBE PRE-DATE ITS
PRODUCER'S POINT-IN-TIME CORRECTION IS NOT POINT-IN-TIME IN THAT CUBE.

WHY. A cube stores each fire's signals as the producer computed them when the
cube was built. A later point-in-time correction of the producer leaves every
older cube's stored values as they were. S6-B3139as (B3139q-r47, commit
265c12ccb, 2026-10-06) made COT positioning usable from its Friday RELEASE and
one contract per file; the R5 merged cube was built in July, so its stored
cot_* values used the positions date and the Micro E-mini file. S6-B3139ar
(owner ruling 2026-10-06, option B) dropped the COT axis from bollinger_lower's
breadth grid for exactly that; the rule never reached the grid builders, so
batch 2's grids (B3139q-r216) kept a COT axis in 3 of 5 - rsi_oversold
cot_ndx_mmoney_pctile_3y, stochrsi_oversold and m_and_a_target_long
cot_rut_commercials_net_pct - and rsi_oversold's holdout read (B3139q-r217)
put 21 of its 41 all-six qualifiers on it (L1019).

The same holds for the two other corrections of the availability sweep that
change STORED values: short interest from FINRA's publication date with a
dated share count (S6-B3139bn / S6-B3139bd, B3139q-r45) and the FRED macro
series at their ALFRED vintage (S6-B3139bi, B3139q-r44).

WHAT. CORRECTIONS lists each point-in-time correction by its keys or key
prefixes, ticket and commit; non_pit_axes(axes, cube) names the axes whose stored
values in `cube` pre-date their correction. A cube is PRE-FIX when it is the
R5 merged cube (built 2026-07, no manifest), or when its run_manifest.json's
frozen_sha does not descend from the correction's commit; an unreadable
manifest or sha reads PRE-FIX with the reason said (fail closed, L642).
A DISCLOSURE: the readers and the packet name the axes; whether a grid may
carry them at all is the owner's decision (S6-B3455a).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R5_CUBE = "output_r5_merged_1_7"
CORRECTIONS = (
    # the S6-B3139aw / S6-B3139ba availability sweep's corrections that change
    # STORED signal values, each EXECUTED on the owner's 2026-10-06 rulings
    # (S6-B3139br); a correction that changes no stored key is not listed
    {"prefixes": ("cot_",), "keys": (), "ticket": "S6-B3139as / S6-B3139at",
     "batch": "B3139q-r47", "commit": "265c12ccb",
     "why": ("COT positioning is usable from its Friday release, one contract per "
             "file; a value stored before the fix used the positions date and the "
             "Micro E-mini file")},
    {"prefixes": (), "keys": ("days_to_cover", "short_interest_pct",
                              "short_interest_observations",
                              "short_interest_settlement_date"),
     "ticket": "S6-B3139bn / S6-B3139bd", "batch": "B3139q-r45", "commit": "c36a07bf4",
     "why": ("a FINRA settlement is usable from its publication date and the share "
             "count is dated at the settlement; a value stored before the fix used "
             "the settlement date and an undated share count")},
    {"prefixes": (), "keys": ("hy_oas", "financial_stress", "recession_probability",
                              "jobless_claims", "fed_balance_sheet", "macro_score"),
     "ticket": "S6-B3139bi", "batch": "B3139q-r44", "commit": "39fbb9bb5",
     "why": ("a FRED series is read at the ALFRED vintage in force on the date; a "
             "value stored before the fix used the latest-revised observation")},
)


def _post_fix(cube, commit: str, root: Path = ROOT) -> tuple[bool, str]:
    """(stored values follow the correction, why) for one cube directory."""
    if not cube or R5_CUBE in str(cube).replace(chr(92), "/"):
        return False, f"{R5_CUBE} was built in 2026-07, before the correction"
    cube = str(cube).split(" (")[0]          # a grid's label suffix, ' (default)'
    man = Path(cube) if Path(cube).is_absolute() else root / cube
    if man.suffix:                       # a file inside the cube - its directory
        man = man.parent
    name = man.name
    try:
        sha = json.loads((man / "run_manifest.json").read_text(encoding="utf-8")).get(
            "frozen_sha")
    except (OSError, ValueError) as exc:
        return False, f"{name}: run_manifest.json unreadable ({type(exc).__name__}) - read as pre-fix"
    if not sha:
        return False, f"{name}: its manifest records no frozen_sha - read as pre-fix"
    r = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", commit, str(sha)],
                       capture_output=True)
    if r.returncode == 0:
        return True, f"{name} froze {str(sha)[:9]}, which descends from {commit}"
    if r.returncode == 1:
        return False, f"{name} froze {str(sha)[:9]}, which predates {commit}"
    return False, f"{name}: git could not order {str(sha)[:9]} against {commit} - read as pre-fix"


def non_pit_axes(axes, cube=None, root: Path = ROOT) -> dict:
    """{axis: reason} for each of `axes` whose stored values in `cube` (None or
    the R5 merged cube for the default) pre-date their producer's correction."""
    out = {}
    for a in sorted({str(x) for x in axes or ()}):
        for c in CORRECTIONS:
            if a in c["keys"] or any(a.startswith(p) for p in c["prefixes"]):
                post, why = _post_fix(cube, c["commit"], root)
                if not post:
                    out[a] = (f"{c['ticket']} ({c['batch']}): {c['why']}; {why} - not "
                              "point-in-time here (S6-B3455)")
    return out


def drop_non_pit(art: dict, read: dict | None, cube=None, root: Path = ROOT):
    """(art', read', dropped) - copies of a breadth Step-1 artifact and its read
    with every row and qualifier on a non-point-in-time axis removed, and the
    {axis: reason} map of what was dropped (S6-B3455). Used to re-price a read's
    holdout null without them, as S6-B3139ar's ruling did for bollinger_lower."""
    dropped = non_pit_axes({r.get("axis") for r in art.get("rows") or []}, cube, root)
    a2 = dict(art, rows=[r for r in art.get("rows") or [] if r.get("axis") not in dropped])
    r2 = None
    if read is not None:
        r2 = dict(read, qualifiers=[q for q in read.get("qualifiers") or []
                                    if q.get("axis") not in dropped])
    return a2, r2, dropped
