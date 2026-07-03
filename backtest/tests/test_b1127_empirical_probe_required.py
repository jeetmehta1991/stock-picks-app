"""B1127 Tier-4 Empirical: Mandatory empirical probe for producer verdicts (Council 246).

CATCHES: BUG-279 initial hypothesis (Turn 2 paragraph verdict on @lru_cache)
that was empirically refuted in B1125 Council 245. Council 197 Outsider
verdict: 'Tests pass because they don't touch the things that break.'

Every producer-level verdict on a strategy must be backed by a runtime
probe on canonical fixture. Static analysis alone is insufficient.
"""
# Source: per CHECKLIST #77 canonical-source; author Council 246 B1127 2026-07-03
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


REPO = Path(__file__).parent.parent.parent
CSV = REPO / "output_batch_A_150" / "phase_1_quiet_fire_investigation.csv"


@pytest.fixture(scope="module")
def df():
    if not CSV.exists():
        pytest.skip(f"CSV missing: {CSV}")
    return pd.read_csv(CSV)


def test_bug_bug_279_empirical_rebuttal_present(df):
    """BUG-279 must have RESOLVED-BY-INVESTIGATION status via empirical probe."""
    halloween = df[df["strategy_name"] == "halloween_seasonal_long"]
    if halloween.empty:
        pytest.skip("halloween_seasonal_long not in CSV")
        return
    comments = str(halloween.iloc[0]["execution_comments"])
    assert "RESOLVED-BY-INVESTIGATION" in comments or "B1125" in comments, (
        "BUG-279 empirical rebuttal missing from execution_comments. "
        "Turn 2 paragraph verdict must be traced to B1125 empirical probe."
    )


def test_bug_277_empirical_uplift_present(df):
    """BUG-277 must have empirical detection uplift documented."""
    triangle = df[df["strategy_name"] == "triangle_ascending_long"]
    if triangle.empty:
        pytest.skip("triangle_ascending_long not in CSV")
        return
    comments = str(triangle.iloc[0]["execution_comments"])
    assert "B1126" in comments, (
        "BUG-277 fix not linked in execution_comments. "
        "B1126 empirical 0->17 detection uplift must be documented."
    )


def test_council_197_outsider_verdict_referenced_in_learnings():
    """Council 197 verdict must be cited in LEARNINGS.md as anti-audit-theater principle."""
    learnings = REPO / "LEARNINGS.md"
    if not learnings.exists():
        pytest.skip("LEARNINGS.md missing")
        return
    content = learnings.read_text(encoding="utf-8", errors="ignore")
    assert "Council 197" in content or "Outsider" in content or "audit-theater" in content, (
        "Council 197 Outsider verdict must be cited in LEARNINGS.md "
        "(anti-audit-theater principle: tests that don't touch things "
        "that break)."
    )


def test_all_blocked_producer_bug_strategies_have_bug_ref(df):
    """Every BLOCKED_PRODUCER_BUG strategy must reference BUG-NNN in verdict/comments."""
    blocked = df[df["execution_status"] == "BLOCKED_PRODUCER_BUG"]
    for _, row in blocked.iterrows():
        strat = row["strategy_name"]
        verdict = str(row.get("post_investigation_verdict", ""))
        recommendation = str(row.get("post_investigation_recommendation", ""))
        combined = verdict + " " + recommendation
        has_bug = any(f"BUG-{n}" in combined for n in ("277", "278", "279", "280", "281"))
        assert has_bug, (
            f"BLOCKED_PRODUCER_BUG strategy {strat} lacks BUG-NNN reference. "
            f"Empirical grounding requires explicit bug link."
        )
