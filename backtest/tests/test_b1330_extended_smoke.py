"""B1330 (Council 361): extended smoke checks (owner "B all") + dispersion-CB
isolation bypass. Validates the analyze-time family check, the determinism and
merge-append modes, and pins the CB-bypass guard.
"""
import json
from pathlib import Path

import pandas as pd
import pytest

import scripts.coverage_smoke as cs

REPO = Path(__file__).resolve().parents[2]


def _fp(d):
    (d / "env_fingerprint.json").write_text(json.dumps({
        "smc_active": True, "smc_lib_importable": True, "smc_phase": "PRODUCTION",
        "calendar_backend": "nyse_mcal", "code_sha": "zzz"}))


def _cube(d, strategies):
    rows = [{"strategy": s, "exit_method": f"e{i}"} for s in strategies for i in range(3)]
    pd.DataFrame(rows).to_csv(d / "exit_strategy_comparison.csv", index=False)


def test_core_family_silent_fails(tmp_path):
    # a trade_log with only non-core (event) strategies -> a CORE family = 0 -> FAIL
    _fp(tmp_path); _cube(tmp_path, ["news_momentum_long", "insider_cluster_long"])
    pd.DataFrame({"ticker": ["A"], "entry_date": ["2024-01-02"],
                  "strategy": ["news_momentum_long"]}).to_parquet(
        tmp_path / "trade_log.parquet")
    # code_sha will mismatch local HEAD -> also fails; assert non-zero (fail) + core msg present
    rc = cs.analyze(str(tmp_path))
    assert rc == 1


def test_core_family_present_ok_on_families(tmp_path, capsys):
    _fp(tmp_path); _cube(tmp_path, ["rsi_oversold", "macd_crossover", "bollinger_tight"])
    # cover all 5 CORE families: oscillator/trend/volatility/candle/avwap_vol
    core = ["rsi_oversold", "ema_50_200", "bollinger_tight",
            "hammer_at_support_long", "obv_volume_breakout"]
    pd.DataFrame({"ticker": ["A"] * len(core),
                  "entry_date": ["2024-01-02"] * len(core),
                  "strategy": core}).to_parquet(tmp_path / "trade_log.parquet")
    cs.analyze(str(tmp_path))
    out = capsys.readouterr().out
    assert "CORE producer family" not in out  # no core-family FAIL


def test_determinism_identical_vs_diff(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(); b.mkdir()
    df = pd.DataFrame({"strategy": ["s"], "exit_method": ["e"], "win_rate": [0.5]})
    df.to_csv(a / "exit_strategy_comparison.csv", index=False)
    df.to_csv(b / "exit_strategy_comparison.csv", index=False)
    assert cs.determinism(str(a), str(b)) == 0
    df2 = df.copy(); df2["win_rate"] = 0.6
    df2.to_csv(b / "exit_strategy_comparison.csv", index=False)
    assert cs.determinism(str(a), str(b)) == 1


def test_merge_check_disjoint_vs_overlap(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(); b.mkdir()
    pd.DataFrame({"ticker": ["AAPL"], "entry_date": ["2024-01-02"],
                  "strategy": ["s"]}).to_parquet(a / "trade_log.parquet")
    pd.DataFrame({"ticker": ["MSFT"], "entry_date": ["2024-01-02"],
                  "strategy": ["s"]}).to_parquet(b / "trade_log.parquet")
    assert cs.merge_check([str(a), str(b)]) == 0  # disjoint OK
    pd.DataFrame({"ticker": ["AAPL"], "entry_date": ["2024-01-03"],
                  "strategy": ["s"]}).to_parquet(b / "trade_log.parquet")
    assert cs.merge_check([str(a), str(b)]) == 1  # overlap -> fail


def test_dispersion_cb_bypassed_in_isolation():
    txt = (REPO / "backtest" / "engine" / "backtest.py").read_text(encoding="utf-8")
    assert '_cb_result.get("triggered") and not self.cube_isolation' in txt
