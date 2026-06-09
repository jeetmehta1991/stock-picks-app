"""scripts/measure_fire_count.py

Fire-count MEASUREMENT pass.

Built Batch 641 (2026-06-09) per B640 external-AI audit findings #1+#2 +
owner directive 2026-06-09 #1. Replaces the independent-product
projection in `scripts/estimate_fire_count.py` (whose upper-bound is
biased in BOTH directions depending on gate-correlation sign) with
ACTUAL firing rates measured against the 220-ticker history.

Usage (CLI):
  python scripts/measure_fire_count.py --strategies pivot_s1_bounce
      pivot_s2_bounce camarilla_r4_breakout
  python scripts/measure_fire_count.py --all       # all 221 strategies
  python scripts/measure_fire_count.py --b640      # the 10 B640 walk strategies
  python scripts/measure_fire_count.py --strategies cpr_narrow_bullish
      --start 2020-01-01 --end 2026-05-31 --output out.json

Output JSON schema:
  {
    "as_of": "2026-06-09",
    "universe": "T1a_PIT_canonical_614",
    "n_tickers": <int>,
    "date_range": {"start": "...", "end": "..."},
    "n_bars_total": <int>,
    "results": [
      {
        "strategy": "pivot_s1_bounce",
        "n_fires_long": <int>,
        "n_fires_short": <int>,
        "n_fires_avoid": <int>,
        "fires_per_year_long": <float>,
        "fires_per_year_short": <float>,
        "first_fire_date": "YYYY-MM-DD",
        "last_fire_date": "YYYY-MM-DD",
        "verdict": "PASS_CUBE" | "BORDERLINE" | "FAIL_FIRE_STARVED",
        "gate_marginals": {gate_signal_name: marginal_rate_observed},
        "gate_pairwise_correlation": {(gate_a, gate_b): pearson_r},
        "independence_predicted_vs_measured_ratio": <float>,
        "notes": "..."
      },
      ...
    ]
  }

The `independence_predicted_vs_measured_ratio` is the diagnostic that
adjudicates the B640 external-AI audit finding: ratio = 1.0 means
the independence assumption was correct; >1.0 means independent product
OVER-estimates (gates negatively correlated/exclusive); <1.0 means
independent product UNDER-estimates (gates positively correlated, the
W5 capitulation pattern).

Gate-marginals + pairwise-correlation surface WHICH gate pairs are
driving the bias direction so we can read it strategy-by-strategy.

Pre-requisite: full Polygon OHLCV cache + tier universe CSVs (Sprint 0A
state). On a machine without the cache, the script reports the cache-
miss count and skips affected tickers gracefully.

Per CHECKLIST (k) + S5-FIRE-COUNT-MEASURED-RUN ticket; primary
artifact for B640 walk bundle revalidation.
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import os
import sys
import time

# Ensure repo root is on sys.path when run as a script
_REPO_ROOT_FOR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT_FOR_PATH not in sys.path:
    sys.path.insert(0, _REPO_ROOT_FOR_PATH)
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger("measure_fire_count")

REPO_ROOT = Path(__file__).resolve().parents[1]
OHLCV_DIR = REPO_ROOT / "data_prefetch" / "polygon" / "ohlcv_daily"
T1A_PATH = REPO_ROOT / "Backtesting universe" / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"


# The 10 strategies covered by B640 walk bundle, post-B641 W10 rename.
B640_STRATEGIES = [
    "bullish_engulfing_support",   # W1
    "shooting_star_short",         # W2
    "pivot_s1_bounce",             # W3 (post-B641 pin_bar fix)
    "pivot_s2_bounce",             # W4
    "pivot_s3_capitulation",       # W5
    "pivot_r1_breakout",           # W6
    "pivot_r2_continuation",       # W7
    "cpr_narrow_bullish",          # W8 (post-B641 F1+F1b)
    "camarilla_s3_bounce",         # W9
    "camarilla_r4_breakout",       # W10 (post-B641 R3->R4 rename)
]


@dataclass
class StrategyResult:
    """Per-strategy measurement output."""

    strategy: str
    n_fires_long: int = 0
    n_fires_short: int = 0
    n_fires_avoid: int = 0
    n_bars_evaluated: int = 0
    first_fire_date: Optional[str] = None
    last_fire_date: Optional[str] = None
    gate_marginals: dict[str, float] = field(default_factory=dict)
    gate_pairwise_correlation: dict[str, float] = field(default_factory=dict)
    independence_predicted: float = 0.0
    notes: str = ""

    def to_dict(self) -> dict:
        # Universe-wide fires per CALENDAR year (matches cube min_trades=30
        # threshold which is universe-wide, not per-ticker). Computed as
        # total_fires / calendar_year_span (set by the run's date range
        # via cli, surfaced by the caller post-hoc into `calendar_year_span`
        # below).
        ticker_year_span = max(self.n_bars_evaluated / 252.0, 1e-9)
        calendar_year_span = max(getattr(self, "calendar_year_span", 1.0), 1e-9)
        fires_long_per_year_universe = self.n_fires_long / calendar_year_span
        fires_short_per_year_universe = self.n_fires_short / calendar_year_span
        total_fires_per_yr_universe = (
            fires_long_per_year_universe + fires_short_per_year_universe
        )
        # Per-ticker-year rate (rare-event diagnostic, NOT the cube gate)
        fires_long_per_ticker_year = self.n_fires_long / ticker_year_span
        fires_short_per_ticker_year = self.n_fires_short / ticker_year_span
        measured_joint = (self.n_fires_long + self.n_fires_short) / max(self.n_bars_evaluated, 1)
        independence_ratio = (
            self.independence_predicted / measured_joint
            if measured_joint > 0 and self.independence_predicted > 0
            else None
        )
        # Verdict on universe-wide total fires per calendar year vs
        # min_trades=30 from PASSING_CRITERIA per CHECKLIST (k).
        if total_fires_per_yr_universe < 30:
            verdict = "FAIL_FIRE_STARVED"
        elif total_fires_per_yr_universe < 60:
            verdict = "BORDERLINE"
        else:
            verdict = "PASS_CUBE"
        # Universe projection: if the smoke used N tickers and the full
        # T1a universe is ~220, project linearly. Caveat: smoke ticker
        # sample may not be representative of full T1a.
        n_tickers_sampled = max(getattr(self, "n_tickers_sampled", 1), 1)
        n_tickers_full_t1a = 220
        projection_scale = n_tickers_full_t1a / n_tickers_sampled
        projected_long_per_year = fires_long_per_year_universe * projection_scale
        projected_short_per_year = fires_short_per_year_universe * projection_scale
        projected_total_per_year = projected_long_per_year + projected_short_per_year
        # Verdict on projected universe-wide total
        if projected_total_per_year < 30:
            projected_verdict = "FAIL_FIRE_STARVED"
        elif projected_total_per_year < 60:
            projected_verdict = "BORDERLINE"
        else:
            projected_verdict = "PASS_CUBE"
        return {
            "strategy": self.strategy,
            "n_fires_long": self.n_fires_long,
            "n_fires_short": self.n_fires_short,
            "n_fires_avoid": self.n_fires_avoid,
            "n_bars_evaluated": self.n_bars_evaluated,
            "n_tickers_sampled": n_tickers_sampled,
            "ticker_year_span": round(ticker_year_span, 2),
            "calendar_year_span": round(calendar_year_span, 2),
            "measured_fires_per_calendar_year_long_sampled": round(fires_long_per_year_universe, 2),
            "measured_fires_per_calendar_year_short_sampled": round(fires_short_per_year_universe, 2),
            "measured_fires_per_calendar_year_total_sampled": round(total_fires_per_yr_universe, 2),
            "projected_fires_per_calendar_year_long_full_t1a": round(projected_long_per_year, 1),
            "projected_fires_per_calendar_year_short_full_t1a": round(projected_short_per_year, 1),
            "projected_fires_per_calendar_year_total_full_t1a": round(projected_total_per_year, 1),
            "projected_verdict_full_t1a": projected_verdict,
            "fires_per_ticker_year_long": round(fires_long_per_ticker_year, 4),
            "fires_per_ticker_year_short": round(fires_short_per_ticker_year, 4),
            "first_fire_date": self.first_fire_date,
            "last_fire_date": self.last_fire_date,
            "verdict": verdict,
            "gate_marginals": {k: round(v, 4) for k, v in self.gate_marginals.items()},
            "gate_pairwise_correlation": {
                k: round(v, 3) for k, v in self.gate_pairwise_correlation.items()
            },
            "independence_predicted_joint_prob": round(self.independence_predicted, 6),
            "independence_predicted_vs_measured_ratio": (
                round(independence_ratio, 3) if independence_ratio is not None else None
            ),
            "notes": self.notes,
        }


def _load_t1a_tickers(as_of: date | None = None) -> list[str]:
    """Load T1a universe; PIT-filter if as_of provided. Skips `#` header
    comment lines per T1a B++ CSV convention."""
    df = pd.read_csv(T1A_PATH, comment="#")
    if as_of is not None:
        added = pd.to_datetime(df["added_date"], errors="coerce").dt.date
        removed = pd.to_datetime(df["removed_date"], errors="coerce").dt.date
        mask = ((added.isna()) | (added <= as_of)) & ((removed.isna()) | (removed > as_of))
        df = df[mask]
    return df["Symbol"].astype(str).str.upper().unique().tolist()


def _load_ohlcv(ticker: str) -> Optional[pd.DataFrame]:
    """Load Polygon OHLCV parquet for a ticker. Returns None on missing."""
    fpath = OHLCV_DIR / f"{ticker}.parquet"
    if not fpath.exists():
        return None
    try:
        df = pd.read_parquet(fpath)
    except Exception as exc:
        logger.warning("OHLCV load failed for %s: %s", ticker, exc)
        return None
    # Normalize: index by date, lowercase columns
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).set_index("date").sort_index()
    df.columns = [c.lower() for c in df.columns]
    needed = {"open", "high", "low", "close", "volume"}
    if not needed.issubset(set(df.columns)):
        return None
    return df


def _precompute_signals_for_ticker(
    df: pd.DataFrame, ticker: str, start: date, end: date,
) -> list[tuple[date, dict]]:
    """Compute signals for every bar in [start, end] for one ticker.

    Returned once; reused across all strategies that evaluate this
    ticker. Single biggest speedup vs the naive per-strategy loop.
    """
    from backtest.signals.technical import compute_all_signals
    out: list[tuple[date, dict]] = []
    if len(df) < 250:
        return out
    for i in range(250, len(df)):
        bar_date = df.index[i].date()
        if bar_date < start or bar_date > end:
            continue
        sub_df = df.iloc[: i + 1]
        try:
            signals = compute_all_signals(sub_df)
        except Exception as exc:
            logger.debug("compute_all_signals failed for %s bar %s: %s", ticker, bar_date, exc)
            continue
        if not signals:
            continue
        out.append((bar_date, signals))
    return out


def _eval_strategy_on_precomputed(
    strategy_fn, signals_by_bar: list[tuple[date, dict]],
) -> tuple[list[tuple], dict[str, list[bool]]]:
    """Run one strategy across precomputed signals."""
    fires: list[tuple] = []
    gate_obs: dict[str, list[bool]] = defaultdict(list)
    for bar_date, signals in signals_by_bar:
        try:
            out = strategy_fn(signals)
        except Exception as exc:
            logger.debug("Strategy eval failed for bar %s: %s", bar_date, exc)
            continue
        if out.get("fires"):
            fires.append((bar_date, out.get("direction")))
        for sig_name, sig_val in signals.items():
            if isinstance(sig_val, bool) or sig_val in (True, False):
                gate_obs[sig_name].append(bool(sig_val))
    return fires, gate_obs


def measure_strategies(
    strategy_names: list[str],
    start: date = date(2020, 1, 1),
    end: date = date(2026, 5, 31),
    max_tickers: Optional[int] = None,
) -> dict:
    """Measure fires for each named strategy across the T1a universe."""
    from backtest.signals.screener import ALL_STRATEGIES

    tickers = _load_t1a_tickers(end)
    if max_tickers is not None:
        tickers = tickers[:max_tickers]
    logger.info("Universe: %d tickers from T1a (PIT as_of=%s)", len(tickers), end)

    results: list[StrategyResult] = []
    cache_misses = 0
    tickers_evaluated = 0
    total_bars = 0

    # Load all OHLCV once + reuse across strategies
    t0 = time.time()
    ohlcv_cache: dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        df = _load_ohlcv(ticker)
        if df is None:
            cache_misses += 1
            continue
        ohlcv_cache[ticker] = df
        tickers_evaluated += 1
        total_bars += len(df)
    logger.info(
        "OHLCV load: %d tickers loaded, %d cache misses, %d total bars (%.1fs)",
        tickers_evaluated, cache_misses, total_bars, time.time() - t0,
    )

    # PRECOMPUTE signals across all (ticker, bar) ONCE; reuse across all strategies.
    # This is the key speedup: compute_all_signals is expensive (~50ms/call) and
    # was previously called n_strategies times per (ticker, bar). Now called once.
    t_pre = time.time()
    signals_cache: dict[str, list[tuple[date, dict]]] = {}
    for ticker, df in ohlcv_cache.items():
        signals_cache[ticker] = _precompute_signals_for_ticker(df, ticker, start, end)
    n_signal_evals = sum(len(v) for v in signals_cache.values())
    logger.info(
        "Signal precompute: %d total (ticker, bar) signal-dicts cached (%.1fs)",
        n_signal_evals, time.time() - t_pre,
    )

    calendar_year_span = max(((end - start).days / 365.25), 1e-9)

    # Per-strategy evaluation against precomputed signals
    for strat_name in strategy_names:
        if strat_name not in ALL_STRATEGIES:
            logger.warning("Strategy %s not in ALL_STRATEGIES; skipping", strat_name)
            continue
        strat_fn = ALL_STRATEGIES[strat_name]
        t1 = time.time()
        result = StrategyResult(strategy=strat_name)
        result.calendar_year_span = calendar_year_span
        result.n_tickers_sampled = tickers_evaluated
        all_gate_obs: dict[str, list[bool]] = defaultdict(list)
        per_strategy_fires: list[tuple[str, date, str]] = []

        for ticker, signals_by_bar in signals_cache.items():
            fires, gate_obs = _eval_strategy_on_precomputed(strat_fn, signals_by_bar)
            for fdate, direction in fires:
                per_strategy_fires.append((ticker, fdate, direction))
                if direction == "long":
                    result.n_fires_long += 1
                elif direction == "short":
                    result.n_fires_short += 1
                elif direction == "avoid":
                    result.n_fires_avoid += 1
            for sig_name, obs_list in gate_obs.items():
                all_gate_obs[sig_name].extend(obs_list)
            # Use the bar count from signals_by_bar (always correct vs probe key)
            result.n_bars_evaluated += len(signals_by_bar)

        # Compute marginals + pairwise correlations for the gate signals
        # the strategy declares (via its bullet metadata)
        declared_signals = _declared_signals_for_strategy(strat_fn)
        for sig in declared_signals:
            obs = all_gate_obs.get(sig, [])
            if obs:
                result.gate_marginals[sig] = sum(obs) / len(obs)

        # Pairwise correlations (Pearson r on the boolean vectors)
        sigs_with_obs = [s for s in declared_signals if all_gate_obs.get(s)]
        for i, a in enumerate(sigs_with_obs):
            for b in sigs_with_obs[i + 1:]:
                obs_a = all_gate_obs[a]
                obs_b = all_gate_obs[b]
                n = min(len(obs_a), len(obs_b))
                if n < 100:
                    continue
                arr_a = np.array(obs_a[:n], dtype=float)
                arr_b = np.array(obs_b[:n], dtype=float)
                std_a = arr_a.std()
                std_b = arr_b.std()
                if std_a == 0 or std_b == 0:
                    continue
                r = float(np.corrcoef(arr_a, arr_b)[0, 1])
                result.gate_pairwise_correlation[f"{a} x {b}"] = r

        # Independence-predicted joint probability =
        # product of marginals (the assumption the estimator made)
        if result.gate_marginals:
            result.independence_predicted = 1.0
            for v in result.gate_marginals.values():
                result.independence_predicted *= v

        if per_strategy_fires:
            per_strategy_fires.sort(key=lambda x: x[1])
            result.first_fire_date = per_strategy_fires[0][1].isoformat()
            result.last_fire_date = per_strategy_fires[-1][1].isoformat()

        elapsed = time.time() - t1
        result.notes = f"Evaluated in {elapsed:.1f}s; {tickers_evaluated} tickers."
        results.append(result)
        logger.info(
            "  %s: long=%d short=%d avoid=%d in %.1fs",
            strat_name, result.n_fires_long, result.n_fires_short, result.n_fires_avoid, elapsed,
        )

    return {
        "as_of": end.isoformat(),
        "universe": "T1a_PIT_canonical",
        "n_tickers": tickers_evaluated,
        "n_cache_misses": cache_misses,
        "date_range": {"start": start.isoformat(), "end": end.isoformat()},
        "n_bars_total": total_bars,
        "results": [r.to_dict() for r in results],
    }


def _declared_signals_for_strategy(strategy_fn) -> list[str]:
    """Probe the strategy on a fully-truthy signals dict to discover which
    keys it reads. We use a sentinel dict that records every key accessed."""

    class _ProbeDict(dict):
        def __init__(self):
            super().__init__()
            self.accessed: set = set()

        def get(self, key, default=None):
            self.accessed.add(key)
            # Return a value that satisfies common gate constructs:
            # - True for boolean checks
            # - 50 for default-50 RSI-style checks
            # - For thresholds, we return both False (gate fails) and True
            #   (gate passes) variants -- here we return True so the
            #   strategy's gate-set is fully traversed.
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


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strategies", nargs="+",
        help="Explicit list of strategy names (registry keys, not function names)",
    )
    parser.add_argument(
        "--b640", action="store_true",
        help=f"Use the 10 B640 walk-bundle strategies: {B640_STRATEGIES}",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Measure ALL registered strategies (long-running; consider --max-tickers)",
    )
    parser.add_argument(
        "--start", default="2020-01-01",
        help="Start date YYYY-MM-DD (default 2020-01-01)",
    )
    parser.add_argument(
        "--end", default="2026-05-31",
        help="End date YYYY-MM-DD (default 2026-05-31)",
    )
    parser.add_argument(
        "--max-tickers", type=int, default=None,
        help="Cap the universe at N tickers (for quick smoke runs)",
    )
    parser.add_argument(
        "--output", default=None,
        help="Output JSON path (default: output_audit/fire_count_measured_<DATE>.json)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Verbose logging",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if not args.verbose else logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    if args.b640:
        strategy_names = B640_STRATEGIES
    elif args.all:
        from backtest.signals.screener import ALL_STRATEGIES
        strategy_names = sorted(ALL_STRATEGIES.keys())
    elif args.strategies:
        strategy_names = args.strategies
    else:
        print("Specify --b640, --all, or --strategies <names>", file=sys.stderr)
        return 2

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)

    output = measure_strategies(
        strategy_names, start=start, end=end, max_tickers=args.max_tickers,
    )

    if args.output:
        out_path = Path(args.output)
    else:
        out_dir = REPO_ROOT / "output_audit"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"fire_count_measured_{end.isoformat()}.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2))
    logger.info("Wrote %s", out_path)

    # Print summary
    print(f"\n=== Fire-count measurement summary ({out_path}) ===")
    print(f"Universe: {output['n_tickers']} tickers; {output['n_cache_misses']} cache misses")
    print(f"Date range: {output['date_range']['start']} -> {output['date_range']['end']}")
    print(f"Total bars: {output['n_bars_total']:,}")
    print(f"\n{'Strategy':<35} {'fires/yr (sample)':>18} {'projected_220':>15} {'verdict_220':<22} {'indep ratio':>14}")
    print("-" * 110)
    for r in output["results"]:
        print(
            f"{r['strategy']:<35} {r['measured_fires_per_calendar_year_total_sampled']:>18.2f} "
            f"{r['projected_fires_per_calendar_year_total_full_t1a']:>15.1f} "
            f"{r['projected_verdict_full_t1a']:<22} {r['independence_predicted_vs_measured_ratio']!s:>14}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
