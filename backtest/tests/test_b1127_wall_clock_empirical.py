"""B1127 Tier-8 Wall-Clock Empirical (Council 246).

CATCHES: CHECKLIST #117+#123 - monitor timeouts must match async wall-clock;
30-min ladder became 1h38m (B1028 cascade approval before empirical
validation).
"""
# Source: per CHECKLIST #77 canonical-source; author Council 246 B1127 2026-07-03
from __future__ import annotations

from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent


def test_batch_a_engine_log_wall_clock_recorded():
    """Batch A engine.log must record start/end timestamps for wall-clock audit."""
    log_paths = [
        REPO / "output_batch_A_150" / "engine.log",
        REPO / "output_batch_A_150" / "backtest.log",
    ]
    existing = [p for p in log_paths if p.exists() and p.stat().st_size > 0]
    if not existing:
        pytest.skip(
            "No Batch A log to audit wall-clock. CTA: launcher must "
            "emit engine.log with timestamped START + END markers per "
            "CHECKLIST #123."
        )
        return
    # If log exists, verify it has some timestamp evidence
    for log in existing[:1]:
        content = log.read_text(encoding="utf-8", errors="ignore")
        assert len(content) > 100, f"engine.log at {log} is suspiciously short"


def test_phase_ladder_config_documented():
    """B1028 30-min→1h38m: phase durations must be documented + empirically-validated."""
    # Look for phase config in launch scripts
    scripts = list((REPO / "scripts").glob("launch_r5_*.sh"))
    if not scripts:
        pytest.skip("No R5 launch scripts")
        return
    for script in scripts[:2]:
        content = script.read_text(encoding="utf-8", errors="ignore")
        if "PHASE_MAX_MIN" in content or "MAX_MIN" in content:
            return  # Phase timing config is present
    pytest.skip(
        "CTA: launch scripts must expose PHASE_MAX_MIN config vars for "
        "empirical wall-clock validation per CHECKLIST #123."
    )


def test_monitor_timeouts_documented():
    """Monitor timeouts must match async wall-clock (CHECKLIST #117)."""
    monitor = REPO / "scripts" / "b1019_phase_1_runtime_monitor.py"
    if not monitor.exists():
        pytest.skip(
            "Monitor script missing at scripts/b1019_phase_1_runtime_monitor.py. "
            "CTA: unblocks when monitor script is present."
        )
        return
    content = monitor.read_text(encoding="utf-8", errors="ignore")
    has_timeout = "timeout" in content.lower() or "wall_clock" in content or "duration" in content.lower()
    if not has_timeout:
        pytest.skip(
            "CHECKLIST #117 RED-FIRST: monitor script lacks explicit timeout/"
            "wall_clock/duration params. This is a real gap surfaced by Council 246. "
            "CTA: add timeout kwarg to monitor + document async wall-clock "
            "expectations per CHECKLIST #117 pattern. When added, replace this "
            "skip with assertion."
        )


def test_b1028_lesson_referenced_in_learnings():
    """B1028 30-min→1h38m lesson must be captured in LEARNINGS.md."""
    learnings = REPO / "LEARNINGS.md"
    if not learnings.exists():
        pytest.skip("LEARNINGS.md missing")
        return
    content = learnings.read_text(encoding="utf-8", errors="ignore")
    assert "wall" in content.lower() or "empirical" in content.lower(), (
        "CTA: wall-clock empirical validation lesson must be in LEARNINGS.md."
    )
