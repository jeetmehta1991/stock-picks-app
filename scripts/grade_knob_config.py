#!/usr/bin/env python
# Source: <cube>/{trade_log.csv,trade_exit_detail.csv,run_manifest.json} per CHECKLIST #77.
"""S6-B3248 / S6-B3304 (B3139q-r162): the Step-1 / Step-2 grader for ANY
SPECS family whose swept axes are PRODUCER env knobs - legs x exits on the
landed cube, at the knob vector the engine ran, verified against the cube's
own run manifest.

WHY ONE GRADER. The portability rule (#291, L754): a grader naming one
strategy is the first instance of a class, and the contract is extracted at
the SECOND family. Engine-knob families already carry six single-family
graders (candle, naked-POC, bollinger, institutional, pairs, LEVER4), and
squeeze_breakout and camarilla_r4_breakout are the next two. This grader
reads WHICH knobs exist from the registry - SPECS[<strategy>]['tools']['keys']
maps each param id to its arm key, and the param row names its env actuator -
so a family joins by registration, never by a copy.

WHAT IT REUSES (L799: inherit the code, not a copy of it): the frame is
smc_lsr_step1.build (the fail-closed path check, the per-fire dedup); the
cells are smc_family_step1.grade_cells (legs x exits, the one-episode
disclosure); the order is lever4_step1.rank (is_ci_lo first, never Sharpe);
the one Step-2 read is grade_npoc_config.grade_step2; the two legs of a
Step-2 verdict are step2_legs.cube_legs (S6-B3367).

THE KNOBS ARE VERIFIED, NOT MERELY STAMPED (the candle grader's rule,
S6-B2900): each flag is compared by VALUE with the landed arm's env for that
param's actuator; a missing manifest, a missing env block or a mismatch
REFUSES - grading on would file one cube under another config's name. The
R5 cube ran no arm: it is graded only at the production vector, and its
fires must reproduce the registered baseline.

LEGS: the union of the registry's per-param `legs` fields, else the
directions the cube's strategy rows carry. Each leg's fire count is written
beside the cells, so a leg that fired nothing shows as 0, never as absence.

Usage (the battery passes the flags from tools.grade.flags):
  python scripts/grade_knob_config.py --strategy squeeze_breakout \\
      --cube output_x --kc-mult 1.5 --bb-std 2.0 --mom-window 20 \\
      --kc-period 20 --prior-n 0 [--step2] [--preregistered-exit E] --out g.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import roster_core as rc  # noqa: E402

R5_DIR = ROOT / "output_r5_merged_1_7"


def knob_rows(strat: str) -> list:
    """[(param id, arm key, env, production)] for the family's registered
    knobs - SPECS tools.keys joined to each param row. Refuses a strategy
    with no SPECS entry, no tools.keys, or a keyed param with no env."""
    from producer_variant_table import SPECS
    entry = SPECS.get(strat)
    if entry is None:
        raise SystemExit(f"REFUSED: {strat!r} has no SPECS entry - register "
                         "it with a tools block first (fail closed, L642)")
    keys = dict((entry.get("tools") or {}).get("keys") or {})
    if not keys:
        raise SystemExit(f"REFUSED: SPECS[{strat!r}] declares no tools.keys - "
                         "this grader grades registered env knobs only")
    by_id = {p["id"]: p for p in entry.get("params") or []}
    out = []
    for pid, key in keys.items():
        row = by_id.get(pid)
        if row is None or not row.get("env"):
            raise SystemExit(f"REFUSED: tools.keys names {pid}, which is not a "
                             "param of the entry or has no env actuator")
        out.append((pid, key, row["env"], row.get("production")))
    # two params may share one actuator and one arm key (Camarilla's R4 and
    # S4 distance read CAM_R4_S4_DIST; bollinger's P3 and P4 read
    # STRAT_EMA_SPAN): the flag, the env check and the config entry are per
    # KEY, so the first param naming a key speaks for it
    seen, uniq = {}, []
    for pid, key, env, prod in out:
        if key in seen:
            if seen[key] != (env, str(prod)):
                raise SystemExit(f"REFUSED: arm key {key!r} maps to two actuators "
                                 f"or productions: {seen[key]} vs {(env, str(prod))}")
            continue
        seen[key] = (env, str(prod))
        uniq.append((pid, key, env, prod))
    return uniq


def legs_of(strat: str, m) -> tuple:
    """The registry's legs (the union of the params' `legs` fields), else
    the directions the cube's rows for the strategy carry."""
    from producer_variant_table import SPECS
    declared = set()
    for p in SPECS[strat].get("params") or []:
        declared |= set(p.get("legs") or [])
    if declared:
        return tuple(x for x in ("long", "short") if x in declared)
    return tuple(x for x in ("long", "short")
                 if x in set(m["direction"].astype(str)))


def _norm(v) -> str:
    """A value by VALUE, not spelling: '2', '2.0' and 2.0 are one level; ''
    and None are the unset level and never collapse into a number."""
    if v is None:
        return ""
    s = str(v).strip()
    if s == "":
        return ""
    try:
        return repr(round(float(s), 9))
    except (TypeError, ValueError):
        return s


def verify_manifest(cube_dir: Path, knobs: list, flags: dict) -> str:
    """'' when every flag equals the landed arm's env for its actuator; else
    the refusal. The stamp is a claim about WHICH cube this is."""
    mf = cube_dir / "run_manifest.json"
    if not mf.exists():
        return (f"REFUSED: no run_manifest.json in {cube_dir} - the knobs the "
                "engine read are unrecorded, so the flags verify nothing")
    try:
        man = json.loads(mf.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError) as exc:
        return f"REFUSED: run_manifest.json unreadable: {exc!r}"
    arms = man.get("arms") or []
    env = dict(((arms[0] or {}) if arms else {}).get("env") or {})
    if not env:
        return ("REFUSED: the landed arm declares no env block - the knobs "
                "the engine read are unrecorded (fail closed, L642)")
    bad = []
    for pid, key, envname, _prod in knobs:
        if envname not in env:
            bad.append(f"{envname} absent from the arm")
        elif _norm(env[envname]) != _norm(flags[key]):
            bad.append(f"{envname} landed {env[envname]!r}, the flag says "
                       f"{flags[key]!r}")
    if bad:
        return ("REFUSED: the flags do not match the landed arm - grading would "
                "file one cube under another config's name: " + "; ".join(bad))
    return ""


def _baseline_fires(strat: str) -> int:
    from producer_variant_table import SPECS
    b = SPECS[strat]["baseline"]
    return int(b.get("cube_fires", b["fires"]))


def main(argv=None) -> int:
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--strategy", required=True)
    known, _ = pre.parse_known_args(argv)
    knobs = knob_rows(known.strategy)
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--strategy", required=True)
    for _pid, key, envname, prod in knobs:
        ap.add_argument("--" + key.replace("_", "-"), dest=key, required=True,
                        help=f"the {envname} level the cube ran at "
                             f"(production {prod!r}) - identity, verified")
    ap.add_argument("--cube", default="",
                    help="cube DIRECTORY to grade; default the R5 baseline")
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--step2", action="store_true",
                    help="declare a Step-2 cube: one leg's holdout is read ONCE "
                         "on the exit its own in-sample selects")
    ap.add_argument("--step2-leg", default="long", choices=("long", "short"))
    ap.add_argument("--preregistered-exit", default=None,
                    help="the Step-1 pre-registered exit - recorded beside the "
                         "selection, never read (owner ruling 2(i))")
    ap.add_argument("--survival", action="store_true",
                    help="S6-B3322: on R5, read only the fires the CURRENT gate "
                         "keeps - required for a gate changed since R5, refused "
                         "on an engine cube (smc_lsr_step1.build)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    t0 = time.time()
    strat = a.strategy
    flags = {key: getattr(a, key) for _pid, key, _env, _prod in knobs}
    at_production = all(_norm(flags[key]) == _norm(prod)
                        for _pid, key, _env, prod in knobs)

    cube_dir = Path(a.cube).resolve() if a.cube else None
    if cube_dir is not None and cube_dir.is_file():
        cube_dir = cube_dir.parent
    is_r5 = cube_dir is None or cube_dir == R5_DIR.resolve()
    if is_r5:
        if not at_production:
            raise SystemExit("REFUSED: the R5 cube ran every knob at production, "
                             f"but the flags name {flags} (fail closed)")
        if a.step2:
            raise SystemExit("REFUSED: --step2 names the R5 cube - its holdout is "
                             "the production strategy's, not an arm's (fail closed)")
        check = "R5 baseline: no arm; graded at the production vector"
    else:
        why = verify_manifest(cube_dir, knobs, flags)
        if why:
            raise SystemExit(why)
        check = ("flags verified against arms[0].env: "
                 + " ".join(f"{e}={flags[k]!r}" for _p, k, e, _x in knobs))
    legs_rec = None
    if a.step2:
        import step2_legs
        legs_rec = step2_legs.cube_legs(cube_dir)
        lerrs = step2_legs.legs_refusals(legs_rec)
        if lerrs:
            raise SystemExit(f"{lerrs[0]} (S6-B3367: the breadth leg rides the "
                             "spec's arm - make_spec --breadth-leg)")

    from smc_lsr_step1 import build as _build
    from smc_family_step1 import grade_cells
    from lever4_step1 import rank
    m = _build(None if is_r5 else cube_dir, strat=strat, keys=[],
               survival=a.survival)
    fires = m.drop_duplicates(["ticker", "entry_date"])
    n_cube = int(m.attrs["fires_before_survival"])
    # NET, the battery family graders' basis (load_cube in grade_candle_config
    # and its siblings): the frame builder carries raw pnl, and grade_cells
    # scores whatever it is handed - so a grader that only delegates would be
    # a raw scorer the B3122 census cannot see. One definition (#271).
    m["pnl_pct"] = rc.net_pnl(m["pnl_pct"].astype(float))
    if is_r5:
        want = _baseline_fires(strat)
        if n_cube != want:
            raise SystemExit(f"REFUSED: {n_cube} unique fires != the registered "
                             f"R5 baseline {want} (fail closed)")
        repro = (f"R5 BASELINE reproduction OK: {n_cube} fires == {want}"
                 + (f"; the current gate keeps {len(fires)} (S6-B3322 survival)"
                    if a.survival else ""))
    else:
        repro = (f"VARIANT-CUBE-NO-R5-REPRODUCTION: produced at "
                 + " ".join(f"{k}={flags[k]!r}" for _p, k, _e, _x in knobs)
                 + f"; own fires {len(fires)}")
    legs = legs_of(strat, m)
    leg_fires = {leg: int((fires["direction"] == leg).sum()) for leg in legs}
    print(f"{repro}; legs {leg_fires} ({time.time() - t0:.0f}s)")

    rows = grade_cells(m, strat, a.min_n, legs=legs)
    graded = [r for r in rows if r["is_sharpe"] is not None]
    ranked = rank(graded)
    print(f"{len(graded)} graded cells of {len(rows)}")
    rec = {"strategy": strat,
           "generator": "scripts/grade_knob_config.py",
           "cube": str(cube_dir) if cube_dir else str(R5_DIR),
           "config": {f"{pid}_{key}": flags[key] for pid, key, _e, _x in knobs},
           "manifest_check": check,
           "basis": ("net: pnl_pct clipped to +/-WINSORIZE then minus "
                     "COST_BPS/100 - roster_core.net_pnl"),
           "reproduction": repro,
           "reproduction_fires": n_cube,
           "legs": list(legs), "leg_fires": leg_fires,
           "design": ("base cell per leg x exits, IS-only; npt barred; ranked on "
                      "is_ci_lo; the knobs are the cube's identity, verified "
                      "against its manifest - one combination per cube"),
           "cells_graded": len(graded),
           "multiplicity": rc.bh_fdr_report(rows),
           "step1_ranking": ranked[:80], "rows": rows,
           "holdout_read": "NOT FIRED - Step 2 needs its own owner word (11.2c)"}
    if a.step2:
        from grade_npoc_config import grade_step2 as _grade_step2
        import step2_legs
        leg = m[m.direction == a.step2_leg]
        s2 = _grade_step2(leg, rc.holdout(leg), min_n=a.min_n,
                          declared_step2=True,
                          preregistered_exit=a.preregistered_exit)
        s2["leg"] = a.step2_leg
        s2["legs"] = legs_rec
        s2["disposition"] = step2_legs.disposition(s2.get("verdict") == "FAIL", legs_rec)
        rec["step2"] = s2
        rec["holdout_read"] = (
            f"FIRED ONCE: {s2['verdict']} on the {a.step2_leg} leg's "
            f"{s2.get('selected_exit')}" if s2.get("holdout_read") else
            f"DECLARED STEP 2, NOT READ: {s2['verdict']} - {s2.get('reason')}")
        print(f"[STEP-2] {s2['verdict']}: {a.step2_leg} leg, exit "
              f"{s2.get('selected_exit')}, holdout_n {s2.get('holdout_n')}")
    from roster_core import stamp_metric_code as _smc
    _smc(rec)
    Path(a.out).write_text(json.dumps(rec, indent=2, default=float), encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
