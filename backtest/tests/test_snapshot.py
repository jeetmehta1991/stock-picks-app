"""Snapshot / golden-data tests - DEC-503 pyramid layer (Pass 53 v8h+1 owner-approved 2026-05-08).

Snapshot = freeze a known-good output and assert future runs produce the
same shape (or, where appropriate, the same numeric values within tolerance).
Catches numerical drift that unit tests miss.

The golden fixtures live under backtest/tests/golden/. When a fixture needs
to change intentionally, regenerate it explicitly + commit + reference the
DEC that justified the change.

Markers:
    pytest -m snapshot
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
GOLDEN = Path(__file__).resolve().parent / "golden"
GOLDEN.mkdir(exist_ok=True)


pytestmark = pytest.mark.snapshot


# -- Snapshot 1: dashboard_stage_2 data.json structure ------------------
def test_snapshot_dashboard_stage_2_top_level_keys() -> None:
    """dashboard_stage_2/data.json top-level keys must include the
    documented set. Catches refactors that drop tabs."""
    p = REPO_ROOT / "dashboard_stage_2" / "data.json"
    if not p.exists():
        pytest.skip("dashboard_stage_2/data.json not present")
    d = json.loads(p.read_text(encoding="utf-8"))
    expected = {
        "generated_at", "decisions", "bugs", "investigations",
        "caveats", "learnings", "tier_items", "active_bgs",
        "pending_pipeline", "automation_status", "test_inventory",
        "pyramid_layers", "structural_drift", "reference_tables",
    }
    actual = set(d.keys())
    missing = expected - actual
    assert not missing, f"data.json missing top-level keys: {missing}"


# -- Snapshot 2: pyramid layers list shape ------------------------------
def test_snapshot_pyramid_layers_shape() -> None:
    """The pyramid_layers list in the dashboard must be the canonical 13-
    layer DEC-503 set. Detection of additions/removals."""
    p = REPO_ROOT / "dashboard_stage_2" / "data.json"
    if not p.exists():
        pytest.skip("dashboard_stage_2/data.json not present")
    d = json.loads(p.read_text(encoding="utf-8"))
    actual = set(d.get("pyramid_layers", []))
    expected = {
        "unit", "smoke", "integration", "system", "functional",
        "regression", "data_integrity", "performance", "acceptance",
        "property", "snapshot", "contract", "compatibility",
    }
    missing = expected - actual
    extra = actual - expected
    assert not missing, f"pyramid_layers missing: {missing}"
    assert not extra, (
        f"pyramid_layers has unexpected additions: {extra}. If intentional, "
        f"update this snapshot."
    )


# -- Snapshot 3: canonical schemas count baseline -----------------------
def test_snapshot_canonical_schemas_count() -> None:
    """The number of locked canonical schemas should grow over time, never
    silently shrink. Floor: 23 as of 2026-05-08."""
    sys.path.insert(0, str(REPO_ROOT / "backtest" / "tests"))
    try:
        from test_schema_canonical import CANONICAL_SCHEMAS
    except ImportError:
        pytest.skip("test_schema_canonical not importable")
    assert len(CANONICAL_SCHEMAS) >= 23, (
        f"CANONICAL_SCHEMAS shrank to {len(CANONICAL_SCHEMAS)} (floor: 23). "
        f"Either someone removed a lock (regression) or this floor needs "
        f"to be updated for a documented schema change."
    )


# -- Snapshot 4: decision count floor -----------------------------------
def test_snapshot_decision_count_floor() -> None:
    """AUDIT_INDEX should have at least 500 decisions; never shrink past
    that. As of 2026-05-08: 520."""
    audit = REPO_ROOT / "AUDIT_INDEX.md"
    if not audit.exists():
        pytest.skip("AUDIT_INDEX.md missing")
    import re
    text = audit.read_text(encoding="utf-8", errors="ignore")
    n = len(re.findall(r"^\| \*\*DECISION-(\d+(?:[-_]\w+)?)", text, re.MULTILINE))
    n_unique = len(set(re.findall(r"^\| \*\*DECISION-(\d+(?:[-_]\w+)?)", text, re.MULTILINE)))
    assert n_unique >= 500, f"decision count shrank to {n_unique} unique (floor: 500)"


# -- Snapshot 5: bug count floor ----------------------------------------
def test_snapshot_bug_count_floor() -> None:
    """BUG_REGISTER should have at least 145 canonical bugs."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        from build_dashboard_stage_2 import parse_bug_register
    except ImportError:
        pytest.skip("dashboard module not importable")
    bugs = parse_bug_register(REPO_ROOT / "BUG_REGISTER.md")
    assert len(bugs) >= 145, f"bug count shrank to {len(bugs)} (floor: 145)"


# -- Snapshot 6: AAII parquet schema lock -------------------------------
def test_snapshot_aaii_extended_schema() -> None:
    """The AAII extended sentiment parquet must retain its 13-column shape
    (date + 12 sentiment/SPY columns)."""
    p = REPO_ROOT / "data_prefetch" / "aaii" / "weekly_sentiment.parquet"
    if not p.exists():
        pytest.skip("AAII parquet not present")
    import pandas as pd
    df = pd.read_parquet(p)
    expected = {
        "date", "bullish", "neutral", "bearish", "total",
        "bullish_8wk_ma", "bull_bear_spread",
        "bullish_long_term_avg",
        "bullish_long_term_avg_plus_1stdev",
        "bullish_long_term_avg_minus_1stdev",
        "spy_weekly_high", "spy_weekly_low", "spy_weekly_close",
    }
    missing = expected - set(df.columns)
    assert not missing, f"AAII parquet missing columns: {missing}"
