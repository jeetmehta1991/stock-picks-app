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
import os
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


def arm_env_matches(manifest_path: str, environ) -> list[str]:
    """B2168 (S6-B2153a): the manifest's `arms` declared config-defining env
    values (SMC_SWING_LENGTH is P1, STRAT_EMA_SPAN is P6) and NOTHING read
    them - the field survived the B2128c sweep unread. A stale shell var, or
    an UNSET one (which silently means the engine default), makes the
    manifest lie about which config a cube is: the exact class that nearly
    re-graded a swing-10 cube as swing-20 (S6-B2136). Fail CLOSED both ways.

    Arms declare env two ways: modern specs carry arm["env"] = {K: V}; the
    b2070/b2114-era manifests carry UPPERCASE keys flat on the arm. Both are
    enforced. `concurrency` is prose and deliberately NOT enforced (L643: a
    FEATURE field, not a bound).
    """
    import json as _j
    from pathlib import Path as _P
    try:
        m = _j.loads(_P(manifest_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []                       # unreadable manifest is the gate's job
    reasons = []
    for arm in (m.get("arms") or []):
        declared = dict(arm.get("env") or {})
        for k, v in arm.items():        # flat legacy style
            if k.isupper():
                declared[k] = v
        for k, v in declared.items():
            live = environ.get(k)
            if live is None:
                reasons.append(
                    f"arm '{arm.get('tag', '?')}' declares {k}={v} but the "
                    f"variable is UNSET - the engine would run its DEFAULT "
                    f"and the manifest would lie about which config this is "
                    f"(the S6-B2136 class)")
            elif str(live) != str(v):
                reasons.append(
                    f"arm '{arm.get('tag', '?')}' declares {k}={v} but the "
                    f"live environment carries {k}={live} - a stale or "
                    f"mismatched variable; the cube would not be the config "
                    f"the manifest names")
    return reasons


def window_matches(manifest: str, engine_args: list[str]) -> list[str]:
    """B2132 (S6-B2128c): the manifest DECLARES a window; nothing read it.

    A run could be launched with --start/--end that contradict the manifest
    and no gate objected - the same unenforced-field class as `isolation`,
    but worse, because the artifact then measures a period its own manifest
    denies and the discrepancy is invisible downstream.
    """
    try:
        w = (json.loads(Path(manifest).read_text(encoding="utf-8")) or {}).get("window")
    except (OSError, ValueError):
        return []                       # unreadable manifest is the gate's job
    if not isinstance(w, dict):
        return []                       # no declared window: nothing to enforce
    got = {}
    for flag in ("--start", "--end"):
        if flag in engine_args:
            got[flag[2:]] = engine_args[engine_args.index(flag) + 1]
    bad = [f"manifest window {k}={w[k]} but launched {k}={got[k]}"
           for k in ("start", "end")
           if k in w and k in got and str(w[k]) != str(got[k])]
    return bad


# B2133 (S6-B2122b): the data dirs the engine reads are anchored on the MODULE's
# own location (backtest/data/cache.py line 31: CACHE_DIR = Path(__file__).parent
# .parent / "data" / "cache" / "ohlcv") and are gitignored - so a bare worktree
# sees an EMPTY cache and the run completes having done nothing, which is exactly
# the 7.3-hour failure the B2118 pilot already paid for. Every linked dir is
# therefore VERIFIED non-empty before the engine is allowed to start.
LINKED_DATA_DIRS = ("backtest/data/cache", "data_prefetch")


def materialise_worktree(sha: str, root: Path) -> tuple[Path | None, list[str]]:
    """Create (or reuse) a detached worktree at `sha` with data dirs linked.

    Returns (worktree_path, problems). A non-empty problems list means the
    caller MUST refuse to launch - never fall back to the live tree silently.
    """
    if not sha:
        return None, ["manifest has no frozen_sha to pin a worktree to"]
    if not root.is_dir():
        # B2133: found by its own pin - passing a missing dir as cwd RAISES
        # instead of refusing, and a launcher that raises where it should
        # refuse is a launcher whose failure path nobody has run.
        return None, [f"repo root does not exist: {root}"]
    wt = root / ".worktrees" / sha[:12]
    problems: list[str] = []
    if not wt.exists():
        r = subprocess.run(["git", "worktree", "add", "--detach",
                            str(wt), sha], cwd=str(root),
                           capture_output=True, text=True)
        if r.returncode != 0:
            return None, [f"git worktree add failed: {r.stderr.strip()[:200]}"]
    for rel in LINKED_DATA_DIRS:
        src, dst = root / rel, wt / rel
        if not src.exists():
            problems.append(f"source data dir missing in the main tree: {rel}")
            continue
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            # Windows directory junction: no admin rights needed, unlike symlinks
            j = subprocess.run(["cmd", "/c", "mklink", "/J", str(dst), str(src)],
                               capture_output=True, text=True)
            if j.returncode != 0 and not dst.exists():
                problems.append(f"could not link {rel}: {j.stderr.strip()[:120]}")
                continue
        # the check that matters: is the data actually VISIBLE from the worktree?
        try:
            if not any(dst.iterdir()):
                problems.append(f"{rel} is EMPTY as seen from the worktree - the "
                                "engine would run on no data and produce nothing")
        except OSError as exc:
            problems.append(f"{rel} unreadable from the worktree: {exc!r}")
    return wt, problems


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

    # B2132: the drift check guards a REAL engine launch. Under the test seam
    # (--engine-cmd) no engine runs, so engine-code reproducibility is moot -
    # and requiring a clean tree there made the suite unrunnable during
    # development, which is when it is most needed. drift_check stays unit-
    # tested directly (test_b2127), so the gate keeps its coverage.
    # B2168: same seam rule as drift - the fake-engine test path skips the
    # environment check (production callers never pass --engine-cmd); the
    # pure function is pinned directly by test_b2168.
    env_probs = [] if a.engine_cmd else arm_env_matches(a.manifest, os.environ)
    if env_probs:
        print("LAUNCH REFUSED (B2168 arm-env mismatch): the manifest's arms "
              "declare config-defining env values the live environment does "
              "not carry. The engine was NOT invoked.")
        for r in env_probs:
            print(f"  - {r}")
        return 2

    drift = [] if a.engine_cmd else drift_check(a.manifest)
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

    win = window_matches(a.manifest, list(a.engine_args))
    if win:
        print("LAUNCH REFUSED (B2132 window mismatch): the engine would measure "
              "a period this manifest denies. The engine was NOT invoked.")
        for r in win:
            print(f"  - {r}")
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
