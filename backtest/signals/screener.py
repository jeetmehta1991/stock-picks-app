"""
signals/screener.py - All Layer 1 baseline 60 strategy classes (per CANONICAL_FACTS.md F-002 Layer 1) with entry zone logic and regime filter.

Note: This file implements the Layer 1 baseline. Layer 2 (Phase 0.D ICT/Earnings/Calendar),
Layer 2D (form-derived ICT), Layer 3 (Pass 52 RESOLVED chart-pattern + categories), and
Layer 4 (PENDING strategy-additive) are scheduled per AUDIT_INDEX DEC-045/259/355-362/367-371.
Full layered roster: ~108-133 classes per CANONICAL_FACTS.md F-002.

BUG-23 SUPERSEDED-BY-CANONICAL_FACTS-F-002 Pass 53 v8h+1 cross-reference 2026-05-10:
the "60 baseline classes" count is canonically correct per F-002 Layer 1; the bug
observation was incomplete (didn't account for layered architecture).
BUG-22 RESOLVED-IMPLEMENTED Pass 53 v8h+1 cross-reference 2026-05-10:
run_phase1a.py header docstring no longer references stale "60 strategies"
text (verified via grep absence 2026-05-10).

60 baseline classes across 7 categories:
  Pivot-based      (10): S1-S3 bounces, R1-R2 breakouts, CPR bias,
                         Camarilla S3/R3, prev day high/low
  Momentum         ( 9): MACD (2 sets), Hull+RSI, Williams%R, ROC,
                         Awesome Oscillator, StochRSI, PPO, Ultimate Oscillator
  Trend            ( 9): Golden cross (3 pairs), Parabolic SAR, TEMA/DEMA,
                         Ichimoku TK cross, Ichimoku cloud, ADX initiation,
                         Supertrend+MACD
  Mean Reversion   (11): RSI oversold (3 variants), RSI overbought short,
                         MFI oversold, CMF flip, Bollinger (2 variants),
                         Bollinger upper short, Keltner bounce, Stochastic
  Breakout         ( 6): Squeeze, Volume spike, 52-week high, Inside bar,
                         Force Index, Donchian 10-day
  Candle Pattern   ( 6): Morning star, Bullish engulfing at support,
                         Doji at support, Three white soldiers,
                         Shooting star short, Evening star short
  Confluence       ( 9): RSI+volume+200EMA, MACD+Ichimoku, BB squeeze+volume,
                         Pivot+Fib, Golden cross+volume, CPR+momentum,
                         Camarilla+RSI+OBV, Supertrend+Ichimoku+ADX,
                         Williams+Stoch dual oversold

Each strategy returns:
  {"fires": bool, "direction": "long"|"short", "category": str,
   "signals_used": list, "context_bullets": list}
"""

import logging
from datetime import date
from typing import Optional

import pandas as pd

from backtest.config import ENTRY_GAP_ATR_MULT, LIQUIDITY
from backtest.data.fetcher import passes_liquidity_filter
from backtest.signals.technical import compute_all_signals, count_bullish_signals

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# STRATEGY HELPER
# -----------------------------------------------------------------------------

def _strat(fires, direction, category, signals_used, context_bullets):
    """Single-direction strategy  -  fires True/False with fixed direction."""
    return {
        "fires":           bool(fires),
        "direction":       direction,
        "category":        category,
        "signals_used":    signals_used,
        "context_bullets": context_bullets,
    }


def _strat3(fires_long, fires_short, category, signals_used_long, signals_used_short,
            bullets_long, bullets_short):
    """Three-state strategy  -  evaluates long, short, or avoid independently.
    Returns the dominant direction; if both fire, returns avoid (conflicting signals).
    """
    if fires_long and not fires_short:
        return {"fires": True,  "direction": "long",  "category": category,
                "signals_used": signals_used_long, "context_bullets": bullets_long}
    if fires_short and not fires_long:
        return {"fires": True,  "direction": "short", "category": category,
                "signals_used": signals_used_short, "context_bullets": bullets_short}
    if fires_long and fires_short:
        return {"fires": True,  "direction": "avoid", "category": category,
                "signals_used": signals_used_long + signals_used_short,
                "context_bullets": ["Conflicting long and short signals  -  avoid"]}
    return {"fires": False, "direction": None, "category": category,
            "signals_used": [], "context_bullets": []}


# -----------------------------------------------------------------------------
# CATEGORY 1: PIVOT-BASED (10 strategies)
# -----------------------------------------------------------------------------

def strat_pivot_s1_bounce(s):
    fl = (s.get("near_s1") and (s.get("hammer") or s.get("pin_bar")) and s.get("obv_bullish"))
    fs = (s.get("near_r1") and (s.get("shooting_star") or s.get("bearish_engulfing")) and not s.get("obv_bullish"))
    return _strat3(fl, fs, "pivot",
        ["near_s1","hammer/pin_bar","obv_bullish"], ["near_r1","shooting_star","obv_falling"],
        ["Price at S1 pivot support","Hammer or pin bar confirming buyers","OBV rising  -  accumulation"],
        ["Price at R1 pivot resistance","Shooting star or bearish engulfing rejecting highs","OBV falling  -  distribution"])


def strat_pivot_s2_bounce(s):
    fl = (s.get("near_s2") and s.get("rsi_14", 50) < 40 and (s.get("hammer") or s.get("bullish_engulfing")))
    fs = (s.get("near_r2") and s.get("rsi_14", 50) > 60 and s.get("bearish_engulfing"))
    return _strat3(fl, fs, "pivot",
        ["near_s2","rsi_14<40","bullish_candle"], ["near_r2","rsi_14>60","bearish_engulfing"],
        [f"Price at S2 deep support","RSI-14 oversold","Bullish candle confirms buyers"],
        [f"Price at R2 strong resistance","RSI-14 overbought","Bearish engulfing confirms sellers"])


def strat_pivot_s3_capitulation(s):
    fires = (s.get("near_s3") and
             s.get("rsi_14", 50) < 30 and
             s.get("vol_spike_2x"))
    return _strat(fires, "long", "pivot",
        ["near_s3","rsi_14<30","vol_spike_2x"],
        ["Price at S3  -  extreme capitulation level",
         f"RSI-14 extremely oversold at {s.get('rsi_14',0):.1f}",
         "Volume spike confirms panic selling  -  reversal likely"])


def strat_pivot_r1_breakout(s):
    """Pivot R1 breakout. Batch 205 (Pivot optimization 2026-05-17 owner-
    approved research review): stacked with Anchored VWAP gate (Brian
    Shannon 2022) + DiNapoli volume confirmation. AVWAP-from-252-day-low
    is the institutional reference level; breakouts above R1 that ALSO
    hold above AVWAP are markedly higher quality than R1 breaks in
    isolation.

    AVWAP gate defaults to True when avwap signals are absent (e.g.
    insufficient history) so backward-compat is preserved.
    """
    avwap_long_ok = s.get("above_avwap_252low", True) and s.get("above_avwap_50low", True)
    avwap_short_ok = (not s.get("above_avwap_252low", False)) and (not s.get("above_avwap_50low", False))
    fl = (
        s.get("above_r1") and s.get("vol_spike_15x")
        and s.get("macd_12_26_9_bullish") and avwap_long_ok
    )
    fs = (
        s.get("below_s1") and s.get("vol_spike_15x")
        and (not s.get("macd_12_26_9_bullish")) and avwap_short_ok
    )
    return _strat3(fl, fs, "pivot",
        ["above_r1", "vol_spike_1.5x", "macd_bullish",
         "above_avwap_252low", "above_avwap_50low"],
        ["below_s1", "vol_spike_1.5x", "macd_bearish",
         "below_avwap_252low", "below_avwap_50low"],
        ["Price broke above R1 resistance",
         "Volume 1.5x ADV(20) - institutional buying",
         "MACD positive",
         "Above Anchored VWAP (252d low + 50d low) - institutional reference"],
        ["Price broke below S1 support",
         "Volume 1.5x ADV(20) - institutional selling",
         "MACD negative",
         "Below Anchored VWAP (252d low + 50d low) - distribution"])


def strat_pivot_r2_continuation(s):
    """Pivot R2 trend-continuation. Batch 205: requires AVWAP + 2x volume
    (stronger threshold than R1 since R2 is the secondary breakout) +
    EMA 50/200 trend confirmation."""
    avwap_long_ok = s.get("above_avwap_252low", True) and s.get("above_avwap_50low", True)
    avwap_short_ok = (not s.get("above_avwap_252low", False)) and (not s.get("above_avwap_50low", False))
    # Stronger volume confirmation for R2 (2x ADV instead of 1.5x)
    fl = (
        s.get("above_r2") and s.get("adx_trending")
        and s.get("ema_50_200_bullish") and avwap_long_ok
        and s.get("vol_spike_2x", s.get("vol_spike_15x", False))
    )
    fs = (
        s.get("below_s2") and s.get("adx_trending")
        and (not s.get("ema_50_200_bullish")) and avwap_short_ok
        and s.get("vol_spike_2x", s.get("vol_spike_15x", False))
    )
    return _strat3(fl, fs, "pivot",
        ["above_r2", "adx_trending", "ema_50_200_bullish",
         "vol_spike_2x", "above_avwap_252low_and_50low"],
        ["below_s2", "adx_trending", "ema_50_200_bearish",
         "vol_spike_2x", "below_avwap_252low_and_50low"],
        ["Price above R2 - strong trend continuation",
         "ADX confirms trend", "Above 50/200 EMA",
         "Volume 2x ADV - heavy participation",
         "Above Anchored VWAP - institutional reference"],
        ["Price below R2 - strong downtrend continuation",
         "ADX confirms trend", "Below 50/200 EMA",
         "Volume 2x ADV - heavy participation",
         "Below Anchored VWAP - distribution"])


def strat_cpr_narrow_bullish(s):
    """Central Pivot Range narrow breakout. Batch 205: stacked with
    Anchored VWAP gate per Brian Shannon. Narrow CPR + above CPR + above
    AVWAP is the canonical institutional-grade directional day signal.
    """
    avwap_long_ok = s.get("above_avwap_50low", True)
    avwap_short_ok = not s.get("above_avwap_50low", False)
    fl = (
        s.get("cpr_narrow") and s.get("above_cpr")
        and s.get("rsi_14", 50) > 50 and avwap_long_ok
    )
    fs = (
        s.get("cpr_narrow") and s.get("below_cpr")
        and s.get("rsi_14", 50) < 50 and avwap_short_ok
    )
    return _strat3(fl, fs, "pivot",
        ["cpr_narrow", "above_cpr", "rsi_14>50", "above_avwap_50low"],
        ["cpr_narrow", "below_cpr", "rsi_14<50", "below_avwap_50low"],
        ["Narrow CPR - directional day likely", "Above CPR - bullish daily bias",
         "RSI above 50", "Above Anchored VWAP (50d low) - institutional reference"],
        ["Narrow CPR - directional day likely", "Below CPR - bearish daily bias",
         "RSI below 50", "Below Anchored VWAP (50d low) - distribution"])


def strat_camarilla_s3_bounce(s):
    fl = (s.get("near_cam_s3") and s.get("rsi_14", 50) < 35 and s.get("obv_bullish"))
    fs = (s.get("near_cam_r3") and s.get("rsi_14", 50) > 65 and not s.get("obv_bullish"))
    return _strat3(fl, fs, "pivot",
        ["near_cam_s3","rsi_14<35","obv_bullish"], ["near_cam_r3","rsi_14>65","obv_falling"],
        ["Price at Camarilla S3  -  primary support","RSI oversold","OBV confirming accumulation"],
        ["Price at Camarilla R3  -  primary resistance","RSI overbought","OBV confirming distribution"])


def strat_camarilla_r3_breakout(s):
    fl = (s.get("above_cam_r3") and s.get("vol_spike_2x"))
    fs = (s.get("below_cam_s3") and s.get("vol_spike_2x"))
    return _strat3(fl, fs, "pivot",
        ["above_cam_r3","vol_spike_2x"], ["below_cam_s3","vol_spike_2x"],
        ["Price broke above Camarilla R3  -  breakout mode","Volume 2x confirms institutional buying"],
        ["Price broke below Camarilla S3  -  breakdown mode","Volume 2x confirms institutional selling"])


def strat_prev_day_high_break(s):
    fl = (s.get("above_prev_high") and s.get("vol_spike_15x") and s.get("above_vwap"))
    fs = (s.get("below_prev_low") and s.get("vol_spike_15x") and not s.get("above_vwap"))
    return _strat3(fl, fs, "pivot",
        ["above_prev_high","vol_spike_1.5x","above_vwap"], ["below_prev_low","vol_spike_1.5x","below_vwap"],
        ["Price broke above previous day's high","Volume confirms participation","Above VWAP  -  buyers in control"],
        ["Price broke below previous day's low","Volume confirms participation","Below VWAP  -  sellers in control"])


def strat_prev_day_low_bounce(s):
    fl = (s.get("near_prev_low") and s.get("hammer") and s.get("cmf_positive"))
    fs = (s.get("near_prev_high") and s.get("shooting_star") and not s.get("cmf_positive"))
    return _strat3(fl, fs, "pivot",
        ["near_prev_low","hammer","cmf_positive"], ["near_prev_high","shooting_star","cmf_negative"],
        ["Price holding at previous day's low","Hammer  -  buyers defended the level","CMF positive"],
        ["Price stalling at previous day's high","Shooting star  -  sellers rejected the level","CMF negative"])


# -----------------------------------------------------------------------------
# CATEGORY 2: MOMENTUM (9 strategies)
# -----------------------------------------------------------------------------

def strat_macd_crossover(s):
    fl = s.get("macd_12_26_9_crossover_up")
    fs = s.get("macd_12_26_9_crossover_dn")
    return _strat3(fl, fs, "momentum",
        ["macd_12_26_9_crossover_up"], ["macd_12_26_9_crossover_dn"],
        ["MACD 12/26/9 crossed above zero  -  momentum turning positive"],
        ["MACD 12/26/9 crossed below zero  -  momentum turning negative"])


def strat_macd_fast_crossover(s):
    fl = s.get("macd_8_21_5_crossover_up")
    fs = s.get("macd_8_21_5_crossover_dn")
    return _strat3(fl, fs, "momentum",
        ["macd_8_21_5_crossover_up"], ["macd_8_21_5_crossover_dn"],
        ["Fast MACD 8/21/5 crossed above zero  -  early momentum shift bullish"],
        ["Fast MACD 8/21/5 crossed below zero  -  early momentum shift bearish"])


def strat_hull_rsi(s):
    """Hull MA + RSI(9) momentum. Batch 207 (2026-05-17 owner-approved
    research review): added ADX(14) > 20 trend confirmation gate. Hull
    alone whipsaws in choppy markets; Hull + ADX>20 cuts false-signal
    rate in half per multiple SSRN replications (cited in research
    report B.4). The 26 trades in Phase 1A-beta yielded Sharpe -0.26 and
    win rate 30.8% - classic whipsaw failure mode without trend filter.
    """
    adx_trend_ok = s.get("adx", 0) > 20 or s.get("adx_trending", False)
    fl = (
        s.get("hull_bullish") and s.get("price_above_hull")
        and s.get("rsi_9", 50) > 50 and adx_trend_ok
    )
    fs = (
        (not s.get("hull_bullish")) and (not s.get("price_above_hull"))
        and s.get("rsi_9", 50) < 50 and adx_trend_ok
    )
    return _strat3(fl, fs, "momentum",
        ["hull_bullish", "price_above_hull", "rsi_9>50", "adx>20"],
        ["hull_bearish", "price_below_hull", "rsi_9<50", "adx>20"],
        ["Hull MA rising - fast trend bullish", "Price above Hull",
         "RSI-9 above midpoint", "ADX>20 confirms trend"],
        ["Hull MA falling - fast trend bearish", "Price below Hull",
         "RSI-9 below midpoint", "ADX>20 confirms trend"])


def strat_williams_r_oversold(s):
    """Williams %R oversold-bounce. Batch 206 (Connors stack 2026-05-17):
    primary entry is Williams %R OR Connors RSI(2) extreme; both confirm
    short-window oversold. 200-EMA regime gate preserved (current best-
    performing strategy in Phase 1A-beta with Sharpe 0.30; intent is to
    tighten further without losing fill rate).

    BUG-11 RESOLVED-IMPLEMENTED Pass 53 v8h+1: short branch uses explicit
    default to prevent firing when key absent.
    """
    rsi_2 = s.get("rsi_2", 50)
    above_200 = s.get("price_above_ema_200", False)
    fl = (
        (s.get("williams_r_oversold") or (rsi_2 < 5))
        and above_200
        and s.get("cmf_positive")
    )
    fs = (
        (s.get("williams_r", 0) > -20 or (rsi_2 > 95))
        and (not above_200)
        and (not s.get("cmf_positive"))
    )
    return _strat3(fl, fs, "momentum",
        ["williams_r_oversold_or_rsi_2<5", "above_ema_200", "cmf_positive"],
        ["williams_r_overbought_or_rsi_2>95", "below_ema_200", "cmf_negative"],
        ["Williams %R oversold OR Connors RSI(2)<5 (short-window extreme)",
         "Above 200 EMA (regime gate)", "CMF positive"],
        ["Williams %R overbought OR RSI(2)>95",
         "Below 200 EMA (bear regime)", "CMF negative"])


def strat_roc_burst(s):
    fl = (s.get("roc_turning_up") and s.get("vol_spike_15x"))
    fs = (s.get("roc_turning_dn") and s.get("vol_spike_15x"))
    return _strat3(fl, fs, "momentum",
        ["roc_turning_up","vol_spike_1.5x"], ["roc_turning_dn","vol_spike_1.5x"],
        ["ROC-12 flipped positive  -  early momentum shift up","Volume confirms"],
        ["ROC-12 flipped negative  -  early momentum shift down","Volume confirms"])


def strat_awesome_oscillator(s):
    fl = (s.get("ao_cross_up") and s.get("price_above_ema_20"))
    fs = (s.get("ao_cross_dn") and not s.get("price_above_ema_20"))
    return _strat3(fl, fs, "momentum",
        ["ao_cross_up","price_above_ema_20"], ["ao_cross_dn","price_below_ema_20"],
        ["Awesome Oscillator crossed above zero  -  momentum positive","Above EMA-20"],
        ["Awesome Oscillator crossed below zero  -  momentum negative","Below EMA-20"])


def strat_stochrsi_oversold(s):
    """StochRSI oversold-bounce. Batch 206 (Connors stack 2026-05-17):
    add 200-EMA regime gate (Connors discipline). StochRSI cross-up is
    a momentum-turn signal; without the regime gate it fires aggressively
    in downtrends (Phase 1A-beta showed -1.01 expected_value at 132
    trades, indicating the strategy fires inside bear/downtrend bias)."""
    rsi_2 = s.get("rsi_2", 50)
    above_200 = s.get("price_above_ema_200", True)
    fl = (
        s.get("stochrsi_oversold") and s.get("stochrsi_cross_up")
        and s.get("rsi_14", 50) < 55 and above_200
    )
    fs = (
        s.get("stochrsi_overbought") and s.get("stochrsi_cross_dn")
        and s.get("rsi_14", 50) > 45 and (not above_200)
    )
    return _strat3(fl, fs, "momentum",
        ["stochrsi_oversold", "stochrsi_cross_up", "rsi_14<55", "above_ema_200"],
        ["stochrsi_overbought", "stochrsi_cross_dn", "rsi_14>45", "below_ema_200"],
        ["StochRSI oversold - below 20", "K crossed above D - momentum turning up",
         "RSI not overbought", "Above 200 EMA (regime gate)"],
        ["StochRSI overbought - above 80", "K crossed below D - momentum turning down",
         "RSI not oversold", "Below 200 EMA (bear regime)"])


def strat_ppo_crossover(s):
    fl = (s.get("ppo_crossover_up") and s.get("adx_trending"))
    fs = (s.get("ppo_crossover_dn") and s.get("adx_trending"))
    return _strat3(fl, fs, "momentum",
        ["ppo_crossover_up","adx_trending"], ["ppo_crossover_dn","adx_trending"],
        ["PPO crossed above signal  -  momentum bullish","ADX confirms trend"],
        ["PPO crossed below signal  -  momentum bearish","ADX confirms trend"])


def strat_ultimate_oscillator(s):
    """Ultimate Oscillator oversold-bounce. Batch 206 (Connors stack
    2026-05-17): primary signal upgraded to (uo_oversold OR rsi_2<5).
    UO already has 200-SMA regime gate; preserved as-is. Phase 1A-beta
    showed UO is the best Sharpe (0.49) carrier in the oversold family
    but only 27 trades; stacking with RSI(2) increases fill rate without
    sacrificing regime discipline."""
    rsi_2 = s.get("rsi_2", 50)
    fl = (
        (s.get("uo_oversold") or (rsi_2 < 5))
        and s.get("price_above_sma_200")
    )
    fs = (
        (s.get("uo", 50) > 70 or (rsi_2 > 95))
        and not s.get("price_above_sma_200")
    )
    return _strat3(fl, fs, "momentum",
        ["uo_oversold_or_rsi_2<5", "price_above_sma_200"],
        ["uo_overbought_or_rsi_2>95", "price_below_sma_200"],
        ["Ultimate Oscillator below 30 OR Connors RSI(2)<5",
         "Above 200 SMA (regime gate)"],
        ["Ultimate Oscillator above 70 OR RSI(2)>95",
         "Below 200 SMA (bear regime)"])


# -----------------------------------------------------------------------------
# CATEGORY 3: TREND FOLLOWING (9 strategies)
# -----------------------------------------------------------------------------

def strat_golden_cross_50_200(s):
    fl = s.get("ema_50_200_golden_cross")
    fs = s.get("ema_50_200_death_cross")
    return _strat3(fl, fs, "trend",
        ["ema_50_200_golden_cross"], ["ema_50_200_death_cross"],
        ["EMA-50 crossed above EMA-200  -  golden cross  -  structural shift bullish"],
        ["EMA-50 crossed below EMA-200  -  death cross  -  structural shift bearish"])


def strat_golden_cross_9_21(s):
    fl = (s.get("ema_9_21_golden_cross") and s.get("price_above_sma_50"))
    fs = (s.get("ema_9_21_death_cross") and not s.get("price_above_sma_50"))
    return _strat3(fl, fs, "trend",
        ["ema_9_21_golden_cross","price_above_sma_50"], ["ema_9_21_death_cross","price_below_sma_50"],
        ["EMA-9 crossed above EMA-21  -  early trend bullish","Above 50 SMA confirms"],
        ["EMA-9 crossed below EMA-21  -  early trend bearish","Below 50 SMA confirms"])


def strat_golden_cross_20_50(s):
    fl = (s.get("ema_20_50_golden_cross") and s.get("price_above_ema_200"))
    fs = (s.get("ema_20_50_death_cross") and not s.get("price_above_ema_200"))
    return _strat3(fl, fs, "trend",
        ["ema_20_50_golden_cross","price_above_ema_200"], ["ema_20_50_death_cross","price_below_ema_200"],
        ["EMA-20 crossed above EMA-50  -  medium-term trend bullish","Above 200 EMA confirms"],
        ["EMA-20 crossed below EMA-50  -  medium-term trend bearish","Below 200 EMA confirms"])


def strat_parabolic_sar_flip(s):
    fl = (s.get("psar_flip_up") and s.get("adx_trending"))
    fs = (s.get("psar_flip_dn") and s.get("adx_trending"))
    return _strat3(fl, fs, "trend",
        ["psar_flip_up","adx_trending"], ["psar_flip_dn","adx_trending"],
        ["Parabolic SAR flipped below price  -  trend reversal up","ADX confirms trend strength"],
        ["Parabolic SAR flipped above price  -  trend reversal down","ADX confirms trend strength"])


def strat_tema_dema(s):
    fl = (s.get("tema_cross_up") and s.get("price_above_tema"))
    fs = (s.get("tema_cross_dn") and not s.get("price_above_tema"))
    return _strat3(fl, fs, "trend",
        ["tema_cross_up","price_above_tema"], ["tema_cross_dn","price_below_tema"],
        ["TEMA crossed above DEMA  -  fast MA system bullish","Price above TEMA"],
        ["TEMA crossed below DEMA  -  fast MA system bearish","Price below TEMA"])


def strat_ichimoku_tk_cross(s):
    fl = (s.get("ichi_tk_cross_up") and not s.get("ichi_below_cloud"))
    fs = (s.get("ichi_tk_cross_dn") and s.get("ichi_below_cloud"))
    return _strat3(fl, fs, "trend",
        ["ichi_tk_cross_up","not_below_cloud"], ["ichi_tk_cross_dn","ichi_below_cloud"],
        ["Ichimoku Tenkan crossed above Kijun  -  TK cross bullish","Not below cloud"],
        ["Ichimoku Tenkan crossed below Kijun  -  TK cross bearish","Below cloud confirms downtrend"])


def strat_ichimoku_cloud_breakout(s):
    """Ichimoku cloud breakout. Batch 207 (2026-05-17 owner-approved
    research review): multi-timeframe Kumo gate per Linda Bradford
    Raschke - weekly Ichimoku cloud position must align with daily
    breakout direction. Phase 1A-beta showed 43 trades / 18.6% WR /
    Sharpe -1.00 - the second-worst strategy by Sharpe in the carrier
    set, indicating the daily-only Kumo is too permissive.

    Weekly gate defaults to True when ichi_weekly_*_cloud signals absent
    (insufficient daily history < 260 bars); backward-compat preserved.
    """
    weekly_long_ok = s.get("ichi_weekly_above_cloud", True)
    weekly_short_ok = s.get("ichi_weekly_below_cloud", True)
    fl = (
        s.get("ichi_above_cloud") and s.get("ichi_tk_bullish")
        and s.get("adx_trending") and weekly_long_ok
    )
    fs = (
        s.get("ichi_below_cloud") and s.get("ichi_tk_bearish")
        and s.get("adx_trending") and weekly_short_ok
    )
    return _strat3(fl, fs, "trend",
        ["ichi_above_cloud", "ichi_tk_bullish", "adx_trending",
         "ichi_weekly_above_cloud"],
        ["ichi_below_cloud", "ichi_tk_bearish", "adx_trending",
         "ichi_weekly_below_cloud"],
        ["Price above Ichimoku Cloud (daily) - full bullish structure",
         "Tenkan above Kijun", "ADX confirms",
         "Weekly Kumo also above cloud (multi-TF regime confirm)"],
        ["Price below Ichimoku Cloud (daily) - full bearish structure",
         "Tenkan below Kijun", "ADX confirms",
         "Weekly Kumo also below cloud (multi-TF regime confirm)"])


def strat_adx_initiation(s):
    fl = (s.get("adx_cross_up") and s.get("adx_di_bull"))
    fs = (s.get("adx_cross_up") and not s.get("adx_di_bull"))
    return _strat3(fl, fs, "trend",
        ["adx_cross_up","adx_di_bull"], ["adx_cross_up","adx_di_bear"],
        ["ADX crossed above 25  -  trend initiating","DI+ above DI-  -  bullish direction"],
        ["ADX crossed above 25  -  trend initiating","DI- above DI+  -  bearish direction"])


def strat_supertrend_macd(s):
    fl = (s.get("supertrend_bullish") and s.get("macd_12_26_9_bullish") and s.get("adx", 0) > 20)
    fs = (not s.get("supertrend_bullish") and not s.get("macd_12_26_9_bullish") and s.get("adx", 0) > 20)
    return _strat3(fl, fs, "trend",
        ["supertrend_bullish","macd_bullish","adx>20"], ["supertrend_bearish","macd_bearish","adx>20"],
        ["Supertrend bullish","MACD positive","ADX strong  -  trend confirmed"],
        ["Supertrend bearish","MACD negative","ADX strong  -  downtrend confirmed"])


# -----------------------------------------------------------------------------
# CATEGORY 4: MEAN REVERSION (11 strategies  -  including 2 shorts)
# -----------------------------------------------------------------------------

def strat_rsi_oversold(s):
    """RSI oversold dip-buy. Batch 206 (Connors stack 2026-05-17): upgrade
    primary signal to (rsi_2<5 OR rsi_14<35). Connors discipline: short-
    window RSI(2) extreme is the canonical mean-reversion trigger, with
    long-window RSI(14) as the slower-moving fallback. Adds 200-EMA
    regime gate (Connors filter) in addition to 50-SMA pullback context.
    Strategy had 0 trades in Phase 1A-beta with rsi_14<35 alone (rarely
    triggers); the rsi_2<5 path opens the strategy to fire on intraday
    extremes."""
    rsi_2 = s.get("rsi_2", 50)
    rsi_14 = s.get("rsi_14", 50)
    above_200 = s.get("price_above_ema_200", True)
    fl = (
        (rsi_2 < 5 or rsi_14 < 35)
        and s.get("price_above_sma_50")
        and above_200
    )
    fs = (
        (rsi_2 > 95 or rsi_14 > 65)
        and (not s.get("price_above_sma_50"))
        and (not above_200)
    )
    return _strat3(fl, fs, "mean_reversion",
        ["rsi_2<5_or_rsi_14<35", "price_above_sma_50", "price_above_ema_200"],
        ["rsi_2>95_or_rsi_14>65", "price_below_sma_50", "price_below_ema_200"],
        ["Connors RSI(2)<5 OR RSI(14)<35", "Above 50 SMA - buying dip",
         "Above 200 EMA (regime gate)"],
        ["RSI(2)>95 OR RSI(14)>65", "Below 50 SMA - selling rally",
         "Below 200 EMA (bear regime)"])


def strat_rsi9_extreme(s):
    # No natural short inverse  -  stays long-only (extreme oversold in uptrend)
    fires = (s.get("rsi_9_extreme_os") and s.get("price_above_ema_200") and s.get("rsi_9_rising"))
    return _strat(fires, "long", "mean_reversion",
        ["rsi_9<20","price_above_ema_200","rsi_9_rising"],
        [f"RSI-9 extreme oversold below 20","Above 200 EMA  -  uptrend context","RSI-9 rising  -  recovering"])


def strat_rsi21_slow(s):
    fl = (s.get("rsi_21", 50) < 35 and s.get("price_above_sma_50"))
    fs = (s.get("rsi_21", 50) > 65 and not s.get("price_above_sma_50"))
    return _strat3(fl, fs, "mean_reversion",
        ["rsi_21<35","price_above_sma_50"], ["rsi_21>65","price_below_sma_50"],
        [f"Slow RSI-21 oversold below 35","Above 50 SMA  -  uptrend context"],
        [f"Slow RSI-21 overbought above 65","Below 50 SMA  -  downtrend context"])


def strat_rsi_overbought_short(s):
    fires = (s.get("rsi_14", 50) > 68 and
             not s.get("price_above_sma_50") and
             (s.get("bearish_engulfing") or s.get("rsi_14_rising") == False))
    return _strat(fires, "short", "mean_reversion",
        ["rsi_14>68","below_sma_50","bearish_signal"],
        [f"RSI-14 overbought at {s.get('rsi_14',0):.1f}  -  above 68",
         "Below 50 SMA  -  selling rally in downtrend",
         "Bearish momentum confirms sellers taking control"])


def strat_mfi_oversold(s):
    fl = (s.get("mfi_oversold") and (s.get("near_s1") or s.get("near_s2")) and s.get("obv_bullish"))
    fs = (s.get("mfi_overbought") and (s.get("near_r1") or s.get("near_r2")) and not s.get("obv_bullish"))
    return _strat3(fl, fs, "mean_reversion",
        ["mfi_oversold","at_support","obv_bullish"], ["mfi_overbought","at_resistance","obv_falling"],
        ["MFI oversold  -  volume-weighted RSI below 20","At pivot support","OBV rising"],
        ["MFI overbought  -  volume-weighted RSI above 80","At pivot resistance","OBV falling"])


def strat_cmf_flip(s):
    fl = (s.get("cmf_cross_up") and s.get("rsi_14", 50) < 50)
    fs = (s.get("cmf_cross_dn") and s.get("rsi_14", 50) > 50)
    return _strat3(fl, fs, "mean_reversion",
        ["cmf_cross_up","rsi_14<50"], ["cmf_cross_dn","rsi_14>50"],
        ["CMF crossed above zero  -  money flow turned positive","RSI below 50"],
        ["CMF crossed below zero  -  money flow turned negative","RSI above 50"])


def strat_bollinger_lower(s):
    """Bollinger lower-band mean-reversion. Batch 204 (2026-05-17 owner-approved
    research review): stacked with Connors RSI(2)<5 OR vanilla RSI(14)<40
    AND price > 200-EMA regime gate (Connors discipline filter from
    Quantified Strategies 2024 backtest). VIX-conditional threshold:
    in low-VIX bands tighten to RSI(14)<35; in high-VIX bands loosen to
    RSI(14)<45 (Atlantis-Press Su 2024 multi-indicator confluence study).
    """
    rsi_2 = s.get("rsi_2", 50)
    rsi_14 = s.get("rsi_14", 50)
    above_200 = s.get("price_above_ema_200", True)
    adx_ok = s.get("adx", 30) < 30
    # VIX-conditional RSI threshold (defaults to 40 when no VIX context)
    if s.get("vix_band_low"):
        rsi_thr_long, rsi_thr_short = 35, 65
    elif s.get("vix_band_high"):
        rsi_thr_long, rsi_thr_short = 45, 55
    else:
        rsi_thr_long, rsi_thr_short = 40, 60
    # Long: BB touch lower AND (Connors RSI(2)<5 OR vanilla RSI<thr) AND
    # regime gate (price > 200-EMA) AND no strong trend.
    rsi_long_ok = (rsi_2 < 5) or (rsi_14 < rsi_thr_long)
    fl = (s.get("bb_20_20_touch_lower") and rsi_long_ok and above_200 and adx_ok)
    # Short: opposite side; no regime gate flip required (still requires
    # NOT above 200-EMA via the same boolean).
    rsi_short_ok = (rsi_2 > 95) or (rsi_14 > rsi_thr_short)
    fs = (s.get("bb_20_20_touch_upper") and rsi_short_ok and (not above_200) and adx_ok)
    return _strat3(fl, fs, "mean_reversion",
        ["bb_20_20_touch_lower", f"rsi_2<5_or_rsi_14<{rsi_thr_long}",
         "price_above_ema_200", "adx<30"],
        ["bb_20_20_touch_upper", f"rsi_2>95_or_rsi_14>{rsi_thr_short}",
         "price_below_ema_200", "adx<30"],
        [f"Price at lower Bollinger Band - statistically extreme low",
         f"RSI(2)<5 Connors extreme OR RSI(14)<{rsi_thr_long}",
         "Price above 200-EMA (regime gate)", "No strong trend"],
        [f"Price at upper Bollinger Band - statistically extreme high",
         f"RSI(2)>95 OR RSI(14)>{rsi_thr_short}",
         "Price below 200-EMA (bear regime)", "No strong trend"])


def strat_bollinger_tight(s):
    """Tight Bollinger touch mean-reversion. Batch 204 (owner-approved
    research review 2026-05-17): same stacking discipline as
    strat_bollinger_lower but uses tighter 1.5-sigma band and a softer
    RSI threshold (Bollinger 1.5sig is by definition more frequent so
    requires less-stringent oscillator confirmation).
    """
    rsi_2 = s.get("rsi_2", 50)
    rsi_14 = s.get("rsi_14", 50)
    above_200 = s.get("price_above_ema_200", True)
    # VIX-conditional threshold (slightly looser than bollinger_lower since
    # the 1.5sig band is more frequent)
    if s.get("vix_band_low"):
        rsi_thr_long, rsi_thr_short = 40, 60
    elif s.get("vix_band_high"):
        rsi_thr_long, rsi_thr_short = 50, 50
    else:
        rsi_thr_long, rsi_thr_short = 45, 55
    rsi_long_ok = (rsi_2 < 10) or (rsi_14 < rsi_thr_long)
    fl = (
        (s.get("bb_20_15_touch_lower") or s.get("bb_20_20_touch_lower"))
        and rsi_long_ok
        and above_200
    )
    rsi_short_ok = (rsi_2 > 90) or (rsi_14 > rsi_thr_short)
    fs = (
        (s.get("bb_20_15_touch_upper") or s.get("bb_20_20_touch_upper"))
        and rsi_short_ok
        and (not above_200)
    )
    return _strat3(fl, fs, "mean_reversion",
        ["bb_touch_lower_tight", f"rsi_2<10_or_rsi_14<{rsi_thr_long}",
         "price_above_ema_200"],
        ["bb_touch_upper_tight", f"rsi_2>90_or_rsi_14>{rsi_thr_short}",
         "price_below_ema_200"],
        ["Price at tight lower Bollinger Band - extreme low",
         f"RSI(2)<10 OR RSI(14)<{rsi_thr_long}",
         "Price above 200-EMA (regime gate)"],
        ["Price at tight upper Bollinger Band - extreme high",
         f"RSI(2)>90 OR RSI(14)>{rsi_thr_short}",
         "Price below 200-EMA (bear regime)"])


def strat_bollinger_upper_short(s):
    fires = (s.get("bb_20_20_touch_upper") and
             s.get("rsi_14", 50) > 70 and
             s.get("shooting_star"))
    return _strat(fires, "short", "mean_reversion",
        ["bb_20_20_touch_upper","rsi_14>70","shooting_star"],
        [f"Price at upper Bollinger Band (20,2)  -  overbought extreme",
         f"RSI-14 at {s.get('rsi_14',0):.1f}  -  overbought above 70",
         "Shooting star candle  -  sellers rejecting the high"])


def strat_keltner_lower(s):
    fl = (s.get("kc_touch_lower") and s.get("hammer") and s.get("obv_bullish"))
    fs = (s.get("kc_touch_upper") and s.get("shooting_star") and not s.get("obv_bullish"))
    return _strat3(fl, fs, "mean_reversion",
        ["kc_touch_lower","hammer","obv_bullish"], ["kc_touch_upper","shooting_star","obv_falling"],
        ["Price at lower Keltner Channel","Hammer confirms buyers","OBV rising"],
        ["Price at upper Keltner Channel","Shooting star confirms sellers","OBV falling"])


def strat_stoch_oversold(s):
    fl = (s.get("stoch_oversold") and s.get("stoch_bullish_cross") and s.get("price_above_ema_20"))
    fs = (s.get("stoch_overbought") and s.get("stoch_bearish_cross") and not s.get("price_above_ema_20"))
    return _strat3(fl, fs, "mean_reversion",
        ["stoch_oversold","stoch_bullish_cross","price_above_ema_20"], ["stoch_overbought","stoch_bearish_cross","price_below_ema_20"],
        ["Stochastic oversold below 20","K crossed above D  -  turning bullish","Above EMA-20"],
        ["Stochastic overbought above 80","K crossed below D  -  turning bearish","Below EMA-20"])


# -----------------------------------------------------------------------------
# CATEGORY 5: BREAKOUT (6 strategies)
# -----------------------------------------------------------------------------

def strat_squeeze_breakout(s):
    fires = s.get("squeeze_fire_up")
    return _strat(fires, "long", "breakout",
        ["squeeze_fire_up"],
        ["Bollinger Bands were inside Keltner Channels  -  coiling",
         "Squeeze released with positive momentum  -  energy unleashing",
         "One of the highest probability breakout signals"])


def strat_volume_spike_breakout(s):
    fl = (s.get("dc20_breakout_up") and s.get("vol_spike_2x") and s.get("above_vwap"))
    fs = (s.get("dc20_breakout_dn") and s.get("vol_spike_2x") and not s.get("above_vwap"))
    return _strat3(fl, fs, "breakout",
        ["dc20_breakout_up","vol_spike_2x","above_vwap"], ["dc20_breakout_dn","vol_spike_2x","below_vwap"],
        ["Price broke above 20-day Donchian high","Volume 2x confirms","Above VWAP"],
        ["Price broke below 20-day Donchian low","Volume 2x confirms","Below VWAP"])


def strat_52w_high_breakout(s):
    fires = (s.get("break_52w_high") and
             s.get("vol_spike_2x"))
    return _strat(fires, "long", "breakout",
        ["break_52w_high","vol_spike_2x"],
        [f"Price broke 52-week high at ${s.get('year_high',0):.2f}",
         "Most studied momentum signal  -  new highs attract buyers",
         "Volume 2x confirms institutional conviction"])


def strat_inside_bar_breakout(s):
    fires = (s.get("inside_bar") and
             s.get("adx_trending") and
             s.get("above_vwap"))
    return _strat(fires, "long", "breakout",
        ["inside_bar","adx_trending","above_vwap"],
        ["Inside bar formed  -  consolidation within prior bar's range",
         "Classic pre-breakout compression setup",
         "ADX trending and above VWAP  -  breakout direction likely up"])


def strat_force_index_breakout(s):
    fl = (s.get("force_index_cross_up") and s.get("price_above_ema_20"))
    fs = (s.get("force_index_cross_dn") and not s.get("price_above_ema_20"))
    return _strat3(fl, fs, "breakout",
        ["force_index_cross_up","price_above_ema_20"], ["force_index_cross_dn","price_below_ema_20"],
        ["Force Index crossed above zero  -  pricexvolume momentum positive","Above EMA-20"],
        ["Force Index crossed below zero  -  pricexvolume momentum negative","Below EMA-20"])


def strat_donchian_10_breakout(s):
    fl = (s.get("dc10_breakout_up") and s.get("vol_spike_15x") and s.get("macd_12_26_9_bullish"))
    fs = (s.get("dc10_breakout_dn") and s.get("vol_spike_15x") and not s.get("macd_12_26_9_bullish"))
    return _strat3(fl, fs, "breakout",
        ["dc10_breakout_up","vol_spike_1.5x","macd_bullish"], ["dc10_breakout_dn","vol_spike_1.5x","macd_bearish"],
        ["Price broke 10-day Donchian high","Volume 1.5x confirms","MACD positive"],
        ["Price broke 10-day Donchian low","Volume 1.5x confirms","MACD negative"])


# -----------------------------------------------------------------------------
# CATEGORY 6: CANDLE PATTERNS (6 strategies  -  2 shorts)
# -----------------------------------------------------------------------------

def strat_morning_star(s):
    fl = (s.get("morning_star") and s.get("rsi_14", 50) < 45 and s.get("ema_50_200_bullish"))
    fs = (s.get("evening_star") and s.get("rsi_14", 50) > 55 and not s.get("ema_50_200_bullish"))
    return _strat3(fl, fs, "candle",
        ["morning_star","rsi_14<45","ema_50_200_bullish"], ["evening_star","rsi_14>55","ema_50_200_bearish"],
        ["Three-bar morning star  -  bullish reversal","RSI not overbought","Above 50/200 EMA"],
        ["Three-bar evening star  -  bearish reversal","RSI not oversold","Below 50/200 EMA"])


def strat_bullish_engulfing_support(s):
    fl = (s.get("bullish_engulfing") and (s.get("near_s1") or s.get("near_s2") or s.get("at_key_fib")) and s.get("obv_bullish"))
    fs = (s.get("bearish_engulfing") and (s.get("near_r1") or s.get("near_r2") or s.get("at_key_fib")) and not s.get("obv_bullish"))
    return _strat3(fl, fs, "candle",
        ["bullish_engulfing","at_support","obv_bullish"], ["bearish_engulfing","at_resistance","obv_falling"],
        ["Bullish engulfing at support  -  two systems confirming","OBV rising"],
        ["Bearish engulfing at resistance  -  two systems confirming","OBV falling"])


def strat_doji_at_support(s):
    fires = (s.get("doji") and
             (s.get("near_s1") or s.get("near_s2") or s.get("at_key_fib")) and
             s.get("vol_spike_15x"))
    return _strat(fires, "long", "candle",
        ["doji","at_support","vol_spike_1.5x"],
        ["Doji candle at support  -  indecision after downmove",
         "Buyers and sellers equally matched  -  reversal often follows",
         "Volume spike confirms the level is being contested"])


def strat_three_white_soldiers(s):
    fires = (s.get("three_white_soldiers") and
             s.get("rsi_14", 50) < 60)
    return _strat(fires, "long", "candle",
        ["three_white_soldiers","rsi_14<60"],
        ["Three consecutive bullish candles each closing near their high",
         "Strong reversal signal  -  sustained buying pressure over 3 days",
         "RSI below 60  -  room to run, not entering overbought"])


def strat_shooting_star_short(s):
    fires = (s.get("shooting_star") and
             (s.get("near_r1") or s.get("near_r2") or
              s.get("bb_20_20_touch_upper")) and
             s.get("rsi_14", 50) > 65)
    return _strat(fires, "short", "candle",
        ["shooting_star","at_resistance","rsi_14>65"],
        ["Shooting star at resistance level  -  bearish reversal",
         "Long upper wick shows sellers rejecting higher prices",
         f"RSI-14 at {s.get('rsi_14',0):.1f}  -  overbought at resistance"])


def strat_evening_star_short(s):
    fires = (s.get("evening_star") and
             s.get("rsi_14", 50) > 55 and
             not s.get("price_above_sma_50"))
    return _strat(fires, "short", "candle",
        ["evening_star","rsi_14>55","below_sma_50"],
        ["Three-bar evening star  -  bearish reversal pattern",
         "Mirror of morning star: buyers exhausted, sellers take control",
         "Below 50 SMA confirms downtrend context for the short"])


# -----------------------------------------------------------------------------
# CATEGORY 7: CONFLUENCE (9 strategies  -  highest conviction)
# -----------------------------------------------------------------------------

def strat_rsi_volume_200ema(s):
    fl = (s.get("rsi_14", 50) < 35 and s.get("vol_spike_2x") and s.get("price_above_ema_200"))
    fs = (s.get("rsi_14", 50) > 65 and s.get("vol_spike_2x") and not s.get("price_above_ema_200"))
    return _strat3(fl, fs, "confluence",
        ["rsi_14<35","vol_spike_2x","above_ema_200"], ["rsi_14>65","vol_spike_2x","below_ema_200"],
        ["RSI oversold + volume spike + above 200 EMA  -  triple confluence bullish"],
        ["RSI overbought + volume spike + below 200 EMA  -  triple confluence bearish"])


def strat_macd_ichimoku(s):
    fl = (s.get("macd_12_26_9_crossover_up") and s.get("ichi_above_cloud"))
    fs = (s.get("macd_12_26_9_crossover_dn") and s.get("ichi_below_cloud"))
    return _strat3(fl, fs, "confluence",
        ["macd_crossover_up","ichi_above_cloud"], ["macd_crossover_dn","ichi_below_cloud"],
        ["MACD crossover up + above cloud  -  two systems bullish simultaneously"],
        ["MACD crossover down + below cloud  -  two systems bearish simultaneously"])


def strat_bb_squeeze_volume(s):
    fl = (s.get("squeeze_fire_up") and s.get("vol_spike_2x") and s.get("above_vwap"))
    fs = (s.get("squeeze_fire_dn") and s.get("vol_spike_2x") and not s.get("above_vwap"))
    return _strat3(fl, fs, "confluence",
        ["squeeze_fire_up","vol_spike_2x","above_vwap"], ["squeeze_fire_dn","vol_spike_2x","below_vwap"],
        ["BB squeeze releasing upward with 2x volume","Above VWAP  -  buyers in control"],
        ["BB squeeze releasing downward with 2x volume","Below VWAP  -  sellers in control"])


def strat_pivot_fib_confluence(s):
    fl = ((s.get("near_s1") or s.get("near_s2")) and s.get("at_key_fib") and (s.get("hammer") or s.get("bullish_engulfing")))
    fs = ((s.get("near_r1") or s.get("near_r2")) and s.get("at_key_fib") and s.get("bearish_engulfing"))
    return _strat3(fl, fs, "confluence",
        ["at_pivot_support","at_key_fib","bullish_candle"], ["at_pivot_resistance","at_key_fib","bearish_engulfing"],
        ["Pivot support + Fibonacci + bullish candle  -  two systems at same level bullish"],
        ["Pivot resistance + Fibonacci + bearish engulfing  -  two systems at same level bearish"])


def strat_golden_cross_volume(s):
    fl = (s.get("ema_50_200_golden_cross") and s.get("vol_spike_2x"))
    fs = (s.get("ema_50_200_death_cross") and s.get("vol_spike_2x"))
    return _strat3(fl, fs, "confluence",
        ["ema_50_200_golden_cross","vol_spike_2x"], ["ema_50_200_death_cross","vol_spike_2x"],
        ["Golden cross with 2x volume  -  institutional confirmation of bullish shift"],
        ["Death cross with 2x volume  -  institutional confirmation of bearish shift"])


def strat_cpr_narrow_momentum(s):
    fl = (s.get("cpr_narrow") and s.get("above_cpr") and s.get("rsi_14", 50) > 50 and s.get("macd_12_26_9_bullish"))
    fs = (s.get("cpr_narrow") and s.get("below_cpr") and s.get("rsi_14", 50) < 50 and not s.get("macd_12_26_9_bullish"))
    return _strat3(fl, fs, "confluence",
        ["cpr_narrow","above_cpr","rsi_14>50","macd_bullish"], ["cpr_narrow","below_cpr","rsi_14<50","macd_bearish"],
        ["Narrow CPR + above CPR + RSI>50 + MACD bullish  -  four signals confirming bullish day"],
        ["Narrow CPR + below CPR + RSI<50 + MACD bearish  -  four signals confirming bearish day"])


def strat_camarilla_rsi_obv(s):
    fl = (s.get("near_cam_s3") and s.get("rsi_14", 50) < 35 and s.get("obv_bullish") and s.get("cmf_positive"))
    fs = (s.get("near_cam_r3") and s.get("rsi_14", 50) > 65 and not s.get("obv_bullish") and not s.get("cmf_positive"))
    return _strat3(fl, fs, "confluence",
        ["near_cam_s3","rsi_14<35","obv_bullish","cmf_positive"], ["near_cam_r3","rsi_14>65","obv_falling","cmf_negative"],
        ["Camarilla S3 + RSI oversold + OBV rising + CMF positive  -  highest conviction long"],
        ["Camarilla R3 + RSI overbought + OBV falling + CMF negative  -  highest conviction short"])


def strat_supertrend_ichimoku_adx(s):
    fl = (s.get("supertrend_bullish") and s.get("ichi_above_cloud") and s.get("adx_strong"))
    fs = (not s.get("supertrend_bullish") and s.get("ichi_below_cloud") and s.get("adx_strong"))
    return _strat3(fl, fs, "confluence",
        ["supertrend_bullish","ichi_above_cloud","adx_strong"], ["supertrend_bearish","ichi_below_cloud","adx_strong"],
        ["Supertrend + Ichimoku cloud + ADX  -  three trend systems bullish"],
        ["Supertrend + Ichimoku cloud + ADX  -  three trend systems bearish"])


def strat_williams_stoch_dual(s):
    fl = (s.get("williams_r_oversold") and s.get("stoch_oversold") and (s.get("near_s1") or s.get("near_s2") or s.get("near_cam_s3")))
    fs = (s.get("williams_r", 0) > -20 and s.get("stoch_overbought") and (s.get("near_r1") or s.get("near_r2") or s.get("near_cam_r3")))
    return _strat3(fl, fs, "confluence",
        ["williams_r_oversold","stoch_oversold","at_pivot_support"], ["williams_r_overbought","stoch_overbought","at_pivot_resistance"],
        ["Williams %R + Stochastic both oversold at pivot support  -  high conviction long"],
        ["Williams %R + Stochastic both overbought at pivot resistance  -  high conviction short"])


# -----------------------------------------------------------------------------
# CATEGORY 8: DEDICATED SHORT STRATEGIES (12 new  -  sell the rip)
# -----------------------------------------------------------------------------

# --- Trend-following shorts (4) ---

def strat_death_cross_50_200_volume(s):
    fires = (s.get("ema_50_200_death_cross") and s.get("vol_spike_2x"))
    return _strat(fires, "short", "trend",
        ["ema_50_200_death_cross", "vol_spike_2x"],
        ["EMA-50 crossed below EMA-200  -  death cross",
         "Volume 2x confirms institutional selling on the cross",
         "Structural shift to bearish  -  strong follow-through expected"])


def strat_supertrend_macd_short(s):
    fires = (not s.get("supertrend_bullish") and
             not s.get("macd_12_26_9_bullish") and
             s.get("adx", 0) > 20)
    return _strat(fires, "short", "trend",
        ["supertrend_bearish", "macd_bearish", "adx>20"],
        ["Supertrend indicator bearish  -  trend confirmed downward",
         "MACD histogram negative  -  momentum aligned bearish",
         "ADX above 20  -  trend has real strength, not a sideways drift"])


def strat_ichimoku_cloud_breakdown(s):
    fires = (s.get("ichi_below_cloud") and
             s.get("ichi_tk_cross_dn") and
             s.get("adx_trending"))
    return _strat(fires, "short", "trend",
        ["ichi_below_cloud", "ichi_tk_cross_dn", "adx_trending"],
        ["Price broke below Ichimoku Cloud  -  full bearish structure",
         "Tenkan crossed below Kijun  -  short-term momentum confirming",
         "ADX trending  -  downtrend has strength"])


def strat_parabolic_sar_flip_short(s):
    fires = (s.get("psar_flip_dn") and s.get("adx_trending"))
    return _strat(fires, "short", "trend",
        ["psar_flip_dn", "adx_trending"],
        ["Parabolic SAR flipped above price  -  trend reversed downward",
         "Clean unambiguous signal  -  SAR is now resistance",
         "ADX trending  -  reversal has follow-through potential"])


# --- Momentum shorts (3) ---

def strat_macd_crossover_short(s):
    fires = s.get("macd_12_26_9_crossover_dn")
    return _strat(fires, "short", "momentum",
        ["macd_12_26_9_crossover_dn"],
        ["MACD 12/26/9 histogram crossed below zero",
         "Momentum turned negative  -  trend shift to downside",
         "High-probability momentum entry  -  catching the shift early"])


def strat_hull_rsi_short(s):
    fires = (not s.get("hull_bullish") and
             not s.get("price_above_hull") and
             s.get("rsi_9", 50) < 50)
    return _strat(fires, "short", "momentum",
        ["hull_bearish", "price_below_hull", "rsi_9<50"],
        ["Hull MA falling  -  fast trend confirmed bearish",
         "Price below Hull MA  -  momentum aligned downward",
         "RSI-9 below 50  -  below midpoint, no upside momentum"])


def strat_stochrsi_overbought_short(s):
    fires = (s.get("stochrsi_overbought") and
             s.get("stochrsi_cross_dn") and
             s.get("rsi_14", 50) > 45)
    return _strat(fires, "short", "momentum",
        ["stochrsi_overbought", "stochrsi_cross_dn", "rsi_14>45"],
        ["StochRSI above 80  -  momentum exhausted at overbought",
         "K crossed below D  -  momentum turning down",
         "RSI-14 not oversold  -  room to fall"])


# --- Breakdown shorts (3  -  no long equivalent) ---

def strat_donchian_breakdown_short(s):
    fires = (s.get("dc10_breakout_dn") and
             s.get("vol_spike_15x") and
             not s.get("macd_12_26_9_bullish"))
    return _strat(fires, "short", "breakout",
        ["dc10_breakout_dn", "vol_spike_1.5x", "macd_bearish"],
        ["Price broke 10-day Donchian low  -  downside breakout",
         "Volume 1.5x confirms institutional selling pressure",
         "MACD negative  -  momentum confirms the breakdown"])


def strat_52w_low_breakdown(s):
    fires = (s.get("break_52w_low") and s.get("vol_spike_2x"))
    return _strat(fires, "short", "breakout",
        ["break_52w_low", "vol_spike_2x"],
        [f"Price broke 52-week low  -  serious capitulation signal",
         "Volume 2x confirms institutional distribution",
         "Stocks at new 52-week lows tend to continue lower"])


def strat_prev_day_low_breakdown(s):
    fires = (s.get("below_prev_low") and
             s.get("vol_spike_15x") and
             not s.get("above_vwap"))
    return _strat(fires, "short", "breakout",
        ["below_prev_low", "vol_spike_1.5x", "below_vwap"],
        ["Price broke below previous day's low  -  failed to hold support",
         "Volume confirms sellers in control",
         "Below VWAP  -  intraday sellers dominating"])


# --- Confluence shorts (2) ---

def strat_camarilla_rsi_obv_short(s):
    fires = (s.get("near_cam_r3") and
             s.get("rsi_14", 50) > 65 and
             not s.get("obv_bullish") and
             not s.get("cmf_positive"))
    return _strat(fires, "short", "confluence",
        ["near_cam_r3", "rsi_14>65", "obv_falling", "cmf_negative"],
        ["Camarilla R3  -  strongest institutional resistance",
         "RSI-14 overbought above 65",
         "OBV falling and CMF negative  -  four systems confirming short"])


def strat_cpr_narrow_momentum_short(s):
    fires = (s.get("cpr_narrow") and
             s.get("below_cpr") and
             s.get("rsi_14", 50) < 50 and
             not s.get("macd_12_26_9_bullish"))
    return _strat(fires, "short", "confluence",
        ["cpr_narrow", "below_cpr", "rsi_14<50", "macd_bearish"],
        ["Narrow CPR  -  directional day expected",
         "Price below CPR  -  bearish professional bias",
         "RSI<50 and MACD bearish  -  four signals confirming bearish day"])


# -----------------------------------------------------------------------------
# BREAK-AND-RETEST STRATEGIES  -  BUG-111 Layer 3 additions
# DEC-355 through DEC-362 chart pattern spec (config.py CHART_PATTERN_STRATEGIES)
# mandates break+retest entry trigger. These 5 strategies implement that requirement
# for the core breakout categories (Breakout + Pivot + Confluence).
# -----------------------------------------------------------------------------

def strat_dc20_break_retest(s):
    """BUG-111: DC20 break-and-retest -- breakout above 20-day channel confirmed by retest hold."""
    fl = (s.get("resistance_break_retest") and s.get("vol_spike_15x") and s.get("adx_trending"))
    fs = (s.get("support_break_retest") and s.get("vol_spike_15x") and s.get("adx_trending"))
    return _strat3(fl, fs, "breakout",
        ["resistance_break_retest", "vol_spike_15x", "adx_trending"],
        ["support_break_retest", "vol_spike_15x", "adx_trending"],
        "DC20 break-and-retest: channel high broken, retested as support, ADX trending",
        "DC20 breakdown-and-retest: channel low broken, retested as resistance, ADX trending")


def strat_r1_break_retest(s):
    """BUG-111: Pivot R1 break-and-retest -- R1 broken then retested as support."""
    fl = (s.get("resistance_break_retest") and s.get("above_r1") and s.get("macd_12_26_9_bullish"))
    fs = (s.get("support_break_retest") and s.get("below_s1") and not s.get("macd_12_26_9_bullish"))
    return _strat3(fl, fs, "pivot",
        ["resistance_break_retest", "above_r1", "macd_12_26_9_bullish"],
        ["support_break_retest", "below_s1", "macd_12_26_9_bearish"],
        "R1 break-and-retest: pivot resistance now acting as support with MACD momentum",
        "S1 breakdown-and-retest: pivot support now acting as resistance with MACD bearish")


def strat_52wh_break_retest(s):
    """BUG-111: 52-week high break-and-retest -- historical resistance becomes support."""
    fl = (s.get("resistance_break_retest") and s.get("near_52w_high") and s.get("price_above_ema_200"))
    return _strat(fl, "long", "breakout",
        ["resistance_break_retest", "near_52w_high", "price_above_ema_200"],
        "52-week high break-and-retest: strongest historical resistance confirmed as support above 200 EMA")


def strat_break_retest_volume(s):
    """BUG-111: Break-and-retest confirmed by volume expansion on the bounce bar."""
    fl = (s.get("resistance_break_retest") and s.get("vol_spike_2x") and s.get("obv_rising"))
    fs = (s.get("support_break_retest") and s.get("vol_spike_2x") and not s.get("obv_rising"))
    return _strat3(fl, fs, "breakout",
        ["resistance_break_retest", "vol_spike_2x", "obv_rising"],
        ["support_break_retest", "vol_spike_2x", "obv_falling"],
        "Break-and-retest + 2x volume: institutional accumulation on the bounce",
        "Breakdown-and-retest + 2x volume: institutional distribution on the rejection")


def strat_break_retest_confluence(s):
    """BUG-111: Break-and-retest with multi-indicator confluence confirmation."""
    fl = (s.get("resistance_break_retest") and s.get("macd_12_26_9_bullish")
          and s.get("price_above_ema_20") and s.get("price_above_ema_50"))
    fs = (s.get("support_break_retest") and not s.get("macd_12_26_9_bullish")
          and not s.get("price_above_ema_20") and not s.get("price_above_ema_50"))
    return _strat3(fl, fs, "confluence",
        ["resistance_break_retest", "macd_12_26_9_bullish", "price_above_ema_20", "price_above_ema_50"],
        ["support_break_retest", "macd_bearish", "below_ema_20", "below_ema_50"],
        "Break-and-retest confluence: MACD + dual EMA confirms breakout continuation",
        "Breakdown-and-retest confluence: MACD + dual EMA confirms breakdown continuation")


# -----------------------------------------------------------------------------
# STRATEGY REGISTRY  -  Layer 1 baseline 60 + currently-implemented dedicated shorts
# (full layered roster ~108-133 classes per CANONICAL_FACTS.md F-002; layered
#  roster: Layer 1 baseline 60 + Layer 2 Phase 0.D ICT/Earnings/Calendar + Layer 2D
#  form-derived ICT + Layer 3 Pass 52 RESOLVED chart-pattern/categories + Layer 4
#  PENDING strategy-additive). Run `len(ALL_STRATEGIES)` for current count.
# -----------------------------------------------------------------------------

def strat_orb_stocks_in_play_long(s):
    """Batch 211 (ORB stocks-in-play 2026-05-17 owner-approved research review).
    Opening Range Breakout for "stocks in play" per Zarattini-Barbon-Aziz
    (2024) SSRN 4729284 "A Profitable Day Trading Strategy For The U.S.
    Equity Market". Paper documents +1,600% return / Sharpe 2.81 on Top-20
    high-volume stocks-in-play with intraday 5-min ORB.

    DAILY-BAR APPROXIMATION: true intraday ORB requires 5-min bars (this
    engine operates on daily). Daily proxy uses:
      - "in-play" filter: gap_up_pct > +2% (vs prev close) - market is
        reacting to overnight catalyst, matching Zarattini's stocks-in-play
        criteria
      - "ORB high break" proxy: close > today's open (close-above-open
        is the daily-bar analogue of breaking the opening range high)
      - Volume confirmation: 2x ADV(20) (Zarattini emphasizes institutional
        participation as a primary edge)
      - 200-EMA regime gate (long-only buy bias)
    """
    fires = (
        s.get("gap_up_2pct", False)
        and s.get("close_above_open", False)
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_200", True)
    )
    gap = s.get("gap_up_pct", 0.0)
    return _strat(fires, "long", "orb",
        ["gap_up_pct>2", "close_above_open", "vol_spike_2x", "price_above_ema_200"],
        [f"Gap up +{gap:.1f}% - in-play catalyst",
         "Close above open - intraday momentum positive",
         "Volume 2x ADV(20) - institutional participation",
         "Above 200 EMA (regime gate)"])


def strat_orb_stocks_in_play_short(s):
    """Batch 211: Symmetric short for gap-down stocks-in-play.
    Daily-bar proxy: gap_dn_pct > 2%, close < open, 2x volume, below
    200-EMA regime gate."""
    fires = (
        s.get("gap_dn_2pct", False)
        and s.get("close_below_open", False)
        and s.get("vol_spike_2x", False)
        and (not s.get("price_above_ema_200", True))
    )
    gap = s.get("gap_dn_pct", 0.0)
    return _strat(fires, "short", "orb",
        ["gap_dn_pct>2", "close_below_open", "vol_spike_2x", "price_below_ema_200"],
        [f"Gap down -{gap:.1f}% - in-play catalyst",
         "Close below open - intraday momentum negative",
         "Volume 2x ADV(20) - institutional participation",
         "Below 200 EMA (bear regime confirmation)"])


def strat_po3_bullish(s):
    """Batch 217 (PO3 + multi-TF 2026-05-18 owner-approved). Power of 3
    bullish daily candle: open near top, manipulation sweeps below
    prior-day low, distribution closes in upper third of range. ICT
    pattern marking institutional accumulation after a stop hunt."""
    fires = (
        s.get("po3_bullish", False)
        and s.get("price_above_ema_200", True)
    )
    return _strat(fires, "long", "po3",
        ["po3_bullish", "price_above_ema_200"],
        ["Bullish PO3 daily candle: sweep below prior low + close upper third",
         "Above 200 EMA (regime gate)"])


def strat_po3_bearish(s):
    """Batch 217: Symmetric bearish PO3 daily."""
    fires = (
        s.get("po3_bearish", False)
        and (not s.get("price_above_ema_200", True))
    )
    return _strat(fires, "short", "po3",
        ["po3_bearish", "price_below_ema_200"],
        ["Bearish PO3 daily candle: sweep above prior high + close lower third",
         "Below 200 EMA (bear regime)"])


def strat_po3_htf_aligned_long(s):
    """Batch 217: PO3 bullish + weekly bias bullish - high-conviction
    long with higher-timeframe directional alignment."""
    fires = (
        s.get("po3_bullish", False)
        and s.get("weekly_bias_bull", False)
    )
    return _strat(fires, "long", "po3",
        ["po3_bullish", "weekly_bias_bull"],
        ["Bullish PO3 daily candle",
         "Weekly bias bullish - higher-TF alignment"])


def strat_po3_htf_aligned_short(s):
    """Batch 217: Symmetric for bearish PO3 with weekly bear bias."""
    fires = (
        s.get("po3_bearish", False)
        and s.get("weekly_bias_bear", False)
    )
    return _strat(fires, "short", "po3",
        ["po3_bearish", "weekly_bias_bear"],
        ["Bearish PO3 daily candle",
         "Weekly bias bearish - higher-TF alignment"])


def strat_htf_aligned_breakout_long(s):
    """Batch 217: Multi-timeframe-aligned daily breakout. Daily breakout
    above prev-day high + weekly + monthly biases both bullish. Triple-
    timeframe confluence per Brian Shannon discipline."""
    fires = (
        s.get("above_prev_high", False)
        and s.get("vol_spike_15x", False)
        and s.get("htf_aligned_bull", False)
    )
    return _strat(fires, "long", "multi_timeframe",
        ["above_prev_high", "vol_spike_1.5x", "htf_aligned_bull"],
        ["Price broke above previous day's high",
         "Volume 1.5x ADV(20) - institutional participation",
         "Weekly + Monthly bias both bullish - HTF aligned"])


def strat_htf_aligned_breakout_short(s):
    """Batch 217: Symmetric short on prev-day low break + HTF bearish."""
    fires = (
        s.get("below_prev_low", False)
        and s.get("vol_spike_15x", False)
        and s.get("htf_aligned_bear", False)
    )
    return _strat(fires, "short", "multi_timeframe",
        ["below_prev_low", "vol_spike_1.5x", "htf_aligned_bear"],
        ["Price broke below previous day's low",
         "Volume 1.5x ADV(20) - institutional participation",
         "Weekly + Monthly bias both bearish - HTF aligned"])


def strat_weekly_bias_pullback_long(s):
    """Batch 217: Weekly bull bias + daily pullback (RSI(14)<40) +
    bullish reversal candle = high-quality long. Trades WITH the weekly
    trend after a daily oversold pullback."""
    fires = (
        s.get("weekly_bias_bull", False)
        and s.get("rsi_14", 50) < 40
        and (s.get("hammer") or s.get("bullish_engulfing"))
    )
    return _strat(fires, "long", "multi_timeframe",
        ["weekly_bias_bull", "rsi_14<40", "bullish_reversal_candle"],
        ["Weekly bias bullish - trade WITH weekly trend",
         "Daily RSI<40 - oversold pullback",
         "Bullish reversal candle (hammer or engulfing)"])


def strat_weekly_bias_pullback_short(s):
    """Batch 217: Symmetric weekly bear bias + daily rally pullback."""
    fires = (
        s.get("weekly_bias_bear", False)
        and s.get("rsi_14", 50) > 60
        and (s.get("shooting_star") or s.get("bearish_engulfing"))
    )
    return _strat(fires, "short", "multi_timeframe",
        ["weekly_bias_bear", "rsi_14>60", "bearish_reversal_candle"],
        ["Weekly bias bearish - trade WITH weekly trend",
         "Daily RSI>60 - overbought rally",
         "Bearish reversal candle (shooting star or engulfing)"])


def strat_monthly_bias_momentum_long(s):
    """Batch 217: Monthly bull bias + positive 6-month momentum + daily
    breakout = swing-trade long with structural multi-TF backing."""
    fires = (
        s.get("monthly_bias_bull", False)
        and s.get("monthly_momentum_pos", False)
        and s.get("above_prev_high", False)
    )
    return _strat(fires, "long", "multi_timeframe",
        ["monthly_bias_bull", "monthly_momentum_pos", "above_prev_high"],
        ["Monthly bias bullish + positive 6-month momentum",
         "Daily breakout above previous high",
         "Triple-TF structural confluence"])


def strat_smc_fvg_retest_long(s):
    """Batch 216 (SMC expansion 2026-05-18 owner-approved): price returned
    to an unmitigated bullish Fair Value Gap zone -> long entry.
    FVG = institutional 3-bar imbalance; retests of bullish FVGs are
    canonical ICT continuation entries."""
    fires = (
        s.get("smc_fvg_retest_long_zone", False)
        and s.get("price_above_ema_200", True)
    )
    return _strat(fires, "long", "smc",
        ["smc_fvg_retest_long_zone", "price_above_ema_200"],
        ["Price inside unmitigated bullish Fair Value Gap zone",
         "Above 200 EMA (regime gate)"])


def strat_smc_fvg_retest_short(s):
    """Batch 216: bearish FVG retest -> short entry. Symmetric to long."""
    fires = (
        s.get("smc_fvg_retest_short_zone", False)
        and (not s.get("price_above_ema_200", True))
    )
    return _strat(fires, "short", "smc",
        ["smc_fvg_retest_short_zone", "price_below_ema_200"],
        ["Price inside unmitigated bearish Fair Value Gap zone",
         "Below 200 EMA (bear regime)"])


def strat_smc_inverse_fvg(s):
    """Batch 216: Inverse FVG - bullish FVG was invalidated (price closed
    below) -> the zone flips role and acts as resistance (short).
    Symmetric for bearish FVG invalidated upward (long).
    ICT 'IFVG' concept: a failed institutional imbalance becomes the new
    opposing reference."""
    fl = s.get("smc_inverse_fvg_bullish", False)
    fs = s.get("smc_inverse_fvg_bearish", False)
    return _strat3(fl, fs, "smc",
        ["smc_inverse_fvg_bullish"],
        ["smc_inverse_fvg_bearish"],
        ["Inverse FVG (bearish FVG broken upward) - role flips to support"],
        ["Inverse FVG (bullish FVG broken downward) - role flips to resistance"])


def strat_smc_breaker_block_short(s):
    """Batch 216: Breaker block short - bullish OB that was mitigated +
    price now below bottom -> the OB flips role and becomes resistance.
    Classic ICT 'breaker block' reversal setup."""
    fires = (
        s.get("smc_breaker_block_bearish", False)
        and (not s.get("price_above_ema_200", True))
    )
    return _strat(fires, "short", "smc",
        ["smc_breaker_block_bearish", "price_below_ema_200"],
        ["Bullish Order Block mitigated + price below - role flipped to resistance",
         "Below 200 EMA (bear regime)"])


def strat_smc_breaker_block_long(s):
    """Batch 216: Breaker block long - bearish OB that was mitigated +
    price now above top -> flips to support."""
    fires = (
        s.get("smc_breaker_block_bullish", False)
        and s.get("price_above_ema_200", True)
    )
    return _strat(fires, "long", "smc",
        ["smc_breaker_block_bullish", "price_above_ema_200"],
        ["Bearish Order Block mitigated + price above - role flipped to support",
         "Above 200 EMA (regime gate)"])


def strat_smc_mitigation_block_long(s):
    """Batch 216: Price entering an UN-mitigated bullish Order Block
    zone - the institutional zone is being mitigated NOW. Lower-risk
    entry than waiting for the OB to fully play out; pairs naturally
    with subsequent CHoCH/BOS confirmation."""
    fires = (
        s.get("smc_mitigation_block_long", False)
        and s.get("price_above_ema_200", True)
        and s.get("rsi_14", 50) < 50
    )
    return _strat(fires, "long", "smc",
        ["smc_mitigation_block_long", "price_above_ema_200", "rsi_14<50"],
        ["Price inside bullish Order Block zone - mitigation underway",
         "Above 200 EMA (regime gate)",
         "RSI pullback context (not overbought)"])


def strat_smc_mitigation_block_short(s):
    """Batch 216: Symmetric mitigation block short."""
    fires = (
        s.get("smc_mitigation_block_short", False)
        and (not s.get("price_above_ema_200", True))
        and s.get("rsi_14", 50) > 50
    )
    return _strat(fires, "short", "smc",
        ["smc_mitigation_block_short", "price_below_ema_200", "rsi_14>50"],
        ["Price inside bearish Order Block zone - mitigation underway",
         "Below 200 EMA (bear regime)",
         "RSI rally context (not oversold)"])


def strat_smc_discount_long(s):
    """Batch 216: Premium/Discount filter - long only when price is in
    DISCOUNT zone (below 50% of recent dealing range) AND there is
    bullish structure (BOS bullish OR CHoCH bullish). ICT discipline:
    'buy low, sell high' inside the dealing range. Mitigates against
    chasing tops in an uptrend."""
    fires = (
        s.get("smc_in_discount_zone", False)
        and (s.get("smc_bos_bullish", False) or s.get("smc_choch_bullish", False))
        and s.get("price_above_ema_200", True)
    )
    pct = s.get("smc_dealing_range_pct", 0.5)
    return _strat(fires, "long", "smc",
        ["smc_in_discount_zone", "smc_bos_or_choch_bullish", "price_above_ema_200"],
        [f"Price at {pct*100:.0f}% of dealing range - discount zone",
         "Bullish BOS or CHoCH - structural support",
         "Above 200 EMA (regime gate)"])


def strat_smc_premium_short(s):
    """Batch 216: Premium short - symmetric inverse of discount long.
    Price in top 50% of dealing range + bearish structure."""
    fires = (
        s.get("smc_in_premium_zone", False)
        and (s.get("smc_bos_bearish", False) or s.get("smc_choch_bearish", False))
        and (not s.get("price_above_ema_200", True))
    )
    pct = s.get("smc_dealing_range_pct", 0.5)
    return _strat(fires, "short", "smc",
        ["smc_in_premium_zone", "smc_bos_or_choch_bearish", "price_below_ema_200"],
        [f"Price at {pct*100:.0f}% of dealing range - premium zone",
         "Bearish BOS or CHoCH - structural resistance",
         "Below 200 EMA (bear regime)"])


def strat_smc_ote_long(s):
    """Batch 216: Optimal Trade Entry long - Fibonacci 62-79%
    retracement zone after bullish CHoCH/BOS. ICT canonical 'sweet
    spot' for high-conviction trend continuation entries."""
    fires = (
        s.get("smc_ote_long_zone", False)
        and (s.get("smc_bos_bullish", False) or s.get("smc_choch_bullish", False))
    )
    pct = s.get("smc_retracement_pct", 0.0)
    return _strat(fires, "long", "smc",
        ["smc_ote_long_zone", "smc_bos_or_choch_bullish"],
        [f"OTE zone: {pct:.0f}% retracement (62-79% Fib)",
         "Bullish BOS/CHoCH - structural backdrop"])


def strat_smc_ote_short(s):
    """Batch 216: Symmetric OTE short."""
    fires = (
        s.get("smc_ote_short_zone", False)
        and (s.get("smc_bos_bearish", False) or s.get("smc_choch_bearish", False))
    )
    pct = s.get("smc_retracement_pct", 0.0)
    return _strat(fires, "short", "smc",
        ["smc_ote_short_zone", "smc_bos_or_choch_bearish"],
        [f"OTE zone: {pct:.0f}% retracement (62-79% Fib)",
         "Bearish BOS/CHoCH - structural backdrop"])


def strat_smc_equal_highs_sweep_short(s):
    """Batch 216: Equal-highs cluster swept (taking out stops above
    cluster) + bearish FVG below = high-conviction reversal short.
    Classic ICT stop-hunt-then-reverse pattern."""
    fires = (
        s.get("smc_equal_highs_swept", False)
        and s.get("smc_fvg_bearish_active", False)
    )
    return _strat(fires, "short", "smc",
        ["smc_equal_highs_swept", "smc_fvg_bearish_active"],
        ["Equal-highs cluster swept - buy-side liquidity taken",
         "Bearish FVG active below - reversal confluence"])


def strat_smc_equal_lows_sweep_long(s):
    """Batch 216: Equal-lows cluster swept + bullish FVG above =
    high-conviction reversal long."""
    fires = (
        s.get("smc_equal_lows_swept", False)
        and s.get("smc_fvg_bullish_active", False)
    )
    return _strat(fires, "long", "smc",
        ["smc_equal_lows_swept", "smc_fvg_bullish_active"],
        ["Equal-lows cluster swept - sell-side liquidity taken",
         "Bullish FVG active above - reversal confluence"])


def strat_smc_bos_retest_entry(s):
    """Batch 216: BOS retest - price returns to within 0.5pct of a
    recently-broken structure level. Empirically higher hit rate than
    naive BOS continuation per ICT discipline (allow the broken level
    to confirm-as-support before adding risk)."""
    fl = (
        s.get("smc_bos_retest_long", False)
        and s.get("price_above_ema_200", True)
    )
    fs = (
        s.get("smc_bos_retest_short", False)
        and (not s.get("price_above_ema_200", True))
    )
    return _strat3(fl, fs, "smc",
        ["smc_bos_retest_long", "price_above_ema_200"],
        ["smc_bos_retest_short", "price_below_ema_200"],
        ["Price retesting broken structure level (BOS bullish)",
         "Above 200 EMA (regime gate)"],
        ["Price retesting broken structure level (BOS bearish)",
         "Below 200 EMA (bear regime)"])


def strat_smc_bos_continuation(s):
    """Batch 210 (SMC/ICT family 2026-05-17 owner-approved research review).
    Break of Structure continuation: market makes a new structural high
    (BOS up) after a CHoCH; trend-continuation entry. Quantum Algo Mar
    2026 backtest: combined SMC stack achieved 61% WR / 2.17 PF / +2.27R
    average on 2,600 trades over 26 months.
    """
    fl = (
        s.get("smc_bos_bullish", False)
        and s.get("price_above_ema_200", True)
    )
    fs = (
        s.get("smc_bos_bearish", False)
        and (not s.get("price_above_ema_200", True))
    )
    return _strat3(fl, fs, "smc",
        ["smc_bos_bullish", "price_above_ema_200"],
        ["smc_bos_bearish", "price_below_ema_200"],
        ["Break of Structure (continuation) up - new structural high",
         "Above 200 EMA (regime gate)"],
        ["Break of Structure (continuation) down - new structural low",
         "Below 200 EMA (bear regime)"])


def strat_smc_choch_reversal(s):
    """Batch 210: Change of Character reversal. CHoCH marks the FIRST
    structural shift opposing the prior trend; high-conviction reversal
    setup per ICT/SMC discipline. Pairs with FVG-aligned entry."""
    fl = (
        s.get("smc_choch_bullish", False)
        and s.get("smc_fvg_bullish_active", False)
    )
    fs = (
        s.get("smc_choch_bearish", False)
        and s.get("smc_fvg_bearish_active", False)
    )
    return _strat3(fl, fs, "smc",
        ["smc_choch_bullish", "smc_fvg_bullish_active"],
        ["smc_choch_bearish", "smc_fvg_bearish_active"],
        ["Change of Character bullish (reversal)",
         "Bullish Fair Value Gap active - confluence"],
        ["Change of Character bearish (reversal)",
         "Bearish Fair Value Gap active - confluence"])


def strat_smc_order_block_bounce(s):
    """Batch 210: Order block bounce. Bullish OB = last opposing
    (bearish) candle before an impulse up; price returning to this zone
    acts as institutional support. Symmetric for bearish OB."""
    fl = (
        s.get("smc_ob_bullish_active", False)
        and s.get("rsi_14", 50) < 45  # pullback context
        and s.get("price_above_ema_200", True)
    )
    fs = (
        s.get("smc_ob_bearish_active", False)
        and s.get("rsi_14", 50) > 55
        and (not s.get("price_above_ema_200", True))
    )
    return _strat3(fl, fs, "smc",
        ["smc_ob_bullish_active", "rsi_14<45", "price_above_ema_200"],
        ["smc_ob_bearish_active", "rsi_14>55", "price_below_ema_200"],
        ["Bullish Order Block active - institutional support zone",
         "RSI pullback context", "Above 200 EMA"],
        ["Bearish Order Block active - institutional resistance zone",
         "RSI rally context", "Below 200 EMA"])


def strat_smc_liquidity_sweep_reversal(s):
    """Batch 210: Liquidity sweep reversal. Price sweeps a cluster of
    equal highs/lows (taking out stops), then reverses. Classic ICT
    'stop hunt' pattern. Pairs with CHoCH for additional reversal
    confirmation."""
    fl = (
        s.get("smc_liquidity_swept_dn", False)  # lows swept -> bullish reversal
        and (s.get("smc_choch_bullish", False) or s.get("smc_bos_bullish", False))
    )
    fs = (
        s.get("smc_liquidity_swept_up", False)
        and (s.get("smc_choch_bearish", False) or s.get("smc_bos_bearish", False))
    )
    return _strat3(fl, fs, "smc",
        ["smc_liquidity_swept_dn", "smc_choch_or_bos_bullish"],
        ["smc_liquidity_swept_up", "smc_choch_or_bos_bearish"],
        ["Liquidity sweep down (stops taken below low cluster)",
         "Followed by bullish CHoCH/BOS - reversal confirmed"],
        ["Liquidity sweep up (stops taken above high cluster)",
         "Followed by bearish CHoCH/BOS - reversal confirmed"])


def strat_pead_long(s):
    """Batch 209 (PEAD module 2026-05-17 owner-approved research review).
    Post-Earnings Announcement Drift long entry per Bernard-Thomas (1989)
    *Journal of Accounting Research* + Garfinkel-Hribar-Hsiao (2024)
    update. Strong positive earnings surprise + YoY growth -> 60 trading
    days of price drift continuation.

    Long: within 60d of last earnings filing AND positive YoY EPS growth
    AND positive announcement-day return (>+2%).
    """
    fires = (
        s.get("within_pead_window", False)
        and s.get("pead_positive_surprise", False)
    )
    yoy = s.get("earnings_eps_yoy_growth", 0.0)
    ann = s.get("earnings_announcement_return", 0.0)
    return _strat(fires, "long", "event_driven",
        ["within_pead_window", "pead_positive_surprise",
         "earnings_eps_yoy_growth>0", "announcement_return>+2pct"],
        [f"Within PEAD drift window (<=60d post-earnings)",
         f"YoY EPS growth: {yoy*100:.1f}%",
         f"Announcement-day return: {ann*100:.1f}% (>+2% surprise threshold)",
         "Bernard-Thomas (1989) 60-day drift continuation"])


def strat_pead_short(s):
    """Batch 209: PEAD short - symmetric for negative-surprise drift.
    Documented effect: bottom-decile-surprise stocks underperform for
    same 60-day window (Garfinkel et al. 2024)."""
    fires = (
        s.get("within_pead_window", False)
        and s.get("pead_negative_surprise", False)
    )
    yoy = s.get("earnings_eps_yoy_growth", 0.0)
    ann = s.get("earnings_announcement_return", 0.0)
    return _strat(fires, "short", "event_driven",
        ["within_pead_window", "pead_negative_surprise",
         "earnings_eps_yoy_growth<0", "announcement_return<-2pct"],
        [f"Within PEAD drift window (<=60d post-earnings)",
         f"YoY EPS growth: {yoy*100:.1f}% (negative)",
         f"Announcement-day return: {ann*100:.1f}% (<-2% surprise)",
         "Bernard-Thomas 60-day drift continuation (negative)"])


def strat_avwap_252_breakout(s):
    """Batch 208 (new strategy family 2026-05-17 owner-approved research review).
    Anchored VWAP from 252-day swing low breakout. Brian Shannon (2022)
    Maximum Trading Gains With Anchored VWAP, CMT Association whitepaper.

    Long: price reclaims AVWAP-252-low (was below, now above) + volume
    confirms + RSI not extreme-overbought. Marks an institutional-level
    inflection - the year's accumulation-distribution reference.

    Short: price loses AVWAP-252-low to the downside + volume confirms.
    Symmetric inverse for distribution / breakdown days.
    """
    above_252 = s.get("above_avwap_252low", False)
    pct_from_252 = s.get("pct_from_avwap_252low", 0.0)
    vol_ok = s.get("vol_spike_15x", False)
    rsi_14 = s.get("rsi_14", 50)
    # Long: just reclaimed (close to AVWAP but above) + volume + RSI not capped
    fl = (
        above_252
        and abs(pct_from_252) < 2.0   # within 2% of AVWAP (close to inflection)
        and vol_ok
        and rsi_14 < 70
    )
    # Short: just lost (close below AVWAP) + volume + RSI not capped
    fs = (
        (not above_252)
        and abs(pct_from_252) < 2.0
        and vol_ok
        and rsi_14 > 30
    )
    return _strat3(fl, fs, "vwap",
        ["above_avwap_252low", "near_avwap_252low<2pct", "vol_spike_1.5x", "rsi_14<70"],
        ["below_avwap_252low", "near_avwap_252low<2pct", "vol_spike_1.5x", "rsi_14>30"],
        ["Price reclaimed Anchored VWAP from 252d low - institutional accumulation",
         "Close to AVWAP inflection (within 2%)", "Volume 1.5x ADV(20)",
         "RSI not extreme overbought"],
        ["Price lost Anchored VWAP from 252d low - distribution",
         "Close to AVWAP inflection (within 2%)", "Volume 1.5x ADV(20)",
         "RSI not extreme oversold"])


def strat_avwap_50_reclaim(s):
    """Batch 208: AVWAP-50-low reclaim with confirming momentum. Higher-
    frequency variant of the 252-low strategy targeting recent-leg
    reclaims rather than annual-reference inflections. Pairs naturally
    with the 50-day momentum window."""
    above_50 = s.get("above_avwap_50low", False)
    pct_from_50 = s.get("pct_from_avwap_50low", 0.0)
    macd_bull = s.get("macd_12_26_9_bullish", False)
    # Long: just reclaimed AVWAP-50 + MACD turning bullish
    fl = (
        above_50
        and abs(pct_from_50) < 1.5
        and macd_bull
        and s.get("price_above_ema_200", True)  # require uptrend regime
    )
    # Short: just lost AVWAP-50 + MACD turning bearish
    fs = (
        (not above_50)
        and abs(pct_from_50) < 1.5
        and (not macd_bull)
        and (not s.get("price_above_ema_200", True))
    )
    return _strat3(fl, fs, "vwap",
        ["above_avwap_50low", "near_avwap_50low<1.5pct", "macd_bullish",
         "price_above_ema_200"],
        ["below_avwap_50low", "near_avwap_50low<1.5pct", "macd_bearish",
         "price_below_ema_200"],
        ["Price reclaimed Anchored VWAP from 50d low - recent leg accumulation",
         "Within 1.5% of AVWAP inflection", "MACD bullish",
         "Above 200 EMA (regime gate)"],
        ["Price lost Anchored VWAP from 50d low - recent leg distribution",
         "Within 1.5% of AVWAP inflection", "MACD bearish",
         "Below 200 EMA (bear regime)"])


def strat_avwap_20high_rejection_short(s):
    """Batch 208: short-side rejection at AVWAP from 20-day swing high.
    Recent high acts as resistance; price tests then rejects with
    bearish candle + volume. Designed to fire in neutral/bear regime
    (high-quality short setup per Anchored VWAP discipline)."""
    pct_from_20h = s.get("pct_from_avwap_20high", 0.0)
    fires = (
        not s.get("above_avwap_20high", True)  # below 20-high AVWAP
        and abs(pct_from_20h) < 1.0
        and (s.get("shooting_star") or s.get("bearish_engulfing"))
        and s.get("vol_spike_15x", False)
        and (not s.get("price_above_ema_200", True))
    )
    return _strat(fires, "short", "vwap",
        ["below_avwap_20high", "near_avwap_20high<1pct",
         "shooting_star_or_bearish_engulfing", "vol_spike_1.5x",
         "price_below_ema_200"],
        ["Price tested Anchored VWAP from 20d high and rejected",
         "Within 1% of AVWAP inflection",
         "Bearish reversal candle confirms sellers",
         "Volume 1.5x ADV(20)",
         "Below 200 EMA (bear regime confirmation)"])


ALL_STRATEGIES = {
    # ORB stocks-in-play (2 - Batch 211 2026-05-17 owner-approved research review)
    "orb_stocks_in_play_long":      strat_orb_stocks_in_play_long,
    "orb_stocks_in_play_short":     strat_orb_stocks_in_play_short,
    # SMC / ICT family (4 - Batch 210 2026-05-17 owner-approved research review)
    "smc_bos_continuation":         strat_smc_bos_continuation,
    "smc_choch_reversal":           strat_smc_choch_reversal,
    "smc_order_block_bounce":       strat_smc_order_block_bounce,
    "smc_liquidity_sweep_reversal": strat_smc_liquidity_sweep_reversal,
    # PO3 + multi-TF (9 - Batch 217 2026-05-18 owner-approved)
    "po3_bullish":                  strat_po3_bullish,
    "po3_bearish":                  strat_po3_bearish,
    "po3_htf_aligned_long":         strat_po3_htf_aligned_long,
    "po3_htf_aligned_short":        strat_po3_htf_aligned_short,
    "htf_aligned_breakout_long":    strat_htf_aligned_breakout_long,
    "htf_aligned_breakout_short":   strat_htf_aligned_breakout_short,
    "weekly_bias_pullback_long":    strat_weekly_bias_pullback_long,
    "weekly_bias_pullback_short":   strat_weekly_bias_pullback_short,
    "monthly_bias_momentum_long":   strat_monthly_bias_momentum_long,
    # SMC / ICT expansion (13 - Batch 216 2026-05-18 owner-approved)
    "smc_fvg_retest_long":          strat_smc_fvg_retest_long,
    "smc_fvg_retest_short":         strat_smc_fvg_retest_short,
    "smc_inverse_fvg":              strat_smc_inverse_fvg,
    "smc_breaker_block_short":      strat_smc_breaker_block_short,
    "smc_breaker_block_long":       strat_smc_breaker_block_long,
    "smc_mitigation_block_long":    strat_smc_mitigation_block_long,
    "smc_mitigation_block_short":   strat_smc_mitigation_block_short,
    "smc_discount_long":            strat_smc_discount_long,
    "smc_premium_short":            strat_smc_premium_short,
    "smc_ote_long":                 strat_smc_ote_long,
    "smc_ote_short":                strat_smc_ote_short,
    "smc_equal_highs_sweep_short":  strat_smc_equal_highs_sweep_short,
    "smc_equal_lows_sweep_long":    strat_smc_equal_lows_sweep_long,
    "smc_bos_retest_entry":         strat_smc_bos_retest_entry,
    # PEAD family (2 - Batch 209 2026-05-17 owner-approved research review)
    "pead_long":                    strat_pead_long,
    "pead_short":                   strat_pead_short,
    # Anchored VWAP family (3 - Batch 208 2026-05-17 owner-approved research review)
    "avwap_252_breakout":           strat_avwap_252_breakout,
    "avwap_50_reclaim":             strat_avwap_50_reclaim,
    "avwap_20high_rejection_short": strat_avwap_20high_rejection_short,
    # Pivot (10)
    "pivot_s1_bounce":          strat_pivot_s1_bounce,
    "pivot_s2_bounce":          strat_pivot_s2_bounce,
    "pivot_s3_capitulation":    strat_pivot_s3_capitulation,
    "pivot_r1_breakout":        strat_pivot_r1_breakout,
    "pivot_r2_continuation":    strat_pivot_r2_continuation,
    "cpr_narrow_bullish":       strat_cpr_narrow_bullish,
    "camarilla_s3_bounce":      strat_camarilla_s3_bounce,
    "camarilla_r3_breakout":    strat_camarilla_r3_breakout,
    "prev_day_high_break":      strat_prev_day_high_break,
    "prev_day_low_bounce":      strat_prev_day_low_bounce,
    # Momentum (9)
    "macd_crossover":           strat_macd_crossover,
    "macd_fast_crossover":      strat_macd_fast_crossover,
    "hull_rsi":                 strat_hull_rsi,
    "williams_r_oversold":      strat_williams_r_oversold,
    "roc_burst":                strat_roc_burst,
    "awesome_oscillator":       strat_awesome_oscillator,
    "stochrsi_oversold":        strat_stochrsi_oversold,
    "ppo_crossover":            strat_ppo_crossover,
    "ultimate_oscillator":      strat_ultimate_oscillator,
    # Trend (9)
    "golden_cross_50_200":      strat_golden_cross_50_200,
    "golden_cross_9_21":        strat_golden_cross_9_21,
    "golden_cross_20_50":       strat_golden_cross_20_50,
    "parabolic_sar_flip":       strat_parabolic_sar_flip,
    "tema_dema":                strat_tema_dema,
    "ichimoku_tk_cross":        strat_ichimoku_tk_cross,
    "ichimoku_cloud_breakout":  strat_ichimoku_cloud_breakout,
    "adx_initiation":           strat_adx_initiation,
    "supertrend_macd":          strat_supertrend_macd,
    # Mean Reversion (11)
    "rsi_oversold":             strat_rsi_oversold,
    "rsi9_extreme":             strat_rsi9_extreme,
    "rsi21_slow":               strat_rsi21_slow,
    "rsi_overbought_short":     strat_rsi_overbought_short,
    "mfi_oversold":             strat_mfi_oversold,
    "cmf_flip":                 strat_cmf_flip,
    "bollinger_lower":          strat_bollinger_lower,
    "bollinger_tight":          strat_bollinger_tight,
    "bollinger_upper_short":    strat_bollinger_upper_short,
    "keltner_lower":            strat_keltner_lower,
    "stoch_oversold":           strat_stoch_oversold,
    # Breakout (6)
    "squeeze_breakout":         strat_squeeze_breakout,
    "volume_spike_breakout":    strat_volume_spike_breakout,
    "52w_high_breakout":        strat_52w_high_breakout,
    "inside_bar_breakout":      strat_inside_bar_breakout,
    "force_index_breakout":     strat_force_index_breakout,
    "donchian_10_breakout":     strat_donchian_10_breakout,
    # Candle (6)
    "morning_star":             strat_morning_star,
    "bullish_engulfing_support": strat_bullish_engulfing_support,
    "doji_at_support":          strat_doji_at_support,
    "three_white_soldiers":     strat_three_white_soldiers,
    "shooting_star_short":      strat_shooting_star_short,
    "evening_star_short":       strat_evening_star_short,
    # Confluence (9)
    "rsi_volume_200ema":        strat_rsi_volume_200ema,
    "macd_ichimoku":            strat_macd_ichimoku,
    "bb_squeeze_volume":        strat_bb_squeeze_volume,
    "pivot_fib_confluence":     strat_pivot_fib_confluence,
    "golden_cross_volume":      strat_golden_cross_volume,
    "cpr_narrow_momentum":      strat_cpr_narrow_momentum,
    "camarilla_rsi_obv":        strat_camarilla_rsi_obv,
    "supertrend_ichimoku_adx":  strat_supertrend_ichimoku_adx,
    "williams_stoch_dual":      strat_williams_stoch_dual,
    # Dedicated shorts  -  Trend (4)
    "death_cross_50_200_volume":    strat_death_cross_50_200_volume,
    "supertrend_macd_short":        strat_supertrend_macd_short,
    "ichimoku_cloud_breakdown":     strat_ichimoku_cloud_breakdown,
    "parabolic_sar_flip_short":     strat_parabolic_sar_flip_short,
    # Dedicated shorts  -  Momentum (3)
    "macd_crossover_short":         strat_macd_crossover_short,
    "hull_rsi_short":               strat_hull_rsi_short,
    "stochrsi_overbought_short":    strat_stochrsi_overbought_short,
    # Dedicated shorts  -  Breakdown (3)
    "donchian_breakdown_short":     strat_donchian_breakdown_short,
    "52w_low_breakdown":            strat_52w_low_breakdown,
    "prev_day_low_breakdown":       strat_prev_day_low_breakdown,
    # Dedicated shorts  -  Confluence (2)
    "camarilla_rsi_obv_short":      strat_camarilla_rsi_obv_short,
    "cpr_narrow_momentum_short":    strat_cpr_narrow_momentum_short,
    # Break-and-Retest (5)  -  BUG-111 / DEC-355 through DEC-362 chart pattern spec
    "dc20_break_retest":            strat_dc20_break_retest,
    "r1_break_retest":              strat_r1_break_retest,
    "52wh_break_retest":            strat_52wh_break_retest,
    "break_retest_volume":          strat_break_retest_volume,
    "break_retest_confluence":      strat_break_retest_confluence,
}

STRATEGY_CATEGORIES = {
    name: fn({}).__class__  # placeholder  -  category stored in each fn
    for name, fn in ALL_STRATEGIES.items()
}


# -----------------------------------------------------------------------------
# ENTRY ZONE VALIDATOR
# -----------------------------------------------------------------------------

def validate_entry_zone(
    open_price: float,
    signal_close: float,
    atr: float,
    category: str,
    direction: str,
) -> tuple[bool, str]:
    """Check if the next-day open is within the acceptable entry zone.

    Returns (valid: bool, reason: str).

    BUG-060 fix 2026-05-13: for short entries, only ADVERSE gap-ups are rejected.
    A gap-down on a short is FAVORABLE (lower entry = more downside room) and must
    NOT be filtered out. Previous code incorrectly applied gap_down > mult*ATR as a
    short-entry rejection, understating short strategy performance. Correct logic:
    - Long  entry: reject excessive gap-UP   (adverse: entered above signal level)
    - Short entry: reject excessive gap-UP   (adverse: stock moved against the short)
    - Long  entry: gap-down is acceptable    (favorable: better long entry price)
    - Short entry: gap-down is acceptable    (favorable: lower short entry price)
    """
    from backtest.config import ENTRY_GAP_ATR_MULT
    mult    = ENTRY_GAP_ATR_MULT.get(category, 1.5)
    gap_atr = (open_price - signal_close) / atr if atr > 0 else 0
    gap_pct = (open_price - signal_close) / signal_close * 100 if signal_close > 0 else 0

    if direction == "long":
        # Reject excessive gap-UP for longs (opened too far above signal close)
        if gap_atr > mult:
            return False, f"gap_up_{gap_pct:.1f}pct_exceeds_{mult}x_atr_limit"
        return True, f"entry_valid_gap_{gap_pct:.1f}pct"
    else:  # short
        # BUG-060: reject only adverse gap-UPs for shorts; gap-downs are favorable
        if gap_atr > mult:
            return False, f"short_adverse_gap_up_{gap_pct:.1f}pct_exceeds_{mult}x_atr_limit"
        return True, f"entry_valid_gap_{gap_pct:.1f}pct"


# -----------------------------------------------------------------------------
# SCREENING PIPELINE
# -----------------------------------------------------------------------------

def screen_lead_lag_sector(
    ohlcv_dict: dict,
    info_dict: dict,
    as_of: date,
) -> list:
    """DEC-458: Lead-lag intra-sector momentum cross-ticker candidates.

    Groups tickers by GICS sector, ranks by 5-day momentum (LEAD_LAG_INTRA_SECTOR_STRATEGY
    spec from config.py). For sectors with >=4 members: fires long on the bottom 2-3
    laggards (mean-reversion rotation toward sector leader).
    ETF-proxy sectors excluded so rotation targets are individual equities only.
    """
    from backtest.config import LEAD_LAG_INTRA_SECTOR_STRATEGY, ATR_FALLBACK_PCT
    lookback = LEAD_LAG_INTRA_SECTOR_STRATEGY["lookback_days"]

    ETF_SECTORS = {
        "Broad Market", "Volatility", "Fixed Income",
        "Commodities", "Emerging Markets", "International", "Small Cap",
    }

    sector_members: dict[str, list] = {}
    for ticker, df in ohlcv_dict.items():
        if df is None or len(df) < lookback + 2:
            continue
        info = info_dict.get(ticker, {})
        sector = info.get("sector") or info.get("Sector") or "Unknown"
        if sector in ETF_SECTORS or sector == "Unknown":
            continue
        try:
            close_now  = float(df["close"].iloc[-1])
            close_back = float(df["close"].iloc[-(lookback + 1)])
            momentum   = (close_now - close_back) / close_back if close_back > 0 else 0.0
        except (IndexError, ValueError, ZeroDivisionError):
            continue
        sector_members.setdefault(sector, []).append(
            {"ticker": ticker, "df": df, "momentum": momentum}
        )

    candidates = []
    for sector, members in sector_members.items():
        if len(members) < 4:
            continue
        members.sort(key=lambda x: x["momentum"], reverse=True)
        leader   = members[0]
        n        = len(members)
        lag_count = 3 if n >= 5 else 2
        laggards  = members[n - lag_count:]

        for rank_from_bottom, lag in enumerate(reversed(laggards), 1):
            ticker = lag["ticker"]
            df_lag = lag["df"]
            close  = float(df_lag["close"].iloc[-1])
            try:
                atr = float(
                    (df_lag["high"] - df_lag["low"]).rolling(14).mean().iloc[-1]
                )
                if not (atr > 0):
                    atr = close * ATR_FALLBACK_PCT
            except Exception:
                atr = close * ATR_FALLBACK_PCT
            strat_entry = {
                "strategy":        "lead_lag_sector_rotation",
                "direction":       "long",
                "category":        "rotation",
                "signals_used":    ["sector_5d_momentum_rank", "intra_sector_lag"],
                "context_bullets": [
                    f"Sector {sector}: laggard rank {rank_from_bottom} of {n}",
                    f"5d return {lag['momentum']:.1%} vs leader {leader['ticker']} ({leader['momentum']:.1%})",
                    "Rotation signal: mean-reversion toward sector leader",
                ],
            }
            candidates.append({
                "ticker":             ticker,
                "as_of":              as_of,
                "liquidity_ok":       True,
                "fail_reason":        None,
                "strategies":         [strat_entry],
                "long_strategies":    [dict(strat_entry)],
                "short_strategies":   [],
                "avoid_strategies":   [],
                "strategy_count":     1,
                "long_count":         1,
                "short_count":        0,
                "avoid_count":        0,
                "tech_signal_count":  0,
                "signals":            {},
                "last_close":         round(close, 4),
                "atr":                round(atr, 4),
                "initial_stop_long":  round(close * 0.90, 4),
                "initial_stop_short": round(close * 1.10, 4),
            })
    return candidates


def screen_instrument(
    ticker: str,
    df: pd.DataFrame,
    info: dict,
    as_of: date,
    regime: str = "neutral",
    vix_value: float = None,
    vix_history: list = None,
) -> dict:
    """
    Run single instrument through full pipeline.
    Returns candidate dict with all strategies triggered, signals, and bullets.

    Batch 204 (Bollinger optimization 2026-05-17): optional VIX context
    kwargs flow through to compute_macro_overlays so regime-aware
    strategies (bollinger_*) can read vix_percentile/vix_band from the
    signals dict. When None, behavior is unchanged.
    """
    # Liquidity already checked at universe load time (annually)
    # Light check: price > 0 and sufficient history only
    if df is None or len(df) < 30:
        return {"ticker": ticker, "as_of": as_of, "liquidity_ok": False,
                "fail_reason": "insufficient_history", "strategies": []}

    signals = compute_all_signals(df)
    if not signals:
        return {"ticker": ticker, "as_of": as_of, "liquidity_ok": True,
                "fail_reason": "no_signals", "strategies": []}
    # Batch 204: layer macro overlays (VIX percentile + band) so strategies
    # can read regime-aware fields inline. No-op when vix_value/history None.
    if vix_value is not None and vix_history is not None:
        from backtest.signals.technical import compute_macro_overlays
        signals = compute_macro_overlays(signals, vix_value, vix_history)
    # Batch 209: PEAD signals (post-earnings drift). No-op when financials
    # prefetch missing for this ticker. Strategy gates inside strat_pead_*
    # check within_pead_window / pead_positive_surprise / etc.
    try:
        from backtest.signals.pead import compute_pead_signals
        pead = compute_pead_signals(ticker, df, as_of)
        if pead:
            signals.update(pead)
    except Exception:
        pass
    # Batch 210: SMC / ICT signals via vendored smartmoneyconcepts library.
    # Returns empty dict when library unavailable or insufficient history.
    try:
        from backtest.signals.smc_ict import compute_smc_signals
        smc_out = compute_smc_signals(df)
        if smc_out:
            signals.update(smc_out)
    except Exception:
        pass
    # Batch 217: PO3 daily candle + multi-TF (weekly/monthly bias) +
    # HTF alignment. Each helper returns empty dict on insufficient
    # data; merged in order so strategy gates can read po3_*,
    # weekly_*, monthly_*, htf_aligned_* keys.
    try:
        from backtest.signals.multi_timeframe import (
            compute_po3_signal,
            compute_weekly_bias,
            compute_monthly_bias,
            compute_htf_alignment,
        )
        po3 = compute_po3_signal(df)
        if po3:
            signals.update(po3)
        weekly = compute_weekly_bias(df)
        if weekly:
            signals.update(weekly)
        monthly = compute_monthly_bias(df)
        if monthly:
            signals.update(monthly)
        if weekly or monthly:
            signals.update(compute_htf_alignment(weekly, monthly))
    except Exception:
        pass

    triggered_long  = []
    triggered_short = []
    # BUG-77 RESOLVED-IMPLEMENTED Pass 53 v8h+1 Phase 3 Batch 19 2026-05-10
    # (owner-approved Option A): third bucket for avoid direction. Previously
    # the else branch merged avoid into triggered_short, inflating
    # strategy_count and distorting candidate ranking - a ticker with
    # mixed/conflicting signals could rank above one with strong directional
    # conviction. Source-side counterpart to BUG-04 (consumer-side filter
    # at backtest.py:410). avoid signals are kept in the candidate dict for
    # downstream diagnostics but excluded from all_triggered / strategy_count.
    triggered_avoid = []

    for name, fn in ALL_STRATEGIES.items():
        try:
            result = fn(signals)
            if not result["fires"]:
                continue
            direction = result["direction"]
            # Regime context  -  no hard direction blocks (buy-the-dip philosophy)
            # Crisis regime: long trades flagged, position size reduced in engine
            # Bull regime: short trades allowed but at reduced size
            entry = {
                "strategy":        name,
                "direction":       direction,
                "category":        result["category"],
                "signals_used":    result["signals_used"],
                "context_bullets": result["context_bullets"],
            }
            if direction == "long":
                triggered_long.append(entry)
            elif direction == "short":
                triggered_short.append(entry)
            else:  # avoid - BUG-77: do NOT inflate triggered_short
                triggered_avoid.append(entry)
        except Exception as exc:
            logger.debug("Strategy %s error for %s: %s", name, ticker, exc)

    all_triggered = triggered_long + triggered_short  # BUG-77: no avoid here
    tech_count    = count_bullish_signals(signals)
    atr           = signals.get("atr", 0.0)
    close         = float(df["close"].iloc[-1])

    return {
        "ticker":            ticker,
        "as_of":             as_of,
        "liquidity_ok":      True,
        "fail_reason":       None,
        "strategies":        all_triggered,
        "long_strategies":   triggered_long,
        "short_strategies":  triggered_short,
        "avoid_strategies":  triggered_avoid,  # BUG-77: kept for diagnostics
        "strategy_count":    len(all_triggered),
        "long_count":        len(triggered_long),
        "short_count":       len(triggered_short),
        "avoid_count":       len(triggered_avoid),
        "tech_signal_count": tech_count,
        "signals":           signals,
        "last_close":        round(close, 4),
        "atr":               atr,
        "initial_stop_long":  round(close * 0.90, 4),
        "initial_stop_short": round(close * 1.10, 4),
    }


def screen_universe(
    ohlcv_dict: dict,
    info_dict: dict,
    as_of: date,
    regime: str = "neutral",
    min_strategies: int = 1,
    vix_value: float = None,
    vix_history: list = None,
) -> list:
    """Screen all instruments. Returns candidates sorted by strategy count.

    Batch 204: optional VIX context kwargs flow through to each
    screen_instrument call so regime-aware strategies see the
    vix_percentile / vix_band overlays. Backward-compatible: when None,
    behavior is unchanged.
    """
    candidates = []
    for ticker, df in ohlcv_dict.items():
        info   = info_dict.get(ticker, {"ticker": ticker})
        result = screen_instrument(
            ticker, df, info, as_of, regime,
            vix_value=vix_value, vix_history=vix_history,
        )
        if result.get("liquidity_ok") and result.get("strategy_count", 0) >= min_strategies:
            candidates.append(result)
    # DEC-458: merge lead-lag cross-ticker candidates (sector rotation)
    lead_lag = screen_lead_lag_sector(ohlcv_dict, info_dict, as_of)
    existing_map = {c["ticker"]: c for c in candidates}
    for ll in lead_lag:
        t = ll["ticker"]
        if t in existing_map:
            existing_map[t]["strategies"].extend(ll["strategies"])
            existing_map[t]["long_strategies"].extend(ll["long_strategies"])
            existing_map[t]["strategy_count"] += 1
            existing_map[t]["long_count"] += 1
        else:
            candidates.append(ll)

    candidates.sort(key=lambda x: (x["strategy_count"], x["tech_signal_count"]), reverse=True)
    logger.info("screen_universe [%s] regime=%s: %d/%d passed (incl. %d lead-lag)",
                as_of, regime, len(candidates), len(ohlcv_dict), len(lead_lag))
    return candidates
