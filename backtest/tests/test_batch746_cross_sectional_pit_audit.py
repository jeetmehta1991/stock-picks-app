# Source: B690 revised step 2 (B746) + owner critique "single most likely lookahead vector" + Decision 5 Cat 1 per CHECKLIST #77
"""B746 pin tests: cross_sectional PIT-invariance audit.

PIT-invariance probe: rank computation across the full universe per bar is
the single most likely place in the harness to introduce lookahead. Output
is a number; contamination is invisible.

These pins:
1. Verify the LIVE production producer (`compute_cross_sectional_features`)
   passes all 3 hazard cases (H1 future-bar leak, H2 universe-membership leak,
   H3 asymmetric slice).
2. Verify the audit demonstrably CATCHES a synthetic peeking producer that
   uses future bars (sanity guard: a PASS on live means something).

Failure mode if any pin fails: cluster routes to DO-NOT-DEPLOY pending fix;
B751 wireup SKIPPED (per the revised B746 queue ticket).
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from scripts.cross_sectional_pit_audit import (
    CASE_BUILDERS,
    FAIL_LEAK,
    FAIL_UNIVERSE,
    PASS,
    audit_all,
    audit_producer,
    build_h1_future_bar_leak,
    build_h2_universe_membership_leak,
    build_h3_asymmetric_slice,
)


# -------------------------------------------------------------------------
# Pin 1: live producer passes all 3 cases
# -------------------------------------------------------------------------
def test_b746_pin1_live_producer_passes_all_cases():
    """The LIVE production `compute_cross_sectional_features` must PASS every
    PIT-invariance case. Per the revised B746 queue ticket: FAIL routes the
    cluster to DO-NOT-DEPLOY + B751 wireup SKIPPED.
    """
    results = audit_all()
    fails = [r for r in results if r.verdict != PASS]
    assert not fails, (
        f"cross_sectional PIT-invariance audit FAILED on {len(fails)} case(s):\n"
        + "\n".join(f"  [{r.hazard}] {r.case_name} -> {r.verdict}: {r.note}" for r in fails)
    )


def test_b746_pin2_three_cases_registered():
    """The 3 hazard cases (H1/H2/H3) must all be present in CASE_BUILDERS."""
    assert set(CASE_BUILDERS.keys()) == {
        "h1_future_bar_leak",
        "h2_universe_membership_leak",
        "h3_asymmetric_slice",
    }


# -------------------------------------------------------------------------
# Pin 3: synthetic peeking producer is CAUGHT (sanity guard)
# -------------------------------------------------------------------------
def _peeking_producer(ohlcv_dict: dict, as_of: date) -> dict:
    """Deliberately PIT-VIOLATING producer: uses each ticker's FULL price
    history (incl. bars beyond as_of) instead of slicing to as_of. The
    invariance audit MUST detect this.
    """
    out: dict = {}
    for ticker, df in ohlcv_dict.items():
        if df is None or df.empty or "close" not in df.columns:
            continue
        # NO PIT-slicing! Use the full series including future bars.
        closes = df["close"].astype(float)
        if len(closes) < 50:
            continue
        # Compute a return-based factor on the FULL series (future bars leak).
        last_50 = closes.tail(50)
        out[ticker] = {
            "leaky_factor": round(float(last_50.pct_change().mean()), 6),
        }
    return out


def test_b746_pin3_synthetic_peeking_producer_caught_h1():
    """The audit must FAIL the H1 future-bar leak case against the peeking
    producer (sanity: the PASS verdict on live producer is meaningful only
    if the audit demonstrably catches the violation it's designed to catch).
    """
    case = build_h1_future_bar_leak()
    result = audit_producer(_peeking_producer, case)
    assert result.verdict == FAIL_LEAK, (
        f"expected FAIL_LEAK on peeking producer; got {result.verdict}: {result.note}"
    )
    assert len(result.diffs) > 0


def test_b746_pin4_synthetic_peeking_producer_caught_h3():
    """The audit must FAIL the H3 asymmetric-slice case against the peeking
    producer.
    """
    case = build_h3_asymmetric_slice()
    result = audit_producer(_peeking_producer, case)
    assert result.verdict == FAIL_LEAK, (
        f"expected FAIL_LEAK on peeking producer for H3; got {result.verdict}"
    )


# -------------------------------------------------------------------------
# Pin 5: synthetic universe-leaker is CAUGHT
# -------------------------------------------------------------------------
def _universe_leaker_producer(ohlcv_dict: dict, as_of: date) -> dict:
    """Deliberately UNIVERSE-VIOLATING producer: includes ALL tickers in the
    output dict, even those whose data starts AFTER as_of. PIT-honest
    producer must exclude such tickers from the universe entirely.
    """
    out: dict = {}
    for ticker, df in ohlcv_dict.items():
        if df is None or df.empty:
            continue
        # Pretend every ticker has a factor, ignoring as_of bounds entirely
        out[ticker] = {"universe_member": True}
    return out


def test_b746_pin5_universe_leaker_caught_h2():
    """H2 case: a deliberately-bad producer that includes a not-yet-IPO'd
    ticker must FAIL the universe-membership audit.
    """
    case = build_h2_universe_membership_leak()
    result = audit_producer(_universe_leaker_producer, case)
    assert result.verdict == FAIL_UNIVERSE, (
        f"expected FAIL_UNIVERSE on universe leaker; got {result.verdict}"
    )
    assert "IPO_NEW" in result.universe_leaks


# -------------------------------------------------------------------------
# Pin 6: PIT-clean synthetic producer PASSES
# -------------------------------------------------------------------------
def _clean_producer(ohlcv_dict: dict, as_of: date) -> dict:
    """PIT-honest reference producer: slices each ticker to as_of FIRST, then
    computes a simple factor. Used as a positive-control sanity check.
    """
    out: dict = {}
    for ticker, df in ohlcv_dict.items():
        if df is None or df.empty or "close" not in df.columns:
            continue
        if hasattr(df.index, "date"):
            sliced = df[df.index.date <= as_of]
        else:
            sliced = df[df.index <= as_of]
        if len(sliced) < 50:
            continue
        last_50 = sliced["close"].astype(float).tail(50)
        out[ticker] = {
            "clean_factor": round(float(last_50.pct_change().mean()), 6),
        }
    return out


def test_b746_pin6_clean_synthetic_producer_passes_all_cases():
    """Positive control: a PIT-honest synthetic producer must pass all 3 cases."""
    for builder in CASE_BUILDERS.values():
        case = builder()
        result = audit_producer(_clean_producer, case)
        assert result.verdict == PASS, (
            f"clean synthetic producer should PASS {case.name}; got {result.verdict}: {result.note}"
        )
