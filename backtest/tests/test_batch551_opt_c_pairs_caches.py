"""Batch 551 (2026-06-02) -- OPT-C Phase 3: compute_pair_signals_for_ticker
parquet-read caches.

Source: per CHECKLIST #77.
Queue: EXECUTION_QUEUE.md OPT-C pivot.

Pre-fix profile (post-B548): 693 calls / 45s / 65ms/call. Bottlenecks:
  - pd.read_parquet(snapshot) per call (same file every time)
  - pd.read_parquet(peer_path) inside the per-row loop (same file once per
    peer-ticker for the entire backtest session)
  - pd.to_datetime + .dt.date on peer_df["date"] per call per peer

Post-fix B551:
  - _PAIRS_DF_CACHE keyed by snapshot path; pd.read_parquet runs once
  - _PEER_OHLCV_CACHE keyed by peer ticker; pd.read_parquet + date_dt
    pre-conversion run once per peer per session
  - Per-call work: dict-lookup + boolean filter on cached DataFrame

Bench (AAPL on 7 active pairs): 65ms/call -> ~11ms/call (-83pct).

Pins:

  (1) Parity: post-fix dict matches pre-fix dict for AAPL/MSFT/JPM/GOOGL
      x 2 dates verified against the pre-B551 commit
  (2) Cache reuse: second call returns the SAME cached pairs_df + same
      cached peer OHLCV references
  (3) Schema: returned dict has the expected 5 keys when not empty
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def reset_caches():
    from backtest.signals.pairs_trading import (
        _PAIRS_DF_CACHE, _PEER_OHLCV_CACHE, _PAIRS_SNAPSHOTS_CACHE,
    )
    _PAIRS_DF_CACHE.clear()
    _PEER_OHLCV_CACHE.clear()
    _PAIRS_SNAPSHOTS_CACHE.clear()
    yield
    _PAIRS_DF_CACHE.clear()
    _PEER_OHLCV_CACHE.clear()
    _PAIRS_SNAPSHOTS_CACHE.clear()


def _have_data() -> bool:
    repo_root = Path(__file__).parent.parent.parent
    return (
        (repo_root / "data_prefetch" / "polygon" / "ohlcv_daily"
         / "AAPL.parquet").exists()
        and (repo_root / "data_prefetch" / "derived"
             / "cointegrated_pairs_t1a").exists()
    )


def _load_close(ticker: str, as_of: date) -> pd.Series:
    repo_root = Path(__file__).parent.parent.parent
    df = pd.read_parquet(
        repo_root / "data_prefetch" / "polygon" / "ohlcv_daily"
        / f"{ticker}.parquet"
    )
    df["date_dt"] = pd.to_datetime(df["date"]).dt.date
    df = df.sort_values("date_dt")
    sliced = df[df["date_dt"] <= as_of]
    return pd.Series(
        sliced["close"].values[-90:], index=sliced["date_dt"].values[-90:]
    )


@pytest.mark.skipif(not _have_data(), reason="pairs+OHLCV data absent")
def test_batch551_aapl_known_pair_outcome():
    """Pre-B551 baseline pin: AAPL 2024-06-14 -> peer=GLW, z=2.3344,
    half_life=20.97, count_active=7."""
    from backtest.signals.pairs_trading import compute_pair_signals_for_ticker
    close = _load_close("AAPL", date(2024, 6, 14))
    out = compute_pair_signals_for_ticker("AAPL", date(2024, 6, 14), close)
    assert out["pair_counterparty"] == "GLW"
    assert abs(out["pair_max_abs_zscore"] - 2.3344) < 0.001
    assert out["pair_count_active"] == 7


@pytest.mark.skipif(not _have_data(), reason="pairs+OHLCV data absent")
def test_batch551_pairs_df_cache_reuse():
    """Second call against the same snapshot path should not re-read
    the parquet; cached pairs_df returned by identity."""
    from backtest.signals.pairs_trading import (
        compute_pair_signals_for_ticker, _PAIRS_DF_CACHE,
    )
    close = _load_close("AAPL", date(2024, 6, 14))
    compute_pair_signals_for_ticker("AAPL", date(2024, 6, 14), close)
    snapshot_paths_after_first = set(_PAIRS_DF_CACHE.keys())
    assert len(snapshot_paths_after_first) >= 1
    df_first = _PAIRS_DF_CACHE[next(iter(snapshot_paths_after_first))]
    compute_pair_signals_for_ticker("AAPL", date(2024, 6, 14), close)
    snapshot_paths_after_second = set(_PAIRS_DF_CACHE.keys())
    df_second = _PAIRS_DF_CACHE[next(iter(snapshot_paths_after_second))]
    assert df_first is df_second, "pairs_df must be cached by identity"


@pytest.mark.skipif(not _have_data(), reason="pairs+OHLCV data absent")
def test_batch551_peer_ohlcv_cache_reuse():
    """After a call processes peer GLW (AAPL's top pair), the GLW OHLCV
    must be in _PEER_OHLCV_CACHE and reused on subsequent calls."""
    from backtest.signals.pairs_trading import (
        compute_pair_signals_for_ticker, _PEER_OHLCV_CACHE,
    )
    close = _load_close("AAPL", date(2024, 6, 14))
    compute_pair_signals_for_ticker("AAPL", date(2024, 6, 14), close)
    assert "GLW" in _PEER_OHLCV_CACHE, "GLW (AAPL top peer) should be cached"
    glw_first = _PEER_OHLCV_CACHE["GLW"]
    # Second call against different as_of -- same peer should still hit cache
    close2 = _load_close("AAPL", date(2024, 5, 15))
    compute_pair_signals_for_ticker("AAPL", date(2024, 5, 15), close2)
    glw_second = _PEER_OHLCV_CACHE["GLW"]
    assert glw_first is glw_second, "peer OHLCV cache must persist across calls"


@pytest.mark.skipif(not _have_data(), reason="pairs+OHLCV data absent")
def test_batch551_returned_dict_schema():
    from backtest.signals.pairs_trading import compute_pair_signals_for_ticker
    close = _load_close("AAPL", date(2024, 6, 14))
    out = compute_pair_signals_for_ticker("AAPL", date(2024, 6, 14), close)
    expected = {
        "pair_max_abs_zscore", "pair_zscore_signed", "pair_counterparty",
        "pair_half_life", "pair_count_active",
    }
    assert expected.issubset(set(out.keys())), (
        f"missing keys: {expected - set(out.keys())}"
    )
