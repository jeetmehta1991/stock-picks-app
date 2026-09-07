#!/usr/bin/env python
# Source: output_r5_merged_1_7/trade_exit_detail.csv via roster_core
# (holdout/evaluate), per CHECKLIST #77.
"""B2633 (S6-B2627a, council-mandated): the family-collinearity PRE-GATE.

Runs BEFORE any campaign target is confirmed. From the existing baseline cube
it measures, per family member:
  - trades and pairwise entry-overlap vs every other member (the institutional
    family measured 6x-overlapping AFTER a 40-hour campaign; this costs
    minutes and runs first now);
  - best-exit holdout sharpe (the SELECTED maximum, L708) beside the
    MEDIAN-exit holdout sharpe (the deflated key the B2631 Contrarian
    objection required so launch decisions see both);
  - the band tag (T/M/L/no-cell) from holdout n.

Output: a JSON artifact plus a printed table. The gate CONFIRMS a family
(high mutual overlap -> one representative campaign + a pre-registered
sibling pass, the B2628 pattern) or SPLITS it (low-overlap members get their
own consideration). It never launches anything.

Usage:
  python scripts/family_pregate.py --strategies pead_long,pead_short,... \
      --out output_audit/b2633_pead_pregate.json
  python scripts/family_pregate.py --prefix pead --out ...
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


def load(strategies: list[str], cube_path: Path = CUBE) -> pd.DataFrame:
    want = ["strategy", "exit_method", "entry_date", "ticker",
            "pnl_pct", "hold_days"]
    df = pd.read_csv(cube_path, low_memory=False,
                     usecols=lambda c: c in want)
    df = df[df["strategy"].isin(strategies)].copy()
    df["entry_date"] = pd.to_datetime(df["entry_date"], errors="coerce").dt.date
    return df


def entry_keys(g: pd.DataFrame) -> set:
    one = g.drop_duplicates(subset=["ticker", "entry_date"])
    return set(map(tuple, one[["ticker", "entry_date"]].values))


def member_stats(g: pd.DataFrame) -> dict:
    """Best-exit AND median-exit holdout sharpe over the member's exits."""
    per_exit = []
    for ex, cell in g.groupby("exit_method"):
        ho = rc.holdout(cell)
        n = len(ho[["ticker", "entry_date"]].drop_duplicates())
        if n < 10:
            continue
        v = rc.evaluate(ho["pnl_pct"].astype(float),
                        ho["hold_days"].astype(float), min_n=10)
        if v and v.get("sharpe") is not None:
            per_exit.append((ex, v["sharpe"], n))
    if not per_exit:
        return {"holdout_gradable_exits": 0}
    shs = sorted(sh for _, sh, _ in per_exit)
    best = max(per_exit, key=lambda t: t[1])
    med = shs[len(shs) // 2]
    return {"holdout_gradable_exits": len(per_exit),
            "best_exit": best[0], "best_exit_holdout_sharpe": best[1],
            "best_exit_holdout_n": best[2],
            "median_exit_holdout_sharpe": med}


def band(n: int) -> str:
    return "T" if n > 300 else ("M" if n > 100 else ("L" if n > 0 else "-"))


def pregate(strategies: list[str]) -> dict:
    df = load(strategies)
    keys = {st: entry_keys(df[df["strategy"] == st]) for st in strategies}
    out = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "cube": str(CUBE.name), "members": {}, "overlap": {}}
    for st in strategies:
        g = df[df["strategy"] == st]
        n = len(keys[st])
        ho_n = len(rc.holdout(g)[["ticker", "entry_date"]].drop_duplicates())
        row = {"n_trades": n, "holdout_n": ho_n, "band": band(ho_n)}
        if n:
            row.update(member_stats(g))
        out["members"][st] = row
    for a in strategies:
        for b in strategies:
            if a < b and keys[a] and keys[b]:
                inter = len(keys[a] & keys[b])
                out["overlap"][f"{a}|{b}"] = {
                    "shared": inter,
                    "of_a": round(inter / len(keys[a]), 3),
                    "of_b": round(inter / len(keys[b]), 3)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategies", default="")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.strategies:
        sts = [s.strip() for s in a.strategies.split(",") if s.strip()]
    elif a.prefix:
        want = ["strategy"]
        allst = pd.read_csv(CUBE, low_memory=False,
                            usecols=lambda c: c in want)["strategy"].unique()
        sts = sorted(s for s in allst if s.startswith(a.prefix + "_")
                     or s == a.prefix)
    else:
        print("--strategies or --prefix required")
        return 2
    out = pregate(sts)
    Path(a.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"{'member':44} {'n':>6} {'ho_n':>5} {'band':>4} "
          f"{'best_exit':22} {'best_sh':>8} {'median_sh':>9}")
    for st, r in out["members"].items():
        print(f"{st:44} {r.get('n_trades',0):>6} {r.get('holdout_n',0):>5} "
              f"{r.get('band','-'):>4} {str(r.get('best_exit','-')):22} "
              f"{str(r.get('best_exit_holdout_sharpe','-')):>8} "
              f"{str(r.get('median_exit_holdout_sharpe','-')):>9}")
    print("\npairwise overlap (share of the smaller member in parentheses):")
    for k, v in sorted(out["overlap"].items(),
                       key=lambda t: -max(t[1]["of_a"], t[1]["of_b"])):
        print(f"  {k:70} shared {v['shared']:>5}  of_a {v['of_a']:.0%}  of_b {v['of_b']:.0%}")
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
