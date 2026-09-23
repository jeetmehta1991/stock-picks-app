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


def run(out: Path, root: Path, pytest_args: list[str]) -> int:
    before = fingerprint(root)
    t0 = time.time()
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
        chain = _chain_inflight()
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(f"\npytest_exit={rc}\n{verdict_line(diff)}\nexit={final}\n"
                     f"elapsed_s={time.time() - t0:.0f}\n"
                     f"chain_inflight={chain}\n")
        print(f"pytest_exit={rc} {verdict_line(diff)} exit={final}")
        if chain != "none":
            print("  NOTE (L621/S6-B3061): a config was IN FLIGHT while "
                  "this pyramid ran - %s. Its wall-clock is contended."
                  % chain)
        return final
    finally:
        pidfile.unlink(missing_ok=True)


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
    ap.add_argument("pytest_args", nargs=argparse.REMAINDER,
                    help="everything after `--` goes to pytest verbatim")
    a = ap.parse_args(argv)
    args = [x for x in a.pytest_args if x != "--"]
    if not args:
        args = ["backtest/tests/test_unit.py", "backtest/tests/test_integration.py",
                "-q", "-p", "no:cacheprovider"]
    return run(Path(a.out), Path(a.root), args)


if __name__ == "__main__":
    sys.exit(main())
