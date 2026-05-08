"""Tests for scripts/_prefetch_utils.py - Tier J6 (Pass 53 v8h+1)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts._prefetch_utils import RESERVED_WIN, safe_filename_stem


def test_normal_ticker_unchanged() -> None:
    assert safe_filename_stem("AAPL") == "AAPL"


def test_dash_replaced_with_underscore() -> None:
    assert safe_filename_stem("BRK-B") == "BRK_B"


def test_reserved_name_appended_underscore() -> None:
    assert safe_filename_stem("CON") == "CON_"
    assert safe_filename_stem("PRN") == "PRN_"
    assert safe_filename_stem("AUX") == "AUX_"
    assert safe_filename_stem("NUL") == "NUL_"


def test_reserved_com_lpt_series() -> None:
    for i in range(1, 10):
        assert safe_filename_stem(f"COM{i}") == f"COM{i}_"
        assert safe_filename_stem(f"LPT{i}") == f"LPT{i}_"


def test_reserved_check_is_case_insensitive() -> None:
    assert safe_filename_stem("con") == "con_"
    assert safe_filename_stem("Con") == "Con_"


def test_reserved_set_is_complete() -> None:
    assert "CON" in RESERVED_WIN
    assert "COM5" in RESERVED_WIN
    assert "LPT9" in RESERVED_WIN
    assert "AAPL" not in RESERVED_WIN


def test_dash_then_reserved_check() -> None:
    assert safe_filename_stem("CO-N") == "CO_N"
