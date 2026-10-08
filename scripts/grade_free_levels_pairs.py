"""S6-B3140: grade the pairs_mean_reversion_long FREE levels off a landed
cube. Zero engine hours.

WHY IT EXISTS. B2569 (owner directive 2026-09-02) made free-level grading a
leg of EVERY landing (L752 / #290): a missing leg produces NO row and NO
FAIL, so the Step-1 cube would land with the approved threshold levels
silently ungraded. Modelled on grade_free_levels_bollinger.py (S6-B3119),
the L754 family-extraction contract.

THE AXES GRADED HERE. The campaign's three gate thresholds, all OFFLINE (no
env knob; each reads a value persisted per trade in signals_at_entry):
  P2  pair_count_active  `> 0`    (TIGHTER = RAISE the floor,  levels >= L)
  P3  pair_half_life     `>= 5`   (TIGHTER = RAISE the floor,  levels >= L)
  P4  pair_zscore_signed `< -2`   (TIGHTER = LOWER the ceiling, levels <= L)
Tighter levels use CLOSED comparisons - the charter's measured retentions
were computed with `ser >= lv` / `ser <= lv` (build_table_a's free-band retention computation), and
this leg must reproduce those counts, while PRODUCTION mirrors the engine
gate verbatim (screener strat_pairs_mean_reversion_long), strict `>` and `<`
included. Coverage on the R5 baseline: all three keys at 100.0% of the
strategy's 5,036 fires (the charter's measured free-band lines).

THE DEPTH FACTORIAL (the charter's Step-1 search): 5 x 5 x 5 = 125
level-combinations (production + 4 tighter per axis), each a strict subset
of the recorded fires, graded per exit. Verdicts are CANDIDATES ranked by
is_ci_lo (B1608: ranked list, no gates at Step 1), never admissions.

AXIS SCOPE, DISCLOSED (#290 - scheduled-with-mechanism, never dropped):
P2/P3/P4 and their factorial are graded here. The producer knobs (EG
significance, z-window, half-life bounds) are DEFINED-NO-ACTUATOR - feature
requests, not gradable axes, named in the SPECS entry. The breadth B-axes
ARE T3-REGISTERED (owner verbatim 2026-10-08 "also register b breadth axes
at T3"; registration artifact output_audit/b3140_pairs_breadth_axes_t3.json:
125 census axes at coverage >= 0.98, both ops per axis since no per-axis
direction was ruled, 53 below-floor keys RESIM-ONLY excluded) and RIDE THIS
LEG: after the depth factorial, breadth_step1_grid runs on the landing's own
cube (--cube-dir, --leg long, --basis net), battery-wired per B2569/#290 -
the status view is regenerated first (the S6-B2848b gate's own instruction),
and a nonzero breadth exit FAILS this leg closed. The permutation-null
search pricing runs at the Step-3 read (breadth_step2_read), per the
bollinger precedent. Each axis family named; none silent.

REPRODUCTION GATE (owner, 2026-09-02): before any level is graded, every
covered row must RE-PASS the full PRODUCTION gate; a covered row that fails
means the logged signals disagree with the gate the engine ran - exit 2,
grade nothing. Unparseable rows are counted, excluded and reported.

THE OCCUPANCY DISCLOSURE (L812): a subset of SIGNALS is not a subset of
TRADES - removing trades at a tighter level frees occupancy the engine alone
can simulate. No count here is a bound in either direction (S6-B3139r):
verdicts are candidates, never admissions.

WINDOW (S6-B3128a, B3135): only rows ENTERED in-sample are read
(free_level_window = roster_core.in_sample, the family grader's own
selector). No holdout-ENTERED row is ever scored, used to rank a level, or
counted toward the reproduction n. The window is ENTRY-dated (B3139).

Usage (the battery passes exactly this):
  python scripts/grade_free_levels_pairs.py --cube <dir> --out <grid.json>
"""
from __future__ import annotations

import argparse
import ast
import itertools
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roster_core as rc  # noqa: E402
from occupancy_disclosure import (  # noqa: E402
    occupancy_disclosure)
import free_level_window as flw  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# adapter-dispatched family leg: no module-level STRAT constant
# (test_b3120d ratchet; the candle-grader shape)
PAIRS_LONG = "pairs_mean_reversion_long"

# the live gate, read from the producer (screener strat_pairs_mean_reversion_long)
AXES = (
    # (param id, signal key, production level, production op, tighter op)
    ("P2", "pair_count_active", 0.0, "gt", "ge"),
    ("P3", "pair_half_life", 5.0, "ge", "ge"),
    ("P4", "pair_zscore_signed", -2.0, "lt", "le"),
)
_OPS = {"gt": lambda v, b: v > b, "ge": lambda v, b: v >= b,
        "lt": lambda v, b: v < b, "le": lambda v, b: v <= b}


def keep_row(value: float, op: str, bound: float) -> bool:
    """Mirror the gate (production ops) / the charter's measured retention
    (closed ops on tighter levels, build_table_a's free-band retention
    computation) EXACTLY."""
    return _OPS[op](value, bound)


def passes(levels: dict, vals: dict) -> bool:
    """One row against one level-combination. levels[key] is None for
    production (gate verbatim) or a tighter level (closed comparison)."""
    for _pid, key, prod, prod_op, tight_op in AXES:
        lv = levels[key]
        if lv is None:
            if not keep_row(vals[key], prod_op, prod):
                return False
        else:
            if not keep_row(vals[key], tight_op, float(lv)):
                return False
    return True


def score_reproduction(prod_per_exit, grid_path, ted_all=None) -> dict:
    """S6-B3120f (L877): the reproduction gate covers the SCORE, not only
    the fire set - the production row's per-exit sharpe / ci_lo (net basis,
    min_n=1) must EQUAL the landed family grade's on every exit the family
    grid carries, with matching trade counts, or the leg fails closed."""
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


def grade_kept(ted, keep_ids, min_n):
    """Per-exit grades over the exit-expanded rows of the kept entries."""
    sub = ted[[(t, d) in keep_ids for t, d in
               zip(ted["ticker"].astype(str), ted["entry_date"])]]
    per_exit = []
    for ex, g in sub.groupby("exit_method", observed=True):
        st = rc.evaluate(g["pnl_pct"], g["hold_days"], min_n=min_n)
        if st is None:
            continue
        per_exit.append({"exit": str(ex), "n": int(len(g)),
                         "sharpe": st.get("sharpe"),
                         "ci_lo": st.get("ci_lo")})
    per_exit.sort(key=lambda r: -(r["ci_lo"] if r["ci_lo"] is not None
                                  else -9e9))
    return sub, per_exit


def parse_signals(raw):
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
    if strat != PAIRS_LONG:
        print(f"[FAIL] graded strategy {strat!r} is not {STRAT!r} - this leg "
              "grades the pairs threshold axes only (fail closed, L642)")
        return 2

    import producer_variant_table as pvt
    by_id = {p["id"]: p for p in pvt.SPECS[strat]["params"]}
    levels_of: dict[str, list[float]] = {}
    for pid, key, prod, _po, _to in AXES:
        row = by_id[pid]
        assert float(row["production"]) == prod, (pid, row["production"], prod)
        levels_of[key] = [float(x) for x in row["free_band"]
                          if float(x) != prod]

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

    # ---- reproduction gate, at the PRODUCTION gate (verbatim) ------------
    keys = [key for _pid, key, *_ in AXES]
    parsed, unverifiable = [], 0
    for raw in tl["signals_at_entry"]:
        d = parse_signals(raw)
        if d is None or any(k not in d for k in keys):
            parsed.append(None)
            unverifiable += 1
        else:
            parsed.append({k: float(d[k]) for k in keys})
    tl["_vals"] = parsed
    covered = tl[tl["_vals"].notna()].copy()
    prod_levels = {key: None for key in keys}
    failed = covered[~covered["_vals"].apply(
        lambda v: passes(prod_levels, v))]
    repro = {"covered_rows": int(len(covered)),
             "unverifiable_rows": int(unverifiable),
             "rows_total": int(len(tl)),
             "production_gate": ("pair_count_active > 0 AND pair_half_life "
                                 ">= 5 AND pair_zscore_signed < -2.0"),
             "failed_reproduction": int(len(failed))}
    if len(failed):
        print(f"[FAIL] reproduction gate: {len(failed)} of {len(covered)} "
              "covered rows do NOT re-pass the production gate "
              "(pair_count_active > 0 AND pair_half_life >= 5 AND "
              "pair_zscore_signed < -2.0) - the logged signals disagree with "
              "the gate the engine ran, so nothing this tool reports about "
              "any level is believable (owner ruling 2026-09-02). "
              "Grading nothing.")
        return 2

    # ---- the exit-expanded cube, on the family grader's basis ------------
    ted_all = pd.read_csv(ted_path, low_memory=False)
    ted_strat = ted_all[ted_all["strategy"].astype(str) == strat]
    ted = flw.in_sample_only(ted_strat).copy()
    ted["pnl_pct"] = rc.net_pnl(ted["pnl_pct"].astype(float))
    ted["entry_date"] = ted["entry_date"].astype(str).str[:10]
    covered["entry_date"] = covered["entry_date"].astype(str).str[:10]

    def ids_for(levels: dict) -> set:
        keep = covered[covered["_vals"].apply(lambda v: passes(levels, v))]
        return set(zip(keep["ticker"].astype(str), keep["entry_date"]))

    # ---- single-axis enumerations (production + each tighter level) ------
    single_axis = {}
    for pid, key, prod, _po, tight_op in AXES:
        rows_ax = []
        for lv in [None] + levels_of[key]:
            levels = dict(prod_levels)
            levels[key] = lv
            ids = ids_for(levels)
            _sub, per_exit = grade_kept(ted, ids, a.min_n)
            rows_ax.append({
                "level": ("production" if lv is None else float(lv)),
                "is_production": lv is None,
                "op": ("gate verbatim" if lv is None else tight_op),
                "trades_kept": len(ids),
                "trades_kept_bound": ("NONE - occupancy cascades both ways "
                                      "(S6-B3139r)"),
                "exits_evaluable": len(per_exit),
                "best": per_exit[0] if per_exit else None,
                "per_exit": per_exit[:6]})
        single_axis[f"{pid}_{key}"] = rows_ax

    # ---- the depth factorial: 5 x 5 x 5 = 125 combinations ---------------
    combos = []
    prod_sub = prod_check = None
    for c_lv, h_lv, z_lv in itertools.product(
            [None] + levels_of["pair_count_active"],
            [None] + levels_of["pair_half_life"],
            [None] + levels_of["pair_zscore_signed"]):
        levels = {"pair_count_active": c_lv, "pair_half_life": h_lv,
                  "pair_zscore_signed": z_lv}
        ids = ids_for(levels)
        sub, per_exit = grade_kept(ted, ids, a.min_n)
        is_prod = c_lv is None and h_lv is None and z_lv is None
        if is_prod:
            prod_sub = sub
        combos.append({
            "combo": {k: ("production" if v is None else float(v))
                      for k, v in levels.items()},
            "is_production": is_prod,
            "trades_kept": len(ids),
            "exits_evaluable": len(per_exit),
            "best": per_exit[0] if per_exit else None,
            "per_exit": per_exit[:4]})
    ranked = sorted(
        (c for c in combos if c["best"] is not None),
        key=lambda c: -(c["best"]["ci_lo"]
                        if c["best"]["ci_lo"] is not None else -9e9))

    # ---- S6-B3120f: SCORE reproduction against the landed family grade --
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

    # ---- the T3-REGISTERED breadth leg (owner verbatim 2026-10-08 "also
    # register b breadth axes at T3"): breadth_step1_grid on the landing's
    # own cube, battery-wired per B2569/#290. Fail CLOSED on any nonzero
    # exit (L642). The status view is regenerated first - the S6-B2848b
    # freshness gate's own instruction ("REGENERATE FIRST").
    import subprocess
    reg_path = ROOT / "output_audit" / "b3140_pairs_breadth_axes_t3.json"
    try:
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"[FAIL] breadth registration unreadable ({exc!r}) at "
              f"{reg_path} - the T3-registered breadth leg cannot run "
              "(fail closed, L642)")
        return 2
    rs = subprocess.run([sys.executable,
                         str(ROOT / "scripts" / "build_strategy_status.py")],
                        cwd=ROOT, capture_output=True, text=True)
    if rs.returncode != 0:
        print("[FAIL] status-view regenerate exit "
              f"{rs.returncode} - the breadth leg's freshness gate "
              f"(S6-B2848b) cannot be satisfied: {rs.stderr[-300:]}")
        return 2
    axes_arg = ",".join([f"{k}:ge" for k in reg["axes"]]
                        + [f"{k}:le" for k in reg["axes"]])
    breadth_out = ROOT / "output_audit" / f"{cube_dir.name}_breadth_grid_long.json"
    ruling = ("owner verbatim 2026-10-08: 'also register b breadth axes at "
              "T3' (with 'proceed with step 1'); registration "
              "output_audit/b3140_pairs_breadth_axes_t3.json")
    rb = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "breadth_step1_grid.py"),
         "--strategy", strat, "--axes", axes_arg,
         "--out", str(breadth_out), "--band-ruling", ruling,
         "--leg", str(reg["leg"]), "--basis", str(reg["basis"]),
         "--cube-dir", str(cube_dir)],
        cwd=ROOT, capture_output=True, text=True)
    breadth = {"registration": str(reg_path).replace("\\", "/"),
               "axes_registered": int(reg["axes_n"]),
               "ops_per_axis": 2,
               "exit": rb.returncode,
               "artifact": str(breadth_out).replace("\\", "/"),
               "tail": (rb.stdout or rb.stderr)[-400:]}
    if rb.returncode != 0 or not breadth_out.exists():
        print(f"[FAIL] breadth leg exit {rb.returncode} (artifact "
              f"{'present' if breadth_out.exists() else 'ABSENT'}) - the "
              "T3-registered breadth axes did not grade; fail closed "
              f"(L642). tail: {(rb.stdout or rb.stderr)[-400:]}")
        return 2

    base = next(c for c in combos if c["is_production"])
    doc = {
        "strategy": strat,
        "axis": "P2 pair_count_active / P3 pair_half_life / P4 "
                "pair_zscore_signed (the charter's depth factorial)",
        "grader": "scripts/grade_free_levels_pairs.py (S6-B3140)",
        "cube": str(cube_dir).replace("\\", "/"),
        "gate_mirrored": ("production: pair_count_active > 0 AND "
                          "pair_half_life >= 5 AND pair_zscore_signed < -2.0 "
                          "(strict, per screener.py); tighter levels CLOSED "
                          "(>= / <=) per build_table_a's free-band retention computation"),
        "levels_searched": {k: v for k, v in levels_of.items()},
        "axis_scope": ("P2/P3/P4 and their 125-combination factorial graded "
                       "here; producer knobs DEFINED-NO-ACTUATOR (named in "
                       "SPECS, not gradable); breadth B-axes T3-REGISTERED "
                       "(owner verbatim 2026-10-08 'also register b breadth "
                       "axes at T3') and graded by the riding "
                       "breadth_step1_grid leg below - each axis family "
                       "named, none silent (#290)"),
        "basis": ("net: pnl_pct clipped to +/-WINSORIZE then minus "
                  "COST_BPS/100 - roster_core.net_pnl (S6-B3120f)"),
        "window": {"trade_log": flw.window_disclosure(tl_all, tl, "trade_log"),
                   "trade_exit_detail": flw.window_disclosure(
                       ted_strat, ted, "trade_exit_detail")},
        "reproduction": repro,
        "score_reproduction": srep,
        "breadth_leg": breadth,
        "occupancy": occupancy_disclosure(cube_dir, strat,
                                          window=flw.IS_WINDOW),
        "single_axis": single_axis,
        "factorial": {
            "combinations": len(combos),
            "production_trades_kept": base["trades_kept"],
            "ranking_key": "best-exit is_ci_lo (B1608: ranked, no gates)",
            "top": ranked[:15],
            "results": combos,
        },
        "multiplicity_exposure": (
            f"{len(combos) - 1} non-production level-combinations searched, "
            f"each a max over up to "
            f"{max((c['exits_evaluable'] for c in combos), default=0)} exits, "
            "nested inside ONE engine run - the combinations are not "
            "independent trials and no correction is applied here "
            "(S6-B2444 recording rule)"),
        "verdict_status": ("CANDIDATES, never admissions - no trade count is "
                           "a bound in either direction while occupancy "
                           "is unsimulated (L812, S6-B3139r); EXPLORATORY "
                           "registration rides (B2085/F24)"),
    }
    out = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube_dir.name}_free_levels.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    from roster_core import stamp_metric_code as _smc  # S6-B3139i
    _smc(doc)
    out.write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")
    print(f"[OK] {strat} P2/P3/P4 - reproduction {repro['covered_rows']} "
          f"covered / {repro['unverifiable_rows']} unverifiable / 0 failed; "
          f"production keeps {base['trades_kept']} trades; "
          f"{len(combos)} combinations graded")
    for c in ranked[:5]:
        b = c["best"]
        print(f"     {c['combo']} keeps {c['trades_kept']:<5} "
              f"best {b['exit']} ci_lo {b['ci_lo']} n {b['n']}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
