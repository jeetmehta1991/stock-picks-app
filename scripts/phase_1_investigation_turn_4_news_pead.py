#!/usr/bin/env python
"""Council 236 Investigation Turn 4 (2026-07-03) — NEWS_SENTIMENT + PEAD.

SCOPE: 4 strategies
  1. news_momentum_long (0 fires, HIGH)
  2. news_sentiment_long (16 fires, HIGH)
  3. pead_long (9 fires, HIGH)
  4. pead_short (30 fires, MED)

PRODUCER FILES REVIEWED:
  - news_sentiment.py (476 lines) - Polygon news vendor + rule-fallback
  - pead.py - quarterly EPS + PEAD window signals

CRITICAL FINDINGS:

FACT 1 - News producer VERIFIED WORKING (live test AAPL 2024-11-15):
  Emits 13 keys including: news_count_7d/5d, news_sentiment_score/5d,
  news_bullish_pct, news_bearish_pct, news_sentiment_shift, news_uses_
  polygon_score, news_volume_zscore_5d. All populated non-zero.

FACT 2 - B832 SPOF SENTINELS ALL TRIPPED DURING BATCH A:
  Batch A resume log 2026-07-01 shows all 3 SPOF thresholds breached:
    17:46:23 - 'Polygon-sentiment-absent (rule-fallback only) for 100 returns'
    17:47:05 - 'returned EMPTY for 50 consecutive calls'
    17:47:15 - 'zero-score for 30 returns despite article-count>0'
  This means for a significant portion of Batch A execution, news
  strategies received DEGRADED signal (rule-fallback OR empty OR zero).

FACT 3 - PEAD producer VERIFIED WORKING (live test 4 tickers 2024-11-15):
  BUG-288 was fixed Batch 312 (fiscal_year string vs int TypeError).
  Post-B312: pead_positive_surprise + pead_negative_surprise emit correctly.
  TSLA: pead_positive_surprise=True (YoY +16.98% + ann_return +26%)
  NVDA: pead_negative_surprise=True (YoY -73% + ann_return -8%)
  AAPL/MSFT: within_pead_window=False (>60d) or =True but no surprise.

FACT 4 - PEAD data cache is Polygon financials (quarterly EPS):
  Producer reads via load_quarterly_eps(ticker). Data-quality contingent
  on prefetch completeness. Tickers with missing EPS data return {}.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_4_INVESTIGATIONS = {
    "news_momentum_long": {
        "post_investigation_verdict": "PRODUCER_OK + B832_SPOF_TRIPPED + THRESHOLDS_TIGHT",
        "post_investigation_recommendation": (
            "Producer VERIFIED on live AAPL 2024-11-15: emits news_sentiment_5d (0.27), "
            "news_volume_zscore_5d (-0.48), news_count_5d (25), news_uses_polygon_score "
            "(True). All 13 keys populated non-zero. HOWEVER B832 SPOF SENTINELS ALL "
            "TRIPPED DURING BATCH A EXECUTION (17:46-17:47 log): 100 rule-fallback + "
            "50 empty + 30 zero-score returns. Producer works when data present but "
            "significant DATA QUALITY DEGRADATION during Batch A. Combined with 7-gate "
            "stack (sentiment >= +0.5 + zscore >= +1.5 + Donchian breakout + strong "
            "close + range + volume + AVWAP), 0 fires is explained by BOTH factors. "
            "ACTIONS: (1) URGENT - audit data_prefetch/polygon/news/ coverage for "
            "Batch A tickers; likely missing/stale parquets for many T1a names; "
            "(2) LOOSEN sentiment threshold >= +0.5 -> >= +0.3, zscore >= +1.5 -> "
            ">= +1.0; (3) drop AVWAP redundancy per feedback_avwap_redundant. Expected "
            "5-10x uplift when data + thresholds fixed."
        ),
    },
    "news_sentiment_long": {
        "post_investigation_verdict": "PRODUCER_OK + B832_SPOF_TRIPPED + B278_B314_HISTORY",
        "post_investigation_recommendation": (
            "Producer VERIFIED (same as news_momentum). Producer emits news_sentiment_"
            "mean and news_article_count. B278 tightening (mean 0.3->0.5, count 3->5) "
            "reduced Phase 1A-beta fire rate to ZERO. B314 loosening (removed momentum "
            "AND clause, count 5->3, retained mean 0.5) restored some fires; 16 fires "
            "post-B314. B832 SPOF sentinels tripped during Batch A adds data-quality "
            "layer on top of gate-tightness. ACTIONS: (1) audit data_prefetch/polygon/"
            "news/ coverage; (2) LOOSEN sentiment mean threshold 0.5 -> 0.3 (Lopez-"
            "Lira-Tang 2023 canonical uses lower); (3) verify news_uses_polygon_score "
            "distribution across Batch A - if rule-fallback dominates, scores may be "
            "systematically shifted. Expected 3-5x uplift."
        ),
    },
    "pead_long": {
        "post_investigation_verdict": "PRODUCER_OK + STRICT_ANN_RETURN_THRESHOLD",
        "post_investigation_recommendation": (
            "Producer VERIFIED on live test (TSLA 2024-11-15: pead_positive_surprise="
            "True, YoY +16.98%, ann_return +26%). BUG-288 fixed B312 (fiscal_year type "
            "mismatch). Producer correctly emits within_pead_window + surprise flags. "
            "Consumer gate: within_pead_window + pead_positive_surprise + ann_return "
            ">= +2%. 9 fires reflects strict thresholds on top of quarterly earnings "
            "event rarity. Structural rate: 4 earnings/yr per ticker x 25-40% positive "
            "surprise x >+2% ann_return ~= 1-2 fires/yr per ticker = 150 x 4y x "
            "1.5/yr = 900 max expected pre-window. Actual 9 = 100x underfire. Likely "
            "cause: >+2% ann-day return threshold catches only top-decile surprises. "
            "ACTIONS: (1) LOOSEN ann_return threshold >= +2% -> >= +1% (Garfinkel 2024 "
            "canonical uses lower); (2) audit polygon/financials coverage for Batch A "
            "tickers (missing EPS = no PEAD signal). Expected 3-5x uplift."
        ),
    },
    "pead_short": {
        "post_investigation_verdict": "PRODUCER_OK + MARGINAL_BOUNDARY + PATTERN_S",
        "post_investigation_recommendation": (
            "Producer VERIFIED on live test (NVDA 2024-11-15: pead_negative_surprise="
            "True, YoY -72.98%, ann_return -8.35%). Consumer gate: within_pead_window "
            "+ pead_negative_surprise + borrow_ok. 30 fires at MARGINAL boundary (30 "
            "= min_trades_per_regime floor). Symmetric mirror of pead_long but LESS "
            "restrictive gate (no ann-return threshold on SHORT side per producer). "
            "Pattern S SHORT asymmetric expectancy caveat. ACTIONS: (1) STATUS QUO on "
            "gates (already lean 2-gate); (2) universe expansion primary lever - "
            "Batch B 1787 will lift proportionally (~4-5x expected); (3) Pattern S "
            "cube interpretation caveat retained."
        ),
    },
}


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    for col in ("post_investigation_verdict", "post_investigation_recommendation"):
        if col not in df.columns:
            df[col] = ""

    updated = 0
    for strat, data in TURN_4_INVESTIGATIONS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)
    print(f"Turn 4 investigation complete: {updated} strategies updated.")
    print()
    print("=== TURN 4 KEY FINDINGS ===")
    print("news_momentum_long (0f):     B832 SPOF all 3 thresholds tripped in Batch A")
    print("                              + strict 7-gate stack. Data audit URGENT.")
    print("news_sentiment_long (16f):   Same B832 + B278/B314 threshold history.")
    print("pead_long (9f):              Producer verified (TSLA pead_positive_surprise")
    print("                              True); >=+2% ann_return threshold catches only")
    print("                              top-decile. Loosen to +1% per Garfinkel 2024.")
    print("pead_short (30f):            Producer verified (NVDA pead_negative_surprise")
    print("                              True); at MARGINAL boundary; universe expansion.")
    print()
    print("ACTION ITEM for BATCH B PRE-LAUNCH:")
    print("  Audit data_prefetch/polygon/news/ + data_prefetch/polygon/financials/")
    print("  coverage across T1a universe. B832 SPOF tripped = degraded signal quality.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
