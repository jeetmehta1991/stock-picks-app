"""SMC / ICT signal computation via vendored smartmoneyconcepts library.

Batch 210 (new strategy family 2026-05-17 owner-approved research review).
Wraps the joshyattridge/smart-money-concepts library (vendored under
DEC-508 Phase A) and emits a compact signal dict suitable for merging
into the screener per-ticker signals.

Implements the core ICT/SMC concepts:
  - Fair Value Gap (FVG): 3-bar imbalance where prev_high < next_low
    (bullish FVG) or prev_low > next_high (bearish FVG)
  - Order Block (OB): last opposing candle before a strong impulse,
    used as support/resistance reference
  - BOS / CHoCH: Break of Structure (continuation) and Change of
    Character (reversal) - market-structure shifts
  - Liquidity sweep: price moves through a cluster of equal highs/lows
    sweeping liquidity then reversing
  - Swing high/low identification (50-bar default)

Empirical backing (Quantum Algo Mar 2026): on 10-asset / 2,600-trade
backtest over 26 months, the combined SMC stack delivered 61% win rate /
2.17 profit factor / +2.27R average. Designed to complement (not
duplicate) the technical-indicator roster.
"""

from __future__ import annotations

import contextlib
import io
from typing import Optional

import pandas as pd


# Suppress the library's startup banner (Unicode glyph triggers
# UnicodeEncodeError on cp1252 Windows consoles). The import remains
# functional under any encoding.
with contextlib.redirect_stdout(io.StringIO()):
    try:
        from vendored.smartmoneyconcepts.smartmoneyconcepts import smc as _smc
        _SMC_AVAILABLE = True
    except Exception:
        _smc = None
        _SMC_AVAILABLE = False


def compute_smc_signals(
    ohlc: pd.DataFrame,
    swing_length: int = 50,
    fvg_lookback: int = 5,
    liquidity_range_pct: float = 0.01,
    dealing_range_lookback: int = 50,
) -> dict:
    """Compute SMC / ICT signals for a single-ticker OHLCV DataFrame.

    Returns a dict of boolean / numeric signals (empty dict when SMC
    library unavailable or insufficient history). All keys optional;
    consumers (screener strategies) should use s.get() with defaults.

    Original keys (Batch 210):
      - smc_fvg_bullish_active / smc_fvg_bearish_active: bool
      - smc_ob_bullish_active / smc_ob_bearish_active: bool
      - smc_bos_bullish / smc_bos_bearish: bool
      - smc_choch_bullish / smc_choch_bearish: bool
      - smc_liquidity_swept_up / smc_liquidity_swept_dn: bool

    Batch 216 expansion (FVG / OB variants + dealing range + OTE +
    BOS retest):
      - smc_fvg_retest_long_zone / smc_fvg_retest_short_zone: bool
        (price currently inside an unmitigated FVG zone)
      - smc_inverse_fvg_bullish / smc_inverse_fvg_bearish: bool
        (FVG was mitigated and price now opposite side -> role flip)
      - smc_breaker_block_bullish / smc_breaker_block_bearish: bool
        (OB was mitigated -> acts opposite to original direction)
      - smc_mitigation_block_long / smc_mitigation_block_short: bool
        (price inside an OB zone that is being mitigated NOW)
      - smc_dealing_range_pct: float in [0,1] (0=at low, 1=at high)
      - smc_in_discount_zone: bool (pct < 0.5)
      - smc_in_premium_zone: bool (pct > 0.5)
      - smc_ote_long_zone / smc_ote_short_zone: bool (62-79% Fib
        retracement zone after bullish/bearish CHoCH)
      - smc_equal_highs_swept / smc_equal_lows_swept: bool (liquidity
        primitive with Swept=True)
      - smc_bos_retest_long / smc_bos_retest_short: bool (price within
        0.5% of a recently-broken BOS level)
    """
    if not _SMC_AVAILABLE or ohlc is None or ohlc.empty:
        return {}
    required = {"open", "high", "low", "close"}
    if not required.issubset(set(ohlc.columns)):
        return {}
    if len(ohlc) < max(swing_length * 2, 100):
        return {}
    out: dict = {}
    close = float(ohlc["close"].iloc[-1])
    current_idx = len(ohlc) - 1
    # FVG: Bullish (1) / Bearish (-1) / no FVG (0). Library also exposes
    # Top / Bottom / MitigatedIndex columns enabling retest / inverse logic.
    fvg_df = None
    try:
        fvg_df = _smc.fvg(ohlc)
        if "FVG" in fvg_df.columns:
            recent = fvg_df["FVG"].tail(fvg_lookback)
            out["smc_fvg_bullish_active"] = bool((recent == 1).any())
            out["smc_fvg_bearish_active"] = bool((recent == -1).any())
            # Batch 216: retest zone - price inside an UNMITIGATED FVG zone.
            # Library's MitigatedIndex is 0/NaN when not mitigated, integer
            # index when mitigated. Iterate recent FVGs to find a live zone
            # bracketing the current close.
            if "Top" in fvg_df.columns and "Bottom" in fvg_df.columns:
                retest_long = False
                retest_short = False
                # Scan last 50 FVGs - balance coverage vs cost
                tail = fvg_df.tail(50)
                for idx_pos in range(len(tail)):
                    row = tail.iloc[idx_pos]
                    fvg_val = row.get("FVG")
                    if pd.isna(fvg_val) or fvg_val == 0:
                        continue
                    top = row.get("Top")
                    bot = row.get("Bottom")
                    mit = row.get("MitigatedIndex")
                    if pd.isna(top) or pd.isna(bot):
                        continue
                    # Mitigated = MitigatedIndex is set (>0) AND < current_idx
                    is_mitigated = (
                        not pd.isna(mit) and mit > 0 and int(mit) < current_idx
                    )
                    in_zone = (close >= float(bot)) and (close <= float(top))
                    if not is_mitigated and in_zone:
                        if fvg_val == 1:
                            retest_long = True
                        elif fvg_val == -1:
                            retest_short = True
                    # Batch 216: inverse FVG - bullish FVG that got
                    # mitigated and price now ABOVE the FVG top (role
                    # flipped from support to resistance) -> short bias;
                    # symmetric bearish FVG below bottom -> long bias.
                    if is_mitigated:
                        if fvg_val == 1 and close < float(bot):
                            out["smc_inverse_fvg_bearish"] = True
                        elif fvg_val == -1 and close > float(top):
                            out["smc_inverse_fvg_bullish"] = True
                out["smc_fvg_retest_long_zone"]  = retest_long
                out["smc_fvg_retest_short_zone"] = retest_short
                out.setdefault("smc_inverse_fvg_bullish", False)
                out.setdefault("smc_inverse_fvg_bearish", False)
    except Exception:
        pass
    try:
        swings = _smc.swing_highs_lows(ohlc, swing_length=swing_length)
        # Order blocks (with Top/Bottom/MitigatedIndex for breaker /
        # mitigation logic)
        try:
            ob_df = _smc.ob(ohlc, swings)
            if "OB" in ob_df.columns:
                recent_ob = ob_df["OB"].tail(fvg_lookback)
                out["smc_ob_bullish_active"] = bool((recent_ob == 1).any())
                out["smc_ob_bearish_active"] = bool((recent_ob == -1).any())
                if "Top" in ob_df.columns and "Bottom" in ob_df.columns:
                    breaker_bull = False
                    breaker_bear = False
                    mitigation_long = False
                    mitigation_short = False
                    tail = ob_df.tail(50)
                    for idx_pos in range(len(tail)):
                        row = tail.iloc[idx_pos]
                        ob_val = row.get("OB")
                        if pd.isna(ob_val) or ob_val == 0:
                            continue
                        top = row.get("Top")
                        bot = row.get("Bottom")
                        mit = row.get("MitigatedIndex")
                        if pd.isna(top) or pd.isna(bot):
                            continue
                        is_mitigated = (
                            not pd.isna(mit) and mit > 0 and int(mit) < current_idx
                        )
                        in_zone = (close >= float(bot)) and (close <= float(top))
                        # Batch 216: Breaker block - mitigated OB flips role.
                        # Bullish OB that's broken downward -> now resistance
                        # (short bias). Bearish OB broken upward -> support.
                        if is_mitigated:
                            if ob_val == 1 and close < float(bot):
                                breaker_bear = True
                            elif ob_val == -1 and close > float(top):
                                breaker_bull = True
                        # Mitigation block: price currently inside an
                        # UN-mitigated OB zone (about to be mitigated NOW)
                        if not is_mitigated and in_zone:
                            if ob_val == 1:
                                mitigation_long = True
                            elif ob_val == -1:
                                mitigation_short = True
                    out["smc_breaker_block_bullish"]  = breaker_bull
                    out["smc_breaker_block_bearish"]  = breaker_bear
                    out["smc_mitigation_block_long"]  = mitigation_long
                    out["smc_mitigation_block_short"] = mitigation_short
        except Exception:
            pass
        # BOS / CHoCH with Level for retest logic
        bos_df = None
        try:
            bos_df = _smc.bos_choch(ohlc, swings)
            if "BOS" in bos_df.columns:
                recent_bos = bos_df["BOS"].tail(fvg_lookback)
                out["smc_bos_bullish"] = bool((recent_bos == 1).any())
                out["smc_bos_bearish"] = bool((recent_bos == -1).any())
            if "CHOCH" in bos_df.columns:
                recent_choch = bos_df["CHOCH"].tail(fvg_lookback)
                out["smc_choch_bullish"] = bool((recent_choch == 1).any())
                out["smc_choch_bearish"] = bool((recent_choch == -1).any())
            # Batch 216: BOS retest - price within 0.5pct of a recently-
            # broken BOS Level. Scan last 50 BOS strikes.
            if "BOS" in bos_df.columns and "Level" in bos_df.columns:
                tail = bos_df.tail(50)
                retest_long = False
                retest_short = False
                tol = 0.005  # 0.5% tolerance
                for idx_pos in range(len(tail)):
                    row = tail.iloc[idx_pos]
                    bos_val = row.get("BOS")
                    if pd.isna(bos_val) or bos_val == 0:
                        continue
                    level = row.get("Level")
                    if pd.isna(level) or float(level) <= 0:
                        continue
                    near = abs(close - float(level)) / float(level) < tol
                    if near:
                        if bos_val == 1:
                            retest_long = True
                        elif bos_val == -1:
                            retest_short = True
                out["smc_bos_retest_long"]  = retest_long
                out["smc_bos_retest_short"] = retest_short
        except Exception:
            pass
        # Liquidity sweeps (with Swept flag exposing equal-highs/lows
        # taken-out events explicitly)
        try:
            liq_df = _smc.liquidity(ohlc, swings, range_percent=liquidity_range_pct)
            if "Liquidity" in liq_df.columns:
                recent_liq = liq_df["Liquidity"].tail(fvg_lookback)
                out["smc_liquidity_swept_up"] = bool((recent_liq == 1).any())
                out["smc_liquidity_swept_dn"] = bool((recent_liq == -1).any())
                # Batch 216: equal-highs / equal-lows sweep - liquidity
                # primitive with Swept flag set TRUE in recent bars.
                if "Swept" in liq_df.columns:
                    tail = liq_df.tail(fvg_lookback)
                    eq_highs_swept = False
                    eq_lows_swept = False
                    for idx_pos in range(len(tail)):
                        row = tail.iloc[idx_pos]
                        liq_val = row.get("Liquidity")
                        swept_val = row.get("Swept")
                        if pd.isna(liq_val) or liq_val == 0:
                            continue
                        # Swept may be bool or numeric truthy
                        is_swept = bool(swept_val) if not pd.isna(swept_val) else False
                        if is_swept:
                            if liq_val == 1:
                                eq_highs_swept = True
                            elif liq_val == -1:
                                eq_lows_swept = True
                    out["smc_equal_highs_swept"] = eq_highs_swept
                    out["smc_equal_lows_swept"]  = eq_lows_swept
        except Exception:
            pass
        # Batch 216: retracements primitive for OTE (Optimal Trade Entry)
        # 62-79% Fibonacci zone after CHoCH.
        try:
            ret_df = _smc.retracements(ohlc, swings)
            if (
                "Direction" in ret_df.columns
                and "CurrentRetracement%" in ret_df.columns
            ):
                direction = ret_df["Direction"].iloc[-1]
                cur_ret = ret_df["CurrentRetracement%"].iloc[-1]
                if not pd.isna(direction) and not pd.isna(cur_ret):
                    in_ote = 62.0 <= float(cur_ret) <= 79.0
                    out["smc_ote_long_zone"]  = bool(in_ote and float(direction) > 0)
                    out["smc_ote_short_zone"] = bool(in_ote and float(direction) < 0)
                    out["smc_retracement_pct"] = round(float(cur_ret), 2)
        except Exception:
            pass
    except Exception:
        pass
    # Batch 216: dealing range pct - close position within
    # lookback-period high/low range. Used for premium/discount filter.
    try:
        if len(ohlc) >= dealing_range_lookback:
            window = ohlc.tail(dealing_range_lookback)
            hi = float(window["high"].max())
            lo = float(window["low"].min())
            if hi > lo:
                pct = (close - lo) / (hi - lo)
                pct = max(0.0, min(1.0, pct))
                out["smc_dealing_range_pct"] = round(pct, 4)
                out["smc_in_discount_zone"]  = pct < 0.5
                out["smc_in_premium_zone"]   = pct > 0.5
    except Exception:
        pass
    return out
