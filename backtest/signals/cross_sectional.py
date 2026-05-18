"""Cross-sectional factor features + factor strategies.

Batch 220 (2026-05-18 owner-approved research review Top-5 #1). Adds
the universe-wide pre-computation pass that lets factor strategies
read cross-sectional ranks per ticker. The current screener
architecture is per-ticker; factor strategies need to know each
ticker's rank within the FULL universe before deciding entry. This
module is called once per day in screen_universe BEFORE the per-ticker
iteration, then its dict-of-dicts output is merged into each ticker's
signals dict by screen_instrument.

Factors computed (all from daily OHLCV - no external data needed):
  - 12-1 momentum (Moskowitz-Ooi-Pedersen 2012 JFE; refreshed
    Goyal-Jegadeesh-Subrahmanyam 2024 RFS). Documented Sharpe 1.2-1.6
    net of costs across 1985-2023. Skip last 21 days to avoid
    short-term reversal contamination.
  - Beta vs SPY (Frazzini-Pedersen 2014 JFE "Betting Against Beta";
    Blitz-van Vliet 2024 JPM update). Low-beta names systematically
    outperform on a risk-adjusted basis.
  - Idiosyncratic volatility / IVOL (Ang-Hodrick-Xing-Zhang 2006 JF;
    Stambaugh-Yuan 2024 RFS). High-IVOL stocks systematically
    underperform - used as a NEGATIVE filter.
  - MAX-anomaly (Bali-Cakici-Whitelaw 2011 JFE "Maxing out: Stocks
    as lotteries"). Stocks with highest single-day return last month
    underperform - used as a NEGATIVE filter.

Output keys merged into per-ticker signals dict:
  - xs_momentum_12_1:        float (12-1 momentum, decimal)
  - xs_momentum_decile:      int 1-10 (1=lowest, 10=highest)
  - xs_momentum_top_decile:  bool (xs_momentum_decile == 10)
  - xs_beta:                 float (rolling 252-day beta vs SPY)
  - xs_beta_decile:          int 1-10
  - xs_low_beta_decile:      bool (xs_beta_decile <= 2, lowest 20%)
  - xs_ivol:                 float (60-day idiosyncratic vol)
  - xs_ivol_decile:          int 1-10
  - xs_avoid_high_ivol:      bool (xs_ivol_decile <= 8, i.e. NOT top 20%)
  - xs_max_anomaly:          float (max single-day return last 21 days)
  - xs_max_anomaly_decile:   int 1-10
  - xs_avoid_high_max:       bool (xs_max_anomaly_decile <= 8)
"""

from __future__ import annotations

from datetime import date
from typing import Dict, Optional

import numpy as np
import pandas as pd


def compute_cross_sectional_features(
    ohlcv_dict: dict,
    as_of: date,
    momentum_lookback: int = 252,
    momentum_skip: int = 21,
    beta_lookback: int = 252,
    ivol_lookback: int = 60,
    max_anomaly_lookback: int = 21,
    benchmark: str = "SPY",
    min_history: int = 252,
) -> Dict[str, dict]:
    """Compute cross-sectional factor features for every ticker in the universe.

    Returns dict-of-dicts: {ticker: {xs_momentum_12_1: ..., xs_momentum_decile: ..., ...}}.
    Tickers with insufficient history are absent from the output (caller's
    per-ticker .get() fallback to default).

    Defensive: empty dict on missing benchmark / empty universe / all-NaN factor.
    """
    if ohlcv_dict is None or not ohlcv_dict:
        return {}
    # Slice each ticker's OHLCV to as_of-or-before for PIT correctness
    # Build wide closes DataFrame: rows=dates, cols=tickers, values=close
    closes_by_ticker = {}
    for ticker, df in ohlcv_dict.items():
        if df is None or df.empty or "close" not in df.columns:
            continue
        if hasattr(df.index, "date"):
            sliced = df[df.index.date <= as_of]
        else:
            sliced = df[df.index <= as_of]
        if len(sliced) < min_history:
            continue
        closes_by_ticker[ticker] = sliced["close"].astype(float)
    if not closes_by_ticker:
        return {}
    closes = pd.DataFrame(closes_by_ticker)
    # Align to common index (forward-fill across tickers; HRP / factor
    # studies typically tolerate small alignment gaps).
    closes = closes.sort_index()
    out: Dict[str, dict] = {ticker: {} for ticker in closes.columns}

    # 12-1 momentum (skip last momentum_skip days)
    if len(closes) >= momentum_lookback:
        try:
            price_skip = closes.iloc[-1 - momentum_skip] if momentum_skip > 0 else closes.iloc[-1]
            price_lookback = closes.iloc[-momentum_lookback]
            mom_12_1 = (price_skip / price_lookback - 1.0).dropna()
            if not mom_12_1.empty:
                deciles = _safe_decile(mom_12_1)
                for ticker in mom_12_1.index:
                    out.setdefault(ticker, {})
                    out[ticker]["xs_momentum_12_1"] = round(float(mom_12_1[ticker]), 4)
                    if ticker in deciles.index:
                        d = int(deciles[ticker])
                        out[ticker]["xs_momentum_decile"] = d
                        out[ticker]["xs_momentum_top_decile"] = (d == 10)
                        out[ticker]["xs_momentum_bottom_decile"] = (d == 1)
        except Exception:
            pass

    # Beta vs benchmark (rolling 252-day OLS regression of returns)
    if benchmark in closes.columns and len(closes) >= beta_lookback:
        try:
            returns = closes.pct_change().dropna(how="all")
            bench_ret = returns[benchmark].tail(beta_lookback)
            if len(bench_ret) >= 30:
                bench_var = float(bench_ret.var())
                if bench_var > 0:
                    betas = {}
                    for ticker in returns.columns:
                        if ticker == benchmark:
                            continue
                        tkr_ret = returns[ticker].tail(beta_lookback)
                        common = pd.concat([tkr_ret, bench_ret], axis=1, join="inner").dropna()
                        if len(common) < 30:
                            continue
                        cov_val = float(common.iloc[:, 0].cov(common.iloc[:, 1]))
                        betas[ticker] = cov_val / bench_var
                    if betas:
                        beta_s = pd.Series(betas)
                        beta_deciles = _safe_decile(beta_s)
                        for ticker, b in beta_s.items():
                            out.setdefault(ticker, {})
                            out[ticker]["xs_beta"] = round(float(b), 4)
                            if ticker in beta_deciles.index:
                                d = int(beta_deciles[ticker])
                                out[ticker]["xs_beta_decile"] = d
                                out[ticker]["xs_low_beta_decile"] = (d <= 2)
                                out[ticker]["xs_high_beta_decile"] = (d >= 9)
        except Exception:
            pass

    # Idiosyncratic volatility (Ang-Hodrick-Xing-Zhang 2006) - residual
    # vol from CAPM regression on rolling ivol_lookback window. We use
    # total vol as a tractable proxy when benchmark unavailable.
    if len(closes) >= ivol_lookback + 1:
        try:
            recent_returns = closes.tail(ivol_lookback + 1).pct_change().dropna(how="all")
            if benchmark in recent_returns.columns:
                bench_ret = recent_returns[benchmark]
                bench_var = float(bench_ret.var())
                ivol_map = {}
                for ticker in recent_returns.columns:
                    if ticker == benchmark:
                        continue
                    tkr_ret = recent_returns[ticker]
                    if tkr_ret.isna().any() or len(tkr_ret) < 20 or bench_var <= 0:
                        continue
                    # Residual = tkr_ret - beta * bench_ret
                    beta_local = float(tkr_ret.cov(bench_ret)) / bench_var
                    residual = tkr_ret - beta_local * bench_ret
                    ivol_map[ticker] = float(residual.std()) * np.sqrt(252.0)
                if ivol_map:
                    ivol_s = pd.Series(ivol_map).dropna()
                    if not ivol_s.empty:
                        ivol_deciles = _safe_decile(ivol_s)
                        for ticker, v in ivol_s.items():
                            out.setdefault(ticker, {})
                            out[ticker]["xs_ivol"] = round(float(v), 4)
                            if ticker in ivol_deciles.index:
                                d = int(ivol_deciles[ticker])
                                out[ticker]["xs_ivol_decile"] = d
                                # AVOID top-IVOL decile (Ang et al)
                                out[ticker]["xs_avoid_high_ivol"] = (d <= 8)
        except Exception:
            pass

    # MAX-anomaly (Bali-Cakici-Whitelaw 2011) - max single-day return
    # over last max_anomaly_lookback days
    if len(closes) >= max_anomaly_lookback + 2:
        try:
            recent_returns = closes.tail(max_anomaly_lookback + 1).pct_change().dropna(how="all")
            max_map = {}
            for ticker in recent_returns.columns:
                if ticker == benchmark:
                    continue
                ret_series = recent_returns[ticker].dropna()
                if len(ret_series) < 10:
                    continue
                max_map[ticker] = float(ret_series.max())
            if max_map:
                max_s = pd.Series(max_map).dropna()
                if not max_s.empty:
                    max_deciles = _safe_decile(max_s)
                    for ticker, v in max_s.items():
                        out.setdefault(ticker, {})
                        out[ticker]["xs_max_anomaly"] = round(float(v), 4)
                        if ticker in max_deciles.index:
                            d = int(max_deciles[ticker])
                            out[ticker]["xs_max_anomaly_decile"] = d
                            # AVOID top-MAX decile (lottery demand)
                            out[ticker]["xs_avoid_high_max"] = (d <= 8)
        except Exception:
            pass

    # Drop tickers with no factor features computed
    return {t: v for t, v in out.items() if v}


def _safe_decile(s: pd.Series) -> pd.Series:
    """Compute deciles (1-10) safely, handling duplicates.

    Returns int Series indexed by ticker; ranks 1=lowest, 10=highest.
    Falls back to qcut with duplicates='drop' or rank-based binning.
    """
    s = s.dropna()
    if s.empty:
        return pd.Series([], dtype=int)
    if len(s.unique()) < 10:
        # Too few unique values - use simple rank-based binning
        ranks = s.rank(method="first", pct=True)
        return (ranks * 10).clip(1, 10).round().astype(int)
    try:
        deciles = pd.qcut(s, 10, labels=range(1, 11), duplicates="drop")
        return deciles.astype(int)
    except Exception:
        ranks = s.rank(method="first", pct=True)
        return (ranks * 10).clip(1, 10).round().astype(int)
