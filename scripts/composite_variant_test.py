#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""B2674 (S6-B2654, owner ruling 2026-09-10 'Test composite upgrades'): the
offline test of the _has_smart_money_buy composite's tightened variants.

VARIANTS (tightenings of the recorded fire population - subset-safe, zero
engine hours; the two loosenings ceo_buy/director_only_buy need the next cube):
  baseline : insider_cluster_active|cfo_buy|large_dollar_buy|inst_strong|inst_buy
             (screener.py:7695-7703, read at build)
  v1_drop_inst_buy      : events OR strong (institutional_buy leg removed)
  v2_strong_replaces_buy: events OR strong (SET-IDENTICAL to v1 by
             construction, since strong is a strict subset of buy inside an
             OR - computed independently and the identity REPORTED, never
             assumed)
  v3_drop_cfo           : baseline minus the cfo_buy leg (B2654 finding 3
             measured 4-of-4 cfo overlap with the cluster leg on peadsm -
             expected near-no-op, measured per strategy)

POPULATION: the 7 hard-gate consumers of the composite (8 call sites minus
strat_52w_high_breakout_with_smart_money_long, where the composite is
annotation-only per B1195 - fires = base_fires, screener.py:7823).

GRADING per strategy x variant x exit, per the recorded owner test plan:
IS sharpe (min 10) AND the six live holdout gates (roster_core.evaluate).
This is an owner-ruled MEASUREMENT; admissions still need their own rulings.
FAITHFULNESS GATE (replaces a key-presence coverage rule after two wrong
drafts, both skipping 7 of 7 on a misread of persistence semantics): for
BOOLEAN legs, an absent key is exactly what the engine's s.get(k, False)
read at gate time, so .get reconstruction is faithful by construction;
the fail-closed check is that the BASELINE composite recomputes True on
>= 98pct of each strategy's fires (it was their admitting gate). A
per-leg presence census is recorded for the reader. next_pivot_target is
flagged on every row
and excluded from any headline selection (runbook 11.2b2 bar).
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import roster_core as rc  # noqa: E402

CUBE = ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv"
TRADE_LOG = ROOT / "output_r5_merged_1_7" / "trade_log.csv"
MIN_COVERAGE = 0.98
BARRED_EXIT = "next_pivot_target"

LEGS = ("insider_cluster_active", "cfo_buy", "large_dollar_buy",
        "institutional_strong_buy", "institutional_buy")

STRATS = (
    "bollinger_tight_with_smart_money_long",
    "mfi_oversold_with_smart_money_long",
    "rsi_oversold_with_smart_money_long",
    "xs_low_beta_with_smart_money_long",
    "donchian_breakout_with_smart_money_long",
    "macd_bullish_with_smart_money_long",
    "pead_with_smart_money_long",
)

VARIANTS = {
    "baseline":               lambda d: any(d.get(k) is True for k in LEGS),
    "v1_drop_inst_buy":       lambda d: any(d.get(k) is True for k in LEGS[:4]),
    "v2_strong_replaces_buy": lambda d: any(d.get(k) is True for k in
                                            LEGS[:3] + ("institutional_strong_buy",)),
    "v3_drop_cfo":            lambda d: any(d.get(k) is True for k in
                                            ("insider_cluster_active", "large_dollar_buy",
                                             "institutional_strong_buy", "institutional_buy")),
}


def _parse(s):
    try:
        return json.loads(s)
    except Exception:
        try:
            return ast.literal_eval(s)
        except Exception:
            return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()

    tl = pd.read_csv(TRADE_LOG, low_memory=False,
                     usecols=["strategy", "ticker", "entry_date", "signals_at_entry"])
    fam = tl[tl.strategy.isin(STRATS)].drop_duplicates(["strategy", "ticker", "entry_date"]).copy()
    dicts = [_parse(s) for s in fam["signals_at_entry"]]
    # B2674 coverage, corrected after the first run's uniform ~5pct false
    # skip (L724 - the reader was wrong): insider_cluster_active is
    # persisted TRUE-ONLY (measured 43 of 656 peadsm dicts present, all
    # True), and an absent key is what the engine's s.get(k, False) read
    # as False at fire time. So a leg is COVERED when its presence >= 98pct
    # OR every present value is True (true-only persistence, absent=False).
    # Only a leg that is sparse AND mixed-valued is genuinely uncoverable.
    fam["_dicts"] = dicts
    for name, fn in VARIANTS.items():
        fam[name] = [bool(fn(d)) for d in dicts]
    fam = fam.drop(columns=["signals_at_entry"])
    print(f"fires {len(fam):,} across {fam.strategy.nunique()} of {len(STRATS)} "
          f"consumers ({time.time()-t0:.0f}s)")

    cube = pd.read_csv(CUBE, low_memory=False,
                       usecols=["strategy", "ticker", "entry_date",
                                "exit_method", "pnl_pct", "hold_days"])
    cube = cube[cube.strategy.isin(STRATS)]
    m = cube.merge(fam, on=["strategy", "ticker", "entry_date"], how="left")
    m["entry_date"] = pd.to_datetime(m["entry_date"], errors="coerce").dt.date
    print(f"cube rows {len(m):,} joined ({time.time()-t0:.0f}s)")

    rows, skips, identity = [], [], []
    for strat, g in m.groupby("strategy"):
        fires = g.drop_duplicates(["ticker", "entry_date"])
        leg_census = {}
        for k in LEGS:
            vals = [d.get(k) for d in fires["_dicts"]]
            present = [v for v in vals if v is not None]
            leg_census[k] = {"presence": round(len(present) / max(len(vals), 1), 3),
                             "true_rate_when_present":
                                 round(sum(1 for v in present if v is True)
                                       / max(len(present), 1), 3)}
        base_rate = float(fires["baseline"].mean())
        if base_rate < MIN_COVERAGE:
            skips.append({"strategy": strat,
                          "baseline_reconstruction_rate": round(base_rate, 3),
                          "census": leg_census})
            continue
        # v1/v2 set-identity, measured not assumed
        identity.append({"strategy": strat,
                         "v1_equals_v2": bool((fires["v1_drop_inst_buy"]
                                               == fires["v2_strong_replaces_buy"]).all()),
                         "fires": int(len(fires)),
                         "leg_census": leg_census})
        for vname in VARIANTS:
            sub_all = g[g[vname] == True]  # noqa: E712
            for ex, sub in sub_all.groupby("exit_method"):
                si = rc.in_sample(sub)
                ho = rc.holdout(sub)
                isr = rc._sharpe(si["pnl_pct"].values, si["hold_days"], min_n=10)
                r = rc.evaluate(ho["pnl_pct"], ho["hold_days"], min_n=15,
                                full_period_n=len(sub))
                rows.append({
                    "strategy": strat, "variant": vname, "exit": ex,
                    "is_sharpe": isr["sharpe"] if isr else None,
                    "holdout_sharpe": r["sharpe"] if r else None,
                    "psr": r["psr"] if r else None,
                    "profit_factor": r["profit_factor"] if r else None,
                    "sortino": r["sortino"] if r else None,
                    "holdout_n": r["n"] if r else int(len(ho)),
                    "full_n": int(len(sub)),
                    "all_live_gates": bool(r and r["all_live_gates"]),
                    "npt_barred": ex == BARRED_EXIT})
        print(f"  {strat} done ({time.time()-t0:.0f}s)")

    quals = [r for r in rows if r["all_live_gates"] and not r["npt_barred"]]
    rec = {"_doc": ("B2674 composite variant test (S6-B2654, owner ruling 2026-09-10 "
                    "'Test composite upgrades') - owner-ruled MEASUREMENT, not an "
                    "admission; provenance labels travel per B2660"),
           "legs": list(LEGS), "variants": list(VARIANTS),
           "strategies": list(STRATS),
           "annotation_only_excluded": "52w_high_breakout_with_smart_money_long (B1195)",
           "min_coverage": MIN_COVERAGE, "skips": skips,
           "v1_v2_identity": identity,
           "trials": len(rows),
           "qualifiers_all_six_gates_non_npt": len(quals),
           "rows": rows}
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"{len(rows):,} graded lines | {len(quals)} all-six non-npt qualifiers "
          f"-> {a.out} ({time.time()-t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
