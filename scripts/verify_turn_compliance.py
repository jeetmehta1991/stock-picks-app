"""scripts/verify_turn_compliance.py - Stop-hook turn gate (Gate B).

# Source: per CHECKLIST #77 canonical-source; B1255 Council 300
# S6-B1253-GATE-B owner-approved 2026-07-08.

Runs when Claude tries to END a turn (configured in .claude/settings.json
hooks.Stop). Exit code 2 BLOCKS the turn from ending and feeds stderr back
to Claude so the omission is fixed in the same turn; exit 0 passes.

Checks (turn-level - catches what commit-level gates cannot: turns that
end without committing at all):
  T1: no MODIFIED TRACKED files left uncommitted (doc-sweep debt;
      CHECKLIST #67). Untracked files are ignored (scratch/output
      artifacts accumulate legitimately during long runs).
  T2: if tracked *.py files are modified-uncommitted, additionally remind
      that the pyramid stamp will be required (preflight C6 enforces at
      commit time; this is the early warning).

Escape hatch (auditable): create sentinel file `.stop_exempt` at repo
root - one-shot; this script consumes (deletes) it and passes, appending
to .queue_exempt_log. For turns that intentionally leave work in progress
(e.g., a long background run mid-flight).

Fast-pass: clean tree -> exit 0 silently (conversational turns cost
nothing).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# B1338 (Council 365, owner-approved): files that legitimately churn during
# LIVE RUNS (engine writes them as side effects). A turn whose only
# modifications are these must NOT block -- the pre-B1338 behavior forced
# dozens of manual .stop_exempt cycles (pure waste, B1334 retrospective).
# They still commit naturally with the next substantive doc-sweep.
LIVE_RUN_CHURN = {
    "STRATEGY_ROSTER.md",
    "backtest/data/economic_calendar.json",
    "data/cache/info_cache.json",
}


def split_churn(modified: list[str]) -> tuple[list[str], list[str]]:
    """Split porcelain lines into (substantive, churn) by path."""
    subst, churn = [], []
    for ln in modified:
        path = ln.split(maxsplit=1)[-1].strip().replace("\\", "/")
        (churn if path in LIVE_RUN_CHURN else subst).append(ln)
    return subst, churn


def scan_transcript_entries(entries: list[dict]) -> tuple[bool, bool]:
    """B1338 compliance-marker check (skill Phase 6 made mechanical).
    Returns (commit_made_this_turn, compliance_marker_present) scanning
    entries AFTER the last genuine user text message. Pure for testability."""
    last_user = -1
    for i, e in enumerate(entries):
        if e.get("type") != "user":
            continue
        content = (e.get("message") or {}).get("content")
        if isinstance(content, str) and content.strip():
            last_user = i
        elif isinstance(content, list) and any(
                isinstance(c, dict) and c.get("type") == "text" for c in content):
            last_user = i
    commit_made = marker = False
    for e in entries[last_user + 1:]:
        if e.get("type") != "assistant":
            continue
        content = (e.get("message") or {}).get("content") or []
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use":
                blob = json.dumps(c.get("input", {}))
                if "git commit" in blob:
                    commit_made = True
            elif c.get("type") == "text" and "CHECKLIST compliance" in (c.get("text") or ""):
                marker = True
    return commit_made, marker

_ENTRIES_CACHE: list | None = None


def _read_entries() -> list:
    """Parse the Stop-hook transcript ONCE. stdin is a single-read stream, so
    every gate must share this cache rather than re-reading it (B1504 defect:
    two gates each calling sys.stdin.read() -> the second always saw '')."""
    global _ENTRIES_CACHE
    if _ENTRIES_CACHE is not None:
        return _ENTRIES_CACHE
    _ENTRIES_CACHE = []
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return _ENTRIES_CACHE
    tpath = payload.get("transcript_path")
    if not tpath or not os.path.exists(tpath):
        return _ENTRIES_CACHE
    with open(tpath, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            try:
                _ENTRIES_CACHE.append(json.loads(line))
            except Exception:
                continue
    return _ENTRIES_CACHE


# B1504 / CHECKLIST #182 -- VERDICT DENOMINATOR GATE.
# Root cause (L363): the Truth Standard's evidence classes tag a claim's
# PROVENANCE, not its SCOPE. "20 combinations ran and 0 passed" and "the
# strategy cannot clear the bar" rest on IDENTICAL evidence and both tag
# EXECUTED, yet the second is false. Nothing required a verdict to carry its
# denominator, so a 2-of-6-producer investigation shipped as a verdict.
# This gate makes the denominator mechanically required in the sentence.
VERDICT_PATTERNS = [
    r"cannot\s+(?:clear|pass|reach|meet)",
    r"(?:does|do)\s+not\s+clear",
    r"\buntunable\b",
    r"nothing\s+to\s+(?:tighten|tune)",
    r"no\s+combination\s+(?:passes|clears|wins)",
    r"cannot\s+be\s+(?:rescued|salvaged|saved)",
    r"is\s+not\s+(?:viable|salvageable)",
]
# A denominator: "0 of 20", "2 of 6 producers", "13 of 41 strategies".
DENOMINATOR_RE = r"\b\d+\s+of\s+\d+\b"


def scan_verdict_denominators(entries: list[dict]) -> list[str]:
    """Return assistant text blocks stating a VERDICT with no denominator.

    Pure for testability. A block trips the gate when it uses verdict language
    about an object's capability but names no "N of M" scope anywhere in it.
    """
    import re as _re
    last_user = -1
    for i, e in enumerate(entries):
        if e.get("type") != "user":
            continue
        content = (e.get("message") or {}).get("content")
        if isinstance(content, str) and content.strip():
            last_user = i
        elif isinstance(content, list) and any(
                isinstance(c, dict) and c.get("type") == "text" for c in content):
            last_user = i
    offenders = []
    for e in entries[last_user + 1:]:
        if e.get("type") != "assistant":
            continue
        content = (e.get("message") or {}).get("content") or []
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict) or c.get("type") != "text":
                continue
            text = c.get("text") or ""
            if _re.search(DENOMINATOR_RE, text):
                continue  # scope is named -> compliant
            for pat in VERDICT_PATTERNS:
                m = _re.search(pat, text, _re.I)
                if m:
                    lo = max(0, m.start() - 60)
                    offenders.append(text[lo:m.end() + 60].replace(chr(10), " "))
                    break
    return offenders


def check_verdict_denominator() -> str | None:
    """Stop-hook wrapper: block a turn that states a verdict without its scope."""
    bad = scan_verdict_denominators(_read_entries())
    if not bad:
        return None
    out = ["TURN-GATE BLOCK (CHECKLIST #182, B1504): a VERDICT was stated "
           "without its denominator. Name the tested scope explicitly "
           "(e.g. '0 of 20 combinations across 2 of 6 producers'):"]
    out += [f"  ...{b}..." for b in bad[:3]]
    return chr(10).join(out)


def check_compliance_marker() -> str | None:
    """Read the shared transcript cache; if a git commit happened this turn
    but the final response has no CHECKLIST compliance statement, block."""
    commit_made, marker = scan_transcript_entries(_read_entries())
    if commit_made and not marker:
        return ("TURN-GATE BLOCK (Gate B v2, B1338): a git commit was made "
                "this turn but the final response has NO 'CHECKLIST "
                "compliance' statement (skill Phase 6 / CLAUDE.md "
                "mandatory end-of-response statement). Add the compliance "
                "statement and end the turn again.")
    return None
    return None


def get_modified_tracked() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        )
    except Exception:
        return []
    return [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]


def main() -> int:
    sentinel = REPO_ROOT / ".stop_exempt"
    if sentinel.exists():
        try:
            sentinel.unlink()
            with open(REPO_ROOT / ".queue_exempt_log", "a", encoding="utf-8") as fh:
                fh.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} .stop_exempt "
                         f"consumed (turn ended with work in progress)\n")
        except Exception:
            pass
        return 0

    # B1338: compliance-marker check runs regardless of tree state (a turn
    # can commit everything cleanly and still omit the mandated statement).
    marker_block = check_compliance_marker()
    # B1504 / CHECKLIST #182: runs regardless of tree state -- an over-scoped
    # verdict is a defect even when the turn commits nothing.
    verdict_block = check_verdict_denominator()
    if verdict_block:
        print(verdict_block, file=sys.stderr)
        return 2

    modified = get_modified_tracked()
    substantive, _churn = split_churn(modified)
    if marker_block and not substantive:
        print(marker_block, file=sys.stderr)
        return 2
    if not substantive:
        return 0  # fast-pass: clean tree or live-run churn only (B1338)
    modified = substantive

    py_mod = [m for m in modified if m.endswith(".py")]
    msg = [
        "TURN-GATE BLOCK (Gate B, B1255): modified tracked files are "
        "uncommitted - complete the CHECKLIST #67 doc-sweep + commit "
        "before ending the turn:",
    ]
    msg += [f"  {m}" for m in modified[:15]]
    if len(modified) > 15:
        msg.append(f"  ... +{len(modified) - 15} more")
    if py_mod:
        msg.append("  NOTE: .py changes present - full pyramid required "
                   "before commit (preflight C6).")
    msg.append("Intentional work-in-progress? create .stop_exempt "
               "(one-shot, logged) and end the turn again.")
    if marker_block:
        msg.append(marker_block)
    print("\n".join(msg), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
