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
import re
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


# B1844: ONE PATTERN, ONE DEFINITION (L561). The marker needle lives here and
# nowhere else, LOWERCASE, and every read of it lowercases its haystack.
#
# It was inline and case-SENSITIVE, so a response carrying `## CHECKLIST
# COMPLIANCE` - the conventional way to write a heading - was BLOCKED with
# "has NO 'CHECKLIST compliance' statement" while the statement was on screen.
# The requirement was met and the mechanism could not see it. B1722, in this
# file: a gate with false positives gets bypassed, and a bypassed gate is worse
# than none.
COMPLIANCE_MARKER = "checklist compliance"


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
            elif (c.get("type") == "text"
                    and COMPLIANCE_MARKER in (c.get("text") or "").lower()):
                marker = True
    return commit_made, marker

_ENTRIES_CACHE: list | None = None


def _read_entries_uncached() -> list:
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


# B1798c (L549): a 0-entry load must ANNOUNCE itself. Every response gate reads
# the transcript; run outside the Stop hook they see nothing and return clean
# unconditionally, so an all-empty result is indistinguishable from "no
# violations". That killed a probe this turn and, per the docstring above, is
# how the #225 gate once called a nonexistent function and still looked green.
#
# A wrapper, not a restructure: the caching threads through three return paths
# and rewriting them to add one warning is how a gate breaks silently.
_EMPTY_WARNED = False


def _read_entries() -> list:
    """`_read_entries_uncached`, but a 0-entry load says so on stderr."""
    global _EMPTY_WARNED
    entries = _read_entries_uncached()
    if not entries and not _EMPTY_WARNED:
        _EMPTY_WARNED = True
        print("[turn-gate] WARNING: 0 transcript entries loaded. Every "
              "response gate will return clean for that reason alone - this "
              "is NOT evidence of compliance. Set TURN_GATE_TRANSCRIPT=<path> "
              "or pass text=/tool_text= to probe a gate directly. (L549)",
              file=sys.stderr)
    return entries



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
def _cron_at_least_hourly(expr: str) -> bool:
    """True when a 5-field cron fires AT LEAST once every hour.

    B1927 (S6-B1857b): `#185`'s cadence half matched PROSE only, so `*/11 * * *
    *` - five reports an hour - was rejected for not containing the word
    "hourly". **B1722, this same file: a gate with false positives gets
    bypassed**, and a rule that punishes over-compliance teaches the author to
    write the magic word instead of scheduling the report.

    The SCHEDULE is the machine-readable fact, so read it:

        */N * * * *   every N minutes       -> at least hourly when N <= 60
        M   * * * *   minute M of each hour -> hourly
        *   * * * *   every minute          -> yes
        0 */N * * *   every N hours         -> only when N == 1

    Anything whose HOUR field restricts to specific hours fires less often than
    hourly and is NOT accepted. Unparseable input returns False - a cadence
    that cannot be read is not a cadence that was proven.
    """
    import re as _rc

    parts = str(expr or "").strip().split()
    if len(parts) != 5:
        return False
    minute, hour = parts[0], parts[1]

    # the hour field must not restrict which hours fire
    if hour != "*":
        m = _rc.fullmatch(r"\*/(\d+)", hour)
        if not (m and int(m.group(1)) == 1):
            return False

    if minute == "*":
        return True
    m = _rc.fullmatch(r"\*/(\d+)", minute)
    if m:
        return 1 <= int(m.group(1)) <= 60
    # a fixed minute, or a list of them, fires at least once per hour
    return bool(_rc.fullmatch(r"\d+(?:,\d+)*", minute))


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
                # B1927 (S6-B1857b): the SCHEDULE counts, not the sentence.
                # `*/11 * * * *` is five reports an hour and was rejected for
                # not saying "hourly". Prose markers stay - a PushNotification
                # arm has no cron to read - but a cron proven <= hourly now
                # satisfies the cadence on its own.
                _cron = ""
                import re as _rx
                _cm = _rx.search(r'"cron"\s*:\s*"([^"]+)"', blob)
                if _cm:
                    _cron = _cm.group(1)
                _periodic = ("every hour" in _low or "hourly" in _low
                             or "scheduled report" in _low
                             or _cron_at_least_hourly(_cron))
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
    # B1773: negation-aware. `in low` accepted 'never executed' as proof.
    if _affirms(low, PROOF_PHRASES):
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
    if not _any_word(FIX_WORDS, low):
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
    # B1925: strip heredoc BODIES before deciding a launch happened.
    #
    # B1880 already put this in the OTHER launch detector, reason and all: "a
    # heredoc BODY is data handed to an interpreter, not a command that ran
    # (L569)". **This sibling never got it**, and it blocked a turn whose only
    # `run_phase1a.py --output-dir` was a string literal inside `python - <<PY`
    # - a fixture for testing another gate.
    #
    # MEASURED over the session transcript: 73 executed Bash commands match
    # `run_phase1a.py` + `--output-dir`; **65 survive the strip and are real
    # launches, 8 exist only inside a heredoc body** (all of them
    # `git add ... && git commit` with `--output-dir` in the message). Every
    # real launch still fires.
    import re as _re3
    _cmds = [_re3.sub(r"<<\s*'?(\w+)'?.*?^\1", " ", c,
                      flags=_re3.S | _re3.M) for c in cmds]
    low = " ".join(_cmds).lower()
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
    # B1767: bare "free" removed. Word boundaries stopped it matching "freely",
    # but "free RAM", "free tier" and "free of charge to run" are all whole-word
    # uses that are not cost claims. A marker whose bare form is ambiguous needs
    # its CONTEXT in the marker, not a tighter matcher.
    "for free", "is free", "are free", "essentially free", "free of cost",
    "negligible", "roughly the same", "about the same",
    "no additional", "without any cost", "at no cost",
)
QUANT_PROOF = (
    "executed", "measured", "computed", "i ran", "re-ran", "benchmark",
    "elapsed", "sim-day", "per config", "h/config", "derived from",
)


def scan_unmeasured_quantity(entries, *, text=None):
    """Flag a COST/QUANTITY claim with no evidence it was computed.

    B1767: given a `text=` seam so it can be exercised on fixed input (#241).
    It had none, so it lived in KNOWN_SEAMLESS and could only be pinned as
    `gate([]) == []` - and it then blocked a turn on a FALSE POSITIVE ("free"
    matching inside "freely") that no test could have reproduced.
    **The gate that misfires is the one that most needs to be askable.**
    """
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
    low = (" ".join(blob).lower() if text is None else text.lower())
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
    hits = _marker_hits(low, QUANT_CLAIMS)  # B1767: word-bounded
    if not hits:
        return []
    # B1773: negation-aware. `in low` accepted 'unmeasured' as proof.
    if _affirms(low, QUANT_PROOF):
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


def _response_text(entries, text=None, *, keep_code: bool = False) -> str:
    """The text a response-scanning gate should read. Use this, not _assistant_text.

    B1783. Two rules were learned on two specific gates and stayed there:

        B1738  strip inline-code spans - MENTION IS NOT USE
        B1742  read only the FINAL assistant block, because the Stop hook
               re-runs after every block and a blocked turn otherwise inherits
               the markers of its own earlier attempts

    MEASURED at B1783: of 15 text-reading gates, **2 had the first, 2 had the
    second, and 13 had NEITHER.** Both rules reached exactly the gate they were
    learned on. That is L536 - a rule learned on one gate does not travel to the
    next unless something carries it - and this function is the something.

    It also strips fenced blocks and blockquotes, because B1781 fired on a
    LEARNINGS entry that RECORDED a defect: **documenting a failure must not
    trip the gate for that failure, or the lesson can never be written down.**
    """
    import re as _re
    if text is None:
        blocks = _raw_assistant(entries)
        t = (blocks[-1] if blocks else "").lower()
    else:
        t = text.lower()
    # B1806: fenced blocks are stripped so a response DESCRIBING a gate's
    # vocabulary cannot trip it (B1738). But a gate that demands a BLOCK OF
    # NUMBERS must read them, and a table of numbers belongs in a fence -
    # scan_ticket_counts_missing reported 5 of 6 classes missing while all six
    # were on screen. Such a gate passes keep_code=True; mention-vs-use is not
    # a risk for it, because a mention of the class names carries no numbers.
    if not keep_code:
        t = _re.sub(r"```.*?```", " ", t, flags=_re.S)
    t = _strip_gate_echo(t)          # B1811
    t = _re.sub(r"^[ \t]*>.*$", " ", t, flags=_re.M)
    if not keep_code:
        # B1806: this must be guarded too. A fence IS backticks, so the INLINE
        # span strip consumed the fenced block even with keep_code=True - the
        # first version of the fix left the gate exactly as blind as before,
        # and only saying so out loud after re-running it caught that.
        t = _re.sub(r"`[^`]*`", " ", t)
    return t


# B1786: MISS MARKERS NEED AN ADMISSION CONTEXT.
#
# B1759 stemmed MISS_MARKERS from 9 entries to 116 to fix a real gap (the gate
# stayed silent on "which is the failure itself"). But 112 of the 116 are
# GENERIC TOPIC NOUNS - defect, gap, bug, broken, fail - and mechanical suffixing
# produced non-words like "brokenure" and "bugure" along the way.
#
# MEASURED: in a session ABOUT enforcement defects, the gate fired on a pure
# COUNTING answer because the response contained "defect", "gap" and "gaps"
# while DESCRIBING existing tickets. **A gate that fires whenever you discuss
# its subject is not detecting the class, it is detecting the topic.**
#
# So: an explicit admission fires alone; a generic word fires only alongside a
# first-person admission cue in the same clause. Over-stemming is the mirror of
# L515's under-stemming, and both were found the same way - by running it.
Q_SP = chr(32)
Q_I = chr(32)+chr(105)+chr(32)
Q_MY = chr(32)+chr(109)+chr(121)+chr(32)
Q_ME = chr(32)+chr(109)+chr(101)+chr(32)
ADMISSION_CUES = ("i was wrong", "owner caught", "correction:", "i should have",
                  "retract", "my mistake", "i missed", "i failed", "i had",
                  "i did not", "i never", "my own", "i shipped", "i reported",
                  "i wrote", "i built", "caught me", "blocked me", "my first")
STRONG_MISS = ("i was wrong", "owner caught", "correction:", "i should have",
               "retract", "my mistake", "i missed", "i failed")


def _miss_hits(text: str) -> list[str]:
    """MISS markers that appear in an ADMISSION context, not merely as topic."""
    import re as _re
    t = (text or "").lower()
    strong = [m for m in STRONG_MISS if m in t]
    if strong:
        return strong
    out = []
    # B1786b: a FIRST-PERSON PRONOUN is itself an admission context. Without it
    # the corpus incident stopped firing - "enforced solely by MY remembering to
    # consult it - which is the failure itself" is a confession, and my first cue
    # list missed it. **Narrowing a marker set is as easy to over-do as widening
    # one**, and the corpus is what caught the over-narrowing.
    first_person = (" i ", " my ", " me ", " mine ")
    for clause in _re.split(r"[.;:\n]", t):
        padded = " " + clause + " "
        if not (any(c in clause for c in ADMISSION_CUES)
                or any(fp in padded for fp in first_person)):
            continue
        out += [m for m in MISS_MARKERS if m in clause]
    return sorted(set(out))


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
NARRATION_STEMS = ("revert", "delete", "disable", "remove", "restore", "wire")
# B1804: irregular or multi-word - suffixing them produces garbage, so they are
# written out. `roll back`+`ed` was "roll backed"; `undid`+`ing` was "undiding".
NARRATION_IRREGULAR = (
    "roll back", "rolls back", "rolled back", "rolling back",
    "undo", "undoes", "undid", "undone", "undoing",
    "i reverted", "now wired",
)


def _conjugate(stem: str) -> set[str]:
    """English forms of a verb stem, with the E-DROP rule.

    B1804: the previous expansion was `stem + suffix` for every suffix, which
    yields `deleteing` / `disableing` / `restoreing`. **MEASURED: 5 of 12 tense
    variants went unmatched** - a gate silently blind to the progressive tense,
    which is the tense you narrate an in-flight action in.
    """
    forms = {stem, stem + "s"}
    if stem.endswith("e"):
        forms |= {stem + "d", stem[:-1] + "ing"}
    else:
        forms |= {stem + "ed", stem + "ing"}
    return forms


NARRATION_MARKERS = tuple(sorted(
    {f for st in NARRATION_STEMS for f in _conjugate(st)} | set(NARRATION_IRREGULAR)))


def _narration_hits(t: str) -> list[str]:
    """NARRATION markers present as WORDS.

    B1804 (S6-B1798b): matched with raw `in` until now, so "undocumented" hit
    `undo`, "hardwired" and "wireless" hit `wire`, "deleterious" hit `delete`.
    **MEASURED: 5 of 5 innocent sentences tripped.** Bounded on BOTH sides -
    unlike VERDICT (#246) which is prefix-guarded only, because here every
    conjugation is enumerated and a trailing suffix would be a different word.
    """
    import re as _re
    return [m for m in NARRATION_MARKERS
            if _re.search(r"(?<![a-z0-9_])" + _re.escape(m) + r"(?![a-z0-9_])", t)]
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
    nh = _narration_hits(t)      # B1804: word-bounded
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


# B1811: A GATE'S OWN DIAGNOSTIC IS NOT EVIDENCE ABOUT THE TURN.
#
# `scan_synthetic_provenance` explains itself by quoting `rng.normal(1,3,30)`.
# The Stop hook feeds its report back into the transcript and the next turn's
# tool calls echo it, so the message became the evidence for re-firing - on a
# turn whose every quoted decimal was a real measurement.
#
# Third instance of the shape: B1732 (the skills gate's self-description shifted
# its own window), B1738 (a response listing trigger words fired the gate), and
# this. B1738 stripped backtick spans from the RESPONSE, which could not help
# because the echo arrives through TOOL text.
def _strip_gate_echo(t: str) -> str:
    """Remove any previous turn-gate report from `t`.

    A report starts at "TURN-GATE BLOCK" and runs to the end of its numbered
    list. Everything in it is the gate machinery describing itself, and none of
    it is evidence about what this turn did.
    """
    import re as _re
    if not t:
        return t
    # B1812: LINE-ANCHORED. The first version used unanchored regexes, and tool
    # text is ONE line - json.dumps(input) joined by spaces - so `[^\n]*`
    # consumed the whole corpus after the first "[1/1]" appearing inside any
    # quoted string. MEASURED: 183 chars in, 84 out, and every tool call after
    # the quote erased. That blinded `scan_discipline_not_loaded` on the very
    # turn the strip shipped.
    #
    # A gate report is LINE-ANCHORED; an echo inside a JSON string is not. That
    # distinction is exact, so it is the one to use.
    out = []
    for line in t.splitlines():
        st = line.lstrip()
        if _re.match(r"turn-gate block\b", st, _re.I):
            continue
        if _re.match(r"\[\d+/\d+\]\s", st):
            continue
        out.append(line)
    return "\n".join(out)

def _tool_text(entries, tool_text=None) -> str:
    """Everything this turn actually RAN or READ - the inputs of every tool call.

    B1721: the four B1720 gates catch SYMPTOMS (a claim with no evidence, a
    finding with no ticket, a fix with no class sweep, a recommendation with no
    objection). None catches the CAUSE the owner named: compressing work into
    fewer tool calls - reading part of a file, answering from a module constant
    instead of its call site. That cause is checkable, because the transcript
    carries the tool calls: if a turn NAMES a constant it never grepped, it is
    reasoning from memory of the code rather than the code.
    """
    # B1811: `tool_text` is the INJECTION SEAM, and it must travel the same
    # pipeline as the live path. Previously every caller wrote
    # `_tool_text(entries) if tool_text is None else tool_text`, so an injected
    # value skipped the scrubbing below - a probe then exercised a path
    # production never takes, and reported clean for that reason (#241's spirit:
    # a seam that bypasses the pipeline is not a seam).
    if tool_text is not None:
        return _strip_gate_echo(tool_text)
    out = []
    for d in entries or ():
        if not isinstance(d, dict) or d.get("type") != "assistant":
            continue
        for blk in (d.get("message") or {}).get("content") or ():
            if isinstance(blk, dict) and blk.get("type") == "tool_use":
                out.append(json.dumps(blk.get("input") or {}))
    # a previous turn-gate report is not evidence about this turn
    return _strip_gate_echo(" ".join(out))


# B1813: WHAT THE TURN RAN, as distinct from what it WROTE INTO A FILE.
#
# `scan_synthetic_provenance` fired on a turn whose only decimals were real cube
# measurements, because `rng.normal` appeared 3 times in a file the turn WROTE -
# a test fixture and a lesson that quote the generator to explain it.
#
# B1738 established mention-vs-use for the RESPONSE. The same distinction exists
# in TOOL text and had no expression until now. The transcript carries the tool
# NAME, so it is exact rather than heuristic:
#
#     Bash / PowerShell  {"command": ...}   EXECUTED
#     Write / Edit       {"content": ...}   WRITTEN, never run
_EXECUTING_TOOLS = ("bash", "powershell")
# B1815: a command SEGMENT whose job is searching mentions its pattern, it does
# not run it. MEASURED: the only executed command containing `rng.` on the turn
# this shipped was the grep run to FIND `rng.`. Fourth instance of the
# self-reference family (B1732, B1738, B1811, B1815).
_SEARCH_TOOLS = ("grep", "rg ", "findstr", "select-string", "ripgrep", "ack ")


def _any_word(markers, text: str) -> bool:
    """Substring scan that will not match a marker inside a LONGER word.

    B1872. MEASURED across 53 marker lists: 3 markers match their own
    NEGATION in real prose - `grade` inside `degrade`, `fixed` inside
    `unfixed`, `corrected` inside `uncorrected`. **A marker matching its own
    negation is the worst shape available: the text says the opposite of what
    the gate concludes.** `STALL_MARKERS` was the demonstrably live one
    ("hang" inside "changed"), fixed at B1866.

    Multi-word phrases keep plain `in` - a phrase cannot hide inside a single
    word, and anchoring it would break on punctuation.
    """
    for m in markers:
        ml = str(m).lower()
        if not ml:
            continue
        # B1872b: anchor only PLAIN WORDS. A marker carrying `_`, `.`, `-`
        # or a space is a prefix (`output_`), an extension (`.csv`) or a
        # phrase (`not a measurement`) - each DELIBERATELY partial, so
        # anchoring is a different rule rather than a stricter one.
        # `output_` exists to match `output_cfg1`, and the trailing `_` is a
        # word character, so the boundary refused the one thing it is for.
        if not ml.isalpha():
            if ml in text:
                return True
            continue
        # B1904: LEFT boundary only, plus an optional plural on the right.
        #
        # The three defects B1872 fixed were all PREFIX collisions - `grade`
        # inside `degrade`, `fixed` inside `unfixed`, `corrected` inside
        # `uncorrected` - where extra letters on the LEFT invert the meaning.
        # Anchoring BOTH sides also blocked SUFFIX inflection, and `cubes` is
        # the same word as `cube`, not its opposite. The gate then refused
        # "measured 15.4 across the four config cubes", which names its source.
        #
        #     grade in degrade   LEFT  collision, meaning INVERTED -> block
        #     cube  in cubes     RIGHT inflection, meaning SAME    -> allow
        #
        # 14 FIGURE_SOURCES members are plain words that pluralise; every one
        # was broken by the two-sided anchor.
        if re.search(r"(?<![a-z0-9_])" + re.escape(ml) + r"(?:s|es)?(?![a-z0-9_])",
                     text):
            return True
    return False


def _since_last_user(entries):
    """Entries AFTER the last genuine user text message - i.e. THIS TURN.

    B1881. Three functions computed this boundary inline and a fourth,
    `_executed_text`, did not - so it read the whole session while its
    docstring said "this turn". ONE definition, per L561: a duplicated pattern
    is a divergence waiting for someone to fix half of it, and here one copy
    was simply MISSING - the same defect with the divergence at zero.
    """
    last = -1
    for i, e in enumerate(entries or ()):
        if not isinstance(e, dict) or e.get("type") != "user":
            continue
        c = (e.get("message") or {}).get("content")
        if (isinstance(c, str) and c.strip()) or (
                isinstance(c, list) and any(
                    isinstance(x, dict) and x.get("type") == "text" for x in c)):
            last = i
    return list(entries or ())[last + 1:]


def _drop_search_segments(cmd: str) -> str:
    """Blank out segments that only SEARCH. Compound commands judged per part."""
    keep = []
    for seg in re.split(r"&&|\|\||;|\|", cmd):
        low = seg.strip().lower()
        if any(low.startswith(t) or f" {t}" in low[:40] for t in _SEARCH_TOOLS):
            continue
        keep.append(seg)
    return " ".join(keep)


def _executed_text(entries, tool_text=None) -> str:
    """Only the commands this turn RAN. Not file contents it wrote.

    Same injection contract as `_tool_text` (B1811): an injected value travels
    the same scrubbing as the live path.

    B1881: "this turn" is now TRUE. The body iterated every entry with no
    boundary, so gates built on it judged the whole session -
    `scan_bare_python_launch` blocked three consecutive turns on a command at
    transcript line 471 dated 2026-05-15, out of 130,622 lines. The docstring
    always said this turn; the implementation contradicted it.
    """
    if tool_text is not None:
        return _strip_gate_echo(tool_text)
    entries = _since_last_user(entries)
    out = []
    for d in entries or ():
        if not isinstance(d, dict) or d.get("type") != "assistant":
            continue
        for blk in (d.get("message") or {}).get("content") or ():
            if not isinstance(blk, dict) or blk.get("type") != "tool_use":
                continue
            if str(blk.get("name") or "").lower() not in _EXECUTING_TOOLS:
                continue
            out.append(_drop_search_segments(
                str((blk.get("input") or {}).get("command") or "")))
    return _strip_gate_echo(" ".join(out))

def scan_uninspected_constant(entries, *, tool_text=None,
                              text=None) -> list[str]:
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
    # B1760b: the EARLY RETURN read entries too, so injected text never got
    # past it. TWO ignored-parameter bugs in one function - both invisible to
    # a proof that only ever fed it live entries.
    # B1938 (S6-B1783b): route through _response_text, ONE gate at a time.
    # This gate is #222 mechanised and read text RAW, so it carried none of
    # the three rules the helper holds: B1738 inline-code spans are MENTIONS,
    # B1742 read only the FINAL assistant block, B1781 strip fenced blocks so
    # documenting a defect cannot trip the gate for that defect.
    #
    # keep_code=False is deliberate and not obvious. This gate hunts ALL-CAPS
    # identifiers and CLI flags, which are routinely written in backticks -
    # stripping code spans makes it read only constants named in PROSE, which
    # is exactly #222's target: a constant QUOTED AS A FACT, not shown as a
    # token.
    #
    # The 11 remaining raw readers are NOT converted here. The identical line
    # appears 12 times, and S6-B1783b says converting them together is the
    # change that breaks several silently.
    t = _response_text(entries, text)
    if not t:
        return []
    tt = _tool_text(entries, tool_text).lower()
    # B1760: honour the injected text. This function accepted `text=` and then
    # read `_raw_assistant(entries)` for the case-preserved copy, so the
    # parameter existed and did nothing - the gate could never be exercised on
    # supplied text. Found by the incident corpus, not by its own 6/6 proof,
    # because that proof only ever fed it live entries.
    # B1938c: the CASE-PRESERVED copy needs the mention strip too. Converting
    # `t` to _response_text left this line reading unstripped text, so a
    # backticked `MIN_N` still fired - L592 inside one function, one batch
    # after L592 was written. The comment above records B1760 fixing the
    # INJECTION path for this same variable; the MENTION-vs-USE strip never
    # reached it.
    #
    # MEASURED: 2 gates keep a case-preserved copy - this one and
    # scan_unverified_structure. Only this one is converted (S6-B1783b:
    # converting together is the change that breaks several silently), and
    # test_b1938 pins the count so the sibling stays visible.
    raw = _strip_mentions(
        " ".join(_raw_assistant(entries)) if text is None else text)
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


def count_text_readers(src: str) -> tuple:
    """(raw, routed, case_preserved) - text-reading gates, counted as FUNCTIONS.

    B1941b / L593: *put the measuring code IN the pin, or derive both from one
    function.* B1938 measured GATES (2) and pinned OCCURRENCES (4) because the
    count was written twice - `re.findall` counted a definition line and two
    comment mentions that a per-function split does not.

    One pass, one definition, three numbers. The pin calls this; any future
    measurement calls this; **they cannot disagree.**

    `raw` is the S6-B1783b backlog: gates still reading `_assistant_text`
    instead of `_response_text`, so they carry none of B1738 (mentions),
    B1742 (final block) or B1781 (fences).
    """
    import re as _rc

    parts = _rc.split(r"\ndef (scan_[a-z_]+)", src)
    raw = routed = case_preserved = 0
    for i in range(1, len(parts), 2):
        body = parts[i + 1]
        if "_response_text" in body:
            routed += 1
        elif "_assistant_text" in body:
            raw += 1
        if "_raw_assistant" in body:
            case_preserved += 1
    return raw, routed, case_preserved


def _strip_mentions(text: str) -> str:
    """B1738/B1781's strips WITHOUT lowercasing, for gates that need case.

    B1938c: `scan_uninspected_constant` searches a CASE-PRESERVED copy for
    ALL-CAPS identifiers, so it cannot use `_response_text` (which lowercases)
    and was reading unstripped text. A backticked `MIN_N` fired as though it
    had been quoted as a fact.

    **Mention-vs-use is orthogonal to case**, and separating them is what lets
    a case-sensitive gate have both.
    """
    import re as _rm

    t = _rm.sub(r"```.*?```", " ", text, flags=_rm.S)   # B1781 fenced blocks
    t = _rm.sub(r"^[ \t]*>.*$", " ", t, flags=_rm.M)    # blockquotes
    return _rm.sub(r"`[^`]*`", " ", t)                  # B1738 inline spans


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
    tt = _tool_text(entries, tool_text)
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
    tt = _tool_text(entries, tool_text).lower()
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
    # B1806: was rsplit(..., 1) - the LAST occurrence. B1732 moved it there
    # because an EARLIER mention shifted the window off the real block; the
    # mirror is equally true. A LATER prose mention ("same standing as SKILLS
    # INVOKED") opened the window PAST a complete block and reported all three
    # skills missing. Neither end is right - the block is wherever the members
    # are, so try every occurrence.
    # B1763: route through require_each instead of hand-rolling it. This gate
    # was ALREADY each-shaped - it computed the absent members and named them -
    # which is precisely why it is the right first conversion: adopting the
    # primitive here changes no behaviour and removes the duplicate.
    #
    # The wider point (S6-B1762f): `require_each` existed from B1751 and two
    # fresh any-vs-each defects still shipped, because AVAILABILITY IS NOT
    # ADOPTION. A primitive nobody reaches for is a library, not a guardrail.
    return require_each(
        "SKILLS-INVOKED BLOCK INCOMPLETE",
        _best_block_window(t, ("skills invoked",),
                           {n: (lambda w, _n=n: _n in w) for n in ALL_SKILLS}),
        why=("Owner directive B1730: every turn lists ALL THREE skills with an "
             "explicit status - FULLY LOADED / TRIGGERED-NOT-INVOKED / "
             "NOT-TRIGGERED / ALWAYS-ON. Omitting one lets silence stand in "
             "for a status."))


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

    B1883 (S6-B1813d): THE RATIONALE BELOW IS STALE AND THE CHECK IS NOT.
    Since B1744 the hook injects the FULL SKILL BODY - see
    `inject_tier3_discipline.py:72` emitting "FULL SKILL, auto-injected
    every turn", with SKILL.md at ~119 KB. **A stale rationale is worse
    than a wrong check: the reader believes the reason and stops asking.**
    The check still earns its place - loading the body is not invoking
    the skill, and the gate fires on the ABSENCE of invocation.

    ORIGINAL, PRESERVED FOR LINEAGE AND KNOWN STALE:
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
    tt = _tool_text(entries, tool_text)
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
    # B1942 (S6-B1783b): third gate routed through _response_text. Still ONE
    # at a time - 9 sites remain and S6-B1783b calls converting them together
    # the change that breaks several silently.
    t = _response_text(entries, text)
    if not t:
        return []
    hits = [w for w in COST_WORDS if w in t]
    if not hits:
        return []
    # B1774: strip AUTHORED payloads first - writing the word "grep"
    # inside a document is not inspecting anything.
    tt = _tool_invocations(
        _tool_text(entries, tool_text)).lower()
    if any(e in tt for e in OPEN_EVIDENCE):
        return []
    return [f'UNCOSTED PROBE (#230 EXT / L506): this turn estimates effort '
            f'({chr(34)}{hits[0].strip()}{chr(34)}) but NO tool call opened an artifact. '
            'An effort estimate is a quantitative claim, and a claim about what '
            'a file can support is a capability claim. OPEN the artifact and '
            'name the FIELD the work needs, or drop the estimate.']


def scan_shell_substitution(entries, *, tool_text=None) -> list[str]:
    """B1765 (#245): a shell -c string must not carry live command substitution.

    THIS RAN. Writing a commit message with `git commit -m "... `git reset
    --hard` ..."` - backticks used to DESCRIBE the danger - made bash execute
    the thing being described. `git reflog` shows `reset: moving to HEAD`. The
    index was cleared and unstaged tracked files reverted; `.claude/settings.json`
    lost its edit and the commit captured one file instead of two.

    It is the third instance of the CLAUDE.md hard rule (L49, L77) and the first
    that was not a decision at all - the command was never typed as a command.
    **Prose about a destructive command is indistinguishable from the command
    once it is inside double quotes.**

    Every earlier commit this session used `git commit -F -` with a QUOTED
    heredoc (`<<'MSG'`), which performs no substitution and would have been
    inert. The deviation to `-m "..."` is the entire defect.
    """
    import re
    t = _tool_text(entries, tool_text)
    if not t:
        return []
    hits = []
    # `...` inside a double-quoted -m/-F argument, or $(...) anywhere in a
    # commit/tag message. Single-quoted heredocs are the safe form and contain
    # neither pattern in the command string itself.
    # B1768 (#248): WIDENED from `git commit|tag` to ANY double-quoted shell
    # argument. The original was named after the INCIDENT (a commit message)
    # rather than the MECHANISM (bash substitutes inside every double-quoted
    # argument). One batch after writing it I hit the identical defect via
    # `python -c "...`backticks`..."` - the under-generalization the mandate
    # forbids, committed against my own rule.
    for m in re.finditer(r"-(?:m|c|F|-message|-eval)\s+\"([^\"]*)\"", t):
        arg = m.group(1)
        if "`" in arg or "$(" in arg:
            hits.append(arg[:70])
    if not hits:
        return []
    return [f"SHELL SUBSTITUTION IN A COMMIT MESSAGE (B1765/#245): {hits[0]!r}. "
            "Backticks and $(...) inside a double-quoted -m argument are "
            "EXECUTED by bash before git ever runs - this is how `git reset "
            "--hard` ran accidentally and reverted uncommitted work. Use "
            "`git commit -F -` with a quoted heredoc (<<'MSG'), which performs "
            "no substitution."]


# B1769: the owner-ruled queue vocabulary (2026-08-19). CLOSED set - a seventh
# class is exactly how 132 labels happened, so adding one is a ruling, not a
# convenience.
# B1778 owner ruling 2026-08-20: "Done isn't closure. CLOSED is only to be
# marked once you have verified their work against the actual code and code log
# and not on documentation." So DONE is SELF-REPORTED and CLOSED is VERIFIED,
# and only `promote_verified_closed.py` may write CLOSED - never a turn.
# B1784 owner ruling 2026-08-20: SIX mutually exclusive classes. DONE is
# replaced by EXECUTED, and CLOSED folds into it. There is no
# "finished but unverified" resting place: a row is EXECUTED (verified
# against code and the change log) or it is still work.
QUEUE_CLASSES = ("EXECUTED", "DROPPED", "BLOCKED", "DEFERRED", "OPEN",
                 "RUNNING")
QUEUE_NEEDS_REASON = ("DROPPED", "BLOCKED", "DEFERRED", "OPEN")
# B1769c: "-" and "N/A" REMOVED. They are degenerate markers - matched as
# substrings they flag any reason containing a hyphen, and matched exactly they
# add nothing the length floor does not already catch. Keeping them cost a
# live block of this gate's own author on its first run.
QUEUE_PLACEHOLDERS = ("reason-not-recorded", "tbd", "todo", "unknown",
                      "see above", "as above", "needs review", "n/a")


def _queue_rows_added(diff_text=None) -> list[str]:
    """Ticket rows ADDED to EXECUTION_QUEUE.md this turn.

    B1795: a SECOND definition of this name shadowed the first, and the one it
    replaced was the one that also read the last commit. The gate could
    therefore only see rows still UNCOMMITTED, so any turn that committed
    before turn-end tripped it - a false positive whose fix already existed in
    the file and had been silently overwritten.

    Both sources are checked now. `HEAD~1..HEAD` assumes the last commit
    belongs to this turn, which is the standing per-turn commit convention;
    a turn that adds no rows and commits nothing still reports none.
    """
    import re
    import subprocess
    if diff_text is not None:
        return [ln[1:] for ln in diff_text.splitlines()
                if re.match(r"^\+\|\s*\*\*S6-", ln)]
    # Working tree FIRST, then the last commit. A row added in the commit and
    # then EDITED in the working tree appears in both; the working-tree copy is
    # newer, so it wins - #271's last-state-wins rule applied to this gate's own
    # input. Without the dedup the gate reports the stale copy and a row that
    # was fixed this turn still fails.
    out: list[str] = []
    seen: set[str] = set()
    for cmd in (["git", "diff", "HEAD", "--unified=0", "--", "EXECUTION_QUEUE.md"],
                ["git", "diff", "HEAD~1", "HEAD", "--unified=0",
                 "--", "EXECUTION_QUEUE.md"]):
        try:
            d = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=20).stdout or ""
        except Exception:
            continue
        for ln in d.splitlines():
            m = re.match(r"^\+\|\s*\*\*(S6-[A-Za-z0-9-]+)\*\*", ln)
            if m and m.group(1) not in seen:
                seen.add(m.group(1))
                out.append(ln[1:])
    return out


# B1778 (#258): DERIVED COUNTS. The 30 gates before this one all scan PROSE for
# marker strings. "271" is not a marker string, so a wrong number sailed through
# every one of them.
#
# The council's Contrarian called the "no gate checks arithmetic" framing
# self-serving, and was right: the defect is STRUCTURE-BLINDNESS, not arithmetic
# specifically. Tomorrow it is a bad join or a stale key - equally invisible to
# a phrase scanner. What IS mechanisable is the narrower, real thing: a turn that
# reports a LEDGER COUNT must have computed it THIS TURN.
COUNT_CLAIMS = (
    "tickets closed", "closed in", "already closed", "were closed",
    "tickets open", "open tickets", "still open", "were created",
    "tickets created", "created in the last", "of them are", "of those are",
)
COUNT_PROOF = ("execution_queue", "audit_done_claims", "audit_ticket_staleness",
               "promote_verified_closed", "git log", "csv.dictreader",
               "value_counts", "collections.counter", "groupby",
               # B1943b: the project's CANONICAL counter was missing.
               # queue_state.py IS collections.Counter (lines 60-62), is run
               # every batch to produce the ticket counts, and is imported BY
               # audit_ticket_staleness which was already listed. MEASURED:
               # `python scripts/queue_state.py` did NOT clear the gate while
               # `grep -c` did - so the vocabulary rewarded a grep that
               # satisfies the gate over the script that answers the question.
               "queue_state")


def scan_unverified_count(entries, *, text=None, tool_text=None) -> list[str]:
    """#258: a ledger count in the response must have been COMPUTED this turn.

    I told the owner "317 created in the last 48h, 271 already closed". The real
    figure was 13. I had computed `created - open = closed`, arithmetic valid
    only if every ticket starts open - and 87pct are written already-DONE.

    **No gate could see it.** Every other gate here matches marker strings in
    prose; a number carries no marker. And the number was FLATTERING, so the
    adversarial pass I run on suspect claims never engaged - which is exactly
    where a favourable figure most needs it.
    """
    import re as _re
    # B1943 (S6-B1783b): fourth gate routed through _response_text.
    #
    # This one guards COUNTS, and four were mis-stated this session -
    # S6-B1757d's 22-that-was-7, S6-B1777d's tickets-vs-batches, B1929's
    # LIVE-vs-OPEN, B1938's gates-vs-occurrences. B1738 means a count shown in
    # backticks as a TOKEN stops reading as a claim, while one asserted in
    # prose still does.
    t = _response_text(entries, text)
    if not t:
        return []
    hits = [c for c in COUNT_CLAIMS if c in t]
    if not hits:
        return []
    # a bare mention with no digits nearby is prose, not a reported count
    if not _re.search(r"[0-9]{2,}", t):
        return []
    tt = _tool_text(entries, tool_text).lower()
    # B1872 (S6-B1827b): this cleared EVERY ledger count in a response as soon
    # as ONE computing call appeared anywhere in the tool stream. `queue_state`
    # runs every turn, so the clearance was PERMANENT - the gate could not fire
    # again for the rest of the session. Require the proof to be word-bounded
    # so `queue_state` does not clear via a substring, and keep the any-match
    # semantics that are correct for "was a count computed at all".
    if _any_word(COUNT_PROOF, tt):
        return []
    return [f"UNVERIFIED LEDGER COUNT (B1778/#258): this turn reports "
            f"{hits[0]!r} with a number, and no tool call this turn computed it. "
            "'271 closed in 48h' was 13 - `created - open = closed` assumed "
            "every ticket starts open, and 87pct are written already-DONE. "
            "Compute the count from EXECUTION_QUEUE.md this turn, or drop it."]


def scan_partial_distribution(entries, *, text=None) -> list[str]:
    """#260: report a class breakdown in FULL, or not at all.

    I told the owner "388 CLOSED / 149 DONE / 96 OPEN ... 261 of 649". The
    owner did the arithmetic: 388+149+96 = 633, not 649. Three of SEVEN classes
    were shown against a total covering all seven, so the reader could not
    reconcile it - and the figures were themselves wrong, lifted from the
    migration script's TRANSITION counts rather than the ledger's final state.

    **The fix needed no verification layer.** Printing every class would have
    exposed it instantly. This gate asks only that: if a response lists queue
    classes with counts and also states a TOTAL, the parts must sum to the whole.
    """
    import re as _re
    t = _response_text(entries, text)
    CLASSES = ("closed", "done", "open", "blocked", "dropped", "deferred",
               "running")
    WINDOW = 240
    for tm in _re.finditer(r"of ([0-9]{3,4})\b", t):
        tot = int(tm.group(1))
        lo, hi = max(0, tm.start() - WINDOW), min(len(t), tm.end() + WINDOW)
        near = t[lo:hi]
        pairs = _re.findall(
            r"(?:^|[^a-z0-9])([0-9]{1,4})\s+(" + "|".join(CLASSES) + r")(?![a-z])",
            near)
        if len(pairs) < 2:
            continue
        seen = {}
        for n, cls in pairs:
            seen.setdefault(cls, int(n))
        part = sum(seen.values())
        # only a PARTIAL listing is a defect: parts short of a stated whole,
        # and only when the shortfall is not itself another figure entirely.
        if part >= tot or part * 3 < tot:
            continue
        missing = sorted(set(CLASSES) - set(seen))
        if not missing:
            continue          # all classes shown; the total refers elsewhere
        return [f"PARTIAL DISTRIBUTION (B1779/#260): the response lists "
                f"{sorted(seen)} summing to {part}, then cites a total of "
                f"{tot} nearby. The reader cannot reconcile {part} against "
                f"{tot}. Unlisted class(es): {missing}. '388+149+96 vs 649' is "
                "how the owner caught the last one - show every class, or cite "
                "no total."]
    return []
    seen = {}
    for n, cls in pairs:
        seen.setdefault(cls, int(n))
    part = sum(seen.values())
    totals = [int(x) for x in _re.findall(r"of ([0-9]{3,4})\b", t)]
    for tot in totals:
        if tot > part:
            missing = sorted({"closed", "done", "open", "blocked", "dropped",
                              "deferred", "running"} - set(seen))
            return [f"PARTIAL DISTRIBUTION (B1779/#260): the response lists "
                    f"{sorted(seen)} summing to {part}, then cites a total of "
                    f"{tot}. The reader cannot reconcile {part} against {tot}. "
                    f"Unlisted class(es): {missing}. '388+149+96 vs 649' is how "
                    "the owner caught the last one - show every class, or cite "
                    "no total."]
    return []


# B1794 (#270): NO HALF MEASURES. Owner directive 2026-08-20:
#   "You didnt bother to read all of them end to end. You are in a hurry to make
#    decisions. ... you are supposed to analyze anything not just tickets by
#    going through the tickets or documents or even code end to end no half
#    measures"
#
# MEASURED: I read 20 of 141 rows, projected the rate onto the other 121, and
# reported that projection as guidance. Reading all 138 gave 100 EXECUTED /
# 38 OPEN - the sample said 10pct complete, the population is 72pct. The first
# 20 were PLANNING rows; the rest were MEASUREMENT records. **A sample drawn
# from one end of a sorted population is not a sample.**
TRUNCATION = (
    "head -", "tail -", "[:20]", "[:30]", "[:50]", "[:100]",
    "[:150]", "[:165]", "[:180]", "[:200]", "[:230]", "[:300]", "--show",
    "first 20", "sample of", "batch 1 of", "spot-check",
)


# B1807: truncation counts only where it is applied to the SOURCE. Everything
# after a `|` has already seen the whole input - `pytest -q | tail -3` trims a
# computation's OUTPUT and is not sampling. MEASURED: three display trims on a
# compliant turn were read as a partial read, the third false positive this
# gate has produced. A gate that cries wolf trains its author to ignore it.
def _sampling_hits(tool_text: str) -> list[str]:
    """TRUNCATION markers applied to the SOURCE, not to a command's output."""
    import re as _re
    hits = []
    for line in tool_text.splitlines():
        head = line.split("|")[0]              # pre-pipe segment only
        hits += [m for m in TRUNCATION if m in head]
        # `sed -n 'N,Mp' file` is THE file-sampling idiom and is what the
        # original incident used. A PATTERN range (`sed -n '/x/,/y/p'`) reads
        # a whole region and is not sampling.
        if _re.search(r"sed\s+-n\s*['\"]?\s*\d+\s*,\s*\d+\s*p", head):
            hits.append("sed line-range")
    return hits
VERDICT = (
    "promoted", "verified", "executed", "complete", "nothing pending",
    "stays open", "verdict", "i judge", "classified", "disposition",
)

# B1796: the ticket dialect above covers ONE THIRD of #270's declared scope.
# A verdict over CODE or a DOCUMENT is a universal quantifier plus a state verb,
# or a negative existential. MEASURED before this: 2 of 10 realistic cases fired,
# 0 of 8 for code and documents.
_UNIVERSAL = (
    r"\b(?:all|every|each|none)\s+(?:of\s+)?(?:the\s+)?\d*\s*"
    r"(?:[\w./-]+\s+){1,5}"
    r"(?:are|is|was|were|have|has|carry|carries|read|reads|use|uses|name|"
    r"names|reference|references|contain|contains|sit|sits|live|lives|"
    r"point|points|call|calls|match|matches)\b")
# B1796: forward-looking clauses state an INTENTION. "each row needs its own
# verdict later" is work narration, not a conclusion drawn from a partial read.
_FUTURE = (r"\b(?:will|later|going to|plan to|next turn|i intend|"
           r"remains? to be|yet to|about to|then )\b")
_NEG_EXISTENTIAL = (
    r"\b(?:no other|none of|nowhere else|not a single)\b|"
    r"\bno\s+[\w./-]+\s+(?:outside|anywhere|still|remains|exists)\b|"
    r"\b(?:is|are|remains|remain)\s+unused\b")


# B1798 (#246 / S6-B1774e): VERDICT was matched with raw `in`, so "classified"
# matched inside "reclassified" and blocked a compliant turn. Prefix-guarded and
# suffix-free is the #239 stem shape: "complete" still catches "completed", but
# a marker cannot match in the middle of a longer word.
def _verdict_hits(s: str) -> list:
    """VERDICT markers present as WORDS (suffixes allowed, prefixes not)."""
    import re as _re
    return [m for m in VERDICT
            if _re.search(r"(?<![a-z0-9_])" + _re.escape(m), s)]

# B1795 (#271): THE LEDGER IS AN APPEND LOG, NOT A TABLE OF TICKETS.
# Closing a ticket APPENDS a row instead of editing the old one, so 81 ids
# carry 2+ rows and 74 sit in contradictory states - 57 are EXECUTED AND OPEN
# at once. MEASURED at B1795: 823 rows vs 721 distinct tickets.
#
# Every queue count quoted this session counted ROWS while calling them
# TICKETS. That is the structural cause of the arithmetic the owner caught by
# addition, and it violates "I want mutually exclusive groups" at the DATA
# level even after the vocabulary was made exclusive at the LABEL level.
#
# A count is fit to quote only if it deduplicates by id, last row wins -
# which is what scripts/queue_state.py does and why it exists.
_QCOUNT_PAT = (
    r"\b(\d{2,4})\s*(?:tickets?|rows?|\w+\s+)?"
    r"(executed|dropped|blocked|deferred|open|running)\b|"
    r"\b(executed|dropped|blocked|deferred|open|running)\s*[:=]?\s*(\d{2,4})\b")
_QDEDUP = ("queue_state", "last row wins", "last-row-wins", "distinct ticket",
           "per distinct", "deduplicat", "dedupe")


def scan_row_vs_ticket(entries, *, text=None, tool_text=None) -> list[str]:
    """#271: a queue class count must be per TICKET, not per ROW.

    Fires when a turn quotes a queue-class count while its tool calls read
    EXECUTION_QUEUE.md without any dedup marker. The ledger has 102 more rows
    than tickets, so a row-level count is wrong by an unbounded amount and
    reads exactly like a right one.

    It cannot tell a correct count from an incorrect one - it checks that the
    METHOD names dedup. A turn that dedups without saying so trips it; saying
    so is cheap and is the point.
    """
    import re as _re
    t = _response_text(entries, text)
    if not t or not _re.search(_QCOUNT_PAT, t, _re.I):
        return []
    tt = _tool_text(entries, tool_text).lower()
    if "execution_queue" not in tt:
        return []
    if any(d in tt or d in t for d in _QDEDUP):
        return []
    return ["ROW-vs-TICKET COUNT (B1795/#271): this turn quotes a queue-class "
            "count and reads EXECUTION_QUEUE.md, but nothing in the method "
            "deduplicates by ticket id. **The ledger is an APPEND LOG: 823 "
            "rows for 721 tickets, 81 ids duplicated, 57 EXECUTED AND OPEN at "
            "once.** Count via scripts/queue_state.py (last row wins), or say "
            "explicitly that the figure is row-level and why that is what you "
            "want."]


# S6-B1705e (#201 PROVENANCE HALF): #201 asks whether a quantity was COMPUTED.
# It never asks what FROM. `2.422` came out of `rng.normal(1, 3, 30)` in my own
# boundary probe and satisfied #201 completely, because "measured" was true of
# the arithmetic and false of the meaning. The probe's one real finding was the
# BOUNDARY (n=29 -> None, n=30 -> a value); the number itself measured nothing.
#
# A random generator in the tool calls plus a number in the prose plus
# measurement language is the exact shape. The escape is one word - SYNTHETIC -
# said where the number is quoted.
SYNTHETIC_SOURCES = (
    "rng.", "np.random", "numpy.random", "default_rng", "random.gauss",
    "random.normal", "random.randn", "random.seed", "random.uniform",
    "make_fixture", "fake_", "dummy_",
)
# B1832: what counts as NAMING AN INPUT. A source is an artifact, a producer,
# or an explicit admission that the figure is not a measurement at all.
# B1832: ONE definition, used by the pre-filter AND the clause loop.
# They were separate copies and I corrected only the second, so the
# first kept rejecting sentence-final decimals and the fix never ran
# (B1812's shape - a guard applied at one site of two).
_DECIMAL = r"(?<![\w.#])\d+\.\d+(?!\.?\d)"
FIGURE_SOURCES = (
    # artifacts
    ".csv", ".json", ".parquet", ".txt", ".md", "output_", "cache",
    "cube", "ledger", "artifact", "transcript",
    # producers
    ".py", "script", "pytest", "grade", "re-grad", "regrad", "queue_state",
    "git ", "commit",
    # explicit non-measurements
    "synthetic", "fixture", "hand-built", "hand built", "illustrative",
    "worked example", "not a measurement", "measures nothing", "made-up",
    "arithmetic", "derived from", "by construction", "ticker-year",
)
SYNTHETIC_LABEL = (
    "synthetic", "not a measurement", "measures nothing", "illustrative",
    "hand-built", "toy fixture", "made-up", "fabricated", "deterministic "
    "fixture", "no rng", "worked example",
)


# B1910 (S6-B1909c): a NOVELTY claim is a claim.
#
# I reported a duplicate-exit collapse as an "undocumented third collapse"
# because the code comment beside it names only the other two. LEARNINGS
# carries it THREE times, at 100.0pct over n=7,319. Caught by grepping the
# record before the report went out - luck dressed as process, because nothing
# required that grep.
#
# #201 governs figures, #222 constants, #256 re-derivation. "this is new /
# undocumented / nothing covers it" is an assertion about the WHOLE RECORD and
# had no gate - the widest claim in the vocabulary and the only unguarded one.
NOVELTY_CLAIMS = (
    "undocumented", "not documented", "nowhere documented",
    "no prior", "nothing covers", "not covered", "no existing",
    "first instance", "unrecorded", "not in the record",
    "no ticket exists", "not filed", "never been filed",
    "nothing in the queue", "not in learnings",
    "no precedent", "unprecedented",
)

# What turns the claim into a finding: the SEARCH that established it.
# Deliberately DISJOINT from the claim vocabulary, so "not in the record"
# cannot satisfy itself on the word `record`.
NOVELTY_SEARCH = (
    "grep", "grepped", "searched", "scanned", "queue_state",
    "learnings.md", "execution_queue", "checklist.md", "git log",
    "no matches", "0 matches", "zero matches", "returns nothing",
    "returned nothing", "no hits", "audit_ticket_staleness",
    "queue_crossref",
)

# B1910: the retraction vocabulary is built in FROM THE START rather than
# bolted on after the gate blocks its own incident report - self-reference has
# hit this file ~13 times. `synthetic` clears #201 for exactly this reason: a
# sentence saying the prior art EXISTS is the honest outcome of the check this
# gate asks for, and punishing it would teach the wrong lesson.
NOVELTY_RETRACTION = (
    "already filed", "already documented", "already covered", "already known",
    "already recorded", "already carries", "carries it", "is documented",
    "was wrong", "turned out", "in fact documented", "prior art exists",
    "it is filed", "already in learnings", "already in the queue",
)


def scan_novelty_claim_without_search(entries, *, text=None,
                                      tool_text=None) -> list[str]:
    """A claim that something is NEW must name the search that established it.

    Fires on a clause asserting novelty that names no search and does not
    retract. Clause-scoped with the same splitter #201 uses (B1872/B1904), so a
    grep named three sentences away does not cover a claim made here.
    """
    import re as _re
    t = _response_text(entries, text)
    if not t:
        return []
    low = t.lower()
    # B1912: a QUOTED rule is a MENTION, not a claim. This gate fired on a
    # quotation of L611 - "a finding only counts as no prior art when ALL FOUR
    # sources confirm absence" - which is a rule being cited, not a claim being
    # made. B1738 established the convention for backticks ("vocabulary shown
    # in backticks is a MENTION, not a USE"); quotation marks are where a cited
    # RULE actually lives.
    #
    # MEASURED on the session transcript, AFTER shipping: 41 firings -> 37, so
    # this clears 4. My pre-ship probe said 11 by counting quote marks within a
    # character WINDOW of the clause - proximity is not containment, and in a
    # report this quote-dense almost any clause has a quote mark near it. The
    # number was measured and it measured the wrong thing (L556).
    #
    # 4 of 41 still discriminates from the retraction-window widening REJECTED
    # at B1911, which would have cleared 0 of 39 - and it includes the firing
    # that blocked the turn. Both proposals felt equally reasonable as
    # arguments; only the measurement separated them.
    #
    # Spans are LENGTH-BOUNDED so one stray quote cannot swallow the response
    # and silence the gate - an unbounded strip is how a check goes quietly
    # vacuous (L582).
    low = _re.sub(r"`[^`]*`", " ", low)
    low = _re.sub(r'"[^"]{0,400}"', " ", low)
    low = _re.sub(r"\u201c[^\u201d]{0,400}\u201d", " ", low)
    if not _any_word(NOVELTY_CLAIMS, low):
        return []
    for clause in _re.split(r"[.;](?!\w)|\n", low):
        if not _any_word(NOVELTY_CLAIMS, clause):
            continue
        if _any_word(NOVELTY_SEARCH, clause):
            continue
        if _any_word(NOVELTY_RETRACTION, clause):
            continue
        return ["NOVELTY CLAIM WITH NO NAMED SEARCH (S6-B1909c/#201-class): "
                f"'{clause.strip()[:100]}' asserts something is new, "
                "undocumented or uncovered and names no search that "
                "established it. **I reported a duplicate-exit collapse as an "
                "'undocumented third collapse'; LEARNINGS carried it three "
                "times at 100.0pct over n=7,319.** Name the grep, the file "
                "searched or the count it returned - or say the prior art "
                "exists."]
    return []


def scan_synthetic_provenance(entries, *, text=None, tool_text=None) -> list[str]:
    """#201's provenance half: a quoted number must name its input.

    Fires when a turn states a NUMBER in measurement language while its tool
    calls show a RANDOM or hand-made generator, and the response never says
    SYNTHETIC.

    It cannot tell which number came from which call - that is not in the
    transcript. It asks a cruder and still useful question: **this turn ran a
    generator and quoted a figure as measured; say which.** Labelling costs one
    word, and the label is the thing that was missing when `2.422` was retracted.
    """
    import re as _re
    t = _response_text(entries, text)
    if not t:
        return []
    # a NUMBER, not a version or a ticket id
    if not _re.search(_DECIMAL, t):
        return []
    if not _affirms(t, QUANT_PROOF):
        return []
    # B1832 (owner ruling 2026-08-21): MECHANISM REPLACED, gate not weakened.
    #
    # The old check asked "did a generator run in the executed tool text?" - a
    # PROXY, wrong on 5 of 7 firings, every one because the only executed
    # segment holding the marker was the command run to SEARCH for it. Four
    # narrowing passes each ended narrower than the last.
    #
    # The requirement (S6-B1705e) is that a quoted number NAMES ITS INPUT. Ask
    # that directly, of the RESPONSE. Self-reference cannot trigger it -
    # searching for a marker quotes no number - and it additionally catches
    # RECALLED and FABRICATED figures, which the generator check never covered:
    # a number with no source is unverifiable whatever produced it.
    # B1832: split on SENTENCE punctuation only. The first version cut on
    # every ".", so 169.347 became "169" and "347" in separate clauses and
    # no clause ever held a decimal - the gate went silent on every
    # must-fire case for a reason unrelated to provenance. A sentence
    # period is one not flanked by digits.
    # B1858 (S6-B1847a): `(?!\d)` guarded DECIMALS and nothing else, so the
    # dot in a file EXTENSION split the clause and carried the source token
    # out of the fragment holding the number. REPRODUCED: "measured 1.5 h,
    # recorded in EXECUTION_QUEUE.md row 7" FIRED while "...in the queue
    # ledger" passed - so naming a FILE, the most natural citation there
    # is, was the one form the gate rejected, and `.csv .json .parquet
    # .txt .md .py` were dead entries in FIGURE_SOURCES. `(?!\w)` is
    # strictly stronger: a sentence boundary is followed by space or
    # end-of-text, never by a word character.
    # B1858b: the `(?<!\d)` lookbehind is REDUNDANT and HARMFUL.
    # REDUNDANT because `(?!\w)` already protects `1.2.3` and `2.422` -
    # their dots are followed by digits. HARMFUL because it refused to
    # split a sentence ENDING in a decimal, so "measured 2.422.
    # output_cfg1 is unrelated" stayed ONE clause and the figure
    # inherited a source from the NEXT sentence. Proven on 6 cases: the
    # old form failed 2, the first fix failed 1, this passes all 6.
    # Found by the fail arm; reading it would not have shown this.
    for clause in _re.split(r"[.;](?!\w)|\n", t):
        if not clause.strip():
            continue
        # B1832: allow a decimal that ENDS a sentence ("2.422.") while still
        # refusing a version ("1.2.3"). They differ by what follows the
        # trailing dot - a digit continues a version, nothing ends a
        # sentence. The first version refused both and went silent on its
        # own incident.
        if not _re.search(_DECIMAL, clause):
            continue
        if not _affirms(clause, QUANT_PROOF):
            continue
        # B1834: an ARTIFACT reference is LOCAL to the claim it supports; an
        # explicit "this is synthetic" is GLOBAL about the turn's figures.
        # Requiring the admission in the same clause fired on
        # "...a Sharpe of 2.422. This figure is SYNTHETIC." - which is exactly
        # how a person writes it.
        # B1872: word-bounded - `grade` matched `degrade`, so a figure
        # described as DEGRADED read as one naming a grading source.
        if _any_word(FIGURE_SOURCES, clause):
            continue
        if any(lbl in t for lbl in SYNTHETIC_LABEL):
            continue
        return [f"FIGURE WITH NO NAMED SOURCE (S6-B1705e/#201, mechanism "
                f"replaced B1832): {clause.strip()[:110]!r} states a decimal in "
                "measurement language and names no input. **`2.422` came from "
                "`rng.normal(1,3,30)` in my own probe and read as a "
                "measurement**; `3.637` and `169.347` were hand-built fixtures "
                "quoted the same way. Name the artifact, script or cube the "
                "number came from IN PLAIN TEXT - inline-code spans are "
                "stripped as mentions (B1738) before this gate reads the "
                "text, so a source in backticks is invisible to it - or "
                "label it SYNTHETIC where you quote it."]
    return []


# B1803: OWNER DIRECTIVE 2026-08-21 - "Always provide a count of tickets by
# groups at the end of the turn. similar to skills invoked."
#
# Same standing as the SKILLS INVOKED block: every turn, no exceptions. The
# queue is the anchor (#94) and its state was invisible between turns unless the
# owner asked for it.
#
# The count must come from scripts/queue_state.py - per DISTINCT TICKET, last
# row wins. The ledger is an APPEND LOG (853 rows for 751 tickets at B1803), so
# a row-level count is wrong by an unbounded amount and reads exactly like a
# right one (#271).
TICKET_COUNT_HEADERS = ("ticket counts", "tickets by group", "ticket state")


# B1806: LOCATING A REQUIRED BLOCK. B1732 moved from the FIRST occurrence of a
# header to the LAST, because an earlier mention shifted the window off the real
# block. **The mirror is equally true** - a LATER mention shifts it past. This
# turn listed all three skills and had all three reported missing, because the
# words "same standing as SKILLS INVOKED" appeared later in prose.
#
# Neither end is right: the block is wherever the members are. Try every
# occurrence and accept the best window.
def _best_block_window(t: str, headers, members, window: int = 900) -> dict:
    """members -> satisfied, from whichever occurrence of any header fits best.

    `members` maps a name to a predicate over the window text. Returns the
    result from the occurrence satisfying the MOST members - so a header
    mentioned in passing cannot mask the real block, from either side.
    """
    best = {k: False for k in members}
    if not t:
        return best
    idx = []
    for h in headers:
        start = 0
        while True:
            i = t.find(h, start)
            if i < 0:
                break
            idx.append(i + len(h))
            start = i + 1
    for i in sorted(idx):
        tail = t[i:i + window]
        got = {k: bool(pred(tail)) for k, pred in members.items()}
        if sum(got.values()) > sum(best.values()):
            best = got
        if all(best.values()):
            break
    return best


def scan_ticket_counts_missing(entries, *, text=None) -> list[str]:
    """Every turn ends with a ticket count across all SIX ledger classes.

    Each class name must carry a NUMBER - naming the classes without counts
    would satisfy a presence check while reporting nothing, which is the
    "any text satisfies the slot" defect #247 was written for.

    Read from the LAST header occurrence per B1732: an earlier mention - this
    docstring included - would otherwise shift the window off the real block and
    fire on a response that got it right.
    """
    import re as _re
    # B1806: keep_code=True - the counts belong in a fenced block, and the
    # default strip made this gate blind to the block it demands.
    t = _response_text(entries, text, keep_code=True)
    if not t:
        return []
    hits = [h for h in TICKET_COUNT_HEADERS if h in t]
    if not hits:
        return ["TICKET COUNTS MISSING (B1803): owner directive 2026-08-21 - "
                "every turn ends with a count of tickets by the six ledger "
                "groups, same standing as SKILLS INVOKED. Derive it with "
                "`python scripts/queue_state.py` (per distinct ticket, last row "
                "wins) - a row-level count is wrong by an unbounded amount "
                "because the ledger is an append log (#271)."]
    def _has(cls):
        c = cls.lower()
        return lambda tail: bool(
            _re.search(rf"(?<![a-z0-9_]){c}\D{{0,12}}\d", tail)
            or _re.search(rf"\d\D{{0,12}}(?<![a-z0-9_]){c}(?![a-z0-9_])", tail))

    observed = _best_block_window(
        t, TICKET_COUNT_HEADERS, {cls: _has(cls) for cls in QUEUE_CLASSES})
    return require_each(
        "TICKET COUNTS INCOMPLETE (B1803)", observed,
        why=("Owner directive 2026-08-21: all SIX classes, each with a number. "
             "A class named without a count reports nothing, and a class "
             "omitted lets silence stand in for zero."))


def scan_partial_read(entries, *, text=None, tool_text=None) -> list[str]:
    """#270: a verdict over a population needs the WHOLE population read.

    Fires when a turn states a verdict over a set AND its tool calls show only
    a truncated view of that set. **The verdict is the trigger, not the
    truncation** - truncating output to look at it is fine; truncating it and
    then deciding is the defect.

    This cannot detect every half measure, and says so: it sees TRUNCATION
    MARKERS, not comprehension. A turn that reads everything and reasons badly
    passes. It catches the specific shape that recurred - decide from a slice.
    """
    import re as _re
    t = _response_text(entries, text)
    if not t:
        return []
    # THREE DIALECTS OF THE SAME CLAIM (B1796):
    #   ticket    - a disposition word plus a population reference
    #   code/doc  - a universal quantifier with a state verb, OR a negative
    #               existential ("no other call sites", "the function is unused")
    # CLAUSE-SCOPED (B1762: proximity is not attribution). A response may plan
    # in one clause and conclude in another; only the concluding clause counts,
    # and a FORWARD-LOOKING clause is an intention rather than a verdict.
    hit = None
    for clause in _re.split(r"[;.\n]", t):
        if not clause.strip() or _re.search(_FUTURE, clause):
            continue
        vs = _verdict_hits(clause)
        pop = _re.search(r"\b(?:all|each|every)\b|\b\d+\s+of\s+\d+\b", clause)
        uni = _re.search(_UNIVERSAL, clause)
        neg = _re.search(_NEG_EXISTENTIAL, clause)
        if (vs and pop) or uni or neg:
            hit = vs[0] if vs else (uni or neg).group(0).strip()
            break
    if hit is None:
        return []
    verdicts = [hit]
    tt = _tool_text(entries, tool_text).lower()
    cuts = _sampling_hits(tt)          # B1807: source truncation, not display
    if not cuts:
        return []
    if "end to end" in t or "in full" in t or "no truncation" in t:
        return []
    return [f"VERDICT FROM A PARTIAL READ (B1794/#270): this turn states a "
            f"verdict over a population ({verdicts[0]!r}) while its tool calls "
            f"show truncation ({cuts[0]!r}). **I read 20 of 141 rows, projected "
            "the rate, and was wrong by 7x** - the sample said 10pct complete, "
            "the population is 72pct, because the first 20 were planning rows "
            "and the rest were measurements. Read the whole set, or say "
            "explicitly which part you read and do not generalise from it."]


def scan_queue_vocabulary(entries, *, rows=None, diff_text=None) -> list[str]:
    """#247 MECHANISED (B1769): every queue row added this turn uses a CLASS from
    the closed vocabulary, and every non-terminal class carries a real reason.

    `#247` shipped as JUDGMENT-ONLY because the vocabulary was unruled - building
    a gate against my own unapproved proposal would have been `#242`'s failure
    with the authority invented. **The owner ruled on 2026-08-19; this is the
    mechanism that item promised, attached the moment the ruling landed.**

    The reason check REJECTS PLACEHOLDERS. Without that the gate is satisfied by
    `_reason:_ TBD`, which is the "any text satisfies the slot" defect that
    produced 132 distinct labels across 688 rows in the first place.
    """
    import re
    import re as _re
    rows = _queue_rows_added(diff_text) if rows is None else list(rows)
    if not rows:
        return []
    bad = []
    for r in rows:
        m = re.match(r"\|\s*\*\*(S6-[A-Za-z0-9-]+)\*\*\s*\|\s*\*\*([A-Z-]+)\*\*", r)
        if not m:
            bad.append(f"{r[:60].strip()} - not in `| **id** | **CLASS** |` shape")
            continue
        tid, cls = m.group(1), m.group(2)
        if cls not in QUEUE_CLASSES:
            bad.append(f"{tid}: class {cls!r} is not one of {list(QUEUE_CLASSES)}")
            continue
        if cls in QUEUE_NEEDS_REASON:
            rm = re.search(r"_reason:_\s*(.+?)\s*(?:\*\*|\|)", r)
            reason = (rm.group(1) if rm else "").strip()
            if not reason:
                bad.append(f"{tid}: {cls} carries NO `_reason:_` - "
                           "blocked/deprioritised/not-started are different things")
            # B1769c: EXACT match on the whole reason, not a substring. The
            # first version used `ph in reason` with "-" and "N/A" in the
            # placeholder set, so ANY reason containing a hyphen read as a
            # placeholder - it blocked its own author's rows on the first live
            # run. **That is #246 (substring vs whole word), in a gate written
            # one batch after #246 was codified.** A short reason is the real
            # signal, so length carries the rest.
            elif (any(reason.lower().lstrip("*_ ").startswith(ph)
                      for ph in QUEUE_PLACEHOLDERS)
                  or len(reason.strip()) < 12):
                bad.append(f"{tid}: {cls} reason is a placeholder ({reason[:32]!r})")
    # B1769b: route through require_each - #244 caught this gate hand-rolling
    # the shape one batch after that rule was written. Each ROW is a member.
    ok = {b.split(":")[0]: False for b in bad}
    ok.update({f"row {i+1}": True for i in range(len(rows) - len(bad))})
    return require_each(
        "QUEUE VOCABULARY (B1769/#247)", ok,
        why=("; ".join(bad[:4]) +
             ("" if len(bad) <= 4 else f" (+{len(bad)-4} more)") +
             ". Owner ruling 2026-08-19: classes are "
             f"{list(QUEUE_CLASSES)}, and every non-terminal class states WHY. "
             "A placeholder reason is the same defect as a prose label."))


def scan_queue_not_updated(entries, *, rows=None, text=None,
                           diff_text=None) -> list[str]:
    """#249 (B1769): the queue is updated EVERY turn - owner directive, gated.

    THE OBJECTION THIS ANSWERS. The council's Contrarian argued that a mandatory
    per-turn gate recreates the pressure that produced 132 labels: on a turn with
    no real queue work the options become skip (blocked), invent a row
    (fabrication - the one thing CLAUDE.md forbids outright), or coin a new
    quasi-class to slide past honestly. **That is a correct read of how the
    original drift happened.**

    So the gate accepts an explicit declaration:

        NO-QUEUE-CHANGE: <reason>

    which converts an empty turn from a fabrication incentive into a RECORDED
    DECISION. The escape is deliberately visible in the response and greppable
    later, so over-use is measurable rather than invisible - the same posture as
    the `.stop_exempt` hatch, which is a disclosure, not a workaround.
    """
    rows = _queue_rows_added(diff_text) if rows is None else list(rows)
    if rows:
        return []
    t = (_assistant_text(entries) if text is None else text.lower())
    if "no-queue-change:" in t:
        after = t.split("no-queue-change:", 1)[1].strip()
        if len(after) >= 12:
            return []
        return ["NO-QUEUE-CHANGE was declared with no reason after the colon "
                "(B1769/#249). The declaration IS the record - write what made "
                "this turn queue-free."]
    return ["QUEUE NOT UPDATED THIS TURN (B1769/#249): owner directive "
            "2026-08-19 - every turn updates EXECUTION_QUEUE.md. Add the row(s) "
            "this turn's work earned, or declare `NO-QUEUE-CHANGE: <reason>` "
            "so an empty turn is a recorded decision instead of a silent gap. "
            "Do NOT invent a row to satisfy this - that is the fabrication the "
            "gate exists to avoid."]


def scan_ungated_addition(entries, *, text=None, added_rules=None) -> list[str]:
    """B1762 (#242): EACH new numbered rule names its own mechanism.

    Owner: *"If added to skill, have the applicable gates been added as per
    requirements? Do we have a requirement in the skill itself that any addition
    must get gated?"*

    MEASURED, and this is the defect: `scan_prose_only_rule` (#231) asks whether
    `verify_turn_compliance.py` or `test_unit.py` was TOUCHED THIS TURN. Touching
    either file for ANY reason silences it. In B1761 I touched both - so the gate
    went quiet while the new section's central claim ("every gate carries a
    corpus entry") shipped with **no mechanism at all**: 17 of 25 gates had no
    entry and nothing failed.

    That is any-vs-each at the FILE level - the same class as `#225`, the
    per-skill check, the runner's early returns and Phase 5's queue-only count.
    A category was touched; no member was verified. So this gate enumerates the
    numbered rules ADDED this turn and requires EACH to name its enforcing
    function, its pin test, or an explicit JUDGMENT-ONLY / PROSE-ONLY waiver.

    `added_rules` is injectable so the gate can be exercised on fixed input
    (#241); left None it reads the CHECKLIST/SKILL diff.
    """
    import re
    import subprocess

    if added_rules is None:
        added_rules = []
        try:
            for path in ("CHECKLIST.md", ".claude/skills/execution-discipline/SKILL.md"):
                d = subprocess.run(["git", "diff", "HEAD", "--unified=0", "--", path],
                                   capture_output=True, text=True, timeout=20).stdout
                added_rules += re.findall(r"^\+#{2,3} #(\d+)", d or "", re.M)
        except Exception:
            return []
    added_rules = sorted(set(str(r) for r in added_rules))
    if not added_rules:
        return []

    t = (_assistant_text(entries) if text is None else text.lower())
    if not t:
        return []

    MECH = ("scan_", "test_b", "enforced by", "pinned by", "judgment-only",
            "prose-only", "gated by")
    satisfied = {}
    for num in added_rules:
        # the rule number must appear WITH a mechanism word near it
        # B1762b: SAME CLAUSE, not a character window. A +/-220 char window let
        # ONE mechanism mention satisfy EVERY number in a short response - the
        # any-vs-each defect returning as a PROXIMITY artifact, inside the gate
        # written to close any-vs-each. Found by probing a half-gated pair, which
        # is the case a self-derived probe would never have constructed.
        near = False
        for clause in re.split(r"[.;\n]", t):
            if re.search(r"#" + re.escape(num) + r"\b", clause) and \
                    any(w in clause for w in MECH):
                near = True
                break
        satisfied[f"#{num} names its mechanism"] = near

    return require_each(
        "UNGATED ADDITION (B1762/#242)", satisfied,
        why=("A numbered rule was added this turn without naming the function or "
             "test that enforces it. #231's gate only asks whether a CODE FILE "
             "was touched - touching it for any reason silences it, which is how "
             "B1761 shipped a rule whose central claim had no mechanism (17 of 25 "
             "gates lacked a corpus entry; nothing failed). Name the enforcer per "
             "rule, or write JUDGMENT-ONLY / PROSE-ONLY and say why."))


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
    # B1947 (S6-B1783b): fifth gate routed through _response_text. Still ONE
    # at a time - 7 sites remain after this one.
    t = _response_text(entries, text)
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
    # B1783: routed through the shared helper so B1738 + B1742 are
    # INHERITED rather than re-implemented per gate.
    t = _response_text(entries, text)
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
# B1767: WHOLE-WORD markers need word boundaries; STEM markers must not have
# them. The distinction is the whole point and it cannot be inferred.
#
# This gate blocked a turn because `QUANT_CLAIMS` contains "free" and the
# response contained "chosen FREELY per row". `q in low` is a substring test, so
# a cost-claim gate fired on an adverb about editorial habit.
#
# L515 said: encode the STEM, not the conjugation - so `_MISS_STEMS` SHOULD match
# inside longer words ("fail" -> "failure", "failed"). That is correct by design.
# The defect is the opposite case: a marker that is a COMPLETE WORD whose meaning
# changes inside another word ("free" in "freely", "read" in "already").
#
# So one rule cannot cover both lists, and applying either rule blindly breaks
# half of them. STEM_LISTS is the explicit register of which is which; a list
# absent from it is treated as whole-word, because that is the safe default -
# an over-tight marker misses a real hit, an over-loose one blocks a clean turn.
STEM_LISTS = frozenset({
    "_MISS_STEMS",        # L515: fail -> failure/failed/failing, by design
    "NARRATION_STEMS",    # L509: wire -> wired/wiring/rewire, by design
    "RETRO_TRIGGERS",     # generaliz -> generalize/generalization, by design
    "MECH",               # scan_ / test_b are PREFIXES of identifiers
    "_DOC_NAMES",         # PROJECT_PLAN matches PROJECT_PLAN.md
    "INSPECTION_TOOLS",   # tool names appear inside tool-call payloads
    "OPEN_EVIDENCE",      # ditto
})



# B1773: NEGATION-AWARE EXEMPTIONS.
#
# MEASURED: `scan_unmeasured_quantity` stayed SILENT on
#   "That figure is unmeasured and was never executed."
#   "I have not measured this and did not compute it."
# Both should FIRE - the gate demands evidence a quantity was COMPUTED, and each
# sentence explicitly says it was not. **A gate demanding proof was satisfied by
# the sentence denying the proof.**
#
# Two distinct defects produced that, and they need different fixes:
#   CLASS A  word-internal - "measured" matching inside "unmeasured".
#            Word boundaries fix it. 5 cases across the marker lists.
#   CLASS B  phrase negation - "executed" IS a whole word in "never executed",
#            so boundaries cannot help. 12 cases. This is the worse one.
#
# B1767 hardened the TRIGGER side (`_marker_hits`, word-bounded) and left the
# EXEMPTION side on raw `in`. That asymmetry is the actual bug: a loose trigger
# only over-fires, while **a loose exemption lets violations through silently.**
_CLAUSE_SEP = "[.;:" + chr(92) + "n]"   # clause boundary; chr() keeps C1 happy
NEGATORS = (
    "not", "no", "never", "without", "lacks", "lacking", "absent", "failed to",
    "unable to", "didn't", "did not", "wasn't", "was not", "isn't", "is not",
    "haven't", "have not", "hasn't", "has not", "cannot", "can't", "yet to",
    "still to", "remains to", "would have", "should have", "instead of",
)


def _affirms(text: str, markers, *, window: int = 60) -> list[str]:
    """Markers that appear as whole words and are NOT negated.

    A marker counts as evidence only when at least one occurrence is
    un-negated. `window` chars of preceding context are inspected; a negator
    inside that span disqualifies THAT occurrence, not the whole marker, so
    "I did not measure X, then I measured Y" still affirms.
    """
    import re as _re
    t = text.lower()
    out = []
    for m in markers:
        ml = str(m).lower()
        if not ml:
            continue
        lead = r"(?<![a-z0-9_])" if ml[0].isalnum() else ""
        tail = r"(?![a-z0-9_])" if ml[-1].isalnum() else ""
        ok = False
        for hit in _re.finditer(lead + _re.escape(ml) + tail, t):
            # B1773b: CLAMP TO THE CLAUSE, and look BOTH WAYS. Two defects the
            # first version had, both found by running it:
            #   - backward-only missed "the benchmark was NOT executed", where
            #     the negator follows the marker
            #   - a flat 60-char window crossed a sentence boundary, so
            #     "I did not measure the old one. I measured this" was read as
            #     negated - a genuine affirmation rejected by its neighbour
            pre = t[max(0, hit.start() - window):hit.start()]
            pre = _re.split(_CLAUSE_SEP, pre)[-1]
            post = t[hit.end():hit.end() + 30]
            post = _re.split(_CLAUSE_SEP, post)[0]
            span = pre + " " + post
            if not any(_re.search(rf"(?<![a-z0-9_]){_re.escape(n)}(?![a-z0-9_])", span)
                       for n in NEGATORS):
                ok = True
                break
        if ok:
            out.append(m)
    return out


# B1774: MENTION-VS-USE ON THE EXEMPTION SIDE.
#
# MEASURED: `scan_uncosted_probe` exempts a turn when its tool text contains an
# OPEN_EVIDENCE marker ("grep", "read_csv", "sed -n"...). Those markers were
# matched against the WHOLE tool payload, so a Write whose CONTENT merely
# mentions the word satisfied the exemption:
#
#   {"name":"Write","input":{"content":"You can grep the cube to check."}}
#     -> gate EXEMPTED. No data was inspected. Writing about inspection counted
#        as inspection.
#
# B1738 fixed the mention-vs-use class on the RESPONSE side by stripping
# backticked spans. **The tool side was never stripped**, and per L528 the
# exemption is the half where looseness passes violations silently.
#
# Evidence of inspection lives in what you RAN - a command, a pattern, a path
# being read - never in a blob you authored.
_WRITTEN_FIELDS = ("content", "new_string", "old_string", "prompt", "text",
                   "description", "body", "message")

# B1774b: stripping authored FIELDS was not enough. `file_path` is itself an
# OPEN_EVIDENCE marker and EVERY Write/Edit carries one, so **writing any file
# counted as having inspected the data** - a wider hole than the content case
# that motivated the fix. Evidence of inspection can only come from a tool that
# READS; mutating calls are dropped whole.
_MUTATING_TOOLS = ("Write", "Edit", "NotebookEdit", "MultiEdit")


def _tool_invocations(tool_text: str) -> str:
    """Tool text with AUTHORED payloads removed.

    Strips the value of any field whose contents are text this turn WROTE, so
    an evidence marker can only match something actually executed.
    """
    import re as _re
    t = tool_text or ""
    for tool in _MUTATING_TOOLS:
        # drop the whole call object for a mutating tool, balanced-brace-free:
        # cut from its "name" marker to the start of the next tool call.
        t = _re.sub(rf'\{{[^{{}}]*"name"\s*:\s*"{tool}".*?(?=\{{[^{{}}]*"name"|$)',
                    " ", t, flags=_re.S)
    for f in _WRITTEN_FIELDS:
        # "field": "....."  (non-greedy, tolerant of escaped quotes)
        t = _re.sub(rf'"{f}"\s*:\s*"(?:[^"\\]|\\.)*"', f'"{f}":""', t)
        # 'field': '.....'
        t = _re.sub(rf"'{f}'\s*:\s*'(?:[^'\\]|\\.)*'", f"'{f}':''", t)
    return t

def _marker_hits(text: str, markers, *, stems: bool = False) -> list[str]:
    """Return markers present in `text`.

    `stems=False` (the default) requires WORD BOUNDARIES, so "free" no longer
    matches "freely". Boundaries are applied only at edges that are word
    characters, so markers like "correction:" and "**rule:**" still match.
    """
    import re as _re
    if stems:
        return [m for m in markers if m.lower() in text]
    out = []
    for m in markers:
        ml = m.lower()
        if not ml:
            continue
        pat = _re.escape(ml)
        if ml[0].isalnum():
            pat = r"\b" + pat
        if ml[-1].isalnum():
            pat = pat + r"\b"
        if _re.search(pat, text):
            out.append(m)
    return out


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


# B1759: STEMS, not conjugations - owner caught the third instance of the class
# L509 named. That lesson fixed NARRATION_MARKERS and left this list in the same
# broken shape. Run against the real finding text - "...which is the failure
# itself" - this list matched NOTHING while `fail` and `failure` were both
# present, so a defect stated plainly went unticketed as a miss.
#
# A marker list is a claim about how a class will be WORDED. Enumerating the
# phrasings you happen to remember is guessing; stem the root and the
# conjugations come free.
_MISS_STEMS = ("fail", "miss", "wrong", "mistake", "defect", "broken", "bug",
               "gap", "lapse", "regress", "incorrect", "unenforced",
               "never ran", "did not fire", "does not fire", "slipped")
MISS_MARKERS = tuple(
    f"{st}{suf}" for st in _MISS_STEMS
    for suf in ("", "s", "ed", "ing", "ure", "ures", "en")
) + ("owner caught", "correction:", "i should have", "retract")


# B1797d: a JUDGMENT-ONLY disposition must say which HALF it means. Detection
# may be impossible; durability usually is not. These are the phrasings that
# show the second question was actually asked.
_DURABILITY = ("durability pinned", "no detection mechanism", "detection is",
               "durability: not pinnable", "not pinnable", "cannot be pinned")


def scan_miss_capture_complete(entries, *, text=None, observed=None,
                               touched=None) -> list[str]:
    """Phase 5 wants THREE artifacts on a miss, not one (B1751 / #234)."""
    # B1786: read the FINAL block with quotes stripped (#262), and require an
    # ADMISSION context rather than a bare topic word. This gate fired on a pure
    # counting answer because the response said "defect" and "gaps" while
    # DESCRIBING tickets - a gate that fires whenever you discuss its subject is
    # detecting the topic, not the class.
    t = _response_text(entries, text)
    if not t or not _miss_hits(t):
        return []
    if observed is None:
        observed = {
            "LEARNINGS.md entry": _artifact_touched("LEARNINGS.md"),
            "CHECKLIST.md item or explicit compliance-failure citation":
                _artifact_touched("CHECKLIST.md")
                or "compliance failure against" in t,
            "EXECUTION_QUEUE.md ticket": _artifact_touched("EXECUTION_QUEUE.md"),
            # B1756 / #236 - THE FIFTH MEMBER. A fully compliant Phase-5
            # remediation could leave its CLASS unenforced: B1702 touched all
            # four artifacts, shipped ten docstring labels, and the same class
            # produced an unwired gate the next day. "Fix" meant fix the
            # INSTANCE. This member asks for the mechanism, and accepts an
            # explicit JUDGMENT-ONLY when none is possible - so the decision is
            # written down rather than skipped.
            # B1797d (#253 - harden the EXEMPTION, not just the trigger).
            # A bare "judgment-only" answers the DETECTION half and leaves the
            # DURABILITY half unasked. MEASURED this turn: I reached for it
            # while a cheap pin was available - assert the rule and its
            # diagnostic still survive in both docs. A rule written into a doc
            # can be dropped from that doc later, which is the same
            # disappearance in slow motion, and that IS mechanisable even when
            # detection is not. So the word alone no longer suffices: say which
            # half applies.
            "mechanism for the CLASS (scan_/pin test) or explicit JUDGMENT-ONLY":
                (_artifact_touched("scripts/verify_turn_compliance.py",
                                   "backtest/tests/test_unit.py")
                 if touched is None else touched)
                or ("judgment-only" in t
                    and any(m in t for m in _DURABILITY)),
        }
    return require_each(
        "PHASE-5 MISS-CAPTURE INCOMPLETE (B1751 / #234)", observed,
        why="Say 'compliance failure against item N' if no new checklist item "
            "is warranted.")


RETRO_TRIGGERS = ("new rule", "added a rule", "new checklist item", "#23",
                  "codified", "this class", "the class is now", "generalis",
                  "generaliz")
RETRO_EVIDENCE = ("retroactive", "re-scan", "rescan", "prior instances",
                  "would have caught", "swept the last", "no siblings",
                  "other instances", "same class elsewhere")


def scan_retroactive_sweep(entries, *, text=None) -> list[str]:
    """B1757 / #237: a NEW rule owes a retroactive sweep, stated in the response.

    Owner: *"when errors are remediated you are supposed to do a retroactive
    audit for similar such errors autonomously as per checklist/skill. Why
    hasn't that happened?"*

    MEASURED: the rule sits in Phase 6 and NO scan_ has ever enforced it - so it
    ran ZERO times autonomously this session. Every retroactive check happened
    because the owner asked. This is the mechanism member (#236) for the
    retroactive-sweep rule itself.
    """
    t = (_assistant_text(entries) if text is None else text.lower())
    if not t or not any(k in t for k in RETRO_TRIGGERS):
        return []
    return require_each(
        "RETROACTIVE SWEEP MISSING (B1757 / #237)",
        {"a statement of what ELSE was scanned for this class, and what it found":
             any(k in t for k in RETRO_EVIDENCE)},
        why="A rule added without sweeping for existing instances leaves the "
            "siblings the GENERALIZATION MANDATE calls non-compliant. Say what "
            "you scanned and what you found, even if the answer is none.")


def scan_compliance_is_content(entries, *, text=None) -> list[str]:
    """B1758 / #238: the compliance statement must CITE ITEMS, not merely exist.

    Owner: *"if its added in checklist and checklist compliance is mandatory as
    per skill, why the above two errors?"*

    Because CHECKLIST COMPLIANCE WAS ITSELF PROSE. `check_compliance_marker`
    asserts only `commit_made and not marker` - that a compliance BLOCK exists.
    It never asked which items were applied, so a block naming nothing passed,
    and an item with no mechanism was enforced solely by remembering to consult
    it. That is the existence-vs-content gap (B1747) at the level of the
    protocol's own compliance check.

    This requires the statement to name at least two CHECKLIST items by number
    and carry a per-item status, so "compliance" cannot be satisfied by a
    heading.
    """
    import re
    # B1941 (S6-B1783b): second gate routed through _response_text, again
    # ONE at a time - the identical line still appears at 10 other sites and
    # converting them together is the change S6-B1783b calls the one that
    # breaks several silently.
    t = _response_text(entries, text)
    if not t or "checklist compliance" not in t:
        return []
    tail = t.split("checklist compliance", 1)[1][:2500]
    items = set(re.findall(r"#(\d{2,3})", tail))
    # B1758b: build the status glyphs from code points - the C1 UNICODE gate
    # bans literal emoji/arrows in runtime code, and a heredoc had collapsed the
    # escapes into real characters.
    _GLYPHS = (chr(0x2705), chr(0x1F534), chr(0x26A0), "n/a", "done", "satisfied")
    status = sum(tail.count(m) for m in _GLYPHS)
    return require_each(
        "COMPLIANCE STATEMENT IS A HEADING, NOT A CHECK (B1758 / #238)",
        {"cites at least 2 CHECKLIST items by number": len(items) >= 2,
         "carries a per-item status": status >= 2},
        why="check_compliance_marker only asserted the block EXISTS. A block "
            "naming no items is a heading. Cite the items you applied.")


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


LAUNCH_MARKERS = ("run_phase1a.py", "run_phase1b.py")
POOL_FLAG = "--screen-pool-workers"
STALL_MARKERS = ("stall", "hang", "mtime", "not advanced", "no progress")
BULK_KILL = ("stop-process -name", "stop-process -force",
             "| stop-process", "|stop-process", "taskkill /im")


def _launch_blobs(entries) -> list[str]:
    """Commands in THIS turn that START a backtest runner. Pure.

    B1880: a launch is a COMMAND, not any tool input mentioning a runner.
    """
    import re as _re2

    out = []
    last_user = -1
    for i, e in enumerate(entries or ()):
        if e.get("type") != "user":
            continue
        c = (e.get("message") or {}).get("content")
        if (isinstance(c, str) and c.strip()) or (
                isinstance(c, list) and any(
                    isinstance(x, dict) and x.get("type") == "text" for x in c)):
            last_user = i
    for e in (entries or ())[last_user + 1:]:
        if e.get("type") != "assistant":
            continue
        for c in (e.get("message") or {}).get("content") or ():
            if not (isinstance(c, dict) and c.get("type") == "tool_use"):
                continue
            # B1880: a LAUNCH is a COMMAND that ran. The first version read
            # `json.dumps` of EVERY tool input, so WRITING a script containing
            # `run_phase1a.py` counted as launching one - and a Write tool call
            # is not a command. Read only executing tools, and only their
            # `command` field.
            if str(c.get("name") or "").lower() not in _EXECUTING_TOOLS:
                continue
            cmd = str((c.get("input") or {}).get("command") or "")
            # a heredoc BODY is data handed to an interpreter, not a command
            # that ran (L569) - applied here up front rather than after it bites
            cmd = _re2.sub(r"<<\s*'?(\w+)'?.*?^\1", " ", cmd,
                           flags=_re2.S | _re2.M)
            if any(m in cmd for m in LAUNCH_MARKERS):
                out.append(cmd)
    return out


def scan_launch_missing_pool_workers(entries, *, blobs=None) -> list[str]:
    """#185 sibling (S6-B1533a): a launch must NAME `--screen-pool-workers`.

    The default is 0 = SEQUENTIAL (L407) and the runbook has said "ALWAYS set
    it" since B1533 - in prose, enforced by nothing. The silent default cost
    ~1.5x on every run of that session. Naming it is free; discovering it
    afterwards is not.
    """
    # B1864b: the LAUNCH_MARKERS filter must apply to SUPPLIED blobs too.
    # It did not, so an injected `pytest` command was judged as a launch -
    # the injected seam behaved differently from the live path, which is
    # B1760's defect (a parameter that exists and does something else) and
    # B1811's rule (the seam travels the same pipeline). The pin's
    # must-not-fire arm caught it; reading did not.
    cand = (_launch_blobs(entries) if blobs is None else
            [b for b in blobs if any(m in b for m in LAUNCH_MARKERS)])
    if not cand:
        return []
    # B1865 (#244): this message says EVERY launch, so the check owes the
    # reader every launch. The first version reported `bad[0]` and hid the
    # rest - the any-vs-each defect, in a gate written one batch after citing
    # S6-B1762f (`require_each` existed since B1751 and I did not use it).
    return require_each(
        "LAUNCH WITHOUT AN EXPLICIT --screen-pool-workers (S6-B1533a / L407)",
        {b[:110]: (POOL_FLAG in b) for b in cand},
        why=("The default is 0 = SEQUENTIAL and the runbook has said ALWAYS "
             "SET IT since B1533; the silent default cost ~1.5x on every run "
             "of that session. Name the flag even when 0 is what you want - "
             "0 chosen is not 0 defaulted."))


def scan_monitor_without_stall_check(entries, *, blobs=None) -> list[str]:
    """#185 sibling (S6-B1555a): a monitor must be able to see a HANG.

    A monitor that only reports progress cannot distinguish a slow run from a
    dead one. THREE ticks reported a hung run as healthy because none asked
    whether the log had advanced. A periodic report that cannot report a stall
    is a liveness check that never checks liveness.
    """
    import json as _json

    arms = []
    last_user = -1
    for i, e in enumerate(entries or ()):
        if e.get("type") != "user":
            continue
        c = (e.get("message") or {}).get("content")
        if (isinstance(c, str) and c.strip()) or (
                isinstance(c, list) and any(
                    isinstance(x, dict) and x.get("type") == "text" for x in c)):
            last_user = i
    for e in (entries or ())[last_user + 1:]:
        if e.get("type") != "assistant":
            continue
        for c in (e.get("message") or {}).get("content") or ():
            # B1880: only an ARMING call carries a prompt. `CronDelete` and
            # `CronList` carry an id or nothing, so judging them as monitors
            # with no stall clause is a guaranteed false positive.
            if isinstance(c, dict) and c.get("type") == "tool_use" and \
                    "croncreate" in str(c.get("name", "")).lower():
                arms.append(_json.dumps(c.get("input", {})).lower())
    if blobs is not None:
        arms = [b.lower() for b in blobs]
    # B1866 (#246 - substring vs whole word): raw `in` made this INERT.
    # "hang" is a substring of "changed", and every unconditional monitor
    # prompt says "do not withhold because nothing changed" - so the most
    # likely phrase in the corpus silently satisfied the stall requirement.
    # Caught by the first corpus entry ever added for this gate. B1769c is
    # the same defect in this same file: a placeholder set containing "-"
    # made any reason with a hyphen read as a placeholder.
    import re as _re2

    def _has_stall(a: str) -> bool:
        return any(_re2.search(r"(?<![a-z0-9_])" + _re2.escape(m)
                               + r"(?![a-z0-9_])", a) for m in STALL_MARKERS)

    bad = [a for a in arms if not _has_stall(a)]
    if not bad:
        return []
    return ["MONITOR WITH NO STALL CHECK (S6-B1555a / L420): the prompt reports "
            "progress but cannot report a HANG, so a dead run reads as a slow "
            "one - THREE ticks called a hung run healthy. Add a stall clause: "
            "if the log mtime has not advanced while processes live, say so. "
            "Accepted words: " + ", ".join(STALL_MARKERS)]


PATTERN_CUES = ("grep", "grep -o", "grep -c", "findstr", "re.search",
                "regex", "pattern")
CONTROL_CUES = ("grep_control", "search_with_control", "known positive",
                "positive control", "verify the pattern", "control line",
                "sample line", "matches a real line")


def scan_monitor_pattern_unverified(entries, *, blobs=None) -> list[str]:
    """L576: a monitor that SEARCHES must prove its pattern can match.

    `S6-B1527a` is a launch-turn gate on the state-file PATH, and at the B1856
    launch the path matched, so it passed. **The monitor was blind anyway:**
    its fire-count grep used `/200` while the screener reports against the
    PIT-ACTIVE 185, so it would have reported "no fires" every 11 minutes on a
    run firing on 29 of 29 screen-days.

    Verifying PLUMBING is not verifying PERCEPTION. An empty grep result is
    indistinguishable from a wrong pattern (L568), and a monitor reports that
    emptiness unattended, on a schedule, as though it were news.
    """
    import json as _json

    arms = []
    for e in _since_last_user(entries):
        if not isinstance(e, dict) or e.get("type") != "assistant":
            continue
        for c in (e.get("message") or {}).get("content") or ():
            if (isinstance(c, dict) and c.get("type") == "tool_use"
                    and "croncreate" in str(c.get("name", "")).lower()):
                arms.append(_json.dumps(c.get("input", {})).lower())
    if blobs is not None:
        arms = [b.lower() for b in blobs]
    searching = [a for a in arms if any(cue in a for cue in PATTERN_CUES)]
    if not searching:
        return []
    # B1887 (#244): this message states a universal rule, so the check owes
    # the reader every offending monitor. Third time this pair has fired on a
    # gate of mine; B1865 fixed the same two on scan_launch_missing_pool_workers.
    return require_each(
        "MONITOR SEARCHES WITHOUT A POSITIVE CONTROL (L576 / S6-B1527a)",
        {a[:110]: any(cue in a for cue in CONTROL_CUES) for a in searching},
        why=("A monitor that greps must say how it knows the pattern can "
             "match. MEASURED: one grepped `/200` while the screener reports "
             "against the PIT-ACTIVE 185, and would have reported 'no fires' "
             "on a run firing on 29 of 29 screen-days. Verifying the "
             "state-file PATH is not verifying PERCEPTION. Name a known "
             "positive - a real line the pattern must match - or use "
             "`scripts/grep_control.py`."))


def scan_bare_python_launch(entries, *, cmds=None) -> list[str]:
    """B1877 / L573: a launch must name its INTERPRETER, never a bare `python`.

    MEASURED with one variable changed: `subprocess.run(["python", ...])` from
    inside the venv resolves to the SYSTEM interpreter, keeps 2 of 33
    producers and fires ZERO trades, while `sys.executable` keeps 3 of 33 and
    fires 10. Same env, same flags, same cwd, deterministic.

    That confound produced a P0 conclusion reported as causally confirmed -
    that demand pruning silently zeroed runs - which one-variable tests then
    refuted. **A run on the wrong interpreter does not crash; it produces a
    clean, empty, exit-0 cube.**

    Fires only on a SUBPROCESS launch written in a script, which is the shape
    that hides the interpreter. A bash command line resolves `python` through
    PATH and gets the venv, so it is not this defect.
    """
    import re as _re

    raw = _executed_text(entries) if cmds is None else " ".join(cmds)
    # B1878: applying L569 BEFORE it bites. A gate that scans executed text is
    # proven by fixtures containing exactly what it detects, so it blocks its
    # own author unless fixture context is excluded. A heredoc BODY is data
    # handed to an interpreter, not a command that ran - same remedy as
    # scan_bulk_process_kill. L570: a cited rule is not an applied one.
    txt = _re.sub(r"<<\s*'?(\w+)'?.*?^\1", " ", raw, flags=_re.S | _re.M)
    bad = []
    for m in _re.finditer(r"""subprocess\.(?:run|Popen|check_output|call)\(\s*\[?\s*["']python["']""",
                          txt):
        bad.append(txt[max(0, m.start() - 20):m.start() + 60])
    if not bad:
        return []
    return ["BARE `python` IN A SUBPROCESS LAUNCH (S6-B1877 / L573): this "
            "resolves to the SYSTEM interpreter, not the venv. MEASURED: "
            "2 of 33 producers kept and ZERO trades, against 3 of 33 and 10 "
            "trades under `sys.executable` - same env, same flags, same cwd. "
            "A run on the wrong interpreter does not crash, it produces a "
            "clean empty exit-0 cube. Use `sys.executable`. Offending: "
            + bad[0][:120]]


def scan_bulk_process_kill(entries, *, cmds=None) -> list[str]:
    import re as _re

    """S6-B1534e / L411: kill VERIFIED PIDs, never sweep by name.

    A force-sweep over every python process is a change to machine state, not
    neutral cleanup - it takes out pytest, other sessions and unrelated work
    along with the target. Killing by PID after confirming the command line is
    the same effort and is reversible in intent.
    """
    # B1868 (THE CLASS FIX): B1867 stripped heredoc bodies and the gate fired
    # again next turn on `python -c "...Stop-Process -Force..."` - a `-c`
    # ARGUMENT, not a heredoc. That is L567 - a ticket names one guard; the
    # expression has two - written by me two batches earlier.
    #
    # Stop asking "is this text quoted?" and ask "could this command have run
    # at all?". `Stop-Process` is a PowerShell CMDLET and cannot run from
    # bash, so it only counts in a PowerShell tool call. Every fixture is
    # written through Bash; the real kill at B1861 went through PowerShell.
    # `taskkill` runs from either shell and keeps the any-tool treatment.
    if cmds is None:
        ps, anysh = [], []
        for d in entries or ():
            if not isinstance(d, dict) or d.get("type") != "assistant":
                continue
            for blk in (d.get("message") or {}).get("content") or ():
                if not isinstance(blk, dict) or blk.get("type") != "tool_use":
                    continue
                nm = str(blk.get("name") or "").lower()
                cmd = str((blk.get("input") or {}).get("command") or "")
                if "powershell" in nm:
                    ps.append(cmd)
                if nm in _EXECUTING_TOOLS:
                    anysh.append(cmd)
        raw = " ".join(ps)
        anyshell = " ".join(anysh)
    else:
        raw = anyshell = " ".join(cmds)
    # B1867: a HEREDOC BODY is data handed to an interpreter, not a command
    # that ran. This gate blocked the very turn that shipped it, on the probe
    # `cmds=["Get-Process python | Stop-Process -Force"]` written inside a
    # `python - <<'PY'` block - while the only process actually killed that
    # turn went by verified PID. Instance 10 of the self-reference family:
    # the fixtures that PROVE a text-scanning gate works are, by
    # construction, the exact text it detects.
    #
    # NARROW BY INTENT. The general question - "heredoc-written fixtures read
    # as Bash execution" - is S6-B1817g and is BLOCKED on an owner ruling.
    # This strips heredoc bodies for THIS gate only.
    def _strip_heredocs(x: str) -> str:
        return _re.sub(r"<<\s*'?(\w+)'?.*?^\1", " ", x, flags=_re.S | _re.M)

    txt = _strip_heredocs(raw).lower()
    txt_any = _strip_heredocs(anyshell).lower()
    hits = [m for m in BULK_KILL if m != "taskkill /im" and m in txt]
    if "taskkill /im" in txt_any:
        hits.append("taskkill /im")
    if not hits:
        return []
    return ["BULK PROCESS KILL (S6-B1534e / L411): " + ", ".join(hits) +
            ". A force-sweep by NAME is a change to machine state, not neutral "
            "cleanup - it takes out pytest, other sessions and unrelated work. "
            "Get the PID, VERIFY its command line, then Stop-Process -Id."]


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
    # B1844 (S6-B1841c): a duplicated unreachable `return None` sat here. Same
    # shape as the shadowed-definition class (B1795) - a duplicate makes the
    # survivor ambiguous to the next reader.
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
                scan_false_skill_status, scan_miss_capture_complete,
                scan_retroactive_sweep, scan_compliance_is_content,
                scan_ungated_addition, scan_shell_substitution,
                scan_queue_vocabulary, scan_queue_not_updated,
                scan_unverified_count, scan_partial_distribution,
                scan_partial_read, scan_row_vs_ticket,
                scan_novelty_claim_without_search,
                scan_synthetic_provenance,
                scan_ticket_counts_missing,
                # B1864 - WIRED, not merely defined. B1751: scan_false_skill_status
                # was DEFINED and never wired, and that is instance 5 of any-vs-each.
                scan_launch_missing_pool_workers,
                scan_monitor_without_stall_check,
                scan_bulk_process_kill,
                scan_bare_python_launch,
                scan_monitor_pattern_unverified):
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
