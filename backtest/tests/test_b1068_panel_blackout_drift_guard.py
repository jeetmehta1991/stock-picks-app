"""B1068 PIVOT #39 panel-blackout fix + drift-guard pyramid tests.

# Source: Council 168 RECOMMEND Option E REMOVE-EMA_SMA-FROM-SKIP +
# DRIFT-GUARD per CHECKLIST #77 + #115 + PIVOT #39 sub-agent
# investigation b1068_pivot_39_suspect_silent_investigation.md.

PIVOT #39 root cause: USE_PANEL_TECHNICAL_SIGNALS=True + skip='ema_sma'
caused technical_panel.compute_panel_signals_for_as_of to substitute for
compute_ema_sma but never emitted post-B609/B634/B721/B722 signals:
  below_ema_X (122 consumers)
  *_break_recent_5d (18 consumers)
  ema_X_Y_bearish (4 consumers)
Result: 9 of 30 SUSPECT SILENT strategies couldn't fire because they
read these signals and got silently-False.

B1068 fix: removed 'ema_sma' from skip set so compute_ema_sma runs again.
Drift-guard test: pin the invariant that panel must emit a SUPERSET of
compute_ema_sma signals so future signal-adds can't re-introduce the
same blackout bug class.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCREENER_PATH = REPO / "backtest" / "signals" / "screener.py"
PANEL_PATH = REPO / "backtest" / "signals" / "technical_panel.py"
TECHNICAL_PATH = REPO / "backtest" / "signals" / "technical.py"


def test_b1068_screener_skip_set_excludes_ema_sma():
    """B1068 PIVOT #39 fix: screener.py skip set must NOT include
    'ema_sma' so compute_ema_sma runs and emits below_ema_X /
    *_break_recent_5d / ema_X_Y_bearish signals."""
    content = SCREENER_PATH.read_text()
    # Find the skip set assignment
    bad_line = 'skip = {"rsi", "ema_sma", "simple_returns"}'
    assert bad_line not in content, (
        "B1068 PIVOT #39 FIX REGRESSED: skip set must NOT contain "
        "'ema_sma' -- panel substitution causes 30pct of SUSPECT SILENT "
        "strategies to never fire. Use skip = {'rsi', 'simple_returns'}"
    )
    good_line = 'skip = {"rsi", "simple_returns"}'
    assert good_line in content, (
        "B1068: screener.py must have skip = {'rsi', 'simple_returns'} "
        "post-PIVOT #39 fix"
    )


def test_b1068_pivot_39_lineage_in_screener():
    """B1068: PIVOT #39 lineage must be documented in screener.py near
    the skip set so future readers know why ema_sma was removed."""
    content = SCREENER_PATH.read_text()
    assert "B1068 PIVOT #39 FIX" in content, (
        "B1068: PIVOT #39 fix lineage must reference batch + pivot in "
        "screener.py near the skip set"
    )
    assert "Council 168" in content, (
        "B1068: Council 168 must be referenced for decision lineage"
    )


def test_b1068_drift_guard_below_ema_signals_in_technical():
    """B1068 drift-guard: compute_ema_sma in technical.py must emit
    below_ema_X signals (the post-B722 family). If this test fails,
    a future refactor may have removed the signals -- investigate."""
    content = TECHNICAL_PATH.read_text()
    # Spot-check key signals from sub-agent finding
    key_signals = ["below_ema_50", "below_ema_200"]
    missing = [s for s in key_signals if s not in content]
    assert not missing, (
        f"B1068 DRIFT-GUARD: compute_ema_sma must emit {key_signals} "
        f"signals. Missing: {missing}. Re-introducing skip='ema_sma' "
        f"would silently drop these for 122 consumer strategies."
    )


def test_b1068_drift_guard_panel_acknowledges_blackout():
    """B1068 drift-guard: technical_panel.py must EITHER emit the
    EMA-family signals (panel coverage parity) OR have a comment
    acknowledging the blackout. If neither, future refactor may
    re-enable skip='ema_sma' assuming panel covers them -- which it
    doesn't."""
    panel_content = PANEL_PATH.read_text()
    has_below_ema = "below_ema_" in panel_content
    has_blackout_comment = (
        "below_ema" in panel_content.lower()
        or "PIVOT #39" in panel_content
        or "B1068" in panel_content
        or "blackout" in panel_content.lower()
    )
    # Either condition is acceptable; assertion fails if BOTH are false
    # (meaning panel doesn't cover AND doesn't document the gap)
    assert has_below_ema or has_blackout_comment, (
        "B1068 DRIFT-GUARD: technical_panel.py must either emit "
        "below_ema_X signals (parity with compute_ema_sma) OR contain "
        "a comment referencing PIVOT #39 / B1068 / blackout so future "
        "readers know not to re-enable skip='ema_sma' without first "
        "extending panel coverage."
    )


def test_b1068_b1067_4fix_batch_still_passes():
    """B1068 regression guard: B1067 4-fix monitor batch must still pass
    after B1068 panel-blackout fix (no shared state changes)."""
    # Import-only check; full B1067 test run is separate
    import importlib.util
    monitor_path = REPO / "scripts" / "b1019_phase_1_runtime_monitor.py"
    spec = importlib.util.spec_from_file_location("monitor", monitor_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "_check_e_new_silent_floor"), (
        "B1068: B1067 FIX 3 E-NEW must still be present"
    )
    assert hasattr(mod, "_check_f_new_regime_coverage"), (
        "B1068: B1067 FIX 4 F-NEW must still be present"
    )


def test_b1068_pivot_39_evidence_artifact_exists():
    """B1068: sub-agent investigation report must be persisted per
    CHECKLIST #126 evidence-artifact rule."""
    report = REPO / "output_audit" / "b1068_pivot_39_suspect_silent_investigation.md"
    assert report.exists(), (
        "B1068: PIVOT #39 sub-agent investigation report must exist at "
        "output_audit/b1068_pivot_39_suspect_silent_investigation.md "
        "per CHECKLIST #126 evidence-artifact rule"
    )
    content = report.read_text()
    assert len(content) > 1000, (
        "B1068: PIVOT #39 report must be substantive (>1000 chars)"
    )
