"""Batch 625 (2026-06-08) -- walk-commit fire-count pin per CHECKLIST
#105 (k) institutionalisation.

Source: scripts/walk_preflight.py + scripts/estimate_fire_count.py.
Per CHECKLIST #77 source-of-truth declaration.

Owner-directed option E (walk-template estimator integration): make
the CHECKLIST (k) fire-count projection requirement enforceable rather
than aspirational. This test scans recent git commits, identifies
which ones are Stage 4 walks (by subject-line pattern), and verifies
each walk commit message contains the `Fire-count projection:` token
emitted by walk_preflight.py.

WHY: B620 deletion of strat_squeeze_setup_event_only_long was driven
by an estimator finding that surfaced AFTER the B-twin was already
shipped in B615. If every walk had run the estimator pre-flight at
B615, we would have caught the FAIL_FIRE_STARVED verdict BEFORE the
B-twin landed - saving the round trip. This test enforces the
estimator invocation per walk commit going forward.

SCOPE:
  - Only commits AFTER B625 land are checked (forward-looking; past
    walks predate the token requirement)
  - Only commits whose subject matches the walk pattern (case-
    insensitive contains "stage 4 walk" OR "stage 4 re-walk" OR
    "Class 7 NEW" OR "walk per CHECKLIST")
  - Skipped: methodology batches, registry maintenance, manifest
    updates, the B625 commit itself (creates the requirement)

OPT-OUT: a walk commit can include
  `Fire-count projection: N/A - <reason>`
to indicate the projection doesn't apply (e.g., deleting a strategy,
docstring-only fix). The test accepts this opt-out.

Pins:
  (1) walk_preflight module imports cleanly
  (2) walk_preflight_one_line emits the FIRE_COUNT_TOKEN
  (3) walk_preflight_block emits the FIRE_COUNT_TOKEN
  (4) recent walk commits (post-B625) include the token (skipped if
      no qualifying commits exist yet)
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from scripts.walk_preflight import (
    FIRE_COUNT_TOKEN,
    walk_preflight_block,
    walk_preflight_one_line,
)


# Cutoff commit: commits ON or AFTER this hash must comply.
# B624 merge `1058af028` (R5 manifest); B625 (this batch) is the first
# batch where the token is enforced.
ENFORCEMENT_CUTOFF_BATCH = 625


def test_batch625_walk_preflight_imports():
    """Pin (1)."""
    assert callable(walk_preflight_block)
    assert callable(walk_preflight_one_line)
    assert FIRE_COUNT_TOKEN == "Fire-count projection:"


def test_batch625_one_line_emits_token():
    """Pin (2)."""
    out = walk_preflight_one_line(
        strategy="strat_test",
        proposed_gates=["close_above_open", "vol_below_avg"],
    )
    assert FIRE_COUNT_TOKEN in out
    # Sanity: should also include fires/yr number + verdict
    assert "fires/yr" in out
    assert "verdict:" in out


def test_batch625_block_emits_token():
    """Pin (3)."""
    out = walk_preflight_block(
        strategy="strat_test",
        proposed_gates=["close_above_open", "vol_below_avg"],
        pre_walk_gate_count=1,
    )
    assert FIRE_COUNT_TOKEN in out
    assert "Pre-flight per CHECKLIST #105 (k)" in out


# Pattern matchers
WALK_SUBJECT_RE = re.compile(
    r"(stage[- ]4[- ](?:re[- ])?walk|walk per CHECKLIST|Class 7 NEW)",
    re.IGNORECASE,
)
# B899 (2026-06-18) doc-sync exemption: doc-sync commits that REFERENCE
# walks ("Stage-4-walks-done" status updates) match WALK_SUBJECT_RE but
# are not walks themselves. Exclude them per CHECKLIST (k) intent
# (fire-count projection applies to walks that PROPOSE GATE CHANGES, not
# status updates).
DOC_SYNC_SUBJECT_RE = re.compile(
    r"(doc[- ]sync|R4[- ]complete|R5[- ]blocked|stage[- ]4[- ]walks[- ]done)",
    re.IGNORECASE,
)
BATCH_NUMBER_RE = re.compile(r"\bBatch\s+(\d+)\b|^Merge batch/(\d+)\b", re.IGNORECASE)


def _get_walk_commits_since_b625() -> list[tuple[str, str, int]]:
    """Run `git log` from main, parse subject + body, return list of
    (sha, full_message, batch_number) for commits AFTER ENFORCEMENT_CUTOFF
    _BATCH whose subject matches the walk pattern."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%H%x00%B%x1e", "main"],
            capture_output=True, check=True,
            cwd=Path(__file__).resolve().parents[2],
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    # Decode bytes manually with errors='replace' to survive non-UTF8
    # codepoints in old commit messages.
    raw_stdout = result.stdout.decode("utf-8", errors="replace")

    commits = []
    for raw in raw_stdout.split("\x1e"):
        raw = raw.strip()
        if not raw or "\x00" not in raw:
            continue
        sha, _, msg = raw.partition("\x00")
        subject = msg.split("\n", 1)[0]
        # Extract batch number
        m = BATCH_NUMBER_RE.search(subject)
        if not m:
            continue
        batch_num = int(m.group(1) or m.group(2))
        if batch_num <= ENFORCEMENT_CUTOFF_BATCH:
            continue
        # Walk-pattern match
        if not WALK_SUBJECT_RE.search(subject):
            continue
        # B899 exemption: skip doc-sync commits that REFERENCE walks but
        # are not walks themselves.
        if DOC_SYNC_SUBJECT_RE.search(subject):
            continue
        commits.append((sha[:10], msg, batch_num))
    return commits


def test_batch625_recent_walk_commits_include_fire_count_token():
    """Pin (4): every walk commit AFTER ENFORCEMENT_CUTOFF_BATCH (B625)
    must include the FIRE_COUNT_TOKEN in its commit message.

    Skipped if no qualifying commits exist yet (forward-looking pin).
    """
    walk_commits = _get_walk_commits_since_b625()
    if not walk_commits:
        pytest.skip(
            f"No walk commits found AFTER batch {ENFORCEMENT_CUTOFF_BATCH}; "
            f"pin is forward-looking and waits for the first post-B625 walk."
        )
    missing = []
    for sha, msg, batch in walk_commits:
        if FIRE_COUNT_TOKEN not in msg:
            missing.append(f"  {sha} (B{batch}): {msg.split(chr(10), 1)[0]}")
    if missing:
        pytest.fail(
            f"Walk commits missing '{FIRE_COUNT_TOKEN}' token "
            f"(CHECKLIST k requirement). Either run "
            f"scripts/walk_preflight.py and include the output in the "
            f"commit message, or add explicit opt-out: "
            f"'{FIRE_COUNT_TOKEN} N/A - <reason>'. Affected commits:\n"
            + "\n".join(missing)
        )
