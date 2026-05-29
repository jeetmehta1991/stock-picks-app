"""Batch 461 (2026-05-29) -- AU5 portfolio_metrics parallel-universe investigation.

FINDING (queue framing was wrong by inspection):
  The queue claimed portfolio_metrics was computed in 6 files
  (metrics.py / writer.py / build_dashboard_phase_1a.py /
  merge_batch_outputs.py / run_t0_close_out.py / verify_batch_69_phase_3.py).
  Direct grep across the repo non-test code shows the actual layout:

    backtest/results/metrics.py:2718  - SINGLE COMPUTATION
      compute_portfolio_metrics_from_curves(eq_curve, bench_curve, capital)
        returns the canonical portfolio_metrics dict.

    backtest/results/writer.py:~1059  - SINGLE WRITER
      Calls compute_portfolio_metrics_from_curves(...) and json.dumps
      the result to output_dir / "portfolio_metrics.json".

    scripts/build_dashboard_phase_1a.py:~361  - SINGLE READER
      load_json("portfolio_metrics.json") -- consumes the file produced
      by writer.py. Does NOT recompute.

    backtest/engine/backtest.py:2364  - comment only, no compute/read
    backtest/engine/portfolio.py:~143 - docstring referencing the chain

  scripts/merge_batch_outputs.py / run_t0_close_out.py /
  verify_batch_69_phase_3.py: NO references to portfolio_metrics at all.
  The queue list of "6 files" was mistaken.

  Total: 1 computation + 1 writer + 1 reader + 2 documentation
  mentions = 5 contact points across 5 files, all part of a single
  pipeline. Zero parallel-universe computations.

NO CONSOLIDATION NEEDED. The single-source flow is already correct.

WHAT BATCH 461 DOES:
  - Adds a docstring at compute_portfolio_metrics_from_curves marking it
    explicitly as THE single source of truth and naming the canonical
    consumer chain (writer -> dashboard).
  - Adds this test asserting:
    1. Only one definition of compute_portfolio_metrics_from_curves exists.
    2. Only one writer of portfolio_metrics.json exists (writer.py).
    3. build_dashboard_phase_1a.py is a READER, not a recomputer (it
       does NOT import or call compute_portfolio_metrics_from_curves).
    4. The three queue-named scripts (merge_batch_outputs.py,
       run_t0_close_out.py, verify_batch_69_phase_3.py) contain ZERO
       references to portfolio_metrics -- the queue claim was wrong.
    5. The function docstring guards the single-source claim
       (greppable wiring guard so future refactors stay coordinated).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def test_only_one_definition_of_compute_portfolio_metrics_from_curves():
    """Single source of truth: only one `def compute_portfolio_metrics_from_curves`
    should exist across the repo non-test code."""
    matches = []
    for sub in ("backtest", "scripts"):
        for p in (REPO / sub).rglob("*.py"):
            if "tests" in p.parts:
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"^\s*def\s+compute_portfolio_metrics_from_curves\b",
                         text, flags=re.MULTILINE):
                matches.append(str(p.relative_to(REPO)).replace("\\", "/"))
    assert matches == ["backtest/results/metrics.py"], \
        f"compute_portfolio_metrics_from_curves must be defined exactly once " \
        f"in backtest/results/metrics.py; found definitions: {matches}"


def test_only_one_writer_of_portfolio_metrics_json():
    """Only writer.py writes portfolio_metrics.json -- no other module emits it."""
    writers = []
    write_re = re.compile(r"write_text|json\.dump|dumps|\.to_json|open\([^)]+['\"]w")
    for sub in ("backtest", "scripts"):
        for p in (REPO / sub).rglob("*.py"):
            if "tests" in p.parts:
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            for match in re.finditer(r'["\']portfolio_metrics\.json["\']', text):
                # Check 250-char window AROUND the string (both before and
                # after) for a write idiom. The canonical writer uses
                # `(output_dir / "portfolio_metrics.json").write_text(...)`
                # so the write keyword follows the string literal.
                start = max(0, match.start() - 250)
                end = min(len(text), match.end() + 250)
                if write_re.search(text[start:end]):
                    writers.append(str(p.relative_to(REPO)).replace("\\", "/"))
                    break
    writers = sorted(set(writers))
    assert writers == ["backtest/results/writer.py"], \
        f"portfolio_metrics.json must be written only by writer.py; found writers: {writers}"


def test_dashboard_phase_1a_is_reader_not_recomputer():
    """scripts/build_dashboard_phase_1a.py reads portfolio_metrics.json
    via load_json but never IMPORTS compute_portfolio_metrics_from_curves
    nor reimplements the math."""
    src = _read("scripts/build_dashboard_phase_1a.py")
    assert 'portfolio_metrics.json' in src, \
        "dashboard build script must reference the JSON it consumes"
    assert "compute_portfolio_metrics_from_curves" not in src, \
        "dashboard build must NOT import the canonical computer (re-derivation would be a parallel universe)"
    # Reads via load_json:
    assert re.search(
        r"load_json\(\s*['\"]portfolio_metrics\.json['\"]",
        src,
    ), "expected load_json('portfolio_metrics.json') pattern in dashboard script"


def test_queue_named_scripts_have_zero_portfolio_metrics_references():
    """The queue listed merge_batch_outputs.py, run_t0_close_out.py, and
    verify_batch_69_phase_3.py as portfolio_metrics consumers. Verified
    against current code: none of them contain a reference. The queue
    claim of 6 files was mistaken -- preserve this finding as a test
    so the same wrong list cannot be re-introduced without surfacing
    the lapse."""
    for rel in (
        "scripts/merge_batch_outputs.py",
        "scripts/run_t0_close_out.py",
        "scripts/verify_batch_69_phase_3.py",
    ):
        p = REPO / rel
        if not p.exists():
            pytest.skip(f"{rel} not present")
        text = p.read_text(encoding="utf-8", errors="ignore")
        assert "portfolio_metrics" not in text, \
            f"{rel} unexpectedly references portfolio_metrics -- " \
            f"re-investigate AU5 parallel-universe lens"


def test_metrics_docstring_marks_single_source_of_truth():
    """Batch 461 added a docstring guard at compute_portfolio_metrics_from_curves
    naming it as the single source of truth + the canonical writer/dashboard
    chain. Greppable so future refactors stay coordinated."""
    src = _read("backtest/results/metrics.py")
    assert "SINGLE SOURCE OF TRUTH FOR `portfolio_metrics`" in src
    assert "writer.py" in src and "build_dashboard_phase_1a.py" in src


def test_canonical_call_chain_remains_intact():
    """End-to-end wiring: writer.py imports compute_portfolio_metrics_from_curves
    and calls it; the file path it writes matches the dashboard reader's path."""
    writer_src = _read("backtest/results/writer.py")
    assert "from backtest.results.metrics import" in writer_src \
        and "compute_portfolio_metrics_from_curves" in writer_src, \
        "writer.py must import the canonical computer"
    assert re.search(
        r"compute_portfolio_metrics_from_curves\s*\(",
        writer_src,
    ), "writer.py must CALL the canonical computer, not just import"
    assert 'portfolio_metrics.json' in writer_src, \
        "writer.py must reference the canonical output filename"


def test_no_portfolio_metrics_recomputation_in_engine_or_scripts():
    """Defensive: any file that mentions portfolio_metrics + key portfolio
    formulas (sharpe / alpha / beta computations) is suspect for being a
    recomputer. Whitelist: metrics.py (the canonical computer)."""
    suspects = []
    formula_hints = re.compile(r"\b(sharpe|alpha|beta|pct_change|cumprod)\b")
    for sub in ("backtest", "scripts"):
        for p in (REPO / sub).rglob("*.py"):
            if "tests" in p.parts:
                continue
            rel = str(p.relative_to(REPO)).replace("\\", "/")
            if rel == "backtest/results/metrics.py":
                continue  # the legitimate source of truth
            text = p.read_text(encoding="utf-8", errors="ignore")
            if "portfolio_metrics" not in text:
                continue
            # File mentions portfolio_metrics. Does it compute Sharpe/alpha
            # in the SAME context (within ~20 lines)?
            for m in re.finditer(r"portfolio_metrics", text):
                start = max(0, m.start() - 500)
                end = min(len(text), m.end() + 500)
                window = text[start:end]
                # Skip if the only formula hint is in a comment/docstring
                # (heuristic: count code-line hints not preceded by `#`).
                hits = [
                    line for line in window.splitlines()
                    if formula_hints.search(line) and not line.lstrip().startswith("#")
                ]
                if len(hits) >= 3:
                    suspects.append((rel, len(hits)))
                    break
    # writer.py legitimately logs the result and may reference these terms
    # in a logger.info call. Strip writer.py from the suspect list.
    suspects = [s for s in suspects if s[0] != "backtest/results/writer.py"]
    assert suspects == [], \
        f"Files suspected of recomputing portfolio_metrics: {suspects}. " \
        "Investigate before promoting -- they may be a parallel universe."
