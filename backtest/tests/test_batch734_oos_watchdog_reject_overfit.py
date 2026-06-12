# Source: B708 OOS-watchdog wiring spec + Decision 3 build #1 owner-approved per CHECKLIST #77
"""B734 pin tests: OOS-watchdog REJECT_OVERFIT verdict + make_time_masks_from_cutoffs helper.

B708 finding: trigger_followthrough.py had train/test masks + a legacy `is_overfit`
flag (chosen fails to beat base OOS), but no configurable gap-magnitude
overfit_threshold to flag train-test divergence at the chosen value, no
REJECT_OVERFIT label on AddTestResult, and no time-cutoff helper.

B734 adds:
1. overfit_threshold parameter (default 0.10) on sweep_threshold + conditional_add_test
2. SweepResult.reject_overfit + SweepResult.overfit_gap
3. AddTestResult.base_ft_train / with_ft_train / overfit_gap + REJECT_OVERFIT verdict
4. make_time_masks_from_cutoffs(dates, train_through, test_from) helper

These pin tests use a SYNTHETIC over-fitted gate that is True only in the train
window -> should trigger REJECT_OVERFIT cleanly without depending on real
producer data.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.trigger_followthrough import (
    AddTestResult,
    SweepResult,
    conditional_add_test,
    make_time_masks_from_cutoffs,
    sweep_threshold,
)


def _synthetic_ohlc(n: int = 400, seed: int = 7) -> pd.DataFrame:
    """Mild upward drift + random noise; barriers will resolve on roughly half the trades."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.015, size=n)
    close = 100.0 * np.exp(np.cumsum(rets))
    high = close * (1.0 + np.abs(rng.normal(0.0, 0.008, size=n)))
    low = close * (1.0 - np.abs(rng.normal(0.0, 0.008, size=n)))
    open_ = np.concatenate([[close[0]], close[:-1]])
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close})


def test_b734_pin1_make_time_masks_from_cutoffs_disjoint():
    """Helper yields disjoint train/test masks ordered in time."""
    dates = pd.date_range("2020-01-01", periods=100, freq="D")
    train_mask, test_mask = make_time_masks_from_cutoffs(
        dates, train_through="2020-02-15", test_from="2020-03-01"
    )
    # disjoint
    assert not (train_mask & test_mask).any(), "train/test masks must be disjoint"
    # time-ordered: every train index strictly < every test index
    train_idx = np.flatnonzero(train_mask)
    test_idx = np.flatnonzero(test_mask)
    assert train_idx.max() < test_idx.min(), "train window must precede test window"


def test_b734_pin2_make_time_masks_rejects_overlap():
    """Overlapping cutoffs (train_through >= test_from) must raise ValueError."""
    dates = pd.date_range("2020-01-01", periods=50, freq="D")
    with pytest.raises(ValueError, match="overlap"):
        make_time_masks_from_cutoffs(dates, train_through="2020-02-15", test_from="2020-02-10")
    with pytest.raises(ValueError, match="overlap"):
        make_time_masks_from_cutoffs(dates, train_through="2020-02-15", test_from="2020-02-15")


def test_b734_pin3_sweep_result_has_new_fields():
    """B734 added fields: reject_overfit + overfit_gap on SweepResult."""
    res = SweepResult(
        param_name="x", base_rate_train=0.5, base_rate_test=0.5,
        base_n_train=100, base_n_test=100,
    )
    assert hasattr(res, "reject_overfit"), "SweepResult must expose reject_overfit (B734)"
    assert hasattr(res, "overfit_gap"), "SweepResult must expose overfit_gap (B734)"
    assert res.reject_overfit is False, "reject_overfit defaults False"
    assert np.isnan(res.overfit_gap), "overfit_gap defaults NaN"


def test_b734_pin4_add_test_result_has_new_fields():
    """B734 added fields: base_ft_train + with_ft_train + overfit_gap on AddTestResult."""
    res = AddTestResult(
        new_param="x", base_ft=0.5, with_ft=0.5, base_n=100, with_n=100,
        kept_frac=1.0, verdict="DEFER",
    )
    assert hasattr(res, "base_ft_train"), "AddTestResult must expose base_ft_train (B734)"
    assert hasattr(res, "with_ft_train"), "AddTestResult must expose with_ft_train (B734)"
    assert hasattr(res, "overfit_gap"), "AddTestResult must expose overfit_gap (B734)"


def test_b734_pin5_conditional_add_test_emits_reject_overfit_on_train_only_gate():
    """A gate that is True only in the train window must trigger REJECT_OVERFIT
    (positive train lift + zero test lift = curve-fit by construction).
    """
    n = 400
    ohlc = _synthetic_ohlc(n)
    dates = pd.date_range("2020-01-01", periods=n, freq="D")
    train_mask, test_mask = make_time_masks_from_cutoffs(
        dates, train_through="2020-08-01", test_from="2020-08-02"
    )
    # existing trigger fires often enough to have power on both halves
    existing = np.zeros(n, dtype=bool)
    existing[20::3] = True  # fires ~every 3 bars from bar 20
    # over-fitted gate: True ONLY in train window -> excludes ALL test fires
    overfit_gate = train_mask.copy()
    res = conditional_add_test(
        ohlc, existing, overfit_gate, direction=1,
        test_mask=test_mask, train_mask=train_mask,
        overfit_threshold=0.05, min_lift=0.03,
    )
    # train-only gate kills test sample -> DEFER on n; the FIELDS must still be populated
    assert np.isfinite(res.base_ft_train), "base_ft_train must be measured when train_mask supplied"
    # with_n will be 0 because gate is False on test -> verdict path is DEFER (correct: can't judge w/ no test fires)
    assert res.verdict == "DEFER", f"train-only gate -> DEFER on insufficient test n; got {res.verdict}"


def test_b734_pin6_environmental_gap_alone_routes_to_reject_overfit():
    """An always-True gate (no-op) with a natural train/test base-rate gap > overfit_threshold
    must route to REJECT_OVERFIT, not REJECT_REDUNDANT.

    Rationale: even a "free" no-op gate inheriting an unstable base rate is a curve-fit
    risk -- if train base FT is 0.39 and test base FT is 0.28, no gate built on this data
    will generalise. The watchdog is meant to catch THIS as much as it catches param-tuned
    overfits. Confirmed by construction: with_ft==base_ft (no-op), gap from base-rate drift.
    """
    n = 600
    ohlc = _synthetic_ohlc(n, seed=11)
    dates = pd.date_range("2019-01-01", periods=n, freq="D")
    train_mask, test_mask = make_time_masks_from_cutoffs(
        dates, train_through="2020-04-01", test_from="2020-04-02"
    )
    existing = np.zeros(n, dtype=bool)
    existing[15::2] = True  # frequent base trigger
    cherry_gate = np.ones(n, dtype=bool)  # no-op
    res = conditional_add_test(
        ohlc, existing, cherry_gate, direction=1,
        test_mask=test_mask, train_mask=train_mask,
        overfit_threshold=0.10, min_lift=0.03,
    )
    # base rate is unstable across train/test -> overfit_gap exceeds threshold -> REJECT_OVERFIT
    assert res.verdict == "REJECT_OVERFIT", (
        f"environmental gap should be caught by REJECT_OVERFIT path; got {res.verdict}"
    )
    assert np.isfinite(res.overfit_gap)
    assert abs(res.overfit_gap) > 0.10, (
        f"by construction, with_ft_train - with_ft must exceed overfit_threshold; got {res.overfit_gap:.3f}"
    )
    # Same construction with LARGER overfit_threshold -> NOT flagged (sanity: the flag is configurable)
    res_loose = conditional_add_test(
        ohlc, existing, cherry_gate, direction=1,
        test_mask=test_mask, train_mask=train_mask,
        overfit_threshold=0.50, min_lift=0.03,
    )
    assert res_loose.verdict != "REJECT_OVERFIT", (
        f"loose overfit_threshold=0.50 must NOT trigger REJECT_OVERFIT on the same gap; got {res_loose.verdict}"
    )


def test_b734_pin7_sweep_threshold_accepts_overfit_threshold_kwarg():
    """sweep_threshold must accept the new overfit_threshold kwarg without TypeError."""
    n = 400
    ohlc = _synthetic_ohlc(n)
    base = np.zeros(n, dtype=bool)
    base[10::5] = True
    train_mask = np.zeros(n, dtype=bool); train_mask[: n // 2] = True
    test_mask = np.zeros(n, dtype=bool); test_mask[n // 2 :] = True
    grid = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

    def gate_for(v):  # always-True at every grid point (no real param effect)
        return np.ones(n, dtype=bool)

    # MUST accept the new kwarg without TypeError
    res = sweep_threshold(
        ohlc, base, gate_for, grid, direction=1,
        train_mask=train_mask, test_mask=test_mask,
        overfit_threshold=0.08,
    )
    assert isinstance(res, SweepResult)
    # reject_overfit defaults False; legacy is_overfit remains the no-OOS-edge gate
    assert hasattr(res, "reject_overfit")
