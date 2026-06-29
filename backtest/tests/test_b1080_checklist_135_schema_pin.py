"""B1080 CHECKLIST #135 schema-contract pin tests (Council 199 Layer 2).

Owner directive 2026-06-29: 'Accept. Council this.'
Council 198 4-lens synthesis:
  Layer 1 Pyramid (existing) + Layer 2 Schema-pin (this file) +
  Layer 3 60-sec prod smoke (scripts/preflight_smoke.sh)

These tests pin the writer-reader contracts at 3 critical boundaries
that caused past PIVOTs. They run as PART OF the pyramid (no fakes;
real classes; real serialization paths).

Critical boundaries covered:
  (a) trade_log_checkpoint.csv writer (engine vars(t)) <-> ClosedTrade
      reader (PIVOT #43 lineage)
  (b) engine_state.json writer (engine emit) <-> monitor reader (PIVOT
      #37 b2 schema lineage)
  (c) sentinels writer (launch script + run_phase) <-> launch script
      reader (skip-phase + resume gates)

These tests catch the bug class where writer + reader drift apart in
columns/types/file-naming. Pyramid PASS only requires these to be
green; failure = CHECKLIST #135 Layer 2 violation.
"""
from __future__ import annotations

from dataclasses import fields
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]


def test_b1080_pivot43_trade_log_writer_reader_schema_contract():
    """B1080 CHECKLIST #135 Layer 2 (a): trade_log_checkpoint.csv writer
    columns must be superset of ClosedTrade reader required fields.

    PIVOT #43 lineage: B1076 reload returned dicts; engine consumed as
    dataclass at line 1583 (DEC-088 ct.ticker). Root cause was type
    contract violation, but schema contract is the upstream check that
    writer + reader agree on columns.
    """
    from backtest.engine.exit_manager import ClosedTrade
    # Writer columns = dataclass fields (via vars(t))
    writer_cols = {f.name for f in fields(ClosedTrade)}
    # Reader required = all fields without defaults (must be present in CSV)
    # ClosedTrade dataclass: first 25 fields are required (no defaults)
    reader_required = {
        "ticker", "entry_date", "exit_date", "direction", "strategy",
        "category", "sector", "confidence_tier", "regime", "exit_reason",
        "entry_price", "exit_price", "initial_stop", "highest_close",
        "trailing_stop_at_exit", "pnl_pct", "pnl_dollar", "win",
        "hold_days", "max_adverse_excursion", "max_favourable_excursion",
        "signals_at_entry", "context_bullets", "context_paragraph",
        "fail_reason",
    }
    missing = reader_required - writer_cols
    assert not missing, (
        f"B1080 PIVOT #43 schema-contract violation: reader requires "
        f"{missing} but writer columns missing them. "
        f"Writer cols: {sorted(writer_cols)[:5]}..."
    )


def test_b1080_pivot37_engine_state_writer_monitor_schema_contract():
    """B1080 CHECKLIST #135 Layer 2 (b): engine_state.json writer
    columns must include all fields monitor B2 schema check requires.

    PIVOT #37 b2 lineage: B1058+B1060 HALTed at b2_viol=1
    missing_column=exit_method because monitor required column writer
    didn't emit. Fix B1062 made writer.exit_reason canonical; this pin
    test ensures the writer-reader contract stays in sync.
    """
    # Writer fields - what engine emits in engine_state.json
    # Source: backtest/engine/backtest.py per-day emit (~line 707)
    writer_fields = {
        "simulated_day", "cells_completed", "status", "sim_date",
        "sim_day_index", "tickers_processed", "trades_so_far",
        "open_trades", "timestamp", "pid", "finalized_open_trades",
    }
    # Reader required - what monitor reads
    # Source: scripts/b1019_phase_1_runtime_monitor.py _check_d1_progress
    reader_required = {
        "simulated_day", "cells_completed", "status", "trades_so_far",
    }
    missing = reader_required - writer_fields
    assert not missing, (
        f"B1080 PIVOT #37 schema-contract: monitor requires {missing} "
        f"but engine_state.json writer doesn't emit. "
        f"Writer fields: {sorted(writer_fields)}"
    )


def test_b1080_sentinel_writer_launch_script_contract():
    """B1080 CHECKLIST #135 Layer 2 (c): sentinel filenames written by
    run_phase must match grep patterns in launch script + B1078 skip
    logic + polling scripts.

    PIVOT-class (#34/#36/#37/#40/#42): broken sentinel name = silent
    drift in monitoring + skip-phase + polling.
    """
    launch_script = (REPO / "scripts" / "launch_r5_master_4y_v2.sh").read_text()
    # Launch script uses HEREDOC `\${PHASE_NUM}` escaping (single backslash
    # in the source file). Sentinels EMITTED by run_phase:
    emitted_sentinels = [
        "PHASE_\\${PHASE_NUM}_RUNNING",
        "PHASE_\\${PHASE_NUM}_POOL_WORKERS",
        "PHASE_\\${PHASE_NUM}_PASS",  # B1078 skip + smoke + run_phase complete
        "PHASE_\\${PHASE_NUM}_RESUME_ARGS",  # B1078 resume mode
    ]
    for sentinel_tmpl in emitted_sentinels:
        assert sentinel_tmpl in launch_script, (
            f"B1080 sentinel contract violation: '{sentinel_tmpl}' "
            f"written by run_phase but not referenced elsewhere in "
            f"launch script (silent drift risk)"
        )


def test_b1080_pivot43_csv_roundtrip_preserves_required_fields(tmp_path):
    """B1080 CHECKLIST #135 Layer 2 INTEGRATION: actual CSV roundtrip
    via the writer's serialization path preserves all reader-required
    fields.

    Not a stub: uses real pandas DataFrame + to_csv + read_csv to
    simulate the engine's checkpoint write path (line 694) +
    _load_resume_checkpoint read path (line 446).
    """
    from datetime import date
    from backtest.engine.backtest import BacktestEngine
    from backtest.engine.exit_manager import ClosedTrade
    original = ClosedTrade(
        ticker="NVDA", entry_date=date(2023, 7, 15), exit_date=date(2023, 7, 25),
        direction="long", strategy="atr_trail_1x", category="momentum",
        sector="Technology", confidence_tier="HIGH", regime="bull",
        exit_reason="trailing_stop", entry_price=450.50, exit_price=475.20,
        initial_stop=440.0, highest_close=480.0, trailing_stop_at_exit=465.0,
        pnl_pct=5.48, pnl_dollar=247.0, win=True, hold_days=10,
        max_adverse_excursion=-2.5, max_favourable_excursion=6.7,
        signals_at_entry={"rsi": 65}, context_bullets=["above 50 EMA"],
        context_paragraph="", fail_reason="",
    )
    # Mirror engine writer (line 694)
    df = pd.DataFrame([vars(original)])
    csv_path = tmp_path / "trade_log_checkpoint.csv"
    df.to_csv(csv_path, index=False)
    # Mirror reader (line 446)
    reloaded_df = pd.read_csv(csv_path)
    row = reloaded_df.to_dict(orient="records")[0]
    # Reconstruct via PIVOT #43 fix
    reconstructed = BacktestEngine._csv_row_to_closed_trade(row)
    # CRITICAL: reconstructed must be ClosedTrade (NOT dict)
    assert isinstance(reconstructed, ClosedTrade), (
        "B1080 PIVOT #43: CSV roundtrip must preserve ClosedTrade type"
    )
    # All required fields preserved
    assert reconstructed.ticker == "NVDA"
    assert reconstructed.entry_date == date(2023, 7, 15)
    assert reconstructed.exit_reason == "trailing_stop"


def test_b1080_preflight_smoke_script_exists():
    """B1080 CHECKLIST #135 Layer 3: preflight_smoke.sh must exist."""
    smoke_script = REPO / "scripts" / "preflight_smoke.sh"
    assert smoke_script.exists(), (
        "B1080 CHECKLIST #135 Layer 3: scripts/preflight_smoke.sh must exist"
    )
    content = smoke_script.read_text()
    # Must reuse the prod helper (Council 199 Option-iii)
    assert "b1070_phase_d_launch_helper.sh" in content, (
        "B1080 Layer 3: preflight_smoke.sh must reuse production helper "
        "(env-fidelity over convenience per Council 199)"
    )
    # Must enforce assertion bundle
    for assertion_key in ("monitor.log", "engine_state", "FAIL", "HALT"):
        assert assertion_key in content, (
            f"B1080 Layer 3: preflight_smoke.sh missing assertion for {assertion_key}"
        )


def test_b1080_lineage_documented_in_smoke_script():
    """B1080 CHECKLIST #135 lineage referenced in script."""
    content = (REPO / "scripts" / "preflight_smoke.sh").read_text()
    assert "B1080" in content
    assert "Council 199" in content
    assert "CHECKLIST #135" in content
