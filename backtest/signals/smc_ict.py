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

from backtest.util.silent_failure_logger import log_silent_failure


# Suppress the library's startup banner (Unicode glyph triggers
# UnicodeEncodeError on cp1252 Windows consoles). The import remains
# functional under any encoding.
with contextlib.redirect_stdout(io.StringIO()):
    try:
        from vendored.smartmoneyconcepts.smartmoneyconcepts import smc as _smc
        _SMC_AVAILABLE = True
    except Exception as _e:
        # Batch 458 (AU2): log the import failure so the SMC silent-failure
        # mode (queue item #3 PRODUCER_LAYER_ZERO_LIKELY) surfaces in logs.
        log_silent_failure("smc_ict.import_smartmoneyconcepts", _e)
        _smc = None
        _SMC_AVAILABLE = False


def _most_recent_event_within(series: pd.Series, current_idx: int,
                                recency_bars: int) -> Optional[int]:
    """Return the value of the most-recent non-zero event in `series` if
    it occurred within `recency_bars` of `current_idx`, else None.

    Batch 273 (Tier 2.1 SMC family wiring audit 2026-05-20): SMC library
    has intrinsic detection lag from swing-confirmation requirement.
    Using tail(N) for "recently active" base signals (BOS/CHOCH/OB/
    liquidity) misses events because detection happens 20-80 bars after
    the event itself. This helper finds the last non-zero event by index
    and checks recency relative to current_idx instead of relative to
    the tail. Per empirical sweep on AAPL (1255 bars, swing_length=20):
    a 90-bar recency window catches the most-recent BOS in ~30% of days
    (vs ~0% with a 5-bar tail).
    """
    nonzero = series[series.fillna(0) != 0]
    if nonzero.empty:
        return None
    last_event_idx = nonzero.index[-1]
    if current_idx - last_event_idx > recency_bars:
        return None
    return nonzero.iloc[-1]


def compute_smc_signals(
    ohlc: pd.DataFrame,
    swing_length: int = 20,
    fvg_lookback: int = 5,
    liquidity_range_pct: float = 0.01,
    dealing_range_lookback: int = 50,
    event_recency_bars: int = 90,
    ticker: Optional[str] = None,
    skip_primitives: Optional[set] = None,
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
    # B1038 (2026-06-27) Council 131 Option-A: SMC_PHASE B-CANARY short-
    # circuit. Per DEC-508 + C-1 declaration: 18 SMC strategies are de-
    # facto disabled in production (vendored smartmoneyconcepts not
    # installed in AWS user-data; B416 root cause H1 confirmed via Phase
    # C smoke 2026-06-27). Flag formalizes the state. Owner promotes
    # to "PRODUCTION" via single-line edit when Phase C 8 sign-off items
    # complete (per C-1 declaration doc).
    try:
        from backtest.config import SMC_PHASE
        if SMC_PHASE != "PRODUCTION":
            return {}
    except Exception:
        # Fail-safe: config missing -> behave as B-CANARY
        return {}
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
    # B555 OPT-C Phase 4: when ticker provided + USE_SMC_PANEL_CACHE flag
    # ON + cache primed for this ticker, read the 6 SMC primitives from
    # the cache (sliced respecting PIT lookahead) instead of calling the
    # vendored library per-call. Cache MISS falls back to per-call compute
    # for back-compat.
    _cached_primitives = None
    if ticker is not None:
        try:
            from backtest.config import USE_SMC_PANEL_CACHE
        except Exception:
            USE_SMC_PANEL_CACHE = False
        if USE_SMC_PANEL_CACHE:
            try:
                from backtest.signals.smc_panel_cache import get_primitives_at
                _cached_primitives = get_primitives_at(
                    ticker, current_idx, swing_length=swing_length,
                )
            except Exception as _e:
                log_silent_failure("smc_ict.cache_lookup", _e)
                _cached_primitives = None
    # FVG: Bullish (1) / Bearish (-1) / no FVG (0). Library also exposes
    # Top / Bottom / MitigatedIndex columns enabling retest / inverse logic.
    fvg_df = None
    try:
        # B555 OPT-C: cache-first dispatch
        # B1569: 28.1pct of SMC primitive cost. Skipped -> empty frame ->
        # the column guards below emit nothing, and GuardedSignals raises if
        # anything actually reads a key we chose not to compute.
        if skip_primitives and "fvg" in skip_primitives:
            fvg_df = pd.DataFrame()
        elif _cached_primitives is not None and "fvg" in _cached_primitives:
            fvg_df = _cached_primitives["fvg"]
        else:
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
                # Batch 556 OPT-C Phase 4 producer fix: filter to non-zero
                # FVG events FIRST then tail(20). Pre-fix tail(50) of
                # OHLCV-aligned rows catches mostly NaN rows. FVG is denser
                # than OB so impact smaller, but apply for consistency
                # with B556 OB + B390 liquidity patterns.
                fvg_events = fvg_df[fvg_df["FVG"].fillna(0) != 0]
                tail = fvg_events.tail(20) if not fvg_events.empty else fvg_df.iloc[0:0]
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
                    # B1137 (2026-07-03 Council 251 LOOSEN per Turn 3):
                    # Widen FVG un-mitigated zone entry tolerance ~2% each
                    # side of strict bot/top boundary. Original strict zone
                    # matches were rare; widening captures near-zone retests
                    # that ICT canonical would count. Expected 2-3x uplift
                    # on smc_fvg_retest_long/short.
                    zone_width = float(top) - float(bot)
                    tolerance = zone_width * 0.20  # B1137: 20% padding each side
                    in_zone = (
                        close >= float(bot) - tolerance
                        and close <= float(top) + tolerance
                    )
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
    except Exception as _e:
        log_silent_failure("smc_ict.fvg_compute", _e)
    try:
        # B555 OPT-C: cache-first dispatch
        if _cached_primitives is not None and "swings" in _cached_primitives:
            swings = _cached_primitives["swings"]
        else:
            swings = _smc.swing_highs_lows(ohlc, swing_length=swing_length)
        # Order blocks (with Top/Bottom/MitigatedIndex for breaker /
        # mitigation logic)
        try:
            if _cached_primitives is not None and "ob" in _cached_primitives:
                ob_df = _cached_primitives["ob"]
            else:
                ob_df = _smc.ob(ohlc, swings)
            if "OB" in ob_df.columns:
                # Batch 273: use event_recency_bars instead of fvg_lookback
                # (OB detection lags by ~swing_length bars, so 5-bar tail
                # never catches an OB; 90-bar recency catches ~30% per audit)
                ob_recent_val = _most_recent_event_within(
                    ob_df["OB"], current_idx, event_recency_bars)
                out["smc_ob_bullish_active"] = bool(ob_recent_val == 1)
                out["smc_ob_bearish_active"] = bool(ob_recent_val == -1)
                if "Top" in ob_df.columns and "Bottom" in ob_df.columns:
                    breaker_bull = False
                    breaker_bear = False
                    mitigation_long = False
                    mitigation_short = False
                    # Batch 556 OPT-C Phase 4 producer fix (mirrors Batch 390
                    # liquidity fix): OB events are SPARSE in the OHLCV-aligned
                    # DataFrame (empirical: ~2 events per 500 bars on AAPL).
                    # tail(50) catches 0-1 actual events; filter to non-zero
                    # OB rows FIRST, then take last 20 ACTUAL events. Keep
                    # the same "current_idx - swing_safe" PIT slicing implicit
                    # in iloc bounds (rows beyond current_idx aren't here).
                    ob_events = ob_df[ob_df["OB"].fillna(0) != 0]
                    tail = ob_events.tail(20) if not ob_events.empty else ob_df.iloc[0:0]
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
        except Exception as _e:
            log_silent_failure("smc_ict.order_block_compute", _e)
        # BOS / CHoCH with Level for retest logic
        bos_df = None
        try:
            # B1569: 18.1pct of SMC primitive cost.
            if skip_primitives and "bos_choch" in skip_primitives:
                bos_df = pd.DataFrame()
            elif _cached_primitives is not None and "bos_choch" in _cached_primitives:
                bos_df = _cached_primitives["bos_choch"]
            else:
                bos_df = _smc.bos_choch(ohlc, swings)
            if "BOS" in bos_df.columns:
                # Batch 273: BOS detection requires swing confirmation
                # which lags by 20-80 bars. Tail(5) misses 100% of events;
                # event_recency_bars (default 90) catches ~30% per audit.
                bos_val = _most_recent_event_within(
                    bos_df["BOS"], current_idx, event_recency_bars)
                out["smc_bos_bullish"] = bool(bos_val == 1)
                out["smc_bos_bearish"] = bool(bos_val == -1)
            if "CHOCH" in bos_df.columns:
                choch_val = _most_recent_event_within(
                    bos_df["CHOCH"], current_idx, event_recency_bars)
                out["smc_choch_bullish"] = bool(choch_val == 1)
                out["smc_choch_bearish"] = bool(choch_val == -1)
            # Batch 216: BOS retest - price within 0.5pct of a recently-
            # broken BOS Level. Scan last 50 BOS strikes.
            if "BOS" in bos_df.columns and "Level" in bos_df.columns:
                # Batch 556 OPT-C Phase 4 producer fix: filter to non-zero
                # BOS events FIRST. tail(50) of OHLCV-aligned df catches
                # ~1-2 actual BOS events on AAPL; filter-then-tail(20)
                # catches 20 actual breaks for retest evaluation.
                bos_events = bos_df[bos_df["BOS"].fillna(0) != 0]
                tail = bos_events.tail(20) if not bos_events.empty else bos_df.iloc[0:0]
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
        except Exception as _e:
            log_silent_failure("smc_ict.bos_choch_compute", _e)
        # Liquidity sweeps (with Swept flag exposing equal-highs/lows
        # taken-out events explicitly)
        try:
            if _cached_primitives is not None and "liquidity" in _cached_primitives:
                liq_df = _cached_primitives["liquidity"]
            else:
                liq_df = _smc.liquidity(ohlc, swings, range_percent=liquidity_range_pct)
            if "Liquidity" in liq_df.columns:
                # Batch 273: same liquidity-detection-lag fix as BOS/OB.
                liq_val = _most_recent_event_within(
                    liq_df["Liquidity"], current_idx, event_recency_bars)
                out["smc_liquidity_swept_up"] = bool(liq_val == 1)
                out["smc_liquidity_swept_dn"] = bool(liq_val == -1)
                # Batch 216: equal-highs / equal-lows sweep - liquidity
                # primitive with Swept flag set TRUE in recent bars.
                if "Swept" in liq_df.columns:
                    tail = liq_df.tail(fvg_lookback)
                    # Batch 390 (owner directive 2026-05-26): producer fix.
                    # PRIOR BUG: tail(50) sliced last 50 rows of OHLCV-aligned
                    # liquidity df, but liquidity events are SPARSE (1 in
                    # 500 rows on AAPL example; events at swing highs/lows
                    # only). tail(50) almost always missed them entirely
                    # -> smc_equal_highs_swept / lows_swept never True
                    # (0/1542 ticker-days x 10 tickers x 4y empirical).
                    # FIX: filter to liquidity-event rows FIRST, take last
                    # 20 ACTUAL EVENTS, then check Swept (bar-index float;
                    # non-null = swept). Also require the sweep happened
                    # within the last 50 bars to keep "recent" semantics.
                    eq_highs_swept = False
                    eq_lows_swept = False
                    liq_events = liq_df[
                        liq_df["Liquidity"].notna() & (liq_df["Liquidity"] != 0)
                    ]
                    if not liq_events.empty:
                        recent_events = liq_events.tail(20)
                        for idx_pos in range(len(recent_events)):
                            row = recent_events.iloc[idx_pos]
                            liq_val = row.get("Liquidity")
                            swept_val = row.get("Swept")
                            if pd.isna(swept_val):
                                continue  # not yet swept
                            # Swept is a bar index float; "recent" = within
                            # last 50 bars of current
                            if (current_idx - float(swept_val)) > 50:
                                continue
                            if liq_val == 1:
                                eq_highs_swept = True
                            elif liq_val == -1:
                                eq_lows_swept = True
                    out["smc_equal_highs_swept"] = eq_highs_swept
                    out["smc_equal_lows_swept"]  = eq_lows_swept
        except Exception as _e:
            log_silent_failure("smc_ict.liquidity_compute", _e)
        # Batch 216: retracements primitive for OTE (Optimal Trade Entry)
        # 62-79% Fibonacci zone after CHoCH.
        try:
            # B1569: 46.7pct of SMC primitive cost -- the single largest.
            if skip_primitives and "retracements" in skip_primitives:
                ret_df = pd.DataFrame()
            elif _cached_primitives is not None and "retracements" in _cached_primitives:
                ret_df = _cached_primitives["retracements"]
            else:
                ret_df = _smc.retracements(ohlc, swings)
            if (
                "Direction" in ret_df.columns
                and "CurrentRetracement%" in ret_df.columns
            ):
                direction = ret_df["Direction"].iloc[-1]
                cur_ret = ret_df["CurrentRetracement%"].iloc[-1]
                if not pd.isna(direction) and not pd.isna(cur_ret):
                    # B1137 (2026-07-03 Council 251 LOOSEN per Turn 3):
                    # Fib band 62-79% -> 60-82% per ICT canonical variance
                    # (Michael J. Huddleston canonical sources use 61.8-78.6%
                    # narrow; some ICT variants use 60-82% wider). Widen to
                    # match wider variant per feedback_never_use_NOT_s_get.
                    in_ote = 60.0 <= float(cur_ret) <= 82.0  # B1137: was 62.0 - 79.0
                    out["smc_ote_long_zone"]  = bool(in_ote and float(direction) > 0)
                    out["smc_ote_short_zone"] = bool(in_ote and float(direction) < 0)
                    out["smc_retracement_pct"] = round(float(cur_ret), 2)
        except Exception as _e:
            log_silent_failure("smc_ict.retracement_compute", _e)
    except Exception as _e:
        log_silent_failure("smc_ict.swing_highs_lows_compute", _e)
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
                # B1137 (2026-07-03 Council 251 LOOSEN per Turn 3): widen
                # discount/premium zone thresholds 0.5 -> 0.6/0.4 symmetric
                # per Turn 3 verdict. Original strict 0.5 boundary excluded
                # near-midpoint prices from BOTH zones. Widen so 0-0.6 =
                # discount + 0.4-1.0 = premium (overlap 0.4-0.6 is transition).
                # Expected 3-5x uplift on smc_discount_long + smc_premium_short.
                out["smc_in_discount_zone"]  = pct < 0.6  # B1137: was < 0.5
                out["smc_in_premium_zone"]   = pct > 0.4  # B1137: was > 0.5
    except Exception as _e:
        log_silent_failure("smc_ict.dealing_range_compute", _e)
    return out
