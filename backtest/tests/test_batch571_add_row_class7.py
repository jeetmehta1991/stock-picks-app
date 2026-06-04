"""Batch 571 (2026-06-04) -- Stage 4 per-strategy deep-dive +
decide_approvals.py --add-row extension + Class 7 NEW_STRATEGY +
first 5 atomic decisions.

Source: owner directive 2026-06-04 chat-conversation:
  - "1 2 3 yes" -> news_sentiment_shift_long: Reject sizing +
    add Class 2 threshold loosen + add Class 7 short variant
  - "4 Doji loosen tolerance bands. DOnt reject." -> doji_at_support:
    Defer sizing + add Class 2 tolerance loosen
  - "We need to do this type of analysis for each strategy
    individually! This is exactly the fine tuning that is required."
    -> codified as feedback_per_strategy_deep_dive_stage4 memory
    + workflow Stage 4 discipline rule #6 + new Class 7

Pins:

  (1) --add-row creates a new owner-surfaced row with
      dimension_source='owner_added' (distinguishable from
      optimizer-extracted)
  (2) Class 7 NEW_STRATEGY is valid (in VALID_CLASSES) + maps to
      backtest/signals/screener.py config_touch_point
  (3) candidate_id for owner-added rows uses 'r4-owner-' prefix
  (4) initial history entry recorded when --to-status != Awaiting
  (5) all 5 B571 atomic decisions left a trace on the live
      approvals.json: 2 Approved Class 2 loosens + 1 Approved Class 7
      new strategy + 1 Rejected Class 4 + 1 Deferred Class 4
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]
APPROVALS = Path("C:/tmp/r4_optimization_candidates/approvals.json")
SCRIPT = REPO / "scripts" / "decide_approvals.py"


def _have_inputs() -> bool:
    return APPROVALS.exists() and SCRIPT.exists()


pytestmark = pytest.mark.skipif(
    not _have_inputs(),
    reason="R4 outputs absent (run B566-B570 first)",
)


@pytest.fixture
def tmp_approvals(tmp_path):
    p = tmp_path / "approvals.json"
    shutil.copy(APPROVALS, p)
    return p


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, timeout=30,
    )


def test_batch571_add_row_class7_creates_owner_added_row(tmp_approvals):
    """Pin (1) + (2) + (3) + (4)."""
    rc = _run(
        "--approvals", str(tmp_approvals),
        "--add-row",
        "--add-strategy", "test_new_strategy",
        "--add-class", "7",
        "--add-detail", "Test Class 7 new strategy proposal",
        "--to-status", "Approved",
        "--by", "test_owner",
        "--rationale", "test rationale",
    )
    assert rc.returncode == 0, f"exit {rc.returncode}; stderr={rc.stderr}"
    data = json.loads(tmp_approvals.read_text(encoding="utf-8"))
    added = [r for r in data["approvals"]
             if r["candidate_id"].startswith("r4-owner-")
             and r["strategy"] == "test_new_strategy"]
    assert len(added) == 1
    r = added[0]
    assert r["change_class"] == 7
    assert r["change_class_name"] == "NEW_STRATEGY"
    assert r["dimension_source"] == "owner_added"
    assert r["status"] == "Approved"
    assert "screener.py" in r["config_touch_point"]
    # History entry on initial Approve
    assert len(r["history"]) == 1
    assert r["history"][0]["to_status"] == "Approved"


def test_batch571_live_approvals_has_5_decisions(tmp_approvals):
    """Pin (5): live approvals.json reflects all 5 B571 decisions.

    Expected state post-B571 on live file:
      - news_sentiment_shift_long Class 4 -> Rejected
      - doji_at_support Class 4 -> Deferred (dependency=doji_at_support_tolerance_loosen)
      - news_sentiment_shift_long Class 2 -> Approved (owner-added)
      - news_sentiment_shift_short Class 7 -> Approved (owner-added)
      - doji_at_support Class 2 -> Approved (owner-added)
    """
    data = json.loads(tmp_approvals.read_text(encoding="utf-8"))
    rows = data["approvals"]

    # 1. news_sentiment_shift_long Class 4 Rejected
    news_class4 = [r for r in rows
                   if r["strategy"] == "news_sentiment_shift_long"
                   and r["change_class"] == 4]
    assert len(news_class4) == 1
    assert news_class4[0]["status"] == "Rejected"

    # 2. doji_at_support Class 4 was Deferred in B571; may have been
    # unblocked to Approved in B573 (paired Class 2 tolerance loosen
    # shipped). Either is valid post-B573.
    doji_class4 = [r for r in rows
                   if r["strategy"] == "doji_at_support"
                   and r["change_class"] == 4]
    assert len(doji_class4) == 1
    assert doji_class4[0]["status"] in {"Deferred", "Approved", "Implemented"}
    # The Deferred -> Approved flip in B573 keeps the history breadcrumb
    history_statuses = [h["to_status"] for h in doji_class4[0]["history"]]
    assert "Deferred" in history_statuses, (
        f"history must show the original B571 Deferred flip; got "
        f"{history_statuses}"
    )

    # 3. Class 2 loosen for news_sentiment_shift_long (owner-added Approved)
    news_class2 = [r for r in rows
                   if r["strategy"] == "news_sentiment_shift_long"
                   and r["change_class"] == 2
                   and r["dimension_source"] == "owner_added"]
    assert len(news_class2) == 1
    assert news_class2[0]["status"] == "Approved"

    # 4. Class 7 NEW_STRATEGY for news_sentiment_shift_short
    news_short = [r for r in rows
                  if r["strategy"] == "news_sentiment_shift_short"
                  and r["change_class"] == 7
                  and r["dimension_source"] == "owner_added"]
    assert len(news_short) == 1
    assert news_short[0]["status"] == "Approved"
    assert news_short[0]["change_class_name"] == "NEW_STRATEGY"

    # 5. Class 2 loosen for doji_at_support - Approved at B571,
    # may have been promoted to Implemented at B573
    doji_class2 = [r for r in rows
                   if r["strategy"] == "doji_at_support"
                   and r["change_class"] == 2
                   and r["dimension_source"] == "owner_added"]
    assert len(doji_class2) == 1
    assert doji_class2[0]["status"] in {"Approved", "Implemented"}
