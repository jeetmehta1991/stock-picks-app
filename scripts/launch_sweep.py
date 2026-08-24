#!/usr/bin/env python
"""The ONE launch path for sweep/engine runs (B2082, S6-B1704c option c,
owner-approved 2026-08-23).

WHY: prelaunch_gate.py had ZERO automatic callers (B1704 audit) - the launch
path was a direct run_phase1a.py invocation that never consulted it, so the
PRE-SPEND OBSOLESCENCE GATE (B1335 rule 1) was hand-run or skipped. This
wrapper makes the gate structurally unskippable for any launch that goes
through it, and the A1 design (b2079) requires every wave launch to.

WHAT IT DOES, in order:
  1. runs prelaunch_gate.py --manifest <manifest>; NON-ZERO EXIT = REFUSE
     (exit 2, engine never invoked)
  2. launches the engine via sys.executable (never bare `python` - L573)
     with the caller's args, capturing t0/sha into the summary log
  3. on exit: appends the run_cfg-style line
     `CFG=<tag> EXIT=<rc> ELAPSED=<s> CUBE_ROWS=<n|ABSENT>` - the L566
     lesson: liveness is rows produced, never exit code alone
  4. exits with the child's return code

USAGE:
  PYTHONPATH=. python scripts/launch_sweep.py --manifest <dir>/run_manifest.json \
      --output-dir <dir> --tag cfg1 [--summary-log <path>] -- <run_phase1a args...>

The `--engine-cmd` override exists ONLY as the test seam (B1761: a gate with
no seam cannot be distinguished from a gate that does nothing); production
callers never pass it.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def gate_passes(manifest: str) -> bool:
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "prelaunch_gate.py"),
                        "--manifest", manifest], cwd=str(ROOT))
    return r.returncode == 0


# B2127 (S6-B2122a, cheap half): the manifest's `isolation: true` was an
# UNENFORCED FIELD - the engine has always run from the live working tree, so
# a commit landing mid-wave silently split a wave across engine versions. Real
# isolation (a worktree pinned at the frozen sha) is the full fix; this is the
# DETECTION half, which ships today: refuse to launch when HEAD has moved off
# the manifest's frozen_sha, or when an engine-consumed path is dirty.
ENGINE_PATHS = ("backtest/engine", "backtest/signals", "backtest/data",
                "backtest/config.py", "backtest/run_phase1a.py")


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(ROOT),
                          capture_output=True, text=True).stdout.strip()


def drift_check(manifest: str) -> list[str]:
    """Return the reasons this launch is NOT reproducible. Empty = clean."""
    reasons = []
    try:
        m = json.loads(Path(manifest).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"manifest unreadable: {exc!r}"]
    if m.get("allow_engine_drift"):
        return []                      # explicit, recorded waiver
    frozen = (m.get("frozen_sha") or "").strip()
    head = _git("rev-parse", "HEAD")
    if frozen and head and not head.startswith(frozen[:12])             and not frozen.startswith(head[:12]):
        reasons.append(f"HEAD {head[:12]} != manifest frozen_sha {frozen[:12]} "
                       "- a commit landed since this wave's manifest was written")
    dirty = [ln for ln in _git("status", "--porcelain").splitlines()
             if any(p in ln.replace("\\", "/") for p in ENGINE_PATHS)]
    if dirty:
        reasons.append("engine-consumed paths are dirty: "
                       + "; ".join(d.strip() for d in dirty[:5]))
    return reasons


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--tag", default="cfg")
    ap.add_argument("--summary-log", default=None)
    ap.add_argument("--engine-cmd", default=None,
                    help="TEST SEAM ONLY - overrides the engine invocation")
    ap.add_argument("engine_args", nargs="*")
    a = ap.parse_args(argv)

    if not gate_passes(a.manifest):
        print(f"LAUNCH REFUSED: prelaunch_gate failed for {a.manifest} - "
              "fix the manifest; the engine was NOT invoked.")
        return 2

    drift = drift_check(a.manifest)
    if drift:
        print("LAUNCH REFUSED (B2127 engine drift): the engine runs from the "
              "LIVE WORKING TREE, so this launch would not reproduce the "
              "manifest's pinned code. The engine was NOT invoked.")
        for r in drift:
            print(f"  - {r}")
        print("  Fix: commit/stash the engine change and regenerate the "
              "manifest, or set allow_engine_drift=true in the manifest to "
              "record the exception deliberately.")
        return 2

    out_dir = Path(a.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = Path(a.summary_log) if a.summary_log else out_dir / "launch_summary.log"
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(ROOT),
                         capture_output=True, text=True).stdout.strip()
    t0 = time.time()
    with summary.open("a", encoding="utf-8") as f:
        f.write(f"LAUNCH tag={a.tag} t0={int(t0)} sha={sha} manifest={a.manifest}\n")

    if a.engine_cmd:
        cmd = [sys.executable, a.engine_cmd] + list(a.engine_args)
    else:
        cmd = ([sys.executable, str(ROOT / "backtest" / "run_phase1a.py")]
               + list(a.engine_args) + ["--output-dir", str(out_dir)])
    rc = subprocess.run(cmd, cwd=str(ROOT)).returncode

    cube = out_dir / "trade_exit_detail.csv"
    rows = "ABSENT"
    if cube.exists():
        with cube.open(encoding="utf-8", errors="replace") as f:
            rows = str(sum(1 for _ in f))
    with summary.open("a", encoding="utf-8") as f:
        f.write(f"CFG={a.tag} EXIT={rc} ELAPSED={int(time.time() - t0)} "
                f"CUBE_ROWS={rows}\n")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
