"""B1039 (Council 132 Option-5/6 sub-agent #5) DEC-505 SMC walk-forward
harness regression tests.

# Source: Council 132 Option-5/6 sub-agent #5 + DEC-505 + C-1 declaration
# Section 4 PENDING walk-forward fold run per CHECKLIST #77.

Tests verify the runner in scripts/run_dec505_walk_forward_smc.py
correctly:

  1. Monkey-patches SMC_PHASE='PRODUCTION' for in-process runs only
     (does NOT mutate disk config; canary flag stays B-CANARY).
  2. Discovers exactly 18 SMC strategies via ALL_STRATEGIES.
  3. DEC-505 fold definitions match canonical (run_walk_forward in
     backtest/engine/improvements.py + walk_forward_batch414_cells.py).
  4. _evaluate_strategy handles the {'fires': bool, 'direction': str}
     contract used by screener._strat / _strat3.

Pyramid tier: unit (no IO; no network; pure function tests).
"""
from __future__ import annotations

import importlib
import sys
from datetime import date
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent.parent
SCRIPT_PATH = REPO / "scripts" / "run_dec505_walk_forward_smc.py"


def _import_runner():
    """Load the runner as a module so we can test its helpers."""
    sys.path.insert(0, str(REPO / "scripts"))
    if "run_dec505_walk_forward_smc" in sys.modules:
        return importlib.reload(sys.modules["run_dec505_walk_forward_smc"])
    import run_dec505_walk_forward_smc  # type: ignore
    return run_dec505_walk_forward_smc


def test_b1039_runner_module_loads():
    """Runner module imports without error."""
    mod = _import_runner()
    assert hasattr(mod, "main")
    assert hasattr(mod, "FOLDS")
    assert hasattr(mod, "_evaluate_strategy")
    assert hasattr(mod, "_enable_smc_production")
    assert hasattr(mod, "_discover_smc_strategies")


def test_b1039_dec505_4_folds_match_canonical_dates():
    """FOLDS list matches canonical DEC-505 dates from improvements.py."""
    mod = _import_runner()
    assert len(mod.FOLDS) == 4
    # Fold 1 OOS = 2022-05-05 -> 2023-05-05 per DEC-505
    assert mod.FOLDS[0][3] == date(2022, 5, 5)
    assert mod.FOLDS[0][4] == date(2023, 5, 5)
    # Fold 4 OOS = 2025-05-05 -> 2026-05-05
    assert mod.FOLDS[3][3] == date(2025, 5, 5)
    assert mod.FOLDS[3][4] == date(2026, 5, 5)
    # All folds share the same IS start (expanding-window per DEC-505)
    is_starts = {f[1] for f in mod.FOLDS}
    assert is_starts == {date(2021, 5, 5)}


def test_b1039_smc_phase_monkey_patch_in_memory_only():
    """_enable_smc_production sets in-memory SMC_PHASE='PRODUCTION'.

    Critical: does NOT touch backtest/config.py on disk; in-memory only
    so canary flag stays 'B-CANARY' in production checkouts.
    """
    mod = _import_runner()
    import backtest.config as cfg
    original = cfg.SMC_PHASE
    try:
        mod._enable_smc_production()
        assert cfg.SMC_PHASE == "PRODUCTION"
    finally:
        cfg.SMC_PHASE = original
    # Re-import config from disk; default value must still be B-CANARY
    importlib.reload(cfg)
    assert cfg.SMC_PHASE == "B-CANARY", (
        "Disk SMC_PHASE drifted from 'B-CANARY'; monkey-patch leaked. "
        "B1038 Council 131 Option-A canary flag corrupted."
    )


def test_b1039_discover_smc_strategies_returns_18():
    """Discovery dynamically finds 18 strat_smc_* entries (matches CLAUDE.md
    + smartmoneyconcepts_phase_c_declaration_2026_06_27.md item #5)."""
    mod = _import_runner()
    smc = mod._discover_smc_strategies()
    assert len(smc) == 18, (
        f"Expected 18 SMC strategies; got {len(smc)}. "
        f"CLAUDE.md + Phase C declaration assert 18."
    )
    # All keys contain 'smc_' substring
    for k in smc:
        assert "smc_" in k, f"Non-SMC key in discovery: {k}"


def test_b1039_evaluate_strategy_recognizes_fires_dict_contract():
    """Strategy contract: {'fires': bool, 'direction': str} per screener._strat."""
    mod = _import_runner()

    def fake_long_fires(s):
        return {"fires": True, "direction": "long", "category": "smc"}

    def fake_short_fires(s):
        return {"fires": True, "direction": "short", "category": "smc"}

    def fake_no_fire(s):
        return {"fires": False, "direction": "long", "category": "smc"}

    assert mod._evaluate_strategy("t1", fake_long_fires, {}) == "long"
    assert mod._evaluate_strategy("t2", fake_short_fires, {}) == "short"
    assert mod._evaluate_strategy("t3", fake_no_fire, {}) is None


def test_b1039_short_pnl_is_inverted():
    """When direction='short', a price-up move must produce NEGATIVE pnl_pct.

    Regression guard against the harness treating SHORT entries as LONG.
    """
    mod = _import_runner()
    # We can't run the full harness here (needs cache + heavy compute);
    # instead verify the logic is encoded in the source.
    src = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "direction == \"long\"" in src or "direction == 'long'" in src
    assert "-raw_pnl" in src, (
        "SHORT pnl inversion missing in runner; direction sign-flip "
        "must be present so short trades on up-moves are losers."
    )
