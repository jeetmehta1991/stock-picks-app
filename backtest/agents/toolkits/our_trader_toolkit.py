"""OurTraderToolkit - Trader agent data bridge. SCAFFOLD ONLY.

Source (per CHECKLIST #77): TRADINGAGENTS_DATA_AUDIT.md Section 23.

HARD DEPENDENCY on BUG-095 Portfolio class. This is a SCAFFOLD module
returning placeholder data; real wiring happens after Portfolio class
ships (Sprint 3 deliverable).

Sprint 7 Phase A scope (Batch 350): scaffold class with stub methods that
return well-formed empty/sentinel dicts. Pyramid tests pin the interface
so future implementation cannot regress the contract.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any


_REPO = Path(__file__).resolve().parents[3]


class OurTraderToolkit:
    """Trader toolkit. SCAFFOLD - real implementation depends on Portfolio class.

    All methods return well-formed dicts with the documented schema; values
    are empty / sentinel until Portfolio class ships.
    """

    def __init__(self, portfolio: Any = None) -> None:
        # `portfolio` will be a Portfolio instance once BUG-095 ships.
        self.portfolio = portfolio

    def get_position_sizing_rules(self, tier: str) -> dict[str, Any]:
        """Return sizing rule for a confidence tier per DEC-021.

        DEC-021 3-tier (5%/3%/1.5%) + LOW skip + Mid-tier 0.75% are
        approved CLAUDE.md rules. This method exposes them as a structured
        dict that the Trader can include in its prompt context.
        """
        tier_map = {
            "EXCEPTIONAL": 5.0,
            "VERY_HIGH": 4.0,
            "HIGH": 3.0,
            "MEDIUM_HIGH": 1.5,
            "MEDIUM": 0.75,
            "LOW": 0.0,  # skip
        }
        size_pct = tier_map.get(tier.upper(), 0.0)
        return {
            "tier": tier.upper(),
            "position_size_pct": size_pct,
            "skip": size_pct == 0.0,
        }

    def get_portfolio_state(self) -> dict[str, Any]:
        """Return current portfolio summary. SCAFFOLD - empty until BUG-095 lands."""
        if self.portfolio is None:
            return {
                "n_positions": 0,
                "cash_available_pct": 100.0,
                "max_drawdown_pct": 0.0,
                "scaffold": True,
            }
        # Future-state: real Portfolio class methods land here.
        return {
            "n_positions": getattr(self.portfolio, "n_positions", 0),
            "cash_available_pct": getattr(self.portfolio, "cash_pct", 0.0),
            "max_drawdown_pct": getattr(self.portfolio, "max_drawdown_pct", 0.0),
            "scaffold": False,
        }

    def get_existing_position(self, ticker: str) -> dict[str, Any]:
        """Return current position in ticker. SCAFFOLD."""
        if self.portfolio is None:
            return {"ticker": ticker, "open": False, "scaffold": True}
        # Future: portfolio.get_position(ticker)
        return {"ticker": ticker, "open": False, "scaffold": False}

    def get_per_ticker_cooldown(self, ticker: str, as_of: date) -> dict[str, Any]:
        """Check if ticker is in 5-day post-stop cooldown per DEC-018. SCAFFOLD."""
        return {
            "ticker": ticker,
            "as_of": as_of.isoformat(),
            "in_cooldown": False,
            "days_remaining": 0,
            "scaffold": True,
        }
