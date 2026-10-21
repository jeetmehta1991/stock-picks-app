#!/usr/bin/env python
"""S6-B3240 (B3139q-r89): battery step 7's engine anchors for the LEVER4 gate
budget - does the knob a LEVER4 spec sweeps actually REACH each strategy's
gate? Read from the live source's AST, so a comment or a docstring that
merely names a token cannot satisfy a check (L748):

  1 backtest/config.py reads the env var LEVER4_GATE_BUDGET
    (os.environ.get("LEVER4_GATE_BUDGET", ...)) and binds the name
    LEVER4_GATE_BUDGET;
  2 backtest/signals/screener.py validates it at import
    (validate_lever4(_cfg.LEVER4_GATE_BUDGET) at module level), and
    _gate_budget reads _cfg.LEVER4_GATE_BUDGET;
  3 every strategy in screener.LEVER4_LEGS calls _gate_budget with its own
    name, and no other strat_ function does - so the honoured set, the
    registry and the call sites are one set.

run_postconfig's step 7 already proves the knob is READ somewhere and that its
consumer list matches the tree (knob_is_read, knob_consumers); this proves it
reaches the GATE of each strategy a spec can name.

Exit 0 when every check holds, 2 otherwise. Read-only; writes nothing.
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "backtest" / "config.py"
SCREENER = ROOT / "backtest" / "signals" / "screener.py"
KNOB = "LEVER4_GATE_BUDGET"


def _is_env_get(n) -> bool:
    return (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "get" and isinstance(n.func.value, ast.Attribute)
            and n.func.value.attr == "environ" and n.args
            and isinstance(n.args[0], ast.Constant) and n.args[0].value == KNOB)


def _reads_cfg_knob(node) -> bool:
    return any(isinstance(x, ast.Attribute) and x.attr == KNOB
               and isinstance(x.value, ast.Name) and x.value.id == "_cfg"
               for x in ast.walk(node))


def check(sources: dict | None = None) -> list[str]:
    """Problems found (empty = every anchor holds). `sources` maps 'config'
    and 'screener' to source text - the test seam."""
    sources = sources or {}
    cfg_src = sources.get("config") or CONFIG.read_text(encoding="utf-8")
    scr_src = sources.get("screener") or SCREENER.read_text(encoding="utf-8")
    probs = []
    cfg = ast.parse(cfg_src)
    if not any(_is_env_get(n) for n in ast.walk(cfg)):
        probs.append(f"config.py never reads os.environ.get({KNOB!r}, ...)")
    bound = False
    for n in ast.walk(cfg):
        tgt = (n.targets if isinstance(n, ast.Assign) else
               [n.target] if isinstance(n, ast.AnnAssign) else [])
        if any(isinstance(t, ast.Name) and t.id == KNOB for t in tgt):
            bound = True
    if not bound:
        probs.append(f"config.py never binds {KNOB}")

    scr = ast.parse(scr_src)
    if not any(isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
               and isinstance(n.value.func, ast.Name)
               and n.value.func.id == "validate_lever4" and _reads_cfg_knob(n)
               for n in scr.body):
        probs.append("screener.py never validates _cfg.LEVER4_GATE_BUDGET at import")
    funcs = {n.name: n for n in scr.body if isinstance(n, ast.FunctionDef)}
    gb = funcs.get("_gate_budget")
    if gb is None or not _reads_cfg_knob(gb):
        probs.append("screener._gate_budget does not read _cfg.LEVER4_GATE_BUDGET")
    legs = None
    for n in scr.body:
        if (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "LEVER4_LEGS"
                                              for t in n.targets)
                and isinstance(n.value, ast.Dict)):
            legs = {k.value for k in n.value.keys if isinstance(k, ast.Constant)}
    if not legs:
        probs.append("screener.py binds no LEVER4_LEGS dict literal")
        legs = set()
    callers = {}
    for name, fn in funcs.items():
        if not name.startswith("strat_"):
            continue
        for x in ast.walk(fn):
            if (isinstance(x, ast.Call) and isinstance(x.func, ast.Name)
                    and x.func.id == "_gate_budget" and x.args
                    and isinstance(x.args[0], ast.Constant)):
                callers.setdefault(name[len("strat_"):], set()).add(x.args[0].value)
    for s in sorted(legs):
        if callers.get(s) != {s}:
            probs.append(f"strat_{s} does not call _gate_budget({s!r}, ...) "
                         f"(found {sorted(callers.get(s, set()))})")
    for s in sorted(set(callers) - legs):
        probs.append(f"strat_{s} calls _gate_budget but is not in LEVER4_LEGS")
    return probs


def main(argv=None) -> int:
    argparse.ArgumentParser(description=__doc__.split("\n\n")[0]).parse_args(argv)
    probs = check()
    for p in probs:
        print("ANCHOR MISSING:", p)
    print(f"LEVER4 engine anchors: {'OK' if not probs else f'{len(probs)} problem(s)'}")
    return 0 if not probs else 2


if __name__ == "__main__":
    raise SystemExit(main())
