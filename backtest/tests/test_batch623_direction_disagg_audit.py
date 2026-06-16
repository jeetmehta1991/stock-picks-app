"""Batch 623 (2026-06-08) -- direction-disaggregated regime-affinity
audit tests (option D Hybrid).

Source: scripts/direction_disaggregated_regime_audit.py (this batch);
output_batch395_final/trade_log.csv (existing cube data, 29360 trades).
Per CHECKLIST #77 source-of-truth declaration.

Owner directive (option D Hybrid): build the post-filter analysis tool
+ validate on existing trade_log. Counterfactual cube re-run (D-ii) is
deferred unless audit findings need empirical confirmation beyond what
the existing 29360-trade data already supports.

Pins:
  (1) audit harness imports cleanly
  (2) compare_keep_vs_remove correctly partitions trades by direction-
      aware default per B291 (LONG -> bull/neutral; SHORT -> bear/
      crisis/neutral)
  (3) classify_recommendation gives KEEP when KEEP-PnL dominates by
      >= 5pp
  (4) classify_recommendation gives REMOVE_OK when REMOVE-PnL >= KEEP-PnL
      with sufficient n
  (5) full audit produces 21 results matching the deferred dual entries
  (6) audit findings: 4 REMOVE_OK candidates documented below (drift
      detection pin)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.direction_disaggregated_regime_audit import (
    DEFAULT_LONG_REGIMES, DEFAULT_SHORT_REGIMES,
    audit,
    classify_recommendation,
    compare_keep_vs_remove,
    compute_direction_stats,
)


def test_batch623_imports():
    """Pin (1)."""
    assert DEFAULT_LONG_REGIMES == {"bull", "neutral"}
    assert DEFAULT_SHORT_REGIMES == {"bear", "crisis", "neutral"}


def test_batch623_compare_keep_vs_remove_partitions_correctly():
    """Pin (2): KEEP counts trades where regime in current; REMOVE
    counts LONG in default-LONG-regimes + SHORT in default-SHORT-regimes."""
    # Synthetic stats: bear regime has both LONG and SHORT; bull regime
    # has LONG only.
    stats = pd.DataFrame([
        {"direction": "long", "regime": "bear", "n_trades": 10,
         "mean_pnl_pct": 1.0, "std_pnl_pct": 2.0, "win_rate": 0.5,
         "total_pnl_pct": 10.0, "sharpe_proxy": 0.5},
        {"direction": "long", "regime": "bull", "n_trades": 20,
         "mean_pnl_pct": 0.5, "std_pnl_pct": 2.0, "win_rate": 0.5,
         "total_pnl_pct": 10.0, "sharpe_proxy": 0.25},
        {"direction": "short", "regime": "bear", "n_trades": 5,
         "mean_pnl_pct": -1.0, "std_pnl_pct": 2.0, "win_rate": 0.4,
         "total_pnl_pct": -5.0, "sharpe_proxy": -0.5},
    ])
    # Current entry is {bear}: dual gates both LONG+SHORT to bear only.
    cmp = compare_keep_vs_remove(stats, {"bear"})
    # KEEP: LONG-bear 10 + SHORT-bear -5 = 5 total pnl; 15 trades
    assert cmp["keep_total_pnl"] == 5.0
    assert cmp["keep_n"] == 15
    # REMOVE -> default: LONG-bull 10 (in {bull,neutral}); SHORT-bear -5
    # (in {bear,crisis,neutral}); LONG-bear blocked.
    assert cmp["remove_total_pnl"] == 5.0
    assert cmp["remove_n"] == 25


def test_batch623_classify_keep_when_remove_loses():
    """Pin (3): KEEP dominates REMOVE by > 5pp."""
    stats = pd.DataFrame([
        {"direction": "long", "regime": "bear", "n_trades": 50,
         "mean_pnl_pct": 2.0, "std_pnl_pct": 1.0, "win_rate": 0.5,
         "total_pnl_pct": 100.0, "sharpe_proxy": 2.0},
        {"direction": "long", "regime": "bull", "n_trades": 10,
         "mean_pnl_pct": -1.0, "std_pnl_pct": 1.0, "win_rate": 0.3,
         "total_pnl_pct": -10.0, "sharpe_proxy": -1.0},
    ])
    rec, cmp = classify_recommendation(stats, {"bear"})
    assert rec == "KEEP", f"Expected KEEP (KEEP=100, REMOVE=-10); got {rec}"


def test_batch623_classify_remove_ok_when_remove_wins_or_ties():
    """Pin (4): REMOVE_OK when REMOVE >= KEEP with sufficient n."""
    stats = pd.DataFrame([
        {"direction": "long", "regime": "bear", "n_trades": 50,
         "mean_pnl_pct": -1.0, "std_pnl_pct": 1.0, "win_rate": 0.3,
         "total_pnl_pct": -50.0, "sharpe_proxy": -1.0},
        {"direction": "long", "regime": "bull", "n_trades": 50,
         "mean_pnl_pct": 2.0, "std_pnl_pct": 1.0, "win_rate": 0.6,
         "total_pnl_pct": 100.0, "sharpe_proxy": 2.0},
    ])
    rec, cmp = classify_recommendation(stats, {"bear"})
    # KEEP: LONG-bear=-50; REMOVE: LONG-bull=+100
    assert rec == "REMOVE_OK", f"Expected REMOVE_OK (delta=+150); got {rec}"


def test_batch623_audit_produces_18_results():
    """Pin (5) B839 UPDATED: audit produces one result per deferred dual
    entry. Count drift 21 -> 18 due to subsequent strategy deletions
    (B620 squeeze_setup_event_only_long + B639 evening_star_short +
    B722 hull_rsi_short / po3_htf_aligned_long / po3_htf_aligned_short).
    Floor pinned to 18 per current B395-final cube state; if count rises
    again, this pin surfaces the addition."""
    tl = Path("output_batch395_final/trade_log.csv")
    if not tl.exists():
        pytest.skip("cube trade_log absent")
    result = audit(tl)
    assert result["deferred_strategies_audited"] == 18
    assert len(result["results"]) == 18
    # Every result has the required keys
    for r in result["results"]:
        assert "strategy" in r
        assert "current_regimes" in r
        assert "recommendation" in r
        assert "comparison" in r


# B623 audit verdicts as documented in commit message
EXPECTED_REMOVE_OK = {
    "camarilla_s3_bounce",     # current bear/crisis/neutral; REMOVE gains +104.2pp
    "force_index_breakout",    # current all-4; REMOVE gains +620.5pp
    "prev_day_low_bounce",     # current bear/neutral; REMOVE marginal +4.1pp
    "ultimate_oscillator",     # current bull; REMOVE gains +31.1pp
}


def test_batch623_remove_ok_set_matches_audit():
    """Pin (6): the 4 REMOVE_OK candidates surfaced by B623 must match
    the documented set in the commit message. Drift detection pin - if
    a strategy moves in/out of REMOVE_OK due to a cube re-run, this
    test surfaces the change."""
    tl = Path("output_batch395_final/trade_log.csv")
    if not tl.exists():
        pytest.skip("cube trade_log absent")
    result = audit(tl)
    remove_ok = {r["strategy"] for r in result["results"]
                 if r["recommendation"] == "REMOVE_OK"}
    assert remove_ok == EXPECTED_REMOVE_OK, (
        f"REMOVE_OK set drift -- expected {EXPECTED_REMOVE_OK}, got "
        f"{remove_ok}. Diff: added {remove_ok - EXPECTED_REMOVE_OK}, "
        f"removed {EXPECTED_REMOVE_OK - remove_ok}. Update commit + "
        f"this pin if intentional (likely indicates cube data refresh)."
    )
