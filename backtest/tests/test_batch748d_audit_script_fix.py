# Source: B748d owner-approved 2026-06-14 "Execute follow up tickets. Comply with checklist for each" + CHECKLIST #106(a)-(g) per CHECKLIST #77
"""B748d pin tests: extended TIER 2 producer audit per CHECKLIST #106(a)-(g).

The B748d audit-script-fix adds:
  (a) producer-source path discovery (depth-3 helper walk for orchestrators)
  (b) RECURSIVE glob (was parent-only)
  (c) temporal-coverage probe vs measurement window
  (d) schema-contract probe (function-body-scoped, not whole module)
  (g) consumer-enumeration scans ALL backtest/signals/*.py (was screener.py only)

These pins lock the new probes + the headline findings.
"""
from __future__ import annotations

from datetime import date

from scripts.audit_tier2_producer_caches import (
    PRODUCERS,
    _discover_producer_path,
    _find_consuming_strategies,
    _probe_data_path,
    _schema_contract_probe,
    _temporal_coverage_probe,
    audit_all,
)


def test_b748d_pin1_recursive_glob_finds_sec_edgar_subdirs():
    """B748d (b): recursive glob over `data_prefetch/sec_edgar/` must
    find > 11000 files (11 form-type subdirs × ~1700 files each).
    Pre-B748d parent-only glob returned 0 -> false Path D classification.
    """
    exists, n_rows, n_tickers = _probe_data_path("data_prefetch/sec_edgar")
    assert exists
    # n_tickers stores file count for directories
    assert n_tickers > 11000, (
        f"recursive glob should find >11k files; got {n_tickers}. "
        f"If you see ~0 the parent-only-glob regression is back."
    )


def test_b748d_pin2_discover_producer_path_catches_sec_edgar_drift():
    """B748d (a): producer-source path discovery must surface that
    `compute_sec_edgar_signals` reads from `sec_edgar_decoded/`, NOT
    `sec_edgar/`. Depth-3 helper walk required (compute -> helpers ->
    _load_decoded -> _DECODED_CACHE_DIR).
    """
    spec = next(p for p in PRODUCERS if p.func == "compute_sec_edgar_signals")
    discovered = _discover_producer_path(spec)
    assert "sec_edgar_decoded" in discovered.replace("\\", "/"), (
        f"discovery should surface sec_edgar_decoded; got {discovered!r}"
    )


def test_b748d_pin3_temporal_coverage_probe_works_on_known_date_col():
    """B748d (c): temporal-coverage probe must return a date range when
    the probed parquet has a known date column. Use sec_edgar_decoded
    (has filing_date) as the positive control.
    """
    result = _temporal_coverage_probe("data_prefetch/sec_edgar_decoded/8_K")
    assert result.get("present"), f"temporal probe missing: {result}"
    assert "first_date" in result and "last_date" in result, (
        f"first/last_date missing on positive control: {result}"
    )
    # 8_K decoded cache should span roughly 2020-2026
    assert result["first_date"] <= "2020-12-31"
    assert result["last_date"] >= "2024-01-01"


def test_b748d_pin4_schema_contract_probe_function_body_scoped():
    """B748d (d): schema-contract probe must scope to the SPECIFIC producer
    function body (depth 3 over helpers), not the entire module file. This
    prevents sibling-producer false-positives in shared modules like
    `congressional_alt_data.py` (6 sibling producers).
    """
    spec = next(p for p in PRODUCERS if p.func == "compute_housetrading_signals")
    actual_path = _discover_producer_path(spec) or spec.data_path
    result = _schema_contract_probe(spec, actual_path)
    if result.get("present") and "missing_cols" in result:
        # The producer body only checks `if "Date" in df.columns` (or similar
        # actual housetrading columns). Schema check should NOT bleed in
        # sibling-module column names like CommitteeName / DPI / OTC_Short.
        bleed = set(result["missing_cols"]) & {"CommitteeName", "DPI", "OTC_Short",
                                                "OTC_Total", "TransactionAmount",
                                                "TransactionDate", "BioGuideID"}
        assert not bleed, (
            f"schema-contract probe is bleeding sibling columns into housetrading: {bleed}"
        )


def test_b748d_pin5_consumer_enumeration_finds_in_module_strategies():
    """B748d (g): consumer enumeration scans ALL `backtest/signals/*.py`
    so in-module strategies in producer files (e.g. 4 in
    `index_rebalance.py`) are surfaced.
    """
    consumers = _find_consuming_strategies(("days_since_inclusion",))
    # The 4 in-module index_rebalance consumers should be found
    expected = {
        "strat_post_inclusion_drift_long",
        "strat_post_inclusion_reversal_short",
    }
    found = set(consumers)
    missing = expected - found
    assert not missing, (
        f"in-module index_rebalance consumers not found by extended scan: {missing}"
    )


def test_b748d_pin6_no_producer_classified_path_d_post_b748d():
    """B748d post-fix audit: 0 producers should classify as Path D since
    the recursive glob catches SEC EDGAR subdirs (the only previous Path D).
    If a NEW Path D appears, that's a real finding worth surfacing.
    """
    rows = audit_all()
    path_d = [r for r in rows if r.path_classification == "D"]
    assert not path_d, (
        f"unexpected Path D producers: {[r.producer for r in path_d]}"
    )


def test_b748d_pin7_path_drift_flags_surface_real_finding_set():
    """B748d: 4 real PATH DRIFT findings must surface in the issue_flags.
    These represent the bugs B748b+B748c made dispositions on.
    """
    rows = audit_all()
    drift_set = set()
    for r in rows:
        for f in r.issue_flags:
            if "REGISTRY_PATH_DRIFT" in f:
                drift_set.add(r.producer)
                break
    expected = {
        "compute_persistence_signals",
        "compute_sec_edgar_signals",
        "compute_news_sentiment_signals",
        "compute_index_rebalance_signals",
    }
    missing = expected - drift_set
    assert not missing, (
        f"PATH DRIFT not surfaced for known cases: {missing}; got {drift_set}"
    )


def test_b748d_pin8_known_event_runtime_probe_for_8k_item_1_01():
    """B748d (e): runtime probe with KNOWN-EVENT (ticker, date) pair drawn
    FROM the data must verify producer fires. AAL Item 1.01 on 2026-03-09
    is in the decoded cache; probe at 2026-03-16 (7d after) must fire.
    """
    from backtest.signals.sec_edgar_extractor import compute_sec_edgar_signals
    out = compute_sec_edgar_signals("AAL", date(2026, 3, 16))
    assert out.get("8k_item_1_01_filed_within_30d") is True, (
        f"AAL Item 1.01 should fire 7d after 2026-03-09; got {out}"
    )
