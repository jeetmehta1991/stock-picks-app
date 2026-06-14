"""scripts/checklist_106_cluster_a_producer_audit.py

# Source: B755-COUNCIL TIER 1.2 ticket
#   S4-B755-COUNCIL-CHECKLIST-106-CLUSTER-A-PRODUCER-DATA-AUDIT
# per CHECKLIST #77 + #106 (data-consumption audit per B748d / 2026-06-14)
# + feedback_data_consumption_audit_must_apply_checklist_44b memory rule.

CHECKLIST #106 data-consumption audit on Cluster A producers.

Built Batch 757 (2026-06-15) per B755-COUNCIL TIER 1.2 ticket
S4-B755-COUNCIL-CHECKLIST-106-CLUSTER-A-PRODUCER-DATA-AUDIT. Owner-approved
2026-06-14 "approve all for filing" + council chairman recommendation.

PURPOSE.
Apply CHECKLIST #106 + `feedback_data_consumption_audit_must_apply_checklist_44b`
discipline to every Cluster A producer signal. Per peer-reviewer convergence:
"After B748c surfaced 9 EXPLORATORY for default-empty/schema-contract holes
in OBV/MACD/AVWAP-class producers, the assumption that RSI/Stoch/Williams/MFI/
Camarilla/BB producers return non-empty across T1a/T1c/T2/T3 x 2020-2026 is
UNTESTED. Pattern Q, Pattern W, EXPLORATORY tags are all CONDITIONAL ON A
FALSE PREMISE if any oscillator silently returns empty on a tier/date slice."

This script systematically probes:
  (a) path-from-source -- trivial for technical.py (reads OHLCV directly)
  (b) recursive glob -- N/A (technical.py is one file)
  (c) temporal-coverage probe -- per-year emission stats
  (d) schema-contract probe -- declared signals_used vs producer-emitted dict
  (e) KNOWN-EVENT runtime probe -- e.g. AAPL 2020-03-23 RSI<35 known to hold
  (f) #44(b) investigate-why -- root cause for any missing signal

OUTPUT.
JSON report at output_audit/checklist_106_cluster_a_producer_audit_<tag>.json
with structure:
  {
    "meta": {
      "n_tickers_probed": int,
      "date_range": {"start": "...", "end": "..."},
      "n_cluster_a_strategies": int,
      "n_unique_signals_declared": int,
      "runtime_seconds": float
    },
    "declared_signals_inventory": {
      "<signal_name>": {
        "n_strategies_using": int,
        "strategies": [list of strategy names]
      },
      ...
    },
    "signal_coverage": {
      "<signal_name>": {
        "n_tickers_emitting": int,
        "n_tickers_with_True": int,    # for boolean signals
        "n_tickers_probed": int,
        "by_year": {
          "2024": {"emitted": True, "n_True": int, "n_observations": int},
          ...
        }
      },
      ...
    },
    "pattern_f_candidates": [
      {"signal": "x", "reason": "declared but never emitted across N tickers"},
      ...
    ],
    "temporal_gaps": [
      {"signal": "y", "year": "2022", "issue": "emission rate 0%"},
      ...
    ],
    "known_event_probes": [
      {"ticker": "AAPL", "date": "2020-03-23",
       "signal": "rsi_oversold", "expected": True, "actual": True/False},
      ...
    ]
  }

USAGE.
  # Smoke (3 tickers x 1 yr):
  python scripts/checklist_106_cluster_a_producer_audit.py --smoke

  # Demo (50 tickers x 2yr 2024-2025):
  python scripts/checklist_106_cluster_a_producer_audit.py --demo

  # Full (T1a window-union x 2020-2026):
  python scripts/checklist_106_cluster_a_producer_audit.py --full

  # Custom:
  python scripts/checklist_106_cluster_a_producer_audit.py \
      --max-tickers 10 --start 2024-01-01 --end 2024-12-31

PRE-FLIGHT per `feedback_data_consumption_audit_must_apply_checklist_44b`:
this script SOURCE-VERIFIES the assumption that all Cluster A producers
emit non-empty across the universe. Before B757, this assumption was
inherited from B660/B689 measurement runs at AGGREGATE level. CHECKLIST #106
requires per-signal/per-year/per-ticker temporal-coverage probe.
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

import pandas as pd

# Repo root on sys.path
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from scripts.build_fire_bar_matrix import CLUSTER_A_STRATEGIES  # noqa: E402
from scripts.measure_fire_count import (  # noqa: E402
    _load_ohlcv,
    _load_t1a_tickers_union_over_window,
    _precompute_signals_for_ticker,
)

logger = logging.getLogger("checklist_106_cluster_a_audit")

REPO_ROOT = Path(_REPO)
OUTPUT_DIR = REPO_ROOT / "output_audit"

# KNOWN-EVENT probes per CHECKLIST #106(e). These are dates where, per
# market history, specific oscillator signals are known to have triggered.
# If a producer fails to emit the signal on these dates, the producer has
# a bug or temporal-coverage gap.
KNOWN_EVENT_PROBES: list[dict] = [
    # March 2020 COVID crash: most T1a tickers were deeply oversold.
    # rsi_14 < 35 on AAPL 2020-03-23 is canonical (closing low of crash).
    {"ticker": "AAPL", "date": "2020-03-23", "signal": "rsi_14<35",
     "expected": True, "note": "COVID crash low; AAPL RSI(14) was ~22"},
    # August 2024 carry-unwind: oversold conditions across mega-caps
    {"ticker": "AAPL", "date": "2024-08-05", "signal": "rsi_14<35",
     "expected": True, "note": "August 2024 carry-unwind; AAPL gapped down"},
]


class _DirectionSeed(dict):
    """Magic signals dict that triggers strategies in a given direction so we
    can discover their declared `signals_used`.

    B757 fix: `_strat3` returns `signals_used=[]` when neither fl nor fs
    fires. To collect signals from dual strategies, we run each strategy
    with multiple seed configurations and union the declared signals:
      - LONG oscillator (numeric -> 2.0): triggers rsi<35-class gates
      - SHORT oscillator (numeric -> 98.0): triggers rsi>65-class gates
      - LONG proximity (numeric -> 0.1): triggers abs(x) < threshold gates
        used by AVWAP / Bollinger / Camarilla level-touch strategies
      - SHORT proximity (numeric -> -0.1): mirror of above

    `dtc` returns 0 in all seeds to avoid _short_borrow_trap_active
    blocking SHORT branches.
    """

    def __init__(self, direction: str, numeric_value: float):
        super().__init__()
        self.direction = direction
        self.numeric_value = numeric_value

    def get(self, key, default=None):
        if key == "dtc":
            return 0  # avoid borrow trap
        if isinstance(default, bool) or default is None:
            return True
        if isinstance(default, (int, float)):
            return self.numeric_value
        return True

    def __contains__(self, key):
        return True


def _gather_declared_signals(strategy_names: list[str]) -> dict[str, list[str]]:
    """Run each strategy on LONG-biased + SHORT-biased seed dicts to
    discover declared `signals_used`. Returns {signal_name: [strategies]}.

    B757 update: empty-dict call returned `signals_used=[]` for all 23
    dual `_strat3` strategies because neither direction fired (default
    numeric values 50 don't satisfy oversold AND overbought simultaneously).
    The seed-based approach triggers each branch once and unions the
    declared signals.
    """
    from backtest.signals.screener import ALL_STRATEGIES

    inventory: dict[str, list[str]] = defaultdict(list)
    seeds = [
        _DirectionSeed("long", 2.0),     # oversold oscillator
        _DirectionSeed("short", 98.0),    # overbought oscillator
        _DirectionSeed("long", 0.1),      # proximity LONG (small pos)
        _DirectionSeed("short", -0.1),    # proximity SHORT (small neg)
    ]

    for strat_name in strategy_names:
        if strat_name not in ALL_STRATEGIES:
            logger.warning("Strategy %s not in registry", strat_name)
            continue
        strat_fn = ALL_STRATEGIES[strat_name]

        per_strategy_signals: set[str] = set()
        for seed in seeds:
            try:
                result = strat_fn(seed)
            except Exception as exc:
                logger.debug(
                    "Strategy %s failed on seed %s: %s",
                    strat_name, seed.direction, exc,
                )
                continue
            signals_used = result.get("signals_used", []) or []
            for sig in signals_used:
                if isinstance(sig, str):
                    per_strategy_signals.add(sig)
                elif isinstance(sig, dict):
                    name = sig.get("name") or sig.get("signal")
                    if name:
                        per_strategy_signals.add(str(name))

        for sig in per_strategy_signals:
            inventory[sig].append(strat_name)

    return dict(inventory)


def _probe_producer_coverage(
    tickers: list[str], start: date, end: date,
    enable_extended_signals: bool = True,
) -> tuple[dict, int]:
    """For each ticker, precompute signals across the window. Aggregate:
      - per-signal: number of tickers emitting + count of True/non-None values
      - per-signal-year: emission rate per year for temporal-gap detection

    Returns (signal_stats, n_bars_total).
    """
    signal_stats: dict[str, dict] = defaultdict(lambda: {
        "n_tickers_emitting": 0,
        "n_tickers_with_True": 0,
        "n_observations": 0,
        "n_True_observations": 0,
        "by_year": defaultdict(lambda: {"n_observations": 0, "n_True": 0}),
    })

    n_bars_total = 0
    as_of_cache: dict = {}

    for i, ticker in enumerate(tickers, 1):
        df = _load_ohlcv(ticker)
        if df is None:
            logger.debug("OHLCV miss for %s", ticker)
            continue
        try:
            signals_by_bar = _precompute_signals_for_ticker(
                df, ticker, start, end,
                as_of_cache=as_of_cache,
                enable_extended_signals=enable_extended_signals,
            )
        except Exception as exc:
            logger.warning("Precompute failed for %s: %s", ticker, exc)
            continue

        n_bars_total += len(signals_by_bar)

        # Track which signals THIS ticker emits at least once
        ticker_emitted: set[str] = set()
        ticker_emitted_True: set[str] = set()

        for bar_date, signals in signals_by_bar:
            year = str(bar_date.year)
            for sig_name, sig_val in signals.items():
                stats = signal_stats[sig_name]
                stats["n_observations"] += 1
                year_stats = stats["by_year"][year]
                year_stats["n_observations"] += 1
                # Treat boolean True or truthy non-None as "active"
                if sig_val is True or (sig_val and isinstance(sig_val, bool)):
                    stats["n_True_observations"] += 1
                    year_stats["n_True"] += 1
                    ticker_emitted_True.add(sig_name)
                ticker_emitted.add(sig_name)

        for sig in ticker_emitted:
            signal_stats[sig]["n_tickers_emitting"] += 1
        for sig in ticker_emitted_True:
            signal_stats[sig]["n_tickers_with_True"] += 1

        if i % 10 == 0 or i == len(tickers):
            logger.info("Probed %d/%d tickers; %d bars", i, len(tickers), n_bars_total)

    # Convert defaultdicts to dicts for JSON
    out: dict = {}
    for sig, stats in signal_stats.items():
        out[sig] = {
            "n_tickers_emitting": stats["n_tickers_emitting"],
            "n_tickers_with_True": stats["n_tickers_with_True"],
            "n_observations": stats["n_observations"],
            "n_True_observations": stats["n_True_observations"],
            "by_year": {y: dict(s) for y, s in stats["by_year"].items()},
        }
    return out, n_bars_total


def _detect_pattern_f_candidates(
    declared_signals: dict[str, list[str]],
    signal_coverage: dict,
    n_tickers_probed: int,
) -> list[dict]:
    """Pattern F-class: declared in strategy signals_used BUT never emitted
    across all probed tickers.
    """
    candidates = []
    for sig_name, strats in declared_signals.items():
        cov = signal_coverage.get(sig_name)
        if cov is None or cov["n_tickers_emitting"] == 0:
            candidates.append({
                "signal": sig_name,
                "issue": "declared_but_never_emitted",
                "n_strategies_declaring": len(strats),
                "strategies": strats,
                "n_tickers_probed": n_tickers_probed,
                "severity": "HIGH" if len(strats) >= 2 else "MEDIUM",
            })
        elif cov["n_tickers_with_True"] == 0:
            # Emitted as False on all observations -> Pattern F-class
            # silent-no-op (strategy can never fire if this is required gate)
            candidates.append({
                "signal": sig_name,
                "issue": "emitted_but_always_False",
                "n_strategies_declaring": len(strats),
                "strategies": strats,
                "n_observations": cov["n_observations"],
                "severity": "HIGH" if len(strats) >= 2 else "MEDIUM",
            })
    return candidates


def _detect_temporal_gaps(
    signal_coverage: dict,
    declared_signals: dict[str, list[str]],
    min_rate_threshold: float = 0.001,
) -> list[dict]:
    """Per CHECKLIST #106(c): for each declared signal, identify years where
    emission rate < min_rate_threshold (default 0.1%). This catches silently
    missing data slices (e.g. producer breaks on 2022 OHLCV schema change).
    """
    gaps = []
    declared_set = set(declared_signals.keys())
    for sig_name, cov in signal_coverage.items():
        if sig_name not in declared_set:
            continue  # only audit declared signals
        for year, year_stats in cov["by_year"].items():
            n_obs = year_stats["n_observations"]
            n_true = year_stats["n_True"]
            if n_obs == 0:
                continue
            rate = n_true / n_obs
            if rate < min_rate_threshold:
                gaps.append({
                    "signal": sig_name,
                    "year": year,
                    "emission_rate": round(rate, 6),
                    "n_True": n_true,
                    "n_observations": n_obs,
                    "issue": "emission_rate_below_threshold",
                })
    return gaps


def _run_known_event_probes(
    enable_extended_signals: bool = True,
) -> list[dict]:
    """Per CHECKLIST #106(e): run producer on KNOWN historical event dates
    and verify the expected signal triggers. If not, that's a strong producer
    bug indicator.
    """
    results = []
    as_of_cache: dict = {}
    for probe in KNOWN_EVENT_PROBES:
        ticker = probe["ticker"]
        probe_date = datetime.strptime(probe["date"], "%Y-%m-%d").date()
        df = _load_ohlcv(ticker)
        actual_value = None
        if df is None:
            actual_value = "OHLCV_MISS"
        else:
            # Window: probe_date back 251 days for RSI warmup + probe_date
            window_start = probe_date
            window_end = probe_date
            try:
                bars = _precompute_signals_for_ticker(
                    df, ticker, window_start, window_end,
                    as_of_cache=as_of_cache,
                    enable_extended_signals=enable_extended_signals,
                )
            except Exception as exc:
                actual_value = f"EXCEPTION:{exc}"
                bars = []
            if bars:
                _, signals = bars[0]
                # Translate semantic signal name to producer key.
                # probe["signal"] is e.g. "rsi_14<35" -> we look up
                # 's.get("rsi_14")' and apply the condition.
                sig_query = probe["signal"]
                if "<" in sig_query:
                    name, thr = sig_query.split("<", 1)
                    name = name.strip()
                    thr_val = float(thr.strip())
                    val = signals.get(name)
                    actual_value = (val is not None) and (val < thr_val)
                elif ">" in sig_query:
                    name, thr = sig_query.split(">", 1)
                    name = name.strip()
                    thr_val = float(thr.strip())
                    val = signals.get(name)
                    actual_value = (val is not None) and (val > thr_val)
                else:
                    val = signals.get(sig_query)
                    actual_value = bool(val)
        results.append({
            "ticker": ticker,
            "date": probe["date"],
            "signal": probe["signal"],
            "expected": probe["expected"],
            "actual": actual_value,
            "passed": (actual_value == probe["expected"]),
            "note": probe.get("note", ""),
        })
    return results


def run_audit(
    max_tickers: Optional[int],
    start: date,
    end: date,
    enable_extended_signals: bool = True,
    skip_known_event_probes: bool = False,
) -> dict:
    """Main entry: orchestrate the 4-axis audit + KNOWN-EVENT probes."""
    t0 = time.time()

    # Axis 0: declared signals inventory
    declared = _gather_declared_signals(CLUSTER_A_STRATEGIES)
    logger.info("Declared signals across Cluster A: %d unique", len(declared))

    # Axis (a) + (b): path + glob (trivially: technical.py is the source)
    # Captured via meta.

    # Resolve T1a universe
    tickers_full = _load_t1a_tickers_union_over_window(start, end)
    if max_tickers is not None and max_tickers > 0:
        tickers = tickers_full[:max_tickers]
    else:
        tickers = tickers_full
    logger.info(
        "Probing %d / %d T1a tickers over [%s, %s]",
        len(tickers), len(tickers_full), start, end,
    )

    # Axis (c): temporal-coverage probe + signal coverage stats
    coverage, n_bars = _probe_producer_coverage(
        tickers, start, end, enable_extended_signals,
    )
    logger.info(
        "Coverage probe done: %d signals tracked across %d bars",
        len(coverage), n_bars,
    )

    # Axis (d): schema-contract -- declared-but-not-emitted detection
    pat_f = _detect_pattern_f_candidates(declared, coverage, len(tickers))
    logger.info("Pattern F-class candidates: %d", len(pat_f))

    # Axis (c) tighter: temporal-gap detection on declared signals
    gaps = _detect_temporal_gaps(coverage, declared)
    logger.info("Temporal-coverage gaps: %d", len(gaps))

    # Axis (e): KNOWN-EVENT runtime probes
    known_probes: list[dict] = []
    if not skip_known_event_probes:
        known_probes = _run_known_event_probes(enable_extended_signals)
        passes = sum(1 for p in known_probes if p["passed"])
        logger.info(
            "KNOWN-EVENT probes: %d / %d passed",
            passes, len(known_probes),
        )

    runtime = round(time.time() - t0, 1)

    return {
        "meta": {
            "as_of_run": datetime.now().isoformat(),
            "n_tickers_probed": len(tickers),
            "n_tickers_universe": len(tickers_full),
            "date_range": {"start": str(start), "end": str(end)},
            "n_cluster_a_strategies": len(CLUSTER_A_STRATEGIES),
            "n_unique_signals_declared": len(declared),
            "n_signals_observed": len(coverage),
            "n_bars_total": n_bars,
            "runtime_seconds": runtime,
            "enable_extended_signals": enable_extended_signals,
            "axes_audited": {
                "a_path_from_source": "technical.py (compute_all_signals dispatcher)",
                "b_recursive_glob": "n/a (single-file producer set)",
                "c_temporal_coverage": "per-year emission rate; threshold 0.1%",
                "d_schema_contract": "declared signals_used vs emitted dict",
                "e_known_event_runtime": (
                    f"{len(KNOWN_EVENT_PROBES)} probes" if not skip_known_event_probes
                    else "SKIPPED"
                ),
                "f_investigate_why": "per-signal severity tagging in candidates",
            },
        },
        "declared_signals_inventory": {
            sig: {
                "n_strategies_using": len(strats),
                "strategies": strats,
            } for sig, strats in declared.items()
        },
        "signal_coverage": coverage,
        "pattern_f_candidates": pat_f,
        "temporal_gaps": gaps,
        "known_event_probes": known_probes,
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="CHECKLIST #106 producer-data audit on Cluster A "
                    "per S4-B755-COUNCIL-CHECKLIST-106-CLUSTER-A-PRODUCER-DATA-AUDIT",
    )
    p.add_argument("--smoke", action="store_true",
                   help="Smoke: 3 tickers x 1yr ~5min")
    p.add_argument("--demo", action="store_true",
                   help="Demo: 50 tickers x 2yr (2024-2025) ~30min")
    p.add_argument("--full", action="store_true",
                   help="Full: T1a window-union x 2020-2026 multi-hour")
    p.add_argument("--max-tickers", type=int, default=None)
    p.add_argument("--start", default="2020-01-01")
    p.add_argument("--end", default="2026-05-31")
    p.add_argument("--output", default=None,
                   help="Output JSON path (default output_audit/...)")
    p.add_argument("--disable-extended-signals", action="store_true")
    p.add_argument("--skip-known-event-probes", action="store_true")
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
        OUTPUT_DIR / f"checklist_106_cluster_a_producer_audit_{tag}.json"
    )

    logger.info("Audit mode=%s start=%s end=%s max_tickers=%s",
                tag, start, end, max_tickers)

    report = run_audit(
        max_tickers=max_tickers,
        start=start, end=end,
        enable_extended_signals=not args.disable_extended_signals,
        skip_known_event_probes=args.skip_known_event_probes,
    )
    out_path.write_text(json.dumps(report, indent=2, default=str))
    logger.info("Wrote audit report to %s", out_path)

    # Stdout summary
    meta = report["meta"]
    print(f"\n=== checklist_106_cluster_a_producer_audit {tag} complete ===")
    print(f"Tickers probed         : {meta['n_tickers_probed']}/{meta['n_tickers_universe']}")
    print(f"Bars total             : {meta['n_bars_total']:,}")
    print(f"Cluster A strategies   : {meta['n_cluster_a_strategies']}")
    print(f"Declared signals       : {meta['n_unique_signals_declared']}")
    print(f"Observed signals       : {meta['n_signals_observed']}")
    print(f"Pattern F candidates   : {len(report['pattern_f_candidates'])}")
    print(f"Temporal gaps          : {len(report['temporal_gaps'])}")
    if report["known_event_probes"]:
        passes = sum(1 for p in report["known_event_probes"] if p["passed"])
        print(f"KNOWN-EVENT probes     : {passes}/{len(report['known_event_probes'])} PASS")
    print(f"Runtime                : {meta['runtime_seconds']}s")
    print(f"Output                 : {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
