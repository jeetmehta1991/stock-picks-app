"""Batch 575 (2026-06-04) -- STRATEGY_ROSTER.md auto-generator script.

Per owner directive 2026-06-04: "Update the strategy roster document,
create a table of each strategy, triggers, parameters of each criteria
in the triggers, other conditions etc. I will use it as a reference
table during this analysis."

`scripts/build_strategy_roster.py` introspects ALL_STRATEGIES, extracts
trigger logic + direction + category + signals_used + regime affinity,
and writes STRATEGY_ROSTER.md at the repo root with:
  - Total / direction / category counts
  - Full per-strategy table (205 rows × 8 cols)
  - SIGNAL_GLOSSARY section (hand-curated definitions; grows
    as Stage 4 walks encounter new signals)

Pins:

  (1) Script exit zero against current code state
  (2) STRATEGY_ROSTER.md exists at repo root after run
  (3) Doc contains a row for every strategy in ALL_STRATEGIES (count
      matches len(ALL_STRATEGIES))
  (4) Each row has the required 8 columns
  (5) Doji rows correctly show the _wide flags (B574 narrow-scope fix
      reflected in the trigger column)
  (6) SIGNAL_GLOSSARY section has at least the signals encountered in
      Stage 4 walks so far (doji, near_s1_wide, vol_spike_15x,
      news_sentiment_shift)
  (7) Regenerating produces identical content (idempotent)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "build_strategy_roster.py"
DOC = REPO / "STRATEGY_ROSTER.md"


@pytest.fixture(scope="module")
def regen_doc():
    """Run the generator once for the module; all tests inspect the
    same DOC."""
    rc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True, timeout=60,
    )
    assert rc.returncode == 0, (
        f"build_strategy_roster exit {rc.returncode}; "
        f"stderr:\n{rc.stderr[-2000:]}"
    )
    assert DOC.exists()
    return DOC.read_text(encoding="utf-8")


def test_batch575_script_runs(regen_doc):
    """Pin (1) + (2)."""
    assert len(regen_doc) > 1000


def test_batch575_row_count_matches_all_strategies(regen_doc):
    """Pin (3)."""
    from backtest.signals.screener import ALL_STRATEGIES
    n_rows = len(re.findall(r"^\| \d+ \| `[a-z_0-9]+`", regen_doc, re.MULTILINE))
    assert n_rows == len(ALL_STRATEGIES), (
        f"Strategy table has {n_rows} rows; ALL_STRATEGIES has "
        f"{len(ALL_STRATEGIES)}. Counts must match."
    )


def test_batch575_columns_present(regen_doc):
    """Pin (4). B576: Roster Status + Stage 4 Status columns added."""
    expected_headers = [
        "Name", "Category", "Direction", "Trigger",
        "Signals consumed", "Regime affinity",
        "Roster Status", "Stage 4 Status",
    ]
    for h in expected_headers:
        assert h in regen_doc, f"missing column header: {h}"


def test_batch575_doji_rows_show_wide_flags(regen_doc):
    """Pin (5): B574 narrow-scope fix reflected -> doji rows use
    near_s1_wide / near_r1_wide / at_key_fib_wide in their trigger."""
    # Locate the doji_at_support row
    m_long = re.search(
        r"`doji_at_support`[^\n]*",
        regen_doc,
    )
    assert m_long, "doji_at_support row missing"
    assert "near_s1_wide" in m_long.group(0), (
        f"doji_at_support trigger should reference near_s1_wide post-B574; "
        f"got:\n{m_long.group(0)}"
    )
    m_short = re.search(
        r"`doji_at_resistance_short`[^\n]*",
        regen_doc,
    )
    assert m_short, "doji_at_resistance_short row missing"
    assert "near_r1_wide" in m_short.group(0)


def test_batch578_projected_section_present(regen_doc):
    """B578: STRATEGY_ROSTER.md must include 'Projected Strategies'
    section sourced from STRATEGY_REGISTER.md Layer 4 per owner
    directive 2026-06-04."""
    assert "## Projected Strategies" in regen_doc
    # All 5 Layer 4 DECs must be listed
    for dec_id in ("DEC-141", "DEC-142", "DEC-143", "DEC-145", "DEC-176"):
        assert dec_id in regen_doc, f"Projected section missing {dec_id}"
    assert "Layer-2D" in regen_doc, "Layer 2D PENDING-FORM placeholder missing"
    assert "PENDING_OWNER_APPROVAL" in regen_doc
    # Note about future approval
    assert "will be approved" in regen_doc.lower() or "post-approval" in regen_doc.lower()


def test_batch578_strategy_roster_full_archived():
    """B578: STRATEGY_ROSTER_FULL.md must be archived (not at repo root)."""
    repo = Path(__file__).resolve().parents[2]
    full_at_root = repo / "STRATEGY_ROSTER_FULL.md"
    assert not full_at_root.exists(), (
        "STRATEGY_ROSTER_FULL.md should be archived; found at repo root"
    )
    # Should exist in archive/
    archive_dir = repo / "archive" / "2026-06-04-strategy-roster-full-archival"
    archive_file = archive_dir / "STRATEGY_ROSTER_FULL.md"
    assert archive_file.exists(), (
        f"STRATEGY_ROSTER_FULL.md missing from archive at {archive_file}"
    )


def test_batch575_glossary_has_core_signals(regen_doc):
    """Pin (6)."""
    for sig in ["doji", "near_s1_wide", "vol_spike_15x", "news_sentiment_shift",
                "hammer", "three_black_crows", "at_key_fib_wide"]:
        # Look for the signal in a glossary entry row: `| \`<sig>\` |`
        pattern = rf"\| `{re.escape(sig)}` \|"
        assert re.search(pattern, regen_doc), (
            f"SIGNAL_GLOSSARY missing entry for {sig!r}"
        )


def test_batch575_idempotent(regen_doc):
    """Pin (7): re-running produces identical content."""
    rc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True, timeout=60,
    )
    assert rc.returncode == 0
    second = DOC.read_text(encoding="utf-8")
    assert regen_doc == second, "regenerated doc differs from initial run"
