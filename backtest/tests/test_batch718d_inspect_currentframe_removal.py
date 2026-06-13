# Source: S4-B713-INSPECT-CURRENTFRAME-REVERT-TO-EXPLICIT-GATE final cleanup + owner-approved "push forward" 2026-06-13 per CHECKLIST #77
"""B718d pin tests: inspect.currentframe central borrow guard REMOVED from
`_strat` + `_strat3` helpers.

After B740-B744 ship the explicit per-strategy borrow gate + cluster-wide
lint, the original central guard in the shared helpers becomes redundant.
B718d removes it.

Structural invariants verified here:
- Live code paths in `_strat` / `_strat3` do NOT call `inspect.currentframe()`
  (docstring mentions are allowed -- they document the migration).
- `_strat` / `_strat3` no longer import the `inspect` module at function scope.
- `_strat` is now a pure return-dict constructor (no direction-specific branching).
- The explicit per-strategy gate continues to block shorts under high DTC
  (re-asserts the B740/B741/B742/B743 behavior at the helper level).
"""
from __future__ import annotations

import ast
from pathlib import Path


SCREENER_PATH = Path(__file__).resolve().parents[2] / "backtest" / "signals" / "screener.py"


def _function_node(name: str) -> ast.FunctionDef:
    src = SCREENER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name} not found in screener.py")


def _function_body_text(name: str) -> str:
    """Return the function's body source (excluding the def line + docstring)."""
    src = SCREENER_PATH.read_text(encoding="utf-8")
    lines = src.splitlines()
    node = _function_node(name)
    body_start = node.lineno  # 1-based; first body line is right after `def ...:`
    body_end = (node.end_lineno or body_start + 1)
    body_lines = lines[body_start:body_end]
    # strip the docstring (first body statement if it's an Expr/Str)
    first = node.body[0] if node.body else None
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
        doc_end = (first.end_lineno or body_start + 1)
        body_lines = lines[doc_end:body_end]
    return "\n".join(body_lines)


def test_b718d_pin1_strat_body_does_not_use_inspect_currentframe():
    """`_strat` function body (excluding docstring) must NOT call inspect.currentframe."""
    body = _function_body_text("_strat")
    assert "inspect.currentframe" not in body, (
        "_strat body still uses inspect.currentframe; expected B718d removal:\n"
        + body
    )


def test_b718d_pin2_strat3_body_does_not_use_inspect_currentframe():
    """`_strat3` function body (excluding docstring) must NOT call inspect.currentframe."""
    body = _function_body_text("_strat3")
    assert "inspect.currentframe" not in body, (
        "_strat3 body still uses inspect.currentframe; expected B718d removal:\n"
        + body
    )


def test_b718d_pin3_strat_does_not_import_inspect():
    """`_strat` function body must NOT contain `import inspect`."""
    body = _function_body_text("_strat")
    assert "import inspect" not in body, (
        "_strat body imports inspect; expected B718d removal"
    )


def test_b718d_pin4_strat3_does_not_import_inspect():
    """`_strat3` function body must NOT contain `import inspect`."""
    body = _function_body_text("_strat3")
    assert "import inspect" not in body


def test_b718d_pin5_strat_is_pure_return_dict_constructor():
    """`_strat` body is now a single return statement (no direction-specific branches)."""
    node = _function_node("_strat")
    # body[0] = docstring; body[1] = return
    non_docstring_body = [
        n for n in node.body
        if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
                and isinstance(n.value.value, str))
    ]
    assert len(non_docstring_body) == 1, (
        f"_strat should be a single return statement post-B718d; got {len(non_docstring_body)} body nodes"
    )
    assert isinstance(non_docstring_body[0], ast.Return)


def test_b718d_pin6_explicit_gate_still_blocks_short_via_helper_call():
    """Functional re-assertion: the explicit per-strategy gate (added in
    B740-B743) still blocks shorts at the call site, even though the central
    inspect.currentframe guard is gone.

    Picks one B740 strategy (strat_rsi_overbought_short) and one B742 strategy
    (strat_pivot_s1_bounce) as representatives.
    """
    from backtest.signals.screener import (
        strat_rsi_overbought_short,
        strat_pivot_s1_bounce,
    )
    # B740 pure-short: under high DTC, the strategy's own gate forces fires=False
    s_short_trap = {
        "rsi_14": 75, "below_sma_50": True, "bearish_engulfing": True,
        "days_to_cover": 10.0,  # trap active via explicit gate
    }
    r1 = strat_rsi_overbought_short(s_short_trap)
    assert r1["fires"] is False, f"B740 explicit gate failed: {r1}"

    # B742 dual: SHORT branch blocked under high DTC; LONG branch unaffected
    s_dual_short_trap = {
        "near_r1": True, "shooting_star": True, "obv_bearish": True,
        "days_to_cover": 10.0,
        "near_s1": False,
    }
    r2 = strat_pivot_s1_bounce(s_dual_short_trap)
    # SHORT branch must NOT fire
    assert not (r2["fires"] and r2["direction"] == "short"), (
        f"B742 explicit short gate failed: {r2}"
    )

    # LONG branch with high DTC still fires (gate is SHORT-only)
    s_dual_long_ok = {
        "near_s1": True, "hammer": True, "obv_bullish": True,
        "days_to_cover": 10.0,
        "near_r1": False,
    }
    r3 = strat_pivot_s1_bounce(s_dual_long_ok)
    assert r3["fires"] is True and r3["direction"] == "long", (
        f"B742 LONG branch should fire despite DTC=10 (gate is SHORT-only): {r3}"
    )
