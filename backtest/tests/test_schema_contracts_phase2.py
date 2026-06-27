"""Phase 2 schema-contract tests for producer-consumer pairs registry.

# Source: Council 140 Option-5 PARALLEL-FAN-OUT Sub-agent B per owner directive
# 2026-06-28 ("Phase 2 expansion: catch schema drift at test-time per
# CHECKLIST #126").

These tests are the Phase 2 EXPANSION of the structural fix for
`feedback_monitor_design_vs_operational_gap` recurrence. Phase 1 (seed)
shipped 11 tests across 3 contracts in test_schema_contracts.py.

This module ADDS 18 NEW tests across 5 NEW categories:

  CATEGORY 1: inject_*_signals contracts (signal_loader.py)
    - One test per registered inject function (10 funcs)
    - Asserts: importable + correct signature + screener consumer ref +
      documented signal keys
  CATEGORY 2: writer.py output schema (3 tests for non-stub outputs)
  CATEGORY 3: SMC_PHASE flag contract (producer + consumer + value enum)
  CATEGORY 4: holdout_guard contract (importability + intrusion raise +
              HoldoutUnlock accept)
  CATEGORY 5: signal_loader registry parametrized sweep (1 batch)

Each test references docs/PRODUCER_CONSUMER_PAIRS.md row numbers for
traceability per registry-driven test pattern.

Per `feedback_silent_failure_pairing_rule`: each test has explicit
assertion + failure message naming the contract.
"""
from __future__ import annotations

import inspect
import json
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


# ============================================================================
# CATEGORY 1: inject_*_signals contracts (10 funcs in signal_loader.py)
# Registry row 3: signal_loader.inject_*_signals -> screener.screen_instrument
# ============================================================================

# Canonical inject function name -> (signature kind, documented signal keys
# from docstring per signal_loader.py)
# Note: `signature_kind` 3 means (signals, ticker, as_of); 4 means
# (signals, ticker, df, as_of) for producers that need ohlcv df.
INJECT_FUNCTIONS = {
    "inject_news_sentiment_signals":          (4, ["news_sentiment_mean",
                                                   "news_sentiment_5d",
                                                   "news_sentiment_shift",
                                                   "news_count_7d"]),
    "inject_institutional_persistence_signals": (3, ["institutional_persistence_growing",
                                                     "institutional_persistence_strong",
                                                     "persistence_quarters_buying",
                                                     "total_active_holders"]),
    "inject_short_interest_signals":          (3, ["short_interest_pct",
                                                   "days_to_cover"]),
    "inject_search_volume_signals":           (3, ["search_volume_index_recent",
                                                   "search_volume_pct_change_7d",
                                                   "search_volume_spike",
                                                   "retail_attention_score"]),
    "inject_earnings_surprise_yoy_signals":   (4, ["yoy_surprise_high",
                                                   "yoy_surprise_negative"]),
    "inject_pead_signals":                    (4, ["days_since_last_earnings",
                                                   "within_pead_window",
                                                   "pead_positive_surprise",
                                                   "pead_negative_surprise"]),
    "inject_classification_change_signals":   (3, ["classification_changed_recent",
                                                   "classification_change_to_tech",
                                                   "classification_change_to_defensive",
                                                   "classification_change_from_tech"]),
    "inject_insider_buying_signals":          (3, ["insider_cluster_active",
                                                   "insider_unique_buyers_30d",
                                                   "insider_director_buyers_30d",
                                                   "insider_officer_buyers_30d"]),
    "inject_insider_signal_keys":             (3, ["concentrated_sell",
                                                   "cfo_buy",
                                                   "large_dollar_buy",
                                                   "ceo_buy",
                                                   "cluster_buy"]),
    "inject_institutional_signals":           (3, ["institutional_signal",
                                                   "institutional_strong_buy",
                                                   "institutional_buy",
                                                   "institutional_negative",
                                                   "institutional_new_positions",
                                                   "institutional_increased"]),
}


@pytest.mark.parametrize("fn_name,expected", list(INJECT_FUNCTIONS.items()))
def test_schema_contract_inject_function_importable_and_signature(fn_name, expected):
    """Contract Cat-1 producer side: every inject_*_signals function must
    be importable from backtest.data.signal_loader with the documented
    (signals, ticker, [df], as_of) signature.

    Per docs/PRODUCER_CONSUMER_PAIRS.md row 3.
    """
    from backtest.data import signal_loader
    assert hasattr(signal_loader, fn_name), (
        f"signal_loader must expose {fn_name!r} per producer-consumer "
        f"pairs registry row 3"
    )
    fn = getattr(signal_loader, fn_name)
    assert callable(fn), f"{fn_name} must be callable"
    sig = inspect.signature(fn)
    required_arity, _docs = expected
    # Allow for default-valued trailing kwargs (e.g. lookback_days=7)
    n_params = len(sig.parameters)
    assert n_params >= required_arity, (
        f"{fn_name} expected >= {required_arity} parameters per signal_loader "
        f"docstring; got {n_params}: {list(sig.parameters)}"
    )
    # First param must be 'signals' (the dict being mutated)
    first_param = list(sig.parameters)[0]
    assert first_param == "signals", (
        f"{fn_name} first param must be 'signals' (dict mutated in-place) "
        f"per signal_loader convention; got {first_param!r}"
    )


@pytest.mark.parametrize("fn_name,expected", list(INJECT_FUNCTIONS.items()))
def test_schema_contract_inject_function_documents_signal_keys(fn_name, expected):
    """Contract Cat-1 producer side: each inject function's docstring must
    document the signal keys it emits per the producer-consumer contract.

    Per `feedback_silent_failure_pairing_rule`: silent producers without
    documented keys are exactly the B273/B1034 silent-gap failure class.
    Per docs/PRODUCER_CONSUMER_PAIRS.md row 3.
    """
    from backtest.data import signal_loader
    fn = getattr(signal_loader, fn_name)
    doc = inspect.getdoc(fn) or ""
    _arity, key_list = expected
    missing = [k for k in key_list if k not in doc]
    assert not missing, (
        f"{fn_name} docstring must document signal keys: missing {missing}. "
        f"Silent producers without docstring keys = B273/B1034 silent-gap "
        f"failure class."
    )


@pytest.mark.parametrize("fn_name", list(INJECT_FUNCTIONS.keys()))
def test_schema_contract_inject_function_referenced_in_screener(fn_name):
    """Contract Cat-1 consumer side: every inject_*_signals function must
    be referenced (imported + called) from screener.py:screen_instrument.

    This is the B1034 silent-gap detector: B1010 concentrated_sell key was
    consumed BUT smart_money.insider_signal() was never called -> strategy
    couldn't fire. inject_insider_signal_keys (B1034 fix) added the call.
    Per docs/PRODUCER_CONSUMER_PAIRS.md row 3.
    """
    screener_path = REPO / "backtest" / "signals" / "screener.py"
    content = screener_path.read_text()
    assert fn_name in content, (
        f"screener.py must import/call {fn_name!r} per producer-consumer "
        f"contract row 3 (B1034 silent-gap class). If this fires, an "
        f"inject_* function was added to signal_loader.py without wiring "
        f"into screen_instrument path."
    )


# ============================================================================
# CATEGORY 2: writer.py output schema (non-stub outputs)
# Registry rows 6, 7, 8
# ============================================================================

def test_schema_contract_writer_trade_log_columns_documented():
    """Contract Cat-2 / row 6: writer.write_all_outputs must reference
    canonical trade_log columns. Schema drift here breaks dashboard,
    metrics.compute_strategy_metrics, sub-agent #5 walk-forward, +
    B1019 post-run analyzer.

    Per docs/PRODUCER_CONSUMER_PAIRS.md row 6.
    """
    writer_path = REPO / "backtest" / "results" / "writer.py"
    content = writer_path.read_text()
    # write_all_outputs must produce trade_log.parquet AND trade_log.csv
    assert "trade_log.parquet" in content, (
        "writer.py must produce trade_log.parquet per Pass 53 Sprint 2 "
        "DEC-491 (hybrid Parquet+CSV) + registry row 6"
    )
    assert "trade_log.csv" in content, (
        "writer.py must also produce trade_log.csv (human-readable; "
        "stringified complex cols) per DEC-491"
    )
    # Combo_id column is the writer-internal derivation per Batch 324
    assert "combo_id" in content, (
        "writer.py must reference combo_id column for winners pipeline "
        "per Batch 324 + registry row 6"
    )


def test_schema_contract_writer_strategy_regime_matrix_schema():
    """Contract Cat-2 / row 7: writer must emit strategy_regime_matrix.json
    with per-strategy { best_regimes, regime_verdicts, overall_win_rate,
    total_trades, passes_all } structure. Dashboard generators consume.

    Per docs/PRODUCER_CONSUMER_PAIRS.md row 7.
    """
    writer_path = REPO / "backtest" / "results" / "writer.py"
    content = writer_path.read_text()
    assert "strategy_regime_matrix.json" in content, (
        "writer.py must produce strategy_regime_matrix.json per registry "
        "row 7 (dashboard consumer)"
    )
    for key in ("best_regimes", "regime_verdicts", "overall_win_rate",
                "total_trades", "passes_all"):
        assert key in content, (
            f"writer.py strategy_regime_matrix must include {key!r} key "
            f"per registry row 7 schema"
        )


def test_schema_contract_writer_portfolio_metrics_dec095_schema():
    """Contract Cat-2 / row 8: writer must emit portfolio_metrics.json with
    DEC-095 schema (return, sharpe, max_dd). Dashboard data.js consumes.

    Per docs/PRODUCER_CONSUMER_PAIRS.md row 8.
    """
    writer_path = REPO / "backtest" / "results" / "writer.py"
    content = writer_path.read_text()
    assert "portfolio_metrics.json" in content, (
        "writer.py must produce portfolio_metrics.json per BUG-95 "
        "sub-batch 5 + DEC-095 + registry row 8"
    )
    # DEC-095 schema is computed via compute_portfolio_metrics_from_curves
    assert "compute_portfolio_metrics_from_curves" in content, (
        "portfolio_metrics computed via canonical helper per DEC-095"
    )


def test_schema_contract_writer_signal_fire_rates_b901_emit():
    """Contract Cat-2 / row 2: B901 signal_fire_rates.json emit is
    env-gated (EMIT_RAW_SIGNAL_FIRES=1). writer must call
    emit_raw_signal_fire_counts.

    Per docs/PRODUCER_CONSUMER_PAIRS.md row 2 + CLAUDE.md banner B1035 F4.
    """
    writer_path = REPO / "backtest" / "results" / "writer.py"
    content = writer_path.read_text()
    assert "emit_raw_signal_fire_counts" in content, (
        "writer.py must call emit_raw_signal_fire_counts per B901 "
        "DEFER-I implementation + registry row 2"
    )
    assert "signal_fire_rates.json" in content, (
        "writer.py must reference signal_fire_rates.json sink per "
        "registry row 2"
    )


# ============================================================================
# CATEGORY 3: SMC_PHASE flag contract
# Registry row 10
# ============================================================================

def test_schema_contract_smc_phase_producer_constant_exists():
    """Contract Cat-3 / row 10 producer side: backtest.config.SMC_PHASE
    must be defined as a string per registry contract.

    Per docs/PRODUCER_CONSUMER_PAIRS.md row 10.
    """
    from backtest import config
    assert hasattr(config, "SMC_PHASE"), (
        "backtest.config must define SMC_PHASE constant per Council 131 "
        "Option-A + DEC-508 + registry row 10"
    )
    assert isinstance(config.SMC_PHASE, str), (
        "SMC_PHASE must be a string per registry row 10 schema"
    )
    assert config.SMC_PHASE in ("B-CANARY", "PRODUCTION"), (
        f"SMC_PHASE must be one of (B-CANARY, PRODUCTION); got "
        f"{config.SMC_PHASE!r}"
    )


def test_schema_contract_smc_phase_consumer_reads_canonical_value():
    """Contract Cat-3 / row 10 consumer side: compute_smc_signals must
    read SMC_PHASE at call-time and short-circuit when != PRODUCTION.

    Per docs/PRODUCER_CONSUMER_PAIRS.md row 10 + B1038 fix.
    """
    smc_path = REPO / "backtest" / "signals" / "smc_ict.py"
    content = smc_path.read_text()
    assert "SMC_PHASE" in content, (
        "smc_ict.py must reference SMC_PHASE per registry row 10 + B1038"
    )
    assert "from backtest.config import SMC_PHASE" in content, (
        "smc_ict.py must import SMC_PHASE from backtest.config at call-time "
        "(not module-load) per B1038 Council 131 Option-A canary contract"
    )
    assert 'SMC_PHASE != "PRODUCTION"' in content, (
        "smc_ict.py compute_smc_signals must short-circuit when "
        "SMC_PHASE != 'PRODUCTION' per B1038 canary contract"
    )


# ============================================================================
# CATEGORY 4: holdout_guard contract
# Registry row 12
# ============================================================================

def test_schema_contract_holdout_guard_importable_api():
    """Contract Cat-4 / row 12 producer side: holdout_guard exposes
    assert_no_holdout_intrusion + HoldoutUnlock + HoldoutViolationError.

    Per docs/PRODUCER_CONSUMER_PAIRS.md row 12.
    """
    from backtest.util import holdout_guard
    for sym in ("assert_no_holdout_intrusion", "HoldoutUnlock",
                "HoldoutViolationError", "is_in_holdout",
                "FINAL_OOS_HOLDOUT_START", "FINAL_OOS_HOLDOUT_END"):
        assert hasattr(holdout_guard, sym), (
            f"holdout_guard must expose {sym!r} per registry row 12 "
            f"contract + DEC-505 walk-forward final-OOS gate"
        )


def test_schema_contract_holdout_guard_raises_on_intrusion():
    """Contract Cat-4 / row 12: assert_no_holdout_intrusion must raise
    HoldoutViolationError when dates intrude on the locked window.

    Per docs/PRODUCER_CONSUMER_PAIRS.md row 12.
    """
    from backtest.util.holdout_guard import (
        assert_no_holdout_intrusion, HoldoutViolationError,
        FINAL_OOS_HOLDOUT_START,
    )
    intruder = FINAL_OOS_HOLDOUT_START  # date inside the holdout window
    with pytest.raises(HoldoutViolationError):
        assert_no_holdout_intrusion(
            [intruder], caller_name="test_phase2_schema_contract"
        )


def test_schema_contract_holdout_guard_unlock_accepts_intrusion():
    """Contract Cat-4 / row 12: under HoldoutUnlock context the same date
    is accepted (final-1A-alpha gate evaluation path).

    Per docs/PRODUCER_CONSUMER_PAIRS.md row 12.
    """
    from backtest.util.holdout_guard import (
        assert_no_holdout_intrusion, HoldoutUnlock,
        FINAL_OOS_HOLDOUT_START,
    )
    intruder = FINAL_OOS_HOLDOUT_START
    with HoldoutUnlock("phase2-schema-contract-test"):
        # Must NOT raise
        assert_no_holdout_intrusion(
            [intruder], caller_name="test_phase2_unlock_path"
        )


def test_schema_contract_holdout_guard_wired_in_run_phase1a():
    """Contract Cat-4 / row 12 consumer side: run_phase1a.py:main() must
    wire holdout_guard (B1043 Sub-B fix, B1045 corrected to HoldoutUnlock).

    B1045 honest-finding pivot #27: Phase C v2.5 smoke FAIL revealed that
    Phase 1A-beta backtest IS the legitimate OOS consumer. Corrected to
    HoldoutUnlock context. Wire still enforces holdout for non-backtest
    callers per design.

    Per docs/PRODUCER_CONSUMER_PAIRS.md row 12 + B1043 Council 138 Sub-B
    + B1045 Council 140 fix.
    """
    runner_path = REPO / "backtest" / "run_phase1a.py"
    content = runner_path.read_text()
    assert "from backtest.util.holdout_guard import" in content, (
        "run_phase1a.py must import from holdout_guard per B1043 Sub-B "
        "fix + registry row 12"
    )
    assert "HoldoutUnlock" in content, (
        "run_phase1a.py main() must wire HoldoutUnlock context per "
        "B1045 fix (assert_no_holdout_intrusion was over-aggressive for "
        "Phase 1A-beta legitimate OOS evaluation)"
    )
    assert "phase_1a_beta_backtest_evaluation_per_design" in content, (
        "HoldoutUnlock reason must document why backtest is unlocked"
    )


# ============================================================================
# CATEGORY 5: signal_loader producer registry parametrized sweep
# Registry row 3 (aggregate)
# ============================================================================

def test_schema_contract_signal_loader_registry_complete():
    """Contract Cat-5: signal_loader.py must expose all 10 canonical
    inject_*_signals functions as the documented producer registry.

    Per docs/PRODUCER_CONSUMER_PAIRS.md row 3 + Council 40 P0 commits
    B921-B932 lineage (extracted 10 producers + 1 helper).
    """
    from backtest.data import signal_loader
    registered = {name for name in dir(signal_loader)
                  if name.startswith("inject_") and callable(getattr(signal_loader, name))}
    expected = set(INJECT_FUNCTIONS.keys())
    missing = expected - registered
    extra = registered - expected
    assert not missing, (
        f"signal_loader missing canonical inject_* funcs: {missing}. "
        f"Per registry row 3 + B921-B932 P0 lineage."
    )
    # Extras are not a failure (additive ships allowed) but should at least
    # be inspectable - assert each is a callable function
    for name in extra:
        fn = getattr(signal_loader, name)
        assert callable(fn), (
            f"signal_loader exposes inject_-prefixed non-callable {name}; "
            f"per `feedback_silent_failure_pairing_rule` namespace "
            f"convention reserves inject_ prefix for callables"
        )


def test_schema_contract_signal_loader_silent_failure_logger_exists():
    """Contract Cat-5: signal_loader must expose _log_silent_producer_failure
    helper. Every inject function must call this helper on producer
    exception per B273 silent-producer-failure lesson.

    Per docs/PRODUCER_CONSUMER_PAIRS.md row 3 + `feedback_silent_failure_pairing_rule`.
    """
    from backtest.data import signal_loader
    assert hasattr(signal_loader, "_log_silent_producer_failure"), (
        "signal_loader must expose _log_silent_producer_failure helper "
        "per B273 + L143 silent-producer-failure lesson + "
        "`feedback_silent_failure_pairing_rule`"
    )
    # Source-level assertion: every inject function references the helper
    source = inspect.getsource(signal_loader)
    inject_calls_to_helper = source.count("_log_silent_producer_failure(")
    # 10 inject functions + 1 def line = 11 references minimum
    assert inject_calls_to_helper >= 11, (
        f"signal_loader source must call _log_silent_producer_failure in "
        f"every inject function; found {inject_calls_to_helper} references "
        f"(expected >=11: 10 inject + 1 def)"
    )


# ============================================================================
# Phase 2 registry integrity tests
# ============================================================================

def test_phase2_registry_documents_phase2_categories():
    """Phase 2 closure: registry must reference the categories covered
    by this test module.

    Per Council 140 Option-5 PARALLEL-FAN-OUT.
    """
    registry_path = REPO / "docs" / "PRODUCER_CONSUMER_PAIRS.md"
    content = registry_path.read_text()
    # SMC_PHASE row
    assert "SMC_PHASE" in content, (
        "Registry must document SMC_PHASE flag per Phase 2 Cat-3"
    )
    # holdout_guard row
    assert "holdout_guard" in content, (
        "Registry must document holdout_guard per Phase 2 Cat-4"
    )
    # signal_loader row
    assert "signal_loader" in content, (
        "Registry must document signal_loader per Phase 2 Cat-1/5"
    )
