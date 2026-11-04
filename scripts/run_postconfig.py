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
  M9 universe artifact; M10 gate receipt vs manifest sha; M11 closed
  trade-log fires with no exit-cube row (S6-B3267).

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
from grid_population import grid_population, ranked_count  # noqa: E402  (B2521 S6-B2520m; S6-B3292)

MEGA = ("NVDA", "MSFT", "GOOGL", "META", "TSLA", "AAPL")
TERMINAL = ("DONE", "N/A")
_GRADER_CHECKS = ("step2_grade_auto", "step2_free_levels", "step2_legs",
                  "step2_holdout_ledger",
                  "step2_grid_contract", "step2_resim_evidence",
                  "step4_spot_check_auto", "step4_sampling_contract", "step4_coverage",
                  "step7_engine_implemented")
# S6-B3397: a check that compares the cube with the GRADER's output is a
# step-3 discrepancy, not step-1 cube sanity - it fails step 3 alone.
_STEP3_ONLY = ("M12_entries_vs_grid_fires",)
_LEDGER_WIDE = ("ledger_status_matches_evidence",)


def graded_and_riders(cube_dir: Path) -> tuple:
    """B2721: (graded strategy, declared riders) from the cube's manifest.

    B2710 runs the whole smc consumer set per variant cube so one engine run
    serves every family member's offline depth (B2707). The BATTERY still
    grades exactly one strategy - the manifest's `strategy_subset` - and the
    others are declared `cube_riders`. S6-B2924: a rider can now be
    graded as its own leg via `--grade-rider`, which is OPT-IN - no
    automatic path passes it, so the default remains exactly one.
    Returns (None, []) when the manifest
    declares nothing, so the pre-B2721 one-strategy rule stands (L642)."""
    import json as _json
    m = cube_dir / "run_manifest.json"
    if not m.exists():
        return None, []
    try:
        d = _json.loads(m.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, []
    sub = d.get("strategy_subset")
    riders_rel = d.get("cube_riders")
    def _names(rel):
        if not rel:
            return []
        p = ROOT / str(rel)
        if not p.exists():
            return []
        return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()
                if ln.strip() and not ln.lstrip().startswith("#")]
    graded = _names(sub)
    return (graded[0] if len(graded) == 1 else None), _names(riders_rel)


def checks(cube_dir: Path, step1: bool = False, graded_leg: str | None = None):
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
    # B2721: a RIDER cube legitimately carries the whole consumer set
    # (B2707/B2710). The check is not "one strategy" but "the graded
    # strategy plus EXACTLY the declared riders" - an undeclared extra
    # is still a FAIL, which is the property the old rule protected.
    _graded, _riders = graded_and_riders(cube_dir)
    if _graded and _riders:
        _seen = set(df["strategy"].unique())
        _want = {_graded} | set(_riders)
        _extra, _missing = sorted(_seen - _want), sorted(_want - _seen)
        out.append(("one_strategy_or_declared_riders",
                    "PASS" if not _extra else "FAIL",
                    f"graded {_graded} + {len(_riders)} declared riders; "
                    f"cube carries {n_strat}"
                    + (f"; UNDECLARED {_extra}" if _extra else "")
                    + (f"; declared-but-absent {_missing} (a rider that "
                       "never fired is not an error)" if _missing else "")))
    else:
        out.append(("one_strategy", "PASS" if n_strat == 1 else "FAIL",
                    f"{n_strat} strategies"))
    # S6-B3397 (runbook 5.3 battery step 1, census line 1803): cube sanity
    # PASS requires the GRADED strategy in the cube. The rider arm above
    # passed a cube whose graded strategy never fired (it read as
    # 'declared-but-absent') and the one-strategy arm never compared its
    # single strategy with the manifest's. MEASURED at B3139q-r183 over 184
    # ledger cubes: 110 name a graded strategy and 110 of 110 carry it; 67
    # legacy manifests name none - SKIP, said plainly, never an assumed PASS
    # (L642). `graded_leg` is the leg --grade-rider grades, when given.
    _leg = graded_leg or _graded
    _present = sorted(str(x) for x in df["strategy"].dropna().unique())
    if _leg is None:
        out.append(("graded_strategy_present", "SKIP",
                    "the manifest names no single graded strategy (no one-name "
                    "strategy_subset) - nothing to compare; every post-B2721 "
                    "launch writes one, so treat SKIP on a NEW cube as a finding"))
    else:
        out.append(("graded_strategy_present",
                    "PASS" if _leg in _present else "FAIL",
                    f"graded leg {_leg}; the cube carries {len(_present)} "
                    f"strateg{'y' if len(_present) == 1 else 'ies'} "
                    f"{_present[:4]}" + ("" if _leg in _present else
                                         " - the cube does not hold the strategy "
                                         "it was run to grade")))
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    # B2724 instance 5 (LATENT): without the strategy key, two strategies
    # firing one ticker on one day summed their exits and read as a
    # registry mismatch. It passed on this cube; fixed before it bites.
    _gb = (["strategy", "ticker", "entry_date"] if "strategy" in df.columns
           else ["ticker", "entry_date"])
    epe = df.groupby(_gb).exit_method.nunique().unique()
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

    # M11 (S6-B3267, owner ruling (a) 2026-10-22): a CLOSED trade-log fire
    # with no exit-cube row is an entry M2 cannot see - M2 judges the
    # entries the cube holds (L952 / S6-B3258: 349 of 189,471 closed R5
    # fires carry none). B2046's fix makes the expected count 0; this
    # verifies it on every landing through the ONE coverage definition.
    tl11 = cube_dir / "trade_log.csv"
    if not tl11.exists():
        out.append(("M11_closed_fires_in_cube", "SKIP",
                    "no trade_log.csv - nothing to compare; the engine writes "
                    "one on every run, so treat SKIP on a NEW cube as a finding"))
    else:
        try:
            import exit_cube_coverage as _ecc
            cov = _ecc.coverage(cube_dir, cube_df=df)
            miss = cov["missing"]
            out.append(("M11_closed_fires_in_cube", "PASS" if miss == 0 else "FAIL",
                        f"{cov['covered']} of {cov['closed_fires']} closed "
                        f"trade-log fires have exit-cube rows; {miss} missing"
                        + (f" - whole {cov['whole'][:3]} partial "
                           f"{cov['partial'][:3]}" if miss else "")))
        except Exception as exc:
            out.append(("M11_closed_fires_in_cube", "FAIL",
                        f"coverage could not be read ({exc!r}) - fail closed (L642)"))

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
    # B2622 (S6-B2578a): when the dir records its build params, the arm's
    # declared INST_* values must match them - a mis-built tag becomes a
    # FAIL here instead of a wrong-population grade. Absence is disclosed,
    # not failed: the pre-B2622 tags carry no record, and failing them
    # would HALT a live landing on its own gate (backfill-first caveat).
    rec_path = exp / "build_params.json"
    if rec_path.exists():
        try:
            rec = json.loads(rec_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return False, f"build_params.json unreadable: {exc!r}"
        pairs = (("min_consecutive_quarters", "INST_MIN_CONSECUTIVE_QUARTERS", int, 4),
                 ("growth_lookback_quarters", "INST_GROWTH_LOOKBACK_QUARTERS", int, 4),
                 ("growth_multiple", "INST_GROWTH_MULTIPLE", float, 1.10))
        bad = []
        for rk, ek, cast, dflt in pairs:
            want = cast(arm_env.get(ek, dflt))
            got_v = rec.get(rk)
            if got_v is not None and cast(got_v) != want:
                bad.append(f"{rk}: dir built at {got_v}, arm declares {want}")
        if bad:
            return False, ("precompute BUILT AT DIFFERENT PARAMS than the arm "
                           "declares (S6-B2578a): " + "; ".join(bad))
        return True, (f"precompute_dir {exp.name} matches the arm; "
                      f"build_params.json verified")
    return True, (f"precompute_dir {exp.name} matches the arm "
                  f"(no build_params.json - pre-B2622 tag, provenance "
                  f"unverifiable, disclosed)")


# S6-B3397 (runbook 2.1 R6, census line 663): the spot check samples n=50
# with seed 42. The battery passes both on every family's argv, so the rule
# has ONE owner instead of eleven checker defaults - MEASURED at B3139q-r183,
# 4 of 11 checkers defaulted to a date seed (5 of 17 families) - and
# spot_sampling_check verifies the artifact recorded what was passed: a
# checker that accepts --seed and ignores it is the L751 class.
SPOT_N = 50
SPOT_SEED = 42


def spot_sample_size(doc):
    """The sample size a spot artifact records: `n_sampled` (6 checkers) or
    `sampled` (5 checkers). MEASURED r183: 53 of 113 artifacts carry only
    `sampled`, and spot_summary, reading `n_sampled` alone, wrote
    'n_sampled None' into the ledger 110 times (the L724 class). None when
    neither is recorded - an unmeasured size stays absent (L580)."""
    if not isinstance(doc, dict):
        return None
    v = doc.get("n_sampled")
    return v if v is not None else doc.get("sampled")


def spot_sampling_check(spot_out: Path, population) -> tuple[bool, str]:
    """R6 on the artifact the checker wrote: the recorded seed is SPOT_SEED
    and the recorded sample is min(SPOT_N, population), the graded leg's
    distinct cube entries. MEASURED r183: 3 of 3 sub-50 artifacts whose cube
    is on disk sampled exactly their population (40 of 40, 37 of 37, 29 of
    29). Fails closed on an unreadable artifact, an unrecorded seed or size,
    or an unknown population (L642)."""
    try:
        doc = json.loads(spot_out.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError) as exc:
        return False, f"R6: spot artifact {spot_out.name} unreadable ({exc!r})"
    seed, size = doc.get("seed"), spot_sample_size(doc)
    if seed is None or size is None:
        return False, (f"R6: {spot_out.name} records seed {seed!r} and sample size "
                       f"{size!r} - the n=50 seed 42 rule cannot be shown (fail closed, L642)")
    if population is None:
        return False, ("R6: the graded leg's cube entries could not be counted, so the "
                       "expected sample size is unknown (fail closed, L642)")
    want = min(SPOT_N, int(population))
    if seed != SPOT_SEED:
        return False, (f"R6: {spot_out.name} sampled with seed {seed}, the battery passed "
                       f"--seed {SPOT_SEED} - the checker did not apply it (L751)")
    if int(size) != want:
        return False, (f"R6: {spot_out.name} sampled {size} of a {population}-entry "
                       f"population; the rule is min({SPOT_N}, population) = {want}")
    return True, f"R6: sampled {size} of {population} entries with seed {seed}"


def spot_summary(spot_out: Path) -> str:
    """Step-4 evidence from the ARTIFACT, never from stdout - the smc checker
    prints a blank line before 'wrote ...', so a stdout tail lost the tally
    (measured on the first B2520 dry run)."""
    try:
        sd = json.loads(spot_out.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return f"artifact {spot_out.name} unreadable: {exc!r}"
    s = (f"n_sampled {spot_sample_size(sd)} seed {sd.get('seed')}: "
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


_KEY_UNSET = object()


def artifact_key(cube_dir: Path, graded=_KEY_UNSET,
                 riders=_KEY_UNSET) -> str:
    """S6-B2918: the battery artifact PREFIX and the ledger KEY, which
    are one contract - postconfig_doc.build() derives every artifact path
    from the ledger key.

    A cube that declares RIDERS carries more than one strategy and is
    graded ONE LEG AT A TIME, so a bare cube-name key makes the second
    grading overwrite the first leg's artifacts and verdict - and
    merge_row never downgrades, so the second leg's FAIL lands under the
    first leg's DONE.

    MEASURED at B2923: 1 of 120 completed cubes declares riders and 0 of
    127 ledger keys contain "__", so gating the per-leg key on riders
    leaves 119 of 120 on their historical bare key and every existing
    artifact valid. A cube with no riders, or whose manifest names no
    single graded strategy, keeps the bare key (L642 - fall back to the
    historical behaviour, never to an invented key)."""
    # S6-B2918 (L728): a SENTINEL, not None. `graded=None` is a real
    # answer - "the manifest names no single graded strategy" - and
    # overloading it with "caller supplied nothing" sent that case to
    # the filesystem instead of falling back to the bare key.
    if graded is _KEY_UNSET or riders is _KEY_UNSET:
        _g, _r = graded_and_riders(cube_dir)
        graded = _g if graded is _KEY_UNSET else graded
        riders = _r if riders is _KEY_UNSET else riders
    if riders and graded:
        return "%s__%s" % (cube_dir.name, graded)
    return cube_dir.name


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
    # S6-B2918: per-LEG key on a cube that carries a pair (see
    # artifact_key) - a bare cube key lets the second leg overwrite the
    # first leg's verdict.
    _key = artifact_key(cube_dir, fam_name)
    grid_out = ROOT / "output_audit" / f"{_key}_grid_auto.json"
    spot_out = ROOT / "output_audit" / f"{_key}_spot_check.json"
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
    step2_na_row = None   # S6-B2919: set on an honest not-evaluable verdict
    _grid: dict = {}      # S6-B3367: the Step-2 grid, read below when graded
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
            if not graded:
                # S6-B2919 (owner ruled 2026-09-22): an HONEST
                # not-evaluable verdict is a terminal N/A carrying
                # its reason - an evidenced answer, not a failure
                # needing hand disposition. The fail-closed path
                # remains for a grid whose step2 block is ABSENT or
                # carries no such verdict (the L642 malformed case).
                _s2b = _grid.get("step2")
                _hv = (_s2b.get("verdict")
                       if isinstance(_s2b, dict) else None)
                if _hv in ("BELOW_POWER_FLOOR", "NO_HOLDOUT_ROWS",
                           "NO_EXIT_SELECTABLE"):
                    step2_na_row = (
                        "step2_grade_auto", "N/A",
                        "%s: %s - terminal N/A per owner ruling "
                        "2026-09-22 (S6-B2919)"
                        % (_hv, str(_s2b.get("reason") or "")[:160]))
    if step2_na_row is not None:
        results.append(step2_na_row)
    else:
        results.append(("step2_grade_auto", "PASS" if ok2 else "FAIL",
                        f"exit {g.returncode}; {label} -> {grid_out.name}"
                        + (f"; {why2[:200]}" if why2 else "")
                        + ("" if ok2 or why2 else f"; {_tail(g)[:160]}")))
    # S6-B3367 (#299): a Step-2 verdict names both legs - depth is this cube,
    # breadth what the spec's arm declared at launch (make_spec --breadth-leg;
    # the launch gate refuses a Step-2 spec without it). An unproven leg fails
    # step 2 closed; a failing verdict with a leg not run reads as that leg's.
    legs_errs: list = []
    if step == 2:
        import step2_legs as _sl
        legs = {"depth": {"state": "ran",
                          "evidence": f"{cube_dir.name} (this landing's Step-2 cube)"},
                "breadth": _sl.arm_breadth_leg(manifest)}
        legs_errs = _sl.legs_refusals(legs)
        _s2b = _grid.get("step2") if isinstance(_grid, dict) else None
        _s2v = _s2b.get("verdict") if ok2 and isinstance(_s2b, dict) else None
        results.append((
            "step2_legs", "FAIL" if legs_errs else "PASS",
            legs_errs[0] if legs_errs else
            (_sl.disposition(True, legs) if _s2v == "FAIL" else
             "both legs named: depth ran, breadth " + str(legs["breadth"].get("state")))))
    # S6-B3395 Batch 7c (runbook 0.3 / 1.1 item 6 / 4.4 item 6): a Step-2 grade
    # that read the holdout is COUNTED in the holdout-read ledger, once per grid
    # artifact; an undeclared re-read of the same arm-env config fails step 2
    # closed - its run passed no launch door (holdout_reads.engine_grade)
    ledger_why = None
    _s2g = _grid.get("step2") if isinstance(_grid, dict) else None
    if step == 2 and ok2 and isinstance(_s2g, dict) and _s2g.get("holdout_read") is True:
        import holdout_reads as _hr
        _arm, _ = _arm0(manifest)
        try:
            ledger_why, _lev = _hr.engine_grade(grid_out, _grid, _arm, strategy=fam_name,
                                                owner_word=manifest.get("owner_word"))
        except SystemExit as exc:      # an unreadable ledger fails step 2 (L642)
            ledger_why, _lev = str(exc), ""
        results.append(("step2_holdout_ledger", "FAIL" if ledger_why else "PASS",
                        ledger_why or _lev))
    # B2569 (owner directive 2026-09-02): a family whose band carries FREE
    # levels grades them on EVERY landing, reproduction-gated - never once at
    # strategy level (the S6-B2501/B2504 class bug). A reproduction failure
    # exits nonzero and FAILS step 2 closed.
    fb = tools.get("free_levels")
    okf, free_out, fl = True, None, None
    if fb:
        free_out = ROOT / "output_audit" / f"{_key}_free_levels.json"
        fl = _run([sys.executable, str(ROOT / "scripts" / fb["script"]),
                   "--cube", str(cube_dir), "--out", str(free_out)],
                  _sub_env(arm_env, fb))
        okf = fl.returncode == 0 and free_out.exists()
        # B2576: the grader's verdict line, not whatever stderr printed last
        results.append(("step2_free_levels", "PASS" if okf else "FAIL",
                        f"exit {fl.returncode}; reproduction-gated free levels "
                        f"-> {free_out.name}; {_verdict_line(fl)[:160]}"))
    # S6-B3397 (runbook 2.1 R4, census 661): the landed grid carries the
    # B2505 contract - its readers cannot place rows it does not declare
    cerrs: list = []
    if ok2:
        try:
            _cg = json.loads(grid_out.read_text(encoding="utf-8")) or {}
        except (OSError, ValueError) as exc:
            _cg, cerrs = {}, [f"grid unreadable: {exc!r}"]
        if not cerrs:
            cerrs = grid_contract_errors(_cg, fam_name)
        results.append(("step2_grid_contract", "FAIL" if cerrs else "PASS",
                        "; ".join(cerrs) if cerrs else
                        "B2505 contract holds: config, strategy, instrument, "
                        "cube / in-sample / holdout counts, population"))
    # S6-B3397 (runbook 4.3 item 4, census 1079): a graded variant landing is
    # registered as engine resim evidence - a crash is a FAIL row (L642)
    rerrs: list = []
    if ok2:
        try:
            _rs, _rev, rerrs = register_resim_evidence(fam_name, cube_dir, p, _key, grid_out)
        except Exception as exc:                      # noqa: BLE001
            _rs, _rev, rerrs = "FAIL", f"crashed: {exc!r}"[:200], [repr(exc)]
        results.append(("step2_resim_evidence", _rs, _rev))
    note2 = gb.get("note", "AUTO")
    notes["2_grade_with_config_params"] = (
        ("FAIL", f"grid contract broken (R4, S6-B3397): {'; '.join(cerrs)[:200]}")
        if ok2 and okf and cerrs else
        ("FAIL", f"resim evidence not registered (S6-B3397): {rerrs[0][:200]}")
        if ok2 and okf and rerrs else
        ("FAIL", f"Step-2 legs unproven (S6-B3367): {legs_errs[0][:200]}")
        if ok2 and okf and legs_errs else
        ("FAIL", f"Step-2 holdout read not admissible (S6-B3395): {ledger_why[:200]}")
        if ok2 and okf and ledger_why else
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
           *_flag_args(sb, tools, p),
           # S6-B3397 (R6): the battery owns the sampling rule - LAST, so it
           # wins over a checker default or an `extra` (argparse keeps the last)
           "--n", str(SPOT_N), "--seed", str(SPOT_SEED),
           "--out", str(spot_out)]
    # S6-B2917: a FAMILY can be a long/short PAIR, and a spot checker that
    # defaults to one leg will silently check the wrong one. MEASURED: the
    # candle blocks passed no --strategy, so grading the short leg ran the
    # check on the long leg and recorded step 4 DONE against it. A block
    # that declares `strategy_flag` is TOLD which leg it is grading;
    # families whose checker takes no such flag declare none and are
    # unchanged.
    if sb.get("strategy_flag"):
        cmd += [str(sb["strategy_flag"]), fam_name]
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
    # S6-B3397 (census 1874): the coverage audit, on every landing
    cov_st, cov_ev = spot_coverage(fam_name, sb["script"])
    results.append(("step4_coverage", cov_st, cov_ev))
    if ok4:
        tail = f"{tail}; coverage {cov_ev}"
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



def direction_lens_verdict(dirs: list[str], graded: str | None) -> tuple[str, str]:
    """S6-B3119a: the single-strategy arm of direction_consistency.

    A DUAL strategy (long+short branches in ONE registration - bollinger_lower
    was the first the battery met) legitimately carries BOTH directions, so
    two directions under a dual's name is the design, not a finding. The
    discriminator is build_phase_1b_roster.is_dual - the ONE definition
    (B1454/B1778, source-inspected: an fs= branch), never a name heuristic.
    Fail-closed: if the detector cannot run, the FAIL stands (L642)."""
    if len(dirs) <= 1:
        return ("INFO", f"directions {dirs} (single direction)")
    detector_note = ""
    if graded:
        try:
            from build_phase_1b_roster import is_dual
            if is_dual(graded):
                return ("INFO",
                        f"graded {graded} is DUAL (is_dual source check) - "
                        f"directions {dirs} are its own two legs, the design "
                        "and not a finding (S6-B3119a)")
        except Exception as exc:                        # noqa: BLE001
            # not a silent pass (test_b2128): the FAIL below carries WHY the
            # detector could not run, and fail-closed stands (L642)
            detector_note = (f"; is_dual detector unavailable "
                             f"({type(exc).__name__}: {exc}) - fail-closed")
    return ("FAIL", f"directions {dirs} (one strategy, one direction expected)"
            + detector_note)

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
def selection_margin_row(rk: list, unit: str, step: int = 1) -> tuple:
    """The rank-1 vs rank-2 margin lens (S6-B2581b, re-cut B2621/S6-B2611a).

    THE AXIS, labeled (the B2611 audit's finding): this lens informs the EXIT
    choice inside one cube and nothing else - Step-1 admission ranks CONFIGS
    by their best exit, so an exit tie never moves a config's score there.

    THE DISCRIMINATOR IS THE STEP, NOT THE SIGN. The old predicate (a
    sign gate on rank-1) imported a bar the Step-1 admission rule forbids
    (B1608: ranked list, NO gates - a negative rank-1 is still admitted).
    Where the exit choice IS consumed - a Step-2 cube, whose own in-sample
    selection names the ADMISSION exit (owner ruling 2(i), 2026-09-05) - a
    noise-level margin is a live selection risk whatever the sign. Where it
    is not (Step 1), the row is INFO with the axis stated, which also keeps
    the S6-B2581b incident closed (the mult1.25 WARN that held a Step-1
    landing hostage over a tie between two exits nothing would consume).
    """
    if len(rk) >= 2 and rk[0].get("is_ci_lo") is not None \
            and rk[1].get("is_ci_lo") is not None:
        r1 = float(rk[0]["is_ci_lo"])
        margin = r1 - float(rk[1]["is_ci_lo"])
        live = step == 2
        why = ("; Step-2 cube: the IS selection names the admission exit "
               "(ruling 2i), so a noise margin is a live risk at any sign"
               if live else
               "; INFO not WARN - Step-1 admission ranks CONFIGS (exit ties "
               "never move a config score); this lens informs only a "
               "pre-registered exit choice (S6-B2611a)")
        return ("selection_margin",
                "WARN" if (margin < 0.05 and live) else "INFO",
                f"rank-1 [{row_label(rk[0])}] is_ci_lo {rk[0]['is_ci_lo']} vs "
                f"rank-2 [{row_label(rk[1])}] {rk[1]['is_ci_lo']}: margin "
                f"{margin:.3f} between {unit}; WARN < 0.05 (selection at "
                f"noise level){why}")
    if rk:
        return ("selection_margin", "INFO",
                f"1 ranked row ({unit}) - no margin to measure")
    return ("selection_margin", "INFO", "no ranked row in the grid artifact")


def grading_provenance_lens(cube_dir: Path) -> tuple:
    """S6-B3120c(b) / L844: compare the grading surface's digest NOW
    against the manifest's freeze-time grading_sha256. INFO either way -
    a drift is DISCLOSED, never refused (L857b: a refusal spanning a
    campaign blocks every unrelated turn inside it; per-landing identity
    is already stamped by graded_with). A manifest without the field is
    a pre-B3120 freeze, said plainly rather than treated as clean."""
    import json as _json
    m = cube_dir / "run_manifest.json"
    try:
        frozen = (_json.loads(m.read_text(encoding="utf-8"))
                  .get("grading_sha256"))
    except (OSError, ValueError):
        frozen = None
    if not isinstance(frozen, dict) or not frozen.get("digest"):
        return ("grading_provenance", "INFO",
                "manifest carries no grading_sha256 (pre-B3120 freeze) - "
                "grading identity is the landing's graded_with stamp only")
    try:
        from run_wave import grading_surface_sha256
        now = grading_surface_sha256()
    except Exception as exc:                        # noqa: BLE001
        return ("grading_provenance", "INFO",
                f"grading surface digest unavailable ({type(exc).__name__}:"
                f" {exc}) - comparison not performed, said plainly")
    if now["digest"] == frozen["digest"]:
        return ("grading_provenance", "INFO",
                f"grading surface UNCHANGED since freeze "
                f"({now['n_files']} files, digest {now['digest'][:12]})")
    return ("grading_provenance", "INFO",
            f"grading surface MOVED since freeze: freeze "
            f"{frozen['digest'][:12]} ({frozen.get('n_files')}) -> now "
            f"{now['digest'][:12]} ({now['n_files']}) - DISCLOSED, not "
            "refused (L857b); each landing's own code identity is its "
            "graded_with stamp")


def lenses(cube_dir: Path, step: int, grid: dict, spot_out: Path | None,
           family=None) -> list:
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

    # S6-B3134a part C (B3136): the eligibility lens - every entry asked the
    # fixed engine's screen question through the ONE predicate
    # (backtest/data/eligibility.py). Report-only: INFO clean, WARN leaks in a
    # pre-B3135 (unstamped) cube, FAIL when a daily_subtract_v1-stamped cube
    # still carries one (the engine fix regressed). A crash is a FAIL row,
    # never a silent skip (#122).
    try:
        import eligibility_leak as _el
        out.append(_el.lens_row(_el.cube_report(cube_dir)))
    except Exception as exc:                          # noqa: BLE001
        out.append(("eligibility_leak", "FAIL", f"crashed: {exc!r}"[:200]))

    # rank-1 vs rank-2 on the ranking key: the rows are OUTCOME CLASSES on a
    # multi-combination grid (two classes may share an exit) and EXITS on a
    # single-combination grid - row_label names whichever it is.
    rk = grid.get("step1_ranking") or []
    # B2521 (S6-B2520m): the population question has ONE owner now.
    _, _pop_field, _pop_unit = grid_population(grid)
    unit = {"per_exit": "exits", "rows": "cell-exit lines"}.get(_pop_field,
                                                                "outcome classes")
    out.append(selection_margin_row(rk, unit, step))
    # S6-B3397 (runbook 2.4 item 7 / 5.3 step 3, census 795 + 1844): every
    # swept level changes the outcome - a crash is a FAIL row, never a skip
    try:
        out.append(grid_bands_lens(grid, family) if family else
                   ("band_levels_change_outcome", "INFO",
                    "no family resolved - no grid keys to check"))
    except Exception as exc:                          # noqa: BLE001
        out.append(("band_levels_change_outcome", "FAIL", f"crashed: {exc!r}"[:200]))
    # S6-B3397 (Lens 12, census 1910): each grade flag moved alone must be
    # REFUSED by its grader - a crash is a FAIL row, never a skip
    try:
        out.append(effective_parameter_lens(cube_dir, step, family, touched))
    except Exception as exc:                          # noqa: BLE001
        out.append(("effective_parameter", "FAIL", f"crashed: {exc!r}"[:200]))
    # S6-B3397 (runbook 2.4 item 19 + 1.5, census 817 / 1293; the redundancy
    # row, census 588): the landed leg against the R5 baseline over the
    # cube's own tickers and window - a crash is a FAIL row, never a skip
    try:
        out.extend(r5_baseline_lenses(cube_dir, read_manifest(cube_dir), grid, family))
    except Exception as exc:                          # noqa: BLE001
        out.append(("entries_per_ticker_vs_r5", "FAIL", f"crashed: {exc!r}"[:200]))
        out.append(("registration_redundancy", "FAIL", f"crashed: {exc!r}"[:200]))

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
    out.append(grading_provenance_lens(cube_dir))

    if "direction" in df.columns:
        # B2724 instance 3: a RIDER cube carries both directions BY DESIGN
        # (B2707/B2710 - long and short consumers share one variant run).
        # The property worth checking is that the GRADED strategy is
        # single-direction; the riders' directions are not a finding.
        _g, _r = graded_and_riders(cube_dir)
        if _g and _r and "strategy" in df.columns:
            _sub = df[df["strategy"] == _g]
            dirs = sorted(str(x) for x in _sub["direction"].dropna().unique())
            _all = sorted(str(x) for x in df["direction"].dropna().unique())
            # S6-B3119b: the rider arm routes through the SAME dual-aware
            # verdict as the else arm - a DUAL graded with riders is its
            # own two legs, not a finding (the S6-B3119a class, both arms)
            _lvl, _msg = direction_lens_verdict(dirs, _g)
            out.append(("direction_consistency", _lvl,
                        _msg + f"; the cube also carries {_all} across "
                        f"{len(_r)} declared riders, which is the B2710 "
                        "design and not a finding"))
        else:
            dirs = sorted(str(x) for x in df["direction"].dropna().unique())
            # S6-B3119a: a DUAL strategy carries both directions by design
            _lvl, _msg = direction_lens_verdict(dirs, _g)
            out.append(("direction_consistency", _lvl, _msg))

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
    elif _pf == "rows":                          # lever4_step1 / grade_knob_config
        # S6-B3397: these lines carry no verdict - graded means is_sharpe set
        _graded = [r for r in _rows if r.get("is_sharpe") is not None]
        _cells = sorted({str(r.get("cell")) for r in _rows})
        s = (f"{len(_graded)} of {len(_rows)} cell-exit lines graded across "
             f"{len(_cells)} cell(s) {_cells[:4]}")
    else:
        cnt = Counter(str(r.get("verdict")) for r in res)
        s = (f"{len(res)} combinations enumerated: "
             + ", ".join(f"{v} {k}" for k, v in cnt.most_common()))
        pq = grid.get("provisional_qualifiers")
        if isinstance(pq, (list, dict)):
            s += f"; provisional_qualifiers {len(pq)}"
    if top:
        t = top[0]
        # S6-B3292: the count carries the key it was counted under -
        # lever4 rows have no `fires` and read 'fires None' for 4 of 4 legs
        s += (f"; rank-1 [{row_label(t)}] is_ci_lo {t.get('is_ci_lo')} "
              f"is_sharpe {t.get('is_sharpe')} {ranked_count(t)}")
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


def leg_entry_counts(cube_dir: Path, strategy) -> tuple:
    """(all, in-sample) distinct (ticker, entry_date) entries of `strategy`
    in the cube - the populations R6 and M12 compare with (S6-B3397). The
    in-sample split is roster_core.in_sample, the ONE definition (it excludes
    the HO_START boundary day). (None, None) when unreadable."""
    import pandas as pd
    import roster_core as rc
    try:
        df = pd.read_csv(cube_dir / "trade_exit_detail.csv", low_memory=False,
                         usecols=["strategy", "ticker", "entry_date"])
    except (OSError, ValueError, KeyError):
        return None, None
    if strategy:
        df = df[df["strategy"].astype(str) == str(strategy)]
    df = df.drop_duplicates(subset=["ticker", "entry_date"]).copy()
    df["entry_date"] = pd.to_datetime(df["entry_date"], errors="coerce").dt.date
    return int(len(df)), int(len(rc.in_sample(df.dropna(subset=["entry_date"]))))


def entries_vs_grid_count(grid: dict, leg_all, leg_is) -> tuple[str, str]:
    """M12 (S6-B3397; runbook 5.3 step 3, census line 1838): the graded
    leg's cube entries equal the grid's largest trade count, or the grader
    silently lost trades it could not diagnose (L454). MEASURED r183: 110 of
    110 landed grids equal. `fires` is in-sample on the per-exit graders and
    full-period on tighten_breaker_block (b2399: 437 = all 437, in-sample
    307), so a `fires` count may match either population and the evidence
    names which; the rows-list dialect states both and both must match.
    No grid -> SKIP (step 2's own FAIL says why); a grid with no count, or
    an uncountable cube -> FAIL closed (L642)."""
    from grid_population import grid_trade_counts
    if not grid:
        return "SKIP", "no grid artifact - step 2 produced none (its own row says why)"
    if leg_all is None or leg_is is None:
        return "FAIL", ("the graded leg's cube entries could not be counted - "
                        "fail closed (L642)")
    c = grid_trade_counts(grid)
    if not c:
        return "FAIL", ("the grid's rows carry no trade count (fires / is_n / "
                        "full_n_count_only) - diagnosis loss cannot be checked; "
                        "fail closed (L642)")
    if "fires" in c:
        f = c["fires"]
        if f == leg_is:
            return "PASS", f"grid max fires {f} = the cube's {leg_is} in-sample entries"
        if f == leg_all:
            return "PASS", f"grid max fires {f} = the cube's {leg_all} full-period entries"
        return "FAIL", (f"grid max fires {f} vs the cube's {leg_is} in-sample / "
                        f"{leg_all} full-period entries - trades lost between the "
                        "cube and the grid (L454)")
    bad = []
    if "is_n" in c and c["is_n"] != leg_is:
        bad.append(f"is_n {c['is_n']} vs {leg_is} in-sample entries")
    if "full_n_count_only" in c and c["full_n_count_only"] != leg_all:
        bad.append(f"full_n_count_only {c['full_n_count_only']} vs {leg_all} full-period entries")
    if bad:
        return "FAIL", "; ".join(bad) + " - trades lost between the cube and the grid (L454)"
    return "PASS", ("grid " + ", ".join(f"{k} {v}" for k, v in c.items())
                    + f" = the cube's {leg_is} in-sample / {leg_all} full-period entries")


def grid_bands_lens(grid: dict, family) -> tuple:
    """S6-B3397 (runbook 2.4 item 7 / 5.3 step 3, census lines 795 and 1844):
    every swept LEVEL must change the outcome - verify_grid_bands.analyse over
    the family's own grid_keys (SPECS tools), anchored at each param's
    production value (the anchor is carried for reproducibility, never judged
    inert). A grid that sweeps none of its keys is N/A, said as INFO. MEASURED
    at B3139q-r184 over 114 landed grids: 81 sweep no key, 23 clean, 10 flag
    tail_n 5 -> 10 (the documented B1610 saturation)."""
    import verify_grid_bands as vgb
    spec = SPECS.get(family) or {}
    keys = list((spec.get("tools") or {}).get("grid_keys") or [])
    rows, _f, _u = grid_population(grid)
    swept = [k for k in keys if len({repr(r.get(k)) for r in rows
                                      if isinstance(r, dict) and k in r}) >= 2]
    if not swept:
        return ("band_levels_change_outcome", "INFO",
                f"no grid key of {keys} carries 2+ levels in this grid - "
                "nothing swept in-cube to check (N/A)")
    by_param = {p.get("param"): p for p in spec.get("params") or []}
    anchors = {k: by_param[k].get("production") for k in swept if k in by_param}
    reports, failures = vgb.analyse(rows, swept, vgb.DEFAULT_MIN_EFFECT, anchors)
    swept_txt = ", ".join(f"{r['param']} {r['changed']}/{r['groups']}" for r in reports)
    if failures:
        return ("band_levels_change_outcome", "WARN",
                f"{len(failures)} inert level pair(s): " + "; ".join(
                    f.split(". These")[0] for f in failures[:3])
                + f" (swept: {swept_txt}; anchors {anchors})")
    return ("band_levels_change_outcome", "INFO",
            f"every swept level changes the outcome (swept: {swept_txt})")


def pass_ci_lo(grid: dict) -> list:
    """The ci_lo of every PASS the grid records - its population's PASS rows
    and a PASS step2 block. ONE definition: step 8's denominators and the
    small-universe entries lens both ask it (S6-B3397)."""
    rows, _f, _u = grid_population(grid)
    out = [r.get("ci_lo") for r in rows
           if isinstance(r, dict) and r.get("verdict") == "PASS"]
    s2 = grid.get("step2")
    if isinstance(s2, dict) and s2.get("verdict") == "PASS":
        out.append(s2.get("ci_lo"))
    return out


def verdict_denominators(cube_dir: Path, manifest: dict, family, grid: dict) -> str:
    """S6-B3397 (runbook 5.3 step 8, census line 1956): what the verdict
    must also state - X of Y producers varied, exits_effective of the
    registry at the cube's SHA, and the ci_lo of every PASS. Raises when a
    part cannot be computed; the caller records step 8 OPEN with why."""
    import pandas as pd
    import roster_core as rc
    spec = SPECS[family]
    params = spec.get("params") or []
    _arm, env = _arm0(manifest)
    rows, _f, _u = grid_population(grid)

    def _n(v):
        try:
            return repr(float(v))
        except (TypeError, ValueError):
            return repr(str(v).strip())
    moved = [p for p in params if p.get("env") and p["env"] in env
             and _n(env[p["env"]]) != _n(p.get("production"))]
    swept = [p for p in params if len({repr(r.get(p.get("param"))) for r in rows
                                       if isinstance(r, dict) and p.get("param") in r}) >= 2]
    varied = {p["id"]: p for p in moved + swept}
    prods = {str(p.get("producer")) for p in params}
    v_prods = {str(p.get("producer")) for p in varied.values()}
    part1 = (f"producers varied {len(v_prods)} of {len(prods)} "
             f"(params {sorted(varied) or 'none'} of {len(params)}; arm-moved "
             f"{sorted(p['id'] for p in moved) or 'none'}, swept in-grid "
             f"{sorted(p['id'] for p in swept) or 'none'})")
    cube = rc.load_cube(cube_dir / "trade_exit_detail.csv")
    leg = cube[cube["strategy"].astype(str) == str(family)]
    registered = int(leg["exit_method"].nunique())
    _ex, stats = rc.select_exit(leg)
    eff = (stats or {}).get("exits_effective")
    part2 = (f"exits_effective {eff} of {registered} registered at the cube's SHA"
             if eff is not None else
             f"exits_effective not measurable - no exit graded in-sample "
             f"({registered} registered at the cube's SHA)")
    pass_ci = pass_ci_lo(grid)
    part3 = (f"ci_lo of every PASS: {pass_ci}" if pass_ci else
             "no PASS row, so no PASS ci_lo")
    return f"{part1}; {part2}; {part3}"


def baseline_scope(cube_dir: Path, manifest: dict, family=None):
    """(graded leg, tickers, start, end) for an R5 comparison over the landed
    cube's OWN universe and window (L376 / L378: only a matched scope is
    comparable), or (None, why) when the manifest cannot name them."""
    graded, _riders = graded_and_riders(cube_dir)
    graded = graded or family
    tk = manifest.get("tickers")
    rel = tk.get("file") if isinstance(tk, dict) else None
    win = manifest.get("window") or {}
    if not graded:
        return None, "the manifest names no graded strategy"
    if not rel or not (ROOT / str(rel)).exists():
        return None, f"the manifest's tickers file {rel!r} is not on disk"
    if not win.get("start") or not win.get("end"):
        return None, "the manifest carries no window"
    tickers = sorted({ln.strip() for ln in (ROOT / str(rel)).read_text(
        encoding="utf-8").splitlines() if ln.strip() and not ln.lstrip().startswith("#")})
    return (str(graded), tickers, str(win["start"])[:10], str(win["end"])[:10]), ""


def entries_rate_row(n_leg: int, n_r5: int, n_tickers: int, universe_r5: int,
                     has_pass: bool, graded: str, lo: str, hi: str,
                     arm_keys=()) -> tuple:
    """Runbook 2.4 item 19 + 1.5 (census 817 / 1293): the landed leg's entries
    per ticker against R5's for the same strategy, tickers and window. INFO
    on every landing; WARN only on a SMALL-universe PASS outside the S2 band
    (universe_ladder_run.S2_RATIO_BAND, B1514) - L382's rung passed all six
    gates at 26.63x the R5 rate. A variant arm's own knob moves the rate too,
    and R5 ran on an older engine, so the ratio also carries every engine
    change since; the evidence names the arm's settings. MEASURED at
    B3139q-r187 over 110 landed cubes: 66 inside the band, 10 below, 34
    above - mostly variant arms (the LEVER4 gate-budget arms 10.6 to 164x,
    the bollinger span sweep 0.17 to 4.1x); 1 landed grid records a PASS
    and it ran on the full 544, so 0 of the 110 would WARN."""
    import universe_ladder_run as ulr
    b_lo, b_hi = ulr.S2_RATIO_BAND
    small = n_tickers < universe_r5
    head = (f"{n_leg} {graded} entries over {n_tickers} tickers "
            f"({n_leg / n_tickers:.4f}/ticker) vs R5's {n_r5} on the same tickers "
            f"{lo}..{hi}")
    arm = (f"; the arm sets {sorted(arm_keys)[:3]}, so the ratio carries the "
           "variant's own effect beside the universe's") if arm_keys else ""
    tail = (f"; {'a PASS' if has_pass else 'no PASS'} on a {n_tickers}-ticker "
            f"universe (R5 ran {universe_r5}); band {b_lo}-{b_hi} "
            "(universe_ladder_run S2, B1514)")
    if n_r5 == 0:
        lvl = "WARN" if (has_pass and small) else "INFO"
        return ("entries_per_ticker_vs_r5", lvl,
                head + " - R5 has no baseline rate for it here" + arm + tail)
    ratio = n_leg / n_r5
    out = not (b_lo <= ratio <= b_hi)
    lvl = "WARN" if (has_pass and small and out) else "INFO"
    note = (" - a small-universe PASS outside the band is an ARTIFACT until the "
            "rate converges (runbook 2.4 item 19, L382)") if lvl == "WARN" else ""
    return ("entries_per_ticker_vs_r5", lvl,
            head + f" ({n_r5 / n_tickers:.4f}/ticker) = {ratio:.2f}x" + arm + tail + note)


def redundancy_row(leg, scope, graded: str, riders_frame=None, eligible=None) -> tuple:
    """The redundancy row of the runbook's verification table (census 588,
    CHECKLIST #169): does the landed leg now fire on another registration's
    trades? Jaccard on (ticker, entry_date) per direction against every other
    R5 registration over the same tickers and window, and against the cube's
    own riders (same engine run); audit_registration_redundancy's constants
    - REDUNDANT 0.70, NEAR_IDENTICAL 0.95, MIN_TRADES 50 - imported, one
    definition. WARN when a pair reaches REDUNDANT and the PRODUCTION pair
    (R5's own entries for the graded leg, same scope) did not - the change
    collapsed them; a pair already redundant at production is named as
    INFO, not this change's finding. `eligible` limits the R5 side to
    registrations that still trade (registered, not disabled): a pair with
    a disabled duplicate is already ruled on (STRATEGIES_DISABLED_DUPLICATE).
    MEASURED at B3139q-r187 over 110 landed cubes: 0 pairs at REDUNDANT; on
    R5's own squeeze_breakout and macd_crossover entries in a landed squeeze
    cube's scope it names the B1463 pairs at J 1.000 (the control)."""
    from audit_registration_redundancy import MIN_TRADES, NEAR_IDENTICAL, REDUNDANT

    def _sets(frame):
        return {(str(s), str(d)): set(zip(g["ticker"], g["entry_date"]))
                for (s, d), g in frame.groupby(["strategy", "direction"], observed=True)}
    mine = _sets(leg)
    prod = _sets(scope[scope["strategy"] == graded])
    r5_all = _sets(scope[scope["strategy"] != graded])
    r5_others = {k: v for k, v in r5_all.items() if eligible is None or k[0] in eligible}
    retired = len(r5_all) - len(r5_others)
    # (label, direction, the set compared, R5's production set for that name)
    cands = [(s, d, b, b) for (s, d), b in r5_others.items()]
    if riders_frame is not None and len(riders_frame):
        cands += [(f"{s} (rider)", d, b, r5_others.get((s, d), set()))
                  for (s, d), b in _sets(riders_frame).items()]
    compared = skipped = 0
    new, old, best = [], [], (0.0, None)
    for (_s, dirn), a in mine.items():
        if len(a) < MIN_TRADES:
            continue
        pa = prod.get((graded, dirn), set())
        for s, d, b, b_prod in cands:
            if d != dirn:
                continue
            if len(b) < MIN_TRADES:
                skipped += 1
                continue
            compared += 1
            inter = len(a & b)
            j = inter / len(a | b) if inter else 0.0
            if j > best[0]:
                best = (j, f"{s}|{d}")
            if j >= REDUNDANT:
                pj = (len(pa & b_prod) / len(pa | b_prod)) if (pa and pa & b_prod) else 0.0
                tag = "NEAR-IDENTICAL" if j >= NEAR_IDENTICAL else "REDUNDANT"
                rec = f"{s}|{d} J {j:.3f} {tag} (production {pj:.3f})"
                (old if pj >= REDUNDANT else new).append(rec)
    big = [k for k, v in mine.items() if len(v) >= MIN_TRADES]
    if not big:
        return ("registration_redundancy", "INFO",
                f"{graded}: {max((len(v) for v in mine.values()), default=0)} entries, "
                f"under MIN_TRADES {MIN_TRADES} - a Jaccard there is noise; not compared")
    base = (f"{graded} vs {compared} registrations over the same tickers and window "
            f"({skipped} under {MIN_TRADES} entries skipped, {retired} disabled or "
            f"retired not compared); bars {REDUNDANT} / {NEAR_IDENTICAL} "
            "(audit_registration_redundancy)")
    if new:
        return ("registration_redundancy", "WARN",
                f"{len(new)} pair(s) reach REDUNDANT that production did not - the "
                f"change collapsed them: {new[:3]}; " + base)
    if old:
        return ("registration_redundancy", "INFO",
                f"already redundant at production, not this change's finding: {old[:3]}; "
                + base)
    return ("registration_redundancy", "INFO",
            f"max J {best[0]:.3f} ({best[1]}); " + base)


def r5_baseline_lenses(cube_dir: Path, manifest: dict, grid: dict, family=None,
                       idx_loader=None) -> list:
    """S6-B3397: the two lenses that read the R5 baseline (r5_entry_index,
    built once and cached beside the R5 cube). An unnameable scope is N/A,
    said as INFO; an absent baseline is a WARN - the check did not run, which
    is never a silent pass (#122)."""
    names = ("entries_per_ticker_vs_r5", "registration_redundancy")
    scope_t, why = baseline_scope(cube_dir, manifest, family)
    if scope_t is None:
        return [(n, "INFO", f"not measurable: {why} (N/A)") for n in names]
    graded, tickers, lo, hi = scope_t
    import pandas as pd
    import r5_entry_index as rei
    try:
        idx = (idx_loader or rei.load)()
    except FileNotFoundError as exc:
        return [(n, "WARN", f"the R5 baseline is absent - the check did not run: {exc}")
                for n in names]
    d = pd.read_csv(cube_dir / "trade_exit_detail.csv", dtype=str,
                    usecols=["strategy", "direction", "ticker", "entry_date"])
    d["entry_date"] = d["entry_date"].str[:10]
    d = d.drop_duplicates()
    leg = d[d["strategy"] == graded]
    _g, riders = graded_and_riders(cube_dir)
    rider_frame = d[d["strategy"].isin(riders)] if riders else None
    scope = rei.scope(idx, tickers, lo, hi)
    n_r5 = int((scope["strategy"] == graded).sum())
    _arm, env = _arm0(manifest)
    rate = entries_rate_row(int(len(leg)), n_r5, len(tickers),
                            int(idx["ticker"].nunique()), bool(pass_ci_lo(grid)),
                            graded, lo, hi, tuple(env))
    from backtest.config import (STRATEGIES_DISABLED_DATA_SCARCITY,
                                 STRATEGIES_DISABLED_DUPLICATE,
                                 STRATEGIES_DISABLED_MISSING_PRODUCER)
    from backtest.signals.screener import ALL_STRATEGIES
    eligible = set(ALL_STRATEGIES) - (set(STRATEGIES_DISABLED_DATA_SCARCITY)
                                      | set(STRATEGIES_DISABLED_DUPLICATE)
                                      | set(STRATEGIES_DISABLED_MISSING_PRODUCER))
    return [rate, redundancy_row(leg, scope, graded, rider_frame, eligible)]


def grid_contract_errors(grid: dict, leg) -> list:
    """S6-B3397 (runbook 2.1 R4, census line 661): what the landed grid lacks
    of the B2505 contract - config, strategy (the graded leg), the grading
    instrument, the cube-row / in-sample / holdout counts, and a population
    list. Two dialects satisfy it: the B2505 graders write `grader` and an int
    `rows`; the B2774-stamped graders write `generator`, and the rows-LIST
    graders (lever4_step1, grade_knob_config, the smc step-1 graders) hold
    their population under `rows`, so their cube-row count is `cube_rows`.
    MEASURED at B3139q-r185 over 114 landed grids: 70 conform (5 graders);
    44 predate it (tighten_breaker_block 33, lever4_step1 9,
    grade_knob_config 2) - a re-grade regenerates them. [] when the contract
    holds."""
    def _int(v):
        return isinstance(v, int) and not isinstance(v, bool)
    errs = []
    if not isinstance(grid.get("config"), dict):
        errs.append("no `config` block")
    if str(grid.get("strategy")) != str(leg):
        errs.append(f"`strategy` {grid.get('strategy')!r} is not the graded leg {leg!r}")
    if not (grid.get("grader") or grid.get("generator")):
        errs.append("no grading-instrument stamp (`grader` / `generator`)")
    if not (_int(grid.get("rows")) or _int(grid.get("cube_rows"))):
        errs.append("no cube-row count (an int `rows`, or `cube_rows`)")
    for k in ("is_rows", "holdout_rows"):
        if not _int(grid.get(k)):
            errs.append(f"no int `{k}`")
    if not any(isinstance(grid.get(k), list) for k in ("results", "per_exit", "rows")):
        errs.append("no population list (`results` / `per_exit` / `rows`)")
    return errs


def register_resim_evidence(fam_name: str, cube_dir: Path, p: dict, key: str,
                            grid_out: Path) -> tuple:
    """S6-B3397 (runbook 4.3 item 4, census 1079): a graded VARIANT landing
    is registered as engine resim evidence the band-coverage gate counts -
    <key>_resim_evidence.json, an axis-grid artifact (no rows, a
    resim_configs list) that band_coverage_gate.artifact_kind reads and its
    _gather counts. Derived through grade_knob_config.knob_rows and
    resim_configs over the landed arm's values - the ONE definition the knob
    grader writes into its own grid; a grid that carries its own and
    disagrees FAILs (status, evidence, errors). A production arm registers
    nothing. MEASURED at B3139q-r188 over 101 ledger cubes resolving to a
    family with arm values: 95 variants, 94 of them without resim evidence
    (only the knob grader wrote it), 6 production arms; run live (output
    into a scratch root) it registered 95 - the knob grader's own entry
    agreeing - skipped 6 and failed 0, and the gate's coverage_report
    counted a registered bollinger level as tested."""
    import grade_knob_config as _gkc
    try:
        derived = _gkc.resim_configs(fam_name, _gkc.knob_rows(fam_name), p)
    except SystemExit as exc:
        msg = f"the family's knobs cannot be read: {exc}"[:200]
        return "FAIL", msg, [msg]
    try:
        own = (json.loads(grid_out.read_text(encoding="utf-8")) or {}).get("resim_configs")
    except (OSError, ValueError):
        own = None
    if own is not None and own != derived:
        msg = (f"the grader's resim_configs {own} disagree with the landed arm's "
               f"{derived} - one of them names the wrong levels")
        return "FAIL", msg[:240], [msg]
    if not derived:
        return "SKIP", ("production arm - no knob ran away from production, so "
                        "there is no resim level to register"), []
    out = ROOT / "output_audit" / f"{key}_resim_evidence.json"
    out.write_text(json.dumps({
        "strategy": fam_name, "cube": cube_dir.name,
        "generator": "scripts/run_postconfig.py register_resim_evidence (S6-B3397)",
        "graded_by": grid_out.name, "resim_configs": derived,
        "basis": "the landed arm's values (params_from_manifest) through "
                 "grade_knob_config.knob_rows + resim_configs"},
        indent=1), encoding="utf-8")
    return "PASS", (f"registered {out.name}: {derived} - band_coverage_gate reads "
                    "it as engine resim evidence (pass it with --artifacts)"), []


def _same_value(a, b) -> bool:
    def _n(v):
        try:
            return repr(round(float(v), 9))
        except (TypeError, ValueError):
            return str(v).strip()
    return _n(a) == _n(b)


def alt_flag_value(row: dict, landed):
    """A second, TYPE-COMPATIBLE value for a grade flag (Lens 12): the
    param's production, then its band and free-band levels, the first that
    differs from the landed value; a LEVER4 gate budget moves each k by one.
    None when no such value exists (the flag is then reported untested)."""
    def _num(v):
        try:
            float(v)
            return True
        except (TypeError, ValueError):
            return False
    if _num(landed):
        for v in ([row.get("production")] + list(row.get("band") or [])
                  + list(row.get("free_band") or [])):
            if v is not None and not isinstance(v, bool) and _num(v) \
                    and not _same_value(v, landed):
                return v
        return None
    try:
        d = json.loads(str(landed))
    except ValueError:
        return None
    if isinstance(d, dict) and d and all(
            isinstance(x, dict) and isinstance(x.get("k"), int) for x in d.values()):
        return json.dumps({s: {**x, "k": x["k"] + 1} for s, x in d.items()})
    return None


def effective_parameter_lens(cube_dir: Path, step: int, family, touched: int) -> tuple:
    """Lens 12 (runbook 5.3 lens table, census 1910 - 'a flag that was
    ACCEPTED: does changing it change the answer?'). A grade flag names the
    level the cube RAN at, so the right answer to a moved value is a
    REFUSAL - the grader verifies the flag against the landed arm (S6-B2900).
    Each tools.grade flag is moved ALONE to a type-compatible second value
    and the grader re-run into a temp dir: refused = verified; graded on =
    WARN, the flag is a stamp (one cube could be filed under another
    config's name). Runs only on a Step-1 cube with no holdout entry, so a
    re-grade can never read a holdout outside the ledger; a Step-2 cube is
    N/A with that reason. MEASURED at B3139q-r188 on the latest Step-1
    landing of each grade script (8 of 11 have one with arm values): 18 of
    24 flags verified; 6 graded on - grade_institutional_config 4 of 4,
    lever4_step1's --gate-budget and tighten_breaker_block's --span - the
    stamp class S6-B3417 fixes; until then those landings WARN here."""
    import tempfile
    name = "effective_parameter"
    if not family or family not in FAMILIES:
        return (name, "INFO", "no family resolved - no grade flags to move (N/A)")
    gb = SPECS[family]["tools"]["grade"]
    flags = dict(gb.get("flags") or {})
    if not flags:
        return (name, "INFO", f"{gb['script']} takes no grade flags (N/A)")
    if step != 1 or touched:
        return (name, "INFO", "N/A on a Step-2 cube or one with holdout entries - a "
                              "re-grade could read the holdout outside the ledger")
    manifest = read_manifest(cube_dir)
    p, why = params_from_manifest(family, manifest)
    if p is None:
        return (name, "INFO", f"no landed flag values: {why} (N/A)")
    tools = SPECS[family]["tools"]
    rows = {r["id"]: r for r in SPECS[family]["params"]}
    env = _sub_env(_arm_env(manifest), gb)
    verified, stamped, untested = [], [], []
    with tempfile.TemporaryDirectory() as tmp:
        for pid, flag in flags.items():
            key = tools["keys"][pid]
            alt = alt_flag_value(rows[pid], p[key])
            if alt is None:
                untested.append(f"{flag} (no second value)")
                continue
            q = dict(p)
            q[key] = alt
            r = _run([sys.executable, str(ROOT / "scripts" / gb["script"]),
                      "--cube", _cube_arg(cube_dir, gb), *_flag_args(gb, tools, q),
                      *list(gb.get("extra") or []),
                      "--out", str(Path(tmp) / f"{pid}.json")], env)
            said = (r.stdout or "") + (r.stderr or "")
            tag = f"{flag} {p[key]}->{alt}"
            if r.returncode == 0:
                stamped.append(tag)
            elif "error: argument" in said:
                untested.append(f"{tag} (argparse rejected the value)")
            else:
                verified.append(tag)
    n = len(flags)
    text = (f"{len(verified)} of {n} grade flags verified (a moved value was refused)"
            + (f"; untested {untested}" if untested else ""))
    if stamped:
        return (name, "WARN", f"{len(stamped)} of {n} grade flags graded on at a moved "
                              f"value - stamped, not verified against the landed arm: "
                              f"{stamped[:3]}; " + text)
    return (name, "INFO", text + f" ({gb['script']})")


def spot_coverage(strategy, checker_script) -> tuple:
    """S6-B3397 (runbook 5.3 step 4, census 1874): may the spot check CERTIFY
    this strategy? verify_spotcheck_coverage.audit with the family checker's
    own verifiable families. PASS = CERTIFIED; WARN = NOT CERTIFIED, the
    uncovered families and keys named - a disclosure, never a FAIL: whether it
    holds step 4 open is the owner's word (S6-B3415, L857 (c)). MEASURED at
    B3139q-r186: 7 of 17 battery families CERTIFIED, 10 NOT (8 on borrow_ok,
    1 also on the VIX bands, 4 checked by spot_check_replay, which re-derives
    no input family). Unmeasurable -> WARN with why, never a silent pass."""
    try:
        import verify_spotcheck_coverage as _vsc
        can = _vsc.checker_verifies(checker_script)
        fams, gaps = _vsc.audit(strategy, can)
    except (Exception, SystemExit) as exc:            # noqa: BLE001
        return ("WARN", f"coverage NOT MEASURABLE ({type(exc).__name__}: {exc})"[:200])
    if not gaps:
        return ("PASS", f"CERTIFIED: every input family the strategy reads "
                        f"({sorted(fams)}) is re-derived by {checker_script}")
    return ("WARN", "NOT CERTIFIED for " + "; ".join(
        f"{g} {fams[g][:4]}" for g in gaps)
        + f" - {checker_script} re-derives "
        + (", ".join(sorted(can)) if can else "no input family")
        + " (whether this holds step 4 open: S6-B3415)")


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


def _evidence_cut(ev, cap: int = 60) -> str:
    """S6-B3187 (L580): one check's value inside the packed step-1 string.

    The 60-character budget is KEPT: ledger_contradictions reads this
    string for non-execution phrases, so a longer value could expose one
    the cut hides today - widening is a behaviour change, not a display
    fix. What changes is HOW it cuts: on a word boundary when one sits in
    the last third, and always with a visible ' ...', so a cut value can
    no longer read as complete. MEASURED before the change, in a landed
    cube's evidence: 'Step-1: manifest window.end 2025-05-05 <= HO_START
    2025-05-0' - a mid-token cut that printed a wrong date."""
    ev = str(ev)
    if len(ev) <= cap:
        return ev
    head = ev[:cap]
    sp = head.rfind(" ")
    if sp >= (cap * 2) // 3:
        head = head[:sp]
    return head.rstrip() + " ..."


def ledger_contradictions(ledger: dict) -> list[str]:
    return [f"{c}/{n}" for c, steps in ledger.items()
            if isinstance(steps, dict) for n, v in steps.items()
            if isinstance(v, dict) and v.get("status") == "DONE"
            and asserts_non_execution(_current_claim(_old_evidence(v)))]


def _main_unguarded() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube", required=True)
    ap.add_argument("--step1-cube", action="store_true")
    ap.add_argument("--step2-cube", action="store_true")
    ap.add_argument("--write-ledger", action="store_true")
    # S6-B2924: grade a DECLARED RIDER as its own leg. Absent from every
    # automatic path - the engine landing hook passes no such flag - so
    # the default behaviour of every landing is unchanged. With it, the
    # rider is graded and written to its own per-leg key (S6-B2918), so
    # both legs of a pair land side by side instead of overwriting.
    ap.add_argument("--grade-rider", default=None,
                    help="grade this DECLARED rider as the leg; refused if it is not declared by the cube manifest")
    a = ap.parse_args()
    cube_dir = Path(a.cube)
    if not cube_dir.is_absolute():
        cube_dir = ROOT / a.cube
    manifest = read_manifest(cube_dir)
    step, step_basis = derive_step(manifest, step1_flag=a.step1_cube,
                                   step2_flag=a.step2_cube)
    try:
        results = checks(cube_dir, step1=(step == 1), graded_leg=a.grade_rider)
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

    # family dispatch - B2721: the MANIFEST's graded strategy decides. The
    # cube's strategy column is the wrong source for a rider cube (B2710):
    # it holds the whole consumer set, so a 22-strategy cube dispatched to
    # no family and five steps FAILed on a shape the design intends. The
    # cube column remains the fallback when the manifest declares nothing.
    strategies = cube_strategies(cube_dir)
    _graded_name, _declared_riders = graded_and_riders(cube_dir)
    fam_name = (_graded_name if (_graded_name and _declared_riders)
                else (strategies[0] if len(strategies) == 1 else None))
    # S6-B2924: an explicit rider becomes the graded leg. REFUSED unless
    # the manifest DECLARES it - grading an undeclared strategy would
    # record a verdict for a leg the cube never said was present, and
    # the absent case is the case the guard exists for (L642).
    if a.grade_rider:
        if a.grade_rider not in (_declared_riders or []):
            print(f"REFUSED: {a.grade_rider!r} is not a declared rider of "
                  f"{cube_dir.name} (declared: {sorted(_declared_riders or [])}) "
                  f"- refusing rather than grading an undeclared leg (S6-B2924)")
            return 2
        fam_name = a.grade_rider
    fam = FAMILIES.get(fam_name) if fam_name else None
    notes: dict = {}
    grid_out = spot_out = None
    fam_fail = None
    if fam is None:
        fam_fail = (f"no registered post-config family for strategies "
                    f"(graded={_graded_name!r}, riders={len(_declared_riders)}) "
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

    # S6-B3397: the graded leg's population, read ONCE for R6 (step 4) and
    # M12 (step 3); an unresolved leg counts as unknown and both fail closed.
    leg_all, leg_is = (leg_entry_counts(cube_dir, fam_name) if fam_name
                       else (None, None))
    # R6 (runbook 2.1, census line 663) on the artifact step 4 wrote - only
    # when step 4 itself succeeded, so a missing artifact keeps its own FAIL
    _n4 = notes.get("4_three_leg_spot_check")
    if spot_out is not None and spot_out.exists() and _n4 and _n4[0] == "DONE":
        _r6_ok, _r6_why = spot_sampling_check(spot_out, leg_all)
        results.append(("step4_sampling_contract", "PASS" if _r6_ok else "FAIL",
                        _r6_why))
        notes["4_three_leg_spot_check"] = (
            (_n4[0], f"{_n4[1]}; {_r6_why}") if _r6_ok else
            ("FAIL", f"R6 sampling contract broken: {_r6_why}"))
    # M12 (runbook 5.3 step 3, census line 1838): entries == grid max fires
    _m12 = entries_vs_grid_count(grid, leg_all, leg_is)
    results.append(("M12_entries_vs_grid_fires",) + _m12)

    # step 5 lenses -> artifact
    try:
        lens_rows = lenses(cube_dir, step, grid, spot_out, family=fam_name)
    except Exception as exc:
        lens_rows = [("lenses_crashed", "FAIL", repr(exc))]
    # S6-B2918: same per-leg key as the grid/spot/free artifacts.
    _lkey = artifact_key(cube_dir, fam_name, _declared_riders)
    lens_out = ROOT / "output_audit" / f"{_lkey}_lenses.json"
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
                    if st == "FAIL"
                    and n not in _GRADER_CHECKS + _LEDGER_WIDE + _STEP3_ONLY
                    and n != "family_dispatch"]
    summary = "; ".join(f"{n}={st}({_evidence_cut(ev)})" for n, st, ev in results)
    steps: dict[str, tuple[str, str]] = {}
    steps["1_cube_sanity"] = ("FAIL" if sanity_fails else "DONE",
                              "run_postconfig: " + summary)
    m_core = ("M2_exits_per_entry_vs_registry", "M3_fill_date", "M4_holdout_touch",
              "M5_pnl_integrity", "M7_degraded_exits", "M12_entries_vs_grid_fires")
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
        # tighten_breaker_block.main: carried = members of the RANKED
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
    # S6-B3397 (runbook 5.3 step 8, census 1956): the verdict also states X of
    # Y producers varied, exits_effective at the cube's SHA and every PASS
    # ci_lo; a verdict that cannot state them stays OPEN, never DONE
    _den, _den_err = "", None
    if grid:
        try:
            _den = "; " + verdict_denominators(cube_dir, manifest, fam_name, grid)
        except Exception as exc:                      # noqa: BLE001
            _den_err = f"{type(exc).__name__}: {exc}"[:200]
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
                    + verdict_from_grid(grid, step) + _den)
    elif grid and _den_err:
        steps["8_verdict_with_denominators"] = (
            "OPEN", f"the verdict cannot state its denominators (S6-B3397): "
                    f"{_den_err} - AUTO VERDICT (from {grid_out.name}): "
                    + verdict_from_grid(grid, step))
    elif grid:
        steps["8_verdict_with_denominators"] = (
            "DONE", f"AUTO (B2520) VERDICT (denominators from {grid_out.name}): "
                    + verdict_from_grid(grid, step) + _den)
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
            # S6-B2918: the ledger key is the artifact prefix, so it
            # carries the leg too - otherwise the second leg of a pair
            # merges into the first leg's row and a FAIL hides under DONE.
            _ekey = artifact_key(cube_dir, fam_name, _declared_riders)
            entry = ledger.get(_ekey) or {}
            for step_name, ev in auto_notes:
                entry = merge_row(entry, step_name, ev["status"], ev["evidence"], ts)
            ledger[_ekey] = entry
            return ledger
        locked_ledger_update(_upgrade)
        print(f"[OK] ledger: all {len(STEPS)} steps recorded for {cube_dir.name}"
              f" ({'FAIL present' if fails else 'no FAIL'})")
    return 2 if fails else 0


def main() -> int:
    """S6-B3156: a battery run by hand (the runbook's run_postconfig.py --cube
    form) refuses to start beside another battery on the SAME cube - two
    batteries race over its ledger rows and per-cube artifacts - and holds the
    in-flight marker while it runs. The supervisor (postconfig_landing.py)
    already holds both for the battery it starts and marks that child
    POSTCONFIG_SUPERVISED=1, so the child skips this. Exit 3 = refused."""
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--cube")
    known, _rest = pre.parse_known_args()
    if not known.cube or os.environ.get("POSTCONFIG_SUPERVISED") == "1":
        return _main_unguarded()
    cube_dir = Path(known.cube)
    if not cube_dir.is_absolute():
        cube_dir = ROOT / known.cube
    from verify_postconfig_complete import (battery_in_flight, claim_inflight,
                                            release_inflight)
    st = battery_in_flight(cube_dir, exclude=(os.getpid(), os.getppid()))
    if st["state"] in ("live", "unknown"):
        who = (f"pid(s) {', '.join(str(p) for p in st['pids'])}"
               if st["state"] == "live" else st["why"])
        print(f"REFUSED (S6-B3156): a post-config battery is "
              f"{'already running' if st['state'] == 'live' else 'possibly running'}"
              f" on {cube_dir.name} ({who}); a second battery on one cube races "
              "the first over its ledger rows and artifacts - wait for it to end.")
        return 3
    claim = claim_inflight(cube_dir, source="run_postconfig")
    try:
        return _main_unguarded()
    finally:
        release_inflight(cube_dir, claim)


if __name__ == "__main__":
    raise SystemExit(main())
