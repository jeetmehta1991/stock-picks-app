#!/usr/bin/env python
"""Machine-readable strategy -> signal-key -> producer map (B2037, S6-B1918b).

Why: B1035 reversed two disablements only because hand-written probes found
the producers alive - no machine-readable mapping existed to mechanise the
#279 reverse check, and the ENG7 class (a strategy consuming a key NOTHING
produces) was findable only by accident.

Resolution tiers, stated on every row (a floor is disclosed, never dressed
as the answer):

  T1 technical   - keys observed by RUNNING every compute_* producer that
                   compute_all_signals calls, on a real >=250-bar cached
                   frame (exact, runtime-observed emission)
  T2 smc         - keys observed by RUNNING compute_smc_signals on the same
                   frame (exact)
  UNRESOLVED     - keys consumed by a strategy that neither run emitted;
                   either produced by a screener-side injector this script
                   does not execute (news / congressional / chart patterns /
                   cross-sectional / avwap / ...), runtime-built (L437), or
                   genuinely produced by NOTHING (the ENG7 class). Listed,
                   never guessed.

Static key extraction per strategy uses the same two expressions as
demand_pruning._static_keys_of_active_strategies - a FLOOR (runtime-built
keys are invisible to it, L437).

Output: output_audit/strategy_producer_map.csv (CSV-first rule) with columns
strategy, key, tier, producer. HAND-RUN:
    PYTHONPATH=. python scripts/build_strategy_producer_map.py
"""
from __future__ import annotations

import csv
import inspect
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "output_audit" / "strategy_producer_map.csv"


def strategy_static_keys() -> dict[str, set[str]]:
    from backtest.signals.screener import ALL_STRATEGIES
    out: dict[str, set[str]] = {}
    for name, fn in ALL_STRATEGIES.items():
        try:
            src = inspect.getsource(fn)
        except Exception:
            out[name] = set()
            continue
        keys = set(re.findall(r's\.get\(\s*["\']([a-zA-Z0-9_]+)', src))
        keys |= set(re.findall(r's\[\s*["\']([a-zA-Z0-9_]+)', src))
        out[name] = keys
    return out


def emitted_key_maps():
    import pandas as pd
    from backtest.signals.demand_pruning import build_producer_key_map
    sample = None
    for p in sorted((ROOT / "backtest/data/cache/ohlcv").glob("*.parquet")):
        df = pd.read_parquet(p)
        if "date" in df.columns:
            df = df.set_index("date")
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        if len(df) >= 300:
            sample = df
            break
    if sample is None:
        raise SystemExit("no cached OHLCV frame >=300 bars - map would be a guess")
    tech = build_producer_key_map(sample)  # producer -> emitted keys (T1)
    key_to_producer: dict[str, tuple[str, str]] = {}
    for prod, keys in tech.items():
        for k in keys:
            key_to_producer.setdefault(k, ("T1_technical", prod))
    try:
        from backtest.signals.smc_ict import compute_smc_signals
        smc = compute_smc_signals(sample)
        for k in (smc or {}):
            key_to_producer.setdefault(k, ("T2_smc", "compute_smc_signals"))
    except Exception as exc:
        print(f"[WARN] compute_smc_signals unavailable on the sample ({exc!r}); "
              "T2 keys absent - smc_* consumption will read UNRESOLVED")
    return key_to_producer


def main() -> int:
    strat_keys = strategy_static_keys()
    k2p = emitted_key_maps()
    rows, unresolved_counts = [], {}
    for strat in sorted(strat_keys):
        for k in sorted(strat_keys[strat]):
            tier, prod = k2p.get(k, ("UNRESOLVED", ""))
            rows.append({"strategy": strat, "key": k, "tier": tier,
                         "producer": prod})
            if tier == "UNRESOLVED":
                unresolved_counts[k] = unresolved_counts.get(k, 0) + 1
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["strategy", "key", "tier", "producer"])
        w.writeheader()
        w.writerows(rows)
    n_res = sum(1 for r in rows if r["tier"] != "UNRESOLVED")
    print(f"strategies: {len(strat_keys)} | key-consumption rows: {len(rows)} "
          f"| resolved {n_res} ({n_res/max(len(rows),1):.0%}) | "
          f"unresolved distinct keys: {len(unresolved_counts)}")
    print("most-consumed UNRESOLVED keys (injector-produced, runtime-built, "
          "or produced by NOTHING - the ENG7 class):")
    for k, n in sorted(unresolved_counts.items(), key=lambda x: -x[1])[:15]:
        print(f"  {k}: consumed by {n} strategies")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
