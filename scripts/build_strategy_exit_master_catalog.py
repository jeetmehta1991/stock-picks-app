#!/usr/bin/env python
"""Master catalog: all registered strategies x all registered exits.

Owner directive 2026-07-02: reference CSV showing WHAT is being tested
(cube universe), not results. One row per (strategy, exit) cube cell.

Also emits standalone lists for convenience:
  - strategies.csv    (one row per registered strategy)
  - exits.csv         (one row per registered exit method)
  - cube_universe.csv (one row per strategy x exit cell)

Usage:
  python scripts/build_strategy_exit_master_catalog.py --output-dir output_batch_A_150
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def infer_direction(name: str) -> str:
    if name.endswith("_short"):
        return "short"
    elif name.endswith("_long"):
        return "long"
    else:
        return "dual"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Strategies
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.config import STRATEGIES_DISABLED_MISSING_PRODUCER
    try:
        from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY
    except Exception:
        STRATEGY_REGIME_AFFINITY = {}

    disabled_set = set()
    for s in STRATEGIES_DISABLED_MISSING_PRODUCER:
        n = s.name if hasattr(s, "name") else str(s)
        if n.startswith("strat_"):
            n = n[len("strat_"):]
        disabled_set.add(n)

    strategies = []
    for s in ALL_STRATEGIES:
        name = getattr(s, "name", None) or getattr(s, "__name__", None) or str(s)
        if name.startswith("strat_"):
            name = name[len("strat_"):]
        direction = infer_direction(name)
        affinity = STRATEGY_REGIME_AFFINITY.get(name, [])
        strategies.append({
            "strategy_name": name,
            "direction": direction,
            "category": getattr(s, "category", "unknown"),
            "status": "DISABLED" if name in disabled_set else "ACTIVE",
            "regime_affinity": ",".join(sorted(affinity)) if affinity else "all_regimes",
        })
    strategies.sort(key=lambda x: x["strategy_name"])

    # Exits
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    exits = []
    for name, fn in sorted(EXIT_STRATEGIES.items()):
        doc = (getattr(fn, "__doc__", "") or "").strip().split("\n")[0][:200]
        exits.append({
            "exit_method": name,
            "description": doc,
        })

    # Write strategies.csv
    p = out / "strategies.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["strategy_name", "direction", "category", "status", "regime_affinity"])
        w.writeheader()
        w.writerows(strategies)
    print(f"Wrote {p}: {len(strategies)} strategies")

    # Write exits.csv
    p = out / "exits.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["exit_method", "description"])
        w.writeheader()
        w.writerows(exits)
    print(f"Wrote {p}: {len(exits)} exit methods")

    # Write cube_universe.csv (all combinations)
    p = out / "cube_universe.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "strategy_name", "direction", "status", "regime_affinity", "exit_method",
        ])
        w.writeheader()
        for strat in strategies:
            for ex in exits:
                w.writerow({
                    "strategy_name": strat["strategy_name"],
                    "direction": strat["direction"],
                    "status": strat["status"],
                    "regime_affinity": strat["regime_affinity"],
                    "exit_method": ex["exit_method"],
                })
    print(f"Wrote {p}: {len(strategies) * len(exits)} cube cells "
          f"({len(strategies)} strategies x {len(exits)} exits)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
