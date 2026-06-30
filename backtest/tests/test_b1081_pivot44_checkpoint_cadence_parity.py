"""B1081 PIVOT #44 fix: checkpoint cadence parity pin test.

Source: Council 200 RECOMMEND Option 4 + framework-first PIVOT #44 fix
post-B1079 Phase 4 spot interrupt at sim_day=50.

ROOT CAUSE (B1079 r5_full_20260629_155837 forensics):
  Phase 4 spot-interrupted at i=50 (sim_day_index=50)
  engine_state.json was WRITTEN at i=50 per backtest.py:865
    'if i > 0 and (i == 50 or i % 100 == 0)'
    -> trades_so_far=610, status='running'
  trade_log_checkpoint.csv was NOT WRITTEN per pre-fix backtest.py:830
    'if i > 0 and i % 100 == 0 and self.closed_trades'  # pre-B1081
    -> i=50 does not match i%100==0
  Resume infra B1076 _load_resume_checkpoint requires BOTH files
  -> FileNotFoundError + Phase 4 partial work LOST

FIX (backtest.py:830):
  Match engine_state.json cadence:
    'if i > 0 and (i == 50 or i % 100 == 0) and self.closed_trades'
  Now both writers fire at the same boundary set.

LESSON (writer-reader pair pattern):
  Per `feedback_writer_reader_schema_contract_pin_test`: when
  multiple writers feed the same reader (here B1076 resume reads
  BOTH engine_state.json + trade_log_checkpoint.csv), their write
  cadences MUST be paired. Drift = silent data loss on early-
  interrupt scenarios.
"""
from __future__ import annotations

import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
BACKTEST_PY = REPO / "backtest" / "engine" / "backtest.py"


def test_b1081_pivot44_checkpoint_cadence_parity():
    """B1081 PIVOT #44: trade_log_checkpoint.csv write condition must
    match engine_state.json write condition. Both must include i==50."""
    content = BACKTEST_PY.read_text()
    # Engine state cadence (line ~865) must include 'i == 50'
    engine_state_pattern = r"(i\s*==\s*50\s+or\s+i\s*%\s*100\s*==\s*0)"
    engine_state_matches = re.findall(engine_state_pattern, content)
    assert len(engine_state_matches) >= 2, (
        f"B1081 PIVOT #44: expected BOTH trade_log_checkpoint write + "
        f"engine_state.json write to use 'i == 50 or i % 100 == 0' "
        f"cadence; found {len(engine_state_matches)} match(es). "
        f"Cadence drift = silent data loss on early-interrupt (B1079 "
        f"Phase 4 lost 610 trades at sim_day=50)."
    )


def test_b1081_pivot44_trade_log_checkpoint_includes_i50():
    """B1081 PIVOT #44: trade_log_checkpoint.csv write block specifically
    must include i==50 cadence."""
    content = BACKTEST_PY.read_text()
    # Find the block that writes trade_log_checkpoint.csv
    # Look for the 'if' guard immediately before checkpoint_path =
    # output_dir / "trade_log_checkpoint.csv"
    lines = content.splitlines()
    found_trade_log_block = False
    for idx, line in enumerate(lines):
        if 'trade_log_checkpoint.csv' in line and 'checkpoint_path' in line:
            # Walk backward to find the gating if statement
            for back_idx in range(idx, max(0, idx - 20), -1):
                if lines[back_idx].lstrip().startswith("if i > 0"):
                    assert "i == 50" in lines[back_idx], (
                        f"B1081 PIVOT #44: trade_log_checkpoint.csv write "
                        f"block at line {back_idx + 1} must include 'i == 50' "
                        f"in its gating condition. Found: "
                        f"{lines[back_idx].strip()}"
                    )
                    found_trade_log_block = True
                    break
            break
    assert found_trade_log_block, (
        "B1081 PIVOT #44: could not locate trade_log_checkpoint.csv "
        "write gating block to verify cadence"
    )


def test_b1081_pivot44_lineage_documented():
    """B1081 PIVOT #44 + Council 200 referenced in source."""
    content = BACKTEST_PY.read_text()
    assert "B1081 PIVOT #44" in content
    assert "Council 200" in content
    assert "B1079" in content  # source incident reference


def test_b1081_pivot44_b1076_resume_compat():
    """B1081 PIVOT #44: B1076 resume infra would now have valid
    checkpoint if interrupted at i=50 (vs pre-fix FileNotFoundError)."""
    content = BACKTEST_PY.read_text()
    # _load_resume_checkpoint still requires trade_log_checkpoint.csv
    assert 'trade_log_checkpoint.csv' in content
    # B1076 error chain remains intact (forward-compat)
    assert 'B1076 resume: trade_log_checkpoint.csv missing' in content


def test_b1081_pivot44_writer_reader_pair_documented():
    """B1081 PIVOT #44: comment block must document writer-reader pair
    rule (paired cadence)."""
    content = BACKTEST_PY.read_text()
    assert 'writer_reader_schema_contract_pin_test' in content, (
        "B1081 PIVOT #44: memory rule reference must be cited in fix "
        "lineage comment (per feedback_writer_reader_schema_contract_pin_test)"
    )
