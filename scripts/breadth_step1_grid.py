#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""B2673 (S6-B2671b, owner word 'Proceed' 2026-09-11): the BREADTH Step-1 grid,
parameterized by strategy (second breadth grid -> the L754 contract extraction;
the first, institutional_companion_grid.py, is family-hardcoded).

WHAT IT DOES - offline, zero engine hours, HOLDOUT UNTOUCHED:
  - loads ONE strategy's recorded R5 fires + signals_at_entry,
  - applies an optional DEPTH base filter (the already-admitted line),
  - REPRODUCTION GATE (fail-closed): the base cell at --repro-exit must
    reproduce the admission artifact's is_sharpe/is n, or the run refuses -
    the offline_level_sweep class,
  - sweeps each breadth axis at retention quantiles derived from the IS BASE
    fires only (holdout signal values never read for band construction),
  - grades IN-SAMPLE ONLY (rc.in_sample; Step-1 is a ranked list, no gates,
    min-trades >= 10 per owner ruling B1608). Holdout pnl is never loaded
    into a statistic; full-period row COUNTS only, for the power projection
    against the trade-count gates (15 holdout / 75 full).
  - next_pivot_target rows are graded but EXCLUDED from the ranked list per
    the promoted npt-bar (runbook 11.2b2).

COVERAGE RULE per axis: skipped (and recorded) when present on < 98pct of the
base fires - a level over a sparse axis silently drops the uncovered rows.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import roster_core as rc  # noqa: E402

CUBE = ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv"
TRADE_LOG = ROOT / "output_r5_merged_1_7" / "trade_log.csv"
MIN_COVERAGE = 0.98
QUANTS = (0.2, 0.4, 0.6, 0.8)
BARRED_EXIT = "next_pivot_target"


def _parse(s):
    try:
        return json.loads(s)
    except Exception:
        try:
            return ast.literal_eval(s)
        except Exception:
            return {}


def _axis_spec(txt):
    # "key:ge" / "key:le" / "key:eq_true"
    key, op = txt.rsplit(":", 1)
    assert op in ("ge", "le", "eq_true"), op
    return key, op


def build_frame(strategy: str, depth: str | None, axis_keys: list[str]):
    """B2678: the joined fires+cube frame both steps read - ONE loader so
    Step-1 and Step-2 cannot drift. Returns (m, depth_tuple)."""
    tl = pd.read_csv(TRADE_LOG, low_memory=False,
                     usecols=["strategy", "ticker", "entry_date", "signals_at_entry"])
    fam = tl[tl.strategy == strategy].drop_duplicates(["ticker", "entry_date"]).copy()
    if fam.empty:
        raise SystemExit(f"REFUSED: no fires for {strategy}")
    sigs = [_parse(s) for s in fam["signals_at_entry"]]
    need = list(axis_keys)
    dep = None
    if depth:
        dk, dop, dlev = depth.split(":")
        dep = (dk, dop, float(dlev))
        need = [dk] + need
    for k in dict.fromkeys(need):
        fam[k] = pd.to_numeric(pd.Series([d.get(k) if not isinstance(d.get(k), bool)
                                          else float(d.get(k)) for d in sigs]),
                               errors="coerce").values
    fam = fam.drop(columns=["signals_at_entry"])
    cube = pd.read_csv(CUBE, low_memory=False,
                       usecols=["strategy", "ticker", "entry_date",
                                "exit_method", "pnl_pct", "hold_days"])
    cube = cube[cube.strategy == strategy]
    m = cube.merge(fam, on=["strategy", "ticker", "entry_date"], how="left")
    m["entry_date"] = pd.to_datetime(m["entry_date"], errors="coerce").dt.date
    if dep:
        dk, dop, dlev = dep
        keepm = (m[dk] >= dlev) if dop == "ge" else (m[dk] <= dlev)
        m = m[keepm & m[dk].notna()]
    return m, dep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--depth", default=None,
                    help="base filter key:op:level, e.g. xs_momentum_12_1:ge:0.529")
    ap.add_argument("--axes", required=True,
                    help="comma-separated key:op list (op in ge|le|eq_true)")
    ap.add_argument("--repro-exit", default="time_stop_10d")
    ap.add_argument("--repro-artifact", default=None,
                    help="admission artifact whose is_sharpe the base must reproduce")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    axes = [_axis_spec(x) for x in a.axes.split(",")]

    m, _dep = build_frame(a.strategy, a.depth, [k for k, _ in axes])
    print(f"frame ready: cube rows {len(m):,} after depth base ({time.time()-t0:.0f}s)")

    # ---- REPRODUCTION GATE (fail-closed) ------------------------------------
    base_cell = m[m.exit_method == a.repro_exit]
    bi = rc.in_sample(base_cell)
    br = rc._sharpe(bi["pnl_pct"].values, bi["hold_days"], min_n=10)
    if br is None:
        raise SystemExit("REFUSED: base cell ungradable")
    repro = {"exit": a.repro_exit, "base_is_sharpe": br["sharpe"], "base_is_n": int(len(bi)),
             "base_full_n": int(base_cell.shape[0])}
    if a.repro_artifact:
        art = json.loads(Path(a.repro_artifact).read_text(encoding="utf-8"))
        want = next(r for r in art["results"] if r["strategy"] == a.strategy)
        repro["artifact_is_sharpe"] = want["is_sharpe"]
        repro["artifact_full_n"] = want["full_period_n"]
        if abs(want["is_sharpe"] - br["sharpe"]) > 1e-3 or want["full_period_n"] != repro["base_full_n"]:
            raise SystemExit(f"REFUSED: reproduction mismatch {repro}")
    print(f"reproduction OK: {repro}")

    # ---- band from IS base fires only ---------------------------------------
    is_all = rc.in_sample(m)
    base_fires_is = is_all.drop_duplicates(["ticker", "entry_date"])
    rows, skips = [], []
    trials = 0
    for key, op in axes:
        vals = base_fires_is[key]
        cov = float(vals.notna().mean())
        if cov < MIN_COVERAGE:
            skips.append({"axis": key, "coverage": round(cov, 3)})
            continue
        if op == "eq_true":
            levels = [1.0]
        else:
            levels = sorted(set(np.round(vals.quantile(QUANTS), 4)))
        for lev in levels:
            if op == "ge":
                mask = m[key] >= lev
            elif op == "le":
                mask = m[key] <= lev
            else:
                mask = m[key] == 1.0
            sub_all = m[mask & m[key].notna()]
            for ex, sub in sub_all.groupby("exit_method"):
                trials += 1
                si = rc.in_sample(sub)
                r = rc._sharpe(si["pnl_pct"].values, si["hold_days"], min_n=10)
                if r is None:
                    continue
                rows.append({
                    "is_sharpe": r["sharpe"],          # ranking key FIRST (L558)
                    "is_ci_lo": r.get("ci_lo"),
                    "axis": key, "op": op, "level": float(lev), "exit": ex,
                    "is_n": int(len(si)),
                    "full_n_count_only": int(len(sub)),
                    "is_retention": round(len(si) / max(len(is_all[is_all.exit_method == ex]), 1), 3),
                    "npt_barred": ex == BARRED_EXIT})
    ranked = sorted((r for r in rows if not r["npt_barred"]),
                    key=lambda r: -r["is_sharpe"])
    rec = {"strategy": a.strategy, "depth_base": a.depth,
           "axes": [{"key": k, "op": o} for k, o in axes],
           "quants": list(QUANTS), "min_coverage": MIN_COVERAGE,
           "window": "IS only (< 2025-05-05); holdout untouched - Step 2 needs its own owner word",
           "reproduction": repro, "trials": trials, "graded": len(rows),
           "skipped_axes": skips,
           "step1_ranking": ranked[:60], "rows": rows}
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"{trials:,} trials | {len(rows):,} graded | ranked head "
          f"{[round(r['is_sharpe'], 3) for r in ranked[:5]]} -> {a.out} "
          f"({time.time()-t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
