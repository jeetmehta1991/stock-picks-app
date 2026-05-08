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
    """Parse BUG_REGISTER.md bug -> decision cross-reference table.

    Defensive: skips HTML comments + blank lines mid-table without
    resetting in_table flag (BUG_REGISTER has <!-- canonical-fact ... -->
    annotations between rows that earlier broke the parser to 17 of 152).
    """
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    rows: list[dict] = []
    in_table = False
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue  # blank lines ignored, don't reset in_table
        if stripped.startswith("<!--") or stripped.endswith("-->"):
            continue  # HTML comments ignored
        if not stripped.startswith("|"):
            in_table = False
            continue
        cols = [c.strip() for c in stripped.strip("|").split("|")]
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


def load_status_corpora() -> dict:
    """Pre-load text corpora for ID-status grep (coded/wired/pushed/tested)."""
    def cat(paths):
        out = []
        for p in paths:
            pp = REPO_ROOT / p
            if pp.exists():
                for f in pp.rglob("*.py"):
                    try:
                        out.append(f.read_text(encoding="utf-8", errors="ignore"))
                    except Exception:
                        continue
        return "\n".join(out)
    prod = cat(["backtest/data", "backtest/engine", "backtest/signals", "backtest/results"])
    tests = cat(["backtest/tests"])
    backtest_all = cat(["backtest"])
    scripts = cat(["scripts"])
    docs_text = ""
    for d in ("AUDIT.md", "AUDIT_INDEX.md", "BUG_REGISTER.md", "PHASE_1A_PRELAUNCH_TODO.md"):
        p = REPO_ROOT / d
        if p.exists():
            docs_text += "\n" + p.read_text(encoding="utf-8", errors="ignore")
    # git log subjects (across all branches, all history)
    try:
        r = subprocess.run(
            ["git", "log", "--all", "--pretty=format:%s"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        )
        git_log_subjects = r.stdout
    except Exception:
        git_log_subjects = ""
    return {
        "prod": prod,
        "tests": tests,
        "backtest_all": backtest_all,
        "scripts": scripts,
        "docs": docs_text,
        "git_log": git_log_subjects,
    }


def id_status(id_str: str, corpora: dict) -> dict:
    """For a given ID (e.g. DEC-422 / BUG-001 / INV-024 / CAV-070), return:
      coded:  referenced in backtest/ or scripts/ Python
      wired:  referenced in active path (data/engine/signals/results)
      tested: referenced in backtest/tests/
      pushed: referenced in any git commit subject (=> code change merged)
      n_doc_refs: doc-only references (AUDIT.md / etc.) for context
    """
    if not id_str or len(id_str) < 4:
        return {"coded": False, "wired": False, "tested": False, "pushed": False, "n_doc_refs": 0}
    return {
        "coded": (id_str in corpora["backtest_all"]) or (id_str in corpora["scripts"]),
        "wired": id_str in corpora["prod"],
        "tested": id_str in corpora["tests"],
        "pushed": id_str in corpora["git_log"],
        "n_doc_refs": corpora["docs"].count(id_str),
    }


def extract_dependencies(text: str) -> list[str]:
    """Extract DEC/BUG/INV/CAV/F references from a string.

    Patterns recognized: 'SUPERSEDED_BY DEC-422', 'BLOCKED_ON DEC-298',
    'Joint DEC-491', 'BUG-095', and any plain ID mention.
    """
    if not text:
        return []
    pattern = re.compile(r"\b(DEC-\d+|BUG-\d+|INV-\d+|CAV-\d+|L-\d+|F-\d+)\b")
    return sorted(set(pattern.findall(text)))


def parse_sprint_dec_map(eng_register_path: Path) -> dict[str, list[str]]:
    """Walk ENGINEERING_REGISTER.md Sprint sections, return
    {DEC-NNN: [sprint_short_names]}.

    Sprint header pattern: '### Sprint X - Title'.
    """
    if not eng_register_path.exists():
        return {}
    text = eng_register_path.read_text(encoding="utf-8", errors="ignore")
    parts = re.split(r"^### (Sprint [^\n]+)$", text, flags=re.MULTILINE)
    # parts[0] = preamble, then alternating (title, body)
    out: dict[str, set] = {}
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        # Short name: first 30 chars of title
        short = title[:30]
        for m in re.finditer(r"DEC-(\d+)", body):
            dec_id = f"DEC-{m.group(1)}"
            out.setdefault(dec_id, set()).add(short)
    return {k: sorted(v) for k, v in out.items()}


def parse_caveats(path: Path) -> list[dict]:
    """Parse LIMITATIONS_CAVEATS_ASSUMPTIONS.md ### CAV-NNN sections."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    cav_re = re.compile(r"^### (CAV-\d+(?:\w*)?)\s+(.+?)(?:\n|$)", re.MULTILINE)
    entries: list[dict] = []
    for m in cav_re.finditer(text):
        cav_id = m.group(1)
        title_line = m.group(2).strip()
        start = m.end()
        next_match = cav_re.search(text, start)
        end = next_match.start() if next_match else min(start + 2000, len(text))
        body = text[start:end]
        status = "ACTIVE"
        if "RESOLVED" in body[:300].upper() or "RESOLVED" in title_line.upper():
            status = "RESOLVED"
        elif "MITIGATED" in body[:300].upper():
            status = "MITIGATED"
        impact_match = re.search(r"\*\*Operational impact:\*\*\s*(.+?)(?=\*\*|\n\n)", body, re.DOTALL)
        impact = (impact_match.group(1).strip()[:200] if impact_match else "")
        entries.append({
            "id": cav_id,
            "title": title_line[:160],
            "status": status,
            "impact": impact,
        })
    return entries


def parse_learnings(path: Path) -> list[dict]:
    """Parse LEARNINGS.md ### Title lines as L-NNN entries (sequential numbering)."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    # Each lesson is an `### Title` under `## N. SECTION`
    lesson_re = re.compile(r"^### ([^\n]+)\n([^\n].*?)(?=\n###|\n##|\Z)", re.DOTALL | re.MULTILINE)
    entries: list[dict] = []
    counter = 0
    for m in lesson_re.finditer(text):
        title = m.group(1).strip()
        body = m.group(2).strip()[:400]
        counter += 1
        entries.append({
            "id": f"L-{counter:03d}",
            "title": title[:200],
            "body": body[:400],
        })
    return entries


def get_active_bgs() -> list[dict]:
    """Detect active prefetch background processes via `ps`."""
    try:
        r = subprocess.run(["ps", "-ef"], capture_output=True, text=True, check=False)
    except Exception:
        return []
    bgs: list[dict] = []
    SCRIPT_PATTERNS = {
        "prefetch_finnhub_full": "Finnhub free-tier (10 endpoints x 1937 tickers)",
        "prefetch_quiver_new_endpoints": "Quiver senate/house/spacs/twitter",
        "prefetch_quiver.py": "Quiver 7 endpoints",
        "prefetch_polygon_indicators": "Polygon SMA/EMA/RSI/MACD",
        "prefetch_polygon_benzinga": "Polygon Benzinga 5 endpoints",
        "prefetch_polygon_corp_actions_full": "Polygon dividends/splits/IPOs",
        "prefetch_polygon_reference_extended": "Polygon reference extended fields",
        "prefetch_polygon_news": "Polygon news re-fetch",
        "prefetch_polygon_ohlcv_daily": "Polygon OHLCV daily",
        "prefetch_sec_xbrl": "SEC EDGAR XBRL companyfacts",
        "prefetch_sec_edgar": "SEC EDGAR per-form",
        "prefetch_polygon_indices": "Polygon Indices Basic",
        "prefetch_polygon_forex": "Polygon Forex Basic",
        "prefetch_polygon_futures": "Polygon Futures Basic",
        "prefetch_polygon_options": "Polygon Options Basic (chain ref)",
        "prefetch_polygon_economy": "Polygon Economy",
        "prefetch_alfred_mirror": "ALFRED vintage mirror",
        "prefetch_cftc_extended": "CFTC 5 missing datasets",
        "prefetch_apewisdom_subreddits": "Apewisdom 8 subreddit feeds",
        "prefetch_alphavantage_news": "Alpha Vantage news",
    }
    for line in r.stdout.split("\n"):
        for pat, desc in SCRIPT_PATTERNS.items():
            if pat in line and "grep" not in line:
                cols = line.split()
                pid = cols[1] if len(cols) > 1 else "?"
                etime = cols[5] if len(cols) > 5 else "?"
                bgs.append({"pid": pid, "elapsed": etime, "script": pat, "description": desc})
                break
    return bgs


def get_pending_pipeline() -> list[dict]:
    """Hard-coded pipeline of queued Tier H items + ETAs (per Pass 53
    Day-9 v8h+1 owner-asked timeline 2026-05-08)."""
    return [
        {"item": "H10 Polygon Options chains (1937 underlyings)", "api": "Polygon", "wallclock": "10-30h", "rate_limit": "Stocks Starter unlimited; storage caveat", "blocker": False, "priority": "P1"},
        {"item": "H20 pytrends 4 dimensions (interest_by_region/related_queries/related_topics/get_historical_interest)", "api": "Google Trends", "wallclock": "8-12h", "rate_limit": "rate-limited single-thread", "blocker": False, "priority": "P2"},
        {"item": "H21 AAII extended fields (8wk avg / historical avg / S&P close)", "api": "AAII", "wallclock": "~1h", "rate_limit": "manual download", "blocker": False, "priority": "P3"},
        {"item": "H8 Polygon Futures redesign (per-contract dated symbol logic)", "api": "Polygon Futures Basic", "wallclock": "2-4h code + 2h fetch", "rate_limit": "free 5/min", "blocker": False, "priority": "P2"},
        {"item": "AlphaVantage news re-fetch (INV-015)", "api": "AlphaVantage", "wallclock": "10-15h or 4 days", "rate_limit": "free 500/day", "blocker": False, "priority": "P1"},
        {"item": "USAspending.gov daily-grain gov contracts (INV-024 alternate)", "api": "USAspending", "wallclock": "2-3h", "rate_limit": "free, no auth", "blocker": False, "priority": "P2"},
        {"item": "H14 Quiver Twitter full-universe (currently in flight)", "api": "Quiver", "wallclock": "~45-60min remaining", "rate_limit": "1.2s per call", "blocker": False, "priority": "P2"},
        {"item": "Tier J1 ticker case standardization", "api": "local", "wallclock": "1h script + run", "rate_limit": "n/a", "blocker": False, "priority": "P3"},
        {"item": "Tier J3 numeric type coercion across all sources", "api": "local", "wallclock": "1-2h", "rate_limit": "n/a", "blocker": False, "priority": "P3"},
        {"item": "Tier J4 schema regression test", "api": "local", "wallclock": "2-3h", "rate_limit": "n/a", "blocker": False, "priority": "P3"},
        {"item": "Tier J5 parquet compression (snappy)", "api": "local", "wallclock": "1h", "rate_limit": "n/a", "blocker": False, "priority": "P3"},
        {"item": "Tier J6 safe_filename_stem() propagation to all prefetch scripts", "api": "local", "wallclock": "1h", "rate_limit": "n/a", "blocker": False, "priority": "P3"},
        {"item": "Tier J7 null/missing normalization", "api": "local", "wallclock": "2h", "rate_limit": "n/a", "blocker": False, "priority": "P3"},
        {"item": "Tier J8 _schema.json per cache directory", "api": "local", "wallclock": "2h", "rate_limit": "n/a", "blocker": False, "priority": "P3"},
    ]


def get_timeline_summary() -> dict:
    """Realistic parallelized end-to-end timeline (per owner Q 2026-05-08)."""
    return {
        "next_5h": "Finnhub + Quiver Twitter active BGs done",
        "next_12_15h": "H10 Options chain reference + H20 pytrends + H21 AAII + H8 Futures + USAspending parallel BGs done",
        "next_24_30h": "H10 Options per-contract aggs (top-100 underlyings) + AV news multi-day if strict free-tier",
        "next_36_48h": "Tier J normalization scripts authored + run",
        "phase_1a_runway": "May 15 (7 days)",
        "net_estimate": "~24-48h wall-clock to reach 100% coverage of accessible endpoints + all dimensions stored + normalized",
        "caveats": [
            "AlphaVantage strict 500/day cap could turn 10-15h into 4 days",
            "pytrends throttles for hours when Google detects bot pattern; could double estimate",
            "H10 Options storage could blow up (100s of GB beyond top-100 underlyings)",
        ],
    }


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
    print("Loading corpora for ID-status grep ...")
    corpora = load_status_corpora()
    print(f"  prod={len(corpora['prod'])} tests={len(corpora['tests'])} backtest_all={len(corpora['backtest_all'])} scripts={len(corpora['scripts'])} git_log={len(corpora['git_log'])}")

    decisions = parse_decisions(REPO_ROOT / "AUDIT_INDEX.md")
    bugs = parse_bug_register(REPO_ROOT / "BUG_REGISTER.md")
    invs = parse_inv_entries(REPO_ROOT / "OPEN_INVESTIGATIONS.md")
    cavs = parse_caveats(REPO_ROOT / "LIMITATIONS_CAVEATS_ASSUMPTIONS.md")
    lessons = parse_learnings(REPO_ROOT / "LEARNINGS.md")

    # Sprint mapping (DEC-NNN -> [sprint names]) from ENGINEERING_REGISTER.md
    print("Parsing sprint x decision map ...")
    sprint_map = parse_sprint_dec_map(REPO_ROOT / "ENGINEERING_REGISTER.md")
    print(f"  decisions with sprint assignment: {len(sprint_map)}")

    # Attach 4-status (coded / wired / tested / pushed) to each
    print("Computing per-ID status (coded/wired/tested/pushed)...")
    for d in decisions:
        # Normalize ID for grep: AUDIT_INDEX uses "DECISION-001" but actual code/commits use "DEC-001"
        full_id = d["id"]
        short_id = full_id.replace("DECISION-", "DEC-")
        d["status_grep"] = id_status(short_id, corpora)
        d["short_id"] = short_id
        d["sprint"] = "; ".join(sprint_map.get(short_id, [])) or "-"
        d["dependencies"] = "; ".join(extract_dependencies(d["title"] + " " + d["status"])) or "-"
    for b in bugs:
        full_id = b["id"]
        m = re.match(r"BUG-(\d+)$", full_id)
        if m:
            short = f"BUG-{int(m.group(1)):03d}"
        else:
            short = full_id
        b["status_grep"] = id_status(short, corpora)
        b["short_id"] = short
        # BUG already has sprint_context column from BUG_REGISTER
        b["sprint"] = b.get("sprint_context", "-") or "-"
        b["dependencies"] = "; ".join(extract_dependencies(b.get("linked_decisions", "") + " " + b.get("title", ""))) or "-"
    for i in invs:
        i["status_grep"] = id_status(i["id"], corpora)
        i["dependencies"] = "; ".join(extract_dependencies(i.get("title", "") + " " + i.get("summary", ""))) or "-"
    for c in cavs:
        c["status_grep"] = id_status(c["id"], corpora)
        c["dependencies"] = "; ".join(extract_dependencies(c.get("title", "") + " " + c.get("impact", ""))) or "-"
    # L-NNN don't need status grep (they're principles, not code)

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decisions": decisions,
        "bugs": bugs,
        "investigations": invs,
        "caveats": cavs,
        "learnings": lessons,
        "tier_items": parse_tier_table(REPO_ROOT / "PHASE_1A_PRELAUNCH_TODO.md"),
        "recent_commits": get_recent_commits(30),
        "uncommitted": get_uncommitted_files(),
        "unpushed_commits": get_unpushed_commits(),
        "active_bgs": get_active_bgs(),
        "pending_pipeline": get_pending_pipeline(),
        "timeline_summary": get_timeline_summary(),
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
