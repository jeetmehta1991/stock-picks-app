"""Index rebalance signals (Batch 251 / DEC-370).

Phase 1C+ Wave 1 final module per owner directive 2026-05-19. Parallel-safe
with Phase 1A-alpha procs (NEW file, no engine touch).

Implements three documented index-rebalance effects:

1. **S&P 500 inclusion drift (Shleifer 1986; Lynch-Mendenhall 1997 *JoB*;
   Petajisto 2011 *JF*):** stocks added to S&P 500 experience ~5-10% pop
   in announcement-to-effective-date window; effect persists ~30-45 days
   post-inclusion, then partially reverses (Beneish-Whaley 1996).

2. **S&P 500 deletion drift (Chen-Noronha-Singal 2004 *RFS*):** stocks
   removed experience -3% to -10% in announcement-to-effective-date
   window. Reversal slower than inclusions.

3. **Russell reconstitution (annual late June; Cai-Houge 2008 *FAJ*):**
   stocks moving Russell 1000 <-> Russell 2000 boundary have predictable
   pre-rebalance positioning (front-running by index funds).

Daily-bar implementation: reads `data_prefetch/derived/index_rebalance_events.parquet`
(populated by Sprint 5 prefetch DEC-380 corp actions feed). Schema:
  ticker, event_date, event_type (s&p_add / s&p_drop / russell_add /
  russell_drop / ndx_add / ndx_drop), announce_date, effective_date.

Graceful no-op when prefetch missing (returns empty dict; strategies
fire 0 trades until Sprint 5 data lands).
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd


_EVENTS_PATH = (
    Path(__file__).parent.parent.parent
    / "data_prefetch" / "derived" / "index_rebalance_events.parquet"
)

# Drift window per literature
_POST_INCLUSION_DRIFT_DAYS = 45      # Petajisto 2011: 30-45 day window
_POST_DELETION_DRIFT_DAYS = 30
_PRE_REBALANCE_WINDOW_DAYS = 10      # front-running by index funds
_REVERSAL_WINDOW_START_DAYS = 60     # Beneish-Whaley 1996 reversal onset

# Batch 315a (2026-05-24): module-level cached load. Phase 1A-beta calls
# compute_index_rebalance_signals 1937 tkrs * 1044 days = ~2M times. Pre-fix:
# each call did Path.exists() + open the parquet (when present). Post-fix:
# load once at first call, reuse the cached DataFrame for the rest of the
# session. Reduces ~2M filesystem probes to 1 + ~2M dict lookups.
# Behavior preserved: when data missing, _CACHED_EVENTS remains empty -> all
# callers see the same empty-dict return path as before.
_CACHED_EVENTS: pd.DataFrame | None = None


def _load_events() -> pd.DataFrame:
    """Load index rebalance events parquet (module-level cached).

    First call: probe filesystem, parse + normalize the parquet if present.
    Subsequent calls: return cached DataFrame.
    Behavior is identical to the pre-Batch-315a per-call load.
    """
    global _CACHED_EVENTS
    if _CACHED_EVENTS is not None:
        return _CACHED_EVENTS
    if not _EVENTS_PATH.exists():
        _CACHED_EVENTS = pd.DataFrame(columns=[
            "ticker", "event_date", "event_type", "announce_date", "effective_date",
        ])
        return _CACHED_EVENTS
    try:
        df = pd.read_parquet(_EVENTS_PATH)
        if not df.empty:
            for col in ("event_date", "announce_date", "effective_date"):
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
        _CACHED_EVENTS = df
        return _CACHED_EVENTS
    except Exception:
        _CACHED_EVENTS = pd.DataFrame()
        return _CACHED_EVENTS


def compute_index_rebalance_signals(ticker: str, as_of: date) -> dict:
    """Compute per-ticker per-as_of index rebalance signals.

    Returns dict with keys (all optional; absent when data missing):
      - within_post_inclusion_window:  bool (T+0..T+45 after S&P/Russell add)
      - days_since_inclusion:          int
      - within_post_deletion_window:   bool (T+0..T+30 after S&P/Russell drop)
      - days_since_deletion:           int
      - within_pre_rebalance_window:   bool (T-10..T-0 before known event)
      - days_to_rebalance:             int
      - in_reversal_window:            bool (T+60..T+120 after S&P add)
      - last_event_type:               str (s&p_add / s&p_drop / etc.)

    Graceful no-op when prefetch missing.
    """
    events = _load_events()
    if events.empty or ticker not in events.get("ticker", pd.Series()).values:
        return {}
    mine = events[events["ticker"] == ticker].copy()
    out: dict = {}

    # Past events (announcement or effective date <= as_of)
    past = mine[mine["effective_date"].apply(lambda d: pd.notna(d) and d <= as_of)]
    if not past.empty:
        last = past.sort_values("effective_date").iloc[-1]
        last_eff = last["effective_date"]
        days_since = (as_of - last_eff).days
        out["last_event_type"] = str(last.get("event_type", ""))

        if "add" in out["last_event_type"]:
            out["days_since_inclusion"] = days_since
            out["within_post_inclusion_window"] = (0 <= days_since <= _POST_INCLUSION_DRIFT_DAYS)
            out["in_reversal_window"] = (
                _REVERSAL_WINDOW_START_DAYS <= days_since <= _REVERSAL_WINDOW_START_DAYS + 60
            )
        elif "drop" in out["last_event_type"]:
            out["days_since_deletion"] = days_since
            out["within_post_deletion_window"] = (0 <= days_since <= _POST_DELETION_DRIFT_DAYS)

    # Future events (effective_date > as_of, within window)
    future = mine[mine["effective_date"].apply(lambda d: pd.notna(d) and d > as_of)]
    if not future.empty:
        next_event = future.sort_values("effective_date").iloc[0]
        days_to = (next_event["effective_date"] - as_of).days
        out["days_to_rebalance"] = days_to
        out["within_pre_rebalance_window"] = (0 < days_to <= _PRE_REBALANCE_WINDOW_DAYS)

    return out


def _strat_signal(fires: bool, direction: str, category: str,
                   signals_used: list, bullets: list) -> dict:
    """Mirror of screener._strat helper (avoid circular import)."""
    return {
        "fires":           bool(fires),
        "direction":       direction,
        "category":        category,
        "signals_used":    signals_used,
        "context_bullets": bullets,
    }


def strat_post_inclusion_drift_long(s: dict) -> dict:
    """DEC-370 #1: ride the post-S&P-500-inclusion drift (T+0..T+45).
    Shleifer 1986 / Lynch-Mendenhall 1997 / Petajisto 2011."""
    fires = (
        s.get("within_post_inclusion_window", False)
        and "add" in str(s.get("last_event_type", ""))
        and s.get("price_above_ema_200", True)
    )
    dse = s.get("days_since_inclusion", 0)
    return _strat_signal(fires, "long", "index_rebalance",
        ["within_post_inclusion_window", "price_above_ema_200"],
        [f"Day +{dse} of post-{s.get('last_event_type', 'add')} window",
         "Shleifer 1986 / Petajisto 2011 inclusion drift",
         "Above 200 EMA (regime gate)"])


def strat_post_inclusion_reversal_short(s: dict) -> dict:
    """DEC-370 #1b: fade the inclusion pop reversal (T+60..T+120).
    Beneish-Whaley 1996 documents partial reversal post-inclusion."""
    fires = (
        s.get("in_reversal_window", False)
        and "add" in str(s.get("last_event_type", ""))
    )
    dse = s.get("days_since_inclusion", 0)
    return _strat_signal(fires, "short", "index_rebalance",
        ["in_reversal_window", "post_add_event"],
        [f"Day +{dse} in reversal window (Beneish-Whaley 1996)",
         "Fade post-inclusion overshoot",
         f"Last event: {s.get('last_event_type', '')}"])


def strat_post_deletion_drift_short(s: dict) -> dict:
    """DEC-370 #2: short post-deletion drift (T+0..T+30).
    Chen-Noronha-Singal 2004 RFS."""
    fires = (
        s.get("within_post_deletion_window", False)
        and "drop" in str(s.get("last_event_type", ""))
        and not s.get("price_above_ema_200", True)
    )
    dse = s.get("days_since_deletion", 0)
    return _strat_signal(fires, "short", "index_rebalance",
        ["within_post_deletion_window", "price_below_ema_200"],
        [f"Day +{dse} of post-{s.get('last_event_type', 'drop')} window",
         "Chen-Noronha-Singal 2004 deletion drift",
         "Below 200 EMA (bear regime confirmation)"])


def strat_pre_rebalance_long(s: dict) -> dict:
    """DEC-370 #3: pre-Russell-rebalance long for known additions.
    Cai-Houge 2008: index-fund front-running creates ~3-5% lift in
    T-10..T-0 window. Requires announce_date already known."""
    fires = (
        s.get("within_pre_rebalance_window", False)
        and s.get("days_to_rebalance", 0) > 0
    )
    dt = s.get("days_to_rebalance", 0)
    return _strat_signal(fires, "long", "index_rebalance",
        ["within_pre_rebalance_window"],
        [f"T-{dt} until announced rebalance",
         "Cai-Houge 2008 index-fund front-running pattern",
         "Pre-rebalance positioning"])
