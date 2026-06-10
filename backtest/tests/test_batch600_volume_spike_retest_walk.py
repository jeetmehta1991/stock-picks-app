"""Batch 600 walk-tests SUPERSEDED by Batch 682 deletion of strat_volume_
spike_breakout_retest per B680 self-critique CC-B + B620 precedent +
owner approval 2026-06-10.

Original B600 tests pinned the post-walk 5-gate design (resistance_break_
retest + vol_spike_2x + above_avwap_20low + close_above_open + close_in_
top_40pct_of_range for LONG; symmetric inverse for SHORT). That design
was correct per the walk's intent but the strategy itself was deleted
B682 due to B621 fire-count estimator 0.01/yr universe-wide projection
(WORST FAIL_FIRE_STARVED case in entire roster - 250x worse than B620
squeeze_setup_event_only_long deletion precedent at 2.5/yr).

Per B670 SM-9/SM-23 deletion precedent: deletion-verification test
replaces strategy-behavior tests. This file retains historical reference
to the walk methodology + the deletion rationale.
"""
from __future__ import annotations


def test_batch682_strat_volume_spike_breakout_retest_deleted():
    """B682 DELETION VERIFICATION: strat_volume_spike_breakout_retest is
    no longer importable from screener module + not in ALL_STRATEGIES."""
    import backtest.signals.screener as screener
    assert not hasattr(screener, "strat_volume_spike_breakout_retest"), (
        "B682 deletion: strat_volume_spike_breakout_retest must be REMOVED"
    )
    from backtest.signals.screener import ALL_STRATEGIES
    assert "volume_spike_breakout_retest" not in ALL_STRATEGIES, (
        "B682 deletion: 'volume_spike_breakout_retest' key must be REMOVED from ALL_STRATEGIES"
    )
