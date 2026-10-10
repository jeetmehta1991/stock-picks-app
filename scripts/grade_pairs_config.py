"""S6-B3140: Step-1/Step-2 grader for the pairs_mean_reversion_long cubes.

WHY IT EXISTS. The owner opened the W-T tighten campaign (verbatim 2026-10-07
"pairs_mean_reversion_long lets proceed. Check table A and display it.") and
launched Step 1 (verbatim 2026-10-08 "proceed with step 1"); launch_refusals
and run_postconfig.family_refusal fail CLOSED without a complete battery
adapter (S6-B2573b), so a landing would otherwise FAIL after the engine
spend. This is the family's grade leg.

MODELLED ON grade_bollinger_config.py (S6-B3119), itself the L754 extraction
of grade_candle_config.py (S6-B2900) - EVERY statistic is a roster_core
delegation, so the pairs cubes are graded by the same code as every admitted
strategy. The council-driven rules carry over:

 1. THE GRADED STRATEGY COMES FROM THE MANIFEST (run_postconfig.
    graded_and_riders), with the cube as the pre-B2721 one-strategy fallback;
    the cube is FILTERED to the graded strategy before any statistic runs.
    This family registers pairs_mean_reversion_long only (LONG leg only -
    the B2085/F24 owner re-scope: EXPLORATORY, the hedge leg does not exist
    in Stage 2, no deployment before Stage 3; an admitted line is a BANKED
    measurement with the tag riding, per the B2668 precedent).
 2. THE ARM IS VERIFIED AGAINST THE MANIFEST, NOT MERELY STAMPED. This
    family has ZERO engine knobs (every campaign axis is OFFLINE - the three
    gate thresholds grade from persisted signals; the producer knobs are
    DEFINED-NO-ACTUATOR). The verification is therefore that the landed
    arm's `env` block is EMPTY: an env key present would mean the engine ran
    something this registry does not describe, and the cube would be graded
    under a label Table A does not carry (fail closed, L642).

ONE COMBINATION PER CUBE: production is the only runnable configuration.
Within one config the exit family IS reported via the report-only
multiplicity block (roster_core.bh_fdr_report over exit_family_rows). The
125 offline level-combinations are graded by the free-levels leg
(grade_free_levels_pairs.py), never here.

Usage:
  python scripts/grade_pairs_config.py --cube output_b3140_pairs \\
      [--step2] [--preregistered-exit time_stop_10d] --out <grid.json>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roster_core as rc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# adapter-dispatched family leg: no module-level STRAT constant
# (test_b3120d ratchet; the candle-grader shape)
PAIRS_LONG = "pairs_mean_reversion_long"
FAMILY = (PAIRS_LONG,)


# S6-B3141a: the two producer knobs (P5 / P6) and their registered bands.
# An arm env may carry ONLY these keys, at band values; an absent key means
# the production value (an EMPTY env is config 1, the production cube).
KNOBS = {"PAIRS_EG_SIGNIFICANCE": ("P5_eg_significance", float, (0.01, 0.05), 0.05),
         "PAIRS_Z_WINDOW": ("P6_z_window", int, (40, 60, 90), 60)}


def arm_knobs(env: dict) -> tuple[dict | None, str]:
    """({config key: value} or None, refusal) for an arm's env block."""
    extra = sorted(set(env) - set(KNOBS))
    if extra:
        return None, (f"[FAIL] the landed arm declares env keys {extra} that "
                      "this family does not register (S6-B3141a registers "
                      f"{sorted(KNOBS)}) - fail closed, L642")
    out = {}
    for envk, (cfgk, typ, band, prod) in KNOBS.items():
        raw = env.get(envk)
        val = prod if raw is None else typ(raw)
        if val not in band:
            return None, (f"[FAIL] {envk}={raw!r} is not a registered band "
                          f"level {list(band)} (S6-B3141a) - fail closed")
        out[cfgk] = val
    return out, ""


def verify_manifest(cube_dir: Path, expect: dict | None = None
                    ) -> tuple[str | None, str]:
    """(refusal or None, disclosure). The landed arm's env may carry only
    the two registered producer knobs at band values (S6-B3141a; an EMPTY
    env is the production config); `expect` - the knob values the battery
    passed by flag - must equal what the arm ran."""
    mf = cube_dir / "run_manifest.json"
    if not mf.exists():
        return (f"[FAIL] no run_manifest.json in {cube_dir} - the arm cannot "
                "be verified as the production config (S6-B3140)"), ""
    try:
        man = json.loads(mf.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError) as exc:
        return f"[FAIL] run_manifest.json unreadable: {exc!r}", ""
    arms = man.get("arms") or []
    arm = (arms[0] or {}) if arms else {}
    env = dict(arm.get("env") or {})
    knobs, why = arm_knobs(env)
    if knobs is None:
        return why, ""
    if expect is not None and any(expect[k] != knobs[k] for k in expect):
        return (f"[FAIL] the battery passed {expect} but the landed arm ran "
                f"{knobs} - the cube would be graded under the wrong label "
                "(fail closed, L642)"), ""
    return None, ("arms[0].env verified against the registered pairs knobs: "
                  + " ".join(f"{k}={v}" for k, v in knobs.items())
                  + (" (EMPTY env = the production config)" if not env else ""))


def resolve_strategy(cube, cube_dir: Path) -> tuple[str, list]:
    """(graded strategy, declared riders) - the B2721 rule, ported."""
    graded, riders = None, []
    try:
        import run_postconfig as rp
        graded, riders = rp.graded_and_riders(cube_dir)
    except Exception:                               # noqa: BLE001
        graded, riders = None, []
    present = sorted(set(cube["strategy"].astype(str).unique()))
    if graded:
        if graded not in FAMILY:
            raise SystemExit(
                f"[FAIL] the manifest grades {graded!r}, which is not one of "
                f"{list(FAMILY)} - this grader is registered for the "
                "pairs_mean_reversion_long family only (fail closed, L642)")
        if graded not in present:
            raise SystemExit(
                f"[FAIL] the manifest grades {graded!r} but the cube carries "
                f"no such rows; it holds {present}")
        return graded, list(riders)
    fam = [s for s in present if s in FAMILY]
    if len(fam) != 1 or len(present) != 1:
        raise SystemExit(
            f"[FAIL] the manifest declares no strategy_subset and the cube "
            f"carries {present}; with nothing declared this grader requires "
            f"exactly one of {list(FAMILY)} (fail closed, L642)")
    return fam[0], []


def grade_step2(cube, ho_rows, *, min_n: int, declared_step2: bool,
                preregistered_exit: str | None = None) -> dict:
    """The ONE holdout read of a Step-2 cube - byte-for-byte the bollinger
    grader's leg (owner ruling 2(i) 2026-09-05; S6-B2409 gates rule)."""
    out = {"holdout_read": False, "holdout_rows": int(len(ho_rows)),
           "selected_exit": None, "selection": None,
           "preregistered_exit": preregistered_exit, "mismatch": None,
           "gates": None, "verdict": None,
           "rule": ("S6-B2409: PASS = all six LIVE_GATES clear on the holdout "
                    "of the IS-selected exit; FAIL otherwise; margin is a "
                    "number, not a gate")}
    if not declared_step2:
        out["verdict"] = "NOT_GRADED"
        out["reason"] = ("cube not declared Step-2 (--step2 absent) - the "
                         f"holdout ({len(ho_rows)} rows) is not read")
        return out
    if not len(ho_rows):
        out["verdict"] = "NO_HOLDOUT_ROWS"
        out["reason"] = ("declared Step-2 but the cube has no rows in "
                         f"[{rc.HO_START}, {rc.HO_END})")
        return out
    out["holdout_read"] = True
    exit_pick, is_stats = rc.select_exit(cube, objective="gates", min_n=min_n)
    out["selection"] = (f"rc.select_exit(objective='gates', min_n={min_n}) on "
                        "IS rows only - key (n_gates, sharpe); byte-identical "
                        "exits collapsed (S6-B2216), next_pivot_target refused "
                        "for NPT-spanning cells (B2014/D7)")
    out["selected_exit"] = exit_pick
    out["is_stats"] = None if not is_stats else {
        k: is_stats.get(k) for k in ("n", "sharpe", "ci_lo", "n_gates",
                                     "exits_effective", "exits_collapsed",
                                     "npt_excluded_identity_boundary")}
    if preregistered_exit is not None:
        out["mismatch"] = (exit_pick != preregistered_exit)
        if out["mismatch"]:
            out["mismatch_disclosure"] = (
                f"the Step-1 pre-registered exit {preregistered_exit!r} is NOT "
                f"the exit this cube's own IS selected ({exit_pick!r}); the "
                "admission verdict is on the selected exit - one read, no "
                "re-roll (owner ruling 2(i) 2026-09-05)")
    if exit_pick is None:
        out["verdict"] = "NO_EXIT_SELECTABLE"
        out["reason"] = f"no exit cleared min_n={min_n} on the IS rows"
        return out
    hb = ho_rows[ho_rows.exit_method == exit_pick]
    fp_n = int((cube.exit_method == exit_pick).sum())
    out["holdout_n"] = int(len(hb))
    out["full_period_n"] = fp_n
    res = rc.evaluate(hb["pnl_pct"], hb["hold_days"], min_n=min_n,
                      full_period_n=fp_n)
    if res is None:
        out["verdict"] = "BELOW_POWER_FLOOR"
        out["reason"] = (f"holdout n {len(hb)} < min_n {min_n} on "
                         f"{exit_pick!r} - the gates were not evaluable")
        return out
    gates = {k: bool(res["gates"][k]) for k in rc.LIVE_GATES}
    out.update({k: res.get(k) for k in
                ("sharpe", "sortino", "psr", "profit_factor", "payoff",
                 "expectancy", "win_rate", "p", "ci_lo")})
    out["gates"] = gates
    out["gates_passed"] = int(sum(gates.values()))
    out["verdict"] = "PASS" if all(gates.values()) else "FAIL"
    if out["verdict"] == "PASS":
        out["margin"] = rc.qualifier_margin(res.get("sharpe"))
    return out


def grade(cube_csv: Path, config: dict, *, min_n: int = 10, top_n: int = 10,
          note: str = "", step2: bool = False, disclosure: str = "",
          preregistered_exit: str | None = None) -> dict:
    full = rc.load_cube(cube_csv, chunksize=500_000)
    strat, riders = resolve_strategy(full, cube_csv.parent)
    cube = full[full["strategy"].astype(str) == strat]
    is_rows, ho_rows = rc.in_sample(cube), rc.holdout(cube)
    ho_n = ho_rows.groupby("exit_method", observed=True).size()
    full_n = cube.groupby("exit_method", observed=True).size()

    per_exit = []
    for ex, g in is_rows.groupby("exit_method", observed=True):
        stats = rc.evaluate(g["pnl_pct"], g["hold_days"], min_n=1)
        if stats is None:
            continue
        sh, cl = stats.get("sharpe"), stats.get("ci_lo")
        per_exit.append({
            "exit": str(ex), "fires": int(len(g)),
            "is_sharpe": None if sh is None else round(float(sh), 3),
            "is_ci_lo": None if cl is None else round(float(cl), 3),
            "class_size": 1,
            "admit": {"holdout_n": int(ho_n.get(ex, 0)),
                      "full_period_n": int(full_n.get(ex, 0)),
                      "verdict": ("RANKED" if len(g) >= min_n
                                  else "BELOW_POWER_FLOOR")}})
    per_exit.sort(key=lambda r: (-(r["is_ci_lo"] if r["is_ci_lo"] is not None
                                   else -9e9), -r["fires"]))
    ranked = [r for r in per_exit if r["admit"]["verdict"] == "RANKED"]
    for i, r in enumerate(ranked, 1):
        r["rank"] = i
    combo_verdict = "RANKED" if ranked else "NO_EXIT_SELECTABLE"
    return {
        "config": dict(config), "strategy": strat,
        "cube_riders": list(riders),
        "grader": "scripts/grade_pairs_config.py (S6-B3140)",
        "cube": str(cube_csv).replace("\\", "/"),
        "manifest_check": disclosure or "NOT RUN (--no-manifest-check)",
        "note": note or ("S6-B3140: Step-1 ranking via roster_core.evaluate "
                         "per exit on the IS rows - the SAME code every "
                         "admitted strategy was graded by; is_ci_lo is the "
                         "ranking key, not a gate (B1608); the holdout is "
                         "counted and read only under --step2. EXPLORATORY "
                         "registration rides (B2085/F24): any verdict is a "
                         "banked measurement, never a deployment."),
        "window": {"is": [str(rc.IS_START), str(rc.IS_END)],
                   "holdout": [str(rc.HO_START), str(rc.HO_END)],
                   "cube_entry_min": str(min(cube["entry_date"])),
                   "cube_entry_max": str(max(cube["entry_date"]))},
        "rows": int(len(cube)), "rows_all_strategies": int(len(full)),
        "is_rows": int(len(is_rows)),
        "holdout_rows": int(len(ho_rows)), "min_n": min_n,
        "results": [{"combo": dict(config), "verdict": combo_verdict,
                     "n_exits_graded": len(per_exit),
                     "n_exits_ranked": len(ranked)}],
        "step1_combinations_carried": 1,
        "step1_distinct_outcomes": 1,
        "step1_ranking": ranked[:top_n],
        "multiplicity": rc.bh_fdr_report(rc.exit_family_rows(
            per_exit, cube["exit_method"].astype(str).unique())),
        "per_exit": per_exit,
        "results_n_exits": len(per_exit),
        "step2": grade_step2(cube, ho_rows, min_n=min_n, declared_step2=step2,
                             preregistered_exit=preregistered_exit),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cube", required=True,
                    help="cube dir (or its trade_exit_detail.csv)")
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--top-n", type=int, default=10)
    ap.add_argument("--note", default="")
    ap.add_argument("--step2", action="store_true",
                    help="declare a Step-2 cube - the holdout is read ONCE on "
                         "the IS-selected exit and the six LIVE_GATES decide")
    ap.add_argument("--preregistered-exit", default=None)
    ap.add_argument("--no-manifest-check", action="store_true",
                    help="grade a cube with no landed arm (a hand-built "
                         "subset). The artifact records that the arm was "
                         "NOT verified - never pass this at landing.")
    ap.add_argument("--eg-significance", type=float, default=None,
                    help="P5 knob value the battery read from the manifest")
    ap.add_argument("--z-window", type=int, default=None,
                    help="P6 knob value the battery read from the manifest")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    cube_dir = Path(a.cube)
    cube = cube_dir / "trade_exit_detail.csv" if cube_dir.is_dir() else cube_dir
    if not cube.exists():
        print(f"[FAIL] no cube at {cube}")
        return 2
    expect = {}
    if a.eg_significance is not None:
        expect["P5_eg_significance"] = a.eg_significance
    if a.z_window is not None:
        expect["P6_z_window"] = a.z_window
    knobs = {"P5_eg_significance": expect.get("P5_eg_significance", 0.05),
             "P6_z_window": expect.get("P6_z_window", 60)}
    ident = ("production" if knobs == {"P5_eg_significance": 0.05,
                                        "P6_z_window": 60}
             else f"eg{knobs['P5_eg_significance']}_zw{knobs['P6_z_window']}")
    config = {"P1_pairs_identity": ident, **knobs}
    if a.no_manifest_check:
        disclosure = ("NOT VERIFIED (--no-manifest-check): the knob "
                      "labels are an UNCHECKED stamp on this artifact")
    else:
        refusal, disclosure = verify_manifest(cube.parent, expect or None)
        if refusal:
            print(refusal)
            return 2

    doc = grade(cube, config, min_n=a.min_n, top_n=a.top_n, note=a.note,
                step2=a.step2, disclosure=disclosure,
                preregistered_exit=a.preregistered_exit)
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube.parent.name}_grid_auto.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    from roster_core import stamp_metric_code as _smc  # S6-B3139i
    _smc(doc)
    out.write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")
    top = doc["step1_ranking"][0] if doc["step1_ranking"] else None
    print(f"graded {doc['strategy']}: {doc['results_n_exits']} exits on "
          f"{doc['is_rows']} IS rows ({doc['rows']} strategy rows of "
          f"{doc['rows_all_strategies']} in cube, holdout rows "
          f"{doc['holdout_rows']}); "
          + (f"best {top['exit']} is_ci_lo {top['is_ci_lo']} is_sharpe "
             f"{top['is_sharpe']} fires {top['fires']}" if top
             else "NO exit cleared the power floor"))
    s2 = doc["step2"]
    if s2.get("holdout_read"):
        print(f"[STEP-2] {s2['verdict']}: exit {s2['selected_exit']} holdout_n "
              f"{s2.get('holdout_n')} full_period_n {s2.get('full_period_n')} "
              f"sharpe {s2.get('sharpe')} gates {s2.get('gates')}")
    else:
        print(f"[STEP-2] {s2['verdict']}: {s2.get('reason')}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
