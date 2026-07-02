#!/usr/bin/env python
"""Phase 1 deep-dive analysis TURN 9 (Council 235 owner-approved 2026-07-02).

Turn 9 scope: STARVED strategies 61-75 by fire count (7-4 fires).
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_9_ANALYSIS = {
    "xs_momentum_with_smart_money_long": {
        "cluster_id": "SMART_MONEY_SLEEVE_FAMILY",
        "owner_review_notes": (
            "7 fires. Base J-T 12-1 top-decile momentum + EMA200 + _has_smart_money_buy "
            "union. Same 3-way scarce pattern as other smart_money_sleeve strategies "
            "(macd/mfi/rsi/donchian/bollinger/squeeze/xs_low_beta all in family). "
            "STATE 13F miscredit for smart_money leg."
        ),
        "recommendation": (
            "Same pattern as smart_money_sleeve family: LOOSEN smart_money to EVENT-only "
            "(insider + cfo + large_dollar; drop STATE 13F) per feedback_signal_"
            "temporality. Or ablate smart_money entirely to isolate pure momentum "
            "top-decile contribution. Expected fire uplift 2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "donchian_breakdown_retest_short": {
        "cluster_id": "BREAK_RETEST_FAMILY",
        "owner_review_notes": (
            "6 fires. Batch 592 restored 3-gate + Batch 596 walk symmetry additions "
            "(close_below_open + close_in_bottom_40pct_of_range). Root cause: Donchian "
            "breakdown is EVENT; retest is a second rare event. Compound = doubly rare. "
            "Pattern S SHORT asymmetric expectancy caveat + retest inherently reduces "
            "fires vs base breakdown."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify donchian retest signal fires post-breakdown. "
            "If producer OK, retest strategies are structurally rare; accept as design. "
            "Producer-side widening (retest window 5d -> 10d) may help. Pattern S caveat."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "donchian_breakdown_short": {
        "cluster_id": "DONCHIAN_FAMILY",
        "owner_review_notes": (
            "6 fires. Batch 592 restore + B595 symmetry (long/short parity with "
            "donchian_breakout_long). Tight Donchian-10 breakdown + 1.5x vol + MACD "
            "bearish. Root cause: 3-gate compound - DC10 breakdown (~10/yr per ticker) "
            "+ vol_spike_15x (fire-starving) + MACD_bearish STATE. Same vol_spike_15x "
            "pattern flagged 13x."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_15x -> vol_spike_2x (recurring high-value fix). Expected "
            "fire uplift 3-5x. Retain DC10 + MACD_bearish + borrow. Pattern S caveat."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "golden_cross_20_50": {
        "cluster_id": "GOLDEN_DEATH_CROSS_FAMILY",
        "owner_review_notes": (
            "6 fires. Dual: LONG = ema_20_50_golden_cross + price_above_ema_200; SHORT "
            "= symmetric. B630 positive-symmetric below_ema_200 sweep. Root cause: "
            "EMA 20/50 crosses are more frequent than 50/200 (~5-10/yr per ticker vs "
            "1-2/yr for 50/200) BUT the 200-EMA regime gate filters most crosses to "
            "trend-aligned only. 6 fires suggests either producer under-firing OR 200-"
            "EMA gate too restrictive."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify ema_20_50_golden_cross populates on canonical "
            "cases. If OK, consider DROPPING 200-EMA regime gate (EMA 20/50 cross itself "
            "IS a trend signal - redundant with longer-EMA confirmation per feedback_"
            "avwap_redundant precedent). Expected fire uplift 3-5x."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "pre_holiday_long": {
        "cluster_id": "EVENT_DRIVEN_MACRO_FAMILY",
        "owner_review_notes": (
            "6 fires. Batch 254 Lakonishok-Smidt 1988 + Ariel 1990 pre-holiday drift. "
            "STATUS: EXPLORATORY POST-B830 PATTERN AA - event-strategy structurally-"
            "limited effective-N. DO NOT DEPLOY marker. Pre-holiday days are ~10-15/yr "
            "(US holidays); base rate matches 6 fires reasonably."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_pre_holiday_wider_long: expand pre-holiday window from d-1 to d-3 "
            "(3 days pre-holiday). Lakonishok-Smidt 1988 documented full pre-holiday "
            "week alpha. Preserves seasonal thesis with 3x fire uplift potential."
        ),
    },
    "prev_day_low_breakdown": {
        "cluster_id": "PRICE_ACTION_FAMILY",
        "owner_review_notes": (
            "6 fires. 3-gate: below_prev_low + vol_spike_15x + below_vwap + borrow. "
            "B634 positive-symmetric below_vwap sweep. Same vol_spike_15x recurring "
            "fire-starving pattern. Universe-agnostic breakdown. Pattern S SHORT "
            "asymmetric expectancy caveat."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_15x -> vol_spike_2x. Expected fire uplift 3-5x. Same "
            "pattern as prev_day_high_break (Turn 5 HIGH), roc_burst (Turn 7 HIGH), "
            "volume_spike_breakout (Turn 7 HIGH), doji_at_resistance (Turn 8 HIGH), "
            "donchian_breakdown (this turn HIGH)."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "stoch_oversold": {
        "cluster_id": "OSCILLATOR_CONFLUENCE_FAMILY",
        "owner_review_notes": (
            "6 fires. Dual: LONG = %K < 20 + K crosses D bullish + above_ema_20; "
            "SHORT = symmetric + borrow. Batch 627 F1 sweep for positive symmetric "
            "below_ema_20. Root cause: %K < 20 + K-D cross event compound - both are "
            "specific conditions. Universe-agnostic mean-reversion."
        ),
        "recommendation": (
            "LOOSEN: Stochastic %K threshold 20 -> 25 (broader oversold; still meaningful "
            "vs neutral 50). Retain K-D cross + EMA-20 trend. Expected fire uplift 2-3x. "
            "Pattern S SHORT asymmetric caveat."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "supertrend_macd": {
        "cluster_id": "TREND_CONFLUENCE_FAMILY",
        "owner_review_notes": (
            "6 fires. Batch 655 EVENT-anchored redesign: supertrend_flip_recent_long_5d "
            "+ macd_12_26_9_bullish + adx > 20. Pre-B655: 3 STATE gates (supertrend_"
            "bullish + MACD_bullish + adx). Post-B655: EVENT supertrend flip + STATE "
            "confirmations. Same B655 T10 pattern as supertrend_ichimoku_adx (Turn 4)."
        ),
        "recommendation": (
            "STATUS QUO on B655 EVENT conversion (empirically justified). 5-day flip "
            "window is deliberate; loose variant could 10-day window per Turn 4 "
            "supertrend_ichimoku recommendation. Universe-agnostic pattern."
        ),
        "priority": "MED",
        "exploratory_loose_variant": (
            "strat_supertrend_macd_wider: expand EVENT window from 5-day to 10-day recent "
            "supertrend flip. Preserves EVENT-alpha distinction. Expected fire uplift "
            "3-5x. Symmetric to supertrend_ichimoku_adx wider variant."
        ),
    },
    "52w_high_breakout_with_smart_money_vol_below_long": {
        "cluster_id": "52W_BREAKOUT_FAMILY",
        "owner_review_notes": (
            "5 fires. Batch 613 B-twin for A/B test: at 52w-high with smart_money, "
            "does vol_below_avg (Bulkowski 2005 retest supply-absorption) vs vol_spike_"
            "12x work better? This is intentional A/B partner to 52w_high_breakout_"
            "with_smart_money_long. Root cause: multi-gate (52w_high + smart_money + "
            "vol_below_avg) triple joint scarce."
        ),
        "recommendation": (
            "ACCEPT AS A/B PARTNER (deliberate low-fire A/B test). Cube measures A vs B "
            "performance not fire count. Statistical validity requires enough fires - "
            "5 is below viable per min_trades. Universe expansion may lift to viable, "
            "or accept A/B as inconclusive at Batch A scale."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": "",
    },
    "hammer_at_support_long": {
        "cluster_id": "CANDLE_PATTERN_FAMILY",
        "owner_review_notes": (
            "5 fires. STATUS: EXPLORATORY POST-B773 per B769 council F5 - Class 7 NEW "
            "inverse-mirror registered B685 but NEVER cluster-walked. Non-deletion "
            "marker per feedback_no_a_priori. Root cause: hammer candle (~2-3% of bars) + "
            "support proximity + gate stack likely tight."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B. Owner may cluster-walk "
            "in future to remove EXPLORATORY tag."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_hammer_at_support_wider_long: widen candle set to (hammer OR "
            "bullish_pin_bar OR piercing_line) - broader bullish-reversal family. "
            "Retain support proximity + OBV. Expected fire uplift 2-3x."
        ),
    },
    "ichimoku_cloud_breakout": {
        "cluster_id": "ICHIMOKU_FAMILY",
        "owner_review_notes": (
            "5 fires. Batch 207 Ichimoku cloud breakout + weekly Kumo alignment. Phase "
            "1A-beta showed 43 trades / 18.6% WR / Sharpe -1.00 - second-worst carrier. "
            "Batch 657 T8 redundancy audit (option E = A+D) applied. Council 232 output "
            "showed 19,805 expected vs 4 actual = MASSIVE gap - producer investigation "
            "critical. Same family-wide issue as ichimoku_cloud_breakdown (Turn 2) and "
            "ichimoku_tk_cross (Turn 6)."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FAMILY-WIDE: Council 232 flagged massive gap. Verify "
            "compute_ichimoku emits ichi_above_cloud + weekly Kumo signals correctly. "
            "This is HIGHER priority than earlier due to expected-vs-actual delta. "
            "If producer OK, B657 tightening + 18.6% WR history suggest strategy has "
            "no edge - accept LOW or delete post-cube."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "macd_ichimoku": {
        "cluster_id": "ICHIMOKU_FAMILY",
        "owner_review_notes": (
            "5 fires. Dual 2-gate: MACD crossover_up + ichi_above_cloud (LONG) / "
            "MACD crossover_dn + ichi_below_cloud (SHORT) + borrow. Simple confluence. "
            "Same Ichimoku family producer issue as other ichimoku_* strategies. "
            "MACD crossover events are ~2-5/yr per ticker; ichi cloud position is STATE."
        ),
        "recommendation": (
            "Same Ichimoku family producer investigation. If producer OK, simple 2-gate "
            "structure has no loose knobs beyond producer widening. Accept as "
            "structurally low-fire OR delete post-cube if no edge."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "news_sentiment_shift_long": {
        "cluster_id": "NEWS_SENTIMENT_FAMILY",
        "owner_review_notes": (
            "5 fires. Batch 253: news_sentiment_shift > +0.4 (delta detector vs 7d prior) "
            "+ news_article_count >= 2 + 200-EMA. B748d producer confirmed working. "
            "B832 SPOF sentinel warnings apply. Root cause: +0.4 sentiment shift is "
            "strong (~top quartile of shifts); combined with article count + EMA200 = "
            "3-way scarce joint."
        ),
        "recommendation": (
            "Same as news_* family: B832 SPOF producer investigation FIRST. If producer "
            "OK, LOOSEN sentiment_shift > +0.4 -> > +0.25 (broader positive shift). "
            "Expected fire uplift 3-5x. Similar loosening pattern as news_momentum_long "
            "(Turn 3 HIGH) and news_sentiment_long (Turn 6 HIGH)."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "52w_high_breakout_with_smart_money_long": {
        "cluster_id": "52W_BREAKOUT_FAMILY",
        "owner_review_notes": (
            "4 fires. Batch 613 re-walk applied F1+F2a+a. F1 docstring reframe: EVENT half "
            "of _has_smart_money_buy (insider_cluster + cfo_buy + large_dollar_buy) is "
            "bar-of-fire timing alpha; STATE 13F is slow eligibility filter (not "
            "conviction). Same 13F STATE-timing distinction pattern as other smart_money "
            "sleeves. 3-gate + smart_money union: 52w high breakout + smart_money + gate. "
            "A-side of Batch 613 A/B test."
        ),
        "recommendation": (
            "LOOSEN smart_money to EVENT-only per feedback_signal_temporality (drop "
            "STATE 13F components). Preserves bar-of-fire timing alpha per B613 F1 "
            "docstring lineage. Expected fire uplift 2-3x. B-side (vol_below_avg "
            "variant) also 5 fires; the A/B test itself is inconclusive at Batch A scale."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "camarilla_s3_bounce": {
        "cluster_id": "FLOOR_PIVOT_FAMILY",
        "owner_review_notes": (
            "4 fires. REFRAMED POST-B879 as daily mean-reversion zone (not intraday "
            "pivot-precision). Camarilla S3 mean-reversion bounce + RSI extreme + OBV "
            "flow. Root cause: S3 proximity is a specific rare event on daily bars; "
            "RSI extreme (~<25 or >75) is ~5-10% of bars; OBV directional gate compounds."
        ),
        "recommendation": (
            "LOOSEN: RSI extreme threshold widening (<25 -> <30). Retain S3 proximity + "
            "OBV. Expected fire uplift 2-3x. Post-B879 daily reframe is correct "
            "framework."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
}


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    for col in ("cluster_id", "owner_review_notes", "recommendation",
                "priority", "exploratory_loose_variant"):
        if col not in df.columns:
            df[col] = ""

    updated = 0
    for strat, data in TURN_9_ANALYSIS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found in CSV")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)
    total_analyzed = (df["owner_review_notes"].fillna("").str.len() > 0).sum()
    starved_total = (df["class"] == "STARVED").sum()
    starved_analyzed = ((df["class"] == "STARVED") & (df["owner_review_notes"].fillna("").str.len() > 0)).sum()
    print(f"Turn 9 complete: updated {updated}. Cumulative {total_analyzed}/{len(df)} ({100*total_analyzed/len(df):.1f}%)")
    print(f"STARVED class: {starved_analyzed}/{starved_total}")

    from collections import Counter
    print(f"Turn 9 priorities: {Counter(d['priority'] for d in TURN_9_ANALYSIS.values())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
