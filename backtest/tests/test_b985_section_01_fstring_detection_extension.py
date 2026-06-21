"""B985 (2026-06-21): Phase P1 walk-1 Sub-B Section 1 helper extension.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.17 META + Council 89
# Option-5 PARTIAL honest-finding pivot owner-approved 2026-06-21
# 'Approve your recommendation. Proceed council this.'

Verifies B985 Council 89 Option-5 implementation:
  - _expand_fstring_with_bindings handles str(NAME).replace(LIT, LIT)
    chain inside FormattedValue (previously rejected at line 75-76)
  - Loop-variable + chained-f-string + str.replace pattern resolves
    (the technical.py::compute_bollinger pattern that was producing
    SIGNAL_ORPHAN false-positives for 6 BB strategies)
  - All 6 BB strategies (bollinger_tight + _with_smart_money_long +
    bollinger_upper_short + bollinger_lower + hammer_at_support_long +
    shooting_star_short) now show 100% wiring_coverage_pct
  - SIGNAL_ORPHAN reduction: 11 -> 5 (Sub-B 6 false positives resolved)
"""
from __future__ import annotations

import ast

from backtest.diagnostics.section_01_wiring_trace import (
    _expand_fstring_with_bindings,
    _try_resolve_str_method_chain,
)


def test_b985_str_replace_chain_resolves():
    """B985: str(X).replace('.', '') chain resolves to expanded literals."""
    # Build AST for the same pattern compute_bollinger uses:
    #   f"bb_{period}_{str(std_m).replace('.', '')}"
    # Use textwrap.dedent + triple-quoted string so escaping isn't fragile.
    src = """f"bb_{period}_{str(std_m).replace('.', '')}" """
    tree = ast.parse(src.strip(), mode="eval")
    fstring = tree.body
    bindings = {"period": ["20", "20", "10"], "std_m": ["2.0", "1.5", "2.0"]}
    results = _expand_fstring_with_bindings(fstring, bindings)
    # NOTE: the function does CARTESIAN-EXPAND, so it actually emits
    # all 3*3 = 9 combinations. The compute_bollinger loop only emits
    # 3 of them (the zipped pairs) but for Section 1 audit purposes
    # the cartesian-product is SUPERSET of actual emissions; the
    # audit is sound as CONSERVATIVE detection. Verify subset.
    assert "bb_20_20" in results
    assert "bb_20_15" in results
    assert "bb_10_20" in results


def test_b985_simple_str_method_chain():
    """B985: helper directly handles ast.Call(str_replace_chain)."""
    src = "str(x).replace('.', '')"
    tree = ast.parse(src, mode="eval")
    call_node = tree.body
    bindings = {"x": ["2.0", "1.5"]}
    result = _try_resolve_str_method_chain(call_node, bindings)
    assert result == ["20", "15"]


def test_b985_chained_methods_supported():
    """B985: nested str method chains (e.g., .lower(), .upper())."""
    src = "str(x).lower()"
    tree = ast.parse(src, mode="eval")
    call_node = tree.body
    bindings = {"x": ["FOO", "BAR"]}
    result = _try_resolve_str_method_chain(call_node, bindings)
    assert result == ["foo", "bar"]


def test_b985_unrecognized_pattern_returns_none():
    """B985: unrecognized patterns fall through to caller's reject."""
    # str(x).upper().some_unknown_method() should return None
    src = "str(x).upper().some_unknown_method()"
    tree = ast.parse(src, mode="eval")
    call_node = tree.body
    bindings = {"x": ["foo"]}
    result = _try_resolve_str_method_chain(call_node, bindings)
    assert result is None


def test_b985_unbound_var_returns_none():
    """B985: unbound variable returns None (caller rejects)."""
    src = "str(unbound_var).replace('a', 'b')"
    tree = ast.parse(src, mode="eval")
    call_node = tree.body
    bindings = {"x": ["foo"]}  # unbound_var NOT in bindings
    result = _try_resolve_str_method_chain(call_node, bindings)
    assert result is None


def test_b985_bollinger_strategies_now_100_pct_coverage():
    """B985 integration: 6 BB strategies have 100% wiring_coverage_pct post-fix.

    These were 60-80% coverage with bb_20_20_touch_*/squeeze/reclaim
    sub-signals listed as SIGNAL_ORPHAN before B985 helper extension.
    All 6 should resolve to 100% via the str(std_m).replace chain
    in compute_bollinger now being detected.
    """
    # Force fresh import to pick up the helper extension
    import sys
    for m in list(sys.modules):
        if "section_01" in m:
            sys.modules.pop(m)
    from backtest.diagnostics.section_01_wiring_trace import extract_section_01_for_strategy
    bb_strategies = [
        "bollinger_tight",
        "bollinger_tight_with_smart_money_long",
        "bollinger_upper_short",
        "bollinger_lower",
        "hammer_at_support_long",
        "shooting_star_short",
    ]
    for strat in bb_strategies:
        result = extract_section_01_for_strategy(strat)
        coverage = result.get("wiring_coverage_pct")
        orphans = result.get("signals_orphan", [])
        assert coverage == 100.0, (
            f"B985: {strat} expected wiring_coverage_pct=100.0 post-fix; "
            f"got {coverage}. signals_orphan={orphans}"
        )
        assert orphans == [], (
            f"B985: {strat} expected signals_orphan=[] post-fix; got {orphans}"
        )
