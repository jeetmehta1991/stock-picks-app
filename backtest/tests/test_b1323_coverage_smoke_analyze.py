"""B1323 (Council 355, #159 Part B): coverage_smoke.analyze() must FAIL when
isolation leaks a cross-strategy portfolio gate or SMC is inactive, and PASS on
a clean isolated run. Synthetic dirs keep this fast (no engine run)."""
import json
import pandas as pd
import pytest

import scripts.coverage_smoke as cs


def _mkdir_clean(d):
    # fanout 2 strat x 3 exits = 6
    pd.DataFrame({
        "strategy": ["a", "a", "a", "b", "b", "b"],
        "exit_method": ["e1", "e2", "e3", "e1", "e2", "e3"],
    }).to_csv(d / "exit_strategy_comparison.csv", index=False)
    # only allowed skip reasons
    pd.DataFrame({
        "ticker": ["X", "Y"], "date": ["2024-01-02", "2024-01-03"],
        "strategy": ["a", "b"],
        "reason": ["no_next_bar", "ticker_already_open_same_strategy_bug61_mode_c"],
    }).to_csv(d / "skipped_trades.csv", index=False)
    (d / "env_fingerprint.json").write_text(json.dumps({
        "smc_active": True, "smc_lib_importable": True, "smc_phase": "PRODUCTION",
        "numpy_blas": "openblas", "os": "test"}))


def test_clean_isolated_run_passes(tmp_path):
    _mkdir_clean(tmp_path)
    assert cs.analyze(str(tmp_path)) == 0


def test_leaked_portfolio_gate_fails(tmp_path):
    _mkdir_clean(tmp_path)
    pd.DataFrame({
        "ticker": ["X"], "date": ["2024-01-02"], "strategy": ["a"],
        "reason": ["portfolio_gate_ticker_already_in_portfolio"],
    }).to_csv(tmp_path / "skipped_trades.csv", index=False)
    assert cs.analyze(str(tmp_path)) == 1  # isolation leak must FAIL


def test_smc_inactive_fails(tmp_path):
    _mkdir_clean(tmp_path)
    (tmp_path / "env_fingerprint.json").write_text(json.dumps({
        "smc_active": False, "smc_lib_importable": False, "smc_phase": "PRODUCTION"}))
    assert cs.analyze(str(tmp_path)) == 1  # SMC silent must FAIL


def test_stale_code_sha_fails(tmp_path):
    """B1324 stale-cloud-code gate: a code_sha != local HEAD must FAIL."""
    _mkdir_clean(tmp_path)
    (tmp_path / "env_fingerprint.json").write_text(json.dumps({
        "smc_active": True, "smc_lib_importable": True, "smc_phase": "PRODUCTION",
        "code_sha": "deadbeef0000"}))  # not the local HEAD
    assert cs.analyze(str(tmp_path)) == 1  # stale code must FAIL
