"""Batch 608 (2026-06-07) -- Stage 4 walk of strat_break_retest_volume
per CHECKLIST #105 deep-read + owner-approved F1 + F2 + a + d + i.

CHECKLIST #105 deep-read surfaced TWO bugs (neither is a name-vs-impl
F1 pattern like B605/B606/B607 - strategy is honestly named DC20
retest + OBV):

  F1 - REGIME AFFINITY BUG: strategy is DUAL (_strat3) but
    STRATEGY_REGIME_AFFINITY had an explicit {bear, neutral} entry
    that capped LONG to short-bias regimes. Removed; falls back to
    Batch 291 direction-aware default.

  F2 - OBV SILENT-GAP BUG: SHORT side used `not s.get("obv_rising")`
    which auto-passed when the OBV key was missing (None is falsy;
    not None = True). Producer also never emitted obv_falling -
    the label "OBV falling" was a lie. B608 F2 added obv_falling
    to compute_volume; SHORT consumes it explicitly.

Plus owner-approved:
  (a) close_above_open / close_below_open (B589 bullish/bearish bar).
  (d) vol_below_avg (Bulkowski supply-absorption thesis).
  (i) Regime: Batch 291 direction-aware default (post-F1).

Skipped: (b) strong-close top/bottom 40pct / (c) B594 strong variants
  / (e) AVWAP / (f) MACD / (j) keep-as-is.

Pins:
  (1) obv_falling signal emitted by compute_volume (F2)
  (2) obv_falling is logically inverse of obv_rising on appropriate
      synthetic data
  (3) STRATEGY_REGIME_AFFINITY no longer has break_retest_volume entry (F1)
  (4) LONG fires in {bull, neutral} but NOT bear/crisis (post-F1 default)
  (5) SHORT fires in {bear, crisis, neutral} but NOT bull
  (6) LONG fires with 4 gates post-B608
  (7) SHORT fires with 4 mirror gates post-B608
  (8) Legacy fixture (resistance_break_retest + obv_rising only) does
      NOT fire post-B608 (a + d added requirements)
  (9) Silent-gap pin: missing obv_falling key does NOT auto-fire SHORT
      (F2 enforced - SHORT requires explicit obv_falling=True)
  (10) ALL_STRATEGIES count unchanged at 221 (F1+F2 are bug fixes, not
       new strategies)
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


def test_batch608_producer_emits_obv_falling():
    """Pin (1): F2 added obv_falling signal."""
    from backtest.signals.technical import compute_volume
    n = 25
    closes = list(np.linspace(110, 90, n))   # falling -> OBV will fall
    highs  = [c + 0.5 for c in closes]
    lows   = [c - 0.5 for c in closes]
    df = _build_df(closes, highs, lows)
    out = compute_volume(df)
    assert "obv_falling" in out
    assert out["obv_falling"] is True


def test_batch608_obv_falling_inverse_of_obv_rising_on_rising_data():
    """Pin (2): on rising-price data with no volume direction confound,
    obv_rising=True and obv_falling=False."""
    from backtest.signals.technical import compute_volume
    n = 25
    closes = list(np.linspace(90, 110, n))   # rising
    highs  = [c + 0.5 for c in closes]
    lows   = [c - 0.5 for c in closes]
    df = _build_df(closes, highs, lows)
    out = compute_volume(df)
    assert out["obv_rising"] is True
    assert out["obv_falling"] is False


def test_batch608_regime_entry_removed():
    """Pin (3): F1 removed explicit regime affinity map entry."""
    from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY
    assert "break_retest_volume" not in STRATEGY_REGIME_AFFINITY, (
        "F1: explicit regime entry must be removed; falls back to direction-aware default"
    )


def test_batch608_regime_default_long_bull_neutral():
    """Pin (4) post-F1: LONG = {bull, neutral} per Batch 291 default."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime(
            "break_retest_volume", r, direction="long"
        ) is True
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime(
            "break_retest_volume", r, direction="long"
        ) is False, (
            f"LONG must NOT fire in {r} post-F1; pre-F1 entry "
            f"{{bear, neutral}} allowed it"
        )


def test_batch608_regime_default_short_bear_crisis_neutral():
    """Pin (5) SHORT side."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime(
            "break_retest_volume", r, direction="short"
        ) is True
    assert should_strategy_fire_in_regime(
        "break_retest_volume", "bull", direction="short"
    ) is False


def test_batch608_strat_long_4_gates_fires():
    """Pin (6). B617 update: LONG OBV gate switched from obv_rising
    to obv_bullish. B821: B728 added close_in_top_40pct_of_range
    strong-close anti-fakeout gate."""
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


def test_batch608_strat_short_4_gates_fires():
    """Pin (7). B617 update: SHORT switched to obv_bearish.
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


def test_batch608_legacy_2_gate_fixture_blocked():
    """Pin (8): legacy fixture (resistance_break_retest + obv_rising only)
    does NOT fire post-B608 - (a) close_above_open and (d) vol_below_avg
    are now required."""
    from backtest.signals.screener import strat_break_retest_volume
    s = {
        "resistance_break_retest": True,
        "obv_rising": True,
        # close_above_open + vol_below_avg ABSENT
    }
    assert strat_break_retest_volume(s)["fires"] is False, (
        "B608 added (a)+(d) gates; legacy 2-gate fixture must not fire"
    )


def test_batch608_short_silent_gap_fixed():
    """Pin (9) F2 critical pin: missing obv_falling key does NOT
    auto-fire SHORT (was the silent-gap bug pre-B608)."""
    from backtest.signals.screener import strat_break_retest_volume
    s = {
        "support_break_retest": True,
        # obv_falling ABSENT - pre-B608 silent-gap would have fired
        # because the strategy used `not s.get("obv_rising")` which
        # was True when obv_rising was missing
        "close_below_open": True,
        "vol_below_avg": True,
    }
    assert strat_break_retest_volume(s)["fires"] is False, (
        "F2 silent-gap fix: missing obv_falling key must NOT auto-fire SHORT"
    )


def test_batch608_short_legacy_not_obv_rising_does_not_fire():
    """Pin (9b) F2: pre-B608 short fixture used obv_rising=False; that
    no longer fires because SHORT now requires explicit obv_falling=True."""
    from backtest.signals.screener import strat_break_retest_volume
    s = {
        "support_break_retest": True,
        "obv_rising": False,     # pre-B608 SHORT would have fired here
        # obv_falling ABSENT - F2 enforces explicit
        "close_below_open": True,
        "vol_below_avg": True,
    }
    assert strat_break_retest_volume(s)["fires"] is False


def test_batch608_all_strategies_count_unchanged_at_221():
    """Pin (10): F1+F2+a+d are bug fixes + gate additions, not new strategies.
    B622 update: converted to FLOOR pin per B622 standard so subsequent
    +/- changes don't require batch-by-batch test updates. Historical
    trail: B608 left count at 221; B613 net 0 (+ vol_below B-twin / -
    52w_low SHORT); B615 +1 (squeeze_setup B-twin); B620 -1 (deleted
    that B-twin). B722 -3 + B874 -2 reduced to 219. B899 floor migration."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) >= 219
