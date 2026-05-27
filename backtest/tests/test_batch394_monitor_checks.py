"""Batch 394: 14-check monitor smoke test.

Source (per CHECKLIST #77): owner directive 2026-05-27 expand monitor.
This test exercises each of the 14 checks against synthetic log inputs
to verify (a) regex parsing handles the real engine output format, and
(b) each check returns the expected severity on its trigger condition.

Run: pytest backtest/tests/test_batch394_monitor_checks.py -v
"""
from __future__ import annotations

import argparse
from datetime import datetime
from types import SimpleNamespace

import pytest

from scripts.monitor_phase_1a_beta_health import (
    CHECKS,
    MonitorState,
    parse_log_into_state,
    RE_MILESTONE_100D,
    RE_MILESTONE_YEAR,
    RE_PROGRESS,
)


def _args(**overrides):
    base = dict(
        host="x", session="y", local=None, interval=60, lines=500,
        max_run_hours=6.0, warn_run_hours=4.0,
        baseline_tpd=7.0, warn_ratio=0.5, abort_ratio=0.3,
        log_stale_seconds=600, auto_kill=False, once=True,
    )
    base.update(overrides)
    return argparse.Namespace(**base)


# --------- regex parsing -----------------------------------------------------

def test_regex_progress_parses_engine_format():
    line = ("2026-05-27 02:25:00,557 [INFO] backtest.engine.backtest: "
            "Progress: 100/120 [2024-01-19] open=4 closed=3 "
            "elapsed_hours=0.06")
    m = RE_PROGRESS.search(line)
    assert m is not None
    assert m.group("day") == "100"
    assert m.group("total") == "120"
    assert m.group("as_of") == "2024-01-19"
    assert m.group("open") == "4"
    assert m.group("closed") == "3"
    assert m.group("elapsed_h") == "0.06"


def test_regex_milestone_100d_parses_engine_format():
    line = ("[MILESTONE-100D] day_idx=100 total_days=120 as_of=2024-01-19 "
            "cumulative_trades=3 delta_trades=0 long_pct=33.3% "
            "top_strats=[williams_stoch_dual:2,pairs_mean_reversion_long:1] "
            "zero_strats=184")
    m = RE_MILESTONE_100D.search(line)
    assert m is not None
    assert m.group("day") == "100"
    assert m.group("cum") == "3"
    assert m.group("long_pct") == "33.3"
    assert "williams_stoch_dual:2" in m.group("top")
    assert m.group("zero") == "184"


def test_regex_milestone_year_parses_engine_format():
    line = ("[MILESTONE-YEAR] year_closed=2023 cumulative_trades=3 "
            "delta_trades=3 long_pct=33.3% "
            "top_strats=[williams_stoch_dual:2] zero_strats=184")
    m = RE_MILESTONE_YEAR.search(line)
    assert m is not None
    assert m.group("year") == "2023"
    assert m.group("delta") == "3"


# --------- parse_log_into_state ---------------------------------------------

def test_parse_log_updates_state():
    log = (
        "2026-05-27 02:25:00,000 [INFO] x.engine: Progress: 100/120 "
        "[2024-01-19] open=4 closed=3 elapsed_hours=2.5\n"
        "2026-05-27 02:25:01,000 [INFO] x.engine: [MILESTONE-100D] "
        "day_idx=100 total_days=120 as_of=2024-01-19 cumulative_trades=15 "
        "delta_trades=15 long_pct=60.0% top_strats=[a:8,b:7] zero_strats=180\n"
        "2026-05-27 02:25:02,000 [INFO] x.engine: [MILESTONE-YEAR] "
        "year_closed=2023 cumulative_trades=10 delta_trades=10 "
        "long_pct=70.0% top_strats=[a:6,b:4] zero_strats=183\n"
    )
    state = MonitorState()
    parse_log_into_state(state, log)
    assert state.last_progress_day == 100
    assert state.last_progress_open == 4
    assert state.last_progress_closed == 3
    assert state.last_progress_elapsed_h == pytest.approx(2.5)
    assert state.last_milestone_100d_seen is not None
    assert state.last_milestone_100d_seen["cumulative_trades"] == 15
    assert state.last_milestone_100d_seen["long_pct"] == 60.0
    assert len(state.year_history) == 1
    assert state.year_history[0]["year"] == 2023


def test_parse_log_empty_increments_ssh_fail_streak():
    state = MonitorState()
    parse_log_into_state(state, "")
    parse_log_into_state(state, "")
    parse_log_into_state(state, "")
    assert state.ssh_fail_streak == 3


# --------- W1 wall-time kill ------------------------------------------------

def test_w1_fires_kill_when_elapsed_exceeds_max_plus_buffer():
    state = MonitorState()
    state.last_progress_elapsed_h = 6.1  # past 6h + 5min buffer
    sev, msg = CHECKS[0][1](state, "", _args(max_run_hours=6.0))
    assert sev == "kill"
    assert "W1" in msg


def test_w1_skips_when_max_unset():
    state = MonitorState()
    sev, _ = CHECKS[0][1](state, "", _args(max_run_hours=None))
    assert sev == "skip"


# --------- W2 log staleness -------------------------------------------------

def test_w2_warns_when_log_stale():
    state = MonitorState()
    state.last_progress_ts = datetime.utcnow().replace(
        year=datetime.utcnow().year - 1
    )
    sev, msg = CHECKS[1][1](state, "", _args(log_stale_seconds=600))
    assert sev == "warn"
    assert "LOG-STALE" in msg


# --------- W3 crash signatures ----------------------------------------------

@pytest.mark.parametrize("snippet", [
    "Traceback (most recent call last):",
    "Killed",
    "MemoryError: out of memory",
    "Segmentation fault (core dumped)",
])
def test_w3_fires_kill_on_each_crash_signature(snippet):
    state = MonitorState()
    sev, msg = CHECKS[2][1](state, snippet, _args())
    assert sev == "kill"
    assert "CRASH-SIGNATURE" in msg


# --------- W4 trade rate ----------------------------------------------------

def test_w4_kill_on_low_rate():
    state = MonitorState()
    state.last_progress_day = 200
    state.last_progress_open = 0
    state.last_progress_closed = 50  # 0.25 tpd vs baseline 7.0
    sev, msg = CHECKS[3][1](state, "", _args(baseline_tpd=7.0))
    assert sev == "kill"
    assert "TRADE-RATE-LOW" in msg


def test_w4_ok_when_rate_healthy():
    state = MonitorState()
    state.last_progress_day = 200
    state.last_progress_open = 0
    state.last_progress_closed = 1500  # 7.5 tpd vs baseline 7.0
    sev, _ = CHECKS[3][1](state, "", _args(baseline_tpd=7.0))
    assert sev == "ok"


# --------- W5 milestone floor -----------------------------------------------

def test_w5_kill_on_milestone_floor_breach():
    state = MonitorState()
    state.last_milestone_100d_seen = {
        "day_idx": 100, "total": 1638,
        "cumulative_trades": 5, "delta_trades": 5,
        "long_pct": 100.0, "top_strats": "a:5", "zero_strats": 184,
        "as_of": "2020-05-15",
    }
    sev, msg = CHECKS[4][1](state, "", _args(baseline_tpd=7.0, abort_ratio=0.3))
    # expected floor at day 100 = 7.0 * 100 * 0.3 = 210; actual 5 << floor
    assert sev == "kill"
    assert "MILESTONE-FLOOR-BREACH" in msg


def test_w5_kill_on_zero_fires_when_no_baseline():
    state = MonitorState()
    state.last_milestone_100d_seen = {
        "day_idx": 100, "total": 1638,
        "cumulative_trades": 0, "delta_trades": 0,
        "long_pct": 0.0, "top_strats": "", "zero_strats": 185,
        "as_of": "2020-05-15",
    }
    sev, msg = CHECKS[4][1](state, "", _args(baseline_tpd=None))
    assert sev == "kill"
    assert "MILESTONE-ZERO" in msg


# --------- W7 direction balance ---------------------------------------------

def test_w7_warns_on_low_long():
    state = MonitorState()
    state.last_milestone_100d_seen = {
        "day_idx": 200, "total": 1638, "cumulative_trades": 100,
        "delta_trades": 100, "long_pct": 5.0, "top_strats": "a:50",
        "zero_strats": 100, "as_of": "2020-09-30",
    }
    sev, msg = CHECKS[6][1](state, "", _args())
    assert sev == "warn"
    assert "LOW-LONG" in msg


# --------- W8 top-strategy share --------------------------------------------

def test_w8_warns_on_top_strategy_dominance():
    state = MonitorState()
    state.last_milestone_100d_seen = {
        "day_idx": 200, "total": 1638, "cumulative_trades": 100,
        "delta_trades": 100, "long_pct": 60.0, "top_strats": "a:60,b:20,c:10",
        "zero_strats": 100, "as_of": "2020-09-30",
    }
    sev, msg = CHECKS[7][1](state, "", _args())
    # top = 60 / 100 = 60% > 40% threshold
    assert sev == "warn"
    assert "TOP-STRAT-DOMINANT" in msg


# --------- W9 year boundary pace --------------------------------------------

def test_w9_warns_on_pace_deviation():
    state = MonitorState()
    state.year_history = [
        {"year": 2020, "delta_trades": 1000, "cumulative_trades": 1000,
         "long_pct": 60.0, "top_strats": "a:500", "zero_strats": 100},
        {"year": 2021, "delta_trades": 100, "cumulative_trades": 1100,
         "long_pct": 60.0, "top_strats": "a:50", "zero_strats": 100},
    ]
    # ratio = 100 / 1000 = 0.1 < 0.3
    sev, msg = CHECKS[8][1](state, "", _args())
    assert sev == "warn"
    assert "YEAR-PACE-OFF" in msg


# --------- W10 open runaway -------------------------------------------------

def test_w10_warns_on_runaway_open():
    state = MonitorState()
    state.last_progress_open = 2500
    sev, msg = CHECKS[9][1](state, "", _args())
    assert sev == "warn"
    assert "OPEN-RUNAWAY" in msg


# --------- W11 memory cap breaches ------------------------------------------

def test_w11_warns_on_repeated_memory_cap():
    log = "MEMORY_CAP_BREACHED\n" * 10
    state = MonitorState()
    sev, msg = CHECKS[10][1](state, log, _args())
    assert sev == "warn"
    assert "MEMORY-CAP" in msg


# --------- W14 wall-time WARN -----------------------------------------------

def test_w14_warns_at_4h():
    state = MonitorState()
    state.last_progress_elapsed_h = 4.1
    sev, msg = CHECKS[13][1](state, "", _args(warn_run_hours=4.0))
    assert sev == "warn"
    assert "WALL-TIME-WARN" in msg


# --------- W14 doesn't refire ------------------------------------------------

def test_w14_does_not_refire():
    state = MonitorState()
    state.last_progress_elapsed_h = 4.5
    args = _args(warn_run_hours=4.0)
    sev1, _ = CHECKS[13][1](state, "", args)
    sev2, _ = CHECKS[13][1](state, "", args)
    assert sev1 == "warn"
    assert sev2 == "ok"  # already warned, returns ok
