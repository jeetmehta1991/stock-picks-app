#!/usr/bin/env python
"""S6-B3244 (owner ruled 2026-10-21, 'Approve all recs execute', option (a)):
every NEGATED read of a strategy signal in the fire logic of the registered
strategies, held at a reviewed register.

The standing rule (feedback_never_use_NOT_s_get_pattern) is to read the
POSITIVE symmetric key. Preflight C7 enforces it on ADDED lines by their text,
so a spelling the line scan cannot read went unseen - avwap_50_reclaim's short
side bound `macd_bull = s.get(...)` and negated the NAME. This scan reads the
AST, in every spelling:

  not <an expression holding s.get(...)>    not s.get(k), not bool(s.get(k))
  not NAME, NAME bound from such an expression          the avwap shape
  <either> is False / == False / is not True / != True

over the S6-B3235 FIRE-LOGIC members of every registered strategy - its own
body and every function it reaches, a delegation into another signals module
followed (the index-rebalance strategies live in index_rebalance.py).

Why a negated read is wrong: `not s.get(k)` and `not s.get(k, False)` PASS
when the key is absent - the gate fails OPEN on missing data - and
`not s.get(k, True)` passes when the producer wrote False because its input
was undefined (price_above_ema_200 under a warming EMA is close > NaN, False),
reading 'unknown' as 'the opposite state'. The positive key (below_ema_N =
close < EMA, macd_*_bearish = histogram < 0) is False in both cases.

REVIEWED holds a member only with a stated reason, keyed on (function, the
unparsed expression). The pin (test_b3244) asserts the found set EQUALS the
register in both directions (L587): a new negation fails until it is fixed or
reviewed here, and a fixed one leaves the register in the same change.

Read-only: prints the findings and writes nothing. Exit 0 when the found set
equals REVIEWED, 1 otherwise.
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for _p in (ROOT, ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

# (function, unparsed expression) -> why the negation stays. Each reason names
# the OBSERVABLE property that makes the member safe (L550), not the intent.
REVIEWED = {
    ("strat_52w_high_breakout", "not s.get('break_52w_high')"): (
        "FAIL-CLOSED GUARD (B697): the whole test of an `if` whose only body "
        "is `return _strat(False, ...)` - an absent or False break_52w_high "
        "BLOCKS the fire, so the negation can never let a gate pass"),
    ("strat_smc_equal_highs_bos_short", "s.get('smc_equal_highs_swept') is False"): (
        "EXACT PARTITION of the owner-ruled S6-B2931 split (B3078): no "
        "default, so an absent key is None and the child does NOT fire; the "
        "child fires exactly when the parent's thesis key is False as the "
        "producer computed it (a Python bool, smc_ict.compute_smc_signals), "
        "which a positive key with its own NaN semantics would not partition"),
    ("strat_turtle_soup_bos_short", "s.get('smc_liquidity_swept_up') is False"): (
        "EXACT PARTITION of the owner-ruled S6-B2931 split (B3078): the same "
        "construction as strat_smc_equal_highs_bos_short - absent -> None -> "
        "no fire; smc_liquidity_swept_up is bool(...) in the producer"),
}


def _is_sget(n, sname: str) -> bool:
    return (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "get" and isinstance(n.func.value, ast.Name)
            and n.func.value.id == sname)


def _holds_sget(n, sname: str) -> bool:
    return any(_is_sget(x, sname) for x in ast.walk(n))


def negations(fn) -> list[tuple[int, str, str]]:
    """(line, kind, unparsed) for every negated signal read in the function
    node `fn`, whose FIRST parameter is the signal dict ([] without one)."""
    if not fn.args.args:
        return []
    sname = fn.args.args[0].arg
    bound = set()
    for n in ast.walk(fn):
        if (isinstance(n, (ast.Assign, ast.AnnAssign)) and n.value is not None
                and _holds_sget(n.value, sname)):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            bound |= {t.id for t in targets if isinstance(t, ast.Name)}

    def reads(x) -> bool:
        return _holds_sget(x, sname) or (isinstance(x, ast.Name) and x.id in bound)

    out = []
    for n in ast.walk(fn):
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not) and reads(n.operand):
            out.append((n.lineno, "not", ast.unparse(n)))
        elif (isinstance(n, ast.Compare) and len(n.ops) == 1 and reads(n.left)
              and isinstance(n.comparators[0], ast.Constant)
              and isinstance(n.comparators[0].value, bool)):
            op, v = n.ops[0], n.comparators[0].value
            if ((isinstance(op, (ast.Is, ast.Eq)) and v is False)
                    or (isinstance(op, (ast.IsNot, ast.NotEq)) and v is True)):
                out.append((n.lineno, "compare", ast.unparse(n)))
    return sorted(out)


def find(code=None, names=None) -> dict:
    """{(function, expr): {"module", "line", "kind", "strategies"}} over the
    fire-logic members of every registered strategy (`names` and `code` - a
    build_strategy_status.CodeSide - are the test seams). A registered name
    with no strat_ function in the screener RAISES: it could not be scanned,
    and an unscanned strategy must not read as clean (L642)."""
    import build_strategy_status as bss
    if names is None:
        from backtest.signals.screener import ALL_STRATEGIES
        names = sorted(ALL_STRATEGIES)
    cs = code if code is not None else bss.CodeSide(None)
    strategies = cs.index(bss._SCREENER)["strategies"]
    missing = [n for n in names if "strat_" + n not in strategies]
    if missing:
        raise RuntimeError(f"{len(missing)} registered strategies have no strat_ "
                           f"function in the screener, so they cannot be scanned: "
                           f"{missing[:5]}")
    out = {}
    for name in names:
        for key in cs.members(strategies["strat_" + name]):
            if not key.startswith("fn:"):
                continue
            _kind, mod, fname = key.split(":")
            ix = cs.index(mod)
            fnode = ix["funcs"].get(fname) or ix["strategies"].get(fname)
            if fnode is None:
                continue
            for line, kind, expr in negations(fnode):
                row = out.setdefault((fname, expr), {
                    "module": mod, "line": line, "kind": kind, "strategies": set()})
                row["strategies"].add(name)
    return out


def problems(found: dict, register=None) -> list[str]:
    """Both directions (L587): a found negation not in the register, a
    register entry no longer found, and an entry with no reason."""
    register = REVIEWED if register is None else register
    out = [f"UNREVIEWED {f}: {e} ({found[(f, e)]['module']}:{found[(f, e)]['line']}) "
           "- read the positive symmetric key, or review it into REVIEWED"
           for f, e in sorted(set(found) - set(register))]
    out += [f"STALE {f}: {e} - no longer found; remove it from REVIEWED"
            for f, e in sorted(set(register) - set(found))]
    out += [f"NO REASON {f}: {e}" for (f, e), why in sorted(register.items())
            if not str(why).strip()]
    return out


def main() -> int:
    argparse.ArgumentParser(description=__doc__.split("\n\n")[0]).parse_args()
    found = find()
    for (f, e), r in sorted(found.items()):
        tag = "REVIEWED" if (f, e) in REVIEWED else "UNREVIEWED"
        print(f"{tag:10s} {r['module']}:{r['line']} {f}: {e} "
              f"(reached by {len(r['strategies'])} strategies)")
    bad = problems(found)
    for b in bad:
        print("PROBLEM", b)
    print(f"{len(found)} negated reads found; {len(REVIEWED)} reviewed; "
          f"{len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
