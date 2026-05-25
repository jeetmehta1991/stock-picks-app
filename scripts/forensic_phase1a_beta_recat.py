"""Forensic re-categorization of Phase 1A-beta strategies.

Source (per CHECKLIST #77): owner directive 2026-05-25 "Start with forensic
batches." Reads `output_phase_1a_beta_merged_local/trade_log.csv` (7191
trades, 66 fired strategies) and computes empirical fire-rate +
PnL summary per Cat-A/B/C bucket from PHASE_1A_BETA_QUIET_STRATEGY_FORENSIC.md.

For each strategy in the forensic doc's Cat-A 13, Cat-B 22, Cat-C 14,
this script reports:
  - n_trades:   actual fire count in Phase 1A-beta
  - wr_pct:     win rate
  - mean_pnl:   per-trade mean PnL
  - sum_pp:     sum of PnL points
  - verdict:    QUIET (0 fires) / RARE (1-19) / NORMAL (20+)

Output:
  output_audit/phase1a_beta_recat.json    (machine-readable)
  output_audit/phase1a_beta_recat.md      (human-readable per-bucket table)

The verdict crystallizes which Cat-B strategies actually broke (still 0
trades after data-missing fix verification) vs. which work (firing at
some baseline). Same for Cat-C cannibalization hypothesis.

Usage:
  python scripts/forensic_phase1a_beta_recat.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


# --- Canonical buckets from PHASE_1A_BETA_QUIET_STRATEGY_FORENSIC.md -------
# Suffix `_long` / `_short` is implicit per the forensic doc; we use the
# strategy name as it appears in the trade_log `strategy` column.

CAT_A_TIGHT = [
    "52w_high_breakout",
    "52w_low_breakdown",
    "52wh_break_retest",
    "bb_squeeze_volume",
    "squeeze_breakout",
    "cup_and_handle_long",
    "head_and_shoulders_bottom_long",
    "double_bottom_long",
    "triangle_ascending_long",
    "flag_bull_long",
    "inside_bar_breakout",
    "pre_holiday_long",
    "halloween_seasonal_long",
    "totm_long",
]

CAT_B_DATA_MISSING = [
    # Index rebalance (4)
    "post_inclusion_drift_long",
    "post_inclusion_reversal_short",
    "post_deletion_drift_short",
    "pre_rebalance_long",
    # Pairs trading (2)
    "pairs_mean_reversion_long",
    "pairs_mean_reversion_short",
    # Pre-FOMC (2)
    "pre_fomc_long_sleeve",
    "pre_fomc_quality_momentum_long",
    # Cross-asset (3)
    "gold_silver_risk_off_long",
    "dxy_headwind_multinational_short",
    "sector_rotation_defensive_long",
    # Multi-timeframe HTF (2)
    "weekly_bias_pullback_long",
    "weekly_bias_pullback_short",
    # SMC/ICT (4)
    "smc_equal_highs_sweep_short",
    "smc_equal_lows_sweep_long",
    "smc_mitigation_block_long",
    "smc_mitigation_block_short",
    # News-shift (1)
    "news_sentiment_shift_long",
    # Insider (1)
    "insider_cluster_with_director_long",
    # Misc (1; vix_backwardation_long already in Batch 312)
    "pivot_fib_confluence",
]

CAT_C_INVESTIGATE = [
    "avwap_20high_rejection_short",
    "camarilla_rsi_obv",
    "camarilla_rsi_obv_short",
    "cpr_narrow_momentum_short",
    "donchian_10_breakout",
    "donchian_breakdown_short",
    "ichimoku_cloud_breakdown",
    "keltner_lower",
    "prev_day_low_breakdown",
    "rsi9_extreme",
    "rsi_overbought_short",
    "rsi_volume_200ema",
    "supertrend_ichimoku_adx",
    "supertrend_macd_short",
    "break_retest_volume",
    "value_area_breakout_long",
]

BUCKETS = {
    "Cat-A_Tight": CAT_A_TIGHT,
    "Cat-B_Data-Missing": CAT_B_DATA_MISSING,
    "Cat-C_Investigate": CAT_C_INVESTIGATE,
}

# Batch 316a un-deprecated strategies (Batch 218 deprecation reversed by
# owner directive 2026-05-25). At Phase 1A-beta run time these were under
# Batch 218 deprecation so most would have been filtered OUT of the
# screener loop; some legacy traces remain (williams_stoch_dual fired 5
# trades 0% WR; camarilla_r3/s3 fired 1-2 trades) - the forensic interest
# is whether any actually produced edge.
UN_DEPRECATED_23 = [
    # Moving-average crossovers (Zakamulin 2014; Faber 2013)
    "golden_cross_50_200", "golden_cross_9_21", "golden_cross_20_50",
    "golden_cross_volume", "death_cross_50_200_volume",
    # Indicator-derivative singles (Marshall-Cahan 2008; Park-Irwin 2007)
    "awesome_oscillator", "ppo_crossover", "tema_dema",
    "force_index_breakout", "mfi_oversold",
    # Parabolic SAR (Park-Irwin 2007; Lukac-Brorsen-Irwin 1988)
    "parabolic_sar_flip", "parabolic_sar_flip_short",
    # Candlestick patterns (Marshall-Young-Cahan 2008; Horton 2009)
    "morning_star", "evening_star_short", "three_white_soldiers",
    "doji_at_support", "bullish_engulfing_support", "shooting_star_short",
    # Williams %R dual-combo
    "williams_stoch_dual",
    # Plain MACD (Hudson-Atanasova-Urquhart 2022)
    "macd_crossover", "macd_crossover_short",
    # Camarilla R3/S3 plain heuristic (Marshall-Cahan 2008)
    "camarilla_r3_breakout", "camarilla_s3_bounce",
]
assert len(UN_DEPRECATED_23) == 23, f"expected 23 got {len(UN_DEPRECATED_23)}"


# Passing-criteria thresholds for the per-strategy verdict (per
# CLAUDE.md). Per-regime thresholds are LOWER than overall thresholds
# (per BUG-31/32/33 codification).
PASS_OVERALL = {
    "min_trades":   100,
    "min_wr_pct":   55,
    "min_pf":       1.5,
    "min_sharpe":   1.0,
    "max_dd_pp":    20.0,
}
PASS_PER_REGIME = {
    "min_trades":   30,
    "min_wr_pct":   50,  # high-vol allowance
    "min_pf":       1.3,
    "min_sharpe":   0.7,
    "max_dd_pp":    20.0,
}


def per_strategy_verdict_against_criteria(df: pd.DataFrame, strategy: str) -> dict:
    """Apply the 5 numeric passing-criteria to a strategy."""
    sub = df[df["strategy"] == strategy]
    n = len(sub)
    if n == 0:
        return {"verdict": "QUIET", "reason": "0 trades", "n": 0}

    wr = (sub["win"].astype(bool).sum() / n) * 100 if "win" in sub.columns else 0.0
    mean_pnl = float(sub["pnl_pct"].mean()) if "pnl_pct" in sub.columns else 0.0
    sum_pp = float(sub["pnl_pct"].sum()) if "pnl_pct" in sub.columns else 0.0

    wins = sub[sub["win"].astype(bool)] if "win" in sub.columns else sub.head(0)
    losses = sub[~sub["win"].astype(bool)] if "win" in sub.columns else sub.head(0)
    gross_win = float(wins["pnl_pct"].sum()) if not wins.empty else 0.0
    gross_loss_abs = float(abs(losses["pnl_pct"].sum())) if not losses.empty else 0.0
    pf = (gross_win / gross_loss_abs) if gross_loss_abs > 0 else (
        float("inf") if gross_win > 0 else 0.0
    )

    # Simple per-trade Sharpe proxy: mean / std
    std_pnl = float(sub["pnl_pct"].std()) if n >= 2 else 0.0
    sharpe = (mean_pnl / std_pnl) if std_pnl > 0 else 0.0

    # Crude max-drawdown on cumulative pp curve
    cum = sub["pnl_pct"].cumsum()
    running_max = cum.cummax()
    dd = (cum - running_max).min() if not cum.empty else 0.0
    max_dd_pp = float(abs(dd))

    # Use overall thresholds when n >= 100, else per-regime
    criteria = PASS_OVERALL if n >= 100 else PASS_PER_REGIME
    fails = []
    if n < criteria["min_trades"]:
        fails.append(f"n={n} < {criteria['min_trades']}")
    if wr < criteria["min_wr_pct"]:
        fails.append(f"wr={wr:.1f} < {criteria['min_wr_pct']}")
    if pf < criteria["min_pf"]:
        fails.append(f"pf={pf:.2f} < {criteria['min_pf']}")
    if sharpe < criteria["min_sharpe"]:
        fails.append(f"sharpe={sharpe:.2f} < {criteria['min_sharpe']}")
    if max_dd_pp > criteria["max_dd_pp"]:
        fails.append(f"dd={max_dd_pp:.1f} > {criteria['max_dd_pp']}")

    verdict = "PASS" if not fails else ("INSUFFICIENT_DATA" if n < 30 else "FAIL")
    return {
        "n":         n,
        "wr_pct":    round(wr, 2),
        "mean_pnl":  round(mean_pnl, 3),
        "sum_pp":    round(sum_pp, 2),
        "pf":        round(pf, 2) if pf != float("inf") else "inf",
        "sharpe":    round(sharpe, 2),
        "max_dd_pp": round(max_dd_pp, 2),
        "criteria_band": "overall" if n >= 100 else "per_regime",
        "verdict":   verdict,
        "failures":  fails,
    }


def regime_breakdown(df: pd.DataFrame) -> dict:
    """Compute per-regime aggregate PnL + per-strategy worst-regime drivers."""
    if "regime" not in df.columns:
        return {"error": "regime column missing"}
    out: dict = {"regimes": {}, "worst_regime_drivers": {}}
    for regime, sub in df.groupby("regime"):
        n = len(sub)
        wr = (sub["win"].astype(bool).sum() / n) * 100 if "win" in sub.columns else 0.0
        sum_pp = float(sub["pnl_pct"].sum()) if "pnl_pct" in sub.columns else 0.0
        out["regimes"][str(regime)] = {
            "n_trades": int(n),
            "wr_pct":   round(wr, 2),
            "mean_pnl": round(float(sub["pnl_pct"].mean()), 3),
            "sum_pp":   round(sum_pp, 2),
        }
    # Per-regime: which strategies are the biggest negative contributors?
    for regime, sub in df.groupby("regime"):
        per_strat = sub.groupby("strategy")["pnl_pct"].agg(["sum", "count", "mean"])
        per_strat = per_strat.sort_values("sum")
        worst = per_strat.head(5).reset_index()
        out["worst_regime_drivers"][str(regime)] = [
            {
                "strategy": r["strategy"],
                "n_trades": int(r["count"]),
                "sum_pp":   round(float(r["sum"]), 2),
                "mean_pnl": round(float(r["mean"]), 3),
            }
            for _, r in worst.iterrows()
        ]
    return out


def verdict_for(n_trades: int) -> str:
    if n_trades == 0:
        return "QUIET"
    if n_trades < 20:
        return "RARE"
    return "NORMAL"


def summarize_strategy(df: pd.DataFrame, strategy: str) -> dict[str, Any]:
    sub = df[df["strategy"] == strategy]
    n = len(sub)
    row: dict[str, Any] = {"strategy": strategy, "n_trades": n}
    if n == 0:
        row.update({
            "wr_pct": None, "mean_pnl_pct": None, "sum_pp": None,
            "verdict": "QUIET",
        })
        return row
    wr = (sub["win"].astype(bool).sum() / n) * 100 if "win" in sub.columns else None
    row.update({
        "wr_pct": round(wr, 2) if wr is not None else None,
        "mean_pnl_pct": round(float(sub["pnl_pct"].mean()), 3),
        "sum_pp": round(float(sub["pnl_pct"].sum()), 2),
        "median_hold_days": round(float(sub["hold_days"].median()), 1)
            if "hold_days" in sub.columns else None,
        "verdict": verdict_for(n),
    })
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trade-log",
        default="output_phase_1a_beta_merged_local/trade_log.csv")
    ap.add_argument("--output-dir", default="output_audit")
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tl_path = Path(args.trade_log)
    if not tl_path.exists():
        print(f"ERROR: {tl_path} not found")
        return 1

    df = pd.read_csv(tl_path, low_memory=False)
    print(f"Loaded {len(df)} trades from {tl_path}")
    print(f"Distinct strategies that fired: {df['strategy'].nunique()}")

    summary: dict[str, Any] = {
        "source": str(tl_path),
        "n_total_trades": int(len(df)),
        "n_strategies_fired": int(df["strategy"].nunique()),
        "buckets": {},
    }

    for bucket_name, strategies in BUCKETS.items():
        rows = [summarize_strategy(df, s) for s in strategies]
        verdict_counts: dict[str, int] = {}
        for r in rows:
            verdict_counts[r["verdict"]] = verdict_counts.get(r["verdict"], 0) + 1
        summary["buckets"][bucket_name] = {
            "n_in_bucket": len(strategies),
            "rows": rows,
            "verdict_counts": verdict_counts,
        }
        print(f"\n[{bucket_name}] {len(strategies)} strategies; verdict counts: {verdict_counts}")

    # Batch 353: un-deprecated 23 verdict
    un_dep_rows = [summarize_strategy(df, s) for s in UN_DEPRECATED_23]
    un_dep_counts: dict[str, int] = {}
    for r in un_dep_rows:
        un_dep_counts[r["verdict"]] = un_dep_counts.get(r["verdict"], 0) + 1
    summary["un_deprecated_23"] = {
        "n_in_bucket": 23,
        "rows": un_dep_rows,
        "verdict_counts": un_dep_counts,
    }
    print(f"\n[Un-Deprecated 23 (Batch 316a)] 23 strategies; verdict counts: {un_dep_counts}")

    # Batch 352b: per-strategy passing-criteria verdict for ALL 66 fired strategies
    fired_strategies = sorted(df["strategy"].unique())
    criteria_verdicts = {}
    pass_count = 0
    fail_count = 0
    insufficient_count = 0
    for strat in fired_strategies:
        v = per_strategy_verdict_against_criteria(df, strat)
        criteria_verdicts[strat] = v
        if v["verdict"] == "PASS":
            pass_count += 1
        elif v["verdict"] == "FAIL":
            fail_count += 1
        else:
            insufficient_count += 1
    summary["passing_criteria_verdicts"] = {
        "n_strategies":         len(fired_strategies),
        "verdict_counts":       {
            "PASS":               pass_count,
            "FAIL":               fail_count,
            "INSUFFICIENT_DATA":  insufficient_count,
        },
        "per_strategy":         criteria_verdicts,
    }
    print(f"\n[Passing-Criteria Verdicts] {len(fired_strategies)} fired strategies; "
          f"PASS={pass_count} FAIL={fail_count} INSUFFICIENT={insufficient_count}")

    # Batch 354: regime-bias audit
    summary["regime_breakdown"] = regime_breakdown(df)
    print("\n[Regime Breakdown]")
    for regime, stats in summary["regime_breakdown"].get("regimes", {}).items():
        print(f"  {regime}: n={stats['n_trades']} sum_pp={stats['sum_pp']} wr={stats['wr_pct']}%")

    json_path = out_dir / "phase1a_beta_recat.json"
    json_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(f"\n[OK] JSON: {json_path}")

    # Human-readable MD
    md = []
    md.append("# Phase 1A-beta forensic re-categorization")
    md.append("")
    md.append("**Source** (per CHECKLIST #77 canonical-source attribution):")
    md.append(f"- Trade log: `{tl_path}` ({summary['n_total_trades']} trades, "
              f"{summary['n_strategies_fired']} fired strategies)")
    md.append("- Bucket lists: PHASE_1A_BETA_QUIET_STRATEGY_FORENSIC.md")
    md.append("- Generator: `scripts/forensic_phase1a_beta_recat.py` (Batch 352)")
    md.append("")
    md.append("**Verdict legend:**")
    md.append("- `QUIET`: 0 trades fired in Phase 1A-beta")
    md.append("- `RARE`: 1-19 trades (sub-threshold for per-regime statistical power)")
    md.append("- `NORMAL`: 20+ trades")
    md.append("")
    for bucket_name, bucket_data in summary["buckets"].items():
        md.append(f"## {bucket_name}")
        md.append("")
        md.append(f"**Verdict counts:** {bucket_data['verdict_counts']}")
        md.append("")
        md.append("| Strategy | n | WR% | Mean PnL% | Sum pp | Verdict |")
        md.append("|---|---:|---:|---:|---:|---|")
        for r in bucket_data["rows"]:
            wr = r["wr_pct"] if r["wr_pct"] is not None else "-"
            mp = r["mean_pnl_pct"] if r["mean_pnl_pct"] is not None else "-"
            sp = r["sum_pp"] if r["sum_pp"] is not None else "-"
            md.append(f"| `{r['strategy']}` | {r['n_trades']} | {wr} | {mp} | {sp} | {r['verdict']} |")
        md.append("")

    # Un-Deprecated 23 (Batch 353)
    md.append("## Un-Deprecated 23 (Batch 316a)")
    md.append("")
    md.append("Strategies un-deprecated by Batch 316a 2026-05-25 (Batch 218 deprecation reversed).")
    md.append("At Phase 1A-beta run time, most of these were filtered OUT by Batch 218; few legacy trades remain.")
    md.append("")
    un = summary["un_deprecated_23"]
    md.append(f"**Verdict counts:** {un['verdict_counts']}")
    md.append("")
    md.append("| Strategy | n | WR% | Mean PnL% | Sum pp | Verdict |")
    md.append("|---|---:|---:|---:|---:|---|")
    for r in un["rows"]:
        wr = r["wr_pct"] if r["wr_pct"] is not None else "-"
        mp = r["mean_pnl_pct"] if r["mean_pnl_pct"] is not None else "-"
        sp = r["sum_pp"] if r["sum_pp"] is not None else "-"
        md.append(f"| `{r['strategy']}` | {r['n_trades']} | {wr} | {mp} | {sp} | {r['verdict']} |")
    md.append("")

    # Passing-Criteria Verdicts (Batch 352b)
    pcv = summary["passing_criteria_verdicts"]
    md.append("## Passing-Criteria Verdicts (66 fired strategies)")
    md.append("")
    md.append(f"Per-strategy verdict against CLAUDE.md passing criteria. n>=100 uses overall thresholds (WR>=55, PF>=1.5, Sharpe>=1.0); 30<=n<100 uses per-regime thresholds (WR>=50, PF>=1.3, Sharpe>=0.7).")
    md.append("")
    md.append(f"**Aggregate:** {pcv['verdict_counts']}")
    md.append("")
    md.append("| Strategy | n | WR% | PF | Sharpe | DD pp | Band | Verdict | Failures |")
    md.append("|---|---:|---:|---:|---:|---:|---|---|---|")
    # Sort: PASS first (alphabetical), then FAIL, then INSUFFICIENT
    def _sort_key(item):
        strat, v = item
        order = {"PASS": 0, "FAIL": 1, "INSUFFICIENT_DATA": 2, "QUIET": 3}
        return (order.get(v["verdict"], 9), strat)
    for strat, v in sorted(pcv["per_strategy"].items(), key=_sort_key):
        fails = "; ".join(v.get("failures", [])) or "-"
        md.append(f"| `{strat}` | {v['n']} | {v.get('wr_pct', '-')} | {v.get('pf', '-')} | "
                  f"{v.get('sharpe', '-')} | {v.get('max_dd_pp', '-')} | "
                  f"{v.get('criteria_band', '-')} | {v['verdict']} | {fails} |")
    md.append("")

    # Regime Breakdown (Batch 354)
    rb = summary["regime_breakdown"]
    md.append("## Regime-Bias Breakdown (Batch 354)")
    md.append("")
    if "regimes" in rb:
        md.append("### Per-regime aggregate")
        md.append("")
        md.append("| Regime | n | WR% | Mean PnL% | Sum pp |")
        md.append("|---|---:|---:|---:|---:|")
        for regime, stats in sorted(rb["regimes"].items(),
                                     key=lambda x: -abs(x[1]["sum_pp"])):
            md.append(f"| {regime} | {stats['n_trades']} | {stats['wr_pct']} | "
                      f"{stats['mean_pnl']} | {stats['sum_pp']} |")
        md.append("")
        md.append("### Worst-5 strategies per regime (largest negative PnL contributors)")
        md.append("")
        for regime, drivers in rb["worst_regime_drivers"].items():
            md.append(f"#### {regime}")
            md.append("")
            md.append("| Strategy | n | Sum pp | Mean PnL% |")
            md.append("|---|---:|---:|---:|")
            for d in drivers:
                md.append(f"| `{d['strategy']}` | {d['n_trades']} | {d['sum_pp']} | {d['mean_pnl']} |")
            md.append("")

    md_path = out_dir / "phase1a_beta_recat.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(f"[OK] MD:   {md_path}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
