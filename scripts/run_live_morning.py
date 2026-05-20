"""Stage 4 daily morning orchestrator (Batch 248).

Daily 8 AM ET cron-trigger for LIVE trading: reads winners.parquet -> generates
picks -> sends owner-approval email -> on owner approval (next run with
--execute-approved <pick_ids>), places IB bracket orders.

Owner-directive 2026-05-19: dry_run=True default; requires explicit owner
opt-in to actually execute. Built but not activated.

Workflow:
  Morning T+0:  python scripts/run_live_morning.py
                -> sends approval email with pick IDs
  Owner reply:  approves IDs (e.g., 1,3,5)
  Same day:     python scripts/run_live_morning.py --execute-approved 1,3,5
                -> places IB bracket orders + risk-overlay enforced
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backtest.live_trading.ib_executor import (
    connect_ib,
    place_bracket_order,
)
from backtest.live_trading.risk_overlay import (
    LiveRiskState,
    check_pre_trade,
    compute_shares_for_pick,
    update_halt_state,
)
from backtest.paper_trading.daily_picks import (
    generate_picks,
    load_winners,
)
from backtest.paper_trading.email_digest import (
    format_picks_email,
    send_email,
)


def load_risk_state(path: Path) -> LiveRiskState:
    if not path.exists():
        return LiveRiskState()
    try:
        d = json.loads(path.read_text())
        return LiveRiskState(**d)
    except Exception:
        return LiveRiskState()


def save_risk_state(state: LiveRiskState, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state.__dict__, indent=2, default=str))


def load_market_data(tickers: list[str], as_of: date) -> dict[str, pd.DataFrame]:
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
                df = df[df["date_dt"] <= as_of].sort_values("date_dt")
            if not df.empty:
                out[t] = df.tail(30)
        except Exception:
            continue
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Stage 4 live morning orchestrator")
    p.add_argument("--winners-source", default="output_v2")
    p.add_argument("--risk-state-path", default="output_live/risk_state.json")
    p.add_argument("--output-dir", default="output_live")
    p.add_argument("--as-of", default=None)
    p.add_argument("--max-picks", type=int, default=10)
    p.add_argument("--execute-approved", type=str, default=None,
                   help="Comma-separated pick IDs (1-indexed) to execute")
    p.add_argument("--ib-port", type=int, default=7497,
                   help="7497=paper IB Gateway; 7496=live")
    p.add_argument("--dry-run", action="store_true", default=True,
                   help="Default TRUE; owner must explicitly --no-dry-run to enable real orders")
    p.add_argument("--no-dry-run", dest="dry_run", action="store_false")
    p.add_argument("--send-email", action="store_true")
    args = p.parse_args()

    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()
    print(f"[INFO] Stage 4 morning run as_of={as_of} dry_run={args.dry_run}")

    # Load winners + market data
    winners_path = REPO / args.winners_source / "winners.parquet"
    winners = load_winners(winners_path)
    if winners.empty:
        print(f"[WARN] No winners at {winners_path}")
        return 2

    relevant = winners[winners["priority"] == "P1"]
    tickers_pool = set()
    for tf in relevant["tickers_fired"]:
        if isinstance(tf, (list, tuple)):
            tickers_pool.update(str(t).strip() for t in tf)
        elif isinstance(tf, str):
            tickers_pool.update(t.strip() for t in tf.strip("[]").split(",") if t.strip())

    market_data = load_market_data(list(tickers_pool), as_of)
    picks = generate_picks(winners, market_data, as_of, max_picks=args.max_picks)
    print(f"[INFO] Generated {len(picks)} picks")

    # Load risk state
    risk_state_path = REPO / args.risk_state_path
    risk_state = load_risk_state(risk_state_path)
    update_halt_state(risk_state)

    # Pre-trade check for each pick (risk overlay)
    output_dir = REPO / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    approved_picks = []
    for i, pick in enumerate(picks, 1):
        pd_dict = pick.to_dict()
        rc = check_pre_trade(pd_dict, risk_state)
        if rc.approved:
            approved_picks.append((i, pick, rc))
            print(f"  Pick #{i} {pick.ticker}: APPROVED (size {rc.adjusted_size_pct}%)")
        else:
            print(f"  Pick #{i} {pick.ticker}: BLOCKED ({rc.reason})")
        if rc.halt_signal:
            print(f"[HALT] {rc.reason} - aborting further checks")
            risk_state.halt_active = True
            risk_state.halt_reason = rc.reason
            break

    # Persist picks for approval workflow
    picks_path = output_dir / f"picks_{as_of.isoformat()}.json"
    picks_path.write_text(json.dumps([p.to_dict() for p in picks], indent=2, default=str))

    # Execute-approved path
    if args.execute_approved:
        approved_ids = set(int(x.strip()) for x in args.execute_approved.split(",") if x.strip())
        print(f"[INFO] Executing approved IDs: {sorted(approved_ids)}")
        ib = connect_ib(port=args.ib_port, dry_run=args.dry_run)
        for i, pick, rc in approved_picks:
            if i not in approved_ids:
                continue
            pd_dict = pick.to_dict()
            shares = compute_shares_for_pick(
                pd_dict,
                portfolio_value=risk_state.portfolio_value,
                cash_available=risk_state.portfolio_value * 0.5,  # 50% cash floor assumed
            )
            if shares == 0:
                print(f"  Pick #{i} {pick.ticker}: 0 shares; skip")
                continue
            r = place_bracket_order(
                ticker=pick.ticker,
                direction="long",
                shares=shares,
                entry_price=pick.entry_price,
                stop_price=pick.initial_stop,
                target_price=None,  # auto = +2R
                order_type="LMT",
                dry_run=args.dry_run,
                ib_connection=ib,
            )
            print(f"  Pick #{i} order: {r}")
        if ib is not None:
            try:
                ib.disconnect()
            except Exception:
                pass
        save_risk_state(risk_state, risk_state_path)
    else:
        # Send approval email
        subject, body = format_picks_email([p.to_dict() for p in picks], as_of)
        subject = f"[LIVE-APPROVAL-NEEDED] {subject}"
        body = (
            "## OWNER APPROVAL REQUIRED\n\n"
            "Reply with the pick IDs you approve (e.g., '1,3,5').\n\n"
            "Then re-run: `python scripts/run_live_morning.py --execute-approved 1,3,5`\n\n"
            "---\n\n" + body
        )
        send_email(subject, body, dry_run=not args.send_email)
        print(f"[OK] Approval email {'sent' if args.send_email else 'dry-run'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
