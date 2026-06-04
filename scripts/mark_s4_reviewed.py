"""Batch 583 (2026-06-04) -- track which strategies have completed
the per-strategy Stage 4 deep-dive walk per
feedback_per_strategy_deep_dive_stage4.

Adds an `s4_reviewed_strategies` top-level dict to approvals.json:
  {
    "<strategy_name>": {
      "reviewed_at": ISO timestamp,
      "reviewed_in_batch": <batch number>,
      "review_outcome": str (free-text - e.g., "wired", "deferred",
                             "rejected sizing", "bug fixed", etc.)
    }
  }

Owner directive 2026-06-04: "add another column in strategy table
which says s4 review completed y/n"

Population strategy:
  - Backfill from prior batches (B570 Class-6 Defer; B571/572/574
    doji walk; B580 turtle_soup; B581 Judas/MMBM/Week Gap; B582
    52w_high bug fix; B571 news_sentiment_shift_long Class 2/7).
  - Going forward: mark each strategy at end of its walk turn.

Usage:
  # backfill from prior batches (one-time):
  python scripts/mark_s4_reviewed.py --backfill

  # mark a new walk completed:
  python scripts/mark_s4_reviewed.py --strategy <name> \
    --batch 583 --outcome "bug fixed; year_high producer corrected"
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


APPROVALS = Path("C:/tmp/r4_optimization_candidates/approvals.json")


# Backfill set: every strategy that has had a B570+ Stage 4 walk
BACKFILL = {
    # B570 Class-6 Defer (7 PLZL strategies)
    "activist_13d_long":               ("B570", "Class-6 Deferred pending producer audit"),
    "smc_choch_reversal":              ("B570", "Class-6 Deferred"),
    "smc_equal_highs_sweep_short":     ("B570", "Class-6 Deferred"),
    "smc_equal_lows_sweep_long":       ("B570", "Class-6 Deferred"),
    "smc_liquidity_sweep_reversal":    ("B570", "Class-6 Deferred"),
    "smc_ote_long":                    ("B570", "Class-6 Deferred"),
    "smc_ote_short":                   ("B570", "Class-6 Deferred"),
    # B571 news_sentiment_shift walk
    "news_sentiment_shift_long":       ("B571", "Class 4 rejected; Class 2 loosen approved; Class 7 short pair surfaced"),
    "news_sentiment_shift_short":      ("B571", "Class 7 NEW_STRATEGY surfaced/approved; awaits wire"),
    # B572 doji_at_resistance_short wired
    "doji_at_resistance_short":        ("B572", "wired Class 7 NEW_STRATEGY; mirror of doji_at_support"),
    # B574 doji_at_support tolerance loosen (resolved via _wide flags)
    "doji_at_support":                 ("B574", "Class 2 ENTRY_GATE_LOOSEN Implemented via _wide flag variants"),
    # B580 turtle_soup pair wired
    "turtle_soup_long":                ("B580", "wired Class 7; Raschke Street Smarts 1996"),
    "turtle_soup_short":               ("B580", "wired Class 7; mirror"),
    # B581 6-strategy ICT batch wired
    "judas_swing_long":                ("B581", "wired Class 7; ICT manipulation reversal"),
    "judas_swing_short":               ("B581", "wired Class 7; mirror"),
    "mmbm_long":                       ("B581", "wired Class 7; PO3 bullish cycle setup; new producer compute_po3_signals"),
    "mmsm_short":                      ("B581", "wired Class 7; mirror"),
    "week_opening_gap_fill_down":      ("B581", "wired Class 7; new producer compute_week_opening_gap_signals"),
    "week_opening_gap_fill_up":        ("B581", "wired Class 7; mirror"),
    # B582 52w_high_breakout bug fix
    "52w_high_breakout":               ("B582", "year_high producer bug fixed (excluded today + strict >); QUIET root-cause resolved"),
    "52w_low_breakdown":               ("B582", "mirror; same producer fix applied"),
    "52w_high_breakout_with_smart_money_long": ("B582", "consumer of near_52w_high; downstream fix from B582"),
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def backfill(data: dict) -> int:
    """Apply the BACKFILL mapping to approvals.json."""
    reviewed = data.setdefault("s4_reviewed_strategies", {})
    n = 0
    for name, (batch, outcome) in BACKFILL.items():
        if name in reviewed:
            continue
        reviewed[name] = {
            "reviewed_at":       _now(),
            "reviewed_in_batch": batch,
            "review_outcome":    outcome,
        }
        n += 1
    return n


def mark(data: dict, strategy: str, batch: str, outcome: str) -> bool:
    reviewed = data.setdefault("s4_reviewed_strategies", {})
    if strategy in reviewed:
        return False
    reviewed[strategy] = {
        "reviewed_at":       _now(),
        "reviewed_in_batch": batch,
        "review_outcome":    outcome,
    }
    return True


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--approvals", default=str(APPROVALS))
    p.add_argument("--backfill", action="store_true")
    p.add_argument("--strategy", default="")
    p.add_argument("--batch", default="")
    p.add_argument("--outcome", default="")
    args = p.parse_args()

    apath = Path(args.approvals)
    if not apath.exists():
        print(f"ERROR: approvals.json not found: {apath}", file=sys.stderr)
        return 1
    data = json.loads(apath.read_text(encoding="utf-8"))

    if args.backfill:
        n = backfill(data)
        print(f"Backfilled {n} strategies into s4_reviewed_strategies.")
    elif args.strategy:
        if not (args.batch and args.outcome):
            print("ERROR: --strategy requires --batch + --outcome",
                  file=sys.stderr)
            return 1
        ok = mark(data, args.strategy, args.batch, args.outcome)
        if ok:
            print(f"Marked {args.strategy} as S4-reviewed (batch={args.batch}).")
        else:
            print(f"{args.strategy} already marked as reviewed (no-op).")
    else:
        print("ERROR: provide --backfill OR --strategy",
              file=sys.stderr)
        return 1

    apath.write_text(json.dumps(data, indent=2), encoding="utf-8")
    total = len(data.get("s4_reviewed_strategies", {}))
    print(f"Total s4_reviewed_strategies: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
