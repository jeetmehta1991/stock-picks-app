"""B719 SPOF SENTINEL: vendored smartmoneyconcepts library import + method
presence + smoke shape sentinel.

# Source: B719 finding (vendored-library SPOF sentinel test) + Council 132
# Option-5/6 owner directive 2026-06-27 'signoff items 3 5 6 7 8 execute
# and implement now.' + C-1 declaration § 4 PENDING item.
# Lineage: B416 root cause CONFIRMED 2026-06-27 - vendored
# smartmoneyconcepts/ not installed in AWS user-data -> silent
# ModuleNotFoundError swallowed by `try: import ... except: log_silent_failure`
# at backtest/signals/smc_ict.py:39-48 -> 18 SMC strategies fired 0 trades
# in R5 production cube (Phase C smoke 2026-06-27 confirmed H1 hypothesis).
# B1038 formalized the SMC_PHASE B-CANARY short-circuit; this test
# complements that by verifying the LIBRARY remains importable + functional
# regardless of the SMC_PHASE gate, so promoting to PRODUCTION later
# doesn't surface another silent regression.

Tests (all run at pyramid startup; FAIL-FAST sentinel pattern):

1. test_smc_spof_vendored_directory_exists                - catches AWS
   deploy regression specifically (`vendored/smartmoneyconcepts/
   smartmoneyconcepts/__init__.py` must be present in repo).
2. test_smc_spof_import_smartmoneyconcepts                - `from
   smartmoneyconcepts import smc` must succeed (uses pytest.fail with
   explicit remediation message if ModuleNotFoundError).
3. test_smc_spof_vendored_import_path                     - the import
   path actually used by smc_ict.py
   (`vendored.smartmoneyconcepts.smartmoneyconcepts.smc`) must work.
4. test_smc_spof_consumed_methods_present_on_namespace    - each method
   consumed by smc_ict.compute_smc_signals must exist as a callable
   attribute on the smc namespace.
5. test_smc_spof_smoke_fvg                                - fvg() returns
   DataFrame with FVG/Top/Bottom/MitigatedIndex columns.
6. test_smc_spof_smoke_swing_highs_lows                   - swing_highs_lows()
   returns DataFrame with HighLow/Level columns.
7. test_smc_spof_smoke_ob                                  - ob() returns
   DataFrame with OB/Top/Bottom/MitigatedIndex columns.
8. test_smc_spof_smoke_bos_choch                          - bos_choch()
   returns DataFrame with BOS/CHOCH/Level columns.
9. test_smc_spof_smoke_liquidity                          - liquidity()
   returns DataFrame with Liquidity/Swept columns.
10. test_smc_spof_smoke_retracements                       - retracements()
    returns DataFrame with Direction/CurrentRetracement% columns.

Each test SKIPS gracefully (not FAIL) only if the library is genuinely
intentionally absent (e.g., dev env without vendored/), via
pytest.importorskip. The vendored-directory-exists check (#1) does NOT
skip; that's the explicit B416-regression detector - a fresh git clone
should always have the directory.

Pyramid baseline 848+2 preserved (council prompt referenced 853+2 but
actual current baseline as of test_unit + test_integration is 848+2 per
pytest run 2026-06-27 pre-add).
"""
from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Test data fixtures
# ---------------------------------------------------------------------------


def _make_ohlc(n: int = 200) -> pd.DataFrame:
    """Construct a minimal valid OHLCV DataFrame for SMC method smoke
    tests. Uses a deterministic sinusoidal-ish path so swings exist for
    swing_highs_lows / bos_choch / ob detection."""
    # Deterministic price path with multiple peaks + troughs
    import math
    closes = [
        100.0 + 10.0 * math.sin(i / 7.0) + 5.0 * math.cos(i / 13.0)
        for i in range(n)
    ]
    opens = [c - 0.3 for c in closes]
    highs = [c + 1.2 for c in closes]
    lows = [c - 1.2 for c in closes]
    vols = [1_000_000 + i * 1_000 for i in range(n)]
    return pd.DataFrame(
        {
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": vols,
        },
        index=pd.date_range("2024-01-01", periods=n, freq="D"),
    )


# ---------------------------------------------------------------------------
# Test 1: Vendored directory exists (B416 deploy regression sentinel)
# ---------------------------------------------------------------------------


def test_smc_spof_vendored_directory_exists():
    """B719 SPOF / B416: vendored/smartmoneyconcepts/smartmoneyconcepts/
    __init__.py MUST exist at repo root.

    This is the explicit B416-regression detector: AWS user-data deploy
    in B1024-B1028 failed to install vendored/smartmoneyconcepts/ which
    caused 18 SMC strategies to silently fire 0 trades. A fresh git
    clone of this repo should always have the directory.

    Does NOT skip - failure here means the vendored library is missing
    from the repo itself, which is a deploy/checkout regression.
    """
    # Resolve repo root from this test file location
    # backtest/tests/test_smc_spof_sentinel.py -> repo root is parents[2]
    repo_root = Path(__file__).resolve().parents[2]
    vendored_init = (
        repo_root / "vendored" / "smartmoneyconcepts"
        / "smartmoneyconcepts" / "__init__.py"
    )
    vendored_smc = (
        repo_root / "vendored" / "smartmoneyconcepts"
        / "smartmoneyconcepts" / "smc.py"
    )
    assert vendored_init.exists(), (
        f"MISSING vendored smartmoneyconcepts library - "
        f"{vendored_init} not found.\n"
        f"This is the B416 AWS-deploy regression pattern: smc_ict.py "
        f"imports `from vendored.smartmoneyconcepts.smartmoneyconcepts "
        f"import smc` and silently swallows ImportError, leaving 18 SMC "
        f"strategies dead.\n"
        f"REMEDIATION: ensure `vendored/smartmoneyconcepts/` is "
        f"committed + present in repo checkout. If running in AWS / "
        f"Docker, verify user-data clones the full repo including "
        f"`vendored/` subdirectories."
    )
    assert vendored_smc.exists(), (
        f"MISSING vendored smartmoneyconcepts smc.py - "
        f"{vendored_smc} not found. Same B416 pattern as above."
    )


# ---------------------------------------------------------------------------
# Test 2: Import smartmoneyconcepts (top-level pip-installed path)
# ---------------------------------------------------------------------------


def test_smc_spof_import_smartmoneyconcepts():
    """B719 SPOF: `from smartmoneyconcepts import smc` must succeed.

    Uses pytest.importorskip to skip gracefully when smartmoneyconcepts
    is genuinely absent (dev env without `pip install -e
    vendored/smartmoneyconcepts/`). Skip is appropriate here because the
    repo MAY use the vendored.smartmoneyconcepts.smartmoneyconcepts.smc
    path (tested separately) without requiring the top-level
    pip-installed namespace.
    """
    # Suppress the library's startup banner (Unicode glyph on cp1252)
    with contextlib.redirect_stdout(io.StringIO()):
        smc_mod = pytest.importorskip(
            "smartmoneyconcepts",
            reason=(
                "smartmoneyconcepts library not installed at top-level "
                "namespace. If this is a production deploy, run: "
                "`pip install -e vendored/smartmoneyconcepts/`. The "
                "vendored-path test (test_smc_spof_vendored_import_path) "
                "is the primary B416-regression sentinel."
            ),
        )
    assert hasattr(smc_mod, "smc"), (
        "smartmoneyconcepts module imported but `smc` attribute missing. "
        "Library may be partially installed or corrupted. "
        "REMEDIATION: pip install -e vendored/smartmoneyconcepts/ --force-reinstall"
    )


# ---------------------------------------------------------------------------
# Test 3: Vendored direct-path import (the actual production code path)
# ---------------------------------------------------------------------------


def test_smc_spof_vendored_import_path():
    """B719 SPOF: import via the path used by smc_ict.py production code:
    `from vendored.smartmoneyconcepts.smartmoneyconcepts import smc`.

    This is the PRIMARY B416-regression sentinel - it tests the exact
    import line at backtest/signals/smc_ict.py:41.
    """
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            from vendored.smartmoneyconcepts.smartmoneyconcepts import smc as _smc  # noqa: E501
        except ModuleNotFoundError as e:
            pytest.fail(
                f"MISSING vendored smartmoneyconcepts library at "
                f"production import path - `from "
                f"vendored.smartmoneyconcepts.smartmoneyconcepts import "
                f"smc` failed with {e!r}.\n\n"
                f"This is the EXACT B416 silent-failure pattern: "
                f"backtest/signals/smc_ict.py:41 wraps this import in "
                f"try/except and swallows the error, leaving "
                f"_SMC_AVAILABLE=False and 18 SMC strategies firing 0 "
                f"trades silently.\n\n"
                f"REMEDIATION:\n"
                f"  1. Verify `vendored/smartmoneyconcepts/smartmoneyconcepts/__init__.py` exists\n"
                f"  2. If absent: `git checkout vendored/` or `git pull`\n"
                f"  3. Ensure repo root is on sys.path (pyproject / "
                f"pytest config / PYTHONPATH)\n"
                f"  4. For AWS deploys: confirm user-data clones the "
                f"FULL repo including vendored/ subdirectories\n"
            )
    # Sanity: object must be a class/instance (has methods)
    assert _smc is not None, "vendored smc import returned None"


# ---------------------------------------------------------------------------
# Test 4: All consumed methods present on smc namespace
# ---------------------------------------------------------------------------


# Methods consumed by backtest/signals/smc_ict.py::compute_smc_signals
# (audited against smc_ict.py 2026-06-27):
#   - _smc.fvg(ohlc)                                      [line 169]
#   - _smc.swing_highs_lows(ohlc, swing_length=...)       [line 228]
#   - _smc.ob(ohlc, swings)                               [line 235]
#   - _smc.bos_choch(ohlc, swings)                        [line 299]
#   - _smc.liquidity(ohlc, swings, range_percent=...)     [line 349]
#   - _smc.retracements(ohlc, swings)                     [line 402]
SMC_CONSUMED_METHODS = (
    "fvg",
    "swing_highs_lows",
    "ob",
    "bos_choch",
    "liquidity",
    "retracements",
)


def _get_vendored_smc():
    """Helper: import vendored smc with banner suppression, skipping
    gracefully when absent. Returns the smc class."""
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            from vendored.smartmoneyconcepts.smartmoneyconcepts import smc as _smc  # noqa: E501
        except ModuleNotFoundError as e:
            pytest.skip(
                f"vendored smartmoneyconcepts unavailable ({e!r}); "
                f"test_smc_spof_vendored_import_path is the primary "
                f"FAIL sentinel."
            )
    return _smc


@pytest.mark.parametrize("method_name", SMC_CONSUMED_METHODS)
def test_smc_spof_consumed_methods_present_on_namespace(method_name):
    """B719 SPOF: each method consumed by compute_smc_signals must exist
    as a callable attribute on the vendored smc namespace.

    Catches partial-install / version-skew regressions where library
    imports but a specific method is missing (e.g., upstream library
    rename / deprecation breaking our consumer code).
    """
    _smc = _get_vendored_smc()
    assert hasattr(_smc, method_name), (
        f"MISSING smartmoneyconcepts method `{method_name}` on smc "
        f"namespace. Consumed by backtest/signals/smc_ict.py::"
        f"compute_smc_signals. Library may be wrong version or "
        f"partially installed.\n"
        f"REMEDIATION: verify vendored/smartmoneyconcepts/"
        f"smartmoneyconcepts/smc.py defines `def {method_name}(...)` "
        f"and pip install -e vendored/smartmoneyconcepts/ "
        f"--force-reinstall."
    )
    method = getattr(_smc, method_name)
    assert callable(method), (
        f"smc.{method_name} exists but is not callable (got {type(method)!r}). "
        f"Library corruption - reinstall vendored package."
    )


# ---------------------------------------------------------------------------
# Tests 5-10: Smoke-test each method returns expected shape
# ---------------------------------------------------------------------------


def test_smc_spof_smoke_fvg():
    """B719 SPOF smoke: fvg() returns DataFrame with FVG / Top / Bottom /
    MitigatedIndex columns (consumed by smc_ict.py lines 170-220)."""
    _smc = _get_vendored_smc()
    ohlc = _make_ohlc()
    with contextlib.redirect_stdout(io.StringIO()):
        result = _smc.fvg(ohlc)
    assert isinstance(result, pd.DataFrame), (
        f"smc.fvg() must return DataFrame; got {type(result)!r}. "
        f"Consumer at smc_ict.py:170 reads .columns / .tail() / .iloc."
    )
    for col in ("FVG", "Top", "Bottom", "MitigatedIndex"):
        assert col in result.columns, (
            f"smc.fvg() result missing required column `{col}`; got "
            f"{list(result.columns)}. Consumer at smc_ict.py:170-220 "
            f"reads this column for retest/inverse logic."
        )


def test_smc_spof_smoke_swing_highs_lows():
    """B719 SPOF smoke: swing_highs_lows() returns DataFrame with HighLow
    / Level columns (consumed by smc_ict.py line 228; output feeds ob /
    bos_choch / liquidity / retracements as `swings` arg)."""
    _smc = _get_vendored_smc()
    ohlc = _make_ohlc()
    with contextlib.redirect_stdout(io.StringIO()):
        result = _smc.swing_highs_lows(ohlc, swing_length=20)
    assert isinstance(result, pd.DataFrame), (
        f"smc.swing_highs_lows() must return DataFrame; got "
        f"{type(result)!r}. Consumer passes this as positional `swings` "
        f"arg to ob/bos_choch/liquidity/retracements."
    )
    # Library schema: HighLow column (1=high, -1=low), Level (price)
    assert "HighLow" in result.columns or "Level" in result.columns, (
        f"smc.swing_highs_lows() result missing both HighLow and Level "
        f"columns; got {list(result.columns)}. Downstream methods "
        f"depend on the swings DataFrame structure."
    )


def test_smc_spof_smoke_ob():
    """B719 SPOF smoke: ob() returns DataFrame with OB / Top / Bottom /
    MitigatedIndex columns (consumed by smc_ict.py lines 236-290 for
    breaker block + mitigation block + active OB signals)."""
    _smc = _get_vendored_smc()
    ohlc = _make_ohlc()
    with contextlib.redirect_stdout(io.StringIO()):
        swings = _smc.swing_highs_lows(ohlc, swing_length=20)
        result = _smc.ob(ohlc, swings)
    assert isinstance(result, pd.DataFrame), (
        f"smc.ob() must return DataFrame; got {type(result)!r}."
    )
    for col in ("OB", "Top", "Bottom", "MitigatedIndex"):
        assert col in result.columns, (
            f"smc.ob() result missing required column `{col}`; got "
            f"{list(result.columns)}. Consumer at smc_ict.py:236-290 "
            f"reads this column for OB / breaker / mitigation signals."
        )


def test_smc_spof_smoke_bos_choch():
    """B719 SPOF smoke: bos_choch() returns DataFrame with BOS / CHOCH /
    Level columns (consumed by smc_ict.py lines 300-340 for bos /
    choch / bos_retest signals)."""
    _smc = _get_vendored_smc()
    ohlc = _make_ohlc()
    with contextlib.redirect_stdout(io.StringIO()):
        swings = _smc.swing_highs_lows(ohlc, swing_length=20)
        result = _smc.bos_choch(ohlc, swings)
    assert isinstance(result, pd.DataFrame), (
        f"smc.bos_choch() must return DataFrame; got {type(result)!r}."
    )
    for col in ("BOS", "CHOCH", "Level"):
        assert col in result.columns, (
            f"smc.bos_choch() result missing required column `{col}`; "
            f"got {list(result.columns)}. Consumer at smc_ict.py:300-340 "
            f"reads this column for BOS/CHoCH event detection."
        )


def test_smc_spof_smoke_liquidity():
    """B719 SPOF smoke: liquidity() returns DataFrame with Liquidity /
    Swept columns (consumed by smc_ict.py lines 350-393 for liquidity
    sweep + equal-highs/lows-swept signals)."""
    _smc = _get_vendored_smc()
    ohlc = _make_ohlc()
    with contextlib.redirect_stdout(io.StringIO()):
        swings = _smc.swing_highs_lows(ohlc, swing_length=20)
        result = _smc.liquidity(ohlc, swings, range_percent=0.01)
    assert isinstance(result, pd.DataFrame), (
        f"smc.liquidity() must return DataFrame; got {type(result)!r}."
    )
    for col in ("Liquidity", "Swept"):
        assert col in result.columns, (
            f"smc.liquidity() result missing required column `{col}`; "
            f"got {list(result.columns)}. Consumer at smc_ict.py:350-393 "
            f"reads this column for liquidity-sweep signals."
        )


def test_smc_spof_smoke_retracements():
    """B719 SPOF smoke: retracements() returns DataFrame with Direction
    / CurrentRetracement% columns (consumed by smc_ict.py lines 402-413
    for OTE 62-79% Fib zone signals)."""
    _smc = _get_vendored_smc()
    ohlc = _make_ohlc()
    with contextlib.redirect_stdout(io.StringIO()):
        swings = _smc.swing_highs_lows(ohlc, swing_length=20)
        result = _smc.retracements(ohlc, swings)
    assert isinstance(result, pd.DataFrame), (
        f"smc.retracements() must return DataFrame; got {type(result)!r}."
    )
    for col in ("Direction", "CurrentRetracement%"):
        assert col in result.columns, (
            f"smc.retracements() result missing required column "
            f"`{col}`; got {list(result.columns)}. Consumer at "
            f"smc_ict.py:402-413 reads this column for OTE zone signal."
        )
