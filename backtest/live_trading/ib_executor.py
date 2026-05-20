"""Stage 4 IB API executor stub (Batch 247).

ib_async-based order placement layer. STUB-MODE default (dry_run=True) per
owner directive 2026-05-19 "built but not activated". Full IB integration
requires owner to provide IB credentials + flip dry_run flag.

Reference: ib_async (fork of ib_insync) per CLAUDE.md adopted forks list.

For each approved trade signal, this layer:
  1. Connects to IB Gateway (TWS API port 7497 paper / 7496 live)
  2. Places bracket order:
     - Entry: market or limit per pick
     - Stop: pick.initial_stop
     - Target: 2x ATR away (per DEC-353 R:R >= 2.0)
  3. Returns IB order_id for reconciliation
  4. Logs fill price for slippage measurement (DEC-122)

Reconciliation script reads IB executions at EOD + compares to expected
fills.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class IBExecutionResult:
    """Result of an IB order placement attempt."""
    success: bool
    ticker: str
    order_id: Optional[str] = None
    fill_price: Optional[float] = None
    shares: int = 0
    error: str = ""
    dry_run: bool = True


def place_bracket_order(
    ticker: str,
    direction: str,  # "long" or "short"
    shares: int,
    entry_price: float,
    stop_price: float,
    target_price: Optional[float] = None,
    order_type: str = "MKT",
    dry_run: bool = True,
    ib_connection=None,  # ib_async IB instance; None = stub mode
) -> IBExecutionResult:
    """Place a bracket order (entry + stop + optional target).

    dry_run=True (default): log the intended order; don't connect to IB.
    dry_run=False: requires ib_connection (live or paper-account IB Gateway).
    """
    # Auto-compute target if not provided (2x R per DEC-353)
    if target_price is None and entry_price > 0 and stop_price > 0:
        risk_per_share = abs(entry_price - stop_price)
        if direction == "long":
            target_price = entry_price + (2 * risk_per_share)
        else:
            target_price = entry_price - (2 * risk_per_share)

    if dry_run or ib_connection is None:
        # Stub mode: log + return synthetic order_id
        order_id = f"STUB-{ticker}-{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}"
        print(f"[DRY RUN] IB bracket order:")
        print(f"  Ticker:        {ticker}")
        print(f"  Direction:     {direction}")
        print(f"  Shares:        {shares}")
        print(f"  Entry:         {order_type} @ ~${entry_price:.2f}")
        print(f"  Stop:          ${stop_price:.2f}")
        print(f"  Target:        ${target_price:.2f}" if target_price else "  Target:        none")
        print(f"  Order ID:      {order_id}")
        return IBExecutionResult(
            success=True,
            ticker=ticker,
            order_id=order_id,
            fill_price=entry_price,  # assumed fill at requested price for stub
            shares=shares,
            dry_run=True,
        )

    # Live mode (requires ib_async; not active in skeleton)
    try:
        from ib_async import Contract, LimitOrder, MarketOrder, Order, Stock, StopOrder
    except ImportError:
        return IBExecutionResult(
            success=False, ticker=ticker, error="ib_async_not_installed", dry_run=False,
        )
    try:
        action = "BUY" if direction == "long" else "SELL"
        contract = Stock(ticker, "SMART", "USD")
        # Bracket order (parent + children)
        parent = MarketOrder(action, shares) if order_type == "MKT" else LimitOrder(action, shares, entry_price)
        parent.transmit = False
        parent.orderId = ib_connection.client.getReqId()

        stop_action = "SELL" if direction == "long" else "BUY"
        stop_order = StopOrder(stop_action, shares, stop_price)
        stop_order.parentId = parent.orderId
        stop_order.transmit = False if target_price else True

        children = [stop_order]
        if target_price:
            target_action = "SELL" if direction == "long" else "BUY"
            target_order = LimitOrder(target_action, shares, target_price)
            target_order.parentId = parent.orderId
            target_order.transmit = True
            children.append(target_order)

        # Place parent + children
        trade = ib_connection.placeOrder(contract, parent)
        for child in children:
            ib_connection.placeOrder(contract, child)
        return IBExecutionResult(
            success=True, ticker=ticker, order_id=str(parent.orderId),
            shares=shares, dry_run=False,
        )
    except Exception as exc:
        return IBExecutionResult(
            success=False, ticker=ticker, error=f"ib_error: {exc}", dry_run=False,
        )


def connect_ib(
    host: str = "127.0.0.1",
    port: int = 7497,  # 7497 = paper account; 7496 = live
    client_id: int = 1,
    dry_run: bool = True,
):
    """Connect to IB Gateway. Returns IB instance or None in dry_run mode."""
    if dry_run:
        return None
    try:
        from ib_async import IB
    except ImportError:
        print("[ERROR] ib_async not installed; install via 'pip install ib_async'")
        return None
    try:
        ib = IB()
        ib.connect(host, port, clientId=client_id, readonly=False)
        return ib
    except Exception as exc:
        print(f"[ERROR] IB connect failed: {exc}")
        return None
