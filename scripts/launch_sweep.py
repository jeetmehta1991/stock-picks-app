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
# SUPERSEDED B3099 (S6-B3093a): the sha half refused a live wave's leg 2 after
# four queue-only commits (L866); drift_check below now compares CONTENT, and
# ENGINE_PATHS is no longer read by it - kept for any external reader.
ENGINE_PATHS = ("backtest/engine", "backtest/signals", "backtest/data",
                "backtest/config.py", "backtest/run_phase1a.py")


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(ROOT),
                          capture_output=True, text=True).stdout.strip()


# S6-B3093a (B3099, owner-approved 2026-09-24): CONTENT, not sha. The sha half
# refused leg 2 of a live Step-2 wave after four queue-only commits (L866) while
# `git diff` over backtest/ was empty; under the every-turn commit rule it would
# refuse every multi-leg wave. The question a leg boundary must answer is "can
# this leg read anything that changed since the wave froze?", so the check now
# reads WHICH paths changed and allows only those no leg can read.
#
# What a LEG reads: run_wave is ONE process for the whole wave and resolves the
# spec and the phase table ONCE at wave start, freezing the window and universe
# into the manifest; each leg then runs launch_sweep.py and prelaunch_gate.py as
# fresh subprocesses and the engine (backtest/**, the tickers file, the strategy
# file, data caches). MEASURED B3099 (scripts/leg_read_set.py - the real gate
# under a sys.addaudithook - on c14's real Step-1 manifest): 557 .py files and 7
# data files - the Tier-1 ETF universe CSV, backtest/data/economic_calendar.json,
# the subset file, output_batches/batch_ledger.json and the manifest, all
# refused below by kind or by pin, plus PHASE_1B_ROSTER.md and
# output_audit/phase_1b_step2_admissions.json. The runbook is NOT opened per leg
# (a first draft froze it by reasoning, not measurement). Those two are POLICY:
# the gate re-reads them at EVERY leg to refuse an admitted strategy
# (producer_variant_table._admitted_retest_refusals), so an admission of the
# wave's OWN strategy stops the wave at the next leg while an unrelated
# admission cannot - freezing them would let an unrelated admission halt a
# wave, L866's shape. LEG_READ_FILES holds any computation input the kinds
# below would ALLOW (none measured); LEG_POLICY_FILES records the re-read
# policy files. test_b3099_every_file_the_leg_gate_opens_is_refused_mid_wave
# re-measures: every file the gate opens must be refused or declared policy,
# and every declared policy file must still be opened (both directions, #279).
LEG_CODE_ROOTS = ("scripts/launch_sweep.py", "scripts/prelaunch_gate.py")
DRIFT_FREE_PREFIXES = (".claude/", "archive/", ".archive/", "backtest/tests/",
                       "output_audit/held_patches/")
AUDIT_ARTIFACT_EXT = ("md", "json", "jsonl", "log", "stdout", "csv", "html",
                      "png", "svg")
LEG_READ_FILES: frozenset = frozenset()
LEG_POLICY_FILES = frozenset({"PHASE_1B_ROSTER.md",
                              "output_audit/phase_1b_step2_admissions.json"})
# The engine WRITES tracked files under these roots during a leg - its OHLCV
# cache index (backtest/data/cache.py _save_index, e.g. when an index entry is
# missing) and its ticker-info cache (backtest/data/universe.py fetch_info_bulk).
# A leg that wrote them leaves them uncommitted, so the uncommitted-change check
# skips them (it would refuse the next leg for the engine's own state) - a
# COMMITTED change to them still refuses. Pinned to the two writers' paths by
# test_b3099_drift_check_is_content_aware. (Before B3099 the dirty rule named
# backtest/data too and would have fired the same way; the template waiver,
# true until B3099, masked it.)
ENGINE_STATE_PREFIXES = ("backtest/data/cache/", "data/cache/")


def _engine_script_imports(root: Path = ROOT) -> set[str]:
    """scripts/*.py the ENGINE imports - every non-test module under backtest/.
    The engine runs in every leg, so a scripts module it imports is leg code.
    MEASURED B3099: backtest/signals/institutional_persistence_consumer.py
    imports build_institutional_persistence_precompute (reached from
    signal_loader), and a diagnostics canary imports inject_null_strategies.
    The first was protected only because the launch gate happens to import it
    too - an accident of the gate's import graph, not a rule. IMPORTS ONLY: a
    .py string literal in the engine names a subprocess the engine starts after
    the LAST leg (run_phase1a -> postconfig_landing.py), and the landing records
    the code that graded it instead (graded_with, Council 1b)."""
    import ast as _ast
    found: set[str] = set()
    for f in sorted((root / "backtest").rglob("*.py")):
        rel = f.relative_to(root).as_posix()
        if rel.startswith("backtest/tests/"):
            continue
        try:
            tree = _ast.parse(f.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, ValueError):
            continue
        for n in _ast.walk(tree):
            mods = []
            if isinstance(n, _ast.Import):
                mods = [a.name for a in n.names]
            elif isinstance(n, _ast.ImportFrom) and n.module and not n.level:
                mods = [n.module]
            for mod in mods:
                parts = mod.split(".")
                nm = (parts[1] if parts[0] == "scripts" and len(parts) > 1
                      else parts[0])
                if nm and (root / "scripts" / f"{nm}.py").is_file():
                    found.add(f"scripts/{nm}.py")
    return found


def leg_code_closure(root: Path = ROOT) -> set[str]:
    """Every scripts/ file a LEG can load: the two per-leg roots and every
    scripts module the engine imports (_engine_script_imports), plus their
    transitive imports, and any scripts/*.py named as a string literal (a
    subprocess target, e.g. prelaunch_gate.py). Read from the CURRENT code, so a
    dependency is protected the moment it is imported. Over-inclusion only makes
    the check stricter; an unparseable file stays in the set."""
    import ast as _ast
    seen: set[str] = set()
    todo = list(LEG_CODE_ROOTS) + sorted(_engine_script_imports(root))
    while todo:
        rel = todo.pop()
        if rel in seen:
            continue
        seen.add(rel)
        try:
            tree = _ast.parse((root / rel).read_text(encoding="utf-8"))
        except (OSError, SyntaxError, ValueError):
            continue
        names: set[str] = set()
        for n in _ast.walk(tree):
            mods = []
            if isinstance(n, _ast.Import):
                mods = [a.name for a in n.names]
            elif isinstance(n, _ast.ImportFrom) and n.module and not n.level:
                mods = [n.module]
            elif (isinstance(n, _ast.Constant) and isinstance(n.value, str)
                    and n.value.endswith(".py") and "\n" not in n.value):
                names.add(n.value.replace("\\", "/").rsplit("/", 1)[-1][:-3])
            for mod in mods:
                parts = mod.split(".")
                names.add(parts[1] if parts[0] == "scripts" and len(parts) > 1
                          else parts[0])
        for nm in names:
            cand = f"scripts/{nm}.py"
            if nm and (root / cand).is_file():
                todo.append(cand)
    return seen


def drift_allowed(path: str, inputs=frozenset(), leg_code=frozenset()) -> bool:
    """FAIL-CLOSED: True only for a path no leg COMPUTES with - docs (.md)
    other than LEG_READ_FILES, the harness (.claude/), tests, archives, parked
    patch scripts, scripts/ OUTSIDE the leg closure, and output_audit ARTIFACTS
    (never an underscore-prefixed input such as _sweep_200.txt / _subset_*.txt /
    _engine_set_*.txt, never a .txt, never a file the manifest pins). The two
    LEG_POLICY_FILES are allowed by kind because the gate re-reads them at
    every leg. Everything else refuses."""
    p = path.replace("\\", "/").strip().strip('"')
    if not p or p in inputs or p in leg_code or p in LEG_READ_FILES:
        return False
    if p.endswith(".md") or p.startswith(DRIFT_FREE_PREFIXES):
        return True
    if p.startswith("scripts/"):
        return True
    if p.startswith("output_audit/"):
        name = p.rsplit("/", 1)[-1]
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        return (not name.startswith("_")) and ext in AUDIT_ARTIFACT_EXT
    return False


def _git_names(*args: str) -> tuple[int, list[str]]:
    """(returncode, paths) for a `git ... --name-only -z` call. The seam the
    drift tests replace (B1761: a gate with no seam cannot be tested)."""
    r = subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True,
                       text=True)
    return r.returncode, [x for x in r.stdout.split("\0") if x.strip()]


def _text_pin(rel: str) -> str | None:
    """sha256 of a text input, whitespace-normalised exactly as
    run_wave.build_manifest pins it (its tokens joined by newlines), so a CRLF
    checkout and an LF one pin identically. None when unreadable."""
    import hashlib as _hl
    try:
        toks = (ROOT / rel).read_text(encoding="utf-8").split()
    except (OSError, ValueError):
        return None
    return _hl.sha256("\n".join(toks).encode()).hexdigest()


def drift_check(manifest: str) -> list[str]:
    """Return the reasons this leg would NOT run on the wave's frozen inputs.
    Empty = clean. Three checks (S6-B3093a, B3099):
      1. COMMITTED changes since frozen_sha, by CONTENT: refuse when any
         changed path is one a leg can read (drift_allowed). The ONLY check
         allow_engine_drift waives - a deliberate, recorded engine change.
      2. UNCOMMITTED changes (tracked) to paths a leg can read: always refuse
         - except the engine's own cache state (ENGINE_STATE_PREFIXES), which
         a leg writes as it runs.
      3. INPUT PINS: the tickers file and every strategy file the manifest
         pins must still hash to the pinned value; a manifest with no pins is
         refused (it predates B3099 - run_wave rewrites the manifest at every
         wave start). Untracked files are covered here, not by git.
    Residual, stated: untracked data caches (data_prefetch/, backtest/data/
    cache) are not content-pinned."""
    reasons = []
    try:
        m = json.loads(Path(manifest).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"manifest unreadable: {exc!r}"]
    tick = m.get("tickers") if isinstance(m.get("tickers"), dict) else {}
    pins = m.get("input_sha256")
    inputs = {str(x).replace("\\", "/") for x in
              ([tick.get("file")] + list((pins or {}).keys())) if x}
    leg_code = leg_code_closure()
    frozen = (m.get("frozen_sha") or "").strip()
    if not frozen:
        reasons.append("manifest has no frozen_sha - nothing to compare the "
                       "leg's code against")
    else:
        rc, changed = _git_names("diff", "--name-only", "-z", frozen, "HEAD")
        if rc != 0:
            reasons.append(f"frozen_sha {frozen[:12]} cannot be diffed against "
                           "HEAD (unknown to this repo?) - content drift UNKNOWN")
        else:
            blocked = [p for p in changed
                       if not drift_allowed(p, inputs, leg_code)]
            if blocked and not m.get("allow_engine_drift"):
                reasons.append(
                    f"commits since frozen_sha {frozen[:12]} changed "
                    f"{len(blocked)} path(s) a leg reads: "
                    + "; ".join(blocked[:6]))
    rc, dirty = _git_names("diff", "--name-only", "-z", "HEAD")
    if rc != 0:
        reasons.append("git diff HEAD failed - uncommitted changes UNKNOWN")
    else:
        dirty_blocked = [p for p in dirty
                         if not drift_allowed(p, inputs, leg_code)
                         and not p.replace("\\", "/").startswith(
                             ENGINE_STATE_PREFIXES)]
        if dirty_blocked:
            reasons.append("uncommitted changes to path(s) a leg reads (never "
                           "waived): " + "; ".join(dirty_blocked[:6]))
    if not tick.get("file") or not tick.get("sha256"):
        reasons.append("manifest carries no tickers pin")
    else:
        # the tickers pin predates B3099: build_manifest hashes the file's
        # tokens joined by newlines, the same normalisation as _text_pin
        got = _text_pin(str(tick["file"]))
        if got != tick["sha256"]:
            reasons.append(f"tickers file {tick['file']} no longer matches its "
                           "pin - the universe changed mid-wave")
    if not isinstance(pins, dict):
        reasons.append("manifest carries no input_sha256 pins (it predates "
                       "B3099); rebuild it - run_wave writes them at wave start")
    else:
        for rel, want in pins.items():
            if _text_pin(rel) != want:
                reasons.append(f"input {rel} no longer matches its pin")
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
        print("  Fix: commit or revert the change a leg would read; a "
              "DELIBERATE committed engine change can be recorded with "
              "allow_engine_drift=true, which never waives uncommitted "
              "changes or a changed input (S6-B3093a, B3099).")
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

    # B2169 (S6-B2159b): a gate PASS leaves a RECEIPT in the run's own output.
    # Before this, PASS printed to stdout and exited - no artifact could later
    # say which results were gated, and a kill erased even the stdout. The
    # receipt binds the gated manifest (by hash) to the launched argv, and
    # run_postconfig FAILS any cube whose dir lacks a matching receipt.
    import hashlib as _hl
    import json as _json2
    import time as _t2
    _man_bytes = Path(a.manifest).read_bytes()
    receipt = {
        "manifest_path": str(a.manifest),
        "manifest_sha256": _hl.sha256(_man_bytes).hexdigest(),
        "gate": "prelaunch_gate PASS + drift/window/arm-env checks",
        "tag": a.tag,
        "engine_argv": list(a.engine_args),
        "timestamp": _t2.strftime("%Y-%m-%dT%H:%M:%SZ", _t2.gmtime()),
    }
    (out_dir / "gate_receipt.json").write_text(
        _json2.dumps(receipt, indent=1), encoding="utf-8")
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
