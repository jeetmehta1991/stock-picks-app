"""
engine/backtest.py — Main backtest orchestrator.

Backtest-mode operating rules (approved April 2026):
  - No open position cap — uncapped for statistical validity
  - No daily loss limit — removed for backtest, will apply in live trading
  - No correlation filter — removed for backtest, sector sizing in live trading
  - No regime position multiplier — full size in all regimes for backtest
  - No regime confidence scaling — full size always for backtest
  - Liquidity filter applied once at load_data, not daily
  - Max candidates: 10 per day
  - Mean reversion entry zone: 1.0× ATR (raised from 0.5×)
  - Position sizing: EXCEPTIONAL 5%, VERY HIGH 4%, HIGH 3%, MEDIUM-HIGH 1.5%
  - Short strategies: strict original conditions, Phase 1B for statistical volume
  - All 5 circuit breakers active
  - Slippage and transaction costs applied to all trades
  - Walk-forward validation on all results
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
    TRAILING_STOP, AI_MODELS, DATA_LOAD_START, LIQUIDITY,
)
from backtest.data.cache import get_ohlcv_bulk as cached_ohlcv_bulk
from backtest.data.universe import fetch_info_bulk, get_sector_map
from backtest.data.macro import macro_snapshot
from backtest.data.sentiment import sentiment_snapshot
from backtest.data.smart_money import smart_money_score
from backtest.engine.regime_filter import get_regime_context, get_spy_ema200
from backtest.engine.exit_manager import (
    OpenTrade, ClosedTrade, process_day_exits,
)
from backtest.engine.improvements import (
    apply_transaction_costs, run_walk_forward, walk_forward_to_df,
    apply_slippage, apply_survivorship_haircut,
    bonferroni_adjusted_threshold,
)
from backtest.signals.screener import screen_universe, validate_entry_zone

logger = logging.getLogger(__name__)


class BacktestEngine:

    def __init__(
        self,
        universe:               list  = None,
        start:                  date  = BACKTEST_START,
        end:                    date  = BACKTEST_END,
        phase:                  str   = "phase_1a",
        max_candidates_per_day: int   = 10,
        run_agents:             bool  = False,
        output_dir:             str   = OUTPUT_DIR,
        use_cache:              bool  = True,
        apply_costs:            bool  = True,
        apply_slippage_model:   bool  = True,
        walk_forward:           bool  = True,
    ):
        self.universe             = universe or UNIVERSE
        self.start                = start
        self.end                  = end
        self.phase                = phase
        self.max_cands            = max_candidates_per_day
        self.run_agents           = run_agents
        self.output_dir           = Path(output_dir)
        self.use_cache            = use_cache
        self.apply_costs          = apply_costs
        self.apply_slippage_model = apply_slippage_model
        self.walk_forward         = walk_forward
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Data stores
        self.ohlcv_dict:  dict[str, pd.DataFrame] = {}
        self.info_dict:   dict[str, dict]          = {}
        self.sector_map:  dict[str, str]           = {}
        self.spy_df:      Optional[pd.DataFrame]   = None

        # Liquidity-filtered universe — computed once at load time
        self.liquid_universe: list[str] = []

        # Trade stores
        self.open_trades:         list[OpenTrade]   = []
        self.closed_trades:       list[ClosedTrade] = []
        self.skipped_trades:      list[dict]        = []
        self.circuit_breaker_log: list[dict]        = []

    # ──────────────────────────────────────────────────────────────────────
    # DATA LOADING
    # ──────────────────────────────────────────────────────────────────────

    def load_data(self):
        logger.info("Loading OHLCV for %d instruments (%s → %s) | cache=%s",
                    len(self.universe), DATA_LOAD_START, self.end, self.use_cache)

        if self.use_cache:
            self.ohlcv_dict = cached_ohlcv_bulk(
                self.universe, start=DATA_LOAD_START, end=self.end)
        else:
            from backtest.data.fetcher import fetch_ohlcv_bulk
            self.ohlcv_dict = fetch_ohlcv_bulk(
                self.universe, start=DATA_LOAD_START, end=self.end, delay_sec=0.3)

        logger.info("Loaded %d/%d tickers", len(self.ohlcv_dict), len(self.universe))

        logger.info("Loading company info (cached)...")
        self.info_dict  = fetch_info_bulk(self.universe)
        self.sector_map = get_sector_map(self.universe, self.info_dict)
        self.spy_df     = self.ohlcv_dict.get("SPY")

        # ── Apply liquidity filter ONCE at load time ──
        # Not daily — if instrument passes at start it stays for full backtest
        self.liquid_universe = self._build_liquid_universe()
        logger.info("Liquid universe: %d/%d instruments after one-time filter",
                    len(self.liquid_universe), len(self.ohlcv_dict))

    def _build_liquid_universe(self) -> list[str]:
        """Apply liquidity filter once. Returns list of passing tickers."""
        passing = []
        ref_date = self.start  # use backtest start as reference date
        for ticker, df in self.ohlcv_dict.items():
            sliced = df[df.index.date <= ref_date]
            if len(sliced) < 30:
                continue
            last_close = float(sliced["close"].iloc[-1])
            if last_close < LIQUIDITY["min_price"]:
                continue
            avg_vol = float(sliced["volume"].tail(20).mean())
            if avg_vol < LIQUIDITY["min_avg_volume"]:
                continue
            # Market cap — skip check if unavailable (rate limit graceful fallback)
            mkt_cap_m = (self.info_dict.get(ticker, {}).get("market_cap", 0) or 0) / 1_000_000
            if mkt_cap_m > 0 and mkt_cap_m < LIQUIDITY["min_market_cap_m"]:
                continue
            passing.append(ticker)
        return passing

    # ──────────────────────────────────────────────────────────────────────
    # MAIN LOOP
    # ──────────────────────────────────────────────────────────────────────

    def run(self):
        if not self.ohlcv_dict:
            self.load_data()

        trading_days = self._trading_days()
        logger.info(
            "Starting backtest: %d days | phase=%s | agents=%s | "
            "costs=%s | slippage=%s | instruments=%d",
            len(trading_days), self.phase, self.run_agents,
            self.apply_costs, self.apply_slippage_model,
            len(self.liquid_universe),
        )

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
                    len(self.open_trades), len(self.closed_trades),
                    len(self.skipped_trades))

    def _trading_days(self) -> list[date]:
        days, d = [], self.start
        while d <= self.end:
            if d.weekday() < 5:
                days.append(d)
            d += timedelta(days=1)
        return days

    def _process_day(self, as_of: date):
        # ── 1. Slice OHLCV to point-in-time using liquid universe only ──
        ohlcv_pit = {}
        for t in self.liquid_universe:
            df = self.ohlcv_dict.get(t)
            if df is None:
                continue
            sliced = df[df.index.date <= as_of]
            if len(sliced) >= 30:
                ohlcv_pit[t] = sliced

        # ── 2. Regime classification — direction gating only, no sizing ──
        macro     = macro_snapshot(as_of)
        vix       = macro.get("vix_value")
        spy_close = float(ohlcv_pit["SPY"]["close"].iloc[-1]) if "SPY" in ohlcv_pit else None
        spy_ema   = get_spy_ema200(self.spy_df, as_of) if self.spy_df is not None else None
        regime_ctx = get_regime_context(vix, spy_close, spy_ema)
        regime     = regime_ctx["regime"]
        # Note: regime_ctx used for direction gating only — no position sizing in backtest

        # ── 3. Build today's bars for exit manager ──
        ticker_bars = self._build_today_bars(as_of, ohlcv_pit)

        # ── 4. Process exits ──
        active_signals = {}
        closed_today, self.open_trades = process_day_exits(
            self.open_trades, ticker_bars, as_of,
            vix, regime, active_signals, self.circuit_breaker_log,
        )
        self.closed_trades.extend(closed_today)

        # ── 5. Screen universe — no daily liquidity filter ──
        candidates     = screen_universe(ohlcv_pit, self.info_dict, as_of, regime)
        active_signals = {c["ticker"]: c for c in candidates}
        sent           = sentiment_snapshot(as_of)

        # ── 6. Open new trades — no position cap, no correlation filter,
        #         no per-ticker limit, no direction hard block ──
        # Track open ticker+strategy combos to avoid exact duplicates only
        open_combos = {(t.ticker, t.strategy) for t in self.open_trades}

        for cand in candidates[:self.max_cands]:
            ticker = cand["ticker"]
            atr    = cand.get("atr", 0.0) or cand["last_close"] * 0.01
            close  = cand["last_close"]

            for strat_entry in cand.get("strategies", []):
                direction = strat_entry["direction"]
                category  = strat_entry["category"]

                # Skip only exact duplicate — same ticker AND same strategy already open
                if (ticker, strat_entry["strategy"]) in open_combos:
                    continue

                # Regime flag — no hard block on any direction
                # Crisis regime is flagged on the trade for analysis, not blocked
                crisis_flag = regime == "crisis"

                # Entry zone gap filter
                next_bar = self._get_next_open(ticker, as_of)
                if next_bar is None:
                    self.skipped_trades.append({
                        "ticker": ticker, "date": as_of,
                        "strategy": strat_entry["strategy"],
                        "reason": "no_next_bar",
                    })
                    continue

                next_open = next_bar["open"]
                valid, gap_reason = validate_entry_zone(
                    next_open, close, atr, category, direction)
                if not valid:
                    self.skipped_trades.append({
                        "ticker": ticker, "date": as_of,
                        "strategy": strat_entry["strategy"],
                        "reason": gap_reason,
                        "close": close, "next_open": next_open, "atr": atr,
                    })
                    continue

                # Slippage model
                gap_pct = (next_open - close) / close if close > 0 else 0
                if self.apply_slippage_model:
                    entry_price, slippage_pct = apply_slippage(
                        next_open, direction, atr, ticker, gap_pct)
                else:
                    entry_price, slippage_pct = next_open, 0.0

                # Smart money
                sm = {"composite_signal": "none", "score": 0}
                if os.environ.get("QUIVER_API_KEY"):
                    sm = smart_money_score(ticker, as_of)

                # Confidence tier
                tier = self._assign_confidence_tier(
                    len(cand["strategies"]), sm, macro, sent)

                # Earnings risk flag
                from backtest.data.fetcher import days_to_next_earnings
                earn_days = days_to_next_earnings(ticker, as_of)

                # Trailing stop
                if direction == "long":
                    init_stop = entry_price * (1 - TRAILING_STOP["initial_pct"])
                else:
                    init_stop = entry_price * (1 + TRAILING_STOP["initial_pct"])

                # Agent context
                context_para = ""
                if self.run_agents:
                    context_para = self._run_agent_context(
                        ticker, as_of, cand, strat_entry, macro, sent, sm, earn_days)

                trade = OpenTrade(
                    ticker=ticker,
                    entry_date=as_of,
                    entry_price=entry_price,
                    direction=direction,
                    strategy=strat_entry["strategy"],
                    category=category,
                    initial_stop=round(init_stop, 4),
                    trailing_stop=round(init_stop, 4),
                    highest_close=entry_price,
                    regime_at_entry=f"{regime}{'_CRISIS_FLAG' if crisis_flag else ''}",
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
                open_combos.add((ticker, strat_entry["strategy"]))

    # ──────────────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────────────

    def _build_today_bars(self, as_of: date, ohlcv_pit: dict) -> dict:
        bars = {}
        for ticker, df in ohlcv_pit.items():
            today_rows = df[df.index.date == as_of]
            if today_rows.empty:
                continue
            row  = today_rows.iloc[-1]
            prev = df[df.index.date < as_of]
            prev_close = float(prev["close"].iloc[-1]) if not prev.empty else float(row["open"])
            ep = 0
            for t in self.open_trades:
                if t.ticker == ticker:
                    ep = t.entry_price; break
            bars[ticker] = {
                "open":           float(row["open"]),
                "high":           float(row["high"]),
                "low":            float(row["low"]),
                "close":          float(row["close"]),
                "prev_close":     prev_close,
                "max_adverse":    (float(row["low"])  - ep) / ep * 100 if ep > 0 else 0,
                "max_favourable": (float(row["high"]) - ep) / ep * 100 if ep > 0 else 0,
            }
        return bars

    def _get_next_open(self, ticker: str, signal_date: date) -> Optional[dict]:
        df = self.ohlcv_dict.get(ticker)
        if df is None:
            return None
        future = df[df.index.date > signal_date]
        if future.empty:
            return None
        return {"open": float(future.iloc[0]["open"]), "date": future.index[0].date()}

    def _assign_confidence_tier(self, strategy_count, sm, macro, sent) -> str:
        sm_sig = sm.get("composite_signal", "none")
        if sm_sig == "congressional+insider_cluster" and strategy_count >= 3:
            return "EXCEPTIONAL"
        if sm_sig == "congressional_or_insider" and strategy_count >= 2:
            return "VERY_HIGH"
        if strategy_count >= 3:
            return "HIGH"
        if strategy_count >= 2:
            return "MEDIUM_HIGH"
        if sm.get("score", 0) >= 2 and strategy_count >= 1:
            return "MEDIUM"
        return "LOW"

    def _run_agent_context(self, ticker, as_of, cand, strat_entry,
                            macro, sent, sm, earn_days) -> str:
        try:
            from backtest.agents.pipeline import run_full_agent_pipeline
            result = run_full_agent_pipeline(
                ticker=ticker, as_of=as_of, candidate=cand,
                smart_money_data=sm, macro_snap=macro,
                sentiment_snap=sent,
                sector=self.info_dict.get(ticker, {}).get("sector", ""),
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
        from backtest.engine.exit_strategies import run_exit_comparison

        df_trades = self.get_trade_log()
        if df_trades.empty:
            logger.warning("No closed trades — nothing to write")
            return

        # Apply transaction costs
        if self.apply_costs:
            df_trades = apply_transaction_costs(df_trades, self.info_dict)
            logger.info("Transaction costs applied — net ROI = %.1f%%",
                        df_trades["pnl_pct"].sum())

        # Survivorship bias haircut
        years = (self.end - self.start).days / 365.25
        gross_roi = df_trades["pnl_pct"].sum()
        adj_roi, haircut = apply_survivorship_haircut(gross_roi, years)
        logger.info("Survivorship haircut: %.1f%% → adjusted ROI %.1f%%",
                    haircut, adj_roi)

        # Metrics
        metrics = compute_all_metrics(df_trades)

        # Walk-forward validation
        wf_df = pd.DataFrame()
        if self.walk_forward and len(df_trades) >= 20:
            wf_results = run_walk_forward(df_trades)
            wf_df      = walk_forward_to_df(wf_results)

        # Bonferroni info
        bonferroni = bonferroni_adjusted_threshold(60)
        logger.info("Bonferroni: %s", bonferroni["recommendation"])

        # Exit comparison
        exit_frames = []
        for strategy in df_trades["strategy"].unique():
            strat_df    = df_trades[df_trades["strategy"] == strategy]
            trades_data = []
            for _, row in strat_df.iterrows():
                ticker  = row["ticker"]
                df_full = self.ohlcv_dict.get(ticker)
                if df_full is None:
                    continue
                entry_date = row["entry_date"]
                if isinstance(entry_date, str):
                    from datetime import datetime as _dt
                    entry_date = _dt.strptime(entry_date[:10], "%Y-%m-%d").date()
                sig = row.get("signals_at_entry", {})
                atr = (sig.get("atr", row["entry_price"] * 0.02)
                       if isinstance(sig, dict) else row["entry_price"] * 0.02)
                trades_data.append({
                    "df":          df_full,
                    "entry_date":  entry_date,
                    "entry_price": row["entry_price"],
                    "direction":   row["direction"],
                    "atr":         atr,
                    "signals":     sig if isinstance(sig, dict) else {},
                })
            if trades_data:
                ec = run_exit_comparison(strategy, trades_data)
                if not ec.empty:
                    exit_frames.append(ec)

        exit_compare = (pd.concat(exit_frames, ignore_index=True)
                        if exit_frames else pd.DataFrame())

        write_all_outputs(
            df_trades=df_trades,
            metrics=metrics,
            skipped=self.skipped_trades,
            cb_log=self.circuit_breaker_log,
            exit_compare=exit_compare,
            walk_forward=wf_df,
            survivorship_info={
                "gross_roi":    round(gross_roi, 3),
                "adjusted_roi": round(adj_roi, 3),
                "haircut_pct":  round(haircut, 3),
                "years":        round(years, 2),
            },
            bonferroni=bonferroni,
            output_dir=self.output_dir,
        )
