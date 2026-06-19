"""B921 (2026-06-19): Canonical signal-loader module per Council 39 engine path unification.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.9.1 (engine path unification) +
# Council 39 verdict (single highest-leverage fix) + Council 40 (Class 2 autonomous
# Phase P0 Item 1) per owner directive 2026-06-19 ("proceed autonomously. Ensure
# discipline. Council this.").

PURPOSE
-------
Two engine paths consumed TIER 2 producers divergently pre-B921:

  Path A (canonical):  backtest.py -> screen_instrument()
                       Calls institutional_signal() + 8 other TIER 2 producers
                       inline at screener.py:7962-8050. This path is what R4
                       (May 31 2026) executed.

  Path B (diagnostic): scripts/measure_fire_count.py
                       Skips TIER 2 producers entirely per B689 scope deferral
                       (lines 443-448). This is why B913/B917/B919 micropilots
                       returned 0 fires for ~44 TIER 2-dependent strategies
                       regardless of strategy logic OR the B918 bug fix.

This module extracts TIER 2 signal computation into reusable functions both
paths import + delegate to. Engine path parity becomes a pytest assertion.

B921 SCOPE (Council 40 Class 2 autonomous; commit 1 of 5):
- Extract ONLY institutional_signal injection (screener.py lines 7962-7985)
- Add inject_institutional_signals() called by both engines (next commit wires
  measure_fire_count.py to opt-in via --include-tier2 flag)
- Remaining TIER 2 producers (pead / short_interest / insider_buying /
  classification_change / yoy_surprise / persistence / recent_8k /
  congressional / news_sentiment / sec_edgar) extracted in subsequent commits
  per `feedback_narrow_scope_blast_radius` (LOCAL changes default; one
  producer at a time)

VERIFICATION
------------
backtest/tests/test_engine_parity_tier2.py asserts inject_institutional_signals
produces identical dict output on a fixed 5-ticker x 20-date fixture when
called from either path. Any divergence = parity test FAIL = pre-commit hook
blocks commit.

PRIOR ART
---------
- screener.py:7962-7985 institutional_signal injection (B330 wired; B918
  fixed `new_pos` -> `new_positions` typo 2026-06-19)
- smart_money.py:institutional_signal() producer (2-source bulk + per-ticker
  fallback per B294 / BUG-273)
"""
from __future__ import annotations

import logging
from datetime import date
from typing import Any

logger = logging.getLogger(__name__)


def _log_silent_producer_failure(producer_name: str, exc: BaseException) -> None:
    """Mirror screener.py's silent-failure logging.

    Rate-limited per producer to avoid log spam when a producer is broken on
    a non-T1a ticker etc. Logs at WARNING (not DEBUG) per L143 + B273 lesson
    (silent producer failures at DEBUG level caused 29,159 trades / 0
    classification_* keys / 0 visible errors on AWS post-run).
    """
    logger.warning(
        "signal_loader: %s failed for input: %s",
        producer_name, type(exc).__name__,
    )


def inject_earnings_surprise_yoy_signals(
    signals: dict[str, Any],
    ticker: str,
    df: Any,
    as_of: date,
) -> dict[str, Any]:
    """Inject YoY earnings surprise signals (Batch 507 M6 Path-2 sleeves).

    B928 (2026-06-19) P0 commit 7/11: extracted from screener.py:7916-7922
    (Batch 507 wiring). Council 43 sequence; additive on PEAD per Foster-
    Olsen-Shevlin 1984. Same df-requirement signature as PEAD producer.

    Produces signal keys:
        yoy_surprise_high       bool (yoy_growth >= +5%; owner-tunable)
        yoy_surprise_negative   bool (yoy_growth <= -5%)

    Failure mode: producer raises -> log at WARNING + leave signals
    unchanged. Reads same Polygon financials as PEAD (chained
    dependency).
    """
    try:
        from backtest.signals.earnings_surprise_yoy import compute_yoy_surprise_signal
        yoy_signal = compute_yoy_surprise_signal(ticker, df, as_of)
        if yoy_signal:
            signals.update(yoy_signal)
    except Exception as _e:
        _log_silent_producer_failure("earnings_surprise_yoy", _e)
    return signals


def inject_pead_signals(
    signals: dict[str, Any],
    ticker: str,
    df: Any,
    as_of: date,
) -> dict[str, Any]:
    """Inject Post-Earnings Announcement Drift (PEAD) signals.

    B927 (2026-06-19) P0 commit 6/11: extracted from screener.py:7904-7910
    (Batch 209 wiring per Bernard-Thomas 1989 PEAD effect). Council 43
    sequence "boring first / risky last"; pead is first in remaining 6
    extractions because it has lowest data-source SPOF risk + ~4 strategies
    consume.

    Note: pead producer requires ohlcv_df (different signature from
    institutional/insider/classification). Caller must pass the per-ticker
    OHLCV DataFrame.

    Produces signal keys (all optional; absent when data missing):
        days_since_last_earnings        int
        within_pead_window              bool (days_since <= 60)
        earnings_eps_yoy_growth         float
        earnings_announcement_return    float
        pead_positive_surprise          bool (yoy>0 AND ann_return>+2%)
        pead_negative_surprise          bool (yoy<0 AND ann_return<0)

    Failure mode: producer raises -> log at WARNING + leave signals
    unchanged. Reads `data_prefetch/polygon/financials/` per-ticker
    parquet (B295 fix: financials_json string handling).
    """
    try:
        from backtest.signals.pead import compute_pead_signals
        pead = compute_pead_signals(ticker, df, as_of)
        if pead:
            signals.update(pead)
    except Exception as _e:
        _log_silent_producer_failure("pead", _e)
    return signals


def inject_classification_change_signals(
    signals: dict[str, Any],
    ticker: str,
    as_of: date,
) -> dict[str, Any]:
    """Inject GICS classification-change signals into per-ticker signals dict.

    B924 (2026-06-19) P0 commit 4/5: extracted from screener.py:7952-7961
    (Batch 332 wiring). Council 41 sequence; ~10 strategies consume the
    classification_change_* keys.

    Produces signal keys (per backtest.data.universe.get_classification_change_signals):
        classification_changed_recent       bool (within 90-day lookback)
        days_since_classification_change    int  (None if no change)
        classification_change_to_tech       bool (moved INTO IT/Comms/Health)
        classification_change_to_defensive  bool (moved INTO defensive)
        classification_change_from_tech     bool (moved OUT OF growth)

    Reads sector_history.csv via universe.get_classification_change_signals.
    Failure mode: producer raises -> log at WARNING + leave signals
    unchanged. Per B416 / B910 sector_history staleness lineage: producer
    output may be empty if sector_history.csv stale (1190+ days since
    last event per B910 finding).
    """
    try:
        from backtest.data.universe import get_classification_change_signals
        cc_out = get_classification_change_signals(ticker, as_of)
        if cc_out:
            signals.update(cc_out)
    except Exception as _e:
        _log_silent_producer_failure("classification_change", _e)
    return signals


def inject_insider_buying_signals(
    signals: dict[str, Any],
    ticker: str,
    as_of: date,
) -> dict[str, Any]:
    """Inject Form-4 insider buying cluster signals into per-ticker signals dict.

    B923 (2026-06-19) P0 commit 3/5: extracted from screener.py:7941-7947
    (Batch 222 wiring). Council 41 sequence; highest-leverage extraction
    after institutional_signal because ~10 strategies consume the keys
    `insider_cluster_active` + `insider_director_buyers_30d` +
    `insider_officer_buyers_30d`.

    Produces signal keys:
        insider_cluster_active              bool (>=2 unique insiders bought
                                            open-market in last 30 days)
        insider_unique_buyers_30d           int  (count of unique insiders)
        insider_total_shares_bought_30d     float (sum of Shares)
        insider_director_buyers_30d         int  (subset isDirector=True)
        insider_officer_buyers_30d          int  (subset isOfficer=True)

    Failure mode: producer raises -> log at WARNING + leave signals dict
    unchanged. Strategy gates default False via s.get(key, False).

    PIT semantics: insider_cluster_signals applies 30-day rolling lookback
    from as_of. Producer is per-(ticker, as_of) pure.
    """
    try:
        from backtest.signals.insider_buying import compute_insider_cluster_signals
        insider = compute_insider_cluster_signals(ticker, as_of)
        if insider:
            signals.update(insider)
    except Exception as _e:
        _log_silent_producer_failure("insider_buying", _e)
    return signals


def inject_institutional_signals(
    signals: dict[str, Any],
    ticker: str,
    as_of: date,
) -> dict[str, Any]:
    """Inject 13F institutional signals into per-ticker signals dict.

    Mirrors the institutional_signal block at screener.py:7962-7985
    (post-B918 fix). Mutates + returns signals dict for caller convenience.

    Produces signal keys (consumed by 7+ strategies per CLAUDE.md
    Wave-3 13F roster):
        institutional_signal           str: "none" / "buy" / "strong_buy" / "negative"
        institutional_strong_buy       bool
        institutional_buy              bool   (True for buy OR strong_buy)
        institutional_negative         bool
        institutional_new_positions    int    (count of new Quiver positions; B918 fix)
        institutional_increased        int    (count of positions increased >= threshold)

    Failure mode: producer raises -> log at WARNING + leave signals dict
    unchanged (no defaults injected). Downstream strategy gates default
    to False via s.get(key, False) pattern + return non-firing.

    PIT semantics: institutional_signal() applies 45-day reporting lag
    (DEC-325). signals dict is per-bar; this function is pure with respect
    to (ticker, as_of) inputs.
    """
    try:
        from backtest.data.smart_money import institutional_signal
        inst = institutional_signal(ticker, as_of)
        if inst and isinstance(inst, dict):
            sig_kind = inst.get("signal", "none")
            signals["institutional_signal"] = sig_kind
            signals["institutional_strong_buy"] = sig_kind == "strong_buy"
            signals["institutional_buy"] = sig_kind in ("buy", "strong_buy")
            signals["institutional_negative"] = sig_kind == "negative"
            # B918 (2026-06-19) bug fix carried forward: producer returns
            # 'new_positions' (plural); 'new_pos' (singular) key never existed
            # -> default 0 silenced 7 strategies from 2026-05-25 to 2026-06-19
            # incl. R4 (May 31). Owner-approved (a) fix.
            signals["institutional_new_positions"] = int(inst.get("new_positions", 0) or 0)
            signals["institutional_increased"] = int(inst.get("increased", 0) or 0)
    except Exception as _e:
        _log_silent_producer_failure("institutional_signal", _e)
    return signals
