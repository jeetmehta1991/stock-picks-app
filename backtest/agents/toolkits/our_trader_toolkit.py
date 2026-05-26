"""OurTraderToolkit - Trader agent data bridge.

Source (per CHECKLIST #77): TRADINGAGENTS_DATA_AUDIT.md Section 23.

Pre-Stream-B2: SCAFFOLD pending BUG-095 Portfolio class.
Post-Stream-B2 (Batch 368 2026-05-26): wired to `backtest.engine.portfolio.Portfolio`
(which shipped as Batch 328 / Pass 53 v8h+1 Batch 20). Stream B2 audit
2026-05-26 confirmed Portfolio class is already implemented; this commit
removes the scaffold sentinel paths and wires real queries.

Sprint 7 Phase A complete (Batches 349-368): toolkit + state augmentation
+ Portfolio wiring. Phase B (real LLM calls on Hetzner Python 3.12)
remains future work.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any


_REPO = Path(__file__).resolve().parents[3]


class OurTraderToolkit:
    """Trader toolkit. Wires backtest.engine.portfolio.Portfolio for live
    portfolio queries; falls back to safe sentinels when portfolio is None
    (e.g., LLM-mocked smoke tests without an active backtest).

    Batch 373 (2026-05-26) Sprint 7 Phase B prep: accept an optional
    `circuit_breaker_log` list (the engine's `self.circuit_breaker_log`
    on BacktestEngine; see backtest/engine/backtest.py:126) so that
    get_per_ticker_cooldown can resolve real stop-out history from the
    Stage 2 engine without requiring Portfolio API changes. Sprint 7
    Phase B wiring (when langgraph_pipeline calls this toolkit) must
    pass the engine's circuit_breaker_log alongside the portfolio.
    """

    def __init__(self, portfolio: Any = None,
                 circuit_breaker_log: Any = None) -> None:
        self.portfolio = portfolio
        # Optional list[dict] with shape:
        #   [{"date": date, "ticker": str, "level": str, "reason": str, ...}]
        # Pass-by-reference is fine - we only read.
        self.circuit_breaker_log = circuit_breaker_log

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
        """Return current portfolio summary backed by Portfolio class.

        Stream B2 (2026-05-26): real implementation reading
        backtest.engine.portfolio.Portfolio. Falls back to safe sentinels
        when portfolio is None (mocked smoke tests, etc.).
        """
        if self.portfolio is None:
            return {
                "n_positions": 0,
                "cash_available_pct": 100.0,
                "max_drawdown_pct": 0.0,
                "scaffold": True,
            }
        # Real Portfolio API per backtest/engine/portfolio.py
        try:
            n_open = self.portfolio.num_open
            total_eq = self.portfolio.total_equity()
            starting = getattr(self.portfolio, "starting_capital", 100_000.0)
            cash = getattr(self.portfolio, "cash", 0.0)
            cash_pct = (cash / total_eq * 100.0) if total_eq > 0 else 0.0
            dd_pct = self.portfolio.current_drawdown_pct()
            return {
                "n_positions":        int(n_open),
                "total_equity":       round(float(total_eq), 2),
                "cash":               round(float(cash), 2),
                "cash_available_pct": round(float(cash_pct), 2),
                "max_drawdown_pct":   round(float(dd_pct), 2),
                "starting_capital":   round(float(starting), 2),
                "scaffold":           False,
            }
        except Exception as e:
            return {
                "n_positions": 0,
                "cash_available_pct": 100.0,
                "max_drawdown_pct": 0.0,
                "scaffold": False,
                "error": f"portfolio query failed: {e}",
            }

    def get_existing_position(self, ticker: str) -> dict[str, Any]:
        """Return current position in ticker (Stream B2 real wiring)."""
        if self.portfolio is None:
            return {"ticker": ticker, "open": False, "scaffold": True}
        positions = getattr(self.portfolio, "positions", {})
        if ticker not in positions:
            return {"ticker": ticker, "open": False, "scaffold": False}
        pos = positions[ticker]
        return {
            "ticker":         ticker,
            "open":           True,
            "direction":      getattr(pos, "direction", "unknown"),
            "entry_date":     str(getattr(pos, "entry_date", "")),
            "entry_price":    float(getattr(pos, "entry_price", 0.0)),
            "shares":         float(getattr(pos, "shares", 0.0)),
            "sector":         getattr(pos, "sector", "unknown"),
            "last_mark":      float(getattr(pos, "last_mark", 0.0)),
            "scaffold":       False,
        }

    def get_per_ticker_cooldown(self, ticker: str, as_of: date) -> dict[str, Any]:
        """Check if ticker is in 5-day post-stop cooldown per DEC-018.

        Batch 373 (Sprint 7 Phase B prep 2026-05-26): real wiring against
        the engine's `circuit_breaker_log` when passed at toolkit init.
        Falls back to scaffold sentinel when log is None (mock-smoke /
        LLM dry-run scenarios). DEC-018 specifies 5-trading-day cooldown
        post-stop; we use a calendar-day proxy (5 days) per the existing
        engine convention - calendar/trading-day exactness can be
        tightened when Phase 1B-alpha lands.
        """
        if self.circuit_breaker_log is None:
            return {
                "ticker": ticker,
                "as_of": as_of.isoformat(),
                "in_cooldown": False,
                "days_remaining": 0,
                "scaffold": True,
                "deferred_reason": (
                    "circuit_breaker_log not passed at toolkit init; mock-smoke "
                    "callers (LLM dry-run) hit this path."
                ),
            }
        # Real path - filter the log for ticker-matching stop events
        from datetime import timedelta
        DEC_018_COOLDOWN_DAYS = 5
        most_recent_stop = None
        for entry in self.circuit_breaker_log:
            if entry.get("ticker") != ticker:
                continue
            ed = entry.get("date")
            if ed is None or ed > as_of:
                continue
            if most_recent_stop is None or ed > most_recent_stop:
                most_recent_stop = ed
        if most_recent_stop is None:
            return {
                "ticker":          ticker,
                "as_of":           as_of.isoformat(),
                "in_cooldown":     False,
                "days_remaining":  0,
                "last_stop_date":  None,
                "scaffold":        False,
            }
        days_since = (as_of - most_recent_stop).days
        days_remaining = max(0, DEC_018_COOLDOWN_DAYS - days_since)
        return {
            "ticker":         ticker,
            "as_of":          as_of.isoformat(),
            "in_cooldown":    days_remaining > 0,
            "days_remaining": int(days_remaining),
            "last_stop_date": most_recent_stop.isoformat(),
            "scaffold":       False,
        }
