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
  - S6-B3237 CORRECTION (B3139q-r88): the next bullet is FALSE for the
    cubes this script reads. Phase 1A-beta cubes run with
    --no-regime-affinity (run_phase1a.py, Batch 384, auto-enabled), so
    they hold every strategy's trades in every regime that occurred -
    MEASURED: output_batch395_final holds adx_initiation (entry {bear})
    long trades in bull 373 and neutral 93, and R5 likewise. Both what
    removal drops and what it adds are observed; by_direction flags a
    regime-side cell with 0 trades. (Original B623 text follows.)
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
# S6-B3237: free_level_window / roster_core - the one in-sample window
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backtest.engine.regime_selector import (  # noqa: E402
    STRATEGY_REGIME_AFFINITY, should_strategy_fire_in_regime)


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


# S6-B1248-SHORT-REGIME-AFFINITY (B3139q-r79): the direction-aware defaults
# are DERIVED from the engine's own function on an empty affinity map, never
# restated - the restated copy kept Batch 291's short set {bear, crisis,
# neutral} after the owner withdrew that policy (2026-10-20, rec (a)).
_REGIMES = ("bull", "neutral", "bear", "crisis")
DEFAULT_LONG_REGIMES = {r for r in _REGIMES if should_strategy_fire_in_regime(
    "_unmapped", r, affinity={}, direction="long")}
DEFAULT_SHORT_REGIMES = {r for r in _REGIMES if should_strategy_fire_in_regime(
    "_unmapped", r, affinity={}, direction="short")}


# S6-B3237 (owner ruled 2026-10-21, 'Approve all recs execute', option (c)):
# the evidence for ruling the two-sided entries is read IN-SAMPLE only - the
# holdout read needs the owner's own word (runbook 0.6).
WINDOWS = ("is", "all")
_COLS = ("strategy", "direction", "regime", "pnl_pct", "entry_date", "win")
VERDICT_SCOPE = (
    "KEEP / REMOVE_OK compare the window's trades by regime. A Phase 1A-beta "
    "cube (B395, R5) runs with --no-regime-affinity (run_phase1a.py), so what "
    "removal drops AND what it adds are both observed; a regime-side cell "
    "with 0 trades is unobserved (R5's window holds no crisis day) and "
    "by_direction flags it. A run with the affinity ON holds only allowed "
    "regimes, and its added cells read 0 for that reason")


def load_trade_log(trade_log_path, strategies=None, window: str = "is"):
    """(rows, meta) - the rows the audit reads. Only the columns the audit
    uses, in chunks, keeping `strategies` (None keeps all): the R5 trade log
    is 4.6 GB. window 'is' (the DEFAULT) keeps the IN-SAMPLE rows only,
    through free_level_window.in_sample_only - roster_core's one entry-dated
    window, which fails closed if a holdout-entered row survives; 'all' keeps
    every row (the pre-S6-B3237 behaviour, for a historical cube read whole).
    Any other window is refused, and 'is' without entry_date is refused."""
    if window not in WINDOWS:
        raise ValueError(f"window must be one of {WINDOWS}, got {window!r}")
    head = list(pd.read_csv(trade_log_path, nrows=0).columns)
    cols = [c for c in _COLS if c in head]
    missing = {"strategy", "direction", "regime", "pnl_pct"} - set(cols)
    if missing:
        raise ValueError(f"{trade_log_path} lacks {sorted(missing)}")
    if window == "is" and "entry_date" not in cols:
        raise ValueError("window 'is' needs an entry_date column")
    parts = []
    for ch in pd.read_csv(trade_log_path, usecols=cols, chunksize=500_000,
                          low_memory=False):
        if strategies is not None:
            ch = ch[ch["strategy"].isin(set(strategies))]
        if len(ch):
            parts.append(ch)
    df = (pd.concat(parts, ignore_index=True) if parts
          else pd.DataFrame(columns=cols))
    meta = {"window": window, "rows_read": len(df), "split": None}
    if window == "is":
        from free_level_window import in_sample_only, split_windows
        meta["split"] = split_windows(df)
        df = in_sample_only(df)
    meta["rows_kept"] = len(df)
    return df, meta


def compare_per_direction(stats: pd.DataFrame, current_regimes: set) -> dict:
    """S6-B3237: what removing an explicit entry does to EACH side, from the
    trades the log holds - per direction, the regimes removal DROPS (the
    entry allows them, the side's default does not: observed n and pnl),
    KEEPS, and ADDS (the default allows them, the entry does not). An added
    set with 0 trades is flagged unobserved - in a Phase 1A-beta cube
    (affinity off) that regime did not occur for the side in the window; in
    a run with the affinity on it may have been blocked."""
    out = {}
    for d, default in (("long", DEFAULT_LONG_REGIMES),
                       ("short", DEFAULT_SHORT_REGIMES)):
        sd = (stats[stats["direction"] == d] if len(stats)
              else pd.DataFrame(columns=["regime", "n_trades", "total_pnl_pct"]))

        def agg(regs, sd=sd):
            sub = sd[sd["regime"].isin(regs)]
            n = int(sub["n_trades"].sum()) if len(sub) else 0
            tot = float(sub["total_pnl_pct"].sum()) if len(sub) else 0.0
            return {"regimes": sorted(regs), "n": n,
                    "total_pnl_pct": round(tot, 2),
                    "mean_pnl_pct": round(tot / n, 3) if n else None}
        added = agg(set(default) - set(current_regimes))
        out[d] = {"kept": agg(set(current_regimes) & set(default)),
                  "dropped": agg(set(current_regimes) - set(default)),
                  "added": {**added, "unobserved": added["n"] == 0}}
    return out


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


def audit(trade_log_path: Path, min_trades: int = 10, window: str = "is") -> dict:
    """Run the audit across the deferred dual entries (17 since B1465 made
    prev_day_high_break long-only). S6-B3237: `window` defaults to 'is' -
    the in-sample rows only (load_trade_log); total_trades counts the
    AUDITED strategies' rows in that window."""
    deferred = _identify_deferred_dual_entries()
    df, meta = load_trade_log(trade_log_path, {s for s, _ in deferred}, window)
    results = []
    for strategy, current_regimes in sorted(deferred):
        stats = compute_direction_stats(df, strategy)
        rec, cmp = classify_recommendation(stats, set(current_regimes), min_trades=min_trades)
        results.append({
            "strategy": strategy,
            "current_regimes": sorted(current_regimes),
            "recommendation": rec,
            "comparison": cmp,
            "by_direction": compare_per_direction(stats, set(current_regimes)),
            "stats": stats.to_dict(orient="records") if not stats.empty else [],
        })
    return {
        "trade_log_path": str(trade_log_path),
        "window": meta,
        "verdict_scope": VERDICT_SCOPE,
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
    w = audit_out.get("window") or {}
    lines.append(f"Window: {w.get('window')} - kept {w.get('rows_kept')} of {w.get('rows_read')} "
                 f"audited-strategy rows (split {w.get('split')})")
    lines.append(f"Scope: {audit_out.get('verdict_scope', '')}")
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

    # S6-B3237: per side, what removal drops (observed) and adds (unobserved)
    lines.append("")
    lines.append("PER SIDE - removal DROPS (observed) / ADDS (unobserved when n=0):")
    for r in audit_out["results"]:
        for d, v in (r.get("by_direction") or {}).items():
            dr, ad, kp = v["dropped"], v["added"], v["kept"]
            lines.append(
                f"  {r['strategy']:<28} {d:<5} kept {kp['regimes']} n={kp['n']} "
                f"mean={kp['mean_pnl_pct']} | drops {dr['regimes']} n={dr['n']} "
                f"mean={dr['mean_pnl_pct']} | adds {ad['regimes']} n={ad['n']}"
                + (" UNOBSERVED" if ad["unobserved"] and ad["regimes"] else ""))

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


def _parser():
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
    # S6-B3237: in-sample by default - the holdout read is the owner's
    parser.add_argument("--window", choices=WINDOWS, default="is",
                        help="is = in-sample rows only (default); all = every row")
    parser.add_argument("--out", type=Path, default=None,
                        help="also write the full audit JSON here")
    return parser


def main():
    args = _parser().parse_args()

    if not args.trade_log.exists():
        raise SystemExit(f"trade_log not found: {args.trade_log}")

    result = audit(args.trade_log, min_trades=args.min_trades, window=args.window)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
        print(f"Saved: {args.out}")
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
