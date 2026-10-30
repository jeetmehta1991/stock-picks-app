#!/usr/bin/env python
# Source: <cube>/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""S6-B3240 (B3139q-r89): the Step-1 grader for the four LEVER4 gate-budget
strategies (screener.LEVER4_LEGS) - the base cell per leg x exits, IS-only,
graded at the gate budget the cube was produced at.

WHY LEGS x EXITS AND NO NUMERIC AXIS. LEVER4 is a STRATEGY-LAYER knob: a
k-of-m budget on the LONG gate (screener._gate_budget, config.
LEVER4_GATE_BUDGET). Its one non-production level under the owner's R2 reading
(2026-10-21: k = m-1 with the thesis leg mandatory) ADMITS fires the
production cube never recorded, so it is resim-only - no offline level exists
to sweep, and a Step-1 grid over a landed cube is legs x exits, the smc
no-free-axis design. grade_cells is IMPORTED from smc_family_step1 with this
family's legs (L799: inherit the code, not a copy of it), and the frame is
smc_lsr_step1.build's, with its fail-closed path check and per-fire dedup.

REPRODUCTION. On the R5 cube - produced with NO budget, every strategy's
production AND - the graded unique fires must equal SPECS[<strategy>]
['baseline']['cube_fires'], the EXIT CUBE's count the entry was registered
with (the trade log can hold more: the R5 cube writer dropped some closed
trades, S6-B3258); a mismatch REFUSES, and so
does a non-production budget claimed for R5. Any other cube records
VARIANT-CUBE-NO-R5-REPRODUCTION with the budget it was produced at and its own
fire count (the L754 portability contract).

--gate-budget is IDENTITY, recorded not swept: the battery passes the landed
arm's LEVER4_GATE_BUDGET env value ('' at production, else the JSON object).
The grid records THIS strategy's entry of it as config.P1_gate_budget (None
at production) - the key the Table D axis family detects.

STEP 2 (S6-B3331, B3139q-r132; the owner's words 2026-10-29 'Build the leg,
read once' and 'breakeven_plus_trail, per 2(i)'): --step2 declares a Step-2
cube, and the holdout is read ONCE by grade_npoc_config.grade_step2 -
imported, not copied (L799) - on the LONG leg's rows: the exit the cube's OWN
in-sample selects (roster_core.select_exit, objective 'gates'), that exit's
holdout graded once with full_period_n, the six LIVE_GATES deciding PASS or
FAIL. --preregistered-exit is RECORDED beside the selection and a mismatch
DISCLOSED, never re-rolled and never read (owner ruling 2(i), 2026-09-05).
The leg is LONG because the LEVER4 budget binds the long gate only
(screener._gate_budget): a dual's short side is its production gate, outside
the arm under test. Without --step2 the grid is unchanged - no step2 block,
the holdout untouched. Before this leg the battery failed step 2 CLOSED on
the first LEVER4 Step-2 landing (pivot_r1_breakout, 2026-10-29): the family's
tools block declared no step2_flag (L974).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import roster_core as rc  # noqa: E402
from smc_family_step1 import grade_cells  # noqa: E402
from smc_lsr_step1 import build as _build  # noqa: E402
from grade_npoc_config import grade_step2 as _grade_step2  # noqa: E402

R5_DIR = ROOT / "output_r5_merged_1_7"

# the four LEVER4 strategies (screener.LEVER4_LEGS - test_b3240 holds the two
# equal) and the sides each emits; the budget binds the LONG side only, a
# dual's short side keeps its full AND.
FAMILY = {
    "pivot_r1_breakout": {"legs": ("long", "short")},
    "news_momentum_long": {"legs": ("long",)},
    "smc_bos_continuation": {"legs": ("long", "short")},
    "orb_stocks_in_play_long": {"legs": ("long",)},
}
# S6-B3331: the leg a Step-2 read grades. The budget binds the LONG gate only
# (screener._gate_budget), so a dual's short side is its production gate and
# not the arm under test; the two long-only members have no other leg.
STEP2_LEG = "long"


def budget_for(raw, strat: str):
    """THIS strategy's entry of a LEVER4_GATE_BUDGET env value, as compact
    JSON, or None at production ('' / absent / an object not naming it).
    Unparseable JSON or a non-object REFUSES - it would mislabel the cube."""
    s = "" if raw is None else str(raw).strip()
    if s == "" or s.lower() == "none":
        return None
    try:
        obj = json.loads(s)
    except ValueError:
        raise SystemExit(f"REFUSED: --gate-budget is not JSON: {s!r}")
    if not isinstance(obj, dict):
        raise SystemExit(f"REFUSED: --gate-budget is not an object: {s!r}")
    entry = obj.get(strat)
    return None if entry is None else json.dumps(entry, sort_keys=True)


def rank(graded: list) -> list:
    """Graded, non-npt rows in the RULED order: the in-sample lower bound
    is_ci_lo first (runbook 6.4b; grade_npoc_config's sort), None last,
    then more in-sample trades - never Sharpe. make_spec takes the first
    row's exit as the Step-2 pre-registered exit (B2612)."""
    return sorted((r for r in graded if not r["npt_barred"]),
                  key=lambda r: (-(r["is_ci_lo"] if r.get("is_ci_lo") is not None
                                   else -9e9), -r["is_n"]))


def _baseline_fires(strat: str) -> int:
    from producer_variant_table import SPECS
    return int(SPECS[strat]["baseline"]["cube_fires"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--strategy", required=True, choices=sorted(FAMILY))
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cube", default="",
                    help="cube DIRECTORY to grade; default the R5 baseline")
    ap.add_argument("--gate-budget", default=None,
                    help="the LEVER4_GATE_BUDGET the cube was produced at - "
                         "identity, recorded not swept")
    ap.add_argument("--step2", action="store_true",
                    help="declare a Step-2 cube: the long leg's holdout is read "
                         "ONCE on the exit the cube's own in-sample selects, "
                         "the six LIVE_GATES decide (S6-B3331)")
    ap.add_argument("--preregistered-exit", default=None,
                    help="the Step-1 pre-registered exit - recorded beside the "
                         "selection, never read (owner ruling 2(i))")
    ap.add_argument("--survival", action="store_true",
                    help="S6-B3322: read only the R5 fires the CURRENT gate "
                         "keeps - required on R5 for a changed gate, refused "
                         "on an engine cube")
    a = ap.parse_args(argv)
    t0 = time.time()
    strat = a.strategy
    budget = budget_for(a.gate_budget, strat)

    cube_dir = Path(a.cube).resolve() if a.cube else None
    if cube_dir is not None and cube_dir.is_file():
        cube_dir = cube_dir.parent
    is_r5 = cube_dir is None or cube_dir == R5_DIR.resolve()
    if is_r5 and budget is not None:
        raise SystemExit(f"REFUSED: the R5 cube ran with no gate budget, "
                         f"but --gate-budget names {budget} (fail closed)")
    if is_r5 and a.step2:
        raise SystemExit("REFUSED: --step2 names the R5 cube - it carries no "
                         "gate budget, so its holdout is the production "
                         "strategy's, not a LEVER4 arm's (fail closed)")
    legs = None
    if a.step2:
        # S6-B3367 (#299): both legs before the holdout is read - depth is
        # this cube, breadth what its spec's arm declared at launch
        import step2_legs
        legs = step2_legs.cube_legs(cube_dir)
        lerrs = step2_legs.legs_refusals(legs)
        if lerrs:
            raise SystemExit(f"{lerrs[0]} (S6-B3367: the breadth leg rides the "
                             "spec's arm - make_spec --breadth-leg)")
    m = _build(None if is_r5 else cube_dir, strat=strat, keys=[],
               survival=a.survival)
    fires = m.drop_duplicates(["ticker", "entry_date"])
    n_cube = m.attrs["fires_before_survival"]    # S6-B3322: reproduce, then select

    if is_r5:
        want = _baseline_fires(strat)
        if n_cube != want:
            raise SystemExit(f"REFUSED: {n_cube} unique fires != the "
                             f"registered R5 baseline {want} (fail closed)")
        repro = (f"R5 BASELINE reproduction OK: {n_cube} fires == {want}"
                 + (f"; the current gate keeps {len(fires)} (S6-B3322 survival)"
                    if a.survival else ""))
    else:
        repro = (f"VARIANT-CUBE-NO-R5-REPRODUCTION: produced at gate budget "
                 f"{budget if budget is not None else 'none (production)'}; "
                 f"own fires {len(fires)}")
    print(f"{repro} ({time.time()-t0:.0f}s)")

    rows = grade_cells(m, strat, a.min_n, legs=FAMILY[strat]["legs"])
    graded = [r for r in rows if r["is_sharpe"] is not None]
    ranked = rank(graded)
    print(f"{len(graded)} graded cells of {len(rows)}")

    rec = {"strategy": strat,
           "generator": "scripts/lever4_step1.py",
           "cube": str(cube_dir) if cube_dir else str(R5_DIR),
           "config": {"P1_gate_budget": budget},
           "reproduction": repro,
           "design": ("base cell per leg x exits, IS-only; holdout untouched; "
                      "npt barred; ranked on is_ci_lo; the LEVER4 budget is resim-only (a looser "
                      "gate adds fires no cube holds), so the grid carries no "
                      "offline numeric axis"),
           "reproduction_fires": int(n_cube),
           "survival": {"applied": bool(a.survival), "fires_graded": int(len(fires))},
           "cells_graded": len(graded),
           # 11.2b2d: mandatory, report-only - no numeric search, so no
           # permutation null exists; the partition says so.
           "multiplicity": rc.bh_fdr_report(rows),
           "step1_ranking": ranked[:80], "rows": rows,
           "holdout_read": "NOT FIRED - Step 2 needs its own owner word (11.2c)"}
    if a.step2:
        # S6-B3331: the ONE holdout read of a Step-2 cube, on the budget-bound
        # leg; the in-sample ranking above is unchanged and never read past it
        leg = m[m.direction == STEP2_LEG]
        s2 = _grade_step2(leg, rc.holdout(leg), min_n=a.min_n,
                          declared_step2=True,
                          preregistered_exit=a.preregistered_exit)
        s2["leg"] = STEP2_LEG
        s2["legs"] = legs
        s2["disposition"] = step2_legs.disposition(s2.get("verdict") == "FAIL", legs)
        rec["step2"] = s2
        rec["design"] = ("base cell per leg x exits, IS-only ranking; npt barred; "
                         "ranked on is_ci_lo; Step 2: the long leg's holdout "
                         "read ONCE in `step2` on the exit its own in-sample "
                         "selects (S6-B3331, owner ruling 2(i))")
        rec["holdout_read"] = (
            f"FIRED ONCE (S6-B3331): {s2['verdict']} on the {STEP2_LEG} leg's "
            f"{s2.get('selected_exit')}" if s2.get("holdout_read") else
            f"DECLARED STEP 2, NOT READ: {s2['verdict']} - {s2.get('reason')}")
        print(f"[STEP-2] {s2['verdict']}: {STEP2_LEG} leg, exit "
              f"{s2.get('selected_exit')}, holdout_n {s2.get('holdout_n')} of "
              f"full_period_n {s2.get('full_period_n')}, sharpe "
              f"{s2.get('sharpe')}, gates {s2.get('gates_passed')} of "
              f"{len(rc.LIVE_GATES)}; pre-registered {a.preregistered_exit} "
              + ("MISMATCH - recorded, not read" if s2.get("mismatch")
                 else "matches" if a.preregistered_exit else "none named"))
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
