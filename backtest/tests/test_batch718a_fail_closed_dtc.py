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
# Pin 2: SUPERSEDED-BY-B718d. Original assertion: `_strat` fails closed when
# caller frame has no `s` (via inspect.currentframe central guard).
# Post-B718d (2026-06-13): central guard REMOVED; explicit per-strategy gate
# at call site replaces it. `_strat` is now a pure passthrough -- this pin
# re-asserts the new contract: fires=True in is fires=True out.
# ---------------------------------------------------------------------------
def test_b718a_pin2_strat_now_passes_through_fires_post_b718d():
    """Post-B718d: `_strat` no longer applies a central borrow guard. The
    strategy itself folds `not _short_borrow_trap_active(s)` into its `fires`
    boolean BEFORE calling `_strat`. B744 lint enforces this cluster-wide.
    """
    result = _strat(
        fires=True,
        direction="short",
        category="test",
        signals_used=["test_signal", "borrow_ok"],
        context_bullets=["test bullet"],
    )
    # Post-B718d: fires=True passes through; strategy was responsible for
    # setting this to False if borrow trap was active.
    assert result["fires"] is True
    assert result["direction"] == "short"


def test_b718a_pin3_strat_short_high_dtc_requires_explicit_gate_post_b718d():
    """Post-B718d: `_strat` no longer reads caller's `s`. The strategy must
    fold the borrow check into `fires` itself. Here we simulate the explicit
    pattern: `fires = trigger AND not _short_borrow_trap_active(s)`.
    """
    s = {"days_to_cover": 10.0}
    # Strategy's own gate folds the borrow check into fires
    fires_after_gate = True and not _short_borrow_trap_active(s)
    assert fires_after_gate is False, "explicit gate should set fires=False at DTC=10"
    result = _strat(
        fires=fires_after_gate,
        direction="short",
        category="test",
        signals_used=["test_signal", "borrow_ok"],
        context_bullets=["test bullet"],
    )
    assert result["fires"] is False


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
# Pin 6: SUPERSEDED-BY-B718d. Original assertion: `_strat3` fails closed when
# caller has no `s` (via inspect.currentframe central guard).
# Post-B718d (2026-06-13): central guard REMOVED; explicit per-strategy gate
# at call site replaces it (B740-B743 + B744 lint). `_strat3` is now a pure
# passthrough -- this pin re-asserts the new contract: fires_short passed in
# True is returned True. Strategies enforce the gate themselves before calling.
# ---------------------------------------------------------------------------
def test_b718a_pin6_strat3_now_passes_through_fires_short_post_b718d():
    """Post-B718d: `_strat3` no longer applies a central borrow guard. Strategies
    are responsible for the explicit `_short_borrow_trap_active(s)` gate at
    their own call site (B740-B743) + the B744 registration-time lint enforces
    it cluster-wide.
    """
    result = _strat3(
        fires_long=False,
        fires_short=True,
        category="test",
        signals_used_long=[],
        signals_used_short=["test_short_signal"],
        bullets_long=[],
        bullets_short=["test short bullet"],
    )
    # Post-B718d: fires_short=True passes through; strategy must have set this
    # to False if borrow trap was active.
    assert result["fires"] is True
    assert result["direction"] == "short"


def test_b718a_pin7_strat3_short_high_dtc_now_requires_explicit_gate_post_b718d():
    """Post-B718d: high DTC alone does NOT block `_strat3` SHORT branch -- the
    strategy must explicitly fold the borrow check into `fires_short` before
    calling. The B744 lint guarantees every short-emitting strategy does so.

    Here we simulate the explicit-gate pattern: strategy computes
    `fires_short = trigger AND not _short_borrow_trap_active(s)` itself.
    """
    from backtest.signals.screener import _short_borrow_trap_active
    s = {"days_to_cover": 7.0}  # GME-class
    # Strategy's own gate folds borrow check into fires_short
    fires_short_after_gate = True and not _short_borrow_trap_active(s)
    assert fires_short_after_gate is False, (
        "explicit gate should set fires_short=False when DTC > 5"
    )
    result = _strat3(
        fires_long=True,
        fires_short=fires_short_after_gate,
        category="test",
        signals_used_long=["test_long"],
        signals_used_short=["test_short", "borrow_ok"],
        bullets_long=["long bullet"],
        bullets_short=["short bullet"],
    )
    # Short blocked at strategy level (post-B718d); LONG passes through
    assert result["fires"] is True
    assert result["direction"] == "long"
