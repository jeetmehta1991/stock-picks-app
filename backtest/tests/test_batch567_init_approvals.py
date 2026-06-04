"""Batch 567 (2026-06-03) -- Stage 4 step 2 of 4 per
PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md.

Source: owner directive 2026-06-03 "lets start as per workflow".

`scripts/init_approvals.py` reads r4_proposed_changes.json (B566)
and writes approvals.json with all rows seeded Awaiting except
Class 5 which auto-DEFERRED (workflow line 337).

Pins:

  (1) initializer exits 0 against the R4 extraction
  (2) approvals.json has 'approvals' list + 'summary' + 'version' keys
  (3) every row has all required keys
  (4) Class 5 rows are auto-status='Deferred' with non-empty rationale
      + dependency='phase_1b_alpha_transition'
  (5) non-Class-5 rows default to status='Awaiting'
  (6) summary.by_status totals match the rows
  (7) status_set_by='system_init' for all rows at init time
  (8) re-running without --force REFUSES (audit trail discipline per
      workflow lines 344-345 - in-flight owner decisions must not be
      clobbered)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]
CAND_DIR = Path("C:/tmp/r4_optimization_candidates")
PROPOSED = CAND_DIR / "r4_proposed_changes.json"
APPROVALS = CAND_DIR / "approvals.json"


def _have_inputs() -> bool:
    return CAND_DIR.exists() and PROPOSED.exists()


pytestmark = pytest.mark.skipif(
    not _have_inputs(),
    reason="R4 cube optimizer outputs absent (run B566 extractor first)",
)


REQUIRED_KEYS = {
    "candidate_id", "strategy", "change_class", "change_class_name",
    "change_detail", "dimension_source", "structured", "rationale_metrics",
    "config_touch_point", "status", "status_set_at", "status_set_by",
    "rationale", "dependency", "conflicts", "history",
}


@pytest.fixture(scope="module")
def approvals(tmp_path_factory):
    """Module-scoped: init_approvals writes to tmp_path so the LIVE
    approvals.json (which holds owner Stage 4 decisions per CHECKLIST
    #67 source-of-truth) is NEVER touched. Previously this fixture used
    --force on APPROVALS itself and clobbered owner state on every
    pyramid run; B570a follow-on rewrote it."""
    tmp = tmp_path_factory.mktemp("approvals_b567") / "approvals.json"
    rc = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "init_approvals.py"),
            "--input",  str(PROPOSED),
            "--output", str(tmp),
            "--force",
        ],
        capture_output=True, text=True, timeout=30,
    )
    assert rc.returncode == 0, (
        f"init_approvals exit {rc.returncode}; stderr:\n{rc.stderr}"
    )
    return json.loads(tmp.read_text(encoding="utf-8"))


def test_batch567_init_exit_zero(approvals):
    assert isinstance(approvals, dict)


def test_batch567_top_level_keys(approvals):
    """Pin (2)."""
    assert "version" in approvals
    assert "summary" in approvals
    assert "approvals" in approvals
    assert "generated_at" in approvals
    assert isinstance(approvals["approvals"], list)
    assert len(approvals["approvals"]) > 100  # R4 has 351; loose guard


def test_batch567_row_keys(approvals):
    """Pin (3)."""
    for r in approvals["approvals"]:
        missing = REQUIRED_KEYS - set(r.keys())
        assert not missing, f"row {r.get('candidate_id')} missing: {missing}"


def test_batch567_class5_auto_deferred(approvals):
    """Pin (4) - workflow line 337 mandate."""
    class5 = [r for r in approvals["approvals"] if r["change_class"] == 5]
    assert class5, "expected >=1 Class 5 row from R4 extraction"
    for r in class5:
        assert r["status"] == "Deferred", (
            f"Class 5 must be auto-Deferred per workflow line 337; "
            f"got {r['status']} for {r['candidate_id']}"
        )
        assert r["rationale"], "Class 5 Deferred must have non-empty rationale"
        assert r["dependency"] == "phase_1b_alpha_transition", (
            f"Class 5 dependency must be phase_1b_alpha_transition; "
            f"got {r['dependency']!r}"
        )


def test_batch567_non_class5_awaiting(approvals):
    """Pin (5)."""
    other = [r for r in approvals["approvals"] if r["change_class"] != 5]
    assert other
    for r in other:
        assert r["status"] == "Awaiting", (
            f"non-Class-5 must default to Awaiting; got {r['status']} "
            f"for {r['candidate_id']} (class {r['change_class']})"
        )
        # Awaiting rows must NOT have a dependency (only Deferred rows do)
        assert not r["dependency"]


def test_batch567_summary_matches_rows(approvals):
    """Pin (6)."""
    s = approvals["summary"]
    total_status = sum(s["by_status"].values())
    assert total_status == s["total"]
    # Recount from the rows
    actual_status = {"Awaiting": 0, "Approved": 0, "Rejected": 0, "Deferred": 0}
    actual_class = {}
    for r in approvals["approvals"]:
        actual_status[r["status"]] += 1
        k = str(r["change_class"])
        actual_class[k] = actual_class.get(k, 0) + 1
    for k, v in actual_status.items():
        assert s["by_status"][k] == v, (
            f"summary.by_status[{k}] = {s['by_status'][k]}, actual = {v}"
        )
    for k, v in actual_class.items():
        assert s["by_class"][k] == v


def test_batch567_status_set_by_system_init(approvals):
    """Pin (7)."""
    for r in approvals["approvals"]:
        assert r["status_set_by"] == "system_init"
        assert r["status_set_at"], "status_set_at must be non-empty"
        # history empty at init
        assert r["history"] == []


def test_batch567_refuses_overwrite_without_force(tmp_path, approvals):
    """Pin (8) - audit-trail discipline (workflow lines 344-345). The
    second run without --force must REFUSE so in-flight owner decisions
    can't be silently clobbered.

    Uses tmp_path (not the LIVE APPROVALS) - the live owner-decision
    state must NEVER be touched by tests per CHECKLIST #67."""
    tmp_target = tmp_path / "approvals.json"
    # Seed the target so the second run sees an existing file
    tmp_target.write_text('{"approvals":[]}', encoding="utf-8")
    rc = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "init_approvals.py"),
            "--input",  str(PROPOSED),
            "--output", str(tmp_target),
            # NO --force
        ],
        capture_output=True, text=True, timeout=30,
    )
    assert rc.returncode != 0, (
        f"second run without --force must fail; got exit {rc.returncode}"
    )
    assert "exists" in rc.stderr.lower() or "force" in rc.stderr.lower()
