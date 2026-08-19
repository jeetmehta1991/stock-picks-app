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


def main() -> int:
    try:
        # Consume stdin (the hook payload) so the pipe closes cleanly; we don't
        # need its content -- the injection is unconditional every turn.
        if not sys.stdin.isatty():
            sys.stdin.read()
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
            sys.stdout.write("[EXECUTION-DISCIPLINE - FULL SKILL, auto-injected "
                             "every turn (B1743). Apply UNPROMPTED.]" + chr(10)
                             + body)
        except Exception:
            sys.stdout.write(TIER3)
    except Exception:
        pass  # fail-open: never block a turn
    return 0


if __name__ == "__main__":
    sys.exit(main())
