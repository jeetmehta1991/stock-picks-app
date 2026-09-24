"""WHEN did I do X - read from the session transcript, never from a summary
(B3096 / L870 / CHECKLIST #322).

MEASURED 2026-09-24, twice in one day. (1) An L-entry recorded a compliance
failure - "after a context compaction, my first action was to write the fourth
draft part from the summary alone" - and the transcript shows that draft was
written at 13:42:22, FIVE MINUTES BEFORE the compaction (13:47:18), twelve
minutes after the whole source had been read in the same context; after the
compaction the source WAS re-read before any rewrite. (2) After the next
compaction I told the owner an Edit was "my first action in this
continuation"; it was issued at 14:39:23, 98 seconds BEFORE that compaction's
boundary entry (14:41:01). Both times the
evidence was the look of the compacted context: a tool call made before a
compaction is replayed after it and reads like the first action, and the
summary listed an already-written file as still to write.

This prints the facts a timeline claim needs:

  * every compaction boundary (entry index, UTC time);
  * for --file SUBSTR, every Write/Edit whose path contains SUBSTR, with the
    nearest boundary BEFORE it and AFTER it, the inspection calls (Read / Grep
    / Glob / Bash / PowerShell) between the earlier boundary and the write, and
    whether that same path was SEEN after the earlier boundary - Read, or
    Written whole (a Write puts the full content in context; an Edit does not).

Cite its entry indices or UTC times in any L-entry, retraction or RCA that says
when, or from what, I did something across a compaction.

    python scripts/transcript_timeline.py [--transcript PATH] [--file SUBSTR]
                                          [--json OUT]

--transcript defaults to $TURN_GATE_TRANSCRIPT, the variable the Stop hook
reads the live session from.
"""
import argparse
import io
import json
import os
import sys

MARKER = "this session is being continued from a previous conversation"
INSPECTING = ("read", "grep", "glob", "bash", "powershell")
WRITING = ("write", "edit", "notebookedit")


def load(path: str) -> list:
    out = []
    for ln in io.open(path, encoding="utf-8"):
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except ValueError:
                out.append({})
    return out


def _user_text(e: dict) -> str:
    c = (e.get("message") or {}).get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return " ".join(x.get("text") or "" for x in c
                        if isinstance(x, dict) and x.get("type") == "text")
    return ""


def boundaries(entries: list) -> list:
    """Indices of compaction boundaries. The harness writes a system
    `compact_boundary` entry and then the continuation message carrying
    MARKER; both mark ONE compaction, so a marker within 10 entries of a
    system boundary is the same event."""
    sysb = [i for i, e in enumerate(entries)
            if isinstance(e, dict) and e.get("type") == "system"
            and e.get("subtype") == "compact_boundary"]
    marks = [i for i, e in enumerate(entries)
             if isinstance(e, dict) and e.get("type") == "user"
             and MARKER in _user_text(e).lower()]
    out = list(sysb)
    for m in marks:
        if not any(0 <= m - b <= 10 for b in sysb):
            out.append(m)
    return sorted(out)


def _norm(p: str) -> str:
    return str(p or "").replace("\\", "/").lower()


def tool_calls(entries: list) -> list:
    """(index, timestamp, tool name lowercased, normalised file_path)."""
    out = []
    for i, e in enumerate(entries):
        if not isinstance(e, dict) or e.get("type") != "assistant":
            continue
        for b in (e.get("message") or {}).get("content") or ():
            if isinstance(b, dict) and b.get("type") == "tool_use":
                inp = b.get("input") or {}
                out.append((i, e.get("timestamp") or "",
                            str(b.get("name") or "").lower(),
                            _norm(inp.get("file_path") or inp.get("notebook_path"))))
    return out


def timeline(entries: list, substr: str = "") -> dict:
    bnd = boundaries(entries)
    calls = tool_calls(entries)
    ts = {i: (entries[i].get("timestamp") or "") for i in bnd}
    rows = []
    want = _norm(substr)
    for i, t, name, path in calls:
        if name not in WRITING or not want or want not in path:
            continue
        before = max((b for b in bnd if b < i), default=None)
        after = min((b for b in bnd if b > i), default=None)
        lo = before if before is not None else -1
        between = [c for c in calls if lo < c[0] < i]
        rows.append({
            "entry": i, "time": t, "tool": name, "path": path,
            "compaction_before": before, "compaction_before_time": ts.get(before, ""),
            "compaction_after": after, "compaction_after_time": ts.get(after, ""),
            "inspections_since_compaction": sum(1 for c in between if c[2] in INSPECTING),
            "same_path_seen_since_compaction": any(
                c[2] in ("read", "write") and c[3] == path for c in between)})
    return {"compactions": [{"entry": b, "time": ts[b]} for b in bnd],
            "writes": rows}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--transcript", default=os.environ.get("TURN_GATE_TRANSCRIPT", ""))
    ap.add_argument("--file", default="", help="substring of the written path")
    ap.add_argument("--json", help="write the full result here")
    a = ap.parse_args(argv)
    if not a.transcript or not os.path.exists(a.transcript):
        print("REFUSED: no transcript (pass --transcript or set TURN_GATE_TRANSCRIPT)")
        return 2
    res = timeline(load(a.transcript), a.file)
    print("compaction boundaries: %d" % len(res["compactions"]))
    for c in res["compactions"][-5:]:
        print("  entry %-7d %s" % (c["entry"], c["time"]))
    if a.file:
        print("writes matching %r: %d" % (a.file, len(res["writes"])))
        for r in res["writes"]:
            print("  %-5s entry %-7d %s  %s" % (r["tool"], r["entry"], r["time"],
                                              r["path"].rsplit("/", 1)[-1]))
            print("        after compaction %s (%s); before compaction %s (%s)"
                  % (r["compaction_before"], r["compaction_before_time"] or "-",
                     r["compaction_after"], r["compaction_after_time"] or "-"))
            print("        inspections since that compaction: %d; same path Read or "
                  "Written since: %s" % (r["inspections_since_compaction"],
                                        "yes" if r["same_path_seen_since_compaction"]
                                        else "no"))
    if a.json:
        io.open(a.json, "w", encoding="utf-8").write(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
