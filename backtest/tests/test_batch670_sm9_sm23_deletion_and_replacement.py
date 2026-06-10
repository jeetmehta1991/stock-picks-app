"""Batch 670 (2026-06-10) -- SM-9 + SM-23 deletion + Class 7 NEW
replacements per owner-approved B669 cluster-walk reviewer F2 + F3 +
Pattern C STRENGTHENED disposition.

Owner decisions (B670 Round 1):
  Q1 SM-9 strat_institutional_distribution_short:
     DELETE + Class 7 NEW strat_simple_below_ema_50_short replacement
  Q2 SM-23 strat_institutional_capitulation_short:
     DELETE + Class 7 NEW strat_vol_spike_2x_below_ema_50_short replacement
  Q3 SM-23 rename: N/A (deleted)
  Q4 SM-5 wiring: verify routing first (DONE - orphan emitter confirmed);
     wiring scope deferred to Round 2 batch.

Per B611 deletion precedent on strat_institutional_breakdown_confirmation_short
(structurally identical Pattern C data-source-asymmetry deletion). Per
project_no_apriori_strategy_pruning explicit owner override per reviewer
F2 (prior is a regulatory fact -- 13F SEC long-only by rule -- not a guess).

Pins:

  Deletions (4):
  (1)  SM-9 strat_institutional_distribution_short no longer importable
       from screener module
  (2)  SM-9 no longer in ALL_STRATEGIES registry
  (3)  SM-23 strat_institutional_capitulation_short no longer importable
       from screener module
  (4)  SM-23 no longer in ALL_STRATEGIES registry

  Class 7 NEW replacements (4):
  (5)  strat_simple_below_ema_50_short importable + callable
  (6)  strat_simple_below_ema_50_short in ALL_STRATEGIES under key
       "simple_below_ema_50_short"
  (7)  strat_vol_spike_2x_below_ema_50_short importable + callable
  (8)  strat_vol_spike_2x_below_ema_50_short in ALL_STRATEGIES under key
       "vol_spike_2x_below_ema_50_short"

  Strategy registry invariants (2):
  (9)  ALL_STRATEGIES total count == 222 (net 0: deleted 2, added 2)
  (10) Both Class 7 NEW are registered in momentum_trend category
       (NOT smart_money_13f or institutional_persistence)

  Class 7 NEW fire-logic pins (4):
  (11) strat_simple_below_ema_50_short fires SHORT when below_ema_50=True
  (12) strat_simple_below_ema_50_short does NOT fire when below_ema_50=False
  (13) strat_vol_spike_2x_below_ema_50_short fires SHORT when both gates True
  (14) strat_vol_spike_2x_below_ema_50_short does NOT fire when only one
       gate True (AND-conjunction verified)

  Regime affinity (2):
  (15) Neither Class 7 NEW has explicit STRATEGY_REGIME_AFFINITY entry
       (B291 SHORT default applies: {bear, crisis, neutral})
  (16) Both Class 7 NEW fire in bear regime under B291 default; do NOT fire
       in bull regime under B291 default
"""
from __future__ import annotations


# ============ Deletions (4) ============

def test_batch670_sm9_function_deleted():
    """Pin (1): SM-9 strat_institutional_distribution_short no longer
    importable from screener module."""
    import backtest.signals.screener as screener
    assert not hasattr(screener, "strat_institutional_distribution_short"), (
        "B670 regression: deleted SM-9 strat_institutional_distribution_short "
        "is still importable. Deletion not complete."
    )


def test_batch670_sm9_registry_entry_removed():
    """Pin (2): SM-9 no longer in ALL_STRATEGIES registry."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "institutional_distribution_short" not in ALL_STRATEGIES, (
        "B670 regression: SM-9 'institutional_distribution_short' key "
        "still in ALL_STRATEGIES. Deletion not complete."
    )


def test_batch670_sm23_function_deleted():
    """Pin (3): SM-23 strat_institutional_capitulation_short no longer
    importable from screener module."""
    import backtest.signals.screener as screener
    assert not hasattr(screener, "strat_institutional_capitulation_short"), (
        "B670 regression: deleted SM-23 strat_institutional_capitulation_short "
        "is still importable. Deletion not complete."
    )


def test_batch670_sm23_registry_entry_removed():
    """Pin (4): SM-23 no longer in ALL_STRATEGIES registry."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "institutional_capitulation_short" not in ALL_STRATEGIES, (
        "B670 regression: SM-23 'institutional_capitulation_short' key "
        "still in ALL_STRATEGIES. Deletion not complete."
    )


# ============ Class 7 NEW replacements (4) ============

def test_batch670_class7_new_simple_below_ema_50_short_importable():
    """Pin (5): strat_simple_below_ema_50_short importable + callable."""
    from backtest.signals.screener import strat_simple_below_ema_50_short
    assert callable(strat_simple_below_ema_50_short)


def test_batch670_class7_new_simple_below_ema_50_short_in_registry():
    """Pin (6): registered under key 'simple_below_ema_50_short'."""
    from backtest.signals.screener import (
        ALL_STRATEGIES, strat_simple_below_ema_50_short,
    )
    assert ALL_STRATEGIES.get("simple_below_ema_50_short") is strat_simple_below_ema_50_short


def test_batch670_class7_new_vol_spike_2x_below_ema_50_short_importable():
    """Pin (7): strat_vol_spike_2x_below_ema_50_short importable + callable."""
    from backtest.signals.screener import strat_vol_spike_2x_below_ema_50_short
    assert callable(strat_vol_spike_2x_below_ema_50_short)


def test_batch670_class7_new_vol_spike_2x_below_ema_50_short_in_registry():
    """Pin (8): registered under key 'vol_spike_2x_below_ema_50_short'."""
    from backtest.signals.screener import (
        ALL_STRATEGIES, strat_vol_spike_2x_below_ema_50_short,
    )
    assert ALL_STRATEGIES.get("vol_spike_2x_below_ema_50_short") is strat_vol_spike_2x_below_ema_50_short


# ============ Strategy registry invariants (2) ============

def test_batch670_all_strategies_total_count_maintained():
    """Pin (9): ALL_STRATEGIES total == 222 (net 0 change: -2 deleted + 2 added)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 222, (
        f"B670 regression: ALL_STRATEGIES count is {len(ALL_STRATEGIES)}; "
        "expected 222 (deletions and additions should net to zero)"
    )


def test_batch670_class7_new_in_momentum_trend_category():
    """Pin (10): Both Class 7 NEW return category='momentum_trend' from
    their _strat call. NOT smart_money_13f or institutional_persistence."""
    from backtest.signals.screener import (
        strat_simple_below_ema_50_short,
        strat_vol_spike_2x_below_ema_50_short,
    )
    out1 = strat_simple_below_ema_50_short({"below_ema_50": True})
    out2 = strat_vol_spike_2x_below_ema_50_short(
        {"vol_spike_2x": True, "below_ema_50": True}
    )
    assert out1.get("category") == "momentum_trend"
    assert out2.get("category") == "momentum_trend"


# ============ Class 7 NEW fire-logic pins (4) ============

def test_batch670_simple_below_ema_50_short_fires_when_gate_true():
    """Pin (11): fires SHORT when below_ema_50=True."""
    from backtest.signals.screener import strat_simple_below_ema_50_short
    out = strat_simple_below_ema_50_short({"below_ema_50": True})
    assert out["fires"] is True
    assert out["direction"] == "short"


def test_batch670_simple_below_ema_50_short_blocked_when_gate_false():
    """Pin (12): does NOT fire when below_ema_50=False."""
    from backtest.signals.screener import strat_simple_below_ema_50_short
    out = strat_simple_below_ema_50_short({"below_ema_50": False})
    assert out["fires"] is False
    # Also test missing key (default False)
    out_missing = strat_simple_below_ema_50_short({})
    assert out_missing["fires"] is False


def test_batch670_vol_spike_below_ema_50_short_fires_when_both_gates_true():
    """Pin (13): fires SHORT when both vol_spike_2x + below_ema_50 True."""
    from backtest.signals.screener import strat_vol_spike_2x_below_ema_50_short
    out = strat_vol_spike_2x_below_ema_50_short(
        {"vol_spike_2x": True, "below_ema_50": True}
    )
    assert out["fires"] is True
    assert out["direction"] == "short"


def test_batch670_vol_spike_below_ema_50_short_blocked_when_only_one_gate():
    """Pin (14): AND-conjunction verified -- does NOT fire when only
    one of the two gates is True."""
    from backtest.signals.screener import strat_vol_spike_2x_below_ema_50_short
    # Only vol_spike True
    out_vol_only = strat_vol_spike_2x_below_ema_50_short(
        {"vol_spike_2x": True, "below_ema_50": False}
    )
    # Only below_ema_50 True
    out_ema_only = strat_vol_spike_2x_below_ema_50_short(
        {"vol_spike_2x": False, "below_ema_50": True}
    )
    assert out_vol_only["fires"] is False
    assert out_ema_only["fires"] is False


# ============ Regime affinity (2) ============

def test_batch670_class7_new_no_explicit_regime_entries():
    """Pin (15): Neither Class 7 NEW has explicit STRATEGY_REGIME_AFFINITY
    entry; B291 SHORT default {bear, crisis, neutral} applies."""
    from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY
    assert "simple_below_ema_50_short" not in STRATEGY_REGIME_AFFINITY
    assert "vol_spike_2x_below_ema_50_short" not in STRATEGY_REGIME_AFFINITY


def test_batch670_class7_new_b291_default_short_regime_behavior():
    """Pin (16): both Class 7 NEW fire in bear/crisis/neutral under B291
    default; do NOT fire in bull under B291 default."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    for strat in ("simple_below_ema_50_short", "vol_spike_2x_below_ema_50_short"):
        # SHORT direction in B291 default = {bear, crisis, neutral}
        assert should_strategy_fire_in_regime(
            strat, "bear", direction="short"
        ) is True
        assert should_strategy_fire_in_regime(
            strat, "crisis", direction="short"
        ) is True
        assert should_strategy_fire_in_regime(
            strat, "neutral", direction="short"
        ) is True
        assert should_strategy_fire_in_regime(
            strat, "bull", direction="short"
        ) is False
