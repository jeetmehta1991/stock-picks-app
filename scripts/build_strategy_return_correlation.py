#!/usr/bin/env python
"""B2182 (S6-B2178a): strategy-return correlation + effective breadth from the
R5 production trade log - ZERO engine runs.

THE QUESTION (external-AI item 12, all five council advisors converged): with
219 registered strategies and a per-strategy Sharpe-1.0 gate that passed 3,
does the CORRELATION STRUCTURE of the existing streams already imply that a
decorrelated portfolio of sub-gate strategies clears 1.0? Portfolio Sharpe
~ s_bar * sqrt(N / (1 + (N-1)*rho_bar)).

DISCLOSED CHOICES (v1, each cheap to revisit):
- SOURCE: output_r5_merged_1_7/trade_log.parquet - the PRODUCTION log, so
  every trade already carries its strategy's own configured exit; no exit
  selection is performed here and none of the grader's selection bias enters.
- IS WINDOW ONLY: trades whose exit_date < HO_START (the locked holdout is
  never read - the council's blind-spot catch).
- DAILY STREAMS: exit-date attribution - a strategy's return on day D is the
  mean pnl_pct of its trades exiting D, reindexed over the IS trading days
  with 0 where it has no exit (cash otherwise; deflates single-strategy vol
  but is the correct grain for PORTFOLIO combination arithmetic).
- FLOOR: >= 30 IS trades per strategy (the program's min_trades bar).
- SHRINKAGE (item 11): James-Stein-style pull of each annualized Sharpe
  toward the cross-sectional mean, weight n/(n+k) with k=30 - flashy
  low-n Sharpes shrink hardest; disclosed as v1, not a fitted estimator.
- CAVEATS STAMPED INTO THE ARTIFACT: IS-only estimates of mostly
  unvalidated strategies carry winner's-curse; pairwise rho is
  regime-unstable; portfolio-level selection of sub-gate strategies imports
  219-way selection bias UP a level (the S6-B2178c decision package carries
  these verbatim).

Usage: PYTHONPATH=".;scripts" python scripts/build_strategy_return_correlation.py --basis gross|net
Writes output_audit/b2182_strategy_correlation.json + _summary.md on gross (the
B2182 artifact), ..._net.json + _net_summary.md on net, or --out and its summary.
S6-B3383 (B3139q-r158): --basis is REQUIRED (breadth_step1_grid.BASES, the
grids' vocabulary) - the streams averaged the raw pnl_pct by omission; 'net' is
roster_core.net_pnl. The script parses its arguments: an unknown one refuses,
and --help prints the usage, before the trade log is read or a file written.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

MIN_TRADES = 30
SHRINK_K = 30.0
SUBSET_N = 20

from breadth_step1_grid import BASES  # noqa: E402  (one basis vocabulary, S6-B3314)


def pnl_of(d, basis: str):
    """S6-B3383: the per-trade P&L the daily streams average - 'gross' is the
    raw pnl_pct (the basis of B2182's committed artifact), 'net' the roster's
    roster_core.net_pnl. One definition; main() calls nothing else."""
    import roster_core as rc
    if basis not in BASES:
        raise SystemExit(f"REFUSED: basis {basis!r} not in {BASES} (S6-B3383)")
    return rc.net_pnl(d["pnl_pct"]) if basis == "net" else d["pnl_pct"]


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="B2182: strategy-return correlation "
                                             "and effective breadth (S6-B3383)")
    ap.add_argument("--basis", required=True, choices=BASES,
                    help="S6-B3383: the pnl basis the streams average, stated on "
                         "every run and recorded on the artifact - no default")
    ap.add_argument("--out", default=None,
                    help="the JSON to write (default output_audit/"
                         "b2182_strategy_correlation[_net].json); the summary "
                         ".md sits beside it")
    a = ap.parse_args(argv)
    import numpy as np
    import pandas as pd
    from roster_core import HO_START

    d = pd.read_parquet(ROOT / "output_r5_merged_1_7" / "trade_log.parquet")
    d["exit_date"] = pd.to_datetime(d["exit_date"])
    is_mask = d["exit_date"].dt.date < HO_START
    d = d[is_mask]
    print(f"IS-window trades (exit < {HO_START}): {len(d)} across "
          f"{d.strategy.nunique()} strategies")

    counts = d.groupby("strategy").size()
    keep = counts[counts >= MIN_TRADES].index
    d = d[d.strategy.isin(keep)]
    print(f"strategies with >= {MIN_TRADES} IS trades: {len(keep)}")

    # daily exit-date-attributed streams over the IS trading days
    days = pd.Index(sorted(d["exit_date"].unique()), name="exit_date")
    d = d.assign(pnl_pct=pnl_of(d, a.basis))          # S6-B3383
    daily = (d.groupby(["exit_date", "strategy"])["pnl_pct"].mean()
             .unstack("strategy").reindex(days).fillna(0.0) / 100.0)

    corr = daily.corr(min_periods=20)
    n_s = corr.shape[0]
    iu = np.triu_indices(n_s, k=1)
    pair_rho = corr.values[iu]
    pair_rho = pair_rho[~np.isnan(pair_rho)]
    rho_bar = float(np.mean(pair_rho))

    ann = np.sqrt(252.0)
    mu, sd = daily.mean(), daily.std(ddof=1)
    sharpe = (mu / sd.replace(0, np.nan) * ann).dropna()
    n_tr = counts.reindex(sharpe.index)
    grand = float(sharpe.mean())
    w = n_tr / (n_tr + SHRINK_K)
    shrunk = (w * sharpe + (1 - w) * grand).sort_values(ascending=False)

    def port_sharpe(s_bar: float, n: int, rho: float) -> float:
        return s_bar * np.sqrt(n / (1 + (n - 1) * rho))

    # greedy min-rho subset seeded by shrunk Sharpe
    cand = list(shrunk.index)
    subset = [cand[0]]
    while len(subset) < min(SUBSET_N, len(cand)):
        best_name, best_score = None, None
        for name in cand:
            if name in subset:
                continue
            r = float(np.nanmean([corr.loc[name, s] for s in subset]))
            score = float(shrunk[name]) - r          # reward Sharpe, punish rho
            if best_score is None or score > best_score:
                best_name, best_score = name, score
        subset.append(best_name)
    sub_rho_vals = [corr.loc[a, b] for i, a in enumerate(subset)
                    for b in subset[i + 1:]]
    sub_rho = float(np.nanmean(sub_rho_vals))
    sub_sbar = float(shrunk[subset].mean())

    scenarios = {f"N={n}": {
        "s_bar_all_shrunk": round(grand, 4),
        "rho_bar_all": round(rho_bar, 4),
        "implied_portfolio_sharpe": round(port_sharpe(grand, n, rho_bar), 3),
    } for n in (10, 20, 40)}
    scenarios["greedy_subset"] = {
        "n": len(subset), "s_bar_shrunk": round(sub_sbar, 4),
        "rho_bar": round(sub_rho, 4),
        "implied_portfolio_sharpe": round(
            port_sharpe(sub_sbar, len(subset), sub_rho), 3),
        "members": subset,
    }

    out = {
        "source": "output_r5_merged_1_7/trade_log.parquet (production exits)",
        "basis": a.basis,                                 # S6-B3383
        "window": f"IS only: exit_date < {HO_START} (holdout untouched)",
        "strategies_analyzed": int(n_s),
        "trades_analyzed": int(len(d)),
        "avg_pairwise_rho": round(rho_bar, 4),
        "sharpe_cross_section": {
            "grand_mean_annualized": round(grand, 4),
            "median": round(float(sharpe.median()), 4),
            "top5_shrunk": {k: round(float(v), 3)
                            for k, v in shrunk.head(5).items()},
        },
        "portfolio_scenarios": scenarios,
        "caveats": [
            "IS-only estimates of mostly UNVALIDATED strategies - winner's "
            "curse compounds at portfolio level (S6-B2178c carries this)",
            "pairwise rho is regime-unstable; the crisis rho is the one that "
            "matters and one window cannot measure it",
            "zero-filled non-exit days deflate single-strategy vol; correct "
            "grain for combination arithmetic, wrong grain for standalone "
            "Sharpe claims",
        ],
    }
    jp = (Path(a.out) if a.out else ROOT / "output_audit" / (
        "b2182_strategy_correlation%s.json" % ("" if a.basis == "gross" else "_net")))
    jp.write_text(json.dumps(out, indent=1), encoding="utf-8")
    md = [
        "# Strategy-return correlation and effective breadth (B2182, zero engine runs)",
        "",
        f"- basis: {a.basis} (S6-B3383)",
        f"- IS trades analyzed: {len(d)} across {n_s} strategies (>= {MIN_TRADES} trades each)",
        f"- average pairwise rho: {rho_bar:.3f}",
        f"- cross-sectional annualized Sharpe: mean {grand:.3f}, median {float(sharpe.median()):.3f}",
        "",
        "| scenario | s_bar (shrunk) | rho_bar | implied portfolio Sharpe |",
        "|---|---|---|---|",
    ]
    for k, v in scenarios.items():
        sb = v.get("s_bar_all_shrunk", v.get("s_bar_shrunk"))
        md.append(f"| {k} | {sb} | {v.get('rho_bar_all', v.get('rho_bar'))} | "
                  f"{v['implied_portfolio_sharpe']} |")
    md += ["", "Caveats: " + " / ".join(out["caveats"])]
    jp.with_name(jp.stem + "_summary.md").write_text(
        "\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(out["portfolio_scenarios"], indent=1))
    print(f"[OK] wrote {jp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
