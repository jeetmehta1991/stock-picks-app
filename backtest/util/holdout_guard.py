"""Batch 477 (2026-05-29) -- M4 final OOS holdout guard.

DEC-505 walk-forward folds are in-sample CV across the available range.
For a truly untouched final-OOS evaluation, this module reserves a date
window that no optimizer / cube / verdict step may inspect until the
1A-alpha gate decision.

API:
  FINAL_OOS_HOLDOUT_START / END  -- module constants defining the locked
                                     window. Updated only in committed
                                     code (review-gated).

  is_in_holdout(d, unlocked=False) -> bool
      True iff `d` falls inside the holdout window AND `unlocked` is False.
      Use to GATE access in optimizer/cube/walk-forward callers.

  assert_no_holdout_intrusion(dates_iterable, caller_name)
      Raises HoldoutViolationError if any date in the iterable falls inside
      the holdout AND no unlock context is active. Designed to wrap engine
      entry points so accidental holdout inspection surfaces in CI.

  HoldoutUnlock() : context manager
      Explicit "yes I really do want to look at the holdout" scope.
      Audit-logs the access via the standard `silent_failure_logger` so
      production unlocks are traceable. Use ONLY for the final 1A-alpha
      gate evaluation.
"""
from __future__ import annotations

import threading
from datetime import date
from typing import Iterable


# DEC-505 final-OOS holdout: 6 months at the tail of the Stage 2 data range.
# Locked window. Edits require owner approval + ADR.
FINAL_OOS_HOLDOUT_START = date(2026, 1, 1)
FINAL_OOS_HOLDOUT_END   = date(2026, 6, 30)


class HoldoutViolationError(RuntimeError):
    """Raised when a caller tries to inspect data inside the locked
    holdout window without an active HoldoutUnlock."""


_unlock_state = threading.local()
_unlock_state.depth = 0


class HoldoutUnlock:
    """Context manager that grants holdout access for the duration of its
    `with` block. Use sparingly -- only for the final 1A-alpha gate read.

    Example:
        with HoldoutUnlock("phase-1a-alpha-gate-evaluation"):
            verdicts = compute_phase_1a_alpha_gate(trade_log)
    """

    def __init__(self, reason: str):
        if not reason or len(reason) < 10:
            raise ValueError(
                "HoldoutUnlock requires a >=10-char reason string "
                "(audit-log entry)"
            )
        self.reason = reason

    def __enter__(self):
        depth = getattr(_unlock_state, "depth", 0)
        _unlock_state.depth = depth + 1
        # Emit a one-shot audit log via the shared helper (Batch 458).
        try:
            from backtest.util.silent_failure_logger import logger
            logger.warning(
                "HoldoutUnlock entered: reason=%s depth=%d",
                self.reason, _unlock_state.depth,
            )
        except Exception:
            pass
        return self

    def __exit__(self, exc_type, exc_val, tb):
        depth = getattr(_unlock_state, "depth", 0)
        _unlock_state.depth = max(0, depth - 1)
        return False


def _is_unlocked() -> bool:
    return getattr(_unlock_state, "depth", 0) > 0


def is_in_holdout(d: date, unlocked: bool = False) -> bool:
    """Return True iff `d` is inside the locked holdout window."""
    if unlocked or _is_unlocked():
        return False
    if not isinstance(d, date):
        return False
    return FINAL_OOS_HOLDOUT_START <= d <= FINAL_OOS_HOLDOUT_END


def assert_no_holdout_intrusion(
    dates_iterable: Iterable,
    caller_name: str,
) -> None:
    """Raise HoldoutViolationError if any date in the iterable intrudes
    on the holdout (unless an HoldoutUnlock context is active).
    """
    if _is_unlocked():
        return
    intruders: list[date] = []
    for d in dates_iterable:
        if isinstance(d, date) and is_in_holdout(d):
            intruders.append(d)
            if len(intruders) >= 5:
                break  # cap the error message length
    if intruders:
        raise HoldoutViolationError(
            f"{caller_name}: dates {intruders[:5]} intrude on holdout "
            f"{FINAL_OOS_HOLDOUT_START}..{FINAL_OOS_HOLDOUT_END}. "
            "Wrap the call in `with HoldoutUnlock('reason'):` to grant "
            "access (final 1A-alpha gate evaluation only)."
        )
