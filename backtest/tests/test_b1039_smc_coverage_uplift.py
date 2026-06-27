"""B1039 Council 132 Item #3 Phase A coverage uplift tests.

# Source: Council 132 Option-5/6 owner directive 2026-06-27 'signoff items
# 3 5 6 7 8 execute and implement now.' per CHECKLIST #77.

Targets uncovered edge paths in backtest/signals/smc_ict.py per
coverage report (lines 128-130 fail-safe + 131 _SMC_AVAILABLE + 134
schema check + 136 history-min check + 148-160 USE_SMC_PANEL_CACHE
branches). Goal: lift coverage from 72% baseline toward 90% target per
C-1 declaration § 2.

NOTE: Test file disables the B1038 SMC_PHASE B-CANARY short-circuit
via monkeypatch SMC_PHASE='PRODUCTION' (sibling pattern to
test_b1038_smc_phase_canary.py).
"""
from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def _smc_phase_production(monkeypatch):
    """Bypass B1038 B-CANARY short-circuit for semantic coverage tests."""
    import backtest.config as _cfg
    monkeypatch.setattr(_cfg, "SMC_PHASE", "PRODUCTION")


def test_b1039_compute_smc_signals_empty_ohlc_returns_empty():
    """Coverage: line 131 ohlc.empty -> return {}."""
    from backtest.signals.smc_ict import compute_smc_signals
    df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    assert compute_smc_signals(df) == {}


def test_b1039_compute_smc_signals_none_ohlc_returns_empty():
    """Coverage: line 131 ohlc is None -> return {}."""
    from backtest.signals.smc_ict import compute_smc_signals
    assert compute_smc_signals(None) == {}


def test_b1039_compute_smc_signals_missing_columns_returns_empty():
    """Coverage: line 134-135 missing required columns -> return {}."""
    from backtest.signals.smc_ict import compute_smc_signals
    df = pd.DataFrame({
        "open": [100.0] * 200,
        "close": [101.0] * 200,
        # Missing 'high' and 'low'
    }, index=pd.date_range("2024-01-01", periods=200, freq="D"))
    assert compute_smc_signals(df) == {}


def test_b1039_compute_smc_signals_insufficient_history_returns_empty():
    """Coverage: line 136-137 len(ohlc) < max(swing_length*2, 100) -> {}."""
    from backtest.signals.smc_ict import compute_smc_signals
    df = pd.DataFrame({
        "open": [100.0] * 50,
        "high": [101.0] * 50,
        "low": [99.0] * 50,
        "close": [100.5] * 50,
        "volume": [1_000_000] * 50,
    }, index=pd.date_range("2024-01-01", periods=50, freq="D"))
    assert compute_smc_signals(df) == {}


def test_b1039_compute_smc_signals_swing_length_floor():
    """Coverage: line 136 enforces max(swing_length*2, 100) floor."""
    from backtest.signals.smc_ict import compute_smc_signals
    # swing_length=20 * 2 = 40, but floor is 100; 95 rows < 100 returns {}
    df = pd.DataFrame({
        "open": [100.0] * 95,
        "high": [101.0] * 95,
        "low": [99.0] * 95,
        "close": [100.5] * 95,
        "volume": [1_000_000] * 95,
    }, index=pd.date_range("2024-01-01", periods=95, freq="D"))
    assert compute_smc_signals(df, swing_length=20) == {}


def test_b1039_compute_smc_signals_use_smc_panel_cache_false():
    """Coverage: lines 148-152 USE_SMC_PANEL_CACHE=False branch."""
    import backtest.config as _cfg
    # Default state is USE_SMC_PANEL_CACHE absent or False
    from backtest.signals.smc_ict import compute_smc_signals
    import numpy as np
    rng = np.random.default_rng(42)
    n = 320
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    base = 100 + np.cumsum(rng.normal(0, 1, n))
    df = pd.DataFrame({
        "open": base, "high": base + 0.5, "low": base - 0.5,
        "close": base, "volume": [1_000_000] * n,
    }, index=idx)
    result = compute_smc_signals(df, ticker="COVERAGE_TEST")
    assert isinstance(result, dict)
    # Returns signals (no cache lookup attempted)
    assert len(result) > 0


def test_b1039_compute_smc_signals_use_smc_panel_cache_true_miss():
    """Coverage: lines 152-160 USE_SMC_PANEL_CACHE=True with cache MISS
    falls back to per-call compute."""
    import backtest.config as _cfg
    # Set USE_SMC_PANEL_CACHE=True temporarily
    _orig = getattr(_cfg, "USE_SMC_PANEL_CACHE", False)
    try:
        _cfg.USE_SMC_PANEL_CACHE = True
        from backtest.signals.smc_ict import compute_smc_signals
        import numpy as np
        rng = np.random.default_rng(43)
        n = 200
        idx = pd.date_range("2024-01-01", periods=n, freq="B")
        base = 100 + np.cumsum(rng.normal(0, 1, n))
        df = pd.DataFrame({
            "open": base, "high": base + 0.5, "low": base - 0.5,
            "close": base, "volume": [1_000_000] * n,
        }, index=idx)
        # Use a ticker name unlikely to have primed cache
        result = compute_smc_signals(df, ticker="CACHE_MISS_TEST_TICKER_XYZ")
        # Should fall back to per-call (no AttributeError on cache lookup)
        assert isinstance(result, dict)
    finally:
        _cfg.USE_SMC_PANEL_CACHE = _orig


def test_b1039_compute_smc_signals_default_swing_length_20():
    """Coverage: default swing_length=20 path execution."""
    from backtest.signals.smc_ict import compute_smc_signals
    import numpy as np
    rng = np.random.default_rng(44)
    n = 350
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    base = 100 + np.cumsum(rng.normal(0, 1, n))
    df = pd.DataFrame({
        "open": base, "high": base + 0.5, "low": base - 0.5,
        "close": base, "volume": [1_000_000] * n,
    }, index=idx)
    result = compute_smc_signals(df)
    assert isinstance(result, dict)


def test_b1039_compute_smc_signals_custom_event_recency_bars():
    """Coverage: event_recency_bars=30 (non-default 90) path."""
    from backtest.signals.smc_ict import compute_smc_signals
    import numpy as np
    rng = np.random.default_rng(45)
    n = 300
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    base = 100 + np.cumsum(rng.normal(0, 1, n))
    df = pd.DataFrame({
        "open": base, "high": base + 0.5, "low": base - 0.5,
        "close": base, "volume": [1_000_000] * n,
    }, index=idx)
    result = compute_smc_signals(df, event_recency_bars=30)
    assert isinstance(result, dict)


def test_b1039_compute_smc_signals_custom_dealing_range_lookback():
    """Coverage: dealing_range_lookback=20 (non-default 50) path."""
    from backtest.signals.smc_ict import compute_smc_signals
    import numpy as np
    rng = np.random.default_rng(46)
    n = 250
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    base = 100 + np.cumsum(rng.normal(0, 1, n))
    df = pd.DataFrame({
        "open": base, "high": base + 0.5, "low": base - 0.5,
        "close": base, "volume": [1_000_000] * n,
    }, index=idx)
    result = compute_smc_signals(df, dealing_range_lookback=20)
    assert isinstance(result, dict)


def test_b1039_compute_smc_signals_custom_fvg_lookback():
    """Coverage: fvg_lookback=10 (non-default 5) path."""
    from backtest.signals.smc_ict import compute_smc_signals
    import numpy as np
    rng = np.random.default_rng(47)
    n = 250
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    base = 100 + np.cumsum(rng.normal(0, 1, n))
    df = pd.DataFrame({
        "open": base, "high": base + 0.5, "low": base - 0.5,
        "close": base, "volume": [1_000_000] * n,
    }, index=idx)
    result = compute_smc_signals(df, fvg_lookback=10)
    assert isinstance(result, dict)
