# Source: B719 SMC review (Pattern K) + B555 panel-cache PIT caveat + Decision 3 build #2 owner-approval per CHECKLIST #77
"""B735 pin tests: SMC PIT auditor adapter from B704 earnings_feed_pit_audit.

The auditor is a black-box tool: it ships with 3 case builders covering hazards
H1 (swing-formation confirmation lag), H2 (dealing-range extrema re-anchor =
Pattern K from B719), H3 (panel-cache edge contamination = B555 caveat).

These pin tests verify the auditor:
1. Returns PASS on a deliberately PIT-honest stub producer
2. Returns FAIL on a deliberately PEEKING stub producer
3. Exposes the public API (case builders + audit_smc_producer + audit_all + verdict constants)
"""
from __future__ import annotations

import pandas as pd

from scripts.smc_pit_audit import (
    CASE_BUILDERS,
    FAIL_PEEK,
    PASS,
    audit_all,
    audit_smc_producer,
    build_case_dealing_range_reanchor,
    build_case_panel_cache_edge,
    build_case_swing_confirmation,
)


# --------------------------------------------------------------------------
# Stub producers used to exercise the auditor.
# --------------------------------------------------------------------------
def _pit_honest_producer(prices: pd.DataFrame, as_of: pd.Timestamp) -> dict:
    """PIT-honest swing detector. Uses bars only on or before as_of.

    Confirms a swing high at bar t requires k=3 bars to the right of t all lower.
    Slice to as_of, take last bar position, then check whether the swing was
    formed AT LEAST k bars before as_of.
    """
    px = prices.loc[:as_of]
    k = 3
    if len(px) < 2 * k + 2:
        return {"swing_high_confirmed": False, "dealing_range_high": float("nan"),
                "dealing_range_high_set": False}
    highs = px["high"].to_numpy()
    # confirmed swing = a bar with k lower-high bars BEFORE AND AFTER it, fully within sliced view
    swing_high = float("nan")
    confirmed = False
    range_high_set = False
    for i in range(k, len(highs) - k):
        left_ok = (highs[i - k:i] < highs[i]).all()
        right_ok = (highs[i + 1:i + 1 + k] < highs[i]).all()
        if left_ok and right_ok:
            swing_high = float(highs[i])
            confirmed = True
            range_high_set = True
    return {
        "swing_high_confirmed": confirmed,
        "dealing_range_high": swing_high,
        "dealing_range_high_set": range_high_set,
    }


def _peeking_producer(prices: pd.DataFrame, as_of: pd.Timestamp) -> dict:
    """Peeking producer: ignores as_of slicing, uses the FULL prices frame.

    Looks for the global max high in the entire prices frame as the "swing
    high" -- straightforward leak that the auditor must catch.
    """
    highs = prices["high"].to_numpy()
    swing_high = float(highs.max())
    return {
        "swing_high_confirmed": True,
        "dealing_range_high": swing_high,
        "dealing_range_high_set": True,
    }


# --------------------------------------------------------------------------
# Pin tests
# --------------------------------------------------------------------------
def test_b735_pin1_case_builders_registered():
    """All 3 hazards are registered in CASE_BUILDERS."""
    assert set(CASE_BUILDERS.keys()) == {
        "swing_confirmation", "dealing_range_reanchor", "panel_cache_edge"
    }, f"CASE_BUILDERS keys must match the 3 SMC hazards; got {set(CASE_BUILDERS.keys())}"


def test_b735_pin2_pit_honest_producer_passes_swing_confirmation():
    """A causal swing detector must pass the H1 case."""
    case = build_case_swing_confirmation(k=3)
    result = audit_smc_producer(_pit_honest_producer, case)
    assert result.verdict == PASS, (
        f"PIT-honest producer should PASS swing_confirmation; got {result.verdict}\n"
        f"probes: {result.probes}"
    )


def test_b735_pin3_peeking_producer_fails_swing_confirmation():
    """A producer that uses the full frame must FAIL on the as_of=swing-bar probe.

    At the swing bar itself, the as-known truth is swing_high_confirmed=False
    (confirmation window not yet complete). The peeking producer returns True.
    """
    case = build_case_swing_confirmation(k=3)
    result = audit_smc_producer(_peeking_producer, case)
    assert result.verdict == FAIL_PEEK, (
        f"peeking producer must FAIL swing_confirmation; got {result.verdict}"
    )


def test_b735_pin4_peeking_producer_fails_dealing_range_reanchor():
    """H2 (Pattern K): peeking producer uses max-of-all-bars which equals the
    LATER swing high -> wrong value at the mid-window probe.
    """
    case = build_case_dealing_range_reanchor(k=3)
    result = audit_smc_producer(_peeking_producer, case)
    assert result.verdict == FAIL_PEEK, (
        f"peeking producer must FAIL dealing_range_reanchor (Pattern K); got {result.verdict}"
    )


def test_b735_pin5_panel_cache_edge_detects_pit_full_disagreement():
    """H3: the auditor compares PIT-mode vs FULL-mode at the same bar. A peeking
    producer returns different values for the two modes -> caught.
    """
    case = build_case_panel_cache_edge(k=3)
    result = audit_smc_producer(_peeking_producer, case)
    assert result.verdict == FAIL_PEEK, (
        f"peeking producer must FAIL panel_cache_edge; got {result.verdict}"
    )


def test_b735_pin6_audit_all_returns_list_of_3_results():
    """audit_all runs every case builder and returns one CaseResult each."""
    results = audit_all(_pit_honest_producer)
    assert len(results) == 3
    assert {r.case_name for r in results} == {
        "swing_confirmation", "dealing_range_reanchor", "panel_cache_edge"
    }


def test_b735_pin7_verdict_constants_exposed():
    """Public API: PASS + FAIL_PEEK verdict constants are importable."""
    assert PASS == "PASS_PIT_CLEAN"
    assert FAIL_PEEK == "FAIL_PEEKED_FUTURE_BARS"
