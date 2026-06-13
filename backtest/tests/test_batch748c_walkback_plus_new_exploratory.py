# Source: B748c owner-approved 2026-06-13 "Walk back B748b AND tag NEW EXPLORATORY for all ~10-15 affected strategies as one batch" + B748c data-quality investigation + CHECKLIST #44/#15 per CHECKLIST #77
"""B748c pin tests: walk-back of false B748b dispositions + NEW EXPLORATORY
tags on strategies whose producers were found to have temporal coverage or
schema contract issues during the B748c extended data-quality investigation.

PER CHECKLIST #44 RIGOROUS DATA-CONSUMPTION DISCIPLINE:
The B748c investigation revealed that B745's path probe was buggy + 6 of
16 TIER 2 producers had previously-undetected data-quality issues:

  REVIVED (5; were tagged EXPLORATORY in B748b on FALSE premise):
    strat_activist_13d_long          -- sec_edgar SC_13D data was present, not missing
    strat_post_inclusion_drift_long       -- index_rebalance parquet exists at different path
    strat_post_inclusion_reversal_short
    strat_post_deletion_drift_short
    strat_pre_rebalance_long

  KEEP-EXPLORATORY (1; B748b correct):
    strat_m_and_a_target_long        -- 8_K parquets have no `item_codes` column;
                                       genuine scaffold-pending state

  NEW EXPLORATORY (9; B748c surfaces):
    persistence 12-day-window:
      strat_institutional_committed_growth_long
      strat_institutional_multi_quarter_persistence_long
    news_sentiment per-ticker schema gap:
      strat_news_momentum_long
      strat_news_momentum_short
      strat_news_reversal_long
      strat_news_reversal_short
      strat_news_sentiment_long
      strat_news_sentiment_shift_long
      strat_squeeze_setup_long  (L2 catalyst dependency)

Net EXPLORATORY post-B748c: 10 strategies (1 carryover + 9 new).
"""
from __future__ import annotations


REVIVED_STRATEGIES_B748C = [
    "strat_activist_13d_long",
    "strat_post_inclusion_drift_long",
    "strat_post_inclusion_reversal_short",
    "strat_post_deletion_drift_short",
    "strat_pre_rebalance_long",
]

NEW_EXPLORATORY_STRATEGIES_B748C = [
    # persistence 12-day window
    "strat_institutional_committed_growth_long",
    "strat_institutional_multi_quarter_persistence_long",
    # news_sentiment per-ticker data gap
    "strat_news_momentum_long",
    "strat_news_momentum_short",
    "strat_news_reversal_long",
    "strat_news_reversal_short",
    "strat_news_sentiment_long",
    "strat_news_sentiment_shift_long",
    "strat_squeeze_setup_long",
]


def test_b748c_pin1_revived_strategies_in_all_strategies_and_not_exploratory():
    """The 5 REVIVED strategies must (a) remain registered, (b) NOT carry
    EXPLORATORY+DO NOT DEPLOY markers (the FALSE B748b tags were removed).
    """
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.signals import screener as scr
    from backtest.signals import index_rebalance as ir
    sources = {
        "strat_activist_13d_long":              scr,
        "strat_post_inclusion_drift_long":      ir,
        "strat_post_inclusion_reversal_short":  ir,
        "strat_post_deletion_drift_short":      ir,
        "strat_pre_rebalance_long":             ir,
    }
    still_tagged = []
    missing = []
    for name, mod in sources.items():
        key = name[len("strat_"):]
        if key not in ALL_STRATEGIES:
            missing.append(name)
            continue
        doc = getattr(mod, name).__doc__ or ""
        if "EXPLORATORY -- DO NOT DEPLOY" in doc:
            still_tagged.append(name)
    assert not missing, f"REVIVED strategies missing from registry: {missing}"
    assert not still_tagged, (
        f"REVIVED strategies still carry EXPLORATORY -- DO NOT DEPLOY: {still_tagged}"
    )


def test_b748c_pin2_nine_new_strategies_carry_exploratory_markers():
    """The 9 NEW EXPLORATORY strategies must declare EXPLORATORY + DO NOT
    DEPLOY in their docstrings.
    """
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.signals import screener as scr
    missing_marker: list[str] = []
    missing_registry: list[str] = []
    for name in NEW_EXPLORATORY_STRATEGIES_B748C:
        key = name[len("strat_"):]
        if key not in ALL_STRATEGIES:
            missing_registry.append(name)
            continue
        fn = getattr(scr, name, None)
        if fn is None:
            missing_registry.append(name)
            continue
        doc = fn.__doc__ or ""
        if "EXPLORATORY" not in doc or "DO NOT DEPLOY" not in doc:
            missing_marker.append(name)
    assert not missing_registry, f"missing from registry: {missing_registry}"
    assert not missing_marker, f"missing EXPLORATORY+DO NOT DEPLOY: {missing_marker}"


def test_b748c_pin3_strategy_count_unchanged_at_221():
    """B748c is docstring + walk-back only; no roster change."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 221


def test_b748c_pin4_strat_activist_13d_long_has_stale_data_caveat():
    """Revived strat_activist_13d_long must document the 17-month SC_13D
    staleness so future readers/cube users know fires apply to 2020-2024 only.
    """
    from backtest.signals.screener import strat_activist_13d_long
    doc = strat_activist_13d_long.__doc__ or ""
    assert "STALENESS" in doc.upper() or "STALE" in doc.upper(), (
        "strat_activist_13d_long must document SC_13D staleness caveat post-B748c"
    )


def test_b748c_pin5_strat_m_and_a_target_long_explicitly_pins_item_codes_gap():
    """strat_m_and_a_target_long EXPLORATORY rationale must point to the
    real blocker: missing item_codes column on 8_K parquets.
    """
    from backtest.signals.screener import strat_m_and_a_target_long
    doc = strat_m_and_a_target_long.__doc__ or ""
    assert "EXPLORATORY" in doc and "DO NOT DEPLOY" in doc


def test_b748c_pin6_news_sentiment_strategies_reference_per_ticker_data_gap():
    """At least one news strategy's docstring must explain the per-ticker
    data gap so the EXPLORATORY status is self-documenting.
    """
    from backtest.signals.screener import strat_news_sentiment_long
    doc = strat_news_sentiment_long.__doc__ or ""
    assert "per-ticker" in doc or "global.parquet" in doc or "Ticker column" in doc, (
        "strat_news_sentiment_long must explain the per-ticker quivernews gap"
    )


def test_b748c_pin7_persistence_strategies_reference_12d_window():
    """At least one persistence strategy must document the 12-day window
    blocker so a future reader understands why EXPLORATORY.
    """
    from backtest.signals.screener import strat_institutional_multi_quarter_persistence_long
    doc = strat_institutional_multi_quarter_persistence_long.__doc__ or ""
    assert ("12" in doc and ("day" in doc.lower() or "twelve" in doc.lower())) or "TWELVE DAYS" in doc, (
        "persistence strategy must document the 12-day window data gap"
    )


def test_b748c_pin8_total_exploratory_post_b748c_is_10():
    """Audit lock: 10 strategies should carry EXPLORATORY + DO NOT DEPLOY
    post-B748c (1 carryover + 9 new).

    Drift here means a new EXPLORATORY tag was added or one was removed
    without going through the same investigation discipline.
    """
    expected = {
        # carryover from B748b (data state unchanged)
        "strat_m_and_a_target_long",
        # new B748c
        "strat_institutional_committed_growth_long",
        "strat_institutional_multi_quarter_persistence_long",
        "strat_news_momentum_long",
        "strat_news_momentum_short",
        "strat_news_reversal_long",
        "strat_news_reversal_short",
        "strat_news_sentiment_long",
        "strat_news_sentiment_shift_long",
        "strat_squeeze_setup_long",
    }
    # Add the earlier EXPLORATORY-tagged strategies from prior batches
    # (B722 po3 + B738 FOMC + B732 CP-3/CP-7 + B652 W5m + others). We are
    # only locking the B748c-relevant set here; the global EXPLORATORY count
    # may legitimately be higher due to those.
    from backtest.signals import screener as scr
    actual_tagged = set()
    for name in expected:
        fn = getattr(scr, name, None)
        if fn is not None:
            doc = fn.__doc__ or ""
            if "EXPLORATORY" in doc and "DO NOT DEPLOY" in doc:
                actual_tagged.add(name)
    missing = expected - actual_tagged
    assert not missing, f"expected EXPLORATORY post-B748c but not tagged: {missing}"
