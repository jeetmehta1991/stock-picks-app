"""scripts/moved_line_citations.py - which line citations in code did the
working tree's edits MOVE? (S6-B3245, L943 instance 2, #196)

WHY: a line citation is an address, and an edit that changes a module's line
count moves every line below its first change - a reworded docstring or a
rewrapped comment included (L943). The S6-B3139bo council kept the code's
string-literal citations as dated campaign evidence (SPECS evidence fields,
the LEG_DEFN text Table A renders, ...), and the S6-B3139bb freeze counts
them per CITING file, so an edit to a CITED module moves them with no test
noticing. MEASURED at B3139q-r82: the first draft of a docstring correction
in smc_ict.py added one line and moved 27 code citations of it, 16 of which
landed on what they describe at HEAD; a hand check before the gate found it
and the edit was reflowed line-count-neutral.

WHAT IT REPORTS: for every tracked .py under backtest/ or scripts/ whose
working-tree text differs from HEAD and that some code cites by line, the
HEAD -> working-tree line map (difflib), then each citation
`<module basename>:<N>` in the HEAD text of the CODE corpus (tracked .py under
backtest/ and scripts/ - the population the S6-B3139bb freeze holds) whose
cited line moved or was rewritten and whose citation text still stands in the
working tree (a citation the same edit already updated is not reported). It
reports MOVEMENT, never correctness: a citation already stale at HEAD moves
too, and the tool cannot read what a citation means.

ONE EXCLUSION, the same as test_b3231's: the frozen B974 one-off classifier,
whose committed output carries the same six screener.py citations - every
screener.py edit above them would otherwise repeat the same six already-stale
hits, and a disclosure that always fires is read past (L599).

IT DISCLOSES; IT NEVER REFUSES. scripts/pyramid_gate.py prints it before
pytest starts and writes moved_line_citations= into the gate footer. A
refusal would tax every comment added above the cited lines of technical.py
and the like - whose cheapest answer is writing less down (L586) - while the
disclosure shows the movement at the one moment it is free to undo: before
the commit, when a text edit can still be reflowed line-neutral (L721).

    python scripts/moved_line_citations.py             # report the working tree
    python scripts/moved_line_citations.py --json PATH # the hits as JSON
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TREES = ("backtest", "scripts")
CRLF, LF = "\r\n", "\n"
# test_b3231's exemption, by the same reason (asserted equal by test_b3245)
FROZEN_CITERS = frozenset({"b974_classify_signal_orphan_17.py"})


def _lines(text: str) -> list[str]:
    # S6-B3273(c): a stray EOL \r (the L885 mangling class) is not content;
    # every caller decodes BYTES - universal newlines made it an extra line
    return [ln.rstrip("\r") for ln in text.replace(CRLF, LF).split(LF)]


def line_map(old: list[str], new: list[str]) -> tuple[dict[int, int], int | None]:
    """({HEAD line -> working line} for every line difflib keeps EQUAL, first
    changed HEAD line or None), 1-based. A line absent from the map was
    rewritten or deleted."""
    sm = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    mapping, first = {}, None
    for tag, i1, i2, j1, _j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                mapping[i1 + k + 1] = j1 + k + 1
        elif first is None:
            first = i1 + 1
    return mapping, first


def cite_pattern(basename: str) -> re.Pattern:
    """`<basename>:<digits>`, not preceded by an identifier character - built
    from parts so this module's own source never cites a line."""
    return re.compile(r"(?<![A-Za-z0-9_])" + re.escape(basename) + ":"
                      + "([0-9]+)" + "(?:-[0-9]+)?")   # S6-B3273(b): A-B span


def moved_in_text(basename: str, mapping: dict, first: int | None,
                  head_text: str, work_text: str) -> list[tuple[int, int, int | None]]:
    """[(citing line, cited HEAD line, working line or None)] for each citation
    of `basename` in `head_text` whose cited line the edit moved or rewrote and
    whose exact citation text still stands in `work_text`."""
    if first is None:
        return []
    pat = cite_pattern(basename)
    out = []
    for i, ln in enumerate(_lines(head_text), 1):
        for m in pat.finditer(ln):
            n = int(m.group(1))
            # S6-B3273(b): a range citation file.py:A-B is checked over
            # its whole span - an edit inside (A, B] moves its tail
            _tail = m.group(0).rsplit(":", 1)[1]   # ONE group kept (findall)
            n2 = int(_tail.split("-")[1]) if "-" in _tail else n
            if n2 < n:
                n2 = n
            if n2 < first:
                continue
            if all(mapping.get(k) == k for k in range(n, n2 + 1)):
                continue
            to = mapping.get(n)
            if m.group(0) not in work_text:
                continue
            out.append((i, n, to))
    return out


def _git(args: list[str], root: Path) -> str:
    # S6-B3273(c): bytes decoded once - text=True made a stray CR a line break
    return subprocess.run(["git", *args], cwd=root, capture_output=True,
                          timeout=120).stdout.decode("utf-8", errors="replace")


def changed_modules(root: Path) -> list[str]:
    """Tracked .py under backtest/ and scripts/ whose working text differs
    from HEAD (staged or not)."""
    # S6-B3273(a): --no-renames - a rename otherwise lists only its NEW
    # path, and the OLD cited basename never enters the changed set
    out = _git(["diff", "--name-only", "--no-renames", "HEAD", "--", *TREES], root)
    return sorted(p for p in out.splitlines() if p.endswith(".py"))


def moved_citations(root: Path = REPO, *, changed: dict | None = None,
                    corpus: dict | None = None) -> list[dict]:
    """Every moved code citation. `changed` maps a module path to its
    (HEAD text, working text); `corpus` maps a citing path to its (HEAD text,
    working text). Both are read from git and the tree unless injected."""
    root = Path(root)
    dirty = None
    if changed is None:
        dirty = changed_modules(root)
        changed = {}
        for rel in dirty:
            p = root / rel
            # S6-B3273(a): a DELETED or RENAMED cited module is an edit
            # that moves every citation of it - empty working text makes
            # each report 'rewritten' instead of vanishing from the set
            changed[rel] = (_git(["show", f"HEAD:{rel}"], root),
                            p.read_bytes().decode("utf-8", errors="replace")
                            if p.exists() else "")
    if not changed:
        return []
    if corpus is None:
        if dirty is None:
            dirty = changed_modules(root)
        corpus = {}
        for rel in _git(["ls-files", "--", *TREES], root).splitlines():
            p = root / rel
            if not rel.endswith(".py") or not p.exists():
                continue
            work = p.read_bytes().decode("utf-8", errors="replace")
            head = _git(["show", f"HEAD:{rel}"], root) if rel in dirty else work
            corpus[rel] = (head, work)
    hits = []
    for mod, (head_mod, work_mod) in sorted(changed.items()):
        base = mod.split("/")[-1]
        pat = cite_pattern(base)
        citing = {rel: tx for rel, tx in corpus.items()
                  if rel.split("/")[-1] not in FROZEN_CITERS and pat.search(tx[0])}
        if not citing:
            continue   # nothing cites it by line: skip the costly line map
        mapping, first = line_map(_lines(head_mod), _lines(work_mod))
        for rel, (head_txt, work_txt) in sorted(citing.items()):
            for line, n, to in moved_in_text(base, mapping, first, head_txt, work_txt):
                hits.append({"module": mod, "citing": rel, "line": line,
                             "cited": n, "now": to})
    return hits


def summary(hits: list[dict], limit: int = 6) -> str:
    """One footer-safe line: 'none', or per module the count and the first
    few citing sites."""
    if not hits:
        return "none"
    by: dict = {}
    for h in hits:
        by.setdefault(h["module"].split("/")[-1], []).append(h)
    parts = []
    for mod, hs in sorted(by.items()):
        sites = ",".join(f"{h['citing'].split('/')[-1]}:{h['line']}" for h in hs[:limit])
        more = f",+{len(hs) - limit}" if len(hs) > limit else ""
        parts.append(f"{mod}={len(hs)}({sites}{more})")
    return ";".join(parts)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", help="write the hits here")
    a = ap.parse_args(argv)
    # L846: resolve the repo by marker, never trust a draft's location
    if not (REPO / "backtest" / "signals" / "screener.py").is_file():
        print(f"REFUSED: {REPO} is not the repo root (no backtest/signals/screener.py)")
        return 2
    hits = moved_citations(REPO)
    print(f"moved_line_citations={summary(hits)}")
    for h in hits:
        print(f"  {h['citing']}:{h['line']} cites {h['module'].split('/')[-1]}:{h['cited']}"
              f" -> now {h['now'] if h['now'] else 'rewritten'}")
    if a.json:
        Path(a.json).write_text(json.dumps(hits, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
