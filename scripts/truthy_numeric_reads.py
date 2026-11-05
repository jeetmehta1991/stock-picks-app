#!/usr/bin/env python
"""S6-B3428 (B3139q-r203, L1012, CHECKLIST #331): a strategy gate that reads a
PERSISTED NUMBER for its truth tests nothing - `s.get("rsi_14", False)` passes
for any non-zero RSI, and NaN is truthy too - so the threshold the strategy's
name promises is not applied. B1145's autonomous loosening executor produced
the one live instance: it applied 'REPLACE rsi_14_oversold -> rsi_14' where the
reviewed recommendation read 'rsi_14 < 35'
(scripts/phase_1_analysis_turn_4.py, its rsi_oversold_with_smart_money_long entry), and
strat_rsi_oversold_with_smart_money_long has tested no RSI level since.

truthy_reads(source)  every `s.get(<literal key>, ...)` in a top-level function
                      consumed for its TRUTH - an and/or operand, an if / ternary
                      / assert test, a `not` operand, a `bool(...)` argument,
                      `_strat`'s first argument, or an and/or chain assigned or
                      returned. A value COALESCE - `s.get(k, 0.0) or 0.0`, an
                      `or` whose other operands are numeric constants - is a
                      None-guard before a comparison, not a truth test, and is
                      excluded (MEASURED B3139q-r203: the 4 days_to_cover /
                      short_interest_pct sites are that form).
numeric_truthy(reads, types)  the reads whose key is persisted as a non-bool
                      number, by the committed type map
                      output_audit/b3428_signal_key_types.json.

The type map is a MEASUREMENT of the R5 trade log (signals_at_entry on its
first 20,000 rows: key -> the value kinds seen). A key absent from it is not
judged (its kind is unmeasured, and the 15 such keys read for truth at
B3139q-r203 are all event flags by name); regenerate with --write-types when
the producer set grows. Pinned by test_b3428, whose frozen set is the one
known instance, shrink-only, until the owner rules S6-B3428.

Usage:
  python scripts/truthy_numeric_reads.py                # list numeric-for-truth reads
  python scripts/truthy_numeric_reads.py --write-types  # re-measure the type map
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCREENER = ROOT / "backtest" / "signals" / "screener.py"
TYPES_JSON = ROOT / "output_audit" / "b3428_signal_key_types.json"
TRADE_LOG = ROOT / "output_r5_merged_1_7" / "trade_log.csv"


def _is_sget(n) -> bool:
    return (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "get" and isinstance(n.func.value, ast.Name)
            and n.func.value.id == "s" and bool(n.args)
            and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str))


def _is_coalesce(op: ast.BoolOp) -> bool:
    """`x or 0.0`: an `or` whose operands other than the s.get reads are all
    numeric constants returns a VALUE, never a truth."""
    if not isinstance(op.op, ast.Or):
        return False
    others = [v for v in op.values if not _is_sget(v)]
    return bool(others) and all(isinstance(v, ast.Constant)
                                and isinstance(v.value, (int, float))
                                and not isinstance(v.value, bool) for v in others)


def _truth_context(n) -> bool:
    cur = n
    while True:
        p = getattr(cur, "_tnr_parent", None)
        if p is None:
            return False
        if isinstance(p, ast.BoolOp):
            if _is_coalesce(p):
                return False
            cur = p
            continue
        if isinstance(p, ast.UnaryOp) and isinstance(p.op, ast.Not):
            return True
        if isinstance(p, (ast.If, ast.While, ast.IfExp, ast.Assert)) and p.test is cur:
            return True
        if isinstance(p, ast.Call) and isinstance(p.func, ast.Name):
            if p.func.id == "bool":
                return True
            if p.func.id in ("_strat", "_strat3") and p.args and p.args[0] is cur:
                return True
            return False
        if isinstance(p, (ast.Assign, ast.Return)):
            # an and/or chain assigned or returned is a truth; a bare read is a value
            return cur is not n
        return False


def truthy_reads(source: str) -> list[tuple[str, str, int]]:
    """(function, key, line) for every s.get read consumed for its truth."""
    tree = ast.parse(source)
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child._tnr_parent = parent
    out = []
    for fn in tree.body:
        if not isinstance(fn, ast.FunctionDef):
            continue
        for n in ast.walk(fn):
            if _is_sget(n) and _truth_context(n):
                out.append((fn.name, n.args[0].value, n.lineno))
    return out


def numeric_truthy(reads, types: dict) -> list[tuple[str, str, int]]:
    """The reads whose key the type map records as a non-bool number."""
    return [r for r in reads if "num" in (types.get(r[1]) or [])]


def measure_types(trade_log: Path = TRADE_LOG, nrows: int = 20000) -> dict:
    import pandas as pd
    kinds = defaultdict(set)
    rows = 0
    for ch in pd.read_csv(trade_log, usecols=["signals_at_entry"], chunksize=5000,
                          nrows=nrows, low_memory=False):
        for s in ch["signals_at_entry"]:
            if not isinstance(s, str) or not s.strip():
                continue
            try:
                d = json.loads(s)
            except Exception:
                try:
                    d = ast.literal_eval(s)
                except Exception:
                    continue
            rows += 1
            for k, v in d.items():
                if isinstance(v, bool):
                    kinds[k].add("bool")
                elif isinstance(v, (int, float)):
                    kinds[k].add("int01" if v in (0, 1) else "num")
                elif v is None:
                    kinds[k].add("none")
                else:
                    kinds[k].add(type(v).__name__)
    if rows == 0:
        raise SystemExit("REFUSED: parsed 0 signal dicts - the reader cannot see the format (L824)")
    return {"rows": rows, "types": {k: sorted(v) for k, v in sorted(kinds.items())}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write-types", action="store_true",
                    help="re-measure the key type map from the R5 trade log and write it")
    a = ap.parse_args(argv)
    if a.write_types:
        m = measure_types()
        doc = {"_doc": ("S6-B3428: signals_at_entry key -> value kinds seen on the first "
                        f"{m['rows']} rows of output_r5_merged_1_7/trade_log.csv (bool / num / "
                        "int01 / none). Written by scripts/truthy_numeric_reads.py --write-types."),
               "rows": m["rows"], "types": m["types"]}
        TYPES_JSON.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {TYPES_JSON.relative_to(ROOT).as_posix()}: {len(m['types'])} keys over {m['rows']} rows")
        return 0
    types = json.loads(TYPES_JSON.read_text(encoding="utf-8"))["types"]
    reads = truthy_reads(SCREENER.read_text(encoding="utf-8"))
    hits = numeric_truthy(reads, types)
    print(f"truthy reads {len(reads)} over {len({k for _, k, _ in reads})} keys; "
          f"numeric-for-truth {len(hits)}")
    for f, k, ln in hits:
        print(f"  backtest/signals/screener.py:{ln} {f} reads {k} (persisted {types[k]}) for truth")
    return 0


if __name__ == "__main__":
    sys.exit(main())
