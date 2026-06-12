# Source: B655 T10 + B721 + B722 STATE->EVENT precedents + S4-B717 routing per CHECKLIST #77
"""B725 pin tests: strat_ichimoku_cloud_breakout STATE -> EVENT conversion.

B710 reviewer's fire-count-ceiling finding (B717 measured):
* ichimoku_cloud_breakout: 11,355 LONG + 5,253 SHORT per year = state-flag rate

B725 changes per B655/B721/B722 precedents:
* compute_ichimoku adds ichi_above_cloud_break_recent_5d + ichi_below_cloud
  _break_recent_5d (5-bar lookback freshness)
* strat_ichimoku_cloud_breakout switches from STATE ichi_above_cloud /
  ichi_below_cloud to EVENT-anchored variants
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.signals.screener import strat_ichimoku_cloud_breakout
from backtest.signals.technical import compute_ichimoku


# ---------------------------------------------------------------------------
# Pin 1: producer emits new event signals
# ---------------------------------------------------------------------------
def test_b725_pin1_producer_emits_event_signals():
    """compute_ichimoku must emit ichi_above_cloud_break_recent_5d + ichi_below_cloud_break_recent_5d."""
    rng = np.random.default_rng(42)
    closes = list(100 + np.arange(80) * 0.1 + rng.normal(0, 0.5, 80))
    highs = [c + 1 for c in closes]
    lows = [c - 1 for c in closes]
    df = pd.DataFrame({"close": closes, "high": highs, "low": lows})
    result = compute_ichimoku(df)
    assert "ichi_above_cloud_break_recent_5d" in result, (
        f"Producer must emit ichi_above_cloud_break_recent_5d; got: {list(result.keys())}"
    )
    assert "ichi_below_cloud_break_recent_5d" in result


# ---------------------------------------------------------------------------
# Pin 2: strategy consumes EVENT signal (not STATE)
# ---------------------------------------------------------------------------
def test_b725_pin2_strategy_consumes_event_not_state():
    """strat_ichimoku_cloud_breakout must require EVENT signal."""
    # STATE-only (no event) -> should not fire
    s_state = {
        "ichi_above_cloud": True,
        "ichi_above_cloud_break_recent_5d": False,  # no fresh break
        "ichi_tk_bullish": True,
        "adx_trending": True,
        "ichi_weekly_above_cloud": True,
    }
    result = strat_ichimoku_cloud_breakout(s_state)
    assert result["fires"] is False, (
        f"Should not fire on STATE-only post-B725; got {result}"
    )

    # EVENT True -> should fire
    s_event = {
        "ichi_above_cloud_break_recent_5d": True,
        "ichi_tk_bullish": True,
        "adx_trending": True,
        "ichi_weekly_above_cloud": True,
    }
    result = strat_ichimoku_cloud_breakout(s_event)
    assert result["fires"] is True


def test_b725_pin3_signals_used_declares_event_signal():
    """signals_used must declare event variant, not bare STATE."""
    s = {
        "ichi_above_cloud_break_recent_5d": True,
        "ichi_tk_bullish": True,
        "adx_trending": True,
        "ichi_weekly_above_cloud": True,
    }
    result = strat_ichimoku_cloud_breakout(s)
    assert "ichi_above_cloud_break_recent_5d" in result["signals_used"]


# ---------------------------------------------------------------------------
# Pin 4: SHORT-side symmetric event behavior
# ---------------------------------------------------------------------------
def test_b725_pin4_short_branch_consumes_event():
    """SHORT branch must consume ichi_below_cloud_break_recent_5d."""
    s = {
        "ichi_below_cloud_break_recent_5d": True,
        "ichi_tk_bearish": True,
        "adx_trending": True,
        "ichi_weekly_below_cloud": True,
        "days_to_cover": 2.0,  # below B718a 5.0 borrow gate
    }
    result = strat_ichimoku_cloud_breakout(s)
    assert result["fires"] is True
    assert result["direction"] == "short"
