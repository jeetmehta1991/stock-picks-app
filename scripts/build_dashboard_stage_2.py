"""scripts/build_dashboard_stage_2.py - Stage 2 project tracker dashboard.

Pass 53 Day-9 v8h+1 owner-mandated 2026-05-08:
"I am a bit confused and docs are all over the place" - need a single
comprehensive view of execution status across decisions, bugs, INVs,
sprints, code state.

Source of truth (per CHECKLIST #77 - canonical sources, never memory):
  AUDIT_INDEX.md          - 354 decisions
  BUG_REGISTER.md         - 148 bugs + bucket classification
  OPEN_INVESTIGATIONS.md  - INV-NNN flag tracker
  PHASE_1A_PRELAUNCH_TODO.md - Tier H/I/J + sprint queue
  CHECKLIST.md            - 77 rules
  LEARNINGS.md            - lessons L-NNN
  git log + git status    - code state

Output: dashboard_stage_2/data.json + data.js (consumed by index.html)

Run hourly via cron: python scripts/build_dashboard_stage_2.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "dashboard_stage_2"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_md_table(path: Path, header_keywords: list[str]) -> list[dict]:
    """Extract markdown table rows from `path`.

    Returns list of dicts keyed by lowercased header column names.
    `header_keywords` are required substrings of the header row to identify
    the right table (a doc may have multiple tables).
    """
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.split("\n")
    rows: list[dict] = []
    in_table = False
    headers: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            headers = []
            continue
        cols = [c.strip() for c in stripped.strip("|").split("|")]
        if not in_table:
            # Look for the header row matching keywords
            if all(any(k.lower() in c.lower() for c in cols) for k in header_keywords):
                headers = [c.lower().replace(" ", "_") for c in cols]
                in_table = True
                continue
        if in_table:
            # Skip separator row
            if all("---" in c or c == "" for c in cols):
                continue
            if len(cols) == len(headers):
                rows.append({headers[i]: cols[i] for i in range(len(headers))})
    return rows


def parse_inv_entries(path: Path) -> list[dict]:
    """Parse OPEN_INVESTIGATIONS.md ## INV-NNN sections."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    inv_re = re.compile(r"^## (INV-\d+(?:\w*)?)\s+(.+?)(?:\n|$)", re.MULTILINE)
    entries: list[dict] = []
    for m in inv_re.finditer(text):
        inv_id = m.group(1)
        title_line = m.group(2).strip()
        # Find the body until next ## or end-of-file
        start = m.end()
        next_match = inv_re.search(text, start)
        end = next_match.start() if next_match else len(text)
        body = text[start:end]
        # Status detection
        status = "OPEN"
        if "RESOLVED" in body[:200].upper() or "RESOLVED" in title_line.upper():
            status = "RESOLVED"
        if "DEFERRED" in body[:200].upper():
            status = "DEFERRED"
        # Severity detection
        severity = "UNKNOWN"
        sev_match = re.search(r"\*\*Severity:\*\*\s*([A-Z\-]+)", body)
        if sev_match:
            severity = sev_match.group(1).strip()
        # Extract first 200 chars as summary
        summary_match = re.search(r"\*\*Observation:\*\*\s*(.+?)(?=\n\n|\*\*)", body, re.DOTALL)
        summary = (summary_match.group(1).strip()[:200] if summary_match else
                    title_line[:200])
        entries.append({
            "id": inv_id,
            "title": title_line[:160],
            "status": status,
            "severity": severity,
            "summary": summary,
        })
    return entries


def parse_decisions(audit_index: Path) -> list[dict]:
    """Parse AUDIT_INDEX.md decisions table."""
    if not audit_index.exists():
        return []
    text = audit_index.read_text(encoding="utf-8", errors="ignore")
    # Find the All Decisions Table section
    # Header: | ID | Title | Status | Theme | Pass Intro | Pass Resolved |
    start_marker = "### All Decisions Table"
    start = text.find(start_marker)
    if start < 0:
        return []
    section = text[start:]
    rows: list[dict] = []
    in_table = False
    for line in section.split("\n"):
        if not line.strip().startswith("|"):
            if in_table:
                break
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if "ID" in cols[0] and "Title" in cols[1]:
            in_table = True
            continue
        if in_table and len(cols) >= 6:
            if all("---" in c or c == "" for c in cols):
                continue
            # Strip markdown bold
            dec_id = re.sub(r"\*\*", "", cols[0])
            title = re.sub(r"\*\*", "", cols[1])
            # Title often has long Pass-52 annotations - keep first 160 chars
            title_short = title[:160]
            status = re.sub(r"\*\*", "", cols[2])
            theme = cols[3]
            pass_intro = cols[4]
            pass_resolved = cols[5]
            rows.append({
                "id": dec_id,
                "title": title_short,
                "status": status,
                "theme": theme,
                "pass_intro": pass_intro,
                "pass_resolved": pass_resolved,
            })
    return rows


def parse_bug_register(path: Path) -> list[dict]:
    """Parse BUG_REGISTER.md bug → decision cross-reference table."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    # Header: | Bug ID | Title (truncated) | Linked decisions | Sprint context |
    rows: list[dict] = []
    in_table = False
    for line in text.split("\n"):
        if not line.strip().startswith("|"):
            in_table = False
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if "Bug ID" in cols[0]:
            in_table = True
            continue
        if in_table and len(cols) >= 4:
            if all("---" in c or c == "" for c in cols):
                continue
            rows.append({
                "id": cols[0],
                "title": cols[1][:200],
                "linked_decisions": cols[2],
                "sprint_context": cols[3],
            })
    return rows


def parse_tier_table(prelaunch_md: Path) -> list[dict]:
    """Parse Tier H/I/J tables from PHASE_1A_PRELAUNCH_TODO.md."""
    if not prelaunch_md.exists():
        return []
    text = prelaunch_md.read_text(encoding="utf-8", errors="ignore")
    # Look for # | Action | Source | Est. effort | Status (Tier H pattern)
    rows: list[dict] = []
    in_table = False
    in_tier_section = False
    for line in text.split("\n"):
        if line.startswith("###"):
            in_tier_section = "Tier" in line and ("H" in line or "I" in line or "J" in line)
            continue
        if not in_tier_section:
            continue
        if not line.strip().startswith("|"):
            in_table = False
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) >= 2 and cols[0] == "#" and "Action" in cols[1]:
            in_table = True
            continue
        if in_table and len(cols) >= 4:
            if all("---" in c or c == "" for c in cols):
                continue
            rows.append({
                "id": cols[0],
                "action": cols[1][:200],
                "source": cols[2] if len(cols) > 2 else "",
                "effort": cols[3] if len(cols) > 3 else "",
                "status": cols[4] if len(cols) > 4 else "",
            })
    return rows


def get_recent_commits(n: int = 30) -> list[dict]:
    try:
        r = subprocess.run(
            ["git", "log", f"-{n}", "--pretty=format:%H|%s|%an|%ar"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        )
        commits = []
        for line in r.stdout.split("\n"):
            if not line.strip():
                continue
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append({
                    "sha": parts[0][:8],
                    "subject": parts[1][:200],
                    "author": parts[2],
                    "rel_time": parts[3],
                })
        return commits
    except Exception:
        return []


def get_uncommitted_files() -> dict:
    try:
        r = subprocess.run(
            ["git", "status", "--short"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        )
        files = []
        for line in r.stdout.split("\n"):
            if not line.strip():
                continue
            files.append({"status": line[:2].strip(), "path": line[3:].strip()})
        return {
            "count": len(files),
            "modified": sum(1 for f in files if f["status"] in ("M", "MM")),
            "added": sum(1 for f in files if f["status"] in ("A", "AM")),
            "untracked": sum(1 for f in files if f["status"] == "??"),
            "deleted": sum(1 for f in files if f["status"] in ("D", "DD")),
            "files": files[:200],
        }
    except Exception:
        return {"count": 0, "files": []}


def get_unpushed_commits() -> list[dict]:
    try:
        r = subprocess.run(
            ["git", "log", "origin/main..HEAD", "--pretty=format:%H|%s|%ar"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        )
        commits = []
        for line in r.stdout.split("\n"):
            if not line.strip():
                continue
            parts = line.split("|", 2)
            if len(parts) == 3:
                commits.append({
                    "sha": parts[0][:8],
                    "subject": parts[1][:200],
                    "rel_time": parts[2],
                })
        return commits
    except Exception:
        return []


def main() -> int:
    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decisions": parse_decisions(REPO_ROOT / "AUDIT_INDEX.md"),
        "bugs": parse_bug_register(REPO_ROOT / "BUG_REGISTER.md"),
        "investigations": parse_inv_entries(REPO_ROOT / "OPEN_INVESTIGATIONS.md"),
        "tier_items": parse_tier_table(REPO_ROOT / "PHASE_1A_PRELAUNCH_TODO.md"),
        "recent_commits": get_recent_commits(30),
        "uncommitted": get_uncommitted_files(),
        "unpushed_commits": get_unpushed_commits(),
    }

    # Aggregations
    dec_by_status: dict = {}
    for d in snapshot["decisions"]:
        s = d["status"].split()[0] if d["status"] else "UNKNOWN"
        dec_by_status[s] = dec_by_status.get(s, 0) + 1
    snapshot["decision_status_counts"] = dec_by_status

    inv_by_status: dict = {}
    for i in snapshot["investigations"]:
        inv_by_status[i["status"]] = inv_by_status.get(i["status"], 0) + 1
    snapshot["inv_status_counts"] = inv_by_status

    tier_by_status: dict = {}
    for t in snapshot["tier_items"]:
        # Status field is markdown like "DONE" or "PENDING"
        s = re.sub(r"[^A-Z\-]", "", t["status"].upper())[:30] or "UNKNOWN"
        tier_by_status[s] = tier_by_status.get(s, 0) + 1
    snapshot["tier_status_counts"] = tier_by_status

    out_json = OUT_DIR / "data.json"
    out_json.write_text(json.dumps(snapshot, indent=2, default=str))
    out_js = OUT_DIR / "data.js"
    out_js.write_text(f"const STAGE2_DATA = {json.dumps(snapshot, default=str)};\n")
    (OUT_DIR / "last_run.txt").write_text(snapshot["generated_at"])

    print(f"=== Stage 2 dashboard built ===")
    print(f"Decisions: {len(snapshot['decisions'])} | by status: {dec_by_status}")
    print(f"Bugs: {len(snapshot['bugs'])}")
    print(f"INVs: {len(snapshot['investigations'])} | by status: {inv_by_status}")
    print(f"Tier items: {len(snapshot['tier_items'])} | by status: {tier_by_status}")
    print(f"Recent commits: {len(snapshot['recent_commits'])}")
    print(f"Uncommitted files: {snapshot['uncommitted']['count']}")
    print(f"Unpushed commits: {len(snapshot['unpushed_commits'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
