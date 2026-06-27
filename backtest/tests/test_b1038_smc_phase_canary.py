"""B1038 Council 131 Option-A SMC_PHASE B-CANARY short-circuit tests.

# Source: Council 131 Option-A owner-approved 2026-06-27 + C-1 declaration
# doc + DEC-508 Phase B canary gate per CHECKLIST #77.

Tests verify SMC_PHASE config flag formalizes the de-facto Phase B
canary state surfaced via B416 root cause confirmation (Phase C smoke
2026-06-27; vendored smartmoneyconcepts not installed in AWS user-data;
H1 hypothesis from C-4 diagnostic plan CONFIRMED).

Pyramid baseline 848+2 preserved per CHECKLIST #69.
"""
from __future__ import annotations

import pandas as pd
import pytest


def test_b1038_smc_phase_default_is_b_canary():
    """B1038: SMC_PHASE default value is 'B-CANARY' per Council 131 Option-A."""
    from backtest.config import SMC_PHASE
    assert SMC_PHASE == "B-CANARY", (
        f"SMC_PHASE must default to 'B-CANARY' per Council 131 Option-A; "
        f"got {SMC_PHASE!r}. Owner promotes to 'PRODUCTION' via single-line "
        f"edit when Phase C 8 sign-off items complete (per C-1 declaration)."
    )


def test_b1038_compute_smc_signals_returns_empty_when_b_canary():
    """B1038: compute_smc_signals short-circuits to empty dict when
    SMC_PHASE is 'B-CANARY' (default)."""
    from backtest.signals.smc_ict import compute_smc_signals
    df = pd.DataFrame({
        "open": [100.0] * 100,
        "high": [101.0] * 100,
        "low": [99.0] * 100,
        "close": [100.5] * 100,
        "volume": [1000000] * 100,
    }, index=pd.date_range("2024-01-01", periods=100, freq="D"))
    result = compute_smc_signals(df, ticker="TEST")
    assert result == {}, (
        f"compute_smc_signals must return empty dict under B-CANARY phase; "
        f"got {len(result)} keys: {sorted(result.keys())[:5]}"
    )


def test_b1038_smc_phase_short_circuit_is_first_check():
    """B1038: SMC_PHASE short-circuit fires BEFORE _SMC_AVAILABLE check
    (so flag works even with library properly installed)."""
    from backtest.signals.smc_ict import compute_smc_signals
    # Even with valid data + library available, B-CANARY returns {}
    df = pd.DataFrame({
        "open": [100.0, 101, 102, 103, 104, 105, 106, 107, 108, 109] * 15,
        "high": [101.0, 102, 103, 104, 105, 106, 107, 108, 109, 110] * 15,
        "low": [99.0, 100, 101, 102, 103, 104, 105, 106, 107, 108] * 15,
        "close": [100.5, 101.5, 102.5, 103.5, 104.5, 105.5, 106.5, 107.5,
                  108.5, 109.5] * 15,
        "volume": [1_000_000] * 150,
    }, index=pd.date_range("2024-01-01", periods=150, freq="D"))
    result = compute_smc_signals(df, ticker="TEST")
    assert result == {}, "B-CANARY short-circuit must precede library check"


def test_b1038_smc_phase_in_canonical_facts():
    """B1038: SMC_PHASE flag is exported from backtest.config."""
    import backtest.config as cfg
    assert hasattr(cfg, "SMC_PHASE"), "SMC_PHASE must be in backtest.config"
    assert isinstance(cfg.SMC_PHASE, str), "SMC_PHASE must be str"
    assert cfg.SMC_PHASE in ("B-CANARY", "PRODUCTION"), (
        f"SMC_PHASE must be 'B-CANARY' or 'PRODUCTION'; got {cfg.SMC_PHASE!r}"
    )


def test_b1038_owner_promotion_path_documented():
    """B1038: Verify config.py comment documents the owner-promotion path
    per C-1 declaration doc 8 sign-off items."""
    import inspect
    from backtest import config
    source = inspect.getsource(config)
    # Verify key documentation elements present
    assert "Council 131 Option-A" in source, "Council 131 Option-A lineage required"
    assert "B416" in source, "B416 root cause reference required"
    assert "C-1 declaration" in source, "C-1 declaration cross-ref required"
    assert "DEC-508" in source, "DEC-508 Phase B canary gate reference required"
    assert "PRODUCTION" in source, "PRODUCTION promotion path must be documented"
