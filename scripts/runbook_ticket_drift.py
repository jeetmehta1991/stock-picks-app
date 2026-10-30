#!/usr/bin/env python
"""S6-B3343 (B3139q-r144): the ticket-versus-runbook comparison the owner
approved as a PRINTED check - 2026-10-28T22:18:34Z, verbatim 'Yes approved /
Be extremely thorough / Fable mode', on 'add the printed check?'. Drafted and
validated read-only on 2026-10-28; landed with the runbook's same-batch rule
(S6-B3369) and pinned by test_b3343. scripts/pyramid_gate.py prints its
summary as runbook_drift= in every gate record.

WHY. A batch that changes the optimisation workflow or one of its reports owes
STRATEGY_OPTIMISATION_PLAN.md a matching edit (CHECKLIST #67). MEASURED
2026-10-28 over the tickets whose ledger rows were added since 2026-10-21 (base
fd2c815be): the runbook named 24 of 103; the other 79 were read in full and 13
had changed the workflow or its reports without the runbook following. No
file-level signal separates those 13: 'a commit naming the ticket touched a
script the runbook cites' caught 13 of 13 and also 51 of the 66 that owed
nothing (it fires on 64 of 79). So this check LISTS and ASKS; a person decides.
A blocking gate would have fired mostly on code fixes - 66 of 79 owed the
runbook nothing - which is why it is printed, never blocking.

WHAT IT PRINTS.
  default (batch mode): the ticket ids in EXECUTION_QUEUE.md rows ADDED in the
  working tree relative to --batch-base (HEAD: the batch about to be committed;
  #292 puts its rows in before the pyramid gate), each NAMED / NOT NAMED in the
  runbook, the unnamed ones with the opening of their row; and the LEARNINGS
  entries the batch adds, CITED / NOT CITED. The question for each unnamed one:
  does it change the workflow or a report? If yes, edit the runbook in this
  batch and cite the ticket id where the rule is described.
  --since YYYY-MM-DD | --base SHA (window mode): the 2026-10-28 census method -
  every ticket with rows added since the base, its state (queue_state, last
  row wins), NAMED or not, and the files of the commits whose messages name
  it; every LEARNINGS entry added since the base, CITED or not.

NAMED means the full id (S6-B3264) or its bare batch form (B3264) appears in
the runbook OUTSIDE generated blocks (<!-- ...:START ... --> to <!-- ...:END
-->): plan_lineage.py's appendix carries commit subjects, which could 'name' a
ticket the runbook's text never describes (2 ids sit there today; 0 of the 24
census-named tickets were named only there).

Exit status is 0 whatever it finds - a printed check by owner ruling. An error
prints 'runbook_drift=unreadable (<type>)' and still exits 0, the convention of
pyramid_gate's other disclosures: a disclosure that could break the gate it
annotates is worse than none.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RUNBOOK = "STRATEGY_OPTIMISATION_PLAN.md"
QUEUE = "EXECUTION_QUEUE.md"
LESSONS = "LEARNINGS.md"


def find_root() -> Path:
    """The repo root by MARKER (L846: a draft run from elsewhere must not read a
    tree its location guesses): the first of cwd and this file's directory, or
    a parent of either, holding the runbook, the queue and .git - else refuse."""
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for p in [start] + list(start.parents):
            if (p / RUNBOOK).is_file() and (p / QUEUE).is_file() and (p / ".git").exists():
                return p
    raise RuntimeError("no repo root holding %s, %s and .git" % (RUNBOOK, QUEUE))

_LESSON = re.compile(r"^\+#{2,3}\s*L(\d+)\b[^A-Za-z0-9]*(.*)$")
_GEN_BLOCK = re.compile(r"<!--[^>]*?:START.*?<!--[^>]*?:END[^>]*?-->", re.S)


def added_ticket_rows(diff_text: str) -> dict:
    """{ticket id: opening of the FIRST added row} for every ledger row a
    unified diff ADDS, in first-seen order. The id is read by
    queue_state.row_id - the ONE ticket-id definition, bold or not (L603,
    test_b3139's charset ratchet refused this file's own copy) - and the
    landing supervisor's machine rows are skipped: they record a landing,
    not a change to the workflow."""
    if str(Path(__file__).resolve().parent) not in sys.path:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
    import queue_state as qs
    out = {}
    for ln in (diff_text or "").splitlines():
        if not ln.startswith("+") or ln.startswith("+++"):
            continue
        row = ln[1:]
        tid = qs.row_id(row)
        if not tid or tid in out or tid.startswith(qs.MACHINE_ROW_PREFIX):
            continue
        rest = row.split("|", 2)[2] if row.count("|") >= 2 else ""
        out[tid] = re.sub(r"\s+", " ", rest.replace("*", "")).strip(" |")[:140]
    return out


def added_lessons(diff_text: str) -> list:
    """[(L number, heading)] for every LEARNINGS heading a unified diff adds."""
    out = []
    for ln in (diff_text or "").splitlines():
        m = _LESSON.match(ln)
        if m and int(m.group(1)) not in [n for n, _ in out]:
            out.append((int(m.group(1)), m.group(2).strip()[:120]))
    return out


def outside_generated(text: str) -> str:
    """The runbook with every generated START..END block blanked (same length,
    so offsets survive)."""
    return _GEN_BLOCK.sub(lambda m: " " * len(m.group(0)), text or "")


def is_named(text: str, tid: str) -> bool:
    """Full id, or the bare batch form of an S6- id, as a whole token."""
    if re.search(re.escape(tid) + r"(?![A-Za-z0-9])", text):
        return True
    m = re.match(r"S6-(B\d+[A-Za-z0-9-]*)$", tid)
    return bool(m) and re.search(r"(?<![A-Za-z0-9-])" + re.escape(m.group(1))
                                 + r"(?![A-Za-z0-9])", text) is not None


def is_cited(text: str, n: int) -> bool:
    return re.search(r"(?<![A-Za-z0-9])L%d(?![0-9])" % n, text) is not None


def _git(root: Path, *a) -> str:
    r = subprocess.run(["git", "-C", str(root)] + list(a), capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=120)
    if r.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (a[0], r.stderr.strip()[:200]))
    return r.stdout


def _runbook_text(root: Path) -> str:
    return outside_generated((root / RUNBOOK).read_text(encoding="utf-8", errors="replace"))


def batch_report(root: Path, base: str = "HEAD") -> dict:
    """Tickets and lessons the working tree ADDS relative to `base`."""
    rb = _runbook_text(root)
    qd = _git(root, "diff", "--unified=0", "--ignore-cr-at-eol", base, "--", QUEUE)
    ld = _git(root, "diff", "--unified=0", "--ignore-cr-at-eol", base, "--", LESSONS)
    rows = added_ticket_rows(qd)
    return {"mode": "batch", "base": base,
            "tickets": [{"id": t, "named": is_named(rb, t), "row": rows[t]} for t in rows],
            "lessons": [{"L": n, "heading": h, "cited": is_cited(rb, n)}
                        for n, h in added_lessons(ld)]}


def window_report(root: Path, since: str | None = None,
                  base: str | None = None) -> dict:
    """The 2026-10-28 census method over base..HEAD."""
    if base is None:
        if not since:
            raise ValueError("window mode needs --since or --base")
        base = _git(root, "rev-list", "-1", "--before=%sT00:00:00" % since, "HEAD").strip()
        if not base:
            raise ValueError("no commit before %s" % since)
    rb = _runbook_text(root)
    qd = _git(root, "diff", "--unified=0", "--ignore-cr-at-eol", base, "HEAD", "--", QUEUE)
    ld = _git(root, "diff", "--unified=0", "--ignore-cr-at-eol", base, "HEAD", "--", LESSONS)
    rows = added_ticket_rows(qd)
    if str(root / "scripts") not in sys.path:
        sys.path.insert(0, str(root / "scripts"))
    import queue_state as qs
    state = qs.tickets(root / QUEUE)
    log = _git(root, "log", "%s..HEAD" % base, "--format=%x1e%h%x1f%B%x1f", "--name-only")
    commits = []
    for chunk in log.split("\x1e"):
        parts = chunk.split("\x1f")
        if len(parts) >= 3:
            commits.append((parts[1], [f.strip() for f in parts[2].splitlines() if f.strip()]))
    tickets = []
    for t in rows:
        pat = re.compile(re.escape(t) + r"(?![A-Za-z0-9])")
        files = sorted({f for msg, fs in commits if pat.search(msg) for f in fs})
        tickets.append({"id": t, "state": state.get(t, "?"), "named": is_named(rb, t),
                        "row": rows[t], "files": files})
    return {"mode": "window", "since": since, "base": base[:9], "commits": len(commits),
            "tickets": tickets,
            "lessons": [{"L": n, "heading": h, "cited": is_cited(rb, n)}
                        for n, h in added_lessons(ld)]}


def summary(rep: dict) -> str:
    """One line for pyramid_gate's footer: 'none' when nothing is added."""
    t, l = rep["tickets"], rep["lessons"]
    if not t and not l:
        return "none"
    un = [x["id"] for x in t if not x["named"]]
    ul = ["L%d" % x["L"] for x in l if not x["cited"]]
    return ("tickets %d, not named in the runbook %d%s; lessons %d, not cited %d%s"
            % (len(t), len(un), (" (" + ", ".join(un) + ")") if un else "",
               len(l), len(ul), (" (" + ", ".join(ul) + ")") if ul else ""))


def render(rep: dict) -> str:
    t, l = rep["tickets"], rep["lessons"]
    head = ("batch vs %s" % rep["base"]) if rep["mode"] == "batch" else (
        "window since %s (base %s, %d commits)" % (rep["since"] or "-", rep["base"], rep["commits"]))
    lines = ["runbook_drift (%s): %s" % (head, summary(rep))]
    for x in t:
        if not x["named"]:
            extra = (" [%s]" % x["state"]) if "state" in x else ""
            lines.append("  NOT NAMED %s%s: %s" % (x["id"], extra, x["row"]))
    for x in l:
        if not x["cited"]:
            lines.append("  NOT CITED L%d: %s" % (x["L"], x["heading"]))
    if any(not x["named"] for x in t) or any(not x["cited"] for x in l):
        lines.append("  For each: does it change the optimisation workflow or one of its "
                     "reports? If yes, edit %s in this batch and cite the id where the "
                     "rule is described (CHECKLIST #67). A printed check: nothing is "
                     "refused." % RUNBOOK)
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="ticket-versus-runbook comparison (printed)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--since", help="window mode: rows added since YYYY-MM-DD")
    g.add_argument("--base", help="window mode: rows added since this commit")
    ap.add_argument("--batch-base", default="HEAD", help="batch mode base (default HEAD)")
    ap.add_argument("--json", help="also write the report as JSON here")
    a = ap.parse_args(argv)
    try:
        root = find_root()
        rep = (window_report(root, a.since, a.base) if (a.since or a.base)
               else batch_report(root, a.batch_base))
    except Exception as e:  # a printed check never fails its caller
        print("runbook_drift=unreadable (%s: %s)" % (type(e).__name__, str(e)[:160]))
        return 0
    print(render(rep))
    if a.json:
        Path(a.json).write_text(json.dumps(rep, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
