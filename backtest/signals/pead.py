"""PEAD - Post-Earnings Announcement Drift signal computation.

Batch 209 (new strategy family 2026-05-17 owner-approved research review).
Implements the canonical Bernard-Thomas (1989) Post-Earnings Announcement
Drift effect using prefetched Polygon financials.

Mechanism (per Bernard-Thomas 1989 *Journal of Accounting Research*;
Garfinkel-Hribar-Hsiao 2024 update; CFA Institute "Can Generative AI
Disrupt PEAD?" 2025):
  - Stocks with strong positive earnings surprise continue to drift
    positively for 60 trading days post-announcement
  - Stocks with negative surprise drift negatively
  - Effect is robust across 30+ years of US equity data and remains
    statistically significant in 2024 backtests (Garfinkel et al.
    documented 5.1% 3-month risk-adjusted return on long-top-decile /
    short-bottom-decile = ~20% annualized)

Since Polygon Stocks Starter does NOT provide consensus EPS estimates
(would be needed for the SUE z-score formulation), this module uses the
Bernard-Thomas variant which only requires reported EPS:
  - YoY EPS growth (current quarter vs same quarter prior year)
  - Announcement-day return (close[T+1] / close[T-1] - 1) as a
    market-revealed surprise proxy
  - Combined signal: long when both YoY growth > 0 AND announcement
    return > +2%, within 60 trading days of filing
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd


_FINANCIALS_DIR = Path(__file__).parent.parent.parent / "data_prefetch" / "polygon" / "financials"


def _safe_eps(row: dict) -> Optional[float]:
    """Extract diluted EPS from a Polygon financials row's financials_json."""
    if not isinstance(row, dict):
        return None
    fin = row.get("income_statement", {}) if isinstance(row.get("income_statement"), dict) else {}
    eps_dict = fin.get("diluted_earnings_per_share") or fin.get("basic_earnings_per_share")
    if isinstance(eps_dict, dict) and "value" in eps_dict:
        try:
            return float(eps_dict["value"])
        except (TypeError, ValueError):
            return None
    return None


def load_quarterly_eps(ticker: str) -> pd.DataFrame:
    """Load quarterly EPS history from prefetched Polygon financials.

    Returns DataFrame with columns: [filing_date, fiscal_year,
    fiscal_period, eps]. Empty DataFrame on data miss or parse error.

    Skips TTM rows (only Q1/Q2/Q3/Q4 quarterly) and rows with NaN
    filing_date so YoY comparison is well-defined per quarter.
    """
    safe_ticker = ticker.replace(".", "-")
    fin_path = _FINANCIALS_DIR / f"{safe_ticker}.parquet"
    if not fin_path.exists():
        return pd.DataFrame(columns=["filing_date", "fiscal_year", "fiscal_period", "eps"])
    try:
        df = pd.read_parquet(fin_path)
    except Exception:
        return pd.DataFrame(columns=["filing_date", "fiscal_year", "fiscal_period", "eps"])
    if df.empty or "financials_json" not in df.columns:
        return pd.DataFrame(columns=["filing_date", "fiscal_year", "fiscal_period", "eps"])

    rows = []
    for _, r in df.iterrows():
        if pd.isna(r.get("filing_date")):
            continue
        period = r.get("fiscal_period")
        if period not in ("Q1", "Q2", "Q3", "Q4"):
            continue
        eps = _safe_eps(r.get("financials_json"))
        if eps is None:
            continue
        rows.append({
            "filing_date":   pd.to_datetime(r["filing_date"]).date(),
            "fiscal_year":   r.get("fiscal_year"),
            "fiscal_period": period,
            "eps":           eps,
        })
    if not rows:
        return pd.DataFrame(columns=["filing_date", "fiscal_year", "fiscal_period", "eps"])
    out = pd.DataFrame(rows).sort_values("filing_date").reset_index(drop=True)
    return out


def compute_pead_signals(
    ticker: str,
    ohlcv_df: pd.DataFrame,
    as_of: date,
    drift_window_days: int = 60,
    yoy_growth_threshold: float = 0.0,
    announcement_return_threshold: float = 0.02,
) -> dict:
    """Compute PEAD signals for a ticker as of a given date.

    Returns a dict suitable for merging into the signals dict consumed by
    screener strategies. Keys (all optional; absent when data missing):
      - days_since_last_earnings: int (trading days since most-recent
        earnings filing on/before as_of)
      - within_pead_window: bool (days_since <= drift_window_days)
      - earnings_eps_yoy_growth: float (current quarter EPS / same-quarter-
        prior-year EPS - 1). Defined when both quarters present in data.
      - earnings_announcement_return: float (close[T+1] / close[T-1] - 1)
      - pead_positive_surprise: bool (yoy_growth > threshold AND ann_return
        > threshold)
      - pead_negative_surprise: bool (yoy_growth < 0 AND ann_return < 0)

    Args:
      ticker:                     equity symbol
      ohlcv_df:                   OHLCV DataFrame for ticker (used to
                                  compute announcement-day return). Must
                                  have DatetimeIndex.
      as_of:                      current date in the backtest loop
      drift_window_days:          PEAD window per Bernard-Thomas (60d default)
      yoy_growth_threshold:       min YoY EPS growth for positive surprise
      announcement_return_threshold: min announcement-day return for
                                  positive surprise (default +2%)
    """
    eps_df = load_quarterly_eps(ticker)
    if eps_df.empty:
        return {}
    past = eps_df[eps_df["filing_date"] <= as_of]
    if past.empty:
        return {}
    most_recent = past.iloc[-1]
    last_filing = most_recent["filing_date"]
    # Use calendar-day delta as proxy for trading days (close enough for
    # 60-day window). Backtest engine already operates on business days
    # so as_of is itself a trading day.
    days_since = (as_of - last_filing).days
    out: dict = {
        "days_since_last_earnings": days_since,
        "within_pead_window":       days_since <= drift_window_days,
    }
    # YoY EPS growth: compare last_filing's quarter to same quarter 1 year ago
    target_period = most_recent["fiscal_period"]
    target_fy = most_recent["fiscal_year"]
    if pd.isna(target_fy):
        return out
    try:
        prior_year_match = past[
            (past["fiscal_period"] == target_period)
            & (past["fiscal_year"] == target_fy - 1)
        ]
    except (TypeError, ValueError):
        return out
    if prior_year_match.empty:
        return out
    prior_eps = float(prior_year_match.iloc[-1]["eps"])
    current_eps = float(most_recent["eps"])
    if prior_eps == 0:
        return out
    yoy_growth = (current_eps - prior_eps) / abs(prior_eps)
    out["earnings_eps_yoy_growth"] = round(yoy_growth, 4)
    # Announcement-day return: close[T+1] / close[T-1] - 1
    if ohlcv_df is not None and not ohlcv_df.empty:
        try:
            idx = ohlcv_df.index
            if hasattr(idx, "date"):
                dates_arr = pd.Series([d.date() if hasattr(d, "date") else d for d in idx])
            else:
                dates_arr = pd.Series(idx)
            target_pos = dates_arr[dates_arr == last_filing]
            if not target_pos.empty:
                pos = int(target_pos.index[0])
                if pos >= 1 and pos + 1 < len(ohlcv_df):
                    pre_close = float(ohlcv_df["close"].iloc[pos - 1])
                    post_close = float(ohlcv_df["close"].iloc[pos + 1])
                    if pre_close > 0:
                        ann_ret = (post_close - pre_close) / pre_close
                        out["earnings_announcement_return"] = round(ann_ret, 4)
        except Exception:
            pass
    # Combined surprise flags
    ann_ret = out.get("earnings_announcement_return")
    if ann_ret is not None:
        out["pead_positive_surprise"] = bool(
            yoy_growth > yoy_growth_threshold
            and ann_ret > announcement_return_threshold
        )
        out["pead_negative_surprise"] = bool(
            yoy_growth < -yoy_growth_threshold
            and ann_ret < -announcement_return_threshold
        )
    return out
