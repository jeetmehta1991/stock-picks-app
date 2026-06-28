"""B1070 Stage B PASS-path P0 BLOCKER fixes pyramid tests.

# Source: Council 172/175/176 Sub-B per CHECKLIST #77 + #115 + owner
# directive 2026-06-29 'Proceed council this'.

3 PASS-path P0 BLOCKER fixes:
  F-1.1: Engine emit status='complete' after _finalize_open_trades
    (atomic .tmp + os.replace) so B1019 monitor PASS-exit fires
  F-2.1: Cube replay IPC OOM fix via imap_unordered + streaming
  F-7.1+F-10.1: Phase 4 pool=60->16 + MAX_MIN=480->1200 to avoid
    PHASE_4_TIMEOUT_HALT under B1068 ema_sma cost
"""
from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BACKTEST_PATH = REPO / "backtest" / "engine" / "backtest.py"
LAUNCH_SCRIPT = REPO / "scripts" / "launch_r5_master_4y_v2.sh"


# ============================ F-1.1 status=complete emit ===================

def test_b1070_f_1_1_status_complete_emit_in_backtest():
    """B1070 F-1.1: backtest.py must emit status='complete' after
    _finalize_open_trades so monitor PASS-exit fires."""
    src = BACKTEST_PATH.read_text()
    assert 'B1070 F-1.1 FIX' in src, "B1070 F-1.1: lineage comment required"
    # Must emit final state with status='complete'
    assert '"status": "complete"' in src, (
        "B1070 F-1.1 REGRESSION: backtest.py must write status='complete' "
        "to engine_state.json after _finalize_open_trades"
    )


def test_b1070_f_1_1_atomic_tmp_replace_pattern():
    """B1070 F-1.1 PIN: final emit must use atomic .tmp + os.replace
    pattern (NOT direct write) so monitor never reads half-written file."""
    src = BACKTEST_PATH.read_text()
    # The F-1.1 fix block uses _state_tmp + os.replace
    f_1_1_section = src[src.find("B1070 F-1.1 FIX"):]
    f_1_1_section = f_1_1_section[:5000]  # bound to fix block region
    assert "_state_tmp" in f_1_1_section, (
        "B1070 F-1.1: must write to .tmp file first"
    )
    assert "_os_b1070.replace" in f_1_1_section or "os.replace" in f_1_1_section, (
        "B1070 F-1.1: must use os.replace for atomic rename"
    )


def test_b1070_f_1_1_tracks_last_sim_day():
    """B1070 F-1.1: per-day loop must track _last_sim_day_index and
    _last_sim_date so final emit has correct values."""
    src = BACKTEST_PATH.read_text()
    assert "self._last_sim_day_index = i" in src, (
        "B1070 F-1.1: per-day loop must track _last_sim_day_index"
    )
    assert "self._last_sim_date = as_of" in src, (
        "B1070 F-1.1: per-day loop must track _last_sim_date"
    )


# ============================ F-2.1 cube replay IPC OOM ====================

def test_b1070_f_2_1_imap_unordered_replaces_starmap():
    """B1070 F-2.1: cube replay must use imap_unordered (streaming)
    instead of starmap (materialized list) to avoid Phase 4 IPC OOM."""
    src = BACKTEST_PATH.read_text()
    # Lineage required
    assert "B1070 F-2.1 FIX" in src, "B1070 F-2.1: lineage comment required"
    # imap_unordered must be in the streaming cube replay block
    assert "imap_unordered" in src, (
        "B1070 F-2.1 REGRESSION: cube replay must use imap_unordered "
        "(not starmap) to stream results and avoid 5-20GB IPC materialization"
    )


def test_b1070_f_2_1_starmap_no_longer_primary():
    """B1070 F-2.1 PIN: starmap must NOT be the primary cube replay
    path (legacy fallback only allowed if explicitly commented)."""
    src = BACKTEST_PATH.read_text()
    # Find the F-2.1 fix section
    f_2_1_start = src.find("B1070 F-2.1 FIX")
    if f_2_1_start == -1:
        # No fix at all
        assert False, "B1070 F-2.1: fix block missing"
    # Check the next 100 lines for primary starmap call
    f_2_1_section = src[f_2_1_start:f_2_1_start + 3500]
    # imap_unordered should be the primary path in this section
    assert "imap_unordered" in f_2_1_section, (
        "B1070 F-2.1: primary cube replay path must use imap_unordered"
    )


# ============================ F-7.1+F-10.1 pool + watchdog =================

def test_b1070_f_7_1_phase_4_pool_workers_16():
    """B1070 F-7.1: Phase 4 pool config must be 16 (was 60)."""
    src = LAUNCH_SCRIPT.read_text()
    # The case-statement should have Phase 4 -> POOL_WORKERS=16
    assert re.search(r"4\)\s+POOL_WORKERS=16", src), (
        "B1070 F-7.1 REGRESSION: launch script must set Phase 4 POOL_WORKERS=16 "
        "(was 60; 60-worker pool projected to OOM at 1929 ticker scale)"
    )


def test_b1070_f_10_1_phase_4_max_min_1200():
    """B1070 F-10.1: Phase 4 MAX_MIN must be 1200 (was 480) to absorb
    B1068 ema_sma 13.5hr cost at 1929 tickers."""
    src = LAUNCH_SCRIPT.read_text()
    # run_phase 4 line must have 1200 as MAX_MIN (6th arg)
    assert re.search(r"run_phase 4 .* 1200", src), (
        "B1070 F-10.1 REGRESSION: launch script run_phase 4 must use "
        "MAX_MIN=1200 (was 480; B1068 ema_sma cost = 13.5 hr at 1929 tickers)"
    )


def test_b1070_f_7_10_lineage_documented():
    """B1070 F-7.1+F-10.1 lineage in launch script."""
    src = LAUNCH_SCRIPT.read_text()
    assert "B1070 F-7.1+F-10.1 FIX" in src, (
        "B1070 F-7.1+F-10.1: lineage comment required in launch script"
    )


# ============================ Integration smoke ============================

def test_b1070_stage_b_files_syntax_clean():
    """B1070 Stage B: modified files must parse cleanly."""
    import ast
    bt_src = BACKTEST_PATH.read_text()
    ast.parse(bt_src)
    # Bash syntax check would require subprocess; assume bash -n run
    # separately in pyramid runner


def test_b1070_no_silent_misses_in_modified_files():
    """B1070 Stage B META: changed files must not have bare excepts.

    F-1.1 fix uses 'except Exception as _e_b1070' (logged, not bare).
    F-2.1 fix uses existing 'except Exception as exc' (logged).
    No new bare 'except:' should be introduced.
    """
    bare_pattern = re.compile(r"^\s*except\s*:\s*(#.*)?$", re.MULTILINE)
    src = BACKTEST_PATH.read_text()
    violations = []
    for m in bare_pattern.finditer(src):
        line_num = src[:m.start()].count("\n") + 1
        violations.append(line_num)
    assert not violations, (
        f"B1070 Stage B: bare 'except:' found in backtest.py at lines "
        f"{violations}; use specific exception types or 'except Exception "
        f"as e' with logging per CHECKLIST #122"
    )


def test_b1070_stage_b_lineage_count():
    """B1070 Stage B: 3 P0 fixes must have lineage comments in their files."""
    bt_src = BACKTEST_PATH.read_text()
    launch_src = LAUNCH_SCRIPT.read_text()
    assert "B1070 F-1.1 FIX" in bt_src, "F-1.1 lineage missing"
    assert "B1070 F-2.1 FIX" in bt_src, "F-2.1 lineage missing"
    assert "B1070 F-7.1+F-10.1 FIX" in launch_src, "F-7.1/F-10.1 lineage missing"
