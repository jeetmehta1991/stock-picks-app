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
    # B1713: allow an explicit transcript so these gates can be TESTED.
    # Every response-scanning gate here (#201, #215, verdict denominators, and
    # any future one) reads stdin, which only the Stop hook populates. Run any
    # other way they see zero entries and return "clean" unconditionally - which
    # is how the #225 gate called a nonexistent function and still looked green
    # (L501). A gate that cannot be observed failing has not been tested.
    # CLI/env override, never used by the Stop hook itself:
    tpath = os.environ.get("TURN_GATE_TRANSCRIPT")
    if tpath and os.path.exists(tpath):
        with open(tpath, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                try:
                    _ENTRIES_CACHE.append(json.loads(line))
                except Exception:
                    continue
        return _ENTRIES_CACHE
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
    # B1738: strip BACKTICK-QUOTED spans before matching. A response that
    # DESCRIBES a gate by listing its trigger vocabulary was firing the gate -
    # this one blocked a turn whose only "costs nothing" was inside a list of
    # the new gate's own trigger words. Second instance of the class (the
    # skills-block gate tripped on its own name), so the fix is a shared
    # convention: vocabulary shown in backticks is a MENTION, not a USE.
    import re as _re
    low = _re.sub(r"`[^`]*`", " ", low)
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


# B1635 / S6-B1634c / CHECKLIST #215 -- the NARROW, honest version of
# "verify against code, not docs". A gate cannot read whether a claim came from
# code. It CAN check that a turn asserting something is WIRED / ABSENT /
# IMPLEMENTED actually opened a file this turn. The skill states code-
# verification in 4 places and gated it in none, which is how "wired" survived
# as a grep result ~150 times.
STRUCTURAL_CLAIMS = (
    "is wired", "not wired", "is implemented", "not implemented",
    "does not exist", "never called", "is absent", "is present in",
    "exists at", "is unreachable", "is dead code", "engine-implemented",
    "grader-only", "hardcoded",
)
# Any of these in the turn means a file was actually opened or run.
INSPECTION_TOOLS = ("Read", "Grep", "Bash", "PowerShell", "Glob")


def scan_unverified_structure(entries):
    """Flag a STRUCTURAL claim made in a turn that never opened a file."""
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

    text, used_tools = [], set()
    for e in entries:
        content = ((e.get("message") or {}).get("content"))
        if isinstance(content, str):
            text.append(content)
        elif isinstance(content, list):
            for c in content:
                if not isinstance(c, dict):
                    continue
                if c.get("type") == "text":
                    text.append(c.get("text", ""))
                elif c.get("type") == "tool_use":
                    used_tools.add(str(c.get("name", "")))
    low = " ".join(text).lower()
    if not low:
        return []
    hits = [k for k in STRUCTURAL_CLAIMS if k in low]
    if not hits:
        return []
    if used_tools & set(INSPECTION_TOOLS):
        return []
    return [("TURN-GATE BLOCK (CHECKLIST #215 / L489): this turn asserts "
             f"something about CODE STRUCTURE ({sorted(set(hits))[:3]}) without "
             "having opened a single file. `wired` as a grep result produced "
             "~150 false RESOLVED claims; `regime_flip` read a key nothing "
             "wrote for its entire life. Read or run the thing, or say "
             "UNVERIFIED.")]


def check_unverified_structure() -> str | None:
    """#215 auto-gate: a claim about code structure needs a file opened."""
    bad = scan_unverified_structure(_read_entries())
    return bad[0] if bad else None


def check_describing_artifact_drift() -> str | None:
    """#221 auto-gate: a record that describes code must AGREE with that code.

    B1692. Three times in one session a hand-maintained record disagreed with
    the code it describes - the variant table's `tail_n` band (denying the
    existence of the level that won both wave-1 top-10s), its
    `engine_implemented` flags, and the manifest's grid enumeration. Each time
    the class was named in prose and the INSTANCE was fixed, which the
    GENERALIZATION MANDATE explicitly calls non-compliant.

    Prose did not hold it. This runs the verifier every turn instead.
    """
    import subprocess
    try:
        r = subprocess.run([sys.executable, "scripts/verify_describing_artifacts.py",
                            "--quiet"], capture_output=True, text=True, timeout=180)
    except Exception as exc:
        return f"describing-artifact verifier could not run ({exc!r}) - fail CLOSED"
    if r.returncode == 0:
        return None
    tail = (r.stdout or r.stderr or "").strip().splitlines()
    return ("a hand-maintained record disagrees with the code it describes "
            "(#221 / L495): " + " | ".join(tail[-4:]))


def check_postconfig_complete() -> str | None:
    """#223 auto-gate: a finished cube owes a COMPLETE post-config ledger.

    B1699 built this and B1701 turned it on. Between those two the script
    existed, ran, returned the right exit code - and was invoked by NOTHING.
    An audit of every gate in `scripts/` found 12 of 16 in that state, so this
    was not an oversight but the house style (L499 / #224).
    """
    import subprocess
    try:
        r = subprocess.run([sys.executable, "scripts/verify_postconfig_complete.py",
                            "--quiet"], capture_output=True, text=True, timeout=120)
    except Exception as exc:
        return f"post-config ledger check could not run ({exc!r}) - fail CLOSED"
    if r.returncode == 0:
        return None
    tail = [l for l in (r.stdout or "").strip().splitlines() if ":" in l][-3:]
    return ("a finished cube owes post-config steps (#223 / L498): " + " | ".join(tail))


# ---------------------------------------------------------------------------
# B1720: the four remaining response-scanning gates, on ONE shared primitive.
#
# The first #225 attempt called `_entry_text`, which did not exist, over
# `_read_entries()`, which returned zero entries outside the Stop hook - so it
# returned clean and looked green (L501). The primitive is DEFINED here, once,
# and every gate below is exercised against a supplied transcript in
# test_b1720_* before being trusted (#226).
# ---------------------------------------------------------------------------
def _assistant_text(entries) -> str:
    """All assistant prose in this turn, lowercased. The thing the gates read."""
    out = []
    for d in entries or ():
        if not isinstance(d, dict) or d.get("type") != "assistant":
            continue
        for blk in (d.get("message") or {}).get("content") or ():
            if isinstance(blk, dict) and blk.get("type") == "text":
                out.append(blk.get("text") or "")
    return " ".join(out).lower()


def _queue_touched() -> bool:
    """EXECUTION_QUEUE.md modified in the tree OR committed in the last commit."""
    import subprocess
    try:
        d = subprocess.run(["git", "status", "--porcelain", "EXECUTION_QUEUE.md"],
                           capture_output=True, text=True, timeout=15).stdout.strip()
        c = subprocess.run(["git", "log", "-1", "--name-only", "--format="],
                           capture_output=True, text=True, timeout=15).stdout
    except Exception:
        return False                      # fail CLOSED: unknown is not "touched"
    return bool(d) or ("EXECUTION_QUEUE.md" in (c or ""))


REMEDIATION_MARKERS = ("not built", "not started", "not wired", "remediation:",
                       "the fix is", "is not enforced", "no mechanical",
                       "not yet built", "this is a bug", "is a defect",
                       "root cause", "p0 bug", "silently overrid")
# Completed-action claims about the WORKING TREE - verbs whose truth is checkable.
# B1748: STEM the verbs. The replay proved this list missed the very error it
# was built for - I wrote "Reverting." and the list held only "reverted", which
# is not a substring of "reverting". A marker list written from the PAST TENSE
# of a remembered incident will miss the gerund, the present, and the
# first-person-plural. Match stems, not the one conjugation you happened to use.
NARRATION_STEMS = ("revert", "delete", "disable", "remove", "restore", "wire",
                   "roll back", "rolled back", "undid", "undo")
NARRATION_MARKERS = tuple(
    f"{v}{suf}" for v in NARRATION_STEMS
    for suf in ("ed", "ing", "s", "d", "")
) + ("i reverted", "now wired")
# B1720b: "the fix is" belongs to REMEDIATION (a fix NOT yet made);
# FIX_MARKERS must mean a fix SHIPPED, or the two gates collide.
FIX_MARKERS = ("i fixed", "fixed the", "patched the", "corrected the")
RECO_MARKERS = ("recommend", "recommendation:", "i'd recommend", "my recommendation")
OBJECTION_MARKERS = ("contrarian", "the case against", "what could make this wrong",
                     "objection", "argues against", "downside", "risk:")


def scan_response_gates(entries, *, queue_touched=None,
                        tree_changed=None, text=None) -> list[str]:
    """The four gates. Each returns a blocking reason or nothing.

    B1720b: `queue_touched` / `tree_changed` are INJECTABLE. Read from git when
    None, which is what the Stop hook does. The first version read git inside
    the function, so its verdict depended on ambient repo state and could not be
    proven to fire - the same untestability that let the #225 gate return clean
    over an empty stdin (L501). A check whose result depends on state you cannot
    supply cannot be shown to fail.
    """
    # B1748:  injectable so the replay harness can feed a recorded
    # response. Without it this gate could only ever be tested against a live
    # transcript - untestable in the same way stdin made the others untestable.
    t = (_assistant_text(entries) if text is None else text.lower())
    if not t:
        return []                         # nothing said -> nothing to check
    bad = []

    # #225: a turn that STATES a remediation or defect owes a queue entry.
    _qt = _queue_touched() if queue_touched is None else queue_touched
    hits = [m for m in REMEDIATION_MARKERS if m in t]
    if hits and not _qt:
        bad.append("#225: this turn states a remediation or defect "
                   f"({', '.join(sorted(set(hits))[:3])}) but EXECUTION_QUEUE.md was "
                   "neither modified nor committed. Findings arrive in prose and "
                   "prose leaves no mtime - which is how ten findings reached zero "
                   "tickets (L500).")

    # NARRATION (L501): claiming a tree change requires having made one.
    nh = [m for m in NARRATION_MARKERS if m in t]
    if nh:
        if tree_changed is None:
            import subprocess
            try:
                dirty = subprocess.run(["git", "status", "--porcelain"],
                                       capture_output=True, text=True,
                                       timeout=15).stdout.strip()
                last = subprocess.run(["git", "log", "-1", "--name-only",
                                       "--format="], capture_output=True,
                                      text=True, timeout=15).stdout
            except Exception:
                dirty, last = "", ""
            _tc = bool(dirty) or bool((last or "").strip())
        else:
            _tc = tree_changed
        if not _tc:
            bad.append(f"NARRATION (L501): this turn claims a completed action "
                       f"({', '.join(sorted(set(nh))[:3])}) but NOTHING changed in "
                       "the tree and nothing was committed. I once wrote "
                       "'Reverting.' and never ran the command - narrating an "
                       "action is not performing it.")

    # RETRO-SWEEP (#136 spirit): a turn that ships a FIX re-scans for siblings.
    if any(m in t for m in FIX_MARKERS) and "retroactive" not in t \
            and "same class" not in t and "siblings" not in t:
        bad.append("RETRO-SWEEP: this turn ships a fix but never states what ELSE "
                   "breaks the same way. The GENERALIZATION MANDATE calls a patch "
                   "leaving siblings of its class open non-compliant - name the "
                   "class and its other instances, or say the fix is one-off and "
                   "why.")

    # COUNCIL: a recommendation carries options AND a written objection.
    if any(m in t for m in RECO_MARKERS) and not any(m in t for m in OBJECTION_MARKERS):
        bad.append("COUNCIL: this turn makes a recommendation with no written "
                   "objection. The repo's own rule is that a council without a "
                   "Contrarian lens is not a council - write the case AGAINST, "
                   "even if it feels weak.")
    return bad


def check_response_gates() -> str | None:
    """#225 / narration / retro-sweep / council, in one pass."""
    bad = scan_response_gates(_read_entries())
    return bad[0] if bad else None


def _tool_text(entries) -> str:
    """Everything this turn actually RAN or READ - the inputs of every tool call.

    B1721: the four B1720 gates catch SYMPTOMS (a claim with no evidence, a
    finding with no ticket, a fix with no class sweep, a recommendation with no
    objection). None catches the CAUSE the owner named: compressing work into
    fewer tool calls - reading part of a file, answering from a module constant
    instead of its call site. That cause is checkable, because the transcript
    carries the tool calls: if a turn NAMES a constant it never grepped, it is
    reasoning from memory of the code rather than the code.
    """
    out = []
    for d in entries or ():
        if not isinstance(d, dict) or d.get("type") != "assistant":
            continue
        for blk in (d.get("message") or {}).get("content") or ():
            if isinstance(blk, dict) and blk.get("type") == "tool_use":
                out.append(json.dumps(blk.get("input") or {}))
    return " ".join(out)


def scan_uninspected_constant(entries, *, tool_text=None) -> list[str]:
    """#222 MECHANISED: naming a constant requires having looked at it.

    Fires when the prose cites an ALL-CAPS identifier or a CLI flag and no tool
    call this turn mentions it. `MIN_N=30` was quoted as "the floor" from the
    module definition while the caller passed 10 - one grep of the call site
    would have shown it, and the grep was the step that got compressed away.
    """
    import re
    # B1722: scope to THIS TURN. _read_entries parses the WHOLE transcript,
    # so the first live run scanned every constant named all session and
    # blocked on four it had legitimately inspected turns ago. Take only
    # entries after the last user message.
    # B1724: TOOL RESULTS are typed "user" in the transcript, so the first
    # version of this window ended at the last tool result and excluded EVERY
    # tool call in the turn - it then blocked on EXECUTION_QUEUE, which the turn
    # had in fact touched. A real user turn carries plain string content; a tool
    # result carries a list of tool_result blocks.
    def _is_real_user(d):
        if not isinstance(d, dict) or d.get("type") != "user":
            return False
        c = (d.get("message") or {}).get("content")
        if isinstance(c, str):
            return True
        return not any(isinstance(b, dict) and b.get("type") == "tool_result"
                       for b in (c or ()))

    last_user = max((i for i, d in enumerate(entries or ()) if _is_real_user(d)),
                    default=-1)
    entries = list(entries or ())[last_user + 1:]
    t = _assistant_text(entries)
    if not t:
        return []
    tt = (_tool_text(entries) if tool_text is None else tool_text).lower()
    raw = " ".join(_raw_assistant(entries))
    # Identifiers that look like code constants, and long-form CLI flags.
    # B1721b: this line shipped with LITERAL BACKSPACE characters where 
    # belonged - the escape was mangled at write time, so the pattern could
    # never match and the gate was silently inert. Exactly the class it was
    # built to catch, in its own source.
    names = set(re.findall(r"\b([A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+)\b", raw))
    # B1722: CLI-flag matching REMOVED. It matched markdown double-hyphens in
    # prose and produced pure noise on the first live turn
    # (--all-41-strategies-snapshot, --cluster-organization-policy). A gate
    # with false positives gets bypassed, and a bypassed gate is worse than
    # none. Constants only.
    # B1724: doc FILENAMES match the constant pattern (EXECUTION_QUEUE,
    # CHECKLIST, LEARNINGS, PROJECT_PLAN...). Naming a document is not the
    # failure this gate exists for - citing a CODE constant unread is.
    _DOC_NAMES = {"EXECUTION_QUEUE", "PROJECT_PLAN", "DETAILED_PROJECT_PLAN",
                  "CANONICAL_FACTS", "BUG_REGISTER", "AUDIT_INDEX",
                  "VERIFICATION_MATRIX", "STRATEGY_ROSTER", "MEMORY",
                  "OPEN_INVESTIGATIONS", "LIMITATIONS_CAVEATS"}
    names -= _DOC_NAMES
    missing = sorted(n for n in names if n.lower() not in tt)
    if not missing:
        return []
    return [f"#222 UNINSPECTED CONSTANT: this turn names {', '.join(missing[:4])} "
            "but no tool call touched it. Naming a constant is not reading it - "
            "MIN_N=30 was quoted as 'the floor' while the caller passed 10, and "
            "the grep that would have shown it was the step that got compressed "
            "away. Grep the identifier, or do not cite it."]


def _raw_assistant(entries) -> list:
    """Assistant prose with case PRESERVED - constants are case-bearing."""
    out = []
    for d in entries or ():
        if not isinstance(d, dict) or d.get("type") != "assistant":
            continue
        for blk in (d.get("message") or {}).get("content") or ():
            if isinstance(blk, dict) and blk.get("type") == "text":
                out.append(blk.get("text") or "")
    return out


def check_uninspected_constant() -> str | None:
    """#222 auto-gate: cite a constant only if you looked at it this turn."""
    bad = scan_uninspected_constant(_read_entries())
    return bad[0] if bad else None


SKILL_TRIGGERS = ("fable mode", "think like fable", "use the fable",
                  "work like fable", "council this", "council it",
                  "run the council", "convene the council", "llm council")


def _last_user_text(entries) -> str:
    """The most recent REAL user message, lowercased."""
    txt = ""
    for d in entries or ():
        if not isinstance(d, dict) or d.get("type") != "user":
            continue
        c = (d.get("message") or {}).get("content")
        if isinstance(c, str):
            txt = c
        elif isinstance(c, list) and not any(
                isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
            txt = " ".join(b.get("text", "") for b in c if isinstance(b, dict))
    return txt.lower()


def scan_skill_not_invoked(entries, *, user_text=None, tool_text=None) -> list[str]:
    """A skill TRIGGER in the user's message requires the Skill tool to run.

    B1725, owner catch: *"Is the fable mode and council skills not being invoked
    if prompted? I am not seeing anything in turn."* Correct - I had been WRITING
    "fable mode" and applying it from having read the file once, and had invoked
    `llm-council` exactly once and `fable-mode` never. Saying the name of a skill
    is not loading it, which is the same shape as naming a class and fixing an
    instance, or narrating an action instead of performing it.
    """
    u = _last_user_text(entries) if user_text is None else user_text.lower()
    hit = [t for t in SKILL_TRIGGERS if t in u]
    if not hit:
        return []
    tt = (_tool_text(entries) if tool_text is None else tool_text)
    if '"name": "Skill"' in tt or "'name': 'Skill'" in tt or "SKILL_INVOKED" in tt:
        return []
    return [f"SKILL NOT INVOKED: the request contains {hit[0]!r} but no Skill "
            "tool call ran this turn. Saying the name of a skill is not loading "
            "it - invoke it, or say plainly that you are applying it from memory "
            "and why that is sufficient."]


def scan_skill_not_updated(entries, *, learnings_touched=None,
                           skill_touched=None) -> list[str]:
    """A recorded miss owes the SKILL file, not just LEARNINGS and CHECKLIST.

    B1723 MEASURED: SKILL.md was touched 5 times (B1597-B1704) while LEARNINGS
    gained 57 entries (L446-L503). The file actually READ at the start of every
    turn is the one least often updated - so lessons accumulate where they are
    not loaded. Owner asked for "learnings, checklist and skill" and got two.
    """
    import subprocess

    def _touched(path):
        try:
            d = subprocess.run(["git", "status", "--porcelain", path],
                               capture_output=True, text=True, timeout=15).stdout
            c = subprocess.run(["git", "log", "-1", "--name-only", "--format="],
                               capture_output=True, text=True, timeout=15).stdout
        except Exception:
            return False
        return bool(d.strip()) or (path.split("/")[-1] in (c or ""))

    lt = _touched("LEARNINGS.md") if learnings_touched is None else learnings_touched
    if not lt:
        return []
    st = (_touched(".claude/skills/execution-discipline/SKILL.md")
          if skill_touched is None else skill_touched)
    if st:
        return []
    return ["SKILL NOT UPDATED: this turn records a LEARNINGS entry but leaves "
            "SKILL.md untouched. MEASURED B1723: the skill was edited 5 times "
            "while LEARNINGS gained 57 entries - lessons accumulate in the file "
            "that is NOT loaded each turn. Add the rule to the skill, or state "
            "why the lesson is incident-specific and belongs only in LEARNINGS."]


# B1730: per-skill trigger map. The B1725 gate accepted ANY Skill call, so
# invoking execution-discipline + fable-mode masked skipping llm-council when
# "Council this" was in the message. Each triggered skill now needs ITS OWN
# invocation, and the confirmation block must name ALL THREE with a status.
SKILL_TRIGGER_MAP = {
    "fable-mode": ("fable mode", "think like fable", "use the fable",
                   "work like fable", "slow down and do this right",
                   "think this through first"),
    "llm-council": ("council this", "council it", "run the council",
                    "convene the council", "llm council",
                    "get me five perspectives"),
    "execution-discipline": ("execution discipline", "execution-discipline"),
}
ALL_SKILLS = tuple(SKILL_TRIGGER_MAP)


def scan_skill_not_invoked_per_skill(entries, *, user_text=None,
                                     tool_text=None) -> list[str]:
    """EACH triggered skill requires ITS OWN invocation."""
    u = _last_user_text(entries) if user_text is None else user_text.lower()
    tt = (_tool_text(entries) if tool_text is None else tool_text).lower()
    missing = [name for name, trigs in SKILL_TRIGGER_MAP.items()
               if any(t in u for t in trigs) and name not in tt]
    if not missing:
        return []
    return [f"SKILL NOT INVOKED (per-skill): {', '.join(missing)} "
            "triggered by the request but never invoked. Invoking a DIFFERENT "
            "skill does not satisfy a trigger - that is how llm-council was "
            "skipped while two others ran (S6-B1729c)."]


def scan_skill_block_incomplete(entries, *, text=None) -> list[str]:
    """The confirmation block must name ALL THREE skills, each with a status."""
    t = (_assistant_text(entries) if text is None else text.lower())
    if not t or "skills invoked" not in t:
        return []                       # absence handled by the other gate
    # B1732: split on the FIRST occurrence read only 900 chars after it, so any
    # EARLIER mention of the phrase - including this gate describing itself -
    # shifted the window off the real block and fired a false positive on a
    # response that named all three. Use the LAST occurrence: the confirmation
    # block is by definition at the end of the turn.
    tail = t.rsplit("skills invoked", 1)[1][:900]
    absent = [n for n in ALL_SKILLS if n not in tail]
    if not absent:
        return []
    return [f"SKILLS-INVOKED BLOCK INCOMPLETE: {', '.join(absent)} not named. "
            "Owner directive B1730: every turn lists ALL THREE skills with an "
            "explicit status - FULLY LOADED / TRIGGERED-NOT-INVOKED / "
            "NOT-TRIGGERED / ALWAYS-ON. Omitting one lets silence stand in for "
            "a status."]


def scan_missing_skill_confirmation(entries, *, text=None) -> list[str]:
    """EVERY turn ends with an explicit skills-invoked confirmation.

    B1726, owner standing directive: *"In each turn i want a confirmation in the
    end if the skills have been invoked."* Reporting invocation only when it
    happened lets silence mean either "not triggered" or "triggered and
    skipped" - which is precisely how fable-mode went un-invoked for the whole
    session while the words appeared in every response.

    The line must be present whether or not any skill ran. NONE is a valid and
    required answer.
    """
    t = (_assistant_text(entries) if text is None else text.lower())
    if not t:
        return []
    if 'skills invoked' in t:
        return []
    return ['MISSING SKILLS-INVOKED CONFIRMATION: every turn must end with an '
            'explicit "SKILLS INVOKED:" line naming each skill loaded this turn, '
            'or NONE. Owner standing directive B1726. Silence cannot distinguish '
            '"not triggered" from "triggered and skipped" - which is how '
            'fable-mode went un-invoked all session while its name appeared in '
            'every response.']


def scan_discipline_not_loaded(entries, *, tool_text=None,
                              substantive=None) -> list[str]:
    """A working turn must LOAD the full execution-discipline skill.

    B1728, owner directive: *"I want the full 632 lines loaded each turn!"*

    MEASURED: the UserPromptSubmit hook injects a 12-bullet summary; the full
    SKILL.md is 644 lines. Invoking the skill DOES deliver all 644 - what I had
    seen before was a copy truncated by COMPACTION, not a design limit. So the
    difference between 12 lines and 644 is entirely whether the Skill tool ran.

    The 632 unloaded lines are not filler. They hold #182 verdict-scope, the
    POST-FIX RE-CHECK rule, B1446 no-arbitrary-decisions, the 20-row tripwire
    table and the anchor-the-rule rule - every one of which this session
    violated while the 12-bullet summary sat in context saying otherwise.

    Substantive = the turn ran a tool that changes or inspects the repo. A pure
    acknowledgement does not owe a 644-line load.
    """
    # B1733 OWNER CORRECTION: the substantive carve-out is REMOVED. I wrote it,
    # then used it to justify skipping the load on an hourly-report turn - which
    # is exactly the choosing the owner said I do not get to do. "The full 644
    # lines skill has to be invoked every turn! No exception and you dont get to
    # choose when to invoke it!" The  parameter is retained ONLY so
    # the pin test can exercise both branches; it defaults to ALWAYS-REQUIRED.
    tt = (_tool_text(entries) if tool_text is None else tool_text)
    if substantive is False:
        return []
    # B1733b: fire only when the turn is OBSERVABLE. With zero entries the gate
    # has no visibility - which is not the same as the skill being absent, and
    # blocking on it made tg.main() unrunnable outside the Stop hook. This is
    # NOT the substantive carve-out returning: work TYPE no longer exempts
    # anything; only total absence of evidence does.
    if not entries and tool_text is None:
        return []
    if 'execution-discipline' in tt:
        return []
    return ['EXECUTION-DISCIPLINE NOT LOADED: this turn did substantive work '
            'with only the 12-bullet hook summary in context. The full skill is '
            '644 lines and invoking it delivers all of them. The 632 lines the '
            'summary omits hold #182 verdict-scope, the POST-FIX RE-CHECK rule, '
            'B1446 no-arbitrary-decisions and the tripwire table - all violated '
            'this session while the summary sat in context. Invoke '
            'Skill(execution-discipline).']


COST_WORDS = (' seconds', 'cheap', 'one command', 'trivial', 'offline on',
              'a minute', 'minutes, not', 'costs nothing', 'no re-run')
OPEN_EVIDENCE = ('file_path', 'grep', 'head ', 'cat ', 'read_csv', 'columns',
                 'sed -n', 'json.load')


def scan_uncosted_probe(entries, *, text=None, tool_text=None) -> list[str]:
    """CHECKLIST #230 EXT (B1736/L506) mechanised: cost + schema claims.

    B1737. #230 was extended in PROSE only - the owner asked whether a hook
    existed and the honest answer was no. Four instances in one session, the
    last two AFTER the rule was written, because a rule is learned from its
    examples and its examples were all about tools.

    Fires when the response ESTIMATES EFFORT ("seconds", "cheap", "one
    command", "offline on cached cubes") and NO tool call this turn opened
    anything. I specified a probe as "split by exit_reason - offline, seconds"
    against a grid JSON that has no exit_reason column and never opened it.
    """
    t = (_assistant_text(entries) if text is None else text.lower())
    if not t:
        return []
    hits = [w for w in COST_WORDS if w in t]
    if not hits:
        return []
    tt = (_tool_text(entries) if tool_text is None else tool_text).lower()
    if any(e in tt for e in OPEN_EVIDENCE):
        return []
    return [f'UNCOSTED PROBE (#230 EXT / L506): this turn estimates effort '
            f'({chr(34)}{hits[0].strip()}{chr(34)}) but NO tool call opened an artifact. '
            'An effort estimate is a quantitative claim, and a claim about what '
            'a file can support is a capability claim. OPEN the artifact and '
            'name the FIELD the work needs, or drop the estimate.']


def _queue_rows_added() -> int:
    """S6-xxx rows ADDED to the queue in the working tree + last commit."""
    import subprocess, re as _re
    n = 0
    for cmd in (["git", "diff", "--", "EXECUTION_QUEUE.md"],
                ["git", "diff", "HEAD~1", "HEAD", "--", "EXECUTION_QUEUE.md"]):
        try:
            d = subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout
        except Exception:
            continue
        n += len(_re.findall(r"^\+\| \*\*S6-", d, _re.M))
    return n


def scan_prose_only_rule(entries, *, docs_touched=None, code_touched=None,
                         text=None) -> list[str]:
    """B1739: a rule added to CHECKLIST/SKILL owes a gate, or an explicit reason.

    Owner: *"prose alone wont suffice. Gates and or other enforcement mechanisms
    need to be added to ensure that value is actually derived."*

    THREE consecutive times a rule shipped as prose and the owner had to ask
    before the mechanism existed - B1723 (skill dropped from a 3-artifact
    request), B1725 (skills documented, never invoked), B1736 (#230 extension
    with no hook). Writing the prose FEELS like closing the loop.
    """
    import subprocess
    def _touched(paths):
        try:
            d = subprocess.run(["git", "status", "--porcelain"] + paths,
                               capture_output=True, text=True, timeout=20).stdout
            c = subprocess.run(["git", "log", "-1", "--name-only", "--format="],
                               capture_output=True, text=True, timeout=20).stdout
        except Exception:
            return False
        return bool(d.strip()) or any(pp.split("/")[-1] in (c or "") for pp in paths)

    dt = _touched(["CHECKLIST.md", ".claude/skills/execution-discipline/SKILL.md"])         if docs_touched is None else docs_touched
    if not dt:
        return []
    ct = _touched(["scripts/verify_turn_compliance.py",
                   "backtest/tests/test_unit.py"]) if code_touched is None else code_touched
    if ct:
        return []
    t = (_assistant_text(entries) if text is None else text.lower())
    if "prose-only" in t:
        return []
    return ["PROSE-ONLY RULE WITH NO GATE (B1739): this turn edits CHECKLIST.md "
            "or SKILL.md without touching verify_turn_compliance.py or "
            "test_unit.py. A rule with no mechanism decays - three times running, "
            "the owner had to ask before the gate existed. Add the gate, or write "
            "PROSE-ONLY and say why a mechanism is not possible."]


def scan_findings_vs_tickets(entries, *, text=None, rows=None) -> list[str]:
    """B1739: EVERY finding owes a ticket, not just the first one.

    The #225 gate fires only when the queue is UNTOUCHED, so one ticket for one
    finding satisfies it while other findings in the same turn go unticketed -
    the same any-vs-each gap the per-skill gate had (S6-B1729c).
    """
    import re as _re
    # B1742: count only the FINAL assistant text block. The Stop hook re-runs
    # after every block, and the turn window spans all attempts - so a blocked
    # turn re-counted the markers of its own earlier tries and could never clear,
    # each retry inheriting the last. Only the response actually being evaluated
    # should be scanned.
    if text is None:
        blocks = _raw_assistant(entries)
        t = (blocks[-1] if blocks else "").lower()
    else:
        t = text.lower()
    if not t:
        return []
    t = _re.sub(r"`[^`]*`", " ", t)          # B1738 mention-vs-use
    # B1741: a finding NAMED ALONGSIDE ITS TICKET is ticketed. Drop any line
    # citing an S6-xxx id before counting - otherwise reporting on last turn work
    # re-counts findings that already have rows, which is what over-fired here.
    t = " ".join(l for l in t.splitlines() if "s6-b" not in l)
    MARKERS = ("not built", "not started", "not done", "unknown - rca",
               "is a defect", "this is a bug", "i am flagging", "needs a gate")
    found = len({m for m in MARKERS if m in t})
    if found == 0:
        return []
    n = _queue_rows_added() if rows is None else rows
    if n >= found:
        return []
    return [f"FINDINGS EXCEED TICKETS (B1739): {found} distinct finding markers in "
            f"the response, {n} S6-xxx rows added to the queue. The #225 gate only "
            "checks the queue was TOUCHED - one ticket satisfied it while the rest "
            "went unrecorded. Ticket each, or fold them into one row explicitly."]


def scan_false_skill_status(entries, *, text=None, injected=None) -> list[str]:
    """B1747: the SKILLS INVOKED line must match what was ACTUALLY injected.

    Owner caught this: since B1744 the hook delivers the FULL 732-line skill on
    every turn, and I kept reporting "ALWAYS-ON (12-bullet hook summary; full
    skill not invoked this turn)" - a stale template copied forward without
    re-checking what arrived.

    That is the session's root cause - reporting a state not observed - inside
    the very line meant to PROVE compliance. And B1726's confirmation gate
    checks the line EXISTS, not that it is TRUE, so it passed the false claim
    every turn. Existence gates cannot catch content lies; this one compares the
    claim against the observable injection.
    """
    t = (_assistant_text(entries) if text is None else text.lower())
    if not t or "skills invoked" not in t:
        return []
    if injected is None:
        u = _last_user_text(entries)
        injected = "full skill, auto-injected" in u
    if not injected:
        return []
    tail = t.split("skills invoked", 1)[1][:600]
    STALE = ("12-bullet", "12 bullet", "hook summary", "not invoked this turn",
             "always-on")
    hit = [m for m in STALE if m in tail]
    if not hit and "execution-discipline" in tail:
        return []
    if hit:
        return [f"FALSE SKILL STATUS (B1747): the injection this turn WAS the "
                f"full skill, but the SKILLS INVOKED block says "
                f"{hit[0]!r}. Reporting a state you did not observe - the "
                "session's root cause, inside the line meant to prove "
                "compliance. Report execution-discipline as FULLY LOADED "
                "(auto-injected)."]
    return []


# B1751: THE ANY-VS-EACH PRIMITIVE.
#
# Five instances of one class, each found and patched separately:
#   1. #225      fired only on an UNTOUCHED queue
#   2. per-skill satisfied by ANY Skill call
#   3. runner    18 early returns - FIRST violation ended the run
#   4. Phase 5   counted QUEUE rows only, so LEARNINGS/CHECKLIST went untouched
#   5. B1747     scan_false_skill_status DEFINED but never wired - I proved it
#                5/5 and reported it live; it has never run
#
# Each was fixed alone; the CLASS stayed open, so instance 6 was always
# available. A rule whose wording says "each" or "every" must never ask whether
# a CATEGORY was touched - it enumerates REQUIRED members, observes which are
# SATISFIED, and names the DIFFERENCE. `require_each` takes a dict so the caller
# is forced to list every member: a member cannot be silently omitted, which is
# how "any" creeps back.
def require_each(rule: str, required: dict, *, why: str = "") -> list[str]:
    """`required` maps MEMBER NAME -> bool satisfied. Reports missing by name."""
    missing = [k for k, ok in required.items() if not ok]
    if not missing:
        return []
    have = [k for k, ok in required.items() if ok]
    return [f"{rule}: {len(missing)} of {len(required)} required member(s) "
            f"NOT satisfied - {', '.join(missing)}"
            + (f" (satisfied: {', '.join(have)})" if have else "")
            + (f". {why}" if why else "")]


def _artifact_touched(*paths) -> bool:
    import subprocess
    try:
        d = subprocess.run(["git", "status", "--porcelain"] + list(paths),
                           capture_output=True, text=True, timeout=20).stdout
        c = subprocess.run(["git", "log", "-1", "--name-only", "--format="],
                           capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return False
    return bool(d.strip()) or any(pp.split("/")[-1] in (c or "") for pp in paths)


MISS_MARKERS = ("i was wrong", "my mistake", "that was a miss", "i missed",
                "owner caught", "i failed to", "correction:", "i should have",
                "this is a compliance failure")


def scan_miss_capture_complete(entries, *, text=None, observed=None) -> list[str]:
    """Phase 5 wants THREE artifacts on a miss, not one (B1751 / #234)."""
    t = (_assistant_text(entries) if text is None else text.lower())
    if not t or not any(m in t for m in MISS_MARKERS):
        return []
    if observed is None:
        observed = {
            "LEARNINGS.md entry": _artifact_touched("LEARNINGS.md"),
            "CHECKLIST.md item or explicit compliance-failure citation":
                _artifact_touched("CHECKLIST.md")
                or "compliance failure against" in t,
            "EXECUTION_QUEUE.md ticket": _artifact_touched("EXECUTION_QUEUE.md"),
        }
    return require_each(
        "PHASE-5 MISS-CAPTURE INCOMPLETE (B1751 / #234)", observed,
        why="Say 'compliance failure against item N' if no new checklist item "
            "is warranted.")


def check_skill_gates() -> str | None:
    """Skill invocation + the skill half of the miss-capture loop."""
    e = _read_entries()
    for bad in (scan_skill_not_invoked(e), scan_skill_not_updated(e),
                scan_missing_skill_confirmation(e),
                scan_discipline_not_loaded(e),
                scan_skill_not_invoked_per_skill(e),
                scan_skill_block_incomplete(e)):
        if bad:
            return bad[0]
    return None


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
    # B1746: RUN EVERY GATE, REPORT EVERY VIOLATION.
    #
    # Root cause of the missed fable-mode catch: main() had 18 early `return 2`
    # points, so the FIRST failing gate ended the run and every later gate was
    # skipped. Last turn check_compliance_marker returned first, so
    # check_skill_gates never executed and the un-invoked skill went unreported.
    #
    # That is the any-vs-each defect (CHECKLIST #231) at the RUNNER level: the
    # runner detected *a* violation instead of counting *all* of them. Same shape
    # as #225 firing only on an untouched queue, and as the per-skill gate that
    # any Skill call satisfied. A gate suite that stops at the first failure
    # trains you to fix one thing per turn and never see the rest.
    _v: list[str] = []
    for _fn in (check_compliance_marker, check_verdict_denominator, check_unverified_structure, check_describing_artifact_drift, check_skill_gates, check_uninspected_constant, check_response_gates, check_postconfig_complete, check_unmeasured_quantity, check_unverified_universe, check_postfix_recheck, check_orphan_rule, check_unrecorded_miss, check_monitor_armed):
        try:
            _r = _fn()
        except Exception as _e:            # a BROKEN gate is itself a finding
            _v.append(f"{_fn.__name__} RAISED {_e!r} - this gate is broken")
            continue
        if _r:
            _v.append(_r if isinstance(_r, str) else str(_r))
    _e2 = _read_entries()
    # B1751: scan_false_skill_status (B1747) was DEFINED and never wired - it
    # is added here alongside the new Phase-5 gate. Instance 5 of any-vs-each.
    for _sc in (scan_unverified_cause, scan_uncosted_probe,
                scan_false_skill_status, scan_miss_capture_complete):
        try:
            _r = _sc(_e2)
        except Exception as _e:
            _v.append(f"{_sc.__name__} RAISED {_e!r} - this gate is broken")
            continue
        if _r:
            _v.append(_r[0])
    if _v:
        print(f"TURN-GATE BLOCK - {len(_v)} violation(s), ALL listed:",
              file=sys.stderr)
        for _i, _msg in enumerate(_v, 1):
            print(f"  [{_i}/{len(_v)}] {_msg}", file=sys.stderr)
        return 2
    # B1746b: FALL THROUGH, never return 0 here. The dirty-tree check (Gate B)
    # and several others live as INLINE logic in the legacy body, not as named
    # check_ functions - so returning 0 on a clean pre-pass silently DISABLED
    # them. Caught by test_b1255 asserting a dirty tree blocks; my own change
    # had turned the most-used gate off. Same silent-fallback class as #232.
    return _main_legacy()


def _main_legacy() -> int:
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

    struct_block = check_unverified_structure()
    if struct_block:
        print(struct_block, file=sys.stderr)
        return 2

    drift_block = check_describing_artifact_drift()
    if drift_block:
        print(drift_block, file=sys.stderr)
        return 2

    for _f in (scan_prose_only_rule, scan_findings_vs_tickets):
        _b = _f(_read_entries())
        if _b:
            print(_b[0], file=sys.stderr)
            return 2

    up_block = scan_uncosted_probe(_read_entries())
    if up_block:
        print(up_block[0], file=sys.stderr)
        return 2

    sk_block = check_skill_gates()
    if sk_block:
        print(sk_block, file=sys.stderr)
        return 2

    uc_block = check_uninspected_constant()
    if uc_block:
        print(uc_block, file=sys.stderr)
        return 2

    rg_block = check_response_gates()
    if rg_block:
        print(rg_block, file=sys.stderr)
        return 2

    pc_block = check_postconfig_complete()
    if pc_block:
        print(pc_block, file=sys.stderr)
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
