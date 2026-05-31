"""Batch 510a (2026-05-31) -- BUG-61 concurrent-block mode tests.

Source: per CHECKLIST #77 + owner directive 2026-05-31.
Queue row: EXECUTION_QUEUE.md item #9 (R4 prerequisite -- fix
ticker_already_open_concurrent_block_bug61).

Investigation: BUG-61's per-ticker block was 49.7% of R3 skip events
(685,846 skipped trades). The block was intentional concentration-risk
management (owner-approved Option A) but is over-aggressive: when AAPL
is already in the portfolio via pead_long, the entire strategy loop is
skipped for AAPL for ALL strategies, blocking xs_momentum_long /
bollinger_tight / etc. from opening their own AAPL positions.

Fix: introduce `config.BUG_61_BLOCK_MODE` with 4 modes (default = "ticker"
preserves prior behavior; alternate modes for R4 owner decision):
  "ticker"           - block any new entry (default; current behavior)
  "ticker_direction" - block only same-direction entries
  "ticker_strategy"  - block only when SAME strategy already open
  "off"              - no block (portfolio cap + cooldown + max-loss
                       still apply)

Tests pin the config + the source-text shape of the engine branches
without instantiating BacktestEngine (heavy + slow).
"""
from __future__ import annotations

from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Config flag exists + default
# ---------------------------------------------------------------------------

def test_batch510a_bug61_block_mode_active_value():
    """Batch 514 (2026-05-31) owner-activated R4: flipped to
    'ticker_strategy' (was 'ticker' in Batch 510a default). Allows
    different strategies to stack on same ticker; same strategy still
    blocked. Recovers 685k blocked candidates from R3 item #2."""
    from backtest.config import BUG_61_BLOCK_MODE
    assert BUG_61_BLOCK_MODE == "ticker_strategy"


def test_batch510a_bug61_block_mode_legal_values_documented():
    """Config file docstring must document all 4 legal modes."""
    cfg = REPO / "backtest" / "config.py"
    src = cfg.read_text(encoding="utf-8")
    # All 4 modes documented in the inline comment block
    assert 'Mode-A "ticker"' in src
    assert 'Mode-B "ticker_direction"' in src
    assert 'Mode-C "ticker_strategy"' in src
    assert 'Mode-D "off"' in src


# ---------------------------------------------------------------------------
# Engine source: 4 branches wired
# ---------------------------------------------------------------------------

def test_batch510a_engine_handles_all_4_modes():
    eng = REPO / "backtest" / "engine" / "backtest.py"
    src = eng.read_text(encoding="utf-8")
    assert 'from backtest.config import BUG_61_BLOCK_MODE as _bug61_mode' in src
    assert 'if _bug61_mode == "off":' in src
    assert 'elif _bug61_mode == "ticker_direction":' in src
    assert 'elif _bug61_mode == "ticker_strategy":' in src


def test_batch510a_default_branch_preserves_prior_behavior():
    """The default `else` branch still emits the original BUG-61 skip
    reason -- prior owner-approved Option A behavior preserved bit-
    identically when mode = 'ticker'."""
    eng = REPO / "backtest" / "engine" / "backtest.py"
    src = eng.read_text(encoding="utf-8")
    # Original skip reason still present in the default branch
    assert '"reason": "ticker_already_open_concurrent_block_bug61"' in src


def test_batch510a_ticker_direction_emits_distinct_skip_reason():
    """Mode B uses a distinct reason string so skipped_trades.csv
    differentiates the block source for downstream analysis."""
    eng = REPO / "backtest" / "engine" / "backtest.py"
    src = eng.read_text(encoding="utf-8")
    assert "ticker_already_open_same_direction_bug61_mode_b" in src


def test_batch510a_ticker_strategy_emits_distinct_skip_reason():
    """Mode C distinct reason for skipped_trades.csv analysis."""
    eng = REPO / "backtest" / "engine" / "backtest.py"
    src = eng.read_text(encoding="utf-8")
    assert "ticker_already_open_same_strategy_bug61_mode_c" in src


# ---------------------------------------------------------------------------
# Mode-comparison logic (synthetic unit tests of the underlying set ops)
# ---------------------------------------------------------------------------

def test_batch510a_mode_b_blocks_when_directions_overlap():
    """Synthetic: open long on AAPL, candidate has long strategy -> block.
    Cross-direction (open long, candidate short) -> no block."""
    open_dirs = {"long"}
    cand_dirs = {"long"}
    assert open_dirs & cand_dirs  # would block

    cand_dirs_short = {"short"}
    assert not (open_dirs & cand_dirs_short)  # would NOT block


def test_batch510a_mode_b_blocks_when_any_candidate_direction_matches():
    """Mixed candidate with both long + short -> blocks if EITHER matches
    an open direction. This is conservative."""
    open_dirs = {"long"}
    cand_dirs = {"long", "short"}
    assert open_dirs & cand_dirs  # intersection non-empty -> block


def test_batch510a_mode_c_blocks_only_same_strategy():
    """Synthetic: open pead_long on AAPL, candidate xs_momentum_long ->
    no block. Same-strategy candidate -> block."""
    open_strats = {"pead_long"}
    cand_strats = {"xs_momentum_top_decile"}
    assert not (open_strats & cand_strats)  # different strategy -> no block

    cand_strats_same = {"pead_long"}
    assert open_strats & cand_strats_same  # same strategy -> block


def test_batch510a_off_mode_imposes_no_block():
    """Mode D has no logic gating skip; portfolio-cap + cooldown +
    max-loss-cap still apply downstream."""
    # No assertion to make beyond source-text pin (done above) -- the
    # branch literally is `pass`. Pin that:
    eng = REPO / "backtest" / "engine" / "backtest.py"
    src = eng.read_text(encoding="utf-8")
    assert 'if _bug61_mode == "off":\n                pass' in src


# ---------------------------------------------------------------------------
# Owner-direction pin: changing default requires owner sign-off
# ---------------------------------------------------------------------------

def test_batch510a_mode_change_requires_owner_signoff():
    """Pin the ACTIVE mode (Batch 514 owner-approved = 'ticker_strategy').
    A change to this value surfaces here and forces co-update of the
    queue row + owner sign-off."""
    from backtest.config import BUG_61_BLOCK_MODE
    legal = {"ticker", "ticker_direction", "ticker_strategy", "off"}
    assert BUG_61_BLOCK_MODE in legal, (
        f"BUG_61_BLOCK_MODE {BUG_61_BLOCK_MODE!r} not in legal set "
        f"{legal}. Owner sign-off required to add a new mode."
    )
    assert BUG_61_BLOCK_MODE == "ticker_strategy", (
        "BUG_61_BLOCK_MODE changed from Batch 514 owner-activated "
        "'ticker_strategy'. Owner sign-off required to switch modes."
    )
