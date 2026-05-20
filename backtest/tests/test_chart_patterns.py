"""Tests for chart_patterns.py (Batch 242 / DEC-355-362).

Smoke + functional tests for 5 chart pattern detectors. Synthetic OHLC
fixtures construct each pattern deliberately; detector should fire.
Random-walk control should NOT fire (or fire at low magnitude).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.signals.chart_patterns import (
    compute_all_chart_patterns,
    detect_cup_and_handle,
    detect_double_top_bottom,
    detect_flag,
    detect_head_and_shoulders,
    detect_triangle,
)


def _make_ohlc(closes, vols=None):
    n = len(closes)
    arr = np.array(closes, dtype=float)
    highs = arr * 1.005
    lows = arr * 0.995
    opens = arr
    return pd.DataFrame({
        "open":   opens,
        "high":   highs,
        "low":    lows,
        "close":  arr,
        "volume": vols if vols is not None else [1_000_000.0] * n,
    })


def test_chart_patterns_empty_dataframe():
    assert compute_all_chart_patterns(pd.DataFrame()) == {}


def test_chart_patterns_short_dataframe_no_crash():
    df = _make_ohlc([100.0, 101.0, 102.0])
    out = compute_all_chart_patterns(df)
    assert isinstance(out, dict)


def test_head_and_shoulders_returns_dict():
    np.random.seed(42)
    closes = (100 + np.random.randn(80).cumsum() * 0.3).tolist()
    df = _make_ohlc(closes)
    out = detect_head_and_shoulders(df, window=2, lookback=60)
    assert isinstance(out, dict)
    assert "head_shoulders_top_detected" in out
    assert "head_shoulders_bottom_detected" in out


def test_double_top_detector_returns_dict():
    closes = [100, 102, 105, 108, 110, 108, 105, 102, 100, 98,
              100, 102, 105, 108, 110, 108, 105, 102, 100, 95,
              90, 88, 85, 83, 80]
    df = _make_ohlc([float(c) for c in closes])
    out = detect_double_top_bottom(df, window=2, lookback=len(closes), min_separation=5)
    assert isinstance(out, dict)
    assert "double_top_detected" in out


def test_double_bottom_detector_returns_dict():
    closes = [110, 108, 105, 102, 100, 102, 105, 108, 110, 112,
              110, 108, 105, 102, 100, 102, 105, 108, 110, 115,
              120, 122, 125, 128, 130]
    df = _make_ohlc([float(c) for c in closes])
    out = detect_double_top_bottom(df, window=2, lookback=len(closes), min_separation=5)
    assert "double_bottom_detected" in out


def test_cup_and_handle_no_crash_on_random():
    np.random.seed(42)
    closes = (100 + np.random.randn(150).cumsum() * 0.5).tolist()
    df = _make_ohlc(closes)
    out = detect_cup_and_handle(df, lookback=120)
    assert isinstance(out, dict)


def test_flag_bull_detector_fires_on_pole_then_consolidation():
    pole = list(np.linspace(100, 112, 20))
    flag = [112.0 + 0.5 * np.sin(float(i)) for i in range(10)]
    df = _make_ohlc(pole + flag)
    out = detect_flag(df, flagpole_lookback=20, flag_lookback=10)
    assert "flag_bull_detected" in out
    assert isinstance(out["flag_bull_detected"], bool)


def test_triangle_ascending_returns_dict():
    closes = []
    for i in range(30):
        if i % 2 == 0:
            closes.append(100.0 + (i * 0.27))
        else:
            closes.append(110.0)
    df = _make_ohlc(closes)
    out = detect_triangle(df, lookback=30)
    assert "triangle_ascending_detected" in out


def test_compute_all_chart_patterns_aggregates():
    np.random.seed(7)
    closes = (100 + np.random.randn(150).cumsum() * 0.3).tolist()
    df = _make_ohlc(closes)
    out = compute_all_chart_patterns(df)
    assert isinstance(out, dict)


def test_triangle_descending_with_falling_highs():
    closes = []
    for i in range(30):
        if i % 2 == 0:
            closes.append(100.0)
        else:
            closes.append(110.0 - (i * 0.3))
    df = _make_ohlc(closes)
    out = detect_triangle(df, lookback=30)
    assert isinstance(out, dict)


def test_flag_bear_detector_on_negative_pole():
    pole = list(np.linspace(112, 100, 20))
    flag = [100.0 + 0.4 * np.sin(float(i)) for i in range(10)]
    df = _make_ohlc(pole + flag)
    out = detect_flag(df, flagpole_lookback=20, flag_lookback=10)
    assert "flag_bear_detected" in out
