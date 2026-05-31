"""Batch 522 (2026-05-31) -- P17b/c/d/e sleeve + modifier scaffolds.

Source: per CHECKLIST #77 + EXECUTION_QUEUE.md items P17b/c/d/e
(SCAFFOLD shipment while P17a scoped extraction completes in flight).

Pins:

  (1) `sc_13g_filed_within_days` schema (boolean + optional enrichment)
  (2) `compute_sec_edgar_signals` returns the expected key bundle
  (3) `strat_activist_13d_long` fires iff sc_13d_filed_within_30d=True
  (4) `strat_m_and_a_target_long` fires iff
      8k_item_1_01_filed_within_30d=True
  (5) `tier_modifier_officer_change_5_02` downgrades by 1 only when
      8k_item_5_02_filed_within_7d=True; floors at LOW; no-op when
      tier unrecognized
  (6) `smart_money_score_modifier_13g` adds +1 only when
      sc_13g_filed_within_30d=True
  (7) NOT-REGISTERED guard: `activist_13d_long` and
      `m_and_a_target_long` MUST NOT be in ALL_STRATEGIES yet
      (forces an explicit owner-approved batch to flip)
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# 1. SC_13G helper schema
# ---------------------------------------------------------------------------

def test_batch522_sc_13g_helper_returns_false_when_no_filings():
    from backtest.signals.sec_edgar_extractor import sc_13g_filed_within_days
    fake_df = pd.DataFrame({
        "filing_date":    [date(2024, 1, 1)],
        "filer_identity": ["Vanguard Group Inc"],
        "percent_owned":  [5.2],
    })
    out = sc_13g_filed_within_days(
        "ZZZZ", date(2024, 6, 1), lookback_days=30, df=fake_df,
    )
    assert out == {"sc_13g_filed_within_30d": False}


def test_batch522_sc_13g_helper_returns_true_with_enrichment():
    from backtest.signals.sec_edgar_extractor import sc_13g_filed_within_days
    fake_df = pd.DataFrame({
        "filing_date":    [date(2024, 5, 20)],
        "filer_identity": ["BlackRock Inc"],
        "percent_owned":  [7.4],
    })
    out = sc_13g_filed_within_days(
        "ZZZZ", date(2024, 6, 1), lookback_days=30, df=fake_df,
    )
    assert out["sc_13g_filed_within_30d"] is True
    assert out["sc_13g_latest_filer_identity"] == "BlackRock Inc"
    assert out["sc_13g_latest_percent_owned"] == pytest.approx(7.4)


def test_batch522_sc_13g_helper_empty_on_missing_cache():
    from backtest.signals.sec_edgar_extractor import sc_13g_filed_within_days
    # No df + ticker that won't exist in any cache
    out = sc_13g_filed_within_days("___NONEXISTENT___", date(2024, 6, 1))
    assert out == {}


# ---------------------------------------------------------------------------
# 2. Producer bundle
# ---------------------------------------------------------------------------

def test_batch522_compute_sec_edgar_signals_returns_dict():
    from backtest.signals.sec_edgar_extractor import compute_sec_edgar_signals
    out = compute_sec_edgar_signals("___NONEXISTENT___", date(2024, 6, 1))
    assert isinstance(out, dict)  # empty on no data


def test_batch522_compute_sec_edgar_signals_does_not_raise():
    """Producer bundle must NEVER raise -- silent-failure pattern
    matches compute_short_interest_signals / earnings_surprise_yoy
    convention used in screen_instrument."""
    from backtest.signals.sec_edgar_extractor import compute_sec_edgar_signals
    # Pathological input: empty string ticker, far-future date
    try:
        compute_sec_edgar_signals("", date(2099, 12, 31))
    except Exception as e:
        pytest.fail(f"producer bundle raised: {e!r}")


# ---------------------------------------------------------------------------
# 3. Strategy fire semantics
# ---------------------------------------------------------------------------

def test_batch522_strat_activist_13d_long_fires_on_true():
    from backtest.signals.screener import strat_activist_13d_long
    sig = {
        "sc_13d_filed_within_30d":         True,
        "sc_13d_latest_filer_identity":    "Carl Icahn",
        "sc_13d_latest_percent_owned":     6.2,
    }
    result = strat_activist_13d_long(sig)
    assert result["fires"] is True
    assert result["direction"] == "long"
    assert result["category"] == "sec_edgar_sleeve"


def test_batch522_strat_activist_13d_long_skips_when_no_filing():
    from backtest.signals.screener import strat_activist_13d_long
    sig = {"sc_13d_filed_within_30d": False}
    result = strat_activist_13d_long(sig)
    assert result["fires"] is False


def test_batch522_strat_activist_13d_long_skips_when_signal_absent():
    """Missing signal key (e.g. extractor not wired yet) MUST default
    to non-firing. This is the safety invariant that lets Batch 522
    ship before P17a scoped extraction completes."""
    from backtest.signals.screener import strat_activist_13d_long
    result = strat_activist_13d_long({})
    assert result["fires"] is False


def test_batch522_strat_m_and_a_target_long_fires_on_true():
    from backtest.signals.screener import strat_m_and_a_target_long
    sig = {"8k_item_1_01_filed_within_30d": True}
    result = strat_m_and_a_target_long(sig)
    assert result["fires"] is True
    assert result["direction"] == "long"


def test_batch522_strat_m_and_a_target_long_skips_when_no_filing():
    from backtest.signals.screener import strat_m_and_a_target_long
    sig = {"8k_item_1_01_filed_within_30d": False}
    result = strat_m_and_a_target_long(sig)
    assert result["fires"] is False


def test_batch522_strat_m_and_a_target_long_skips_when_signal_absent():
    from backtest.signals.screener import strat_m_and_a_target_long
    result = strat_m_and_a_target_long({})
    assert result["fires"] is False


# ---------------------------------------------------------------------------
# 4. Modifier helpers
# ---------------------------------------------------------------------------

def _patch_8k_5_02(fired: bool):
    return patch(
        "backtest.signals.sec_edgar_extractor.eight_k_item_filed_within_days",
        return_value={"8k_item_5_02_filed_within_7d": fired},
    )


def test_batch522_tier_modifier_downgrades_by_one_when_5_02_fired():
    from backtest.signals.sec_edgar_modifiers import (
        tier_modifier_officer_change_5_02,
    )
    with _patch_8k_5_02(True):
        new_tier = tier_modifier_officer_change_5_02(
            "AAPL", date(2024, 6, 1), "HIGH",
        )
    assert new_tier == "MEDIUM-HIGH"


def test_batch522_tier_modifier_noop_when_no_5_02_filing():
    from backtest.signals.sec_edgar_modifiers import (
        tier_modifier_officer_change_5_02,
    )
    with _patch_8k_5_02(False):
        new_tier = tier_modifier_officer_change_5_02(
            "AAPL", date(2024, 6, 1), "HIGH",
        )
    assert new_tier == "HIGH"


def test_batch522_tier_modifier_floors_at_low():
    from backtest.signals.sec_edgar_modifiers import (
        tier_modifier_officer_change_5_02,
    )
    with _patch_8k_5_02(True):
        new_tier = tier_modifier_officer_change_5_02(
            "AAPL", date(2024, 6, 1), "LOW",
        )
    assert new_tier == "LOW"  # can't downgrade below LOW


def test_batch522_tier_modifier_noop_on_unknown_tier():
    from backtest.signals.sec_edgar_modifiers import (
        tier_modifier_officer_change_5_02,
    )
    new_tier = tier_modifier_officer_change_5_02(
        "AAPL", date(2024, 6, 1), "GIBBERISH",
    )
    assert new_tier == "GIBBERISH"


def _patch_13g(fired: bool):
    return patch(
        "backtest.signals.sec_edgar_extractor.sc_13g_filed_within_days",
        return_value={"sc_13g_filed_within_30d": fired},
    )


def test_batch522_smart_money_score_modifier_adds_one_when_13g_fired():
    from backtest.signals.sec_edgar_modifiers import (
        smart_money_score_modifier_13g,
    )
    with _patch_13g(True):
        new_score = smart_money_score_modifier_13g(
            "AAPL", date(2024, 6, 1), current_score=2,
        )
    assert new_score == 3


def test_batch522_smart_money_score_modifier_noop_when_no_13g():
    from backtest.signals.sec_edgar_modifiers import (
        smart_money_score_modifier_13g,
    )
    with _patch_13g(False):
        new_score = smart_money_score_modifier_13g(
            "AAPL", date(2024, 6, 1), current_score=2,
        )
    assert new_score == 2


# ---------------------------------------------------------------------------
# 5. WIRED + REGISTERED assertion (Batch 531 ACTIVATED)
# ---------------------------------------------------------------------------
# Batch 531 (2026-05-31, owner directive "wire in activate truly pending
# items") flipped these from NOT-REGISTERED/NOT-WIRED safety guards to
# REGISTERED/WIRED assertions. If activation is ever reverted, these
# tests fire and force the revert commit to also document the rollback.

def test_batch522_p17_strategies_ARE_registered_in_all_strategies():
    """Batch 531 ACTIVATED: the 2 P17 sleeve strategies MUST appear in
    ALL_STRATEGIES. Producer compute_sec_edgar_signals wired in
    screen_instrument so they receive their boolean trigger signals."""
    from backtest.signals.screener import ALL_STRATEGIES
    must_register = {"activist_13d_long", "m_and_a_target_long"}
    missing = must_register - set(ALL_STRATEGIES.keys())
    assert not missing, (
        f"Batch 531 P17 sleeve activation regressed: {missing} absent "
        f"from ALL_STRATEGIES. Restore registrations in screener.py "
        f"ALL_STRATEGIES dict per Batch 531 wire-in block."
    )


def test_batch522_modifiers_ARE_wired_in_tier_and_score_logic():
    """Batch 531 ACTIVATED: P17d tier modifier wired into
    `backtest/engine/backtest.py` (post-preliminary_tier hook); P17e
    smart-money modifier wired into `backtest/data/smart_money.py`
    (post-composite-band hook). Both silent-failure guarded."""
    repo = Path(__file__).resolve().parent.parent.parent
    engine_text = (repo / "backtest" / "engine" / "backtest.py").read_text(
        encoding="utf-8",
    )
    smart_money_text = (repo / "backtest" / "data" / "smart_money.py").read_text(
        encoding="utf-8",
    )
    assert "tier_modifier_officer_change_5_02" in engine_text, (
        "Batch 531 P17d tier modifier wire-in removed from "
        "engine/backtest.py -- restore the post-preliminary_tier hook."
    )
    assert "smart_money_score_modifier_13g" in smart_money_text, (
        "Batch 531 P17e modifier wire-in removed from "
        "data/smart_money.py -- restore the post-composite-band hook."
    )


def test_batch531_producer_compute_sec_edgar_signals_wired_in_screener():
    """Batch 531: producer bundle wired into screen_instrument via
    silent-failure logger pattern (mirrors P15 + P16 producers)."""
    repo = Path(__file__).resolve().parent.parent.parent
    screener_text = (repo / "backtest" / "signals" / "screener.py").read_text(
        encoding="utf-8",
    )
    assert "compute_sec_edgar_signals" in screener_text, (
        "Batch 531 producer wire-in regressed: compute_sec_edgar_signals "
        "absent from screener.py. Restore try/except block."
    )
    assert '_log_silent_producer_failure("sec_edgar"' in screener_text, (
        "Batch 531 producer not guarded by silent-failure logger -- "
        "restore standard wrapper per Batch 458 convention."
    )
