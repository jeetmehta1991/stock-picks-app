"""B1320 (Council 352, M3=a): the hybrid_50pct_target exit was missing a
SHORT-side hard stop -- a losing short had no stop before half_taken and rode
to end_of_data, producing the -32.7%/trade + -11,941pp additive-DD anomaly on
short strategies (B1315/B1316). This pins the symmetric close-based short stop.
"""
import datetime as dt
import pandas as pd
import pytest

from backtest.engine.exit_strategies import exit_hybrid_50pct
from backtest.engine.exit_strategies_vectorized import vexit_hybrid_50pct


def _df(closes, entry_date):
    """Build a daily OHLC frame starting the day AFTER entry_date."""
    idx = pd.to_datetime([entry_date + dt.timedelta(days=i + 1)
                          for i in range(len(closes))])
    rows = [{"open": c, "high": c, "low": c, "close": c} for c in closes]
    return pd.DataFrame(rows, index=idx)


def test_losing_short_is_stopped_not_ride_to_eod():
    entry_date = dt.date(2023, 1, 2)
    entry_price = 100.0
    # atr small -> short target (entry - 3*atr = 97) is never hit as price RISES.
    # stop for a short = entry*1.10 = 110. Price climbs through it.
    df = _df([104.0, 108.0, 111.0, 120.0], entry_date)
    res = exit_hybrid_50pct(df, entry_date, entry_price, "short", atr=1.0)
    assert res["exit_reason"] == "stop_loss", (
        f"losing short must stop out, got {res['exit_reason']}")
    assert res["exit_price"] == pytest.approx(110.0, abs=0.01)
    # loss must be bounded near -10% (not the unbounded -20%/-100% ride)
    assert abs(res["pnl_pct"]) <= 11.0
    assert res["exit_date"] == dt.date(2023, 1, 5)  # the 111 bar, not the 120 EOD


def test_long_stop_still_works():
    entry_date = dt.date(2023, 1, 2)
    df = _df([96.0, 92.0, 89.0], entry_date)  # long stop = 90; 89 breaches
    res = exit_hybrid_50pct(df, entry_date, 100.0, "long", atr=1.0)
    assert res["exit_reason"] == "stop_loss"
    assert res["exit_price"] == pytest.approx(90.0, abs=0.01)


# Parity: scalar vs vectorized hybrid must be byte-identical. The pre-B1320
# coverage gap (no losing-short case tested) is exactly what let the missing
# short stop hide in BOTH paths. These lock the fixed parity.
_PARITY_CASES = [
    ("short", [104.0, 108.0, 111.0, 120.0]),   # losing short -> stop
    ("short", [98.0, 95.0, 96.0, 99.0]),       # short dips then recovers
    ("long",  [96.0, 92.0, 89.0]),             # losing long -> stop
    ("long",  [103.0, 106.0, 104.0, 108.0]),   # long rises
]


@pytest.mark.parametrize("direction,closes", _PARITY_CASES)
def test_scalar_vectorized_hybrid_parity(direction, closes):
    entry_date = dt.date(2023, 1, 2)
    df = _df(closes, entry_date)
    sc = exit_hybrid_50pct(df, entry_date, 100.0, direction, atr=1.0)
    ve = vexit_hybrid_50pct(df, entry_date, 100.0, direction, atr=1.0)
    for k in ("exit_reason", "exit_price", "pnl_pct", "win", "hold_days"):
        assert sc[k] == pytest.approx(ve[k]) if isinstance(sc[k], float) \
            else sc[k] == ve[k], f"{direction} {k}: scalar={sc[k]} vec={ve[k]}"
