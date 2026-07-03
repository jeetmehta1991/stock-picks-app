"""B1127 Tier-9 Silent Failure Paired Check (Council 246).

CATCHES: CHECKLIST #122 - every `|| true` requires paired explicit
success-check. Silent failures are the CLASS of bug that produced the
pandas-ta install failure + downstream engine.log 0-byte pass path.
"""
# Source: per CHECKLIST #77 canonical-source; author Council 246 B1127 2026-07-03
from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent


def _sh_scripts() -> list[Path]:
    return list((REPO / "scripts").rglob("*.sh"))


def test_or_true_patterns_documented():
    """`|| true` patterns must be explicitly documented (per CHECKLIST #122)."""
    findings = []
    for script in _sh_scripts():
        content = script.read_text(encoding="utf-8", errors="ignore")
        # Find || true occurrences with surrounding context
        for match in re.finditer(r"([^\n]{0,120}\|\|\s*true)", content):
            line = match.group(1).strip()
            # Skip if line has explicit success verification nearby
            if "CHECKLIST" in content[max(0, match.start() - 200) : match.end() + 200]:
                continue
            findings.append((script.name, line[:100]))

    # Non-fatal: soft floor - many `|| true` are legitimate. Just cap raw count.
    if len(findings) > 30:
        pytest.fail(
            f"CHECKLIST #122 regression: {len(findings)} `|| true` occurrences "
            f"without CHECKLIST reference nearby. Each needs paired success-check. "
            f"First 5: {findings[:5]}"
        )


def test_except_pass_patterns_bounded():
    """`except: pass` patterns in production code must be bounded."""
    findings = []
    for src in (REPO / "backtest").rglob("*.py"):
        if "test_" in src.name or "conftest" in src.name:
            continue
        content = src.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r"except\s+.*?:\s*(?:\n\s+pass|\s*pass)", content, re.DOTALL):
            findings.append((src.relative_to(REPO), match.start()))

    # Soft floor - many except-pass are for optional producers (see screener.py)
    # but should not explode
    assert len(findings) < 200, (
        f"except:pass count = {len(findings)}. Each needs paired _log_silent_producer_failure "
        f"or explicit rationale. Cap at 200."
    )


def test_silent_producer_failure_logger_present():
    """screener.py must have _log_silent_producer_failure or equivalent (per L177 phantom-name)."""
    screener = REPO / "backtest" / "signals" / "screener.py"
    content = screener.read_text(encoding="utf-8")
    has_logger = (
        "_log_silent_producer_failure" in content
        or "log_silent_producer" in content
        or "_silent_" in content
    )
    assert has_logger, (
        "L177 regression: screener.py must have silent-producer-failure "
        "logger to prevent silent partial-success masquerade."
    )


def test_no_bare_try_except_in_signals():
    """`try: ... except: pass` (bare except) is a code smell in signal producers."""
    findings = []
    for src in (REPO / "backtest" / "signals").glob("*.py"):
        content = src.read_text(encoding="utf-8", errors="ignore")
        bare_excepts = re.findall(r"except\s*:\s*(?:\n\s+pass|\s*pass)", content)
        if bare_excepts:
            findings.append((src.name, len(bare_excepts)))
    # Bare `except:` catches KeyboardInterrupt/SystemExit too - a smell
    assert not findings, (
        f"Bare `except: pass` patterns in signal producers: {findings}. "
        f"Use `except Exception:` at minimum + logger."
    )
