"""
engine.py — Backtesting engine orchestrator.

Iterates over all trading days in the backtest window, applies the full
screening pipeline, records entry/exit points, and tracks strategy performance.

Architecture:
  1. Load all OHLCV data upfront (one yfinance call per ticker)
  2. For each trading day:
       a. Apply point-in-time slice (df.loc[:as_of])
       b. Screen universe → Pool 2 → Pool 3 candidates
       c. Fetch smart money + macro + sentiment data (point-in-time)
       d. Run TradingAgents on candidates (top N per day for cost control)
       e. Record trade signals
  3. Simulate trade outcomes (entry next day open, exit by stop/target/max hold)
  4. Aggregate results by strategy and regime
"""

import json
import logging
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd

from backtest.config import (
    BACKTEST_START, BACKTEST_END, MARKET_REGIMES,
    HOLD_DAYS_DEFAULT, HOLD_DAYS_OPTIONS,
    TRADE_RULES, OUTPUT_DIR, OUTPUT_FILES, UNIVERSE_PHASE1A,
)
from backtest.data.fetcher import fetch_ohlcv_bulk, fetch_info, passes_liquidity_filter
from backtest.data.smart_money import (
    congressional_signal, insider_signal, institutional_signal, smart_money_score,
)
from backtest.data.macro import macro_snapshot
from backtest.data.sentiment import sentiment_snapshot
from backtest.signals.screener import screen_universe, ALL_STRATEGIES
from backtest.agents.pipeline import run_full_agent_pipeline

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# TRADE SIMULATION
# ---------------------------------------------------------------------------

def simulate_trade_outcome(
    df_full: pd.DataFrame,
    entry_date: date,
    atr: float,
    direction: str = "long",
    hold_days: int = HOLD_DAYS_DEFAULT,
) -> dict:
    """
    Simulate a swing trade entered at `entry_date`'s open.
    Exit on: stop loss hit, take profit hit, or max hold days.

    Returns: entry_price, exit_price, exit_date, exit_reason, pnl_pct, win
    """
    future = df_full[df_full.index.date > entry_date]  # type: ignore[attr-defined]
    if future.empty:
        return {"win": False, "exit_reason": "no_future_data", "pnl_pct": 0.0}

    entry_price = float(future["open"].iloc[0])
    stop_loss   = entry_price - TRADE_RULES["stop_loss_atr_mult"] * atr if atr else entry_price * 0.97
    take_profit = entry_price + TRADE_RULES["take_profit_atr_mult"] * atr if atr else entry_price * 1.06

    for i in range(min(hold_days, len(future))):
        bar = future.iloc[i]
        low  = float(bar["low"])
        high = float(bar["high"])
        exit_date = future.index[i].date()

        # Check stop loss first (intraday low hit stop)
        if low <= stop_loss:
            pnl = (stop_loss - entry_price) / entry_price * 100
            return {
                "entry_price":  entry_price,
                "exit_price":   stop_loss,
                "exit_date":    exit_date,
                "exit_reason":  "stop_loss",
                "pnl_pct":      round(pnl, 4),
                "win":          False,
                "hold_bars":    i + 1,
            }

        # Check take profit
        if high >= take_profit:
            pnl = (take_profit - entry_price) / entry_price * 100
            return {
                "entry_price":  entry_price,
                "exit_price":   take_profit,
                "exit_date":    exit_date,
                "exit_reason":  "take_profit",
                "pnl_pct":      round(pnl, 4),
                "win":          True,
                "hold_bars":    i + 1,
            }

    # Max hold days — exit at close
    last_bar = future.iloc[min(hold_days - 1, len(future) - 1)]
    exit_price = float(last_bar["close"])
    pnl = (exit_price - entry_price) / entry_price * 100
    return {
        "entry_price":  entry_price,
        "exit_price":   exit_price,
        "exit_date":    future.index[min(hold_days - 1, len(future) - 1)].date(),
        "exit_reason":  "max_hold",
        "pnl_pct":      round(pnl, 4),
        "win":          pnl > 0,
        "hold_bars":    min(hold_days, len(future)),
    }


# Expose ATR multipliers on TRADE_RULES for simulate_trade_outcome
TRADE_RULES["stop_loss_atr_mult"]   = 2.0
TRADE_RULES["take_profit_atr_mult"] = 3.0


def assign_regime(trade_date: date) -> list[str]:
    """Return list of market regime labels that include `trade_date`."""
    regimes = []
    for name, regime in MARKET_REGIMES.items():
        if regime["start"] <= trade_date <= regime["end"]:
            regimes.append(name)
    return regimes or ["unclassified"]


# ---------------------------------------------------------------------------
# MAIN BACKTEST RUNNER
# ---------------------------------------------------------------------------

class BacktestEngine:
    """
    Full backtesting engine for Phase 1A (and reusable for 1B-1D).
    """

    def __init__(
        self,
        universe: list[str] = None,
        start: date = BACKTEST_START,
        end: date   = BACKTEST_END,
        phase: str  = "phase_1a",
        max_candidates_per_day: int = 10,   # cost control: max agent calls/day
        run_agents: bool = True,
        output_dir: str = OUTPUT_DIR,
    ):
        self.universe   = universe or UNIVERSE_PHASE1A
        self.start      = start
        self.end        = end
        self.phase      = phase
        self.max_cands  = max_candidates_per_day
        self.run_agents = run_agents
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Storage
        self.ohlcv_dict:  dict[str, pd.DataFrame] = {}
        self.info_dict:   dict[str, dict]          = {}
        self.trade_log:   list[dict]               = []
        self.signal_log:  list[dict]               = []

    # ------------------------------------------------------------------
    # DATA LOADING
    # ------------------------------------------------------------------

    def load_data(self):
        """Pre-load all OHLCV data. Called once before the backtest loop."""
        logger.info("Loading OHLCV data for %d instruments (%s to %s)...",
                    len(self.universe), self.start, self.end)
        # Load with a buffer before start for indicator warmup
        load_start = self.start - timedelta(days=260)   # ~1 year warmup
        self.ohlcv_dict = fetch_ohlcv_bulk(
            self.universe, start=load_start, end=self.end, delay_sec=0.3
        )
        logger.info("Loaded OHLCV for %d/%d tickers", len(self.ohlcv_dict), len(self.universe))

        logger.info("Loading company info...")
        for ticker in self.universe:
            self.info_dict[ticker] = fetch_info(ticker)

    # ------------------------------------------------------------------
    # BACKTEST LOOP
    # ------------------------------------------------------------------

    def run(self):
        """Execute the full backtest loop."""
        if not self.ohlcv_dict:
            self.load_data()

        # Generate trading days
        trading_days = self._get_trading_days()
        logger.info("Starting backtest: %d trading days, phase=%s", len(trading_days), self.phase)

        for i, as_of in enumerate(trading_days):
            if i % 20 == 0:
                logger.info("Progress: %d/%d [%s]", i, len(trading_days), as_of)

            try:
                self._process_day(as_of)
            except Exception as exc:
                logger.error("Error processing day %s: %s", as_of, exc)

        logger.info("Backtest complete. %d signals, %d trades recorded.",
                    len(self.signal_log), len(self.trade_log))

    def _get_trading_days(self) -> list[date]:
        """Return all trading days (Mon-Fri, excluding major US holidays approx)."""
        days = []
        d = self.start
        while d <= self.end:
            if d.weekday() < 5:  # Monday=0 ... Friday=4
                days.append(d)
            d += timedelta(days=1)
        return days

    def _process_day(self, as_of: date):
        """Process a single trading day through the full pipeline."""
        # Slice all OHLCV to point-in-time
        ohlcv_as_of = {}
        for ticker, df in self.ohlcv_dict.items():
            slice_df = df[df.index.date <= as_of]  # type: ignore[attr-defined]
            if len(slice_df) >= 20:   # need minimum bars for indicators
                ohlcv_as_of[ticker] = slice_df

        if not ohlcv_as_of:
            return

        # Screen universe → candidates
        candidates = screen_universe(ohlcv_as_of, self.info_dict, as_of, min_strategies=1)

        # Log all screening results (Pool 2+3 data)
        for cand in candidates:
            self.signal_log.append({
                "as_of":          str(as_of),
                "ticker":         cand["ticker"],
                "strategy_count": cand["strategy_count"],
                "strategies":     "|".join(cand.get("strategies_triggered", [])),
                "tech_signals":   cand.get("tech_signal_count", 0),
                "last_close":     cand.get("last_close", 0),
                "regime":         "|".join(assign_regime(as_of)),
            })

        # Only run agents on top N candidates (cost control)
        top_candidates = candidates[:self.max_cands]

        if not self.run_agents or not top_candidates:
            # Without agents: simulate trades directly from screener output
            for cand in top_candidates:
                self._simulate_all_strategies(cand, as_of, ohlcv_as_of)
            return

        # Fetch macro + sentiment ONCE per day (shared across all candidates)
        macro_snap = macro_snapshot(as_of)
        sent_snap  = sentiment_snapshot(as_of)

        for cand in top_candidates:
            ticker = cand["ticker"]
            sector = self.info_dict.get(ticker, {}).get("sector", "Unknown")

            # Smart money signals (per ticker — rate limited)
            cong_sig   = congressional_signal(ticker, as_of)
            ins_sig    = insider_signal(ticker, as_of)
            inst_sig   = institutional_signal(ticker, as_of)
            sm_score   = smart_money_score(
                ticker, as_of, cong_sig, ins_sig, inst_sig
            )

            # Earnings proximity
            from backtest.data.fetcher import days_to_next_earnings
            earn_days = days_to_next_earnings(ticker, as_of)

            # Run full agent pipeline
            agent_result = run_full_agent_pipeline(
                ticker=ticker,
                as_of=as_of,
                candidate=cand,
                smart_money_data={
                    "congressional_sig":   cong_sig,
                    "insider_sig":         ins_sig,
                    "institutional_sig":   inst_sig,
                    "smart_money_composite": sm_score,
                },
                macro_snap=macro_snap,
                sentiment_snap=sent_snap,
                sector=sector,
                earnings_days=earn_days,
                phase=self.phase,
            )

            # Only take trades where Decision Agent says TAKE_TRADE
            if agent_result.get("action") == "TAKE_TRADE":
                self._simulate_all_strategies(cand, as_of, ohlcv_as_of, agent_result)

    def _simulate_all_strategies(
        self,
        candidate: dict,
        as_of: date,
        ohlcv_as_of: dict,
        agent_result: Optional[dict] = None,
    ):
        """
        For each triggered strategy, simulate the trade outcome.
        Records result in self.trade_log.
        """
        ticker     = candidate["ticker"]
        df_full    = self.ohlcv_dict.get(ticker)
        if df_full is None:
            return

        atr = candidate.get("atr", 0.0)
        if atr == 0.0:
            # Fall back to a basic ATR estimate (1% of price)
            atr = candidate.get("last_close", 100.0) * 0.01

        for strat in candidate.get("strategies_triggered", []):
            for hold_days in HOLD_DAYS_OPTIONS:
                outcome = simulate_trade_outcome(df_full, as_of, atr, hold_days=hold_days)
                regimes = assign_regime(as_of)

                self.trade_log.append({
                    "strategy":        strat,
                    "ticker":          ticker,
                    "entry_date":      str(as_of),
                    "entry_price":     outcome.get("entry_price", 0),
                    "exit_price":      outcome.get("exit_price", 0),
                    "exit_date":       str(outcome.get("exit_date", "")),
                    "exit_reason":     outcome.get("exit_reason", ""),
                    "pnl_pct":         outcome.get("pnl_pct", 0.0),
                    "win":             outcome.get("win", False),
                    "hold_days":       hold_days,
                    "hold_bars_actual": outcome.get("hold_bars", 0),
                    "regime":          "|".join(regimes),
                    "strategy_count":  candidate.get("strategy_count", 0),
                    "tech_signals":    candidate.get("tech_signal_count", 0),
                    "agent_score":     agent_result.get("final_score") if agent_result else None,
                    "confidence_tier": agent_result.get("confidence_tier") if agent_result else None,
                    "phase":           self.phase,
                })

    # ------------------------------------------------------------------
    # RESULTS
    # ------------------------------------------------------------------

    def get_results(self) -> pd.DataFrame:
        """Return trade log as DataFrame."""
        if not self.trade_log:
            return pd.DataFrame()
        return pd.DataFrame(self.trade_log)

    def get_strategy_summary(self) -> pd.DataFrame:
        """
        Aggregate results by strategy + hold_days.
        Returns: strategy, hold_days, total_trades, win_rate, avg_pnl_pct,
                 max_drawdown_pct, regimes_profitable (count)
        """
        df = self.get_results()
        if df.empty:
            return pd.DataFrame()

        rows = []
        for (strat, hold), grp in df.groupby(["strategy", "hold_days"]):
            wins     = grp["win"].sum()
            total    = len(grp)
            win_rate = wins / total if total > 0 else 0.0
            avg_pnl  = grp["pnl_pct"].mean()
            max_dd   = grp["pnl_pct"].min()

            # Count regimes where win rate >= 55%
            regime_passes = 0  # legacy count — superseded by per-regime verdict matrix
            for regime_str, r_grp in grp.groupby("regime"):
                if len(r_grp) >= 5:  # need at least 5 trades per regime
                    r_wr = r_grp["win"].mean()
                    if r_wr >= 0.55:
                        regime_passes += 1

            rows.append({
                "strategy":           strat,
                "hold_days":          hold,
                "total_trades":       total,
                "win_rate":           round(win_rate, 4),
                "avg_pnl_pct":        round(avg_pnl, 4),
                "max_loss_pct":       round(max_dd, 4),
                "regimes_profitable": regime_passes,
                "passes_threshold":   win_rate >= 0.55 and total >= 100,
            })

        result = pd.DataFrame(rows).sort_values(
            ["passes_threshold", "win_rate"], ascending=False
        )
        return result

    def get_regime_breakdown(self) -> pd.DataFrame:
        """Win rate per strategy per market regime."""
        df = self.get_results()
        if df.empty:
            return pd.DataFrame()

        rows = []
        # Explode multi-regime rows
        df = df.copy()
        df["regime_list"] = df["regime"].str.split("|")
        df_exp = df.explode("regime_list")

        for (strat, hold, regime), grp in df_exp.groupby(["strategy", "hold_days", "regime_list"]):
            if len(grp) < 3:
                continue
            rows.append({
                "strategy":    strat,
                "hold_days":   hold,
                "regime":      regime,
                "trades":      len(grp),
                "win_rate":    round(grp["win"].mean(), 4),
                "avg_pnl_pct": round(grp["pnl_pct"].mean(), 4),
            })

        return pd.DataFrame(rows).sort_values(["strategy", "hold_days", "win_rate"], ascending=False)

    def save_all_outputs(self):
        """Write all 8 output files defined in section 4.13."""
        from backtest.results.writer import write_all_outputs
        df_trades  = self.get_results()
        df_summary = self.get_strategy_summary()
        df_regime  = self.get_regime_breakdown()
        write_all_outputs(df_trades, df_summary, df_regime, self.output_dir)