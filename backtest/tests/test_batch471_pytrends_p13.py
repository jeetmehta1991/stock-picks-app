"""Batch 471 (2026-05-29) -- P13 pytrends search-volume producer tests.

Tests for backtest/signals/search_volume.py:
  1. Empty when ticker file missing.
  2. Empty when file empty.
  3. Returns recent index + observations on short history (<30 weeks).
  4. Returns full signal dict (recent + zscore + observations) on long history.
  5. Z-score is positive when recent 4 weeks > trailing 26-week baseline.
  6. Z-score is negative on a flat-to-declining series.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def _make_pytrends_df(start_date: date, n_weeks: int, values):
    dates = [start_date + timedelta(days=7 * i) for i in range(n_weeks)]
    return pd.DataFrame({
        "ticker": ["TEST"] * n_weeks,
        "date": [pd.Timestamp(d) for d in dates],
        "search_volume_index": values,
        "query_label": ["TEST stock"] * n_weeks,
    })


def test_empty_on_missing_file(tmp_path, monkeypatch):
    import backtest.signals.search_volume as sv
    monkeypatch.setattr(sv, "_PYTRENDS_DIR", tmp_path)
    out = sv.compute_search_volume_signals("NOEXIST", date.today())
    assert out == {}


def test_empty_on_empty_file(tmp_path, monkeypatch):
    import backtest.signals.search_volume as sv
    monkeypatch.setattr(sv, "_PYTRENDS_DIR", tmp_path)
    pd.DataFrame({"ticker": [], "date": [], "search_volume_index": [],
                  "query_label": []}).to_parquet(tmp_path / "EMP.parquet")
    out = sv.compute_search_volume_signals("EMP", date.today())
    assert out == {}


def test_recent_index_on_short_history(tmp_path, monkeypatch):
    import backtest.signals.search_volume as sv
    monkeypatch.setattr(sv, "_PYTRENDS_DIR", tmp_path)
    df = _make_pytrends_df(date(2024, 1, 7), 10,
                            [50] * 9 + [80])
    df.to_parquet(tmp_path / "SHRT.parquet")
    out = sv.compute_search_volume_signals("SHRT", date(2024, 5, 1))
    assert out["search_volume_index_recent"] == 80
    assert out["search_volume_observations"] == 10
    assert "search_volume_zscore_30d" not in out  # too few observations


def test_full_signal_on_long_history(tmp_path, monkeypatch):
    import backtest.signals.search_volume as sv
    monkeypatch.setattr(sv, "_PYTRENDS_DIR", tmp_path)
    rng = np.random.RandomState(13)
    # 50 weeks: baseline ~50 with realistic variability, recent spike to ~80.
    baseline = list(rng.normal(50, 5, 46))
    recent = [80, 82, 78, 85]
    values = baseline + recent
    df = _make_pytrends_df(date(2023, 1, 7), len(values), values)
    df.to_parquet(tmp_path / "LONG.parquet")
    out = sv.compute_search_volume_signals("LONG", date(2024, 5, 1))
    assert "search_volume_zscore_30d" in out
    assert out["search_volume_zscore_30d"] > 0
    assert out["search_volume_observations"] == 50
    assert out["search_volume_index_recent"] == 85


def test_zscore_negative_when_recent_below_baseline(tmp_path, monkeypatch):
    import backtest.signals.search_volume as sv
    monkeypatch.setattr(sv, "_PYTRENDS_DIR", tmp_path)
    rng = np.random.RandomState(7)
    baseline = list(rng.normal(70, 5, 26))  # baseline around 70
    recent = [40, 42, 38, 35]               # recent low
    values = baseline + recent
    df = _make_pytrends_df(date(2023, 6, 4), len(values), values)
    df.to_parquet(tmp_path / "DROP.parquet")
    out = sv.compute_search_volume_signals("DROP", date(2024, 5, 1))
    assert out["search_volume_zscore_30d"] < -1
    assert out["search_volume_index_recent"] == 35


def test_zscore_zero_on_flat_baseline_with_no_std(tmp_path, monkeypatch):
    import backtest.signals.search_volume as sv
    monkeypatch.setattr(sv, "_PYTRENDS_DIR", tmp_path)
    # All identical values -> std=0 -> zscore returns 0.0 (defined)
    values = [50.0] * 35
    df = _make_pytrends_df(date(2023, 6, 4), len(values), values)
    df.to_parquet(tmp_path / "FLAT.parquet")
    out = sv.compute_search_volume_signals("FLAT", date(2024, 5, 1))
    assert out["search_volume_zscore_30d"] == 0.0
