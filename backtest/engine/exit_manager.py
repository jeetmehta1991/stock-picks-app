"""
engine/exit_manager.py  -  Complete exit logic.

Implements:
  1. Trailing stop at 10% below highest closing price (long)
     / 10% above lowest closing price (short)
  2. Five circuit breaker levels checked before trailing stop
  3. Short-to-long conversion in bull market only
  4. Stop only moves in favour of trade  -  never reverses

Exit priority order (checked each day):
  1. Circuit breaker level 1  -  overnight gap
  2. Circuit breaker level 2  -  earnings gap
  3. Circuit breaker level 4  -  market-wide halt (flag only)
  4. Circuit breaker level 5  -  VIX crisis (tighten stops)
  5. Circuit breaker level 3  -  intraday halt (checked separately)
  6. Trailing stop check at end of day
"""

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

import pandas as pd

from backtest.config import CIRCUIT_BREAKERS, TRAILING_STOP

logger = logging.getLogger(__name__)


def make_trade_id(ticker: str, entry_date: date, strategy: str,
                    direction: str = "long", seq: int = 0) -> str:
    """DEC-493  -  generate a time-ordered, human-readable trade_id.

    Format: ``T-{TICKER}-{YYYY-MM-DD}-{STRATEGY}-{DIR}-{SEQ}``

    Sortable lexicographically. Collision-free for unique
    (ticker, entry_date, strategy, direction) within a single backtest. The
    optional ``seq`` field disambiguates the rare case of multiple identical
    entries on the same bar (e.g. signal re-fires). Phase 1B+ may add a
    secondary uuid4 field for cross-table joins; Phase 1A baseline uses this
    composite.
    """
    safe_ticker = str(ticker).replace(".", "_")
    safe_strategy = str(strategy).replace(" ", "_").replace("/", "_")[:32]
    safe_dir = "L" if direction == "long" else "S"
    return f"T-{safe_ticker}-{entry_date}-{safe_strategy}-{safe_dir}-{seq}"


@dataclass
class OpenTrade:
    """Represents a live open trade being managed by the exit manager."""
    ticker:             str
    entry_date:         date
    entry_price:        float
    direction:          str           # 'long' or 'short'
    strategy:           str
    category:           str
    sector:             str           # from Current Snapshot_SP500 Tickers_May 2026.csv
    initial_stop:       float         # 10% from entry
    trailing_stop:      float         # current trailing stop (moves in favour)
    highest_close:      float         # highest close seen (long) / lowest (short)
    regime_at_entry:    str
    conversion_pair_id: Optional[str] = None
    # DEC-493 (Pass 53 Sprint 2): unique trade_id field
    trade_id:           Optional[str] = None
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
    # MAE/MFE tracked across full trade duration  -  updated daily
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
# previously lived here. Canonical definition follows below  -  has 41 fields
# vs the old 38, includes `sector` at the canonical position after `regime`,
# and properly defaults `conversion_pair_id` / `circuit_breaker_level` as
# Optional fields. The duplicate was being silently overwritten by Python.


@dataclass
class ClosedTrade:
    """A completed trade with full performance record.

    BUG-03 RESOLVED-IMPLEMENTED Pass 53 v8h+1 cross-reference 2026-05-10:
    canonical single definition (duplicate in another module was removed).
    This is the only ClosedTrade class in the codebase; engine + exits +
    tests all import from here.
    """
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

    # Raw granular signals at entry  -  for audit and re-analysis
    congressional_signal: str = "none"
    insider_signal:       str = "none"
    institutional_signal: str = "none"
    aaii_bullish:         float = 0.0
    aaii_bearish:         float = 0.0
    aaii_signal:          str = "neutral"
    cnn_fg_score:         float = 50.0
    cnn_fg_label:         str = "Neutral"
    # DEC-493 (Pass 53 Sprint 2): unique trade_id propagated from OpenTrade
    trade_id:             Optional[str] = None


def _pnl(entry, exit_p, direction, hold_days=0):
    """
    Gross percentage PnL for a trade. DOES NOT subtract borrow cost  -  that is
    applied centrally in improvements.apply_transaction_costs (DEC-295 fix,
    Pass 50). hold_days kept in signature for backward compatibility but unused.
    """
    if direction == "long":
        return (exit_p - entry) / entry * 100
    # Short: gross only; borrow cost handled elsewhere
    return (entry - exit_p) / entry * 100


def check_circuit_breakers_all(
    trade: OpenTrade,
    today_open: float,
    prev_close: float,
    vix_value: Optional[float],
) -> list[dict]:
    """
    Check ALL circuit breakers at market open and return every one that triggered.

    DEC-315 fix (Pass 51): previously check_circuit_breakers returned only the
    FIRST triggered breaker. If today had both Level 1 (overnight gap) AND
    Level 5 (VIX crisis), Level 1 fired and Level 5 was missed silently.
    Now caller receives the full list and can apply all relevant actions
    (e.g., exit_at_open is terminal for that trade; tighten_stop is additive
    for surviving positions).
    """
    cb = CIRCUIT_BREAKERS
    results = []

    # Level 1  -  overnight gap
    if prev_close > 0:
        gap_pct = (today_open - prev_close) / prev_close
        if trade.direction == "long" and gap_pct <= -cb["level_1_gap_pct"]:
            results.append({"level": 1, "action": "exit_at_open",
                            "reason": f"overnight_gap_down_{abs(gap_pct)*100:.1f}pct"})
        elif trade.direction == "short" and gap_pct >= cb["level_1_gap_pct"]:
            results.append({"level": 1, "action": "exit_at_open",
                            "reason": f"overnight_gap_up_{gap_pct*100:.1f}pct"})

    # Level 2  -  earnings gap
    if trade.days_to_earnings == 0 and prev_close > 0:
        gap_pct = (today_open - prev_close) / prev_close
        if trade.direction == "long" and gap_pct <= -cb["level_2_earnings_gap_pct"]:
            results.append({"level": 2, "action": "exit_at_open",
                            "reason": f"earnings_gap_down_{abs(gap_pct)*100:.1f}pct"})
        elif trade.direction == "short" and gap_pct >= cb["level_2_earnings_gap_pct"]:
            results.append({"level": 2, "action": "exit_at_open",
                            "reason": f"earnings_gap_up_{gap_pct*100:.1f}pct"})

    # Level 5  -  VIX crisis (tighten stops; additive  -  does not exit position)
    if vix_value and vix_value >= cb["level_5_vix_crisis"]:
        results.append({"level": 5, "action": "tighten_stop",
                        "new_pct": cb["level_5_tightened_pct"],
                        "reason": f"vix_crisis_{vix_value:.1f}"})

    return results


def check_circuit_breakers(
    trade: OpenTrade,
    today_open: float,
    prev_close: float,
    vix_value: Optional[float],
) -> Optional[dict]:
    """
    Backward-compat wrapper around check_circuit_breakers_all.

    Returns the FIRST triggered circuit breaker, or None. New callers should
    use check_circuit_breakers_all for full visibility (DEC-315). Existing
    callers continue to receive the highest-priority single result.
    """
    results = check_circuit_breakers_all(trade, today_open, prev_close, vix_value)
    return results[0] if results else None


def update_trailing_stop(
    trade:        OpenTrade,
    today_close:  float,
    vix_value:    Optional[float] = None,
    today_high:   Optional[float] = None,
    today_low:    Optional[float] = None,
) -> OpenTrade:
    """
    Update trailing stop based on today's price.
    Stop only moves in favour of trade  -  never reverses.

    BUG-232 RESOLVED-IMPLEMENTED Batch 113 2026-05-12 (owner-approved
    option C 2026-05-12): trailing-ratchet source is config-toggleable
    via TRAILING_STOP["ratchet_from"]:
      "close" (default, conservative): advance the stop only when
        today_close beats highest_close. Less whipsaw, gives up some
        intraday gains.
      "intraday_extreme": advance the stop from today_high (longs)
        / today_low (shorts). Locks gains from favourable intraday
        excursions faster but causes more whipsaw stops.
    Falls back to "close" if today_high/today_low not supplied by caller.
    """
    cb  = CIRCUIT_BREAKERS
    pct = cb["level_5_tightened_pct"] if (vix_value and vix_value >= cb["level_5_vix_crisis"]) \
          else TRAILING_STOP["trail_pct"]
    ratchet_from = TRAILING_STOP.get("ratchet_from", "close")

    if trade.direction == "long":
        # Pick the favourable reference price per config toggle
        if ratchet_from == "intraday_extreme" and today_high is not None:
            ref_price = today_high
        else:
            ref_price = today_close
        if ref_price > trade.highest_close:
            trade.highest_close   = ref_price
            new_stop              = ref_price * (1 - pct)
            # Stop only moves up
            trade.trailing_stop   = max(trade.trailing_stop, new_stop)
    else:  # short
        if ratchet_from == "intraday_extreme" and today_low is not None:
            ref_price = today_low
        else:
            ref_price = today_close
        if ref_price < trade.highest_close:
            trade.highest_close   = ref_price
            new_stop              = ref_price * (1 + pct)
            # Stop only moves down
            trade.trailing_stop   = min(trade.trailing_stop, new_stop)

    return trade


def compute_fill_price(
    direction: str,
    level_type: str,
    level: float,
    bar_open: float,
    bar_high: float,
    bar_low: float,
) -> Optional[float]:
    """DEC-514  -  Backtest fill methodology (Pass 53 owner-approved 2026-05-06 Q1 P0).

    Compute the realistic fill price when a stop or target is hit on an EOD bar.
    Without this helper, code that returns ``level`` directly silently
    understates downside on overnight gap-downs (every gap-through-stop fills
    at stop, but a real broker fills at open  -  the gap-loss is real).

    Spec source: TRADING_RULES_AND_INFORMATION.md section11.

    Args:
        direction:  ``'long'`` or ``'short'``
        level_type: ``'stop'`` (loss-side) or ``'target'`` (profit-side)
        level:      stop or target price
        bar_open / bar_high / bar_low: today's OHLC
            (close is not needed for fill calculation; intraday triggers happen
             before close).

    Returns:
        Fill price, or ``None`` if the level was not crossed this bar.

    Six rules  -  symmetric across long/short:
      Long stop:    low > stop                -> None
                    low <= stop <= open         -> fill at stop
                    open < stop (gap-through) -> fill at open
      Long target:  high < target             -> None
                    high >= target >= open      -> fill at target
                    open > target (gap-up)    -> fill at open  (favourable)
      Short stop:   high < stop               -> None
                    high >= stop >= open        -> fill at stop
                    open > stop (gap-up)      -> fill at open  (adverse)
      Short target: low > target              -> None
                    low <= target <= open       -> fill at target
                    open < target (gap-down)  -> fill at open  (favourable)
    """
    if direction == "long":
        if level_type == "stop":
            # Stop is BELOW entry. Hit if intraday low touches it.
            if bar_low > level:
                return None
            if bar_open < level:
                return bar_open  # Gap-down through stop  -  fill at open
            return level
        elif level_type == "target":
            # Target is ABOVE entry. Hit if intraday high touches it.
            if bar_high < level:
                return None
            if bar_open > level:
                return bar_open  # Gap-up through target  -  favourable fill at open
            return level
    elif direction == "short":
        if level_type == "stop":
            # Stop is ABOVE entry. Hit if intraday high touches it.
            if bar_high < level:
                return None
            if bar_open > level:
                return bar_open  # Gap-up through stop  -  adverse fill at open
            return level
        elif level_type == "target":
            # Target is BELOW entry. Hit if intraday low touches it.
            if bar_low > level:
                return None
            if bar_open < level:
                return bar_open  # Gap-down through target  -  favourable fill at open
            return level
    raise ValueError(f"Invalid direction='{direction}' or level_type='{level_type}'")


def check_trailing_stop_hit(trade: OpenTrade, today_low: float, today_high: float,
                              today_close: float, today_open: Optional[float] = None
                              ) -> Optional[float]:
    """
    Check if trailing stop was breached during the day.

    Pass 53 Day-9 v8e DEC-514 fix: now uses ``compute_fill_price()`` to apply
    the gap-through-stop rule (fill at open instead of stop when bar opened
    past the stop level). Falls back to legacy "fill at stop" if today_open
    not provided (backwards-compat).
    """
    if today_open is None:
        # Backwards-compat path (legacy callers without bar_open)
        if trade.direction == "long":
            if today_low <= trade.trailing_stop:
                return trade.trailing_stop
        else:
            if today_high >= trade.trailing_stop:
                return trade.trailing_stop
        return None

    return compute_fill_price(
        direction=trade.direction,
        level_type="stop",
        level=trade.trailing_stop,
        bar_open=today_open,
        bar_high=today_high,
        bar_low=today_low,
    )


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
            fail_reason = "Large loss  -  trailing stop could not prevent full decline"
        else:
            fail_reason = "Price declined below trailing stop  -  trend reversed"

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
        # Raw granular signals  -  passed through from OpenTrade
        congressional_signal=trade.congressional_signal,
        insider_signal=trade.insider_signal,
        institutional_signal=trade.institutional_signal,
        aaii_bullish=trade.aaii_bullish,
        aaii_bearish=trade.aaii_bearish,
        aaii_signal=trade.aaii_signal,
        cnn_fg_score=trade.cnn_fg_score,
        cnn_fg_label=trade.cnn_fg_label,
        # DEC-493 (Pass 53 Sprint 2): propagate trade_id from OpenTrade
        trade_id=trade.trade_id,
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

        # -- Update MAE/MFE across full trade duration --
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

        # -- Step 1: Circuit breaker check (DEC-315  -  process ALL triggered breakers) --
        cb_results = check_circuit_breakers_all(trade, today_open, prev_close, vix_value)
        # Find terminal action (exit_at_open) and additive action (tighten_stop)
        exit_cb    = next((r for r in cb_results if r["action"] == "exit_at_open"),  None)
        tighten_cb = next((r for r in cb_results if r["action"] == "tighten_stop"), None)

        if exit_cb:
            trade.circuit_breaker_triggered = exit_cb["level"]
            # BUG-80 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 15 2026-05-10:
            # apply exit slippage symmetrically to entry slippage; longs receive
            # below-trigger fill, shorts pay above-trigger.
            from backtest.engine.improvements import apply_exit_slippage
            cb_exit_price, _ = apply_exit_slippage(today_open, trade.direction, trade.ticker)
            closed.append(close_trade(
                trade, cb_exit_price, today_date,
                f"circuit_breaker_{exit_cb['level']}",
                0.0, 0.0,  # MAE/MFE now on trade object
                fail_reason=exit_cb["reason"],
            ))
            circuit_breaker_log.append({
                "date": today_date, "ticker": trade.ticker,
                "level": exit_cb["level"], "reason": exit_cb["reason"],
                "exit_price": today_open,
            })
            # If a tighten ALSO fired today, log it too (visible in audit trail)
            if tighten_cb:
                circuit_breaker_log.append({
                    "date": today_date, "ticker": trade.ticker,
                    "level": tighten_cb["level"], "reason": tighten_cb["reason"],
                    "note": "co-fired with exit; not applied (position already closing)",
                })

            # -- Conversion check after CB exit --
            if (regime == "bull" and trade.direction == "short"):
                long_signal = active_signals.get(trade.ticker)
                if long_signal and long_signal.get("long_count", 0) > 0:
                    closed[-1].conversion_pair_id = f"convert_{trade.ticker}_{today_date}"
            continue

        # No exit_at_open; if tighten_stop fired, apply it (additive  -  position survives)
        if tighten_cb:
            new_pct = tighten_cb["new_pct"]
            if trade.direction == "long":
                trade.trailing_stop = max(trade.trailing_stop,
                                          trade.highest_close * (1 - new_pct))
            else:
                trade.trailing_stop = min(trade.trailing_stop,
                                          trade.highest_close * (1 + new_pct))
            circuit_breaker_log.append({
                "date": today_date, "ticker": trade.ticker,
                "level": tighten_cb["level"], "reason": tighten_cb["reason"],
                "action": "tighten_stop", "new_stop": trade.trailing_stop,
            })

        # -- Step 2: Check if trailing stop was hit using YESTERDAY's stop --
        # BUG-78 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 14 2026-05-10:
        # Previously updated trailing_stop FROM today's close BEFORE checking against
        # today's intraday low/high - a classic lookahead bias. Real-time trading
        # can't know today's close at the time today's intraday low was made.
        # Correct order:
        #   1. Check today's intraday low/high against the EXISTING stop (set yesterday)
        #   2. AFTER the check, update highest_close + trailing_stop from today's close
        #      (for use on tomorrow's intraday check)
        # This eliminates the lookahead - the stop level used today is what was set
        # at end-of-day yesterday, never includes today's information.
        exit_price = check_trailing_stop_hit(trade, today_low, today_high, today_close,
                                              today_open=today_open)  # DEC-514

        if exit_price is not None:
            # BUG-80 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 15 2026-05-10:
            # apply exit slippage to trailing-stop trigger price too (sister of CB exit above).
            from backtest.engine.improvements import apply_exit_slippage
            ts_exit_price, _ = apply_exit_slippage(exit_price, trade.direction, trade.ticker)
            closed.append(close_trade(
                trade, ts_exit_price, today_date, "trailing_stop",
                0.0, 0.0,  # MAE/MFE now on trade object
            ))

            # -- Conversion check after trailing stop exit --
            if regime == "bull" and trade.direction == "short":
                long_signal = active_signals.get(trade.ticker)
                if long_signal and long_signal.get("long_count", 0) > 0:
                    closed[-1].conversion_pair_id = f"convert_{trade.ticker}_{today_date}"
            continue

        # -- Step 3: Update trailing stop from today's close (post-check, no lookahead) --
        # BUG-78 fix: this update runs AFTER the intraday check, so the new stop only
        # applies to tomorrow's intraday check, not today's.
        # BUG-232 fix: pass today_high/today_low so the ratchet can use
        # intraday_extreme when TRAILING_STOP["ratchet_from"] = "intraday_extreme".
        # Default config remains "close" - this is forward-compat plumbing.
        trade = update_trailing_stop(trade, today_close, vix_value, today_high=today_high, today_low=today_low)

        still_open.append(trade)

    return closed, still_open
