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
    _write_freshness_stamp()
    return 0


def _write_freshness_stamp():
    """B2058: record this generator's content hash in the shared freshness
    stamp, so an OUTPUT-PRESERVING generator edit (proven by regeneration)
    does not read as staleness under the B1974 timestamp rule - the same
    contract build_phase_1b_roster.py uses."""
    import hashlib
    import json
    sp = ROOT / "output_audit" / "phase_1b_roster_freshness.json"
    stamp = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
    me = "scripts/build_strategy_producer_map.py"
    stamp[me] = hashlib.sha256((ROOT / me).read_bytes()).hexdigest()
    sp.write_text(json.dumps(stamp, indent=1), encoding="utf-8")





# B2057 (S6-B1531c): the FAMILY-AXES view - one orthogonal sweep per shared
# producer serves every consumer, rather than each strategy buying its own
# grid. PLUMBED = the axis reaches the engine via a config/env knob today
# (B1519/B1616/B2016 lineage); UNPLUMBED = producer literals, tunable only
# after an owner-approved plumb of the same pattern.
PLUMBED_AXES = {
    "compute_smc_signals": "SMC_SWING_LENGTH (+ SMC_OB_CLOSE_MITIGATION, "
                           "SMC_OB_TAIL_N, SMC_BREAKER_AGE_BARS_MAX, "
                           "SMC_BREAKER_BREAK_PCT_MAX - B1616/B1519)",
    "compute_ema_sma": "EMA_PAIRS (B2016) + STRAT_EMA_SPAN consumer key",
}


def write_family_axes(out_path):
    import collections
    import csv as _csv
    fam = collections.defaultdict(set)
    with OUT.open(encoding="utf-8") as f:
        for r in _csv.DictReader(f):
            if r["tier"] != "UNRESOLVED":
                fam[r["producer"]].add(r["strategy"])
    lines = [
        "# Strategy family axes (generated - B2057, S6-B1531c)",
        "",
        "Derived from strategy_producer_map.csv. One orthogonal sweep of a",
        "family's axis serves EVERY member; an UNPLUMBED axis needs a",
        "B1519-pattern config plumb (owner-approved) before it is sweepable.",
        "",
        "| producer family | members | axis status |",
        "|---|---|---|",
    ]
    for p, members in sorted(fam.items(), key=lambda x: -len(x[1])):
        ax = PLUMBED_AXES.get(p, "UNPLUMBED (producer literals)")
        lines.append(f"| {p} | {len(members)} | {ax} |")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    # B2057: `--families` renders the family-axes view from the existing CSV
    # (defined below); anything else rebuilds the map. The first landing put
    # the dispatch AFTER this exit - dead code, caught by the missing file.
    if "--families" in sys.argv:
        write_family_axes(ROOT / "output_audit" / "strategy_family_axes.md")
        sys.exit(0)
    sys.exit(main())
