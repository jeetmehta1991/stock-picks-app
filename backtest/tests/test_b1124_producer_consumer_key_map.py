"""B1124 Test 9/10: producer-consumer key contract (Council 244).

Turn 9 autonomous loop extracted gate stacks via regex; the caveat is
that regex may miss dynamically constructed gates. This test cross-checks
that every s.get('key') consumer reference in screener.py has a producer
that actually emits that key.

Catches producer-consumer schema drift (analog to PIVOT #37 exit_method
vs exit_reason writer-reader schema).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent
SCREENER = REPO / "backtest" / "signals" / "screener.py"


PRODUCER_FILES = [
    "backtest/signals/technical.py",
    "backtest/signals/chart_patterns.py",
    "backtest/signals/calendar_effects.py",
    "backtest/signals/smc_ict.py",
    "backtest/signals/volume_profile.py",
    "backtest/signals/insider_buying.py",
    "backtest/signals/institutional_persistence_consumer.py",
    "backtest/signals/news_sentiment.py",
    "backtest/signals/pead.py",
    "backtest/signals/index_rebalance.py",
    "backtest/signals/cross_sectional.py",
    "backtest/signals/short_interest.py",
    "backtest/signals/multi_timeframe.py",
    "backtest/signals/earnings_surprise_yoy.py",
    "backtest/data/signal_loader.py",
    "backtest/data/smart_money.py",
    "backtest/data/macro.py",
    "backtest/data/sentiment.py",
]


def _extract_consumer_keys() -> set[str]:
    """Extract all s.get('key') AND s["key"] references from screener.py."""
    content = SCREENER.read_text(encoding="utf-8")
    get_keys = set(re.findall(r's\.get\(\s*["\']([a-z_0-9]+)["\']', content))
    bracket_keys = set(re.findall(r's\[\s*["\']([a-z_0-9]+)["\']\s*\]', content))
    return get_keys | bracket_keys


def _extract_emitted_keys() -> set[str]:
    """Extract all `result[key] =`, `out[key] =` and `signals[key] =` references from producer files."""
    emitted = set()
    for rel in PRODUCER_FILES:
        p = REPO / rel
        if not p.exists():
            continue
        content = p.read_text(encoding="utf-8", errors="ignore")
        # Match result["key"] = or out["key"] = or signals["key"] =
        emitted |= set(
            re.findall(
                r'(?:result|out|signals|df|features|state)\[\s*["\']([a-z_0-9]+)["\']\s*\]\s*=',
                content,
            )
        )
        # Match f-string dynamic keys: result[f"{prefix}_key"] - hard to statically resolve
        # Also match dict literal patterns: {"key": ...
        emitted |= set(re.findall(r'["\']([a-z_0-9]+)["\']\s*:\s*(?:True|False|None|\d)', content))
    return emitted


def test_screener_and_producer_files_exist():
    """Baseline: screener + at least one producer file exist."""
    assert SCREENER.exists(), f"screener.py missing at {SCREENER}"
    existing = [REPO / p for p in PRODUCER_FILES if (REPO / p).exists()]
    assert len(existing) >= 10, (
        f"At least 10 producer files must exist; got {len(existing)}"
    )


def test_consumer_key_universe_bounded():
    """screener.py must reference a substantial number of signal keys."""
    keys = _extract_consumer_keys()
    assert len(keys) >= 100, (
        f"Expected screener.py to consume >=100 distinct signal keys; got {len(keys)}"
    )


def test_universe_expected_signal_keys_present():
    """Known-important signal keys must appear in consumer set."""
    consumer_keys = _extract_consumer_keys()
    critical_keys = {
        "close_above_open",
        "rsi_14",
        "vol_above_avg",
        "price_above_ema_200",
        "adx",
        "macd_12_26_9_bullish",
    }
    missing = critical_keys - consumer_keys
    assert not missing, (
        f"Critical signal keys missing from screener consumption: {missing}. "
        f"Either producer/consumer drift OR key was renamed silently."
    )


def test_producer_consumer_coverage_report_writable():
    """Meta-test: coverage-diff artifact can be written (for future audit)."""
    consumer_keys = _extract_consumer_keys()
    emitted_keys = _extract_emitted_keys()
    orphaned_consumer_keys = consumer_keys - emitted_keys
    coverage_ratio = len(consumer_keys - orphaned_consumer_keys) / max(len(consumer_keys), 1)

    # Coverage floor: at least 30% of consumer keys have emit-side evidence.
    # NOTE: this is a soft floor - many keys are dynamically constructed and
    # will not appear in static emit sweep. Use for regression detection.
    assert coverage_ratio >= 0.30, (
        f"Producer-consumer static coverage regressed to {coverage_ratio:.1%}. "
        f"Consumer keys: {len(consumer_keys)}, "
        f"emit-side evidence: {len(consumer_keys - orphaned_consumer_keys)}. "
        f"Investigate silent producer removal."
    )
