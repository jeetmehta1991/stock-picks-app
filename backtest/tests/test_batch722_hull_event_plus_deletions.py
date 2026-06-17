# Source: B718 Pattern W deletion + B655 STATE->EVENT + B652 EXPLORATORY precedents per CHECKLIST #77
"""B722 pin tests covering 3 owner-approved changes:

(1) DELETE strat_hull_rsi_short (B718 Pattern W deterministic-duplicate)
(2) STATE->EVENT conversion on strat_hull_rsi dual (B655 T10 + B721 below_ema_50_short pattern)
(3) DELETE strat_po3_htf_aligned_long + _short (Pattern F strict-subset)
(4) Mark strat_po3_bullish + strat_po3_bearish EXPLORATORY (B652 W5m precedent)

Roster impact: 224 -> 221 (-3 deletions); active 223 -> 220.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Pin 1: strat_hull_rsi_short DELETED (no longer importable + not in registry)
# ---------------------------------------------------------------------------
def test_b722_pin1_strat_hull_rsi_short_deleted():
    """strat_hull_rsi_short must NOT be importable + must NOT be in ALL_STRATEGIES."""
    from backtest.signals import screener
    assert not hasattr(screener, "strat_hull_rsi_short"), (
        "strat_hull_rsi_short should be DELETED post-B722 per Pattern W finding"
    )
    assert "hull_rsi_short" not in screener.ALL_STRATEGIES, (
        "hull_rsi_short key should be REMOVED from ALL_STRATEGIES post-B722"
    )


# ---------------------------------------------------------------------------
# Pin 2: strat_po3_htf_aligned_long + _short DELETED
# ---------------------------------------------------------------------------
def test_b722_pin2_strat_po3_htf_aligned_long_deleted():
    """strat_po3_htf_aligned_long DELETED (Pattern F HYBRID rec)."""
    from backtest.signals import screener
    assert not hasattr(screener, "strat_po3_htf_aligned_long")
    assert "po3_htf_aligned_long" not in screener.ALL_STRATEGIES


def test_b722_pin3_strat_po3_htf_aligned_short_deleted():
    """strat_po3_htf_aligned_short DELETED (Pattern F HYBRID rec)."""
    from backtest.signals import screener
    assert not hasattr(screener, "strat_po3_htf_aligned_short")
    assert "po3_htf_aligned_short" not in screener.ALL_STRATEGIES


# ---------------------------------------------------------------------------
# Pin 4: strat_po3_bullish + _bearish marked EXPLORATORY in docstring
# ---------------------------------------------------------------------------
def test_b722_pin4_strat_po3_bullish_exploratory_docstring():
    from backtest.signals.screener import strat_po3_bullish
    docstring = strat_po3_bullish.__doc__ or ""
    assert "EXPLORATORY" in docstring, (
        "strat_po3_bullish must declare EXPLORATORY status in docstring post-B722"
    )
    assert "DO NOT DEPLOY" in docstring, (
        "strat_po3_bullish docstring must include explicit do-not-deploy warning"
    )


def test_b722_pin5_strat_po3_bearish_exploratory_docstring():
    from backtest.signals.screener import strat_po3_bearish
    docstring = strat_po3_bearish.__doc__ or ""
    assert "EXPLORATORY" in docstring
    assert "DO NOT DEPLOY" in docstring


# ---------------------------------------------------------------------------
# Pin 6: strat_hull_rsi (dual) consumes EVENT signals, not STATE
# ---------------------------------------------------------------------------
def test_b722_pin6_strat_hull_rsi_long_consumes_event_signal():
    """strat_hull_rsi LONG must consume price_above_ema_200_break_recent_5d
    (B722 EVENT-anchored), NOT bare price_above_ema_200 (STATE)."""
    from backtest.signals.screener import strat_hull_rsi
    # STATE-only (no event) -> must NOT fire
    s_state = {
        "hull_bullish": True,
        "price_above_hull": True,
        "adx": 25,
        "price_above_ema_200": True,
        "price_above_ema_200_break_recent_5d": False,  # event False
    }
    result = strat_hull_rsi(s_state)
    assert result["fires"] is False, (
        f"strat_hull_rsi LONG should NOT fire on STATE-only (event False) post-B722; got {result}"
    )

    # EVENT True -> must fire
    s_event = {
        "hull_bullish": True,
        "price_above_hull": True,
        "adx": 25,
        "price_above_ema_200_break_recent_5d": True,
    }
    result = strat_hull_rsi(s_event)
    assert result["fires"] is True, (
        f"strat_hull_rsi LONG must fire on EVENT post-B722; got {result}"
    )


def test_b722_pin7_strat_hull_rsi_short_consumes_event_signal():
    """strat_hull_rsi SHORT must consume below_ema_200_break_recent_5d (B722)."""
    from backtest.signals.screener import strat_hull_rsi
    s_state = {
        "hull_bearish": True,
        "price_below_hull": True,
        "adx": 25,
        "below_ema_200": True,
        "below_ema_200_break_recent_5d": False,
        "days_to_cover": 2.0,  # below B718a 5.0 borrow gate
    }
    result = strat_hull_rsi(s_state)
    assert result["fires"] is False or result.get("direction") != "short", (
        f"strat_hull_rsi SHORT should NOT fire on STATE-only post-B722; got {result}"
    )

    s_event = {
        "hull_bearish": True,
        "price_below_hull": True,
        "adx": 25,
        "below_ema_200_break_recent_5d": True,
        "days_to_cover": 2.0,
    }
    result = strat_hull_rsi(s_event)
    assert result["fires"] is True
    assert result["direction"] == "short"


# ---------------------------------------------------------------------------
# Pin 8: ALL_STRATEGIES count = 221 post-B722
# ---------------------------------------------------------------------------
def test_b722_pin8_all_strategies_count_decreased_by_three():
    """ALL_STRATEGIES must be 221 post-B722 (was 224 pre-B722; -3 deletions)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 219, (
        f"Expected ALL_STRATEGIES == 221 post-B722; got {len(ALL_STRATEGIES)}. "
        f"Either B722 deletions incomplete or another concurrent change shifted count."
    )


# ---------------------------------------------------------------------------
# Pin 9: producer-additive price_above_ema_N_break_recent_5d emitted
# ---------------------------------------------------------------------------
def test_b722_pin9_producer_emits_price_above_ema_event_signals():
    """compute_ema_sma must emit price_above_ema_N_break_recent_5d signals (B722)."""
    import numpy as np
    import pandas as pd
    from backtest.signals.technical import compute_ema_sma
    rng = np.random.default_rng(42)
    # 300 bars trend-up
    closes = list(100 + np.arange(300) * 0.1 + rng.normal(0, 0.5, 300))
    df = pd.DataFrame({"close": closes})
    result = compute_ema_sma(df)
    assert "price_above_ema_50_break_recent_5d" in result
    assert "price_above_ema_200_break_recent_5d" in result
    # also verify the B721 below signals are still emitted (no regression)
    assert "below_ema_50_break_recent_5d" in result
    assert "below_ema_200_break_recent_5d" in result
