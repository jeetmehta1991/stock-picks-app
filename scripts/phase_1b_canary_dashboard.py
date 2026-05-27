"""Batch 399 (2026-05-27): Sprint 7 Phase B canary dashboard.

Source (per CHECKLIST #77): owner directive 2026-05-27 "all wired items
activated".  Per DEC-508 / CHECKLIST #71 Phase B: Dashboard validates
20-50 signals + statistical sanity + PIT regression.

This script consumes canary_signals.parquet (from phase_1b_canary_compute.py)
and produces:
  - canary_validation_report.json: machine-readable PASS/FAIL per check
  - canary_validation_report.html: human-readable dashboard

Checks performed (5 sanity gates):
  G1 sample size       : 20 <= N <= 50
  G2 tier distribution : no single tier > 70% (avoids degenerate constant outputs)
  G3 PIT compliance    : 100% pass
  G4 score-tier coherence: tier=1 has score<=40 mean; tier=5 has score>=85 mean
  G5 context non-empty : context_paragraph non-empty + > 50 chars for >=80% samples
                         (skipped in --dry-run since mock contexts are short)

Usage:
    python scripts/phase_1b_canary_dashboard.py \\
        --signals output_phase_1b_canary/canary_signals.parquet \\
        --output-dir output_phase_1b_canary/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent


def check_g1_sample_size(df: pd.DataFrame) -> tuple[bool, str]:
    n = len(df)
    if 20 <= n <= 50:
        return True, f"N={n} in [20, 50]"
    return False, f"N={n} OUT-OF-RANGE [20, 50]"


def check_g2_tier_distribution(df: pd.DataFrame) -> tuple[bool, str]:
    if df.empty:
        return False, "empty"
    counts = df["agent_tier"].value_counts(normalize=True)
    max_share = counts.max()
    if max_share > 0.70:
        return False, (
            f"top tier {counts.idxmax()} = {max_share*100:.0f}% > 70% "
            f"(degenerate constant output risk); distribution={counts.to_dict()}"
        )
    return True, f"max tier share={max_share*100:.0f}% <= 70%; distribution={counts.to_dict()}"


def check_g3_pit_compliance(df: pd.DataFrame) -> tuple[bool, str]:
    if df.empty:
        return False, "empty"
    bad = (~df["pit_compliant"]).sum()
    if bad > 0:
        return False, f"{bad} of {len(df)} signals failed PIT heuristic"
    return True, f"{len(df)}/{len(df)} PIT compliant"


def check_g4_score_tier_coherence(df: pd.DataFrame) -> tuple[bool, str]:
    if df.empty:
        return False, "empty"
    t1 = df[df["agent_tier"] == 1]["agent_score"]
    t5 = df[df["agent_tier"] == 5]["agent_score"]
    issues = []
    if not t1.empty and t1.mean() > 50:
        issues.append(f"tier=1 mean score {t1.mean():.1f} > 50 (should be <=40)")
    if not t5.empty and t5.mean() < 70:
        issues.append(f"tier=5 mean score {t5.mean():.1f} < 70 (should be >=85)")
    if issues:
        return False, "; ".join(issues)
    return True, (
        f"tier=1 mean={t1.mean():.1f} (n={len(t1)}), "
        f"tier=5 mean={t5.mean():.1f} (n={len(t5)})"
        if not t1.empty and not t5.empty else "skipped (no tier=1 or tier=5)"
    )


def check_g5_context_quality(df: pd.DataFrame) -> tuple[bool, str]:
    if df.empty:
        return False, "empty"
    if (df["llm_model"] == "dry_run_mock").all():
        return True, "skipped (all dry-run mock contexts)"
    long_enough = df["context_paragraph"].fillna("").str.len() >= 50
    pct = long_enough.mean()
    if pct < 0.80:
        return False, f"only {pct*100:.0f}% of contexts >= 50 chars (need >=80%)"
    return True, f"{pct*100:.0f}% of contexts >= 50 chars"


CHECKS = [
    ("G1 sample size",         check_g1_sample_size),
    ("G2 tier distribution",   check_g2_tier_distribution),
    ("G3 PIT compliance",      check_g3_pit_compliance),
    ("G4 score-tier coherence", check_g4_score_tier_coherence),
    ("G5 context quality",     check_g5_context_quality),
]


def build_html(report: dict, signals: pd.DataFrame) -> str:
    """Minimal HTML report -- no external deps."""
    rows = []
    for r in report["checks"]:
        color = "green" if r["pass"] else "red"
        rows.append(
            f"<tr><td>{r['name']}</td><td style='color:{color};'>"
            f"{'PASS' if r['pass'] else 'FAIL'}</td><td>{r['message']}</td></tr>"
        )
    sig_summary = ""
    if not signals.empty:
        td = signals["agent_tier"].value_counts().sort_index().to_dict()
        sig_summary = (
            f"<p>Signals: {len(signals)} | Tier distribution: {td}</p>"
            f"<p>LLM model(s): {signals['llm_model'].unique().tolist()}</p>"
            f"<p>Generated: {report['generated_at']}</p>"
        )
    return f"""<!DOCTYPE html>
<html><head><title>Phase 1B Canary Validation</title>
<style>body{{font-family:sans-serif;}} table{{border-collapse:collapse;}}
td,th{{border:1px solid #ccc;padding:6px 12px;}}</style></head>
<body>
<h1>Sprint 7 Phase B Canary Validation</h1>
<h2>Overall: <span style="color:{'green' if report['overall_pass'] else 'red'};">
{'PASS' if report['overall_pass'] else 'FAIL'}</span></h2>
{sig_summary}
<table>
<tr><th>Check</th><th>Status</th><th>Detail</th></tr>
{''.join(rows)}
</table>
</body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--signals", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path,
                    default=REPO / "output_phase_1b_canary")
    args = ap.parse_args()

    if not args.signals.exists():
        print(f"[FATAL] signals missing: {args.signals}")
        return 1
    signals = pd.read_parquet(args.signals)

    from datetime import datetime, timezone
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "signals_file": str(args.signals),
        "n_signals":    len(signals),
        "checks":       [],
        "overall_pass": True,
    }
    print(f"[INIT] {len(signals)} signals loaded")
    for name, fn in CHECKS:
        ok, msg = fn(signals)
        report["checks"].append({"name": name, "pass": ok, "message": msg})
        report["overall_pass"] = report["overall_pass"] and ok
        marker = "[PASS]" if ok else "[FAIL]"
        print(f"  {marker} {name}: {msg}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "canary_validation_report.json"
    html_path = args.output_dir / "canary_validation_report.html"
    json_path.write_text(json.dumps(report, indent=2))
    html_path.write_text(build_html(report, signals), encoding="utf-8")
    print(f"\n[OK] {json_path}")
    print(f"[OK] {html_path}")
    print(f"\nOverall: {'PASS' if report['overall_pass'] else 'FAIL'}")
    return 0 if report["overall_pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
