"""Batch 522 (2026-05-31, P17d + P17e SCAFFOLD per EXECUTION_QUEUE).

P17d + P17e are NOT standalone strategies -- they are pure modifiers
that adjust an EXISTING strategy's tier (P17d) or smart-money score
(P17e). The producer that feeds them is
`backtest.signals.sec_edgar_extractor.compute_sec_edgar_signals`.

NEITHER MODIFIER IS WIRED in Batch 522. The functions ship + are
unit-tested in isolation; flipping the wire-in (modifying
`_assign_confidence_tier` and `smart_money_score`) requires a
separate owner-approved batch once P17a scoped extraction completes.

P17d: officer-change overlay
  - 8-K Item 5.02 covers officer departure/election
  - CEO/CFO departure carries high uncertainty premium; sudden CFO
    exits especially predictive of accounting issues
  - Modifier downgrades the preliminary tier by 1 slot for affected
    ticker during the 7-day window post-filing

P17e: passive flow (SC 13G) overlay
  - SC 13G filings = passive 5%+ holders (Vanguard, BlackRock, etc.)
  - Less actionable than 13D but: smart-passive concentration
    (Sequoia, Wellington, GMO) signals quality; Vanguard/BlackRock
    crossing 5% predicts index reweighting + forced index-fund buying
  - Modifier adds +1 to smart_money_score for 30 days post-filing
"""
from __future__ import annotations

from datetime import date

# Ordered worst -> best (lowest tier index = LOW position size, etc.).
# Matches the canonical tier_assignment lattice used throughout the
# engine. The downgrade modifier moves a tier ONE position toward LOW.
_TIER_ORDER = (
    "LOW", "MEDIUM", "MEDIUM-HIGH", "HIGH", "VERY HIGH", "EXCEPTIONAL",
)


def tier_modifier_officer_change_5_02(
    ticker: str,
    as_of: date,
    current_tier: str,
) -> str:
    """P17d (SCAFFOLD) -- downgrade `current_tier` by 1 slot if an
    8-K Item 5.02 (officer change) was filed in the last 7 days.

    Returns the new tier label. If already at LOW (or current_tier
    is unrecognized), returns `current_tier` unchanged. If no 5.02
    filing in window, returns `current_tier` unchanged.

    Module-level import of `compute_sec_edgar_signals` to keep the
    dependency direction unidirectional (modifier -> extractor,
    not the other way).
    """
    if current_tier not in _TIER_ORDER:
        return current_tier
    try:
        from backtest.signals.sec_edgar_extractor import (
            eight_k_item_filed_within_days,
        )
        sig = eight_k_item_filed_within_days(
            ticker, as_of, item_code="5.02", lookback_days=7,
        )
    except Exception:
        return current_tier
    if not sig.get("8k_item_5_02_filed_within_7d", False):
        return current_tier
    idx = _TIER_ORDER.index(current_tier)
    if idx == 0:
        return current_tier  # already at LOW, can't downgrade further
    return _TIER_ORDER[idx - 1]


def smart_money_score_modifier_13g(
    ticker: str,
    as_of: date,
    current_score: int,
) -> int:
    """P17e (SCAFFOLD) -- add +1 to `current_score` if an SC 13G
    passive filing landed in the last 30 days.

    Returns the new integer score. If no 13G filing in window OR
    the extractor errors, returns `current_score` unchanged.
    """
    try:
        from backtest.signals.sec_edgar_extractor import (
            sc_13g_filed_within_days,
        )
        sig = sc_13g_filed_within_days(ticker, as_of, lookback_days=30)
    except Exception:
        return current_score
    if sig.get("sc_13g_filed_within_30d", False):
        return current_score + 1
    return current_score


__all__ = [
    "tier_modifier_officer_change_5_02",
    "smart_money_score_modifier_13g",
]
