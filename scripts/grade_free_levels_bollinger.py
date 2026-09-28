"""S6-B3119: grade the bollinger_lower P9 FREE levels off a landed cube.
Zero engine hours.

WHY IT EXISTS. B2569 (owner directive 2026-09-02) made free-level grading a
leg of EVERY landing (L752 / #290): a missing leg produces NO row and NO
FAIL, so the span campaign's cubes would land with the approved adx levels
silently ungraded. Modelled on grade_free_levels_candle.py (S6-B2904), the
L754 second-family extraction.

THE AXIS GRADED HERE. P9 is the adx ceiling, and it is OFFLINE: no env knob,
and the engine's gate reads a value persisted per trade -
  bollinger_lower  screener.py (strat_bollinger_lower)  adx < 35  (a CEILING)
Every free level TIGHTENS (the ceiling drops), so each level selects a
STRICT SUBSET of trades already in the cube. Coverage on the R5 baseline:
adx present at 100.0% of the strategy's 1,622 fires (the charter's measured
free-band line).

AXIS SCOPE, DISCLOSED (#290 - scheduled-with-mechanism, never dropped):
this leg grades P9 only. The OTHER free axes of the entry ride their own
named instruments per landing: the B-row companion axes ride the per-leg
Step-1 grid instrument (scripts/breadth_step1_grid.py --cube-dir <landing>
--leg long|short, the b3119 pattern), and the P8xP11 VIX-edge composite is
S6-B3118a's dedicated grader (the band-coverage gate names it at any Step-2
declaration). One leg per axis family; each named; none silent.

THE GATE IS MIRRORED EXACTLY, STRICT COMPARISON INCLUDED: the producer uses
`<` (adx_ok = s.get("adx", 30) < 35).

REPRODUCTION GATE (owner, 2026-09-02): before any level is graded, every
covered row must RE-PASS at the PRODUCTION bound; a covered row that fails
means the logged signal disagrees with the gate the engine ran - exit 2,
grade nothing. Unparseable rows are counted, excluded and reported.

THE OCCUPANCY DISCLOSURE (L812): a subset of SIGNALS is not a subset of
TRADES - removing trades at a tighter level frees occupancy the engine alone
can simulate. Every count here is a LOWER BOUND; verdicts are candidates,
never admissions.

Usage (the battery passes exactly this):
  python scripts/grade_free_levels_bollinger.py --cube <dir> --out <grid.json>
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roster_core as rc  # noqa: E402
from occupancy_disclosure import (  # noqa: E402
    occupancy_disclosure)

ROOT = Path(__file__).resolve().parent.parent

STRAT = "bollinger_lower"

# the live gate, read from the producer - a strict ceiling
DIRECTION, PRODUCTION = "lt", 35.0
KEY = "adx"


def keep_row(value, direction: str, bound: float) -> bool:
    """Mirror the producer's gate EXACTLY, strict comparison included."""
    return (value < bound) if direction == "lt" else (value > bound)


def parse_signals(raw):
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        d = ast.literal_eval(raw)
    except Exception:                                   # noqa: BLE001
        try:
            d = json.loads(raw)
        except Exception:                               # noqa: BLE001
            return None
    return d if isinstance(d, dict) and d else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cube", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--strategy", default=None,
                    help="override the manifest's graded strategy (hand runs)")
    a = ap.parse_args()

    cube_dir = Path(a.cube)
    tl_path = cube_dir / "trade_log.csv"
    ted_path = cube_dir / "trade_exit_detail.csv"
    for p in (tl_path, ted_path):
        if not p.exists():
            print(f"[FAIL] no {p.name} in {cube_dir}")
            return 2

    strat = a.strategy
    if strat is None:
        try:
            import run_postconfig as rp
            strat, _riders = rp.graded_and_riders(cube_dir)
        except Exception:                               # noqa: BLE001
            strat = None
    if strat != STRAT:
        print(f"[FAIL] graded strategy {strat!r} is not {STRAT!r} - this leg "
              "grades the bollinger P9 axis only (fail closed, L642)")
        return 2

    import producer_variant_table as pvt
    p9 = [x for x in pvt.SPECS[strat]["params"] if x["id"] == "P9"][0]
    assert float(p9["production"]) == PRODUCTION, (p9["production"], PRODUCTION)
    levels = [float(x) for x in p9["free_band"]
              if float(x) != PRODUCTION]

    tl = pd.read_csv(tl_path, low_memory=False)
    tl = tl[tl["strategy"].astype(str) == strat].copy()
    if tl.empty:
        print(f"[FAIL] no {strat} rows in {tl_path.name}")
        return 2

    # ---- reproduction gate, at the PRODUCTION bound ----------------------
    vals, unverifiable = [], 0
    for raw in tl["signals_at_entry"]:
        d = parse_signals(raw)
        if d is None or KEY not in d:
            vals.append(None)
            unverifiable += 1
        else:
            vals.append(float(d[KEY]))
    tl["_adx"] = vals
    covered = tl[tl["_adx"].notna()]
    failed = covered[~covered["_adx"].apply(
        lambda v: keep_row(v, DIRECTION, PRODUCTION))]
    repro = {"covered_rows": int(len(covered)),
             "unverifiable_rows": int(unverifiable),
             "rows_total": int(len(tl)),
             "production_bound": PRODUCTION, "direction": DIRECTION,
             "failed_reproduction": int(len(failed))}
    if len(failed):
        print(f"[FAIL] reproduction gate: {len(failed)} of {len(covered)} "
              f"covered rows do NOT re-pass {KEY} {DIRECTION} {PRODUCTION} - "
              "the logged signals disagree with the gate the engine ran, so "
              "nothing this tool reports about any level is believable "
              "(owner ruling 2026-09-02). Grading nothing.")
        return 2

    # ---- grade each free level on the exit-expanded cube -----------------
    ted = pd.read_csv(ted_path, low_memory=False)
    ted = ted[ted["strategy"].astype(str) == strat].copy()
    ted["entry_date"] = ted["entry_date"].astype(str).str[:10]
    covered = covered.copy()
    covered["entry_date"] = covered["entry_date"].astype(str).str[:10]

    results = []
    for lvl in [PRODUCTION] + levels:
        keep = covered[covered["_adx"].apply(
            lambda v: keep_row(v, DIRECTION, float(lvl)))]
        ids = set(zip(keep["ticker"].astype(str), keep["entry_date"]))
        sub = ted[[(t, d) in ids for t, d in
                   zip(ted["ticker"].astype(str), ted["entry_date"])]]
        per_exit = []
        for ex, g in sub.groupby("exit_method", observed=True):
            st = rc.evaluate(g["pnl_pct"], g["hold_days"], min_n=a.min_n)
            if st is None:
                continue
            per_exit.append({"exit": str(ex), "n": int(len(g)),
                             "sharpe": st.get("sharpe"),
                             "ci_lo": st.get("ci_lo")})
        per_exit.sort(key=lambda r: -(r["ci_lo"] if r["ci_lo"] is not None
                                      else -9e9))
        results.append({
            "level": float(lvl),
            "is_production": float(lvl) == PRODUCTION,
            "trades_kept": int(len(keep)),
            "trades_kept_is_a_lower_bound": True,
            "exit_rows": int(len(sub)),
            "exits_evaluable": len(per_exit),
            "best": per_exit[0] if per_exit else None,
            "per_exit": per_exit[:6],
        })

    doc = {
        "strategy": strat, "axis": "P9 " + str(p9["param"]),
        "grader": "scripts/grade_free_levels_bollinger.py (S6-B3119)",
        "cube": str(cube_dir).replace("\\", "/"),
        "gate_mirrored": f"{KEY} {DIRECTION} <level> (strict, per screener.py)",
        "levels_searched": [PRODUCTION] + levels,
        "axis_scope": ("P9 graded here; B-row companions ride "
                       "breadth_step1_grid --cube-dir per leg; the P8xP11 "
                       "composite is S6-B3118a's grader - each axis family "
                       "has a named instrument (#290)"),
        "reproduction": repro,
        "occupancy": occupancy_disclosure(cube_dir, strat),
        "results": results,
        "levels": {str(r["level"]): {"p9": r["level"],
                                     "is_fires": r["trades_kept"],
                                     "per_exit_ranked_by_ci_lo": r["per_exit"]}
                   for r in results},
        "multiplicity_exposure": (
            f"{len(levels)} free levels searched on this axis, each a max over "
            f"{max((r['exits_evaluable'] for r in results), default=0)} exits, "
            "nested inside ONE engine run - the levels are not independent "
            "trials and no correction is applied here (S6-B2444 recording "
            "rule)"),
        "verdict_status": ("CANDIDATES, never admissions - every trade count "
                           "is a lower bound while the occupancy correction "
                           "is unsimulated (L812)"),
    }
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube_dir.name}_free_levels.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")
    base = results[0]
    print(f"[OK] {strat} P9 {DIRECTION} - reproduction {repro['covered_rows']} "
          f"covered / {repro['unverifiable_rows']} unverifiable / 0 failed; "
          f"production {base['level']} keeps {base['trades_kept']} trades")
    for r in results[1:]:
        b = r["best"]
        print(f"     level {r['level']:<8} keeps {r['trades_kept']:<5} "
              + (f"best {b['exit']} ci_lo {b['ci_lo']} n {b['n']}"
                 if b else "no exit cleared the power floor"))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
