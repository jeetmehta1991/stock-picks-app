"""S6-B3119: Step-1/Step-2 grader for the bollinger_lower span configs.

WHY IT EXISTS. The owner approved testing ema spans (verbatim 2026-09-27:
"Q2 approved one line change fix. I want to test various spans"), the gate is
span-keyed since B3119, and validate_spec (S6-B2883) refuses an engine-band
promise without a complete `tools` adapter - a landing would otherwise fail
closed AFTER the engine spend. This is the family's grade leg.

MODELLED ON grade_candle_config.py (S6-B2900) - the second family extracts the
contract (L754) - and like it, EVERY statistic is a roster_core delegation, so
the span cubes are graded by the same code as every admitted strategy. The
candle grader's council-driven rules carry over:

 1. THE GRADED STRATEGY COMES FROM THE MANIFEST (run_postconfig.
    graded_and_riders), with the cube as the pre-B2721 one-strategy fallback;
    the cube is FILTERED to the graded strategy before any statistic runs.
    This family registers bollinger_lower only (a DUAL long/short strategy in
    ONE registration - both legs share the cube rows under one name).
 2. THE KNOB IS VERIFIED AGAINST THE MANIFEST, NOT MERELY STAMPED. One env
    knob: STRAT_EMA_SPAN. Mismatch is refused; a landed arm with no env block
    is refused (fail closed, L642).
 3. SPAN PRODUCIBILITY IS CHECKED: the gate reads price_above_ema_{span} /
    below_ema_{span}, which compute_ema_sma emits only for spans present in
    EMA_PAIRS (technical.py:768, env-driven; default
    "9:21,20:50,50:200,100:150", config.py:2524). A span absent from the
    pairs would produce a ZERO-FIRE cube that graded clean - refused here
    with the pairs named.

ONE COMBINATION PER CUBE: the engine read the knob, so the funnel has a single
row. Within one config the exit family IS reported via the report-only
multiplicity block (roster_core.bh_fdr_report over exit_family_rows), which
breadth_step2_read requires. Cross-config multiplicity across the span
campaign is computable post-hoc by globbing the per-config grids.

Usage:
  python scripts/grade_bollinger_config.py --cube output_bl_span050 \\
      --ema-span 50 [--step2] [--preregistered-exit time_stop_10d] \\
      --out <grid.json>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roster_core as rc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

STRAT = "bollinger_lower"
FAMILY = (STRAT,)

# the launcher's contract: one env knob for the swept axis (B2865); arm env
# values serialise as STRINGS, so comparison is by VALUE, not spelling.
ENV_OF = {"ema_span": "STRAT_EMA_SPAN"}

DEFAULT_EMA_PAIRS = "9:21,20:50,50:200,100:150"   # config.py:2524


def _norm(v) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    if s == "":
        return ""
    try:
        return repr(round(float(s), 9))
    except (TypeError, ValueError):
        return s


def _pairs_spans(raw: str) -> set[int]:
    out: set[int] = set()
    for tok in str(raw).split(","):
        tok = tok.strip()
        if not tok:
            continue
        f, s = tok.split(":")
        out.add(int(f))
        out.add(int(s))
    return out


def verify_manifest(cube_dir: Path, flags: dict) -> tuple[str | None, str]:
    """(refusal or None, disclosure). The stamp is a claim about WHICH cube
    this is; an unverified one is how a grader files one cube under another
    config's name (the grade_candle_config rule, ported)."""
    mf = cube_dir / "run_manifest.json"
    if not mf.exists():
        return (f"[FAIL] no run_manifest.json in {cube_dir} - the span flag "
                "cannot be verified against what the engine read "
                "(S6-B3119)"), ""
    try:
        man = json.loads(mf.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError) as exc:
        return f"[FAIL] run_manifest.json unreadable: {exc!r}", ""
    arms = man.get("arms") or []
    arm = (arms[0] or {}) if arms else {}
    env = dict(arm.get("env") or {})
    if not env:
        return ("[FAIL] the landed arm declares no `env` block, so the "
                "STRAT_EMA_SPAN the engine read is unrecorded and the flag "
                "verifies nothing (fail closed, L642)"), ""
    bad = []
    for key, envname in ENV_OF.items():
        if envname not in env:
            bad.append(f"{envname} absent from the arm")
        elif _norm(env[envname]) != _norm(flags[key]):
            bad.append(f"{envname} landed {env[envname]!r} but the flag says "
                       f"{flags[key]!r}")
    if bad:
        return ("[FAIL] the flags do not match the landed arm: "
                + "; ".join(bad)), ""
    span = int(float(str(flags["ema_span"])))
    pairs_raw = env.get("EMA_PAIRS", DEFAULT_EMA_PAIRS)
    spans = _pairs_spans(pairs_raw)
    if span not in spans:
        return (f"[FAIL] span {span} is not emitted by the run's EMA_PAIRS "
                f"({pairs_raw!r} -> spans {sorted(spans)}): the gate would "
                "have read an ABSENT key all run, so this cube's fires cannot "
                "be the span-{span} strategy (zero-fire-by-construction, "
                "S6-B3119)"), ""
    return None, ("flags verified against arms[0].env: "
                  f"STRAT_EMA_SPAN={env.get('STRAT_EMA_SPAN')!r}; span {span} "
                  f"emitted by EMA_PAIRS={pairs_raw!r}")


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
                "bollinger_lower family only (fail closed, L642)")
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
    """The ONE holdout read of a Step-2 cube - byte-for-byte the candle
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
        "grader": "scripts/grade_bollinger_config.py (S6-B3119)",
        "cube": str(cube_csv).replace("\\", "/"),
        "manifest_check": disclosure or "NOT RUN (--no-manifest-check)",
        "note": note or ("S6-B3119: Step-1 ranking via roster_core.evaluate "
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
    ap.add_argument("--ema-span", type=int, required=True,
                    help="the STRAT_EMA_SPAN the engine ran (verified against "
                         "the landed arm's env)")
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
    config = {"P4_ema_span": a.ema_span}
    flags = {"ema_span": a.ema_span}
    if a.no_manifest_check:
        disclosure = ("NOT VERIFIED (--no-manifest-check): the span is an "
                      "UNCHECKED stamp on this artifact")
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
