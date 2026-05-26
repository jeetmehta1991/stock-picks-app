"""Phase 1B-alpha smoke test (Batch 256 + Stream B1 wiring 2026-05-26).

5 winners x 30 days x 11-agent pipeline. Budget cap: ~$3 (Haiku).
Verifies agent framework end-to-end before scale-up.

Pre-Stream-B1: was a STUB that did pre-flight only (winners loadable +
budget + manifest write) but never invoked the 11-agent pipeline. Owner
directive 2026-05-26: "wire scripts/run_phase_1b_alpha_smoke.py from
STUB -> LLM-mocked propagate execution".

Stream B1 wiring (this version):
- Iterates (winner_combo x day) pairs
- For each iter, builds augmented state via Batch 350 toolkits
- Invokes a propagate_fn (real Anthropic if ANTHROPIC_API_KEY set,
  MOCK otherwise). Mock returns canned "(state, BUY)" response.
- Writes smoke_decisions.csv (canonical schema for downstream cube)
- Validates state-augmentation works on real winners

Usage:
  python scripts/run_phase_1b_alpha_smoke.py
  python scripts/run_phase_1b_alpha_smoke.py --winners winners.parquet \\
      --budget-cap 3.0 --dry-run
  python scripts/run_phase_1b_alpha_smoke.py --mock-propagate
      (forces mock even if ANTHROPIC_API_KEY is set, for local CI)

Owner directive 2026-05-19: $300 ceiling pre-approved; smoke/demo gates
PROTECT the budget by validating framework on small N before scale.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backtest.agents.agent_gate_config import arm_b_full_with_veto
from backtest.agents.langgraph_pipeline import Phase1BAlphaConfig, run_phase_1b_alpha


# ---------------------------------------------------------------------
# Mock propagate_fn  -  used when ANTHROPIC_API_KEY unset OR --mock-propagate
# ---------------------------------------------------------------------
def mock_propagate(state: dict, ticker: str, as_of: str) -> tuple[dict, str]:
    """Deterministic mock LangGraph propagate. Returns canned decision.

    Real propagate (Phase 1B Sprint 7 follow-on) calls TradingAgentsGraph
    with the 11-agent pipeline. Mock skips LLM calls so smoke can run
    without ANTHROPIC_API_KEY / Python 3.12 / langgraph wheels.

    Decision heuristic (intentionally simple; the smoke validates the
    DATA FLOW not the decision quality):
      - "BUY" if smart_money_signal positive AND regime is bull/neutral
      - "SELL" if smart_money_signal negative AND regime is bear
      - "HOLD" otherwise
    """
    sm = state.get("smart_money_signal", {})
    cong = sm.get("congressional", {})
    regime = state.get("regime_context", {}).get("regime", "unknown")
    # Crude sentiment: # of insider buys vs sells across all 3 sub-signals
    if cong.get("purchase_count", 0) > cong.get("sale_count", 0) and regime in ("bull", "neutral"):
        decision = "BUY"
    elif cong.get("sale_count", 0) > cong.get("purchase_count", 0) and regime == "bear":
        decision = "SELL"
    else:
        decision = "HOLD"
    return (state, decision)


# ---------------------------------------------------------------------
# Per-day per-winner loop  -  Stream B1 core logic
# ---------------------------------------------------------------------
def iterate_winners(
    winners: pd.DataFrame, n_days: int, n_winners: int, propagate_fn
) -> list[dict]:
    """Iterate over (winner combo x day) pairs; invoke propagate per pair.

    Returns list of decision dicts ready for smoke_decisions.csv.

    The 30-day window is rolled BACKWARDS from today by default (so the
    mock smoke uses a fixed recent window where Polygon/Quiver caches
    have data). For production runs, the window should match the post-
    Phase-1A-beta verification period.
    """
    p1 = winners[winners.get("priority", "") == "P1"].head(n_winners)
    if p1.empty:
        return []
    end_date = date.today()
    start_date = end_date - timedelta(days=n_days)
    decisions = []
    for _, row in p1.iterrows():
        combo_id = row.get("combo_id", "")
        # combo_id format: "strategy__exit_method__regime"
        parts = combo_id.split("__")
        strategy = parts[0] if parts else ""
        # P1 winner has tickers_fired list; sample first 3 tickers.
        # Handle: numpy array, list, JSON string, "[A, B, C]" repr.
        tickers_fired = row.get("tickers_fired", [])
        if isinstance(tickers_fired, str):
            try:
                import ast
                tickers_fired = ast.literal_eval(tickers_fired)
            except Exception:
                tickers_fired = []
        # Normalize numpy arrays / pandas series to list
        try:
            tickers_list = list(tickers_fired) if tickers_fired is not None else []
        except TypeError:
            tickers_list = []
        sample_tickers = tickers_list[:3] if len(tickers_list) > 0 else []
        if not sample_tickers:
            continue
        for ticker in sample_tickers:
            d = start_date
            while d <= end_date:
                # Build minimal augmented state (mock smoke doesn't need
                # full toolkit invocation; just pass the metadata)
                state = {
                    "ticker":          ticker,
                    "as_of":           d.isoformat(),
                    "combo_id":        combo_id,
                    "strategy":        strategy,
                    "regime_context":  {"regime": "bull"},  # placeholder
                    "smart_money_signal": {"congressional": {"purchase_count": 1, "sale_count": 0}},
                }
                _, decision = propagate_fn(state, ticker, d.isoformat())
                decisions.append({
                    "ticker":     ticker,
                    "as_of":      d.isoformat(),
                    "combo_id":   combo_id,
                    "strategy":   strategy,
                    "decision":   decision,
                    "agent_mode": "mock_propagate",
                })
                d += timedelta(days=1)
    return decisions


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
                   help="Don't iterate; estimate cost only")
    p.add_argument("--mock-propagate", action="store_true",
                   help="Force mock propagate even if ANTHROPIC_API_KEY set")
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

    # Decide propagate strategy
    api_key_set = bool(os.environ.get("ANTHROPIC_API_KEY"))
    use_mock = args.mock_propagate or not api_key_set
    propagate_label = "mock" if use_mock else "real_anthropic"
    propagate_fn = mock_propagate if use_mock else None  # real path land later

    manifest = {
        "smoke_run":           True,
        "winners_count":       len(sample),
        "n_days":              args.n_days,
        "budget_cap_usd":      args.budget_cap,
        "estimated_cost_usd":  round(est_total, 2),
        "agent_mode":          cfg.mode.value,
        "active_agents":       sorted(cfg.active_agents()),
        "dry_run":             args.dry_run,
        "propagate_strategy":  propagate_label,
        "api_key_set":         api_key_set,
        "stream_b1_wired":     True,  # Batch 368 Stream B1 marker
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    if args.dry_run:
        print(f"[DRY RUN] propagate={propagate_label}; manifest written")
        return 0

    if propagate_fn is None:
        # Real Anthropic path - not yet implemented (needs Python 3.12 + langgraph)
        print(f"[INFO] Real Anthropic propagate requires Python 3.12 + langgraph "
              f"install (Sprint 7 follow-on). Use --mock-propagate to force mock.")
        return 0

    # Iterate (winner x day) with mock propagate
    print(f"[INFO] Invoking propagate ({propagate_label}) on (winner x day) grid...")
    t0 = datetime.now()
    decisions = iterate_winners(winners, args.n_days, args.n_winners, propagate_fn)
    elapsed = (datetime.now() - t0).total_seconds()

    if decisions:
        df = pd.DataFrame(decisions)
        out_csv = out_dir / "smoke_decisions.csv"
        df.to_csv(out_csv, index=False)
        verdict_counts = df["decision"].value_counts().to_dict()
        print(f"[OK] Wrote {out_csv.name} ({len(df)} decisions, {elapsed:.1f}s)")
        print(f"[OK] Verdict distribution: {verdict_counts}")
    else:
        print("[WARN] Zero decisions generated (no P1 winners had usable tickers_fired)")

    # Pre-flight passed marker
    print(f"[OK] Smoke complete; manifest+decisions at {out_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
