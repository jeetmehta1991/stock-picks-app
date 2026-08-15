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


# B1545 / plan SS9 item 13 -- MONITOR-ARMED GATE.
# L420: I launched three long runs with no monitor AFTER writing the rule that
# forbids it. A rule applied only when remembered is not a control, so this
# reads the transcript and BLOCKS the turn when a long-running launch happened
# without an arming call in the SAME turn.
LAUNCH_MARKERS = (
    "run_phase1a.py",
    "universe_ladder_run.py",
    "nohup",
    "run_in_background",
)
ARM_MARKERS = ("CronCreate", "cron", "PushNotification", "Monitor")


def scan_unmonitored_launch(entries: list[dict]) -> list[str]:
    """Return launch snippets that had no monitor armed in the same turn.

    Pure for testability. A launch is any tool_use whose input mentions a
    long-running runner; an arm is any tool_use naming a scheduling or
    notification tool. Both are counted only AFTER the last real user message.
    """
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
    launches, armed = [], False
    for e in entries[last_user + 1:]:
        if e.get("type") != "assistant":
            continue
        content = (e.get("message") or {}).get("content") or []
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict) or c.get("type") != "tool_use":
                continue
            name = str(c.get("name", ""))
            blob = json.dumps(c.get("input", {}))
            if any(m in name for m in ARM_MARKERS) or any(
                    m in blob for m in ("CronCreate", "PushNotification")):
                # B1548 (L424): a monitor that EXISTS but reports exception-only
                # fails the owner's standing hourly directive while passing the
                # existence check. #185 caught absence; it did not catch cadence,
                # and I armed exception-only FOUR times. So the arming call must
                # ALSO promise an unconditional periodic report.
                _low = blob.lower()
                _periodic = ("every hour" in _low or "hourly" in _low
                             or "scheduled report" in _low)
                _unconditional = ("do not withhold" in _low
                                  or "unconditional" in _low
                                  or "silence is correct only" in _low
                                  or "silence is correct onlY".lower() in _low)
                if "CronCreate" in name or "CronCreate" in blob:
                    armed = _periodic and _unconditional
                else:
                    armed = armed or False
            # a launch: long-running runner AND backgrounded
            if any(m in blob for m in LAUNCH_MARKERS[:2]) and (
                    "nohup" in blob or c.get("input", {}).get("run_in_background")):
                launches.append(blob[:140])
    return [] if (armed or not launches) else launches


def check_unrecorded_miss() -> str | None:
    """Block a turn that ACKNOWLEDGED a miss without writing it to LEARNINGS."""
    try:
        import subprocess
        # B1574: "modified" must mean modified-OR-COMMITTED this turn. The
        # first version checked only the working tree, so writing the L-entry
        # and COMMITTING it - the behaviour the skill actually requires -
        # left the file clean and tripped this gate. A gate that punishes
        # compliance trains people to bypass it.
        r = subprocess.run(["git", "status", "--porcelain", "LEARNINGS.md"],
                           capture_output=True, text=True, timeout=15)
        touched = bool(r.stdout.strip())
        if not touched:
            h = subprocess.run(
                ["git", "log", "-1", "--name-only", "--pretty=format:"],
                capture_output=True, text=True, timeout=15)
            touched = "LEARNINGS.md" in (h.stdout or "")
    except Exception:
        # Never let the gate itself break the turn; fail OPEN and say so.
        return None
    bad = scan_unrecorded_miss(_read_entries(), touched)
    return bad[0] if bad else None


def check_monitor_armed() -> str | None:
    """Block a turn that launched a long run without arming its reporting path."""
    bad = scan_unmonitored_launch(_read_entries())
    if not bad:
        return None
    out = ["TURN-GATE BLOCK (CHECKLIST #185 / L420+L424): a long-running job was "
           "LAUNCHED without a monitor armed in the same turn AT THE OWNER'S "
           "CADENCE. The CronCreate prompt must promise a PERIODIC report "
           "('every hour' / 'hourly') AND state it is UNCONDITIONAL ('do not "
           "withhold' / 'silence is correct only when nothing is running'). "
           "Exception-only alerting does NOT satisfy this (armed 4x wrongly):"]
    out += [f"  ...{b}..." for b in bad[:2]]
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


# B1573 / CHECKLIST #188 -- an acknowledged miss must land in LEARNINGS the SAME
# turn. 12 misses were admitted in-response this session and never written down;
# the big ones got entries, the small recurring ones did not -- and recurrence,
# not severity, is what makes a miss expensive. Prose cannot enforce prose.
MISS_PHRASES = (
    "i was wrong", "i am wrong", "retract", "retraction",
    "my error", "my mistake", "my bug", "that was my",
    "i should have", "was misleading", "that result is misleading",
    "caught by preflight", "caught by the hook", "the hook is right",
    "correction:", "correcting my", "i nearly shipped", "i almost shipped",
)


def scan_unrecorded_miss(entries, learnings_modified: bool):
    """Return [reason] when a miss was acknowledged but LEARNINGS was not touched.

    Only ASSISTANT text is scanned -- the owner pointing out an error is not the
    trigger; ACKNOWLEDGING it is. Fires once per turn with the phrases found.
    """
    if learnings_modified:
        return []
    # B1577: window to THIS TURN only. The first version scanned the whole
    # transcript, so phrases from earlier turns ("caught by preflight",
    # "correction:") kept re-firing forever - a gate that fires on a turn with
    # no miss is the same defect L447 fixed, one layer up. The sibling scanners
    # already window on the last real user message; this now matches them.
    entries = list(entries or [])
    last_user = -1
    for i, e in enumerate(entries):
        if (e or {}).get("type") != "user":
            continue
        content = ((e.get("message") or {}).get("content"))
        if isinstance(content, str):
            last_user = i
        elif isinstance(content, list) and any(
                isinstance(c, dict) and c.get("type") == "text" for c in content):
            last_user = i
    entries = entries[last_user + 1:] if last_user >= 0 else entries

    hits = []
    for e in entries:
        if (e or {}).get("type") != "assistant":
            continue
        msg = (e.get("message") or {})
        content = msg.get("content")
        blob = ""
        if isinstance(content, str):
            blob = content
        elif isinstance(content, list):
            blob = " ".join(
                c.get("text", "") for c in content
                if isinstance(c, dict) and c.get("type") == "text")
        low = blob.lower()
        for ph in MISS_PHRASES:
            if ph in low:
                hits.append(ph)
    if not hits:
        return []
    uniq = sorted(set(hits))[:4]
    return [("TURN-GATE BLOCK (CHECKLIST #188 / L446): this turn ACKNOWLEDGED a "
             f"miss ({uniq}) but LEARNINGS.md was not modified. Severity is not "
             "the filter -- 12 unrecorded misses this session included the 5th "
             "instance of the monitor-cadence class. Add the L-entry (plus a new "
             "CHECKLIST item or an explicit 'compliance failure against item N') "
             "and end the turn again.")]


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
    # B1545: monitor-armed gate (L420 - third unmonitored launch).
    # B1573 / CHECKLIST #188: an acknowledged miss must land in LEARNINGS the
    # SAME turn. Checked BEFORE the monitor gate so a turn that both admits a
    # miss and launches a run reports the miss first.
    miss_block = check_unrecorded_miss()
    if miss_block:
        print(miss_block, file=sys.stderr)
        return 2

    monitor_block = check_monitor_armed()
    if monitor_block:
        print(monitor_block, file=sys.stderr)
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
