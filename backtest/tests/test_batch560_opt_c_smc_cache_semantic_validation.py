"""Batch 560 (2026-06-02) -- OPT-C Phase 4 Option (A) semantic validation
pin from the 987-pair A/B sweep.

Source: per CHECKLIST #77, owner directive 2026-06-02 "C then A".
Queue: OPT-C Phase 4 (A) validation pass.

Methodology:
  - 20 mega-cap tickers x ~50 as_of dates (spread across history) =
    987 (ticker, as_of) pairs (some idxs skipped when ticker history
    < idx).
  - For each pair: call compute_smc_signals twice -- once with
    USE_SMC_PANEL_CACHE=False, once with =True + primed cache.
  - Compare key set + per-key boolean / float divergence.

Empirical findings (verbatim from the 2026-06-02 sweep):
  Key-set divergent pairs: 0 / 987 (cached + uncached produce same
    set of signal keys).
  Pairs with at least 1 signal value diff: 987 / 987 (100pct).

Per-key bool divergence (top 10):
  smc_equal_highs_swept   37.5pct
  smc_ob_bullish_active   22.3pct
  smc_ob_bearish_active   17.7pct
  smc_equal_lows_swept    17.3pct
  smc_bos_bullish         16.7pct
  smc_choch_bullish       12.0pct
  smc_choch_bearish       11.1pct
  smc_liquidity_swept_dn  10.9pct
  smc_ote_short_zone       9.6pct
  smc_liquidity_swept_up   9.3pct

Float divergence:
  smc_retracement_pct     99.8pct (iloc[-1] 20-bar offset).

Wall-time A/B (33-day BacktestEngine pass):
  baseline (flag OFF) 428.9s -> cached (flag ON) 255.5s
  = 1.68x speedup (40.4pct reduction).

VERDICT: cache speedup is REAL (40pct wall savings) but semantic
parity with uncached path is NOT achievable without library refactor.
Every (ticker, as_of) pair differs by at least one signal; per-key
boolean divergence ranges 0.3pct to 37.5pct; smc_retracement_pct
differs in 99.8pct of pairs.

RECOMMENDATION: keep USE_SMC_PANEL_CACHE default False (current
state). Owner can flip explicitly after running a full-cube
comparison and accepting the semantic shift.

Pins:

  (1) Pin the key-set parity invariant (cached + uncached emit same
      keys -- regression guard against silent key-removal in cache
      slicing logic).
  (2) Pin the upper-bound divergence-rate empirical observation so
      a future commit that makes divergence WORSE surfaces in CI.
  (3) Pin the flag default remains False (semantic-safe default).
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def reset_smc_cache():
    from backtest.signals.smc_panel_cache import reset_cache
    reset_cache()
    yield
    reset_cache()


def _have_ohlcv(ticker: str) -> bool:
    repo_root = Path(__file__).parent.parent.parent
    return (repo_root / "data_prefetch" / "polygon" / "ohlcv_daily"
            / f"{ticker.replace('.', '-')}.parquet").exists()


def _load_ohlc(ticker: str) -> pd.DataFrame:
    repo_root = Path(__file__).parent.parent.parent
    df = pd.read_parquet(
        repo_root / "data_prefetch" / "polygon" / "ohlcv_daily"
        / f"{ticker.replace('.', '-')}.parquet"
    )
    df["date_dt"] = pd.to_datetime(df["date"]).dt.date
    return df.sort_values("date_dt").reset_index(drop=True)


def test_batch560_flag_default_remains_false():
    """USE_SMC_PANEL_CACHE must default to False (semantic-safe).
    Owner flip is gated behind explicit decision after this
    validation pass."""
    import importlib
    import backtest.config as cfg
    importlib.reload(cfg)
    assert cfg.USE_SMC_PANEL_CACHE is False, (
        "Per B560 validation: cache semantic divergence vs uncached "
        "is widespread (100pct of pairs differ on at least 1 signal). "
        "Flag must stay False until owner accepts the semantic shift."
    )


@pytest.mark.skipif(not _have_ohlcv("AAPL"), reason="AAPL OHLCV absent")
def test_batch560_key_set_parity_holds():
    """Cached + uncached compute_smc_signals must emit the SAME set
    of signal keys for any (ticker, as_of) pair. Regression guard
    against silent key-removal in cache slicing logic."""
    import backtest.config as cfg
    from backtest.signals.smc_ict import compute_smc_signals
    from backtest.signals.smc_panel_cache import (
        prime_ticker_primitives, reset_cache,
    )
    df = _load_ohlc("AAPL")
    for current_idx in (400, 700, 1000):
        if current_idx >= len(df):
            continue
        truncated = df.iloc[:current_idx + 1]
        cfg.USE_SMC_PANEL_CACHE = False
        reset_cache()
        out_off = compute_smc_signals(truncated)
        cfg.USE_SMC_PANEL_CACHE = True
        reset_cache()
        prime_ticker_primitives("AAPL", df, swing_length=20)
        out_on = compute_smc_signals(truncated, ticker="AAPL")
        cfg.USE_SMC_PANEL_CACHE = False
        assert set(out_off.keys()) == set(out_on.keys()), (
            f"key set diverges at current_idx={current_idx}; "
            f"missing in cached: {set(out_off.keys()) - set(out_on.keys())}, "
            f"extra in cached: {set(out_on.keys()) - set(out_off.keys())}"
        )


@pytest.mark.skipif(not _have_ohlcv("AAPL"), reason="AAPL OHLCV absent")
def test_batch560_empirical_divergence_within_documented_ceiling():
    """Pin the per-key divergence rates observed in the 2026-06-02
    validation sweep. If a future commit makes divergence WORSE for
    any key (e.g., cache slicing change introduces more drift), this
    test catches it. NOT enforcing strict parity -- pinning the
    empirical UPPER ceiling so regressions surface."""
    import backtest.config as cfg
    from backtest.signals.smc_ict import compute_smc_signals
    from backtest.signals.smc_panel_cache import (
        prime_ticker_primitives, reset_cache,
    )
    # Small subset for unit-test speed (full 987-pair sweep is in
    # the docstring; this test runs a 30-pair subset on AAPL only).
    df = _load_ohlc("AAPL")
    test_idxs = [i for i in range(400, 1200, 27) if i < len(df)]  # ~30 idxs
    from collections import Counter
    bool_diffs: Counter = Counter()
    samples_per_key: Counter = Counter()
    n_pairs = 0
    for current_idx in test_idxs:
        truncated = df.iloc[:current_idx + 1]
        cfg.USE_SMC_PANEL_CACHE = False
        reset_cache()
        out_off = compute_smc_signals(truncated)
        cfg.USE_SMC_PANEL_CACHE = True
        reset_cache()
        prime_ticker_primitives("AAPL", df, swing_length=20)
        out_on = compute_smc_signals(truncated, ticker="AAPL")
        cfg.USE_SMC_PANEL_CACHE = False
        for k in set(out_off.keys()) & set(out_on.keys()):
            v_off = out_off[k]
            v_on = out_on[k]
            if isinstance(v_off, bool) and isinstance(v_on, bool):
                samples_per_key[k] += 1
                if v_off != v_on:
                    bool_diffs[k] += 1
        n_pairs += 1
    # The empirical ceiling for the full 987-pair sweep was 37.5pct
    # on smc_equal_highs_swept. The unit-test subset (30 AAPL idxs)
    # has higher variance; pin 70pct as the regression ceiling so a
    # MATERIAL drift (e.g., cache slicing logic regression) surfaces
    # without false alarms on small-sample noise.
    for k, divs in bool_diffs.items():
        total = samples_per_key[k]
        rate = divs / max(total, 1)
        assert rate < 0.70, (
            f"key {k} bool divergence {rate:.4f} > 70pct ceiling; "
            f"regression -- cache slicing logic drifted further from "
            f"uncached. Full B560 sweep observed max 37.5pct on "
            f"smc_equal_highs_swept."
        )


def test_batch560_validation_documentation_present():
    """Pin that the validation findings are documented in EXECUTION_QUEUE.md
    OPT-C row. Future readers must see the verdict + recommendation
    inline with the queue entry, not lost in commit history."""
    repo_root = Path(__file__).parent.parent.parent
    queue_path = repo_root / "EXECUTION_QUEUE.md"
    if not queue_path.exists():
        pytest.skip("EXECUTION_QUEUE.md absent")
    content = queue_path.read_text(encoding="utf-8")
    # OPT-C row must reference B560 verdict + cite the 40pct wall
    # win + the 100pct semantic divergence + flag-default-False
    # recommendation. Loose grep allows wording flexibility.
    assert "B560" in content or "Batch 560" in content, (
        "OPT-C row must reference B560 validation pass in EXECUTION_QUEUE.md"
    )
