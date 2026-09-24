#!/usr/bin/env python
"""S6-B3093a (B3099): which repo files does the PER-LEG launch gate open?

WHY: drift_check allows a mid-wave commit only to paths no leg can read. What a
leg reads cannot be reliably read off the source - MEASURED B3099: filename
literals in the 33-module per-leg closure named EXECUTION_QUEUE.md, which the
gate never opens, while PHASE_1B_ROSTER.md and
output_audit/phase_1b_step2_admissions.json, which it does open, looked like
docs and artifacts. So this runs scripts/prelaunch_gate.py IN-PROCESS under a
sys.addaudithook and records every file under the repo it opens.

Run it as its own process (an audit hook cannot be removed once added):
    python scripts/leg_read_set.py --manifest <out_dir>/run_manifest.json --out reads.json
Writes {"exit": <gate exit code>, "data_files": [...], "python_files": N}.
A gate that REFUSES exits early and opens less; callers check exit == 0.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import runpy
import sys
from pathlib import Path

_MARKER = Path("scripts") / "prelaunch_gate.py"


def _repo_root() -> Path:
    """The repo by MARKER, never by where this file happens to sit (#305 / L846:
    a draft run from another directory resolved a tree that does not exist).
    Tries this file's grandparent, then the cwd; refuses a tree neither
    confirms."""
    for cand in (Path(__file__).resolve().parent.parent, Path.cwd().resolve()):
        if (cand / _MARKER).is_file():
            return cand
    raise SystemExit(f"REFUSED: no {_MARKER} above {__file__} or in the cwd - "
                     "run from the repo root")


ROOT = _repo_root()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    root = ROOT.resolve()
    opened: set[str] = set()

    def hook(event, args):
        if event != "open" or not args:
            return
        try:
            p = Path(os.fsdecode(args[0])).resolve()
            rel = p.relative_to(root).as_posix()
        except (TypeError, ValueError, OSError):
            return
        if "__pycache__" not in rel:
            opened.add(rel)

    manifest = str(Path(a.manifest).resolve())
    sys.addaudithook(hook)
    os.chdir(root)
    if str(root / "scripts") not in sys.path:
        sys.path.insert(0, str(root / "scripts"))
    sys.argv = ["prelaunch_gate.py", "--manifest", manifest]
    rc = 0
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            runpy.run_path(str(root / "scripts" / "prelaunch_gate.py"),
                           run_name="__main__")
        except SystemExit as exc:
            rc = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    doc = {"exit": rc,
           "data_files": sorted(r for r in opened if not r.endswith(".py")),
           "python_files": sum(1 for r in opened if r.endswith(".py"))}
    Path(a.out).write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print(f"gate exit {rc}; {doc['python_files']} python files, "
          f"{len(doc['data_files'])} data files opened")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
