"""Tests for index_rebalance.py (Batch 251 / DEC-370)."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from backtest.signals.index_rebalance import (
    _load_events,
    compute_index_rebalance_signals,
    strat_post_deletion_drift_short,
    strat_post_inclusion_drift_long,
    strat_post_inclusion_reversal_short,
    strat_pre_rebalance_long,
)


def _mock_events_df():
    return pd.DataFrame([
        {"ticker": "TSLA", "event_date": date(2020, 12, 21),
         "event_type": "s&p_add", "announce_date": date(2020, 11, 16),
         "effective_date": date(2020, 12, 21)},
        {"ticker": "SNDK", "event_date": date(2025, 11, 28),
         "event_type": "s&p_add", "announce_date": date(2025, 11, 14),
         "effective_date": date(2025, 11, 28)},
        {"ticker": "ABMD", "event_date": date(2022, 12, 22),
         "event_type": "s&p_drop", "announce_date": date(2022, 12, 7),
         "effective_date": date(2022, 12, 22)},
        {"ticker": "FUTURE", "event_date": date(2026, 6, 30),
         "event_type": "russell_add", "announce_date": date(2026, 6, 1),
         "effective_date": date(2026, 6, 30)},
    ])


def test_load_events_missing_returns_empty():
    """Graceful no-op when prefetch file missing.

    Batch 479 (2026-05-29): also reset the module-level `_CACHED_EVENTS`
    singleton. Without this reset, earlier tests in the pyramid that
    called `_load_events()` against the real parquet populate the cache
    with 357 rows, and `_load_events` returns the cache without
    re-checking `_EVENTS_PATH`. This caused a local-only failure that
    did not surface in isolation (test pollution).
    """
    with patch("backtest.signals.index_rebalance._EVENTS_PATH",
                Path("/nonexistent/index_rebalance_events.parquet")), \
         patch("backtest.signals.index_rebalance._CACHED_EVENTS", None):
        df = _load_events()
        assert df.empty
        # Schema preserved
        assert "ticker" in df.columns


def test_compute_signals_unknown_ticker_returns_empty():
    """Unknown ticker -> empty dict (graceful no-op)."""
    with patch("backtest.signals.index_rebalance._load_events", _mock_events_df):
        out = compute_index_rebalance_signals("UNKNOWN_TICKER_XYZ", date(2026, 5, 19))
        assert out == {}


def test_compute_signals_post_inclusion_window():
    """Ticker recently added to S&P -> within_post_inclusion_window=True."""
    with patch("backtest.signals.index_rebalance._load_events", _mock_events_df):
        out = compute_index_rebalance_signals("SNDK", date(2025, 12, 10))  # 12 days post
        assert out.get("within_post_inclusion_window") is True
        assert out.get("days_since_inclusion") == 12
        assert out.get("last_event_type") == "s&p_add"


def test_compute_signals_post_inclusion_window_expired():
    """Beyond 45-day window -> within_post_inclusion_window=False."""
    with patch("backtest.signals.index_rebalance._load_events", _mock_events_df):
        out = compute_index_rebalance_signals("TSLA", date(2021, 3, 1))  # ~70 days post
        assert out.get("within_post_inclusion_window") is False
        assert out.get("days_since_inclusion") == 70


def test_compute_signals_reversal_window():
    """T+60..T+120 -> in_reversal_window=True."""
    with patch("backtest.signals.index_rebalance._load_events", _mock_events_df):
        out = compute_index_rebalance_signals("TSLA", date(2021, 3, 21))  # ~90 days post add
        assert out.get("in_reversal_window") is True


def test_compute_signals_post_deletion_window():
    """Recently deleted ticker -> within_post_deletion_window=True."""
    with patch("backtest.signals.index_rebalance._load_events", _mock_events_df):
        out = compute_index_rebalance_signals("ABMD", date(2023, 1, 10))  # ~19 days post drop
        assert out.get("within_post_deletion_window") is True
        assert out.get("days_since_deletion") == 19


def test_compute_signals_pre_rebalance_window():
    """Within T-10..T-0 of future event -> within_pre_rebalance_window=True."""
    with patch("backtest.signals.index_rebalance._load_events", _mock_events_df):
        out = compute_index_rebalance_signals("FUTURE", date(2026, 6, 25))  # 5 days pre
        assert out.get("within_pre_rebalance_window") is True
        assert out.get("days_to_rebalance") == 5


# ---------------------------------------------------------------------------
# Strategy function tests
# ---------------------------------------------------------------------------
def test_strat_post_inclusion_drift_long_fires():
    s = {
        "within_post_inclusion_window": True,
        "last_event_type": "s&p_add",
        "price_above_ema_200": True,
        "days_since_inclusion": 10,
    }
    r = strat_post_inclusion_drift_long(s)
    assert r["fires"]
    assert r["direction"] == "long"


def test_strat_post_inclusion_drift_long_blocked_below_200ema():
    s = {
        "within_post_inclusion_window": True,
        "last_event_type": "s&p_add",
        "price_above_ema_200": False,
    }
    assert not strat_post_inclusion_drift_long(s)["fires"]


def test_strat_post_inclusion_reversal_short_fires():
    s = {
        "in_reversal_window": True,
        "last_event_type": "s&p_add",
        "days_since_inclusion": 75,
    }
    r = strat_post_inclusion_reversal_short(s)
    assert r["fires"]
    assert r["direction"] == "short"


def test_strat_post_deletion_drift_short_fires():
    s = {
        "within_post_deletion_window": True,
        "last_event_type": "s&p_drop",
        "price_above_ema_200": False,
        "days_since_deletion": 5,
    }
    r = strat_post_deletion_drift_short(s)
    assert r["fires"]
    assert r["direction"] == "short"


def test_strat_pre_rebalance_long_fires():
    s = {
        "within_pre_rebalance_window": True,
        "days_to_rebalance": 5,
    }
    r = strat_pre_rebalance_long(s)
    assert r["fires"]
    assert r["direction"] == "long"


def test_all_strategies_noop_when_signals_empty():
    """Graceful no-op: all strategies return fires=False on empty signal dict."""
    for fn in [
        strat_post_inclusion_drift_long,
        strat_post_inclusion_reversal_short,
        strat_post_deletion_drift_short,
        strat_pre_rebalance_long,
    ]:
        assert not fn({})["fires"]
