"""End-to-end Phase 1A smoke pytest  -  Pass 53 Day-9 wiring closure.

G1 of the test-pyramid gap closure (DEC-503 + DEC-595).

Distinct from `test_e2e.py`:
- test_e2e.py: 5 tickers x 3 months  -  minimal pipeline smoke
- this file:   10 tickers x 1 year  -  exercises full Day-9 wiring
                (DEC-505 4-fold WF, DEC-515 Level 6 CB, DEC-516 regime_flip,
                 DEC-578 verdict_cube, Tier 1-4 25-col exit context,
                 per-exit conditional analyzer)

Target runtime: <2 min on developer laptop. Skipped if cache unavailable.

BUG-006 protocol-fix coverage attribution (owner directive 2026-05-10):
this smoke run is the canonical end-to-end exerciser of the engine code
paths fixed by the following bugs. Each bug listed has its addressal
pyramid (CHECKLIST #78) including a passing run of this smoke file. The
PYRAMID_OVERRIDES dict in scripts/build_dashboard_stage_2.py declares
non-applicable layers as N/A; this docstring is the source-of-truth for
the smoke layer coverage claim picked up by the grep mechanism.

Smoke layer covers (engine code paths exercised):
  BUG-029 - end-of-backtest open-trade finalization
  BUG-061 - ticker-level concurrent-position block
  BUG-077 - third-bucket avoid categorization
  BUG-078 - trailing stop lookahead bias fix
  BUG-080 - exit slippage symmetric to entry
  BUG-095 - Portfolio class engine lifecycle
  BUG-110 - entry gap filter validate_entry_zone enforcement
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

import pandas as pd
import pytest


SMOKE_TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
                 "META", "TSLA", "JPM", "XOM", "SPY"]
SMOKE_START = date(2023, 1, 1)
SMOKE_END = date(2023, 12, 31)


@pytest.fixture(scope="module")
def smoke_engine(tmp_path_factory):
    """Run full Phase 1A backtest once; share across tests."""
    from backtest.engine.backtest import BacktestEngine

    out_dir = tmp_path_factory.mktemp("smoke_phase1a")
    logging.disable(logging.CRITICAL)

    eng = BacktestEngine(
        universe=SMOKE_TICKERS,
        start=SMOKE_START,
        end=SMOKE_END,
        phase="phase_1a",
        max_candidates_per_day=5,
        run_agents=False,
        output_dir=str(out_dir),
        apply_costs=True,
        walk_forward=False,
    )
    eng.load_data()

    if len(getattr(eng, "ohlcv_dict", {}) or {}) == 0:
        pytest.skip("OHLCV cache not populated  -  skip e2e smoke")

    eng.run()

    if not getattr(eng, "closed_trades", None):
        pytest.skip("Smoke produced no trades  -  likely empty cache window")

    eng.save_all_outputs()
    logging.disable(logging.NOTSET)
    return eng, out_dir


def test_g1_engine_finishes(smoke_engine):
    eng, _ = smoke_engine
    assert len(eng.closed_trades) > 0


def test_g1_level6_state_initialized(smoke_engine):
    """N5: DEC-515 Level 6 CB state must exist post-run."""
    eng, _ = smoke_engine
    assert hasattr(eng, "level_6_state")
    from backtest.engine.circuit_breakers import Level6State
    assert isinstance(eng.level_6_state, Level6State)


def test_g1_trade_log_has_exit_context_columns(smoke_engine):
    """Tier 1-4 exit context (25 cols) propagated to trade_log if available."""
    eng, _ = smoke_engine
    df = eng.get_trade_log()
    from backtest.engine.exit_context import CONTEXT_COLUMN_NAMES
    present = [c for c in CONTEXT_COLUMN_NAMES if c in df.columns]
    # Trade log itself may not include all 25  -  they propagate via trade_exit_detail
    # At minimum, regime_at_entry / cap_band / vol_band should be present somewhere
    detail = getattr(eng, "trade_exit_detail_rows", None)
    if detail is not None and len(detail) > 0:
        ddf = pd.DataFrame(detail) if not isinstance(detail, pd.DataFrame) else detail
        present_detail = [c for c in CONTEXT_COLUMN_NAMES if c in ddf.columns]
        assert len(present_detail) >= 5, \
            f"trade_exit_detail missing context cols: only {present_detail}"
    else:
        # No counterfactual rows is acceptable in single-pass smoke; assert at least core fields
        for col in ["pnl_pct", "hold_days", "win"]:
            assert col in df.columns


def test_g1_outputs_emitted(smoke_engine):
    eng, out_dir = smoke_engine
    out = Path(out_dir)
    expected = ["trade_log.csv", "backtest_results.csv"]
    written = {p.name for p in out.glob("*.csv")}
    for f in expected:
        assert f in written, f"missing required output {f}; got {sorted(written)}"


def test_g1_verdict_cube_emitted_or_documented(smoke_engine):
    """N6: verdict_cube.csv emits when df_trades has the required dim cols."""
    eng, out_dir = smoke_engine
    out = Path(out_dir)
    df_log = pd.read_csv(out / "trade_log.csv") if (out / "trade_log.csv").exists() else pd.DataFrame()
    needs = {"strategy", "regime", "sector"}
    if needs.issubset(df_log.columns) and len(df_log) >= 30:
        # If conditions met, verdict_cube.csv should exist
        assert (out / "verdict_cube.csv").exists(), \
            "verdict_cube.csv expected when strategy/regime/sector present and n>=30"


def test_g1_no_lookahead(smoke_engine):
    eng, _ = smoke_engine
    df = eng.get_trade_log()
    df = df.copy()
    df["entry_date"] = pd.to_datetime(df["entry_date"])
    df["exit_date"] = pd.to_datetime(df["exit_date"])
    bad = df[df["entry_date"] >= df["exit_date"]]
    assert bad.empty, f"{len(bad)} trades have entry>=exit"


def test_g1_pnl_realistic(smoke_engine):
    """Realism floor: PnL is bounded AND short-hold trades cannot post extreme returns.

    Threshold rationale (INV-046 RESOLVED-DOCUMENTED 2026-05-10):
    - Absolute cap 300%: NVDA 2023 (+200% / 4mo), SMCI 2023 (+500% / 6mo) and similar
      momentum names are legitimate Phase 1A holdings; the original 100% cap rejected
      real trend-trade outcomes (smoke fixture flagged NVDA Feb-Aug 2023 +106%).
    - Rapidity gate: PnL > 100% with hold_days < 30 is the "real bug" pattern
      (split-adjust, decimal, or fill-side mistakes); legitimate momentum trades
      that big take time to develop.
    """
    eng, _ = smoke_engine
    df = eng.get_trade_log()
    abs_max = df["pnl_pct"].abs().max()
    assert abs_max < 300, f"single-trade PnL > 300% (got {abs_max:.2f}%)  -  engine bug suspected"

    rapid = df[(df["pnl_pct"].abs() > 100) & (df["hold_days"] < 30)]
    assert rapid.empty, (
        f"{len(rapid)} short-hold trades posted >100% PnL in <30 days  -  "
        f"likely split/dividend/fill bug"
    )
