"""S6-B3139ae (owner ruling 2026-10-06, packet row 21 'approve'): refuse, BEFORE
it runs, a Bash command that feeds a heredoc body carrying a backslash pair to
an interpreter (python / py / node / perl / ruby). A git commit or tag message
heredoc is exempt. Wired as a PreToolUse hook on Bash in .claude/settings.json.

Why a refusal and not only the Stop-time scan (S6-B3138a): the scan runs at
turn close, after the command has executed, so it records the hazard and
cannot prevent it. Measured over this session's transcript at B3139q-r48:
42 such commands ran after the scan shipped (2026-09-30T07:32Z), 23 of them on
2026-10-06 alone.

ONE definition: the decisions are verify_turn_compliance.heredoc_escape_hits
and dash_c_escape_hits, the same functions the Stop-time scan calls, so the
refusal and the record can never disagree about what counts.

Scope, as ruled: heredoc bodies (packet row 21, 2026-10-06) AND, since
S6-B3144 (owner ruling 2026-10-13, "Approve all other recommendations"),
the double-quoted `python -c "..."` sibling (dash_c_escape_hits,
S6-B3139v). And since S6-B3268 (owner ruling (a), 2026-10-22, 'Addendum
Approve all your recommendations'): --help or -h on a repo script that
builds no argument parser, for Bash AND PowerShell, through the Stop-time
scan's own help_on_parserless_hits - such a script runs main() on any
argument (L947 rewrote a committed census). It reads imports, not parses,
so a parser built in a helper module would be refused too: MEASURED before
wiring, 0 of 477 scripts under scripts/ do that (S6-B3279's dependency).
MEASURED before the -c refusal shipped: 157 Bash commands in one session's
transcript ran such a payload (the last at 2026-10-14T02:11Z), and the Stop-time record raised none after
its first report - its one-report key is the hit text, identical for every
payload with the same escape set. A refusal before running closes that.

S6-B3327 (B3139q-r131, L967; executed on the owner's word 2026-10-27, "No
approval needed (5) / Proceed fable mode execute now"): a RUN of two or more
backslashes anywhere in a Bash command, through verify_turn_compliance's
backslash_run_hits. MEASURED: this tool halves every such run before bash
parses the command, inside single quotes and quoted heredoc bodies alike,
while a lone backslash before another character arrives unchanged - so the
S6-B3144 message's "a single-quoted -c payload ... is fine" held only for a
payload without a run, and is corrected. A git commit or tag message heredoc
stays exempt. The rule runs after the two above, so their refusals keep
their own messages. Bash only: the PowerShell tool's transport is unmeasured.

B3139q-r216 (owner 'except for new strategy runs. Address and impletement all
open tickets. Test extensively. do not invoke fable mode', sent
2026-11-16T08:22:37Z, read as the ruling word on each ticket's recommendation
(a)) - three more refusals, each decided in verify_turn_compliance, where the
Stop-time scans live, so a refusal and a record cannot disagree:

  S6-B3377 (a): a Bash, PowerShell or Monitor call while the transcript's last
    compaction is NEWER than its last Skill(execution-discipline) load
    (skill_reload_owed - the same compaction marker and load forms as the
    close-time scan_discipline_not_loaded's _skill_context_text; L871, L998
    and its four addenda: five instances in seventeen days, the longest
    7 h 42 min and six commits, every one inside a long turn and invisible
    to the close-time gate until a close). The check reads the transcript
    INCREMENTALLY - a state file in the OS temp dir, one per transcript,
    keeps the byte offset and the newest compaction and load - MEASURED on
    the 1.4 GB live transcript: 0.39 s for the first read, 0.022 s after.
    No transcript path in the payload, or an unreadable one, allows: the
    close-time gate stays the backstop. Runs FIRST: nothing else should run
    before the reload.
  S6-B3391 (a): (1) a TOP-LEVEL cd / pushd / chdir (Bash) or cd / chdir / sl /
    Set-Location / Push-Location / pushd (PowerShell) whose target is not the
    repository root (cwd_move_hits; #330, L1005: one `cd scripts &&` moved
    the session's directory and every relative hook path with it). A ( )
    subshell, a $( ) substitution, a quoted string and a heredoc body are not
    top level. (2) The Monitor tool's command is read as a Bash command - the
    settings.json matcher carries Monitor beside Bash and PowerShell.
  S6-B3379 (a): a Bash or Monitor `python -` whose stdin is EMPTY - an empty
    heredoc body or /dev/null (python_stdin_hang_hits; L999, #329: either
    input enters the Python 3.14 interactive REPL, whose Windows console
    layer raises OSError on a non-console handle and retries forever,
    15.4 MB of tracebacks in about 5 s from an empty heredoc, 119.3 MB in
    about 2.5 min from /dev/null, silent once stderr is discarded).

Failure mode: an internal error exits 1, which Claude Code treats as a
NON-blocking hook error, so a broken guard lets commands through (fail-open)
rather than refusing every Bash call. The pin runs this file as a subprocess
on its must-fire and must-quiet corpus so a break shows in the pyramid. A
MISSING guard is the opposite case: python exits 2 when it cannot open the
script, and 2 BLOCKS - MEASURED 2026-10-31 (L1005): one `cd scripts &&`
moved the session's working directory, this hook's then-relative path no
longer resolved, and every Bash and PowerShell call was refused for 26
minutes. Every hook command in .claude/settings.json is therefore anchored
on the project root (S6-B3388).

Protocol (Claude Code PreToolUse): the payload arrives as JSON on stdin with
tool_name and tool_input; exit 2 blocks the call and returns stderr to the
model; exit 0 allows it.
"""
import json
import sys
from pathlib import Path


def decide(payload: dict, root=None, state_dir=None) -> tuple[int, str]:
    """(exit code, stderr message) for one PreToolUse payload. `root` is
    the test seam for the repository root (the --help check's repo-file read
    and the cwd rule's target comparison; None: the repo); `state_dir` is the
    skill-reload check's state-file seam (None: the OS temp dir)."""
    tool = str(payload.get("tool_name") or "")
    if tool not in ("Bash", "PowerShell", "Monitor"):
        return 0, ""
    # S6-B3391 (a)(2): the Monitor tool runs its command through Bash
    shell = "PowerShell" if tool == "PowerShell" else "Bash"
    cmd = str((payload.get("tool_input") or {}).get("command") or "")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from verify_turn_compliance import (cwd_move_hits,
                                        python_stdin_hang_hits,
                                        skill_reload_owed)
    # S6-B3377 (a): first - nothing runs before the reload
    owed = skill_reload_owed(payload, state_dir)
    if owed:
        return 2, ("REFUSED BEFORE RUNNING (S6-B3377 / #229 / L998): "
                   f"{owed}. The compacted copy of the skill is a preview "
                   "(L871): call Skill(execution-discipline) first - this "
                   "check reads the transcript, so the reload clears it on "
                   "the next call. No shell or Monitor command runs until "
                   "then.")
    # S6-B3391 (a)(1): a top-level directory move off the repository root
    moves = cwd_move_hits(cmd, shell, root)
    if moves:
        return 2, ("REFUSED BEFORE RUNNING (S6-B3391 / #330 / L1005): "
                   f"{len(moves)} top-level change(s) of the session's working "
                   f"directory off the repository root - first: {moves[0]!r}. "
                   "The directory persists between tool calls and every hook "
                   "runs from it. Use an absolute path, `git -C <dir>`, or a "
                   "subshell `( cd <dir> && ... )`; a cd to the repository "
                   "root is the one top-level cd allowed.")
    if "-h" in cmd:                    # --help contains it too
        from verify_turn_compliance import (_HELP_PARSERLESS_HEAD,
                                            help_on_parserless_hits)
        helps = help_on_parserless_hits(cmd, root=root)
        if helps:
            # the Stop-time scan's head + the hit's repr: its one-report
            # rule then reads this refused command as reported, not run
            return 2, ("REFUSED BEFORE RUNNING (S6-B3268 / #327 / L947): "
                       f"{_HELP_PARSERLESS_HEAD} - {len(helps)} command(s) "
                       f"would run --help or -h on a repo script that builds "
                       f"no argument parser - first: {helps[0]!r}. Such a "
                       "script runs main() on any "
                       "argument and may write its artifact (L947: --help "
                       "rewrote a committed census). Read the script's source "
                       "to learn its flags; a script that imports argparse, "
                       "optparse, click, typer or docopt, or compares against "
                       "a --help literal, is not refused.")
    if shell != "Bash":
        return 0, ""
    # S6-B3379 (a): `python -` on an empty heredoc body or /dev/null
    hangs = (python_stdin_hang_hits(cmd)
             if ("<<" in cmd or "/dev/null" in cmd) else [])
    if hangs:
        return 2, ("REFUSED BEFORE RUNNING (S6-B3379 / #329 / L999): "
                   f"{len(hangs)} `python -` call(s) with EMPTY stdin - first: "
                   f"{hangs[0]!r}. An empty heredoc body or /dev/null puts "
                   "the interpreter in the interactive REPL, which on this "
                   "machine retries an OSError forever (L999: 119.3 MB of "
                   "tracebacks in 2.5 min, silent once stderr is discarded). "
                   "Give `python -` a program on stdin, or run a FILE.")
    if "<<" not in cmd and "-c" not in cmd and "\\\\" not in cmd:
        return 0, ""
    from verify_turn_compliance import (backslash_run_hits,
                                        dash_c_escape_hits,
                                        heredoc_escape_hits)
    hits = heredoc_escape_hits(cmd) if "<<" in cmd else []
    if hits:
        return 2, ("REFUSED BEFORE RUNNING (S6-B3139ae / #259 / L885): "
                   f"{len(hits)} heredoc body(ies) fed to an interpreter carry a "
                   f"backslash pair - first: {hits[0]!r}. A backslash pair can "
                   "arrive altered through the shell and tool layers. Write the "
                   "script with the Write tool and run the FILE. A heredoc with no "
                   "backslash is fine, and a git commit or tag message heredoc is "
                   "exempt.")
    dash = dash_c_escape_hits(cmd) if "-c" in cmd else []
    if dash:
        # S6-B3327 corrected the last sentence: a single-quoted payload is
        # fine only without a backslash RUN, which the transport halves
        return 2, ("REFUSED BEFORE RUNNING (S6-B3144 / #259 / L893): "
                   f"{len(dash)} double-quoted python -c payload(s) carry a "
                   f"backslash pair the shell does not consume - first: "
                   f"{dash[0]!r}. Inside double quotes bash leaves such a "
                   "pair for the interpreter, so what runs depends on two "
                   "quoting layers at once. Write the script with the Write "
                   "tool and run the FILE. A single-quoted -c payload with no "
                   "run of two or more backslashes, or a pair bash consumes "
                   "inside double quotes (before a quote, a dollar or a "
                   "backtick), is fine.")
    # S6-B3327 (B3139q-r131, L967): last, so the two rules above keep their
    # own refusals and messages for the commands they already cover
    runs = backslash_run_hits(cmd) if "\\\\" in cmd else []
    if runs:
        return 2, ("REFUSED BEFORE RUNNING (S6-B3327 / #259 / L967): "
                   f"{len(runs)} run(s) of two or more backslashes - first: "
                   f"{runs[0]!r}. This tool halves every backslash run before "
                   "bash reads the command (MEASURED: a doubled backslash in "
                   "single quotes reached the program as one, and four as "
                   "two), so no quoting delivers it as written. Write a single "
                   "backslash where one is meant, or write the payload with "
                   "the Write tool and run the FILE. A lone backslash before "
                   "another character arrives unchanged, and a git commit or "
                   "tag message heredoc is exempt.")
    return 0, ""


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        rc, msg = decide(payload if isinstance(payload, dict) else {})
    except Exception as exc:  # fail-open, visibly: see the module docstring
        print(f"pretooluse_heredoc_guard error (not blocking): {exc!r}",
              file=sys.stderr)
        return 1
    if msg:
        print(msg, file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
