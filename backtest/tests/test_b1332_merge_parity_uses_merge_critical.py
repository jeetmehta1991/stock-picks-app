"""B1332 (Council 362): adversarial-review find - merge_batch_outputs enforced
env-parity on a HARDCODED (grid,calendar) tuple, NOT env_fingerprint.MERGE_
CRITICAL, so the B1329 code_sha + smc_active additions were never enforced at
merge (batches at different code/SMC-state would merge silently). This pins that
the merge uses the single-source MERGE_CRITICAL.
"""
from pathlib import Path

import scripts.env_fingerprint as ef

REPO = Path(__file__).resolve().parents[2]


def test_merge_uses_merge_critical_not_hardcoded():
    txt = (REPO / "scripts" / "merge_batch_outputs.py").read_text(encoding="utf-8")
    assert "from scripts.env_fingerprint import MERGE_CRITICAL" in txt, (
        "merge must import MERGE_CRITICAL (single source), not hardcode crit")


def test_merge_critical_includes_code_sha_and_smc():
    # the fields the merge now enforces across batches
    assert "code_sha" in ef.MERGE_CRITICAL
    assert "smc_active" in ef.MERGE_CRITICAL
    assert "grid_hash" in ef.MERGE_CRITICAL
    assert "calendar_backend" in ef.MERGE_CRITICAL
