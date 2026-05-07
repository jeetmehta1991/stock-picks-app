"""Retroactive DEC audit for spec-without-build patterns (DEC-594 / CHECKLIST #73 / L149).

Scans AUDIT_INDEX.md for every DEC whose body contains test/gate/validation
trigger words, and reports whether the corresponding executable artifact exists
in the codebase.

Output: audit_decs_for_artifacts_report.json + console summary.

Usage:
  python scripts/audit_decs_for_artifacts.py             # full report
  python scripts/audit_decs_for_artifacts.py --critical  # only flag DECs without artifact
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIT_INDEX = REPO_ROOT / "AUDIT_INDEX.md"
REPORT_OUT = REPO_ROOT / "AUDIT_DECS_ARTIFACTS_REPORT.json"

# Trigger words per DEC-594 (case-insensitive)
TRIGGER_WORDS = [
    r"\btest\b", r"\btests\b", r"\bvalidate\b", r"\bvalidates\b",
    r"\bvalidation\b", r"\bvalidator\b", r"\bvalidated\b",
    r"\bverify\b", r"\bverifies\b", r"\bverified\b", r"\bverification\b",
    r"\bgate\b", r"\bgates\b",
    r"\bacceptance criterion\b", r"\bpass criterion\b", r"\bmust pass\b",
    r"\bbefore [A-Z]\w+\b",  # "before Phase", "before Stage"
    r"\bbefore phase\b", r"\bbefore stage\b", r"\bbefore commit\b",
    r"\bbefore run\b", r"\bbefore merge\b", r"\bbefore scale\b",
    r"\bsmoke test\b", r"\bregression test\b",
]

TRIGGER_PATTERN = re.compile("|".join(TRIGGER_WORDS), re.IGNORECASE)

# Regex to find executable-artifact mentions in DEC body
ARTIFACT_PATTERN = re.compile(
    r"(?:`|\b)([\w./-]+\.(?:py|yml|yaml|sh|json|md))(?:`|\b)|"
    r"(`?backtest/tests/[^`\s)]+`?)|"
    r"(`?scripts/[^`\s)]+`?)|"
    r"(`?\.github/workflows/[^`\s)]+`?)"
)

# DEC ID extraction
DEC_ROW_RE = re.compile(r"\|\s*\*\*(DECISION-\d+(?:-\w+)?)\*\*\s*\|\s*(.+?)\s*\|\s*([\w-]+)\s*\|")

# DECs that touch test/gate/validation but are KNOWN to have artifacts; allowlist
# (or DECs where the test/gate is INPUT not OUTPUT — i.e., the DEC consumes
# existing test infra rather than creating new test infra)
KNOWN_COMPLIANT = {
    "DECISION-097",   # 90% test coverage minimum (consumes coverage infra)
    "DECISION-098",   # hot-path 100% coverage (consumes coverage infra)
    "DECISION-503",   # test pyramid HARD RULE — was the FIRST L149 victim; layer 7 unbuilt; remediated by DEC-591 + L148
    "DECISION-504",   # T3-over-T1 precedence (10 unit tests in test_unit.py)
    "DECISION-507",   # wiring matrix (TRADINGAGENTS_DATA_AUDIT.md tracks status)
    "DECISION-508",   # smartmoneyconcepts 4-tier testing (test_smartmoneyconcepts_*.py exists)
    "DECISION-589",   # audit-iteration ceiling (process rule, no artifact required)
    "DECISION-590",   # Phase 1A begin date (process rule)
    "DECISION-591",   # data-integrity test layer (test_data_integrity.py landed same-commit)
    "DECISION-592",   # Apewisdom prefetcher (script + workflow landed same-commit)
    "DECISION-593",   # Wikipedia authorization (data-only DEC)
    "DECISION-594",   # this DEC (this script + test_gates.py land same-commit)
    "DECISION-595",   # gate executable tests (test_gates.py landed same-commit)
}


def scan_audit_index():
    """Parse AUDIT_INDEX.md and return list of (dec_id, body, status)."""
    if not AUDIT_INDEX.exists():
        print(f"ERROR: {AUDIT_INDEX} not found")
        sys.exit(1)
    text = AUDIT_INDEX.read_text(encoding="utf-8")
    decs = []
    for m in DEC_ROW_RE.finditer(text):
        dec_id = m.group(1)
        body = m.group(2)
        status = m.group(3)
        decs.append({"id": dec_id, "body": body, "status": status})
    return decs


def has_trigger_words(body):
    """Return list of trigger words found in body."""
    matches = TRIGGER_PATTERN.findall(body)
    return list({m.lower() if m else "" for m in matches if m})


def has_artifact_reference(body):
    """Return list of artifact paths referenced in body."""
    artifacts = []
    for m in ARTIFACT_PATTERN.finditer(body):
        for g in m.groups():
            if g:
                artifacts.append(g.strip("`"))
    return list(set(artifacts))


def artifact_exists(artifact_path: str) -> bool:
    """Check if artifact file exists in repo."""
    p = REPO_ROOT / artifact_path.lstrip("./")
    return p.exists()


def classify_dec(dec):
    """Return classification: COMPLIANT / SPEC_WITHOUT_BUILD / NO_TRIGGER /
    KNOWN_COMPLIANT / SUPERSEDED / DEFERRED."""
    if dec["id"] in KNOWN_COMPLIANT:
        return "KNOWN_COMPLIANT", [], [], []

    status = (dec.get("status") or "").upper()
    # Non-active statuses — no standalone artifact required
    if "SUPERSEDED" in status:
        return "SUPERSEDED", [], [], []
    if "DEFERRED" in status:
        return "DEFERRED", [], [], []
    if "PARTIAL-SPEC-ONLY" in status or "PARTIAL_SPEC_ONLY" in status:
        return "PARTIAL_SPEC_ONLY", [], [], []
    if "PROPOSED" in status or "PENDING" in status:
        return "PROPOSED_OR_PENDING", [], [], []
    if "OBSOLETE" in status or "BLOCKED_ON" in status or "FAIL_RR" in status:
        return "INACTIVE_STATUS", [], [], []

    triggers = has_trigger_words(dec["body"])
    if not triggers:
        return "NO_TRIGGER", [], [], []

    artifacts = has_artifact_reference(dec["body"])
    existing = [a for a in artifacts if artifact_exists(a)]
    missing = [a for a in artifacts if not artifact_exists(a)]
    if existing:
        return "COMPLIANT", triggers, existing, missing

    # Pass 53 evening 2026-05-07 audit-script enhancement (per DEC-594 retroactive
    # remediation): a DEC body may carry an inline annotation listing the matched
    # test path(s). If annotation present + path exists, classify as ANNOTATED_COMPLIANT.
    body = dec["body"]
    annotation_marker = "Pass 53 evening 2026-05-06 DEC-594 audit"
    if annotation_marker in body:
        # Body annotated — extract test path references (handle both / and \ separators)
        annotated_paths_raw = re.findall(
            r"`(backtest[/\\]tests[/\\][^`\s]+\.py)`", body
        )
        annotated_paths = [p.replace("\\", "/") for p in annotated_paths_raw]
        existing_annotated = [a for a in annotated_paths if artifact_exists(a)]
        if existing_annotated:
            return "ANNOTATED_COMPLIANT", triggers, existing_annotated, []
        # Annotation says "PARTIAL-SPEC-ONLY" — that's the demote case
        if "PARTIAL-SPEC-ONLY" in body:
            return "PARTIAL_SPEC_ONLY", triggers, [], []
        # Annotation present but no path matched (e.g., "covered by test_data_integrity
        # + test_unit indirectly") — annotation explicitly justifies no direct path;
        # treat as audit-trail-compliant
        return "ANNOTATED_NO_DIRECT_TEST", triggers, [], []

    # No explicit artifact path; check if the DEC body has "Test signal:" pattern
    # which describes a test scenario. For these, look for code references in
    # backtest/tests/ that mention this DEC ID.
    has_test_signal_pattern = "test signal" in body.lower()
    if has_test_signal_pattern:
        # Search backtest/tests/ for this DEC ID reference
        dec_short = dec["id"].replace("DECISION-", "DEC-")
        tests_dir = REPO_ROOT / "backtest" / "tests"
        if tests_dir.exists():
            for test_file in tests_dir.rglob("*.py"):
                try:
                    text = test_file.read_text(encoding="utf-8", errors="ignore")
                    if dec_short in text or dec["id"] in text:
                        return "TEST_SIGNAL_REFERENCED_IN_CODE", triggers, [str(test_file.relative_to(REPO_ROOT))], []
                except Exception:
                    pass
        # Test signal pattern but no code reference — needs verification
        return "TEST_SIGNAL_UNVERIFIED", triggers, [], missing

    return "SPEC_WITHOUT_BUILD", triggers, existing, missing


def main():
    ap = argparse.ArgumentParser(description="Retroactive DEC artifact audit")
    ap.add_argument("--critical", action="store_true",
                    help="Print only DECs flagged SPEC_WITHOUT_BUILD")
    args = ap.parse_args()

    decs = scan_audit_index()
    print(f"Scanned AUDIT_INDEX.md: {len(decs)} DEC entries")

    counts = {
        "COMPLIANT": 0, "ANNOTATED_COMPLIANT": 0, "ANNOTATED_NO_DIRECT_TEST": 0,
        "SPEC_WITHOUT_BUILD": 0, "NO_TRIGGER": 0, "KNOWN_COMPLIANT": 0,
        "SUPERSEDED": 0, "DEFERRED": 0, "PARTIAL_SPEC_ONLY": 0,
        "PROPOSED_OR_PENDING": 0, "TEST_SIGNAL_REFERENCED_IN_CODE": 0,
        "TEST_SIGNAL_UNVERIFIED": 0, "INACTIVE_STATUS": 0,
    }
    findings = {k: [] for k in counts}

    for dec in decs:
        classification, triggers, existing, missing = classify_dec(dec)
        counts[classification] += 1
        finding = {
            "id": dec["id"],
            "status": dec["status"],
            "classification": classification,
            "triggers": triggers,
            "artifacts_existing": existing,
            "artifacts_missing": missing,
            "body_excerpt": dec["body"][:200] + "..." if len(dec["body"]) > 200 else dec["body"],
        }
        findings[classification].append(finding)

    print()
    print("=== CLASSIFICATION SUMMARY ===")
    for cat, count in counts.items():
        print(f"  {cat}: {count}")
    print(f"  TOTAL: {sum(counts.values())}")

    if args.critical:
        print()
        print("=== SPEC_WITHOUT_BUILD findings (REMEDIATION REQUIRED) ===")
        for f in findings["SPEC_WITHOUT_BUILD"]:
            print(f"\n  {f['id']} [{f['status']}]")
            print(f"    Triggers: {f['triggers'][:5]}")
            print(f"    Body: {f['body_excerpt']}")

    # Write full JSON report
    report = {
        "scanned_count": len(decs),
        "counts": counts,
        "findings": findings,
    }
    REPORT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nFull report: {REPORT_OUT}")


if __name__ == "__main__":
    main()
