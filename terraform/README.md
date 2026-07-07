<!-- Source: per CHECKLIST #77 canonical-source; Council 287 B1234 2026-07-07 doc-sync sweep -->

<!-- COUNCIL 278-287 SYNC BANNER (B1234 2026-07-07) - READ FIRST -->
> **Sync status:** Body may contain refs stale as of 2026-06-27 or earlier. Canonical current state (B1231):
> - `len(ALL_STRATEGIES) = 219` (post-B1189 DELETE dxy_headwind); `STRATEGIES_DISABLED_MISSING_PRODUCER = set()`
> - Test count: 858 passed, 2 skipped on test_unit + test_integration
> - CHECKLIST items #1-#157, LEARNINGS through L202, latest batch B1231
> - Councils 278-287: 40 strategies loosened + 11 silent misses remediated + 25+ producer coverage audits + historical timeline finding + 2 critical bugs FIXED via graceful degradation
> - Stage 4 walks: ARCHIVED to `archive/2026-07-07-stage-4-walks-complete/`
> - Sprint 5 tickets: 3 queued (S5-B1214 HIGH / S5-B1216 MED post-B1230 correction / S5-B1212 MED)
> - Comprehensive coverage report: `output_audit/PRODUCER_COVERAGE_COMPREHENSIVE_REPORT.md`

---

# Stage 4 LIVE infrastructure (Terraform)

**Status:** SKELETON ONLY — Batch 373 C-2 2026-05-26.

Per `STAGE_2_STAGE_3_STAGE_4_BUILD_PLAN_MAY_29.md` Stage 4 row "Deploy +
DR (`scripts/deploy_live.sh` + `terraform/`)" — this directory is the
infrastructure-as-code half of one-shot AWS deploy + disaster recovery.

## Status

| Component | Status | Notes |
|---|---|---|
| `main.tf` (AWS Lightsail instance) | SKELETON | Provider + variable scaffold; values not finalized |
| `iam.tf` (least-privilege IAM) | NOT WRITTEN | Owner-scoped; requires owner AWS account |
| `secrets.tf` (Anthropic + IB credentials via SSM Parameter Store) | NOT WRITTEN | Pending owner-supplied secret values |
| `dns.tf` (Route53 if owner wants `picks.<domain>`) | DEFERRED | Stage 3 currently uses GitHub Pages |
| `backup.tf` (EBS snapshots) | NOT WRITTEN | Daily snapshot + 7-day retention is the DR plan |
| Restore-from-backup runbook | NOT WRITTEN | See `docs/dr_runbook.md` (queued) |

## Activation path (owner-driven)

1. Owner creates AWS account + provisions `terraform-bootstrap` IAM user
   with permissions: Lightsail, IAM, SSM, EC2 (for EBS snapshots).
2. Owner runs `scripts/deploy_live.sh` which invokes `terraform init`,
   `terraform plan`, `terraform apply` against this directory.
3. Lightsail instance comes up; SSM Parameter Store holds Anthropic /
   IB credentials; instance pulls latest `main` + runs
   `python scripts/run_live_morning.py` + `python scripts/run_live_end_of_day.py`
   on cron.
4. Owner enables email-approval gate per Stage 4 build plan.

## NOT-ACTIVATED reasons (per CLAUDE.md hard rule)

> "AWS Lightsail $5/mo, BUILT BUT NOT ACTIVATED until owner triggers
> post-May-29"

Stage 4 activation gated on:
- Stage 3 paper-trading validation (DEC-131 net Sharpe gate)
- Owner provides AWS account credentials
- Owner provides IB account credentials
- Owner approves cost ceiling ($5-15/mo Lightsail + IB tiered commission)

## Cost estimate (when activated)

| Item | Monthly cost | Notes |
|---|---:|---|
| Lightsail nano (1 vCPU / 2 GB) | $5-10 | sufficient for daily picks job |
| EBS snapshot (7-day retention) | $1-2 | DR coverage |
| SSM Parameter Store standard tier | $0 | free up to 10K parameters |
| Route53 hosted zone (optional) | $0.50 | if owner wants custom domain |
| **Total** | **$6.50-12.50/mo** | + IB tiered commission |

## Files in this directory

- `README.md` (this file) — Status + activation path
- `main.tf` — Terraform provider + Lightsail instance scaffold (skeleton)
- `variables.tf` — Configurable variables (region, instance size, ssh key)
- `.gitignore` — Block `*.tfstate*`, `.terraform/`, `*.tfvars` (secrets)

## Related deliverables

- `scripts/deploy_live.sh` — One-shot deploy wrapper (PRESENT)
- `scripts/run_live_morning.py` — Daily picks + email approval gate (PRESENT)
- `scripts/run_live_end_of_day.py` — Daily reconciliation (Batch 373 C-1 NEW)
- `backtest/live_trading/ib_executor.py` — IB order placement (PRESENT, dry-run default)
- `backtest/live_trading/risk_overlay.py` — DEC-515 + circuit breakers (PRESENT)
- `Dockerfile` — Container image for Lightsail (PRESENT)
