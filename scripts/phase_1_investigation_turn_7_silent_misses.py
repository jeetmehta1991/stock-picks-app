#!/usr/bin/env python
"""Council 240 (2026-07-03) Turn 7: 11 silent-miss strategies investigation.

SCOPE: 11 strategies with chat-surfacing in Turn 1-6 but no CSV verdict.

FAMILY INHERITANCE (6):
  Triangle family (BUG-277):    triangle_descending_short
  Calendar B723 family (BUG-279): totm_long, pre_holiday_long
  Index rebalance (BUG-278):    post_inclusion_drift_long,
                                post_inclusion_reversal_short,
                                pre_rebalance_long

FRESH PRODUCER INVESTIGATION (5):
  double_bottom_long (NEW BUG-281)
  smc_ote_long, smc_ote_short
  smc_premium_short, smc_fvg_retest_short

ADDITIONAL COLUMN: execution_comments
  Free-form text describing what actions were executed + any misses/gaps.
  Populated for all 46+11=57 investigated strategies this turn.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


TURN_7_INVESTIGATIONS = {
    # ========== FAMILY INHERITANCE (6) ==========
    # Triangle family (BUG-277)
    "triangle_descending_short": {
        "post_investigation_verdict": "PRODUCER_DEPENDENT_ON_TRIANGLE_DETECTOR (BUG-277 family)",
        "post_investigation_recommendation": (
            "Inherits BUG-277: chart_patterns.py:347 detect_triangle fires 0% on SPY "
            "2020-2026 sample. Symmetric SHORT mirror of triangle_ascending_long added "
            "B685 per Bulkowski 2005 canonical. Producer bug (or SPY-only structural "
            "absence) cascades to this strategy. Same fix path as triangle_ascending_"
            "long: widen flat-top tolerance OR restrict to small-cap subset. Pattern S "
            "SHORT asymmetric expectancy caveat also applies + borrow_ok audit."
        ),
        "final_recommended_actions": "[CRITICAL] [FIX_PRODUCER] Inherits BUG-277 detect_triangle 0-fire fix (widen flat-top tolerance); [FIX_PRODUCER] borrow_ok audit; [UNIVERSE_EXPAND] Batch B",
        "execution_status": "BLOCKED_PRODUCER_BUG",
        "execution_batch_ref": "",
        "execution_comments": "B1120 pre-classified as BLOCKED_PRODUCER_BUG (BUG-277 family inheritance). B1121 turn 7 confirmed via family binding to triangle_ascending_long (same producer chart_patterns.py:347 detect_triangle). Will unblock when BUG-277 fixed in B1123. Gap: SHORT-side may need per-strategy verification post-fix if borrow_ok audit surfaces additional blocking.",
    },
    # Calendar B723 family (BUG-279)
    "totm_long": {
        "post_investigation_verdict": "PRODUCER_LIKELY_BUG_OR_PLUMBING (BUG-279 family)",
        "post_investigation_recommendation": (
            "Inherits BUG-279: calendar_effects.py @lru_cache on _cached_calendar_"
            "signals causing 300-400x underfire on B723 EVENT-converted calendar "
            "strategies. TOTM (Turn Of The Month) first-day EVENT emitted via "
            "compute_calendar_signals. Expected ~4300 fires (10 TOTM days/yr x 4y x "
            "150 tickers x ~72% EMA200 pass); actual 12 = 360x underfire. Same class "
            "as halloween_seasonal_long. Runtime probe: check trade_log.csv for ANY "
            "TOTM strategy fires on last-1-BD OR first-3-BD of month across 4-year "
            "window. If ZERO = plumbing broken. Discriminate cache-invalidation vs "
            "tdm calculation edge case."
        ),
        "final_recommended_actions": "[CRITICAL] [FIX_PRODUCER] Inherits BUG-279 calendar @lru_cache 300x underfire fix; runtime probe first-3-BD-of-month dates; discriminate cache vs tdm root cause",
        "execution_status": "BLOCKED_PRODUCER_BUG",
        "execution_batch_ref": "",
        "execution_comments": "B1120 pre-classified as BLOCKED_PRODUCER_BUG (BUG-279 family). B1121 turn 7 confirmed via family binding to halloween_seasonal_long (same calendar_effects.py producer + same @lru_cache decorator). 360x underfire vs halloween's 300x = consistent family pattern. Will unblock when BUG-279 fixed in B1122. Gap: no runtime probe yet on Batch A trade_log for TOTM-specific dates - discriminator between cache-invalidation and tdm-edge-case root cause pending.",
    },
    "pre_holiday_long": {
        "post_investigation_verdict": "PRODUCER_LIKELY_BUG_OR_PLUMBING (BUG-279 family)",
        "post_investigation_recommendation": (
            "Inherits BUG-279: calendar_effects.py @lru_cache underfire pattern. "
            "pre_holiday_long uses is_pre_holiday signal from same producer. Expected "
            "~10 pre-holiday events/yr (day before US federal + Christmas + NYE) x 4y "
            "x 150 tickers x ~50% EMA200 = ~750 potential fires; actual 6 = 125x "
            "underfire. Consistent with halloween 300x + totm 360x = calendar_effects "
            "producer or plumbing systematically underfires. Same family fix path."
        ),
        "final_recommended_actions": "[HIGH] [FIX_PRODUCER] Inherits BUG-279 calendar @lru_cache fix; probe pre-holiday dates in Batch A trade_log; family-wide fix",
        "execution_status": "BLOCKED_PRODUCER_BUG",
        "execution_batch_ref": "",
        "execution_comments": "B1120 pre-classified BLOCKED_PRODUCER_BUG (BUG-279 family). B1121 turn 7 confirmed - is_pre_holiday emitted by same calendar_effects.py compute_calendar_signals producer. 125x underfire consistent with family pattern (halloween 300x + totm 360x + pre_holiday 125x). Will unblock when BUG-279 fixed in B1122. Gap: pre-holiday date list (US federal + Christmas + NYE) not enumerated - producer smoke test in B1121 should verify each holiday-1BD fires.",
    },
    # Index rebalance (BUG-278)
    "post_inclusion_drift_long": {
        "post_investigation_verdict": "DATA_FILE_MISSING (BUG-278 family)",
        "post_investigation_recommendation": (
            "Inherits BUG-278: data_prefetch/derived/index_rebalance_events.parquet "
            "MISSING. Producer index_rebalance.py compute_index_rebalance_signals "
            "reads from expected parquet path; parquet does not exist. Producer "
            "gracefully no-ops per docstring. Strategy fires 0 signals structurally "
            "until Sprint 5 DEC-380 corp actions Polygon feed prefetch lands. Same "
            "family as post_deletion_drift_short (Turn 6 primary investigation)."
        ),
        "final_recommended_actions": "[CRITICAL] [DISABLED_PENDING_DATA] Inherits BUG-278 index_rebalance parquet missing; Sprint 5 DEC-380 corp actions prefetch dependency",
        "execution_status": "BLOCKED_DATA_MISSING",
        "execution_batch_ref": "",
        "execution_comments": "B1120 pre-classified BLOCKED_DATA_MISSING (BUG-278 family). B1121 turn 7 confirmed via family binding to post_deletion_drift_short (same producer + same missing parquet). Will unblock when Sprint 5 DEC-380 corp actions prefetch lands. Gap: alternative implementation path not evaluated - could use Polygon /v3/reference/tickers events feed OR could defer as STRATEGIES_DISABLED_MISSING_PRODUCER per B975 precedent.",
    },
    "post_inclusion_reversal_short": {
        "post_investigation_verdict": "DATA_FILE_MISSING (BUG-278 family)",
        "post_investigation_recommendation": (
            "Inherits BUG-278 same as post_inclusion_drift_long + adds Pattern S "
            "SHORT asymmetric expectancy caveat + borrow_ok audit. 9 fires despite "
            "producer no-op is anomaly - suggests strategy MAY have fallback signal "
            "path from another producer (grep screener.py for actual gate stack)."
        ),
        "final_recommended_actions": "[CRITICAL] [DISABLED_PENDING_DATA] Inherits BUG-278; [AUDIT_DATA] why 9 fires if producer no-op - probe strategy gate stack; [FIX_PRODUCER] borrow_ok",
        "execution_status": "BLOCKED_DATA_MISSING",
        "execution_batch_ref": "",
        "execution_comments": "B1120 pre-classified BLOCKED_DATA_MISSING (BUG-278 family). B1121 turn 7 confirmed via family binding. ANOMALY SURFACED: 9 fires despite producer no-op suggests either (a) another producer emits the signal used by this strategy, (b) 9 fires are from earlier producer state before parquet went missing, or (c) fallback signal path. Gap: strategy gate stack not verified against screener.py to identify signal source of the 9 fires - requires B1121 grep for strategy's gate list.",
    },
    "pre_rebalance_long": {
        "post_investigation_verdict": "DATA_FILE_MISSING (BUG-278 family)",
        "post_investigation_recommendation": (
            "Inherits BUG-278. 0 fires consistent with producer no-op. Awaits Sprint "
            "5 DEC-380 corp actions Polygon feed prefetch. Same disposition as "
            "post_deletion_drift_short + post_inclusion_drift_long."
        ),
        "final_recommended_actions": "[CRITICAL] [DISABLED_PENDING_DATA] Inherits BUG-278; Sprint 5 corp actions prefetch dependency",
        "execution_status": "BLOCKED_DATA_MISSING",
        "execution_batch_ref": "",
        "execution_comments": "B1120 pre-classified BLOCKED_DATA_MISSING (BUG-278 family). B1121 turn 7 confirmed - 0 fires matches producer no-op behavior exactly. Will unblock when Sprint 5 lands OR when strategy is officially DISABLED per B975 precedent. Gap: none - fully consistent with family pattern.",
    },
    # ========== FRESH PRODUCER INVESTIGATION (5) ==========
    "double_bottom_long": {
        "post_investigation_verdict": "PRODUCER_LIKELY_BROKEN (NEW BUG-281)",
        "post_investigation_recommendation": (
            "Producer chart_patterns.py:131 detect_double_top_bottom. Empirical fire "
            "rate 0/57 SPY samples 2020-2026 (same 0% pattern as detect_triangle in "
            "Turn 5). Bulkowski 2005 cites ~10-20 double bottom events/yr per ticker "
            "in bull markets. Expected 150 x 4y x 10/yr = 6,000 signal-events; "
            "actual 0. Same class as BUG-277 triangle detector - CLASSIFY AS NEW "
            "BUG-281. Discriminate producer bug vs SPY-only structural absence by "
            "running detector on 20-ticker Batch A subset with mid-cap volatile "
            "names. ACTIONS: (1) URGENT audit detect_double_top_bottom across Batch "
            "A tickers - if 0-1 fires universe-wide = PRODUCER BROKEN; (2) if "
            "producer needs loosening, widen the bottom-similarity tolerance from "
            "strict to 'nearly-equal within N%'; (3) verify neckline calculation."
        ),
        "final_recommended_actions": "[CRITICAL] [FIX_PRODUCER] URGENT audit detect_double_top_bottom - 0 fires SPY 6y like triangle detector; [LOOSEN_THRESHOLD] widen bottom-similarity tolerance; [UNIVERSE_EXPAND] mid-cap subset",
        "execution_status": "BLOCKED_PRODUCER_BUG",
        "execution_batch_ref": "",
        "execution_comments": "B1121 turn 7 NEW INVESTIGATION - registered as BUG-281 in BUG_REGISTER.md same turn. Chat surfacing Turn 5 said 'DOUBLE BOTTOM DETECTOR FIRES 0% on SPY sample' but was NOT included in Turn 5 investigation script (silent miss caught by Council 238 audit). Now BLOCKED_PRODUCER_BUG pending B1123 producer smoke test + B1122 producer fix. Gap: detector not yet run on non-SPY Batch A tickers to discriminate producer-bug vs SPY-structural-absence.",
    },
    "smc_ote_long": {
        "post_investigation_verdict": "PRODUCER_OK + SMC_PHASE_LATENT_RISK",
        "post_investigation_recommendation": (
            "Producer smc_ict.py emits ote_long via Optimal Trade Entry Fibonacci "
            "62-79% retracement zone (ICT/joshyattridge library). 14 fires quiet-"
            "fire zone. Same SMC_PHASE latent-kill risk as Turn 3 investigated SMC "
            "siblings - if SMC_PHASE != 'PRODUCTION', producer silently returns "
            "empty dict. ACTIONS: (1) verify SMC_PHASE='PRODUCTION' env flag set "
            "for Batch A execution; (2) LOOSEN Fibonacci band 62-79% -> 60-82% per "
            "ICT canonical variance; (3) drop secondary trend confirmation gate; "
            "(4) UNIVERSE_EXPAND Batch B."
        ),
        "final_recommended_actions": "[HIGH] [AUDIT_DATA] Verify SMC_PHASE='PRODUCTION' (silent-kill risk); [LOOSEN_THRESHOLD] Fib band 62-79% -> 60-82% ICT canonical; [LOOSEN_GATE] drop trend confirmation",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1121 turn 7 investigation - was silent miss from Turn 3 (Turn 3 script said 14 SMC investigated but only 10 populated CSV verdicts). Producer verified via smc_ict.py compute_smc_signals emits ote_long key (empirical Turn 3 sanity: 28 signals emitted for SPY). Gap: OTE Fibonacci band variance across ICT sources not enumerated (60-82% is one canonical variant; other Michael J. Huddleston sources use 61.8-78.6%). LOOSEN_THRESHOLD B1126 grouped batch will pick specific band.",
    },
    "smc_ote_short": {
        "post_investigation_verdict": "PRODUCER_OK + SMC_PHASE_LATENT_RISK + PATTERN_S",
        "post_investigation_recommendation": (
            "Symmetric SHORT mirror of smc_ote_long. Same producer + SMC_PHASE risk "
            "+ Pattern S SHORT asymmetric expectancy caveat + borrow_ok audit. 11 "
            "fires reflects SHORT-side structural expectancy on equity upward drift. "
            "Same LOOSEN + AUDIT actions as smc_ote_long."
        ),
        "final_recommended_actions": "[HIGH] [AUDIT_DATA] SMC_PHASE flag; [LOOSEN_THRESHOLD] Fib band 62-79% -> 60-82%; [FIX_PRODUCER] borrow_ok audit; Pattern S caveat",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1121 turn 7 investigation - silent miss from Turn 3. Symmetric SHORT mirror of smc_ote_long with same producer + SMC_PHASE risk. Gap: 11 vs 14 delta for LONG partly explained by Pattern S but also possibly by borrow_ok blocking - correlate with Turn 1 ichimoku_cloud_breakdown finding in B1125 borrow_ok blocking-rate audit.",
    },
    "smc_premium_short": {
        "post_investigation_verdict": "PRODUCER_OK + SMC_PHASE_LATENT_RISK + PATTERN_S",
        "post_investigation_recommendation": (
            "Producer smc_ict.py smc_in_premium_zone via dealing_range_pct > 0.5. "
            "Symmetric SHORT of smc_discount_long (Turn 3 investigated). 10 fires "
            "reflects 3-way AND (premium zone + Pattern S SHORT + borrow_ok). Same "
            "LOOSEN threshold + SMC_PHASE audit as smc_discount_long: widen "
            "dealing_range_pct > 0.5 -> > 0.4 for premium zone; drop structure "
            "gate; borrow_ok audit."
        ),
        "final_recommended_actions": "[HIGH] [AUDIT_DATA] SMC_PHASE flag; [LOOSEN_THRESHOLD] dealing_range_pct > 0.5 -> > 0.4; [FIX_PRODUCER] borrow_ok; [DROP_REDUNDANT] structure gate",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1121 turn 7 investigation - silent miss from Turn 3. Symmetric SHORT mirror of Turn 3 investigated smc_discount_long. Same producer + same LOOSEN_THRESHOLD approach mirrored. Gap: none - fully aligned with LONG sibling investigation.",
    },
    "smc_fvg_retest_short": {
        "post_investigation_verdict": "PRODUCER_OK + SMC_PHASE_LATENT_RISK + FVG_ZONE_RARE + PATTERN_S",
        "post_investigation_recommendation": (
            "Producer smc_ict.py:217 emits retest_short_zone when price IN un-"
            "mitigated bearish FVG zone. Symmetric SHORT of smc_fvg_retest_long "
            "(Turn 3 investigated). 8 fires vs LONG 1 fire = SHORT actually fires "
            "MORE (contrary to Pattern S SHORT typical expectancy) suggests bearish "
            "FVG zones more prevalent than bullish in 2022-2026 window (bearish "
            "sessions 2022 + Jul-Oct 2023 + Aug 2024). ACTIONS: same as fvg_retest_"
            "long: SMC_PHASE audit; widen FVG un-mitigated zone entry tolerance; "
            "borrow_ok."
        ),
        "final_recommended_actions": "[HIGH] [AUDIT_DATA] SMC_PHASE flag; [LOOSEN_THRESHOLD] widen FVG un-mitigated zone entry tolerance; [FIX_PRODUCER] borrow_ok",
        "execution_status": "PENDING",
        "execution_batch_ref": "",
        "execution_comments": "B1121 turn 7 investigation - silent miss from Turn 3. Interesting anomaly: SHORT (8 fires) > LONG (1 fire) contrary to Pattern S caveat, explained by 2022-2026 window having 2-3 significant bearish sessions where bearish FVG zones formed more than bullish. Gap: FVG zone tolerance widening magnitude not specified - B1126 grouped batch will pick based on producer inspection.",
    },
}


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    # Force text columns to object dtype (fix float64 coercion on empty cols)
    for col in ("execution_batch_ref", "execution_status", "execution_comments"):
        if col in df.columns:
            df[col] = df[col].astype("object").fillna("")

    # Add execution_comments column if not present
    if "execution_comments" not in df.columns:
        df["execution_comments"] = ""

    # Update columns for the 11 investigated strategies
    updated = 0
    for strat, data in TURN_7_INVESTIGATIONS.items():
        mask = df["strategy_name"] == strat
        if not mask.any():
            print(f"WARN: {strat} not found in CSV")
            continue
        for col, val in data.items():
            df.loc[mask, col] = val
        updated += 1

    # Backfill execution_comments for the 46 Turn 1-6 investigated strategies
    _TURN_1_6_BACKFILL = (
        "Investigation complete in Turns 1-6 (B1112-B1117) with producer verification "
        "via live runtime probes. No execution actions taken yet - final_recommended_"
        "actions column captures required loosening/fix/audit directives. Status "
        "remains PENDING (or BLOCKED_* if family-inheritance). Awaits sequenced "
        "execution per Council 238 remediation plan (B1122-B1133). Gaps captured in "
        "post_investigation_recommendation column."
    )
    for _, r in df.iterrows():
        strat = r["strategy_name"]
        verdict = str(r.get("post_investigation_verdict", ""))
        current_comments = str(r.get("execution_comments", ""))
        # Populate ONLY if verdict populated AND comments empty AND not Turn 7
        if (
            verdict
            and verdict.lower() != "nan"
            and (not current_comments or current_comments.lower() == "nan")
            and strat not in TURN_7_INVESTIGATIONS
        ):
            df.loc[df["strategy_name"] == strat, "execution_comments"] = (
                _TURN_1_6_BACKFILL
            )

    # Backfill execution_comments for the 135 PENDING un-investigated strategies
    _PENDING_BACKFILL = (
        "No investigation yet - PENDING per Council 235 pre-investigation analysis "
        "only (B1097-B1109). recommendation column contains loosening/action directive "
        "derived from producer signals + fire class + regime affinity. Awaits either "
        "(a) per-strategy investigation if quiet-fire / starved concern requires "
        "producer verification, OR (b) direct execution per final_recommended_actions "
        "in grouped LOOSEN batches B1126-B1131."
    )
    for _, r in df.iterrows():
        strat = r["strategy_name"]
        verdict = str(r.get("post_investigation_verdict", ""))
        current_comments = str(r.get("execution_comments", ""))
        if (
            (not verdict or verdict.lower() == "nan")
            and (not current_comments or current_comments.lower() == "nan")
        ):
            df.loc[df["strategy_name"] == strat, "execution_comments"] = (
                _PENDING_BACKFILL
            )

    df.to_csv(csv_path, index=False)

    # Report
    print(f"Turn 7 silent-miss investigation complete: {updated} strategies updated.")
    print()
    print("EXECUTION_STATUS DISTRIBUTION:")
    for status in sorted(df["execution_status"].unique()):
        n = (df["execution_status"] == status).sum()
        print(f"  {status:30s}: {n:3d}")
    print()
    total = len(df)
    pop = (df["post_investigation_verdict"].fillna("").str.len() > 0).sum()
    exec_pop = (df["execution_comments"].fillna("").str.len() > 0).sum()
    print(
        f"Total rows: {total} | Investigated: {pop} (46+11=57) | "
        f"execution_comments populated: {exec_pop}"
    )
    print()
    print("CSV COLUMNS NOW (23 total):")
    for col in df.columns:
        print(f"  {col}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
