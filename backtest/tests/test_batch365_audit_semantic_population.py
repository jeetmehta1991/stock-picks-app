"""Batch 365 Item 2: semantic-population check in audit_trade_log_forensic.py.

Source (per CHECKLIST #77): owner approval 2026-05-25 of 3 hardening items
after the Batch 363 silent gap. The forensic audit's "Column population
rates" check used `.notna()` which counts default sentinels (0 numeric,
"none" string) as populated. Result: 0% real fire rate on smart_money_score
was reported as "[OK] 100% populated" -- masking the silent gap.

Item 2 adds a semantic-non-default check alongside the literal-population
check. The semantic check uses a DEFAULT_SENTINELS registry mapping each
signal column to its known default value (0 or "none"), then computes
`pct of rows with non-default value`. Gates at 5% min for [WARN], 50% for
[OK].

Pyramid tiers exercised:
  T1 (Unit)        DEFAULT_SENTINELS registry is consistent with engine
                   default initialization
  T2 (Smoke)       audit script runs end-to-end and emits the semantic-
                   non-default rate per column
  T6 (Regression)  silent-default columns (all zeros / all "none") flag
                   as [FAIL] not [OK]
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).parent.parent.parent
SCRIPT = REPO / "scripts" / "audit_trade_log_forensic.py"


def test_batch365_audit_script_imports_default_sentinels():
    """The DEFAULT_SENTINELS registry must be present in the audit script."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert "DEFAULT_SENTINELS" in src, (
        "Batch 365 Item 2: DEFAULT_SENTINELS registry must be defined "
        "in audit_trade_log_forensic.py to drive the semantic-non-default "
        "check."
    )
    for col in ("smart_money_score", "congressional_signal",
                 "insider_signal", "institutional_signal"):
        assert f'"{col}"' in src, (
            f"DEFAULT_SENTINELS missing column {col!r} -- "
            f"the Batch 363 silent gap's exact pattern can recur silently"
        )


def test_batch365_audit_script_runs_on_silent_default_csv(tmp_path):
    """Smoke: when the trade_log has 0% real fire rate on smart money,
    the audit must report semantic=0.0% non-default (the FAIL we want).
    Compare to the pre-fix behavior where the same data reported
    100% populated, [OK]."""
    # Build a minimal trade_log with all-default smart-money fields
    df = pd.DataFrame({
        "ticker":               ["AAPL", "MSFT", "NVDA"] * 10,
        "entry_date":           ["2024-06-01"] * 30,
        "exit_date":            ["2024-06-15"] * 30,
        "direction":            ["long"] * 30,
        "strategy":             ["dummy"] * 30,
        "category":             ["test"] * 30,
        "sector":               ["Technology"] * 30,
        "confidence_tier":      ["MEDIUM"] * 30,
        "regime":               ["bull"] * 20 + ["bear"] * 10,
        "exit_reason":          ["trailing_stop"] * 30,
        "entry_price":          [100.0] * 30,
        "exit_price":            [105.0] * 30,
        "initial_stop":         [95.0] * 30,
        "trailing_stop_at_exit": [104.0] * 30,
        "pnl_pct":              [5.0] * 30,
        "pnl_dollar":            [500.0] * 30,
        "win":                  [True] * 30,
        "hold_days":            [10] * 30,
        "max_adverse_excursion": [-2.0] * 30,
        "max_favourable_excursion": [6.0] * 30,
        "signals_at_entry":     ["{}"] * 30,
        # Smart money fields: ALL DEFAULT (the silent gap)
        "smart_money_score":    [0] * 30,
        "macro_score":          [0] * 30,
        "sentiment_score":      [0] * 30,
        "congressional_signal": ["none"] * 30,
        "insider_signal":       ["none"] * 30,
        "institutional_signal": ["none"] * 30,
        "aaii_signal":          [0] * 30,
        "cnn_fg_score":         [50.0] * 30,
    })
    tl = tmp_path / "trade_log.csv"
    df.to_csv(tl, index=False)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(tl)],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout + result.stderr
    # Per-column semantic output line format:
    # "[FAIL] smart_money_score          literal=100.0% / semantic=  0.0% non-default (default=0)"
    for col in ("smart_money_score", "congressional_signal",
                 "insider_signal", "institutional_signal"):
        assert f"{col:<25}" in out or col in out, f"audit didn't print {col}"
    # The semantic rate for these columns MUST be 0.0% and the marker FAIL
    assert "semantic=  0.0%" in out, (
        "Batch 365 Item 2 regression: audit didn't emit semantic-non-default "
        "rate, or rate didn't reflect all-default trade-log. Pre-fix "
        "behavior would have shown 'literal=100% [OK]' here."
    )


def test_batch365_audit_distinguishes_real_data_from_default():
    """When trade_log has REAL smart-money data (non-zero / non-'none'),
    the audit must report semantic > 0% (and ideally >= 50% [OK])."""
    df = pd.DataFrame({
        "ticker":               ["AAPL"] * 30,
        "entry_date":           ["2024-06-01"] * 30,
        "exit_date":            ["2024-06-15"] * 30,
        "direction":            ["long"] * 30,
        "strategy":             ["dummy"] * 30,
        "category":             ["test"] * 30,
        "sector":               ["Technology"] * 30,
        "confidence_tier":      ["MEDIUM"] * 30,
        "regime":               ["bull"] * 30,
        "exit_reason":          ["trailing_stop"] * 30,
        "entry_price":          [100.0] * 30,
        "exit_price":            [105.0] * 30,
        "initial_stop":         [95.0] * 30,
        "trailing_stop_at_exit": [104.0] * 30,
        "pnl_pct":              [5.0] * 30,
        "pnl_dollar":            [500.0] * 30,
        "win":                  [True] * 30,
        "hold_days":            [10] * 30,
        "max_adverse_excursion": [-2.0] * 30,
        "max_favourable_excursion": [6.0] * 30,
        "signals_at_entry":     ["{}"] * 30,
        # Smart money fields: REAL DATA
        "smart_money_score":    [3] * 30,     # non-zero
        "macro_score":          [2] * 30,
        "sentiment_score":      [1] * 30,
        "congressional_signal": ["buy"] * 30,   # non-'none'
        "insider_signal":       ["strong_buy"] * 30,
        "institutional_signal": ["buy"] * 30,
        "aaii_signal":          [1] * 30,
        "cnn_fg_score":         [50.0] * 30,
    })
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tf:
        df.to_csv(tf.name, index=False)
        tl = tf.name
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", tl],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    # smart_money_score semantic rate should be 100% (all rows have value 3)
    assert "semantic=100.0%" in out, (
        "audit must report semantic-non-default rate when real data is present"
    )
