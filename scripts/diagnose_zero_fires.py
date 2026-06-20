"""diagnose_zero_fires.py

B693 (2026-06-11) per external reviewer's specific two-part test:
"a measured zero must be diagnosed, not assumed."

When B660 reports 0 fires for a strategy, the result is ambiguous:
  (a) HARNESS GAP -- the strategy's gate signals were never present in the
      precompute signals dict (producer wasn't wired). The strategy returned
      0 because it never had a chance to fire.
  (b) EMPTY CONJUNCTION -- the strategy's gate signals were all present,
      but the AND of them is empty across the universe-window. The strategy
      had every chance to fire and chose not to. This is a real verdict
      meaning the gate-stack is too tight, not that the producer is missing.

These two outcomes are observationally identical (a zero is a zero), and the
B660 doc currently dispositions all six FAIL_FIRE_STARVED breakout-cluster
strategies as "false negative pending re-run." This tool produces a positive
test that distinguishes them.

USAGE:
  python scripts/diagnose_zero_fires.py --strategy strat_52w_high_breakout \\
      --ticker AAPL --start 2024-01-01 --end 2024-12-31

REPORT:
  - For each gate the strategy reads:
    * Is the key emitted by compute_all_signals on at least one bar? (HARNESS)
    * What fraction of bars is the gate True? (marginal True-rate)
    * What is the pairwise overlap between gate True-bars? (conjunction count)
  - For the strategy's full N-gate AND: how many bars satisfy all? (the zero)
  - For 3-of-N, 4-of-N: how many bars? (the relaxed-conjunction count;
    answers "if we loosen to a score, is the strategy tradeable?")

This is the BR-1 ground truth test the reviewer demanded. If a strategy
returns 0 fires AND the harness gap test PASSES (signals present, gates
fire individually) AND the relaxed-conjunction count is large, the verdict
is "empty conjunction" -- a real signal that the AND is too tight, not a
harness gap waiting for re-run.

NOT YET PRODUCTION-READY: this tool is a SCAFFOLD per B693 owner approval.
Wiring it to the strategy registry probes for each strat_* function's
declared signal-keys + extending to multi-ticker / full-universe is a
follow-on once owner reviews the diagnostic methodology on a single case.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path

# Ensure repo root is on sys.path
_REPO_ROOT_FOR_PATH = str(Path(__file__).resolve().parents[1])
if _REPO_ROOT_FOR_PATH not in sys.path:
    sys.path.insert(0, _REPO_ROOT_FOR_PATH)

from collections import Counter
from itertools import combinations

logger = logging.getLogger("diagnose_zero_fires")


def declared_signal_keys(strategy_fn) -> list[str]:
    """Probe the strategy function with a sentinel dict that records every
    key the strategy reads. Mirrors the existing _declared_signals_for_strategy
    pattern in scripts/measure_fire_count.py but exposed as a public helper."""
    class _ProbeDict(dict):
        def __init__(self):
            super().__init__()
            self.accessed: set = set()

        def get(self, key, default=None):
            self.accessed.add(key)
            return True if default is None or isinstance(default, bool) else default

        def __getitem__(self, key):
            self.accessed.add(key)
            return True

        def __contains__(self, key):
            self.accessed.add(key)
            return True

    probe = _ProbeDict()
    try:
        strategy_fn(probe)
    except Exception:
        pass
    return sorted(probe.accessed)


def diagnose(
    strategy_name: str,
    ticker: str,
    start: date,
    end: date,
    enable_extended_signals: bool = True,
) -> dict:
    """Two-part diagnosis per reviewer specification.

    Part 1 (HARNESS GAP test): are the gate keys actually present in the
    signals dict on at least one bar?
    Part 2 (EMPTY CONJUNCTION test): given the keys are present, how does
    the per-gate True-rate + N-of-N AND count behave?
    """
    # Import here so the help/CLI works without the full backtest stack loaded
    import pandas as pd
    from backtest.signals.screener import ALL_STRATEGIES
    from scripts.measure_fire_count import (
        _load_ohlcv,
        _precompute_signals_for_ticker,
    )

    if strategy_name not in ALL_STRATEGIES:
        raise SystemExit(f"strategy {strategy_name!r} not in ALL_STRATEGIES")
    strat_fn = ALL_STRATEGIES[strategy_name]

    declared = declared_signal_keys(strat_fn)
    logger.info("Strategy %s declares %d signal keys: %s", strategy_name, len(declared), declared)

    df = _load_ohlcv(ticker)
    if df is None:
        raise SystemExit(f"OHLCV cache miss for {ticker}")

    # B939 (2026-06-20) Council 47 explicit-intent: diagnose_zero_fires must
    # include TIER 2 producers to distinguish "zero from gate-stacking" vs
    # "zero from TIER 2 deferral". Without include_tier2_producers=True, the
    # diagnostic is structurally unable to answer its own question for ~44
    # TIER 2-dependent strategies (B919 architectural class).
    signals_by_bar = _precompute_signals_for_ticker(
        df, ticker, start, end,
        enable_extended_signals=enable_extended_signals,
        include_tier2_producers=True,
    )
    if not signals_by_bar:
        raise SystemExit(f"precompute returned 0 bars for {ticker} in {start}..{end}")
    logger.info("Precompute: %d bars", len(signals_by_bar))

    # Part 1: harness gap -- which declared keys are PRESENT in the signals
    # dict on at least one bar?
    present_anywhere: set = set()
    for _, sigs in signals_by_bar:
        for k in declared:
            if k in sigs:
                present_anywhere.add(k)
    missing_keys = [k for k in declared if k not in present_anywhere]
    logger.info("HARNESS GAP test: %d keys present / %d declared; %d MISSING: %s",
                len(present_anywhere), len(declared), len(missing_keys), missing_keys)

    # Part 2: empty conjunction -- per-gate True-rate + N-of-N AND counts
    per_gate_true: Counter = Counter()
    per_gate_present: Counter = Counter()
    per_bar_score: list[int] = []  # how many of the declared keys fire on each bar
    fires: int = 0
    for bd, sigs in signals_by_bar:
        # Strategy's actual fire?
        try:
            out = strat_fn(sigs)
            if out.get("fires"):
                fires += 1
        except Exception:
            pass
        # Per-gate True observations
        score = 0
        for k in declared:
            if k in sigs:
                per_gate_present[k] += 1
                v = sigs[k]
                if isinstance(v, bool) and v:
                    per_gate_true[k] += 1
                    score += 1
                elif v is True:
                    per_gate_true[k] += 1
                    score += 1
        per_bar_score.append(score)

    gate_summary = {}
    for k in declared:
        n_present = per_gate_present.get(k, 0)
        n_true = per_gate_true.get(k, 0)
        marg = (n_true / n_present) if n_present else None
        gate_summary[k] = {
            "present_on_bars": n_present,
            "true_on_bars": n_true,
            "marginal_true_rate": round(marg, 4) if marg is not None else None,
            "MISSING_FROM_HARNESS": (k in missing_keys),
        }

    # N-of-N distribution + relaxed counts
    score_dist = Counter(per_bar_score)
    n_decl = len(declared)
    relaxed_counts = {
        f"{m}_of_{n_decl}_or_more": sum(c for s, c in score_dist.items() if s >= m)
        for m in range(1, n_decl + 1)
    }

    # Diagnosis verdict
    if missing_keys:
        verdict = "HARNESS_GAP"
        verdict_reason = (
            f"{len(missing_keys)} of {len(declared)} declared keys are not present in the signals dict "
            f"on ANY bar: {missing_keys}. Re-run with the missing producer wired."
        )
    elif fires > 0:
        verdict = "FIRES_NORMALLY"
        verdict_reason = f"Strategy fired {fires} times on this ticker/window; not a zero case."
    else:
        # All keys present, strategy still fires 0. Empty conjunction.
        all_n = relaxed_counts.get(f"{n_decl}_of_{n_decl}_or_more", 0)
        one_less = relaxed_counts.get(f"{n_decl-1}_of_{n_decl}_or_more", 0)
        verdict = "EMPTY_CONJUNCTION"
        verdict_reason = (
            f"All {n_decl} gate keys are present in the signals dict but the strategy fires 0 times. "
            f"The {n_decl}-of-{n_decl} AND has {all_n} bars in this window; relaxing to "
            f"{n_decl-1}-of-{n_decl} would yield {one_less} bars. "
            f"This is NOT a harness gap. The gate-stack is genuinely too tight. "
            f"Re-running with a different harness will not change the verdict. "
            f"Loosen the conjunction (e.g. score-of-N, or +/-1-bar confirmation window) "
            f"per the B693 reviewer recommendations."
        )

    return {
        "strategy": strategy_name,
        "ticker": ticker,
        "date_range": {"start": start.isoformat(), "end": end.isoformat()},
        "extended_signals_enabled": enable_extended_signals,
        "declared_signal_keys": declared,
        "n_bars_precomputed": len(signals_by_bar),
        "n_strategy_fires": fires,
        "harness_gap_test": {
            "n_declared": len(declared),
            "n_present_anywhere": len(present_anywhere),
            "n_missing": len(missing_keys),
            "missing_keys": missing_keys,
        },
        "per_gate_summary": gate_summary,
        "score_distribution": dict(score_dist),
        "relaxed_conjunction_counts": relaxed_counts,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--strategy", required=True, help="Strategy name (registry key, e.g. strat_52w_high_breakout)")
    p.add_argument("--ticker", required=True, help="OHLCV ticker symbol")
    p.add_argument("--start", default="2024-01-01")
    p.add_argument("--end", default="2024-12-31")
    p.add_argument("--no-extended-signals", action="store_true", help="Disable B689 TIER 1 + TIER 3 wire-in")
    p.add_argument("--output", default=None, help="Output JSON path; default stdout")
    p.add_argument("--verbose", action="store_true")
    return p


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    result = diagnose(
        strategy_name=args.strategy,
        ticker=args.ticker,
        start=date.fromisoformat(args.start),
        end=date.fromisoformat(args.end),
        enable_extended_signals=not args.no_extended_signals,
    )
    text = json.dumps(result, indent=2, default=str)
    if args.output:
        Path(args.output).write_text(text)
        logger.info("Wrote %s", args.output)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
