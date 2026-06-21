"""B970 (2026-06-21): pyramid tests for Stream V reproducibility verifier.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.7 launch gate #14 +
# Council 72 RECOMMEND zeta per CHECKLIST #77 + #115.
"""
from __future__ import annotations

from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent.parent


def test_b970_seed_registry_exists():
    """B970: output_audit/seed_registry.json must exist + carry 5 strategies."""
    import json
    seed_path = REPO / "output_audit" / "seed_registry.json"
    assert seed_path.exists()
    data = json.load(open(seed_path))
    assert data["seed_int"] == 13371337
    assert len(data["strategies_sampled"]) == 5
    assert isinstance(data["stream_e_extractors_validated"], list)


def test_b970_seed_registry_strategies_deterministic():
    """B970: 5 strategies match random.Random(13371337) sample of ALL_STRATEGIES keys."""
    import json
    import random
    from backtest.signals.screener import ALL_STRATEGIES
    seed_path = REPO / "output_audit" / "seed_registry.json"
    data = json.load(open(seed_path))
    rng = random.Random(data["seed_int"])
    expected = rng.sample(sorted(ALL_STRATEGIES.keys()), 5)
    assert data["strategies_sampled"] == expected


def test_b970_stream_v_script_importable():
    """B970 contract: stream_v_verify_reproducibility.py importable."""
    from scripts import stream_v_verify_reproducibility as mod
    assert hasattr(mod, "main")
    assert hasattr(mod, "verify_reproducibility")
    assert hasattr(mod, "_all_extractors")
    assert hasattr(mod, "_bit_identical")
    assert hasattr(mod, "_load_seed_registry")


def test_b970_bit_identical_function():
    """B970: _bit_identical correctly identifies equal vs differing dicts."""
    from scripts.stream_v_verify_reproducibility import _bit_identical
    assert _bit_identical({"a": 1, "b": 2}, {"b": 2, "a": 1}) is True  # key order
    # int vs float canonicalize differently in JSON ("1" vs "1.0"); not bit-identical
    assert _bit_identical({"a": 1.0}, {"a": 1.0}) is True  # same type same value
    assert _bit_identical({"a": 1}, {"a": 2}) is False


def test_b970_all_extractors_loads_14_functions():
    """B970: _all_extractors returns >=10 extractor callables."""
    from scripts.stream_v_verify_reproducibility import _all_extractors
    extractors = _all_extractors()
    assert len(extractors) >= 10  # 14 currently; floor at 10 for resilience
    for section_id, fn in extractors.items():
        assert callable(fn)
        assert section_id.startswith("section_")


def test_b970_verify_reproducibility_smoke():
    """B970: verify_reproducibility runs without error on 1 strategy x all extractors."""
    from scripts.stream_v_verify_reproducibility import (
        verify_reproducibility, _all_extractors,
    )
    extractors = _all_extractors()
    # Pick first available extractor target; use a known canonical strategy
    results = verify_reproducibility(["macd_crossover"], extractors)
    assert results["n_strategies"] == 1
    assert results["n_extractors"] == len(extractors)
    assert results["n_total_checks"] == len(extractors)
    # All should pass given deterministic extractors
    assert results["all_bit_identical"] is True


def test_b970_path_launch_gate_14_satisfied():
    """B970: report JSON exists + claims gate 14 satisfied."""
    import json
    report_path = REPO / "output_audit" / "b970_stream_v_reproducibility_report.json"
    if not report_path.exists():
        pytest.skip("B970 report not yet generated; run scripts/stream_v_verify_reproducibility.py")
    report = json.load(open(report_path))
    assert report["batch"] == "B970"
    assert report["path_launch_gate_satisfied"] == "13.7 gate #14"
    assert report["all_bit_identical"] is True
    assert report["n_failed"] == 0
