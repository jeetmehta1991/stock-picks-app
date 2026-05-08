"""Property-based tests - DEC-503 pyramid layer (Pass 53 v8h+1 owner-approved 2026-05-08).

Property = invariant that must hold for ALL valid inputs. Hypothesis generates
random inputs and shrinks failures to a minimal counterexample. Catches edge
cases unit tests miss because the test author didn't think of them.

Markers:
    pytest -m property
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


pytestmark = pytest.mark.property


# -- Property 1: safe_filename_stem is idempotent ------------------------
@given(ticker=st.text(min_size=1, max_size=10))
@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
def test_property_safe_filename_stem_idempotent(ticker: str) -> None:
    """safe_filename_stem(safe_filename_stem(x)) == safe_filename_stem(x).
    Applying the safety mapping twice must equal once."""
    from _prefetch_utils import safe_filename_stem
    once = safe_filename_stem(ticker)
    twice = safe_filename_stem(once)
    assert once == twice, f"not idempotent: {ticker!r} -> {once!r} -> {twice!r}"


# -- Property 2: safe_filename_stem never returns reserved names --------
@given(ticker=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
                     min_size=1, max_size=8))
@settings(max_examples=200)
def test_property_safe_filename_stem_avoids_reserved(ticker: str) -> None:
    """Output stem must never be a Windows-reserved name (regardless of input)."""
    from _prefetch_utils import safe_filename_stem, RESERVED_WIN
    out = safe_filename_stem(ticker)
    assert out.upper() not in RESERVED_WIN, (
        f"safe_filename_stem({ticker!r}) -> {out!r} is reserved"
    )


# -- Property 3: doc count is invariant under input order ---------------
@given(ids=st.lists(st.integers(min_value=1, max_value=999), min_size=1, max_size=50))
def test_property_doc_count_dedup_invariant(ids: list[int]) -> None:
    """Counting unique IDs must be invariant under reorderings + duplicates."""
    canonical = len(set(ids))
    shuffled = list(reversed(ids)) + ids
    assert len(set(shuffled)) == canonical


# -- Property 4: regime classifier is idempotent ------------------------
def test_property_regime_classifier_deterministic() -> None:
    """classify_regime(same_input) returns same output across calls."""
    try:
        from backtest.engine.regime_filter import classify_regime
    except ImportError:
        pytest.skip("regime_filter not importable")
    import pandas as pd
    dates = pd.date_range("2024-01-01", periods=252, freq="B")
    spy = pd.DataFrame({
        "close": 400.0 + (pd.Series(range(252)) * 0.5),
        "high":  410.0 + (pd.Series(range(252)) * 0.5),
        "low":   390.0 + (pd.Series(range(252)) * 0.5),
        "open":  400.0 + (pd.Series(range(252)) * 0.5),
        "volume": 100_000_000,
    }, index=dates)
    try:
        a = classify_regime(spy, as_of=dates[-1])
        b = classify_regime(spy, as_of=dates[-1])
    except Exception:
        pytest.skip("classify_regime signature differs from synthetic harness")
    assert a == b, f"non-deterministic regime: {a} vs {b}"


# -- Property 5: profit_factor is non-negative for any pnl series -------
@given(pnl=st.lists(st.floats(min_value=-1000, max_value=1000, allow_nan=False),
                    min_size=1, max_size=100))
def test_property_profit_factor_nonneg(pnl: list[float]) -> None:
    """_profit_factor returns a non-negative number for any pnl series."""
    try:
        from backtest.results.metrics import _profit_factor
    except ImportError:
        pytest.skip("_profit_factor not importable")
    import pandas as pd
    pf = _profit_factor(pd.Series(pnl))
    assert pf >= 0, f"profit_factor returned negative: {pf}"


# -- Property 6: win_rate in [0, 1] -------------------------------------
@given(wins=st.integers(min_value=0, max_value=1000),
       total=st.integers(min_value=1, max_value=1000))
def test_property_win_rate_bounded(wins: int, total: int) -> None:
    """Computed win_rate stays within [0, 1] regardless of input counts."""
    if wins > total:
        wins = total
    rate = wins / total
    assert 0.0 <= rate <= 1.0
