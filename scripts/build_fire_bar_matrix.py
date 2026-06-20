"""scripts/build_fire_bar_matrix.py

Fire-bar SPARSE MATRIX precompute pass.

Built Batch 756 (2026-06-15) per LLM Council B755-COUNCIL TIER 1 directive
(S4-B755-COUNCIL-FIRE-BAR-SPARSE-MATRIX-PRECOMPUTE — "the one thing to do
first"). Owner-approved 2026-06-14 "approve all for filing" + path (a)
"start TIER 1 fire-bar matrix precompute".

PURPOSE.
Produces a per-(strategy, ticker, bar) boolean fire matrix. Foundation for
- Pattern W validation via Jaccard similarity on fire-bar sets
- Pattern J consolidation per phi-correlation (B709 phi>=0.70 threshold)
- Pattern N effective-N via autocorrelation of fire-bars
- Pattern AA effective-N adjustment per cluster
- Orthogonal return-stream selection (council Advisor B framing)

Without this matrix, every Pattern W deletion candidate (A-8/A-19/A-21),
every Pattern J consolidation family verdict (RSI window / Stoch / Bollinger
/ AVWAP / Camarilla / CPR / Williams-Connors), and every effective-N
adjustment claim is unfalsifiable opinion. This single precompute resolves
half the B755-COUNCIL ticket queue.

USAGE (CLI):

  # Smoke (3 strategies x 3 tickers x 1 year; ~30sec):
  python scripts/build_fire_bar_matrix.py --smoke

  # Demo (Cluster A 30 strategies x 50 tickers x 1 year; ~5min):
  python scripts/build_fire_bar_matrix.py --demo

  # Full (Cluster A 30 strategies x T1a-union x 2020-2026; multi-hour):
  python scripts/build_fire_bar_matrix.py --full

  # Custom:
  python scripts/build_fire_bar_matrix.py \
      --strategies rsi_oversold stoch_oversold mfi_oversold \
      --max-tickers 10 --start 2024-01-01 --end 2024-12-31 \
      --output output_audit/custom_matrix.parquet

ARCHITECTURE.
Reuses scripts.measure_fire_count infrastructure:
- _load_t1a_tickers_union_over_window (B748a window-union PIT-correct)
- _load_ohlcv (Polygon OHLCV parquet loader)
- _precompute_signals_for_ticker (TIER 1 + TIER 3 producer merge)

Adds:
- Per-bar fire matrix accumulation (LONG / SHORT / AVOID directions)
- Sparse Parquet output (long-format for compact storage)
- Pairwise Jaccard + phi-correlation precompute
- Cluster A strategy default list (30 strategies)

OUTPUT SCHEMAS.

(1) Long-format fire matrix at --output (default
    output_audit/fire_bar_matrix_cluster_a.parquet):
  columns: strategy (str) | ticker (str) | bar_date (date)
           | direction (str: 'long'|'short'|'avoid')
           | fires (bool)
  index: row id
  storage: pyarrow Parquet, snappy compression
  expected size full run: ~24M cells x ~30 bytes = ~720MB uncompressed,
    ~50-150MB compressed depending on fire rate.

(2) Similarity matrix at --similarity-output (default
    output_audit/fire_bar_similarity_cluster_a.parquet):
  columns: strategy_a (str) | strategy_b (str) | direction (str)
           | n_a (int)  | n_b (int)  | n_both (int)
           | jaccard (float)  | phi_correlation (float)
           | n_bars_total (int)
  one row per strategy-pair per direction.

(3) Summary JSON at --summary-output:
  meta + per-strategy aggregate fire counts + Pattern W/J candidates
  (jaccard > 0.85 or phi > 0.70 surfaced as duplicate candidates).

CLUSTER A 30 STRATEGIES (per STAGE_4_OSCILLATOR_MEAN_REVERSION_CLUSTER_WALKS.md
state table):
  A.1 RSI (5):           rsi_oversold rsi_overbought_short rsi9_extreme
                         rsi21_slow rsi_volume_200ema
  A.2 Stoch (3):         stoch_oversold stochrsi_oversold
                         stochrsi_overbought_short
  A.3 Williams/UO/MFI 3: williams_r_oversold ultimate_oscillator mfi_oversold
  A.4 Bollinger (3):     bollinger_lower bollinger_tight bollinger_upper_short
  A.5 Keltner (1):       keltner_lower
  A.6 Camarilla (1):     camarilla_r4_breakout
                         (camarilla_rsi_obv dual + camarilla_rsi_obv_short
                         DELETED B874 per S4-B754-A-19 Pattern W council
                         5-lens option A2; deterministic strict-subset of
                         W9 strat_camarilla_s3_bounce)
  A.7 CPR (2):           cpr_narrow_momentum cpr_narrow_momentum_short
  A.8 AVWAP (3):         avwap_50_reclaim avwap_252_breakout
                         avwap_20high_rejection_short
  A.9 Momentum osc (4):  awesome_oscillator cmf_flip ppo_crossover roc_burst
  A.10 Williams/Stoch 1: williams_stoch_dual
  A.11 Prev-day (1):     prev_day_low_bounce
  A.12 BB-squeeze (1):   bb_squeeze_volume

PRE-FLIGHT per CHECKLIST #44(b) + #105: this script ORCHESTRATES existing
producers (no new producer logic). PIT discipline is inherited from the
underlying _precompute_signals_for_ticker pipeline. Per #68 the CLI exposes
smoke / demo / full as separate modes; council recommendation is to land
smoke + demo this batch + run full in background.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# Ensure repo root on sys.path
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.measure_fire_count import (  # noqa: E402
    DEFAULT_COT_SERIES,
    _load_ohlcv,
    _load_t1a_tickers_union_over_window,
    _precompute_signals_for_ticker,
)

logger = logging.getLogger("build_fire_bar_matrix")

REPO_ROOT = Path(_REPO_ROOT)
OUTPUT_DIR = REPO_ROOT / "output_audit"

# Cluster A 30 strategies per STAGE_4_OSCILLATOR_MEAN_REVERSION_CLUSTER_WALKS.md
CLUSTER_A_STRATEGIES: list[str] = [
    # A.1 RSI family
    "rsi_oversold",
    "rsi_overbought_short",
    "rsi9_extreme",
    "rsi21_slow",
    "rsi_volume_200ema",
    # A.2 Stoch / StochRSI
    "stoch_oversold",
    "stochrsi_oversold",
    "stochrsi_overbought_short",
    # A.3 Williams / Ultimate / MFI
    "williams_r_oversold",
    "ultimate_oscillator",
    "mfi_oversold",
    # A.4 Bollinger
    "bollinger_lower",
    "bollinger_tight",
    "bollinger_upper_short",
    # A.5 Keltner
    "keltner_lower",
    # A.6 Camarilla
    "camarilla_r4_breakout",
    # camarilla_rsi_obv + camarilla_rsi_obv_short DELETED B874 (B899 cluster
    # A list migration; Pattern W deterministic-duplicate verdict)
    # A.7 CPR
    "cpr_narrow_momentum",
    "cpr_narrow_momentum_short",
    # A.8 AVWAP
    "avwap_50_reclaim",
    "avwap_252_breakout",
    "avwap_20high_rejection_short",
    # A.9 Momentum oscillators
    "awesome_oscillator",
    "cmf_flip",
    "ppo_crossover",
    "roc_burst",
    # A.10 Williams/Stoch dual
    "williams_stoch_dual",
    # A.11 Prev-day mean-rev
    "prev_day_low_bounce",
    # A.12 BB-squeeze
    "bb_squeeze_volume",
]

SMOKE_STRATEGIES = ["rsi_oversold", "stoch_oversold", "mfi_oversold"]


def _eval_strategy_for_fire_bars(
    strategy_fn, signals_by_bar: list[tuple[date, dict]],
) -> list[tuple[date, str]]:
    """Return list of (bar_date, direction) for every fire.

    Differs from measure_fire_count._eval_strategy_on_precomputed which
    aggregates; here we keep the per-bar tuple so the caller can build
    the (strategy, ticker, bar) matrix.
    """
    fires: list[tuple[date, str]] = []
    for bar_date, signals in signals_by_bar:
        try:
            out = strategy_fn(signals)
        except Exception as exc:
            logger.debug("Strategy eval failed for bar %s: %s", bar_date, exc)
            continue
        if out.get("fires"):
            direction = out.get("direction") or "long"
            fires.append((bar_date, str(direction)))
    return fires


def build_fire_bar_matrix(
    strategy_names: list[str],
    start: date,
    end: date,
    max_tickers: Optional[int] = None,
    enable_extended_signals: bool = True,
) -> tuple[pd.DataFrame, dict]:
    """Build the fire-bar matrix across (strategy, ticker, bar).

    Returns:
        rows_df: long-format DataFrame with columns
            strategy, ticker, bar_date, direction, fires (always True for
            rows in the long-format; absence = no fire).
        meta: dict with run statistics + ticker / bar / strategy counts.
    """
    from backtest.signals.screener import ALL_STRATEGIES

    # Resolve T1a window-union universe (B748a PIT-correct)
    tickers_full = _load_t1a_tickers_union_over_window(start, end)
    if max_tickers is not None and max_tickers > 0:
        tickers = tickers_full[:max_tickers]
    else:
        tickers = tickers_full
    logger.info(
        "T1a window-union [%s, %s]: %d tickers (using %d after max_tickers=%s)",
        start, end, len(tickers_full), len(tickers), max_tickers,
    )

    # Resolve strategies (filter to those that exist in registry)
    resolved: list[tuple[str, object]] = []
    for name in strategy_names:
        if name not in ALL_STRATEGIES:
            logger.warning("Strategy %s not in ALL_STRATEGIES; skipping", name)
            continue
        resolved.append((name, ALL_STRATEGIES[name]))
    logger.info("Resolved %d / %d strategies", len(resolved), len(strategy_names))

    # Load OHLCV once
    t0 = time.time()
    ohlcv_cache: dict[str, pd.DataFrame] = {}
    cache_misses = 0
    for t in tickers:
        df = _load_ohlcv(t)
        if df is None:
            cache_misses += 1
            continue
        ohlcv_cache[t] = df
    logger.info(
        "OHLCV load: %d hits, %d misses (%.1fs)",
        len(ohlcv_cache), cache_misses, time.time() - t0,
    )

    # Precompute signals per ticker once (shared across all strategies)
    # Then evaluate each strategy across the precomputed signals.
    rows: list[dict] = []
    n_total_bars = 0
    n_total_fires = 0
    per_strategy_fires: dict[str, int] = defaultdict(int)
    as_of_cache: dict = {}

    t1 = time.time()
    for i, (ticker, df) in enumerate(sorted(ohlcv_cache.items()), 1):
        try:
            # B939 (2026-06-20) Council 47 explicit-intent: fire-bar matrix
            # is a COVERAGE diagnostic; truncating ~44 TIER 2-dependent
            # strategies makes the matrix non-representative of production
            # engine path.
            # B941 NOTE: kept explicit because FUNCTION-level default of
            # include_tier2_producers in _precompute_signals_for_ticker is
            # still False. B940 flipped CLI default only.
            signals_by_bar = _precompute_signals_for_ticker(
                df, ticker, start, end,
                as_of_cache=as_of_cache,
                enable_extended_signals=enable_extended_signals,
                include_tier2_producers=True,
            )
        except Exception as exc:
            logger.warning("Precompute failed for %s: %s", ticker, exc)
            continue
        n_total_bars += len(signals_by_bar)
        for strat_name, strat_fn in resolved:
            fires = _eval_strategy_for_fire_bars(strat_fn, signals_by_bar)
            for bar_date, direction in fires:
                rows.append({
                    "strategy": strat_name,
                    "ticker": ticker,
                    "bar_date": pd.Timestamp(bar_date),
                    "direction": direction,
                    "fires": True,
                })
                per_strategy_fires[strat_name] += 1
                n_total_fires += 1
        if i % 25 == 0 or i == len(ohlcv_cache):
            elapsed = time.time() - t1
            logger.info(
                "[%d / %d] tickers processed; %d total bars; %d total fires; %.1fs",
                i, len(ohlcv_cache), n_total_bars, n_total_fires, elapsed,
            )

    rows_df = pd.DataFrame(rows, columns=[
        "strategy", "ticker", "bar_date", "direction", "fires",
    ])

    meta = {
        "as_of_run": datetime.now().isoformat(),
        "start": str(start),
        "end": str(end),
        "n_tickers_universe": len(tickers_full),
        "n_tickers_evaluated": len(ohlcv_cache),
        "n_strategies_requested": len(strategy_names),
        "n_strategies_resolved": len(resolved),
        "n_bars_total": int(n_total_bars),
        "n_fires_total": int(n_total_fires),
        "per_strategy_fires": dict(per_strategy_fires),
        "enable_extended_signals": bool(enable_extended_signals),
        "runtime_seconds": round(time.time() - t1, 1),
    }
    logger.info(
        "Matrix build complete: %d fires across %d (strategy, ticker, bar) cells, %.1fs",
        n_total_fires, n_total_bars * len(resolved), time.time() - t1,
    )
    return rows_df, meta


def compute_pairwise_similarity(
    rows_df: pd.DataFrame, n_bars_total: int,
) -> pd.DataFrame:
    """Compute Jaccard + phi-correlation for every (strategy_a, strategy_b)
    pair across all directions.

    Args:
        rows_df: long-format fire DataFrame (strategy, ticker, bar_date, direction, fires=True)
        n_bars_total: total (ticker, bar) cells evaluated across all strategies
            (used as the denominator for phi-correlation 2x2 contingency).

    Returns DataFrame columns:
        strategy_a strategy_b direction n_a n_b n_both jaccard phi_correlation
    """
    if rows_df.empty:
        return pd.DataFrame(columns=[
            "strategy_a", "strategy_b", "direction", "n_a", "n_b",
            "n_both", "jaccard", "phi_correlation",
        ])

    # Build per-(strategy, direction) fire-bar sets
    fire_sets: dict[tuple[str, str], set[tuple[str, pd.Timestamp]]] = {}
    for (strat, direction), group in rows_df.groupby(["strategy", "direction"]):
        fire_sets[(strat, direction)] = set(zip(group["ticker"], group["bar_date"]))

    out_rows: list[dict] = []
    keys = sorted(fire_sets.keys())
    for i, key_a in enumerate(keys):
        for key_b in keys[i + 1:]:
            strat_a, dir_a = key_a
            strat_b, dir_b = key_b
            if dir_a != dir_b:
                continue  # only same-direction pairs
            set_a = fire_sets[key_a]
            set_b = fire_sets[key_b]
            n_a = len(set_a)
            n_b = len(set_b)
            n_both = len(set_a & set_b)
            n_union = n_a + n_b - n_both
            jaccard = n_both / n_union if n_union > 0 else 0.0
            # Phi correlation (2x2 contingency on the (ticker, bar) cells)
            # n_neither = n_bars_total - n_a - n_b + n_both
            n_neither = n_bars_total - n_a - n_b + n_both
            if n_neither < 0:
                n_neither = 0
            # phi = (n_both * n_neither - (n_a - n_both) * (n_b - n_both)) /
            #       sqrt(n_a * (n_bars - n_a) * n_b * (n_bars - n_b))
            denom = (
                n_a * (n_bars_total - n_a) * n_b * (n_bars_total - n_b)
            )
            if denom <= 0:
                phi = 0.0
            else:
                num = n_both * n_neither - (n_a - n_both) * (n_b - n_both)
                phi = num / (denom ** 0.5)
            out_rows.append({
                "strategy_a": strat_a,
                "strategy_b": strat_b,
                "direction": dir_a,
                "n_a": n_a,
                "n_b": n_b,
                "n_both": n_both,
                "jaccard": round(jaccard, 6),
                "phi_correlation": round(phi, 6),
            })
    return pd.DataFrame(out_rows)


def surface_pattern_candidates(
    similarity_df: pd.DataFrame,
    jaccard_threshold: float = 0.85,
    phi_threshold: float = 0.70,
) -> dict:
    """Surface Pattern W (deterministic-duplicate; Jaccard > threshold)
    and Pattern J (consolidation candidate; phi-correlation > threshold).
    """
    base = {
        "jaccard_threshold": jaccard_threshold,
        "phi_threshold": phi_threshold,
    }
    if similarity_df.empty:
        base["pattern_w_candidates"] = []
        base["pattern_j_candidates"] = []
        return base
    pat_w = similarity_df[similarity_df["jaccard"] >= jaccard_threshold]
    pat_j = similarity_df[similarity_df["phi_correlation"] >= phi_threshold]
    base["pattern_w_candidates"] = pat_w.to_dict(orient="records")
    base["pattern_j_candidates"] = pat_j.to_dict(orient="records")
    return base


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Build fire-bar sparse matrix + similarity per "
                    "B755-COUNCIL TIER 1 ticket.",
    )
    p.add_argument("--smoke", action="store_true",
                   help="Smoke: 3 strategies x 3 tickers x 1 year (~30s)")
    p.add_argument("--demo", action="store_true",
                   help="Demo: Cluster A 30 strategies x 50 tickers x 1 yr")
    p.add_argument("--full", action="store_true",
                   help="Full: Cluster A 30 strategies x T1a-union x 2020-2026")
    p.add_argument("--strategies", nargs="+", default=None,
                   help="Custom strategy names (overrides --smoke/--demo/--full preset)")
    p.add_argument("--start", default="2020-01-01")
    p.add_argument("--end", default="2026-05-31")
    p.add_argument("--max-tickers", type=int, default=None)
    p.add_argument("--output", default=None,
                   help="Output Parquet for long-format fire matrix")
    p.add_argument("--similarity-output", default=None,
                   help="Output Parquet for pairwise similarity matrix")
    p.add_argument("--summary-output", default=None,
                   help="Output JSON for run summary + Pattern W/J candidates")
    p.add_argument("--disable-extended-signals", action="store_true",
                   help="Disable B689 TIER 1 + TIER 3 producer merge "
                        "(for diff vs pre-B689 baseline)")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    args = _build_arg_parser().parse_args(argv)

    # Resolve preset
    if args.smoke:
        strategy_names = SMOKE_STRATEGIES
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        max_tickers = 3
        preset_tag = "smoke"
    elif args.demo:
        strategy_names = CLUSTER_A_STRATEGIES
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        max_tickers = 50
        preset_tag = "demo"
    elif args.full:
        strategy_names = CLUSTER_A_STRATEGIES
        start = date(2020, 1, 1)
        end = date(2026, 5, 31)
        max_tickers = None
        preset_tag = "full"
    else:
        strategy_names = args.strategies or CLUSTER_A_STRATEGIES
        start = datetime.strptime(args.start, "%Y-%m-%d").date()
        end = datetime.strptime(args.end, "%Y-%m-%d").date()
        max_tickers = args.max_tickers
        preset_tag = "custom"

    # Resolve output paths
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = Path(args.output) if args.output else (
        OUTPUT_DIR / f"fire_bar_matrix_cluster_a_{preset_tag}.parquet"
    )
    sim_path = Path(args.similarity_output) if args.similarity_output else (
        OUTPUT_DIR / f"fire_bar_similarity_cluster_a_{preset_tag}.parquet"
    )
    summary_path = Path(args.summary_output) if args.summary_output else (
        OUTPUT_DIR / f"fire_bar_summary_cluster_a_{preset_tag}.json"
    )

    logger.info(
        "Build mode=%s strategies=%d start=%s end=%s max_tickers=%s",
        preset_tag, len(strategy_names), start, end, max_tickers,
    )

    rows_df, meta = build_fire_bar_matrix(
        strategy_names=strategy_names,
        start=start, end=end,
        max_tickers=max_tickers,
        enable_extended_signals=not args.disable_extended_signals,
    )

    # Save long-format matrix
    rows_df.to_parquet(output_path, index=False, compression="snappy")
    logger.info("Wrote %d rows to %s (%.1f MB)",
                len(rows_df), output_path,
                output_path.stat().st_size / 1e6 if output_path.exists() else 0)

    # Compute similarity matrix
    n_bars_total = meta["n_bars_total"] * meta["n_strategies_resolved"]
    # n_bars_total in meta is per-strategy cell count; for phi denominator
    # we want per-(ticker, bar) cell count which is meta["n_bars_total"].
    # Use per-strategy denominator for safety (over-counts -> phi conservative).
    sim_df = compute_pairwise_similarity(rows_df, n_bars_total=meta["n_bars_total"])
    sim_df.to_parquet(sim_path, index=False, compression="snappy")
    logger.info("Wrote %d pairs to %s", len(sim_df), sim_path)

    # Surface Pattern W / J candidates
    patterns = surface_pattern_candidates(sim_df)
    meta["pattern_candidates"] = {
        "jaccard_threshold": patterns["jaccard_threshold"],
        "phi_threshold": patterns["phi_threshold"],
        "n_pattern_w_candidates": len(patterns["pattern_w_candidates"]),
        "n_pattern_j_candidates": len(patterns["pattern_j_candidates"]),
    }

    summary = {
        "meta": meta,
        "patterns": patterns,
        "output_paths": {
            "long_format_matrix": str(output_path),
            "similarity_matrix": str(sim_path),
            "summary": str(summary_path),
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2, default=str))
    logger.info("Wrote summary to %s", summary_path)

    # Final stdout summary
    print(f"\n=== build_fire_bar_matrix {preset_tag} complete ===")
    print(f"Strategies resolved : {meta['n_strategies_resolved']}/{meta['n_strategies_requested']}")
    print(f"Tickers evaluated   : {meta['n_tickers_evaluated']}/{meta['n_tickers_universe']}")
    print(f"Bars total          : {meta['n_bars_total']:,}")
    print(f"Fires total         : {meta['n_fires_total']:,}")
    print(f"Pattern W candidates: {meta['pattern_candidates']['n_pattern_w_candidates']} (jaccard>=0.85)")
    print(f"Pattern J candidates: {meta['pattern_candidates']['n_pattern_j_candidates']} (phi>=0.70)")
    print(f"Long-format matrix  : {output_path}")
    print(f"Similarity matrix   : {sim_path}")
    print(f"Summary             : {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
