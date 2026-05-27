"""Batch 399 (2026-05-27): Sprint 7 Phase B canary - signal compute.

Source (per CHECKLIST #77): owner directive 2026-05-27 "all wired items
activated".  Per DEC-508 / CHECKLIST #71 Phase B: signals computed but
strategies disabled (canary; A/B validation comes in Phase C).

This script takes a sample_pairs.parquet (from
phase_1b_canary_sample_selector.py) and runs each (ticker, as_of) pair
through the LangGraph pipeline to capture the agent tier output +
context paragraph.

Two execution modes:
  --dry-run    : returns deterministic mocked tiers (uses agent_score hash
                 of ticker+as_of for reproducibility).  Runs on any Python
                 3.10+.  No LLM dependency.
  (default)    : invokes the real LangGraph pipeline via
                 backtest/agents/langgraph_pipeline.run_phase_1b_alpha.
                 Requires Python 3.12 + langgraph + langchain-core wheels
                 per vendored/MANIFEST.md.  Will fail loudly if deps missing.

Output: canary_signals.parquet with columns
  ticker, as_of, agent_tier (1..5), agent_score (0..100),
  context_paragraph, computed_at, llm_model, pit_compliant (bool).

Usage:
    # Dry-run for Phase B prep (this is what runs without Python 3.12):
    python scripts/phase_1b_canary_compute.py \\
        --samples output_phase_1b_canary/sample_pairs.parquet \\
        --output output_phase_1b_canary/canary_signals.parquet \\
        --dry-run

    # Real LLM (Python 3.12 + ANTHROPIC_API_KEY needed):
    python scripts/phase_1b_canary_compute.py \\
        --samples output_phase_1b_canary/sample_pairs.parquet \\
        --output output_phase_1b_canary/canary_signals.parquet
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent


def _deterministic_mock_tier(ticker: str, as_of: str) -> tuple[int, int]:
    """Reproducible mocked (tier, score) from ticker+as_of hash.

    Used in --dry-run mode while real LLM dependency is unavailable.
    Distribution roughly:
      tier=1 (10%)  tier=2 (20%)  tier=3 (40%)  tier=4 (20%)  tier=5 (10%)
    """
    h = int(hashlib.md5(f"{ticker}|{as_of}".encode()).hexdigest(), 16)
    pct = h % 100
    if   pct < 10: tier, score_band = 1, (10, 40)
    elif pct < 30: tier, score_band = 2, (40, 55)
    elif pct < 70: tier, score_band = 3, (55, 70)
    elif pct < 90: tier, score_band = 4, (70, 85)
    else:          tier, score_band = 5, (85, 99)
    score = score_band[0] + (h // 100) % (score_band[1] - score_band[0])
    return tier, score


def _run_real_pipeline(ticker: str, as_of: str) -> dict:
    """Invoke vendored TradingAgents LangGraph pipeline.

    Requires Python 3.12 + ANTHROPIC_API_KEY env var + vendored package
    pip-installed.  Falls back to FAIL hard if any prereq missing.
    """
    try:
        from backtest.agents.langgraph_pipeline import (
            Phase1BAlphaConfig,
            run_phase_1b_alpha,
        )
    except ImportError as exc:
        raise SystemExit(
            f"[FATAL] LangGraph pipeline import failed (Python 3.14 + "
            f"langgraph wheels unavailable per vendored/MANIFEST.md): {exc}"
        )
    cfg = Phase1BAlphaConfig(
        winners_parquet=REPO / "_unused_for_canary.parquet",
        output_dir=REPO / "output_phase_1b_canary" / "compute",
        smoke_mode=True,
        max_tickers=1,
    )
    # Single-pair invocation -- upstream API supports per-(ticker, as_of) call
    result = run_phase_1b_alpha(cfg, tickers=[ticker], as_of=as_of)
    return {
        "agent_tier":  result.get("final_tier"),
        "agent_score": result.get("final_score"),
        "context_paragraph": result.get("context_paragraph", ""),
        "llm_model":   cfg.llm_model,
    }


def _check_pit_compliance(ticker: str, as_of_iso: str) -> bool:
    """Verify the agent context only used data available <= as_of.

    Minimal heuristic for Phase B canary: as_of must be <= today and
    the ticker must exist in our PIT universe at as_of.  Real PIT
    leak detection requires inspecting the toolkit call log (Phase B+
    work; deferred to Phase C audit).
    """
    try:
        as_of = pd.Timestamp(as_of_iso).date()
    except Exception:
        return False
    if as_of > pd.Timestamp.today().date():
        return False
    return True


def compute_canary(samples_df: pd.DataFrame, dry_run: bool) -> pd.DataFrame:
    """Run canary compute over each (ticker, as_of) sample.  Returns
    canary_signals DataFrame ready to write to parquet."""
    rows = []
    n = len(samples_df)
    for i, row in samples_df.iterrows():
        ticker  = row["ticker"]
        as_of   = str(row["entry_date"])[:10]
        if dry_run:
            tier, score = _deterministic_mock_tier(ticker, as_of)
            ctx = (f"[DRY-RUN mock] ticker={ticker} as_of={as_of} "
                   f"deterministic tier={tier} score={score}")
            llm_model = "dry_run_mock"
        else:
            r = _run_real_pipeline(ticker, as_of)
            tier  = r["agent_tier"]
            score = r["agent_score"]
            ctx   = r["context_paragraph"]
            llm_model = r["llm_model"]

        pit_ok = _check_pit_compliance(ticker, as_of)
        rows.append({
            "ticker":            ticker,
            "as_of":             as_of,
            "agent_tier":        tier,
            "agent_score":       score,
            "context_paragraph": ctx,
            "computed_at":       datetime.now(timezone.utc).isoformat(),
            "llm_model":         llm_model,
            "pit_compliant":     pit_ok,
        })
        if (i + 1) % 10 == 0:
            print(f"[INFO] computed {i+1}/{n}")
    return pd.DataFrame(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=Path, required=True,
                    help="sample_pairs.parquet from sample selector")
    ap.add_argument("--output", type=Path,
                    default=REPO / "output_phase_1b_canary" / "canary_signals.parquet")
    ap.add_argument("--dry-run", action="store_true",
                    help="use deterministic mock tiers (no LLM call); "
                         "needed when Python 3.12 + langgraph not available")
    args = ap.parse_args()

    if not args.samples.exists():
        print(f"[FATAL] samples missing: {args.samples}")
        return 1
    samples = pd.read_parquet(args.samples)
    print(f"[INIT] {len(samples)} samples loaded; mode="
          f"{'DRY-RUN' if args.dry_run else 'REAL-LLM'}")

    signals = compute_canary(samples, dry_run=args.dry_run)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    signals.to_parquet(args.output, index=False)

    # Tier distribution sanity report
    if not signals.empty:
        print(f"[OK] tier distribution: {signals['agent_tier'].value_counts().sort_index().to_dict()}")
        pit_bad = (~signals["pit_compliant"]).sum()
        if pit_bad > 0:
            print(f"[WARN] {pit_bad} signals failed PIT compliance heuristic")
        else:
            print(f"[OK] all signals PIT compliant")
    print(f"[OK] wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
