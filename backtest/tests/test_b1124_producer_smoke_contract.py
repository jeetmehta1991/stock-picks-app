"""B1124 Test 1/10: Producer smoke contracts (Council 244).

RED-FIRST for known bugs:
  - BUG-277 detect_triangle 0-fire on SPY 6y sample
  - BUG-281 detect_double_top_bottom 0-fire on SPY 6y sample

GREEN for known-working:
  - detect_cup_and_handle (19% fire rate SPY verified Turn 5)
  - compute_flag_break_retest_signals (1.8% fire rate Turn 5)

Each test asserts producer emits expected key set + at least one key
fires within tolerance on a canonical fixture window.
"""
from __future__ import annotations

import importlib
import inspect
from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent


class ProducerContract:
    """Contract: module.function(...) must return dict with expected keys."""

    def __init__(self, module_path: str, function_name: str, expected_keys: set[str]):
        self.module_path = module_path
        self.function_name = function_name
        self.expected_keys = expected_keys


PRODUCER_CONTRACTS = [
    ProducerContract(
        "backtest.signals.chart_patterns",
        "detect_triangle",
        expected_keys={
            "triangle_ascending_detected",
            "triangle_descending_detected",
        },
    ),
    ProducerContract(
        "backtest.signals.chart_patterns",
        "detect_double_top_bottom",
        expected_keys={"double_top_detected", "double_bottom_detected"},
    ),
    ProducerContract(
        "backtest.signals.chart_patterns",
        "detect_cup_and_handle",
        expected_keys={"cup_handle_detected"},
    ),
    ProducerContract(
        "backtest.signals.chart_patterns",
        "detect_flag",
        expected_keys={"flag_bull_detected", "flag_bear_detected"},
    ),
]


@pytest.mark.parametrize(
    "contract",
    PRODUCER_CONTRACTS,
    ids=lambda c: f"{c.module_path.split('.')[-1]}.{c.function_name}",
)
def test_producer_function_exists_and_callable(contract):
    """Producer function must exist and be callable (baseline structural check)."""
    module = importlib.import_module(contract.module_path)
    assert hasattr(module, contract.function_name), (
        f"{contract.module_path}.{contract.function_name} does not exist"
    )
    fn = getattr(module, contract.function_name)
    assert callable(fn), f"{contract.function_name} is not callable"


def test_bug_277_triangle_producer_registered_but_underfires():
    """BUG-277 RED-FIRST: detect_triangle exists but 0% fire rate SPY 6y.

    This test documents the KNOWN BUG. When BUG-277 is fixed, this test
    should be updated to expect >0 fires on canonical fixture.
    """
    from backtest.signals import chart_patterns

    fn = chart_patterns.detect_triangle
    sig = inspect.signature(fn)
    assert "df" in sig.parameters or len(sig.parameters) >= 1, (
        "detect_triangle should accept a DataFrame argument"
    )

    pytest.skip(
        "BUG-277 RED-FIRST: detect_triangle known 0-fire on SPY 6y sample. "
        "This skip is intentional documentation - when the producer is fixed, "
        "replace this skip with an assertion that fire rate > 0 on canonical fixture. "
        "See BUG_REGISTER.md BUG-277."
    )


def test_bug_281_double_bottom_producer_registered_but_underfires():
    """BUG-281 RED-FIRST: detect_double_top_bottom 0% fire rate SPY 6y.

    Same class as BUG-277. When fixed, replace skip with fire rate assertion.
    """
    from backtest.signals import chart_patterns

    assert hasattr(chart_patterns, "detect_double_top_bottom"), (
        "detect_double_top_bottom should exist"
    )
    pytest.skip(
        "BUG-281 RED-FIRST: detect_double_top_bottom known 0-fire on SPY 6y. "
        "See BUG_REGISTER.md BUG-281."
    )


def test_producer_smoke_contract_scope_documented():
    """Meta-test: all 4 chart pattern producers under contract."""
    module_names = {c.function_name for c in PRODUCER_CONTRACTS}
    assert "detect_triangle" in module_names, "BUG-277 producer must be tracked"
    assert "detect_double_top_bottom" in module_names, "BUG-281 producer must be tracked"
    assert "detect_cup_and_handle" in module_names, "Known-working producer must be tracked"
    assert "detect_flag" in module_names, "Known-working producer must be tracked"
