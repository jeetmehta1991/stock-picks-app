# Source: B690 revised step 2 (B746) + owner critique "single most likely lookahead vector" + Decision 5 Cat 1 per CHECKLIST #77
"""
cross_sectional_pit_audit.py
============================

PIT-invariance audit for `compute_cross_sectional_features`. Per the B690
sketch review (2026-06-13), cross-sectional rank computation across the
full universe per bar is THE SINGLE MOST LIKELY PLACE in the harness to
introduce lookahead -- output is a number, contamination is invisible.

Adapted directly from `scripts/smc_pit_audit.py` (B735 template) + earnings
PIT auditor pattern (B704). Three hazard probes:

  H1  FUTURE-BAR LEAK -- per-ticker
      Build two ohlcv_dicts: FULL (each ticker has future bars beyond as_of)
      and SLICED (each ticker's data truncated at as_of). Run producer with
      each + assert per-ticker output dicts are bit-identical at as_of.
      Failure = the producer uses future bars somewhere in the rank pipeline.

  H2  UNIVERSE-MEMBERSHIP LEAK
      Add a TICKER to the FULL dict that exists ONLY in bars > as_of (a
      ticker not-yet-IPO'd as of as_of). PIT-honest producer must IGNORE
      that ticker entirely. A non-PIT producer counts it in the universe
      and shifts every other ticker's decile rank.

  H3  CROSS-TICKER ASYMMETRIC SLICE
      One ticker has bars beyond as_of in FULL; one doesn't. The decile of
      the "has-future-bars" ticker must be the SAME whether we run on FULL
      or on the per-ticker-sliced version. Catches the subtle case where
      the producer slices SOME tickers PIT-correctly but not all.

DESIGN
------
The producer takes `(ohlcv_dict, as_of)` and returns `Dict[str, dict]`. The
audit calls it in TWO modes per probe and asserts equality:

  (a) PIT mode: ohlcv_dict has each ticker pre-sliced to <= as_of
  (b) FULL mode: ohlcv_dict has each ticker's full history (incl. future bars)

For each probe + each ticker that appears in BOTH outputs, assert every
emitted signal value is identical. A PIT-honest producer must satisfy this
for every ticker by definition.

USAGE
-----
    from scripts.cross_sectional_pit_audit import audit_all, format_report
    rep = audit_all()
    print(format_report(rep))

The pyramid pin (`test_batch746_cross_sectional_pit_audit.py`) invokes
audit_all() against the LIVE production producer + fails if any case FAILs.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

# Allow direct CLI invocation: ensure repo root is importable
_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


# ----------------------------------------------------------------------------
# Synthetic ohlcv generation
# ----------------------------------------------------------------------------
def _synth_ohlcv(
    seed: int,
    start: str = "2022-01-03",
    n_bars: int = 400,
    drift: float = 0.0005,
    vol: float = 0.012,
) -> pd.DataFrame:
    """Geometric-Brownian-motion price series for one ticker."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, size=n_bars)
    close = 100.0 * np.exp(np.cumsum(rets))
    open_ = np.concatenate([[close[0]], close[:-1]])
    high = np.maximum(open_, close) + np.abs(rng.normal(0, 0.5, size=n_bars))
    low = np.minimum(open_, close) - np.abs(rng.normal(0, 0.5, size=n_bars))
    vol_arr = rng.lognormal(14, 0.3, size=n_bars)
    dates = pd.bdate_range(start, periods=n_bars)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": vol_arr},
        index=dates,
    )


def _slice_dict_to_as_of(ohlcv_dict: dict, as_of: date) -> dict:
    """Return a copy where each ticker's DataFrame is truncated to <= as_of."""
    out = {}
    for ticker, df in ohlcv_dict.items():
        if hasattr(df.index, "date"):
            out[ticker] = df[df.index.date <= as_of]
        else:
            out[ticker] = df[df.index <= as_of]
    return out


# ----------------------------------------------------------------------------
# Case shapes
# ----------------------------------------------------------------------------
@dataclass
class PITCase:
    name: str
    hazard: str  # H1 / H2 / H3
    ohlcv_full: dict  # has future bars beyond as_of
    as_of: date
    expected_tickers: set  # tickers that MUST appear identically in both outputs
    note: str = ""


PASS = "PASS_PIT_CLEAN"
FAIL_LEAK = "FAIL_FUTURE_BARS_LEAKED"
FAIL_UNIVERSE = "FAIL_UNIVERSE_LEAKED"
ERROR = "ERROR"


def build_h1_future_bar_leak() -> PITCase:
    """H1: every ticker has bars beyond as_of in FULL. PIT-honest producer must
    return identical per-ticker outputs in FULL mode vs PIT-sliced mode.
    """
    # 12 synthetic tickers with 400 bars each (covers 252+21 momentum lookback + buffer)
    tickers = [f"T{i:02d}" for i in range(1, 13)] + ["SPY"]
    ohlcv = {t: _synth_ohlcv(seed=hash(t) % (2**31), n_bars=400) for t in tickers}
    # as_of in the middle (~bar 300); so each ticker has ~100 future bars
    as_of = ohlcv["T01"].index[300].date()
    return PITCase(
        "h1_future_bar_leak",
        "H1",
        ohlcv,
        as_of,
        expected_tickers=set(tickers),
        note="every ticker has ~100 bars beyond as_of in FULL mode; PIT-honest must ignore",
    )


def build_h2_universe_membership_leak() -> PITCase:
    """H2: one ticker exists ONLY in bars > as_of (e.g., a not-yet-IPO'd name).
    PIT-honest producer must NOT include it in the universe at all -- so it
    must NOT appear in the FULL-mode output (since SLICED-mode obviously won't
    have it either).
    """
    tickers = [f"T{i:02d}" for i in range(1, 13)] + ["SPY"]
    ohlcv = {t: _synth_ohlcv(seed=hash(t) % (2**31), n_bars=400) for t in tickers}
    as_of = ohlcv["T01"].index[280].date()
    # Add a NEW ticker that exists ONLY post-as_of (the future-IPO case)
    future_ipo = _synth_ohlcv(seed=99, n_bars=400)
    # Shift its index forward by 320 bars so its EARLIEST bar is past as_of
    new_dates = pd.bdate_range(start=ohlcv["T01"].index[330], periods=400)
    future_ipo.index = new_dates
    ohlcv["IPO_NEW"] = future_ipo
    return PITCase(
        "h2_universe_membership_leak",
        "H2",
        ohlcv,
        as_of,
        expected_tickers=set(tickers),  # IPO_NEW excluded -- PIT-honest must drop it
        note="IPO_NEW exists ONLY in bars > as_of; PIT-honest universe must exclude it",
    )


def build_h3_asymmetric_slice() -> PITCase:
    """H3: half the tickers have future bars, half don't. Tests whether the
    producer's per-ticker PIT slicing is symmetric across the universe (i.e.,
    no early-return path that conditionally skips slicing for some tickers).
    """
    half = [f"T{i:02d}" for i in range(1, 7)]
    full_history_only = [f"T{i:02d}" for i in range(7, 13)] + ["SPY"]
    ohlcv = {t: _synth_ohlcv(seed=hash(t) % (2**31), n_bars=400) for t in half + full_history_only}
    as_of = ohlcv["T01"].index[290].date()
    # Truncate the "no-future-bars" half BEFORE building FULL
    for t in full_history_only:
        ohlcv[t] = ohlcv[t][ohlcv[t].index.date <= as_of]
    return PITCase(
        "h3_asymmetric_slice",
        "H3",
        ohlcv,
        as_of,
        expected_tickers=set(half + full_history_only),
        note="half the tickers have future bars; per-ticker PIT slicing must be symmetric",
    )


CASE_BUILDERS = {
    "h1_future_bar_leak":           build_h1_future_bar_leak,
    "h2_universe_membership_leak":  build_h2_universe_membership_leak,
    "h3_asymmetric_slice":          build_h3_asymmetric_slice,
}


# ----------------------------------------------------------------------------
# Result types
# ----------------------------------------------------------------------------
@dataclass
class TickerDiff:
    ticker: str
    key: str
    got_full: object
    got_sliced: object


@dataclass
class CaseResult:
    case_name: str
    hazard: str
    verdict: str
    n_tickers_compared: int = 0
    diffs: list = field(default_factory=list)         # list[TickerDiff]
    universe_leaks: list = field(default_factory=list)  # tickers in FULL but not expected
    note: str = ""


# ----------------------------------------------------------------------------
# Core audit
# ----------------------------------------------------------------------------
def audit_producer(producer_fn: Callable, case: PITCase) -> CaseResult:
    """Run producer in FULL mode and PIT mode; compare per-ticker outputs.

    producer_fn(ohlcv_dict, as_of) -> Dict[str, dict]
    """
    try:
        ohlcv_sliced = _slice_dict_to_as_of(case.ohlcv_full, case.as_of)
        out_full = producer_fn(case.ohlcv_full, case.as_of)
        out_sliced = producer_fn(ohlcv_sliced, case.as_of)
    except Exception as e:
        return CaseResult(case.name, case.hazard, ERROR, note=f"producer error: {e!r}")

    if not isinstance(out_full, dict) or not isinstance(out_sliced, dict):
        return CaseResult(case.name, case.hazard, ERROR, note="non-dict return")

    # H2: universe-leak check -- tickers in FULL output beyond expected set
    universe_leaks = [t for t in out_full.keys() if t not in case.expected_tickers]
    diffs: list[TickerDiff] = []

    # Per-ticker FULL vs SLICED comparison
    common = set(out_full.keys()) & set(out_sliced.keys())
    n_compared = 0
    for t in common:
        if t not in case.expected_tickers:
            continue
        n_compared += 1
        d_full = out_full[t]
        d_sliced = out_sliced[t]
        if not isinstance(d_full, dict) or not isinstance(d_sliced, dict):
            continue
        all_keys = set(d_full.keys()) | set(d_sliced.keys())
        for key in all_keys:
            v_full = d_full.get(key, "<missing>")
            v_sliced = d_sliced.get(key, "<missing>")
            if not _values_equal(v_full, v_sliced):
                diffs.append(TickerDiff(t, key, v_full, v_sliced))

    # Verdict resolution
    if universe_leaks:
        verdict = FAIL_UNIVERSE
        note = f"universe leak: tickers in FULL output that should not be in PIT universe: {universe_leaks[:5]}"
    elif diffs:
        verdict = FAIL_LEAK
        note = f"{len(diffs)} per-ticker value diffs between FULL and PIT-sliced mode"
    else:
        verdict = PASS
        note = f"FULL and PIT-sliced outputs identical for {n_compared} tickers"

    return CaseResult(
        case.name, case.hazard, verdict, n_compared, diffs, universe_leaks, note
    )


def _values_equal(a, b, tol: float = 1e-9) -> bool:
    """Robust equality: floats within tol; rest by ==."""
    if isinstance(a, float) and isinstance(b, float):
        if np.isnan(a) and np.isnan(b):
            return True
        return abs(a - b) <= tol
    return a == b


def audit_all(producer_fn: Callable | None = None) -> list:
    """Run all cases against `producer_fn` (defaults to live production)."""
    if producer_fn is None:
        from backtest.signals.cross_sectional import compute_cross_sectional_features
        producer_fn = compute_cross_sectional_features
    return [audit_producer(producer_fn, b()) for b in CASE_BUILDERS.values()]


def format_report(results: list) -> str:
    L = ["CROSS-SECTIONAL PIT-INVARIANCE AUDIT"]
    L.append("")
    for r in results:
        tag = "[PASS]" if r.verdict == PASS else "[FAIL]"
        L.append(f"{tag} [{r.hazard}] {r.case_name} -> {r.verdict}")
        L.append(f"    n_tickers_compared={r.n_tickers_compared}")
        L.append(f"    note: {r.note}")
        if r.universe_leaks:
            L.append(f"    universe_leaks: {r.universe_leaks[:5]}")
        if r.diffs:
            for d in r.diffs[:5]:
                L.append(f"    diff: ticker={d.ticker} key={d.key} full={d.got_full!r} sliced={d.got_sliced!r}")
            if len(r.diffs) > 5:
                L.append(f"    ... and {len(r.diffs) - 5} more diffs")
        L.append("")
    return "\n".join(L)


if __name__ == "__main__":  # pragma: no cover
    results = audit_all()
    print(format_report(results))
    n_fail = sum(1 for r in results if r.verdict != PASS)
    import sys
    sys.exit(0 if n_fail == 0 else 1)
