"""S6-B1248-LEVER4-GATE-BUDGET: how many conditions each open LONG side ANDs.

LEVER4 proposes rewriting the most condition-stacked strategies to fire when
most of their conditions agree (k of m) instead of all. Before scope, form or
k is chosen this counts the stack per LONG side - the side the owner's 30-long
target needs (S6-B3220). A k-of-m rewrite LOOSENS a gate (it adds fires no
cube holds), so grading one needs engine runs; this census grades nothing.

METHOD. Per registered strategy, per LONG side (a _strat3's fires_long, or a
_strat whose direction is 'long'): the AND operands of every assignment to
the side's fires variable - a re-assignment `fl = fl and X` adds X's
operands, and a reference to another name counts once - plus one per
early-return guard. Hand-checked against the screener source: hull_rsi's
long side ANDs 4 legs, squeeze_breakout's 1 (pinned by test_b1248_lever4_
census_counts_each_long_sides_and_legs). Open means the status view row is
NOT-STARTED or STALLED-CAMPAIGN; the run refuses a status it does not
classify, so a new status can never silently fall on either side.

A LEVER4 side (screener._gate_budget, S6-B1248-LEVER4 B3139q-r81) is read as
the AND of its legs - its production meaning - one condition per leg, the
leg's thunk body as the operand, so a restructured strategy keeps its count.

    python scripts/lever4_condition_census.py [--out PATH]
writes output_audit/b3139_lever4_condition_census.json. B3139q-r81: any
other argument is refused before anything is written - the script once took
any argv, and a `--help` probe overwrote the committed artifact.
"""
import argparse
import ast
import json
import sys
from collections import Counter
from pathlib import Path


def _root() -> Path:
    """The repo root, resolved by MARKER (L846): the script's own parent
    tree when installed in scripts/, else the working directory - refused
    unless backtest/signals/screener.py is there."""
    for c in (Path(__file__).resolve().parents[1], Path.cwd()):
        if (c / "backtest" / "signals" / "screener.py").is_file():
            return c
    raise SystemExit("cannot find the repo root (backtest/signals/screener.py) - refusing")


ROOT = _root()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import signals_used_lint as sul  # noqa: E402

OUT = ROOT / "output_audit" / "b3139_lever4_condition_census.json"
VIEW = ROOT / "output_audit" / "strategy_optimisation_status.json"
OPEN = {"NOT-STARTED", "STALLED-CAMPAIGN"}
# S6-B3303 (B3139q-r115): an owner-opened campaign owns its strategy, so it
# is not open for a rewrite. MEASURED r115: without this class the census
# refused the view's IN-CAMPAIGN rows (exit 1). Classified BY HAND on
# purpose - a new status must refuse here, not fall silently on a side -
# and test_b3303 holds OPEN | BUSY | CLOSED equal to the builder's
# build_strategy_status.ALL_STATUSES, so the next status fails a pin at the
# commit that adds it instead of this run weeks later.
BUSY = {"IN-CAMPAIGN"}
CLOSED = {"DONE-ADMITTED", "IN-ROSTER-FUNNEL", "IN-ROSTER-MIRROR", "DONE-OWNER-CLOSED",
          "CLOSED-NO-READ", "DISABLED", "PRUNED-DUPLICATE", "CLOSED-NEGATIVE",
          "CONTAINED-IN-REPRESENTATIVE"}


def budget_legs(node):
    """The leg thunk bodies of a `_gate_budget(name, ((leg, thunk), ...))`
    call (S6-B1248-LEVER4), or None when `node` is not one."""
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "_gate_budget" and len(node.args) == 2
            and isinstance(node.args[1], (ast.Tuple, ast.List))):
        return [e.elts[1].body for e in node.args[1].elts
                if isinstance(e, (ast.Tuple, ast.List)) and len(e.elts) == 2
                and isinstance(e.elts[1], ast.Lambda)]
    return None


def and_ops(node):
    legs = budget_legs(node)
    if legs is not None:
        out = []
        for leg in legs:
            out += and_ops(leg)
        return out
    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
        out = []
        for v in node.values:
            out += and_ops(v)
        return out
    return [node]


def conditions(fn, var):
    ops = []
    for st in ast.walk(fn):
        if (isinstance(st, ast.Assign) and len(st.targets) == 1
                and isinstance(st.targets[0], ast.Name) and st.targets[0].id == var):
            ops += [ast.unparse(o) for o in and_ops(st.value)
                    if not (isinstance(o, ast.Name) and o.id == var)]
    return ops


def long_side_rows(names=None) -> list:
    """One row per registered LONG side: strategy, declaration, conditions,
    operands, early-return guards. `names` limits the strategies (the pin's
    seam); None reads every registration."""
    from backtest.signals import index_rebalance, screener
    from backtest.signals.screener import ALL_STRATEGIES
    mods = {"backtest.signals.screener": sul.Module.of(screener),
            "backtest.signals.index_rebalance": sul.Module.of(index_rebalance)}
    rows = []
    for name, f in ALL_STRATEGIES.items():
        if names is not None and name not in names:
            continue
        fn = mods[f.__module__].funcs[f.__name__]
        guards = sum(1 for n in ast.walk(fn) if isinstance(n, ast.If) and any(
            isinstance(b, ast.Return) and sul._is_decl(b.value)
            and isinstance(b.value.args[0], ast.Constant) for b in n.body))
        for c in [c for c in ast.walk(fn) if sul._is_decl(c)]:
            long_side = c.func.id == "_strat3" or (
                len(c.args) > 1 and isinstance(c.args[1], ast.Constant)
                and c.args[1].value == "long")
            fx = c.args[0]
            if not long_side or not isinstance(fx, ast.Name):
                continue
            ops = conditions(fn, fx.id)
            rows.append({"strategy": name, "declaration": c.func.id,
                         "conditions": len(ops) + guards, "operands": ops,
                         "early_return_guards": guards})
    return rows


def main(argv=None) -> int:
    global OUT
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", help=f"write here instead of {OUT}")
    a = ap.parse_args(argv)
    if a.out:
        OUT = Path(a.out)
    view = {r["strategy"]: r for r in json.loads(VIEW.read_text(encoding="utf-8"))["rows"]}
    unknown = {r.get("status") for r in view.values()} - OPEN - BUSY - CLOSED
    if unknown:
        raise SystemExit(f"status view has statuses this census does not classify: "
                         f"{sorted(unknown)}")
    rows = long_side_rows()
    for r in rows:
        v = view.get(r["strategy"]) or {}
        r.update(status=v.get("status"), open=v.get("status") in OPEN,
                 r5_fires=v.get("r5_fires"),
                 projected_step1_fires=v.get("projected_step1_fires"))
    opened = [r for r in rows if r["open"]]
    deep = sorted([r for r in opened if r["conditions"] >= 4],
                  key=lambda r: (-r["conditions"], r["strategy"]))
    summary = {"long_sides": len(rows), "open_long_sides": len(opened),
               "open_conditions_distribution": dict(sorted(
                   Counter(r["conditions"] for r in opened).items())),
               "open_long_sides_with_4_plus_conditions": len(deep),
               "deep_open_long_sides": [r["strategy"] for r in deep]}
    OUT.write_bytes((json.dumps({"generator": "scripts/lever4_condition_census.py",
                                 "status_view": VIEW.relative_to(ROOT).as_posix(),
                                 "summary": summary, "rows": rows}, indent=1)
                     + "\n").encode("utf-8"))
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
