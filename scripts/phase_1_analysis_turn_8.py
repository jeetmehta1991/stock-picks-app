#!/usr/bin/env python
"""Phase 1 deep-dive analysis TURN 8 (Council 235 owner-approved 2026-07-02).

Turn 8 scope: STARVED strategies 46-60 by fire count (9-7 fires).
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_8_ANALYSIS = {
    "52w_high_breakout": {
        "cluster_id": "52W_BREAKOUT_FAMILY",
        "owner_review_notes": (
            "9 fires. Batch 697 walk applied 2 B693 sweep changes: (1) DROPPED "
            "sector_outperforming_spy gate (REJECT_REDUNDANT verdict; sector RS filter "
            "vetoes good individual breakouts), (2) LOOSENED same-bar 4-way AND. Post-"
            "B697 gate stack should have been reduced. Root cause: even post-loosening, "
            "52w high breakout is a specific EVENT (~5-10/yr per ticker); combined with "
            "remaining gates + T1a-only universe = 9 fires reasonable."
        ),
        "recommendation": (
            "INVESTIGATE: verify B697 changes applied - if sector gate still present + "
            "4-way AND not loosened, apply the pending changes. If B697 fully applied, "
            "9 fires is close to structural minimum for T1a. Universe expansion (Batch B) "
            "primary lever. Universe-agnostic pattern."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "cup_and_handle_retest_long": {
        "cluster_id": "CHART_PATTERN_FAMILY",
        "owner_review_notes": (
            "9 fires. Batch 685 replaced buggy resistance_break_retest (DC20-anchored "
            "proxy) with cup_handle_neckline_break_retest_long (B685 NEW producer, "
            "anchored on cup_handle_breakout_level = handle high). Same B607/B605/B606 "
            "family fix pattern. B685 also swapped price_above_ema_50 default-True -> "
            "default-False (silent-gap closure). Root cause: cup pattern detection + "
            "neckline break + retest = triple-rare event sequence."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify compute_cup_handle_neckline_break_retest_signals "
            "fires on canonical cases. If OK, chart-pattern-retest strategies "
            "inherently rare (Bulkowski canonical); accept LOW. Producer-side widen "
            "retest tolerance band (1% -> 2%) may help 2x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "doji_at_resistance_short": {
        "cluster_id": "CANDLE_PATTERN_FAMILY",
        "owner_review_notes": (
            "9 fires. Batch 572 Nison symmetric mirror of doji_at_support. B574 narrow-"
            "scope: consumes _wide flag variants (1.5% band vs standard 0.3%) - already "
            "loosened. 3-gate: doji + (near_r1_wide OR near_r2_wide OR at_key_fib_wide) "
            "+ vol_spike_15x + borrow. Root cause: doji itself is 3-5% of bars; vol_"
            "spike_15x is fire-starving (same pattern as 12+ other strategies)."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_15x -> vol_spike_2x (same fix as recurring vol pattern). "
            "Expected fire uplift 3-5x. Retain wide-pivot proximity + doji + borrow. "
            "Pattern S SHORT asymmetric expectancy caveat."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "pead_long": {
        "cluster_id": "PEAD_FAMILY",
        "owner_review_notes": (
            "9 fires. Batch 209 PEAD Bernard-Thomas 1989 + Garfinkel-Hribar-Hsiao 2024. "
            "3-gate: within_pead_window (60d post-earnings) + pead_positive_surprise + "
            "positive ann-day return >+2%. Root cause: 60d post-earnings window is "
            "broad (~25% of bars); positive surprise + >+2% ann-day return are "
            "conditional on earnings dates + magnitude. Compound: earnings ~4/yr per "
            "ticker; positive-surprise-with-strong-day ~30-40% of earnings = 1-2/yr per "
            "ticker. 150 tickers x 4y = expected 600-1200 fires universe-wide theoretical; "
            "9 fires suggests producer under-firing OR window/threshold too strict."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify pead_positive_surprise + within_pead_window "
            "producers fire correctly. Cross-reference with pead_with_smart_money variant "
            "(same 7 fires - similar producer dependency). If producer OK, LOOSEN >+2% "
            "ann-day return -> >+1% (Garfinkel 2024 uses lower threshold). Expected fire "
            "uplift 3-5x."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "post_inclusion_reversal_short": {
        "cluster_id": "INDEX_REBALANCE_FAMILY",
        "owner_review_notes": (
            "9 fires. Post-index-inclusion reversal short (fade the inclusion pop). "
            "Chen-Noronha-Singal 2004 documented reversal window post initial pop. "
            "Producer dependency on index_rebalance_events.parquet. Same universe issue "
            "as post_deletion/pre_rebalance family (Turn 3 findings). Batch A 150 "
            "tickers may capture 3-9 inclusion events across 4y = 9 fires reasonable."
        ),
        "recommendation": (
            "ACCEPT AS STRUCTURAL: universe expansion (Batch B 1787) will 10-20x fires. "
            "Producer investigation as family (verify index_rebalance_events.parquet "
            "populated). Pattern S SHORT asymmetric expectancy caveat."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": "",
    },
    "xs_quality_top_quintile_long": {
        "cluster_id": "CROSS_SECTIONAL_FAMILY",
        "owner_review_notes": (
            "9 fires. Batch 222 Novy-Marx 2013 quality (gross profitability) + Asness-"
            "Frazzini-Pedersen 2019 QMJ. 2-gate: xs_quality_top_quintile + price_above_"
            "ema_200. Sharpe 0.8-1.1 standalone + 1.4 combined with momentum. Root cause: "
            "top quintile of quality is ~20% of universe per snapshot; EMA200 uptrend "
            "further filters. On T1a 150 tickers, top-quintile quality is inherently "
            "limited (~30 names) + rebalance cadence."
        ),
        "recommendation": (
            "UNIVERSE EXPANSION primary lever: T1a S&P 500 includes many high-quality "
            "names naturally; top-quintile within this pre-filtered universe is even "
            "narrower than full-market quintiling. Batch B 1787 tickers will 5-10x "
            "fires. Consumer-side gates minimal."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "52w_high_breakout_pullback_long": {
        "cluster_id": "52W_BREAKOUT_FAMILY",
        "owner_review_notes": (
            "8 fires. Batch 586 owner-directive 'MISSING inverse' addition. Single-gate: "
            "near_52w_high_retest_long. Producer emits when (a) 52w high broken in last "
            "10 days, (b) close within 1% of that level, (c) volume below 20d avg, "
            "(d) bullish bar. 4-condition producer compound = rare event. Universe-"
            "agnostic pattern."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify near_52w_high_retest_long fires on canonical "
            "cases. Producer-side widening (1% -> 2% proximity band OR 10d -> 20d "
            "recency window) may 2-3x. Otherwise accept as structural rare event."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "golden_cross_50_200": {
        "cluster_id": "GOLDEN_DEATH_CROSS_FAMILY",
        "owner_review_notes": (
            "8 fires. Dual single-gate: ema_50_200_golden_cross (LONG) / _death_cross "
            "(SHORT) + borrow. NO vol confirmation, NO other gates - just the cross event. "
            "B660 baseline = 504/yr universe-wide (unvolume gated). 8 fires on Batch A "
            "150 x 4y is way below expected. Likely explanations: (a) B660 measured on "
            "503 tickers vs 150 stratified; (b) trading calendar / regime distribution "
            "in Batch A window suppressed crosses (2022-2026 has 2 bear phases + 2 bull "
            "phases = ~4-8 crosses total per ticker); (c) producer issue."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify ema_50_200_golden_cross fires on known events "
            "(SPY 2020-06-30, 2023-01-25 golden crosses). If producer OK, universe "
            "expansion primary lever. This is a STRUCTURALLY low-fire strategy per B660 "
            "baseline; 8 fires may be near expected for 150-ticker universe."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "smc_fvg_retest_short": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "8 fires. Batch 216 bearish FVG retest + below_ema_200 + borrow. Simple "
            "2-gate but smc_fvg_retest_short_zone is a specific ICT-library producer "
            "signal. Family-wide producer investigation applies (per Turn 6 finding). "
            "Pattern S SHORT asymmetric expectancy caveat."
        ),
        "recommendation": (
            "Same as SMC family: producer investigation (smartmoneyconcepts library). "
            "Accept as structural if producer OK. Pattern S caveat."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "vol_spike_2x_below_ema_50_short": {
        "cluster_id": "PRICE_ACTION_FAMILY",
        "owner_review_notes": (
            "8 fires. Batch 670 Class 7 NEW replacement for deleted "
            "strat_institutional_capitulation_short. 2-gate: vol_spike_2x + below_ema_50 "
            "+ borrow. Honest 2-gate tape-capitulation continuation SHORT thesis. Root "
            "cause: vol_spike_2x is not overly tight (~5-8% of bars); combined with "
            "below_ema_50 (~40% in downtrend) + borrow filter = expected 1-3% of bars. "
            "Universe-agnostic but Pattern S SHORT asymmetric caveat."
        ),
        "recommendation": (
            "STATUS QUO on gates (already loose 2-gate structure). Pattern S SHORT "
            "asymmetric expectancy is the underlying constraint - cube may show "
            "FAIL_EDGE even with more fires. Universe expansion may 2-3x fires; borrow "
            "filter blocks small-caps typically."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": "",
    },
    "bollinger_tight": {
        "cluster_id": "BOLLINGER_MEAN_REVERSION_FAMILY",
        "owner_review_notes": (
            "7 fires. Batch 204 Bollinger 1.5-sigma variant (tighter than "
            "bollinger_lower 2.0-sigma). Root cause: 1.5-sigma tightness means BB "
            "touches are MORE frequent (~15% of bars vs 5% at 2-sigma) but softer RSI "
            "threshold compensates - net effect is fires more often than bollinger_lower. "
            "7 fires vs bollinger_lower 29 = 4x DIFFERENCE despite tighter BB - "
            "suggests EITHER: (a) producer bb_20_15_squeeze underfires OR (b) 200-EMA "
            "regime gate blocks most fires OR (c) RSI threshold interaction."
        ),
        "recommendation": (
            "INVESTIGATE: why 7 fires vs bollinger_lower 29 when 1.5-sigma should fire "
            "MORE often? Likely producer bb_20_15_squeeze is silent-mode - grep for key "
            "and verify. If producer OK, LOOSEN 200-EMA regime gate OR RSI threshold. "
            "Expected fire uplift 2-3x."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "monthly_bias_momentum_long": {
        "cluster_id": "MULTI_TIMEFRAME_FAMILY",
        "owner_review_notes": (
            "7 fires. Batch 217 monthly bias + 6-month momentum + daily breakout. "
            "Batch 727 tightened above_prev_high -> above_prev_high_clearance_atr_05 "
            "per B710 W6 anti-fakeout + S4-B717 ceiling routing. B660 pre-B727 fired "
            "10,507/yr LONG = state flag; post-B727 ATR-scaled clearance separates real "
            "breaks from one-tick pokes. 7 fires post-tightening is expected outcome per "
            "B717 ceiling routing."
        ),
        "recommendation": (
            "STATUS QUO on B727 tightening (empirically justified per ceiling routing). "
            "7 fires is deliberate outcome. Consider small ATR clearance widening (0.5 "
            "-> 0.3) if owner wants MARGINAL territory."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": "",
    },
    "pead_with_smart_money_long": {
        "cluster_id": "PEAD_FAMILY",
        "owner_review_notes": (
            "7 fires. Variant of pead_with_insider_confirmation_long using broader "
            "smart_money composite (insider + institutional + CFO + large_dollar via "
            "_has_smart_money_buy). Same producer dependency as pead_long. Sleeve on "
            "top of PEAD base signal."
        ),
        "recommendation": (
            "Same producer investigation as pead_long. STATE 13F miscredit caveat for "
            "smart_money leg. If producer OK, threshold loosen ann-day return >+2% -> "
            ">+1%. Expected fire uplift 2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "squeeze_breakout_with_smart_money_long": {
        "cluster_id": "SMART_MONEY_SLEEVE_FAMILY",
        "owner_review_notes": (
            "7 fires. B975 fixed key-mismatch: 'squeeze_on_release' (nonexistent) -> "
            "'squeeze_fire_up' (canonical Lazy Bear). 3-gate + smart_money: "
            "squeeze_fire_up + close_above_open + _has_smart_money_buy. Root cause: "
            "squeeze_fire_up is EVENT (~2-5/yr per ticker on daily bars); + close_above_"
            "open + smart_money union = 3-way scarce. Same STATE-timing miscredit for "
            "smart_money leg."
        ),
        "recommendation": (
            "LOOSEN smart_money to EVENT-only components (insider + cfo + large_dollar) "
            "per feedback_signal_temporality - drop STATE 13F. Alternatively drop "
            "smart_money AND requirement; move to secondary boost. Expected fire uplift "
            "2-3x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "xs_momentum_quality_combined": {
        "cluster_id": "CROSS_SECTIONAL_FAMILY",
        "owner_review_notes": (
            "7 fires. Batch 222: top-decile momentum + top-quintile quality + EMA200. "
            "STATUS: EXPLORATORY POST-B787 per B786 verdict FAIL_FIRE_STARVED 0/yr under "
            "full B779+B781 config. Sister of xs_combined_momentum_low_ivol - same "
            "Pattern AA compound rarity (xs_momentum_top_decile 43/yr x xs_quality_top_"
            "quintile rarity x EMA200 = ~0)."
        ),
        "recommendation": (
            "KEEP EXPLORATORY per owner Council 235 Option B."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": (
            "strat_xs_momentum_quality_wider_long: LOOSEN xs_momentum_top_decile -> "
            "xs_momentum_top_quintile (top 20% vs top 10%). Retain quality confluence. "
            "Same pattern as xs_combined_momentum_low_ivol wider variant. Expected fire "
            "uplift 3-5x."
        ),
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
    for strat, data in TURN_8_ANALYSIS.items():
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
    print(f"Turn 8 complete: updated {updated}. Cumulative {total_analyzed}/{len(df)} ({100*total_analyzed/len(df):.1f}%)")
    print(f"STARVED class: {starved_analyzed}/{starved_total}")

    from collections import Counter
    print(f"Turn 8 priorities: {Counter(d['priority'] for d in TURN_8_ANALYSIS.values())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
