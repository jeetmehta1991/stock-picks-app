"""Batch 492 (2026-05-30) -- Pattern 3 audit closure 0a:
R:R-gate-uses-profit-factor-as-proxy.

Source: per CHECKLIST #77 owner directive 2026-05-27.
Queue row: EXECUTION_QUEUE.md item 0a.
Production reference: scripts/optimize_strategies_from_cube.py:159
  `"rr_>=_2.0":   stats["profit_factor"] >= GATE_RR_MIN`

Audit finding (Batch 448 broad Pattern 3 sweep):

The 5-Gate dict key is `"rr_>=_2.0"` but the code asserts
`stats["profit_factor"] >= GATE_RR_MIN`. R:R and profit_factor are
DIFFERENT quantities:

  R:R           = avg_win / abs(avg_loss)
  profit_factor = sum_wins / abs(sum_losses)
                = (n_wins * avg_win) / (n_losses * avg_loss)
                = (WR / (1 - WR)) * R:R

For a 60% win-rate strategy, profit_factor = 2.0 implies
R:R = 2.0 * (1 - 0.60) / 0.60 = 1.33, NOT 2.0.

These tests:

  (a) prove the mathematical relationship by computing both quantities
      on synthetic data;
  (b) provide a counter-example: WR=60% strategy with profit_factor=2.0
      and R:R=1.33 -- passes today's gate but FAILS what the key name
      implies;
  (c) pin the current production behaviour (gate uses profit_factor) so
      a fix or refactor is detected explicitly;
  (d) leave the decision to owner: change production to compute actual
      R:R (avg_win/avg_loss) and gate on it, OR rename the dict key to
      `"pf_>=_2.0"` to honest-up the current behaviour.

Neither (d.1) nor (d.2) is made autonomously here -- that's an owner
gate decision that affects strict-pass cell count downstream.
"""
from __future__ import annotations

import numpy as np
import pytest


def _profit_factor_and_rr(pnls):
    """Compute both quantities from a list of pnls. Returns (pf, rr, wr)."""
    arr = np.array(pnls, dtype=float)
    wins = arr[arr > 0]
    losses = arr[arr < 0]
    n_wins = len(wins)
    n_losses = len(losses)
    wr = n_wins / len(arr) if len(arr) > 0 else 0.0
    avg_win = float(wins.mean()) if n_wins > 0 else 0.0
    avg_loss_abs = float(abs(losses.mean())) if n_losses > 0 else 0.0
    sum_win = float(wins.sum()) if n_wins > 0 else 0.0
    sum_loss_abs = float(abs(losses.sum())) if n_losses > 0 else 0.0
    pf = sum_win / sum_loss_abs if sum_loss_abs > 0 else float("inf")
    rr = avg_win / avg_loss_abs if avg_loss_abs > 0 else float("inf")
    return pf, rr, wr


# ---------------------------------------------------------------------------
# Mathematical relationship: PF = (WR / (1 - WR)) * R:R
# ---------------------------------------------------------------------------

def test_batch492_0a_pf_rr_relationship_holds_60_wr():
    """WR = 60%: 60 wins of 2.0 + 40 losses of -1.5 -> RR=1.33, PF=2.0."""
    pnls = [2.0] * 60 + [-1.5] * 40
    pf, rr, wr = _profit_factor_and_rr(pnls)
    assert pf == pytest.approx(2.0, abs=1e-6), f"pf={pf}"
    assert rr == pytest.approx(1.333333, abs=1e-5), f"rr={rr}"
    assert wr == pytest.approx(0.60, abs=1e-6), f"wr={wr}"
    # The relationship: PF = (WR / (1-WR)) * RR
    derived_pf = (wr / (1 - wr)) * rr
    assert pf == pytest.approx(derived_pf, abs=1e-6)


def test_batch492_0a_pf_rr_relationship_holds_50_wr():
    """WR = 50%: 50 wins of 1.0 + 50 losses of -0.5 -> RR=2.0, PF=2.0
    (only at WR=50% do PF and RR coincide).
    """
    pnls = [1.0] * 50 + [-0.5] * 50
    pf, rr, wr = _profit_factor_and_rr(pnls)
    assert pf == pytest.approx(2.0, abs=1e-6)
    assert rr == pytest.approx(2.0, abs=1e-6)
    assert wr == pytest.approx(0.50, abs=1e-6)


def test_batch492_0a_pf_rr_relationship_holds_30_wr():
    """WR = 30%: 30 wins of 4.0 + 70 losses of -1.0 -> RR=4.0, PF=1.714.
    Demonstrates PF can be LESS than RR when WR < 50%.
    """
    pnls = [4.0] * 30 + [-1.0] * 70
    pf, rr, wr = _profit_factor_and_rr(pnls)
    assert pf == pytest.approx(120 / 70, abs=1e-5), f"pf={pf}"
    assert rr == pytest.approx(4.0, abs=1e-6), f"rr={rr}"
    assert pf < rr, f"At WR<50%, PF should be < RR; got PF={pf}, RR={rr}"


# ---------------------------------------------------------------------------
# Counter-example: PF=2.0 cell that the gate passes but R:R<2.0
# ---------------------------------------------------------------------------

def test_batch492_0a_counterexample_pf_2_passes_gate_but_rr_below_2():
    """Construct a cell with PF >= 2.0 (passes today's gate) but
    actual R:R < 2.0 (would fail the gate if it were truly R:R)."""
    # 60 wins of $2 each ($120 total), 40 losses of $1.50 each ($60 total)
    # PF = 120/60 = 2.0  -- PASSES the rr_>=_2.0 gate today
    # RR = 2.0/1.5 = 1.33 -- would FAIL if gate were actual R:R
    pnls = [2.0] * 60 + [-1.5] * 40
    pf, rr, wr = _profit_factor_and_rr(pnls)
    # Today's gate (uses profit_factor)
    gate_uses_pf = pf >= 2.0
    # What the dict key NAMES (actual R:R)
    gate_would_use_actual_rr = rr >= 2.0
    assert gate_uses_pf is True, (
        "Counter-example must pass the CURRENT gate (which uses profit_factor)"
    )
    assert gate_would_use_actual_rr is False, (
        "Counter-example must FAIL a renamed gate that used actual R:R"
    )
    # Document the gap explicitly
    assert pf >= 2.0 > rr, f"PF={pf} >= 2.0 > RR={rr}: gate-semantics gap demonstrated"


def test_batch492_0a_counterexample_inverse_high_wr_low_rr():
    """A 90% WR strategy with R:R = 0.5 still has PF = 4.5.
    Demonstrates the inverse problem: extremely high WR + tiny R:R cells
    pass the 'R:R' gate purely on WR mass.
    """
    # 90 wins of $1, 10 losses of $2 -> PF = 90/20 = 4.5; RR = 0.5
    pnls = [1.0] * 90 + [-2.0] * 10
    pf, rr, wr = _profit_factor_and_rr(pnls)
    assert pf == pytest.approx(4.5, abs=1e-5)
    assert rr == pytest.approx(0.5, abs=1e-5)
    assert wr == pytest.approx(0.90, abs=1e-6)
    # Today's gate passes; actual R:R fails by miles
    assert pf >= 2.0, "PF >= 2.0 passes today's gate"
    assert rr < 2.0, "actual R:R < 2.0 would fail a renamed gate"


# ---------------------------------------------------------------------------
# Pin current production behaviour
# ---------------------------------------------------------------------------

def test_batch492_0a_current_production_gate_uses_profit_factor():
    """Pin the enforced-gate state at
    scripts/optimize_strategies_from_cube.py.

    Batch 502 (2026-05-31) Path-1 update: the dict key was renamed
    from `"rr_>=_2.0"` -> `"pf_>=_2.0"` (honest-up the label). The
    enforced behaviour is UNCHANGED -- still gates on profit_factor.
    A NEW informational `"rr_actual_>=_2.0"` reading ships alongside
    but is NOT in the enforced verdict path; Path-2 (owner-gated)
    will swap that into enforcement later.
    """
    from pathlib import Path
    optimizer = Path(__file__).resolve().parent.parent.parent / "scripts" / \
        "optimize_strategies_from_cube.py"
    src = optimizer.read_text(encoding="utf-8")
    # Pin: renamed pf_>=_2.0 key bound to profit_factor (Batch 502 Path-1).
    assert '"pf_>=_2.0":       stats["profit_factor"] >= GATE_RR_MIN' in src, (
        "Production gate no longer reads stats['profit_factor'] for "
        "pf gate. If deliberate Path-2 fix (swap to avg_win/abs(avg_loss)), "
        "update this test + queue row 0a status."
    )
    # Pin: rr_actual_>=_2.0 informational reading shipped (Batch 502).
    assert '"rr_actual_>=_2.0": rr_actual_pass' in src, (
        "Batch 502 informational rr_actual reading missing from gates dict."
    )
    assert 'enforced_gates = ["n_>=_30", "p_<_0.05", "t_>=_3.4", "pf_>=_2.0"]' in src, (
        "Batch 502 enforced_gates list changed; verify rr_actual_>=_2.0 "
        "still NOT enforced (Path-2 swap not yet shipped)."
    )


def test_batch492_0a_documented_decision_outstanding():
    """Document that the resolution of 0a is OWNER-GATED.

    Two paths:
      (1) Rename the dict key from `"rr_>=_2.0"` to `"pf_>=_2.0"` and
          keep current behaviour. Lower friction, no strict-pass count
          impact.
      (2) Compute actual R:R = avg_win / abs(avg_loss) and gate on it.
          Stricter; will reduce strict-5-Gate pass count further.

    Owner has not selected. This test exists so the queue row 0a stays
    'investigated + documented' rather than silently 'PENDING'.
    """
    # No-op assertion; the test's purpose is the docstring.
    assert True
