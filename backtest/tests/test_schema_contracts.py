"""Schema-contract tests for producer-consumer pairs registry.

# Source: Council 139 Option-8 HYBRID Layer B per owner directive
# 2026-06-28 "I don't want to keep demanding adversarial reviews."
# per CHECKLIST #77 + #124.

These tests are the STRUCTURAL FIX for `feedback_monitor_design_vs_
operational_gap` recurrence (3 incidents in 24 hours: B1028 + sub-agent
polling + B1042 schema mismatch).

Each test asserts a producer-consumer SCHEMA CONTRACT: the keys that
the producer emits MUST match the keys that the consumer reads. Schema
drift = pyramid failure = silent miss caught at test-time NOT runtime.

Registry: `docs/PRODUCER_CONSUMER_PAIRS.md`

Seed contracts (Phase 1 of Option 8):
  - Contract 1: engine.backtest -> b1019_monitor (engine_state.json)
  - Contract 2: B660 baseline -> b1019_monitor._load_baseline
  - Contract 3: trade_log_checkpoint.csv -> b1019_monitor checkers
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


# ============================================================================
# Contract 1: engine.backtest -> b1019_monitor (engine_state.json)
# ============================================================================

ENGINE_STATE_REQUIRED_KEYS = {"simulated_day", "cells_completed", "status"}


def test_schema_contract_engine_state_producer_emits_required_keys():
    """Contract 1 (producer side): backtest.py engine_state.json emit
    block must include all keys that b1019_monitor.py reads."""
    from backtest.engine import backtest as _bt
    source = inspect.getsource(_bt)
    for key in ENGINE_STATE_REQUIRED_KEYS:
        assert f'"{key}"' in source, (
            f"engine_state.json producer must emit {key!r} per b1019_monitor "
            f"consumer contract. Per docs/PRODUCER_CONSUMER_PAIRS.md row 1."
        )


def test_schema_contract_engine_state_consumer_reads_canonical_keys():
    """Contract 1 (consumer side): b1019_monitor.py reads
    simulated_day + cells_completed + status (must match producer)."""
    monitor_path = REPO / "scripts" / "b1019_phase_1_runtime_monitor.py"
    content = monitor_path.read_text()
    for key in ENGINE_STATE_REQUIRED_KEYS:
        assert f'"{key}"' in content, (
            f"b1019_monitor consumer must reference {key!r} per producer "
            f"contract"
        )


# ============================================================================
# Contract 2: B660 baseline -> b1019_monitor._load_baseline
# ============================================================================

B660_BASELINE_RESULT_KEYS = {"strategy", "n_fires_long", "n_fires_short",
                              "n_fires_avoid", "calendar_year_span"}


def test_schema_contract_b660_baseline_file_schema():
    """Contract 2 (producer side): B660 baseline file has 'results' list
    with required per-item keys."""
    baseline_path = REPO / "output_audit" / "fire_count_measured_b660_full_universe.json"
    if not baseline_path.exists():
        pytest.skip(f"Baseline not available at {baseline_path}")
    data = json.loads(baseline_path.read_text())
    assert "results" in data, "B660 baseline must have 'results' top-level key"
    assert isinstance(data["results"], list)
    if data["results"]:
        first = data["results"][0]
        for key in B660_BASELINE_RESULT_KEYS:
            assert key in first, (
                f"B660 results item must include {key!r} per "
                f"b1019_monitor._load_baseline parse expectations"
            )


def test_schema_contract_b660_baseline_consumer_parses_results():
    """Contract 2 (consumer side): _load_baseline references 'results'
    list + calendar_year_span field per B660 schema."""
    monitor_path = REPO / "scripts" / "b1019_phase_1_runtime_monitor.py"
    content = monitor_path.read_text()
    assert "if \"results\" in data" in content, (
        "_load_baseline must reference 'results' top-level key per "
        "B660 producer schema"
    )
    assert "calendar_year_span" in content, (
        "_load_baseline must reference calendar_year_span field per "
        "B660 producer schema"
    )


# ============================================================================
# Contract 3: trade_log_checkpoint.csv -> b1019_monitor checkers
# ============================================================================

TRADE_LOG_REQUIRED_COLUMNS = {"strategy", "ticker", "entry_date",
                               "exit_date", "exit_method"}


def test_schema_contract_trade_log_b1019_required_columns():
    """Contract 3 (consumer side): b1019_monitor _check_b2_schema
    requires these columns."""
    monitor_path = REPO / "scripts" / "b1019_phase_1_runtime_monitor.py"
    content = monitor_path.read_text()
    # Required columns must be referenced in schema check
    assert "required = [\"strategy\", \"ticker\", \"entry_date\", \"exit_date\", \"exit_method\"]" in content, (
        "_check_b2_schema must enforce trade_log column contract"
    )


def test_schema_contract_trade_log_reader_dispatches_csv_and_parquet():
    """Contract 3: monitor must support BOTH csv (checkpoint) AND parquet
    (final write) since the producer emits .csv during run + .parquet
    at end."""
    monitor_path = REPO / "scripts" / "b1019_phase_1_runtime_monitor.py"
    content = monitor_path.read_text()
    # Both A1 + B2 checks must dispatch by file extension
    assert content.count("endswith(\".csv\")") >= 2, (
        "Monitor must dispatch csv/parquet reader by extension (was the "
        "B1042 bug: read_parquet on csv = false HALT-CRITICAL)"
    )


# ============================================================================
# Registry-integrity tests
# ============================================================================

def test_registry_file_exists():
    """Council 139 Layer A: producer-consumer registry exists at canonical path."""
    registry_path = REPO / "docs" / "PRODUCER_CONSUMER_PAIRS.md"
    assert registry_path.exists(), (
        "Producer-consumer registry must exist at docs/PRODUCER_CONSUMER_PAIRS.md "
        "per Council 139 Option-8 HYBRID Layer A"
    )


def test_registry_documents_seed_contracts():
    """Council 139 Layer A: registry includes the 3 seed contracts above."""
    registry_path = REPO / "docs" / "PRODUCER_CONSUMER_PAIRS.md"
    content = registry_path.read_text()
    # Each contract should appear by producer file reference
    assert "backtest/engine/backtest.py" in content
    assert "fire_count_measured_b660_full_universe.json" in content
    assert "trade_log_checkpoint" in content
    # Two-tier status discipline
    assert "DESIGNED-NOT-VERIFIED" in content
    assert "OPERATIONALLY-VERIFIED" in content


def test_registry_status_discipline_documented():
    """Council 139 Layer D: registry documents two-tier status scheme."""
    registry_path = REPO / "docs" / "PRODUCER_CONSUMER_PAIRS.md"
    content = registry_path.read_text()
    assert "Default for new entries is `DESIGNED-NOT-VERIFIED`" in content
    assert "Promote to `OPERATIONALLY-VERIFIED` only when evidence link added" in content
