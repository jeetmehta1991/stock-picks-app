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


# DEC-503 / CHECKLIST 69: 9-layer test pyramid. Each layer maps to specific
# test files. A layer with no mapped file means we have NO tests in that
# layer yet (which is informative - exposes coverage gaps).
TEST_PYRAMID_LAYERS = {
    "unit": ["test_unit.py", "test_prefetch_utils.py"],
    "smoke": ["test_smoke.py"],
    "integration": ["test_integration.py"],
    "system": ["test_gate_pre_phase_1a_entry.py"],
    "functional": ["test_doc_count_consistency.py"],
    "regression": ["test_regression.py"],
    "data_integrity": ["test_schema_canonical.py"],
    "performance": ["test_performance.py"],
    "acceptance": ["test_acceptance.py"],
    "property": ["test_property.py"],
    "snapshot": ["test_snapshot.py"],
    "contract": ["test_contract.py"],
    "compatibility": ["test_compatibility.py"],
}


# Per-ID per-layer applicability overrides (Pass 53 v8h+1 owner directive
# 2026-05-09: a bool boolean for every layer is misleading - some IDs have
# layers that simply don't apply. Annotate "N/A" or "LATER" here so the
# dashboard distinguishes 'no coverage' (gap) from 'not applicable' (correct).
#
# Format: { id_short: { layer: "N/A" | "LATER:reason" } }
# Layers not listed default to the bool grep result (YES / no).
PYRAMID_OVERRIDES: dict[str, dict[str, str]] = {
    # BUG-007 is an environmental guard fix (run_phase1a accepts --no-agents
    # without ANTHROPIC_API_KEY). Only regression layer is meaningful;
    # other layers don't apply to this kind of bug.
    "BUG-007": {
        "unit": "N/A",
        "smoke": "N/A",
        "integration": "N/A",
        "system": "N/A",
        "functional": "N/A",
        "data_integrity": "N/A",
        "performance": "N/A",
        "acceptance": "N/A",
        "property": "N/A",
        "snapshot": "N/A",
        "contract": "N/A",
        "compatibility": "N/A",
    },
}


def load_status_corpora() -> dict:
    """Pre-load text corpora for ID-status grep (coded/wired/pushed/tested).
    Tests corpus is also broken out per pyramid layer (DEC-503)."""
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
    def cat_files(filenames):
        out = []
        tests_dir = REPO_ROOT / "backtest" / "tests"
        for fn in filenames:
            p = tests_dir / fn
            if p.exists():
                try:
                    out.append(p.read_text(encoding="utf-8", errors="ignore"))
                except Exception:
                    pass
        return "\n".join(out)

    prod = cat(["backtest/data", "backtest/engine", "backtest/signals", "backtest/results"])
    tests = cat(["backtest/tests"])
    backtest_all = cat(["backtest"])
    scripts = cat(["scripts"])
    # Per-pyramid-layer corpora
    layers = {layer: cat_files(files) for layer, files in TEST_PYRAMID_LAYERS.items()}
    docs_text = ""
    for d in ("AUDIT.md", "AUDIT_INDEX.md", "BUG_REGISTER.md", "PHASE_1A_PRELAUNCH_TODO.md"):
        p = REPO_ROOT / d
        if p.exists():
            docs_text += "\n" + p.read_text(encoding="utf-8", errors="ignore")
    # git log: full message (subject + body) - 2026-05-09 fix per owner
    # finding that BUG-007 mentions in commit body weren't being detected
    # (was using %s subject-only). %B is the full raw body. Force utf-8
    # decode + errors=replace because some commit messages contain non-cp1252
    # characters (em-dashes from older commits) that crashed default decode.
    try:
        r = subprocess.run(
            ["git", "log", "--all", "--pretty=format:%B%n----COMMIT----"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
            encoding="utf-8", errors="replace",
        )
        git_log_subjects = r.stdout or ""
    except Exception:
        git_log_subjects = ""
    return {
        "prod": prod,
        "tests": tests,
        "backtest_all": backtest_all,
        "scripts": scripts,
        "docs": docs_text,
        "git_log": git_log_subjects,
        "pyramid_layers": layers,
    }


def id_status(id_str: str, corpora: dict) -> dict:
    """For a given ID (e.g. DEC-422 / BUG-001 / INV-024 / CAV-070), return:
      coded:  referenced in backtest/ or scripts/ Python
      wired:  referenced in active path (data/engine/signals/results)
      tested: referenced in backtest/tests/ (rolls up across pyramid)
      pushed: referenced in any git commit subject (=> code change merged)
      n_doc_refs: doc-only references (AUDIT.md / etc.) for context
      pyramid: per-layer test coverage (DEC-503 9-layer model). Empty layers
               (no test files mapped yet) always evaluate False to surface
               the coverage gap rather than pretend coverage exists.
    """
    if not id_str or len(id_str) < 4:
        return {
            "coded": False, "wired": False, "tested": False, "pushed": False,
            "n_doc_refs": 0,
            "pyramid": {layer: False for layer in TEST_PYRAMID_LAYERS},
        }
    pyramid_layers = corpora.get("pyramid_layers", {})
    overrides = PYRAMID_OVERRIDES.get(id_str, {})
    pyramid: dict = {}
    for layer in TEST_PYRAMID_LAYERS:
        # Detected coverage from grep
        detected = id_str in pyramid_layers.get(layer, "")
        if detected:
            # Coverage exists - YES wins regardless of override
            pyramid[layer] = True
        elif layer in overrides:
            # Apply manual override (N/A or LATER:reason)
            pyramid[layer] = overrides[layer]
        else:
            # Default: no coverage (treated as gap)
            pyramid[layer] = False
    return {
        "coded": (id_str in corpora["backtest_all"]) or (id_str in corpora["scripts"]),
        "wired": id_str in corpora["prod"],
        "tested": id_str in corpora["tests"],
        "pushed": id_str in corpora["git_log"],
        "n_doc_refs": corpora["docs"].count(id_str),
        "pyramid": pyramid,
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


def parse_audit_descriptions() -> dict[str, str]:
    """Parse AUDIT.md for ### BUG-NN / ### DEC-NN sections and index by ID.
    Returns the first 1-3 lines of body content as a short description.
    Owner directive 2026-05-09: dashboards must surface descriptions, not
    just titles, so the user can decode each entry without leaving the page."""
    audit = REPO_ROOT / "AUDIT.md"
    if not audit.exists():
        return {}
    text = audit.read_text(encoding="utf-8", errors="ignore")
    out: dict[str, str] = {}
    # Pattern: heading line + body until next heading or 4 blank-line gap
    heading_re = re.compile(
        r"^### (BUG-\d+(?:[-_]\w+)?|DEC-\d+(?:[-_]\w+)?|DECISION-\d+(?:[-_]\w+)?)"
        r"(?:\s*[" + chr(0xb7) + r":.\-]\s*|\s+)(.+?)$",
        re.MULTILINE,
    )
    matches = list(heading_re.finditer(text))
    for i, m in enumerate(matches):
        raw_id = m.group(1)
        # Normalize: BUG-01 -> BUG-001 to match dashboard's short_id convention
        num_match = re.match(r"(BUG|DEC|DECISION)-(\d+)(.*)$", raw_id)
        if num_match:
            kind = "BUG" if num_match.group(1) == "BUG" else "DEC"
            num = int(num_match.group(2))
            suffix = num_match.group(3)
            norm_id = f"{kind}-{num:03d}{suffix}"
        else:
            norm_id = raw_id
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else min(body_start + 1500, len(text))
        body = text[body_start:body_end].strip()
        # Pull first 200 chars of substantive content (skip blank lines)
        first_lines = []
        for line in body.split("\n"):
            stripped = line.strip()
            if not stripped:
                if first_lines:
                    break  # First blank after content = end of intro
                continue
            first_lines.append(stripped)
            if sum(len(s) for s in first_lines) > 240:
                break
        desc = " ".join(first_lines)[:280]
        # Don't overwrite if a more detailed entry exists already
        if norm_id not in out or len(desc) > len(out[norm_id]):
            out[norm_id] = desc
    return out


def _classify_priority_tier(item: dict, kind: str, back_refs: dict) -> tuple[int | None, str]:
    """Classify an item into priority Tier 0-7. Returns (tier, reason) or
    (None, '') if not actionable (RESOLVED-DECIDED with no pyramid gap).
    See AUDIT.md / Pass 53 v8h+1 owner-approved 2026-05-08 framework."""
    title = (item.get("title") or "").upper()
    status = (item.get("status") or "").upper()
    sg = item.get("status_grep") or {}
    item_id = item.get("short_id") or item.get("id") or ""

    # Tier 0: Phase 1A May 15 blockers (explicit)
    if "BUG-007" in item_id and not sg.get("tested"):
        return 0, "BUG-007 API key guard blocks --no-agents (explicit Phase 1A dep)"
    if "PHASE 1A" in title and ("BLOCK" in title or "DEPENDENCY" in title):
        return 0, "Phase 1A blocker per title"
    if kind == "inv" and "OPEN" in status and ("CRITICAL" in title or "HIGH" in (item.get("severity", "") or "").upper()):
        return 0, "INV OPEN with HIGH/CRITICAL severity"

    # Tier 1: Dependency root - many downstream items reference this
    n_back = back_refs.get(item_id, 0)
    if n_back >= 3:
        return 1, f"Dependency root ({n_back} downstream items reference)"

    # Tier 2: CRITICAL OPEN
    if "CRITICAL" in title:
        if status in ("", "OPEN") or "OPEN" in status:
            return 2, "CRITICAL OPEN"

    # Tier 3: coded but NOT wired (silent gap pattern - L146 / DEC-507)
    if sg.get("coded") and not sg.get("wired") and sg.get("pushed"):
        return 3, "coded + pushed but not wired (silent gap candidate)"

    # Tier 4: PARTIAL-SPEC-ONLY
    if "PARTIAL-SPEC-ONLY" in status or "PARTIAL-SPEC" in status:
        return 4, "PARTIAL-SPEC-ONLY: needs implementation OR explicit defer"

    # Tier 5: Wired + tested rollup but pyramid coverage thin
    pyramid = sg.get("pyramid") or {}
    if sg.get("wired") and sg.get("tested"):
        covered = sum(1 for v in pyramid.values() if v)
        if covered < 5:
            return 5, f"Pyramid gap: {covered}/13 layers covered"

    # Tier 6: SUPERSEDED / OBSOLETE cleanup
    if "SUPERSEDED" in status or "OBSOLETE" in status:
        return 6, "Cleanup: confirm no live deps, delete refs"

    # Tier 7: Deferred - quarterly verification
    if "DEFERRED" in status:
        return 7, "Verify deferral rationale still holds"

    # PROPOSED / NEEDS_CLARIFICATION
    if "PROPOSED" in status or "NEEDS_CLARIFICATION" in status:
        return 4, f"Status={status}: owner decision needed"

    return None, ""


def compute_next_up(decisions: list, bugs: list, invs: list, max_items: int = 20) -> list[dict]:
    """Rank actionable items into priority tiers and return the top N.
    Owner directive 2026-05-08."""
    # Pass 1: build back-reference counts (which IDs do other items depend on)
    back_refs: dict = {}
    for d in decisions:
        for dep in (d.get("dependencies") or "").split(";"):
            dep = dep.strip()
            if dep and dep != "-":
                back_refs[dep] = back_refs.get(dep, 0) + 1
    for b in bugs:
        deps_str = (b.get("dependencies") or "") + " " + (b.get("linked_decisions") or "")
        for dep in re.findall(r"DEC-\d+|BUG-\d+|INV-\d+", deps_str):
            back_refs[dep] = back_refs.get(dep, 0) + 1

    # Pass 2: classify each item
    ranked: list[dict] = []
    for d in decisions:
        tier, reason = _classify_priority_tier(d, "decision", back_refs)
        if tier is None:
            continue
        ranked.append({
            "kind": "DEC",
            "id": d.get("short_id") or d.get("id"),
            "title": (d.get("title") or "")[:140],
            "status": d.get("status", "-"),
            "tier": tier,
            "reason": reason,
            "back_refs": back_refs.get(d.get("short_id") or d.get("id"), 0),
            "sprint": d.get("sprint", "-"),
        })
    for b in bugs:
        tier, reason = _classify_priority_tier(b, "bug", back_refs)
        if tier is None:
            continue
        ranked.append({
            "kind": "BUG",
            "id": b.get("short_id") or b.get("id"),
            "title": (b.get("title") or "")[:140],
            "status": "OPEN",  # BUG_REGISTER doesn't track status per row
            "tier": tier,
            "reason": reason,
            "back_refs": back_refs.get(b.get("short_id") or b.get("id"), 0),
            "sprint": b.get("sprint", "-") or b.get("sprint_context", "-"),
        })
    for inv in invs:
        tier, reason = _classify_priority_tier(inv, "inv", back_refs)
        if tier is None:
            continue
        ranked.append({
            "kind": "INV",
            "id": inv.get("id"),
            "title": (inv.get("title") or "")[:140],
            "status": inv.get("status", "-"),
            "tier": tier,
            "reason": reason,
            "back_refs": back_refs.get(inv.get("id"), 0),
            "sprint": "-",
        })

    # Sort by (tier asc, back_refs desc, id asc) then take top N
    ranked.sort(key=lambda x: (x["tier"], -x["back_refs"], x["id"]))
    return ranked[:max_items]


def get_structural_drift() -> dict:
    """Walk data_prefetch/ for any subdir containing >=1 parquet; cross-check
    against the union of CACHE_PATHS scanned by build_dashboard_sprint0a.

    Per owner directive 2026-05-08 (after polygon_options gap was missed by
    the 2-hour drift cron because cron only checks numerical drift): this
    function surfaces STRUCTURAL drift - cached subdirs not represented in
    the dashboard scan list.
    """
    # Cached subdirs (have >=1 parquet)
    cached: set[str] = set()
    pf = REPO_ROOT / "data_prefetch"
    if pf.is_dir():
        for p in pf.rglob("*.parquet"):
            rel = str(p.parent.relative_to(REPO_ROOT)).replace("\\", "/")
            if "legacy_archive" in rel:
                continue
            cached.add(rel)

    # Scanned by sprint0a dashboard - parse CACHE_PATHS list from source
    sprint0a_path = REPO_ROOT / "scripts" / "build_dashboard_sprint0a.py"
    scanned: set[str] = set()
    if sprint0a_path.exists():
        text = sprint0a_path.read_text(encoding="utf-8", errors="ignore")
        # Match tuples like ("polygon", "news", "data_prefetch/polygon/news", "per_ticker")
        for m in re.finditer(r'"(data_prefetch/[^"]+)"', text):
            scanned.add(m.group(1).replace("\\", "/").rstrip("/"))

    # Filter cached: drop trivial top-level placeholders (like data_prefetch
    # itself) and dirs that are clearly transient (_checkpoint files only).
    uncovered = sorted(
        c for c in cached
        if c not in scanned
        and not any(c.startswith(s + "/") for s in scanned)  # parent already scanned
    )
    return {
        "cached_dir_count": len(cached),
        "scanned_dir_count": len(scanned),
        "uncovered": uncovered,
        "uncovered_count": len(uncovered),
    }


def get_reference_tables() -> dict:
    """Owner-requested reference page: 4-badge meanings, full-system stages
    1-4, and Stage 2 sub-phases. Static content - update when the project
    structure changes."""
    return {
        "badges": [
            {
                "stage": "Coded",
                "definition": "The function/class/signal exists physically in a file.",
                "detection": "grep finds it in backtest/, scripts/, or agents/.",
                "failure_mode": "Spec written in AUDIT.md but never implemented; coded=NO.",
            },
            {
                "stage": "Wired",
                "definition": "Code is reachable from a runtime entry point (run_phase1a, prefetch script, agent pipeline). Actually CALLED.",
                "detection": "Grep finds it imported + called from a hot-path module (backtest/data, engine, signals, results); not orphan code.",
                "failure_mode": "L146 / DEC-507: Polygon news cached + smart_money.get_news_sentiment coded, but the function read legacy cache/av_news/ paths -> coded=YES, wired=NO.",
            },
            {
                "stage": "Tested",
                "definition": "A test exercises the code path. ROLLS UP across the 9-layer DEC-503 pyramid.",
                "detection": "Per-layer corpus grep using TEST_PYRAMID_LAYERS map. A YES rollup hides per-layer gaps; see pyramid columns for layer breakdown.",
                "failure_mode": "Function works, but no test exercises it; if it breaks no test fails -> silent regression.",
            },
            {
                "stage": "Pushed",
                "definition": "Change is on origin/main.",
                "detection": "git log --all subject lines reference the ID.",
                "failure_mode": "Local-only fix lost in a session reset.",
            },
        ],
        "stages": [
            {"stage": "Stage 1: Foundation", "status": "DONE (pre-Pass 53)", "description": "Codebase scaffolded; tooling chosen; CI / hooks / tests / git layout."},
            {"stage": "Stage 2: Strategy validation", "status": "CURRENT", "description": "Validate strategies via backtest before any real money. Subdivided into Phase 0A/1A/1B/1C+ below."},
            {"stage": "Stage 3: Papertrading", "status": "Future", "description": "Run live with simulated capital; verify the engine works end-to-end against real-time data."},
            {"stage": "Stage 4: Live trading", "status": "Future", "description": "Real money. Email-based per-trade approvals (per DEC, not Telegram)."},
        ],
        "phases": [
            {"phase": "Phase 0A", "status": "CURRENT (Sprint 0A - Pass 53)", "purpose": "Cache all Stage-2 inputs locally so backtests have NO live API calls. Universe T1a/T1b/T1c/T2/T3 + ETFs. Sprint 0A dashboard tracks this."},
            {"phase": "Phase 1A", "status": "Launch May 15 (DEC-590)", "purpose": "Run all 60 baseline strategies x 7 regimes against cached data. Owner gate at 1A-alpha (rules-only Sharpe >= 0.7 OOS)."},
            {"phase": "Phase 1A-alpha", "status": "Sub-phase", "purpose": "Strategy x regime x parameter cube; rules only."},
            {"phase": "Phase 1A-beta", "status": "Sub-phase", "purpose": "Same scope, full universe, end-to-end dry-run."},
            {"phase": "Phase 1B", "status": "After 1A passes", "purpose": "11-agent TradingAgents pipeline scores Phase 1A's candidates and overlays a tier adjustment (>=75 upgrade, <=40 downgrade). Haiku model (~$116 CAD)."},
            {"phase": "Phase 1B-alpha", "status": "Sub-phase", "purpose": "Rules + agents combined cube; A/B vs 1A baseline."},
            {"phase": "Phase 1C+", "status": "After 1B passes", "purpose": "Overlays: news (Unusual Whales), options (H10 ep2), pytrends. Sonnet model."},
        ],
        "pyramid": [
            {"col": "U",  "layer": "Unit",          "asserts": "One function/class behaves correctly in isolation.",                                          "when_to_run": "Run unless the addressal is doc-only (no code touched).",                              "files": "test_unit.py, test_prefetch_utils.py"},
            {"col": "Sm", "layer": "Smoke",          "asserts": "The minimum end-to-end path runs without crashing (script imports, dashboard builds, etc.).", "when_to_run": "Run if any prefetch / dashboard / runner script touched.",                            "files": "test_smoke.py"},
            {"col": "I",  "layer": "Integration",   "asserts": "Multiple components collaborate correctly across module boundaries.",                          "when_to_run": "Run if any cross-module call path touched.",                                          "files": "test_integration.py"},
            {"col": "Sy", "layer": "System",         "asserts": "Full pipeline / Phase 1A entry path produces the expected output.",                            "when_to_run": "Run if Phase 1A entry path touched.",                                                 "files": "test_gate_pre_phase_1a_entry.py"},
            {"col": "F",  "layer": "Functional",    "asserts": "Parser / schema / cross-doc correctness; user-visible behavior matches spec.",                  "when_to_run": "Run if doc / parser / dashboard touched.",                                            "files": "test_doc_count_consistency.py"},
            {"col": "R",  "layer": "Regression",    "asserts": "A previously-fixed bug stays fixed (one test per resolved BUG-NN).",                            "when_to_run": "ALWAYS run if a BUG is being claimed RESOLVED (the BUG-NN test must exist).",         "files": "test_regression.py"},
            {"col": "D",  "layer": "Data integrity", "asserts": "Cache shape and schema invariants (every cached parquet matches its locked column set).",      "when_to_run": "Run if any cache schema touched.",                                                    "files": "test_schema_canonical.py"},
            {"col": "P",  "layer": "Performance",   "asserts": "Runtime / memory stays within bounds (no O(n^2) sneaks; cache loads under budget).",            "when_to_run": "Run if hot-path code touched.",                                                       "files": "test_performance.py"},
            {"col": "A",  "layer": "Acceptance",    "asserts": "Owner-defined pass criteria met (9-criteria PASSING_CRITERIA + per-regime verdict).",            "when_to_run": "Run if PASSING_CRITERIA / 9-criteria touched.",                                       "files": "test_acceptance.py + golden/"},
            {"col": "Pr", "layer": "Property-based", "asserts": "Invariants hold for ALL valid inputs (Hypothesis-generated counterexamples).",                  "when_to_run": "Run if invariant-bearing code touched (regime classifier, profit_factor, etc.).",     "files": "test_property.py"},
            {"col": "Sn", "layer": "Snapshot",       "asserts": "Output shape and key counts match a frozen golden baseline.",                                  "when_to_run": "Run if dashboard data shape OR a golden fixture touched.",                            "files": "test_snapshot.py"},
            {"col": "C",  "layer": "Contract",       "asserts": "Our parser handles the actual API response shape (frozen mock fixtures per source).",          "when_to_run": "Run if API parser touched.",                                                          "files": "test_contract.py"},
            {"col": "Cm", "layer": "Compatibility",  "asserts": "Code works across the supported Python / pandas / pyarrow matrix.",                            "when_to_run": "Run if pandas / numpy / pyarrow API surface touched.",                                "files": "test_compatibility.py"},
        ],
        "badge_meaning": [
            {"col": "Coded",  "meaning": "Code with this ID/name reference exists in backtest/ or scripts/ (any Python file). Detected by grep across prod + tests + scripts corpora."},
            {"col": "Wired",  "meaning": "Code is reachable from a runtime entry point - actually CALLED from backtest/data, engine, signals, results (the active path), not orphan code."},
            {"col": "Tested", "meaning": "Rolled-up: ANY of the 13 pyramid layers reference the ID. The 13 layer columns to the right show per-layer breakdown."},
            {"col": "Pushed", "meaning": "Change is on origin/main per git log --all subject lines."},
            {"col": "U / Sm / I / Sy / F / R / D / P / A / Pr / Sn / C / Cm", "meaning": "13 pyramid layer columns: per-layer test coverage. 4-state cell (Pass 53 v8h+1 owner directive 2026-05-09): YES = a test in this layer references the ID; no = layer applies but no coverage (real gap); N/A = layer doesn't apply to this ID type (e.g. property-based test for an env-guard fix); LATER = applicable but deferred to a later phase (hover for reason). See PYRAMID_OVERRIDES dict in build_dashboard_stage_2.py for the per-ID annotations."},
        ],
    }


def get_automation_status() -> list[dict]:
    """Surface the automation infrastructure that other parts of the dashboard
    don't represent. Each entry: name + what it does + how to verify.
    """
    items = []

    # 1. Pre-commit hook chain
    hook_path = REPO_ROOT / ".git" / "hooks" / "pre-commit"
    hook_installed = hook_path.exists()
    hook_text = hook_path.read_text(errors="ignore") if hook_installed else ""
    items.append({
        "name": "Pre-commit hook chain",
        "description": "preflight.py (unicode/em-dash/canonical-source/git-commit-capture) + sync_doc_counts.py --check (cross-doc count drift)",
        "installed": hook_installed,
        "gates": [
            "preflight" if "preflight.py" in hook_text else "MISSING preflight",
            "sync_doc_counts" if "sync_doc_counts.py" in hook_text else "MISSING sync_doc_counts",
        ],
        "source": "scripts/git_hooks/pre-commit (canonical) + .git/hooks/pre-commit (installed)",
    })

    # 2. 2-hour drift cron (session-scoped)
    items.append({
        "name": "2-hour drift-alignment cron",
        "description": "Owner-mandated 2026-05-08: every 2h auto-runs sync_doc_counts.py --update + dashboard rebuilds + status updates. Content changes need explicit owner approval.",
        "installed": "session-only",
        "schedule": "minute :13 every 2h local",
        "scope_limits": "drift alignment + status updates ONLY; no content/rule/threshold changes",
        "source": "CronCreate runtime (resets at session end; not persisted to disk despite durable=true flag).",
    })

    # 3. Doc count drift detector
    items.append({
        "name": "Doc count drift detector (sync_doc_counts.py)",
        "description": "Asserts header numerical claims match source-of-truth tables. Uses canonical parsers (parse_decisions/parse_bug_register/parse_inv_entries) for BUG/INV/DEC; regex for CHECKLIST/CAV.",
        "installed": (REPO_ROOT / "scripts" / "sync_doc_counts.py").exists(),
        "modes": ["--check (CI gate)", "--update (manual sync)"],
        "source": "scripts/sync_doc_counts.py",
    })

    # 4. Schema canonical regression test (J4)
    schema_test = REPO_ROOT / "backtest" / "tests" / "test_schema_canonical.py"
    items.append({
        "name": "Schema canonical regression (J4)",
        "description": "23 cache-dir column sets locked by parametrized pytest. Catches prefetch scripts writing extra/missing columns.",
        "installed": schema_test.exists(),
        "source": "backtest/tests/test_schema_canonical.py + scripts/write_cache_schemas.py + 23 _schema.json sidecars",
    })

    # 5. Cross-doc count consistency tests
    cross_test = REPO_ROOT / "backtest" / "tests" / "test_doc_count_consistency.py"
    items.append({
        "name": "Cross-doc count consistency tests",
        "description": "11 tests: AUDIT_INDEX/BUG_REGISTER/CHECKLIST/INV/CAV claim-vs-table cross-checks + dashboard parser correctness gates + duplicate-const JS gate.",
        "installed": cross_test.exists(),
        "source": "backtest/tests/test_doc_count_consistency.py",
    })

    # 6. Shared prefetch helper (J6)
    helper = REPO_ROOT / "scripts" / "_prefetch_utils.py"
    items.append({
        "name": "Shared safe_filename_stem helper (J6)",
        "description": "Canonical helper for new prefetch scripts. Avoids Windows reserved names (CON/PRN/AUX/NUL/COM*/LPT*).",
        "installed": helper.exists(),
        "source": "scripts/_prefetch_utils.py + 7 unit tests in test_prefetch_utils.py",
    })

    return items


def get_test_inventory() -> dict:
    """Count tests in the repo by module, for the dashboard's pyramid panel."""
    test_dir = REPO_ROOT / "backtest" / "tests"
    if not test_dir.is_dir():
        return {"total": 0, "by_module": {}}
    by_module: dict = {}
    total = 0
    for f in sorted(test_dir.glob("test_*.py")):
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        n = len(re.findall(r"^def test_\w+", text, re.MULTILINE))
        if n:
            by_module[f.stem] = n
            total += n
    return {"total": total, "by_module": by_module}


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
    audit_descs = parse_audit_descriptions()  # owner directive 2026-05-09
    print(f"  AUDIT.md descriptions indexed: {len(audit_descs)}")
    for d in decisions:
        # Normalize ID for grep: AUDIT_INDEX uses "DECISION-001" but actual code/commits use "DEC-001"
        full_id = d["id"]
        short_id = full_id.replace("DECISION-", "DEC-")
        d["status_grep"] = id_status(short_id, corpora)
        d["short_id"] = short_id
        d["sprint"] = "; ".join(sprint_map.get(short_id, [])) or "-"
        d["dependencies"] = "; ".join(extract_dependencies(d["title"] + " " + d["status"])) or "-"
        d["description"] = audit_descs.get(short_id, "") or audit_descs.get(full_id, "") or ""
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
        b["description"] = audit_descs.get(short, "") or ""
    for i in invs:
        i["status_grep"] = id_status(i["id"], corpora)
        i["dependencies"] = "; ".join(extract_dependencies(i.get("title", "") + " " + i.get("summary", ""))) or "-"
        # INVs already carry a 'summary' field extracted from **Observation:**.
        # Promote it to a description alias for HTML rendering consistency.
        i["description"] = i.get("summary", "") or ""
    for c in cavs:
        c["status_grep"] = id_status(c["id"], corpora)
        c["dependencies"] = "; ".join(extract_dependencies(c.get("title", "") + " " + c.get("impact", ""))) or "-"
        # Caveats already carry an 'impact' field; promote to description.
        c["description"] = c.get("impact", "") or ""
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
        "automation_status": get_automation_status(),
        "test_inventory": get_test_inventory(),
        "pyramid_layers": list(TEST_PYRAMID_LAYERS.keys()),
        "pyramid_layer_files": TEST_PYRAMID_LAYERS,
        "structural_drift": get_structural_drift(),
        "reference_tables": get_reference_tables(),
        "next_up": compute_next_up(decisions, bugs, invs, max_items=25),
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
    # Canonical status keywords (in priority order - first match wins).
    STATUS_KEYWORDS = [
        "DONE", "RESOLVED", "DEFERRED", "BLOCKED", "PARTIAL",
        "IN-PROGRESS", "IN PROGRESS", "PENDING",
        "NEEDS-OWNER-SCOPE", "NEEDS OWNER",
        "EMPIRICALLY-CLEAN", "EMPIRICALLY CLEAN",
        "OPEN", "MOSTLY DONE",
    ]
    for t in snapshot["tier_items"]:
        raw = (t.get("status") or "").upper()
        normalized = "UNKNOWN"
        for kw in STATUS_KEYWORDS:
            if kw in raw:
                normalized = kw.replace(" ", "-")
                break
        tier_by_status[normalized] = tier_by_status.get(normalized, 0) + 1
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
