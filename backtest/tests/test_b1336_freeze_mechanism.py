"""B1336 (Council 365, owner-approved): the code-freeze mechanism must EXIST
(L212 -- B1333 promised --expect-sha / build-at-SHA before they were built,
and coverage_smoke false-failed frozen batches by comparing to git HEAD).
"""
import json
from pathlib import Path

import pandas as pd

import scripts.coverage_smoke as cs

REPO = Path(__file__).resolve().parents[2]
FROZEN = "e846b6d2cfb3"  # batch-1 sequence SHA


def test_launcher_has_expect_sha_flag():
    txt = (REPO / "scripts" / "aws_chunk_launch.py").read_text(encoding="utf-8")
    assert '"--expect-sha"' in txt, "launcher must expose --expect-sha"
    assert "args.expect_sha or" in txt, "--expect-sha must override the HEAD default"


def test_build_script_supports_arbitrary_sha_and_sidecar():
    txt = (REPO / "scripts" / "build_r5_code_tar.py").read_text(encoding="utf-8")
    assert '"--sha"' in txt, "build must support building at an arbitrary SHA"
    assert 'KEY + ".sha"' in txt, "build --upload must write the .sha sidecar (#161)"


def _frozen_dir(d, code_sha):
    pd.DataFrame({
        "strategy": ["a"] * 3 + ["b"] * 3,
        "exit_method": ["e1", "e2", "e3"] * 2,
    }).to_csv(d / "exit_strategy_comparison.csv", index=False)
    core = ["rsi_oversold", "ema_50_200", "bollinger_tight",
            "hammer_at_support_long", "obv_volume_breakout"]
    pd.DataFrame({"ticker": ["A"] * len(core),
                  "entry_date": ["2024-01-02"] * len(core),
                  "strategy": core}).to_parquet(d / "trade_log.parquet")
    (d / "env_fingerprint.json").write_text(json.dumps({
        "smc_active": True, "smc_lib_importable": True, "smc_phase": "PRODUCTION",
        "calendar_backend": "nyse_mcal", "code_sha": code_sha}))


def test_analyze_expected_sha_passes_frozen_batch(tmp_path):
    """A frozen-SHA batch must PASS when --expected-sha matches the batch."""
    _frozen_dir(tmp_path, FROZEN)
    assert cs.analyze(str(tmp_path), expected_sha=FROZEN) == 0


def test_analyze_head_compare_would_fail_frozen_batch(tmp_path):
    """Without --expected-sha the same frozen batch fails vs advanced HEAD --
    the exact B1334 trap this flag exists to fix."""
    _frozen_dir(tmp_path, FROZEN)
    assert cs.analyze(str(tmp_path)) == 1
