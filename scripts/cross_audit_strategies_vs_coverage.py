"""B1217 Council 282: Cross-audit 219 strategies against Council 281 producer
coverage findings.

For each strategy, identify:
  - Producer dependencies (via signal-name grep of function body)
  - Coverage impact from output_audit/*_coverage_batch_a.json
  - Classification: BLOCKED_UPSTREAM / COVERAGE_LIMITED / UNAFFECTED

Output: output_audit/strategy_vs_producer_coverage_matrix.json + summary stdout.
"""
# Source: per CHECKLIST #77 canonical-source; Council 282 B1217 2026-07-07
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


# Map coverage-audited producers to signal names they emit
PRODUCER_SIGNALS = {
    "news_sentiment": {
        "signals": [
            "news_sentiment_5d", "news_sentiment_mean", "news_sentiment_shift",
            "news_sentiment_score", "news_article_count", "news_count_5d",
            "news_volume_zscore_5d",
        ],
        "effective_pct": 84.2,
        "zero_pct": 15.8,
        "coverage_file": "news_coverage_batch_a.json",
    },
    "short_interest_dtc": {
        "signals": ["days_to_cover"],
        "effective_pct": 97.7,
        "zero_pct": 2.3,
        "coverage_file": "short_interest_coverage_batch_a.json",
    },
    "short_interest_pct": {
        # SPECIAL: producer emits days_to_cover but NEVER emits short_interest_pct
        # (shares_outstanding NULL in FINRA cache per B1214 finding)
        "signals": ["short_interest_pct"],
        "effective_pct": 0.0,
        "zero_pct": 100.0,
        "coverage_file": "short_interest_coverage_batch_a.json",
        "note": "B1214 critical: short_interest_pct NEVER emitted",
    },
    "pead": {
        "signals": [
            "within_pead_window", "pead_positive_surprise",
            "pead_negative_surprise", "days_since_last_earnings",
            "yoy_earnings_growth", "announcement_return",
        ],
        "effective_pct": 85.0,
        "zero_pct": 15.0,
        "coverage_file": "pead_coverage_batch_a.json",
    },
    "insider": {
        "signals": [
            "insider_cluster_active", "insider_unique_buyers_30d",
            "insider_total_shares_bought_30d", "insider_director_buyers_30d",
            "insider_officer_buyers_30d",
        ],
        "effective_pct": 18.8,
        "zero_pct": 81.2,
        "coverage_file": "insider_coverage_batch_a.json",
        "note": "Partly event-rarity (Form 4 filings sporadic)",
    },
    "institutional": {
        "signals": [
            "institutional_buy", "institutional_increased",
            "institutional_new_positions", "institutional_persistence_growing",
            "institutional_persistence_positive_30d",
            "committed_growth_holders", "institutional_recent_init",
        ],
        "effective_pct": 30.1,
        "zero_pct": 69.9,
        "coverage_file": "institutional_coverage_batch_a.json",
        "note": "Data source gap (constant across dates)",
    },
}


def main() -> int:
    with open(_REPO / "backtest" / "signals" / "screener.py") as f:
        src = f.read()

    csv_path = _REPO / "output_batch_A_150" / "phase_1_quiet_fire_investigation.csv"
    df = pd.read_csv(csv_path)

    strategies = df["strategy_name"].tolist()
    print(f"Cross-auditing {len(strategies)} strategies vs 6 producer coverage findings")

    strategy_impact = {}
    stats = {
        "BLOCKED_UPSTREAM_SHORT_INTEREST_PCT": 0,
        "COVERAGE_LIMITED_INSTITUTIONAL": 0,
        "COVERAGE_LIMITED_INSIDER": 0,
        "COVERAGE_LIMITED_NEWS": 0,
        "COVERAGE_LIMITED_PEAD": 0,
        "UNAFFECTED": 0,
    }

    for strat in strategies:
        # Find strategy function body
        idx = src.find(f"def strat_{strat}(")
        if idx < 0:
            strategy_impact[strat] = {"classification": "NOT_FOUND", "producers": []}
            continue
        end = src.find("\ndef ", idx + 30)
        body = src[idx:end] if end > 0 else src[idx:]

        # Grep signals in body
        signals_used = set(re.findall(r's\.get\(\s*["\']([a-z_0-9]+)["\']', body))

        # Map signals to producers
        producers_hit = {}
        for producer, meta in PRODUCER_SIGNALS.items():
            matched = signals_used & set(meta["signals"])
            if matched:
                producers_hit[producer] = {
                    "signals_matched": sorted(matched),
                    "effective_pct": meta["effective_pct"],
                    "zero_pct": meta["zero_pct"],
                    "note": meta.get("note", ""),
                }

        # Classify
        if not producers_hit:
            classification = "UNAFFECTED"
        elif "short_interest_pct" in producers_hit:
            classification = "BLOCKED_UPSTREAM_SHORT_INTEREST_PCT"
        elif "institutional" in producers_hit and producers_hit["institutional"]["effective_pct"] < 50:
            classification = "COVERAGE_LIMITED_INSTITUTIONAL"
        elif "insider" in producers_hit:
            classification = "COVERAGE_LIMITED_INSIDER"
        elif "news_sentiment" in producers_hit:
            classification = "COVERAGE_LIMITED_NEWS"
        elif "pead" in producers_hit:
            classification = "COVERAGE_LIMITED_PEAD"
        else:
            classification = "UNAFFECTED"

        strategy_impact[strat] = {
            "classification": classification,
            "producers_hit": producers_hit,
        }
        stats[classification] = stats.get(classification, 0) + 1

    print("\n=== IMPACT DISTRIBUTION ===")
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        pct = 100 * v / len(strategies)
        print(f"  {k}: {v} ({pct:.1f}%)")

    # Show BLOCKED strategies specifically
    blocked = [s for s, r in strategy_impact.items()
               if r["classification"] == "BLOCKED_UPSTREAM_SHORT_INTEREST_PCT"]
    print(f"\n=== BLOCKED_UPSTREAM_SHORT_INTEREST_PCT (effectively unfireable): {len(blocked)} ===")
    for s in blocked:
        print(f"  {s}")

    # Show COVERAGE_LIMITED_INSTITUTIONAL
    inst_limited = [s for s, r in strategy_impact.items()
                    if r["classification"] == "COVERAGE_LIMITED_INSTITUTIONAL"]
    print(f"\n=== COVERAGE_LIMITED_INSTITUTIONAL (fire on ~30% of Batch A): {len(inst_limited)} ===")
    for s in inst_limited[:20]:
        print(f"  {s}")

    output_path = _REPO / "output_audit" / "strategy_vs_producer_coverage_matrix.json"
    output = {
        "batch": "B1217",
        "council": 282,
        "measurement_date": "2026-07-07",
        "universe_size_strategies": len(strategies),
        "producer_findings": PRODUCER_SIGNALS,
        "impact_stats": stats,
        "strategy_impact": strategy_impact,
    }
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nCanonical output: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
