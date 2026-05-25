"""OurNewsToolkit - News Analyst data bridge.

Source (per CHECKLIST #77): TRADINGAGENTS_DATA_AUDIT.md Section 22.

Bridges TradingAgents News Analyst to Polygon news cache (DEC-440) +
FRED event calendar (FOMC, CPI, NFP) + Quiver analyst rating changes.

Sprint 7 Phase A scope (Batch 350): 3 methods covering core news inputs:
  - get_polygon_news(ticker, as_of, lookback_days) - cached news articles
  - get_fred_event_log(as_of, lookback_days) - FOMC / CPI / NFP releases
  - get_analyst_rating_changes(ticker, as_of, lookback_days) - Quiver
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd


_REPO = Path(__file__).resolve().parents[3]
_POLYGON_NEWS_DIR = _REPO / "data_prefetch" / "polygon" / "news"
_FOMC_PATH = _REPO / "data_prefetch" / "fred" / "fomc_calendar.parquet"
_RATING_CHANGES_PATH = _REPO / "data_prefetch" / "quiver" / "wallstreetbets" / "global.parquet"


class OurNewsToolkit:
    """News Analyst toolkit. PIT-correct by published_date filter."""

    def __init__(
        self,
        polygon_news_dir: Path | None = None,
        fomc_path: Path | None = None,
        rating_changes_path: Path | None = None,
    ) -> None:
        self.polygon_news_dir = polygon_news_dir or _POLYGON_NEWS_DIR
        self.fomc_path = fomc_path or _FOMC_PATH
        self.rating_changes_path = rating_changes_path or _RATING_CHANGES_PATH

    def get_polygon_news(
        self, ticker: str, as_of: date, lookback_days: int = 30, max_articles: int = 25
    ) -> dict[str, Any]:
        """Return recent Polygon news article headlines + sentiment for ticker."""
        ticker_safe = ticker.replace(".", "-")
        path = self.polygon_news_dir / f"{ticker_safe}.parquet"
        if not path.exists():
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "cache_miss"}
        try:
            df = pd.read_parquet(path)
        except Exception as e:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": f"parquet_read_error: {e}"}
        if df.empty:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "n_articles": 0, "articles": []}
        date_col = "published_utc" if "published_utc" in df.columns else (
            "published_date" if "published_date" in df.columns else None
        )
        if date_col is None:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "no_date_column"}
        df["_pub"] = pd.to_datetime(df[date_col], errors="coerce", utc=True).dt.date
        window_start = as_of - pd.Timedelta(days=lookback_days).to_pytimedelta()
        sub = df[df["_pub"].notna() & (df["_pub"] >= window_start) & (df["_pub"] <= as_of)]
        if sub.empty:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "n_articles": 0, "articles": []}
        sub = sub.sort_values("_pub", ascending=False).head(max_articles)
        articles = []
        for _, r in sub.iterrows():
            articles.append({
                "date": r["_pub"].isoformat() if r["_pub"] is not None else None,
                "title": str(r.get("title", ""))[:200] or None,
                "publisher": str(r.get("publisher", "")) or None,
            })
        return {
            "ticker": ticker,
            "as_of": as_of.isoformat(),
            "lookback_days": lookback_days,
            "n_articles": int(len(sub)),
            "articles": articles,
        }

    def get_fred_event_log(self, as_of: date, lookback_days: int = 30) -> dict[str, Any]:
        """Return FOMC meeting log within lookback window."""
        if not self.fomc_path.exists():
            return {"as_of": as_of.isoformat(), "error": "cache_miss"}
        try:
            df = pd.read_parquet(self.fomc_path)
        except Exception as e:
            return {"as_of": as_of.isoformat(), "error": f"parquet_read_error: {e}"}
        if df.empty or "date" not in df.columns:
            return {"as_of": as_of.isoformat(), "error": "no_date_col"}
        df["_d"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        window_start = as_of - pd.Timedelta(days=lookback_days).to_pytimedelta()
        sub = df[df["_d"].notna() & (df["_d"] >= window_start) & (df["_d"] <= as_of)]
        events = [
            {
                "date": r["_d"].isoformat(),
                "meeting_type": str(r.get("meeting_type", "FOMC")),
            }
            for _, r in sub.iterrows()
        ]
        return {
            "as_of": as_of.isoformat(),
            "lookback_days": lookback_days,
            "n_events": len(events),
            "events": events,
        }

    def get_analyst_rating_changes(
        self, ticker: str, as_of: date, lookback_days: int = 90
    ) -> dict[str, Any]:
        """Return recent analyst rating changes for ticker (Quiver)."""
        if not self.rating_changes_path.exists():
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "cache_miss"}
        try:
            df = pd.read_parquet(self.rating_changes_path)
        except Exception as e:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": f"parquet_read_error: {e}"}
        if df.empty:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "n_changes": 0}
        ticker_col = "Ticker" if "Ticker" in df.columns else ("ticker" if "ticker" in df.columns else None)
        date_col = "Date" if "Date" in df.columns else ("date" if "date" in df.columns else None)
        if ticker_col is None or date_col is None:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "schema_unexpected"}
        df["_d"] = pd.to_datetime(df[date_col], errors="coerce").dt.date
        window_start = as_of - pd.Timedelta(days=lookback_days).to_pytimedelta()
        sub = df[(df[ticker_col] == ticker) & df["_d"].notna() &
                 (df["_d"] >= window_start) & (df["_d"] <= as_of)]
        return {
            "ticker": ticker,
            "as_of": as_of.isoformat(),
            "lookback_days": lookback_days,
            "n_changes": int(len(sub)),
        }
