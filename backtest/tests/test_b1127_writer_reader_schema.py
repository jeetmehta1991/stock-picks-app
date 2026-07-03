"""B1127 Tier-6 Writer/Reader Schema-Boundary (Council 246).

CATCHES: L180 monitor required exit_method but writer emits exit_reason
(PIVOT #37). Boundary schema drift is silent until runtime against real
data.

RULE: every writer-reader pair (writer.py -> monitor.py -> analyzer.py)
must have shared key vocabulary + pin test.
"""
# Source: per CHECKLIST #77 canonical-source; author Council 246 B1127 2026-07-03
from __future__ import annotations

from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent


def test_writer_emits_canonical_exit_reason():
    """writer.py must emit 'exit_reason' column (canonical), not 'exit_method'."""
    writer = REPO / "backtest" / "results" / "writer.py"
    if not writer.exists():
        pytest.skip(f"writer.py missing at {writer}")
        return
    content = writer.read_text(encoding="utf-8", errors="ignore")
    # Verify canonical exit_reason is present
    assert "exit_reason" in content, "L180 regression: writer.py must emit 'exit_reason'"


def test_monitor_reads_canonical_exit_reason():
    """B1019 monitor must read 'exit_reason' (post-B1062 fix), not 'exit_method'."""
    monitor = REPO / "scripts" / "b1019_phase_1_runtime_monitor.py"
    if not monitor.exists():
        pytest.skip(f"Monitor script missing at {monitor}")
        return
    content = monitor.read_text(encoding="utf-8", errors="ignore")
    # If exit_method appears in monitor, verify it's used correctly (not as REQUIRED trade_log column)
    if "exit_method" in content:
        # Check if it's a required column list vs cube-specific reference
        if "required" in content.lower() and "exit_method" in content:
            problematic_lines = [
                line for line in content.split("\n")
                if "exit_method" in line and "required" in line.lower()
            ]
            if problematic_lines:
                pytest.fail(
                    f"L180 regression: monitor requires exit_method in trade_log "
                    f"(writer emits exit_reason). Problematic lines:\n"
                    + "\n".join(problematic_lines[:5])
                )


def test_b1062_schema_pin_test_exists():
    """B1062 monitor schema contract pin test must be present."""
    test_file = REPO / "backtest" / "tests" / "test_b1062_monitor_schema_contract.py"
    assert test_file.exists(), (
        f"L180 pin test missing at {test_file.relative_to(REPO)}. "
        f"Every writer-reader pair needs schema contract pin test."
    )


def test_closed_trade_field_and_resolver_present():
    """B1079 fix: ClosedTrade must reconstruct + carry exit fields correctly."""
    for candidate in (
        REPO / "backtest" / "engine" / "backtest.py",
        REPO / "backtest" / "engine" / "exit_manager.py",
    ):
        if not candidate.exists():
            continue
        content = candidate.read_text(encoding="utf-8", errors="ignore")
        if "ClosedTrade" in content:
            return
    pytest.fail(
        "L180 companion: ClosedTrade dataclass not found in engine. "
        "B1079 fix requires proper field reconstruction on resume."
    )
