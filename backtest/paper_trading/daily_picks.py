"""Stage 3 daily picks generator (Batch 246).

Reads Phase 1A-beta winners.parquet (P1 combos), evaluates current-day signals
on the universe of tickers where P1 combos fire, ranks by confidence, returns
top-N candidates (default 10 per CLAUDE.md approved rule).

Daily-cron-friendly: stateless; reads winners + per-day data; emits picks.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass
class Pick:
    """A single trade candidate."""
    ticker: str
    combo_id: str
    strategy: str
    exit_method: str
    regime_at_entry: str
    confidence_tier: str  # EXCEPTIONAL / VERY_HIGH / HIGH / MEDIUM-HIGH / MEDIUM
    position_size_pct: float  # 5 / 4 / 3 / 1.5 / 0.75 per CLAUDE.md tiered sizing
    entry_price: float
    initial_stop: float
    rationale_bullets: list[str]

    def to_dict(self) -> dict:
        return {
            "ticker":            self.ticker,
            "combo_id":          self.combo_id,
            "strategy":          self.strategy,
            "exit_method":       self.exit_method,
            "regime_at_entry":   self.regime_at_entry,
            "confidence_tier":   self.confidence_tier,
            "position_size_pct": self.position_size_pct,
            "entry_price":       self.entry_price,
            "initial_stop":      self.initial_stop,
            "rationale_bullets": self.rationale_bullets,
        }


# Position sizing per CLAUDE.md approved rules
_TIER_SIZE_PCT = {
    "EXCEPTIONAL":   5.0,
    "VERY_HIGH":     4.0,
    "HIGH":          3.0,
    "MEDIUM-HIGH":   1.5,
    "MEDIUM":        0.75,
    "LOW":           0.0,   # skip
    "AVOID":         0.0,   # skip (post Batch 190 fix)
}


def _confidence_tier_from_sharpe(sharpe: float) -> str:
    """Map Sharpe ratio to confidence tier per CLAUDE.md position sizing.

    Rough mapping: higher Sharpe = higher tier = larger size.
    """
    if sharpe >= 2.0:
        return "EXCEPTIONAL"
    if sharpe >= 1.5:
        return "VERY_HIGH"
    if sharpe >= 1.0:
        return "HIGH"
    if sharpe >= 0.7:
        return "MEDIUM-HIGH"
    if sharpe >= 0.5:
        return "MEDIUM"
    return "LOW"


def load_winners(path: Path) -> pd.DataFrame:
    """Load winners.parquet; return empty DataFrame if missing."""
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()


def generate_picks(
    winners: pd.DataFrame,
    market_data: dict[str, pd.DataFrame],
    as_of: date,
    max_picks: int = 10,
    priority_filter: tuple = ("P1",),
) -> list[Pick]:
    """Generate top-N daily picks.

    Inputs:
      winners:      winners.parquet (per cube_populator schema)
      market_data:  {ticker: pd.DataFrame (OHLCV ending at as_of)} for tickers
                     where winners fire
      as_of:        today's date
      max_picks:    cap per CLAUDE.md (10 candidates/day)
      priority_filter:  which winner tiers to consider (default P1 only)

    Returns up to max_picks Pick instances ranked by Sharpe desc.
    """
    if winners is None or winners.empty:
        return []
    filtered = winners[winners["priority"].isin(priority_filter)].copy()
    if filtered.empty:
        return []
    # Sort by Sharpe descending (highest-confidence first)
    filtered = filtered.sort_values("sharpe", ascending=False)
    picks: list[Pick] = []
    for _, row in filtered.iterrows():
        if len(picks) >= max_picks:
            break
        # tickers_fired could be list or string; normalize
        tickers_fired = row.get("tickers_fired", [])
        if isinstance(tickers_fired, str):
            tickers_fired = [t.strip() for t in tickers_fired.strip("[]").split(",") if t.strip()]
        if not tickers_fired:
            continue
        # Pick first ticker from this combo that has market data
        ticker = None
        for t in tickers_fired:
            if t in market_data and not market_data[t].empty:
                ticker = t
                break
        if ticker is None:
            continue
        df = market_data[ticker]
        if df.empty:
            continue
        latest = df.iloc[-1]
        entry_price = float(latest.get("close", 0))
        if entry_price <= 0:
            continue
        # Initial stop = 2% below entry (simplified; real engine uses ATR)
        initial_stop = round(entry_price * 0.98, 2)
        sharpe = float(row.get("sharpe", 0))
        tier = _confidence_tier_from_sharpe(sharpe)
        size_pct = _TIER_SIZE_PCT.get(tier, 0.0)
        if size_pct == 0.0:
            continue
        picks.append(Pick(
            ticker=ticker,
            combo_id=str(row.get("combo_id", "")),
            strategy=str(row.get("strategy", "")),
            exit_method=str(row.get("exit_method", "")),
            regime_at_entry=str(row.get("regime", "neutral")),
            confidence_tier=tier,
            position_size_pct=size_pct,
            entry_price=entry_price,
            initial_stop=initial_stop,
            rationale_bullets=[
                f"P1 winner from Phase 1A-beta: {row.get('combo_id', '')}",
                f"Sharpe {sharpe:.2f} OOS (rank #{len(picks) + 1})",
                f"Win rate {row.get('win_rate', 0):.0%}, n_trades {int(row.get('n_trades', 0))}",
                f"Confidence tier {tier} -> position size {size_pct}%",
            ],
        ))
    return picks


def picks_to_dataframe(picks: list[Pick]) -> pd.DataFrame:
    """Convert pick list to DataFrame for CSV/parquet emit."""
    if not picks:
        return pd.DataFrame()
    return pd.DataFrame([p.to_dict() for p in picks])
