"""Batch 477 (2026-05-29) -- M4 final OOS holdout guard tests."""
from __future__ import annotations

from datetime import date

import pytest

from backtest.util.holdout_guard import (
    FINAL_OOS_HOLDOUT_END,
    FINAL_OOS_HOLDOUT_START,
    HoldoutUnlock,
    HoldoutViolationError,
    assert_no_holdout_intrusion,
    is_in_holdout,
)


def test_constants_define_a_meaningful_window():
    assert FINAL_OOS_HOLDOUT_START < FINAL_OOS_HOLDOUT_END
    # Should be a multi-month window for meaningful evaluation
    span = (FINAL_OOS_HOLDOUT_END - FINAL_OOS_HOLDOUT_START).days
    assert span >= 90, f"holdout span {span}d too short for OOS eval"


def test_is_in_holdout_inside_window_returns_true():
    inside = date(2026, 3, 15)  # mid-holdout assuming default
    assert FINAL_OOS_HOLDOUT_START <= inside <= FINAL_OOS_HOLDOUT_END
    assert is_in_holdout(inside) is True


def test_is_in_holdout_before_window_returns_false():
    before = FINAL_OOS_HOLDOUT_START.replace(year=FINAL_OOS_HOLDOUT_START.year - 1)
    assert is_in_holdout(before) is False


def test_is_in_holdout_after_window_returns_false():
    # End + 30 days
    after = date.fromordinal(FINAL_OOS_HOLDOUT_END.toordinal() + 30)
    assert is_in_holdout(after) is False


def test_unlock_kwarg_overrides_holdout_check():
    inside = FINAL_OOS_HOLDOUT_START
    assert is_in_holdout(inside, unlocked=True) is False


def test_assert_no_intrusion_raises_when_inside_window():
    inside = date(2026, 3, 15)
    with pytest.raises(HoldoutViolationError, match="intrude on holdout"):
        assert_no_holdout_intrusion([inside], "test_caller")


def test_assert_no_intrusion_passes_when_outside_window():
    outside = date(2023, 6, 15)
    assert_no_holdout_intrusion([outside], "test_caller")  # no raise


def test_holdout_unlock_context_grants_access():
    inside = FINAL_OOS_HOLDOUT_START
    with HoldoutUnlock("phase-1a-alpha-gate-evaluation"):
        assert is_in_holdout(inside) is False
        assert_no_holdout_intrusion([inside], "alpha-gate")  # no raise
    # Outside the context, lock re-engages
    assert is_in_holdout(inside) is True


def test_holdout_unlock_requires_long_reason():
    with pytest.raises(ValueError, match=">=10-char reason"):
        HoldoutUnlock("too short")


def test_unlock_is_thread_local_reentrant():
    """Nested unlock contexts don't drop the lock prematurely."""
    inside = FINAL_OOS_HOLDOUT_START
    with HoldoutUnlock("outer-reason-context-block"):
        with HoldoutUnlock("inner-reason-context-block"):
            assert is_in_holdout(inside) is False
        # Inner exited, outer still active -> still unlocked
        assert is_in_holdout(inside) is False
    # Both exited -> lock restored
    assert is_in_holdout(inside) is True
