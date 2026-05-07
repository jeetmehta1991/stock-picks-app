"""DEC-513 extended signals (Pass 53 Day-9 v8g — owner-approved 2026-05-06 Q3 P0).

Spec source: TRADING_RULES_AND_INFORMATION.md §2A.10.

Additive signal-computing helpers. Each function takes an OHLCV DataFrame
(DatetimeIndex + open/high/low/close/volume) and returns a dict of computed
signals as_of the LAST bar in the DataFrame. Callers slice df to as_of for
PIT correctness.

Implemented (7 of 10 — Pass 53 Day-9 v8h evening adds #2 + #7):
  #1 compute_realized_vol           — 3 horizons (10d/20d/60d annualized)
  #2 compute_betas                  — rolling beta + R² vs market (60d/252d) + sector ETF
  #5 compute_overnight_intraday_split — overnight vs intraday return decomposition
  #6 compute_gaps                    — gap size, bucket, fill outcomes T+1/T+3/T+5
  #7 compute_vix_term_structure     — VIX1M vs VIX3M (premium + ratio + regime)
  #8 compute_extremes                — 52w/20d/252d high/low distance
  #10 attach_signal_age              — universal age field

Deferred (still require new prefetched data not yet available):
  #3 compute_factor_exposures — needs FF3 factor returns prefetch
  #4 compute_correlation_matrix — DONE elsewhere (correlation_cluster.py per DEC-509)
  #9 FINRA short interest    — new data source not in prefetch
"""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd


_TRADING_DAYS_YEAR = 252


# ---------------------------------------------------------------------------
# DEC-513 #1 — Realized volatility (3 horizons)
# ---------------------------------------------------------------------------
def compute_realized_vol(df: pd.DataFrame) -> Dict[str, float]:
    """Annualized stddev of daily simple returns over 10d/20d/60d windows.

    Returns dict with realized_vol_10d, realized_vol_20d, realized_vol_60d.
    Values are unitless (e.g. 0.20 = 20% annualized vol). NaN for windows
    with insufficient history.
    """
    if df is None or "close" not in df.columns or len(df) < 11:
        return {"realized_vol_10d": float("nan"),
                "realized_vol_20d": float("nan"),
                "realized_vol_60d": float("nan")}
    rets = df["close"].pct_change().dropna()
    out = {}
    for w in (10, 20, 60):
        sliced = rets.tail(w)
        if len(sliced) < w:
            out[f"realized_vol_{w}d"] = float("nan")
            continue
        out[f"realized_vol_{w}d"] = float(sliced.std() * np.sqrt(_TRADING_DAYS_YEAR))
    return out


# ---------------------------------------------------------------------------
# DEC-513 #2 — Rolling betas vs market + sector ETF
# ---------------------------------------------------------------------------
def compute_betas(df: pd.DataFrame,
                  market_df: pd.DataFrame,
                  sector_df: pd.DataFrame | None = None) -> Dict[str, float]:
    """Rolling beta + R² of stock vs market and optional sector ETF.

    beta = cov(stock_rets, bench_rets) / var(bench_rets)
    R²   = corr(stock_rets, bench_rets) ** 2

    Computed over 60d and 252d windows on simple daily returns. All series
    are aligned on common dates before fitting; if alignment yields fewer
    than the window size, that horizon returns NaN.

    Args:
        df: stock OHLCV with close column (DatetimeIndex).
        market_df: market benchmark OHLCV with close column (e.g. SPY).
        sector_df: optional sector ETF OHLCV with close column.

    Returns dict:
        beta_market_60d, beta_market_252d, r2_market_60d, r2_market_252d,
        beta_sector_60d, beta_sector_252d, r2_sector_60d, r2_sector_252d
        (sector_* are NaN when sector_df is None).
    """
    nan_keys = {
        "beta_market_60d": float("nan"), "beta_market_252d": float("nan"),
        "r2_market_60d":  float("nan"), "r2_market_252d":  float("nan"),
        "beta_sector_60d": float("nan"), "beta_sector_252d": float("nan"),
        "r2_sector_60d":  float("nan"), "r2_sector_252d":  float("nan"),
    }
    if df is None or "close" not in df.columns or len(df) < 11:
        return nan_keys
    if market_df is None or "close" not in market_df.columns or len(market_df) < 11:
        return nan_keys

    stock_rets = df["close"].pct_change()
    market_rets = market_df["close"].pct_change()
    aligned = pd.concat([stock_rets, market_rets], axis=1, keys=["s", "m"]).dropna()

    out = dict(nan_keys)
    for w in (60, 252):
        if len(aligned) < w:
            continue
        sliced = aligned.tail(w)
        var_m = sliced["m"].var()
        if var_m and var_m > 1e-12:
            cov_sm = sliced["s"].cov(sliced["m"])
            corr_sm = sliced["s"].corr(sliced["m"])
            out[f"beta_market_{w}d"] = float(cov_sm / var_m)
            out[f"r2_market_{w}d"] = float(corr_sm * corr_sm) if pd.notna(corr_sm) else float("nan")

    if sector_df is not None and "close" in sector_df.columns and len(sector_df) >= 11:
        sector_rets = sector_df["close"].pct_change()
        aligned_sec = pd.concat([stock_rets, sector_rets], axis=1, keys=["s", "x"]).dropna()
        for w in (60, 252):
            if len(aligned_sec) < w:
                continue
            sliced = aligned_sec.tail(w)
            var_x = sliced["x"].var()
            if var_x and var_x > 1e-12:
                cov_sx = sliced["s"].cov(sliced["x"])
                corr_sx = sliced["s"].corr(sliced["x"])
                out[f"beta_sector_{w}d"] = float(cov_sx / var_x)
                out[f"r2_sector_{w}d"] = float(corr_sx * corr_sx) if pd.notna(corr_sx) else float("nan")

    return out


# ---------------------------------------------------------------------------
# DEC-513 #5 — Overnight vs intraday return decomposition
# ---------------------------------------------------------------------------
def compute_overnight_intraday_split(df: pd.DataFrame) -> Dict[str, float]:
    """Decompose total return into overnight and intraday components.

    overnight_return  = open_t / close_{t-1} - 1   (gap)
    intraday_return   = close_t / open_t - 1       (within-bar)
    overnight_intraday_ratio_20d = mean(overnight_20d) / mean(intraday_20d)

    Returns most-recent bar's overnight/intraday return + 20d ratio.
    NaN for any field that cannot be computed (insufficient history,
    division by zero).
    """
    if df is None or len(df) < 21 or not {"open", "close"}.issubset(df.columns):
        return {"overnight_return": float("nan"),
                "intraday_return": float("nan"),
                "overnight_intraday_ratio_20d": float("nan")}
    o = df["open"]
    c = df["close"]
    prev_c = c.shift(1)
    on = (o / prev_c - 1.0)
    intra = (c / o - 1.0)
    out = {
        "overnight_return": float(on.iloc[-1]) if pd.notna(on.iloc[-1]) else float("nan"),
        "intraday_return":  float(intra.iloc[-1]) if pd.notna(intra.iloc[-1]) else float("nan"),
    }
    on_20 = on.tail(20).mean()
    intra_20 = intra.tail(20).mean()
    if pd.notna(on_20) and pd.notna(intra_20) and abs(intra_20) > 1e-9:
        out["overnight_intraday_ratio_20d"] = float(on_20 / intra_20)
    else:
        out["overnight_intraday_ratio_20d"] = float("nan")
    return out


# ---------------------------------------------------------------------------
# DEC-513 #6 — Gap classification + fill outcomes
# ---------------------------------------------------------------------------
def compute_gaps(df: pd.DataFrame) -> Dict[str, float]:
    """Classify gap on the most-recent bar and report whether it filled in
    the next 1/3/5 bars.

    Output keys:
      gap_size_pct       — (open / prev_close - 1) × 100; sign indicates direction
      gap_size_bucket    — 'small' (<1%), 'medium' (1-3%), 'large' (>3%)
      gap_filled_T1/T3/T5 — bool: did price retrace through prev_close within
                            the next 1/3/5 bars (0 if no future data)?

    Returns NaN-equivalent (None) for fill flags when insufficient future data.
    """
    if df is None or len(df) < 2 or not {"open", "high", "low", "close"}.issubset(df.columns):
        return {"gap_size_pct": float("nan"), "gap_size_bucket": "unknown",
                "gap_filled_T1": False, "gap_filled_T3": False,
                "gap_filled_T5": False}
    # Most-recent bar's gap = open vs prev close.
    # NB: with only the gap day in the slice and no T+N future, fills can't
    # be evaluated. Caller should pass a slice that includes T+5 to get
    # fill flags. If insufficient future data, returns False (not yet filled).
    last_idx = len(df) - 1
    gap_idx = last_idx
    if gap_idx == 0:
        return {"gap_size_pct": float("nan"), "gap_size_bucket": "unknown",
                "gap_filled_T1": False, "gap_filled_T3": False,
                "gap_filled_T5": False}
    prev_close = float(df["close"].iloc[gap_idx - 1])
    gap_open = float(df["open"].iloc[gap_idx])
    if prev_close <= 0:
        return {"gap_size_pct": float("nan"), "gap_size_bucket": "unknown",
                "gap_filled_T1": False, "gap_filled_T3": False,
                "gap_filled_T5": False}
    gap_pct = (gap_open / prev_close - 1.0) * 100.0
    abs_pct = abs(gap_pct)
    if abs_pct < 1.0:
        bucket = "small"
    elif abs_pct < 3.0:
        bucket = "medium"
    else:
        bucket = "large"

    # Fill check: did intraday range from gap_idx..gap_idx+N include prev_close?
    out = {"gap_size_pct": float(gap_pct), "gap_size_bucket": bucket,
           "gap_filled_T1": False, "gap_filled_T3": False,
           "gap_filled_T5": False}
    for n, key in [(1, "gap_filled_T1"), (3, "gap_filled_T3"), (5, "gap_filled_T5")]:
        end_idx = min(gap_idx + n, len(df) - 1)
        if end_idx <= gap_idx:
            # No future data
            continue
        sliced = df.iloc[gap_idx:end_idx + 1]
        # Filled if any subsequent bar's intraday range crosses prev_close
        # For gap-up: low touches prev_close (or below)
        # For gap-down: high touches prev_close (or above)
        if gap_pct > 0:
            filled = (sliced["low"] <= prev_close).any()
        elif gap_pct < 0:
            filled = (sliced["high"] >= prev_close).any()
        else:
            filled = True  # zero gap auto-"filled"
        out[key] = bool(filled)
    return out


# ---------------------------------------------------------------------------
# DEC-513 #7 — VIX term structure (1M vs 3M)
# ---------------------------------------------------------------------------
def compute_vix_term_structure(vix_df: pd.DataFrame,
                                vix3m_df: pd.DataFrame) -> Dict[str, float]:
    """VIX term-structure regime signal (1M vs 3M).

    Source: FRED VIXCLS (1M) and VXVCLS (3M) — both prefetched to
    ``data_prefetch/fred/observations/``. Caller passes per-series DataFrames
    sliced to the as_of date (PIT enforcement is the caller's responsibility).

    Returns most-recent observation:
        vix_spot              — VIX1M close (annualized %)
        vix_3m                — VIX3M close (annualized %)
        vix_term_premium      — vix_3m - vix_spot (positive = contango/normal,
                                 negative = backwardation/stress)
        vix_term_ratio        — vix_3m / vix_spot
        vix_term_regime       — 'contango' (ratio > 1.05),
                                 'flat' (0.95 ≤ ratio ≤ 1.05),
                                 'backwardation' (ratio < 0.95)

    Schema is FRED-agnostic — accepts any DataFrame with a 'value' column or
    a single non-index column, as long as last row is the most-recent obs.
    """
    nan_out = {
        "vix_spot": float("nan"), "vix_3m": float("nan"),
        "vix_term_premium": float("nan"), "vix_term_ratio": float("nan"),
        "vix_term_regime": "unknown",
    }
    if vix_df is None or vix3m_df is None or len(vix_df) == 0 or len(vix3m_df) == 0:
        return nan_out

    def _last_value(s_df):
        if "value" in s_df.columns:
            v = s_df["value"].dropna()
        else:
            # FRED-style observation parquets sometimes have just one numeric col
            num_cols = [c for c in s_df.columns if pd.api.types.is_numeric_dtype(s_df[c])]
            if not num_cols:
                return float("nan")
            v = s_df[num_cols[0]].dropna()
        return float(v.iloc[-1]) if len(v) else float("nan")

    vix_spot = _last_value(vix_df)
    vix_3m = _last_value(vix3m_df)
    if not (pd.notna(vix_spot) and pd.notna(vix_3m) and vix_spot > 0):
        return nan_out

    premium = vix_3m - vix_spot
    ratio = vix_3m / vix_spot
    if ratio > 1.05:
        regime = "contango"
    elif ratio < 0.95:
        regime = "backwardation"
    else:
        regime = "flat"
    return {
        "vix_spot": vix_spot,
        "vix_3m": vix_3m,
        "vix_term_premium": float(premium),
        "vix_term_ratio": float(ratio),
        "vix_term_regime": regime,
    }


# ---------------------------------------------------------------------------
# DEC-513 #8 — 52-week / 20-day / 252-day distance continuous fields
# ---------------------------------------------------------------------------
def compute_extremes(df: pd.DataFrame) -> Dict[str, float]:
    """Continuous distance-from-extreme fields.

    Output keys (all percent-points unless noted):
      dist_from_52w_high_pct
      dist_from_52w_low_pct
      dist_from_20d_high_pct
      dist_from_20d_low_pct
      dist_from_252d_high_atr   — distance from 252d high in ATR multiples
      dist_from_252d_low_atr    — distance from 252d low in ATR multiples
      pct_to_52w_high           — (close/52w_high) ratio (0..1+)
      pct_to_52w_low            — (close/52w_low) ratio

    Conventions: dist_pct is signed; positive when below the high (price has
    room to rally) and negative when above (price extended).
    """
    if df is None or "close" not in df.columns or len(df) < 21:
        return {k: float("nan") for k in [
            "dist_from_52w_high_pct", "dist_from_52w_low_pct",
            "dist_from_20d_high_pct", "dist_from_20d_low_pct",
            "dist_from_252d_high_atr", "dist_from_252d_low_atr",
            "pct_to_52w_high", "pct_to_52w_low",
        ]}
    close = float(df["close"].iloc[-1])
    out = {}
    win_252 = df["high"].tail(_TRADING_DAYS_YEAR)  # 52w high using bar highs
    lo_252 = df["low"].tail(_TRADING_DAYS_YEAR)
    win_20_high = df["high"].tail(20)
    win_20_low = df["low"].tail(20)
    if len(win_252) and close > 0:
        h_252 = float(win_252.max())
        l_252 = float(lo_252.min())
        out["dist_from_52w_high_pct"] = (h_252 - close) / h_252 * 100.0 if h_252 > 0 else float("nan")
        out["dist_from_52w_low_pct"] = (close - l_252) / l_252 * 100.0 if l_252 > 0 else float("nan")
        out["pct_to_52w_high"] = float(close / h_252) if h_252 > 0 else float("nan")
        out["pct_to_52w_low"] = float(close / l_252) if l_252 > 0 else float("nan")
        # ATR-normalized distance
        from backtest.signals.dec513_extended_signals import _compute_atr_simple  # self-import OK at runtime
        atr_val = _compute_atr_simple(df.tail(min(252, len(df))))
        if atr_val and atr_val > 0:
            out["dist_from_252d_high_atr"] = (h_252 - close) / atr_val
            out["dist_from_252d_low_atr"] = (close - l_252) / atr_val
        else:
            out["dist_from_252d_high_atr"] = float("nan")
            out["dist_from_252d_low_atr"] = float("nan")
    else:
        for k in ["dist_from_52w_high_pct", "dist_from_52w_low_pct",
                   "pct_to_52w_high", "pct_to_52w_low",
                   "dist_from_252d_high_atr", "dist_from_252d_low_atr"]:
            out[k] = float("nan")
    if len(win_20_high) and close > 0:
        h_20 = float(win_20_high.max())
        l_20 = float(win_20_low.min())
        out["dist_from_20d_high_pct"] = (h_20 - close) / h_20 * 100.0 if h_20 > 0 else float("nan")
        out["dist_from_20d_low_pct"] = (close - l_20) / l_20 * 100.0 if l_20 > 0 else float("nan")
    else:
        out["dist_from_20d_high_pct"] = float("nan")
        out["dist_from_20d_low_pct"] = float("nan")
    return out


def _compute_atr_simple(df: pd.DataFrame, period: int = 14) -> float:
    """Simple EMA-ATR — duplicate of signals/technical.py to avoid import cycle."""
    if df is None or len(df) < period + 1:
        return float("nan")
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return float(tr.ewm(alpha=1 / period, adjust=False).mean().iloc[-1])


# ---------------------------------------------------------------------------
# DEC-513 #10 — Universal signal_age_days field
# ---------------------------------------------------------------------------
def attach_signal_age(signal_dict: dict, signal_date, as_of) -> dict:
    """Add ``signal_age_days = (as_of - signal_date).days`` to a signal dict.

    DEC-513 #10 schema additive — every signal output gets age_days populated
    so the strategy harness can age-weight or reject stale data uniformly.

    Args:
        signal_dict: dict to mutate (returned for chaining).
        signal_date: datetime/date of the underlying signal observation.
        as_of: cutoff date used when querying the signal (typically as_of).

    Returns the same dict with signal_age_days added.
    """
    from datetime import date, datetime
    if isinstance(signal_date, datetime):
        signal_date = signal_date.date()
    if isinstance(as_of, datetime):
        as_of = as_of.date()
    if isinstance(signal_date, date) and isinstance(as_of, date):
        signal_dict["signal_age_days"] = (as_of - signal_date).days
    else:
        signal_dict["signal_age_days"] = None
    return signal_dict
