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
    match engine_state.json write condition. Both must include i==50.

    B1089 evolution: paired-writer block now uses _should_checkpoint flag
    computed ONCE from (sim_day OR time) triggers. The i==50 cadence is
    in _sim_day_trigger expression; both writers gated by same flag =
    parity preserved (even stronger than B1081 original)."""
    content = BACKTEST_PY.read_text()
    # B1081 invariant: sim_day cadence 'i == 50 or i % 100 == 0' MUST
    # appear in source (either as direct condition OR as _sim_day_trigger
    # expression per B1089 refactor).
    engine_state_pattern = r"(i\s*==\s*50\s+or\s+i\s*%\s*100\s*==\s*0)"
    engine_state_matches = re.findall(engine_state_pattern, content)
    assert len(engine_state_matches) >= 1, (
        f"B1081 PIVOT #44 (B1089-compatible): sim_day cadence "
        f"'i == 50 or i % 100 == 0' MUST appear in source "
        f"(now as _sim_day_trigger per B1089 paired-writer refactor); "
        f"found {len(engine_state_matches)} match(es). "
        f"Cadence drift = silent data loss on early-interrupt."
    )
    # B1089 evolution check: both writers must gate by SAME flag
    if "_should_checkpoint" in content:
        # Post-B1089: both writers gated by _should_checkpoint
        should_checkpoint_uses = content.count("if _should_checkpoint")
        assert should_checkpoint_uses >= 2, (
            f"B1089 paired-writer invariant: both CSV + engine_state writers "
            f"must gate on _should_checkpoint; found {should_checkpoint_uses} usages"
        )


def test_b1081_pivot44_trade_log_checkpoint_includes_i50():
    """B1081 PIVOT #44: trade_log_checkpoint.csv write block specifically
    must include i==50 cadence (directly OR via _sim_day_trigger per B1089).
    """
    content = BACKTEST_PY.read_text()
    lines = content.splitlines()
    found_trade_log_block = False
    for idx, line in enumerate(lines):
        if 'trade_log_checkpoint.csv' in line and 'checkpoint_path' in line:
            # Walk backward to find the gating if statement
            for back_idx in range(idx, max(0, idx - 30), -1):
                stripped = lines[back_idx].lstrip()
                if stripped.startswith("if i > 0") or \
                   stripped.startswith("if _should_checkpoint"):
                    # B1089-compatible: either direct cadence OR
                    # _should_checkpoint flag (which is computed from
                    # _sim_day_trigger that uses i==50 cadence)
                    gating_line = stripped
                    if "_should_checkpoint" in gating_line:
                        # Verify _sim_day_trigger uses i==50 in nearby code
                        nearby = "\n".join(lines[max(0, back_idx - 20):back_idx])
                        assert "i == 50" in nearby, (
                            f"B1081 PIVOT #44 + B1089: when CSV gates on "
                            f"_should_checkpoint, _sim_day_trigger must "
                            f"include i==50 in nearby code. Not found in "
                            f"lines {back_idx - 20}-{back_idx}"
                        )
                    elif "i == 50" not in gating_line:
                        raise AssertionError(
                            f"B1081 PIVOT #44: CSV write block at line "
                            f"{back_idx + 1} missing i==50 cadence. "
                            f"Found: {gating_line}"
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
