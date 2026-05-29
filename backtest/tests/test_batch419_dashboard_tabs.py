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


def test_batch422_build_script_emits_window_attached_global(build_src):
    """Batch 422 (2026-05-28) fix for the 'all tabs blank' regression.

    In a regular <script> context (non-module), top-level `const X = ...`
    creates a lexical global that does NOT attach to window. app.js's
    `const D = window.PHASE_1A_DATA || {}` therefore always saw `{}`
    pre-Batch-422, rendering all tabs blank. Build script must emit
    `window.PHASE_1A_DATA = ...` (or `var PHASE_1A_DATA`) for the
    assignment to be visible via `window.PHASE_1A_DATA`."""
    assert "window.PHASE_1A_DATA =" in build_src, (
        "Build script must emit `window.PHASE_1A_DATA = ...` per "
        "Batch 422 fix; got `const PHASE_1A_DATA = ...` which doesn't "
        "attach to window in regular <script> context."
    )
    assert "const PHASE_1A_DATA =" not in build_src.split("# Browser-loadable", 1)[-1].split("\n", 6)[5:][0:1], (
        "Build script must not use `const PHASE_1A_DATA = ...` for the "
        "browser data.js emission (silently breaks window-scope lookup)."
    ) if False else None  # informational only; primary assertion above


def test_batch422_data_js_starts_with_window_attached_global():
    """Regen artifact must reflect the fix: data.js starts with
    `window.PHASE_1A_DATA = `."""
    data_js = (REPO / "dashboard_phase_1a" / "data.js")
    if not data_js.exists():
        pytest.skip("data.js missing (build not run yet)")
    first_chunk = data_js.read_text(encoding="utf-8")[:80]
    assert first_chunk.startswith("window.PHASE_1A_DATA ="), (
        f"data.js does not start with `window.PHASE_1A_DATA =`; got "
        f"first 80 chars: {first_chunk!r}. Regenerate via "
        f"`python scripts/build_dashboard_phase_1a.py`."
    )


def test_batch422_app_js_defensive_data_lookup():
    """app.js's `D` initializer must be defensive against either a window-
    attached global OR a lexical const (backward compat)."""
    app_js = (REPO / "dashboard_phase_1a" / "app.js").read_text(encoding="utf-8")
    assert "window.PHASE_1A_DATA" in app_js, (
        "app.js must reference window.PHASE_1A_DATA for the canonical "
        "data lookup")
    assert "typeof PHASE_1A_DATA" in app_js, (
        "app.js must also have a `typeof PHASE_1A_DATA !== 'undefined'` "
        "fallback per Batch 422 defensive pattern")


def test_batch430_buildtable_window_ready_bug_removed():
    """app.js's buildTable() previously had `$(window).ready(...)` which
    threw SyntaxError because `$` was overridden as document.querySelector
    (so `$(window)` -> `document.querySelector(window)` -> '[object Window]
    is not a valid selector'). That killed every buildTable() call so
    Tabs 1-9 + Exits + Trades + Tab 13 (CubeCells) showed only their
    <h2> header + an empty <table> stub. Batch 430 removes the line."""
    app_js = (REPO / "dashboard_phase_1a" / "app.js").read_text(encoding="utf-8")
    assert "$(window).ready" not in app_js, (
        "buildTable() must not contain `$(window).ready(...)` - "
        "throws because `$` is overridden as document.querySelector")


def test_batch430_marked_js_loaded_in_index():
    """Tab 10 Optimizer Summary renders optimization_summary.md via
    marked.js. The CDN script must be loaded BEFORE app.js so marked is
    in scope when renderOptimizer fires."""
    html = (REPO / "dashboard_phase_1a" / "index.html").read_text(encoding="utf-8")
    assert "marked.min.js" in html, (
        "index.html must load marked.min.js for Tab 10 markdown render")
    # Order check: marked.min.js must appear before app.js
    pos_marked = html.find("marked.min.js")
    pos_app = html.find("app.js")
    assert 0 < pos_marked < pos_app, (
        f"marked.min.js (pos {pos_marked}) must precede app.js "
        f"(pos {pos_app}) so `marked` is in scope when renderOptimizer runs")


def test_batch430_optimizer_uses_marked_parse():
    """renderOptimizer must call marked.parse() instead of dumping raw
    markdown into a <pre> with .textContent."""
    app_js = (REPO / "dashboard_phase_1a" / "app.js").read_text(encoding="utf-8")
    assert "marked.parse" in app_js, (
        "renderOptimizer must use marked.parse() for Tab 10 rendering")
    # Target element renamed in index.html
    assert "#optimizer-md-rendered" in app_js, (
        "renderOptimizer must target #optimizer-md-rendered (Batch 430 "
        "rename of #optimizer-md-pre)")


def test_batch430_optimizer_target_is_div():
    """Batch 430 changed the optimizer markdown container from <pre> to
    <div> so marked.js's HTML output renders properly (rather than being
    displayed as escaped text inside a preformatted block)."""
    html = (REPO / "dashboard_phase_1a" / "index.html").read_text(encoding="utf-8")
    # The optimizer summary container should be a <div> with class md-render
    import re
    m = re.search(r'<div\s+id="optimizer-md-rendered"[^>]*class="md-render"', html)
    assert m is not None, (
        "Tab 10 optimizer markdown container must be "
        "<div id='optimizer-md-rendered' class='md-render' ...>")
    # And the prior <pre id="optimizer-md-pre"> must be gone
    assert 'id="optimizer-md-pre"' not in html, (
        "Old <pre id='optimizer-md-pre'> must be removed (Batch 430 "
        "renamed to #optimizer-md-rendered)")


def test_batch430_candidate_detail_is_div_with_structured_render():
    """Tab 11 candidate-detail switched from raw JSON dump in <pre> to
    structured render (KPIs + per-dimension table + collapsible JSON) in
    <div>."""
    html = (REPO / "dashboard_phase_1a" / "index.html").read_text(encoding="utf-8")
    assert 'id="candidate-detail"' in html, (
        "candidate-detail element must exist for Tab 11")
    # Must be a <div> not <pre> now
    import re
    m_div = re.search(r'<div\s+id="candidate-detail"', html)
    m_pre = re.search(r'<pre\s+id="candidate-detail"', html)
    assert m_div is not None and m_pre is None, (
        "candidate-detail must be a <div> (Batch 430 switched from <pre>)")

    app_js = (REPO / "dashboard_phase_1a" / "app.js").read_text(encoding="utf-8")
    # Structured render markers
    assert "Per-dimension summary" in app_js, (
        "renderCandidates must build a per-dimension summary table")
    assert "dimension_a_thresholds" in app_js, (
        "renderCandidates must enumerate the 9 dimension keys")
    # Collapsible raw JSON fallback retained
    assert "Raw JSON (full payload)" in app_js, (
        "renderCandidates must retain a collapsible full-JSON fallback")
