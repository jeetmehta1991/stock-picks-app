"""scripts/measure_criterion_11.py (B1456) -- MEASURE what canonical criterion #11 would admit.

OWNER QUESTION (2026-08-04): "how many strategies come in if Canonical criterion #11 is applied?
What does pass mean?"

THIS IS A MEASUREMENT, NOT A GATE CHANGE. Nothing in config or in the roster pipeline is modified.
Criterion #11 is `min_regimes_passing` = 1: a cell PASSES if it clears the PER-REGIME thresholds
inside at least one regime, rather than clearing the pooled thresholds over the whole window.

WHAT "PASS" MEANS UNDER #11 -- the per-regime threshold tier, which is a DIFFERENT set of numbers
from the pooled tier the roster currently uses:

  criterion      per-regime (used here)          what the roster currently uses (pooled)
  trades         min_trades_per_regime   30      min_trades              100
  sharpe         min_sharpe_per_regime   0.5     min_sharpe_per_regime   0.5   (same)
  sortino        min_sortino_per_regime  0.7     min_sortino_per_regime  0.7   (same)
  profit factor  min_profit_factor       1.2     min_profit_factor_overall 1.3
  psr            min_psr                 0.95    min_psr                 0.95  (same)

So #11 is MORE permissive on trade count (30 vs 100) and profit factor (1.2 vs 1.3), and identical
on the three ratio bars -- but HARDER in practice, because a within-regime sample is a fraction of
the pooled sample, which widens the Sharpe standard error and depresses PSR.

Selection discipline is unchanged and non-negotiable: the exit is chosen on the IS folds by argmax
gates-cleared, and the per-regime verdict is computed ONCE on the holdout for that single exit.
No search over regimes on the graded window -- picking "whichever regime passes" from 3 candidates
would be a milder cousin of the B1452 lookahead, so the regime that passes is REPORTED, and the
count of passing regimes is what the criterion tests.
"""
from __future__ import annotations

import argparse
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
import roster_core as _rc                                   # noqa: E402
from backtest.results.metrics import _sortino_ratio, _deflated_sharpe  # noqa: E402
from walk_forward_r5_cells import _sharpe                    # noqa: E402

IS_START, IS_END = date(2022, 5, 5), date(2025, 5, 5)
HO_START, HO_END = date(2025, 5, 5), date(2026, 5, 5)
WINSORIZE, COST_BPS = 300.0, 20.0


def gates_pooled(pnl, hold):
    """B2008 (D1+D2): the canonical POOLED tier - overall bars throughout.

    The fork graded its self-described "pooled tier" with per-regime sharpe
    (0.5) and sortino (0.7): S6-B1903a's crossed bars, duplicated. Output
    verdicts CHANGE under the owner-approved D2 bars; the old artifact is
    superseded, not comparable.
    """
    r = _rc.evaluate(pnl, hold, min_n=PC["min_trades"],
                     pf_bar=PC["min_profit_factor_overall"], tier="pooled")
    if r is None:
        return None
    return {"n": r["n"], "sharpe": r["sharpe"],
            "ok": bool(r["gates"]["pooled_sharpe"] and r["gates"]["profit_factor"]
                       and r["gates"]["sortino"] and r["gates"]["psr"]
                       and r["n"] >= PC["min_trades"])}


def gates_per_regime(pnl, hold):
    """B2008 (D1): the canonical PER-REGIME tier - criterion #11's bars."""
    r = _rc.evaluate(pnl, hold, tier="per_regime")
    if r is None:
        return None
    return {"n": r["n"], "sharpe": r["sharpe"], "psr": r["psr"],
            "pf": r["profit_factor"],
            "ok": bool(r["gates"]["pooled_sharpe"] and r["gates"]["profit_factor"]
                       and r["gates"]["sortino"] and r["gates"]["psr"])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube", default="output_r5_merged_1_7")
    ap.add_argument("--output", default="output_audit/b1456_criterion_11_measurement.json")
    args = ap.parse_args()

    print("=" * 100)
    print("CRITERION #11 MEASUREMENT (B1456) -- measurement only, no gate or config changed")
    print("=" * 100)
    print(f"  per-regime tier: trades>={PC['min_trades_per_regime']}, "
          f"sharpe>={PC['min_sharpe_per_regime']}, sortino>={PC['min_sortino_per_regime']}, "
          f"pf>={PC['min_profit_factor']}, psr>={PC['min_psr']}")
    # B2008 (D2): the pooled header now tells the truth - OVERALL bars.
    # The old line printed per-regime sharpe/sortino for the pooled tier,
    # matching the crossed-bar arithmetic the tier= change removed.
    print(f"  pooled tier    : trades>={PC['min_trades']}, "
          f"sharpe>={PC['min_sharpe_overall']}, sortino>={PC['min_sortino_overall']}, "
          f"pf>={PC['min_profit_factor_overall']}, psr>={PC['min_psr']}")
    print(f"  min_regimes_passing = {PC['min_regimes_passing']}\n")

    df = pd.read_csv(REPO / args.cube / "trade_exit_detail.csv",
                     usecols=["strategy", "direction", "exit_method", "entry_date",
                              "regime_at_entry", "pnl_pct", "hold_days"], low_memory=False,
                     dtype={"strategy": "category", "direction": "category",
                            "exit_method": "category", "regime_at_entry": "category",
                            "pnl_pct": "float32", "hold_days": "float32"})
    df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    df["pnl_pct"] = df["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0

    rows = []
    for (strat, direction), g in df.groupby(["strategy", "direction"], observed=True):
        isg = g[(g.entry_date >= IS_START) & (g.entry_date < IS_END)]
        hog = g[(g.entry_date >= HO_START) & (g.entry_date < HO_END)]
        # SELECT the exit on IS by the same objective the roster uses (argmax gates-cleared).
        best, best_key = None, (-1, -9.0)
        for ex, ge in isg.groupby("exit_method", observed=True):
            r = gates_pooled(ge["pnl_pct"], ge["hold_days"])
            if not r:
                continue
            k = (1 if r["ok"] else 0, rank_key(r["sharpe"]))
            if k > best_key:
                best_key, best = k, ex
        if best is None:
            continue
        he = hog[hog.exit_method == best]
        pooled = gates_pooled(he["pnl_pct"], he["hold_days"])
        per_reg, passing = {}, []
        for reg, gr in he.groupby("regime_at_entry", observed=True):
            r = gates_per_regime(gr["pnl_pct"], gr["hold_days"])
            if r:
                per_reg[str(reg)] = r
                if r["ok"]:
                    passing.append(str(reg))
        rows.append({"strategy": strat, "direction": direction, "exit": best,
                     "pooled_pass": bool(pooled and pooled["ok"]),
                     "n_regimes_evaluable": len(per_reg),
                     "n_regimes_passing": len(passing), "passing_regimes": passing,
                     "crit11_pass": len(passing) >= PC["min_regimes_passing"],
                     "per_regime": per_reg})

    pooled_p = [r for r in rows if r["pooled_pass"]]
    c11_p = [r for r in rows if r["crit11_pass"]]
    both = [r for r in rows if r["pooled_pass"] and r["crit11_pass"]]
    only11 = [r for r in rows if r["crit11_pass"] and not r["pooled_pass"]]
    onlyp = [r for r in rows if r["pooled_pass"] and not r["crit11_pass"]]

    print(f"  cells evaluated                       {len(rows)}")
    print(f"  POOLED pass (roster's current gate)   {len(pooled_p)}")
    print(f"  CRITERION #11 pass (>=1 regime)       {len(c11_p)}")
    print(f"     of which also pooled-pass          {len(both)}")
    print(f"     ADMITTED ONLY BY #11               {len(only11)}")
    print(f"     pooled-pass but FAILS #11          {len(onlyp)}")
    print()
    import collections
    rc = collections.Counter(reg for r in c11_p for reg in r["passing_regimes"])
    print(f"  which regime carries the #11 passers: {dict(rc)}")
    dc = collections.Counter(r["direction"] for r in c11_p)
    print(f"  direction split of #11 passers:       {dict(dc)}")
    print()
    print(f"  {'strategy':<44}{'dir':<7}{'regimes':<22}{'pooled?':>8}")
    for r in sorted(only11, key=lambda x: x["strategy"])[:30]:
        print(f"  {r['strategy']:<44}{r['direction']:<7}{','.join(r['passing_regimes']):<22}{'no':>8}")

    out = REPO / args.output
    out.write_text(json.dumps({
        "MEASUREMENT_ONLY_NO_GATE_CHANGED": True,
        "per_regime_tier": {"min_trades_per_regime": PC["min_trades_per_regime"],
                            "min_sharpe_per_regime": PC["min_sharpe_per_regime"],
                            "min_sortino_per_regime": PC["min_sortino_per_regime"],
                            "pooled_bars_B2008": {
                                "sharpe": PC["min_sharpe_overall"],
                                "sortino": PC["min_sortino_overall"]},
                            "min_profit_factor": PC["min_profit_factor"],
                            "min_psr": PC["min_psr"]},
        "min_regimes_passing": PC["min_regimes_passing"],
        "n_cells": len(rows), "n_pooled_pass": len(pooled_p), "n_crit11_pass": len(c11_p),
        "n_only_crit11": len(only11), "n_only_pooled": len(onlyp),
        "rows": rows}, indent=2, default=str), encoding="utf-8")
    print(f"\n[OK] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
