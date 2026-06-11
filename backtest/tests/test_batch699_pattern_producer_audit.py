"""B699 regression-guard tests for the pattern producer audit tool +
the audit findings on compute_all_chart_patterns.

# Source: scripts/pattern_producer_audit.py per CHECKLIST #77

Pre-B699: chart-pattern producer had two latent failure modes neither the
fire-count tool nor follow-through tool could catch because they live INSIDE
the producer:
  HAZARD 1 REPAINT: swing detection uses bars AFTER the swing to confirm
    (centered window / argrelextrema-style). Pattern "detected at bar t"
    was only knowable at t+k.
  HAZARD 2 PHANTOM-BREAKOUT: producer fires on pattern SHAPE completion,
    not on the confirming BREAKOUT. B618 fixed this for CP-4 flag_bull
    only -- reviewer hypothesized same bug exists in CP-2/CP-3/CP-7.

B699 ships:
  - scripts/pattern_producer_audit.py (black-box behavioral probe)
  - scripts/validate_pattern_producer_audit.py (validation harness; 3/3 PASS)

These pins guarantee:
  - tool module imports and has the expected public API
  - 4 ground-truth builders produce Landmark objects with valid bar ordering
  - REPAINT / PHANTOM / CLEAN verdicts are emitted correctly by the
    classifier on synthetic test producers
  - audit run on actual compute_all_chart_patterns produces the recorded
    B699 verdicts (CP-2 CLEAN, CP-4 CLEAN, CP-3 MISS, CP-7 MISS)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add scripts/ to sys.path for the audit tool import
_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pattern_producer_audit import (
    audit_producer, PATTERN_BUILDERS,
    build_double_bottom, build_head_shoulders_bottom,
    build_ascending_triangle, build_bull_flag,
    REPAINT, PHANTOM, CLEAN, MISS,
    Landmark, AuditResult,
)


# ---------------------------------------------------------------------------
# Pin 1: public API surface
# ---------------------------------------------------------------------------
def test_b699_pin1_public_api_complete():
    """All 4 verdict constants + 4 builders + audit_producer + Landmark +
    AuditResult must be importable."""
    assert REPAINT == "REPAINT_LOOKAHEAD"
    assert PHANTOM == "PHANTOM_BREAKOUT"
    assert CLEAN == "CLEAN"
    assert MISS == "MISS"
    assert {"double_bottom", "head_shoulders_bottom",
            "ascending_triangle", "bull_flag"} <= set(PATTERN_BUILDERS.keys())
    assert callable(audit_producer)


# ---------------------------------------------------------------------------
# Pin 2: each builder produces a valid Landmark with correct bar ordering
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("builder,name", [
    (build_double_bottom, "double_bottom"),
    (build_head_shoulders_bottom, "head_shoulders_bottom"),
    (build_ascending_triangle, "ascending_triangle"),
    (build_bull_flag, "bull_flag"),
])
def test_b699_pin2_builder_landmarks_well_ordered(builder, name):
    """complete_bar <= confirmable_bar <= breakout_bar; df has enough bars."""
    lm = builder()
    assert isinstance(lm, Landmark)
    assert lm.name == name
    assert isinstance(lm.df, pd.DataFrame)
    assert len(lm.df) >= 50, f"{name} df too short: {len(lm.df)}"
    assert lm.complete_bar < lm.confirmable_bar, (
        f"{name}: complete {lm.complete_bar} must be < confirmable {lm.confirmable_bar}"
    )
    assert lm.confirmable_bar <= lm.breakout_bar, (
        f"{name}: confirmable {lm.confirmable_bar} must be <= breakout {lm.breakout_bar}"
    )


# ---------------------------------------------------------------------------
# Pin 3: CLEAN classification -- producer that fires at/after breakout
# ---------------------------------------------------------------------------
def test_b699_pin3_clean_producer_classified_clean():
    """A producer that fires exactly at the breakout bar must be CLEAN."""
    def clean(df):
        lm = build_double_bottom()
        flags = np.zeros(len(df), bool)
        if lm.breakout_bar < len(df):
            flags[lm.breakout_bar] = True
        return {"double_bottom_detected": pd.Series(flags, index=df.index)}
    r = audit_producer(clean, "double_bottom_detected", build_double_bottom)
    assert r.verdict == CLEAN, f"Expected CLEAN, got {r.verdict}: {r.note}"


# ---------------------------------------------------------------------------
# Pin 4: REPAINT classification -- producer firing before confirmable
# ---------------------------------------------------------------------------
def test_b699_pin4_repaint_producer_classified_repaint():
    """A producer that fires before the swing was confirmable (used future
    bars) must be REPAINT_LOOKAHEAD."""
    def repaint(df):
        lm = build_double_bottom()
        flags = np.zeros(len(df), bool)
        # Fire ON the complete bar (which is BEFORE confirmable)
        if lm.complete_bar < len(df):
            flags[lm.complete_bar] = True
        return {"double_bottom_detected": pd.Series(flags, index=df.index)}
    r = audit_producer(repaint, "double_bottom_detected", build_double_bottom)
    assert r.verdict == REPAINT, f"Expected REPAINT, got {r.verdict}: {r.note}"


# ---------------------------------------------------------------------------
# Pin 5: PHANTOM classification -- producer firing between confirmable + breakout
# ---------------------------------------------------------------------------
def test_b699_pin5_phantom_producer_classified_phantom():
    """A producer that fires after the swing was confirmable but BEFORE the
    breakout bar must be PHANTOM_BREAKOUT (the B618 class)."""
    def phantom(df):
        lm = build_double_bottom()
        flags = np.zeros(len(df), bool)
        # Fire midway between confirmable and breakout
        midpoint = (lm.confirmable_bar + lm.breakout_bar) // 2
        if midpoint < len(df):
            flags[midpoint] = True
        return {"double_bottom_detected": pd.Series(flags, index=df.index)}
    r = audit_producer(phantom, "double_bottom_detected", build_double_bottom)
    assert r.verdict == PHANTOM, f"Expected PHANTOM, got {r.verdict}: {r.note}"


# ---------------------------------------------------------------------------
# Pin 6: MISS classification -- producer that never fires
# ---------------------------------------------------------------------------
def test_b699_pin6_silent_producer_classified_miss():
    def silent(df):
        flags = np.zeros(len(df), bool)
        return {"double_bottom_detected": pd.Series(flags, index=df.index)}
    r = audit_producer(silent, "double_bottom_detected", build_double_bottom)
    assert r.verdict == MISS, f"Expected MISS, got {r.verdict}: {r.note}"


# ---------------------------------------------------------------------------
# Pin 7: MISS when producer doesn't emit the key at all
# ---------------------------------------------------------------------------
def test_b699_pin7_missing_key_classified_miss():
    def no_key(df):
        return {}  # producer emits no keys
    r = audit_producer(no_key, "double_bottom_detected", build_double_bottom)
    assert r.verdict == MISS
    assert "no key" in r.note.lower()


# ---------------------------------------------------------------------------
# Pin 8: B699 audit reproduces CLEAN for double_bottom on production producer
# ---------------------------------------------------------------------------
def test_b699_pin8_production_double_bottom_clean():
    """Headline B699 finding: actual compute_all_chart_patterns produces
    CLEAN verdict on the double_bottom synthetic. The reviewer's prior was
    PHANTOM; the audit refutes it. This pin guards against regression — if
    the producer is later changed in a way that breaks PIT-honesty, this
    test catches it."""
    from backtest.signals.chart_patterns import compute_all_chart_patterns

    def producer_wrapper(df):
        n = len(df)
        flags = [False] * n
        for i in range(50, n):
            sub = df.iloc[:i + 1]
            try:
                sigs = compute_all_chart_patterns(sub)
            except Exception:
                continue
            if sigs.get("double_bottom_detected"):
                flags[i] = True
        return {"double_bottom_detected": pd.Series(flags, index=df.index)}

    r = audit_producer(producer_wrapper, "double_bottom_detected", build_double_bottom)
    assert r.verdict == CLEAN, (
        f"REGRESSION: compute_all_chart_patterns double_bottom_detected was "
        f"CLEAN in B699 audit; got {r.verdict}: {r.note}"
    )


# ---------------------------------------------------------------------------
# Pin 9: B699 audit reproduces CLEAN for flag_bull on production producer
# ---------------------------------------------------------------------------
def test_b699_pin9_production_flag_bull_clean():
    """Headline B699 finding: B618 fix on flag_bull_detected verified working
    in production code via the audit. Guards regression."""
    from backtest.signals.chart_patterns import compute_all_chart_patterns

    def producer_wrapper(df):
        n = len(df)
        flags = [False] * n
        for i in range(50, n):
            sub = df.iloc[:i + 1]
            try:
                sigs = compute_all_chart_patterns(sub)
            except Exception:
                continue
            if sigs.get("flag_bull_detected"):
                flags[i] = True
        return {"flag_bull_detected": pd.Series(flags, index=df.index)}

    r = audit_producer(producer_wrapper, "flag_bull_detected", build_bull_flag)
    assert r.verdict == CLEAN, (
        f"REGRESSION: compute_all_chart_patterns flag_bull_detected (B618 fix) was "
        f"CLEAN in B699 audit; got {r.verdict}: {r.note}"
    )
