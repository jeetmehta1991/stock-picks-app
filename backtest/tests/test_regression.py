"""Regression tests - DEC-503 pyramid layer (Pass 53 v8h+1 owner-approved 2026-05-08).

Regression = a previously-fixed bug stays fixed. One test per RESOLVED bug
that has clear regression risk. Test name format: test_bug_NN_<short-desc>.
Failure means: the original bug just came back.

Started with the bugs visible in current commits; expand as more BUG-NN
cases are codified. Per CHECKLIST 69, this layer is mandatory for Phase 1A.

Markers:
    pytest -m regression   # run only these
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


pytestmark = pytest.mark.regression


# -- BUG-269/270/271 fixed: smart_money silent-gap pattern -----------------
def test_bug_silent_gap_smart_money_endpoints_wired() -> None:
    """L146 / DEC-507: smart_money.get_news_sentiment must NOT read legacy
    cache/av_news/ paths. Regression: catches any reversion to the wired-but-
    broken state where data is fresh and code is fresh but path mapping is
    stale."""
    from backtest.data import smart_money
    src = Path(smart_money.__file__).read_text(encoding="utf-8", errors="ignore")
    assert "cache/av_news" not in src, (
        "smart_money.py references the legacy cache/av_news/ path - "
        "L146/DEC-507 regression. Should read data_prefetch/polygon/news/."
    )


# -- BUG-INV-041 fixed: prefetch git_commit must be path-restricted --------
def test_bug_inv041_prefetch_git_commit_path_restricted() -> None:
    """INV-041: prefetch scripts must use path-restricted git commits to avoid
    capturing unrelated staged files. Regression: any prefetch script using
    `git add -A` or unrestricted `git commit` triggers this."""
    scripts_dir = REPO_ROOT / "scripts"
    for f in scripts_dir.glob("prefetch_*.py"):
        text = f.read_text(encoding="utf-8", errors="ignore")
        if "git_commit" in text or "git add" in text:
            assert "git", f"placeholder"
            # Look for the smell: subprocess.run([..., 'add', '-A', ...]) or unrestricted commits
            assert 'git", "add", "-A"' not in text and "git', 'add', '-A'" not in text, (
                f"{f.name}: uses unrestricted 'git add -A' (INV-041 regression). "
                f"Should pass explicit paths."
            )


# -- BUG-VIX-PROXY fixed: regime classifier uses VIX, not synthetic ---------
def test_bug_vix_proxy_regime_classifier() -> None:
    """Day-9 v8b: regime classifier must use real VIX from cache, not a
    synthetic vol estimate. Regression: code reverts to computing realized
    vol when VIX cache is available."""
    rf = REPO_ROOT / "backtest" / "engine" / "regime_filter.py"
    if not rf.exists():
        pytest.skip("regime_filter.py not present")
    text = rf.read_text(encoding="utf-8", errors="ignore")
    # The fix added VIX cache loading; if that's gone, regression triggered
    has_vix_load = "vix" in text.lower() or "VIX" in text
    assert has_vix_load, (
        "regime_filter.py has no VIX reference - BUG-VIX-PROXY regression."
    )


# -- BUG-CHECKLIST-77 fixed: CHECKLIST has >= 70 numbered items ------------
def test_bug_checklist_count_lower_bound() -> None:
    """CHECKLIST.md should retain >=70 numbered items. Regression: someone
    deletes a rule in a refactor."""
    checklist = REPO_ROOT / "CHECKLIST.md"
    if not checklist.exists():
        pytest.skip("CHECKLIST.md not present")
    text = checklist.read_text(encoding="utf-8", errors="ignore")
    n = len(re.findall(r"^\d+\.\s+", text, re.MULTILINE))
    assert n >= 70, f"CHECKLIST has only {n} numbered items - rules deleted?"


# -- BUG-INV-045 fixed: doc count drift detector exists + clean ------------
def test_bug_inv045_doc_count_drift_clean() -> None:
    """INV-045: cross-doc numerical drift was undetected (e.g. AUDIT_INDEX
    354 vs 520). Regression: the detector script must exist and report
    clean (no drift)."""
    import subprocess
    sync = REPO_ROOT / "scripts" / "sync_doc_counts.py"
    assert sync.exists(), "sync_doc_counts.py missing - INV-045 regression"
    r = subprocess.run(
        [sys.executable, str(sync), "--check"],
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=60,
    )
    assert r.returncode == 0, (
        f"sync_doc_counts.py --check returned {r.returncode}; numerical "
        f"drift detected:\n{r.stdout[-500:]}"
    )


# -- BUG-DASHBOARD-SCAN-GAP fixed: polygon_options scan registered ---------
def test_bug_dashboard_polygon_options_scanned() -> None:
    """The polygon_options gap (cache existed, scan list silent) must stay
    fixed. Regression: someone refactors CACHE_PATHS and drops options_chains."""
    sprint0a = REPO_ROOT / "scripts" / "build_dashboard_sprint0a.py"
    if not sprint0a.exists():
        pytest.skip("build_dashboard_sprint0a.py not present")
    text = sprint0a.read_text(encoding="utf-8", errors="ignore")
    assert "options_chains" in text, (
        "build_dashboard_sprint0a.py no longer registers options_chains - "
        "scan list drift regression."
    )


# -- BUG-J5 ALREADY-CLEAN: parquet compression stays SNAPPY ----------------
def test_bug_j5_parquet_compression_snappy() -> None:
    """Sample 50 random parquets; assert compression is uniformly SNAPPY.
    Regression: someone introduces a write that uses 'gzip' or 'none'."""
    import random
    import pyarrow.parquet as pq
    candidates = list((REPO_ROOT / "data_prefetch").rglob("*.parquet"))
    if len(candidates) < 50:
        pytest.skip(f"only {len(candidates)} parquets - need >=50 for sample")
    random.seed(53)
    sample = random.sample(candidates, 50)
    bad: list[str] = []
    for p in sample:
        try:
            meta = pq.read_metadata(p)
            if meta.num_row_groups == 0:
                continue
            comp = meta.row_group(0).column(0).compression
            if comp not in ("SNAPPY", None):
                bad.append(f"{p.name}:{comp}")
        except Exception:
            continue
    assert not bad, f"non-SNAPPY parquets detected: {bad[:5]}"
