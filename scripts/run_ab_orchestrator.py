"""Batch 398 (2026-05-27): DEC-216 engine-consumption runner.

CLI wrapper that activates `backtest/results/ab_orchestrator.py` from
the command line.  Per DEC-216: this is the engine call-path consumer
the AUDIT_INDEX status drift complained about (module existed but no
one invoked it from a script).

Usage:
    python scripts/run_ab_orchestrator.py \\
        --winners-parquet output_phase_1a_beta_final/winners.parquet \\
        --trade-log-rules-only output_phase_1a_beta_final/trade_log.csv \\
        --output output_audit/ab_results.parquet

    # Three-arm flow (Phase 1B+):
    python scripts/run_ab_orchestrator.py \\
        --winners-parquet ... \\
        --trade-log-rules-only output_arm_a/trade_log.csv \\
        --trade-log-full-agents output_arm_b/trade_log.csv \\
        --trade-log-no-risk output_arm_c/trade_log.csv \\
        --output output_audit/ab_results.parquet
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from backtest.results.ab_orchestrator import orchestrate_ab_run


def _load_trade_log(p: Path | None, arm_label: str) -> pd.DataFrame:
    if p is None:
        return pd.DataFrame()
    if not p.exists():
        print(f"[WARN] {arm_label}: trade_log missing at {p}; using empty")
        return pd.DataFrame()
    if p.suffix == ".parquet":
        return pd.read_parquet(p)
    return pd.read_csv(p, low_memory=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--winners-parquet", required=True, type=Path,
                    help="winners.parquet from Phase 1A-beta extract_winners")
    ap.add_argument("--trade-log-rules-only", required=True, type=Path,
                    help="Arm A: rules-only trade log (Phase 1A-beta output)")
    ap.add_argument("--trade-log-full-agents", type=Path, default=None,
                    help="Arm B: full-with-veto trade log (Phase 1B output)")
    ap.add_argument("--trade-log-no-risk", type=Path, default=None,
                    help="Arm C: no-Risk trade log (Phase 1B output)")
    ap.add_argument("--output", type=Path, default=REPO / "output_audit" / "ab_results.parquet",
                    help="ab_results.parquet output path")
    args = ap.parse_args()

    if not args.winners_parquet.exists():
        print(f"[FATAL] winners.parquet missing: {args.winners_parquet}")
        return 1

    winners_df = pd.read_parquet(args.winners_parquet)
    print(f"[INFO] winners loaded: {len(winners_df)} P1 combos")

    trade_logs = {
        "rules_only":  _load_trade_log(args.trade_log_rules_only, "rules_only"),
        "full_agents": _load_trade_log(args.trade_log_full_agents, "full_agents"),
        "no_risk":     _load_trade_log(args.trade_log_no_risk, "no_risk"),
    }
    for arm, df in trade_logs.items():
        print(f"[INFO] arm {arm}: {len(df)} trades")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    results = orchestrate_ab_run(winners_df, trade_logs, output_path=args.output)
    print(f"[OK] ab_results written -> {args.output}")
    print(f"[OK] {len(results)} A/B verdicts computed")
    if not results.empty and "verdict" in results.columns:
        print(f"[OK] verdict distribution: {results['verdict'].value_counts().to_dict()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
