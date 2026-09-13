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
# S6-B2732a: the R5 baseline is the DEFAULT, no longer the only cube.
# A depth config lands its own cube and the battery grades THAT one
# (the L754 portability contract; the family-hardcoded form was the
# first instance and this is its parameterization).
R5_DIR = ROOT / "output_r5_merged_1_7"
CUBE = R5_DIR / "trade_exit_detail.csv"
TRADE_LOG = R5_DIR / "trade_log.csv"
# S6-B2804: the CURRENT gate's required sweep leg, per direction.
# B2075 (owner-approved 2026-08-23) restored it as REQUIRED after B1202
# had let bos alone satisfy both clauses of the old gate.
SWEEP_KEYS = {"long": "smc_liquidity_swept_dn",
              "short": "smc_liquidity_swept_up"}
ARM_KEYS = {"long": ("smc_choch_bullish", "smc_bos_bullish"),
            "short": ("smc_choch_bearish", "smc_bos_bearish")}
B_AXES = [("monthly_momentum_6m", "ge"), ("bb_20_20_bandwidth", "le"),
          ("vp_close_near_poc_pct", "le"), ("atr_pct", "le"),
          ("bullish_engulfing", "eq_true_long"), ("gap_up_2pct", "eq_false")]


def build(cube_dir: Path | None = None, strat: str = STRAT,
          keys: list[str] | None = None) -> pd.DataFrame:
    """The graded frame for `strat` from `cube_dir` (default: the R5 baseline).

    S6-B2752a: `strat` and `keys` are PARAMETERS rather than module constants,
    so hub-2's grader imports this builder instead of copying it. That is L799
    applied at the moment it would have been broken again - a new grader written
    beside an existing one inherits none of its lessons unless it inherits its
    CODE, and this builder already carries the fail-closed path check, the
    per-fire de-duplication and the bool->float coercion that a fresh copy would
    have had to rediscover. Defaults reproduce hub-1 exactly.
    """
    trade_log = (cube_dir / "trade_log.csv") if cube_dir else TRADE_LOG
    cube_csv = (cube_dir / "trade_exit_detail.csv") if cube_dir else CUBE
    for _p in (trade_log, cube_csv):
        if not _p.exists():
            raise SystemExit(f"REFUSED: {_p} does not exist (fail closed)")
    if keys is None:
        keys = ([k for k, _ in B_AXES]
                + [k for pair in ARM_KEYS.values() for k in pair]
                + list(SWEEP_KEYS.values()))
    tl = pd.read_csv(trade_log, low_memory=False,
                     usecols=["strategy", "ticker", "entry_date", "direction",
                              "signals_at_entry"])
    fam = tl[tl.strategy == strat].drop_duplicates(["ticker", "entry_date"]).copy()
    sigs = [_parse(s) for s in fam["signals_at_entry"]]
    for k in keys:
        fam[k] = pd.to_numeric(
            pd.Series([float(d.get(k)) if isinstance(d.get(k), bool)
                       else d.get(k) for d in sigs]), errors="coerce").values
    fam = fam.drop(columns=["signals_at_entry"])
    cube = pd.read_csv(cube_csv, low_memory=False,
                       usecols=["strategy", "ticker", "entry_date",
                                "exit_method", "pnl_pct", "hold_days"])
    cube = cube[cube.strategy == strat]
    m = cube.merge(fam, on=["strategy", "ticker", "entry_date"], how="left")
    m["entry_date"] = pd.to_datetime(m["entry_date"], errors="coerce").dt.date
    return m


def current_gate_rows(m: pd.DataFrame) -> pd.DataFrame:
    """The rows the CURRENT gate would fire on - a SELECTION, not an estimate.

    current: swept AND (choch OR bos), per leg (screener.py:4722).
    Exact on two counts, both READ rather than assumed: exits are per-trade
    independent (exit_strategies.py:4), so dropping rows changes no survivor;
    and the pre-B2075 gate was strictly LOOSER, so every trade the current
    rule would take is already recorded here. Nothing is missing.
    """
    parts = []
    for leg, (ck, bk) in ARM_KEYS.items():
        sk = SWEEP_KEYS[leg]
        sub = m[(m.direction == leg) & (m[sk] == 1.0)
                & ((m[ck] == 1.0) | (m[bk] == 1.0))]
        parts.append(sub)
    return pd.concat(parts) if parts else m.iloc[0:0]


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
    ap.add_argument("--current-gate-only", action="store_true",
                    help="grade only the fires the CURRENT gate would "
                         "take. The R5 cube predates B2075, so without "
                         "this the grid ranks an OR-gate population "
                         "(S6-B2802)")
    ap.add_argument("--out", required=True)
    # S6-B2732a: the cube to grade, and this config's knob IDENTITY.
    # The knobs are NOT search axes here - they are baked into the cube
    # by the engine run, exactly as --swing-length identifies a breaker
    # config rather than sweeping one. They are recorded so the grid
    # names the config it graded.
    ap.add_argument("--cube", default="",
                    help="cube DIRECTORY to grade; default the R5 baseline")
    ap.add_argument("--swing-length", type=int, default=None)
    ap.add_argument("--liquidity-range-pct", type=float, default=None)
    ap.add_argument("--event-recency-bars", type=int, default=None)
    a = ap.parse_args()
    t0 = time.time()

    _cube_dir = Path(a.cube).resolve() if a.cube else None
    if _cube_dir is not None and _cube_dir.is_file():
        _cube_dir = _cube_dir.parent
    _is_r5 = _cube_dir is None or _cube_dir == R5_DIR.resolve()
    m = build(None if _is_r5 else _cube_dir)
    fires = m.drop_duplicates(["ticker", "entry_date"])
    # S6-B2732a: the R5 reproduction gate binds the BASELINE only. A
    # variant cube fires a DIFFERENT set by construction - changing a
    # producer knob is the whole point of the depth leg - so comparing
    # it to the R5 pre-gate count would refuse every config that did
    # what it was asked to do. Recorded either way; never silent.
    if _is_r5:
        pre = json.loads((ROOT / "output_audit" / "b2690_smc_pregate.json").read_text(encoding="utf-8"))
        want = pre["members"][STRAT]["n_trades"]
        if len(fires) != want:
            raise SystemExit(f"REFUSED: {len(fires)} unique fires != pre-gate {want}")
        _repro = f"R5 BASELINE reproduction OK: {len(fires)} fires == pre-gate {want}"
    else:
        _repro = ("VARIANT-CUBE-NO-R5-REPRODUCTION: this cube was produced at "
                  f"knobs swing_length={a.swing_length} "
                  f"liquidity_range_pct={a.liquidity_range_pct} "
                  f"event_recency_bars={a.event_recency_bars}, so its fire set "
                  f"DIFFERS from the R5 baseline by design; own fires {len(fires)}")
    print(f"{_repro} ({time.time()-t0:.0f}s)")

    # S6-B2804: applied AFTER the reproduction gate, deliberately - the gate
    # must still bind against the cube's OWN recorded population, or a
    # filtered run could pass a gate it never faced.
    gate_note = "ALL recorded fires (the cube's own population)"
    if a.current_gate_only:
        before = len(fires)
        m = current_gate_rows(m)
        fires = m.drop_duplicates(["ticker", "entry_date"])
        gate_note = (f"CURRENT-GATE ONLY: {len(fires)} of {before} recorded "
                     "fires satisfy swept AND (choch OR bos) per leg. The "
                     "pre-B2075 gate was strictly looser, so this is the "
                     "COMPLETE set the current rule would take, not a sample")
        print(gate_note)

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
           # B2774: an artifact names its CUBE, not its INSTRUMENT - so two
           # JSONs about one cube look comparable and are not. I compared a
           # grid_auto "0 graded" against this grader and warned the owner of
           # a low yield; this grader then graded 528 cells. Stamp the
           # generator so the next reader cannot make that comparison blind.
           "generator": "scripts/smc_lsr_step1.py",
           "cube": str(_cube_dir) if _cube_dir else str(R5_DIR),
           "config": {"P1_swing_length": a.swing_length,
                      "P2_liquidity_range_pct": a.liquidity_range_pct,
                      "P3_event_recency_bars": a.event_recency_bars},
           "reproduction": _repro,
           "population": gate_note,

           "ruling": "owner band word 'Lets proceed with step 1' 2026-09-12 (S6-B2691a)",
           "design": "9 depth cells (leg x arm) + 6 breadth axes one-at-a-time on the "
                     "production base; IS-only; holdout untouched; npt barred from ranking",
           "reproduction_fires": int(len(fires)),
           "cells_graded": len(graded),
           "permutation_null": pn,
           # B2768 (owner-approved 2026-09-13): grid-stage BH-FDR,
           # REPORT-ONLY - changes no gate and no ranking (B1608).
           # B2775: this grader establishes significance with a
           # PERMUTATION NULL, not per-row p-values, so hand it in -
           # otherwise the report says graded=0 while hundreds of cells
           # were graded, which is the silent-loss shape the partition
           # exists to stop (S6-B2773, found on its first live run).
           "multiplicity": rc.bh_fdr_report(rows, permutation_null=pn),
           "step1_ranking": ranked[:80], "rows": rows,
           "holdout_read": "NOT FIRED - Step 2 needs its own owner word (11.2c)"}
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
