"""B938 (2026-06-19): pyramid tests for --no-tier2 escape hatch.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13 + Council 46 batch 2 commit 3
# per owner directive 2026-06-19 Option A.
"""
from __future__ import annotations

import pytest


def test_b938_no_tier2_flag_present_in_parser():
    """B938 CLI contract: --no-tier2 flag MUST exist."""
    from scripts.measure_fire_count import _build_arg_parser
    parser = _build_arg_parser()
    args = parser.parse_args(["--no-tier2"])
    assert hasattr(args, "no_tier2")
    assert args.no_tier2 is True


def test_b938_no_tier2_default_false():
    """B938 CLI contract: --no-tier2 defaults to False (does not disable when unspecified)."""
    from scripts.measure_fire_count import _build_arg_parser
    parser = _build_arg_parser()
    args = parser.parse_args([])
    assert args.no_tier2 is False


def test_b938_include_tier2_and_no_tier2_both_settable():
    """B938 CLI contract: --include-tier2 + --no-tier2 both parseable; precedence resolved in main."""
    from scripts.measure_fire_count import _build_arg_parser
    parser = _build_arg_parser()
    args = parser.parse_args(["--include-tier2", "--no-tier2"])
    assert args.include_tier2 is True
    assert args.no_tier2 is True
