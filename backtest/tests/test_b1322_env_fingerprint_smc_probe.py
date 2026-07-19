"""B1322 (Council 354, #159 Part A): the env-fingerprint parity manifest must
carry the SMC vendored-import probe + smc_active as a MERGE-CRITICAL field.
The chunk-2 gap (B1317) was 22 SMC strategies silent on cloud (lib failed to
import) while local had them -- pip-freeze can't see a vendored directory, so
only a direct import-probe catches it. This pins that the gate now does.
"""
import json
import subprocess
import sys
from pathlib import Path

import scripts.env_fingerprint as ef

REPO = Path(__file__).resolve().parents[2]


def test_smc_active_is_merge_critical():
    assert "smc_active" in ef.MERGE_CRITICAL


def test_fingerprint_has_probe_fields():
    fp = ef.fingerprint()
    for k in ("smc_lib_importable", "smc_phase", "smc_active", "numpy_blas",
              "os", "python", "pip_freeze_hash", "pip_n_packages"):
        assert k in fp, f"fingerprint missing {k}"
    assert isinstance(fp["smc_active"], bool)


def test_check_flags_smc_active_mismatch(tmp_path):
    """A chunk WITH smc vs a chunk WITHOUT must fail the parity --check."""
    base = ef.fingerprint()
    a = dict(base); a["smc_active"] = True
    b = dict(base); b["smc_active"] = False
    pa, pb = tmp_path / "a.json", tmp_path / "b.json"
    pa.write_text(json.dumps(a)); pb.write_text(json.dumps(b))
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "env_fingerprint.py"),
         "--check", str(pa), str(pb)],
        capture_output=True, text=True)
    assert r.returncode == 1, "parity check must FAIL on smc_active mismatch"
    assert "smc_active" in r.stdout
