"""
engine/regime_filter.py  -  VIX + SPY regime classification (Option B).

Classifies market into: bull / neutral / bear / crisis
Used to:
  - Gate which trade directions are allowed
  - Scale position sizes
  - Determine if short-to-long conversion is permitted
"""

import logging
from datetime import date, timedelta
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


# DEC-183 RESOLVED-IMPLEMENTED Batch 84 2026-05-12 owner-mandated wiring:
# `classify_regime` is a pure-functional signal helper with hashable scalar
# inputs (Optional[float], Optional[bool]); wrapping it in the
# `lru_cached` decorator from improvements.py closes the helper-only gap so
# the engine's regime-classification path (called once per day via
# get_regime_context + many times across walk-forward folds re-evaluating
# overlapping dates) reuses cached results instead of re-running the
# threshold ladder on every call. Pure function, immutable str output,
# small input cardinality (VIX rounds to a finite set of float prints,
# spy_above is bool/None) -> high hit rate across folds + repeat dates.
from backtest.engine.improvements import lru_cached as _lru_cached_dec183


def compute_bear_composite_score(
    as_of: date,
    yield_curve_df: "Optional[pd.DataFrame]" = None,
    aaii_df: "Optional[pd.DataFrame]" = None,
    sector_ohlcv_dict: "Optional[dict]" = None,
) -> dict:
    """Batch 292 (2026-05-21 owner-approved option 3 per Stage C v3 forensic):
    Compute a 3-indicator bear composite score to catch 2022-style stealth
    bears that VIX-only or SPY-only classification miss.

    Indicators (each contributes 1 point if firing):
      1. Yield curve inversion: T10Y2Y < 0
         Source: data_prefetch/fred/observations/T10Y2Y.parquet
         Canonical recession signal (Estrella-Hardouvelis 1991).
      2. AAII bearish sentiment >= 40%
         Source: data_prefetch/aaii/weekly_sentiment.parquet
         Survey-based extreme pessimism marker.
      3. Sector breadth: >=5 of 8 sector ETFs below their 200-EMA
         Source: XLK, XLF, XLE, XLV, XLI, XLU, XLP, XLY from polygon cache.
         Broad-market deterioration signal.

    Returns dict with:
      score: int 0-3 (count of indicators firing)
      yield_curve_inverted: bool
      aaii_bearish_extreme: bool
      sector_breadth_bear: bool
      details: dict with raw values

    Each indicator falls back gracefully to False when data unavailable
    (e.g., early in backtest history). Score==0 in that case means
    no override - regime falls back to classify_regime VIX/SPY ladder.
    """
    out = {
        "score": 0,
        "yield_curve_inverted": False,
        "aaii_bearish_extreme": False,
        "sector_breadth_bear": False,
        "details": {},
    }
    # 1. Yield curve inversion
    if yield_curve_df is not None and not yield_curve_df.empty:
        try:
            df = yield_curve_df.copy()
            df["dt"] = pd.to_datetime(df["date"], errors="coerce").dt.date
            df = df.dropna(subset=["dt"]).sort_values("dt")
            df = df[df["dt"] <= as_of]
            if not df.empty:
                last_val = float(df["value"].iloc[-1])
                out["yield_curve_inverted"] = last_val < 0
                out["details"]["t10y2y"] = round(last_val, 2)
        except Exception as exc:
            # Batch 374 DEC-231: log silently-swallowed failures with context
            # so a bear-composite input regression surfaces in run.log instead
            # of zero-scoring stealth-bear undetected.
            logger.warning(
                "bear_composite: yield_curve parse failed as_of=%s exc=%s",
                as_of, exc,
            )

    # 2. AAII bearish extreme
    if aaii_df is not None and not aaii_df.empty:
        try:
            df = aaii_df.copy()
            df["dt"] = pd.to_datetime(df["date"], errors="coerce").dt.date
            df = df.dropna(subset=["dt"]).sort_values("dt")
            df = df[df["dt"] <= as_of]
            if not df.empty:
                last_bearish = float(df["bearish"].iloc[-1])
                out["aaii_bearish_extreme"] = last_bearish >= 0.40
                out["details"]["aaii_bearish"] = round(last_bearish, 3)
        except Exception as exc:
            logger.warning(
                "bear_composite: aaii parse failed as_of=%s exc=%s",
                as_of, exc,
            )

    # 3. Sector breadth
    if sector_ohlcv_dict is not None:
        try:
            sectors = ("XLK", "XLF", "XLE", "XLV", "XLI", "XLU", "XLP", "XLY")
            n_below = 0
            n_eligible = 0
            for sym in sectors:
                sec_df = sector_ohlcv_dict.get(sym)
                if sec_df is None or sec_df.empty:
                    continue
                # Filter to as_of and compute 200-EMA
                if "date" in sec_df.columns:
                    sec_df = sec_df.copy()
                    sec_df["dt"] = pd.to_datetime(sec_df["date"], errors="coerce").dt.date
                    sliced = sec_df[sec_df["dt"] <= as_of].sort_values("dt")
                else:
                    sliced = sec_df[sec_df.index.date <= as_of]
                if len(sliced) < 200:
                    continue
                ema_200 = sliced["close"].ewm(span=200, adjust=False).mean().iloc[-1]
                close = float(sliced["close"].iloc[-1])
                n_eligible += 1
                if close < float(ema_200):
                    n_below += 1
            if n_eligible >= 5:
                out["sector_breadth_bear"] = n_below >= 5
                out["details"]["sector_breadth"] = f"{n_below}/{n_eligible}_below_200ema"
        except Exception as exc:
            logger.warning(
                "bear_composite: sector_breadth parse failed as_of=%s exc=%s",
                as_of, exc,
            )

    out["score"] = (
        int(out["yield_curve_inverted"]) +
        int(out["aaii_bearish_extreme"]) +
        int(out["sector_breadth_bear"])
    )
    return out


@_lru_cached_dec183(maxsize=256)
def classify_regime(
    vix_value: Optional[float],
    spy_above_200ema: Optional[bool],
    bear_composite_score: int = 0,
) -> str:
    """
    Classify market regime from VIX level and SPY vs 200 EMA.

    Returns: 'bull' | 'neutral' | 'bear' | 'crisis' | 'unknown'

    DEC-316 fix (Pass 51) BUG-225: returns 'unknown' on missing VIX data instead of
    silently defaulting to 'neutral'. Previously, a cache miss or data feed
    failure caused the system to trade as if conditions were normal. Now
    'unknown' is a fail-closed signal  -  REGIME_FILTER['unknown'] blocks new
    entries; existing positions continue under their original stop logic.

    DEC-183 Batch 84: now wrapped in lru_cached (maxsize=256) so repeated
    calls (walk-forward folds, replay backtests) reuse cached results.

    Batch 288 (2026-05-20 owner-approved option A.2 per Audit Part 1 sec-4):
    SPY-below-200-EMA alone now triggers "bear" regardless of VIX. The prior
    "VIX>=30 AND below-200EMA" gate was too strict for 2022-style stealth
    bear (SPY -23% YTD with VIX 20-35 range that never hit 30 + below-200
    simultaneously). Stage C diagnostic: 100% of 2022 trades classified
    "neutral" despite the real bear, contributing -275pp aggregate loss.

    Batch 642 (2026-06-09 owner-directed per B640 external-AI regime-classifier
    audit finding #2): The canonical "VIX>=30 AND below-200EMA" line was
    DEAD CODE post-B288. Any day satisfying it also satisfied the
    SPY-only line below, so the canonical line never returned anything
    the SPY-only line wouldn't have. Removed to surface honestly that
    bear classification is now SPY-vs-200EMA only; VIX contributes only
    to crisis (>=40) and bull (<20) thresholds. Without the cleanup,
    casual readers + future editors believed VIX was still gating bear
    when it wasn't.

    Ladder post-B642 (top-to-bottom):
      VIX missing                      -> unknown (fail-closed)
      VIX >= 40                        -> crisis
      below-200EMA (any VIX)           -> bear (Batch 288 SPY-only gate)
      bear_composite_score >= 2        -> bear (Batch 292 override)
      VIX < 20 AND above-200EMA        -> bull
      else                             -> neutral
    """
    if vix_value is None:
        return "unknown"

    if vix_value >= 40:
        return "crisis"
    # Batch 288 SPY-only bear gate. The pre-B642 ladder also had a
    # "VIX>=30 AND below-200EMA" line above this one; per B642 audit
    # finding #2, that line was dead code (any case it caught was also
    # caught here) and was removed for clarity. VIX no longer
    # contributes to bear classification (only to crisis and bull).
    if spy_above_200ema is False:
        return "bear"
    # Batch 292 (2026-05-21 owner-approved option 3): bear composite override.
    # When >=2 of 3 bear indicators fire (yield curve inverted, AAII bearish
    # >=40%, sector breadth >=5 of 8 below 200-EMA), force "bear" regime even
    # if SPY is above 200-EMA. Catches mid-bear rallies (Aug 2022) when SPY
    # temporarily crossed above 200-EMA but the broader bear thesis held.
    if bear_composite_score >= 2:
        return "bear"
    if vix_value < 20 and spy_above_200ema is True:
        return "bull"
    return "neutral"


def get_regime_context(
    vix_value: Optional[float],
    spy_close: Optional[float],
    spy_ema200: Optional[float],
    prev_regime: Optional[str] = None,
    vix_smoothed: Optional[float] = None,
    use_hysteresis: bool = False,
    bear_composite_score: int = 0,
) -> dict:
    """
    Full regime context dict including position size multipliers.
    Used by engine and site card generator.

    DEC-317 + DEC-388 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 43
    engine wiring (2026-05-11): optional prev_regime + vix_smoothed + use_hysteresis
    flags enable VIX MA smoothing + hysteresis when caller tracks day-over-day
    state. Defaults preserve original behavior (raw VIX, no hysteresis) so
    legacy call sites remain unchanged.

    Batch 292 (2026-05-21): optional bear_composite_score (0-3 from
    compute_bear_composite_score). When >= 2, forces bear regime
    classification (overrides SPY-above-200-EMA fallback to bull/neutral).
    Caller computes the score from yield curve + AAII + sector breadth.
    """
    from backtest.config import REGIME_FILTER, POSITION_SIZE_MULT

    spy_above = (spy_close > spy_ema200
                 if spy_close and spy_ema200 else None)
    # Batch 642: signed % from 200-EMA for EMA-cross hysteresis band.
    spy_pct_from_200ema: Optional[float] = None
    if spy_close is not None and spy_ema200 is not None and spy_ema200 > 0:
        spy_pct_from_200ema = (spy_close - spy_ema200) / spy_ema200 * 100.0
    # Use smoothed VIX if provided; else raw
    vix_for_classify = vix_smoothed if vix_smoothed is not None else vix_value
    if use_hysteresis:
        regime = classify_regime_with_hysteresis(
            vix_for_classify, spy_above, prev_regime,
            bear_composite_score=bear_composite_score,
            spy_pct_from_200ema=spy_pct_from_200ema)
    else:
        regime = classify_regime(
            vix_for_classify, spy_above,
            bear_composite_score=bear_composite_score)
    # DEC-316 fix (Pass 51): when regime is 'unknown', use unknown config (block).
    # Previously fell through to 'neutral' which silently allowed trading on
    # missing data. Now 'unknown' has long='none' / short='none' -> blocks entries.
    cfg       = REGIME_FILTER.get(regime, REGIME_FILTER["unknown"])

    long_mult  = POSITION_SIZE_MULT.get(cfg.get("long", "full"), 1.0)
    short_mult = POSITION_SIZE_MULT.get(cfg.get("short", "full"), 1.0)

    return {
        "regime":              regime,
        "vix":                 round(vix_value, 2) if vix_value else None,
        "spy_above_200ema":    spy_above,
        "long_allowed":        long_mult > 0,
        "short_allowed":       short_mult > 0,
        "long_size_mult":      long_mult,
        "short_size_mult":     short_mult,
        "conversion_allowed":  regime == "bull",
        "description":         {
            "bull":    "VIX < 20, SPY above 200 EMA  -  risk-on, favour longs",
            "neutral": "Mixed conditions  -  both directions allowed at full size",
            "bear":    "VIX > 30, SPY below 200 EMA  -  favour shorts",
            "crisis":  "VIX > 40  -  reduce long size to 50%, require VERY HIGH min tier. Do NOT tighten stops (causes whipsawing).",
            "unknown": "Insufficient data (no VIX)  -  fail closed, block new entries (DEC-316)",
        }.get(regime, ""),
    }


def get_spy_ema200(spy_df: pd.DataFrame, as_of: date) -> Optional[float]:
    """Compute SPY 200-day EMA as of a given date."""
    if spy_df is None or spy_df.empty:
        return None
    sliced = spy_df[spy_df.index.date <= as_of]
    if len(sliced) < 200:
        return None
    ema = sliced["close"].ewm(span=200, adjust=False).mean()
    return float(ema.iloc[-1])


# DEC-317 + DEC-388 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 42
# 2026-05-11 (owner-approved Path C). VIX 5-day SMA smoothing + hysteresis
# prevents regime flips on single noisy VIX prints. Previously hard
# thresholds (40/30/20) on raw VIX caused regime oscillation during spikes
# that reverted within 1-2 days.

def get_vix_smoothed(vix_series: pd.Series, as_of: date, window: int = 5) -> Optional[float]:
    """Return N-day SMA of VIX at or before `as_of`.

    DEC-388 Phase 3 Batch 42: smooths VIX before threshold application.
    Default window=5 trading days per DEC-388 spec ("vix_sma_5 = VIX.rolling(5).mean()").

    Inputs:
      vix_series: pd.Series of VIX values indexed by date
      as_of: target date
      window: SMA window (default 5)

    Returns float SMA or None if insufficient data.
    """
    if vix_series is None or len(vix_series) < window:
        return None
    try:
        # Filter to as_of-or-before
        if hasattr(vix_series.index, 'date'):
            sliced = vix_series[vix_series.index.date <= as_of]
        else:
            sliced = vix_series[vix_series.index <= as_of]
        if len(sliced) < window:
            return None
        sma = float(sliced.rolling(window).mean().iloc[-1])
        if pd.isna(sma):
            return None
        return sma
    except Exception as exc:
        # Batch 374 DEC-231: log silently-swallowed failures
        logger.warning(
            "vix_sma_smoothed: window=%s as_of=%s parse failed exc=%s",
            window, as_of, exc,
        )
        return None


REGIME_STATES = ("bull", "neutral", "bear", "crisis")


def dispersion_circuit_breaker(
    daily_returns_df,
    window: int = 20,
    sigma_threshold: float = 3.0,
) -> dict:
    """DEC-128 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 58 2026-05-11
    (owner-approved Path C 10-DEC bundle). Dispersion-conditional circuit
    breaker per Pass 52 turn 119 spec: trigger when cross-sectional
    dispersion exceeds sigma_threshold standard deviations vs the rolling
    historical mean dispersion.

    Inputs:
      daily_returns_df: DataFrame indexed by date, columns = tickers,
        values = daily returns (decimal, e.g. 0.01 = 1%)
      window: rolling window for historical dispersion mean+std (default 20)
      sigma_threshold: trigger threshold in std-devs (default 3.0)

    Cross-sectional dispersion per day = std-across-tickers of that day's
    returns. Then compute z-score vs rolling window of prior dispersions:
      z = (today_dispersion - mean_rolling) / std_rolling
    Trigger when z > sigma_threshold.

    Returns dict with triggered (bool), z_score (float), today_dispersion,
    note. Insufficient history returns triggered=False + note.
    Joint DEC-314/315 circuit breakers.
    """
    import pandas as pd
    if daily_returns_df is None or len(daily_returns_df) < window + 1:
        return {"triggered": False, "z_score": None,
                "today_dispersion": None, "note": "insufficient_history"}
    daily_disp = daily_returns_df.std(axis=1)
    if len(daily_disp) < window + 1:
        return {"triggered": False, "z_score": None,
                "today_dispersion": None, "note": "insufficient_history"}
    rolling_mean = daily_disp.iloc[-(window + 1):-1].mean()
    rolling_std = daily_disp.iloc[-(window + 1):-1].std()
    today_disp = float(daily_disp.iloc[-1])
    # Batch 188 (INV-052 fix): numerical guard for near-zero rolling_std.
    # When the rolling window has very low dispersion variability (calm
    # period after correction), even a modest dispersion uptick produces
    # an astronomical z-score (Phase 1A baseline saw z=379 on 2022-06-09
    # with today_dispersion=1.73 and inferred rolling_std~0.005). Two
    # guards: (1) min rolling_std floor 1e-3 = treat as zero-stddev case;
    # (2) z-score cap at 10.0 for reporting + triggering. Real activations
    # at z=3-7 still work; z>10 is mathematically dominant signal but
    # numerically suspect (treat as triggered but capped).
    STDDEV_FLOOR = 1e-3
    Z_CAP = 10.0
    if rolling_std == 0 or pd.isna(rolling_std) or rolling_std < STDDEV_FLOOR:
        return {"triggered": False, "z_score": 0.0,
                "today_dispersion": today_disp,
                "note": "zero_rolling_std" if (rolling_std == 0 or pd.isna(rolling_std))
                        else f"rolling_std_below_floor_{STDDEV_FLOOR}_batch188"}
    z = (today_disp - rolling_mean) / rolling_std
    z_capped = min(float(z), Z_CAP) if z > 0 else max(float(z), -Z_CAP)
    return {
        "triggered":         bool(z_capped > sigma_threshold),
        "z_score":           round(z_capped, 4),
        "today_dispersion":  round(today_disp, 6),
        "note":              "TRIGGERED" if z_capped > sigma_threshold else "ok",
    }


def multi_input_regime_score(
    vix: Optional[float],
    spy_above_200ema: Optional[bool],
    yield_curve_spread: Optional[float] = None,
    hy_spread_bps: Optional[float] = None,
    icsa_yoy_pct: Optional[float] = None,
    breadth_pct_above_50ema: Optional[float] = None,
    sector_dispersion: Optional[float] = None,
    aaii_bull_bear_spread: Optional[float] = None,
    cnn_fg: Optional[float] = None,
) -> dict:
    """DEC-106 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 55 2026-05-11
    (owner-approved Path C 5-DEC bundle). Multi-input regime scorecard
    expanding original 2-input (VIX, SPY trend) classifier to 8+ inputs
    per Pass 52 turn 61 owner spec. Each provided input contributes a
    bullish/bearish vote in [-1, +1]; missing inputs are skipped (not
    treated as neutral) so the score reflects only present evidence.

    Vote calibrations (each clipped to [-1, +1]):
      VIX:        +1 if <20, -1 if >30, linear scale in between
      SPY trend:  +1 if above 200ema, -1 if below
      yc_spread:  +1 if >1.0 (steep), -1 if <-0.5 (inverted)
      hy_spread:  +1 if <300 bps (tight), -1 if >700 bps (wide)
      icsa_yoy:   +1 if <0% (claims falling), -1 if >20% (rising)
      breadth:    +1 if >70%, -1 if <30%
      dispersion: -1 if high dispersion (>median*1.5), +1 if low
      aaii bb:    +1 if <-20 (bearish crowd, contrarian bull), -1 if >+20
      cnn_fg:     +1 if 30-70 (neutral), -1 if <20 or >80 (extremes)

    Returns dict with regime_score (normalized 0-100, 50=neutral),
    inputs_used (count), regime_label ('bull'/'neutral'/'bear'/'crisis').
    """
    votes = []
    if vix is not None:
        if vix < 20:    votes.append(1.0)
        elif vix > 30:  votes.append(-1.0)
        else:           votes.append(round((25.0 - vix) / 5.0, 3))
    if spy_above_200ema is not None:
        votes.append(1.0 if spy_above_200ema else -1.0)
    if yield_curve_spread is not None:
        if yield_curve_spread > 1.0:   votes.append(1.0)
        elif yield_curve_spread < -0.5: votes.append(-1.0)
        else:                          votes.append(round(yield_curve_spread / 1.0, 3))
    if hy_spread_bps is not None:
        if hy_spread_bps < 300:    votes.append(1.0)
        elif hy_spread_bps > 700:  votes.append(-1.0)
        else:                      votes.append(round((500.0 - hy_spread_bps) / 200.0, 3))
    if icsa_yoy_pct is not None:
        if icsa_yoy_pct < 0:       votes.append(1.0)
        elif icsa_yoy_pct > 20:    votes.append(-1.0)
        else:                      votes.append(round((10.0 - icsa_yoy_pct) / 10.0, 3))
    if breadth_pct_above_50ema is not None:
        if breadth_pct_above_50ema > 70:  votes.append(1.0)
        elif breadth_pct_above_50ema < 30: votes.append(-1.0)
        else:                             votes.append(round((breadth_pct_above_50ema - 50) / 20.0, 3))
    if sector_dispersion is not None:
        votes.append(-1.0 if sector_dispersion > 1.5 else 1.0 if sector_dispersion < 0.7 else 0.0)
    if aaii_bull_bear_spread is not None:
        if aaii_bull_bear_spread < -20:   votes.append(1.0)
        elif aaii_bull_bear_spread > 20:  votes.append(-1.0)
        else:                             votes.append(round(-aaii_bull_bear_spread / 20.0, 3))
    if cnn_fg is not None:
        if 30 <= cnn_fg <= 70:     votes.append(1.0)
        elif cnn_fg < 20 or cnn_fg > 80: votes.append(-1.0)
        else:                      votes.append(0.0)
    if not votes:
        return {"regime_score": None, "inputs_used": 0, "regime_label": "unknown"}
    raw_mean = sum(votes) / len(votes)
    score = round(50.0 + raw_mean * 50.0, 2)  # map [-1, +1] -> [0, 100]
    if score >= 65:    label = "bull"
    elif score >= 40:  label = "neutral"
    elif score >= 25:  label = "bear"
    else:              label = "crisis"
    return {"regime_score": score, "inputs_used": len(votes), "regime_label": label}


def multi_asset_regime_score(
    equity_vix: Optional[float],
    credit_hy_spread_bps: Optional[float] = None,
    commodity_pct_change_20d: Optional[float] = None,
    currency_dxy_pct_change_20d: Optional[float] = None,
) -> dict:
    """DEC-150 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 55 2026-05-11
    (owner-approved Path C 5-DEC bundle). Multi-asset regime detection
    composite per Pass 52 turn 119 owner spec. Combines 4 asset class
    signals into single regime score [0, 100] (50=neutral).

    Each asset class contributes equal weight. Missing inputs skipped.
    Joint with DEC-106 multi-input regime; DEC-150 specifically expands
    to non-equity asset classes (credit/commodity/FX) that often lead
    equity moves.

    Returns dict with regime_score, inputs_used, regime_label.
    """
    votes = []
    if equity_vix is not None:
        if equity_vix < 20:    votes.append(1.0)
        elif equity_vix > 30:  votes.append(-1.0)
        else:                  votes.append(round((25.0 - equity_vix) / 5.0, 3))
    if credit_hy_spread_bps is not None:
        if credit_hy_spread_bps < 300:    votes.append(1.0)
        elif credit_hy_spread_bps > 700:  votes.append(-1.0)
        else: votes.append(round((500.0 - credit_hy_spread_bps) / 200.0, 3))
    if commodity_pct_change_20d is not None:
        if commodity_pct_change_20d > 3:    votes.append(1.0)
        elif commodity_pct_change_20d < -3: votes.append(-1.0)
        else: votes.append(round(commodity_pct_change_20d / 3.0, 3))
    if currency_dxy_pct_change_20d is not None:
        # Strong USD typically bearish for risk assets (inverse)
        if currency_dxy_pct_change_20d > 3:    votes.append(-1.0)
        elif currency_dxy_pct_change_20d < -3: votes.append(1.0)
        else: votes.append(round(-currency_dxy_pct_change_20d / 3.0, 3))
    if not votes:
        return {"regime_score": None, "inputs_used": 0, "regime_label": "unknown"}
    raw_mean = sum(votes) / len(votes)
    score = round(50.0 + raw_mean * 50.0, 2)
    if score >= 65:    label = "bull"
    elif score >= 40:  label = "neutral"
    elif score >= 25:  label = "bear"
    else:              label = "crisis"
    return {"regime_score": score, "inputs_used": len(votes), "regime_label": label}


def sector_regime(
    sector_etf_price: Optional[float],
    sector_etf_ema200: Optional[float],
    sector_vol_annualized: Optional[float],
    crisis_vol_threshold: float = 0.40,
    bear_vol_threshold: float = 0.30,
    bull_vol_threshold: float = 0.20,
) -> str:
    """DEC-151 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 55 2026-05-11
    (owner-approved Path C 5-DEC bundle). Sector-level analog of
    `classify_regime`: per-sector regime independent of market-level.

    Mirrors VIX+SPY classifier semantics applied to sector ETF: replaces
    SPY with sector ETF price-vs-200EMA, replaces VIX with sector
    annualized realized vol. Thresholds caller-tunable (defaults match
    market-level VIX 20/30/40).

    Joint with DEC-323/394 PIT sector taxonomy (Batch 46) for upstream
    sector membership; this function classifies the sector's regime.

    Test signal example: 2022 sector regime output XLK=bear, XLE=bull,
    XLF=neutral (per DEC-151 spec). Caller supplies actual sector ETF
    price/EMA/vol; this returns the label.

    Returns 'bull' | 'neutral' | 'bear' | 'crisis' | 'unknown'.
    """
    if (sector_vol_annualized is None or sector_etf_price is None
            or sector_etf_ema200 is None):
        return "unknown"
    above_ema = sector_etf_price > sector_etf_ema200
    if sector_vol_annualized >= crisis_vol_threshold:
        return "crisis"
    if sector_vol_annualized >= bear_vol_threshold and not above_ema:
        return "bear"
    if sector_vol_annualized < bull_vol_threshold and above_ema:
        return "bull"
    return "neutral"


def ema_smooth_regime_probability(
    new_score: float,
    prev_smoothed: Optional[float] = None,
    alpha: float = 0.1,
) -> float:
    """DEC-108 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 54 2026-05-11
    (owner-approved Path C bundle). Exponential smoothing of a regime
    probability or score (HMM rejected per Pass 52 turn 61 owner-approved
    spec; exponential smoothing chosen for simplicity-vs-benefit).

    Formula: smoothed = (1 - alpha) * prev_smoothed + alpha * new_score
    matches the spec: EMA = 0.9 * previous + 0.1 * new_observation (default
    alpha=0.1 weights new observation at 10%).

    First call (prev_smoothed=None) returns new_score unchanged to seed the
    EMA. Generalizes to any continuous regime input (DEC-388 VIX SMA already
    handles raw-VIX smoothing; this helper applies to derived regime scores
    like probability vectors or stratified inputs).

    Inputs:
      new_score: today's raw regime score (any continuous value)
      prev_smoothed: yesterday's EMA-smoothed value (None on first call)
      alpha: weight on new_score (default 0.1)

    Returns float smoothed score.
    """
    if prev_smoothed is None:
        return float(new_score)
    return float((1.0 - alpha) * prev_smoothed + alpha * new_score)


def compute_regime_transition_matrix(
    regime_sequence,
    states=REGIME_STATES,
) -> pd.DataFrame:
    """DEC-149 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 50 2026-05-11
    (owner-approved Path C). Empirical Markov-1 transition probability matrix
    estimated from a historical sequence of regime labels.

    Each row sums to 1.0 across non-degenerate origin states (states with at
    least one observed outgoing transition); origin states never observed in
    the sequence have a row of NaN to signal "no data" (avoids forcing a flat
    uniform prior).

    'unknown' regime labels are dropped before transition counting per spec
    (DEC-316 fail-closed: 'unknown' is a missing-data signal, not a regime).

    Inputs:
      regime_sequence: iterable of regime labels (e.g. ['bull','bull','neutral',
        'bear','bear','bull'])
      states: tuple of valid regime names (default: bull/neutral/bear/crisis)

    Returns DataFrame indexed by from_regime, columns to_regime, values P(next |
    current). matrix.loc['bull', 'neutral'] = P(next=neutral | current=bull).

    Cross-references:
      DEC-107 (regime probability) + DEC-108 (EMA smoothing): forward-expectation
      use case at Sprint 7 agent prompt integration.
    """
    import numpy as np
    matrix = pd.DataFrame(
        np.nan, index=list(states), columns=list(states), dtype=float,
    )
    # Filter to known states only
    cleaned = [r for r in regime_sequence if r in states]
    if len(cleaned) < 2:
        return matrix
    counts = pd.DataFrame(
        0.0, index=list(states), columns=list(states), dtype=float,
    )
    for i in range(len(cleaned) - 1):
        counts.loc[cleaned[i], cleaned[i + 1]] += 1.0
    row_totals = counts.sum(axis=1)
    for s in states:
        if row_totals.loc[s] > 0:
            matrix.loc[s] = counts.loc[s] / row_totals.loc[s]
    return matrix


# Batch 642 introduced EMA_CROSS_HYSTERESIS_PCT = 2.0 as an asymmetric
# sticky-bear directional bet. Batch 665 (2026-06-09 2nd-wave-redux critique
# #8 owner-approved revert): unvalidated curve-fit-to-2022 directional bet
# defaults OFF in pre-deployment systems. Setting 0.0% restores symmetric
# binary EMA-cross behavior (any close above 200-EMA exits bear). If
# S5-REGIME-WALK-FORWARD-VALIDATION shows asymmetric sticky-bear earns
# its keep OOS, the asymmetry returns with documented empirical support.
# Until then: symmetric is the unbiased baseline for the eventual walk-
# forward comparison.
EMA_CROSS_HYSTERESIS_PCT = 0.0


def classify_regime_with_hysteresis(
    vix_value: Optional[float],
    spy_above_200ema: Optional[bool],
    prev_regime: Optional[str] = None,
    hysteresis_buffer: float = 5.0,
    bear_composite_score: int = 0,
    spy_pct_from_200ema: Optional[float] = None,
) -> str:
    """Classify regime with hysteresis-buffer applied to VIX AND SPY-vs-200EMA.

    DEC-317 + DEC-388: prevents oscillation when VIX hovers near a threshold.
    Once in a regime, the VIX must move past threshold +/- buffer to switch.
    Without hysteresis a VIX print of 39.9 -> 40.1 -> 39.5 would flip the
    regime 3 times in 3 days. With hysteresis (buffer=5), to EXIT crisis the
    VIX must drop to <= 35 (40 - 5); to ENTER crisis it must rise to >= 40.

    Buffers applied symmetrically to all threshold pairs:
      crisis entry: VIX >= 40; exit: VIX < 35
      bear entry: VIX >= 30; exit: VIX < 25
      bull entry: VIX < 20; exit: VIX >= 25 (back to neutral)

    Batch 642 (2026-06-09 owner-directed per B640 external-AI regime audit
    finding #3): EMA-cross hysteresis band added. Pre-B642 the SPY-vs-
    200-EMA condition was binary at every threshold pair, so SPY oscillating
    +/-0.1% around its 200-EMA at range tops/bottoms flipped bear<->neutral
    day-by-day even though VIX was smoothed via 5-day SMA + 5-point buffer.
    The architecture was guarding VIX (the secondary input post-B288) while
    leaving the dominant input (SPY-vs-EMA cross) unbuffered. Asymmetric
    fix: SLOW to exit bear (require SPY decisively above 200-EMA --
    +EMA_CROSS_HYSTERESIS_PCT = 2%), FAST to enter bear (any below-EMA
    close triggers, since we don't want to delay risk-reduction). Caller
    passes spy_pct_from_200ema = (spy_close - spy_ema200) / spy_ema200 * 100
    (signed % from EMA); positive = SPY above EMA. When parameter is None
    (legacy callers), behavior degrades gracefully to the pre-B642 binary
    gate.

    Inputs:
      vix_value: smoothed VIX (use get_vix_smoothed); raw VIX also acceptable
        for callers that don't want smoothing
      spy_above_200ema: same as classify_regime
      prev_regime: previous day's regime (passed by engine); None first day
      hysteresis_buffer: VIX points (default 5)
      spy_pct_from_200ema (B642): signed % from 200-EMA (e.g. +2.5 = SPY is
        2.5% above 200-EMA). None for legacy callers.

    Returns: 'bull' | 'neutral' | 'bear' | 'crisis' | 'unknown'
    """
    if vix_value is None:
        return "unknown"

    # Hysteresis thresholds depend on prev_regime
    if prev_regime == "crisis":
        # Stay in crisis until VIX drops well below 40
        if vix_value >= 40 - hysteresis_buffer:
            return "crisis"
        # else fall through to lower thresholds
    if prev_regime == "bear":
        # Stay in bear until SPY recovers DECISIVELY above 200-EMA.
        # Batch 642: EMA-cross hysteresis band. Pre-B642 a single
        # +0.01% close above the EMA exited bear; post-B642 requires
        # SPY to close >= +EMA_CROSS_HYSTERESIS_PCT (default 2.0%)
        # above its 200-EMA to confirm exit. Falls back to pre-B642
        # binary gate when spy_pct_from_200ema is not provided.
        if spy_above_200ema is False:
            return "bear"
        # SPY is now above 200-EMA -- check the hysteresis band
        if spy_pct_from_200ema is not None:
            if spy_pct_from_200ema < EMA_CROSS_HYSTERESIS_PCT:
                # Above EMA but within +2% band -- not yet a decisive cross
                return "bear"
        # else legacy callers without spy_pct: pre-B642 behavior
    if prev_regime == "bull":
        # Stay in bull until VIX rises well above 20
        if vix_value < 20 + hysteresis_buffer and spy_above_200ema is True:
            return "bull"

    # Standard entry thresholds (same as classify_regime post-B642 cleanup)
    if vix_value >= 40:
        return "crisis"
    # Batch 642: removed dead canonical "VIX>=30 AND below-200EMA" line
    # (was redundant with SPY-only gate below). VIX no longer contributes
    # to bear classification (only to crisis and bull).
    if spy_above_200ema is False:
        return "bear"
    # Batch 292: bear composite override (mirror of classify_regime).
    if bear_composite_score >= 2:
        return "bear"
    if vix_value < 20 and spy_above_200ema is True:
        return "bull"
    return "neutral"
