"""DEC-250 — Edge decay haircut for crowded-trade Sharpe discount (Pass 53 build).

Per DEC-250 Pass 52 turn 117 owner-approved: discount backtest Sharpe by expected
crowding %. Default haircut = 20% (Sharpe × 0.80) per REVISIT_AFTER_BACKTEST tag.

Phase 1B-α 7-gate verdict (DEC-578) Gate 6 = post-haircut Sharpe ≥ threshold.

Status: PARTIAL-SPEC-ONLY → RESOLVED-DECIDED post artifact landing per DEC-594.
"""

from __future__ import annotations

from typing import Dict


DEFAULT_HAIRCUT_PCT = 0.20  # 20% Sharpe haircut for expected crowding (DEC-250)
HIGH_CROWDING_HAIRCUT_PCT = 0.40  # 40% for known-crowded strategies (e.g., basic momentum)
LOW_CROWDING_HAIRCUT_PCT = 0.10  # 10% for novel-signal strategies


def apply_haircut(
    sharpe_raw: float,
    haircut_pct: float = DEFAULT_HAIRCUT_PCT,
) -> float:
    """Apply Sharpe haircut for expected crowding decay.

    Args:
        sharpe_raw: backtest-derived Sharpe (annualized).
        haircut_pct: fraction to discount (default 0.20 per DEC-250).

    Returns:
        Adjusted Sharpe = sharpe_raw × (1 - haircut_pct).

    Example: sharpe_raw=1.5, haircut=0.20 → adjusted=1.20.
    """
    if not 0 <= haircut_pct < 1:
        raise ValueError(f"haircut_pct must be in [0, 1); got {haircut_pct}")
    return float(sharpe_raw * (1 - haircut_pct))


def categorize_crowding(strategy_name: str, strategy_meta: Dict | None = None) -> float:
    """Heuristic crowding classification → haircut %.

    Per DEC-250 Phase B (Sprint 7+): replace heuristic with empirical per-strategy
    decay measured from prior 1y rolling Sharpe stability.

    Heuristic rules (Pass 53 baseline):
      - "momentum" / "mean_reversion" / "breakout" — known crowded → 40% haircut
      - "smart_money" / "ICT" / "options_implied" — moderate crowding → 20%
      - novel signal types (e.g., universe-level rank) → low crowding → 10%
    """
    name_lower = strategy_name.lower()
    high_crowding_keywords = ("momentum", "mean_reversion", "mean_revert", "breakout", "rsi", "macd")
    low_crowding_keywords = ("universe_rank", "cross_sectional", "factor_exposure", "breadth")

    if any(kw in name_lower for kw in high_crowding_keywords):
        return HIGH_CROWDING_HAIRCUT_PCT
    if any(kw in name_lower for kw in low_crowding_keywords):
        return LOW_CROWDING_HAIRCUT_PCT
    return DEFAULT_HAIRCUT_PCT


def adjusted_metrics(
    sharpe_raw: float,
    win_rate_raw: float,
    profit_factor_raw: float,
    haircut_pct: float = DEFAULT_HAIRCUT_PCT,
) -> Dict[str, float]:
    """Apply edge-decay haircut to Sharpe + WR + PF.

    Per DEC-250: WR and PF also haircut, but at half the Sharpe rate (less
    selection pressure on these metrics in the literature).

    Returns:
        {sharpe_adj, win_rate_adj, profit_factor_adj}
    """
    sharpe_adj = apply_haircut(sharpe_raw, haircut_pct)
    half_haircut = haircut_pct / 2
    wr_adj = win_rate_raw * (1 - half_haircut)
    # PF haircut: discount the EXCESS over 1.0 (since PF=1.0 is break-even)
    if profit_factor_raw > 1.0:
        excess = profit_factor_raw - 1.0
        pf_adj = 1.0 + excess * (1 - half_haircut)
    else:
        pf_adj = profit_factor_raw  # don't haircut losing strategies further

    return {
        "sharpe_adj": float(sharpe_adj),
        "win_rate_adj": float(wr_adj),
        "profit_factor_adj": float(pf_adj),
        "haircut_pct_applied": float(haircut_pct),
    }
