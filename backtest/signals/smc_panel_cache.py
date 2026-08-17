"""Batch 554 OPT-C Phase 4 (2026-06-02): SMC primitive panel-cache.

Backs out the 175s/profile cost of `compute_smc_signals` (vendored
smartmoneyconcepts library) by precomputing the 6 SMC primitives on the
FULL per-ticker OHLCV ONCE per session, then slicing the cached
DataFrames at each (ticker, as_of) call.

The library's primitives:
  - fvg(ohlc) - Fair Value Gap: 3-bar pattern, NO lookahead (formed at
    bar i, detectable at bar i).
  - swing_highs_lows(ohlc, swing_length) - uses `shift(-swing_length)`,
    LOOKAHEAD = swing_length bars.
  - ob(ohlc, swings) - Order Block, depends on swings -> inherits
    swing_length lookahead.
  - bos_choch(ohlc, swings) - Break of Structure / Change of Character,
    swing-dependent -> swing_length lookahead.
  - liquidity(ohlc, swings, range_percent) - swing-dependent.
  - retracements(ohlc, swings) - swing-dependent.

PIT-safety contract:
  - FVG: at as_of_idx, expose primitives with `Index <= as_of_idx`.
  - Swing-dependent (swings/ob/bos_choch/liquidity/retracements): at
    as_of_idx, expose primitives with `Index <= as_of_idx - swing_length`.
  - The existing derivation logic in `compute_smc_signals` already
    filters MitigatedIndex by `mit < current_idx`, so forward-time
    mitigation events caught during full-series compute are
    automatically masked out at earlier as_of values.

Open caveat (documented in B554 parity test):
  - The library's OB function has forward-mutating state (breaker block
    resets when a later bar's high exceeds the OB top). When precomputed
    on the full series, an OB at bar 100 may show different final state
    than when computed on a truncated slice at bar 300. The parity test
    enumerates divergence rate across (ticker, as_of) tuples; if
    divergence exceeds tolerance, this cache stays opt-in until a
    library refactor or replay-based correction lands.

Wire-in (B555 follow-on):
  - Engine `__init__` calls `prime_all_tickers(ohlcv_dict)` to populate
    cache from full series.
  - `compute_smc_signals(ohlc, ticker=ticker)` reads from cache when
    ticker provided and primed; falls back to per-call when not.
"""
from __future__ import annotations

import contextlib
import io
from typing import Optional

import pandas as pd


# Suppress library banner on import (cp1252 Unicode glyph).
with contextlib.redirect_stdout(io.StringIO()):
    try:
        from vendored.smartmoneyconcepts.smartmoneyconcepts import smc as _smc
        _SMC_AVAILABLE = True
    except Exception:
        _smc = None
        _SMC_AVAILABLE = False


# {ticker: {primitive_name: DataFrame_or_None, "swing_length": int,
#           "ohlc_len": int}}
_FULL_PRIMITIVES_BY_TICKER: dict[str, dict] = {}


def prime_ticker_primitives(
    ticker: str,
    full_ohlc: pd.DataFrame,
    swing_length: int = 20,
    liquidity_range_pct: float = 0.01,
    close_mitigation: bool = False,
) -> None:
    """Compute and cache the 6 SMC primitives for a ticker's full-series
    OHLCV. Idempotent: re-priming with the same swing_length is a no-op."""
    if not _SMC_AVAILABLE:
        return
    if ticker in _FULL_PRIMITIVES_BY_TICKER:
        return  # already primed
    if full_ohlc is None or full_ohlc.empty:
        _FULL_PRIMITIVES_BY_TICKER[ticker] = {"swing_length": swing_length}
        return
    required = {"open", "high", "low", "close"}
    if not required.issubset(set(full_ohlc.columns)):
        _FULL_PRIMITIVES_BY_TICKER[ticker] = {"swing_length": swing_length}
        return
    if len(full_ohlc) < max(swing_length * 2, 100):
        _FULL_PRIMITIVES_BY_TICKER[ticker] = {"swing_length": swing_length}
        return

    primitives: dict = {
        "swing_length": swing_length,
        "ohlc_len": len(full_ohlc),
    }
    # FVG: no swing dependency
    try:
        primitives["fvg"] = _smc.fvg(full_ohlc)
    except Exception:
        primitives["fvg"] = None
    # Swings: stateless rolling max/min with shift-ahead lookahead
    try:
        swings = _smc.swing_highs_lows(full_ohlc, swing_length=swing_length)
        primitives["swings"] = swings
    except Exception:
        swings = None
        primitives["swings"] = None
    if swings is not None:
        # Swing-dependent primitives
        try:
            primitives["ob"] = _smc.ob(full_ohlc, swings,
                                       close_mitigation=close_mitigation)
        except Exception:
            primitives["ob"] = None
        try:
            primitives["bos_choch"] = _smc.bos_choch(full_ohlc, swings)
        except Exception:
            primitives["bos_choch"] = None
        try:
            primitives["liquidity"] = _smc.liquidity(
                full_ohlc, swings, range_percent=liquidity_range_pct,
            )
        except Exception:
            primitives["liquidity"] = None
        try:
            primitives["retracements"] = _smc.retracements(full_ohlc, swings)
        except Exception:
            primitives["retracements"] = None
    primitives["close_mitigation"] = close_mitigation
    _FULL_PRIMITIVES_BY_TICKER[ticker] = primitives


def get_primitives_at(
    ticker: str, current_idx: int, swing_length: int = 20,
    close_mitigation: bool = False,
) -> Optional[dict]:
    """Return primitives sliced to bars visible at current_idx for PIT
    safety. Returns None when ticker isn't primed; returns empty-ish dict
    when primed but insufficient history.

    Slicing rules:
      - FVG: `Index <= current_idx` (no lookahead).
      - Swing-dependent (swings/ob/bos_choch/liquidity/retracements):
        `Index <= current_idx - swing_length` to mask the swing's
        shift-ahead detection.
    """
    p = _FULL_PRIMITIVES_BY_TICKER.get(ticker)
    if p is None:
        return None
    if p.get("swing_length") != swing_length:
        # Primed with different swing_length -- cache miss, signal caller
        # to fall back to per-call compute (avoid silent semantic drift).
        return None
    # B1616: same guard for close_mitigation. It changes which order blocks
    # are MITIGATED, so a cache primed at one value would silently serve the
    # other's order blocks - the exact drift the swing_length guard prevents.
    if bool(p.get("close_mitigation", False)) != bool(close_mitigation):
        return None
    out: dict = {"current_idx": current_idx}
    # FVG has 1-bar lookahead: uses ohlc["low"].shift(-1) and
    # ohlc["high"].shift(-1) to detect the 3-bar gap pattern. So FVG at
    # bar i needs bar i+1's data and is only PIT-detectable at as_of i+1.
    # At current_idx, filter FVG to `Index <= current_idx - 1`.
    fvg_df = p.get("fvg")
    if fvg_df is not None and current_idx >= 1:
        out["fvg"] = fvg_df.iloc[:current_idx]
    # Swing-dependent primitives: swing_highs_lows uses shift(-swing_length)
    # to detect swings (`swing_length *= 2`, then shift = swing_length // 2
    # in the library; so for user swing_length=20, the effective lookahead
    # IS swing_length=20 bars). Filter to Index <= current_idx - swing_length.
    swing_safe_idx = current_idx - swing_length
    if swing_safe_idx >= 0:
        for key in ("swings", "ob", "bos_choch", "liquidity", "retracements"):
            df = p.get(key)
            if df is not None:
                out[key] = df.iloc[:swing_safe_idx + 1]
    return out


def is_primed(ticker: str) -> bool:
    """True iff a non-empty cache entry exists for ticker."""
    p = _FULL_PRIMITIVES_BY_TICKER.get(ticker)
    if p is None:
        return False
    return p.get("fvg") is not None or p.get("swings") is not None


def reset_cache() -> None:
    """Test helper. Clears the module-level cache."""
    _FULL_PRIMITIVES_BY_TICKER.clear()
