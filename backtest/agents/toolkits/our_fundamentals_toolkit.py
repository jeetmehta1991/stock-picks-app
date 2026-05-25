"""OurFundamentalsToolkit - Fundamentals Analyst data bridge.

Source (per CHECKLIST #77): TRADINGAGENTS_DATA_AUDIT.md Section 21.

Bridges TradingAgents Fundamentals Analyst to our PIT-correct financials
+ smart money + insider data from data_prefetch/ caches.

Sprint 7 Phase A scope (Batch 350): 5 methods covering highest-impact
fundamentals inputs per audit doc:
  - get_pit_financials(ticker, as_of) - Polygon financials filed <= as_of
  - get_earnings_history(ticker, as_of, lookback_quarters)
  - get_insider_transactions(ticker, as_of)
  - get_congressional_trades(ticker, as_of)
  - get_13f_holdings(ticker, as_of)

Deferred (separate batches per audit):
  - earnings_transcripts (Gap B - not in current stack)
  - analyst_estimates (Gap C - Quiver has rating changes only)
  - short_interest (Gap D - Ortex wiring pending)
  - government_contracts (BUG-284 OPEN)
  - sec_filings text (SEC EDGAR integration - separate sprint)
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd


_REPO = Path(__file__).resolve().parents[3]
_FINANCIALS_DIR = _REPO / "data_prefetch" / "polygon" / "financials"
_INSIDERS_PATH = _REPO / "data_prefetch" / "quiver" / "insiders" / "global.parquet"
_CONGRESS_PATH = _REPO / "data_prefetch" / "quiver" / "congressional" / "global.parquet"
_INSTITUTIONAL_DIR = _REPO / "data_prefetch" / "quiver" / "institutional"


class OurFundamentalsToolkit:
    """Fundamentals Analyst toolkit. PIT-correct by construction.

    All methods filter by filing_date / report_date / disclosure_date
    so as_of cannot be exceeded.
    """

    def __init__(
        self,
        financials_dir: Path | None = None,
        insiders_path: Path | None = None,
        congress_path: Path | None = None,
        institutional_dir: Path | None = None,
    ) -> None:
        self.financials_dir = financials_dir or _FINANCIALS_DIR
        self.insiders_path = insiders_path or _INSIDERS_PATH
        self.congress_path = congress_path or _CONGRESS_PATH
        self.institutional_dir = institutional_dir or _INSTITUTIONAL_DIR

    def get_pit_financials(self, ticker: str, as_of: date) -> dict[str, Any]:
        """Return latest 10-Q/10-K filed at or before as_of.

        Returns:
            dict with keys: ticker, as_of, fiscal_period, fiscal_year,
            filing_date, eps, summary (text excerpt or empty). cache_miss
            on parquet absence.
        """
        ticker_safe = ticker.replace(".", "-")
        path = self.financials_dir / f"{ticker_safe}.parquet"
        if not path.exists():
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "cache_miss"}
        try:
            df = pd.read_parquet(path)
        except Exception as e:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": f"parquet_read_error: {e}"}
        if df.empty or "filing_date" not in df.columns:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "no_data"}
        df["filing_date_dt"] = pd.to_datetime(df["filing_date"], errors="coerce").dt.date
        past = df[df["filing_date_dt"].notna() & (df["filing_date_dt"] <= as_of)]
        if past.empty:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "no_filings_before_as_of"}
        latest = past.sort_values("filing_date_dt").iloc[-1]
        eps = None
        try:
            from backtest.signals.pead import _safe_eps
            eps = _safe_eps(latest.get("financials_json"))
        except Exception:
            pass
        return {
            "ticker": ticker,
            "as_of": as_of.isoformat(),
            "fiscal_period": str(latest.get("fiscal_period", "")) or None,
            "fiscal_year": str(latest.get("fiscal_year", "")) or None,
            "filing_date": latest["filing_date_dt"].isoformat(),
            "eps": eps,
            "company_name": str(latest.get("company_name", "")) or None,
        }

    def get_earnings_history(
        self, ticker: str, as_of: date, lookback_quarters: int = 8
    ) -> dict[str, Any]:
        """Return ticker's last N quarterly EPS readings filed at or before as_of."""
        ticker_safe = ticker.replace(".", "-")
        path = self.financials_dir / f"{ticker_safe}.parquet"
        if not path.exists():
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "cache_miss"}
        try:
            from backtest.signals.pead import load_quarterly_eps
            eps_df = load_quarterly_eps(ticker)
        except Exception as e:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": f"load_error: {e}"}
        if eps_df.empty:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "no_eps_data"}
        past = eps_df[eps_df["filing_date"] <= as_of]
        if past.empty:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "no_filings_before_as_of"}
        recent = past.sort_values("filing_date").tail(lookback_quarters)
        history = [
            {
                "fiscal_period": str(r["fiscal_period"]),
                "fiscal_year": str(r["fiscal_year"]),
                "filing_date": r["filing_date"].isoformat() if hasattr(r["filing_date"], "isoformat") else str(r["filing_date"]),
                "eps": float(r["eps"]) if r["eps"] is not None and not pd.isna(r["eps"]) else None,
            }
            for _, r in recent.iterrows()
        ]
        return {
            "ticker": ticker,
            "as_of": as_of.isoformat(),
            "n_quarters": len(history),
            "history": history,
        }

    def get_insider_transactions(
        self, ticker: str, as_of: date, lookback_days: int = 90
    ) -> dict[str, Any]:
        """Return summary of recent insider purchase/sale activity (Form 4).

        Filters on disclosure_date <= as_of (PIT-correct: trades are
        reported within ~2 business days of execution).
        """
        if not self.insiders_path.exists():
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "cache_miss"}
        try:
            df = pd.read_parquet(self.insiders_path)
        except Exception as e:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": f"parquet_read_error: {e}"}
        date_col = "Date" if "Date" in df.columns else ("date" if "date" in df.columns else None)
        ticker_col = "Ticker" if "Ticker" in df.columns else "ticker"
        if date_col is None or ticker_col not in df.columns:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "schema_unexpected"}
        df["_date"] = pd.to_datetime(df[date_col], errors="coerce").dt.date
        window_start = as_of - pd.Timedelta(days=lookback_days).to_pytimedelta()
        sub = df[(df[ticker_col] == ticker) & (df["_date"].notna()) &
                 (df["_date"] >= window_start) & (df["_date"] <= as_of)]
        if sub.empty:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "n_transactions": 0, "buy_count": 0, "sell_count": 0}
        buys = sub[sub.get("AcquiredDisposedCode", "") == "A"]
        sells = sub[sub.get("AcquiredDisposedCode", "") == "D"]
        return {
            "ticker": ticker,
            "as_of": as_of.isoformat(),
            "lookback_days": lookback_days,
            "n_transactions": int(len(sub)),
            "buy_count": int(len(buys)),
            "sell_count": int(len(sells)),
            "director_count": int(sub.get("isDirector", pd.Series([], dtype=bool)).sum()) if "isDirector" in sub.columns else 0,
        }

    def get_congressional_trades(
        self, ticker: str, as_of: date, lookback_days: int = 180
    ) -> dict[str, Any]:
        """Return summary of recent congressional disclosure trades.

        Filters on disclosure_date (the date the trade became public),
        NOT transaction_date - this is the PIT-correct boundary because
        the public could only have known about the trade once disclosed.
        """
        if not self.congress_path.exists():
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "cache_miss"}
        try:
            df = pd.read_parquet(self.congress_path)
        except Exception as e:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": f"parquet_read_error: {e}"}
        date_col = "Disclosed" if "Disclosed" in df.columns else ("disclosure_date" if "disclosure_date" in df.columns else None)
        ticker_col = "Ticker" if "Ticker" in df.columns else "ticker"
        if date_col is None or ticker_col not in df.columns:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "schema_unexpected"}
        df["_date"] = pd.to_datetime(df[date_col], errors="coerce").dt.date
        window_start = as_of - pd.Timedelta(days=lookback_days).to_pytimedelta()
        sub = df[(df[ticker_col] == ticker) & (df["_date"].notna()) &
                 (df["_date"] >= window_start) & (df["_date"] <= as_of)]
        if sub.empty:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "n_disclosures": 0}
        purchases = sub[sub.get("Transaction", "").astype(str).str.contains("Purchase", case=False, na=False)]
        sales = sub[sub.get("Transaction", "").astype(str).str.contains("Sale", case=False, na=False)]
        return {
            "ticker": ticker,
            "as_of": as_of.isoformat(),
            "lookback_days": lookback_days,
            "n_disclosures": int(len(sub)),
            "purchase_count": int(len(purchases)),
            "sale_count": int(len(sales)),
            "unique_filers": int(sub.get("Representative", pd.Series([], dtype=str)).nunique()) if "Representative" in sub.columns else 0,
        }

    def get_13f_holdings(self, ticker: str, as_of: date) -> dict[str, Any]:
        """Return 13F institutional holding count + AUM exposure.

        Filters on filing_date (45-day reporting lag per SEC; DEC-325).
        """
        ticker_safe = ticker.replace(".", "-")
        path = self.institutional_dir / f"{ticker_safe}.parquet"
        if not path.exists():
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "cache_miss"}
        try:
            df = pd.read_parquet(path)
        except Exception as e:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": f"parquet_read_error: {e}"}
        if df.empty:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "no_holdings"}
        # filing_date is the PIT-correct boundary (45-day lag from quarter-end)
        date_col = "filing_date" if "filing_date" in df.columns else ("Date" if "Date" in df.columns else None)
        if date_col is None:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "no_filing_date_col"}
        df["_date"] = pd.to_datetime(df[date_col], errors="coerce").dt.date
        past = df[df["_date"].notna() & (df["_date"] <= as_of)]
        if past.empty:
            return {"ticker": ticker, "as_of": as_of.isoformat(), "error": "no_filings_before_as_of"}
        latest_quarter = past["_date"].max()
        latest = past[past["_date"] == latest_quarter]
        return {
            "ticker": ticker,
            "as_of": as_of.isoformat(),
            "latest_filing_date": latest_quarter.isoformat(),
            "n_institutional_holders": int(len(latest)),
        }
