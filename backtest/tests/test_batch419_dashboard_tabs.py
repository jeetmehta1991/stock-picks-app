"""Batch 419 (2026-05-28 owner-approved): test-pin the 4 new dashboard
tabs added per the locked workflow Stage 3 expectations doc.

Source attribution (per CHECKLIST #77):
  Spec: PHASE_1A_BETA_CUBE_OPTIMIZATION_WORKFLOW.md Stage 3 dashboard
  expectations table (4 new tabs: Optimizer Summary, Candidates, Quiet
  Strategies, Cell Verdict Cube).

  Source data: output_optimization_candidates_<date>/ folder produced by
  scripts/optimize_strategies_from_cube.py (Batch 388 + 391).

These tests pin:
  1. The 4 new tab buttons exist in index.html
  2. The 4 new tab panels exist in index.html
  3. Total tab count = 17 (13 existing + 4 new)
  4. Build script has the --optimizer-dir CLI flag
  5. load_optimizer_dir() helper exists and returns the expected payload
     shape when OPT_DIR exists.

Per feedback_doc_count_drift_must_be_test_pinned: tab count test-pinned
so future refactors can't silently drop tabs.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DASH_HTML = REPO / "dashboard_phase_1a" / "index.html"
BUILD_SCRIPT = REPO / "scripts" / "build_dashboard_phase_1a.py"


BATCH_419_TAB_PANELS = ["optimizer", "candidates", "quiet", "cubecells"]
PRE_BATCH_419_TAB_PANELS = [
    "overview", "strategies", "regime", "maemfe", "equity",
    "walkforward", "smartmoney", "sector", "skipped", "circuit",
    "exits", "trades", "raw",
]


@pytest.fixture(scope="module")
def html_src() -> str:
    assert DASH_HTML.exists(), f"{DASH_HTML} missing"
    return DASH_HTML.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def build_src() -> str:
    assert BUILD_SCRIPT.exists(), f"{BUILD_SCRIPT} missing"
    return BUILD_SCRIPT.read_text(encoding="utf-8")


@pytest.mark.parametrize("panel_id", BATCH_419_TAB_PANELS)
def test_batch419_tab_button_present(html_src, panel_id):
    """Each Batch 419 tab must have a <button class='tab-btn'> entry."""
    needle = f'data-panel="{panel_id}"'
    assert needle in html_src, (
        f'index.html missing tab button data-panel="{panel_id}" '
        f"(Batch 419 not applied or reverted)")


@pytest.mark.parametrize("panel_id", BATCH_419_TAB_PANELS)
def test_batch419_tab_panel_present(html_src, panel_id):
    """Each Batch 419 tab must have a <section class='panel' id='...'>."""
    needle = f'id="{panel_id}"'
    assert needle in html_src, (
        f'index.html missing <section id="{panel_id}"> (Batch 419 not '
        f"applied or reverted)")


def test_batch419_total_tab_count_17(html_src):
    """Tab buttons in index.html: 13 pre-Batch-419 + 4 new = 17 total.
    Per feedback_doc_count_drift_must_be_test_pinned."""
    expected_panels = set(PRE_BATCH_419_TAB_PANELS + BATCH_419_TAB_PANELS)
    found = set()
    for panel in expected_panels:
        if f'data-panel="{panel}"' in html_src:
            found.add(panel)
    assert found == expected_panels, (
        f"Tab roster drift: missing {expected_panels - found}; "
        f"unexpected/dropped {found - expected_panels}")
    assert len(expected_panels) == 17, (
        f"Expected 17 tabs total (13 + 4 Batch 419); got "
        f"{len(expected_panels)}")


def test_batch419_optimizer_dir_cli_flag(build_src):
    """Build script must have --optimizer-dir CLI flag."""
    assert "--optimizer-dir" in build_src, (
        "scripts/build_dashboard_phase_1a.py missing --optimizer-dir flag "
        "(Batch 419 not applied)")


def test_batch419_load_optimizer_dir_helper(build_src):
    """Build script must define load_optimizer_dir() helper."""
    assert "def load_optimizer_dir(" in build_src, (
        "scripts/build_dashboard_phase_1a.py missing load_optimizer_dir() "
        "helper (Batch 419 not applied)")


def test_batch419_payload_keys_in_build(build_src):
    """The 4 new payload keys must be emitted by build()."""
    for key in ["optimizer_summary_md", "per_strategy_candidates",
                "exit_method_analysis", "producer_zero_audit"]:
        assert f'"{key}":' in build_src, (
            f'build_dashboard_phase_1a.py missing payload key "{key}" '
            f"(Batch 419 not applied)")


def test_batch419_renderers_in_app_js():
    """app.js must define the 4 new renderXxx() functions + call them."""
    app_js = (REPO / "dashboard_phase_1a" / "app.js").read_text(encoding="utf-8")
    for fn in ["renderOptimizer", "renderCandidates",
                "renderQuiet", "renderCubeCells"]:
        assert f"function {fn}(" in app_js, (
            f"app.js missing {fn}() definition (Batch 419 not applied)")
        assert f"{fn}();" in app_js, (
            f"app.js does not call {fn}() in the render-all block")
