"""S6-B3130a (owner ruling 2026-09-29, '6. Yes'): the pytest plugin behind
the pyramid gate's READ-SET.

Loaded ONLY by scripts/pyramid_gate.py (`-p pyramid_readset`, with scripts/
on PYTHONPATH) and active only while PYRAMID_READSET names an output file, so
a plain pytest run is untouched.

WHAT IT RECORDS, per test: every file under <root>/output_audit/ the test
OPENED FOR READING, through sys.addaudithook's 'open' event - builtins, io
and os opens; pandas read_csv and read_parquet raise it too (MEASURED B3137).
A test that SPAWNS a process (subprocess / CreateProcess / os.system) is
flagged: a child's reads are invisible to this process's hook, so the gate
treats a spawner as having read every moved file. Reads made outside any test
(collection, module import) are recorded under "session". A WRITE-only open is
not a read - a test that rewrites an artifact did not consume it.
B3139 (the batch-2 gate run): WRITE opens are recorded too, per test, under
"writes" - never as reads. A test writing under the production output_audit
is L689's class (a test driving production code is production code for the
run), and its write moves a file other tests may list; the gate names each
one (readset_suite_writes=) and says so when a re-run's own writes are what
moved again. A spawned child's writes are invisible here, as its reads are.

B3139 (S6-B3130a council, 5 advisors) adds two read kinds:
  FIXTURE-SCOPED READS. A read made while a session / package / module /
  class-scoped fixture is being SET UP is credited to EVERY test that uses
  that fixture (item.fixturenames, the transitive closure) - a later test
  reuses the cached object and consumed the file just the same.
  DIRECTORY LISTINGS. os.listdir and os.scandir events are recorded as a
  read of the DIRECTORY ('output_audit/<dir>/', trailing slash); glob.glob,
  Path.glob / rglob / iterdir and os.walk all raise os.scandir (MEASURED on
  Python 3.14). The gate matches a directory read to every moved path
  beneath it.
BLIND SPOT, stated: an existence or size check (os.stat, Path.exists,
os.path.getsize) raises NO audit event, so a test that branches on whether
a file exists without opening it or listing its directory is not recorded.

WHY: tracked output_audit files are TEST INPUTS (L880), and the gate's tree
fingerprint excludes output_audit by design (a landing mid-run is not an edit
to the code under test). The gate already DISCLOSED a moved input; this lets
it name the tests that read one and re-run exactly those.

S6-B3310 (B3139q-r112b): REPO-WIDE READS, UNDER THEIR OWN KEYS. A test
that reads EXECUTION_QUEUE.md through an imported script, or lists a folder a
batch added a file to, is invisible to the pre-gate selector's static rules
(the r111 gate failed on one of each). Every non-.py file a test OPENS FOR
READING anywhere in the repo outside output_audit/ and the skipped trees, and
every directory it LISTS ('<dir>/', './' for the root), is recorded under
repo_tests / repo_session - keys the gate itself never reads, so its
verdicts cannot move; writes stay output_audit-only (the suite-writes
disclosure keeps its meaning). scripts/pregate_select.py reads them (R6, R7).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ENV_OUT = "PYRAMID_READSET"
ENV_ROOT = "PYRAMID_READSET_ROOT"
LIST_EVENTS = ("os.listdir", "os.scandir")
SPAWN_EVENTS = ("subprocess.Popen", "_winapi.CreateProcess", "os.system",
                "os.posix_spawn", "os.spawn", "os.exec", "os.fork")
SESSION = "session"
# S6-B3310: trees a repo-wide read is never recorded under
REPO_SKIP = (".git", ".venv", "__pycache__", "node_modules", ".pytest_cache")

_STATE = {"current": None, "tests": {}, "session": set(), "spawned": set(),
          "addr": {}, "oa": None, "installed": False,
          "fixture_stack": [], "fixture_reads": {}, "fixture_scope": {},
          "uses": {}, "writes": {},
          # S6-B3310: repo-wide reads and listings, apart from the above
          "repo": None, "repo_tests": {}, "repo_session": set(),
          "repo_fixture_reads": {}}


def is_read(mode, flags) -> bool:
    """An open that can consume content: a text/binary mode carrying 'r' or
    '+', or an os.open whose access mode is not write-only."""
    if isinstance(mode, str):
        return "r" in mode or "+" in mode
    if isinstance(flags, int):
        return (flags & (os.O_RDONLY | os.O_WRONLY | os.O_RDWR)) != os.O_WRONLY
    return True


def is_write(mode, flags) -> bool:
    """An open that can CHANGE content: a mode carrying 'w', 'a', 'x' or
    '+', or an os.open whose access mode is not read-only (B3139)."""
    if isinstance(mode, str):
        return any(c in mode for c in "wax+")
    if isinstance(flags, int):
        return (flags & (os.O_RDONLY | os.O_WRONLY | os.O_RDWR)) != os.O_RDONLY
    return False


def rel_under(path, oa_norm: str):
    """'output_audit/<name>' for a path inside the watched directory (case as
    written, compared case-insensitively where the OS is), else None."""
    if path is None or isinstance(path, int):
        return None
    try:
        orig = os.path.abspath(os.fsdecode(os.fspath(path)))
    except (TypeError, ValueError):
        return None
    if not os.path.normcase(orig).startswith(oa_norm):
        return None
    return "output_audit/" + orig[len(oa_norm):].replace(os.sep, "/")


def rel_dir_under(path, oa_norm: str):
    """'output_audit/<dir>/' for a LISTED directory inside the watched one
    (the watched directory itself is 'output_audit/'), else None."""
    if path is None or isinstance(path, int):
        return None
    try:
        orig = os.path.abspath(os.fsdecode(os.fspath(path)))
    except (TypeError, ValueError):
        return None
    norm = os.path.normcase(orig).rstrip(os.sep) + os.sep
    if not norm.startswith(oa_norm):
        return None
    sub = orig.rstrip(os.sep)[len(oa_norm) - 1:].strip(os.sep)
    return "output_audit/" + (sub.replace(os.sep, "/") + "/" if sub else "")


def _repo_rel(path, repo_norm: str, oa_norm: str, listing: bool = False):
    """S6-B3310: the repo-relative name of a read file (a non-.py file) or a
    LISTED directory ('<dir>/', './' for the root) under the repo and outside
    output_audit/ and REPO_SKIP, case as written; None for anything else."""
    if repo_norm is None or path is None or isinstance(path, int):
        return None
    try:
        orig = os.path.abspath(os.fsdecode(os.fspath(path)))
    except (TypeError, ValueError):
        return None
    norm = os.path.normcase(orig)
    if listing:
        norm = norm.rstrip(os.sep) + os.sep
        orig = orig.rstrip(os.sep) + os.sep
    if not norm.startswith(repo_norm) or norm.startswith(oa_norm):
        return None
    rel = orig[len(repo_norm):].replace(os.sep, "/")
    if any(part in REPO_SKIP for part in rel.split("/")):
        return None
    if listing:
        return rel if rel else "./"
    if not rel or rel.endswith((".py", ".pyc")):
        return None
    return rel


def _record_repo(st, rel):
    for f in st["fixture_stack"]:
        st["repo_fixture_reads"].setdefault(f, set()).add(rel)
    cur = st["current"]
    if cur is None:
        st["repo_session"].add(rel)
    else:
        st["repo_tests"].setdefault(cur, set()).add(rel)


def _record(st, rel):
    for f in st["fixture_stack"]:
        st["fixture_reads"].setdefault(f, set()).add(rel)
    cur = st["current"]
    if cur is None:
        st["session"].add(rel)
    else:
        st["tests"].setdefault(cur, set()).add(rel)


def _hook(event, args):
    st = _STATE
    oa = st["oa"]
    if oa is None:
        return
    if event == "open":
        rel = rel_under(args[0] if args else None, oa)
        mode = args[1] if len(args) > 1 else None
        flags = args[2] if len(args) > 2 else None
        if rel is None:
            # S6-B3310: a repo-wide READ goes under its own key, never a write
            rr = _repo_rel(args[0] if args else None, st["repo"], oa)
            if rr is not None and is_read(mode, flags):
                _record_repo(st, rr)
            return
        if is_write(mode, flags):
            st["writes"].setdefault(st["current"] or SESSION, set()).add(rel)
        if not is_read(mode, flags):
            return
        _record(st, rel)
    elif event in LIST_EVENTS:
        rel = rel_dir_under(args[0] if args else None, oa)
        if rel is not None:
            _record(st, rel)
        else:
            rr = _repo_rel(args[0] if args else None, st["repo"], oa, listing=True)
            if rr is not None:
                _record_repo(st, rr)
    elif event in SPAWN_EVENTS:
        st["spawned"].add(st["current"] or SESSION)


def pytest_configure(config):
    out = os.environ.get(ENV_OUT)
    if not out:
        return
    root = os.environ.get(ENV_ROOT) or os.getcwd()
    _STATE["oa"] = os.path.normcase(os.path.join(os.path.abspath(root),
                                                 "output_audit")) + os.sep
    _STATE["repo"] = os.path.normcase(os.path.abspath(root)) + os.sep   # S6-B3310
    if not _STATE["installed"]:
        sys.addaudithook(_hook)       # cannot be removed; inert when oa is None
        _STATE["installed"] = True


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    """While a NON-function-scoped fixture is being set up, its reads are
    also filed under the fixture, so every test using it is credited."""
    scope = str(getattr(fixturedef, "scope", "function"))
    push = scope != "function"
    if push:
        _STATE["fixture_stack"].append(fixturedef.argname)
        _STATE["fixture_scope"][fixturedef.argname] = scope
    try:
        yield
    finally:
        if push:
            _STATE["fixture_stack"].pop()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    _STATE["current"] = item.nodeid
    _STATE["uses"][item.nodeid] = list(getattr(item, "fixturenames", []) or [])
    rest = item.nodeid.split("::", 1)[1] if "::" in item.nodeid else ""
    _STATE["addr"][item.nodeid] = f"{item.path}::{rest}" if rest else str(item.path)
    try:
        yield
    finally:
        _STATE["current"] = None


def pytest_sessionfinish(session, exitstatus):
    out = os.environ.get(ENV_OUT)
    if not out or _STATE["oa"] is None:
        return
    tests = {k: set(v) for k, v in _STATE["tests"].items()}
    fr = _STATE["fixture_reads"]
    for node, names in _STATE["uses"].items():
        inherited = set().union(*(fr[n] for n in names if n in fr)) if fr else set()
        if inherited:
            tests.setdefault(node, set()).update(inherited)
    rtests = {k: set(v) for k, v in _STATE["repo_tests"].items()}
    rfr = _STATE["repo_fixture_reads"]
    for node, names in _STATE["uses"].items():
        inherited = set().union(*(rfr[n] for n in names if n in rfr)) if rfr else set()
        if inherited:
            rtests.setdefault(node, set()).update(inherited)
    doc = {"schema": 1,
           "watched": _STATE["oa"],
           "n_items": len(getattr(session, "items", []) or []),
           "tests": {k: sorted(v) for k, v in sorted(tests.items())},
           "fixtures": {k: {"scope": _STATE["fixture_scope"].get(k),
                            "reads": sorted(v)} for k, v in sorted(fr.items())},
           "session": sorted(_STATE["session"]),
           "writes": {k: sorted(v) for k, v in sorted(_STATE["writes"].items())},
           "spawned": sorted(_STATE["spawned"]),
           "addr": dict(sorted(_STATE["addr"].items())),
           # S6-B3310: read by scripts/pregate_select.py, never by the gate
           "repo_watched": _STATE["repo"],
           "repo_tests": {k: sorted(v) for k, v in sorted(rtests.items())},
           "repo_session": sorted(_STATE["repo_session"])}
    Path(out).write_text(json.dumps(doc, indent=1), encoding="utf-8")
