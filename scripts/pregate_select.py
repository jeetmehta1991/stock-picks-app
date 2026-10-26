"""S6-B3269 (B3139q-r92, L950): run the tests that READ what a change touched,
before the 25-minute gate.

MEASURED at B3139q-r86..r89c: four of my own defects reached full gates - a
derived artifact (test_b3232), a derived test subject (test_b3171b), a
generator's freshness stamp (test_b1974) and a repo-wide ratchet
(test_b2128) - and none of the four failing tests ran between its change and
the gate. The gate's read-set (scripts/pytest_plugins/pyramid_readset.py)
watches output_audit/ only, so alone it selects 1 of the 4. This selector
unions seven rules, each a LOWER bound - the full gate stays the authority:

  R1 read-set  tests whose reads, in the newest gate read-set
               (output_audit/*_pyramid.json.readset.json), include a changed
               output_audit path - untracked, so absent on a clean checkout;
  R2 named     tests whose source - or the source of a module-level name they
               reach, transitively - names a changed file's path, file name or
               stem as a whole word;
  R3 scanner   tests that walk the source tree (rglob / os.walk / a *.py
               glob, reached the same way), selected by ANY changed .py file;
  R4 edited    test functions whose own lines the diff touches;
  R5 self-read tests that read a CHANGED test module's own source - via
               __file__, or by naming the module in a quoted literal -
               which R2 skips (S6-B3283: test_b2557, unselected, turned
               the r95 gate RED);
  R6 repo-read tests whose reads, in the newest gate read-set's repo_tests,
               include a changed non-.py file outside output_audit/ - a
               read through an imported script's default (S6-B3310:
               test_b3106 read the queue via audit_ticket_staleness);
  R7 listing   tests that LISTED the parent directory of an ADDED or
               DELETED path, in either map (S6-B3310: test_b3167 lists
               strategy_optimisation/tighten/, where r111 added files).

    python scripts/pregate_select.py                       # changed = git diff HEAD + untracked
    python scripts/pregate_select.py --changed scripts/make_spec.py --run
"""
import argparse
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEST_FILES = ("backtest/tests/test_unit.py", "backtest/tests/test_integration.py")
_SCAN_MARKS = (".rglob(", "os.walk(", '.glob("*.py")', ".glob('*.py')",
               '.glob("**/*.py")', ".glob('**/*.py')")
# S6-B3283 (R5): a test that opens its own module's source
_SELF_READ = re.compile(r"\(__file__\)\s*\.\s*read_(?:text|bytes)\(|open\(\s*__file__")


def changed_files(root=ROOT, all_untracked=False) -> list:
    """Paths changed against HEAD, plus untracked files under scripts/ and
    backtest/ (new code and tests), repo-relative. Not every untracked file:
    this working tree carries thousands of untracked output artifacts
    (MEASURED 2026-10-21: 14,610), and matching each against every test kept
    the first draft's selection computing for minutes. all_untracked=True
    takes them all."""
    out = set()
    untracked = ["git", "ls-files", "--others", "--exclude-standard"]
    if not all_untracked:
        untracked += ["--", "scripts", "backtest"]
    for cmd in (["git", "diff", "--name-only", "HEAD"], untracked):
        r = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=120)
        out.update(ln.strip().replace("\\", "/") for ln in r.stdout.splitlines()
                   if ln.strip())
    return sorted(out)


def changed_lines(test_file, root=ROOT) -> set:
    """Line numbers (new side) the diff against HEAD touches in `test_file`."""
    r = subprocess.run(["git", "diff", "-U0", "HEAD", "--", test_file], cwd=root,
                       capture_output=True, text=True, timeout=120)
    lines = set()
    for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", r.stdout, re.M):
        start, n = int(m.group(1)), int(m.group(2) or 1)
        lines.update(range(start, start + max(n, 1)))
    return lines


def index_module(src) -> tuple:
    """(tests, defs): test name -> its node; module-level name -> (source
    segment, node) for functions, classes and assignments."""
    tree = ast.parse(src)
    lines = src.splitlines()      # once - get_source_segment re-splits per call
    tests, defs = {}, {}
    for node in tree.body:
        seg = "\n".join(lines[node.lineno - 1:(node.end_lineno or node.lineno)])
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs[node.name] = (seg, node)
            if node.name.startswith("test_"):
                tests[node.name] = node
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for tg in targets:
                if isinstance(tg, ast.Name):
                    defs[tg.id] = (seg, node)
    return tests, defs


def reach(name, defs, depth=4) -> str:
    """The source `name` reaches: its own segment and the segments of the
    module-level names it references, transitively to `depth`."""
    seen, frontier, texts = {name}, [name], []
    for _ in range(depth + 1):
        nxt = []
        for nm in frontier:
            seg, node = defs.get(nm, ("", None))
            texts.append(seg)
            for n in (ast.walk(node) if node is not None else ()):
                if isinstance(n, ast.Name) and n.id in defs and n.id not in seen:
                    seen.add(n.id)
                    nxt.append(n.id)
        frontier = nxt
        if not frontier:
            break
    return "\n".join(texts)


def _tokens(path) -> list:
    p = str(path).replace("\\", "/")
    name = p.rsplit("/", 1)[-1]
    stem = name.rsplit(".", 1)[0]
    return [t for t in {p, name, stem} if len(t) >= 3]


_TOK_RE = {}


def _names(text, tok) -> bool:
    """`tok` appears in `text` as a whole word (a stem inside a longer
    identifier does not count)."""
    rx = _TOK_RE.get(tok)
    if rx is None:
        rx = _TOK_RE[tok] = re.compile(r"(?<![\w])" + re.escape(tok) + r"(?![\w])")
    return rx.search(text) is not None


def newest_readset(root=ROOT, key="tests"):
    """The newest gate read-set's {nodeid: [reads]} under `key` ("tests":
    output_audit reads; "repo_tests": the S6-B3310 repo-wide reads and
    listings), or None."""
    cands = sorted((root / "output_audit").glob("*_pyramid.json.readset.json"),
                   key=lambda q: q.stat().st_mtime)
    if not cands:
        return None
    try:
        return json.loads(cands[-1].read_text(encoding="utf-8")).get(key) or {}
    except (OSError, ValueError):
        return None


def _fold(p) -> str:
    p = str(p).replace("\\", "/")
    return p.lower() if os.name == "nt" else p


def added_or_deleted(changed, root=ROOT) -> list:
    """S6-B3310: the changed paths that change a directory LISTING - absent
    from HEAD's tree (added) or absent from the disk (deleted)."""
    r = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=root,
                       capture_output=True, text=True, timeout=120)
    head = {_fold(ln.strip()) for ln in r.stdout.splitlines() if ln.strip()}
    return [c for c in changed
            if _fold(c) not in head or not (Path(root) / c).exists()]


def _parent(p) -> str:
    d = str(p).replace("\\", "/").rsplit("/", 1)
    return d[0] + "/" if len(d) == 2 else "./"


def select(changed, root=ROOT, readset=None, edited=None, repo_readset=None,
           listed=None, test_files=TEST_FILES) -> dict:
    """{nodeid: [rules]} for the changed paths. `readset` injects R1's map
    (None reads the newest on disk); `edited` maps a test file to the line
    numbers its diff touches (None reads git); `repo_readset` injects
    R6/R7's repo-wide map and `listed` the added-or-deleted paths (None
    reads the read-set / git); `test_files` the modules R2-R5 parse."""
    changed = [str(c).replace("\\", "/") for c in changed]
    rs = newest_readset(root) if readset is None else readset
    rrs = newest_readset(root, "repo_tests") if repo_readset is None else repo_readset
    lst = added_or_deleted(changed, root) if listed is None else list(listed)
    py_changed = [c for c in changed if c.endswith(".py") and c not in TEST_FILES]
    oa_changed = {c for c in changed if c.startswith("output_audit/")}
    test_changed = [c for c in changed if c in TEST_FILES]
    lits = [re.compile(r"[\"']" + re.escape(c.rsplit("/", 1)[-1]) + r"[\"']")
            for c in test_changed]
    hits = {}

    def add(node_id, rule):
        hits.setdefault(node_id, [])
        if rule not in hits[node_id]:
            hits[node_id].append(rule)

    for k, reads in (rs or {}).items():
        if oa_changed & {str(x).replace("\\", "/") for x in (reads or [])}:
            add(k, "R1")
    # S6-B3310 R6: a changed non-.py file outside output_audit that a test read
    repo_changed = {_fold(c) for c in changed if not c.startswith("output_audit/")
                    and not c.endswith(".py") and c not in TEST_FILES}
    for k, reads in (rrs or {}).items():
        if repo_changed & {_fold(x) for x in (reads or [])}:
            add(k, "R6")
    # S6-B3310 R7: a test that LISTED the folder an added/deleted path sits in;
    # a .py is R3's - the import machinery lists every sys.path folder
    parents = {_fold(_parent(p)) for p in lst if not str(p).endswith(".py")}
    for m in (rs or {}, rrs or {}):
        for k, reads in m.items():
            if any(str(x).endswith("/") and _fold(x) in parents for x in (reads or [])):
                add(k, "R7")
    for tf in test_files:
        f = root / tf
        if not f.is_file():
            continue
        src = f.read_text(encoding="utf-8")
        tests, defs = index_module(src)
        lines = (changed_lines(tf, root) if edited is None else set(edited.get(tf, ())))
        for name, node in tests.items():
            nid = f"{tf}::{name}"
            text = reach(name, defs)
            for c in changed:
                if c in TEST_FILES:
                    continue
                if any(_names(text, tok) for tok in _tokens(c)):
                    add(nid, "R2")
                    break
            if py_changed and any(m in text for m in _SCAN_MARKS):
                add(nid, "R3")
            if lines and any(node.lineno <= ln <= (node.end_lineno or node.lineno)
                             for ln in lines):
                add(nid, "R4")
            if test_changed and ((tf in test_changed and _SELF_READ.search(text))
                                 or any(rx.search(text) for rx in lits)):
                add(nid, "R5")
    return dict(sorted(hits.items()))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--changed", nargs="*", default=None,
                    help="paths to select for (default: git diff HEAD + untracked)")
    ap.add_argument("--run", action="store_true", help="run the selected tests")
    ap.add_argument("--all-untracked", action="store_true",
                    help="count every untracked file as changed, not only scripts/ and backtest/")
    ap.add_argument("--json", help="write the selection here")
    a = ap.parse_args(argv)
    if not (ROOT / "backtest" / "signals" / "screener.py").is_file():
        print(f"REFUSED (pregate_select, S6-B3269): {ROOT} is not the repo root")
        return 2
    changed = (a.changed if a.changed is not None
               else changed_files(all_untracked=a.all_untracked))
    sel = select(changed)
    by_rule = {r: sum(1 for v in sel.values() if r in v)
               for r in ("R1", "R2", "R3", "R4", "R5", "R6", "R7")}
    print(f"pregate_select: {len(changed)} changed path(s) -> {len(sel)} test(s) "
          f"(R1 {by_rule['R1']}, R2 {by_rule['R2']}, R3 {by_rule['R3']}, R4 {by_rule['R4']}, "
          f"R5 {by_rule['R5']}, R6 {by_rule['R6']}, R7 {by_rule['R7']}) "
          "- a LOWER bound; the full gate stays the authority")
    if a.json:
        Path(a.json).write_text(json.dumps({"changed": changed, "selected": sel},
                                           indent=1), encoding="utf-8")
    if not a.run:
        for nid, rules in sel.items():
            print(f"  {nid}  [{','.join(rules)}]")
        return 0
    if not sel:
        print("nothing selected - nothing to run")
        return 0
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                           *sel], cwd=ROOT).returncode


if __name__ == "__main__":
    sys.exit(main())
