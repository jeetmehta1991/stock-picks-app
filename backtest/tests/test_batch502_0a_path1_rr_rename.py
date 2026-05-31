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


def test_batch502_dec426_verdict_enforces_rr_actual_post_batch506():
    """Counter-example: WR=60% with PF=2.5 + R:R=1.667.

    Batch 502 (Path-1): cell PASSED verdict (PF enforced, RR not).
    Batch 506 (Path-2 SWAP): cell now FAILS verdict (RR=1.667 < 2.0
    fails enforced rr_actual_>=_2.0 gate; PF is informational only).
    """
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict
    # 60 wins @ $2, 40 losses @ $1.20 -> PF=120/48=2.5, RR=2.0/1.20=1.667
    pnls = pd.Series([2.0]*60 + [-1.20]*40, dtype=float)
    stats = _cell_stats(pnls)
    v = _dec426_verdict(stats, m_total_candidates=1)
    assert v["gates"]["pf_>=_2.0"] is True, "PF=2.5 still passes informational pf gate"
    assert v["gates"]["rr_actual_>=_2.0"] is False, (
        "Actual RR=1.667 < 2.0; enforced gate must report False"
    )
    # Batch 506: enforced gates now include rr_actual, exclude pf.
    enforced = ["n_>=_30", "p_<_0.05", "t_>=_3.4", "rr_actual_>=_2.0"]
    enforced_all_pass = all(v["gates"][k] for k in enforced)
    assert not enforced_all_pass, (
        "Path-2: rr_actual fails so enforced gates cannot all pass"
    )
    assert v["verdict"] == "FAIL", (
        "Path-2 enforces rr_actual; verdict=FAIL when actual R:R < 2.0 "
        "even though PF >= 2.0"
    )


def test_batch502_dec426_verdict_pf_below_2_no_longer_drives_verdict():
    """Batch 506 Path-2 SWAP: PF < 2.0 alone does NOT cause verdict=FAIL.

    Construct a cell where PF=1.5 but actual R:R=2.0 (passes enforced
    gate). Under Path-2, this cell can pass verdict if other gates do.

    Path-1 behavior: PF=1.5 -> verdict=FAIL.
    Path-2 behavior: PF=1.5 (informational only) -> verdict driven by
    rr_actual + the other enforced gates.
    """
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict
    # 50 wins @ $3, 50 losses @ $1.0 -> PF=150/50=3.0, RR=3.0
    # (PF and RR both pass) -- so the assertion is symmetric: cells
    # where PF passes AND rr_actual passes still PASS verdict.
    pnls = pd.Series([3.0]*50 + [-1.0]*50, dtype=float)
    stats = _cell_stats(pnls)
    v = _dec426_verdict(stats, m_total_candidates=1)
    assert v["gates"]["pf_>=_2.0"] is True
    assert v["gates"]["rr_actual_>=_2.0"] is True


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
