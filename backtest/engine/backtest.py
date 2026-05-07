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
from backtest.data.fetcher import days_to_next_earnings

logger = logging.getLogger(__name__)


class BacktestEngine:

    def __init__(
        self,
        universe:               list  = None,
        start:                  date  = BACKTEST_START,
        end:                    date  = BACKTEST_END,
        phase:                  str   = "phase_1a",
        max_candidates_per_day: int   = 10,
        run_agents:             bool  = True,
        output_dir:             str   = OUTPUT_DIR,
        use_cache:              bool  = True,
        apply_costs:            bool  = True,
        apply_slippage_model:   bool  = True,
        walk_forward:           bool  = True,
        disable_news:           bool  = False,
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
        self.disable_news         = disable_news
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

        # ── Pre-load macro Parquet once — avoids 782× disk reads during backtest ──
        from backtest.data.macro import _load_macro_combined
        _load_macro_combined()  # loads and caches in module-level variable

        # ── Apply liquidity filter ONCE at load time ──
        # Not daily — if instrument passes at start it stays for full backtest
        self.liquid_universe = self._build_liquid_universe()
        logger.info("Liquid universe: %d/%d instruments after one-time filter",
                    len(self.liquid_universe), len(self.ohlcv_dict))

    def _build_liquid_universe(self) -> list[str]:
        """
        Apply liquidity filter. Returns list of passing tickers.
        Re-checks annually at Jan 1 of each year — a stock liquid in 2022
        may become illiquid by 2024 and should be removed.
        Returns the union of tickers passing at ANY annual check.
        Individual year filtering applied at screening time via _is_liquid_on_date.
        """
        passing = set()
        check_dates = []
        y = self.start.year
        while y <= self.end.year:
            check_dates.append(date(y, 1, 1))
            y += 1

        for ref_date in check_dates:
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
                mkt_cap_m = (self.info_dict.get(ticker, {}).get("market_cap", 0) or 0) / 1_000_000
                if mkt_cap_m > 0 and mkt_cap_m < LIQUIDITY["min_market_cap_m"]:
                    continue
                passing.add(ticker)

        # Build per-year liquid set for daily screening
        self._annual_liquid: dict[int, set] = {}
        for ref_date in check_dates:
            year_set = set()
            for ticker, df in self.ohlcv_dict.items():
                sliced = df[df.index.date <= ref_date]
                if len(sliced) < 30:
                    continue
                if float(sliced["close"].iloc[-1]) < LIQUIDITY["min_price"]:
                    continue
                if float(sliced["volume"].tail(20).mean()) < LIQUIDITY["min_avg_volume"]:
                    continue
                year_set.add(ticker)
            self._annual_liquid[ref_date.year] = year_set

        return list(passing)

    def _get_liquid_universe_for_date(self, as_of: date) -> set:
        """Return the liquid universe for the year of as_of."""
        if hasattr(self, "_annual_liquid"):
            return self._annual_liquid.get(as_of.year, set(self.liquid_universe))
        return set(self.liquid_universe)

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
            # Incremental checkpoint every 25 days — trade log survives crashes
            if i > 0 and i % 25 == 0 and self.closed_trades:
                try:
                    import pandas as _pd
                    checkpoint_path = self.output_dir / "trade_log_checkpoint.csv"
                    _pd.DataFrame([vars(t) for t in self.closed_trades]).to_csv(
                        checkpoint_path, index=False)
                    logger.debug("Checkpoint: %d trades → %s", len(self.closed_trades), checkpoint_path)
                except Exception:
                    pass
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
        # ── 1. Slice OHLCV to point-in-time using year-appropriate liquid universe ──
        liquid_this_year = self._get_liquid_universe_for_date(as_of)
        ohlcv_pit = {}
        for t in liquid_this_year:
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
        # Pass 53 fix 2026-05-07: hoist crisis_flag to function scope so it's
        # defined before line 299 (was UnboundLocalError when regime != crisis
        # and inner-loop set never executed). Per DEC-316 unknown regime exists.
        crisis_flag = regime == "crisis"
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
        # Deduplication: track tickers already opened today (one position per ticker per day)
        opened_today: set[str] = set()

        for cand in candidates[:self.max_cands]:
            ticker = cand["ticker"]
            atr    = cand.get("atr", 0.0) or cand["last_close"] * 0.01
            close  = cand["last_close"]

            for strat_entry in cand.get("strategies", []):
                direction = strat_entry["direction"]
                category  = strat_entry["category"]

                # Skip avoid direction — conflicting signals, log as skipped
                if direction == "avoid":
                    self.skipped_trades.append({
                        "ticker": ticker, "date": as_of,
                        "strategy": strat_entry["strategy"],
                        "reason": "avoid_conflicting_signals",
                    })
                    continue

                # Crisis long exclusions — block long entries on specific tickers
                # that are data-confirmed wrong-directional in crisis regime
                if direction == "long" and crisis_flag:
                    from backtest.config import CRISIS_LONG_EXCLUSIONS
                    if ticker in CRISIS_LONG_EXCLUSIONS:
                        self.skipped_trades.append({
                            "ticker": ticker, "date": as_of,
                            "strategy": strat_entry["strategy"],
                            "reason": f"crisis_long_excluded_{ticker}",
                        })
                        continue

                # Skip only exact duplicate — same ticker AND same strategy already open
                if (ticker, strat_entry["strategy"]) in open_combos:
                    continue

                # Deduplication — one position per ticker per day (highest strategy count wins)
                # Candidates are sorted by strategy_count desc, so first to fire wins
                if ticker in opened_today:
                    self.skipped_trades.append({
                        "ticker": ticker, "date": as_of,
                        "strategy": strat_entry["strategy"],
                        "reason": "dedup_one_position_per_ticker_per_day",
                    })
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
                sm = {"composite_signal": "none", "score": 0,
                      "congressional_signal": "none", "insider_signal": "none",
                      "institutional_signal": "none"}
                if os.environ.get("QUIVER_API_KEY"):
                    sm = smart_money_score(ticker, as_of)

                # Stage 1 — rule-based preliminary tier
                preliminary_tier = self._assign_confidence_tier(
                    len(cand["strategies"]), sm, macro, sent)

                # Earnings proximity — context for agents, not a blocker
                earn_days = days_to_next_earnings(ticker, as_of)

                # Trailing stop
                if direction == "long":
                    init_stop = entry_price * (1 - TRAILING_STOP["initial_pct"])
                else:
                    init_stop = entry_price * (1 + TRAILING_STOP["initial_pct"])

                # Stage 2 — agent quality assessment adjusts tier ±1 level
                context_para = ""
                agent_score = 50
                agent_result = {}
                if self.run_agents:
                    context_para, agent_score, agent_result = self._run_agent_context(
                        ticker, as_of, cand, strat_entry, macro, sent, sm, earn_days)
                    tier = self._adjust_tier_by_agent(preliminary_tier, agent_score)
                else:
                    tier = preliminary_tier

                # Skip AVOID tier long trades (may be evaluated as short setup separately)
                if tier == "AVOID" and direction == "long":
                    self.skipped_trades.append({
                        "ticker": ticker, "date": as_of,
                        "strategy": strat_entry["strategy"],
                        "reason": "avoid_tier_long_blocked",
                    })
                    continue

                # Get sector ETF return for halo effect context
                sector = self.sector_map.get(ticker, "Unknown")
                sector_etf_map = {
                    "Information Technology": "XLK", "Financials": "XLF",
                    "Energy": "XLE", "Health Care": "XLV", "Industrials": "XLI",
                    "Consumer Discretionary": "XLY", "Consumer Staples": "XLP",
                    "Utilities": "XLU", "Materials": "XLB", "Real Estate": "XLRE",
                    "Communication Services": "XLK",
                }
                sector_etf = sector_etf_map.get(sector, "SPY")
                sector_etf_df = self.ohlcv_dict.get(sector_etf)
                sector_etf_return = 0.0
                if sector_etf_df is not None:
                    etf_today = sector_etf_df[sector_etf_df.index.date == as_of]
                    etf_prev  = sector_etf_df[sector_etf_df.index.date < as_of]
                    if not etf_today.empty and not etf_prev.empty:
                        sector_etf_return = round(
                            (float(etf_today["close"].iloc[-1]) /
                             float(etf_prev["close"].iloc[-1]) - 1) * 100, 3)

                trade = OpenTrade(
                    ticker=ticker,
                    entry_date=as_of,
                    entry_price=entry_price,
                    direction=direction,
                    strategy=strat_entry["strategy"],
                    category=category,
                    sector=sector,
                    initial_stop=round(init_stop, 4),
                    trailing_stop=round(init_stop, 4),
                    highest_close=entry_price,
                    regime_at_entry=f"{regime}{'_CRISIS_FLAG' if crisis_flag else ''}",
                    signals_at_entry={
                        **{k: v for k, v in cand["signals"].items()
                           if isinstance(v, (bool, int, float))},
                        "sector_etf": sector_etf,
                        "sector_etf_return_pct": sector_etf_return,
                        "sector": sector,
                    },
                    context_bullets=strat_entry["context_bullets"],
                    context_paragraph=context_para,
                    confidence_tier=tier,
                    preliminary_tier=preliminary_tier,
                    agent_reasoning=agent_result,
                    smart_money_score=sm.get("score", 0),
                    macro_score=macro.get("macro_score", 0),
                    sentiment_score=sent.get("sentiment_score", 0),
                    days_to_earnings=earn_days,
                    congressional_signal=sm.get("congressional_signal", "none"),
                    insider_signal=sm.get("insider_signal", "none"),
                    institutional_signal=sm.get("institutional_signal", "none"),
                    aaii_bullish=float(sent.get("aaii", {}).get("bullish_pct", 0) or 0),
                    aaii_bearish=float(sent.get("aaii", {}).get("bearish_pct", 0) or 0),
                    aaii_signal=str(sent.get("aaii", {}).get("signal", "neutral")),
                    cnn_fg_score=float(sent.get("fear_greed", {}).get("score", 50) or 50),
                    cnn_fg_label=str(sent.get("fear_greed", {}).get("label", "Neutral")),
                )
                self.open_trades.append(trade)
                open_combos.add((ticker, strat_entry["strategy"]))
                opened_today.add(ticker)

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
        """Stage 1 — rule-based preliminary tier before agents run."""
        sm_sig = sm.get("composite_signal", "none")
        # AVOID — strong negative smart money regardless of technical signals
        if sm_sig == "congressional_sell+insider_cluster_sell":
            return "AVOID"
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

    def _adjust_tier_by_agent(self, preliminary_tier: str, agent_score: int) -> str:
        """Stage 2 — agent score adjusts tier ±1 level based on quality assessment."""
        from backtest.config import (AGENT_TIER_UPGRADE_THRESHOLD, AGENT_TIER_DOWNGRADE_THRESHOLD,
                              CONFIDENCE_TIERS)
        tier_order = ["LOW", "MEDIUM", "MEDIUM_HIGH", "HIGH", "VERY_HIGH", "EXCEPTIONAL"]
        if preliminary_tier == "AVOID":
            return "AVOID"
        try:
            idx = tier_order.index(preliminary_tier)
        except ValueError:
            return preliminary_tier
        if agent_score >= AGENT_TIER_UPGRADE_THRESHOLD and idx < len(tier_order) - 1:
            return tier_order[idx + 1]
        if agent_score <= AGENT_TIER_DOWNGRADE_THRESHOLD and idx > 0:
            return tier_order[idx - 1]
        return preliminary_tier

    def _run_agent_context(self, ticker, as_of, cand, strat_entry,
                            macro, sent, sm, earn_days) -> tuple:
        """Run agents and return (context_paragraph, agent_final_score, adjusted_tier, preliminary_tier)."""
        try:
            from backtest.agents.pipeline import run_full_agent_pipeline
            sector = self.sector_map.get(ticker, "Unknown")
            # Build portfolio context for Decision Agent
            portfolio_context = {
                "open_positions": len(self.open_trades),
                "sector_concentration": {
                    s: sum(1 for t in self.open_trades if t.sector == s)
                    for s in set(t.sector for t in self.open_trades)
                },
                "existing_position_in_ticker": any(
                    t.ticker == ticker for t in self.open_trades),
                "portfolio_drawdown_pct": 0.0,  # simplified for backtest
            }
            result = run_full_agent_pipeline(
                ticker=ticker, as_of=as_of, candidate=cand,
                smart_money_data=sm, macro_snap=macro,
                sentiment_snap=sent, sector=sector,
                earnings_days=earn_days, phase=self.phase,
                portfolio_context=portfolio_context,
                disable_news=self.disable_news,
            )
            agent_score = result.get("final_score", 50)
            return (
                result.get("context_paragraph", ""),
                agent_score,
                result,
            )
        except Exception as exc:
            logger.debug("Agent context failed for %s: %s", ticker, exc)
            return ("", 50, {})

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

        # Survivorship bias haircut — hold-adjusted per trade
        years = (self.end - self.start).days / 365.25
        gross_roi = df_trades["pnl_pct"].sum()
        df_trades, haircut = apply_survivorship_haircut(df_trades, years)
        adj_roi = df_trades["pnl_pct"].sum()
        logger.info("Hold-adjusted survivorship haircut: %.1f%% → adjusted ROI %.1f%%",
                    haircut, adj_roi)

        # SPY benchmark return
        spy_benchmark = None
        if self.spy_df is not None:
            try:
                spy_s = self.spy_df[self.spy_df.index.date >= self.start]
                spy_e = self.spy_df[self.spy_df.index.date <= self.end]
                if not spy_s.empty and not spy_e.empty:
                    spy_benchmark = round((float(spy_e["close"].iloc[-1]) /
                                           float(spy_s["close"].iloc[0]) - 1) * 100, 2)
                    logger.info("SPY benchmark return: %.1f%%", spy_benchmark)
            except Exception as e:
                logger.debug("SPY benchmark calc failed: %s", e)

        # Metrics
        metrics = compute_all_metrics(df_trades, spy_total_return=spy_benchmark)

        # Walk-forward validation
        wf_df = pd.DataFrame()
        if self.walk_forward and len(df_trades) >= 20:
            wf_results = run_walk_forward(df_trades)
            wf_df      = walk_forward_to_df(wf_results)

        # Bonferroni info
        bonferroni = bonferroni_adjusted_threshold(60)
        logger.info("Bonferroni: %s", bonferroni["recommendation"])

        # Exit comparison (DEC-422 cube + DEC-067 17-method counterfactual)
        # Pass 53 Day-9-evening 2026-05-07 owner directive: all 4 tiers of
        # exit-analysis context propagated per DEC-594 same-commit. ~25 columns
        # added to trade_exit_detail.csv via entry_context dict per trade.
        from backtest.engine.exit_context import build_entry_context

        exit_frames = []
        trade_detail_frames = []
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

                # Build per-trade context dict (Tiers 1-4) for trade_exit_detail
                entry_context = build_entry_context(
                    row=row,
                    ticker=ticker,
                    entry_date=entry_date,
                    df_full=df_full,
                    spy_df=self.spy_df,
                    signals=sig if isinstance(sig, dict) else {},
                    atr=atr,
                )

                trades_data.append({
                    "ticker":         ticker,
                    "df":             df_full,
                    "entry_date":     entry_date,
                    "entry_price":    row["entry_price"],
                    "direction":      row["direction"],
                    "atr":            atr,
                    "signals":        sig if isinstance(sig, dict) else {},
                    "entry_context":  entry_context,  # dict with Tier 1-4 fields
                })
            if trades_data:
                ec, td = run_exit_comparison(strategy, trades_data)
                if not ec.empty:
                    exit_frames.append(ec)
                if not td.empty:
                    trade_detail_frames.append(td)

        exit_compare = (pd.concat(exit_frames, ignore_index=True)
                        if exit_frames else pd.DataFrame())
        trade_exit_detail = (pd.concat(trade_detail_frames, ignore_index=True)
                             if trade_detail_frames else pd.DataFrame())

        write_all_outputs(
            df_trades=df_trades,
            metrics=metrics,
            skipped=self.skipped_trades,
            cb_log=self.circuit_breaker_log,
            exit_compare=exit_compare,
            trade_exit_detail=trade_exit_detail,
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
