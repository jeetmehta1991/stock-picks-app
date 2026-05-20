"""Exit distribution sanity gate (Batch 261).

Permanent regression catch for the Phase 1A-alpha 2026-05-20 failure mode:
30.8% of 1181 trades closed via vix_spike_kill_switch_batch226 because
the +5 VIX-in-5-days threshold was too tight. By the time the 17h run
finished, alpha was destroyed.

This test would have caught it in <5 min by running a small backtest
fixture + asserting no single exit method fires >25% of trades.

Source: per CHECKLIST #77 - sanity gate codifies the lesson L-2026-05-20
'compute-spend smoke gate before any backtest >2h'. Joint with CHECKLIST #68
smoke->demo->full protocol (was scoped to API spend only; now extends to
compute spend).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]


# Single-exit-method dominance threshold. Lower = stricter; 25% catches
# Batch 226 vix_spike_kill_switch failure (which fired 30.8%) but doesn't
# false-positive on legitimate trailing_stop dominance (typically 50-65%).
# trailing_stop is the canonical exit per CLAUDE.md so it's whitelisted.
NON_DEFAULT_EXIT_DOMINANCE_THRESHOLD = 0.25
DEFAULT_EXITS = {"trailing_stop", "atr_trail_1x", "end_of_backtest"}


def _check_exit_distribution(trade_log: pd.DataFrame) -> dict:
    """Returns dict with dominant_non_default_exit (str or None) +
    its share (float). Defensive on empty + missing columns.
    """
    if trade_log is None or trade_log.empty:
        return {"dominant_non_default_exit": None, "share": 0.0, "n_trades": 0}
    exit_col = "exit_reason" if "exit_reason" in trade_log.columns else (
        "exit_method" if "exit_method" in trade_log.columns else None
    )
    if exit_col is None:
        return {"dominant_non_default_exit": None, "share": 0.0, "n_trades": len(trade_log)}
    n = len(trade_log)
    counts = trade_log[exit_col].value_counts()
    for exit_name, count in counts.items():
        if exit_name in DEFAULT_EXITS:
            continue
        share = count / n
        if share > NON_DEFAULT_EXIT_DOMINANCE_THRESHOLD:
            return {
                "dominant_non_default_exit": str(exit_name),
                "share": float(share),
                "n_trades": n,
                "count": int(count),
            }
    return {"dominant_non_default_exit": None, "share": 0.0, "n_trades": n}


def test_no_exit_method_dominates_synthetic():
    """Synthetic balanced trade log -> no single non-default exit dominates."""
    df = pd.DataFrame({
        "exit_reason": (
            ["trailing_stop"] * 60
            + ["vix_spike_kill_switch_batch226"] * 10
            + ["circuit_breaker_1"] * 10
            + ["time_stop_20d"] * 10
            + ["regime_flip"] * 10
        ),
    })
    result = _check_exit_distribution(df)
    assert result["dominant_non_default_exit"] is None, (
        f"Smoke balanced fixture should not flag any exit; got "
        f"{result['dominant_non_default_exit']} @ {result['share']:.1%}"
    )


def test_detects_vix_spike_dominance_regression():
    """Recreate Phase 1A-alpha 2026-05-20 failure mode -> should detect."""
    df = pd.DataFrame({
        "exit_reason": (
            ["trailing_stop"] * 60
            + ["vix_spike_kill_switch_batch226"] * 30  # 30% = above threshold
            + ["other"] * 10
        ),
    })
    result = _check_exit_distribution(df)
    assert result["dominant_non_default_exit"] == "vix_spike_kill_switch_batch226"
    assert result["share"] > 0.25


def test_canonical_trailing_stop_dominance_allowed():
    """trailing_stop dominance is canonical (whitelisted) -> no flag.
    Other exits must be below 25% threshold."""
    df = pd.DataFrame({
        "exit_reason": (
            ["trailing_stop"] * 60
            + ["circuit_breaker_1"] * 20  # below 25%
            + ["time_stop"] * 20          # below 25%
        ),
    })
    result = _check_exit_distribution(df)
    assert result["dominant_non_default_exit"] is None


def test_empty_trade_log_no_crash():
    result = _check_exit_distribution(pd.DataFrame())
    assert result["dominant_non_default_exit"] is None
    assert result["n_trades"] == 0


def test_missing_exit_column_no_crash():
    df = pd.DataFrame({"strategy": ["rsi"], "pnl_pct": [0.5]})
    result = _check_exit_distribution(df)
    assert result["dominant_non_default_exit"] is None


@pytest.mark.xfail(
    reason=(
        "Pre-Batch-261-rerun: output_v2/trade_log.csv still reflects the "
        "OLD VIX threshold (+5 in 5d). vix_spike_kill_switch_batch226 "
        "dominates at 30.8% in that stale baseline. After Phase 1A-alpha "
        "rerun with tightened threshold (VIX>35 AND +50% in 5d), this "
        "xfail removes."
    ),
    strict=False,
)
def test_output_v2_current_trade_log_passes_post_fix():
    """Forward-looking regression catch: after the Batch 261 rerun, current
    output_v2/trade_log.csv should NOT have vix_spike_kill_switch dominance.

    Currently xfail because the latest trade_log on disk is the PRE-fix run.
    After rerun completes, remove the xfail marker.
    """
    log_path = REPO / "output_v2" / "trade_log.csv"
    if not log_path.exists():
        pytest.skip("output_v2/trade_log.csv not present (CI or fresh clone)")
    df = pd.read_csv(log_path)
    result = _check_exit_distribution(df)
    if result["dominant_non_default_exit"] == "vix_spike_kill_switch_batch226":
        pytest.fail(
            f"Batch 261 fix regressed: vix_spike_kill_switch still dominates "
            f"({result['share']:.1%} of {result['n_trades']} trades). "
            f"Check exit_manager.py:507-528 threshold."
        )


# ---------------------------------------------------------------------------
# Future: compute-spend smoke gate
# ---------------------------------------------------------------------------
# When integrated into the canonical backtest CLI, this check fires at
# checkpoint write time. If any non-default exit > 25%, abort the run and
# surface to owner BEFORE compute is wasted further. This is the missing
# pyramid tier that would have caught the 2026-05-20 17h-waste failure
# in the first 5 minutes.
