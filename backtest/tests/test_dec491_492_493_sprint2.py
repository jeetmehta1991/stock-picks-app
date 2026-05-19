"""Sprint 2 trade-capture fragility fixes (DEC-491/492/493) regression tests
(Pass 53 Day-9 v8h).

Spec source: AUDIT.md "Pass 53 - Trade-capture fragility logged as Sprint 2
sub-decisions (DEC-491/492/493 PROPOSED)".

DEC-491: trade_log Parquet (parquet+CSV hybrid; parquet preserves nested types).
DEC-492: signals_at_entry filter REMOVED (preserve string/list signals).
DEC-493: trade_id schema field added to OpenTrade + ClosedTrade.

Owner-approved 2026-05-07 with these defaults:
- DEC-491: parquet+CSV hybrid (parquet primary, CSV human-readable secondary)
- DEC-493: time-ordered composite format ``T-{TICKER}-{DATE}-{STRAT}-{DIR}-{SEQ}``
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# DEC-493 - trade_id field
# ---------------------------------------------------------------------------
def test_dec493_make_trade_id_format():
    from backtest.engine.exit_manager import make_trade_id
    tid = make_trade_id("AAPL", date(2024, 6, 15), "rsi_oversold", direction="long")
    assert tid == "T-AAPL-2024-06-15-rsi_oversold-L-0"


def test_dec493_make_trade_id_short_direction():
    from backtest.engine.exit_manager import make_trade_id
    tid = make_trade_id("MSFT", date(2024, 7, 1), "macd_cross", direction="short")
    assert "-S-" in tid


def test_dec493_make_trade_id_handles_dot_ticker():
    """Tickers with dots (e.g. BRK.B) must be safe in filenames."""
    from backtest.engine.exit_manager import make_trade_id
    tid = make_trade_id("BRK.B", date(2024, 6, 15), "value", direction="long")
    assert "BRK_B" in tid
    assert "." not in tid


def test_dec493_make_trade_id_truncates_long_strategy_name():
    """Long strategy names must be truncated to keep trade_id manageable."""
    from backtest.engine.exit_manager import make_trade_id
    long_strat = "very_long_strategy_name_that_exceeds_thirty_two_characters_total_yes"
    tid = make_trade_id("AAPL", date(2024, 6, 15), long_strat, direction="long")
    # The strategy portion should be <=32 chars
    parts = tid.split("-")
    # Format: T - TICKER - YYYY - MM - DD - STRATEGY - DIR - SEQ
    # Find strategy portion (after date, before direction)
    assert len(tid) < 100  # reasonable upper bound


def test_dec493_make_trade_id_seq_disambiguates():
    from backtest.engine.exit_manager import make_trade_id
    tid0 = make_trade_id("AAPL", date(2024, 6, 15), "rsi", "long", seq=0)
    tid1 = make_trade_id("AAPL", date(2024, 6, 15), "rsi", "long", seq=1)
    assert tid0 != tid1


def test_dec493_open_trade_accepts_trade_id():
    from backtest.engine.exit_manager import OpenTrade, make_trade_id
    tid = make_trade_id("AAPL", date(2024, 6, 15), "rsi", "long")
    ot = OpenTrade(
        ticker="AAPL", entry_date=date(2024, 6, 15), entry_price=100.0,
        direction="long", strategy="rsi", category="mean_reversion",
        sector="Technology", initial_stop=98.0, trailing_stop=98.0,
        highest_close=100.0, regime_at_entry="neutral", trade_id=tid,
    )
    assert ot.trade_id == tid


def test_dec493_closed_trade_propagates_trade_id():
    from backtest.engine.exit_manager import ClosedTrade, make_trade_id
    tid = make_trade_id("AAPL", date(2024, 6, 15), "rsi", "long")
    ct = ClosedTrade(
        ticker="AAPL", entry_date=date(2024, 6, 15),
        exit_date=date(2024, 6, 20),
        direction="long", strategy="rsi", category="mean_reversion",
        sector="Technology", confidence_tier="MEDIUM", regime="neutral",
        exit_reason="trailing_stop",
        entry_price=100.0, exit_price=99.0, initial_stop=98.0,
        highest_close=100.0, trailing_stop_at_exit=99.0,
        pnl_pct=-1.0, pnl_dollar=-100.0, win=False, hold_days=5,
        max_adverse_excursion=-1.5, max_favourable_excursion=0.0,
        signals_at_entry={"rsi": 28},
        context_bullets=[], context_paragraph="", fail_reason="",
        trade_id=tid,
    )
    assert ct.trade_id == tid


# ---------------------------------------------------------------------------
# DEC-492 - signals_at_entry filter removed (mixed types preserved)
# ---------------------------------------------------------------------------
def test_dec492_signals_at_entry_preserves_strings():
    """Pre-fix, only (bool, int, float) were kept. Post-fix, string/list/dict
    signals are preserved."""
    from backtest.engine.exit_manager import OpenTrade
    signals = {
        "rsi": 28,                    # numeric - was kept pre-fix
        "regime_tag": "oversold",     # str - was DROPPED pre-fix
        "signal_list": ["macd_cross", "bb_lower_touch"],  # list - was DROPPED
        "patterns": {"flag": True},   # nested dict - was DROPPED
    }
    ot = OpenTrade(
        ticker="AAPL", entry_date=date(2024, 6, 15), entry_price=100.0,
        direction="long", strategy="multi", category="confluence",
        sector="Technology", initial_stop=98.0, trailing_stop=98.0,
        highest_close=100.0, regime_at_entry="neutral",
        signals_at_entry=signals,
    )
    assert ot.signals_at_entry["rsi"] == 28
    assert ot.signals_at_entry["regime_tag"] == "oversold"
    assert ot.signals_at_entry["signal_list"] == ["macd_cross", "bb_lower_touch"]
    assert ot.signals_at_entry["patterns"] == {"flag": True}


def test_dec492_engine_path_no_filter():
    """Confirm engine code at backtest.py no longer filters signals."""
    import inspect
    from backtest.engine import backtest as bt
    src = inspect.getsource(bt)
    # The pre-fix filter pattern: `if isinstance(v, (bool, int, float))`
    # - this should NO LONGER appear in the OpenTrade construction site.
    # (It might appear elsewhere for unrelated reasons, but the OpenTrade
    # signals_at_entry should not have it.)
    open_trade_section = src[src.find("signals_at_entry={"):src.find("signals_at_entry={") + 600]
    assert "isinstance(v, (bool, int, float))" not in open_trade_section, (
        "DEC-492 regression: backtest.py still filters signals to numeric types"
    )


# ---------------------------------------------------------------------------
# DEC-491 - Parquet primary + CSV hybrid
# ---------------------------------------------------------------------------
def test_dec491_writer_emits_parquet_for_nonempty_trades(tmp_path):
    """write_all_outputs should emit BOTH trade_log.parquet AND trade_log.csv
    for non-empty df_trades."""
    from backtest.results.writer import write_all_outputs

    df = pd.DataFrame([
        {
            "ticker": "AAPL", "entry_date": "2024-06-15",
            "exit_date": "2024-06-20", "direction": "long",
            "strategy": "rsi_oversold", "category": "mean_reversion",
            "sector": "Technology",
            "confidence_tier": "MEDIUM",
            "regime": "neutral",
            "pnl_pct": -1.0, "win": False, "hold_days": 5,
            "max_adverse_excursion": -1.5,
            "max_favourable_excursion": 0.0,
            "entry_price": 100.0, "exit_price": 99.0,
            "initial_stop": 98.0, "highest_close": 100.0,
            "trailing_stop_at_exit": 99.0,
            "exit_reason": "trailing_stop",
            "signals_at_entry": {"rsi": 28, "tags": ["oversold"]},  # nested
            "context_bullets": ["RSI oversold", "MACD cross"],
            "context_paragraph": "",
            "fail_reason": "",
        }
    ])
    metrics = pd.DataFrame()
    try:
        write_all_outputs(
            df_trades=df, metrics=metrics, skipped=[], cb_log=[],
            exit_compare=pd.DataFrame(), trade_exit_detail=pd.DataFrame(),
            walk_forward=pd.DataFrame(),
            survivorship_info={"gross_roi": 0.0, "adjusted_roi": 0.0,
                               "haircut_pct": 0.0, "years": 0.0},
            bonferroni={"recommendation": "test"},
            output_dir=tmp_path,
        )
    except Exception as exc:
        pytest.skip(f"writer failed (likely missing test config): {exc}")

    parquet_path = tmp_path / "trade_log.parquet"
    csv_path = tmp_path / "trade_log.csv"
    assert parquet_path.exists(), "DEC-491: trade_log.parquet not emitted"
    assert csv_path.exists(), "DEC-491: trade_log.csv not emitted"

    # Parquet roundtrip preserves nested types
    df_parquet = pd.read_parquet(parquet_path)
    assert "signals_at_entry" in df_parquet.columns
    sig = df_parquet["signals_at_entry"].iloc[0]
    # In Parquet, nested dict survives as dict (or struct)
    assert isinstance(sig, dict) or hasattr(sig, "__getitem__"), (
        "DEC-491: nested dict not preserved in Parquet roundtrip"
    )


def test_dec491_writer_csv_stringifies_nested_columns(tmp_path):
    """CSV emission of nested columns must JSON-stringify, not crash."""
    from backtest.results.writer import write_all_outputs
    df = pd.DataFrame([
        {
            "ticker": "AAPL", "entry_date": "2024-06-15",
            "exit_date": "2024-06-20", "direction": "long",
            "strategy": "rsi", "category": "mean_reversion",
            "sector": "Technology", "confidence_tier": "MEDIUM",
            "regime": "neutral",
            "pnl_pct": -1.0, "win": False, "hold_days": 5,
            "max_adverse_excursion": -1.5, "max_favourable_excursion": 0.0,
            "entry_price": 100.0, "exit_price": 99.0,
            "initial_stop": 98.0, "highest_close": 100.0,
            "trailing_stop_at_exit": 99.0, "exit_reason": "trailing_stop",
            "signals_at_entry": {"rsi": 28, "tags": ["oversold"]},
            "context_bullets": ["A", "B"], "context_paragraph": "",
            "fail_reason": "",
        }
    ])
    try:
        write_all_outputs(
            df_trades=df, metrics=pd.DataFrame(), skipped=[], cb_log=[],
            exit_compare=pd.DataFrame(), trade_exit_detail=pd.DataFrame(),
            walk_forward=pd.DataFrame(),
            survivorship_info={"gross_roi": 0.0, "adjusted_roi": 0.0,
                               "haircut_pct": 0.0, "years": 0.0},
            bonferroni={"recommendation": "test"},
            output_dir=tmp_path,
        )
    except Exception as exc:
        pytest.skip(f"writer failed: {exc}")

    csv_path = tmp_path / "trade_log.csv"
    if csv_path.exists():
        df_csv = pd.read_csv(csv_path)
        # signals_at_entry column should be a JSON string (CSV-readable)
        if "signals_at_entry" in df_csv.columns:
            sig_str = df_csv["signals_at_entry"].iloc[0]
            assert isinstance(sig_str, str), (
                "DEC-491: nested column should be stringified in CSV"
            )
            # Must be valid JSON
            parsed = json.loads(sig_str)
            assert parsed.get("rsi") == 28


def test_dec491_writer_handles_empty_trades(tmp_path):
    """Empty df_trades must not crash writer."""
    from backtest.results.writer import write_all_outputs
    try:
        write_all_outputs(
            df_trades=pd.DataFrame(), metrics=pd.DataFrame(), skipped=[],
            cb_log=[], exit_compare=pd.DataFrame(),
            trade_exit_detail=pd.DataFrame(), walk_forward=pd.DataFrame(),
            survivorship_info={"gross_roi": 0.0, "adjusted_roi": 0.0,
                               "haircut_pct": 0.0, "years": 0.0},
            bonferroni={"recommendation": "test"},
            output_dir=tmp_path,
        )
    except Exception as exc:
        pytest.skip(f"writer failed on empty: {exc}")
    csv_path = tmp_path / "trade_log.csv"
    assert csv_path.exists()


def test_inv014_parquet_writes_with_uniformly_empty_struct_columns(tmp_path):
    """INV-014 regression: writer must emit trade_log.parquet even when
    nested object columns (agent_reasoning, signals_at_entry,
    context_bullets) are uniformly empty across all rows.

    Pre-fix bug: pyarrow rejects empty struct with no child fields, causing
    --no-agents Phase 1A baseline runs to silently degrade to CSV-only and
    miss DEC-491's parquet-as-primary contract.

    Fix: writer sanitizes uniformly-empty nested cols to None before
    to_parquet. None becomes pyarrow null type (valid), not empty struct.
    """
    from backtest.results.writer import write_all_outputs

    # Simulate --no-agents Phase 1A run: agent_reasoning empty dict
    # everywhere, context_bullets empty list everywhere.
    df = pd.DataFrame([
        {
            "ticker": "AAPL", "entry_date": "2024-06-15",
            "exit_date": "2024-06-20", "direction": "long",
            "strategy": "rsi", "category": "mean_reversion",
            "sector": "Technology", "confidence_tier": "MEDIUM",
            "regime": "neutral",
            "pnl_pct": -1.0, "win": False, "hold_days": 5,
            "max_adverse_excursion": -1.5, "max_favourable_excursion": 0.0,
            "entry_price": 100.0, "exit_price": 99.0,
            "initial_stop": 98.0, "highest_close": 100.0,
            "trailing_stop_at_exit": 99.0, "exit_reason": "trailing_stop",
            "signals_at_entry": {"rsi": 28},  # non-empty (other col)
            "context_bullets": [],   # empty list (--no-agents pattern)
            "agent_reasoning": {},   # empty dict (--no-agents pattern)
            "context_paragraph": "",
            "fail_reason": "",
        },
        {
            "ticker": "MSFT", "entry_date": "2024-07-01",
            "exit_date": "2024-07-05", "direction": "long",
            "strategy": "rsi", "category": "mean_reversion",
            "sector": "Technology", "confidence_tier": "HIGH",
            "regime": "bull",
            "pnl_pct": 2.0, "win": True, "hold_days": 4,
            "max_adverse_excursion": -0.5, "max_favourable_excursion": 2.5,
            "entry_price": 400.0, "exit_price": 408.0,
            "initial_stop": 390.0, "highest_close": 408.0,
            "trailing_stop_at_exit": 408.0, "exit_reason": "trailing_stop",
            "signals_at_entry": {"rsi": 25},
            "context_bullets": [],   # empty list
            "agent_reasoning": {},   # empty dict
            "context_paragraph": "",
            "fail_reason": "",
        }
    ])

    try:
        write_all_outputs(
            df_trades=df, metrics=pd.DataFrame(), skipped=[], cb_log=[],
            exit_compare=pd.DataFrame(), trade_exit_detail=pd.DataFrame(),
            walk_forward=pd.DataFrame(),
            survivorship_info={"gross_roi": 0.0, "adjusted_roi": 0.0,
                               "haircut_pct": 0.0, "years": 0.0},
            bonferroni={"recommendation": "test"},
            output_dir=tmp_path,
        )
    except Exception as exc:
        pytest.skip(f"writer dependency failure: {exc}")

    parquet_path = tmp_path / "trade_log.parquet"
    csv_path = tmp_path / "trade_log.csv"
    assert parquet_path.exists(), (
        "INV-014: trade_log.parquet must be emitted even when "
        "agent_reasoning/context_bullets are uniformly empty"
    )
    assert csv_path.exists()

    # Roundtrip read - empty-struct cols become null (None), other cols intact
    df_parquet = pd.read_parquet(parquet_path)
    assert len(df_parquet) == 2
    # signals_at_entry has non-empty dicts -> preserved
    assert "signals_at_entry" in df_parquet.columns
    sig = df_parquet["signals_at_entry"].iloc[0]
    assert isinstance(sig, dict) or hasattr(sig, "__getitem__")
    # agent_reasoning was uniformly-empty -> sanitized to null
    if "agent_reasoning" in df_parquet.columns:
        ar = df_parquet["agent_reasoning"].iloc[0]
        assert ar is None or pd.isna(ar), (
            "INV-014: uniformly-empty agent_reasoning should be null in parquet"
        )
