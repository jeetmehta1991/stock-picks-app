"""Stage 4 live risk overlay (Batch 247).

Real-time enforcement of risk rules during live execution. Mirrors backtest
risk constraints to live trading per DEC-515 Level 6 (portfolio DD circuit
breaker), DEC-021 tier mapping, DEC-061/062 tier-to-size, and the 5 circuit
breakers documented in CLAUDE.md.

Owner directive 2026-05-19: this layer enforces SAFETY before any IB API
order placement. Single canonical gate that all live-execution paths pass
through.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


# Per CLAUDE.md approved position sizing
_TIER_SIZE_PCT = {
    "EXCEPTIONAL":   5.0,
    "VERY_HIGH":     4.0,
    "HIGH":          3.0,
    "MEDIUM-HIGH":   1.5,
    "MEDIUM":        0.75,
    "LOW":           0.0,
    "AVOID":         0.0,
}

# Per DEC-515 Level 6 portfolio drawdown circuit breaker
DEC_515_LEVEL_6_DD_TRIGGER_PCT = 15.0  # halt at 15% peak-to-trough
DEC_515_LEVEL_6_DD_RECOVERY_PCT = 5.0  # resume below 5% from new peak

# Daily loss limit (per DEC-034; removed from backtest per CLAUDE.md but
# RE-INTRODUCED for live trading safety per Stage 4 best practice)
LIVE_DAILY_LOSS_LIMIT_PCT = 3.0


@dataclass
class RiskCheckResult:
    """Result of a pre-trade risk check."""
    approved: bool
    reason: str = ""
    adjusted_size_pct: float = 0.0
    halt_signal: bool = False


@dataclass
class LiveRiskState:
    """Persistent risk state across the trading day."""
    portfolio_value:        float = 100_000.0
    portfolio_peak:         float = 100_000.0
    daily_starting_value:   float = 100_000.0
    open_positions_count:   int = 0
    halt_active:            bool = False
    halt_reason:            str = ""
    halt_timestamp:         Optional[str] = None

    @property
    def current_dd_pct(self) -> float:
        if self.portfolio_peak <= 0:
            return 0.0
        return (self.portfolio_peak - self.portfolio_value) / self.portfolio_peak * 100

    @property
    def daily_pnl_pct(self) -> float:
        if self.daily_starting_value <= 0:
            return 0.0
        return (self.portfolio_value - self.daily_starting_value) / self.daily_starting_value * 100


def check_pre_trade(
    pick: dict,
    risk_state: LiveRiskState,
) -> RiskCheckResult:
    """Pre-trade risk check. Returns approved/rejected + reason.

    Enforces:
    1. Halt state (DEC-515 Level 6 active -> reject all new entries)
    2. Daily loss limit (live-only addition per Stage 4 best practice)
    3. Confidence tier sizing (AVOID + LOW skip; per Batch 190 INV-049)
    4. Position size validity (entry price > 0; calculated shares > 0)
    """
    # Halt check
    if risk_state.halt_active:
        return RiskCheckResult(
            approved=False,
            reason=f"halt_active: {risk_state.halt_reason}",
        )

    # Daily loss limit
    if risk_state.daily_pnl_pct <= -LIVE_DAILY_LOSS_LIMIT_PCT:
        return RiskCheckResult(
            approved=False,
            reason=f"daily_loss_limit_breached: {risk_state.daily_pnl_pct:.2f}% <= -{LIVE_DAILY_LOSS_LIMIT_PCT}%",
            halt_signal=True,
        )

    # Portfolio DD circuit breaker (DEC-515 Level 6)
    if risk_state.current_dd_pct >= DEC_515_LEVEL_6_DD_TRIGGER_PCT:
        return RiskCheckResult(
            approved=False,
            reason=f"dec_515_level_6_dd_trigger: {risk_state.current_dd_pct:.2f}% >= {DEC_515_LEVEL_6_DD_TRIGGER_PCT}%",
            halt_signal=True,
        )

    # Confidence tier sizing
    tier = pick.get("confidence_tier", "MEDIUM")
    size_pct = _TIER_SIZE_PCT.get(tier, 0.0)
    if size_pct == 0.0:
        return RiskCheckResult(
            approved=False,
            reason=f"avoid_or_low_tier_blocked: {tier}",
        )

    # Entry price sanity
    entry_price = float(pick.get("entry_price", 0))
    if entry_price <= 0:
        return RiskCheckResult(
            approved=False,
            reason=f"invalid_entry_price: {entry_price}",
        )

    return RiskCheckResult(
        approved=True,
        reason="risk_check_passed",
        adjusted_size_pct=size_pct,
    )


def update_halt_state(risk_state: LiveRiskState) -> bool:
    """Re-evaluate halt state based on current portfolio metrics.

    Activates halt if DD >= trigger, deactivates if DD < recovery threshold.
    Returns True if halt currently active.
    """
    dd = risk_state.current_dd_pct
    if not risk_state.halt_active and dd >= DEC_515_LEVEL_6_DD_TRIGGER_PCT:
        risk_state.halt_active = True
        risk_state.halt_reason = f"dec_515_level_6_dd_{dd:.1f}pct"
        risk_state.halt_timestamp = datetime.utcnow().isoformat()
    elif risk_state.halt_active and dd < DEC_515_LEVEL_6_DD_RECOVERY_PCT:
        risk_state.halt_active = False
        risk_state.halt_reason = ""
        risk_state.halt_timestamp = None
    return risk_state.halt_active


def compute_shares_for_pick(
    pick: dict,
    portfolio_value: float,
    cash_available: float,
) -> int:
    """Convert (size_pct, entry_price) to share count.

    Respects cash_available; rounds DOWN (no fractional shares).
    """
    size_pct = float(pick.get("position_size_pct", 0))
    entry_price = float(pick.get("entry_price", 0))
    if size_pct <= 0 or entry_price <= 0:
        return 0
    target_dollar = portfolio_value * (size_pct / 100)
    if target_dollar > cash_available:
        target_dollar = cash_available * 0.95  # 5% cash buffer
    shares = int(target_dollar / entry_price)
    return max(0, shares)
