"""B1052 launch script --no-agents flag pyramid test (PIVOT #30 catch).

# Source: HONEST-FINDING PIVOT #30 Phase D Phase 1 silent engine.
# Engine ran agent retry loop at 21s/day; 1003 days = 5.85hr vs MAX_MIN
# =120 min cap. Smoke didn't catch because of scale (~7.7 min at 22 days
# fit in 15-min cap; ~5.85hr at 1003 days exceeds 120-min cap). Per
# CHECKLIST #126 + #77.

Bug class: scale-dependent agent retry overhead in Phase 1A-beta cube
evaluation. Phase 1A-beta does NOT need agents (agents are for Phase 1B+
when agent overlay is the experiment). The launch script must pass
`--no-agents` explicitly.

This test catches the bug class so future R6 launches don't repeat.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LAUNCH = REPO / "scripts" / "launch_r5_master_4y_v2.sh"


def test_b1052_phase_1a_beta_engine_invocation_has_no_agents_flag():
    """B1052 PIVOT #30: launch script engine invocation must include
    --no-agents for Phase 1A-beta cube evaluation.

    Without --no-agents:
      - Engine runs agent pipeline per sim_day
      - ANTHROPIC_API_KEY not set on AWS instance (expected)
      - 5 retry attempts × ~1.5s = ~7.5s overhead per agent call
      - Scales to ~5.85 hr for 1003-day Phase 1; exceeds 120-min cap
    """
    content = LAUNCH.read_text()
    # Find the engine invocation line(s)
    engine_lines = [
        line for line in content.splitlines()
        if "run_phase1a --phase 1a-beta" in line
    ]
    assert engine_lines, (
        "B1052 launch script must contain run_phase1a --phase 1a-beta "
        "invocation"
    )
    for line in engine_lines:
        assert "--no-agents" in line, (
            f"B1052 PIVOT #30 fix: engine invocation must include "
            f"--no-agents flag for Phase 1A-beta cube evaluation. "
            f"Phase 1A-beta is NO-AGENTS by design (agents are for "
            f"Phase 1B+). Without this flag, engine runs agent retry "
            f"loop at ~21s/day, scaling to ~5.85hr for 1003-day Phase 1. "
            f"Found line: {line[:200]}"
        )


def test_b1052_run_phase1a_supports_no_agents_flag():
    """B1052: backtest/run_phase1a.py must support --no-agents flag
    (it does; this test guards against future removal)."""
    import inspect
    from backtest import run_phase1a
    source = inspect.getsource(run_phase1a)
    assert '--no-agents' in source, (
        "B1052: run_phase1a.py must define --no-agents argparse flag "
        "for Phase 1A-beta cube evaluation"
    )
    # And the flag must control the agents var passed to the engine
    assert "args.no_agents" in source or "no_agents" in source, (
        "B1052: --no-agents flag must control agent invocation"
    )


def test_b1052_scale_dependent_bug_class_documented():
    """B1052: CHECKLIST #127 honest limitation must be documented
    in audit doc per feedback_audit_recommendations_against_existing_
    directives."""
    audit_doc = REPO / "output_audit" / "b1052_phase_d_silent_engine_root_cause_2026_06_28.md"
    assert audit_doc.exists(), (
        "B1052: root-cause audit doc must exist documenting scale-"
        "dependent bug class limitation of CHECKLIST #127"
    )
    content = audit_doc.read_text(encoding='utf-8')
    assert "scale-dependent" in content.lower(), (
        "B1052 audit doc must document scale-dependent bug class"
    )
    assert "CHECKLIST #127" in content, (
        "B1052 audit must reference #127 limitation honestly"
    )
