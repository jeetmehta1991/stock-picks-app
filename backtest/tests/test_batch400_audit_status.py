"""Batch 400 (2026-05-27): verify zero PARTIAL-IMPL-HELPER-ONLY DECs remain.

Source (per CHECKLIST #77): owner directive 2026-05-27 "all wired but
not engine-consumed items activate or close".  Batch 400 swept 20 DECs
that had been flagged PARTIAL-IMPL-HELPER-ONLY in AUDIT_INDEX.md:

  - 4 status-drift items (Batch 374 shipped; flag not updated): DEC-230/231/234/246
  - 6 Sprint 8+/9+ deferred: DEC-425/426/427/428/429/430
  - 4 Phase A toolkit shipped: DEC-459/463/467/473
  - 5 owner-deferred / Sprint 1+ / Stage 3+: DEC-378/417/436/456/495
  - 1 partially-superseded: DEC-433

This test pins the post-Batch-400 state so future audit cycles can
detect any regression (status flag drifting back).

Run: pytest backtest/tests/test_batch400_audit_status.py -v
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
AUDIT = REPO / "AUDIT_INDEX.md"

# DECs flipped in Batch 400 + their expected new status
BATCH_400_UPDATES = {
    "230": "RESOLVED-IMPLEMENTED",
    "231": "RESOLVED-IMPLEMENTED",
    "234": "RESOLVED-IMPLEMENTED",
    "246": "RESOLVED-IMPLEMENTED",
    "425": "RESOLVED-DECIDED-DEFERRED",
    "426": "RESOLVED-DECIDED-DEFERRED",
    "427": "RESOLVED-DECIDED-DEFERRED",
    "428": "RESOLVED-DECIDED-DEFERRED",
    "429": "RESOLVED-DECIDED-DEFERRED",
    "430": "RESOLVED-DECIDED-DEFERRED",
    "459": "RESOLVED-IMPLEMENTED",
    "463": "RESOLVED-IMPLEMENTED",
    "467": "RESOLVED-IMPLEMENTED",
    "473": "RESOLVED-IMPLEMENTED",
    "378": "RESOLVED-DECIDED-DEFERRED",
    "417": "RESOLVED-DECIDED-DEFERRED",
    "436": "RESOLVED-DECIDED-DEFERRED",
    "456": "RESOLVED-DECIDED-DEFERRED",
    "495": "RESOLVED-DECIDED-DEFERRED",
    "433": "RESOLVED-PARTIALLY-SUPERSEDED",
}


def _table_rows():
    """Iterate over AUDIT_INDEX.md table rows that match the DECISION-N pattern."""
    src = AUDIT.read_text(encoding="utf-8")
    # Pattern: a single logical row may span multiple lines, but the
    # row always starts with `| **DECISION-N** |` at column 0.
    # Split into rows by looking for ^| **DECISION- markers.
    pattern = re.compile(r"^\| \*\*DECISION-(\d+)\*\* \|.*?(?=^\| \*\*DECISION-|\Z)",
                         re.MULTILINE | re.DOTALL)
    return [(m.group(1), m.group(0)) for m in pattern.finditer(src)]


def test_audit_index_exists():
    assert AUDIT.exists(), f"AUDIT_INDEX.md missing at {AUDIT}"


def test_no_partial_impl_helper_only_remain():
    """Hard gate: no DEC in the table may carry PARTIAL-IMPL-HELPER-ONLY status."""
    src = AUDIT.read_text(encoding="utf-8")
    violations = []
    for dec_num, row in _table_rows():
        # Status is the cell after the last `|` before status; simple check:
        # if row contains PARTIAL-IMPL-HELPER-ONLY followed by `|` (status cell),
        # it's still flagged.
        if re.search(r"PARTIAL-IMPL-HELPER-ONLY\s*\|", row):
            violations.append(dec_num)
    assert not violations, (
        f"PARTIAL-IMPL-HELPER-ONLY still flagged for DECs: {violations}.  "
        f"Per Batch 400, all 20 must be either RESOLVED-IMPLEMENTED, "
        f"RESOLVED-DECIDED-DEFERRED, RESOLVED-PARTIALLY-SUPERSEDED, or "
        f"SUPERSEDED.  Status drift detected."
    )


@pytest.mark.parametrize("dec_num,expected_status", list(BATCH_400_UPDATES.items()))
def test_batch_400_dec_status(dec_num, expected_status):
    """Each Batch 400 DEC must end with the expected status."""
    rows = dict(_table_rows())
    assert dec_num in rows, f"DEC-{dec_num} row not found in AUDIT_INDEX.md"
    row = rows[dec_num]
    # Status cell appears late in the row; check it's present after the
    # last Batch 400 annotation
    assert "Batch 400" in row, (
        f"DEC-{dec_num} missing Batch 400 annotation (status correction "
        f"not applied)"
    )
    assert expected_status in row, (
        f"DEC-{dec_num}: expected status `{expected_status}` not found in row"
    )


def test_total_batch_400_dec_count_is_20():
    assert len(BATCH_400_UPDATES) == 20


def test_engine_consumption_evidence_present_for_resolved_implemented():
    """Each Category-A/C DEC marked RESOLVED-IMPLEMENTED must cite engine
    consumption evidence in its body (line refs, module paths, etc)."""
    rows = dict(_table_rows())
    cat_a_c_resolved = [d for d, s in BATCH_400_UPDATES.items()
                        if s == "RESOLVED-IMPLEMENTED"]
    # Each must have an engine consumption evidence keyword
    evidence_keywords = ("regime_filter", "cube_populator", "ab_orchestrator",
                         "structured_logger", "ticker_lifecycle_events",
                         "state_augmentation", "agent_gate_config",
                         "our_fundamentals_toolkit", "OUR_AGENT_STATE_NEW_FIELDS",
                         "arm_a_rules_only", "quant_audit")
    for dec_num in cat_a_c_resolved:
        row = rows[dec_num]
        assert any(kw in row for kw in evidence_keywords), (
            f"DEC-{dec_num} marked RESOLVED-IMPLEMENTED but Batch 400 "
            f"annotation lacks engine-consumption evidence (no match in "
            f"{evidence_keywords})"
        )
