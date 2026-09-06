"""B2615 (S6-B2611e): ATR for the OFFLINE cube re-scorers - from
signals_at_entry when the engine recorded it, else DERIVED from the OHLCV the
re-scorer has already reloaded, and NEVER a silent 2pct-of-price proxy.

Background (output_audit/b2611 audit, S6-B2611e): scripts/
recompute_cube_from_trade_log.py and scripts/rebuild_cube_from_trade_log.py
both read ``sig.get("atr", entry_price * 0.02)`` - the same crude proxy the
engine's replay path uses at backtest/engine/backtest.py resolve_replay_atr,
but WITHOUT the engine's counter, its >5pct warning, or the
replay_atr_fallback.json the post-config battery's lens review reads
(B1261 / B2574).
A trade log whose signals_at_entry had been wiped (S6-B2512: checkpoint
writers bypassing dumps_signals, fixed B2574) was re-scored on a fabricated
ATR with no trace. CLASS: a fallback that is
observable in one caller and silent in its siblings.

Fix, class-level: one resolver shared by both scripts.
  1. ``signals_at_entry['atr']`` when present and positive  -> ``from_signals``
  2. else ATR-14 derived on the bars UP TO AND INCLUDING entry_date ->
     ``derived``. The engine records ``entry_date = as_of``, the signal bar
     (backtest/engine/backtest.py OpenTrade(entry_date=as_of)), and its
     producer ran on ``df[df.index.date <= as_of]`` (screener.py
     ``_worker_screen_ticker``), so the recorded ATR is ATR-14 through the
     entry_date bar. MEASURED B2615 on the 373 cfg1-rerun trades: with
     bars STRICTLY before entry_date the derivation missed every recorded
     value (median 2.5pct, max 40pct - FTNT 2024-08-07, an earnings gap
     bar); with bars <= entry_date it reproduces them. Same
     ``_atr_series`` (Wilder EWM, alpha=1/14, adjust=False) that
     ``compute_atr_levels`` writes into signals_at_entry, seeded on the
     same first bar when the caller loads the engine's warmup window.
  3. else ``unresolved`` - the trade is NOT scored and the caller fails
     closed (``assert_resolved`` raises) before any cube is written. The
     absent case is the case the guard exists for (L642).

The ENGINE's resolve_replay_atr is deliberately unchanged: its proxy is
counted, warned and surfaced by the battery (run_postconfig.py
replay_atr_proxy_lens FAILs above the 5pct engine threshold - a landing-report
finding), and the wipe that fed it has its own fix (B2574).
"""
from __future__ import annotations

import math
import sys
from datetime import date
from pathlib import Path

import pandas as pd

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from backtest.signals.technical import _atr_series  # noqa: E402

ATR_PERIOD = 14
# compute_atr_levels (technical.py) returns {} below period + 2 bars; the
# derivation holds the same floor so it never invents a value the producer
# would have refused to write.
MIN_BARS = ATR_PERIOD + 2


class ATRUnresolved(RuntimeError):
    """Raised by assert_resolved when any trade has no ATR from either path."""


def new_counters() -> dict:
    return {"total": 0, "from_signals": 0, "derived": 0, "unresolved": 0}


def _bar_dates(df: pd.DataFrame):
    idx = df.index
    if not isinstance(idx, pd.DatetimeIndex):
        idx = pd.to_datetime(idx)
    return idx.date


def derive_atr(df_full: pd.DataFrame, entry_date: date,
               period: int = ATR_PERIOD) -> float | None:
    """ATR-14 through the entry_date bar (bars <= entry_date - the engine's
    entry_date IS the signal bar), or None when fewer than MIN_BARS bars
    exist through it or the value is not finite and positive."""
    if df_full is None or df_full.empty:
        return None
    if hasattr(entry_date, "date") and callable(getattr(entry_date, "date")):
        entry_date = entry_date.date()      # datetime / Timestamp -> date
    hist = df_full[_bar_dates(df_full) <= entry_date]
    if len(hist) < MIN_BARS:
        return None
    try:
        val = float(_atr_series(hist, period).iloc[-1])
    except (KeyError, TypeError, ValueError, IndexError):
        return None
    if not math.isfinite(val) or val <= 0:
        return None
    return val


def resolve_atr(sig, entry_price, df_full: pd.DataFrame, entry_date: date,
                counters: dict, *, period: int = ATR_PERIOD) -> float | None:
    """The one resolver both re-scorers call. Tallies into ``counters`` and
    returns None (never a proxy) when neither path yields an ATR."""
    counters["total"] = counters.get("total", 0) + 1
    if isinstance(sig, dict):
        try:
            v = float(sig.get("atr"))
        except (TypeError, ValueError):
            v = float("nan")    # unparseable recorded atr -> fall through to derive
        if math.isfinite(v) and v > 0:
            counters["from_signals"] = counters.get("from_signals", 0) + 1
            return v
    d = derive_atr(df_full, entry_date, period)
    if d is not None:
        counters["derived"] = counters.get("derived", 0) + 1
        return d
    counters["unresolved"] = counters.get("unresolved", 0) + 1
    return None


def report(counters: dict) -> str:
    t = counters.get("total", 0)
    if t == 0:
        return "replay-ATR (B2615): no trades resolved"
    fs, dv, un = (counters.get(k, 0) for k in ("from_signals", "derived", "unresolved"))
    return (f"replay-ATR (B2615): {fs}/{t} from signals_at_entry, {dv}/{t} derived "
            f"from OHLCV ({dv / t:.1%}), {un}/{t} UNRESOLVED - no proxy path exists")


def assert_resolved(counters: dict, where: str) -> None:
    """Fail closed: any unresolved trade means the cube must not be written."""
    un = counters.get("unresolved", 0)
    if un:
        raise ATRUnresolved(
            f"{where}: {un} of {counters.get('total', 0)} trades have no ATR from "
            f"signals_at_entry and fewer than {MIN_BARS} OHLCV bars before entry - "
            "refusing to write a cube (S6-B2611e: no silent 2pct proxy)")
