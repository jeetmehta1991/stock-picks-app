"""scripts/mean_reversion_edge_prior_test.py

# Source: B755-COUNCIL TIER 1.3 ticket
#   S4-B755-COUNCIL-MEAN-REVERSION-EDGE-PRIOR-TEST
# per CHECKLIST #77 + #106 (data-consumption audit per B748d / 2026-06-14)
# + feedback_no_prior_edge_consolidate_before_tune (B705 lesson) +
# council peer-reviewer convergence (reviewers 1 + 5):
#   "Does mean-reversion have a tradeable edge in the T1a/T1c equity
#    universe at daily-bar frequency AT ALL?"
# Reviewer 5: "The entire Cluster A may be a 30-strategy search over a
# regime where the prior expectation is null - making walk-tuning,
# consolidation, and cube verdicts all noise-fitting."

PURPOSE.
Tests the meta-question raised by peer reviewers: does mean-reversion have
a tradeable edge at T1a daily-bar frequency in 2020-2026? Per Lo-MacKinlay
1988 literature, daily mean-reversion alpha collapsed in large-caps post-
2010; survives mainly in microcaps + intraday. If aggregate hit rates near
50% and mean PnL near 0 across the simplest possible Cluster A trigger
conditions, then ALL Cluster A walk-tuning + consolidation work is
noise-fitting per `feedback_no_prior_edge_consolidate_before_tune.md`.

METHODOLOGY.
For each "core mean-reversion" trigger condition with NO ADDITIONAL GATES:
- enter at NEXT-DAY OPEN (PIT-discipline + standard slippage assumption)
- exit at fixed N-day hold (5 / 10 / 20 trading days)
- record per-trade forward return in basis points
- aggregate: hit rate (% positive) + mean PnL + std + Sharpe-ish

Triggers tested (universe-level, no strategy-level gates):
- rsi_14<30 LONG (canonical Wilder oversold)
- rsi_14>70 SHORT (canonical Wilder overbought)
- rsi_14<20 LONG (Connors extreme)
- rsi_14>80 SHORT (Connors extreme)
- stoch K<20 LONG
- stoch K>80 SHORT
- mfi<20 LONG
- mfi>80 SHORT
- bollinger_lower_touch LONG
- bollinger_upper_touch SHORT
- williams_r<-80 LONG
- williams_r>-20 SHORT
- ultimate_oscillator<30 LONG
- ultimate_oscillator>70 SHORT

Per CHECKLIST #44(b): if smoke produces no signals, INVESTIGATE WHY
before declaring null.

OUTPUT SCHEMA.
{
  "meta": {ticker counts, runtime, etc},
  "triggers": [
    {
      "name": "rsi_14_lt_30_long",
      "n_signals": int,
      "n_tickers_with_signals": int,
      "hit_rate_5d": float (proportion of trades with fwd_ret > 0),
      "hit_rate_10d": float,
      "hit_rate_20d": float,
      "mean_pnl_5d_bps": float,
      "mean_pnl_10d_bps": float,
      "mean_pnl_20d_bps": float,
      "std_pnl_5d_bps": float,
      "std_pnl_10d_bps": float,
      "std_pnl_20d_bps": float,
      "sharpe_5d": float (mean / std, NOT annualized),
      "sharpe_10d": float,
      "sharpe_20d": float,
      "verdict": one of EDGE_EXISTS / EDGE_MARGINAL / EDGE_NULL / EDGE_NEGATIVE / INSUFFICIENT_DATA
    },
    ...
  ],
  "aggregate_verdict": one of
    "MEAN_REVERSION_EDGE_CONFIRMED" / "MEAN_REVERSION_EDGE_MARGINAL" /
    "MEAN_REVERSION_EDGE_NULL" / "INSUFFICIENT_DATA"
}

VERDICT THRESHOLDS (literature-anchored):
- EDGE_EXISTS: hit_rate > 0.53 AND mean_pnl > 10bps AND sharpe > 0.05
- EDGE_MARGINAL: hit_rate > 0.51 AND mean_pnl > 0
- EDGE_NULL: hit_rate within [0.49, 0.51] OR mean_pnl within +/-3bps
- EDGE_NEGATIVE: hit_rate < 0.49 OR mean_pnl < -3bps
- INSUFFICIENT_DATA: n_signals < 30

CLI MODES per CHECKLIST #68 smoke->demo->full progression:
- --smoke: 3 tickers x 1yr 2024
- --demo: 50 tickers x 2yr 2024-2025
- --full: T1a window-union x 2020-2026
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

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from scripts.measure_fire_count import (  # noqa: E402
    _load_ohlcv,
    _load_t1a_tickers_union_over_window,
    _precompute_signals_for_ticker,
)

logger = logging.getLogger("mean_reversion_edge_prior_test")

REPO_ROOT = Path(_REPO)
OUTPUT_DIR = REPO_ROOT / "output_audit"

# Forward-return holding horizons in trading days
HORIZONS = [5, 10, 20]

# Trigger definitions: each is (name, direction, predicate_fn).
# predicate_fn(signals) -> bool. Strategy-level gates are intentionally
# OMITTED -- this is the unconditional edge test per council reviewer.
def _trigger_rsi_14_lt_30(s):  return s.get("rsi_14", 50) < 30
def _trigger_rsi_14_gt_70(s):  return s.get("rsi_14", 50) > 70
def _trigger_rsi_14_lt_20(s):  return s.get("rsi_14", 50) < 20
def _trigger_rsi_14_gt_80(s):  return s.get("rsi_14", 50) > 80
def _trigger_stoch_lt_20(s):   return s.get("stoch_k", 50) < 20
def _trigger_stoch_gt_80(s):   return s.get("stoch_k", 50) > 80
def _trigger_mfi_lt_20(s):     return s.get("mfi", 50) < 20
def _trigger_mfi_gt_80(s):     return s.get("mfi", 50) > 80
def _trigger_bb_lower(s):      return bool(s.get("bb_20_20_touch_lower"))
def _trigger_bb_upper(s):      return bool(s.get("bb_20_20_touch_upper"))
def _trigger_wr_lt_neg80(s):   return s.get("williams_r", -50) < -80
def _trigger_wr_gt_neg20(s):   return s.get("williams_r", -50) > -20
def _trigger_uo_lt_30(s):      return s.get("uo", 50) < 30
def _trigger_uo_gt_70(s):      return s.get("uo", 50) > 70

TRIGGERS: list[tuple[str, str, callable]] = [
    ("rsi_14_lt_30_long",       "long",  _trigger_rsi_14_lt_30),
    ("rsi_14_gt_70_short",      "short", _trigger_rsi_14_gt_70),
    ("rsi_14_lt_20_long",       "long",  _trigger_rsi_14_lt_20),
    ("rsi_14_gt_80_short",      "short", _trigger_rsi_14_gt_80),
    ("stoch_k_lt_20_long",      "long",  _trigger_stoch_lt_20),
    ("stoch_k_gt_80_short",     "short", _trigger_stoch_gt_80),
    ("mfi_lt_20_long",          "long",  _trigger_mfi_lt_20),
    ("mfi_gt_80_short",         "short", _trigger_mfi_gt_80),
    ("bb_lower_touch_long",     "long",  _trigger_bb_lower),
    ("bb_upper_touch_short",    "short", _trigger_bb_upper),
    ("williams_r_lt_neg80_long",  "long",  _trigger_wr_lt_neg80),
    ("williams_r_gt_neg20_short", "short", _trigger_wr_gt_neg20),
    ("ultimate_osc_lt_30_long",   "long",  _trigger_uo_lt_30),
    ("ultimate_osc_gt_70_short",  "short", _trigger_uo_gt_70),
]


def _compute_forward_returns(
    df: pd.DataFrame, entry_idx: int, direction: str,
) -> dict[int, float]:
    """Return forward returns (bps) at each horizon for an entry at
    df.iloc[entry_idx]. Entry assumed at next-day open (entry_idx + 1
    if available); exit at +H days close.
    """
    out: dict[int, float] = {}
    n = len(df)
    if entry_idx + 1 >= n:
        return out
    entry_price = float(df["open"].iloc[entry_idx + 1])
    if entry_price <= 0:
        return out
    for H in HORIZONS:
        exit_idx = entry_idx + 1 + H
        if exit_idx >= n:
            continue
        exit_price = float(df["close"].iloc[exit_idx])
        if exit_price <= 0:
            continue
        raw_ret = (exit_price - entry_price) / entry_price
        if direction == "short":
            raw_ret = -raw_ret
        out[H] = raw_ret * 10_000  # bps
    return out


def _assign_trigger_verdict(stats: dict) -> str:
    """Per-trigger verdict using literature-anchored thresholds."""
    if stats["n_signals"] < 30:
        return "INSUFFICIENT_DATA"
    # Use 10-day as the canonical horizon
    hit_rate = stats.get("hit_rate_10d", 0.5)
    mean_pnl = stats.get("mean_pnl_10d_bps", 0.0)
    sharpe = stats.get("sharpe_10d", 0.0)
    if hit_rate > 0.53 and mean_pnl > 10.0 and sharpe > 0.05:
        return "EDGE_EXISTS"
    if hit_rate > 0.51 and mean_pnl > 0.0:
        return "EDGE_MARGINAL"
    if hit_rate < 0.49 or mean_pnl < -3.0:
        return "EDGE_NEGATIVE"
    return "EDGE_NULL"


def _assign_aggregate_verdict(trigger_results: list[dict]) -> str:
    """Roll-up verdict across all triggers."""
    qualifying = [t for t in trigger_results if t["verdict"] != "INSUFFICIENT_DATA"]
    if not qualifying:
        return "INSUFFICIENT_DATA"
    n_exist = sum(1 for t in qualifying if t["verdict"] == "EDGE_EXISTS")
    n_marginal = sum(1 for t in qualifying if t["verdict"] == "EDGE_MARGINAL")
    n_null = sum(1 for t in qualifying if t["verdict"] == "EDGE_NULL")
    n_neg = sum(1 for t in qualifying if t["verdict"] == "EDGE_NEGATIVE")
    n_total = len(qualifying)
    # Confirmed: >=3 triggers EDGE_EXISTS
    if n_exist >= 3:
        return "MEAN_REVERSION_EDGE_CONFIRMED"
    if n_exist >= 1 or n_marginal >= 3:
        return "MEAN_REVERSION_EDGE_MARGINAL"
    if n_neg >= n_total / 2:
        return "MEAN_REVERSION_EDGE_NEGATIVE"
    return "MEAN_REVERSION_EDGE_NULL"


def run_edge_prior_test(
    max_tickers: Optional[int],
    start: date,
    end: date,
    enable_extended_signals: bool = True,
) -> dict:
    """Main entry: probe each trigger across the universe, aggregate stats."""
    t0 = time.time()

    tickers_full = _load_t1a_tickers_union_over_window(start, end)
    if max_tickers is not None and max_tickers > 0:
        tickers = tickers_full[:max_tickers]
    else:
        tickers = tickers_full
    logger.info(
        "Probing %d / %d T1a tickers over [%s, %s]",
        len(tickers), len(tickers_full), start, end,
    )

    # Per-trigger accumulators
    per_trigger_pnl: dict[str, dict[int, list[float]]] = {
        name: defaultdict(list) for name, _, _ in TRIGGERS
    }
    per_trigger_tickers: dict[str, set[str]] = defaultdict(set)
    per_trigger_count: dict[str, int] = defaultdict(int)

    n_bars_total = 0
    cache_misses = 0
    as_of_cache: dict = {}

    for i, ticker in enumerate(tickers, 1):
        df = _load_ohlcv(ticker)
        if df is None:
            cache_misses += 1
            continue
        try:
            # B939 (2026-06-20) Council 47 explicit-intent: mean-reversion
            # edge prior is a STATISTICAL BASELINE artifact. Its prior was
            # computed pre-B922 with TIER 2 deferred. Flipping silently
            # re-bases the prior + invalidates downstream Bayesian updates.
            # Preserve by EXPLICIT include_tier2_producers=False; queue
            # separate ticket to recompute prior with TIER 2 if Phase P1
            # needs it.
            signals_by_bar = _precompute_signals_for_ticker(
                df, ticker, start, end,
                as_of_cache=as_of_cache,
                enable_extended_signals=enable_extended_signals,
                include_tier2_producers=False,  # B939: preserve B660 v1 baseline semantics
            )
        except Exception as exc:
            logger.warning("Precompute failed for %s: %s", ticker, exc)
            continue

        n_bars_total += len(signals_by_bar)

        # For each bar, check every trigger; if fires, compute forward
        # returns from the underlying df (need bar_date -> df index map).
        df_index_by_date = {
            d.date(): pos for pos, d in enumerate(df.index)
        }
        for bar_date, signals in signals_by_bar:
            entry_idx = df_index_by_date.get(bar_date)
            if entry_idx is None:
                continue
            for name, direction, predicate in TRIGGERS:
                if not predicate(signals):
                    continue
                fwd = _compute_forward_returns(df, entry_idx, direction)
                if not fwd:
                    continue
                per_trigger_count[name] += 1
                per_trigger_tickers[name].add(ticker)
                for H, ret_bps in fwd.items():
                    per_trigger_pnl[name][H].append(ret_bps)

        if i % 10 == 0 or i == len(tickers):
            logger.info(
                "Probed %d/%d tickers; %d bars; %s",
                i, len(tickers), n_bars_total,
                ", ".join(f"{n}={per_trigger_count[n]}" for n, _, _ in TRIGGERS[:3]),
            )

    # Aggregate per-trigger stats
    trigger_results: list[dict] = []
    for name, direction, _ in TRIGGERS:
        stat: dict = {
            "name": name,
            "direction": direction,
            "n_signals": per_trigger_count[name],
            "n_tickers_with_signals": len(per_trigger_tickers[name]),
        }
        for H in HORIZONS:
            arr = per_trigger_pnl[name][H]
            if len(arr) < 1:
                stat[f"hit_rate_{H}d"] = None
                stat[f"mean_pnl_{H}d_bps"] = None
                stat[f"std_pnl_{H}d_bps"] = None
                stat[f"sharpe_{H}d"] = None
                continue
            arr_np = np.array(arr)
            stat[f"hit_rate_{H}d"] = round(float((arr_np > 0).mean()), 4)
            stat[f"mean_pnl_{H}d_bps"] = round(float(arr_np.mean()), 2)
            stat[f"std_pnl_{H}d_bps"] = round(float(arr_np.std(ddof=1) if len(arr_np) > 1 else 0.0), 2)
            stat[f"sharpe_{H}d"] = round(
                float(arr_np.mean() / arr_np.std(ddof=1)) if (len(arr_np) > 1 and arr_np.std(ddof=1) > 0) else 0.0,
                4,
            )
        stat["verdict"] = _assign_trigger_verdict(stat)
        trigger_results.append(stat)

    runtime = round(time.time() - t0, 1)
    aggregate = _assign_aggregate_verdict(trigger_results)

    return {
        "meta": {
            "as_of_run": datetime.now().isoformat(),
            "n_tickers_universe": len(tickers_full),
            "n_tickers_probed": len(tickers),
            "n_tickers_with_data": len(tickers) - cache_misses,
            "n_cache_misses": cache_misses,
            "date_range": {"start": str(start), "end": str(end)},
            "n_bars_total": n_bars_total,
            "n_triggers": len(TRIGGERS),
            "horizons_days": HORIZONS,
            "runtime_seconds": runtime,
            "enable_extended_signals": enable_extended_signals,
            "verdict_thresholds": {
                "EDGE_EXISTS": "hit_rate>0.53 AND mean_pnl>10bps AND sharpe>0.05 (10d horizon)",
                "EDGE_MARGINAL": "hit_rate>0.51 AND mean_pnl>0",
                "EDGE_NULL": "hit_rate within [0.49, 0.51] OR mean_pnl within +/-3bps",
                "EDGE_NEGATIVE": "hit_rate<0.49 OR mean_pnl<-3bps",
                "INSUFFICIENT_DATA": "n_signals<30",
            },
        },
        "triggers": trigger_results,
        "aggregate_verdict": aggregate,
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Mean-reversion edge-prior test per "
                    "S4-B755-COUNCIL-MEAN-REVERSION-EDGE-PRIOR-TEST.",
    )
    p.add_argument("--smoke", action="store_true",
                   help="Smoke: 3 tickers x 1yr 2024 ~5min")
    p.add_argument("--demo", action="store_true",
                   help="Demo: 50 tickers x 2yr 2024-2025 ~30min")
    p.add_argument("--full", action="store_true",
                   help="Full: T1a window-union x 2020-2026 multi-hour")
    p.add_argument("--max-tickers", type=int, default=None)
    p.add_argument("--start", default="2020-01-01")
    p.add_argument("--end", default="2026-05-31")
    p.add_argument("--output", default=None)
    p.add_argument("--disable-extended-signals", action="store_true")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    args = _build_arg_parser().parse_args(argv)

    if args.smoke:
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        max_tickers = 3
        tag = "smoke"
    elif args.demo:
        start = date(2024, 1, 1)
        end = date(2025, 12, 31)
        max_tickers = 50
        tag = "demo"
    elif args.full:
        start = date(2020, 1, 1)
        end = date(2026, 5, 31)
        max_tickers = None
        tag = "full"
    else:
        start = datetime.strptime(args.start, "%Y-%m-%d").date()
        end = datetime.strptime(args.end, "%Y-%m-%d").date()
        max_tickers = args.max_tickers
        tag = "custom"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.output) if args.output else (
        OUTPUT_DIR / f"mean_reversion_edge_prior_test_{tag}.json"
    )

    logger.info("Mode=%s start=%s end=%s max_tickers=%s",
                tag, start, end, max_tickers)

    report = run_edge_prior_test(
        max_tickers=max_tickers,
        start=start, end=end,
        enable_extended_signals=not args.disable_extended_signals,
    )
    out_path.write_text(json.dumps(report, indent=2, default=str))

    # Stdout summary
    meta = report["meta"]
    print(f"\n=== mean_reversion_edge_prior_test {tag} complete ===")
    print(f"Tickers probed         : {meta['n_tickers_probed']}/{meta['n_tickers_universe']}")
    print(f"Bars total             : {meta['n_bars_total']:,}")
    print(f"Triggers tested        : {meta['n_triggers']}")
    print(f"\nPer-trigger verdicts (10-day horizon, canonical):")
    print(f"  {'TRIGGER':35s} | {'DIR':5s} | {'N':>5s} | {'HitRt':>6s} | {'PnL bps':>9s} | {'Sharpe':>7s} | VERDICT")
    print(f"  {'-'*35} | {'-'*5} | {'-'*5} | {'-'*6} | {'-'*9} | {'-'*7} | -------")
    for t in report["triggers"]:
        hr = t.get("hit_rate_10d")
        pnl = t.get("mean_pnl_10d_bps")
        sh = t.get("sharpe_10d")
        print(f"  {t['name']:35s} | {t['direction']:5s} | "
              f"{t['n_signals']:>5d} | "
              f"{(f'{hr:.3f}' if hr is not None else 'N/A'):>6s} | "
              f"{(f'{pnl:+.2f}' if pnl is not None else 'N/A'):>9s} | "
              f"{(f'{sh:+.4f}' if sh is not None else 'N/A'):>7s} | "
              f"{t['verdict']}")
    print(f"\nAGGREGATE VERDICT      : {report['aggregate_verdict']}")
    print(f"Runtime                : {meta['runtime_seconds']}s")
    print(f"Output                 : {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
