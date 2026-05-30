"""Batch 499 (2026-05-31) -- Item 7 analyst overlay tests.

Source: per CHECKLIST #77.
Queue row: EXECUTION_QUEUE.md item 7.
Script: scripts/analyst_overlay_from_trade_log.py.

Tests the no-rerun analyst pass that reconstructs equity_curve +
portfolio summary + strategy_regime_matrix from a cube trade_log.csv.
Synthetic trade logs feed into the functions so output is
deterministic.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import json
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Equity-curve reconstruction
# ---------------------------------------------------------------------------

def _make_trade_log(rows):
    return pd.DataFrame(rows, columns=[
        "ticker", "entry_date", "exit_date", "direction", "strategy",
        "regime", "win", "pnl_pct", "pnl_dollar", "hold_days",
    ])


def test_batch499_equity_curve_basic_cumulative():
    """5 trades closing on consecutive days, +$100 each -> linear ramp."""
    from scripts.analyst_overlay_from_trade_log import reconstruct_equity_curve
    rows = [
        ("AAPL", "2024-01-02", "2024-01-05", "long", "s1", "bull", 1, 1.0, 100, 3),
        ("MSFT", "2024-01-03", "2024-01-08", "long", "s1", "bull", 1, 1.0, 100, 5),
        ("GOOG", "2024-01-04", "2024-01-09", "long", "s2", "bull", 1, 1.0, 100, 5),
        ("AMZN", "2024-01-05", "2024-01-10", "long", "s2", "bull", 1, 1.0, 100, 5),
        ("META", "2024-01-06", "2024-01-11", "long", "s3", "bull", 1, 1.0, 100, 5),
    ]
    df = _make_trade_log(rows)
    curve = reconstruct_equity_curve(df, starting_capital=10_000)
    assert len(curve) == 5
    assert curve["equity_dollar"].iloc[0] == 10_100
    assert curve["equity_dollar"].iloc[-1] == 10_500


def test_batch499_equity_curve_handles_losses():
    """Mix of wins + losses -> equity goes both directions."""
    from scripts.analyst_overlay_from_trade_log import reconstruct_equity_curve
    rows = [
        ("AAPL", "2024-01-02", "2024-01-05", "long", "s1", "bull", 1,  1.0,  500, 3),
        ("MSFT", "2024-01-06", "2024-01-08", "long", "s1", "bull", 0, -2.0, -200, 2),
        ("GOOG", "2024-01-09", "2024-01-12", "long", "s2", "bull", 0, -1.0, -300, 3),
    ]
    df = _make_trade_log(rows)
    curve = reconstruct_equity_curve(df, starting_capital=10_000)
    assert curve["equity_dollar"].iloc[0] == 10_500   # after $500 win
    assert curve["equity_dollar"].iloc[1] == 10_300   # after $200 loss
    assert curve["equity_dollar"].iloc[2] == 10_000   # back to start


def test_batch499_equity_curve_groups_same_day_exits():
    """Two trades closing on the same day -> single curve row."""
    from scripts.analyst_overlay_from_trade_log import reconstruct_equity_curve
    rows = [
        ("AAPL", "2024-01-02", "2024-01-05", "long", "s1", "bull", 1, 1.0, 100, 3),
        ("MSFT", "2024-01-02", "2024-01-05", "long", "s1", "bull", 1, 1.0, 200, 3),
    ]
    df = _make_trade_log(rows)
    curve = reconstruct_equity_curve(df, starting_capital=10_000)
    assert len(curve) == 1
    assert curve["equity_dollar"].iloc[0] == 10_300
    assert curve["trades_closed"].iloc[0] == 2


def test_batch499_equity_curve_empty_trade_log():
    from scripts.analyst_overlay_from_trade_log import reconstruct_equity_curve
    curve = reconstruct_equity_curve(pd.DataFrame(), starting_capital=10_000)
    assert len(curve) == 1
    assert curve["equity_dollar"].iloc[0] == 10_000
    assert curve["trades_closed"].iloc[0] == 0


# ---------------------------------------------------------------------------
# Portfolio summary
# ---------------------------------------------------------------------------

def test_batch499_portfolio_summary_total_return():
    from scripts.analyst_overlay_from_trade_log import (
        reconstruct_equity_curve, compute_portfolio_summary_from_curve,
    )
    rows = [
        ("AAPL", "2024-01-02", "2024-01-05", "long", "s1", "bull", 1, 1.0, 500, 3),
        ("MSFT", "2024-01-06", "2024-01-08", "long", "s1", "bull", 1, 1.0, 500, 2),
    ]
    curve = reconstruct_equity_curve(_make_trade_log(rows), 10_000)
    summary = compute_portfolio_summary_from_curve(curve, 10_000)
    # Started 10k, ended 11k -> +10%
    assert summary["total_return_pct"] == pytest.approx(10.0, abs=1e-4)
    assert summary["ending_equity"] == 11_000


def test_batch499_portfolio_summary_max_drawdown():
    from scripts.analyst_overlay_from_trade_log import (
        reconstruct_equity_curve, compute_portfolio_summary_from_curve,
    )
    # Up 10%, then down 20%, then flat
    rows = [
        ("AAPL", "2024-01-02", "2024-01-05", "long", "s1", "bull", 1,  1.0,  1000, 3),
        ("MSFT", "2024-01-06", "2024-01-08", "long", "s1", "bull", 0, -2.0, -2200, 2),
    ]
    curve = reconstruct_equity_curve(_make_trade_log(rows), 10_000)
    summary = compute_portfolio_summary_from_curve(curve, 10_000)
    # Peak 11k -> trough 8.8k -> 20% drawdown
    assert summary["max_drawdown_pct"] == pytest.approx(-20.0, abs=1e-4)


def test_batch499_portfolio_summary_empty_curve():
    from scripts.analyst_overlay_from_trade_log import (
        compute_portfolio_summary_from_curve,
    )
    summary = compute_portfolio_summary_from_curve(pd.DataFrame(), 10_000)
    assert summary["total_return_pct"] == 0.0
    assert summary["n_trades_closed"] == 0


# ---------------------------------------------------------------------------
# Strategy-regime matrix
# ---------------------------------------------------------------------------

def test_batch499_strategy_regime_matrix_basic():
    from scripts.analyst_overlay_from_trade_log import compute_strategy_regime_matrix
    rows = [
        ("AAPL", "2024-01-02", "2024-01-05", "long", "s1", "bull",    1, 1.0, 100, 3),
        ("MSFT", "2024-01-03", "2024-01-08", "long", "s1", "bull",    1, 1.0, 100, 5),
        ("GOOG", "2024-01-04", "2024-01-09", "long", "s1", "bear",    0, -1.0, -100, 5),
        ("AMZN", "2024-01-05", "2024-01-10", "long", "s2", "bull",    0, -1.0, -100, 5),
    ]
    matrix = compute_strategy_regime_matrix(_make_trade_log(rows))
    assert "s1" in matrix
    assert "s2" in matrix
    # s1 in bull: 2 wins / 2 trades -> wr=1.0
    assert matrix["s1"]["bull"]["wr"] == pytest.approx(1.0, abs=1e-4)
    assert matrix["s1"]["bull"]["n_trades"] == 2
    # s1 in bear: 1 trade, 0 wins -> wr=0.0
    assert matrix["s1"]["bear"]["wr"] == pytest.approx(0.0, abs=1e-4)


def test_batch499_strategy_regime_matrix_empty():
    from scripts.analyst_overlay_from_trade_log import compute_strategy_regime_matrix
    assert compute_strategy_regime_matrix(pd.DataFrame()) == {}


def test_batch499_strategy_regime_matrix_handles_missing_regime():
    from scripts.analyst_overlay_from_trade_log import compute_strategy_regime_matrix
    rows = [
        ("AAPL", "2024-01-02", "2024-01-05", "long", "s1", None, 1, 1.0, 100, 3),
    ]
    matrix = compute_strategy_regime_matrix(_make_trade_log(rows))
    # NaN regime collapsed to 'unknown'
    assert "s1" in matrix
    assert "unknown" in matrix["s1"]


# ---------------------------------------------------------------------------
# emit_overlay end-to-end
# ---------------------------------------------------------------------------

def test_batch499_emit_overlay_writes_three_files(tmp_path):
    from scripts.analyst_overlay_from_trade_log import emit_overlay
    rows = [
        ("AAPL", "2024-01-02", "2024-01-05", "long", "s1", "bull", 1, 1.0, 500, 3),
        ("MSFT", "2024-01-06", "2024-01-08", "long", "s1", "bull", 1, 1.0, 500, 2),
    ]
    log_path = tmp_path / "trade_log.csv"
    _make_trade_log(rows).to_csv(log_path, index=False)
    manifest = emit_overlay(log_path, tmp_path, starting_capital=10_000)
    assert manifest["equity_curve.parquet"] == "written"
    assert manifest["portfolio_metrics_overlay.json"] == "written"
    assert manifest["strategy_regime_matrix_overlay.json"] == "written"
    assert (tmp_path / "equity_curve.parquet").exists()
    assert (tmp_path / "portfolio_metrics_overlay.json").exists()
    assert (tmp_path / "strategy_regime_matrix_overlay.json").exists()
    # Parquet round-trips
    curve = pd.read_parquet(tmp_path / "equity_curve.parquet")
    assert len(curve) == 2


def test_batch499_emit_overlay_skips_existing_files(tmp_path):
    """By default, existing files are skipped (no overwrite)."""
    from scripts.analyst_overlay_from_trade_log import emit_overlay
    rows = [
        ("AAPL", "2024-01-02", "2024-01-05", "long", "s1", "bull", 1, 1.0, 500, 3),
    ]
    log_path = tmp_path / "trade_log.csv"
    _make_trade_log(rows).to_csv(log_path, index=False)
    (tmp_path / "equity_curve.parquet").write_bytes(b"sentinel")
    manifest = emit_overlay(log_path, tmp_path, starting_capital=10_000)
    assert manifest["equity_curve.parquet"] == "skipped_exists"
    # File contents preserved
    assert (tmp_path / "equity_curve.parquet").read_bytes() == b"sentinel"


def test_batch499_emit_overlay_overwrite_flag(tmp_path):
    """--overwrite forces re-emission."""
    from scripts.analyst_overlay_from_trade_log import emit_overlay
    rows = [
        ("AAPL", "2024-01-02", "2024-01-05", "long", "s1", "bull", 1, 1.0, 500, 3),
    ]
    log_path = tmp_path / "trade_log.csv"
    _make_trade_log(rows).to_csv(log_path, index=False)
    (tmp_path / "equity_curve.parquet").write_bytes(b"sentinel")
    manifest = emit_overlay(log_path, tmp_path, starting_capital=10_000,
                              overwrite=True)
    assert manifest["equity_curve.parquet"] == "written"
    # File contents replaced
    assert (tmp_path / "equity_curve.parquet").read_bytes() != b"sentinel"


def test_batch499_emit_overlay_raises_on_missing_trade_log(tmp_path):
    from scripts.analyst_overlay_from_trade_log import emit_overlay
    with pytest.raises(FileNotFoundError):
        emit_overlay(tmp_path / "nope.csv", tmp_path, 10_000)
