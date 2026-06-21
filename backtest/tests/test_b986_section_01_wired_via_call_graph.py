"""B986 (2026-06-21): Phase P1 walk-1 Sub-C + Sub-D WIRED_VIA_CALL_GRAPH set.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.17 META + Council 90
# Option-6 HYBRID owner-approved 2026-06-21 'Approve your recommendation.
# Proceed council this.'

Verifies B986 Council 90 Option-6 implementation:
  - WIRED_VIA_CALL_GRAPH curated set exists + has expected entries
  - Set membership folds into _load_signal_producer_index
  - Sub-C activist_13d_long now 100% wired coverage
  - Sub-D january_effect_small_cap_long now 100% wired coverage
  - Sub-C empirical smoke: XRX/BEN/NEXT activist tickers fire
    sc_13d_filed_within_30d=True per pre-flight verification

Closes walk-1 11-of-11 RESOLVED.
"""
from __future__ import annotations

from datetime import date

from backtest.diagnostics.section_01_wiring_trace import (
    WIRED_VIA_CALL_GRAPH,
    _load_signal_producer_index,
    extract_section_01_for_strategy,
)


def test_b986_wired_via_call_graph_set_exists():
    """B986: WIRED_VIA_CALL_GRAPH curated set is exported."""
    assert isinstance(WIRED_VIA_CALL_GRAPH, dict)
    assert len(WIRED_VIA_CALL_GRAPH) >= 2  # Sub-C + Sub-D minimum


def test_b986_sub_c_entry_present():
    """B986: sc_13d_filed_within_30d in WIRED_VIA_CALL_GRAPH per Sub-C."""
    assert "sc_13d_filed_within_30d" in WIRED_VIA_CALL_GRAPH
    producer, evidence = WIRED_VIA_CALL_GRAPH["sc_13d_filed_within_30d"]
    assert producer == "sec_edgar_extractor.py"
    assert "compute_sec_edgar_signals" in evidence


def test_b986_sub_d_entry_present():
    """B986: cap_band in WIRED_VIA_CALL_GRAPH per Sub-D."""
    assert "cap_band" in WIRED_VIA_CALL_GRAPH
    producer, evidence = WIRED_VIA_CALL_GRAPH["cap_band"]
    assert producer == "screener.py"
    assert "cap_band_from_market_cap" in evidence


def test_b986_set_folded_into_producer_index():
    """B986: set membership appears in _load_signal_producer_index output."""
    # Force fresh load to pick up B986 fold-in
    _load_signal_producer_index.cache_clear()
    index = _load_signal_producer_index()
    assert "sc_13d_filed_within_30d" in index
    assert "cap_band" in index
    assert index["sc_13d_filed_within_30d"] == "sec_edgar_extractor.py"
    assert index["cap_band"] == "screener.py"


def test_b986_activist_13d_long_now_100_pct_coverage():
    """B986: activist_13d_long Sub-C now 100% wiring coverage post-fix."""
    import sys
    for m in list(sys.modules):
        if "section_01" in m:
            sys.modules.pop(m)
    from backtest.diagnostics.section_01_wiring_trace import extract_section_01_for_strategy
    result = extract_section_01_for_strategy("activist_13d_long")
    assert result["wiring_coverage_pct"] == 100.0, (
        f"B986: activist_13d_long expected 100% post-fix; got "
        f"{result['wiring_coverage_pct']}. orphan={result['signals_orphan']}"
    )
    assert result["signals_orphan"] == []


def test_b986_january_effect_small_cap_long_now_100_pct_coverage():
    """B986: january_effect_small_cap_long Sub-D now 100% wiring coverage."""
    import sys
    for m in list(sys.modules):
        if "section_01" in m:
            sys.modules.pop(m)
    from backtest.diagnostics.section_01_wiring_trace import extract_section_01_for_strategy
    result = extract_section_01_for_strategy("january_effect_small_cap_long")
    assert result["wiring_coverage_pct"] == 100.0, (
        f"B986: january_effect_small_cap_long expected 100% post-fix; got "
        f"{result['wiring_coverage_pct']}. orphan={result['signals_orphan']}"
    )
    assert result["signals_orphan"] == []


def test_b986_sub_c_empirical_smoke_passes_on_activist_ticker():
    """B986 integration: sc_13d_filed_within_30d fires True on activist ticker.

    Per Council 90 Option-6 Step 1: empirical proof producer wired
    end-to-end. XRX (Xerox) had documented SC 13D filing 2026-05-14.
    Skips if parquet data absent (CI environment may not have full
    sec_edgar_decoded cache).
    """
    import sys
    for m in list(sys.modules):
        if "sec_edgar" in m:
            sys.modules.pop(m)
    from pathlib import Path
    sc_path = Path("data_prefetch/sec_edgar_decoded/SC_13D/XRX.parquet")
    if not sc_path.exists():
        import pytest
        pytest.skip("XRX SC_13D parquet absent in CI environment")
    from backtest.signals.sec_edgar_extractor import compute_sec_edgar_signals
    out = compute_sec_edgar_signals("XRX", date(2026, 5, 20))
    assert out.get("sc_13d_filed_within_30d") is True, (
        f"B986: XRX 2026-05-20 expected sc_13d_filed_within_30d=True "
        f"(documented activist filing 2026-05-14); got {out}"
    )
