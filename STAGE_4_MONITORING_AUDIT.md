# Stage 4 LIVE monitoring pipeline audit (Batch 374 C-3)

**Source (per CHECKLIST #77 canonical-source attribution):** owner directive 2026-05-26 bucket-C closure - status check of the live monitoring pipeline referenced in `STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md` Stage 4 row "Live monitoring (AWS Lightsail container)".

## Build plan commitment

> "Live monitoring (AWS Lightsail container) | Real-time PnL + risk + alerting + auto-restart | Same | Real-time | $5-15/mo AWS Lightsail (BUILT BUT NOT ACTIVATED) | Position state + market data | Real-time dashboard + email alerts on circuit-breaker fires"

## Current state inventory

| Component | Status | Evidence | Activation gate |
|---|---|---|---|
| `backtest/live_trading/ib_executor.py` (order placement) | ✅ BUILT (stub) | 40+ LOC; `dry_run=True` default | Owner IB credentials + `--live` flag |
| `backtest/live_trading/risk_overlay.py` (DEC-515 + circuit breakers) | ✅ BUILT | Imports + tier-sizing wired | Stage 3 paper-trading validation |
| `Dockerfile` (container image for Lightsail) | ✅ BUILT | Repo root | Owner activation |
| `scripts/run_live_morning.py` (daily picks + email approval) | ✅ BUILT | 146 LOC | Owner activation |
| `scripts/run_live_end_of_day.py` (Batch 373 C-1) | ✅ BUILT (this session) | 200+ LOC; dry-run default | `--live` flag |
| `scripts/deploy_live.sh` (one-shot AWS deploy) | ✅ BUILT (~Batch 247) | Repo root | Terraform skeleton (Batch 373 C-2) |
| `terraform/` (Batch 373 C-2) | ✅ SKELETON | `activated=false` default | Owner `activated=true` + AWS account |
| **Real-time PnL alerting (cron-fired)** | 🔴 NOT BUILT | No `scripts/run_live_alerting.py` or equivalent | Stage 4 activation |
| **Auto-restart on Lightsail crash** | 🔴 NOT BUILT | systemd unit or supervisor not committed | Stage 4 activation |
| **Circuit-breaker fire email** | ⚠ PARTIAL | `email_digest.py` exists; CB-fire trigger not wired to live engine | Risk overlay -> email hook |
| **Stage 4 dashboard** (`dashboard_stage_4/`) | ⚠ SCAFFOLD | Journal dir exists (Batch 373); HTML/CSS not built | Owner activation |
| **Position state persistence** (cross-restart durability) | 🔴 NOT BUILT | Live IB state read fresh each cron; no local mirror | Owner activation |

## Activation-gate dependencies

```
Stage 3 paper-trading validation (DEC-131 net Sharpe gate)
    |
    +--> Owner-approved Stage 4 activation trigger
            |
            +--> terraform/ activated=true + ssh_cidrs filled
            |       |
            |       +--> terraform apply -> Lightsail instance up
            |               |
            |               +--> SSM Parameter Store: Anthropic + IB credentials populated
            |                       |
            |                       +--> scripts/deploy_live.sh -> instance bootstrap
            |                               |
            |                               +--> systemd timer / cron jobs active
            |                                       |
            |                                       +--> scripts/run_live_morning.py daily 13:00 UTC
            |                                       +--> scripts/run_live_end_of_day.py daily 21:30 UTC
            +--> (parallel) Build remaining monitoring pieces:
                    - scripts/run_live_alerting.py (CB-fire email trigger)
                    - systemd unit for auto-restart
                    - dashboard_stage_4/ HTML build
                    - position state mirror to local parquet
```

## Recommendations (no implementation this batch)

1. **Stage 4 activation is not blocked on monitoring pipeline** — daily picks + EOD reconciliation work via cron without dashboard. Monitoring polish can happen post-activation.
2. **CB-fire email hook is the highest-value missing piece** (~30 min effort): wire `risk_overlay.py` to call `email_digest.send_email` when a circuit breaker fires. Currently CB events are logged but not actioned.
3. **Auto-restart** can be a 5-line systemd unit; not blocking.
4. **Real-time dashboard** is nice-to-have; the journal markdown + EOD email already cover the operational surface.

## Status: AUDIT-ONLY, no code change this batch

This document is the deliverable. No file changes in `backtest/live_trading/` or new scripts in this batch (separate from the C-1 EOD script shipped Batch 373).

Action items queued for activation-time batches:
- [ ] `scripts/run_live_alerting.py` (CB-fire email trigger)
- [ ] `dashboard_stage_4/index.html` template
- [ ] systemd unit for auto-restart resilience
- [ ] Live position state mirror parquet (for durability across restarts)
