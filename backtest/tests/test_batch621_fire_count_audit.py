"""Batch 621 (2026-06-08) -- fire-count audit harness tests.

Source: scripts/audit_fire_counts.py (this batch); scripts/estimate_fire
_count.py (B619). Per CHECKLIST #77 source-of-truth declaration.


Harness scans every ALL_STRATEGIES entry, runs the B619 estimator,
classifies into PASS_CUBE / WARN / FAIL / FAIL_BUT_HAS_OR /
INCOMPLETE_PRIORS / NO_GATES_EXTRACTED.

Owner-directed B621 (option A from the queue): "fire-count audit of
all walked strategies". The harness lets future audits run as a
single command.

CRITICAL LIMITATION codified in pin (5): the estimator treats all
extracted gates as AND; strategies with OR composites (e.g.
squeeze_setup_long via L1c OR + L2 OR; smart-money sleeves via
_has_smart_money_buy helper) get false-FAIL verdicts. The
has_or_composite flag + the *_BUT_HAS_OR verdict suffix mark these
for manual review.

Pins:
  (1) extract_gates returns unique gate names from a strategy fn
  (2) has_or_composite detects 'or s.get(' patterns
  (3) has_or_composite detects _has_smart_money_buy helper calls
  (4) audit_all runs without error on the full ALL_STRATEGIES set
  (5) FAIL_FIRE_STARVED_BUT_HAS_OR is applied to squeeze_setup_long
      (the canonical OR-composite false-FAIL example)
  (6) the REAL FAIL list (pure-AND, < 5 fires/yr) matches the expected
      set documented in the commit message + audit JSON
"""
from __future__ import annotations

import pytest

from scripts.audit_fire_counts import (
    audit_all, extract_gates, has_or_composite,
)


def test_batch621_extract_gates_unique():
    """Pin (1)."""
    from backtest.signals.screener import strat_break_retest_volume
    gates = extract_gates(strat_break_retest_volume)
    assert isinstance(gates, list)
    assert len(gates) == len(set(gates)), "gates must be unique"
    # Sanity check: post-B617 break_retest_volume uses obv_bullish
    # (LONG) + obv_bearish (SHORT) etc.
    assert "resistance_break_retest" in gates
    assert "obv_bullish" in gates


def test_batch621_has_or_composite_detects_or_keyword():
    """Pin (2): squeeze_setup_long uses 'or s.get(' in L1c + L2."""
    from backtest.signals.screener import strat_squeeze_setup_long
    assert has_or_composite(strat_squeeze_setup_long) is True, (
        "squeeze_setup_long uses OR composites in L1c + L2; detector "
        "must flag this so the estimator's AND-based output is marked "
        "as a likely false-FAIL"
    )


def test_batch621_has_or_composite_detects_helper():
    """Pin (3): smart-money sleeves use _has_smart_money_buy() which
    is an OR-composite helper. Helper-call detection must trigger."""
    from backtest.signals.screener import strat_52w_high_breakout_with_smart_money_long
    assert has_or_composite(strat_52w_high_breakout_with_smart_money_long) is True


def test_batch621_audit_all_runs_clean():
    """Pin (4): audit_all() runs without error on full ALL_STRATEGIES."""
    audit = audit_all()
    assert "total_strategies" in audit
    assert "verdict_counts" in audit
    assert "results" in audit
    assert audit["total_strategies"] >= 200  # current is 221
    # Every result has required keys
    for r in audit["results"]:
        assert "strategy" in r
        assert "verdict" in r
        assert "has_or_composite" in r


def test_batch621_or_composite_strategies_get_demoted_verdict():
    """Pin (5): squeeze_setup_long appears in audit with
    FAIL_FIRE_STARVED_BUT_HAS_OR verdict (false-FAIL via OR clauses
    that the AND-product estimator over-restricts)."""
    audit = audit_all()
    row = next(r for r in audit["results"]
               if r["strategy"] == "squeeze_setup_long")
    assert row["has_or_composite"] is True
    # The independence-AND product gives < 5 fires/yr; the OR-flag
    # demotes verdict to FAIL_BUT_HAS_OR (manual review)
    assert row["verdict"] == "FAIL_FIRE_STARVED_BUT_HAS_OR", (
        f"squeeze_setup_long should be marked FAIL_FIRE_STARVED_BUT_HAS_OR "
        f"(false-FAIL via OR composites); got {row['verdict']}"
    )


# The REAL FAIL set as of B635 audit (post-PRIOR_RATES expansion;
# pure-AND strategies, < 5 fires/yr UB).
# These are CANDIDATES for owner review (loosen / mark exploratory /
# delete) per `feedback_minimum_fire_count_gate_before_cube`. NOT
# auto-actioned by this audit.
#
# B635 update: PRIOR_RATES expansion (243 -> 22 INCOMPLETE) surfaced
# 14 new REAL FAIL candidates that were previously hidden as
# INCOMPLETE_PRIORS. Pre-B635 set was 5; post-B635 is 19. Drift
# detection pin should not break on PRIOR_RATES refinement (post-R5
# back-fill); accept superset.
EXPECTED_REAL_FAIL = {
    # Pre-B635 set (well-known fire-starved walked strategies):
    "volume_spike_breakout_retest",
    "volume_spike_breakout",
    "break_retest_confluence",
    "52wl_break_retest_short",
    "break_retest_volume",
    # B635 newly surfaced (formerly INCOMPLETE_PRIORS):
    "stochrsi_oversold",
    "cup_and_handle_long",
    "golden_cross_volume",
    "stoch_oversold",
    "dc20_break_retest",
    "morning_star",
    "52wh_break_retest",
    "golden_cross_20_50",
    "activist_13d_long",
    "donchian_10_breakout",
    "keltner_lower",
    "pivot_r2_continuation",
    "cup_and_handle_retest_long",
    "r1_break_retest",
}


def test_batch621_real_fail_set_matches_audit():
    """Pin (6): the REAL FAIL set (pure-AND, < 5 fires/yr UB) matches
    the documented set. Test fails if a strategy moves out of the FAIL
    bucket (loosened) or a new one moves in (tightened) - either way,
    surfaces the change for the commit message."""
    audit = audit_all()
    real_fail = {
        r["strategy"] for r in audit["results"]
        if r["verdict"] == "FAIL_FIRE_STARVED"
    }
    assert real_fail == EXPECTED_REAL_FAIL, (
        f"REAL FAIL set drift -- expected {EXPECTED_REAL_FAIL}, got "
        f"{real_fail}. Diff: added {real_fail - EXPECTED_REAL_FAIL}, "
        f"removed {EXPECTED_REAL_FAIL - real_fail}. Update commit + "
        f"this pin if intentional."
    )
