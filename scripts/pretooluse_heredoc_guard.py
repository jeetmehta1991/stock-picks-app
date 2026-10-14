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
S6-B3139v). MEASURED before it shipped: 157 Bash commands in one session's
transcript ran such a payload (the last at 2026-10-14T02:11Z), and the Stop-time record raised none after
its first report - its one-report key is the hit text, identical for every
payload with the same escape set. A refusal before running closes that.

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


def decide(payload: dict) -> tuple[int, str]:
    """(exit code, stderr message) for one PreToolUse payload."""
    if str(payload.get("tool_name") or "") != "Bash":
        return 0, ""
    cmd = str((payload.get("tool_input") or {}).get("command") or "")
    if "<<" not in cmd and "-c" not in cmd:
        return 0, ""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from verify_turn_compliance import dash_c_escape_hits, heredoc_escape_hits
    hits = heredoc_escape_hits(cmd) if "<<" in cmd else []
    if not hits:
        dash = dash_c_escape_hits(cmd) if "-c" in cmd else []
        if not dash:
            return 0, ""
        return 2, ("REFUSED BEFORE RUNNING (S6-B3144 / #259 / L893): "
                   f"{len(dash)} double-quoted python -c payload(s) carry a "
                   f"backslash pair the shell does not consume - first: "
                   f"{dash[0]!r}. Inside double quotes bash leaves such a "
                   "pair for the interpreter, so what runs depends on two "
                   "quoting layers at once. Write the script with the Write "
                   "tool and run the FILE. A single-quoted -c payload, or a "
                   "pair bash consumes inside double quotes (before a quote, "
                   "a dollar, a backtick or a backslash), is fine.")
    return 2, ("REFUSED BEFORE RUNNING (S6-B3139ae / #259 / L885): "
               f"{len(hits)} heredoc body(ies) fed to an interpreter carry a "
               f"backslash pair - first: {hits[0]!r}. A backslash pair can "
               "arrive altered through the shell and tool layers. Write the "
               "script with the Write tool and run the FILE. A heredoc with no "
               "backslash is fine, and a git commit or tag message heredoc is "
               "exempt.")


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
