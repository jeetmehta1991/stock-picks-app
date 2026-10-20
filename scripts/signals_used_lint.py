"""S6-B3139c: every strategy's declared signals_used list names exactly the
signal keys its fire decision reads.

WHY: backtest/agents/pipeline.py (run_technical_agent) passes a declared
name to the Phase-1B agents only when it is an EXACT key of the signal dict.
A comparator string ('rsi_14<50'), a composite ('(a OR b)'), a concept label
('smart_money_buy') or a stale key (a gate retuned from vol_spike_15x to
vol_spike_12x without its list) reaches no agent, and a gate input left off
the list reaches them only if it sits in the pipeline's fixed context list.
MEASURED B3139q-r72s with this tool: 181 of 285 declaration sides drifted,
across 144 of 225 strategies. (The B3139 detector's 94 - literal reads
against the declared lists - was never committed, so its exact definition is
not recoverable; this tool follows helpers, guards and per-side attribution.)

THE RULE, per side (a _strat3 has a long and a short side): the declared
list is the keys that FEED that side's fire decision - read in the fires
expression, in every assignment to a name it references (transitively), in
the test of an early-return guard (an `if` whose body returns a
constant-fires declaration), and inside every module-level helper called
with the signal dict there - plus 'borrow_ok' where the side calls
_short_borrow_trap_active (the B744 lint's marker). Keys read only for
bullet text are not triggers and are not listed. A key whose name is built
at runtime (an f-string over a span knob) is listed as the same expression.
A declaration whose fires argument is a constant (an early return of False)
is never consumed and is left as it is.

    python scripts/signals_used_lint.py            # report
    python scripts/signals_used_lint.py --check    # exit 1 on any drift
    python scripts/signals_used_lint.py --json PATH

Pinned by test_b3139c_every_declared_signal_list_names_the_keys_its_gate_reads.
"""
import argparse
import ast
import inspect
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BORROW_HELPER, BORROW = "_short_borrow_trap_active", "borrow_ok"
# declaration helper -> (fires argument positions, list argument positions)
DECL = {"_strat": ((0,), (3,)), "_strat3": ((0, 1), (3, 4)), "_strat_signal": ((0,), (3,))}
DECL_KW = {"_strat": ("signals_used",), "_strat3": ("signals_used_long", "signals_used_short"),
           "_strat_signal": ("signals_used",)}
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class Module:
    """A parsed source file: its text, tree and module-level functions."""

    def __init__(self, src: str, path: str = "<source>"):
        self.path = Path(path)
        self.src = src
        self.tree = ast.parse(src)
        self.funcs = {n.name: n for n in self.tree.body if isinstance(n, ast.FunctionDef)}

    @classmethod
    def of(cls, mod):
        p = Path(inspect.getsourcefile(mod))
        return cls(p.read_text(encoding="utf-8"), str(p))

    def seg(self, node):
        return ast.get_source_segment(self.src, node)


def _key(node, mod):
    """('lit', key) for a literal key; ('dyn', source) for a built one."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return ("lit", node.value)
    return ("dyn", mod.seg(node) or ast.unparse(node))


def _reads(expr, sname, mod, seen):
    keys, names = [], []
    for n in ast.walk(expr):
        if isinstance(n, ast.Call):
            f = n.func
            if (isinstance(f, ast.Attribute) and f.attr == "get" and isinstance(f.value, ast.Name)
                    and f.value.id == sname and n.args):
                keys.append(_key(n.args[0], mod))
            elif isinstance(f, ast.Name) and any(isinstance(a, ast.Name) and a.id == sname
                                                 for a in n.args):
                if f.id == BORROW_HELPER:
                    keys.append(("lit", BORROW))
                elif f.id in mod.funcs and f.id not in seen and not f.id.startswith("strat_"):
                    h = mod.funcs[f.id]
                    hs = h.args.args[0].arg if h.args.args else None
                    for stmt in h.body:
                        keys += _reads(stmt, hs, mod, seen | {f.id})[0]
        elif isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) and n.value.id == sname:
            keys.append(_key(n.slice, mod))
        elif (isinstance(n, ast.Compare) and len(n.ops) == 1
              and isinstance(n.ops[0], (ast.In, ast.NotIn))
              and isinstance(n.comparators[0], ast.Name) and n.comparators[0].id == sname
              and isinstance(n.left, ast.Constant) and isinstance(n.left.value, str)):
            keys.append(("lit", n.left.value))
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            names.append(n.id)
    return keys, names


def _assignments(fn):
    """name -> every expression that decides its value: each value assigned
    to it, AND the test of every if / while enclosing such an assignment -
    control dependence counts (bollinger_lower's vix_band_low and
    vix_band_high choose which RSI threshold its gate compares against)."""
    out = {}

    def add(name, exprs):
        out.setdefault(name, []).extend(exprs)

    def visit(stmts, tests):
        for st in stmts:
            if isinstance(st, ast.Assign):
                for t in st.targets:
                    for tn in ast.walk(t):
                        if isinstance(tn, ast.Name):
                            add(tn.id, [st.value] + tests)
            elif (isinstance(st, (ast.AugAssign, ast.AnnAssign)) and isinstance(st.target, ast.Name)
                  and st.value is not None):
                add(st.target.id, [st.value] + tests)
            if isinstance(st, (ast.If, ast.While)):
                visit(st.body, tests + [st.test])
                visit(st.orelse, tests + [st.test])
            elif isinstance(st, (ast.For, ast.With, ast.Try)):
                for block in ("body", "orelse", "finalbody"):
                    visit(getattr(st, block, []) or [], tests)
                for h in getattr(st, "handlers", []) or []:
                    visit(h.body, tests)
    visit(fn.body, [])
    return out


def _closure(expr, fn, mod, assigns):
    sname = fn.args.args[0].arg
    out, todo, done = [], [expr], set()
    while todo:
        k, names = _reads(todo.pop(0), sname, mod, set())
        out += k
        for nm in names:
            if nm in assigns and nm not in done:
                done.add(nm)
                todo += assigns[nm]
    return list(dict.fromkeys(out))


def _is_decl(node):
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in DECL


def analyse_function(mod: Module, fn: ast.FunctionDef) -> list:
    """The declaration sides of one strategy function: for each, the keys
    that feed it, the declared entries, and the drift between them."""
    assigns = _assignments(fn)
    guards = []
    for n in ast.walk(fn):
        if isinstance(n, ast.If) and any(
                isinstance(b, ast.Return) and _is_decl(b.value)
                and isinstance(b.value.args[0], ast.Constant) for b in n.body):
            guards += _closure(n.test, fn, mod, assigns)
    sides = []
    for c in [c for c in ast.walk(fn) if _is_decl(c)]:
        fire_ix, list_ix = DECL[c.func.id]
        lists = [c.args[i] if i < len(c.args) else None for i in list_ix]
        for kw in c.keywords:
            if kw.arg in DECL_KW[c.func.id]:
                lists[DECL_KW[c.func.id].index(kw.arg)] = kw.value
        for si, (fx, lst) in enumerate(zip([c.args[i] for i in fire_ix], lists)):
            side = ("long", "short")[si] if c.func.id == "_strat3" else "single"
            rec = {"side": side, "module": mod.path.name, "function": fn.name,
                   "list_pos": ([lst.lineno, lst.col_offset, lst.end_lineno, lst.end_col_offset]
                                if lst is not None else None)}
            if isinstance(fx, ast.Constant):
                rec["status"] = "CONSTANT_FIRES"
                sides.append(rec)
                continue
            feeds = list(dict.fromkeys(guards + _closure(fx, fn, mod, assigns)))
            if not isinstance(lst, (ast.List, ast.Tuple)):
                rec.update(status="NONLITERAL_LIST", feeds=feeds)
                sides.append(rec)
                continue
            declared = [_key(e, mod) for e in lst.elts]
            rec.update(status="OK", feeds=feeds, declared=declared,
                       drift=sorted(set(declared) ^ set(feeds), key=str))
            sides.append(rec)
    return sides


def analyse():
    """One row per registered strategy (a pure delegation `return X(s)` to a
    function in index_rebalance is followed to that function)."""
    from backtest.signals import index_rebalance, screener
    from backtest.signals.screener import ALL_STRATEGIES
    mods = {"backtest.signals.screener": Module.of(screener),
            "backtest.signals.index_rebalance": Module.of(index_rebalance)}
    rows = []
    for name, f in ALL_STRATEGIES.items():
        mod = mods[f.__module__]
        fn = mod.funcs[f.__name__]
        body = [b for b in fn.body
                if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant))]
        if (len(body) == 1 and isinstance(body[0], ast.Return) and isinstance(body[0].value, ast.Call)
                and isinstance(body[0].value.func, ast.Name)):
            tgt = getattr(screener, body[0].value.func.id, None)
            if getattr(tgt, "__module__", None) in mods and tgt.__module__ != f.__module__:
                mod = mods[tgt.__module__]
                fn = mod.funcs[tgt.__name__]
        rows.append({"strategy": name, "sides": analyse_function(mod, fn)})
    return rows


def proposed(side) -> list:
    """The corrected list for one side: the declared entries that name a
    feeding key, in place (a comparator or composite string replaced by the
    feeding keys it names), then the feeding keys still absent, in source
    order. Entries naming no feeding key (labels, stale keys) are dropped."""
    lits = {v for t, v in side["feeds"] if t == "lit"}
    out = []
    for t, v in side["declared"]:
        if (t, v) in side["feeds"]:
            cand = [(t, v)]
        else:
            cand = [("lit", tok) for tok in dict.fromkeys(TOKEN.findall(v)) if tok in lits]
        for k in cand:
            if k not in out:
                out.append(k)
    out += [k for k in side["feeds"] if k not in out]
    # the borrow marker closes the list, as every short's list wrote it
    return [k for k in out if k != ("lit", BORROW)] + [k for k in out if k == ("lit", BORROW)]


def drifted(rows) -> list:
    return [(r["strategy"], s["side"]) for r in rows for s in r["sides"]
            if s.get("status") == "OK" and s["drift"]]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 on any drifted side")
    ap.add_argument("--json", help="write the per-strategy rows here")
    a = ap.parse_args(argv)
    rows = analyse()
    bad = drifted(rows)
    nsides = sum(len(r["sides"]) for r in rows)
    print(f"strategies {len(rows)}; declaration sides {nsides}; drifted sides {len(bad)} "
          f"across {len({b[0] for b in bad})} strategies")
    for strat, side in bad:
        print(f"  DRIFT {strat} [{side}]")
    if a.json:
        Path(a.json).write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return 1 if (a.check and bad) else 0


if __name__ == "__main__":
    sys.exit(main())
