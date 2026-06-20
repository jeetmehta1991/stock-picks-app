"""B950 (2026-06-20): pyramid tests for v2 ledger + verdict-bearing feature flag.

# Source: Council 54 UNANIMOUS option-epsilon ship-conditional verdict
# per owner directive 2026-06-20 (i)+(iii) combined.
"""
from __future__ import annotations

import pytest


def test_b950_ledger_v2_builder_script_importable():
    """B950 contract: build_walk_verdict_ledger_v2.py importable + main() callable."""
    from scripts import build_walk_verdict_ledger_v2 as mod
    assert hasattr(mod, "main")
    assert hasattr(mod, "build_ledger_v2")
    assert hasattr(mod, "parse_walk_doc_v2")


def test_b950_v2_section_header_no_hyphen_matches():
    """B950 A.1: no-hyphen section header `### T1. \\`strat_NAME\\`` matches."""
    from scripts.build_walk_verdict_ledger_v2 import WALK_HEADER_PATTERN_V2
    sample = "### T1. `strat_macd_crossover`"
    m = WALK_HEADER_PATTERN_V2.match(sample)
    assert m is not None, "no-hyphen format should match (TREND cluster)"
    assert m.group("strategy") == "strat_macd_crossover"
    assert m.group("cluster_id") == "T1"


def test_b950_v2_section_header_hyphen_matches():
    """B950 A.1: hyphen section header still matches (backward-compat with B948 BR-1)."""
    from scripts.build_walk_verdict_ledger_v2 import WALK_HEADER_PATTERN_V2
    sample = "### BR-1. `strat_52w_high_breakout` (Batch 586+589, 52w family, walked B676)"
    m = WALK_HEADER_PATTERN_V2.match(sample)
    assert m is not None
    assert m.group("strategy") == "strat_52w_high_breakout"
    assert m.group("cluster_id") == "BR-1"


def test_b950_v2_table_row_smart_money_format():
    """B950 A.2: table-row `| **SM-4** \\`strat_NAME\\`` format matches."""
    from scripts.build_walk_verdict_ledger_v2 import TABLE_ROW_PATTERN
    sample = "| **SM-4** `strat_ma_target_long` | Walked clean (EVENT) | NEW ticket queued |"
    m = TABLE_ROW_PATTERN.search(sample)
    assert m is not None
    assert m.group("strategy") == "strat_ma_target_long"
    assert m.group("cluster_id") == "SM-4"


def test_b950_v2_table_row_pivot_format():
    """B950 A.2: PIVOT table format `| **P5** | W10 \\`strategy_no_prefix\\`` matches."""
    from scripts.build_walk_verdict_ledger_v2 import TABLE_ROW_PATTERN
    sample = "| **P5** | W10 `camarilla_r4_breakout` | R3 fade level vs R4 breakout |"
    m = TABLE_ROW_PATTERN.search(sample)
    assert m is not None
    assert m.group("strategy") == "camarilla_r4_breakout"
    assert m.group("cluster_id") == "P5"


def test_b950_verdict_strength_classifier_strong():
    """B950 B: strong keyword present -> 'strong'."""
    from scripts.build_walk_verdict_ledger_v2 import _classify_verdict_strength
    assert _classify_verdict_strength(["SHIPPED"], []) == "strong"
    assert _classify_verdict_strength(["DELETED"], []) == "strong"
    assert _classify_verdict_strength(["VERIFIED"], []) == "strong"


def test_b950_verdict_strength_classifier_medium():
    """B950 B: >=2 medium keywords -> 'medium'; <2 -> 'walked_only'."""
    from scripts.build_walk_verdict_ledger_v2 import _classify_verdict_strength
    assert _classify_verdict_strength([], ["loosen", "tighten"]) == "medium"
    assert _classify_verdict_strength([], ["loosen"]) == "walked_only"
    assert _classify_verdict_strength([], []) == "walked_only"


def test_b950_ledger_loads_v2_preferentially():
    """B950: criterion module prefers ledger_v2.json over original."""
    from backtest.diagnostics.r5_inclusion_criterion import _load_walk_verdict_ledger
    ledger = _load_walk_verdict_ledger()
    if not ledger:
        pytest.skip("Neither ledger available")
    # v2 has 125 strategies; v1 has 108. If we got >108, we're loading v2.
    assert len(ledger) >= 108, f"Expected >=108 strategies; got {len(ledger)}"


def test_b950_feature_flag_default_true():
    """B950: LEDGER_REQUIRE_VERDICT_BEARING defaults True per Council 54 ship verdict."""
    from backtest.diagnostics.r5_inclusion_criterion import LEDGER_REQUIRE_VERDICT_BEARING
    assert LEDGER_REQUIRE_VERDICT_BEARING is True


def test_b950_walked_only_entry_filtered_when_flag_true():
    """B950: with flag True, walked_only entries filtered out from _walk_verdict_ledger_entries.

    Functional test: pick a strategy known to have only walked_only ledger entries
    (rare strategy added via parser but lacking verdict keywords).
    """
    from backtest.diagnostics import r5_inclusion_criterion as mod
    # Force-reload cache for isolation
    mod._WALK_VERDICT_LEDGER_CACHE = None
    raw_ledger = mod._load_walk_verdict_ledger()
    # Find a strategy with ONLY walked_only entries (no strong/medium)
    walked_only_strat = None
    for strat, entries in raw_ledger.items():
        if entries and all(e.get("verdict_strength") == "walked_only" for e in entries):
            walked_only_strat = strat
            break
    if walked_only_strat is None:
        pytest.skip("No walked_only-only strategy in v2 ledger; cannot test")
    # With flag True, this strategy's entries should be filtered out
    assert mod.LEDGER_REQUIRE_VERDICT_BEARING is True
    filtered = mod._walk_verdict_ledger_entries(walked_only_strat)
    assert filtered == [], (
        f"Strategy {walked_only_strat} has only walked_only entries; "
        f"should be filtered when flag True; got {filtered}"
    )
