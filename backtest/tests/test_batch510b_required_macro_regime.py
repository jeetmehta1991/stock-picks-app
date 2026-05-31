"""Batch 510b (2026-05-31) -- R4 spec required-macro-regime tests.

Source: per CHECKLIST #77 + owner directive 2026-05-31 ("wire
macro_score == neutral on all 5 candidate strategies for R4").
Queue row: EXECUTION_QUEUE.md item #9 (R4 cube spec).

Wires `config.STRATEGY_REQUIRED_MACRO_REGIME` -- a dict mapping
strategy name to required macro band ("negative" / "neutral" /
"positive"). Engine consults the dict at candidate evaluation and
skips with `required_macro_regime_mismatch_*` reason when the
current macro_score doesn't match.

Default dict is EMPTY -> no behavior change for non-R4 runs.
Owner populates entries in `backtest/config.py` for the R4 cube
spec (5 candidate strategies expected: bollinger_tight,
monthly_bias_momentum_long, xs_quality_top_quintile_long,
pead_long, adx_initiation).
"""
from __future__ import annotations

from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Config knob exists + default empty
# ---------------------------------------------------------------------------

def test_batch510b_required_macro_regime_dict_exists():
    from backtest.config import STRATEGY_REQUIRED_MACRO_REGIME
    assert isinstance(STRATEGY_REQUIRED_MACRO_REGIME, dict)


def test_batch510b_required_macro_regime_active_r4_entries():
    """Batch 514 (2026-05-31) -- R4 cube ACTIVATED per owner directive.
    Dict now contains the 5 candidate strategies (entry filter:
    macro_score == neutral), backed by Batch 501 entry-side optimizer
    findings."""
    from backtest.config import STRATEGY_REQUIRED_MACRO_REGIME
    expected = {
        "bollinger_tight":              "neutral",
        "monthly_bias_momentum_long":   "neutral",
        "xs_quality_top_quintile_long": "neutral",
        "pead_long":                    "neutral",
        "adx_initiation":               "neutral",
    }
    assert STRATEGY_REQUIRED_MACRO_REGIME == expected, (
        "Batch 514 R4 activation: STRATEGY_REQUIRED_MACRO_REGIME drifted "
        "from owner-approved 5-strategy macro_neutral set."
    )


def test_batch510b_config_documents_5_candidate_examples():
    """Config docstring documents the 5 candidate strategies as
    commented-out examples for owner R4 activation."""
    cfg = (REPO / "backtest" / "config.py").read_text(encoding="utf-8")
    # All 5 strategy names appear in the comment block
    assert "bollinger_tight" in cfg
    assert "monthly_bias_momentum_long" in cfg
    assert "xs_quality_top_quintile_long" in cfg
    assert "pead_long" in cfg
    assert "adx_initiation" in cfg


# ---------------------------------------------------------------------------
# Engine wire-in (source-text pin; full engine instantiation skipped)
# ---------------------------------------------------------------------------

def test_batch510b_engine_consults_required_macro_regime():
    eng = (REPO / "backtest" / "engine" / "backtest.py").read_text(encoding="utf-8")
    assert "from backtest.config import STRATEGY_REQUIRED_MACRO_REGIME" in eng
    assert "STRATEGY_REQUIRED_MACRO_REGIME.get(" in eng


def test_batch510b_macro_band_classifier_three_bands():
    """Engine maps macro_score sign to one of {negative, neutral, positive}
    matching the Batch 501 entry-side optimizer bucketing."""
    eng = (REPO / "backtest" / "engine" / "backtest.py").read_text(encoding="utf-8")
    assert '_macro_band = "negative"' in eng
    assert '_macro_band = "neutral"' in eng
    assert '_macro_band = "positive"' in eng


def test_batch510b_skip_reason_carries_required_and_actual_bands():
    """Engine emits a descriptive skip_reason so skipped_trades.csv
    differentiates required-macro-regime mismatch from other skip causes."""
    eng = (REPO / "backtest" / "engine" / "backtest.py").read_text(encoding="utf-8")
    assert "required_macro_regime_mismatch" in eng
    assert "_batch510b" in eng


# ---------------------------------------------------------------------------
# Synthetic dispatch logic (sign -> band)
# ---------------------------------------------------------------------------

def test_batch510b_macro_score_sign_classifies_correctly():
    """Pin the band-classification rule outside the engine for clarity:
    -1.0 -> negative; 0.0 -> neutral; +1.0 -> positive."""
    def _classify(v: float) -> str:
        if v < 0: return "negative"
        if v > 0: return "positive"
        return "neutral"
    assert _classify(-1.0) == "negative"
    assert _classify(-0.01) == "negative"
    assert _classify(0.0) == "neutral"
    assert _classify(0.01) == "positive"
    assert _classify(1.0) == "positive"


# ---------------------------------------------------------------------------
# Owner-sign-off pin: changing default requires explicit approval
# ---------------------------------------------------------------------------

def test_batch510b_active_set_size_pinned():
    """Pin the active set size at 5 (Batch 514 owner-activated R4).
    A change in size surfaces here forcing co-update of queue row #9
    + owner sign-off."""
    from backtest.config import STRATEGY_REQUIRED_MACRO_REGIME
    assert len(STRATEGY_REQUIRED_MACRO_REGIME) == 5, (
        f"STRATEGY_REQUIRED_MACRO_REGIME size changed from 5 (Batch 514 "
        f"R4 activation) to {len(STRATEGY_REQUIRED_MACRO_REGIME)}. "
        f"Owner sign-off required; update queue row #9 + this pin."
    )
    # All 5 entries must be 'neutral' regime
    assert all(v == "neutral" for v in STRATEGY_REQUIRED_MACRO_REGIME.values())
