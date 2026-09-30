"""S6-B3134a (B3135, owner-approved A + C 2026-09-29): point-in-time screen
eligibility - ONE definition for the engine's screen (backtest.py
_process_day), the grader-side leak guard (scripts/eligibility_leak.py) and
the label re-score. Two readings of "eligible" drift; one cannot (L593).

THE TWO LEAKS THIS CLOSES (measured on R5, output_r5_merged_1_7):
  M1  year-granular eligibility - the set was built once per year at Jan 1
      (backtest.py _build_liquid_universe), so a mid-year index removal or a
      collapse below min_price stayed screenable to the next Jan 1 (SBNY:
      321 entries 2023-03-30..2023-12-29 after its 2023-03-15 removal).
  M2  the open-trade carry - every ticker with an open trade was added to
      the day's price dict for EXIT checks (BUG-287) and the screen then
      screened that same dict for NEW entries: 7,097 of 189,471 R5 trades
      (5,063 not-in-PIT / 1,915 20-bar volume / 119 price), 7,097 of 7,097
      with a same-ticker trade already open that morning.

MODES (backtest.config.ENGINE_ELIGIBILITY_MODE):
  daily_subtract_v1  eligible TODAY = in the year's Jan-1 set AND (a T1a
                     ticker) a PIT S&P member today, or (any other
                     ticker, S6-B3136c) PIT-active in at least one tier
                     today, AND today's close >= min_price.
                     SUBTRACT-ONLY by design: it never admits a
                     ticker the Jan-1 set excluded - mid-year additions
                     (index joiners, recoveries above the floors) are a
                     universe change put to the owner separately
                     (S6-B3134a: measured +15,737 ticker-days on 104 tickers).
                     Carried tickers are exit-checked only, never screened.
  jan1_legacy        the pre-B3135 screen (year-start set, carried tickers
                     screened) - kept ONLY to reproduce historical cubes.
"""
from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

MODE_DAILY = "daily_subtract_v1"
MODE_LEGACY = "jan1_legacy"
MODES = (MODE_DAILY, MODE_LEGACY)


def jan1_reason(sliced, ticker: str, t1a_master: set, pit_jan1: set,
                min_price: float, min_avg_volume: float) -> str | None:
    """Why `ticker` fails the Jan-1 set (None = it passes). `sliced` is its
    OHLCV up to and including Jan 1. The order and the comparisons are the
    engine's year-set loop verbatim (backtest.py _build_liquid_universe)."""
    if len(sliced) < 30:
        return "history<30"
    if float(sliced["close"].iloc[-1]) < min_price:
        return "price<min"
    if float(sliced["volume"].tail(20).mean()) < min_avg_volume:
        return "avgvol<min"
    if t1a_master and ticker in t1a_master and ticker not in pit_jan1:
        return "not-in-PIT"
    return None


def daily_reason(ticker: str, close_today: float, t1a_master: set,
                 pit_today: set, min_price: float, *,
                 tiers_today: set) -> str | None:
    """Why a ticker ALREADY in its Jan-1 set is not screenable today under
    daily_subtract_v1 (None = screenable). Membership: S&P convention, out on
    the removal date itself (universe._filter_pit). S6-B3136c (owner ruling
    2026-09-29, '8 approve your recommendation'): a ticker the T1a rule does
    not judge (outside the master, or no master loaded) is judged by the
    tier windows instead - screenable only on a day it is PIT-active in at
    least one tier (`tiers_today`, DailyTiers.members). A REQUIRED keyword:
    a caller that forgets it fails loudly rather than skipping the rule."""
    t1a_rule = bool(t1a_master) and ticker in t1a_master
    if t1a_rule and ticker not in pit_today:
        return "not-member-today"
    if not t1a_rule and ticker.upper() not in tiers_today:
        return "no-tier-today"
    if close_today < min_price:
        return "close<min-today"
    return None


def screen_input(ohlcv_pit: dict, screenable: set, mode: str) -> dict:
    """The dict the SCREEN reads. ohlcv_pit also carries every open-trade
    ticker for EXIT checks (BUG-287); under daily_subtract_v1 only the
    screenable ones pass (the M2 carry fix), under jan1_legacy the whole
    dict (the pre-B3135 input, carried tickers included)."""
    if check_mode(mode) == MODE_LEGACY:
        return ohlcv_pit
    return {t: v for t, v in ohlcv_pit.items() if t in screenable}


def check_mode(mode: str) -> str:
    """Fail closed on an unknown mode - an unreadable screen rule is not the
    legacy one (L642)."""
    if mode not in MODES:
        raise ValueError(f"ENGINE_ELIGIBILITY_MODE={mode!r} is not one of {MODES}")
    return mode


STAMP = "eligibility_mode.json"


def stamp_doc(mode: str, tier_coverage: dict | None = None) -> dict:
    """The stamp the engine writes on every cube it builds. A daily-mode
    run also records each tier file's stated coverage against the run's
    end (S6-B3136c, B3139); readers read only "mode" (read_stamp)."""
    doc = {"mode": check_mode(mode),
           "defined_in": "backtest/data/eligibility.py",
           "ticket": "S6-B3134a"}
    if tier_coverage is not None:
        doc["tier_coverage"] = tier_coverage
    return doc


def read_stamp(cube_dir) -> str | None:
    """The mode a cube's stamp records, or None when it carries no stamp (a
    cube built before B3135). A stamp that exists but cannot be read, or
    names an unknown mode, RAISES - an unreadable rule is not the legacy one
    (L642)."""
    p = Path(cube_dir) / STAMP
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    mode = doc.get("mode") if isinstance(doc, dict) else None
    if mode not in MODES:
        raise ValueError(f"{p}: stamp mode {mode!r} is not one of {MODES}")
    return mode


def built_mode(stamp_mode: str | None) -> str:
    """The rule a cube's rows were screened under. No stamp = the pre-B3135
    engine = jan1_legacy by construction."""
    return MODE_LEGACY if stamp_mode is None else check_mode(stamp_mode)


def check_resume(stamp_mode: str | None, mode: str) -> str:
    """A resumed run continues under the rule its checkpoint was built with,
    or refuses: one cube, one screen rule. Returns the mode to run."""
    built = built_mode(stamp_mode)
    if built != check_mode(mode):
        raise RuntimeError(
            f"S6-B3134a: refusing to resume a cube built under {built!r} "
            f"({'no stamp - a pre-B3135 cube' if stamp_mode is None else 'its stamp'})"
            f" with ENGINE_ELIGIBILITY_MODE={mode!r}: rows screened by two "
            f"rules would be graded as one cube. Resume with "
            f"ENGINE_ELIGIBILITY_MODE={built}, or start a fresh cube.")
    return mode


# B3139 (S6-B3136c council): the fixed-date positive control this file
# carried (TIER_CONTROL_DATE, a CHOSEN date) is REPLACED by the per-tier
# file check in DailyTiers - a date inside every file's window proved the
# files readable on that one day and said nothing about a file that lost
# its window columns (_filter_pit then reads EVERY row as active).


class DailyTiers:
    """S6-B3136c: per-day union of every tier's PIT window
    (universe.tickers_in_any_tier), asked once per calendar date. With no
    injected `fn` the constructor runs the PER-TIER FILE CHECK (B3139,
    council; it replaced a fixed-date control): every tier file must exist,
    read, carry Symbol rows and - windowed tiers - added_date/removed_date
    (universe.tier_file_problems). A loader answers [] for a missing file,
    which would subtract a whole tier from the screen, and a file without
    its window columns reads as all-active - either REFUSES, naming the
    tier (L642). With `run_end` it also records each file's stated coverage
    month against the run's end (`coverage`, written into the cube's
    stamp) and warns on a run past a file's stated end. MEASURED B3139: one
    tickers_in_any_tier call costs 25.2 ms, ~25 s per 1,004-day run."""

    def __init__(self, fn=None, run_end=None):
        self.coverage = None
        if fn is None:
            from backtest.data import universe as _u
            bad = _u.tier_file_problems()
            if bad:
                raise RuntimeError(
                    f"S6-B3136c: tier file check failed for {sorted(bad)} - "
                    + "; ".join(f"{t}: {r}" for t, r in sorted(bad.items()))
                    + ". Refusing rather than subtract a whole tier from the "
                    "screen or read an unwindowed file as always-active (L642).")
            if run_end is not None:
                self.coverage = _u.tier_coverage(run_end)
                past = sorted(t for t, c in self.coverage.items()
                              if c["status"] == "past")
                if past:
                    logger.warning(
                        "S6-B3136c: the run ends %s, PAST the stated coverage of "
                        "tier file(s) %s - membership after a file's stated end "
                        "is not covered by it (recorded in the cube's stamp)",
                        run_end, past)
            fn = _u.tickers_in_any_tier
        self._fn = fn
        self._cache: dict[date, set] = {}

    def members(self, d: date) -> set:
        if d not in self._cache:
            self._cache = {d: {str(t).upper() for t in self._fn(d)}}
        return self._cache[d]


class DailyPit:
    """Per-day S&P membership, asked of get_sp500_constituents_pit once per
    calendar date (one definition of 'member on day D'; the CSV is read at
    most once per simulated day)."""

    def __init__(self, fn=None):
        if fn is None:
            from backtest.data.universe import get_sp500_constituents_pit as fn
        self._fn = fn
        self._cache: dict[date, set] = {}

    def members(self, d: date) -> set:
        if d not in self._cache:
            self._cache = {d: set(self._fn(d))}      # one day in memory
        return self._cache[d]
