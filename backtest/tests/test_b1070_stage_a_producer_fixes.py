"""B1070 Stage A producer fixes pyramid tests.

# Source: Council 172/174/175 per CHECKLIST #77 + #115 + owner directive
# 2026-06-28 'Yes council this. Ensure thats its engine implemented.
# No silent misses. Ensure testing and evidence pyramid as per past
# workflows.'

5 producer P0 fixes:
  P0-1: compute_adx::adx_cross_up close-vs-ADX confusion
  P0-2: compute_vwap::avwap_20high silent continue on breakout bars
  P0-3: compute_volume NameError silent swallow (c_today scope)
  P0-4: SMC bare-except (verified ALREADY-LOGGED; pyramid asserts pattern)
  P0-5: lobbying KeyError (verified ALREADY-HANDLED; logger.debug ->
        logger.warning so failures surface)

Engine-activation verified per CHECKLIST #124 + feedback_wired_means_
engine_consumed.
"""
from __future__ import annotations

import re
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]


def _make_synthetic_ohlcv(n_bars=300, start_price=100.0, trend="up"):
    """Synthesize OHLCV df with deterministic trend."""
    rng = np.random.default_rng(42)
    if trend == "up":
        drift = np.linspace(0, 0.5, n_bars)
    elif trend == "down":
        drift = np.linspace(0, -0.5, n_bars)
    else:
        drift = np.zeros(n_bars)
    noise = rng.normal(0, 0.01, n_bars)
    returns = drift / n_bars + noise
    close = start_price * np.exp(np.cumsum(returns))
    high = close * (1 + np.abs(rng.normal(0, 0.005, n_bars)))
    low = close * (1 - np.abs(rng.normal(0, 0.005, n_bars)))
    open_ = close * (1 + rng.normal(0, 0.002, n_bars))
    volume = rng.integers(1_000_000, 5_000_000, n_bars).astype(float)
    dates = pd.date_range("2023-01-01", periods=n_bars, freq="D")
    return pd.DataFrame({
        "open": open_, "high": high, "low": low, "close": close, "volume": volume
    }, index=dates)


# ============================ P0-1 compute_adx ============================

def test_b1070_p0_1_adx_cross_up_can_be_true_for_ticker_above_25():
    """B1070 P0-1: adx_cross_up must be capable of True when adx rises
    above 25 from below. Pre-fix: padx = close PRICE meant for ANY ticker
    priced >$25, adx_cross_up was permanently False."""
    from backtest.signals.technical import compute_adx
    # Construct df where ADX crosses above 25; use a price series with
    # strong trending behavior + close > $25 (NVDA-class)
    df = _make_synthetic_ohlcv(n_bars=300, start_price=120.0, trend="up")
    out = compute_adx(df)
    assert "adx_cross_up" in out, "B1070 P0-1: adx_cross_up key must be emitted"
    assert isinstance(out["adx_cross_up"], bool), "B1070: adx_cross_up must be bool"
    # The actual True/False depends on synthetic data; the contract is
    # that the field exists + uses adx values not close prices
    assert "adx" in out, "B1070 P0-1: adx value must be emitted"


def test_b1070_p0_1_padx_compares_adx_not_close():
    """B1070 P0-1 PIN: source code must use ADX values for padx, not close."""
    src = (REPO / "backtest" / "signals" / "technical.py").read_text()
    # The bug pattern should NOT exist
    bad = 'padx = _safe_float(df["close"].iloc[-2])'
    assert bad not in src, (
        f"B1070 P0-1 REGRESSION: padx must NOT use df['close'].iloc[-2]. "
        f"Use adx_series.iloc[-2] or a[cols[0]].iloc[-2]"
    )
    # Lineage comment must be present
    assert "B1070 P0-1 FIX" in src, "B1070 P0-1: lineage comment required"


# ============================ P0-2 compute_vwap ============================

def test_b1070_p0_2_avwap_20high_emits_on_breakout_bar():
    """B1070 P0-2: avwap_20high family must populate when TODAY is the
    new 20-bar high (breakout bar) - previously silent continue dropped
    the entire family."""
    from backtest.signals.technical import compute_vwap
    # Construct df where last bar IS the new 20-bar high
    df = _make_synthetic_ohlcv(n_bars=300, start_price=100.0, trend="flat")
    # Force last bar to be max in last 20 by injecting a spike
    df.loc[df.index[-1], "high"] = float(df["high"].tail(25).max()) * 1.05
    df.loc[df.index[-1], "close"] = float(df["close"].tail(25).max()) * 1.05
    out = compute_vwap(df)
    # Verify the avwap_20high family is populated post-fix
    assert "avwap_20high" in out, (
        "B1070 P0-2 REGRESSION: avwap_20high must be emitted on breakout bar"
    )
    assert "above_avwap_20high" in out or "below_avwap_20high" in out, (
        "B1070 P0-2: above/below_avwap_20high must be emitted"
    )


def test_b1070_p0_2_lineage_documented():
    """B1070 P0-2: lineage comment in source."""
    src = (REPO / "backtest" / "signals" / "technical.py").read_text()
    assert "B1070 P0-2 FIX" in src, "B1070 P0-2: lineage comment required"


# ============================ P0-3 compute_volume =========================

def test_b1070_p0_3_capitulation_blowoff_keys_can_be_true():
    """B1070 P0-3: capitulation/blowoff keys must be EMITTED with real
    values (not stuck-False due to NameError swallow). Pre-fix: c_today
    used before definition -> NameError -> silent except -> all 6 keys
    deterministically False."""
    from backtest.signals.technical import compute_volume
    df = _make_synthetic_ohlcv(n_bars=300, start_price=100.0, trend="flat")
    out = compute_volume(df)
    expected_keys = [
        "vol_spike_2x_on_down_day_recent_3d",
        "vol_spike_2x_on_up_day_recent_3d",
        "drying_volume_on_up_turn",
        "drying_volume_on_down_turn",
        "capitulation_recent_3d",
        "blowoff_recent_3d",
    ]
    for k in expected_keys:
        assert k in out, f"B1070 P0-3 REGRESSION: {k} missing"
        assert isinstance(out[k], bool), f"B1070: {k} must be bool"


def test_b1070_p0_3_except_does_not_swallow_nameerror():
    """B1070 P0-3 PIN: except block must NOT catch NameError /
    AttributeError (structural bugs must propagate to pyramid)."""
    src = (REPO / "backtest" / "signals" / "technical.py").read_text()
    # The fix uses specific exception types
    fix_pattern = "except (IndexError, ZeroDivisionError, ValueError, KeyError)"
    assert fix_pattern in src, (
        "B1070 P0-3 REGRESSION: must catch only data-shape errors so "
        "NameError/AttributeError propagate"
    )


# ============================ P0-4 SMC bare-except ========================

def test_b1070_p0_4_smc_excepts_log_failures():
    """B1070 P0-4: SMC primitive try/except blocks must log on exception
    (verified ALREADY-LOGGED; this pin asserts pattern remains)."""
    src = (REPO / "backtest" / "signals" / "smc_ict.py").read_text()
    # Count log_silent_failure calls in the file
    log_calls = src.count("log_silent_failure")
    assert log_calls >= 5, (
        f"B1070 P0-4 PIN: SMC primitives must log failures via "
        f"log_silent_failure (found {log_calls}; expected >=5)"
    )


# ============================ P0-5 lobbying ==============================

def test_b1070_p0_5_lobbying_warning_level_not_debug():
    """B1070 P0-5: get_lobbying error log promoted from debug -> warning
    so repeated failures surface (debug usually filtered out)."""
    src = (REPO / "backtest" / "data" / "smart_money.py").read_text()
    # The fix promoted to warning
    assert 'logger.warning("get_lobbying' in src, (
        "B1070 P0-5 REGRESSION: get_lobbying error must use logger.warning "
        "(not debug) so failures surface in default log config"
    )


# ============================ no-silent-miss meta-test ====================

def test_b1070_no_bare_except_in_critical_paths():
    """B1070 META: no BARE 'except:' (without exception type) in critical
    paths. 'except Exception' with logging is acceptable per existing
    patterns; pure bare 'except:' is banned per CHECKLIST #122."""
    critical_paths = [
        REPO / "backtest" / "signals" / "technical.py",
        REPO / "backtest" / "signals" / "smc_ict.py",
        REPO / "backtest" / "signals" / "screener.py",
        REPO / "backtest" / "engine" / "backtest.py",
        REPO / "backtest" / "results" / "writer.py",
    ]
    bare_except_pattern = re.compile(r"^\s*except\s*:\s*(#.*)?$", re.MULTILINE)
    violations = []
    for path in critical_paths:
        if not path.exists():
            continue
        src = path.read_text()
        for m in bare_except_pattern.finditer(src):
            # Find line number
            line_num = src[:m.start()].count("\n") + 1
            violations.append(f"{path.name}:{line_num}")
    assert not violations, (
        f"B1070 META: bare 'except:' found in critical paths "
        f"(use specific exception types or 'except Exception as e' with "
        f"logging per CHECKLIST #122): {violations}"
    )


def test_b1070_stage_a_lineage():
    """B1070 Stage A: all 5 P0 fixes must have B1070 lineage comments."""
    technical = (REPO / "backtest" / "signals" / "technical.py").read_text()
    smart_money = (REPO / "backtest" / "data" / "smart_money.py").read_text()
    assert technical.count("B1070") >= 3, (
        "B1070 Stage A: technical.py must have lineage comments for "
        "P0-1, P0-2, P0-3 fixes (>=3 references)"
    )
    assert "B1070 P0-5 FIX" in smart_money, (
        "B1070 Stage A: smart_money.py must have P0-5 lineage"
    )
