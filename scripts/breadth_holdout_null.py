#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""S6-B3139bw (owner question 2026-10-07, "i closed because you said qualifying
cells were just noise in step 3. Is that true?"): is a breadth Step-2 holdout
read's qualifier set beyond what chance produces?

Nothing new is selected. The read's OWN registered cells are re-scored on the
read's OWN frame (breadth_step1_grid.build_frame, the leg and basis the Step-1
artifact recorded) with the reader's OWN grade (breadth_step2_read.grade_holdout).

1. REPRODUCTION, fail closed: the all-six non-npt qualifier set must equal the
   read artifact's qualifier set exactly.
2. BASELINE: the unfiltered leg's holdout grade per exit.
3. NULL: K joint shuffles of the signal vectors across fires WITHIN each period
   (in-sample, holdout). Each cell keeps its exact in-sample and holdout trade
   counts and the axes keep their joint structure; only the link between a
   fire's signals and its outcome is broken. Recorded per shuffle: the number
   of all-six qualifiers, the distinct cells with one, each observed
   qualifier's holdout Sharpe (a per-cell p, valid only for a PRE-CHOSEN cell),
   and the best holdout lower bound over every cell-exit (the FAMILY-WISE
   statistic: the observed best was picked as the best of all cell-exits).

Provenance (B1801 / #201): every null figure here - the shuffle medians,
percentiles and p-values - is SYNTHETIC: drawn from rng shuffles of the read's
own data, so it prices chance and never performance. The OBSERVED figures
(qualifier set, holdout grades, baseline) are measured.

Direction of the null's known bias: random subsets spread over time, while a
real filter's trades cluster, so a real no-edge filter is MORE variable than
this null - its p-values are, if anything, too small. A "not beyond chance"
verdict from it is therefore conservative.

usage: breadth_holdout_null.py --step1-artifact A --read-artifact R
                               --perms K [--seed S] --out O
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import roster_core as rc  # noqa: E402
import breadth_step1_grid as bg  # noqa: E402
from breadth_step2_read import grade_holdout  # noqa: E402

FK = ["ticker", "entry_date"]


def prepare(art: dict):
    """(cells, F, period, by_exit) for the artifact's strategy, leg and basis."""
    cells = sorted({(r["axis"], r["op"], r["level"]) for r in art["rows"]})
    axis_keys = sorted({c[0] for c in cells})
    m, _ = bg.build_frame(art["strategy"], art.get("depth_base"), axis_keys,
                          basis=art.get("basis") or "gross",
                          leg=art.get("leg") or "both")
    F = m.drop_duplicates(FK)[FK + axis_keys].reset_index(drop=True)
    F["_fid"] = np.arange(len(F))
    ed = pd.to_datetime(F["entry_date"]).dt.date
    period = np.where((ed >= rc.IS_START) & (ed < rc.IS_END), "IS",
                      np.where((ed >= rc.HO_START) & (ed < rc.HO_END), "HO", "OUT"))
    m = m.merge(F[FK + ["_fid"]], on=FK, how="left")
    by_exit = {}
    for ex in sorted(e for e in m.exit_method.unique() if e != bg.BARRED_EXIT):
        g = m[m.exit_method == ex][["entry_date", "pnl_pct", "hold_days", "_fid"]]
        g = g.reset_index(drop=True)
        by_exit[ex] = (g, g["_fid"].to_numpy(dtype=int))
    return cells, axis_keys, F, period, by_exit


def score(cells, frame, by_exit) -> dict:
    """{(axis, op, level, exit): grade or None} over every non-npt cell-exit."""
    res = {}
    for key, op, lev in cells:
        mk = (bg._cell_mask(frame, key, op, lev) & frame[key].notna()).to_numpy()
        for ex, (g, fid) in by_exit.items():
            sub = g[mk[fid]]
            res[(key, op, lev, ex)] = grade_holdout(sub) if len(sub) else None
    return res


def qualifiers(res: dict) -> set:
    return {k for k, r in res.items() if r and r["all_live_gates"]}


def max_ci_lo(res: dict, keys=None):
    keys = res.keys() if keys is None else keys
    xs = [res[k].get("ci_lo") for k in keys
          if res[k] and res[k].get("ci_lo") is not None]
    return max(xs) if xs else None


def run(art: dict, read: dict, perms: int, seed: int) -> dict:
    if (art.get("leg") or "both") != (read.get("leg") or "both"):
        raise SystemExit("REFUSED: the read and the Step-1 artifact name different legs")
    cells, axis_keys, F, period, by_exit = prepare(art)
    obs = score(cells, F, by_exit)
    got = qualifiers(obs)
    want = {(q["axis"], q["op"], q["level"], q["exit"]) for q in read["qualifiers"]}
    if got != want:
        raise SystemExit(f"REFUSED: reproduction failed - {len(got)} qualifiers here, "
                         f"{len(want)} in the read; differ on {sorted(got ^ want)[:5]}")
    base = {}
    for ex, (g, _) in by_exit.items():
        r = grade_holdout(g)
        base[ex] = None if r is None else {
            "holdout_sharpe": r["sharpe"], "ci_lo": r.get("ci_lo"), "holdout_n": r["n"],
            "profit_factor": r["profit_factor"], "all_live_gates": bool(r["all_live_gates"])}
    rng = np.random.default_rng(seed)
    groups = {p: np.flatnonzero(period == p) for p in ("IS", "HO", "OUT")}
    vals = F[axis_keys].to_numpy()
    counts, ncells, mx = [], [], []
    per_q = {k: [] for k in got}
    for _ in range(perms):
        perm = np.arange(len(F))
        for idx in groups.values():
            if len(idx) > 1:
                perm[idx] = rng.permutation(idx)
        Fs = F.copy()
        Fs[axis_keys] = vals[perm]
        res = score(cells, Fs, by_exit)
        q = qualifiers(res)
        counts.append(len(q))
        ncells.append(len({x[:3] for x in q}))
        mx.append(max_ci_lo(res))
        for k in per_q:
            per_q[k].append(res[k]["sharpe"] if res.get(k) else None)
    nc, nce = np.array(counts), np.array(ncells)
    obs_cells = len({x[:3] for x in got})
    per = []
    for k in sorted(got, key=lambda x: -obs[x]["sharpe"]):
        o, xs = obs[k]["sharpe"], [v for v in per_q[k] if v is not None]
        per.append({"axis": k[0], "op": k[1], "level": k[2], "exit": k[3],
                    "holdout_sharpe": o, "ci_lo": obs[k].get("ci_lo"),
                    "holdout_n": obs[k]["n"],
                    "null_median_sharpe": float(np.median(xs)) if xs else None,
                    "null_p95_sharpe": float(np.percentile(xs, 95)) if xs else None,
                    "p_value_if_prechosen": ((1 + sum(v >= o for v in xs)) / (1 + len(xs))
                                             if xs else None)})
    best = max_ci_lo(obs)
    best_at = (max((k for k in obs if obs[k] and obs[k].get("ci_lo") is not None),
                   key=lambda k: obs[k]["ci_lo"]) if best is not None else None)
    a = np.array([x for x in mx if x is not None])

    def _p(arr, o):
        return float((1 + (arr >= o).sum()) / (1 + len(arr))) if len(arr) else None
    return {
        "_doc": __doc__, "strategy": art["strategy"], "leg": art.get("leg") or "both",
        "basis": art.get("basis") or "gross", "n_perms": perms, "seed": seed,
        "null_label": ("SYNTHETIC null (rng shuffles of the read's own data) - "
                       "prices chance, never performance; observed figures are measured"),
        "cell_exits_scored": len(obs), "registered_cells": len(cells),
        "fires": {p: int(len(i)) for p, i in groups.items()},
        "observed": {"qualifiers": len(got), "cells_with_a_qualifier": obs_cells},
        "null_qualifiers": ({"mean": float(nc.mean()), "median": float(np.median(nc)),
                             "p95": float(np.percentile(nc, 95)), "max": int(nc.max()),
                             "p_value": _p(nc, len(got))} if perms else None),
        "null_cells_with_a_qualifier": ({"mean": float(nce.mean()),
                                         "p95": float(np.percentile(nce, 95)),
                                         "p_value": _p(nce, obs_cells)} if perms else None),
        "family_best_ci_lo": {
            "observed": best, "at": list(best_at) if best_at else None,
            "null_median": float(np.median(a)) if len(a) else None,
            "null_p95": float(np.percentile(a, 95)) if len(a) else None,
            "p_value": _p(a, best) if (len(a) and best is not None) else None},
        "baseline_unfiltered_by_exit": base,
        "per_qualifier": per,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step1-artifact", required=True)
    ap.add_argument("--read-artifact", required=True)
    ap.add_argument("--perms", type=int, required=True)
    ap.add_argument("--seed", type=int, default=20261007)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    art = json.loads(Path(a.step1_artifact).read_text(encoding="utf-8"))
    read = json.loads(Path(a.read_artifact).read_text(encoding="utf-8"))
    out = run(art, read, a.perms, a.seed)
    out["step1_artifact"], out["read_artifact"] = a.step1_artifact, a.read_artifact
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("observed", "null_qualifiers",
                                          "family_best_ci_lo")}, indent=1))
    print(f"wrote {a.out} ({time.time()-t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
