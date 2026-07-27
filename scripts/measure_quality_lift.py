"""scripts/measure_quality_lift.py (B1401) -- the TIGHTENING instrument.

Owner directive 2026-07-27: "not all strategies need to be relaxed, only the quiet and
starved ones; for high-fire strategies we need to focus on improving the win rate, R:R and
Sharpe."

The 91 HIGH-FIRE strategies (>=300 IS fires) do not have a volume problem - they have a
QUALITY problem: `camarilla_r4_breakout` fires 4,478 times at a 27.2% win rate,
`pairs_mean_reversion_short` 4,320 at 24.5%. Loosening those makes them worse. They need
SELECTIVITY: an added gate that keeps the good fires and drops the bad ones.

WHY THIS IS METHODOLOGICALLY EASIER THAN LOOSENING
The loosening question needs bars where the strategy did NOT fire - absent from the trade log,
which is why B1394 had to re-derive signals bar by bar. The tightening question only needs to
PARTITION EXISTING FIRES by outcome, and the trade log already carries `signals_at_entry` plus
the realised pnl for every one of them. No counterfactual is required, so fire-conditioning -
fatal for Lens A Dim A/B (L241) - is here exactly the right conditioning.

WHAT IT MEASURES, per (strategy, candidate signal):
  baseline      n / win-rate / mean pnl / payoff (avg win over avg loss)
  kept          the same, restricted to fires where the signal is True
  delta_wr      win-rate improvement from adding the gate
  delta_exp     expectancy improvement (pct per trade)
  retained      how many fires survive - a gate that "improves" by keeping 12 trades is useless
  p / bh_reject Welch t-test on the pnl difference, BH-FDR corrected across the WHOLE search

GUARDRAILS (this is a search over 91 strategies x many signals - without these it is
curve-fitting):
  - IS window only; the holdout is never read (hard-refused, same as B1394).
  - Candidates must retain >= --min-retained fires (default 100 = PASSING_CRITERIA min_trades),
    so a proposal cannot tighten a strategy into starvation.
  - BH-FDR across the entire family of tests, not per strategy.
  - Output is a RANKED PROPOSAL LIST for owner approval and pre-registration. Nothing is
    applied. R6 is what actually tests whether the improvement survives.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402

from walk_forward_r5_cells import bh_fdr  # noqa: E402

IS_START, IS_END = date(2022, 5, 5), date(2025, 5, 5)
WINSORIZE, COST_BPS = 300.0, 20.0     # same friction as the R5 grading (B1377)


def stats_of(p) -> dict:
    n = len(p)
    if n == 0:
        return {"n": 0}
    wins, loss = p[p > 0], p[p <= 0]
    payoff = float(wins.mean() / abs(loss.mean())) if len(wins) and len(loss) and loss.mean() else None
    return {"n": int(n), "wr": round(float((p > 0).mean()), 4),
            "exp": round(float(p.mean()), 4),
            "payoff": round(payoff, 3) if payoff else None}


def welch_p(a, b) -> float:
    """One-sided Welch t-test: is mean(a) > mean(b)?

    B1402 WARNING: at TRADE level this is invalid here. Trades entered on the same DAY share
    the market move, so they are not independent observations - see `cluster_by_date`, which
    is what the verdict actually uses. Kept only as a diagnostic for comparison.
    """
    na, nb = len(a), len(b)
    if na < 5 or nb < 5:
        return 1.0
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = math.sqrt(va / na + vb / nb)
    if se <= 0:
        return 1.0
    t = (a.mean() - b.mean()) / se
    return 0.5 * math.erfc(t / math.sqrt(2.0))


def cluster_by_date(pnl, dates):
    """B1402 - THE FIX THAT MATTERS. Collapse trades to one observation PER DATE before any
    inference.

    Why: the first run of this tool ranked `vix_term_backwardation` as the top gate for SIX
    unrelated strategies, each with a spectacular expectancy jump. Measured, the retained
    trades for `r1_break_retest` spanned just 32 distinct dates out of 611, and a SINGLE date
    (2025-04-22, the post-tariff rebound) supplied 54 of 195 trades at +24.6%. The "gate" was
    not selecting better trades - it was selecting a handful of huge up-days, and a
    market-wide daily signal (VIX term structure, USD) is exactly the kind of conditioner that
    does that. A trade-level t-test counted 195 correlated trades as 195 independent draws and
    produced a p-value good enough to clear BH-FDR.

    Clustering by date makes the effective sample the number of DAYS, which is the honest unit
    when the conditioner is a market-wide daily variable.
    """
    df = pd.DataFrame({"d": list(dates), "p": list(pnl)})
    g = df.groupby("d")["p"].mean()
    return g


def date_concentration(dates) -> tuple:
    """(n_distinct_dates, share of the single most common date). A gate whose retained trades
    pile onto a few dates is a date-picker, not a filter."""
    s = pd.Series(list(dates)).value_counts()
    if s.empty:
        return 0, 1.0
    return int(len(s)), round(float(s.iloc[0] / s.sum()), 4)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-fires", type=int, default=300,
                    help="only analyse strategies with at least this many IS fires (high-fire set)")
    ap.add_argument("--min-retained", type=int, default=100,
                    help="a candidate gate must leave at least this many fires (min_trades)")
    ap.add_argument("--min-coverage", type=float, default=0.20,
                    help="candidate signal must be present on at least this fraction of fires")
    ap.add_argument("--end", default=IS_END.isoformat())
    ap.add_argument("--fdr-q", type=float, default=0.05)
    ap.add_argument("--min-dates", type=int, default=60,
                    help="candidate must retain trades on at least this many DISTINCT dates "
                         "(B1402: the effective sample is days, not trades)")
    ap.add_argument("--max-top-date-share", type=float, default=0.10,
                    help="no single date may supply more than this share of retained trades")
    ap.add_argument("--output", default="output_audit/b1401_quality_lift.json")
    args = ap.parse_args()

    end = datetime.strptime(args.end, "%Y-%m-%d").date()
    if end > IS_END:
        print(f"[FATAL] --end {end} reaches into the holdout (>= {IS_END}). Refusing: gate "
              f"decisions must stay holdout-free.")
        return 2

    print(f"[INFO] reading trade_log (IS {IS_START} -> {end}) ...")
    frames = []
    for ch in pd.read_csv(REPO / "output_r5_merged_1_7" / "trade_log.csv", chunksize=200000,
                          low_memory=False,
                          usecols=["strategy", "entry_date", "pnl_pct", "signals_at_entry"]):
        ch["entry_date"] = pd.to_datetime(ch["entry_date"]).dt.date
        frames.append(ch[(ch.entry_date >= IS_START) & (ch.entry_date < end)])
    tl = pd.concat(frames, ignore_index=True)
    tl["pnl_pct"] = tl["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0
    counts = tl.strategy.value_counts()
    targets = [s for s, c in counts.items() if c >= args.min_fires]
    print(f"[INFO] {len(tl):,} IS trades | {len(targets)} strategies with >= {args.min_fires} fires")

    cands = []
    for s in targets:
        sub = tl[tl.strategy == s]
        pnl = sub.pnl_pct.reset_index(drop=True)
        base = stats_of(pnl)
        sig = []
        for raw in sub.signals_at_entry:
            try:
                sig.append(json.loads(raw) if isinstance(raw, str) else {})
            except Exception:
                sig.append({})
        keys = {}
        for d in sig:
            for k, v in d.items():
                if isinstance(v, bool):
                    keys[k] = keys.get(k, 0) + 1
        for k, seen in keys.items():
            if seen / len(sig) < args.min_coverage:
                continue
            mask = pd.Series([bool(d.get(k)) for d in sig])
            kept, dropped = pnl[mask.values], pnl[~mask.values]
            if len(kept) < args.min_retained or len(dropped) < 5:
                continue
            ks, ds = stats_of(kept), stats_of(dropped)
            # B1402: date-clustered inference + concentration guards. Trades sharing a date
            # share the market move; the honest unit is the DAY.
            dts = sub.entry_date.reset_index(drop=True)
            kd, dd = dts[mask.values], dts[~mask.values]
            n_dates, top_share = date_concentration(kd)
            ck, cd = cluster_by_date(kept, kd), cluster_by_date(dropped, dd)
            cands.append({
                "strategy": s, "signal": k,
                "baseline": base, "kept": ks, "dropped": ds,
                "delta_wr": round(ks["wr"] - base["wr"], 4),
                "delta_exp": round(ks["exp"] - base["exp"], 4),
                "retained": ks["n"], "retained_pct": round(ks["n"] / base["n"], 3),
                "n_dates_kept": n_dates,
                "top_date_share": top_share,
                "trades_per_date": round(ks["n"] / n_dates, 2) if n_dates else None,
                "p_trade_level_INVALID": welch_p(kept, dropped),
                "p": welch_p(ck, cd),          # the verdict p: clustered by date
            })
    if not cands:
        print("[RESULT] no candidate passed the coverage/retention filters")
        return 0

    rej, thr = bh_fdr([c["p"] for c in cands], q=args.fdr_q)
    for c, ok in zip(cands, rej):
        c["bh_reject"] = bool(ok)
    # B1402 concentration guards, applied ON TOP of date-clustered FDR: a candidate must
    # spread across enough distinct days, and no single day may dominate what it retains.
    survivors = [c for c in cands
                 if c["bh_reject"] and c["delta_wr"] > 0 and c["delta_exp"] > 0
                 and c["n_dates_kept"] >= args.min_dates
                 and c["top_date_share"] <= args.max_top_date_share]
    survivors.sort(key=lambda c: -c["delta_exp"])

    print(f"\n[RESULT] {len(cands)} candidate gates tested across {len(targets)} strategies")
    print(f"         {sum(1 for c in cands if c['bh_reject'])} survive BH-FDR q<{args.fdr_q} "
          f"(threshold p<={thr:.2e})")
    print(f"         {len(survivors)} also improve BOTH win rate and expectancy\n")
    print(f"  {'strategy':<38}{'add gate':<30}{'WR':>16}{'exp/trade':>18}{'fires kept':>14}")
    for c in survivors[:30]:
        b, k = c["baseline"], c["kept"]
        print(f"  {c['strategy']:<38}{c['signal']:<30}"
              f"{b['wr']:.3f}->{k['wr']:.3f}{'':>4}"
              f"{b['exp']:+.3f}->{k['exp']:+.3f}%{'':>3}"
              f"{b['n']:>6}->{k['n']:<6}")

    out = REPO / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "window": [str(IS_START), str(end)], "holdout_touched": False,
        "min_fires": args.min_fires, "min_retained": args.min_retained,
        "fdr_q": args.fdr_q, "bh_threshold": thr,
        "n_tested": len(cands), "n_fdr_survivors": sum(1 for c in cands if c["bh_reject"]),
        "n_proposals": len(survivors), "proposals": survivors,
        "all_candidates": cands}, indent=2), encoding="utf-8")
    print(f"\n[OK] wrote {out}")
    print("[NOTE] PROPOSALS ONLY - nothing applied. These are IN-SAMPLE improvements and must "
          "be pre-registered before R6; R6 is what tests whether they survive.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
