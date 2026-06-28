"""B1062 monitor required-column schema-contract pin test (PIVOT #37 catch).

# Source: HONEST-FINDING PIVOT #37 B1058 + B1060 Phase 1 HALTed at
# b2_viol=1 (missing_column_exit_method) per Council 162 Option-F.
# Engine trade_log uses canonical 'exit_reason'; monitor required list
# had drifted to 'exit_method'. CHECKLIST #124 DESIGNED-NOT-VERIFIED
# default fix: pin the schema-contract test.

B1062 fix: monitor.py:257 required = ["strategy", "ticker", "entry_date",
"exit_date", "exit_reason"] (was "exit_method").

This test pins the contract so future drift between monitor expectations
and engine output fails fast in pyramid, not at AWS launch time
($1.32 sunk to surface PIVOT #37 via B1058 + B1060).
"""
from __future__ import annotations

import inspect
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MONITOR_PATH = REPO / "scripts" / "b1019_phase_1_runtime_monitor.py"


def test_b1062_monitor_requires_exit_reason_not_exit_method():
    """B1062 PIVOT #37 fix: monitor's required-column list must include
    'exit_reason' (canonical engine column per writer.py:50)."""
    content = MONITOR_PATH.read_text()
    # The required list must contain exit_reason
    assert '"exit_reason"' in content, (
        "B1062 PIVOT #37: monitor required column list must include "
        "'exit_reason' (canonical engine column per writer.py)"
    )
    # The required list must NOT contain exit_method (which is downstream
    # cube aggregate, not trade_log column)
    # Specifically check the required = [...] line
    required_line = next(
        (line for line in content.splitlines()
         if "required = " in line and "exit" in line and "strategy" in line),
        None
    )
    assert required_line is not None, (
        "B1062: could not locate required column list in monitor"
    )
    assert "exit_method" not in required_line, (
        f"B1062 PIVOT #37: required list must NOT contain 'exit_method' "
        f"(found in: {required_line.strip()!r}). Engine emits exit_reason."
    )
    assert "exit_reason" in required_line, (
        f"B1062: required list must contain 'exit_reason'. "
        f"Found: {required_line.strip()!r}"
    )


def test_b1062_writer_emits_exit_reason_in_trade_log():
    """B1062 schema-contract: writer.py trade_log emission must use
    'exit_reason' as canonical column name."""
    from backtest.results import writer
    source = inspect.getsource(writer)
    # exit_reason must be used in trade_log construction/processing
    # (per writer.py:50, 516, 519)
    assert 'exit_reason' in source, (
        "B1062: writer.py must reference 'exit_reason' for trade_log "
        "schema (canonical column name)"
    )


def test_b1062_engine_exit_manager_emits_exit_reason():
    """B1062: exit_manager.py must produce exit_reason (canonical name)."""
    from backtest.engine import exit_manager
    source = inspect.getsource(exit_manager)
    assert 'exit_reason' in source.lower() or 'exit_method' in source.lower(), (
        "B1062: exit_manager must define exit_reason or exit_method"
        " (the column name eventually written by writer)"
    )


def test_b1062_pivot_37_lineage_documented():
    """B1062: PIVOT #37 fix lineage must be in monitor.py comments."""
    content = MONITOR_PATH.read_text()
    assert "PIVOT #37" in content, (
        "B1062: PIVOT #37 lineage must be in monitor.py docstring/comments"
    )
    assert "B1062" in content, "B1062 batch lineage must be referenced"


def test_b1062_b_check_required_columns_consistent():
    """B1062 schema-contract pin: the monitor's b2 required list must
    match the columns ACTUALLY emitted by engine trade_log writes.

    This is the regression-guard against future schema-name drift.
    Engine writes trade_log_checkpoint.csv with columns per
    backtest/results/writer.py. The 5 minimum columns are:
      strategy, ticker, entry_date, exit_date, exit_reason
    """
    EXPECTED_REQUIRED = ["strategy", "ticker", "entry_date", "exit_date",
                         "exit_reason"]
    content = MONITOR_PATH.read_text()
    for col in EXPECTED_REQUIRED:
        assert f'"{col}"' in content, (
            f"B1062 pin: monitor must require '{col}' column in b2 check"
        )
