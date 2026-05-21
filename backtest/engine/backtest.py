"""
engine/backtest.py  -  Main backtest orchestrator.

Backtest-mode operating rules (approved April 2026):
  - No open position cap  -  uncapped for statistical validity
  - No daily loss limit  -  removed for backtest, will apply in live trading
  - No correlation filter  -  removed for backtest, sector sizing in live trading
  - No regime position multiplier  -  full size in all regimes for backtest
  - No regime confidence scaling  -  full size always for backtest
  - Liquidity filter applied once at load_data, not daily
  - Max candidates: 10 per day
  - Mean reversion entry zone: 1.0x ATR (raised from 0.5x)
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
    STARTING_CAPITAL, TIER_POSITION_SIZE_PCT, LIVE_TRADING_RULES,
)
from backtest.data.cache import get_ohlcv_bulk as cached_ohlcv_bulk
from backtest.data.universe import fetch_info_bulk, get_sector_map
from backtest.data.macro import macro_snapshot
from backtest.data.sentiment import sentiment_snapshot
from backtest.data.smart_money import smart_money_score
from backtest.engine.regime_filter import (
    get_regime_context, get_spy_ema200, get_vix_smoothed,
)
from backtest.engine.exit_manager import (
    OpenTrade, ClosedTrade, process_day_exits,
)
from backtest.engine.improvements import (
    apply_transaction_costs, run_walk_forward, walk_forward_to_df,
    apply_slippage, apply_survivorship_haircut,
    bonferroni_adjusted_threshold,
)
from backtest.signals.screener import screen_universe, validate_entry_zone, ALL_STRATEGIES
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

        # Liquidity-filtered universe  -  computed once at load time
        self.liquid_universe: list[str] = []

        # Trade stores
        self.open_trades:         list[OpenTrade]   = []
        self.closed_trades:       list[ClosedTrade] = []
        self.skipped_trades:      list[dict]        = []
        # Batch 191 (INV-053 optimization): sizing decisions are NOT skips
        # (the trade still proceeds at the scaled size). Pre-batch baseline
        # mis-logged 92,345 vol_target / per_pos_vol / dd_band entries to
        # skipped_trades.csv polluting rejection accounting (53.5% of
        # "rejects" were actually sizing decisions). Owner-approved 2026-05-16.
        self.sizing_log:          list[dict]        = []
        self.circuit_breaker_log: list[dict]        = []
        # DEC-515 Level 6 CB state  -  Pass 53 Day-9-evening v5 engine wiring
        # per DEC-594 same-commit. Persistent state across days within a run.
        from backtest.engine.circuit_breakers import Level6State
        self.level_6_state = Level6State()
        self._backtest_start_date: Optional[date] = None  # set at run() start

        # BUG-95 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 20
        # Sub-batch 2/5 (engine integration) - owner-approved Option A:
        # instantiate the portfolio-level state tracker. Engine wires the
        # following lifecycle: mark_to_market each day before entries,
        # add_position after a trade is appended to open_trades, remove_position
        # after a trade is closed (process_day_exits + _finalize_open_trades).
        # The can_open() gate is NOT enforced in sub-batch 2 (shadow state
        # only); sub-batch 4 turns LIVE_TRADING_RULES gates on.
        from backtest.engine.portfolio import Portfolio
        self.portfolio = Portfolio(starting_capital=STARTING_CAPITAL)

        # DEC-317 + DEC-388 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 43
        # engine wiring 2026-05-11: track prev_regime across days for
        # classify_regime_with_hysteresis. None at start; updated in _process_day.
        self._prev_regime: Optional[str] = None
        # DEC-108 Batch 78 2026-05-12: EMA-smoothed regime probability state
        self._regime_smoothed: Optional[float] = None
        # DEC-149 Batch 79 2026-05-12: regime sequence for transition matrix
        self._regime_history: list[str] = []
        # Pre-loaded VIX series for smoothing (populated by load_data)
        self._vix_series: Optional[pd.Series] = None

    # ----------------------------------------------------------------------
    # DATA LOADING
    # ----------------------------------------------------------------------

    def load_data(self):
        logger.info("Loading OHLCV for %d instruments (%s -> %s) | cache=%s",
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

        # -- Pre-load macro Parquet once  -  avoids 782x disk reads during backtest --
        from backtest.data.macro import _load_macro_combined
        _load_macro_combined()  # loads and caches in module-level variable

        # -- Apply liquidity filter ONCE at load time --
        # Not daily  -  if instrument passes at start it stays for full backtest
        self.liquid_universe = self._build_liquid_universe()
        logger.info("Liquid universe: %d/%d instruments after one-time filter",
                    len(self.liquid_universe), len(self.ohlcv_dict))

        # DEC-317 + DEC-388 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 43:
        # Pre-load VIX series for hysteresis-aware regime classification. The
        # series feeds get_vix_smoothed in _process_day so 5-day SMA can be
        # computed at each as_of. Source priority per backtest.data.macro.get_vix
        # (FRED VIXCLS canonical; ^VIX fallback; VXX proxy degraded).
        try:
            from backtest.data.macro import get_vix
            vix_df = get_vix(DATA_LOAD_START, self.end)
            if vix_df is not None and not vix_df.empty:
                # Use close column as VIX value series; ensure datetime index
                if "close" in vix_df.columns:
                    self._vix_series = vix_df["close"]
                elif "vix" in vix_df.columns:
                    self._vix_series = vix_df["vix"]
                logger.info("VIX series loaded for hysteresis: %d rows",
                            len(self._vix_series) if self._vix_series is not None else 0)
        except Exception as exc:
            logger.warning("VIX series load for hysteresis failed: %s", exc)

    def _build_liquid_universe(self) -> list[str]:
        """
        Apply liquidity filter. Returns list of passing tickers.
        Re-checks annually at Jan 1 of each year  -  a stock liquid in 2022
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
                # BUG-238 RESOLVED-IMPLEMENTED Batch 98 2026-05-12: fail-closed
                # on missing market_cap. Previously the filter only rejected
                # when `mkt_cap_m > 0 and < min`, so any ticker without
                # market_cap data (e.g. delisted, recent IPO with stale ref
                # row, or Polygon reference gap) silently passed the gate.
                # Now: missing data (mkt_cap_m == 0) fails the filter unless
                # LIQUIDITY config explicitly sets min_market_cap_m=0.
                mkt_cap_m = (self.info_dict.get(ticker, {}).get("market_cap", 0) or 0) / 1_000_000
                _min_cap = LIQUIDITY["min_market_cap_m"]
                if _min_cap > 0 and mkt_cap_m < _min_cap:
                    continue
                passing.add(ticker)

        # BUG-222 RESOLVED-IMPLEMENTED Batch 117 2026-05-12 (owner-
        # approved option B 2026-05-12): tier-specific PIT S&P 500
        # filter. Load T1a master set (all tickers ever in T1a) + PIT
        # membership per year_start. Tickers in T1a master must
        # intersect with PIT membership at year_start to pass the
        # annual liquid set; tickers NOT in T1a master (T1 ETFs, T2
        # spinoffs, T3 momentum) bypass the PIT intersection and use
        # OHLCV liquidity only. Empty T1a master (CSV read failure)
        # disables the intersection entirely so the engine falls back
        # to pre-Batch-117 no-PIT behavior.
        from backtest.data.universe import (
            get_t1a_master_set,
            get_sp500_constituents_pit,
        )
        _t1a_master = get_t1a_master_set()

        # Build per-year liquid set for daily screening
        self._annual_liquid: dict[int, set] = {}
        for ref_date in check_dates:
            # BUG-222: per-year T1a PIT membership (only if T1a master is
            # populated; otherwise empty set + skip PIT intersection below)
            if _t1a_master:
                _t1a_pit_at_year = set(get_sp500_constituents_pit(ref_date))
            else:
                _t1a_pit_at_year = set()
            year_set = set()
            for ticker, df in self.ohlcv_dict.items():
                sliced = df[df.index.date <= ref_date]
                if len(sliced) < 30:
                    continue
                if float(sliced["close"].iloc[-1]) < LIQUIDITY["min_price"]:
                    continue
                if float(sliced["volume"].tail(20).mean()) < LIQUIDITY["min_avg_volume"]:
                    continue
                # BUG-222 tier-specific PIT filter: T1a-classified tickers
                # must be in the PIT S&P 500 set at year_start; other tier
                # tickers bypass.
                if (_t1a_master and ticker in _t1a_master
                        and ticker not in _t1a_pit_at_year):
                    continue
                year_set.add(ticker)
            self._annual_liquid[ref_date.year] = year_set

        return list(passing)

    def _get_liquid_universe_for_date(self, as_of: date) -> set:
        """Return the liquid universe for the year of as_of."""
        if hasattr(self, "_annual_liquid"):
            return self._annual_liquid.get(as_of.year, set(self.liquid_universe))
        return set(self.liquid_universe)

    def _get_sector_pit_for_ticker(self, ticker: str, as_of: date) -> str:
        """BUG-218 + BUG-239 RESOLVED-IMPLEMENTED Batch 116 2026-05-12 (owner-
        approved option A 2026-05-12): PIT-correct sector lookup at the
        engine level. Wraps `backtest.data.universe.get_sector_pit` so
        sector reclassifications in `Backtesting universe/sector_history.csv`
        (e.g. META 2018 IT->Comms, V/MA 2023 IT->Financials, T/VZ 2018
        Telecom->Comms, NFLX/DIS/CMCSA 2018 CD->Comms) apply correctly
        to trades whose as_of predates the reclassification.

        Falls back to the snapshot `self.sector_map` when the PIT helper
        returns "Unknown" or raises (e.g. universe module not available
        in unit-test fixture). This preserves existing behavior for
        tickers not in sector_history.csv.

        Used at 3 engine sites: concentration breach gate (line 811),
        entry context for sector ETF lookup (line 1095), and
        _run_agent_context (line 1288). Portfolio internal sector dict
        keys are migrated implicitly: `add_position(ticker, sector, ...)`
        is the only writer and now receives the PIT-correct sector at
        entry time, so all downstream concentration accounting reads
        the entry-time sector correctly.
        """
        fallback = self.sector_map.get(ticker, "Unknown")
        try:
            from backtest.data.universe import get_sector_pit
            pit_sector = get_sector_pit(ticker, as_of, fallback=fallback)
            return pit_sector if pit_sector else fallback
        except Exception:
            return fallback

    # ----------------------------------------------------------------------
    # MAIN LOOP
    # ----------------------------------------------------------------------

    def run(self):
        if not self.ohlcv_dict:
            self.load_data()

        trading_days = self._trading_days()
        # DEC-515 Level 6 CB: record backtest start date for min_history check
        if trading_days:
            self._backtest_start_date = trading_days[0]
        # DEC-179 RESOLVED-IMPLEMENTED Batch 83 2026-05-12 owner-mandated
        # wiring: memory profiling consumed by engine.run(). Helper has
        # lived in improvements.py since Batch 57 but was never called;
        # this wiring closes the helper-only gap so the engine logs RSS
        # at start / every 50 days / finalize and warns on cap breach.
        from backtest.engine.improvements import (
            check_memory_cap,
            MEMORY_CAP_MB_DEFAULT,
        )
        _mem_start = check_memory_cap(cap_mb=MEMORY_CAP_MB_DEFAULT)
        logger.info(
            "DEC-179 memory at run() start: %s MB / cap %s MB (breached=%s)",
            _mem_start["current_mb"], _mem_start["cap_mb"],
            _mem_start["breached"],
        )
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
            # DEC-179 Batch 83: periodic memory check every 50 days; warn
            # on cap breach. Does not abort -- caller may opt to terminate
            # by inspecting return-value note in finalize log.
            if i > 0 and i % 50 == 0:
                _mem = check_memory_cap(cap_mb=MEMORY_CAP_MB_DEFAULT)
                if _mem["breached"]:
                    logger.warning(
                        "DEC-179 MEMORY_CAP_BREACHED at day %d: %s MB > %s MB",
                        i, _mem["current_mb"], _mem["cap_mb"],
                    )
                else:
                    logger.debug(
                        "DEC-179 memory at day %d: %s MB / cap %s MB",
                        i, _mem["current_mb"], _mem["cap_mb"],
                    )
            # Incremental checkpoint every 25 days  -  trade log survives crashes
            if i > 0 and i % 25 == 0 and self.closed_trades:
                try:
                    import pandas as _pd
                    checkpoint_path = self.output_dir / "trade_log_checkpoint.csv"
                    _pd.DataFrame([vars(t) for t in self.closed_trades]).to_csv(
                        checkpoint_path, index=False)
                    logger.debug("Checkpoint: %d trades -> %s", len(self.closed_trades), checkpoint_path)
                except Exception:
                    pass
            try:
                self._process_day(as_of)
            except Exception as exc:
                logger.error("Day %s failed: %s", as_of, exc, exc_info=True)

        # BUG-29 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 8 2026-05-10:
        # Force-close any remaining open trades at last available close price so
        # they're included in final metrics. Without this, open winners inflated
        # results (silently capped by trailing stop not yet triggered) and open
        # losers disappeared entirely. Both biases removed by end-of-backtest
        # finalization at mark-to-market exit.
        n_finalized = self._finalize_open_trades()

        # DEC-149 RESOLVED-IMPLEMENTED Batch 79 2026-05-12 owner-mandated
        # wiring: compute regime transition matrix from accumulated daily
        # regime history. Stored on self for retrieval by writer / agents.
        # O(n) one-time at finalize; not in hot loop.
        try:
            from backtest.engine.regime_filter import (
                compute_regime_transition_matrix,
            )
            self._regime_transition_matrix = compute_regime_transition_matrix(
                self._regime_history,
            )
            logger.info(
                "DEC-149 regime transition matrix computed from %d daily regimes",
                len(self._regime_history),
            )
        except Exception as _exc:
            logger.debug("DEC-149 regime transition matrix computation skipped: %s", _exc)
            self._regime_transition_matrix = None

        # DEC-179 Batch 83: end-of-run memory snapshot for capacity tuning.
        _mem_end = check_memory_cap(cap_mb=MEMORY_CAP_MB_DEFAULT)
        logger.info(
            "DEC-179 memory at run() finalize: %s MB / cap %s MB (breached=%s)",
            _mem_end["current_mb"], _mem_end["cap_mb"], _mem_end["breached"],
        )
        self._memory_profile = {"start": _mem_start, "end": _mem_end}

        logger.info("Backtest complete. Open=%d Closed=%d Skipped=%d (finalized %d at end-of-backtest)",
                    len(self.open_trades), len(self.closed_trades),
                    len(self.skipped_trades), n_finalized)

    def _finalize_open_trades(self) -> int:
        """Force-close remaining open trades at the last available close price.

        BUG-29 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 8 2026-05-10:
        Previously open trades at backtest end were silently discarded. This
        biased results upward because winning open trades (still trending) didn't
        register against their unrealized loss potential, while losing open trades
        also vanished. Fix: mark-to-market each remaining open trade at the last
        available close price on or before self.end, with exit_reason set to
        'end_of_backtest'. Per-trade MAE/MFE preserved from OpenTrade running state.

        Returns: count of trades finalized.
        """
        if not self.open_trades:
            return 0
        from backtest.engine.exit_manager import close_trade as _close_trade

        n_finalized = 0
        remaining: list = []  # for trades we cannot finalize (no price data)
        for trade in self.open_trades:
            df = self.ohlcv_dict.get(trade.ticker)
            if df is None or df.empty:
                # No price data available - cannot mark-to-market; leave as open
                remaining.append(trade)
                continue
            try:
                # Use the last close <= self.end (avoids future-dated bars)
                eligible = df[df.index.date <= self.end]
                if eligible.empty:
                    remaining.append(trade)
                    continue
                exit_price = float(eligible["close"].iloc[-1])
                exit_date = eligible.index[-1].date() if hasattr(eligible.index[-1], "date") else self.end
                closed = _close_trade(
                    trade=trade,
                    exit_price=exit_price,
                    exit_date=exit_date,
                    exit_reason="end_of_backtest",
                    max_adverse=trade.max_adverse_excursion,
                    max_favourable=trade.max_favourable_excursion,
                    fail_reason="Backtest period ended before exit signal fired",
                )
                self.closed_trades.append(closed)
                # BUG-95 sub-batch 2: mirror end-of-backtest finalization into
                # Portfolio state so equity_curve reflects realized PnL at run end.
                # hasattr guard tolerates test paths that bypass __init__.
                if hasattr(self, "portfolio") and trade.ticker in self.portfolio.positions:
                    try:
                        self.portfolio.remove_position(trade.ticker, exit_price)
                    except (KeyError, ValueError) as exc:
                        logger.debug(
                            "Portfolio remove_position(%s) during finalize failed: %s",
                            trade.ticker, exc)
                n_finalized += 1
            except Exception as exc:
                logger.warning(
                    "Could not finalize open trade %s (%s entry %s): %s",
                    trade.ticker, trade.strategy, trade.entry_date, exc,
                )
                remaining.append(trade)

        self.open_trades = remaining
        if n_finalized:
            logger.info(
                "End-of-backtest finalization: closed %d open trades at last-available close (exit_reason=end_of_backtest)",
                n_finalized,
            )
        return n_finalized

    def _trading_days(self) -> list[date]:
        # DEC-235 RESOLVED-IMPLEMENTED Batch 82 2026-05-12 owner-mandated
        # wiring: use NYSE calendar helper to skip holidays + half-days
        # in addition to weekends. Falls back to Mon-Fri filter when
        # pandas_market_calendars unavailable.
        from backtest.engine.improvements import is_nyse_trading_day, get_nyse_calendar_helper
        cal = get_nyse_calendar_helper()
        days, d = [], self.start
        while d <= self.end:
            if is_nyse_trading_day(d, calendar=cal):
                days.append(d)
            d += timedelta(days=1)
        return days

    def _process_day(self, as_of: date):
        # -- 1. Slice OHLCV to point-in-time using year-appropriate liquid universe --
        liquid_this_year = self._get_liquid_universe_for_date(as_of)
        ohlcv_pit = {}
        for t in liquid_this_year:
            df = self.ohlcv_dict.get(t)
            if df is None:
                continue
            sliced = df[df.index.date <= as_of]
            if len(sliced) >= 30:
                ohlcv_pit[t] = sliced

        # -- 2. Regime classification  -  direction gating only, no sizing --
        # DEC-317 + DEC-388 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 43
        # engine wiring 2026-05-11: hysteresis active. Pass smoothed VIX (5d
        # SMA) + prev_regime so regime doesn't flip on single noisy prints.
        # When VIX series unavailable (first 5 days or missing cache), falls
        # back to raw VIX with no hysteresis (legacy behavior).
        macro     = macro_snapshot(as_of)
        vix       = macro.get("vix_value")
        spy_close = float(ohlcv_pit["SPY"]["close"].iloc[-1]) if "SPY" in ohlcv_pit else None
        spy_ema   = get_spy_ema200(self.spy_df, as_of) if self.spy_df is not None else None
        # Compute smoothed VIX from pre-loaded series if available
        vix_smoothed = None
        if self._vix_series is not None:
            vix_smoothed = get_vix_smoothed(self._vix_series, as_of, window=5)
        # Use hysteresis only when we have prev_regime + smoothed VIX
        use_hysteresis = (self._prev_regime is not None) and (vix_smoothed is not None)
        regime_ctx = get_regime_context(
            vix, spy_close, spy_ema,
            prev_regime=self._prev_regime,
            vix_smoothed=vix_smoothed,
            use_hysteresis=use_hysteresis,
        )
        regime     = regime_ctx["regime"]
        # Persist for next iteration
        self._prev_regime = regime

        # DEC-108 RESOLVED-IMPLEMENTED Batch 78 2026-05-12 owner-mandated
        # wiring: EMA-smoothed regime probability (Phase A). Converts the
        # hard regime label to a numeric score (bull=80, neutral=50, bear=30,
        # crisis=10, unknown=50) and applies EMA (alpha=0.1: smoothed =
        # 0.9*prev + 0.1*new). State persisted on self for next-day call.
        # Surfaced via regime_ctx as `regime_score_smoothed`. Joint DEC-388
        # VIX-SMA hysteresis (already wired Batch 42-43) -- this DEC adds
        # the regime-score smoothing layer for downstream agent / signal
        # consumption (Phase B strategies migrate to probability-gating
        # later; currently this is telemetry).
        from backtest.engine.regime_filter import (
            ema_smooth_regime_probability as _ema_regime,
        )
        _regime_score_map = {
            "bull": 80.0, "neutral": 50.0, "bear": 30.0,
            "crisis": 10.0, "unknown": 50.0,
        }
        _raw_score = _regime_score_map.get(regime, 50.0)
        _smoothed = _ema_regime(
            _raw_score, prev_smoothed=getattr(self, "_regime_smoothed", None),
            alpha=0.1,
        )
        self._regime_smoothed = _smoothed
        regime_ctx["regime_score_smoothed"] = round(_smoothed, 2)
        # DEC-149 RESOLVED-IMPLEMENTED Batch 79 2026-05-12: append regime to
        # history for end-of-run transition-matrix computation. Cheap O(1)
        # per day; matrix computed once at finalize().
        self._regime_history.append(regime)
        # DEC-106 RESOLVED-IMPLEMENTED Batch 80 2026-05-12 owner-mandated
        # wiring: multi-input regime scorecard (Phase A telemetry). Uses
        # whatever inputs are currently available (VIX + SPY trend + AAII
        # + CNN F&G); missing inputs (yield curve, HY spread, ICSA, breadth,
        # sector dispersion) skipped per helper semantics. Surfaced via
        # regime_ctx['multi_input_regime'] for downstream consumption.
        # Joint DEC-150 (multi-asset; needs cross-asset plumbing) + DEC-151
        # (sector regime; needs sector ETF plumbing).
        try:
            from backtest.engine.regime_filter import multi_input_regime_score
            spy_above = (spy_close is not None and spy_ema is not None
                         and spy_close > spy_ema)
            aaii_bull = sent.get("aaii", {}).get("bullish_pct", None)
            aaii_bear = sent.get("aaii", {}).get("bearish_pct", None)
            aaii_spread = (
                (aaii_bull - aaii_bear)
                if (aaii_bull is not None and aaii_bear is not None) else None
            )
            cnn_fg = sent.get("fear_greed", {}).get("score", None)
            mi_result = multi_input_regime_score(
                vix=vix,
                spy_above_200ema=spy_above,
                aaii_bull_bear_spread=aaii_spread,
                cnn_fg=cnn_fg,
            )
            regime_ctx["multi_input_regime"] = mi_result
        except Exception as _exc:
            logger.debug("DEC-106 multi-input regime score skipped: %s", _exc)
        # Pass 53 fix 2026-05-07: hoist crisis_flag to function scope so it's
        # defined before line 299 (was UnboundLocalError when regime != crisis
        # and inner-loop set never executed). Per DEC-316 unknown regime exists.
        # BUG-02 RESOLVED-IMPLEMENTED Pass 53 v8h+1 cross-reference 2026-05-10:
        # this hoisting also addresses BUG-02 (`days` UnboundLocalError pattern).
        # BUG-01 RESOLVED-IMPLEMENTED Pass 53 v8h+1 cross-reference 2026-05-10:
        # this is the canonical crisis_flag pre-definition that prevents the
        # original BUG-01 NameError when regime is not "crisis".
        crisis_flag = regime == "crisis"
        # Note: regime_ctx used for direction gating only  -  no position sizing in backtest

        # -- 3. Build today's bars for exit manager --
        ticker_bars = self._build_today_bars(as_of, ohlcv_pit)

        # -- 4. Process exits --
        active_signals = {}
        # Batch 226: pass trailing VIX series for VIX-spike kill switch.
        # Defensive: process_day_exits no-ops when vix_history=None.
        _vix_history_for_exits = None
        try:
            if hasattr(self, "_vix_series") and self._vix_series is not None:
                _vs = self._vix_series
                if hasattr(_vs.index, "date"):
                    _sliced = _vs[_vs.index.date <= as_of]
                else:
                    _sliced = _vs[_vs.index <= as_of]
                if len(_sliced) > 0:
                    _vix_history_for_exits = _sliced.tolist()
        except Exception:
            _vix_history_for_exits = None
        closed_today, self.open_trades = process_day_exits(
            self.open_trades, ticker_bars, as_of,
            vix, regime, active_signals, self.circuit_breaker_log,
            vix_history=_vix_history_for_exits,
        )
        self.closed_trades.extend(closed_today)

        # BUG-95 sub-batch 2: remove closed positions from portfolio state
        # (mirror trade exits into Portfolio.cash credit + position removal).
        # hasattr guard tolerates test paths that build BacktestEngine via
        # __new__ without running __init__ (e.g. test_bug_029 finalize test).
        if hasattr(self, "portfolio"):
            for ct in closed_today:
                if ct.ticker in self.portfolio.positions:
                    try:
                        self.portfolio.remove_position(ct.ticker, ct.exit_price)
                    except (KeyError, ValueError) as exc:
                        logger.debug("Portfolio remove_position(%s) failed: %s",
                                     ct.ticker, exc)

            # BUG-95 sub-batch 2: mark portfolio to today's close prices and append
            # to equity_curve. ticker_bars holds today's close for every ticker with
            # data today. Missing prices: Portfolio.mark_to_market carries forward
            # last_mark per position; no crash on sparse data.
            today_prices = {
                t: float(bar["close"]) for t, bar in ticker_bars.items()
                if isinstance(bar, dict) and "close" in bar
            }
            self.portfolio.mark_to_market(today_prices, as_of)
            # Benchmark curve: SPY close
            if "SPY" in today_prices:
                self.portfolio.add_benchmark_point(as_of, today_prices["SPY"])

        # -- 5. Screen universe  -  no daily liquidity filter --
        # Batch 204 (Bollinger optimization 2026-05-17): pass VIX context so
        # macro-overlay-aware strategies (bollinger_lower / bollinger_tight)
        # can read vix_percentile + vix_band from the per-ticker signals
        # dict. When VIX history unavailable, extra kwargs are no-ops.
        _vix_today_for_screen = None
        _vix_history_for_screen = None
        if hasattr(self, "_vix_series") and getattr(self, "_vix_series", None) is not None:
            try:
                _vs = self._vix_series
                if hasattr(_vs.index, "date"):
                    _sliced = _vs[_vs.index.date <= as_of]
                else:
                    _sliced = _vs[_vs.index <= as_of]
                if len(_sliced) > 0:
                    _vix_today_for_screen = float(_sliced.iloc[-1])
                    _vix_history_for_screen = _sliced.tolist()
            except Exception:
                _vix_today_for_screen = None
                _vix_history_for_screen = None
        candidates     = screen_universe(
            ohlcv_pit, self.info_dict, as_of, regime,
            vix_value=_vix_today_for_screen,
            vix_history=_vix_history_for_screen,
        )
        active_signals = {c["ticker"]: c for c in candidates}
        sent           = sentiment_snapshot(as_of)

        # -- 5.5 DEC-515 Level 6 portfolio DD-from-peak circuit breaker --
        # (Pass 53 Day-9-evening v5 engine wiring per DEC-594)
        # Compute today's portfolio equity from closed trades; update Level 6 state;
        # if halt_active, block all new entries this day.
        from backtest.engine.circuit_breakers import update_level_6_state
        days_since_start = (as_of - self._backtest_start_date).days if self._backtest_start_date else 0
        # Equity proxy: cumulative pnl_dollar of closed trades
        try:
            closed_pnl_total = sum(float(t.pnl_dollar) for t in self.closed_trades
                                    if hasattr(t, "pnl_dollar") and t.pnl_dollar is not None)
            current_equity = 100000.0 + closed_pnl_total  # initial $100k baseline
        except Exception:
            current_equity = 100000.0
        l6_result = update_level_6_state(
            self.level_6_state, current_equity=current_equity, as_of=as_of,
            days_since_start=days_since_start,
        )
        if l6_result.get("event") in ("halt_triggered", "halt_resumed"):
            self.circuit_breaker_log.append({
                "date": as_of, "level": 6,
                "event": l6_result["event"],
                "dd_from_peak": l6_result["dd_from_peak"],
                "rolling_peak_equity": l6_result["rolling_peak_equity"],
                "current_equity": current_equity,
            })
        if self.level_6_state.halt_triggered:
            # Halt = no new entries this day; existing trades continue under exit logic
            for cand in candidates[:self.max_cands]:
                self.skipped_trades.append({
                    "ticker": cand["ticker"], "date": as_of,
                    "strategy": cand.get("strategies", [{}])[0].get("strategy", "unknown"),
                    "reason": f"level_6_halt_dd_{l6_result['dd_from_peak']:.3f}",
                })
            return  # skip entry loop entirely

        # DEC-314 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 45 2026-05-11
        # (owner-approved Path C). Market-wide circuit breaker Levels 3/4/5
        # (NYSE Rule 80B intraday thresholds -7%/-13%/-20%). Daily-data proxy:
        # SPY intraday low vs open = (low - open) / open. When low dropped
        # >= 7%/13%/20% from open, market-wide CB triggered that day. Block
        # all new entries; existing positions continue under exit logic.
        # Level 3 (intraday halt + 15% from entry, config.level_3_halt_loss_pct)
        # requires real-time intraday data; deferred to Stage 3 paper trading.
        if "SPY" in ohlcv_pit:
            spy_today_df = ohlcv_pit["SPY"][ohlcv_pit["SPY"].index.date == as_of]
            if not spy_today_df.empty:
                spy_today = spy_today_df.iloc[-1]
                spy_open = float(spy_today.get("open", 0))
                spy_low = float(spy_today.get("low", 0))
                if spy_open > 0:
                    intraday_low_pct = (spy_low - spy_open) / spy_open
                    market_cb_level = None
                    if intraday_low_pct <= -0.20:
                        market_cb_level = 5
                    elif intraday_low_pct <= -0.13:
                        market_cb_level = 4
                    elif intraday_low_pct <= -0.07:
                        market_cb_level = 3
                    if market_cb_level is not None:
                        self.circuit_breaker_log.append({
                            "date": as_of, "level": market_cb_level,
                            "event": f"market_wide_cb_nyse_rule_80b_level_{market_cb_level - 2}",
                            "spy_intraday_low_pct": round(intraday_low_pct, 4),
                            "spy_open": spy_open, "spy_low": spy_low,
                        })
                        for cand in candidates[:self.max_cands]:
                            self.skipped_trades.append({
                                "ticker": cand["ticker"], "date": as_of,
                                "strategy": cand.get("strategies", [{}])[0].get("strategy", "unknown"),
                                "reason": f"market_wide_cb_level_{market_cb_level}_spy_low_{intraday_low_pct:.3f}",
                            })
                        return  # skip entry loop entirely

        # DEC-128 RESOLVED-IMPLEMENTED Batch 77 2026-05-12 owner-mandated
        # wiring: dispersion-conditional CB. Trigger if cross-sectional
        # dispersion of today's universe returns exceeds 3 sigma vs rolling
        # 20-day baseline. Halt new entries when extreme cross-sectional
        # vol indicates a regime/correlation breakdown. Joint DEC-314 / 315.
        try:
            import pandas as _pd
            _ret_rows = []
            for _tkr, _df in ohlcv_pit.items():
                if _df is None or _df.empty:
                    continue
                _slice = _df[_df.index.date <= as_of].tail(22)
                if len(_slice) < 22:
                    continue
                _ret = _slice["close"].pct_change().dropna()
                if len(_ret) < 21:
                    continue
                _ret_rows.append(_ret.reset_index(drop=True))
            if len(_ret_rows) >= 5:
                _ret_df = _pd.concat(_ret_rows, axis=1).dropna(how="any")
                if len(_ret_df) >= 21:
                    from backtest.engine.regime_filter import (
                        dispersion_circuit_breaker as _disp_cb,
                    )
                    _cb_result = _disp_cb(
                        _ret_df, window=20, sigma_threshold=3.0,
                    )
                    if _cb_result.get("triggered"):
                        self.circuit_breaker_log.append({
                            "date": as_of,
                            "event": "dispersion_cb_triggered_dec128",
                            "z_score": _cb_result["z_score"],
                            "today_dispersion": _cb_result["today_dispersion"],
                        })
                        for cand in candidates[:self.max_cands]:
                            self.skipped_trades.append({
                                "ticker": cand["ticker"], "date": as_of,
                                "strategy": cand.get("strategies", [{}])[0].get(
                                    "strategy", "unknown",
                                ),
                                "reason": (
                                    f"dispersion_cb_dec128_z_"
                                    f"{_cb_result['z_score']:.2f}"
                                ),
                            })
                        return
        except Exception as _exc:
            # Dispersion CB is informational; never fail the run on this path
            logger.debug("Dispersion CB skipped: %s", _exc)

        # -- 6. Open new trades  -  no position cap, no correlation filter,
        #         direction hard block removed; ticker-level concurrent block ON --
        # Track open ticker+strategy combos to avoid exact duplicates only
        open_combos = {(t.ticker, t.strategy) for t in self.open_trades}
        # BUG-61 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 17 2026-05-10
        # (owner-approved Option A): match live max_positions_per_ticker=1 by
        # blocking any new entry on a ticker that already has an open position.
        # Previously, different strategies on consecutive days each opened a
        # position on the same trending ticker, accumulating 10+ concurrent
        # positions in backtest where live would hold only 1. Inflated backtest
        # ROI in trending regimes; removed by this ticker-set membership check.
        open_tickers = {t.ticker for t in self.open_trades}
        # Deduplication: track tickers already opened today (one position per ticker per day)
        # Batch 279: opened_today set removed - dedup eliminated per Option 1.
        # See per-strategy-loop notes ~line 1043 for full rationale.

        for cand in candidates[:self.max_cands]:
            ticker = cand["ticker"]
            atr    = cand.get("atr", 0.0) or cand["last_close"] * 0.01
            close  = cand["last_close"]

            # Batch 279 (2026-05-20 owner-approved Option 1): dedup removed.
            # Multiple strategies firing on the same ticker the same day each
            # open their own position with size_pct / N split (where N is
            # the candidate's strategy_count). Prior behavior gave the slot
            # to whichever strategy came first in ALL_STRATEGIES dict
            # insertion order - an arbitrary artifact of registration order
            # rather than empirical edge. See SMOKE_STAGE_B_v3_DIAGNOSIS.
            # The BUG-61 block STILL applies to cross-day concurrent
            # positions (don't stack same-ticker exposure across days).
            _n_strategies_for_split = max(1, len(cand.get("strategies", [])))

            # BUG-61: ticker-level concurrent-position block (owner-approved Option A)
            # Skip the entire strategy loop if any prior open position exists on this ticker
            if ticker in open_tickers:
                self.skipped_trades.append({
                    "ticker": ticker, "date": as_of,
                    "strategy": "(any)",
                    "reason": "ticker_already_open_concurrent_block_bug61",
                })
                continue

            # DEC-018 RESOLVED-IMPLEMENTED Batch 73 2026-05-12 owner-mandated
            # wiring: 5-trading-day cooldown after a stop-out on this ticker.
            # Prevents whipsaw re-entry into a name that just hit our stop.
            # Joint DEC-135 per-ticker max-loss cap (separate gate, same theme).
            # Inline check (avoids per-call DataFrame build): scan
            # self.closed_trades for stop_loss exits on this ticker within
            # TICKER_STOPOUT_COOLDOWN_DAYS.
            from backtest.config import TICKER_STOPOUT_COOLDOWN_DAYS
            cooldown_breach = False
            for ct in self.closed_trades:
                if ct.ticker != ticker:
                    continue
                reason = str(getattr(ct, "exit_reason", "")).lower()
                if "stop" not in reason:
                    continue
                ct_exit = getattr(ct, "exit_date", None)
                if ct_exit is None:
                    continue
                # Robust date subtraction (handles both date and datetime)
                try:
                    days_since = (as_of - ct_exit).days
                except TypeError:
                    continue
                if 0 <= days_since < TICKER_STOPOUT_COOLDOWN_DAYS:
                    cooldown_breach = True
                    break
            if cooldown_breach:
                self.skipped_trades.append({
                    "ticker": ticker, "date": as_of,
                    "strategy": "(any)",
                    "reason": (
                        f"stopout_cooldown_active_{TICKER_STOPOUT_COOLDOWN_DAYS}d_dec018"
                    ),
                })
                continue

            # DEC-135 RESOLVED-IMPLEMENTED Batch 75 2026-05-12: per-ticker
            # 30-day cumulative max-loss cap. If sum of pnl_pct on this ticker
            # over the trailing 30 days <= -10%, halt entries for cooldown.
            _cap_pct = -10.0
            _window_days = 30
            _cum_pnl = 0.0
            for ct in self.closed_trades:
                if ct.ticker != ticker:
                    continue
                ct_exit = getattr(ct, "exit_date", None)
                if ct_exit is None:
                    continue
                try:
                    days_ago = (as_of - ct_exit).days
                except TypeError:
                    continue
                if 0 <= days_ago <= _window_days:
                    _cum_pnl += float(getattr(ct, "pnl_pct", 0.0) or 0.0)
            if _cum_pnl <= _cap_pct:
                self.skipped_trades.append({
                    "ticker": ticker, "date": as_of,
                    "strategy": "(any)",
                    "reason": (
                        f"max_loss_cap_breach_dec135_{round(_cum_pnl, 2)}pct"
                    ),
                })
                continue

            # DEC-076 RESOLVED-IMPLEMENTED Batch 74 2026-05-12 owner-mandated
            # wiring: factor concentration breaker. If candidate's sector is
            # currently >25% of total portfolio equity, gate the entry.
            # Joint DEC-070 portfolio-level exit logic. Uses
            # Portfolio.factor_concentration_breach() which reads
            # exposure_by_sector and flags any sector above threshold.
            # Batch 223 (research review Section C #3 owner-approved
            # 2026-05-18): tighten sector cap 30% -> 25% per Litterman
            # 2003 *Modern Investment Management* Ch 17 industry standard.
            if hasattr(self, "portfolio") and self.portfolio.positions:
                _conc = self.portfolio.factor_concentration_breach(
                    sector_threshold_pct=25.0,
                )
                if _conc.get("any_breach"):
                    # Candidate's own sector contributes to the breach -- skip
                    # BUG-218/239 Batch 116: PIT-correct sector lookup so the
                    # concentration gate uses the as_of sector for tickers in
                    # sector_history.csv (e.g. META pre-2018 = "Information Technology").
                    cand_sector = self._get_sector_pit_for_ticker(ticker, as_of)
                    if cand_sector in _conc.get("sector_breaches", []):
                        self.skipped_trades.append({
                            "ticker": ticker, "date": as_of,
                            "strategy": "(any)",
                            "reason": (
                                f"factor_concentration_breach_dec076_"
                                f"{cand_sector}_{_conc['max_sector'][1]:.0f}pct"
                            ),
                        })
                        continue

            # Batch 223 (correlation cap 2026-05-18 owner-approved): refuse
            # entry if candidate is highly-correlated to any open position
            # (Carver 2015 *Systematic Trading* Ch 10 IDM). |corr|>=0.85
            # skip; 0.70<=|corr|<0.85 halve size; else no adjustment. The
            # multiplier is applied at the sizing stack below; the skip
            # branch fires here when full correlation lockout triggers.
            _corr_mult = 1.0
            _corr_max = 0.0
            if hasattr(self, "portfolio") and self.portfolio.positions:
                try:
                    from backtest.engine.correlation_gate import (
                        correlation_with_open_positions,
                        correlation_size_multiplier,
                    )
                    _corr_info = correlation_with_open_positions(
                        ticker, self.ohlcv_dict,
                        list(self.portfolio.positions.keys()),
                        as_of,
                    )
                    _corr_max = _corr_info.get("max_abs_corr", 0.0)
                    _corr_mult = correlation_size_multiplier(_corr_max)
                    if _corr_mult == 0.0:
                        self.skipped_trades.append({
                            "ticker": ticker, "date": as_of,
                            "strategy": "(any)",
                            "reason": (
                                f"correlation_cap_batch223_"
                                f"corr_{_corr_max:.2f}_with_"
                                f"{_corr_info.get('max_corr_ticker', '?')}"
                            ),
                        })
                        continue
                except Exception:
                    _corr_mult = 1.0
                    _corr_max = 0.0

            # Batch 274 (2026-05-20 owner-approved): REVERTED Batch 272.
            # Stage B smoke (20 tkrs x 2y) showed Batch 272's category-priority
            # dedup sort had unintended consequence - cpr_narrow_momentum
            # (confluence category, 4 signals) won dedup over every competing
            # strategy and fired 102x at -14.4% mean PnL vs 1x in T1a baseline.
            # break_retest_confluence similarly went from 0 -> 14 firings at
            # 0% WR. Empirical edge does NOT correlate with confluence
            # tagging; categorical priority forced losers to fire instead of
            # winners. Pre-Batch-272 dict-insertion-order dedup was at least
            # empirically neutral. Revisit with empirical edge data (post-
            # full-T1a-rerun realized PnL per strategy) in a future batch.
            for strat_entry in cand.get("strategies", []):
                direction = strat_entry["direction"]
                category  = strat_entry["category"]

                # Skip avoid direction - conflicting signals, log as skipped
                # BUG-04 RESOLVED-IMPLEMENTED Pass 53 v8h+1 cross-reference 2026-05-10:
                # avoid direction no longer falls into triggered_short bucket
                if direction == "avoid":
                    self.skipped_trades.append({
                        "ticker": ticker, "date": as_of,
                        "strategy": strat_entry["strategy"],
                        "reason": "avoid_conflicting_signals",
                    })
                    continue

                # BUG-34 RESOLVED-IMPLEMENTED Batch 109 2026-05-12 (owner-
                # approved option C): per-strategy regime blocklist. When
                # STRATEGY_REGIME_BLOCKLIST has an entry for this strategy
                # and the current regime is on its blocklist, skip the entry.
                # Empty default dict = no behavior change; owner populates
                # after Phase 1B-alpha per-regime verdict empirical tuning.
                from backtest.config import STRATEGY_REGIME_BLOCKLIST
                _blocklist = STRATEGY_REGIME_BLOCKLIST.get(strat_entry["strategy"], [])
                if regime in _blocklist:
                    self.skipped_trades.append({
                        "ticker": ticker, "date": as_of,
                        "strategy": strat_entry["strategy"],
                        "reason": f"regime_blocklist_{regime}_bug34",
                    })
                    continue

                # Batch 203 (regime SELECTOR per AMH research review owner-
                # approved 2026-05-17): the BUG-34 blocklist is a hard
                # exclusion; the SELECTOR adds a soft regime-affinity
                # filter. Strategies in STRATEGY_REGIME_AFFINITY only fire
                # in their permitted regime set; unmapped strategies retain
                # default allow-all behavior. Phase 1A-beta showed
                # strong regime-coupling (-117pp 2022 / +517 2024 / +792
                # 2025) but no selection mechanism. Affinity initialized
                # from Phase 1A-beta carriers analysis; owner re-tunes
                # post-Phase-1B-alpha empirical verdicts.
                from backtest.engine.regime_selector import (
                    should_strategy_fire_in_regime,
                )
                if not should_strategy_fire_in_regime(
                        strat_entry["strategy"], regime):
                    self.skipped_trades.append({
                        "ticker": ticker, "date": as_of,
                        "strategy": strat_entry["strategy"],
                        "reason": f"regime_affinity_block_{regime}_batch203",
                    })
                    continue

                # Crisis long exclusions  -  block long entries on specific tickers
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

                # Skip only exact duplicate  -  same ticker AND same strategy already open
                if (ticker, strat_entry["strategy"]) in open_combos:
                    continue

                # Batch 279 (2026-05-20 owner-approved Option 1): REMOVED the
                # prior dedup skip-reason block. Previously, the first strategy
                # to iterate ALL_STRATEGIES.items() opened the position and all
                # later strategies on the same ticker were skipped - position-
                # in-dict determined the winner, an arbitrary design with no
                # relationship to edge. Now all firing strategies on the same
                # ticker the same day open their own positions; size is split
                # via _n_strategies_for_split below so aggregate ticker exposure
                # stays bounded.
                #
                # BUG-12 RESOLVED-IMPLEMENTED Pass 53 v8h+1 cross-reference
                # (history note retained): the prior dedup ordering by
                # strategy_count desc was a partial fix for the directional
                # bias bug (long strategies always won over shorts). Batch 279
                # supersedes that fix entirely - shorts and longs both fire
                # independently on the same ticker; strategy_count is no
                # longer used for dedup arbitration.

                # Regime flag  -  no hard block on any direction
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
                # BUG-110 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 16 2026-05-10:
                # entry gap filter IS enforced via validate_entry_zone + skip-on-not-valid
                # below; trades exceeding ENTRY_GAP_ATR_MULT[category] x ATR are logged
                # to skipped_trades with explicit reason and NOT entered. Per-category
                # multiplier defined in backtest.config.
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

                # Stage 1  -  rule-based preliminary tier
                preliminary_tier = self._assign_confidence_tier(
                    len(cand["strategies"]), sm, macro, sent)

                # Earnings proximity  -  context for agents, not a blocker
                earn_days = days_to_next_earnings(ticker, as_of)

                # DEC-348 RESOLVED-IMPLEMENTED Batch 76 2026-05-12 owner-
                # mandated wiring: event-calendar suppression. Skip entry
                # if as_of is within DEC-349 asymmetric window (pre=1, post=3)
                # of FOMC / CPI / NFP / per-ticker earnings. Joint DEC-256
                # (earnings calendar) + DEC-407/448 (FRED FOMC/CPI dates) +
                # DEC-349 (asymmetric window). Conservative gate -- earnings_
                # tolerant strategies (DEC-013 attribute) bypass via per-
                # strategy override (deferred to attribute-honoring batch).
                from backtest.config import (EVENT_WINDOW_PRE_DAYS,
                                              EVENT_WINDOW_POST_DAYS,
                                              EVENT_WINDOWS_BATCH191)
                _event_suppressed = False
                _suppression_reason = None
                if earn_days is not None:
                    # earn_days is positive when earnings ahead, negative after
                    # Earnings retains DEC-349 default window (pre=1, post=3).
                    if -EVENT_WINDOW_POST_DAYS <= earn_days <= EVENT_WINDOW_PRE_DAYS:
                        _event_suppressed = True
                        _suppression_reason = (
                            f"EVENT_SUPPRESSION_EARNINGS_d{earn_days}_dec348"
                        )
                # Macro events (FOMC/CPI/NFP) -- macro['near_high_impact_event']
                # already populated upstream. Batch 191 owner-approved 2026-05-16:
                # per-event-type windows replace the single DEC-349 window for
                # macro types. CPI / NFP: d=0 only. FOMC: d-1 + d=0 (Lucca-Moench
                # pre-FOMC drift). Unknown event types fall back to DEC-349 default.
                if not _event_suppressed and macro.get("near_high_impact_event"):
                    days_to_event = macro.get("event_days_away")
                    ev_type = macro.get("event_type", "macro")
                    ev_type_upper = ev_type.upper()
                    _pre, _post = EVENT_WINDOWS_BATCH191.get(
                        ev_type_upper,
                        (EVENT_WINDOW_PRE_DAYS, EVENT_WINDOW_POST_DAYS),
                    )
                    if days_to_event is not None and \
                            -_post <= days_to_event <= _pre:
                        _event_suppressed = True
                        _suppression_reason = (
                            f"EVENT_SUPPRESSION_{ev_type_upper}_d{days_to_event}_dec348"
                        )
                # Batch 224 (pre-FOMC sleeve 2026-05-18): strategies tagged
                # in STRATEGIES_BYPASS_EVENT_SUPPRESSION are explicitly
                # designed to TRADE INTO macro event windows (e.g.
                # Lucca-Moench 2015 pre-FOMC drift). Bypass the suppression
                # gate for these strategies; non-tagged strategies still
                # respect Batch 191 windows.
                if _event_suppressed:
                    from backtest.config import STRATEGIES_BYPASS_EVENT_SUPPRESSION
                    if strat_entry["strategy"] in STRATEGIES_BYPASS_EVENT_SUPPRESSION:
                        # Strategy explicitly trades events; do not suppress
                        pass
                    else:
                        self.skipped_trades.append({
                            "ticker": ticker, "date": as_of,
                            "strategy": strat_entry["strategy"],
                            "reason": _suppression_reason,
                        })
                        continue

                # Trailing stop
                if direction == "long":
                    init_stop = entry_price * (1 - TRAILING_STOP["initial_pct"])
                else:
                    init_stop = entry_price * (1 + TRAILING_STOP["initial_pct"])

                # Stage 2  -  agent quality assessment adjusts tier +/-1 level
                context_para = ""
                agent_score = 50
                agent_result = {}
                if self.run_agents:
                    context_para, agent_score, agent_result = self._run_agent_context(
                        ticker, as_of, cand, strat_entry, macro, sent, sm, earn_days)
                    tier = self._adjust_tier_by_agent(preliminary_tier, agent_score)
                else:
                    tier = preliminary_tier

                # Batch 190 (INV-049 fix): block AVOID tier for BOTH directions.
                # Prior code blocked only AVOID-long with comment "may be
                # evaluated as short setup separately" -- but the intended
                # short-thesis confirmation gate was never added, so AVOID-short
                # trades fell through unfiltered. Phase 1A baseline empirically
                # showed 88 AVOID-short trades averaging -2.79% PnL (worst of
                # all tier-direction combos), confirming the asymmetry was
                # behaviorally incorrect. Block both directions; if future
                # Phase 1B adds an explicit short-thesis confirmation signal,
                # we can re-introduce an opt-in path for AVOID-short.
                if tier == "AVOID":
                    self.skipped_trades.append({
                        "ticker": ticker, "date": as_of,
                        "strategy": strat_entry["strategy"],
                        "reason": f"avoid_tier_{direction}_blocked_batch190",
                    })
                    continue

                # BUG-95 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 20
                # Sub-batch 4/5 (owner-approved Option A): enforce LIVE_TRADING_RULES
                # via Portfolio.can_open. This is the source-side enforcement that
                # makes backtest behave like live trading:
                #   - max_open_positions (default 10): blocks new entries once 10
                #     concurrent positions are held
                #   - drawdown suspend (default >30%): blocks new entries when
                #     portfolio is in deep drawdown (LIVE_TRADING_RULES
                #     drawdown_suspend_threshold)
                #   - insufficient cash: blocks when required notional exceeds
                #     available cash (live broker would reject)
                #   - ticker uniqueness: redundant with BUG-61 outer block but
                #     defends against future refactors that change BUG-61
                # hasattr guard tolerates test paths bypassing __init__.
                if hasattr(self, "portfolio"):
                    size_pct = TIER_POSITION_SIZE_PCT.get(tier, 0.0)
                    # Batch 279 (2026-05-20 owner-approved Option 1): when
                    # N strategies fire on the same ticker the same day, divide
                    # base tier size by N so aggregate ticker exposure stays
                    # bounded. Replaces the prior dict-position dedup rule.
                    if _n_strategies_for_split > 1:
                        size_pct = size_pct / _n_strategies_for_split
                    # DEC-091 RESOLVED-IMPLEMENTED Batch 70 2026-05-12 owner-
                    # mandated wiring: scale size_pct by tiered drawdown-band
                    # multiplier {1.0 / 0.75 / 0.5 / 0.0} at 0/10/20/30% DD.
                    # Adds 10% and 20% size-reduction bands that the existing
                    # can_open(drawdown_suspend_pct=30%) gate does NOT enforce.
                    # 30%+ DD remains a hard halt via both this multiplier (-> 0)
                    # AND can_open (defense in depth).
                    dd_mult = self.portfolio.drawdown_size_multiplier()
                    size_pct = size_pct * dd_mult
                    # DEC-088 RESOLVED-IMPLEMENTED Batch 71 2026-05-12: stack the
                    # portfolio annualized-vol-target scaler on top of DD-band.
                    # Returns 1.0 (no-op) when realized vol unavailable
                    # (insufficient history; first ~21 days), so harmless in
                    # early backtest. Bounded [0.5, 1.5] to prevent extreme
                    # adjustments. Joint with DEC-091 (DD-band) -- both scale
                    # the same size_pct multiplicatively before can_open.
                    vol_scale = self.portfolio.vol_target_scale_factor()
                    size_pct = size_pct * vol_scale
                    # DEC-087 RESOLVED-IMPLEMENTED Batch 72 2026-05-12: per-
                    # position vol-targeted sizing. Uses ATR-derived per-ticker
                    # annualized vol proxy: daily_vol_proxy = ATR/entry_price,
                    # annualized via sqrt(252). High-vol positions (e.g. XOM
                    # during oil shock vol ~40%) get smaller allocations than
                    # low-vol positions (e.g. KO ~15%) at the same edge level.
                    # Bounded multiplier [0.25, 2.0] per DEC-087 spec.
                    # Stacks after DD-band (DEC-091) and portfolio-vol (DEC-088)
                    # so per-position is the innermost adjustment.
                    from backtest.engine.portfolio import vol_targeted_size as _vts
                    import math as _math
                    _ticker_vol_proxy = None
                    if close and close > 0 and atr > 0:
                        _ticker_vol_proxy = (atr / close) * _math.sqrt(252)
                    size_pct_pre_per_pos = size_pct
                    size_pct = _vts(size_pct, _ticker_vol_proxy)
                    per_pos_mult = (
                        (size_pct / size_pct_pre_per_pos)
                        if size_pct_pre_per_pos > 0 else 1.0
                    )
                    # Batch 212 (Lopez de Prado half-Kelly per-strategy
                    # 2026-05-17 owner-approved research review): scale by
                    # per-strategy half-Kelly fraction derived from rolling
                    # 252-day trade log. MacLean-Ziemba-Blazenko (1992):
                    # half-Kelly = 75% of full-Kelly growth at 50% of
                    # volatility. Falls back to 1.0 (no-op) when sample
                    # too small or stats missing. Stacks BEFORE VIX overlay
                    # so VIX adjustment applies on the Kelly-adjusted base.
                    # Batch 219 (HRP wiring 2026-05-18 owner-approved):
                    # additionally apply per-strategy HRP-relative tilt
                    # (Lopez de Prado 2016 JPM). Bounded [0.25, 2.0].
                    # Stacks after Kelly so HRP tilts the Kelly-adjusted size.
                    try:
                        from backtest.engine.sizing_hrp_kelly import (
                            per_strategy_kelly_from_trade_log,
                            per_strategy_hrp_weight_from_trade_log,
                        )
                        _closed_log = pd.DataFrame([
                            {
                                "strategy": ct.strategy,
                                "entry_date": ct.entry_date,
                                "win": getattr(ct, "win", None),
                                "pnl_pct": getattr(ct, "pnl_pct", None),
                            }
                            for ct in getattr(self, "closed_trades", [])
                        ])
                        kelly_mult = per_strategy_kelly_from_trade_log(
                            _closed_log, strat_entry["strategy"],
                            as_of=pd.Timestamp(as_of),
                        )
                        hrp_mult = per_strategy_hrp_weight_from_trade_log(
                            _closed_log, strat_entry["strategy"],
                            as_of=pd.Timestamp(as_of),
                        )
                    except Exception:
                        kelly_mult = 1.0
                        hrp_mult = 1.0
                    size_pct_pre_kelly = size_pct
                    size_pct = size_pct * kelly_mult
                    if kelly_mult != 1.0 and size_pct_pre_kelly > 0:
                        self.sizing_log.append({
                            "ticker": ticker, "date": as_of,
                            "strategy": strat_entry["strategy"],
                            "scaler": "half_kelly_batch212",
                            "multiplier": round(float(kelly_mult), 4),
                        })
                    size_pct_pre_hrp = size_pct
                    size_pct = size_pct * hrp_mult
                    if hrp_mult != 1.0 and size_pct_pre_hrp > 0:
                        self.sizing_log.append({
                            "ticker": ticker, "date": as_of,
                            "strategy": strat_entry["strategy"],
                            "scaler": "hrp_relative_batch219",
                            "multiplier": round(float(hrp_mult), 4),
                        })
                    # Batch 223: correlation cap halving multiplier
                    # (Carver IDM). _corr_mult was computed once before
                    # the strategy loop and applied here so all strategies
                    # firing for this ticker share the same correlation
                    # debit. Already-zero correlation cases skipped above.
                    if _corr_mult != 1.0:
                        size_pct_pre_corr = size_pct
                        size_pct = size_pct * _corr_mult
                        if size_pct_pre_corr > 0:
                            self.sizing_log.append({
                                "ticker": ticker, "date": as_of,
                                "strategy": strat_entry["strategy"],
                                "scaler": "correlation_cap_batch223",
                                "multiplier": round(float(_corr_mult), 4),
                            })
                    # Batch 203 (VIX-conditional sizing overlay per Cederburg
                    # Johnson Maio 2024 Finance Research Letters): scale by
                    # inverse-percentile of VIX over trailing 252 days.
                    # Bounded [0.3, 1.5] per paper. Stacks AFTER per-position
                    # vol-target so this is the outermost market-context
                    # multiplier. Paper documents Sharpe +71% on US equity
                    # overlay backtest with the same scaling rule.
                    from backtest.engine.regime_selector import (
                        vix_percentile_sizing_multiplier,
                    )
                    _vix_history = getattr(self, "_vix_history_cache", None)
                    if _vix_history is None and hasattr(self, "spy_df"):
                        # Lazy-init VIX history from macro cache if available
                        try:
                            _vix_history = list(
                                self.macro_data.get("vix", {}).values()
                            ) if hasattr(self, "macro_data") else None
                        except Exception:
                            _vix_history = None
                        self._vix_history_cache = _vix_history
                    _vix_today = macro.get("vix") if isinstance(macro, dict) else None
                    vix_mult = vix_percentile_sizing_multiplier(
                        _vix_today, _vix_history,
                    )
                    size_pct_pre_vix = size_pct
                    size_pct = size_pct * vix_mult
                    if vix_mult != 1.0 and size_pct_pre_vix > 0:
                        self.sizing_log.append({
                            "ticker": ticker, "date": as_of,
                            "strategy": strat_entry["strategy"],
                            "scaler": "vix_percentile_batch203",
                            "multiplier": round(float(vix_mult), 4),
                        })
                    # Batch 191 (INV-053 optimization) owner-approved 2026-05-16:
                    # sizing scalers (DD-band, portfolio vol-target, per-position
                    # vol-target) route to sizing_log.csv NOT skipped_trades.csv.
                    # These are sizing decisions; the entry still proceeds at the
                    # scaled size. Pre-batch baseline mis-logged 92,345 of these
                    # to skipped_trades.csv polluting rejection accounting
                    # (53.5% of all "skips" were actually sizing events).
                    if dd_mult < 1.0 and size_pct > 0:
                        self.sizing_log.append({
                            "ticker": ticker, "date": as_of,
                            "strategy": strat_entry["strategy"],
                            "scaler": "dd_band",
                            "multiplier": round(float(dd_mult), 4),
                        })
                    if vol_scale != 1.0 and size_pct > 0:
                        self.sizing_log.append({
                            "ticker": ticker, "date": as_of,
                            "strategy": strat_entry["strategy"],
                            "scaler": "portfolio_vol_target",
                            "multiplier": round(float(vol_scale), 4),
                        })
                    if per_pos_mult != 1.0 and size_pct > 0:
                        self.sizing_log.append({
                            "ticker": ticker, "date": as_of,
                            "strategy": strat_entry["strategy"],
                            "scaler": "per_position_vol_target",
                            "multiplier": round(float(per_pos_mult), 4),
                        })
                    if size_pct > 0:
                        # Batch 203 (regime-conditional cap per AMH research):
                        # cap = min(LIVE_TRADING_RULES base, regime cap).
                        # bull:40 / neutral:25 / bear:15 / crisis:10 / unknown:5.
                        # Bear/crisis tightening protects capital in adverse
                        # regimes; static cap-25 was too loose for crisis (per
                        # Phase 1A-beta 2022 -117pp loss year).
                        from backtest.engine.regime_selector import (
                            regime_position_count_cap,
                        )
                        _regime_cap = regime_position_count_cap(regime)
                        _effective_cap = min(
                            LIVE_TRADING_RULES["max_open_positions"],
                            _regime_cap,
                        )
                        ok, reason = self.portfolio.can_open(
                            ticker=ticker, size_pct=size_pct,
                            max_positions=_effective_cap,
                            drawdown_suspend_pct=(
                                LIVE_TRADING_RULES["drawdown_suspend_threshold"] * 100.0
                            ),
                        )
                        if not ok:
                            self.skipped_trades.append({
                                "ticker": ticker, "date": as_of,
                                "strategy": strat_entry["strategy"],
                                "reason": f"portfolio_gate_{reason}",
                            })
                            continue

                # Get sector ETF return for halo effect context
                # BUG-218/239 Batch 116: PIT-correct sector at entry time so
                # the ETF halo context uses the as_of sector classification,
                # not the current-snapshot sector.
                sector = self._get_sector_pit_for_ticker(ticker, as_of)
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

                # DEC-493 (Pass 53 Sprint 2): assign unique trade_id at entry.
                from backtest.engine.exit_manager import make_trade_id
                _tid = make_trade_id(ticker, as_of, strat_entry["strategy"],
                                     direction=direction)
                trade = OpenTrade(
                    ticker=ticker,
                    entry_date=as_of,
                    entry_price=entry_price,
                    direction=direction,
                    strategy=strat_entry["strategy"],
                    category=category,
                    trade_id=_tid,
                    sector=sector,
                    initial_stop=round(init_stop, 4),
                    trailing_stop=round(init_stop, 4),
                    highest_close=entry_price,
                    regime_at_entry=f"{regime}{'_CRISIS_FLAG' if crisis_flag else ''}",
                    # DEC-492 (Pass 53 Sprint 2): filter REMOVED. Pre-fix kept
                    # only (bool, int, float) types, dropping all string/list
                    # signals (e.g. categorical regime tags, signal-list
                    # arrays). Now preserves all signal types  -  Parquet
                    # serialization (DEC-491) handles nested dicts/lists.
                    signals_at_entry={
                        **cand["signals"],
                        "sector_etf": sector_etf,
                        "sector_etf_return_pct": sector_etf_return,
                        "sector": sector,
                        # BUG-237 RESOLVED-IMPLEMENTED Batch 102 2026-05-12:
                        # tag CNN F&G interpolation staleness on each trade
                        # via days_since_publish from get_fear_and_greed
                        # (DEC-320/391 heuristic: run-length of identical
                        # scores indicates interpolated bridge values vs
                        # actual publication days). Downstream metrics +
                        # agents can downweight trades entered against
                        # heavily-interpolated F&G readings. 0 = fresh
                        # publication; high N = staler interpolation.
                        "cnn_fg_days_since_publish": int(
                            sent.get("fear_greed", {}).get("days_since_publish", 0) or 0
                        ),
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
                # Batch 279: opened_today removed (dedup eliminated per Option 1).
                # open_tickers still updated for BUG-61 cross-day concurrent block.
                open_tickers.add(ticker)  # BUG-61: lock ticker for cross-day

                # BUG-95 sub-batch 2 + 4: mirror entry into Portfolio state.
                # Sub-batch 4 has already gated this with can_open above; reaching
                # here means the gates passed. size_pct was computed up-front for
                # the can_open call; recompute here defensively in case the gate
                # was skipped by hasattr branch.
                if hasattr(self, "portfolio"):
                    size_pct = TIER_POSITION_SIZE_PCT.get(tier, 0.0)
                    # Batch 279: same size-split as the can_open call site upstream.
                    # Without this mirror, can_open would approve SPLIT size but
                    # add_position would record FULL-SIZE - inconsistency bug.
                    if _n_strategies_for_split > 1:
                        size_pct = size_pct / _n_strategies_for_split
                    # DEC-091 wiring (mirror of the can_open call site upstream):
                    # apply DD-band multiplier so add_position uses the same
                    # scaled size that can_open approved. Without this, the
                    # gate would approve a SCALED size but we would open a
                    # FULL-SIZE position -- size inconsistency.
                    size_pct = size_pct * self.portfolio.drawdown_size_multiplier()
                    # DEC-088 wiring (mirror of upstream): also apply vol-target
                    # scale factor so opened size matches gate-approved size.
                    size_pct = size_pct * self.portfolio.vol_target_scale_factor()
                    # DEC-087 wiring (mirror of upstream): per-position vol-
                    # targeted scaling with same ATR-derived proxy.
                    from backtest.engine.portfolio import vol_targeted_size as _vts2
                    import math as _math2
                    if close and close > 0 and atr > 0:
                        _proxy = (atr / close) * _math2.sqrt(252)
                        size_pct = _vts2(size_pct, _proxy)
                    if size_pct > 0:
                        try:
                            self.portfolio.add_position(
                                ticker=ticker, sector=sector, direction=direction,
                                entry_price=entry_price, size_pct=size_pct,
                                entry_date=as_of,
                            )
                        except (ValueError, KeyError) as exc:
                            logger.debug("Portfolio add_position(%s) failed: %s",
                                         ticker, exc)

    # ----------------------------------------------------------------------
    # HELPERS
    # ----------------------------------------------------------------------

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
            # Batch 286 (audit fix): compute today's EMA-9 from prev closes.
            # Required by Batch 285 ma_exit_ema9 exit method. Falls back to None
            # when insufficient history (<9 bars including today).
            ema_9 = None
            try:
                closes_incl_today = pd.concat([
                    prev["close"], pd.Series([float(row["close"])])
                ]) if not prev.empty else pd.Series([float(row["close"])])
                if len(closes_incl_today) >= 9:
                    ema_9 = float(closes_incl_today.ewm(span=9, adjust=False).mean().iloc[-1])
            except Exception:
                ema_9 = None
            bars[ticker] = {
                "open":           float(row["open"]),
                "high":           float(row["high"]),
                "low":            float(row["low"]),
                "close":          float(row["close"]),
                "prev_close":     prev_close,
                "ema_9":          ema_9,   # Batch 286: for ma_exit_ema9 exit method
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
        """Stage 1  -  rule-based preliminary tier before agents run.

        Batch 263 (Class B confluence, owner-approved 2026-05-20):
        Tightened tier thresholds to better differentiate quality.
        Post-1A-alpha forensic showed 1165 of 1181 trades got HIGH tier
        because strategy_count >= 3 was too easy. HIGH now requires >=4
        strategies + VERY_HIGH requires >=3 + smart money confluence.
        """
        sm_sig = sm.get("composite_signal", "none")
        # AVOID  -  strong negative smart money regardless of technical signals
        if sm_sig == "congressional_sell+insider_cluster_sell":
            return "AVOID"
        if sm_sig == "congressional+insider_cluster" and strategy_count >= 4:
            return "EXCEPTIONAL"
        if sm_sig == "congressional_or_insider" and strategy_count >= 3:
            return "VERY_HIGH"
        if strategy_count >= 4:                                    # Batch 263: was >= 3
            return "HIGH"
        if strategy_count >= 3:                                    # Batch 263: was >= 2
            return "MEDIUM_HIGH"
        if strategy_count >= 2:                                    # Batch 263: was sm + count>=1
            return "MEDIUM"
        if sm.get("score", 0) >= 2 and strategy_count >= 1:
            return "LOW"  # Batch 263: was else; now MEDIUM-LOW floor on smart-money-confluence-only
        return "LOW"

    def _adjust_tier_by_agent(self, preliminary_tier: str, agent_score: int) -> str:
        """Stage 2  -  agent score adjusts tier +/-1 level based on quality assessment."""
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
            # BUG-218/239 Batch 116: PIT-correct sector for agent context so
            # agent reasoning sees the as_of sector classification rather
            # than the current-snapshot.
            sector = self._get_sector_pit_for_ticker(ticker, as_of)
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

    # ----------------------------------------------------------------------
    # RESULTS
    # ----------------------------------------------------------------------

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
            logger.warning("No closed trades  -  nothing to write")
            return

        # Apply transaction costs
        if self.apply_costs:
            df_trades = apply_transaction_costs(df_trades, self.info_dict)
            logger.info("Transaction costs applied  -  net ROI = %.1f%%",
                        df_trades["pnl_pct"].sum())

        # Survivorship bias haircut  -  hold-adjusted per trade
        years = (self.end - self.start).days / 365.25
        gross_roi = df_trades["pnl_pct"].sum()
        df_trades, haircut = apply_survivorship_haircut(df_trades, years)
        adj_roi = df_trades["pnl_pct"].sum()
        logger.info("Hold-adjusted survivorship haircut: %.1f%% -> adjusted ROI %.1f%%",
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

        # DEC-155 RESOLVED-IMPLEMENTED Batch 81 2026-05-12 owner-mandated
        # wiring: per-strategy vs-SPY alpha/beta/IR/tracking-error. Builds
        # strategy daily-return series from trade pnl_pct binned by exit_date,
        # SPY daily returns from same window; calls compute_vs_spy_metrics
        # for each strategy and adds 4 new columns to metrics output. Joint
        # DEC-208 multi-metric A/B (telemetry consumer).
        try:
            from backtest.results.metrics import compute_vs_spy_metrics
            if "SPY" in self.cache_index and not df_trades.empty:
                import pandas as _pd
                _spy = self.cache_index["SPY"][
                    self.cache_index["SPY"].index.date >= self.start
                ]
                _spy_daily = _spy["close"].pct_change().dropna()
                _vs_spy_cols = {
                    "alpha_annualized": [], "beta": [],
                    "information_ratio": [], "tracking_error_annualized": [],
                }
                for _strat in metrics["strategy"].tolist():
                    _strat_trades = df_trades[df_trades["strategy"] == _strat]
                    if _strat_trades.empty:
                        for k in _vs_spy_cols:
                            _vs_spy_cols[k].append(None)
                        continue
                    _strat_daily = _strat_trades.groupby("exit_date")["pnl_pct"].sum() / 100.0
                    _strat_daily.index = _pd.to_datetime(_strat_daily.index)
                    _vs = compute_vs_spy_metrics(_strat_daily, _spy_daily)
                    for k in _vs_spy_cols:
                        _vs_spy_cols[k].append(_vs.get(k))
                for k, v in _vs_spy_cols.items():
                    metrics[k] = v
                logger.info("DEC-155 vs-SPY metrics added for %d strategies",
                            len(metrics))
        except Exception as _exc:
            logger.debug("DEC-155 vs-SPY metrics skipped: %s", _exc)

        # Walk-forward validation
        wf_df = pd.DataFrame()
        if self.walk_forward and len(df_trades) >= 20:
            wf_results = run_walk_forward(df_trades)
            wf_df      = walk_forward_to_df(wf_results)

        # Bonferroni info
        # BUG-018 FIX: use len(ALL_STRATEGIES) instead of hardcoded 60; current is 72
        bonferroni = bonferroni_adjusted_threshold(len(ALL_STRATEGIES))
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
            sizing_log=self.sizing_log,
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
            # BUG-95 sub-batch 5: pass Portfolio so writer can emit
            # equity_curve.parquet + portfolio_metrics.json
            portfolio=getattr(self, "portfolio", None),
        )
