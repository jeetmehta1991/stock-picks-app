"""scripts/sync_doc_counts.py - regenerate count claims in reference docs.

Pass 53 Day-9 v8h+1 owner-mandated 2026-05-08:
"Counts should match across reference docs if not error" + analysis showed
AUDIT_INDEX.md header claimed 354 decisions when table actually had 520.

This script counts actual entries in source-of-truth tables and replaces
stale numerical claims in doc headers. Per CHECKLIST #34 (count-derived
fields regenerate from source of truth) + #36 (numerical claims regenerated
at write time).

Modes:
  --check   exit non-zero if any drift detected (CI gate)
  --update  rewrite docs with current counts (manual sync)

Source of truth (per doc):
  AUDIT_INDEX.md       row count of '| **DECISION-' lines
  BUG_REGISTER.md      row count of '| BUG-' table rows
  AUDIT.md             count of '### BUG-NN' sections
  CHECKLIST.md         count of '^N\\.' numbered items
  OPEN_INVESTIGATIONS  count of '## INV-NN' sections
  LIMITATIONS_CAVEATS  count of '### CAV-NN' sections
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def count_lines(path: Path, pattern: str) -> int:
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8", errors="ignore")
    return len(re.findall(pattern, text, re.MULTILINE))


CHECKS = [
    {
        "name": "AUDIT_INDEX decisions",
        "doc": "AUDIT_INDEX.md",
        "count_pattern": r"^\| \*\*DECISION-",
        "claim_regex": r"(Total:\s*)(\d+)(\s*decision entries)",
        "claim_doc": "AUDIT_INDEX.md",
    },
    {
        "name": "BUG_REGISTER bugs",
        "doc": "BUG_REGISTER.md",
        "count_pattern": r"^\| BUG-\d+",
        "claim_regex": r"(Total canonical bugs in AUDIT\.md \(### BUG-NN sections\) \| )(\d+)",
        "claim_doc": "BUG_REGISTER.md",
    },
    {
        "name": "AUDIT BUG sections",
        "doc": "AUDIT.md",
        "count_pattern": r"^### BUG-\d+",
        # No claim to update - used for cross-check only via test
        "claim_regex": None,
        "claim_doc": None,
    },
    {
        "name": "CHECKLIST items",
        "doc": "CHECKLIST.md",
        "count_pattern": r"^\d+\.\s+",
        "claim_regex": None,  # CHECKLIST has no header total claim
        "claim_doc": None,
    },
    {
        "name": "OPEN_INVESTIGATIONS",
        "doc": "OPEN_INVESTIGATIONS.md",
        "count_pattern": r"^## INV-\d+",
        "claim_regex": None,
        "claim_doc": None,
    },
    {
        "name": "LIMITATIONS_CAVEATS",
        "doc": "LIMITATIONS_CAVEATS_ASSUMPTIONS.md",
        "count_pattern": r"^### CAV-\d+",
        "claim_regex": None,
        "claim_doc": None,
    },
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="non-zero exit on drift")
    ap.add_argument("--update", action="store_true", help="rewrite stale claims")
    args = ap.parse_args()
    if not (args.check or args.update):
        ap.error("must specify --check or --update")

    drift_found = False
    print("=== Doc count sync ===")
    for c in CHECKS:
        doc_path = REPO_ROOT / c["doc"]
        actual = count_lines(doc_path, c["count_pattern"])
        line = f"  {c['name']}: actual={actual}"

        if c["claim_regex"] and c["claim_doc"]:
            claim_path = REPO_ROOT / c["claim_doc"]
            claim_text = claim_path.read_text(encoding="utf-8", errors="ignore")
            m = re.search(c["claim_regex"], claim_text)
            if m:
                claimed = int(m.group(2))
                line += f" claimed={claimed}"
                if claimed != actual:
                    drift_found = True
                    line += f" DRIFT={actual - claimed:+d}"
                    if args.update:
                        # Rewrite to match actual
                        new_text = (
                            claim_text[:m.start(2)]
                            + str(actual)
                            + claim_text[m.end(2):]
                        )
                        claim_path.write_text(new_text, encoding="utf-8")
                        line += " UPDATED"
            else:
                line += " (no claim found in doc)"
        print(line)

    if args.check and drift_found:
        print("\nDrift detected. Run 'python scripts/sync_doc_counts.py --update' to fix.")
        return 1
    if args.update and drift_found:
        print("\nUpdated stale claims. Re-run --check to confirm.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
