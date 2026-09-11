#!/usr/bin/env python
# Source: output_r5_merged_1_7/trade_log.csv + backtest.signals.screener per CHECKLIST #77.
"""B2677 (S6-B2638c): the OFFLINE-GRADABILITY CENSUS across the active roster.

For each ACTIVE strategy (live registry minus disabled sets, re-derived at
run time - never a hardcoded count), map the signal keys its gate expression
consumes (source scan of s.get("...") plus ONE level of _has_*() helper
follow, the B2669 classifier lesson) onto:
  (a) the PERSISTED keyspace - union of signals_at_entry keys over a sample
      of recorded R5 trades (the cube persists ~759 keys/trade), and
  (b) the strategy's RECORDED FIRE COUNT in the R5 merged trade log - an
      offline campaign filters recorded fires, so zero fires means nothing
      to filter regardless of key coverage.

LABELS (a feasibility SCREEN for campaign planning, never a gate):
  FULLY-FREE  - every consumed key persisted AND >= min-fires recorded fires:
                a tightening campaign runs offline in seconds.
  PARTIAL     - fires exist and >= 50pct of consumed keys persisted.
  NEEDS-ENGINE- zero recorded fires, or < 50pct of keys persisted.

HONEST LIMITS, stated: a source scan reads WHICH keys are consumed, not
which THRESHOLD levels are interesting; boolean-only strategies are
"tightenable" only by leg-dropping (the B2674 pattern); and key presence in
the sample keyspace is necessary, not sufficient, for a numeric level sweep
(the value must also be a magnitude, which the campaign's own coverage
refusal checks per axis at run time).
"""
from __future__ import annotations

import argparse
import ast
import inspect
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
TRADE_LOG = ROOT / "output_r5_merged_1_7" / "trade_log.csv"
KEY_SAMPLE_ROWS = 2000


def _parse(s):
    try:
        return json.loads(s)
    except Exception:
        try:
            return ast.literal_eval(s)
        except Exception:
            return {}


def consumed_keys(fn, module) -> tuple[set[str], set[str]]:
    """Returns (all_keys, boolean_default_keys). A key read as
    s.get("k", False) is a BOOLEAN GATE: an absent persisted key is
    exactly the False the engine read (the B2674 lesson), so it is
    reconstructable offline regardless of keyspace-sample presence."""
    def scan(src):
        return (set(re.findall(r"s\.get\(\"([a-z0-9_]+)\"", src)),
                set(re.findall(r"s\.get\(\"([a-z0-9_]+)\", False\)", src)))
    src = inspect.getsource(fn)
    keys, bools = scan(src)
    # one level of helper follow (B2669: helpers hid keys from the scan)
    for h in set(re.findall(r"(_has_[a-z_]+)\(s\)", src)):
        try:
            k2, b2 = scan(inspect.getsource(getattr(module, h)))
            keys |= k2
            bools |= b2
        except Exception as e:  # noqa: BLE001 - logged, never silent
            print(f"  helper-follow failed for {h}: {type(e).__name__}")
    return keys, bools


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-fires", type=int, default=75,
                    help="min recorded fires for FULLY-FREE (the full-period "
                         "trade-count gate; below it no offline campaign can "
                         "clear the gates anyway)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()

    from backtest import config as _cfg
    from backtest.signals import screener
    from backtest.signals.screener import ALL_STRATEGIES
    # disabled sets live in backtest.config (screener imports them at its
    # own call sites, screener.py:8478-8480); absent name = empty, LOGGED
    disabled = set()
    for _name in ("DEPRECATED_STRATEGIES", "STRATEGIES_DISABLED_DATA_SCARCITY",
                  "STRATEGIES_DISABLED_DUPLICATE",
                  "STRATEGIES_DISABLED_MISSING_PRODUCER"):
        _s = getattr(_cfg, _name, None)
        if _s is None:
            print(f"  note: config has no {_name} (treated empty)")
        else:
            disabled |= set(_s)
    active = {k: v for k, v in ALL_STRATEGIES.items() if k not in disabled}

    tl = pd.read_csv(TRADE_LOG, low_memory=False,
                     usecols=["strategy", "signals_at_entry"])
    fire_counts = tl["strategy"].value_counts().to_dict()
    keyspace: set[str] = set()
    # STRIDE sample across the whole log - a head() sample missed sparse
    # true-only keys (insider_cluster_active, caught by the L644 hand-read)
    stride = max(1, len(tl) // KEY_SAMPLE_ROWS)
    for s in tl["signals_at_entry"].iloc[::stride]:
        keyspace |= set(_parse(s).keys())
    print(f"keyspace {len(keyspace)} keys from {KEY_SAMPLE_ROWS} sampled trades; "
          f"{len(active)} active strategies ({time.time()-t0:.0f}s)")

    rows = []
    for name, fn in sorted(active.items()):
        keys, bools = consumed_keys(fn, screener)
        persisted = (keys & keyspace) | (bools & keys)
        missing = sorted((keys - bools) - keyspace)
        fires = int(fire_counts.get(name, 0))
        frac = len(persisted) / len(keys) if keys else 0.0
        if fires >= a.min_fires and keys and not missing:
            label = "FULLY-FREE"
        elif fires > 0 and frac >= 0.5:
            label = "PARTIAL"
        else:
            label = "NEEDS-ENGINE"
        rows.append({"strategy": name, "label": label,
                     "recorded_fires": fires,
                     "keys_consumed": len(keys),
                     "keys_persisted": len(persisted),
                     "keys_missing": missing})

    counts = {}
    for r in rows:
        counts[r["label"]] = counts.get(r["label"], 0) + 1
    rec = {"_doc": ("B2677 offline-gradability census (S6-B2638c) - a "
                    "feasibility SCREEN for campaign planning, never a gate; "
                    "labels per the module docstring, limits stated there"),
           "active_strategies": len(active),
           "registered": len(ALL_STRATEGIES),
           "min_fires": a.min_fires,
           "keyspace_size": len(keyspace),
           "counts": counts,
           "rows": rows}
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"census: {counts} over {len(active)} actives -> {a.out} "
          f"({time.time()-t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
