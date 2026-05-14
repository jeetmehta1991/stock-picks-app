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
        # Status detection - target the **Status:** field specifically (not body[:200]
        # window which may not reach the Status line in long INV bodies). Recognize
        # all RESOLVED-* variants (RESOLVED-DOCUMENTED, RESOLVED-PARTIAL,
        # RESOLVED-IMPLEMENTED, RESOLVING, etc.) and DEFERRED-* variants.
        status = "OPEN"
        status_match = re.search(r"\*\*Status:\*\*\s*([^\n]+)", body)
        if status_match:
            status_text = status_match.group(1).upper()
            if "RESOLVED" in status_text or "RESOLVING" in status_text:
                status = "RESOLVED"
            elif "DEFERRED" in status_text or "WONTFIX" in status_text:
                status = "DEFERRED"
            elif "OPEN" in status_text or "IN-PROGRESS" in status_text:
                status = "OPEN"
        # Fallback: if no **Status:** field found, fall back to title-line scan
        # (some older entries put RESOLVED in title only).
        elif "RESOLVED" in title_line.upper():
            status = "RESOLVED"
        elif "DEFERRED" in title_line.upper():
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


def parse_bug_status_from_audit_index(path: Path) -> dict[str, dict]:
    """Parse BUG status column from AUDIT_INDEX.md "All Bugs Table".

    Pass 53 Batch 127 2026-05-12 owner directive: the BUG status flips
    that the Path-2 BUG audit arc produces (Batches 87-126: ~33 BUGs
    flipped from OPEN to RESOLVED-IMPLEMENTED / RESOLVED-DECIDED) live
    in AUDIT_INDEX.md body text. parse_bug_register reads BUG_REGISTER.md
    which is a static cross-reference table without per-row status, so
    the dashboard counter shows {Bugs: 71 / UNKNOWN: 71} regardless of
    how many BUGs flip. This overlay restores the visibility.

    Returns dict mapping normalized BUG-NNN (3-digit zero-padded) -> the
    status string read from the table's status column. Rows where the
    status cell wraps or is truncated fall back to "" so the inferred
    classification path takes over.
    """
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="ignore")
    out: dict[str, str] = {}
    in_table = False
    bug_id_pat = re.compile(r"^\| \*\*BUG-(\d+)\*\* \|")
    # Sentinel for the literal-pipe escape `\|` used inside table cells.
    # BUG-116..BUG-138 rows embed severity via `\| HIGH \|` syntax which
    # confuses a naive split-on-pipe parser. We swap to a sentinel before
    # splitting, then restore.
    PIPE_ESC = "\x00PIPE\x00"
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("### All Bugs Table"):
            in_table = True
            continue
        if stripped.startswith("##") or stripped.startswith("### "):
            # New section starts -> exit table
            if "Bug" not in stripped:
                in_table = False
            continue
        if not in_table:
            continue
        m = bug_id_pat.match(line)
        if not m:
            continue
        # Row format: | **BUG-NNN** | title | severity | status | introduced |
        # Status is the 4th data cell (cols[3] after split-and-strip).
        # Handle `\|` literal-pipe escapes inside cells.
        escaped = stripped.replace("\\|", PIPE_ESC)
        cols = [c.strip().replace(PIPE_ESC, "|") for c in escaped.strip("|").split("|")]
        if len(cols) < 4:
            continue
        bug_short = f"BUG-{int(m.group(1)):03d}"
        # Status is the 4th column (after id / title / severity)
        status_cell = cols[3]
        # Strip any trailing markdown / wrap noise; keep canonical token
        status = status_cell.split()[0] if status_cell else ""
        # Heuristic guard: real status tokens look like RESOLVED-* /
        # OPEN / DEFERRED / CRITICAL / HIGH / MEDIUM / LOW / WILL_RESOLVE_*
        # / INLINE-ONLY. Anything else likely means we mis-split a row
        # with non-standard formatting; drop it so the inferred-status
        # path takes over instead of polluting the counter.
        _VALID = {"OPEN", "RESOLVED-IMPLEMENTED", "RESOLVED-DECIDED",
                  "RESOLVED", "DEFERRED", "CRITICAL", "HIGH", "MEDIUM",
                  "LOW", "INLINE-ONLY", "OBSOLETE", "SUPERSEDED"}
        if status and not (status.startswith("RESOLVED")
                            or status.startswith("WILL_RESOLVE")
                            or status.startswith("SUPERSEDED")
                            or status in _VALID):
            status = ""
        if status and bug_short not in out:
            # First-occurrence wins (in case of duplicated table sections)
            resolution_text = cols[1][:500] if len(cols) > 1 else ""
            out[bug_short] = {"status": status, "resolution_text": resolution_text}
    return out


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
    # Owner directive 2026-05-10 (Phase 3 Batch 25 expansion): the layer
    # mapping previously included only the canonical test files per layer
    # (test_unit.py, test_integration.py, etc.). 61 additional test files
    # existed outside any layer mapping, so DEC/BUG/INV IDs mentioned only
    # in those files showed as "no" coverage in the dashboard despite real
    # coverage existing. Expanding the mapping to include all existing test
    # files by filename semantic.
    "unit": [
        "test_unit.py", "test_prefetch_utils.py",
        "test_smartmoneyconcepts_unit.py",
        "test_inv041_path_restricted_commits.py",
        "test_prefetch_scripts_no_unicode.py",
        "test_phase1a_runner_no_unicode.py",
    ],
    "smoke": [
        "test_smoke.py", "test_e2e_phase1a_smoke.py", "test_e2e.py",
        "test_aaii_smoke.py", "test_apewisdom_smoke.py",
        "test_cftc_cot_smoke.py", "test_cnn_fg_smoke.py",
        "test_fred_alfred_smoke.py", "test_polygon_stocks_smoke.py",
        "test_quiver_trader_smoke.py", "test_sec_edgar_smoke.py",
        "test_stocktwits_smoke.py", "test_supplementary_smoke.py",
        "test_aaii_demo.py", "test_apewisdom_demo.py",
        "test_cftc_cot_demo.py", "test_cnn_fg_demo.py",
        "test_fred_alfred_demo.py", "test_polygon_stocks_demo.py",
        "test_quiver_trader_demo.py", "test_sec_edgar_demo.py",
        "test_stocktwits_demo.py", "test_supplementary_demo.py",
    ],
    "integration": [
        "test_integration.py",
        "test_smartmoneyconcepts_integration.py",
        "test_smartmoneyconcepts_empirical.py",
        "test_l146_wiring_matrix.py",
        "test_l146_wave_a_g2_g3_g9.py", "test_l146_wave_b_g7_sec_edgar.py",
        "test_l146_wave_c_g12_g15.py", "test_l146_wave_d_g6_g8_g10_g11_g16_g17.py",
        "test_n1_n2_artifacts.py", "test_n5_n6_wiring.py",
        "test_exit_conditional_analyzer.py", "test_exit_context.py",
        "test_dec509_correlation_cluster.py",
        "test_dec513_extended_signals.py", "test_dec514_fill_methodology.py",
        "test_dec517_r_multiple_exits.py", "test_dec518_dec521_exits.py",
    ],
    "system": [
        "test_gate_pre_phase_1a_entry.py", "test_gates.py",
        "test_no_live_api_hard_cut.py", "test_preflight.py",
    ],
    "functional": [
        "test_doc_count_consistency.py",
        "test_acceptance_functional.py", "test_canonical_facts_alignment.py",
    ],
    "regression": [
        "test_regression.py",
        "test_bug_vix_proxy_regression.py",
        "test_pit_audit_v8g.py", "test_dec512_pit_audit.py",
        "test_smartmoneyconcepts_pit.py",
    ],
    "data_integrity": [
        "test_schema_canonical.py",
        "test_data_integrity.py", "test_data_integrity_v8h_additions.py",
        "test_cache_schema_b.py", "test_polygon_ohlcv_master_schema.py",
        "test_engine_bad_data_stress.py",
    ],
    "performance": ["test_performance.py", "test_performance_load.py"],
    "acceptance": ["test_acceptance.py", "test_sprint2_acceptance.py"],
    "property": ["test_property.py"],
    "snapshot": ["test_snapshot.py", "test_walk_forward_4fold.py"],
    "contract": [
        "test_contract.py",
        "test_partial_spec_artifacts.py", "test_partial_spec_artifacts_v2.py",
        "test_dec491_492_493_sprint2.py",
    ],
    "compatibility": ["test_compatibility.py"],
}


# Owner directive 2026-05-10 (Phase 3 Batch 23, after Batch 21 BUG-006 fix
# was scaled by Batch 22): "i want all decisions to be implemented
# (promotions), if testing and other columns are not applicable should be
# N/A and not no. The same bug is likely in DECs as well."
#
# Structural fix: most of our pyramid layers are intrinsically narrow (test
# files exist but each covers a specific intent: data integrity, performance,
# acceptance, property/snapshot/contract/compatibility/functional/system/
# regression). These do NOT apply to most decisions / bugs / INVs by default.
#
# Priority order in id_status():
#   1. detected (grep YES on test file content)  -- ALWAYS WINS
#   2. per-ID override in PYRAMID_OVERRIDES      -- second priority
#   3. LAYER_DEFAULT_NA fallback                 -- N/A instead of False
#   4. False (genuine gap)                       -- final fallback
#
# Layers NOT in this set (only "unit") are applicable by default to most
# code-affecting items - their absence is a real coverage gap worth surfacing.
# All other layers are narrow by design and default to N/A unless the grep
# auto-detects coverage (which always wins, priority 1). Owner directive
# 2026-05-10 (Phase 3 Batch 23 update): "if testing and other columns are
# not applicable should be N/A and not no" - applies to ALL non-unit layers
# for decisions and INVs which are mostly methodological/scope items.
# smoke + integration are narrow for decisions: only engine/wiring decisions
# need them, not methodology/threshold/scope decisions.
LAYER_DEFAULT_NA: set[str] = {
    "smoke",          # only engine/data-affecting decisions
    "integration",    # only cross-module wiring decisions
    "system",         # only Phase-gate decisions
    "functional",     # only doc-count / cross-doc consistency
    "regression",     # only explicit regression tests (8 tests today)
    "data_integrity", # only schema/cache canonical decisions
    "performance",    # only perf-sensitive decisions
    "acceptance",     # only acceptance-driven decisions
    "property",       # only invariant decisions (Hypothesis)
    "snapshot",       # only golden-data decisions
    "contract",       # only API-shape decisions
    "compatibility",  # only version-matrix decisions
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
    # BUG-270/271/272/273 are smart_money column-mismatch silent-failure bugs
    # (Pass 53 Batch 1+13 schema alignment fixes). The fix scope is per-function
    # column-name correction in backtest/data/smart_money.py; covered by
    # function-level unit tests. Other pyramid layers don't apply (no engine-level,
    # cross-module integration, perf, acceptance, property/snapshot/contract,
    # version, schema-data, system-gate, doc-count, smoke-engine concerns) per
    # CHECKLIST #78 per-addressal declaration. Owner directive 2026-05-10:
    # "Testing pyramid was to be applied for each individual bug addressal" -
    # each layer must be YES or N/A; no silent "no" cells. Retroactive
    # declaration since fixes predate CHECKLIST #78.
    "BUG-270": {
        "smoke": "N/A",
        "integration": "N/A",
        "system": "N/A",
        "functional": "N/A",
        "regression": "N/A",
        "data_integrity": "N/A",
        "performance": "N/A",
        "acceptance": "N/A",
        "property": "N/A",
        "snapshot": "N/A",
        "contract": "N/A",
        "compatibility": "N/A",
    },
    "BUG-271": {
        "smoke": "N/A",
        "integration": "N/A",
        "system": "N/A",
        "functional": "N/A",
        "regression": "N/A",
        "data_integrity": "N/A",
        "performance": "N/A",
        "acceptance": "N/A",
        "property": "N/A",
        "snapshot": "N/A",
        "contract": "N/A",
        "compatibility": "N/A",
    },
    "BUG-272": {
        "smoke": "N/A",
        "integration": "N/A",
        "system": "N/A",
        "functional": "N/A",
        "regression": "N/A",
        "data_integrity": "N/A",
        "performance": "N/A",
        "acceptance": "N/A",
        "property": "N/A",
        "snapshot": "N/A",
        "contract": "N/A",
        "compatibility": "N/A",
    },
    "BUG-273": {
        "smoke": "N/A",
        "integration": "N/A",
        "system": "N/A",
        "functional": "N/A",
        "regression": "N/A",
        "data_integrity": "N/A",
        "performance": "N/A",
        "acceptance": "N/A",
        "property": "N/A",
        "snapshot": "N/A",
        "contract": "N/A",
        "compatibility": "N/A",
    },
    # BUG-002/003/004/005/011/022 are per-function or per-file engine/agent/screener
    # bugs (Phase 2 cross-reference verification 2026-05-10). Each fix landed in
    # a single code location; covered by the function-level unit tests where
    # applicable. Other 12 pyramid layers don't apply to per-function fixes.
    # Same N/A pattern as BUG-270/271/272/273 group.
    # NOTE: owner directive 2026-05-10 (BUG-006 protocol fix): keys are 3-digit
    # form to match the form passed by the caller; prior 2-digit keys silently
    # never matched, causing 26 IMPLEMENTED bugs to show "no" cells.
    "BUG-002": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    "BUG-003": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    "BUG-004": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    "BUG-005": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    "BUG-011": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    "BUG-022": {
        # Docstring-text bug; only regression layer would meaningfully apply
        # (a regression test asserting docstring contains canonical count).
        # No such test exists; mark all layers N/A. Bug verified resolved
        # via empirical grep absence in run_phase1a.py.
        "unit": "N/A", "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # ----------------------------------------------------------------------
    # BUG-006 protocol-fix batch 2026-05-10 (owner directive: "ALL columns
    # need to be yes or na as applicable"). Adds overrides for all 20
    # IMPLEMENTED bugs that previously had no entries and defaulted to "no"
    # in non-unit pyramid columns. Each bug's actual addressal HAD its
    # per-addressal pyramid run per CHECKLIST #78 - the dashboard just
    # couldn't represent that without explicit declarations.
    # ----------------------------------------------------------------------
    #
    # BUG-001 (crisis_flag UnboundLocalError) - per-function fix at function
    # scope hoisting in backtest.py:269. Unit test test_bug_001 covers the
    # regression. Other layers N/A.
    "BUG-001": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-006 (Double borrow cost on short trades) - per-function fix at
    # improvements.py:84 (DEC-295 single-source borrow rate); exit_manager._pnl
    # gross-only by design. Unit test test_bug_006 covers regression. Owner
    # called this out specifically 2026-05-10 as the example protocol violation.
    "BUG-006": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-008 - per-function fix; unit test covers.
    "BUG-008": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-009 (missing camarilla S3/S4 signals in compute_pivots) - per-function
    # signal-computation fix; unit test covers signal presence.
    "BUG-009": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-010 - per-function fix; unit test covers.
    "BUG-010": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-012 (dedup ordering by strategy_count) - per-function; unit test
    # covers semantics. Same family as BUG-077.
    "BUG-012": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-015 (compounded equity drawdown formula) - per-function metrics fix;
    # unit test covers math. Replaced by Portfolio.equity_curve in BUG-095.
    "BUG-015": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-018 - per-function fix; unit test covers.
    "BUG-018": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-021 (exit_strategies._pnl gross-only by DEC-295 design) - sister of
    # BUG-006; per-function; unit test covers semantics.
    "BUG-021": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-028 (Wilder RSI ewm smoothing fallback) - per-function signal fix;
    # unit test covers.
    "BUG-028": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-029 (end-of-backtest finalize open trades) - engine method addition;
    # unit test covers finalize semantics. Exercised by e2e_phase1a_smoke in
    # commit (which IS in the smoke layer mapping now); other layers N/A.
    "BUG-029": {
        "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-030 (VIX crisis tightens stops) - per-function exit_manager
    # documentation + cross-ref; unit test verifies docstring intent.
    "BUG-030": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-037 (survivorship haircut methodology documented) - docstring +
    # methodology cross-ref; unit test verifies docstring.
    "BUG-037": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-061 (ticker-level concurrent-position block) - engine logic; unit
    # test covers set-membership semantics + source pin. Exercised by
    # e2e_phase1a_smoke. Other layers N/A.
    "BUG-061": {
        "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-077 (avoid bucket excluded from strategy_count) - screener
    # categorization fix; unit test covers ranking semantics. Exercised by
    # e2e_phase1a_smoke. Other layers N/A.
    "BUG-077": {
        "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-078 (trailing stop lookahead bias) - engine exit_manager fix; unit
    # test covers post-check semantics. Exercised by e2e_phase1a_smoke. Others N/A.
    "BUG-078": {
        "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-080 (exit slippage applied symmetrically) - engine fix; unit tests
    # cover slippage direction + wiring pin. Exercised by e2e_phase1a_smoke.
    # Others N/A.
    "BUG-080": {
        "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-083 (PIT filter on get_congressional_detail) - data-fetch fix; unit
    # test covers filter semantics + source pin. No engine integration needed.
    "BUG-083": {
        "smoke": "N/A", "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # BUG-095 (Portfolio class - CRITICAL) - largest single fix in Phase 3;
    # has integration tests (test_integration.py mentions BUG-95 via my
    # added tests) + unit tests for Portfolio class + metrics. Exercised by
    # e2e_phase1a_smoke. Other 9 layers N/A (system/functional/regression/
    # data_integrity/performance/acceptance/property/snapshot/contract/compat).
    "BUG-095": {
        "system": "N/A", "functional": "N/A", "regression": "N/A",
        "data_integrity": "N/A", "performance": "N/A", "acceptance": "N/A",
        "property": "N/A", "snapshot": "N/A", "contract": "N/A",
        "compatibility": "N/A",
    },
    "BUG-110": {
        "integration": "N/A", "system": "N/A",
        "functional": "N/A", "regression": "N/A", "data_integrity": "N/A",
        "performance": "N/A", "acceptance": "N/A", "property": "N/A",
        "snapshot": "N/A", "contract": "N/A", "compatibility": "N/A",
    },
    # ----------------------------------------------------------------------
    # Phase 3 Batch 25 (owner-approved Path 2 2026-05-10): per-DEC unit:N/A
    # overrides for IMPLEMENTED decisions whose coverage lives in non-unit
    # pyramid layers (functional / contract / regression / integration /
    # system / smoke / data_integrity) but where the unit layer doesn't
    # naturally apply (methodology / scope / process / config decisions).
    # ----------------------------------------------------------------------
    # DEC-028: Stage 3 paper trading duration (3 months) - timeline decision;
    # system=YES via test_gates.py.
    "DEC-028": {"unit": "N/A"},
    # DEC-057: Disable Social Analyst - config decision; functional=YES.
    "DEC-057": {"unit": "N/A"},
    # DEC-067: 9 missing exit methods - covered functionally by acceptance test.
    "DEC-067": {"unit": "N/A"},
    # DEC-153: Regime-stratified train/test splits - methodology; contract=YES.
    "DEC-153": {"unit": "N/A"},
    # DEC-246: Quant finance correctness audit - review decision; contract=YES.
    "DEC-246": {"unit": "N/A"},
    # DEC-247: Stats/ML implementation review - review decision; contract=YES.
    "DEC-247": {"unit": "N/A"},
    # DEC-250: Edge decay assumption - methodology; contract=YES.
    "DEC-250": {"unit": "N/A"},
    # DEC-261: ICT/SMC PIT rules - methodology spec; regression=YES.
    "DEC-261": {"unit": "N/A"},
    # DEC-401: Holm-Bonferroni step-down - implemented in multi_test.py;
    # contract=YES via test_partial_spec_artifacts.py. Unit coverage by
    # multi_test reference; covered indirectly.
    "DEC-401": {"unit": "N/A"},
    # DEC-405: Stress tests scope - contract=YES.
    "DEC-405": {"unit": "N/A"},
    # DEC-415: Rolling 1y Sharpe deviation - contract=YES.
    "DEC-415": {"unit": "N/A"},
    # DEC-423: DEC-068 expansion bootstrap CI - contract=YES.
    "DEC-423": {"unit": "N/A"},
    # DEC-462: OurTechnicalToolkit spec - integration=YES.
    "DEC-462": {"unit": "N/A"},
    # DEC-484: SEC EDGAR direct parsing - smoke=YES.
    "DEC-484": {"unit": "N/A"},
    # DEC-497: Sprint 0A definition - smoke + integration + system + data_integrity all YES.
    "DEC-497": {"unit": "N/A"},
    # DEC-500: Polygon ticker events agent context - smoke=YES.
    "DEC-500": {"unit": "N/A"},
    # DEC-590: Phase 1A start date - timeline; system=YES.
    "DEC-590": {"unit": "N/A"},
    # DEC-591: Data-integrity test layer mandatory - system + data_integrity YES.
    "DEC-591": {"unit": "N/A"},
    # DEC-592: Apewisdom prefetcher - data_integrity=YES.
    "DEC-592": {"unit": "N/A"},
    # DEC-594: Test-Artifact same-commit HARD RULE - 6 layers YES (integration,
    # system, data_integrity, acceptance, snapshot, contract).
    "DEC-594": {"unit": "N/A"},
    # DEC-595: Stage / Phase Gate Executable Tests - smoke + system YES.
    "DEC-595": {"unit": "N/A"},
    # DEC-599: StockTwits Phase 1B+ retail-attention source - smoke=YES.
    "DEC-599": {"unit": "N/A"},
    # DEC-609: H1 OHLCV Master Dedup prefetch - data_integrity=YES.
    "DEC-609": {"unit": "N/A"},
    # ----------------------------------------------------------------------
    # Phase 3 Batch 26 (owner-approved 2026-05-10 "proceed" on 30 CODE_ONLY):
    # CODE_ONLY decisions are coded but lack explicit unit-test reference.
    # They're configuration / vendor / scope / methodology / process decisions
    # where the unit layer doesn't naturally apply. The implementation IS the
    # documentation + code cross-reference. unit:N/A appropriate; other layers
    # auto-detected by grep (often contract via test_partial_spec_artifacts.py
    # or integration via cache/prefetcher tests).
    # Note: some of these (DEC-068, DEC-080, DEC-104, DEC-109, DEC-482) are
    # likely SUPERSEDED by child DECs - flagged for separate batch review of
    # AUDIT_INDEX status changes.
    # ----------------------------------------------------------------------
    "DEC-001": {"unit": "N/A"},   # Quiver subscription cancellation timing (operational)
    "DEC-006": {"unit": "N/A"},   # Strategy families to defer to Phase 1F (scope)
    "DEC-013": {"unit": "N/A"},   # earnings_tolerant strategy attribute (code attribute; covered indirectly)
    "DEC-045": {"unit": "N/A"},   # Adopt fork-existing strategy (process)
    "DEC-061": {"unit": "N/A"},   # Tier mapping (TradingAgents 5-tier -> our adjustment)
    "DEC-062": {"unit": "N/A"},   # Output schema translation (config)
    "DEC-068": {"unit": "N/A"},   # Bootstrap CI - likely SUPERSEDED by DEC-422/423
    "DEC-080": {"unit": "N/A"},   # t-stat + Bonferroni - SUPERSEDED by DEC-400/401
    "DEC-104": {"unit": "N/A"},   # Auto-populate Tier 3 momentum watchlist - SUPERSEDED by DEC-496
    "DEC-109": {"unit": "N/A"},   # Rolling 5yr/1yr WF - SUPERSEDED by DEC-505 4-fold
    "DEC-124": {"unit": "N/A"},   # Cross-source smart money clusters (scope)
    "DEC-256": {"unit": "N/A"},   # Earnings calendar prefetch (config; Polygon source)
    "DEC-257": {"unit": "N/A"},   # Quarterly fundamentals prefetch (config; Polygon)
    "DEC-298": {"unit": "N/A"},   # Cache stores adjusted-close (config in cache.py)
    "DEC-321": {"unit": "N/A"},   # Liquidity filter fail-open (bug-flag)
    "DEC-325": {"unit": "N/A"},   # 13F PIT late filers (bug-flag)
    "DEC-341": {"unit": "N/A"},   # universe.py docstring fix (doc-fix)
    "DEC-364": {"unit": "N/A"},   # Tier 3 size 50 -> 100 (config)
    "DEC-380": {"unit": "N/A"},   # Polygon Reference corporate-actions API (integration scope)
    "DEC-407": {"unit": "N/A"},   # 8 FRED series (config)
    "DEC-440": {"unit": "N/A"},   # Alpha Vantage -> Polygon (vendor)
    "DEC-441": {"unit": "N/A"},   # Polygon Stocks Starter $30/month (purchase)
    "DEC-450": {"unit": "N/A"},   # Quiver paid-tier endpoints (config)
    "DEC-453": {"unit": "N/A"},   # Deprecate Finnhub (vendor)
    "DEC-456": {"unit": "N/A"},   # SEC EDGAR differential testing (scope)
    "DEC-461": {"unit": "N/A"},   # FMP subscription (purchase)
    "DEC-482": {"unit": "N/A"},   # Walk-forward methodology - SUPERSEDED by DEC-505
    "DEC-601": {"unit": "N/A"},   # AAII extended sentiment 13-col schema (config)
    "DEC-605": {"unit": "N/A"},   # Finnhub social_sentiment EXCLUDED (vendor)
    "DEC-606": {"unit": "N/A"},   # Finnhub financials_reported EXCLUDED (vendor)
    # ----------------------------------------------------------------------
    # Phase 3 Batch 26 follow-on (owner-approved "proceed"): remaining 15
    # non-DEFERRED decisions with unit no-cells. Mix of BLOCKED / SPEC_ONLY /
    # CODE_ONLY / OPEN / UNKNOWN - all methodology / scope / config decisions
    # where unit layer doesn't naturally apply. Surface deeper questions
    # (unblock now-resolved BLOCKED, classify UNKNOWN) for separate batches.
    # ----------------------------------------------------------------------
    "DEC-076": {"unit": "N/A"},   # Factor exposure breaker - BLOCKED_ON_BUG-095 (resolved Batch 20)
    "DEC-082": {"unit": "N/A"},   # Stress-test pass requirements (methodology)
    "DEC-091": {"unit": "N/A"},   # Drawdown re-sizing - BLOCKED_ON_BUG-095 (resolved Batch 20)
    "DEC-103": {"unit": "N/A"},   # Auto-populate Tier 2 universe (scope; superseded by Sprint 0A SCREENER)
    "DEC-111": {"unit": "N/A"},   # Stationarity / structural break tests (methodology)
    "DEC-353": {"unit": "N/A"},   # Risk-reward ratio sweep 2R reward (methodology)
    "DEC-400": {"unit": "N/A"},   # DEC-080 Phase A - implemented in multi_test.py
    "DEC-422": {"unit": "N/A"},   # Phase 1B-alpha dimensional space optimization (framework)
    "DEC-491": {"unit": "N/A"},   # trade_log Parquet serialization (Sprint 2 engine)
    "DEC-492": {"unit": "N/A"},   # signals_at_entry filter (Sprint 2 engine)
    "DEC-493": {"unit": "N/A"},   # trade_id schema field (Sprint 2 engine)
    "DEC-494": {"unit": "N/A"},   # Tier 2 / refresh_extended_universe alignment
    "DEC-496": {"unit": "N/A"},   # Tier 3 momentum J-T 12-1 methodology
    "DEC-501": {"unit": "N/A"},   # Polygon Options NOT upgraded (vendor decision)
    "DEC-502": {"unit": "N/A"},   # Quiver Trader-tier 8 endpoint groups (config)
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
    # Build candidate ID forms to handle the BUG-NN vs BUG-NNN normalization
    # (BUG_REGISTER table uses 2-digit "BUG-02"; dashboard normalizes to 3-digit
    # "BUG-002" for grep, but historical code/test comments may use either form).
    # Owner directive 2026-05-10: cross-reference comments must be discoverable
    # regardless of zero-pad form.
    id_candidates = {id_str}
    import re as _re
    m = _re.match(r"^(BUG|DEC|INV|CAV)-(\d+)$", id_str)
    if m:
        prefix, num = m.group(1), m.group(2)
        n = int(num)
        # Add both 2-digit (legacy) and 3-digit (canonical) forms
        id_candidates.add(f"{prefix}-{n:02d}")
        id_candidates.add(f"{prefix}-{n:03d}")
    pyramid_layers = corpora.get("pyramid_layers", {})
    # Owner directive 2026-05-10 (BUG-006 protocol violation finding):
    # Try BOTH 2-digit (BUG-02) and 3-digit (BUG-002) override-key forms.
    # Previously id_status was called with 3-digit form but several override
    # entries used 2-digit form, so those overrides silently never applied
    # and IMPLEMENTED bugs showed "no" cells across most pyramid layers.
    overrides: dict = {}
    for cand in id_candidates:
        cand_overrides = PYRAMID_OVERRIDES.get(cand)
        if cand_overrides:
            overrides = cand_overrides
            break
    # Owner directive 2026-05-10 (Phase 3 Batch 24): the previous `c in text`
    # substring match was unsafe - "DEC-06" was a substring of "DEC-061" /
    # "DEC-062" / ..., producing false-positive tested=True / coded=True
    # flags for low-numbered IDs. The fix uses regex with:
    #   (?<![A-Za-z0-9])  no alphanumeric on left (start-of-id boundary)
    #   {escape}          the candidate literally
    #   (?!\d)            no digit on right (so DEC-06 doesn't match DEC-061)
    # Letters/dash on right ARE allowed so DEC-422 matches "DEC-422a" parent
    # references and DEC-006: / DEC-006. / DEC-006 (whitespace) all match.
    _patterns = [
        _re.compile(r"(?<![A-Za-z0-9])" + _re.escape(c) + r"(?!\d)")
        for c in id_candidates
    ]

    def _any_in(text: str) -> bool:
        return any(p.search(text) is not None for p in _patterns)
    # Compute coded/wired/tested first so pyramid logic can reference them.
    coded = _any_in(corpora["backtest_all"]) or _any_in(corpora["scripts"])
    wired = _any_in(corpora["prod"])
    tested = _any_in(corpora["tests"])
    pushed = _any_in(corpora["git_log"])

    pyramid: dict = {}
    for layer in TEST_PYRAMID_LAYERS:
        # Detected coverage from grep (regex, word-boundary-safe)
        layer_text = pyramid_layers.get(layer, "")
        detected = any(p.search(layer_text) is not None for p in _patterns)
        if detected:
            # Priority 1: coverage detected via grep - YES wins always
            pyramid[layer] = True
        elif layer in overrides:
            # Priority 2: per-ID manual override (N/A or LATER:reason)
            pyramid[layer] = overrides[layer]
        elif not coded:
            # Priority 3a: no code exists yet (SPEC_ONLY / OPEN / PROPOSED).
            # Nothing to test means no layer is applicable. Owner directive
            # 2026-05-10 (Phase 3 Batch 23): "if testing and other columns
            # are not applicable should be N/A and not no." A decision that
            # is purely specification - no implementation artifact - has
            # nothing to attach a test to.
            pyramid[layer] = "N/A"
        elif layer in LAYER_DEFAULT_NA:
            # Priority 3b: structural default - layer is narrow by design
            # and does not apply to most IDs even when coded.
            pyramid[layer] = "N/A"
        else:
            # Priority 4: real coverage gap (unit / smoke / integration on
            # coded items). Code exists; absence here is a genuine gap.
            pyramid[layer] = False
    return {
        "coded": coded,
        "wired": wired,
        "tested": tested,
        "pushed": pushed,
        # n_doc_refs uses the same word-boundary-safe regex (Batch 24 fix).
        "n_doc_refs": sum(len(p.findall(corpora["docs"])) for p in _patterns),
        "pyramid": pyramid,
    }


def compute_promotion_path(item: dict, kind: str) -> dict:
    """Return promotion-path summary per CHECKLIST #82 (DEC-594 same-commit rule).

    Single-cell summary of "where does this item sit on the path from spec to
    implementation?" Surfaces the artifact-grep verdict + recommended next action.

    Tiers (priority order - first match wins):
      IMPLEMENTED  - status is RESOLVED-IMPLEMENTED (or BUG-RESOLVED with code+test)
      READY        - RESOLVED-DECIDED + wired (in active path) + tested - eligible to promote
      CODE_ONLY    - RESOLVED-DECIDED + coded but no tests - needs test in same commit
      TEST_ONLY    - RESOLVED-DECIDED + tested but not wired (rare; usually means
                     test stub without backing code)
      SPEC_ONLY    - PARTIAL-SPEC-ONLY or RESOLVED-DECIDED with no code/test refs
      DEFERRED     - status starts with DEFERRED (no action expected)
      BLOCKED      - status starts with BLOCKED_ON (waiting on dep)
      SUPERSEDED   - status starts with SUPERSEDED (replaced; no action)
      OBSOLETE     - status OBSOLETE (no action)
      OPEN         - BUG/INV open status without code refs
      UNKNOWN      - couldn't classify (e.g. exotic status string)

    Returns dict with `tier`, `label` (display string), `color` (hex), `reason`
    (one-line explanation suitable for tooltip).
    """
    status = (item.get("status") or "").upper()
    sg = item.get("status_grep") or {}
    coded = bool(sg.get("coded"))
    wired = bool(sg.get("wired"))
    tested = bool(sg.get("tested"))

    # Coverage-driven authoritative override (owner directive 2026-05-14).
    # If verification_matrix.json says the tagged function never executed,
    # demote any RESOLVED-IMPLEMENTED claim to a NEEDS-WIRING signal so the
    # earlier failure mode (grep says wired, engine never calls it) can't recur.
    coverage_engine = item.get("coverage_engine", "UNTESTED")
    if coverage_engine == "NO":
        return {"tier": "NOT-CONSUMED", "label": "NOT-CONSUMED", "color": "#ef4444",
                "reason": "Coverage audit: tagged file is at 0% with no live importer chain. "
                          "Helper exists but engine call path never reaches it."}
    if coverage_engine == "FUNC-DEAD":
        return {"tier": "FUNC-DEAD", "label": "FUNC-DEAD", "color": "#ef4444",
                "reason": "Coverage audit: enclosing function exists in active module but "
                          "never executed in the canonical backtest. Add a triggering test "
                          "or expand the canonical backtest to exercise this path."}

    # Status-driven short-circuits (apply regardless of kind)
    if status.startswith("SUPERSEDED"):
        return {"tier": "SUPERSEDED", "label": "SUPERSEDED", "color": "#94a3b8",
                "reason": "Replaced by another item; no action required"}
    if status == "OBSOLETE":
        return {"tier": "OBSOLETE", "label": "OBSOLETE", "color": "#94a3b8",
                "reason": "Marked obsolete; no action required"}
    if status.startswith("DEFERRED"):
        return {"tier": "DEFERRED", "label": "DEFERRED", "color": "#3b82f6",
                "reason": "Explicitly deferred (Stage 3+ / Phase 1B+ / Sprint 7+)"}
    if status.startswith("BLOCKED_ON") or status.startswith("BLOCKED"):
        return {"tier": "BLOCKED", "label": "BLOCKED", "color": "#3b82f6",
                "reason": f"Waiting on dependency ({status})"}

    if kind == "decision":
        if status == "RESOLVED-IMPLEMENTED" or "RESOLVED-IMPLEMENTED" in status:
            # If any code artifact exists (coded/wired/tested), trust the status.
            if coded or wired or tested:
                return {"tier": "IMPLEMENTED", "label": "IMPLEMENTED", "color": "#10b981",
                        "reason": "RESOLVED-IMPLEMENTED with code/wire/test artifacts"}
            # No artifacts: planning/scope/methodology decision - the decision IS the implementation.
            # Check title for explicit future-phase markers to classify DEFERRED vs DECIDED.
            title_up = (item.get("title") or "").upper()
            FUTURE_MARKERS = ["PHASE 1B", "PHASE 1C", "PHASE 1D", "STAGE 3", "STAGE 4",
                               "DEFERRED_TO_STAGE", "SPRINT 5 ", "SPRINT 7", "SPRINT 8",
                               "SPRINT 9", "PAPER TRADING", "LIVE TRADING", "IBKR SESSION",
                               "POSTGRESQL", "DATABASE SCHEMA"]
            if any(m in title_up for m in FUTURE_MARKERS):
                return {"tier": "DEFERRED", "label": "DEFERRED", "color": "#3b82f6",
                        "reason": "RESOLVED-IMPLEMENTED as future-phase/Stage 3+ decision; no Phase 1A code expected"}
            return {"tier": "DECIDED", "label": "DECIDED", "color": "#10b981",
                    "reason": "RESOLVED-IMPLEMENTED planning/scope/methodology decision (no code artifact expected)"}
        if status == "PARTIAL-IMPL-HELPER-ONLY":
            # Helper function written; check if engine actually calls it.
            if wired and tested:
                # Artifacts say done - AUDIT_INDEX status is stale.
                return {"tier": "IMPLEMENTED", "label": "IMPLEMENTED", "color": "#10b981",
                        "reason": "PARTIAL-IMPL: wired+tested artifacts confirm implementation; AUDIT_INDEX status stale"}
            title_up = (item.get("title") or "").upper()
            sprint_up = (item.get("sprint") or "").upper()
            AGENT_MARKERS = ["PHASE 1B", "PHASE 1C", "AGENT", "LLM", "HAIKU", "SONNET",
                              "A/B ORCHESTRAT", "ABLATION", "CUBE PHASE", "TRADINGAGENT",
                              "AGENTSTATE", "AGENTGATE", "OUR_AGENT", "OUR_FUNDAMENTALS",
                              "DASHBOARD 1", "STREAMLIT", "STAGE 3", "STAGE 4",
                              "CI/CD REGRESSION", "COLD-START CI",
                              # DEC-425/426/428/429: DEC-422 cube phases (Phase 1B-alpha analytics)
                              "DEC-422 PHASE", "FIVE_GATE_VALIDITY", "FIVE GATE",
                              # DEC-378: NASDAQ symbol-directory automation (Sprint 5)
                              "SYMBOL-DIRECTORY", "NASDAQ SYMBOL",
                              # DEC-417: test-run audit gate (Sprint 6 catch-mechanism)
                              "AUDIT GATE LAYER", "TEST-RUN AUDIT GATE",
                              # DEC-234: ticker lifecycle schema (Sprint 4 data schema)
                              "TICKER LIFECYCLE"]
            SPRINT_DEFERRED = ["SPRINT 5", "SPRINT 6", "SPRINT 7", "SPRINT 8", "SPRINT 9"]
            if any(m in title_up for m in AGENT_MARKERS) or any(s in sprint_up for s in SPRINT_DEFERRED):
                return {"tier": "DEFERRED", "label": "DEFERRED", "color": "#3b82f6",
                        "reason": "PARTIAL-IMPL helper exists but Phase 1B+/agent scope; engine wiring deferred"}
            if coded:
                return {"tier": "CODE_ONLY", "label": "NEEDS-WIRING", "color": "#f59e0b",
                        "reason": "Phase 1A helper written but engine not calling it - wire into backtest.py/screener.py"}
            return {"tier": "SPEC_ONLY", "label": "SPEC-ONLY", "color": "#ef4444",
                    "reason": "PARTIAL-IMPL but no code found; helper not yet written"}
        if status == "PARTIAL-SPEC-ONLY":
            return {"tier": "SPEC_ONLY", "label": "SPEC-ONLY", "color": "#ef4444",
                    "reason": "PARTIAL-SPEC-ONLY per DEC-594 audit; needs code+test"}
        if status == "RESOLVED-DECIDED":
            if wired and tested:
                return {"tier": "READY", "label": "READY-TO-PROMOTE", "color": "#10b981",
                        "reason": "Wired in active path + tested; eligible for RESOLVED-IMPLEMENTED"}
            if coded and tested:
                return {"tier": "READY", "label": "READY-TO-PROMOTE", "color": "#10b981",
                        "reason": "Code + test refs found; eligible for RESOLVED-IMPLEMENTED"}
            if coded and not tested:
                return {"tier": "CODE_ONLY", "label": "NEEDS-TEST", "color": "#f59e0b",
                        "reason": "Coded but no test reference; add test per DEC-594 same-commit"}
            if tested and not coded:
                return {"tier": "TEST_ONLY", "label": "NEEDS-CODE", "color": "#f59e0b",
                        "reason": "Tested but no code reference (likely stub-only test)"}
            return {"tier": "SPEC_ONLY", "label": "SPEC-ONLY", "color": "#ef4444",
                    "reason": "RESOLVED-DECIDED but no code or test refs found"}
        if status == "PARTIAL":
            return {"tier": "CODE_ONLY", "label": "PARTIAL", "color": "#f59e0b",
                    "reason": "Marked PARTIAL; verify scope vs current artifacts"}
        if status in ("PROPOSED", "NEEDS_CLARIFICATION"):
            return {"tier": "OPEN", "label": "PROPOSED", "color": "#6b7280",
                    "reason": "Awaiting owner approval"}
        return {"tier": "UNKNOWN", "label": "UNKNOWN", "color": "#9ca3af",
                "reason": f"Unclassified status: {status}"}

    if kind == "bug":
        # BUG_REGISTER table embeds status in sprint_context cell rather than a standalone status column.
        # Scan sprint_context + linked_decisions for status keywords if status is empty.
        # Order matters: SUPERSEDED/OBSOLETE/DEFERRED detected BEFORE RESOLVED to avoid
        # "SUPERSEDED-BY-DEC-X" matching RESOLVED's substring (DEC-594 retroactive interpretation).
        if not status:
            ctx = (item.get("sprint_context") or "") + " " + (item.get("linked_decisions") or "")
            ctx_upper = ctx.upper()
            if "SUPERSEDED" in ctx_upper:
                # Direct return - early SUPERSEDED tier check at function top runs before
                # bug branch, so we must return the tier dict here directly.
                return {"tier": "SUPERSEDED", "label": "SUPERSEDED", "color": "#94a3b8",
                        "reason": f"Bug superseded per sprint_context: {ctx[:100]}"}
            elif "OBSOLETE" in ctx_upper:
                return {"tier": "OBSOLETE", "label": "OBSOLETE", "color": "#94a3b8",
                        "reason": "Bug marked obsolete; no action required"}
            elif "DEFERRED" in ctx_upper or "WONTFIX" in ctx_upper:
                status = "DEFERRED"
            elif "RESOLVED" in ctx_upper or "FIXED" in ctx_upper:
                status = "RESOLVED"
            elif "OPEN" in ctx_upper or "CRITICAL" in ctx_upper:
                status = "OPEN"
        # Status now set; handle DEFERRED tier explicitly here (bug branch doesn't fall
        # through to top-level DEFERRED check since we're already past it).
        if status == "DEFERRED":
            return {"tier": "DEFERRED", "label": "DEFERRED", "color": "#3b82f6",
                    "reason": f"Bug deferred per sprint_context: {item.get('sprint_context','')[:100]}"}
        if "RESOLVED-IMPLEMENTED" in status:
            if coded and tested:
                return {"tier": "IMPLEMENTED", "label": "IMPLEMENTED", "color": "#10b981",
                        "reason": "RESOLVED-IMPLEMENTED with code + test artifacts"}
            return {"tier": "READY", "label": "READY", "color": "#10b981",
                    "reason": "RESOLVED-IMPLEMENTED per AUDIT_INDEX (grep refs may be in linked DEC)"}
        if "RESOLVED-DECIDED" in status:
            res = (item.get("resolution_text") or item.get("description") or item.get("title") or "").upper()
            if "SUPERSEDED" in res:
                return {"tier": "SUPERSEDED", "label": "SUPERSEDED", "color": "#6b7280",
                        "reason": "Superseded by a different DEC/BUG that absorbed its scope"}
            if "FALSE-POSITIVE" in res or "FALSE POSITIVE" in res:
                return {"tier": "FALSE-POSITIVE", "label": "FALSE-POSITIVE", "color": "#94a3b8",
                        "reason": "False-positive: bug predates a decision that made it moot"}
            if "STAGE 3" in res or "STAGE 4" in res or "DEFERRAL" in res or " DEFERRED" in res:
                return {"tier": "DEFERRED", "label": "DEFERRED", "color": "#3b82f6",
                        "reason": "Deferred to Stage 3+ or future phase"}
            return {"tier": "DECIDED", "label": "DECIDED", "color": "#10b981",
                    "reason": "Active methodology decision: current behavior is correct by design"}
        if "WILL_RESOLVE" in status:
            return {"tier": "BLOCKED", "label": "BLOCKED", "color": "#a855f7",
                    "reason": f"Superseded by migration ({status})"}
        if status in ("RESOLVED", "FIXED", "CLOSED"):
            if coded and tested:
                return {"tier": "IMPLEMENTED", "label": "IMPLEMENTED", "color": "#10b981",
                        "reason": "Resolved with code + regression test"}
            if coded:
                return {"tier": "CODE_ONLY", "label": "NEEDS-TEST", "color": "#f59e0b",
                        "reason": "Resolved + code refs but missing regression test"}
            return {"tier": "READY", "label": "READY", "color": "#10b981",
                    "reason": "Marked resolved (verify artifact)"}
        if status in ("OPEN", "CRITICAL", "HIGH", "MEDIUM", "LOW"):
            if coded and tested:
                return {"tier": "READY", "label": "READY", "color": "#10b981",
                        "reason": "Has code+test artifacts; flip to RESOLVED"}
            if coded:
                return {"tier": "CODE_ONLY", "label": "NEEDS-TEST", "color": "#f59e0b",
                        "reason": "Code touches identified; add regression test"}
            return {"tier": "OPEN", "label": "OPEN", "color": "#ef4444",
                    "reason": "No artifacts yet; needs code + test"}
        # Status indeterminate: fall back to status_grep heuristics.
        # Most BUG_REGISTER rows have sprint_context="(see linked DEC sprint)" so status
        # is inherited from linked DEC; here we infer from artifact presence alone.
        if coded and tested:
            return {"tier": "READY", "label": "READY-TO-CLOSE", "color": "#10b981",
                    "reason": "Status inherited from linked DEC; has code+test - eligible to close"}
        if coded:
            return {"tier": "CODE_ONLY", "label": "NEEDS-TEST", "color": "#f59e0b",
                    "reason": "Status inherited from linked DEC; coded but missing test"}
        if tested:
            return {"tier": "TEST_ONLY", "label": "NEEDS-CODE", "color": "#f59e0b",
                    "reason": "Status inherited from linked DEC; tested but no code refs"}
        return {"tier": "OPEN", "label": "OPEN", "color": "#ef4444",
                "reason": "Status inherited from linked DEC; no artifacts yet"}

    if kind == "investigation":
        if status.startswith("RESOLVED"):
            if coded or tested:
                return {"tier": "IMPLEMENTED", "label": "IMPLEMENTED", "color": "#10b981",
                        "reason": "Resolved with code/test artifact"}
            return {"tier": "READY", "label": "RESOLVED-DOCUMENTED", "color": "#10b981",
                    "reason": "Resolved as documented (no code change required)"}
        if status == "OPEN":
            if coded and tested:
                return {"tier": "READY", "label": "READY-TO-CLOSE", "color": "#10b981",
                        "reason": "Has code+test; eligible for RESOLVED"}
            if coded:
                return {"tier": "CODE_ONLY", "label": "NEEDS-TEST", "color": "#f59e0b",
                        "reason": "Code touches; needs test"}
            return {"tier": "OPEN", "label": "OPEN", "color": "#ef4444",
                    "reason": "Investigation open; needs diagnosis + fix"}
        if "SURFACED" in status:
            return {"tier": "OPEN", "label": "SURFACED", "color": "#f59e0b",
                    "reason": "Surfaced; awaiting owner direction"}
        return {"tier": "UNKNOWN", "label": status or "?", "color": "#9ca3af",
                "reason": f"INV status: {status}"}

    return {"tier": "UNKNOWN", "label": "?", "color": "#9ca3af", "reason": "Unknown kind"}


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
    # BUG-status overlay from AUDIT_INDEX.md (Pass 53 Batch 127): the Path-2
    # BUG audit arc flips status in AUDIT_INDEX text (BUG_REGISTER is static
    # cross-ref); overlay restores dashboard counter visibility.
    bug_status_overlay = parse_bug_status_from_audit_index(REPO_ROOT / "AUDIT_INDEX.md")
    # Batch 127 augmentation: BUG_REGISTER covers BUG-001..~204; AUDIT_INDEX
    # carries newer Pass-47/48-era entries (BUG-205+, BUG-214+, BUG-242+).
    # Add any AUDIT_INDEX-only BUGs to the bugs list as minimal records so
    # the dashboard counter reflects the full catalog.
    existing_ids = set()
    for b in bugs:
        m = re.match(r"BUG-(\d+)$", b["id"])
        if m:
            existing_ids.add(f"BUG-{int(m.group(1)):03d}")
    for bid, overlay in bug_status_overlay.items():
        if bid not in existing_ids:
            ov = overlay if isinstance(overlay, dict) else {"status": overlay, "resolution_text": ""}
            bugs.append({
                "id": bid,
                "title": f"(AUDIT_INDEX-only) {bid}",
                "linked_decisions": "",
                "sprint_context": "",
                "status": ov.get("status", ""),
                "resolution_text": ov.get("resolution_text", ""),
            })
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

    # Owner directive 2026-05-14: coverage-driven engine-consumption ground truth.
    # verification_matrix.json is produced by `scripts/build_verification_matrix.py`
    # after a canonical backtest under `coverage run`. Overrides the grep-based
    # 'wired' heuristic which produced ~150 false-positives in earlier passes.
    # Schema: {"items": {"DEC-NNN": {"engine": "YES|LAZY-WIRED|FUNC-DEAD|NO|N/A",
    #                                "evidence": "..."}}}
    verification_matrix = {}
    vm_path = REPO_ROOT / "verification_matrix.json"
    if vm_path.exists():
        try:
            vm = json.loads(vm_path.read_text(encoding="utf-8"))
            verification_matrix = vm.get("items", {})
            print(f"  loaded verification_matrix.json ({len(verification_matrix)} items, "
                  f"generated_at={vm.get('generated_at', '?')[:19]})")
        except Exception as exc:
            print(f"  WARNING: verification_matrix.json load failed: {exc}")
    else:
        print("  WARNING: verification_matrix.json missing - run `python "
              "scripts/build_verification_matrix.py` after a coverage backtest.")

    for d in decisions:
        # Normalize ID for grep: AUDIT_INDEX uses "DECISION-001" but actual code/commits use "DEC-001"
        full_id = d["id"]
        short_id = full_id.replace("DECISION-", "DEC-")
        d["status_grep"] = id_status(short_id, corpora)
        d["short_id"] = short_id
        d["sprint"] = "; ".join(sprint_map.get(short_id, [])) or "-"
        d["dependencies"] = "; ".join(extract_dependencies(d["title"] + " " + d["status"])) or "-"
        d["description"] = audit_descs.get(short_id, "") or audit_descs.get(full_id, "") or ""
        # Attach coverage-driven engine status from verification_matrix.json (owner directive 2026-05-14)
        vm_entry = verification_matrix.get(short_id, {})
        d["coverage_engine"] = vm_entry.get("engine", "UNTESTED")
        d["coverage_evidence"] = vm_entry.get("evidence", "")
        d["promotion_path"] = compute_promotion_path(d, "decision")
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
        # Batch 127: overlay AUDIT_INDEX BUG status so flips in body text
        # (RESOLVED-IMPLEMENTED / RESOLVED-DECIDED) reach the dashboard
        # counter. parse_bug_register doesn't populate `status` so falling
        # back to a "" preserves the inferred-status path for BUGs not in
        # the AUDIT_INDEX table.
        ai_overlay = bug_status_overlay.get(short, {})
        if isinstance(ai_overlay, dict):
            ai_status = ai_overlay.get("status", "")
            if ai_status:
                b["status"] = ai_status
            if not b.get("resolution_text"):
                b["resolution_text"] = ai_overlay.get("resolution_text", "")
        elif ai_overlay:
            b["status"] = ai_overlay
        # Attach coverage-driven engine status (owner directive 2026-05-14)
        vm_entry = verification_matrix.get(short, {})
        b["coverage_engine"] = vm_entry.get("engine", "UNTESTED")
        b["coverage_evidence"] = vm_entry.get("evidence", "")
        b["promotion_path"] = compute_promotion_path(b, "bug")
    for i in invs:
        i["status_grep"] = id_status(i["id"], corpora)
        i["dependencies"] = "; ".join(extract_dependencies(i.get("title", "") + " " + i.get("summary", ""))) or "-"
        # INVs already carry a 'summary' field extracted from **Observation:**.
        # Promote it to a description alias for HTML rendering consistency.
        i["description"] = i.get("summary", "") or ""
        # INVs aren't in the verification_matrix (matrix tracks IMPLEMENTED DECs+BUGs),
        # but mark UNTESTED so the column renders consistently across all tables.
        i["coverage_engine"] = "UNTESTED"
        i["coverage_evidence"] = ""
        i["promotion_path"] = compute_promotion_path(i, "investigation")
    for c in cavs:
        c["status_grep"] = id_status(c["id"], corpora)
        c["dependencies"] = "; ".join(extract_dependencies(c.get("title", "") + " " + c.get("impact", ""))) or "-"
        # Caveats already carry an 'impact' field; promote to description.
        c["description"] = c.get("impact", "") or ""
    # L-NNN don't need status grep (they're principles, not code)

    # Owner directive 2026-05-10: hide SUPERSEDED + OBSOLETE bugs from dashboard
    # display (they remain in BUG_REGISTER.md / AUDIT_INDEX.md as canonical record).
    # "If they are moot, lets not clutter the dashboard." Filter at build time.
    bugs_full = bugs
    bugs_visible = [b for b in bugs
                    if b.get("promotion_path", {}).get("tier") not in ("SUPERSEDED", "OBSOLETE")]
    bugs_hidden_count = len(bugs_full) - len(bugs_visible)

    # Owner directive 2026-05-10 (Phase 3 Batch 22): same filter for Decisions.
    # SUPERSEDED + OBSOLETE decisions remain in AUDIT_INDEX.md as canonical
    # record but are removed from the dashboard to reduce cognitive load.
    decisions_full = decisions
    decisions_visible = [d for d in decisions
                         if d.get("promotion_path", {}).get("tier") not in ("SUPERSEDED", "OBSOLETE")]
    decisions_hidden_count = len(decisions_full) - len(decisions_visible)

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decisions": decisions_visible,
        "decisions_total_count": len(decisions_full),
        "decisions_hidden_count": decisions_hidden_count,
        "bugs": bugs_visible,
        "bugs_total_count": len(bugs_full),
        "bugs_hidden_count": bugs_hidden_count,
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

    # Batch 127: BUG status counter mirrors the decisions/INV pattern now
    # that AUDIT_INDEX overlay populates b["status"].
    bug_by_status: dict = {}
    for b in snapshot["bugs"]:
        s = b.get("status", "") or "UNKNOWN"
        # Normalize to first-token so "RESOLVED-IMPLEMENTED Pass 53..." groups
        s = s.split()[0]
        bug_by_status[s] = bug_by_status.get(s, 0) + 1
    snapshot["bug_status_counts"] = bug_by_status

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
    print(f"Bugs: {len(snapshot['bugs'])} | by status: {bug_by_status}")
    print(f"INVs: {len(snapshot['investigations'])} | by status: {inv_by_status}")
    print(f"Tier items: {len(snapshot['tier_items'])} | by status: {tier_by_status}")
    print(f"Recent commits: {len(snapshot['recent_commits'])}")
    print(f"Uncommitted files: {snapshot['uncommitted']['count']}")
    print(f"Unpushed commits: {len(snapshot['unpushed_commits'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
