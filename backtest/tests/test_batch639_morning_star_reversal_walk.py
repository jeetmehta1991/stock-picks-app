"""Batch 639 (2026-06-09) -- Stage 4 walk of strat_morning_star per
owner-directed CHECKLIST #105 walk + 7 critique points on Step 1.

Owner directives applied (2026-06-09):
  (2) Reconcile-to-reversal: removed ema_50_200_bullish / ema_50_200
      _bearish trend gates from both directions. Strategy is now
      canonical Nison 1991 morning-star / evening-star pair: pattern +
      RSI-not-extreme band only.
  (a) Same-walk: deleted strat_evening_star_short as strictly redundant
      with strat_morning_star SHORT post-option-2 reconciliation.
  F3   Deleted STRATEGY_REGIME_AFFINITY['morning_star'] = {'bear'} entry
       (LONG side could never fire under bear-only gate; SHORT side
       over-restricted vs B291 default). Now falls back to B291
       direction-aware default.
  F4   Investigated dangling evening_star_short regime entry -> confirmed
       it was a real strategy (now deleted by (a)). Regime entry also
       deleted.
  F5   Queued: RSI default-50 family grep (separate ticket in
       EXECUTION_QUEUE.md - silent-gap class hiding in numeric defaults).
  F6   Added: CHECKLIST.md item (q) - candle-pattern producers using
       close[-1] must verify engine entry path is next-bar open.

Pins:
  (1) strat_morning_star LONG fires on morning_star + rsi<45 alone
  (2) strat_morning_star SHORT fires on evening_star + rsi>55 alone
  (3) strat_morning_star LONG no longer reads ema_50_200_bullish
      (gate removed -- omitting the key still fires LONG given pattern+RSI)
  (4) strat_morning_star LONG blocked by rsi >= 45
  (5) strat_morning_star SHORT blocked by rsi <= 55
  (6) strat_evening_star_short NOT importable (deleted)
  (7) "evening_star_short" NOT in ALL_STRATEGIES registry
  (8) "morning_star" NOT in STRATEGY_REGIME_AFFINITY (F3 deletion)
  (9) "evening_star_short" NOT in STRATEGY_REGIME_AFFINITY (F4 deletion)
  (10) B291 direction-aware default: morning_star LONG fires in
       {bull, neutral}, NOT in {bear, crisis}
  (11) B291 direction-aware default: morning_star SHORT fires in
       {bear, crisis, neutral}, NOT in {bull}
  (12) CHECKLIST.md contains item (q) candle-pattern next-bar-open rule
  (13) EXECUTION_QUEUE.md contains F5 RSI-default-50 family grep ticket
"""
from __future__ import annotations


def test_batch639_long_fires_on_pattern_and_rsi_only():
    """Pin (1)."""
    from backtest.signals.screener import strat_morning_star
    s = {"morning_star": True, "rsi_14": 30}
    # Notably: no ema_50_200_bullish key - LONG must still fire
    out = strat_morning_star(s)
    assert out["fires"] is True and out["direction"] == "long"


def test_batch639_short_fires_on_pattern_and_rsi_only():
    """Pin (2)."""
    from backtest.signals.screener import strat_morning_star
    s = {"evening_star": True, "rsi_14": 70}
    out = strat_morning_star(s)
    assert out["fires"] is True and out["direction"] == "short"


def test_batch639_long_no_longer_requires_ema_trend():
    """Pin (3): omitting ema_50_200_bullish key still fires LONG."""
    from backtest.signals.screener import strat_morning_star
    s = {"morning_star": True, "rsi_14": 30}
    assert "ema_50_200_bullish" not in s
    assert strat_morning_star(s)["fires"] is True


def test_batch639_long_blocked_by_rsi_above_45():
    """Pin (4)."""
    from backtest.signals.screener import strat_morning_star
    s = {"morning_star": True, "rsi_14": 50}
    assert strat_morning_star(s)["fires"] is False


def test_batch639_short_blocked_by_rsi_below_55():
    """Pin (5)."""
    from backtest.signals.screener import strat_morning_star
    s = {"evening_star": True, "rsi_14": 50}
    assert strat_morning_star(s)["fires"] is False


def test_batch639_evening_star_short_not_importable():
    """Pin (6): strat_evening_star_short deleted per (a)."""
    import backtest.signals.screener as screener
    assert not hasattr(screener, "strat_evening_star_short")


def test_batch639_evening_star_short_not_in_registry():
    """Pin (7)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "evening_star_short" not in ALL_STRATEGIES


def test_batch639_morning_star_regime_entry_deleted():
    """Pin (8) F3."""
    from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY
    assert "morning_star" not in STRATEGY_REGIME_AFFINITY


def test_batch639_evening_star_short_regime_entry_deleted():
    """Pin (9) F4."""
    from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY
    assert "evening_star_short" not in STRATEGY_REGIME_AFFINITY


def test_batch639_morning_star_long_b291_default():
    """Pin (10): direction-aware default. LONG fires {bull, neutral}."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    for r in ["bull", "neutral"]:
        assert should_strategy_fire_in_regime("morning_star", r, direction="long") is True, (
            f"LONG must fire in {r} per B291 default")
    for r in ["bear", "crisis"]:
        assert should_strategy_fire_in_regime("morning_star", r, direction="long") is False, (
            f"LONG must NOT fire in {r} per B291 default")


def test_batch639_morning_star_short_b291_default():
    """Pin (11): direction-aware default. SHORT fires {bear, crisis, neutral}."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    for r in ["bear", "crisis", "neutral"]:
        assert should_strategy_fire_in_regime("morning_star", r, direction="short") is True, (
            f"SHORT must fire in {r} per B291 default")
    assert should_strategy_fire_in_regime("morning_star", "bull", direction="short") is False


def test_batch639_checklist_q_candle_pit_rule_present():
    """Pin (12) F6: CHECKLIST.md contains candle-pattern next-bar-open rule."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    text = (root / "CHECKLIST.md").read_text(encoding="utf-8", errors="replace")
    # Marker token for the new (q) rule
    assert "candle-pattern" in text.lower() and "next-bar" in text.lower() and "close[-1]" in text


def test_batch639_execution_queue_f5_rsi_default_ticket_present():
    """Pin (13) F5: EXECUTION_QUEUE.md contains RSI default-50 family grep ticket."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    text = (root / "EXECUTION_QUEUE.md").read_text(encoding="utf-8", errors="replace")
    assert "RSI" in text and "default" in text.lower() and "B639" in text
