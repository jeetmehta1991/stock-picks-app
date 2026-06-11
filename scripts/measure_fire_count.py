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
        # Universe projection: linear scale from N sampled tickers to the
        # PIT-active T1a count at as_of (= calendar end). Owner directive
        # 2026-06-09 post-external-AI critique: target ~503 active (T1a
        # active subset PIT-eligible at as_of), NOT 614 all-time T1a or
        # 220 hardcoded. The hardcoded-220 was a B641 bug -- understated
        # projections by ~2.3x. Per critique #1: "is the universe 220 or
        # 614? scale factor wrong either way."
        #
        # The active count is captured from the actual ticker load in
        # `measure_strategies` (set as `self.n_tickers_full_t1a` on each
        # result). If absent (legacy callers), fall back to 503 (B648
        # owner-approved literal: T1a active at 2024-12-31 per CLAUDE.md
        # canonical-fact F-002).
        #
        # CAVEAT (still): linear scaling assumes the sample is
        # representative of the full universe. The default ticker-sample
        # strategy `first` (alphabetical-ish) over-weights large-cap
        # survivors; breakout/trend strategies (W6/W8) fire more on
        # large-cap uptrending names than they would on
        # small/distressed/delisted names. Use --ticker-sample-strategy
        # `random` or `stratified` for less-biased samples, and
        # `--max-tickers 0` (all) for the authoritative run.
        n_tickers_sampled = max(getattr(self, "n_tickers_sampled", 1), 1)
        n_tickers_full_t1a = max(getattr(self, "n_tickers_full_t1a", 503), 1)
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
            "projection_scale_factor": round(n_tickers_full_t1a / n_tickers_sampled, 2),
            "n_tickers_full_t1a_used_for_projection": n_tickers_full_t1a,
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


# ---------------------------------------------------------------------------
# B689 (2026-06-11): TIER 1 + TIER 3 producer wire-in per B660 self-critique.
# Pre-B689 the precompute loop called only `compute_all_signals` from
# technical.py. Strategies whose entry depends on non-technical producers
# (chart_patterns, smc_ict, ict_producers, multi_timeframe, volume_profile,
# cross_asset, calendar_effects, macro_events, cot_positioning) were
# structurally guaranteed 0 fires/yr -- 103 of 146 FAIL_FIRE_STARVED
# verdicts in B660 were false negatives caused by this harness gap.
#
# B689 extends the precompute to:
#   TIER 1 (per-bar df-only; no cache deps): chart_patterns + smc_ict +
#     ict_producers + multi_timeframe + volume_profile
#   TIER 3 (per-as_of global; cached once per unique date across all
#     tickers): cross_asset + calendar_effects + pre_fomc + cot_combined
#
# DEFERRED to B690 (Tier 2): per-(ticker, as_of) cache-read producers
# (insider, institutional, short_interest, sec_edgar, news_sentiment,
# pead, search_volume, congressional_*, recent_8k). Those require
# per-ticker parquet pre-load architecture; out of B689 scope.
# Cross-sectional is similarly deferred (needs ohlcv_dict of ALL tickers).
# ---------------------------------------------------------------------------

# Default COT series injected as TIER 3 signals. Series chosen for breadth
# (equity, fx, commodity, rates). All exist in data_prefetch/cftc/ per
# B689 cache audit. Owner can extend via --cot-series CLI flag.
DEFAULT_COT_SERIES = (
    "cot_emini_sp500",
    "cot_emini_nasdaq100",
    "cot_dxy_dollar_idx",
    "cot_gold",
    "cot_wti_crude",
    "cot_vix_futures",
    "cot_treasury_10y",
)


def _compute_tier3_signals_for_as_of(
    as_of: date,
    cot_series: tuple[str, ...] = DEFAULT_COT_SERIES,
) -> dict:
    """B689: TIER 3 per-as_of global signals (one call per unique bar_date,
    shared across all tickers). Produces a flat dict combining:
      cross_asset.compute_cross_asset_signals(as_of)
      calendar_effects.compute_calendar_signals(as_of)
      macro_events.compute_pre_fomc_signals(as_of)
      cot_positioning.compute_cot_series_signals(series, as_of) for each
        series in `cot_series` (default: 7 series covering equity/fx/comm/rates)

    Each producer is wrapped in try/except so a single failure (e.g.,
    missing CFTC parquet) silently degrades to empty rather than killing
    the whole precompute loop. Failures are logged at DEBUG.
    """
    out: dict = {}
    try:
        from backtest.signals.cross_asset import compute_cross_asset_signals
        out.update(compute_cross_asset_signals(as_of))
    except Exception as exc:
        logger.debug("cross_asset failed at %s: %s", as_of, exc)
    try:
        from backtest.signals.calendar_effects import compute_calendar_signals
        out.update(compute_calendar_signals(as_of))
    except Exception as exc:
        logger.debug("calendar_effects failed at %s: %s", as_of, exc)
    try:
        from backtest.signals.macro_events import compute_pre_fomc_signals
        out.update(compute_pre_fomc_signals(as_of))
    except Exception as exc:
        logger.debug("pre_fomc failed at %s: %s", as_of, exc)
    try:
        from backtest.signals.cot_positioning import compute_cot_series_signals
        for series in cot_series:
            try:
                out.update(compute_cot_series_signals(series, as_of))
            except Exception as exc:
                logger.debug("cot %s failed at %s: %s", series, as_of, exc)
    except Exception as exc:
        logger.debug("cot import failed: %s", exc)
    return out


def _compute_tier1_signals_for_bar(sub_df: pd.DataFrame, ticker: str) -> dict:
    """B689: TIER 1 per-bar df-only signals (chart_patterns + smc + ict +
    multi_timeframe + volume_profile). All take only the OHLCV slice;
    no external cache reads. Each producer wrapped in try/except so a
    single failure degrades silently rather than killing the precompute.

    Key-collision policy: technical.py signals are computed FIRST (the
    caller passes those in via the outer dict); TIER 1 outputs added
    SECOND. If a producer emits a key that overlaps technical.py, the
    TIER 1 value wins (this is intentional -- TIER 1 producers are more
    specific, e.g., `weekly_bias_bull` vs none in technical.py).
    """
    out: dict = {}
    # chart_patterns: cup_and_handle / head_and_shoulders / triangles /
    # flags / wedges / double-tops/bottoms / + 3 B685 new producers for
    # retest variants.
    try:
        from backtest.signals.chart_patterns import (
            compute_all_chart_patterns,
        )
        out.update(compute_all_chart_patterns(sub_df))
    except Exception as exc:
        logger.debug("chart_patterns failed for %s: %s", ticker, exc)
    # smc_ict: SMC primitives (BOS/CHoCH, FVG, order_block, liquidity_swept,
    # premium/discount, mitigation_block, equal_highs/lows, OTE, inverse_FVG).
    # Owns ~ 30 keys feeding all 18 SMC strategies + ICT-7/8/9/10 (Turtle
    # Soup + Judas Swing) sub-features.
    try:
        from backtest.signals.smc_ict import compute_smc_signals
        out.update(compute_smc_signals(sub_df, ticker=ticker))
    except Exception as exc:
        logger.debug("smc_ict failed for %s: %s", ticker, exc)
    # ict_producers (B581): po3_mmbm_setup + po3_mmsm_setup (PO3 plural)
    # + week_opening_gap signals (ICT-11/12).
    try:
        from backtest.signals.ict_producers import (
            compute_po3_signals,
            compute_week_opening_gap_signals,
        )
        out.update(compute_po3_signals(sub_df))
        out.update(compute_week_opening_gap_signals(sub_df))
    except Exception as exc:
        logger.debug("ict_producers failed for %s: %s", ticker, exc)
    # multi_timeframe: weekly_bias_bull/_bear, monthly_bias_bull/_bear,
    # htf_aligned_bull/_bear/_disagreement, po3_bullish/_bearish (singular
    # PO3 from multi_timeframe.py is distinct from ict_producers.py's
    # plural setups -- both naming conventions live per B675 audit).
    try:
        from backtest.signals.multi_timeframe import (
            compute_weekly_bias, compute_monthly_bias,
            compute_htf_alignment, compute_po3_signal,
        )
        weekly = compute_weekly_bias(sub_df)
        monthly = compute_monthly_bias(sub_df)
        out.update(weekly)
        out.update(monthly)
        out.update(compute_htf_alignment(weekly, monthly))
        out.update(compute_po3_signal(sub_df))
    except Exception as exc:
        logger.debug("multi_timeframe failed for %s: %s", ticker, exc)
    # volume_profile: poc_magnet / value_area_high|low / naked_poc / etc.
    try:
        from backtest.signals.volume_profile import compute_volume_profile
        out.update(compute_volume_profile(sub_df))
    except Exception as exc:
        logger.debug("volume_profile failed for %s: %s", ticker, exc)
    return out


def _precompute_signals_for_ticker(
    df: pd.DataFrame, ticker: str, start: date, end: date,
    as_of_cache: Optional[dict] = None,
    enable_extended_signals: bool = True,
    cot_series: tuple[str, ...] = DEFAULT_COT_SERIES,
) -> list[tuple[date, dict]]:
    """Compute signals for every bar in [start, end] for one ticker.

    Returned once; reused across all strategies that evaluate this
    ticker. Single biggest speedup vs the naive per-strategy loop.

    B689: extended to merge TIER 1 (df-only) + TIER 3 (per-as_of global)
    producer outputs into the per-bar signals dict. `as_of_cache` is a
    dict[date, dict] mapping bar_date -> TIER 3 signals (lazily filled
    on cache miss; shared across all tickers in the run). If
    `enable_extended_signals` is False, behavior reverts to pre-B689
    (compute_all_signals only) for diffing.
    """
    from backtest.signals.technical import compute_all_signals
    out: list[tuple[date, dict]] = []
    if len(df) < 250:
        return out
    if as_of_cache is None:
        as_of_cache = {}
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
        if enable_extended_signals:
            # B689 TIER 1 merge (df-only producers; ~10 modules)
            tier1 = _compute_tier1_signals_for_bar(sub_df, ticker)
            signals.update(tier1)
            # B689 TIER 3 merge (per-as_of global; cached across tickers)
            if bar_date not in as_of_cache:
                as_of_cache[bar_date] = _compute_tier3_signals_for_as_of(bar_date, cot_series)
            signals.update(as_of_cache[bar_date])
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
    ticker_sample_strategy: str = "first",
    random_seed: int = 42,
    enable_extended_signals: bool = True,
    cot_series: tuple[str, ...] = DEFAULT_COT_SERIES,
) -> dict:
    """Measure fires for each named strategy across the T1a universe.

    `ticker_sample_strategy` (B648 owner-directed post-critique):
      "first" -- alphabetical-ish first N (legacy default; B641 used this;
                 over-weights large-cap survivors -- per external-AI critique
                 #1 the breakout/trend strategies fire much more on this
                 subset than on a representative T1a sample)
      "random" -- pseudo-random N tickers (more representative; seeded
                 for reproducibility)
      "stratified" -- TODO: when sector metadata loads correctly, stratify
                 by sector. For B648 ships "random" as the closest
                 representative option.
      "all" -- skip sampling; use full PIT-active T1a (overnight run)
    """
    import random as _random
    from backtest.signals.screener import ALL_STRATEGIES

    tickers_full = _load_t1a_tickers(end)
    n_tickers_full_t1a = len(tickers_full)
    logger.info(
        "T1a PIT-active at as_of=%s: %d tickers (used as projection target)",
        end, n_tickers_full_t1a,
    )

    if max_tickers is None or max_tickers == 0 or max_tickers >= n_tickers_full_t1a:
        tickers = tickers_full
    elif ticker_sample_strategy == "random" or ticker_sample_strategy == "stratified":
        # Stratified falls back to random for B648; sector-stratified TODO
        rng = _random.Random(random_seed)
        tickers = sorted(rng.sample(tickers_full, max_tickers))
        logger.info(
            "Sample strategy: %s (seed=%d) -> %d tickers from %d-PIT-active",
            ticker_sample_strategy, random_seed, len(tickers), n_tickers_full_t1a,
        )
    else:
        # "first" (legacy default)
        tickers = tickers_full[:max_tickers]
        logger.info("Sample strategy: first %d (alphabetical-ish; LEGACY -- consider --ticker-sample-strategy random)", max_tickers)

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
    # B665 follow-up post-B660-crash-triage: added per-ticker progress logging
    # (every 25 tickers) + per-ticker try/except for crash-diagnosis traceback.
    # Pre-fix the loop ran silently for 503 tickers x ~1200 bars; a crash mid-
    # loop produced 4 hours of silence with no error indication. Per-25 progress
    # logs let the operator see whether the run is alive, and the try/except
    # surfaces the ticker that crashes if any single-ticker compute fails.
    t_pre = time.time()
    signals_cache: dict[str, list[tuple[date, dict]]] = {}
    # B689: shared per-as_of cache for TIER 3 signals (cross_asset +
    # calendar + pre_fomc + cot). Filled lazily on cache-miss inside
    # _precompute_signals_for_ticker; reused across all subsequent
    # tickers. Net effect: TIER 3 producers run once per unique bar_date
    # in the run, not 503-times-per-bar.
    tier3_as_of_cache: dict[date, dict] = {}
    if enable_extended_signals:
        logger.info(
            "B689 extended signals ENABLED: TIER 1 (chart_patterns + smc + ict + multi_timeframe + volume_profile) "
            "+ TIER 3 (cross_asset + calendar + pre_fomc + %d cot series) wired into precompute path",
            len(cot_series),
        )
    else:
        logger.info("B689 extended signals DISABLED (pre-B689 behavior; technical.py producers only)")
    n_tickers_total = len(ohlcv_cache)
    n_done = 0
    for ticker, df in ohlcv_cache.items():
        try:
            signals_cache[ticker] = _precompute_signals_for_ticker(
                df, ticker, start, end,
                as_of_cache=tier3_as_of_cache,
                enable_extended_signals=enable_extended_signals,
                cot_series=cot_series,
            )
        except Exception as exc:
            import traceback
            logger.error(
                "Signal precompute CRASHED on ticker=%s (after %d of %d done; %.1fs elapsed); traceback below; continuing with empty signals for this ticker",
                ticker, n_done, n_tickers_total, time.time() - t_pre,
            )
            logger.error("Traceback:\n%s", traceback.format_exc())
            signals_cache[ticker] = []
        n_done += 1
        if n_done % 25 == 0 or n_done == n_tickers_total:
            elapsed = time.time() - t_pre
            rate = n_done / elapsed if elapsed > 0 else 0
            eta_sec = (n_tickers_total - n_done) / rate if rate > 0 else 0
            logger.info(
                "Signal precompute progress: %d / %d tickers done (%.1f%%); %.1fs elapsed; %.2f tickers/sec; ETA %.0fs",
                n_done, n_tickers_total, 100.0 * n_done / n_tickers_total,
                elapsed, rate, eta_sec,
            )
    n_signal_evals = sum(len(v) for v in signals_cache.values())
    logger.info(
        "Signal precompute COMPLETE: %d total (ticker, bar) signal-dicts cached (%.1fs)",
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
        result.n_tickers_full_t1a = n_tickers_full_t1a  # B648 -- pass actual T1a active count
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
        "n_tickers_sampled": tickers_evaluated,
        "n_tickers_full_t1a_pit_active": n_tickers_full_t1a,
        "projection_scale_factor": round(n_tickers_full_t1a / max(tickers_evaluated, 1), 2),
        "ticker_sample_strategy": ticker_sample_strategy,
        "ticker_sample_seed": random_seed if ticker_sample_strategy in ("random", "stratified") else None,
        "n_cache_misses": cache_misses,
        "date_range": {"start": start.isoformat(), "end": end.isoformat()},
        "n_bars_total": total_bars,
        "results": [r.to_dict() for r in results],
        "non_representativeness_caveat": (
            "20-large-cap-sample x single-regime-arc (2022 bear -> 2023-24 bull) linearly "
            "scaled to T1a active. Breakout/trend strategies over-fire on this sample vs full universe; "
            "knife-catch strategies under-fire vs full universe (delisted/distressed names absent). "
            "Per external-AI critique 2026-06-09: 'specific verdict reversals are HYPOTHESES, not "
            "results.' Authoritative numbers require full --max-tickers 0 run across multiple regimes."
        ),
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
        help="Cap the universe at N tickers (for quick smoke runs). Pass 0 or N >= full T1a active count to disable sampling.",
    )
    parser.add_argument(
        "--ticker-sample-strategy", default="first",
        choices=["first", "random", "stratified", "all"],
        help="(B648) How to pick N tickers from T1a. 'first'=alphabetical-ish (LEGACY; over-weights large-cap survivors), 'random'=seeded random (representative), 'stratified'=sector-stratified (TODO falls back to random), 'all'=full universe. Default 'first' for backward-compat; prefer 'random' or 'all' for honest measurement.",
    )
    parser.add_argument(
        "--random-seed", type=int, default=42,
        help="(B648) Seed for random/stratified sampling. Default 42; change to test sensitivity.",
    )
    parser.add_argument(
        "--output", default=None,
        help="Output JSON path (default: output_audit/fire_count_measured_<DATE>.json)",
    )
    parser.add_argument(
        "--no-extended-signals", action="store_true",
        help="(B689) DISABLE TIER 1 + TIER 3 producer wire-in (chart_patterns, smc_ict, ict_producers, multi_timeframe, volume_profile, cross_asset, calendar_effects, pre_fomc, cot). Reverts to pre-B689 behavior (technical.py producers only). Use for diff vs the B660 baseline run.",
    )
    parser.add_argument(
        "--cot-series", nargs="+", default=list(DEFAULT_COT_SERIES),
        help=f"(B689) COT series to inject. Default: {list(DEFAULT_COT_SERIES)}. Must match filenames in data_prefetch/cftc/ (without .parquet).",
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
        ticker_sample_strategy=args.ticker_sample_strategy,
        random_seed=args.random_seed,
        enable_extended_signals=not args.no_extended_signals,
        cot_series=tuple(args.cot_series),
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
    print(f"Sample: {output['n_tickers_sampled']} tickers (strategy={output['ticker_sample_strategy']}, seed={output.get('ticker_sample_seed')})")
    print(f"T1a PIT-active at as_of: {output['n_tickers_full_t1a_pit_active']} tickers; projection scale x{output['projection_scale_factor']}")
    print(f"Cache misses: {output['n_cache_misses']}; date range: {output['date_range']['start']} -> {output['date_range']['end']}")
    print(f"Total bars: {output['n_bars_total']:,}")
    print(f"\nCAVEAT: {output['non_representativeness_caveat']}\n")
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
