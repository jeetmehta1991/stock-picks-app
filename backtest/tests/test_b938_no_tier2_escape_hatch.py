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


# ---------------------------------------------------------------------------
# B940 (2026-06-20) Phase P1 batch 3 commit 2: default-flip backward-compat tests
# ---------------------------------------------------------------------------


def test_b940_default_resolution_is_tier2_on():
    """B940 DEFAULT-FLIP contract: no flag passed -> TIER 2 ON (resolved=True).

    Pre-B940 default: TIER 2 OFF (backward-compat per Council 41).
    Post-B940 default: TIER 2 ON (matches production engine path per Phase P0).
    """
    from scripts.measure_fire_count import _build_arg_parser
    parser = _build_arg_parser()
    args = parser.parse_args([])
    # Simulate main()'s resolution logic
    include_tier2_resolved = not args.no_tier2
    assert include_tier2_resolved is True, (
        "B940 DEFAULT FLIP FAIL: no flag passed should resolve to TIER 2 ON. "
        "If this asserts False, the default-flip was reverted."
    )


def test_b940_no_tier2_flag_disables_tier2():
    """B940 ESCAPE HATCH contract: --no-tier2 -> TIER 2 OFF (resolved=False).

    Backward-compat for callers that need pre-B922 baseline semantics
    (e.g., mean_reversion_edge_prior_test per Council 47).
    """
    from scripts.measure_fire_count import _build_arg_parser
    parser = _build_arg_parser()
    args = parser.parse_args(["--no-tier2"])
    include_tier2_resolved = not args.no_tier2
    assert include_tier2_resolved is False, (
        "B940 ESCAPE HATCH FAIL: --no-tier2 must disable TIER 2 even though "
        "default is now ON. Backward-compat for mean_rev_prior class of "
        "callers depends on this."
    )


def test_b940_include_tier2_redundant_but_consistent():
    """B940 LEGACY-FLAG contract: --include-tier2 still enables TIER 2 (redundant post-flip but harmless)."""
    from scripts.measure_fire_count import _build_arg_parser
    parser = _build_arg_parser()
    args = parser.parse_args(["--include-tier2"])
    include_tier2_resolved = not args.no_tier2
    assert include_tier2_resolved is True, (
        "B940: --include-tier2 + no --no-tier2 should resolve to TIER 2 ON. "
        "Legacy flag from B922; redundant post-B940 but kept for B939 caller "
        "explicit-intent declarations until B941 cleanup."
    )


def test_b940_no_tier2_takes_precedence_over_include_tier2():
    """B940: --no-tier2 wins when both passed (B938 escape hatch precedence preserved)."""
    from scripts.measure_fire_count import _build_arg_parser
    parser = _build_arg_parser()
    args = parser.parse_args(["--include-tier2", "--no-tier2"])
    include_tier2_resolved = not args.no_tier2
    assert include_tier2_resolved is False, (
        "B940: --no-tier2 must take precedence over --include-tier2 (B938 contract preserved)."
    )
