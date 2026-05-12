#!/usr/bin/env python3
"""Batch 69 Phase 1: revert 47 self-confessed-deferred decisions + 1 bug
from RESOLVED-IMPLEMENTED back to PARTIAL-IMPL-HELPER-ONLY.

Owner directive 2026-05-12:
  "Wired" should mean engine call-path actually consumes the helper.
  These 47 DECs had explicit "engine wiring deferred" / "current scope is
  helper" / "implementation deferred" phrasing in the body I wrote -- self-
  confessed shelf-ready items that were nevertheless flipped to
  RESOLVED-IMPLEMENTED during Batches 49-68.

Revert action:
  status: RESOLVED-IMPLEMENTED -> PARTIAL-IMPL-HELPER-ONLY
  description: append [Batch 69 revert 2026-05-12 owner directive:
    helper exists but engine doesn't consume; status falsely flipped
    in Batch X; reverted pending real engine wiring + 13-tier pyramid]
"""
import re
from pathlib import Path

REPO = Path(__file__).parent.parent

DEFERRED_DECS = {
    "DECISION-019", "DECISION-021", "DECISION-062", "DECISION-076",
    "DECISION-087", "DECISION-088", "DECISION-091", "DECISION-092",
    "DECISION-106", "DECISION-108", "DECISION-128", "DECISION-134",
    "DECISION-135", "DECISION-138", "DECISION-149", "DECISION-150",
    "DECISION-151", "DECISION-159", "DECISION-183", "DECISION-209",
    "DECISION-216", "DECISION-230", "DECISION-231", "DECISION-234",
    "DECISION-235", "DECISION-280", "DECISION-314", "DECISION-354",
    "DECISION-365", "DECISION-378", "DECISION-417", "DECISION-425",
    "DECISION-426", "DECISION-427", "DECISION-428", "DECISION-429",
    "DECISION-430", "DECISION-433", "DECISION-436", "DECISION-456",
    "DECISION-458", "DECISION-459", "DECISION-463", "DECISION-467",
    "DECISION-473", "DECISION-483", "DECISION-495",
}
DEFERRED_BUGS = {"BUG-36"}

REVERT_NOTE = (
    " -- Batch 69 revert 2026-05-12 owner directive: helper exists but "
    "engine call path does not consume; status was falsely flipped to "
    "RESOLVED-IMPLEMENTED in Batches 49-68 (self-confessed via "
    "\"engine wiring deferred\" phrase in body). Reverted to "
    "PARTIAL-IMPL-HELPER-ONLY pending real engine wiring + full 13-tier "
    "pyramid per CHECKLIST #78 per-addressal."
)


def revert_audit_index() -> int:
    p = REPO / "AUDIT_INDEX.md"
    with p.open(encoding="utf-8") as f:
        lines = f.readlines()
    reverted = 0
    for i, line in enumerate(lines):
        m = re.match(r"^\| \*\*(DECISION-[\w-]+)\*\* \|", line)
        if not m or m.group(1) not in DEFERRED_DECS:
            continue
        raw = line.rstrip("\n")
        if not raw.startswith("| ") or not raw.endswith(" |"):
            continue
        inner = raw[2:-2]
        cells = inner.split(" | ")
        if len(cells) != 6:
            continue
        id_cell, desc, status, theme, pass_orig, pass_resolved = cells
        if status != "RESOLVED-IMPLEMENTED":
            # Already not-implemented; skip
            continue
        if "Batch 69 revert" in desc:
            continue  # idempotent
        new_desc = desc + REVERT_NOTE
        new_status = "PARTIAL-IMPL-HELPER-ONLY"
        new_line = (
            f"| {id_cell} | {new_desc} | {new_status} | {theme} | "
            f"{pass_orig} | {pass_resolved} |\n"
        )
        lines[i] = new_line
        reverted += 1
    p.write_text("".join(lines), encoding="utf-8", newline="")
    return reverted


def revert_bug_register() -> int:
    p = REPO / "BUG_REGISTER.md"
    if not p.exists():
        return 0
    with p.open(encoding="utf-8") as f:
        lines = f.readlines()
    reverted = 0
    for i, line in enumerate(lines):
        m = re.match(r"^\| (BUG-[\w-]+) \|", line)
        if not m or m.group(1) not in DEFERRED_BUGS:
            continue
        raw = line.rstrip("\n")
        if not raw.startswith("| ") or not raw.endswith(" |"):
            continue
        inner = raw[2:-2]
        cells = inner.split(" | ")
        if len(cells) != 4:
            continue
        id_cell, desc, resolving_dec, status = cells
        if "Batch 69 revert" in desc:
            continue
        # Detect previously-claimed implementation
        if "RESOLVED-IMPLEMENTED" not in status:
            continue
        new_desc = desc + REVERT_NOTE
        new_status = status.replace(
            "RESOLVED-IMPLEMENTED", "PARTIAL-IMPL-HELPER-ONLY"
        )
        new_line = f"| {id_cell} | {new_desc} | {resolving_dec} | {new_status} |\n"
        lines[i] = new_line
        reverted += 1
    p.write_text("".join(lines), encoding="utf-8", newline="")
    return reverted


def main() -> None:
    n_dec = revert_audit_index()
    n_bug = revert_bug_register()
    print(f"Reverted {n_dec} decisions + {n_bug} bugs to PARTIAL-IMPL-HELPER-ONLY")


if __name__ == "__main__":
    main()
