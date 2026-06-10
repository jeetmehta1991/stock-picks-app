"""measure_survivorship_sensitivity.py -- Batch 666 (2026-06-09) per
SURVIVORSHIP_VERIFICATION_METHODOLOGY.md.

Per-strategy survivorship sensitivity audit. For each strategy, runs the
3-mode comparison (SURVIVOR_ONLY / DELISTED_ONLY / FULL) against T1a
universe + computes per-mode aggregate metrics + survivor sensitivity diff.

NOT EXECUTED by default in B666 (ships as ready-to-run scaffold per
methodology doc's "wait for B660 first" recommendation). Owner approval
required to execute.

Usage:
  python scripts/measure_survivorship_sensitivity.py \
      --strategies pivot_s3_capitulation pivot_r3_blowoff_short \
      --start 2020-01-01 --end 2026-05-31 \
      --output output_audit/survivorship_sensitivity_w5_w5m.json

Per `feedback_no_rushing_per_strategy_tweak`: surface harness, WAIT for
owner approval before execution.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from backtest.signals.screener import ALL_STRATEGIES  # noqa: E402

logger = logging.getLogger(__name__)

T1A_CSV_PATH = (
    REPO_ROOT / "Backtesting universe" /
    "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"
)
OHLCV_DIR = REPO_ROOT / "data_prefetch" / "polygon" / "ohlcv_daily"


@dataclass
class PerModeMetrics:
    mode: str
    n_tickers: int
    n_fires: int = 0
    sum_return_atr_trail: float = 0.0
    sum_return_20bar: float = 0.0
    n_hits: int = 0
    sum_mae: float = 0.0
    sum_mfe: float = 0.0
    n_blow_ups: int = 0

    def to_dict(self) -> dict:
        d = asdict(self)
        if self.n_fires > 0:
            d["mean_return_atr_trail"] = self.sum_return_atr_trail / self.n_fires
            d["mean_return_20bar"] = self.sum_return_20bar / self.n_fires
            d["hit_rate"] = self.n_hits / self.n_fires
            d["mean_mae"] = self.sum_mae / self.n_fires
            d["mean_mfe"] = self.sum_mfe / self.n_fires
            d["blow_up_rate"] = self.n_blow_ups / self.n_fires
        return d


@dataclass
class SurvivorSensitivity:
    return_inflation_pp: float = 0.0
    hit_rate_inflation_pp: float = 0.0
    blow_up_rate_hidden_pp: float = 0.0
    verdict: str = "indeterminate"


@dataclass
class StrategyResult:
    strategy: str
    by_mode: dict = field(default_factory=dict)
    survivor_sensitivity: SurvivorSensitivity = field(default_factory=SurvivorSensitivity)

    def compute_sensitivity(self) -> None:
        s = self.by_mode.get("survivor_only")
        f = self.by_mode.get("full")
        if s is None or f is None:
            return
        s_dict = s.to_dict() if isinstance(s, PerModeMetrics) else s
        f_dict = f.to_dict() if isinstance(f, PerModeMetrics) else f
        if s_dict.get("n_fires", 0) == 0 or f_dict.get("n_fires", 0) == 0:
            return
        self.survivor_sensitivity.return_inflation_pp = (
            (s_dict.get("mean_return_atr_trail", 0) - f_dict.get("mean_return_atr_trail", 0))
            * 100
        )
        self.survivor_sensitivity.hit_rate_inflation_pp = (
            (s_dict.get("hit_rate", 0) - f_dict.get("hit_rate", 0)) * 100
        )
        self.survivor_sensitivity.blow_up_rate_hidden_pp = (
            (f_dict.get("blow_up_rate", 0) - s_dict.get("blow_up_rate", 0)) * 100
        )
        infl = abs(self.survivor_sensitivity.return_inflation_pp)
        if infl < 0.5:
            self.survivor_sensitivity.verdict = "robust"
        elif infl < 2.0:
            self.survivor_sensitivity.verdict = "moderate sensitivity"
        else:
            self.survivor_sensitivity.verdict = "high sensitivity"


def _load_t1a_with_lifecycle() -> pd.DataFrame:
    """Load T1a CSV with added_date + removed_date columns.

    Uses csv.reader to handle embedded commas in company names (e.g.
    "Acme Real Estate, Inc."). Comment lines start with `#` and are
    skipped before passing to csv.reader.
    """
    import csv
    rows = []
    with open(T1A_CSV_PATH, encoding="utf-8") as f:
        data_lines = [ln for ln in f if ln.strip() and not ln.startswith("#")]
    reader = csv.reader(data_lines)
    header = next(reader, None)
    for parts in reader:
        if len(parts) < 5:
            continue
        symbol, company, sector, added_date, removed_date = (
            parts[0], parts[1], parts[2], parts[3], parts[4]
        )
        rows.append({
            "Symbol": symbol.strip(),
            "Company": company.strip(),
            "Sector": sector.strip(),
            "added_date": pd.to_datetime(added_date.strip()) if added_date.strip() else pd.NaT,
            "removed_date": pd.to_datetime(removed_date.strip()) if removed_date.strip() else pd.NaT,
        })
    return pd.DataFrame(rows)


def _resolve_universe_modes(
    as_of: date,
    window_start: date,
    window_end: date,
) -> dict[str, list[str]]:
    """Return dict of {mode_name: ticker_list} for survivor_only, delisted_only, full."""
    df = _load_t1a_with_lifecycle()
    survivor_only = sorted(df[df["removed_date"].isna()]["Symbol"].tolist())
    delisted_mask = (
        df["removed_date"].notna()
        & (df["removed_date"] >= pd.Timestamp(window_start))
        & (df["removed_date"] <= pd.Timestamp(window_end))
    )
    delisted_only = sorted(df[delisted_mask]["Symbol"].tolist())
    full = sorted(set(survivor_only) | set(delisted_only))
    return {
        "survivor_only": survivor_only,
        "delisted_only": delisted_only,
        "full": full,
    }


def _load_ohlcv(ticker: str) -> Optional[pd.DataFrame]:
    """Load OHLCV parquet for ticker. Returns None if missing."""
    path = OHLCV_DIR / f"{ticker}.parquet"
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(path)
        return df if not df.empty else None
    except Exception as exc:
        logger.warning("OHLCV load failed for %s: %s", ticker, exc)
        return None


def _measure_strategy_in_mode(
    strategy_name: str,
    tickers: list[str],
    start: date,
    end: date,
    mode_name: str,
) -> PerModeMetrics:
    """SCAFFOLD: per-strategy measurement against ticker list.

    NOT IMPLEMENTED in B666 -- this is the harness scaffold that compiles
    and runs to completion (returning all-zero metrics) but does not yet
    perform the actual fire-detection + forward-return computation.

    To execute the actual measurement, the body of this function needs:
      1. For each ticker, load OHLCV + run compute_all_signals at each bar
      2. Call ALL_STRATEGIES[strategy_name] at each bar; record fire bars
      3. For each fire bar: compute return_1bar / return_5bar / return_20bar /
         return_atr_trail / max_mae / max_mfe / delisted_within_6mo /
         squeezed_within_6mo
      4. Aggregate per-mode metrics

    The full implementation depends on a more general fire+forward-return
    measurement framework that is queued for the post-B660 batch. This
    scaffold is the design framing per SURVIVORSHIP_VERIFICATION_METHODOLOGY
    .md; the implementation ships when owner approves the 4 open
    methodology questions in that doc.
    """
    logger.info(
        "[%s / %s] SCAFFOLD: would measure %d tickers from %s to %s "
        "(implementation deferred to post-B660 batch per owner-approved "
        "foundational re-prioritization commitment)",
        strategy_name, mode_name, len(tickers), start, end,
    )
    # Count tickers with OHLCV available -- this part DOES work
    n_with_data = sum(1 for t in tickers if (OHLCV_DIR / f"{t}.parquet").exists())
    return PerModeMetrics(
        mode=mode_name,
        n_tickers=n_with_data,
        # All fire-detection + return metrics zero in scaffold
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strategies", nargs="+",
        help="Strategy names to audit (registry keys)",
    )
    parser.add_argument(
        "--exploratory-only", action="store_true",
        help="Audit only EXPLORATORY strategies (currently W5 + W5m)",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Audit all registered strategies (long-running)",
    )
    parser.add_argument(
        "--start", default="2020-01-01",
        help="Window start (default 2020-01-01)",
    )
    parser.add_argument(
        "--end", default="2026-05-31",
        help="Window end (default 2026-05-31)",
    )
    parser.add_argument(
        "--modes", nargs="+",
        default=["survivor_only", "delisted_only", "full"],
        help="Universe modes to compare (default all 3)",
    )
    parser.add_argument(
        "--output", default=None,
        help="Output JSON path (default: output_audit/survivorship_sensitivity_<DATE>.json)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Verbose logging",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if not args.verbose else logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    if args.exploratory_only:
        strategy_names = ["pivot_s3_capitulation", "pivot_r3_blowoff_short"]
    elif args.all:
        strategy_names = sorted(ALL_STRATEGIES.keys())
    elif args.strategies:
        strategy_names = args.strategies
    else:
        print(
            "Specify --strategies <names>, --exploratory-only, or --all",
            file=sys.stderr,
        )
        return 2

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)

    universes = _resolve_universe_modes(end, start, end)
    logger.info(
        "Universe modes: survivor_only=%d, delisted_only=%d, full=%d",
        len(universes["survivor_only"]),
        len(universes["delisted_only"]),
        len(universes["full"]),
    )

    results: list[StrategyResult] = []
    for strat_name in strategy_names:
        if strat_name not in ALL_STRATEGIES:
            logger.warning("Strategy %s not in ALL_STRATEGIES; skipping", strat_name)
            continue
        result = StrategyResult(strategy=strat_name)
        for mode in args.modes:
            if mode not in universes:
                logger.warning("Unknown mode %s; skipping", mode)
                continue
            result.by_mode[mode] = _measure_strategy_in_mode(
                strat_name, universes[mode], start, end, mode,
            )
        result.compute_sensitivity()
        results.append(result)

    output = {
        "as_of": end.isoformat(),
        "window": {"start": start.isoformat(), "end": end.isoformat()},
        "modes": {
            mode: {
                "n_tickers": len(tickers),
                "definition": _mode_definition(mode),
            }
            for mode, tickers in universes.items()
            if mode in args.modes
        },
        "strategies": {
            r.strategy: {
                "by_mode": {m: v.to_dict() for m, v in r.by_mode.items()},
                "survivor_sensitivity": asdict(r.survivor_sensitivity),
            }
            for r in results
        },
        "scaffold_note": (
            "B666 scaffold: per-strategy fire+return measurement deferred "
            "to post-B660 batch per SURVIVORSHIP_VERIFICATION_METHODOLOGY"
            ".md. Only n_tickers counts are populated; metrics are zero."
        ),
    }

    out_path = args.output or (
        REPO_ROOT / "output_audit" / f"survivorship_sensitivity_{end}.json"
    )
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    logger.info("Wrote %s", out_path)
    return 0


def _mode_definition(mode: str) -> str:
    return {
        "survivor_only": "T1a active at as_of (removed_date IS NULL)",
        "delisted_only": "T1a removed during window (removed_date BETWEEN start AND end)",
        "full": "SURVIVOR_ONLY UNION DELISTED_ONLY with PIT filter applied per-bar",
    }.get(mode, "unknown mode")


if __name__ == "__main__":
    sys.exit(main())
