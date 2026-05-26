"""Batch 365 Item 3: per-criterion empirical evaluability gate in metrics.py.

Source (per CHECKLIST #77): owner approval 2026-05-25 of 3 hardening items
after the Batch 363 silent gap. Pre-Batch-365 behavior: when smart_money_
score==0 across all trades (the silent-gap state), sm_lift evaluated to
None and the passing-criterion #7 short-circuited to auto-pass via
`(sm_lift is None) or (sm_lift >= SM_LIFT_THRESHOLD)`. Result: criterion
#7 was reported as PASS even though it was UNCOMPUTABLE.

Item 3 surfaces criterion_evaluable dict so downstream winners.parquet
extraction can refuse to write when critical criteria can't be
empirically computed. The "auto-pass on None" short-circuit is retained
(strategies without smart money signal aren't penalized) but evaluability
is now explicit so it can't hide a silent gap.

Pyramid tiers exercised:
  T1 (Unit)        criterion_evaluable dict surfaces in metrics output
  T1 (Unit)        smart_money_lift evaluable=False when all trades have
                   smart_money_score=0
  T1 (Unit)        macro_correlation evaluable=False when all trades
                   have macro_score=0
  T1 (Unit)        Both evaluable=True when samples present on both sides
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO))

from backtest.results.metrics import compute_strategy_metrics  # noqa: E402


def _make_trades(*, n: int, sm_score: int, macro_score: int):
    """Build a synthetic trade-log group satisfying min-n criteria.

    `compute_strategy_metrics(df, strategy)` filters df by strategy name
    so we tag every row with the same strategy name."""
    return pd.DataFrame({
        "ticker":             ["AAPL"] * n,
        "strategy":           ["dummy"] * n,
        "category":           ["test"] * n,
        "regime":             (["bull"] * (n // 2)) + (["bear"] * (n - n // 2)),
        "direction":          ["long"] * n,
        "pnl_pct":            ([2.0] * (n // 2)) + ([-1.0] * (n - n // 2)),
        "win":                ([True] * (n // 2)) + ([False] * (n - n // 2)),
        "hold_days":          [5] * n,
        "entry_price":        [100.0] * n,
        "exit_price":          [101.0] * n,
        "smart_money_score":  [sm_score] * n,
        "macro_score":        [macro_score] * n,
        "sentiment_score":    [0] * n,
        "exit_reason":         ["trailing_stop"] * n,
        "entry_date":          ["2024-06-01"] * n,
        "exit_date":           ["2024-06-15"] * n,
    })


def test_batch365_criterion_evaluable_key_present_in_metrics():
    """The metrics dict for any strategy must include the
    `criterion_evaluable` key (Batch 365 Item 3 contract)."""
    g = _make_trades(n=60, sm_score=0, macro_score=0)
    m = compute_strategy_metrics(g, "dummy")
    assert "criterion_evaluable" in m, (
        "Batch 365 Item 3: criterion_evaluable dict must be in metrics output"
    )
    ce = m["criterion_evaluable"]
    assert "smart_money_lift" in ce
    assert "macro_correlation" in ce


def test_batch365_smart_money_lift_unevaluable_when_all_zero():
    """The Batch 363 silent gap state: all trades have smart_money_score=0.
    sm_lift returns None AND criterion_evaluable.smart_money_lift.evaluable
    must be False so downstream consumers know to flag this."""
    g = _make_trades(n=60, sm_score=0, macro_score=2)
    m = compute_strategy_metrics(g, "dummy")
    ce = m["criterion_evaluable"]
    assert ce["smart_money_lift"]["evaluable"] is False, (
        "Batch 363 silent-gap regression: all smart_money_score=0 but "
        "criterion_evaluable.smart_money_lift.evaluable is True"
    )
    # Need 30 with signal AND 30 without; we have 0 with, 60 without
    assert ce["smart_money_lift"]["n_with_signal"] == 0
    assert ce["smart_money_lift"]["n_without_signal"] == 60
    assert ce["smart_money_lift"]["blocked_reason"] is not None
    assert "n=0" in ce["smart_money_lift"]["blocked_reason"]


def test_batch365_smart_money_lift_evaluable_when_mixed():
    """When some trades have smart_money_score>=2 and some have <2,
    the criterion is evaluable."""
    # 30 with sm_score=3 + 30 with sm_score=0
    g_high = _make_trades(n=30, sm_score=3, macro_score=0)
    g_low  = _make_trades(n=30, sm_score=0, macro_score=0)
    g = pd.concat([g_high, g_low], ignore_index=True)
    m = compute_strategy_metrics(g, "dummy")
    ce = m["criterion_evaluable"]
    assert ce["smart_money_lift"]["evaluable"] is True
    assert ce["smart_money_lift"]["n_with_signal"] == 30
    assert ce["smart_money_lift"]["n_without_signal"] == 30
    assert ce["smart_money_lift"]["blocked_reason"] is None


def test_batch365_macro_correlation_unevaluable_when_all_neutral():
    """All trades with macro_score=1 (neither >=2 nor <0) -> macro
    correlation is unevaluable."""
    g = _make_trades(n=60, sm_score=3, macro_score=1)
    m = compute_strategy_metrics(g, "dummy")
    ce = m["criterion_evaluable"]
    assert ce["macro_correlation"]["evaluable"] is False
    assert ce["macro_correlation"]["n_favorable"] == 0
    assert ce["macro_correlation"]["n_unfavorable"] == 0


def test_batch365_macro_correlation_evaluable_when_mixed():
    """Macro correlation needs 20+ samples each side."""
    g_fav   = _make_trades(n=25, sm_score=0, macro_score=3)
    g_unfav = _make_trades(n=25, sm_score=0, macro_score=-2)
    g = pd.concat([g_fav, g_unfav], ignore_index=True)
    m = compute_strategy_metrics(g, "dummy")
    ce = m["criterion_evaluable"]
    assert ce["macro_correlation"]["evaluable"] is True


def test_batch365_passing_criterion_short_circuit_documented():
    """Pin in source: comment explaining WHY passes['smart_money_lift']
    auto-passes when sm_lift is None (legitimate strategies without
    SM signal aren't penalized) vs criterion_evaluable=False (the silent
    gap state). Both states yield passes=True but only one indicates
    real edge measurement."""
    import inspect
    from backtest.results import metrics
    src = inspect.getsource(metrics)
    assert "criterion_evaluable" in src
    assert "Batch 365" in src or "Batch 363 silent gap" in src
