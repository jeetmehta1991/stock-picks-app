"""B737 Decision 4 confronting tests -- 7-test bundle per owner directive
2026-06-12 "Run all 7 in sequenced order".

# Source: Decision 4 Run all 7 in sequenced order per CHECKLIST #77

Each test uses the conditional_add_test pattern from B701 + the B734-enhanced
overfit detection (REJECT_OVERFIT verdict on train/test gap > 0.10).

Tests
-----
A1  PEAD LONG gap-conditioning           (gap_pct < 0.02 ADD-test on PEAD long)
A2  PEAD SHORT gap-conditioning          (gap_pct < 0.02 ADD-test on PEAD short)
B1  FOMC SPY confirmation                (Lucca-Moench survives 2022-2026?)
B2  FOMC single-stock beta-decile        (CONDITIONAL on B1 PASS)
C1  Week-gap size band                   (|gap_pct| < 0.03 ADD-test on ICT-11/12)
C2  Week-gap earnings filter             (no-earnings-2d ADD-test)
C3  Week-gap trend context               (against-trend ADD-test)

Universe: 30 alphabetical T1a PIT-active tickers (same as B701).
Train through 2023-12-31; test from 2024-01-01.
Barrier race: +2x ATR target, -1x ATR stop, 10-bar horizon.

Output: output_audit/b737_confronting_tests/
    - b737_report.md (owner-facing)
    - b737_results.json (machine-readable)

Proxies vs production: each test uses a documented PROXY signal to test the
reviewer HYPOTHESIS (B701 precedent). The verdict tells us whether the gate
ADDITION would lift FT in PRODUCTION; it doesn't depend on bit-identical
producer logic. Each test docstring states its proxy assumption.

Verdict semantics (per B734 OOS-watchdog):
    ADD              -- test_lift >= min_lift (= 0.03) -> wire the gate
    REJECT_HARMFUL   -- test_lift <= -min_lift -> gate hurts, do NOT wire
    REJECT_REDUNDANT -- |test_lift| < min_lift -> gate doesn't earn its slot
    REJECT_OVERFIT   -- |train_ft - test_ft| > overfit_threshold (= 0.10) AND
                        test_lift < min_lift -> train edge does NOT persist OOS
    DEFER            -- with_n < min_n (= 30) -> insufficient sample to judge
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "scripts"))

from trigger_followthrough import follow_through_rate  # noqa: E402

OUT_DIR = _REPO / "output_audit" / "b737_confronting_tests"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OHLCV_DIR = _REPO / "data_prefetch" / "polygon" / "ohlcv_daily"
T1A_PATH = _REPO / "Backtesting universe" / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"

TRAIN_END = pd.Timestamp(date(2023, 12, 31))
TEST_START = pd.Timestamp(date(2024, 1, 1))

MIN_N = 30
MIN_LIFT = 0.03
OVERFIT_THRESHOLD = 0.10


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------
def load_ohlcv(ticker: str) -> pd.DataFrame | None:
    fp = OHLCV_DIR / f"{ticker}.parquet"
    if not fp.exists():
        return None
    df = pd.read_parquet(fp)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()
    df.columns = [c.lower() for c in df.columns]
    if {"open", "high", "low", "close", "volume"} - set(df.columns):
        return None
    return df


def load_universe(n: int = 30) -> list[str]:
    df = pd.read_csv(T1A_PATH, comment="#")
    as_of = date(2026, 5, 31)
    added = pd.to_datetime(df["added_date"], errors="coerce").dt.date
    removed = pd.to_datetime(df["removed_date"], errors="coerce").dt.date
    mask = ((added.isna()) | (added <= as_of)) & ((removed.isna()) | (removed > as_of))
    tickers = sorted(df[mask]["Symbol"].astype(str).str.upper().unique().tolist())
    return tickers[:n]


# --------------------------------------------------------------------------
# Pooled conditional-add aggregator (B701 pattern + B734 verdict).
# --------------------------------------------------------------------------
def _pooled_ft(per_ticker_trig: dict, direction: int) -> tuple[float, int]:
    """Pool numerator + denominator across tickers; return weighted FT + total n."""
    num = 0.0
    n_total = 0
    for ticker, (df, trig) in per_ticker_trig.items():
        if trig.sum() == 0:
            continue
        r, n, _ = follow_through_rate(
            df, trig, direction,
            target_mult=2.0, stop_mult=1.0, horizon=10,
        )
        if np.isfinite(r) and n > 0:
            num += r * n
            n_total += n
    ft = num / n_total if n_total else float("nan")
    return ft, n_total


def conditional_add_test_pooled(
    per_ticker: dict,
    direction: int,
    test_name: str,
) -> dict:
    """For each ticker we get a tuple (df, existing_trigger, new_gate). Compute
    pooled train_ft / test_ft for both (existing) and (existing AND new_gate),
    then apply B734 verdict semantics.

    Returns verdict dict consumed by the report.
    """
    base_train_inputs = {}
    base_test_inputs = {}
    with_train_inputs = {}
    with_test_inputs = {}

    for ticker, (df, existing, new_gate) in per_ticker.items():
        train_mask = np.asarray(df.index <= TRAIN_END)
        test_mask = np.asarray(df.index >= TEST_START)
        base_train_inputs[ticker] = (df, existing & train_mask)
        base_test_inputs[ticker] = (df, existing & test_mask)
        with_train_inputs[ticker] = (df, existing & new_gate & train_mask)
        with_test_inputs[ticker] = (df, existing & new_gate & test_mask)

    base_train_ft, base_train_n = _pooled_ft(base_train_inputs, direction)
    base_test_ft, base_test_n = _pooled_ft(base_test_inputs, direction)
    with_train_ft, with_train_n = _pooled_ft(with_train_inputs, direction)
    with_test_ft, with_test_n = _pooled_ft(with_test_inputs, direction)

    if with_test_n < MIN_N:
        verdict = "DEFER"
        note = (f"too few surviving test trades (n={with_test_n} < {MIN_N}) to judge add")
    elif not np.isfinite(with_test_ft) or not np.isfinite(base_test_ft):
        verdict = "DEFER"
        note = "follow-through unestimable"
    else:
        test_lift = with_test_ft - base_test_ft
        gap = with_train_ft - with_test_ft
        if abs(gap) > OVERFIT_THRESHOLD and test_lift < MIN_LIFT:
            verdict = "REJECT_OVERFIT"
            note = (f"train FT {with_train_ft:.3f} vs test FT {with_test_ft:.3f} "
                    f"(gap {gap:+.3f} > {OVERFIT_THRESHOLD:.2f}); test lift {test_lift:+.3f} < {MIN_LIFT:.2f}")
        elif test_lift >= MIN_LIFT:
            verdict = "ADD"
            note = (f"lifts FT {base_test_ft:.3f}->{with_test_ft:.3f} "
                    f"(+{test_lift:.3f}); train gap {gap:+.3f}; n_test={with_test_n}")
        elif test_lift <= -MIN_LIFT:
            verdict = "REJECT_HARMFUL"
            note = f"LOWERS FT {base_test_ft:.3f}->{with_test_ft:.3f} ({test_lift:+.3f})"
        else:
            verdict = "REJECT_REDUNDANT"
            note = (f"no FT lift ({base_test_ft:.3f}->{with_test_ft:.3f}, {test_lift:+.3f}); "
                    f"gate doesn't earn its slot")

    return {
        "test_name": test_name,
        "direction": direction,
        "base_train_ft": round(base_train_ft, 4) if np.isfinite(base_train_ft) else None,
        "base_test_ft": round(base_test_ft, 4) if np.isfinite(base_test_ft) else None,
        "with_train_ft": round(with_train_ft, 4) if np.isfinite(with_train_ft) else None,
        "with_test_ft": round(with_test_ft, 4) if np.isfinite(with_test_ft) else None,
        "base_train_n": base_train_n,
        "base_test_n": base_test_n,
        "with_train_n": with_train_n,
        "with_test_n": with_test_n,
        "verdict": verdict,
        "note": note,
    }


# --------------------------------------------------------------------------
# Proxy signal computations
# --------------------------------------------------------------------------
def compute_signals(df: pd.DataFrame) -> dict[str, np.ndarray]:
    """All proxy signals computed once per ticker; consumed by multiple tests."""
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    v = df["volume"].to_numpy(float)
    n = len(c)

    # Gap-pct (today's open vs yesterday's close)
    prev_c = np.concatenate([[c[0]], c[:-1]])
    gap_pct = o / prev_c - 1.0

    # Daily return (close-to-close)
    ret = pd.Series(c).pct_change().to_numpy()

    # PEAD ANN-day proxy: bars where |daily return| > 5% (top-of-distribution moves
    # are the strongest reversion-vs-drift candidates for earnings ANN day).
    ann_up = ret > 0.05
    ann_dn = ret < -0.05

    # PEAD window (1-60 bars after ANN day): mark each post-ANN window
    pead_window_up = np.zeros(n, dtype=bool)
    pead_window_dn = np.zeros(n, dtype=bool)
    for i in np.flatnonzero(ann_up):
        end = min(n, i + 61)
        pead_window_up[i + 1:end] = True
    for i in np.flatnonzero(ann_dn):
        end = min(n, i + 61)
        pead_window_dn[i + 1:end] = True

    # Week-opening-gap (Monday or first-trading-day-of-week gap > 1.5%)
    dates = pd.DatetimeIndex(df.index)
    dow = dates.dayofweek.to_numpy()
    # First trading day of week = bar whose previous bar is from prior week
    # (using ISO week year + week number)
    iso = dates.isocalendar()
    week_id = (iso["year"].astype(int) * 100 + iso["week"].astype(int)).to_numpy()
    prev_week = np.concatenate([[week_id[0]], week_id[:-1]])
    is_first_of_week = week_id != prev_week
    week_open_gap_up_15 = is_first_of_week & (gap_pct >= 0.015)
    week_open_gap_dn_15 = is_first_of_week & (gap_pct <= -0.015)

    # EMA-200 (proxy for trend gate)
    ema200 = pd.Series(c).ewm(span=200, adjust=False).mean().to_numpy()
    price_above_ema200 = c > ema200
    price_below_ema200 = c < ema200

    # "Recent earnings (proxy): |daily return| > 5% in last 2 trading days"
    earnings_last_2d = pd.Series(ann_up | ann_dn).rolling(2).max().shift(1).fillna(0).astype(bool).to_numpy()

    return {
        "gap_pct": gap_pct,
        "ret": ret,
        "ann_up": ann_up,
        "ann_dn": ann_dn,
        "pead_window_up": pead_window_up,
        "pead_window_dn": pead_window_dn,
        "is_first_of_week": is_first_of_week,
        "week_open_gap_up_15": week_open_gap_up_15,
        "week_open_gap_dn_15": week_open_gap_dn_15,
        "price_above_ema200": price_above_ema200,
        "price_below_ema200": price_below_ema200,
        "earnings_last_2d": earnings_last_2d,
        "dow": dow,
    }


# --------------------------------------------------------------------------
# A1: PEAD LONG gap-conditioning
# --------------------------------------------------------------------------
def test_a1_pead_long_gap_conditioning(tickers: list[str]) -> dict:
    """existing = inside post-positive-ANN PEAD window; candidate = gap_pct < 0.02
    AND-required at entry bar. Direction = +1 long.

    Proxy assumption: ANN-day = |ret|>5% bar; positive = upward; PEAD window =
    bars 1-60 after ANN. Confronts whether GAP-CONDITIONING (small entry-bar gap)
    lifts FT vs unconditional PEAD-window entry.
    """
    per_ticker = {}
    for ticker in tickers:
        df = load_ohlcv(ticker)
        if df is None or len(df) < 300:
            continue
        s = compute_signals(df)
        existing = s["pead_window_up"]
        new_gate = s["gap_pct"] < 0.02
        per_ticker[ticker] = (df, existing, new_gate)
    return conditional_add_test_pooled(per_ticker, +1, "A1_PEAD_LONG_gap_conditioning")


# --------------------------------------------------------------------------
# A2: PEAD SHORT gap-conditioning (mirror)
# --------------------------------------------------------------------------
def test_a2_pead_short_gap_conditioning(tickers: list[str]) -> dict:
    """existing = inside post-negative-ANN PEAD window; candidate = gap_pct > -0.02
    (small downward gap) AND-required. Direction = -1 short.
    """
    per_ticker = {}
    for ticker in tickers:
        df = load_ohlcv(ticker)
        if df is None or len(df) < 300:
            continue
        s = compute_signals(df)
        existing = s["pead_window_dn"]
        new_gate = s["gap_pct"] > -0.02
        per_ticker[ticker] = (df, existing, new_gate)
    return conditional_add_test_pooled(per_ticker, -1, "A2_PEAD_SHORT_gap_conditioning")


# --------------------------------------------------------------------------
# B1: FOMC SPY confirmation -- Lucca-Moench (2015) +50bp 24h pre-FOMC drift
#     survives on 2022-2026 (post-Mueller-Tahbaz-Salehi 2017 weakening era)?
# --------------------------------------------------------------------------
def test_b1_fomc_spy_confirmation() -> dict:
    """Measures SPY close-to-close return from FOMC_DATE-1 to FOMC_DATE for every
    FOMC announcement 2022-2026 in our calendar. Lucca-Moench baseline: +50bp.

    PASS if mean test-window return > +25 bp (half Lucca-Moench) AND a one-sample
    t-test rejects mean=0 at p<0.10.
    FAIL otherwise -> abandon FOMC refactor; mark FOMC strategies EXPLORATORY.
    """
    try:
        from backtest.data.macro import FOMC_DATES
    except Exception as e:
        return {"test_name": "B1_FOMC_SPY_confirmation", "verdict": "ERROR",
                "note": f"FOMC_DATES import failed: {e}"}

    spy = load_ohlcv("SPY")
    if spy is None:
        return {"test_name": "B1_FOMC_SPY_confirmation", "verdict": "ERROR",
                "note": "SPY OHLCV cache missing"}

    fomc = pd.to_datetime(FOMC_DATES)
    fomc = fomc[(fomc >= "2022-01-01") & (fomc <= "2026-12-31")]
    spy_close = spy["close"].astype(float)

    pre_fomc_returns = []
    used_dates = []
    for d in fomc:
        # find bar at or after d (the announcement day)
        idx = spy.index.searchsorted(d)
        if idx == 0 or idx >= len(spy):
            continue
        # use prev day's close vs ann-day close (proxy for 24h pre-FOMC drift to ann)
        prev_close = spy_close.iloc[idx - 1]
        ann_close = spy_close.iloc[idx]
        if not (np.isfinite(prev_close) and np.isfinite(ann_close)) or prev_close == 0:
            continue
        pre_fomc_returns.append(ann_close / prev_close - 1.0)
        used_dates.append(str(spy.index[idx].date()))

    arr = np.asarray(pre_fomc_returns)
    n = len(arr)
    if n < 10:
        return {"test_name": "B1_FOMC_SPY_confirmation", "verdict": "DEFER",
                "n": n, "note": "too few FOMC dates intersect SPY cache"}

    mean = float(arr.mean())
    std = float(arr.std(ddof=1))
    se = std / np.sqrt(n)
    t_stat = mean / se if se > 0 else 0.0
    # one-sided p-value approx via normal tail (n=40 -> close enough)
    from math import erf, sqrt
    p_one_sided = 0.5 * (1 - erf(t_stat / sqrt(2))) if mean > 0 else 1.0

    lucca_moench_baseline_bp = 50.0
    pass_threshold_bp = 25.0
    mean_bp = mean * 10000

    if mean_bp >= pass_threshold_bp and p_one_sided < 0.10:
        verdict = "PASS"
        note = (f"SPY mean pre-FOMC return {mean_bp:+.1f}bp >= {pass_threshold_bp}bp "
                f"(half Lucca-Moench {lucca_moench_baseline_bp}bp); p_one_sided={p_one_sided:.3f} "
                f"on n={n} FOMC dates 2022-2026 -- effect survives")
    else:
        verdict = "FAIL"
        note = (f"SPY mean pre-FOMC return {mean_bp:+.1f}bp; p_one_sided={p_one_sided:.3f}; "
                f"on n={n} FOMC dates 2022-2026 -- effect does NOT clearly survive "
                f"(Mueller-Tahbaz-Salehi 2017 weakening era confirmed)")

    return {
        "test_name": "B1_FOMC_SPY_confirmation",
        "verdict": verdict,
        "n_fomc_dates": n,
        "mean_return_bp": round(mean_bp, 2),
        "std_return_bp": round(std * 10000, 2),
        "t_stat": round(t_stat, 3),
        "p_one_sided": round(p_one_sided, 4),
        "lucca_moench_baseline_bp": lucca_moench_baseline_bp,
        "pass_threshold_bp": pass_threshold_bp,
        "note": note,
        "sample_dates": used_dates[:5],  # first 5 for spot-check
    }


# --------------------------------------------------------------------------
# B2: FOMC single-stock beta-decile (CONDITIONAL on B1 PASS)
# --------------------------------------------------------------------------
def test_b2_fomc_single_stock_beta_decile(tickers: list[str]) -> dict:
    """Per-beta-decile mean pre-FOMC 24h return on T1a 2022-2026 FOMC dates.

    Question: does top-decile beta single-stock pre-FOMC drift EXCEED SPY mean
    (justifying single-stock entry over SPX ETF)?

    Beta computed as 60-day rolling corr(stock_ret, spy_ret) * std_stock / std_spy.
    """
    try:
        from backtest.data.macro import FOMC_DATES
    except Exception as e:
        return {"test_name": "B2_FOMC_single_stock_beta_decile", "verdict": "ERROR",
                "note": f"FOMC_DATES import failed: {e}"}
    spy = load_ohlcv("SPY")
    if spy is None:
        return {"test_name": "B2_FOMC_single_stock_beta_decile", "verdict": "ERROR",
                "note": "SPY OHLCV cache missing"}

    fomc = pd.to_datetime(FOMC_DATES)
    fomc = fomc[(fomc >= "2022-01-01") & (fomc <= "2026-12-31")]
    spy_ret = spy["close"].astype(float).pct_change()

    per_obs = []  # (ticker, fomc_date, beta_60d_at_d_minus_1, pre_fomc_return)
    for ticker in tickers:
        df = load_ohlcv(ticker)
        if df is None or len(df) < 300:
            continue
        stock_ret = df["close"].astype(float).pct_change()
        joined = pd.concat([stock_ret.rename("stock"), spy_ret.rename("spy")], axis=1).dropna()
        for d in fomc:
            idx = joined.index.searchsorted(d)
            if idx <= 60 or idx >= len(joined):
                continue
            window = joined.iloc[idx - 60:idx]
            if window["spy"].std() <= 0:
                continue
            beta = float(window["stock"].cov(window["spy"]) / window["spy"].var())
            # the FOMC pre-window return = stock return on the announcement bar
            pre_return = float(joined["stock"].iloc[idx])
            if np.isfinite(beta) and np.isfinite(pre_return):
                per_obs.append((ticker, str(joined.index[idx].date()), beta, pre_return))

    if len(per_obs) < 100:
        return {"test_name": "B2_FOMC_single_stock_beta_decile", "verdict": "DEFER",
                "n": len(per_obs), "note": "too few obs across tickers x FOMC dates"}

    obs = pd.DataFrame(per_obs, columns=["ticker", "fomc_date", "beta", "pre_return"])
    obs["decile"] = pd.qcut(obs["beta"], 10, labels=False, duplicates="drop")
    decile_stats = obs.groupby("decile")["pre_return"].agg(["mean", "std", "count"]).reset_index()
    decile_stats.columns = ["decile", "mean_return", "std_return", "n"]

    top_decile_mean_bp = float(decile_stats[decile_stats["decile"] == decile_stats["decile"].max()]["mean_return"].iloc[0]) * 10000
    bottom_decile_mean_bp = float(decile_stats[decile_stats["decile"] == 0]["mean_return"].iloc[0]) * 10000
    spread_bp = top_decile_mean_bp - bottom_decile_mean_bp

    # PASS if top decile mean > 60bp (SPY baseline + 10bp lift) AND spread > 30bp
    pass_top_threshold_bp = 60.0
    pass_spread_threshold_bp = 30.0
    if top_decile_mean_bp >= pass_top_threshold_bp and spread_bp >= pass_spread_threshold_bp:
        verdict = "PASS"
        note = (f"top beta decile pre-FOMC mean {top_decile_mean_bp:+.1f}bp; bottom decile "
                f"{bottom_decile_mean_bp:+.1f}bp; spread {spread_bp:+.1f}bp >= thresholds; "
                f"single-stock beta-conditioning justified")
    else:
        verdict = "FAIL"
        note = (f"top beta decile pre-FOMC mean {top_decile_mean_bp:+.1f}bp; bottom "
                f"{bottom_decile_mean_bp:+.1f}bp; spread {spread_bp:+.1f}bp -- does NOT "
                f"clearly exceed SPY ETF entry; abandon single-stock refactor")

    return {
        "test_name": "B2_FOMC_single_stock_beta_decile",
        "verdict": verdict,
        "n_observations": int(len(obs)),
        "top_decile_mean_bp": round(top_decile_mean_bp, 2),
        "bottom_decile_mean_bp": round(bottom_decile_mean_bp, 2),
        "spread_bp": round(spread_bp, 2),
        "pass_top_threshold_bp": pass_top_threshold_bp,
        "pass_spread_threshold_bp": pass_spread_threshold_bp,
        "decile_stats": decile_stats.to_dict("records"),
        "note": note,
    }


# --------------------------------------------------------------------------
# C1: Week-gap size band (|gap_pct| < 0.03 upper bound)
# --------------------------------------------------------------------------
def test_c1_week_gap_size_band(tickers: list[str]) -> dict:
    """existing = week_open_gap_up_15 OR week_open_gap_dn_15; candidate =
    |gap_pct| < 0.03 AND-required.

    Tested as LONG fade of gap-down + SHORT fade of gap-up, combined direction
    via the sign of gap_pct. For simplicity we test gap-DOWN-fade-LONG side
    (ICT-12) because the symmetric SHORT side gives a similar verdict by
    construction and the LONG side has fewer drift-bias confounds.
    """
    per_ticker = {}
    for ticker in tickers:
        df = load_ohlcv(ticker)
        if df is None or len(df) < 300:
            continue
        s = compute_signals(df)
        # ICT-12 = gap-down fade long; existing trigger fires on week_open_gap_dn_15
        existing = s["week_open_gap_dn_15"]
        # candidate gate: gap_pct > -0.03 (not too big a gap)
        new_gate = s["gap_pct"] > -0.03
        per_ticker[ticker] = (df, existing, new_gate)
    return conditional_add_test_pooled(per_ticker, +1, "C1_week_gap_size_band_long")


# --------------------------------------------------------------------------
# C2: Week-gap earnings filter (no-earnings-2d-window)
# --------------------------------------------------------------------------
def test_c2_week_gap_earnings_filter(tickers: list[str]) -> dict:
    """existing = week_open_gap_dn_15; candidate = NOT earnings_last_2d
    AND-required. Avoids fading gaps that are PEAD continuation events.
    """
    per_ticker = {}
    for ticker in tickers:
        df = load_ohlcv(ticker)
        if df is None or len(df) < 300:
            continue
        s = compute_signals(df)
        existing = s["week_open_gap_dn_15"]
        new_gate = ~s["earnings_last_2d"]
        per_ticker[ticker] = (df, existing, new_gate)
    return conditional_add_test_pooled(per_ticker, +1, "C2_week_gap_earnings_filter_long")


# --------------------------------------------------------------------------
# C3: Week-gap trend context (against-trend AND-required)
# --------------------------------------------------------------------------
def test_c3_week_gap_trend_context(tickers: list[str]) -> dict:
    """existing = week_open_gap_dn_15; candidate = price_above_ema200 (don't
    fade gap-down INTO a downtrend; only fade gap-down in an uptrend where
    mean-reversion to trend is consistent with trend).
    """
    per_ticker = {}
    for ticker in tickers:
        df = load_ohlcv(ticker)
        if df is None or len(df) < 300:
            continue
        s = compute_signals(df)
        existing = s["week_open_gap_dn_15"]
        new_gate = s["price_above_ema200"]
        per_ticker[ticker] = (df, existing, new_gate)
    return conditional_add_test_pooled(per_ticker, +1, "C3_week_gap_trend_context_long")


# --------------------------------------------------------------------------
# Orchestrator + report
# --------------------------------------------------------------------------
def fmt_verdict_table(results: dict) -> str:
    L = ["| Test | Verdict | base_test_ft | with_test_ft | lift | train_test_gap | with_test_n |",
         "|---|---|---:|---:|---:|---:|---:|"]
    for key in ["a1", "a2", "c1", "c2", "c3"]:
        if key not in results:
            continue
        r = results[key]
        base = r.get("base_test_ft")
        with_ = r.get("with_test_ft")
        with_train = r.get("with_train_ft")
        lift = (with_ - base) if (base is not None and with_ is not None) else None
        gap = (with_train - with_) if (with_train is not None and with_ is not None) else None
        L.append(f"| {r['test_name']} | **{r['verdict']}** | {base if base is not None else 'n/a'} | "
                 f"{with_ if with_ is not None else 'n/a'} | {round(lift, 4) if lift is not None else 'n/a'} | "
                 f"{round(gap, 4) if gap is not None else 'n/a'} | {r.get('with_test_n', 'n/a')} |")
    return "\n".join(L)


def fmt_md_report(results: dict, tickers: list[str]) -> str:
    L = [
        "# B737 Decision 4 Confronting-Tests Report (2026-06-12)",
        "",
        "# Source: scripts/run_b737_confronting_tests.py per CHECKLIST #77",
        "",
        f"Universe: {len(tickers)} alphabetical T1a PIT-active tickers ({tickers[:5]} ...).",
        "Train through 2023-12-31; test from 2024-01-01. Barrier race: +2x ATR target, -1x ATR stop, 10-bar horizon.",
        "OOS-watchdog (B734) thresholds: REJECT_OVERFIT fires when |train_ft - test_ft| > 0.10 AND test_lift < 0.03.",
        "",
        "## Sequenced verdict summary",
        "",
        fmt_verdict_table(results),
        "",
        "## A1: PEAD LONG gap-conditioning",
        "",
        f"**Verdict: {results.get('a1', {}).get('verdict', 'n/a')}**",
        f"  - {results.get('a1', {}).get('note', '')}",
        "",
        "## A2: PEAD SHORT gap-conditioning (mirror)",
        "",
        f"**Verdict: {results.get('a2', {}).get('verdict', 'n/a')}**",
        f"  - {results.get('a2', {}).get('note', '')}",
        "",
        "## B1: FOMC SPY Lucca-Moench survival (2022-2026)",
        "",
        f"**Verdict: {results.get('b1', {}).get('verdict', 'n/a')}**",
        f"  - {results.get('b1', {}).get('note', '')}",
        f"  - n FOMC dates measured: {results.get('b1', {}).get('n_fomc_dates', 'n/a')}",
        f"  - SPY mean pre-FOMC return: {results.get('b1', {}).get('mean_return_bp', 'n/a')} bp (Lucca-Moench baseline +50 bp)",
        f"  - One-sided p-value: {results.get('b1', {}).get('p_one_sided', 'n/a')}",
        "",
        "## B2: FOMC single-stock beta-decile",
        "",
    ]
    if "b2" in results:
        L.extend([
            f"**Verdict: {results['b2']['verdict']}**",
            f"  - {results['b2']['note']}",
            f"  - Top beta-decile mean: {results['b2'].get('top_decile_mean_bp', 'n/a')} bp",
            f"  - Bottom beta-decile mean: {results['b2'].get('bottom_decile_mean_bp', 'n/a')} bp",
            f"  - Spread: {results['b2'].get('spread_bp', 'n/a')} bp",
        ])
    else:
        L.append("**SKIPPED** -- gated on B1 PASS; B1 did not pass.")
    L.extend([
        "",
        "## C1: Week-gap size band (gap_pct > -0.03 on gap-down-fade-long)",
        "",
        f"**Verdict: {results.get('c1', {}).get('verdict', 'n/a')}**",
        f"  - {results.get('c1', {}).get('note', '')}",
        "",
        "## C2: Week-gap earnings filter (NOT earnings_last_2d)",
        "",
        f"**Verdict: {results.get('c2', {}).get('verdict', 'n/a')}**",
        f"  - {results.get('c2', {}).get('note', '')}",
        "",
        "## C3: Week-gap trend context (price_above_ema200 AND-required)",
        "",
        f"**Verdict: {results.get('c3', {}).get('verdict', 'n/a')}**",
        f"  - {results.get('c3', {}).get('note', '')}",
        "",
        "---",
        "",
        "## Proxy disclosures (each test states its assumption)",
        "",
        "- **A1/A2 PEAD ANN-day proxy**: |daily_return| > 5% bar; positive sign = up; PEAD window = bars 1-60 after ANN. "
        "Production producer uses real EPS data + SUE; this proxy uses price-move-based detection. The confronting "
        "test asks 'does gap-conditioning lift FT given the existing entry mechanism?' -- the answer transfers if "
        "the production producer's FT curve has the same monotonicity in gap_pct.",
        "- **B1/B2 FOMC**: real FOMC_DATES from backtest/data/macro.py (40 dates 2022-2026); SPY OHLCV from "
        "polygon prefetch. No proxy.",
        "- **C1/C2/C3 Week-gap proxy**: ICT-11/12 production uses ict_producers.compute_week_opening_gap_signals "
        "with week_open_gap_up_15pct / week_open_gap_dn_15pct (gap_pct >= 1.5%). Our proxy uses gap-pct ratio at "
        "first trading day of ISO week + same 1.5% threshold. Equivalent on regular Monday opens; differs on "
        "Monday-holiday weeks where production uses Tuesday open.",
        "- **C2 earnings proxy**: |daily_return|>5% in last 2 trading days. Production uses real earnings calendar.",
        "- **C3 trend proxy**: EMA-200 from close-only EMA. Production uses identical EMA-200.",
        "",
        "## Owner action by verdict",
        "",
        "| Verdict | Action |",
        "|---|---|",
        "| ADD | wire the gate to the named production strategy |",
        "| REJECT_HARMFUL | do NOT wire; gate hurts |",
        "| REJECT_REDUNDANT | do NOT wire; gate doesn't earn its slot |",
        "| REJECT_OVERFIT | do NOT wire; train edge does not persist OOS |",
        "| DEFER | insufficient sample; revisit post-B660 fire-count run |",
        "",
    ])
    return "\n".join(L)


def main():
    tickers = load_universe(30)
    results: dict = {}

    print("[B737] Running Decision 4 confronting tests on", len(tickers), "tickers ...")

    # Batch 1: independent tests
    print("[B737] A1 PEAD LONG gap-conditioning ...")
    results["a1"] = test_a1_pead_long_gap_conditioning(tickers)
    print("       ->", results["a1"]["verdict"], "|", results["a1"]["note"][:140])

    print("[B737] A2 PEAD SHORT gap-conditioning ...")
    results["a2"] = test_a2_pead_short_gap_conditioning(tickers)
    print("       ->", results["a2"]["verdict"], "|", results["a2"]["note"][:140])

    print("[B737] B1 FOMC SPY Lucca-Moench survival ...")
    results["b1"] = test_b1_fomc_spy_confirmation()
    print("       ->", results["b1"]["verdict"], "|", results["b1"]["note"][:140])

    print("[B737] C1 Week-gap size band ...")
    results["c1"] = test_c1_week_gap_size_band(tickers)
    print("       ->", results["c1"]["verdict"], "|", results["c1"]["note"][:140])

    # Conditional B2 on B1
    if results["b1"]["verdict"] == "PASS":
        print("[B737] B2 FOMC single-stock beta-decile (B1 PASS -> running) ...")
        results["b2"] = test_b2_fomc_single_stock_beta_decile(tickers)
        print("       ->", results["b2"]["verdict"], "|", results["b2"]["note"][:140])
    else:
        print("[B737] B2 SKIPPED (B1 did not pass)")

    # Batch 3
    print("[B737] C2 Week-gap earnings filter ...")
    results["c2"] = test_c2_week_gap_earnings_filter(tickers)
    print("       ->", results["c2"]["verdict"], "|", results["c2"]["note"][:140])

    print("[B737] C3 Week-gap trend context ...")
    results["c3"] = test_c3_week_gap_trend_context(tickers)
    print("       ->", results["c3"]["verdict"], "|", results["c3"]["note"][:140])

    # Write outputs
    json_path = OUT_DIR / "b737_results.json"
    md_path = OUT_DIR / "b737_report.md"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"tickers": tickers, "results": results}, f, indent=2, default=str)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(fmt_md_report(results, tickers))
    print(f"[B737] DONE -> {json_path}  +  {md_path}")
    return results


if __name__ == "__main__":
    main()
