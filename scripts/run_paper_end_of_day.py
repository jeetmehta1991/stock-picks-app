"""Stage 3 EOD reconciliation (Batch 248).

Daily 4 PM ET cron-trigger: marks paper positions to market close, checks
trailing-stop exits, computes daily PnL, writes journal entry, emails summary.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backtest.paper_trading.email_digest import (
    format_eod_summary_email,
    send_email,
)
from backtest.paper_trading.journal import (
    build_journal_entry,
    save_journal_entry,
)
from backtest.paper_trading.paper_portfolio import PaperPortfolio


def load_market_data(tickers: list[str], as_of: date) -> dict[str, pd.DataFrame]:
    """Load OHLCV for tickers; same as run_paper_morning.py."""
    ohlcv_dir = REPO / "data_prefetch" / "polygon" / "ohlcv_daily"
    out = {}
    for t in tickers:
        safe = str(t).replace(".", "-")
        path = ohlcv_dir / f"{safe}.parquet"
        if not path.exists():
            continue
        try:
            df = pd.read_parquet(path)
            if "date" in df.columns:
                df["date_dt"] = pd.to_datetime(df["date"], errors="coerce").dt.date
                df = df.dropna(subset=["date_dt"])
                df = df[df["date_dt"] <= as_of].sort_values("date_dt")
            if not df.empty:
                out[t] = df.tail(5)
        except Exception:
            continue
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Stage 3 EOD reconciliation")
    p.add_argument("--portfolio-path", default="output_paper/portfolio.json")
    p.add_argument("--journal-dir", default="dashboard_stage_3/journal")
    p.add_argument("--output-dir", default="output_paper")
    p.add_argument("--as-of", default=None)
    p.add_argument("--send-email", action="store_true")
    args = p.parse_args()

    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()
    print(f"[INFO] Stage 3 EOD as_of={as_of}")

    portfolio_path = REPO / args.portfolio_path
    if not portfolio_path.exists():
        print(f"[WARN] No portfolio at {portfolio_path}; nothing to reconcile")
        return 2
    portfolio = PaperPortfolio.load(portfolio_path)

    tickers = [p.ticker for p in portfolio.open_positions]
    if not tickers:
        print("[INFO] No open positions; portfolio metrics unchanged")
        eod = portfolio.update_eod({}, as_of)
    else:
        print(f"[INFO] Marking {len(tickers)} positions to market close")
        market_data = load_market_data(tickers, as_of)
        eod = portfolio.update_eod(market_data, as_of)

    portfolio.save(portfolio_path)
    print(f"[OK] EOD update complete: {eod}")

    # Today's opens (read from picks_<date>.parquet if exists)
    output_dir = REPO / args.output_dir
    picks_path = output_dir / f"picks_{as_of.isoformat()}.parquet"
    picks_executed = []
    if picks_path.exists():
        try:
            picks_executed = pd.read_parquet(picks_path).to_dict(orient="records")
        except Exception:
            pass

    # Today's closes (from portfolio.closed_trades filtered by exit_date)
    closed_today = [
        t for t in portfolio.closed_trades
        if t.get("exit_date") == str(as_of)
    ]

    # Journal entry
    journal_text = build_journal_entry(as_of, eod, picks_executed, closed_today)
    journal_path = save_journal_entry(journal_text, as_of, REPO / args.journal_dir)
    print(f"[OK] Journal saved: {journal_path.relative_to(REPO)}")

    # Email EOD summary
    subject, body = format_eod_summary_email(eod, journal_text[:1500])
    sent = send_email(subject, body, dry_run=not args.send_email)
    print(f"[OK] EOD email {'sent' if args.send_email and sent else 'dry-run'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
