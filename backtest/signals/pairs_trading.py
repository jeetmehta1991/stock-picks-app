"""Cointegration-based pairs trading helpers.

Batch 229 (2026-05-18 owner-approved deferred-items implementation; safe
to build in parallel with Batch 225 final rerun because it does not
mutate any running-engine module).

Source: Krauss 2017/2024 *Journal of Economic Surveys* "Statistical
Arbitrage Pairs Trading Strategies: Review and Outlook"; Gatev-
Goetzmann-Rouwenhorst 2006 *RFS* "Pairs Trading: Performance of a
Relative-Value Arbitrage Rule".

Pairs trading is **market-neutral** by construction - long one stock /
short the cointegrated counterpart. Per the research review (section
A.1 item #12), this fills a gap in our long-bias roster: documented
Sharpe 0.6-0.9 net of HFT impact, low correlation with single-stock
momentum / mean-reversion strategies.

Mechanism:
  1. For each candidate pair (within sector to maximize cointegration
     probability): test Engle-Granger cointegration on log-prices
  2. If p < 0.05 AND half-life of mean reversion in [5, 30] trading
     days (Krauss 2024 "slow mean-reversion" filter that survives
     post-HFT) -> keep pair
  3. Compute spread z-score: z_t = (spread_t - mean_60d) / std_60d
  4. Entry: |z| > 2.0 -> long the underpriced leg, short the overpriced
  5. Exit: z crosses 0 (mean reversion) OR |z| > 4.0 (stop-out;
     cointegration may have broken)

This module computes the COINTEGRATION TEST + HALF-LIFE + Z-SCORE only.
Strategy registration is deferred to post-Batch-225 to avoid touching
screener.py during the running rerun.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

import numpy as np
import pandas as pd


def engle_granger_cointegration(
    series_a: pd.Series,
    series_b: pd.Series,
    significance: float = 0.05,
) -> dict:
    """Engle-Granger 2-step cointegration test on two price series.

    Step 1: OLS regression of series_a on series_b -> residuals
    Step 2: ADF test on residuals -> reject H0 (residuals unit-root) =
            cointegrated

    Returns dict:
      - cointegrated:    bool (residual ADF p < significance)
      - hedge_ratio:     float (OLS slope of series_a ~ series_b)
      - intercept:       float (OLS intercept)
      - adf_pvalue:      float (residual stationarity test p-value)
      - residuals:       pd.Series (in-sample regression residuals)
      - note:            str

    Returns {"cointegrated": False, ...} on insufficient data / NaN
    contamination / statsmodels unavailable (defensive).
    """
    if series_a is None or series_b is None:
        return {"cointegrated": False, "hedge_ratio": None,
                "intercept": None, "adf_pvalue": None,
                "residuals": None, "note": "null_input"}
    # Align indices
    df = pd.concat([series_a.rename("a"), series_b.rename("b")],
                    axis=1, join="inner").dropna()
    if len(df) < 60:
        return {"cointegrated": False, "hedge_ratio": None,
                "intercept": None, "adf_pvalue": None,
                "residuals": None, "note": "insufficient_overlap"}
    try:
        from statsmodels.regression.linear_model import OLS
        from statsmodels.tsa.stattools import adfuller
        from statsmodels.tools.tools import add_constant
    except ImportError:
        return {"cointegrated": False, "hedge_ratio": None,
                "intercept": None, "adf_pvalue": None,
                "residuals": None, "note": "statsmodels_unavailable"}
    try:
        x = add_constant(df["b"].values)
        result = OLS(df["a"].values, x).fit()
        intercept, hedge_ratio = float(result.params[0]), float(result.params[1])
        residuals = pd.Series(
            df["a"].values - (intercept + hedge_ratio * df["b"].values),
            index=df.index,
        )
        adf_stat, adf_p, *_ = adfuller(residuals.values, autolag="AIC")
        is_coint = bool(adf_p < significance)
        return {
            "cointegrated": is_coint,
            "hedge_ratio":  round(hedge_ratio, 4),
            "intercept":    round(intercept, 4),
            "adf_pvalue":   round(float(adf_p), 4),
            "residuals":    residuals,
            "note":         "ok" if is_coint else "not_cointegrated",
        }
    except Exception as e:
        return {"cointegrated": False, "hedge_ratio": None,
                "intercept": None, "adf_pvalue": None,
                "residuals": None, "note": f"error_{type(e).__name__}"}


def spread_half_life(residuals: pd.Series) -> Optional[float]:
    """Compute the OU mean-reversion half-life of a residuals series.

    Half-life = log(2) / |theta| where theta is the AR(1) coefficient
    from residual ~ residual_lag1 regression. Krauss 2024 filter:
    survive HFT post-2010 requires half-life in [5, 30] trading days
    (faster pairs are arbitraged away).

    Returns None on degenerate input.
    """
    if residuals is None or len(residuals) < 10:
        return None
    try:
        from statsmodels.regression.linear_model import OLS
        from statsmodels.tools.tools import add_constant
    except ImportError:
        return None
    try:
        s = residuals.dropna()
        if len(s) < 10:
            return None
        # Lagged regression: delta_s_t = theta * s_{t-1} + epsilon
        delta = s.diff().dropna()
        lag = s.shift(1).dropna()
        common = pd.concat([delta, lag.rename("lag")], axis=1, join="inner").dropna()
        if len(common) < 10:
            return None
        x = add_constant(common["lag"].values)
        res = OLS(common.iloc[:, 0].values, x).fit()
        theta = float(res.params[1])
        if theta >= 0:
            # No mean-reversion (random walk or trending)
            return None
        half_life = float(np.log(2.0) / abs(theta))
        return round(half_life, 2)
    except Exception:
        return None


def pair_zscore(
    series_a: pd.Series,
    series_b: pd.Series,
    hedge_ratio: float,
    intercept: float,
    window: int = 60,
) -> Optional[float]:
    """Compute the current spread z-score for an entry/exit signal.

    spread_t = series_a_t - (intercept + hedge_ratio * series_b_t)
    z_t = (spread_t - rolling_mean_window) / rolling_std_window

    Returns latest z-score float, or None on insufficient data.
    """
    if series_a is None or series_b is None:
        return None
    df = pd.concat([series_a, series_b], axis=1, join="inner").dropna()
    if len(df) < window + 1:
        return None
    spread = df.iloc[:, 0] - (intercept + hedge_ratio * df.iloc[:, 1])
    if len(spread) < window:
        return None
    rolling_mean = spread.rolling(window).mean()
    rolling_std = spread.rolling(window).std()
    last_spread = float(spread.iloc[-1])
    last_mean = float(rolling_mean.iloc[-1])
    last_std = float(rolling_std.iloc[-1])
    if not (last_std > 0):
        return None
    return round((last_spread - last_mean) / last_std, 4)


def find_cointegrated_pairs(
    closes: pd.DataFrame,
    significance: float = 0.05,
    min_half_life: int = 5,
    max_half_life: int = 30,
    max_pairs: int = 100,
) -> list:
    """Identify all cointegrated pairs in a closes-matrix.

    Inputs:
      closes:     DataFrame indexed by date, columns = tickers, values = close
      significance: ADF p-value threshold (default 0.05)
      min_half_life / max_half_life: post-HFT-survival window (default 5-30 days)
      max_pairs:  return top-N pairs ranked by ADF p-value (default 100)

    Returns list of dicts: [{ticker_a, ticker_b, hedge_ratio, intercept,
                              adf_pvalue, half_life, note}, ...]

    Defensive: returns [] when input empty or fewer than 2 tickers.
    Pairwise complexity O(N^2 * cointegration_test_cost); typical 100-
    ticker universe with 252-day window completes in 30-90s.
    """
    if closes is None or closes.empty or closes.shape[1] < 2:
        return []
    tickers = list(closes.columns)
    pairs = []
    for i in range(len(tickers)):
        for j in range(i + 1, len(tickers)):
            t_a, t_b = tickers[i], tickers[j]
            result = engle_granger_cointegration(
                closes[t_a].apply(np.log),
                closes[t_b].apply(np.log),
                significance=significance,
            )
            if not result["cointegrated"]:
                continue
            hl = spread_half_life(result["residuals"])
            if hl is None or hl < min_half_life or hl > max_half_life:
                continue
            pairs.append({
                "ticker_a":    t_a,
                "ticker_b":    t_b,
                "hedge_ratio": result["hedge_ratio"],
                "intercept":   result["intercept"],
                "adf_pvalue":  result["adf_pvalue"],
                "half_life":   hl,
                "note":        "post_hft_survivor",
            })
    pairs.sort(key=lambda p: p["adf_pvalue"])
    return pairs[:max_pairs]
