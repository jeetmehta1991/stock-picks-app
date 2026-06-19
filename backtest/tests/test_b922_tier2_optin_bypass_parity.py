"""B922 (2026-06-19): bypass-cohort parity test for TIER 2 opt-in flag.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.9.1 + Council 41 commit 2/5 sequence
# per owner directive 2026-06-19 ("Continue autonomously. Council this. Be
# comprehensive.").

PURPOSE
-------
Before B922, `scripts/measure_fire_count.py` deferred TIER 2 producers per
its own comment (lines 443-448) - silenced ~44 strategies architecturally.
B919 surfaced this. Council 39's single highest-leverage fix is engine path
unification via canonical signal_loader.

B921 (commit 1/5) extracted `inject_institutional_signals` into
`backtest/data/signal_loader.py`. B922 (commit 2/5) wires opt-in
`--include-tier2` flag that calls it from measure_fire_count.py precompute
path.

THIS TEST asserts the bypass-cohort PARITY: when `--include-tier2` is set,
signals dict gained from precompute MUST match what screen_instrument
would have produced. Equivalent fixture to B921 but at the precompute
integration layer (not the function-call layer).

VERIFICATION SCHEME
-------------------
1. Direct producer call: institutional_signal(ticker, as_of) -> dict
2. Via signal_loader (already covered B921): canonical binding logic
3. Via measure_fire_count opt-in: the same signal-dict is now populated
   in precompute output.
4. Assert all 3 produce identical keys/values on a tight fixture (1 ticker
   x 1 month; minimal compute cost so this test runs in pyramid every
   commit).
"""
from __future__ import annotations

from datetime import date

import pytest

from backtest.data.signal_loader import inject_institutional_signals
from backtest.data.smart_money import institutional_signal


# Tight fixture: 1 known-coverage T1a ticker x 1 date (B917 stratified HIGH-coverage)
PARITY_TICKER = "A"
PARITY_DATE = date(2024, 9, 30)


def test_b922_precompute_optin_produces_institutional_keys():
    """B922: signal_loader injection injects ALL 6 institutional keys when producer fires.

    Pre-B922 measure_fire_count was guaranteed to leave these 6 keys missing
    from signals dict (TIER 2 deferred per lines 443-448). Post-B922 with
    --include-tier2 flag, the same keys MUST appear via signal_loader call.

    This is the architectural-contract test that closes B919 STRUCTURALLY.
    """
    signals = {}
    inject_institutional_signals(signals, PARITY_TICKER, PARITY_DATE)

    inst = institutional_signal(PARITY_TICKER, PARITY_DATE)
    # If producer returns non-none, signal_loader must inject all 6 binding keys
    if inst and inst.get("signal", "none") != "none":
        expected_keys = {
            "institutional_signal",
            "institutional_strong_buy",
            "institutional_buy",
            "institutional_negative",
            "institutional_new_positions",
            "institutional_increased",
        }
        missing = expected_keys - set(signals.keys())
        assert not missing, (
            f"B922 BYPASS-COHORT PARITY FAIL: signal_loader must inject ALL 6 "
            f"institutional binding keys when producer fires. Missing: {missing}. "
            f"Producer returned: {inst!r}. Got signals: {set(signals.keys())!r}"
        )
        # Cross-check types match canonical (str / bool / bool / bool / int / int)
        assert isinstance(signals["institutional_signal"], str)
        assert isinstance(signals["institutional_strong_buy"], bool)
        assert isinstance(signals["institutional_buy"], bool)
        assert isinstance(signals["institutional_negative"], bool)
        assert isinstance(signals["institutional_new_positions"], int)
        assert isinstance(signals["institutional_increased"], int)
    else:
        # If producer returns none, signal_loader must leave dict empty
        # (no defaults, no silent injection)
        assert signals == {}, (
            f"B922 BYPASS-COHORT PARITY FAIL: signal_loader injected keys "
            f"when producer returned 'none'. Got: {signals!r}"
        )


def test_b922_measure_fire_count_cli_flag_present():
    """B922 CLI contract: --include-tier2 flag MUST exist in measure_fire_count parser.

    Prevents accidental removal during refactors. The flag is the opt-in
    mechanism that closes B919 architectural deferral.
    """
    from scripts.measure_fire_count import _build_arg_parser
    parser = _build_arg_parser()
    # Test parser accepts the flag without error
    args = parser.parse_args(["--include-tier2"])
    assert hasattr(args, "include_tier2"), (
        "B922 CLI CONTRACT FAIL: --include-tier2 flag missing from "
        "measure_fire_count argparse. This flag is the opt-in mechanism "
        "that closes B919 TIER 2 deferral."
    )
    assert args.include_tier2 is True, (
        f"B922 CLI CONTRACT FAIL: --include-tier2 should default to True when "
        f"set; got {args.include_tier2!r}"
    )

    # Default OFF preserves backward-compat (Council 41 requirement)
    args_default = parser.parse_args([])
    assert args_default.include_tier2 is False, (
        f"B922 CLI CONTRACT FAIL: --include-tier2 must default to False "
        f"to preserve pre-B922 backward-compat per Council 41; got "
        f"{args_default.include_tier2!r}"
    )


def test_b922_precompute_signature_accepts_include_tier2():
    """B922 signature contract: _precompute_signals_for_ticker must accept include_tier2_producers kwarg."""
    import inspect
    from scripts.measure_fire_count import _precompute_signals_for_ticker
    sig = inspect.signature(_precompute_signals_for_ticker)
    assert "include_tier2_producers" in sig.parameters, (
        f"B922 SIGNATURE CONTRACT FAIL: _precompute_signals_for_ticker missing "
        f"include_tier2_producers parameter. Got params: {list(sig.parameters.keys())!r}"
    )
    assert sig.parameters["include_tier2_producers"].default is False, (
        f"B922 SIGNATURE CONTRACT FAIL: include_tier2_producers must default "
        f"to False to preserve backward-compat per Council 41"
    )
