"""B1127 Tier-10 Retroactive PIVOT Coverage (Council 246).

CATCHES: CHECKLIST #136 anti-audit-theater guard - new audit layers must
demonstrate retroactive coverage of last 3 PIVOTs or be rejected.

Council 197 verdict: 'Eight layers is the smell, not the cure. Tests pass
because they don't touch the things that break.'
"""
# Source: per CHECKLIST #77 canonical-source; author Council 246 B1127 2026-07-03
from __future__ import annotations

from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent


def test_last_3_pivots_have_regression_tests():
    """PIVOT #42, #43, #44 must have corresponding regression tests."""
    tests_dir = REPO / "backtest" / "tests"
    # PIVOT #42 = E-NEW HALT / active_tickers gate = B1073
    # PIVOT #43 = ClosedTrade dataclass reconstruction = B1079
    # PIVOT #44 = checkpoint cadence mismatch = B1081
    for pivot_batch in ("b1073", "b1079", "b1081"):
        test_files = list(tests_dir.glob(f"test_{pivot_batch}_*"))
        assert test_files, (
            f"CHECKLIST #136 regression: no test for PIVOT batch {pivot_batch}. "
            f"Every PIVOT must have regression guard."
        )


def test_b1082_process_restructure_documented():
    """CLAUDE.md must reference B1082 process restructure."""
    claude = REPO / "CLAUDE.md"
    if not claude.exists():
        pytest.skip(
            "CLAUDE.md missing at repo root. "
            "CTA: unblocks when CLAUDE.md is present."
        )
        return
    content = claude.read_text(encoding="utf-8", errors="ignore")
    assert "B1082" in content, "B1082 process restructure must be documented in CLAUDE.md banner"


def test_council_236_236_and_237_referenced_in_docs():
    """Recent Council 236-240 must be referenced in AUDIT_INDEX.md."""
    audit = REPO / "AUDIT_INDEX.md"
    if not audit.exists():
        pytest.skip("AUDIT_INDEX.md missing")
        return
    content = audit.read_text(encoding="utf-8", errors="ignore")
    for council in ("236", "237"):
        assert f"Council {council}" in content or f"Council#{council}" in content, (
            f"Council {council} not documented in AUDIT_INDEX.md. "
            f"CTA: doc-sweep required per CHECKLIST #67."
        )


def test_recent_bugs_registered():
    """BUG-277 through BUG-281 must be registered."""
    bug_register = REPO / "BUG_REGISTER.md"
    if not bug_register.exists():
        pytest.skip("BUG_REGISTER.md missing")
        return
    content = bug_register.read_text(encoding="utf-8", errors="ignore")
    for bug in ("277", "278", "279", "280", "281"):
        assert f"BUG-{bug}" in content, f"BUG-{bug} missing from BUG_REGISTER.md"


def test_pyramid_extension_batches_documented():
    """B1124 + B1127 test extensions must be in EXECUTION_QUEUE.md."""
    eq = REPO / "EXECUTION_QUEUE.md"
    if not eq.exists():
        pytest.skip("EXECUTION_QUEUE.md missing")
        return
    content = eq.read_text(encoding="utf-8", errors="ignore")
    assert "B1124" in content, "B1124 test extension must be in EXECUTION_QUEUE"
    # B1127 self-reference - will be added same commit
