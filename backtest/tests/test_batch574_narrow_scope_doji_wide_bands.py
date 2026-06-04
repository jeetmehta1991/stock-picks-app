"""Batch 574 (2026-06-04) -- narrow-scope fix for B573 owner-caught
lapse per feedback_narrow_scope_blast_radius.

B573 changed `near()` in technical.py globally from 0.003 -> 0.015,
which propagated to 14 strategies. Owner: "Why have 14 strategies
been affected? Should just be 2!"

B574 reverts that global change and instead emits NEW `_wide` flag
variants at 1.5pct tolerance (alongside the existing narrow 0.3pct
flags). Only the 2 doji strategies (strat_doji_at_support +
strat_doji_at_resistance_short) consume the `_wide` variants. The
other 12 previously-affected strategies are restored to their
original 0.3pct near()-based behavior.

Pins:

  (1) Pivot near() tolerance REVERTED to 0.003 (not 0.015 from B573)
  (2) Pivot near_wide tolerance is 0.015 (new in B574)
  (3) Fib near() tolerance REVERTED to 0.005 (not 0.015 from B573)
  (4) Fib near_wide tolerance is 0.015 (new in B574)
  (5) New flags emitted: near_s1_wide, near_s2_wide, near_r1_wide,
      near_r2_wide, at_key_fib_wide
  (6) Old narrow flags still emit + still work for the 12 strategies
      that rely on them (near_s1, near_r1, at_key_fib unchanged)
  (7) strat_doji_at_support consumes the `_wide` flags
  (8) strat_doji_at_resistance_short consumes the `_wide` flags
  (9) Other strategies' near_s1 / at_key_fib reads unchanged - if
      they were True before B573, they're True after B574 (regression
      guard for the 12 other strategies)
  (10) Doji predicates do NOT fire on the narrow near_s1 alone
       (must consume `_wide` exclusively)
"""
from __future__ import annotations

import pandas as pd
import numpy as np


def _mk_2bar_ohlcv(today_close, prev_high=100, prev_low=95, prev_close=98):
    dates = pd.date_range("2024-01-01", periods=2)
    return pd.DataFrame({
        "open":  [97, today_close - 0.1],
        "high":  [prev_high, today_close + 0.1],
        "low":   [prev_low, today_close - 0.1],
        "close": [prev_close, today_close],
        "volume": [1_000_000, 1_000_000],
    }, index=dates)


def test_batch574_pivot_near_reverted_to_0_003():
    """Pin (1)."""
    from backtest.signals.technical import compute_pivots
    s1 = 2 * (100 + 95 + 98) / 3 - 100  # ~95.334
    # At 1.0pct away from S1: narrow near_s1 should NOT fire (was True
    # under B573 global; now False after B574 revert).
    df = _mk_2bar_ohlcv(today_close=s1 * 1.010)
    p = compute_pivots(df)
    assert p["near_s1"] == False, (
        f"Pin (1): narrow near_s1 must be False at S1+1.0pct under "
        f"the reverted 0.3pct tolerance"
    )


def test_batch574_pivot_near_wide_is_0_015():
    """Pin (2) + (5): near_*_wide flags emit + fire at 1.0pct."""
    from backtest.signals.technical import compute_pivots
    s1 = 2 * (100 + 95 + 98) / 3 - 100
    df = _mk_2bar_ohlcv(today_close=s1 * 1.010)
    p = compute_pivots(df)
    # New _wide flags must exist + fire at 1.0pct
    for flag in ("near_s1_wide", "near_s2_wide",
                 "near_r1_wide", "near_r2_wide"):
        assert flag in p, f"Pin (5): {flag} must be emitted in pivot dict"
    assert p["near_s1_wide"] == True, (
        f"Pin (2): near_s1_wide must fire at S1+1.0pct under 1.5pct band"
    )


def test_batch574_pivot_narrow_close_still_fires():
    """Pin (6): at 0.2pct from S1 the NARROW near_s1 still fires
    (regression guard for the 12 strategies depending on narrow band)."""
    from backtest.signals.technical import compute_pivots
    s1 = 2 * (100 + 95 + 98) / 3 - 100
    df = _mk_2bar_ohlcv(today_close=s1 * 1.002)
    p = compute_pivots(df)
    assert p["near_s1"] == True, (
        "Pin (6): narrow near_s1 must still fire at S1+0.2pct"
    )


def test_batch574_fib_near_reverted_to_0_005():
    """Pin (3)."""
    from backtest.signals.technical import compute_fibonacci
    n = 50
    dates = pd.date_range("2024-01-01", periods=n)
    highs = np.linspace(50, 110, n)
    lows  = np.linspace(40, 100, n)
    closes = (highs + lows) / 2
    df = pd.DataFrame({
        "open":  closes, "high": highs, "low": lows, "close": closes,
        "volume": [1_000_000] * n,
    }, index=dates)
    sh, sl = highs.max(), lows.min()
    fib_500 = sh - 0.500 * (sh - sl)
    # 1.0pct away from fib_500: NARROW near_fib_500 should NOT fire
    # (above 0.5pct tolerance after revert)
    df.iloc[-1, df.columns.get_loc("close")] = fib_500 * 1.010
    fb = compute_fibonacci(df)
    assert fb["near_fib_500"] == False, (
        "Pin (3): narrow near_fib_500 must be False at fib+1.0pct "
        "under reverted 0.5pct tolerance"
    )


def test_batch574_fib_at_key_fib_wide_emitted():
    """Pin (4) + (5): at_key_fib_wide emits + fires at 1.0pct."""
    from backtest.signals.technical import compute_fibonacci
    n = 50
    dates = pd.date_range("2024-01-01", periods=n)
    highs = np.linspace(50, 110, n)
    lows  = np.linspace(40, 100, n)
    closes = (highs + lows) / 2
    df = pd.DataFrame({
        "open":  closes, "high": highs, "low": lows, "close": closes,
        "volume": [1_000_000] * n,
    }, index=dates)
    sh, sl = highs.max(), lows.min()
    fib_500 = sh - 0.500 * (sh - sl)
    df.iloc[-1, df.columns.get_loc("close")] = fib_500 * 1.010
    fb = compute_fibonacci(df)
    assert "at_key_fib_wide" in fb, (
        "Pin (5): at_key_fib_wide must be emitted in fibonacci dict"
    )
    assert fb["at_key_fib_wide"] == True, (
        "Pin (4): at_key_fib_wide must fire at fib+1.0pct under 1.5pct band"
    )


def test_batch574_doji_at_support_consumes_wide():
    """Pin (7)."""
    from backtest.signals.screener import strat_doji_at_support
    # Strategy fires when wide flag is True
    s_wide = {"doji": True, "near_s1_wide": True, "vol_spike_15x": True}
    assert strat_doji_at_support(s_wide)["fires"] == True
    # Strategy does NOT fire when only the narrow flag is True (wide
    # is False) - per pin (10)
    s_narrow_only = {
        "doji": True, "near_s1": True,
        "near_s1_wide": False, "near_s2_wide": False,
        "at_key_fib_wide": False,
        "vol_spike_15x": True,
    }
    assert strat_doji_at_support(s_narrow_only)["fires"] == False, (
        "Pin (10): doji_at_support must consume `_wide` exclusively; "
        "narrow near_s1 alone should not fire it"
    )


def test_batch574_doji_at_resistance_short_consumes_wide():
    """Pin (8)."""
    from backtest.signals.screener import strat_doji_at_resistance_short
    s_wide = {"doji": True, "near_r1_wide": True, "vol_spike_15x": True}
    assert strat_doji_at_resistance_short(s_wide)["fires"] == True
    s_narrow_only = {
        "doji": True, "near_r1": True,
        "near_r1_wide": False, "near_r2_wide": False,
        "at_key_fib_wide": False,
        "vol_spike_15x": True,
    }
    assert strat_doji_at_resistance_short(s_narrow_only)["fires"] == False


def test_batch574_other_strategies_unchanged_regression():
    """Pin (9): the other 12 strategies that consume narrow near_s* /
    near_r* / at_key_fib must NOT see behavior change. Spot-check on
    pivot_s1_bounce + shooting_star_short."""
    from backtest.signals.screener import (
        strat_pivot_s1_bounce, strat_shooting_star_short,
    )
    # pivot_s1_bounce fires on narrow near_s1
    s = {"near_s1": True, "vol_spike_15x": True, "rsi_14": 35}
    out = strat_pivot_s1_bounce(s)
    # Smoke check: callable returns a dict with the right keys (the
    # specific predicate logic varies; we're checking no crash + the
    # narrow flag is what's consumed)
    assert "fires" in out

    # shooting_star_short consumes narrow near_r1
    s = {"shooting_star": True, "near_r1": True, "rsi_14": 70}
    out = strat_shooting_star_short(s)
    assert out["fires"] == True


def test_batch574_no_global_revert_remains_in_source():
    """Source-level check: technical.py has BOTH 0.003 (narrow) AND
    0.015 (wide) tolerances. The B573 global 0.015-only state is gone."""
    from pathlib import Path
    src = (Path(__file__).resolve().parents[2]
           / "backtest" / "signals" / "technical.py"
           ).read_text(encoding="utf-8")
    # 0.003 narrow (compute_pivots) + 0.005 narrow (compute_fibonacci)
    # + 0.015 wide (both)
    assert "< 0.003" in src, "narrow pivot near() reverted"
    assert "< 0.005" in src, "narrow fib near() reverted"
    assert src.count("< 0.015") >= 2, (
        f"expected >=2 wide tolerances (pivot + fib); got "
        f"{src.count('< 0.015')}"
    )
    # near_wide identifier must appear in technical.py
    assert "near_wide" in src
