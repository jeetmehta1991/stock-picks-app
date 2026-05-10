"""DEC-497 + Sprint 0A.8 NO-LIVE-API HARD CUT regression test.

Pass 53 v8h+1 2026-05-10: Stage 2 backtest must NEVER call live APIs at runtime.
Live HTTP calls (requests.get/post/Session/etc., httpx, urllib) are permitted
ONLY in:
  - scripts/prefetch_*.py (prefetch jobs that populate data_prefetch/)
  - scripts/* one-off utilities
  - backtest/agents/pipeline.py (Anthropic LLM API; gated by --run-agents)

Forbidden everywhere else under backtest/data/, backtest/signals/,
backtest/engine/, backtest/results/.

Failure mode: pre-Phase-1A wiring landed live-API fallback paths in macro.py,
smart_money.py, sentiment.py. This test gates against future regressions
where contributors silently re-introduce a live-fallback branch.
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Modules that are runtime hot-path; MUST NOT import or call live HTTP libs.
RUNTIME_HOT_PATHS = [
    ROOT / "data",
    ROOT / "signals",
    ROOT / "engine",
    ROOT / "results",
]

# Allowlist: explicit per-file exceptions (pin down with reason).
ALLOWLIST = {
    # backtest/data/cache.py is permitted to maintain a session for legacy
    # paths; assert no actual call sites exist by inspection in PR review.
    # (No actual entries currently; placeholder for owner-approved exceptions.)
}

LIVE_HTTP_PATTERNS = [
    re.compile(r"^\s*import\s+requests\b", re.MULTILINE),
    re.compile(r"^\s*from\s+requests\b", re.MULTILINE),
    re.compile(r"^\s*import\s+httpx\b", re.MULTILINE),
    re.compile(r"^\s*import\s+urllib\.request\b", re.MULTILINE),
    re.compile(r"\brequests\.(get|post|put|delete|head|patch|Session)\s*\(", re.MULTILINE),
    re.compile(r"\bhttpx\.(get|post|put|delete|head|patch|Client|AsyncClient)\s*\(", re.MULTILINE),
    re.compile(r"\burllib\.request\.urlopen\s*\(", re.MULTILINE),
]


def test_no_live_http_in_backtest_runtime():
    """Walk runtime hot-paths; assert no live-HTTP imports or call sites.

    Joint: DEC-497 (NO-LIVE-API HARD CUT), Sprint 0A.8 (refactor implementation),
    DEC-503 (test pyramid - this is regression layer).
    """
    violations = []
    for root in RUNTIME_HOT_PATHS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if str(path) in ALLOWLIST:
                continue
            try:
                src = path.read_text(encoding="utf-8")
            except Exception:
                continue
            # Strip out single-line comments to avoid false positives in docstrings/comments
            # (basic heuristic; sufficient for current code style).
            src_no_comments = re.sub(r"#[^\n]*", "", src)
            for pat in LIVE_HTTP_PATTERNS:
                m = pat.search(src_no_comments)
                if m:
                    rel = path.relative_to(ROOT.parent)
                    violations.append(f"{rel}: matched /{pat.pattern}/ at offset {m.start()}")

    assert not violations, (
        "DEC-497 NO-LIVE-API HARD CUT violations found in runtime hot-paths. "
        "Live HTTP calls belong in scripts/prefetch_*.py only. Violations:\n  - "
        + "\n  - ".join(violations)
    )


def test_macro_module_no_requests_import():
    """Specific assert: backtest/data/macro.py has no `import requests`.

    Pin down the Sprint 0A.8 refactor result so future merges cannot silently
    re-introduce the live FRED API fallback.
    """
    src = (ROOT / "data" / "macro.py").read_text(encoding="utf-8")
    src_no_comments = re.sub(r"#[^\n]*", "", src)
    assert "import requests" not in src_no_comments, (
        "backtest/data/macro.py must not import requests at runtime "
        "(DEC-497 HARD CUT). Live FRED/ALFRED calls live in scripts/prefetch_*.py."
    )


def test_smart_money_module_no_requests_import():
    """Specific assert: backtest/data/smart_money.py has no `import requests`."""
    src = (ROOT / "data" / "smart_money.py").read_text(encoding="utf-8")
    src_no_comments = re.sub(r"#[^\n]*", "", src)
    assert "import requests" not in src_no_comments, (
        "backtest/data/smart_money.py must not import requests at runtime "
        "(DEC-497 HARD CUT). Live Quiver calls live in scripts/prefetch_quiver*.py."
    )


def test_sentiment_module_no_requests_import():
    """Specific assert: backtest/data/sentiment.py has no `import requests`."""
    src = (ROOT / "data" / "sentiment.py").read_text(encoding="utf-8")
    src_no_comments = re.sub(r"#[^\n]*", "", src)
    assert "import requests" not in src_no_comments, (
        "backtest/data/sentiment.py must not import requests at runtime "
        "(DEC-497 HARD CUT). Sentiment data lives in prefetched parquet caches."
    )


def test_quiver_get_dead_function_removed():
    """Pin down: smart_money._quiver_get function REMOVED in Sprint 0A.8."""
    src = (ROOT / "data" / "smart_money.py").read_text(encoding="utf-8")
    assert "def _quiver_get(" not in src, (
        "backtest/data/smart_money.py::_quiver_get function must remain removed "
        "(Sprint 0A.8 NO-LIVE-API HARD CUT). It was a dead live-API fallback path."
    )
