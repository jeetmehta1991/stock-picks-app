# Source: B690 revised step 1 (B745) + owner critique pull-forward 2026-06-13 + Decision 5 Cat 1 per CHECKLIST #77
"""B745 pin tests: TIER 2 producer audit script + finding-grade invariants.

The audit (scripts/audit_tier2_producer_caches.py) classifies 17 TIER 2
producers into Path A/B/C/D and runs a smoke probe + consumer enumeration
+ dead-strategy determination.

These pins lock the headline findings + script invariants. Re-running the
audit must reproduce the path classification + headline findings.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from scripts.audit_tier2_producer_caches import (
    PRODUCERS,
    ProducerAuditRow,
    _list_all_emitted_keys,
    _probe_data_path,
    audit_all,
)


# --------------------------------------------------------------------------
# Registry-level invariants
# --------------------------------------------------------------------------
def test_b745_pin1_producer_registry_has_16_tier2_producers_post_b748b():
    """PRODUCERS registry covers 16 TIER 2 producers post-B748b
    (compute_recent_8k_signal DELETED 2026-06-13 as genuine orphan).
    If this fails, the registry has been edited; verify the new producer
    was added intentionally + classify it.
    """
    assert len(PRODUCERS) == 16, f"expected 16 TIER 2 producers (post-B748b); got {len(PRODUCERS)}"


def test_b745_pin2_no_duplicate_producer_entries():
    """No (module, func) duplicates in the registry."""
    keys = [(p.module, p.func) for p in PRODUCERS]
    assert len(keys) == len(set(keys)), f"duplicate entries: {keys}"


# --------------------------------------------------------------------------
# Headline finding: B689 stub-claim refuted
# --------------------------------------------------------------------------
def test_b745_pin3_patentmomentum_cache_is_not_a_stub():
    """B689 audit claimed patentmomentum had STUB cache (1 entry). FALSE.
    The actual parquet has > 5,000,000 rows.
    """
    exists, n_rows, n_tickers = _probe_data_path("data_prefetch/quiver/patentmomentum/global.parquet")
    assert exists, "patentmomentum parquet missing"
    assert n_rows >= 5_000_000, (
        f"patentmomentum was claimed STUB (1 entry) by B689; actual rows={n_rows:,}. "
        f"If rows < 5M now, the cache was truncated or replaced -- investigate."
    )


def test_b745_pin4_corporatedonors_cache_is_not_a_stub():
    """Same for corporatedonors -- B689 claimed STUB; actual is 25K rows."""
    exists, n_rows, n_tickers = _probe_data_path("data_prefetch/quiver/corporatedonors/global.parquet")
    assert exists, "corporatedonors parquet missing"
    assert n_rows >= 20_000, (
        f"corporatedonors was claimed STUB (1 entry) by B689; actual rows={n_rows:,}. "
        f"If rows < 20K, the cache was truncated -- investigate."
    )


# --------------------------------------------------------------------------
# Path classification snapshot (locks current state for regression detection)
# --------------------------------------------------------------------------
def test_b745_pin5_classification_snapshot_post_b748b():
    """Path classification snapshot post-B748b (recent_8k DELETED):
      Path A: 12 producers (existing module-level caches)
      Path B: 2  producers (no cache; needs one added) -- was 3 pre-B748b
      Path C: 1  producer  (cross_sectional; needs ohlcv_dict)
      Path D: 1  producer  (sec_edgar_extractor; data dir empty)

    If this distribution changes, the change must be documented in
    EXECUTION_QUEUE.md and the relevant B746-B754 tickets re-scoped.
    """
    rows = audit_all()
    counts: dict[str, int] = {"A": 0, "B": 0, "C": 0, "D": 0}
    for r in rows:
        counts[r.path_classification] += 1
    assert counts == {"A": 12, "B": 2, "C": 1, "D": 1}, (
        f"path classification drift: {counts} (expected A=12, B=2, C=1, D=1 post-B748b). "
        f"Re-scope B746-B754 if intentional."
    )


def test_b745_pin6_specific_producer_paths_pinned():
    """Spot-check critical producers' path classifications.

    Locks individual classifications so a future regression on, e.g.,
    insider_buying's cache being removed flips it from A -> B and surfaces.
    """
    rows = audit_all()
    by_func = {r.producer: r.path_classification for r in rows}
    expected = {
        "compute_insider_cluster_signals":       "A",
        "compute_pead_signals":                  "A",
        "compute_short_interest_signals":        "A",
        "compute_news_sentiment_signals":        "A",
        "compute_patentmomentum_signals":        "A",
        "compute_corporatedonors_signals":       "A",
        "compute_cross_sectional_features":      "C",
        "compute_sec_edgar_signals":             "D",
    }
    for func, expected_path in expected.items():
        assert by_func.get(func) == expected_path, (
            f"{func} path classification drift: got {by_func.get(func)}, expected {expected_path}"
        )


# --------------------------------------------------------------------------
# Dead-producer findings
# --------------------------------------------------------------------------
def test_b745_pin7_zero_data_producers_flagged():
    """Three producers have 0 data rows + must be flagged in the audit:
      sec_edgar_extractor (Path D), index_rebalance + recent_8k (Path B but data-missing).

    Their consuming strategies have been firing on absent signal -- Pattern F input.
    """
    rows = audit_all()
    by_func = {r.producer: r for r in rows}
    sec_edgar = by_func.get("compute_sec_edgar_signals")
    assert sec_edgar is not None
    assert sec_edgar.data_row_count == 0, (
        f"sec_edgar should have 0 rows (B689 silent-gap was correct for THIS producer); "
        f"got {sec_edgar.data_row_count}"
    )
    assert sec_edgar.path_classification == "D"

    index_reb = by_func.get("compute_index_rebalance_signals")
    assert index_reb is not None
    assert index_reb.data_row_count == 0


def test_b745_pin8_emitted_keys_detection_finds_pead_signal_consumers():
    """The widened consumer enumeration (AST-detect emitted keys + grep
    screener.py) must find >= 5 PEAD consumers. PEAD has the most consumers
    in the TIER 2 cluster; if this drops below 5, the consumer enumeration
    has broken.
    """
    rows = audit_all()
    by_func = {r.producer: r for r in rows}
    pead = by_func.get("compute_pead_signals")
    assert pead is not None
    assert len(pead.consuming_strategies) >= 5, (
        f"PEAD consumer enumeration drift: got {len(pead.consuming_strategies)} consumers; "
        f"expected >= 5"
    )


def test_b745_pin9_emitted_keys_helper_returns_non_empty_for_pead():
    """The _list_all_emitted_keys helper must surface PEAD's actual emit keys.
    Sanity check on the AST walk used by the audit script.
    """
    spec = next(p for p in PRODUCERS if p.func == "compute_pead_signals")
    keys = _list_all_emitted_keys(spec)
    assert "within_pead_window" in keys, f"expected within_pead_window in {keys}"
    assert "days_since_last_earnings" in keys


# --------------------------------------------------------------------------
# Output artifact existence
# --------------------------------------------------------------------------
def test_b745_pin10_audit_artifacts_exist():
    """The audit script writes report + JSON to output_audit/b745_tier2_producer_audit/.
    These artifacts feed B746/B747/B748/B749 ticket scoping.
    """
    out_dir = Path(__file__).resolve().parents[2] / "output_audit" / "b745_tier2_producer_audit"
    assert (out_dir / "b745_audit_report.md").exists(), "audit report not written"
    assert (out_dir / "b745_audit_results.json").exists(), "audit JSON not written"
