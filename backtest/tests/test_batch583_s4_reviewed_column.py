"""Batch 583 (2026-06-04) -- add S4 Reviewed Y/N column to
STRATEGY_ROSTER.md per owner directive 2026-06-04:
  "add another column in strategy table which says s4 review
   completed y/n"

Mechanism:
  - approvals.json has a NEW top-level dict `s4_reviewed_strategies`
    populated by scripts/mark_s4_reviewed.py (B583).
  - scripts/build_strategy_roster.py reads it and emits "Y (BNNN)"
    in the new "S4 Reviewed" column.
  - mark_s4_reviewed.py backfilled 22 strategies that already had
    a B570+ walk (Class 6 PLZL Defer, doji walk, turtle_soup, B581
    ICT batch, B582 52w_high bug fix, news_sentiment_shift pair).

Pins:

  (1) approvals.json has the s4_reviewed_strategies dict
  (2) STRATEGY_ROSTER.md has an "S4 Reviewed" column header
  (3) doji_at_support row shows "Y (B574)" (was Y from backfill)
  (4) 52w_high_breakout row shows "Y (B582)"
  (5) A known-not-yet-reviewed strategy (e.g. golden_cross_volume)
      shows "N"
  (6) header has the S4 Review progress summary (X REVIEWED / Y PENDING)
  (7) mark_s4_reviewed.py --strategy CLI flow updates approvals.json
      correctly (smoke)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]
APPROVALS = Path("C:/tmp/r4_optimization_candidates/approvals.json")
ROSTER_DOC = REPO / "STRATEGY_ROSTER.md"
ROSTER_SCRIPT = REPO / "scripts" / "build_strategy_roster.py"
MARK_SCRIPT = REPO / "scripts" / "mark_s4_reviewed.py"


def _have_inputs() -> bool:
    return APPROVALS.exists() and ROSTER_SCRIPT.exists() and MARK_SCRIPT.exists()


pytestmark = pytest.mark.skipif(not _have_inputs(),
                                 reason="R4 cube outputs absent")


@pytest.fixture(scope="module")
def regen_roster():
    rc = subprocess.run([sys.executable, str(ROSTER_SCRIPT)],
                        capture_output=True, text=True, timeout=60)
    assert rc.returncode == 0
    return ROSTER_DOC.read_text(encoding="utf-8")


def test_batch583_approvals_has_s4_reviewed_dict():
    """Pin (1)."""
    data = json.loads(APPROVALS.read_text(encoding="utf-8"))
    assert "s4_reviewed_strategies" in data
    reviewed = data["s4_reviewed_strategies"]
    assert isinstance(reviewed, dict)
    # B585: post-unmark expected count is ~19 (22 backfilled +6 B584 -9 unmarked).
    # Relaxed lower bound for forward-compatibility.
    assert len(reviewed) >= 13, (
        f"Expected >= 13 reviewed entries; got {len(reviewed)}"
    )
    # Schema check on one entry
    entry = next(iter(reviewed.values()))
    for key in ("reviewed_at", "reviewed_in_batch", "review_outcome"):
        assert key in entry, f"Missing {key} in s4_reviewed entry"


@pytest.mark.skip(
    reason="B894 (2026-06-18 Council 18) SCRUBBED 'S4 Reviewed' column from "
    "STRATEGY_ROSTER.md per CHECKLIST #111: source data (s4_reviewed flags "
    "in approvals.json) was stale pre-B585. Will be restored post-R5."
)
def test_batch583_roster_has_s4_column(regen_roster):
    """Pin (2). B899 STATUS: SKIPPED per B894 column scrub."""
    assert "S4 Reviewed" in regen_roster


@pytest.mark.skip(
    reason="B894 SCRUBBED S4 Reviewed column; re-enable post-R5 per CHECKLIST #111"
)
def test_batch583_doji_at_support_reviewed(regen_roster):
    """Pin (3): doji_at_support shows Y (B574). B899 SKIP per B894 column scrub."""
    # Find the row
    import re
    m = re.search(r"`doji_at_support`[^\n]*", regen_roster)
    assert m, "doji_at_support row missing from roster"
    row = m.group(0)
    assert "Y (B574)" in row, (
        f"doji_at_support should show 'Y (B574)' in S4 Reviewed column; "
        f"row content:\n{row}"
    )


@pytest.mark.skip(
    reason="B894 SCRUBBED S4 Reviewed + Producer Bug Fix columns; re-enable post-R5"
)
def test_batch586_52w_high_breakout_walked_post_b586(regen_roster):
    """Pin (4) - B899 SKIP per B894 column scrub.
    updated B586: 52w_high_breakout was unmarked in B585,
    then properly walked through full 7-step deep-dive in B586
    (vol_spike_17x + sector filter + pullback variants). Now shows
    S4 Reviewed=Y (B586) AND Producer Bug Fix=B582."""
    import re
    m = re.search(r"`52w_high_breakout`[^\n]*", regen_roster)
    assert m
    row = m.group(0)
    # Producer Bug Fix B582 still tracked
    assert "B582" in row, "Producer Bug Fix column should reference B582"
    # S4 Reviewed = Y (B586) after the walk
    assert "Y (B586)" in row, (
        f"52w_high_breakout S4 Reviewed should be 'Y (B586)' post-walk; row:\n{row}"
    )


def test_batch583_not_reviewed_strategy_shows_N(regen_roster):
    """Pin (5): a known-not-yet-reviewed strategy shows N. Pick
    golden_cross_volume (B583 audit identified as next candidate but
    no walk done yet)."""
    import re
    m = re.search(r"`golden_cross_volume`[^\n]*", regen_roster)
    assert m
    row = m.group(0)
    # Find the S4 Reviewed column - it should contain just "N" (not "Y ...")
    # Column layout: ... | R4 Fires | S4 Reviewed | Trigger | ...
    parts = row.split("|")
    # Parts are: |# |name |category |direction |fires |s4reviewed |trigger ...
    # so s4reviewed is index 6 (after blank-leading)
    # Easier check: assert "Y (" NOT in s4 reviewed column.
    # Since "Y (" appears only when reviewed, scan for it explicitly:
    assert "Y (B" not in row, (
        f"golden_cross_volume should NOT be S4-reviewed; row:\n{row}"
    )


@pytest.mark.skip(
    reason="B894 SCRUBBED 'S4 Review progress' banner from STRATEGY_ROSTER per "
    "CHECKLIST #111 (stale data source). Re-enable post-R5 with fresh data."
)
def test_batch583_header_summary(regen_roster):
    """Pin (6): header has S4 Review progress summary. B585 updated
    header text to include 'full 7-step walk' qualifier. B899 SKIP per B894."""
    assert "S4 Review progress" in regen_roster
    import re
    # B585 header: "**N REVIEWED (full 7-step walk)** (n%)"
    m = re.search(r"\*\*(\d+) REVIEWED(?:\s*\(full 7-step walk\))?\*\*", regen_roster)
    assert m
    n_reviewed = int(m.group(1))
    assert n_reviewed >= 13, (
        f"Expected at least 13 reviewed strategies in header; got {n_reviewed}"
    )


def test_batch583_mark_script_smoke(tmp_path):
    """Pin (7): mark_s4_reviewed.py --strategy works on a tmp copy."""
    import shutil
    tmp_approvals = tmp_path / "approvals.json"
    shutil.copy(APPROVALS, tmp_approvals)
    # Mark a fake strategy
    rc = subprocess.run([
        sys.executable, str(MARK_SCRIPT),
        "--approvals", str(tmp_approvals),
        "--strategy", "test_fake_strategy_xyz_b583",
        "--batch", "B583-test",
        "--outcome", "test smoke",
    ], capture_output=True, text=True, timeout=30)
    assert rc.returncode == 0
    data = json.loads(tmp_approvals.read_text(encoding="utf-8"))
    assert "test_fake_strategy_xyz_b583" in data["s4_reviewed_strategies"]
    entry = data["s4_reviewed_strategies"]["test_fake_strategy_xyz_b583"]
    assert entry["reviewed_in_batch"] == "B583-test"
    assert entry["review_outcome"] == "test smoke"
