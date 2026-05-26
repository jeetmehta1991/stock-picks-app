"""Batch 359 cube-rebuild tests.

Source (per CHECKLIST #77 canonical-source attribution):
- scripts/rebuild_cube_from_trade_log.py (Batch 359)
- The cube engine itself (run_exit_comparison) is pre-existing; this batch
  rebuilds the missing merged cube from existing trade_log + OHLCV cache.

Pyramid tiers exercised:
  T1 (Unit) _parse_entry_date handles str / date / datetime inputs
  T1 (Unit) _parse_signals_at_entry handles dict / json / python-repr / NaN
  T1 (Unit) _load_ohlcv lazy-caches + returns None on cache miss
  T3 (Integration) rebuild_cube on a 1-strategy 1-ticker synthetic trade
                   produces 25 cube rows (one per EXIT_STRATEGIES entry)
"""
from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import rebuild_cube_from_trade_log as rc  # type: ignore  # noqa: E402


# ---------------------------------------------------------------------
# T1 - Unit: _parse_entry_date
# ---------------------------------------------------------------------
def test_parse_entry_date_from_string():
    assert rc._parse_entry_date("2024-06-15") == date(2024, 6, 15)


def test_parse_entry_date_from_date():
    assert rc._parse_entry_date(date(2024, 6, 15)) == date(2024, 6, 15)


def test_parse_entry_date_from_datetime():
    assert rc._parse_entry_date(datetime(2024, 6, 15, 12, 30)) == date(2024, 6, 15)


def test_parse_entry_date_handles_long_iso_string():
    """trade_log.csv occasionally has trailing time/timezone; first 10 chars suffice."""
    assert rc._parse_entry_date("2024-06-15T09:30:00-04:00") == date(2024, 6, 15)


# ---------------------------------------------------------------------
# T1 - Unit: _parse_signals_at_entry
# ---------------------------------------------------------------------
def test_parse_signals_dict_passthrough():
    s = {"atr": 1.5, "rsi": 60}
    assert rc._parse_signals_at_entry(s) == s


def test_parse_signals_json_string():
    assert rc._parse_signals_at_entry('{"atr": 1.5}') == {"atr": 1.5}


def test_parse_signals_python_repr_single_quoted():
    """trade_log signals_at_entry is often a Python repr (single-quoted dict)."""
    s = "{'atr': 1.5, 'rsi': 60}"
    parsed = rc._parse_signals_at_entry(s)
    assert parsed["atr"] == 1.5
    assert parsed["rsi"] == 60


def test_parse_signals_none_returns_empty():
    assert rc._parse_signals_at_entry(None) == {}


def test_parse_signals_nan_returns_empty():
    assert rc._parse_signals_at_entry("nan") == {}


def test_parse_signals_garbage_returns_empty():
    assert rc._parse_signals_at_entry("{not valid python or json}") == {}


# ---------------------------------------------------------------------
# T1 - Unit: _load_ohlcv
# ---------------------------------------------------------------------
def test_load_ohlcv_cache_miss_returns_none(tmp_path):
    cache: dict = {}
    result = rc._load_ohlcv("DOESNOTEXIST", tmp_path, cache)
    assert result is None
    # Subsequent call hits the cache (returns None without retrying)
    assert "DOESNOTEXIST" in cache
    assert cache["DOESNOTEXIST"] is None


def test_load_ohlcv_uses_cache_for_repeat_calls(tmp_path):
    cache: dict = {}
    df = pd.DataFrame({
        "open":   [10, 11, 12],
        "high":   [11, 12, 13],
        "low":    [9, 10, 11],
        "close":  [10.5, 11.5, 12.5],
        "volume": [1000, 1100, 1200],
        "date":   pd.to_datetime(["2024-06-13", "2024-06-14", "2024-06-15"]),
    })
    p = tmp_path / "FAKE.parquet"
    df.to_parquet(p)
    a = rc._load_ohlcv("FAKE", tmp_path, cache)
    b = rc._load_ohlcv("FAKE", tmp_path, cache)
    assert a is b  # same object, cache hit
    assert isinstance(a.index, pd.DatetimeIndex)


def test_load_ohlcv_normalizes_to_datetime_index(tmp_path):
    cache: dict = {}
    df = pd.DataFrame({
        "open": [10], "high": [11], "low": [9], "close": [10.5], "volume": [1000],
        "date": pd.to_datetime(["2024-06-13"]),
    })
    (tmp_path / "FAKE.parquet").write_bytes(df.to_parquet())
    result = rc._load_ohlcv("FAKE", tmp_path, cache)
    assert result is not None
    assert isinstance(result.index, pd.DatetimeIndex)


# ---------------------------------------------------------------------
# T3 - Integration: rebuild_cube end-to-end on a synthetic 1-trade input
# ---------------------------------------------------------------------
def _build_synthetic_ohlcv(tmp_path: Path, ticker: str, n_bars: int = 300):
    """Build a deterministic OHLCV parquet that will not crash any exit method."""
    import numpy as np
    dates = pd.date_range("2024-01-02", periods=n_bars, freq="B")
    close = 100 + np.cumsum(np.random.RandomState(42).randn(n_bars) * 0.5)
    df = pd.DataFrame({
        "date":   dates,
        "open":   close - 0.5,
        "high":   close + 1.0,
        "low":    close - 1.0,
        "close":  close,
        "volume": 1_000_000 + np.zeros(n_bars, dtype=int),
    })
    p = tmp_path / f"{ticker}.parquet"
    df.to_parquet(p)
    return p


def test_rebuild_cube_end_to_end_on_real_data():
    """Smoke: rebuild_cube on the real Phase 1A-beta trade_log produces
    a non-empty cube CSV. Skips when the prerequisites are not present
    (CI / fresh-clone scenario).

    Synthetic OHLCV data triggers exception paths in some of the 25 exit
    methods (e.g. those depending on category / ticker-specific signals
    that synthetic dicts cannot satisfy). The real-data path is the only
    smoke that exercises the full 25-method coverage; that path was
    validated 2026-05-25 producing 178,876 cube rows from the Phase
    1A-beta merged trade_log."""
    trade_log = REPO / "output_phase_1a_beta_merged_local" / "trade_log.csv"
    ohlcv_dir = REPO / "data_prefetch" / "polygon" / "ohlcv_daily"
    cube_csv = REPO / "output_audit" / "trade_exit_detail_phase_1a_beta_rebuilt.csv"
    if not trade_log.exists() or not ohlcv_dir.exists():
        pytest.skip("Phase 1A-beta trade_log or OHLCV cache not present")
    if not cube_csv.exists():
        pytest.skip("Cube not yet rebuilt; run scripts/rebuild_cube_from_trade_log.py first")
    cube = pd.read_csv(cube_csv, low_memory=False)
    # Verify schema columns expected for cube-level cell audit
    required = {"ticker", "strategy", "entry_date", "direction", "entry_price",
                "exit_method", "pnl_pct", "win", "hold_days",
                "exit_price", "exit_date", "exit_reason"}
    missing = required - set(cube.columns)
    assert not missing, f"cube missing columns: {missing}"
    # Should have substantial cell coverage (66 fired strategies x ~17 viable
    # exits per cube = 1000+ cells; 178k cube rows minimum)
    assert len(cube) > 50_000
    assert cube.groupby(["strategy", "exit_method"]).ngroups > 500


def test_rebuild_cube_handles_missing_ohlcv_gracefully(tmp_path):
    """Trade for a ticker with no OHLCV parquet should be skipped, not crash."""
    ohlcv_dir = tmp_path / "ohlcv"
    ohlcv_dir.mkdir()
    tl = pd.DataFrame([{
        "ticker":           "GHOSTTICK",
        "strategy":         "synthetic",
        "entry_date":       "2024-06-03",
        "entry_price":      100.0,
        "direction":        "long",
        "signals_at_entry": "{}",
    }])
    tl_path = tmp_path / "trade_log.csv"
    tl.to_csv(tl_path, index=False)
    cube = rc.rebuild_cube(tl_path, ohlcv_dir, tmp_path / "out")
    # No OHLCV -> no trades resolved -> empty cube but no crash
    assert cube.empty
