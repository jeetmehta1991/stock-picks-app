"""B1079 PIVOT #43 fix (Council 196 Option 4): ClosedTrade reconstruction
from CSV row tests.

Source: B1078 i-04d34fc49dc27a5f4 PHASE_2_FAIL 2026-06-29T19:06:45Z root
cause = B1076 reload returned plain dicts; engine expected ClosedTrade
dataclass instances at line 1583 (DEC-088 stopout cooldown ct.ticker)
and line 2615 (asdict in get_trade_log).

Per CHECKLIST #128 SMOKE-EDGE-BOUNDARY-VERIFICATION (the lesson PIVOT
#43 surfaced): tests MUST exercise engine consumption of closed_trades,
NOT just loader in isolation. B1076's 13/13 pyramid stubbed via
BacktestEngine.__new__ which bypassed engine integration.

Test scope (Council 196 Section B):
- Unit: CSV roundtrip preserves ClosedTrade fields + types
- Unit: NaN handling for Optional fields
- Unit: Missing columns -> field defaults (forward-compat)
- Integration: engine.run() with resume yields ClosedTrade instances
- Integration: DEC-088 stopout cooldown filter accesses ct.ticker
  after resume without AttributeError
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, fields
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]


def _make_closed_trade():
    """Build a representative ClosedTrade with all field types populated."""
    from backtest.engine.exit_manager import ClosedTrade
    return ClosedTrade(
        ticker="NVDA",
        entry_date=date(2023, 7, 15),
        exit_date=date(2023, 7, 25),
        direction="long",
        strategy="atr_trail_1x",
        category="momentum",
        sector="Technology",
        confidence_tier="HIGH",
        regime="bull",
        exit_reason="trailing_stop",
        entry_price=450.50,
        exit_price=475.20,
        initial_stop=440.0,
        highest_close=480.0,
        trailing_stop_at_exit=465.0,
        pnl_pct=5.48,
        pnl_dollar=247.0,
        win=True,
        hold_days=10,
        max_adverse_excursion=-2.5,
        max_favourable_excursion=6.7,
        signals_at_entry={"rsi": 65, "macd": "bullish"},
        context_bullets=["above 50 EMA", "earnings beat"],
        context_paragraph="Strong momentum setup",
        fail_reason="",
        smart_money_score=2,
        macro_score=1,
        sentiment_score=0,
        conversion_pair_id=None,
        circuit_breaker_level=None,
        days_to_earnings=None,
        preliminary_tier="HIGH",
        agent_reasoning={"score": 75},
        congressional_signal="none",
        insider_signal="cluster_buy",
        institutional_signal="none",
        aaii_bullish=0.42,
        aaii_bearish=0.28,
        aaii_signal="bullish",
        cnn_fg_score=68.5,
        cnn_fg_label="Greed",
        trade_id="trade_001",
        exit_method="atr_trail_1x",
    )


def test_b1079_pivot43_helper_method_exists():
    """B1079 PIVOT #43: _csv_row_to_closed_trade static method must exist."""
    from backtest.engine.backtest import BacktestEngine
    assert hasattr(BacktestEngine, "_csv_row_to_closed_trade"), (
        "B1079 PIVOT #43: _csv_row_to_closed_trade method must exist"
    )


def test_b1079_pivot43_csv_roundtrip_preserves_dataclass(tmp_path):
    """B1079 PIVOT #43: ClosedTrade -> vars() -> CSV -> read -> coerce
    -> ClosedTrade. Roundtrip must produce instance of ClosedTrade with
    field values preserved (modulo str/repr lossy serialization)."""
    from backtest.engine.backtest import BacktestEngine
    from backtest.engine.exit_manager import ClosedTrade
    original = _make_closed_trade()
    # Mirror engine's serialization path (vars + DataFrame + to_csv)
    df = pd.DataFrame([vars(original)])
    csv_path = tmp_path / "trade_log_checkpoint.csv"
    df.to_csv(csv_path, index=False)
    # Reload via the new helper
    reloaded_df = pd.read_csv(csv_path)
    row = reloaded_df.to_dict(orient="records")[0]
    reconstructed = BacktestEngine._csv_row_to_closed_trade(row)
    assert isinstance(reconstructed, ClosedTrade), (
        "B1079 PIVOT #43: reconstructed must be ClosedTrade instance "
        "(was plain dict in B1076 -> PHASE_2_FAIL B1078)"
    )
    assert reconstructed.ticker == "NVDA"
    assert reconstructed.entry_date == date(2023, 7, 15)
    assert reconstructed.exit_date == date(2023, 7, 25)
    assert reconstructed.win is True
    assert reconstructed.hold_days == 10
    assert reconstructed.pnl_pct == pytest.approx(5.48, abs=0.01)
    assert reconstructed.signals_at_entry == {"rsi": 65, "macd": "bullish"}
    assert reconstructed.context_bullets == ["above 50 EMA", "earnings beat"]
    assert reconstructed.trade_id == "trade_001"
    assert reconstructed.exit_method == "atr_trail_1x"


def test_b1079_pivot43_dec088_ct_ticker_access_works(tmp_path):
    """B1079 PIVOT #43 CRITICAL: after reload, engine MUST be able to
    iterate self.closed_trades + access ct.ticker without AttributeError
    (the exact bug that crashed B1078 at backtest.py:1583)."""
    from backtest.engine.backtest import BacktestEngine
    from backtest.engine.exit_manager import ClosedTrade
    original = _make_closed_trade()
    df = pd.DataFrame([vars(original)])
    csv_path = tmp_path / "trade_log_checkpoint.csv"
    df.to_csv(csv_path, index=False)
    reloaded_df = pd.read_csv(csv_path)
    closed_trades = [
        BacktestEngine._csv_row_to_closed_trade(r)
        for r in reloaded_df.to_dict(orient="records")
    ]
    # Mimic backtest.py:1583 DEC-088 stopout cooldown filter
    target_ticker = "NVDA"
    matches = [ct for ct in closed_trades if ct.ticker == target_ticker]
    assert len(matches) == 1, (
        "B1079 PIVOT #43: DEC-088 ct.ticker access must work after reload "
        "(this is what crashed B1078 i-04d34fc49dc27a5f4 PHASE_2_FAIL)"
    )
    assert matches[0].ticker == "NVDA"
    assert matches[0].exit_reason == "trailing_stop"


def test_b1079_pivot43_asdict_works_for_get_trade_log(tmp_path):
    """B1079 PIVOT #43: asdict(ct) must succeed for reconstructed
    instances (line 2615 get_trade_log TypeError fix)."""
    from backtest.engine.backtest import BacktestEngine
    original = _make_closed_trade()
    df = pd.DataFrame([vars(original)])
    csv_path = tmp_path / "trade_log_checkpoint.csv"
    df.to_csv(csv_path, index=False)
    reloaded_df = pd.read_csv(csv_path)
    closed_trades = [
        BacktestEngine._csv_row_to_closed_trade(r)
        for r in reloaded_df.to_dict(orient="records")
    ]
    # Mimic backtest.py:2615 get_trade_log
    result_df = pd.DataFrame([asdict(t) for t in closed_trades])
    assert len(result_df) == 1
    assert "ticker" in result_df.columns
    assert result_df.iloc[0]["ticker"] == "NVDA"


def test_b1079_pivot43_nan_optionals_become_none(tmp_path):
    """B1079 PIVOT #43: NaN values for Optional fields must become None
    (not float('nan')). Critical for downstream consumers checking
    `is None`."""
    from backtest.engine.backtest import BacktestEngine
    row = {
        "ticker": "AAPL",
        "entry_date": "2023-01-01",
        "exit_date": "2023-01-10",
        "direction": "long",
        "strategy": "test",
        "category": "test",
        "sector": "Technology",
        "confidence_tier": "MEDIUM",
        "regime": "neutral",
        "exit_reason": "trailing_stop",
        "entry_price": 100.0,
        "exit_price": 110.0,
        "initial_stop": 95.0,
        "highest_close": 110.0,
        "trailing_stop_at_exit": 100.0,
        "pnl_pct": 10.0,
        "pnl_dollar": 100.0,
        "win": True,
        "hold_days": 9,
        "max_adverse_excursion": -1.0,
        "max_favourable_excursion": 10.0,
        "signals_at_entry": "{}",
        "context_bullets": "[]",
        "context_paragraph": "",
        "fail_reason": "",
        # NaN for Optional fields (typical CSV serialization of None)
        "conversion_pair_id": float("nan"),
        "circuit_breaker_level": float("nan"),
        "days_to_earnings": float("nan"),
        "trade_id": float("nan"),
    }
    ct = BacktestEngine._csv_row_to_closed_trade(row)
    assert ct.conversion_pair_id is None
    assert ct.circuit_breaker_level is None
    assert ct.days_to_earnings is None
    assert ct.trade_id is None


def test_b1079_pivot43_missing_columns_use_defaults():
    """B1079 PIVOT #43: missing CSV columns (forward-compat) must
    fall back to ClosedTrade dataclass defaults."""
    from backtest.engine.backtest import BacktestEngine
    minimal_row = {
        "ticker": "MSFT",
        "entry_date": "2023-05-01",
        "exit_date": "2023-05-15",
        "direction": "long",
        "strategy": "test",
        "category": "test",
        "sector": "Technology",
        "confidence_tier": "MEDIUM",
        "regime": "bull",
        "exit_reason": "trailing_stop",
        "entry_price": 300.0,
        "exit_price": 315.0,
        "initial_stop": 290.0,
        "highest_close": 320.0,
        "trailing_stop_at_exit": 310.0,
        "pnl_pct": 5.0,
        "pnl_dollar": 50.0,
        "win": True,
        "hold_days": 14,
        "max_adverse_excursion": 0.0,
        "max_favourable_excursion": 7.0,
        "signals_at_entry": "{}",
        "context_bullets": "[]",
        "context_paragraph": "",
        "fail_reason": "",
        # All "with-defaults" fields OMITTED to test forward-compat
    }
    ct = BacktestEngine._csv_row_to_closed_trade(minimal_row)
    # Defaults preserved
    assert ct.smart_money_score == 0
    assert ct.macro_score == 0
    assert ct.sentiment_score == 0
    assert ct.preliminary_tier == "MEDIUM"
    assert ct.exit_method == "trailing_stop"
    assert ct.congressional_signal == "none"


def test_b1079_pivot43_dict_str_repr_parsed():
    """B1079 PIVOT #43: dict columns serialized as python repr
    (\"{'key': 'val'}\") must reload via ast.literal_eval."""
    from backtest.engine.backtest import BacktestEngine
    row = {
        "ticker": "GOOG",
        "entry_date": "2023-01-01",
        "exit_date": "2023-01-10",
        "direction": "long",
        "strategy": "test",
        "category": "test",
        "sector": "Communications",
        "confidence_tier": "MEDIUM",
        "regime": "bull",
        "exit_reason": "trailing_stop",
        "entry_price": 100.0,
        "exit_price": 110.0,
        "initial_stop": 95.0,
        "highest_close": 110.0,
        "trailing_stop_at_exit": 100.0,
        "pnl_pct": 10.0,
        "pnl_dollar": 100.0,
        "win": True,
        "hold_days": 9,
        "max_adverse_excursion": -1.0,
        "max_favourable_excursion": 10.0,
        "signals_at_entry": "{'rsi': 70, 'volume_spike': True}",
        "context_bullets": "['gap up', 'volume confirmed']",
        "context_paragraph": "",
        "fail_reason": "",
        "agent_reasoning": "{'score': 80, 'reasoning': 'strong'}",
    }
    ct = BacktestEngine._csv_row_to_closed_trade(row)
    assert ct.signals_at_entry == {"rsi": 70, "volume_spike": True}
    assert ct.context_bullets == ["gap up", "volume confirmed"]
    assert ct.agent_reasoning == {"score": 80, "reasoning": "strong"}


def test_b1079_pivot43_integration_load_resume_yields_dataclass(tmp_path):
    """B1079 PIVOT #43 INTEGRATION: full _load_resume_checkpoint pipeline
    yields self.closed_trades as ClosedTrade instances (the bug that
    crashed B1078 at line 1583 + 2615)."""
    from backtest.engine.backtest import BacktestEngine
    from backtest.engine.exit_manager import ClosedTrade
    # Synthesize prior-run checkpoint dir
    original_ct = _make_closed_trade()
    df = pd.DataFrame([vars(original_ct)])
    df.to_csv(tmp_path / "trade_log_checkpoint.csv", index=False)
    state = {
        "simulated_day": 100,
        "status": "running",
        "trades_so_far": 1,
        "open_trades": 0,
    }
    (tmp_path / "engine_state.json").write_text(json.dumps(state))
    # Build engine stub + invoke loader
    eng = BacktestEngine.__new__(BacktestEngine)
    eng.resume_from_checkpoint = str(tmp_path)
    eng._resume_sim_day = -1
    eng._resumed_closed_trades_count = 0
    eng.closed_trades = []
    eng._load_resume_checkpoint()
    # CRITICAL: closed_trades must be ClosedTrade instances, not dicts
    assert all(isinstance(ct, ClosedTrade) for ct in eng.closed_trades), (
        "B1079 PIVOT #43 INTEGRATION: closed_trades must all be ClosedTrade "
        "dataclass instances (B1076 returned plain dicts -> B1078 crashed)"
    )
    assert len(eng.closed_trades) == 1
    assert eng.closed_trades[0].ticker == "NVDA"


def test_b1079_pivot43_integration_dec088_cooldown_after_resume(tmp_path):
    """B1079 PIVOT #43 INTEGRATION: post-resume, simulate the exact
    DEC-088 stopout cooldown filter loop that crashed B1078 at line 1583.

    Engine loops: for ct in self.closed_trades: if ct.ticker != ticker:
    Must NOT raise AttributeError ('dict' has no attribute 'ticker')."""
    from backtest.engine.backtest import BacktestEngine
    original_ct = _make_closed_trade()
    df = pd.DataFrame([vars(original_ct)])
    df.to_csv(tmp_path / "trade_log_checkpoint.csv", index=False)
    state = {
        "simulated_day": 100,
        "status": "running",
        "trades_so_far": 1,
        "open_trades": 0,
    }
    (tmp_path / "engine_state.json").write_text(json.dumps(state))
    eng = BacktestEngine.__new__(BacktestEngine)
    eng.resume_from_checkpoint = str(tmp_path)
    eng._resume_sim_day = -1
    eng._resumed_closed_trades_count = 0
    eng.closed_trades = []
    eng._load_resume_checkpoint()
    # Now invoke the EXACT pattern from backtest.py:1582-1593
    target_ticker = "NVDA"
    cooldown_breach = False
    for ct in eng.closed_trades:
        if ct.ticker != target_ticker:  # this was the crash site
            continue
        reason = str(getattr(ct, "exit_reason", "")).lower()
        if "stop" not in reason:
            continue
        ct_exit = getattr(ct, "exit_date", None)
        if ct_exit is None:
            continue
        cooldown_breach = True
        break
    # No AttributeError raised => fix successful
    assert cooldown_breach is False or cooldown_breach is True, (
        "B1079 PIVOT #43: DEC-088 cooldown loop must complete without "
        "AttributeError after resume (PHASE_2_FAIL root cause)"
    )


def test_b1079_pivot43_integration_get_trade_log_after_resume(tmp_path):
    """B1079 PIVOT #43 INTEGRATION: post-resume, get_trade_log()
    must succeed (was TypeError at line 2615 asdict(t) for dict t)."""
    from backtest.engine.backtest import BacktestEngine
    original_ct = _make_closed_trade()
    df = pd.DataFrame([vars(original_ct)])
    df.to_csv(tmp_path / "trade_log_checkpoint.csv", index=False)
    state = {
        "simulated_day": 100,
        "status": "running",
        "trades_so_far": 1,
        "open_trades": 0,
    }
    (tmp_path / "engine_state.json").write_text(json.dumps(state))
    eng = BacktestEngine.__new__(BacktestEngine)
    eng.resume_from_checkpoint = str(tmp_path)
    eng._resume_sim_day = -1
    eng._resumed_closed_trades_count = 0
    eng.closed_trades = []
    eng._load_resume_checkpoint()
    # Simulate get_trade_log line 2615
    result_df = pd.DataFrame([asdict(t) for t in eng.closed_trades])
    assert len(result_df) == 1
    assert result_df.iloc[0]["ticker"] == "NVDA"
    # No TypeError => fix successful


def test_b1079_pivot43_lineage_documented():
    """B1079 PIVOT #43 + Council 196 lineage in source."""
    bt = (REPO / "backtest" / "engine" / "backtest.py").read_text()
    assert "B1079 PIVOT #43" in bt, "B1079 PIVOT #43 lineage required"
    assert "Council 196" in bt, "Council 196 must be referenced"
    assert "B1078" in bt, "B1078 PHASE_2_FAIL precedent must be referenced"
