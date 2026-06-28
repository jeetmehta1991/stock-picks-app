"""B1061 Phase D post-completion analyzer pyramid test.

# Source: Council 161 Option-2 wait-window pre-staging per CHECKLIST #77.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ANALYZER = REPO / "scripts" / "analyze_phase_d_results.py"


def test_b1061_analyzer_exists():
    """B1061: analyzer script must exist."""
    assert ANALYZER.exists(), (
        "B1061: scripts/analyze_phase_d_results.py must be present per "
        "Council 161 Option-2 wait-window pre-staging"
    )


def test_b1061_analyzer_imports_clean():
    """B1061: analyzer must import without errors (Python syntax)."""
    import ast
    code = ANALYZER.read_text()
    ast.parse(code)  # raises SyntaxError on failure


def test_b1061_analyzer_parses_phase_timing_markers():
    """B1061: analyzer must parse PHASE_TIMING markers from engine.log
    (B1057 C-fix instrumentation)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("analyzer", ANALYZER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Synthesize 3-day engine.log
    sample = (
        "2026-06-28 14:00:00 [INFO] PHASE_TIMING day=2022-10-19 start\n"
        "2026-06-28 14:00:00 [INFO] PHASE_TIMING day=2022-10-19 ohlcv_pit_built dur=0.001s tickers=2\n"
        "2026-06-28 14:00:00 [INFO] PHASE_TIMING day=2022-10-19 pre_exits dur=0.065s\n"
        "2026-06-28 14:00:00 [INFO] PHASE_TIMING day=2022-10-19 exits_done dur=0.000s closed=0\n"
        "2026-06-28 14:00:00 [INFO] PHASE_TIMING day=2022-10-19 screen_done dur=0.521s candidates=1\n"
        "2026-06-28 14:00:00 [INFO] PHASE_TIMING day=2022-10-19 sentiment_done dur=0.029s total=0.616s\n"
        "2026-06-28 14:00:01 [INFO] PHASE_TIMING day=2022-10-20 start\n"
        "2026-06-28 14:00:01 [INFO] PHASE_TIMING day=2022-10-20 ohlcv_pit_built dur=0.001s tickers=2\n"
        "2026-06-28 14:00:01 [INFO] PHASE_TIMING day=2022-10-20 screen_done dur=0.556s candidates=2\n"
        "2026-06-28 14:00:01 [INFO] PHASE_TIMING day=2022-10-20 sentiment_done dur=0.027s total=0.649s\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as f:
        f.write(sample)
        log_path = Path(f.name)
    try:
        timing = mod.parse_phase_timing(log_path)
        assert timing["n_markers"] >= 8, (
            f"B1061: expected >= 8 markers parsed, got {timing['n_markers']}"
        )
        assert timing["n_days"] == 2, (
            f"B1061: expected 2 days with total=X.Xs, got {timing['n_days']}"
        )
        assert "ohlcv_pit_built" in timing["stage_durations"], (
            "B1061: ohlcv_pit_built stage missing from durations"
        )
        assert "screen_done" in timing["stage_durations"], (
            "B1061: screen_done stage missing from durations"
        )
        assert len(timing["total_per_day"]) == 2, (
            "B1061: total_per_day must capture both total= lines"
        )
    finally:
        log_path.unlink(missing_ok=True)


def test_b1061_analyzer_handles_missing_engine_log_gracefully():
    """B1061: analyzer must not crash on missing engine.log."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("analyzer", ANALYZER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    timing = mod.parse_phase_timing(Path("/nonexistent/file.log"))
    assert timing["n_markers"] == 0
    assert timing["n_days"] == 0


def test_b1061_analyzer_percentile_computation():
    """B1061: pct() helper must compute percentiles correctly."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("analyzer", ANALYZER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    xs = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    # p50 of 10 sorted values; idx = round(0.5 * 9) = 4 -> xs[4] = 5.0
    assert mod.pct(xs, 50) == 5.0
    # p100 -> last element
    assert mod.pct(xs, 100) == 10.0
    # empty list -> 0
    assert mod.pct([], 50) == 0.0
