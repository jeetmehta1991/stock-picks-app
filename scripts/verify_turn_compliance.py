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
            # a launch: long-running runner AND backgrounded.
            # B1603: read the EXECUTED command only. Previously this scanned the
            # whole tool-input blob, so WRITING a file that MENTIONS a launch -
            # a test fixture, a gate implementation, a doc example - tripped it.
            # Writing about a launch is not launching. Restricting to
            # Bash/PowerShell `command` keeps every real launch detected while
            # excluding Write payloads and prose.
            _cmd = ""
            if name in ("Bash", "PowerShell"):
                _cmd = str((c.get("input") or {}).get("command", ""))
            if _cmd and any(m in _cmd for m in LAUNCH_MARKERS[:2]) and (
                    "nohup" in _cmd or c.get("input", {}).get("run_in_background")):
                launches.append(_cmd[:140])
    return [] if (armed or not launches) else launches


# B1587 / CHECKLIST #195 -- an untested causal claim must not ship as a finding.
# L455: "probable cause is the i<250 warmup guard" was published as the
# explanation of a 4pct residual. It was WRONG (the fires sat at bars 799-1158)
# and one command disproved it. The rule is not "label hypotheses" - the skill
# already says that and it did not help. The rule is: if the test is available,
# RUN IT before publishing a cause.
CAUSE_PHRASES = (
    "probable cause", "likely cause", "likely because", "probably because",
    "i suspect", "suspect the", "my hypothesis", "hypothesis is",
    "most likely", "presumably", "it appears to be caused",
)
# Evidence that the claim was actually tested in the same turn.
PROOF_PHRASES = (
    "executed", "confirmed by", "verified by", "proven by", "measured",
    "i ran", "re-ran", "probe", "test shows", "disproved", "ruled out",
)


def scan_unverified_cause(entries):
    """Flag a turn that states a CAUSE without evidence of testing it.

    Windowed to the current turn (L449). Fires only when cause language appears
    with NO proof language anywhere in the same turn's assistant text -- the
    check is deliberately coarse, because the remedy (run the probe, or say
    "I don't know") is cheap and the failure (a wrong cause shipped as fact) is
    expensive.
    """
    entries = list(entries or [])
    last_user = -1
    for i, e in enumerate(entries):
        if (e or {}).get("type") != "user":
            continue
        content = ((e.get("message") or {}).get("content"))
        if isinstance(content, str) or (
                isinstance(content, list) and any(
                    isinstance(c, dict) and c.get("type") == "text"
                    for c in content)):
            last_user = i
    entries = entries[last_user + 1:] if last_user >= 0 else entries

    blob = []
    for e in entries:
        if (e or {}).get("type") != "assistant":
            continue
        content = ((e.get("message") or {}).get("content"))
        if isinstance(content, str):
            blob.append(content)
        elif isinstance(content, list):
            blob.extend(c.get("text", "") for c in content
                        if isinstance(c, dict) and c.get("type") == "text")
    low = " ".join(blob).lower()
    if not low:
        return []
    causes = [c for c in CAUSE_PHRASES if c in low]
    if not causes:
        return []
    if any(pp in low for pp in PROOF_PHRASES):
        return []
    return [("TURN-GATE BLOCK (CHECKLIST #195 / L455): this turn states a CAUSE "
             f"({sorted(set(causes))[:3]}) with no evidence it was TESTED. "
             "L455: a 'probable cause' shipped as the explanation of a 4pct "
             "residual was wrong, and one command disproved it. Either run the "
             "probe and cite it, or say plainly that the cause is UNKNOWN. A "
             "hypothesis presented as a finding is a fabrication.")]


# B1596 / CHECKLIST #197 -- a rule recorded ONLY in LEARNINGS is a story, not a
# gate. MEASURED this session: 24 L-entries state a generalised rule and 18 are
# referenced in NEITHER CHECKLIST nor the skill - a 75pct orphan rate. LEARNINGS
# is read when someone goes looking; CHECKLIST and the skill are read every turn.
# Every rule that HELD this session had a script behind it (#182, #185/#186,
# #187, #188, #189); the ones that decayed were prose.
# B1626: these three exact phrases WERE the gate. An L-entry stating a rule in
# any other wording was classified "narrative" and passed. MEASURED: L481-L484
# all state generalised rules, none contain one of these strings, and all four
# went unanchored across four consecutive turns while the gate reported clean.
# A gate that only fires when I use its vocabulary fires when I am ALREADY
# thinking in its terms - exactly when it is least needed.
#
# The default is now INVERTED: every new L-entry is treated as rule-bearing and
# must be anchored, unless it explicitly opts out. Opting out is a written
# decision, which is the point - the same fail-CLOSED move applied to my own
# gate that L482 was about.
RULE_MARKERS = ("generalised rule", "generalized rule", "**rule:**")
# An entry that genuinely records only a measurement or an event says so.
RECORD_ONLY_MARKERS = ("**record-of-fact**", "**no rule**", "(no rule)")


def scan_orphan_rule(learnings_text, checklist_text, skill_text, new_entries):
    import re
    """Flag L-entries added THIS TURN that state a rule but are anchored nowhere.

    A rule is ANCHORED when its L-number appears in CHECKLIST.md or the skill -
    which is what makes it consulted every turn rather than merely archived.
    """
    orphans = []
    for ln in new_entries or []:
        pat = "\n### " + re.escape(ln) + r"\b(.*?)(?=\n### L|\Z)"
        m = re.search(pat, learnings_text, re.S)
        if not m:
            continue
        body = m.group(1).lower()
        # B1626: fail CLOSED. Previously this skipped anything not containing
        # one of three exact phrases; now only an EXPLICIT opt-out skips.
        if any(k in body for k in RECORD_ONLY_MARKERS):
            continue                      # declared a pure record, not a rule
        if ln in checklist_text or ln in skill_text:
            continue                      # anchored
        orphans.append(ln)
    if not orphans:
        return []
    return [("TURN-GATE BLOCK (CHECKLIST #197 / L464): these L-entries state a "
             "GENERALISED RULE but are referenced in neither CHECKLIST nor the "
             "skill: " + str(orphans) + ". A rule recorded only in LEARNINGS is "
             "a story, not a gate - it gets rediscovered by repeating the "
             "failure that produced it. Add a CHECKLIST item (or cite an "
             "existing one) referencing the L-number, then end the turn again. "
             "If an entry genuinely records only a measurement or an event, "
             "mark it **record-of-fact** and it will be skipped - but that is a "
             "decision you are writing down, not a default (B1626).")]


def check_orphan_rule() -> str | None:
    """Block a turn whose new L-entries state a rule anchored nowhere (#191)."""
    try:
        import re
        import subprocess
        from pathlib import Path
        r = subprocess.run(["git", "diff", "HEAD", "--unified=0", "--", "LEARNINGS.md"],
                           capture_output=True, text=True, timeout=15)
        added = r.stdout or ""
        if not added.strip():
            r2 = subprocess.run(["git", "log", "-1", "-p", "--unified=0", "--", "LEARNINGS.md"],
                                capture_output=True, text=True, timeout=15)
            added = r2.stdout or ""
        new_entries = re.findall(r"^\+### (L\d+)", added, re.M)
        # B1633: this gate was PER-TURN only. An entry that slipped through on
        # an earlier turn was never looked at again, so orphans accumulated
        # silently - MEASURED 8 of 53 session entries still unanchored, four of
        # them (L477-L480) created after the gate existed. A check that only
        # ever sees the newest item has no memory of what it missed.
        # BACKLOG SWEEP: also re-examine the most recent entries regardless of
        # whether they changed this turn.
        try:
            _all = re.findall(r"^### (L\d+)", Path("LEARNINGS.md").read_text(
                encoding="utf-8", errors="ignore"), re.M)
            _recent = sorted(_all, key=lambda x: int(x[1:]))[-12:]
            new_entries = sorted(set(new_entries) | set(_recent),
                                 key=lambda x: int(x[1:]))
        except Exception:
            pass
        if not new_entries:
            return None
        L = Path("LEARNINGS.md").read_text(encoding="utf-8", errors="ignore")
        C = Path("CHECKLIST.md").read_text(encoding="utf-8", errors="ignore")
        S = Path(".claude/skills/execution-discipline/SKILL.md").read_text(
            encoding="utf-8", errors="ignore")
    except Exception:
        return None          # never let the gate itself break the turn
    bad = scan_orphan_rule(L, C, S, new_entries)
    return bad[0] if bad else None


# B1602 / CHECKLIST #196 -> AUTO-GATED. A fix can invalidate a conclusion the
# defect itself left intact: while the bug stood the numbers were
# self-consistent. L467 - the roster relabel was reverted by the very next
# regeneration because the fix belonged in the GENERATOR, not the output.
FIX_WORDS = ("fix:", "fixed", "bugfix", "defect", "root cause", "rca",
             "corrected", "correction")
# Artifacts whose conclusions are DOWNSTREAM of engine/grading behaviour.
DOWNSTREAM_ARTIFACTS = ("PHASE_1B_ROSTER.md", "PASSED_STRATEGY_EXIT_LIST.md",
                        "STRATEGY_OPTIMISATION_PLAN.md", "EXECUTION_QUEUE.md")


def scan_postfix_recheck(commit_msg, changed_files):
    """Flag a FIX commit that touched no downstream artifact and no queue entry.

    A fix with zero downstream footprint is either genuinely self-contained or
    an unrecorded invalidation. The gate cannot tell which - so it asks, and an
    EXECUTION_QUEUE entry saying "self-contained" satisfies it.
    """
    low = (commit_msg or "").lower()
    if not any(w in low for w in FIX_WORDS):
        return []
    touched = [f for f in (changed_files or [])
               if any(a in f for a in DOWNSTREAM_ARTIFACTS)]
    if touched:
        return []
    return [("TURN-GATE BLOCK (CHECKLIST #196 / L467): this turn commits a FIX "
             "but touched no downstream artifact and no queue entry. A fix can "
             "invalidate a conclusion the defect left intact - the roster "
             "relabel was reverted by the next regeneration because the fix "
             "belonged in the GENERATOR, not the output. GREP for shipped "
             "conclusions that depended on the old behaviour, MEASURE the "
             "overlap, and ticket each - or record 'self-contained' in "
             "EXECUTION_QUEUE and end the turn again.")]


# B1602 / CHECKLIST #193 -> AUTO-GATED. Launching a config against an
# unverified universe is the B1571 failure: two configs searched an abandoned
# A-C chunk for 3.3 h each before anyone looked at the ticker list.
def scan_unverified_universe(entries):
    """Flag a LAUNCH whose turn never ran verify_universe_artifact.py."""
    entries = list(entries or [])
    last_user = -1
    for i, e in enumerate(entries):
        if (e or {}).get("type") != "user":
            continue
        c = ((e.get("message") or {}).get("content"))
        if isinstance(c, str) or (isinstance(c, list) and any(
                isinstance(x, dict) and x.get("type") == "text" for x in c)):
            last_user = i
    entries = entries[last_user + 1:] if last_user >= 0 else entries

    # B1603: same discrimination as scan_unmonitored_launch - only an EXECUTED
    # Bash/PowerShell command counts. My first version scanned all tool input,
    # so the very test fixtures written FOR this gate tripped it.
    cmds, allblob = [], []
    for e in entries:
        content = ((e.get("message") or {}).get("content"))
        if isinstance(content, list):
            for c in content:
                if not isinstance(c, dict):
                    continue
                allblob.append(str(c.get("input", "")) + str(c.get("text", "")))
                if c.get("name") in ("Bash", "PowerShell"):
                    cmds.append(str((c.get("input") or {}).get("command", "")))
        elif isinstance(content, str):
            allblob.append(content)
    low = " ".join(cmds).lower()
    launched = ("run_phase1a.py" in low and
                ("nohup" in low or "--output-dir" in low))
    if not launched:
        return []
    if "verify_universe_artifact" in " ".join(allblob).lower():
        return []
    return [("TURN-GATE BLOCK (CHECKLIST #193 / L445): a config was LAUNCHED "
             "without running verify_universe_artifact.py in the same turn. "
             "Two configs once searched an abandoned A-C chunk for 3.3 h each "
             "because nobody looked at the ticker list. Run it against the "
             "baseline cube, then end the turn again.")]


def check_postfix_recheck() -> str | None:
    """#190 auto-gate: a FIX commit must show downstream re-check."""
    try:
        import subprocess
        m = subprocess.run(["git", "log", "-1", "--pretty=%B"],
                           capture_output=True, text=True, timeout=15).stdout
        f = subprocess.run(["git", "log", "-1", "--name-only", "--pretty=format:"],
                           capture_output=True, text=True, timeout=15).stdout
    except Exception:
        return None
    bad = scan_postfix_recheck(m, [x for x in (f or "").splitlines() if x.strip()])
    return bad[0] if bad else None


def check_unverified_universe() -> str | None:
    """#187 auto-gate: a launch requires a universe verification the same turn."""
    bad = scan_unverified_universe(_read_entries())
    return bad[0] if bad else None


# B1605 / CHECKLIST #201 -- an unmeasured QUANTITATIVE claim is as damaging as an
# untested cause, and #195 never covered it. "costs nothing - same runtime" was
# stated about a 3-year window against a 2-year baseline: it cost 50pct more
# (5.00 h vs 3.33 h per config, 50 h vs 33 h for the sweep). The arithmetic was
# one multiplication. The recurring shape is substituting a RATE for a TOTAL -
# same class as quoting a per-call ratio as a wall-clock saving (L432), a spot
# RAM reading as a ceiling, or a cold JIT timing as steady state.
QUANT_CLAIMS = (
    "costs nothing", "cost nothing", "same runtime", "no extra cost",
    "free", "negligible", "roughly the same", "about the same",
    "no additional", "without any cost", "at no cost",
)
QUANT_PROOF = (
    "executed", "measured", "computed", "i ran", "re-ran", "benchmark",
    "elapsed", "sim-day", "per config", "h/config", "derived from",
)


def scan_unmeasured_quantity(entries):
    """Flag a COST/QUANTITY claim with no evidence it was computed."""
    entries = list(entries or [])
    last_user = -1
    for i, e in enumerate(entries):
        if (e or {}).get("type") != "user":
            continue
        c = ((e.get("message") or {}).get("content"))
        if isinstance(c, str) or (isinstance(c, list) and any(
                isinstance(x, dict) and x.get("type") == "text" for x in c)):
            last_user = i
    entries = entries[last_user + 1:] if last_user >= 0 else entries

    blob = []
    for e in entries:
        if (e or {}).get("type") != "assistant":
            continue
        content = ((e.get("message") or {}).get("content"))
        if isinstance(content, str):
            blob.append(content)
        elif isinstance(content, list):
            blob.extend(c.get("text", "") for c in content
                        if isinstance(c, dict) and c.get("type") == "text")
    low = " ".join(blob).lower()
    if not low:
        return []
    hits = [q for q in QUANT_CLAIMS if q in low]
    if not hits:
        return []
    if any(pp in low for pp in QUANT_PROOF):
        return []
    return [("TURN-GATE BLOCK (CHECKLIST #201 / L470): this turn makes a COST or "
             f"QUANTITY claim ({sorted(set(hits))[:3]}) with no evidence it was "
             "COMPUTED. 'costs nothing - same runtime' was stated about a 3-year "
             "window against a 2-year baseline; it cost 50pct more, and the "
             "arithmetic was one multiplication. Do the multiplication and show "
             "it, or drop the claim.")]


def check_unmeasured_quantity() -> str | None:
    """#201 auto-gate: a cost/quantity claim must be computed, not asserted."""
    bad = scan_unmeasured_quantity(_read_entries())
    return bad[0] if bad else None


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
            # B1583: check the last SEVERAL commits, not just HEAD. A turn
            # routinely makes multiple commits; L452 landed in commit N-1 and
            # commit N (queue-only) then hid it from `git log -1`. Same shape as
            # L447 - I enumerated one legitimate end state and missed the rest.
            h = subprocess.run(
                ["git", "log", "-6", "--name-only", "--pretty=format:"],
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


# B1573 / CHECKLIST #194 -- an acknowledged miss must land in LEARNINGS the SAME
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
    return [("TURN-GATE BLOCK (CHECKLIST #194 / L446): this turn ACKNOWLEDGED a "
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
    # B1573 / CHECKLIST #194: an acknowledged miss must land in LEARNINGS the
    # SAME turn. Checked BEFORE the monitor gate so a turn that both admits a
    # miss and launches a run reports the miss first.
    cause_block = scan_unverified_cause(_read_entries())
    if cause_block:
        print(cause_block[0], file=sys.stderr)
        return 2

    quant_block = check_unmeasured_quantity()
    if quant_block:
        print(quant_block, file=sys.stderr)
        return 2

    universe_block = check_unverified_universe()
    if universe_block:
        print(universe_block, file=sys.stderr)
        return 2

    postfix_block = check_postfix_recheck()
    if postfix_block:
        print(postfix_block, file=sys.stderr)
        return 2

    orphan_block = check_orphan_rule()
    if orphan_block:
        print(orphan_block, file=sys.stderr)
        return 2

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
