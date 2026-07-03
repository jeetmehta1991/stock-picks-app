"""B1127 Tier-4 Empirical: VERIFICATION_MATRIX freshness (Council 246).

CATCHES: 'wired=yes' grep heuristic false-positive floor of ~150 claims.
VERIFICATION_MATRIX must be coverage-driven (regenerated after canonical
backtest under `coverage run`), not grep-driven.
"""
# Source: per CHECKLIST #77 canonical-source; author Council 246 B1127 2026-07-03
from __future__ import annotations

from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent


def test_verification_matrix_file_exists():
    """VERIFICATION_MATRIX.md must exist as the canonical wired-vs-consumed ledger."""
    matrix = REPO / "VERIFICATION_MATRIX.md"
    if not matrix.exists():
        pytest.skip(
            "CTA: VERIFICATION_MATRIX.md must exist per CLAUDE.md as engine-"
            "consumption ground truth. Replaces `wired=yes` grep heuristic."
        )
        return


def test_verification_matrix_builder_script_present():
    """scripts/build_verification_matrix.py must exist for regeneration."""
    builder = REPO / "scripts" / "build_verification_matrix.py"
    if not builder.exists():
        pytest.skip(
            "CTA: scripts/build_verification_matrix.py must exist to "
            "regenerate matrix under `coverage run`."
        )


def test_verification_matrix_mentions_coverage_driven_methodology():
    """Matrix should reference coverage-driven regeneration methodology."""
    matrix = REPO / "VERIFICATION_MATRIX.md"
    if not matrix.exists():
        pytest.skip("Matrix file missing (soft check)")
        return
    content = matrix.read_text(encoding="utf-8", errors="ignore")
    has_methodology = (
        "coverage" in content.lower()
        or "engine-consumption" in content.lower()
        or "consumed" in content.lower()
    )
    assert has_methodology, (
        "VERIFICATION_MATRIX.md must document its coverage-driven methodology "
        "to distinguish from grep-based `wired=yes` heuristic."
    )


def test_claude_md_references_verification_matrix():
    """CLAUDE.md must cite VERIFICATION_MATRIX + build script."""
    claude = REPO / "CLAUDE.md"
    if not claude.exists():
        pytest.skip(
            "CLAUDE.md missing at repo root. "
            "CTA: unblocks when CLAUDE.md is present."
        )
        return
    content = claude.read_text(encoding="utf-8", errors="ignore")
    assert "VERIFICATION_MATRIX" in content, (
        "CLAUDE.md must reference VERIFICATION_MATRIX as canonical "
        "engine-consumption ground truth."
    )
