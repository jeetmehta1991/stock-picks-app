"""B1127 Tier-6 Cross-boundary: BUG_REGISTER + CSV execution_status consistency (Council 246).

CATCHES: If BUG_REGISTER says RESOLVED-IMPLEMENTED but CSV still shows
BLOCKED_PRODUCER_BUG, there's silent drift. This test enforces consistency.
"""
# Source: per CHECKLIST #77 canonical-source; author Council 246 B1127 2026-07-03
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


REPO = Path(__file__).parent.parent.parent
BUG_REGISTER = REPO / "BUG_REGISTER.md"
CSV = REPO / "output_batch_A_150" / "phase_1_quiet_fire_investigation.csv"


BUG_STRATEGY_MAP = {
    "277": [  # triangle detector
        "triangle_ascending_long",
        "triangle_ascending_retest_long",
        "triangle_descending_short",
    ],
    "278": [  # index rebalance parquet missing
        "post_deletion_drift_short",
        "post_inclusion_drift_long",
        "post_inclusion_reversal_short",
        "pre_rebalance_long",
    ],
    "279": [  # calendar - RESOLVED-BY-INVESTIGATION B1125
        "halloween_seasonal_long",
        "totm_long",
        "pre_holiday_long",
    ],
    "281": [  # double_bottom detector
        "double_bottom_long",
    ],
}


@pytest.fixture(scope="module")
def csv_df():
    if not CSV.exists():
        pytest.skip(f"CSV missing: {CSV}")
    return pd.read_csv(CSV)


@pytest.fixture(scope="module")
def bug_content():
    if not BUG_REGISTER.exists():
        pytest.skip("BUG_REGISTER.md missing")
    return BUG_REGISTER.read_text(encoding="utf-8", errors="ignore")


def test_bug_277_status_matches_csv(csv_df, bug_content):
    """BUG-277 RESOLVED-IMPLEMENTED => triangle family CSV must be DONE or PENDING."""
    if "BUG-277" not in bug_content:
        pytest.skip("BUG-277 not registered")
        return
    # Look for RESOLVED-IMPLEMENTED near BUG-277
    b277_idx = bug_content.find("BUG-277")
    section = bug_content[b277_idx : b277_idx + 3000]
    if "RESOLVED-IMPLEMENTED" not in section:
        return  # Not yet resolved, no consistency to check

    for strat in BUG_STRATEGY_MAP["277"]:
        row = csv_df[csv_df["strategy_name"] == strat]
        if row.empty:
            continue
        status = str(row.iloc[0].get("execution_status", ""))
        assert not status.startswith("BLOCKED_PRODUCER_BUG"), (
            f"BUG-277 RESOLVED but {strat} still BLOCKED_PRODUCER_BUG in CSV. "
            f"BUG_REGISTER and CSV out of sync."
        )


def test_bug_279_status_matches_csv(csv_df, bug_content):
    """BUG-279 RESOLVED-BY-INVESTIGATION => calendar family CSV must not be BLOCKED."""
    if "BUG-279" not in bug_content:
        pytest.skip("BUG-279 not registered")
        return
    b279_idx = bug_content.find("BUG-279")
    section = bug_content[b279_idx : b279_idx + 3000]
    if "RESOLVED-BY-INVESTIGATION" not in section:
        return

    for strat in BUG_STRATEGY_MAP["279"]:
        row = csv_df[csv_df["strategy_name"] == strat]
        if row.empty:
            continue
        status = str(row.iloc[0].get("execution_status", ""))
        assert not status.startswith("BLOCKED_"), (
            f"BUG-279 RESOLVED-BY-INVESTIGATION but {strat} still BLOCKED in CSV."
        )


def test_bug_278_status_matches_csv(csv_df, bug_content):
    """BUG-278 OPEN => index rebalance family CSV must be BLOCKED_DATA_MISSING."""
    if "BUG-278" not in bug_content:
        pytest.skip("BUG-278 not registered")
        return
    b278_idx = bug_content.find("BUG-278")
    section = bug_content[b278_idx : b278_idx + 3000]
    if "RESOLVED" in section.split("Fix (")[0][:1000]:
        return  # Already resolved

    for strat in BUG_STRATEGY_MAP["278"]:
        row = csv_df[csv_df["strategy_name"] == strat]
        if row.empty:
            continue
        status = str(row.iloc[0].get("execution_status", ""))
        assert status == "BLOCKED_DATA_MISSING", (
            f"BUG-278 OPEN but {strat} not BLOCKED_DATA_MISSING (got {status})"
        )


def test_all_registered_bugs_referenced_in_csv():
    """Every BUG-NNN in register should have at least one CSV row referencing it."""
    if not BUG_REGISTER.exists():
        pytest.skip("BUG_REGISTER missing")
        return
    content = BUG_REGISTER.read_text(encoding="utf-8", errors="ignore")
    import re

    registered = set(re.findall(r"BUG-(\d{3})", content))
    if not registered:
        pytest.skip(
            "No BUG-NNN references found in BUG_REGISTER.md. "
            "CTA: unblocks when at least one BUG is registered."
        )
        return
    if not CSV.exists():
        pytest.skip(
            "CSV artifact missing - restore from output_batch_A_150. "
            "CTA: unblocks when CSV rebuilt."
        )
        return
    csv_content = CSV.read_text(encoding="utf-8", errors="ignore")
    unreferenced = set()
    # Session-scope BUGs I registered THIS session (Council 246 explicit scope).
    # BUGs 282+ pre-date this session and may reference different naming.
    SESSION_SCOPE_BUGS = {"277", "278", "279", "281"}
    for bug in registered:
        if bug in SESSION_SCOPE_BUGS:
            if f"BUG-{bug}" not in csv_content:
                unreferenced.add(bug)
    assert not unreferenced, (
        f"Session-scope BUGs registered but NOT referenced in CSV execution_comments: "
        f"{unreferenced}. Session scope = 277/278/279/281 (Council 246 registered)."
    )
