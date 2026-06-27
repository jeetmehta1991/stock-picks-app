"""pytest conftest for backtest/tests.

# Source: B1039 Council 132 Item #3 Phase A >=90% coverage measurement.
# Per CHECKLIST #77.

B1038 introduced SMC_PHASE B-CANARY short-circuit at compute_smc_signals
entry. This causes 7 SMC test files (unit/pit/integration/performance/
statistical/adversarial/xvalidation) that exercise compute_smc_signals
semantics to return {} from all calls, leaving the function body (lines
128-433) uncovered.

This fixture auto-monkeypatches SMC_PHASE='PRODUCTION' for any test in
files matching test_smartmoneyconcepts_*.py + test_smc_* - semantic
tests bypass the canary gate; production-mode tests (test_b1038_*)
explicitly opt-out.
"""
from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _smc_phase_production_for_semantic_tests(request, monkeypatch):
    """Auto-monkeypatch SMC_PHASE='PRODUCTION' for SMC semantic tests.

    Applies to: test_smartmoneyconcepts_*.py + test_smc_spof_sentinel.py
    Does NOT apply to: test_b1038_smc_phase_canary.py (tests the canary
      gate itself + must observe B-CANARY default)
    """
    test_file = str(request.node.fspath)
    if "test_b1038_smc_phase_canary" in test_file:
        return  # B1038 tests must see B-CANARY default
    if "test_smartmoneyconcepts_" in test_file or "test_smc_spof_sentinel" in test_file:
        import backtest.config as _cfg
        monkeypatch.setattr(_cfg, "SMC_PHASE", "PRODUCTION")
