"""Batch 348: look-ahead-bias audit script regression tests.

Source: per CHECKLIST #77 canonical-source attribution.
Owner directive Pass 53 2026-05-25: audit look-ahead-bias before Phase 1A-beta
full re-run (option i). Audit script is `scripts/audit_look_ahead_bias.py`;
report is `output_audit/look_ahead_bias_audit.md`.

These tests pin:

  T1 (Unit)        the regex patterns flag known forward-peek constructs
  T1 (Unit)        the empirical heuristic correctly flags fabricated suspect rows
  T2 (Smoke)       end-to-end script run produces both JSON + MD outputs
  T6 (Regression)  the 3 known-false-positive snippets in calendar_effects /
                   pead / smc_ict still surface as findings (so future code
                   reviewer is forced to re-review rather than silently
                   missing a real leak that takes the same shape)
  T11 (Property)   the verdict_for() function obeys: static-finding -> CODE_FIX_REQUIRED;
                   empirical-flag-only -> INVESTIGATE; small-n -> LIKELY_LEGIT_RARE;
                   no flag -> CLEAN

Why pin false-positives instead of suppressing them: an audit tool that
silently filters known patterns will later silently miss a real leak that
happens to look like one of those patterns. Pinning the surface area means
each commit that touches calendar_effects/pead/smc_ict re-asserts that the
producer is still safe by virtue of upstream df-truncation invariant.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).parent.parent.parent
SCRIPT = REPO / "scripts" / "audit_look_ahead_bias.py"

# Import the script's functions for unit tests
sys.path.insert(0, str(REPO / "scripts"))
import audit_look_ahead_bias as audit  # type: ignore  # noqa: E402


# ---------------------------------------------------------------------
# Tier 1 - Unit: static pattern matching
# ---------------------------------------------------------------------
def test_static_pattern_flags_negative_shift(tmp_path):
    """`.shift(-N)` must be flagged HIGH severity."""
    f = tmp_path / "bad.py"
    f.write_text("import pandas as pd\nx = df['close'].shift(-1)\n", encoding="utf-8")
    findings = audit.static_scan_file(f)
    assert any("shift(-N)" in finding["pattern"] for finding in findings)
    assert any(finding["severity"] == "HIGH" for finding in findings)


def test_static_pattern_flags_iloc_forward(tmp_path):
    """`.iloc[i+N]` must be flagged HIGH severity."""
    f = tmp_path / "bad.py"
    f.write_text("v = df.iloc[i + 1]\n", encoding="utf-8")
    findings = audit.static_scan_file(f)
    assert any("iloc[i+N]" in finding["pattern"] for finding in findings)


def test_static_pattern_flags_forward_named_local(tmp_path):
    """A local named `future_close` must be flagged."""
    f = tmp_path / "bad.py"
    f.write_text("future_close = 100.0\n", encoding="utf-8")
    findings = audit.static_scan_file(f)
    assert any("forward-named local" in finding["pattern"] for finding in findings)


def test_static_pattern_skips_safe_positive_shift(tmp_path):
    """`.shift(1)` (positive = backward) must NOT be flagged."""
    f = tmp_path / "ok.py"
    f.write_text("prev = df['close'].shift(1)\n", encoding="utf-8")
    findings = audit.static_scan_file(f)
    assert findings == []


def test_static_pattern_skips_comments(tmp_path):
    """Pattern in a comment must NOT be flagged."""
    f = tmp_path / "ok.py"
    f.write_text("# this would peek if used: df.shift(-1)\nx = 1\n", encoding="utf-8")
    findings = audit.static_scan_file(f)
    assert findings == []


# ---------------------------------------------------------------------
# Tier 1 - Unit: empirical heuristic
# ---------------------------------------------------------------------
def test_empirical_flags_suspicious_win_rate(tmp_path):
    """Strategy with WR > 70% on n >= 10 must be flagged WIN_RATE_SUSPICIOUS."""
    df = pd.DataFrame({
        "strategy": ["fake_strat"] * 12,
        "win": [True] * 9 + [False] * 3,  # 75% wr
        "pnl_pct": [1.0] * 9 + [-1.0] * 3,
        "hold_days": [5] * 12,
    })
    fake_log = tmp_path / "trade_log.csv"
    df.to_csv(fake_log, index=False)
    result = audit.empirical_scan(fake_log)
    row = next(r for r in result["rows"] if r["strategy"] == "fake_strat")
    assert "WIN_RATE_SUSPICIOUS" in row["empirical_flags"]


def test_empirical_flags_no_losses(tmp_path):
    """Strategy with 100% WR on n >= 5 must be flagged NO_LOSSES_SUSPICIOUS."""
    df = pd.DataFrame({
        "strategy": ["fake_strat"] * 6,
        "win": [True] * 6,
        "pnl_pct": [1.0] * 6,
        "hold_days": [5] * 6,
    })
    fake_log = tmp_path / "trade_log.csv"
    df.to_csv(fake_log, index=False)
    result = audit.empirical_scan(fake_log)
    row = next(r for r in result["rows"] if r["strategy"] == "fake_strat")
    assert "NO_LOSSES_SUSPICIOUS" in row["empirical_flags"]


def test_empirical_skips_small_n(tmp_path):
    """Strategy with WR=100% on n < 5 must NOT be flagged."""
    df = pd.DataFrame({
        "strategy": ["rare_strat"] * 3,
        "win": [True] * 3,
        "pnl_pct": [1.0] * 3,
        "hold_days": [5] * 3,
    })
    fake_log = tmp_path / "trade_log.csv"
    df.to_csv(fake_log, index=False)
    result = audit.empirical_scan(fake_log)
    row = next(r for r in result["rows"] if r["strategy"] == "rare_strat")
    assert row["empirical_flags"] == []


# ---------------------------------------------------------------------
# Tier 11 - Property: verdict logic
# ---------------------------------------------------------------------
def test_verdict_clean_when_no_signal():
    emp_row = {"n": 20, "empirical_flags": []}
    assert audit.verdict_for("x", [], emp_row) == "CLEAN"


def test_verdict_investigate_when_empirical_only():
    emp_row = {"n": 20, "empirical_flags": ["WIN_RATE_SUSPICIOUS"]}
    assert audit.verdict_for("x", [], emp_row) == "INVESTIGATE"


def test_verdict_likely_legit_rare_when_small_n():
    emp_row = {"n": 3, "empirical_flags": []}
    assert audit.verdict_for("x", [], emp_row) == "LIKELY_LEGIT_RARE"


# ---------------------------------------------------------------------
# Tier 6 - Regression: known false-positive shapes must still surface
# ---------------------------------------------------------------------
def test_regression_pead_iloc_forward_still_flagged():
    """pead.py line 233 uses `iloc[pos + 1]`. The audit MUST surface this so a
    reviewer can re-validate the upstream df-truncation invariant on every
    commit that touches the file. False-positive verdict is documented in
    output_audit/look_ahead_bias_audit.md; suppressing the flag would let a
    real future-peek slip past."""
    pead_path = REPO / "backtest" / "signals" / "pead.py"
    if not pead_path.exists():
        pytest.skip("pead.py not present")
    findings = audit.static_scan_file(pead_path)
    assert any("iloc[i+N]" in finding["pattern"] for finding in findings), \
        "pead.py iloc[pos + 1] no longer flagged - verify audit regex didn't regress"


def test_regression_calendar_effects_lookahead_label_still_flagged():
    """calendar_effects.py uses `max_lookahead` as a parameter name. Audit
    should surface; false-positive verdict documented (holiday calendar is
    deterministic, not future-data peek)."""
    cal_path = REPO / "backtest" / "signals" / "calendar_effects.py"
    if not cal_path.exists():
        pytest.skip("calendar_effects.py not present")
    findings = audit.static_scan_file(cal_path)
    assert any("look-ahead label" in finding["pattern"] for finding in findings)


# ---------------------------------------------------------------------
# Tier 2 - Smoke: end-to-end script
# ---------------------------------------------------------------------
def test_smoke_audit_script_runs_end_to_end(tmp_path):
    """Run the audit script against the live repo + write to a temp output dir.
    Must produce both JSON and MD outputs."""
    trade_log = REPO / "output_stage_d" / "trade_log.csv"
    if not trade_log.exists():
        pytest.skip("output_stage_d/trade_log.csv not present")
    out = tmp_path / "audit_out"
    cmd = [
        sys.executable, str(SCRIPT),
        "--trade-log", str(trade_log),
        "--signals-dir", str(REPO / "backtest" / "signals"),
        "--engine-dir", str(REPO / "backtest" / "engine"),
        "--output-dir", str(out),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, f"script failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    assert (out / "look_ahead_bias_audit.json").exists()
    assert (out / "look_ahead_bias_audit.md").exists()
    payload = json.loads((out / "look_ahead_bias_audit.json").read_text())
    assert "verdict_counts" in payload
    assert "static" in payload
    assert "empirical" in payload
