"""B700 regression-guard tests for the 6 additional pattern builders +
expanded chart_patterns.py audit results.

# Source: scripts/pattern_producer_audit.py per CHECKLIST #77

B700 adds builders for: cup_and_handle, double_top, head_shoulders_top,
descending_triangle, bear_flag, inverted_cup_and_handle. Then re-runs the
black-box audit on all 13 remaining keys of compute_all_chart_patterns to
extend the B699 coverage from 4/17 to 17/17.

Headline B700 findings (additional to B699):
  - double_top_detected -> CLEAN (short mirror of CP-2 also PIT-honest)
  - flag_bull_broke + flag_bull_break_retest_long -> CLEAN (B618 + B607 verified for retest variants)
  - flag_bear_broke + flag_bear_break_retest_short -> CLEAN (short mirrors verified)
  - cup_handle_detected (CP-1) + cup_handle_neckline_break_retest_long (CP-9) -> MISS
  - head_shoulders_top + inverted_cup_handle -> MISS (short mirrors)
  - triangle_descending + triangle_symmetric + triangle_apex_break_retest_long -> MISS

The MISS pattern strongly suggests: complex multi-swing pattern detection
in compute_all_chart_patterns has thresholds calibrated for real-data
geometry that the textbook synthetic doesn't reproduce. Whether MISS means
"detection too strict" or "real fire-starvation" depends on whether the
B689 re-run produces nonzero fire counts for these patterns -- which then
themselves need PIT-cleanliness verification on the real-data fires.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pattern_producer_audit import (
    audit_producer, PATTERN_BUILDERS,
    build_cup_and_handle, build_double_top, build_head_shoulders_top,
    build_descending_triangle, build_bear_flag, build_inverted_cup_and_handle,
    CLEAN, MISS, Landmark,
)


# ---------------------------------------------------------------------------
# Pin 1: B700 builders are registered + Landmark-valid
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", [
    "cup_and_handle", "double_top", "head_shoulders_top",
    "descending_triangle", "bear_flag", "inverted_cup_and_handle",
])
def test_b700_pin1_builders_registered_and_valid(name):
    assert name in PATTERN_BUILDERS
    lm = PATTERN_BUILDERS[name]()
    assert isinstance(lm, Landmark)
    assert lm.name == name
    assert len(lm.df) >= 50
    assert lm.complete_bar < lm.confirmable_bar
    assert lm.confirmable_bar <= lm.breakout_bar


# ---------------------------------------------------------------------------
# Pin 2: B700 production audit -- double_top CLEAN (short mirror of CP-2)
# ---------------------------------------------------------------------------
def test_b700_pin2_production_double_top_clean():
    from backtest.signals.chart_patterns import compute_all_chart_patterns

    def producer(df):
        n = len(df)
        flags = [False] * n
        for i in range(50, n):
            sub = df.iloc[:i + 1]
            try:
                sigs = compute_all_chart_patterns(sub)
            except Exception:
                continue
            if sigs.get("double_top_detected"):
                flags[i] = True
        return {"double_top_detected": pd.Series(flags, index=df.index)}

    r = audit_producer(producer, "double_top_detected", build_double_top)
    assert r.verdict == CLEAN, f"double_top regression: {r.verdict}: {r.note}"


# ---------------------------------------------------------------------------
# Pin 3: B700 production audit -- flag_bull_broke CLEAN (B618 fix verified)
# ---------------------------------------------------------------------------
def test_b700_pin3_production_flag_bull_broke_clean():
    from pattern_producer_audit import build_bull_flag
    from backtest.signals.chart_patterns import compute_all_chart_patterns

    def producer(df):
        n = len(df)
        flags = [False] * n
        for i in range(50, n):
            sub = df.iloc[:i + 1]
            try:
                sigs = compute_all_chart_patterns(sub)
            except Exception:
                continue
            if sigs.get("flag_bull_broke"):
                flags[i] = True
        return {"flag_bull_broke": pd.Series(flags, index=df.index)}

    r = audit_producer(producer, "flag_bull_broke", build_bull_flag)
    assert r.verdict == CLEAN, f"flag_bull_broke (B618 fix) regression: {r.verdict}: {r.note}"


# ---------------------------------------------------------------------------
# Pin 4: B700 production audit -- flag_bear_broke CLEAN (short mirror)
# ---------------------------------------------------------------------------
def test_b700_pin4_production_flag_bear_broke_clean():
    from backtest.signals.chart_patterns import compute_all_chart_patterns

    def producer(df):
        n = len(df)
        flags = [False] * n
        for i in range(50, n):
            sub = df.iloc[:i + 1]
            try:
                sigs = compute_all_chart_patterns(sub)
            except Exception:
                continue
            if sigs.get("flag_bear_broke"):
                flags[i] = True
        return {"flag_bear_broke": pd.Series(flags, index=df.index)}

    r = audit_producer(producer, "flag_bear_broke", build_bear_flag)
    assert r.verdict == CLEAN, f"flag_bear_broke regression: {r.verdict}: {r.note}"


# ---------------------------------------------------------------------------
# Pin 5: B700 production audit -- flag_bull_break_retest_long CLEAN (B607 fix)
# ---------------------------------------------------------------------------
def test_b700_pin5_production_flag_bull_break_retest_long_clean():
    from pattern_producer_audit import build_bull_flag
    from backtest.signals.chart_patterns import compute_all_chart_patterns

    def producer(df):
        n = len(df)
        flags = [False] * n
        for i in range(50, n):
            sub = df.iloc[:i + 1]
            try:
                sigs = compute_all_chart_patterns(sub)
            except Exception:
                continue
            if sigs.get("flag_bull_break_retest_long"):
                flags[i] = True
        return {"flag_bull_break_retest_long": pd.Series(flags, index=df.index)}

    r = audit_producer(producer, "flag_bull_break_retest_long", build_bull_flag)
    assert r.verdict == CLEAN, f"flag_bull_break_retest_long (B607 fix) regression: {r.verdict}: {r.note}"


# ---------------------------------------------------------------------------
# Pin 6: PATTERN_BUILDERS dict has exactly 10 entries (4 B699 + 6 B700)
# ---------------------------------------------------------------------------
def test_b700_pin6_builders_count():
    assert len(PATTERN_BUILDERS) == 10, (
        f"Expected 10 builders (4 B699 + 6 B700), got {len(PATTERN_BUILDERS)}"
    )
    expected = {
        "double_bottom", "head_shoulders_bottom", "ascending_triangle", "bull_flag",
        "cup_and_handle", "double_top", "head_shoulders_top",
        "descending_triangle", "bear_flag", "inverted_cup_and_handle",
    }
    assert set(PATTERN_BUILDERS.keys()) == expected
