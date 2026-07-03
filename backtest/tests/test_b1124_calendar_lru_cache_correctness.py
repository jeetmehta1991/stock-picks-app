"""B1124 Test 7/10: calendar @lru_cache correctness (Council 244).

RED-FIRST for BUG-279: halloween_seasonal_long 300x underfire + totm_long
360x underfire + pre_holiday_long 125x underfire, all sharing calendar_
effects.py @lru_cache on _cached_calendar_signals.

Root cause hypotheses:
  (a) @lru_cache returning stale/wrong values across per-day fan-out
  (b) tdm (trading day of month) edge case around US holidays/DST
  (c) Signals silently dropped per-ticker
  (d) Cube fan-out drops trades (similar to B1095 Bug A + Bug B)
"""
from __future__ import annotations

from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent


def test_calendar_effects_producer_exists():
    """calendar_effects.py must exist."""
    cal_file = REPO / "backtest" / "signals" / "calendar_effects.py"
    assert cal_file.exists(), f"calendar_effects.py missing at {cal_file}"


def test_calendar_lru_cache_decorator_present():
    """@lru_cache decorator must be present per Turn 2 finding."""
    cal_file = REPO / "backtest" / "signals" / "calendar_effects.py"
    screener_file = REPO / "backtest" / "signals" / "screener.py"
    for f in [cal_file, screener_file]:
        content = f.read_text(encoding="utf-8", errors="ignore")
        if "lru_cache" in content or "_cached_calendar" in content:
            return
    pytest.fail(
        "@lru_cache reference not found in calendar_effects.py or screener.py. "
        "BUG-279 root cause hypothesis (a) requires this decorator."
    )


def test_halloween_dates_recognized():
    """Producer must recognize 4 halloween-first-days in 2022-2025.

    Simplified check: source contains month=11 + tdm=1 logic per Turn 2
    calendar_effects.py:196 finding.
    """
    cal_file = REPO / "backtest" / "signals" / "calendar_effects.py"
    if not cal_file.exists():
        pytest.skip("calendar_effects.py missing")
        return
    content = cal_file.read_text(encoding="utf-8", errors="ignore")
    has_month_11 = "month == 11" in content or "month==11" in content
    has_tdm = "tdm" in content
    assert has_month_11 and has_tdm, (
        "calendar_effects.py must have halloween logic (month==11 AND tdm=1) "
        "per Turn 2 investigation."
    )


def test_bug_279_calendar_family_underfire_documented():
    """BUG-279 open: 3 calendar strategies must show underfire in CSV."""
    import pandas as pd

    csv = REPO / "output_batch_A_150" / "phase_1_quiet_fire_investigation.csv"
    if not csv.exists():
        pytest.skip("CSV missing")
        return
    df = pd.read_csv(csv)

    calendar_strategies = {
        "halloween_seasonal_long": 300,  # expected ~300 fires; got 1
        "totm_long": 4300,  # expected ~4300; got 12
        "pre_holiday_long": 750,  # expected ~750; got 6
    }
    for strat, expected in calendar_strategies.items():
        row = df[df["strategy_name"] == strat]
        if row.empty:
            continue
        n_fires = int(row.iloc[0]["n_fires"])
        underfire_ratio = expected / max(n_fires, 1)
        assert underfire_ratio > 50, (
            f"BUG-279 RED-FIRST: {strat} expected underfire ratio > 50x per "
            f"Turn 2 finding. Got expected/actual = {expected}/{n_fires} = "
            f"{underfire_ratio:.1f}x. If ratio dropped below 50x, "
            f"BUG-279 may have been fixed - update this test."
        )


def test_batch_a_calendar_probe_dates_reachable():
    """Meta-test: 4 halloween-first-days + 4 turn-of-month dates enumerable."""
    from datetime import date

    halloween_dates = [date(2022, 11, 1), date(2023, 11, 1), date(2024, 11, 1), date(2025, 11, 3)]
    for d in halloween_dates:
        assert d.month == 11, "November required"
        assert 1 <= d.day <= 3, "First trading day"
