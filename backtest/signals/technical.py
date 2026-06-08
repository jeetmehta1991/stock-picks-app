"""
signals/technical.py  -  Complete technical indicator computation.

Computes ALL indicators from the project plan:
  Pivots:     Standard (P/R1-R3/S1-S3), Camarilla (R1-R4/S1-S4),
              Woodie's (P/R1-R2/S1-S2), CPR, Fibonacci (5 levels + extensions),
              VWAP (+ deviation bands), Previous Day H/L/C
  Momentum:   RSI (9/14/21), Stochastic, StochRSI, Williams %R, ROC,
              MACD (12/26/9 and 8/21/5), PPO, Awesome Oscillator,
              Ultimate Oscillator
  Trend:      EMA/SMA crossovers (9/21, 20/50, 50/200), ADX (+DI/-DI),
              Parabolic SAR, Ichimoku (all 5 components), Supertrend,
              Hull MA, DEMA, TEMA
  Volatility: Bollinger Bands (3 param sets), Keltner Channels,
              Donchian (10 + 20 day), ATR, Squeeze Momentum, Envelopes
  Volume:     OBV, Volume Spike (1.5x/2x/3x), VWAP deviation,
              A/D Line, CMF, MFI, Force Index
  Patterns:   Inside/Outside bar, Bullish/Bearish Engulfing, Pin bar,
              Hammer, Shooting Star, Morning Star, Evening Star, Doji,
              Three White Soldiers, Three Black Crows

Entry: compute_all_signals(df) -> flat dict of ~220 signal fields
All computations are pure  -  no I/O. df must be pre-sliced to as_of date.
"""

import logging
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=FutureWarning)
logger = logging.getLogger(__name__)

try:
    import pandas_ta as ta
    _HAS_TA = True
except ImportError:
    logger.warning("pandas-ta not installed  -  using manual implementations")
    _HAS_TA = False


# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------

def _safe_float(val, default=0.0):
    try:
        v = float(val)
        return v if np.isfinite(v) else default
    except Exception:
        return default


def _atr_series(df: pd.DataFrame, period: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()


# -----------------------------------------------------------------------------
# PIVOT POINTS  -  Standard, Camarilla, Woodie's, CPR, Prev Day
# -----------------------------------------------------------------------------

def compute_pivots(df: pd.DataFrame) -> dict:
    if len(df) < 2:
        return {}
    prev  = df.iloc[-2]
    H, L, C, O = prev["high"], prev["low"], prev["close"], prev["open"]
    today = df["close"].iloc[-1]
    rng   = H - L
    near  = lambda lvl: abs(today - lvl) / max(abs(lvl), 0.01) < 0.003
    # Batch 574 (2026-06-04 owner correction of B573 scoping lapse per
    # feedback_narrow_scope_blast_radius): add `_wide` variant at 1.5pct
    # ONLY for doji strategies. Narrow near() (0.3pct) preserved for the
    # other 12 affected strategies so their behavior is unchanged.
    near_wide = lambda lvl: abs(today - lvl) / max(abs(lvl), 0.01) < 0.015

    # -- Standard --
    P  = (H + L + C) / 3
    R1 = 2*P - L;  R2 = P + rng;  R3 = H + 2*(P - L)
    S1 = 2*P - H;  S2 = P - rng;  S3 = L - 2*(H - P)

    # -- CPR --
    cpr_top    = (H + L) / 2
    cpr_bottom = P
    cpr_width  = abs(cpr_top - cpr_bottom)
    cpr_narrow = (cpr_width < rng * 0.15) if rng > 0 else False

    # -- Camarilla --
    cr4 = C + rng*1.1/2;  cr3 = C + rng*1.1/4
    cr2 = C + rng*1.1/6;  cr1 = C + rng*1.1/12
    cs1 = C - rng*1.1/12; cs2 = C - rng*1.1/6
    cs3 = C - rng*1.1/4;  cs4 = C - rng*1.1/2

    # -- Woodie's --
    wp  = (H + L + 2*O) / 4
    wr1 = 2*wp - L;  wr2 = wp + rng
    ws1 = 2*wp - H;  ws2 = wp - rng

    return {
        # Standard levels
        "pivot": round(P,4), "r1": round(R1,4), "r2": round(R2,4), "r3": round(R3,4),
        "s1": round(S1,4),   "s2": round(S2,4), "s3": round(S3,4),
        # CPR
        "cpr_top": round(cpr_top,4), "cpr_bottom": round(cpr_bottom,4),
        "cpr_width": round(cpr_width,4), "cpr_narrow": cpr_narrow,
        # Camarilla
        "cam_r4": round(cr4,4), "cam_r3": round(cr3,4),
        "cam_r2": round(cr2,4), "cam_r1": round(cr1,4),
        "cam_s1": round(cs1,4), "cam_s2": round(cs2,4),
        "cam_s3": round(cs3,4), "cam_s4": round(cs4,4),
        # Woodie's
        "wood_p":  round(wp,4),  "wood_r1": round(wr1,4), "wood_r2": round(wr2,4),
        "wood_s1": round(ws1,4), "wood_s2": round(ws2,4),
        # Previous day
        "prev_high": round(H,4), "prev_low": round(L,4), "prev_close": round(C,4),
        # Standard position flags
        "above_pivot":  today > P,  "above_r1": today > R1, "above_r2": today > R2,
        "below_s1":     today < S1, "below_s2": today < S2,
        "near_pivot":   near(P),    "near_s1":  near(S1),   "near_s2": near(S2),
        "near_s3":      near(S3),   "near_r1":  near(R1),   "near_r2": near(R2),
        # B574: doji-only wide-band flags (1.5pct tolerance). Consumed
        # exclusively by strat_doji_at_support + strat_doji_at_resistance_short.
        "near_s1_wide": near_wide(S1), "near_s2_wide": near_wide(S2),
        "near_r1_wide": near_wide(R1), "near_r2_wide": near_wide(R2),
        # CPR flags
        "above_cpr": today > cpr_top, "inside_cpr": cpr_bottom <= today <= cpr_top,
        "below_cpr": today < cpr_bottom,
        # Camarilla flags (BUG-09 RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10:
        # below_cam_s3 + below_cam_s4 added for symmetry with above_cam_r3/r4;
        # screener.py:153 references below_cam_s3 which previously returned None)
        "near_cam_s3": near(cs3), "near_cam_s4": near(cs4),
        "near_cam_r3": near(cr3), "above_cam_r3": today > cr3,
        "above_cam_r4": today > cr4,
        "below_cam_s3": today < cs3, "below_cam_s4": today < cs4,
        # Woodie's flags
        "above_wood_p": today > wp, "near_wood_s1": near(ws1), "near_wood_r1": near(wr1),
        # Previous day flags
        "above_prev_high": today > H,  "below_prev_low":  today < L,
        # B616 (2026-06-07 owner-directed LOW-priority not-s.get refactor):
        # symmetric pair so turtle_soup_long/_short can switch from
        # `not s.get("below_prev_low"|"above_prev_high", True)` (silent-gap
        # fragile) to positive `above_prev_low` / `below_prev_high` signals.
        # Strict-less-than convention matches existing strict-greater-than.
        "below_prev_high": today < H,  "above_prev_low":  today > L,
        "near_prev_high":  near(H),    "near_prev_low":   near(L),
        "near_prev_close": near(C),
        # Batch 211 (ORB stocks-in-play 2026-05-17): gap pct + intraday
        # range signals for ORB-style daily-bar entries. True intraday
        # ORB (5-min bars per Zarattini 2024 SSRN 4729284) requires
        # minute-bar pipeline; daily proxy uses today's open vs prev
        # close as the gap and today's range as a same-day breakout
        # confirmation. Acknowledged approximation - documented in
        # ORB strategies inline.
        "gap_up_pct":      round((df["open"].iloc[-1] - C) / C * 100, 3) if C else 0.0,
        "gap_dn_pct":      round((C - df["open"].iloc[-1]) / C * 100, 3) if C else 0.0,
        "gap_up_2pct":     ((df["open"].iloc[-1] - C) / C) > 0.02 if C else False,
        "gap_dn_2pct":     ((C - df["open"].iloc[-1]) / C) > 0.02 if C else False,
        "close_above_open": today > df["open"].iloc[-1],
        "close_below_open": today < df["open"].iloc[-1],
    }


def compute_fibonacci(df: pd.DataFrame, lookback: int = 50) -> dict:
    if len(df) < 10:
        return {}
    w  = df.tail(min(lookback, len(df)))
    sh = w["high"].max();  sl = w["low"].min()
    d  = sh - sl;          today = df["close"].iloc[-1]
    near = lambda lvl: abs(today - lvl) / max(abs(lvl), 0.01) < 0.005
    # Batch 574 (2026-06-04 narrow-scope fix per
    # feedback_narrow_scope_blast_radius): add `_wide` variant at 1.5pct
    # for at_key_fib_wide. Doji strategies consume the _wide variant;
    # other 12 strategies that use at_key_fib stay at the narrow 0.5pct.
    near_wide = lambda lvl: abs(today - lvl) / max(abs(lvl), 0.01) < 0.015
    lvls = {
        "fib_236": sh - 0.236*d, "fib_382": sh - 0.382*d,
        "fib_500": sh - 0.500*d, "fib_618": sh - 0.618*d,
        "fib_786": sh - 0.786*d,
        "fib_ext_127": sh + 0.272*d, "fib_ext_162": sh + 0.618*d,
        "swing_high": sh, "swing_low": sl,
    }
    result = {k: round(v, 4) for k, v in lvls.items()}
    for k in ["fib_236","fib_382","fib_500","fib_618","fib_786"]:
        result[f"near_{k}"] = near(lvls[k])
    result["at_key_fib"] = result["near_fib_382"] or result["near_fib_500"] or result["near_fib_618"]
    # B574: doji-only wide-band Fib flag (1.5pct). Consumed exclusively
    # by strat_doji_at_support + strat_doji_at_resistance_short.
    result["at_key_fib_wide"] = (
        near_wide(lvls["fib_382"]) or
        near_wide(lvls["fib_500"]) or
        near_wide(lvls["fib_618"])
    )
    return result


def compute_vwap(df: pd.DataFrame) -> dict:
    if len(df) < 5:
        return {}
    tp  = (df["high"] + df["low"] + df["close"]) / 3
    vol = df["volume"]
    vwap_s = (tp * vol).cumsum() / vol.cumsum()
    vwap   = _safe_float(vwap_s.iloc[-1])
    std    = _safe_float(tp.tail(20).std())
    close  = _safe_float(df["close"].iloc[-1])
    out = {
        "vwap":          round(vwap, 4),
        "vwap_upper_1":  round(vwap + std, 4),
        "vwap_upper_2":  round(vwap + 2*std, 4),
        "vwap_lower_1":  round(vwap - std, 4),
        "vwap_lower_2":  round(vwap - 2*std, 4),
        "above_vwap":    close > vwap,
        "pct_from_vwap": round((close - vwap) / vwap * 100, 3) if vwap else 0,
    }
    # Batch 205 (Pivot/CPR optimization 2026-05-17): Anchored VWAP per
    # Brian Shannon (2022) "Maximum Trading Gains With Anchored VWAP".
    # Anchor at recent swing low / high to compute institutional reference
    # level. Pivot/CPR breakouts above AVWAP are markedly higher quality
    # than naive pivot breaks (CMT Association whitepaper). Four anchors:
    #   - 252-day swing low (1-year reference)
    #   -  50-day swing low (recent leg)
    #   -  20-day swing high (recent breakout reference)
    #   -  20-day swing low  (Batch 598 - symmetric to 20high so dual
    #                         breakout strategies can use a matched-
    #                         timeframe anchor pair {20low, 20high})
    for lookback, key in [(252, "252low"), (50, "50low"), (20, "20high"), (20, "20low")]:
        if len(df) < lookback + 5:
            continue
        window = df.tail(lookback)
        if "high" in key:
            anchor_idx = window["high"].idxmax()
        else:
            anchor_idx = window["low"].idxmin()
        try:
            anchor_pos = df.index.get_loc(anchor_idx)
        except KeyError:
            continue
        # Slice from anchor forward
        post = df.iloc[anchor_pos:]
        if len(post) < 2:
            continue
        tp_post = (post["high"] + post["low"] + post["close"]) / 3
        vol_post = post["volume"]
        avwap_s = (tp_post * vol_post).cumsum() / vol_post.cumsum().replace(0, np.nan)
        avwap = _safe_float(avwap_s.iloc[-1])
        if avwap <= 0:
            continue
        out[f"avwap_{key}"]              = round(avwap, 4)
        out[f"above_avwap_{key}"]        = close > avwap
        # B612 F2 (2026-06-07 owner+AI critique post-B608/B609/B610):
        # symmetric below_avwap_* signal added to fix silent-gap bug
        # in volume_spike_breakout + volume_spike_breakout_retest SHORT
        # sides which used `not s.get("above_avwap_20high")` (no default,
        # so missing key would auto-pass). Now those strategies can
        # consume below_avwap_20high explicitly (positive gate, default
        # False if absent).
        out[f"below_avwap_{key}"]        = close < avwap
        out[f"pct_from_avwap_{key}"]     = round((close - avwap) / avwap * 100, 3)
    return out


# -----------------------------------------------------------------------------
# MOMENTUM
# -----------------------------------------------------------------------------

def compute_rsi(df: pd.DataFrame) -> dict:
    """RSI computation using Wilder exponential smoothing.

    BUG-28 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 3 2026-05-10:
    Fallback path (when pandas_ta unavailable) previously used `rolling(p).mean()`
    which is Simple Moving Average, NOT Wilder's EMA smoothing. Industry-standard
    RSI per Wilder (1978) uses `ewm(alpha=1/p, adjust=False)` which gives equal
    weight to all historical periods via exponential decay. Fix applies Wilder
    smoothing in the fallback path; pandas_ta path already uses Wilder internally.

    Batch 204 (Bollinger optimization 2026-05-17): added RSI(2) Connors-RSI
    period. Larry Connors' canonical mean-reversion gate: RSI(2) < 5 entry
    + price > 200-MA filter. Documented Sharpe lift on equity backtests
    (Quantified Strategies 2024). Period 2 is short-window noise-heavy
    on purpose; Connors discipline requires combination with regime filter.
    """
    result = {}
    for p in [2, 9, 14, 21]:
        if len(df) < p + 2:
            continue
        if _HAS_TA:
            s = ta.rsi(df["close"], length=p)
        else:
            d = df["close"].diff()
            # BUG-28 fix: Wilder smoothing (alpha=1/p) instead of simple rolling mean.
            # Wilder RSI: weight = 1/p for newest, with exponential decay backward.
            g = d.clip(lower=0).ewm(alpha=1 / p, adjust=False).mean()
            ls = (-d.clip(upper=0)).ewm(alpha=1 / p, adjust=False).mean()
            s = 100 - 100 / (1 + g / ls.replace(0, np.nan))
        if s is None or s.empty:
            continue
        v = _safe_float(s.iloc[-1], 50)
        pv = _safe_float(s.iloc[-2], 50)
        result[f"rsi_{p}"]             = round(v, 2)
        result[f"rsi_{p}_oversold"]    = v < 30
        result[f"rsi_{p}_overbought"]  = v > 70
        result[f"rsi_{p}_bullish"]     = v > 50
        result[f"rsi_{p}_rising"]      = v > pv
        result[f"rsi_{p}_extreme_os"]  = v < 20
        result[f"rsi_{p}_extreme_ob"]  = v > 80
    return result


def compute_stochrsi(df: pd.DataFrame, period: int = 14) -> dict:
    if len(df) < period * 2:
        return {}
    if _HAS_TA:
        s = ta.stochrsi(df["close"], length=period)
        if s is None or s.empty:
            return {}
        cols = s.columns.tolist()
        k = _safe_float(s[cols[0]].iloc[-1], 50)
        d = _safe_float(s[cols[1]].iloc[-1] if len(cols) > 1 else k, 50)
    else:
        d_s = df["close"].diff()
        g = d_s.clip(lower=0).rolling(period).mean()
        l = (-d_s.clip(upper=0)).rolling(period).mean()
        rsi = 100 - 100 / (1 + g / l.replace(0, np.nan))
        rsi_min = rsi.rolling(period).min()
        rsi_max = rsi.rolling(period).max()
        k_s = (rsi - rsi_min) / (rsi_max - rsi_min).replace(0, np.nan) * 100
        d_val = k_s.rolling(3).mean()
        k, d = _safe_float(k_s.iloc[-1], 50), _safe_float(d_val.iloc[-1], 50)
    return {
        "stochrsi_k":         round(k, 2),
        "stochrsi_d":         round(d, 2),
        "stochrsi_oversold":  k < 20,
        "stochrsi_overbought": k > 80,
        "stochrsi_cross_up":  k > d and k < 80,
        "stochrsi_cross_dn":  k < d and k > 20,
    }


def compute_stochastic(df: pd.DataFrame) -> dict:
    if len(df) < 17:
        return {}
    if _HAS_TA:
        s = ta.stoch(df["high"], df["low"], df["close"], k=14, d=3, smooth_k=3)
        if s is None or s.empty:
            return {}
        cols = s.columns.tolist()
        k = _safe_float(s[cols[0]].iloc[-1], 50)
        d = _safe_float(s[cols[1]].iloc[-1] if len(cols) > 1 else k, 50)
        pk = _safe_float(s[cols[0]].iloc[-2] if len(s) > 1 else k, 50)
        pd_v = _safe_float(s[cols[1]].iloc[-2] if len(cols) > 1 and len(s) > 1 else d, 50)
    else:
        l14 = df["low"].rolling(14).min()
        h14 = df["high"].rolling(14).max()
        fk  = 100*(df["close"]-l14)/(h14-l14).replace(0,np.nan)
        sk  = fk.rolling(3).mean(); sd = sk.rolling(3).mean()
        k,d,pk,pd_v = (_safe_float(sk.iloc[-1],50), _safe_float(sd.iloc[-1],50),
                       _safe_float(sk.iloc[-2],50), _safe_float(sd.iloc[-2],50))
    return {
        "stoch_k":             round(k, 2), "stoch_d": round(d, 2),
        "stoch_oversold":      k < 20,      "stoch_overbought": k > 80,
        "stoch_bullish_cross": k > d and pk <= pd_v,
        "stoch_bearish_cross": k < d and pk >= pd_v,
    }


def compute_macd(df: pd.DataFrame) -> dict:
    result = {}
    for fast, slow, sig in [(12,26,9),(8,21,5)]:
        if len(df) < slow + sig + 2:
            continue
        key = f"macd_{fast}_{slow}_{sig}"
        if _HAS_TA:
            m = ta.macd(df["close"], fast=fast, slow=slow, signal=sig)
            if m is None or m.empty:
                continue
            cols = m.columns.tolist()
            ml  = _safe_float(m[cols[0]].iloc[-1])
            ms  = _safe_float(m[cols[1]].iloc[-1] if len(cols)>1 else 0)
            mh  = _safe_float(m[cols[2]].iloc[-1] if len(cols)>2 else 0)
            pmh = _safe_float(m[cols[2]].iloc[-2] if len(cols)>2 and len(m)>1 else 0)
        else:
            ef = df["close"].ewm(span=fast,adjust=False).mean()
            es = df["close"].ewm(span=slow,adjust=False).mean()
            ml_s  = ef - es
            ms_s  = ml_s.ewm(span=sig,adjust=False).mean()
            mh_s  = ml_s - ms_s
            ml,ms,mh  = _safe_float(ml_s.iloc[-1]),_safe_float(ms_s.iloc[-1]),_safe_float(mh_s.iloc[-1])
            pmh = _safe_float(mh_s.iloc[-2] if len(mh_s)>1 else 0)
        result[f"{key}_line"]         = round(ml,4)
        result[f"{key}_signal"]       = round(ms,4)
        result[f"{key}_hist"]         = round(mh,4)
        result[f"{key}_bullish"]      = mh > 0
        # B609 F2 (2026-06-07 owner directive break_retest_confluence
        # walk): explicit macd_*_bearish signal added symmetric to
        # _bullish to fix the silent-gap bug where strat_break_retest
        # _confluence SHORT side used `not s.get(_bullish)` which
        # auto-passed when the key was missing.
        result[f"{key}_bearish"]      = mh < 0
        result[f"{key}_crossover_up"] = mh > 0 and pmh <= 0
        result[f"{key}_crossover_dn"] = mh < 0 and pmh >= 0
    return result


def compute_ppo(df: pd.DataFrame, fast: int = 12, slow: int = 26, sig: int = 9) -> dict:
    if len(df) < slow + sig + 2:
        return {}
    ef  = df["close"].ewm(span=fast, adjust=False).mean()
    es  = df["close"].ewm(span=slow, adjust=False).mean()
    ppo = (ef - es) / es.replace(0, np.nan) * 100
    ppo_sig  = ppo.ewm(span=sig, adjust=False).mean()
    ppo_hist = ppo - ppo_sig
    v,pv = _safe_float(ppo.iloc[-1]),_safe_float(ppo.iloc[-2])
    h,ph = _safe_float(ppo_hist.iloc[-1]),_safe_float(ppo_hist.iloc[-2])
    return {
        "ppo":              round(v,4),
        "ppo_signal":       round(_safe_float(ppo_sig.iloc[-1]),4),
        "ppo_hist":         round(h,4),
        "ppo_bullish":      h > 0,
        "ppo_crossover_up": h > 0 and ph <= 0,
        "ppo_crossover_dn": h < 0 and ph >= 0,
    }


def compute_williams_r(df: pd.DataFrame, period: int = 14) -> dict:
    if len(df) < period:
        return {}
    hh = df["high"].rolling(period).max()
    ll = df["low"].rolling(period).min()
    wr = -100*(hh - df["close"]) / (hh - ll).replace(0,np.nan)
    v  = _safe_float(wr.iloc[-1], -50)
    pv = _safe_float(wr.iloc[-2], -50)
    return {
        "williams_r":            round(v,2),
        "williams_r_oversold":   v < -80,
        "williams_r_overbought": v > -20,
        "williams_r_rising":     v > pv,
    }


def compute_roc(df: pd.DataFrame, period: int = 12) -> dict:
    if len(df) < period + 2:
        return {}
    v  = (df["close"].iloc[-1] - df["close"].iloc[-period-1]) / df["close"].iloc[-period-1] * 100
    pv = (df["close"].iloc[-2] - df["close"].iloc[-period-2]) / df["close"].iloc[-period-2] * 100
    return {
        "roc_12":          round(v,3),
        "roc_positive":    v > 0,
        "roc_turning_up":  v > 0 and pv <= 0,
        "roc_turning_dn":  v < 0 and pv >= 0,
    }


def compute_awesome_oscillator(df: pd.DataFrame) -> dict:
    if len(df) < 34:
        return {}
    hl2  = (df["high"] + df["low"]) / 2
    ao   = hl2.rolling(5).mean() - hl2.rolling(34).mean()
    v    = _safe_float(ao.iloc[-1])
    pv   = _safe_float(ao.iloc[-2])
    ppv  = _safe_float(ao.iloc[-3] if len(ao) > 2 else 0)
    return {
        "ao":              round(v,4),
        "ao_positive":     v > 0,
        "ao_cross_up":     v > 0 and pv <= 0,
        "ao_cross_dn":     v < 0 and pv >= 0,
        "ao_twin_peaks_bull": v < 0 and pv < v and ppv > pv,   # two valleys, second higher
    }


def compute_ultimate_oscillator(df: pd.DataFrame) -> dict:
    if len(df) < 28:
        return {}
    c  = df["close"];  h = df["high"];  l = df["low"]
    pc = c.shift(1)
    bp = c - pd.concat([l, pc], axis=1).min(axis=1)
    tr = pd.concat([h, pc], axis=1).max(axis=1) - pd.concat([l, pc], axis=1).min(axis=1)
    def avg(bp, tr, p):
        return bp.rolling(p).sum() / tr.rolling(p).sum().replace(0, np.nan)
    uo = 100 * (4*avg(bp,tr,7) + 2*avg(bp,tr,14) + avg(bp,tr,28)) / 7
    v  = _safe_float(uo.iloc[-1], 50)
    return {
        "uo":             round(v,2),
        "uo_oversold":    v < 30,
        "uo_overbought":  v > 70,
    }


# -----------------------------------------------------------------------------
# TREND
# -----------------------------------------------------------------------------

def compute_ema_sma(df: pd.DataFrame) -> dict:
    result = {}
    for fast, slow in [(9,21),(20,50),(50,200)]:
        if len(df) < slow + 2:
            continue
        ef  = df["close"].ewm(span=fast, adjust=False).mean()
        es  = df["close"].ewm(span=slow, adjust=False).mean()
        sf  = df["close"].rolling(fast).mean()
        ss  = df["close"].rolling(slow).mean()
        efv,esv = _safe_float(ef.iloc[-1]),_safe_float(es.iloc[-1])
        efp,esp = _safe_float(ef.iloc[-2]),_safe_float(es.iloc[-2])
        sfv,ssv = _safe_float(sf.iloc[-1]),_safe_float(ss.iloc[-1])
        sfp,ssp = _safe_float(sf.iloc[-2]),_safe_float(ss.iloc[-2])
        close   = _safe_float(df["close"].iloc[-1])
        result[f"ema_{fast}_{slow}_bullish"]      = efv > esv
        result[f"ema_{fast}_{slow}_golden_cross"] = efv > esv and efp <= esp
        result[f"ema_{fast}_{slow}_death_cross"]  = efv < esv and efp >= esp
        result[f"sma_{fast}_{slow}_bullish"]      = sfv > ssv
        result[f"sma_{fast}_{slow}_golden_cross"] = sfv > ssv and sfp <= ssp
        result[f"price_above_ema_{fast}"]         = close > efv
        result[f"price_above_ema_{slow}"]         = close > esv
        result[f"price_above_sma_{slow}"]         = close > ssv
        # B609 F2 (2026-06-07 owner directive break_retest_confluence
        # walk): explicit below_ema_N signals symmetric to price_above
        # _ema_N to fix the silent-gap bug where strat_break_retest
        # _confluence SHORT side used `not s.get(price_above_ema_N)`
        # which auto-passed when the key was missing.
        result[f"below_ema_{fast}"]               = close < efv
        result[f"below_ema_{slow}"]               = close < esv
        # B630 F2 (2026-06-08 owner-directed mega-sweep): symmetric
        # below_sma_{fast,slow} signals for the 4 strategies that
        # previously used `not s.get("price_above_sma_{fast,slow}")`
        # silent-gap pattern.
        result[f"below_sma_{fast}"]               = close < sfv
        result[f"below_sma_{slow}"]               = close < ssv
    return result


def compute_dema_tema(df: pd.DataFrame, period: int = 20) -> dict:
    if len(df) < period * 3:
        return {}
    c    = df["close"]
    ema1 = c.ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    dema = 2*ema1 - ema2
    tema = 3*ema1 - 3*ema2 + ema3
    dv,tv = _safe_float(dema.iloc[-1]),_safe_float(tema.iloc[-1])
    dp,tp = _safe_float(dema.iloc[-2]),_safe_float(tema.iloc[-2])
    close = _safe_float(c.iloc[-1])
    return {
        "dema":            round(dv,4), "tema": round(tv,4),
        "tema_above_dema": tv > dv,
        "tema_cross_up":   tv > dv and tp <= dp,
        "tema_cross_dn":   tv < dv and tp >= dp,
        "price_above_tema": close > tv,
        "price_above_dema": close > dv,
    }


def compute_adx(df: pd.DataFrame, period: int = 14) -> dict:
    if len(df) < period * 2 + 2:
        return {}
    if _HAS_TA:
        a = ta.adx(df["high"], df["low"], df["close"], length=period)
        if a is None or a.empty:
            return {}
        cols = a.columns.tolist()
        adx_v  = _safe_float(a[cols[0]].iloc[-1])
        dip    = _safe_float(a[cols[1]].iloc[-1] if len(cols)>1 else 0)
        dim    = _safe_float(a[cols[2]].iloc[-1] if len(cols)>2 else 0)
    else:
        h,l,c = df["high"],df["low"],df["close"]
        tr = pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
        atr = tr.ewm(alpha=1/period,adjust=False).mean()
        up,dn = h.diff(),-l.diff()
        dmp = up.where((up>dn)&(up>0),0.0)
        dmm = dn.where((dn>up)&(dn>0),0.0)
        dip = 100*dmp.ewm(alpha=1/period,adjust=False).mean()/atr.replace(0,np.nan)
        dim = 100*dmm.ewm(alpha=1/period,adjust=False).mean()/atr.replace(0,np.nan)
        dx  = 100*(dip-dim).abs()/(dip+dim).replace(0,np.nan)
        adx_v = _safe_float(dx.ewm(alpha=1/period,adjust=False).mean().iloc[-1])
        dip,dim = _safe_float(dip.iloc[-1]),_safe_float(dim.iloc[-1])
    padx = _safe_float(df["close"].iloc[-2]) if len(df)>1 else adx_v
    return {
        "adx":           round(adx_v,2),
        "adx_di_plus":   round(dip,2),
        "adx_di_minus":  round(dim,2),
        "adx_trending":  adx_v > 25,
        "adx_strong":    adx_v > 40,
        "adx_di_bull":   dip > dim,
        "adx_cross_up":  adx_v > 25 and padx <= 25,
    }


def compute_parabolic_sar(df: pd.DataFrame) -> dict:
    """Parabolic SAR with correct flip detection.

    BUG-055 fix 2026-05-13: previous flip detection used `pclose > psar_long` as a proxy
    for the prior bar's bullish state, which is incorrect (psar_long is the CURRENT SAR
    value, not the prior bar's SAR). Fix: track prev_bullish explicitly in both paths.
    - pandas_ta path: flip_up = current bar has PSARl not-NaN AND prev bar had PSARl NaN.
    - manual path: track prev_bullish at start of each loop iteration.
    """
    if len(df) < 10:
        return {}
    if _HAS_TA:
        s = ta.psar(df["high"], df["low"], df["close"])
        if s is None or s.empty:
            return {}
        cols = s.columns.tolist()
        # psar returns PSARl (long/bullish SAR) and PSARs (short/bearish SAR).
        # PSARl is NaN when in short mode; PSARs is NaN when in long mode.
        long_col  = [c for c in cols if "l" in c.lower()]
        short_col = [c for c in cols if "s" in c.lower()]
        if long_col:
            psar_long_cur  = s[long_col[0]].iloc[-1]
            psar_long_prev = s[long_col[0]].iloc[-2] if len(s) > 1 else psar_long_cur
            psar_long  = _safe_float(psar_long_cur, 0)
            close      = _safe_float(df["close"].iloc[-1])
            bullish      = (not (psar_long_cur is None) and not pd.isna(psar_long_cur)
                            and float(psar_long_cur) > 0)
            prev_bullish = (not (psar_long_prev is None) and not pd.isna(psar_long_prev)
                            and float(psar_long_prev) > 0)
        else:
            bullish = True
            prev_bullish = True
            psar_long = 0
    else:
        # Batch 545 OPT-C: Numba JIT the SAR state machine. Pre-Numba
        # path used pure-Python loop with list indexing -- ~30-50ms
        # per call on 250-bar history. Numba-compiled inner loop runs
        # at ~0.5-1ms per call.
        h_arr = df["high"].to_numpy(dtype=np.float64, na_value=0.0)
        l_arr = df["low"].to_numpy(dtype=np.float64, na_value=0.0)
        psar_long, bullish_int, prev_bullish_int = (
            _parabolic_sar_inner_loop_numba(h_arr, l_arr)
        )
        bullish = bool(bullish_int)
        prev_bullish = bool(prev_bullish_int)
    close = _safe_float(df["close"].iloc[-1])
    return {
        "psar_bullish": bullish,
        "psar_value":   round(psar_long, 4),
        "psar_flip_up": bullish and not prev_bullish,   # BUG-055: true flip, not approximation
        "psar_flip_dn": not bullish and prev_bullish,   # BUG-055: true flip, not approximation
    }


# -----------------------------------------------------------------------------
# NOTE ON VWAP APPROXIMATION
# True VWAP is an intraday metric that resets every day. On daily bars we
# approximate it as (High + Low + Close) / 3. This differs from real intraday
# VWAP that traders see on screens. The 7 strategies using VWAP conditions
# (prev_day_high_break, prev_day_low_bounce, squeeze_breakout, volume_spike_breakout,
# bb_squeeze_volume, inside_bar_breakout, cpr_narrow_momentum) use this
# approximation. In live trading, real intraday VWAP should be used.
# -----------------------------------------------------------------------------

def compute_ichimoku(df: pd.DataFrame) -> dict:
    if len(df) < 52:
        return {}
    def mid(p): return (df["high"].rolling(p).max() + df["low"].rolling(p).min()) / 2
    tenkan  = mid(9)
    kijun   = mid(26)
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    senkou_b = mid(52).shift(26)
    t,k     = _safe_float(tenkan.iloc[-1]),_safe_float(kijun.iloc[-1])
    pt,pk   = _safe_float(tenkan.iloc[-2]),_safe_float(kijun.iloc[-2])
    sa      = _safe_float(senkou_a.iloc[-1])
    sb      = _safe_float(senkou_b.iloc[-1])
    close   = _safe_float(df["close"].iloc[-1])
    above_cloud = close > max(sa,sb) if sa and sb else False
    below_cloud = close < min(sa,sb) if sa and sb else False
    out = {
        "ichi_tenkan":      round(t,4), "ichi_kijun": round(k,4),
        "ichi_senkou_a":    round(sa,4), "ichi_senkou_b": round(sb,4),
        "ichi_above_cloud": above_cloud, "ichi_below_cloud": below_cloud,
        "ichi_tk_bullish":  t > k,
        "ichi_tk_cross_up": t > k and pt <= pk,
        "ichi_tk_bearish":  t < k,
        "ichi_tk_cross_dn": t < k and pt >= pk,
        "ichi_cloud_thick": abs(sa-sb) > abs(sa)*0.01 if sa else False,
    }
    # Batch 207 (Ichimoku optimization 2026-05-17): multi-timeframe Kumo
    # gate per Linda Raschke. Resample daily -> weekly to compute the
    # weekly Ichimoku cloud position; use as regime filter for daily
    # entries. Requires >=52 weeks (52*5 = 260 daily bars) for full
    # weekly Senkou B (mid_52 weekly).
    if len(df) >= 260 and isinstance(df.index, pd.DatetimeIndex):
        try:
            wk = df.resample("W").agg({
                "high": "max", "low": "min", "close": "last",
                "open": "first", "volume": "sum",
            }).dropna()
            if len(wk) >= 52:
                def wmid(p): return (wk["high"].rolling(p).max() + wk["low"].rolling(p).min()) / 2
                w_tenkan  = wmid(9)
                w_kijun   = wmid(26)
                w_senkou_a = ((w_tenkan + w_kijun) / 2).shift(26)
                w_senkou_b = wmid(52).shift(26)
                wsa = _safe_float(w_senkou_a.iloc[-1])
                wsb = _safe_float(w_senkou_b.iloc[-1])
                wclose = _safe_float(wk["close"].iloc[-1])
                w_above = wclose > max(wsa, wsb) if wsa and wsb else False
                w_below = wclose < min(wsa, wsb) if wsa and wsb else False
                out["ichi_weekly_above_cloud"] = w_above
                out["ichi_weekly_below_cloud"] = w_below
                out["ichi_weekly_in_cloud"]    = not (w_above or w_below)
        except Exception:
            pass
    return out


# Batch 544 OPT-C pivot (2026-06-02): Numba JIT supertrend state-tracking
# inner loop. Profile showed compute_supertrend = 104ms/call dominated
# by 4 separate `float(series.iloc[i])` indexings PER ITERATION (4 *
# 1044 iterations = 4176 pandas indexings per call). Pre-extract numpy
# arrays + run loop in compiled code = ~10-50x speedup on the inner
# loop. Module-level cache for the JIT-compiled function avoids
# re-compilation overhead.
try:
    from numba import njit as _njit  # noqa: F401
    _HAS_NUMBA = True
except Exception:
    _HAS_NUMBA = False
    _njit = lambda f: f  # noqa: E731  -- no-op decorator fallback


@_njit(cache=True)
def _parabolic_sar_inner_loop_numba(
    h: np.ndarray, l: np.ndarray,
) -> tuple:
    """Batch 545 OPT-C: JIT-compiled Parabolic SAR state machine.

    Inputs: high, low numpy arrays. Output: (final_sar, bullish,
    prev_bullish) where bullish/prev_bullish are returned as int (1/0)
    because Numba is happier with int returns than Python bool.
    """
    af_start = 0.02
    af_step = 0.02
    af_max = 0.20
    n = h.shape[0]
    sar = l[0]
    af = af_start
    ep = h[0]
    bullish = 1
    prev_bullish = 1
    for i in range(1, n):
        prev_bullish = bullish
        if bullish == 1:
            sar = sar + af * (ep - sar)
            # min(sar, l[i-1], l[max(0, i-2)])
            l_prev = l[i - 1]
            l_pprev = l[i - 2] if i >= 2 else l[i - 1]
            if l_prev < sar:
                sar = l_prev
            if l_pprev < sar:
                sar = l_pprev
            if l[i] < sar:
                bullish = 0
                sar = ep
                ep = l[i]
                af = af_start
            else:
                if h[i] > ep:
                    ep = h[i]
                    new_af = af + af_step
                    af = new_af if new_af < af_max else af_max
        else:
            sar = sar + af * (ep - sar)
            h_prev = h[i - 1]
            h_pprev = h[i - 2] if i >= 2 else h[i - 1]
            if h_prev > sar:
                sar = h_prev
            if h_pprev > sar:
                sar = h_pprev
            if h[i] > sar:
                bullish = 1
                sar = ep
                ep = h[i]
                af = af_start
            else:
                if l[i] < ep:
                    ep = l[i]
                    new_af = af + af_step
                    af = new_af if new_af < af_max else af_max
    return sar, bullish, prev_bullish


@_njit(cache=True)
def _supertrend_inner_loop_numba(
    ub: np.ndarray, lb: np.ndarray, close: np.ndarray,
) -> tuple:
    """JIT-compiled supertrend state-tracking. Takes pre-computed
    upper-band / lower-band / close numpy arrays + returns (st, bull)
    arrays. Inner-loop semantics IDENTICAL to the pre-Numba pandas
    implementation."""
    n = ub.shape[0]
    st = np.zeros(n, dtype=np.float64)
    bull = np.ones(n, dtype=np.bool_)
    for i in range(1, n):
        ub_prev = ub[i - 1]
        lb_prev = lb[i - 1]
        ub_cur = ub[i]
        lb_cur = lb[i]
        cl_prev = close[i - 1]
        cl_cur = close[i]
        if cl_prev > lb_prev:
            if lb_prev > lb_cur:
                lb_cur = lb_prev
        if cl_prev < ub_prev:
            if ub_prev < ub_cur:
                ub_cur = ub_prev
        if st[i - 1] == ub_prev:
            st[i] = lb_cur if cl_cur > ub_prev else ub_cur
        else:
            st[i] = ub_cur if cl_cur < lb_prev else lb_cur
        bull[i] = cl_cur > st[i]
    return st, bull


def compute_supertrend(df: pd.DataFrame, period: int = 7, mult: float = 3.0) -> dict:
    if len(df) < period + 2:
        return {}
    atr  = _atr_series(df, period)
    hl2  = (df["high"] + df["low"]) / 2
    ub   = hl2 + mult*atr
    lb   = hl2 - mult*atr
    # Batch 544: hand off to JIT-compiled inner loop via numpy arrays.
    # Pre-extracting arrays once is much cheaper than 4 `.iloc[i]` calls
    # per loop iteration.
    ub_arr = ub.to_numpy(dtype=np.float64, na_value=0.0)
    lb_arr = lb.to_numpy(dtype=np.float64, na_value=0.0)
    cl_arr = df["close"].to_numpy(dtype=np.float64, na_value=0.0)
    st_arr, bull_arr = _supertrend_inner_loop_numba(ub_arr, lb_arr, cl_arr)
    return {
        "supertrend_bullish":  bool(bull_arr[-1]),
        # B630 F2 (2026-06-08 owner-directed mega-sweep): symmetric
        # supertrend_bearish for the 3 strategies that previously used
        # `not s.get("supertrend_bullish")` silent-gap pattern.
        "supertrend_bearish":  not bool(bull_arr[-1]),
        "supertrend_value":    round(float(st_arr[-1]), 4),
        "supertrend_flip_up":  bool(bull_arr[-1]) and not bool(bull_arr[-2]),
        "supertrend_flip_dn":  not bool(bull_arr[-1]) and bool(bull_arr[-2]),
    }


def compute_chandelier_exit(
    df: pd.DataFrame,
    period: int = 22,
    mult: float = 3.0,
) -> dict:
    """DEC-432 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 53 2026-05-11
    (owner-approved Path C). Chandelier exit (Charles LeBeau): trailing stop
    anchored to highest-high (long) or lowest-low (short) over `period` bars
    less an ATR-multiple buffer.

    chandelier_long  = highest_high(period) - ATR(period) * mult
    chandelier_short = lowest_low(period)   + ATR(period) * mult

    A long position should exit when close < chandelier_long; a short
    position when close > chandelier_short. flip_dn / flip_up signal the
    bar on which that cross occurred.

    Defaults match Charles LeBeau's original spec (22, 3.0). Returns empty
    dict on insufficient history (< period + 1 bars).
    """
    if len(df) < period + 1:
        return {}
    atr = _atr_series(df, period)
    highest = df["high"].rolling(period).max()
    lowest = df["low"].rolling(period).min()
    chand_long  = highest - mult * atr
    chand_short = lowest  + mult * atr
    close = df["close"]
    long_bullish_now  = bool(float(close.iloc[-1]) > float(chand_long.iloc[-1]))
    long_bullish_prev = bool(float(close.iloc[-2]) > float(chand_long.iloc[-2]))
    short_bearish_now  = bool(float(close.iloc[-1]) < float(chand_short.iloc[-1]))
    short_bearish_prev = bool(float(close.iloc[-2]) < float(chand_short.iloc[-2]))
    return {
        "chandelier_long_value":  round(float(chand_long.iloc[-1]), 4),
        "chandelier_short_value": round(float(chand_short.iloc[-1]), 4),
        "chandelier_long_bullish":  long_bullish_now,
        "chandelier_short_bearish": short_bearish_now,
        "chandelier_long_flip_dn":  long_bullish_prev and not long_bullish_now,
        "chandelier_short_flip_up": short_bearish_prev and not short_bearish_now,
    }


def _wma(series: pd.Series, period: int) -> pd.Series:
    """Weighted Moving Average -- linearly increasing weights (most recent = period weight).

    BUG-054 fix 2026-05-13: HMA formula requires WMA(n/2) and WMA(n), not SMA.
    Weights: [1, 2, 3, ..., period] normalised by period*(period+1)/2.

    Batch 545 OPT-C: replaced `rolling.apply(lambda)` with vectorized
    `np.convolve` (~50-100x faster). Each WMA call previously dispatched
    a Python lambda per rolling window via pandas rolling.apply (slow);
    np.convolve does the equivalent linear-combination in one C-level
    op. Output is identical to pre-Numba implementation: first
    (period-1) values are NaN; subsequent values are the weighted mean.
    """
    n = len(series)
    if n < period:
        return pd.Series(np.full(n, np.nan), index=series.index)
    arr = series.to_numpy(dtype=np.float64)
    weights = np.arange(1, period + 1, dtype=np.float64)
    denom = weights.sum()
    # np.convolve with reversed weights gives the rolling-weighted-mean
    # the same way pandas rolling.apply does. Use 'valid' mode for
    # the (n - period + 1) valid positions; left-pad with NaN to align.
    valid = np.convolve(arr, weights[::-1], mode="valid") / denom
    out = np.empty(n, dtype=np.float64)
    out[: period - 1] = np.nan
    out[period - 1 :] = valid
    return pd.Series(out, index=series.index)


def compute_hull_ma(df: pd.DataFrame, period: int = 20) -> dict:
    """Hull Moving Average using proper WMA components.

    BUG-054 fix 2026-05-13: previous implementation used rolling().mean() (SMA) for
    all three components. HMA formula is: WMA(sqrt(n), 2*WMA(n/2, price) - WMA(n, price)).
    Using SMA instead of WMA understates the signal timing advantage of HMA vs EMA/SMA.
    Fixed to use _wma() helper throughout.
    """
    if len(df) < period * 2 + 2:
        return {}
    half = int(period / 2)
    sqr  = int(np.sqrt(period))
    wma1 = _wma(df["close"], half)
    wma2 = _wma(df["close"], period)
    hull = _wma(2 * wma1 - wma2, sqr)
    v, pv = _safe_float(hull.iloc[-1]), _safe_float(hull.iloc[-2])
    close = _safe_float(df["close"].iloc[-1])
    return {
        "hull_ma":          round(v, 4),
        "hull_bullish":     v > pv,
        "hull_flip_up":     v > pv and _safe_float(hull.iloc[-3] if len(hull) > 2 else v) >= pv,
        "hull_flip_dn":     v < pv and _safe_float(hull.iloc[-3] if len(hull) > 2 else v) <= pv,
        "price_above_hull": close > v,
    }


# -----------------------------------------------------------------------------
# VOLATILITY / BANDS
# -----------------------------------------------------------------------------

def compute_bollinger(df: pd.DataFrame) -> dict:
    result = {}
    for period, std_m in [(20,2.0),(20,1.5),(10,2.0)]:
        if len(df) < period + 2:
            continue
        key   = f"bb_{period}_{str(std_m).replace('.','')}"
        mid   = df["close"].rolling(period).mean()
        std   = df["close"].rolling(period).std()
        upper = mid + std_m*std; lower = mid - std_m*std
        m,u,l = _safe_float(mid.iloc[-1]),_safe_float(upper.iloc[-1]),_safe_float(lower.iloc[-1])
        pm,pu,pl = (_safe_float(mid.iloc[-2]),_safe_float(upper.iloc[-2]),
                    _safe_float(lower.iloc[-2]))
        close = _safe_float(df["close"].iloc[-1])
        bw    = (u-l)/m if m else 0
        result[f"{key}_upper"]      = round(u,4)
        result[f"{key}_lower"]      = round(l,4)
        result[f"{key}_mid"]        = round(m,4)
        result[f"{key}_bandwidth"]  = round(bw,4)
        result[f"{key}_above_mid"]  = close > m
        result[f"{key}_touch_lower"] = close <= l*1.005
        result[f"{key}_touch_upper"] = close >= u*0.995
        result[f"{key}_squeeze"]    = bw < 0.08
        result[f"{key}_expanding"]  = bw > (pu-pl)/pm if pm else False
    return result


def compute_keltner(df: pd.DataFrame, period: int = 20, mult: float = 2.0) -> dict:
    if len(df) < period + 2:
        return {}
    ema   = df["close"].ewm(span=period, adjust=False).mean()
    atr   = _atr_series(df, period)
    upper = ema + mult*atr; lower = ema - mult*atr
    close = _safe_float(df["close"].iloc[-1])
    return {
        "kc_upper":    round(_safe_float(upper.iloc[-1]),4),
        "kc_lower":    round(_safe_float(lower.iloc[-1]),4),
        "kc_mid":      round(_safe_float(ema.iloc[-1]),4),
        "inside_kc":   _safe_float(lower.iloc[-1]) < close < _safe_float(upper.iloc[-1]),
        "kc_touch_lower": close <= _safe_float(lower.iloc[-1])*1.005,
        "kc_touch_upper": close >= _safe_float(upper.iloc[-1])*0.995,
    }


def compute_donchian(df: pd.DataFrame) -> dict:
    """Donchian channel signals.

    Batch 584 (2026-06-04 owner-directed bug fix per Stage 4 audit):
    `breakout_up` / `breakout_dn` / `new_high` now use the PRIOR
    N-day window (excluding today) so the breakout check is "today's
    close vs prior-N high/low", matching the canonical breakout
    semantic. Pre-B584, `df["high"].rolling(N).max()` included today's
    intraday high - making `close >= rolling_max * 0.998` effectively
    require close == today_high == max-of-N (extremely rare;
    same bug pattern as B582 year_high).

    Affected strategies (6): donchian_10_breakout (dual), donchian_breakdown_short,
    volume_spike_breakout (dual), squeeze_setup_long, news_momentum_long,
    donchian_breakout_with_smart_money_long.

    `dc{N}_upper` / `_lower` / `_mid` retain current-rolling semantic
    (include today) as display-only signals; no consumer uses them
    for fire-logic.
    """
    result = {}
    for period in [10, 20]:
        if len(df) < period + 2:
            continue
        upper = df["high"].rolling(period).max()
        lower = df["low"].rolling(period).min()
        mid   = (upper + lower) / 2
        close = _safe_float(df["close"].iloc[-1])
        today_high = _safe_float(df["high"].iloc[-1])
        u,l   = _safe_float(upper.iloc[-1]),_safe_float(lower.iloc[-1])
        # B584 fix: PRIOR N-day window (excludes today) for breakout +
        # new_high comparisons. Uses df.iloc[:-1] so today's bar isn't
        # included in the level being broken.
        prior = df.iloc[:-1]
        upper_prior = _safe_float(prior["high"].tail(period).max())
        lower_prior = _safe_float(prior["low"].tail(period).min())
        result[f"dc{period}_upper"]        = round(u,4)
        result[f"dc{period}_lower"]        = round(l,4)
        result[f"dc{period}_mid"]          = round(_safe_float(mid.iloc[-1]),4)
        result[f"dc{period}_breakout_up"]  = close >= upper_prior * 0.998
        result[f"dc{period}_breakout_dn"]  = close <= lower_prior * 1.002
        # new_high: today's high exceeded prior-N-day max (expanded the
        # upper channel). Symmetric definition to the breakout flags;
        # owner-directed B584 consistency fix.
        result[f"dc{period}_new_high"]     = today_high > upper_prior
    # B591 (2026-06-04 owner directive on donchian_10_breakout Stage 4
    # walk): 1% tolerance variants for dc10 only. LOCAL signals -
    # consumed ONLY by strat_donchian_10_breakout (per owner B591
    # answer "signals consumed by donchian_10_breakout alone"). Other
    # 5 consumers of dc10_breakout_up/dn keep the 0.2% tolerance.
    if len(df) >= 12:
        prior = df.iloc[:-1]
        upper_prior_10 = _safe_float(prior["high"].tail(10).max())
        lower_prior_10 = _safe_float(prior["low"].tail(10).min())
        close = _safe_float(df["close"].iloc[-1])
        result["dc10_breakout_up_1pct"] = close >= upper_prior_10 * 0.99
        result["dc10_breakout_dn_1pct"] = close <= lower_prior_10 * 1.01
        # B592 (2026-06-05 owner directive answer (i) "Strong-breakout
        # requirement" - B591 deferred (e) for breakout-entry): close
        # must clear prior_high by at least 0.5 * ATR(14) (long) or
        # break prior_low by at least 0.5 * ATR(14) (short) to count
        # as a real breakout (filters trivial closes-just-above-level).
        # LOCAL signals - consumed by strat_donchian_10_breakout alone.
        try:
            atr14 = float(_atr_series(df, period=14).iloc[-1])
        except Exception:
            atr14 = 0.0
        if atr14 > 0:
            result["dc10_strong_breakout_up"] = close >= upper_prior_10 + 0.5 * atr14
            result["dc10_strong_breakout_dn"] = close <= lower_prior_10 - 0.5 * atr14
        else:
            result["dc10_strong_breakout_up"] = False
            result["dc10_strong_breakout_dn"] = False
    return result


def compute_atr_levels(df: pd.DataFrame, period: int = 14) -> dict:
    if len(df) < period + 2:
        return {}
    atr_s = _atr_series(df, period)
    atr   = _safe_float(atr_s.iloc[-1])
    close = _safe_float(df["close"].iloc[-1])
    return {
        "atr":              round(atr, 4),
        "atr_pct":          round(atr/close*100, 3) if close else 0,
        "entry_stop_long":  round(close - 2*atr, 4),
        "entry_stop_short": round(close + 2*atr, 4),
    }


def compute_squeeze(df: pd.DataFrame) -> dict:
    bb = compute_bollinger(df)
    kc = compute_keltner(df)
    if not bb or not kc:
        return {}
    bb_l = bb.get("bb_20_20_lower", 0)
    bb_u = bb.get("bb_20_20_upper", 0)
    kc_l = kc.get("kc_lower", 0)
    kc_u = kc.get("kc_upper", 0)
    in_squeeze = bb_l > kc_l and bb_u < kc_u
    if len(df) < 20:
        return {"squeeze_in": in_squeeze}
    # Batch 390 (owner directive 2026-05-26): producer fix for squeeze_fire_up
    # / squeeze_fire_dn. Prior formula `delta = close - mid20 + ema20`
    # produced absolute-price-level values (~$150 for AAPL) so `pmom <= 0`
    # was essentially impossible -> squeeze_fire_up never True (0/1542 sampled
    # ticker-days across 10 tickers x 4y empirical). Classic Lazy Bear squeeze
    # momentum is the LSMA of (close - midpoint20) - we use a simpler
    # close - midpoint20 momentum which gives signed values around zero
    # (37.8% <= 0 on AAPL 500-row sample). Transitions across zero become
    # measurable + squeeze_fire_up fires meaningfully.
    hh = df["high"].rolling(20).max()
    ll = df["low"].rolling(20).min()
    delta = df["close"] - (hh + ll) / 2  # relative-to-midpoint momentum
    mom   = _safe_float(delta.iloc[-1])
    pmom  = _safe_float(delta.iloc[-2])
    return {
        "squeeze_in":       in_squeeze,
        "squeeze_momentum": round(mom, 4),
        "squeeze_positive": mom > 0,
        "squeeze_fire_up":  not in_squeeze and mom > 0 and pmom <= 0,
        "squeeze_fire_dn":  not in_squeeze and mom < 0 and pmom >= 0,
    }


# -----------------------------------------------------------------------------
# VOLUME
# -----------------------------------------------------------------------------

def compute_volume(df: pd.DataFrame) -> dict:
    if len(df) < 21:
        return {}
    result = {}
    c,h,l,v = df["close"],df["high"],df["low"],df["volume"]

    # OBV - B547 OPT-C: np.sign replaces per-element Python lambda
    # (direction was 1/0/-1; np.sign returns the same on numeric Series).
    direction = np.sign(c.diff()).fillna(0)
    obv       = (direction*v).cumsum()
    obv_ma    = obv.rolling(20).mean()
    result["obv_bullish"]   = _safe_float(obv.iloc[-1]) > _safe_float(obv_ma.iloc[-1])
    # B617 F2 (2026-06-07 owner-directed external-AI critique re-fix on
    # strat_break_retest_volume): obv_bearish symmetric to obv_bullish.
    # Critique flagged that obv_rising (OBV[-1] > OBV[-5], 5-bar trend) is
    # contaminated by the breakout bar still sitting in the lookback window
    # at retest time, so the LONG OBV gate became near-tautological on
    # valid setups. obv_bullish (OBV[-1] > 20-bar MA) is a cleaner baseline.
    # break_retest_volume LONG switches to obv_bullish in B617; SHORT
    # switches to obv_bearish for symmetric framing.
    result["obv_bearish"]   = _safe_float(obv.iloc[-1]) < _safe_float(obv_ma.iloc[-1])
    result["obv_rising"]    = _safe_float(obv.iloc[-1]) > _safe_float(obv.iloc[-5])
    # B608 F2 (2026-06-07 owner directive break_retest_volume walk):
    # symmetric obv_falling signal added to fix the silent-gap bug where
    # strat_break_retest_volume SHORT side used `not obv_rising` which
    # auto-passed when the OBV key was missing. obv_rising / obv_falling
    # retained for back-compat with other consumers; B617 switched
    # break_retest_volume itself to obv_bullish / obv_bearish (cleaner
    # 20-bar baseline; see external-AI critique 2026-06-07).
    result["obv_falling"]   = _safe_float(obv.iloc[-1]) < _safe_float(obv.iloc[-5])
    result["obv_diverge_bull"] = (c.iloc[-1] < c.iloc[-5] and
                                   _safe_float(obv.iloc[-1]) > _safe_float(obv.iloc[-5]))

    # Volume ratios
    avg20 = _safe_float(v.rolling(20).mean().iloc[-1])
    today_v = _safe_float(v.iloc[-1])
    ratio = today_v / avg20 if avg20 > 0 else 1.0
    result["vol_ratio_20d"] = round(ratio,2)
    # Batch 320 (2026-05-25): vol_above_avg added for owner-approved gate
    # loosens on donchian_10_breakout + rsi_volume_200ema. Any above-average
    # volume vs 20d mean - softer than the 1.5x / 2x spike gates.
    result["vol_above_avg"] = ratio >= 1.0
    # B594 (2026-06-05 owner directive donchian_20_breakout_retest walk):
    # vol_below_avg = ratio STRICTLY LESS THAN 1.0. Bulkowski 2005:
    # retest entry confirmation has LOWER volume than the initial
    # break (supply absorption thesis). Strategy-specific; ADDITIVE.
    result["vol_below_avg"] = ratio < 1.0
    # B589 (2026-06-04 owner directive 52w_high_breakout_with_smart_money_long
    # walk: "vol_above_avg = >= 1.2x make it"). Strategy-specific
    # threshold; ADDITIVE - existing strategies using vol_above_avg
    # (>= 1.0) unchanged.
    result["vol_spike_12x"] = ratio >= 1.2
    result["vol_spike_15x"] = ratio >= 1.5
    # B586: vol_spike_17x = strict >1.7x for 52w_high_breakout
    result["vol_spike_17x"] = ratio >  1.7
    result["vol_spike_2x"]  = ratio >= 2.0
    result["vol_spike_3x"]  = ratio >= 3.0

    # B589 (2026-06-04 owner directive 52w_high_breakout walk: "add
    # close above open and close within 40% of day high. Add inverse
    # for mirror"). Range-position signals:
    #   close_in_top_40pct_of_range:  close in top 40% of bar range
    #   close_in_bottom_40pct_of_range: close in bottom 40% (mirror)
    # Both used by the 52w high/low breakout strategies.
    h_today = _safe_float(h.iloc[-1])
    l_today = _safe_float(l.iloc[-1])
    c_today = _safe_float(c.iloc[-1])
    bar_range = h_today - l_today
    if bar_range > 0:
        result["close_in_top_40pct_of_range"]    = ((h_today - c_today) / bar_range) <= 0.40
        result["close_in_bottom_40pct_of_range"] = ((c_today - l_today) / bar_range) <= 0.40
    else:
        result["close_in_top_40pct_of_range"]    = False
        result["close_in_bottom_40pct_of_range"] = False

    # A/D Line
    clv = ((c-l)-(h-c))/(h-l).replace(0,np.nan)
    ad  = (clv*v).cumsum()
    result["ad_rising"] = _safe_float(ad.iloc[-1]) > _safe_float(ad.iloc[-5])

    # CMF (20-period)
    mf_vol = clv*v
    cmf    = mf_vol.rolling(20).sum() / v.rolling(20).sum().replace(0,np.nan)
    cmf_v  = _safe_float(cmf.iloc[-1])
    pcmf_v = _safe_float(cmf.iloc[-2])
    result["cmf"]          = round(cmf_v,4)
    result["cmf_positive"] = cmf_v > 0
    # B629 F2 (2026-06-08 owner directive cmf-family sweep): symmetric
    # cmf_negative signal so SHORT-side strategies can switch from
    # `not s.get("cmf_positive")` (silent-gap fragile per
    # feedback_never_use_NOT_s_get_pattern) to positive symmetric
    # cmf_negative. Mirror of cmf_positive (CMF < 0 = distribution).
    result["cmf_negative"] = cmf_v < 0
    result["cmf_cross_up"] = cmf_v > 0 and pcmf_v <= 0
    result["cmf_cross_dn"] = cmf_v < 0 and pcmf_v >= 0

    # MFI (14-period)
    if len(df) >= 15:
        tp   = (h+l+c)/3
        mf   = tp*v
        diff = tp.diff()
        pos_mf = mf.where(diff>0,0.0).rolling(14).sum()
        neg_mf = mf.where(diff<=0,0.0).rolling(14).sum()
        mfi_s  = 100 - 100/(1+pos_mf/neg_mf.replace(0,np.nan))
        mfi_v  = _safe_float(mfi_s.iloc[-1])
        result["mfi"]            = round(mfi_v,2)
        result["mfi_oversold"]   = mfi_v < 20
        result["mfi_overbought"] = mfi_v > 80

    # Force Index
    fi    = c.diff()*v
    fi13  = fi.ewm(span=13,adjust=False).mean()
    fi_v  = _safe_float(fi13.iloc[-1])
    pfi_v = _safe_float(fi13.iloc[-2])
    result["force_index_positive"] = fi_v > 0
    result["force_index_cross_up"] = fi_v > 0 and pfi_v <= 0
    result["force_index_cross_dn"] = fi_v < 0 and pfi_v >= 0

    # 52-week high/low
    # Batch 582 (2026-06-04 owner-directed bug fix per Stage 4 audit of
    # strat_52w_high_breakout QUIET status): year_high / year_low must
    # EXCLUDE today's bar so the breakout comparison is `today close vs
    # PRIOR 252-day high` (matches the canonical algorithmic spec). The
    # previous calculation `df["high"].tail(252).max()` included today's
    # intraday high, which made `close >= year_high` effectively require
    # close == today_high == max-of-252d -- extremely rare. AMD example:
    # AMD broke its 52w high multiple times in the backtest but the bug
    # gated the strategy down to ~0 fires.
    # Fix: use df.iloc[:-1] (excluding today) for the 252-day window.
    # Also: use strict `>` for break (per owner spec "Close > Highest
    # High (250d)") rather than `>=`. near_52w_high keeps `>=` since
    # "near" semantics include touching the level.
    lookback = min(252, len(df) - 1)  # -1 to exclude today
    if lookback > 0:
        prior = df.iloc[:-1]  # everything except today
        year_high = prior["high"].tail(lookback).max()
        year_low  = prior["low"].tail(lookback).min()
    else:
        # Fallback for very-short histories (<= 1 bar): use today
        year_high = df["high"].iloc[-1]
        year_low  = df["low"].iloc[-1]
    result["near_52w_high"]   = _safe_float(c.iloc[-1]) >= year_high*0.98
    result["break_52w_high"]  = _safe_float(c.iloc[-1]) >  year_high  # strict per spec
    result["year_high"]       = round(year_high,4)
    result["near_52w_low"]    = _safe_float(c.iloc[-1]) <= year_low*1.02
    result["break_52w_low"]   = _safe_float(c.iloc[-1]) <  year_low   # strict per spec
    result["year_low"]        = round(year_low,4)
    # B589 (2026-06-04 owner directive 52w_high_breakout_with_smart_money_long
    # walk: "near_52w_high - make it 95% of prev 52 week high").
    # Wider tolerance variants for smart-money sleeves. ADDITIVE - the
    # existing near_52w_high (98%) + near_52w_low (102%) preserved for
    # other consumers.
    result["near_52w_high_95pct"] = _safe_float(c.iloc[-1]) >= year_high*0.95
    result["near_52w_low_105pct"] = _safe_float(c.iloc[-1]) <= year_low*1.05

    # B590 (2026-06-04 owner-directed pullback redesign + clarification
    # round 2 + false-breakout filters): use a SINGLE INTERNALLY-CONSISTENT
    # 30-bar window for BOTH (a) breakout detection AND (b) year_high
    # pre-breakout reference. Plus two additional false-breakout filters
    # added per owner directive 2026-06-04: 3-candle time filter +
    # ATR-band filter.
    #
    # LONG fires when ALL 7 conditions hold:
    #   1. breakout_occurred: max CLOSE in last 30 bars (excluding
    #      today) > year_high_pre30 (pre-breakout 52w high)
    #   2. within_3pct_of_year_high_pre30: today's close within +/-3pct
    #      of the pre-breakout reference (owner B590 directive: 3% tolerance)
    #   3. today_below_recent_peak: today_close < recent_max_close * 0.99
    #   4. vol_below_avg: today_vol / 20d_avg < 1.0
    #   5. close_above_open: bullish bar
    #   6. breakout_at_least_3_bars_old: the FIRST bar in the 30-day
    #      window whose close exceeded year_high_pre30 occurred at
    #      least 3 bars before today (gives the retest time to form)
    #   7. within_atr_band_long: today_close >= year_high_pre30 - ATR(14)
    #      (a true breakdown more than 1 ATR below the broken level is
    #      a failed retest, not a valid pullback)
    #
    # SHORT mirror uses year_low_pre30 + symmetric filters.
    try:
        breakout_window_days = 30
        retest_tolerance = 0.03
        today_c = _safe_float(c.iloc[-1])
        today_o = _safe_float(df["open"].iloc[-1])
        # Pre-breakout reference: 252-day window ending breakout_window_days
        # bars ago. Excludes both today and the 30-day breakout-detection
        # window. Single source of "the pre-breakout 52w resistance level."
        ref_end = -(breakout_window_days + 1)
        if len(df) >= 252 + breakout_window_days + 1:
            ref_window = df.iloc[-(252 + breakout_window_days + 1):ref_end]
            year_high_pre30 = float(ref_window["high"].max())
            year_low_pre30  = float(ref_window["low"].min())
        else:
            year_high_pre30 = year_high
            year_low_pre30  = year_low
        if len(df) >= breakout_window_days + 1:
            recent_closes = df["close"].iloc[-(breakout_window_days + 1):-1]
            recent_max_close = float(recent_closes.max())
            recent_min_close = float(recent_closes.min())
        else:
            recent_max_close = today_c
            recent_min_close = today_c
        # B590 owner directive 2026-06-04 "close within 1% of moving
        # ref. make it 3%": tolerance widened from 0.01 -> 0.03 for
        # both retest-near-level checks. Reference is year_high_pre30 /
        # year_low_pre30 (STABLE pre-breakout level) - not year_high /
        # year_low which would drift each day as the breakout itself
        # prints new highs (B590 owner criticism of B586 design).
        # LONG: stock recently breached prior 52w high then pulled back
        breakout_high_occurred = recent_max_close > year_high_pre30
        within_3pct_high       = abs(today_c - year_high_pre30) / max(year_high_pre30, 0.01) <= retest_tolerance
        today_below_peak       = today_c < recent_max_close * 0.99
        vol_below_avg          = ratio < 1.0
        close_above_open       = today_c > today_o
        close_below_open       = today_c < today_o
        # SHORT mirror: stock recently breached prior 52w low then bounced back
        breakdown_low_occurred = recent_min_close < year_low_pre30
        within_3pct_low        = abs(today_c - year_low_pre30) / max(year_low_pre30, 0.01) <= retest_tolerance
        today_above_trough     = today_c > recent_min_close * 1.01

        # B590 false-breakout filter (a) - 3-candle time filter:
        # Require >=3 candles to form between initial breakout day and
        # today before validating retest (per owner directive).
        # Find first bar in the 30-day window whose close exceeded
        # year_high_pre30 (LONG) / went below year_low_pre30 (SHORT);
        # require today_idx - breakout_idx >= 3 (i.e. >=3 candles
        # between the breakout and today).
        min_candles_post_breakout = 3
        try:
            if breakout_high_occurred:
                # recent_closes has 30 entries indexed 0..29 (oldest..newest);
                # today is index 30 in absolute terms (=last bar of df).
                breakout_mask_long = (recent_closes > year_high_pre30).values
                first_breakout_idx_long = int(np.argmax(breakout_mask_long))  # first True
                bars_since_breakout_long = (len(recent_closes) - first_breakout_idx_long)
                breakout_3_candles_old_long = bars_since_breakout_long >= min_candles_post_breakout
            else:
                breakout_3_candles_old_long = False
            if breakdown_low_occurred:
                breakdown_mask_short = (recent_closes < year_low_pre30).values
                first_breakdown_idx_short = int(np.argmax(breakdown_mask_short))
                bars_since_breakdown_short = (len(recent_closes) - first_breakdown_idx_short)
                breakdown_3_candles_old_short = bars_since_breakdown_short >= min_candles_post_breakout
            else:
                breakdown_3_candles_old_short = False
        except Exception:
            breakout_3_candles_old_long = False
            breakdown_3_candles_old_short = False

        # B590 false-breakout filter (b) - ATR band filter:
        # If today's close is more than 1*ATR below year_high_pre30
        # (LONG) or more than 1*ATR above year_low_pre30 (SHORT), the
        # broken S/R has been re-broken and this is a failed retest
        # rather than a valid pullback. Use ATR(14) computed inline
        # so the pullback producer remains self-contained.
        try:
            atr14_series = _atr_series(df, period=14)
            atr14 = float(atr14_series.iloc[-1])
        except Exception:
            atr14 = 0.0
        within_atr_band_long  = (today_c >= year_high_pre30 - atr14) if atr14 > 0 else True
        within_atr_band_short = (today_c <= year_low_pre30  + atr14) if atr14 > 0 else True

        result["near_52w_high_retest_long"] = bool(
            breakout_high_occurred
            and within_3pct_high
            and today_below_peak
            and vol_below_avg
            and close_above_open
            and breakout_3_candles_old_long
            and within_atr_band_long
        )
        result["near_52w_low_retest_short"] = bool(
            breakdown_low_occurred
            and within_3pct_low
            and today_above_trough
            and vol_below_avg
            and close_below_open
            and breakdown_3_candles_old_short
            and within_atr_band_short
        )
    except Exception:
        result["near_52w_high_retest_long"] = False
        result["near_52w_low_retest_short"] = False

    return result


# -----------------------------------------------------------------------------
# CANDLE PATTERNS
# -----------------------------------------------------------------------------

def compute_candles(df: pd.DataFrame) -> dict:
    if len(df) < 5:
        return {}
    result = {}
    o = df["open"].values;  h = df["high"].values
    l = df["low"].values;   c = df["close"].values
    n = len(c)

    # Current bar metrics
    body   = abs(c[-1]-o[-1])
    rng    = h[-1]-l[-1]
    uwk    = h[-1]-max(c[-1],o[-1])
    lwk    = min(c[-1],o[-1])-l[-1]
    bull   = c[-1] > o[-1]

    # -- Single-bar patterns --
    result["inside_bar"]    = (h[-1]<h[-2]) and (l[-1]>l[-2])
    result["outside_bar"]   = (h[-1]>h[-2]) and (l[-1]<l[-2])
    result["doji"]          = (body < 0.05*rng) if rng>0 else False
    if rng > 0:
        result["hammer"]        = lwk>2*body and uwk<body and body>0
        result["shooting_star"] = uwk>2*body and lwk<body and body>0
        result["pin_bar"]       = max(uwk,lwk) > 0.66*rng
        result["marubozu_bull"] = bull and uwk<body*0.05 and lwk<body*0.05
        result["marubozu_bear"] = not bull and uwk<body*0.05 and lwk<body*0.05
    else:
        result["hammer"] = result["shooting_star"] = result["pin_bar"] = False
        result["marubozu_bull"] = result["marubozu_bear"] = False

    # -- Two-bar patterns --
    result["bullish_engulfing"] = (
        c[-2]<o[-2] and c[-1]>o[-1] and c[-1]>o[-2] and o[-1]<c[-2])
    result["bearish_engulfing"] = (
        c[-2]>o[-2] and c[-1]<o[-1] and c[-1]<o[-2] and o[-1]>c[-2])

    # -- Three-bar patterns --
    # Batch 559 OPT-C Phase 4 producer correctness fix: operator-precedence
    # bug. `A and B if C else D and E` parsed as `(A and B) if C else (D and E)`
    # not `A and (B if C else D) and E` -- so the prior code only checked 2 of
    # 4 intended morning_star / evening_star conditions when mid_rng > 0.
    # Empirical (NVDA 504 bars): buggy parse fired morning_star 66x; intended
    # 4-condition AND fires 29x. The bug OVER-FIRED morning_star + evening_star.
    if n >= 3:
        mid_body = abs(c[-2]-o[-2])
        mid_rng  = h[-2]-l[-2]
        mid_small = (mid_body < 0.3*mid_rng) if mid_rng > 0 else False
        result["morning_star"] = (
            c[-3]<o[-3]
            and mid_small
            and c[-1]>o[-1]
            and c[-1] > (o[-3]+c[-3])/2
        )
        result["evening_star"] = (
            c[-3]>o[-3]
            and mid_small
            and c[-1]<o[-1]
            and c[-1] < (o[-3]+c[-3])/2
        )

    # -- Five-bar patterns --
    if n >= 5:
        result["three_white_soldiers"] = (
            all(c[-i]>o[-i] for i in range(1,4)) and
            all(c[-i]>c[-i-1] for i in range(1,3)) and
            all(o[-i]>o[-i-1] for i in range(1,3)))
        result["three_black_crows"] = (
            all(c[-i]<o[-i] for i in range(1,4)) and
            all(c[-i]<c[-i-1] for i in range(1,3)) and
            all(o[-i]<o[-i-1] for i in range(1,3)))
    else:
        result["three_white_soldiers"] = result["three_black_crows"] = False

    return result


# -----------------------------------------------------------------------------
# BREAK-AND-RETEST  (BUG-111)
# -----------------------------------------------------------------------------

def compute_break_retest_signals(df: pd.DataFrame) -> dict:
    """Multi-bar break-and-retest pattern signals.

    BUG-111 fix 2026-05-13: detects when price broke above/below a significant
    level 2-8 bars ago, then pulled back to retest that level, and is holding above/below.
    Retest confirms the broken level has flipped from resistance->support (long) or
    support->resistance (short).

    resistance_break_retest (long): DC20 high broken 2-8 bars ago; subsequent bar
      touched within 1.5 ATR of the broken level; current close >= broken level.
    support_break_retest (short): DC20 low broken 2-8 bars ago; subsequent bar
      touched within 1.5 ATR of the broken level from below; current close <= broken level.
    """
    if len(df) < 30:
        return {"resistance_break_retest": False, "support_break_retest": False}

    close = df["close"].values
    high  = df["high"].values
    low   = df["low"].values
    n     = len(close)

    # Batch 545 OPT-C: vectorize TR list-comp (was Python loop over n bars).
    # Numpy ops give ~50-100x speedup on the TR portion of this call.
    tr1 = high[1:] - low[1:]
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])
    tr_arr = np.maximum(np.maximum(tr1, tr2), tr3)
    atr = float(np.mean(tr_arr[-14:])) if len(tr_arr) >= 14 else float(np.mean(tr_arr))
    if atr <= 0:
        atr = close[-1] * 0.01
    tolerance = 1.5 * atr

    # B594 (2026-06-05 owner directive donchian_20_breakout_retest walk):
    # STRONG-breakout LOCAL variants require the original breakout bar to
    # have closed by at least 0.5*ATR(14) BEYOND the broken level, not
    # just to have crossed it. Filters trivial closes-just-above-level
    # pseudo-breakouts on the retest pattern. Consumed by
    # strat_donchian_20_breakout_retest alone. Same lag window 2-8,
    # same 1.5*ATR retest tolerance, same hold check; ONLY the breakout
    # detection is tightened.
    strong_atr_clearance = 0.5 * atr

    # Resistance break-and-retest (long signal) - emits BOTH standard
    # and _strong variants in one pass.
    resistance_brt = False
    resistance_brt_strong = False
    for lag in range(2, 9):
        if n <= lag + 2:
            break
        idx = n - 1 - lag          # index of the potential breakout bar
        pre_start = max(0, idx - 20)
        if pre_start >= idx:
            continue
        level = float(np.max(close[pre_start:idx]))
        if close[idx] > level:     # breakout: bar at idx closed above prior DC20
            # Any subsequent bar retested (low touched within tolerance of level)
            if any(l <= level + tolerance for l in low[idx + 1:]):
                if close[-1] >= level:  # current bar still above the broken level
                    if not resistance_brt:
                        resistance_brt = True
                    # B594 strong check: breakout bar cleared by >= 0.5*ATR
                    if not resistance_brt_strong and close[idx] >= level + strong_atr_clearance:
                        resistance_brt_strong = True
                    if resistance_brt and resistance_brt_strong:
                        break

    # Support breakdown-and-retest (short signal)
    support_brt = False
    support_brt_strong = False
    for lag in range(2, 9):
        if n <= lag + 2:
            break
        idx = n - 1 - lag
        pre_start = max(0, idx - 20)
        if pre_start >= idx:
            continue
        level = float(np.min(close[pre_start:idx]))
        if close[idx] < level:     # breakdown: bar at idx closed below prior DC20
            if any(h >= level - tolerance for h in high[idx + 1:]):
                if close[-1] <= level:  # current bar still below the broken level
                    if not support_brt:
                        support_brt = True
                    if not support_brt_strong and close[idx] <= level - strong_atr_clearance:
                        support_brt_strong = True
                    if support_brt and support_brt_strong:
                        break

    return {
        "resistance_break_retest":         resistance_brt,
        "support_break_retest":            support_brt,
        # B594 LOCAL strong variants (donchian_20_breakout_retest only)
        "dc20_resistance_break_retest_strong": resistance_brt_strong,
        "dc20_support_break_retest_strong":    support_brt_strong,
    }


def compute_52w_break_retest_signals(df: pd.DataFrame) -> dict:
    """Batch 605 (2026-06-06 owner-directed F1 bug fix in 52wh_break_retest
    walk): 52-WEEK-HIGH (or LOW) break-and-retest primitive. Same retest
    structure as compute_break_retest_signals but anchored on year_high
    / year_low (prior-252-day max-HIGH / min-LOW, excluding today via
    the B582 fix) instead of DC20-max-CLOSE.

    Bug context (CHECKLIST #105 deep-read surfaced this):
      The original strat_52wh_break_retest (BUG-111 / Batch 162) was
      documented as "52-week high break-and-retest" but consumed the
      DC20-anchored resistance_break_retest signal. The DC20-max-close
      could be any price; it bore no relationship to the 52w high. The
      near_52w_high gate (within 2pct of year_high) was added as a
      proximity filter but did NOT tie the retest event to the year_high
      breakout. Strategy name + docstring lied about what it detected.

    Fix: build the 52w-anchored equivalent primitive so the strategy
    can consume what its name promises. Emits:
      - year_high_break_retest_long (long): some bar 2-8 ago closed
        > year_high (the prior-252d max-HIGH excluding today); subsequent
        bar low touched within 1.5*ATR(14) of year_high; today's close
        still >= year_high.
      - year_low_break_retest_short (short): mirror around year_low.

    Both emit `False` when df < 252+9 = 261 bars (need enough history
    to define year_high + 8-bar lag window).

    Producer signals consumed only by strat_52wh_break_retest +
    strat_52wl_break_retest_short (B605 ADDED).
    """
    out = {
        "year_high_break_retest_long":  False,
        "year_low_break_retest_short": False,
    }
    if len(df) < 252 + 9:  # need 252-day window + max 8-bar lag + today
        return out

    close = df["close"].values
    high  = df["high"].values
    low   = df["low"].values
    n     = len(close)

    # ATR(14) same as compute_break_retest_signals (vectorized TR).
    tr1 = high[1:] - low[1:]
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])
    tr_arr = np.maximum(np.maximum(tr1, tr2), tr3)
    atr = float(np.mean(tr_arr[-14:])) if len(tr_arr) >= 14 else float(np.mean(tr_arr))
    if atr <= 0:
        atr = close[-1] * 0.01
    tolerance = 1.5 * atr

    # year_high / year_low computed at the BREAK bar (lag), using the
    # 252 bars PRIOR to the break bar. Excludes today (B582 fix carried
    # through). This way the "broken level" the bar at idx broke is
    # defined consistently with how a trader would have observed the
    # year_high at the time of the break.
    resistance_long = False
    for lag in range(2, 9):
        if n <= lag + 252:  # need 252 bars of history BEFORE the break bar
            break
        idx = n - 1 - lag                          # break-bar index
        window_start = idx - 252                   # prior 252 bars
        if window_start < 0:
            continue
        year_high_at_break = float(np.max(high[window_start:idx]))
        if close[idx] > year_high_at_break:        # break: bar at idx closed above year_high
            # any subsequent bar's low touched within tolerance of year_high
            if any(l <= year_high_at_break + tolerance for l in low[idx + 1:]):
                if close[-1] >= year_high_at_break:  # today still above year_high
                    resistance_long = True
                    break

    support_short = False
    for lag in range(2, 9):
        if n <= lag + 252:
            break
        idx = n - 1 - lag
        window_start = idx - 252
        if window_start < 0:
            continue
        year_low_at_break = float(np.min(low[window_start:idx]))
        if close[idx] < year_low_at_break:
            if any(h >= year_low_at_break - tolerance for h in high[idx + 1:]):
                if close[-1] <= year_low_at_break:
                    support_short = True
                    break

    out["year_high_break_retest_long"]  = resistance_long
    out["year_low_break_retest_short"] = support_short
    return out


def compute_pivot_break_retest_signals(df: pd.DataFrame) -> dict:
    """Batch 606 (2026-06-06 owner-directed F1 bug fix in r1_break_retest
    walk): pivot-anchored break-and-retest primitive.

    Bug context (CHECKLIST #105 deep-read surfaced this in B606):
      The original strat_r1_break_retest (BUG-111 / Batch 162) was
      documented as "Pivot R1 break-and-retest" but consumed the
      DC20-anchored resistance_break_retest signal. R1 is a 1-day
      level recomputed daily from prior day's H/L/C; the DC20-max-CLOSE
      bore no relationship to any specific R1 value. The above_r1
      gate was a same-day position filter, not a "broken R1 acting
      as support" check. Same name-vs-implementation lie that
      compute_52w_break_retest_signals fixed for 52wh_break_retest
      in B605.

    Fix: build the R1-anchored equivalent of compute_break_retest
    _signals (DC20-anchored) and compute_52w_break_retest_signals
    (year-anchored). At each candidate break-bar B (lag 2-8 ago):
      - Compute R1_at_B from bar B-1's H/L/C using standard pivot
        formula (R1 = 2*P - L; P = (H+L+C)/3)
      - Check close[B] > R1_at_B (break occurred AT bar B)
      - Check subsequent bar's low touched within 1.5*ATR(14) of
        R1_at_B (retest of THAT specific R1 level)
      - Check today's close >= R1_at_B (still holding above the
        broken-then-retested R1)
    Same mirror for S1 with S1_at_B = 2*P - H.

    Both signals emit False when df < 30 bars (need ATR(14) + lag-8
    window + bar B-1).

    LOCAL signals consumed only by strat_r1_break_retest (B606 F1).
    """
    out = {
        "r1_break_retest_long":  False,
        "s1_break_retest_short": False,
    }
    if len(df) < 30:
        return out

    close = df["close"].values
    high  = df["high"].values
    low   = df["low"].values
    n     = len(close)

    # ATR(14) vectorized TR (same as compute_break_retest_signals).
    tr1 = high[1:] - low[1:]
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])
    tr_arr = np.maximum(np.maximum(tr1, tr2), tr3)
    atr = float(np.mean(tr_arr[-14:])) if len(tr_arr) >= 14 else float(np.mean(tr_arr))
    if atr <= 0:
        atr = close[-1] * 0.01
    tolerance = 1.5 * atr

    # LONG: R1 break-retest-hold.
    resistance_long = False
    for lag in range(2, 9):
        if n <= lag + 2:  # need bar B AND bar B-1
            break
        idx = n - 1 - lag
        if idx < 1:
            continue
        # R1 at bar idx, derived from bar (idx-1)'s H/L/C (standard pivot).
        H_prev = float(high[idx - 1])
        L_prev = float(low[idx - 1])
        C_prev = float(close[idx - 1])
        P_at_idx  = (H_prev + L_prev + C_prev) / 3.0
        R1_at_idx = 2.0 * P_at_idx - L_prev
        if close[idx] > R1_at_idx:                            # break at bar idx
            if any(l <= R1_at_idx + tolerance for l in low[idx + 1:]):   # retest
                if close[-1] >= R1_at_idx:                    # today still above R1_at_idx
                    resistance_long = True
                    break

    # SHORT mirror: S1 breakdown-retest-hold.
    support_short = False
    for lag in range(2, 9):
        if n <= lag + 2:
            break
        idx = n - 1 - lag
        if idx < 1:
            continue
        H_prev = float(high[idx - 1])
        L_prev = float(low[idx - 1])
        C_prev = float(close[idx - 1])
        P_at_idx  = (H_prev + L_prev + C_prev) / 3.0
        S1_at_idx = 2.0 * P_at_idx - H_prev
        if close[idx] < S1_at_idx:
            if any(h >= S1_at_idx - tolerance for h in high[idx + 1:]):
                if close[-1] <= S1_at_idx:
                    support_short = True
                    break

    out["r1_break_retest_long"]  = resistance_long
    out["s1_break_retest_short"] = support_short
    return out


# -----------------------------------------------------------------------------
# MASTER AGGREGATOR
# -----------------------------------------------------------------------------

def compute_all_signals(df: pd.DataFrame,
                          skip_indicators: set | None = None) -> dict:
    """
    Compute all ~220 technical signals from a point-in-time OHLCV DataFrame.
    Returns flat dict. df must already be sliced to as_of date by fetcher.

    Batch 538 OPT-B Phase 7: `skip_indicators` is a set of indicator
    names (e.g. {"rsi", "ema_sma", "simple_returns"}) whose computation
    is skipped because the caller has already populated those keys
    (e.g. via panel-style compute_panel_signals_for_as_of). When the
    panel path runs upstream, the per-ticker function call here is
    redundant -- skipping it is the actual speedup.

    SAFETY: caller MUST pre-populate the skipped indicators' keys
    in the signals dict it merges with this function's output, otherwise
    downstream strategies see missing keys.
    """
    if df.empty or len(df) < 10:
        return {}
    skip = skip_indicators or set()
    signals = {}
    signals.update(compute_pivots(df))
    signals.update(compute_fibonacci(df))
    signals.update(compute_vwap(df))
    if "rsi" not in skip:
        signals.update(compute_rsi(df))
    signals.update(compute_stochrsi(df))
    signals.update(compute_stochastic(df))
    signals.update(compute_macd(df))
    signals.update(compute_ppo(df))
    signals.update(compute_williams_r(df))
    signals.update(compute_roc(df))
    signals.update(compute_awesome_oscillator(df))
    signals.update(compute_ultimate_oscillator(df))
    if "ema_sma" not in skip:
        signals.update(compute_ema_sma(df))
    signals.update(compute_dema_tema(df))
    signals.update(compute_adx(df))
    signals.update(compute_parabolic_sar(df))
    signals.update(compute_ichimoku(df))
    signals.update(compute_supertrend(df))
    signals.update(compute_chandelier_exit(df))
    signals.update(compute_hull_ma(df))
    signals.update(compute_bollinger(df))
    signals.update(compute_keltner(df))
    signals.update(compute_donchian(df))
    signals.update(compute_atr_levels(df))
    signals.update(compute_squeeze(df))
    signals.update(compute_volume(df))
    signals.update(compute_candles(df))
    signals.update(compute_break_retest_signals(df))  # BUG-111
    signals.update(compute_52w_break_retest_signals(df))  # B605 F1 - 52w-anchored retest
    signals.update(compute_pivot_break_retest_signals(df))  # B606 F1 - R1/S1-anchored retest
    if "simple_returns" not in skip:
        signals.update(compute_simple_returns(df))        # Batch 467 P10
    return {k: v for k, v in signals.items() if v is not None}


def compute_simple_returns(df: pd.DataFrame) -> dict:
    """Batch 467 (P10): simple percent-change returns over 5 / 10 / 20
    trading-day lookbacks. Returns dict with `pct_change_5d`,
    `pct_change_10d`, `pct_change_20d` as floats in fractional units
    (0.10 = +10 percent). Returns {} when history is too short.

    These are generic momentum signals used by news-reversal strategies
    (e.g. `pct_change_5d > 0.10` to flag overreaction after positive
    news) and any future strategy that needs short-horizon return
    context without recomputing.
    """
    if df is None or df.empty or len(df) < 21:
        return {}
    close = df["close"].astype(float)
    last = float(close.iloc[-1])
    out: dict = {}
    for lb in (5, 10, 20):
        if len(close) > lb:
            prev = float(close.iloc[-(lb + 1)])
            if prev > 0:
                out[f"pct_change_{lb}d"] = round((last - prev) / prev, 6)
    return out


def compute_macro_overlays(
    signals: dict,
    vix_value: float = None,
    vix_history: list = None,
    lookback_days: int = 252,
) -> dict:
    """Batch 204 (Bollinger optimization 2026-05-17): add VIX context overlays
    to a per-ticker signals dict so strategies can read regime-aware fields
    (vix_percentile, vix_band) inline. Existing strategies remain backward-
    compatible: when vix_value/history are None, no new keys are added.

    Adds (when inputs available):
      - vix_value: today's raw VIX
      - vix_percentile: percentile of today's VIX within trailing
        lookback_days distribution [0.0, 1.0]
      - vix_band: 'low' (<33rd pct), 'mid' (33-66), 'high' (>66th pct)
      - vix_band_low / vix_band_mid / vix_band_high: bool flags for
        strategy condition reuse

    Per Cederburg-Johnson-Maio (2024) VIX-managed portfolios: regime
    bucketing by VIX percentile is the canonical low-cost macro-overlay
    used by institutional volatility strategies.
    """
    if vix_value is None or vix_history is None:
        return signals
    arr = [v for v in vix_history if v is not None]
    if len(arr) < 20:
        return signals
    if len(arr) > lookback_days:
        arr = arr[-lookback_days:]
    n = len(arr)
    pct = sum(1 for v in arr if v <= vix_value) / n
    if pct < 1.0 / 3:
        band = "low"
    elif pct < 2.0 / 3:
        band = "mid"
    else:
        band = "high"
    out = dict(signals)
    out["vix_value"]      = round(float(vix_value), 2)
    out["vix_percentile"] = round(pct, 4)
    out["vix_band"]       = band
    out["vix_band_low"]   = band == "low"
    out["vix_band_mid"]   = band == "mid"
    out["vix_band_high"]  = band == "high"
    return out


def count_bullish_signals(signals: dict) -> int:
    bullish_keys = [
        k for k, v in signals.items()
        if isinstance(v, bool) and v is True and any(w in k for w in [
            "bullish", "oversold", "above_pivot", "breakout_up", "golden_cross",
            "above_vwap", "positive", "squeeze_positive", "hammer", "morning_star",
            "bullish_engulfing", "inside_bar", "vol_spike", "above_mid", "trending",
            "crossover_up", "touch_lower", "cross_up", "flip_up", "rising",
            "three_white", "marubozu_bull", "above_cpr", "above_cam_r",
            "above_prev_high", "near_cam_s", "near_s", "near_fib",
        ])
    ]
    return len(bullish_keys)
