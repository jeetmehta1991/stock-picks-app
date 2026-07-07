"""B1214 Council 281 CHECKLIST #154 retroactive audit: generic producer
coverage measurement. Handles short_interest / PEAD / insider / institutional
producers with same methodology as B1211 news_sentiment audit.

Usage:
  python scripts/measure_producer_coverage.py <producer>

Where <producer> is one of:
  short_interest    (compute_short_interest_signals -> short_interest_pct, days_to_cover)
  pead              (compute_pead_signals -> within_pead_window, pead_positive_surprise)
  insider           (compute_insider_cluster_signals -> insider_cluster_active, unique/director_buyers_30d)
  institutional     (compute_institutional_persistence -> institutional_buy, new_positions, etc.)

Output: output_audit/<producer>_coverage_batch_a.json
"""
# Source: per CHECKLIST #77 canonical-source; Council 281 B1214 2026-07-07
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TEST_DATES = [
    date(2024, 3, 15),
    date(2024, 6, 15),
    date(2024, 9, 15),
    date(2024, 12, 15),
]


PRODUCERS = {
    "short_interest": {
        "module": "backtest.signals.short_interest",
        "func": "compute_short_interest_signals",
        "primary_signal": "days_to_cover",  # B1214: NOT short_interest_pct - producer emits only when shares_outstanding available (currently None in FINRA cache)
        "check": lambda r: (r.get("days_to_cover") is not None and r.get("days_to_cover") > 0),
    },
    "pead": {
        "module": "backtest.signals.pead",
        "func": "compute_pead_signals",
        "primary_signal": "within_pead_window",
        # PEAD coverage = has ANY earnings data (within_pead_window is bool but
        # populated from days_since_last_earnings which requires earnings data)
        "check": lambda r: (r.get("days_since_last_earnings", -1) >= 0),
        # B1215 (2026-07-07): pead requires ohlcv_df signature
        "needs_ohlcv": True,
    },
    "insider": {
        "module": "backtest.signals.insider_buying",
        "func": "compute_insider_cluster_signals",
        "primary_signal": "insider_cluster_active",
        # Insider coverage = producer returns non-empty dict
        "check": lambda r: bool(r) and "insider_unique_buyers_30d" in r,
    },
    "institutional": {
        "module": "backtest.signals.institutional_persistence_consumer",
        "func": "compute_persistence_signals",
        "primary_signal": "institutional_buy",
        "check": lambda r: bool(r) and any(k.startswith("institutional") for k in r),
    },
    "congressional": {
        "module": "backtest.signals.congressional_alt_data",
        "func": "compute_housetrading_signals",
        "primary_signal": "house_cluster_buy",
        # B1218 fix: producer emits house_* keys, not congressional_*
        "check": lambda r: bool(r) and any(k.startswith("house_") for k in r),
    },
    "sec_edgar": {
        "module": "backtest.signals.sec_edgar_extractor",
        "func": "compute_sec_edgar_signals",
        "primary_signal": "recent_8k_filed",
        "check": lambda r: bool(r),
    },
}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in PRODUCERS:
        print(f"Usage: {sys.argv[0]} <{'|'.join(PRODUCERS)}>")
        return 1

    producer_name = sys.argv[1]
    spec = PRODUCERS[producer_name]

    trade_log = _REPO / "output_batch_A_150" / "trade_log.csv"
    df = pd.read_csv(trade_log)
    tickers = sorted(df["ticker"].unique())
    print(f"Producer: {producer_name}")
    print(f"Batch A universe: {len(tickers)} unique tickers")

    # Import the producer function
    mod = __import__(spec["module"], fromlist=[spec["func"]])
    func = getattr(mod, spec["func"])

    per_ticker: dict[str, dict] = {}
    per_date: dict[str, dict] = {d.isoformat(): {"has_data": 0, "zero": 0, "error": 0} for d in TEST_DATES}

    needs_ohlcv = spec.get("needs_ohlcv", False)
    if needs_ohlcv:
        from pathlib import Path
        cache_dir = _REPO / "backtest" / "data" / "cache" / "ohlcv"

        def _load_ohlcv(t):
            p = cache_dir / f"{t}.parquet"
            if not p.exists():
                return None
            df = pd.read_parquet(p)
            df["date"] = pd.to_datetime(df["date"])
            return df.set_index("date").sort_index()

    for i, ticker in enumerate(tickers):
        if i % 20 == 0:
            print(f"  progress: {i}/{len(tickers)}...")
        per_ticker[ticker] = {"dates_with_data": 0, "dates_zero": 0, "errors": 0}
        ohlcv_df = _load_ohlcv(ticker) if needs_ohlcv else None
        for d in TEST_DATES:
            try:
                if needs_ohlcv:
                    if ohlcv_df is None:
                        raise ValueError("no ohlcv")
                    r = func(ticker, ohlcv_df, d)
                else:
                    r = func(ticker, d)
                if spec["check"](r):
                    per_ticker[ticker]["dates_with_data"] += 1
                    per_date[d.isoformat()]["has_data"] += 1
                else:
                    per_ticker[ticker]["dates_zero"] += 1
                    per_date[d.isoformat()]["zero"] += 1
            except Exception as e:
                per_ticker[ticker]["errors"] += 1
                per_date[d.isoformat()]["error"] += 1

    # Categorize
    always_covered = [t for t, r in per_ticker.items() if r["dates_with_data"] == len(TEST_DATES)]
    always_zero = [t for t, r in per_ticker.items() if r["dates_with_data"] == 0 and r["errors"] == 0]
    partial = [t for t in tickers if t not in always_covered and t not in always_zero]
    error_tickers = [t for t, r in per_ticker.items() if r["errors"] == len(TEST_DATES)]

    print(f"\n=== PER-TICKER COVERAGE ({producer_name}) ===")
    print(f"  ALWAYS_COVERED (4/4 dates): {len(always_covered)} ({100*len(always_covered)/len(tickers):.1f}%)")
    print(f"  PARTIAL (1-3/4 dates):      {len(partial)} ({100*len(partial)/len(tickers):.1f}%)")
    print(f"  ALWAYS_ZERO (0/4 dates):    {len(always_zero)} ({100*len(always_zero)/len(tickers):.1f}%)")
    print(f"  ALL_ERROR (4/4 errors):     {len(error_tickers)} ({100*len(error_tickers)/len(tickers):.1f}%)")

    print(f"\n=== PER-DATE COVERAGE ({producer_name}) ===")
    for d in TEST_DATES:
        r = per_date[d.isoformat()]
        pct_with = 100 * r["has_data"] / len(tickers)
        print(f"  {d.isoformat()}: {r['has_data']}/{len(tickers)} with data ({pct_with:.1f}%), "
              f"{r['zero']} zero, {r['error']} error")

    effective_pct = 100 * (len(always_covered) + len(partial)) / len(tickers)
    print(f"\n=== EFFECTIVE UNIVERSE FOR {producer_name} STRATEGIES ===")
    print(f"  Effective (any coverage): {len(always_covered) + len(partial)}/{len(tickers)} = {effective_pct:.1f}%")
    print(f"  Zero-coverage tickers: {len(always_zero)}")

    output_path = _REPO / "output_audit" / f"{producer_name}_coverage_batch_a.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "batch": "B1214",
        "council": 281,
        "producer": producer_name,
        "primary_signal": spec["primary_signal"],
        "measurement_date": "2026-07-07",
        "test_dates_2024": [d.isoformat() for d in TEST_DATES],
        "universe_size": len(tickers),
        "per_ticker_categories": {
            "always_covered": always_covered,
            "always_covered_count": len(always_covered),
            "partial_coverage": partial,
            "partial_coverage_count": len(partial),
            "always_zero": always_zero,
            "always_zero_count": len(always_zero),
            "all_error": error_tickers,
            "all_error_count": len(error_tickers),
        },
        "per_date_summary": per_date,
        "effective_universe_pct": round(effective_pct, 1),
        "zero_coverage_pct": round(100 * len(always_zero) / len(tickers), 1),
    }
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nCanonical output: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
