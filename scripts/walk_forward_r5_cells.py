"""R5 (strategy x exit) CELL-level walk-forward for the 1A-alpha gate.

Source attribution (per CHECKLIST #77):
  - Cube: output_r5_merged_1_7/trade_exit_detail.csv (the merged 7-batch R5 cube)
  - Cell set: either the DEC-426 5-Gate shortlist
    (output_optimization_candidates_2026_07_25/exit_method_analysis.json
    layer_2_per_strategy_exit_cell) OR --all-cells = every (strategy x exit)
    cell with in-sample n >= --min-n from exit_strategy_comparison.csv.
  - Method: DEC-505 4-fold expanding-window, disjoint 1y OOS -- the SAME folds +
    per-cell Sharpe as scripts/walk_forward_batch414_cells.py (which is hardcoded
    to the R4 cube + 9 R4-era winners). This is the R5 generalization: read the
    current cube + a configurable cell set, evaluated by groupby in one pass.
  - Owner gate (CLAUDE.md): >=1 (strategy x exit) cell with rules-only OOS
    Sharpe >= 0.7 at OOS n >= 30 in >=1 fold for the $300 Phase 1B-alpha budget.

Multiple-testing note: scanning all ~4.7k n>=30 cells x 4 folds inflates the
best-of-folds false-positive rate. So this reports BOTH the loose count (>=0.7
in >=1 fold) AND the robust count (>=0.7 in >=2 folds) -- the robust count is
the multiple-testing-aware read. It does NOT weaken any threshold.

Usage:
  python scripts/walk_forward_r5_cells.py                 # 5-Gate shortlist
  python scripts/walk_forward_r5_cells.py --all-cells     # every n>=30 cell
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent

# DEC-505 4-fold expanding-window, disjoint 1y OOS (identical to
# walk_forward_batch414_cells.py). Warmup 1y 2021-05-05 -> 2022-05-05.
FOLDS = [
    ("fold_1", date(2022, 5, 5), date(2023, 5, 5)),
    ("fold_2", date(2023, 5, 5), date(2024, 5, 5)),
    ("fold_3", date(2024, 5, 5), date(2025, 5, 5)),
    ("fold_4", date(2025, 5, 5), date(2026, 5, 5)),
]
OOS_MIN_N = 30          # per-fold statistical-power floor (criterion 9 per-regime)
GATE_SHARPE = 0.7       # 1A-alpha OOS Sharpe threshold


def _friction(df, args):
    """F6 winsorize + F1 net-of-cost applied to per-trade pnl_pct at read time (B1376)."""
    w = getattr(args, "winsorize", 0.0) or 0.0
    c = getattr(args, "cost_bps", 0.0) or 0.0
    if w > 0:
        df["pnl_pct"] = df["pnl_pct"].clip(-w, w)
    if c > 0:
        df["pnl_pct"] = df["pnl_pct"] - c / 100.0   # bps -> pct (20bps = 0.20%)
    if w > 0 or c > 0:
        print(f"[INFO] friction applied: winsorize=+/-{w} cost={c}bps")
    return df


def _sharpe(a, hold, min_n: int | None = None):
    """B1714 P0-1: `min_n` is now EXPLICIT and defaults to OOS_MIN_N.

    Owner ruling: *"There should be no over riding my min n=10 command."*
    `roster_core` imports this function and `evaluate(min_n=...)` accepted a
    caller floor for ADMISSION - but the Sharpe itself was gated by the module
    constant OOS_MIN_N=30, a PER-FOLD WALK-FORWARD floor, silently governing a
    non-walk-forward grading path. MEASURED: n=10/20/29 returned a verdict with
    `sharpe=None`; n=30 returned a Sharpe. The 16-29 band sat between two floors
    and the caller could not move the one that bound.

    The constant remains the DEFAULT so every walk-forward caller is unchanged;
    only callers that pass a floor now get the floor they asked for.
    """
    # ANNUALIZED per-trade Sharpe, IDENTICAL to backtest/results/metrics.py::_sharpe
    # (B1371 fix): per_trade_sharpe * sqrt(252/avg_hold). The gate threshold 0.7
    # was calibrated against this annualized number; the prior version returned
    # raw per-trade mean/std, ~sqrt(trades/yr) too small, making the 0.7 bar
    # effectively require an annualized Sharpe of ~5 (owner-surfaced, only 10/4758
    # passed).
    n = len(a)
    if n < (OOS_MIN_N if min_n is None else min_n):
        return None
    std = a.std(ddof=1) if n > 1 else 0.0
    if std <= 0:
        return {"n": int(n), "sharpe": 0.0, "wr": round(float((a > 0).mean()), 3)}
    # B1589 UNITS FIX (owner ruling 2026-08-16: "252 trading").
    # `hold_days` in the cube is CALENDAR days - VERIFIED 20/20 against real
    # trades (B1588). Dividing 252 TRADING days by a CALENDAR hold mixed units
    # and understated trades_per_year by the calendar/trading ratio, measured at
    # 1.454 on 400 trades (365/252 = 1.448). Every annualised Sharpe was
    # therefore 17.1pct TOO LOW - conservative, so nothing was wrongly admitted,
    # but strategies may have been wrongly REJECTED.
    # Convert the hold to TRADING days first, then annualise on 252. This is
    # algebraically identical to 365/calendar; it is written this way because it
    # states the basis explicitly instead of hiding it in a constant.
    avg_hold = float(hold.mean()) if len(hold) > 0 else 10.0   # CALENDAR days
    avg_hold_trading = max(avg_hold * (252.0 / 365.0), 1e-9)
    trades_per_year = max(1.0, 252.0 / avg_hold_trading)
    sr_pt = float(a.mean() / std)          # per-trade Sharpe
    ann = trades_per_year ** 0.5
    sh = sr_pt * ann
    # F2 (B1378): Lo (2002, FAJ "The Statistics of Sharpe Ratios") IID standard error
    # SE(SR) = sqrt((1 + SR^2/2)/n), scaled by the SAME annualization factor so the CI
    # is on the ANNUALIZED number the 0.7 gate is applied to. Reported on every Sharpe
    # (class fix, not per-caller) because a point Sharpe at n=30-40 has a ~+/-1.6 CI and
    # is statistically indistinguishable from 0 -- ranking on the point estimate
    # over-selects noise. t/p are one-sided (H0: SR <= 0) for the BH-FDR family below.
    se_ann = math.sqrt((1.0 + 0.5 * sr_pt ** 2) / n) * ann
    tstat = sr_pt * math.sqrt(n)
    pval = 0.5 * math.erfc(tstat / math.sqrt(2.0))
    return {"n": int(n), "sharpe": round(sh, 3), "wr": round(float((a > 0).mean()), 3),
            "avg_hold": round(avg_hold, 1), "se": round(se_ann, 3),
            "ci_lo": round(sh - 1.96 * se_ann, 3), "ci_hi": round(sh + 1.96 * se_ann, 3),
            "t": round(tstat, 2), "p": pval}


def bh_fdr(pvals, q=0.05):
    """Benjamini-Hochberg (1995) FDR control -- the repo's canonical multiple-testing
    correction (B982 promoted BH-FDR over Bonferroni as a HARD gate at N>1000).
    Returns (reject_flags in ORIGINAL order, largest passing threshold).

    F3 (B1378): the loose set was selected from thousands of (strategy x exit x fold)
    comparisons with NO correction, so a chunk of it is expected to clear by chance
    alone. BH controls the expected FALSE-DISCOVERY fraction among the rejects at q."""
    m = len(pvals)
    if m == 0:
        return [], 0.0
    order = sorted(range(m), key=lambda i: pvals[i])
    kmax, thresh = 0, 0.0
    for rank, i in enumerate(order, start=1):
        if pvals[i] <= q * rank / m:
            kmax, thresh = rank, q * rank / m
    rej = [False] * m
    for rank, i in enumerate(order, start=1):
        if rank <= kmax:
            rej[i] = True
    return rej, thresh


def _validate_conditional(args) -> int:
    """A / the gate: IS-pick / OOS-measure. Per strategy, pick its best exit
    conditional-per-<by> AND unconditional on the IS folds (entry 2022-05-05 ->
    2025-05-05), then MEASURE both exit policies on the OOS fold (entry >=
    2025-05-05). A strategy's conditional override is deployable ONLY if the
    conditional OOS annualized Sharpe beats the unconditional OOS Sharpe. This
    disciplines the in-sample 87%-differ selection bias (council statistician +
    outsider lenses)."""
    import pandas as pd
    by = args.by or "regime_at_entry"
    cdir = REPO / args.cube_dir
    out = Path(args.out) if args.out else (cdir / f"validate_conditional_exit_{by}.json")
    split = date(2025, 5, 5)  # IS = folds 1-3, OOS = fold 4 (last year)
    minn = args.cond_min_n
    print(f"[INFO] validate-conditional by {by}: IS entry<{split}, OOS entry>={split}, n>={minn}")
    df = pd.read_csv(cdir / "trade_exit_detail.csv",
                     usecols=["strategy", "exit_method", by, "entry_date", "pnl_pct", "hold_days"],
                     low_memory=False)
    df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    df = _friction(df, args)
    IS, OOS = df[df.entry_date < split], df[df.entry_date >= split]

    def best_exit(sub):
        b = None
        for ex, g in sub.groupby("exit_method"):
            if len(g) < minn:
                continue
            st = _sharpe(g.pnl_pct.values, g.hold_days.values)
            if st and (b is None or st["sharpe"] > b[1]):
                b = (ex, st["sharpe"])
        return b

    rows, cond_win, cond_win_margin, evaluated = [], 0, 0, 0
    for strat in df.strategy.unique():
        iss, oos = IS[IS.strategy == strat], OOS[OOS.strategy == strat]
        u = best_exit(iss)
        if u is None:
            continue
        uncond_exit = u[0]
        cond = {}
        for val, gv in iss.groupby(by):
            b = best_exit(gv)
            if b:
                cond[val] = b[0]
        # OOS measure both policies
        ou = _sharpe(oos[oos.exit_method == uncond_exit].pnl_pct.values,
                     oos[oos.exit_method == uncond_exit].hold_days.values)
        parts = [gv[gv.exit_method == cond.get(val, uncond_exit)] for val, gv in oos.groupby(by)]
        oc_df = pd.concat(parts) if parts else oos.iloc[0:0]
        oc = _sharpe(oc_df.pnl_pct.values, oc_df.hold_days.values)
        if ou is None or oc is None:
            continue
        evaluated += 1
        delta = round(oc["sharpe"] - ou["sharpe"], 3)
        wins = oc["sharpe"] > ou["sharpe"]
        if wins:
            cond_win += 1
        if delta >= 0.3:
            cond_win_margin += 1
        rows.append({"strategy": strat, "uncond_exit": uncond_exit,
                     "oos_uncond_sharpe": ou["sharpe"], "oos_cond_sharpe": oc["sharpe"],
                     "oos_delta": delta, "cond_wins_oos": bool(wins),
                     "cond_map": cond})
    rows.sort(key=lambda r: -r["oos_delta"])
    out.write_text(json.dumps({"by": by, "split": str(split), "cond_min_n": minn,
                               "n_evaluated": evaluated, "n_cond_wins_oos": cond_win,
                               "n_cond_wins_oos_margin_0.3": cond_win_margin,
                               "strategies": rows}, indent=1), encoding="utf-8")
    print(f"[OK] wrote {out}")
    print(f"\n=== strategies where CONDITIONAL exit beats UNCONDITIONAL out-of-sample (top +delta) ===")
    for r in rows[:12]:
        if r["oos_delta"] > 0:
            print(f"  {r['strategy'][:30]:30} uncond={r['uncond_exit'][:14]:14} "
                  f"OOS uncond={r['oos_uncond_sharpe']:>5} cond={r['oos_cond_sharpe']:>5} "
                  f"delta=+{r['oos_delta']}")
    print(f"\n=== worst (conditional OVERFIT - loses OOS) ===")
    for r in rows[-5:]:
        print(f"  {r['strategy'][:30]:30} OOS uncond={r['oos_uncond_sharpe']:>5} "
              f"cond={r['oos_cond_sharpe']:>5} delta={r['oos_delta']}")
    print("\n" + "=" * 62)
    print(f"evaluated {evaluated} strategies (IS+OOS both n>={minn}) | "
          f"conditional beats unconditional OOS: {cond_win} ({100*cond_win/max(evaluated,1):.0f}%) | "
          f"by margin >=0.3: {cond_win_margin}")
    print(f"IS said 155/178 'differ' -> OOS-validated real advantage is the {cond_win_margin} margin set.")
    print("=" * 62)
    return 0


def _conditional(args) -> int:
    """--by: rank (strategy x exit x <category-value>) by ANNUALIZED Sharpe over the
    full 2022-2026 window (n>=--cond-min-n). This is the per-category deployment map
    -- which strategy x exit to run in which regime / vix bucket / sector / etc. It
    is full-window conditional (like the engine's per-regime verdict), NOT a temporal
    walk-forward; cross-reference the temporal-robust set (--all-cells) for stability."""
    import pandas as pd
    cdir = REPO / args.cube_dir
    cube = cdir / "trade_exit_detail.csv"
    by = args.by
    out = Path(args.out) if args.out else (cdir / f"conditional_by_{by}.json")
    print(f"[INFO] --by {by}: reading {cube} (usecols) ...")
    df = pd.read_csv(cube, usecols=["strategy", "exit_method", "pnl_pct", "hold_days", by],
                     low_memory=False)
    df = _friction(df, args)
    print(f"[INFO] cube rows={len(df):,}; grouping by (strategy, exit_method, {by}) ...")
    rows = []
    for (strat, exit_m, val), g in df.groupby(["strategy", "exit_method", by], sort=False):
        st = _sharpe(g["pnl_pct"].values, g["hold_days"].values) if len(g) >= args.cond_min_n else None
        if st:
            rows.append({"strategy": strat, "exit_method": exit_m, by: str(val),
                         "sharpe": st["sharpe"], "n": st["n"], "wr": st["wr"]})
    rows.sort(key=lambda r: -r["sharpe"])

    # (1) UNCONDITIONAL best exit per strategy (the base STRATEGY_EXIT_OVERRIDE):
    #     group by (strategy, exit) over the whole window.
    uncond = {}
    for (strat, exit_m), g in df.groupby(["strategy", "exit_method"], sort=False):
        st = _sharpe(g["pnl_pct"].values, g["hold_days"].values) if len(g) >= args.cond_min_n else None
        if st:
            cur = uncond.get(strat)
            if cur is None or st["sharpe"] > cur["sharpe"]:
                uncond[strat] = {"exit_method": exit_m, "sharpe": st["sharpe"], "n": st["n"]}

    # (2) CONDITIONAL best exit per (strategy, by-value) -- the deployable
    #     regime/vix/etc-conditioned exit override.
    per_strat = {}
    for r in rows:
        d = per_strat.setdefault(r["strategy"], {})
        cur = d.get(r[by])
        if cur is None or r["sharpe"] > cur["sharpe"]:
            d[r[by]] = {"exit_method": r["exit_method"], "sharpe": r["sharpe"], "n": r["n"], "wr": r["wr"]}

    # how often does the conditional best-exit DIFFER from the unconditional? (the
    # value of conditioning: a strategy that wants a different exit in bear vs bull)
    differ = 0
    for strat, dv in per_strat.items():
        base = uncond.get(strat, {}).get("exit_method")
        if base and any(x["exit_method"] != base for x in dv.values()):
            differ += 1

    out.write_text(json.dumps({"by": by, "gate_threshold": GATE_SHARPE, "cond_min_n": args.cond_min_n,
                               "n_slices": len(rows), "n_pass_0.7": sum(r["sharpe"] >= GATE_SHARPE for r in rows),
                               "n_strategies": len(per_strat),
                               "n_strategies_conditional_exit_differs": differ,
                               "best_exit_per_strategy_uncond": uncond,
                               "best_exit_per_strategy_by_value": per_strat}, indent=1), encoding="utf-8")
    print(f"[OK] wrote {out}")
    print(f"\n=== FOR EACH STRATEGY: best exit unconditional vs per {by} (sample, top by uncond Sharpe) ===")
    for strat in sorted(uncond, key=lambda s: -uncond[s]["sharpe"])[:15]:
        u = uncond[strat]
        cond = per_strat.get(strat, {})
        cstr = "  ".join(f"{v}:{x['exit_method']}({x['sharpe']})" for v, x in
                         sorted(cond.items(), key=lambda kv: -kv[1]["sharpe"]))
        flag = " *regime-varies*" if any(x["exit_method"] != u["exit_method"] for x in cond.values()) else ""
        print(f"  {strat[:30]:30} uncond={u['exit_method']}({u['sharpe']}){flag}")
        print(f"       by {by}: {cstr}")
    print("\n" + "=" * 60)
    print(f"{by}: {len(per_strat)} strategies with a qualifying exit | "
          f"{differ} have a DIFFERENT best exit in >=1 {by} value than their unconditional best")
    print("=" * 60)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube-dir", default="output_r5_merged_1_7")
    ap.add_argument("--analysis",
                    default="output_optimization_candidates_2026_07_25/exit_method_analysis.json")
    ap.add_argument("--all-cells", action="store_true",
                    help="evaluate every (strategy x exit) cell with in-sample n>=--min-n "
                         "from exit_strategy_comparison.csv (not just the 5-Gate shortlist)")
    ap.add_argument("--min-n", type=int, default=30, help="in-sample n floor for --all-cells")
    ap.add_argument("--by", default=None,
                    help="conditional mode: a cube categorical column (e.g. regime_at_entry, "
                         "vix_at_entry, sector, smart_money_signal_present, confidence_tier). "
                         "Ranks (strategy x exit x <by-value>) by ANNUALIZED Sharpe over the "
                         "full 2022-2026 window with n>=--cond-min-n. Answers 'best strategy x "
                         "exit in each category value'.")
    ap.add_argument("--cond-min-n", type=int, default=30,
                    help="per-slice n floor for --by (conditioning shrinks n)")
    ap.add_argument("--validate-conditional", action="store_true",
                    help="A (the gate): per strategy, PICK best conditional-vs-unconditional exit "
                         "on IS folds (entry 2022-2025), MEASURE both on the OOS fold (entry "
                         ">=2025-05-05). Answers 'does regime-conditional exit BEAT unconditional "
                         "OUT-OF-SAMPLE?' -> the deployable STRATEGY_EXIT_OVERRIDE survivors.")
    ap.add_argument("--winsorize", type=float, default=0.0,
                    help="F6 (B1376): clip per-trade pnl_pct to +/-this before metrics "
                         "(e.g. 300) - removes delisting-collapse outliers (SBNY +264900pct). 0=off.")
    ap.add_argument("--cost-bps", type=float, default=0.0,
                    help="F1: subtract this round-trip cost (bps) from each trade's pnl_pct "
                         "(T1a canonical = 20). 0=off. NOTE: does not add short-borrow (shorts understated).")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.validate_conditional:
        return _validate_conditional(args)
    if args.by:
        return _conditional(args)

    cdir = REPO / args.cube_dir
    cube = cdir / "trade_exit_detail.csv"
    out = Path(args.out) if args.out else (cdir / (
        "walk_forward_r5_all_cells.json" if args.all_cells else "walk_forward_r5_cells.json"))

    if args.all_cells:
        cmp = pd.read_csv(cdir / "exit_strategy_comparison.csv")
        ncol = "trades" if "trades" in cmp.columns else "n"
        cellset = set(map(tuple, cmp[cmp[ncol] >= args.min_n][["strategy", "exit_method"]].values))
        print(f"[INFO] --all-cells: {len(cellset)} cells with in-sample {ncol}>={args.min_n}")
    else:
        an = json.loads((REPO / args.analysis).read_text(encoding="utf-8"))
        l2 = an.get("layer_2_per_strategy_exit_cell", [])
        cellset = set((c.get("strategy"), c.get("exit_method")) for c in l2
                      if c.get("strategy") and c.get("exit_method"))
        print(f"[INFO] 5-Gate shortlist: {len(cellset)} cells")

    print(f"[INFO] reading {cube} (usecols) ...")
    df = pd.read_csv(cube, usecols=["strategy", "entry_date", "exit_method", "pnl_pct", "hold_days"],
                     low_memory=False)
    df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    df = _friction(df, args)
    print(f"[INFO] cube rows={len(df):,}; grouping by (strategy, exit_method) ...")

    results = []
    for (strat, exit_m), g in df.groupby(["strategy", "exit_method"], sort=False):
        if (strat, exit_m) not in cellset:
            continue
        ed = g["entry_date"].values
        pn = g["pnl_pct"].values
        hd = g["hold_days"].values
        folds, qualifying = {}, []
        for name, o0, o1 in FOLDS:
            mask = (ed >= o0) & (ed < o1)
            st = _sharpe(pn[mask], hd[mask])
            folds[name] = st
            if st:
                qualifying.append(st["sharpe"])
        n_ge_07 = sum(1 for s in qualifying if s >= GATE_SHARPE)
        best = max(qualifying) if qualifying else None
        results.append({"strategy": strat, "exit_method": exit_m,
                        "best_oos_sharpe": best, "n_folds_ge_0.7": n_ge_07,
                        "n_qualifying_folds": len(qualifying), "folds": folds})

    pass1 = [r for r in results if r["n_folds_ge_0.7"] >= 1]
    pass2 = [r for r in results if r["n_folds_ge_0.7"] >= 2]
    results.sort(key=lambda r: (r["best_oos_sharpe"] is None, -(r["best_oos_sharpe"] or -9)))
    out.write_text(json.dumps({"gate_threshold": GATE_SHARPE, "oos_min_n": OOS_MIN_N,
                               "mode": "all_cells" if args.all_cells else "shortlist",
                               "n_cells_evaluated": len(results),
                               "n_pass_1fold": len(pass1), "n_pass_2fold": len(pass2),
                               "cells": results}, indent=1), encoding="utf-8")
    print(f"[OK] wrote {out}")

    print("\n=== top cells by best OOS Sharpe (n>=30 folds) ===")
    for r in results[:15]:
        print(f"  {r['strategy'][:30]:30} x {r['exit_method'][:18]:18} "
              f"best={r['best_oos_sharpe']} folds>=0.7={r['n_folds_ge_0.7']}/{r['n_qualifying_folds']}")

    print("\n" + "=" * 60)
    print(f"CELLS EVALUATED: {len(results)}")
    print(f"PASS loose  (>=0.7 in >=1 fold): {len(pass1)}   <- headline count")
    print(f"PASS ROBUST (>=0.7 in >=2 folds): {len(pass2)}   <- multiple-testing-aware")
    print("=" * 60)
    if pass2:
        print(f"1A-ALPHA GATE: OPEN (robust) -- {len(pass2)} cell(s) clear >=0.7 in >=2 folds.")
    elif pass1:
        print(f"1A-ALPHA GATE: OPEN (loose only) -- {len(pass1)} cell(s) at >=1 fold, "
              f"but 0 clear >=2 folds. Treat as marginal.")
    else:
        print("1A-ALPHA GATE: LOCKED.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
