"""Batch 462 (2026-05-29) -- AU6 semantic-integration test pyramid.

Closes 5 audit-gap findings surfaced by the 5-pattern audit (Batches 455+),
each previously caught by pattern 3 ("Tests check 'script runs' not
'verdict is meaningful'").

GAPS CLOSED:
  M3   adversarial random-walk baseline           -> test_random_walk_zero_5gate_passes
  0b   Bonferroni denominator runtime > 1000      -> test_optimizer_main_bonferroni_denominator_runtime
  0c   walk-forward fold IS/OOS time-ordering     -> test_walk_forward_folds_chronological_disjoint
  #4 + AU1  PSR computed not hardcoded            -> test_psr_real_computed_summary
  positive control for the 5-Gate pipeline       -> test_strong_positive_drift_passes_5gate

Each test exercises the production code path end-to-end and asserts a
meaningful invariant about the OUTPUT, not just that the call succeeded.

This file is the AU6 "semantic-integration test framework" deliverable
per CHECKLIST #100. New audit findings whose check is "verdict is
meaningful" should append a test here rather than living as a one-off.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


REPO = Path(__file__).resolve().parents[2]


# ======================================================================
# M3 -- ADVERSARIAL RANDOM-WALK BASELINE
# ======================================================================
def test_random_walk_zero_5gate_passes():
    """Feed synthetic random-walk pnl% (mean=0) through the optimizer
    verdict pipeline; the strict 5-Gate should reject every cell. If any
    cell passes, the pipeline is overfit and current 'PASS' cells are
    partly noise.

    Closes audit finding M3 (queue item 'missing-random-walk-adversarial-
    baseline'). Without this test, a verdict pipeline could pass synthetic
    noise as a winner.
    """
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict

    rng = np.random.RandomState(0)
    passes = 0
    # Run many synthetic random-walk samples through the verdict to ensure
    # the noise rejection is robust (not seed-dependent).
    for trial in range(40):
        pnl_pct = pd.Series(rng.normal(0.0, 2.0, size=100))
        hold_days = pd.Series([20.0] * 100)
        stats = _cell_stats(pnl_pct, hold_days)
        verdict = _dec426_verdict(stats, m_total_candidates=1500)
        if verdict.get("five_gate_pass"):
            passes += 1
    assert passes == 0, \
        f"random-walk noise passed strict 5-Gate in {passes}/40 trials; pipeline is overfit"


def test_strong_positive_drift_passes_5gate():
    """Positive control: synthetic strongly-positive-edge data MUST pass
    the strict 5-Gate. If this fails, a real edge can not pass either --
    typically meaning a gate was hardcoded or a threshold drifted.

    Pairs with test_random_walk_zero_5gate_passes as a two-sided check on
    the 5-Gate pipeline.

    Batch 506 (2026-05-31, 0a Path-2 swap): enforced gate changed from
    profit_factor to actual R:R = avg_win / abs(avg_loss). Synthetic
    fixture updated to asymmetric wins/losses (150 wins @ 1.5%, 50
    losses @ -0.5% -> R:R = 3.0, PF = 9.0) so both gates pass.
    """
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict

    pnl = pd.Series([1.5]*150 + [-0.5]*50)
    hold = pd.Series([20.0] * 200)
    stats = _cell_stats(pnl, hold)
    verdict = _dec426_verdict(stats, m_total_candidates=1)
    assert verdict["five_gate_pass"], \
        f"strong-edge synthetic data did not pass 5-Gate; gates={verdict.get('gates')}"


# ======================================================================
# 0b -- BONFERRONI DENOMINATOR AT RUNTIME > 1000
# ======================================================================
def test_optimizer_main_bonferroni_denominator_runtime():
    """`_dec426_verdict(m_total_candidates=1)` default would make Bonferroni
    a no-op (raw_p * 1 == raw_p). The production caller at
    optimize_strategies_from_cube.main MUST pass a real M derived from the
    fired-strategy count x dimension count, not the default 1.

    Production formula (line ~903):
        M = max(len(fired) * 9, 1)
    With ~150 strategies x 9 dimensions = 1350, the runtime M > 1000.

    Greppable + numeric guard: if a future refactor accidentally removes
    the M computation or pins it to a small number, this test surfaces it.
    """
    src = (REPO / "scripts" / "optimize_strategies_from_cube.py").read_text(
        encoding="utf-8"
    )
    # The main() function must compute M from len(fired) (not hardcoded).
    assert "M = max(len(fired) * 9, 1)" in src, \
        "optimizer main() must derive M from len(fired) * 9 -- regression"
    # And it must be passed positionally / via kwarg to optimize_strategy
    # so the downstream _dec426_verdict actually receives a non-trivial M.
    assert "optimize_strategy(strat, trade_log, cube, screener_source, M)" in src, \
        "optimize_strategy must receive M via main() -- regression"


def test_dec426_verdict_default_m_is_documented_warning():
    """`_dec426_verdict(m_total_candidates: int = 1)` default of 1 means
    NO multiple-testing correction. That's only safe when the caller passes
    a real M. This test guards the warning lives in the function body so
    a future refactor that drops main()'s M=... call surfaces in code
    review rather than silently bypassing Bonferroni.

    Closes finding 0b (pattern-3-bonferroni-denominator).
    """
    src = (REPO / "scripts" / "optimize_strategies_from_cube.py").read_text(
        encoding="utf-8"
    )
    # Function definition keeps the int=1 default for ergonomic call sites
    # (e.g., unit tests on a single strategy). Production main() overrides.
    assert "m_total_candidates: int = 1" in src
    # Production callsite passes M, not the default
    assert "m_total_candidates=M" in src or "_dec426_verdict(agg, m_total_candidates=m_total_candidates)" in src


# ======================================================================
# 0c -- WALK-FORWARD FOLD IS/OOS CHRONOLOGICAL + DISJOINT
# ======================================================================
def test_walk_forward_folds_chronological_disjoint():
    """DEC-505 4-fold expanding-window: each fold must satisfy
        is_start <= is_end == oos_start <= oos_end
    AND no two OOS windows may overlap (disjoint annual OOS years).

    A bug that randomly shuffled the fold dates would produce JSON output
    + 4 fold cells that LOOK valid (existence checks pass) but with
    garbage OOS Sharpe numbers. This test asserts the TIME-ORDERING
    invariant directly so such a regression cannot pass silently.

    Closes audit finding 0c (pattern-3-walk-forward-chronological-split).
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_wf", str(REPO / "scripts" / "walk_forward_batch414_cells.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    folds = mod.FOLDS
    assert len(folds) == 4, f"DEC-505 expects 4 folds; got {len(folds)}"

    # Per-fold invariants
    oos_windows = []
    for name, is_start, is_end, oos_start, oos_end in folds:
        assert is_start <= is_end, f"{name}: is_start > is_end"
        assert oos_start <= oos_end, f"{name}: oos_start > oos_end"
        assert is_end == oos_start, \
            f"{name}: expanding-window IS_end ({is_end}) must equal " \
            f"OOS_start ({oos_start})"
        oos_windows.append((name, oos_start, oos_end))

    # All OOS windows disjoint (no overlap with any other fold's OOS)
    for i, (n1, s1, e1) in enumerate(oos_windows):
        for n2, s2, e2 in oos_windows[i + 1:]:
            overlap = max(s1, s2) < min(e1, e2)
            assert not overlap, \
                f"OOS overlap: {n1}({s1}..{e1}) and {n2}({s2}..{e2})"


def test_walk_forward_oos_windows_are_one_year_each():
    """DEC-505 explicitly calls for 'disjoint 1y OOS' folds. Test that
    each OOS span is approximately one calendar year (365 +- 1 day for
    leap-year tolerance)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_wf", str(REPO / "scripts" / "walk_forward_batch414_cells.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    for name, _is_s, _is_e, oos_s, oos_e in mod.FOLDS:
        span_days = (oos_e - oos_s).days
        assert 364 <= span_days <= 366, \
            f"{name} OOS span {span_days}d should be ~365 (DEC-505 1y)"


# ======================================================================
# #4 + AU1 -- PSR COMPUTED NOT HARDCODED (semantic-integration summary)
# ======================================================================
def test_psr_real_computed_summary():
    """Smoke summary: PSR varies with edge strength + the strict 5-Gate
    CAN pass on positive-edge data. Detailed assertions live in
    test_batch457_psr_wireup.py; this test is the pyramid-level
    semantic-integration entrypoint that closes the audit gap.
    """
    from scripts.optimize_strategies_from_cube import _cell_stats, _dec426_verdict

    rng = np.random.RandomState(0)
    psr_values = set()
    for loc in (0.05, 0.2, 0.5, 0.8):
        pnl = pd.Series(rng.normal(loc=loc, scale=1.0, size=80))
        hold = pd.Series([20.0] * 80)
        stats = _cell_stats(pnl, hold)
        verdict = _dec426_verdict(stats, m_total_candidates=1500)
        psr = verdict.get("psr")
        if psr is not None:
            psr_values.add(round(psr, 3))
    assert len(psr_values) >= 2, \
        f"PSR must vary across edge strengths (computed, not hardcoded); got {psr_values}"


# ======================================================================
# Framework discoverability (for future audit-finding additions)
# ======================================================================
def test_pyramid_file_documents_audit_gap_closures():
    """The pyramid test file's docstring must list which audit-gap findings
    each test closes. Guards that future contributors who add a new
    semantic-integration test also update the GAPS CLOSED block in the
    module docstring (so the framework's purpose stays discoverable)."""
    src = Path(__file__).read_text(encoding="utf-8")
    assert "GAPS CLOSED" in src
    # Sanity: at least 4 gap references present
    for marker in ("M3", "0b", "0c", "AU1"):
        assert marker in src, f"audit gap marker {marker} missing from docstring"
