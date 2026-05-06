"""Canonical facts alignment test.

Enforces that every forward-looking doc agrees with the canonical values stated
in CANONICAL_FACTS.md. When a doc drifts (e.g. someone writes "6 agents" or
"36/36 must pass" or "274 signals"), this test fails and identifies the
file:line so it can be corrected.

Historical narratives (AUDIT.md, archive/, rendered HTML, etc.) are excluded
per L143 (don't rewrite history). Forward-looking docs that intentionally use
a scope-narrow value (e.g. EXPLANATION.md saying "~220 technical signals" — correct
for Category 1 only) can be annotated with:

    <!-- canonical-fact-scope: F-NNN <reason> -->

placed on the line immediately preceding the value, to signal "this scope is
intentional".

Run: pytest backtest/tests/test_canonical_facts_alignment.py -v
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, NamedTuple

REPO_ROOT = Path(__file__).resolve().parents[2]


# Files excluded from alignment checks per L143 (historical narratives, archives,
# rendered run artifacts, the canonical file itself, the alignment test, and
# helpers that reference stale phrasing for traceability).
EXCLUDED_PATHS = (
    "AUDIT.md",
    "PROJECT_PLAN_ARCHIVE.md",
    "LEARNINGS.md",
    "archive/",
    ".archive/",
    "output_1b_dashboard.html",
    "analysis_dashboard_1b.html",
    "analysis_dashboard.html",
    "CANONICAL_FACTS.md",
    "test_canonical_facts_alignment.py",
    "STRATEGY_REGISTER.md",  # canonical layered roster — uses raw integers per scope intentionally
    "TRADING_RULES_AND_INFORMATION.md",  # canonical signal universe — uses raw integers per scope
    "AUDIT_TRIAGE.md",  # historical pass-specific decision tracking
    "AUDIT_INDEX.md",  # historical decision register
)

SCOPE_ANNOTATION_RE = re.compile(
    r"<!--\s*canonical-fact-(scope|historical):\s*F-\d+\s+.*?\s*-->",
    re.IGNORECASE,
)

# Lines that document stale phrasing as historical context (rather than asserting
# it as current) are allowed without explicit annotation when they contain
# explicit historical markers near the match.
HISTORICAL_CONTEXT_RE = re.compile(
    r"\b(prior(?:\s+wording)?|historical(?:ly)?|previously|"
    r"was\s+a\s+simplif|no\s+longer\s+accurate|"
    r"retired|stale|was\s+wrong|"
    r"pre-Pattern-2|conceptual\s+role|reflected\s+pre-)",
    re.IGNORECASE,
)


class Drift(NamedTuple):
    fact_id: str
    file: str
    line_no: int
    line: str
    reason: str


def _iter_forward_looking_docs() -> Iterator[Path]:
    """Yield Markdown + Python files that should align to CANONICAL_FACTS.md."""
    for ext in ("*.md", "*.py"):
        for p in REPO_ROOT.rglob(ext):
            rel = p.relative_to(REPO_ROOT).as_posix()
            if any(excl in rel for excl in EXCLUDED_PATHS):
                continue
            if "tests/" in rel and p.name != "test_canonical_facts_alignment.py":
                # Other tests are scope-bounded — don't enforce on them
                continue
            if "vendored/" in rel:
                continue
            yield p


def _scan(pattern: re.Pattern, fact_id: str, reason: str) -> list[Drift]:
    """Return all forward-looking doc lines matching `pattern` that lack scope annotation.

    A match is excluded if the line OR the immediately preceding line contains either:
      (a) `<!-- canonical-fact-scope: F-NNN reason -->` annotation
      (b) `<!-- canonical-fact-historical: F-NNN reason -->` annotation
      (c) an inline historical-context marker (e.g. "prior", "historically", "retired",
          "pre-Pattern-2", "was a simplification") that signals the stale phrasing is
          being documented, not asserted as current
    """
    drifts: list[Drift] = []
    for path in _iter_forward_looking_docs():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines, start=1):
            if not pattern.search(line):
                continue
            prev = lines[i - 2] if i >= 2 else ""
            if SCOPE_ANNOTATION_RE.search(line) or SCOPE_ANNOTATION_RE.search(prev):
                continue
            if HISTORICAL_CONTEXT_RE.search(line):
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            drifts.append(Drift(fact_id, rel, i, line.strip()[:200], reason))
    return drifts


# ---------------------------------------------------------------------------
# F-001 — Agent count
# ---------------------------------------------------------------------------

# Forbidden: bare "6 agents" / "6-agent pipeline" / "all 6 TradingAgents" / "six agents"
# in forward-looking docs. Acceptable: any reference to 11, 12, "11 active", "11-active-agent",
# or scope-annotated mention.
# The negative lookbehind (?<![\d.]) prevents false positives when "6" is part of a
# section number like "§2.6 Agent overlay" or "11.6 agents-of-record".
_F001_PATTERN = re.compile(
    r"(?<![\d.])\b("
    r"6[-\s]agents?\b"
    r"|6[-\s]agent\s+pipeline"
    r"|all\s+6\s+TradingAgents"
    r"|six\s+agents"
    r"|6\s+TA\s+agents"
    r")\b",
    re.IGNORECASE,
)


def test_f001_agent_count_no_stale_six():
    """F-001: no doc may state '6 agents' (we use 11 active + 1 Reflection)."""
    drifts = _scan(
        _F001_PATTERN,
        fact_id="F-001",
        reason="Agent count is 11 active + 1 Reflection (canonical). Replace '6 agents' "
        "with '11 active agents per DEC-057' or 'all 11 active TradingAgents'.",
    )
    assert not drifts, _format(drifts)


# ---------------------------------------------------------------------------
# F-003 — Signal count
# ---------------------------------------------------------------------------

# Forbidden: bare "274 signals" / "274 signal fields" — retired phrasing.
# Acceptable: scope-narrow with annotation, or "~270-280 total" / "~220 technical".
_F003_PATTERN = re.compile(
    r"\b274\s+signals?\b"
    r"|\b274\s+signal\s+fields?\b",
    re.IGNORECASE,
)


def test_f003_signal_count_no_stale_274():
    """F-003: '274 signals' is retired phrasing — disambiguate per F-003."""
    drifts = _scan(
        _F003_PATTERN,
        fact_id="F-003",
        reason="'274 signals' is retired (stale point-in-time count). Use "
        "'~220 technical signals (Category 1)' or '~270-280 total signals across "
        "6 categories' per CANONICAL_FACTS.md F-003.",
    )
    assert not drifts, _format(drifts)


# ---------------------------------------------------------------------------
# F-007 — Test count
# ---------------------------------------------------------------------------

# Forbidden: "36/36 must pass" / "36/36 tests" — frozen baseline; test count grows.
_F007_PATTERN = re.compile(
    r"\b36/36\s+(must\s+pass|tests|passing|in\s+test)",
    re.IGNORECASE,
)


def test_f007_test_count_no_frozen_36():
    """F-007: '36/36 must pass' is a frozen Pass-50 baseline — test count grows."""
    drifts = _scan(
        _F007_PATTERN,
        fact_id="F-007",
        reason="'36/36 must pass' is frozen at Pass-50 baseline; current count is ~102 "
        "and grows over time. Replace with 'all tests must pass (run pytest -q to verify)'.",
    )
    assert not drifts, _format(drifts)


# ---------------------------------------------------------------------------
# F-002 — Strategy count (lighter check: bare '60 strategies' / '72 strategies'
# without scope qualifier in forward-looking docs)
# ---------------------------------------------------------------------------

# Forbidden: bare claim "60 strategies" / "72 strategies" without scope-narrowing context.
# A line is OK if it ALSO contains a scope marker (Layer N, baseline, PROJECT_PLAN, classes,
# variants, delta, code has X) OR the historical-context marker.
_F002_INTEGER_PATTERN = re.compile(
    r"\b(60|72)\s+strateg(y|ies)\b",
    re.IGNORECASE,
)
_F002_SCOPE_MARKER = re.compile(
    r"\b(Layer\s*[1-4]|baseline|PROJECT_PLAN|class(es)?|variant|delta|"
    r"should\s+be|code\s+has|mentions?|specifies?|hardcoded|prints?|docstring|"
    r"~108|~109|~117|~119|108-|109-|117-|119-|108\+|"
    r"long\s+\+\s+short|long\+short)\b",
    re.IGNORECASE,
)


def test_f002_strategy_count_no_bare_integer():
    """F-002: claims of '60 strategies' or '72 strategies' need scope qualifier in same line."""
    drifts: list[Drift] = []
    for path in _iter_forward_looking_docs():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines, start=1):
            if not _F002_INTEGER_PATTERN.search(line):
                continue
            prev = lines[i - 2] if i >= 2 else ""
            if SCOPE_ANNOTATION_RE.search(line) or SCOPE_ANNOTATION_RE.search(prev):
                continue
            if HISTORICAL_CONTEXT_RE.search(line):
                continue
            if _F002_SCOPE_MARKER.search(line):
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            drifts.append(
                Drift(
                    "F-002",
                    rel,
                    i,
                    line.strip()[:200],
                    "Bare 'N strategies' lacks scope qualifier (Layer 1, baseline, classes, "
                    "etc). Reference the layered roster (~108-133 classes per F-002) or add "
                    "explicit scope.",
                )
            )
    assert not drifts, _format(drifts)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _format(drifts: list[Drift]) -> str:
    if not drifts:
        return ""
    lines = [
        "",
        f"Found {len(drifts)} canonical-fact alignment drift(s):",
        "",
    ]
    by_fact: dict[str, list[Drift]] = {}
    for d in drifts:
        by_fact.setdefault(d.fact_id, []).append(d)
    for fact_id, items in sorted(by_fact.items()):
        lines.append(f"=== {fact_id} ===")
        lines.append(f"  Reason: {items[0].reason}")
        lines.append("")
        for d in items:
            lines.append(f"  {d.file}:{d.line_no}")
            lines.append(f"      > {d.line}")
        lines.append("")
    lines.append(
        "Fix by either: (a) updating the doc to use canonical phrasing, or "
        "(b) adding `<!-- canonical-fact-scope: F-NNN <reason> -->` on the "
        "preceding line if the scope-narrow value is intentional."
    )
    return "\n".join(lines)


def test_canonical_facts_md_exists():
    """The canonical facts file itself must exist (sanity)."""
    assert (REPO_ROOT / "CANONICAL_FACTS.md").is_file()
