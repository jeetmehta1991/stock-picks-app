#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""B2638 (S6-B2633): Step-1 for an OFFLINE-FREE strategy - no engine hours.

THE CLASS THIS SERVES. A producer parameter is *offline-free* when the
MAGNITUDE it thresholds was persisted in `signals_at_entry` at fire time. Then
a TIGHTER level is not a new simulation - it is a SUBSET of the landed fire
set, and Step-1 costs seconds instead of the 16-40 engine hours a config
carries. This module is the generic instrument (the owner's run-producers-once
directive); `pead_long_high_yoy_growth_only` is its first caller, and the axis
map is data, not code, so the next strategy is a new --axes argument.

FOUR REFUSALS, all fail-closed (L642: the absent input is the case the guard
exists for):

  1. REPRODUCTION. Re-applying the PRODUCTION levels must return the landed
     fire set exactly. Anything below 1.0 means the persisted magnitude is not
     the quantity the engine thresholded, and every derived level would be
     measuring a different gate than the one that ran. Refuses below --repro-min.
  2. COVERAGE. Rows whose signals_at_entry is empty cannot be levelled. An
     empty dict is NOT a zero (S6-B2512 / B2574): it means the engine's live
     signals were never persisted for that row. Refuses below --coverage-min.
  3. JOIN. Every cube row must find its magnitudes. An unmatched row would be
     silently dropped from the subset and quietly shrink the denominator.
  4. TRUNCATION. Subsetting is exact only if the engine recorded EVERY
     candidate that fired. `backtest.py:2417` bypasses max_candidates_per_day
     under cube isolation, so an isolation cube is safe; a NON-isolation cube
     truncates at the cap, and the trades a tighter level would have freed were
     never simulated. MEASURED for pead: max 48 fires on one day against a cap
     of 30, which is the positive evidence that no truncation occurred.

IN-SAMPLE ONLY, BY CONSTRUCTION. This module never slices the holdout - it
imports roster_core.in_sample and has no holdout code path at all. Step-1 is a
ranked list with NO gates (owner ruling B1608); the single pre-registered
holdout read is a SEPARATE, owner-fired action against the cell named here.

WHAT THE ARTIFACT IS FOR. The written JSON is the pre-registration record: it
names the trials count, the selected cell and the axis map BEFORE any holdout
code runs. A ranked list produced after a holdout read is not evidence.

Usage:
  python scripts/offline_level_sweep.py --strategy pead_long_high_yoy_growth_only \
      --axes "days_since_last_earnings:le:20,40,60" \
             "earnings_eps_yoy_growth:ge:0.05,0.10,0.20,0.35,0.50" \
      --production 60,0.05 --out output_audit/b2638_pead_step1_is_surface.json
"""
from __future__ import annotations

import argparse
import ast
import itertools
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import roster_core as rc  # noqa: E402

CUBE = ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv"
TRADE_LOG = ROOT / "output_r5_merged_1_7" / "trade_log.csv"
CANDIDATE_CAP = 30          # backtest.py:171 default; bypassed under isolation


def parse_axis(spec: str) -> dict:
    """'key:op:v1,v2' -> {'key','op','levels'}. op is le (tighten downward)
    or ge (tighten upward) - the direction the THRESHOLD is applied, which is
    a property of the gate, never inferable from the numbers."""
    key, op, levels = spec.split(":", 2)
    if op not in ("le", "ge"):
        raise ValueError(f"axis {key}: op must be le or ge, got {op!r}")
    return {"key": key, "op": op, "levels": [float(v) for v in levels.split(",")]}


def _parse_sig(s):
    if not isinstance(s, str) or not s.strip():
        return {}
    try:
        return json.loads(s)
    except Exception:
        try:
            return ast.literal_eval(s)
        except Exception:
            return {}


def keep(frame: pd.DataFrame, axes: list[dict], combo: tuple) -> pd.DataFrame:
    m = pd.Series(True, index=frame.index)
    for ax, level in zip(axes, combo):
        col = frame[ax["key"]]
        m &= (col <= level) if ax["op"] == "le" else (col >= level)
    return frame[m]


def load(strategy: str, axes: list[dict]) -> tuple[pd.DataFrame, dict]:
    """Merged cube + magnitudes, plus the refusal evidence. Raises on refusal."""
    tl = pd.read_csv(TRADE_LOG, low_memory=False,
                     usecols=["ticker", "strategy", "entry_date", "signals_at_entry"])
    t = tl[tl.strategy == strategy].copy()
    if t.empty:
        raise SystemExit(f"REFUSED: {strategy} has no rows in {TRADE_LOG.name}")
    sig = t["signals_at_entry"].map(_parse_sig)
    covered = sig.map(lambda d: isinstance(d, dict) and len(d) > 0)
    coverage = float(covered.mean())
    for ax in axes:
        t[ax["key"]] = sig.map(lambda d, k=ax["key"]: d.get(k))

    cube = pd.read_csv(CUBE, low_memory=False)
    g = cube[cube.strategy == strategy].copy()
    cols = ["ticker", "entry_date"] + [ax["key"] for ax in axes]
    m = g.merge(t[cols].drop_duplicates(["ticker", "entry_date"]),
                on=["ticker", "entry_date"], how="left")
    unmatched = int(m[axes[0]["key"]].isna().sum())

    per_day = t.groupby("entry_date").size()
    ev = {"landed_fires": int(len(t)), "coverage": coverage,
          "cube_rows": int(len(g)), "unmatched_join_rows": unmatched,
          "max_fires_per_day": int(per_day.max()),
          "candidate_cap": CANDIDATE_CAP,
          "cap_bypassed_evidence": bool(per_day.max() > CANDIDATE_CAP)}
    m["entry_date"] = pd.to_datetime(m["entry_date"], errors="coerce").dt.date
    return m, ev


def permutation_null(IS, axes, min_n, n_perms, seed):
    """B2676 (S6-B2638a): the grid-stage multiplicity instrument.

    Under NO signal->outcome link, what does the BEST IS sharpe over this
    exact grid look like? Each permutation shuffles the MAGNITUDE block
    jointly across unique fires (preserving the magnitudes' joint
    distribution and the per-exit pnl structure) and re-grades the identical
    cells x exits grid. The returned maxima are SYNTHETIC (rng) by
    construction - they price the search, they are never performance.
    B2376 measured that NO multiplicity correction existed at the grid
    stage; this is that correction, inherited by every campaign that runs
    this module with --null-perms.
    """
    import numpy as np
    rng = np.random.default_rng(seed)
    keys = [ax["key"] for ax in axes]
    fires = (IS.drop_duplicates(["ticker", "entry_date"])
               [["ticker", "entry_date"] + keys].reset_index(drop=True))
    base = IS.drop(columns=keys)
    maxima = []
    for _ in range(n_perms):
        idx = rng.permutation(len(fires))
        shuf = fires[["ticker", "entry_date"]].join(
            fires.loc[idx, keys].reset_index(drop=True))
        mm = base.merge(shuf, on=["ticker", "entry_date"], how="left")
        best = None
        for combo in itertools.product(*[ax["levels"] for ax in axes]):
            k = keep(mm, axes, combo)
            for _ex, sub in k.groupby("exit_method"):
                r = rc.evaluate(sub["pnl_pct"], sub["hold_days"], min_n=min_n)
                if r and r.get("sharpe") is not None and (best is None or r["sharpe"] > best):
                    best = r["sharpe"]
        maxima.append(best)
    return maxima


def sweep(strategy: str, axes: list[dict], production: tuple,
          coverage_min: float, repro_min: float, min_n: int) -> dict:
    m, ev = load(strategy, axes)
    if ev["coverage"] < coverage_min:
        raise SystemExit(f"REFUSED: signal coverage {ev['coverage']:.4f} < "
                         f"{coverage_min} - un-levellable rows would be dropped silently")
    if ev["unmatched_join_rows"]:
        raise SystemExit(f"REFUSED: {ev['unmatched_join_rows']} cube rows found no "
                         "magnitudes - the subset denominator would be wrong")

    fires = m.drop_duplicates(["ticker", "entry_date"])
    repro = len(keep(fires, axes, production)) / max(len(fires), 1)
    if repro < repro_min:
        raise SystemExit(f"REFUSED: production levels reproduce {repro:.4f} of the "
                         f"landed fire set (< {repro_min}) - the persisted magnitude "
                         "is not the quantity the engine thresholded")
    if not ev["cap_bypassed_evidence"]:
        ev["truncation_note"] = (
            f"max fires/day {ev['max_fires_per_day']} <= cap {CANDIDATE_CAP}: no "
            "positive evidence the cap was bypassed. Subsetting is exact only if "
            "the cube ran under isolation (backtest.py:2417).")

    IS = rc.in_sample(m)          # the only window this module ever reads
    cells = []
    for combo in itertools.product(*[ax["levels"] for ax in axes]):
        k = keep(IS, axes, combo)
        best_sh, best_ex = None, None
        for ex, sub in k.groupby("exit_method"):
            r = rc.evaluate(sub["pnl_pct"], sub["hold_days"], min_n=min_n)
            if r and r.get("sharpe") is not None and (best_sh is None or r["sharpe"] > best_sh):
                best_sh, best_ex = r["sharpe"], ex
        # owner directive: report TRADES, never cube rows - a cell's row count
        # is trades x exits and overstates the evidence ~26x.
        cells.append({"levels": list(combo),
                      "is_trades": int(len(k.drop_duplicates(["ticker", "entry_date"]))),
                      "is_cube_rows": int(len(k)),
                      "best_exit": best_ex, "is_sharpe": best_sh,
                      "exits_evaluated": int(k["exit_method"].nunique())})
    graded = [c for c in cells if c["is_sharpe"] is not None]
    graded.sort(key=lambda c: c["is_sharpe"], reverse=True)
    trials = sum(c["exits_evaluated"] for c in cells)
    return {"strategy": strategy,
            "axes": [{"key": a["key"], "op": a["op"], "levels": a["levels"]} for a in axes],
            "production_levels": list(production),
            "evidence": ev, "reproduction": repro,
            "cells_total": len(cells), "cells_graded": len(graded),
            "trials_searched": trials,
            "window": {"is": [str(rc.IS_START), str(rc.IS_END)]},
            "ranked": graded,
            "preregistration_candidate": graded[0] if graded else None,
            "holdout_read": "NOT FIRED - owner-gated, one shot, against the "
                            "preregistration_candidate named above"}


def attach_null(rec, strategy, axes, min_n, null_perms, null_seed):
    """Compute the permutation null for a completed sweep record, in place.
    Reloads the frame (sweep does not retain it) - the same refusals apply
    upstream, so a record that graded is a record the null can price."""
    import numpy as np
    m, _ = load(strategy, axes)
    IS = rc.in_sample(m)
    maxima = permutation_null(IS, axes, min_n, null_perms, null_seed)
    valid = [x for x in maxima if x is not None]
    obs = (rec.get("preregistration_candidate") or {}).get("is_sharpe")
    p = ((1 + sum(1 for x in valid if x >= obs)) / (len(valid) + 1)
         if (obs is not None and valid) else None)
    qs = ({str(q): round(float(np.quantile(valid, q)), 3)
           for q in (0.5, 0.9, 0.95, 0.99)} if valid else {})
    rec["permutation_null"] = {
        "provenance": "SYNTHETIC - rng permutations of the magnitude block "
                      "across fires; prices the search, never performance",
        "n_perms": null_perms, "seed": null_seed,
        "null_none_count": null_perms - len(valid),
        "null_max_is_sharpe_quantiles": qs,
        "observed_best_is_sharpe": obs,
        "p_value_best": round(p, 4) if p is not None else None}



def render_table(rec: dict) -> str:
    """B2643 (owner directive 2026-09-08): TABLE D, OFFLINE FORM.

    The ranked producer-combination view must NOT wait for an engine run - for
    an offline campaign the Step-1 artifact IS the run, so its ranking renders
    to markdown beside the JSON, automatically, every sweep (L651: delivery
    cannot depend on the reporter remembering; the runner invokes the renderer).
    """
    axes = rec["axes"]
    head = (f"# TABLE D (OFFLINE FORM) - {rec['strategy']}\n\n"
            f"Ranked producer combinations from the IN-SAMPLE sweep: "
            f"{rec['cells_graded']} of {rec['cells_total']} cells, "
            f"{rec['trials_searched']} trials (cells x exits); window "
            f"{rec['window']['is'][0]} .. {rec['window']['is'][1]}; "
            f"holdout NOT read by this artifact.\n\n")
    cols = " | ".join(f"{a['key']} ({a['op']})" for a in axes)
    lines = [f"| rank | {cols} | IS trades | best exit | IS sharpe |",
             "|" + "---|" * (len(axes) + 4)]
    prod = list(rec.get("production_levels", ()))
    for i, c in enumerate(rec["ranked"], 1):
        vals = " | ".join(str(v) for v in c["levels"])
        mark = " (production)" if list(c["levels"]) == prod else ""
        lines.append(f"| {i} | {vals}{mark} | {c['is_trades']} | "
                     f"{c['best_exit']} | {c['is_sharpe']:.3f} |")
    return head + "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--axes", nargs="+", required=True,
                    help="key:op:v1,v2,... with op in {le,ge}")
    ap.add_argument("--production", required=True,
                    help="comma-separated production level per axis, in order")
    ap.add_argument("--out", required=True)
    ap.add_argument("--coverage-min", type=float, default=0.99)
    ap.add_argument("--repro-min", type=float, default=0.999)
    ap.add_argument("--min-n", type=int, default=30)
    ap.add_argument("--null-perms", type=int, default=0,
                    help="B2676: permutation-null size for the best-of-grid "
                         "multiplicity price; 0 = off")
    ap.add_argument("--null-seed", type=int, default=13)
    a = ap.parse_args()

    axes = [parse_axis(s) for s in a.axes]
    production = tuple(float(v) for v in a.production.split(","))
    if len(production) != len(axes):
        raise SystemExit(f"REFUSED: --production has {len(production)} values for "
                         f"{len(axes)} axes")
    rec = sweep(a.strategy, axes, production, a.coverage_min, a.repro_min, a.min_n)
    if a.null_perms > 0:
        attach_null(rec, a.strategy, axes, a.min_n, a.null_perms, a.null_seed)
        pn = rec["permutation_null"]
        print(f"permutation null ({pn['n_perms']} perms): observed best "
              f"{pn['observed_best_is_sharpe']} | null q95 "
              f"{pn['null_max_is_sharpe_quantiles'].get('0.95')} | p {pn['p_value_best']}")
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    # B2643: the offline Table D ships WITH the artifact, unconditionally.
    table_path = Path(a.out).with_suffix(".md")
    table_path.write_text(render_table(rec), encoding="utf-8")

    print(f"{rec['strategy']}: reproduction {rec['reproduction']:.4f} | coverage "
          f"{rec['evidence']['coverage']:.4f} | {rec['cells_graded']} of "
          f"{rec['cells_total']} cells graded | {rec['trials_searched']} trials")
    for c in rec["ranked"][:5]:
        print(f"   {c['levels']}  IS sharpe {c['is_sharpe']:.3f}  "
              f"exit {c['best_exit']}  n={c['is_trades']}")
    print(f"wrote {a.out}  (holdout NOT read)")
    print(f"wrote {table_path}  (TABLE D, offline form)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
