"""
engine/backtest.py — Main backtest orchestrator.

Daily loop:
  1. Slice OHLCV to point-in-time (as_of date)
  2. Classify regime (VIX + SPY)
  3. Fetch macro + sentiment snapshots
  4. Screen universe → candidates
  5. Validate entry zones (gap filter)
  6. Fetch smart money signals for top candidates
  7. Run TradingAgents (optional — Phase 1A/1B use Haiku)
  8. Open new trades with trailing stop initialised
  9. Process exits on existing open trades
  10. Log everything

All data is point-in-time. No future information ever used.
"""

import logging
import os
from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd

from backtest.config import (
    BACKTEST_START, BACKTEST_END, UNIVERSE, OUTPUT_DIR,
    TRAILING_STOP, AI_MODELS,
)
from backtest.data.fetcher import fetch_ohlcv_bulk, fetch_info, days_to_next_earnings
from backtest.data.macro import macro_snapshot
from backtest.data.sentiment import sentiment_snapshot
from backtest.data.smart_money import smart_money_score
from backtest.engine.regime_filter import get_regime_context, get_spy_ema200
from backtest.engine.exit_manager import (
    OpenTrade, ClosedTrade, process_day_exits, close_trade,
)
from backtest.signals.screener import screen_universe, validate_entry_zone

logger = logging.getLogger(__name__)


class BacktestEngine:

    def __init__(
        self,
        universe:             list  = None,
        start:                date  = BACKTEST_START,
        end:                  date  = BACKTEST_END,
        phase:                str   = "phase_1a",
        max_candidates_per_day: int = 10,
        run_agents:           bool  = False,
        output_dir:           str   = OUTPUT_DIR,
    ):
        self.universe   = universe or UNIVERSE
        self.start      = start
        self.end        = end
        self.phase      = phase
        self.max_cands  = max_candidates_per_day
        self.run_agents = run_agents
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Data stores
        self.ohlcv_dict:  dict[str, pd.DataFrame] = {}
        self.info_dict:   dict[str, dict]          = {}
        self.spy_df:      Optional[pd.DataFrame]   = None

        # Trade stores
        self.open_trades:    list[OpenTrade]  = []
        self.closed_trades:  list[ClosedTrade] = []
        self.skipped_trades: list[dict]        = []
        self.circuit_breaker_log: list[dict]   = []

    # ──────────────────────────────────────────────────────────────────────
    # DATA LOADING
    # ──────────────────────────────────────────────────────────────────────

    def load_data(self):
        from backtest.config import DATA_LOAD_START
        logger.info("Loading OHLCV for %d instruments (%s → %s)...",
                    len(self.universe), DATA_LOAD_START, self.end)
        self.ohlcv_dict = fetch_ohlcv_bulk(
            self.universe, start=DATA_LOAD_START, end=self.end, delay_sec=0.25)
        logger.info("Loaded %d/%d tickers", len(self.ohlcv_dict), len(self.universe))

        logger.info("Loading company info...")
        for t in self.universe:
            self.info_dict[t] = fetch_info(t)

        self.spy_df = self.ohlcv_dict.get("SPY")

    # ──────────────────────────────────────────────────────────────────────
    # MAIN LOOP
    # ──────────────────────────────────────────────────────────────────────

    def run(self):
        if not self.ohlcv_dict:
            self.load_data()

        trading_days = self._trading_days()
        logger.info("Starting backtest: %d days | phase=%s | agents=%s",
                    len(trading_days), self.phase, self.run_agents)

        for i, as_of in enumerate(trading_days):
            if i % 20 == 0:
                logger.info("Progress: %d/%d [%s] open=%d closed=%d",
                            i, len(trading_days), as_of,
                            len(self.open_trades), len(self.closed_trades))
            try:
                self._process_day(as_of)
            except Exception as exc:
                logger.error("Day %s failed: %s", as_of, exc, exc_info=True)

        logger.info("Backtest complete. Open=%d Closed=%d Skipped=%d",
                    len(self.open_trades), len(self.closed_trades), len(self.skipped_trades))

    def _trading_days(self) -> list[date]:
        days, d = [], self.start
        while d <= self.end:
            if d.weekday() < 5:
                days.append(d)
            d += timedelta(days=1)
        return days

    def _process_day(self, as_of: date):
        # ── Slice OHLCV to point-in-time ──
        ohlcv_pit = {}
        for t, df in self.ohlcv_dict.items():
            sliced = df[df.index.date <= as_of]
            if len(sliced) >= 30:
                ohlcv_pit[t] = sliced

        # ── Regime classification ──
        macro  = macro_snapshot(as_of)
        vix    = macro.get("vix_value")
        spy_close = float(ohlcv_pit["SPY"]["close"].iloc[-1]) if "SPY" in ohlcv_pit else None
        spy_ema   = get_spy_ema200(self.spy_df, as_of) if self.spy_df is not None else None
        regime_ctx = get_regime_context(vix, spy_close, spy_ema)
        regime     = regime_ctx["regime"]

        # ── Build today's bar dict for exit manager ──
        ticker_bars = self._build_today_bars(as_of, ohlcv_pit)

        # ── Process exits on open trades ──
        active_signals = {}   # populated below for conversion check
        closed_today, self.open_trades = process_day_exits(
            self.open_trades, ticker_bars, as_of,
            vix, regime, active_signals, self.circuit_breaker_log,
        )
        self.closed_trades.extend(closed_today)

        # ── Screen universe for new entries ──
        candidates = screen_universe(ohlcv_pit, self.info_dict, as_of, regime)
        active_signals = {c["ticker"]: c for c in candidates}

        # ── Sentiment snapshot (once per day) ──
        sent = sentiment_snapshot(as_of)

        # ── Open new trades ──
        already_open = {t.ticker for t in self.open_trades}
        new_entries   = 0

        for cand in candidates[:self.max_cands]:
            ticker = cand["ticker"]
            if ticker in already_open:
                continue

            atr   = cand.get("atr", 0.0) or cand["last_close"] * 0.01
            close = cand["last_close"]

            # Evaluate each triggered strategy
            for strat_entry in cand.get("strategies", []):
                direction = strat_entry["direction"]
                category  = strat_entry["category"]

                # Direction gating
                if direction == "long" and not regime_ctx["long_allowed"]:
                    continue
                if direction == "short" and not regime_ctx["short_allowed"]:
                    continue

                # Validate entry zone (gap filter applied at next-day open — simulated here)
                # In backtest, we use the next day's open from the bar after as_of
                next_bar = self._get_next_open(ticker, as_of)
                if next_bar is None:
                    self.skipped_trades.append({
                        "ticker": ticker, "date": as_of,
                        "strategy": strat_entry["strategy"],
                        "reason": "no_next_bar",
                    })
                    continue

                next_open = next_bar["open"]
                valid, gap_reason = validate_entry_zone(next_open, close, atr, category, direction)
                if not valid:
                    self.skipped_trades.append({
                        "ticker": ticker, "date": as_of,
                        "strategy": strat_entry["strategy"],
                        "reason": gap_reason,
                        "close": close, "next_open": next_open, "atr": atr,
                    })
                    continue

                # Smart money (only if Quiver key set)
                sm = {"composite_signal": "none", "score": 0}
                if os.environ.get("QUIVER_API_KEY"):
                    sm = smart_money_score(ticker, as_of)

                # Confidence tier
                tier = self._assign_confidence_tier(
                    len(cand["strategies"]), sm, macro, sent)

                # Earnings risk flag
                earn_days = days_to_next_earnings(ticker, as_of)

                # Initial trailing stop
                if direction == "long":
                    init_stop = next_open * (1 - TRAILING_STOP["initial_pct"])
                else:
                    init_stop = next_open * (1 + TRAILING_STOP["initial_pct"])

                # Build context (agents or rule-based)
                context_para = ""
                if self.run_agents:
                    context_para = self._run_agent_context(
                        ticker, as_of, cand, strat_entry, macro, sent, sm, earn_days)

                trade = OpenTrade(
                    ticker=ticker,
                    entry_date=as_of,         # signal date
                    entry_price=next_open,     # actual entry = next day open
                    direction=direction,
                    strategy=strat_entry["strategy"],
                    category=category,
                    initial_stop=round(init_stop, 4),
                    trailing_stop=round(init_stop, 4),
                    highest_close=next_open,   # initialised to entry
                    regime_at_entry=regime,
                    signals_at_entry={k: v for k, v in cand["signals"].items()
                                      if isinstance(v, (bool, int, float))},
                    context_bullets=strat_entry["context_bullets"],
                    context_paragraph=context_para,
                    confidence_tier=tier,
                    smart_money_score=sm.get("score", 0),
                    macro_score=macro.get("macro_score", 0),
                    sentiment_score=sent.get("sentiment_score", 0),
                    days_to_earnings=earn_days,
                )
                self.open_trades.append(trade)
                already_open.add(ticker)
                new_entries += 1
                break  # one trade per ticker per day

    def _build_today_bars(self, as_of: date, ohlcv_pit: dict) -> dict:
        """Build today's OHLCV bar for each ticker for exit processing."""
        bars = {}
        for ticker, df in ohlcv_pit.items():
            today_rows = df[df.index.date == as_of]
            if today_rows.empty:
                continue
            row  = today_rows.iloc[-1]
            prev = df[df.index.date < as_of]
            prev_close = float(prev["close"].iloc[-1]) if not prev.empty else float(row["open"])
            entry_price_ref = 0
            for t in self.open_trades:
                if t.ticker == ticker:
                    entry_price_ref = t.entry_price
                    break

            bars[ticker] = {
                "open":       float(row["open"]),
                "high":       float(row["high"]),
                "low":        float(row["low"]),
                "close":      float(row["close"]),
                "prev_close": prev_close,
                "max_adverse":    (float(row["low"]) - entry_price_ref) / entry_price_ref * 100
                                   if entry_price_ref > 0 else 0,
                "max_favourable": (float(row["high"]) - entry_price_ref) / entry_price_ref * 100
                                   if entry_price_ref > 0 else 0,
            }
        return bars

    def _get_next_open(self, ticker: str, signal_date: date) -> Optional[dict]:
        """Get the bar immediately after signal_date for entry price."""
        df = self.ohlcv_dict.get(ticker)
        if df is None:
            return None
        future = df[df.index.date > signal_date]
        if future.empty:
            return None
        row = future.iloc[0]
        return {"open": float(row["open"]), "date": future.index[0].date()}

    def _assign_confidence_tier(self, strategy_count, sm, macro, sent) -> str:
        sm_sig  = sm.get("composite_signal", "none")
        sm_score = sm.get("score", 0)
        macro_s  = macro.get("macro_score", 0)

        if sm_sig in ("congressional+insider_cluster",) and strategy_count >= 3:
            return "EXCEPTIONAL"
        if sm_sig in ("congressional_or_insider",) and strategy_count >= 2:
            return "VERY_HIGH"
        if strategy_count >= 3:
            return "HIGH"
        if strategy_count >= 2:
            return "MEDIUM_HIGH"
        if sm_score >= 2 and strategy_count >= 1:
            return "MEDIUM"
        return "LOW"

    def _run_agent_context(self, ticker, as_of, cand, strat_entry,
                            macro, sent, sm, earn_days) -> str:
        """Call TradingAgents pipeline for plain-English context paragraph."""
        try:
            from backtest.agents.pipeline import run_full_agent_pipeline
            result = run_full_agent_pipeline(
                ticker=ticker, as_of=as_of, candidate=cand,
                smart_money_data=sm, macro_snap=macro,
                sentiment_snap=sent, sector=self.info_dict.get(ticker, {}).get("sector",""),
                earnings_days=earn_days, phase=self.phase,
            )
            return result.get("context_paragraph", "")
        except Exception as exc:
            logger.debug("Agent context failed for %s: %s", ticker, exc)
            return ""

    # ──────────────────────────────────────────────────────────────────────
    # RESULTS
    # ──────────────────────────────────────────────────────────────────────

    def get_trade_log(self) -> pd.DataFrame:
        if not self.closed_trades:
            return pd.DataFrame()
        return pd.DataFrame([asdict(t) for t in self.closed_trades])

    def save_all_outputs(self):
        from backtest.results.writer import write_all_outputs
        from backtest.results.metrics import compute_all_metrics
        df_trades = self.get_trade_log()
        if df_trades.empty:
            logger.warning("No closed trades — nothing to write")
            return
        metrics = compute_all_metrics(df_trades)
        write_all_outputs(
            df_trades=df_trades,
            metrics=metrics,
            skipped=self.skipped_trades,
            cb_log=self.circuit_breaker_log,
            output_dir=self.output_dir,
        )
