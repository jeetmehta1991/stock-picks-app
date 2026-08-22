"""scripts/compare_sample_fix_variants.py (B1459) -- END-TO-END funnel under each fix to the
GRADING SAMPLE, so the owner can size S6-B1456a / S6-B1457a before deciding.

OWNER QUESTION (2026-08-04): "After fixing how many strategies will pass this gate vs current?"

The defect (L292): the cube deliberately bypassed STRATEGY_REGIME_AFFINITY so per-regime verdicts
could be measured, then the grading pipeline pooled every trade into one Sharpe -- including trades
in regimes the strategy explicitly disclaims. The threshold (0.5) is not the problem; the SAMPLE is.

Four variants, each run through the SAME downstream pipeline the roster uses
(gates -> BH-FDR q<0.05 -> Jaccard>=0.70 de-dup), so the numbers are comparable end to end:

  POOLED       current behaviour: all holdout trades, pooled tier
                 (trades>=100, sharpe>=0.5, sortino>=0.7, pf>=1.3, psr>=0.95)
  IN-AFFINITY  restrict to the strategy's declared regimes, then the pooled tier.
                 Undeclared affinity (121 of 222 strategies) => unchanged, all regimes.
  PER-REGIME   criterion #11: per-regime tier inside each regime, pass if >=1 regime clears
                 (trades>=30, sharpe>=0.5, sortino>=0.7, pf>=1.2, psr>=0.95)
  BOTH         per-regime verdict restricted to declared-affinity regimes

SELECTION DISCIPLINE IS IDENTICAL ACROSS VARIANTS AND UNCHANGED: the exit is chosen on the IS folds
by argmax gates-cleared (pooled tier, IS only), and the holdout is read once. Only the GRADING
sample differs. Varying selection too would confound the comparison.

MEASUREMENT ONLY -- no config, gate or threshold is modified by this script.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backtest.config import PASSING_CRITERIA as PC          # noqa: E402
from roster_core import rank_key                            # noqa: E402
from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY as AFF  # noqa: E402
from backtest.results.metrics import _sortino_ratio, _deflated_sharpe  # noqa: E402
from walk_forward_r5_cells import _sharpe, bh_fdr            # noqa: E402

IS_START, IS_END = date(2022, 5, 5), date(2025, 5, 5)
HO_START, HO_END = date(2025, 5, 5), date(2026, 5, 5)
WINSORIZE, COST_BPS, FDR_Q, JACCARD = 300.0, 20.0, 0.05, 0.70


def _stats(pnl, hold, min_n, pf_bar):
    n = len(pnl)
    if n < min_n:
        return None
    sh = _sharpe(pnl.values, hold)
    sharpe = sh["sharpe"] if sh else None
    sortino = _sortino_ratio(pnl, hold)
    # B1976: an UNMEASURABLE Sharpe must not reach DSR as a MEASURED zero.
    dsr = (_deflated_sharpe(sharpe, n, float(pnl.skew()), float(pnl.kurtosis()))
           if sharpe is not None else None)
    w, l = pnl[pnl > 0], pnl[pnl <= 0]
    pf = float(w.sum() / abs(l.sum())) if len(l) and l.sum() != 0 else float("inf")
    ok = (sharpe is not None and sharpe >= PC["min_sharpe_per_regime"]
          and pf >= pf_bar
          and sortino is not None and sortino >= PC["min_sortino_per_regime"]
          and dsr.get("psr") is not None and dsr["psr"] >= PC["min_psr"]
          and n >= min_n)
    return {"n": n, "sharpe": sharpe, "ok": ok, "p": (sh or {}).get("p", 1.0)}


def pooled(g):
    return _stats(g["pnl_pct"], g["hold_days"], PC["min_trades"], PC["min_profit_factor_overall"])


def per_regime(g):
    """Criterion #11: best regime by the per-regime tier; pass if >=1 regime clears."""
    best, passing = None, []
    for reg, gr in g.groupby("regime_at_entry", observed=True):
        r = _stats(gr["pnl_pct"], gr["hold_days"],
                   PC["min_trades_per_regime"], PC["min_profit_factor"])
        if not r:
            continue
        if r["ok"]:
            passing.append(str(reg))
        if best is None or rank_key(r["sharpe"]) > rank_key(best["sharpe"]):
            best = r
    if best is None:
        return None
    out = dict(best)
    out["ok"] = len(passing) >= PC["min_regimes_passing"]
    out["passing_regimes"] = passing
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube", default="output_r5_merged_1_7")
    ap.add_argument("--output", default="output_audit/b1459_sample_fix_variants.json")
    args = ap.parse_args()

    print("=" * 98)
    print("SAMPLE-FIX VARIANT COMPARISON (B1459) -- measurement only, nothing changed")
    print("=" * 98)

    df = pd.read_csv(REPO / args.cube / "trade_exit_detail.csv",
                     usecols=["strategy", "direction", "exit_method", "entry_date", "ticker",
                              "regime_at_entry", "pnl_pct", "hold_days"], low_memory=False,
                     dtype={"strategy": "category", "direction": "category",
                            "exit_method": "category", "ticker": "category",
                            "regime_at_entry": "category",
                            "pnl_pct": "float32", "hold_days": "float32"})
    df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    df["pnl_pct"] = df["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0

    n_decl = sum(1 for s in df.strategy.unique() if AFF.get(str(s)))
    print(f"  {df.strategy.nunique()} strategies in cube | {n_decl} declare a regime affinity")
    print(f"  selection: argmax IS gates-cleared (identical across variants)\n")

    variants = {"POOLED": [], "IN-AFFINITY": [], "PER-REGIME": [], "BOTH": []}
    for (strat, direction), g in df.groupby(["strategy", "direction"], observed=True):
        strat, direction = str(strat), str(direction)
        isg = g[(g.entry_date >= IS_START) & (g.entry_date < IS_END)]
        hog = g[(g.entry_date >= HO_START) & (g.entry_date < HO_END)]
        # SELECT on IS -- unchanged, pooled tier, holdout never read
        pick, key = None, (-1, -9.0)
        for ex, ge in isg.groupby("exit_method", observed=True):
            r = pooled(ge)
            if not r:
                continue
            k = (1 if r["ok"] else 0, rank_key(r["sharpe"]))
            if k > key:
                key, pick = k, str(ex)
        if pick is None:
            continue
        he = hog[hog.exit_method == pick]
        aff = AFF.get(strat)
        he_aff = he[he.regime_at_entry.isin(aff)] if aff else he
        for name, r in (("POOLED", pooled(he)), ("IN-AFFINITY", pooled(he_aff)),
                        ("PER-REGIME", per_regime(he)), ("BOTH", per_regime(he_aff))):
            if r:
                variants[name].append({"strategy": strat, "direction": direction, "exit": pick,
                                       **r, "_trades": he_aff if "AFF" in name or name == "BOTH" else he})

    def funnel(rows):
        ev = len(rows)
        passed = [r for r in rows if r["ok"]]
        if not passed:
            return ev, 0, 0, 0, []
        rej, _ = bh_fdr([r["p"] for r in passed], q=FDR_Q)
        surv = [r for r, k in zip(passed, rej) if k]
        surv.sort(key=lambda r: -rank_key(r["sharpe"]))
        kept, seen = [], []
        for r in surv:
            A = set(map(tuple, r["_trades"][["ticker", "entry_date"]].drop_duplicates().values))
            if any(A and B and len(A & B) / len(A | B) >= JACCARD for B in seen):
                continue
            seen.append(A)
            kept.append(r)
        return ev, len(passed), len(surv), len(kept), kept

    print(f"  {'variant':<14}{'evaluable':>10}{'gates':>8}{'BH-FDR':>8}{'de-duped':>10}"
          f"{'long':>7}{'short':>7}")
    results = {}
    for name, rows in variants.items():
        ev, gp, fd, dd, kept = funnel(rows)
        dc = collections.Counter(r["direction"] for r in kept)
        results[name] = {"evaluable": ev, "gates": gp, "fdr": fd, "final": dd,
                         "long": dc.get("long", 0), "short": dc.get("short", 0),
                         "cells": [{k: v for k, v in r.items() if k != "_trades"} for r in kept]}
        mark = "  <-- CURRENT" if name == "POOLED" else ""
        print(f"  {name:<14}{ev:>10}{gp:>8}{fd:>8}{dd:>10}"
              f"{dc.get('long',0):>7}{dc.get('short',0):>7}{mark}")

    base = {c["strategy"] for c in results["POOLED"]["cells"]}
    print()
    for name in ("IN-AFFINITY", "PER-REGIME", "BOTH"):
        s = {c["strategy"] for c in results[name]["cells"]}
        print(f"  {name:<14} vs POOLED:  +{len(s - base):<3} new   -{len(base - s):<3} dropped   "
              f"{len(s & base)} retained")

    out = REPO / args.output
    out.write_text(json.dumps({"MEASUREMENT_ONLY": True, "cube": args.cube,
                               "results": results}, indent=2, default=str), encoding="utf-8")
    print(f"\n[OK] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
