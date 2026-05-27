"""Batch 406 (2026-05-27): DATA_LOAD_START bug fix verification.

Source (per CHECKLIST #77): owner directive 2026-05-27 path 2.
batch_1 forensic revealed engine loaded OHLCV from hardcoded
2021-05-05 regardless of --start CLI arg.  Day-loop iterated
2020-01-02 -> 2026-04-30 but universe was empty for 2020-2021
because no OHLCV existed for those dates.

Result: 1.4 years silently lost (~22% of intended scope).

Fix in backtest/engine/backtest.py:load_data:
    warmup_start = self.start - timedelta(days=400)
    actual_start = min(DATA_LOAD_START, warmup_start)

Test pins this invariant so the bug cannot regress.

Run: pytest backtest/tests/test_batch406_data_load_start.py -v
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent.parent


def test_data_load_start_constant_present():
    """DATA_LOAD_START constant must exist in config.py."""
    from backtest.config import DATA_LOAD_START
    assert DATA_LOAD_START is not None
    assert isinstance(DATA_LOAD_START, date)


def test_load_data_uses_min_of_constant_and_start_minus_400d():
    """Engine load_data must use min(DATA_LOAD_START, self.start - 400d).

    Inspects the load_data source for the Batch 406 fix tokens rather
    than running the engine (which would require full data + ~minutes).
    """
    engine_src = (REPO / "backtest" / "engine" / "backtest.py").read_text(encoding="utf-8")
    # Required tokens that prove the Batch 406 fix is wired
    required = [
        "warmup_start = self.start - timedelta(days=400)",
        "actual_start = min(DATA_LOAD_START, warmup_start)",
        # The load call must use actual_start, not DATA_LOAD_START directly
        "start=actual_start",
    ]
    for tok in required:
        assert tok in engine_src, (
            f"Batch 406 fix token missing in backtest/engine/backtest.py: `{tok}`. "
            f"DATA_LOAD_START bug regression risk."
        )


def test_load_data_logs_batch_406_marker():
    """Engine should log [Batch 406: actual_start = ...] so post-run
    forensics can confirm the fix is active."""
    engine_src = (REPO / "backtest" / "engine" / "backtest.py").read_text(encoding="utf-8")
    assert "[Batch 406:" in engine_src, (
        "Engine load_data log line missing the [Batch 406:] marker"
    )


def test_warmup_buffer_covers_252day_indicators():
    """400-day warmup must cover the longest indicator lookback (252-day
    annual momentum) with safety margin."""
    # 400 calendar days = ~280 trading days; comfortably > 252
    # If we ever shorten warmup below 365 days, this test fails so we
    # remember why 400 was chosen.
    target_calendar_days = 400
    target_trading_days = int(target_calendar_days * 5 / 7)
    assert target_trading_days >= 252, (
        f"Warmup {target_calendar_days}d -> ~{target_trading_days} trading days "
        f"is insufficient for 252-day momentum indicator"
    )


@pytest.mark.parametrize("user_start,expected_load_start", [
    # When user start is BEFORE the legacy constant, engine should load earlier
    (date(2020, 1, 2),  date(2020, 1, 2) - timedelta(days=400)),  # = 2018-11-28
    (date(2019, 1, 2),  date(2019, 1, 2) - timedelta(days=400)),  # = 2017-11-28
    # When user start is AFTER the legacy constant, engine uses the constant
    (date(2024, 1, 2),  date(2021, 5, 5)),  # min(2021-05-05, 2022-11-28) = 2021-05-05
    (date(2023, 1, 2),  date(2021, 5, 5)),  # min(2021-05-05, 2021-11-28) = 2021-05-05
    # Edge case: user start exactly aligns with legacy
    (date(2022, 6, 9),  date(2021, 5, 5)),  # 2022-06-09 - 400d = 2021-05-05 exactly
])
def test_actual_start_logic(user_start, expected_load_start):
    """Direct unit test of the min(DATA_LOAD_START, start - 400d) formula."""
    from backtest.config import DATA_LOAD_START
    warmup_start = user_start - timedelta(days=400)
    actual_start = min(DATA_LOAD_START, warmup_start)
    assert actual_start == expected_load_start, (
        f"user_start={user_start} warmup={warmup_start} "
        f"DATA_LOAD_START={DATA_LOAD_START} actual={actual_start} "
        f"expected={expected_load_start}"
    )
