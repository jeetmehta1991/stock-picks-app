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

Failure mode: an internal error exits 1, which Claude Code treats as a
NON-blocking hook error, so a broken guard lets commands through (fail-open)
rather than refusing every Bash call. The pin runs this file as a subprocess
on its must-fire and must-quiet corpus so a break shows in the pyramid.

Protocol (Claude Code PreToolUse): the payload arrives as JSON on stdin with
tool_name and tool_input; exit 2 blocks the call and returns stderr to the
model; exit 0 allows it.
"""
import json
import sys
from pathlib import Path


def decide(payload: dict, root=None) -> tuple[int, str]:
    """(exit code, stderr message) for one PreToolUse payload. `root` is
    the test seam for the --help check's repo-file read (None: the repo)."""
    tool = str(payload.get("tool_name") or "")
    if tool not in ("Bash", "PowerShell"):
        return 0, ""
    cmd = str((payload.get("tool_input") or {}).get("command") or "")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
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
    if tool != "Bash" or ("<<" not in cmd and "-c" not in cmd
                          and "\\\\" not in cmd):
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
