"""Smoke tests - DEC-503 pyramid layer (Pass 53 v8h+1 owner-approved 2026-05-08).

Smoke = the minimum end-to-end path runs without crashing. These tests
exercise import surfaces and trivial entry-point invocations of every script
that matters for Phase 1A. They are FAST (each <1s) and run on every push.

A smoke failure = a script that someone modified and broke import-side; the
issue would otherwise stay hidden until manual invocation.

Markers:
    pytest -m smoke   # run only these
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"


pytestmark = pytest.mark.smoke


def _import_from_path(path: Path):
    """Import a module by file path without polluting sys.modules namespace."""
    spec = importlib.util.spec_from_file_location(f"smoke_{path.stem}", path)
    if spec is None or spec.loader is None:
        pytest.fail(f"could not load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# -- Smoke 1: every prefetch script imports cleanly ------------------------
PREFETCH_SCRIPTS = sorted((SCRIPTS).glob("prefetch_*.py"))


@pytest.mark.parametrize("script_path", PREFETCH_SCRIPTS, ids=lambda p: p.stem)
def test_prefetch_script_imports(script_path: Path) -> None:
    """Every prefetch_*.py imports without ImportError / SyntaxError. The
    scripts have side-effects (env loading, API key checks) which we suppress
    by importing as a module rather than running."""
    if not script_path.exists():
        pytest.skip(f"{script_path} missing")
    # Some prefetch scripts exit 1 if API key is unset; we accept that here
    # because import-time SystemExit is the expected behavior, not a bug.
    try:
        _import_from_path(script_path)
    except SystemExit:
        pass  # API-key guard fired; not a smoke failure
    except (ImportError, SyntaxError) as e:
        pytest.fail(f"{script_path.name} import failed: {e}")


# -- Smoke 2: dashboard builders import + expose main() ---------------------
DASHBOARD_BUILDERS = [
    SCRIPTS / "build_dashboard_stage_2.py",
    SCRIPTS / "build_dashboard_sprint0a.py",
]


@pytest.mark.parametrize("script_path", DASHBOARD_BUILDERS, ids=lambda p: p.stem)
def test_dashboard_builder_imports(script_path: Path) -> None:
    if not script_path.exists():
        pytest.skip(f"{script_path} missing")
    mod = _import_from_path(script_path)
    assert hasattr(mod, "main"), f"{script_path.name} has no main()"


# -- Smoke 3: doc-count drift detector runs --------------------------------
def test_sync_doc_counts_runs() -> None:
    """sync_doc_counts.py --check should exit 0 when no drift."""
    import subprocess
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "sync_doc_counts.py"), "--check"],
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=60,
    )
    assert r.returncode == 0, (
        f"sync_doc_counts.py --check exit={r.returncode}\n"
        f"stdout: {r.stdout[-500:]}\nstderr: {r.stderr[-500:]}"
    )


# -- Smoke 4: backtest engine imports + key modules load -------------------
@pytest.mark.parametrize("module_name", [
    "backtest.config",
    "backtest.data.universe",
    "backtest.data.cache",
    "backtest.engine.backtest",
    "backtest.engine.regime_filter",
    "backtest.signals.technical",
    "backtest.signals.screener",
    "backtest.results.metrics",
])
def test_engine_module_imports(module_name: str) -> None:
    """Each backtest module imports cleanly. Catches broken imports
    introduced by refactors that integration tests miss."""
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    try:
        __import__(module_name)
    except ImportError as e:
        pytest.fail(f"{module_name} import failed: {e}")


# -- Smoke 5: shared prefetch util ----------------------------------------
def test_prefetch_utils_smoke() -> None:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    from _prefetch_utils import safe_filename_stem
    assert safe_filename_stem("AAPL") == "AAPL"
    assert safe_filename_stem("CON") == "CON_"
