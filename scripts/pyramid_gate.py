#!/usr/bin/env python
"""B2580 (CHECKLIST #292 / L755): the enforced pyramid as a measurement of ONE tree.

Three times in one session (2026-09-02/03) a pyramid's verdict covered a tree
that changed under it: a mid-run engine edit shifted the function an
`inspect.getsource` pin reads (B2574, false RED); an un-dry patcher overwrote
three scripts at ~40% (B2576, would-have-been false GREEN); and a gate run
pre-dated the doc edits it vouched for (B2570 -> test_b1486 at B2571). The
log of a GREEN run over a moving tree reads exactly like a real one.

This wrapper fingerprints the tree under test BEFORE pytest and AFTER it and
writes the verdict beside the `exit=` line the artifact already carries (L738:
read the artifact's own exit, never a pipe's):

    pytest_exit=<pytest's code>
    tree=SAME | CHANGED (<n> paths): a, b, ...
    exit=<pytest's code, or 4 when the tree changed>

A CHANGED run is VOID whatever pytest said; re-run it on the settled tree.

S6-B3130a (owner ruling 2026-09-29): the READ-SET. A watched output_audit
file that moved during the run sends EXACTLY the tests that read it back
through pytest once (readset=RERUN-PASS / RERUN-FAILED), or marks the run
SUSPECT (exit=6) when the tests cannot be named. A run the gate does not
pass - exit 4, 6 or a failed re-run - WOULD demote the GREEN stamp it
wrote; until the owner rules on the demotion (S6-B3130a, B3139 council)
the gate records stamp_binding=would-demote and writes nothing, because
C6 refuses EVERY commit on a non-green stamp while no launch path checks
the stamp - a demotion before a wave launched would refuse that wave's
unattended landing commit (L873). The gate's exit code is the verdict.

Usage:
    python scripts/pyramid_gate.py --out <artifact> [--root <repo>] -- <pytest args...>
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The tree under test: every module a test can import, every skill file the
# fragment pins read, and the root canonical docs (CLAUDE.md, CHECKLIST.md,
# LEARNINGS.md, EXECUTION_QUEUE.md, STRATEGY_OPTIMISATION_PLAN.md, ...) that
# test_b1486 / test_b2123 / the plan pins read. Cube dirs, output_audit/ and
# data_prefetch/ are NOT in scope: a landing or a heartbeat during the run is
# not an edit to the thing being measured.
SCOPE_DIRS = ("scripts", "backtest", ".claude/skills")
ROOT_GLOBS = ("*.md",)
_SKIP_SUFFIXES = (".pyc", ".pyo")

# EXECUTION_QUEUE.md is IN scope (tests read its vocabulary), but an unattended
# landing appends its own `| **S6-LANDING-...` row to it at any moment (B2520) -
# MEASURED on the B2578 run, where the icg_mult1.25 landing at 16:48:55Z voided
# an otherwise settled tree. Such a row is data the supervisor recorded, not an
# edit to the thing under test, so these files are fingerprinted by a hash of
# their content MINUS the tolerated rows: a landing row is invisible, any other
# character of the file is not.
APPEND_TOLERANT = {"EXECUTION_QUEUE.md": "| **S6-LANDING-"}


def _paths(root: Path) -> list[Path]:
    out: list[Path] = []
    for d in SCOPE_DIRS:
        base = root / d
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts \
                    and not p.name.endswith(_SKIP_SUFFIXES):
                out.append(p)
    for g in ROOT_GLOBS:
        out.extend(p for p in root.glob(g) if p.is_file())
    return sorted(set(out))


def fingerprint(root: Path | str) -> dict[str, tuple]:
    """relative path -> (size, mtime_ns), or ("filtered", sha) for the
    append-tolerant files."""
    root = Path(root)
    fp: dict[str, tuple] = {}
    for p in _paths(root):
        rel = str(p.relative_to(root)).replace(os.sep, "/")
        tol = APPEND_TOLERANT.get(rel)
        try:
            if tol is not None:
                body = "".join(
                    ln for ln in p.read_text(encoding="utf-8",
                                             errors="ignore").splitlines(True)
                    if not ln.startswith(tol))
                fp[rel] = ("filtered",
                           hashlib.sha256(body.encode("utf-8")).hexdigest()[:16])
            else:
                st = p.stat()
                fp[rel] = (st.st_size, st.st_mtime_ns)
        except OSError:
            continue
    return fp


def changed(before: dict, after: dict) -> list[str]:
    """Paths added, removed, or rewritten between two fingerprints."""
    return sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))


def verdict_line(diff: list[str]) -> str:
    if not diff:
        return "tree=SAME"
    shown = ", ".join(diff[:10]) + (" ..." if len(diff) > 10 else "")
    return f"tree=CHANGED ({len(diff)} paths): {shown}"


EXIT_REFUSED_BESIDE_WAVE = 5


def refusal_beside_wave(engine: str, beside_wave: str | None) -> str | None:
    """S6-B3062 (B3108): the refusal message, or None when the gate may run.
    Refuses while ANY runner is in flight - `engine` is _engine_inflight()'s
    answer, and 'unknown' refuses too (fail closed, L642) - unless the
    caller gave a non-empty --beside-wave reason, which the artifact records.
    MEASURED before building it: a pyramid beside the live c14 Step-1 wave
    failed on memory and its RED stamp refused the landing commit 5 of 5
    (L873); pyramids beside the c14 Step-2 wave exhausted commit (L865)."""
    if engine == "none" or (beside_wave or "").strip():
        return None
    return ("REFUSED (S6-B3062, runbook 4.9 Step 2.4): an engine run is in flight - "
            f"{engine}. A pyramid beside a live run has exhausted commit (L865) and "
            "its RED stamp has refused an unattended landing commit (L873). Run "
            "the suite after the run lands, or pass --beside-wave \"<reason>\" to "
            "override; the reason is recorded in the artifact.")


def output_audit_snapshot(root) -> set | None:
    """S6-B3120g: the file names under the PRODUCTION output_audit before
    pytest runs. None when unreadable - reported as such, never treated as
    empty (an empty 'before' would list the whole directory as created)."""
    try:
        return {p.name for p in (Path(root) / "output_audit").iterdir()
                if p.is_file()}
    except OSError:
        return None


def output_audit_created(before, root) -> str:
    """S6-B3120g: files a suite run left in the production output_audit.
    Untracked residue is invisible to the tree fingerprint (tree=SAME held
    while test_b2919 dropped three stubs per run), so the artifact
    DISCLOSES it - a disclosure, not a refusal (L721/L857b): 'none' is the
    only clean reading."""
    if before is None:
        return "unreadable"
    after = output_audit_snapshot(root)
    if after is None:
        return "unreadable"
    new = sorted(after - before)
    return ",".join(new) if new else "none"


def output_audit_state(root) -> dict | None:
    """S6-B3130a (B3135, L880): what the suite's artifact-level pins READ.
    Tracked output_audit files are TEST INPUTS, so they are fingerprinted by
    CONTENT (sha1 - a same-size rewrite with its mtime restored still shows);
    untracked ones by (size, mtime_ns). None when unreadable - reported as
    such, never treated as an empty directory (L642). MEASURED at build: 1,245
    tracked files / 72.1 MB hash in ~5 s, about 10 s per gate run."""
    import hashlib
    root = Path(root)
    if not (root / "output_audit").is_dir():
        return {"tracked": {}, "untracked": {}}   # nothing to move
    try:
        r = subprocess.run(["git", "ls-files", "-z", "output_audit"], cwd=str(root),
                           capture_output=True, timeout=120)
        if r.returncode != 0:
            # S6-B3130a (B3137): outside a repository nothing is TRACKED -
            # every file is fingerprinted by (size, mtime); any other git
            # failure is unreadable, never an empty tracked set (L642)
            if b"not a git repository" not in (r.stderr or b"").lower():
                return None
            tracked = set()
        else:
            tracked = {n for n in r.stdout.decode("utf-8", "replace").split("\0")
                       if n}
        state = {"tracked": {}, "untracked": {}}
        base = root / "output_audit"
        # S6-B3130a (B3137): RECURSIVE - 126 tracked files sit in
        # subdirectories (MEASURED), invisible to a top-level listing
        for p in base.rglob("*") if base.exists() else []:
            if not p.is_file():
                continue
            rel = "output_audit/" + p.relative_to(base).as_posix()
            if rel in tracked:
                h = hashlib.sha1()
                with open(p, "rb") as fh:
                    for chunk in iter(lambda: fh.read(1 << 20), b""):
                        h.update(chunk)
                state["tracked"][rel] = h.hexdigest()
            else:
                st = p.stat()
                state["untracked"][rel] = (st.st_size, st.st_mtime_ns)
        return state
    except (OSError, subprocess.SubprocessError):
        return None


def output_audit_modified(before, root, after=None) -> tuple[str, str]:
    """S6-B3130a: PRE-EXISTING output_audit files rewritten or removed while
    the suite ran - (tracked, untracked), each 'none', a comma list, or
    'unreadable'. A DISCLOSURE, never a refusal (L721): the landing supervisor
    writes here by design (L841), and a line naming the moved inputs is what
    lets a reader tell a green run on moving inputs from a clean one. Files
    CREATED mid-run are output_audit_created's, not this line's."""
    if before is None:
        return "unreadable", "unreadable"
    if after is None:
        after = output_audit_state(root)
    if after is None:
        return "unreadable", "unreadable"
    out = []
    for kind in ("tracked", "untracked"):
        b, a = before[kind], after[kind]
        moved = sorted(n for n in b if a.get(n) != b[n])
        out.append(",".join(moved) if moved else "none")
    return out[0], out[1]


# S6-B3130a (owner ruling 2026-09-29, '6. Yes'): the READ-SET. The pytest
# child loads scripts/pytest_plugins/pyramid_readset.py, which records every
# output_audit file each test OPENED FOR READING and every test that spawned a
# process. When a watched file moved during the run, the gate re-runs EXACTLY
# the tests that read one (or spawned - a child's reads are invisible), or
# marks the run SUSPECT when it cannot. The session writes .pyramid_stamp
# BEFORE the gate has judged the run, so a run the gate does not pass (VOID,
# SUSPECT, a failed re-run) DEMOTES the GREEN stamp this run wrote - otherwise
# C6 would honour a verdict the gate withheld (MEASURED B3137: a tree=CHANGED
# run exited 4 while its GREEN stamp still let commits through).
EXIT_SUSPECT = 6
RERUN_CAP = 150
PLUGIN = "pyramid_readset"
PLUGIN_DIR = Path(__file__).resolve().parent / "pytest_plugins"
READSET_SUFFIX = ".readset.json"
RERUN_READSET_SUFFIX = ".readset_rerun.json"
RERUN_LOG_SUFFIX = ".rerun.txt"
if str(PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR))
from pyramid_readset import ENV_OUT, ENV_ROOT, SESSION  # noqa: E402


def _fold(p: str) -> str:
    p = str(p).replace("\\", "/")
    return p.lower() if os.name == "nt" else p


def output_audit_moved(before, after) -> set | None:
    """Every output_audit path rewritten, removed or created between two
    output_audit_state readings; None when either is unreadable (L642)."""
    if before is None or after is None:
        return None
    out: set = set()
    for kind in ("tracked", "untracked"):
        b, a = before[kind], after[kind]
        out |= {n for n in set(b) | set(a) if b.get(n) != a.get(n)}
    return out


def reads_moved(paths, mv: set) -> bool:
    """Did any recorded read consume a moved path? A FILE read matches its
    own path; a DIRECTORY read (a listing, recorded with a trailing '/')
    matches every moved path beneath it - a created, removed or rewritten
    file under a listed directory changes what the listing returned or what
    the test then opened (B3139, S6-B3130a council)."""
    for p in paths or []:
        f = _fold(p)
        if f.endswith("/"):
            if any(m.startswith(f) for m in mv):
                return True
        elif f in mv:
            return True
    return False


def load_readset(path) -> dict | None:
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) and d.get("schema") == 1 else None


def readset_verdict(readset, moved, cap: int = RERUN_CAP) -> tuple[str, list]:
    """(verdict, node ids to re-run). CLEAN when nothing moved or no test read
    a moved file; RERUN with the exact tests otherwise; SUSPECT when the
    answer cannot be known - an unreadable state or read-set, a moved file
    read at COLLECTION time (every test of that module may carry it), or more
    tests than the re-run cap. A session-level SPAWN does not escalate: the
    session's own stamp writer spawns git at finish."""
    if moved is None:
        return "SUSPECT:output_audit-state-unreadable", []
    if not moved:
        return "CLEAN", []
    if readset is None:
        return "SUSPECT:read-set-unreadable", []
    mv = {_fold(m) for m in moved}
    if reads_moved(readset.get("session"), mv):
        return "SUSPECT:a-collection-time-read-moved", []
    hit = sorted(n for n, ps in (readset.get("tests") or {}).items()
                 if reads_moved(ps, mv))
    spawn = sorted(n for n in (readset.get("spawned") or [])
                   if n != SESSION and n not in hit)
    todo = hit + spawn
    if not todo:
        return "CLEAN:moved-files-read-by-no-test", []
    if len(todo) > cap:
        return f"SUSPECT:{len(todo)}-tests-exceed-rerun-cap-{cap}", []
    return "RERUN", todo


@contextlib.contextmanager
def readset_env(root, readset_path):
    """The plugin's environment for ONE child, restored after. It rides
    os.environ rather than a subprocess keyword, so every caller's
    subprocess.call signature is unchanged; PYTHONPATH gains ONLY the plugin
    directory, never scripts/ (a script named like a stdlib module would
    shadow it in the child)."""
    pp = os.environ.get("PYTHONPATH")
    keys = {ENV_OUT: str(readset_path), ENV_ROOT: str(Path(root).resolve()),
            "PYTHONPATH": str(PLUGIN_DIR) + (os.pathsep + pp if pp else "")}
    saved = {k: os.environ.get(k) for k in keys}
    os.environ.update(keys)
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def gate_own_paths(out, root) -> set:
    """The gate's OWN artifacts - the --out file, its pidfile, the read-set
    files and the re-run log - as folded 'output_audit/...' names, when
    --out sits under root/output_audit. The gate writes them during every
    run (MEASURED: b3127/b3129/b3130_pyramid.out each record
    output_audit_created=<out>,<out>.pid), so they are never a moved INPUT;
    counted, they would re-run every test that lists output_audit on every
    pyramid (B3139, S6-B3130a)."""
    base = (Path(root) / "output_audit").resolve()
    own = set()
    for suffix in ("", ".pid", READSET_SUFFIX, RERUN_READSET_SUFFIX,
                   RERUN_LOG_SUFFIX):
        p = Path(str(out) + suffix).resolve()
        if p.is_relative_to(base):
            own.add(_fold("output_audit/" + p.relative_to(base).as_posix()))
    return own


def minus_gate_own(created: str, own) -> str:
    """S6-B3139l (B3139): the created-files disclosure WITHOUT the gate's
    own --out, .pid and read-set files (gate_own_paths) - the gate writes
    them on every run whose --out sits under output_audit, so counting them
    printed a 'test residue' NOTE on every such run (L721: a NOTE that
    always fires trains its reader to skip it). 'none' / 'unreadable' pass
    through unchanged."""
    if created in ("none", "unreadable"):
        return created
    keep = [n for n in created.split(",")
            if n and _fold("output_audit/" + n) not in own]
    return ",".join(keep) if keep else "none"


def _minus_own(moved, own: set):
    return None if moved is None else {m for m in moved if _fold(m) not in own}


def suite_writes(doc) -> dict:
    """{folded output_audit path: [node ids]} for every in-process WRITE the
    read-set recorded (B3139, S6-B3130a). A spawned child's writes are not
    here - the audit hook sees this interpreter only - though a child's write
    that CHANGES a file still shows in output_audit_modified_*."""
    out: dict = {}
    for node, paths in sorted(((doc or {}).get("writes") or {}).items()):
        for p in paths or []:
            out.setdefault(_fold(p), []).append(node)
    return out


def suite_writes_line(doc, own=frozenset(), limit: int = 6) -> str:
    """The footer's readset_suite_writes= value: every output_audit path a
    test of this run WROTE in-process (L689 - a test driving production code
    is production code for the run), minus the gate's own files, each with
    the first test that wrote it. 'unreadable' when the read-set is."""
    if doc is None:
        return "unreadable"
    w = sorted((p, ns) for p, ns in suite_writes(doc).items() if p not in own)
    if not w:
        return "none"
    shown = [p + "<-" + ns[0].split("::")[-1]
             + (f"(+{len(ns) - 1})" if len(ns) > 1 else "") for p, ns in w[:limit]]
    more = f"; +{len(w) - limit} more" if len(w) > limit else ""
    return f"{len(w)}: " + "; ".join(shown) + more


def rerun_settled(v2: str, moved2, doc2) -> str | None:
    """None when the read-set re-run settled, else its SUSPECT reason. When
    EVERY path that moved during the re-run was written in-process by the
    re-run's own tests, the suite moved its own input (L689) and the reason
    names the paths - the generic reason cost B3139 a diagnosis to find a
    test rewriting output_audit/workflow_state.json on every pyramid."""
    if not (v2 == "RERUN" or v2.startswith("SUSPECT")):
        return None
    mv = {_fold(m) for m in (moved2 or ())}
    if mv and mv <= set(suite_writes(doc2)):
        return "SUSPECT:rerun-tests-rewrote-" + ",".join(sorted(mv))
    return "SUSPECT:inputs-moved-again-during-rerun"


def readset_decide(out, root, st_before, st_after, readset_path) -> tuple[str, str]:
    """Judge the main run's read-set; when it names tests, re-run EXACTLY
    those once on the now-settled inputs and judge that run the same way."""
    own = gate_own_paths(out, root)
    moved = _minus_own(output_audit_moved(st_before, st_after), own)
    doc = load_readset(readset_path)
    verdict, todo = readset_verdict(doc, moved)
    if verdict != "RERUN":
        return verdict, "none"
    addr = (doc or {}).get("addr") or {}
    args = [addr.get(n, n) for n in todo]
    rs2 = Path(str(out) + RERUN_READSET_SUFFIX)
    rs2.unlink(missing_ok=True)
    log2 = Path(str(out) + RERUN_LOG_SUFFIX)
    st1 = output_audit_state(root)
    with open(log2, "w", encoding="utf-8") as fh2, readset_env(root, rs2):
        rc2 = subprocess.call([sys.executable, "-m", "pytest", "-p", PLUGIN,
                               "-q", "-p", "no:cacheprovider", *args],
                              stdout=fh2, stderr=subprocess.STDOUT, cwd=str(root))
    doc2 = load_readset(rs2)
    moved2 = _minus_own(output_audit_moved(st1, output_audit_state(root)), own)
    v2, _ = readset_verdict(doc2, moved2, cap=10 ** 9)
    line = f"{len(todo)} tests rc={rc2} log={log2.name}"
    if rc2 != 0:
        return f"RERUN-FAILED:{len(todo)}-tests", line
    unsettled = rerun_settled(v2, moved2, doc2)
    if unsettled:
        return unsettled, line
    return f"RERUN-PASS:{len(todo)}-tests", line


# S6-B3130a (B3139, council 5 of 5): the owner approved the READ-SET, never
# the DEMOTION. False = disclose what would happen (would-demote) and write
# nothing; flipping it is the owner's ruling, together with a launch-time
# GREEN-stamp check so a landing can never be the commit a demotion blocks.
DEMOTION_ENABLED = False


def bind_stamp(root, t0: float, final: int, reason: str) -> str:
    """Demote the GREEN .pyramid_stamp THIS run wrote when the gate does not
    pass the run (final != 0) - only while DEMOTION_ENABLED; until then the
    same case returns 'would-demote' and the stamp is left as written. A
    stamp older than the run is not this run's and is never touched (a
    partial run through the gate writes none)."""
    p = Path(root) / ".pyramid_stamp"
    if not p.exists():
        return "no-stamp"
    try:
        stamp = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "unreadable"
    if float(stamp.get("timestamp", 0) or 0) < t0:
        return "not-this-run"
    if final == 0:
        return "kept-green" if stamp.get("green") else "kept-red"
    if not stamp.get("green"):
        return "already-red"
    if not DEMOTION_ENABLED:
        return "would-demote"
    stamp.update(green=False, gate_exit=int(final), gate_verdict=str(reason)[:200])
    p.write_text(json.dumps(stamp), encoding="utf-8")
    return "demoted"


def run(out: Path, root: Path, pytest_args: list[str],
        beside_wave: str | None = None) -> int:
    engine_start = _engine_inflight()
    refused = refusal_beside_wave(engine_start, beside_wave)
    if refused:
        Path(out).write_text(refused + "\nexit=%d\n" % EXIT_REFUSED_BESIDE_WAVE,
                             encoding="utf-8")
        print(refused)
        return EXIT_REFUSED_BESIDE_WAVE
    oa_before = output_audit_snapshot(root)
    oa_state_before = output_audit_state(root)
    before = fingerprint(root)
    t0 = time.time()
    chain_start = _chain_inflight()
    # B2856 (S6-B2854b): a stopper needs the TREE, not the wrapper. TaskStop
    # on the launching shell orphans this process and its pytest child (four
    # processes were hand-killed at B2854, two racing on one artifact). The
    # pidfile beside the artifact lets kill_gate_tree.py find the tree root;
    # removed on normal completion, so a LEFTOVER pidfile marks a killed or
    # crashed gate - and its PID is re-verified by command line before any
    # kill, because PIDs are reused.
    import os
    pidfile = Path(str(out) + ".pid")
    pidfile.write_text(str(os.getpid()), encoding="utf-8")
    readset_path = Path(str(out) + READSET_SUFFIX)
    readset_path.unlink(missing_ok=True)
    try:
        with open(out, "w", encoding="utf-8") as fh, \
                readset_env(root, readset_path):
            rc = subprocess.call([sys.executable, "-m", "pytest", "-p", PLUGIN,
                                  *pytest_args],
                                 stdout=fh, stderr=subprocess.STDOUT, cwd=str(root))
        diff = changed(before, fingerprint(root))
        final = 4 if diff else rc
        # the main run's output_audit disclosures, read BEFORE any re-run
        oa_state_after = output_audit_state(root)
        oa_created = output_audit_created(oa_before, root)
        # S6-B3139l: the gate's own out / pid / read-set files are never
        # test residue (they are subtracted from 'moved' the same way)
        oa_created = minus_gate_own(oa_created, gate_own_paths(out, root))
        oa_mod_tracked, oa_mod_untracked = output_audit_modified(
            oa_state_before, root, oa_state_after)
        # S6-B3130a: judge the read-set; re-run exactly the named tests
        rs_verdict, rs_rerun = readset_decide(
            out, root, oa_state_before, oa_state_after, readset_path)
        rs_writes = suite_writes_line(load_readset(readset_path),
                                      gate_own_paths(out, root))
        if final == 0 and rs_verdict.startswith("SUSPECT"):
            final = EXIT_SUSPECT
        elif final == 0 and rs_verdict.startswith("RERUN-FAILED"):
            final = 1
        binding = bind_stamp(root, t0, final,
                             verdict_line(diff) if diff else rs_verdict)
        # S6-B3061 (L621): a pyramid is CPU-heavy and the engine is
        # timing-sensitive. L621 says hold it until the completion line
        # and NOTHING ENFORCED THAT - 30 gate runs landed inside one
        # campaign window at ~45 pct duty cycle, and the configs that
        # ran alongside them were 61 pct slower than those that did not.
        # This RECORDS the contention rather than refusing: a refusal
        # over a 40-hour chain would block every commit for the rest of
        # it, which is L721 tightening-over-a-backlog. A disclosure costs
        # nothing and keeps the per-config runtime record readable.
        # S6-B3063: sampling only HERE reads the state AFTER pytest has
        # returned, so a config that LANDED mid-run reads 'none' despite
        # having contended for most of it, and one that LAUNCHED late
        # reads as in flight although it barely overlapped. Record BOTH
        # ends: 'none' on both is the only honest all-clear.
        chain_end = _chain_inflight()
        chain = chain_start if chain_start != "none" else chain_end
        engine_end = _engine_inflight()
        engine = engine_start if engine_start != "none" else engine_end
        engine_dead = _engine_dead_within_window()
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(f"\npytest_exit={rc}\n{verdict_line(diff)}\nexit={final}\n"
                     f"elapsed_s={time.time() - t0:.0f}\n"
                     f"chain_inflight={chain}\n"
                     f"chain_inflight_start={chain_start}\n"
                     f"chain_inflight_end={chain_end}\n"
                     f"engine_inflight={engine}\n"
                     f"engine_inflight_start={engine_start}\n"
                     f"engine_inflight_end={engine_end}\n"
                     f"engine_dead_within_window={engine_dead}\n"
                     f"beside_wave_override={(beside_wave or '').strip() or 'none'}\n"
                     f"output_audit_created={oa_created}\n"
                     f"output_audit_modified_tracked={oa_mod_tracked}\n"
                     f"output_audit_modified_untracked={oa_mod_untracked}\n"
                     f"readset={rs_verdict}\n"
                     f"readset_rerun={rs_rerun}\n"
                     f"readset_suite_writes={rs_writes}\n"
                     f"stamp_binding={binding}\n")
        print(f"pytest_exit={rc} {verdict_line(diff)} exit={final}")
        if chain != "none":
            print("  NOTE (L621/S6-B3061): a config was IN FLIGHT while "
                  "this pyramid ran - %s. Its wall-clock is contended."
                  % chain)
        if engine != "none":
            print("  NOTE (B3091/runbook Step 2.4): an ENGINE heartbeat was fresh "
                  "while this pyramid ran - %s. A pyramid beside a live "
                  "wave can exhaust commit; runbook Step 2.4 says run the "
                  "full suite BEFORE the launch - there is no leg-boundary window."
                  % engine)
        if oa_mod_tracked not in ("none", "unreadable"):
            print("  NOTE (S6-B3130a/L880): TRACKED output_audit file(s) were "
                  "rewritten while this suite ran - artifact-level pins may "
                  "have read moving inputs: %s" % oa_mod_tracked)
        if rs_verdict != "CLEAN":
            print("  NOTE (S6-B3130a): read-set %s (re-run: %s; stamp: %s)"
                  % (rs_verdict, rs_rerun, binding))
        if rs_writes not in ("none", "unreadable"):
            print("  NOTE (S6-B3130a/L689): test(s) WROTE under the production "
                  "output_audit in-process: %s" % rs_writes)
        if oa_created not in ("none", "unreadable"):
            print("  NOTE (S6-B3120g): this suite run CREATED file(s) under "
                  "the production output_audit - test residue: %s"
                  % oa_created)
        return final
    finally:
        pidfile.unlink(missing_ok=True)


ENGINE_FRESH_S = 3600

# S6-B3093c (B3099): a runner is a python process whose SCRIPT argument is one of
# these. The venv launcher and the interpreter it starts both carry the same
# command line, so labels are de-duplicated; pool workers (`-c spawn_main`) are
# children of a runner and are not runners themselves.
# S6-B2556a (B3139): ONE shared definition (scripts/runner_scripts.py); the
# in-flight check reads the processes that ARE a run while alive.
from runner_scripts import RUN_PROCESSES as RUNNER_SCRIPTS  # noqa: E402


def _python_argvs():
    """[(pid, argv)] for every running python process, read IN-PROCESS - ctypes
    on Windows (EnumProcesses, then NtQueryInformationProcess class 60 for the
    command line, split by CommandLineToArgvW exactly as Windows splits it),
    /proc elsewhere. No PowerShell, so it still answers under the commit
    exhaustion this gate exists to report (runbook Step 2.5). A process whose
    command line cannot be read yields argv None. Returns None when the table
    itself cannot be read."""
    if os.name != "nt":
        rows = []
        for d in Path("/proc").iterdir():
            if not d.name.isdigit():
                continue
            try:
                parts = (d / "cmdline").read_bytes().split(b"\0")
            except OSError:
                continue
            argv = [x.decode("utf-8", "replace") for x in parts if x]
            if argv and "python" in argv[0].rsplit("/", 1)[-1]:
                rows.append((int(d.name), argv))
        return rows
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    ntdll = ctypes.WinDLL("ntdll")
    shell32 = ctypes.WinDLL("shell32")
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    k32.CloseHandle.argtypes = (wintypes.HANDLE,)
    k32.LocalFree.argtypes = (ctypes.c_void_p,)
    k32.QueryFullProcessImageNameW.argtypes = (
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD))
    ntdll.NtQueryInformationProcess.restype = ctypes.c_long
    ntdll.NtQueryInformationProcess.argtypes = (
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.ULONG,
        ctypes.POINTER(wintypes.ULONG))
    shell32.CommandLineToArgvW.restype = ctypes.POINTER(wintypes.LPWSTR)
    shell32.CommandLineToArgvW.argtypes = (wintypes.LPCWSTR,
                                           ctypes.POINTER(ctypes.c_int))

    class _US(ctypes.Structure):
        _fields_ = [("Length", ctypes.c_ushort),
                    ("MaximumLength", ctypes.c_ushort),
                    ("Buffer", ctypes.c_void_p)]
    cap = 4096
    while True:
        arr = (wintypes.DWORD * cap)()
        needed = wintypes.DWORD()
        if not psapi.EnumProcesses(arr, ctypes.sizeof(arr), ctypes.byref(needed)):
            return None
        if needed.value < ctypes.sizeof(arr):
            break
        cap *= 2
    rows = []
    for pid in arr[:needed.value // ctypes.sizeof(wintypes.DWORD)]:
        if not pid:
            continue
        h = k32.OpenProcess(0x1000, False, pid)   # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            continue
        try:
            img = ctypes.create_unicode_buffer(1024)
            size = wintypes.DWORD(1024)
            if not k32.QueryFullProcessImageNameW(h, 0, img, ctypes.byref(size)):
                continue
            if not img.value.lower().endswith(("python.exe", "pythonw.exe")):
                continue
            ln = wintypes.ULONG(0)
            ntdll.NtQueryInformationProcess(h, 60, None, 0, ctypes.byref(ln))
            buf = ctypes.create_string_buffer(ln.value or 1)
            if not ln.value or ntdll.NtQueryInformationProcess(
                    h, 60, buf, ln, ctypes.byref(ln)) != 0:
                rows.append((pid, None))
                continue
            us = _US.from_buffer(buf)
            cmd = ctypes.wstring_at(us.Buffer, us.Length // 2)
            argc = ctypes.c_int(0)
            av = shell32.CommandLineToArgvW(cmd, ctypes.byref(argc))
            if not av:
                rows.append((pid, None))
                continue
            try:
                rows.append((pid, [av[i] for i in range(argc.value)]))
            finally:
                k32.LocalFree(av)
        finally:
            k32.CloseHandle(h)
    return rows


def _runner_label(argv):
    """The runner a python argv executes - 'run_wave:<spec>' or
    'run_phase1a:<out dir>' - or None. Decided by the SCRIPT argument only:
    `-c` code that merely NAMES a runner is not a launch (B1603's rule),
    and `-m pytest` is not a runner."""
    if not argv or len(argv) < 2 or str(argv[1]).startswith("-"):
        return None
    name = str(argv[1]).replace("\\", "/").rsplit("/", 1)[-1]
    if name not in RUNNER_SCRIPTS:
        return None
    for flag in ("--output-dir", "--spec"):
        if flag in argv[2:]:
            i = argv.index(flag, 2)
            if i + 1 < len(argv):
                return f"{name[:-3]}:" + str(argv[i + 1]).replace(
                    "\\", "/").rstrip("/").rsplit("/", 1)[-1]
    return name[:-3]


def _engine_heartbeats(root=None, now=None):
    """[(out dir name, heartbeat pid)] for heartbeats touched within
    ENGINE_FRESH_S under <root>/output_*."""
    import json as _j
    import time as _t
    now = _t.time() if now is None else now
    out = []
    for hb in Path(root or ROOT).glob("output_*/run_heartbeat.json"):
        try:
            if now - hb.stat().st_mtime > ENGINE_FRESH_S:
                continue
            pid = _j.loads(hb.read_text(encoding="utf-8")).get("pid")
        except (OSError, ValueError):
            pid = None
        out.append((hb.parent.name, pid))
    return out


def _engine_inflight(now=None, rows=None, root=None) -> str:
    """B3091 -> S6-B3093c (B3099): is an ENGINE running right now, by ANY launch
    path, in ANY output dir?

    B3091 read heartbeat AGE, so a dead run's last heartbeat kept it 'in
    flight' for up to an hour (MEASURED B3093). A pid check on the heartbeat
    alone fails the other way: between legs the engine has exited while
    run_wave is alive and about to start the next leg. The process table
    answers the question itself: every running python whose script is a
    runner (RUNNER_SCRIPTS) is in flight, labelled by its --output-dir or
    --spec. When the table cannot be read, the answer is 'unknown' - which
    every caller treats as in flight (fail closed). `rows` and `root` are the
    test seams. Never raises."""
    try:
        rows = _python_argvs() if rows is None else rows
        if rows is None:
            return "unknown"
        live = sorted({lbl for _pid, argv in rows
                       if (lbl := _runner_label(argv))})
        unreadable = [pid for pid, argv in rows if argv is None]
        if unreadable and not live:
            return "unknown(unreadable python pid %s)" % unreadable[0]
        return ",".join(live) if live else "none"
    except Exception:
        return "unknown"


def _engine_dead_within_window(now=None, rows=None, root=None) -> str:
    """S6-B3093c: fresh heartbeats whose engine pid is NOT running - the case
    B3091 reported as in flight. Disclosed separately, never as a contention.
    'unknown' when the process table cannot be read."""
    try:
        rows = _python_argvs() if rows is None else rows
        if rows is None:
            return "unknown"
        pids = {pid for pid, _argv in rows}
        dead = sorted(d for d, pid in _engine_heartbeats(root, now)
                      if pid not in pids)
        return ",".join(dead) if dead else "none"
    except Exception:
        return "unknown"


def _chain_inflight() -> str:
    """S6-B3061 (L621): is a serial-chain config running right now?

    Reads the chain log the way every other consumer does - a LAUNCH with
    no matching finished line is in flight. Returns the wave name(s) or
    "none". Never raises: a disclosure that could break the gate it
    annotates would be worse than no disclosure at all.
    """
    try:
        import re as _re
        log = ROOT / "output_audit" / "serial_chain.log"
        if not log.exists():
            return "none"
        pend = {}
        for line in log.read_text(encoding="utf-8", errors="replace").split("\n"):
            m = _re.match(r"\S+Z LAUNCH (\S+)", line)
            if m:
                pend[m.group(1)] = True
                continue
            m = _re.match(r"\S+Z (\S+) finished", line)
            if m:
                pend.pop(m.group(1), None)
        return ",".join(sorted(pend)) if pend else "none"
    except Exception:
        return "unknown"

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, help="the pyramid artifact (stdout+stderr of pytest, then the verdict lines)")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--beside-wave", default=None, metavar="REASON",
                    help="S6-B3062: run even though an engine run is in flight; "
                         "the reason is recorded in the artifact")
    ap.add_argument("pytest_args", nargs=argparse.REMAINDER,
                    help="everything after `--` goes to pytest verbatim")
    a = ap.parse_args(argv)
    args = [x for x in a.pytest_args if x != "--"]
    if not args:
        args = ["backtest/tests/test_unit.py", "backtest/tests/test_integration.py",
                "-q", "-p", "no:cacheprovider"]
    return run(Path(a.out), Path(a.root), args, beside_wave=a.beside_wave)


if __name__ == "__main__":
    sys.exit(main())
