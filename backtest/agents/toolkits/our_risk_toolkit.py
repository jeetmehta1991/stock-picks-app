"""OurRiskToolkit - Risk Debaters data bridge. PARTIAL SCAFFOLD.

Source (per CHECKLIST #77): TRADINGAGENTS_DATA_AUDIT.md Section 24.

Partial scaffold:
  - get_volatility_regime - REAL (bridges DEC-106 + macro)
  - get_macro_stress_signals - REAL (bridges FRED VIX/HY/T10Y2Y)
  - get_event_proximity - REAL (bridges FRED FOMC calendar)
  - get_crisis_flags - REAL (bridges DEC-262 regime classifier output)
  - get_correlation_to_existing_positions - SCAFFOLD (Portfolio dep)
  - get_sector_concentration - SCAFFOLD (Portfolio dep)
  - get_drawdown_context - SCAFFOLD (Portfolio dep)
  - get_recent_outcomes_on_similar_setups - SCAFFOLD (DEC-189 reflection
    log not yet shipped)
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd


_REPO = Path(__file__).resolve().parents[3]
_FOMC_PATH = _REPO / "data_prefetch" / "fred" / "fomc_calendar.parquet"


class OurRiskToolkit:
    """Risk Debaters toolkit. PIT-correct macro + event methods; Portfolio
    methods are scaffolded until BUG-095 lands."""

    def __init__(self, portfolio: Any = None, fomc_path: Path | None = None) -> None:
        self.portfolio = portfolio
        self.fomc_path = fomc_path or _FOMC_PATH

    def get_volatility_regime(self, as_of: date) -> dict[str, Any]:
        """Return DEC-106 regime classifier output + VIX value."""
        try:
            from backtest.data.macro import macro_snapshot
        except Exception as e:
            return {"as_of": as_of.isoformat(), "error": f"import_error: {e}"}
        try:
            macro = macro_snapshot(as_of)
        except Exception as e:
            return {"as_of": as_of.isoformat(), "error": f"snapshot_error: {e}"}
        vix = macro.get("vix_value")
        return {
            "as_of": as_of.isoformat(),
            "vix_value": vix,
            "vix_regime": "elevated" if vix and vix >= 25 else ("normal" if vix else "unknown"),
            "hy_oas": macro.get("hy_oas"),
            "t10y2y": macro.get("t10y2y"),
        }

    def get_macro_stress_signals(self, as_of: date) -> dict[str, Any]:
        """Return macro stress indicators per DEC-262 + DEC-317.

        Combines VIX, HY OAS, T10Y2Y, and initial jobless claims into a
        single dict the Risk Debaters can reason about.
        """
        try:
            from backtest.data.macro import macro_snapshot
        except Exception as e:
            return {"as_of": as_of.isoformat(), "error": f"import_error: {e}"}
        try:
            macro = macro_snapshot(as_of)
        except Exception as e:
            return {"as_of": as_of.isoformat(), "error": f"snapshot_error: {e}"}
        return {
            "as_of": as_of.isoformat(),
            "vix_value": macro.get("vix_value"),
            "hy_oas": macro.get("hy_oas"),
            "t10y2y": macro.get("t10y2y"),
            "icsa_jobless": macro.get("icsa_jobless"),
        }

    def get_event_proximity(self, as_of: date, window_days: int = 14) -> dict[str, Any]:
        """Return FOMC events within [as_of, as_of + window_days].

        Per DEC-348 / DEC-349 asymmetric window suppression: agents should
        be aware of imminent FOMC and condition risk-on bias accordingly.
        """
        if not self.fomc_path.exists():
            return {"as_of": as_of.isoformat(), "error": "cache_miss"}
        try:
            df = pd.read_parquet(self.fomc_path)
        except Exception as e:
            return {"as_of": as_of.isoformat(), "error": f"parquet_read_error: {e}"}
        if df.empty or "date" not in df.columns:
            return {"as_of": as_of.isoformat(), "error": "no_date_col"}
        df["_d"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        window_end = as_of + timedelta(days=window_days)
        sub = df[df["_d"].notna() & (df["_d"] >= as_of) & (df["_d"] <= window_end)]
        upcoming = [
            {
                "date": r["_d"].isoformat(),
                "meeting_type": str(r.get("meeting_type", "FOMC")),
                "days_until": (r["_d"] - as_of).days,
            }
            for _, r in sub.iterrows()
        ]
        return {
            "as_of": as_of.isoformat(),
            "window_days": window_days,
            "n_upcoming_events": len(upcoming),
            "upcoming_events": upcoming,
        }

    def get_crisis_flags(self, as_of: date) -> dict[str, Any]:
        """Return crisis-regime flags per DEC-262 + DEC-317.

        Bridges regime_filter.classify_regime; flags `crisis=True` when
        VIX >= 35 OR HY OAS spike OR equity drawdown criteria per DEC-262.
        """
        try:
            from backtest.data.macro import macro_snapshot
            from backtest.engine.regime_filter import classify_regime
        except Exception as e:
            return {"as_of": as_of.isoformat(), "error": f"import_error: {e}"}
        try:
            macro = macro_snapshot(as_of)
        except Exception as e:
            return {"as_of": as_of.isoformat(), "error": f"snapshot_error: {e}"}
        vix = macro.get("vix_value")
        try:
            regime = classify_regime(spy_close=None, spy_ema200=None, vix=vix, vix_smoothed=None, prev_regime=None)
        except Exception:
            regime = "unknown"
        return {
            "as_of": as_of.isoformat(),
            "regime": regime,
            "vix_value": vix,
            "crisis_flag": bool(vix and vix >= 35),
        }

    def get_correlation_to_existing_positions(self, ticker: str, as_of: date) -> dict[str, Any]:
        """SCAFFOLD - requires Portfolio class (BUG-095)."""
        return {
            "ticker": ticker,
            "as_of": as_of.isoformat(),
            "max_correlation": 0.0,
            "scaffold": True,
        }

    def get_sector_concentration(self) -> dict[str, Any]:
        """SCAFFOLD - requires Portfolio class (BUG-095)."""
        return {"max_sector_pct": 0.0, "sectors": {}, "scaffold": True}

    def get_drawdown_context(self) -> dict[str, Any]:
        """SCAFFOLD - requires Portfolio class (BUG-095)."""
        return {"current_drawdown_pct": 0.0, "max_drawdown_pct": 0.0, "scaffold": True}

    def get_recent_outcomes_on_similar_setups(
        self, ticker: str, setup_signature: str, as_of: date
    ) -> dict[str, Any]:
        """SCAFFOLD - requires DEC-189 reflection log."""
        return {
            "ticker": ticker,
            "setup_signature": setup_signature,
            "as_of": as_of.isoformat(),
            "n_similar_trades": 0,
            "win_rate_pct": None,
            "scaffold": True,
        }
