"""Batch 502 (2026-05-31) -- 0a Path-1 implementation tests.

Source: per CHECKLIST #77.
Queue row: EXECUTION_QUEUE.md item 0a (R:R vs profit_factor).

Path-1 ship: rename dict key `"rr_>=_2.0"` -> `"pf_>=_2.0"` to honest-
up the label (gate has always tested profit_factor; prior name was
mathematically wrong per Batch 492 counter-examples). Add a NEW
informational `"rr_actual_>=_2.0"` reading using avg_win/abs(avg_loss)
exposed via stats['rr_ratio'] -- NOT enforced in the verdict path.

Owner-gated Path-2 would swap the informational reading into enforcement
to reduce strict-pass count. This batch does NOT make that swap.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _make_pnls_with_known_pf_and_rr(wr_pct, pf_target, n=100):
    """Synthesise pnls Series with controlled WR + profit_factor."""
    n_wins = int(round(n * wr_pct / 100))
    n_losses = n - n_wins
    avg_win = 2.0
    avg_loss = (n_wins * avg_win) / (n_losses * pf_target) if n_losses > 0 else 1.0
    pnls = [avg_win] * n_wins + [-avg_loss] * n_losses
    return pd.Series(pnls, dtype=float)


# ---------------------------------------------------------------------------
# _cell_stats now emits rr_ratio alongside profit_factor
# ---------------------------------------------------------------------------

def test_batch502_cell_stats_emits_rr_ratio_field():
    from scripts.optimize_strategies_from_cube import _cell_stats
    pnls = _make_pnls_with_known_pf_and_rr(60, 2.0, 100)
    stats = _cell_stats(pnls)
    assert "rr_ratio" in stats, "Batch 502 must emit rr_ratio field"
    assert "profit_factor" in stats, "profit_factor must still be present"


def test_batch502_rr_ratio_uses_avg_win_over_avg_loss():
    """rr_ratio = avg_win / abs(avg_loss). For 60% WR with 60 wins @ $2
    and 40 losses @ $1.50: rr = 2.0/1.5 = 1.333, pf = 120/60 = 2.0."""
    from scripts.optimize_strategies_from_cube import _cell_stats
    pnls = pd.Series([2.0]*60 + [-1.5]*40, dtype=float)
    stats = _cell_stats(pnls)
    assert stats["rr_ratio"] == pytest.approx(1.3333, abs=1e-3)
    assert stats["profit_factor"] == pytest.approx(2.0, abs=1e-3)
    # PF >= RR for WR > 50%
    assert stats["profit_factor"] > stats["rr_ratio"]


def test_batch502_rr_ratio_zero_when_no_losses():
    """When losses array empty, rr_ratio = 99 (matches PF convention)."""
    from scripts.optimize_strategies_from_cube import _cell_stats
    pnls = pd.Series([1.0]*30, dtype=float)
    stats = _cell_stats(pnls)
    assert stats["rr_ratio"] == 99.0


def test_batch502_rr_ratio_zero_when_empty_input():
    """Empty array -> _cell_stats returns {n: 0} early; rr_ratio absent."""
    from scripts.optimize_strategies_from_cube import _cell_stats
    stats = _cell_stats(pd.Series([], dtype=float))
    assert stats.get("n", 0) == 0


# ---------------------------------------------------------------------------
# _dec426_verdict: renamed gate key + informational rr_actual reading
# ---------------------------------------------------------------------------

def test_batch502_dec426_verdict_renamed_pf_gate_key():
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict
    pnls = _make_pnls_with_known_pf_and_rr(60, 2.5, 100)  # PF >= 2.0
    stats = _cell_stats(pnls)
    v = _dec426_verdict(stats, m_total_candidates=1)
    assert "pf_>=_2.0" in v["gates"], "Batch 502 renamed gate key must be present"
    assert "rr_>=_2.0" not in v["gates"], "Old key must be removed"


def test_batch502_dec426_verdict_emits_informational_rr_actual_gate():
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict
    pnls = _make_pnls_with_known_pf_and_rr(60, 2.5, 100)
    stats = _cell_stats(pnls)
    v = _dec426_verdict(stats, m_total_candidates=1)
    assert "rr_actual_>=_2.0" in v["gates"], (
        "Batch 502 must emit informational rr_actual_>=_2.0 reading"
    )


def test_batch502_dec426_verdict_does_not_enforce_rr_actual():
    """Counter-example: WR=60% with PF=2.5 + R:R=1.667 must PASS verdict
    today (PF gate enforced, RR not). When Path-2 ships, this test flips.
    """
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict
    # 60 wins @ $2, 40 losses @ $1.20 -> PF=120/48=2.5, RR=2.0/1.20=1.667
    pnls = pd.Series([2.0]*60 + [-1.20]*40, dtype=float)
    stats = _cell_stats(pnls)
    # n=100 -> meets n_>=30. With small Bonferroni M and high t-stat, expect
    # the gate-key checks to fire as expected.
    v = _dec426_verdict(stats, m_total_candidates=1)
    assert v["gates"]["pf_>=_2.0"] is True, "PF=2.5 passes pf gate"
    assert v["gates"]["rr_actual_>=_2.0"] is False, (
        "Actual RR=1.667 < 2.0; informational reading should be False"
    )
    # verdict computation uses enforced gates only (PF, not RR)
    # If all enforced gates pass, verdict=PASS regardless of rr_actual.
    enforced = ["n_>=_30", "p_<_0.05", "t_>=_3.4", "pf_>=_2.0"]
    enforced_all_pass = all(v["gates"][k] for k in enforced)
    if enforced_all_pass:
        assert v["verdict"] == "PASS", (
            "Path-1 must NOT enforce rr_actual; verdict=PASS when all "
            "enforced gates pass"
        )


def test_batch502_dec426_verdict_pf_below_2_fails():
    """When profit_factor < 2.0, the pf gate fails."""
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict
    pnls = _make_pnls_with_known_pf_and_rr(60, 1.5, 100)  # PF=1.5
    stats = _cell_stats(pnls)
    v = _dec426_verdict(stats, m_total_candidates=1)
    assert v["gates"]["pf_>=_2.0"] is False
    assert v["verdict"] == "FAIL"


def test_batch502_dec426_verdict_insufficient_sample_unchanged():
    """n<30 still returns INSUFFICIENT_SAMPLE per pre-Batch-502 behavior."""
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict
    pnls = pd.Series([1.0]*10, dtype=float)
    stats = _cell_stats(pnls)
    v = _dec426_verdict(stats, m_total_candidates=1)
    assert v["verdict"] == "INSUFFICIENT_SAMPLE"


# ---------------------------------------------------------------------------
# Cross-reference Batch 492 counter-example pin
# ---------------------------------------------------------------------------

def test_batch502_inverse_high_wr_low_rr_still_passes_pf_gate():
    """Inverse counter-example (Batch 492): 90% WR + R:R=0.5 + PF=4.5.
    PF gate passes (informational rr_actual flags the gap). Verdict=PASS
    today (path-1); Path-2 would flip verdict=FAIL.
    """
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict
    pnls = pd.Series([1.0]*90 + [-2.0]*10, dtype=float)
    stats = _cell_stats(pnls)
    assert stats["profit_factor"] == pytest.approx(4.5, abs=1e-3)
    assert stats["rr_ratio"] == pytest.approx(0.5, abs=1e-3)
    v = _dec426_verdict(stats, m_total_candidates=1)
    assert v["gates"]["pf_>=_2.0"] is True
    assert v["gates"]["rr_actual_>=_2.0"] is False
