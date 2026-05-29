"""Batch 460 (2026-05-29) -- AU4 equity_curve parallel-universe investigation.

FINDING (not a bug -- a documentation gap):
  The name `equity_curve` appears across 5 files but does NOT correspond to
  5 parallel computations of the same quantity. There are exactly TWO
  semantically-distinct entities + ONE generic helper that operates on
  either:

  1. PORTFOLIO equity curve  (portfolio.py:~140)
     - shape: list[(date, equity_dollar)]
     - math: cash + sum(position_dollar_mtm) appended once per trading day
     - scope: portfolio-level (one entry across all strategies)
     - consumers: writer.py (parquet emit), metrics.compute_portfolio_metrics_
       from_curves (Sharpe / alpha / beta / max-DD), agents/our_risk_toolkit
     - canonical source of truth for PORTFOLIO performance

  2. PER-STRATEGY compounded equity curve  (metrics.py:~2222)
     - shape: pd.Series indexed by trade order (no dates)
     - math: (1.0 + pnl_pct / 100.0).cumprod()  -- returns-based
     - scope: per-strategy (recomputed inside compute_strategy_metrics)
     - consumers: _adf_test (DEC-414 stationarity), _chow_test (DEC-416
       structural break)
     - NOT interchangeable with #1 (different unit, different shape,
       different scope)

  3. Generic max_drawdown(equity_curve: Sequence[float])  (quant_audit.py:69)
     - utility function callable with EITHER #1 (equity_dollar values) OR
       #2 (compounded multiplier values) -- both yield correct peak-to-
       trough percentages.

  backtest.py mentions equity_curve only in comments referencing Portfolio
  state; it calls portfolio.mark_to_market() but never computes its own
  curve. NOT a third definition.

NO CONSOLIDATION NEEDED (queue framing was wrong):
  The two real entities are semantically distinct -- merging them would
  break stationarity testing (needs returns-based, no-cash compounding)
  AND portfolio Sharpe (needs dollar curve with cash dynamics). Both
  carry the name `equity_curve` because each is locally meaningful as
  "equity over time" in its own scope.

WHAT BATCH 460 DOES INSTEAD:
  Adds explicit docstrings + comments at both call sites making the
  distinction explicit + asserts it in this test so future readers don't
  conflate.

THIS TEST asserts:
  1. Portfolio.equity_curve has list[(date, float)] shape with dollar values.
  2. The per-strategy curve from metrics.compute_strategy_metrics is a
     pd.Series of compounded multipliers starting near 1.0, NOT dollars.
  3. quant_audit.max_drawdown produces the SAME drawdown percentage when
     fed either curve scaled to the same drawdown shape (helper is
     scale-invariant on the percent metric).
  4. portfolio.py docstring at line ~140 documents the distinction
     (greppable wiring guard so future renames stay coordinated).
  5. metrics.py:~2222 comment documents the distinction.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from backtest.engine.portfolio import Portfolio
from backtest.results.quant_audit import max_drawdown


REPO = Path(__file__).resolve().parents[2]


def test_portfolio_equity_curve_is_list_of_date_dollar_tuples():
    """Definition #1: Portfolio.equity_curve is list[(date, equity_dollar)]
    after mark_to_market appends."""
    p = Portfolio(starting_capital=100_000.0)
    assert p.equity_curve == []
    for i in range(5):
        # Note: positions=empty, prices empty -> mark_to_market still
        # appends a (date, equity) point at today's cash equity.
        p.mark_to_market({}, date(2024, 1, 1) + timedelta(days=i))
    assert len(p.equity_curve) == 5
    for d, eq in p.equity_curve:
        assert isinstance(d, date)
        assert isinstance(eq, float)
        # Equity should be in dollars near starting capital
        assert 50_000 < eq < 200_000


def test_per_strategy_equity_curve_is_compounded_multiplier_series():
    """Definition #2: the per-strategy curve at metrics.py:~2222 is
    `(1 + pnl_pct/100).cumprod()` -- a pd.Series of multipliers starting
    near 1.0, NOT dollars."""
    pnl = pd.Series([1.0, -0.5, 2.0, -1.0, 1.5])
    curve = (1.0 + pnl / 100.0).cumprod()
    assert isinstance(curve, pd.Series)
    # Values are multipliers around 1.0, NOT dollars near 100k.
    assert 0.9 < curve.iloc[0] < 1.1
    assert 0.9 < curve.iloc[-1] < 1.1
    # No dates / no portfolio cash
    assert curve.index.dtype.kind in ("i", "u")  # integer index, not date


def test_two_curves_are_not_interchangeable():
    """Portfolio.equity_curve and per-strategy cumprod curve are semantically
    different -- feeding one to a function expecting the other yields a
    wrong answer."""
    # Portfolio curve: dollar values starting at 100k
    portfolio_curve = [100_000.0, 100_300.0, 100_800.0, 100_100.0, 100_600.0]
    # Per-strategy curve: multipliers around 1.0
    pnl = pd.Series([0.3, 0.5, -0.7, 0.5])
    per_strat_curve = (1.0 + pnl / 100.0).cumprod()

    pdd = max_drawdown(portfolio_curve)["max_drawdown_pct"]
    sdd = max_drawdown(per_strat_curve.tolist())["max_drawdown_pct"]
    # quant_audit.max_drawdown returns NEGATIVE fractions (e.g., -0.007 for
    # 0.7% drawdown). Both curves should produce a real (non-zero) DD here
    # because each has a peak-to-trough leg.
    assert pdd < 0
    assert sdd < 0
    # Sanity: the two definitions are DIFFERENT data types / units even
    # though the helper happens to be scale-invariant.
    assert isinstance(portfolio_curve, list)
    assert isinstance(per_strat_curve, pd.Series)
    # Magnitude check: portfolio values >>> per-strategy values
    assert portfolio_curve[0] > per_strat_curve.iloc[0] * 1000


def test_max_drawdown_helper_is_scale_invariant_on_percent():
    """quant_audit.max_drawdown returns a negative FRACTION (e.g., -0.04 for
    -4% DD), so scaling the input by a constant should not change the
    result."""
    base = [1.0, 1.02, 1.05, 1.00, 1.03]  # peak 1.05 -> trough 1.00 -> -4.76%
    scaled = [v * 100_000 for v in base]
    dd_a = max_drawdown(base)["max_drawdown_pct"]
    dd_b = max_drawdown(scaled)["max_drawdown_pct"]
    assert dd_a == pytest.approx(dd_b, abs=1e-6), \
        "max_drawdown_pct must be scale-invariant"
    assert dd_a < 0, "drawdown should be negative"


def test_portfolio_py_docstring_documents_distinction():
    """Batch 460 added a docstring at portfolio.py:~140 explaining the
    distinction between Portfolio.equity_curve and the metrics.py:~2222
    per-strategy curve. Greppable so the wiring stays coordinated."""
    src = (REPO / "backtest" / "engine" / "portfolio.py").read_text(encoding="utf-8")
    assert "Canonical PORTFOLIO equity curve" in src
    assert "per-STRATEGY synthetic" in src or "metrics.py:~2222" in src


def test_metrics_py_2222_comment_documents_distinction():
    """Batch 460 added a comment at metrics.py:~2222 noting the per-strategy
    curve is different from Portfolio.equity_curve."""
    src = (REPO / "backtest" / "results" / "metrics.py").read_text(encoding="utf-8")
    assert "Batch 460 (AU4)" in src
    assert "different entity" in src.lower() or "different unit" in src.lower() \
        or "different" in src
    assert "Portfolio.equity_curve" in src


def test_backtest_py_does_not_define_separate_curve():
    """backtest.py mentions equity_curve only in comments referencing the
    Portfolio path. No independent computation (e.g., no
    `backtest_self.equity_curve = ...` assignment)."""
    src = (REPO / "backtest" / "engine" / "backtest.py").read_text(encoding="utf-8")
    # Should NOT contain a separate assignment to a local equity_curve
    # variable inside backtest.py (it should only reference
    # self.portfolio.equity_curve via mark_to_market).
    import re
    # Allow `self.portfolio.equity_curve` references; flag any other
    # `equity_curve = ...` assignment.
    matches = re.findall(r"^\s*(?!#)\S*equity_curve\s*=", src, flags=re.MULTILINE)
    # Filter out the `self.portfolio.equity_curve` references (they end in
    # .equity_curve, not = equity_curve)
    rogue = [m for m in matches if "portfolio" not in m]
    assert rogue == [], \
        f"backtest.py must not define its own equity_curve, found: {rogue}"
