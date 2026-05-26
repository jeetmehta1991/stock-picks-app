"""Batch 365 silent-gap hardening: promote BUG-296 fire-rate warnings to
Tier 4 (System) gate; add semantic-population audit; add per-criterion
evaluability gate.

Source (per CHECKLIST #77 canonical-source attribution):
- Owner approval 2026-05-25 of 3 hardening items after Batch 363 silent
  gap diagnosis: smart_money_score was at 0% fire rate in every prior
  Phase 1A run because the engine gate at backtest.py:1308 was wrong.
  BUG-296 fire-rate monitor was emitting warnings every run -- but no
  one read them.

Item 1 (this file): pyramid Tier 4 gate that reads signal_fire_rates.json
and FAILS the test (rather than warning) when any signal has
fire_rate < 50% of expected_min_rate. The first run that re-introduces
the silent gap will fail the pyramid.

Item 2 (separate change in scripts/audit_trade_log_forensic.py): semantic-
population check that distinguishes "populated with default sentinel"
(0 numeric / "none" string) from "populated with real data".

Item 3 (separate change in backtest/results/metrics.py): per-criterion
empirical evaluability gate that surfaces criterion_evaluable=False
when a criterion can't be computed from the trade_log (e.g. smart
money lift needs both score>0 AND score=0 samples).

Pyramid tiers exercised:
  T4 (System)      reading the engine's signal_fire_rates.json output
                   and gating on fire-rate baselines
  T6 (Regression)  if any silent gap re-appears in a future run, the
                   test fails BEFORE downstream analysis (winners.parquet,
                   passing-criteria evaluation, agent overlay) reads
                   garbage data
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent.parent


# Canonical signal contract per BUG-296 fire-rate monitor in the engine
# (backtest.py emits this dict structure to signal_fire_rates.json).
# fire_rate < 50% of expected_min_rate triggers the alert.
SMART_MONEY_SIGNALS = (
    "smart_money_score", "congressional_signal", "insider_signal",
    "institutional_signal",
)


def _find_signal_fire_rates() -> Path | None:
    """Locate signal_fire_rates.json from the most-recent Phase 1A-beta-
    scope output dir. Returns None if no run has produced one yet."""
    candidates = [
        # Order matters: prefer most-recent / most-canonical
        REPO / "output_phase_1a_beta_merged_local" / "signal_fire_rates.json",
        REPO / "output_smoke_cube" / "signal_fire_rates.json",
        REPO / "output_stage_d" / "signal_fire_rates.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def test_batch365_signal_fire_rates_json_exists_when_phase_1a_beta_has_run():
    """If a Phase 1A-beta-scope run has happened, signal_fire_rates.json
    MUST exist. Otherwise the BUG-296 monitor regressed."""
    p = _find_signal_fire_rates()
    # If no run has happened yet, skip rather than fail (clean-clone case)
    if p is None:
        pytest.skip(
            "No Phase 1A-beta-scope output found; run "
            "scripts/smoke_test_cube_stage_d.py first to populate "
            "signal_fire_rates.json"
        )
    payload = json.loads(p.read_text())
    assert "signals" in payload, f"{p} missing 'signals' key"
    for sig in SMART_MONEY_SIGNALS:
        assert sig in payload["signals"], (
            f"{p} missing signal {sig!r} -- BUG-296 monitor regressed; "
            f"the engine no longer emits the canonical 4 smart-money "
            f"signal fire rates"
        )


def test_batch365_smart_money_signals_meet_fire_rate_baseline():
    """OWNER-GATED PYRAMID TIER 4 (System): smart-money signals must fire
    at >=50% of their expected_min_rate. This is the gate that would have
    caught the Batch 363 silent gap in 2026-05-24's Phase 1A-beta run.

    Before this test, fire_rate=0.0% on all 4 smart-money signals across
    every prior Phase 1A run was emitted as a WARNING and ignored. The
    test fails the pyramid so the next run with the silent gap blocks
    downstream analysis (winners.parquet extraction, criterion-7 smart
    money lift evaluation, agent overlay)."""
    p = _find_signal_fire_rates()
    if p is None:
        pytest.skip("No Phase 1A-beta-scope output found")
    payload = json.loads(p.read_text())
    signals = payload.get("signals", {})

    failures = []
    for sig in SMART_MONEY_SIGNALS:
        entry = signals.get(sig)
        if entry is None:
            failures.append(f"{sig}: missing from signal_fire_rates.json")
            continue
        fire_rate = entry.get("fire_rate")
        expected_min = entry.get("expected_min_rate")
        if fire_rate is None or expected_min is None:
            failures.append(
                f"{sig}: malformed entry; fire_rate={fire_rate} "
                f"expected_min_rate={expected_min}"
            )
            continue
        # Half-expected-min is the BUG-296 alert threshold; we enforce
        # the same as a hard gate.
        gate = expected_min * 0.5
        if fire_rate < gate:
            failures.append(
                f"{sig}: fire_rate={fire_rate*100:.1f}% < "
                f"50% of expected_min ({expected_min*100:.1f}%) = "
                f"{gate*100:.1f}% gate. "
                f"alert={entry.get('alert', 'NONE')}"
            )
    assert not failures, (
        f"Batch 365 silent-gap gate: {len(failures)} smart-money "
        f"signal(s) below fire-rate baseline (would have caught Batch 363 "
        f"silent gap in 2026-05-24 run):\n  - " + "\n  - ".join(failures)
    )


def test_batch365_alert_field_consistent_with_fire_rate():
    """Schema invariant: BUG-296 monitor sets alert string when
    fire_rate < 0.5 * expected_min_rate; null otherwise. This test pins
    the contract so future BUG-296 modifications don't silently change
    the gate threshold without updating us."""
    p = _find_signal_fire_rates()
    if p is None:
        pytest.skip("No Phase 1A-beta-scope output found")
    payload = json.loads(p.read_text())
    signals = payload.get("signals", {})
    inconsistencies = []
    for sig_name, entry in signals.items():
        if not isinstance(entry, dict):
            continue
        fr = entry.get("fire_rate")
        em = entry.get("expected_min_rate")
        alert = entry.get("alert")
        if fr is None or em is None:
            continue
        gate = em * 0.5
        if fr < gate and alert is None:
            inconsistencies.append(
                f"{sig_name}: fire_rate={fr} < {gate} but alert is null "
                f"(BUG-296 monitor schema break)"
            )
        if fr >= gate and alert is not None:
            inconsistencies.append(
                f"{sig_name}: fire_rate={fr} >= {gate} but alert={alert!r} "
                f"(BUG-296 monitor false alarm)"
            )
    assert not inconsistencies, "\n".join(inconsistencies)
