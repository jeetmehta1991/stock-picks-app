"""Batch 526 (2026-05-31) -- SEC EDGAR decoded-cache validator tests.

Source: per CHECKLIST #77.
Queue rows: P17a (in flight) + P17b/c/d/e wire-in gating.

Pins:

  (1) Each gate function returns the expected schema (`name`, `pass`,
      `details`).
  (2) Synthetic happy-path: a well-formed decoded cache passes all 6
      gates.
  (3) Per-gate failure isolation: corrupting ONE aspect of the
      synthetic cache fails ONLY that gate, not others.
  (4) Script import + run_all_gates() works without raising on a
      fresh repo (returns a structured result dict even when the
      decoded cache is empty).
  (5) NOT-REGISTERED guard for the validator: the script is an
      operator-run tool, NOT wired into any engine path.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))


@pytest.fixture
def synthetic_cache(tmp_path: Path):
    """Build a fully-populated synthetic SEC cache (index + decoded)
    so the validator's 6 gates have something to inspect.

    Yields (index_dir, decoded_dir) and patches the validator's
    module-level paths so it scans the synthetic layout.
    """
    index_dir = tmp_path / "sec_edgar"
    decoded_dir = tmp_path / "sec_edgar_decoded"
    for form in ("SC_13D", "SC_13G", "8_K"):
        (index_dir / form).mkdir(parents=True)
        (decoded_dir / form).mkdir(parents=True)

    # Build N=8 tickers; index + decoded cover them all so coverage = 100%
    tickers = ("AAPL", "MSFT", "AMZN", "GOOGL", "META", "JPM", "DIS", "NFLX")
    for tkr in tickers:
        # Index parquet (minimal)
        idx_df = pd.DataFrame({
            "ticker":           [tkr] * 3,
            "filing_date":      pd.to_datetime([
                "2024-01-15", "2024-06-15", "2024-11-15"]),
            "accession_number": [f"0001-{tkr}-1", f"0001-{tkr}-2",
                                  f"0001-{tkr}-3"],
            "primary_doc":      ["a.htm", "b.htm", "c.htm"],
        })
        for form in ("SC_13D", "SC_13G", "8_K"):
            idx_df.to_parquet(index_dir / form / f"{tkr}.parquet",
                              index=False)

        # Decoded parquets per form
        sc_df = pd.DataFrame({
            "ticker":           [tkr] * 3,
            "filing_date":      pd.to_datetime([
                "2024-01-15", "2024-06-15", "2024-11-15"]).date,
            "accession_number": [f"0001-{tkr}-1", f"0001-{tkr}-2",
                                  f"0001-{tkr}-3"],
            "filer_identity":   ["Carl Icahn", "Vanguard", "BlackRock"],
            "percent_owned":    [6.2, 5.5, 7.1],
            "item_4_purpose":   ["", "", ""],
            "decoded_status":   ["ok", "ok", "ok"],
        })
        sc_df.to_parquet(decoded_dir / "SC_13D" / f"{tkr}.parquet",
                         index=False)
        sc_df.to_parquet(decoded_dir / "SC_13G" / f"{tkr}.parquet",
                         index=False)
        _8k_df = pd.DataFrame({
            "ticker":           [tkr] * 3,
            "filing_date":      pd.to_datetime([
                "2024-02-01", "2024-07-01", "2024-12-01"]).date,
            "accession_number": [f"0001-{tkr}-4", f"0001-{tkr}-5",
                                  f"0001-{tkr}-6"],
            "item_codes":       ["2.02", "1.01", "5.02"],
            "decoded_status":   ["ok", "ok", "ok"],
        })
        _8k_df.to_parquet(decoded_dir / "8_K" / f"{tkr}.parquet",
                          index=False)

    # Patch validator module paths + lower floors to match the
    # synthetic fixture size (8 tickers x 3 rows/form = 24 rows). The
    # production floors (500/1000) are calibrated for the real
    # ~5000-filing universe extraction, not unit-test scope.
    from scripts import validate_sec_edgar_decoded_completeness as v
    test_floors = {"SC_13D": 5, "SC_13G": 5, "8_K": 5}
    with patch.object(v, "INDEX_DIR", index_dir), \
         patch.object(v, "DECODED_DIR", decoded_dir), \
         patch.object(v, "MIN_ROWS_PER_FORM", test_floors):
        yield v, index_dir, decoded_dir


def test_batch526_validator_imports_clean():
    """Module import must not raise (used by `python scripts/...`)."""
    from scripts import validate_sec_edgar_decoded_completeness as v
    assert callable(v.run_all_gates)


def test_batch526_run_all_gates_returns_structured_dict_empty_cache(tmp_path):
    """When no decoded cache exists, gates fail gracefully but the
    function still returns a structured result -- never raises."""
    from scripts import validate_sec_edgar_decoded_completeness as v
    with patch.object(v, "INDEX_DIR", tmp_path / "idx"), \
         patch.object(v, "DECODED_DIR", tmp_path / "dec"):
        result = v.run_all_gates()
    assert "all_pass" in result
    assert "gates" in result
    assert len(result["gates"]) == 6
    # Empty cache -> all_pass=False
    assert result["all_pass"] is False


def test_batch526_synthetic_happy_path_passes_all_gates(synthetic_cache):
    """A well-formed cache passes all 6 gates."""
    v, _, _ = synthetic_cache
    result = v.run_all_gates()
    failed = [g["name"] for g in result["gates"] if not g["pass"]]
    assert result["all_pass"], (
        f"synthetic happy-path failed gates: {failed}\n"
        f"details: {[g['details'] for g in result['gates'] if not g['pass']]}"
    )


def test_batch526_coverage_gate_fires_on_partial_decoded(synthetic_cache):
    """Removing a decoded parquet drops coverage below 50% only if
    the index set is large enough -- with 8 tickers, removing 5
    drops coverage to 3/8 = 37.5% < 50% floor."""
    v, _, decoded_dir = synthetic_cache
    for tkr in ("AAPL", "MSFT", "AMZN", "GOOGL", "META"):
        (decoded_dir / "SC_13D" / f"{tkr}.parquet").unlink()
    g = v.gate_1_coverage()
    assert g["pass"] is False
    assert g["details"]["SC_13D"]["ratio"] < v.COVERAGE_FLOOR_PCT


def test_batch526_schema_gate_fires_on_missing_column(synthetic_cache):
    """Removing decoded_status column from one parquet trips the
    schema gate."""
    v, _, decoded_dir = synthetic_cache
    path = decoded_dir / "8_K" / "AAPL.parquet"
    df = pd.read_parquet(path).drop(columns=["decoded_status"])
    df.to_parquet(path, index=False)
    g = v.gate_2_schema()
    assert g["pass"] is False
    assert g["details"]["8_K"]["bad_count"] >= 1


def test_batch526_status_dist_gate_fires_on_low_ok_ratio(synthetic_cache):
    """If <80% of decoded rows are status=ok, gate 4 fails. Flipping
    every row to 'fetch_error' drops ok_ratio to 0."""
    v, _, decoded_dir = synthetic_cache
    for path in (decoded_dir / "SC_13D").glob("*.parquet"):
        df = pd.read_parquet(path)
        df["decoded_status"] = "fetch_error"
        df.to_parquet(path, index=False)
    g = v.gate_4_status_dist()
    assert g["pass"] is False
    assert g["details"]["SC_13D"]["ok_ratio"] == 0.0


def test_batch526_spot_check_gate_fires_when_aapl_2024_missing(synthetic_cache):
    """Removing AAPL's 8-K decoded parquet trips spot-check gate 5."""
    v, _, decoded_dir = synthetic_cache
    (decoded_dir / "8_K" / "AAPL.parquet").unlink()
    g = v.gate_5_spot_check()
    assert g["pass"] is False
    aapl = g["details"]["8_K_2024_per_ticker"]["AAPL"]
    assert aapl["pass"] is False


def test_batch526_sample_sanity_gate_fires_on_out_of_range_percent(synthetic_cache):
    """percent_owned > 100 trips gate 6."""
    v, _, decoded_dir = synthetic_cache
    path = decoded_dir / "SC_13D" / "AAPL.parquet"
    df = pd.read_parquet(path)
    df["percent_owned"] = 150.0
    df.to_parquet(path, index=False)
    g = v.gate_6_sample_sanity()
    assert g["pass"] is False


def test_batch526_validator_not_wired_into_engine():
    """SCAFFOLD invariant: the validator is operator-run, not wired
    into screen_instrument / agents / cube_populator. Flip this test
    when the wire-in is intentional."""
    repo = Path(__file__).resolve().parent.parent.parent
    targets = [
        repo / "backtest" / "signals" / "screener.py",
        repo / "backtest" / "engine" / "backtest.py",
    ]
    needle = "validate_sec_edgar_decoded_completeness"
    for tgt in targets:
        if not tgt.exists():
            continue
        assert needle not in tgt.read_text(encoding="utf-8"), (
            f"Batch 526 validator wired into {tgt.name}. If intentional, "
            f"flip this test + document the wire-in."
        )
