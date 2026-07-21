"""B1337 (Council 365, owner-approved): prelaunch gate (#160/#161) + preflight
C10 (batch-complete claims require committed outputs).
"""
import scripts.prelaunch_gate as pg
import scripts.preflight as pf

GOOD_MANIFEST = {
    "sequence": "r5_t1a_escalating", "batch": 2, "frozen_sha": "e846b6d2cfb3",
    "isolation": True, "calendar": "nyse_mcal",
    "tickers": ["MSFT", "GOOGL"], "budget_cap_usd": 50.0,
    "spent_usd": 26.0, "projected_batch_usd": 1.0,
}
LEDGER = {"batches": [{"batch": 1, "tickers": ["SNDK", "MU", "WDC"],
                       "committed": True}]}


def test_gate_passes_good_manifest():
    assert pg.check(dict(GOOD_MANIFEST), LEDGER, "e846b6d2cfb3full") == []


def test_gate_fails_stale_tar():
    fails = pg.check(dict(GOOD_MANIFEST), LEDGER, "deadbeef0000")
    assert any("STALE ARTIFACT" in f for f in fails)


def test_gate_fails_ticker_overlap():
    m = dict(GOOD_MANIFEST); m["tickers"] = ["MU", "MSFT"]
    fails = pg.check(m, LEDGER, "e846b6d2cfb3")
    assert any("overlap" in f for f in fails)


def test_gate_fails_uncommitted_prior_batch():
    led = {"batches": [{"batch": 1, "tickers": ["X"], "committed": False}]}
    fails = pg.check(dict(GOOD_MANIFEST), led, "e846b6d2cfb3")
    assert any("NOT committed" in f for f in fails)


def test_gate_fails_budget_breach():
    m = dict(GOOD_MANIFEST); m["projected_batch_usd"] = 30.0
    fails = pg.check(m, LEDGER, "e846b6d2cfb3")
    assert any("budget breach" in f for f in fails)


def test_gate_fails_missing_field_and_wrong_semantics():
    m = dict(GOOD_MANIFEST); del m["frozen_sha"]
    assert any("missing" in f for f in pg.check(m, LEDGER, "abc"))
    m2 = dict(GOOD_MANIFEST); m2["isolation"] = False
    assert any("isolation" in f for f in pg.check(m2, LEDGER, "e846b6d2cfb3"))


def test_c10_flags_unbacked_claim_and_accepts_backed():
    lines = [("EXECUTION_QUEUE.md", "BATCH 2 COMPLETE all checks green")]
    v = pf.find_unbacked_batch_claims(lines, lambda n: False)
    assert v and "C10" in v[0]
    assert pf.find_unbacked_batch_claims(lines, lambda n: True) == []


def test_c10_ignores_waiver_other_files_and_big_numbers():
    assert pf.find_unbacked_batch_claims(
        [("EXECUTION_QUEUE.md", "BATCH 2 COMPLETE preflight-allow: C10")],
        lambda n: False) == []
    assert pf.find_unbacked_batch_claims(
        [("notes.md", "BATCH 2 COMPLETE")], lambda n: False) == []
    # queue batch-numbering (B1331-style 4-digit) must not trigger
    assert pf.find_unbacked_batch_claims(
        [("EXECUTION_QUEUE.md", "Batch 1331 (2026-07-20): X COMPLETE")],
        lambda n: False) == []


def test_launcher_wires_manifest_gate():
    from pathlib import Path
    txt = (Path(pf.__file__).resolve().parents[1] / "scripts"
           / "aws_chunk_launch.py").read_text(encoding="utf-8")
    assert '"--manifest"' in txt and "prelaunch_gate.py" in txt
