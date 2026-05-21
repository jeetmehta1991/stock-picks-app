"""Phase 1A-beta IS/OOS split reporter (Batch 297).
Source: per CHECKLIST #77 - canonical-source attribution.
Reads from output_phase_1a_beta_merged/trade_log.csv produced by the
Phase 1A-beta run; output paths documented in argparse.

Per DESIGN_AUDIT_PART_3 sec-3 + owner directive 2026-05-21: per-strategy
exit assignments (STRATEGY_EXIT_OVERRIDE) were derived from Stage C
2021-2023 in-sample data. Phase 1A-beta (2022-2026 full window) overlaps
the same period. To produce honest out-of-sample metrics, this script
splits the trade_log by entry_date and reports per-(strategy x exit x
period) cube separately.

IS window:  2022-01-01 to 2024-06-30  (~2.5 years, includes 2022 bear,
                                        2023 recovery, 2024 H1 rally)
OOS window: 2024-07-01 to 2026-04-30  (~1.8 years, includes 2024 H2 bull,
                                        2025-2026 environment)

Output:
  - is_metrics.json:  WR / mean / sum / sharpe for IS period
  - oos_metrics.json: same for OOS period
  - per_strategy_is_oos.csv: per-strategy IS vs OOS comparison
  - per_cell_is_oos.csv: per-(strategy x exit_reason) IS vs OOS
  - IS_OOS_REPORT.md: human-readable summary highlighting regression
                       between IS and OOS metrics

Usage:
  python scripts/phase_1a_beta_is_oos_report.py --output-dir output_phase_1a_beta_merged
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd


IS_END = date(2024, 6, 30)
OOS_START = date(2024, 7, 1)


def _agg_metrics(df: pd.DataFrame, label: str) -> dict:
    if df.empty:
        return {"period": label, "n": 0, "wr": 0.0, "mean": 0.0, "sum_pp": 0.0}
    return {
        "period": label,
        "n": len(df),
        "wr": round((df["pnl_pct"] > 0).mean() * 100, 2),
        "mean": round(df["pnl_pct"].mean(), 2),
        "sum_pp": round(df["pnl_pct"].sum(), 1),
        "sharpe_proxy": round(
            df["pnl_pct"].mean() / df["pnl_pct"].std() * (252 ** 0.5)
            if df["pnl_pct"].std() > 0 else 0.0,
            2,
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output_phase_1a_beta_merged")
    args = parser.parse_args()

    out = Path(args.output_dir)
    tl_path = out / "trade_log.csv"
    if not tl_path.exists():
        print(f"ERROR: {tl_path} not found")
        sys.exit(1)

    tl = pd.read_csv(tl_path)
    tl["entry_dt"] = pd.to_datetime(tl["entry_date"]).dt.date

    is_df = tl[tl["entry_dt"] <= IS_END].copy()
    oos_df = tl[tl["entry_dt"] >= OOS_START].copy()

    is_metrics = _agg_metrics(is_df, "IS_2022-01_2024-06")
    oos_metrics = _agg_metrics(oos_df, "OOS_2024-07_2026-04")

    with open(out / "is_metrics.json", "w") as f:
        json.dump(is_metrics, f, indent=2)
    with open(out / "oos_metrics.json", "w") as f:
        json.dump(oos_metrics, f, indent=2)

    # Per-strategy IS vs OOS
    rows = []
    for strat in sorted(tl["strategy"].unique()):
        is_sub = is_df[is_df["strategy"] == strat]
        oos_sub = oos_df[oos_df["strategy"] == strat]
        rows.append({
            "strategy": strat,
            "is_n": len(is_sub),
            "is_wr_pct": round((is_sub["pnl_pct"] > 0).mean() * 100, 2)
                if not is_sub.empty else 0.0,
            "is_mean_pct": round(is_sub["pnl_pct"].mean(), 2)
                if not is_sub.empty else 0.0,
            "is_sum_pp": round(is_sub["pnl_pct"].sum(), 1)
                if not is_sub.empty else 0.0,
            "oos_n": len(oos_sub),
            "oos_wr_pct": round((oos_sub["pnl_pct"] > 0).mean() * 100, 2)
                if not oos_sub.empty else 0.0,
            "oos_mean_pct": round(oos_sub["pnl_pct"].mean(), 2)
                if not oos_sub.empty else 0.0,
            "oos_sum_pp": round(oos_sub["pnl_pct"].sum(), 1)
                if not oos_sub.empty else 0.0,
            "oos_minus_is_mean": round(
                oos_sub["pnl_pct"].mean() - is_sub["pnl_pct"].mean(), 2
            ) if not oos_sub.empty and not is_sub.empty else None,
        })
    per_strat = pd.DataFrame(rows).sort_values(
        "oos_sum_pp", ascending=False, na_position="last"
    )
    per_strat.to_csv(out / "per_strategy_is_oos.csv", index=False)

    # Per-(strategy x exit) cube IS vs OOS
    if "exit_reason" in tl.columns:
        is_cells = is_df.groupby(["strategy", "exit_reason"]).agg(
            is_n=("pnl_pct", "count"),
            is_wr_pct=("pnl_pct", lambda x: (x > 0).mean() * 100),
            is_mean_pct=("pnl_pct", "mean"),
            is_sum_pp=("pnl_pct", "sum"),
        ).round(2)
        oos_cells = oos_df.groupby(["strategy", "exit_reason"]).agg(
            oos_n=("pnl_pct", "count"),
            oos_wr_pct=("pnl_pct", lambda x: (x > 0).mean() * 100),
            oos_mean_pct=("pnl_pct", "mean"),
            oos_sum_pp=("pnl_pct", "sum"),
        ).round(2)
        cells = is_cells.join(oos_cells, how="outer").fillna(0)
        cells.to_csv(out / "per_cell_is_oos.csv")

    # Markdown report
    md = []
    md.append("# Phase 1A-beta IS/OOS validity report")
    md.append("")
    md.append(f"**IS window**: 2022-01 -> 2024-06 (~2.5y)")
    md.append(f"**OOS window**: 2024-07 -> 2026-04 (~1.8y)")
    md.append(f"**Source**: {tl_path}")
    md.append("")
    md.append("## Aggregate")
    md.append(f"| | IS | OOS |")
    md.append(f"|---|---:|---:|")
    md.append(f"| n | {is_metrics['n']} | {oos_metrics['n']} |")
    md.append(f"| WR | {is_metrics['wr']}% | {oos_metrics['wr']}% |")
    md.append(f"| Mean PnL | {is_metrics['mean']:+.2f}% | {oos_metrics['mean']:+.2f}% |")
    md.append(f"| Sum pp | {is_metrics['sum_pp']:+.1f} | {oos_metrics['sum_pp']:+.1f} |")
    md.append(f"| Sharpe proxy | {is_metrics.get('sharpe_proxy','N/A')} | {oos_metrics.get('sharpe_proxy','N/A')} |")
    md.append("")
    md.append("## Overfitting verdict")
    delta = oos_metrics["mean"] - is_metrics["mean"]
    if abs(delta) > 1.0:
        verdict = (
            "**OVERFITTING SUSPECT**: OOS mean PnL differs from IS by >1pp. "
            "Per-strategy exit assignments may be over-tuned to 2022-2023 data."
        )
    elif delta < -0.5:
        verdict = (
            "**MILD OVERFITTING**: OOS underperforms IS by 0.5-1pp. "
            "Per-(strategy x exit) assignments hold up but with some drift."
        )
    else:
        verdict = (
            "**OOS HOLDS**: OOS within 0.5pp of IS. Per-strategy assignments "
            "generalize."
        )
    md.append(verdict)
    md.append("")
    md.append("## Top 10 strategies by OOS aggregate")
    md.append("")
    md.append("| Strategy | IS n | IS mean | OOS n | OOS mean | OOS-IS delta |")
    md.append("|---|---:|---:|---:|---:|---:|")
    for _, row in per_strat.head(10).iterrows():
        md.append(
            f"| {row['strategy']} | {row['is_n']} | {row['is_mean_pct']:+.2f}% | "
            f"{row['oos_n']} | {row['oos_mean_pct']:+.2f}% | "
            f"{row['oos_minus_is_mean'] if row['oos_minus_is_mean'] is not None else 'N/A'} |"
        )
    md.append("")
    md.append("## Bottom 10 by OOS aggregate")
    md.append("")
    md.append("| Strategy | IS n | IS mean | OOS n | OOS mean | OOS-IS delta |")
    md.append("|---|---:|---:|---:|---:|---:|")
    for _, row in per_strat.tail(10).iterrows():
        md.append(
            f"| {row['strategy']} | {row['is_n']} | {row['is_mean_pct']:+.2f}% | "
            f"{row['oos_n']} | {row['oos_mean_pct']:+.2f}% | "
            f"{row['oos_minus_is_mean'] if row['oos_minus_is_mean'] is not None else 'N/A'} |"
        )
    md.append("")
    md.append("Per-(strategy x exit) cube: see per_cell_is_oos.csv")
    md.append("")

    (out / "IS_OOS_REPORT.md").write_text("\n".join(md))
    print(f"Wrote: is_metrics.json, oos_metrics.json, per_strategy_is_oos.csv, "
          f"per_cell_is_oos.csv, IS_OOS_REPORT.md  to {out}")
    print()
    print(verdict)


if __name__ == "__main__":
    main()
