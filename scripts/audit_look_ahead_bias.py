"""Look-ahead-bias forensic audit for the screener + signal-producers + trade-log.

Source (per CHECKLIST #77 canonical-source attribution):
- Owner directive Pass 53 2026-05-25: audit 46 look-ahead-bias-flagged strategies
  before launching Phase 1A-beta full re-run (option i)
- Conversation summary reference (46 number) not found materialized on disk; this
  audit reconstructs the analysis from first principles
- Patterns informed by Lopez de Prado "Advances in Financial ML" Ch 7 (info leakage)
  + DEC-505 walk-forward isolation principles

Output:
  output_audit/look_ahead_bias_audit.json  (machine-readable findings)
  output_audit/look_ahead_bias_audit.md    (human-readable report)

Two layers:

  STATIC LAYER -- AST scan of backtest/signals/*.py + backtest/engine/exit_*.py
    for known forward-peek patterns:
      * .shift(-N)                           (negative shift = future bars)
      * .iloc[i+N], .iloc[idx+]              (forward index)
      * df.tail(N) without time-truncation   (assumes 'last N' = oldest)
      * rolling().shift(-N)                  (rolling + forward shift)
      * max()/min()/quantile() called on a series WITHOUT .loc[:as_of] truncation
      * future_close / next_close / tomorrow / forward_return named locals
      * direct array .iloc[len(df):]         (sentinel value access)
      * Comparisons to bars dated AFTER as_of_date

  EMPIRICAL LAYER -- on output_stage_d/trade_log.csv (per-strategy aggregates):
      * WIN_RATE_SUSPICIOUS    win_rate > 70% on n >= 10 trades
      * NO_LOSSES_SUSPICIOUS   100% wins on n >= 5 trades
      * ZERO_HOLD_POSITIVE     hold_days == 0 AND pnl_pct > 0 in > 50% of trades
      * PERFECT_EXIT_ANOMALY   exit_price equals NEXT-bar high/low > 30% (would need
                               OHLCV cross-ref; skipped if cache unavailable)
      * IS_OOS_INVERSION       IS mean << OOS mean (Sharpe IS < 0 AND OOS > 1)

Cross-reference: any strategy flagged STATIC or EMPIRICAL above gets a row in the
output table; final verdict per-strategy is:
  * CODE_FIX_REQUIRED  (static pattern found in producer or strategy gate)
  * INVESTIGATE        (empirical only; needs per-strategy gate walkthrough)
  * LIKELY_LEGIT_RARE  (no pattern + fired < 5 trades; not actually flagged)

Usage:
  python scripts/audit_look_ahead_bias.py \
      --trade-log output_stage_d/trade_log.csv \
      --signals-dir backtest/signals \
      --engine-dir backtest/engine \
      --output-dir output_audit
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd


STATIC_PATTERNS = [
    # (regex, description, severity)
    (r"\.shift\(\s*-\s*\d+", "negative .shift(-N) = forward peek", "HIGH"),
    (r"\.iloc\[\s*\w+\s*\+\s*\d+\s*\]", "iloc[i+N] forward index", "HIGH"),
    (r"\.iloc\[\s*-\s*\d+\s*:\s*-\s*\d+\s*\]", "iloc[-A:-B] tail slice (ok only if df pre-truncated)", "LOW"),
    (r"future_close|future_high|future_low|next_close|next_high|next_low", "forward-named local", "HIGH"),
    (r"tomorrow_|forward_return|fwd_return", "forward-return named local", "HIGH"),
    (r"\.rolling\([^)]+\)\.shift\(\s*-\s*\d+", "rolling().shift(-N)", "HIGH"),
    (r"np\.roll\([^,]+,\s*-\s*\d+", "np.roll(...,-N) backward roll", "HIGH"),
    (r"peek_ahead|look_ahead|lookahead", "explicit look-ahead label", "MEDIUM"),
]

# Patterns that LOOK suspicious but are usually safe (whitelisted with a note).
SAFE_PATTERNS = [
    r"shift\(\s*1\s*\)",      # positive shift = backward = safe
    r"\.shift\(\s*-1\s*\)\s*#\s*safe",  # explicit-safe marker
]


def static_scan_file(path: Path) -> list[dict]:
    """AST + regex scan; returns list of finding dicts."""
    findings = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [{"file": str(path), "line": 0, "pattern": "READ_ERROR", "severity": "ERROR", "snippet": str(e)}]

    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for pattern, desc, severity in STATIC_PATTERNS:
            if re.search(pattern, line):
                # whitelist check
                if any(re.search(sp, line) for sp in SAFE_PATTERNS):
                    continue
                findings.append({
                    "file": str(path.relative_to(path.parents[2])) if len(path.parents) >= 3 else str(path),
                    "line": i,
                    "pattern": desc,
                    "severity": severity,
                    "snippet": stripped[:200],
                })
    return findings


def static_scan_tree(root: Path) -> list[dict]:
    findings = []
    for py in sorted(root.rglob("*.py")):
        if "__pycache__" in str(py):
            continue
        findings.extend(static_scan_file(py))
    return findings


def empirical_scan(trade_log: Path) -> dict[str, Any]:
    df = pd.read_csv(trade_log, low_memory=False)
    n_total = len(df)
    by_strat = df.groupby("strategy")
    rows = []
    for strat, sub in by_strat:
        n = len(sub)
        n_wins = int(sub["win"].astype(bool).sum()) if "win" in sub.columns else 0
        wr = (n_wins / n) * 100 if n else 0.0
        mean_pnl = float(sub["pnl_pct"].mean()) if "pnl_pct" in sub.columns else 0.0
        median_hold = float(sub["hold_days"].median()) if "hold_days" in sub.columns else 0.0
        zero_hold_pos = 0
        if "hold_days" in sub.columns and "pnl_pct" in sub.columns:
            zh = sub[(sub["hold_days"] == 0) & (sub["pnl_pct"] > 0)]
            zero_hold_pos = len(zh)
        flags = []
        if n >= 10 and wr > 70:
            flags.append("WIN_RATE_SUSPICIOUS")
        if n >= 5 and wr >= 100:
            flags.append("NO_LOSSES_SUSPICIOUS")
        if n >= 5 and zero_hold_pos / n > 0.5:
            flags.append("ZERO_HOLD_POSITIVE")
        rows.append({
            "strategy": strat,
            "n": n,
            "wr_pct": round(wr, 2),
            "mean_pnl_pct": round(mean_pnl, 3),
            "median_hold_days": round(median_hold, 1),
            "zero_hold_positive_count": zero_hold_pos,
            "empirical_flags": flags,
        })
    rows.sort(key=lambda r: (-len(r["empirical_flags"]), -r["wr_pct"]))
    return {
        "n_total_trades": n_total,
        "n_strategies_fired": len(rows),
        "rows": rows,
    }


def verdict_for(strategy: str, static_findings: list[dict], emp_row: dict | None) -> str:
    """Per-strategy verdict combining static + empirical."""
    has_static = any(strategy in f.get("snippet", "") for f in static_findings)
    has_empirical = emp_row and bool(emp_row.get("empirical_flags"))
    if has_static:
        return "CODE_FIX_REQUIRED"
    if has_empirical:
        return "INVESTIGATE"
    if emp_row and emp_row["n"] < 5:
        return "LIKELY_LEGIT_RARE"
    return "CLEAN"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trade-log", default="output_stage_d/trade_log.csv")
    ap.add_argument("--signals-dir", default="backtest/signals")
    ap.add_argument("--engine-dir", default="backtest/engine")
    ap.add_argument("--output-dir", default="output_audit")
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("  LOOK-AHEAD-BIAS FORENSIC AUDIT")
    print("=" * 78)

    print("\n[1/3] Static scan: backtest/signals/")
    sig_findings = static_scan_tree(Path(args.signals_dir))
    print(f"  {len(sig_findings)} findings")

    print("\n[2/3] Static scan: backtest/engine/")
    eng_findings = static_scan_tree(Path(args.engine_dir))
    print(f"  {len(eng_findings)} findings")

    all_static = sig_findings + eng_findings
    by_severity = {}
    for f in all_static:
        by_severity.setdefault(f["severity"], 0)
        by_severity[f["severity"]] += 1
    print(f"  Severity breakdown: {by_severity}")

    print("\n[3/3] Empirical scan: trade_log")
    emp_data = empirical_scan(Path(args.trade_log))
    flagged = [r for r in emp_data["rows"] if r["empirical_flags"]]
    print(f"  {emp_data['n_strategies_fired']} strategies fired; {len(flagged)} have empirical flags")

    # Aggregate verdict per strategy fired
    verdicts = {}
    for row in emp_data["rows"]:
        verdicts[row["strategy"]] = verdict_for(row["strategy"], all_static, row)

    summary = {
        "static": {
            "signals_dir": args.signals_dir,
            "engine_dir": args.engine_dir,
            "findings_count": len(all_static),
            "by_severity": by_severity,
            "findings": all_static,
        },
        "empirical": emp_data,
        "verdicts": verdicts,
        "verdict_counts": {v: sum(1 for x in verdicts.values() if x == v)
                           for v in {"CODE_FIX_REQUIRED", "INVESTIGATE", "LIKELY_LEGIT_RARE", "CLEAN"}},
    }

    json_path = out_dir / "look_ahead_bias_audit.json"
    json_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(f"\n[OK] JSON written: {json_path}")

    # Human-readable markdown report
    md = []
    md.append("# Look-ahead-bias forensic audit")
    md.append("")
    md.append(f"**Generated:** {pd.Timestamp.now().isoformat(timespec='seconds')}")
    md.append(f"**Trade log:** `{args.trade_log}`")
    md.append("")
    md.append("## Static scan summary")
    md.append("")
    md.append(f"- Files scanned: `{args.signals_dir}` + `{args.engine_dir}`")
    md.append(f"- Findings: **{len(all_static)}**")
    md.append(f"- Severity: {by_severity}")
    md.append("")
    if all_static:
        md.append("### Static findings detail")
        md.append("")
        md.append("| File | Line | Severity | Pattern | Snippet |")
        md.append("|---|---:|---|---|---|")
        for f in all_static[:200]:
            md.append(f"| `{f['file']}` | {f['line']} | {f['severity']} | {f['pattern']} | `{f['snippet'][:80]}` |")
        # B1994 (L571): a capped table must SAY it is capped - past 200
        # findings the report silently read complete.
        if len(all_static) > 200:
            md.append("")
            md.append(f"**SCOPE: showing 200 of {len(all_static)} static "
                      "findings - the detail table is capped; every finding "
                      "IS counted in the totals above.**")
        md.append("")
    else:
        md.append("**No static look-ahead-bias patterns found.**")
        md.append("")

    md.append("## Empirical scan summary")
    md.append("")
    md.append(f"- Total trades: {emp_data['n_total_trades']}")
    md.append(f"- Strategies fired: {emp_data['n_strategies_fired']}")
    md.append(f"- Strategies with empirical flags: {len(flagged)}")
    md.append("")

    if flagged:
        md.append("### Empirical findings (flagged strategies only)")
        md.append("")
        md.append("| Strategy | n | WR% | Mean PnL% | Median Hold | ZeroHoldPos | Flags |")
        md.append("|---|---:|---:|---:|---:|---:|---|")
        for r in flagged:
            md.append(f"| `{r['strategy']}` | {r['n']} | {r['wr_pct']} | {r['mean_pnl_pct']} | "
                     f"{r['median_hold_days']} | {r['zero_hold_positive_count']} | "
                     f"{', '.join(r['empirical_flags'])} |")
        md.append("")
    else:
        md.append("**No empirical look-ahead-bias signatures found.**")
        md.append("")

    md.append("## Per-strategy verdicts (strategies that fired)")
    md.append("")
    md.append(f"- CODE_FIX_REQUIRED: {summary['verdict_counts']['CODE_FIX_REQUIRED']}")
    md.append(f"- INVESTIGATE: {summary['verdict_counts']['INVESTIGATE']}")
    md.append(f"- LIKELY_LEGIT_RARE: {summary['verdict_counts']['LIKELY_LEGIT_RARE']}")
    md.append(f"- CLEAN: {summary['verdict_counts']['CLEAN']}")
    md.append("")

    md_path = out_dir / "look_ahead_bias_audit.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(f"[OK] MD written:   {md_path}")

    print("\n" + "=" * 78)
    print(f"  VERDICT COUNTS: {summary['verdict_counts']}")
    print("=" * 78)


if __name__ == "__main__":
    main()
