# Source: B713 Phase 0 + Decision 3 build #4 + Decision 5 Cat 1 + owner-approved "push forward" 2026-06-13 per CHECKLIST #77
"""B744 borrow-gate lint -- static check that every short-emitting strategy
registered through `backtest/signals/screener.py` declares an explicit borrow
guard at its call site.

Per S4-B713-REGISTRATION-TIME-BORROW-GATE-LINT-BUILD: each strategy whose return
path includes direction="short" output (`_strat(..., "short", ...)` OR `_strat3`
with a SHORT branch) must:
  1. Call `_short_borrow_trap_active(s)` in its function body (the explicit
     borrow gate at the call site).
  2. Declare `"borrow_ok"` in its `signals_used` list passed to `_strat`/`_strat3`.

S6-B3226 (owner ruled 2026-10-20, 'Approve all recs fable mode be extremely
thorough', option (a)) widened what the lint can see, in two ways:
  * A strategy whose screener.py body is one `return <alias>(s)`, where
    <alias> is imported from another backtest.signals module, is FOLLOWED to
    that module's function and checked there (`via` names the file and line).
    The two index-rebalance shorts are defined in index_rebalance.py and
    registered through such one-line delegations; from B744 to S6-B3226 the
    lint read neither as a short, so the invariant's enforcement was blind to
    both. That module declares through its own mirror of `_strat`,
    `_strat_signal`, which is read as a declaration call too.
  * The gate and the declaration are read from the PARSED code - a call node,
    a string constant inside the declared list - not from substrings of the
    function's text, so a docstring or comment naming the gate or 'borrow_ok'
    cannot satisfy them (L748: anchor on something prose cannot produce).
The lint's population is checked against the REGISTRY in the gate tier
(test_b3226_borrow_lint_sees_every_registered_short): every registered
strategy whose empty-signal call returns direction 'short' must be in the
lint's pure-short set, and every one returning None (a _strat3 dual) in its
dual set - a runtime classification the lint's static reading does not
share, so a short this lint cannot see fails that pin.

This complements the per-cohort regression guards in B741/B743 by providing a
single cluster-wide invariant check that runs every pyramid invocation.

Prerequisites met by B740-B743 cohort: all 51 pure-short + 61 dual _strat3
strategies converted to explicit gate.

USAGE
-----
    from scripts.borrow_gate_lint import audit_screener, format_report
    report = audit_screener("backtest/signals/screener.py")
    print(format_report(report))

CLI: `python -m scripts.borrow_gate_lint`

The pyramid pin in `backtest/tests/test_batch744_borrow_gate_lint.py` invokes
this auditor + fails if `report.violations` is non-empty.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

BORROW_GATE = "_short_borrow_trap_active"
BORROW_DECL = "borrow_ok"
# declaration helper -> positions of (signals_used_long, signals_used_short).
# A single-direction helper has one list, at position 3; `_strat_signal` is
# index_rebalance.py's mirror of `_strat` (it cannot import screener).
DECL_HELPERS = {"_strat": (None, 3), "_strat_signal": (None, 3), "_strat3": (3, 4)}
DECL_KEYWORDS = {"_strat": (None, "signals_used"), "_strat_signal": (None, "signals_used"),
                 "_strat3": ("signals_used_long", "signals_used_short")}
SIGNALS_PACKAGE = "backtest.signals."


# --------------------------------------------------------------------------
# Data shapes
# --------------------------------------------------------------------------
@dataclass
class ShortStrategy:
    """One strategy in screener.py whose return path emits direction='short'."""
    name: str
    line: int
    is_dual: bool                  # True if uses _strat3 (long+short); False if pure-short _strat
    has_borrow_gate: bool          # function body calls _short_borrow_trap_active(s)
    has_borrow_ok_declared: bool   # signals_used (or signals_used_short) contains "borrow_ok"
    via: str = ""                  # S6-B3226: "<file>:<line>" of the function a one-line
                                   # screener delegation was followed to; "" when defined here


@dataclass
class LintReport:
    short_strategies: list = field(default_factory=list)
    violations: list = field(default_factory=list)  # list[ShortStrategy] with missing gate/decl
    files_scanned: int = 0
    note: str = ""
    unresolved: list = field(default_factory=list)  # S6-B3226: delegations not followable


# --------------------------------------------------------------------------
# Static analysis
# --------------------------------------------------------------------------
def _function_bodies(src: str) -> list[tuple[str, int, int, int]]:
    """Return list of (function_name, def_line, body_start, body_end_exclusive)
    for every module-level `strat_*` function, from the ast."""
    tree = ast.parse(src)
    out = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("strat_"):
            start = node.lineno - 1
            end = (node.end_lineno or start + 1)
            out.append((node.name, node.lineno, start, end))
    return out


def _decl_calls(fn: ast.FunctionDef) -> list:
    """Every `return <helper>(...)` whose helper is a declaration helper."""
    return [n.value for n in ast.walk(fn)
            if isinstance(n, ast.Return) and isinstance(n.value, ast.Call)
            and isinstance(n.value.func, ast.Name) and n.value.func.id in DECL_HELPERS]


def _is_short_call(call: ast.Call) -> tuple[bool, bool]:
    """(emits_short, is_dual) for one declaration call."""
    if call.func.id == "_strat3":
        return (True, True)
    d = call.args[1] if len(call.args) > 1 else next(
        (k.value for k in call.keywords if k.arg == "direction"), None)
    return (isinstance(d, ast.Constant) and d.value == "short", False)


def _is_short_strategy(fn: ast.FunctionDef) -> tuple[bool, bool]:
    """Returns (emits_short, is_dual) over every declaration the function returns."""
    flags = [_is_short_call(c) for c in _decl_calls(fn)]
    return (any(e for e, _ in flags), any(d for _, d in flags))


def _has_explicit_borrow_gate(fn: ast.FunctionDef) -> bool:
    """The function CALLS `_short_borrow_trap_active` with its signal dict - a
    call node, so a docstring or comment naming the gate does not count."""
    sname = fn.args.args[0].arg if fn.args.args else None
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id == BORROW_GATE
               and any(isinstance(a, ast.Name) and a.id == sname for a in n.args)
               for n in ast.walk(fn))


def _declared_list(call: ast.Call, side: str):
    """The list node a declaration call passes for `side` ('long'/'short')."""
    pos = DECL_HELPERS[call.func.id][0 if side == "long" else 1]
    kw = DECL_KEYWORDS[call.func.id][0 if side == "long" else 1]
    if pos is None:
        return None
    if pos < len(call.args):
        return call.args[pos]
    return next((k.value for k in call.keywords if k.arg == kw), None)


def _names_borrow_ok(node) -> bool:
    return (isinstance(node, (ast.List, ast.Tuple))
            and any(isinstance(e, ast.Constant) and e.value == BORROW_DECL for e in node.elts))


def _short_fires_arg(call: ast.Call):
    """The fires argument of a declaration's SHORT side (args[1] of a
    _strat3, args[0] of a single-direction helper)."""
    i = 1 if call.func.id == "_strat3" else 0
    return call.args[i] if i < len(call.args) else None


def _declares_borrow_ok(fn: ast.FunctionDef) -> bool:
    """Every short-emitting declaration that CAN fire lists the string
    constant 'borrow_ok' in its short-side signals_used list
    (signals_used_short for a _strat3). A declaration whose short fires
    argument is a FALSY constant - an early `return _strat(False, ...)` -
    never emits a trade and is not required to (signals_used_lint's
    CONSTANT_FIRES rule); a constant True fires on every bar and is."""
    def never_fires(arg):
        return isinstance(arg, ast.Constant) and not arg.value
    live = [c for c in _decl_calls(fn) if _is_short_call(c)[0]
            and not never_fires(_short_fires_arg(c))]
    return all(_names_borrow_ok(_declared_list(c, "short")) for c in live)


def _borrow_ok_in_long_branch(fn: ast.FunctionDef) -> bool:
    """A dual `_strat3` that declares 'borrow_ok' in its LONG list (the gate
    is SHORT-only)."""
    return any(_names_borrow_ok(_declared_list(c, "long"))
               for c in _decl_calls(fn) if c.func.id == "_strat3")


def _delegations(tree: ast.Module) -> dict:
    """{alias: (module, function)} for every module-level
    `from backtest.signals.<module> import <function> as <alias>`."""
    out = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(SIGNALS_PACKAGE):
            for a in node.names:
                out[a.asname or a.name] = (node.module, a.name)
    return out


def _delegate_target(fn: ast.FunctionDef, delegations: dict):
    """(module, function) when the function's body - docstring aside - is one
    `return <alias>(<its signal dict>)` naming an imported alias; else None."""
    body = [b for b in fn.body
            if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant))]
    if len(body) != 1 or not isinstance(body[0], ast.Return):
        return None
    call = body[0].value
    sname = fn.args.args[0].arg if fn.args.args else None
    if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
            and call.func.id in delegations and len(call.args) == 1
            and isinstance(call.args[0], ast.Name) and call.args[0].id == sname):
        return None
    return delegations[call.func.id]


def audit_screener(screener_path: str | Path = "backtest/signals/screener.py") -> LintReport:
    path = Path(screener_path)
    if not path.is_file():
        return LintReport(note=f"screener.py not found at {path}")

    tree = ast.parse(path.read_text(encoding="utf-8"))
    delegations = _delegations(tree)
    parsed = {path.resolve(): tree}

    def resolve(module: str, func: str):
        """The FunctionDef and file of a delegated function, read from the
        package directory screener.py lives in (backtest/signals/)."""
        mpath = (path.parent / (module[len(SIGNALS_PACKAGE):].replace(".", "/") + ".py")).resolve()
        if not mpath.is_file():
            return None, mpath
        if mpath not in parsed:
            parsed[mpath] = ast.parse(mpath.read_text(encoding="utf-8"))
        node = next((n for n in parsed[mpath].body
                     if isinstance(n, ast.FunctionDef) and n.name == func), None)
        return node, mpath

    rep = LintReport()
    for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("strat_")]:
        target, via = fn, ""
        tgt = _delegate_target(fn, delegations)
        if tgt is not None:
            node, mpath = resolve(*tgt)
            if node is None:
                rep.unresolved.append(f"{fn.name} -> {tgt[0]}.{tgt[1]} ({mpath})")
                continue
            target = node
            via = f"{mpath.parent.name}/{mpath.name}:{node.lineno}"
        emits_short, is_dual = _is_short_strategy(target)
        if not emits_short:
            continue
        s = ShortStrategy(
            name=fn.name,
            line=fn.lineno,
            is_dual=is_dual,
            has_borrow_gate=_has_explicit_borrow_gate(target),
            has_borrow_ok_declared=_declares_borrow_ok(target),
            via=via,
        )
        rep.short_strategies.append(s)
        # Violation conditions
        if not s.has_borrow_gate or not s.has_borrow_ok_declared:
            rep.violations.append(s)
            continue
        # For dual strategies, also check `borrow_ok` is NOT in long branch
        if is_dual and _borrow_ok_in_long_branch(target):
            rep.violations.append(s)
    rep.files_scanned = len(parsed)
    if rep.unresolved:
        rep.note = f"{len(rep.unresolved)} delegation(s) could not be followed"
    return rep


def format_report(rep: LintReport) -> str:
    L = [
        f"BORROW-GATE LINT  files={rep.files_scanned}  short_strategies={len(rep.short_strategies)}  violations={len(rep.violations)}",
    ]
    if rep.note:
        L.append(f"  note: {rep.note}")
    for u in rep.unresolved:
        L.append(f"  UNRESOLVED delegation: {u}")
    L.append("")
    if rep.violations:
        L.append("VIOLATIONS:")
        for v in rep.violations:
            kind = "dual_strat3" if v.is_dual else "pure_short"
            where = f"line {v.line}" + (f" (via {v.via})" if v.via else "")
            issues = []
            if not v.has_borrow_gate:
                issues.append("missing _short_borrow_trap_active(s) in body")
            if not v.has_borrow_ok_declared:
                issues.append("missing 'borrow_ok' in signals_used")
            L.append(f"  [{kind}] {v.name}  {where}  --  {'; '.join(issues) or 'borrow_ok appears in LONG branch (should be SHORT-only)'}")
    else:
        L.append("OK: every short-emitting strategy declares explicit borrow_ok gate at call site")
    return "\n".join(L)


if __name__ == "__main__":  # pragma: no cover
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "backtest/signals/screener.py"
    rep = audit_screener(target)
    print(format_report(rep))
    sys.exit(0 if not (rep.violations or rep.unresolved) else 1)
