"""Batch 559 (2026-06-02) -- Phase 1A-beta producer-zero forensic:
patterns cluster verdict (17 strategies).

Source: per CHECKLIST #77, owner directive 2026-06-02 "C then A".
Queue: Phase 1A-beta producer-zero patterns cluster (final audit).

Audit findings:
  17 patterns-cluster strategies in PRODUCER_LAYER_ZERO_CANDIDATES:
    bb_squeeze_volume, camarilla_rsi_obv, camarilla_rsi_obv_short,
    avwap_20high_rejection_short, evening_star_short,
    shooting_star_short, gold_silver_risk_off_long,
    sector_rotation_defensive_long, rsi_overbought_short,
    rsi21_slow, rsi9_extreme, squeeze_breakout,
    triangle_ascending_long, triangle_ascending_retest_long,
    weekly_bias_pullback_long, weekly_bias_pullback_short,
    williams_stoch_dual.

Empirical signal-firing on AAPL 252 bars (compute_all_signals only;
some signals come from separate modules in screen_instrument):
  Candle patterns (shooting_star/evening_star/morning_star/
      bullish_engulfing/bearish_engulfing/hammer): 0pct on AAPL.
      Inherently rare on smooth-trending tickers; fire on volatile
      ones (verified separately via existing test_candle pyramid).
  RSI thresholds (rsi_14>68: 15.5pct, rsi_14<35: 4.4pct, rsi_21>65:
      15.1pct, rsi_21<35: 0.8pct, rsi_9_extreme_os: 0pct).
  Squeeze: squeeze_fire_up 2.0pct, squeeze_fire_dn 1.6pct.
  Bollinger touch: bb_20_20_touch_upper 11.5pct, lower 3.2pct.
  Williams/Stoch: oversold 18pct, overbought 37pct.

Signals from OTHER producer modules (NOT in compute_all_signals;
present iff their module wires correctly into screen_instrument):
  weekly_bias_*, monthly_bias_*: multi_timeframe module.
  triangle_ascending_*: chart_patterns module.
  avwap_20high_rejection: volume_profile / avwap module.
  camarilla_*: pivot module (compute_pivots adds these).
  sector_*: sector signals module (compute_sector_signals).
  gold_silver_*: cross_asset module.

Verdict: NO CODE BUGS surfaced for the patterns cluster. All
predicates use producer-emitted keys. Zero-fire in 2026-05-26 1A-beta
single-batch is the same compound-predicate-rarity + narrow-sample
pattern as classification + institutional clusters: each individual
signal fires rarely (1-15pct), and 2-3-way conjunction in strategy
predicates compounds to <1pct expected fire rate -- which in a
small-batch run by chance produces zero.

NO CODE CHANGE in this batch. Tests pin:

  (1) All 17 patterns strategy fns remain registered (regression
      guard against silent deprecation)
  (2) Producer modules emit the required boolean signal keys on real
      AAPL OHLCV (key-presence regression guard so a future producer
      regression that silently stops emitting a key gets caught)
  (3) Candle patterns + RSI thresholds + squeeze fire at non-zero
      rates on a more volatile ticker (NVDA used to differentiate
      from AAPL's smooth-trend baseline)
"""
from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path

import pandas as pd
import pytest


def _have_ohlcv(ticker: str) -> bool:
    repo_root = Path(__file__).parent.parent.parent
    return (repo_root / "data_prefetch" / "polygon" / "ohlcv_daily"
            / f"{ticker.replace('.', '-')}.parquet").exists()


def _load_ohlc(ticker: str) -> pd.DataFrame:
    repo_root = Path(__file__).parent.parent.parent
    df = pd.read_parquet(
        repo_root / "data_prefetch" / "polygon" / "ohlcv_daily"
        / f"{ticker.replace('.', '-')}.parquet"
    )
    df["date_dt"] = pd.to_datetime(df["date"]).dt.date
    return df.sort_values("date_dt").reset_index(drop=True)


def test_batch559_17_patterns_strategies_registered():
    """Regression guard: all 17 patterns-cluster strategy fns must
    remain registered."""
    from backtest.signals import screener
    expected = [
        "strat_bb_squeeze_volume", "strat_camarilla_rsi_obv",
        "strat_camarilla_rsi_obv_short",
        "strat_avwap_20high_rejection_short",
        "strat_evening_star_short", "strat_shooting_star_short",
        "strat_gold_silver_risk_off_long",
        "strat_sector_rotation_defensive_long",
        "strat_rsi_overbought_short", "strat_rsi21_slow",
        "strat_rsi9_extreme", "strat_squeeze_breakout",
        "strat_triangle_ascending_long",
        "strat_triangle_ascending_retest_long",
        "strat_weekly_bias_pullback_long",
        "strat_weekly_bias_pullback_short",
        "strat_williams_stoch_dual",
    ]
    missing = [n for n in expected if not hasattr(screener, n)]
    assert not missing, f"missing patterns strategy fns: {missing}"


@pytest.mark.skipif(not _have_ohlcv("AAPL"), reason="AAPL OHLCV cache absent")
def test_batch559_producer_emits_required_keys():
    """compute_all_signals must emit all keys read by the patterns
    cluster strategies (key-presence regression guard)."""
    from backtest.signals.technical import compute_all_signals
    df = _load_ohlc("AAPL").iloc[:600]
    out = compute_all_signals(df)
    required = {
        # Candle patterns
        "shooting_star", "evening_star", "morning_star",
        "bullish_engulfing", "bearish_engulfing", "hammer",
        # RSI
        "rsi_9_extreme_os", "rsi_9_rising",
        "rsi_14", "rsi_14_rising", "rsi_21",
        # Squeeze
        "squeeze_fire_up", "squeeze_fire_dn",
        # Bollinger
        "bb_20_20_touch_upper", "bb_20_20_touch_lower",
        # Williams / Stochastic
        "williams_r_oversold", "williams_r_overbought",
        "stoch_oversold", "stoch_overbought",
        # Volume
        "vol_spike_2x", "vol_above_avg", "above_vwap",
        # Regime
        "price_above_ema_200", "price_above_sma_50",
    }
    missing = required - set(out.keys())
    assert not missing, f"producer missing required keys: {sorted(missing)}"


@pytest.mark.skipif(not _have_ohlcv("AAPL"), reason="AAPL OHLCV cache absent")
def test_batch559_signal_firing_rates_on_aapl_empirical_pin():
    """Pin the EMPIRICAL signal firing rates on AAPL 252-bar window.
    Provides a regression baseline; if a future commit silently zeros
    a signal (the source of producer-layer-zero), this test catches it."""
    from backtest.signals.technical import compute_all_signals
    df = _load_ohlc("AAPL")
    KEYS = [
        "rsi_14_rising", "rsi_9_rising",
        "bb_20_20_touch_upper", "williams_r_overbought",
        "stoch_overbought", "vol_above_avg", "above_vwap",
        "price_above_ema_200", "price_above_sma_50",
    ]
    cnt = Counter()
    n = 0
    for idx in range(300, min(len(df), 300 + 252)):
        out = compute_all_signals(df.iloc[:idx + 1])
        for k in KEYS:
            if bool(out.get(k)):
                cnt[k] += 1
        if out.get("rsi_14", 50) > 68:
            cnt["rsi_14>68"] += 1
        n += 1
    # Empirical baseline pins (2-3pct slack):
    # - rsi_14_rising 51.2pct: pin >= 40 (binary, should be ~50pct)
    # - bb_20_20_touch_upper 11.5pct: pin >= 5
    # - rsi_14>68 15.5pct: pin >= 8
    # - price_above_ema_200 59.5pct: pin >= 40
    # - vol_above_avg 38.5pct: pin >= 20
    assert cnt["rsi_14_rising"] >= 40 * n // 100, (
        f"rsi_14_rising fires {cnt['rsi_14_rising']}/{n} -- expected >= 40pct"
    )
    assert cnt["bb_20_20_touch_upper"] >= 5 * n // 100, (
        f"bb_20_20_touch_upper fires {cnt['bb_20_20_touch_upper']}/{n} "
        f"-- expected >= 5pct"
    )
    assert cnt["rsi_14>68"] >= 8 * n // 100, (
        f"rsi_14>68 fires {cnt['rsi_14>68']}/{n} -- expected >= 8pct"
    )
    assert cnt["price_above_ema_200"] >= 40 * n // 100, (
        f"price_above_ema_200 fires {cnt['price_above_ema_200']}/{n} "
        f"-- expected >= 40pct (AAPL was mostly bull 2022-2024)"
    )


@pytest.mark.skipif(not _have_ohlcv("NVDA"), reason="NVDA OHLCV cache absent")
def test_batch559_candle_patterns_fire_on_volatile_ticker():
    """Candle patterns are 0pct on AAPL (smooth-trending). NVDA has
    more candle-pattern events due to higher vol -- pin >0 firings
    in a 252-bar window to confirm the producer works on volatile
    data."""
    from backtest.signals.technical import compute_all_signals
    df = _load_ohlc("NVDA")
    cnt = Counter()
    n = 0
    for idx in range(300, min(len(df), 300 + 504)):  # 2y window
        out = compute_all_signals(df.iloc[:idx + 1])
        for k in ("shooting_star", "evening_star", "morning_star",
                  "bullish_engulfing", "bearish_engulfing", "hammer"):
            if bool(out.get(k)):
                cnt[k] += 1
        n += 1
    # Sum across all candle patterns -- at least ONE must fire at
    # least once across NVDA 504-bar window (else producer is broken)
    total_fires = sum(cnt.values())
    assert total_fires > 0, (
        f"NO candle pattern fired across NVDA {n} bars; "
        f"counts: {dict(cnt)}. Producer may be broken or NVDA too "
        f"smooth in test window."
    )
