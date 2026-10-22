"""S6-B3252 re-measure (B3139q-r102): every <x>.get(<literal key>, True) read
in backtest/signals/*.py (whole modules, not only strat_ functions), with its
enclosing function; then, on the R5 trade log, how many fires each such gate
saw with the key ABSENT from signals_at_entry - the only fires a True default
changes. screen_instrument's close_above_open applies to every long fire of a
non-mean-reversion strategy (screener.py, the Batch 263 confirmation gate).

Read-only; prints its census and writes nothing.

    python scripts/default_true_read_census.py
"""
import argparse
import ast
import sys
from pathlib import Path

argparse.ArgumentParser(description=__doc__.split("\n")[0]).parse_args()
ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / "backtest" / "signals" / "screener.py").is_file():
    sys.exit(f"REFUSED: {ROOT} is not the repo root (L846)")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

sites = []
for p in sorted((ROOT / "backtest" / "signals").glob("*.py")):
    tree = ast.parse(p.read_text(encoding="utf-8"))
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for n in ast.walk(fn):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "get" and len(n.args) == 2
                    and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)
                    and isinstance(n.args[1], ast.Constant) and n.args[1].value is True):
                sites.append((p.name, fn.name, n.args[0].value))
# nested defs are walked twice (outer and inner): keep the innermost owner
seen = {}
for f, fn, k in sites:
    seen.setdefault((f, k), set()).add(fn)
print(f"default-True .get sites: {len(sites)} (function, key) hits")
for (f, k), fns in sorted(seen.items()):
    print(f"  {f}: key {k!r} in {sorted(fns)}")

import pandas as pd
from backtest.signals.screener import ALL_STRATEGIES
import build_strategy_status as bss
# the two sets are LOCAL to screen_instrument: read them from its source (L593)
_scr = ast.parse((ROOT / "backtest" / "signals" / "screener.py").read_text(encoding="utf-8"))
_si = next(n for n in _scr.body if isinstance(n, ast.FunctionDef) and n.name == "screen_instrument")
_sets = {t.id: ast.literal_eval(a.value) for a in ast.walk(_si) if isinstance(a, ast.Assign)
         for t in a.targets if isinstance(t, ast.Name)
         and t.id in ("MEAN_REVERSION_CATEGORIES", "MEAN_REVERSION_STRATEGIES")}
MEAN_REVERSION_CATEGORIES = _sets["MEAN_REVERSION_CATEGORIES"]
MEAN_REVERSION_STRATEGIES = _sets["MEAN_REVERSION_STRATEGIES"]
print(f"mean-reversion sets read: {len(MEAN_REVERSION_CATEGORIES)} categories, "
      f"{len(MEAN_REVERSION_STRATEGIES)} strategies")
tl = pd.read_csv(ROOT / "output_r5_merged_1_7" / "trade_log.csv", low_memory=False,
                 usecols=["strategy", "ticker", "entry_date", "direction", "signals_at_entry"])
tl = tl.drop_duplicates(["strategy", "ticker", "entry_date"])
sig = [bss._parse_signals(x) for x in tl["signals_at_entry"]]
tl = tl.assign(_sig=sig)
print(f"R5 fires: {len(tl)}")

# strategy categories from the live functions (category is returned per call)
cat = {}
for name, fn in ALL_STRATEGIES.items():
    rows = tl[tl["strategy"] == name]
    for d in rows["_sig"].head(200):
        try:
            r = fn(d)
        except Exception:
            continue
        if r and r.get("category"):
            cat[name] = r["category"]
            break
print(f"categories resolved for {len(cat)} of {tl['strategy'].nunique()} strategies with fires")
nonmr_long = tl[(tl["direction"] == "long") & tl["strategy"].map(
    lambda s: not (s in MEAN_REVERSION_STRATEGIES or cat.get(s) in MEAN_REVERSION_CATEGORIES))]
absent = nonmr_long[nonmr_long["_sig"].map(lambda d: "close_above_open" not in d)]
print(f"screen_instrument close_above_open: non-mean-reversion LONG fires {len(nonmr_long)}, "
      f"key absent on {len(absent)} ({sorted(absent['strategy'].unique())[:10]})")
emp = nonmr_long[nonmr_long["_sig"].map(lambda d: len(d) == 0)]
print(f"  of those, fires with an EMPTY persisted signal dict: {len(emp)}")

# strat_ sites: per strategy reading the key, fires with the key absent
src = (ROOT / "backtest" / "signals" / "screener.py").read_text(encoding="utf-8")
for (f, k), fns in sorted(seen.items()):
    strs = sorted(fn[len("strat_"):] for fn in fns if fn.startswith("strat_"))
    for s in strs:
        rows = tl[tl["strategy"] == s]
        na = int(rows["_sig"].map(lambda d: k not in d).sum())
        print(f"  {s}: key {k!r} absent on {na} of {len(rows)} R5 fires")
