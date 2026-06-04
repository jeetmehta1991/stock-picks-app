"""Batch 581 (2026-06-04) -- ship 6 ICT strategies + 2 new producers
in one batch per owner directive 2026-06-04:
  "MMBM/MMSM (Accumulation -> Manipulation -> Distribution) + Week
  Opening Gap (Sunday open gap fill) - implement now. Judas Swing
  variant approve"

Strategies wired:
  judas_swing_long / judas_swing_short - false range-break + return
    to pivot midpoint (no new producer; uses existing smc_liquidity_swept_*
    + near_pivot + close_above/below_open)
  mmbm_long - Market Maker Buy Model bullish PO3 cycle
  mmsm_short - Market Maker Sell Model bearish PO3 cycle
  week_opening_gap_fill_down - fade Monday upside gap (short)
  week_opening_gap_fill_up - fade Monday downside gap (long)

Producers wired (backtest/signals/ict_producers.py):
  compute_po3_signals - 3-phase Accumulation/Manipulation/Distribution
    detector (emits po3_mmbm_setup / po3_mmsm_setup booleans)
  compute_week_opening_gap_signals - Monday-vs-Friday gap detector
    (emits week_open_gap_up_15pct / week_open_gap_down_15pct booleans)

Both producers ADDITIVE - new signals consumed only by the 4 new
B581 strategies. CHECKLIST #104 local-scope respected.

Pins:

  (1) all 6 strategies registered in ALL_STRATEGIES
  (2) ALL_STRATEGIES count = 213 (was 207 pre-B581)
  (3) Judas Swing long fires on sweep_dn + near_pivot + close_above_open
  (4) Judas Swing short fires on mirrored conditions
  (5) MMBM long fires when po3_mmbm_setup=True
  (6) MMSM short fires when po3_mmsm_setup=True
  (7) Week Opening Gap Fill DOWN (short) fires on gap_up_15pct=True
  (8) Week Opening Gap Fill UP (long) fires on gap_down_15pct=True
  (9) compute_po3_signals returns correct mmbm_setup on synthetic
      accumulation + sweep-down + reversal pattern
  (10) compute_po3_signals returns False mmbm_setup when accumulation
       range is too wide (no PO3 cycle possible)
  (11) compute_week_opening_gap_signals identifies Monday after Friday
       + 2pct gap up as week_open_gap_up_15pct=True
  (12) compute_week_opening_gap_signals returns is_week_open=False on
       a Tue->Wed transition (no weekend)
  (13) all 6 strategies have direction + category correct
"""
from __future__ import annotations

import pandas as pd


# ---------- registration + count pins (1)(2) ----------

def test_batch581_all_six_registered():
    """Pin (1)."""
    from backtest.signals.screener import ALL_STRATEGIES
    for name in (
        "judas_swing_long", "judas_swing_short",
        "mmbm_long", "mmsm_short",
        "week_opening_gap_fill_down", "week_opening_gap_fill_up",
    ):
        assert name in ALL_STRATEGIES, f"{name} not registered"


def test_batch581_count_213():
    """Pin (2)."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 213, (
        f"ALL_STRATEGIES = {len(ALL_STRATEGIES)}; expected 213 "
        f"(207 pre-B581 + 6 new ICT strategies)"
    )


# ---------- Judas Swing pins (3)(4) ----------

def test_batch581_judas_long_fires():
    """Pin (3)."""
    from backtest.signals.screener import strat_judas_swing_long
    out = strat_judas_swing_long({
        "smc_liquidity_swept_dn": True,
        "near_pivot": True,
        "close_above_open": True,
    })
    assert out["fires"] is True
    assert out["direction"] == "long"
    # Missing sweep -> no fire
    out_no_sweep = strat_judas_swing_long({
        "smc_liquidity_swept_dn": False,
        "near_pivot": True,
        "close_above_open": True,
    })
    assert out_no_sweep["fires"] is False


def test_batch581_judas_short_mirror():
    """Pin (4)."""
    from backtest.signals.screener import strat_judas_swing_short
    out = strat_judas_swing_short({
        "smc_liquidity_swept_up": True,
        "near_pivot": True,
        "close_below_open": True,
    })
    assert out["fires"] is True
    assert out["direction"] == "short"


# ---------- MMBM/MMSM pins (5)(6) ----------

def test_batch581_mmbm_long_fires():
    """Pin (5)."""
    from backtest.signals.screener import strat_mmbm_long
    out = strat_mmbm_long({"po3_mmbm_setup": True})
    assert out["fires"] is True
    assert out["direction"] == "long"
    # Setup False -> no fire
    out_no = strat_mmbm_long({"po3_mmbm_setup": False})
    assert out_no["fires"] is False


def test_batch581_mmsm_short_fires():
    """Pin (6)."""
    from backtest.signals.screener import strat_mmsm_short
    out = strat_mmsm_short({"po3_mmsm_setup": True})
    assert out["fires"] is True
    assert out["direction"] == "short"


# ---------- Week Opening Gap pins (7)(8) ----------

def test_batch581_week_gap_fill_down_short():
    """Pin (7) - upside gap -> fade short."""
    from backtest.signals.screener import strat_week_opening_gap_fill_down
    out = strat_week_opening_gap_fill_down({"week_open_gap_up_15pct": True})
    assert out["fires"] is True
    assert out["direction"] == "short"


def test_batch581_week_gap_fill_up_long():
    """Pin (8) - downside gap -> fade long."""
    from backtest.signals.screener import strat_week_opening_gap_fill_up
    out = strat_week_opening_gap_fill_up({"week_open_gap_down_15pct": True})
    assert out["fires"] is True
    assert out["direction"] == "long"


# ---------- PO3 producer pins (9)(10) ----------

def test_batch581_po3_producer_mmbm_setup():
    """Pin (9) - synthetic accumulation + sweep + reversal -> mmbm_setup."""
    from backtest.signals.ict_producers import compute_po3_signals
    # 5 bars in tight range 99-101 (range ~2pct), then 6th bar sweeps
    # below 99 to 92 but closes back at 99.5 with bullish bar
    df = pd.DataFrame({
        "open":   [100, 100, 100, 100, 100, 94],
        "high":   [101, 101, 101, 101, 101, 95],
        "low":    [ 99,  99,  99,  99,  99, 92],
        "close":  [100, 100, 100, 100, 100, 99.5],
        "volume": [1_000_000] * 6,
    })
    out = compute_po3_signals(df, accum_window=5)
    assert out["po3_accumulation_active"] is True
    assert out["po3_manipulation_sweep_down"] is True
    assert out["po3_mmbm_setup"] is True
    assert out["po3_mmsm_setup"] is False


def test_batch581_po3_no_setup_when_range_wide():
    """Pin (10) - wide accumulation range -> no PO3 setup possible."""
    from backtest.signals.ict_producers import compute_po3_signals
    # 5 bars range 80-120 (range ~40pct, way above 5pct threshold)
    df = pd.DataFrame({
        "open":   [100, 90, 110, 95, 115, 80],
        "high":   [120, 100, 120, 110, 120, 85],
        "low":    [ 80,  85,  90,  85,  90, 70],
        "close":  [100,  90, 110,  95, 115, 75],
        "volume": [1_000_000] * 6,
    })
    out = compute_po3_signals(df, accum_window=5)
    assert out["po3_accumulation_active"] is False
    assert out["po3_mmbm_setup"] is False
    assert out["po3_mmsm_setup"] is False


# ---------- Week Opening Gap producer pins (11)(12) ----------

def test_batch581_week_gap_producer_monday_after_friday():
    """Pin (11) - Friday -> Monday transition with 2pct gap up."""
    from backtest.signals.ict_producers import compute_week_opening_gap_signals
    # 2024-06-07 is a Friday; 2024-06-10 is a Monday
    df = pd.DataFrame({
        "open":   [99.0, 102.0],   # Monday opens at 102 vs Friday close 100
        "high":   [101.0, 103.0],
        "low":    [98.0, 101.0],
        "close":  [100.0, 102.5],
        "volume": [1_000_000, 1_000_000],
    }, index=pd.to_datetime(["2024-06-07", "2024-06-10"]))
    out = compute_week_opening_gap_signals(df)
    assert out["is_week_open"] is True
    assert out["week_open_gap_up_pct"] > 0
    assert out["week_open_gap_up_15pct"] is True
    assert out["week_open_gap_down_15pct"] is False


def test_batch581_week_gap_producer_no_weekend():
    """Pin (12) - mid-week transition does NOT count as week_open."""
    from backtest.signals.ict_producers import compute_week_opening_gap_signals
    # Tuesday -> Wednesday
    df = pd.DataFrame({
        "open":   [99.0, 105.0],   # large gap but mid-week
        "high":   [101.0, 106.0],
        "low":    [98.0, 104.0],
        "close":  [100.0, 105.5],
        "volume": [1_000_000, 1_000_000],
    }, index=pd.to_datetime(["2024-06-11", "2024-06-12"]))  # Tue -> Wed
    out = compute_week_opening_gap_signals(df)
    assert out["is_week_open"] is False
    assert out["week_open_gap_up_15pct"] is False
    assert out["week_open_gap_down_15pct"] is False


# ---------- direction + category invariants (13) ----------

def test_batch581_directions_and_categories():
    """Pin (13)."""
    from backtest.signals.screener import (
        strat_judas_swing_long, strat_judas_swing_short,
        strat_mmbm_long, strat_mmsm_short,
        strat_week_opening_gap_fill_down, strat_week_opening_gap_fill_up,
    )
    expected = [
        (strat_judas_swing_long, "long",
            {"smc_liquidity_swept_dn": True, "near_pivot": True, "close_above_open": True}),
        (strat_judas_swing_short, "short",
            {"smc_liquidity_swept_up": True, "near_pivot": True, "close_below_open": True}),
        (strat_mmbm_long, "long",
            {"po3_mmbm_setup": True}),
        (strat_mmsm_short, "short",
            {"po3_mmsm_setup": True}),
        (strat_week_opening_gap_fill_down, "short",
            {"week_open_gap_up_15pct": True}),
        (strat_week_opening_gap_fill_up, "long",
            {"week_open_gap_down_15pct": True}),
    ]
    for fn, expected_dir, fire_signals in expected:
        out = fn(fire_signals)
        assert out["direction"] == expected_dir, (
            f"{fn.__name__}: direction = {out['direction']}, expected {expected_dir}"
        )
        assert out["category"] == "ict", (
            f"{fn.__name__}: category = {out['category']}, expected 'ict'"
        )
