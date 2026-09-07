#!/usr/bin/env python
# Source: output_r5_merged_1_7/trade_exit_detail.csv graded through
# scripts/roster_core.py (select_exit + evaluate), per CHECKLIST #77.
"""B2628 (S6-B2627, owner ruling 2026-09-06 "Option (c) with pre-registration,
then (b)"): grade every institutional_persistence sibling's EXISTING R5 trades
through the Step-2 machinery - one offline pass, zero engine hours.

PRE-REGISTERED: output_audit/b2628_family_pass_prereg.json is committed BEFORE
this script's first real run, carrying the 19-name population, the mechanism
(IS-only exit selection via roster_core.select_exit objective=gates, one
holdout read via roster_core.evaluate, the six LIVE_GATES), and the decision
rules R1/R2. R1 deliberately triggers on the NON-SHARED-with-icg holdout
trades, never the full population - the maximum of 19 correlated readings
exceeds the reference by chance alone (the costed Contrarian objection), so a
full-population trigger would manufacture the campaign the pass exists to
avoid. Every output row carries its overlap-with-icg share inline so 19
correlated grades cannot read as independent evidence.

Usage:
  python scripts/grade_family_siblings.py \
      --out output_audit/b2628_institutional_family_grades.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import roster_core as rc  # noqa: E402

CUBE = ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv"
PREREG = ROOT / "output_audit" / "b2628_family_pass_prereg.json"
REFERENCE = "institutional_committed_growth_long"


def load_family(cube_path: Path = CUBE) -> pd.DataFrame:
    want = ["strategy", "exit_method", "entry_date", "ticker",
            "pnl_pct", "hold_days"]
    df = pd.read_csv(cube_path, low_memory=False,
                     usecols=lambda c: c in want)
    df = df[df["strategy"].str.startswith("institutional_", na=False)].copy()
    df["entry_date"] = pd.to_datetime(df["entry_date"], errors="coerce").dt.date
    return df


def entry_keys(g: pd.DataFrame) -> set:
    one = g[g["exit_method"] == g["exit_method"].iloc[0]]
    return set(map(tuple, one[["ticker", "entry_date"]].values))


def six_gates(hold_rows: pd.DataFrame, full_n: int) -> tuple[dict | None, dict]:
    """The six LIVE_GATES on one holdout population (mirrors the icg Step-2
    grade): evaluate() carries the four statistical gates; the two min-trade
    legs are explicit here at the ruled bars (holdout>=15, full>=75)."""
    v = rc.evaluate(hold_rows["pnl_pct"].astype(float),
                    hold_rows["hold_days"].astype(float), min_n=10)
    n_ho = len(hold_rows[["ticker", "entry_date"]].drop_duplicates())
    gates = {}
    if v:
        gates.update({k: bool(v["gates"].get(k)) for k in
                      ("pooled_sharpe", "profit_factor", "sortino", "psr")
                      if k in (v.get("gates") or {})})
    gates["min_trades_holdout"] = n_ho >= 15
    gates["min_trades_full_period"] = full_n >= 75
    return v, gates


def grade_all(df: pd.DataFrame) -> dict:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    icg_keys = entry_keys(df[df["strategy"] == REFERENCE])
    out = {"prereg": str(PREREG.name), "reference": REFERENCE,
           "reference_holdout_sharpe": prereg["reference_holdout_sharpe"],
           "graded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "siblings": {}}
    for st in prereg["population"]:
        g = df[df["strategy"] == st]
        if g.empty:
            out["siblings"][st] = {"error": "no rows in cube"}
            continue
        keys = entry_keys(g)
        overlap = len(keys & icg_keys) / len(keys) if keys else 0.0
        ex, is_stats = rc.select_exit(g, objective="gates", min_n=10)
        row: dict = {"n_trades": len(keys),
                     "overlap_with_icg": round(overlap, 3),
                     "selected_exit": ex}
        if ex is None:
            row["verdict"] = "NO_EXIT_SELECTABLE"
            out["siblings"][st] = row
            continue
        cell = g[g["exit_method"] == ex]
        ho = rc.holdout(cell)
        v, gates = six_gates(ho, full_n=len(keys))
        row["holdout_n"] = len(ho[["ticker", "entry_date"]].drop_duplicates())
        row["holdout_sharpe"] = v.get("sharpe") if v else None
        row["gates"] = gates
        row["gates_passed"] = sum(bool(x) for x in gates.values())
        row["verdict"] = "PASS" if all(gates.values()) and len(gates) == 6 else "FAIL"
        # R1: the non-shared holdout population, graded separately
        ns = ho[~ho.apply(lambda r: (r["ticker"], r["entry_date"]) in icg_keys,
                          axis=1)]
        ns_n = len(ns[["ticker", "entry_date"]].drop_duplicates())
        ns_v = (rc.evaluate(ns["pnl_pct"].astype(float),
                            ns["hold_days"].astype(float), min_n=10)
                if ns_n >= 15 else None)
        ns_sh = ns_v.get("sharpe") if ns_v else None
        row["non_shared_holdout_n"] = ns_n
        row["non_shared_holdout_sharpe"] = ns_sh
        row["R1_campaign_consideration"] = bool(
            ns_n >= 15 and ns_sh is not None
            and ns_sh > prereg["reference_holdout_sharpe"])
        row["R2_campaign_consideration"] = overlap < 0.80
        out["siblings"][st] = row
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    df = load_family()
    out = grade_all(df)
    Path(a.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"{'sibling':46} {'n':>5} {'ovl':>5} {'exit':22} {'ho_n':>5} "
          f"{'ho_sharpe':>9} {'gates':>5} {'verdict':7} {'R1':>3} {'R2':>3}")
    for st, r in out["siblings"].items():
        print(f"{st:46} {r.get('n_trades','-'):>5} "
              f"{r.get('overlap_with_icg','-'):>5} "
              f"{str(r.get('selected_exit')):22} {r.get('holdout_n','-'):>5} "
              f"{str(r.get('holdout_sharpe')):>9} "
              f"{r.get('gates_passed','-'):>5} {str(r.get('verdict')):7} "
              f"{'YES' if r.get('R1_campaign_consideration') else 'no':>3} "
              f"{'YES' if r.get('R2_campaign_consideration') else 'no':>3}")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
