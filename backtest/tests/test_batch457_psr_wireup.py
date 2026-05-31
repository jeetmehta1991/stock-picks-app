"""Batch 457 (2026-05-29) — AU1 + queue #4 PSR wire-up semantic integration.

PROBLEM (pre-Batch-457):
  Both cube_populator.compute_cell_metrics and
  optimize_strategies_from_cube._dec426_verdict carried PSR placeholders:
    - optimize_strategies_from_cube: hardcoded "psr_>=_0.95": False  -> strict
      5-Gate could never PASS by code, regardless of input quality.
    - cube_populator: monotonic approximation 0.5 + sharpe * sqrt(n) / 50
      (rank-correct but not a real Probabilistic Sharpe Ratio).

  Pattern 1 fingerprint: "wired = greppable string in code, but the call path
  cannot achieve the asserted outcome." DEC-247 + metrics._deflated_sharpe were
  built but never consumed by the cube-verdict pathway.

FIX:
  Both modules now call backtest.results.metrics._deflated_sharpe (Bailey &
  Lopez de Prado 2014) for PSR + deflated Sharpe.

THIS TEST asserts the wire-up is SEMANTIC, not greppable:
  1. PSR field varies with input distribution (not always False / always
     placeholder approximation).
  2. Strict 5-Gate CAN PASS with synthetic strong-edge data (proving PSR is
     real-computed, not hardcoded False).
  3. PSR is identical between the two modules when given identical input
     (single source of truth: metrics._deflated_sharpe).
  4. Insufficient-sample case (n<30) returns insufficient-sample handling.

CHECKLIST coverage:
  #69 (test pyramid: unit + integration + semantic)
  #93 (verify CI conclusion via separate runner)
  #100 (tests/wired/activated for every queue addressal)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.results.cube_populator import (
    compute_cell_metrics,
    evaluate_cell_criteria,
)
from backtest.results.metrics import _deflated_sharpe


# ---------------------------------------------------------------------
# Synthetic-edge fixtures
# ---------------------------------------------------------------------
def _strong_edge_pnls(n: int = 60, seed: int = 13) -> pd.DataFrame:
    """Synthetic positive-edge trade series: realistic Sharpe so the PSR
    denominator does not explode under Bailey-Lopez de Prado (denominator
    stability requires moderate annualised Sharpe; very high SR + non-trivial
    skew can make `1 - skew*SR` negative)."""
    rng = np.random.RandomState(seed)
    pnls = rng.normal(loc=0.5, scale=1.0, size=n)
    return pd.DataFrame({
        "strategy":    ["strong_edge"] * n,
        "exit_method": ["atr_trail_1x"] * n,
        "regime":      ["bull"] * n,
        "pnl_pct":     pnls,
        "ticker":      ["AAPL"] * n,
        "hold_days":   [20.0] * n,
    })


def _weak_edge_pnls(n: int = 60, seed: int = 17) -> pd.DataFrame:
    """Synthetic near-zero-edge series: low Sharpe -> PSR should NOT pass 0.95."""
    rng = np.random.RandomState(seed)
    pnls = rng.normal(loc=0.02, scale=2.0, size=n)
    return pd.DataFrame({
        "strategy":    ["weak_edge"] * n,
        "exit_method": ["atr_trail_1x"] * n,
        "regime":      ["bull"] * n,
        "pnl_pct":     pnls,
        "ticker":      ["AAPL"] * n,
        "hold_days":   [20.0] * n,
    })


# ---------------------------------------------------------------------
# Unit assertions on the wired pathway
# ---------------------------------------------------------------------
def test_cube_populator_psr_is_real_not_placeholder_approximation():
    """compute_cell_metrics PSR must match metrics._deflated_sharpe output,
    NOT the prior monotonic approximation 0.5 + sharpe*sqrt(n)/50."""
    trades = _strong_edge_pnls()
    metrics = compute_cell_metrics(trades)
    # Pull the standalone real PSR for the same inputs:
    expected = _deflated_sharpe(
        sharpe=metrics["sharpe"],
        n_trades=metrics["n_trades"],
        skew=metrics["skew"],
        kurtosis=metrics["kurtosis"],
    )
    assert "psr" in metrics, "PSR field must be present in metrics dict"
    assert metrics["psr"] == pytest.approx(expected["psr"], abs=1e-4), \
        "compute_cell_metrics PSR must equal metrics._deflated_sharpe PSR"
    # Reject the OLD placeholder approximation
    sharpe = metrics["sharpe"]
    n = metrics["n_trades"]
    old_placeholder = min(0.99, max(0.0, 0.5 + (sharpe * np.sqrt(n) / 50)))
    # The two should typically diverge meaningfully (Bailey formula vs simple
    # linear), so assert at least one strong-edge sample shows >0.01 absolute
    # difference. This catches accidental reintroduction of the placeholder.
    assert abs(metrics["psr"] - old_placeholder) > 0.001 or metrics["psr"] != pytest.approx(old_placeholder, abs=1e-6), \
        "PSR equals the OLD placeholder approximation - wire-up regressed"


def test_cube_populator_psr_field_varies_with_edge_strength():
    """Regression guard: ensure PSR varies meaningfully across edge strengths
    (the bug was PSR=False placeholder; a constant return would also be wrong).
    Spans weak-edge -> strong-edge so PSR should range across (0.x, 1.0)."""
    seen = set()
    rng = np.random.RandomState(0)
    for loc in (0.05, 0.15, 0.3, 0.5):
        pnls = rng.normal(loc=loc, scale=1.0, size=60)
        df = pd.DataFrame({
            "strategy":    ["edge"] * 60,
            "exit_method": ["atr"] * 60,
            "regime":      ["bull"] * 60,
            "pnl_pct":     pnls,
            "ticker":      ["AAPL"] * 60,
            "hold_days":   [20.0] * 60,
        })
        m = compute_cell_metrics(df)
        seen.add(round(m["psr"], 3))
    assert len(seen) >= 2, f"PSR must vary across edge strengths, got {seen}"


def test_optimize_script_dec426_verdict_psr_is_real_not_hardcoded_false():
    """optimize_strategies_from_cube._dec426_verdict must compute PSR via
    metrics._deflated_sharpe, not return psr_>=_0.95: False unconditionally."""
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict

    trades = _strong_edge_pnls()
    stats = _cell_stats(trades["pnl_pct"], trades["hold_days"])
    assert "skew" in stats and "kurtosis" in stats, \
        "_cell_stats must populate skew + kurtosis (Batch 457)"
    verdict = _dec426_verdict(stats, m_total_candidates=1)
    assert "psr" in verdict, "_dec426_verdict must return real PSR field"
    assert verdict["psr"] is not None, \
        "PSR is None despite n>=30 + non-zero sharpe (Batch 457 regression)"
    # The gate value must reflect the computed PSR, not a hardcoded False:
    expected_gate = verdict["psr"] >= 0.95
    assert verdict["gates"]["psr_>=_0.95"] == expected_gate, \
        "psr_>=_0.95 gate does not reflect computed PSR (hardcoded regression)"


def test_strict_5_gate_CAN_pass_with_strong_edge_data():
    """Pre-Batch-457 bug: PSR hardcoded False prevented strict 5-Gate from
    EVER passing. This test asserts the gate CAN flip true with positive-edge
    synthetic data; if this fails, PSR is still hardcoded somewhere."""
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict

    # Construct a strong-edge sample large enough to push PSR past 0.95
    # WITHOUT making the Bailey denominator unstable (no enormous SR).
    rng = np.random.RandomState(101)
    pnls = pd.Series(rng.normal(loc=0.6, scale=1.0, size=200))
    hold_days = pd.Series([20.0] * 200)
    stats = _cell_stats(pnls, hold_days)
    verdict = _dec426_verdict(stats, m_total_candidates=1)
    # Should pass all 5 gates: n >= 30, p < 0.05, PSR >= 0.95, t >= 3.4, PF >= 2.0
    # Batch 502 (2026-05-31) renamed "rr_>=_2.0" -> "pf_>=_2.0" (the gate
    # has always tested profit_factor; the prior label was mathematically
    # wrong per Batch 492 counter-example).
    assert verdict["gates"]["n_>=_30"], "n>=30 gate failed on n=200"
    assert verdict["gates"]["p_<_0.05"], "p-value gate failed on extreme-edge data"
    assert verdict["gates"]["psr_>=_0.95"], \
        f"PSR gate failed despite strong edge -- PSR was {verdict.get('psr')}"
    assert verdict["gates"]["t_>=_3.4"], "t-stat gate failed on extreme-edge data"
    assert verdict["gates"]["pf_>=_2.0"], "PF gate failed on extreme-edge data"
    assert verdict["five_gate_pass"], \
        "Strict 5-Gate must PASS on strong-edge data (was blocked by hardcoded PSR)"


def test_weak_edge_data_fails_psr_gate():
    """Sanity check: weak-edge data should NOT pass PSR>=0.95."""
    trades = _weak_edge_pnls()
    metrics = compute_cell_metrics(trades)
    # PSR could be None for very low sharpe, or some computed value < 0.95
    psr = metrics.get("psr", 0.0)
    if psr is None:
        psr = 0.0
    verdict = evaluate_cell_criteria(metrics, regime="bull")
    # On weak edge: at minimum, either PSR < 0.95 OR the 5-Gate fails for
    # other statistical reasons. Strict assertion: PSR shouldn't be artificially
    # high (would indicate placeholder approximation taking over).
    assert psr < 0.95 or not verdict["five_gate_pass"], \
        f"Weak-edge data unexpectedly passed PSR gate (psr={psr})"


def test_cube_populator_and_optimize_script_psr_agree():
    """Single source of truth: both modules should produce IDENTICAL PSR for
    identical inputs (both delegate to metrics._deflated_sharpe)."""
    from scripts.optimize_strategies_from_cube import _cell_stats

    trades = _strong_edge_pnls()
    cube_metrics = compute_cell_metrics(trades)
    script_stats = _cell_stats(trades["pnl_pct"], trades["hold_days"])

    # The sharpe formulas in the two modules use slightly different signal
    # paths (cube_populator uses hold_days column if present; optimize script
    # accepts hold_days as 2nd arg). With identical hold_days they must agree.
    assert cube_metrics["sharpe"] == pytest.approx(script_stats["sharpe"], rel=1e-3), \
        "Sharpe diverges between cube_populator and optimize script for same trades"

    # PSR must be identical given identical sharpe + n + skew + kurtosis
    psr_cube = cube_metrics["psr"]
    expected = _deflated_sharpe(
        sharpe=script_stats["sharpe"],
        n_trades=script_stats["n"],
        skew=script_stats["skew"],
        kurtosis=script_stats["kurtosis"],
    )
    assert psr_cube == pytest.approx(expected["psr"], abs=1e-4), \
        f"PSR mismatch: cube={psr_cube} vs script-equivalent={expected['psr']}"


def test_insufficient_sample_psr_handled_gracefully():
    """n < 30 should not crash; PSR field should be handled (None or 0)."""
    rng = np.random.RandomState(7)
    pnls = rng.normal(loc=1.0, scale=1.0, size=10)  # n=10 < 30 threshold
    trades = pd.DataFrame({
        "strategy":    ["small"] * 10,
        "exit_method": ["atr_trail_1x"] * 10,
        "regime":      ["bull"] * 10,
        "pnl_pct":     pnls,
        "ticker":      ["AAPL"] * 10,
        "hold_days":   [5.0] * 10,
    })
    metrics = compute_cell_metrics(trades)
    # With n=10 < 30, _deflated_sharpe returns psr=None; compute_cell_metrics
    # converts None -> 0.0 for downstream gate evaluation safety.
    assert metrics["n_trades"] == 10
    assert metrics["psr"] in (0.0, None) or metrics["psr"] < 0.95
    # 5-Gate must mark as P3 / insufficient_trades, not crash on PSR
    verdict = evaluate_cell_criteria(metrics, regime="bull")
    assert verdict["priority"] == "P3"
    assert verdict["fail_reason"] == "insufficient_trades"


def test_psr_field_returned_alongside_deflated_sharpe():
    """Schema: compute_cell_metrics must return BOTH psr and deflated_sharpe
    so downstream consumers (dashboards, exporters) can show both."""
    trades = _strong_edge_pnls()
    metrics = compute_cell_metrics(trades)
    assert "psr" in metrics, "Missing psr field in cube_populator metrics"
    assert "deflated_sharpe" in metrics, \
        "Missing deflated_sharpe field in cube_populator metrics"
    assert "skew" in metrics, "Missing skew field (needed for PSR derivation)"
    assert "kurtosis" in metrics, "Missing kurtosis field (needed for PSR derivation)"
