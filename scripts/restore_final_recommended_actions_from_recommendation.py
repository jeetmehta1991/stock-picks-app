"""B1149 Council 260: Restore final_recommended_actions from recommendation column.

Per owner diagnostic 2026-07-03:
  User pointed out that 52wh_break_retest recommendation column has SPECIFIC
  action "LOOSEN: drop vol_below_avg AND above_avwap_20low" but
  final_recommended_actions column has generic "Drop 1-2 secondary gates
  from 7-gate stack".

ROOT CAUSE:
  Council 243 Turn 9 autonomous loop (B1123) overwrote final_recommended_
  actions for 129 un-investigated strategies with gate-count-based template,
  losing the specificity in the recommendation column.

FIX:
  For strategies currently in SKIP_GENERIC_TEMPLATE_B1145 status:
  Re-extract specific actions from recommendation column and re-populate
  final_recommended_actions with hand-crafted specificity preserved.

PRESERVATION RULES:
  1. Do NOT touch strategies that were investigated (Turn 1-6, 7, 8) -
     their final_recommended_actions has hand-crafted verdicts.
  2. Do NOT touch strategies already DONE_B* - their actions were applied.
  3. Only restore SKIP_GENERIC_TEMPLATE + SKIP_UNCLASSIFIED strategies.
  4. Preserve tier prefix [CRITICAL]/[HIGH]/[MED]/[MARGINAL] based on n_fires.

EXTRACTION LOGIC (mirrors Council 237 B1118 extractor):
  Look for LOOSEN: / DROP: / WIDEN: / REPLACE: clauses in recommendation.
  Extract full sentence-level clauses (not just the verb).
  Result becomes: "[TIER] [LOOSEN_GATE] <extracted specific clauses>"
"""
# Source: per CHECKLIST #77 canonical-source; author Council 260 B1149 2026-07-03
from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd


CSV_PATH = _REPO / "output_batch_A_150" / "phase_1_quiet_fire_investigation.csv"


# LOOSEN / DROP / WIDEN / REPLACE clause extractor (Council 237 B1118 pattern)
_ACTION_RE = re.compile(
    r"(LOOSEN[:\s]+[^.]+(?:\.|$))"
    r"|(DROP[:\s]+[^.]+(?:\.|$))"
    r"|(REMOVE[:\s]+[^.]+(?:\.|$))"
    r"|(WIDEN[:\s]+[^.]+(?:\.|$))"
    r"|(REPLACE[:\s]+[^.]+(?:\.|$))",
    re.IGNORECASE,
)


def _priority_tier(n_fires: int) -> str:
    if n_fires == 0:
        return "CRITICAL"
    if n_fires <= 15:
        return "HIGH"
    if n_fires <= 30:
        return "MED"
    return "MARGINAL"


def _extract_specific_action(recommendation: str, n_fires: int) -> str | None:
    """Extract specific action from recommendation column.

    Returns None if recommendation is empty OR only has generic language.
    """
    if not isinstance(recommendation, str) or not recommendation.strip():
        return None

    matches = _ACTION_RE.findall(recommendation)
    clauses = [c for tup in matches for c in tup if c][:3]

    if not clauses:
        return None

    concise = "; ".join(c.strip().rstrip(".;") for c in clauses)
    if len(concise) > 500:
        concise = concise[:497] + "..."

    tier = _priority_tier(n_fires)
    return f"[{tier}] [LOOSEN_GATE] {concise}"


def main() -> int:
    df = pd.read_csv(CSV_PATH)
    for col in ("execution_status", "final_recommended_actions", "recommendation"):
        if col in df.columns:
            df[col] = df[col].astype("object").fillna("")

    # Only touch SKIP strategies (leave DONE_* and PENDING alone)
    target_statuses = ("SKIP_GENERIC_TEMPLATE_B1145", "SKIP_UNCLASSIFIED_B1145")

    stats = {
        "restored_specific": 0,
        "kept_generic_no_specific_found": 0,
        "not_touched_DONE": 0,
        "not_touched_STATUS_QUO": 0,
        "not_touched_BLOCKED": 0,
        "not_touched_INVESTIGATED": 0,
    }

    # Investigated strategies (Turn 1-6, 7, 8) have HAND-CRAFTED verdicts to preserve.
    # Turn 9 auto-loop verdicts contain "(autonomous per-strategy analysis Turn 9)" - EXCLUDE those.
    # So: hand-crafted = has verdict AND does NOT contain Turn 9 marker
    verdict_col = df["post_investigation_verdict"].fillna("").astype(str)
    has_verdict = verdict_col.str.len() > 0
    is_auto_loop_verdict = verdict_col.str.contains(
        "autonomous per-strategy analysis Turn 9", na=False
    )
    investigated_mask = has_verdict & ~is_auto_loop_verdict

    for idx, row in df.iterrows():
        strat = row["strategy_name"]
        status = str(row.get("execution_status", ""))
        n_fires = int(row.get("n_fires", 0) or 0)
        recommendation = str(row.get("recommendation", ""))

        # Skip non-target statuses
        if status not in target_statuses:
            if status.startswith("DONE_"):
                stats["not_touched_DONE"] += 1
            elif "STATUS_QUO" in status:
                stats["not_touched_STATUS_QUO"] += 1
            elif status.startswith("BLOCKED"):
                stats["not_touched_BLOCKED"] += 1
            elif status.startswith("SKIP_PRODUCER_SIDE") or status.startswith("SKIP_AUDIT"):
                # These need producer edits or are audit-only, not consumer action
                pass
            continue

        # Skip if investigated (hand-crafted verdict already in place)
        if investigated_mask.at[idx]:
            stats["not_touched_INVESTIGATED"] += 1
            continue

        # Extract specific action from recommendation
        specific = _extract_specific_action(recommendation, n_fires)

        if specific is None:
            stats["kept_generic_no_specific_found"] += 1
            continue

        # Restore specific action + reset execution_status to PENDING so
        # autonomous executor can re-attempt
        df.at[idx, "final_recommended_actions"] = specific
        df.at[idx, "execution_status"] = "PENDING"
        current_comments = str(df.at[idx, "execution_comments"])
        df.at[idx, "execution_comments"] = (
            current_comments
            + " B1149 (Council 260 fix) RESTORED specific action from "
            + "recommendation column (Turn 9 auto-loop had overwritten with generic template). "
            + "Reset to PENDING for autonomous executor re-attempt."
        )
        stats["restored_specific"] += 1

    df.to_csv(CSV_PATH, index=False)

    print("B1149 Council 260 Fix: Restore specific actions from recommendation column")
    print("=" * 78)
    for k, v in stats.items():
        print(f"  {k:40s}: {v:4d}")
    print()
    total_restored = stats["restored_specific"]
    print(f"Total strategies with specific actions restored: {total_restored}")
    print(f"These will be re-attempted by autonomous executor in B1150.")

    # Show sample restorations
    if total_restored > 0:
        print()
        print("Sample restorations (first 3):")
        restored_df = df[
            df["execution_comments"].str.contains("B1149", na=False)
            & (df["execution_status"] == "PENDING")
        ].head(3)
        for _, r in restored_df.iterrows():
            print(f"\n  {r['strategy_name']} (n={int(r['n_fires'])}):")
            print(f"    ORIGINAL rec: {str(r['recommendation'])[:100]}...")
            print(f"    RESTORED action: {str(r['final_recommended_actions'])[:200]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
