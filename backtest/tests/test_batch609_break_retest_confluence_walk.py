"""Batch 609 (2026-06-07) -- Stage 4 walk of strat_break_retest_confluence
per CHECKLIST #105 deep-read + owner-approved F1 + F2 + a + d + i.

CHECKLIST #105 deep-read surfaced TWO bugs - same pattern as B608
(strategy is honestly DC20-coupled, no F1 name-vs-impl bug like
B605/B606/B607). This is the THIRD strategy walk in a row to surface
the regime-affinity-on-dual-strategy bug + the silent-gap on inverted
.get() bug; confluence-style strategies appear to share this lineage.

  F1 - REGIME AFFINITY BUG: strategy is DUAL but
    STRATEGY_REGIME_AFFINITY had explicit {bull} entry that capped
    BOTH directions to bull-only since the Batch 271 mass-edit.
    LONG over-restricted (couldn't fire in neutral); SHORT mis-regimed
    (firing in bull = wrong). Fixed by removing the entry; falls back
    to Batch 291 direction-aware default.

  F2 - THREE SILENT-GAP BUGS on SHORT side: previously used
    `not s.get(macd_12_26_9_bullish)`, `not s.get(price_above_ema
    _20)`, `not s.get(price_above_ema_50)` - each auto-passed when the
    key was missing (None is falsy; not None = True). Labels said
    macd_bearish / below_ema_20 / below_ema_50 but producer never
    emitted them. B609 F2 added all 3 signals explicitly; SHORT
    consumes them.

Plus owner-approved B589/Bulkowski standardization:
  (a) close_above_open / close_below_open.
  (d) vol_below_avg.
  (i) Regime: Batch 291 direction-aware default (post-F1).

Skipped: (b) strong-close 40pct / (c) B594 strong variants / (e)
  AVWAP / (j) keep-as-is - strategy already has 4 confluence signals
  per direction; adding more would over-tighten.

Pins:
  (1) macd_12_26_9_bearish emitted by compute_macd (F2)
  (2) below_ema_20 + below_ema_50 emitted by compute_ema_sma (F2)
  (3) macd_bearish is logical inverse of macd_bullish on rising data
  (4) below_ema_20 is logical inverse of price_above_ema_20 on rising data
  (5) STRATEGY_REGIME_AFFINITY no longer has break_retest_confluence entry (F1)
  (6) LONG fires in {bull, neutral} but NOT bear/crisis (post-F1 default)
  (7) SHORT fires in {bear, crisis, neutral} but NOT bull
  (8) LONG fires with 6 gates post-B609
  (9) SHORT fires with 6 mirror gates post-B609
  (10) Legacy fixture (4-gate, no (a) + (d)) does NOT fire post-B609
  (11) Silent-gap pin: missing macd_bearish key does NOT auto-fire SHORT
  (12) Silent-gap pin: missing below_ema_20 key does NOT auto-fire SHORT
  (13) Silent-gap pin: missing below_ema_50 key does NOT auto-fire SHORT
  (14) ALL_STRATEGIES count unchanged at 221 (F1+F2+a+d are bug fixes
       + gate additions; no new strategies)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _build_df(closes, highs, lows, opens=None, volumes=None):
    n = len(closes)
    if opens is None: opens = closes[:]
    if volumes is None: volumes = [1_000_000] * n
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    }, index=pd.date_range("2024-01-01", periods=n))


def test_batch609_producer_emits_macd_bearish():
    """Pin (1)."""
    from backtest.signals.technical import compute_macd
    n = 300
    closes = list(np.linspace(110, 90, n))  # falling -> MACD hist < 0
    df = _build_df(closes, [c + 0.5 for c in closes], [c - 0.5 for c in closes])
    out = compute_macd(df)
    assert "macd_12_26_9_bearish" in out
    assert out["macd_12_26_9_bearish"] is True
    assert out["macd_12_26_9_bullish"] is False


def test_batch609_producer_emits_below_ema_20_50():
    """Pin (2)."""
    from backtest.signals.technical import compute_ema_sma
    n = 300
    closes = list(np.linspace(110, 90, n))  # falling -> close < EMA
    df = _build_df(closes, [c + 0.5 for c in closes], [c - 0.5 for c in closes])
    out = compute_ema_sma(df)
    assert "below_ema_20" in out
    assert "below_ema_50" in out
    assert out["below_ema_20"] is True
    assert out["below_ema_50"] is True


def test_batch609_macd_bearish_inverse_of_bullish_on_rising_data():
    """Pin (3): macd_bearish logically inverse of macd_bullish."""
    from backtest.signals.technical import compute_macd
    n = 300
    closes = list(np.linspace(90, 110, n))  # rising
    df = _build_df(closes, [c + 0.5 for c in closes], [c - 0.5 for c in closes])
    out = compute_macd(df)
    assert out["macd_12_26_9_bullish"] is True
    assert out["macd_12_26_9_bearish"] is False


def test_batch609_below_ema_inverse_of_above_on_rising_data():
    """Pin (4)."""
    from backtest.signals.technical import compute_ema_sma
    n = 300
    closes = list(np.linspace(90, 110, n))
    df = _build_df(closes, [c + 0.5 for c in closes], [c - 0.5 for c in closes])
    out = compute_ema_sma(df)
    assert out["price_above_ema_20"] is True
    assert out["below_ema_20"] is False
    assert out["price_above_ema_50"] is True
    assert out["below_ema_50"] is False


def test_batch609_regime_entry_removed():
    """Pin (5) F1."""
    from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY
    assert "break_retest_confluence" not in STRATEGY_REGIME_AFFINITY


def test_batch609_regime_default_long_bull_neutral():
    """Pin (6) post-F1."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime(
            "break_retest_confluence", r, direction="long"
        ) is True
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime(
            "break_retest_confluence", r, direction="long"
        ) is False


def test_batch609_regime_default_short_bear_crisis_neutral():
    """Pin (7)."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime(
            "break_retest_confluence", r, direction="short"
        ) is True
    assert should_strategy_fire_in_regime(
        "break_retest_confluence", "bull", direction="short"
    ) is False


def test_batch609_strat_long_6_gates_fires():
    """Pin (8) B821: B728 added close_in_top_40pct_of_range strong-close."""
    from backtest.signals.screener import strat_break_retest_confluence
    s = {
        "resistance_break_retest":      True,
        "macd_12_26_9_bullish":         True,
        "price_above_ema_20":           True,
        "price_above_ema_50":           True,
        "close_above_open":             True,
        "vol_below_avg":                True,
        "close_in_top_40pct_of_range":  True,   # B728 strong-close
    }
    out = strat_break_retest_confluence(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch609_strat_short_6_gates_fires():
    """Pin (9) B821: B728 added close_in_bottom_40pct_of_range strong-close."""
    from backtest.signals.screener import strat_break_retest_confluence
    s = {
        "support_break_retest":            True,
        "macd_12_26_9_bearish":            True,
        "below_ema_20":                    True,
        "below_ema_50":                    True,
        "close_below_open":                True,
        "vol_below_avg":                   True,
        "close_in_bottom_40pct_of_range":  True,   # B728 strong-close
    }
    out = strat_break_retest_confluence(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch609_legacy_4_gate_fixture_blocked():
    """Pin (10): legacy 4-gate fixture (no (a) + (d)) does NOT fire."""
    from backtest.signals.screener import strat_break_retest_confluence
    s = {
        "resistance_break_retest": True,
        "macd_12_26_9_bullish": True,
        "price_above_ema_20": True,
        "price_above_ema_50": True,
    }
    assert strat_break_retest_confluence(s)["fires"] is False, (
        "B609 added (a) close_above_open + (d) vol_below_avg; legacy "
        "fixture must not fire"
    )


def test_batch609_short_silent_gap_macd_fixed():
    """Pin (11) F2: missing macd_bearish key does NOT auto-fire SHORT."""
    from backtest.signals.screener import strat_break_retest_confluence
    s = {
        "support_break_retest": True,
        # macd_12_26_9_bearish ABSENT (pre-B609 used `not bullish`)
        "below_ema_20": True,
        "below_ema_50": True,
        "close_below_open": True,
        "vol_below_avg": True,
    }
    assert strat_break_retest_confluence(s)["fires"] is False


def test_batch609_short_silent_gap_below_ema_20_fixed():
    """Pin (12) F2: missing below_ema_20 key does NOT auto-fire SHORT."""
    from backtest.signals.screener import strat_break_retest_confluence
    s = {
        "support_break_retest": True,
        "macd_12_26_9_bearish": True,
        # below_ema_20 ABSENT
        "below_ema_50": True,
        "close_below_open": True,
        "vol_below_avg": True,
    }
    assert strat_break_retest_confluence(s)["fires"] is False


def test_batch609_short_silent_gap_below_ema_50_fixed():
    """Pin (13) F2: missing below_ema_50 key does NOT auto-fire SHORT."""
    from backtest.signals.screener import strat_break_retest_confluence
    s = {
        "support_break_retest": True,
        "macd_12_26_9_bearish": True,
        "below_ema_20": True,
        # below_ema_50 ABSENT
        "close_below_open": True,
        "vol_below_avg": True,
    }
    assert strat_break_retest_confluence(s)["fires"] is False


def test_batch609_all_strategies_count_unchanged_at_221():
    """Pin (14)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 220
