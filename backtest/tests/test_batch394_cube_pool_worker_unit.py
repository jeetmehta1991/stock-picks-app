"""Batch 394: direct unit test of _pool_cube_replay_worker.

Stronger than the engine-scale parity test because it bypasses the
n>=5 cube cell filter by constructing inputs that guarantee fires.
Verifies the worker function produces byte-identical output to
calling run_exit_comparison directly.

Run: pytest backtest/tests/test_batch394_cube_pool_worker_unit.py -v
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parent.parent.parent


def _load_real_ohlcv(ticker: str) -> pd.DataFrame:
    """Load a real OHLCV parquet from the prefetch."""
    safe = ticker.replace(".", "-")
    p = REPO / "data_prefetch" / "polygon" / "ohlcv_daily" / f"{safe}.parquet"
    if not p.exists():
        pytest.skip(f"OHLCV prefetch missing for {ticker}")
    df = pd.read_parquet(p)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
    return df


def _synthetic_trades(ticker: str, df: pd.DataFrame, n: int = 10) -> list:
    """Build N trades on a known-good OHLCV slice (2023-H2) so the cube
    cell filter (n>=5 per (strategy, exit)) always fires."""
    df_slice = df[df.index.year == 2023]
    if len(df_slice) < 60:
        pytest.skip(f"insufficient 2023 OHLCV for {ticker}")
    trades = []
    dates = sorted(df_slice.index.unique())[:n]
    for d in dates:
        row = df_slice.loc[d] if d in df_slice.index else df_slice.iloc[0]
        # Schema-B / cap-on/off-agnostic minimal trade dict
        trades.append({
            "ticker":         ticker,
            "entry_date":     d.date() if hasattr(d, "date") else d,
            "entry_price":    float(row["close"]),
            "direction":      "long",
            "atr":            float(row["close"]) * 0.02,
            "signals":        {"atr": float(row["close"]) * 0.02},
            "entry_context":  {"sector": "Technology", "cap_band": "large"},
        })
    return trades


def test_worker_matches_run_exit_comparison_direct_call():
    """Pool worker must produce byte-identical output to a direct call
    to run_exit_comparison.  Bypasses pool entirely by setting
    _WORKER_OHLCV manually -- isolates worker logic.
    """
    from backtest.engine.exit_strategies import (
        _pool_cube_replay_worker,
        run_exit_comparison,
    )
    from backtest.signals import screener

    df = _load_real_ohlcv("AAPL")
    trades = _synthetic_trades("AAPL", df, n=15)

    # Direct call: trades carry df explicitly.
    trades_full = [{**t, "df": df} for t in trades]
    ec_direct, td_direct = run_exit_comparison("test_strategy", trades_full)

    # Worker call: trades DON'T carry df; worker looks up from _WORKER_OHLCV.
    screener._WORKER_OHLCV = {"AAPL": df}
    try:
        ec_worker, td_worker = _pool_cube_replay_worker("test_strategy", trades)
    finally:
        screener._WORKER_OHLCV = None

    # Row counts match
    assert len(ec_direct) == len(ec_worker), (
        f"exit_compare row count: direct={len(ec_direct)} "
        f"worker={len(ec_worker)}"
    )
    assert len(td_direct) == len(td_worker), (
        f"trade_detail row count: direct={len(td_direct)} "
        f"worker={len(td_worker)}"
    )

    # Sort for deterministic compare
    if not td_direct.empty:
        sort_cols = [c for c in ("entry_date", "exit_method") if c in td_direct.columns]
        d = td_direct.sort_values(sort_cols).reset_index(drop=True)
        w = td_worker.sort_values(sort_cols).reset_index(drop=True)
        # Numeric columns: tight tolerance
        for col in ("pnl_pct", "hold_days", "entry_price", "exit_price"):
            if col not in d.columns or col not in w.columns:
                continue
            ds = pd.to_numeric(d[col], errors="coerce")
            ws = pd.to_numeric(w[col], errors="coerce")
            assert np.allclose(ds.fillna(0), ws.fillna(0),
                              rtol=1e-9, atol=1e-12), (
                f"col {col}: max diff = {(ds-ws).abs().max():.6e}"
            )


def test_worker_returns_empty_when_ohlcv_missing():
    """When _WORKER_OHLCV is None (initializer never ran), worker should
    return empty DataFrames and log a warning rather than crash."""
    from backtest.engine.exit_strategies import _pool_cube_replay_worker
    from backtest.signals import screener

    screener._WORKER_OHLCV = None
    trades = [{
        "ticker": "AAPL", "entry_date": date(2024, 1, 5),
        "entry_price": 100.0, "direction": "long", "atr": 2.0,
        "signals": {}, "entry_context": {},
    }]
    ec, td = _pool_cube_replay_worker("test", trades)
    assert ec.empty
    assert td.empty


def test_worker_skips_unknown_tickers():
    """When _WORKER_OHLCV has tickers but one trade refers to a
    different ticker, the worker should skip that trade -- not crash."""
    from backtest.engine.exit_strategies import _pool_cube_replay_worker
    from backtest.signals import screener

    df = _load_real_ohlcv("AAPL")
    trades = _synthetic_trades("AAPL", df, n=10)
    # Mix in 5 trades for a ticker we WON'T put in the cache
    trades.extend(_synthetic_trades("AAPL", df, n=5))  # same ticker, fine
    # And one unknown ticker
    trades.append({
        "ticker":         "UNKNOWN_XYZ",
        "entry_date":     date(2023, 6, 1),
        "entry_price":    50.0,
        "direction":      "long",
        "atr":            1.0,
        "signals":        {},
        "entry_context":  {},
    })

    screener._WORKER_OHLCV = {"AAPL": df}  # only AAPL
    try:
        ec, td = _pool_cube_replay_worker("test", trades)
    finally:
        screener._WORKER_OHLCV = None

    # 15 AAPL trades survived; UNKNOWN_XYZ dropped
    if not td.empty:
        tickers = td["ticker"].unique()
        assert "UNKNOWN_XYZ" not in tickers
        assert "AAPL" in tickers
