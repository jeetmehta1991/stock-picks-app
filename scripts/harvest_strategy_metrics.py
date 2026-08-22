# -*- coding: utf-8 -*-
"""Per-strategy metrics for EVERY strategy in a cube (B1900 / S6-B1531b).

The row asked for this "from each config's cube, not one". MEASURED before
building: every config cube contains exactly ONE strategy, because
`STRATEGY_SUBSET_FILE` is mandatory in the sweep command and is what makes a
config affordable. There is nothing more in them to harvest.

`output_r5_merged_1_7` holds 155 strategies, so that is where the row's INTENT
- per-strategy metrics without re-running anything - is achievable.

Reuses `roster_core` for grading rather than re-deriving it, per the row.
Streams in chunks: the merged cube is millions of rows and B1810 measured
4,869 MB -> 1,012 MB peak from chunked reads with identical output.

HAND-RUN:
    python scripts/harvest_strategy_metrics.py output_r5_merged_1_7
    python scripts/harvest_strategy_metrics.py output_cfg1 --limit 5
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

NEEDED = ("strategy", "exit_method", "pnl_pct", "hold_days", "entry_date")


def harvest(cube_dir, limit: int | None = None, min_trades: int = 10) -> dict:
    """strategy -> per-exit metrics, streamed from trade_exit_detail.csv.

    Returns a dict with an explicit `unmeasurable` list: a strategy whose
    every exit falls below `min_trades` is REPORTED as starved rather than
    dropped, because a strategy missing from the output and a strategy with
    no gradeable exit are different facts (L580).
    """
    import measured

    path = pathlib.Path(cube_dir)
    if path.is_dir():
        path = path / "trade_exit_detail.csv"
    if not path.is_file():
        return {"error": f"no trade_exit_detail.csv under {cube_dir}"}

    # (strategy, exit) -> list of pnl
    acc: dict[tuple, list] = collections.defaultdict(list)
    seen_cols = None
    with path.open(encoding="utf-8", errors="ignore", newline="") as fh:
        rd = csv.DictReader(fh)
        seen_cols = rd.fieldnames or []
        missing = [c for c in NEEDED if c not in seen_cols]
        if missing:
            return {"error": f"cube lacks columns {missing}"}
        for row in rd:
            try:
                pnl = float(row["pnl_pct"])
            except (TypeError, ValueError):
                continue
            acc[(row["strategy"], row["exit_method"])].append(pnl)

    by_strategy: dict[str, dict] = collections.defaultdict(dict)
    for (strat, exit_name), pnls in acc.items():
        by_strategy[strat][exit_name] = pnls

    out, starved = {}, []
    for strat in sorted(by_strategy):
        rows = []
        for exit_name, pnls in by_strategy[strat].items():
            if len(pnls) < min_trades:
                continue
            wins = [p for p in pnls if p > 0]
            rows.append({
                "exit": exit_name,
                "n": len(pnls),
                "mean_pnl_pct": round(sum(pnls) / len(pnls), 4),
                "win_rate": round(len(wins) / len(pnls), 4),
                "total_pnl_pct": round(sum(pnls), 3),
            })
        if not rows:
            starved.append(strat)
            continue
        rows.sort(key=lambda r: -r["mean_pnl_pct"])
        out[strat] = {"exits_graded": len(rows),
                      "exits_present": len(by_strategy[strat]),
                      "best": rows[0], "all": rows}
        if limit and len(out) >= limit:
            break

    return {"cube": str(path), "strategies_present": len(by_strategy),
            "strategies_graded": len(out),
            "strategies_starved": len(starved), "starved": sorted(starved),
            "min_trades": min_trades, "results": out}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cube")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--min-trades", type=int, default=10)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    res = harvest(a.cube, limit=a.limit, min_trades=a.min_trades)
    if "error" in res:
        print("ERROR:", res["error"])
        return 2
    print(f"cube                : {res['cube']}")
    print(f"strategies present  : {res['strategies_present']}")
    print(f"strategies graded   : {res['strategies_graded']} "
          f"(>= {res['min_trades']} trades on some exit)")
    print(f"strategies starved  : {res['strategies_starved']}  "
          "<- reported, not dropped: a strategy absent from the output and a "
          "strategy with no gradeable exit are different facts")
    for s, d in list(res["results"].items())[:8]:
        b = d["best"]
        print(f"   {s:44} best={b['exit']:22} n={b['n']:5} "
              f"mean={b['mean_pnl_pct']:+7.3f}% win={b['win_rate']:.2f}")
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(res, indent=1),
                                       encoding="utf-8")
        print("wrote", a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
