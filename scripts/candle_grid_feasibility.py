#!/usr/bin/env python
"""S6-B2914/B2916: how many of the 54 candle cells can produce a verdict?

WHY THIS EXISTS. The figure "27 of 54 cells below the holdout floor" has been
quoted across many turns of this programme and had NO ARTIFACT ON DISK - it
was computed once, in conversation, and never persisted. A figure whose source
is a computation that left no trace cannot be re-derived by anyone, which is
exactly what #201 forbids. This script makes it re-derivable.

THE GRID. SPECS['three_white_soldiers'] bands four ENGINE knobs - n_bars
[3,4] x min_body_pct [0.0,0.3,0.5] x min_step_pct [0.0,0.1,0.25] x
max_wick_pct [None,0.3,0.2] = 54 combinations. Production is the LOOSEST
corner (3, 0.0, 0.0, None).

THE METHOD, and its one load-bearing premise. Every scheduled cell is a
TIGHTENING of production, so its signal set is a strict SUBSET of the landed
fires: re-derive the anatomy at each landed entry bar under each config and
count survivors. The premise is checked rather than assumed - the production
corner must reproduce the landed set exactly, and the script REFUSES if it
does not.

WHAT IT IS A LOWER BOUND ON, stated because it changes how the number may be
used. A tighter config FREES OCCUPANCY (backtest.py:2522-2538 blocks a fire
while the same strategy already holds that ticker), so a tighter cell can
admit trades present in NO cube. Survivor counts here are therefore a LOWER
bound, which makes the count of BELOW-FLOOR cells an UPPER bound: at most
this many are unevaluable. A cell reading below the floor is NOT proven dead,
so this ranks and admits and must never be used to reject (S6-B2914).

ONE DEFINITION OF THE ANATOMY. leg A of spot_check_candle is imported rather
than reimplemented - two copies of one rule diverge (L593), and that checker's
arithmetic is the one already validated against the live producer.

    python scripts/candle_grid_feasibility.py --strategy three_white_soldiers
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

BULLISH = "three_white_soldiers"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cube", default="output_r5_merged_1_7")
    ap.add_argument("--strategy", default=BULLISH)
    ap.add_argument("--min-n", type=int, default=None,
                    help="holdout floor; default = the live gate's value")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    from spot_check_candle import _leg_a
    from spot_check_trades import load_ohlcv
    import roster_core as rc
    from producer_variant_table import SPECS

    floor = a.min_n if a.min_n is not None else int(
        rc.PC["min_trades_holdout"])

    spec = SPECS[a.strategy]
    band = {p["env"]: (p.get("band") or []) for p in spec["params"]
            if p.get("env")}
    axes = [band["CANDLE_N_BARS"], band["CANDLE_MIN_BODY_PCT"],
            band["CANDLE_MIN_STEP_PCT"], band["CANDLE_MAX_WICK_PCT"]]
    combos = list(itertools.product(*axes))

    cube = Path(a.cube)
    df = pd.read_csv(cube / "trade_log.csv")
    df = df[df["strategy"] == a.strategy].copy()
    if df.empty:
        print(json.dumps({"verdict": "NOT_COMPARABLE",
                          "reason": f"no {a.strategy} rows in {cube}"}))
        return 2
    df["entry_date"] = pd.to_datetime(df["entry_date"],
                                      errors="coerce").dt.date
    landed = len(df)
    bullish = a.strategy == BULLISH

    # bars once per ticker, and the entry-bar index once per trade
    cache: dict = {}
    fires = []
    unresolved = 0
    for _, r in df.iterrows():
        tk, when = str(r.get("ticker", "")), r.get("entry_date")
        if tk not in cache:
            try:
                cache[tk] = load_ohlcv(tk)
            except Exception:                              # noqa: BLE001
                cache[tk] = None
        o = cache[tk]
        if o is None:
            unresolved += 1
            continue
        hit = o.index.searchsorted(pd.Timestamp(when))
        if hit >= len(o) or o.index[hit].date() != when:
            unresolved += 1
            continue
        fires.append((tk, when, int(hit)))

    rows = []
    for n_bars, body, step, wick in combos:
        w = None if wick in (None, "", "None") else float(wick)
        keep = []
        for tk, when, i in fires:
            if _leg_a(cache[tk], i, bullish, int(n_bars), float(body),
                      float(step), w) is True:
                keep.append(when)
        kdf = pd.DataFrame({"entry_date": keep})
        ho = rc.holdout(kdf) if len(kdf) else kdf
        is_ = rc.in_sample(kdf) if len(kdf) else kdf
        rows.append({
            "n_bars": int(n_bars), "min_body_pct": float(body),
            "min_step_pct": float(step),
            "max_wick_pct": None if w is None else w,
            "survivors": len(keep), "is_n": len(is_),
            "holdout_n": len(ho),
            "clears_floor": bool(len(ho) >= floor),
            "is_production": (int(n_bars) == 3 and float(body) == 0.0
                              and float(step) == 0.0 and w is None),
        })

    prod = [r for r in rows if r["is_production"]]
    resolved = len(fires)
    repro_ok = bool(prod) and prod[0]["survivors"] == resolved
    below = [r for r in rows if not r["clears_floor"]]

    doc = {
        "ticket": "S6-B2914 / S6-B2916",
        "strategy": a.strategy, "cube": str(cube).replace("\\", "/"),
        "holdout_floor": floor,
        "landed_trades": landed, "resolved_to_bars": resolved,
        "unresolved": unresolved,
        "combinations": len(rows),
        "reproduction": {
            "production_corner_survivors": prod[0]["survivors"] if prod else None,
            "expected": resolved, "ok": repro_ok,
            "note": ("the loosest corner must recover every resolved landed "
                     "fire; if it does not, the subset premise fails and no "
                     "count below is usable"),
        },
        "below_floor": len(below), "clears_floor": len(rows) - len(below),
        "bound": ("LOWER bound on survivors, therefore an UPPER bound on the "
                  "count of unevaluable cells - a tighter config frees "
                  "occupancy and can admit trades present in no cube (L812). "
                  "RANK AND ADMIT ONLY; a below-floor cell is NOT proven "
                  "dead."),
        "cells": sorted(rows, key=lambda r: -r["holdout_n"]),
    }
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube.name}_{a.strategy}_grid_feasibility.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, default=str), encoding="utf-8")

    print(f"candle grid feasibility - {a.strategy} on {cube.name}")
    print(f"  landed {landed}, resolved to bars {resolved}, unresolved "
          f"{unresolved}; holdout floor {floor}")
    print(f"  production corner reproduces: {repro_ok} "
          f"({prod[0]['survivors'] if prod else '-'} of {resolved})")
    if not repro_ok:
        print("  REFUSING to report cell counts - the subset premise failed")
        return 2
    print(f"  {'n_bars':>6} {'body':>6} {'step':>6} {'wick':>6} "
          f"{'surv':>7} {'is_n':>7} {'ho_n':>6}  floor")
    for r in doc["cells"]:
        print(f"  {r['n_bars']:>6} {r['min_body_pct']:>6} "
              f"{r['min_step_pct']:>6} {str(r['max_wick_pct']):>6} "
              f"{r['survivors']:>7} {r['is_n']:>7} {r['holdout_n']:>6}  "
              + ("ok" if r["clears_floor"] else "BELOW"))
    print(f"  {len(below)} of {len(rows)} cells below the floor "
          f"(UPPER bound - not proven dead)")
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
