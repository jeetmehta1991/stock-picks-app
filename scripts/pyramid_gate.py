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
    with open(out, "w", encoding="utf-8") as fh:
        rc = subprocess.call([sys.executable, "-m", "pytest", *pytest_args],
                             stdout=fh, stderr=subprocess.STDOUT, cwd=str(root))
    diff = changed(before, fingerprint(root))
    final = 4 if diff else rc
    with open(out, "a", encoding="utf-8") as fh:
        fh.write(f"\npytest_exit={rc}\n{verdict_line(diff)}\nexit={final}\n"
                 f"elapsed_s={time.time() - t0:.0f}\n")
    print(f"pytest_exit={rc} {verdict_line(diff)} exit={final}")
    return final


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
