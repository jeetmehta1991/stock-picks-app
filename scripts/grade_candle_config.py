"""S6-B2900: Step-1/Step-2 grader for the candle anatomy configs.

WHY IT EXISTS. `run_postconfig.family_refusal` reported exactly one remaining
gap for the candle pair after B2899 wired the spot_check leg, verbatim:
"`tools.grade` lacks ['cube']". That is NOT a missing string - it is a missing
grader. THE SIX DEFECTS of the incumbent `offline_level_sweep.py`, written out
because "unusable on six counts" with no contents is a preference, not a
finding (council Outsider, 2026-09-20):

  1. it has no `--cube` flag at all, so the battery's invocation cannot reach
     it;
  2. `--band-ruling` is REQUIRED, and the battery passes no such flag;
  3. its `_flag_args` emits one unsubstituted argv token;
  4. `--production` parses as a float, but the candle wick level at its
     no-bound end is the EMPTY STRING - which is not 0.0, since 0.0 means
     "refuse any bar carrying any wick at all";
  5. `require_fresh_status()` demands the status stamp equal git HEAD, which
     no landing can guarantee;
  6. it is IN-SAMPLE by construction, so it can never produce the Step-2 gate
     verdict the battery fails closed without.
  And beyond the six: it pins CUBE and TRADE_LOG to `output_r5_merged_1_7` as
  MODULE CONSTANTS, so wiring it would grade the WRONG cube while faithfully
  stamping whichever flags it was handed.

MODELLED ON grade_institutional_config.py (B2520/B2612), the sibling with the
same `cube: ""` shape, and it reuses roster_core for EVERY statistic - MEASURED
at B2900: zero self-computed statistics here, 12 delegations - so the candle
pair is graded by the same code as every admitted strategy. A grader with its
own arithmetic would make its numbers incomparable with the roster.

THREE DELIBERATE DIFFERENCES from that sibling, each council-driven:

 1. THE GRADED STRATEGY COMES FROM THE MANIFEST, NOT FROM COUNTING THE CUBE.
    The sibling pins one STRAT and refuses a cube carrying anything else. That
    rule would refuse the candle campaign's own shape: a long/short PAIR run in
    one engine pass puts BOTH legs in one cube, and B2710/B2721 already
    established that a cube legitimately carries a graded strategy PLUS
    declared riders. So `resolve_strategy` asks `run_postconfig.
    graded_and_riders`, which reads `strategy_subset` - the same source the
    battery's own integrity check uses - and falls back to the cube only when
    the manifest declares nothing (the pre-B2721 one-strategy rule, L642).
    The cube is then FILTERED to the graded strategy before any statistic runs.

 2. THE KNOBS ARE VERIFIED AGAINST THE MANIFEST, NOT MERELY STAMPED. The
    sibling REFUSES non-production values because its two flags are artifact
    stamps its grade() never reads (L751). The candle knobs are different in
    kind: the ENGINE consumed them, so a cube IS one combination and any value
    is legitimate - which makes the stamp A CLAIM ABOUT WHICH CUBE THIS IS, and
    an unverified stamp is precisely how the incumbent would have graded
    output_r5_merged_1_7 under a candle config's name. Mismatch is REFUSED. A
    manifest with no env block is also refused: MEASURED, 0 of 70 existing
    run_manifest.json files carry a candle cube, so fail-closed here refuses
    nothing that exists.

 3. `--max-wick-pct` IS REQUIRED. Defaulting it meant a FORGOTTEN flag silently
    selected "unbounded" - the three-state trap (absent / empty / zero) the
    council Outsider named, and defect 4 above in a new costume. Required, the
    only way to say unbounded is to say it explicitly.

ONE COMBINATION PER CUBE: the four knobs were read by the engine, so the funnel
has a single row and equivalence collapse needs >= 2 combinations. Cross-config
multiplicity across the 54-config campaign is NOT handled here and is tracked
separately - every config writes its own grid carrying its own `config` block,
so the campaign-level deflation is computable post-hoc by globbing them.
WITHIN one config the exit family IS reported (B3101, S6-B3096f): every grid
carries the report-only `multiplicity` block over the exits searched
(roster_core.exit_family_rows), which breadth_step2_read requires.

Usage:
  python scripts/grade_candle_config.py --cube output_candle_cfg01 \\
      --n-bars 3 --min-body-pct 0.0 --min-step-pct 0.0 --max-wick-pct '' \\
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

BULLISH = "three_white_soldiers"
BEARISH = "three_black_crows_short"
FAMILY = (BULLISH, BEARISH)

# the launcher's contract: one env knob per swept axis (B2865). MEASURED at
# B2900 - arm env values serialise as STRINGS ("5", "200"), so the no-bound
# wick level arrives as "" and the comparison below is by VALUE, not spelling.
ENV_OF = {"n_bars": "CANDLE_N_BARS", "min_body_pct": "CANDLE_MIN_BODY_PCT",
          "min_step_pct": "CANDLE_MIN_STEP_PCT",
          "max_wick_pct": "CANDLE_MAX_WICK_PCT"}


def _norm(v) -> str:
    """Compare a manifest stamp to a CLI value by VALUE, not by spelling.

    '0.0', '0' and 0.0 are one level. '' and None are the NO-BOUND level and
    must NOT collapse into 0.0, which is the OPPOSITE bound - a zero wick
    ceiling refuses every bar carrying any wick at all."""
    if v is None:
        return ""
    s = str(v).strip()
    if s == "":
        return ""
    try:
        return repr(round(float(s), 9))
    except (TypeError, ValueError):
        return s


def verify_manifest(cube_dir: Path, flags: dict) -> tuple[str | None, str]:
    """(refusal or None, disclosure).

    The stamp is a claim about WHICH cube this is; an unverified one is how a
    module-constant grader grades the wrong artifact under the right name."""
    mf = cube_dir / "run_manifest.json"
    if not mf.exists():
        return (f"[FAIL] no run_manifest.json in {cube_dir} - the flags cannot "
                "be verified against what the engine actually read, and an "
                "unverified stamp is a claim (S6-B2900)"), ""
    try:
        man = json.loads(mf.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError) as exc:
        return f"[FAIL] run_manifest.json unreadable: {exc!r}", ""
    arms = man.get("arms") or []
    arm = (arms[0] or {}) if arms else {}
    env = dict(arm.get("env") or {})
    if not env:
        return ("[FAIL] the landed arm declares no `env` block, so the four "
                "CANDLE_* knobs the engine read are unrecorded and these flags "
                "verify nothing. MEASURED at B2900: 0 of 70 existing "
                "run_manifest.json files carry a candle cube, so this refuses "
                "nothing that exists (fail closed, L642)"), ""
    bad = []
    for key, envname in ENV_OF.items():
        if envname not in env:
            bad.append(f"{envname} absent from the arm")
        elif _norm(env[envname]) != _norm(flags[key]):
            bad.append(f"{envname} landed {env[envname]!r} but the flag says "
                       f"{flags[key]!r}")
    if bad:
        return ("[FAIL] the flags do not match the landed arm - grading this "
                "would file one cube under another config's name: "
                + "; ".join(bad)), ""
    return None, ("flags verified against arms[0].env: "
                  + " ".join(f"{e}={env[e]!r}" for e in ENV_OF.values()))


def resolve_strategy(cube, cube_dir: Path) -> tuple[str, list]:
    """(graded strategy, declared riders).

    B2721: the battery grades the manifest's `strategy_subset`, and a cube may
    legitimately carry declared RIDERS beside it - which a long/short pair run
    in one engine pass always will. Counting distinct strategies would refuse
    that shape, so the manifest is asked first and the cube is the fallback."""
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
                f"{list(FAMILY)} - this grader is registered for the candle "
                "family only (fail closed, L642)")
        if graded not in present:
            raise SystemExit(
                f"[FAIL] the manifest grades {graded!r} but the cube carries "
                f"no such rows; it holds {present}")
        return graded, list(riders)
    # no manifest declaration -> the pre-B2721 one-strategy rule stands
    fam = [s for s in present if s in FAMILY]
    if len(fam) != 1 or len(present) != 1:
        raise SystemExit(
            f"[FAIL] the manifest declares no strategy_subset and the cube "
            f"carries {present}; with nothing declared this grader requires "
            f"exactly one of {list(FAMILY)} (fail closed, L642)")
    return fam[0], []


def grade_step2(cube, ho_rows, *, min_n: int, declared_step2: bool,
                preregistered_exit: str | None = None) -> dict:
    """The ONE holdout read of a Step-2 cube (owner ruling 2(i) 2026-09-05).

    Identical in intent to the institutional grader's leg: the exit is chosen
    on IN-SAMPLE rows alone by rc.select_exit, that exit's holdout rows are
    evaluated once with full_period_n so min_trades_full_period is a real gate,
    and the six LIVE_GATES decide. ALWAYS returns `holdout_read` and `gates` so
    run_postconfig.grid_step2_graded can fail closed (B2612/L642)."""
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
                         f"holdout ({len(ho_rows)} rows) is not read; a Step-1 "
                         "cube with holdout rows is M4_holdout_touch's finding")
        return out
    if not len(ho_rows):
        out["verdict"] = "NO_HOLDOUT_ROWS"
        out["reason"] = ("declared Step-2 but the cube has no rows in "
                         f"[{rc.HO_START}, {rc.HO_END}) - nothing to admit on")
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
                "admission verdict is on the selected exit, the pre-registered "
                "exit is recorded here and NOT evaluated on the holdout - one "
                "read, no re-roll (owner ruling 2(i) 2026-09-05)")
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
    # B2721: grade the DECLARED strategy only - riders ride, they are not graded
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
        "grader": "scripts/grade_candle_config.py (S6-B2900)",
        "cube": str(cube_csv).replace("\\", "/"),
        "manifest_check": disclosure or "NOT RUN (--no-manifest-check)",
        "note": note or ("S6-B2900: Step-1 ranking via roster_core.evaluate "
                         "per exit on the IS rows - the SAME code every "
                         "admitted strategy was graded by; is_ci_lo is the "
                         "ranking key, not a gate (B1608); the holdout is "
                         "counted and read only under --step2."),
        "window": {"is": [str(rc.IS_START), str(rc.IS_END)],
                   "holdout": [str(rc.HO_START), str(rc.HO_END)],
                   "cube_entry_min": str(min(cube["entry_date"])),
                   "cube_entry_max": str(max(cube["entry_date"]))},
        "rows": int(len(cube)), "rows_all_strategies": int(len(full)),
        "is_rows": int(len(is_rows)),
        "holdout_rows": int(len(ho_rows)), "min_n": min_n,
        # ONE combination per cube: the four knobs were read by the ENGINE.
        "results": [{"combo": dict(config), "verdict": combo_verdict,
                     "n_exits_graded": len(per_exit),
                     "n_exits_ranked": len(ranked)}],
        "step1_combinations_carried": 1,
        "step1_distinct_outcomes": 1,
        "step1_ranking": ranked[:top_n],
        # S6-B3096f (B3101): the report-only multiplicity block S6-B2766 made
        # mandatory - every exit SEARCHED in this cube, partitioned (a zero-trade
        # exit stays in the denominator). Scope: one config's exits; the
        # campaign-level family (configs x exits) is not priced here. No
        # ranking or verdict reads it (B1608).
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
    ap.add_argument("--n-bars", type=int, required=True)
    ap.add_argument("--min-body-pct", type=float, required=True)
    ap.add_argument("--min-step-pct", type=float, required=True)
    ap.add_argument("--max-wick-pct", required=True,
                    help="REQUIRED. The empty string is the NO-BOUND level, "
                         "which is NOT 0.0 (0.0 refuses any bar with a wick). "
                         "Required so a forgotten flag cannot silently mean "
                         "unbounded (S6-B2900).")
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--top-n", type=int, default=10)
    ap.add_argument("--note", default="")
    ap.add_argument("--step2", action="store_true",
                    help="declare a Step-2 cube - the holdout is read ONCE on "
                         "the IS-selected exit and the six LIVE_GATES decide")
    ap.add_argument("--preregistered-exit", default=None)
    ap.add_argument("--no-manifest-check", action="store_true",
                    help="grade a cube with no landed arm (a hand-built "
                         "subset). The artifact records that the stamp was "
                         "NOT verified - never pass this at landing.")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    cube_dir = Path(a.cube)
    cube = cube_dir / "trade_exit_detail.csv" if cube_dir.is_dir() else cube_dir
    if not cube.exists():
        print(f"[FAIL] no cube at {cube}")
        return 2
    config = {"P2_n_bars": a.n_bars, "P3_min_body_pct": a.min_body_pct,
              "P4_min_step_pct": a.min_step_pct,
              "P5_max_wick_pct": (None if str(a.max_wick_pct).strip() == ""
                                  else float(a.max_wick_pct))}
    flags = {"n_bars": a.n_bars, "min_body_pct": a.min_body_pct,
             "min_step_pct": a.min_step_pct, "max_wick_pct": a.max_wick_pct}
    if a.no_manifest_check:
        disclosure = ("NOT VERIFIED (--no-manifest-check): the four knobs are "
                      "an UNCHECKED stamp on this artifact")
    else:
        refusal, disclosure = verify_manifest(cube.parent, flags)
        if refusal:
            print(refusal)
            return 2

    doc = grade(cube, config, min_n=a.min_n, top_n=a.top_n, note=a.note,
                step2=a.step2, disclosure=disclosure,
                preregistered_exit=a.preregistered_exit)
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube.parent.name}_grid_auto.json")
    out.parent.mkdir(parents=True, exist_ok=True)
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
