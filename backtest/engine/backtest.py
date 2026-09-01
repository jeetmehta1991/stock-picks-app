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
import sys
import time
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
from backtest.config import CUBE_ISOLATION_SIZE_PCT
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
_OFFICER_MOD_WARNED = False  # B2120 one-shot


# Council 233 Bug A fix (2026-07-02): module-level wrapper for pool.imap_unordered.
# Previously defined as closure inside BacktestEngine.save_all_outputs which
# multiprocessing spawn (Windows default) cannot pickle -- silently caused
# cube fan-out to fall back to a broken sequential path (Bug B) producing
# empty trade_exit_detail.csv. Council 231 CHECKLIST #130 EQUAL-count gate
# will now catch this class of bug pre-Batch-B.
def resolve_replay_atr(sig, entry_price: float, counters: dict) -> float:
    """B1261 (Council 303, S6-B1250-ENG2 owner-approved 2026-07-08): resolve
    ATR for cube-replay from signals_at_entry, tallying proxy fallbacks.

    Returns sig['atr'] when present and positive; otherwise the crude
    2pct-of-price proxy, incrementing counters['fallback']. B1250 ENG-1
    made the proxy fire for 100% of Batch A replayed trades silently --
    this helper makes the rate observable (post-loop >5% warning).
    """
    counters["total"] = counters.get("total", 0) + 1
    if isinstance(sig, dict):
        atr_val = sig.get("atr")
        try:
            if atr_val is not None and float(atr_val) > 0:
                return float(atr_val)
        except (TypeError, ValueError):
            pass
    counters["fallback"] = counters.get("fallback", 0) + 1
    return entry_price * 0.02


REPLAY_ATR_FALLBACK_WARN_RATE = 0.05  # B1261: >5% proxy usage = data problem


def emit_replay_atr_fallback_report(counters: dict) -> str:
    """B1261 (S6-B1250-ENG2): format + threshold-classify the ATR-proxy
    fallback rate. Returns the message (caller logs it); WARNING-level
    escalation left to caller when rate exceeds REPLAY_ATR_FALLBACK_WARN_RATE.
    """
    total = counters.get("total", 0)
    fb = counters.get("fallback", 0)
    if total == 0:
        return "replay-ATR: no trades replayed"
    rate = fb / total
    status = "OK" if rate <= REPLAY_ATR_FALLBACK_WARN_RATE else "EXCEEDS-5PCT-THRESHOLD"
    return (f"replay-ATR proxy fallback: {fb}/{total} trades ({rate:.1%}) "
            f"[{status}] (B1261 ENG-2; 100% pre-ENG-1-fix on Batch A)")


def _b1070_starmap_wrapper(args):
    """Module-level unpacker so multiprocessing.Pool.imap_unordered can pickle
    it on Windows spawn. Delegates to _pool_cube_replay_worker with unpacked args."""
    from backtest.engine.exit_strategies import _pool_cube_replay_worker
    return _pool_cube_replay_worker(*args)


class BacktestEngine:

    def __init__(
        self,
        universe:               list  = None,
        start:                  date  = BACKTEST_START,
        end:                    date  = BACKTEST_END,
        phase:                  str   = "phase_1a",
        max_candidates_per_day: int   = 30,  # Batch 314 Cat-5 A: 10 -> 30 (owner 2026-05-24)
        run_agents:             bool  = True,
        output_dir:             str   = OUTPUT_DIR,
        use_cache:              bool  = True,
        apply_costs:            bool  = True,
        apply_slippage_model:   bool  = True,
        walk_forward:           bool  = True,
        disable_news:           bool  = False,
        screen_pool_workers:    int   = 0,    # Batch 322: 0 = disabled (sequential)
        no_portfolio_cap:       bool  = False, # Batch 377 owner 2026-05-26: bypass portfolio cap for Phase 1A-beta cube evaluation. Re-engaged in Phase 1B-alpha.
        no_dd_halt:             bool  = False, # Batch 383 owner 2026-05-26: bypass DEC-515 Level 6 + Portfolio drawdown_suspend halt for Phase 1A-beta cube. Capital-protection gate not applicable to cell-verdict computation. Re-engaged in Phase 1B-alpha.
        no_regime_affinity:     bool  = False, # Batch 384 owner 2026-05-26 Gate 2 opt: bypass Batch 203/293 STRATEGY_REGIME_AFFINITY filter for Phase 1A-beta cube. Cube measures per-regime cell verdicts empirically; let data say which regime works per strategy. Re-engaged Phase 1B-alpha.
        no_event_suppression:   bool  = False, # Batch 384 owner 2026-05-26 Gate 3 opt: bypass DEC-348 event suppression (FOMC/CPI/NFP/earnings) for Phase 1A-beta cube. Cube needs event-day data to measure strategy robustness through events. Re-engaged Phase 1B-alpha.
        warn_run_hours:         Optional[float] = None, # Batch 394 owner 2026-05-27: WARN once when run exceeds this wall-time. None = disabled.
        max_run_hours:          Optional[float] = None, # Batch 394 owner 2026-05-27: hard sys.exit(1) at this wall-time after flushing checkpoint. None = disabled.
        resume_from_checkpoint: Optional[str] = None, # B1076 Council 191 Option 1: local dir with engine_state.json + trade_log_checkpoint.csv from prior interrupted run.
        cube_isolation:         bool  = False, # B1321 Council 353 owner M2=(i): PURE-SIGNAL per-strategy isolation for the cube. Every valid signal opens a trade (PIT + data + same-strategy dedup + strategy-intrinsic gates ONLY). Bypasses ALL cross-strategy PORTFOLIO gates (candidate cap, cross-strategy ticker block, cooldown, max-loss, factor-concentration, can_open, portfolio mirror) so per-(strategy x exit) cube cells are independent of other strategies. Keep OFF for portfolio-sim (BUG-61 shared book).
    ):
        self.resume_from_checkpoint = resume_from_checkpoint
        self.cube_isolation = cube_isolation
        self._resume_sim_day = -1  # set by _load_resume_checkpoint when active
        self._resumed_closed_trades_count = 0  # idempotency check
        self.no_portfolio_cap = bool(no_portfolio_cap)
        self.no_dd_halt = bool(no_dd_halt)
        self.no_regime_affinity = bool(no_regime_affinity)
        self.no_event_suppression = bool(no_event_suppression)
        if self.no_portfolio_cap:
            logger.info(
                "Batch 377: portfolio cap BYPASSED (no_portfolio_cap=True). "
                "Cube evaluation mode - all gate-eligible candidates are "
                "admitted regardless of position count. Re-engage in Phase 1B-alpha."
            )
        if self.no_dd_halt:
            logger.info(
                "Batch 383: DD halt BYPASSED (no_dd_halt=True). DEC-515 Level 6 "
                "halt + Portfolio.can_open drawdown_suspend gate skipped. "
                "Phase 1A-beta cube evaluation only - capital-protection gates "
                "re-engage in Phase 1B-alpha."
            )
        if self.no_regime_affinity:
            logger.info(
                "Batch 384 Gate 2 opt: REGIME AFFINITY BYPASSED (no_regime_affinity=True). "
                "Batch 203/293 STRATEGY_REGIME_AFFINITY filter skipped. Every strategy "
                "evaluated in every regime for empirical cube verdicts. Phase 1B-alpha "
                "re-engages regime affinity per cube outcomes."
            )
        if self.no_event_suppression:
            logger.info(
                "Batch 384 Gate 3 opt: EVENT SUPPRESSION BYPASSED (no_event_suppression=True). "
                "DEC-348 FOMC/CPI/NFP/earnings blackout windows skipped. Cube measures "
                "strategy robustness THROUGH events. Phase 1B-alpha re-engages."
            )
        _user_universe = universe or UNIVERSE
        # Batch 290 (2026-05-20): SPY is system-required for regime
        # classification. Auto-include in universe when not user-supplied so
        # engine has SPY OHLCV regardless of trading universe. Without this,
        # custom --tickers runs had self.spy_df=None -> spy_ema=None ->
        # spy_above_200ema=None -> classify_regime always "neutral" (the
        # Batch 288 SPY-only bear gate became inert silently). Discovered
        # during Stage C v2 smoke - 100% neutral classifications through
        # the 2022 bear despite Batches 288/289 fixes.
        if "SPY" not in _user_universe:
            self.universe = list(_user_universe) + ["SPY"]
        else:
            self.universe = list(_user_universe)
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
        # Batch 322 (2026-05-25): per-ticker process-pool wiring. 0 = sequential
        # (default; preserves pre-Batch-322 behavior). >0 enables parallelization
        # of screen_instrument calls via multiprocessing.Pool with spawn context.
        # Pool is lazy-initialized at the first _process_day call (after
        # ohlcv_dict is populated) and torn down at end of backtest.
        self.screen_pool_workers  = max(0, int(screen_pool_workers or 0))
        self._screen_pool         = None
        # Batch 489 (M9 wire-in): strategy-cluster lookup for
        # correlation-aware effective_strategy_count in _assign_confidence_tier.
        # Default empty -> back-compat: confidence tier uses raw
        # strategy_count exactly as pre-Batch-489. To activate, call
        # `engine.load_strategy_cluster_lookup(<path>)` before run(); the
        # path points at a JSON written by a prior-run scripts utility (not
        # yet shipped -- M1 correlation matrix lives in
        # backtest.results.strategy_correlation; the lookup generator is a
        # follow-on batch).
        self._strategy_cluster_lookup: dict[str, int] = {}
        # Batch 394 (2026-05-27) owner-mandated wall-time guard.
        #   warn_run_hours: log WARN once when exceeded (default None=off)
        #   max_run_hours:  hard sys.exit(1) when exceeded; flushes a final
        #                   checkpoint first so partial cube is salvageable.
        # Engine-side primary kill; external monitor is the watchdog backup.
        self.warn_run_hours = (float(warn_run_hours)
                               if warn_run_hours is not None else None)
        self.max_run_hours  = (float(max_run_hours)
                               if max_run_hours is not None else None)
        self._run_start_time      = None  # set at start of run()
        self._warn_fired          = False
        # B1089 Council 215 Fix 1 owner directive 2026-06-30 "Progress and
        # data to be saved every 30 minutes": time-based checkpoint cadence
        # in addition to sim_day-based (B1081 PIVOT #44 fix). Paired-writer
        # block at backtest.py:838+873 fires on EITHER trigger; timestamp
        # resets ONLY after both writers succeed (atomic-pair semantics per
        # Council 214). 1800s = 30 min per owner.
        import time as _time_init
        self._last_checkpoint_time = _time_init.time()
        self._checkpoint_interval_seconds = 1800  # 30 min per owner B1089
        # Batch 394: year-boundary detector; set in day loop.
        self._last_seen_year      = None
        # Batch 394: 100-day milestone telemetry baseline for per-100d
        # delta logging.
        self._last_milestone_trades = 0
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
    # B1076 RESUME-FROM-CHECKPOINT (Council 191 Option 1 MVP)
    # S6-B2213a: _csv_row_to_open_trade - the OPEN-book half of the resume
    # contract. Deliberately TYPE-DISPATCHED off the dataclass rather than
    # hand-enumerated like its closed-trade sibling: OpenTrade has 34 fields,
    # a hand list goes stale the first time one is added, and L620/B2092 is
    # exactly that failure (a payload's arity is a contract with every
    # consumer). Dispatching means a new field is handled unwritten.
    # ----------------------------------------------------------------------

    def _flush_open_trades_checkpoint(self, out_dir):
        """S6-B2213a: write open_trades_checkpoint.csv beside the closed one.

        Called from ALL THREE checkpoint sites (periodic, wall-time kill, final
        flush) rather than one - L620/B2092: a payload's contract binds every
        writer, and a fix through one path proves one path. Uses the
        signals_serde contract for dict/list fields, matching the periodic
        closed-trade writer's post-B1260 form rather than the older raw vars().
        Atomic via .tmp + replace, matching B1046 F-11.
        """
        import os as _os
        from pathlib import Path as _P

        import pandas as _pd

        from backtest.util.signals_serde import dumps_signals as _dumps

        d = _P(out_dir)
        path = d / "open_trades_checkpoint.csv"
        tmp = d / "open_trades_checkpoint.csv.tmp"
        rows = []
        for t in (self.open_trades or []):
            r = dict(vars(t))
            for k, v in r.items():
                if isinstance(v, (dict, list)):
                    r[k] = _dumps(v)
            rows.append(r)
        if not rows:
            # An EMPTY book is a MEASURED fact and must be distinguishable from
            # "never written" (L580: a missing measurement and a measured zero
            # are different facts). Write the header-only file.
            from backtest.engine.exit_manager import OpenTrade as _OT
            from dataclasses import fields as _f
            _pd.DataFrame(columns=[x.name for x in _f(_OT)]).to_csv(tmp, index=False)
        else:
            _pd.DataFrame(rows).to_csv(tmp, index=False)
        _os.replace(tmp, path)

    @staticmethod
    def _csv_row_to_open_trade(row: dict) -> "OpenTrade":
        """Reconstruct an OpenTrade from a checkpoint CSV row.

        Mirrors _csv_row_to_closed_trade's coercion inverse (B1079 PIVOT #43)
        and reuses the same signals_serde contract for nested fields (B1260),
        which is where this class of round trip silently loses data. Missing
        columns fall back to the dataclass default, so a schema addition is
        forward-compatible rather than a KeyError.
        """
        import math as _math
        from dataclasses import MISSING as _MISSING, fields as _fields
        from datetime import date as _date

        from backtest.engine.exit_manager import OpenTrade as _OT
        from backtest.util.signals_serde import loads_signals as _loads

        def _nan(v):
            try:
                return isinstance(v, float) and _math.isnan(v)
            except Exception:
                return False

        def _default(f):
            if f.default is not _MISSING:
                return f.default
            if f.default_factory is not _MISSING:      # type: ignore[misc]
                return f.default_factory()             # type: ignore[misc]
            return None

        kwargs = {}
        for f in _fields(_OT):
            raw = row.get(f.name, _MISSING)
            dflt = _default(f)
            if raw is _MISSING or raw is None or _nan(raw):
                kwargs[f.name] = dflt
                continue
            ann = str(f.type)
            try:
                if "dict" in ann.lower() or "list" in ann.lower():
                    kwargs[f.name] = _loads(raw, dflt if dflt is not None
                                            else ({} if "dict" in ann.lower() else []))
                elif "date" in ann.lower():
                    kwargs[f.name] = (raw if isinstance(raw, _date)
                                      else _date.fromisoformat(str(raw).split(" ")[0]))
                elif "bool" in ann.lower():
                    kwargs[f.name] = (raw if isinstance(raw, bool)
                                      else str(raw).strip().lower() in ("true", "1", "yes"))
                elif "int" in ann.lower():
                    kwargs[f.name] = int(float(raw))
                elif "float" in ann.lower():
                    kwargs[f.name] = float(raw)
                else:
                    kwargs[f.name] = str(raw)
            except (TypeError, ValueError):
                kwargs[f.name] = dflt
        return _OT(**kwargs)

    # B1079 PIVOT #43 fix (Council 196 Option 4): _csv_row_to_closed_trade
    # ----------------------------------------------------------------------

    @staticmethod
    def _csv_row_to_closed_trade(row: dict) -> "ClosedTrade":
        """B1079 PIVOT #43 fix (Council 196 Option 4): reconstruct
        ClosedTrade dataclass instance from CSV row dict.

        Root cause: B1076 reloaded closed_trades via df.to_dict(records)
        producing plain dicts. Engine consumes self.closed_trades as
        ClosedTrade instances at line 1583 (ct.ticker access for DEC-088
        stopout cooldown filter) and line 2615 (asdict for get_trade_log).

        CSV serialization via vars(t) preserves field names but coerces:
          date -> str like '2023-07-15'
          dict -> str like \"{'key': 'val'}\" (python repr, NOT JSON)
          list -> str like \"['a', 'b']\"
          NaN for missing optionals

        This helper inverts that coercion per ClosedTrade dataclass spec
        (backtest/engine/exit_manager.py:100-173). Missing columns -> field
        defaults (forward-compat for schema additions).
        """
        import ast
        from datetime import date as _date
        from dataclasses import fields as _fields
        import math as _math

        def _is_nan(v):
            try:
                return isinstance(v, float) and _math.isnan(v)
            except Exception:
                return False

        def _parse_date(v):
            if v is None or _is_nan(v):
                return None
            if isinstance(v, _date):
                return v
            return _date.fromisoformat(str(v).split(" ")[0])

        def _parse_literal(v, default):
            # B1260 (Council 303, S6-B1250-ENG1 owner-approved): delegate to
            # the signals_serde writer-reader contract. Pre-B1260 this used
            # bare ast.literal_eval, which parses NEITHER the checkpoint's
            # numpy reprs NOR writer.py's JSON booleans -> silent {} default
            # wiped signals_at_entry on every resume (B1250 ENG-1 VERIFIED).
            if v is None or _is_nan(v):
                return default
            from backtest.util.signals_serde import loads_signals
            return loads_signals(v, default)

        def _parse_bool(v):
            if isinstance(v, bool):
                return v
            if _is_nan(v):
                return False
            return str(v).strip().lower() in ("true", "1", "yes")

        def _parse_int(v, default):
            if v is None or _is_nan(v):
                return default
            try:
                return int(float(v))
            except (ValueError, TypeError):
                return default

        def _parse_float(v, default):
            if v is None or _is_nan(v):
                return default
            try:
                return float(v)
            except (ValueError, TypeError):
                return default

        def _parse_str(v, default):
            if v is None or _is_nan(v):
                return default
            return str(v)

        def _parse_optional(v):
            if v is None or _is_nan(v) or (isinstance(v, str) and v.strip() == ""):
                return None
            return v

        # Build kwargs honoring ClosedTrade field types + defaults
        kwargs = {
            "ticker": _parse_str(row.get("ticker"), ""),
            "entry_date": _parse_date(row.get("entry_date")),
            "exit_date": _parse_date(row.get("exit_date")),
            "direction": _parse_str(row.get("direction"), "long"),
            "strategy": _parse_str(row.get("strategy"), ""),
            "category": _parse_str(row.get("category"), ""),
            "sector": _parse_str(row.get("sector"), ""),
            "confidence_tier": _parse_str(row.get("confidence_tier"), "MEDIUM"),
            "regime": _parse_str(row.get("regime"), "neutral"),
            "exit_reason": _parse_str(row.get("exit_reason"), ""),
            "entry_price": _parse_float(row.get("entry_price"), 0.0),
            "exit_price": _parse_float(row.get("exit_price"), 0.0),
            "initial_stop": _parse_float(row.get("initial_stop"), 0.0),
            "highest_close": _parse_float(row.get("highest_close"), 0.0),
            "trailing_stop_at_exit": _parse_float(row.get("trailing_stop_at_exit"), 0.0),
            "pnl_pct": _parse_float(row.get("pnl_pct"), 0.0),
            "pnl_dollar": _parse_float(row.get("pnl_dollar"), 0.0),
            "win": _parse_bool(row.get("win")),
            "hold_days": _parse_int(row.get("hold_days"), 0),
            "max_adverse_excursion": _parse_float(row.get("max_adverse_excursion"), 0.0),
            "max_favourable_excursion": _parse_float(row.get("max_favourable_excursion"), 0.0),
            "signals_at_entry": _parse_literal(row.get("signals_at_entry"), {}),
            "context_bullets": _parse_literal(row.get("context_bullets"), []),
            "context_paragraph": _parse_str(row.get("context_paragraph"), ""),
            "fail_reason": _parse_str(row.get("fail_reason"), ""),
            "smart_money_score": _parse_int(row.get("smart_money_score"), 0),
            "macro_score": _parse_int(row.get("macro_score"), 0),
            "sentiment_score": _parse_int(row.get("sentiment_score"), 0),
            "conversion_pair_id": _parse_optional(row.get("conversion_pair_id")),
            "circuit_breaker_level": (_parse_int(row.get("circuit_breaker_level"), None)
                                      if not _is_nan(row.get("circuit_breaker_level")) and row.get("circuit_breaker_level") is not None
                                      else None),
            "days_to_earnings": (_parse_int(row.get("days_to_earnings"), None)
                                 if not _is_nan(row.get("days_to_earnings")) and row.get("days_to_earnings") is not None
                                 else None),
            "preliminary_tier": _parse_str(row.get("preliminary_tier"), "MEDIUM"),
            "agent_reasoning": _parse_literal(row.get("agent_reasoning"), {}),
            "congressional_signal": _parse_str(row.get("congressional_signal"), "none"),
            "insider_signal": _parse_str(row.get("insider_signal"), "none"),
            "institutional_signal": _parse_str(row.get("institutional_signal"), "none"),
            "aaii_bullish": _parse_float(row.get("aaii_bullish"), 0.0),
            "aaii_bearish": _parse_float(row.get("aaii_bearish"), 0.0),
            "aaii_signal": _parse_str(row.get("aaii_signal"), "neutral"),
            "cnn_fg_score": _parse_float(row.get("cnn_fg_score"), 50.0),
            "cnn_fg_label": _parse_str(row.get("cnn_fg_label"), "Neutral"),
            "trade_id": _parse_optional(row.get("trade_id")),
            "exit_method": _parse_str(row.get("exit_method"), "trailing_stop"),
        }
        # Filter kwargs to only valid ClosedTrade fields (forward-compat
        # if CSV has extra columns from older schema)
        valid_fields = {f.name for f in _fields(ClosedTrade)}
        kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}
        return ClosedTrade(**kwargs)

    @staticmethod
    def suspension_seconds(gap_s: float, interval_s: float) -> float:
        """S6-B2490: suspended seconds implied by a heartbeat gap, else 0.0.

        A watchdog thread cannot observe a machine suspend while it happens -
        it is frozen too. It can only see the HOLE afterwards. A gap far
        larger than the sampling interval means wall-clock advanced while
        nothing computed, which is what silently converted ~32 s of real work
        into a reported 15.3 h and got a healthy run killed at the cap.

        THE FLOOR'S REAL REACH, measured at the live interval (S6-B2495).
        interval=30 s gives threshold=150 s, so:
          gap 150 s -> 0.0 credited   (counted as work)
          gap 180 s -> 150.0 credited (FORGIVEN)
        This function CANNOT distinguish a sleeping machine from a stall
        longer than 2.5 minutes - a slow disk, a swap storm, a long GC. An
        earlier version of this docstring claimed "a slow disk never
        registers as a suspend"; that is true of JITTER and false of a
        genuine stall, and the difference matters because credited seconds
        are seconds a cap will not count. That ambiguity is why S6-B2490
        shipped REPORTING ONLY at first, and why the CAP now reads a
        SEPARATE, stricter accumulator: sleep_credit_seconds credits only
        gaps >= 30 min (unambiguous machine sleep), so a stall this
        function reports is never a stall the cap forgives. S6-B2491
        (owner go 2026-09-01) gates the kill on active hours computed from
        that credit, via kill_decision(), which both gating sites call.
        """
        if gap_s <= 0 or interval_s <= 0:
            return 0.0
        threshold = max(5.0 * interval_s, 120.0)
        return (gap_s - interval_s) if gap_s > threshold else 0.0

    # S6-B2502b: only a gap at least this long earns CAP credit. A disk
    # stall, swap storm or GC pause lasts minutes; a machine suspend lasts
    # tens of minutes to hours. Gaps between the reporting threshold
    # (max(5x interval, 120 s)) and this floor are AMBIGUOUS and count as
    # WORK - the conservative direction (they can only shorten a run's
    # budget, never extend it).
    SLEEP_CREDIT_MIN_S = 1800.0

    @staticmethod
    def sleep_credit_seconds(gap_s: float, interval_s: float) -> float:
        """S6-B2502b: cap credit implied by one heartbeat gap, else 0.0.

        DISTINCT FROM suspension_seconds, deliberately (L728 - one field
        must not carry two questions): suspension_seconds answers the
        REPORTING question (how long was the machine not computing, floor
        2.5 min) and this answers the CAP question (how much of that is
        unambiguous machine sleep, floor 30 min). A 3-minute disk stall is
        reported as suspension and earns NO cap credit.
        """
        if gap_s <= 0 or interval_s <= 0:
            return 0.0
        if gap_s < BacktestEngine.SLEEP_CREDIT_MIN_S:
            return 0.0
        return gap_s - interval_s

    @staticmethod
    def kill_decision(elapsed_h, sleep_credit_h, max_run_hours):
        """S6-B2491/B2502b: what the run-hours cap measures, decided ONCE.

        Returns None (keep running) or "active_cap".

        OWNER RULING IMPLEMENTED (2026-09-01, "address and implement all
        open tickets" over the twice-presented S6-B2491 recommendation):
        the cap gates on ACTIVE hours - wall-clock minus CREDITED machine
        sleep - because cfg1 was killed at 16.10 h wall of which 15.32 h
        was the laptop asleep and 0.78 h was compute (L731).

        DESIGN CORRECTION, FOUND BY THIS FUNCTION'S OWN BOUNDARY MATRIX
        BEFORE ANY RUN: the recommendation carried a wall-clock backstop
        at 3x the cap to bound detector forgiveness (L733) - and the
        matrix showed f(16.10, 15.32, 4.0) trips a 12 h backstop, so the
        backstop KILLS THE MOTIVATING INCIDENT: any overnight sleep
        exceeds 3x a sane cap. The forgiveness bound therefore moved to
        the GAP: only gaps >= SLEEP_CREDIT_MIN_S (30 min) earn credit,
        which a stall physically cannot reach, so no wall ceiling is
        needed and none exists.

        FAIL DIRECTION IS CONSERVATIVE: with no credit accrued (supervisor
        dead, or only short gaps), active == elapsed and this reduces
        exactly to the old wall-clock kill. Both gating sites - the
        supervisor thread and the in-loop cap - call THIS function (L732).
        """
        if max_run_hours is None or elapsed_h is None:
            return None
        credit_h = max(0.0, float(sleep_credit_h or 0.0))
        active_h = max(0.0, float(elapsed_h) - credit_h)
        if active_h >= float(max_run_hours):
            return "active_cap"
        return None

    def _start_run_supervisor(self) -> None:
        """B2148 (S6-B2143a/b, L637): a watchdog that shares NO control flow
        with the day loop.

        THE DEFECT IT CLOSES, measured: a 2.5h cap ran to 2.9h with no kill,
        no warn and no checkpoint, because every guard and every writer in
        this engine is evaluated at the top of a sim-day iteration - seven of
        them - and one long iteration silences all seven at once. Even the
        30-minute checkpoint trigger, added so progress would survive, is
        read once per simulated day.

        This thread samples wall-clock on its own schedule. It writes a
        HEARTBEAT every interval so any session (or none) can read progress
        from disk, and it hard-exits when max_run_hours is exceeded no matter
        where the main loop is. Daemon=True so it can never hold the process
        open.
        """
        import json as _sj
        import os as _so
        import threading as _st
        import time as _stime

        if self.max_run_hours is None and not self.output_dir:
            return
        interval = float(getattr(self, "supervisor_interval_s", 30.0))
        hb_path = Path(self.output_dir) / "run_heartbeat.json"

        def _supervise() -> None:
            # S6-B2490: a beat gap far larger than the interval means the
            # MACHINE was suspended - every thread frozen, nothing computed.
            # This thread cannot observe a suspend while it happens; it can
            # only see the hole afterwards, which is enough.
            _last_beat = _stime.time()
            while True:
                _stime.sleep(interval)
                _now = _stime.time()
                _gap = _now - _last_beat
                _susp = self.suspension_seconds(_gap, interval)
                if _susp > 0.0:
                    self._suspended_seconds = (
                        getattr(self, "_suspended_seconds", 0.0) + _susp)
                    # S6-B2502b: the CAP credit is a separate, stricter
                    # accumulator - only unambiguous sleep (>= 30 min gap)
                    # buys a run time back; a stall is reported above and
                    # credited nothing.
                    _cr = self.sleep_credit_seconds(_gap, interval)
                    if _cr > 0.0:
                        self._sleep_credit_seconds = (
                            getattr(self, "_sleep_credit_seconds", 0.0) + _cr)
                    logger.warning(
                        "B2490 SUSPENSION DETECTED: %.0fs gap between beats "
                        "(interval=%.0fs). The machine slept; no compute "
                        "happened. Cumulative suspended=%.2fh. Wall-clock "
                        "elapsed OVERSTATES work by that much, and the "
                        "wall-clock cap is still what kills this run.",
                        _gap, interval,
                        self._suspended_seconds / 3600.0,
                    )
                _last_beat = _now
                try:
                    elapsed_h = ((_stime.time() - self._run_start_time) / 3600.0
                                 if self._run_start_time else 0.0)
                    _susp_h = getattr(self, "_suspended_seconds", 0.0) / 3600.0
                    _cred_h = getattr(self, "_sleep_credit_seconds", 0.0) / 3600.0
                    beat = {
                        "elapsed_hours": round(elapsed_h, 4),
                        "suspended_hours": round(_susp_h, 4),
                        "sleep_credit_hours": round(_cred_h, 4),
                        "active_hours": round(max(0.0, elapsed_h - _cred_h), 4),
                        "sim_day_index": getattr(self, "_last_sim_day_index", -1),
                        "sim_date": str(getattr(self, "_last_sim_date", "")),
                        "closed_trades": len(self.closed_trades),
                        "open_trades": len(self.open_trades),
                        "max_run_hours": self.max_run_hours,
                        "pid": _so.getpid(),
                        "timestamp": _stime.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                     _stime.gmtime()),
                        "source": "supervisor_thread",
                    }
                    tmp = hb_path.with_suffix(".json.tmp")
                    tmp.write_text(_sj.dumps(beat, indent=1))
                    _so.replace(tmp, hb_path)
                except Exception as _hb_exc:      # never kill the watchdog
                    logger.warning("B2148 heartbeat write failed: %r", _hb_exc)
                try:
                    _el = ((_stime.time() - self._run_start_time) / 3600.0
                           if self._run_start_time else None)
                    _sh = getattr(self, "_suspended_seconds", 0.0) / 3600.0
                    _cr_h = getattr(self, "_sleep_credit_seconds", 0.0) / 3600.0
                    _why = self.kill_decision(_el, _cr_h, self.max_run_hours)
                    if _why:
                        logger.error(
                            "B2148 SUPERVISOR KILL [%s]: elapsed=%.2fh "
                            "(suspended=%.2fh active=%.2fh sleep_credit=%.2fh) "
                            "cap=%sh. S6-B2491 IMPLEMENTED: the cap gates on "
                            "ACTIVE hours = elapsed minus CREDITED sleep "
                            "(gaps >= 30 min only - a stall earns nothing). "
                            "Flushing state and hard-exiting.",
                            _why, _el, _sh, max(0.0, _el - _cr_h), _cr_h,
                            self.max_run_hours,
                        )
                        self._emit_kill_state("supervisor_%s" % _why)
                        _so._exit(1)
                except Exception as _k_exc:
                    logger.error("B2148 supervisor kill path failed: %r", _k_exc)

        # S6-B2490: block IDLE sleep for the life of this process. This does
        # NOT cover an explicit user/API suspend (measured: Event 187
        # SetSuspendState is what took cfg1 down, with idle-sleep already
        # disabled at powercfg "Sleep after"=0), so it closes a SIBLING
        # class, not the observed one.
        try:
            if _so.name == "nt":
                import ctypes as _ct
                _ES = 0x80000000 | 0x00000001 | 0x00000040  # CONT|SYS|AWAY
                if _ct.windll.kernel32.SetThreadExecutionState(_ES):
                    logger.info("B2490 idle-sleep blocked for this process "
                                "(explicit user suspend is NOT covered)")
        except Exception as _es_exc:
            logger.warning("B2490 could not block idle sleep: %r", _es_exc)

        t = _st.Thread(target=_supervise, name="b2148_run_supervisor",
                       daemon=True)
        t.start()
        self._supervisor_thread = t
        logger.info(
            "B2148 supervisor armed: interval=%.0fs cap=%s heartbeat=%s "
            "(shares no control flow with the day loop)",
            interval, self.max_run_hours, hb_path,
        )

    def _emit_kill_state(self, status: str) -> None:
        """Write engine_state.json from OUTSIDE the day loop (B2148).

        The in-loop writers cannot run when an iteration is long; this one is
        callable from the supervisor thread at any moment.
        """
        import json as _ej
        import os as _eo
        import time as _et
        try:
            # S6-B2387: build the portfolio block DEFENSIVELY. The whole flush is
            # wrapped in `except Exception`, so anything raising here silently
            # disables checkpointing - which a first cut of this did, caught by
            # test_b2148. self.portfolio may not exist when the supervisor thread
            # fires, and getattr(self.portfolio, ...) guards only the INNER
            # attribute while the outer access still raises.
            _pf_obj = getattr(self, "portfolio", None)
            _pf_block = None
            if _pf_obj is not None:
                try:
                    _pf_block = {
                        "starting_capital": getattr(_pf_obj, "starting_capital", None),
                        "cash": getattr(_pf_obj, "cash", None),
                        "positions": [
                            {"ticker": p.ticker, "sector": p.sector,
                             "direction": p.direction,
                             "entry_date": str(p.entry_date),
                             "entry_price": p.entry_price, "shares": p.shares,
                             "last_mark": p.last_mark}
                            for p in getattr(_pf_obj, "positions", {}).values()]}
                except Exception as _pexc:
                    logger.error("S6-B2387: portfolio block NOT serialised (%r) - "
                                 "the rest of the checkpoint still writes, but this "
                                 "resume will restart portfolio accounting", _pexc)
            state = {
                "simulated_day": getattr(self, "_last_sim_day_index", -1),
                "cells_completed": len(self.closed_trades),
                "status": status,
                "sim_date": str(getattr(self, "_last_sim_date", "")),
                "sim_day_index": getattr(self, "_last_sim_day_index", -1),
                "tickers_processed": len(getattr(self, "liquid_universe", []) or []),
                "trades_so_far": len(self.closed_trades),
                "open_trades": len(self.open_trades),
                "timestamp": _et.strftime("%Y-%m-%dT%H:%M:%SZ", _et.gmtime()),
                "pid": _eo.getpid(),
                # S6-B2387: portfolio cash and positions were NEVER checkpointed, so
                # every resume silently reset them to starting_capital with an empty
                # book. Position carries `shares`, so the Portfolio can serialise
                # itself - no OpenTrade schema change is needed.
                "portfolio": _pf_block,
            }
            d = Path(self.output_dir)
            tmp, final = d / "engine_state.json.tmp", d / "engine_state.json"
            tmp.write_text(_ej.dumps(state, indent=2))
            _eo.replace(tmp, final)
            if self.closed_trades:
                import pandas as _epd
                _epd.DataFrame([vars(t) for t in self.closed_trades]).to_csv(
                    d / "trade_log_checkpoint.csv", index=False)
            self._flush_open_trades_checkpoint(d)   # S6-B2213a
            logger.error("B2148 %s state flushed: day=%s trades=%d",
                         status, state["sim_day_index"], state["trades_so_far"])
        except Exception as _exc:
            logger.error("B2148 kill-state flush FAILED: %r - this run is NOT "
                         "resumable", _exc)

    def _load_resume_checkpoint(self):
        """B1076 Council 191 Option 1: load engine_state.json +
        trade_log_checkpoint.csv from self.resume_from_checkpoint dir.

        Sets:
          self._resume_sim_day = engine_state["simulated_day"] - 1 (so
            main loop skips iterations i <= resume_sim_day; resumes at
            resume_sim_day + 1 which == simulated_day in the prior run)
          self._resumed_closed_trades_count = engine_state["trades_so_far"]

        Per CHECKLIST #124 + #128 schema-contract: HALT on:
          - missing engine_state.json
          - engine_state["status"] == "complete" (nothing to resume)
          - engine_state["simulated_day"] <= 0
          - trade_log_checkpoint.csv row count != trades_so_far (B1062
            schema-contract per PIVOT #37 lineage)

        Open trades at interruption point are DROPPED with WARNING
        (acknowledged caveat; B1075 had 0 open at interruption per
        engine_state.json).
        """
        import json
        from pathlib import Path
        resume_dir = Path(self.resume_from_checkpoint)
        state_path = resume_dir / "engine_state.json"
        log_path = resume_dir / "trade_log_checkpoint.csv"
        if not state_path.exists():
            raise FileNotFoundError(
                f"B1076 resume: engine_state.json not found at {state_path}"
            )
        with open(state_path) as f:
            state = json.load(f)
        if state.get("status") == "complete":
            raise ValueError(
                "B1076 resume: prior run status=complete; nothing to resume. "
                "Remove --resume-from-checkpoint flag for fresh run."
            )
        # S6-B2387: restore portfolio cash + open positions. Absent block means
        # a pre-B2387 checkpoint; leave the fresh Portfolio and say so, rather
        # than silently resuming with reset accounting.
        _pf = state.get("portfolio")
        if _pf:
            from backtest.engine.portfolio import Position as _Pos
            from datetime import date as _d
            self.portfolio.cash = float(_pf["cash"])
            self.portfolio.positions = {}
            for _p in _pf.get("positions", []):
                _ed = _p["entry_date"]
                try:
                    _ed = _d.fromisoformat(str(_ed)[:10])
                except ValueError:
                    logger.warning("S6-B2387 resume: position %s has an "
                                   "unparseable entry_date %r - kept as-is",
                                   _p.get("ticker"), _p.get("entry_date"))
                self.portfolio.positions[_p["ticker"]] = _Pos(
                    ticker=_p["ticker"], sector=_p["sector"],
                    direction=_p["direction"], entry_date=_ed,
                    entry_price=float(_p["entry_price"]),
                    shares=float(_p["shares"]),
                    last_mark=float(_p["last_mark"]))
            logger.info("S6-B2387 resume: portfolio restored cash=%.2f "
                        "positions=%d", self.portfolio.cash,
                        len(self.portfolio.positions))
        else:
            logger.warning("S6-B2387 resume: checkpoint carries NO portfolio "
                           "block (pre-B2387); cash and positions stay at their "
                           "starting values - portfolio accounting for this run "
                           "is NOT continuous across the resume")
        resume_sim_day = int(state.get("simulated_day", 0))
        trades_so_far = int(state.get("trades_so_far", 0))
        if resume_sim_day <= 0:
            raise ValueError(
                f"B1076 resume: simulated_day={resume_sim_day} invalid; "
                f"engine never advanced past day 0"
            )
        # Reload closed trades from CSV
        if log_path.exists() and log_path.stat().st_size > 0:
            try:
                df = pd.read_csv(log_path)
                # B1062 PIVOT #37 schema-contract: row count must match
                # engine_state.trades_so_far. Mismatch indicates checkpoint
                # corruption or torn write.
                csv_rows = len(df)
                if csv_rows != trades_so_far:
                    raise ValueError(
                        f"B1076 resume schema-contract: trade_log "
                        f"row_count={csv_rows} != engine_state.trades_so_far"
                        f"={trades_so_far}; HALT per CHECKLIST #124+#128"
                    )
                # Reconstitute closed_trades list as ClosedTrade dataclass
                # instances (B1079 PIVOT #43 fix Council 196 Option 4).
                # Engine consumes closed_trades as dataclass at line 1583
                # (ct.ticker DEC-088 cooldown) + line 2615 (asdict for
                # get_trade_log). Plain dicts from df.to_dict crash both
                # sites - see B1078 i-04d34fc49dc27a5f4 PHASE_2_FAIL.
                self.closed_trades = [
                    self._csv_row_to_closed_trade(r)
                    for r in df.to_dict(orient="records")
                ]
            except pd.errors.EmptyDataError:
                if trades_so_far > 0:
                    raise ValueError(
                        f"B1076 resume: trade_log_checkpoint.csv empty but "
                        f"engine_state.trades_so_far={trades_so_far}; HALT"
                    )
                self.closed_trades = []
        else:
            if trades_so_far > 0:
                raise FileNotFoundError(
                    f"B1076 resume: trade_log_checkpoint.csv missing at "
                    f"{log_path} but engine_state.trades_so_far={trades_so_far}"
                )
            self.closed_trades = []
        # Set resume marker; main loop skips i <= self._resume_sim_day.
        # Prior run last completed simulated_day == N; resume at N+1.
        # Engine writes simulated_day = self._last_sim_day_index (0-indexed
        # iteration count). To skip the FIRST N iterations: skip i < N.
        # Equivalently: continue if i <= self._resume_sim_day where
        # self._resume_sim_day = N - 1.
        self._resume_sim_day = resume_sim_day  # skip i <= this index
        self._resumed_closed_trades_count = trades_so_far
        # S6-B2213a: RESTORE the open book. Pre-B2213a this logged
        # "open-trades DROPPED" and continued with a fresh portfolio - a
        # silent correctness loss dressed as a warning (L641: a record that
        # only reports the success path says nothing about the endings that
        # matter). The engine now restores, or HALTS. Never partial.
        open_at_resume = int(state.get("open_trades", 0))
        open_path = resume_dir / "open_trades_checkpoint.csv"
        if open_at_resume > 0 and not open_path.exists():
            raise RuntimeError(
                f"S6-B2213a RESUME HALT: engine_state.json declares "
                f"open_trades={open_at_resume} but {open_path} is absent. "
                f"That checkpoint predates the open-book writer, so the book "
                f"CANNOT be restored and continuing would silently trade a "
                f"partial portfolio. Re-run from scratch, or resume from a "
                f"checkpoint written by this engine version."
            )
        if open_path.exists():
            import pandas as _opd
            _odf = _opd.read_csv(open_path)
            restored = [self._csv_row_to_open_trade(r)
                        for r in _odf.to_dict("records")]
            if len(restored) != open_at_resume:
                raise RuntimeError(
                    f"S6-B2213a RESUME HALT: open-book count mismatch - "
                    f"engine_state.json says {open_at_resume}, "
                    f"{open_path.name} holds {len(restored)}. A partial book "
                    f"is a correctness defect, not a warning."
                )
            self.open_trades = restored
            # SCOPE BOUNDARY, measured rather than assumed. The design said
            # "open positions are the entire missing state". THEY ARE NOT:
            # self.portfolio is constructed fresh in __init__ and never
            # restored, so cash and positions reset - and OpenTrade carries NO
            # size field, so portfolio.add_position(ticker, sector, direction,
            # entry_price, size_pct, entry_date) cannot be reconstructed from
            # the open book alone. Restoring open_trades is therefore CORRECT
            # AND SUFFICIENT for the EXIT path (exit logic reads OpenTrade
            # fields only) and for cube runs, where cube_isolation bypasses all
            # portfolio gates by design. It does NOT restore portfolio
            # ACCOUNTING, which matters for portfolio-sim; ticketed separately.
            # An earlier draft called a non-existent self.position_sizer inside
            # a bare try/except, which would have swallowed an AttributeError
            # on every resume and reported success - CHECKLIST #122 exactly.
            logger.info(
                "S6-B2213a RESUME: restored %d open position(s) at "
                "resume_sim_day=%d (exit path only; portfolio accounting is "
                "NOT restored - see S6-B2387)", len(restored), resume_sim_day)
        logger.info(
            "B1076 RESUME: resume_sim_day=%d closed_trades=%d (from %s)",
            resume_sim_day, trades_so_far, resume_dir,
        )

    # ----------------------------------------------------------------------
    # MAIN LOOP
    # ----------------------------------------------------------------------

    def run(self):
        if not self.ohlcv_dict:
            self.load_data()

        # Batch 555 OPT-C Phase 4 wire-in: prime the SMC primitive
        # panel-cache from the FULL per-ticker OHLCV once per session
        # (before per-day iteration). compute_smc_signals will read the
        # 6 SMC primitives (FVG/swings/OB/BOS_CHOCH/liquidity/retracements)
        # from cache, sliced respecting PIT lookahead, instead of running
        # the vendored smartmoneyconcepts library per (ticker, as_of)
        # call. Gated by USE_SMC_PANEL_CACHE config flag.
        try:
            from backtest.config import USE_SMC_PANEL_CACHE
        except Exception:
            USE_SMC_PANEL_CACHE = False
        if USE_SMC_PANEL_CACHE:
            try:
                from backtest.signals.smc_panel_cache import (
                    prime_ticker_primitives,
                )
                primed = 0
                for t, full_df in self.ohlcv_dict.items():
                    if full_df is None or full_df.empty:
                        continue
                    prime_ticker_primitives(t, full_df, swing_length=20)
                    primed += 1
                logger.info(
                    "B555 OPT-C SMC panel-cache primed for %d tickers",
                    primed,
                )
            except Exception as exc:
                logger.warning(
                    "B555 OPT-C SMC panel-cache prime failed: %s", exc,
                )

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

        # Batch 394 (2026-05-27): wall-time tracking.  Recorded once at
        # run() start; checked every 20 days alongside progress log.
        self._run_start_time = time.time()
        if self.warn_run_hours is not None or self.max_run_hours is not None:
            logger.info(
                "Batch 394 wall-time guard: warn_run_hours=%s "
                "max_run_hours=%s (engine-side primary kill; monitor is "
                "watchdog backup)", self.warn_run_hours, self.max_run_hours,
            )

        # B1076 Council 191 Option 1 (MVP): resume-from-checkpoint hydration.
        # Sub-B F-13.1 + S5-B1073-RESUME-FROM-CHECKPOINT ticket. Loaded
        # state: sim_day_index + closed_trades_count from prior interrupted
        # run. Main loop skips iterations where i <= self._resume_sim_day.
        # Open trades at interruption point are DROPPED (acknowledged
        # caveat; documented in CLI help). HALT on schema mismatch.
        if self.resume_from_checkpoint:
            self._load_resume_checkpoint()

        # B2148: arm the out-of-loop supervisor BEFORE the
        # first iteration, so a pathological day 0 is still bounded.
        self._start_run_supervisor()

        for i, as_of in enumerate(trading_days):
            # B1076 Council 191 Option 1: skip iterations already completed
            # by prior interrupted run. Continue from sim_day = resume + 1.
            if self._resume_sim_day >= 0 and i <= self._resume_sim_day:
                continue
            # Batch 394: year-boundary milestone telemetry.  Detect when
            # calendar year flips between consecutive trading days.
            cur_year = as_of.year if hasattr(as_of, "year") else None
            if cur_year is not None and self._last_seen_year is not None \
                    and cur_year != self._last_seen_year:
                self._emit_milestone_telemetry(
                    "YEAR", year_closed=self._last_seen_year,
                )
            if cur_year is not None:
                self._last_seen_year = cur_year

            # Batch 394: 100-day milestone telemetry.  Same cadence as
            # the checkpoint so monitor can correlate the two.
            if i > 0 and i % 100 == 0:
                self._emit_milestone_telemetry(
                    "100D", day_idx=i, total_days=len(trading_days),
                    as_of=as_of,
                )

            # B2132 (S6-B2128b): elapsed + the wall-time KILL used to sit
            # INSIDE `if i % 20 == 0`, so the owner's hard cap was only
            # evaluated every 20 sim-days - an overshoot of up to 20x the
            # per-day cost (MEASURED: 5.6x over a 0.05h cap on a 50-ticker
            # probe; 5-11 min over 2.5h caps on the B2118 pilot). On a heavy
            # config that let a 2.5h cap run past 5h while APPEARING to
            # honour it. Now evaluated EVERY day; only the progress LOG line
            # keeps the 20-day cadence.
            elapsed_s = (time.time() - self._run_start_time
                         if self._run_start_time else 0.0)
            elapsed_h = elapsed_s / 3600.0
            # S6-B2492: THIS is the guard that killed cfg1 at 16.10h, of
            # which 15.32h was the machine asleep. B2490 taught the
            # supervisor to tell those apart but left this site reading raw
            # wall-clock - the sibling the GENERALIZATION MANDATE is about.
            # The GATE still uses elapsed_h (owner ruling S6-B2491 pending);
            # only the reporting distinguishes them.
            suspended_h = getattr(self, "_suspended_seconds", 0.0) / 3600.0
            # S6-B2502b: the cap credits only unambiguous sleep (>= 30 min
            # gaps); suspended_h stays the REPORTING figure and active_h is
            # the CAP figure - two questions, two fields (L728).
            sleep_credit_h = getattr(self, "_sleep_credit_seconds", 0.0) / 3600.0
            active_h = max(0.0, elapsed_h - sleep_credit_h)
            if i % 20 == 0:
                # Batch 394: emit elapsed_hours in the progress line so the
                # external monitor (W1/W12) can grep wall-time without
                # needing to compute from start-of-log.
                logger.info(
                    "Progress: %d/%d [%s] open=%d closed=%d "
                    "elapsed_hours=%.2f suspended_hours=%.2f "
                    "active_hours=%.2f",
                    i, len(trading_days), as_of,
                    len(self.open_trades), len(self.closed_trades),
                    elapsed_h, suspended_h, active_h,
                )
            # WARN once at warn_run_hours threshold - on ACTIVE hours,
            # matching what the kill measures (S6-B2491).
            if (self.warn_run_hours is not None
                    and active_h >= self.warn_run_hours
                    and not self._warn_fired):
                logger.warning(
                    "Batch 394 WALL-TIME WARN: elapsed_hours=%.2f >= "
                    "warn_run_hours=%s; run will hard-exit at "
                    "max_run_hours=%s if still running",
                    elapsed_h, self.warn_run_hours, self.max_run_hours,
                )
                self._warn_fired = True
            # HARD-KILL at max_run_hours threshold.  Flush a final
            # checkpoint first so partial cube is salvageable.
            _kill_why = self.kill_decision(elapsed_h, sleep_credit_h,
                                           self.max_run_hours)
            if _kill_why:
                logger.error(
                    "Batch 394 RUN-HOURS KILL [%s]: elapsed=%.2fh "
                    "(suspended=%.2fh active=%.2fh sleep_credit=%.2fh) "
                    "cap=%sh. S6-B2491 IMPLEMENTED: the cap gates on ACTIVE "
                    "hours = elapsed minus CREDITED sleep (>= 30 min gaps "
                    "only). Flushing final checkpoint and exiting with code 1",
                    _kill_why, elapsed_h, suspended_h, active_h,
                    sleep_credit_h, self.max_run_hours,
                )
                try:
                    if self.closed_trades:
                        import pandas as _pd
                        _pd.DataFrame(
                            [vars(t) for t in self.closed_trades]
                        ).to_csv(
                            self.output_dir / "trade_log_checkpoint.csv",
                            index=False,
                        )
                        self._flush_open_trades_checkpoint(
                            self.output_dir)   # S6-B2213a
                        logger.error(
                            "Batch 394 final-checkpoint flushed: %d "
                            "closed trades to trade_log_checkpoint.csv",
                            len(self.closed_trades),
                        )
                except Exception as _exc:
                    logger.error(
                        "Batch 394 final-checkpoint flush failed: %s",
                        _exc,
                    )
                # B2126 (S6-B2125a): write engine_state.json BESIDE the CSV,
                # from the SAME closed-trade count, in the same instant.
                # Before this, the kill path wrote only the CSV while
                # engine_state.json still held the last PERIODIC checkpoint's
                # number - so the B1076 resume contract was inconsistent BY
                # CONSTRUCTION on every wall-time kill, and every resume was
                # refused (measured: sw10 csv 35 rows vs state 32). That made
                # --max-run-hours and --resume-from-checkpoint mutually
                # incompatible, which is exactly the pairing the owner's 3h
                # local cap forces. Same dict + atomic .tmp/os.replace as the
                # periodic emitter, so both writers stay one schema.
                try:
                    import json as _kjson
                    import os as _kos
                    import time as _ktime
                    _ktrades = len(self.closed_trades)
                    _kopen = len(self.open_trades)
                    _kstate = {
                        "simulated_day": i,
                        "cells_completed": _ktrades,
                        "status": "wall_time_kill",
                        "sim_date": str(as_of),
                        "sim_day_index": i,
                        "tickers_processed": len(
                            getattr(self, "liquid_universe", []) or []),
                        "trades_so_far": _ktrades,
                        "open_trades": _kopen,
                        "timestamp": _ktime.strftime(
                            "%Y-%m-%dT%H:%M:%SZ", _ktime.gmtime()),
                        "pid": _kos.getpid(),
                    }
                    _kpath = self.output_dir / "engine_state.json"
                    _ktmp = self.output_dir / "engine_state.json.tmp"
                    _ktmp.write_text(_kjson.dumps(_kstate, indent=2))
                    _kos.replace(_ktmp, _kpath)
                    logger.error(
                        "B2126 kill-path engine_state written: day=%d "
                        "trades=%d open=%d - resume contract intact",
                        i, _ktrades, _kopen,
                    )
                except Exception as _kexc:
                    # #122 paired success-check: a failed state write here
                    # means the NEXT resume will refuse. Say so loudly.
                    logger.error(
                        "B2126 kill-path engine_state write FAILED: %s - "
                        "this run is NOT resumable; re-run from scratch",
                        _kexc,
                    )
                # sys.exit(1) -- caller treats as fatal; monitor
                # watchdog backs this up at +5min if engine hangs.
                sys.exit(1)
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
            # Incremental checkpoint every 100 days - trade log survives crashes.
            # Batch 394 (2026-05-27) owner directive 2026-05-27: restore the
            # documented 100-day cadence.  The earlier `% 25` was a code drift
            # from 100-day cadence cited across LEARNINGS.md / CHECKLIST
            # references.  100-day balances salvage frequency against CSV
            # write cost on uncapped Phase 1A-beta runs (20K-50K trades).
            # B1081 PIVOT #44 fix (Council 200 framework-first): match the
            # engine_state.json write cadence at line 865 (i==50 OR i%100==0).
            # Pre-fix mismatch caused B1079 Phase 4 spot interrupt at i=50 to
            # leave trades_so_far=610 reported in engine_state.json but the
            # trade_log_checkpoint.csv never written (i=50 != i%100==0). Resume
            # infra (B1076) then HALTs on FileNotFoundError or schema-contract
            # mismatch. Writer-reader cadence must be paired per `feedback_
            # writer_reader_schema_contract_pin_test`.
            # B1089 Council 215 Fix 1 owner directive 2026-06-30 "Progress and
            # data to be saved every 30 minutes": ADD time-based trigger
            # (1800s) on top of sim_day cadence. Either trigger fires the
            # paired-writer block. _last_checkpoint_time resets ONLY after
            # BOTH writers succeed (atomic-pair semantics per Council 214).
            import time as _time_chkpt
            _now_chkpt = _time_chkpt.time()
            # B2181 (S6-B2175a): day 5 joins the trigger. The first
            # checkpoint used to be day 50 / 30 minutes, whichever came
            # first - so the sw10 crash at 19 minutes lost EVERYTHING and
            # sw50 at ~30 was saved by seconds. An early crash now costs
            # minutes of compute, not the whole leg.
            _sim_day_trigger = (i > 0 and (i == 5 or i == 50 or i % 100 == 0))
            _time_trigger = (i > 0 and (_now_chkpt - self._last_checkpoint_time)
                             >= self._checkpoint_interval_seconds)
            _should_checkpoint = _sim_day_trigger or _time_trigger
            _csv_written = False
            _engine_state_written = False
            if _should_checkpoint and self.closed_trades:
                try:
                    # B1046 F-11 fix: atomic write via tempfile + os.replace
                    # prevents partial-CSV reads by monitor (F-15 false HALT).
                    # Source: B1045 disposition F-11 + ticket S6-ATOMIC-CSV-
                    # WRITE-PATTERN per CHECKLIST #122.
                    import os as _os
                    import pandas as _pd
                    checkpoint_path = self.output_dir / "trade_log_checkpoint.csv"
                    checkpoint_tmp = self.output_dir / "trade_log_checkpoint.csv.tmp"
                    # B1260 (Council 303, S6-B1250-ENG1): serialize dict/list
                    # fields via the signals_serde contract. Pre-B1260 the
                    # raw vars(t) dicts hit to_csv as str(dict) with numpy
                    # reprs + nan -> unparseable by the resume reader ->
                    # every resume wiped signals_at_entry (B1250 ENG-1).
                    from backtest.util.signals_serde import dumps_signals
                    _rows = []
                    for t in self.closed_trades:
                        _r = dict(vars(t))
                        for _k, _v in _r.items():
                            if isinstance(_v, (dict, list)):
                                _r[_k] = dumps_signals(_v)
                        _rows.append(_r)
                    _pd.DataFrame(_rows).to_csv(checkpoint_tmp, index=False)
                    _os.replace(checkpoint_tmp, checkpoint_path)
                    logger.debug("Checkpoint: %d trades -> %s", len(self.closed_trades), checkpoint_path)
                    _csv_written = True  # B1089 atomic-pair tracking
                except Exception as _chk_exc:
                    # B1277 (FIX-4 companion; closes B1250 ENG-10 while here):
                    # checkpoint write failure now logged, not swallowed.
                    logger.warning("Checkpoint CSV write failed: %s", _chk_exc)
                # B1277 (Council 316, FIX-4 owner-approved): flush the raw
                # signal-fire counter at checkpoint cadence. Rung-3 lesson:
                # the counter lived only in memory until end-of-run emit, so
                # the interrupted segment's census died with the process --
                # G5 could only cover the resume segment. PID-tagged file is
                # simply overwritten with cumulative counts each checkpoint.
                try:
                    from backtest.signals.screener import emit_raw_signal_fire_counts
                    emit_raw_signal_fire_counts(self.output_dir)
                except Exception as _rf_exc:
                    logger.debug("raw-fires checkpoint flush skipped: %s", _rf_exc)

            # B1042 (2026-06-28) Council 136 Option-7 Layer 1 + B1043 Council 138
            # Sub-A F-01/F-05 fix: engine_state.json emission with SCHEMA MATCHING
            # b1019_phase_1_runtime_monitor.py reader (simulated_day +
            # cells_completed + status). Source: feedback_monitor_design_vs_
            # operational_gap (CHECKLIST #121) per Sub-A adversarial review B1043.
            #
            # B1043 FIXES:
            #   F-01: Monitor-expected key names (simulated_day NOT sim_day_index;
            #         cells_completed NOT trades_so_far). Backwards-compat keys
            #         retained for debugging.
            #   F-05: First emit at day 50 (was day 100 = ~50 min vs Phase 1
            #         MAX_MIN=30 = 30 min => never emitted). Add i==50 case.
            #
            # Atomic write via .tmp + os.replace prevents partial-state reads.
            # B1070 F-1.1 track latest sim_day + sim_date so final emit
            # (post _finalize_open_trades) has correct values.
            self._last_sim_day_index = i
            self._last_sim_date = as_of
            # B1089 Council 215 Fix 1: gate by same _should_checkpoint flag
            # as paired-writer CSV block above. Either sim_day OR 30-min
            # time trigger fires both writers.
            if _should_checkpoint:
                # S6-B2213a: the OPEN book is flushed HERE, not inside the
                # closed-trade block above, because that block is gated on
                # `self.closed_trades` - so a run holding open positions with
                # NONE closed yet wrote nothing, which is the worst case and
                # not an edge one: it is early in every run, exactly when a
                # kill loses the most. This block is unconditional on the
                # checkpoint trigger and writes engine_state.json, so pairing
                # the book with it makes the count and the positions ALWAYS
                # consistent - which is what the resume HALT relies on.
                self._flush_open_trades_checkpoint(self.output_dir)
                try:
                    import json as _json
                    import os as _os
                    import time as _time
                    _trades = len(self.closed_trades)
                    _open = len(self.open_trades)
                    state = {
                        # B1043 F-01 monitor-expected keys:
                        "simulated_day": i,
                        "cells_completed": _trades,
                        "status": "running",
                        # Backwards-compat + debugging fields:
                        "sim_date": str(as_of),
                        "sim_day_index": i,
                        "tickers_processed": len(getattr(self, "liquid_universe", []) or []),
                        "trades_so_far": _trades,
                        "open_trades": _open,
                        "timestamp": _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime()),
                        "pid": _os.getpid(),
                    }
                    state_path = self.output_dir / "engine_state.json"
                    state_tmp = self.output_dir / "engine_state.json.tmp"
                    state_tmp.write_text(_json.dumps(state, indent=2))
                    _os.replace(state_tmp, state_path)
                    _engine_state_written = True  # B1089 atomic-pair tracking
                    logger.info(
                        "CHECKPOINT day=%d sim_date=%s trades=%d open=%d "
                        "trigger=%s",
                        i, as_of, _trades, _open,
                        "sim_day" if _sim_day_trigger else "time_30min",
                    )
                except OSError as _ose:
                    # B1046 F-28 fix: disk-full (errno 28) is HALT-CRITICAL;
                    # transient OSErrors (EINTR, EAGAIN) treated as warnings.
                    # Source: B1045 disposition F-28 per CHECKLIST #122
                    # silent-failure-pairing rule.
                    import errno as _errno
                    if _ose.errno == _errno.ENOSPC:
                        logger.error("engine_state.json emit FAILED disk-full (ENOSPC); raising")
                        raise
                    logger.warning(
                        "engine_state.json emit transient OSError errno=%s: %s",
                        _ose.errno, _ose,
                    )
                except Exception as _e:
                    logger.warning("engine_state.json emit failed: %s", _e)
            # B1089 Council 215 Fix 1: atomic-pair timestamp reset.
            # Only reset _last_checkpoint_time if BOTH writers succeeded
            # (per Council 214 "Reset timestamp ONLY after both writers
            # succeed (atomic-pair semantics)"). If either failed, the
            # 30-min timer keeps ticking and next iteration retries.
            # Edge case: if closed_trades empty (CSV writer skipped),
            # we still consider checkpoint successful when engine_state
            # writes (degenerate-pair: trades=0 has no CSV to write).
            if _should_checkpoint:
                _pair_ok = _engine_state_written and (
                    _csv_written or not self.closed_trades
                )
                if _pair_ok and _time_trigger:
                    self._last_checkpoint_time = _now_chkpt
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

        # B1070 F-1.1 FIX (Council 172/175/176 Sub-B): emit status='complete'
        # to engine_state.json so B1019 monitor's PASS-exit conditions
        # (monitor.py lines 119-122, 146-148 poll for status=='complete')
        # actually fire. Pre-fix: lines 595-619 only wrote 'running'; never
        # re-written after _finalize_open_trades -> monitor hangs indefinitely
        # on PASS path. Same bug class as B1067 G-IMPL (buffer flush masked
        # by HALT path SIGTERM). Atomic .tmp + os.replace ensures monitor
        # never reads a half-written file. Per CHECKLIST #122 + #124 +
        # feedback_adversarial_review_must_check_successful_path_output.
        try:
            import json as _json_b1070
            import os as _os_b1070
            import time as _time_b1070
            _state_path = self.output_dir / "engine_state.json"
            _state_tmp = self.output_dir / "engine_state.json.tmp"
            _final_state = {
                "simulated_day": int(getattr(self, "_last_sim_day_index", 0)),
                "cells_completed": int(len(self.closed_trades)),
                "status": "complete",
                "sim_date": str(getattr(self, "_last_sim_date", "")),
                "sim_day_index": int(getattr(self, "_last_sim_day_index", 0)),
                "tickers_processed": int(len(getattr(self, "liquid_universe", []) or [])),
                "trades_so_far": int(len(self.closed_trades)),
                "open_trades": int(len(self.open_trades)),
                "timestamp": _time_b1070.strftime("%Y-%m-%dT%H:%M:%SZ", _time_b1070.gmtime()),
                "pid": _os_b1070.getpid(),
                "finalized_open_trades": int(n_finalized),
            }
            _state_tmp.write_text(_json_b1070.dumps(_final_state, indent=2))
            _os_b1070.replace(_state_tmp, _state_path)
            logger.info("B1070 F-1.1: emitted status='complete' to %s", _state_path)
        except Exception as _e_b1070:
            # Per CHECKLIST #122 silent-failure-pairing: log + propagate context
            # so structural bugs surface; engine still exits cleanly via outer
            # save_all_outputs call.
            logger.warning("B1070 F-1.1: status='complete' emit failed: %s", _e_b1070)

        # Batch 394 (2026-05-27): defer pool teardown to save_all_outputs so
        # the same spawn pool services both screen + cube replay.  Calling
        # teardown here would force save_all_outputs back to sequential
        # cube replay.  save_all_outputs invokes teardown at its end.

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

    def _emit_milestone_telemetry(self, kind: str, **context):
        """Batch 394 (2026-05-27): emit structured milestone telemetry.

        Two kinds:
          - MILESTONE-YEAR: at calendar-year flip, summarize prior year
            (trades, top strategies, direction balance, zero-fire strategies,
            regime distribution).
          - MILESTONE-100D: every 100 backtest days, summarize cumulative
            health (delta-trades, top strategies, direction balance,
            zero-fire strategies).

        Monitor parses these via regex on `[MILESTONE-` prefix.  Keep the
        format stable: changing breaks the monitor.
        """
        try:
            n_total = len(self.closed_trades)
            if n_total == 0:
                # Emit a "no fires yet" marker so monitor distinguishes
                # engine-stuck from engine-running-but-silent.
                logger.info(
                    "[MILESTONE-%s] %s cumulative_trades=0 (no fires yet)",
                    kind, " ".join(f"{k}={v}" for k, v in context.items()),
                )
                return

            # Direction balance
            n_long = sum(1 for t in self.closed_trades
                         if getattr(t, "direction", "") == "long")
            long_pct = round(100.0 * n_long / n_total, 1)

            # Per-strategy trade counts; top 5 + zero-fire count
            from collections import Counter
            strat_counts = Counter(
                getattr(t, "strategy", "?") for t in self.closed_trades
            )
            top5 = [f"{s}:{c}" for s, c in strat_counts.most_common(5)]
            registered = len(ALL_STRATEGIES) if "ALL_STRATEGIES" in globals() else 0
            zero_strats = max(0, registered - len(strat_counts))

            # Delta since last milestone for 100D variant
            delta = n_total - self._last_milestone_trades
            self._last_milestone_trades = n_total

            ctx_str = " ".join(f"{k}={v}" for k, v in context.items())
            logger.info(
                "[MILESTONE-%s] %s cumulative_trades=%d delta_trades=%d "
                "long_pct=%.1f%% top_strats=[%s] zero_strats=%d",
                kind, ctx_str, n_total, delta, long_pct,
                ",".join(top5), zero_strats,
            )
        except Exception as exc:  # noqa: BLE001
            # Never let telemetry crash the engine; log + continue.
            logger.warning(
                "Batch 394 telemetry emit failed (%s): %s", kind, exc,
            )

    def _init_screen_pool(self):
        """Batch 322 (2026-05-25): lazy-init the per-ticker screen pool.

        Uses multiprocessing.get_context('spawn') for cross-platform behavior
        (Windows requires spawn; Linux defaults to fork but spawn is safer
        for forks that import pandas / numpy after a process has already
        loaded large state).

        Workers receive ohlcv_dict + info_dict via the initializer (_pool_init
        in backtest.signals.screener); from then on per-day work-tuples carry
        only (ticker, as_of, regime, vix_value, vix_history, xs_features) -
        keeping per-call IPC small. Behavior preserved vs sequential per
        Batch 321 in-process parity test (DummyPool).

        No-op when self.screen_pool_workers == 0 (sequential mode).
        """
        if self.screen_pool_workers <= 0 or self._screen_pool is not None:
            return
        import multiprocessing as mp
        import os as _os_b1294
        from backtest.signals.screener import _pool_init
        # B1294 (FIX-4b): expose output dir to spawn-inherited worker env so
        # the worker-side census flush knows where to write (B1292 gap:
        # counter lives in worker, main-process flush saw it empty).
        _os_b1294.environ["R5_OUTPUT_DIR"] = str(self.output_dir)
        ctx = mp.get_context("spawn")
        # Cap workers at cpu_count so we don't oversubscribe (Hetzner CPX62
        # advertises 16 shared vCPU; setting screen_pool_workers=16 makes
        # sense there). Pool is small + long-lived for entire backtest run.
        n = min(self.screen_pool_workers, mp.cpu_count() or 1)
        logger.info("Batch 322: initializing screen pool with %d workers (spawn)", n)
        try:
            self._screen_pool = ctx.Pool(
                processes=n,
                initializer=_pool_init,
                initargs=(self.ohlcv_dict, self.info_dict),
            )
        except Exception as exc:
            # Fall back to sequential if pool init fails (large pickle, OOM,
            # spawn issue). Logged loud so runs surface the regression.
            logger.warning(
                "Batch 322: screen pool init failed (%s) - falling back to "
                "sequential screening", exc,
            )
            self._screen_pool = None
            self.screen_pool_workers = 0

    def _teardown_screen_pool(self):
        """Batch 322 (2026-05-25): clean up screen pool at end of run.
        Called from run() after the day-loop completes."""
        if self._screen_pool is None:
            return
        try:
            self._screen_pool.close()
            self._screen_pool.join()
        except Exception as exc:
            logger.warning("Batch 322: screen pool teardown error: %s", exc)
        finally:
            self._screen_pool = None

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
        # B1057 C-instrumentation (PIVOT #33 forensics enabler):
        # Phase-timing logs for per-day wall-clock decomposition. Smoke
        # v2.5d engine.log forensics revealed ~92% of per-day cost is
        # in unaccounted silent gaps. These markers let next forensics
        # decompose where the gap actually lives. Per Council 153/154 +
        # CHECKLIST #126 evidence-artifact rule. INFO-level so visible
        # without log-level flags.
        import time as _b1057_time
        _b1057_t_start = _b1057_time.time()
        logger.info("PHASE_TIMING day=%s start", as_of)
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
        _b1057_t_after_pit = _b1057_time.time()
        logger.info("PHASE_TIMING day=%s ohlcv_pit_built dur=%.3fs tickers=%d",
                    as_of, _b1057_t_after_pit - _b1057_t_start, len(ohlcv_pit))

        # -- 1b. BUG-287 fix (Batch 308 2026-05-24): include OHLCV for any
        # ticker with an OPEN trade, even if it dropped out of the annual
        # liquid set. Previously, when a ticker fell below the liquidity
        # floor (e.g., price < $5 mid-window), it was silently excluded
        # from `ohlcv_pit` -> ticker_bars -> process_day_exits, so the
        # exit-check loop never gave the trade a chance to close.
        #
        # Phase 1A-beta 2026-05-24 surfaced 6 stuck shorts on RIOT / HOUS /
        # UWMC / WW / CUBI / CURI held 371-1239 days while underlyings
        # rallied 2-5x against the position. Five of six were closed only
        # when the year-rollover annual re-check re-added them to liquid
        # set; CUBI/CURI never re-qualified and sat until end-of-backtest.
        # Combined drag: -1,347 pp on Phase 1A-beta aggregate.
        #
        # Fix scope: exit-check only. New entries are still gated by
        # liquid_this_year (we don't want to enter illiquid positions);
        # existing entries get exit-checked regardless of current liquidity.
        for trade in self.open_trades:
            if trade.ticker in ohlcv_pit:
                continue
            df = self.ohlcv_dict.get(trade.ticker)
            if df is None:
                continue
            sliced = df[df.index.date <= as_of]
            if len(sliced) >= 1:
                ohlcv_pit[trade.ticker] = sliced

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

        # Batch 292 (2026-05-21): bear composite indicator. Loads cached
        # yield curve, AAII sentiment, sector ETF OHLCV; computes 0-3 bear
        # score; passes to classifier. When >=2 indicators fire, regime
        # forced to "bear" regardless of SPY-above-200-EMA (catches
        # mid-bear rallies like Aug 2022). Caches loaded once via
        # self._bear_indicator_cache; recomputed lazily.
        try:
            if not hasattr(self, "_bear_indicator_cache"):
                from pathlib import Path
                _cache = {}
                # B2047 (S6-B1250-ENG8): anchored to the repo root - the bare
                # relative form silently found NOTHING from any other cwd and
                # the .exists() guards turned that into an empty cache with no
                # symptom (fail-open path resolution).
                _root = Path(__file__).resolve().parents[2]
                _yc_path = _root / "data_prefetch/fred/observations/T10Y2Y.parquet"
                if _yc_path.exists():
                    _cache["yc"] = pd.read_parquet(_yc_path)
                _aaii_path = _root / "data_prefetch/aaii/weekly_sentiment.parquet"
                if _aaii_path.exists():
                    _cache["aaii"] = pd.read_parquet(_aaii_path)
                # Sector ETF dict (already in self.ohlcv_dict)
                _cache["sectors"] = {
                    s: self.ohlcv_dict.get(s)
                    for s in ("XLK", "XLF", "XLE", "XLV", "XLI", "XLU", "XLP", "XLY")
                    if self.ohlcv_dict.get(s) is not None
                }
                self._bear_indicator_cache = _cache
            from backtest.engine.regime_filter import compute_bear_composite_score
            _bear = compute_bear_composite_score(
                as_of,
                yield_curve_df=self._bear_indicator_cache.get("yc"),
                aaii_df=self._bear_indicator_cache.get("aaii"),
                sector_ohlcv_dict=self._bear_indicator_cache.get("sectors"),
            )
            _bear_score = _bear.get("score", 0)
        except Exception as _exc:
            logger.debug("bear composite score failed: %s", _exc)
            _bear_score = 0

        regime_ctx = get_regime_context(
            vix, spy_close, spy_ema,
            prev_regime=self._prev_regime,
            vix_smoothed=vix_smoothed,
            use_hysteresis=use_hysteresis,
            bear_composite_score=_bear_score,
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
        # B1593 (owner-approved C): a DATE-KEYED regime map. `_regime_history`
        # is order-only, so `exit_regime_flip` could never locate the regime for
        # a given bar and fell back to a time stop on EVERY trade in EVERY cube
        # (L460: identical to time_stop_20d on 330 of 330).
        # B1622 CORRECTION: this comment previously said "Threaded to exits via
        # signals_at_entry" - it was NOT. Nothing wrote the key, so the fix was
        # inert for its whole life and the exit stayed a time stop. It is now
        # passed to `run_exit_comparison`, which injects it per trade at replay
        # (L481). The comment described an intention as though it were done.
        if not hasattr(self, "_regime_by_date"):
            self._regime_by_date = {}
        self._regime_by_date[as_of] = regime   # _process_day(self, as_of)
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
        # B1057 C-instrumentation: PHASE_TIMING decomposition checkpoint
        _b1057_t_pre_exits = _b1057_time.time()
        logger.info("PHASE_TIMING day=%s pre_exits dur=%.3fs",
                    as_of, _b1057_t_pre_exits - _b1057_t_after_pit)
        closed_today, self.open_trades = process_day_exits(
            self.open_trades, ticker_bars, as_of,
            vix, regime, active_signals, self.circuit_breaker_log,
            vix_history=_vix_history_for_exits,
        )
        self.closed_trades.extend(closed_today)
        _b1057_t_after_exits = _b1057_time.time()
        logger.info("PHASE_TIMING day=%s exits_done dur=%.3fs closed=%d",
                    as_of, _b1057_t_after_exits - _b1057_t_pre_exits,
                    len(closed_today))

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
        # Batch 322 (2026-05-25): lazy-init screen pool on first day when
        # enabled. Workers receive the full ohlcv_dict via initializer at
        # init time; per-day calls carry only the work-tuple per ticker.
        if self.screen_pool_workers > 0 and self._screen_pool is None:
            self._init_screen_pool()
        # B1057 C-instrumentation: PHASE_TIMING screen_universe
        _b1057_t_pre_screen = _b1057_time.time()
        logger.info("PHASE_TIMING day=%s pre_screen dur=%.3fs",
                    as_of, _b1057_t_pre_screen - _b1057_t_after_exits)
        candidates     = screen_universe(
            ohlcv_pit, self.info_dict, as_of, regime,
            vix_value=_vix_today_for_screen,
            vix_history=_vix_history_for_screen,
            pool=self._screen_pool,  # None when sequential mode
        )
        _b1057_t_after_screen = _b1057_time.time()
        logger.info("PHASE_TIMING day=%s screen_done dur=%.3fs candidates=%d",
                    as_of, _b1057_t_after_screen - _b1057_t_pre_screen,
                    len(candidates))
        active_signals = {c["ticker"]: c for c in candidates}
        sent           = sentiment_snapshot(as_of)
        _b1057_t_after_sentiment = _b1057_time.time()
        logger.info("PHASE_TIMING day=%s sentiment_done dur=%.3fs total=%.3fs",
                    as_of,
                    _b1057_t_after_sentiment - _b1057_t_after_screen,
                    _b1057_t_after_sentiment - _b1057_t_start)

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
        if self.level_6_state.halt_triggered and not self.no_dd_halt:
            # Halt = no new entries this day; existing trades continue under exit logic
            # Batch 383: when no_dd_halt=True (Phase 1A-beta cube evaluation),
            # this halt is bypassed - cube verdict computation is not a
            # capital-deployment decision so the DD halt does not apply.
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
                    # B1330 (Council 361, owner-approved): bypass the dispersion
                    # CB in cube isolation - it's a market-wide execution-layer
                    # halt, not a per-strategy signal gate; pure-signal cells
                    # must not lose entries to it (consistent with M2 bypassing
                    # the other execution gates).
                    if _cb_result.get("triggered") and not self.cube_isolation:
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

        # B1321 (Council 353, M2 pure-signal isolation): no cross-strategy
        # candidate cap in isolation - every strategy's signal is evaluated.
        _cand_iter = candidates if self.cube_isolation else candidates[:self.max_cands]
        for cand in _cand_iter:
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
            #
            # Batch 287.B (2026-05-20 owner-approved per Audit Part 3 sec-10):
            # Two-pass split count. Original Batch 279 used pre-gate count
            # which over-counts strategies (some get filtered by regime
            # affinity / blocklist / crisis-exclusion downstream), causing
            # under-sized positions. Now pre-scan to count survivors of the
            # deterministic gates (regime affinity, blocklist, crisis-long-
            # exclusion, avoid-direction). Conservative: validate_entry_zone
            # and portfolio gates still happen later; those may filter more
            # but are too expensive to pre-check. Net effect: recovers ~30%
            # of tier capacity on multi-strategy days.
            from backtest.config import (
                STRATEGY_REGIME_BLOCKLIST as _SRB,
                CRISIS_LONG_EXCLUSIONS as _CLE,
            )
            from backtest.engine.regime_selector import should_strategy_fire_in_regime as _ssfir
            _crisis_now = regime == "crisis"
            _survivors = 0
            for _se in cand.get("strategies", []):
                _sname = _se.get("strategy", "")
                _sdir = _se.get("direction", "")
                if _sdir == "avoid":
                    continue
                if regime in _SRB.get(_sname, []):
                    continue
                # Batch 291: pass direction so pre-scan uses the same
                # direction-aware default that the inner loop uses.
                if not _ssfir(_sname, regime, direction=_sdir):
                    continue
                if _sdir == "long" and _crisis_now and ticker in _CLE:
                    continue
                _survivors += 1
            _n_strategies_for_split = max(1, _survivors)

            # BUG-61 concurrent-block (Batch 510a 2026-05-31 -- modes added
            # per owner directive "investigate + fix" to recover 685k blocked
            # candidates without removing concentration risk management).
            # Mode logic gated on config.BUG_61_BLOCK_MODE. The default
            # ("ticker") preserves the prior owner-approved Option A behavior
            # exactly; alternate modes only fire when owner sets the flag.
            from backtest.config import BUG_61_BLOCK_MODE as _bug61_mode
            # B1321 (Council 353): isolation forces same-strategy-only block
            # (different strategies stack on a ticker; a strategy can't
            # double-open). Removes the cross-strategy ticker contamination.
            if self.cube_isolation:
                _bug61_mode = "ticker_strategy"
            if _bug61_mode == "off":
                pass  # No block; portfolio cap + cooldown + max-loss still apply
            elif _bug61_mode == "ticker_direction":
                # Block only same-direction entries on this ticker
                _open_dirs = {
                    t.direction for t in self.open_trades if t.ticker == ticker
                }
                # The candidate has one or more strategies; if any candidate
                # direction matches an open direction, block; otherwise allow.
                _cand_dirs = {
                    s.get("direction") for s in cand.get("strategies", [])
                }
                if _open_dirs & _cand_dirs:
                    self.skipped_trades.append({
                        "ticker": ticker, "date": as_of,
                        "strategy": "(any-same-direction)",
                        "reason": "ticker_already_open_same_direction_bug61_mode_b",
                    })
                    continue
            elif _bug61_mode == "ticker_strategy":
                # Block only when the SAME strategy already has an open pos
                # on this ticker. Different strategies can stack.
                _open_strats = {
                    t.strategy for t in self.open_trades if t.ticker == ticker
                }
                _cand_strats = {
                    s.get("strategy") for s in cand.get("strategies", [])
                }
                if _open_strats & _cand_strats:
                    self.skipped_trades.append({
                        "ticker": ticker, "date": as_of,
                        "strategy": "(same-strategy)",
                        "reason": "ticker_already_open_same_strategy_bug61_mode_c",
                    })
                    continue
            else:  # default "ticker": owner-approved Option A (prior behavior)
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
            if cooldown_breach and not self.cube_isolation:
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
            if _cum_pnl <= _cap_pct and not self.cube_isolation:
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
            if (hasattr(self, "portfolio") and self.portfolio.positions
                    and not self.cube_isolation):
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

                # Batch 510b (2026-05-31, R4 spec per owner directive):
                # STRATEGY_REQUIRED_MACRO_REGIME -- when a strategy is keyed
                # here, accept the candidate only if `macro_score` matches.
                # macro_score sign: < 0 = "negative", > 0 = "positive",
                # == 0 = "neutral" (matches the Batch 501 bucketing).
                # Default empty dict -> no behavior change for non-R4 runs.
                # Owner populates the dict in backtest/config.py for R4
                # cube spec; populated entries activate the filter.
                from backtest.config import STRATEGY_REQUIRED_MACRO_REGIME
                _req_macro = STRATEGY_REQUIRED_MACRO_REGIME.get(
                    strat_entry["strategy"]
                )
                if _req_macro is not None:
                    _macro_val = float(macro.get("macro_score", 0) or 0)
                    if _macro_val < 0:
                        _macro_band = "negative"
                    elif _macro_val > 0:
                        _macro_band = "positive"
                    else:
                        _macro_band = "neutral"
                    if _macro_band != _req_macro:
                        self.skipped_trades.append({
                            "ticker": ticker, "date": as_of,
                            "strategy": strat_entry["strategy"],
                            "reason": f"required_macro_regime_mismatch_{_req_macro}_got_{_macro_band}_batch510b",
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
                # Batch 291 (2026-05-21 owner-approved option B): pass
                # direction so the regime selector applies the new
                # direction-aware default for un-mapped strategies (long
                # defaults to {bull, neutral}, short to {bear, crisis, neutral})
                # instead of allow-all. Closes Stage C v2 gap where 25 long
                # trades fired in bear regime via affinity-not-in-map fallback.
                # Batch 384: when no_regime_affinity=True (Phase 1A-beta cube),
                # skip the affinity filter. Cube collects per-regime data
                # empirically.
                if not self.no_regime_affinity:
                    if not should_strategy_fire_in_regime(
                            strat_entry["strategy"], regime,
                            direction=direction):
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

                # Batch 287.C (2026-05-20): removed duplicate `crisis_flag =
                # regime == "crisis"` here. The canonical assignment at
                # function scope (line 601) is the only one needed; this
                # inner re-assignment was redundant (same value, no effect).

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

                # Smart money. Batch 363 silent-gap fix (owner-approved 2026-05-25):
                # smart_money_score reads from data_prefetch/quiver/ ONLY (NO live
                # API per DEC-497 HARD CUT; enforced at smart_money._get_quiver_data
                # line 132). The legacy QUIVER_API_KEY gate caused all 2026-05-24
                # Phase 1A-beta trades to record smart_money_score=0,
                # congressional/insider/institutional_signal="none" -- invalidating
                # DEC-124 confluence cells + "smart money lift >=3pp" passing
                # criterion. Removed the env-var gate so the cache-only function
                # is always called. Sentinel default retained for hard cache-miss.
                sm = {"composite_signal": "none", "score": 0,
                      "congressional_signal": "none", "insider_signal": "none",
                      "institutional_signal": "none"}
                # B1544 REVERTED (B1543's skip was WRONG). I argued sizing could
                # not move the gates because the cube records pnl_pct, a
                # PERCENTAGE. But tier does not only SIZE a trade - config.py:857:
                # "LOW maps to 0 to skip". Tier GATES ENTRY. Measured A/B on 20
                # tickers x 2y: skipping this call changed the entry set (245 only
                # -ON, 124 only-OFF of ~5.2k), so optimisation cubes would not be
                # comparable to R5. The saving was 6.3pct measured, not the 14.3pct
                # profiler share - not worth a semantic change even if it were safe.
                try:
                    sm = smart_money_score(ticker, as_of)
                except Exception as e:
                    logger.warning("smart_money_score failed for %s @ %s: %s",
                                   ticker, as_of, e)

                # Stage 1  -  rule-based preliminary tier
                # Batch 489 (M9 wire-in): also pass strategy names so
                # _assign_confidence_tier can use effective_strategy_count
                # (cluster-collapsed) when self._strategy_cluster_lookup is
                # populated. Defaults to raw count when lookup is empty.
                firing_strategy_names = [
                    s["strategy"] for s in cand["strategies"] if "strategy" in s
                ]
                preliminary_tier = self._assign_confidence_tier(
                    len(cand["strategies"]), sm, macro, sent,
                    firing_strategies=firing_strategy_names,
                )
                # Batch 531 (2026-05-31, P17d activation per owner directive
                # "wire in activate truly pending items"). Apply officer-
                # change tier modifier: if 8-K Item 5.02 was filed in last
                # 7 days, downgrade preliminary tier by 1 slot (CEO/CFO
                # departure uncertainty premium). Silent-failure guarded;
                # no-op when decoded cache miss OR no 5.02 filing in window.
                try:
                    from backtest.signals.sec_edgar_modifiers import (
                        tier_modifier_officer_change_5_02,
                    )
                    preliminary_tier = tier_modifier_officer_change_5_02(
                        ticker, as_of, preliminary_tier,
                    )
                except Exception as _mod_exc:
                    # B2120 (#122): a silent pass here disabled the 5.02
                    # officer-change tier modifier with no trace (the B832
                    # SPOF class). One-shot warning per process.
                    global _OFFICER_MOD_WARNED
                    if not _OFFICER_MOD_WARNED:
                        _OFFICER_MOD_WARNED = True
                        logger.warning(
                            "officer-change 5.02 tier modifier failed (%r) - "
                            "tiers proceed unmodified (B2120 #122)", _mod_exc)

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
                # Batch 384: when no_event_suppression=True (Phase 1A-beta cube),
                # skip the entire DEC-348 event-suppression gate. Cube
                # measures strategy robustness through events.
                if _event_suppressed and not self.no_event_suppression:
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
                # Batch 287.A (2026-05-20 owner-approved per Audit Part 3 sec-2):
                # Per-strategy initial_pct override. Mean-reversion strategies
                # need tighter stops (e.g., 3-5%); trend strategies need wider
                # (e.g., 12-15%) to avoid whipsaw. Falls back to TRAILING_STOP
                # default (0.10) when no override.
                from backtest.config import STRATEGY_EXIT_OVERRIDE as _SEO_INIT
                _strat_init_override = _SEO_INIT.get(strat_entry["strategy"], {})
                _init_pct = _strat_init_override.get(
                    "initial_pct", TRAILING_STOP["initial_pct"])
                if direction == "long":
                    init_stop = entry_price * (1 - _init_pct)
                else:
                    init_stop = entry_price * (1 + _init_pct)

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
                    # B1545 (owner-approved): in cube isolation, the sizing TIER
                    # must not gate ENTRY. LOW/AVOID map to 0.0, and a 0 size
                    # skips the trade - so smart-money/agent tier data was
                    # silently deciding WHICH SIGNALS BECOME TRADES, which is
                    # exactly what isolation exists to remove (L418: a measured
                    # A/B showed 245/124 entry differences from this alone).
                    # Every valid signal now opens a trade at a UNIFORM size.
                    # Metrics are unaffected because the cube records pnl_pct,
                    # a PERCENTAGE - size cancels. Owner accepted the loss of
                    # R5 comparability on the trade POPULATION to get
                    # signal-pure cells.
                    if self.cube_isolation:
                        size_pct = CUBE_ISOLATION_SIZE_PCT
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
                        # Batch 377 (owner directive 2026-05-26): when
                        # no_portfolio_cap=True (Phase 1A--beta cube evaluation),
                        # bypass BOTH Batch 203 regime cap AND
                        # LIVE_TRADING_RULES["max_open_positions"]. Cube
                        # exhaustive evaluation needs every gate-eligible
                        # candidate to enter; Phase 1A--beta prior runs lost 56
                        # strategies to cap saturation. Phase 1B--alpha re-engages
                        # the cap.
                        if self.no_portfolio_cap:
                            # Still apply drawdown halt (capital-protection
                            # gate is separate from cap saturation gate);
                            # still apply ticker-uniqueness + cash-sufficiency
                            # gates per can_open() second-stage checks.
                            _effective_cap = 99999
                        else:
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
                        # Batch 383: when no_dd_halt=True (Phase 1A-beta cube),
                        # raise the can_open drawdown_suspend gate to 999%
                        # so portfolio.can_open never blocks on DD. Other
                        # second-stage gates (ticker-uniqueness + cash
                        # sufficiency) still apply.
                        if self.no_dd_halt:
                            _dd_suspend = 999.0
                        else:
                            _dd_suspend = LIVE_TRADING_RULES["drawdown_suspend_threshold"] * 100.0
                        ok, reason = self.portfolio.can_open(
                            ticker=ticker, size_pct=size_pct,
                            max_positions=_effective_cap,
                            drawdown_suspend_pct=_dd_suspend,
                        )
                        # B1321 (Council 353): isolation bypasses the portfolio
                        # gate (position cap / cash / cross-strategy ticker
                        # uniqueness) - every valid signal opens a trade.
                        if not ok and not self.cube_isolation:
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

                # B1321 (Council 353): in isolation, multiple strategies hold the
                # same ticker, but Portfolio.positions is ticker-keyed and cannot
                # represent that. The cube reads self.closed_trades (not portfolio
                # state), so skip the portfolio mirror in isolation - the trade is
                # already recorded in open_trades above. (Equity curve is not used
                # for per-strategy cube cells, which are per-trade-% + per-strategy.)
                if self.cube_isolation:
                    continue

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

    def _assign_confidence_tier(self, strategy_count, sm, macro, sent,
                                  firing_strategies=None) -> str:
        """Stage 1  -  rule-based preliminary tier before agents run.

        Batch 263 (Class B confluence, owner-approved 2026-05-20):
        Tightened tier thresholds to better differentiate quality.
        Post-1A-alpha forensic showed 1165 of 1181 trades got HIGH tier
        because strategy_count >= 3 was too easy. HIGH now requires >=4
        strategies + VERY_HIGH requires >=3 + smart money confluence.

        Batch 489 (M9 wire-in 2026-05-30): when `firing_strategies` list +
        a populated `self._strategy_cluster_lookup` are both present, use
        the EFFECTIVE strategy count (number of distinct clusters firing)
        instead of the raw count. Five strategies that are surface forms
        of the same underlying pattern count as 1 independent signal, not
        5 (closes M9 queue item). Back-compat: when lookup is empty
        (default) OR firing_strategies is None, falls back to raw
        strategy_count -- preserves pre-Batch-489 behaviour exactly.
        """
        # M9 wire-in: derive effective count when lookup + names available
        effective_count = strategy_count
        if firing_strategies is not None and \
                getattr(self, "_strategy_cluster_lookup", None):
            try:
                from backtest.engine.correlation_aware_count import (
                    effective_strategy_count,
                )
                effective_count = effective_strategy_count(
                    firing_strategies, self._strategy_cluster_lookup,
                )
            except Exception as exc:
                logger.debug("effective_strategy_count failed: %s; "
                             "falling back to raw count", exc)
                effective_count = strategy_count
        sm_sig = sm.get("composite_signal", "none")
        # AVOID  -  strong negative smart money regardless of technical signals
        if sm_sig == "congressional_sell+insider_cluster_sell":
            return "AVOID"
        if sm_sig == "congressional+insider_cluster" and effective_count >= 4:
            return "EXCEPTIONAL"
        if sm_sig == "congressional_or_insider" and effective_count >= 3:
            return "VERY_HIGH"
        if effective_count >= 4:                                    # Batch 263: was >= 3
            return "HIGH"
        if effective_count >= 3:                                    # Batch 263: was >= 2
            return "MEDIUM_HIGH"
        if effective_count >= 2:                                    # Batch 263: was sm + count>=1
            return "MEDIUM"
        if sm.get("score", 0) >= 2 and effective_count >= 1:
            return "LOW"  # Batch 263: was else; now MEDIUM-LOW floor on smart-money-confluence-only
        return "LOW"

    def load_strategy_cluster_lookup(self, path) -> int:
        """Batch 489 (M9 wire-in): load a precomputed strategy-cluster
        lookup JSON to activate effective_strategy_count in
        _assign_confidence_tier.

        Path must point at a JSON file containing a dict
        {strategy_name -> cluster_id (int)}. Returns the number of
        clusters (max cluster_id + 1) after loading.

        Generator (follow-on batch): scripts/build_strategy_clusters.py
        will read a prior cube trade_log, call M1's
        `compute_strategy_correlation_matrix` +
        `build_strategy_cluster_lookup`, and dump the result here. Until
        that ships, the lookup stays empty + the engine falls back to
        raw strategy_count.
        """
        import json
        from pathlib import Path as _P
        p = _P(path)
        if not p.exists():
            logger.warning(
                "load_strategy_cluster_lookup: %s does not exist; "
                "cluster lookup remains empty (engine uses raw strategy_count)",
                path,
            )
            return 0
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError(f"expected dict, got {type(data).__name__}")
            self._strategy_cluster_lookup = {str(k): int(v)
                                              for k, v in data.items()}
            n_clusters = (max(self._strategy_cluster_lookup.values()) + 1
                          if self._strategy_cluster_lookup else 0)
            logger.info(
                "Batch 489 M9: loaded strategy_cluster_lookup from %s -- "
                "%d strategies across %d clusters", path,
                len(self._strategy_cluster_lookup), n_clusters,
            )
            return n_clusters
        except Exception as exc:
            logger.warning(
                "load_strategy_cluster_lookup failed for %s: %s; "
                "cluster lookup remains empty", path, exc,
            )
            return 0

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
        #
        # Batch 394 (2026-05-27): parallelize per-strategy cube replay
        # across the existing Batch 322 screen pool when alive.  Each
        # strategy is independent; the loop is embarrassingly parallel.
        # Per-task IPC stays small: trades_data_lite drops `df` and the
        # worker reconstructs from screener._WORKER_OHLCV.  When pool is
        # not alive (screen_pool_workers==0), falls through to sequential.
        from backtest.engine.exit_context import build_entry_context
        from backtest.engine.exit_strategies import _pool_cube_replay_worker

        # B1261 (S6-B1250-ENG2): ATR-proxy fallback observability counters.
        self._replay_atr_counters = {"total": 0, "fallback": 0}

        # Build per-strategy task list (without df_full in payload).
        strategy_tasks = []
        for strategy in df_trades["strategy"].unique():
            strat_df    = df_trades[df_trades["strategy"] == strategy]
            trades_data_lite = []
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
                # B1261 (Council 303, S6-B1250-ENG2 owner-approved): count
                # ATR-proxy fallbacks instead of falling back silently. In
                # Batch A the ENG-1 wipe made this fallback fire for 100%
                # of replayed trades (crude 2pct-of-price proxy) with zero
                # visibility. resolve_replay_atr tallies into
                # self._replay_atr_counters; rate warning emitted after the
                # replay loop (>5% threshold).
                atr = resolve_replay_atr(
                    sig, row["entry_price"], self._replay_atr_counters)

                entry_context = build_entry_context(
                    row=row,
                    ticker=ticker,
                    entry_date=entry_date,
                    df_full=df_full,
                    spy_df=self.spy_df,
                    signals=sig if isinstance(sig, dict) else {},
                    atr=atr,
                )

                trades_data_lite.append({
                    # B1682: the entry REGIME. `exit_regime_flip` needs BOTH a
                    # regime series AND `entry_regime`; B1622 supplied only the
                    # series. PROVEN root cause: `signals_at_entry` carries 768
                    # keys and `regime_at_entry` is NOT one of them - it is a
                    # top-level trade field - so `entry_regime` resolved to None,
                    # `if regime_series is not None and entry_regime:` was False,
                    # and the exit fell back to a time stop on 302 of 302 trades.
                    "regime_at_entry": row.get("regime_at_entry") or row.get("regime"),
                    "ticker":         ticker,
                    # NOTE: no "df" -- worker reconstructs from _WORKER_OHLCV
                    "entry_date":     entry_date,
                    "entry_price":    row["entry_price"],
                    "direction":      row["direction"],
                    "atr":            atr,
                    "signals":        sig if isinstance(sig, dict) else {},
                    "entry_context":  entry_context,
                    # Batch 415 (2026-05-28): propagate category so cube replay
                    # can populate signals["category"] downstream for
                    # class_time_stop / earnings_blackout etc. Without this,
                    # those exits silently failed (class_time_stop defaulted
                    # to "momentum"; earnings_blackout got ticker="" and
                    # returned no_earnings_known 100% of the time).
                    "category":       row.get("category", "momentum"),
                })
            if trades_data_lite:
                # B2043 (S6-B2018a): the regime map rides IN THE TASK PAYLOAD.
                # `set_worker_regime_map` was defined at B1682 to hand workers
                # the map and had exactly ONE occurrence in the codebase - its
                # own definition - so every pooled replay ran with no regime
                # series and regime_flip fired its cap branch on 549/549 E1
                # rows. The pool initializer cannot carry it (the pool exists
                # before the sim fills the map), so the payload does (~251
                # entries per task - trivial IPC).
                strategy_tasks.append((strategy, trades_data_lite,
                                       dict(getattr(self, "_regime_by_date", {}) or {})))

        # B1261 (S6-B1250-ENG2): emit the ATR-proxy fallback rate; escalate
        # to WARNING above the 5% threshold (pre-ENG-1-fix Batch A was 100%).
        _atr_msg = emit_replay_atr_fallback_report(self._replay_atr_counters)
        _atr_rate_bad = (self._replay_atr_counters.get("total", 0) > 0 and
                         self._replay_atr_counters.get("fallback", 0) /
                         self._replay_atr_counters["total"]
                         > REPLAY_ATR_FALLBACK_WARN_RATE)
        (logger.warning if _atr_rate_bad else logger.info)(_atr_msg)

        exit_frames = []
        trade_detail_frames = []
        if (self._screen_pool is not None and self.screen_pool_workers > 0
                and strategy_tasks):
            # B1070 F-2.1 FIX (Council 172/175/176 Sub-B): pool.starmap
            # materializes results list = 5-20GB resident at Phase 4 scale
            # (220 strategies x 30-50K trades x per-trade entry_context
            # pickled to N workers). 64GB instance OOM risk. Fix: use
            # imap_unordered + stream-collect so memory peaks at single-
            # result-pair instead of full materialized list. Per
            # feedback_designed_vs_verified_requires_evidence_artifact +
            # CHECKLIST #124. Same parallelism + same semantics; lower
            # peak memory.
            logger.info(
                "B1070 F-2.1 (was Batch 394): streaming parallel cube replay "
                "across %d strategies on %d pool workers via imap_unordered",
                len(strategy_tasks), self.screen_pool_workers,
            )
            results = []
            try:
                # Council 233 Bug A fix: use module-level _b1070_starmap_wrapper
                # (defined at top of this file) so multiprocessing spawn (Windows
                # default) can pickle it. Previously a closure -> silent pickle
                # failure -> fallback to broken sequential path (Bug B).
                # imap_unordered yields results as workers complete; we consume
                # them in a generator-loop so full result list is NOT held in
                # memory simultaneously.
                for _result_pair in self._screen_pool.imap_unordered(
                    _b1070_starmap_wrapper, strategy_tasks,
                    chunksize=1,
                ):
                    results.append(_result_pair)
            except Exception as exc:
                # Council 233 Bug B fix: when pool imap fails, DO NOT call
                # _pool_cube_replay_worker from main process (it requires
                # screener._WORKER_OHLCV which is only set by pool initializer).
                # Instead use the same main-process reconstruction as the
                # pool-disabled ELSE branch below: pull df from
                # self.ohlcv_dict + call run_exit_comparison directly.
                logger.warning(
                    "B1070 F-2.1: streaming pool cube replay failed (%s); "
                    "falling back to sequential per-strategy with main-process "
                    "df reconstruction (Council 233 Bug B fix 2026-07-02)", exc,
                )
                from backtest.engine.exit_strategies import run_exit_comparison
                results = []
                # B2092: the payload is a 3-TUPLE since B2043 (regime map
                # rides the task). Both non-pool branches kept 2-tuple
                # unpacks and crashed the S6-B2070 save after a completed
                # 3-hour day loop (L592 - the unit of the change was
                # smaller than the unit of the defect). The payload's own
                # map is authoritative here, same as the pool worker sees.
                for strategy_name, trades_data_lite, _rbd in strategy_tasks:
                    trades_data_full = []
                    for t in trades_data_lite:
                        df_full = self.ohlcv_dict.get(t["ticker"])
                        if df_full is None:
                            continue
                        trades_data_full.append({**t, "df": df_full})
                    if trades_data_full:
                        results.append(
                            run_exit_comparison(strategy_name, trades_data_full,
                                            _rbd or None)
                        )
        else:
            # Sequential fallback -- workers can't run; reconstruct df
            # inline since _WORKER_OHLCV is not set in main process.
            results = []
            # B2092: same 3-tuple unpack as the pool-failure branch above.
            for strategy_name, trades_data_lite, _rbd in strategy_tasks:
                trades_data_full = []
                for t in trades_data_lite:
                    df_full = self.ohlcv_dict.get(t["ticker"])
                    if df_full is None:
                        continue
                    trades_data_full.append({**t, "df": df_full})
                if trades_data_full:
                    results.append(
                        run_exit_comparison(strategy_name, trades_data_full,
                                            _rbd or None)
                    )

        for ec, td in results:
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

        # Batch 394 (2026-05-27): tear down screen pool now that both
        # screen + cube replay have completed.  Single teardown point.
        self._teardown_screen_pool()
