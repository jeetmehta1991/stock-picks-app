"""S6-B3139ae (owner ruling 2026-10-06, packet row 21 'approve'): refuse, BEFORE
it runs, a Bash command that feeds a heredoc body carrying a backslash pair to
an interpreter (python / py / node / perl / ruby). A git commit or tag message
heredoc is exempt. Wired as a PreToolUse hook on Bash in .claude/settings.json.

Why a refusal and not only the Stop-time scan (S6-B3138a): the scan runs at
turn close, after the command has executed, so it records the hazard and
cannot prevent it. Measured over this session's transcript at B3139q-r48:
42 such commands ran after the scan shipped (2026-09-30T07:32Z), 23 of them on
2026-10-06 alone.

ONE definition: the decision is verify_turn_compliance.heredoc_escape_hits,
the same function the Stop-time scan calls, so the refusal and the record can
never disagree about what counts.

Scope, as ruled: heredoc bodies only. The double-quoted `python -c "..."`
sibling (dash_c_escape_hits, S6-B3139v) stays on the Stop-time scan; refusing
it before it runs would be a second new refusal the owner has not ruled on.

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
    if "<<" not in cmd:
        return 0, ""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from verify_turn_compliance import heredoc_escape_hits
    hits = heredoc_escape_hits(cmd)
    if not hits:
        return 0, ""
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
