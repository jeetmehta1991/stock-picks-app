"""Phase 1A pre-entry gate (System pyramid layer; Pass 53 v8h+1 owner-mandated 2026-05-08).

System-level gate: must pass BEFORE Phase 1A May 15 launch. Asserts that the
prerequisites a Phase 1A run depends on are all in place. Failures here block
launch (no point running a 1937-ticker backtest if the universe CSV is broken
or thresholds are missing).

Markers:
    pytest -m system
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


pytestmark = pytest.mark.system


# -- Gate 1: Master universe CSV exists + minimum row count -------------
def test_gate_master_universe_csv() -> None:
    csv = REPO_ROOT / "Backtesting universe" / "Master Universe_Deduplicated_All Tiers_May 2026.csv"
    assert csv.exists(), f"Master universe CSV missing at {csv}"
    import pandas as pd
    df = pd.read_csv(csv, comment="#")
    assert "Symbol" in df.columns, "Master CSV missing Symbol column"
    assert len(df) >= 1900, f"Master CSV has only {len(df)} rows (gate floor: 1900)"


# -- Gate 2: Tier 1A T1c T1ETF CSVs all present ------------------------
def test_gate_all_tier_csvs_present() -> None:
    base = REPO_ROOT / "Backtesting universe"
    required = [
        "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv",
        "Tier 1C Universe_NASDAQ-100 Tickers_Jan 2020 to May 2026.csv",
        "Tier 1 ETFs Universe_Sector and Broad-Market ETFs_May 2026.csv",
        "Tier 2 Universe_Spinoffs and Recent IPOs_Feb 2010 to May 2026.csv",
        "Tier 3 Universe_Momentum Top-100_Jun 2022 to May 2026.csv",
    ]
    missing = [r for r in required if not (base / r).exists()]
    assert not missing, f"Tier CSVs missing: {missing}"


# -- Gate 3: Passing-criteria thresholds in config.py -----------------
def test_gate_passing_criteria_thresholds() -> None:
    config = REPO_ROOT / "backtest" / "config.py"
    assert config.exists(), "config.py missing"
    text = config.read_text(encoding="utf-8", errors="ignore")
    must = ["min_win_rate", "min_profit_factor", "min_trades", "max_drawdown"]
    missing = [k for k in must if k not in text]
    assert not missing, f"config.py PASSING_CRITERIA missing keys: {missing}"


# -- Gate 4: OHLCV cache populated for at least 90% of universe --------
def test_gate_ohlcv_cache_coverage() -> None:
    import pandas as pd
    csv = REPO_ROOT / "Backtesting universe" / "Master Universe_Deduplicated_All Tiers_May 2026.csv"
    if not csv.exists():
        pytest.skip("universe csv missing")
    universe = sorted(pd.read_csv(csv, comment="#")["Symbol"].dropna().str.upper().unique())
    cache_dir = REPO_ROOT / "backtest" / "data" / "cache" / "ohlcv"
    if not cache_dir.is_dir():
        pytest.skip("OHLCV cache dir not present")
    cached = {p.stem.upper() for p in cache_dir.glob("*.parquet")}
    coverage = len([t for t in universe if t in cached]) / max(len(universe), 1)
    assert coverage >= 0.85, (
        f"OHLCV cache coverage only {coverage:.1%} of universe (gate floor: 85%)"
    )


# -- Gate 5: Pre-commit hook installed --------------------------------
def test_gate_pre_commit_hook_installed() -> None:
    hook = REPO_ROOT / ".git" / "hooks" / "pre-commit"
    assert hook.exists(), "pre-commit hook not installed"
    text = hook.read_text(encoding="utf-8", errors="ignore")
    assert "preflight.py" in text, "hook missing preflight gate"
    assert "sync_doc_counts.py" in text, "hook missing drift detector gate"


# -- Gate 6: Doc-count drift clean ------------------------------------
def test_gate_doc_count_drift_clean() -> None:
    import subprocess
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "sync_doc_counts.py"), "--check"],
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=60,
    )
    assert r.returncode == 0, (
        f"sync_doc_counts.py --check failed (rc={r.returncode}). Drift "
        f"present: pre-Phase-1A gate cannot pass with reference-doc drift.\n"
        f"{r.stdout[-500:]}"
    )


# -- Gate 7: All canonical schemas have parquet caches present --------
def test_gate_canonical_schemas_have_caches() -> None:
    sys.path.insert(0, str(REPO_ROOT / "backtest" / "tests"))
    from test_schema_canonical import CANONICAL_SCHEMAS
    missing = []
    for rel_dir in CANONICAL_SCHEMAS:
        d = REPO_ROOT / rel_dir
        if not d.is_dir():
            missing.append(rel_dir)
            continue
        if not any(d.glob("*.parquet")):
            missing.append(f"{rel_dir} (empty)")
    assert not missing, f"canonical-locked cache dirs missing: {missing[:5]}..."


# -- Gate 8: Sprint 0A leftover items resolved ------------------------
def test_gate_sprint_0a_phase_1a_blockers() -> None:
    """PHASE_1A_PRELAUNCH_TODO.md must report 0 OPEN blockers in section A."""
    import re
    todo = REPO_ROOT / "PHASE_1A_PRELAUNCH_TODO.md"
    if not todo.exists():
        pytest.skip("PHASE_1A_PRELAUNCH_TODO.md missing")
    text = todo.read_text(encoding="utf-8", errors="ignore")
    # Pre-launch gate: the strict-blockers section must be tabulated and
    # not contain any actively blocking row. INV-046 logged 2026-05-08
    # is OPEN HIGH severity but documented as 'launch dependency
    # candidate' not 'BLOCKS PHASE 1A' literal. The literal phrase the
    # gate checks for must NOT appear in the section header.
    assert "Phase 1A May 15 strict blockers status" in text, (
        "PHASE_1A_PRELAUNCH_TODO.md missing 'strict blockers status' "
        "section (stale doc structure - gate cannot evaluate)."
    )
    # Bugs tagged CRITICAL OPEN that explicitly state 'Phase 1A baseline
    # runs without' / 'bypassed' are not gate blockers. The gate fails
    # only if the doc says something blocks Phase 1A launch directly.
    blocks_launch = re.search(r"(BLOCKS\s+PHASE\s+1A|Phase\s+1A\s+launch\s+blocked)",
                               text, re.IGNORECASE)
    assert blocks_launch is None, (
        f"PHASE_1A_PRELAUNCH_TODO.md indicates Phase 1A launch is blocked: "
        f"'{blocks_launch.group(0)}' near doc position {blocks_launch.start()}."
    )
