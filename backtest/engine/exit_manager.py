"""
engine/exit_manager.py — Complete exit logic.

Implements:
  1. Trailing stop at 10% below highest closing price (long)
     / 10% above lowest closing price (short)
  2. Five circuit breaker levels checked before trailing stop
  3. Short-to-long conversion in bull market only
  4. Stop only moves in favour of trade — never reverses

Exit priority order (checked each day):
  1. Circuit breaker level 1 — overnight gap
  2. Circuit breaker level 2 — earnings gap
  3. Circuit breaker level 4 — market-wide halt (flag only)
  4. Circuit breaker level 5 — VIX crisis (tighten stops)
  5. Circuit breaker level 3 — intraday halt (checked separately)
  6. Trailing stop check at end of day
"""

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

import pandas as pd

from backtest.config import CIRCUIT_BREAKERS, TRAILING_STOP

logger = logging.getLogger(__name__)


@dataclass
class OpenTrade:
    """Represents a live open trade being managed by the exit manager."""
    ticker:             str
    entry_date:         date
    entry_price:        float
    direction:          str           # 'long' or 'short'
    strategy:           str
    category:           str
    sector:             str           # from sp500_tickers.csv
    initial_stop:       float         # 10% from entry
    trailing_stop:      float         # current trailing stop (moves in favour)
    highest_close:      float         # highest close seen (long) / lowest (short)
    regime_at_entry:    str
    conversion_pair_id: Optional[str] = None
    circuit_breaker_triggered: Optional[int] = None
    signals_at_entry:   dict = field(default_factory=dict)
    context_bullets:    list = field(default_factory=list)
    context_paragraph:  str = ""
    confidence_tier:    str = "MEDIUM"
    preliminary_tier:   str = "MEDIUM"    # Stage 1 rule-based tier before agent adjustment
    agent_reasoning:    dict = field(default_factory=dict)  # full agent pipeline output
    smart_money_score:  int = 0
    macro_score:        int = 0
    sentiment_score:    int = 0
    days_to_earnings:   Optional[int] = None
    # MAE/MFE tracked across full trade duration — updated daily
    max_adverse_excursion:    float = 0.0  # worst % against trade seen during hold
    max_favourable_excursion: float = 0.0  # best % in favour seen during hold
    # Raw granular signals at entry
    congressional_signal: str = "none"
    insider_signal:       str = "none"
    institutional_signal: str = "none"
    aaii_bullish:         float = 0.0
    aaii_bearish:         float = 0.0
    aaii_signal:          str = "neutral"
    cnn_fg_score:         float = 50.0
    cnn_fg_label:         str = "Neutral"


# BUG-215 fix (Pass 48): removed duplicate older ClosedTrade dataclass that
# previously lived here. Canonical definition follows below — has 41 fields
# vs the old 38, includes `sector` at the canonical position after `regime`,
# and properly defaults `conversion_pair_id` / `circuit_breaker_level` as
# Optional fields. The duplicate was being silently overwritten by Python.


@dataclass
class ClosedTrade:
    """A completed trade with full performance record."""
    # Identity
    ticker:             str
    entry_date:         date
    exit_date:          date
    direction:          str
    strategy:           str
    category:           str
    sector:             str
    confidence_tier:    str
    regime:             str
    exit_reason:        str

    # Prices
    entry_price:        float
    exit_price:         float
    initial_stop:       float
    highest_close:      float
    trailing_stop_at_exit: float

    # Performance
    pnl_pct:            float
    pnl_dollar:         float
    win:                bool
    hold_days:          int
    max_adverse_excursion:   float
    max_favourable_excursion: float

    # Context
    signals_at_entry:   dict
    context_bullets:    list
    context_paragraph:  str
    fail_reason:        str

    # Smart money / macro / sentiment scores
    smart_money_score:  int = 0
    macro_score:        int = 0
    sentiment_score:    int = 0

    # Optional fields
    conversion_pair_id:    Optional[str] = None
    circuit_breaker_level: Optional[int] = None
    days_to_earnings:      Optional[int] = None
    preliminary_tier:      str = "MEDIUM"   # before agent adjustment
    agent_reasoning:       dict = field(default_factory=dict)  # full agent output

    # Raw granular signals at entry — for audit and re-analysis
    congressional_signal: str = "none"
    insider_signal:       str = "none"
    institutional_signal: str = "none"
    aaii_bullish:         float = 0.0
    aaii_bearish:         float = 0.0
    aaii_signal:          str = "neutral"
    cnn_fg_score:         float = 50.0
    cnn_fg_label:         str = "Neutral"


def _pnl(entry, exit_p, direction, hold_days=0):
    if direction == "long":
        return (exit_p - entry) / entry * 100
    # Short PnL minus daily borrow cost
    from backtest.config import SHORT_BORROW_COST_PER_DAY
    raw = (entry - exit_p) / entry * 100
    borrow_cost = SHORT_BORROW_COST_PER_DAY * max(hold_days, 1)
    return raw - borrow_cost


def check_circuit_breakers(
    trade: OpenTrade,
    today_open: float,
    prev_close: float,
    vix_value: Optional[float],
) -> Optional[dict]:
    """
    Check all circuit breakers at market open.
    Returns dict with level and action if triggered, else None.
    """
    cb = CIRCUIT_BREAKERS

    # Level 1 — overnight gap
    if prev_close > 0:
        gap_pct = (today_open - prev_close) / prev_close
        if trade.direction == "long" and gap_pct <= -cb["level_1_gap_pct"]:
            return {"level": 1, "action": "exit_at_open",
                    "reason": f"overnight_gap_down_{abs(gap_pct)*100:.1f}pct"}
        if trade.direction == "short" and gap_pct >= cb["level_1_gap_pct"]:
            return {"level": 1, "action": "exit_at_open",
                    "reason": f"overnight_gap_up_{gap_pct*100:.1f}pct"}

    # Level 2 — earnings gap (checked separately with earnings flag)
    if trade.days_to_earnings == 0:
        gap_pct = (today_open - prev_close) / prev_close if prev_close > 0 else 0
        if trade.direction == "long" and gap_pct <= -cb["level_2_earnings_gap_pct"]:
            return {"level": 2, "action": "exit_at_open",
                    "reason": f"earnings_gap_down_{abs(gap_pct)*100:.1f}pct"}
        if trade.direction == "short" and gap_pct >= cb["level_2_earnings_gap_pct"]:
            return {"level": 2, "action": "exit_at_open",
                    "reason": f"earnings_gap_up_{gap_pct*100:.1f}pct"}

    # Level 5 — VIX crisis (tighten stops, no new longs — existing positions tighten)
    if vix_value and vix_value >= cb["level_5_vix_crisis"]:
        return {"level": 5, "action": "tighten_stop",
                "new_pct": cb["level_5_tightened_pct"],
                "reason": f"vix_crisis_{vix_value:.1f}"}

    return None


def update_trailing_stop(trade: OpenTrade, today_close: float, vix_value: Optional[float] = None) -> OpenTrade:
    """
    Update trailing stop based on today's closing price.
    Stop only moves in favour of trade — never reverses.
    """
    cb  = CIRCUIT_BREAKERS
    pct = cb["level_5_tightened_pct"] if (vix_value and vix_value >= cb["level_5_vix_crisis"]) \
          else TRAILING_STOP["trail_pct"]

    if trade.direction == "long":
        if today_close > trade.highest_close:
            trade.highest_close   = today_close
            new_stop              = today_close * (1 - pct)
            # Stop only moves up
            trade.trailing_stop   = max(trade.trailing_stop, new_stop)
    else:  # short
        if today_close < trade.highest_close:
            trade.highest_close   = today_close
            new_stop              = today_close * (1 + pct)
            # Stop only moves down
            trade.trailing_stop   = min(trade.trailing_stop, new_stop)

    return trade


def check_trailing_stop_hit(trade: OpenTrade, today_low: float, today_high: float,
                              today_close: float) -> Optional[float]:
    """
    Check if trailing stop was breached during the day.
    Uses daily Low (long) or daily High (short) — the intraday extreme.
    This correctly reflects that a real stop order triggers if price TRADES through
    the stop at any point during the day, not just at close.

    Exit price = trailing stop level (not the low/high — stop is a limit price).
    If stock gaps through stop entirely (low < stop by large margin), the
    gap-down circuit breaker handles the extreme case separately.

    More conservative than close-based: ~2-4pp lower win rate expected but realistic.
    """
    if trade.direction == "long":
        if today_low <= trade.trailing_stop:
            return trade.trailing_stop  # exit at stop price, not at low
    else:
        if today_high >= trade.trailing_stop:
            return trade.trailing_stop  # exit at stop price, not at high
    return None


def close_trade(
    trade: OpenTrade,
    exit_price: float,
    exit_date: date,
    exit_reason: str,
    max_adverse: float,
    max_favourable: float,
    fail_reason: str = "",
) -> ClosedTrade:
    """Convert an OpenTrade to a ClosedTrade with full performance metrics."""
    # BUG-214 fix (Pass 48): days must be computed BEFORE _pnl() call
    days  = (exit_date - trade.entry_date).days
    pnl   = _pnl(trade.entry_price, exit_price, trade.direction, days)
    win   = pnl > 0

    if not win and not fail_reason:
        # Auto-generate fail reason
        if exit_reason.startswith("circuit_breaker"):
            fail_reason = f"Circuit breaker level {trade.circuit_breaker_triggered} triggered"
        elif pnl < -8:
            fail_reason = "Large loss — trailing stop could not prevent full decline"
        else:
            fail_reason = "Price declined below trailing stop — trend reversed"

    return ClosedTrade(
        ticker=trade.ticker, entry_date=trade.entry_date, exit_date=exit_date,
        direction=trade.direction, strategy=trade.strategy, category=trade.category,
        sector=trade.sector,
        confidence_tier=trade.confidence_tier, regime=trade.regime_at_entry,
        conversion_pair_id=trade.conversion_pair_id,
        entry_price=trade.entry_price, exit_price=round(exit_price,4),
        initial_stop=trade.initial_stop, highest_close=trade.highest_close,
        trailing_stop_at_exit=trade.trailing_stop,
        circuit_breaker_level=trade.circuit_breaker_triggered,
        exit_reason=exit_reason,
        pnl_pct=round(pnl,4), pnl_dollar=round(pnl/100*10000,2),
        win=win, hold_days=days,
        # Use trade-level MAE/MFE (accumulated over full hold period, not just today)
        max_adverse_excursion=round(trade.max_adverse_excursion, 4),
        max_favourable_excursion=round(trade.max_favourable_excursion, 4),
        signals_at_entry=trade.signals_at_entry,
        context_bullets=trade.context_bullets,
        context_paragraph=trade.context_paragraph,
        fail_reason=fail_reason,
        smart_money_score=trade.smart_money_score,
        macro_score=trade.macro_score,
        sentiment_score=trade.sentiment_score,
        days_to_earnings=trade.days_to_earnings,
        preliminary_tier=trade.preliminary_tier,
        agent_reasoning=trade.agent_reasoning,
        # Raw granular signals — passed through from OpenTrade
        congressional_signal=trade.congressional_signal,
        insider_signal=trade.insider_signal,
        institutional_signal=trade.institutional_signal,
        aaii_bullish=trade.aaii_bullish,
        aaii_bearish=trade.aaii_bearish,
        aaii_signal=trade.aaii_signal,
        cnn_fg_score=trade.cnn_fg_score,
        cnn_fg_label=trade.cnn_fg_label,
    )


def process_day_exits(
    open_trades: list[OpenTrade],
    ticker_bars: dict,          # {ticker: today's bar dict with open/high/low/close}
    today_date: date,
    vix_value: Optional[float],
    regime: str,
    active_signals: dict,       # {ticker: screener candidate} for conversion check
    circuit_breaker_log: list,
) -> tuple[list[ClosedTrade], list[OpenTrade]]:
    """
    Process all open trades for a single day.
    Returns (closed_trades, remaining_open_trades).
    """
    closed   = []
    still_open = []

    for trade in open_trades:
        bar = ticker_bars.get(trade.ticker)
        if not bar:
            still_open.append(trade)
            continue

        today_open  = bar["open"]
        today_high  = bar["high"]
        today_low   = bar["low"]
        today_close = bar["close"]
        prev_close  = bar.get("prev_close", today_open)

        # ── Update MAE/MFE across full trade duration ──
        # Accumulate worst adverse and best favourable excursion seen so far
        ep = trade.entry_price
        if ep > 0:
            if trade.direction == "long":
                today_adv = (today_low  - ep) / ep * 100   # negative = adverse
                today_fav = (today_high - ep) / ep * 100   # positive = favourable
            else:
                today_adv = (ep - today_high) / ep * 100   # short: high is adverse
                today_fav = (ep - today_low)  / ep * 100   # short: low is favourable
            trade.max_adverse_excursion    = min(trade.max_adverse_excursion,    today_adv)
            trade.max_favourable_excursion = max(trade.max_favourable_excursion, today_fav)

        # ── Step 1: Circuit breaker check ──
        cb_result = check_circuit_breakers(trade, today_open, prev_close, vix_value)

        if cb_result and cb_result["action"] == "exit_at_open":
            trade.circuit_breaker_triggered = cb_result["level"]
            closed.append(close_trade(
                trade, today_open, today_date,
                f"circuit_breaker_{cb_result['level']}",
                0.0, 0.0,  # MAE/MFE now on trade object
                fail_reason=cb_result["reason"],
            ))
            circuit_breaker_log.append({
                "date": today_date, "ticker": trade.ticker,
                "level": cb_result["level"], "reason": cb_result["reason"],
                "exit_price": today_open,
            })

            # ── Conversion check after CB exit ──
            if (regime == "bull" and trade.direction == "short"):
                long_signal = active_signals.get(trade.ticker)
                if long_signal and long_signal.get("long_count", 0) > 0:
                    closed[-1].conversion_pair_id = f"convert_{trade.ticker}_{today_date}"
            continue

        if cb_result and cb_result["action"] == "tighten_stop":
            new_pct = cb_result["new_pct"]
            if trade.direction == "long":
                trade.trailing_stop = max(trade.trailing_stop,
                                          trade.highest_close * (1 - new_pct))
            else:
                trade.trailing_stop = min(trade.trailing_stop,
                                          trade.highest_close * (1 + new_pct))

        # ── Step 2: Update trailing stop from today's close ──
        trade = update_trailing_stop(trade, today_close, vix_value)

        # ── Step 3: Check if trailing stop was hit (uses intraday low/high) ──
        exit_price = check_trailing_stop_hit(trade, today_low, today_high, today_close)

        if exit_price is not None:
            closed.append(close_trade(
                trade, exit_price, today_date, "trailing_stop",
                0.0, 0.0,  # MAE/MFE now on trade object
            ))

            # ── Conversion check after trailing stop exit ──
            if regime == "bull" and trade.direction == "short":
                long_signal = active_signals.get(trade.ticker)
                if long_signal and long_signal.get("long_count", 0) > 0:
                    closed[-1].conversion_pair_id = f"convert_{trade.ticker}_{today_date}"
            continue

        still_open.append(trade)

    return closed, still_open
