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


def test_b748c_pin2_nine_originally_tagged_strategies_now_revived_post_b748d():
    """B748d (2026-06-14) walked back ALL 9 B748c-NEW EXPLORATORY tags
    after audit-script-fix surfaced 4 PATH DRIFT findings:
      - persistence reads `derived/institutional_persistence_t1a/`
      - news_sentiment reads `polygon/news/`
      - sec_edgar reads `sec_edgar_decoded/`
      - index_rebalance reads `derived/index_rebalance_events.parquet`
    All B748c-tagged strategies have working data + producers; tags were
    FALSE per CHECKLIST #44(b) when B748c audit-script bugs were corrected.
    """
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.signals import screener as scr
    still_tagged: list[str] = []
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
        if "EXPLORATORY -- DO NOT DEPLOY" in doc:
            still_tagged.append(name)
    assert not missing_registry, f"missing from registry: {missing_registry}"
    assert not still_tagged, (
        f"B748d walk-back regressed: {still_tagged} still carry EXPLORATORY"
    )


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


def test_b748c_pin5_strat_m_and_a_target_long_revived_in_b748d():
    """B748d 2026-06-14: strat_m_and_a_target_long was REVIVED. The
    `item_codes` column DOES exist in the decoded cache at
    `data_prefetch/sec_edgar_decoded/8_K/<TICKER>.parquet`. B748c
    pointed at the wrong cache path.
    """
    from backtest.signals.screener import strat_m_and_a_target_long
    doc = strat_m_and_a_target_long.__doc__ or ""
    assert "EXPLORATORY -- DO NOT DEPLOY" not in doc


def test_b748c_pin6_news_sentiment_strategies_revived_with_b748d_caveat():
    """B748d walk-back: news strategies revived because polygon/news/
    per-ticker data was discovered (B748c assumed wrong path).
    """
    from backtest.signals.screener import strat_news_sentiment_long
    doc = strat_news_sentiment_long.__doc__ or ""
    assert "polygon/news" in doc or "polygon\\news" in doc or "B748d" in doc, (
        "news sentiment docstring must reference the post-B748d discovered path"
    )


def test_b748c_pin7_persistence_strategies_revived_with_b748d_caveat():
    """B748d walk-back: persistence strategies revived because the
    `derived/institutional_persistence_t1a/` snapshots have 4Q persistence
    columns populated.
    """
    from backtest.signals.screener import strat_institutional_multi_quarter_persistence_long
    doc = strat_institutional_multi_quarter_persistence_long.__doc__ or ""
    assert ("institutional_persistence_t1a" in doc or "B748d" in doc), (
        "persistence docstring must reference the B748d-discovered path"
    )


def test_b748c_pin8_total_b748c_originals_exploratory_post_b748d_is_zero():
    """B748d walk-back: 0 of the 10 B748b+B748c-originally-EXPLORATORY
    strategies remain tagged. ALL of them were FALSE positives caused
    by B745+B748c audit-script path-discovery bugs.

    Drift = a strategy here re-acquires EXPLORATORY without owner-approved
    re-disposition (which would be unexpected since B748d verified the
    data state empirically).
    """
    b748_originals = {
        "strat_m_and_a_target_long",
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
    from backtest.signals import screener as scr
    still_tagged = set()
    for name in b748_originals:
        fn = getattr(scr, name, None)
        if fn is not None:
            doc = fn.__doc__ or ""
            if "EXPLORATORY -- DO NOT DEPLOY" in doc:
                still_tagged.add(name)
    assert not still_tagged, (
        f"B748d walk-back regressed: {still_tagged} should NOT have EXPLORATORY post-B748d"
    )
