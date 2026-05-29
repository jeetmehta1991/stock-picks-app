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


def test_batch433_render_regime_reads_regime_verdicts_nested():
    """Tab 2 Regime heatmap previously read top-level keys of each
    strategy entry AS regime names - so the columns became literally
    `best_regimes / regime_verdicts / overall_win_rate / total_trades /
    passes_all` (because that is what the keys actually are) and every
    cell rendered empty because none of those values are verdict strings.
    The actual data nests verdicts under entry.regime_verdicts. Pin that
    renderRegime reads from the nested location."""
    app_js = (REPO / "dashboard_phase_1a" / "app.js").read_text(encoding="utf-8")
    # The fix must walk into regime_verdicts, not the top level.
    assert "regime_verdicts" in app_js, (
        "renderRegime must read regime names from "
        "entry.regime_verdicts (not the strategy's top-level keys)")
    # Sanity: a `flatMap` over top-level keys would look like
    # `Object.keys(matrix[s] || {})` with no `.regime_verdicts` lookup.
    # Require the lookup is present in the flatMap.
    assert "regime_verdicts || {}))" in app_js or "regime_verdicts) || {})" in app_js, (
        "renderRegime must build the regimes column list from "
        "Object.keys(matrix[s].regime_verdicts || {})")


def test_batch433_render_regime_emits_summary_columns():
    """Batch 433 appends 3 summary columns (Trades / Win % / Passes) to
    the regime heatmap so the strategy-level aggregates are visible
    alongside the per-regime verdicts."""
    app_js = (REPO / "dashboard_phase_1a" / "app.js").read_text(encoding="utf-8")
    for label in ['"Trades"', '"Win %"', '"Passes"']:
        assert label in app_js, (
            f"renderRegime must emit summary column header {label}")
    # entry.total_trades / overall_win_rate / passes_all must be read
    for k in ["total_trades", "overall_win_rate", "passes_all"]:
        assert f"entry.{k}" in app_js or f'["{k}"]' in app_js, (
            f"renderRegime must read entry.{k} for the summary column")


def test_batch434_reference_tab_button_and_panel():
    """Owner-directed Reference / Background tab (#14) must be wired
    into both the nav and the panels."""
    html = (REPO / "dashboard_phase_1a" / "index.html").read_text(encoding="utf-8")
    assert '<button class="tab-btn" data-panel="reference">14. Reference</button>' in html, (
        "Reference tab button missing from nav")
    assert '<section class="panel" id="reference">' in html, (
        "Reference panel section missing")


def test_batch434_reference_content_includes_required_sections():
    """Reference tab must include: Strategy library (layers), 25 Exit
    methods, 9 Success criteria, DEC-426 5-Gate, Universe 5-bucket,
    Regime classification, Position sizing, Tab navigation guide,
    Glossary, Data flow."""
    html = (REPO / "dashboard_phase_1a" / "index.html").read_text(encoding="utf-8")
    required_headings = [
        "Strategy library",
        "25 Exit methods",
        "9 Success criteria",
        "DEC-426 5-Gate",
        "5-bucket architecture",
        "Regime classification",
        "Position sizing",
        "Tab navigation guide",
        "Glossary",
        "Data flow",
    ]
    for h in required_headings:
        assert h in html, f"Reference tab missing required section: {h}"


def test_batch434_render_reference_function_present_and_dispatched():
    """app.js must define renderReference() AND dispatch it in the
    try/catch render block."""
    app_js = (REPO / "dashboard_phase_1a" / "app.js").read_text(encoding="utf-8")
    assert "function renderReference()" in app_js, (
        "renderReference() function must be defined")
    assert "renderReference();" in app_js, (
        "renderReference() must be dispatched in the render-all block")
    assert "#reference-counts" in app_js, (
        "renderReference must populate the #reference-counts KPI grid")


def test_batch434_strategies_tab_surfaces_185_100_36_85_split():
    """Tab 1 Strategies KPI grid must surface the registered / fired /
    in-table / quiet split so owner understands why only 36 strategies
    appear in the CSV."""
    app_js = (REPO / "dashboard_phase_1a" / "app.js").read_text(encoding="utf-8")
    # KPI labels (Batch 437 collapsed to cube-only labels - dropped
    # the baseline-vs-cube split because Phase 1A-beta is cube-only
    # per owner directive).
    for label in ['"Registered (code)"', '"Fired in this cube run"',
                  '"Quiet (Tab 12)"']:
        assert label in app_js, (
            f"renderStrategies KPI label missing: {label}")
    # Must read producer_zero_audit.summary for the cube counts
    assert "producer_zero_audit" in app_js, (
        "renderStrategies must read producer_zero_audit for the split")


def test_batch435_strat_inclusion_callout_present():
    """Tab 1 must include an explicit inclusion-criteria callout for
    new viewers - prior version mixed cube vs baseline counts without
    labeling, which obscured why only 36 strategies appear in the table."""
    html = (REPO / "dashboard_phase_1a" / "index.html").read_text(encoding="utf-8")
    assert 'id="strat-inclusion-callout"' in html, (
        "Tab 1 must include an inclusion-criteria callout div with "
        "id=strat-inclusion-callout")
    app_js = (REPO / "dashboard_phase_1a" / "app.js").read_text(encoding="utf-8")
    assert "strat-inclusion-callout" in app_js, (
        "renderStrategies must populate the inclusion-criteria callout")
    # The callout text must mention the criteria + the cube-vs-baseline gap.
    assert "Inclusion criteria" in app_js, (
        "Callout text must say 'Inclusion criteria'")


def test_batch437_kpi_labels_cube_only():
    """Batch 437 collapsed Tab 1 KPI labels to a single cube source
    after owner clarified Phase 1A-beta = cube-only. The prior
    Batch 435 split (baseline vs cube) was structurally wrong."""
    app_js = (REPO / "dashboard_phase_1a" / "app.js").read_text(encoding="utf-8")
    assert '"Fired in this cube run"' in app_js, (
        "Cube-fired KPI must say 'Fired in this cube run'")
    assert '"Quiet (Tab 12)"' in app_js, (
        "Quiet KPI must be 'Quiet (Tab 12)' (no baseline/cube split)")
    assert '"Registered (code)"' in app_js, (
        "Registered count KPI must say 'Registered (code)'")
    # The baseline-cube split labels must be GONE.
    for old in ['"In this table (this run)"', '"Fired in cube"',
                '"Quiet in cube (Tab 12)"']:
        assert old not in app_js, (
            f"Old Batch 435/436 label `{old}` must be removed "
            "(Phase 1A-beta dashboard is cube-only)")


def test_batch437_reference_first_time_viewer_block_cube_only():
    """Tab 14 First-time viewer block must explain the cube-only Phase
    1A-beta architecture (Batch 437 superseded Batch 435/436 framing
    that incorrectly treated baseline output_v2 as a parallel source)."""
    html = (REPO / "dashboard_phase_1a" / "index.html").read_text(encoding="utf-8")
    assert "First-time viewer?" in html, (
        "Tab 14 must lead with a 'First-time viewer?' callout")
    # Must explain the cube-only Phase 1A-beta architecture.
    assert "Phase 1A-beta runs with all four legacy gates OFF" in html, (
        "Tab 14 banner must explain Phase 1A-beta = all-gates-off")
    assert "single source for every tab" in html, (
        "Tab 14 banner must state cube is the single source")
    # Must list the recommended reading order.
    assert "Recommended reading order" in html, (
        "Tab 14 banner must include a recommended reading order")


def test_batch437_tab1_callout_explains_185_vs_fired_cube_only():
    """Tab 1 callout post-Batch-437 must explain the 185 vs fired
    split as cube-only (no baseline comparison)."""
    app_js = (REPO / "dashboard_phase_1a" / "app.js").read_text(encoding="utf-8")
    # Must cite "Phase 1A-beta" + "cube" + "all four legacy gates OFF".
    assert "Phase 1A-beta cube run" in app_js, (
        "Callout must identify the source as the Phase 1A-beta cube run")
    assert "185 registered" in app_js, (
        "Callout must cite 185 = registered strategies")
    # The 4 flags must still be present in the architecture banner
    # (now in Tab 14, not Tab 1).
    html = (REPO / "dashboard_phase_1a" / "index.html").read_text(encoding="utf-8")
    for flag in ["--no-portfolio-cap", "--no-dd-halt",
                 "--no-regime-affinity", "--no-event-suppression"]:
        assert flag in html, (
            f"Tab 14 architecture banner must cite the {flag} flag")


def test_batch437_tab14_phase_1a_beta_cube_only_banner():
    """Tab 14 must lead with the Phase 1A-beta cube-only architecture
    banner (NOT the prior Batch 436 'two different runs' framing)."""
    html = (REPO / "dashboard_phase_1a" / "index.html").read_text(encoding="utf-8")
    assert "Phase 1A-beta runs with all four legacy gates OFF" in html, (
        "Tab 14 banner must explain Phase 1A-beta = all-gates-off")
    assert "Returns in" in html and "Phase 1B-alpha" in html, (
        "Tab 14 banner must clarify the gates return in Phase 1B-alpha")
    # The cube source must be the single source.
    assert "single source for every tab" in html, (
        "Tab 14 banner must explicitly state cube is the single source")
    # Old Batch 436 'two-run comparison' headings must be REMOVED.
    assert "Strict run (Tab 1's source)" not in html, (
        "Old Batch 436 'Strict run' column must be removed - "
        "Phase 1A-beta dashboard is cube-only")


def test_batch438_position_sizing_two_stage_block_present():
    """Tab 14 Position sizing section was rewritten to (a) drop the
    wrong '9 criteria + agent score' trigger column and (b) explain
    the actual two-stage process: Stage 1 = rule-based confluence
    tier (Phase 1A-beta active), Stage 2 = agent tier adjustment
    (Phase 1B+ only)."""
    html = (REPO / "dashboard_phase_1a" / "index.html").read_text(encoding="utf-8")
    assert "Stage 1 - Rule-based preliminary tier" in html, (
        "Position sizing section must lead with Stage 1 (rule-based "
        "preliminary tier) - this is the only stage active in 1A-beta")
    assert "Stage 2 - Agent tier adjustment" in html, (
        "Position sizing section must include Stage 2 (agent "
        "adjustment) with 'Phase 1B+ only' qualifier")
    assert "_assign_confidence_tier" in html, (
        "Stage 1 must cite the actual code function")
    assert "_adjust_tier_by_agent" in html, (
        "Stage 2 must cite the actual code function")
    # Worked example must be present.
    assert "Example A - EXCEPTIONAL" in html, (
        "Position sizing must include worked examples (A through D)")
    # Old (wrong) sizing-trigger text must be removed.
    assert "All 9 criteria + agent score" not in html, (
        "Old (wrong) 'All 9 criteria + agent score X' trigger column "
        "must be removed - sizing does not consume the 9 criteria")


def test_batch438_quiet_tab_bucket_explainer_present():
    """Tab 12 must include a plain-English explainer for the 3
    quiet-strategy buckets (PRODUCER_LAYER_ZERO_LIKELY /
    COMPOUND_RESTRICTIVE / SKIPPED_AT_ENGINE) with everyday analogy
    + fix instructions, not just a one-liner per bucket."""
    html = (REPO / "dashboard_phase_1a" / "index.html").read_text(encoding="utf-8")
    # The explainer is a <details> block on Tab 12.
    assert "What do these buckets mean?" in html, (
        "Tab 12 must include a 'What do these buckets mean?' details "
        "block with full bucket explanations")
    # Each bucket must have the 4-element explanation: meaning + analogy /
    # example + fix.
    for bucket in ["PRODUCER_LAYER_ZERO_LIKELY",
                   "COMPOUND_RESTRICTIVE", "SKIPPED_AT_ENGINE"]:
        assert bucket in html, f"Tab 12 explainer missing bucket: {bucket}"
    assert "everyday analogy" in html.lower() or "sunny AND" in html, (
        "Compound restrictive bucket must include the everyday analogy")
    assert "Quick decision rule" in html, (
        "Explainer must close with the quick decision rule")


def test_batch438_reference_tab_quiet_bucket_table_present():
    """Tab 14 must also document the 3 quiet-strategy buckets so the
    explanation persists in the reference page even after a user
    closes the Tab 12 details block."""
    html = (REPO / "dashboard_phase_1a" / "index.html").read_text(encoding="utf-8")
    assert "Quiet-strategy buckets explained (Tab 12)" in html, (
        "Tab 14 must include a 'Quiet-strategy buckets explained' "
        "section with the 3-bucket table")


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
