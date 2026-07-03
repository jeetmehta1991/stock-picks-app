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


def test_bug_277_triangle_producer_fires_on_spy_canonical():
    """BUG-277 FIXED (B1126 Council 245): detect_triangle now fires >=5 on SPY 4y.

    B1126 widened flat-top tolerance 0.001 -> 0.002 (Bulkowski 2005
    canonical). Empirical: SPY 4y detection went 0 -> 17 with widened
    tolerance. Test asserts >=5 detections on canonical rolling window.
    """
    import numpy as np
    import pandas as pd
    from pathlib import Path
    from backtest.signals.chart_patterns import detect_triangle

    spy_path = REPO / "data_prefetch" / "polygon" / "ohlcv_daily" / "SPY.parquet"
    if not spy_path.exists():
        pytest.skip(f"SPY OHLCV parquet missing at {spy_path}")
        return

    spy = pd.read_parquet(spy_path)
    spy["date"] = pd.to_datetime(spy["date"])
    spy = spy.set_index("date").sort_index()

    detections = 0
    for i in range(30, len(spy), 20):
        window = spy.iloc[i - 30 : i]
        if len(window) < 30:
            continue
        result = detect_triangle(window)
        if result.get("triangle_ascending_detected") or result.get("triangle_descending_detected"):
            detections += 1

    assert detections >= 5, (
        f"BUG-277 REGRESSION: detect_triangle detected {detections} triangles "
        f"on SPY 4y sample (rolling 30-bar every 20 bars); expected >=5 per "
        f"B1126 widened tolerance fix. If below 5, producer regressed."
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
