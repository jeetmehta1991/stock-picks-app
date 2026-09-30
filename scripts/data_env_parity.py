#!/usr/bin/env python
"""L889 (B3139): before comparing runs of TWO code trees, prove they read the
SAME data.

WHY. A git worktree carries only TRACKED files; most of the engine's data -
the OHLCV cache (backtest/data/cache, anchored on the module's own path) and
data_prefetch/ - is gitignored, but both roots also hold TRACKED files
(149,783 and 4,654 at B3139), so after `git worktree add` each root EXISTS
holding its tracked part only. launch_sweep.materialise_worktree (B2133)
linked a root only when it did not exist, so it linked nothing; since B3139
it merge-links and refuses unless this check passes. MEASURED at B3139: the
S6-B3134a engine slice compared the MAIN tree
(old engine) with a hand-built worktree (new engine) that lacked 4,342 decoded
SEC filings (data_prefetch/sec_edgar_decoded) - and claim (1), old == legacy,
failed on exactly the ticker most exposed to them (25 of 27 old-only entries
on JPM). The comparison measured the data gap, not the code.

WHAT IT CHECKS, per data root (LINKED_DATA_DIRS from launch_sweep, plus the
universe CSVs): every directory's file count and byte total, walked on both
sides; a directory present on one side only, or differing, is a DIFFERENCE.
Files whose content differs only by line endings are compared normalised (a
pandas reader cannot tell them apart), so they are not a difference.

Read-only. Exit 0 = the data environments are identical; 1 = a difference
(each printed); 3 = a root unreadable.

Usage: python scripts/data_env_parity.py --left <tree> --right <tree>
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if not (ROOT / "EXECUTION_QUEUE.md").is_file():          # L846 marker rule
    raise SystemExit(f"data_env_parity: {ROOT} is not the repo root (L846)")
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

UNIVERSE = "Backtesting universe"


def data_roots() -> tuple:
    """The engine's data roots: launch_sweep's LINKED_DATA_DIRS (one
    definition, L593) plus the universe CSVs the loaders read."""
    from launch_sweep import LINKED_DATA_DIRS
    return tuple(LINKED_DATA_DIRS) + (UNIVERSE,)


def _norm_size(p: Path) -> int:
    b = p.read_bytes()
    return len(b.replace(b"\r\n", b"\n"))


def census(tree: Path, rel: str, normalise_text: bool) -> dict:
    """{relative dir: (files, bytes)} for every directory under tree/rel,
    following junctions (a linked data dir is data the engine reads)."""
    out = {}
    top = tree / rel
    if not top.exists():
        return out
    for dirpath, dirnames, filenames in os.walk(top, followlinks=True):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        n = b = 0
        for f in filenames:
            if f.endswith((".py", ".pyc")):
                continue
            fp = Path(dirpath) / f
            try:
                b += _norm_size(fp) if (normalise_text and f.endswith(".csv")) else fp.stat().st_size
                n += 1
            except OSError as e:
                # #122: an unreadable file is uncounted on THIS side only, so
                # it can silently manufacture (or hide) a parity difference -
                # say so where the verdict is read.
                print(f"PARITY WARNING: unreadable, not counted: {fp} ({e})",
                      file=sys.stderr)
        out[str(Path(dirpath).relative_to(tree)).replace("\\", "/")] = (n, b)
    return out


def differences(left: Path, right: Path, roots=None) -> list[tuple]:
    out = []
    for rel in (roots or data_roots()):
        norm = rel == UNIVERSE
        a, b = census(left, rel, norm), census(right, rel, norm)
        for d in sorted(set(a) | set(b)):
            if a.get(d) != b.get(d):
                out.append((d, a.get(d), b.get(d)))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--left", required=True)
    ap.add_argument("--right", required=True)
    a = ap.parse_args(argv)
    left, right = Path(a.left), Path(a.right)
    for t in (left, right):
        if not t.is_dir():
            print(f"[FAIL] not a directory: {t}")
            return 3
    diffs = differences(left, right)
    for d, x, y in diffs:
        print(f"DIFFERS {d}: left {x} | right {y}")
    print("VERDICT:", "the data environments are IDENTICAL" if not diffs
          else f"{len(diffs)} data director(ies) DIFFER - a cross-tree comparison "
               "would measure the data, not the code (L889)")
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main())
