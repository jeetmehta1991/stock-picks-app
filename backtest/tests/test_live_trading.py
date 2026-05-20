"""Tests for Stage 4 live trading module (Batch 247)."""
from __future__ import annotations

from datetime import date

import pytest

from backtest.live_trading.ib_executor import (
    IBExecutionResult,
    connect_ib,
    place_bracket_order,
)
from backtest.live_trading.risk_overlay import (
    DEC_515_LEVEL_6_DD_RECOVERY_PCT,
    DEC_515_LEVEL_6_DD_TRIGGER_PCT,
    LIVE_DAILY_LOSS_LIMIT_PCT,
    LiveRiskState,
    RiskCheckResult,
    check_pre_trade,
    compute_shares_for_pick,
    update_halt_state,
)


# ---------------------------------------------------------------------------
# risk_overlay tests
# ---------------------------------------------------------------------------
def test_check_pre_trade_approves_valid_pick():
    state = LiveRiskState()
    pick = {"confidence_tier": "HIGH", "entry_price": 200.0}
    r = check_pre_trade(pick, state)
    assert r.approved
    assert r.adjusted_size_pct == 3.0


def test_check_pre_trade_blocks_avoid_tier():
    state = LiveRiskState()
    pick = {"confidence_tier": "AVOID", "entry_price": 200.0}
    r = check_pre_trade(pick, state)
    assert not r.approved
    assert "avoid_or_low_tier" in r.reason


def test_check_pre_trade_blocks_when_halt_active():
    state = LiveRiskState(halt_active=True, halt_reason="dd_breach")
    pick = {"confidence_tier": "HIGH", "entry_price": 200.0}
    r = check_pre_trade(pick, state)
    assert not r.approved
    assert "halt_active" in r.reason


def test_check_pre_trade_blocks_at_daily_loss_limit():
    state = LiveRiskState(
        portfolio_value=96_500,  # -3.5% from 100K
        daily_starting_value=100_000,
        portfolio_peak=100_000,
    )
    pick = {"confidence_tier": "HIGH", "entry_price": 200.0}
    r = check_pre_trade(pick, state)
    assert not r.approved
    assert r.halt_signal
    assert "daily_loss_limit" in r.reason


def test_check_pre_trade_blocks_at_dec_515_dd():
    state = LiveRiskState(
        portfolio_value=84_000,  # -16% from peak
        portfolio_peak=100_000,
        daily_starting_value=84_500,
    )
    pick = {"confidence_tier": "HIGH", "entry_price": 200.0}
    r = check_pre_trade(pick, state)
    assert not r.approved
    assert r.halt_signal
    assert "dec_515" in r.reason


def test_check_pre_trade_invalid_entry_price():
    state = LiveRiskState()
    pick = {"confidence_tier": "HIGH", "entry_price": 0.0}
    r = check_pre_trade(pick, state)
    assert not r.approved


def test_update_halt_state_activates_at_trigger():
    state = LiveRiskState(portfolio_value=84_000, portfolio_peak=100_000)
    halted = update_halt_state(state)
    assert halted
    assert state.halt_active


def test_update_halt_state_recovers_below_threshold():
    state = LiveRiskState(
        portfolio_value=96_000,  # 4% DD; below 5% recovery
        portfolio_peak=100_000,
        halt_active=True,
    )
    halted = update_halt_state(state)
    assert not halted
    assert not state.halt_active


def test_compute_shares_for_pick():
    pick = {"position_size_pct": 3.0, "entry_price": 200.0}
    shares = compute_shares_for_pick(pick, portfolio_value=100_000, cash_available=50_000)
    # 3% of 100K = 3000; 3000 / 200 = 15
    assert shares == 15


def test_compute_shares_for_pick_respects_cash_buffer():
    pick = {"position_size_pct": 5.0, "entry_price": 200.0}
    shares = compute_shares_for_pick(pick, portfolio_value=100_000, cash_available=1000)
    # target $5000 but only $1000 cash; 95% buffer = $950; 950/200 = 4
    assert shares == 4


def test_compute_shares_for_pick_zero_on_zero_size():
    pick = {"position_size_pct": 0.0, "entry_price": 200.0}
    assert compute_shares_for_pick(pick, 100_000, 50_000) == 0


# ---------------------------------------------------------------------------
# ib_executor tests
# ---------------------------------------------------------------------------
def test_place_bracket_order_dry_run(capsys):
    r = place_bracket_order(
        ticker="AAPL", direction="long", shares=10,
        entry_price=200.0, stop_price=196.0, dry_run=True,
    )
    assert r.success
    assert r.dry_run
    assert r.shares == 10
    assert "STUB-AAPL" in r.order_id
    captured = capsys.readouterr()
    assert "DRY RUN" in captured.out


def test_place_bracket_order_auto_target():
    r = place_bracket_order(
        ticker="AAPL", direction="long", shares=10,
        entry_price=200.0, stop_price=196.0,  # 4 risk
        dry_run=True,
    )
    # Auto target = 200 + 2 * 4 = 208
    assert r.success


def test_place_bracket_order_short_direction():
    r = place_bracket_order(
        ticker="AAPL", direction="short", shares=10,
        entry_price=200.0, stop_price=204.0, dry_run=True,
    )
    assert r.success
    assert r.dry_run


def test_connect_ib_dry_run_returns_none():
    ib = connect_ib(dry_run=True)
    assert ib is None
