"""B1211 Council 280 Fix #11 follow-up: Full Batch A news coverage audit.

Per B1209 finding: 52% of 25-sample non-mega Batch A tickers had zero news
coverage. This script upgrades qualitative finding to quantitative measurement
across ALL Batch A tickers on multiple test dates for temporal robustness.

Output: output_audit/news_coverage_batch_a.json + summary stdout.

METHODOLOGY:
  1. Enumerate Batch A ticker universe from output_batch_A_150/trade_log.csv
  2. Sample 4 test dates across 2024 (quarterly for temporal robustness)
  3. Call compute_news_sentiment_signals per (ticker, date)
  4. Categorize: HAS_DATA (news_count_5d > 0), ZERO_COVERAGE (=0), ERROR
  5. Compute per-ticker AND per-date coverage rates
  6. Save canonical JSON output for future audits + downstream consumers
"""
# Source: per CHECKLIST #77 canonical-source; Council 280 B1211 2026-07-07
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


def main() -> int:
    trade_log = _REPO / "output_batch_A_150" / "trade_log.csv"
    if not trade_log.exists():
        print(f"ERROR: {trade_log} not found")
        return 1

    df = pd.read_csv(trade_log)
    tickers = sorted(df["ticker"].unique())
    print(f"Batch A universe: {len(tickers)} unique tickers")

    from backtest.signals.news_sentiment import compute_news_sentiment_signals

    # 4 quarterly test dates across 2024
    TEST_DATES = [
        date(2024, 3, 15),
        date(2024, 6, 15),
        date(2024, 9, 15),
        date(2024, 12, 15),
    ]

    per_ticker: dict[str, dict] = {}
    per_date: dict[str, dict] = {d.isoformat(): {"has_data": 0, "zero": 0, "error": 0} for d in TEST_DATES}

    for i, ticker in enumerate(tickers):
        if i % 10 == 0:
            print(f"  progress: {i}/{len(tickers)}...")
        per_ticker[ticker] = {"dates_with_data": 0, "dates_zero": 0, "errors": 0}
        for d in TEST_DATES:
            try:
                r = compute_news_sentiment_signals(ticker, d)
                cnt = r.get("news_count_5d", 0)
                if cnt > 0:
                    per_ticker[ticker]["dates_with_data"] += 1
                    per_date[d.isoformat()]["has_data"] += 1
                else:
                    per_ticker[ticker]["dates_zero"] += 1
                    per_date[d.isoformat()]["zero"] += 1
            except Exception:
                per_ticker[ticker]["errors"] += 1
                per_date[d.isoformat()]["error"] += 1

    # Categorize tickers
    always_covered = [t for t, r in per_ticker.items() if r["dates_with_data"] == len(TEST_DATES)]
    always_zero = [t for t, r in per_ticker.items() if r["dates_with_data"] == 0 and r["errors"] == 0]
    partial = [t for t in tickers if t not in always_covered and t not in always_zero]

    print(f"\n=== PER-TICKER COVERAGE ===")
    print(f"  ALWAYS_COVERED (4/4 dates): {len(always_covered)} ({100*len(always_covered)/len(tickers):.1f}%)")
    print(f"  PARTIAL (1-3/4 dates):      {len(partial)} ({100*len(partial)/len(tickers):.1f}%)")
    print(f"  ALWAYS_ZERO (0/4 dates):    {len(always_zero)} ({100*len(always_zero)/len(tickers):.1f}%)")

    print(f"\n=== PER-DATE COVERAGE ===")
    for d in TEST_DATES:
        r = per_date[d.isoformat()]
        pct_with = 100 * r["has_data"] / len(tickers)
        print(f"  {d.isoformat()}: {r['has_data']}/{len(tickers)} with data ({pct_with:.1f}%), "
              f"{r['zero']} zero, {r['error']} error")

    # Effective universe = ALWAYS_COVERED + PARTIAL (any date has data)
    effective_pct = 100 * (len(always_covered) + len(partial)) / len(tickers)
    print(f"\n=== EFFECTIVE UNIVERSE FOR NEWS STRATEGIES ===")
    print(f"  Effective (any coverage): {len(always_covered) + len(partial)}/{len(tickers)} = {effective_pct:.1f}%")
    print(f"  Zero-coverage tickers (news strategies will never fire): {len(always_zero)}")

    # Save canonical output
    output_path = _REPO / "output_audit" / "news_coverage_batch_a.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "batch": "B1211",
        "council": 280,
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
        },
        "per_date_summary": per_date,
        "effective_universe_pct": round(effective_pct, 1),
        "zero_coverage_pct": round(100 * len(always_zero) / len(tickers), 1),
        "affected_strategies": [
            "news_momentum_short",
            "news_reversal_long",
            "news_reversal_short",
            "news_sentiment_long",
            "news_sentiment_shift_long",
            "news_momentum_long",
            "pead_with_insider_confirmation_long",
        ],
        "recommendation": (
            "News strategies effective universe is only "
            f"{effective_pct:.1f}% of Batch A. Fire-count expectations should be "
            "recalibrated. Consider secondary news source (Finnhub/AlphaVantage) "
            "for zero-coverage tickers via Sprint 5 ticket."
        ),
    }
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nCanonical output saved: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
