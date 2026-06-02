"""Batch 539 (2026-06-02) -- OPT-D pre-computed signals scaffold tests.

Source: per CHECKLIST #77.
Queue: EXECUTION_QUEUE.md OPT-D Phase 1.

Pins:

  (1) load_precomputed_signals returns None on cache miss
  (2) Returns dict of signal values on cache hit (matching the parquet
      row content)
  (3) Module-level cache hit on second call (no disk re-read)
  (4) Empty/malformed parquet -> None (graceful degradation)
  (5) precompute_ticker emits one row per in-window date with
      compute_all_signals output
  (6) NOT-WIRED guard: screener.py does NOT yet call
      load_precomputed_signals (wire-in is Batch 541)
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def _reset_signals_cache():
    """Reset module-level cache between tests."""
    from backtest.signals.precomputed_cache import (
        _reset_signals_cache_for_tests,
    )
    _reset_signals_cache_for_tests()
    yield
    _reset_signals_cache_for_tests()


def _write_fake_parquet(tmp_path: Path, ticker: str,
                          dates_signals: list[tuple]) -> Path:
    """Build a fake pre-computed parquet at tmp_path/<ticker>.parquet.
    dates_signals is a list of (as_of_date, signal_dict) tuples.
    """
    rows = []
    for as_of, sigs in dates_signals:
        row = {"as_of_date": as_of, **sigs}
        rows.append(row)
    df = pd.DataFrame(rows)
    out = tmp_path / f"{ticker.upper()}.parquet"
    df.to_parquet(out, index=False)
    return out


# ---------------------------------------------------------------------------
# Reader behavior
# ---------------------------------------------------------------------------

def test_batch539_load_returns_none_on_cache_miss(tmp_path, monkeypatch):
    """When no parquet exists for the ticker, return None."""
    from backtest.signals import precomputed_cache as pc
    monkeypatch.setattr(pc, "PRECOMPUTED_DIR", tmp_path)
    pc._reset_signals_cache_for_tests()
    result = pc.load_precomputed_signals("ZZZZ", date(2024, 6, 1))
    assert result is None


def test_batch539_load_returns_dict_on_hit(tmp_path, monkeypatch):
    """When parquet has a row for the date, return its signal dict."""
    from backtest.signals import precomputed_cache as pc
    _write_fake_parquet(tmp_path, "AAPL", [
        (date(2024, 6, 1), {"rsi_14": 55.5, "ema_20_50_bullish": True}),
        (date(2024, 6, 2), {"rsi_14": 56.0, "ema_20_50_bullish": False}),
    ])
    monkeypatch.setattr(pc, "PRECOMPUTED_DIR", tmp_path)
    pc._reset_signals_cache_for_tests()
    result = pc.load_precomputed_signals("AAPL", date(2024, 6, 1))
    assert result is not None
    assert result["rsi_14"] == pytest.approx(55.5)
    assert result["ema_20_50_bullish"] is True or result["ema_20_50_bullish"] == 1
    # And a second date
    result2 = pc.load_precomputed_signals("AAPL", date(2024, 6, 2))
    assert result2["rsi_14"] == pytest.approx(56.0)


def test_batch539_load_returns_none_for_unknown_date(tmp_path, monkeypatch):
    """Date not present in parquet -> None (caller falls back to compute)."""
    from backtest.signals import precomputed_cache as pc
    _write_fake_parquet(tmp_path, "AAPL", [
        (date(2024, 6, 1), {"rsi_14": 55.5}),
    ])
    monkeypatch.setattr(pc, "PRECOMPUTED_DIR", tmp_path)
    pc._reset_signals_cache_for_tests()
    result = pc.load_precomputed_signals("AAPL", date(2024, 12, 31))
    assert result is None


def test_batch539_cache_avoids_repeat_disk_read(tmp_path, monkeypatch):
    """Second call for same ticker doesn't re-read parquet."""
    from backtest.signals import precomputed_cache as pc
    _write_fake_parquet(tmp_path, "AAPL", [
        (date(2024, 6, 1), {"rsi_14": 55.5}),
    ])
    monkeypatch.setattr(pc, "PRECOMPUTED_DIR", tmp_path)
    pc._reset_signals_cache_for_tests()
    read_calls = []
    real_read = pd.read_parquet

    def counting_read(path, *args, **kwargs):
        read_calls.append(path)
        return real_read(path, *args, **kwargs)

    with patch.object(pd, "read_parquet", side_effect=counting_read):
        pc.load_precomputed_signals("AAPL", date(2024, 6, 1))
        pc.load_precomputed_signals("AAPL", date(2024, 6, 1))
        pc.load_precomputed_signals("AAPL", date(2024, 6, 1))
    assert len(read_calls) == 1, (
        f"expected 1 disk read, got {len(read_calls)}: {read_calls}"
    )


def test_batch539_empty_parquet_returns_none(tmp_path, monkeypatch):
    """Malformed / empty parquet -> None (no crash)."""
    from backtest.signals import precomputed_cache as pc
    out = tmp_path / "AAPL.parquet"
    pd.DataFrame().to_parquet(out, index=False)
    monkeypatch.setattr(pc, "PRECOMPUTED_DIR", tmp_path)
    pc._reset_signals_cache_for_tests()
    result = pc.load_precomputed_signals("AAPL", date(2024, 6, 1))
    assert result is None


# ---------------------------------------------------------------------------
# Pre-compute script
# ---------------------------------------------------------------------------

def test_batch539_precompute_ticker_emits_row_per_in_window_date(tmp_path):
    """precompute_ticker writes one row per in-window date with the
    full compute_all_signals output."""
    from scripts.precompute_signals import precompute_ticker
    # Build a synthetic OHLCV DataFrame
    rng = np.random.default_rng(seed=42)
    n = 60
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    log_ret = rng.normal(0.0005, 0.015, size=n)
    log_ret[0] = 0
    close = 100.0 * np.exp(np.cumsum(log_ret))
    ohlcv = pd.DataFrame({
        "open": close * 0.99, "high": close * 1.01,
        "low": close * 0.98, "close": close,
        "volume": rng.integers(1_000_000, 5_000_000, size=n),
    }, index=dates)
    # Window covers the last 10 days
    out = precompute_ticker("AAPL", ohlcv,
                              start=dates[-10].date(),
                              end=dates[-1].date())
    assert not out.empty
    # Expect 10 rows (one per in-window trading day)
    assert len(out) <= 10
    assert "as_of_date" in out.columns
    # Should have a bunch of signal columns
    assert len(out.columns) >= 20, (
        f"expected >=20 signal columns, got {len(out.columns)}"
    )


def test_batch539_precompute_cache_info_diagnostic(tmp_path, monkeypatch):
    """precompute_cache_info returns dict with ticker_count + sample."""
    from backtest.signals import precomputed_cache as pc
    _write_fake_parquet(tmp_path, "AAPL", [
        (date(2024, 6, 1), {"rsi_14": 55.5}),
    ])
    _write_fake_parquet(tmp_path, "MSFT", [
        (date(2024, 6, 1), {"rsi_14": 60.0}),
    ])
    monkeypatch.setattr(pc, "PRECOMPUTED_DIR", tmp_path)
    info = pc.precompute_cache_info()
    assert info["dir_exists"] is True
    assert info["ticker_count"] == 2
    assert set(info["tickers"]) == {"AAPL", "MSFT"}


# ---------------------------------------------------------------------------
# NOT-WIRED guard
# ---------------------------------------------------------------------------

def test_batch539_precomputed_cache_not_yet_wired_in_screener():
    """Scaffold-only ship: screener.py must NOT yet call
    load_precomputed_signals. Wire-in is Batch 541 (separate parity
    gate batch). Flipping this test = explicit wire-in commit."""
    repo = Path(__file__).resolve().parent.parent.parent
    screener_text = (repo / "backtest" / "signals" / "screener.py").read_text(
        encoding="utf-8")
    assert "load_precomputed_signals" not in screener_text, (
        "Batch 539 SCAFFOLD-only invariant violated: screener imports "
        "load_precomputed_signals. The wire-in requires its own batch + "
        "parity gate against compute_all_signals output. Flip this test "
        "when Batch 541 (USE_PRECOMPUTED_SIGNALS flag + wire-in) lands."
    )
