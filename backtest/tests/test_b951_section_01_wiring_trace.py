"""B951 (2026-06-20): pyramid tests for Section 1 wiring trace coverage extractor.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.3 + Council 55 UNANIMOUS 4/4
# verdict per owner directive 2026-06-20 'Council this'.
"""
from __future__ import annotations

import pytest


def test_b951_section_01_extractor_importable():
    """B951 contract: section_01_wiring_trace module importable + extract function callable."""
    from backtest.diagnostics import section_01_wiring_trace as mod
    assert hasattr(mod, "extract_section_01_for_strategy")
    assert hasattr(mod, "_parse_screener_for_strategy_signal_deps")
    assert hasattr(mod, "_load_signal_producer_index")


def test_b951_static_ast_screener_parser_returns_strategies():
    """B951 AST parser: returns dict mapping strategy names to signal-key lists."""
    from backtest.diagnostics.section_01_wiring_trace import _parse_screener_for_strategy_signal_deps
    deps = _parse_screener_for_strategy_signal_deps()
    # Should find ~219 strategies (matches ALL_STRATEGIES roster)
    assert len(deps) >= 200, f"Expected >=200 strategies parsed; got {len(deps)}"
    # Each value is a list of strings
    for strat, signals in deps.items():
        assert isinstance(signals, list)
        for sig in signals:
            assert isinstance(sig, str)


def test_b951_extract_section_01_for_known_strategy_returns_schema():
    """B951: extract for canonical strategy returns dict with expected keys."""
    from backtest.diagnostics.section_01_wiring_trace import extract_section_01_for_strategy
    result = extract_section_01_for_strategy("macd_crossover")
    expected_keys = {
        "n_signals_required", "n_signals_wired", "n_signals_orphan",
        "wiring_coverage_pct", "signals_required", "signals_wired",
        "signals_orphan", "wiring_map", "method", "limitation",
    }
    assert set(result.keys()) == expected_keys
    assert result["method"] == "static_ast"


def test_b951_extract_unknown_strategy_returns_zero_required():
    """B951: unknown strategy name returns n_signals_required=0."""
    from backtest.diagnostics.section_01_wiring_trace import extract_section_01_for_strategy
    result = extract_section_01_for_strategy("nonexistent_strategy_xyz")
    assert result["n_signals_required"] == 0


def test_b970_kappa_a_fstring_loop_expansion_avwap():
    """Council 73 kappa-a fix: f-string subscript assignments inside for-loops
    must resolve. Pre-fix, `out[f"above_avwap_{key}"] = ...` inside
    `for lookback, key in [(252,"252low"),(50,"50low"),(20,"20high"),(20,"20low")]`
    was missed by producer_index causing ~60-70 false-positive SIGNAL_ORPHAN.
    """
    from backtest.diagnostics.section_01_wiring_trace import _load_signal_producer_index
    _load_signal_producer_index.cache_clear()
    idx = _load_signal_producer_index()
    # All four loop-variable expansions must resolve
    for k in ("above_avwap_252low", "above_avwap_50low",
              "above_avwap_20high", "above_avwap_20low"):
        assert k in idx, f"{k} missing from producer_index after kappa-a fix"
    # Symmetric below_ variants
    for k in ("below_avwap_252low", "below_avwap_50low",
              "below_avwap_20high", "below_avwap_20low"):
        assert k in idx, f"{k} missing from producer_index after kappa-a fix"
    # Reclaim/loss event variants
    for k in ("avwap_252low_reclaim_recent_3d", "avwap_50low_loss_recent_3d"):
        assert k in idx, f"{k} missing from producer_index after kappa-a fix"


def test_b970_kappa_a_intermediate_var_expansion_macd():
    """Council 73 kappa-a fix: chained f-string via intermediate var must resolve.
    Pattern in technical.compute_macd:
      key = f"macd_{fast}_{slow}_{sig}"   # for fast,slow,sig in [(12,26,9),(8,21,5)]
      result[f"{key}_bullish"] = ...
    Pre-fix missed all macd_12_26_9_* and macd_8_21_5_* signal keys.
    """
    from backtest.diagnostics.section_01_wiring_trace import _load_signal_producer_index
    _load_signal_producer_index.cache_clear()
    idx = _load_signal_producer_index()
    for k in ("macd_12_26_9_bullish", "macd_12_26_9_bearish",
              "macd_12_26_9_crossover_up", "macd_12_26_9_crossover_dn",
              "macd_8_21_5_bullish", "macd_8_21_5_crossover_up"):
        assert k in idx, f"{k} missing from producer_index after kappa-a fix"


def test_b970_kappa_a_signal_orphan_count_reasonable():
    """Council 73 kappa-a regression: full producer_index must contain >=1000
    signal keys post-fix (pre-fix was ~640). Locks in non-regression on the
    f-string expansion paths so a future refactor doesn't silently drop them.
    """
    from backtest.diagnostics.section_01_wiring_trace import _load_signal_producer_index
    _load_signal_producer_index.cache_clear()
    idx = _load_signal_producer_index()
    assert len(idx) >= 1000, (
        f"producer_index has only {len(idx)} keys; expected >=1000 post-kappa-a fix. "
        "Likely the f-string/intermediate-var expansion regressed."
    )


def test_b951_section_01_populate_helper_writes_to_dossier(tmp_path):
    """B951: populate_section_01_for_dossier writes section_01_wiring_trace_coverage slot."""
    import json
    from backtest.diagnostics.section_01_populate import populate_section_01_for_dossier
    # Create minimal dossier
    dossier_path = tmp_path / "dossier.json"
    dossier_path.write_text(json.dumps({
        "strategy": "macd_crossover",
        "sections": {}
    }))
    populate_section_01_for_dossier("macd_crossover", dossier_path)
    with open(dossier_path) as f:
        updated = json.load(f)
    assert "section_01_wiring_trace_coverage" in updated["sections"]
    section = updated["sections"]["section_01_wiring_trace_coverage"]
    assert section is not None
    assert "n_signals_required" in section
    assert "method" in section
