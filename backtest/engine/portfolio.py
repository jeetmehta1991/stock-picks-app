"""
Portfolio-level state for the backtest engine.

BUG-95 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 20 2026-05-10
(owner-approved Option A).

Prior to this module, the engine tracked individual OpenTrade / ClosedTrade
objects but had no portfolio-level state - no equity curve, no cash balance,
no mark-to-market, no per-sector exposure, no LIVE_TRADING_RULES enforcement.
Per-strategy Sharpe was reported but the true portfolio Sharpe (correlated
positions) was unknowable; total ROI implicitly assumed infinite capital.

This module introduces a Portfolio class that the engine instantiates once at
Backtest construction and updates each day. The Portfolio:
  - Tracks cash, positions (ticker -> Position), and daily (date, equity)
    points in equity_curve
  - Marks open positions to today's close each day (mark_to_market)
  - Gates new entries via can_open(): max_open_positions, cash sufficiency,
    drawdown breach (suspend at >30%)
  - Reports per-sector exposure for downstream concentration checks (DEC-076)
  - Supports per-tier position-size scaling (DEC-091) via the size_pct param
    passed by the engine

Design notes:
  - All amounts are CAD (per LIVE_TRADING_RULES.base_currency); FX conversion
    of USD trades happens at engine call sites (Phase 1B+ work).
  - Positions are SHARE-based (entry_price + shares); the engine derives shares
    from position_size_pct * total_equity / entry_price at add_position time.
  - mark_to_market accepts a sparse prices dict; positions with missing
    prices are valued at the LAST known price (carried forward); this matches
    the engine's behavior when ticker data is missing for a single day.
  - The class is pure - no I/O, no global state. All inputs flow in via method
    args; outputs are accessor properties. This keeps it unit-testable in
    isolation from the engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Position:
    """A single open position held in the portfolio."""
    ticker:        str
    sector:        str
    direction:     str           # 'long' or 'short'
    entry_date:    date
    entry_price:   float
    shares:        float         # may be fractional
    last_mark:     float = 0.0   # last mark-to-market price (cached for stale data)

    def notional_value(self, price: float) -> float:
        """Current notional dollar value at a given price."""
        return abs(self.shares) * price

    def unrealised_pnl_dollar(self, price: float) -> float:
        """Unrealised PnL at a given price (positive = profit)."""
        if self.direction == "long":
            return self.shares * (price - self.entry_price)
        else:  # short
            return self.shares * (self.entry_price - price)


def vol_targeted_size(
    base_size_pct: float,
    position_vol_annualized: Optional[float],
    target_vol_annualized: Optional[float] = None,
) -> float:
    """DEC-087 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 52 2026-05-11
    (owner-approved Path C). Vol-targeted per-position sizing: scale base
    tier size by `target_vol / position_vol` so higher-vol positions get
    proportionally smaller allocations (equal risk contribution per name).

    Closes DEC-023 (SUPERSEDED_BY_DEC-087). Joint with DEC-088 portfolio-
    level vol target which applies on top of per-position scaling.

    Inputs:
      base_size_pct: tier-derived position size (TIER_POSITION_SIZE_PCT)
      position_vol_annualized: per-ticker annualized realized vol (e.g.,
        from backtest.signals.dec513_extended_signals.compute_realized_vol)
      target_vol_annualized: per-position target (default
        VOL_TARGETED_TARGET_PER_POSITION_ANNUALIZED = 0.20)

    Returns float adjusted size_pct. Fail-soft to base_size_pct when
    position_vol is None / non-positive (no vol input -> no adjustment).
    Multiplier bounded by [VOL_TARGETED_SIZE_MIN_MULTIPLIER,
    VOL_TARGETED_SIZE_MAX_MULTIPLIER] to avoid extreme adjustments.
    """
    from backtest.config import (
        VOL_TARGETED_TARGET_PER_POSITION_ANNUALIZED,
        VOL_TARGETED_SIZE_MIN_MULTIPLIER,
        VOL_TARGETED_SIZE_MAX_MULTIPLIER,
    )
    if position_vol_annualized is None or position_vol_annualized <= 0:
        return base_size_pct
    tgt = (target_vol_annualized
           if target_vol_annualized is not None
           else VOL_TARGETED_TARGET_PER_POSITION_ANNUALIZED)
    if tgt <= 0:
        return base_size_pct
    ratio = tgt / position_vol_annualized
    bounded = max(
        VOL_TARGETED_SIZE_MIN_MULTIPLIER,
        min(VOL_TARGETED_SIZE_MAX_MULTIPLIER, ratio),
    )
    return base_size_pct * bounded


class Portfolio:
    """
    Portfolio-level state. Instantiated once per Backtest run.

    Usage from Backtest:
      self.portfolio = Portfolio(starting_capital=100_000)
      ...
      # Each day, after exits, before entries:
      self.portfolio.mark_to_market(prices_today, today_date)
      # Before adding a trade:
      if self.portfolio.can_open(ticker, size_pct=0.03,
                                 max_positions=10):
          self.portfolio.add_position(ticker, sector, direction,
                                      entry_price, size_pct=0.03,
                                      entry_date=today_date)
      # On exit:
      self.portfolio.remove_position(ticker, exit_price)
    """

    def __init__(self, starting_capital: float = 100_000.0,
                 benchmark: str = "SPY"):
        if starting_capital <= 0:
            raise ValueError(
                f"starting_capital must be positive (got {starting_capital})")
        self.starting_capital: float = float(starting_capital)
        self.benchmark: str = benchmark
        self.cash: float = float(starting_capital)
        self.positions: dict[str, Position] = {}
        self.equity_curve: list[tuple[date, float]] = []
        self.benchmark_curve: list[tuple[date, float]] = []
        # Peak equity used for drawdown calc - starts at initial capital
        self._equity_peak: float = float(starting_capital)

    # ------------------------------------------------------------------
    # State accessors
    # ------------------------------------------------------------------

    @property
    def num_open(self) -> int:
        return len(self.positions)

    def total_equity(self, prices: Optional[dict[str, float]] = None) -> float:
        """Total portfolio equity = cash + mark-to-market of all positions.

        If `prices` not supplied, uses each position's `last_mark` (carried
        forward). At t=0 with no marks, the only position value is
        entry_price * shares and total = starting_capital (cash deducted at
        add_position covers the equality).
        """
        if not self.positions:
            return self.cash
        pos_value = 0.0
        for pos in self.positions.values():
            mark = (prices or {}).get(pos.ticker, pos.last_mark)
            if mark <= 0:
                # Fall back to entry_price if no mark available
                mark = pos.entry_price
            pos_value += pos.notional_value(mark)
        return self.cash + pos_value

    def current_drawdown_pct(self) -> float:
        """Drawdown from running equity peak, as a positive percent
        (0.0 if no drawdown, e.g. equity == peak).
        """
        if not self.equity_curve:
            return 0.0
        current = self.equity_curve[-1][1]
        if self._equity_peak <= 0:
            return 0.0
        dd = (self._equity_peak - current) / self._equity_peak
        return max(0.0, dd) * 100.0

    def exposure_by_sector(self, prices: Optional[dict[str, float]] = None
                           ) -> dict[str, float]:
        """Returns dict {sector: pct_of_total_equity}. Empty if no positions."""
        if not self.positions:
            return {}
        total = self.total_equity(prices)
        if total <= 0:
            return {}
        out: dict[str, float] = {}
        for pos in self.positions.values():
            mark = (prices or {}).get(pos.ticker, pos.last_mark) or pos.entry_price
            val = pos.notional_value(mark)
            out[pos.sector] = out.get(pos.sector, 0.0) + (val / total)
        return out

    # ------------------------------------------------------------------
    # State mutators
    # ------------------------------------------------------------------

    def mark_to_market(self, prices: dict[str, float],
                       today: date) -> float:
        """Mark all open positions to today's close, append (today, equity) to
        equity_curve, and update running peak. Returns total equity.

        Missing prices: position's `last_mark` is preserved (no update); equity
        contribution uses last_mark. This matches engine behavior where a
        ticker may lack data for a single day.
        """
        for pos in self.positions.values():
            if pos.ticker in prices and prices[pos.ticker] > 0:
                pos.last_mark = float(prices[pos.ticker])
        equity = self.total_equity(prices)
        self.equity_curve.append((today, equity))
        if equity > self._equity_peak:
            self._equity_peak = equity
        return equity

    def add_benchmark_point(self, today: date, benchmark_price: float) -> None:
        """Append a benchmark close to the benchmark_curve. Engine wires this
        each day from SPY close.
        """
        if benchmark_price > 0:
            self.benchmark_curve.append((today, float(benchmark_price)))

    def realized_portfolio_vol_annualized(
        self, window_days: Optional[int] = None,
    ) -> Optional[float]:
        """DEC-088 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 51 2026-05-11
        (owner-approved Path C). Realized portfolio vol annualized via
        sqrt(252) on daily equity returns over the lookback window.

        Returns None if fewer than `window_days + 1` equity points exist
        (insufficient data; caller-side decides fallback). Returns 0.0 only
        when equity is genuinely flat across the window.
        """
        from backtest.config import PORTFOLIO_VOL_LOOKBACK_DAYS
        win = window_days if window_days is not None else PORTFOLIO_VOL_LOOKBACK_DAYS
        if len(self.equity_curve) < win + 1:
            return None
        recent = self.equity_curve[-(win + 1):]
        equities = [e for _, e in recent]
        if any(eq <= 0 for eq in equities):
            return None
        rets = []
        for i in range(1, len(equities)):
            rets.append((equities[i] - equities[i - 1]) / equities[i - 1])
        if len(rets) < 2:
            return None
        n = len(rets)
        mean = sum(rets) / n
        var = sum((r - mean) ** 2 for r in rets) / (n - 1)  # sample variance
        daily_std = var ** 0.5
        return float(daily_std * (252 ** 0.5))

    def vol_target_scale_factor(
        self,
        target: Optional[float] = None,
        window_days: Optional[int] = None,
    ) -> float:
        """DEC-088: recommend gross-sizing scale factor to maintain target
        annualized portfolio vol. scale = target / max(realized, target * 0.5)
        bounded by PORTFOLIO_VOL_SCALE_MIN..MAX.

        Returns 1.0 (no scaling) when realized vol unavailable (insufficient
        history) or when realized is within +/- 10% of target. Engine
        consumption deferred to follow-on decision; current scope is helper
        + telemetry, not auto-scaling.
        """
        from backtest.config import (
            PORTFOLIO_VOL_TARGET_ANNUALIZED,
            PORTFOLIO_VOL_SCALE_MIN,
            PORTFOLIO_VOL_SCALE_MAX,
        )
        tgt = target if target is not None else PORTFOLIO_VOL_TARGET_ANNUALIZED
        realized = self.realized_portfolio_vol_annualized(window_days)
        if realized is None or tgt <= 0:
            return 1.0
        # Floor at half-target to avoid divide-by-near-zero blowup when
        # equity has been near-flat (cash-heavy early days).
        denom = max(realized, tgt * 0.5)
        scale = tgt / denom
        return max(PORTFOLIO_VOL_SCALE_MIN, min(PORTFOLIO_VOL_SCALE_MAX, scale))

    def can_open(self, ticker: str, size_pct: float,
                 max_positions: int = 10,
                 prices: Optional[dict[str, float]] = None,
                 drawdown_suspend_pct: float = 30.0) -> tuple[bool, str]:
        """Returns (can_open: bool, reason: str).

        Gates:
          1. Drawdown breach: current_drawdown >= drawdown_suspend_pct -> deny
          2. max_open_positions: num_open >= max_positions -> deny (BUG-95)
          3. Cash sufficiency: required_dollar > cash -> deny
          4. Ticker uniqueness: ticker already in positions -> deny (BUG-61
             ticker-level concurrent block is enforced upstream too)
        """
        if size_pct <= 0:
            return False, "size_pct_non_positive"
        if self.current_drawdown_pct() >= drawdown_suspend_pct:
            return False, f"drawdown_suspend_breach_{drawdown_suspend_pct}pct"
        if self.num_open >= max_positions:
            return False, f"max_open_positions_{max_positions}_reached"
        if ticker in self.positions:
            return False, "ticker_already_in_portfolio"
        required = self.total_equity(prices) * size_pct
        if required > self.cash:
            return False, f"insufficient_cash_required_{required:.2f}_have_{self.cash:.2f}"
        return True, "ok"

    def add_position(self, ticker: str, sector: str, direction: str,
                     entry_price: float, size_pct: float,
                     entry_date: date,
                     prices: Optional[dict[str, float]] = None) -> Position:
        """Open a new position. Deducts cash for the notional dollar amount.

        Long: cash -= shares * entry_price (covers full notional)
        Short: cash unchanged at entry (proceeds offset by margin; for backtest
        simplicity we treat shorts symmetrically to longs - same dollar
        deducted as a proxy for margin posting; this is a CONSERVATIVE
        simplification suitable for Stage 2 metrics and acceptable for
        Phase 1A May 15 since shorts are a small fraction of the strategy
        roster).
        """
        if entry_price <= 0:
            raise ValueError(f"entry_price must be positive (got {entry_price})")
        if direction not in ("long", "short"):
            raise ValueError(f"direction must be long|short (got {direction})")
        if ticker in self.positions:
            raise ValueError(f"ticker {ticker} already has open position")
        total_equity = self.total_equity(prices)
        dollar_alloc = total_equity * size_pct
        shares = dollar_alloc / entry_price
        pos = Position(
            ticker=ticker, sector=sector, direction=direction,
            entry_date=entry_date, entry_price=float(entry_price),
            shares=float(shares), last_mark=float(entry_price),
        )
        self.positions[ticker] = pos
        self.cash -= dollar_alloc  # Both long and short deduct (margin proxy)
        return pos

    def remove_position(self, ticker: str, exit_price: float) -> float:
        """Close a position at exit_price. Returns realised PnL in dollars.

        Cash credit is original_dollar_alloc + realised_pnl (long) so that
        a winning long credits back more than the original allocation.
        For shorts the same accounting applies via the unrealised_pnl
        formula sign.
        """
        if ticker not in self.positions:
            raise KeyError(f"ticker {ticker} not in portfolio")
        pos = self.positions.pop(ticker)
        if exit_price <= 0:
            exit_price = pos.last_mark or pos.entry_price
        realised = pos.unrealised_pnl_dollar(exit_price)
        original_notional = abs(pos.shares) * pos.entry_price
        # Credit back original alloc + realised PnL
        self.cash += original_notional + realised
        return realised
