"""Stage 4 LIVE EOD reconciliation (Batch 373 C-1).

Mirror of `scripts/run_paper_end_of_day.py` (Batch 248) but sources
positions + fills from Interactive Brokers (via ib_async) instead of
the synthetic PaperPortfolio. Daily 4 PM ET cron-trigger.

Per STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md table row Stage 4 -
this is the missing end-of-day complement to `run_live_morning.py`.

STUB-MODE by default per CLAUDE.md "BUILT BUT NOT ACTIVATED until owner
triggers post-May-29" + ib_executor.py `dry_run=True` default. To
activate live IB reads, owner must:
  1. Set IB_GATEWAY_HOST / IB_GATEWAY_PORT env vars (or pass --host/--port)
  2. Run IB Gateway (TWS API port 7497 paper / 7496 live)
  3. Pass --live (drops the dry_run guard)

Reconciliation produces:
  - `output_live/eod_reconciliation_<DATE>.json` summary
  - `dashboard_stage_4/journal/<DATE>.md` daily journal entry
  - Optional email summary (--send-email)

Slippage / fill-quality measurement per DEC-122 + DEC-280:
  expected_fill = pick.entry_price (close-on-signal)
  actual_fill   = IB execution price
  slippage_bps  = (actual - expected) / expected * 1e4

Per CLAUDE.md "Email approval for trade execution" gate: this EOD job
does NOT place trades. It only reconciles fills + reports.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def _connect_ib(host: str, port: int, client_id: int, dry_run: bool):
    """Connect to IB Gateway. Returns (ib_client, connection_ok)."""
    if dry_run:
        return None, True
    try:
        from ib_async import IB  # type: ignore
    except ImportError:
        print("[WARN] ib_async not installed; falling back to dry-run mode")
        return None, False
    ib = IB()
    try:
        ib.connect(host, port, clientId=client_id, readonly=True)
        return ib, True
    except Exception as exc:
        print(f"[WARN] IB connect failed: {exc}; falling back to dry-run")
        return None, False


def _fetch_ib_positions(ib, dry_run: bool):
    """Read current open positions from IB. Returns list of dicts.

    Schema per ib_async portfolio API:
      [{"ticker": str, "shares": int, "avg_cost": float,
        "market_price": float, "unrealized_pnl": float}]
    """
    if dry_run or ib is None:
        return []
    try:
        portfolio_items = ib.portfolio()
        return [
            {
                "ticker":          str(item.contract.symbol),
                "shares":          int(item.position),
                "avg_cost":        float(item.averageCost),
                "market_price":    float(item.marketPrice),
                "market_value":    float(item.marketValue),
                "unrealized_pnl":  float(item.unrealizedPNL),
            }
            for item in portfolio_items
        ]
    except Exception as exc:
        print(f"[WARN] IB portfolio fetch failed: {exc}")
        return []


def _fetch_ib_fills(ib, as_of: date, dry_run: bool):
    """Read today's executions from IB. Returns list of dicts.

    Schema per ib_async executions API:
      [{"ticker": str, "side": "BOT"/"SLD", "shares": int,
        "fill_price": float, "fill_time": str, "order_id": str}]
    """
    if dry_run or ib is None:
        return []
    try:
        # ib_async: ib.executions() returns Fill objects with .execution
        # and .contract sub-objects
        fills_raw = ib.executions()
        out = []
        for fill in fills_raw:
            ex = fill.execution
            ct = fill.contract
            fill_date = str(ex.time.date()) if hasattr(ex.time, "date") else str(ex.time)
            if fill_date != as_of.isoformat():
                continue
            out.append({
                "ticker":     str(ct.symbol),
                "side":       str(ex.side),      # "BOT" / "SLD"
                "shares":     int(ex.shares),
                "fill_price": float(ex.price),
                "fill_time":  str(ex.time),
                "order_id":   str(ex.orderId),
            })
        return out
    except Exception as exc:
        print(f"[WARN] IB executions fetch failed: {exc}")
        return []


def _compute_slippage(expected_pick: dict, actual_fill: dict) -> dict | None:
    """Per DEC-122 + DEC-280 slippage measurement vs signal-day close."""
    expected = expected_pick.get("entry_price")
    actual   = actual_fill.get("fill_price")
    if not expected or not actual or expected <= 0:
        return None
    side = actual_fill.get("side", "BOT")
    # For long entries (BOT): positive bps = paid more than expected (bad slippage)
    # For short entries (SLD): positive bps = received less than expected (bad)
    direction = 1 if side == "BOT" else -1
    slippage_bps = direction * (actual - expected) / expected * 1e4
    return {
        "ticker":         actual_fill.get("ticker"),
        "expected_price": round(expected, 4),
        "actual_price":   round(actual, 4),
        "slippage_bps":   round(slippage_bps, 2),
        "side":           side,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Stage 4 LIVE EOD reconciliation")
    p.add_argument("--host", default=os.environ.get("IB_GATEWAY_HOST", "127.0.0.1"))
    p.add_argument("--port", type=int,
                   default=int(os.environ.get("IB_GATEWAY_PORT", "7497")))
    p.add_argument("--client-id", type=int, default=42,
                   help="IB API client id (must be unique per concurrent connection)")
    p.add_argument("--output-dir", default="output_live")
    p.add_argument("--journal-dir", default="dashboard_stage_4/journal")
    p.add_argument("--as-of", default=None)
    p.add_argument("--live", action="store_true",
                   help="Drop dry-run guard - requires IB Gateway running + credentials")
    p.add_argument("--send-email", action="store_true")
    args = p.parse_args()

    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()
    dry_run = not args.live
    print(f"[INFO] Stage 4 LIVE EOD as_of={as_of} dry_run={dry_run} "
          f"host={args.host}:{args.port}")

    output_dir = REPO / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    journal_dir = REPO / args.journal_dir
    journal_dir.mkdir(parents=True, exist_ok=True)

    # Connect to IB Gateway
    ib, connected = _connect_ib(args.host, args.port, args.client_id, dry_run)
    if not connected and not dry_run:
        print("[ERROR] IB connection failed; pass --live only when Gateway is reachable")
        return 1

    # Fetch positions + fills
    positions = _fetch_ib_positions(ib, dry_run)
    fills     = _fetch_ib_fills(ib, as_of, dry_run)
    print(f"[INFO] IB positions: {len(positions)}; fills today: {len(fills)}")

    # Slippage vs morning picks
    picks_path = REPO / "output_live" / f"picks_{as_of.isoformat()}.parquet"
    expected_picks = {}
    if picks_path.exists():
        try:
            import pandas as pd
            df = pd.read_parquet(picks_path)
            expected_picks = {row["ticker"]: dict(row) for _, row in df.iterrows()}
        except Exception as exc:
            print(f"[WARN] picks parquet read failed: {exc}")

    slippage = []
    for fill in fills:
        if fill.get("ticker") in expected_picks:
            s = _compute_slippage(expected_picks[fill["ticker"]], fill)
            if s is not None:
                slippage.append(s)

    summary = {
        "as_of":           as_of.isoformat(),
        "dry_run":         dry_run,
        "ib_connected":    connected and not dry_run,
        "n_positions":     len(positions),
        "n_fills_today":   len(fills),
        "positions":       positions,
        "fills":           fills,
        "slippage":        slippage,
        "host":            f"{args.host}:{args.port}",
    }
    summary_path = output_dir / f"eod_reconciliation_{as_of.isoformat()}.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str),
                            encoding="utf-8")
    print(f"[OK] reconciliation summary -> {summary_path.relative_to(REPO)}")

    # Journal entry (markdown)
    journal_text = (
        f"# Stage 4 LIVE EOD journal - {as_of.isoformat()}\n\n"
        f"- IB connected: {connected and not dry_run} "
        f"(dry_run={dry_run})\n"
        f"- Open positions: {len(positions)}\n"
        f"- Today's fills: {len(fills)}\n"
        f"- Slippage measurements: {len(slippage)}\n\n"
    )
    if slippage:
        journal_text += "## Slippage per fill (vs signal-day close)\n\n"
        journal_text += "| ticker | side | expected | actual | bps |\n"
        journal_text += "|---|---|---:|---:|---:|\n"
        for s in slippage:
            journal_text += (
                f"| {s['ticker']} | {s['side']} | "
                f"{s['expected_price']:.4f} | {s['actual_price']:.4f} | "
                f"{s['slippage_bps']:.1f} |\n"
            )
    journal_path = journal_dir / f"{as_of.isoformat()}.md"
    journal_path.write_text(journal_text, encoding="utf-8")
    print(f"[OK] journal -> {journal_path.relative_to(REPO)}")

    # Email summary (optional)
    if args.send_email:
        try:
            from backtest.paper_trading.email_digest import send_email
            subject = f"Stage 4 LIVE EOD {as_of.isoformat()} - {len(fills)} fills"
            send_email(subject, journal_text, dry_run=False)
            print("[OK] email sent")
        except Exception as exc:
            print(f"[WARN] email failed: {exc}")

    # Disconnect IB
    if ib is not None:
        try:
            ib.disconnect()
        except Exception:
            pass

    print(f"[OK] Stage 4 LIVE EOD complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
