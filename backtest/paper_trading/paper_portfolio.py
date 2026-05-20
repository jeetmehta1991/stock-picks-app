"""Stage 3 paper portfolio (Batch 246).

Simulated portfolio tracking for Stage 3 paper trading. Reads daily picks,
tracks open positions, marks-to-market at close, computes PnL.

Persistence: SQLite (per DEC-267 trade event store) OR CSV/parquet (simpler
for skeleton; SQLite wired post-1B-alpha when active).

Stateful: portfolio.json persists between daily runs. Loaded at start of
run_paper_morning.py, updated, saved at end of run_paper_end_of_day.py.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass
class PaperPosition:
    """Single open paper position."""
    ticker: str
    combo_id: str
    entry_date: str  # ISO
    entry_price: float
    size_pct: float  # of portfolio
    shares: int      # computed from size_pct + portfolio_value
    initial_stop: float
    current_stop: float
    highest_close: float
    days_held: int
    direction: str = "long"
    exit_method: str = "atr_trail_1x"
    confidence_tier: str = "MEDIUM"

    def mark_to_market(self, close_price: float) -> float:
        """PnL in % if exited at close_price."""
        if self.entry_price <= 0:
            return 0.0
        if self.direction == "long":
            return (close_price - self.entry_price) / self.entry_price * 100
        return (self.entry_price - close_price) / self.entry_price * 100


@dataclass
class PaperPortfolio:
    """Top-level paper portfolio state."""
    starting_value: float = 100_000.0
    current_value: float = 100_000.0
    cash: float = 100_000.0
    open_positions: list[PaperPosition] = field(default_factory=list)
    closed_trades: list[dict] = field(default_factory=list)
    last_update_date: Optional[str] = None
    peak_value: float = 100_000.0
    current_dd_pct: float = 0.0

    def to_dict(self) -> dict:
        return {
            "starting_value":    self.starting_value,
            "current_value":     self.current_value,
            "cash":              self.cash,
            "open_positions":    [asdict(p) for p in self.open_positions],
            "closed_trades":     self.closed_trades,
            "last_update_date":  self.last_update_date,
            "peak_value":        self.peak_value,
            "current_dd_pct":    self.current_dd_pct,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PaperPortfolio":
        positions = [PaperPosition(**p) for p in d.get("open_positions", [])]
        return cls(
            starting_value=d.get("starting_value", 100_000.0),
            current_value=d.get("current_value", 100_000.0),
            cash=d.get("cash", 100_000.0),
            open_positions=positions,
            closed_trades=d.get("closed_trades", []),
            last_update_date=d.get("last_update_date"),
            peak_value=d.get("peak_value", 100_000.0),
            current_dd_pct=d.get("current_dd_pct", 0.0),
        )

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2, default=str))

    @classmethod
    def load(cls, path: Path) -> "PaperPortfolio":
        if not path.exists():
            return cls()
        try:
            return cls.from_dict(json.loads(path.read_text()))
        except Exception:
            return cls()

    def open_position(self, pick: dict, as_of: date) -> Optional[PaperPosition]:
        """Open a new paper position from a pick."""
        ticker = pick["ticker"]
        # Don't double-open same ticker
        if any(p.ticker == ticker for p in self.open_positions):
            return None
        size_pct = float(pick["position_size_pct"])
        entry_price = float(pick["entry_price"])
        if entry_price <= 0 or size_pct <= 0:
            return None
        position_value = self.current_value * (size_pct / 100)
        if position_value > self.cash:
            position_value = self.cash * 0.95  # buffer
        if position_value <= 0:
            return None
        shares = int(position_value / entry_price)
        if shares == 0:
            return None
        pos = PaperPosition(
            ticker=ticker,
            combo_id=pick.get("combo_id", ""),
            entry_date=str(as_of),
            entry_price=entry_price,
            size_pct=size_pct,
            shares=shares,
            initial_stop=float(pick.get("initial_stop", entry_price * 0.98)),
            current_stop=float(pick.get("initial_stop", entry_price * 0.98)),
            highest_close=entry_price,
            days_held=0,
            exit_method=pick.get("exit_method", "atr_trail_1x"),
            confidence_tier=pick.get("confidence_tier", "MEDIUM"),
        )
        self.open_positions.append(pos)
        self.cash -= shares * entry_price
        return pos

    def update_eod(self, market_data: dict[str, pd.DataFrame], as_of: date) -> dict:
        """End-of-day update: mark positions, check exits, log PnL.

        Returns summary dict with daily_pnl_pct, n_open, n_closed_today.
        """
        n_closed_today = 0
        daily_pnl_dollar = 0.0
        survivors: list[PaperPosition] = []
        for pos in self.open_positions:
            df = market_data.get(pos.ticker)
            if df is None or df.empty:
                survivors.append(pos)
                continue
            close_price = float(df.iloc[-1].get("close", pos.entry_price))
            pos.days_held += 1
            pos.highest_close = max(pos.highest_close, close_price)
            # Simple trailing stop: 2% below highest close
            new_stop = pos.highest_close * 0.98
            if new_stop > pos.current_stop:
                pos.current_stop = new_stop
            # Exit if close < current_stop
            if close_price <= pos.current_stop:
                pnl_pct = pos.mark_to_market(close_price)
                pnl_dollar = pos.shares * (close_price - pos.entry_price)
                daily_pnl_dollar += pnl_dollar
                self.cash += pos.shares * close_price
                self.closed_trades.append({
                    "ticker":      pos.ticker,
                    "combo_id":    pos.combo_id,
                    "entry_date":  pos.entry_date,
                    "exit_date":   str(as_of),
                    "entry_price": pos.entry_price,
                    "exit_price":  close_price,
                    "pnl_pct":     round(pnl_pct, 4),
                    "pnl_dollar":  round(pnl_dollar, 2),
                    "hold_days":   pos.days_held,
                    "exit_reason": "trailing_stop",
                })
                n_closed_today += 1
            else:
                # Unrealized P&L
                survivors.append(pos)
        self.open_positions = survivors

        # Mark portfolio value
        mtm = self.cash
        for pos in self.open_positions:
            df = market_data.get(pos.ticker)
            if df is None or df.empty:
                mtm += pos.shares * pos.entry_price
                continue
            close_price = float(df.iloc[-1].get("close", pos.entry_price))
            mtm += pos.shares * close_price
        self.current_value = mtm
        self.peak_value = max(self.peak_value, mtm)
        if self.peak_value > 0:
            self.current_dd_pct = round((self.peak_value - mtm) / self.peak_value * 100, 2)
        self.last_update_date = str(as_of)

        return {
            "as_of":          str(as_of),
            "current_value":  round(self.current_value, 2),
            "cash":           round(self.cash, 2),
            "n_open":         len(self.open_positions),
            "n_closed_today": n_closed_today,
            "daily_pnl_dollar": round(daily_pnl_dollar, 2),
            "current_dd_pct": self.current_dd_pct,
        }
