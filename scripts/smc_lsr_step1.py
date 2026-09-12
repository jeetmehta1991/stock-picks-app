#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""B2694 (S6-B2691a, owner band word 'Lets proceed with step 1' 2026-09-12):
smc_liquidity_sweep_reversal STEP-1 - the owner-approved 11-row band.

DESIGN (pre-registered by the approved Table A + 11.2b3):
  DEPTH cells: leg {both, long, short} x confirmation_arm {either(prod),
    choch_only, bos_only} = 9 cells, each graded across all exits (IS only).
    Arm reconstruction from persisted booleans: choch_only keeps fires where
    the leg's choch key is True; bos_only likewise (subset-safe - the
    production OR admitted both).
  BREADTH cells: each B-axis independently on the PRODUCTION base (both
    legs, either arm), levels = retention quantiles (QUANTS) of the axis
    over the base's IS fires; bullish_engulfing == True applies to the LONG
    leg only (B5's Table A term); gap_up_2pct == False on the full base.
  GRADING: IS sharpe (min 10), rc.in_sample only - HOLDOUT UNTOUCHED.
  npt excluded from ranking. Reproduction gate: unique fires must equal the
  B2690 pre-gate count (fail-closed).
  MULTIPLICITY: the breadth sub-grid's best is priced by a permutation null
  (magnitude columns shuffled across fires, --null-perms, SYNTHETIC maxima).
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
from breadth_step1_grid import QUANTS, BARRED_EXIT, _parse  # noqa: E402

STRAT = "smc_liquidity_sweep_reversal"
CUBE = ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv"
TRADE_LOG = ROOT / "output_r5_merged_1_7" / "trade_log.csv"
ARM_KEYS = {"long": ("smc_choch_bullish", "smc_bos_bullish"),
            "short": ("smc_choch_bearish", "smc_bos_bearish")}
B_AXES = [("monthly_momentum_6m", "ge"), ("bb_20_20_bandwidth", "le"),
          ("vp_close_near_poc_pct", "le"), ("atr_pct", "le"),
          ("bullish_engulfing", "eq_true_long"), ("gap_up_2pct", "eq_false")]


def build() -> pd.DataFrame:
    keys = [k for k, _ in B_AXES] + [k for pair in ARM_KEYS.values() for k in pair]
    tl = pd.read_csv(TRADE_LOG, low_memory=False,
                     usecols=["strategy", "ticker", "entry_date", "direction",
                              "signals_at_entry"])
    fam = tl[tl.strategy == STRAT].drop_duplicates(["ticker", "entry_date"]).copy()
    sigs = [_parse(s) for s in fam["signals_at_entry"]]
    for k in keys:
        fam[k] = pd.to_numeric(
            pd.Series([float(d.get(k)) if isinstance(d.get(k), bool)
                       else d.get(k) for d in sigs]), errors="coerce").values
    fam = fam.drop(columns=["signals_at_entry"])
    cube = pd.read_csv(CUBE, low_memory=False,
                       usecols=["strategy", "ticker", "entry_date",
                                "exit_method", "pnl_pct", "hold_days"])
    cube = cube[cube.strategy == STRAT]
    m = cube.merge(fam, on=["strategy", "ticker", "entry_date"], how="left")
    m["entry_date"] = pd.to_datetime(m["entry_date"], errors="coerce").dt.date
    return m


def grade_cells(m: pd.DataFrame, min_n: int) -> list[dict]:
    rows = []

    def emit(tag, axis, level, sub):
        for ex, cell in sub.groupby("exit_method"):
            si = rc.in_sample(cell)
            r = rc._sharpe(si["pnl_pct"].values, si["hold_days"], min_n=min_n)
            if r is None:
                continue
            rows.append({"is_sharpe": r["sharpe"], "is_ci_lo": r.get("ci_lo"),
                         "cell": tag, "axis": axis, "level": level, "exit": ex,
                         "is_n": int(len(si)),
                         "full_n_count_only": int(len(cell)),
                         "npt_barred": ex == BARRED_EXIT})

    # DEPTH: leg x arm
    for leg in ("both", "long", "short"):
        base = m if leg == "both" else m[m.direction == leg]
        for arm in ("either", "choch_only", "bos_only"):
            if arm == "either":
                sub = base
            else:
                want = 0 if arm == "choch_only" else 1
                parts = []
                for lg, (ck, bk) in ARM_KEYS.items():
                    key = (ck, bk)[want]
                    part = base[(base.direction == lg) & (base[key] == 1.0)]
                    parts.append(part)
                sub = pd.concat(parts) if parts else base.iloc[0:0]
            emit(f"depth:{leg}/{arm}", None, None, sub)

    # BREADTH: one at a time on the production base
    is_fires = rc.in_sample(m).drop_duplicates(["ticker", "entry_date"])
    for key, op in B_AXES:
        if op in ("eq_true_long", "eq_false"):
            if op == "eq_true_long":
                sub = m[(m.direction == "long") & (m[key] == 1.0)]
                emit(f"breadth:{key}", key, "True(long)", sub)
            else:
                sub = m[m[key] == 0.0]
                emit(f"breadth:{key}", key, "False", sub)
            continue
        vals = is_fires[key]
        cov = float(vals.notna().mean())
        if cov < 0.98:
            rows.append({"is_sharpe": None, "cell": f"SKIP:{key}",
                         "axis": key, "level": f"coverage {cov:.3f}",
                         "exit": None, "is_n": 0, "full_n_count_only": 0,
                         "npt_barred": False})
            continue
        for lev in sorted(set(np.round(vals.quantile(QUANTS), 4))):
            mask = (m[key] >= lev) if op == "ge" else (m[key] <= lev)
            emit(f"breadth:{key}", key, float(lev), m[mask & m[key].notna()])
    return rows


def breadth_null(m, min_n, n_perms, seed) -> list:
    """Permutation null for the BREADTH sub-grid only (SYNTHETIC maxima)."""
    rng = np.random.default_rng(seed)
    num_keys = [k for k, op in B_AXES if op in ("ge", "le")]
    IS = rc.in_sample(m)
    fires = (IS.drop_duplicates(["ticker", "entry_date"])
               [["ticker", "entry_date"] + num_keys].reset_index(drop=True))
    base = IS.drop(columns=num_keys)
    maxima = []
    for _ in range(n_perms):
        idx = rng.permutation(len(fires))
        shuf = fires[["ticker", "entry_date"]].join(
            fires.loc[idx, num_keys].reset_index(drop=True))
        mm = base.merge(shuf, on=["ticker", "entry_date"], how="left")
        best = None
        for key, op in B_AXES:
            if op not in ("ge", "le"):
                continue
            vals = shuf[key]
            for lev in sorted(set(np.round(vals.quantile(QUANTS), 4))):
                mask = (mm[key] >= lev) if op == "ge" else (mm[key] <= lev)
                for _ex, cell in mm[mask & mm[key].notna()].groupby("exit_method"):
                    r = rc._sharpe(cell["pnl_pct"].values, cell["hold_days"], min_n=min_n)
                    if r and (best is None or r["sharpe"] > best):
                        best = r["sharpe"]
        maxima.append(best)
    return maxima


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--null-perms", type=int, default=100)
    ap.add_argument("--null-seed", type=int, default=13)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()

    m = build()
    fires = m.drop_duplicates(["ticker", "entry_date"])
    pre = json.loads((ROOT / "output_audit" / "b2690_smc_pregate.json").read_text(encoding="utf-8"))
    want = pre["members"][STRAT]["n_trades"]
    if len(fires) != want:
        raise SystemExit(f"REFUSED: {len(fires)} unique fires != pre-gate {want}")
    print(f"reproduction OK: {len(fires)} fires ({time.time()-t0:.0f}s)")

    rows = grade_cells(m, a.min_n)
    graded = [r for r in rows if r["is_sharpe"] is not None]
    ranked = sorted((r for r in graded if not r["npt_barred"]),
                    key=lambda r: -r["is_sharpe"])
    print(f"{len(graded)} graded cells ({time.time()-t0:.0f}s)")

    pn = {}
    if a.null_perms > 0:
        breadth_best = max((r["is_sharpe"] for r in ranked
                            if r["cell"].startswith("breadth:") and r["axis"]
                            and r["level"] not in ("True(long)", "False")),
                           default=None)
        maxima = breadth_null(m, a.min_n, a.null_perms, a.null_seed)
        valid = [x for x in maxima if x is not None]
        p = ((1 + sum(1 for x in valid if x >= breadth_best)) / (len(valid) + 1)
             if (breadth_best is not None and valid) else None)
        pn = {"provenance": "SYNTHETIC - rng permutations; prices the numeric "
                            "breadth search, never performance",
              "n_perms": a.null_perms, "seed": a.null_seed,
              "observed_breadth_best_is_sharpe": breadth_best,
              "null_max_quantiles": {str(q): round(float(np.quantile(valid, q)), 3)
                                     for q in (0.5, 0.9, 0.95, 0.99)} if valid else {},
              "p_value_best": round(p, 4) if p is not None else None}
        print(f"breadth null: best {breadth_best} vs q95 "
              f"{pn['null_max_quantiles'].get('0.95')} p {pn['p_value_best']} "
              f"({time.time()-t0:.0f}s)")

    rec = {"strategy": STRAT,
           "ruling": "owner band word 'Lets proceed with step 1' 2026-09-12 (S6-B2691a)",
           "design": "9 depth cells (leg x arm) + 6 breadth axes one-at-a-time on the "
                     "production base; IS-only; holdout untouched; npt barred from ranking",
           "reproduction_fires": int(len(fires)),
           "cells_graded": len(graded),
           "permutation_null": pn,
           "step1_ranking": ranked[:80], "rows": rows,
           "holdout_read": "NOT FIRED - Step 2 needs its own owner word (11.2c)"}
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
