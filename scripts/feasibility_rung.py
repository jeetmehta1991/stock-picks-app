#!/usr/bin/env python
"""S6-B2914 (R10): can a scheduled cell produce a VERDICT at all?

WHY IT EXISTS. R1-R9 all ask CAN WE RUN AND GRADE IT. None asks WILL THE
GRADE BE EVALUABLE. MEASURED across 110 grid artifacts and 17,927 rows, all
strategies: 14,712 of 17,927 cells (82.1 pct) produced no answer because there
were not enough trades - BELOW_POWER_FLOOR 7,493, NO_EXIT_SELECTABLE 7,219
(also a sample-size death), ZERO_FIRES 796. Only 63 cells (0.4 pct) ever
PASSED. Every one of those cells cost a full engine run to discover.

WHAT IT DOES. For each level of a TIGHTENING axis, re-derives from an
already-landed cube how many trades would survive, splits them into the
in-sample and holdout windows with roster_core's own helpers, and ranks the
levels by projected HOLDOUT count against the live floor.

WHAT IT MUST NEVER DO - AND THIS IS ENFORCED BY CONSTRUCTION, NOT BY PROSE.
It RANKS and ADMITS. It never REJECTS. There is no reject path in this file:
no --strict, no refuse branch, and a readable cube always exits 0. The reason
is measured, not stylistic: a tighter config FREES OCCUPANCY (the engine
blocks a fire while the same strategy already holds that ticker,
backtest.py:2522-2538), so a tighter cell can admit trades present in NO cube
and every count here is a LOWER BOUND (L812). A lower bound on trades makes
the count of BELOW-FLOOR cells an UPPER bound - at most this many are dead,
possibly fewer - so rejecting on it would kill cells that would clear the
floor live. Cells reading just under the floor are exactly the ones most
likely to survive a real run.

APPLICABILITY, stated rather than assumed (the Council Contrarian's limit on
S6-B2914): this works only where production is the LOOSEST corner, so every
scheduled cell is a strict SIGNAL-subset of the landed ledger. A band with a
window knob or a non-monotone knob has no landed superset and needs the
engine. The artifact records which case it was run on.

    python scripts/feasibility_rung.py --cube output_r5_merged_1_7 \\
        --strategy three_white_soldiers --signal-key rsi_14 \\
        --comparator lt --levels 60,55,50,45
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

_CMP = {
    "lt": lambda v, lvl: v < lvl,
    "le": lambda v, lvl: v <= lvl,
    "gt": lambda v, lvl: v > lvl,
    "ge": lambda v, lvl: v >= lvl,
}


def _signals(raw):
    """Parse a persisted signals_at_entry cell.

    L824: a probe that reports absence must prove it can see presence. The
    column is written in BOTH python-repr and JSON dialects across cube
    generations, and ast.literal_eval alone fails on every JSON-style row -
    which reads identically to the field being absent. Try both."""
    if not isinstance(raw, str) or not raw.strip():
        return None
    import ast
    try:
        d = ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        try:
            d = json.loads(raw)
        except ValueError:
            return None
    return d if isinstance(d, dict) else None


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cube", required=True, help="landed cube dir")
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--signal-key", required=True,
                    help="the key inside signals_at_entry the axis gates on")
    ap.add_argument("--comparator", required=True, choices=sorted(_CMP))
    ap.add_argument("--levels", required=True,
                    help="comma-separated levels, tightening order")
    ap.add_argument("--min-n", type=int, default=None,
                    help="holdout floor; default = the live gate's value")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    import roster_core as rc
    floor = a.min_n
    if floor is None:
        # roster_core imports the live gate dict as PC; read the floor from
        # there rather than restating it, so the rung cannot drift from the
        # gate it is projecting against (the owner ruled this 15 on 2026-08-29).
        floor = int(rc.PC["min_trades_holdout"])

    cube = Path(a.cube)
    tl = cube / "trade_log.csv"
    if not tl.exists():
        # NOT a rejection - the rung has nothing to measure and says so.
        print(json.dumps({"verdict": "NOT_COMPARABLE",
                          "reason": f"no trade_log.csv at {tl}"}))
        return 0

    df = pd.read_csv(tl)
    # roster_core.in_sample / holdout compare entry_date against date objects
    # (IS_START etc.), and load_cube:180 is where that contract is normally
    # established - `pd.to_datetime(...).dt.date`. Reading the trade log
    # directly leaves the column as str, which raises "Invalid comparison
    # between dtype=str and date" inside the window helpers. Match the
    # contract here rather than reimplementing the windows.
    if "entry_date" in df.columns:
        df["entry_date"] = pd.to_datetime(df["entry_date"],
                                          errors="coerce").dt.date
    if "strategy" in df.columns:
        df = df[df["strategy"] == a.strategy]
    if df.empty:
        print(json.dumps({"verdict": "NOT_COMPARABLE",
                          "reason": f"no {a.strategy} rows in {tl.name}"}))
        return 0

    # the axis value per landed trade, from the persisted signal dict
    vals, seen = [], 0
    for raw in df.get("signals_at_entry", pd.Series([None] * len(df))):
        d = _signals(raw)
        if d is not None and a.signal_key in d:
            seen += 1
            try:
                vals.append(float(d[a.signal_key]))
            except (TypeError, ValueError):
                vals.append(float("nan"))
        else:
            vals.append(float("nan"))
    df = df.assign(_axis=vals)
    coverage = seen / float(len(df)) if len(df) else 0.0

    op = _CMP[a.comparator]
    levels = [float(x) for x in a.levels.split(",") if str(x).strip()]

    rows = []
    for lvl in levels:
        keep = df[[bool(op(v, lvl)) if v == v else False for v in df["_axis"]]]
        ho = rc.holdout(keep)
        is_ = rc.in_sample(keep)
        rows.append({
            "level": lvl,
            "trades_kept": int(len(keep)),
            "is_n": int(len(is_)),
            "projected_holdout_n": int(len(ho)),
            "clears_floor_offline": bool(len(ho) >= floor),
            "bound": "LOWER",
        })

    # rank by projected holdout evidence, most-evidenced first
    rows.sort(key=lambda r: (-r["projected_holdout_n"], r["level"]))
    admitted = [r for r in rows if r["clears_floor_offline"]]

    doc = {
        "rung": "R10",
        "ticket": "S6-B2914",
        "strategy": a.strategy,
        "cube": str(cube).replace("\\", "/"),
        "axis": {"signal_key": a.signal_key, "comparator": a.comparator,
                 "levels": levels},
        "holdout_floor": floor,
        "signal_coverage": round(coverage, 6),
        "landed_trades": int(len(df)),
        "levels": rows,
        "admitted_offline": [r["level"] for r in admitted],
        "disposition": (
            "ADMISSION CANDIDATES. Every count here is a LOWER BOUND - a "
            "tighter config frees occupancy and can admit trades present in "
            "no cube (L812), so the count of below-floor cells is an UPPER "
            "bound on how many are truly unevaluable. This rung RANKS and "
            "ADMITS; it NEVER rejects, and a cell reading below the floor is "
            "NOT proven dead."),
        "applicability": (
            "Valid only where production is the loosest corner so every cell "
            "is a strict signal-subset of this cube. A window knob or a "
            "non-monotone knob has no landed superset and needs the engine."),
    }
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube.name}_{a.strategy}_r10_feasibility.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, default=str), encoding="utf-8")

    print(f"R10 feasibility - {a.strategy} on {cube.name}")
    print(f"  landed trades {len(df)}, {a.signal_key} coverage "
          f"{coverage:.4f}, holdout floor {floor}")
    print(f"  {'level':>12} {'kept':>8} {'is_n':>8} {'holdout_n':>10}  offline")
    for r in rows:
        print(f"  {r['level']:>12} {r['trades_kept']:>8} {r['is_n']:>8} "
              f"{r['projected_holdout_n']:>10}  "
              + ("ADMIT" if r["clears_floor_offline"] else "below floor"))
    print(f"  {len(admitted)} of {len(rows)} levels clear the floor OFFLINE "
          f"(lower bound - below-floor cells are NOT proven dead)")
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
