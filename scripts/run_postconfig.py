#!/usr/bin/env python
"""Post-config battery: all nine runbook steps, recorded on EVERY landing.

B2520 (owner ruling 2026-09-01: "Once the config lands, i want it to run
automatically no exceptions and share results with me").

WHAT THIS REPLACES. B2118 automated the mechanical checks and recorded step 1;
B2177 added steps 2/4 for the ONE family whose parameters the manifest carried
(smc swing/span); B2192 recorded 3/6b from the same run. Steps 5/6/8 were
declared "JUDGMENT (never auto-marked)", every other family fell into the
else-branch as "pre-B2138 cube", and a single FAIL discarded the records of
every step that had run. Six owner asks, six instance fixes. This file is the
CLASS fix:

  * a FAMILY REGISTRY (FAMILIES) keyed by the cube's strategy column - an
    unregistered strategy FAILS closed (L642), it never "skips";
  * step-1 / step-2 derived from the manifest window (flags win; no window ->
    Step-1, the stricter arm, basis recorded);
  * a mechanical LENS battery for step 5 -> output_audit/<cube>_lenses.json;
    a WARN/FAIL lens makes step 6 OPEN (a finding must be rechecked), no lens
    finding makes step 6 N/A on evidence;
  * step 8 = the verdict WITH DENOMINATORS read from the grid artifact;
  * step 7 = the engine-implementation check, N/A on a Step-1 cube (nothing is
    admitted at Step 1), DONE/OPEN on a Step-2 cube;
  * EVERY step written to the ledger on EVERY run, FAIL included. Statuses are
    DONE / N/A (terminal) / OPEN / FAIL (block the gate) - never SKIPPED
    (L721; verify_postconfig_complete.py treats only DONE and N/A as terminal).
    Terminal rows are never downgraded automatically: the battery's finding
    rides along as " | battery re-run <ts>: ..." and the B2136 contradiction
    check flags a kept status the battery contradicts.

The mechanical checks (the M-list, S6-B2117b) are unchanged in checks():
  M1 determinism content-sha; M2 exits-per-entry vs len(EXIT_STRATEGIES);
  M3 fill_date; M4 PIT window + HOLDOUT-TOUCH (FAIL on a Step-1 cube);
  M5 NaN/inf pnl + beyond-winsorize; M7 measure_degraded_exits;
  M9 universe artifact; M10 gate receipt vs manifest sha.

Usage:
  PYTHONPATH=. python scripts/run_postconfig.py --cube output_<dir>
      [--step1-cube | --step2-cube]   # else derived from the manifest window
      [--write-ledger]                # records all nine steps in the ledger
Exit 0 = no FAIL; 2 = at least one FAIL (every step is recorded either way).
Invoked automatically by scripts/postconfig_landing.py, which the engine calls
from backtest/run_phase1a.py the moment a cube lands.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from verify_postconfig_complete import STEPS  # noqa: E402  (the gate's list)
from grid_population import grid_population  # noqa: E402  (B2521 S6-B2520m)

MEGA = ("NVDA", "MSFT", "GOOGL", "META", "TSLA", "AAPL")
TERMINAL = ("DONE", "N/A")
_GRADER_CHECKS = ("step2_grade_auto", "step2_free_levels",
                  "step4_spot_check_auto", "step7_engine_implemented")
_LEDGER_WIDE = ("ledger_status_matches_evidence",)


def checks(cube_dir: Path, step1: bool = False):
    import pandas as pd
    from roster_core import HO_START, WINSORIZE

    out = []
    f = cube_dir / "trade_exit_detail.csv"
    if not f.exists():
        return [("cube_exists", "FAIL", f"{f} missing")]
    df = pd.read_csv(f, low_memory=False)
    out.append(("cube_exists", "PASS", f"{len(df)} rows"))

    # 1. sanity: strategies / exits-per-entry / mega-caps
    n_strat = df["strategy"].nunique()
    out.append(("one_strategy", "PASS" if n_strat == 1 else "FAIL",
                f"{n_strat} strategies"))
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    epe = df.groupby(["ticker", "entry_date"]).exit_method.nunique().unique()
    reg = len(EXIT_STRATEGIES)
    ok = len(epe) == 1 and (epe[0] == reg or epe[0] in (24, 25, 26))
    out.append(("M2_exits_per_entry_vs_registry",
                "PASS" if len(epe) == 1 and epe[0] == reg else
                ("PASS" if ok else "FAIL"),
                f"cube {sorted(epe.tolist())} vs registry-now {reg} "
                f"(a differing single value = an older registry at the "
                f"cube's sha - disclosed, judged there)"))
    megas = [t for t in MEGA if t in set(df["ticker"])]
    mega_ev = (", ".join(megas) if megas else
               "none - small/deliberate universes SKIP; the archived A-C "
               "chunk trap is the FAIL case for 100t+ cubes")
    out.append(("megacaps_present", "PASS" if megas else "SKIP", mega_ev))

    # M1 determinism sha
    cols = [c for c in ("strategy", "direction", "exit_method", "entry_date",
                        "ticker", "pnl_pct", "hold_days") if c in df.columns]
    sha = hashlib.sha256(
        df[cols].sort_values(cols).to_csv(index=False).encode()).hexdigest()[:16]
    out.append(("M1_content_sha", "PASS", sha))

    # M3 fill_date
    if "fill_date" in df.columns:
        bad = (pd.to_datetime(df["fill_date"], errors="coerce")
               < pd.to_datetime(df["entry_date"], errors="coerce")).sum()
        out.append(("M3_fill_date", "PASS" if bad == 0 else "FAIL",
                    f"{bad} fills before entry"))
    else:
        out.append(("M3_fill_date", "SKIP",
                    "column absent (pre-B2087 cube - expected)"))

    # M4 PIT bounds + holdout touch
    ed = pd.to_datetime(df["entry_date"], errors="coerce").dt.date
    out.append(("M4_window", "PASS", f"entries {ed.min()} .. {ed.max()}"))
    touched = int((ed >= HO_START).sum())
    if step1:
        out.append(("M4_holdout_touch", "PASS" if touched == 0 else "FAIL",
                    f"{touched} entries at/after HO_START {HO_START} in a "
                    "STEP-1 cube"))
    else:
        out.append(("M4_holdout_touch", "SKIP",
                    f"{touched} entries past {HO_START} (not declared a "
                    "Step-1 cube; pass --step1-cube to arm the FAIL)"))

    # M5 pnl integrity
    import numpy as np
    pnl = pd.to_numeric(df["pnl_pct"], errors="coerce")
    nan_inf = int(pnl.isna().sum() + np.isinf(pnl.fillna(0)).sum())
    beyond = int((pnl.abs() > WINSORIZE).sum())
    out.append(("M5_pnl_integrity", "PASS" if nan_inf == 0 else "FAIL",
                f"{nan_inf} NaN/inf; {beyond} beyond winsorize {WINSORIZE} "
                "(beyond-count is DISCLOSURE - the SBNY class - clip "
                "happens at grade time)"))

    # M7 degraded exits, auto
    try:
        import roster_core as rc
        deg = rc.measure_degraded_exits(rc.load_cube(f))
        out.append(("M7_degraded_exits", "PASS",
                    f"degraded map (B1623 measure-not-assume): {deg or '{}'}"))
    except Exception as exc:
        out.append(("M7_degraded_exits", "SKIP", f"lens unavailable: {exc!r}"))

    # M10 gate receipt (B2169, S6-B2159b): the cube's dir must carry the
    # receipt the gate wrote at launch, and its manifest hash must match the
    # manifest sitting beside the cube. A cube with no receipt was launched
    # around the gate; a hash mismatch means the manifest changed after the
    # gate read it. Legacy cubes (pre-B2169) SKIP with the reason stated.
    import hashlib as _hl10
    rp = cube_dir / "gate_receipt.json"
    mp10 = cube_dir / "run_manifest.json"
    if not rp.exists():
        out.append(("M10_gate_receipt", "SKIP",
                        "no gate_receipt.json - cube predates B2169 or was "
                        "launched AROUND the gate; post-B2169 launches always "
                        "write one, so treat SKIP on a NEW cube as a finding"))
    elif not mp10.exists():
        out.append(("M10_gate_receipt", "FAIL",
                        "receipt present but run_manifest.json missing - the "
                        "receipt cannot be verified against anything"))
    else:
        rec = json.loads(rp.read_text(encoding="utf-8"))
        actual = _hl10.sha256(mp10.read_bytes()).hexdigest()
        if rec.get("manifest_sha256") == actual:
            out.append(("M10_gate_receipt", "PASS",
                            f"receipt matches manifest sha {actual[:12]}"))
        else:
            out.append(("M10_gate_receipt", "FAIL",
                            "receipt manifest_sha256 != the manifest beside "
                            "the cube - the manifest CHANGED after the gate "
                            "read it (the rebind hole the council named)"))


    return out


# --------------------------------------------------------------------------
# helpers shared by the family runners
# --------------------------------------------------------------------------
def _run(cmd: list[str], env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, **(env_extra or {})}
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT),
                          env=env)


def _tail(p: subprocess.CompletedProcess, n: int = 2) -> str:
    lines = ((p.stdout or "") + "\n" + (p.stderr or "")).strip().splitlines()
    return "; ".join(x.strip() for x in lines[-n:] if x.strip())


_VERDICT_PREFIXES = ("[FAIL]", "[PASS]", "REPRODUCTION:")


def _verdict_line(p: subprocess.CompletedProcess) -> str:
    """The grader's own verdict line, when it printed one.

    B2576 (S6-B2574b): `_tail` joins stdout+stderr and keeps the LAST two
    lines, so a stderr trailer ("pandas-ta not installed ...") displaced the
    grader's `[FAIL] NOT_COMPARABLE: ...` line from the span100 ledger row -
    the row carried the noise and not the verdict. Prefer a stdout line that
    starts with a verdict prefix; fall back to `_tail` when none was printed.
    """
    for line in reversed((p.stdout or "").splitlines()):
        s = line.strip()
        if s.startswith(_VERDICT_PREFIXES):
            return s
    return _tail(p)


def _arm_env(manifest: dict) -> dict:
    """The landed arm's env, passed to EVERY family subprocess (B2576).

    S6-B2574b: `_run` accepted `env_extra` and no family runner passed the
    manifest arm env, so a battery run outside the engine hook resolved
    env-dependent inputs (the INST_PERSIST_CACHE_TAG precompute directory)
    from the CALLER's environment - production - and the minq8 spot check
    read `_t1a` while the cube was built from `_t1a_minq8` (32 agree /
    18 DISAGREE against a landed 50 / 0). Inside the hook the env happened
    to match; the battery's correctness must not depend on who calls it.
    """
    return {str(k): str(v) for k, v in _arm0(manifest)[1].items()}


def _expected_precompute_dir(arm_env: dict) -> Path:
    """Where the arm's persistence precompute lives - ONE resolver (S6-B2484),
    called with the arm's tag rather than the caller's environment."""
    from build_institutional_persistence_precompute import persistence_cache_dir
    return persistence_cache_dir(ROOT, tag=arm_env.get("INST_PERSIST_CACHE_TAG", ""))


def _precompute_dir_check(spot_out: Path, arm_env: dict) -> tuple[bool, str]:
    """B2576: the spot-check artifact records the precompute directory it
    read; it must be the arm's. A missing record fails closed."""
    try:
        doc = json.loads(spot_out.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError):
        return False, f"spot artifact {spot_out.name} unreadable"
    got = doc.get("precompute_dir")
    if not got:
        return False, (f"spot artifact {spot_out.name} records no "
                       f"precompute_dir - cannot show it read the arm's artifact")
    exp = _expected_precompute_dir(arm_env)
    if Path(str(got)).name != exp.name:
        return False, (f"precompute-dir mismatch: spot check read "
                       f"{Path(str(got)).name} but the arm expects {exp.name} "
                       f"(battery ran against the wrong persistence artifact - "
                       f"S6-B2574b class)")
    return True, f"precompute_dir {exp.name} matches the arm"


def spot_summary(spot_out: Path) -> str:
    """Step-4 evidence from the ARTIFACT, never from stdout - the smc checker
    prints a blank line before 'wrote ...', so a stdout tail lost the tally
    (measured on the first B2520 dry run)."""
    try:
        sd = json.loads(spot_out.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return f"artifact {spot_out.name} unreadable: {exc!r}"
    s = (f"n_sampled {sd.get('n_sampled')} seed {sd.get('seed')}: "
         f"{sd.get('agree')} agree / {sd.get('disagree')} DISAGREE / "
         f"{sd.get('skipped')} skipped; execution failures "
         f"{len(sd.get('execution_failures') or [])}")
    if "empty_records" in sd:
        s += (f"; empty records {sd.get('empty_records')}; legs A/B disagree "
              f"{sd.get('legs_ab_disagree')}")
    return s + f"; artifact {spot_out.name}"


def row_label(r: dict) -> str:
    """A ranked row's identity: the combination (smc grids rank OUTCOME
    CLASSES whose production-closest member sits in `admit`) plus its exit,
    or the exit alone on a per-exit grid."""
    adm = r.get("admit") or {}
    parts = [f"{k}={adm[k]}" for k in ("close_mitigation", "break_pct_max",
                                      "age_bars_max", "tail_n") if k in adm]
    return (" ".join(parts) + " -> " if parts else "") + str(r.get("exit"))


def read_manifest(cube_dir: Path) -> dict:
    mf = cube_dir / "run_manifest.json"
    if not mf.exists():
        return {}
    try:
        return json.loads(mf.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError):
        return {}


def _arm0(manifest: dict) -> tuple[dict, dict]:
    arms = manifest.get("arms") or []
    arm = (arms[0] or {}) if arms else {}
    return arm, dict(arm.get("env") or {})


def cube_strategies(cube_dir: Path) -> list[str]:
    """The cube's strategy column, read alone (a 9k-row cube is cheap; a junk
    cube without the column returns [] and the family resolves to nothing)."""
    import pandas as pd
    try:
        s = pd.read_csv(cube_dir / "trade_exit_detail.csv", usecols=["strategy"],
                        low_memory=False)["strategy"]
    except (OSError, ValueError, KeyError):
        return []
    return sorted(str(x) for x in s.dropna().unique())


def derive_step(manifest: dict, *, step1_flag: bool, step2_flag: bool) -> tuple[int, str]:
    """1 or 2 plus the basis. Flags win; else the manifest window end against
    HO_START; else Step-1 - the arm that arms the holdout-touch FAIL (L642)."""
    from roster_core import HO_START
    if step1_flag:
        return 1, "declared --step1-cube"
    if step2_flag:
        return 2, "declared --step2-cube"
    end = (manifest.get("window") or {}).get("end")
    if end:
        try:
            d = _dt.date.fromisoformat(str(end)[:10])
        except ValueError:
            d = None
        if d is not None:
            if d <= HO_START:
                return 1, f"manifest window.end {d} <= HO_START {HO_START} -> Step-1 cube"
            return 2, f"manifest window.end {d} > HO_START {HO_START} -> Step-2 cube"
    return 1, ("UNDECLARED (no --step1-cube/--step2-cube flag, no manifest "
               "window) - treated as Step-1, the stricter arm (fail closed, L642)")


# --------------------------------------------------------------------------
# family registry - keyed by the cube's strategy column. An unregistered
# strategy FAILS closed; there is no else-branch that skips.
# --------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# B2579 (S6-B2573a): ONE generic adapter, driven by the SPECS `tools` block.
#
# Before B2579 each family was six hand-written pieces (params parser, runner,
# grader flags, spot-check flags, step-7 anchors, registry row) and a new
# strategy could spend its cube before anyone noticed the battery had no
# adapter for it (four institutional configs landed ungraded pre-B2520).
# Now the family-specific facts live in producer_variant_table.SPECS[...]
# ["tools"] beside the parameters they describe, and FAMILIES is DERIVED from
# SPECS: a strategy is a battery family exactly when its `tools` block is
# complete (family_refusal names what is missing). The two hand-written
# adapters remain as thin wrappers so the B2520/B2569/B2576 pins keep
# reading them.
# ---------------------------------------------------------------------------
from producer_variant_table import (  # noqa: E402
    CODE_ROOT as _CODE_ROOT, SPECS, declared_consumers, knob_consumers, knob_is_read)

_TOOLS_REQUIRED = ("keys", "grid_keys", "grade", "spot_check", "single_combination")
_GRADE_REQUIRED = ("script", "cube", "flags")
# where the tools SCRIPTS live - the code tree, which a test never relocates
# (ROOT is the runtime root: artifacts land under it and tests point it at
# tmp_path; the B2569/B2576 pins do exactly that)
_SCRIPTS_DIR = Path(__file__).resolve().parent


def family_refusal(fam_name: str) -> str:
    """Why `fam_name` is NOT a battery family ('' when it is one)."""
    spec = SPECS.get(fam_name)
    if spec is None:
        return "no SPECS entry in producer_variant_table"
    tools = spec.get("tools")
    if not isinstance(tools, dict):
        return "SPECS entry has no `tools` adapter block (S6-B2573a)"
    missing = [k for k in _TOOLS_REQUIRED if k not in tools]
    if missing:
        return f"`tools` block lacks {missing}"
    by_id = {p["id"]: p for p in spec.get("params") or []}
    for pid, key in dict(tools["keys"]).items():
        if pid not in by_id:
            return f"`tools.keys` names {pid}, which is not a param of the entry"
        if not by_id[pid].get("env"):
            return f"`tools.keys` names {pid} ({by_id[pid].get('param')}) but it has no env knob"
    for section in ("grade", "spot_check"):
        blk = tools.get(section) or {}
        lacks = [k for k in _GRADE_REQUIRED if k not in blk]
        if lacks:
            return f"`tools.{section}` lacks {lacks}"
        for pid in blk["flags"]:
            if pid not in tools["keys"]:
                return f"`tools.{section}.flags` names {pid}, which is not in tools.keys"
        script = _SCRIPTS_DIR / str(blk["script"])
        if not script.exists():
            return f"`tools.{section}.script` {blk['script']} does not exist under scripts/"
    fl = tools.get("free_levels")
    if fl and not (_SCRIPTS_DIR / str(fl.get("script", ""))).exists():
        return f"`tools.free_levels.script` {fl.get('script')} does not exist under scripts/"
    if not isinstance(tools["single_combination"], bool):
        return "`tools.single_combination` is not a bool"
    return ""


def _tools(fam_name: str) -> dict:
    why = family_refusal(fam_name)
    if why:
        raise KeyError(f"{fam_name}: {why}")
    return SPECS[fam_name]["tools"]


def params_from_manifest(fam_name: str, manifest: dict,
                         expect: tuple | None = None) -> tuple[dict | None, str]:
    """The landed arm's values for the family's swept knobs (tools.keys),
    env first (the launcher's contract), then the plain arm key. Missing ->
    (None, reason) and the battery fails CLOSED (L642). `expect` pins the
    params keys a caller relies on (the institutional wrapper)."""
    tools = _tools(fam_name)
    by_id = {p["id"]: p for p in SPECS[fam_name]["params"]}
    arm, env = _arm0(manifest)
    vals, envs = {}, []
    for pid, key in dict(tools["keys"]).items():
        row = by_id[pid]
        envs.append(row["env"])
        v = env.get(row["env"])
        if v is None:
            v = arm.get(key)
        if v is None:
            v = arm.get(row["param"])
        vals[key] = v
    if expect is not None:
        assert set(vals) == set(expect), (fam_name, sorted(vals), expect)
    missing = [k for k, v in vals.items() if v is None]
    if missing:
        return None, (f"manifest arms[0] lacks {missing} (neither the "
                      f"{' + '.join(envs)} env keys nor the plain keys; a "
                      "pre-B2138 cube has this shape)")
    return vals, "manifest arms[0] " + " ".join(f"{k}={v}" for k, v in vals.items())


def _cube_arg(cube_dir: Path, blk: dict) -> str:
    return str(cube_dir / blk["cube"]) if blk.get("cube") else str(cube_dir)


def _flag_args(blk: dict, tools: dict, p: dict) -> list[str]:
    out: list[str] = []
    for pid, flag in dict(blk.get("flags") or {}).items():
        out += [flag, str(p[tools["keys"][pid]])]
    return out


def _sub_env(arm_env: dict, blk: dict) -> dict:
    pp = blk.get("pythonpath")
    return {**arm_env, "PYTHONPATH": pp} if pp else dict(arm_env)


def preregistered_exit(manifest: dict) -> str | None:
    """B2612: the exit the spec arm pre-registered at Step 1 (arm key
    `preregistered_exit`), or None. Recorded beside the grader's own
    selection; never a selector."""
    arm, _ = _arm0(manifest)
    v = arm.get("preregistered_exit")
    return str(v) if v else None


def grid_step2_graded(grid: dict) -> tuple[bool, str]:
    """B2612 (S6-B2612a, L642): did the grader actually grade the holdout?

    True when the grid carries a Step-2 gate verdict: a `step2` block whose
    `gates` is a dict (the institutional grader), or any result row carrying
    a `gates` dict (tighten_breaker_block's per-combination rows). A Step-2
    cube whose grid has neither was graded Step-1-shaped - before this check
    the battery passed it and step 8 wrote 'PASS rows are the admission
    candidates' over a grid that had no PASS row to offer."""
    s2 = grid.get("step2")
    if isinstance(s2, dict) and isinstance(s2.get("gates"), dict):
        return True, f"step2 block: {s2.get('verdict')} on {s2.get('selected_exit')}"
    rows = [r for r in (grid.get("results") or [])
            if isinstance(r, dict) and isinstance(r.get("gates"), dict)]
    if rows:
        return True, f"{len(rows)} of {len(grid.get('results') or [])} rows carry gates"
    if isinstance(s2, dict):
        return False, (f"step2 block graded nothing: {s2.get('verdict')} - "
                       f"{str(s2.get('reason') or '')[:120]}")
    return False, ("no `step2` block and no result row carries `gates` - the "
                   "grader has no Step-2 leg, or nothing reached the holdout floor")


def run_family(fam_name: str, cube_dir: Path, p: dict,
               manifest: dict, step: int | None = None) -> tuple[list, dict, Path, Path]:
    """Steps 2 (grade + optional reproduction-gated free levels), 4 (spot
    check, window + precompute-dir check when the contract says so) and 7
    (engine anchors) for ANY family, from its tools block. Every subprocess
    runs under the landed arm's env (B2576). `step` is the battery's derived
    step (main passes it); None derives it from the manifest alone."""
    spec, tools = SPECS[fam_name], _tools(fam_name)
    results, notes = [], {}
    arm_env = _arm_env(manifest)          # B2576: every subprocess runs armed
    grid_out = ROOT / "output_audit" / f"{cube_dir.name}_grid_auto.json"
    spot_out = ROOT / "output_audit" / f"{cube_dir.name}_spot_check.json"
    label = " ".join(f"{k}={p[k]}" for k in tools["keys"].values())
    if step is None:
        step, _ = derive_step(manifest, step1_flag=False, step2_flag=False)

    # ---- step 2: the family grader at the manifest's own parameters
    gb = tools["grade"]
    # B2612: a grader whose tools block declares the flags is TOLD the step
    # and the pre-registered exit; one that does not (tighten_breaker_block
    # grades whatever holdout it finds) is run as before.
    pre = preregistered_exit(manifest)
    s2_args: list[str] = []
    if step == 2 and gb.get("step2_flag"):
        s2_args.append(str(gb["step2_flag"]))
    if pre and gb.get("preregistered_flag"):
        s2_args += [str(gb["preregistered_flag"]), pre]
    g = _run([sys.executable, str(ROOT / "scripts" / gb["script"]),
              "--cube", _cube_arg(cube_dir, gb), *_flag_args(gb, tools, p),
              *list(gb.get("extra") or []), *s2_args, "--out", str(grid_out)],
             _sub_env(arm_env, gb))
    ok2 = g.returncode == 0 and grid_out.exists()
    why2 = ""
    if ok2 and step == 2:
        # B2612 (S6-B2612a): a Step-2 cube's grid MUST carry a gate verdict;
        # a Step-1-shaped grid on a Step-2 cube fails step 2 CLOSED (L642) -
        # the old fail-open path graded the holdout of nothing and passed.
        try:
            _grid = json.loads(grid_out.read_text(encoding="utf-8")) or {}
        except (OSError, ValueError) as exc:
            _grid, why2 = {}, f"grid unreadable: {exc!r}"
        if not why2:
            graded, why2 = grid_step2_graded(_grid)
            ok2 = bool(graded)
            why2 = ("Step-2 gate verdict present: " if graded else
                    "Step-2 cube with NO gate verdict (fail closed, L642): ") + why2
    results.append(("step2_grade_auto", "PASS" if ok2 else "FAIL",
                    f"exit {g.returncode}; {label} -> {grid_out.name}"
                    + (f"; {why2[:200]}" if why2 else "")
                    + ("" if ok2 or why2 else f"; {_tail(g)[:160]}")))
    # B2569 (owner directive 2026-09-02): a family whose band carries FREE
    # levels grades them on EVERY landing, reproduction-gated - never once at
    # strategy level (the S6-B2501/B2504 class bug). A reproduction failure
    # exits nonzero and FAILS step 2 closed.
    fb = tools.get("free_levels")
    okf, free_out, fl = True, None, None
    if fb:
        free_out = ROOT / "output_audit" / f"{cube_dir.name}_free_levels.json"
        fl = _run([sys.executable, str(ROOT / "scripts" / fb["script"]),
                   "--cube", str(cube_dir), "--out", str(free_out)],
                  _sub_env(arm_env, fb))
        okf = fl.returncode == 0 and free_out.exists()
        # B2576: the grader's verdict line, not whatever stderr printed last
        results.append(("step2_free_levels", "PASS" if okf else "FAIL",
                        f"exit {fl.returncode}; reproduction-gated free levels "
                        f"-> {free_out.name}; {_verdict_line(fl)[:160]}"))
    note2 = gb.get("note", "AUTO")
    notes["2_grade_with_config_params"] = (
        ("DONE", f"{note2}: {Path(gb['script']).stem} at manifest {label} -> "
                 f"{grid_out.name}"
                 + (f"; {why2[:160]}" if why2 else "")
                 + (f"; free levels reproduction-gated -> {free_out.name}"
                    if fb else "")) if ok2 and okf else
        ("FAIL", (f"{Path(gb['script']).stem} exit {g.returncode} at {label}: "
                  f"{why2[:200] if why2 else _tail(g)[:140]}" if not ok2 else
                  f"free-levels grade exit {fl.returncode} (reproduction gate "
                  f"or grading failed): {_verdict_line(fl)[:140]}")))

    # ---- step 4: the three-leg spot check
    sb = tools["spot_check"]
    cmd = [sys.executable, str(ROOT / "scripts" / sb["script"]),
           "--cube", _cube_arg(cube_dir, sb), *list(sb.get("extra") or []),
           *_flag_args(sb, tools, p), "--out", str(spot_out)]
    if sb.get("window"):
        win = manifest.get("window") or {}
        if win.get("start"):
            cmd += ["--start", str(win["start"])[:10]]
        if win.get("end"):
            cmd += ["--end", str(win["end"])[:10]]
    sc = _run(cmd, _sub_env(arm_env, sb))
    ok4 = sc.returncode == 0 and spot_out.exists()
    tail = spot_summary(spot_out) if ok4 else _tail(sc)
    if ok4 and sb.get("precompute_check"):
        # B2576 (S6-B2574b): the artifact must have read the ARM's precompute
        # directory; a production read under a tagged arm is a wrong answer
        # that agrees with nothing (minq8: 32 agree / 18 DISAGREE by hand vs
        # the landed 50 / 0). Fails closed on a missing record.
        ok4, why = _precompute_dir_check(spot_out, arm_env)
        tail = f"{tail}; {why}" if ok4 else why
    results.append(("step4_spot_check_auto", "PASS" if ok4 else "FAIL",
                    f"exit {sc.returncode}; {tail[:180]}"))
    notes["4_three_leg_spot_check"] = (
        ("DONE", f"{sb.get('note', 'AUTO')}: {Path(sb['script']).stem} at "
                 f"manifest {label}; {tail[:200]}") if ok4 else
        ("FAIL", f"{Path(sb['script']).stem} exit {sc.returncode}: {tail[:200]}"))

    # ---- step 7: every swept knob is READ from the environment and its
    # declared consumer list equals the tree's (S6-B2573d); plus the family's
    # own anchor script when the contract names one.
    knobs = [(row["id"], row["param"], row["env"])
             for row in spec["params"] if row.get("env")]
    not_read = [e for _, _, e in knobs if not knob_is_read(e, _CODE_ROOT)]
    drift = [e for _, _, e in knobs
             if declared_consumers(spec, e) != knob_consumers(e)]
    script = (tools.get("engine_anchors") or {}).get("script")
    rc = None
    if script:
        r = _run([sys.executable, str(ROOT / "scripts" / script)], arm_env)
        rc = r.returncode
    ok7 = not not_read and not drift and rc in (None, 0)
    results.append(("step7_engine_implemented", "PASS" if ok7 else "FAIL",
                    (f"{len(knobs)} of {len(knobs)} declared knobs read from the "
                     f"environment + consumer lists match the tree"
                     + (f"; {script} exit {rc}" if script else "")) if ok7 else
                    (f"knobs not read {not_read}; consumer drift {drift}"
                     + (f"; {script} exit {rc}" if script else ""))))
    return results, notes, grid_out, spot_out


def family_entry(fam_name: str) -> dict | None:
    """The FAMILIES row for `fam_name`, or None when family_refusal says why."""
    if family_refusal(fam_name):
        return None
    tools = SPECS[fam_name]["tools"]
    return {"params": (lambda m, _f=fam_name: params_from_manifest(_f, m)),
            "run": (lambda c, p, m, step=None, _f=fam_name:
                    run_family(_f, c, p, m, step=step)),
            "single_combination": bool(tools["single_combination"])}


# thin wrappers - the B2520 / B2569 / B2576 pins read these by name
def _smc_params(manifest: dict) -> tuple[dict | None, str]:
    return params_from_manifest("smc_breaker_block_long", manifest,
                                expect=("swing", "span"))


def _institutional_params(manifest: dict) -> tuple[dict | None, str]:
    return params_from_manifest(
        "institutional_committed_growth_long", manifest,
        expect=("min_consecutive_quarters", "growth_lookback_quarters",
                "growth_multiple", "ema_span"))


def run_smc(cube_dir: Path, p: dict, manifest: dict,
            step: int | None = None) -> tuple[list, dict, Path, Path]:
    return run_family("smc_breaker_block_long", cube_dir, p, manifest, step=step)


def run_institutional(cube_dir: Path, p: dict, manifest: dict,
                      step: int | None = None) -> tuple[list, dict, Path, Path]:
    return run_family("institutional_committed_growth_long", cube_dir, p, manifest,
                      step=step)


# DERIVED from SPECS (S6-B2573a): a strategy is a battery family exactly when
# its tools block is complete. FAMILY_REFUSALS names why the others are not.
FAMILIES = {k: e for k in SPECS if (e := family_entry(k)) is not None}
FAMILY_REFUSALS = {k: family_refusal(k) for k in SPECS if k not in FAMILIES}


# B2574: the engine's threshold is the ONE number for "how much of the cube
# replay may run on the ATR proxy before the ranking is a different
# population" - imported, never retyped.
from backtest.engine.backtest import REPLAY_ATR_FALLBACK_WARN_RATE  # noqa: E402

NOT_COMPARABLE_TAG = "NOT COMPARABLE"


def replay_atr_proxy_lens(cube_dir: Path, empty_share: float | None) -> tuple:
    """B2574: FAIL when the cube replay priced exits off the 2pct-of-price
    ATR proxy for more than the engine's threshold of trades. Reads the
    engine's measured rate (replay_atr_fallback.json); a cube landed before
    B2574 has no file, so the empty signals_at_entry share stands in for it,
    labelled INFERRED (every empty row hits the proxy: resolve_replay_atr
    reads sig['atr'] and an empty dict has none)."""
    f = cube_dir / "replay_atr_fallback.json"
    thr = REPLAY_ATR_FALLBACK_WARN_RATE
    if f.exists():
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
            rate, tot, fb = float(j["rate"]), int(j["total"]), int(j["fallback"])
        except (OSError, ValueError, KeyError, TypeError) as exc:
            return ("replay_atr_proxy", "FAIL",
                    f"{f.name} unreadable ({exc!r}) - the measured rate is owed")
        src = f"MEASURED {fb}/{tot} ({rate:.1%}) from {f.name}"
    elif empty_share is not None:
        rate, src = empty_share, (f"INFERRED from the empty signals_at_entry "
                                  f"share {empty_share:.1%} (pre-B2574 cube, no "
                                  f"{f.name})")
    else:
        return ("replay_atr_proxy", "INFO",
                f"no {f.name} and no readable trade_log - nothing to measure")
    if rate > thr:
        return ("replay_atr_proxy", "FAIL",
                f"{NOT_COMPARABLE_TAG}: cube replay used the 2pct-of-price ATR "
                f"proxy on {rate:.1%} of trades (> {thr:.0%} engine threshold; "
                f"{src}) - the exit ranking is a different population from a "
                f"cube with signals (S6-B2512 / B2574); re-land under the B2574 "
                f"engine before comparing")
    return ("replay_atr_proxy", "INFO",
            f"ATR proxy on {rate:.1%} of replayed trades (<= {thr:.0%}; {src})")


# --------------------------------------------------------------------------
# step 5: the mechanical lens battery. Each lens returns INFO / WARN / FAIL
# with its evidence; WARN or FAIL is a FINDING and makes step 6 OPEN.
# --------------------------------------------------------------------------
def selection_margin_row(rk: list, unit: str) -> tuple:
    """The rank-1 vs rank-2 margin lens (S6-B2581b).

    WARN means "the top two are within noise of each other, so which one you
    picked is arbitrary". That reading only holds when rank-1 is a CANDIDATE.
    MEASURED at the output_icg_mult1.25_mult1.25 landing: rank-1 and rank-2
    both carried is_ci_lo -0.297, margin 0.000, and the resulting WARN held
    the landing in a blocking state - a warning about choosing between two
    exits neither of which would be chosen.

    Step 1 ranks and does not admit (B1608), so a negative rank-1 means the
    selection question is not live and the row is INFO. The margin is still
    reported either way; only the LEVEL changes, so nothing is hidden.
    """
    if len(rk) >= 2 and rk[0].get("is_ci_lo") is not None \
            and rk[1].get("is_ci_lo") is not None:
        r1 = float(rk[0]["is_ci_lo"])
        margin = r1 - float(rk[1]["is_ci_lo"])
        selectable = r1 > 0
        why = ("" if selectable else
               f"; INFO not WARN - rank-1 is_ci_lo {r1} is not above zero, so "
               "nothing is selectable and a narrow margin is not a selection "
               "risk (S6-B2581b)")
        return ("selection_margin",
                "WARN" if (margin < 0.05 and selectable) else "INFO",
                f"rank-1 [{row_label(rk[0])}] is_ci_lo {rk[0]['is_ci_lo']} vs "
                f"rank-2 [{row_label(rk[1])}] {rk[1]['is_ci_lo']}: margin "
                f"{margin:.3f} between {unit}; WARN < 0.05 (selection at "
                f"noise level){why}")
    if rk:
        return ("selection_margin", "INFO",
                f"1 ranked row ({unit}) - no margin to measure")
    return ("selection_margin", "INFO", "no ranked row in the grid artifact")


def lenses(cube_dir: Path, step: int, grid: dict, spot_out: Path | None) -> list:
    import pandas as pd
    from roster_core import HO_START
    out = []
    want = {"strategy", "direction", "entry_date", "ticker", "exit_method"}
    df = pd.read_csv(cube_dir / "trade_exit_detail.csv", low_memory=False,
                     usecols=lambda c: c in want)
    ent = df.drop_duplicates(subset=["ticker", "entry_date"])
    ed = pd.to_datetime(ent["entry_date"], errors="coerce")
    n = int(len(ent))

    touched = int((ed.dt.date >= HO_START).sum())
    if step == 1:
        out.append(("holdout_untouched", "FAIL" if touched else "INFO",
                    f"{touched} of {n} entries at/after HO_START {HO_START} "
                    "(Step-1 cube: any touch is a leak, B1718 class)"))
    else:
        out.append(("holdout_untouched", "INFO",
                    f"{touched} of {n} entries in the holdout (Step-2 cube: the "
                    "holdout is graded separately, never ranked on)"))

    span_days = int((ed.max() - ed.min()).days) if n else 0
    if span_days > 540:
        per, label, bar = ed.dt.year.astype(str), "year", 0.6
    else:
        per, label, bar = ed.dt.to_period("Q").astype(str), "quarter", 0.5
    shares = per.value_counts(normalize=True)
    top = float(shares.iloc[0]) if len(shares) else 0.0
    out.append(("period_concentration", "WARN" if top > bar else "INFO",
                f"max {label} share {top:.2f} ({shares.index[0] if len(shares) else '-'}) "
                f"over {len(shares)} {label}s of {n} entries; WARN > {bar}"))

    tick = ent["ticker"].value_counts(normalize=True)
    top5 = float(tick.head(5).sum())
    if len(tick) < 20:
        out.append(("ticker_concentration", "INFO",
                    f"{len(tick)} tickers (< 20: top-5 share {top5:.2f} is not a "
                    "concentration measure)"))
    else:
        out.append(("ticker_concentration", "WARN" if top5 > 0.3 else "INFO",
                    f"top-5 tickers carry {top5:.2f} of {n} entries across "
                    f"{len(tick)} tickers; WARN > 0.30"))

    # rank-1 vs rank-2 on the ranking key: the rows are OUTCOME CLASSES on a
    # multi-combination grid (two classes may share an exit) and EXITS on a
    # single-combination grid - row_label names whichever it is.
    rk = grid.get("step1_ranking") or []
    # B2521 (S6-B2520m): the population question has ONE owner now.
    _, _pop_field, _pop_unit = grid_population(grid)
    unit = "exits" if _pop_field == "per_exit" else "outcome classes"
    out.append(selection_margin_row(rk, unit))

    # B2574 (S6-B2512 CAUSE FOUND): the empty share is the SYMPTOM; the
    # consequence is that the cube replay priced every such trade's exits
    # off a 2pct-of-price ATR proxy (backtest.py resolve_replay_atr), so the
    # exit ranking is NOT COMPARABLE to a cube with signals. span100 landed
    # with 313/374 empty, the engine logged 83.7 pct proxy use, and this
    # lens WARNed on the count without saying so. Now: the engine's own
    # measured rate (replay_atr_fallback.json, B2574) decides, FAIL above the
    # engine's threshold; a pre-B2574 cube without the file falls back to the
    # empty share against the same threshold, labelled as inferred.
    tl = cube_dir / "trade_log.csv"
    empty_share = None
    if tl.exists():
        try:
            s = pd.read_csv(tl, usecols=["signals_at_entry"], low_memory=False
                            )["signals_at_entry"].fillna("").astype(str).str.strip()
            empty = int(((s == "") | (s == "{}")).sum())
            empty_share = (empty / len(s)) if len(s) else 0.0
            out.append(("empty_signals_share", "WARN" if empty else "INFO",
                        f"{empty} of {len(s)} trade_log rows carry an empty "
                        "signals_at_entry (S6-B2512 class)"))
        except (OSError, ValueError, KeyError) as exc:
            out.append(("empty_signals_share", "INFO",
                        f"trade_log.csv has no readable signals_at_entry: {exc!r}"))
    else:
        out.append(("empty_signals_share", "INFO", "no trade_log.csv beside the cube"))
    out.append(replay_atr_proxy_lens(cube_dir, empty_share))

    if "direction" in df.columns:
        dirs = sorted(str(x) for x in df["direction"].dropna().unique())
        out.append(("direction_consistency", "INFO" if len(dirs) == 1 else "FAIL",
                    f"directions {dirs} (one strategy, one direction expected)"))

    if spot_out is not None and spot_out.exists():
        try:
            sd = json.loads(spot_out.read_text(encoding="utf-8"))
            dis = int(sd.get("disagree") or 0)
            out.append(("spot_check_disagreements", "WARN" if dis else "INFO",
                        f"{sd.get('agree')} agree / {dis} DISAGREE / "
                        f"{sd.get('skipped')} skipped in {spot_out.name}"))
        except (OSError, ValueError) as exc:
            out.append(("spot_check_disagreements", "WARN",
                        f"spot-check artifact unreadable: {exc!r}"))
    else:
        out.append(("spot_check_disagreements", "WARN",
                    "no spot-check artifact - step 4 produced nothing to read"))

    try:
        from backtest.config import PASSING_CRITERIA as _pc
        ho, fp = _pc.get("min_trades_holdout"), _pc.get("min_trades_full_period")
    except Exception:  # pragma: no cover - config import failure is reported, not fatal
        ho = fp = "?"
    out.append(("min_trades_floor", "INFO",
                f"{n} distinct entries; the live gates need holdout >= {ho} and "
                f"full-period >= {fp} (applied by the grader, not here)"))
    return out


def verdict_from_grid(grid: dict, step: int) -> str:
    """Step 8: the verdict sentence names its denominators (CHECKLIST #182)."""
    res = grid.get("results") or []
    top = grid.get("step1_ranking") or []
    # B2619 (S6-B2566): the population question goes through grid_population -
    # this asked `'per_exit' in grid` directly, the raw probe the helper was
    # written to replace, while run_family already used the helper correctly.
    _rows, _pf, _pu = grid_population(grid)
    if _pf == "per_exit":                        # single-combination grid
        pe = _rows
        ranked = [r for r in pe if (r.get("admit") or {}).get("verdict") == "RANKED"]
        s = (f"{len(ranked)} of {len(pe)} exits RANKED at min-trades >= "
             f"{grid.get('min_n')} on {grid.get('is_rows')} IS rows "
             f"({grid.get('rows')} cube rows, {grid.get('holdout_rows')} holdout rows)")
    else:
        cnt = Counter(str(r.get("verdict")) for r in res)
        s = (f"{len(res)} combinations enumerated: "
             + ", ".join(f"{v} {k}" for k, v in cnt.most_common()))
        pq = grid.get("provisional_qualifiers")
        if isinstance(pq, (list, dict)):
            s += f"; provisional_qualifiers {len(pq)}"
    if top:
        t = top[0]
        s += (f"; rank-1 [{row_label(t)}] is_ci_lo {t.get('is_ci_lo')} "
              f"is_sharpe {t.get('is_sharpe')} fires {t.get('fires')}")
    else:
        s += "; NO ranked row (nothing cleared the power floor)"
    if step == 1:
        s += " - Step-1: ranking only, no admission (B1608)"
    elif isinstance(grid.get("step2"), dict):
        # B2612: the single-combination Step-2 verdict, with its denominators
        s2 = grid["step2"]
        gates = s2.get("gates") or {}
        s += (f" - Step-2 admission on the IS-selected exit {s2.get('selected_exit')}: "
              f"holdout n {s2.get('holdout_n')} of full-period {s2.get('full_period_n')}, "
              f"holdout sharpe {s2.get('sharpe')}, gates {sum(bool(v) for v in gates.values())} "
              f"of {len(rc_live_gates())} PASS -> {s2.get('verdict')}"
              + (f" (margin {s2.get('margin')})" if s2.get('margin') is not None else "")
              + (f"; pre-registered exit {s2.get('preregistered_exit')} "
                 f"{'MISMATCH - disclosed, not re-rolled' if s2.get('mismatch') else 'matches'}"
                 if s2.get("preregistered_exit") else "")
              + ("" if isinstance(s2.get("gates"), dict) else
                 f"; NO gate verdict ({s2.get('verdict')}) - fail closed (L642)")
              + " (S6-B2409: clearing the six live gates IS qualification)")
    else:
        s += (" - Step-2: PASS rows are the admission candidates (S6-B2409: "
              "clearing the six live gates IS qualification)")
    return s


def rc_live_gates() -> tuple:
    from roster_core import LIVE_GATES
    return LIVE_GATES


# --------------------------------------------------------------------------
# ledger merge: FAIL/OPEN/DONE/N/A written for every step; terminal rows are
# never downgraded automatically - the battery's finding rides along.
# --------------------------------------------------------------------------
def _old_evidence(row) -> str:
    if not isinstance(row, dict):
        return ""
    return " / ".join(str(row[k]) for k in ("evidence", "reason", "note")
                      if row.get(k))


def merge_row(entry: dict, step: str, status: str, evidence: str, ts: str) -> dict:
    old = entry.get(step)
    old_st = old.get("status") if isinstance(old, dict) else None
    old_ev = _old_evidence(old)
    # Never truncate the evidence (B2211: the truncation the owner saw came
    # from packing; the measured values sit at the END of a battery line, so a
    # [:200] cut removed exactly the numbers). Growth is bounded by KEEPING
    # ONE re-run tag and ONE level of prior history, not by cutting text.
    if old_st in TERMINAL:
        base = old_ev.split(" | battery re-run ")[0]
        if status == "FAIL":
            tag = (f" | battery re-run {ts}: FAIL (status kept - terminal rows "
                   f"are never downgraded automatically; disposition by hand) "
                   f"- {evidence}")
        else:
            tag = f" | battery re-run {ts}: {status} - {evidence}"
        entry[step] = {"status": old_st, "evidence": base + tag}
    else:
        prior = old_ev.split(" | prior: ")[0]
        entry[step] = {"status": status,
                       "evidence": evidence + (f" | prior: {prior}"
                                               if prior else "")}
    return entry


def _current_claim(ev: str) -> str:
    """The evidence text that IS the row's claim: history after ' | prior:'
    is excluded; a number followed by 'skipped' is a tally, not a status
    (B2136's detector matched '0 skipped' inside spot-check tallies - the
    false positive that flipped seven DONE rows, B2520)."""
    cur = ev.split(" | prior:")[0]
    return re.sub(r"\b\d+\s+skipped\b", "", cur, flags=re.I)


# B2136 (S6-B2135b): a status must never contradict its own evidence. The
# ledger carried `DONE` on a step whose evidence ended "...SKIPPED", so a
# reader trusting the status believed a check ran that never did and never
# can. "(STATUS KEPT" is the battery's own contradiction marker (B2520).
#
# A MENTION is not an ASSERTION (B2520, second false-positive class): a
# narrative row may quote a status ("wrote steps 2-8 as SKIPPED citing...")
# or contain the words inside another token ("run_phase1a direct, not
# run_wave" holds "NOT RUN"). A row asserts non-execution when its claim
# STARTS or ENDS with the status word - B2136's original shape - or carries
# a phrase no narrative quotes, or the battery's own kept-status marker.
_CONTRA_EDGE = ("SKIPPED", "NOT RUN")
_CONTRA_ANY = ("CANNOT BE APPLIED", "NEVER RAN", "(STATUS KEPT")


def asserts_non_execution(claim: str) -> bool:
    up = claim.upper().strip()
    if any(t in up for t in _CONTRA_ANY):
        return True
    return any(re.match(rf"^\W*{t}\b", up) or re.search(rf"\b{t}\W*$", up)
               for t in _CONTRA_EDGE)


def ledger_contradictions(ledger: dict) -> list[str]:
    return [f"{c}/{n}" for c, steps in ledger.items()
            if isinstance(steps, dict) for n, v in steps.items()
            if isinstance(v, dict) and v.get("status") == "DONE"
            and asserts_non_execution(_current_claim(_old_evidence(v)))]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube", required=True)
    ap.add_argument("--step1-cube", action="store_true")
    ap.add_argument("--step2-cube", action="store_true")
    ap.add_argument("--write-ledger", action="store_true")
    a = ap.parse_args()
    cube_dir = Path(a.cube)
    if not cube_dir.is_absolute():
        cube_dir = ROOT / a.cube
    manifest = read_manifest(cube_dir)
    step, step_basis = derive_step(manifest, step1_flag=a.step1_cube,
                                   step2_flag=a.step2_cube)
    try:
        results = checks(cube_dir, step1=(step == 1))
    except Exception as exc:
        # a cube whose schema breaks the checks is a FAILED cube, loudly -
        # never a traceback that reads as a tooling problem (L566 class)
        results = [("checks_crashed", "FAIL", repr(exc))]
    results.append(("step_derivation", "PASS", f"Step-{step}: {step_basis}"))

    # M9 universe artifact check (the L445 wrong-artifact class), auto-wired:
    # the cube's own manifest names its tickers file. verify_universe_artifact
    # is non-blocking BY DESIGN (a deliberately narrow universe must stay
    # possible) - a FAIL here is a loud record for the human to judge.
    tf = None
    try:
        tf = (manifest.get("tickers") or {}).get("file")
    except AttributeError:
        tf = None
    if tf and (ROOT / tf).exists():
        u = _run([sys.executable, str(ROOT / "scripts" / "verify_universe_artifact.py"),
                  tf])
        results.append(("M9_universe_artifact",
                        "PASS" if u.returncode == 0 else "FAIL",
                        f"exit {u.returncode} on {tf} (verifier is "
                        "non-blocking by design - human judges a FAIL)"))
    else:
        results.append(("M9_universe_artifact", "SKIP",
                        f"no manifest tickers file resolvable ({tf!r})"))

    # family dispatch - the cube's own strategy column decides; nothing skips
    strategies = cube_strategies(cube_dir)
    fam_name = strategies[0] if len(strategies) == 1 else None
    fam = FAMILIES.get(fam_name) if fam_name else None
    notes: dict = {}
    grid_out = spot_out = None
    fam_fail = None
    if fam is None:
        fam_fail = (f"no registered post-config family for strategies "
                    f"{strategies or '[]'} - give its SPECS entry a complete "
                    f"`tools` adapter block (B2579; "
                    f"{FAMILY_REFUSALS.get(fam_name or '', 'no SPECS entry')}) "
                    f"(fail closed, L642; the old else-branch called this a "
                    f"pre-B2138 cube and skipped)")
        results.append(("family_dispatch", "FAIL", fam_fail))
    else:
        params, basis = fam["params"](manifest)
        if params is None:
            fam_fail = f"family {fam_name}: {basis} (fail closed, L642)"
            results.append(("family_dispatch", "FAIL", fam_fail))
        else:
            results.append(("family_dispatch", "PASS", f"{fam_name}: {basis}"))
            fr, notes, grid_out, spot_out = fam["run"](cube_dir, params, manifest,
                                                       step=step)
            results.extend(fr)

    grid: dict = {}
    if grid_out is not None and grid_out.exists():
        try:
            grid = json.loads(grid_out.read_text(encoding="utf-8")) or {}
        except (OSError, ValueError):
            grid = {}

    # step 5 lenses -> artifact
    try:
        lens_rows = lenses(cube_dir, step, grid, spot_out)
    except Exception as exc:
        lens_rows = [("lenses_crashed", "FAIL", repr(exc))]
    lens_out = ROOT / "output_audit" / f"{cube_dir.name}_lenses.json"
    try:
        lens_out.parent.mkdir(parents=True, exist_ok=True)
        lens_out.write_text(json.dumps(
            {"cube": cube_dir.name, "step": step, "step_basis": step_basis,
             "family": fam_name, "ts": _dt.datetime.now().isoformat(timespec="seconds"),
             "lenses": [{"lens": ln, "level": lv, "evidence": ev}
                        for ln, lv, ev in lens_rows]}, indent=1), encoding="utf-8")
    except OSError as exc:
        lens_rows.append(("lenses_artifact", "FAIL", f"could not write {lens_out}: {exc!r}"))
    findings = [(ln, lv, ev) for ln, lv, ev in lens_rows if lv in ("WARN", "FAIL")]

    # ledger-wide contradiction check (B2136), read before this run writes
    lp_chk = ROOT / "output_audit" / "postconfig_ledger.json"
    if lp_chk.exists():
        try:
            bad = ledger_contradictions(json.loads(lp_chk.read_text(encoding="utf-8")))
        except (OSError, ValueError) as exc:
            bad = [f"ledger unreadable: {exc!r}"]
        results.append(("ledger_status_matches_evidence",
                        "PASS" if not bad else "FAIL",
                        f"{len(bad)} row(s) claim DONE with contradicting evidence"
                        + (f": {bad[:4]}" if bad else "")))

    # ---- assemble the nine steps ------------------------------------------
    by = {n: (st, ev) for n, st, ev in results}
    sanity_fails = [n for n, st, _ in results
                    if st == "FAIL" and n not in _GRADER_CHECKS + _LEDGER_WIDE
                    and n != "family_dispatch"]
    summary = "; ".join(f"{n}={st}({ev[:60]})" for n, st, ev in results)
    steps: dict[str, tuple[str, str]] = {}
    steps["1_cube_sanity"] = ("FAIL" if sanity_fails else "DONE",
                              "run_postconfig: " + summary)
    m_core = ("M2_exits_per_entry_vs_registry", "M3_fill_date", "M4_holdout_touch",
              "M5_pnl_integrity", "M7_degraded_exits")
    m_missing = [m for m in m_core if m not in by]
    m_fail = [m for m in m_core if by.get(m, ("", ""))[0] == "FAIL"]
    if m_missing:
        steps["3_outlier_discrepancy_sweep"] = (
            "FAIL", f"mechanical core did not run ({m_missing} absent - checks "
                    f"crashed: {by.get('checks_crashed', ('', ''))[1][:120]})")
    elif m_fail:
        steps["3_outlier_discrepancy_sweep"] = (
            "FAIL", "mechanical core FAILED: " + "; ".join(
                f"{m}: {by[m][1][:100]}" for m in m_fail))
    else:
        steps["3_outlier_discrepancy_sweep"] = (
            "DONE", "AUTO (B2192): mechanical core executed by the battery "
                    "(M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded "
                    "exits) + the grader's union diagnosis-loss gate and "
                    "ci_lo-led ranking; " + "; ".join(
                        f"{m}={by[m][0]}" for m in m_core))
    for s_name in ("2_grade_with_config_params", "4_three_leg_spot_check"):
        steps[s_name] = notes.get(s_name) or ("FAIL", fam_fail or
                                              "family runner recorded nothing")
    # step 5 / 6
    n_w = sum(1 for _, lv, _ in lens_rows if lv == "WARN")
    n_f = sum(1 for _, lv, _ in lens_rows if lv == "FAIL")
    n_i = sum(1 for _, lv, _ in lens_rows if lv == "INFO")
    crashed = any(ln == "lenses_crashed" for ln, _, _ in lens_rows)
    lens_txt = (f"AUTO (B2520): lenses {len(lens_rows)} run: {n_w} WARN / {n_f} "
                f"FAIL / {n_i} INFO -> {lens_out.name}")
    if findings:
        lens_txt += "; findings: " + "; ".join(f"{ln} {lv}: {ev[:90]}"
                                                for ln, lv, ev in findings)
    steps["5_adversarial_lens_review"] = ("FAIL" if crashed else "DONE", lens_txt)
    if crashed:
        steps["6_post_fix_recheck"] = ("OPEN", "lens battery crashed - nothing "
                                               "to recheck until step 5 runs")
    elif findings:
        steps["6_post_fix_recheck"] = (
            "OPEN", f"{len(findings)} lens finding(s) need a recheck with evidence "
                    f"(#196): " + "; ".join(f"{ln} {lv}" for ln, lv, _ in findings))
    else:
        steps["6_post_fix_recheck"] = (
            "N/A", f"no lens finding ({len(lens_rows)} lenses, 0 WARN / 0 FAIL) "
                   "-> nothing to recheck; N/A on evidence")
    # 6b
    if fam is None or fam_fail:
        steps["6b_equivalence_class_check"] = ("FAIL", fam_fail or "no family")
    elif fam["single_combination"]:
        steps["6b_equivalence_class_check"] = (
            "N/A", "1 combination per cube (the swept parameters live in the "
                   "precompute the engine consumed); equivalence collapse "
                   "requires >= 2 combinations - N/A on evidence")
    elif grid:
        # tighten_breaker_block.py:549-550: carried = members of the RANKED
        # classes; distinct = outcome classes among ALL enumerated combinations
        steps["6b_equivalence_class_check"] = (
            "DONE", f"AUTO (B2192): the grader collapses identical outcomes - "
                    f"{len(grid.get('step1_ranking') or [])} ranked outcome "
                    f"classes carry {grid.get('step1_combinations_carried')} "
                    f"parameter combinations; {grid.get('step1_distinct_outcomes')} "
                    f"distinct outcome classes among {len(grid.get('results') or [])} "
                    f"combinations enumerated in {grid_out.name}")
    else:
        steps["6b_equivalence_class_check"] = ("FAIL", "no grid artifact to read "
                                                       "equivalence classes from")
    # 7
    e7 = by.get("step7_engine_implemented")
    if e7 is None:
        steps["7_implement_in_engine"] = ("FAIL", fam_fail or "engine check did not run")
    elif step == 1:
        steps["7_implement_in_engine"] = (
            ("N/A", "Step-1 ranking cube; admission happens at Step 2; nothing "
                    f"to implement. Engine check {e7[0]}: {e7[1][:140]}")
            if e7[0] == "PASS" else
            ("OPEN", "engine check FAIL on a Step-1 cube - a swept parameter "
                     "does not reach the engine; resolve before any Step-2 "
                     f"admission: {e7[1][:140]}"))
    else:
        steps["7_implement_in_engine"] = (
            ("DONE", f"engine check PASS on a Step-2 cube: {e7[1][:160]}")
            if e7[0] == "PASS" else
            ("OPEN", f"engine check FAIL on a Step-2 cube: {e7[1][:160]}"))
    # 8
    # B2574: a verdict on a cube whose replay ran on the ATR proxy is a
    # verdict on a different population - it is written (the numbers are
    # what they are) but OPEN, prefixed NOT COMPARABLE, never terminal.
    not_comparable = [ev for ln, lv, ev in lens_rows
                      if ln == "replay_atr_proxy" and lv == "FAIL"]
    if grid and not_comparable:
        steps["8_verdict_with_denominators"] = (
            "OPEN", f"{NOT_COMPARABLE_TAG} (B2574: {not_comparable[0][:160]}) - "
                    f"AUTO VERDICT (denominators from {grid_out.name}): "
                    + verdict_from_grid(grid, step))
    elif grid:
        steps["8_verdict_with_denominators"] = (
            "DONE", f"AUTO (B2520) VERDICT (denominators from {grid_out.name}): "
                    + verdict_from_grid(grid, step))
    else:
        steps["8_verdict_with_denominators"] = (
            "OPEN", "no grid artifact - step 2 produced nothing to derive a "
                    "verdict from" + (f" ({fam_fail})" if fam_fail else ""))
    assert set(steps) == set(STEPS), sorted(set(STEPS) ^ set(steps))

    for name, st, ev in results:
        print(f"  {st:<5} {name}: {ev}")
    print("\nSTEPS (every one recorded; DONE / N/A are terminal, OPEN / FAIL "
          "block the gate until dispositioned with evidence):")
    for s_name in STEPS:
        st, ev = steps[s_name]
        print(f"  {st:<5} {s_name}: {ev[:220]}")

    fails = [x for x in results if x[1] == "FAIL"]
    auto_notes = [(s_name, {"status": st, "evidence": ev})
                  for s_name, (st, ev) in steps.items()]
    if a.write_ledger:
        # B2207 (S6-B2205a): locked + atomic - see scripts/ledger_lock.py.
        from ledger_lock import locked_ledger_update
        ts = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")

        def _upgrade(ledger: dict) -> dict:
            entry = ledger.get(cube_dir.name) or {}
            for step_name, ev in auto_notes:
                entry = merge_row(entry, step_name, ev["status"], ev["evidence"], ts)
            ledger[cube_dir.name] = entry
            return ledger
        locked_ledger_update(_upgrade)
        print(f"[OK] ledger: all {len(STEPS)} steps recorded for {cube_dir.name}"
              f" ({'FAIL present' if fails else 'no FAIL'})")
    return 2 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
