#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""B2698 (owner option (b), verbatim 2026-09-12: "first re-sweep it under a
widened coverage rule (grade only the covered 94.2% with the gap disclosed)"):

monthly_momentum_6m on smc_liquidity_sweep_reversal hub-1 - the axis the
b2694 Step-1 grid COVERAGE-SKIPPED at 0.942 < 0.98 (the screen's rank-1
companion, until now UNTESTED on this hub).

WIDENED COVERAGE RULE (this run only, owner-ruled): the sweep grades ONLY
fires where monthly_momentum_6m is non-null (the covered 94.2% of IS fires);
the uncovered gap is EXCLUDED from both the observed arm and the null arm and
is disclosed on the artifact's face. The verdict binds the covered
subpopulation, not the full base.

Same design as the b2694 breadth cells otherwise: production base (both legs,
either arm), levels = retention quantiles (QUANTS) of the axis over the
covered IS fires, IS-only grading (holdout UNTOUCHED), npt barred from
ranking, and the search priced by its own single-axis permutation null
(momentum values shuffled across covered fires; SYNTHETIC maxima).
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
from breadth_step1_grid import QUANTS, BARRED_EXIT  # noqa: E402
from smc_lsr_step1 import build, STRAT  # noqa: E402

AXIS = "monthly_momentum_6m"


def grade(base: pd.DataFrame, levels: list[float], min_n: int) -> list[dict]:
    rows = []
    for lev in levels:
        sub = base[base[AXIS] >= lev]
        for ex, cell in sub.groupby("exit_method"):
            si = rc.in_sample(cell)
            r = rc._sharpe(si["pnl_pct"].values, si["hold_days"], min_n=min_n)
            if r is None:
                continue
            rows.append({"is_sharpe": r["sharpe"], "is_ci_lo": r.get("ci_lo"),
                         "cell": f"breadth:{AXIS}", "axis": AXIS,
                         "level": float(lev), "exit": ex,
                         "is_n": int(len(si)),
                         "full_n_count_only": int(len(cell)),
                         "npt_barred": ex == BARRED_EXIT})
    return rows


def null_maxima(is_cov: pd.DataFrame, levels, min_n, n_perms, seed) -> list:
    """Single-axis permutation null: shuffle the momentum values ACROSS the
    covered IS fires, re-run the identical 4-level x exit search, keep each
    permutation's maximum IS sharpe. SYNTHETIC - prices the search only."""
    rng = np.random.default_rng(seed)
    fires = is_cov.drop_duplicates(["ticker", "entry_date"])
    key = fires["ticker"].astype(str) + "|" + fires["entry_date"].astype(str)
    vals = fires[AXIS].to_numpy()
    fire_idx = {k: i for i, k in enumerate(key)}
    row_key = (is_cov["ticker"].astype(str) + "|"
               + is_cov["entry_date"].astype(str)).map(fire_idx).to_numpy()
    pnl = is_cov["pnl_pct"].to_numpy()
    hold = is_cov["hold_days"].to_numpy()
    exits = is_cov["exit_method"].to_numpy()
    maxima = []
    for _ in range(n_perms):
        shuf = vals[rng.permutation(len(vals))][row_key]
        best = None
        for lev in levels:
            mask = shuf >= lev
            sub_ex = exits[mask]
            for ex in np.unique(sub_ex):
                sel = mask.copy()
                sel[mask] = sub_ex == ex
                r = rc._sharpe(pnl[sel], hold[sel], min_n=min_n)
                if r and (best is None or r["sharpe"] > best):
                    best = r["sharpe"]
        maxima.append(best)
    return maxima


def render_md(rec: dict, out_md: Path) -> None:
    """STANDARD offline Table D form (one column per axis, bands in header) -
    the b2694 shape, rendered as an ADDENDUM carrying the one re-swept axis."""
    lines = [
        "# TABLE D ADDENDUM (OFFLINE FORM, standard shape) - "
        "smc_liquidity_sweep_reversal Step-1: monthly_momentum_6m re-sweep",
        "",
        f"{rec['cells_graded']} graded cells; reproduction "
        f"{rec['reproduction_fires']} fires = b2690; holdout NOT read; "
        "no gates (B1608); npt excluded from ranking.",
        f"WIDENED COVERAGE RULE (owner option (b) 2026-09-12): coverage "
        f"{rec['coverage']['is_fire_coverage']:.3f} of IS fires - the "
        f"{rec['coverage']['excluded_gap_pct']:.1f}% uncovered gap is EXCLUDED "
        "from both arms; the verdict binds the covered subpopulation only. "
        "This axis was COVERAGE-SKIPPED in b2694 (0.942 < 0.98) and is swept "
        "here on the owner's word.",
        f"BANDS SWEPT - breadth numeric (retention quantiles on covered IS "
        f"fires, derived at grid time): {AXIS} in "
        f"{{{', '.join(str(v) for v in rec['levels'])}}}. '-' = axis not "
        "applied (production behavior); single-axis design.",
        f"Single-axis null: best {rec['permutation_null']['observed_best_is_sharpe']} vs q95 "
        f"{rec['permutation_null']['null_max_quantiles'].get('0.95')}, p "
        f"{rec['permutation_null']['p_value_best']} "
        f"({rec['permutation_null']['n_perms']} perms, SYNTHETIC).",
        "",
        "| rank | leg | confirmation_arm | monthly_momentum_6m | bb_20_20_bandwidth "
        "| vp_close_near_poc_pct | atr_pct | bullish_engulfing | gap_up_2pct "
        "| exit | IS sharpe | IS ci_lo | IS n | full n |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    ranked = [r for r in rec["rows"] if not r["npt_barred"]]
    ranked.sort(key=lambda r: -r["is_sharpe"])
    for i, r in enumerate(ranked[:25], 1):
        lines.append(
            f"| {i} | both | either | >={r['level']} | - | - | - | - | - "
            f"| {r['exit']} | {r['is_sharpe']:.3f} | "
            f"{'' if r['is_ci_lo'] is None else round(r['is_ci_lo'], 3)} "
            f"| {r['is_n']} | {r['full_n_count_only']} |")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


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

    IS = rc.in_sample(m)
    is_fires = IS.drop_duplicates(["ticker", "entry_date"])
    cov = float(is_fires[AXIS].notna().mean())
    cov_fires = is_fires[is_fires[AXIS].notna()]
    levels = sorted(set(np.round(cov_fires[AXIS].quantile(QUANTS), 4)))
    print(f"coverage {cov:.4f} | covered IS fires {len(cov_fires)}/{len(is_fires)} "
          f"| levels {levels}")

    base = m[m[AXIS].notna()]          # covered fires, full period (full_n)
    rows = grade(base, levels, a.min_n)
    ranked = sorted((r for r in rows if not r["npt_barred"]),
                    key=lambda r: -r["is_sharpe"])
    best = ranked[0]["is_sharpe"] if ranked else None
    print(f"{len(rows)} graded cells; observed best {best} ({time.time()-t0:.0f}s)")

    is_cov = IS[IS[AXIS].notna()]
    maxima = null_maxima(is_cov, levels, a.min_n, a.null_perms, a.null_seed)
    valid = [x for x in maxima if x is not None]
    p = ((1 + sum(1 for x in valid if x >= best)) / (len(valid) + 1)
         if (best is not None and valid) else None)
    pn = {"provenance": "SYNTHETIC - rng permutations; prices the single-axis "
                        "level search on the covered subpopulation, never performance",
          "n_perms": a.null_perms, "seed": a.null_seed,
          "observed_best_is_sharpe": best,
          "null_max_quantiles": {str(q): round(float(np.quantile(valid, q)), 3)
                                 for q in (0.5, 0.9, 0.95, 0.99)} if valid else {},
          "p_value_best": round(p, 4) if p is not None else None}
    print(f"null: best {best} vs q95 {pn['null_max_quantiles'].get('0.95')} "
          f"p {pn['p_value_best']} ({time.time()-t0:.0f}s)")

    rec = {"strategy": STRAT, "axis": AXIS,
           "ruling": "owner option (b) verbatim 2026-09-12: 're-sweep it under a "
                     "widened coverage rule (grade only the covered 94.2% with "
                     "the gap disclosed)' - S6-B2698",
           "coverage": {"is_fire_coverage": round(cov, 4),
                        "covered_is_fires": int(len(cov_fires)),
                        "total_is_fires": int(len(is_fires)),
                        "excluded_gap_pct": round((1 - cov) * 100, 1),
                        "rule": "WIDENED for this run only (owner word); the "
                                "0.98 floor stands elsewhere; gap fires are in "
                                "NEITHER arm - verdict binds the covered "
                                "subpopulation only"},
           "b2694_disposition": "this axis was COVERAGE-SKIPPED in "
                                "b2694_smc_lsr_step1.json (0.942 < 0.98); "
                                "this artifact supersedes UNTESTED with a "
                                "priced verdict under the disclosed rule",
           "design": "production base (both legs, either arm); levels = "
                     "retention quantiles of covered IS fires; IS-only; "
                     "holdout untouched; npt barred from ranking",
           "reproduction_fires": int(len(fires)),
           "levels": [float(v) for v in levels],
           "cells_graded": len(rows),
           "permutation_null": pn,
           "step1_ranking": ranked[:40], "rows": rows,
           "holdout_read": "NOT FIRED - Step 2 needs its own owner word (11.2c)"}
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    render_md(rec, Path(a.out).with_suffix(".md"))
    print(f"wrote {a.out} + standard-form .md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
