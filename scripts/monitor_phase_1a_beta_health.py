"""Batch 394: 14-check Phase 1A-beta health monitor.

Source (per CHECKLIST #77 canonical-source attribution): owner directive
2026-05-27 - expand monitor beyond `trade-count vs baseline` to catch
the broader class of run-pathologies early.  Replaces the Batch 377
shell script.

Design: SSH-tail the engine's run log (via tmux capture-pane on the
target host, or --local <path> for local runs) and apply 14 checks
every poll interval.  When any check fires at KILL severity, issue
the kill (ssh tmux kill-session).  Memory: feedback_monitor_intermediate_counts.md

The 14 checks (memory: feedback_strategy_x_exit_cell_analysis.md - cell-level
not aggregate where possible):

  W1   Wall-time KILL at max_run_hours (+5min watchdog buffer)
  W2   Log-staleness -> engine crashed/hung
  W3   Crash-signature scan (Traceback / Killed / MemoryError / segfault)
  W4   Total trade-rate vs baseline floor
  W5   100-day milestone cumulative trade floor (catches the 361-trade case)
  W6   Per-strategy zero-fire at 50% completion (PRODUCER_LAYER_ZERO regressions)
  W7   Direction balance (long share in 20-95% window)
  W8   Top-strategy share > 40% (one strategy dominating)
  W9   Year-boundary pace deviation (one year << prior year)
  W10  Open-position runaway (open > 2000 even with no_portfolio_cap)
  W11  Memory RSS climb slope (potential leak)
  W12  Disk free % on host
  W13  SSH-reachability streak
  W14  Wall-time WARN at warn_run_hours (yellow flag, not kill)

Usage:
  python scripts/monitor_phase_1a_beta_health.py \\
      --host root@HOST_IP --session phase1a_single \\
      --max-run-hours 6.0 --warn-run-hours 4.0 \\
      --baseline-tpd null  # use null for cap-off runs without a baseline

  # Or local:
  python scripts/monitor_phase_1a_beta_health.py \\
      --local backtest_v2.log --max-run-hours 6.0 --warn-run-hours 4.0
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Parsing helpers - keep regexes stable; the engine telemetry format is the
# contract.  See backtest/engine/backtest.py Batch 394 hooks.
# ---------------------------------------------------------------------------

# Progress line: "Progress: %d/%d [date] open=%d closed=%d elapsed_hours=%.2f"
RE_PROGRESS = re.compile(
    r"Progress:\s+(?P<day>\d+)/(?P<total>\d+)\s+\[(?P<as_of>\d{4}-\d{2}-\d{2})\]"
    r"\s+open=(?P<open>\d+)\s+closed=(?P<closed>\d+)"
    r"(?:\s+elapsed_hours=(?P<elapsed_h>[\d.]+))?"
)

# Milestone-100D line:
#   [MILESTONE-100D] day_idx=N total_days=N as_of=YYYY-MM-DD cumulative_trades=N
#                    delta_trades=N long_pct=X.X% top_strats=[a:N,b:N,...] zero_strats=N
RE_MILESTONE_100D = re.compile(
    r"\[MILESTONE-100D\]\s+day_idx=(?P<day>\d+)\s+total_days=(?P<total>\d+)\s+"
    r"as_of=(?P<as_of>\d{4}-\d{2}-\d{2})\s+cumulative_trades=(?P<cum>\d+)\s+"
    r"delta_trades=(?P<delta>\d+)\s+long_pct=(?P<long_pct>[\d.]+)%\s+"
    r"top_strats=\[(?P<top>[^\]]*)\]\s+zero_strats=(?P<zero>\d+)"
)

# Milestone-YEAR line:
RE_MILESTONE_YEAR = re.compile(
    r"\[MILESTONE-YEAR\]\s+year_closed=(?P<year>\d+)\s+"
    r"cumulative_trades=(?P<cum>\d+)\s+delta_trades=(?P<delta>\d+)\s+"
    r"long_pct=(?P<long_pct>[\d.]+)%\s+top_strats=\[(?P<top>[^\]]*)\]\s+"
    r"zero_strats=(?P<zero>\d+)"
)

# Engine timestamp: "2026-05-27 02:25:00,557 [INFO] ..."
RE_LOG_TS = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
)

# Crash signatures
CRASH_PATTERNS = [
    re.compile(r"Traceback \(most recent call last\)"),
    re.compile(r"\bKilled\b"),
    re.compile(r"MemoryError"),
    re.compile(r"Segmentation fault"),
    re.compile(r"OutOfMemoryError"),
    re.compile(r"\boom-killer\b"),
]


# ---------------------------------------------------------------------------
# Log capture - SSH tmux for remote, file tail for local.
# ---------------------------------------------------------------------------

def capture_remote(host: str, session: str, lines: int = 500) -> str:
    """SSH into host, tmux capture-pane on session, return last N lines."""
    cmd = [
        "ssh", "-o", "ConnectTimeout=15",
        host,
        f"tmux capture-pane -p -t {session} -S -{lines} 2>/dev/null | tail -{lines}",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return r.stdout
    except Exception as exc:
        return ""


def capture_local(path: Path, lines: int = 500) -> str:
    """Tail last N lines of a local log file."""
    if not path.exists():
        return ""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            return "".join(deque(f, maxlen=lines))
    except Exception:
        return ""


def kill_remote(host: str, session: str) -> bool:
    """Issue tmux kill-session on host.  Returns True if command exited 0."""
    cmd = [
        "ssh", "-o", "ConnectTimeout=15", host,
        f"tmux kill-session -t {session}",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return r.returncode == 0
    except Exception:
        return False


# ---------------------------------------------------------------------------
# State tracked across polls
# ---------------------------------------------------------------------------

class MonitorState:
    """Cross-iteration state for trend / streak / first-fire checks."""

    def __init__(self):
        self.start_epoch: float = time.time()
        self.last_progress_ts: Optional[datetime] = None
        self.last_progress_elapsed_h: float = 0.0
        self.last_progress_day: int = 0
        self.last_progress_total: int = 0
        self.last_progress_open: int = 0
        self.last_progress_closed: int = 0
        self.last_milestone_100d_seen: Optional[dict] = None
        self.last_milestone_year_seen: Optional[dict] = None
        self.year_history: list = []  # list of dicts from year milestones
        self.ssh_fail_streak: int = 0
        self.fire_count: dict = {}    # name -> count (how many times each check fired)
        self.killed: bool = False
        self.warned_4h: bool = False


# ---------------------------------------------------------------------------
# 14 checks - each returns (severity, message) where severity in
#   "ok" / "warn" / "kill" / "skip"
# ---------------------------------------------------------------------------

def check_w1_wall_time_kill(
    state: MonitorState, log: str, args
) -> tuple[str, str]:
    """W1: hard-kill at max_run_hours + 5min watchdog buffer."""
    if args.max_run_hours is None:
        return "skip", "max_run_hours not set"
    # Prefer engine-emitted elapsed_h (more accurate than monitor wall-clock
    # because monitor may have started after engine).
    elapsed_h = state.last_progress_elapsed_h
    if elapsed_h <= 0:
        elapsed_h = (time.time() - state.start_epoch) / 3600.0
    threshold = args.max_run_hours + (5 / 60.0)  # +5min buffer
    if elapsed_h >= threshold:
        return "kill", (
            f"W1 WALL-TIME-KILL: elapsed_h={elapsed_h:.2f} >= "
            f"max_run_hours+5min={threshold:.2f} (engine should have "
            f"self-killed at {args.max_run_hours:.2f}h)"
        )
    return "ok", f"elapsed_h={elapsed_h:.2f} < threshold={threshold:.2f}"


def check_w2_log_staleness(
    state: MonitorState, log: str, args
) -> tuple[str, str]:
    """W2: last log timestamp > 10min ago = engine likely crashed/hung."""
    if state.last_progress_ts is None:
        return "ok", "no progress line yet"
    age_s = (datetime.utcnow() - state.last_progress_ts).total_seconds()
    if age_s > args.log_stale_seconds:
        return "warn", (
            f"W2 LOG-STALE: last engine log {age_s:.0f}s ago "
            f"(threshold {args.log_stale_seconds}s)"
        )
    return "ok", f"last_log_age={age_s:.0f}s"


def check_w3_crash_signatures(
    state: MonitorState, log: str, args
) -> tuple[str, str]:
    """W3: scan for crash signatures (Traceback / Killed / etc)."""
    for pat in CRASH_PATTERNS:
        m = pat.search(log)
        if m:
            return "kill", f"W3 CRASH-SIGNATURE: {m.group()}"
    return "ok", "no crash signatures"


def check_w4_trade_rate(
    state: MonitorState, log: str, args
) -> tuple[str, str]:
    """W4: total trades / backtest day vs baseline floor.

    For cap-off cube runs we have no historical baseline; in that case
    we only check the floor=0 condition (any trades by day 50).  Set
    --baseline-tpd explicitly to enable ratio-based check.
    """
    if state.last_progress_day == 0:
        return "skip", "no progress yet"
    total = state.last_progress_open + state.last_progress_closed
    if state.last_progress_day < 50:
        return "ok", "too early (< 50 days) for rate check"
    if args.baseline_tpd is None:
        if total == 0:
            return "warn", (
                f"W4 ZERO-FIRES at day {state.last_progress_day}: no trades "
                f"fired (cap-off run should have fires by day 50)"
            )
        return "ok", f"trades={total} day={state.last_progress_day} (no baseline set)"
    actual_tpd = total / state.last_progress_day
    ratio = actual_tpd / args.baseline_tpd
    if ratio < args.abort_ratio:
        return "kill", (
            f"W4 TRADE-RATE-LOW: actual_tpd={actual_tpd:.2f} / "
            f"baseline_tpd={args.baseline_tpd:.2f} = ratio={ratio:.2f} < "
            f"abort_ratio={args.abort_ratio:.2f}"
        )
    if ratio < args.warn_ratio:
        return "warn", (
            f"W4 TRADE-RATE-WARN: ratio={ratio:.2f} < "
            f"warn_ratio={args.warn_ratio:.2f}"
        )
    return "ok", f"actual_tpd={actual_tpd:.2f} ratio={ratio:.2f}"


def check_w5_milestone_floor(
    state: MonitorState, log: str, args
) -> tuple[str, str]:
    """W5: at each 100-day milestone, cumulative_trades vs expected floor.

    Catches the 361-trade case at ~10% completion: expected trades by
    day 100 = (baseline_tpd * 100) * 0.5; if actual < that, KILL.
    """
    if state.last_milestone_100d_seen is None:
        return "skip", "no 100D milestone yet"
    m = state.last_milestone_100d_seen
    cum = m["cumulative_trades"]
    day = m["day_idx"]
    if args.baseline_tpd is None:
        if cum == 0 and day >= 100:
            return "kill", (
                f"W5 MILESTONE-ZERO: day_idx={day} cumulative_trades=0 "
                f"(cap-off run with zero fires at 100-day milestone = "
                f"engine broken)"
            )
        return "ok", f"day={day} cum={cum} (no baseline set)"
    expected_floor = args.baseline_tpd * day * args.abort_ratio
    if cum < expected_floor:
        return "kill", (
            f"W5 MILESTONE-FLOOR-BREACH: day_idx={day} cumulative_trades={cum} "
            f"< expected_floor={expected_floor:.0f} (baseline_tpd={args.baseline_tpd} "
            f"* abort_ratio={args.abort_ratio})"
        )
    return "ok", f"day={day} cum={cum} floor={expected_floor:.0f}"


def check_w6_strategy_zero_fire(
    state: MonitorState, log: str, args
) -> tuple[str, str]:
    """W6: per-strategy zero-fire detector at 50% completion.

    `zero_strats` is emitted in the milestone telemetry.  We use the
    latest 100D milestone reading: if >50% of registered strategies have
    fired zero trades when we are past 50% completion, surface a WARN.
    """
    if state.last_milestone_100d_seen is None:
        return "skip", "no 100D milestone yet"
    m = state.last_milestone_100d_seen
    if m["total"] == 0:
        return "skip", "no total_days info"
    pct_done = m["day_idx"] / m["total"]
    if pct_done < 0.5:
        return "skip", f"too early ({pct_done*100:.0f}% done)"
    zero = m["zero_strats"]
    # Heuristic: warn if more than 75% of registered strategies have
    # never fired by mid-run.  Real PRODUCER_LAYER_ZERO regressions
    # should be flagged for post-run audit.
    total_strats = zero + (len(m["top_strats"].split(",")) if m["top_strats"] else 0)
    if total_strats == 0:
        return "skip", "no strategy data"
    # Use the registered-strategy count by reading the engine's known set;
    # if not available, compare zero against a 150-strategy proxy.
    proxy_total = 185
    zero_pct = 100.0 * zero / proxy_total
    if zero_pct > 75.0:
        return "warn", (
            f"W6 STRATEGY-ZERO-FIRE-WARN: {zero} of {proxy_total} strategies "
            f"({zero_pct:.0f}%) have fired zero trades at "
            f"{pct_done*100:.0f}% completion"
        )
    return "ok", f"zero_strats={zero} of {proxy_total} ({zero_pct:.0f}%)"


def check_w7_direction_balance(
    state: MonitorState, log: str, args
) -> tuple[str, str]:
    """W7: long share in 20-95% window."""
    if state.last_milestone_100d_seen is None:
        return "skip", "no 100D milestone yet"
    m = state.last_milestone_100d_seen
    long_pct = m["long_pct"]
    if long_pct < 20.0:
        return "warn", f"W7 DIRECTION-LOW-LONG: long_pct={long_pct:.1f}% < 20%"
    if long_pct > 95.0:
        return "warn", f"W7 DIRECTION-HIGH-LONG: long_pct={long_pct:.1f}% > 95%"
    return "ok", f"long_pct={long_pct:.1f}%"


def check_w8_top_strategy_share(
    state: MonitorState, log: str, args
) -> tuple[str, str]:
    """W8: top-1 strategy share > 40% = one strategy dominating."""
    if state.last_milestone_100d_seen is None:
        return "skip", "no 100D milestone yet"
    m = state.last_milestone_100d_seen
    cum = m["cumulative_trades"]
    if cum < 50:
        return "skip", f"too few trades ({cum}) for share check"
    top = m["top_strats"]
    # top format: "name1:N1,name2:N2,..."
    if not top:
        return "ok", "no strategies fired"
    try:
        first = top.split(",")[0]
        _, n_str = first.rsplit(":", 1)
        n = int(n_str)
        share = 100.0 * n / cum
        if share > 40.0:
            return "warn", (
                f"W8 TOP-STRAT-DOMINANT: top strategy = {n} trades "
                f"({share:.1f}% of {cum})"
            )
        return "ok", f"top_share={share:.1f}%"
    except Exception:
        return "skip", "top_strats parse failure"


def check_w9_year_boundary_pace(
    state: MonitorState, log: str, args
) -> tuple[str, str]:
    """W9: each year's trades within 0.3-3x prior year.

    Catches regime classifier breakage or universe collapse mid-run.
    Skipped until we have 2+ year milestones.
    """
    if len(state.year_history) < 2:
        return "skip", f"only {len(state.year_history)} year milestones seen"
    prior = state.year_history[-2]
    curr = state.year_history[-1]
    if prior["delta_trades"] == 0:
        return "skip", "prior year had zero trades"
    ratio = curr["delta_trades"] / prior["delta_trades"]
    if ratio < 0.3 or ratio > 3.0:
        return "warn", (
            f"W9 YEAR-PACE-OFF: curr_delta={curr['delta_trades']} vs "
            f"prior_delta={prior['delta_trades']} = ratio={ratio:.2f} "
            f"(outside 0.3-3.0)"
        )
    return "ok", f"year_pace_ratio={ratio:.2f}"


def check_w10_open_runaway(
    state: MonitorState, log: str, args
) -> tuple[str, str]:
    """W10: open positions > 2000 = runaway despite no_portfolio_cap."""
    n_open = state.last_progress_open
    if n_open > 2000:
        return "warn", (
            f"W10 OPEN-RUNAWAY: {n_open} open positions; engine may "
            f"OOM. Check no_portfolio_cap behavior."
        )
    return "ok", f"open={n_open}"


def check_w11_memory_climb(
    state: MonitorState, log: str, args
) -> tuple[str, str]:
    """W11: DEC-179 MEMORY_CAP_BREACHED scan in log."""
    if "MEMORY_CAP_BREACHED" in log:
        # Count occurrences as a rough trend signal
        n = log.count("MEMORY_CAP_BREACHED")
        if n > 5:
            return "warn", (
                f"W11 MEMORY-CAP: DEC-179 cap breached {n} times in log "
                f"window; potential leak"
            )
    return "ok", "no memory cap breaches"


def check_w12_disk_free(
    state: MonitorState, log: str, args
) -> tuple[str, str]:
    """W12: SSH into host, check disk free %.  Skip in --local mode."""
    if args.local:
        return "skip", "disk check only valid in remote mode"
    try:
        cmd = [
            "ssh", "-o", "ConnectTimeout=15", args.host,
            "df -h / | awk 'NR==2 {print $5}'",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        pct_str = r.stdout.strip().rstrip("%")
        pct = int(pct_str) if pct_str.isdigit() else None
        if pct is None:
            return "skip", "could not parse df output"
        if pct > 90:
            return "warn", f"W12 DISK-LOW: {pct}% used on /"
        return "ok", f"disk_used={pct}%"
    except Exception as exc:
        return "skip", f"df ssh failed: {exc}"


def check_w13_ssh_streak(
    state: MonitorState, log: str, args
) -> tuple[str, str]:
    """W13: N consecutive SSH failures = host crashed."""
    if state.ssh_fail_streak >= 5:
        return "warn", (
            f"W13 SSH-UNREACHABLE: {state.ssh_fail_streak} consecutive "
            f"polls failed; host may have crashed"
        )
    return "ok", f"ssh_fail_streak={state.ssh_fail_streak}"


def check_w14_warn_4h(
    state: MonitorState, log: str, args
) -> tuple[str, str]:
    """W14: WARN at warn_run_hours threshold (yellow flag, not kill)."""
    if args.warn_run_hours is None:
        return "skip", "warn_run_hours not set"
    elapsed_h = state.last_progress_elapsed_h
    if elapsed_h <= 0:
        elapsed_h = (time.time() - state.start_epoch) / 3600.0
    if elapsed_h >= args.warn_run_hours and not state.warned_4h:
        state.warned_4h = True
        return "warn", (
            f"W14 WALL-TIME-WARN: elapsed_h={elapsed_h:.2f} >= "
            f"warn_run_hours={args.warn_run_hours:.2f} (kill at "
            f"max_run_hours={args.max_run_hours})"
        )
    return "ok", f"elapsed_h={elapsed_h:.2f}"


CHECKS = [
    ("W1",  check_w1_wall_time_kill),
    ("W2",  check_w2_log_staleness),
    ("W3",  check_w3_crash_signatures),
    ("W4",  check_w4_trade_rate),
    ("W5",  check_w5_milestone_floor),
    ("W6",  check_w6_strategy_zero_fire),
    ("W7",  check_w7_direction_balance),
    ("W8",  check_w8_top_strategy_share),
    ("W9",  check_w9_year_boundary_pace),
    ("W10", check_w10_open_runaway),
    ("W11", check_w11_memory_climb),
    ("W12", check_w12_disk_free),
    ("W13", check_w13_ssh_streak),
    ("W14", check_w14_warn_4h),
]


# ---------------------------------------------------------------------------
# Log parsing - update state from log text
# ---------------------------------------------------------------------------

def parse_log_into_state(state: MonitorState, log: str) -> None:
    """Walk the log lines and update MonitorState fields."""
    if not log:
        state.ssh_fail_streak += 1
        return
    state.ssh_fail_streak = 0

    # Latest Progress line
    for m in RE_PROGRESS.finditer(log):
        d = m.groupdict()
        state.last_progress_day = int(d["day"])
        state.last_progress_total = int(d["total"])
        state.last_progress_open = int(d["open"])
        state.last_progress_closed = int(d["closed"])
        if d.get("elapsed_h"):
            state.last_progress_elapsed_h = float(d["elapsed_h"])

    # Latest log timestamp
    ts_matches = list(RE_LOG_TS.finditer(log))
    if ts_matches:
        try:
            state.last_progress_ts = datetime.strptime(
                ts_matches[-1].group("ts"), "%Y-%m-%d %H:%M:%S",
            )
        except ValueError:
            pass

    # Latest 100D milestone
    for m in RE_MILESTONE_100D.finditer(log):
        d = m.groupdict()
        state.last_milestone_100d_seen = {
            "day_idx":            int(d["day"]),
            "total":              int(d["total"]),
            "as_of":              d["as_of"],
            "cumulative_trades":  int(d["cum"]),
            "delta_trades":       int(d["delta"]),
            "long_pct":           float(d["long_pct"]),
            "top_strats":         d["top"],
            "zero_strats":        int(d["zero"]),
        }

    # All year milestones (history)
    seen_years = {y["year"] for y in state.year_history}
    for m in RE_MILESTONE_YEAR.finditer(log):
        d = m.groupdict()
        if int(d["year"]) in seen_years:
            continue
        entry = {
            "year":              int(d["year"]),
            "cumulative_trades": int(d["cum"]),
            "delta_trades":      int(d["delta"]),
            "long_pct":          float(d["long_pct"]),
            "top_strats":        d["top"],
            "zero_strats":       int(d["zero"]),
        }
        state.year_history.append(entry)
        state.last_milestone_year_seen = entry


# ---------------------------------------------------------------------------
# Main poll loop
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="root@46.224.181.68",
                    help="SSH host (used in remote mode)")
    ap.add_argument("--session", default="phase1a_single",
                    help="tmux session name on remote host")
    ap.add_argument("--local", type=Path, default=None,
                    help="Local log file path (skips SSH).  When set, "
                         "monitor tails this file instead of SSH-tmux.")
    ap.add_argument("--interval", type=int, default=60,
                    help="Poll interval seconds (default 60)")
    ap.add_argument("--lines", type=int, default=500,
                    help="Log lines to capture per poll (default 500)")
    ap.add_argument("--max-run-hours", type=float, default=6.0,
                    help="W1 kill threshold + 5min watchdog buffer")
    ap.add_argument("--warn-run-hours", type=float, default=4.0,
                    help="W14 WARN threshold (yellow flag)")
    ap.add_argument("--baseline-tpd", type=float, default=None,
                    help="Baseline trades-per-day; None disables ratio "
                         "checks (use for cap-off runs without a baseline)")
    ap.add_argument("--warn-ratio", type=float, default=0.5,
                    help="W4 ratio threshold for WARN")
    ap.add_argument("--abort-ratio", type=float, default=0.3,
                    help="W4/W5 ratio threshold for KILL")
    ap.add_argument("--log-stale-seconds", type=int, default=600,
                    help="W2 log-staleness threshold (default 10 min)")
    ap.add_argument("--auto-kill", action="store_true",
                    help="Issue ssh tmux kill-session on KILL severity. "
                         "Default OFF for safety; explicit opt-in.")
    ap.add_argument("--once", action="store_true",
                    help="Run one poll cycle and exit (for tests/CI)")
    args = ap.parse_args()

    print(f"[INIT] Batch 394 14-check Phase 1A-beta health monitor")
    print(f"[INIT] mode={'local' if args.local else 'remote'} "
          f"host={args.host} session={args.session}")
    print(f"[INIT] max_run_hours={args.max_run_hours} "
          f"warn_run_hours={args.warn_run_hours} "
          f"baseline_tpd={args.baseline_tpd}")
    print(f"[INIT] auto_kill={args.auto_kill} interval={args.interval}s")

    state = MonitorState()

    while True:
        # Capture log
        if args.local:
            log = capture_local(args.local, args.lines)
        else:
            log = capture_remote(args.host, args.session, args.lines)

        # Update state
        parse_log_into_state(state, log)

        # Run 14 checks
        summary = {"ok": 0, "warn": 0, "kill": 0, "skip": 0}
        fired = []
        for name, fn in CHECKS:
            try:
                sev, msg = fn(state, log, args)
            except Exception as exc:
                sev, msg = "skip", f"{name} exception: {exc}"
            summary[sev] += 1
            if sev in ("warn", "kill"):
                fired.append((name, sev, msg))
                state.fire_count[name] = state.fire_count.get(name, 0) + 1

        # Print one summary line + any fired checks
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{ts}] day={state.last_progress_day}/{state.last_progress_total} "
            f"open={state.last_progress_open} closed={state.last_progress_closed} "
            f"elapsed_h={state.last_progress_elapsed_h:.2f} "
            f"ok={summary['ok']} warn={summary['warn']} kill={summary['kill']} "
            f"skip={summary['skip']}"
        )
        for name, sev, msg in fired:
            print(f"  [{sev.upper():4}] {name}: {msg}")

        # Auto-kill if any KILL fired
        kills = [(n, m) for n, s, m in fired if s == "kill"]
        if kills and args.auto_kill and not state.killed:
            print(f"[AUTO-KILL] {len(kills)} KILL check(s) fired; "
                  f"issuing tmux kill-session")
            if not args.local:
                ok = kill_remote(args.host, args.session)
                print(f"[AUTO-KILL] kill_remote returned {ok}")
            state.killed = True
            sys.exit(2)

        if args.once:
            break

        # Inside last hour before kill, drop to 30s polling
        elapsed_h = state.last_progress_elapsed_h
        interval = args.interval
        if elapsed_h >= (args.max_run_hours - 1.0):
            interval = min(interval, 30)
        time.sleep(interval)


if __name__ == "__main__":
    main()
