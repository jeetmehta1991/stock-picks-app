"""scripts/pattern_t_family_grep_audit.py

# Source: B755-COUNCIL TIER 3 ticket #14
#   S4-B755-COUNCIL-PATTERN-T-FAMILY-GREP-ALL-221-STRATEGIES
# per CHECKLIST #77 + feedback_family_bug_grep_before_one_liners.md

PURPOSE.
Per council Advisor E (Executor): grep for the MA-cross + trend-gate
collinearity pattern across all 221 strategies. The chairman + multiple
reviewers flagged Pattern T as a likely cluster-wide issue: when a strategy
fires on golden_cross_X_Y AND requires price_above_ema_Y, the two gates are
collinear (golden cross implies fast MA > slow MA, which implies price tends
to be above slow MA at the cross event).

Minimum 8-12 hits expected outside Cluster A. Per feedback_family_bug_grep_
before_one_liners.md: BUNDLED audit before any one-liner fixes; surface ALL
affected strategies in single batch.

METHODOLOGY.
For each strategy in ALL_STRATEGIES:
1. Inspect the source code of the strategy's predicate function via inspect
2. Check for presence of MA-cross signals (golden_cross / death_cross / cross_up / cross_dn / cross_above / cross_below)
3. Check for presence of trend-state gates (price_above_ema / price_below_ema / above_sma / below_sma / above_ema / below_ema)
4. If BOTH present AND on related MA windows, flag as Pattern T candidate

The "related MA windows" check (heuristic): if the cross signal is
ema_X_Y_golden_cross AND a trend gate uses ema_X or ema_Y or sma_X or sma_Y,
classify HIGH-collinearity. If unrelated windows (e.g., ema_9_21_cross + price_above_ema_200),
classify MEDIUM-collinearity (trend gate is at a different timescale).

OUTPUT.
JSON report at output_audit/pattern_t_family_grep_audit.json:
{
  "meta": {
    "n_strategies_audited": int,
    "n_pattern_t_candidates": int,
    "n_high_collinearity": int,
    "n_medium_collinearity": int
  },
  "candidates": [
    {
      "strategy": "golden_cross_50_200",
      "ma_cross_signals": ["ema_50_200_golden_cross", "ema_50_200_death_cross"],
      "trend_gate_signals": [],  // single-gate -- not Pattern T
      "verdict": "CLEAN" / "PATTERN_T_HIGH" / "PATTERN_T_MEDIUM"
    },
    ...
  ]
}

USAGE.
  python scripts/pattern_t_family_grep_audit.py
"""
from __future__ import annotations

import argparse
import inspect
import json
import logging
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

logger = logging.getLogger("pattern_t_family_grep_audit")

REPO_ROOT = Path(_REPO)
OUTPUT_DIR = REPO_ROOT / "output_audit"

# Patterns to detect in strategy source code.
# MA-cross EVENT signal patterns
MA_CROSS_PATTERNS = [
    r'\b(\w+_golden_cross)\b',
    r'\b(\w+_death_cross)\b',
    r'\b(\w+_cross_up)\b',
    r'\b(\w+_cross_dn)\b',
    r'\b(\w+_cross_down)\b',
    r'\b(macd_\w*crossover\w*)\b',
    r'\b(stoch_bullish_cross)\b',
    r'\b(stoch_bearish_cross)\b',
    r'\b(stochrsi_cross_up)\b',
    r'\b(stochrsi_cross_dn)\b',
    r'\b(ppo_crossover_\w+)\b',
    r'\b(ema_\d+_\d+_(?:golden|death)_cross)\b',
    r'\b(tema_cross_\w+)\b',
    r'\b(psar_flip_\w+)\b',
]

# Trend-state STATE signal patterns
TREND_STATE_PATTERNS = [
    r'\b(price_above_ema_\d+)\b',
    r'\b(price_below_ema_\d+)\b',
    r'\b(below_ema_\d+)\b',
    r'\b(above_ema_\d+)\b',
    r'\b(price_above_sma_\d+)\b',
    r'\b(price_below_sma_\d+)\b',
    r'\b(below_sma_\d+)\b',
    r'\b(above_sma_\d+)\b',
]

# Window-extraction regex for collinearity classification
WINDOW_REGEX = re.compile(r'(\d+)')


def _extract_signals(source: str) -> tuple[list[str], list[str]]:
    """Return (ma_cross_signals, trend_state_signals) found in strategy source."""
    ma_cross = []
    for pat in MA_CROSS_PATTERNS:
        ma_cross.extend(re.findall(pat, source))
    trend = []
    for pat in TREND_STATE_PATTERNS:
        trend.extend(re.findall(pat, source))
    return sorted(set(ma_cross)), sorted(set(trend))


def _classify_collinearity(
    ma_cross: list[str], trend: list[str],
) -> str:
    """Return verdict per chairman heuristic."""
    if not ma_cross:
        return "CLEAN_NO_MA_CROSS"
    if not trend:
        return "CLEAN_NO_TREND_GATE"

    # Extract numeric windows from MA-cross signals
    cross_windows: set[int] = set()
    for sig in ma_cross:
        cross_windows.update(int(m) for m in WINDOW_REGEX.findall(sig))

    # Extract numeric windows from trend gates
    trend_windows: set[int] = set()
    for sig in trend:
        trend_windows.update(int(m) for m in WINDOW_REGEX.findall(sig))

    # HIGH collinearity: cross windows and trend windows overlap
    if cross_windows & trend_windows:
        return "PATTERN_T_HIGH"

    # MEDIUM collinearity: both present but at unrelated timescales
    return "PATTERN_T_MEDIUM"


def audit_all_strategies() -> dict:
    """Iterate every entry in ALL_STRATEGIES, extract source, classify."""
    from backtest.signals.screener import ALL_STRATEGIES

    candidates: list[dict] = []
    n_high = n_medium = n_clean = 0
    n_no_source = 0

    for strat_name in sorted(ALL_STRATEGIES.keys()):
        strat_fn = ALL_STRATEGIES[strat_name]
        try:
            source = inspect.getsource(strat_fn)
        except (OSError, TypeError):
            n_no_source += 1
            continue

        ma_cross, trend = _extract_signals(source)
        verdict = _classify_collinearity(ma_cross, trend)

        if verdict.startswith("CLEAN"):
            n_clean += 1
            continue

        if verdict == "PATTERN_T_HIGH":
            n_high += 1
        elif verdict == "PATTERN_T_MEDIUM":
            n_medium += 1

        candidates.append({
            "strategy": strat_name,
            "verdict": verdict,
            "ma_cross_signals": ma_cross,
            "trend_gate_signals": trend,
            "n_ma_cross_signals": len(ma_cross),
            "n_trend_gate_signals": len(trend),
        })

    return {
        "meta": {
            "as_of_run": datetime.now().isoformat(),
            "n_strategies_audited": len(ALL_STRATEGIES),
            "n_no_source": n_no_source,
            "n_clean": n_clean,
            "n_pattern_t_candidates": len(candidates),
            "n_high_collinearity": n_high,
            "n_medium_collinearity": n_medium,
            "thresholds": {
                "HIGH": "MA-cross + trend-gate share at least one numeric window",
                "MEDIUM": "MA-cross + trend-gate present but at unrelated timescales",
            },
        },
        "candidates": sorted(candidates, key=lambda c: (c["verdict"], c["strategy"])),
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Pattern T family-grep audit per "
                    "S4-B755-COUNCIL-PATTERN-T-FAMILY-GREP-ALL-221-STRATEGIES.",
    )
    p.add_argument("--output", default=None)
    return p


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    args = _build_arg_parser().parse_args(argv)

    report = audit_all_strategies()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.output) if args.output else (
        OUTPUT_DIR / "pattern_t_family_grep_audit.json"
    )
    out_path.write_text(json.dumps(report, indent=2, default=str))

    meta = report["meta"]
    print(f"\n=== pattern_t_family_grep_audit complete ===")
    print(f"Strategies audited     : {meta['n_strategies_audited']}")
    print(f"No source available    : {meta['n_no_source']}")
    print(f"CLEAN                  : {meta['n_clean']}")
    print(f"Pattern T HIGH         : {meta['n_high_collinearity']}")
    print(f"Pattern T MEDIUM       : {meta['n_medium_collinearity']}")
    print(f"Total Pattern T cands  : {meta['n_pattern_t_candidates']}")
    print(f"\nFirst 15 HIGH-collinearity candidates:")
    high_cands = [c for c in report['candidates'] if c['verdict'] == 'PATTERN_T_HIGH'][:15]
    for c in high_cands:
        print(f"  {c['strategy']:40s} | cross: {','.join(c['ma_cross_signals'])[:60]}")
    print(f"\nOutput                 : {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
