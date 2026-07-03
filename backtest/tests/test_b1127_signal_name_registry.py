"""B1127 Tier-4 Empirical: Signal name registry (Council 246).

CATCHES: vol_spike naming errors (this session, 13 recs rewrote); close /
macd_bullish name assumptions (B1124 authoring mistakes). Signal names
have decimal-shift conventions (vol_spike_15x = 1.5x NOT 15x) that
regex/grep won't catch.

RED-FIRST for any signal name referenced in a strategy that no producer
actually emits.
"""
# Source: per CHECKLIST #77 canonical-source; author Council 246 B1127 2026-07-03
from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent
SCREENER = REPO / "backtest" / "signals" / "screener.py"


def _all_consumer_signal_refs() -> set[str]:
    content = SCREENER.read_text(encoding="utf-8")
    return (
        set(re.findall(r's\.get\(\s*["\']([a-z_0-9]+)["\']', content))
        | set(re.findall(r's\[\s*["\']([a-z_0-9]+)["\']\s*\]', content))
    )


VOL_SPIKE_KNOWN_VALID = {
    "vol_spike_12x",
    "vol_spike_15x",
    "vol_spike_17x",
    "vol_spike_2x",
    "vol_spike_3x",
    "vol_above_avg",
    "vol_below_avg",
}

VOL_SPIKE_KNOWN_INVALID = {
    "vol_spike_5x",
    "vol_spike_10x",
    "vol_spike_20x",
}


def test_vol_spike_naming_convention_no_invalid_refs():
    """catch invalid vol_spike references (feedback_vol_spike_naming_convention).

    vol_spike_15x = 1.5x avg (NOT 15x). vol_spike_5x/10x/20x DO NOT EXIST.
    """
    refs = _all_consumer_signal_refs()
    invalid = refs & VOL_SPIKE_KNOWN_INVALID
    assert not invalid, (
        f"Invalid vol_spike references in screener.py: {invalid}. "
        f"Per feedback_vol_spike_naming_convention: vol_spike_15x=1.5x, "
        f"vol_spike_17x=1.7x; only vol_spike_2x/3x are integer multiples. "
        f"vol_spike_5x/10x/20x DO NOT EXIST."
    )


def test_at_least_one_vol_spike_variant_consumed():
    """screener.py must consume at least one valid vol_spike variant."""
    refs = _all_consumer_signal_refs()
    valid_consumed = refs & VOL_SPIKE_KNOWN_VALID
    assert valid_consumed, (
        f"screener.py consumes ZERO valid vol_spike variants. "
        f"Expected any of: {VOL_SPIKE_KNOWN_VALID}"
    )


def test_macd_signal_name_uses_full_period_notation():
    """MACD signal names use `macd_12_26_9_*` not bare `macd_bullish`."""
    refs = _all_consumer_signal_refs()
    bare_names = {"macd_bullish", "macd_bearish"}
    invalid = refs & bare_names
    assert not invalid, (
        f"Bare macd_bullish/bearish references found: {invalid}. "
        f"Canonical form is macd_12_26_9_bullish etc. per producer emit."
    )


def test_close_signal_names_use_qualified_form():
    """`close` alone is ambiguous; use close_above_open / close_in_top_40pct_of_range etc."""
    refs = _all_consumer_signal_refs()
    assert "close" not in refs, (
        "Bare 'close' consumer reference found. Use qualified form "
        "(close_above_open, close_below_open, close_in_top_40pct_of_range)."
    )


def test_signal_name_lexical_lowercase_underscore():
    """All signal names must be lowercase alphanumeric with underscores.

    Allow leading digit for legitimate names like '8k_item_1_01_filed_within_30d'
    (SEC EDGAR 8-K item form reference).
    """
    refs = _all_consumer_signal_refs()
    invalid_names = {r for r in refs if not re.match(r"^[a-z0-9][a-z_0-9]*$", r)}
    assert not invalid_names, (
        f"Signal names must be lowercase snake_case. Invalid: {list(invalid_names)[:10]}"
    )
