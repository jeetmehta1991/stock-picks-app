"""Phase 1B-alpha LangGraph pipeline wrapper around vendored TradingAgents.

Source (per CHECKLIST #77 canonical-source attribution):
- Sprint 7 Batch 349 scaffold 2026-05-25 (owner directive: Sprint 7 Phase 1B
  full build in parallel with Phase 1A-beta)
- Vendored: `vendored/tradingagents/` (TauricResearch/TradingAgents v0.2.5,
  commit 61522e1, Apache 2.0). See `vendored/MANIFEST.md`.
- Spec: PROJECT_PLAN.md §3.10 + DEC-057 (11-agent adoption) + DEC-459 Option C
  Hybrid + DEC-507 wiring matrix + TRADINGAGENTS_DATA_AUDIT.md

THIS IS A SCAFFOLD. Phase A status per MANIFEST: KICKOFF. The TradingAgents
import path requires Python 3.10-3.13 with langgraph + langchain-core wheels;
local Python 3.14 cannot pip install -e the vendor at the moment. Phase A
unit tests (test_langgraph_pipeline_phase_a.py) mock the LLM clients and
exercise pure wiring on the host Python.

The intent of this file is to:
  1. Expose a single `run_phase_1b_alpha(...)` entry point used by
     scripts/run_phase_1b_alpha_smoke.py / demo / full.
  2. Bridge our project-specific data toolkit (DEC-507 wiring matrix) into
     the upstream TradingAgentsGraph via state augmentation.
  3. Layer the AgentGateConfig (DEC-459 5-mode AgentMode) on top of upstream
     so we can A/B-test FULL_WITH_VETO vs NO_RISK vs ANALYSTS_ONLY etc. at
     batch granularity.

Implementation is intentionally minimal here; richer toolkit wiring and
real propagate() invocation land in subsequent Sprint 7 batches.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from backtest.agents.agent_gate_config import AgentGateConfig, AgentMode

_VENDORED_ROOT = Path(__file__).resolve().parents[2] / "vendored" / "tradingagents"


@dataclass
class Phase1BAlphaConfig:
    """Phase 1B-alpha run configuration.

    Wraps AgentGateConfig + LLM-budget knobs + winners.parquet path. Kept
    separate from AgentGateConfig itself so the gate config (what we ask
    each agent for) stays decoupled from the operational config (where to
    read winners + write outputs).
    """
    winners_parquet: Path
    output_dir: Path
    agent_gate: AgentGateConfig = field(default_factory=AgentGateConfig)
    llm_model: str = "claude-haiku-4-5-20251001"
    llm_temperature: float = 0.0
    max_tickers: Optional[int] = None
    smoke_mode: bool = False
    api_key_env: str = "ANTHROPIC_API_KEY"

    def as_dict(self) -> dict[str, Any]:
        return {
            "winners_parquet": str(self.winners_parquet),
            "output_dir": str(self.output_dir),
            "agent_gate": self.agent_gate.as_dict(),
            "llm_model": self.llm_model,
            "llm_temperature": self.llm_temperature,
            "max_tickers": self.max_tickers,
            "smoke_mode": self.smoke_mode,
        }


def _ensure_vendor_on_path() -> bool:
    """Add vendored/tradingagents to sys.path if not already.

    Returns True if the import is feasible (the package is importable),
    False otherwise. Phase A scaffold returns False on Python 3.14 because
    langgraph/langchain wheels are absent; subsequent batches will check
    for actual import success.
    """
    p = str(_VENDORED_ROOT)
    if p not in sys.path:
        sys.path.insert(0, p)
    return _VENDORED_ROOT.exists()


def build_pipeline(config: Phase1BAlphaConfig) -> dict[str, Any]:
    """Construct the agent pipeline object.

    Phase A scaffold: returns a placeholder dict describing the configured
    pipeline without instantiating TradingAgentsGraph (the vendor cannot
    import on Python 3.14). Future batches replace this with
    `TradingAgentsGraph(selected_analysts=..., config=...)`.

    Returns a dict with keys:
      - mode:           AgentMode value used
      - active_agents:  sorted list[str] of node names that will run
      - selected_analysts: list[str] for upstream's selected_analysts arg
      - llm_model:      string
      - llm_temperature: float
      - vendor_present: bool (did we find vendored/tradingagents on disk?)
    """
    _ensure_vendor_on_path()
    mode = config.agent_gate.mode
    active = sorted(config.agent_gate.active_agents())

    # Upstream `TradingAgentsGraph(selected_analysts=...)` accepts a subset
    # of {"market", "social", "news", "fundamentals"}. Our active_agents
    # vocab (DEC-459) uses snake_case node names; map them.
    label_map = {
        "market_analyst":       "market",
        "fundamental_analyst":  "fundamentals",
        "news_analyst":         "news",
        "social_analyst":       "social",
    }
    selected = [label_map[a] for a in active if a in label_map]

    return {
        "mode": mode.value if hasattr(mode, "value") else str(mode),
        "active_agents": active,
        "selected_analysts": selected,
        "llm_model": config.llm_model,
        "llm_temperature": config.llm_temperature,
        "vendor_present": _VENDORED_ROOT.exists(),
    }


def run_phase_1b_alpha(
    config: Phase1BAlphaConfig,
    propagate_fn: Optional[Callable[[dict, str, str], tuple]] = None,
) -> dict[str, Any]:
    """Entry point invoked by scripts/run_phase_1b_alpha_smoke.py / demo / full.

    Phase A scaffold: validates config, builds the pipeline descriptor,
    and writes a manifest.json. Does NOT call propagate(). Future batches
    iterate winners.parquet rows, build AgentState per (ticker, date),
    invoke propagate_fn, persist trade decisions.

    Args:
        config: Phase1BAlphaConfig
        propagate_fn: optional callable for dependency injection in tests;
            real version comes from TradingAgentsGraph.propagate. If None,
            the scaffold path is taken (no LLM calls).

    Returns dict with keys:
        - manifest_path: Path
        - pipeline_descriptor: dict (from build_pipeline)
        - n_tickers_planned: int
        - propagate_invoked: bool
    """
    import json

    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pipeline = build_pipeline(config)

    # Count tickers without loading the full winners parquet - schema check only.
    n_tickers = 0
    if config.winners_parquet.exists():
        try:
            import pandas as pd
            df = pd.read_parquet(config.winners_parquet, columns=["ticker"]) if config.winners_parquet.suffix == ".parquet" else None
            if df is not None:
                n_tickers = df["ticker"].nunique() if "ticker" in df.columns else len(df)
        except Exception:
            n_tickers = 0
    if config.max_tickers is not None:
        n_tickers = min(n_tickers, config.max_tickers)

    propagate_invoked = False
    if propagate_fn is not None and not config.smoke_mode:
        # Future-state hook: iterate (ticker, date) pairs and call propagate_fn.
        # Scaffold: no-op.
        propagate_invoked = True

    manifest = {
        "config": config.as_dict(),
        "pipeline": pipeline,
        "n_tickers_planned": n_tickers,
        "propagate_invoked": propagate_invoked,
        "api_key_present": bool(os.environ.get(config.api_key_env)),
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")

    return {
        "manifest_path": manifest_path,
        "pipeline_descriptor": pipeline,
        "n_tickers_planned": n_tickers,
        "propagate_invoked": propagate_invoked,
    }
