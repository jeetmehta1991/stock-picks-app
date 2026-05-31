"""Batch 506 (2026-05-31) -- 0a Path-2 enforcement swap tests.

Source: per CHECKLIST #77 + owner directive 2026-05-31.
Queue row: EXECUTION_QUEUE.md item 0a Path-2 SWAP.

Path-2 ships: swap the enforced 5-Gate position from `pf_>=_2.0` to
`rr_actual_>=_2.0` (actual R:R = avg_win / abs(avg_loss)). The pf
reading remains in the gates dict as informational only.

Behavior under Path-2:
  - Cells with PF >= 2.0 but actual R:R < 2.0 (the Batch 492
    counter-example pattern) now FAIL verdict.
  - Cells with PF < 2.0 but actual R:R >= 2.0 (rare; requires WR > 50%
    + very small avg_loss with low n_losses) now PASS the rr gate
    (verdict driven by other enforced gates).
  - For most data: PF and R:R correlate, so PASS/FAIL outcomes look
    similar; the swap surfaces previously-hidden false positives.
"""
from __future__ import annotations

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Enforced gate list: rr_actual_>=_2.0 is NOW the 4th enforced gate
# ---------------------------------------------------------------------------

def test_batch506_enforced_gates_swap_present_in_source():
    """Pin the swap in scripts/optimize_strategies_from_cube.py source."""
    from pathlib import Path
    optimizer = Path(__file__).resolve().parent.parent.parent / "scripts" / \
        "optimize_strategies_from_cube.py"
    src = optimizer.read_text(encoding="utf-8")
    # Enforced list must include rr_actual + exclude pf
    assert ('enforced_gates = ["n_>=_30", "p_<_0.05", "t_>=_3.4", '
            '"rr_actual_>=_2.0"]') in src
    # Make sure the old enforced list is GONE
    assert ('enforced_gates = ["n_>=_30", "p_<_0.05", "t_>=_3.4", '
            '"pf_>=_2.0"]') not in src


def test_batch506_both_gates_present_in_gates_dict():
    """Both gates still in gates dict (pf as informational)."""
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict
    pnls = pd.Series([2.0]*60 + [-1.0]*40, dtype=float)
    stats = _cell_stats(pnls)
    v = _dec426_verdict(stats, m_total_candidates=1)
    assert "pf_>=_2.0" in v["gates"]
    assert "rr_actual_>=_2.0" in v["gates"]


# ---------------------------------------------------------------------------
# Counter-example: PF passes, R:R fails -> verdict now FAILS
# ---------------------------------------------------------------------------

def test_batch506_pf_passes_rr_fails_cell_fails_verdict():
    """The Batch 492 counter-example: WR=60% with PF=2.0 + R:R=1.33.

    Under Path-1: verdict=PASS (PF enforced).
    Under Path-2: verdict=FAIL (R:R enforced; 1.33 < 2.0).
    """
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict
    # 60 wins @ $2, 40 losses @ $1.50 -> PF=120/60=2.0, RR=1.333
    pnls = pd.Series([2.0]*60 + [-1.5]*40, dtype=float)
    stats = _cell_stats(pnls)
    v = _dec426_verdict(stats, m_total_candidates=1)
    assert v["gates"]["pf_>=_2.0"] is True
    assert v["gates"]["rr_actual_>=_2.0"] is False
    assert v["verdict"] == "FAIL", "Path-2 must FAIL when R:R < 2.0"


def test_batch506_high_wr_low_rr_inverse_counter_example_fails():
    """Batch 492 inverse: 90% WR + R:R=0.5 + PF=4.5.

    Under Path-1: verdict=PASS (PF=4.5 enforced).
    Under Path-2: verdict=FAIL (R:R=0.5 enforced).
    """
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict
    pnls = pd.Series([1.0]*90 + [-2.0]*10, dtype=float)
    stats = _cell_stats(pnls)
    v = _dec426_verdict(stats, m_total_candidates=1)
    assert v["gates"]["pf_>=_2.0"] is True
    assert v["gates"]["rr_actual_>=_2.0"] is False
    assert v["verdict"] == "FAIL", (
        "Path-2 must reject the high-WR-low-R:R inverse counter-example"
    )


# ---------------------------------------------------------------------------
# Both pass / both fail symmetric cases
# ---------------------------------------------------------------------------

def test_batch506_both_pf_and_rr_pass_cell_can_pass_verdict():
    """When both PF >= 2.0 AND R:R >= 2.0, the cell can pass verdict
    (subject to the other enforced gates)."""
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict
    # 50 wins @ $3, 50 losses @ $1.0 -> PF=150/50=3.0, RR=3.0
    pnls = pd.Series([3.0]*50 + [-1.0]*50, dtype=float)
    stats = _cell_stats(pnls)
    v = _dec426_verdict(stats, m_total_candidates=1)
    assert v["gates"]["pf_>=_2.0"] is True
    assert v["gates"]["rr_actual_>=_2.0"] is True


def test_batch506_both_pf_and_rr_fail_cell_fails_verdict():
    """When neither gate passes, verdict still FAIL (n + t + p enforced
    additionally but cell can't recover)."""
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict
    # 30 wins @ $0.5, 70 losses @ $1.0 -> PF=15/70=0.21, RR=0.5
    pnls = pd.Series([0.5]*30 + [-1.0]*70, dtype=float)
    stats = _cell_stats(pnls)
    v = _dec426_verdict(stats, m_total_candidates=1)
    assert v["gates"]["pf_>=_2.0"] is False
    assert v["gates"]["rr_actual_>=_2.0"] is False
    assert v["verdict"] == "FAIL"


# ---------------------------------------------------------------------------
# Insufficient sample short-circuit unchanged
# ---------------------------------------------------------------------------

def test_batch506_insufficient_sample_short_circuits():
    """n < 30 still returns INSUFFICIENT_SAMPLE regardless of Path-2 swap."""
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict
    pnls = pd.Series([2.0]*10, dtype=float)
    stats = _cell_stats(pnls)
    v = _dec426_verdict(stats, m_total_candidates=1)
    assert v["verdict"] == "INSUFFICIENT_SAMPLE"
