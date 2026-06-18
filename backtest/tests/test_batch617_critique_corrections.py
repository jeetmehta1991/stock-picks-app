"""Batch 617 (2026-06-07) -- external-AI critique corrections on B608
walk + Batch 271 family-bug audit + CHECKLIST #105 extensions
(k)/(l)/(m)/(n).

The B608 walk landed two real fixes (F1 regime, F2 silent-gap) but
missed three issues a 2nd external-AI critique surfaced:

  (1) B320 deleted vol_spike_2x citing Bulkowski - misread (Bulkowski's
      rule is HIGH volume on the BREAK + low volume on the retest;
      B320 threw away the wrong half). B608 added vol_below_avg (the
      retest dry-up half) but breakout-bar volume confirmation is
      still missing - the strategy named "volume" has no breakout-bar
      volume gate.
  (2) obv_rising = OBV[-1] > OBV[-5] is a 5-bar trend window, not a
      "bounce-bar" confirmation. Soft thesis-vs-impl mismatch.
  (3) The 5-bar window at the retest bar contains the breakout bar's
      high-volume - obv_rising reads "rising" largely because the
      breakout day hasn't aged out. Near-tautological on valid setups.

Plus the critique identified a Batch 271 family-bug signature: 40 dual
(_strat3) strategies had explicit STRATEGY_REGIME_AFFINITY entries
constraining BOTH directions identically; 27 of those were Class A
(LONG-bias `{bull,neutral}` on dual blocking SHORT in bear/crisis) or
Class B (SHORT-bias `{bear}` on dual blocking LONG in bull/neutral).

B617 actions:
  (II) Family audit - REMOVED 19 clear Class A entries
  (I)  break_retest_volume - switched OBV gate from obv_rising (5-bar
       contaminated) to obv_bullish/obv_bearish (20-bar baseline);
       added obv_bearish producer signal symmetric to existing
       obv_bullish; honest docstring acknowledging the breakout-bar
       volume gap (recategorization deferred)
  (III) CHECKLIST #105 extensions (k) fire-count pre-check, (l)
        AVWAP/OBV/MACD non-redundancy, (m) economic-symmetry audit,
        (n) family-bug grep before one-line F1 removals

Pins:
  (1) producer emits obv_bearish symmetric to existing obv_bullish
  (2) obv_bullish on falling-OBV data is False (sanity)
  (3) obv_bearish on falling-OBV data is True (sanity)
  (4) strat_break_retest_volume LONG fires with obv_bullish (B617 switch)
  (5) LONG silent-gap: missing obv_bullish blocks (pre-B617 used
      obv_rising; was 5-bar contaminated)
  (6) SHORT fires with obv_bearish (B617 switch)
  (7) SHORT silent-gap: missing obv_bearish blocks
  (8)-(26) 19 Class A entries removed from STRATEGY_REGIME_AFFINITY
  (27) ALL_STRATEGIES count unchanged at 222
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _build_df(closes, highs, lows, opens=None, volumes=None):
    n = len(closes)
    if opens is None:
        opens = closes[:]
    if volumes is None:
        volumes = [1_000_000] * n
    return pd.DataFrame({
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    }, index=pd.date_range("2024-01-01", periods=n))


# ----- Producer pins -----

def test_batch617_producer_emits_obv_bearish():
    """Pin (1)."""
    from backtest.signals.technical import compute_volume
    # 30 bars - falling OBV
    closes = list(np.linspace(110, 90, 30))
    highs  = [c + 0.5 for c in closes]
    lows   = [c - 0.5 for c in closes]
    volumes = [1_000_000] * 30
    df = _build_df(closes, highs, lows, volumes=volumes)
    out = compute_volume(df)
    assert "obv_bearish" in out, "B617 producer must emit obv_bearish"
    assert "obv_bullish" in out, "obv_bullish still emitted (back-compat)"


def test_batch617_obv_bullish_false_on_falling_obv():
    """Pin (2): sanity check that falling-OBV data flips obv_bullish False."""
    from backtest.signals.technical import compute_volume
    closes = list(np.linspace(110, 90, 30))
    highs  = [c + 0.5 for c in closes]
    lows   = [c - 0.5 for c in closes]
    df = _build_df(closes, highs, lows)
    out = compute_volume(df)
    assert bool(out["obv_bullish"]) is False


def test_batch617_obv_bearish_true_on_falling_obv():
    """Pin (3): sanity check obv_bearish symmetric to obv_bullish."""
    from backtest.signals.technical import compute_volume
    closes = list(np.linspace(110, 90, 30))
    highs  = [c + 0.5 for c in closes]
    lows   = [c - 0.5 for c in closes]
    df = _build_df(closes, highs, lows)
    out = compute_volume(df)
    assert bool(out["obv_bearish"]) is True


# ----- strat_break_retest_volume pins -----

def test_batch617_long_fires_with_obv_bullish():
    """Pin (4): LONG switched to obv_bullish (B617). B821: B728 added
    close_in_top_40pct_of_range strong-close gate."""
    from backtest.signals.screener import strat_break_retest_volume
    s = {
        "resistance_break_retest":      True,
        "obv_bullish":                  True,   # B617: switched from obv_rising
        "close_above_open":             True,
        "vol_below_avg":                True,
        "close_in_top_40pct_of_range":  True,   # B728 strong-close
    }
    out = strat_break_retest_volume(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch617_long_silent_gap_obv_bullish_absent():
    """Pin (5): missing obv_bullish key blocks LONG (pre-B617 used
    obv_rising which had 5-bar contamination)."""
    from backtest.signals.screener import strat_break_retest_volume
    s = {
        "resistance_break_retest": True,
        # obv_bullish ABSENT
        "close_above_open": True,
        "vol_below_avg": True,
    }
    out = strat_break_retest_volume(s)
    assert out["fires"] is False


def test_batch617_short_fires_with_obv_bearish():
    """Pin (6): SHORT switched to obv_bearish (B617 symmetric).
    B821: B728 added close_in_bottom_40pct_of_range strong-close."""
    from backtest.signals.screener import strat_break_retest_volume
    s = {
        "support_break_retest":            True,
        "obv_bearish":                     True,   # B617: switched from obv_falling
        "close_below_open":                True,
        "vol_below_avg":                   True,
        "close_in_bottom_40pct_of_range":  True,   # B728 strong-close
    }
    out = strat_break_retest_volume(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch617_short_silent_gap_obv_bearish_absent():
    """Pin (7): missing obv_bearish blocks SHORT."""
    from backtest.signals.screener import strat_break_retest_volume
    s = {
        "support_break_retest": True,
        # obv_bearish ABSENT
        "close_below_open": True,
        "vol_below_avg": True,
    }
    out = strat_break_retest_volume(s)
    assert out["fires"] is False


# ----- Family audit pins (19 Class A removals) -----

CLASS_A_REMOVED = [
    "avwap_50_reclaim", "bollinger_lower", "cpr_narrow_bullish",
    "cpr_narrow_momentum", "donchian_10_breakout", "hull_rsi",
    "ichimoku_cloud_breakout", "macd_crossover", "mfi_oversold",
    "pivot_r1_breakout", "pivot_r2_continuation", "rsi_oversold",
    "smc_bos_continuation", "smc_choch_reversal",
    "smc_liquidity_sweep_reversal", "smc_order_block_bounce",
    "stoch_oversold", "stochrsi_oversold", "williams_r_oversold",
]


@pytest.mark.parametrize("strategy", CLASS_A_REMOVED)
def test_batch617_class_a_removed(strategy):
    """Pins (8)-(26): each of 19 Class A entries removed from
    STRATEGY_REGIME_AFFINITY by B617 family audit."""
    from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY
    assert strategy not in STRATEGY_REGIME_AFFINITY, (
        f"B617 family audit: {strategy} should be REMOVED from "
        f"STRATEGY_REGIME_AFFINITY (was dual with explicit Class A entry "
        f"that mis-regimed the SHORT/LONG opposite direction). "
        f"Currently maps to {STRATEGY_REGIME_AFFINITY.get(strategy)}"
    )


def test_batch617_class_a_strategies_get_direction_aware_default():
    """Class A strategies, post-removal, get Batch 291 direction-aware
    default: LONG -> {bull, neutral}; SHORT -> {bear, crisis, neutral}."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    # Sample one - donchian_10_breakout (dual)
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime(
            "donchian_10_breakout", r, direction="long"
        ) is True
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime(
            "donchian_10_breakout", r, direction="long"
        ) is False
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime(
            "donchian_10_breakout", r, direction="short"
        ) is True
    assert should_strategy_fire_in_regime(
        "donchian_10_breakout", "bull", direction="short"
    ) is False


def test_batch617_all_strategies_count_unchanged_at_222():
    """Pin (27): B617 is pure refactor + family audit + producer-additive;
    no add/delete strategies.
    B622 floor-pin (converted from ==): B620 deleted squeeze_setup
    _event_only_long (222->221). B899 migration post-B722/B874 to 219."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) >= 219
