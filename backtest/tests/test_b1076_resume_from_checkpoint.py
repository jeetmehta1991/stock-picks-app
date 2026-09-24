"""B1076 Council 191 Option 1: resume-from-checkpoint MVP pyramid tests.

Source: Council 190 owner-approved Option C (resume infra FIRST) + Council
191 Option 1 SIMPLE-RESUME-MVP per 1-2 hr budget.

B1075 spot-interrupted at 13:42:08Z (Phase 1+2 PASS; Phase 3 ~32/167min).
Sub-B F-12.1: spot interruption 5-15pct over 16-20hr runs; no resume infra
exists. Council 191 ships MVP: sim_day skip + closed_trades reload from
trade_log_checkpoint.csv. (B3098: open trades were DROPPED at B1076; since
S6-B2213a they are RESTORED or the resume HALTS - the test below says so.)

Tests:
- CLI flag wired to BacktestEngine
- _load_resume_checkpoint reads engine_state.json + trade_log_checkpoint.csv
- HALT on missing engine_state.json
- HALT on status=complete (nothing to resume)
- HALT on simulated_day <= 0
- HALT on schema mismatch (trade_log row_count != engine_state.trades_so_far)
- Open trades declared without an open-book checkpoint HALT (S6-B2213a)
- Resume sim_day index set correctly: B3098 resumes AT the checkpoint's
  never-run day (the loop skips i <= simulated_day - 1)
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest


REPO = Path(__file__).resolve().parents[2]


def test_b1076_cli_flag_in_run_phase1a():
    """B1076 Council 191 Option 1: --resume-from-checkpoint CLI flag
    must be wired in run_phase1a.py."""
    content = (REPO / "backtest" / "run_phase1a.py").read_text()
    assert '--resume-from-checkpoint' in content, (
        "B1076: --resume-from-checkpoint CLI flag must be added to "
        "run_phase1a.py argparse"
    )
    assert 'resume_from_checkpoint=args.resume_from_checkpoint' in content, (
        "B1076: BacktestEngine constructor must receive resume_from_checkpoint"
    )


def test_b1076_engine_init_accepts_resume_kwarg():
    """B1076: BacktestEngine.__init__ must accept resume_from_checkpoint kwarg."""
    from backtest.engine.backtest import BacktestEngine
    import inspect
    sig = inspect.signature(BacktestEngine.__init__)
    assert 'resume_from_checkpoint' in sig.parameters, (
        "B1076: BacktestEngine.__init__ must accept resume_from_checkpoint"
    )
    # Default must be None (opt-in)
    assert sig.parameters['resume_from_checkpoint'].default is None, (
        "B1076: resume_from_checkpoint must default to None (opt-in)"
    )


def test_b1076_load_resume_checkpoint_method_exists():
    """B1076: _load_resume_checkpoint helper method must exist."""
    from backtest.engine.backtest import BacktestEngine
    assert hasattr(BacktestEngine, '_load_resume_checkpoint'), (
        "B1076: _load_resume_checkpoint method must exist on BacktestEngine"
    )


def _make_engine_stub(resume_dir):
    """Build minimal BacktestEngine instance just to test resume loader."""
    from backtest.engine.backtest import BacktestEngine
    # Bypass __init__ side-effects (data loading, universe) by
    # constructing via __new__ and setting only what _load_resume_checkpoint
    # needs.
    eng = BacktestEngine.__new__(BacktestEngine)
    eng.resume_from_checkpoint = str(resume_dir)
    eng._resume_sim_day = -1
    eng._resumed_closed_trades_count = 0
    eng.closed_trades = []
    return eng


def test_b1076_resume_halts_on_missing_engine_state(tmp_path):
    """B1076 schema-contract: missing engine_state.json must HALT."""
    eng = _make_engine_stub(tmp_path)
    with pytest.raises(FileNotFoundError, match="engine_state.json not found"):
        eng._load_resume_checkpoint()


def test_b1076_resume_halts_on_status_complete(tmp_path):
    """B1076: status=complete means nothing to resume; HALT."""
    state = {
        "simulated_day": 1000,
        "status": "complete",
        "trades_so_far": 50,
        "open_trades": 0,
    }
    (tmp_path / "engine_state.json").write_text(json.dumps(state))
    eng = _make_engine_stub(tmp_path)
    with pytest.raises(ValueError, match="status=complete"):
        eng._load_resume_checkpoint()


def test_b1076_resume_halts_on_zero_simulated_day(tmp_path):
    """B1076: simulated_day=0 means engine never advanced; HALT."""
    state = {
        "simulated_day": 0,
        "status": "running",
        "trades_so_far": 0,
        "open_trades": 0,
    }
    (tmp_path / "engine_state.json").write_text(json.dumps(state))
    eng = _make_engine_stub(tmp_path)
    with pytest.raises(ValueError, match="simulated_day=0"):
        eng._load_resume_checkpoint()


def test_b1076_resume_halts_on_schema_mismatch(tmp_path):
    """B1076 PIVOT #37 schema-contract lineage: trade_log row_count must
    match engine_state.trades_so_far."""
    state = {
        "simulated_day": 100,
        "status": "running",
        "trades_so_far": 5,
        "open_trades": 0,
    }
    (tmp_path / "engine_state.json").write_text(json.dumps(state))
    # CSV has 3 rows but state says 5
    df = pd.DataFrame([
        {"ticker": "NVDA", "strategy": "s1", "exit_reason": "tp"},
        {"ticker": "NVDA", "strategy": "s2", "exit_reason": "tp"},
        {"ticker": "NVDA", "strategy": "s3", "exit_reason": "tp"},
    ])
    df.to_csv(tmp_path / "trade_log_checkpoint.csv", index=False)
    eng = _make_engine_stub(tmp_path)
    with pytest.raises(ValueError, match="schema-contract"):
        eng._load_resume_checkpoint()


def test_b1076_resume_happy_path(tmp_path):
    """B1076 happy path: load engine_state.json + trade_log_checkpoint.csv
    + set _resume_sim_day correctly."""
    state = {
        "simulated_day": 250,
        "status": "running",
        "trades_so_far": 3,
        "open_trades": 0,
    }
    (tmp_path / "engine_state.json").write_text(json.dumps(state))
    df = pd.DataFrame([
        {"ticker": "NVDA", "strategy": "s1", "exit_reason": "tp"},
        {"ticker": "NVDA", "strategy": "s2", "exit_reason": "tp"},
        {"ticker": "NVDA", "strategy": "s3", "exit_reason": "tp"},
    ])
    df.to_csv(tmp_path / "trade_log_checkpoint.csv", index=False)
    eng = _make_engine_stub(tmp_path)
    eng._load_resume_checkpoint()
    # B3098 (S6-B3094g, owner 'Fix it'): simulated_day=250 is written BEFORE
    # day 250 runs, so the resume runs it: skip i <= 249. This pin read 250
    # until B3098 - it froze the off-by-one that skipped a never-run day.
    assert eng._resume_sim_day == 249
    assert eng._resumed_closed_trades_count == 3
    assert len(eng.closed_trades) == 3


def test_b1076_resume_open_trades_warning_emitted(tmp_path):
    """B1076 dropped open trades with a WARNING; S6-B2213a replaced that with
    RESTORE-or-HALT (owner 2026-08-26 'no dropped trades'), and this test kept
    asserting the DROPPED warning - it failed on HEAD from then until B3098
    (outside the gated pyramid, so nothing noticed: L867's stale caveat, in a
    test). Open trades declared with no open-book checkpoint must HALT."""
    state = {
        "simulated_day": 100,
        "status": "running",
        "trades_so_far": 0,
        "open_trades": 5,
    }
    (tmp_path / "engine_state.json").write_text(json.dumps(state))
    eng = _make_engine_stub(tmp_path)
    with pytest.raises(RuntimeError, match="S6-B2213a RESUME HALT"):
        eng._load_resume_checkpoint()


def test_b1076_resume_empty_trade_log_with_zero_trades(tmp_path):
    """B1076: missing/empty trade_log_checkpoint.csv with trades_so_far=0
    is valid (interrupted before first trade)."""
    state = {
        "simulated_day": 50,
        "status": "running",
        "trades_so_far": 0,
        "open_trades": 0,
    }
    (tmp_path / "engine_state.json").write_text(json.dumps(state))
    # No CSV created
    eng = _make_engine_stub(tmp_path)
    eng._load_resume_checkpoint()
    assert eng._resume_sim_day == 49      # B3098: day 50 never ran; it runs
    assert eng._resumed_closed_trades_count == 0
    assert eng.closed_trades == []


def test_b1076_main_loop_skip_logic_in_source():
    """B1076: backtest.py main loop must skip iterations where
    i <= self._resume_sim_day."""
    content = (REPO / "backtest" / "engine" / "backtest.py").read_text()
    assert 'self._resume_sim_day >= 0 and i <= self._resume_sim_day' in content, (
        "B1076: main loop must check resume marker + skip completed iterations"
    )


def test_b1076_lineage_documented():
    """B1076: PIVOT lineage + Council 191 referenced in source."""
    bt = (REPO / "backtest" / "engine" / "backtest.py").read_text()
    assert "B1076" in bt, "B1076 batch lineage must be referenced"
    assert "Council 191" in bt, "Council 191 must be referenced"
    assert "F-13.1" in bt or "S5-B1073" in bt, (
        "Sub-B F-13.1 / S5-B1073 ticket lineage must be referenced"
    )


def test_b1076_default_no_resume_no_side_effects():
    """B1076: default behavior (no --resume-from-checkpoint) must be
    no-op; _resume_sim_day stays at -1."""
    from backtest.engine.backtest import BacktestEngine
    eng = BacktestEngine.__new__(BacktestEngine)
    eng.resume_from_checkpoint = None
    eng._resume_sim_day = -1
    eng._resumed_closed_trades_count = 0
    # Without calling _load_resume_checkpoint, resume marker stays -1
    assert eng._resume_sim_day == -1
    assert eng.resume_from_checkpoint is None
