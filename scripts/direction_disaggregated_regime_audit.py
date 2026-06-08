"""Batch 623 (2026-06-08) -- direction-disaggregated STRATEGY_REGIME
_AFFINITY audit per owner option D (Hybrid).

Reads an existing cube trade_log.csv + computes per-(strategy, direction,
regime) summary stats (n trades, mean pnl_pct, win-rate, Sharpe proxy).
For each of the 21 deferred dual _strat3 entries in STRATEGY_REGIME
_AFFINITY (kept at B617 family audit pending direction-disaggregated
validation), surfaces:
  - whether the LONG side empirically performs in the entry's regime set
  - whether the SHORT side empirically performs there
  - recommendation: REMOVE (let B291 direction-aware default apply) /
    KEEP-LONG-CONSTRAINED / KEEP-SHORT-CONSTRAINED / INSUFFICIENT_DATA

Source: trade_log.csv from a prior cube run (default
output_batch395_final/trade_log.csv with 29,360 trades from May 2026
cube).

CAVEATS:
  - The trade_log already reflects the explicit regime entry in force
    at run time, so the cube only observed trades the affinity ALLOWED.
    Direction-disaggregated stats here describe behavior conditional on
    the affinity gating - not what would happen if the affinity were
    removed. To get the latter (the counterfactual: what would the LONG
    side do in regimes where the dual entry currently BLOCKS it?),
    the small validation re-run (option D-ii per owner hybrid) is
    required: run cube with affinity removed on 3-5 strategies +
    compare.
  - This script answers: "given the affinity is currently {X}, does
    the LONG side or SHORT side dominate the trades that DID fire?"
    If a single direction completely dominates, the affinity is
    effectively a single-direction filter and B291 default would
    achieve the same gating; REMOVE is safe. If both sides have
    trades, the dual constraint is doing real work + needs the
    counterfactual re-run.

USAGE:
  python scripts/direction_disaggregated_regime_audit.py \\
      [--trade-log output_batch395_final/trade_log.csv] \\
      [--min-trades 10] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

# Make root importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY


# B617 audit identified 21 deferred dual strategies. Source of truth is
# the live STRATEGY_REGIME_AFFINITY map intersected with strategies
# emitting via _strat3.
def _identify_deferred_dual_entries() -> list[tuple[str, set]]:
    """Returns [(strategy_name, regime_set)] for dual _strat3 strategies
    that still have an explicit STRATEGY_REGIME_AFFINITY entry post-B617."""
    import inspect
    from backtest.signals import screener
    out = []
    for name, regimes in STRATEGY_REGIME_AFFINITY.items():
        fn = getattr(screener, f"strat_{name}", None)
        if fn is None:
            continue
        try:
            src = inspect.getsource(fn)
        except Exception:
            continue
        if "_strat3(" in src:
            out.append((name, regimes))
    return out


def compute_direction_stats(
    trade_log: pd.DataFrame,
    strategy: str,
) -> pd.DataFrame:
    """Per-(direction, regime) stats for one strategy."""
    sub = trade_log[trade_log["strategy"] == strategy]
    if sub.empty:
        return pd.DataFrame()
    g = sub.groupby(["direction", "regime"], dropna=False)
    stats = pd.DataFrame({
        "n_trades": g.size(),
        "mean_pnl_pct": g["pnl_pct"].mean(),
        "std_pnl_pct": g["pnl_pct"].std(),
        "win_rate": g["win"].mean() if "win" in sub.columns else g["pnl_pct"].apply(lambda s: (s > 0).mean()),
        "total_pnl_pct": g["pnl_pct"].sum(),
    }).reset_index()
    # Sharpe-proxy: mean/std (no annualization; relative comparison only)
    stats["sharpe_proxy"] = stats.apply(
        lambda r: (r["mean_pnl_pct"] / r["std_pnl_pct"])
                  if pd.notna(r["std_pnl_pct"]) and r["std_pnl_pct"] > 0
                  else None, axis=1,
    )
    return stats


DEFAULT_LONG_REGIMES = {"bull", "neutral"}
DEFAULT_SHORT_REGIMES = {"bear", "crisis", "neutral"}


def compare_keep_vs_remove(
    stats: pd.DataFrame, current_regimes: set
) -> dict:
    """For a strategy with explicit current_regimes affinity, compute
    total cumulative pnl_pct under KEEP (current dual entry) vs REMOVE
    (B291 direction-aware default applies per direction).

    Returns dict with keep_total_pnl + remove_total_pnl + keep_n +
    remove_n.

    KEEP semantics: trades in current_regimes count for BOTH directions
    (because the dual constraint applies to both).

    REMOVE semantics: LONG trades count in DEFAULT_LONG_REGIMES; SHORT
    trades count in DEFAULT_SHORT_REGIMES. (B291 direction-aware
    default.)
    """
    if stats.empty:
        return {"keep_total_pnl": 0.0, "remove_total_pnl": 0.0,
                "keep_n": 0, "remove_n": 0,
                "delta_pnl": 0.0}
    # KEEP: dual entry applies to both directions -> regime in current
    keep_mask = stats["regime"].isin(current_regimes)
    keep_total = float(stats.loc[keep_mask, "total_pnl_pct"].sum())
    keep_n = int(stats.loc[keep_mask, "n_trades"].sum())

    # REMOVE: direction-aware default
    long_mask = (stats["direction"] == "long") & stats["regime"].isin(DEFAULT_LONG_REGIMES)
    short_mask = (stats["direction"] == "short") & stats["regime"].isin(DEFAULT_SHORT_REGIMES)
    remove_total = float(stats.loc[long_mask | short_mask, "total_pnl_pct"].sum())
    remove_n = int(stats.loc[long_mask | short_mask, "n_trades"].sum())

    return {
        "keep_total_pnl": round(keep_total, 2),
        "remove_total_pnl": round(remove_total, 2),
        "delta_pnl": round(remove_total - keep_total, 2),
        "keep_n": keep_n,
        "remove_n": remove_n,
    }


def classify_recommendation(
    stats: pd.DataFrame, current_regimes: set, min_trades: int = 10
) -> tuple[str, dict]:
    """Decide KEEP / REMOVE / INSUFFICIENT based on actual KEEP-vs-REMOVE
    total PnL comparison + sufficiency floor.

    Returns (verdict, comparison_dict).

    Decision rule:
      - If stats empty -> NO_TRADES
      - If <min_trades total in current regime set -> INSUFFICIENT_DATA
      - If REMOVE total PnL >= KEEP total PnL with sufficient n -> REMOVE
      - Else -> KEEP
    """
    if stats.empty:
        return "NO_TRADES", {}
    in_regime = stats[stats["regime"].isin(current_regimes)]
    if in_regime.empty:
        return "NO_TRADES_IN_REGIME", {}

    cmp = compare_keep_vs_remove(stats, current_regimes)

    if cmp["keep_n"] < min_trades and cmp["remove_n"] < min_trades:
        return "INSUFFICIENT_DATA", cmp

    # Decision: prefer REMOVE if it doesn't lose PnL AND has min trades.
    if cmp["delta_pnl"] >= -5.0 and cmp["remove_n"] >= min_trades:
        # REMOVE doesn't materially lose vs KEEP (within 5pct-points slack)
        return "REMOVE_OK", cmp
    if cmp["delta_pnl"] < -5.0:
        # KEEP dominates by more than 5pp - dual entry is doing real work
        return "KEEP", cmp
    if cmp["remove_n"] < min_trades:
        return "KEEP_REMOVE_INSUFFICIENT", cmp
    return "KEEP", cmp


def audit(trade_log_path: Path, min_trades: int = 10) -> dict:
    """Run the audit across all 21 deferred dual entries."""
    df = pd.read_csv(trade_log_path)
    deferred = _identify_deferred_dual_entries()
    results = []
    for strategy, current_regimes in sorted(deferred):
        stats = compute_direction_stats(df, strategy)
        rec, cmp = classify_recommendation(stats, set(current_regimes), min_trades=min_trades)
        results.append({
            "strategy": strategy,
            "current_regimes": sorted(current_regimes),
            "recommendation": rec,
            "comparison": cmp,
            "stats": stats.to_dict(orient="records") if not stats.empty else [],
        })
    return {
        "trade_log_path": str(trade_log_path),
        "total_trades": len(df),
        "deferred_strategies_audited": len(deferred),
        "results": results,
    }


def _format_summary(audit_out: dict) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("DIRECTION-DISAGGREGATED REGIME-AFFINITY AUDIT (B623)")
    lines.append("=" * 100)
    lines.append(f"Trade log: {audit_out['trade_log_path']} ({audit_out['total_trades']} trades)")
    lines.append(f"Deferred dual entries audited: {audit_out['deferred_strategies_audited']}")
    lines.append("")
    lines.append(f"{'Strategy':<32} {'Current':<22} {'KEEP-PnL':>9} {'REMOVE-PnL':>11} {'Delta':>8} {'Verdict'}")
    lines.append("-" * 100)
    for r in audit_out["results"]:
        regimes_str = ",".join(r["current_regimes"])[:22]
        c = r.get("comparison", {})
        keep_pnl = c.get("keep_total_pnl", 0.0)
        rem_pnl = c.get("remove_total_pnl", 0.0)
        delta = c.get("delta_pnl", 0.0)
        lines.append(
            f"{r['strategy']:<32} {regimes_str:<22} "
            f"{keep_pnl:>9.1f} {rem_pnl:>11.1f} {delta:>+8.1f} "
            f"{r['recommendation']}"
        )
    lines.append("=" * 100)

    # Per-strategy detail for non-trivial cases
    interesting = [r for r in audit_out["results"]
                   if r["recommendation"] not in ("NO_TRADES", "NO_TRADES_IN_REGIME")]
    if interesting:
        lines.append("")
        lines.append("PER-STRATEGY DETAIL (cells with trades):")
        for r in interesting:
            lines.append(f"\n{r['strategy']} (current regimes: {r['current_regimes']}) -> {r['recommendation']}")
            for c in r["stats"]:
                lines.append(
                    f"  {c['direction']:<6} regime={c['regime']:<10} "
                    f"n={int(c['n_trades']):>4} "
                    f"mean={c['mean_pnl_pct']:>6.2f}% "
                    f"win={c['win_rate']:>5.2f} "
                    f"sharpe~{(c['sharpe_proxy'] or 0):>6.3f}"
                )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trade-log", type=Path,
        default=Path("output_batch395_final/trade_log.csv"),
        help="Path to cube trade_log.csv")
    parser.add_argument("--min-trades", type=int, default=10,
                        help="Minimum n per (direction, regime) cell to make a decision")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--save-json", action="store_true",
                        help="Save full audit to output_audit/direction_disagg_audit.json")
    args = parser.parse_args()

    if not args.trade_log.exists():
        raise SystemExit(f"trade_log not found: {args.trade_log}")

    result = audit(args.trade_log, min_trades=args.min_trades)
    if args.save_json:
        out = Path("output_audit/direction_disagg_audit.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
        print(f"Saved: {out}")
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(_format_summary(result))


if __name__ == "__main__":
    main()
