"""S6-B3252 (B3139q-r102, restructured B3139q-r105): every <x>.get(<literal
key>, True) read in backtest/signals/*.py (whole modules, not only strat_
functions), with its enclosing function; then, on the R5 trade log, how many
fires each such gate saw with the key ABSENT from signals_at_entry - the only
fires a True default changes. screen_instrument's close_above_open applies to
every long fire of a non-mean-reversion strategy (screener.py, the Batch 263
confirmation gate).

THE REGISTER (owner ruling 2026-10-22, verbatim "Approve all recs / Implement
now", on the r102 recommendation "(b) for the admitted strategy and (a) for
the rest"): output_audit/b3252_default_true_reads.json names every site with
its ruling - (b) KEEP, pinned, for the reads on an admitted line's path;
(a) FALSE-DEFAULT for the rest, applied when the chain's leg-code closure
opens (S6-B3289). register_check() is the pin's predicate: the live census
must equal the register's (b) sites plus its (a) sites not yet applied, so
a new default-True read, a silently dropped one, or an (a) patch that landed
without flipping `applied` all fail test_b3252.

Read-only as a CLI; prints its census and writes nothing. The exposure pass
streams the 4.6 GB trade log in chunks and keeps no signal dict (B3139q-r105:
the r102 pass parsed every row at once, which the memory budget beside a
running chain cannot carry).

    python scripts/default_true_read_census.py [--no-exposure]
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "output_audit" / "b3252_default_true_reads.json"
SIGNALS_DIR = ROOT / "backtest" / "signals"
TRADE_LOG = ROOT / "output_r5_merged_1_7" / "trade_log.csv"


def _default_true_get(n) -> str | None:
    """The key of a `.get(<str literal>, True)` call node, else None."""
    if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "get" and len(n.args) == 2
            and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)
            and isinstance(n.args[1], ast.Constant) and n.args[1].value is True):
        return n.args[0].value
    return None


def find_sites(signals_dir: Path = SIGNALS_DIR) -> list[tuple[str, str, str]]:
    """Sorted (file, enclosing function, key) triples for every
    `.get(<str literal>, True)` call inside a function body. ast.walk is
    breadth-first, so an outer def is visited before a def nested in it: a
    call is credited to the LAST def that walked it, the innermost."""
    out: set[tuple[str, str, str]] = set()
    for p in sorted(Path(signals_dir).glob("*.py")):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        owner: dict[int, tuple[str, str]] = {}
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for n in ast.walk(fn):
                key = _default_true_get(n)
                if key is not None:
                    owner[id(n)] = (fn.name, key)
        out |= {(p.name, fnm, key) for fnm, key in owner.values()}
    return sorted(out)


def load_register(path: Path = REGISTER) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def register_check(live: list[tuple[str, str, str]], reg: dict) -> list[str]:
    """The pin predicate. Empty = the register describes the code: every
    live default-True read is registered, and every registered read that
    should still be in the code (ruling b, or ruling a not yet applied) is."""
    errs = []
    expected = set()
    for e in reg["sites"]:
        trip = (e["file"], e["function"], e["key"])
        if e["ruling"] not in ("a", "b"):
            errs.append(f"{trip}: ruling must be a or b, got {e['ruling']!r}")
        if e["ruling"] == "b" or not e.get("applied", False):
            expected.add(trip)
    live_set = set(live)
    for trip in sorted(live_set - expected):
        errs.append(f"UNREGISTERED default-True read: {trip}")
    for trip in sorted(expected - live_set):
        errs.append(f"register names a default-True read the code no longer has: {trip}")
    return errs


def exposure(sites, chunksize: int = 200_000) -> dict:
    """Fires where the key was ABSENT from the persisted dict, per site, from
    one streamed pass over the trade log. screen_instrument's site counts
    every non-mean-reversion LONG fire; a strat_ site counts its own
    strategy's fires. No dict is retained."""
    import pandas as pd
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_strategy_status as bss
    from backtest.signals.screener import ALL_STRATEGIES
    _scr = ast.parse((SIGNALS_DIR / "screener.py").read_text(encoding="utf-8"))
    _si = next(n for n in _scr.body if isinstance(n, ast.FunctionDef)
               and n.name == "screen_instrument")
    _sets = {t.id: ast.literal_eval(a.value) for a in ast.walk(_si)
             if isinstance(a, ast.Assign) for t in a.targets
             if isinstance(t, ast.Name)
             and t.id in ("MEAN_REVERSION_CATEGORIES", "MEAN_REVERSION_STRATEGIES")}
    mr_cats, mr_strats = _sets["MEAN_REVERSION_CATEGORIES"], _sets["MEAN_REVERSION_STRATEGIES"]
    strat_keys: dict[str, set] = {}
    for f, fn, k in sites:
        if fn.startswith("strat_"):
            strat_keys.setdefault(fn[len("strat_"):], set()).add(k)
    counts = {("screen_instrument", "close_above_open"): [0, 0]}
    for s, ks in strat_keys.items():
        for k in ks:
            counts[(s, k)] = [0, 0]
    cat: dict = {}
    seen: set = set()
    for ch in pd.read_csv(TRADE_LOG, low_memory=False, chunksize=chunksize,
                          usecols=["strategy", "ticker", "entry_date", "direction",
                                   "signals_at_entry"]):
        for row in ch.itertuples(index=False):
            ident = (row.strategy, row.ticker, row.entry_date)
            if ident in seen:
                continue
            seen.add(ident)
            d = bss._parse_signals(row.signals_at_entry)
            s = row.strategy
            if s not in cat and s in ALL_STRATEGIES and d:
                try:
                    r = ALL_STRATEGIES[s](d)
                    cat[s] = r.get("category") if r else None
                except Exception:
                    cat[s] = None
            if row.direction == "long" and not (s in mr_strats or cat.get(s) in mr_cats):
                c = counts[("screen_instrument", "close_above_open")]
                c[0] += 1
                c[1] += ("close_above_open" not in d)
            for k in strat_keys.get(s, ()):
                c = counts[(s, k)]
                c[0] += 1
                c[1] += (k not in d)
    return {f"{s}:{k}": {"fires": v[0], "key_absent": v[1]} for (s, k), v in counts.items()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--no-exposure", action="store_true",
                    help="census and register check only (no trade-log pass)")
    a = ap.parse_args()
    if not (SIGNALS_DIR / "screener.py").is_file():
        sys.exit(f"REFUSED: {ROOT} is not the repo root (L846)")
    sites = find_sites()
    print(f"default-True .get sites: {len(sites)} (file, function, key)")
    for f, fn, k in sites:
        print(f"  {f}: {fn} reads {k!r}")
    if REGISTER.is_file():
        errs = register_check(sites, load_register())
        print("register check: " + ("CLEAN" if not errs else "; ".join(errs)))
    else:
        print(f"register absent: {REGISTER.relative_to(ROOT)}")
    if a.no_exposure:
        return 0
    ex = exposure(sites)
    for k, v in sorted(ex.items()):
        print(f"  {k}: key absent on {v['key_absent']} of {v['fires']} R5 fires")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
