#!/usr/bin/env python
"""Council 237 (2026-07-03): Add final_recommended_actions column.

Per owner directive: 'All quiet and starved strategies need to be loosened'.
Merge post_investigation_recommendation (46 strategies) + recommendation
(146 strategies) into single terse actionable column.

FORMAT: [PRIORITY_TIER] [ACTION_CLASS] specific_directive; [SECONDARY]
  PRIORITY_TIER: CRITICAL (0 fires) / HIGH (1-15) / MED (16-30) / MARGINAL (>30)
  ACTION_CLASS:
    LOOSEN_GATE        - drop / weaken gates (default per owner directive)
    LOOSEN_THRESHOLD   - widen numeric bounds
    DROP_REDUNDANT     - remove collinear signal per feedback_avwap_redundant
    EVENT_TO_STATE     - reverse B725/B723 tightening (owner-directed loosen)
    FIX_PRODUCER       - producer bug requires code-side fix (loosen post-fix)
    AUDIT_DATA         - upstream data coverage audit (loosen post-audit)
    UNIVERSE_EXPAND    - Batch B primary lever (also loosen per owner)
    DISABLED_PENDING_DATA - blocked by missing prefetch parquet

INVESTIGATED (Turn 1-6 findings): use post_investigation_recommendation.
NON-INVESTIGATED (146 rows): parse recommendation column for LOOSEN/DROP verbs.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


# Hand-crafted concise directives for INVESTIGATED strategies (Turn 1-6).
# Bypasses regex parse of long paragraphs; owner gets 1-line action.
INVESTIGATED_ACTIONS = {
    # Turn 1 - Ichimoku
    "ichimoku_cloud_breakout": "[HIGH] [LOOSEN_GATE] Drop rsi_14<70 + volume_above_avg secondary gates (B725 EVENT is sufficient); [AUDIT_DATA] verify Ichimoku producer wired post-B725",
    "ichimoku_cloud_breakdown": "[CRITICAL] [FIX_PRODUCER] Audit _short_borrow_trap_active blocking rate (SHORT under-fires); [LOOSEN_GATE] drop rsi_14>30 secondary",
    "ichimoku_tk_cross": "[HIGH] [LOOSEN_GATE] Drop cloud_position redundant gate (TK cross carries direction); [DROP_REDUNDANT] price_above_ema_50 vs cloud_bullish",
    # Turn 2 - BB / Squeeze / Halloween
    "bb_squeeze_volume": "[CRITICAL] [LOOSEN_THRESHOLD] vol_spike_2x -> vol_above_avg (Bollinger 1992 canonical); [DROP_REDUNDANT] above_vwap (squeeze direction confirms)",
    "bollinger_tight": "[HIGH] [LOOSEN_THRESHOLD] rsi_14 threshold VIX-conditional 45/55 -> 40/60 Connors canonical; [AUDIT_DATA] verify bb_20_15 variant emits proportionally to bb_20_20",
    "squeeze_breakout": "[MARGINAL] [UNIVERSE_EXPAND] Structural 0.065/ticker/yr - Batch B primary lever; [LOOSEN_GATE] add secondary tier boost on squeeze_fire_up",
    "halloween_seasonal_long": "[CRITICAL] [FIX_PRODUCER] URGENT audit calendar_effects.py @lru_cache on _cached_calendar_signals (300x underfire); [FIX_PRODUCER] probe trade_log for any strategy fires on 2022-11-01/2023-11-01/2024-11-01/2025-11-03",
    # Turn 3 - SMC (10 populated + 1 ichimoku_tk_cross above)
    "smc_mitigation_block_long": "[CRITICAL] [AUDIT_DATA] Verify SMC_PHASE='PRODUCTION' env flag (silent-kill risk on all SMC); [LOOSEN_GATE] widen OB-zone tolerance band; [UNIVERSE_EXPAND]",
    "smc_bos_continuation": "[MED] [AUDIT_DATA] SMC_PHASE flag; [LOOSEN_GATE] drop B278 vol_confirms + rsi_direction_aligned secondaries (B278 empirically-justified but starving)",
    "smc_equal_highs_sweep_short": "[MED] [AUDIT_DATA] SMC_PHASE flag; [FIX_PRODUCER] borrow_ok audit (Pattern S asymmetric); [LOOSEN_GATE] drop volume secondary",
    "smc_liquidity_sweep_reversal": "[HIGH] [AUDIT_DATA] SMC_PHASE flag; [LOOSEN_GATE] widen dual-gate compound (liquidity_swept_dn AND (choch OR bos)) - break AND into OR",
    "smc_discount_long": "[HIGH] [AUDIT_DATA] SMC_PHASE flag; [LOOSEN_THRESHOLD] widen dealing_range_pct < 0.5 -> < 0.6 for discount zone; [DROP_REDUNDANT] structure gate",
    "smc_fvg_retest_long": "[HIGH] [AUDIT_DATA] SMC_PHASE flag; [LOOSEN_THRESHOLD] widen FVG un-mitigated zone entry tolerance; [UNIVERSE_EXPAND]",
    "smc_mitigation_block_short": "[HIGH] [AUDIT_DATA] SMC_PHASE flag; [FIX_PRODUCER] borrow_ok audit (Pattern S); [LOOSEN_GATE] widen OB-zone tolerance",
    "smc_choch_reversal": "[MARGINAL] [AUDIT_DATA] SMC_PHASE flag; [UNIVERSE_EXPAND] B273 90-bar recency justified; Batch B primary lever",
    "smc_bos_retest_entry": "[MARGINAL] [AUDIT_DATA] SMC_PHASE flag; [LOOSEN_THRESHOLD] 0.5% retest tolerance -> 1.0%; [UNIVERSE_EXPAND]",
    "smc_equal_lows_sweep_long": "[MARGINAL] [AUDIT_DATA] SMC_PHASE flag; [LOOSEN_THRESHOLD] liquidity_range_pct 0.01 -> 0.02; [UNIVERSE_EXPAND]",
    # Turn 4 - News / PEAD
    "news_momentum_long": "[CRITICAL] [AUDIT_DATA] URGENT B832 SPOF tripped Batch A - audit data_prefetch/polygon/news coverage; [LOOSEN_THRESHOLD] sentiment>=+0.5 -> +0.3, zscore>=+1.5 -> +1.0; [DROP_REDUNDANT] AVWAP per feedback_avwap_redundant",
    "news_sentiment_long": "[HIGH] [AUDIT_DATA] B832 SPOF audit polygon news coverage; [LOOSEN_THRESHOLD] sentiment_mean 0.5 -> 0.3 (Lopez-Lira-Tang 2023)",
    "pead_long": "[HIGH] [LOOSEN_THRESHOLD] ann_return >=+2% -> >=+1% (Garfinkel 2024 canonical); [AUDIT_DATA] polygon/financials coverage across Batch A",
    "pead_short": "[MARGINAL] [UNIVERSE_EXPAND] Structural at min-trades floor; [LOOSEN_GATE] status quo on 2-gate lean structure",
    # Turn 5 - Chart pattern
    "cup_and_handle_long": "[CRITICAL] [LOOSEN_THRESHOLD] vol_spike_2x -> vol_above_avg (O'Neil CANSLIM canonical); [DROP_REDUNDANT] rsi_14<70 redundant with EMA trend",
    "flag_bull_long": "[CRITICAL] [FIX_PRODUCER] Widen K bar-window 1..8 -> 1..15 (Edwards-Magee 1-4wk); [UNIVERSE_EXPAND] Batch B mid-cap coverage",
    "flag_bull_retest_long": "[CRITICAL] [FIX_PRODUCER] Widen retest tolerance band; K 3..12 -> 3..15; [UNIVERSE_EXPAND]",
    "triangle_ascending_long": "[CRITICAL] [FIX_PRODUCER] URGENT audit detect_triangle producer - 0 fires SPY 6y likely BROKEN; [LOOSEN_THRESHOLD] widen flat-top tolerance strict-flat -> nearly-flat-within-N%",
    "triangle_ascending_retest_long": "[CRITICAL] [FIX_PRODUCER] Inherits triangle_ascending detector bug; fix upstream first",
    "cup_and_handle_retest_long": "[MED] [LOOSEN_THRESHOLD] Widen retest tolerance band 1% -> 2%; [UNIVERSE_EXPAND] Batch B primary lever",
    # Turn 6 FINAL
    "post_deletion_drift_short": "[CRITICAL] [DISABLED_PENDING_DATA] Missing data_prefetch/derived/index_rebalance_events.parquet - blocked until Sprint 5 DEC-380 corp actions prefetch lands",
    "avwap_252_breakout": "[MED] [LOOSEN_THRESHOLD] vol_spike_15x (1.5x) -> vol_above_avg (Shannon 2022 canonical); [DROP_REDUNDANT] extreme-overbought RSI filter",
    "donchian_breakdown_retest_short": "[HIGH] [UNIVERSE_EXPAND] B682 vol_below_avg justified per Bulkowski; Batch B primary lever; [FIX_PRODUCER] borrow_ok audit",
    "squeeze_setup_long": "[CRITICAL] [AUDIT_DATA] URGENT FINRA short_interest prefetch coverage across Batch A; [UNIVERSE_EXPAND] Batch B / T3 high-SI names",
    "break_retest_confluence": "[MED] [UNIVERSE_EXPAND] Post-B617 empirically-justified; Batch B primary lever",
    "cpr_narrow_momentum": "[MED] [UNIVERSE_EXPAND] B718 tightening empirically-justified (S4-B717 ceiling); Batch B primary lever",
    "52w_low_breakdown_pullback_short": "[HIGH] [UNIVERSE_EXPAND] Batch B distressed-name coverage; [FIX_PRODUCER] borrow_ok audit",
    "xs_low_beta_long": "[HIGH] [UNIVERSE_EXPAND] URGENT Batch B / T3 mid-cap primary lever (S&P 500 majors 1.0+ beta by definition); expect 5-10x uplift",
    "macd_crossover_short": "[HIGH] [FIX_PRODUCER] URGENT audit _short_borrow_trap_active - 10x underfire suggests filter blocks most candidates; [UNIVERSE_EXPAND]",
    "52w_high_breakout": "[HIGH] [UNIVERSE_EXPAND] B697 empirically-justified; Batch B primary lever",
    "52w_high_breakout_pullback_long": "[HIGH] [LOOSEN_THRESHOLD] Widen 1% proximity -> 2%; extend 10d recency -> 20d",
    "golden_cross_50_200": "[HIGH] [UNIVERSE_EXPAND] Structural 1-2/yr per ticker; [FIX_PRODUCER] borrow_ok audit on SHORT (death_cross)",
    "golden_cross_20_50": "[HIGH] [DROP_REDUNDANT] Drop 200-EMA regime gate (EMA 20/50 cross IS trend direction per feedback_avwap_redundant precedent); expect 3-5x uplift",
    "adx_initiation": "[CRITICAL] [LOOSEN_THRESHOLD] adx>25 -> adx>20 (broader trend initiation); [UNIVERSE_EXPAND]",
    "camarilla_r4_breakout": "[MARGINAL] [FIX_PRODUCER] Verify Camarilla R4/S4 emit post-B641 rename; [LOOSEN_THRESHOLD] volume threshold if present",
}


# Regex extractors for the NON-INVESTIGATED 146 rows.
_LOOSEN_RE = re.compile(
    r"(LOOSEN[:\s]+[^.;]+[.;])|(DROP[:\s]+[^.;]+[.;])|(REMOVE[:\s]+[^.;]+[.;])"
    r"|(WIDEN[:\s]+[^.;]+[.;])|(REPLACE[:\s]+[^.;]+[.;])",
    re.IGNORECASE,
)


def _priority_tier(n_fires: int) -> str:
    """Assign priority tier based on fire count."""
    if n_fires == 0:
        return "CRITICAL"
    if n_fires <= 15:
        return "HIGH"
    if n_fires <= 30:
        return "MED"
    return "MARGINAL"


def _extract_action(recommendation: str) -> str:
    """Extract terse action items from a recommendation paragraph."""
    if not isinstance(recommendation, str) or not recommendation:
        return "[LOOSEN_GATE] no upstream recommendation - manual review required"

    # Find LOOSEN / DROP / WIDEN / REPLACE clauses
    matches = _LOOSEN_RE.findall(recommendation)
    clauses = [c for tup in matches for c in tup if c][:3]

    if clauses:
        # Trim to concise form
        concise = "; ".join(c.strip().rstrip(".;") for c in clauses)
        # Cap length
        if len(concise) > 400:
            concise = concise[:397] + "..."
        return f"[LOOSEN_GATE] {concise}"

    # Fallback: first 2 sentences of recommendation
    sentences = re.split(r"[.;](?:\s|$)", recommendation)
    trimmed = ". ".join(s.strip() for s in sentences[:2] if s.strip())
    if len(trimmed) > 400:
        trimmed = trimmed[:397] + "..."
    return f"[LOOSEN_GATE] {trimmed}"


def _classify_row(row: pd.Series) -> str:
    """Emit final_recommended_actions text for one strategy row."""
    strat = row["strategy_name"]
    n_fires = int(row.get("n_fires", 0) or 0)
    tier = _priority_tier(n_fires)

    # 1. Investigated strategies use hand-crafted concise directive
    if strat in INVESTIGATED_ACTIONS:
        # Already has tier prefix in the dict; strip and re-prefix with current tier
        raw = INVESTIGATED_ACTIONS[strat]
        # remove existing [TIER] prefix if present
        raw_no_tier = re.sub(r"^\[(CRITICAL|HIGH|MED|MARGINAL)\]\s*", "", raw)
        return f"[{tier}] {raw_no_tier}"

    # 2. Non-investigated: parse the `recommendation` column
    rec = row.get("recommendation", "")
    action = _extract_action(rec)

    # Add universe-expand secondary for MARGINAL (30+ fires)
    if tier == "MARGINAL":
        action = f"{action}; [UNIVERSE_EXPAND] Batch B secondary lever"

    return f"[{tier}] {action}"


def main() -> int:
    csv_path = Path("output_batch_A_150/phase_1_quiet_fire_investigation.csv")
    df = pd.read_csv(csv_path)

    df["final_recommended_actions"] = df.apply(_classify_row, axis=1)

    df.to_csv(csv_path, index=False)

    # Report distribution
    print(f"Added final_recommended_actions column to {len(df)} rows.")
    print()
    print("PRIORITY TIER DISTRIBUTION:")
    for tier in ("CRITICAL", "HIGH", "MED", "MARGINAL"):
        n = df["final_recommended_actions"].str.startswith(f"[{tier}]").sum()
        print(f"  {tier:10s}: {n:3d}")
    print()
    print("ACTION CLASS DISTRIBUTION (primary class):")
    for cls in (
        "LOOSEN_GATE",
        "LOOSEN_THRESHOLD",
        "DROP_REDUNDANT",
        "EVENT_TO_STATE",
        "FIX_PRODUCER",
        "AUDIT_DATA",
        "UNIVERSE_EXPAND",
        "DISABLED_PENDING_DATA",
    ):
        n = df["final_recommended_actions"].str.contains(f"[{cls}]", regex=False).sum()
        print(f"  {cls:22s}: {n:3d}")
    print()
    print("SAMPLE (first 5 investigated):")
    for strat in list(INVESTIGATED_ACTIONS.keys())[:5]:
        row = df[df["strategy_name"] == strat].iloc[0]
        print(f"  {strat}: {row['final_recommended_actions'][:120]}...")
    print()
    print("SAMPLE (first 3 non-investigated):")
    non_inv = df[~df["strategy_name"].isin(INVESTIGATED_ACTIONS.keys())].head(3)
    for _, row in non_inv.iterrows():
        print(f"  {row['strategy_name']}: {row['final_recommended_actions'][:120]}...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
