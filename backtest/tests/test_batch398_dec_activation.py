"""Batch 398 (2026-05-27): activation tests for DEC-062 / DEC-138 / DEC-216 / DEC-365.

Source (per CHECKLIST #77): owner directive 2026-05-27 "all wired items
need to be activated now -- doesn't matter if blocker or not".

Tests:
  DEC-062: apply_agent_tier_size_modifier helper exists + matches dict
  DEC-138: cold_start.yml exists at the cited path + has timeout + steps
  DEC-216: scripts/run_ab_orchestrator.py exists + has correct CLI
  DEC-365: status text in AUDIT_INDEX.md reflects RESOLVED-DECIDED-DEFERRED
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent


# ---------- DEC-062 ---------------------------------------------------------

def test_dec062_helper_exists():
    from backtest.config import (
        AGENT_TIER_TO_SIZE_MODIFIER,
        apply_agent_tier_size_modifier,
    )
    # Dict spec
    assert AGENT_TIER_TO_SIZE_MODIFIER == {1: 0.50, 2: 0.75, 3: 1.00, 4: 1.25, 5: 1.50}
    # Helper matches dict
    for tier, mod in AGENT_TIER_TO_SIZE_MODIFIER.items():
        assert apply_agent_tier_size_modifier(tier, 1.0) == pytest.approx(mod)


def test_dec062_helper_handles_out_of_range():
    """Out-of-range tier returns base unchanged (fail-open, logs warning)."""
    from backtest.config import apply_agent_tier_size_modifier
    assert apply_agent_tier_size_modifier(0, 0.05) == pytest.approx(0.05)
    assert apply_agent_tier_size_modifier(6, 0.05) == pytest.approx(0.05)
    assert apply_agent_tier_size_modifier(99, 0.10) == pytest.approx(0.10)


def test_dec062_helper_scales_base_size():
    """tier=4 modifier 1.25x applied to base 4% -> 5%."""
    from backtest.config import apply_agent_tier_size_modifier
    assert apply_agent_tier_size_modifier(4, 0.04) == pytest.approx(0.05)
    assert apply_agent_tier_size_modifier(1, 0.04) == pytest.approx(0.02)
    assert apply_agent_tier_size_modifier(5, 0.04) == pytest.approx(0.06)


def test_dec062_helper_clamps_negative_to_zero():
    """Negative base size clamped non-negative."""
    from backtest.config import apply_agent_tier_size_modifier
    assert apply_agent_tier_size_modifier(3, -0.05) == 0.0


# ---------- DEC-138 ---------------------------------------------------------

def test_dec138_workflow_file_exists():
    """Cold-start workflow must exist at the cited path constant."""
    from backtest.config import (
        COLD_START_CI_WORKFLOW_PATH,
        COLD_START_CI_MAX_MINUTES,
    )
    wf = REPO / COLD_START_CI_WORKFLOW_PATH
    assert wf.exists(), f"DEC-138: workflow missing at {wf}"
    src = wf.read_text(encoding="utf-8")
    # Timeout matches DEC-138 constant
    assert f"timeout-minutes: {COLD_START_CI_MAX_MINUTES}" in src, (
        f"DEC-138: timeout-minutes constant mismatch (expected {COLD_START_CI_MAX_MINUTES})"
    )
    # Workflow includes core steps
    for step in ("Checkout", "Set up Python", "Cold dependency install",
                 "Import smoke", "DEC-138 constants"):
        assert step in src, f"DEC-138: missing required step `{step}`"


# ---------- DEC-216 ---------------------------------------------------------

def test_dec216_runner_script_exists():
    """A/B orchestrator CLI runner must exist + be importable."""
    runner = REPO / "scripts" / "run_ab_orchestrator.py"
    assert runner.exists(), f"DEC-216: runner missing at {runner}"
    src = runner.read_text(encoding="utf-8")
    # Required CLI flags
    for flag in ("--winners-parquet", "--trade-log-rules-only",
                 "--trade-log-full-agents", "--trade-log-no-risk",
                 "--output"):
        assert flag in src, f"DEC-216: runner missing CLI flag `{flag}`"
    # Imports the orchestrator
    assert "from backtest.results.ab_orchestrator import orchestrate_ab_run" in src


def test_dec216_orchestrator_importable():
    """The module the runner invokes must be importable."""
    from backtest.results.ab_orchestrator import orchestrate_ab_run
    # Sanity: function signature
    import inspect
    sig = inspect.signature(orchestrate_ab_run)
    assert "winners_df" in sig.parameters
    assert "trade_logs_per_arm" in sig.parameters


# ---------- DEC-365 ---------------------------------------------------------

def test_dec365_status_corrected_in_audit_index():
    """AUDIT_INDEX.md must reflect RESOLVED-DECIDED-DEFERRED status."""
    audit = REPO / "AUDIT_INDEX.md"
    assert audit.exists()
    src = audit.read_text(encoding="utf-8")
    # Find the DEC-365 row (markdown table row -- match full line)
    row = None
    for line in src.splitlines():
        if "**DECISION-365**" in line:
            row = line
            break
    assert row is not None, "DEC-365 row not found in AUDIT_INDEX.md"
    assert "Batch 398" in row, "DEC-365 row missing Batch 398 annotation"
    assert "RESOLVED-DECIDED-DEFERRED" in row, "DEC-365 status not updated"
