"""Batch 655 (2026-06-09) -- T10 strat_supertrend_macd redundancy-audit
option B per 2nd-wave external-AI critique #2 + owner directive
2026-06-09. Same template as B643 W5 capitulation lookback + B645 W5m
blowoff lookback: EVENT-anchored multi-bar window replaces all-STATE
composite.

ROOT: pre-B655 the strategy used `supertrend_bullish` (99.19% True on
B648 random-30 sample, near-NO-OP), `macd_12_26_9_bullish` (50% STATE),
and `adx > 20` (STATE trend-strength). 3 STATE gates, ZERO EVENT =
no bar-of-fire timing alpha; effectively "MACD + ADX wearing
supertrend as 99%-True camouflage." Per CHECKLIST (s) all-STATE
composite hazard.

FIX: NEW producer-additive signals `supertrend_flip_recent_long_5d`
+ `_short_5d` in compute_supertrend (B574-style; other consumers
unchanged). Strategy switches to EVENT-anchored 5-bar lookback +
existing MACD + ADX gates.

Pins:
  (1)  compute_supertrend emits new lookback signals
  (2)  supertrend_flip_recent_long_5d True when supertrend flipped up
       0 bars ago (today)
  (3)  supertrend_flip_recent_long_5d True when supertrend flipped up
       3 bars ago (within 5-bar window)
  (4)  supertrend_flip_recent_long_5d False when supertrend flipped up
       7 bars ago (outside window)
  (5)  supertrend_flip_recent_long_5d False on steady-state series
       (never flipped)
  (6)  SHORT mirror `_short_5d` symmetric
  (7)  strat_supertrend_macd LONG fires on flip_recent_long_5d + MACD
       + ADX
  (8)  strat_supertrend_macd LONG does NOT fire on supertrend_bullish
       STATE alone (proves the swap happened)
  (9)  strat_supertrend_macd SHORT mirror fires correctly
  (10) strat_supertrend_macd executable body no longer references
       supertrend_bullish / supertrend_bearish
  (11) Other consumers of supertrend_bullish (strat_supertrend_macd
       _short, strat_supertrend_ichimoku_adx) UNCHANGED -- B574-style
       producer-additive isolation
  (12) Strategy registered + callable + B291 default applies for the
       deferred {bull} regime entry
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _make_steady_uptrend(n: int = 300, base: float = 100.0, slope: float = 0.02):
    """Smooth uptrend; supertrend stays bullish throughout (no flip)."""
    close = base + np.arange(n) * slope
    high = close + 0.3
    low = close - 0.3
    open_ = close.copy()
    vol = np.full(n, 1e6)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": vol},
        index=pd.date_range("2020-01-01", periods=n, freq="D"),
    )


def _inject_supertrend_flip_at(df: pd.DataFrame, bar_offset_from_end: int):
    """Inject a large bullish move at bar (len-1-offset) so supertrend
    flips up there. Pre-flip bars driven down to make supertrend bearish
    first; flip bar gaps up."""
    df = df.copy()
    flip_idx = len(df) - 1 - bar_offset_from_end
    # Drive down for ~50 bars before flip_idx to make supertrend bearish
    pre_start = max(flip_idx - 60, 0)
    for i in range(pre_start, flip_idx):
        progress = (i - pre_start) / max(flip_idx - pre_start, 1)
        df.iloc[i, df.columns.get_loc("close")] = 100.0 - progress * 30.0
        df.iloc[i, df.columns.get_loc("high")] = df.iloc[i]["close"] + 0.3
        df.iloc[i, df.columns.get_loc("low")] = df.iloc[i]["close"] - 0.3
        df.iloc[i, df.columns.get_loc("open")] = df.iloc[i]["close"]
    # Large bullish gap at flip_idx
    pre_close = float(df.iloc[flip_idx - 1]["close"])
    df.iloc[flip_idx, df.columns.get_loc("open")] = pre_close
    df.iloc[flip_idx, df.columns.get_loc("close")] = pre_close + 8.0
    df.iloc[flip_idx, df.columns.get_loc("high")] = pre_close + 8.5
    df.iloc[flip_idx, df.columns.get_loc("low")] = pre_close - 0.5
    # Hold/rally after flip
    for i in range(flip_idx + 1, len(df)):
        last_close = float(df.iloc[i - 1]["close"])
        df.iloc[i, df.columns.get_loc("close")] = last_close + 0.1
        df.iloc[i, df.columns.get_loc("high")] = df.iloc[i]["close"] + 0.3
        df.iloc[i, df.columns.get_loc("low")] = df.iloc[i]["close"] - 0.3
        df.iloc[i, df.columns.get_loc("open")] = last_close
    return df


# =================== Producer pins ===================

def test_batch655_producer_emits_lookback_keys():
    """Pin (1)."""
    from backtest.signals.technical import compute_supertrend
    df = _make_steady_uptrend()
    out = compute_supertrend(df)
    assert "supertrend_flip_recent_long_5d" in out
    assert "supertrend_flip_recent_short_5d" in out
    assert out["supertrend_lookback_window"] == 5


def test_batch655_flip_recent_long_true_today():
    """Pin (2): flip on bar -1 (today)."""
    from backtest.signals.technical import compute_supertrend
    df = _inject_supertrend_flip_at(_make_steady_uptrend(), 0)
    out = compute_supertrend(df)
    assert out["supertrend_flip_recent_long_5d"] is True


def test_batch655_flip_recent_long_true_within_window():
    """Pin (3): flip 3 bars ago -> still True."""
    from backtest.signals.technical import compute_supertrend
    df = _inject_supertrend_flip_at(_make_steady_uptrend(), 3)
    out = compute_supertrend(df)
    assert out["supertrend_flip_recent_long_5d"] is True


def test_batch655_flip_recent_long_false_outside_window():
    """Pin (4): flip 7 bars ago -> outside 5-bar window."""
    from backtest.signals.technical import compute_supertrend
    df = _inject_supertrend_flip_at(_make_steady_uptrend(), 7)
    out = compute_supertrend(df)
    assert out["supertrend_flip_recent_long_5d"] is False


def test_batch655_flip_recent_long_false_no_flip():
    """Pin (5): smooth uptrend with no flip -> False."""
    from backtest.signals.technical import compute_supertrend
    df = _make_steady_uptrend()
    out = compute_supertrend(df)
    assert out["supertrend_flip_recent_long_5d"] is False


def test_batch655_short_mirror_symmetric():
    """Pin (6): symmetric SHORT mirror via downward injection."""
    df = _make_steady_uptrend()
    # Reverse the trend: smooth downtrend
    df = df.copy()
    df["close"] = 100.0 - np.arange(len(df)) * 0.02
    df["high"] = df["close"] + 0.3
    df["low"] = df["close"] - 0.3
    df["open"] = df["close"]
    # Inject downward flip at end (large drop after uptrend phase)
    from backtest.signals.technical import compute_supertrend
    # Build a fixture where supertrend is bullish for first half then flips down
    df2 = _make_steady_uptrend(n=300)
    flip_idx = len(df2) - 1  # flip on today
    pre_close = float(df2.iloc[flip_idx - 1]["close"])
    df2.iloc[flip_idx, df2.columns.get_loc("open")] = pre_close
    df2.iloc[flip_idx, df2.columns.get_loc("close")] = pre_close - 15.0
    df2.iloc[flip_idx, df2.columns.get_loc("high")] = pre_close + 0.5
    df2.iloc[flip_idx, df2.columns.get_loc("low")] = pre_close - 15.5
    out = compute_supertrend(df2)
    assert out["supertrend_flip_recent_short_5d"] is True


# =================== Strategy pins ===================

def test_batch655_long_fires_on_flip_recent_plus_macd_plus_adx():
    """Pin (7)."""
    from backtest.signals.screener import strat_supertrend_macd
    s = {
        "supertrend_flip_recent_long_5d": True,
        "macd_12_26_9_bullish": True,
        "adx": 25,
    }
    out = strat_supertrend_macd(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch655_long_does_NOT_fire_on_supertrend_bullish_alone():
    """Pin (8): proves the B655 swap happened. Pre-B655 this fixture
    would have fired LONG; post-B655 must NOT fire because the
    strategy now requires the lookback EVENT-anchored signal."""
    from backtest.signals.screener import strat_supertrend_macd
    s = {
        "supertrend_bullish": True,  # pre-B655 STATE trigger -- now ignored
        # NO supertrend_flip_recent_long_5d -- defaults False
        "macd_12_26_9_bullish": True,
        "adx": 25,
    }
    out = strat_supertrend_macd(s)
    assert out["fires"] is False, (
        "B655 regression: T10 still consumes supertrend_bullish STATE; "
        "should require supertrend_flip_recent_long_5d (EVENT-anchored)"
    )


def test_batch655_short_mirror_fires():
    """Pin (9)."""
    from backtest.signals.screener import strat_supertrend_macd
    s = {
        "supertrend_flip_recent_short_5d": True,
        "macd_12_26_9_bearish": True,
        "adx": 25,
    }
    out = strat_supertrend_macd(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch655_executable_body_no_longer_references_state_supertrend():
    """Pin (10): strategy code body must not read supertrend_bullish /
    supertrend_bearish (STATE) anymore -- only the lookback EVENT
    signals."""
    import inspect
    from backtest.signals.screener import strat_supertrend_macd
    src = inspect.getsource(strat_supertrend_macd)
    parts = src.split('"""')
    body = "".join(parts[2:]) if len(parts) >= 3 else src
    # Strip comment lines
    code_lines = [ln for ln in body.splitlines() if not ln.strip().startswith("#")]
    code = "\n".join(code_lines)
    assert 's.get("supertrend_bullish"' not in code, (
        "B655 regression: STATE supertrend_bullish still in executable code"
    )
    assert 's.get("supertrend_bearish"' not in code, (
        "B655 regression: STATE supertrend_bearish still in executable code"
    )
    assert "supertrend_flip_recent_long_5d" in code
    assert "supertrend_flip_recent_short_5d" in code


def test_batch655_other_supertrend_consumers_unchanged():
    """Pin (11): per feedback_narrow_scope_blast_radius, B655 is
    producer-additive isolation -- other consumers of supertrend_*
    signals (strat_supertrend_macd_short, strat_supertrend_ichimoku_adx)
    UNCHANGED. Verify by grepping their source for the STATE signals."""
    import inspect
    from backtest.signals.screener import (
        strat_supertrend_macd_short, strat_supertrend_ichimoku_adx,
    )
    for fn in (strat_supertrend_macd_short, strat_supertrend_ichimoku_adx):
        src = inspect.getsource(fn)
        # Both should STILL read supertrend_bullish or supertrend_bearish
        # (proves we didn't accidentally modify them)
        assert ("supertrend_bullish" in src) or ("supertrend_bearish" in src), (
            f"{fn.__name__} unexpectedly lost its supertrend STATE gate "
            f"after B655 (should be UNCHANGED per B574-style isolation)"
        )


def test_batch655_t10_strategy_registered_and_callable():
    """Pin (12)."""
    from backtest.signals.screener import ALL_STRATEGIES, strat_supertrend_macd
    assert "supertrend_macd" in ALL_STRATEGIES
    assert ALL_STRATEGIES["supertrend_macd"] is strat_supertrend_macd
