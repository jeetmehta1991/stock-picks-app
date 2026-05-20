"""Stage 3 daily morning orchestrator (Batch 248).

Daily 8 AM ET cron-trigger: reads winners.parquet -> generates picks -> opens
paper positions -> emails owner. Idempotent (won't double-open same ticker).

Usage:
  python scripts/run_paper_morning.py
  python scripts/run_paper_morning.py --winners-source output_v2 \
      --portfolio-path output_paper/portfolio.json --dry-run

Owner activates by cron-scheduling on local Windows OR AWS Lightsail.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backtest.paper_trading.daily_picks import (
    generate_picks,
    load_winners,
    picks_to_dataframe,
)
from backtest.paper_trading.email_digest import (
    format_picks_email,
    send_email,
)
from backtest.paper_trading.paper_portfolio import PaperPortfolio


def load_market_data(tickers: list[str], as_of: date) -> dict[str, pd.DataFrame]:
    """Load OHLCV for each ticker from data_prefetch cache."""
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
                out[t] = df.tail(30)  # last 30 days enough for picks
        except Exception:
            continue
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Stage 3 morning paper trading orchestrator")
    p.add_argument("--winners-source", default="output_v2",
                   help="Dir containing winners.parquet")
    p.add_argument("--portfolio-path", default="output_paper/portfolio.json",
                   help="Persistent portfolio state path")
    p.add_argument("--output-dir", default="output_paper",
                   help="Output dir for picks + journal")
    p.add_argument("--as-of", default=None,
                   help="Date (YYYY-MM-DD); default today")
    p.add_argument("--max-picks", type=int, default=10,
                   help="Max picks per CLAUDE.md approved rule")
    p.add_argument("--include-p2", action="store_true",
                   help="Include P2 winners in pick pool")
    p.add_argument("--dry-run", action="store_true", default=False,
                   help="Don't open positions; just emit picks")
    p.add_argument("--send-email", action="store_true",
                   help="Actually send email (requires EMAIL_SMTP_* env vars)")
    args = p.parse_args()

    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()
    print(f"[INFO] Stage 3 morning run as_of={as_of}")

    # Load winners
    winners_path = REPO / args.winners_source / "winners.parquet"
    winners = load_winners(winners_path)
    if winners.empty:
        print(f"[WARN] No winners at {winners_path}; nothing to pick")
        # Still send email summary
        if args.send_email:
            s, b = format_picks_email([], as_of)
            send_email(s, b, dry_run=False)
        return 2
    print(f"[INFO] Loaded {len(winners)} winners")

    # Resolve tickers
    priority_filter = ("P1", "P2") if args.include_p2 else ("P1",)
    relevant = winners[winners["priority"].isin(priority_filter)]
    tickers_pool = set()
    for tf in relevant["tickers_fired"]:
        if isinstance(tf, str):
            tickers_pool.update(t.strip() for t in tf.strip("[]").split(",") if t.strip())
        elif isinstance(tf, (list, tuple)):
            tickers_pool.update(str(t).strip() for t in tf)

    print(f"[INFO] Loading market data for {len(tickers_pool)} candidate tickers")
    market_data = load_market_data(list(tickers_pool), as_of)

    picks = generate_picks(
        winners, market_data, as_of,
        max_picks=args.max_picks,
        priority_filter=priority_filter,
    )
    print(f"[INFO] Generated {len(picks)} picks")

    # Save picks parquet
    output_dir = REPO / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    picks_df = picks_to_dataframe(picks)
    picks_path = output_dir / f"picks_{as_of.isoformat()}.parquet"
    if not picks_df.empty:
        picks_df.to_parquet(picks_path, index=False)
        print(f"[OK] Wrote {picks_path.relative_to(REPO)}")

    # Open positions (unless dry-run)
    if not args.dry_run:
        portfolio_path = REPO / args.portfolio_path
        portfolio_path.parent.mkdir(parents=True, exist_ok=True)
        portfolio = PaperPortfolio.load(portfolio_path)
        opened = 0
        for pick in picks:
            pos = portfolio.open_position(pick.to_dict(), as_of)
            if pos is not None:
                opened += 1
                print(f"  Opened {pos.ticker} ({pos.shares} shares @ ${pos.entry_price:.2f})")
        portfolio.save(portfolio_path)
        print(f"[OK] Opened {opened}/{len(picks)} positions; portfolio saved")

    # Email
    subject, body = format_picks_email([p.to_dict() for p in picks], as_of)
    sent = send_email(subject, body, dry_run=not args.send_email)
    print(f"[OK] Email {'sent' if args.send_email and sent else 'dry-run'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
