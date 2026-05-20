"""Phase 1B-alpha demo (Batch 256).

20 winners x 1 quarter x 11-agent pipeline. Budget cap: ~$10 (Haiku).
Owner gate before full $50-150 run.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backtest.agents.agent_gate_config import arm_b_full_with_veto


def main() -> int:
    p = argparse.ArgumentParser(description="Phase 1B-alpha DEMO")
    p.add_argument("--winners", default="output_v2/winners.parquet")
    p.add_argument("--n-winners", type=int, default=20)
    p.add_argument("--n-days", type=int, default=90)
    p.add_argument("--budget-cap", type=float, default=10.0)
    p.add_argument("--output-dir", default="output_phase_1b_alpha_demo")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    winners_path = REPO / args.winners
    if not winners_path.exists():
        print(f"[ERROR] winners.parquet not found at {winners_path}")
        return 1

    winners = pd.read_parquet(winners_path)
    p1_only = winners[winners.get("priority", "") == "P1"]
    if p1_only.empty:
        print("[WARN] No P1 winners")
        return 2

    sample = p1_only.head(args.n_winners)
    cfg = arm_b_full_with_veto(cost_ceiling_usd=args.budget_cap)
    est_total = cfg.estimated_cost_per_candidate() * len(sample) * args.n_days * 0.3
    print(f"[INFO] Demo: {len(sample)} winners x {args.n_days} days; est ${est_total:.2f} (cap ${args.budget_cap})")
    if est_total > args.budget_cap:
        print(f"[ABORT] estimate ${est_total:.2f} > cap ${args.budget_cap}")
        return 1

    out_dir = REPO / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "demo_run": True, "winners_count": len(sample), "n_days": args.n_days,
        "budget_cap_usd": args.budget_cap, "estimated_cost_usd": round(est_total, 2),
        "dry_run": args.dry_run,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"[OK] Demo manifest written to {out_dir}/manifest.json")
    if args.dry_run:
        return 0
    print(f"[INFO] Full agent execution requires Phase 1B Sprint 7 langgraph_pipeline.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
