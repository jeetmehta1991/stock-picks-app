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
        "near_prev_high":  near(H),    "near_prev_low":   near(L),
        "near_prev_close": near(C),
    }


def compute_fibonacci(df: pd.DataFrame, lookback: int = 50) -> dict:
    if len(df) < 10:
        return {}
    w  = df.tail(min(lookback, len(df)))
    sh = w["high"].max();  sl = w["low"].min()
    d  = sh - sl;          today = df["close"].iloc[-1]
    near = lambda lvl: abs(today - lvl) / max(abs(lvl), 0.01) < 0.005
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
    return {
        "vwap":          round(vwap, 4),
        "vwap_upper_1":  round(vwap + std, 4),
        "vwap_upper_2":  round(vwap + 2*std, 4),
        "vwap_lower_1":  round(vwap - std, 4),
        "vwap_lower_2":  round(vwap - 2*std, 4),
        "above_vwap":    close > vwap,
        "pct_from_vwap": round((close - vwap) / vwap * 100, 3) if vwap else 0,
    }


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
    """
    result = {}
    for p in [9, 14, 21]:
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
        # Manual Parabolic SAR -- track prev_bullish at start of each bar
        af_start, af_step, af_max = 0.02, 0.02, 0.20
        h, l = df["high"].values, df["low"].values
        n = len(h)
        sar, af, ep = l[0], af_start, h[0]
        bullish = True
        prev_bullish = True
        for i in range(1, n):
            prev_bullish = bullish  # record state BEFORE update
            if bullish:
                sar = sar + af * (ep - sar)
                sar = min(sar, l[i - 1], l[max(0, i - 2)])
                if l[i] < sar:
                    bullish = False; sar = ep; ep = l[i]; af = af_start
                else:
                    if h[i] > ep: ep = h[i]; af = min(af + af_step, af_max)
            else:
                sar = sar + af * (ep - sar)
                sar = max(sar, h[i - 1], h[max(0, i - 2)])
                if h[i] > sar:
                    bullish = True; sar = ep; ep = h[i]; af = af_start
                else:
                    if l[i] < ep: ep = l[i]; af = min(af + af_step, af_max)
        psar_long = sar
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
    return {
        "ichi_tenkan":      round(t,4), "ichi_kijun": round(k,4),
        "ichi_senkou_a":    round(sa,4), "ichi_senkou_b": round(sb,4),
        "ichi_above_cloud": above_cloud, "ichi_below_cloud": below_cloud,
        "ichi_tk_bullish":  t > k,
        "ichi_tk_cross_up": t > k and pt <= pk,
        "ichi_tk_bearish":  t < k,
        "ichi_tk_cross_dn": t < k and pt >= pk,
        "ichi_cloud_thick": abs(sa-sb) > abs(sa)*0.01 if sa else False,
    }


def compute_supertrend(df: pd.DataFrame, period: int = 7, mult: float = 3.0) -> dict:
    if len(df) < period + 2:
        return {}
    atr  = _atr_series(df, period)
    hl2  = (df["high"] + df["low"]) / 2
    ub   = hl2 + mult*atr
    lb   = hl2 - mult*atr
    close = df["close"]
    # Proper supertrend with state tracking
    st    = [0.0] * len(df)
    bull  = [True] * len(df)
    for i in range(1, len(df)):
        ub_prev = float(ub.iloc[i-1]); lb_prev = float(lb.iloc[i-1])
        ub_cur  = float(ub.iloc[i]);   lb_cur  = float(lb.iloc[i])
        lb_cur  = max(lb_cur, lb_prev) if float(close.iloc[i-1]) > lb_prev else lb_cur
        ub_cur  = min(ub_cur, ub_prev) if float(close.iloc[i-1]) < ub_prev else ub_cur
        if st[i-1] == ub_prev:
            st[i] = lb_cur if float(close.iloc[i]) > ub_prev else ub_cur
        else:
            st[i] = ub_cur if float(close.iloc[i]) < lb_prev else lb_cur
        bull[i] = float(close.iloc[i]) > st[i]
    return {
        "supertrend_bullish":  bull[-1],
        "supertrend_value":    round(st[-1], 4),
        "supertrend_flip_up":  bull[-1] and not bull[-2],
        "supertrend_flip_dn":  not bull[-1] and bull[-2],
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
    """
    weights = np.arange(1, period + 1, dtype=float)
    denom = weights.sum()
    return series.rolling(period).apply(lambda x: float(np.dot(x, weights) / denom), raw=True)


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
    result = {}
    for period in [10, 20]:
        if len(df) < period + 2:
            continue
        upper = df["high"].rolling(period).max()
        lower = df["low"].rolling(period).min()
        mid   = (upper + lower) / 2
        close = _safe_float(df["close"].iloc[-1])
        u,l   = _safe_float(upper.iloc[-1]),_safe_float(lower.iloc[-1])
        pu    = _safe_float(upper.iloc[-2])
        result[f"dc{period}_upper"]        = round(u,4)
        result[f"dc{period}_lower"]        = round(l,4)
        result[f"dc{period}_mid"]          = round(_safe_float(mid.iloc[-1]),4)
        result[f"dc{period}_breakout_up"]  = close >= u*0.998
        result[f"dc{period}_breakout_dn"]  = close <= l*1.002
        result[f"dc{period}_new_high"]     = u > pu   # expanding upper channel
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
    ema20 = df["close"].ewm(span=20, adjust=False).mean()
    delta = df["close"] - (df["high"].rolling(20).max() + df["low"].rolling(20).min())/2 + ema20
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

    # OBV
    direction = c.diff().apply(lambda x: 1 if x>0 else (-1 if x<0 else 0))
    obv       = (direction*v).cumsum()
    obv_ma    = obv.rolling(20).mean()
    result["obv_bullish"]   = _safe_float(obv.iloc[-1]) > _safe_float(obv_ma.iloc[-1])
    result["obv_rising"]    = _safe_float(obv.iloc[-1]) > _safe_float(obv.iloc[-5])
    result["obv_diverge_bull"] = (c.iloc[-1] < c.iloc[-5] and
                                   _safe_float(obv.iloc[-1]) > _safe_float(obv.iloc[-5]))

    # Volume ratios
    avg20 = _safe_float(v.rolling(20).mean().iloc[-1])
    today_v = _safe_float(v.iloc[-1])
    ratio = today_v / avg20 if avg20 > 0 else 1.0
    result["vol_ratio_20d"] = round(ratio,2)
    result["vol_spike_15x"] = ratio >= 1.5
    result["vol_spike_2x"]  = ratio >= 2.0
    result["vol_spike_3x"]  = ratio >= 3.0

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
    lookback = min(252, len(df))
    year_high = df["high"].tail(lookback).max()
    year_low  = df["low"].tail(lookback).min()
    result["near_52w_high"]   = _safe_float(c.iloc[-1]) >= year_high*0.98
    result["break_52w_high"]  = _safe_float(c.iloc[-1]) >= year_high
    result["year_high"]       = round(year_high,4)
    result["near_52w_low"]    = _safe_float(c.iloc[-1]) <= year_low*1.02
    result["break_52w_low"]   = _safe_float(c.iloc[-1]) <= year_low
    result["year_low"]        = round(year_low,4)

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
    if n >= 3:
        mid_body = abs(c[-2]-o[-2])
        mid_rng  = h[-2]-l[-2]
        result["morning_star"] = (
            c[-3]<o[-3] and
            mid_body < 0.3*mid_rng if mid_rng>0 else False and
            c[-1]>o[-1] and
            c[-1] > (o[-3]+c[-3])/2)
        result["evening_star"] = (
            c[-3]>o[-3] and
            mid_body < 0.3*mid_rng if mid_rng>0 else False and
            c[-1]<o[-1] and
            c[-1] < (o[-3]+c[-3])/2)

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
# MASTER AGGREGATOR
# -----------------------------------------------------------------------------

def compute_all_signals(df: pd.DataFrame) -> dict:
    """
    Compute all ~220 technical signals from a point-in-time OHLCV DataFrame.
    Returns flat dict. df must already be sliced to as_of date by fetcher.
    """
    if df.empty or len(df) < 10:
        return {}
    signals = {}
    signals.update(compute_pivots(df))
    signals.update(compute_fibonacci(df))
    signals.update(compute_vwap(df))
    signals.update(compute_rsi(df))
    signals.update(compute_stochrsi(df))
    signals.update(compute_stochastic(df))
    signals.update(compute_macd(df))
    signals.update(compute_ppo(df))
    signals.update(compute_williams_r(df))
    signals.update(compute_roc(df))
    signals.update(compute_awesome_oscillator(df))
    signals.update(compute_ultimate_oscillator(df))
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
    return {k: v for k, v in signals.items() if v is not None}


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
