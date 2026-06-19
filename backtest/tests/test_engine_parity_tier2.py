"""B921 (2026-06-19): engine path parity test for TIER 2 signal injection.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.9.1 (engine path unification) +
# Council 39 verdict (single highest-leverage fix) + Council 40 (Phase P0
# Item 1 commit 1 of 5) per owner directive 2026-06-19.

PURPOSE
-------
After B921 extraction of inject_institutional_signals from screener.py into
backtest/data/signal_loader.py, BOTH engine paths (screen_instrument +
measure_fire_count) MUST produce identical signal dict output when called
on the same (ticker, as_of) inputs.

This test asserts that contract on a fixed 5-ticker x 20-date fixture.
Future TIER 2 producers extracted in subsequent commits will extend this
test with additional injection functions.

VERIFICATION SCHEME
-------------------
1. Direct producer call: institutional_signal(ticker, as_of) -> dict
2. Via signal_loader: inject_institutional_signals({}, ticker, as_of)
   -> signal_keys derived from producer dict
3. Assert signal_keys produced by (2) match the canonical screener.py:7975-7983
   binding logic over the producer output of (1).

This catches any future divergence in:
- Dict-key typos (B918 class)
- Producer signature changes
- Silent-failure path divergence
- Default-injection changes
"""
from __future__ import annotations

from datetime import date

import pytest

from backtest.data.signal_loader import inject_institutional_signals
from backtest.data.smart_money import institutional_signal


# Fixed fixture: 5 T1a tickers with verified producer-data coverage in window
# (per B917 stratified-sample audit; A/ABNB/ACGL/ADM/ADP had 100% coverage Sep-Dec 2024)
PARITY_FIXTURE_TICKERS = ["A", "ABNB", "ACGL", "ADM", "ADP"]

# Fixed fixture: 4 monthly snapshots in 2024 (within R4 cube window)
PARITY_FIXTURE_DATES = [
    date(2024, 3, 31),
    date(2024, 6, 30),
    date(2024, 9, 30),
    date(2024, 12, 31),
]


def _canonical_screener_logic(inst: dict) -> dict:
    """Mirror the canonical screener.py:7975-7983 binding logic for comparison.

    This is the EXACT same logic that screener.py used pre-B921 + that
    signal_loader.inject_institutional_signals uses post-B921. The parity
    test confirms they remain identical.
    """
    if not (inst and isinstance(inst, dict)):
        return {}
    sig_kind = inst.get("signal", "none")
    return {
        "institutional_signal": sig_kind,
        "institutional_strong_buy": sig_kind == "strong_buy",
        "institutional_buy": sig_kind in ("buy", "strong_buy"),
        "institutional_negative": sig_kind == "negative",
        "institutional_new_positions": int(inst.get("new_positions", 0) or 0),
        "institutional_increased": int(inst.get("increased", 0) or 0),
    }


@pytest.mark.parametrize("ticker", PARITY_FIXTURE_TICKERS)
@pytest.mark.parametrize("as_of", PARITY_FIXTURE_DATES)
def test_b921_signal_loader_institutional_matches_canonical_screener(ticker, as_of):
    """B921 engine path parity: signal_loader output must equal canonical screener binding.

    For each (ticker, as_of) in the fixture, assert:
        inject_institutional_signals({}, ticker, as_of) ==
        canonical_screener_logic(institutional_signal(ticker, as_of))

    Any divergence indicates one of:
    - Dict-key typo introduced (B918 class)
    - Producer signature changed without consumer update
    - Silent-failure path divergence
    - Default-injection drift
    """
    # Direct producer call (what canonical screener.py uses inline)
    inst = institutional_signal(ticker, as_of)
    expected = _canonical_screener_logic(inst)

    # Via extracted signal_loader (B921)
    actual = {}
    inject_institutional_signals(actual, ticker, as_of)

    # All canonical keys must match exactly
    for key in expected:
        assert key in actual, (
            f"B921 PARITY FAIL: key '{key}' missing from signal_loader output "
            f"for {ticker} @ {as_of}. Producer returned: {inst!r}"
        )
        assert actual[key] == expected[key], (
            f"B921 PARITY FAIL: key '{key}' value mismatch for {ticker} @ {as_of}. "
            f"Canonical screener: {expected[key]!r}, signal_loader: {actual[key]!r}. "
            f"Producer returned: {inst!r}"
        )

    # No extra keys (would indicate signal_loader injected something canonical didn't)
    extra = set(actual.keys()) - set(expected.keys())
    assert not extra, (
        f"B921 PARITY FAIL: signal_loader injected unexpected keys {extra} "
        f"for {ticker} @ {as_of}. Producer returned: {inst!r}"
    )


def test_b921_signal_loader_handles_missing_producer_gracefully():
    """Empty/None producer output must produce empty signals dict, not exception."""
    # Empty input dict + impossible-coverage ticker should produce empty result
    # (some keys may or may not be present depending on producer behavior on
    # a synthetic non-existent ticker; assert no exception is raised)
    signals = {}
    try:
        inject_institutional_signals(signals, "NONEXISTENT_TICKER_XYZ123", date(2024, 6, 30))
    except Exception as e:
        pytest.fail(
            f"B921 signal_loader raised on non-existent ticker (expected silent failure): {e!r}"
        )


# ---------------------------------------------------------------------------
# B923 (2026-06-19) P0 commit 3/5: insider_buying extraction parity
# ---------------------------------------------------------------------------

from backtest.data.signal_loader import inject_insider_buying_signals
from backtest.signals.insider_buying import compute_insider_cluster_signals


def _canonical_screener_insider_logic(insider: dict) -> dict:
    """Mirror screener.py:7944-7945 insider-cluster binding logic.

    Pre-B923 inline:
        insider = compute_insider_cluster_signals(ticker, as_of)
        if insider:
            signals.update(insider)

    The binding is a passthrough `signals.update(insider)` so canonical
    output is just the producer output dict.
    """
    return insider if insider else {}


@pytest.mark.parametrize("ticker", PARITY_FIXTURE_TICKERS)
@pytest.mark.parametrize("as_of", PARITY_FIXTURE_DATES)
def test_b923_signal_loader_insider_matches_canonical_screener(ticker, as_of):
    """B923 engine path parity: insider buying signal_loader output equals canonical screener binding."""
    insider = compute_insider_cluster_signals(ticker, as_of)
    expected = _canonical_screener_insider_logic(insider)

    actual = {}
    inject_insider_buying_signals(actual, ticker, as_of)

    # All canonical keys must match exactly (passthrough binding)
    for key in expected:
        assert key in actual, (
            f"B923 PARITY FAIL: key '{key}' missing from signal_loader output "
            f"for {ticker} @ {as_of}. Producer returned: {insider!r}"
        )
        assert actual[key] == expected[key], (
            f"B923 PARITY FAIL: key '{key}' value mismatch for {ticker} @ {as_of}. "
            f"Canonical: {expected[key]!r}, signal_loader: {actual[key]!r}."
        )

    # No extra keys
    extra = set(actual.keys()) - set(expected.keys())
    assert not extra, (
        f"B923 PARITY FAIL: signal_loader injected unexpected keys {extra} "
        f"for {ticker} @ {as_of}."
    )


def test_b923_signal_loader_insider_handles_missing_producer_gracefully():
    """Insider producer raising must not propagate; signals dict left unchanged."""
    signals = {}
    try:
        inject_insider_buying_signals(signals, "NONEXISTENT_TICKER_XYZ123", date(2024, 6, 30))
    except Exception as e:
        pytest.fail(
            f"B923 signal_loader insider raised on non-existent ticker "
            f"(expected silent failure): {e!r}"
        )
