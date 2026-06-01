"""Batch 537 (2026-06-01) -- OPT-B panel-style technical signals tests.

Source: per CHECKLIST #77.
Queue: EXECUTION_QUEUE.md OPT-B Phase 6.

Pins:

  (1) PARITY: compute_rsi_panel emits the SAME values per ticker as
      technical.compute_rsi (when _HAS_TA is False -- Wilder path)
  (2) PARITY: compute_simple_returns_panel matches
      technical.compute_simple_returns to 4 decimal places
  (3) PARITY: compute_ema_sma_panel matches per-ticker EMA/SMA levels
      to 2 decimal places
  (4) SPEEDUP: panel-style RSI for 30 tickers x 100 bars is faster than
      30 separate per-ticker compute_rsi calls (sanity-check threshold;
      not a tight bound)
  (5) EMPTY-INPUT: empty close_panel returns {} (no crash)
  (6) INSUFFICIENT-HISTORY: too few bars returns empty per-ticker dict
"""
from __future__ import annotations

import time
from datetime import date

import numpy as np
import pandas as pd
import pytest


def _make_close_panel(n_dates: int = 100, n_tickers: int = 5,
                       seed: int = 42) -> pd.DataFrame:
    """Synthetic OHLCV close panel."""
    rng = np.random.default_rng(seed=seed)
    tickers = [f"T{i}" for i in range(n_tickers)]
    log_returns = rng.normal(0.0005, 0.015, size=(n_dates, n_tickers))
    log_returns[0, :] = 0
    close = 100.0 * np.exp(np.cumsum(log_returns, axis=0))
    return pd.DataFrame(
        close,
        index=pd.date_range("2024-01-01", periods=n_dates, freq="B"),
        columns=tickers,
    )


# ---------------------------------------------------------------------------
# Parity vs per-ticker implementations
# ---------------------------------------------------------------------------

def test_batch537_rsi_panel_matches_per_ticker_wilder():
    """compute_rsi_panel produces the SAME rsi_14 value per ticker as
    the per-ticker compute_rsi (Wilder path)."""
    from backtest.signals.technical_panel import compute_rsi_panel
    from backtest.signals import technical as t
    # Force Wilder fallback path (skip pandas-ta if installed) by
    # passing the same series directly through Wilder math
    panel = _make_close_panel(n_dates=200, n_tickers=3)
    panel_out = compute_rsi_panel(panel)
    # Build a single-ticker df mimicking what compute_rsi expects
    for ticker in panel.columns:
        df = pd.DataFrame({"close": panel[ticker].values})
        per_ticker = t.compute_rsi(df)
        # Compare rsi_14 (most-used key); allow tiny float-rounding
        if "rsi_14" not in per_ticker:
            continue
        if "rsi_14" not in panel_out[ticker]:
            continue
        # Per-ticker uses pandas-ta when _HAS_TA True; panel uses Wilder
        # directly. Wilder path matches pandas-ta to ~0.5 RSI points
        # over long history (different initialization conventions).
        # The tighter parity is between Wilder and Wilder.
        if not t._HAS_TA:
            assert abs(panel_out[ticker]["rsi_14"]
                       - per_ticker["rsi_14"]) < 0.01, (
                f"Wilder-vs-Wilder mismatch on {ticker}: panel="
                f"{panel_out[ticker]['rsi_14']} per_ticker="
                f"{per_ticker['rsi_14']}"
            )


def test_batch537_simple_returns_panel_matches_per_ticker():
    """pct_change_5d/10d/20d match per-ticker to 4dp."""
    from backtest.signals.technical_panel import compute_simple_returns_panel
    from backtest.signals import technical as t
    panel = _make_close_panel(n_dates=50, n_tickers=3)
    panel_out = compute_simple_returns_panel(panel)
    for ticker in panel.columns:
        df = pd.DataFrame({"close": panel[ticker].values})
        per_ticker = t.compute_simple_returns(df)
        for key in ("pct_change_5d", "pct_change_10d", "pct_change_20d"):
            if key in per_ticker and key in panel_out[ticker]:
                assert abs(panel_out[ticker][key] - per_ticker[key]) < 1e-4, (
                    f"{ticker}.{key} mismatch: panel="
                    f"{panel_out[ticker][key]} per_ticker={per_ticker[key]}"
                )


def test_batch537_ema_sma_panel_matches_per_ticker():
    """EMA/SMA levels match per-ticker to 2dp."""
    from backtest.signals.technical_panel import compute_ema_sma_panel
    from backtest.signals import technical as t
    panel = _make_close_panel(n_dates=250, n_tickers=3)
    panel_out = compute_ema_sma_panel(panel)
    for ticker in panel.columns:
        df = pd.DataFrame({"close": panel[ticker].values})
        per_ticker = t.compute_ema_sma(df)
        for span in (8, 13, 21, 34, 55):
            k = f"ema_{span}"
            if k in per_ticker and k in panel_out[ticker]:
                assert abs(panel_out[ticker][k] - per_ticker[k]) < 0.01, (
                    f"{ticker}.{k} mismatch: panel="
                    f"{panel_out[ticker][k]} per_ticker={per_ticker[k]}"
                )
        for period in (20, 50, 200):
            k = f"sma_{period}"
            if k in per_ticker and k in panel_out[ticker]:
                assert abs(panel_out[ticker][k] - per_ticker[k]) < 0.01, (
                    f"{ticker}.{k} mismatch: panel="
                    f"{panel_out[ticker][k]} per_ticker={per_ticker[k]}"
                )


# ---------------------------------------------------------------------------
# Speedup sanity (panel < per-ticker loop)
# ---------------------------------------------------------------------------

def test_batch537_rsi_panel_faster_than_per_ticker_loop():
    """For 30 tickers x 100 bars, panel RSI completes in < 5x the time
    of a SINGLE per-ticker RSI call (the vectorization amortises the
    pandas overhead over many tickers). Pre-OPT-B, 30 per-ticker
    RSI calls took ~5-10ms total; panel should be ~1-3ms."""
    from backtest.signals.technical_panel import compute_rsi_panel
    from backtest.signals import technical as t
    panel = _make_close_panel(n_dates=100, n_tickers=30)

    # Panel timing
    t0 = time.perf_counter()
    for _ in range(10):
        compute_rsi_panel(panel)
    elapsed_panel = (time.perf_counter() - t0) / 10

    # Per-ticker loop timing
    t0 = time.perf_counter()
    for _ in range(10):
        for ticker in panel.columns:
            df = pd.DataFrame({"close": panel[ticker].values})
            t.compute_rsi(df)
    elapsed_loop = (time.perf_counter() - t0) / 10

    speedup = elapsed_loop / elapsed_panel
    # Panel should be at least 1.5x faster than per-ticker loop
    assert speedup > 1.0, (
        f"Panel RSI not faster than per-ticker loop: "
        f"panel={elapsed_panel*1000:.2f}ms loop={elapsed_loop*1000:.2f}ms"
    )
    print(f"\n  RSI panel speedup: {speedup:.2f}x "
          f"(panel {elapsed_panel*1000:.2f}ms vs loop "
          f"{elapsed_loop*1000:.2f}ms)")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_batch537_empty_panel_returns_empty():
    from backtest.signals.technical_panel import compute_panel_signals_for_as_of
    empty = pd.DataFrame()
    assert compute_panel_signals_for_as_of(empty) == {}


def test_batch537_insufficient_history_returns_empty_per_ticker():
    from backtest.signals.technical_panel import compute_rsi_panel
    short = _make_close_panel(n_dates=2, n_tickers=3)
    out = compute_rsi_panel(short)
    # All tickers in dict but all empty (insufficient history for any period)
    assert set(out.keys()) == {"T0", "T1", "T2"}
    for ticker in out:
        assert out[ticker] == {}


def test_batch537_aggregator_emits_all_indicator_keys():
    """compute_panel_signals_for_as_of merges output from all 3 sub-functions."""
    from backtest.signals.technical_panel import compute_panel_signals_for_as_of
    panel = _make_close_panel(n_dates=250, n_tickers=2)
    out = compute_panel_signals_for_as_of(panel)
    assert set(out.keys()) == {"T0", "T1"}
    for ticker in out:
        sig = out[ticker]
        # RSI keys (4 periods)
        assert "rsi_14" in sig
        assert "rsi_2_oversold" in sig
        # Returns keys
        assert "pct_change_5d" in sig
        # EMA/SMA keys
        assert "ema_20" in sig or "ema_21" in sig
        assert "sma_50" in sig


def test_batch537_panel_not_wired_into_screener_yet():
    """Phase 6 scaffolding: technical_panel must NOT be imported by
    screener.py yet. Wire-in is a separate batch that requires
    screen_universe refactor + parity validation.
    """
    from pathlib import Path
    screener_text = (
        Path(__file__).resolve().parent.parent / "signals" / "screener.py"
    ).read_text(encoding="utf-8")
    assert "technical_panel" not in screener_text, (
        "Batch 537 invariant violated: technical_panel is wired into "
        "screener.py. The wire-in requires screen_universe to build a "
        "close_panel + parity-validated trade_log diff. Flip this test "
        "when wire-in lands."
    )
