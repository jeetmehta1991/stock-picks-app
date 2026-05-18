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
) -> dict:
    """Compute SMC / ICT signals for a single-ticker OHLCV DataFrame.

    Returns a dict of boolean / numeric signals (empty dict when SMC
    library unavailable or insufficient history). All keys are optional
    so consumers (screener strategies) should use s.get() with defaults.

    Keys:
      - smc_fvg_bullish_active: bool - bullish FVG within last fvg_lookback bars
      - smc_fvg_bearish_active: bool - bearish FVG within last fvg_lookback bars
      - smc_ob_bullish_active:  bool - bullish order block recently confirmed
      - smc_ob_bearish_active:  bool - bearish order block recently confirmed
      - smc_bos_bullish:        bool - Break of Structure (continuation) up
      - smc_bos_bearish:        bool - Break of Structure (continuation) down
      - smc_choch_bullish:      bool - Change of Character (reversal) up
      - smc_choch_bearish:      bool - Change of Character (reversal) down
      - smc_liquidity_swept_up: bool - high cluster swept (potential reversal)
      - smc_liquidity_swept_dn: bool - low cluster swept
    """
    if not _SMC_AVAILABLE or ohlc is None or ohlc.empty:
        return {}
    # SMC library expects lowercase OHLC columns
    required = {"open", "high", "low", "close"}
    if not required.issubset(set(ohlc.columns)):
        return {}
    # Need enough bars for swing + structure detection
    if len(ohlc) < max(swing_length * 2, 100):
        return {}
    out: dict = {}
    try:
        # FVG: Bullish (1) / Bearish (-1) / no FVG (0)
        fvg_df = _smc.fvg(ohlc)
        if "FVG" in fvg_df.columns:
            recent = fvg_df["FVG"].tail(fvg_lookback)
            out["smc_fvg_bullish_active"] = bool((recent == 1).any())
            out["smc_fvg_bearish_active"] = bool((recent == -1).any())
    except Exception:
        pass
    try:
        # Swing highs/lows: 1 = high, -1 = low, 0 = neither
        swings = _smc.swing_highs_lows(ohlc, swing_length=swing_length)
        # Order blocks
        try:
            ob_df = _smc.ob(ohlc, swings)
            if "OB" in ob_df.columns:
                recent_ob = ob_df["OB"].tail(fvg_lookback)
                out["smc_ob_bullish_active"] = bool((recent_ob == 1).any())
                out["smc_ob_bearish_active"] = bool((recent_ob == -1).any())
        except Exception:
            pass
        # BOS / CHoCH
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
        except Exception:
            pass
        # Liquidity sweeps
        try:
            liq_df = _smc.liquidity(ohlc, swings, range_percent=liquidity_range_pct)
            if "Liquidity" in liq_df.columns:
                recent_liq = liq_df["Liquidity"].tail(fvg_lookback)
                out["smc_liquidity_swept_up"] = bool((recent_liq == 1).any())
                out["smc_liquidity_swept_dn"] = bool((recent_liq == -1).any())
        except Exception:
            pass
    except Exception:
        pass
    return out
