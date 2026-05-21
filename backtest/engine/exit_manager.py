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


def _check_per_strategy_exit_hit(
    trade: "OpenTrade",
    today_high: float,
    today_low: float,
    today_close: float,
    today_date: date,
) -> tuple:
    """Batch 284 (2026-05-20 owner-approved): per-strategy exit method
    dispatch. Returns (exit_price, exit_reason) if the strategy's
    configured exit_method triggered today, else (None, None).

    Supported exit methods (per-day evaluable):
      - 'fixed_4r_2r':    hard target +4R / hard stop -2R from entry
      - 'r_multiple_2r':  hard target +2R from entry
      - 'r_multiple_3r':  hard target +3R from entry
      - 'class_time_stop': category-specific time exit (Kestner 2003)
      - 'breakeven_plus_trail': move stop to entry at +1xATR, then trail 10%
                                (handled via existing breakeven_move_at_1r
                                in update_trailing_stop; this branch is a
                                no-op tagged for completeness)
      - 'ma_exit_ema9':    deferred to Batch 285 (requires close history)

    R = |entry_price - initial_stop|. ATR-as-R approximation when initial_stop
    is missing or zero: R = entry_price * 0.02.
    """
    from backtest.config import STRATEGY_EXIT_OVERRIDE as _SEO
    override = _SEO.get(trade.strategy, {})
    method = override.get("exit_method")
    if not method:
        return (None, None)
    ep = trade.entry_price
    if ep <= 0:
        return (None, None)
    # R-multiple base
    if trade.initial_stop and trade.initial_stop > 0:
        r_value = abs(ep - trade.initial_stop)
    else:
        r_value = ep * 0.02   # fallback per ATR_FALLBACK_PCT semantics
    if r_value <= 0:
        return (None, None)

    direction = trade.direction

    # ---------------- fixed_4r_2r ----------------
    if method == "fixed_4r_2r":
        target_r = 4.0
        stop_r = 2.0
        if direction == "long":
            target_price = ep + target_r * r_value
            stop_price = ep - stop_r * r_value
            if today_high >= target_price:
                return (target_price, "fixed_4r_2r_target_hit_batch284")
            if today_low <= stop_price:
                return (stop_price, "fixed_4r_2r_stop_hit_batch284")
        else:  # short
            target_price = ep - target_r * r_value
            stop_price = ep + stop_r * r_value
            if today_low <= target_price:
                return (target_price, "fixed_4r_2r_target_hit_batch284")
            if today_high >= stop_price:
                return (stop_price, "fixed_4r_2r_stop_hit_batch284")
        return (None, None)

    # ---------------- r_multiple_2r / 3r ----------------
    if method in ("r_multiple_2r", "r_multiple_3r"):
        n_r = 2.0 if method == "r_multiple_2r" else 3.0
        if direction == "long":
            target_price = ep + n_r * r_value
            if today_high >= target_price:
                return (target_price, f"{method}_target_hit_batch284")
        else:
            target_price = ep - n_r * r_value
            if today_low <= target_price:
                return (target_price, f"{method}_target_hit_batch284")
        return (None, None)

    # ---------------- class_time_stop ----------------
    # Time-based per-category exit. Hard close at category-specific window.
    # Distinct from Batch 213's MFE-conditional time stop (which only fires
    # on under-developing trades). This one always closes at the window.
    if method == "class_time_stop":
        cat = (trade.category or "").lower()
        window = {
            "mean_reversion": 10,
            "momentum":       30,
            "trend":          50,
        }.get(cat, 20)
        hold_days = (today_date - trade.entry_date).days
        if hold_days >= window:
            return (today_close, f"class_time_stop_{cat}_{window}d_batch284")
        return (None, None)

    # ---------------- breakeven_plus_trail ----------------
    # Already implemented via TRAILING_STOP["breakeven_move_at_1r"] flag
    # (always-on per Batch 281). Per-strategy override of this method is
    # a no-op since the global default already applies. Future: per-strategy
    # breakeven_at_R override could differentiate (e.g., 0.5R vs 1.0R).
    if method == "breakeven_plus_trail":
        return (None, None)

    # ---------------- ma_exit_ema9 ----------------
    # Deferred to Batch 285 - requires close history not available here.
    if method == "ma_exit_ema9":
        return (None, None)

    # Unknown method - fall through to default
    return (None, None)


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
    # BUG-30 RESOLVED-IMPLEMENTED Batch 114 2026-05-12: gated on
    # cb["level_5_tighten_in_crisis"] (default True; set False to skip).
    if (
        vix_value and vix_value >= cb["level_5_vix_crisis"]
        and cb.get("level_5_tighten_in_crisis", True)
    ):
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
    # BUG-30 RESOLVED-IMPLEMENTED Batch 114 2026-05-12: Level-5 VIX-crisis
    # tighten is now config-toggleable. When level_5_tighten_in_crisis is
    # True (default), VIX>=crisis ratchets to the tightened pct as before.
    # When False, the trail uses standard trail_pct even during crisis -
    # DEC-091 DD-band sizing + DEC-088 vol-target stay the only crisis-
    # mode exposure reductions.
    _l5_enabled = cb.get("level_5_tighten_in_crisis", True)
    in_crisis = bool(vix_value and vix_value >= cb["level_5_vix_crisis"])
    # Batch 282 (2026-05-20 owner-approved): per-strategy trail_pct override.
    # Falls back to TRAILING_STOP["trail_pct"] when strategy not in override
    # dict. Crisis-tighten still takes precedence over per-strategy override.
    from backtest.config import STRATEGY_EXIT_OVERRIDE as _SEO
    _strat_override = _SEO.get(trade.strategy, {}) if hasattr(trade, "strategy") else {}
    _strat_trail_pct = _strat_override.get("trail_pct", TRAILING_STOP["trail_pct"])
    if _l5_enabled and in_crisis:
        pct = cb["level_5_tightened_pct"]
    else:
        pct = _strat_trail_pct
    ratchet_from = TRAILING_STOP.get("ratchet_from", "close")

    # Batch 262: breakeven-at-1R logic. Once trade hits +1R (= |entry -
    # initial_stop| favourable from entry), ratchet stop to BREAKEVEN
    # (entry price). Locks in $0-worst-case while preserving trailing
    # upside. Reduces 12.58pp avg give-back observed in 1A-alpha post-
    # mortem. Disabled when initial_stop unavailable or 1R not yet hit.
    breakeven_enabled = TRAILING_STOP.get("breakeven_move_at_1r", False)
    if breakeven_enabled and trade.initial_stop and trade.entry_price:
        ep = trade.entry_price
        init_stop = trade.initial_stop
        one_r = abs(ep - init_stop)
        if one_r > 0:
            if trade.direction == "long":
                if today_close >= ep + one_r:
                    trade.trailing_stop = max(trade.trailing_stop, ep)
            else:  # short
                if today_close <= ep - one_r:
                    trade.trailing_stop = min(trade.trailing_stop, ep) if trade.trailing_stop > 0 else ep

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
    vix_history: Optional[list] = None,
) -> tuple[list[ClosedTrade], list[OpenTrade]]:
    """
    Process all open trades for a single day.
    Returns (closed_trades, remaining_open_trades).

    Batch 268 (2026-05-20 owner-approved): REMOVED vix_spike_kill_switch
    (originally Batch 226). Counterfactual bootstrap on 91 trades that
    exited via vix_kill in the 20tkr x 2y smoke showed vix_kill cost
    -6.98% per trade vs trailing_15pct (95% CI [-11.35%, -3.00%],
    p=0.0005). The "profit-protect" interpretation was wrong - vix_kill
    cuts winners short during transient VIX spikes that resolve
    favorably. Trailing_15pct + breakeven-at-1R (Batch 262) handles
    volatility-driven exits without truncating recoveries.

    vix_history parameter retained for backward compatibility with
    callers; no longer consumed in this function. May be re-introduced
    in a regime-gated form (e.g., only fire when regime in {bear,
    crisis} AND VIX absolute > 35) if portfolio-level drawdowns emerge
    at Phase 1A-alpha/beta scale.
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

        # -- Step 1.5: Per-strategy exit_method check (Batch 284) --
        # When STRATEGY_EXIT_OVERRIDE[strategy].exit_method is set, run the
        # method-specific check BEFORE the default trailing stop. If it
        # triggers, close the trade with the method's exit_reason. If it
        # doesn't trigger, fall through to the default trailing stop logic
        # as backstop. Per-strategy exit replaces dominance order; default
        # trailing stop is now the backstop, not the primary.
        try:
            _per_strat_exit_price, _per_strat_exit_reason = (
                _check_per_strategy_exit_hit(
                    trade, today_high, today_low, today_close, today_date,
                )
            )
            if _per_strat_exit_price is not None:
                from backtest.engine.improvements import apply_exit_slippage
                ps_exit_price, _ = apply_exit_slippage(
                    _per_strat_exit_price, trade.direction, trade.ticker)
                closed.append(close_trade(
                    trade, ps_exit_price, today_date,
                    _per_strat_exit_reason, 0.0, 0.0,
                ))
                # Conversion check (mirror of trailing_stop conversion below)
                if regime == "bull" and trade.direction == "short":
                    long_signal = active_signals.get(trade.ticker)
                    if long_signal and long_signal.get("long_count", 0) > 0:
                        closed[-1].conversion_pair_id = (
                            f"convert_{trade.ticker}_{today_date}"
                        )
                continue
        except Exception as exc:
            logger.debug("per-strategy exit check failed for %s: %s",
                          trade.strategy, exc)

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

        # Batch 282 (2026-05-20 owner-approved): per-strategy hard time_stop.
        # When STRATEGY_EXIT_OVERRIDE[strategy].time_stop_days is set, force-
        # close the trade at that many bars regardless of MFE. Distinct from
        # the existing Batch 213 MFE-conditional time-stop below (which only
        # fires on under-developing trades).
        try:
            from backtest.config import STRATEGY_EXIT_OVERRIDE as _SEO
            _strat_override = _SEO.get(trade.strategy, {})
            _hard_time_stop = _strat_override.get("time_stop_days")
            if _hard_time_stop is not None:
                hold_days = (today_date - trade.entry_date).days
                if hold_days >= _hard_time_stop:
                    from backtest.engine.improvements import apply_exit_slippage
                    ts_exit_price, _ = apply_exit_slippage(
                        today_close, trade.direction, trade.ticker)
                    closed.append(close_trade(
                        trade, ts_exit_price, today_date,
                        f"strategy_time_stop_{_hard_time_stop}d_batch282",
                        0.0, 0.0,
                    ))
                    continue
        except Exception:
            pass

        # -- Step 4: Time-stop discipline (Batch 213 2026-05-17 owner-approved
        # research review) - Lars Kestner "Quantitative Trading Strategies"
        # (2003): hard-close trades that fail to develop favourable
        # excursion within a sample-size window. Frees capital from "drift
        # trades" that consume risk budget without producing returns.
        # Per-category window:
        #   mean_reversion: 10 bars (Connors mean-rev decay rate)
        #   momentum:       30 bars (allow trend continuation)
        #   trend:          50 bars (longer-horizon)
        #   smc / vwap / orb / event_driven / pivot / breakout: 20 bars
        # Trigger: MFE < 0.5 x avg_true_range_pct after window_days bars.
        try:
            hold_days = (today_date - trade.entry_date).days
            cat = (trade.category or "").lower()
            window = {
                "mean_reversion": 10,
                "momentum":       30,
                "trend":          50,
            }.get(cat, 20)
            # Approximate ATR-pct threshold: use entry_price * 1% as floor.
            # Real ATR was at entry; use a fraction of entry_price as proxy.
            mfe_threshold = 0.5  # 0.5% MFE minimum to keep position open
            if hold_days >= window and trade.max_favourable_excursion < mfe_threshold:
                from backtest.engine.improvements import apply_exit_slippage
                ts_exit_price, _ = apply_exit_slippage(today_close, trade.direction, trade.ticker)
                closed.append(close_trade(
                    trade, ts_exit_price, today_date,
                    f"time_stop_{window}d_mfe<{mfe_threshold}pct_batch213",
                    0.0, 0.0,
                ))
                continue
        except Exception:
            pass

        still_open.append(trade)

    return closed, still_open
