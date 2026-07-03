"""B1124 Test 6/10: borrow_ok blocking rate audit (Council 244).

RED-FIRST for Turn 1 + Turn 6 finding: `_short_borrow_trap_active` filter
suspected of blocking most SHORT candidates (ichimoku_cloud_breakdown
0 fires + macd_crossover_short 11 fires ~10x underfire).

Asserts filter exists AND that if a blocking-rate audit script has been
run, its verdict is <70% blocking (else 13 SHORT strategies systemically
under-fire).
"""
from __future__ import annotations

from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent


def test_short_borrow_trap_filter_exists_in_source():
    """`_short_borrow_trap_active` filter must exist in screener or engine."""
    for source_file in [
        REPO / "backtest" / "signals" / "screener.py",
        REPO / "backtest" / "engine" / "backtest.py",
        REPO / "backtest" / "data" / "smart_money.py",
    ]:
        if source_file.exists():
            content = source_file.read_text(encoding="utf-8", errors="ignore")
            if "short_borrow_trap" in content or "borrow_ok" in content:
                return
    pytest.fail(
        "borrow_ok / _short_borrow_trap_active filter reference not found in "
        "screener/engine/smart_money. Filter suspected of blocking 13 SHORT "
        "strategies per Turn 1 + Turn 6 findings."
    )


def test_short_strategy_registry_count_bounded():
    """SHORT strategy count via CSV should be substantial (>=40).

    If SHORT strategies are systemically starved, the practical count of
    firing SHORT strategies drops. Registry count is a floor check.
    """
    import pandas as pd

    csv = REPO / "output_batch_A_150" / "phase_1_quiet_fire_investigation.csv"
    if not csv.exists():
        pytest.skip("CSV missing")
        return
    df = pd.read_csv(csv)
    short_count = (df["direction"] == "short").sum()
    assert short_count >= 40, (
        f"SHORT strategy count in CSV = {short_count}; expected >= 40. "
        f"If dropped, may indicate silent SHORT deletion."
    )


def test_borrow_ok_audit_report_documented_when_present():
    """When borrow_ok blocking-rate audit runs, its verdict is documented."""
    audit_report_paths = [
        REPO / "output_audit" / "borrow_ok_blocking_rate_audit.json",
        REPO / "output_batch_A_150" / "borrow_ok_audit.json",
    ]
    existing = [p for p in audit_report_paths if p.exists()]
    if not existing:
        pytest.skip(
            "borrow_ok blocking-rate audit not yet run (S1125 pending Council 238 plan). "
            "When B1125 lands, this test asserts blocking_rate < 0.70."
        )
        return
    import json
    for report in existing:
        data = json.loads(report.read_text(encoding="utf-8"))
        blocking_rate = data.get("blocking_rate")
        if blocking_rate is not None:
            assert blocking_rate < 0.70, (
                f"borrow_ok blocking rate = {blocking_rate:.2%}; must be <70% "
                f"to avoid systemic SHORT under-fire. Root cause per Turn 1 + Turn 6."
            )


def test_ichimoku_breakdown_short_pattern_in_csv():
    """CSV must record ichimoku_cloud_breakdown = 0 fires (Turn 1 finding)."""
    import pandas as pd

    csv = REPO / "output_batch_A_150" / "phase_1_quiet_fire_investigation.csv"
    if not csv.exists():
        pytest.skip("CSV missing")
        return
    df = pd.read_csv(csv)
    row = df[df["strategy_name"] == "ichimoku_cloud_breakdown"]
    if row.empty:
        pytest.skip("ichimoku_cloud_breakdown not in CSV (may be renamed)")
        return
    n_fires = int(row.iloc[0]["n_fires"])
    assert n_fires <= 3, (
        f"ichimoku_cloud_breakdown expected <=3 fires per Turn 1 finding "
        f"(borrow_ok suspect); got {n_fires}."
    )
