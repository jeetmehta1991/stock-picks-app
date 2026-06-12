# Source: B710 reviewer fire-count-ceiling + S4-B717-CEILING-FLAGGED-REDUNDANCY-DIAGNOSTIC + B655 T10 STATE->EVENT precedent per CHECKLIST #77
"""B721 pin tests: strat_simple_below_ema_50_short converted from STATE to
EVENT-anchored per B655 T10 supertrend precedent.

B710 reviewer's fire-count-ceiling finding (B717 measured):
* simple_below_ema_50_short: 34,378/yr SHORT = 68/name/yr = state filter

B721 producer-additive change: compute_ema_sma now also emits
below_ema_N_break_recent_5d which is True only when close[t] is below
ema_N[t] AND close was at-least-once above ema_N within the last 5 bars
(excluding today).

Strategy switches from `below_ema_50` (STATE) to
`below_ema_50_break_recent_5d` (EVENT-anchored).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.signals.screener import strat_simple_below_ema_50_short
from backtest.signals.technical import compute_ema_sma


def _make_close_series(closes_list, periods_needed=300):
    """Build a synthetic DataFrame with `close` series ending in given closes."""
    rng = np.random.default_rng(42)
    n_pad = periods_needed - len(closes_list)
    if n_pad < 0:
        n_pad = 0
    # Pad with mild noise around 100
    padding = 100 + rng.normal(0, 0.5, n_pad).cumsum()
    full_closes = list(padding) + list(closes_list)
    df = pd.DataFrame({"close": full_closes})
    return df


def test_b721_pin1_producer_emits_below_ema_50_break_recent_5d():
    """compute_ema_sma must emit the new B721 signal."""
    df = _make_close_series([100] * 10)  # flat-ish
    result = compute_ema_sma(df)
    assert "below_ema_50_break_recent_5d" in result, (
        f"compute_ema_sma must emit below_ema_50_break_recent_5d; got keys: {list(result.keys())}"
    )


def test_b721_pin2_state_to_event_basic_break():
    """When close has just dropped below EMA-50 in the last bar (was above
    yesterday), the EVENT signal must fire."""
    # Trend up (close > ema), then sharp drop to below ema in last bar
    closes = [102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 95]
    df = _make_close_series(closes, periods_needed=300)
    result = compute_ema_sma(df)
    # below_ema_50 (state) should be True
    assert result.get("below_ema_50") is True
    # below_ema_50_break_recent_5d (event) should ALSO be True (fresh break)
    assert result.get("below_ema_50_break_recent_5d") is True


def test_b721_pin3_no_event_when_state_persisted_too_long():
    """When close has been below EMA-50 for many bars (state persisted),
    the EVENT signal must NOT fire — only the STATE is True."""
    # Sustained downtrend: close has been well below ema for 10+ bars
    closes = [85] * 20
    df = _make_close_series(closes, periods_needed=300)
    result = compute_ema_sma(df)
    # STATE: close < ema_50
    assert result.get("below_ema_50") is True
    # EVENT: NOT fresh (close was never above in last 5 bars)
    assert result.get("below_ema_50_break_recent_5d") is False, (
        "Sustained downtrend should NOT trigger event-anchored signal"
    )


def test_b721_pin4_no_event_when_above_ema():
    """When close is above EMA-50, neither STATE nor EVENT signals fire."""
    closes = [105] * 10
    df = _make_close_series(closes, periods_needed=300)
    result = compute_ema_sma(df)
    assert result.get("below_ema_50") is False
    assert result.get("below_ema_50_break_recent_5d") is False


def test_b721_pin5_strategy_consumes_event_signal_not_state():
    """strat_simple_below_ema_50_short must fire on event-anchored signal,
    NOT on state signal alone."""
    # STATE-only: below_ema_50=True but event=False
    s_state_only = {
        "below_ema_50": True,
        "below_ema_50_break_recent_5d": False,
        "days_to_cover": 2.0,  # below B718a 5.0 borrow gate
    }
    result = strat_simple_below_ema_50_short(s_state_only)
    assert result["fires"] is False, (
        f"Strategy must NOT fire on STATE-only signal post-B721; got {result}"
    )

    # EVENT: both True
    s_event = {
        "below_ema_50": True,
        "below_ema_50_break_recent_5d": True,
        "days_to_cover": 2.0,
    }
    result = strat_simple_below_ema_50_short(s_event)
    assert result["fires"] is True, (
        f"Strategy must fire on EVENT-anchored signal post-B721; got {result}"
    )


def test_b721_pin6_signals_used_declares_event_signal():
    """signals_used must reference below_ema_50_break_recent_5d, not bare below_ema_50."""
    s = {
        "below_ema_50_break_recent_5d": True,
        "days_to_cover": 2.0,
    }
    result = strat_simple_below_ema_50_short(s)
    assert "below_ema_50_break_recent_5d" in result["signals_used"], (
        f"signals_used must declare event-anchored signal; got {result['signals_used']}"
    )
    assert "below_ema_50" not in result["signals_used"], (
        f"signals_used must NOT declare bare state signal post-B721; got {result['signals_used']}"
    )


def test_b721_pin7_below_ema_20_event_also_emitted():
    """The producer also emits below_ema_20_break_recent_5d for the (20,50)
    EMA tuple iteration."""
    closes = [102] * 10 + [95]
    df = _make_close_series(closes, periods_needed=300)
    result = compute_ema_sma(df)
    assert "below_ema_20_break_recent_5d" in result, (
        "below_ema_20_break_recent_5d must also be emitted"
    )
