#!/usr/bin/env python
# Source: <cube>/{trade_log.csv,trade_exit_detail.csv,run_manifest.json} per CHECKLIST #77.
"""S6-B3248 / S6-B3304 (B3139q-r163): the FREE-LEVEL leg (B2569 - graded on
EVERY landing) for any SPECS family whose free axes are persisted or derived
signal keys. Zero engine hours: each level is a filter of the landed fires.

WHY ONE LEG (#291 / L754): five free-level graders exist, one per family
(bollinger, candle, naked-POC, pairs, institutional). This one reads the axes
from the registry, so squeeze_breakout and camarilla_r4_breakout - and any
later family - join by registration, never by a sixth and seventh copy.

THE REGISTRY CONTRACT: SPECS[<strategy>].tools.free_levels =
  {"script": "grade_free_levels_knob.py",
   "ops": {<param id>: "ge" | "gt" | "le" | "lt"},
   "derive": "scripts/<module>.py" or absent}
Each op'd param reads its signal_keys[0] (persisted, or added by the derive
module) and keeps a fire when value <op> level. Its FREE levels on this cube
are its free_band levels STRICTLY TIGHTER than the LANDED level - the arm's
env value when the param has an actuator, else its production. A param's
`legs` field limits it to those legs' fires.

DERIVE: loaded by offline_level_sweep.load_derive (one loader, its sha256
recorded), called derive(sig) or, when it takes two arguments,
derive(sig, landed_env). A module may expose derivable(landed_env) -> '' or a
reason; then every axis whose key it derives is NOT EVALUABLE on this cube and
is written with that reason - never graded, never silently skipped.

REPRODUCTION GATE: before any level is graded, the covered in-sample fires
must pass every axis at its LANDED level - at least --repro-min of them
(0.999, offline_level_sweep's default; the persisted magnitudes are rounded,
so a fire on the edge can read a hair inside it). Below it: exit 2, nothing
graded. Rows a key does not cover are counted and excluded, never failed.

SCORE REPRODUCTION (S6-B3120f / L877): the landed row's NET per-leg x exit
in-sample Sharpe and lower bound, computed by roster_core._sharpe exactly as
grade_knob_config grades the family cells, must equal the family grid's
(cell base:<leg>, rounded to 3 places) with matching trade counts - else
exit 2. The family grid is the battery's <key>_grid_auto.json beside --out.

WINDOW: in-sample entries only (roster_core.in_sample). OCCUPANCY: a subset
of signals is not a subset of trades (L812) - disclosed, never simulated.

Usage (the battery passes exactly this, under the landed arm's env):
  python scripts/grade_free_levels_knob.py --cube <dir> --out <key>_free_levels.json
"""
from __future__ import annotations

import argparse
import ast
import inspect
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import roster_core as rc  # noqa: E402
from episode_disclosure import month_concentration  # noqa: E402  (S6-B3318)
from occupancy_disclosure import occupancy_disclosure  # noqa: E402

OPS = {"ge": lambda v, x: v >= x, "gt": lambda v, x: v > x,
       "le": lambda v, x: v <= x, "lt": lambda v, x: v < x}


def _parse(raw):
    if not isinstance(raw, str) or not raw.strip():
        return None
    for reader in (json.loads, ast.literal_eval):
        try:
            d = reader(raw)
            return d if isinstance(d, dict) and d else None
        except Exception:                                   # noqa: BLE001
            continue
    return None


def _tighter(op: str, level, landed) -> bool:
    """Is `level` strictly tighter than the landed level for this op?"""
    lv, ld = float(level), float(landed)
    return lv > ld if op in ("ge", "gt") else lv < ld


def landed_env(cube_dir: Path) -> tuple[dict | None, str]:
    mf = cube_dir / "run_manifest.json"
    if not mf.exists():
        return None, f"no run_manifest.json in {cube_dir}"
    try:
        man = json.loads(mf.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError) as exc:
        return None, f"run_manifest.json unreadable: {exc!r}"
    arms = man.get("arms") or []
    env = dict(((arms[0] or {}) if arms else {}).get("env") or {})
    return env, ""


def axes_of(entry: dict, env: dict) -> list:
    """[{pid, key, op, landed, levels, legs}] from the registry contract."""
    fl = (entry.get("tools") or {}).get("free_levels") or {}
    ops = dict(fl.get("ops") or {})
    by_id = {p["id"]: p for p in entry.get("params") or []}
    out = []
    for pid, op in ops.items():
        p = by_id.get(pid)
        if p is None or op not in OPS or not p.get("signal_keys"):
            raise SystemExit(f"[FAIL] free_levels.ops names {pid!r} with op {op!r} - "
                             "not a param with signal_keys and a known op (fail closed)")
        landed = p.get("production")
        if p.get("env"):
            raw = env.get(p["env"])
            if raw is None:
                raise SystemExit(f"[FAIL] the landed arm records no {p['env']} - the "
                                 f"landed level of {pid} is unknowable (fail closed, L642)")
            if str(raw).strip() != "":
                landed = float(raw)
        levels = sorted((float(x) for x in (p.get("free_band") or [])
                         if _tighter(op, x, landed)),
                        reverse=op in ("le", "lt"))
        out.append({"pid": pid, "key": p["signal_keys"][0], "op": op,
                    "landed": float(landed), "levels": levels,
                    "legs": list(p.get("legs") or [])})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--cube", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--repro-min", type=float, default=0.999)
    ap.add_argument("--family-grid", default=None,
                    help="the landed family grid to reproduce (default: --out "
                         "with _free_levels.json read as _grid_auto.json)")
    ap.add_argument("--strategy", default=None,
                    help="override the manifest's graded strategy (hand runs)")
    a = ap.parse_args(argv)
    cube_dir = Path(a.cube)
    for name in ("trade_log.csv", "trade_exit_detail.csv"):
        if not (cube_dir / name).exists():
            print(f"[FAIL] no {name} in {cube_dir}")
            return 2
    strat = a.strategy
    if strat is None:
        try:
            import run_postconfig as rp
            strat, _riders = rp.graded_and_riders(cube_dir)
        except Exception:                               # noqa: BLE001
            strat = None
    from producer_variant_table import SPECS
    entry = SPECS.get(strat or "")
    if entry is None or not ((entry.get("tools") or {}).get("free_levels") or {}).get("ops"):
        print(f"[FAIL] {strat!r} declares no tools.free_levels.ops in SPECS - "
              "nothing this leg may grade (fail closed, L642)")
        return 2
    env, why = landed_env(cube_dir)
    if env is None:
        print(f"[FAIL] {why}")
        return 2
    axes = axes_of(entry, env)
    fl = entry["tools"]["free_levels"]
    derive_fn, derive_rec, not_eval = None, None, {}
    if fl.get("derive"):
        from offline_level_sweep import load_derive
        derive_fn, derive_rec = load_derive(ROOT / fl["derive"])
        # the module is loaded from its file, not imported, so its own
        # globals - not sys.modules - hold its derivable()
        derivable = derive_fn.__globals__.get("derivable")
        reason = derivable(env) if callable(derivable) else ""
        two = len(inspect.signature(derive_fn).parameters) >= 2
        probe = derive_fn({}, env) if two else derive_fn({})
        derived = set(probe)
        for ax in axes:
            if reason and ax["key"] in derived:
                not_eval[ax["pid"]] = reason

    # ---- the landed fires, in-sample, with each axis' value -----------------
    from smc_lsr_step1 import build
    m = build(cube_dir, strat=strat, keys=[])
    m["pnl_pct"] = rc.net_pnl(m["pnl_pct"].astype(float))
    m = rc.in_sample(m)
    tl = pd.read_csv(cube_dir / "trade_log.csv", low_memory=False,
                     usecols=["strategy", "ticker", "entry_date", "direction",
                              "signals_at_entry"])
    tl = tl[tl["strategy"].astype(str) == strat].drop_duplicates(["ticker", "entry_date"])
    vals = {ax["pid"]: [] for ax in axes}
    for raw in tl["signals_at_entry"]:
        d = _parse(raw)
        if d is not None and derive_fn is not None:
            d = derive_fn(d, env) if two else derive_fn(d)
        for ax in axes:
            v = None if d is None else d.get(ax["key"])
            try:
                vals[ax["pid"]].append(None if v is None else float(v))
            except (TypeError, ValueError):
                vals[ax["pid"]].append(None)
    keyed = tl[["ticker", "entry_date"]].copy()
    keyed["entry_date"] = pd.to_datetime(keyed["entry_date"], errors="coerce").dt.date
    for ax in axes:
        keyed["_" + ax["pid"]] = vals[ax["pid"]]
    m = m.merge(keyed, on=["ticker", "entry_date"], how="left")
    fires = m.drop_duplicates(["ticker", "entry_date"])
    legs = [x for x in ("long", "short") if x in set(fires["direction"].astype(str))]

    def applies(ax, leg):
        return not ax["legs"] or leg in ax["legs"]

    # ---- reproduction at the landed levels ----------------------------------
    live = [ax for ax in axes if ax["pid"] not in not_eval]
    cov = fires.copy()
    for ax in live:
        mask = cov["direction"].map(lambda d, ax=ax: applies(ax, d))
        cov = cov[~mask | cov["_" + ax["pid"]].notna()]
    passed = cov.copy()
    for ax in live:
        col = "_" + ax["pid"]
        ok = [(not applies(ax, d)) or OPS[ax["op"]](v, ax["landed"])
              for d, v in zip(passed["direction"], passed[col])]
        passed = passed[ok]
    repro = {"covered_fires": int(len(cov)), "fires_total": int(len(fires)),
             "uncovered_fires": int(len(fires) - len(cov)),
             "pass_at_landed": int(len(passed)),
             "rate": round(len(passed) / max(len(cov), 1), 6),
             "landed": {ax["pid"]: ax["landed"] for ax in axes},
             "repro_min": a.repro_min}
    if live and repro["rate"] < a.repro_min:
        print(f"[FAIL] reproduction: {len(passed)} of {len(cov)} covered fires pass "
              f"every axis at its landed level ({repro['rate']}) < {a.repro_min} - the "
              "logged signals disagree with the gate the engine ran; grading nothing")
        return 2

    def grade(keep_ids, leg, label, axis, level):
        sub = m[[(t, d) in keep_ids for t, d in zip(m["ticker"], m["entry_date"])]]
        sub = sub[sub["direction"] == leg]
        per_exit = []
        for ex, g in sub.groupby("exit_method", observed=True):
            r = rc._sharpe(g["pnl_pct"].values, g["hold_days"], min_n=a.min_n)
            if r is None:
                continue
            per_exit.append({"exit": str(ex), "n": int(len(g)),
                             "sharpe": r.get("sharpe"), "ci_lo": r.get("ci_lo"),
                             # S6-B3318: the one-episode disclosure at this floor
                             "episode": month_concentration(
                                 g, lambda d: (rc._sharpe(d["pnl_pct"].values, d["hold_days"],
                                                          min_n=a.min_n) or {}).get("sharpe"))})
        per_exit.sort(key=lambda r: -(r["ci_lo"] if r["ci_lo"] is not None else -9e9))
        return {"axis": axis, "level": level, "leg": leg, "label": label,
                "fires_kept": int(len(set(zip(sub["ticker"], sub["entry_date"])))),
                "exits_evaluable": len(per_exit),
                "best": per_exit[0] if per_exit else None, "per_exit": per_exit[:6]}

    base_ids = set(zip(passed["ticker"], passed["entry_date"]))
    results = [grade(base_ids, leg, f"landed ({leg})", "base", None) for leg in legs]
    for ax in live:
        col = "_" + ax["pid"]
        for lvl in ax["levels"]:
            keep = passed[[v is not None and OPS[ax["op"]](v, lvl) for v in passed[col]]]
            ids = set(zip(keep["ticker"], keep["entry_date"]))
            for leg in legs:
                if applies(ax, leg):
                    results.append(grade(ids, leg, f"{ax['pid']} {ax['key']} {ax['op']} {lvl}",
                                         ax["pid"], lvl))

    # ---- score reproduction against the family grid -------------------------
    grid_path = Path(a.family_grid) if a.family_grid else Path(
        str(a.out).replace("_free_levels.json", "_grid_auto.json"))
    srep = {"family_grid": str(grid_path).replace("\\", "/"), "compared": 0, "mismatches": []}
    try:
        grid = json.loads(grid_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        grid = None
        srep["mismatches"].append(f"family grid unreadable: {exc!r}")
    if grid is not None:
        fam = {(r.get("cell"), str(r.get("exit"))): r for r in grid.get("rows") or []
               if r.get("is_sharpe") is not None}
        for leg in legs:
            # every landed fire of the leg - the family grid's population
            sub = m[m["direction"] == leg]
            for ex, g in sub.groupby("exit_method", observed=True):
                r = rc._sharpe(g["pnl_pct"].values, g["hold_days"], min_n=a.min_n)
                f = fam.get((f"base:{leg}", str(ex)))
                if r is None and f is None:
                    continue
                srep["compared"] += 1
                if f is None or r is None:
                    srep["mismatches"].append(f"{leg} {ex}: one side ungraded")
                    continue
                if int(f.get("is_n", -1)) != int(len(g)):
                    srep["mismatches"].append(f"{leg} {ex}: n {len(g)} vs family {f.get('is_n')}")
                    continue
                for k, fk in (("sharpe", "is_sharpe"), ("ci_lo", "is_ci_lo")):
                    v, w = r.get(k), f.get(fk)
                    if not ((v is None and w is None) or (v is not None and w is not None
                                                          and round(float(v), 3) == round(float(w), 3))):
                        srep["mismatches"].append(f"{leg} {ex}: {k} {v} vs family {w}")
        if srep["compared"] == 0:
            srep["mismatches"].append("no cell compared - the family grid carries no graded rows")
    if srep["mismatches"]:
        print("[FAIL] score reproduction (S6-B3120f): " + "; ".join(srep["mismatches"][:6])
              + " - grading nothing")
        return 2

    doc = {"strategy": strat, "grader": "scripts/grade_free_levels_knob.py",
           "cube": str(cube_dir).replace("\\", "/"),
           "basis": ("net: pnl_pct clipped to +/-WINSORIZE then minus "
                     "COST_BPS/100 - roster_core.net_pnl"),
           "window": f"in-sample entries only [{rc.IS_START}, {rc.IS_END})",
           "axes": [{k: ax[k] for k in ("pid", "key", "op", "landed", "levels", "legs")}
                    for ax in axes],
           "not_evaluable": [{"axis": pid, "reason": r} for pid, r in sorted(not_eval.items())],
           "derive": derive_rec,
           "levels_searched": {ax["pid"]: ax["levels"] for ax in live},
           "reproduction": repro, "score_reproduction": srep,
           "occupancy": occupancy_disclosure(cube_dir, strat,
                                             window=(rc.IS_START, rc.IS_END)),
           "results": results,
           "levels": {f"{r['axis']}:{r['level']}:{r['leg']}": {
                          "level": r["level"], "axis": r["axis"], "leg": r["leg"],
                          "is_fires": r["fires_kept"],
                          "per_exit_ranked_by_ci_lo": r["per_exit"]}
                      for r in results if r["axis"] != "base"},
           "multiplicity_exposure": (
               f"{sum(len(ax['levels']) for ax in live)} free levels across "
               f"{len(live)} axes, each a max over the evaluable exits, nested in ONE "
               "engine run - not independent trials; no correction here (S6-B2444)"),
           "verdict_status": ("CANDIDATES, never admissions - no trade count is a "
                              "bound in either direction while occupancy is "
                              "unsimulated (L812, S6-B3139r)")}
    from roster_core import stamp_metric_code as _smc
    _smc(doc)
    Path(a.out).write_text(json.dumps(doc, indent=1, default=str), encoding="utf-8")
    na = "; ".join(f"{d['axis']} not evaluable: {d['reason']}" for d in doc["not_evaluable"])
    print(f"[OK] {strat} - reproduction {repro['pass_at_landed']} of {repro['covered_fires']} "
          f"covered fires at the landed levels; {len(results) - len(legs)} level rows graded"
          + (f"; {na}" if na else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
