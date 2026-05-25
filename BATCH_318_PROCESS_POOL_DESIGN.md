# Batch 318: Per-Ticker Process Pool — Design Doc

**Status:** Design draft 2026-05-25; **implementation deferred** to its own
focused batch given parity risk + complexity.

## Goal
Parallelize the per-ticker `screen_instrument` loop inside `screen_universe`
on Hetzner CPX62's 16 vCPU. Theoretical speedup: 10-14× on the per-day
screen path. Expected real speedup after IPC + pickle overhead: 4-8×.

## Current architecture
- `BacktestEngine._process_day(as_of)` runs per day in the backtest range.
- It calls `screen_universe(ohlcv_pit, info_dict, as_of, regime, vix_value, vix_history)`.
- `screen_universe` (in `backtest/signals/screener.py:screen_universe`) does:
  1. Universe-wide cross-sectional pre-pass (`compute_cross_sectional_features`).
  2. Sequential per-ticker iteration calling `screen_instrument` on each
     ticker (~1937 calls for Phase 1A-β at ~300ms = ~10 min per day; ×1044 days).

`screen_instrument` is a pure function over `(ticker, df, info, as_of, regime, vix_value, vix_history, xs_features)`. No engine state mutation.

## Pickling-aware design
- **IPC overhead is the critical constraint.** OHLCV DataFrames are ~200KB
  pickled each × 1937 tickers × 1044 days = ~400GB total IPC if naive.
- **Solution: workers hold their own copy of `ohlcv_dict`** after pool init.
  Per-day work item becomes just `(ticker, as_of, regime, vix_value,
  vix_history_compact, xs_features_for_ticker)` — small dict pickleable
  in microseconds.

## Implementation sketch
```python
# In backtest/engine/backtest.py BacktestEngine.__init__
self._screen_pool = None  # Lazy-init at first _process_day

def _init_screen_pool(self):
    import multiprocessing as mp
    ctx = mp.get_context("spawn")  # spawn for Windows + clean process state
    self._screen_pool = ctx.Pool(
        processes=min(16, mp.cpu_count()),
        initializer=_pool_init,
        initargs=(self.ohlcv_dict, self.info_dict),
    )

# Worker module-level state (set by initializer)
_OHLCV: dict = None
_INFO: dict = None

def _pool_init(ohlcv_dict, info_dict):
    global _OHLCV, _INFO
    _OHLCV = ohlcv_dict
    _INFO = info_dict
    # Pre-warm module-level caches (insider_buying, index_rebalance, etc.)
    from backtest.signals.insider_buying import _load_insiders_global
    from backtest.signals.index_rebalance import _load_events
    _load_insiders_global()
    _load_events()

def _worker_screen(args):
    ticker, as_of, regime, vix_value, vix_history, xs_features = args
    from backtest.signals.screener import screen_instrument
    df = _OHLCV.get(ticker)
    if df is None:
        return None
    info = _INFO.get(ticker, {"ticker": ticker})
    # Slice df to as_of in worker (avoids sending sliced df over wire)
    df_slice = df[df.index.date <= as_of]
    return screen_instrument(
        ticker, df_slice, info, as_of, regime,
        vix_value=vix_value, vix_history=vix_history,
        xs_features=xs_features,
    )
```

## Risk considerations
1. **Pickle overhead per pool init.** `ohlcv_dict` = ~400MB serialized. With
   `spawn` context (Windows-compatible) we pay this ONCE at pool startup,
   not per day. On Linux `fork` is cheap; on Windows / macOS `spawn` is
   3-10 seconds per worker = ~30-160 seconds startup cost. Amortized over
   1044 days, that's negligible.

2. **`xs_features` distribution.** Currently computed by `screen_universe`
   in the main process and passed per-ticker via dict lookup. Solution:
   stays in main process; we send the per-ticker sub-dict in the work
   tuple. Small payload.

3. **`regime` + `vix_value` + `vix_history`.** All small primitives /
   short lists. Per-day broadcast cost negligible.

4. **Determinism + parity.** The current `screen_universe` sorts candidates
   by `(strategy_count, tech_signal_count)` after iteration. The parallel
   version returns candidates in arbitrary order, then re-sorts. Same final
   ordering, but in-process iteration order changes during scoring. Parity
   golden may regen if any tie-breaker is order-sensitive — needs careful
   audit.

5. **Engine state.** `_process_day` reads/writes self state outside
   `screen_universe` (open trades, equity curve, regime classifier).
   That stays in main process. Only the screen step parallelizes.

6. **Lead-lag sector strategies.** `screen_lead_lag_sector` reads
   `ohlcv_dict` directly. Either keep it in main process (after parallel
   screen) or pass `ohlcv_dict` via worker init (already planned).

## Empirical Pre-flight required
1. Smoke test: run engine on Stage D scenario WITHOUT pool; record
   wall-clock + trade count + sum_pnl.
2. Same with pool, single worker (sanity).
3. Same with pool, 4 workers.
4. Same with pool, 16 workers.
5. Compare trade logs row-by-row for parity. Investigate any divergence.
6. Profile pool init overhead and per-day dispatch overhead.

## Estimated savings
On Hetzner CPX62 (16 shared vCPU):
- Sequential baseline: ~11h Phase 1A-β
- 4 workers: ~3.5-4h (Amdahl-limited by main-process steps: equity
  update, exit checks, regime classify).
- 16 workers: ~2-2.5h (heavily Amdahl-limited; mostly bound by single-
  threaded exit/equity logic).

Combined with 316b cache savings (~1-1.5h) and any compute_smc / supertrend
optimization (~30-60min potential), total target: **<2h on Hetzner CPX62**
without going to AWS spot.

## Implementation effort
- 4-6 hours code + 1h focused parity validation + 1h cross-platform
  testing (spawn vs fork) = ~1 working session.
- HIGH risk on parity — must run full pyramid + parity + smoke before
  any Stage D / Phase 1A-β re-run.

## Recommendation
**Implement as its own focused batch (e.g., Batch 320 after 319 forensic
land first).** This work has:
- Parity risk (tie-breaker ordering)
- Cross-platform risk (Windows spawn vs Linux fork)
- IPC overhead measurement needs (real machine, not dev laptop)

Deferring it gives owner a chance to confirm scope + provides time to
land safer wins (316b cache, 319+ forensic) first.
