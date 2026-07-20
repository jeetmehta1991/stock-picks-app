"""B1326 (Council 358, B4): the cloud smoke exposed two real gaps -
(1) SMC silent on cloud: `smartmoneyconcepts` pip-installed locally but not on
    the instance; the vendored __init__ does a bare `import smartmoneyconcepts`.
    Fix: launcher runs `pip install -e vendored/smartmoneyconcepts/`.
(2) code_sha=unknown: the lean git-archive tar has no .git; fix: bake CODE_SHA
    into the tar + env_fingerprint reads it when git is absent.
"""
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_launcher_installs_vendored_smc():
    txt = (REPO / "scripts" / "aws_chunk_launch.py").read_text(encoding="utf-8")
    assert "pip install --quiet -e vendored/smartmoneyconcepts/" in txt, (
        "launcher must install the vendored SMC package so the bare "
        "`import smartmoneyconcepts` resolves on cloud (B4)")


def test_build_script_bakes_code_sha():
    txt = (REPO / "scripts" / "build_r5_code_tar.py").read_text(encoding="utf-8")
    assert 'tar", "-rf", OUT, "CODE_SHA"' in txt or "CODE_SHA" in txt
    assert "-rf" in txt and "CODE_SHA" in txt, "build must append CODE_SHA to tar"


def test_env_fingerprint_reads_baked_code_sha(tmp_path, monkeypatch):
    """In a dir with no .git but a CODE_SHA file, fingerprint uses the file."""
    import scripts.env_fingerprint as ef
    (tmp_path / "CODE_SHA").write_text("abc123def456789", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    fp = ef.fingerprint()
    assert fp["code_sha"] == "abc123def456", f"expected baked SHA, got {fp['code_sha']}"
