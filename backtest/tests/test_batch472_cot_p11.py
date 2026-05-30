"""Batch 472 (2026-05-29) -- P11 CFTC COT macro-positioning producer tests."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from backtest.signals.cot_positioning import (
    SERIES_FILE_MAP,
    _load_cot_series,
    compute_cot_series_signals,
    get_all_cot_signals,
)


def _make_cot_df(n_weeks: int, long_vals, short_vals, oi_vals,
                  start_date: date = date(2021, 1, 5)):
    dates = [start_date + timedelta(days=7 * i) for i in range(n_weeks)]
    return pd.DataFrame({
        "report_date_as_yyyy_mm_dd": [d.isoformat() for d in dates],
        "report_date": [pd.Timestamp(d) for d in dates],
        "prod_merc_positions_long":  long_vals,
        "prod_merc_positions_short": short_vals,
        "m_money_positions_long_all":  long_vals,
        "m_money_positions_short_all": short_vals,
        "open_interest_all":         oi_vals,
    })


def test_compute_cot_returns_empty_on_missing_file(tmp_path, monkeypatch):
    import backtest.signals.cot_positioning as cot
    monkeypatch.setattr(cot, "_COT_DIR", tmp_path)
    cot._load_cot_series.cache_clear()
    out = compute_cot_series_signals("sp500", date.today())
    assert out == {}


def test_compute_cot_emits_commercials_keys_with_history(tmp_path, monkeypatch):
    import backtest.signals.cot_positioning as cot
    monkeypatch.setattr(cot, "_COT_DIR", tmp_path)
    cot._load_cot_series.cache_clear()
    rng = np.random.RandomState(7)
    n = 200
    long_v = rng.randint(40_000, 60_000, n)
    short_v = rng.randint(40_000, 60_000, n)
    oi = rng.randint(150_000, 250_000, n)
    df = _make_cot_df(n, long_v, short_v, oi)
    df.to_parquet(tmp_path / SERIES_FILE_MAP["sp500"])
    out = compute_cot_series_signals("sp500", date(2024, 5, 1))
    assert "cot_sp500_commercials_net_pct" in out
    assert "cot_sp500_commercials_pctile_3y" in out
    assert 0.0 <= out["cot_sp500_commercials_pctile_3y"] <= 1.0


def test_compute_cot_pctile_is_high_when_recent_net_is_extreme(tmp_path, monkeypatch):
    import backtest.signals.cot_positioning as cot
    monkeypatch.setattr(cot, "_COT_DIR", tmp_path)
    cot._load_cot_series.cache_clear()
    n = 100
    # Baseline: roughly balanced
    long_v = [50_000] * 90 + [99_000] * 10  # last 10 are extremely long
    short_v = [50_000] * 100
    oi = [200_000] * 100
    df = _make_cot_df(n, long_v, short_v, oi)
    df.to_parquet(tmp_path / SERIES_FILE_MAP["ndx"])
    out = compute_cot_series_signals("ndx", date(2024, 5, 1))
    assert out["cot_ndx_commercials_pctile_3y"] > 0.9, \
        f"Expected high percentile on net-long extreme; got {out}"


def test_compute_cot_returns_empty_when_series_unknown():
    out = compute_cot_series_signals("NONEXISTENT", date.today())
    assert out == {}


def test_get_all_cot_signals_merges_multiple_series(tmp_path, monkeypatch):
    import backtest.signals.cot_positioning as cot
    monkeypatch.setattr(cot, "_COT_DIR", tmp_path)
    cot._load_cot_series.cache_clear()
    rng = np.random.RandomState(0)
    n = 200
    for series, fname in [("sp500", SERIES_FILE_MAP["sp500"]),
                           ("ndx",   SERIES_FILE_MAP["ndx"])]:
        long_v = rng.randint(40_000, 60_000, n)
        short_v = rng.randint(40_000, 60_000, n)
        oi = rng.randint(150_000, 250_000, n)
        _make_cot_df(n, long_v, short_v, oi).to_parquet(tmp_path / fname)
    out = get_all_cot_signals(date(2024, 5, 1))
    # Both sp500 and ndx commercial keys must appear
    assert "cot_sp500_commercials_net_pct" in out
    assert "cot_ndx_commercials_net_pct" in out


def test_compute_cot_handles_financial_format_columns(tmp_path, monkeypatch):
    """dxy_dollar_idx + emini files use dealer_*/lev_money_* column names.
    The resolver should map them to the same output keys."""
    import backtest.signals.cot_positioning as cot
    monkeypatch.setattr(cot, "_COT_DIR", tmp_path)
    cot._load_cot_series.cache_clear()
    n = 100
    dates = [date(2021, 1, 5) + timedelta(days=7 * i) for i in range(n)]
    df = pd.DataFrame({
        "report_date_as_yyyy_mm_dd": [d.isoformat() for d in dates],
        "report_date": [pd.Timestamp(d) for d in dates],
        "dealer_positions_long_all":  [30_000] * n,
        "dealer_positions_short_all": [20_000] * n,
        "lev_money_positions_long":  [10_000] * n,
        "lev_money_positions_short": [15_000] * n,
        "open_interest_all":         [100_000] * n,
    })
    df.to_parquet(tmp_path / SERIES_FILE_MAP["dxy"])
    out = compute_cot_series_signals("dxy", date(2024, 5, 1))
    assert "cot_dxy_commercials_net_pct" in out
    assert out["cot_dxy_commercials_net_pct"] == pytest.approx(0.1, abs=0.001)
    assert "cot_dxy_mmoney_pctile_3y" in out
