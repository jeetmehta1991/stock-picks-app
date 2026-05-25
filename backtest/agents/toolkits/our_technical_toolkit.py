"""OurTechnicalToolkit - Market Analyst data bridge.

Source (per CHECKLIST #77): TRADINGAGENTS_DATA_AUDIT.md Section 20.

Bridges TradingAgents Market Analyst to our project's technical signal
layer (backtest/signals/technical.py + backtest/signals/screener.py)
and Polygon OHLCV cache (data_prefetch/polygon/ohlcv_daily/).

Sprint 7 Phase A scope (Batch 350): 5 methods covering the highest-impact
technical inputs per audit doc:
  - get_polygon_ohlcv(ticker, start, end) - cached daily bars (DEC-440)
  - get_technical_signals(ticker, as_of) - full 270+-signal dict from
    compute_all_signals()
  - get_regime_context(as_of) - DEC-106 regime classifier output
  - get_liquidity_metrics(ticker, as_of) - ADV / dollar volume per DEC-366
  - get_sector_relative_strength(ticker, as_of) - vs sector ETF (DEC-118)

Deferred to subsequent batches (not needed for Phase A scaffold):
  - get_intraday_ohlcv (Polygon 1H/4H bars - not yet prefetched)
  - get_ict_smc_signals (smartmoneyconcepts wrapper - Phase A library
    work still IN PROGRESS per vendored/MANIFEST.md)
  - get_chart_pattern_signals (DEC-355-362 deduplication batch)
  - get_volume_profile (computed inline by compute_all_signals)
  - get_multi_timeframe_regime (DEC-106 covered by get_regime_context)
  - get_break_and_retest_signal (BUG-111 RESOLVED Batch 339)
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd


_OHLCV_DIR = Path(__file__).resolve().parents[3] / "data_prefetch" / "polygon" / "ohlcv_daily"


class OurTechnicalToolkit:
    """Market Analyst toolkit. PIT-correct by construction.

    Methods return dict payloads suitable for inclusion in an LLM prompt
    or as structured tool-call results. Cache-miss returns `{}` or
    `{"error": "..."}` rather than raising; this keeps the agent graph
    resilient when a single ticker has data gaps.
    """

    def __init__(self, ohlcv_dir: Path | None = None) -> None:
        self.ohlcv_dir = ohlcv_dir or _OHLCV_DIR

    def get_polygon_ohlcv(self, ticker: str, start: date, end: date) -> dict[str, Any]:
        """Return daily OHLCV bars from cached parquet within [start, end].

        Returns:
            dict with keys:
              - ticker
              - n_bars
              - first_date / last_date (ISO strings)
              - last_close / last_volume
              - error (only when cache missing)
        """
        ticker_safe = ticker.replace(".", "-")
        path = self.ohlcv_dir / f"{ticker_safe}.parquet"
        if not path.exists():
            return {"ticker": ticker, "error": "cache_miss"}
        try:
            df = pd.read_parquet(path)
        except Exception as e:
            return {"ticker": ticker, "error": f"parquet_read_error: {e}"}
        if df.empty:
            return {"ticker": ticker, "error": "empty_parquet"}
        date_col = "date" if "date" in df.columns else None
        if date_col is None and isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index().rename(columns={"index": "date"})
            date_col = "date"
        if date_col is None:
            return {"ticker": ticker, "error": "no_date_column"}
        df[date_col] = pd.to_datetime(df[date_col]).dt.date
        sub = df[(df[date_col] >= start) & (df[date_col] <= end)]
        if sub.empty:
            return {"ticker": ticker, "n_bars": 0, "error": "no_bars_in_window"}
        last = sub.iloc[-1]
        return {
            "ticker": ticker,
            "n_bars": int(len(sub)),
            "first_date": sub.iloc[0][date_col].isoformat(),
            "last_date": last[date_col].isoformat(),
            "last_close": float(last["close"]) if "close" in last else None,
            "last_volume": int(last["volume"]) if "volume" in last and not pd.isna(last["volume"]) else None,
        }

    def get_technical_signals(self, ticker: str, as_of: date) -> dict[str, Any]:
        """Return our 270+-signal dict for the ticker at as_of.

        Bridges to backtest.signals.screener.compute_all_signals after
        truncating the OHLCV df to as_of. Returns subset of signals most
        useful to Market Analyst (avoids dumping all 270 into LLM context).

        Returns:
            dict with keys: ticker, as_of, n_signals, signals (subset).
        """
        ticker_safe = ticker.replace(".", "-")
        path = self.ohlcv_dir / f"{ticker_safe}.parquet"
        if not path.exists():
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "cache_miss"}
        try:
            df = pd.read_parquet(path)
        except Exception as e:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": f"parquet_read_error: {e}"}

        date_col = "date" if "date" in df.columns else None
        if date_col is None and isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index().rename(columns={"index": "date"})
            date_col = "date"
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col]).dt.date
            df = df[df[date_col] <= as_of]
        if len(df) < 30:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "insufficient_history"}

        try:
            from backtest.signals.screener import compute_all_signals
            all_signals = compute_all_signals(df)
        except Exception as e:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": f"compute_error: {e}"}

        if not all_signals:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "n_signals": 0, "signals": {}}

        # Subset to Market-Analyst-relevant keys (avoid dumping 270 into prompt)
        relevant_prefixes = (
            "rsi_", "macd_", "ema_", "sma_", "above_", "below_", "trend_",
            "vol_", "atr_", "bb_", "donchian_", "supertrend_", "ichimoku_",
            "adx_", "obv_", "cmf_", "vwap", "regime_", "gap_", "candle_",
        )
        subset = {k: v for k, v in all_signals.items()
                  if any(k.startswith(p) for p in relevant_prefixes)}
        return {
            "ticker": ticker,
            "as_of": as_of.isoformat(),
            "n_signals": len(all_signals),
            "n_subset": len(subset),
            "signals": subset,
        }

    def get_regime_context(self, as_of: date) -> dict[str, Any]:
        """Return DEC-106 regime classifier output for the trading date.

        Bridges to backtest.engine.regime_filter.classify_regime.

        Returns:
            dict with keys: as_of, regime, vix_value, spy_above_200ema,
            crisis_flag.
        """
        try:
            from backtest.data.macro import macro_snapshot
            from backtest.engine.regime_filter import classify_regime
        except Exception as e:
            return {"as_of": as_of.isoformat(), "error": f"import_error: {e}"}

        try:
            macro = macro_snapshot(as_of)
        except Exception as e:
            return {"as_of": as_of.isoformat(), "error": f"macro_snapshot_error: {e}"}

        vix = macro.get("vix_value")
        try:
            regime = classify_regime(spy_close=None, spy_ema200=None, vix=vix, vix_smoothed=None, prev_regime=None)
        except Exception:
            regime = "unknown"

        return {
            "as_of": as_of.isoformat(),
            "regime": regime,
            "vix_value": vix,
            "hy_oas": macro.get("hy_oas"),
            "t10y2y": macro.get("t10y2y"),
        }

    def get_liquidity_metrics(self, ticker: str, as_of: date, lookback_days: int = 20) -> dict[str, Any]:
        """Return ADV and dollar-volume metrics for liquidity gate (DEC-366).

        Returns:
            dict with keys: ticker, as_of, adv_20d, dollar_volume_20d_mean,
            last_close.
        """
        ticker_safe = ticker.replace(".", "-")
        path = self.ohlcv_dir / f"{ticker_safe}.parquet"
        if not path.exists():
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "cache_miss"}
        try:
            df = pd.read_parquet(path)
        except Exception as e:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": f"parquet_read_error: {e}"}

        date_col = "date" if "date" in df.columns else None
        if date_col is None and isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index().rename(columns={"index": "date"})
            date_col = "date"
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col]).dt.date
            df = df[df[date_col] <= as_of]
        sub = df.tail(lookback_days)
        if len(sub) < 5:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "insufficient_history"}
        adv = float(sub["volume"].mean())
        dv = float((sub["close"] * sub["volume"]).mean())
        last_close = float(sub.iloc[-1]["close"])
        return {
            "ticker": ticker,
            "as_of": as_of.isoformat(),
            "adv_20d": adv,
            "dollar_volume_20d_mean": dv,
            "last_close": last_close,
        }

    def get_sector_relative_strength(
        self, ticker: str, sector_etf: str, as_of: date, lookback_days: int = 60
    ) -> dict[str, Any]:
        """Return ticker's relative-strength vs sector ETF over lookback.

        RS = (ticker_return - etf_return) over lookback_days bars. Positive
        RS means ticker is outperforming sector.

        Returns:
            dict with keys: ticker, sector_etf, as_of, lookback_days,
            ticker_return_pct, etf_return_pct, rs_pct.
        """
        def _load_returns(t: str) -> tuple[float, float] | None:
            t_safe = t.replace(".", "-")
            path = self.ohlcv_dir / f"{t_safe}.parquet"
            if not path.exists():
                return None
            try:
                d = pd.read_parquet(path)
            except Exception:
                return None
            date_col = "date" if "date" in d.columns else None
            if date_col is None and isinstance(d.index, pd.DatetimeIndex):
                d = d.reset_index().rename(columns={"index": "date"})
                date_col = "date"
            if date_col:
                d[date_col] = pd.to_datetime(d[date_col]).dt.date
                d = d[d[date_col] <= as_of]
            sub = d.tail(lookback_days)
            if len(sub) < 5:
                return None
            first = float(sub.iloc[0]["close"])
            last = float(sub.iloc[-1]["close"])
            if first <= 0:
                return None
            return ((last / first) - 1.0) * 100.0, last

        t_data = _load_returns(ticker)
        e_data = _load_returns(sector_etf)
        if t_data is None or e_data is None:
            return {
                "ticker": ticker, "sector_etf": sector_etf, "as_of": as_of.isoformat(),
                "error": "data_unavailable",
            }
        t_ret, _ = t_data
        e_ret, _ = e_data
        return {
            "ticker": ticker,
            "sector_etf": sector_etf,
            "as_of": as_of.isoformat(),
            "lookback_days": lookback_days,
            "ticker_return_pct": round(t_ret, 3),
            "etf_return_pct": round(e_ret, 3),
            "rs_pct": round(t_ret - e_ret, 3),
        }
