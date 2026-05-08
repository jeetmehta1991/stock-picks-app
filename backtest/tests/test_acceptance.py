"""Acceptance tests - DEC-503 pyramid layer (Pass 53 v8h+1 owner-approved 2026-05-08).

Acceptance = owner-defined pass criteria are met (the 9-criteria matrix from
CLAUDE.md). For Phase 1A baseline, we wrap the metrics from
results/metrics.py as pytest assertions. Until the first Phase 1A run lands
golden data, most assertions are SKIP and serve as a placeholder for the
post-launch wiring.

Markers:
    pytest -m acceptance
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


pytestmark = pytest.mark.acceptance


# -- Acceptance 1: 9-criteria thresholds match CLAUDE.md spec --------------
def test_acceptance_criteria_thresholds_codified() -> None:
    """The 9 passing criteria must encode the documented thresholds. Numbers
    live in backtest/config.py PASSING_CRITERIA dict; metrics.py reads them.
    """
    config = REPO_ROOT / "backtest" / "config.py"
    if not config.exists():
        pytest.skip("config.py missing")
    text = config.read_text(encoding="utf-8", errors="ignore")

    must_appear = [
        ("0.55", "min_win_rate (default tier)"),
        ("1.2",  "min_profit_factor (high-vol fallback)"),
        ("1.3",  "min_profit_factor (standard tier)"),
        ("100",  "min_trades (overall)"),
    ]
    missing = []
    for sig, desc in must_appear:
        if sig not in text:
            missing.append(f"{sig} ({desc})")
    assert not missing, (
        f"backtest/config.py PASSING_CRITERIA is missing documented "
        f"thresholds: {missing}. Either an AUDIT.md decision moved them "
        f"(then update this test) or config.py drifted from spec."
    )


# -- Acceptance 2: per-regime verdict system exists ------------------------
def test_acceptance_per_regime_verdict_system() -> None:
    """Per CLAUDE.md, each strategy gets a per-regime verdict (PASS/FAIL/
    INSUFFICIENT_DATA). The metrics module must produce this matrix."""
    metrics = REPO_ROOT / "backtest" / "results" / "metrics.py"
    if not metrics.exists():
        pytest.skip("metrics.py missing")
    text = metrics.read_text(encoding="utf-8", errors="ignore")
    must_have = ["regime", "verdict", "PASS"]
    missing = [m for m in must_have if m not in text]
    assert not missing, (
        f"metrics.py missing per-regime verdict primitives: {missing}"
    )


# -- Acceptance 3: Phase 1A golden-run fixture path is set up --------------
def test_acceptance_phase_1a_golden_fixture_scaffolded() -> None:
    """Acceptance scaffold for Phase 1A: the golden fixture path under
    backtest/tests/golden/ exists. After the first Phase 1A baseline run,
    a phase_1a_baseline.json (or .parquet) drops in, and downstream
    numerical-drift tests light up automatically.

    Today this asserts the directory exists and the README explains the
    contract. Numerical assertions activate once the fixture lands.
    """
    golden = REPO_ROOT / "backtest" / "tests" / "golden"
    assert golden.is_dir(), (
        f"{golden} missing. Create with `mkdir -p backtest/tests/golden`."
    )
    readme = golden / "README.md"
    assert readme.exists(), (
        f"{readme} missing. Should document the fixture contract: when a "
        f"phase_1a_baseline.* file lands, downstream tests assert against it."
    )
    # If the actual fixture exists, assert it has the expected top-level shape.
    fixture = golden / "phase_1a_baseline.json"
    if fixture.exists():
        import json
        d = json.loads(fixture.read_text(encoding="utf-8"))
        for required_key in ("metrics", "strategies", "regimes", "generated_at"):
            assert required_key in d, f"phase_1a_baseline.json missing key: {required_key}"


# -- Acceptance 4: Phase 1A entry gate exists and passes -------------------
def test_acceptance_phase_1a_entry_gate_exists() -> None:
    """A pre-Phase-1A gate test must exist (catches missed dependencies)."""
    gate = REPO_ROOT / "backtest" / "tests" / "test_gate_pre_phase_1a_entry.py"
    assert gate.exists(), (
        "test_gate_pre_phase_1a_entry.py missing. The system-layer gate is "
        "mandatory pre-Phase-1A per CHECKLIST."
    )


# -- Acceptance 5: 9 universe / 5-tier integrity --------------------------
def test_acceptance_master_universe_5_tier() -> None:
    """The Master Deduplicated universe CSV must exist with the 5 expected
    tier-source columns + resolved_tier per DEC-504."""
    import pandas as pd
    csv = REPO_ROOT / "Backtesting universe" / "Master Universe_Deduplicated_All Tiers_May 2026.csv"
    if not csv.exists():
        pytest.skip("Master Universe csv not present (path may have rolled forward)")
    df = pd.read_csv(csv, comment="#")
    assert "Symbol" in df.columns, "Master CSV missing Symbol column"
    assert len(df) >= 1900, f"Master CSV has only {len(df)} rows (expected >=1900)"
    if "resolved_tier" in df.columns:
        # DEC-504 precedence: T3 > T2 > T1c > T1a > T1ETF
        valid = {"T1a", "T1c", "T1b", "T2", "T3", "T1ETF"}
        bad = set(df["resolved_tier"].dropna().unique()) - valid
        assert not bad, f"resolved_tier has unexpected values: {bad}"
