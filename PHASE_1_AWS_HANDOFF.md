<!-- Source: per CHECKLIST #77 canonical-source; Council 287 B1233 2026-07-07 doc-sync sweep -->

<!-- 🟢 COUNCIL 278-287 SYNC BANNER (B1233 2026-07-07) — READ FIRST BEFORE THIS DOC -->
> **Doc-sync status:** This document may contain references stale as of 2026-06-27 or earlier. The current state below overrides any stale references in the body until the next full-rewrite.
>
> **Current canonical values (as of 2026-07-07 B1231):**
> - `len(ALL_STRATEGIES) = 219` (was 220 pre-B1189 DELETE of dxy_headwind_multinational_short; was 221 pre-B874)
> - `STRATEGIES_DISABLED_MISSING_PRODUCER = set()` (was `{dxy_headwind_multinational_short}` pre-B1189)
> - Active strategies for Phase 1A-β cube: 219; cube cells 219×26 = 5,694
> - Test count: **880 passed, 2 skipped** on `test_unit.py + test_integration.py`
> - **CHECKLIST items:** #1–#157 (added #151-#157 in Councils 279-285)
> - **LEARNINGS lessons:** through L209 (added L197-L202 in Councils 279-285)
> - **Latest batch:** B1310 (Council 342)
>
> **Recent Council 278-287 milestones (chronological):**
> - Council 278 (B1188-B1204): 40 SKIP strategies loosened per CSV recommendations
> - Council 279 (B1205-B1210): 11 silent misses remediated + L197 + CHECKLIST #151-#153
> - Council 280 (B1211-B1213): News coverage refined (84.2%) + CHECKLIST #154 codified
> - Council 281 (B1214-B1216): short_interest_pct producer bug + institutional 30% gap surfaced
> - Council 282 (B1217-B1219): Cross-audit 192 strategies + CHECKLIST #155
> - Council 283 (B1220-B1223): 5 more producer audits + comprehensive report
> - Council 284 (B1224-B1228): All 25+ producers audited + historical 2020-2023 spot-check + L201 + CHECKLIST #156
> - Council 285 (B1229-B1231): 2 critical bugs FIXED with graceful degradation + L202 + CHECKLIST #157
> - Council 287 (B1232-B1236 in progress): Stage 4 walks archived + doc-sync sweep
>
> **Stage 4 walks: ARCHIVED 2026-07-07 to `archive/2026-07-07-stage-4-walks-complete/`** (Council 121+ 2026-06-27 owner-approved completion). Any `STAGE_4_*.md` reference in this doc now points to archived location.
>
> **Producer coverage (all 25+ producers audited Councils 280-284):**
> - news_sentiment 84.2% / short_interest_dtc 97.7% / **short_interest_pct 0%** (bug; graceful-degradation fix in B1229) / pead 85% / insider 18.8% (event-rarity) / **institutional_signal 85%** (B1230 corrected from B1216's 30% misattribution) / congressional 67.7% / sec_edgar 97.7% / search_volume 99.2% / index_rebalance 10.5% (event) / earnings_yoy 78.9% / cot_positioning 100% / cross_asset 100% (5 fns) / calendar_effects 100% / macro_events 100% / OHLCV-derived (chart_patterns/technical/dec513/multi_timeframe/cross_sectional/ict_producers/volume_profile/smc_ict/pairs_trading) all 100% (bounded by ~84% OHLCV cache)
> - **Critical historical finding (B1227):** news_sentiment 0% in 2020; short_interest_dtc 0% in 2020; institutional 0% in 2020-2021. Backtest interpretation must annotate producer coverage TIMELINE.
>
> **Sprint 5 tickets queued (post-Council 285 priorities):**
> - S5-B1214-SHARES-OUTSTANDING (HIGH; 1 strategy; 1d) - remove B1229 fallback when data ships
> - S5-B1216-INSTITUTIONAL-13F (MED after B1230 correction; 1 strategy; 1-2d) - expand T1a persistence file
> - S5-B1212-SECONDARY-NEWS (MED; 6 strategies; 2d) - Finnhub/AlphaVantage fallback
>
> **Comprehensive coverage report:** `output_audit/PRODUCER_COVERAGE_COMPREHENSIVE_REPORT.md`

---

# Phase 1 AWS Handoff — Owner Execution Guide

# Source: Council 112 Action-5 COMPREHENSIVE bundle per owner directive
# 2026-06-27 'Approve all. Proceed. Arm monitor. Council this.' per
# CHECKLIST #77.

## TL;DR

Phase 1 AWS cloud smoke. Owner runs ONE command:
```bash
bash scripts/launch_phase_1_aws.sh <BUCKET_NAME>
```

After ~30 min, Phase 1 results land in S3 + Claude Monitor surfaces events to chat.

## Approved configuration (Council 111 + 112)

| Item | Value |
|---|---|
| Phase 1 ticker | **NVDA** (high-vol representative; Council 109/111) |
| Architecture | **Arch-2 spot fan-out** (Phase 1 = 1× c6a.4xlarge spot) |
| Instance type | `c6a.4xlarge` (16 vCPU, 32 GB) |
| Spot price ceiling | $0.25/hr (on-demand $0.408/hr; 39% discount) |
| Runtime estimate | ~30 min |
| Cost ceiling | **$2 hard cap** (B1019 STOP-S3 halts at >10× baseline) |
| Monitor cadence | 100-day checkpoints + day-1 canary first-5-fires |
| STOP rule | S3 severity-tiered (CRITICAL instant / HIGH 2nd-consecutive / MEDIUM log-continue) |
| A2 disposition | **A2-Opt2** (roll into R5; no separate batch) |

## Prerequisites checklist (CHECKLIST #13 expensive-job)

Before running launch script, verify:

- [ ] AWS CLI installed locally (`aws --version`)
- [ ] AWS credentials configured (`aws configure`)
- [ ] AWS account active with billing alerts enabled (recommended $20/mo cap)
- [ ] S3 bucket provisioned (or specify name; script creates if missing? — manual verification recommended)
- [ ] AMI ID known (pre-built with venv + pandas-ta + scipy + freezegun) — edit `AMI_ID` in script
- [ ] IAM role + instance profile created with EC2 + S3 + CloudWatch perms — edit `IAM_INSTANCE_PROFILE`
- [ ] VPC subnet + security group provisioned — edit `SUBNET_ID` + `SECURITY_GROUP_ID`
- [ ] SSH keypair for emergency access (optional) — edit `KEY_NAME`

## Step-by-step execution

### Step 1: Pre-launch verification (1 min)

```powershell
# Verify AWS CLI working
aws sts get-caller-identity

# Verify S3 bucket accessible
aws s3 ls s3://<BUCKET_NAME>/
```

### Step 2: Launch Phase 1 (1 command; runs in background)

```bash
bash scripts/launch_phase_1_aws.sh <BUCKET_NAME>
```

This will:
1. Sync 2.97 GB cache to S3 (~10-20 min at typical home BW)
2. Generate bootstrap user-data (Phase 0 audit + B1019 monitor + engine launch + S3 log sync)
3. Request c6a.4xlarge spot instance at $0.25/hr ceiling
4. AWS launches instance + runs Phase 1 cube + syncs results to S3
5. Self-terminates after ~30 min

### Step 3: Monitor armed locally (Claude side)

Claude has armed a local Monitor tool watching `output_phase_1_aws/runtime_monitor.log`. As S3 syncs the log mirror back locally (via Step 4 below), Monitor surfaces structured checkpoint events to chat automatically.

### Step 4: Sync monitor log back locally (Claude-armed pull)

In a separate terminal, run:
```bash
mkdir -p output_phase_1_aws
while true; do
  aws s3 cp s3://<BUCKET_NAME>/phase_1_<TIMESTAMP>/runtime_monitor.log \
    output_phase_1_aws/runtime_monitor.log 2>/dev/null
  sleep 30
done
```

(Or use S3 fsync watch if available.)

### Step 5: Post-run results pull

After Phase 1 completes (~30 min):
```bash
aws s3 sync s3://<BUCKET_NAME>/phase_1_<TIMESTAMP>/results/ output_phase_1_aws/
```

### Step 6: Phase 1 verdict review

Claude runs:
```bash
python scripts/b1019_phase_1_post_run_analyzer.py \
  --trade-log output_phase_1_aws/trade_log.parquet \
  --baseline output_batch395_final/trade_log.parquet
```

Owner reviews `output_audit/b1019_phase_1_post_run_summary.md` + decides Phase 2 GO/NO-GO.

## Phase 1 success criteria (Council 109)

Phase 1 PASS requires ALL 5:

1. **Engine completes** without runtime error / segfault / writer fail
2. **Wall-clock ≤ 60 min** (estimate 30 min; >60 indicates parallelism issue)
3. **A1 fire-rate anomalies = 0** (per-strategy fires within 2× B660 baseline)
4. **B2 schema-invariant violations = 0** (trade_log schema clean)
5. **Day-1 canary** first 5 fires logged with full context surface to chat

Phase 1 FAIL = HALT + investigate; do NOT proceed to Phase 2.

## Cost surveillance (CHECKLIST #29)

| Stage | Estimated cost | Hard ceiling |
|---|---|---|
| S3 cache upload | $0.07 one-time | $0.50 |
| Phase 1 spot instance | $0.20 | $2.00 |
| S3 storage (1 mo) | $0.07 | $0.50 |
| Egress for results | $0.27 | $1.00 |
| **TOTAL Phase 1** | **~$0.61** | **$4.00** |

CloudWatch billing alert recommended at $5 / $10 / $20 tiers.

## Failure / abort handling

If Monitor surfaces HALT-CRITICAL event:
1. CloudWatch logs auto-captured
2. Spot instance terminated
3. Partial results synced to S3 for forensics
4. Owner reviews + decides retry vs investigate

If spot interrupted (rare at $0.25 ceiling):
- Bootstrap script checkpoints engine state per 100 days
- Restart with same run_id resumes from last checkpoint
- Cost-cap reset (each attempt counts toward $2 ceiling)

## Phase 2-4 sequence (per Council 110)

| Phase | Trigger | Instances | Cost | ETA |
|---|---|---|---|---|
| Phase 2 | Phase 1 PASS | 1× c6a.4xlarge spot | $0.20 | 30 min |
| Phase 3 | Phase 2 PASS | 8× c6a.4xlarge spot | $1.60 | 30 min |
| Phase 4 R5 | Phase 3 PASS + **explicit "Launch R5" directive** | 8× c6a.4xlarge spot | $1.60-3.20 | 30-60 min |

## R5 launch gate status (post-A4-A5)

**15 of 15 PATH §13.7 gates READY.** Final launch requires:

1. Phase 1 PASS
2. Phase 2 PASS
3. Phase 3 PASS
4. **Explicit "Launch R5" directive from owner** (7th-reinforcement gate)

A2 cube re-measurement rolled into R5 per A2-Opt2 (Council 111).

## Council lineage

| Council | Verdict |
|---|---|
| Council 107 | Option-I1 4-phase ladder |
| Council 108 | Option-5 Modified 7 enhancements |
| Council 109 | E3 RANGE-BAND + CP-4 LAPTOP-OVERNIGHT (superseded by AWS) |
| Council 110 | Option-AWS-5 HYBRID Arch-2 spot |
| Council 111 | Option-3 PARALLEL + A2-Opt2 + NVDA |
| Council 112 | Action-5 COMPREHENSIVE bundle (this) |

## Critical-rules preservation

- R5 BLOCKED-TILL-EXPLICIT-OWNER (7th reinforcement preserved)
- A2-Opt2 disposition (roll into R5; no separate batch)
- HARD-CUT NO LIVE API CALLS (Stage 2 cube reads pre-cached S3 data)
- L86/L95 precedent: hard cost-cap $2 per phase
- CHECKLIST #13/#22/#23/#29 expensive-job protocol enforced
- DO-NOT-DELETE preserved
- feedback_audit_recommendations_against_existing_directives applied
- feedback_council_enumerate_plus_recommend (Council 112)
- feedback_no_greek_alphabets

## When Phase 1 completes

Claude will:
1. Receive Monitor events as they land
2. Run post-run analyzer
3. Surface verdict to chat
4. Council 113 reviews Phase 1 + recommends Phase 2 GO/NO-GO

Owner then decides:
- Phase 2 approval (single command launch)
- Or HALT for investigation
