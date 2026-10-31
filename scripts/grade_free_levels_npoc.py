"""S6-B3171a: grade the naked-POC FREE levels off a landed cube. Zero engine hours.

WHY IT EXISTS. B2569 (owner directive 2026-09-02) made free-level grading a
leg of EVERY landing (L752 / #290). The naked_poc_retest_long entry carries
TWO offline axes and a missing leg produces NO row and NO FAIL, so the
engine-slate configs would land with those levels silently ungraded.

THE AXES - both read from signals_at_entry, both strict per the screener gate
(backtest/signals/screener.py strat_naked_poc_retest_long):
  * P5  count floor:        naked_poc_count > N      (production N = 0;
        free floors 1, 2 - each a strict SUBSET of the cube's fires)
  * P6  distance ceiling:   naked_poc_nearest_distance_pct < C
        (free levels = the SPECS free_band quantiles STRICTLY TIGHTER than
        the LANDED ceiling - P6 is ENGINE-SWEPT in this family, so the
        reproduction bound is the landed arm's NAKED_POC_MAX_DISTANCE_PCT,
        never a hardcoded production constant. The candle leg could hardcode
        its bound because its rsi axis was never engine-swept; copying that
        here would re-grade every non-production-ceiling cube against the
        wrong gate.)

REPRODUCTION GATE (owner, 2026-09-02): before any level is graded, every
covered row must RE-PASS at the LANDED bounds (count > 0 AND dist < landed
ceiling). A covered row that fails means the logged signals disagree with the
gate the engine ran; this exits 2 and grades nothing. Unverifiable rows are
counted, excluded and reported - never silently failed or kept.

SCORE REPRODUCTION (S6-B3120f / L877): the production row's per-exit sharpe /
ci_lo (NET basis, min_n=1) must EQUAL the landed family grade's figures with
matching trade counts, or the leg fails closed.

OCCUPANCY: a subset of SIGNALS is not a subset of TRADES (L812) - the
disclosure block reports the bound rather than pretending to it; no trade
count here bounds a level's true count in either direction (S6-B3139r).

WINDOW: only rows ENTERED in-sample are read (free_level_window =
roster_core.in_sample); no holdout-entered row is scored or counted.

Usage (the battery passes exactly this):
  python scripts/grade_free_levels_npoc.py --cube <dir> --out <grid.json>
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roster_core as rc  # noqa: E402
from episode_disclosure import month_concentration  # noqa: E402  (S6-B3318)
from occupancy_disclosure import occupancy_disclosure  # noqa: E402
import free_level_window as flw  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

LONG = "naked_poc_retest_long"
KEY_COUNT = "naked_poc_count"
KEY_DIST = "naked_poc_nearest_distance_pct"


def parse_signals(raw):
    """(dict or None). None means unverifiable - not empty, not failing."""
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        d = ast.literal_eval(raw)
    except Exception:                                   # noqa: BLE001
        try:
            d = json.loads(raw)
        except Exception:                               # noqa: BLE001
            return None
    return d if isinstance(d, dict) and d else None


def landed_ceiling(cube_dir: Path,
                   disclosed: float | None = None) -> tuple[float | None, str]:
    """(the landed arm's NAKED_POC_MAX_DISTANCE_PCT, or None + reason).
    Fail-closed: P6 is engine-swept, so the reproduction bound MUST come from
    the manifest - defaulting to 0.02 would re-grade a looser-ceiling cube
    against the wrong gate (L642).

    S6-B3173 (B3139q-r70i, L919): `disclosed` answers ONE absence only - a
    manifest that EXISTS and records no NAKED_POC_MAX_DISTANCE_PCT (the
    1-of-4-knob specs of S6-B3171, whose engine read its env default,
    backtest/config.py NAKED_POC_MAX_DISTANCE_PCT). The declared value comes
    back WITH a disclosure string the caller stamps on the artifact, and the
    reproduction gate then tests it against every covered row. A missing or
    unreadable manifest, an unparseable value, and a declaration that
    CONTRADICTS a recorded value all still fail closed - the same narrow
    escape leg 1 carries as grade_npoc_config --no-manifest-check.
    """
    mf = cube_dir / "run_manifest.json"
    if not mf.exists():
        return None, f"no run_manifest.json in {cube_dir}"
    try:
        man = json.loads(mf.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError) as exc:
        return None, f"run_manifest.json unreadable: {exc!r}"
    arms = man.get("arms") or []
    env = dict((arms[0] or {}).get("env") or {}) if arms else {}
    raw = env.get("NAKED_POC_MAX_DISTANCE_PCT")
    if raw is None or str(raw).strip() == "":
        if disclosed is None:
            return None, ("the landed arm declares no NAKED_POC_MAX_DISTANCE_PCT "
                          "- P6 is engine-swept, so the reproduction bound is "
                          "unknowable without it (fail closed, L642)")
        return float(disclosed), (
            f"DISCLOSED (--disclose-landed-ceiling {disclosed}): the landed "
            "arm records no NAKED_POC_MAX_DISTANCE_PCT, so this bound is the "
            "hand run's declaration, not the manifest's; the reproduction "
            "gate tested it against every covered row (S6-B3173)")
    try:
        val = float(raw)
    except (TypeError, ValueError):
        return None, f"NAKED_POC_MAX_DISTANCE_PCT unparseable: {raw!r}"
    if disclosed is not None and float(disclosed) != val:
        return None, (f"--disclose-landed-ceiling {disclosed} contradicts the "
                      f"manifest's NAKED_POC_MAX_DISTANCE_PCT {val} (refused)")
    return val, ""

def score_reproduction(prod_per_exit, grid_path, ted_all=None) -> dict:
    """S6-B3120f: the reproduction gate covers the SCORE, not only the fire
    set - identical in intent to the candle leg's block."""
    try:
        grid = json.loads(Path(grid_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"family_grid": str(grid_path).replace("\\", "/"),
                "basis": "net (roster_core.net_pnl)",
                "compared_exits": 0,
                "mismatches": [f"family grid unreadable: {exc!r}"]}
    mine = {str(r["exit"]): r for r in prod_per_exit}
    compared, mismatches = 0, []
    for row in grid.get("per_exit") or []:
        ex = str(row.get("exit"))
        fam_sh, fam_cl = row.get("is_sharpe"), row.get("is_ci_lo")
        if fam_sh is None and fam_cl is None:
            continue
        m = mine.get(ex)
        if m is None:
            mismatches.append(f"{ex}: in the family grid, absent here")
            continue
        compared += 1
        if int(row.get("fires", -1)) != int(m["n"]):
            why = ("" if ted_all is None
                   else " [" + flw.gap_breakdown(ted_all, ex) + "]")
            mismatches.append(
                f"{ex}: n {m['n']} vs family fires {row.get('fires')}{why}")
            continue
        for key, fam in (("sharpe", fam_sh), ("ci_lo", fam_cl)):
            v = m.get(key)
            same = (v is None and fam is None) or (
                v is not None and fam is not None
                and round(float(v), 3) == round(float(fam), 3))
            if not same:
                mismatches.append(f"{ex}: {key} {v} vs family {fam}")
    if compared == 0:
        mismatches.append(
            "no exit compared - the family grid carries no graded rows")
    return {"family_grid": str(grid_path).replace("\\", "/"),
            "basis": "net (roster_core.net_pnl)",
            "compared_exits": compared, "mismatches": mismatches}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cube", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--family-grid", default=None,
                    help="the landed family grid this leg must reproduce "
                         "(default output_audit/<cube>_grid_auto.json)")
    ap.add_argument("--strategy", default=None,
                    help="override the manifest's graded strategy (hand runs)")
    ap.add_argument("--disclose-landed-ceiling", type=float, default=None,
                    help="S6-B3173 hand runs only: the ceiling the engine "
                         "ran when the manifest records none - stamped on "
                         "the artifact, refused if it contradicts a "
                         "recorded value")
    a = ap.parse_args()

    cube_dir = Path(a.cube)
    tl_path = cube_dir / "trade_log.csv"
    ted_path = cube_dir / "trade_exit_detail.csv"
    for p in (tl_path, ted_path):
        if not p.exists():
            print(f"[FAIL] no {p.name} in {cube_dir}")
            return 2

    strat = a.strategy
    if strat is None:
        try:
            import run_postconfig as rp
            strat, _riders = rp.graded_and_riders(cube_dir)
        except Exception:                               # noqa: BLE001
            strat = None
    if strat != LONG:
        print(f"[FAIL] graded strategy {strat!r} is not {LONG!r} - this leg "
              "grades the naked-POC free axes only (fail closed, L642)")
        return 2

    ceiling, why = landed_ceiling(cube_dir, a.disclose_landed_ceiling)
    if ceiling is None:
        print(f"[FAIL] {why}")
        return 2

    import producer_variant_table as pvt
    spec = pvt.SPECS.get(LONG) or pvt.SPECS_PHASE0[LONG]
    by_id = {p["id"]: p for p in spec["params"]}
    p6_levels = sorted(float(x) for x in by_id["P6"]["free_band"]
                       if float(x) < ceiling)
    p5_floors = sorted(int(x) for x in by_id["P5"]["free_band"] if int(x) > 0)

    tl = pd.read_csv(tl_path, low_memory=False)
    tl = tl[tl["strategy"].astype(str) == strat].copy()
    if tl.empty:
        print(f"[FAIL] no {strat} rows in {tl_path.name}")
        return 2
    tl_all = tl
    tl = flw.in_sample_only(tl).copy()
    if tl.empty:
        print(f"[FAIL] no in-sample {strat} rows in {tl_path.name} "
              f"({flw.split_windows(tl_all)}) - nothing this leg may grade")
        return 2

    # ---- reproduction gate, at the LANDED bounds --------------------------
    counts, dists, unverifiable = [], [], 0
    for raw in tl["signals_at_entry"]:
        d = parse_signals(raw)
        if d is None or KEY_COUNT not in d or KEY_DIST not in d:
            counts.append(None)
            dists.append(None)
            unverifiable += 1
        else:
            counts.append(float(d[KEY_COUNT]))
            dists.append(float(d[KEY_DIST]))
    tl["_cnt"], tl["_dist"] = counts, dists
    covered = tl[tl["_cnt"].notna() & tl["_dist"].notna()]
    failed = covered[~((covered["_cnt"] > 0) & (covered["_dist"] < ceiling))]
    repro = {"covered_rows": int(len(covered)),
             "unverifiable_rows": int(unverifiable),
             "rows_total": int(len(tl)),
             "landed_ceiling": ceiling,
             "landed_ceiling_source": why or "run_manifest.json arms[0].env",
             "max_covered_dist": (float(covered["_dist"].max())
                                  if len(covered) else None),
             "gate_mirrored": (f"{KEY_COUNT} > 0 AND {KEY_DIST} < {ceiling} "
                               "(strict, per screener.py)"),
             "failed_reproduction": int(len(failed))}
    if len(failed):
        print(f"[FAIL] reproduction gate: {len(failed)} of {len(covered)} "
              f"covered rows do NOT re-pass count>0 AND dist<{ceiling} - the "
              "logged signals disagree with the gate the engine ran, so "
              "nothing this tool reports about any level is believable "
              "(owner ruling 2026-09-02). Grading nothing.")
        return 2

    # ---- grade each free level on the exit-expanded cube ------------------
    ted_all = pd.read_csv(ted_path, low_memory=False)
    ted_strat = ted_all[ted_all["strategy"].astype(str) == strat]
    ted = flw.in_sample_only(ted_strat).copy()
    ted["pnl_pct"] = rc.net_pnl(ted["pnl_pct"].astype(float))
    ted["entry_date"] = ted["entry_date"].astype(str).str[:10]
    covered = covered.copy()
    covered["entry_date"] = covered["entry_date"].astype(str).str[:10]

    def grade_keep(keep, label, axis, level, is_production):
        ids = set(zip(keep["ticker"].astype(str), keep["entry_date"]))
        sub = ted[[(t, d) in ids for t, d in
                   zip(ted["ticker"].astype(str), ted["entry_date"])]]
        per_exit = []
        for ex, g in sub.groupby("exit_method", observed=True):
            st = rc.evaluate(g["pnl_pct"], g["hold_days"], min_n=a.min_n)
            if st is None:
                continue
            per_exit.append({"exit": str(ex), "n": int(len(g)),
                             "sharpe": st.get("sharpe"),
                             "ci_lo": st.get("ci_lo"),
                             # S6-B3318 (B3139q-r159): the one-episode disclosure,
                             # the rest scored at this row's own floor
                             "episode": month_concentration(
                                 g, lambda d: (rc.evaluate(d["pnl_pct"], d["hold_days"],
                                                           min_n=a.min_n) or {}).get("sharpe"))})
        per_exit.sort(key=lambda r: -(r["ci_lo"] if r["ci_lo"] is not None
                                      else -9e9))
        return sub, {"axis": axis, "level": level, "label": label,
                     "is_production": is_production,
                     "trades_kept": int(len(keep)),
                     "trades_kept_bound": ("NONE - occupancy cascades both "
                                           "ways (S6-B3139r)"),
                     "exit_rows": int(len(sub)),
                     "exits_evaluable": len(per_exit),
                     "best": per_exit[0] if per_exit else None,
                     "per_exit": per_exit[:6]}

    results = []
    prod_keep = covered  # every covered row re-passed the landed bounds
    prod_sub, prod_row = grade_keep(prod_keep, f"landed (count>0, dist<{ceiling})",
                                    "base", ceiling, True)
    results.append(prod_row)
    for lvl in p6_levels:
        keep = covered[covered["_dist"] < float(lvl)]
        results.append(grade_keep(keep, f"P6 dist<{lvl}", "P6",
                                  float(lvl), False)[1])
    for floor in p5_floors:
        keep = covered[covered["_cnt"] > float(floor)]
        results.append(grade_keep(keep, f"P5 count>{floor}", "P5",
                                  float(floor), False)[1])

    # ---- S6-B3120f: SCORE reproduction against the landed family grade ----
    prod_check = []
    for ex, g in prod_sub.groupby("exit_method", observed=True):
        st = rc.evaluate(g["pnl_pct"], g["hold_days"], min_n=1)
        if st is not None:
            prod_check.append({"exit": str(ex), "n": int(len(g)),
                               "sharpe": st.get("sharpe"),
                               "ci_lo": st.get("ci_lo")})
    fam_grid = Path(a.family_grid) if a.family_grid else (
        ROOT / "output_audit" / f"{cube_dir.name}_grid_auto.json")
    srep = score_reproduction(prod_check, fam_grid, ted_all=ted_all)
    if srep["mismatches"]:
        print("[FAIL] score reproduction (S6-B3120f): the production row does "
              "not reproduce the landed family grade ("
              + "; ".join(str(x) for x in srep["mismatches"][:6])
              + ") - grading nothing.")
        return 2

    doc = {
        "strategy": strat,
        "axes": {"P5": "count floor (naked_poc_count > N)",
                 "P6": f"distance ceiling tighter than the landed {ceiling}"},
        "grader": "scripts/grade_free_levels_npoc.py (S6-B3171a)",
        "cube": str(cube_dir).replace("\\", "/"),
        "levels_searched": {"P6": p6_levels, "P5": p5_floors},
        "basis": ("net: pnl_pct clipped to +/-WINSORIZE then minus "
                  "COST_BPS/100 - roster_core.net_pnl (S6-B3120f)"),
        "window": {"trade_log": flw.window_disclosure(tl_all, tl, "trade_log"),
                   "trade_exit_detail": flw.window_disclosure(
                       ted_strat, ted, "trade_exit_detail")},
        "reproduction": repro,
        "score_reproduction": srep,
        "occupancy": occupancy_disclosure(cube_dir, strat,
                                          window=flw.IS_WINDOW),
        "results": results,
        # the free_band_levels_graded reader's shape (S6-B2871b / L741)
        "levels": {f"{r['axis']}:{r['level']}": {
                       "level": r["level"], "axis": r["axis"],
                       "is_fires": r["trades_kept"],
                       "per_exit_ranked_by_ci_lo": r["per_exit"]}
                   for r in results},
        "multiplicity_exposure": (
            f"{len(p6_levels) + len(p5_floors)} free levels searched across "
            "2 axes, each a max over the evaluable exits, nested inside ONE "
            "engine run - not independent trials; no correction applied here "
            "(S6-B2444 recording rule)"),
        "verdict_status": ("CANDIDATES, never admissions - no trade count is "
                           "a bound in either direction while occupancy is "
                           "unsimulated (L812, S6-B3139r)"),
    }
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube_dir.name}_free_levels.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    from roster_core import stamp_metric_code as _smc  # S6-B3139i
    _smc(doc)
    out.write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")
    base = results[0]
    print(f"[OK] {strat} - reproduction {repro['covered_rows']} covered / "
          f"{repro['unverifiable_rows']} unverifiable / 0 failed at the "
          f"landed bounds; base keeps {base['trades_kept']} trades")
    for r in results[1:]:
        b = r["best"]
        print(f"     {r['label']:<18} keeps {r['trades_kept']:<5} "
              + (f"best {b['exit']} ci_lo {b['ci_lo']} n {b['n']}"
                 if b else "no exit cleared the power floor"))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
