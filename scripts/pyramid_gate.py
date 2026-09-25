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

Usage:
    python scripts/pyramid_gate.py --out <artifact> [--root <repo>] -- <pytest args...>
"""
from __future__ import annotations

import argparse
import hashlib
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


def run(out: Path, root: Path, pytest_args: list[str],
        beside_wave: str | None = None) -> int:
    engine_start = _engine_inflight()
    refused = refusal_beside_wave(engine_start, beside_wave)
    if refused:
        Path(out).write_text(refused + "\nexit=%d\n" % EXIT_REFUSED_BESIDE_WAVE,
                             encoding="utf-8")
        print(refused)
        return EXIT_REFUSED_BESIDE_WAVE
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
    try:
        with open(out, "w", encoding="utf-8") as fh:
            rc = subprocess.call([sys.executable, "-m", "pytest", *pytest_args],
                                 stdout=fh, stderr=subprocess.STDOUT, cwd=str(root))
        diff = changed(before, fingerprint(root))
        final = 4 if diff else rc
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
                     f"beside_wave_override={(beside_wave or '').strip() or 'none'}\n")
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
        return final
    finally:
        pidfile.unlink(missing_ok=True)


ENGINE_FRESH_S = 3600

# S6-B3093c (B3099): a runner is a python process whose SCRIPT argument is one of
# these. The venv launcher and the interpreter it starts both carry the same
# command line, so labels are de-duplicated; pool workers (`-c spawn_main`) are
# children of a runner and are not runners themselves.
RUNNER_SCRIPTS = ("run_phase1a.py", "run_wave.py", "run_serial_chain.py",
                  "launch_sweep.py")


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
