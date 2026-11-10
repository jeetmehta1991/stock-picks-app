#!/usr/bin/env python
"""Which REGISTERED strategies read a signal key - the reach of a producer
change, measured from the gate code, never recalled (S6-B3446, L1015).

A decision to change a producer moves every output key the changed code
feeds, and through those keys every strategy whose gate reads one. MEASURED
B3139q-r214: the S6-B3441 option (a) row named the 5 readers of ONE field,
news_sentiment_5d, for a change to the shared word list - which feeds every
sentiment field the news producer emits, read by 9 registered strategies.
The owner approved on the 5. This answers the second half of that question
for any key set; the first half - which keys a change feeds - is read from
the producer.

Reads backtest/signals/screener.py with ast. A read is `s.get("key", ...)`
or `s["key"]` with a literal key anywhere inside a module-level function,
lambdas included. A function also reads every key read by a module-level
function it calls (the closure - `_short_borrow_trap_active` reads
days_to_cover for every short gate that calls it). A key read through a
variable (`s.get(k)`) is invisible to this scan; `dynamic_reads` counts them
per function so the gap is stated, not hidden. Functions map to their
ALL_STRATEGIES names by identity.

Read-only. Usage: python scripts/key_readers.py KEY [KEY ...] [--union]
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCREENER = ROOT / "backtest" / "signals" / "screener.py"


def _function_reads(tree: ast.Module) -> tuple[dict, dict, dict]:
    """(direct literal reads, module-level calls, dynamic-read count) per
    module-level function name."""
    top = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    reads, calls, dynamic = {}, {}, {}
    for fn in tree.body:
        if not isinstance(fn, ast.FunctionDef):
            continue
        r, c, d = set(), set(), 0
        for node in ast.walk(fn):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "get" and node.args):
                a0 = node.args[0]
                if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                    r.add(a0.value)
                else:
                    d += 1
            elif isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
                    and node.value.id == "s":
                if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                    r.add(node.slice.value)
                else:
                    d += 1
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id in top and node.func.id != fn.name:
                c.add(node.func.id)
        reads[fn.name], calls[fn.name], dynamic[fn.name] = r, c, d
    return reads, calls, dynamic


def closure_reads(src: str | None = None) -> tuple[dict, dict]:
    """function name -> every literal key it reads directly or through the
    module-level functions it calls; and the dynamic-read counts."""
    tree = ast.parse(src if src is not None else SCREENER.read_text(encoding="utf-8"))
    reads, calls, dynamic = _function_reads(tree)
    out = {}
    for name in reads:
        seen, stack, keys = {name}, [name], set()
        while stack:
            f = stack.pop()
            keys |= reads.get(f, set())
            for g in calls.get(f, ()):
                if g not in seen:
                    seen.add(g)
                    stack.append(g)
        out[name] = keys
    return out, dynamic


def readers(keys, src: str | None = None, strategies: dict | None = None) -> dict:
    """key -> sorted registered strategy names whose gate reads it."""
    if strategies is None:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from backtest.signals.screener import ALL_STRATEGIES as strategies
    by_fn: dict = {}
    for name, f in strategies.items():
        by_fn.setdefault(getattr(f, "__name__", ""), []).append(name)
    fn_keys, _dyn = closure_reads(src)
    out = {}
    for k in keys:
        names = []
        for fn, ks in fn_keys.items():
            if k in ks:
                names.extend(by_fn.get(fn, []))
        out[k] = sorted(set(names))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Registered strategies whose gate reads "
                                             "each signal key (screener.py AST, read-only).")
    ap.add_argument("keys", nargs="+", help="signal keys")
    ap.add_argument("--union", action="store_true", help="also print the union over the keys")
    a = ap.parse_args(argv)
    res = readers(a.keys)
    for k in a.keys:
        print("%s: %d strategies: %s" % (k, len(res[k]), ", ".join(res[k]) or "-"))
    if a.union:
        u = sorted(set().union(*res.values()))
        print("UNION over %d keys: %d strategies: %s" % (len(a.keys), len(u), ", ".join(u)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
