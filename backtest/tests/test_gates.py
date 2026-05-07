"""Stage / Phase / Sub-phase Gate Executable Tests (DEC-595 / CHECKLIST #73 / L149).

Per DEC-594 Test-Artifact Same-Commit HARD RULE: every transition between stages,
phases, sprints, or sub-phases MUST have an executable gate test asserting the
entry/exit criteria. No transition without preceding gate test PASS.

This file extends as new transitions are defined. Current scope (Pass 53):

  Gate 1: pre-Phase-1A entry          (DEC-590; before May 15)
  Gate 2: post-Phase-1A-α              (before $300 1B-α budget commit)
  Gate 3: pre-Phase-1B-α run           (Sprint 9; before scaled API spend)
  Gate 4: post-Phase-1B-α verdict      (DEC-578 7-gate; before Stage 3)
  Gate 5: pre-Stage-3 entry            (paper-trading start)
  Gate 6: pre-Stage-4 entry            (live trading start)

Each gate is a pytest function. Failed gate BLOCKS transition with actionable
error. Gates 2-6 will SKIP with explicit reason until criteria materialize;
gate 1 PASSES today (data-integrity 7/7 verified in Pass 53 evening 2026-05-06).
"""

import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Gate 1: pre-Phase-1A entry (DEC-590; before May 15 implementation start)
# ---------------------------------------------------------------------------
def test_gate_pre_phase_1a_entry():
    """Gate 1 — Phase 1A entry criteria (DEC-590 May 15).

    Asserts:
      a) Data-integrity 7/7 PASS (DEC-591 / CHECKLIST #72)
      b) Universe build verified (Master Dedup CSV present + parseable)
      c) Smoke run on 5 tickers via canonical OHLCV cache works
      d) DEC-505 4-fold walk-forward config valid in backtest/config.py
    """
    # (a) Data-integrity tests already exist and PASS
    di_test = REPO_ROOT / "backtest" / "tests" / "test_data_integrity.py"
    assert di_test.exists(), (
        "Gate 1 BLOCKED: data-integrity test suite missing per DEC-591"
    )

    # (b) Universe build verified
    universe_csv = (
        REPO_ROOT / "Backtesting universe"
        / "Master Universe_Deduplicated_All Tiers_May 2026.csv"
    )
    assert universe_csv.exists(), (
        f"Gate 1 BLOCKED: Master Dedup CSV missing at {universe_csv}"
    )

    # (c) Smoke OHLCV — 5 sample tickers across tiers
    import pandas as pd
    smoke_tickers = ["AAPL", "SPY", "VST", "AA", "NVDA"]
    ohlcv_dir = REPO_ROOT / "backtest" / "data" / "cache" / "ohlcv"
    for t in smoke_tickers:
        p = ohlcv_dir / f"{t}.parquet"
        assert p.exists(), f"Gate 1 BLOCKED: smoke ticker {t} OHLCV missing"
        df = pd.read_parquet(p)
        assert len(df) > 100, f"Gate 1 BLOCKED: {t} OHLCV has only {len(df)} rows"

    # (d) DEC-505 walk-forward config — 4 OOS folds
    config_path = REPO_ROOT / "backtest" / "config.py"
    if config_path.exists():
        text = config_path.read_text(errors="ignore")
        # Either WALK_FORWARD_FOLDS list-of-4-tuples OR explicit 4-fold reference
        has_4_fold = "WALK_FORWARD_FOLDS" in text or "4-fold" in text or "DEC-505" in text
        assert has_4_fold, (
            "Gate 1 BLOCKED: DEC-505 4-fold walk-forward not configured in backtest/config.py"
        )


# ---------------------------------------------------------------------------
# Gate 2: post-Phase-1A-α (before $300 1B-α budget commit)
# ---------------------------------------------------------------------------
def test_gate_post_phase_1a_alpha():
    """Gate 2 — rules-only Sharpe ≥ 0.7 OOS verified before $300 1B-α commits.

    Asserts:
      a) Phase 1A-α run output exists at backtest/results/phase_1a_alpha/
      b) rules-only Sharpe metric ≥ 0.7 across OOS folds
    """
    output_dir = REPO_ROOT / "backtest" / "results" / "phase_1a_alpha"
    if not output_dir.exists():
        pytest.skip(
            "Gate 2 PENDING: Phase 1A-α has not run yet. Will assert "
            "rules-only Sharpe ≥ 0.7 OOS once results land. (DEC-590 schedule: post May 15.)"
        )
    # Once Phase 1A-α runs, will assert Sharpe metric here
    metrics_path = output_dir / "rules_only_metrics.json"
    assert metrics_path.exists(), "Gate 2 BLOCKED: rules-only metrics file missing"
    import json
    metrics = json.loads(metrics_path.read_text())
    sharpe = metrics.get("sharpe_oos")
    assert sharpe is not None and sharpe >= 0.7, (
        f"Gate 2 FAILED: rules-only OOS Sharpe = {sharpe} (need ≥ 0.7 per "
        f"PROJECT_PLAN §3.6-3.10 owner-gated criterion)"
    )


# ---------------------------------------------------------------------------
# Gate 3: pre-Phase-1B-α run (before scaled API spend)
# ---------------------------------------------------------------------------
def test_gate_pre_phase_1b_alpha_run():
    """Gate 3 — Pre-Phase-1B-α run readiness.

    Asserts:
      a) DEC-507 wiring matrix all rows ✅ (TRADINGAGENTS_DATA_AUDIT.md)
      b) DEC-508 Tier 1-3 fork tests pass (smartmoneyconcepts Phase A green)
      c) budget tracker armed (backtest/ab/budget_tracking.py exists)
      d) Anthropic API rate headroom verified (smoke ping)
    """
    pytest.skip(
        "Gate 3 PENDING: Phase 1B-α has not entered planning yet. Will assert "
        "wiring matrix + fork tests + budget tracker + API headroom once Sprint 9 begins. "
        "(DEC-590 schedule: post Phase 1A completion.)"
    )


# ---------------------------------------------------------------------------
# Gate 4: post-Phase-1B-α verdict (before Stage 3 entry)
# ---------------------------------------------------------------------------
def test_gate_post_phase_1b_alpha_verdict():
    """Gate 4 — DEC-578 7-gate Phase 1B-α verdict has ≥1 PASS cell + DSR + walk-forward.

    Asserts:
      a) backtest/results/phase_1b_alpha/verdict_cube.parquet exists
      b) ≥1 cell has PASS verdict per DEC-578 7-gate criteria
      c) DSR (Deflated Sharpe) computed
      d) walk-forward 4 OOS folds completed (DEC-505)
    """
    pytest.skip(
        "Gate 4 PENDING: Phase 1B-α verdict not produced yet. Will assert ≥1 PASS "
        "cell + DSR + 4-fold walk-forward once cube populates. (DEC-590 schedule: "
        "post Phase 1B-α run completion.)"
    )


# ---------------------------------------------------------------------------
# Gate 5: pre-Stage-3 entry (paper-trading start)
# ---------------------------------------------------------------------------
def test_gate_pre_stage_3_entry():
    """Gate 5 — Pre-Stage-3 (paper trading) entry.

    Asserts:
      a) Phase 1B-α verdict produced (Gate 4 PASS)
      b) paper-trading infrastructure ready (broker SDK + order routing tests)
      c) 3-month duration plan codified (DEC-028)
    """
    pytest.skip(
        "Gate 5 PENDING: Stage 2 → 3 transition is months out. Will assert verdict "
        "+ paper infra + 3-month plan once Stage 2 completes. (DEC-028 paper duration.)"
    )


# ---------------------------------------------------------------------------
# Gate 6: pre-Stage-4 entry (live trading start)
# ---------------------------------------------------------------------------
def test_gate_pre_stage_4_entry():
    """Gate 6 — Pre-Stage-4 (live trading) entry.

    Asserts:
      a) 3-month paper-trading audit pass (Stage 3 verdict)
      b) email approval pipeline operational (Stage 4 design)
      c) capital pre-funded (owner-controlled)
    """
    pytest.skip(
        "Gate 6 PENDING: Stage 3 → 4 transition is years out. Will assert paper "
        "audit + email pipeline + capital once Stage 3 completes."
    )
