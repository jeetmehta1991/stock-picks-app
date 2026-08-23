"""Cross-asset signals — Track A batch 232 parallel-safe module.

Batch 232 (2026-05-18 owner-approved deferred-items implementation;
parallel-safe with Batch 225 final rerun). Addresses DEC-369 Cross-Asset
strategies category.

Cross-asset signals capture relationships BETWEEN markets (equity /
bond / commodity / currency / volatility) that single-asset technical
indicators cannot see. Used as risk-on / risk-off regime context +
sector-rotation signals.

Documented effects + sources:

1. Bond/Equity ratio (TLT vs SPY)
   Source: Asness 2003 *Financial Analysts Journal* "Fight the Fed
   Model"; Connolly-Stivers-Sun 2005 *RFS*. When TLT outperforms SPY
   over rolling window, signals risk-off regime (flight to safety).
   Strategies: reduce equity gross exposure when bond/equity ratio
   trending up.

2. Sector relative strength (XLF/XLU/XLE/XLK vs SPY)
   Source: Connolly-Stivers-Sun 2005 RFS sector rotation work;
   Conover-Jensen-Johnson-Mercer 2008 *JoF* "Sector Rotation and
   Monetary Conditions". Defensive sectors (XLU utilities, XLP staples)
   outperform during contractions; cyclicals (XLY discretionary, XLI
   industrials) outperform during expansions.

3. VIX term structure (VIX9D / VIX / VIX3M)
   Source: Cheng 2019 *Journal of Financial Economics* "The VIX
   Premium". VIX < VIX3M = contango = normal complacency; VIX > VIX3M
   = backwardation = stress regime. Backwardation is the regime where
   short vol unwinds and longs benefit from convexity.

4. Gold/Silver ratio (GLD vs SLV)
   Source: Hammoudeh-Yuan 2008 *Resources Policy*. Rising ratio =
   risk-off (gold preferred to silver); falling = risk-on.

5. Currency-equity correlation (DXY vs SPY)
   Source: Fratzscher 2009 *JoB*. Strong USD pressures multinational
   earnings (S&P 500 ~40% foreign rev); EM equity especially sensitive.
   Inverse signal: rising DXY = headwind for SPY long-only.

This module computes per-date cross-asset signals from prefetched ETF
OHLCV (data_prefetch/polygon/ohlcv_daily/{TICKER}.parquet for TLT, SPY,
GLD, SLV, sector XLX ETFs, etc.) and FRED macro data. Strategy
registration is deferred to post-Batch-225.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd


_OHLCV_DIR = (
    Path(__file__).parent.parent.parent
    / "data_prefetch" / "polygon" / "ohlcv_daily"
)
_FRED_DIR = (
    Path(__file__).parent.parent.parent
    / "data_prefetch" / "fred" / "observations"
)
# Batch 264 fix: VIX + VIX3M live in FRED observations (VIXCLS / VXVCLS),
# not polygon. Cross-asset signals were silently no-op because lookup
# went to polygon/ohlcv_daily/VIX.parquet which doesn't exist.
# Per CHECKLIST #77 canonical-source: FRED is the cached VIX provider.
_FRED_TICKER_MAP = {
    "VIX":   "VIXCLS",
    "VIX3M": "VXVCLS",
    # VIX9D: not in FRED (CBOE-only per INV-010); graceful no-op
}


def _load_close_series(ticker: str, as_of: date,
                        lookback_days: int = 252) -> Optional[pd.Series]:
    """Load close-series for ticker up to as_of with `lookback_days` history.

    Source priority:
      1. data_prefetch/polygon/ohlcv_daily/{ticker}.parquet (equity ETFs)
      2. data_prefetch/fred/observations/{fred_id}.parquet (VIX family)
    """
    safe_ticker = ticker.replace(".", "-")
    path = _OHLCV_DIR / f"{safe_ticker}.parquet"
    if not path.exists() and ticker in _FRED_TICKER_MAP:
        fred_path = _FRED_DIR / f"{_FRED_TICKER_MAP[ticker]}.parquet"
        if fred_path.exists():
            try:
                df = pd.read_parquet(fred_path)
                if df.empty:
                    return None
                date_col = "date" if "date" in df.columns else "observation_date"
                val_col = "value" if "value" in df.columns else "close"
                if date_col not in df.columns or val_col not in df.columns:
                    return None
                df["date_dt"] = pd.to_datetime(df[date_col], errors="coerce").dt.date
                df = df.dropna(subset=["date_dt"])
                df = df[df["date_dt"] <= as_of].sort_values("date_dt")
                df = df[pd.to_numeric(df[val_col], errors="coerce").notna()]
                if df.empty:
                    return None
                series = pd.Series(
                    pd.to_numeric(df[val_col]).values,
                    index=df["date_dt"].values,
                )
                return series.tail(lookback_days + 30)
            except Exception:
                return None
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(path)
        if df.empty or "close" not in df.columns:
            return None
        if "date" in df.columns:
            df["date_dt"] = pd.to_datetime(df["date"], errors="coerce").dt.date
            df = df.dropna(subset=["date_dt"])
            df = df[df["date_dt"] <= as_of].sort_values("date_dt")
            if df.empty:
                return None
            series = pd.Series(df["close"].values, index=df["date_dt"].values)
            return series.tail(lookback_days + 30)
        # Index-based
        if hasattr(df.index, "date"):
            sliced = df[df.index.date <= as_of]
        else:
            sliced = df[df.index <= as_of]
        if sliced.empty:
            return None
        return sliced["close"].tail(lookback_days + 30)
    except Exception:
        return None


def _ratio_trend_signal(
    series_num: pd.Series,
    series_den: pd.Series,
    window: int = 20,
) -> Optional[dict]:
    """Compute the ratio's rolling change. Returns dict with current ratio
    + window-period percent change (positive = numerator outperforming
    denominator)."""
    if series_num is None or series_den is None:
        return None
    common = pd.concat([series_num.rename("n"), series_den.rename("d")],
                       axis=1, join="inner").dropna()
    if len(common) < window + 1:
        return None
    ratio = common["n"] / common["d"]
    current = float(ratio.iloc[-1])
    prior = float(ratio.iloc[-window - 1])
    if prior <= 0:
        return None
    pct_change = (current - prior) / prior
    return {
        "ratio":         round(current, 6),
        "pct_change":    round(float(pct_change), 4),
        "trend_up":      pct_change > 0.02,
        "trend_down":    pct_change < -0.02,
        # B724 (2026-06-12 owner-approved per "continue autonomously"):
        # B654 narrow-scope tighten precedent (cpr_narrow 0.15 -> cpr_narrow
        # _tight 0.05) applied to ratio-trend threshold. risk_off_bond
        # _equity_short measured 14,185/yr SHORT = state-flag rate above
        # B710 5K ceiling. Loose 2% threshold means trend_up True ~30-40%
        # of bars in any sustained regime. Narrow-scope strong variant
        # (>5%) is True only in materially-rising-bonds environments;
        # other consumers of bare trend_up/trend_down unchanged.
        "trend_up_strong":      pct_change > 0.05,
        "trend_down_strong":    pct_change < -0.05,
        # B2076 (S6-B1248-LEVER3, owner-approved 2026-08-23): EVENT key -
        # the strong flag CROSSED False->True within the last 5 sessions.
        # The STATE flag is True for entire regimes (B724 measured the loose
        # variant at state-flag rates); the cross is the regime's onset, the
        # only bar-of-fire with timing content. B655/B643 window semantics.
        "trend_up_strong_cross_recent_5d": _cross_recent(
            ratio, window, 0.05, 5),
    }


def _cross_recent(ratio: pd.Series, window: int, thresh: float,
                  tap_window: int) -> bool:
    """True if `ratio`'s `window`-period pct-change crossed above `thresh`
    (False->True transition) within the last `tap_window` sessions."""
    pct = ratio / ratio.shift(window) - 1
    strong = pct > thresh
    cross = strong & ~strong.shift(1).fillna(False)
    return bool(cross.iloc[-tap_window:].any())


def compute_bond_equity_signals(as_of: date, window: int = 20) -> dict:
    """TLT/SPY ratio: rising = risk-off (bonds outperform); falling =
    risk-on (equities outperform)."""
    tlt = _load_close_series("TLT", as_of)
    spy = _load_close_series("SPY", as_of)
    res = _ratio_trend_signal(tlt, spy, window=window)
    if not res:
        return {}
    return {
        "bond_equity_ratio":            res["ratio"],
        "bond_equity_20d_pct_change":   res["pct_change"],
        "risk_off_regime_bond_signal":  res["trend_up"],
        "risk_on_regime_bond_signal":   res["trend_down"],
        # B724: narrow-scope strong variants (>5% vs 2%) for ceiling-fix.
        "risk_off_regime_bond_signal_strong": res["trend_up_strong"],
        "risk_on_regime_bond_signal_strong":  res["trend_down_strong"],
        # B2076 (LEVER3): EVENT onset key; sole approved consumer is
        # strat_risk_off_bond_equity_short (narrow blast radius - the
        # risk-on mirror waits for a consumer of its own).
        "risk_off_bond_signal_strong_cross_recent_5d":
            res["trend_up_strong_cross_recent_5d"],
    }


def compute_vix_term_structure_signals(as_of: date) -> dict:
    """VIX term structure - VIX9D / VIX / VIX3M.
    Contango (VIX < VIX3M) = normal complacency; backwardation = stress.

    Falls back gracefully if VIX9D or VIX3M parquets unavailable
    (just emits the available signals)."""
    vix = _load_close_series("VIX", as_of, lookback_days=60)
    vix3m = _load_close_series("VIX3M", as_of, lookback_days=60)
    vix9d = _load_close_series("VIX9D", as_of, lookback_days=60)
    out: dict = {}
    if vix is not None and not vix.empty:
        out["vix_today"] = round(float(vix.iloc[-1]), 2)
    if vix is not None and vix3m is not None:
        try:
            v = float(vix.iloc[-1])
            v3 = float(vix3m.iloc[-1])
            ratio = v / v3 if v3 > 0 else None
            if ratio is not None:
                out["vix_vix3m_ratio"] = round(ratio, 4)
                out["vix_term_contango"] = ratio < 1.0
                out["vix_term_backwardation"] = ratio >= 1.0
        except (TypeError, ValueError, IndexError):
            pass
    return out


def compute_sector_rotation_signals(
    as_of: date,
    window: int = 20,
    sectors: tuple = ("XLF", "XLY", "XLI", "XLK",
                       "XLU", "XLP", "XLV", "XLE"),
) -> dict:
    """Sector relative-strength: rolling 20d return per-sector vs SPY.
    Returns the strongest + weakest sector + the corresponding lifts.

    Conover-Jensen-Johnson-Mercer 2008 sector-rotation literature.
    Defensive sectors (XLU/XLP/XLV) lead during contractions; cyclicals
    (XLF/XLY/XLI/XLK/XLE) lead during expansions.
    """
    spy = _load_close_series("SPY", as_of, lookback_days=window + 5)
    if spy is None or len(spy) < window + 1:
        return {}
    spy_ret = float(spy.iloc[-1]) / float(spy.iloc[-window - 1]) - 1.0
    rs_map = {}
    for sec in sectors:
        s = _load_close_series(sec, as_of, lookback_days=window + 5)
        if s is None or len(s) < window + 1:
            continue
        sec_ret = float(s.iloc[-1]) / float(s.iloc[-window - 1]) - 1.0
        rs_map[sec] = sec_ret - spy_ret  # relative strength vs SPY
    if not rs_map:
        return {}
    strongest = max(rs_map.items(), key=lambda kv: kv[1])
    weakest = min(rs_map.items(), key=lambda kv: kv[1])
    return {
        "sector_strongest":     strongest[0],
        "sector_strongest_rs":  round(strongest[1], 4),
        "sector_weakest":       weakest[0],
        "sector_weakest_rs":    round(weakest[1], 4),
        "sector_rs_map":        {k: round(v, 4) for k, v in rs_map.items()},
        # Defensive vs cyclical: are defensive sectors leading?
        "defensive_leadership": (
            max(rs_map.get(s, -float("inf")) for s in ("XLU", "XLP", "XLV"))
            > max(rs_map.get(s, -float("inf")) for s in ("XLF", "XLY", "XLI"))
        ),
    }


def compute_gold_silver_ratio_signals(as_of: date, window: int = 20) -> dict:
    """GLD/SLV ratio: rising = risk-off (gold preferred); falling =
    risk-on. Hammoudeh-Yuan 2008 *Resources Policy*."""
    gld = _load_close_series("GLD", as_of)
    slv = _load_close_series("SLV", as_of)
    res = _ratio_trend_signal(gld, slv, window=window)
    if not res:
        return {}
    return {
        "gold_silver_ratio":             res["ratio"],
        "gold_silver_20d_pct_change":    res["pct_change"],
        "risk_off_regime_gold_signal":   res["trend_up"],
    }


def compute_dxy_signals(as_of: date, window: int = 20) -> dict:
    """DXY trend (proxied by UUP ETF). Rising USD = headwind for SPY
    multinational earnings. Fratzscher 2009 *JoB*."""
    uup = _load_close_series("UUP", as_of)
    if uup is None or len(uup) < window + 1:
        return {}
    cur = float(uup.iloc[-1])
    prior = float(uup.iloc[-window - 1])
    if prior <= 0:
        return {}
    pct = (cur - prior) / prior
    return {
        "dxy_proxy_close":      round(cur, 4),
        "dxy_20d_pct_change":   round(pct, 4),
        "usd_strengthening":    pct > 0.02,
        "usd_weakening":        pct < -0.02,
    }


def compute_cross_asset_signals(as_of: date) -> dict:
    """One-shot cross-asset signal aggregator.

    Returns merged dict from all sub-helpers; defensive on missing data
    (empty dict per-helper -> not merged).
    """
    out: dict = {}
    out.update(compute_bond_equity_signals(as_of))
    out.update(compute_vix_term_structure_signals(as_of))
    out.update(compute_sector_rotation_signals(as_of))
    out.update(compute_gold_silver_ratio_signals(as_of))
    out.update(compute_dxy_signals(as_of))
    return out
