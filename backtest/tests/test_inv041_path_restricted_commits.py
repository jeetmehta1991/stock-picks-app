"""INV-041 regression test (Pass 53 v8h+1 2026-05-10).

Pins down the path-restricted commit pattern in prefetch scripts so
future contributors cannot silently re-introduce the bug where
`git commit -m message` captures ALL staged files in the index
(including unrelated work from another concurrent session) under a
misleading per-script commit message.

The fix per INV-041: every `git_commit(message)` helper in scripts/
must use `git commit -m message -- <path1> [<path2> ...]` form which
restricts the commit to the named paths only.

This test scans scripts that have a `git_commit` function and asserts
the path-restricted form is used. New scripts should follow the same
pattern; the test will catch regressions.
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = ROOT / "scripts"

# Scripts in scope: prefetch_*.py with a git_commit function.
# Note: scripts that DON'T have a git_commit function (e.g. our newer
# prefetch_polygon_ohlcv_master.py) are out of scope - the user commits
# the data manually after the BG completes.
SCRIPTS_WITH_GIT_COMMIT = [
    "prefetch_sec_xbrl.py",
    "prefetch_polygon_benzinga.py",
    "prefetch_alphavantage_news.py",
    "prefetch_quiver.py",
    "prefetch_finnhub_news.py",
    "prefetch_finnhub_full.py",
    "prefetch_finnhub_social_sentiment.py",
    "prefetch_polygon_indicators.py",
    "prefetch_polygon_options_full.py",
    "prefetch_quiver_new_endpoints.py",
    "prefetch_stocktwits.py",
]


def _read(name: str) -> str:
    path = SCRIPTS_DIR / name
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def test_inv041_no_unrestricted_commit_in_scope_scripts():
    """No `git commit -m message` form without a `--` path delimiter.

    Detects the unrestricted form via regex: `subprocess.run([..., "git", "commit", "-m", ...])`
    that does NOT include `"--"` in the same call.
    """
    violations = []
    for name in SCRIPTS_WITH_GIT_COMMIT:
        src = _read(name)
        if not src:
            continue
        # Find every subprocess.run call that includes "git" + "commit"
        for m in re.finditer(
            r"subprocess\.run\(\s*\[[^\]]*\"git\"[^\]]*\"commit\"[^\]]*\][^)]*\)",
            src, re.DOTALL,
        ):
            chunk = m.group(0)
            # Must contain "--" delimiter for path restriction
            if '"--"' not in chunk:
                snippet = chunk[:150].replace("\n", " ")
                violations.append(f"{name}: unrestricted commit at offset {m.start()}: {snippet}")
    assert not violations, (
        "INV-041 regression: unrestricted git commit found in prefetch script. "
        "Use `git commit -m msg -- <path>` form to restrict to cache path:\n  - "
        + "\n  - ".join(violations)
    )


def test_inv041_sec_xbrl_uses_path_restricted_commit():
    """Pin: prefetch_sec_xbrl.py git_commit() must include `--` + CACHE_DIR."""
    src = _read("prefetch_sec_xbrl.py")
    assert src, "prefetch_sec_xbrl.py missing"
    # The fix landed: 'commit', '-m', message, '--', str(CACHE_DIR)
    assert '"--", str(CACHE_DIR)' in src or '"--",str(CACHE_DIR)' in src, (
        "prefetch_sec_xbrl.py git_commit() must use path-restricted commit "
        "with -- str(CACHE_DIR)"
    )


def test_inv041_polygon_benzinga_uses_path_restricted_commit():
    src = _read("prefetch_polygon_benzinga.py")
    assert src, "prefetch_polygon_benzinga.py missing"
    assert '"--", str(CACHE_ROOT)' in src or '"--",str(CACHE_ROOT)' in src, (
        "prefetch_polygon_benzinga.py git_commit() must use path-restricted commit "
        "with -- str(CACHE_ROOT)"
    )


def test_inv041_quiver_uses_path_restricted_commit():
    src = _read("prefetch_quiver.py")
    assert src, "prefetch_quiver.py missing"
    # Looks for commit invocation with -- + paths
    assert re.search(r'"git",\s*"commit",\s*"-m",\s*\w+,\s*"--"', src), (
        "prefetch_quiver.py git_commit() must use path-restricted commit form"
    )


def test_inv041_alphavantage_news_uses_path_restricted_commit():
    src = _read("prefetch_alphavantage_news.py")
    assert src, "prefetch_alphavantage_news.py missing"
    assert re.search(r'"git",\s*"commit",\s*"-m",\s*\w+,\s*"--"', src), (
        "prefetch_alphavantage_news.py git_commit() must use path-restricted commit form"
    )
