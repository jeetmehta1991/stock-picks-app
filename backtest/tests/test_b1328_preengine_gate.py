"""B1328 (Council 360): the HARD pre-engine gate must FAIL (exit 3) on a bad
env (smc inactive / wrong calendar / stale code_sha) so a batch never spends
compute on a broken environment; PASS (0) only when all three are good.
"""
import json
import subprocess
import sys
from pathlib import Path

GATE = Path(__file__).resolve().parents[2] / "scripts" / "preengine_gate.py"
GOOD = {"smc_active": True, "smc_lib_importable": True, "smc_phase": "PRODUCTION",
        "calendar_backend": "nyse_mcal", "code_sha": "91c2627ea3a7"}


def _run(fp: dict, expected: str, tmp_path) -> int:
    p = tmp_path / "fp.json"
    p.write_text(json.dumps(fp))
    return subprocess.run([sys.executable, str(GATE), str(p), expected]).returncode


def test_good_env_passes(tmp_path):
    assert _run(GOOD, "91c2627ea3a7", tmp_path) == 0


def test_smc_inactive_aborts(tmp_path):
    bad = dict(GOOD, smc_active=False)
    assert _run(bad, "91c2627ea3a7", tmp_path) == 3


def test_wrong_calendar_aborts(tmp_path):
    bad = dict(GOOD, calendar_backend="monfri_fallback")
    assert _run(bad, "91c2627ea3a7", tmp_path) == 3


def test_stale_code_sha_aborts(tmp_path):
    assert _run(GOOD, "deadbeef0000", tmp_path) == 3  # expected != fingerprint


def test_missing_fingerprint_aborts(tmp_path):
    r = subprocess.run([sys.executable, str(GATE),
                        str(tmp_path / "nope.json"), "abc"]).returncode
    assert r == 3


def test_launcher_wires_gate():
    txt = (Path(__file__).resolve().parents[2] / "scripts"
           / "aws_chunk_launch.py").read_text(encoding="utf-8")
    assert "preengine_gate.py" in txt and "CHUNK@N@_GATEFAIL" in txt
    assert "@EXPECT_SHA@" in txt
