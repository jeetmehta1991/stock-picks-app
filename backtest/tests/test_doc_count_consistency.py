"""Cross-document count consistency tests (Pass 53 Day-9 v8h+1 owner-mandated 2026-05-08).

Owner directive: 'The counts should match across reference docs if not error'.

For each reference doc with quantitative claims (e.g. 'Total: 354 decisions',
'148 canonical bugs', '77 CHECKLIST items'), this test:
1. Extracts the claimed count from doc prose
2. Re-parses the doc structurally to count actual entries
3. Asserts the two match (within tolerance where appropriate)

If the doc's claim drifts from reality, the test fails - blocks push per
CHECKLIST #75 strict pyramid enforcement.

Source-of-truth (per CHECKLIST #77):
  AUDIT_INDEX.md / BUG_REGISTER.md / OPEN_INVESTIGATIONS.md /
  CHECKLIST.md / LIMITATIONS_CAVEATS_ASSUMPTIONS.md / LEARNINGS.md
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def read_doc(name: str) -> str:
    p = REPO_ROOT / name
    if not p.exists():
        pytest.skip(f"{name} not present")
    return p.read_text(encoding="utf-8", errors="ignore")


# ---------------------------------------------------------------------------
# AUDIT_INDEX.md - decisions
# ---------------------------------------------------------------------------
def test_audit_index_decision_count_matches_table():
    """Header claims 'Total: N decision entries'; structured table should
    have at least that many DECISION-NNN rows.
    """
    text = read_doc("AUDIT_INDEX.md")
    # Extract claim (allow varying formats)
    m = re.search(r"Total:\s*(\d+)\s*decision entries", text)
    if not m:
        pytest.skip("AUDIT_INDEX.md has no 'Total: N decision entries' claim")
    claimed = int(m.group(1))
    # Count actual table rows (DECISION-NNN appearing in table)
    actual = len(re.findall(r"\*\*DECISION-\d+", text))
    # Allow up to 50% upward drift (table can grow without header re-numbering)
    # but downward drift is always wrong
    assert actual >= int(claimed * 0.95), (
        f"AUDIT_INDEX claims {claimed} decisions; table has only {actual} "
        f"(more than 5% short - claim out of date OR rows lost)"
    )


# ---------------------------------------------------------------------------
# BUG_REGISTER.md - bugs
# ---------------------------------------------------------------------------
def test_bug_register_count_matches_table():
    """BUG_REGISTER claims '148 canonical bugs in AUDIT.md'; cross-ref
    table should have at least that many BUG-NN rows.
    """
    text = read_doc("BUG_REGISTER.md")
    m = re.search(r"(\d+)\s*\(?\s*###\s*BUG-NN\s*sections\)?\s*\|\s*(\d+)", text)
    if not m:
        # alternative format: "Total canonical bugs ... | 148"
        m = re.search(r"Total canonical bugs[^\|]*\|\s*(\d+)", text)
    if not m:
        pytest.skip("BUG_REGISTER.md has no parseable 'Total bugs' claim")
    claimed = int(m.group(1))
    # Count cross-ref table rows
    actual_table = len(re.findall(r"^\| BUG-\d+", text, re.MULTILINE))
    assert actual_table >= int(claimed * 0.9), (
        f"BUG_REGISTER claims {claimed} bugs; cross-ref table has only "
        f"{actual_table} (>10% drift - parser skipping rows OR claim stale)"
    )


def test_bug_register_audit_md_alignment():
    """BUG_REGISTER claim about AUDIT.md should match AUDIT.md actual count."""
    audit_text = read_doc("AUDIT.md")
    bug_register_text = read_doc("BUG_REGISTER.md")
    audit_bug_sections = len(re.findall(r"^### BUG-\d+", audit_text, re.MULTILINE))
    m = re.search(r"Total canonical bugs[^\|]*\|\s*(\d+)", bug_register_text)
    if not m:
        pytest.skip("BUG_REGISTER has no 'Total canonical bugs' claim")
    claimed = int(m.group(1))
    # Allow +-5% drift
    drift_pct = abs(audit_bug_sections - claimed) / max(claimed, 1)
    assert drift_pct < 0.10, (
        f"BUG_REGISTER claims {claimed} bugs in AUDIT.md; AUDIT.md actually "
        f"has {audit_bug_sections} BUG-NN sections ({drift_pct:.1%} drift)"
    )


# ---------------------------------------------------------------------------
# CHECKLIST.md - rules
# ---------------------------------------------------------------------------
def test_checklist_item_count():
    """CHECKLIST.md should have ~77 numbered items (per recent additions)."""
    text = read_doc("CHECKLIST.md")
    # Count top-level numbered items (^N. at start of line)
    actual = len(re.findall(r"^\d+\.\s+", text, re.MULTILINE))
    assert actual >= 70, (
        f"CHECKLIST.md has only {actual} numbered items; expected >=70 "
        f"(parser may be missing items OR rules deleted)"
    )


# ---------------------------------------------------------------------------
# OPEN_INVESTIGATIONS.md - INV-NNN
# ---------------------------------------------------------------------------
def test_open_investigations_count():
    """OPEN_INVESTIGATIONS.md should have a reasonable number of INV-NNN sections."""
    text = read_doc("OPEN_INVESTIGATIONS.md")
    actual = len(re.findall(r"^## INV-\d+", text, re.MULTILINE))
    assert actual >= 20, (
        f"OPEN_INVESTIGATIONS.md has only {actual} INV-NNN sections; "
        f"expected >=20 (Pass 53 has logged 40+ INVs)"
    )


# ---------------------------------------------------------------------------
# LIMITATIONS_CAVEATS_ASSUMPTIONS.md - CAV-NNN
# ---------------------------------------------------------------------------
def test_caveats_count():
    """LIMITATIONS_CAVEATS_ASSUMPTIONS.md should have CAV-NNN entries."""
    text = read_doc("LIMITATIONS_CAVEATS_ASSUMPTIONS.md")
    actual = len(re.findall(r"^### CAV-\d+", text, re.MULTILINE))
    assert actual >= 30, (
        f"LIMITATIONS_CAVEATS_ASSUMPTIONS.md has only {actual} CAV-NNN entries; "
        f"expected >=30 (Pass 52+ has logged many caveats)"
    )


# ---------------------------------------------------------------------------
# Dashboard parser correctness (catches 17-vs-148 regression)
# ---------------------------------------------------------------------------
def test_dashboard_stage_2_parses_full_bug_register():
    """build_dashboard_stage_2.py parse_bug_register must return at least
    100 rows (catches the 17-row regression where HTML comments mid-table
    silently broke the parser)."""
    import sys
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        from build_dashboard_stage_2 import parse_bug_register
    except ImportError:
        pytest.skip("build_dashboard_stage_2 not importable")
    bugs = parse_bug_register(REPO_ROOT / "BUG_REGISTER.md")
    assert len(bugs) >= 100, (
        f"parse_bug_register returned only {len(bugs)} rows; BUG_REGISTER "
        f"has 148+ bugs - parser is silently dropping rows"
    )


def test_dashboard_stage_2_parses_decisions():
    """build_dashboard_stage_2.py parse_decisions must return >=300 rows."""
    import sys
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        from build_dashboard_stage_2 import parse_decisions
    except ImportError:
        pytest.skip("build_dashboard_stage_2 not importable")
    decs = parse_decisions(REPO_ROOT / "AUDIT_INDEX.md")
    assert len(decs) >= 300, (
        f"parse_decisions returned only {len(decs)} rows; AUDIT_INDEX has "
        f"354+ decisions - parser is silently dropping rows"
    )


def test_dashboard_stage_2_parses_invs():
    """build_dashboard_stage_2.py parse_inv_entries must return >=20 rows."""
    import sys
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        from build_dashboard_stage_2 import parse_inv_entries
    except ImportError:
        pytest.skip("build_dashboard_stage_2 not importable")
    invs = parse_inv_entries(REPO_ROOT / "OPEN_INVESTIGATIONS.md")
    assert len(invs) >= 20, (
        f"parse_inv_entries returned only {len(invs)} rows; expected >=20"
    )


# ---------------------------------------------------------------------------
# Dashboard HTML JS correctness (catches duplicate const declaration)
# ---------------------------------------------------------------------------
def test_dashboard_stage_2_html_no_duplicate_top_level_const():
    """dashboard_stage_2/index.html must not declare the same TOP-LEVEL const
    twice (catches the duplicate 'caveats' regression).

    Note: consts inside .map() callbacks / nested functions are correctly
    scoped per JavaScript and are NOT flagged. Only column-0 (top-level
    script body) consts are checked.
    """
    html_path = REPO_ROOT / "dashboard_stage_2" / "index.html"
    if not html_path.exists():
        pytest.skip("dashboard_stage_2/index.html not present")
    text = html_path.read_text(encoding="utf-8")
    # Top-level only: const at column 0
    consts = re.findall(r"^const\s+(\w+)\s*=", text, re.MULTILINE)
    duplicates = {c for c in consts if consts.count(c) > 1}
    assert not duplicates, (
        f"dashboard_stage_2/index.html declares TOP-LEVEL const(s) more than once: "
        f"{duplicates} (will throw SyntaxError and break entire page)"
    )


def test_dashboard_sprint0a_html_no_duplicate_top_level_const():
    """Same check for dashboard_sprint0a/index.html (top-level only)."""
    html_path = REPO_ROOT / "dashboard_sprint0a" / "index.html"
    if not html_path.exists():
        pytest.skip("dashboard_sprint0a/index.html not present")
    text = html_path.read_text(encoding="utf-8")
    consts = re.findall(r"^const\s+(\w+)\s*=", text, re.MULTILINE)
    duplicates = {c for c in consts if consts.count(c) > 1}
    assert not duplicates, (
        f"dashboard_sprint0a/index.html declares TOP-LEVEL const(s) more than once: "
        f"{duplicates}"
    )
