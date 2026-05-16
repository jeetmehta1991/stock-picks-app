"""Circuit breaker logic — DEC-515 Pass 53 Day-9-evening engine compliance.

Per DEC-515 (Pass 53 owner-approved 2026-05-06 Q1 P0 CRITICAL gap):
  Level 1: Single-day -1% portfolio   → soft pause (halve sizes 1d)
  Level 2: Single-day -2% portfolio   → soft pause (halve sizes 2d)
  Level 3: Intraday -7% from open     → intraday halt (NYSE Rule 80B-1)
  Level 4: Intraday -13% from open    → extended halt (NYSE Rule 80B-2)
  Level 5: Intraday -20% from open    → market halt (NYSE Rule 80B-3)
  Level 6: Portfolio DD-from-peak ≥X% → halt new entries until peak +Y%
                                        (Pass 53 NEW per DEC-515)

Per DEC-586 priority order (Pass 53 fix): Level 6 → 5 → 4 → 3 → 2 → 1
(most-severe first; sequential check per DEC-315).

Per L149 spec-without-build: DEC-515 spec'd Pass 53 turn 2026-05-06 (~2 days
ago) but engine had no Level 6 implementation. This module closes the gap
per DEC-594 same-commit rule.

Status: PARTIAL-SPEC-ONLY (engine) → RESOLVED-DECIDED post artifact landing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional


# DEC-515 Level 6 default thresholds - REVISIT_AFTER_BACKTEST per DEC-581
# Class B Bonferroni-corrected tuning post-Phase-1B-alpha empirical results.
# Batch 193 (Phase 1A baseline regression) owner-approved 2026-05-16
# Option B: relax thresholds + add hard-stop timeout. Pre-Batch-193 the halt
# was a permanent freeze (resume condition "halt_equity * 1.05" was
# unreachable once halted because no new entries are permitted; only existing
# open positions could lift equity, which they cannot reliably do off the
# halt-level). Phase 1A Batch 192 baseline trapped 4 years of trading
# behind a single halt fired on 2022-06-16. Post-Batch-193 the halt is a
# temporary pause, not a freeze.
LEVEL_6_DD_HALT_THRESHOLD = 0.20      # 20% portfolio DD-from-peak triggers halt (matches Passing-Criteria #5 max DD)
LEVEL_6_RECOVERY_THRESHOLD = 0.025    # peak must recover 2.5% above halt-level to resume early
LEVEL_6_MIN_PEAK_HISTORY_DAYS = 30    # require >=30 days of peak history before activation
LEVEL_6_MAX_HALT_DURATION_DAYS = 60   # hard-stop auto-resume timeout (regardless of recovery threshold)


@dataclass
class Level6State:
    """State for Level 6 portfolio DD-from-peak circuit breaker."""
    rolling_peak_equity: float = 0.0
    halt_triggered: bool = False
    halt_triggered_date: Optional[date] = None
    halt_equity: float = 0.0
    target_resume_equity: float = 0.0
    halt_log: List[dict] = field(default_factory=list)


def update_level_6_state(
    state: Level6State,
    current_equity: float,
    as_of: date,
    dd_threshold: float = LEVEL_6_DD_HALT_THRESHOLD,
    recovery_threshold: float = LEVEL_6_RECOVERY_THRESHOLD,
    min_history_days: int = LEVEL_6_MIN_PEAK_HISTORY_DAYS,
    days_since_start: int = 0,
    max_halt_duration_days: int = LEVEL_6_MAX_HALT_DURATION_DAYS,
) -> Dict[str, object]:
    """Update Level 6 state with today's portfolio equity.

    Returns dict with:
      - halt_active: bool (True = no new entries permitted)
      - dd_from_peak: float (current DD as decimal, e.g. -0.12 for -12%)
      - rolling_peak_equity: float
      - event: 'halt_triggered' | 'halt_resumed' | 'halt_resumed_timeout' | None

    Logic:
      1. Update rolling peak (peak = max(peak, current_equity)).
      2. Compute dd_from_peak = (current_equity - peak) / peak.
      3. If not halted:
           - If dd_from_peak <= -dd_threshold AND days_since_start >= min_history_days
             -> trigger halt; record halt_equity + target_resume_equity.
      4. If halted:
           - If current_equity >= target_resume_equity -> resume (clear halt flag).
           - ELSE if (as_of - halt_triggered_date).days >= max_halt_duration_days
             -> auto-resume via timeout (Batch 193 off-ramp). Required because
             the halt itself blocks new entries, so existing positions must
             deliver the recovery on their own; if they cannot within
             max_halt_duration_days, force release rather than freeze
             indefinitely (Phase 1A Batch 192 trapped 4 years behind a single
             halt fired on 2022-06-16).
    """
    event: Optional[str] = None

    # Update rolling peak
    if current_equity > state.rolling_peak_equity:
        state.rolling_peak_equity = current_equity

    # Compute DD from peak
    if state.rolling_peak_equity > 0:
        dd_from_peak = (current_equity - state.rolling_peak_equity) / state.rolling_peak_equity
    else:
        dd_from_peak = 0.0

    # Halt logic
    if not state.halt_triggered:
        if (dd_from_peak <= -dd_threshold
                and days_since_start >= min_history_days):
            state.halt_triggered = True
            state.halt_triggered_date = as_of
            state.halt_equity = current_equity
            # Resume when current_equity >= halt_equity * (1 + recovery_threshold)
            # i.e. recovery off the halt-level
            state.target_resume_equity = current_equity * (1 + recovery_threshold)
            state.halt_log.append({
                "date": as_of,
                "event": "halt_triggered",
                "dd_from_peak": round(dd_from_peak, 4),
                "halt_equity": current_equity,
                "rolling_peak_equity": state.rolling_peak_equity,
                "target_resume_equity": state.target_resume_equity,
            })
            event = "halt_triggered"
    else:
        # Halted - check resume condition (recovery threshold OR timeout)
        if current_equity >= state.target_resume_equity:
            state.halt_triggered = False
            state.halt_log.append({
                "date": as_of,
                "event": "halt_resumed",
                "current_equity": current_equity,
                "resume_threshold": state.target_resume_equity,
            })
            event = "halt_resumed"
        elif (state.halt_triggered_date is not None
                and (as_of - state.halt_triggered_date).days >= max_halt_duration_days):
            # Batch 193 timeout off-ramp: halt auto-releases after
            # max_halt_duration_days regardless of recovery threshold.
            state.halt_triggered = False
            state.halt_log.append({
                "date": as_of,
                "event": "halt_resumed_timeout",
                "current_equity": current_equity,
                "resume_threshold": state.target_resume_equity,
                "halt_triggered_date": state.halt_triggered_date,
                "halt_duration_days": (as_of - state.halt_triggered_date).days,
            })
            event = "halt_resumed_timeout"

    return {
        "halt_active": state.halt_triggered,
        "dd_from_peak": round(dd_from_peak, 4),
        "rolling_peak_equity": state.rolling_peak_equity,
        "event": event,
    }


def evaluate_circuit_breakers_priority(
    daily_portfolio_pct: float,
    intraday_low_vs_open_pct: float,
    level_6_state: Level6State,
    current_equity: float,
    as_of: date,
    days_since_start: int,
) -> Dict[str, object]:
    """Sequential circuit-breaker check per DEC-315 + DEC-586 priority (Level 6 → 1).

    Most-severe wins; lower-level breakers don't fire if higher-level already active.

    Args:
        daily_portfolio_pct: today's portfolio return (e.g., -0.025 = -2.5%).
        intraday_low_vs_open_pct: SPY intraday low/open - 1 (e.g., -0.08 = -8%).
        level_6_state: persistent Level 6 state (mutated in place).
        current_equity: today's portfolio equity.
        as_of: today's date.
        days_since_start: days since backtest start (for L6 min_history check).

    Returns:
        {
          "active_breakers": list[int] (active levels by number),
          "highest_level": int | None,
          "level_6_event": str | None,
          "size_multiplier": float (1.0 = full; 0.5 = halved; 0.0 = halt),
        }
    """
    active: List[int] = []

    # Level 6: portfolio DD-from-peak (highest priority new in Pass 53)
    l6 = update_level_6_state(
        level_6_state, current_equity, as_of, days_since_start=days_since_start,
    )
    if l6["halt_active"]:
        active.append(6)

    # Level 5: intraday -20% (NYSE Rule 80B-3)
    if intraday_low_vs_open_pct <= -0.20:
        active.append(5)
    # Level 4: intraday -13%
    elif intraday_low_vs_open_pct <= -0.13:
        active.append(4)
    # Level 3: intraday -7%
    elif intraday_low_vs_open_pct <= -0.07:
        active.append(3)

    # Level 2: daily -2%
    if daily_portfolio_pct <= -0.02:
        active.append(2)
    # Level 1: daily -1%
    elif daily_portfolio_pct <= -0.01:
        active.append(1)

    highest = max(active) if active else None

    # Size multiplier per priority
    if highest is None:
        size_mult = 1.0
    elif highest == 6:
        size_mult = 0.0  # halt new entries
    elif highest in (5, 4, 3):
        size_mult = 0.0  # market halt
    elif highest == 2:
        size_mult = 0.5  # halve 2 days
    elif highest == 1:
        size_mult = 0.5  # halve 1 day
    else:
        size_mult = 1.0

    return {
        "active_breakers": active,
        "highest_level": highest,
        "level_6_event": l6.get("event"),
        "level_6_dd_from_peak": l6.get("dd_from_peak"),
        "size_multiplier": size_mult,
    }
