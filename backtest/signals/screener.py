"""
signals/screener.py — All 60 strategies with entry zone logic and regime filter.

60 strategies across 7 categories:
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


# ─────────────────────────────────────────────────────────────────────────────
# STRATEGY HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _strat(fires, direction, category, signals_used, context_bullets):
    return {
        "fires":           fires,
        "direction":       direction,
        "category":        category,
        "signals_used":    signals_used,
        "context_bullets": context_bullets,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY 1: PIVOT-BASED (10 strategies)
# ─────────────────────────────────────────────────────────────────────────────

def strat_pivot_s1_bounce(s):
    fires = (s.get("near_s1") and
             (s.get("hammer") or s.get("pin_bar")) and
             s.get("obv_bullish"))
    return _strat(fires, "long", "pivot",
        ["near_s1","hammer/pin_bar","obv_bullish"],
        ["Price at S1 pivot support",
         "Hammer or pin bar candle confirming buyers",
         "OBV rising — volume supports the bounce"])


def strat_pivot_s2_bounce(s):
    fires = (s.get("near_s2") and
             s.get("rsi_14", 50) < 40 and
             (s.get("hammer") or s.get("bullish_engulfing")))
    return _strat(fires, "long", "pivot",
        ["near_s2","rsi_14<40","bullish_candle"],
        ["Price at S2 deep support — stronger conviction level",
         f"RSI-14 oversold at {s.get('rsi_14',0):.1f}",
         "Bullish candle confirms buyers stepping in"])


def strat_pivot_s3_capitulation(s):
    fires = (s.get("near_s3") and
             s.get("rsi_14", 50) < 30 and
             s.get("vol_spike_2x"))
    return _strat(fires, "long", "pivot",
        ["near_s3","rsi_14<30","vol_spike_2x"],
        ["Price at S3 — extreme capitulation level",
         f"RSI-14 extremely oversold at {s.get('rsi_14',0):.1f}",
         "Volume spike confirms panic selling — reversal likely"])


def strat_pivot_r1_breakout(s):
    fires = (s.get("above_r1") and
             s.get("vol_spike_15x") and
             s.get("macd_12_26_9_bullish"))
    return _strat(fires, "long", "pivot",
        ["above_r1","vol_spike_1.5x","macd_bullish"],
        ["Price broke above R1 resistance",
         "Volume 1.5× average confirms institutional participation",
         "MACD histogram positive — momentum supporting breakout"])


def strat_pivot_r2_continuation(s):
    fires = (s.get("above_r2") and
             s.get("adx_trending") and
             s.get("ema_50_200_bullish"))
    return _strat(fires, "long", "pivot",
        ["above_r2","adx_trending","ema_50_200_bullish"],
        ["Price broke above R2 — strong trend continuation signal",
         f"ADX at {s.get('adx',0):.1f} confirms trend is real",
         "Above 50/200 EMA — macro trend structure intact"])


def strat_cpr_narrow_bullish(s):
    fires = (s.get("cpr_narrow") and
             s.get("above_cpr") and
             s.get("rsi_14", 50) > 50)
    return _strat(fires, "long", "pivot",
        ["cpr_narrow","above_cpr","rsi_14>50"],
        ["Narrow CPR — directional day likely",
         "Price opened and held above CPR — bullish daily bias",
         "RSI above 50 confirms upward momentum"])


def strat_camarilla_s3_bounce(s):
    fires = (s.get("near_cam_s3") and
             s.get("rsi_14", 50) < 35 and
             s.get("obv_bullish"))
    return _strat(fires, "long", "pivot",
        ["near_cam_s3","rsi_14<35","obv_bullish"],
        ["Price at Camarilla S3 — primary support level",
         f"RSI-14 oversold at {s.get('rsi_14',0):.1f}",
         "OBV confirms accumulation at this level"])


def strat_camarilla_r3_breakout(s):
    fires = (s.get("above_cam_r3") and
             s.get("vol_spike_2x"))
    return _strat(fires, "long", "pivot",
        ["above_cam_r3","vol_spike_2x"],
        ["Price broke above Camarilla R3 — breakout mode",
         "Volume 2× average confirms institutional buying",
         "Above R3 = momentum likely to continue to R4"])


def strat_prev_day_high_break(s):
    fires = (s.get("above_prev_high") and
             s.get("vol_spike_15x") and
             s.get("above_vwap"))
    return _strat(fires, "long", "pivot",
        ["above_prev_high","vol_spike_1.5x","above_vwap"],
        ["Price broke above previous day's high",
         "Volume 1.5× confirms participation",
         "Above VWAP — intraday buyers in control"])


def strat_prev_day_low_bounce(s):
    fires = (s.get("near_prev_low") and
             s.get("hammer") and
             s.get("cmf_positive"))
    return _strat(fires, "long", "pivot",
        ["near_prev_low","hammer","cmf_positive"],
        ["Price holding at previous day's low — key support",
         "Hammer candle — buyers defended the level",
         "CMF positive — money flow confirms accumulation"])


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY 2: MOMENTUM (9 strategies)
# ─────────────────────────────────────────────────────────────────────────────

def strat_macd_crossover(s):
    fires = s.get("macd_12_26_9_crossover_up")
    return _strat(fires, "long", "momentum",
        ["macd_12_26_9_crossover_up"],
        ["MACD 12/26/9 histogram crossed above zero",
         "Short-term momentum overtook long-term — trend shift",
         f"MACD histogram: {s.get('macd_12_26_9_hist',0):.4f}"])


def strat_macd_fast_crossover(s):
    fires = s.get("macd_8_21_5_crossover_up")
    return _strat(fires, "long", "momentum",
        ["macd_8_21_5_crossover_up"],
        ["Fast MACD 8/21/5 histogram crossed above zero",
         "Earlier momentum signal than standard MACD",
         f"Fast MACD histogram: {s.get('macd_8_21_5_hist',0):.4f}"])


def strat_hull_rsi(s):
    fires = (s.get("hull_bullish") and
             s.get("price_above_hull") and
             s.get("rsi_9", 50) > 50)
    return _strat(fires, "long", "momentum",
        ["hull_bullish","price_above_hull","rsi_9>50"],
        ["Hull MA rising — fast trend confirmed",
         "Price above Hull MA — momentum aligned",
         f"RSI-9 at {s.get('rsi_9',0):.1f} — above midpoint"])


def strat_williams_r_oversold(s):
    fires = (s.get("williams_r_oversold") and
             s.get("price_above_ema_200") and
             s.get("cmf_positive"))
    return _strat(fires, "long", "momentum",
        ["williams_r_oversold","price_above_ema_200","cmf_positive"],
        [f"Williams %R at {s.get('williams_r',0):.1f} — oversold below -80",
         "Price above 200 EMA — in overall uptrend",
         "CMF positive — money flow supporting recovery"])


def strat_roc_burst(s):
    fires = (s.get("roc_turning_up") and
             s.get("vol_spike_15x"))
    return _strat(fires, "long", "momentum",
        ["roc_turning_up","vol_spike_1.5x"],
        [f"ROC-12 flipped positive at {s.get('roc_12',0):.2f}%",
         "Rate of change turning up — early momentum shift",
         "Volume 1.5× confirms the move has participation"])


def strat_awesome_oscillator(s):
    fires = (s.get("ao_cross_up") and
             s.get("price_above_ema_20"))
    return _strat(fires, "long", "momentum",
        ["ao_cross_up","price_above_ema_20"],
        ["Awesome Oscillator crossed above zero",
         "Bill Williams momentum signal — market momentum turning positive",
         "Price above EMA-20 confirms uptrend context"])


def strat_stochrsi_oversold(s):
    fires = (s.get("stochrsi_oversold") and
             s.get("stochrsi_cross_up") and
             s.get("rsi_14", 50) < 55)
    return _strat(fires, "long", "momentum",
        ["stochrsi_oversold","stochrsi_cross_up","rsi_14<55"],
        [f"StochRSI at {s.get('stochrsi_k',0):.1f} — oversold below 20",
         "StochRSI K crossed above D — momentum turning",
         "RSI context confirms not already overbought"])


def strat_ppo_crossover(s):
    fires = (s.get("ppo_crossover_up") and
             s.get("adx_trending"))
    return _strat(fires, "long", "momentum",
        ["ppo_crossover_up","adx_trending"],
        ["PPO crossed above signal line — percentage-normalised MACD",
         "Works across different price levels — more consistent signal",
         f"ADX {s.get('adx',0):.1f} confirms trend is real"])


def strat_ultimate_oscillator(s):
    fires = (s.get("uo_oversold") and
             s.get("price_above_sma_200"))
    return _strat(fires, "long", "momentum",
        ["uo_oversold","price_above_sma_200"],
        [f"Ultimate Oscillator at {s.get('uo',0):.1f} — below 30, oversold",
         "Triple-timeframe momentum — fewer false signals than single-period",
         "Above 200 SMA — oversold in uptrend context"])


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY 3: TREND FOLLOWING (9 strategies)
# ─────────────────────────────────────────────────────────────────────────────

def strat_golden_cross_50_200(s):
    fires = s.get("ema_50_200_golden_cross")
    return _strat(fires, "long", "trend",
        ["ema_50_200_golden_cross"],
        ["EMA-50 crossed above EMA-200 — golden cross",
         "Most widely followed long-term trend signal",
         "Signals structural shift from bearish to bullish"])


def strat_golden_cross_9_21(s):
    fires = (s.get("ema_9_21_golden_cross") and
             s.get("price_above_sma_50"))
    return _strat(fires, "long", "trend",
        ["ema_9_21_golden_cross","price_above_sma_50"],
        ["Fast EMA-9 crossed above EMA-21 — early trend signal",
         "Earlier than 50/200 cross — more trades, faster entry",
         "Above 50 SMA confirms broader uptrend intact"])


def strat_golden_cross_20_50(s):
    fires = (s.get("ema_20_50_golden_cross") and
             s.get("price_above_ema_200"))
    return _strat(fires, "long", "trend",
        ["ema_20_50_golden_cross","price_above_ema_200"],
        ["EMA-20 crossed above EMA-50 — medium-term trend confirmation",
         "Sits between fast (9/21) and slow (50/200) signals",
         "Above 200 EMA confirms long-term trend structure"])


def strat_parabolic_sar_flip(s):
    fires = (s.get("psar_flip_up") and
             s.get("adx_trending"))
    return _strat(fires, "long", "trend",
        ["psar_flip_up","adx_trending"],
        ["Parabolic SAR flipped from above price to below — trend reversal",
         "Clean, unambiguous signal used by professional trend traders",
         f"ADX at {s.get('adx',0):.1f} confirms trend has strength"])


def strat_tema_dema(s):
    fires = (s.get("tema_cross_up") and
             s.get("price_above_tema"))
    return _strat(fires, "long", "trend",
        ["tema_cross_up","price_above_tema"],
        ["TEMA crossed above DEMA — fast moving average system",
         "Catches trends earlier than standard EMAs",
         "Price above TEMA confirms momentum alignment"])


def strat_ichimoku_tk_cross(s):
    fires = (s.get("ichi_tk_cross_up") and
             not s.get("ichi_below_cloud"))
    return _strat(fires, "long", "trend",
        ["ichi_tk_cross_up","not_below_cloud"],
        ["Ichimoku Tenkan crossed above Kijun — TK cross",
         "Earlier signal than full cloud breakout",
         "Price not below cloud — structure not bearish"])


def strat_ichimoku_cloud_breakout(s):
    fires = (s.get("ichi_above_cloud") and
             s.get("ichi_tk_bullish") and
             s.get("adx_trending"))
    return _strat(fires, "long", "trend",
        ["ichi_above_cloud","ichi_tk_bullish","adx_trending"],
        ["Price above Ichimoku Cloud — full bullish structure",
         "Tenkan above Kijun — short-term momentum aligned",
         f"ADX {s.get('adx',0):.1f} confirms strong trend"])


def strat_adx_initiation(s):
    fires = (s.get("adx_cross_up") and
             s.get("adx_di_bull"))
    return _strat(fires, "long", "trend",
        ["adx_cross_up","adx_di_bull"],
        [f"ADX crossed above 25 — trend initiating from flat",
         "DI+ above DI- confirms bullish directional movement",
         "High probability entry — catching trend at inception"])


def strat_supertrend_macd(s):
    fires = (s.get("supertrend_bullish") and
             s.get("macd_12_26_9_bullish") and
             s.get("adx", 0) > 20)
    return _strat(fires, "long", "trend",
        ["supertrend_bullish","macd_bullish","adx>20"],
        ["Supertrend indicator bullish — trend confirmed",
         "MACD histogram positive — momentum aligned",
         f"ADX {s.get('adx',0):.1f} — trend has strength"])


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY 4: MEAN REVERSION (11 strategies — including 2 shorts)
# ─────────────────────────────────────────────────────────────────────────────

def strat_rsi_oversold(s):
    fires = (s.get("rsi_14", 50) < 35 and
             s.get("price_above_sma_50"))
    return _strat(fires, "long", "mean_reversion",
        ["rsi_14<35","price_above_sma_50"],
        [f"RSI-14 oversold at {s.get('rsi_14',0):.1f} — below 35",
         "Above 50 SMA — buying dip within uptrend",
         "Classic mean reversion setup — oversold in bull context"])


def strat_rsi9_extreme(s):
    fires = (s.get("rsi_9_extreme_os") and
             s.get("price_above_ema_200") and
             s.get("rsi_9_rising"))
    return _strat(fires, "long", "mean_reversion",
        ["rsi_9<20","price_above_ema_200","rsi_9_rising"],
        [f"RSI-9 at {s.get('rsi_9',0):.1f} — extreme oversold below 20",
         "Above 200 EMA — oversold within long-term uptrend",
         "RSI-9 rising — momentum beginning to recover"])


def strat_rsi21_slow(s):
    fires = (s.get("rsi_21", 50) < 35 and
             s.get("price_above_sma_50"))
    return _strat(fires, "long", "mean_reversion",
        ["rsi_21<35","price_above_sma_50"],
        [f"Slow RSI-21 oversold at {s.get('rsi_21',0):.1f}",
         "Slower RSI = higher quality signals, fewer false positives",
         "Above 50 SMA — confirms overall uptrend"])


def strat_rsi_overbought_short(s):
    fires = (s.get("rsi_14", 50) > 70 and
             not s.get("price_above_sma_50") and
             s.get("bearish_engulfing"))
    return _strat(fires, "short", "mean_reversion",
        ["rsi_14>70","below_sma_50","bearish_engulfing"],
        [f"RSI-14 overbought at {s.get('rsi_14',0):.1f} — above 70",
         "Below 50 SMA — selling rally in downtrend",
         "Bearish engulfing confirms sellers taking control"])


def strat_mfi_oversold(s):
    fires = (s.get("mfi_oversold") and
             s.get("near_s1") or s.get("near_s2") and
             s.get("obv_bullish"))
    return _strat(fires, "long", "mean_reversion",
        ["mfi_oversold","at_support","obv_bullish"],
        [f"MFI at {s.get('mfi',0):.1f} — volume-weighted RSI oversold",
         "At pivot support level — double confirmation",
         "OBV rising — smart money accumulating"])


def strat_cmf_flip(s):
    fires = (s.get("cmf_cross_up") and
             s.get("rsi_14", 50) < 50)
    return _strat(fires, "long", "mean_reversion",
        ["cmf_cross_up","rsi_14<50"],
        [f"CMF crossed above zero — institutional money flow turned positive",
         "Chaikin Money Flow measures buying/selling pressure over 20 days",
         "RSI below 50 — not entering overbought territory"])


def strat_bollinger_lower(s):
    fires = (s.get("bb_20_20_touch_lower") and
             s.get("rsi_14", 50) < 40 and
             s.get("adx", 30) < 30)
    return _strat(fires, "long", "mean_reversion",
        ["bb_20_20_touch_lower","rsi_14<40","adx<30"],
        [f"Price at lower Bollinger Band (20,2) — statistically extreme",
         f"RSI-14 at {s.get('rsi_14',0):.1f} confirms oversold",
         "ADX below 30 — no strong downtrend, reversion likely"])


def strat_bollinger_tight(s):
    fires = (s.get("bb_20_15_touch_lower") and
             s.get("rsi_14", 50) < 45)
    return _strat(fires, "long", "mean_reversion",
        ["bb_20_15_touch_lower","rsi_14<45"],
        ["Price at tighter Bollinger Band (20,1.5) — more frequent signal",
         f"RSI-14 at {s.get('rsi_14',0):.1f} — oversold",
         "1.5σ band = lower threshold, more trades than 2σ"])


def strat_bollinger_upper_short(s):
    fires = (s.get("bb_20_20_touch_upper") and
             s.get("rsi_14", 50) > 70 and
             s.get("shooting_star"))
    return _strat(fires, "short", "mean_reversion",
        ["bb_20_20_touch_upper","rsi_14>70","shooting_star"],
        [f"Price at upper Bollinger Band (20,2) — overbought extreme",
         f"RSI-14 at {s.get('rsi_14',0):.1f} — overbought above 70",
         "Shooting star candle — sellers rejecting the high"])


def strat_keltner_lower(s):
    fires = (s.get("kc_touch_lower") and
             s.get("hammer") and
             s.get("obv_bullish"))
    return _strat(fires, "long", "mean_reversion",
        ["kc_touch_lower","hammer","obv_bullish"],
        ["Price at lower Keltner Channel — ATR-based support",
         "Hammer candle confirms buyers defending the level",
         "OBV rising — volume-confirmed accumulation"])


def strat_stoch_oversold(s):
    fires = (s.get("stoch_oversold") and
             s.get("stoch_bullish_cross") and
             s.get("price_above_ema_20"))
    return _strat(fires, "long", "mean_reversion",
        ["stoch_oversold","stoch_bullish_cross","price_above_ema_20"],
        [f"Stochastic %K at {s.get('stoch_k',0):.1f} — oversold below 20",
         "K crossed above D — momentum turning bullish",
         "Above EMA-20 — buying dip in short-term uptrend"])


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY 5: BREAKOUT (6 strategies)
# ─────────────────────────────────────────────────────────────────────────────

def strat_squeeze_breakout(s):
    fires = s.get("squeeze_fire_up")
    return _strat(fires, "long", "breakout",
        ["squeeze_fire_up"],
        ["Bollinger Bands were inside Keltner Channels — coiling",
         "Squeeze released with positive momentum — energy unleashing",
         "One of the highest probability breakout signals"])


def strat_volume_spike_breakout(s):
    fires = (s.get("dc20_breakout_up") and
             s.get("vol_spike_2x") and
             s.get("above_vwap"))
    return _strat(fires, "long", "breakout",
        ["dc20_breakout_up","vol_spike_2x","above_vwap"],
        ["Price broke above 20-day Donchian channel high",
         "Volume 2× confirms institutional participation",
         "Above VWAP — intraday buyers in control"])


def strat_52w_high_breakout(s):
    fires = (s.get("break_52w_high") and
             s.get("vol_spike_2x"))
    return _strat(fires, "long", "breakout",
        ["break_52w_high","vol_spike_2x"],
        [f"Price broke 52-week high at ${s.get('year_high',0):.2f}",
         "Most studied momentum signal — new highs attract buyers",
         "Volume 2× confirms institutional conviction"])


def strat_inside_bar_breakout(s):
    fires = (s.get("inside_bar") and
             s.get("adx_trending") and
             s.get("above_vwap"))
    return _strat(fires, "long", "breakout",
        ["inside_bar","adx_trending","above_vwap"],
        ["Inside bar formed — consolidation within prior bar's range",
         "Classic pre-breakout compression setup",
         "ADX trending and above VWAP — breakout direction likely up"])


def strat_force_index_breakout(s):
    fires = (s.get("force_index_cross_up") and
             s.get("price_above_ema_20"))
    return _strat(fires, "long", "breakout",
        ["force_index_cross_up","price_above_ema_20"],
        ["Force Index crossed above zero — price × volume momentum turning positive",
         "Combines both price movement and volume — strong confirmation",
         "Above EMA-20 confirms short-term uptrend context"])


def strat_donchian_10_breakout(s):
    fires = (s.get("dc10_breakout_up") and
             s.get("vol_spike_15x") and
             s.get("macd_12_26_9_bullish"))
    return _strat(fires, "long", "breakout",
        ["dc10_breakout_up","vol_spike_1.5x","macd_bullish"],
        ["Price broke 10-day Donchian high — faster breakout signal",
         "Volume 1.5× confirms move has participation",
         "MACD positive — momentum supporting breakout"])


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY 6: CANDLE PATTERNS (6 strategies — 2 shorts)
# ─────────────────────────────────────────────────────────────────────────────

def strat_morning_star(s):
    fires = (s.get("morning_star") and
             s.get("rsi_14", 50) < 45 and
             s.get("ema_50_200_bullish"))
    return _strat(fires, "long", "candle",
        ["morning_star","rsi_14<45","ema_50_200_bullish"],
        ["Three-bar morning star reversal pattern",
         "Day 1: sellers in control. Day 2: indecision. Day 3: buyers take over",
         "Above 50/200 EMA confirms overall uptrend supports this reversal"])


def strat_bullish_engulfing_support(s):
    fires = (s.get("bullish_engulfing") and
             (s.get("near_s1") or s.get("near_s2") or s.get("at_key_fib")) and
             s.get("obv_bullish"))
    return _strat(fires, "long", "candle",
        ["bullish_engulfing","at_support_level","obv_bullish"],
        ["Bullish engulfing candle at support level",
         "Two independent systems confirming: candle pattern + price level",
         "OBV rising — volume confirms accumulation at support"])


def strat_doji_at_support(s):
    fires = (s.get("doji") and
             (s.get("near_s1") or s.get("near_s2") or s.get("at_key_fib")) and
             s.get("vol_spike_15x"))
    return _strat(fires, "long", "candle",
        ["doji","at_support","vol_spike_1.5x"],
        ["Doji candle at support — indecision after downmove",
         "Buyers and sellers equally matched — reversal often follows",
         "Volume spike confirms the level is being contested"])


def strat_three_white_soldiers(s):
    fires = (s.get("three_white_soldiers") and
             s.get("rsi_14", 50) < 60)
    return _strat(fires, "long", "candle",
        ["three_white_soldiers","rsi_14<60"],
        ["Three consecutive bullish candles each closing near their high",
         "Strong reversal signal — sustained buying pressure over 3 days",
         "RSI below 60 — room to run, not entering overbought"])


def strat_shooting_star_short(s):
    fires = (s.get("shooting_star") and
             (s.get("near_r1") or s.get("near_r2") or
              s.get("bb_20_20_touch_upper")) and
             s.get("rsi_14", 50) > 65)
    return _strat(fires, "short", "candle",
        ["shooting_star","at_resistance","rsi_14>65"],
        ["Shooting star at resistance level — bearish reversal",
         "Long upper wick shows sellers rejecting higher prices",
         f"RSI-14 at {s.get('rsi_14',0):.1f} — overbought at resistance"])


def strat_evening_star_short(s):
    fires = (s.get("evening_star") and
             s.get("rsi_14", 50) > 55 and
             not s.get("price_above_sma_50"))
    return _strat(fires, "short", "candle",
        ["evening_star","rsi_14>55","below_sma_50"],
        ["Three-bar evening star — bearish reversal pattern",
         "Mirror of morning star: buyers exhausted, sellers take control",
         "Below 50 SMA confirms downtrend context for the short"])


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY 7: CONFLUENCE (9 strategies — highest conviction)
# ─────────────────────────────────────────────────────────────────────────────

def strat_rsi_volume_200ema(s):
    fires = (s.get("rsi_14", 50) < 35 and
             s.get("vol_spike_2x") and
             s.get("price_above_ema_200"))
    return _strat(fires, "long", "confluence",
        ["rsi_14<35","vol_spike_2x","price_above_ema_200"],
        [f"Triple confluence: RSI oversold at {s.get('rsi_14',0):.1f}",
         "Volume 2× — institutional buying on the dip",
         "Above 200 EMA — buying within structural uptrend"])


def strat_macd_ichimoku(s):
    fires = (s.get("macd_12_26_9_crossover_up") and
             s.get("ichi_above_cloud"))
    return _strat(fires, "long", "confluence",
        ["macd_crossover_up","ichi_above_cloud"],
        ["MACD crossover + above Ichimoku Cloud simultaneously",
         "Two independent systems both turning bullish at same time",
         "Momentum signal confirmed by trend structure signal"])


def strat_bb_squeeze_volume(s):
    fires = (s.get("squeeze_fire_up") and
             s.get("vol_spike_2x") and
             s.get("above_vwap"))
    return _strat(fires, "long", "confluence",
        ["squeeze_fire_up","vol_spike_2x","above_vwap"],
        ["BB squeeze releasing with 2× volume — institutional breakout",
         "Compression followed by high-participation expansion",
         "Above VWAP — buyers in control intraday"])


def strat_pivot_fib_confluence(s):
    fires = ((s.get("near_s1") or s.get("near_s2")) and
             s.get("at_key_fib") and
             (s.get("hammer") or s.get("bullish_engulfing")))
    return _strat(fires, "long", "confluence",
        ["at_pivot_support","at_key_fib","bullish_candle"],
        ["Two independent systems pointing to the same price level",
         "Standard pivot AND Fibonacci retracement both at current price",
         "Bullish candle confirms buyers at the confluence zone"])


def strat_golden_cross_volume(s):
    fires = (s.get("ema_50_200_golden_cross") and
             s.get("vol_spike_2x"))
    return _strat(fires, "long", "confluence",
        ["ema_50_200_golden_cross","vol_spike_2x"],
        ["Golden cross with 2× volume on the cross day itself",
         "Institutional confirmation — the cross has real participation",
         "High conviction — volume validates the signal"])


def strat_cpr_narrow_momentum(s):
    fires = (s.get("cpr_narrow") and
             s.get("above_cpr") and
             s.get("rsi_14", 50) > 50 and
             s.get("macd_12_26_9_bullish"))
    return _strat(fires, "long", "confluence",
        ["cpr_narrow","above_cpr","rsi_14>50","macd_bullish"],
        ["Narrow CPR + above CPR = professional directional bias setup",
         f"RSI-14 at {s.get('rsi_14',0):.1f} and MACD positive — momentum aligned",
         "Four signals confirming bullish day — high conviction"])


def strat_camarilla_rsi_obv(s):
    fires = (s.get("near_cam_s3") and
             s.get("rsi_14", 50) < 35 and
             s.get("obv_bullish") and
             s.get("cmf_positive"))
    return _strat(fires, "long", "confluence",
        ["near_cam_s3","rsi_14<35","obv_bullish","cmf_positive"],
        ["Camarilla S3 + RSI oversold + OBV rising + CMF positive",
         "Four independent signals at the strongest Camarilla support",
         "Extremely rare — highest conviction mean reversion setup"])


def strat_supertrend_ichimoku_adx(s):
    fires = (s.get("supertrend_bullish") and
             s.get("ichi_above_cloud") and
             s.get("adx_strong"))
    return _strat(fires, "long", "confluence",
        ["supertrend_bullish","ichi_above_cloud","adx_strong"],
        ["Three trend systems simultaneously bullish",
         "Supertrend + Ichimoku Cloud + ADX all aligned",
         f"ADX at {s.get('adx',0):.1f} — very strong trend confirmed"])


def strat_williams_stoch_dual(s):
    fires = (s.get("williams_r_oversold") and
             s.get("stoch_oversold") and
             (s.get("near_s1") or s.get("near_s2") or s.get("near_cam_s3")))
    return _strat(fires, "long", "confluence",
        ["williams_r_oversold","stoch_oversold","at_pivot_support"],
        [f"Williams %R at {s.get('williams_r',0):.1f} — oversold",
         f"Stochastic at {s.get('stoch_k',0):.1f} — also oversold",
         "Both momentum indicators oversold at pivot support — high conviction"])


# ─────────────────────────────────────────────────────────────────────────────
# STRATEGY REGISTRY — all 60 strategies
# ─────────────────────────────────────────────────────────────────────────────

ALL_STRATEGIES = {
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
}

STRATEGY_CATEGORIES = {
    name: fn({}).__class__  # placeholder — category stored in each fn
    for name, fn in ALL_STRATEGIES.items()
}


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY ZONE VALIDATOR
# ─────────────────────────────────────────────────────────────────────────────

def validate_entry_zone(
    open_price: float,
    signal_close: float,
    atr: float,
    category: str,
    direction: str,
) -> tuple[bool, str]:
    """
    Check if the next-day open is within the acceptable entry zone.
    Returns (valid: bool, reason: str).
    """
    from backtest.config import ENTRY_GAP_ATR_MULT
    mult      = ENTRY_GAP_ATR_MULT.get(category, 1.5)
    gap_atr   = (open_price - signal_close) / atr if atr > 0 else 0
    gap_pct   = (open_price - signal_close) / signal_close * 100 if signal_close > 0 else 0

    if direction == "long":
        if gap_atr > mult:
            return False, f"gap_up_{gap_pct:.1f}pct_exceeds_{mult}x_atr_limit"
        return True, f"entry_valid_gap_{gap_pct:.1f}pct"
    else:  # short
        gap_atr_short = (signal_close - open_price) / atr if atr > 0 else 0
        if gap_atr_short > mult:
            return False, f"gap_down_{abs(gap_pct):.1f}pct_exceeds_{mult}x_atr_limit"
        return True, f"entry_valid_gap_{gap_pct:.1f}pct"


# ─────────────────────────────────────────────────────────────────────────────
# SCREENING PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def screen_instrument(
    ticker: str,
    df: pd.DataFrame,
    info: dict,
    as_of: date,
    regime: str = "neutral",
) -> dict:
    """
    Run single instrument through full pipeline.
    Returns candidate dict with all strategies triggered, signals, and bullets.
    """
    passes, fail_reason = passes_liquidity_filter(ticker, df, info, as_of)
    if not passes:
        return {"ticker": ticker, "as_of": as_of, "liquidity_ok": False,
                "fail_reason": fail_reason, "strategies": []}

    signals = compute_all_signals(df)
    if not signals:
        return {"ticker": ticker, "as_of": as_of, "liquidity_ok": True,
                "fail_reason": "no_signals", "strategies": []}

    triggered_long  = []
    triggered_short = []

    for name, fn in ALL_STRATEGIES.items():
        try:
            result = fn(signals)
            if not result["fires"]:
                continue
            direction = result["direction"]
            # Regime filter — check if direction is allowed
            if direction == "long" and regime == "crisis":
                continue
            if direction == "short" and regime == "bull":
                result["direction"] = "long_only"  # mark as reduced
            entry = {
                "strategy":        name,
                "direction":       direction,
                "category":        result["category"],
                "signals_used":    result["signals_used"],
                "context_bullets": result["context_bullets"],
            }
            if direction == "long":
                triggered_long.append(entry)
            else:
                triggered_short.append(entry)
        except Exception as exc:
            logger.debug("Strategy %s error for %s: %s", name, ticker, exc)

    all_triggered = triggered_long + triggered_short
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
        "strategy_count":    len(all_triggered),
        "long_count":        len(triggered_long),
        "short_count":       len(triggered_short),
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
) -> list:
    """Screen all instruments. Returns candidates sorted by strategy count."""
    candidates = []
    for ticker, df in ohlcv_dict.items():
        info   = info_dict.get(ticker, {"ticker": ticker})
        result = screen_instrument(ticker, df, info, as_of, regime)
        if result.get("liquidity_ok") and result.get("strategy_count", 0) >= min_strategies:
            candidates.append(result)
    candidates.sort(key=lambda x: (x["strategy_count"], x["tech_signal_count"]), reverse=True)
    logger.info("screen_universe [%s] regime=%s: %d/%d passed",
                as_of, regime, len(candidates), len(ohlcv_dict))
    return candidates
