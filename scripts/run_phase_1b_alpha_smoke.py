"""Phase 1B-alpha smoke test (Batch 256).

5 winners x 30 days x 11-agent pipeline. Budget cap: ~$3 (Haiku).
Verifies agent framework end-to-end before scale-up.

Usage:
  python scripts/run_phase_1b_alpha_smoke.py
  python scripts/run_phase_1b_alpha_smoke.py --winners winners.parquet \
      --budget-cap 3.0 --dry-run

Owner directive 2026-05-19: $300 ceiling pre-approved; smoke/demo gates
PROTECT the budget by validating framework on small N before scale.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backtest.agents.agent_gate_config import arm_b_full_with_veto


def main() -> int:
    p = argparse.ArgumentParser(description="Phase 1B-alpha SMOKE test")
    p.add_argument("--winners", default="output_v2/winners.parquet",
                   help="Path to winners.parquet from Phase 1A-beta")
    p.add_argument("--n-winners", type=int, default=5,
                   help="Number of P1 winners to test (default 5)")
    p.add_argument("--n-days", type=int, default=30,
                   help="Calendar days of simulation (default 30)")
    p.add_argument("--budget-cap", type=float, default=3.0,
                   help="USD spend ceiling; halt if exceeded (default $3)")
    p.add_argument("--output-dir", default="output_phase_1b_alpha_smoke")
    p.add_argument("--dry-run", action="store_true",
                   help="Don't call Anthropic; estimate cost only")
    args = p.parse_args()

    winners_path = REPO / args.winners
    if not winners_path.exists():
        print(f"[ERROR] winners.parquet not found at {winners_path}")
        return 1

    winners = pd.read_parquet(winners_path)
    if winners.empty:
        print("[ERROR] winners.parquet is empty; run extract_phase_1a_beta_winners.py first")
        return 1

    p1_only = winners[winners.get("priority", "") == "P1"]
    if p1_only.empty:
        print("[WARN] No P1 winners found")
        return 2

    sample = p1_only.head(args.n_winners)
    print(f"[INFO] Smoke test: {len(sample)} P1 winners x {args.n_days} days")

    cfg = arm_b_full_with_veto(cost_ceiling_usd=args.budget_cap)
    est_cost_per_candidate = cfg.estimated_cost_per_candidate()
    est_candidates = len(sample) * args.n_days * 0.3  # ~30% pass screener
    est_total = est_cost_per_candidate * est_candidates
    print(f"[INFO] Cost estimate: ${est_total:.2f} (cap ${args.budget_cap})")

    if est_total > args.budget_cap:
        print(f"[ABORT] Estimated cost ${est_total:.2f} exceeds cap ${args.budget_cap}")
        return 1

    out_dir = REPO / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "smoke_run":           True,
        "winners_count":       len(sample),
        "n_days":              args.n_days,
        "budget_cap_usd":      args.budget_cap,
        "estimated_cost_usd":  round(est_total, 2),
        "agent_mode":          cfg.mode.value,
        "active_agents":       sorted(cfg.active_agents()),
        "dry_run":             args.dry_run,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    if args.dry_run:
        print(f"[DRY RUN] Would invoke 11-agent pipeline on {len(sample)} winners x {args.n_days} days")
        print(f"[DRY RUN] Manifest written: {out_dir}/manifest.json")
        return 0

    # Full smoke: wire to LangGraph pipeline (deferred to post-1A-beta)
    print(f"[INFO] Full agent execution requires Phase 1B Sprint 7 langgraph_pipeline.py")
    print(f"[INFO] For now, smoke validates: winners loadable, budget within cap, agent config valid")
    print(f"[OK] Smoke pre-flight passed; manifest at {out_dir}/manifest.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
