"""scripts/inject_tier3_discipline.py (B1355, Council 373) -- UserPromptSubmit
hook. Fires at the START of EVERY turn and injects the Tier-3 (judgment)
execution-discipline protocol into context, so it is MECHANICALLY present every
turn instead of relying on a prior /execution-discipline invocation.

Owner directive 2026-07-23: "Tier 3 insert hook to make it mechanical." The
mechanical layer (Stop hook + pre-commit preflight) already enforces the
Tier-1/2 items (pyramid, queue, doc-sweep, compliance marker). This closes the
Tier-3 gap: the ~24KB skill previously loaded only when invoked, so its judgment
gates decayed across turns (the dashboard-error streak, L218). This hook keeps
the judgment gates in front of me every turn. It does NOT (and cannot) fully
mechanize judgment -- it guarantees PRESENCE + the concrete, checkable gates.

UserPromptSubmit stdout is injected into the turn context. Fail-open: any error
prints nothing and exits 0 (a broken hook must never block a turn).
"""
from __future__ import annotations

import pathlib
import sys

TIER3 = """\
[EXECUTION-DISCIPLINE TIER-3 -- auto-injected every turn; apply UNPROMPTED. \
Full skill: .claude/skills/execution-discipline/SKILL.md]
- SCOPE LEDGER (Phase 1): enumerate every in-scope item now; each ends the turn \
with a terminal disposition (DONE/DEFERRED-ticket/N/A/BLOCKED). A row with no \
disposition is a silent miss.
- PRE-FLIGHT (Phase 2): a visible CHECKLIST block before EACH recommendation; \
any red -> HALT and report, do not state the rec.
- AUDIT DEPTH (Phase 4): code-verified not doc-verified; inspect the HAPPY-PATH \
OUTPUT ARTIFACT. For a rendered deliverable (dashboard/report/HTML) that means \
LOAD it -> scripts/verify_dashboard.py --dir <d> --url <deployed> (CHECKLIST \
#163). "Generated the data" != "the deliverable works".
- TRUTH STANDARD: tag every factual claim EXECUTED / READ / DERIVED / UNVERIFIED. \
Never say done/live/ready/fixed/verified without evidence RUN THIS TURN. \
Re-derive every count by running code. "I don't know" / "it failed" are \
compliant answers.
- MISS-CAPTURE (Phase 5): any miss or OWNER CORRECTION -> LEARNINGS entry + \
fix-or-ticket SAME TURN (owner corrections are always misses).
- GENERALIZATION MANDATE: fix the CLASS not the instance; state the class; \
one-off only with explicit owner approval.
- CONFIRM-BEFORE-REPLICATING: to copy an existing template/artifact/format, \
enumerate ALL candidates + confirm the exact one before building; after any \
correction, restart with full enumeration (L217).
- END-OF-TURN SWEEP (Phase 6): doc-sync + EXECUTION_QUEUE entry + compliance \
statement (Stop hook + pre-commit enforce the mechanical half).
"""


# MEASURED B3102 (S6-B3097b delivery, three hook firings): 15,395 and 11,829
# chars were persisted to a file with only a 2 KB preview in context; 8,890
# chars reached context INLINE. The harness limit is in (8,890, 11,829], so
# the budget is a measured-inline value with margin - the first CHOSEN value,
# 16,000, did not fit. Banners count toward the same limit (see main).
HOOK_BUDGET = 9000   # chars, whole hook output
HEAD_BUDGET = 2000    # chars the harness ALWAYS shows (its preview) - essentials first


def _section(body: str, title: str) -> str:
    i = body.find(title)
    if i < 0:
        return ""
    j = body.find("\n## ", i + len(title))
    return body[i:j if j > 0 else len(body)]


def compact_index(body: str, budget: int = HOOK_BUDGET) -> str:
    """S6-B3097b (B3098): what the hook injects instead of the whole skill.

    MEASURED B3097: at ~377 KB the full skill is persisted to a file and only a
    2 KB preview reaches context, so every rule past the first 2 KB was
    under-delivered while the hook reported success (L871). The HEAD - invoke
    instruction, brevity rule, truth-standard core - fits HEAD_BUDGET, the part
    the harness always shows. The tripwire index follows: the first column of
    EVERY row, GENERATED from SKILL.md, so a new row appears without anyone
    editing this hook. Pure ASCII; capped at HOOK_BUDGET with the dropped count
    stated (a silent cap reads as complete)."""
    import re as _re
    head = [
        "[EXECUTION-DISCIPLINE - COMPACT INDEX (S6-B3097b). The full skill is "
        ".claude/skills/execution-discipline/SKILL.md and ONLY a Skill call "
        "delivers it - this index is not the skill. It must be in context on "
        "every working turn: INVOKE Skill(execution-discipline) at session start "
        "and again after EVERY compaction (L871). Apply it UNPROMPTED.]",
        "- BREVITY (owner 2026-09-10): lead with the answer; ~300 words before the "
        "end blocks; tables over prose; plain words, every quant term glossed.",
        "- TRUTH: every claim is EXECUTED / READ / DERIVED or labelled UNVERIFIED; "
        "sub-agent output is UNVERIFIED until spot-checked; counts are re-derived "
        "this turn; DONE needs pyramid GREEN + commit hash, FIXED needs a passing "
        "pin; a verdict names its N of M; retract a false claim visibly, then Phase 5.",
        "- END BLOCKS: SKILLS INVOKED; ticket counts table (6 classes + delta, from "
        "scripts/queue_state.py); CHECKLIST compliance citing items with status.",
    ]
    trip = _section(body, "## TRIPWIRE TABLE")
    rows = [ln for ln in trip.splitlines()
            if ln.startswith("| ") and not ln.startswith("| If you are about to")
            and not _re.match(r"^\|\s*-{3}", ln)]
    firsts = [ln.split(" | ")[0].lstrip("| ").strip() for ln in rows]
    out = "\n".join(head) + "\n[TRIPWIRES - if you are about to... (full check "
    out += "per row in the skill)]\n"
    shown = 0
    for f in firsts:
        line = "- " + f + "\n"
        if len(out) + len(line) > budget - 120:
            break
        out += line
        shown += 1
    if shown < len(firsts):
        out += (f"[{len(firsts) - shown} more tripwire rows not shown - "
                "invoke the skill]\n")
    return out.encode("ascii", "replace").decode("ascii")


def undelivered_landings_banner() -> str:
    """B2520 (owner ruling 2026-09-01, "share results with me"): every cube
    whose landing has not yet been reported to the owner is printed at the
    TOP of the next turn, before the skill - so the reader meets the result
    before any other work, and the Stop hook (scan_undelivered_landing) has a
    reader who already knows what it will ask for. Pure ASCII; never raises;
    empty when nothing is pending or the record cannot be read."""
    try:
        here = str(pathlib.Path(__file__).resolve().parent)
        if here not in sys.path:
            sys.path.insert(0, here)
        import postconfig_landing as _pl
        pend = _pl.undelivered()
    except Exception:
        return ""
    if not pend:
        return ""
    lines = ["[UNDELIVERED LANDINGS (B2520) - report each as `LANDING REPORT: "
             "<cube>` in this turn's final response; the Stop hook blocks until "
             "you do]"]
    for ev in pend:
        blocking = ev.get("blocking") or []
        finds = ev.get("findings") or []
        lines.append(
            f"  {ev.get('cube')}: landed {ev.get('ts')} via {ev.get('source')}; "
            f"battery_exit {ev.get('battery_exit')}; blocking "
            f"{', '.join(blocking) if blocking else 'none'}; findings "
            f"{len(finds)}; committed {ev.get('committed')}; pushed "
            f"{ev.get('pushed')}")
        # B2211: never truncate a finding - the measured numbers sit at
        # the END of a battery line, so a cut removes exactly the numbers
        for f in finds:
            lines.append("    - " + str(f))
    return "\n".join(lines).encode("ascii", "replace").decode("ascii") + "\n\n"


def chain_halts_banner() -> str:
    """B2577: every serial-chain HALT not yet reported to the owner, printed
    at the top of the next turn beside the landings (the Stop hook's
    scan_chain_halt asks for `CHAIN HALT REPORT: <wave>`). Never raises."""
    try:
        here = str(pathlib.Path(__file__).resolve().parent)
        if here not in sys.path:
            sys.path.insert(0, here)
        import run_serial_chain as _rsc
        pend = _rsc.undelivered_halts()
    except Exception:
        return ""
    if not pend:
        return ""
    lines = ["[CHAIN HALTS NOT REPORTED (B2577) - report each as `CHAIN HALT "
             "REPORT: <wave>` in this turn's final response; the Stop hook "
             "blocks until you do]"]
    for ev in pend:
        lines.append(f"  {ev.get('wave')}: {ev.get('ts')} - {ev.get('reason')}; "
                     f"{len(ev.get('remaining') or [])} spec(s) not launched")
    return "\n".join(lines).encode("ascii", "replace").decode("ascii") + "\n\n"


def main() -> int:
    try:
        # Consume stdin (the hook payload) so the pipe closes cleanly; we don't
        # need its content -- the injection is unconditional every turn.
        if not sys.stdin.isatty():
            sys.stdin.read()
        # SUPERSEDED 2026-09-24 by the owner's approval of S6-B3097b option (a):
        # at ~377 KB the harness persists this output to a file and shows a
        # 2 KB preview, so emitting the whole file delivered 2 KB (MEASURED
        # B3097, L871) while reporting success. The hook now emits a COMPACT
        # INDEX with the essentials inside that preview, and the Skill call is
        # the only delivery of the full file. The directive's reasoning below
        # is kept: its goal - the protocol present every turn - is unchanged.
        # B1743 OWNER DIRECTIVE: emit the FULL SKILL, not a 12-bullet summary.
        #
        # "There is no logic if a turn proceeds without fully invoking it."
        # Correct. The summary made the full protocol depend on my REMEMBERING to
        # invoke it - and across this session I forgot on the turns where context
        # was tightest, which are exactly the turns that most needed it. A gate at
        # turn-END (#229) blocks too late: the work is already done.
        #
        # This hook already runs on EVERY prompt. Emitting the whole file makes
        # the protocol unconditional and removes the decision entirely.
        # Falls back to the summary only if the file cannot be read - the skill
        # missing is not a reason to emit nothing.
        _skill = (pathlib.Path(__file__).resolve().parent.parent
                  / ".claude" / "skills" / "execution-discipline" / "SKILL.md")
        try:
            body = _skill.read_text(encoding="utf-8")
            # S6-B3097b (B3098): a COMPACT INDEX, not the whole file - at ~377 KB
            # the harness showed only a 2 KB preview of it (L871).
            _banners = undelivered_landings_banner() + chain_halts_banner()
            # the banners print first and count toward the same inline limit
            # (the head is always emitted, whatever budget is left)
            out = _banners + compact_index(
                body, budget=max(0, HOOK_BUDGET - len(_banners)))
            # B1744 ROOT CAUSE. B1743 shipped and SILENTLY did nothing for two
            # sessions, including across a restart. PROVEN: this hook writes to a
            # cp1252 stdout on Windows, SKILL.md contains U+2192 and U+2264 and
            # em-dashes, so  raised UnicodeEncodeError -
            # "charmap codec cannot encode character u2192 at position 1695" -
            # and MY OWN except clause swallowed it back to the 12-bullet
            # summary. The fallback I added "so a missing skill never blocks a
            # turn" is what hid the failure.
            #
            # Write BYTES through the buffer, bypassing the console codec
            # entirely. Never re-encode to whatever cp the console happens to be.
            buf = getattr(sys.stdout, "buffer", None)
            if buf is not None:
                buf.write(out.encode("utf-8", "replace"))
                buf.flush()
            else:
                sys.stdout.write(out.encode("utf-8", "replace").decode("utf-8"))
        except Exception:
            # Fallback retained, but it is now a REAL last resort rather than the
            # everyday path. TIER3 is pure ASCII so it always encodes.
            sys.stdout.write(undelivered_landings_banner() + chain_halts_banner() + TIER3)
    except Exception:
        pass  # fail-open: never block a turn
    return 0


if __name__ == "__main__":
    sys.exit(main())
