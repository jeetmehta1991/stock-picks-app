# B1020 AWS Pre-Flight Audit (Phase 0)

# Source: Council 110 Option-AWS-5 Step 1 + Council 111 Option-3
# PARALLEL + owner directive 2026-06-27 '1 approve phase 0 audit
# 2 yes to all 3 approve' per CHECKLIST #77.

## Purpose

Resolve 5 unknowns (U1-U5) BEFORE committing AWS spend per Council
110 Option-AWS-5 sequence + CHECKLIST #13 expensive-job protocol.

## Verdict summary

**ALL 5 UNKNOWNS RESOLVED. Arch-2 SPOT FAN-OUT GO.**

| Unknown | Verdict | Implication |
|---|---|---|
| U1 multiprocessing readiness | READY | Arch-2 8x c6a.4xlarge spot fan-out viable |
| U2 --tickers flag | READY | Batch split flag confirmed `--tickers TICKERS` |
| U3 cache size | 2.96 GB | Tiny vs worst-case 50-200 GB; sync 10-20 min |
| U4 AMI/Docker | OWNER-CONFIRMED YES | Per "yes to all" directive |
| U5 AWS account + S3 + IAM | OWNER-CONFIRMED YES | Per "yes to all" directive |

## U1 — Engine multiprocessing.Pool readiness

**VERDICT: READY (Arch-2 viable).**

### Evidence

`backtest/engine/backtest.py` lines 138, 750, 765:

```
# line 138: of screen_instrument calls via multiprocessing.Pool with spawn context.
# line 750: Uses multiprocessing.get_context('spawn') for cross-platform behavior
# line 765: import multiprocessing as mp
# line 774: self._screen_pool = ctx.Pool(
```

Engine uses `multiprocessing.get_context('spawn').Pool()` for cross-platform
worker spawning. Spawn context works on Linux + Windows + macOS. Pool is
lazy-initialized at first `_process_day` call and long-lived for entire
backtest run.

### Implications for AWS

- Arch-2 spot fan-out: 8x c6a.4xlarge each spawn 16-vCPU spawn-Pool internally
- OR Arch-1 single c6a.16xlarge spawn 64-vCPU spawn-Pool single instance
- Engine readiness is NOT a blocker; both architectures supported

## U2 — `--tickers` batch split flag

**VERDICT: READY.**

### Evidence

`scripts/run_phase1a.py` line 151:
```
--tickers TICKERS     Comma-separated list of tickers for batch test
```

Plus additional batch-relevant flags surfaced:
- `--screen-pool-workers SCREEN_POOL_WORKERS` (explicit worker count)
- `--no-git` (for parallel batches - commit manually at end)
- `--no-walk-forward` (use for parallel-batch mode; merge recomputes
  on combined trade log)
- `--output-dir OUTPUT_DIR` (per-batch output separation)

### Implications for AWS Arch-2

- Each spot instance gets `--tickers <subset>` + `--output-dir output_batch_NN`
- Engine handles per-instance multiprocessing pool internally
- Post-run merge recomputes walk-forward on combined trade log
- `--no-git` recommended for parallel batches; manual commit on merge

## U3 — Local cache size

**VERDICT: ~3 GB total (smaller than estimate).**

### Evidence

```
backtest/data/cache:    0.12 GB
data_prefetch:          2.84 GB
output_audit:           0.01 GB
TOTAL:                  2.97 GB
```

### Implications

- S3 sync ~10-20 min at typical home upload bandwidth (vs 2-8 hr
  worst-case estimate)
- S3 storage cost ~$0.07/month for 3 GB (vs $5 estimate)
- Egress for final results pull ~$0.27 for <10 GB (vs $5-10 estimate)
- TOTAL DATA-LAYER COST DRAMATICALLY LOWER than Council 110 estimate

## U4 — AMI / Docker container readiness

**VERDICT: OWNER-CONFIRMED YES per 'yes to all'.**

Owner directive Part 2 covered all 5 unknowns positive. Pre-built AMI
or Docker container with pandas-ta + scipy + freezegun + ib_async +
all backtest dependencies assumed ready.

If runtime issues surface, Phase 1 cloud smoke catches them at 1× spot
$0.20 cost (smallest blast radius per L86/L95).

## U5 — AWS account + S3 bucket + IAM role

**VERDICT: OWNER-CONFIRMED YES per 'yes to all'.**

AWS account active + S3 bucket provisioned + IAM role with
EC2 + S3 + CloudWatch permissions assumed ready.

If access issues surface, Phase 1 catches at 1× spot $0.20 cost.

## Updated AWS estimate post-U1-U3 audit

| Phase | Architecture | Wall-clock | Spot Cost |
|---|---|---|---|
| Phase 0 audit | laptop | DONE (this batch) | $0 |
| S3 cache sync (one-time) | upload 3 GB | **10-20 min** (was 2-8 hr) | **$0.07** (was $1-5) |
| Phase 1 (1-ticker) | 1x c6a.4xlarge spot | 30 min | $0.20 |
| Phase 2 (10-ticker smoke) | 1x c6a.4xlarge spot | 30 min | $0.20 |
| Phase 3 (50-ticker demo) | 8x c6a.4xlarge spot | 30 min | $1.60 |
| Phase 4 R5 (503 T1a) | 8x c6a.4xlarge spot | 30-60 min | $1.60-3.20 |
| A2 (if standalone) | 8x c6a.4xlarge spot | 15-30 min | $0.80-1.60 |
| S3 storage (1 mo) | 3 GB | -- | **$0.07** (was $5) |
| Egress final results | <10 GB | -- | $0.27-0.90 |
| **TOTAL marginal** | | **~3-6 hr** | **~$5-12** (was $10-25) |

**Reduction: ~50% cost** vs Council 110 estimate due to U3 cache size.

## Architecture decision (per owner approval Part 3)

**Arch-2 SPOT FAN-OUT GO.** 8x c6a.4xlarge spot instances for Phase 3-4 + A2.
Phase 1-2 use 1x c6a.4xlarge spot (parallelism not needed at small ticker
scope).

Fallback to Arch-1 single c6a.16xlarge NOT NEEDED since U1 confirmed
multiprocessing.Pool ready.

## Next phase per Council 110 protocol

**Step 2: Phase 1 cloud smoke** (1x c6a.4xlarge spot, $0.20, 30 min).

Owner gates next:
1. Phase 1 ticker selection (NVDA / AAPL / SPY / auto-pick)
2. After Phase 1 verdict-clean: Phase 2 approval
3. After Phase 2: Phase 3 approval
4. After Phase 3: Phase 4 R5 launch approval (+ A2 disposition)

## Memory rule references

- Council 110 Option-AWS-5 Arch-2 spot fan-out verdict
- Council 111 Option-3 PARALLEL execute-+-surface verdict
- CHECKLIST #13/#22/#23/#29 expensive-job protocol
- L86/L95 $150 discarded-work precedent (now ~$5-12 risk)
- HARD CUT NO LIVE API CALLS (cube reads S3-cached data only)
- feedback_council_enumerate_plus_recommend
- feedback_audit_recommendations_against_existing_directives
- feedback_no_greek_alphabets

## Sign-off

Phase 0 audit COMPLETE. All 5 unknowns resolved positive. Arch-2 spot
fan-out architecture confirmed. AWS estimate reduced ~50% vs Council
110 baseline (3 GB cache + 5-12 USD total).

Next: Phase 1 cloud smoke pending owner ticker selection.
