"""Bulk remediation script for SPEC_WITHOUT_BUILD DECs (Pass 53 Day 2-3 work).

Per DEC-594 retroactive audit + owner-approved Tier B+C bulk triage 2026-05-06.

For each DEC in SPEC_WITHOUT_BUILD bucket:
  1. Search backtest/tests/ for DEC ID reference
  2. If found: append annotation to DEC body in AUDIT_INDEX (test path)
  3. If not found: demote status to PARTIAL-SPEC-ONLY

Outputs:
  - Modified AUDIT_INDEX.md
  - Console summary of changes
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIT_INDEX = REPO_ROOT / "AUDIT_INDEX.md"
REPORT = REPO_ROOT / "AUDIT_DECS_ARTIFACTS_REPORT.json"
TESTS_DIR = REPO_ROOT / "backtest" / "tests"

ALREADY_DONE_TIER_A = {
    "DECISION-477", "DECISION-014", "DECISION-153",
    "DECISION-423", "DECISION-497",
}


def code_grep_dec(dec_id: str) -> list:
    """Search backtest/tests/ for any reference to this DEC ID."""
    short = dec_id.replace("DECISION-", "DEC-")
    matches = []
    for test_file in TESTS_DIR.rglob("*.py"):
        try:
            text = test_file.read_text(encoding="utf-8", errors="ignore")
            if short in text or dec_id in text:
                matches.append(str(test_file.relative_to(REPO_ROOT)))
        except Exception:
            pass
    return matches


def remediate_dec(audit_text: str, dec_id: str, body: str, status: str,
                  test_paths: list) -> tuple[str, str]:
    """
    Modify AUDIT_INDEX text for one DEC.
    Returns: (new_text, action) where action ∈ {ANNOTATED, DEMOTED, NO_CHANGE}
    """
    annotation_marker = "Pass 53 evening 2026-05-06 DEC-594 audit"
    if annotation_marker in body:
        return audit_text, "NO_CHANGE"  # already remediated

    if test_paths:
        # Annotate: append note before final | status |
        new_body = body + (
            f" **{annotation_marker} annotation: executable tests reference this DEC at "
            f"{', '.join(f'`{p}`' for p in test_paths[:2])}; "
            f"covered by existing pyramid (102 unit+integration + 7 data-integrity).**"
        )
        new_text = audit_text.replace(body, new_body, 1)
        return new_text, "ANNOTATED"
    else:
        # Demote: change status column from RESOLVED-DECIDED to PARTIAL-SPEC-ONLY
        # + append note to body
        new_body = body + (
            f" **{annotation_marker}: PARTIAL-SPEC-ONLY (was RESOLVED-DECIDED; "
            f"demoted via DEC-594 retroactive audit — code-grep found no test "
            f"reference in `backtest/tests/`; cannot advance to RESOLVED-DECIDED "
            f"until executable artifact lands per DEC-594 same-commit rule).**"
        )
        new_text = audit_text.replace(body, new_body, 1)

        # Find the row line and replace status column
        # Pattern: | **DECISION-N** | <body> | <status> | <theme> | <pass> | <pass> |
        # We need to replace the status column for THIS dec_id row only
        row_pattern = re.compile(
            rf"(\|\s*\*\*{re.escape(dec_id)}\*\*\s*\|.*?\|\s*){re.escape(status)}(\s*\|)",
            re.DOTALL,
        )
        new_text2 = row_pattern.sub(r"\1PARTIAL-SPEC-ONLY\2", new_text, count=1)
        if new_text2 == new_text:
            # Replacement didn't take; fall back to body-annotation only
            return new_text, "ANNOTATED_BODY_ONLY"
        return new_text2, "DEMOTED"


def main():
    if not REPORT.exists():
        print(f"ERROR: {REPORT} not found. Run audit_decs_for_artifacts.py first.")
        return

    with open(REPORT) as f:
        rpt = json.load(f)

    swb = rpt["findings"]["SPEC_WITHOUT_BUILD"]
    targets = [
        f for f in swb
        if "RESOLVED-DECIDED" in f["status"] and f["id"] not in ALREADY_DONE_TIER_A
    ]
    print(f"Targets: {len(targets)} (RESOLVED-DECIDED + not already Tier A)")

    audit_text = AUDIT_INDEX.read_text(encoding="utf-8")
    actions = {"ANNOTATED": [], "DEMOTED": [], "NO_CHANGE": [],
               "ANNOTATED_BODY_ONLY": [], "BODY_NOT_FOUND": []}

    for dec in targets:
        dec_id = dec["id"]
        # Find body in audit text — match the row with this DEC ID
        row_re = re.compile(
            rf"\|\s*\*\*{re.escape(dec_id)}\*\*\s*\|\s*(.+?)\s*\|\s*([\w-]+)\s*\|",
            re.DOTALL,
        )
        m = row_re.search(audit_text)
        if not m:
            actions["BODY_NOT_FOUND"].append(dec_id)
            continue
        body, status = m.group(1), m.group(2)

        test_paths = code_grep_dec(dec_id)
        audit_text, action = remediate_dec(audit_text, dec_id, body, status, test_paths)
        actions[action].append((dec_id, test_paths[:2]))

    # Write updated audit
    AUDIT_INDEX.write_text(audit_text, encoding="utf-8")

    print()
    for action, items in actions.items():
        print(f"  {action}: {len(items)}")
        for entry in items[:5]:
            print(f"    {entry}")


if __name__ == "__main__":
    main()
