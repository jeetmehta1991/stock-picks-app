"""Pin tests for scripts/pattern_t_family_grep_audit.py per Batch 763 +
S4-B755-COUNCIL-PATTERN-T-FAMILY-GREP-ALL-221-STRATEGIES.

# Source: scripts/pattern_t_family_grep_audit.py (B763 build)
# per CHECKLIST #77 + feedback_family_bug_grep_before_one_liners.md

Locks in:
- Signal-extraction regex correctness on synthetic strategy source
- Collinearity classification logic (HIGH / MEDIUM / CLEAN)
- Window-window overlap detection (the HIGH-collinearity heuristic)
"""
from __future__ import annotations

import pytest

from scripts.pattern_t_family_grep_audit import (
    MA_CROSS_PATTERNS,
    TREND_STATE_PATTERNS,
    _classify_collinearity,
    _extract_signals,
)


# ---------------------------------------------------------------------------
# Pin 1: MA_CROSS_PATTERNS non-empty + valid regex
# ---------------------------------------------------------------------------
def test_pin1_ma_cross_patterns_compile():
    import re
    assert len(MA_CROSS_PATTERNS) > 0
    for pat in MA_CROSS_PATTERNS:
        re.compile(pat)  # must compile without error


# ---------------------------------------------------------------------------
# Pin 2: TREND_STATE_PATTERNS non-empty + valid regex
# ---------------------------------------------------------------------------
def test_pin2_trend_state_patterns_compile():
    import re
    assert len(TREND_STATE_PATTERNS) > 0
    for pat in TREND_STATE_PATTERNS:
        re.compile(pat)


# ---------------------------------------------------------------------------
# Pin 3: _extract_signals captures golden_cross + price_above_ema_200
# from a synthetic strategy source
# ---------------------------------------------------------------------------
def test_pin3_extract_golden_cross_with_trend_gate():
    source = """
def strat_test(s):
    fires = s.get("ema_50_200_golden_cross") and s.get("price_above_ema_200", False)
    return _strat(fires, "long", "trend", ...)
"""
    ma, trend = _extract_signals(source)
    assert "ema_50_200_golden_cross" in ma
    assert "price_above_ema_200" in trend


# ---------------------------------------------------------------------------
# Pin 4: _extract_signals returns empty lists when no patterns present
# ---------------------------------------------------------------------------
def test_pin4_extract_empty_when_no_patterns():
    source = """
def strat_test(s):
    fires = s.get("rsi_14", 50) < 30 and s.get("bb_lower_touch", False)
    return _strat(fires, "long", "mean_reversion", ...)
"""
    ma, trend = _extract_signals(source)
    assert ma == []
    assert trend == []


# ---------------------------------------------------------------------------
# Pin 5: _classify_collinearity HIGH when MA-cross window overlaps trend gate
# (the canonical Pattern T case: ema_50_200_golden_cross + price_above_ema_200)
# ---------------------------------------------------------------------------
def test_pin5_classify_high_when_windows_overlap():
    ma_cross = ["ema_50_200_golden_cross"]
    trend = ["price_above_ema_200"]
    assert _classify_collinearity(ma_cross, trend) == "PATTERN_T_HIGH"


# ---------------------------------------------------------------------------
# Pin 6: _classify_collinearity MEDIUM when windows don't overlap
# (e.g. ema_9_21 cross + price_above_ema_200 -- different timescales)
# ---------------------------------------------------------------------------
def test_pin6_classify_medium_when_windows_differ():
    ma_cross = ["ema_9_21_golden_cross"]
    trend = ["price_above_ema_200"]
    assert _classify_collinearity(ma_cross, trend) == "PATTERN_T_MEDIUM"


# ---------------------------------------------------------------------------
# Pin 7: _classify_collinearity CLEAN_NO_MA_CROSS when no cross signal
# ---------------------------------------------------------------------------
def test_pin7_classify_clean_no_ma_cross():
    assert _classify_collinearity([], ["price_above_ema_200"]) == "CLEAN_NO_MA_CROSS"


# ---------------------------------------------------------------------------
# Pin 8: _classify_collinearity CLEAN_NO_TREND_GATE when no trend signal
# (e.g. simple golden_cross_50_200 strategy with NO additional trend gate)
# ---------------------------------------------------------------------------
def test_pin8_classify_clean_no_trend_gate():
    assert _classify_collinearity(
        ["ema_50_200_golden_cross"], []
    ) == "CLEAN_NO_TREND_GATE"


# ---------------------------------------------------------------------------
# Pin 9: macd_crossover detection
# ---------------------------------------------------------------------------
def test_pin9_macd_crossover_detected():
    source = """
def strat_test(s):
    fires = s.get("macd_12_26_9_crossover_up") and s.get("price_above_ema_50")
"""
    ma, trend = _extract_signals(source)
    # macd_*crossover* should be captured
    assert any("crossover" in m for m in ma)
    assert "price_above_ema_50" in trend


# ---------------------------------------------------------------------------
# Pin 10: psar_flip detection
# ---------------------------------------------------------------------------
def test_pin10_psar_flip_detected():
    source = """
def strat_test(s):
    fires = s.get("psar_flip_up") and s.get("price_above_ema_200")
"""
    ma, trend = _extract_signals(source)
    assert "psar_flip_up" in ma


# ---------------------------------------------------------------------------
# Pin 11: stoch_bullish_cross detection
# ---------------------------------------------------------------------------
def test_pin11_stoch_cross_detected():
    source = """
def strat_test(s):
    fires = s.get("stoch_bullish_cross") and s.get("price_above_ema_20")
"""
    ma, trend = _extract_signals(source)
    assert "stoch_bullish_cross" in ma
    assert "price_above_ema_20" in trend
    # 20 not in stoch_bullish_cross window-list -> MEDIUM
    assert _classify_collinearity(ma, trend) == "PATTERN_T_MEDIUM"


# ---------------------------------------------------------------------------
# Pin 12: tema_cross detection
# ---------------------------------------------------------------------------
def test_pin12_tema_cross_detected():
    source = """
def strat_test(s):
    fires = s.get("tema_cross_up") and s.get("price_above_tema")
"""
    ma, trend = _extract_signals(source)
    assert "tema_cross_up" in ma
