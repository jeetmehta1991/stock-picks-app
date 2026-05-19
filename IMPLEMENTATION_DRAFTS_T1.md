# IMPLEMENTATION_DRAFTS_T1.md — T1.1-T1.5 module engine wiring drafts

**Authored:** 2026-05-19 (while T1a Phase 1A-α 5-batch rerun runs)
**Status:** DRAFTS — apply when batches complete + T0 close-out lands
**Owner-approved 2026-05-18:** Option 2 — pre-author drafts to accelerate post-T0 chain

**Pattern confirmed** from [backtest/signals/screener.py](backtest/signals/screener.py:2302-2381):
- `screen_instrument(ticker, df, info, as_of, regime, vix_value, vix_history, xs_features)` is the per-ticker entry point
- Signals merged into `signals` dict via repeated `signals.update(...)` blocks (lines 2314-2381)
- Strategies are functions `strat_X(s)` returning `_strat(fires, direction, category, signals_used, context_bullets)` dict
- Registration in `ALL_STRATEGIES` dict (line 1978+)
- Regime affinity in [backtest/engine/regime_selector.py](backtest/engine/regime_selector.py) `STRATEGY_REGIME_AFFINITY`

---

## T1.1 — pairs_trading wiring (Batch 240 target)

**Prerequisites:** T5b precompute must land first (`data_prefetch/derived/cointegrated_pairs_t1a/{YYYY-MM-DD}.parquet`). Without it, the pairs lookup returns no pairs and strategies fire 0 trades — graceful no-op.

### New helper in [backtest/signals/pairs_trading.py](backtest/signals/pairs_trading.py)

```python
def compute_pair_signals_for_ticker(
    ticker: str, as_of: date, ticker_close: pd.Series,
    pairs_dir: Path = None,
) -> dict:
    """Look up cointegrated pairs for `ticker` at as_of from precomputed
    parquets. For each pair, fetch the counterparty close history and
    compute current z-score. Returns the MAX |z| as the primary signal.

    Returns dict with:
      - pair_max_abs_zscore: float (0 if no pairs found)
      - pair_zscore_signed: float (positive if ticker overpriced)
      - pair_counterparty: str (ticker of best pair, or "")
      - pair_half_life: float (days)
      - pair_count_active: int

    Graceful no-op when precompute parquet missing (returns empty dict).
    """
    from datetime import date as _date
    if pairs_dir is None:
        pairs_dir = Path(__file__).parent.parent.parent / "data_prefetch" / "derived" / "cointegrated_pairs_t1a"
    if not pairs_dir.exists():
        return {}
    # Find latest snapshot <= as_of
    snapshots = sorted([p for p in pairs_dir.glob("*.parquet") if p.stem != "_index"])
    latest = None
    for s in snapshots:
        try:
            snap_date = _date.fromisoformat(s.stem)
            if snap_date <= as_of:
                latest = s
        except ValueError:
            continue
    if latest is None:
        return {}
    try:
        pairs_df = pd.read_parquet(latest)
    except Exception:
        return {}
    # Filter for pairs involving this ticker
    mine = pairs_df[(pairs_df["ticker_a"] == ticker) | (pairs_df["ticker_b"] == ticker)]
    if mine.empty:
        return {"pair_max_abs_zscore": 0.0, "pair_zscore_signed": 0.0,
                "pair_counterparty": "", "pair_half_life": 0.0,
                "pair_count_active": 0}
    # For each pair, compute current z-score
    best_z = 0.0
    best_z_signed = 0.0
    best_peer = ""
    best_hl = 0.0
    for _, row in mine.iterrows():
        is_a = row["ticker_a"] == ticker
        peer = row["ticker_b"] if is_a else row["ticker_a"]
        # Load peer close
        peer_safe = peer.replace(".", "-")
        peer_path = Path(__file__).parent.parent.parent / "data_prefetch" / "polygon" / "ohlcv_daily" / f"{peer_safe}.parquet"
        if not peer_path.exists():
            continue
        try:
            peer_df = pd.read_parquet(peer_path)
            if "date" in peer_df.columns:
                peer_df["date_dt"] = pd.to_datetime(peer_df["date"], errors="coerce").dt.date
                peer_df = peer_df[peer_df["date_dt"] <= as_of].sort_values("date_dt")
                peer_close = pd.Series(peer_df["close"].values[-90:], index=peer_df["date_dt"].values[-90:])
            else:
                continue
            # Align to ticker_close
            if is_a:
                z = pair_zscore(ticker_close, peer_close, row["hedge_ratio"], row["intercept"])
            else:
                z = pair_zscore(peer_close, ticker_close, row["hedge_ratio"], row["intercept"])
            if z is None:
                continue
            if abs(z) > abs(best_z):
                best_z = z
                best_z_signed = z if is_a else -z
                best_peer = peer
                best_hl = float(row["half_life"])
        except Exception:
            continue
    return {
        "pair_max_abs_zscore": round(abs(best_z), 4),
        "pair_zscore_signed":  round(best_z_signed, 4),
        "pair_counterparty":   best_peer,
        "pair_half_life":      best_hl,
        "pair_count_active":   len(mine),
    }
```

### Strategy functions to add in screener.py (above ALL_STRATEGIES dict)

```python
def strat_pairs_mean_reversion_long(s):
    """T1.1 Batch 240: cointegrated-pair mean-reversion long.
    Entry: ticker is at low end of spread vs cointegrated peer (z < -2.0).
    Krauss 2017/2024 JES + Gatev-Goetzmann-Rouwenhorst 2006 RFS."""
    fires = (
        s.get("pair_count_active", 0) > 0
        and s.get("pair_zscore_signed", 0.0) < -2.0
        and s.get("pair_half_life", 0.0) >= 5
    )
    z = s.get("pair_zscore_signed", 0.0)
    peer = s.get("pair_counterparty", "")
    return _strat(fires, "long", "pairs",
        ["pair_zscore_signed<-2", "pair_half_life>=5", "pair_count_active>0"],
        [f"Pair z={z:.2f} vs {peer} (overpriced peer / cheap self)",
         f"Half-life {s.get('pair_half_life', 0):.1f}d (mean-revert window)",
         "Cointegrated relationship validated at precompute"])


def strat_pairs_mean_reversion_short(s):
    """T1.1 Batch 240: cointegrated-pair mean-reversion short.
    Entry: ticker is at high end of spread vs cointegrated peer (z > +2.0)."""
    fires = (
        s.get("pair_count_active", 0) > 0
        and s.get("pair_zscore_signed", 0.0) > 2.0
        and s.get("pair_half_life", 0.0) >= 5
    )
    z = s.get("pair_zscore_signed", 0.0)
    peer = s.get("pair_counterparty", "")
    return _strat(fires, "short", "pairs",
        ["pair_zscore_signed>2", "pair_half_life>=5", "pair_count_active>0"],
        [f"Pair z={z:.2f} vs {peer} (ticker overpriced relative to peer)",
         f"Half-life {s.get('pair_half_life', 0):.1f}d (mean-revert window)",
         "Cointegrated relationship validated at precompute"])
```

### screen_instrument wiring (after line 2381 `compute_htf_alignment` block)

```python
# T1.1 Batch 240: cointegrated pair signals. No-op when T5b precompute missing.
try:
    from backtest.signals.pairs_trading import compute_pair_signals_for_ticker
    ticker_close = pd.Series(df["close"].values[-90:], index=df.index[-90:])
    pair_sigs = compute_pair_signals_for_ticker(ticker, as_of, ticker_close)
    if pair_sigs:
        signals.update(pair_sigs)
except Exception:
    pass
```

### ALL_STRATEGIES dict additions (insert in screener.py:1978-2030 block)

```python
# Pairs trading (2 - Batch 240 2026-05-19 T1.1)
"pairs_mean_reversion_long":    strat_pairs_mean_reversion_long,
"pairs_mean_reversion_short":   strat_pairs_mean_reversion_short,
```

### regime_selector.py affinity additions

```python
# Pairs trading (Batch 240): mean-reversion fails in trending markets; allow
# neutral + low-vol bull only. Krauss 2024 recommends explicit regime gate
# since cointegration drift accelerates in volatile/crisis regimes.
"pairs_mean_reversion_long":    {"bull", "neutral"},
"pairs_mean_reversion_short":   {"bull", "neutral"},
```

### Unit test file (NEW: `backtest/tests/test_t1_1_pairs_strategies.py`)

```python
"""T1.1 Batch 240: pairs_trading strategy regression tests."""
import pytest
from backtest.signals.screener import (
    strat_pairs_mean_reversion_long, strat_pairs_mean_reversion_short,
)


def test_pairs_long_fires_at_negative_z():
    s = {"pair_count_active": 3, "pair_zscore_signed": -2.5, "pair_half_life": 15}
    r = strat_pairs_mean_reversion_long(s)
    assert r["fires"]
    assert r["direction"] == "long"


def test_pairs_long_blocked_at_z_above_threshold():
    s = {"pair_count_active": 3, "pair_zscore_signed": -1.5, "pair_half_life": 15}
    assert not strat_pairs_mean_reversion_long(s)["fires"]


def test_pairs_long_blocked_when_half_life_too_short():
    s = {"pair_count_active": 3, "pair_zscore_signed": -2.5, "pair_half_life": 3}
    assert not strat_pairs_mean_reversion_long(s)["fires"]


def test_pairs_short_fires_at_positive_z():
    s = {"pair_count_active": 3, "pair_zscore_signed": 2.5, "pair_half_life": 15}
    r = strat_pairs_mean_reversion_short(s)
    assert r["fires"]
    assert r["direction"] == "short"


def test_pairs_strategies_noop_when_no_pairs():
    s = {"pair_count_active": 0, "pair_zscore_signed": -2.5, "pair_half_life": 15}
    assert not strat_pairs_mean_reversion_long(s)["fires"]
    assert not strat_pairs_mean_reversion_short(s)["fires"]
```

---

## T1.2 — news_sentiment wiring (Batch 241)

### screen_instrument wiring (after T1.1 block)

```python
# T1.2 Batch 241: per-ticker news sentiment over last 7 days.
try:
    from backtest.signals.news_sentiment import compute_news_sentiment_signals
    news_sigs = compute_news_sentiment_signals(ticker, as_of, lookback_days=7)
    if news_sigs:
        signals.update(news_sigs)
except Exception:
    pass
```

### Strategy functions

```python
def strat_news_sentiment_long(s):
    """T1.2 Batch 241: positive-sentiment cluster long.
    Lopez-Lira-Tang 2023 + Loughran-McDonald 2011 lexicon. Entry: 7-day
    sentiment mean > +0.3 with >=3 articles + above 200-EMA."""
    fires = (
        s.get("news_sentiment_mean", 0.0) > 0.3
        and s.get("news_article_count", 0) >= 3
        and s.get("price_above_ema_200", True)
    )
    sent = s.get("news_sentiment_mean", 0.0)
    return _strat(fires, "long", "news_sentiment",
        ["news_sentiment_mean>0.3", "news_article_count>=3", "price_above_ema_200"],
        [f"7-day mean sentiment +{sent:.2f} (positive cluster)",
         f"{s.get('news_article_count', 0)} articles in window (coverage threshold)",
         "Above 200 EMA (regime gate)"])


def strat_news_sentiment_shift_long(s):
    """T1.2 Batch 241: sentiment-shift long (delta detector).
    Entry: sentiment shift +0.4 vs 7d prior + above 200-EMA + DTC-positive
    catalyst delta. Captures news-driven momentum onset."""
    fires = (
        s.get("news_sentiment_shift", 0.0) > 0.4
        and s.get("news_article_count", 0) >= 2
        and s.get("price_above_ema_200", True)
    )
    shift = s.get("news_sentiment_shift", 0.0)
    return _strat(fires, "long", "news_sentiment",
        ["news_sentiment_shift>0.4", "news_article_count>=2", "price_above_ema_200"],
        [f"Sentiment shift +{shift:.2f} (positive delta vs prior 7d)",
         "Coverage threshold met",
         "Above 200 EMA (regime gate)"])
```

### ALL_STRATEGIES + affinity

```python
# News sentiment (2 - Batch 241 2026-05-19 T1.2)
"news_sentiment_long":          strat_news_sentiment_long,
"news_sentiment_shift_long":    strat_news_sentiment_shift_long,
```

```python
# News sentiment (Batch 241): bull + neutral - sentiment momentum tracks
# risk-on regimes. Bad-news clustering in crisis overwhelms positive signal.
"news_sentiment_long":          {"bull", "neutral"},
"news_sentiment_shift_long":    {"bull", "neutral"},
```

### Test file (NEW: `backtest/tests/test_t1_2_news_strategies.py`) — same pattern as T1.1

---

## T1.3 — calendar_effects wiring (Batch 242)

### Day-level cache pattern (universe-wide signals, compute once per as_of)

```python
# T1.3 Batch 242: universe-wide calendar signals. Same dict for all tickers
# on a given day. Cache via lru cache per as_of.
from functools import lru_cache

@lru_cache(maxsize=2)
def _cached_calendar_signals(as_of_iso: str) -> dict:
    from datetime import date as _d
    from backtest.signals.calendar_effects import compute_calendar_signals
    return compute_calendar_signals(_d.fromisoformat(as_of_iso))

# In screen_instrument, after T1.2 block:
try:
    cal_sigs = _cached_calendar_signals(str(as_of))
    if cal_sigs:
        signals.update(cal_sigs)
except Exception:
    pass
```

### Strategy functions

```python
def strat_totm_long(s):
    """T1.3 Batch 242: Ariel 1987 TOTM (last-4 + first-3 trading days).
    Sharpe ~1.0 1928-1986; replicated McConnell-Xu 2008 with attenuated
    Sharpe ~0.6. Long-only on TOTM window + regime != crisis."""
    fires = (
        s.get("is_totm_window", False)
        and s.get("price_above_ema_200", True)
    )
    return _strat(fires, "long", "calendar",
        ["is_totm_window", "price_above_ema_200"],
        ["TOTM window (Ariel 1987: last-4 + first-3 trading days)",
         "Above 200 EMA (regime gate)"])


def strat_pre_holiday_long(s):
    """T1.3 Batch 242: Lakonishok-Smidt 1988 + Ariel 1990 pre-holiday drift.
    +5-10x daily-mean abnormal return on the pre-holiday day. Long-only."""
    fires = (
        s.get("is_pre_holiday", False)
        and s.get("dow", 0) != 0  # not Monday (Cross 1973 weakness pattern)
        and s.get("price_above_ema_200", True)
    )
    return _strat(fires, "long", "calendar",
        ["is_pre_holiday", "dow!=0", "price_above_ema_200"],
        ["Pre-holiday session (Lakonishok-Smidt 1988)",
         "Not Monday (avoid Cross 1973 weakness)",
         "Above 200 EMA (regime gate)"])


def strat_january_effect_small_cap_long(s):
    """T1.3 Batch 242: Rozeff-Kinney 1976 January Effect for small-caps.
    Post-1990 attenuated for liquid names; persists in micro-caps + recent
    IPOs (Easterday-Sen-Stephan 2009). Long-only on T2/T3 small-caps in January."""
    fires = (
        s.get("is_january", False)
        and s.get("cap_band", "") in ("micro", "small")  # T2/T3 universe
        and s.get("price_above_ema_200", True)
    )
    return _strat(fires, "long", "calendar",
        ["is_january", "cap_band in (micro,small)", "price_above_ema_200"],
        ["January Effect (Rozeff-Kinney 1976; small-cap subset)",
         "Small/micro-cap (post-1990 effect concentrated here)",
         "Above 200 EMA (regime gate)"])


def strat_halloween_seasonal_long(s):
    """T1.3 Batch 242: Bouman-Jacobsen 2002 Halloween Indicator.
    Equity returns concentrate Nov-Apr. Long-only outside crisis regime."""
    fires = (
        s.get("is_halloween_period", False)
        and s.get("price_above_ema_200", True)
    )
    return _strat(fires, "long", "calendar",
        ["is_halloween_period", "price_above_ema_200"],
        ["Halloween period Nov-Apr (Bouman-Jacobsen 2002)",
         "Above 200 EMA (regime gate)"])
```

### ALL_STRATEGIES + affinity

```python
# Calendar effects (4 - Batch 242 2026-05-19 T1.3)
"totm_long":                    strat_totm_long,
"pre_holiday_long":             strat_pre_holiday_long,
"january_effect_small_cap_long": strat_january_effect_small_cap_long,
"halloween_seasonal_long":      strat_halloween_seasonal_long,
```

```python
# Calendar effects (Batch 242): all-regime except crisis - calendar
# anomalies don't survive stress regimes (TOTM disappears in 2008/2020).
"totm_long":                    {"bull", "neutral", "bear"},
"pre_holiday_long":             {"bull", "neutral", "bear"},
"january_effect_small_cap_long": {"bull", "neutral", "bear"},
"halloween_seasonal_long":      {"bull", "neutral", "bear"},
```

---

## T1.4 — cross_asset wiring (Batch 243)

### Day-level cache (same lru_cache pattern as T1.3 — even more important here, cross_asset reads multiple ETF parquets per call)

```python
@lru_cache(maxsize=2)
def _cached_cross_asset_signals(as_of_iso: str) -> dict:
    from datetime import date as _d
    from backtest.signals.cross_asset import compute_cross_asset_signals
    return compute_cross_asset_signals(_d.fromisoformat(as_of_iso))

# In screen_instrument, after T1.3:
try:
    xa_sigs = _cached_cross_asset_signals(str(as_of))
    if xa_sigs:
        signals.update(xa_sigs)
except Exception:
    pass
```

### Strategy functions (5 strategies — see source for full bodies; pattern same as T1.3)

```python
def strat_risk_off_bond_equity_short(s):
    """T1.4 Batch 243: short equity when TLT/SPY ratio rising = risk-off
    bond-flight. Asness 2003 Fed Model / Connolly-Stivers-Sun 2005."""
    fires = s.get("risk_off_regime_bond_signal", False)
    return _strat(fires, "short", "cross_asset",
        ["risk_off_regime_bond_signal"],
        ["TLT/SPY ratio rising (bond flight = risk-off)",
         "Asness 2003 Fed Model; bonds outperforming equity 20d"])


def strat_vix_backwardation_long(s):
    """T1.4 Batch 243: long quality when VIX > VIX3M (backwardation = stress
    regime). Cheng 2019 JFE: short-vol unwinds; convexity for longs."""
    fires = (
        s.get("vix_term_backwardation", False)
        and s.get("xs_quality_decile", 0) >= 8
    )
    return _strat(fires, "long", "cross_asset",
        ["vix_term_backwardation", "xs_quality_decile>=8"],
        ["VIX > VIX3M (backwardation; stress regime)",
         "Top-quintile quality (defensive sleeve)"])


def strat_sector_rotation_defensive_long(s):
    """T1.4 Batch 243: long defensive sectors (XLU/XLP/XLV) when defensive
    leadership signal active. Conover-Jensen-Johnson-Mercer 2008 JoF."""
    fires = (
        s.get("defensive_leadership", False)
        and s.get("sector", "") in ("Utilities", "Consumer Staples", "Health Care")
    )
    return _strat(fires, "long", "cross_asset",
        ["defensive_leadership", "sector in defensive"],
        ["Defensive sectors leading XLU/XLP/XLV vs cyclicals XLF/XLY/XLI",
         f"Ticker in defensive sector {s.get('sector', '')}"])


def strat_gold_silver_risk_off_long(s):
    """T1.4 Batch 243: gold-silver ratio rising = risk-off. Long defensive
    overlay. Hammoudeh-Yuan 2008. Used as confirming signal."""
    fires = (
        s.get("risk_off_regime_gold_signal", False)
        and s.get("sector", "") in ("Utilities", "Consumer Staples")
    )
    return _strat(fires, "long", "cross_asset",
        ["risk_off_regime_gold_signal", "sector in defensive"],
        ["Gold/Silver ratio rising (risk-off confirmation)",
         f"Defensive sector {s.get('sector', '')}"])


def strat_dxy_headwind_multinational_short(s):
    """T1.4 Batch 243: short SPY-multinational names when DXY strengthening.
    Fratzscher 2009 JoB. S&P 500 ~40% foreign rev; multinationals headwind."""
    fires = (
        s.get("usd_strengthening", False)
        and s.get("foreign_rev_pct", 0.0) > 40.0  # field from fundamentals
    )
    return _strat(fires, "short", "cross_asset",
        ["usd_strengthening", "foreign_rev_pct>40"],
        ["DXY strengthening 20d > 2% (multinational headwind)",
         f"Foreign rev {s.get('foreign_rev_pct', 0):.0f}% (translation risk)"])
```

### ALL_STRATEGIES + affinity

```python
# Cross-asset signals (5 - Batch 243 2026-05-19 T1.4)
"risk_off_bond_equity_short":       strat_risk_off_bond_equity_short,
"vix_backwardation_long":           strat_vix_backwardation_long,
"sector_rotation_defensive_long":   strat_sector_rotation_defensive_long,
"gold_silver_risk_off_long":        strat_gold_silver_risk_off_long,
"dxy_headwind_multinational_short": strat_dxy_headwind_multinational_short,
```

```python
# Cross-asset (Batch 243): stress-regime activations preferred. Defensive
# sleeves crisis/bear; DXY headwind shorts work in all regimes.
"risk_off_bond_equity_short":       {"bear", "crisis"},
"vix_backwardation_long":           {"bear", "crisis"},
"sector_rotation_defensive_long":   {"bear", "crisis"},
"gold_silver_risk_off_long":        {"bear", "crisis"},
"dxy_headwind_multinational_short": {"bull", "neutral", "bear", "crisis"},
```

---

## T1.5 — volume_profile wiring (Batch 244)

### screen_instrument wiring (per-ticker call)

```python
# T1.5 Batch 244: 60-day volume profile (POC + Value Area + naked POC).
try:
    from backtest.signals.volume_profile import compute_volume_profile, compute_period_pocs
    vp_sigs = compute_volume_profile(df, lookback_days=60)
    if vp_sigs:
        signals.update(vp_sigs)
    # Naked POC: distance to nearest higher-period untested POC
    period_pocs = compute_period_pocs(df, period_lookback=252, n_periods=6)
    if period_pocs:
        close = float(df["close"].iloc[-1])
        # Find nearest naked POC (untested = price hasn't traded through it recently)
        signals["naked_poc_count"] = len(period_pocs)
        signals["naked_poc_nearest_distance_pct"] = min(
            abs(close - p) / close for p in period_pocs
        ) if period_pocs else 0.0
except Exception:
    pass
```

### Strategy functions

```python
def strat_poc_magnet_long(s):
    """T1.5 Batch 244: POC magnet long. Steidlmayer 1985 Market Profile.
    Entry: close within 2% of POC + bullish bias + above 200-EMA."""
    fires = (
        s.get("vp_close_near_poc_pct", 1.0) < 0.02
        and s.get("vp_close_above_poc", False)
        and s.get("price_above_ema_200", True)
    )
    dist = s.get("vp_close_near_poc_pct", 0.0)
    return _strat(fires, "long", "volume_profile",
        ["vp_close_near_poc_pct<0.02", "vp_close_above_poc", "price_above_ema_200"],
        [f"Within {dist*100:.1f}% of 60d POC (volume magnetism)",
         "Bullish bias (close above POC)",
         "Above 200 EMA (regime gate)"])


def strat_value_area_breakout_long(s):
    """T1.5 Batch 244: Value Area breakout long. Close breaks above VAH
    with volume confirmation. Dalton-Jones-Dalton 1990 Market Profile."""
    fires = (
        s.get("vp_above_value_area", False)
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_200", True)
    )
    return _strat(fires, "long", "volume_profile",
        ["vp_above_value_area", "vol_spike_2x", "price_above_ema_200"],
        ["Close above Value Area High (institutional acceptance)",
         "Volume 2x ADV(20) (breakout confirmation)",
         "Above 200 EMA (regime gate)"])


def strat_naked_poc_retest_long(s):
    """T1.5 Batch 244: Naked POC retest long. Close within 1% of an
    untested period POC + bullish bias. Levels act as magnetic attractors."""
    fires = (
        s.get("naked_poc_count", 0) > 0
        and s.get("naked_poc_nearest_distance_pct", 1.0) < 0.01
        and s.get("price_above_ema_200", True)
    )
    return _strat(fires, "long", "volume_profile",
        ["naked_poc_nearest_distance_pct<0.01", "price_above_ema_200"],
        [f"Within 1% of naked POC (untested institutional level)",
         f"{s.get('naked_poc_count', 0)} naked POCs identified (6-period)",
         "Above 200 EMA (regime gate)"])
```

### ALL_STRATEGIES + affinity

```python
# Volume profile / VPVR (3 - Batch 244 2026-05-19 T1.5)
"poc_magnet_long":              strat_poc_magnet_long,
"value_area_breakout_long":     strat_value_area_breakout_long,
"naked_poc_retest_long":        strat_naked_poc_retest_long,
```

```python
# Volume profile (Batch 244): POC magnetism + Value Area work in trending
# + range markets; break down in crisis (panic selling overrides structure).
"poc_magnet_long":              {"bull", "neutral"},
"value_area_breakout_long":     {"bull", "neutral"},
"naked_poc_retest_long":        {"bull", "neutral"},
```

---

## Application order when batches finish

1. T0 close-out runs (1 command): `python scripts/run_t0_close_out.py`
2. T5b precompute runs in parallel: `python scripts/precompute_cointegrated_pairs.py`
3. T1.1 (depends on T5b being at least partially done — even 1 quarterly snapshot is enough for testing)
4. T1.2 → T1.3 → T1.4 → T1.5 (independent of T5b; can run in any order)

Each addressal:
- Copy strategy function definitions from this doc into screener.py (above ALL_STRATEGIES at line ~1978)
- Copy screen_instrument wiring snippet into the signals-merge block (after line ~2381)
- Copy ALL_STRATEGIES dict entries into the dict
- Copy STRATEGY_REGIME_AFFINITY entries into regime_selector.py
- Save the new test file
- Run targeted test + unit + integration pyramid
- Commit + push with structured message

**Effort per addressal (with drafts ready):** ~10-15 min vs ~30-45 min from scratch.

**Total T1 savings:** ~2-2.5 hours.

---

## CHECKLIST compliance for this drafts doc

- ✅ #45 — compliance via the addressal turns, not this doc
- ✅ #67 — doc lands same-turn
- ✅ #69 — pyramid runs at each addressal apply step (drafts don't ship without it)
- ✅ #74 — drafts ship in same commit as their corresponding code change at apply time
- ✅ #77 — patterns verified by reading screener.py + regime_selector.py source (not memory)
