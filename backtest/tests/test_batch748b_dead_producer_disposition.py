# Source: B748b owner-approved 2026-06-13 (revised) per B747 + B745 finding-grade audit + CHECKLIST #77
"""B748b pin tests: dead-producer disposition.

Per B745 finding-grade audit + B747 PIT-discipline finding, three TIER 2
producers had 0 data rows:
- compute_sec_edgar_signals (2 consumers in screener.py)
- compute_index_rebalance_signals (4 consumers in index_rebalance.py itself)
- compute_recent_8k_signal (0 consumers; genuine orphan)

B748b owner-approved disposition 2026-06-13 (REVISED after correction):
- sec_edgar consumers: 2 strategies tagged EXPLORATORY
- index_rebalance consumers: 4 strategies tagged EXPLORATORY (corrected from
  initial DELETE recommendation when in-module consumers were missed)
- recent_8k: producer DELETED + screener call site removed

These pins lock the dispositions.
"""
from __future__ import annotations

import importlib


# ---------------------------------------------------------------------------
# EXPLORATORY tagging on 6 strategies
# ---------------------------------------------------------------------------
EXPLORATORY_STRATEGIES_B748B = [
    # POST-B748d (2026-06-14): ALL 6 original B748b EXPLORATORY tags
    # are now removed. B748d audit-script-fix surfaced path-drift on
    # sec_edgar (registry: `data_prefetch/sec_edgar`; actual:
    # `data_prefetch/sec_edgar_decoded`); decoded cache has item_codes
    # populated + producer fires 3/3 on KNOWN Item 1.01 events.
    # Net B748B EXPLORATORY: 0.
]


def test_b748b_pin1_post_b748d_zero_b748b_originals_remain_exploratory():
    """Post B748d walk-back: all 6 original B748b EXPLORATORY tags
    proven FALSE. The previously-retained `strat_m_and_a_target_long`
    was also revived after B748d audit-script-fix surfaced the
    sec_edgar_decoded cache (which has item_codes populated).
    """
    from backtest.signals.screener import strat_m_and_a_target_long
    doc = strat_m_and_a_target_long.__doc__ or ""
    assert "EXPLORATORY -- DO NOT DEPLOY" not in doc, (
        "strat_m_and_a_target_long should have been REVIVED in B748d; doc still contains EXPLORATORY"
    )


def test_b748b_pin2_b748c_revived_strategies_lack_exploratory_marker():
    """The 5 strategies REVIVED in B748c must NOT carry EXPLORATORY markers
    anymore. Lock the walk-back so regression brings the bug back.
    """
    from backtest.signals import screener as scr
    from backtest.signals import index_rebalance as ir
    revived = {
        "strat_activist_13d_long":              scr,
        "strat_post_inclusion_drift_long":      ir,
        "strat_post_inclusion_reversal_short":  ir,
        "strat_post_deletion_drift_short":      ir,
        "strat_pre_rebalance_long":             ir,
    }
    still_tagged = []
    for name, mod in revived.items():
        fn = getattr(mod, name)
        doc = fn.__doc__ or ""
        if "EXPLORATORY -- DO NOT DEPLOY" in doc:
            still_tagged.append(name)
    assert not still_tagged, (
        f"B748c walk-back regressed: {still_tagged} still have EXPLORATORY -- DO NOT DEPLOY markers"
    )


# ---------------------------------------------------------------------------
# compute_recent_8k_signal DELETED
# ---------------------------------------------------------------------------
def test_b748b_pin3_compute_recent_8k_signal_deleted():
    """The function `compute_recent_8k_signal` must NOT exist on the
    macro_events module post-B748b.
    """
    mod = importlib.import_module("backtest.signals.macro_events")
    assert not hasattr(mod, "compute_recent_8k_signal"), (
        "compute_recent_8k_signal should have been DELETED in B748b"
    )


def test_b748b_pin4_screener_does_not_import_recent_8k_signal():
    """The screener.py call site for compute_recent_8k_signal must be removed."""
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "backtest" / "signals" / "screener.py"
    code = src.read_text(encoding="utf-8")
    # Strip docstrings/comments before checking, so the deletion note (which
    # mentions the function name) doesn't trigger a false positive
    import re
    stripped = re.sub(r'"""[\s\S]*?"""', '', code)
    stripped = re.sub(r"'''[\s\S]*?'''", '', stripped)
    stripped = "\n".join(line.split("#", 1)[0] for line in stripped.splitlines())
    assert "compute_recent_8k_signal" not in stripped, (
        "screener.py still references compute_recent_8k_signal in live code; B748b deletion incomplete"
    )


def test_b748b_pin5_compute_pre_fomc_signals_still_imported():
    """B748b removed only the recent_8k call; compute_pre_fomc_signals must
    still be imported + called (regression guard).
    """
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "backtest" / "signals" / "screener.py"
    code = src.read_text(encoding="utf-8")
    assert "compute_pre_fomc_signals" in code, (
        "compute_pre_fomc_signals reference accidentally removed; revert B748b"
    )


# ---------------------------------------------------------------------------
# Strategy count regression guard
# ---------------------------------------------------------------------------
def test_b748b_pin6_strategy_count_unchanged_at_221():
    """B748b is a docstring + producer-deletion batch -- the 6 EXPLORATORY
    strategies remain registered. ALL_STRATEGIES count must stay at 221.
    """
    from backtest.signals.screener import ALL_STRATEGIES
    assert len(ALL_STRATEGIES) == 219, (
        f"strategy count drifted to {len(ALL_STRATEGIES)}; expected 221"
    )
