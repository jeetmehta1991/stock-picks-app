# Source: B713 reviewer critique + S4-B713-INSPECT-CURRENTFRAME-REVERT + S4-B713-DTC-THRESHOLD-DIRECTION-FIX per CHECKLIST #77
"""B718a pin tests: fail-closed behavior + DTC threshold direction fix.

B713 reviewer's 4-claim critique resolved (or partially-resolved):

(1) inspect.currentframe FAIL-OPEN behavior -- now FAIL-CLOSED.
    Original: `if s is not None and _short_borrow_trap_active(s): fires = False`
    -- if frame introspection failed, shorts fired UNPROTECTED.
    B718a: if frame introspection cannot find `s`, fires = False.
    The fragility (introspection itself) remains; fail-mode is now safe.
    Full structural revert to explicit borrow_ok gate per-strategy is staged
    as B718b/c/d cluster-by-cluster bulk refactor (116 short strategies).

(2) DTC THRESHOLD WRONG DIRECTION -- now FIXED.
    Original: `dtc > 8.0` (Q6 2026-06-10 tightening from 5.0 -> 8.0)
    B718a: `dtc > 5.0` (revert direction; GME pre-squeeze DTC 5-7 passes
    >8 threshold, defeating the guard's stated purpose).

B713 reviewer's remaining concerns (NOT addressed in B718a):
(3) Pre-B671 cross-cluster short backtest contamination -- S4-B713-PRE-B671...
    queued; needs full pyramid re-run after structural revert lands.
(4) Bi-monthly FINRA staleness -- S4-B713-FASTER-BORROW-COST-DATA-SOURCE
    queued for data-source evaluation.
"""
from __future__ import annotations

import pytest

from backtest.signals.screener import _strat, _strat3, _short_borrow_trap_active


# ---------------------------------------------------------------------------
# Pin 1: _short_borrow_trap_active threshold = 5.0 (not 8.0)
# ---------------------------------------------------------------------------
def test_b718a_pin1_dtc_threshold_direction_fix():
    """DTC threshold MUST be > 5.0, not > 8.0 (B713 reviewer wrong-direction
    critique). GME pre-squeeze range 5-7 must be CAUGHT by the guard."""
    # GME-class: DTC=6.0 -- pre-squeeze, MUST be caught
    assert _short_borrow_trap_active({"days_to_cover": 6.0}) is True, (
        "GME-class DTC=6 must trigger guard; if False, threshold reverted"
    )
    # Below threshold: DTC=4.0 -- normal, must NOT trigger
    assert _short_borrow_trap_active({"days_to_cover": 4.0}) is False
    # At threshold boundary: DTC=5.0 -- NOT caught (uses > not >=)
    assert _short_borrow_trap_active({"days_to_cover": 5.0}) is False
    # Edge: missing days_to_cover defaults to 0 -- not caught
    assert _short_borrow_trap_active({}) is False
    # Edge: None -- not caught
    assert _short_borrow_trap_active({"days_to_cover": None}) is False


# ---------------------------------------------------------------------------
# Pin 2: _strat SHORT direction fails CLOSED when frame introspection
# cannot find `s` (B713 reviewer fail-open critique)
# ---------------------------------------------------------------------------
def test_b718a_pin2_strat_short_fails_closed_when_no_s_in_caller():
    """When _strat is called with direction='short' from a caller that does
    NOT have `s` in its local scope, fires MUST be forced to False
    (fail-closed) -- NOT silently passed through (fail-open per B713 critique).
    """
    # Simulate a caller that doesn't have `s` in locals -- the introspection
    # will find this test function's frame, which has no `s`
    result = _strat(
        fires=True,
        direction="short",
        category="test",
        signals_used=["test_signal"],
        context_bullets=["test bullet"],
    )
    assert result["fires"] is False, (
        "_strat(direction='short') must fail CLOSED when caller has no `s` "
        "in locals; got fires=True (fail-open, the original bug)"
    )


def test_b718a_pin3_strat_short_with_high_dtc_blocks_fire():
    """When caller has `s` in locals with days_to_cover > 5.0, fires must
    be blocked."""
    s = {"days_to_cover": 10.0}  # noqa: F841 -- intentional local for introspection
    result = _strat(
        fires=True,
        direction="short",
        category="test",
        signals_used=["test_signal"],
        context_bullets=["test bullet"],
    )
    assert result["fires"] is False, (
        "_strat(direction='short') must block when caller's s has DTC > 5"
    )


def test_b718a_pin4_strat_short_with_low_dtc_allows_fire():
    """When caller has `s` in locals with days_to_cover <= 5.0, fires
    must pass through."""
    s = {"days_to_cover": 3.0}  # noqa: F841 -- intentional local for introspection
    result = _strat(
        fires=True,
        direction="short",
        category="test",
        signals_used=["test_signal"],
        context_bullets=["test bullet"],
    )
    assert result["fires"] is True, (
        "_strat(direction='short') must allow fire when caller's s has DTC <= 5"
    )


# ---------------------------------------------------------------------------
# Pin 5: LONG direction unaffected (no borrow guard on longs)
# ---------------------------------------------------------------------------
def test_b718a_pin5_strat_long_unaffected_by_borrow_guard():
    """direction='long' must not be subject to borrow guard regardless of
    DTC value."""
    s = {"days_to_cover": 50.0}  # noqa: F841
    result = _strat(
        fires=True,
        direction="long",
        category="test",
        signals_used=["test_signal"],
        context_bullets=["test bullet"],
    )
    assert result["fires"] is True, (
        "direction='long' must not be subject to borrow guard"
    )


# ---------------------------------------------------------------------------
# Pin 6: _strat3 fails CLOSED parallel to _strat
# ---------------------------------------------------------------------------
def test_b718a_pin6_strat3_short_branch_fails_closed_when_no_s():
    """When _strat3 is called with fires_short=True from a caller without
    `s` in locals, fires_short must be forced to False (fail-closed)."""
    result = _strat3(
        fires_long=False,
        fires_short=True,
        category="test",
        signals_used_long=[],
        signals_used_short=["test_short_signal"],
        bullets_long=[],
        bullets_short=["test short bullet"],
    )
    # Both branches blocked -> overall return is no-fire
    assert result["fires"] is False, (
        "_strat3 SHORT branch must fail CLOSED when caller has no `s`"
    )


def test_b718a_pin7_strat3_short_high_dtc_blocks_only_short():
    """When _strat3 is called with fires_short=True AND fires_long=True AND
    DTC > 5 in caller's s, the SHORT branch is blocked and the LONG branch
    passes through cleanly (single-direction LONG outcome)."""
    s = {"days_to_cover": 7.0}  # noqa: F841 -- GME-class
    result = _strat3(
        fires_long=True,
        fires_short=True,
        category="test",
        signals_used_long=["test_long"],
        signals_used_short=["test_short"],
        bullets_long=["long bullet"],
        bullets_short=["short bullet"],
    )
    # Short blocked, long not -> direction=long
    assert result["fires"] is True
    assert result["direction"] == "long", (
        f"Expected direction='long' after SHORT blocked by borrow guard; got {result}"
    )
