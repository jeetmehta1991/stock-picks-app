#!/usr/bin/env python
"""Phase 1 deep-dive analysis TURN 6 (Council 235 owner-approved 2026-07-02).

Turn 6 scope: STARVED strategies 16-30 by fire count (19-14 fires).
Same schema + depth as prior turns.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_6_ANALYSIS = {
    "institutional_persistence_breakout_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "19 fires. 3-gate: institutional_increased >= 5 + resistance_break_retest + "
            "price_above_ema_200. Wave 3 Batch 337. Same >= 5 threshold and 13F STATE "
            "issues as institutional_persistence_momentum (Turn 5). Compounded with "
            "resistance_break_retest (rare event) makes joint rare."
        ),
        "recommendation": (
            "LOOSEN: institutional_increased >= 5 -> >= 3 (canonical cluster). Retain "
            "retest + EMA200. Expected fire uplift 2-3x (19 -> 40-60, MARGINAL/near-"
            "VIABLE). Same pattern as Turn 5 institutional_persistence_momentum."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "vix_backwardation_long": {
        "cluster_id": "CROSS_ASSET_FAMILY",
        "owner_review_notes": (
            "19 fires. 2-gate: vix_term_backwardation + xs_quality_decile >= 8. Cheng "
            "2019 short-vol unwind convexity. Root cause: VIX backwardation is a genuine "
            "stress regime (rare - 2022 bear phases, 2025-04 tariff panic). Restricted "
            "to top-quintile quality further narrows. Batch A 4y window captured the "
            "2022 stress + 2025-04 stress = ~40-60 days of VIX backwardation; combined "
            "with quality decile filter = 19 fires."
        ),
        "recommendation": (
            "LOOSEN: xs_quality_decile >= 8 -> >= 7 (top-quintile broader). Retain "
            "backwardation gate (this IS the alpha hypothesis). Expected fire uplift "
            "1.5-2x. Or drop quality filter entirely to isolate pure backwardation "
            "convexity - broader test of Cheng 2019 hypothesis."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "htf_aligned_breakout_short": {
        "cluster_id": "MULTI_TIMEFRAME_FAMILY",
        "owner_review_notes": (
            "18 fires. Batch 217 symmetric mirror of htf_aligned_breakout_long. 3-gate: "
            "below_prev_low + vol_spike_15x + htf_aligned_bear + borrow_ok. Same "
            "vol_spike_15x fire-starving pattern as long variant + Pattern S SHORT "
            "asymmetric expectancy."
        ),
        "recommendation": (
            "LOOSEN: vol_spike_15x -> vol_spike_2x (symmetric to Turn 5 long variant fix). "
            "Expected fire uplift 3-5x. Pattern S caveat."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "52w_low_breakdown_pullback_short": {
        "cluster_id": "52W_BREAKOUT_FAMILY",
        "owner_review_notes": (
            "17 fires. Batch 586 inverse of 52w_high_breakout_pullback_long per feedback"
            "_long_short_inverse_audit. Single-gate: near_52w_low_retest_short + borrow. "
            "Root cause: 52w low breakdown followed by retest is a specific rare event - "
            "producer-side rarity. Universe-agnostic pattern but structurally low fire "
            "count."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER: verify near_52w_low_retest_short populates on canonical "
            "cases. If OK, universe expansion (Batch B / T3 with more distressed names) "
            "more likely to help than gate loosening. Accept STARVED as structural minimum "
            "for T1a-only Batch A universe. Pattern S caveat."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "ichimoku_tk_cross": {
        "cluster_id": "ICHIMOKU_FAMILY",
        "owner_review_notes": (
            "17 fires. Dual: LONG = ichi_tk_cross_up + ichi_above_cloud; SHORT = "
            "ichi_tk_cross_dn + ichi_below_cloud + borrow. B634 semantic tightening: "
            "pre-B634 'not below cloud' allowed in-cloud fires; post-B634 'strictly "
            "above cloud'. Root cause: TK cross is EVENT (~1-2/yr per ticker); cloud "
            "position is STATE. Ichimoku family low-fire caveat (from Council 232 "
            "ichimoku_cloud_breakout showed 19,805 expected vs 4 actual - producer may "
            "have wider issue)."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FIRST (family-wide): verify compute_ichimoku emits "
            "TK cross + cloud position on canonical cases. Council 232 showed ichimoku_"
            "cloud_breakout massive expected-vs-actual gap. If producer OK, this is "
            "structurally low-fire (TK crosses ~2/yr); accept 17 fires as reasonable "
            "for 4y x 150 tickers."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "activist_13d_long": {
        "cluster_id": "SEC_EDGAR_EVENT_FAMILY",
        "owner_review_notes": (
            "16 fires. Batch 522 P17b: sc_13d_filed_within_30d single-gate. Brav-Jiang-"
            "Partnoy-Thomas 2008 activist +6.8% abnormal return; Bebchuk-Brav-Jiang 2015 "
            "sustained +3-5pp/yr alpha 5y post-filing. B748c producer state confirmed: "
            "1715 per-ticker SC_13D parquets. Root cause: 13D filings are STRUCTURALLY "
            "rare (10-50/yr universe-wide across activist filers Icahn/Ackman/Peltz/"
            "Elliott/ValueAct/Starboard). 16 fires on T1a 4y = reasonable base rate."
        ),
        "recommendation": (
            "ACCEPT AS STRUCTURAL: 13D activist filings are inherently rare events. "
            "Universe expansion (Batch B including small-caps + non-T1a) will lift "
            "fires 5-10x since activists disproportionately target non-S&P 500 names. "
            "For T1a-only Batch A, 16 fires is close to realistic maximum. Widening "
            "the 30d window (30d -> 90d Brav 2008 window) could 2-3x fires."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "bollinger_tight_with_smart_money_long": {
        "cluster_id": "SMART_MONEY_SLEEVE_FAMILY",
        "owner_review_notes": (
            "16 fires. 2-gate + smart_money union: bb_20_20_squeeze + close_above_open + "
            "_has_smart_money_buy. B975 fixed key-mismatch ('bb_squeeze' -> "
            "'bb_20_20_squeeze'). Root cause: BB squeeze is a specific event (~5-10% of "
            "bars); combined with smart_money union = 3-way joint. Similar to Turn 3 "
            "smart_money_sleeve family."
        ),
        "recommendation": (
            "LOOSEN: expand bb_squeeze to (bb_20_20_squeeze OR bb_20_15_squeeze) - "
            "canonical BB squeeze definitions vary (Bollinger 1992 uses 20-period 2-"
            "stdev). Retain close_above_open + smart_money. Expected fire uplift 2-3x. "
            "Same STATE-timing miscredit caveat for smart_money."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "insider_cluster_concentrated_sell_short": {
        "cluster_id": "INSIDER_FORM4_FAMILY",
        "owner_review_notes": (
            "16 fires. B1010 Class 7 NEW SHORT-only. Uses concentrated_sell (>50% of "
            "insider's holdings dumped) - the ONLY economically-defensible SHORT mirror "
            "per B662 SM-1 walk + feedback_asymmetric_data_sources_break_mechanical_inverse. "
            "Root cause: concentrated_sell threshold is HIGH (>50% liquidation is rare - "
            "typical insider selling is 5-20% for diversification/tax). Universe-agnostic "
            "signal but structurally rare."
        ),
        "recommendation": (
            "ACCEPT AS STRUCTURAL. concentrated_sell at 50% is the correct threshold "
            "per Lakonishok-Lee 2001 + Marin-Olivier 2008 filtering out diversification "
            "noise. Loosening would reintroduce noise. Universe expansion may 2-3x fires. "
            "Pattern S SHORT asymmetric expectancy caveat."
        ),
        "priority": "LOW",
        "exploratory_loose_variant": "",
    },
    "news_sentiment_long": {
        "cluster_id": "NEWS_SENTIMENT_FAMILY",
        "owner_review_notes": (
            "16 fires. Batch 253/278/314 evolution: mean sentiment > 0.5 + article count "
            ">= 3 (loosened from B278 which drove fires to zero). Lopez-Lira-Tang 2023 + "
            "Loughran-McDonald 2011. B832 SPOF sentinel warnings during Batch A run: "
            "Polygon news sentiment field may be silently dropped for 100+ returns. "
            "Root cause could be producer-side (SPOF) OR genuine gate stack."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FIRST (B832 SPOF): verify Polygon sentiment field "
            "populates non-null in news_sentiment.py for Batch A window. If producer OK, "
            "consider LOOSEN mean_sentiment > 0.5 -> > 0.3 (broader positive vs top-"
            "quartile). Expected fire uplift 3-5x. Similar to news_momentum recommendations "
            "from Turn 3."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "smc_liquidity_sweep_reversal": {
        "cluster_id": "ICT_SMC_FAMILY",
        "owner_review_notes": (
            "16 fires. Dual: LONG = smc_liquidity_swept_dn + (smc_choch_bullish OR "
            "smc_bos_bullish); SHORT = symmetric mirror + borrow. Batch 210 SMC/ICT "
            "family. Root cause: liquidity sweep is producer-rare event + CHoCH/BOS "
            "confirmation is also producer-rare. Same smartmoneyconcepts library "
            "dependency as other smc_* strategies."
        ),
        "recommendation": (
            "INVESTIGATE PRODUCER FAMILY: verify smartmoneyconcepts library emits sweep "
            "+ CHoCH + BOS signals reliably. Producer investigation should be family-"
            "wide (covers judas_swing, turtle_soup, smc_bos, smc_mitigation, smc_"
            "equal_highs/lows, smc_order_block, smc_choch, smc_fvg, smc_ote). If OK, "
            "accept as structural."
        ),
        "priority": "HIGH",
        "exploratory_loose_variant": "",
    },
    "institutional_multi_quarter_persistence_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "15 fires. Batch 344/333b: TRUE multi-quarter persistence (Yan-Zhang 2009 "
            "RFS canonical) - persistent_holders_4q >= 10 (held position across >=4 "
            "consecutive quarters) + price_above_ema_200. Reads from data_prefetch/"
            "derived/institutional_persistence_t1a/ (B748d confirmed). Root cause: "
            ">=10 persistent holders across 4 quarters is strict; +200 EMA regime "
            "gate further narrows."
        ),
        "recommendation": (
            "LOOSEN: persistent_holders_4q >= 10 -> >= 5 (Yan-Zhang 2009 canonical "
            "threshold varies - 5 is used in some implementations). Retain EMA200 "
            "regime gate. Expected fire uplift 2x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "orb_stocks_in_play_long": {
        "cluster_id": "GAP_AND_GO_FAMILY",
        "owner_review_notes": (
            "15 fires. Batch 211 daily-bar proxy for Zarattini-Barbon-Aziz 2024 5-min "
            "intraday ORB. Setup: gap_up_pct > +2% (in-play filter) + close > today's "
            "open (ORB high break proxy) + vol_spike_2x. Root cause: gap_up_pct > +2% "
            "is rare (~5-10% of bars for T1a large-caps; higher for small-caps). Compound "
            "with vol_spike_2x = ~1-2% of bars per ticker per year. Universe-agnostic "
            "but T1a large-caps have fewer +2% gaps than small-caps."
        ),
        "recommendation": (
            "LOOSEN: gap_up_pct > +2% -> > +1.5% (broader gap-and-go zone). Retain "
            "ORB proxy + vol confirmation. Expected fire uplift 1.5-2x. Universe "
            "expansion to non-T1a much larger (small-caps have 3-5x more gap events)."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "donchian_breakout_with_smart_money_long": {
        "cluster_id": "SMART_MONEY_SLEEVE_FAMILY",
        "owner_review_notes": (
            "14 fires. 2-gate + smart_money union: dc20_breakout_up + close_above_open + "
            "_has_smart_money_buy. Classic trend-following + smart-money confirmation "
            "sleeve. Root cause: DC20 breakout is a specific EVENT (~5-10/yr per ticker); "
            "compound with smart_money union rarity + close bullish = joint. Same STATE-"
            "timing miscredit caveat as other smart_money_sleeve strategies."
        ),
        "recommendation": (
            "STATUS QUO on core gates (DC20 + close). LOOSEN smart_money: consider "
            "ablation to isolate DC20 pure vs DC20+smart_money contribution. Or: split "
            "smart_money union into EVENT-only (insider + cfo + large_dollar buy) vs "
            "STATE (13F) - per feedback_signal_temporality, only EVENT provides bar-of-"
            "fire timing alpha."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "institutional_breakout_confirmation_long": {
        "cluster_id": "INSTITUTIONAL_13F_FAMILY",
        "owner_review_notes": (
            "14 fires. Batch 610 walk: institutional_buy + resistance_break_retest + "
            "close_above_open + vol_below_avg (Bulkowski canonical retest supply-"
            "absorption). Same institutional STATE + retest event compound rarity."
        ),
        "recommendation": (
            "LOOSEN: drop vol_below_avg gate (Bulkowski canonical is optional; "
            "feedback_avwap_redundant precedent applies to volume-below-avg retest "
            "condition too). Retain institutional_buy + retest + close_above_open. "
            "Expected fire uplift 2x."
        ),
        "priority": "MED",
        "exploratory_loose_variant": "",
    },
    "poc_magnet_long": {
        "cluster_id": "VOLUME_PROFILE_FAMILY",
        "owner_review_notes": (
            "14 fires. Batch 255 POC magnet: vp_close_near_poc_pct < 0.02 (2%) + bullish "
            "bias + EMA200. Batch 724 REVERSED B314's 4% loosening back to 2% per S4-"
            "B717 ceiling routing (B660 measured 11,334/yr at 4% threshold = state-flag "
            "rate). Root cause: 2% POC proximity is deliberately tight per B710/B724 "
            "reviewer verdict - LOOSENING RISKS reintroducing 'fires too often to be "
            "selective' issue."
        ),
        "recommendation": (
            "STATUS QUO on B724 tightening (empirically justified). 14 fires is intended "
            "outcome. If owner wants more fires, alternative is Universe expansion "
            "(Batch B) NOT threshold loosening. Producer-side note: verify volume_"
            "profile.py POC computation is correct (B1035 confirmed producer exists)."
        ),
        "priority": "LOW",
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
    for strat, data in TURN_6_ANALYSIS.items():
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
    print(f"Turn 6 complete: updated {updated}. Cumulative {total_analyzed}/{len(df)} ({100*total_analyzed/len(df):.1f}%)")
    print(f"STARVED class: {starved_analyzed}/{starved_total}")

    from collections import Counter
    print(f"Turn 6 priorities: {Counter(d['priority'] for d in TURN_6_ANALYSIS.values())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
