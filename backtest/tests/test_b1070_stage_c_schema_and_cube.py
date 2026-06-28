"""B1070 Stage C ITEM 1 + ITEM 2 pyramid tests.

# Source: Council 172/174/177 per CHECKLIST #77 + #115 + owner directive
# 2026-06-28 'A and c' + 'Yes council this. Ensure thats its engine
# implemented. No silent misses.'

ITEM 1: (c) schema - exit_method column in trade_log.csv
ITEM 2: (a) STRATEGY_EXIT_OVERRIDE re-derive (deferred to ITEM 2 commit)
"""
from __future__ import annotations

import pandas as pd
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXIT_MGR_PATH = REPO / "backtest" / "engine" / "exit_manager.py"


# ============================ ITEM 1 schema field =========================

def test_b1070_stage_c_closed_trade_has_exit_method_field():
    """B1070 Stage C ITEM 1: ClosedTrade dataclass must include
    exit_method field (string, default 'trailing_stop')."""
    from backtest.engine.exit_manager import ClosedTrade
    from dataclasses import fields
    field_names = {f.name for f in fields(ClosedTrade)}
    assert "exit_method" in field_names, (
        "B1070 Stage C ITEM 1: ClosedTrade must have exit_method field"
    )
    assert "exit_reason" in field_names, (
        "B1070: exit_reason must remain (distinct from exit_method)"
    )


def test_b1070_stage_c_resolve_exit_method_helper():
    """B1070 Stage C ITEM 1: _b1070_resolve_exit_method must return
    STRATEGY_EXIT_OVERRIDE value for known + 'trailing_stop' default."""
    from backtest.engine.exit_manager import _b1070_resolve_exit_method
    # Strategy in OVERRIDE returns its exit_method
    from backtest.config import STRATEGY_EXIT_OVERRIDE
    if STRATEGY_EXIT_OVERRIDE:
        known_strat = next(iter(STRATEGY_EXIT_OVERRIDE.keys()))
        expected = STRATEGY_EXIT_OVERRIDE[known_strat].get(
            "exit_method", "trailing_stop"
        )
        actual = _b1070_resolve_exit_method(known_strat)
        assert actual == expected, (
            f"B1070: known strategy {known_strat} should return its OVERRIDE "
            f"exit_method ({expected}), got {actual}"
        )
    # Unknown strategy returns trailing_stop default
    unknown = _b1070_resolve_exit_method("zzz_not_a_real_strategy_xxx")
    assert unknown == "trailing_stop", (
        f"B1070: unknown strategy must default to 'trailing_stop', got {unknown}"
    )


def test_b1070_stage_c_exit_method_threaded_to_closed_trade():
    """B1070 Stage C ITEM 1: close_trade() must populate exit_method from
    resolver (verified via integration: build OpenTrade, close, inspect)."""
    from backtest.engine.exit_manager import (
        OpenTrade, close_trade, _b1070_resolve_exit_method
    )
    # Use a known OVERRIDE strategy (stochrsi_oversold per B309/B414)
    from backtest.config import STRATEGY_EXIT_OVERRIDE
    if not STRATEGY_EXIT_OVERRIDE:
        # No overrides defined; skip integration test
        return
    test_strat = next(iter(STRATEGY_EXIT_OVERRIDE.keys()))
    expected_em = _b1070_resolve_exit_method(test_strat)
    # Synthesize minimal OpenTrade
    trade = OpenTrade(
        ticker="TEST",
        entry_date=date(2024, 1, 1),
        direction="long",
        strategy=test_strat,
        category="momentum",
        sector="Information Technology",
        confidence_tier="MEDIUM",
        regime_at_entry="bull",
        conversion_pair_id=None,
        entry_price=100.0,
        initial_stop=95.0,
        highest_close=100.0,
        trailing_stop=95.0,
        circuit_breaker_triggered=None,
        signals_at_entry={},
        context_bullets=[],
        context_paragraph="",
        max_adverse_excursion=0.0,
        max_favourable_excursion=0.0,
        smart_money_score=0,
        macro_score=0,
        sentiment_score=0,
    )
    closed = close_trade(
        trade=trade,
        exit_price=105.0,
        exit_date=date(2024, 1, 15),
        exit_reason="trailing_stop",
        max_adverse=0.0,
        max_favourable=5.0,
    )
    assert closed.exit_method == expected_em, (
        f"B1070 Stage C ITEM 1: closed.exit_method ({closed.exit_method}) "
        f"must match resolver output ({expected_em})"
    )


def test_b1070_stage_c_trade_log_csv_has_exit_method_column():
    """B1070 Stage C ITEM 1: writer auto-emits exit_method column via
    vars(ClosedTrade) -> DataFrame -> CSV pipeline."""
    from backtest.engine.exit_manager import ClosedTrade
    from dataclasses import asdict
    # Synthesize ClosedTrade + verify dataframe column
    ct = ClosedTrade(
        ticker="TEST", entry_date=date(2024, 1, 1), exit_date=date(2024, 1, 15),
        direction="long", strategy="zzz_test", category="momentum",
        sector="Tech", confidence_tier="MEDIUM", regime="bull",
        exit_reason="trailing_stop", entry_price=100.0, exit_price=105.0,
        initial_stop=95.0, highest_close=105.0, trailing_stop_at_exit=95.0,
        pnl_pct=5.0, pnl_dollar=500.0, win=True, hold_days=14,
        max_adverse_excursion=0.0, max_favourable_excursion=5.0,
        signals_at_entry={}, context_bullets=[], context_paragraph="",
        fail_reason="",
        exit_method="breakeven_plus_trail",
    )
    # vars() includes the new field (this is what backtest.py uses)
    d = vars(ct)
    assert "exit_method" in d, (
        "B1070: vars(ClosedTrade) must include exit_method"
    )
    # DataFrame round-trip
    df = pd.DataFrame([vars(ct)])
    assert "exit_method" in df.columns, (
        "B1070: pd.DataFrame from ClosedTrade vars must contain exit_method"
    )
    assert df["exit_method"].iloc[0] == "breakeven_plus_trail", (
        "B1070: exit_method value must round-trip through DataFrame"
    )


def test_b1070_stage_c_item_1_lineage_documented():
    """B1070 Stage C ITEM 1: lineage comment in exit_manager.py."""
    src = EXIT_MGR_PATH.read_text()
    assert "B1070 Stage C ITEM 1" in src, (
        "B1070: exit_manager.py must reference 'Stage C ITEM 1' for the "
        "exit_method field + resolver lineage"
    )
    assert "_b1070_resolve_exit_method" in src, (
        "B1070: helper function name must be present"
    )


def test_b1070_stage_c_exit_method_distinct_from_exit_reason():
    """B1070 Stage C ITEM 1: PIN that exit_method is config-time +
    exit_reason is runtime-triggered (distinction NOT collapsed)."""
    src = EXIT_MGR_PATH.read_text()
    assert "exit_reason:        str" in src or "exit_reason: str" in src.replace(" ", ""), (
        "B1070: exit_reason field must remain (runtime trigger)"
    )
    # exit_method default is trailing_stop string
    assert 'exit_method:          str = "trailing_stop"' in src, (
        "B1070: exit_method field must default to 'trailing_stop'"
    )
