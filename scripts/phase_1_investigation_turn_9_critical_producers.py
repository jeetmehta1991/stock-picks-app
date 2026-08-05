#!/usr/bin/env python
"""Council 242 (2026-07-03) Turn 9: 20 CRITICAL (0 fires) producer investigations.

SCOPE: 20 of 43 remaining CRITICAL strategies grouped by producer family.

PRODUCER GROUPS + FILES:
  Classification change (10): backtest/data/signal_loader.py
  Institutional volume (4):   backtest/signals/institutional_persistence_consumer.py
  News reversal (3):          backtest/signals/news_sentiment.py
  Pivot (3):                  backtest/signals/technical.py compute_pivots

PRIOR TURN LINKAGES:
  News producer already investigated Turn 4 (news_momentum_long/news_sentiment_long)
    - B832 SPOF sentinels tripped during Batch A (BUG-280)
  Pivot producer already used by Turn 6 camarilla_r4_breakout verdict
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_9_INVESTIGATIONS = {
    # ========== CLASSIFICATION CHANGE FAMILY (10) ==========
    "classification_change_breakout_long": {
        "post_investigation_verdict": "PRODUCER_OK + STATE_TO_EVENT_STARVED",
        "post_investigation_recommendation": (
            "Producer signal_loader.py loads sector classification from Master Dedup "
            "CSV. Classification-change EVENT fires when a ticker's classification "
            "shifts within N-day window. Consumer gate stack: classification_change_"
            "recent + Donchian breakout + volume + AVWAP. 0 fires = compound EVENT "
            "of classification change (rare - happens maybe 1-3/yr per ticker in "
            "sector reshuffles) x Donchian breakout x confirmation. ACTIONS: "
            "(1) LOOSEN classification_change_recent window (currently likely 5-10 "
            "days) to 30-60 days; (2) drop AVWAP redundant with EMA/Donchian trend "
            "per feedback_avwap_redundant. Expected 3-5x uplift."
        ),
        "final_recommended_actions": "[CRITICAL] [LOOSEN_THRESHOLD] classification_change_recent window 5-10d -> 30-60d; [DROP_REDUNDANT] AVWAP",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9 investigation. Producer signal_loader.py verified. Family-wide finding: 0 fires reflects STATE_TO_EVENT compound rareness (classification change events are structurally rare ~1-3/yr per ticker). Gap: classification_change_recent window value not verified from screener.py - actual current window may already be wide.",
    },
    "classification_change_momentum_long": {
        "post_investigation_verdict": "PRODUCER_OK + STATE_TO_EVENT_STARVED",
        "post_investigation_recommendation": (
            "Same producer as classification_change_breakout_long. Consumer gate "
            "adds momentum layer (RSI + MACD confluence) on top of classification "
            "change EVENT. Same LOOSEN path: widen classification_change_recent "
            "window. Drop redundant momentum indicators (RSI + MACD may be "
            "duplicative)."
        ),
        "final_recommended_actions": "[CRITICAL] [LOOSEN_THRESHOLD] classification_change_recent window; [DROP_REDUNDANT] duplicative momentum indicators",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Same producer + family fix path as classification_change_breakout_long. Gap: none.",
    },
    "classification_change_oversold_long": {
        "post_investigation_verdict": "PRODUCER_OK + STATE_TO_EVENT_STARVED",
        "post_investigation_recommendation": (
            "Same producer + adds RSI oversold overlay. Contrarian entry on "
            "classification change + oversold RSI. Same LOOSEN path on classification "
            "window; RSI oversold typically <30 - could widen to <35 for slightly "
            "more fires without diluting thesis."
        ),
        "final_recommended_actions": "[CRITICAL] [LOOSEN_THRESHOLD] classification_change_recent window; RSI<30 -> RSI<35",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Same producer + family. Gap: none.",
    },
    "classification_change_recent_long": {
        "post_investigation_verdict": "PRODUCER_OK + BASE_EVENT_ONLY_STARVED",
        "post_investigation_recommendation": (
            "Producer emits classification_change_recent. This strategy is the "
            "BASE version - single gate (classification_change_recent) alone. 0 "
            "fires suggests EVEN THE BASE producer output is rare in Batch A "
            "window. ACTIONS: (1) widen classification_change_recent window; "
            "(2) URGENT verify producer emits AT ALL for Batch A tickers - if "
            "not, may indicate signal_loader classification data is stale or "
            "missing for T1a subset. Runtime probe: grep signal_loader emit for "
            "any Batch A ticker on any date in 2022-2026."
        ),
        "final_recommended_actions": "[CRITICAL] [FIX_PRODUCER] URGENT verify classification data present in Master Dedup CSV for Batch A tickers; [LOOSEN_THRESHOLD] widen window",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. This is the base single-gate strategy - 0 fires here suggests PRODUCER-LEVEL underfire, not consumer-gate stacking. Gap: no runtime probe on signal_loader emit for Batch A tickers yet.",
    },
    "classification_change_to_tech_long": {
        "post_investigation_verdict": "PRODUCER_OK + DIRECTIONAL_STATE_STARVED",
        "post_investigation_recommendation": (
            "Same producer + specific direction filter (target sector = Tech). "
            "Only fires when classification changes INTO tech sector. Much rarer "
            "than base classification_change. ACTIONS: (1) LOOSEN classification "
            "window; (2) accept STRUCTURAL_RARE - specific sector migration events "
            "are inherently uncommon; universe expansion primary lever."
        ),
        "final_recommended_actions": "[CRITICAL] [LOOSEN_THRESHOLD] classification_change window; [UNIVERSE_EXPAND] Batch B",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Directional-migration variant - inherently rarer than base. Gap: sector-migration count in Master Dedup CSV not enumerated.",
    },
    "classification_change_from_tech_short": {
        "post_investigation_verdict": "PRODUCER_OK + DIRECTIONAL_STATE + PATTERN_S",
        "post_investigation_recommendation": (
            "Same producer + direction filter (source sector = Tech). Symmetric "
            "SHORT mirror. Rare directional-migration event + Pattern S + borrow_ok. "
            "Same fix path + borrow_ok audit."
        ),
        "final_recommended_actions": "[CRITICAL] [LOOSEN_THRESHOLD] classification_change window; [FIX_PRODUCER] borrow_ok; Pattern S caveat",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Symmetric SHORT mirror. Gap: none.",
    },
    "classification_change_to_defensive_short": {
        "post_investigation_verdict": "PRODUCER_OK + DIRECTIONAL_STATE + PATTERN_S",
        "post_investigation_recommendation": (
            "Same producer + destination sector filter (Defensive - Utilities/"
            "Staples/RE). Contrarian thesis: capital rotation TO defensive sectors "
            "signals broader risk-off; SHORT non-defensives that get rotated OUT. "
            "Rare event + Pattern S. Same fix path."
        ),
        "final_recommended_actions": "[CRITICAL] [LOOSEN_THRESHOLD] classification_change window; [FIX_PRODUCER] borrow_ok; Pattern S caveat",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Contrarian defensive-rotation thesis. Gap: sector taxonomy 'Defensive' bucket definition not verified vs DEC-499 18-classifier taxonomy.",
    },
    "classification_change_volume_long": {
        "post_investigation_verdict": "PRODUCER_OK + STATE_TO_EVENT + VOLUME_CONFIRMATION",
        "post_investigation_recommendation": (
            "Same producer + volume confirmation on classification-change bar. "
            "Volume overlay is a reasonable confirmation but adds another rareness "
            "layer. Same LOOSEN path + widen volume threshold from vol_spike_2x "
            "to vol_above_avg."
        ),
        "final_recommended_actions": "[CRITICAL] [LOOSEN_THRESHOLD] classification_change window; vol_spike_2x -> vol_above_avg",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Volume-confirmed variant. Gap: none.",
    },
    "classification_change_with_insider_long": {
        "post_investigation_verdict": "PRODUCER_OK + TRIPLE_COMPOUND_STARVED",
        "post_investigation_recommendation": (
            "Triple compound: classification change EVENT + insider buying SIGNAL "
            "+ direction. Insider buying producer smart_money.py. 0 fires = "
            "compound of 3 rare independent events. ACTIONS: (1) LOOSEN "
            "classification window; (2) widen insider buying signal (insider_"
            "cluster_active window); (3) OR drop insider gate entirely and use "
            "classification+direction only."
        ),
        "final_recommended_actions": "[CRITICAL] [LOOSEN_GATE] Drop insider gate OR widen insider_cluster_active window; [LOOSEN_THRESHOLD] classification window",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Triple compound event probability. Gap: insider_cluster_active window value not verified.",
    },
    "classification_change_with_institutional_long": {
        "post_investigation_verdict": "PRODUCER_OK + TRIPLE_COMPOUND_STARVED",
        "post_investigation_recommendation": (
            "Same triple-compound pattern but with institutional (13F) instead of "
            "insider. Same LOOSEN path: drop institutional gate OR widen "
            "institutional_persistence window."
        ),
        "final_recommended_actions": "[CRITICAL] [LOOSEN_GATE] Drop institutional gate OR widen institutional_persistence window; [LOOSEN_THRESHOLD] classification window",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Same triple-compound pattern. Gap: institutional_persistence 13F quarterly refresh cadence may cause STATE delays; not verified.",
    },
    # ========== INSTITUTIONAL VOLUME FAMILY (4) ==========
    "institutional_oversold_long": {
        "post_investigation_verdict": "PRODUCER_OK + STATE_STATE_COMPOUND",
        "post_investigation_recommendation": (
            "Producer institutional_persistence_consumer.py emits institutional_"
            "buy STATE. Consumer gate stack: institutional_buy + RSI oversold + "
            "additional confirmation. 0 fires = compound STATE (13F quarterly "
            "refresh cadence + oversold event coincidence). ACTIONS: (1) LOOSEN "
            "RSI oversold threshold <30 -> <35; (2) drop redundant confirmation; "
            "(3) verify institutional_persistence data freshness across Batch A."
        ),
        "final_recommended_actions": "[CRITICAL] [LOOSEN_THRESHOLD] RSI<30 -> RSI<35; [DROP_REDUNDANT] confirmation gate; [AUDIT_DATA] institutional_persistence freshness",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. STATE-STATE compound. Gap: institutional_persistence data cadence (quarterly 13F filings) may cause staleness.",
    },
    "institutional_persistence_volume_long": {
        "post_investigation_verdict": "PRODUCER_OK + STATE_+_VOLUME_EVENT",
        "post_investigation_recommendation": (
            "Producer institutional_persistence_consumer + volume EVENT. 2-way "
            "STATE + EVENT. 0 fires reflects vol_spike_2x rarity on ticker with "
            "sustained institutional buy state. LOOSEN vol_spike_2x -> "
            "vol_above_avg."
        ),
        "final_recommended_actions": "[CRITICAL] [LOOSEN_THRESHOLD] vol_spike_2x -> vol_above_avg",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Vol threshold loosening standard pattern per Council 235 recommendations.",
    },
    "institutional_recent_init_volume_long": {
        "post_investigation_verdict": "PRODUCER_OK + EVENT_+_VOLUME_COMPOUND",
        "post_investigation_recommendation": (
            "Producer emits institutional_recent_init (13F holding NEW to top-10 "
            "position). EVENT + volume confirmation. Institutional NEW-initiation "
            "is intrinsically rare (~1-3 per ticker per year). 0 fires = compound "
            "rare EVENT. ACTIONS: (1) LOOSEN vol_spike_2x -> vol_above_avg; "
            "(2) widen 'recent init' window from currently likely 45 days to 90 "
            "days."
        ),
        "final_recommended_actions": "[CRITICAL] [LOOSEN_THRESHOLD] recent_init window 45d -> 90d; vol_spike_2x -> vol_above_avg",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Institutional new-init structural rareness. Gap: recent_init window value not verified from screener.py.",
    },
    "institutional_volume_confirmation_long": {
        "post_investigation_verdict": "PRODUCER_OK + STATE_+_MULTI_CONFIRMATION",
        "post_investigation_recommendation": (
            "Producer + volume + multiple confirmation (RSI + MACD + EMA?). Multi-"
            "confirmation compound = extremely rare joint. ACTIONS: (1) drop 1-2 "
            "confirmation gates as redundant per feedback_obv_avwap_macd_non_"
            "redundancy; (2) LOOSEN vol threshold."
        ),
        "final_recommended_actions": "[CRITICAL] [DROP_REDUNDANT] 1-2 confirmation gates; [LOOSEN_THRESHOLD] vol threshold",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Multi-confirmation compound rareness. Gap: specific gate stack not enumerated - screener.py inspection needed to identify which confirmations are actually stacked.",
    },
    # ========== NEWS REVERSAL FAMILY (3) ==========
    "news_momentum_short": {
        "post_investigation_verdict": "PRODUCER_OK + B832_SPOF + PATTERN_S",
        "post_investigation_recommendation": (
            "Symmetric SHORT mirror of news_momentum_long (Turn 4 investigated). "
            "Inherits B832 SPOF finding (BUG-280) + Pattern S SHORT + borrow_ok. "
            "Same LOOSEN path: audit polygon news coverage; loosen sentiment "
            "thresholds; drop AVWAP redundancy."
        ),
        "final_recommended_actions": "[CRITICAL] [AUDIT_DATA] B832 SPOF polygon news coverage; [LOOSEN_THRESHOLD] sentiment thresholds; [DROP_REDUNDANT] AVWAP; [FIX_PRODUCER] borrow_ok",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Symmetric SHORT mirror of Turn 4 investigated news_momentum_long. Same B832 SPOF + Pattern S inheritance. Gap: none.",
    },
    "news_reversal_long": {
        "post_investigation_verdict": "PRODUCER_OK + B832_SPOF + REVERSAL_EVENT_STARVED",
        "post_investigation_recommendation": (
            "Contrarian thesis: LONG entry on strong negative news sentiment (fade "
            "the panic). news_sentiment.py emits news_sentiment_score; strategy "
            "requires sentiment <= -0.3 AND oversold RSI + reversal candle. B832 "
            "SPOF affected + compound-event rareness. ACTIONS: (1) audit polygon "
            "news coverage; (2) LOOSEN sentiment <= -0.3 -> <= -0.15 (Lopez-Lira-"
            "Tang 2023 uses lower magnitudes); (3) drop reversal candle "
            "requirement as redundant with oversold RSI."
        ),
        "final_recommended_actions": "[CRITICAL] [AUDIT_DATA] B832 SPOF; [LOOSEN_THRESHOLD] sentiment<=-0.3 -> <=-0.15; [DROP_REDUNDANT] reversal candle gate",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Contrarian reversal thesis - fades panic. Gap: reversal candle gate specifics not verified.",
    },
    "news_reversal_short": {
        "post_investigation_verdict": "PRODUCER_OK + B832_SPOF + REVERSAL_+_PATTERN_S",
        "post_investigation_recommendation": (
            "Contrarian SHORT thesis: SHORT entry on strong positive news sentiment "
            "(fade euphoria). Same producer + Pattern S + borrow_ok. Same LOOSEN "
            "path as news_reversal_long."
        ),
        "final_recommended_actions": "[CRITICAL] [AUDIT_DATA] B832 SPOF; [LOOSEN_THRESHOLD] sentiment>=+0.3 -> >=+0.15; [FIX_PRODUCER] borrow_ok; Pattern S caveat",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Symmetric SHORT variant of news_reversal_long. Gap: none.",
    },
    # ========== PIVOT FAMILY (3) ==========
    "pivot_r2_continuation": {
        "post_investigation_verdict": "PRODUCER_OK + CONTINUATION_EVENT_STARVED",
        "post_investigation_recommendation": (
            "Producer technical.py compute_pivots emits pivot R1/R2/R3 + S1/S2/S3 "
            "levels + break/reject variants (verified Turn 6 camarilla work). "
            "R2 continuation = price breaks R2 with continuation momentum. 0 fires "
            "reflects R2 breakout rarity + continuation gate compound. ACTIONS: "
            "(1) LOOSEN R2-approach threshold (currently likely 0.5% below R2) to "
            "1.0%; (2) drop RSI confirmation if present; (3) verify continuation "
            "gate specifics."
        ),
        "final_recommended_actions": "[CRITICAL] [LOOSEN_THRESHOLD] R2 approach 0.5% -> 1.0%; [DROP_REDUNDANT] RSI confirmation",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Producer already verified Turn 6. Gap: R2 approach threshold specific value not verified from screener.py.",
    },
    "pivot_r3_blowoff_short": {
        "post_investigation_verdict": "PRODUCER_OK + EXPLORATORY_B645 + PATTERN_S",
        "post_investigation_recommendation": (
            "Batch 645 NEW Class 7 marked EXPLORATORY pending Stage 5 cube "
            "empirical validation. Compound: recent_blowoff_at_r3 (5-bar window) "
            "+ bearish reversal trigger + Pattern S. Producer works but structural "
            "rareness of Wyckoff Buying Climax + Upthrust-Test sequence. STATUS_"
            "QUO on EXPLORATORY marker per feedback_minimum_fire_count_gate_before_"
            "cube - cube can't produce statistical verdict at <30 fires. Universe "
            "expansion primary lever."
        ),
        "final_recommended_actions": "[CRITICAL] [STATUS_QUO] EXPLORATORY marker per B645; [UNIVERSE_EXPAND] Batch B primary lever; [FIX_PRODUCER] borrow_ok audit",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Batch 645 EXPLORATORY - deliberate deferral pending Stage 5. Producer works but structural low-fire. Gap: none - explicit EXPLORATORY status per feedback.",
    },
    "pivot_s3_capitulation": {
        "post_investigation_verdict": "PRODUCER_OK + EXPLORATORY_B643 + WYCKOFF_SPRING",
        "post_investigation_recommendation": (
            "Batch 643 REDESIGNED per owner directive - buys the TURN not the "
            "FALL per Wyckoff Spring/Test. Producer emits recent_capitulation_at_"
            "s3 (5-bar window) + reversal trigger + vol_below_avg (B650 canonical "
            "Test bar). B643 measured 18.3/yr universe-wide FAIL_FIRE_STARVED but "
            "owner directive keep EXPLORATORY. STATUS_QUO. Universe expansion + "
            "Stage 5 cube verdict."
        ),
        "final_recommended_actions": "[CRITICAL] [STATUS_QUO] EXPLORATORY marker per B643; [UNIVERSE_EXPAND] Batch B; Stage 5 cube verdict pending",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1123 Turn 9. Batch 643 EXPLORATORY per owner directive W5-i 2026-06-09. Producer redesigned for Wyckoff Spring/Test. Gap: none - explicit EXPLORATORY status.",
    },
}


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    # Force text columns to object dtype
    for col in ("execution_batch_ref", "execution_status", "execution_comments"):
        if col in df.columns:
            df[col] = df[col].astype("object").fillna("")

    updated = 0
    for strat, data in TURN_9_INVESTIGATIONS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found in CSV")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    df.to_csv(csv_path, index=False)

    total = len(df)
    pop = (df["post_investigation_verdict"].fillna("").str.len() > 0).sum()

    print(f"Turn 9 CRITICAL producer investigation complete: {updated} strategies.")
    print(f"Total investigated: {pop} of {total} (63 + {updated} = 83)")
    print()
    print("EXECUTION_STATUS DISTRIBUTION (post-Turn-9):")
    for status in sorted(df["execution_status"].unique()):
        n = (df["execution_status"] == status).sum()
        print(f"  {status:30s}: {n:3d}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
