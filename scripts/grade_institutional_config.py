"""B2520: Step-1 grader for institutional_committed_growth_long configs.

Until this file existed, run_postconfig.py could grade ONE strategy family
(smc_breaker_block via tighten_breaker_block.py) and silently SKIPPED step 2
for every other cube with the wrong diagnosis "pre-B2138 cube". The
institutional config-1 grid (output_audit/output_icg_cfg1_grid_auto.json)
was built by hand at B2511 from an uncommitted scratchpad script; this is that
grader as a committed, pinned, family-registered tool. test_b2520 holds it to
the B2511 golden: breakeven_plus_trail is_sharpe 0.263 / is_ci_lo -0.087 /
fires 373 / 24 exits graded.

METHOD (identical to the smc grader's Step-1 leg, S6-B2409 vocabulary):
  * rc.load_cube -> the shared conditioning (winsorize + cost) exactly once;
  * IS rows via rc.in_sample; every exit graded with rc.evaluate(min_n=1) so
    the artifact records EVERY exit, and the Step-1 power floor (--min-n,
    default 10) is applied as the RANKED / BELOW_POWER_FLOOR verdict, not as
    a silent drop;
  * ranked by is_ci_lo desc then fires desc - is_ci_lo is the RANKING KEY,
    not a gate (owner ruling B1608);
  * the holdout is counted (holdout_n) but never graded here.

CONFIG KEYS follow the B2505 pinned contract (producer_variant_table.
D_AXIS_FAMILIES["institutional_committed_growth_long"]) so Table D renders
the artifact natively: P4_min_consecutive_quarters, P5_growth_lookback_quarters,
P6_growth_multiple, P9_span; admit carries min_committed_growth (P7) and
fallback_min_increased (P8), which are grader-only levels (S6-B2504).

ONE combination per cube: the swept parameters live in the precompute the
engine consumed, so a cube IS one combination and equivalence collapse (6b)
needs >= 2 combinations - run_postconfig records that as N/A, not SKIPPED.

Usage:
  python scripts/grade_institutional_config.py --cube output_icg_cfg1 \
      --min-consecutive-quarters 4 --growth-lookback-quarters 4 \
      --growth-multiple 1.1 --span 200
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roster_core as rc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STRAT = "institutional_committed_growth_long"
P7_PROD, P8_PROD = 3, 5   # screener.py:6648 production levels (S6-B2504)


def refuse_nonproduction(p7: int, p8: int) -> str | None:
    """L751/B2569: these flags are artifact STAMPS, not filters - grade()
    never reads them. A non-production value would ship an identical grade
    stamped as a different measurement, so it is REFUSED, not recorded.
    Free levels are graded by grade_free_levels_institutional.py --cube,
    which applies the OR gate and gates on baseline reproduction first."""
    if (p7, p8) != (P7_PROD, P8_PROD):
        return (f"[FAIL] --min-committed-growth/--fallback-min-increased are "
                f"artifact stamps at production ({P7_PROD}, {P8_PROD}) only; "
                f"this grader does NOT filter on them (L751). Got ({p7}, {p8})."
                f" Use grade_free_levels_institutional.py --cube for levels.")
    return None


def grade(cube_csv: Path, config: dict, admit: dict, *, min_n: int = 10,
          top_n: int = 10, note: str = "") -> dict:
    cube = rc.load_cube(cube_csv, chunksize=500_000)
    strategies = sorted(set(cube["strategy"].astype(str).unique()))
    if strategies != [STRAT]:
        raise SystemExit(f"cube carries strategies {strategies}; this grader "
                         f"is registered for {STRAT} only (fail closed, L642)")
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
            "admit": {**admit, "holdout_n": int(ho_n.get(ex, 0)),
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
        "config": dict(config), "strategy": STRAT,
        "grader": "scripts/grade_institutional_config.py (B2520)",
        "cube": str(cube_csv).replace("\\", "/"),
        "note": note or ("B2520: Step-1 ranking, graded via roster_core."
                         "evaluate per exit on the IS rows; is_ci_lo is the "
                         "ranking key, not a gate (B1608); holdout counted, "
                         "never graded. Config keys follow the B2505 contract."),
        "window": {"is": [str(rc.IS_START), str(rc.IS_END)],
                   "holdout": [str(rc.HO_START), str(rc.HO_END)],
                   "cube_entry_min": str(min(cube["entry_date"])),
                   "cube_entry_max": str(max(cube["entry_date"]))},
        "rows": int(len(cube)), "is_rows": int(len(is_rows)),
        "holdout_rows": int(len(ho_rows)), "min_n": min_n,
        # ONE combination per cube: the swept parameters were consumed by the
        # engine through the precompute, so the funnel has a single row.
        "results": [{"combo": {**config, **admit}, "verdict": combo_verdict,
                     "n_exits_graded": len(per_exit),
                     "n_exits_ranked": len(ranked)}],
        "step1_combinations_carried": 1,
        "step1_distinct_outcomes": 1,
        "step1_ranking": ranked[:top_n],
        "per_exit": per_exit,
        "results_n_exits": len(per_exit),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cube", required=True,
                    help="cube dir or its trade_exit_detail.csv")
    ap.add_argument("--min-consecutive-quarters", type=int, required=True)
    ap.add_argument("--growth-lookback-quarters", type=int, required=True)
    ap.add_argument("--growth-multiple", type=float, required=True)
    ap.add_argument("--span", type=int, required=True)
    ap.add_argument("--min-committed-growth", type=int, default=P7_PROD)
    ap.add_argument("--fallback-min-increased", type=int, default=P8_PROD)
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--top-n", type=int, default=10)
    ap.add_argument("--note", default="")
    ap.add_argument("--out", default=None,
                    help="default output_audit/<cube dir>_grid_auto.json")
    a = ap.parse_args()
    refusal = refuse_nonproduction(a.min_committed_growth,
                                   a.fallback_min_increased)
    if refusal:
        print(refusal)
        return 2
    cube = Path(a.cube)
    if cube.is_dir():
        cube = cube / "trade_exit_detail.csv"
    if not cube.exists():
        print(f"[FAIL] no cube at {cube}")
        return 2
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube.parent.name}_grid_auto.json")
    config = {"P4_min_consecutive_quarters": a.min_consecutive_quarters,
              "P5_growth_lookback_quarters": a.growth_lookback_quarters,
              "P6_growth_multiple": a.growth_multiple, "P9_span": a.span}
    admit = {"min_committed_growth": a.min_committed_growth,
             "fallback_min_increased": a.fallback_min_increased}
    doc = grade(cube, config, admit, min_n=a.min_n, top_n=a.top_n, note=a.note)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")
    top = doc["step1_ranking"][0] if doc["step1_ranking"] else None
    print(f"graded {doc['results_n_exits']} exits on {doc['is_rows']} IS rows "
          f"({doc['rows']} total, holdout rows {doc['holdout_rows']}); "
          + (f"best {top['exit']} is_ci_lo {top['is_ci_lo']} is_sharpe "
             f"{top['is_sharpe']} fires {top['fires']}" if top
             else "NO exit cleared the power floor"))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
