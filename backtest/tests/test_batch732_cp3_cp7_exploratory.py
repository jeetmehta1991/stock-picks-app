# Source: B699 audit CP-3 + CP-7 MISS verdict + Decision 2 Group C #11/#12 owner-approval per CHECKLIST #77
"""B732 pin tests: CP-3 head_shoulders_bottom_long + CP-7 triangle_descending_short
marked EXPLORATORY per Decision 2 Group C #11/#12.

Per B699 audit: both patterns MISS textbook synthetic geometry (detection
too strict OR real fire-starvation; Bulkowski 2005 cites ~5-15/yr per
ticker = sub-min_trades by design). EXPLORATORY classification per B652
W5m / B722 po3 precedent: cube measures + records; no production
deployment regardless of cube verdict.

Resolves S4-B699-CHART-PATTERN-CP-3-CP-7-MISS-RESOLUTION (both branches).
"""
from __future__ import annotations


def test_b732_pin1_strat_head_and_shoulders_bottom_long_exploratory_docstring():
    """CP-3 strategy must declare EXPLORATORY + DO NOT DEPLOY in docstring."""
    from backtest.signals.screener import strat_head_and_shoulders_bottom_long
    docstring = strat_head_and_shoulders_bottom_long.__doc__ or ""
    assert "EXPLORATORY" in docstring, (
        "strat_head_and_shoulders_bottom_long must declare EXPLORATORY status post-B732"
    )
    assert "DO NOT DEPLOY" in docstring, (
        "strat_head_and_shoulders_bottom_long docstring must include do-not-deploy warning"
    )


def test_b732_pin2_strat_triangle_descending_short_exploratory_docstring():
    """CP-7 strategy must declare EXPLORATORY + DO NOT DEPLOY in docstring."""
    from backtest.signals.screener import strat_triangle_descending_short
    docstring = strat_triangle_descending_short.__doc__ or ""
    assert "EXPLORATORY" in docstring
    assert "DO NOT DEPLOY" in docstring


def test_b732_pin3_strategies_still_registered():
    """Both CP-3 and CP-7 remain in ALL_STRATEGIES (EXPLORATORY != deletion)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "head_and_shoulders_bottom_long" in ALL_STRATEGIES, (
        "CP-3 should still be registered (EXPLORATORY, not deleted)"
    )
    assert "triangle_descending_short" in ALL_STRATEGIES
