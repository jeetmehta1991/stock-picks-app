"""Batch 503 (2026-05-31) -- M6 Path-2 YoY-growth surprise tests.

Source: per CHECKLIST #77.
Queue row: EXECUTION_QUEUE.md item M6.
Producer module: backtest/signals/earnings_surprise_yoy.py.
"""
from __future__ import annotations

from datetime import date

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Threshold + module-level pins
# ---------------------------------------------------------------------------

def test_batch503_module_importable():
    from backtest.signals.earnings_surprise_yoy import (
        compute_yoy_surprise_signal, SLEEVE_DEFINITIONS,
        YOY_GROWTH_LONG_THRESHOLD, YOY_GROWTH_SHORT_THRESHOLD,
    )
    assert callable(compute_yoy_surprise_signal)
    assert isinstance(SLEEVE_DEFINITIONS, dict)


def test_batch503_default_thresholds():
    from backtest.signals.earnings_surprise_yoy import (
        YOY_GROWTH_LONG_THRESHOLD, YOY_GROWTH_SHORT_THRESHOLD,
    )
    assert YOY_GROWTH_LONG_THRESHOLD == 0.05
    assert YOY_GROWTH_SHORT_THRESHOLD == -0.05


def test_batch503_sleeve_definitions_have_both_sides():
    from backtest.signals.earnings_surprise_yoy import SLEEVE_DEFINITIONS
    assert "pead_long_high_yoy_growth_only" in SLEEVE_DEFINITIONS
    assert "pead_short_negative_yoy_growth" in SLEEVE_DEFINITIONS
    long = SLEEVE_DEFINITIONS["pead_long_high_yoy_growth_only"]
    short = SLEEVE_DEFINITIONS["pead_short_negative_yoy_growth"]
    assert long["direction"] == "long"
    assert short["direction"] == "short"
    assert long["category"] == "earnings"
    assert short["category"] == "earnings"


# ---------------------------------------------------------------------------
# Producer behavior via mock pead.compute_pead_signals
# ---------------------------------------------------------------------------

def test_batch503_high_yoy_growth_triggers_long_signal(monkeypatch):
    """yoy_growth = +10% -> yoy_surprise_high True, yoy_surprise_negative False."""
    from backtest.signals import earnings_surprise_yoy as mod
    monkeypatch.setattr(
        "backtest.signals.pead.compute_pead_signals",
        lambda *a, **k: {
            "earnings_eps_yoy_growth": 0.10,
            "days_since_last_earnings": 5,
            "within_pead_window": True,
        },
    )
    out = mod.compute_yoy_surprise_signal("AAPL", pd.DataFrame(), date(2024, 6, 1))
    assert out["earnings_eps_yoy_growth"] == 0.10
    assert out["yoy_surprise_high"] is True
    assert out["yoy_surprise_negative"] is False
    assert out["within_pead_window"] is True


def test_batch503_negative_yoy_growth_triggers_short_signal(monkeypatch):
    """yoy_growth = -10% -> yoy_surprise_high False, yoy_surprise_negative True."""
    from backtest.signals import earnings_surprise_yoy as mod
    monkeypatch.setattr(
        "backtest.signals.pead.compute_pead_signals",
        lambda *a, **k: {
            "earnings_eps_yoy_growth": -0.10,
            "days_since_last_earnings": 5,
            "within_pead_window": True,
        },
    )
    out = mod.compute_yoy_surprise_signal("AAPL", pd.DataFrame(), date(2024, 6, 1))
    assert out["yoy_surprise_high"] is False
    assert out["yoy_surprise_negative"] is True


def test_batch503_threshold_boundary(monkeypatch):
    """yoy_growth = +0.05 exactly -> long-flag True (>= comparison)."""
    from backtest.signals import earnings_surprise_yoy as mod
    monkeypatch.setattr(
        "backtest.signals.pead.compute_pead_signals",
        lambda *a, **k: {"earnings_eps_yoy_growth": 0.05},
    )
    out = mod.compute_yoy_surprise_signal("AAPL", pd.DataFrame(), date(2024, 6, 1))
    assert out["yoy_surprise_high"] is True


def test_batch503_below_threshold_does_not_flag(monkeypatch):
    """yoy_growth between -5% and +5% -> neither flag fires."""
    from backtest.signals import earnings_surprise_yoy as mod
    monkeypatch.setattr(
        "backtest.signals.pead.compute_pead_signals",
        lambda *a, **k: {"earnings_eps_yoy_growth": 0.02},
    )
    out = mod.compute_yoy_surprise_signal("AAPL", pd.DataFrame(), date(2024, 6, 1))
    assert out["yoy_surprise_high"] is False
    assert out["yoy_surprise_negative"] is False


def test_batch503_pead_empty_returns_empty(monkeypatch):
    """compute_pead_signals empty dict -> producer empty dict."""
    from backtest.signals import earnings_surprise_yoy as mod
    monkeypatch.setattr(
        "backtest.signals.pead.compute_pead_signals", lambda *a, **k: {}
    )
    out = mod.compute_yoy_surprise_signal("AAPL", pd.DataFrame(), date(2024, 6, 1))
    assert out == {}


def test_batch503_pead_missing_yoy_growth_returns_empty(monkeypatch):
    """compute_pead_signals without yoy_growth key -> producer empty dict."""
    from backtest.signals import earnings_surprise_yoy as mod
    monkeypatch.setattr(
        "backtest.signals.pead.compute_pead_signals",
        lambda *a, **k: {"days_since_last_earnings": 5},  # no yoy_growth
    )
    out = mod.compute_yoy_surprise_signal("AAPL", pd.DataFrame(), date(2024, 6, 1))
    assert out == {}


def test_batch503_owner_tunable_thresholds(monkeypatch):
    """Caller can pass custom thresholds."""
    from backtest.signals import earnings_surprise_yoy as mod
    monkeypatch.setattr(
        "backtest.signals.pead.compute_pead_signals",
        lambda *a, **k: {"earnings_eps_yoy_growth": 0.08},
    )
    # With higher threshold, 8% doesn't trigger
    out = mod.compute_yoy_surprise_signal(
        "AAPL", pd.DataFrame(), date(2024, 6, 1),
        long_threshold=0.10, short_threshold=-0.10,
    )
    assert out["yoy_surprise_high"] is False  # 0.08 < 0.10


# ---------------------------------------------------------------------------
# Sleeve strategies NOT yet registered in ALL_STRATEGIES
# ---------------------------------------------------------------------------

def test_batch682_deletion_pead_yoy_sleeves_no_longer_registered():
    """Batch 682 (2026-06-10 owner-approved) DELETION VERIFICATION:
    pead_long_high_yoy_growth_only + pead_short_negative_yoy_growth
    were REGISTERED B507 then DELETED B682 per B680 self-critique CC-C
    Pattern W deterministic-subset finding.

    These strategies were a STRICT SUBSET of pead_long/pead_short on the
    YoY-growth axis; cube replay would produce near-identical per-trade
    Sharpe by construction. Per `project_no_apriori_strategy_pruning`
    explicit owner override on deterministic-subset evidence.

    Pre-B682 (B503 + B507 test): assertion was IN ALL_STRATEGIES.
    Post-B682 (this test): assertion is NOT IN ALL_STRATEGIES.

    YoY-surprise PRODUCER tests above (compute_yoy_surprise +
    yoy_surprise_high + yoy_surprise_negative + threshold tuning) all
    REMAIN valid because the producer signals are still used by future
    work (if owner wants YoY-threshold parameter variant on EV-1/EV-2).
    """
    from backtest.signals.screener import ALL_STRATEGIES
    assert "pead_long_high_yoy_growth_only" not in ALL_STRATEGIES, (
        "B682 deletion: pead_long_high_yoy_growth_only must be REMOVED"
    )
    assert "pead_short_negative_yoy_growth" not in ALL_STRATEGIES, (
        "B682 deletion: pead_short_negative_yoy_growth must be REMOVED"
    )
    # Strategy function deletion verification
    import backtest.signals.screener as screener
    assert not hasattr(screener, "strat_pead_long_high_yoy_growth_only")
    assert not hasattr(screener, "strat_pead_short_negative_yoy_growth")
