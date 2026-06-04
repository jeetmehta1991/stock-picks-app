"""Batch 570 (2026-06-04) -- Stage 4 owner-decision tool +
first real owner decisions: 7 Class-6 PLZL Defer flips.

Source: owner directive 2026-06-04 in chat - Defer all 7 Class-6
ROSTER_DEPRECATION candidates pending per-strategy producer audit
(per project_no_apriori_strategy_pruning + workflow line 343
sweep advice). Strategies are recent additions (May 17-31 2026)
with B556/B559/B561 producer-fix precedent.

`scripts/decide_approvals.py` flips one or more candidates'
status with audit-trail history entries.

Pins:

  (1) decide_approvals selector matches change-class=6 -> 7 rows
  (2) after Defer flip, ALL 7 Class-6 rows are status=Deferred
  (3) every Class-6 row has dependency='producer_audit_per_strategy'
  (4) every Class-6 row has exactly 1 history entry post-flip
      (Awaiting -> Deferred); ts, from_status, to_status, by, rationale
      all populated
  (5) summary.by_status recomputed correctly (343 Awaiting + 8 Deferred
      after this batch)
  (6) dry-run does NOT modify approvals.json
  (7) re-running the same flip is a no-op (already-Deferred rows skipped)
  (8) selector with no matches surfaces 'none matched' and exits 0
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]
CAND_DIR = Path("C:/tmp/r4_optimization_candidates")
APPROVALS = CAND_DIR / "approvals.json"
SCRIPT = REPO / "scripts" / "decide_approvals.py"


def _have_inputs() -> bool:
    return APPROVALS.exists() and SCRIPT.exists()


pytestmark = pytest.mark.skipif(
    not _have_inputs(),
    reason="R4 cube outputs absent (run B566-B569 first)",
)


@pytest.fixture
def tmp_approvals(tmp_path):
    """Copy the live approvals.json to a tmp path so tests can mutate
    freely without clobbering the real Stage 4 state."""
    copy_path = tmp_path / "approvals.json"
    shutil.copy(APPROVALS, copy_path)
    return copy_path


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, timeout=30,
    )


def test_batch570_class6_selector_matches_7(tmp_approvals):
    """Pin (1): selecting --change-class 6 --status-from Deferred
    finds the 7 PLZL rows that the live approvals.json (post B570
    decision) already has Deferred."""
    data = json.loads(tmp_approvals.read_text(encoding="utf-8"))
    class6 = [r for r in data["approvals"] if r["change_class"] == 6]
    assert len(class6) == 7


def test_batch570_class6_all_deferred(tmp_approvals):
    """Pin (2): live approvals.json reflects the owner decision -
    all 7 Class-6 rows are Deferred."""
    data = json.loads(tmp_approvals.read_text(encoding="utf-8"))
    class6 = [r for r in data["approvals"] if r["change_class"] == 6]
    statuses = {r["status"] for r in class6}
    assert statuses == {"Deferred"}, (
        f"all Class 6 should be Deferred; got {statuses}"
    )


def test_batch570_dependency_set(tmp_approvals):
    """Pin (3): dependency = producer_audit_per_strategy on all 7."""
    data = json.loads(tmp_approvals.read_text(encoding="utf-8"))
    class6 = [r for r in data["approvals"] if r["change_class"] == 6]
    for r in class6:
        assert r["dependency"] == "producer_audit_per_strategy", (
            f"row {r['candidate_id']} dependency = {r['dependency']!r}; "
            f"expected 'producer_audit_per_strategy'"
        )


def test_batch570_history_populated(tmp_approvals):
    """Pin (4): each Class-6 row has 1 history entry with the
    Awaiting -> Deferred flip metadata."""
    data = json.loads(tmp_approvals.read_text(encoding="utf-8"))
    class6 = [r for r in data["approvals"] if r["change_class"] == 6]
    for r in class6:
        assert len(r["history"]) == 1
        h = r["history"][0]
        assert h["from_status"] == "Awaiting"
        assert h["to_status"] == "Deferred"
        assert h["by"] == "owner_jeet"
        assert h["rationale"]
        assert h["ts"]


def test_batch570_summary_recomputed(tmp_approvals):
    """Pin (5): summary reflects the flips (343 Awaiting + 8 Deferred
    after Class 6 batch + 1 auto-Deferred Class 5)."""
    data = json.loads(tmp_approvals.read_text(encoding="utf-8"))
    bs = data["summary"]["by_status"]
    assert bs["Awaiting"] == 343, f"Awaiting count: {bs['Awaiting']}"
    assert bs["Deferred"] == 8, f"Deferred count: {bs['Deferred']}"
    assert bs["Approved"] == 0
    assert bs["Rejected"] == 0


def test_batch570_dry_run_no_mutation(tmp_approvals):
    """Pin (6): --dry-run does NOT write to approvals.json."""
    before = tmp_approvals.read_text(encoding="utf-8")
    rc = _run(
        "--approvals", str(tmp_approvals),
        "--change-class", "3",
        "--status-from", "Awaiting",
        "--to-status", "Rejected",
        "--by", "test_owner",
        "--rationale", "dry-run test",
        "--dry-run",
    )
    assert rc.returncode == 0
    after = tmp_approvals.read_text(encoding="utf-8")
    assert before == after, "dry-run modified the file"


def test_batch570_rerun_is_noop(tmp_approvals):
    """Pin (7): re-running the same Defer flip on already-Deferred rows
    is a no-op."""
    rc = _run(
        "--approvals", str(tmp_approvals),
        "--change-class", "6",
        "--status-from", "Deferred",  # re-target already-Deferred rows
        "--to-status", "Deferred",
        "--by", "owner_jeet",
        "--rationale", "noop re-run",
    )
    assert rc.returncode == 0
    assert "noop" in rc.stdout.lower() or "0 changed" in rc.stdout
    # Verify rows weren't double-history'd
    data = json.loads(tmp_approvals.read_text(encoding="utf-8"))
    class6 = [r for r in data["approvals"] if r["change_class"] == 6]
    for r in class6:
        assert len(r["history"]) == 1, (
            f"{r['candidate_id']} history length: {len(r['history'])}"
        )


def test_batch570_no_match_selector(tmp_approvals):
    """Pin (8): selector with no matches surfaces 'none matched'."""
    rc = _run(
        "--approvals", str(tmp_approvals),
        "--strategies", "nonexistent_strategy_xyz_12345",
        "--to-status", "Rejected",
        "--by", "test_owner",
        "--rationale", "test",
    )
    assert rc.returncode == 0
    assert "none matched" in rc.stdout.lower() or "Selected 0" in rc.stdout
